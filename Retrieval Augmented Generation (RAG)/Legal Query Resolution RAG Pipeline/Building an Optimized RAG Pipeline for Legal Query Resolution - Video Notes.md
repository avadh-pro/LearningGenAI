# Building an Optimized RAG Pipeline for Legal Query Resolution — Video Notes

Condensed, slide-and-transcript-based notes from a TMLC Academy hands-on session on building a production-style RAG system over Indian statutory law. See *Building an Optimized RAG Pipeline for Legal Query Resolution - Transcript.md* in this folder for the full source recording transcript, and the `RAG Project` folder for the source slide deck (`XVwAT1b8R9uuzHPbeZuw_...pdf`) and the working notebook (`Indian_Laws_RAG_Solution.ipynb`) this session builds. Every slide is embedded below at the point it's discussed.

**The one-sentence version:** this session takes every optimization technique from the *Retrieval Optimization Techniques* note and wires them together into one real, working system — a legal question-answering assistant that reads Indian Acts and Sections instead of guessing.

**The analogy that runs through this whole document 👩‍⚖️**

Imagine you hire a very fast, very well-read **paralegal** to answer legal questions for you. They've read every Indian Act cover to cover, but they have three problems: they can't tell "Section 6" of one Act from "Section 6" of a completely different Act, they sometimes forget what you asked two questions ago, and — worst of all — an unsupervised paralegal will *guess* confidently rather than admit "I don't know." This entire session is about building the training, filing system, and guardrails that turn that raw paralegal into someone you'd actually trust with a real legal question. Every section below is one piece of that training.

---

## 0. What We're Building

![Building RAG Solution for Legal Query Resolution](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/1.png)

At the highest level, the whole system does four things, in order, every time someone asks a question:

1. **Ask a question** — "Is this contract valid?"
2. **Find trusted sources** — search the actual law, not the model's memory.
3. **Pick the most relevant information** — narrow thousands of possible sections down to the handful that actually matter.
4. **Generate a clear answer** — with the exact Act and Section cited, not a vague paraphrase.

That's the paralegal analogy in diagram form. Everything from here is *how* each of those four steps is actually built, because each one turns out to hide a surprising amount of difficulty.

---

## 1. Why Legal Text Is a Uniquely Hard Test Case

![Problem Statement](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/2.png)

**The objective, in plain words:** build a RAG system over Indian statutory law — the Aadhaar Act, the Actuaries Act, the Administrative Tribunals Act, and others — and make it actually reliable. Legal text was picked *on purpose* because it stress-tests RAG harder than almost any other domain, for three specific reasons:

**1. "Section 6" means nothing on its own.** Section numbers are not unique — dozens of different Acts each have their own "Section 6," and they say completely different things. A generic RAG system that just searches for "Section 6" has no way to know *which* Section 6 the user means. The real, unique identifier is the *pair* — (which Act, which Section) — not the section number alone.

> 🗂️ **Paralegal analogy:** this is exactly like a filing cabinet where every single drawer has a folder labeled "Page 6." Useless, unless every folder also says *which book* that page 6 came from.

**2. Laws are nested, not flat.** An Act contains Chapters, which contain Sections, which contain Sub-clauses. A generic chunking approach that just slices text every N characters has no concept of this structure, and can easily separate a rule from the sub-clause that defines its one crucial exception.

**3. Follow-up questions are incomplete on their own.** Someone asks "What are the provisions under Section 6?", then follows up with "For women residents only?" That second question, taken in isolation, is meaningless — it has no subject. It only makes sense *combined with* the first question. This means retrieval alone can never be enough; the system needs to actively **rewrite** the follow-up into a standalone question before it can search for anything.

These three problems point directly at the three things the rest of this session builds: a **composite key** (Act + Section) instead of a bare section number, **structure-aware chunking**, and **query rewriting**.

---

## 2. The Architecture, at a Glance

![Architecture](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/3.png)

Before diving into each piece, it's worth seeing the whole shape of the system once. It has three parts:

| Part | When it runs | What it does |
|---|---|---|
| **1. Offline Indexing** | Once, before any user ever asks anything | Load the law dataset, clean it, chunk it, embed it, store it |
| **2. Online Query-Time Workflow** | Every single time a question comes in | Rewrite the query, decompose it if needed, retrieve, rerank, decide confidence, generate an answer |
| **3. Evaluation & Inspection** | Whenever you want to check if the system is actually good | Measure retrieval quality and generation quality against a real test set |

This mirrors the pre-retrieval / retrieval / post-retrieval split from the *Retrieval Optimization Techniques* note almost exactly — Part 1 here is where chunking (a pre-retrieval technique) lives, and Part 2 is where query rewriting, hybrid search, and reranking all show up in sequence, in one real pipeline instead of as separate concepts.

The rest of this document walks through Parts 1, 2, and 3 in that order.

---

## 3. Dataset & Chunking (Part 1, first half)

![Dataset & Chunking](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/4.png)

### 3.1 Dataset Characterization

![Dataset Characterization](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/5.png)

The source is a Hugging Face dataset of Indian laws — 34,244 records in total, with this implementation working on an initial subset of 200 for speed. Each record has three fields: `act_title`, `section`, and `law` (the actual text).

The critical design decision, straight from Section 1's problem statement: **the true primary key is the pair `(act_title, section)`, never `section` alone.** The team didn't assume this — they inspected the actual data first and found:

- Some records are empty or near-empty (malformed source entries), and get filtered out with a minimum-length rule.
- Record length ranges from 0 all the way to **~493,000 characters** — meaning some records are entire chapters, not tidy individual sections.

That last point is exactly why chunking can't be skipped: you cannot hand a 493,000-character block of text to an embedding model and expect a useful, focused vector out the other end — this is precisely the "averaging problem" from the Sentence Window note. **The design principle they follow:** inspect the real data first, then choose a chunking strategy — never start from a default chunk size and hope it fits.

### 3.2 Chunking Methodology

![Chunking Methodology](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/6.png)

This is the most important diagram in the whole session, because it solves a problem the Sentence Window note only hints at: **what do you do when precise retrieval and full context genuinely pull in opposite directions?**

**Step 1 — the default unit is one *section*.** Only if a section is unusually long does it get split further, using a *recursive character splitter*.

**Step 2 — splitting respects the law's own structure**, in a strict priority order:

1. Paragraph breaks
2. Numbered sub-clauses — (1), (2), (3)…
3. Lettered sub-clauses — (a), (b), (c)…
4. Sentence boundaries
5. Word boundaries (last resort)

The splitter always tries the *most meaningful* boundary first, and only falls back to a cruder one if it has to. This is the "recursive" strategy from the chunking-strategy table in the other note, applied for real: paragraphs first, then numbered clauses, then letters, then sentences, then — only if truly desperate — words.

**Step 3 — parent-child architecture, the actual clever part:**

> 📎 **Paralegal analogy:** imagine giving your paralegal sticky-note index tabs for quick searching, while the actual full page of the law book stays intact and untouched. The tabs are for *finding* the right page fast; the full page is what they actually *read* once found.

Concretely:
- Each **section** is the "parent" — the complete, unsplit legal text.
- It's cut into small **child chunks** purely so the *search* can be precise.
- Every child chunk carries a `parent_doc_id` pointing back to its full parent section.
- **Retrieval searches the small child chunks** (for precision — a tight, focused match).
- **Generation always receives the full parent section**, not just the matched snippet (for completeness — no clause is ever interpreted missing its neighbours).

This is the exact answer to the sentence-window trade-off discussed earlier: instead of *choosing* between small-and-precise or large-and-complete, this architecture gets **both at once**, by search and generation deliberately using two different sizes of the same content.

---

## 4. Embeddings and the Vector Store (Part 1, second half)

![Embeddings and Vector Store](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/7.png)

### 4.1 Embedding Strategy

![Embedding Strategy](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/8.png)

This is hybrid search — from Stage 2 of *Retrieval Optimization Techniques* — but now made concrete with real numbers:

- **Dense embeddings** (`mxbai-embed-large-v1` locally, or OpenAI's `text-embedding-3-large`) capture *meaning*. They know "punishment for murder" and "penalty for homicide" are close in meaning, even though they don't share a single word.
- **Sparse embeddings** (BM25, via FastEmbed) capture *exact terms* — a section reference like "Section 6," an exact phrase like "Aadhaar Act," or a code like "IPC 302." Dense embeddings alone are unreliable at exact-match tasks like this; sparse embeddings are built for exactly this.

**One detail worth remembering for interviews:** the two are computed **independently, per chunk,** and only combined *at retrieval time* (in Section 5 below) — never merged together into one blended vector at embedding time. Keeping them as two separate vectors is what lets the system search each in its own way and fuse the results afterwards, rather than pre-committing to one blend that can't be adjusted per query.

### 4.2 Vector Store Configuration

![Vector Store Configuration](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/9.png)

The vectors live in **Qdrant**, in a single collection called `indian_laws`, using **two named vectors per point** (`dense` and `sparse`) rather than maintaining two entirely separate databases — simpler to operate, same dual-search capability.

Qdrant's sparse vectors are configured with an **IDF modifier**, which is what actually makes them behave like BM25: term frequency gets weighted by how rare that term is across the whole collection, so a common word like "the" contributes almost nothing to a match, while a rare, specific term like "Aadhaar" contributes a lot.

**What's stored alongside each vector (the payload):**

| Field | Example | Purpose |
|---|---|---|
| `act_title` | "Aadhaar Act, 2016" | Which law this is from |
| `section` | "Section 6" | Which part of that law |
| `parent_doc_id` | `SEC_6_ActX` | Link back to the complete, unsplit section |
| `chunk_text` | (the small piece) | What actually gets searched |
| `parent_text` | (the full section) | What actually gets sent to the LLM to answer from |

Notice `act_title` and `section` sitting right there in the payload, together — that's the composite-key problem from Section 1, solved at the storage level.

---

## 5. Retrieval and Reranking (Part 2, the heart of the pipeline)

![Retrieval and Reranking](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/10.png)

This is the longest and most important part of the online workflow — five distinct techniques, each solving one specific failure mode, stacked in sequence.

### 5.1 Hybrid Search and Rank Fusion

![Hybrid Search and Rank Fusion](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/11.png)

Dense retrieval and sparse retrieval run **independently** — each produces its own separate top-k ranked list — and then get combined with **Reciprocal Rank Fusion (RRF)**.

**Why not just average the two scores together?** Because they're not comparable numbers at all:

| | Cosine similarity (dense) | BM25 score (sparse) |
|---|---|---|
| Range | −1 to 1 | 0 to ∞ (unbounded) |
| Meaning | "how semantically similar" | "how lexically relevant" |

Averaging a bounded −1-to-1 number with an unbounded 0-to-∞ number is statistically meaningless — a large BM25 score would always dominate a small cosine score regardless of which one actually mattered more for that query.

**RRF's trick: ignore the raw scores completely, use only rank *position*.**

$$RRF(d) = \sum_{r \in \{dense, sparse\}} \frac{1}{k + rank_r(d)}$$

A document ranked #1 on both lists scores far higher than one that's #1 on only one list and absent from the other. It's scale-independent by construction, because a rank position (1st, 2nd, 3rd…) means the same thing regardless of which scoring system produced it.

### 5.2 Diversity, Efficiency, and Filtering

![Diversity, Efficiency, and Filtering](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/12.png)

Three refinements sit between "fused results" and "final answer":

**Maximal Marginal Relevance (MMR)** trims redundancy. If the top 5 fused results are all near-identical restatements of the same clause, MMR swaps some of them out for results that are *still relevant* but *meaningfully different* — balancing relevance against dissimilarity from what's already been picked.

**Adaptive retrieval width** is a funnel: cast a broad net first (~20–30 candidates from RRF), narrow to a small diverse set (4–6, via MMR), and *only then* run the expensive reranker on that small set. Reranking every one of the original 20–30 candidates would be wasteful; reranking only the surviving 4–6 is cheap and just as effective.

**Metadata pre-filtering on `act_title`** lets a query optionally be scoped to one specific Act before searching at all — directly solving the "Section 6 means nothing on its own" problem from Section 1, by letting the user (or the system) constrain the search universe up front rather than hoping retrieval sorts out the ambiguity after the fact.

### 5.3 Query Decomposition

![Query Decomposition](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/13.png)

A compound question — *"What are the grounds for divorce under Indian law, and what is the procedure to file for it?"* — is really **two separate questions** stitched together. Retrieving for it as one single blended query risks partially answering both halves instead of fully answering either.

The fix: **split → retrieve independently → merge.**

1. Break the compound query into independent sub-queries (Q1: grounds for divorce, Q2: filing procedure).
2. Retrieve separately for each — each sub-query gets its own focused search.
3. Merge and de-duplicate the combined results.

This directly matches the "multi-intent queries" failure mode from the other Video Notes file in this folder (*Current State of RAG*) — same problem, same fix, now shown as an actual pipeline node rather than just a concept.

### 5.4 Reranking and Confidence Scoring

![Reranking and Confidence Scoring](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/14.png)

The small surviving candidate set goes through a **cross-encoder reranker** (`BGE-reranker-v2-m3`). The difference from everything before it: a cross-encoder reads the **query and the chunk together, at the same time**, rather than comparing two separately-computed vectors. That joint reading is slower per item — which is exactly why it only runs on a handful of survivors, not the whole candidate pool — but far more precise.

The reranker's **top score becomes a confidence signal.** In the diagram's worked example, Chunk 3 reranks to 0.92 — labeled **HIGH CONFIDENCE**. That single number is what the next step routes on.

### 5.5 Confidence-Gated Web Search

![Confidence-Gated Web Search](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/15.png)

This is the paralegal finally learning to say **"I don't know — let me check with someone else"** instead of confidently guessing.

- **Score ≥ threshold (τ = 0.60 in the example):** trust the local corpus, generate the answer from the retrieved legal text.
- **Score < threshold:** the local knowledge base genuinely doesn't have a good enough match — fall back to a **live web search** (via the Serper API, scoped specifically to `indiacode.nic.in` and `indiankanoon.org`, not the open web) and generate from *that* instead.

Either way, the final answer carries a **source tag** — `SOURCE: LOCAL` or `SOURCE: WEB` — so nothing is presented as more certain than it actually is. This is the single most important trust-building mechanism in the whole system: a wrong answer delivered with obvious low confidence is far less dangerous than a wrong answer delivered as if it were certain.

---

## 6. Memory and Orchestration

![Memory and Orchestration](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/16.png)

### 6.1 Session Memory and Query Rewriting

![Session Memory and Query Rewriting](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/17.png)

This solves the "For women residents only?" problem from Section 1 directly.

**Conversation history is persisted per session in a local SQLite store** — every turn's original query, its rewritten (standalone) version, and the response, all saved.

Before each new turn is processed:
1. Recent session history is pulled from that SQLite store.
2. A lightweight LLM call rewrites the current turn into a **standalone** version — e.g. turn 2's "What about Section 7?" becomes "What is Section 7 of the Aadhaar Act?", using turn 1's context to fill in what "it" refers to.
3. *That* rewritten, self-contained query is what actually goes on to retrieval — never the raw, ambiguous follow-up.

The slide is blunt about this one: **query rewriting is called the single highest-leverage improvement for multi-turn RAG systems — and also the one most commonly skipped** in simpler implementations. It's easy to build a RAG system that works great for standalone questions and then quietly falls apart the moment a real user asks a natural follow-up.

### 6.2 State Schema

![State Schema](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/18.png)

The entire pipeline is orchestrated with **LangGraph**, around one structured object called `RAGState` — think of it as a clipboard that gets handed from person to person along an assembly line, with each person adding their own notes to it, never starting a fresh clipboard.

Key fields on that clipboard: `session_id`, `raw_query`, `rewritten_query`, `sub_queries`, `retrieved_chunks`, `reranked_chunks`, `top_score`, `answer`, `citations`, `source`, `confidence`, `error`.

Three properties make this design work:

- **Each node is a pure function** — it reads the current state and returns an updated state, with no hidden side effects.
- **The same state object flows through every node** — nothing gets lost or recomputed between steps.
- **Edges define the execution order** — including the branch point where the Confidence Gate sends execution either to "Generator (Local)" or "Web Search (Fallback)," exactly matching Section 5.5.

---

## 7. Evaluation

![Evaluation](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/19.png)

Every other Video Notes file in this folder ends on "you can't fix what you never measured" — this session shows what that actually looks like in practice, split into the same two halves as always: did retrieval find the right thing, and did generation use it correctly.

### 7.1 Retrieval Metrics

![Retrieval Metrics](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/20.png)

**Recall@6** — a strict yes/no check: does the correct `(act_title, section)` pair appear *anywhere* in the top 6 reranked results? In the worked example, the correct pair (Indian Penal Code, Section 302) shows up at rank 6 — the very last acceptable position — so Recall@6 = 1. One rank later and it would have scored 0.

**Mean Reciprocal Rank (MRR)** — a stricter, position-sensitive version: score = 1 / (rank of the correct result). Correct at rank 1 scores a perfect 1.0; correct at rank 6 scores a much weaker 0.167; not found at all scores 0. Two systems can tie on Recall@6 while MRR reveals one of them is burying the right answer near the bottom of the acceptable range.

**Evaluation setup:** a **20-question gold-labeled test set**, hand-curated with the correct `(act_title, section)` pair for each, spanning all 10 Acts present in the first 200 dataset records — small, but deliberately built to reflect the whole corpus rather than one lucky Act.

### 7.2 Generation Metrics

![Generation Metrics](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/21.png)

Three checks, run with DeepEval:

**1. Citation Correctness (a custom GEval metric)** — the strictest of the three. Every factual claim in the generated answer must have a citation, that citation must actually be present in the retrieved context, and the cited section must genuinely support the claim. This catches a subtle failure a plain faithfulness check would miss: an answer that's *technically true* but cites the *wrong* section as its source.

**2. Answer Relevancy** — does the response actually address what was asked, or does it drift off-topic? **Example given:** asked for the punishment for murder under the IPC, an answer that only explains general IPC rules — without ever mentioning murder's actual punishment — scores poorly here, even if every word in it happens to be true.

**3. Faithfulness** — does the answer avoid claims that contradict, or simply aren't supported by, the retrieved context? **Example given:** a claim like "bail is mandatory for all offences," when the retrieved context says nothing about mandatory bail at all, scores a **low faithfulness score** — this is the formal name for the "confidently invents a specific detail that was never actually there" failure discussed in the other Video Notes file's Generation-Side Failures section.

---

## 8. Is This System "Agentic"? — RAG vs. Fine-Tuning vs. Agents

![System Classification: RAG, Fine-tuning, and Agents](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/22.png)

### 8.1 Defining Agentic Behavior

![Defining Agentic Behavior](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/23.png)

A **fixed, linear pipeline** always runs the exact same steps in the exact same order: query → retrieve → rerank → generate → return. No decision points, no adapting.

An **agentic system** instead runs a loop: **Perceive** (take in the query and retrieved documents) → **Plan** (reason about what to do next) → **Act** (actually retrieve, search, or generate) → **Observe** (check whether the outcome was good enough) — and that loop can send execution back around again rather than always marching straight through to the end.

This system earns the "agentic" label through three specific behaviors, all already covered above:

- **Confidence-based routing** (Section 5.5) — deciding, per query, whether to trust the local corpus or fall back to the web.
- **Query decomposition** (Section 5.3) — deciding, per query, whether it even needs to be split into sub-questions.
- **Conditional tool use** — invoking web search only *when* local knowledge is judged insufficient, not on every query regardless.

### 8.2 Comparative Framework

![Comparative Framework](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/24.png)

A clean way to keep these three ideas separate, since they get conflated constantly:

| Approach | What it actually does |
|---|---|
| **Fine-tuning** | Bakes domain behavior and style directly into the model's own weights |
| **RAG** | Grounds the model in external, updatable knowledge — swap the data without retraining anything |
| **Agents** | Adds multi-step reasoning and the ability to dynamically choose which tool to use |

**The important point:** these are not competing choices — they're complementary layers. A real production system, this one included, typically uses **RAG as its core** (this is fundamentally a retrieval-augmented system) **with agentic components layered on top** (routing and conditional tool use) — and could add fine-tuning on top of both if the domain's writing style needed it too.

### 8.3 System Positioning

![System Positioning](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/25.png)

Worth being precise about, especially for an interview: this system is honestly described as **"a RAG system with agentic components," not a fully autonomous agent.**

| What it is | What it is *not* |
|---|---|
| Retrieval-augmented generation at its core | A fully autonomous agent |
| Agentic behavior limited to routing and tool use | No open-ended, self-directed multi-step planning |
| A deterministic workflow with predefined steps | No continuous self-evaluation and adaptation of its own strategy |

**Three named directions for pushing it further toward real autonomy:**

1. **Self-correction via re-retrieval** (CRAG-style) — automatically detect a low-confidence or unsupported answer and trigger a fresh retrieval attempt to fix it, rather than just labeling it low-confidence and moving on.
2. **Dynamic tool selection** — replace the single fixed confidence threshold with a genuine policy that picks the most appropriate tool for each specific query's context and goals.
3. **Multi-step reasoning across decomposed sub-queries** — let the system reason iteratively across the sub-questions from Section 5.3, rather than treating each sub-query as a fully independent, unconnected retrieval.

---

## 9. Key Takeaways

![Key Takeaways](Building%20an%20Optimized%20RAG%20Pipeline%20for%20Legal%20Query%20Resolution/26.png)

1. Built an end-to-end RAG pipeline for answering questions from a real Indian legal dataset.
2. Combined dense semantic embeddings with BM25 sparse embeddings for hybrid retrieval.
3. Improved retrieval with metadata filtering, adaptive top-k, RRF, MMR, and BGE reranking.
4. Used small-to-big (parent-child) retrieval: precise child chunks for search, full parent sections for generation.
5. Orchestrated the whole workflow with LangGraph — rewriting, decomposition, retrieval, routing, generation.
6. Added SQLite-based conversational memory so contextual follow-up questions actually work.
7. Implemented confidence-based routing between the local knowledge base and authoritative legal web sources.
8. Generated grounded answers with Act-and-Section citations, using interchangeable OpenAI, Groq, or Gemini models.
9. Evaluated retrieval with Recall@k and MRR, and generation quality with DeepEval (citation correctness, relevancy, faithfulness).
10. Learned how fine-tuning, RAG, and agents are complementary layers — not competing choices — in a production-grade system.

**The closing thought:** every technique in this session already existed as a separate idea in the *Retrieval Optimization Techniques* note and the *Current State of RAG* session — hybrid search, reranking, query rewriting, confidence gating, evaluation. What this session actually demonstrates is that a trustworthy RAG system isn't about knowing any one of these tricks; it's about wiring *all* of them together into one coherent pipeline, in the right order, with the paralegal knowing exactly when to say "I don't know."

---

## 🎤 Interview Prep — Mock Interview (Production Legal/Domain-Specific RAG Architecture, ~4 Years' AI Engineering Experience)

*This session's real focus was wiring every retrieval-optimization technique into one coherent, production-shaped pipeline over a genuinely hard domain — so this interview set is deliberately different from the ones in* LangChain.md*,* Introduction to Vector Database.md*, and* Current State of RAG - Video Notes.md*: it's about the specific architectural decisions this pipeline makes (composite keys, parent-child chunking, RRF, confidence gating, decomposition, rewriting, agentic classification, evaluation) and *why* each one exists. Same two-layer format as those sections: a plain-language answer with an example, then a crisp, technically precise version. Try answering out loud first.*

---

**🎙️ Interview Q1:** "Why can't 'Section 6' alone be used as a unique identifier when you're building a RAG system over a large collection of legal Acts?"

**✅ Strong answer:** "Because section numbers repeat across completely unrelated documents — dozens of different Acts each have their own 'Section 6,' saying completely different things. It's like a filing cabinet where every drawer has a folder labeled 'Page 6': useless unless every folder also says which book that page came from. The fix is to treat the *pair* — (which Act, which Section) — as the real primary key, not the section number by itself, and to carry both fields in the metadata payload stored alongside every chunk so retrieval, filtering, and citation can all key off the composite identifier."

**🎯 Standard Interview Answer:** "This is a data-modeling problem that surfaces the moment you profile the real corpus instead of assuming a naive schema: the section number is not globally unique, so `(act_title, section)` is the true composite key. Concretely, this means storing both fields as payload metadata on every vector-store point, using the composite key for citation generation, and optionally allowing metadata pre-filtering on `act_title` so a query can be scoped to one specific Act before search even begins — directly resolving the ambiguity rather than hoping semantic similarity sorts it out after the fact. This generalizes beyond law: any corpus with repeating structural labels (chapter numbers, article numbers, invoice line numbers) needs the same treatment — profile the data first, then design the key, never assume a bare label is unique."

---

**🎙️ Interview Q2:** "What is parent-child (small-to-big) retrieval, and why not just embed and search the full section text directly?"

**✅ Strong answer:** "It's giving your search system sticky-note index tabs while leaving the actual full page of the law book untouched. You cut each section into small child chunks purely so *search* can be precise — matching a tight, focused piece of text against the query — but once a match is found, you hand the LLM the *entire* parent section, not just the matched snippet, so no clause is ever interpreted missing the sub-clause that defines its exception. Every child chunk carries a `parent_doc_id` pointing back to its full parent, which is how the system knows what to actually retrieve for generation once search has done its job on the small pieces."

**🎯 Standard Interview Answer:** "This resolves the same trade-off the Sentence Window technique addresses, but head-on instead of by picking a single chunk size: small chunks (roughly 100-200 tokens) give precise, high-specificity embeddings and stronger retrieval precision, but discard surrounding context; large chunks (roughly 500-1500 tokens) preserve context but produce embeddings that average multiple concepts together, reducing retrieval precision. Parent-child retrieval gets both by decoupling what's *searched* from what's *generated from*: only small child chunks are indexed and matched against the query for precision, while each carries a `parent_doc_id` linking back to a larger parent chunk or full section, which is what actually gets passed to the LLM once retrieval identifies the right region — precision at search time, completeness at generation time, without compromising either."

---

**🎙️ Interview Q3:** "Walk me through why you'd fuse a BM25 score and a cosine-similarity score with Reciprocal Rank Fusion instead of just averaging them."

**✅ Strong answer:** "Because the two numbers aren't measuring the same thing on the same scale — cosine similarity is bounded between −1 and 1, while a BM25 score is unbounded, anywhere from 0 to infinity. If you average them directly, whichever score happens to have the larger range dominates every single time, regardless of which retrieval method actually mattered more for that particular query. RRF sidesteps this entirely by throwing away the raw scores and using only *rank position* — a document that's ranked #1 on both lists scores far higher than one that's #1 on only one list and absent from the other, and 'being ranked #1' means the exact same thing no matter which scoring system produced that ranking."

**🎯 Standard Interview Answer:** "RRF computes a fused score as RRF(d) = Σ 1/(k + rank_r(d)) across each retriever r, where k is a smoothing constant (commonly 60) that flattens the gap between adjacent top ranks — rank 1 contributes 1/61 ≈ 0.0164 and rank 2 contributes 1/62 ≈ 0.0161, a gentle decline rather than a cliff. Because RRF operates purely on rank position, it's scale-independent by construction and requires no score normalization or per-query tuning, unlike a weighted-sum fusion, which needs its weights calibrated and can be dominated by whichever score distribution happens to have the larger numeric range. The trade-off is that RRF discards magnitude information entirely — a document ranked #1 by a landslide and one ranked #1 by a hair both just count as 'rank 1.'"

---

**🎙️ Interview Q4:** "What's the difference between Recall@k and Mean Reciprocal Rank, and could two retrieval systems tie on one while differing sharply on the other?"

**✅ Strong answer:** "Recall@k is a blunt yes/no check: does the correct answer appear *anywhere* in the top k results? Nothing about *where* in those k results it landed. MRR is stricter about position: it scores 1 / (rank of the correct result), so a correct answer at rank 1 scores a perfect 1.0, but the same correct answer at rank 6 only scores about 0.167. Yes, two systems can absolutely tie on Recall@6 — both technically 'found' the right answer within the top 6 — while MRR reveals that one of them buried it near the very bottom of that acceptable range and the other put it right at the top, which matters a lot in practice since users rarely read past the first couple of results."

**🎯 Standard Interview Answer:** "Recall@k is a binary, threshold-based metric — 1 if the ground-truth item appears anywhere in the top-k retrieved set, 0 otherwise — so it measures coverage but is blind to rank within that window. MRR = 1/rank of the first relevant result, so it's a continuous, position-sensitive metric that directly penalizes burying the correct answer near the bottom of an otherwise-passing window. The two are complementary rather than redundant: Recall@k tells you whether your retrieval depth (k) is sufficient at all, while MRR tells you whether reranking is actually doing its job of pushing the correct result toward the top — a system can have perfect Recall@6 and still have a mediocre MRR if it's consistently landing the right answer at rank 5 or 6 instead of rank 1."

---

**🎙️ Interview Q5:** "Explain confidence-gated fallback in a RAG pipeline — how does the system decide whether to trust its own knowledge base or fall back to a live web search?"

**✅ Strong answer:** "This is the system finally learning to say 'I don't know, let me check with someone else' instead of confidently guessing. After reranking, the top result's relevance score becomes a confidence signal: above a threshold, the system trusts its local corpus and generates the answer from those retrieved chunks. Below that threshold, it doesn't force an answer from weak evidence — it falls back to a live, scoped web search (restricted to trusted, authoritative sources, not the open web) and generates from that instead. Either way, the final answer is tagged with where it actually came from, so nothing is presented as more certain than it really is."

**🎯 Standard Interview Answer:** "This is the core idea behind Corrective RAG (CRAG): a retrieval evaluator scores the top reranked result, and that score routes execution down one of two (or, in the fuller CRAG formulation, three) paths — trust the local retrieval and generate directly above a high-confidence threshold, discard it and reformulate as a fresh external query below a low-confidence threshold, and in the three-path variant, merge local and external results when the score falls in an ambiguous middle band. The engineering cost is that both thresholds require domain-specific calibration — too permissive and low-quality local matches get generated from anyway; too strict and the system offloads to (slower, less controlled) web search unnecessarily often. Attaching an explicit `SOURCE: LOCAL` / `SOURCE: WEB` tag to every answer is what actually operationalizes trust calibration for the end user, independent of how well-tuned the threshold is."

---

**🎙️ Interview Q6:** "A user asks a compound legal question — grounds for divorce *and* the filing procedure — in one sentence. Why does that need query decomposition instead of a single retrieval call?"

**✅ Strong answer:** "Because it's really two separate questions stitched together, and retrieving for it as one blended query risks partially answering both instead of fully answering either — the embedding for the combined sentence ends up as some average of two different topics, matching okay-ish chunks for each half rather than great chunks for either. The fix is to split the compound question into its two independent sub-questions, retrieve separately for each — so each one gets its own focused search — and then merge and de-duplicate the combined results before generation."

**🎯 Standard Interview Answer:** "A compound or multi-intent query dilutes the query embedding across multiple semantic targets, a failure mode sometimes called semantic dilution, which degrades retrieval precision for every intent bundled into the single query rather than for just one of them. The standard mitigation is a decomposition step — typically a binary classifier prompt that first detects whether a query is single- or multi-intent, then splits a multi-intent query into atomic sub-queries, retrieves independently per sub-query, and merges and deduplicates the combined candidate pool before reranking and generation. This directly increases faithfulness and coverage versus single-pass retrieval, at the cost of one extra classification call and, for genuinely multi-intent queries, N times the retrieval calls."

---

**🎙️ Interview Q7:** "Why is query rewriting often called the single highest-leverage improvement for multi-turn RAG — and also one of the most commonly skipped?"

**✅ Strong answer:** "Because a natural follow-up question is almost never self-contained. Someone asks 'What are the provisions under Section 6?' and then follows up with 'For women residents only?' — that second question has no subject on its own; it only makes sense combined with the first. Query rewriting fixes this with one extra, cheap LLM call before retrieval: take the conversation history plus the new turn, and rewrite it into a standalone question — 'What are the provisions under Section 6 of the Aadhaar Act for women residents only?' — *before* it ever reaches the retriever. It's high-leverage because it's the single fix that makes an otherwise-working RAG system stop quietly falling apart the moment a real user asks a natural follow-up, and it's commonly skipped because a system built and tested only on standalone questions never surfaces the problem until real multi-turn usage exposes it."

**🎯 Standard Interview Answer:** "Multi-turn user queries very commonly contain unresolved coreferences or context that depends entirely on prior turns — one production analysis found this in over 60% of follow-up messages — so retrieval performed directly on the raw follow-up text matches against the wrong (or no) topical anchor. Query rewriting inserts a decontextualization step: an LLM call that, given recent session history and the new turn, collapses the exchange into one self-contained query, resolving pronouns and implicit references before the retriever ever sees the query. It's considered the highest-leverage multi-turn fix specifically because it's a single, localized addition (one extra LLM call, no retrieval or index changes) that fixes an entire class of failure that otherwise degrades silently — a system with excellent single-turn retrieval metrics can still fail the majority of realistic multi-turn conversations without it, which is exactly why it needs to be tested for explicitly rather than assumed from single-turn evaluation numbers."

---

**🎙️ Interview Q8:** "This pipeline does confidence-based routing and query decomposition — does that make it a fully autonomous agent?"

**✅ Strong answer:** "No, and it's worth being precise about that distinction. A fixed pipeline always runs the same steps in the same order — retrieve, rerank, generate, done. A fully autonomous agent runs an open-ended loop — perceive, plan, act, observe, and decide for itself whether to loop back around again. This system sits in between: it makes a handful of specific, bounded decisions per query — whether to trust local retrieval or fall back to the web, whether a query needs splitting into sub-questions — but it doesn't do open-ended, self-directed multi-step planning or continuously re-evaluate its own strategy. The honest description is 'a RAG system with agentic components,' not 'an autonomous agent that happens to use RAG.'"

**🎯 Standard Interview Answer:** "RAG, fine-tuning, and agents solve different problems and are complementary layers, not competing choices: RAG grounds a model in external, updatable knowledge; fine-tuning changes the model's own behavior or style; agents add multi-step reasoning and dynamic tool selection on top of either. A practical rule of thumb: if the knowledge changes frequently, that's a RAG problem; if the required style, tone, or output format needs to change, that's a fine-tuning problem; if the task needs multi-step actions across tools, that's an agentic problem. This system is RAG at its core with two narrowly-scoped agentic behaviors layered on — confidence-based routing and conditional query decomposition — which qualifies it as agentic in a limited, bounded sense, but it lacks the defining trait of a fully autonomous agent: an open-ended perceive-plan-act-observe loop that can revise its own strategy and re-enter itself indefinitely, rather than following a deterministic, predefined set of branch points."

---

**🎙️ Interview Q9:** "Why would a dedicated 'citation correctness' metric catch a failure that a general faithfulness check would miss?"

**✅ Strong answer:** "Because an answer can be completely accurate in general and still cite the *wrong* specific source for a specific claim — and a faithfulness check, which just asks 'does this answer avoid contradicting the retrieved context,' can pass that answer without ever verifying the citation actually supports that exact claim. A dedicated citation-correctness check goes one level deeper: for every factual claim in the answer, it verifies that a citation exists, that the citation is genuinely present in the retrieved context, *and* that the specific cited section actually supports that specific claim — catching the subtle case of a technically-true statement attributed to the wrong Act or Section."

**🎯 Standard Interview Answer:** "Faithfulness measures whether the generated answer is grounded in the retrieved context as a whole — it fails on hallucinated or unsupported claims, but it's satisfied as long as *some* part of the retrieved context supports the claim somewhere, without checking whether the specific citation attached to that claim is the actual source of support. A custom citation-correctness metric (implemented here as a G-Eval-style custom metric in DeepEval) closes that gap by verifying the full claim → citation → supporting-passage chain per factual statement, which is what catches an answer that is faithful in aggregate but attributes an individual claim to the wrong section — a failure mode that's especially costly in a legal domain, where the specific citation *is* the deliverable, not just supporting color."

---

**Sources consulted while calibrating this section:**
- [RAG Interview Questions (2026): The Complete Guide — GitGood](https://gitgood.dev/blog/complete-guide-rag-interview-questions-2026)
- [Advanced RAG 01: Small-to-Big Retrieval — Sophia Yang, TDS Archive](https://medium.com/data-science/advanced-rag-01-small-to-big-retrieval-172181b396d4)
- [What is Reciprocal Rank Fusion? — ParadeDB](https://www.paradedb.com/learn/search-concepts/reciprocal-rank-fusion)
- [Retrieval Metrics Tutorial: Recall@k and MRR Explained — Medium](https://medium.com/@rajnish_khatri/retrieval-metrics-tutorial-recall-k-and-mrr-explained-d2f12afb9c89)
- [What Is Corrective RAG (CRAG)? — FutureAGI Glossary](https://futureagi.com/glossary/corrective-rag/)
- [RAG vs Fine-Tuning vs Agents: A Decision Framework for 2026 — BEON.tech](https://beon.tech/blog/rag-vs-fine-tuning-vs-agents/)
- [Query Decomposition: Tackling Semantic Dilution in RAG — Data Engineer Things](https://blog.dataengineerthings.org/query-decomposition-tackling-semantic-dilution-in-rag-3fb4307126ff)
- [RAG Query Rewriting: 4 Layers That Fix Multi-Turn Retrieval — Alhena.ai](https://alhena.ai/blog/query-rewriting-before-retrieval-multi-turn-rag/)
- [Using the RAG Triad for RAG Evaluation — DeepEval](https://deepeval.com/guides/guides-rag-triad)
- [LangGraph state machines explained with a code example — n4n.ai](https://n4n.ai/blog/langgraph-state-machines-explained-with-a-code-example/)

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape:

- The heading is the question **as asked** — often phrased as a statement to confirm.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** (sub-heading with an emoji) carries the explanation, plus a comparison table when two concepts are being contrasted.
- Earlier answers are referred back to ("from Q1") so the picture stays connected.
- A bolded **One line:** summary closes the answer, restating the whole thing in a single sentence.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

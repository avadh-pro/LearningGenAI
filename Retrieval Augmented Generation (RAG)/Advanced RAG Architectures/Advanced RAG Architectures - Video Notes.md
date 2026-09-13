# Advanced RAG Architectures — Video Notes

Notes from a session on **advanced RAG architectures**. This is deliberately *not* one linear pipeline — it's a survey of the different techniques that can be plugged into a RAG system at each stage, collected together and then assembled into one general flow at the end.

The session is built around the LangChain RAG architecture diagram (`Architecture Overview .png` in this folder), which maps the whole landscape onto six coloured regions: **Query Translation, Routing, Query Construction, Indexing, Retrieval, and Generation**.

![RAG Architecture Overview](Architecture%20Overview%20.png)

### Quick glossary: the acronyms shown in the diagram

The green **Retrieval** box and the purple **Generation** box each pack a few dense acronyms into a small space. Here's what each one means in plain language, before the rest of this document unpacks them in full further down.

**In the Retrieval region:**

- **RankGPT** — using the LLM itself as the re-ranker, instead of a dedicated re-ranking model like Cohere's Rerank. You hand the model the query plus the list of retrieved documents and ask it to directly judge and reorder them by relevance, the way a person skimming a stack of search results would put the most useful one on top.
  > **Example:** retrieve 20 candidate paragraphs about "vaccine side effects," then ask an LLM to "rank these 20 passages from most to least relevant to the question," and use *its* ordering instead of the vector database's original ranking.

- **RAG-Fusion** — send the question out as several different rephrasings at once, retrieve for each one separately, then merge everything into a single ranked, de-duplicated list using RRF (Reciprocal Rank Fusion). Explained in full in Section 2.2.
  > **Example:** "What is LangChain?" fans out into three similar queries, each is searched independently, and the combined results are fused so no document shows up twice.

- **CRAG (Corrective RAG)** — grade the retrieved documents before trusting them, and if none pass the grade, don't just give up: reroute the question to a fresh source, like a live web search, instead of returning "no context found." It shows up twice in the diagram — once under Ranking/Refinement, once under Active Retrieval — because the same corrective idea applies both to filtering what came back and to going and fetching something better. Explained in full in Section 7.
  > **Example:** ask about a product released yesterday. The vector database has nothing recent, the grader flags the results as "not relevant," and the query is rerouted to a live web search instead of failing outright.

**In the Generation region:**

- **RRR (Rewrite-Retrieve-Read)** — paired with Self-RAG here because they solve the same class of problem from the other end: instead of only checking the retrieved *documents* before generating, also check the generated *answer* itself afterward. If the answer's quality isn't good enough, loop back and either rewrite the question or retrieve again with more context. Explained in full in Section 8.
  > **Example:** the model answers a question, but a grading pass judges the answer as vague or unsupported. Rather than showing that to the user, the pipeline loops back, retrieves again with a rewritten query, and generates a second attempt.

See also *Retrieval Augmented Generation (RAG).md* for the basics and *RAG Workflow - Three Steps.md* for the fundamental retrieve → augment → generate loop. This document assumes those are understood and picks up from there.

---

## 1. Chunking Strategies

### What is a chunk?

A **chunk is just a small piece of text extracted from a document**. The document can be anything — a PDF, a Word file, even text extracted from an image. When a large document is stored in a vector database, it isn't stored whole; it's broken into smaller batches, and each of those batches is a chunk.

### Why chunking matters: memory limitations

The core constraint is the **LLM's token limit**. Every model has a fixed context window, and that window has to hold the input *and* the output.

> Suppose a model has a 4,000-token limit. If you feed it 3,000 tokens of input and expect 5,000 tokens of output, the model simply can't do it — it will produce a truncated or irrelevant response.

Chunking converts the original text into pieces small enough that the relevant context fits comfortably inside the window, leaving room for the model to actually answer.

### Chunk optimization approaches

From the **Indexing** section of the diagram, splits can be made on different boundaries:

| Strategy | Split on |
|---|---|
| **Character** | A fixed number of characters (the simplest, what `RecursiveCharacterTextSplitter` does by default) |
| **Section** | Document structure — headings, sections |
| **Semantic** | Meaning shifts — a *Semantic Splitter* starts a new chunk when the topic changes |
| **Delimiter** | Explicit markers in the text |

**One line:** chunk size is a trade-off — too big and it won't fit the context window, too small and each chunk loses the meaning that made it worth retrieving.

---

## 2. Query Translation

Everything in this section happens **before retrieval**. The user's question, as typed, is often a bad search query. Query translation fixes the question first.

### 2.1 Query Rewriting

**The problem.** A user's question may be messy, distracted, or full of irrelevant context. The example used in the session:

> *"man that SBF blowup is crazy! What is LangChain?"*

Passed straight into a RAG pipeline, the retriever gets confused by the noise about Sam Bankman-Fried and pulls irrelevant documents. The answer that comes back is correspondingly vague — you can't even tell which question was being answered. **Randomness in the question produces randomness in the answer.**

This is a realistic failure mode: once real users are on your platform, they *will* ask questions shaped like this.

**The fix.** LangChain provides a ready-made rewrite component (available through the LangChain Hub). Its prompt is essentially:

> *"Provide a better search query for a web search engine to answer the given question."*

Run the messy query through the rewriter first, and it becomes something meaningful:

| Stage | Query |
|---|---|
| Original | *"man that SBF blowup is crazy! What is LangChain?"* |
| Rewritten | *"What is the definition and purpose of LangChain?"* |

Feed **that** into the actual RAG pipeline, and retrieval and generation both become far more accurate.

**Note on the alternative:** sometimes you'd rather the model say *"I don't have this in my context"* or *"I don't understand your question"* instead of rewriting. That's a separate design decision, handled later with grading and guardrails.

### 2.2 Multi-Query Generation and RAG-Fusion

Instead of rewriting one query into one better query, **generate several queries from the original** and retrieve for all of them.

The example used (from LlamaIndex) starts with:

> *"How do the models developed in this work compare to open-source chat models on the benchmarks tested?"*

The model generates three sub-queries:

1. Comparison of models developed in this work to open-source chat models
2. Performance evaluation of models on benchmarks
3. *(and so on)*

Retrieval runs **for each generated query**, and the result sets are then fused together.

**Reciprocal Rank Fusion (RRF)** is the algorithm that does the fusing. Two things make it the right choice here:

- It **ranks** all retrieved documents across all the query result sets.
- It **de-duplicates**. If the same document was retrieved by several of the sub-queries, it appears once, not three times.

That de-duplication is the crucial part. If you ask for five documents, you get five *unique* documents with no redundant information — where a plain re-ranker would happily hand you the same document three times and waste your context window.

> **The flow:** query → generate multiple similar queries → retrieve for all of them → fuse with RRF (ranked and de-duplicated) → pass to the LLM.

Result for the example: *"The models developed in this work, specifically the Llama 2 chat models, outperform open-source models on most of the benchmarks tested."*

### 2.3 Query Decomposition

Break a complex question into **sub-questions** that are each answerable on their own, retrieve for each, then combine. Closely related to multi-query, but the sub-questions are *components* of the original rather than *rephrasings* of it.

### 2.4 Step-Back Prompting

When a specific question retrieves nothing useful, **step back to a more general question first**, then work down to the specific one.

The example from the session:

> *"Who won the first prize in shooting at the Olympics?"*

A step-back approach first establishes the broader context — *which* Olympics, when was the last Olympics held, were shooting events held there — and only then narrows to who won. Retrieving the general context first gives the specific query something to stand on.

### 2.5 HyDE (Hypothetical Document Embeddings)

Rather than embedding the *question*, have the LLM write a **hypothetical answer document** and embed that instead. The reasoning: a fake answer looks much more like a real answer chunk than a question does, so the vector comparison is apples-to-apples. Shown in the diagram under **Pseudo-documents**.

---

## 3. Specialized Embeddings — Fine-Tuning the Embedding Model

An embedding model converts a word or passage into a vector — and **every embedding model produces a different representation** of the same input.

The problem arises in **domain-specific work**. Take a financial domain: a general-purpose embedding model may represent certain finance terms poorly, because it never saw them used that way during training. Retrieval then fails, not because the pipeline is broken but because the vectors are wrong.

**The fix** is to fine-tune the embedding model on your domain, so it produces high-quality embeddings for *your* vocabulary. Better embeddings at storage time means better retrieval at query time.

The diagram also lists **ColBERT** under specialized embeddings — a late-interaction model that scores at token level rather than compressing a whole chunk into one vector.

> This connects back to earlier weeks: fine-tuning an embedding model was covered previously, and LLM fine-tuning was covered in Week 2.

---

## 4. Types of RAG

There is no single RAG architecture — people build many. These are the main families.

| Type | Shape |
|---|---|
| **Naive / Direct RAG** | query → retrieve → LLM → response |
| **Two-Stage RAG** | query → retrieve (top 20–25) → **re-rank** → top-K → LLM → response |
| **Active / Adaptive Retrieval RAG** | retrieve → grade → refine query → retrieve again → loop until good |
| **Fusion RAG** | fan out across queries / retrievers / re-rankers → fuse results |

### 4.1 Naive RAG

The most direct approach: take the query, retrieve documents, pass them to the LLM, generate the response. Everything else on this page is an improvement on this baseline.

### 4.2 Two-Stage RAG (Retrieval + Re-ranking)

Retrieve a wide net of documents, then use a **re-ranker** to pick the genuinely best ones before they reach the LLM.

**In LangChain** this is built with Cohere's Rerank model plus a `ContextualCompressionRetriever`, which wraps the re-ranker around the base retriever.

**Worked example from the session.** Three documents were retrieved with IDs `11, 9, 14`. After re-ranking, the order became `14, 11, 9` — the document the vector search ranked *last* was actually the most relevant.

At three documents the difference is minor. Scale it up and it matters a lot: retrieve ten documents without a re-ranker and you get IDs 1–10; add a re-ranker and documents 5 and 7 might be replaced entirely by 22 and 30 — documents the plain vector search had ranked far down the list.

#### 💬 Asked in the session: "Can you explain re-ranking again?"

Walk through it concretely:

1. Your model can handle **three documents** at a time before generating a response.
2. You have a big document, chunked and stored in a vector database.
3. You retrieve the **top 25** documents for the query — a wide net.
4. If you just passed the top 3 straight through, there's a real chance one of them is irrelevant.
5. So you apply the **re-ranker**, which scores all 25 against the query and picks the 3 that are genuinely most relevant.

The key insight: **a re-ranker is a completely different model from the retriever.** The retriever is designed to *fetch* candidates from a vector database quickly. The re-ranker is designed to *judge relevance* between a query and a document, and it's much better at that because it looks at the query and document together rather than comparing two pre-computed vectors.

> Re-ranking isn't strictly necessary every time, but it is a **standard part of a modern RAG workflow**.

### 4.3 Active / Adaptive Retrieval RAG

A loop rather than a straight line:

1. Retrieve.
2. Grade the result.
3. If unsatisfactory, **refine the query** and retrieve again.
4. Repeat until the result is good enough.

This needs a **grading script** to decide when to stop. Without one, you need a hard cap — refine two or three times, then return whatever you have — otherwise the system loops forever.

### 4.4 Fusion RAG

"Fusion" is a general pattern, not one specific technique. You can fuse at several points:

- **Fuse queries** — one query becomes many, retrieve for all, combine.
- **Fuse retrievers** — one query sent to several different retrievers, combine what comes back.
- **Fuse re-rankers** — multiple re-rankers, combine their judgements.

**One line:** in Fusion RAG you can play with queries, with retrievers, or with re-rankers — any kind of fan-out-and-combine counts.

---

## 5. Query Routing

### Why routing exists

Imagine building a RAG system for school students covering physics, chemistry, maths and biology. Store all of it in **one** vector database and you get collisions.

**The concrete failure:** thermodynamics appears in *both* physics and chemistry, with different laws in each. A query about it retrieves a mix of both, and the model produces a confused answer that blends two subjects.

**A second failure, from the session:** a particular formula appeared in both the physics document and the maths document. The retriever ranked the *maths* version first and never retrieved the physics one — so the model answered with the wrong formula, when the user clearly wanted the physics one.

**The fix:** store each domain in its own vector database, and put a **router** in front that decides which one a query should go to. A physics question only ever touches the physics store. Retrieval relevance goes up and the answer gets more accurate.

**The other big use case is multi-tenancy.** If you provide RAG solutions to several different banks, their data cannot all live in one place. Each customer's data goes in its own store, and a router directs each query to the right one.

### 5.1 Logical Routing

**Let rules or an LLM pick the database.** Two ways to build it:

- **A plain Python script.** If the query contains the word *finance*, send it to the finance retriever. No model needed — routing does not always require an LLM.
- **A text-classification model or an LLM.** Give it the query plus a description of each available database, and let it decide. For example, a classifier that recognises a text as invoice-related and routes accordingly.

With an LLM, the router is essentially a prompt: describe each data source, pass in the user query, and have the model return which store to use.

### 5.2 Semantic Routing

**Embed the query and compare it against embedded prompt templates.**

You write a physics template and a maths template. The incoming user query is embedded, compared for **semantic similarity** against each template, and routed to whichever it's closest to.

Semantic routing is generally the better of the two — but on a domain-specific dataset it may need a fine-tuned embedding model to work well.

> **Think of routing as a module.** You can attach it when you need it; it isn't required in every system. If all your data is one bank's documents, you don't need a router at all.

---

## 6. RAPTOR

**RAPTOR = Recursive Abstractive Processing for Tree-Organized Retrieval.**

*(The name is worth getting right — it's* Abstractive*, meaning it writes summaries, not* extractive*.)*

It's called **tree-organized** because the documents aren't stored as one flat list — they're built into a tree of increasingly abstract summaries.

**How it works:**

1. **Embed** all the documents.
2. **Cluster** them. If documents 1 and 2 land in the same cluster, they contain similar information.
3. **Summarize** each cluster into a single, more abstract document. This step needs a model to do the summarizing.
4. **Repeat** — embed the summaries, cluster them, summarize again.

How many levels you build is a judgement call: keep going **until information starts being lost**, or until the summaries stop being accurate enough to answer from.

The final tree is stored in the vector database, so a query can be answered from a detailed leaf chunk *or* from a high-level summary, depending on how broad the question is. That's why the diagram lists it under **Hierarchical Indexing**.

---

## 7. Corrective RAG (CRAG)

CRAG belongs to a family of research architectures — **Corrective RAG, Self-RAG, self-reflective RAG** — all of which aim to improve RAG as a whole system, both the retrieval part and the response part.

**The flow:**

1. The user query goes to the retriever, which returns documents.
2. A **grading script** evaluates each document for relevance to the query. This grader is not fixed — it can be an LLM, an embedding model, a semantic-similarity model, or a custom NLP script.
3. **If at least one document is genuinely relevant** → pass it to the LLM and generate the response.
4. **If no relevant document is found** → don't just reply *"no context found."* Instead, **reroute the query to a web search**, scrape the results, and generate the answer from that text.

Libraries exist that run the web search and extract the text for you (many are paid), or you can write custom scraping scripts.

> Web search is one *suggested* correction, not the only one. At that same decision point you could equally apply query decomposition, query rewriting, or any other translation technique from section 2.

---

## 8. Self-RAG — Grading the Answer

Everything above corrects **retrieval**. Self-RAG corrects **generation**.

After the answer is generated, don't send it straight to the user. First judge it — again with an LLM or a script that assesses relevance. If the answer isn't good, feed it back with the original query, note that it wasn't relevant, and run the loop again — this time with more information than before.

**The general principle:** you can place a feedback checkpoint **after retrieval** *and* **after generation**. If either the retrieved documents or the final answer fail their check, the pipeline loops back and tries again with more context.

The diagram lists **Self-RAG and RRR** here, described as *"use generation quality to inform question re-writing and/or re-retrieval of documents."*

---

## 9. The Complete RAG Flow

Pulling every piece above into one general (not universal) pipeline — this is the diagram read left to right.

### Stage 1 — Question / Query Translation

Everything that reshapes the question before it's used:

- Query decomposition and query rewriting — rephrase the input question
- Multi-query generation + RAG-Fusion — many queries, retrieve for each, fuse with RRF
- **Step-back prompting** — go general first, then specific
- **HyDE** — embed a hypothetical answer document instead of the question

### Stage 2 — Routing

Send the query to the right place:

- **Logical routing** — let an LLM (or a rule) choose the database
- **Semantic routing** — embed the question, choose by similarity to prompt templates

### Stage 3 — Query Construction

Now translate the query into whatever query *language* the target store speaks:

| Target | Technique |
|---|---|
| **Relational DB** | Text-to-SQL (natural language → SQL, or SQL with PGVector) |
| **Graph DB** | Text-to-Cypher (natural language → Cypher) |
| **Vector DB** | **Self-query retriever** — auto-generates metadata filters from the query |

The self-query retriever is worth calling out: it reads the query and automatically builds **metadata filters** from it. Not every vector database supports this — check before relying on it.

### Stage 4 — Indexing

How the data was stored in the first place, which determines what can be retrieved:

- **Chunk optimization** — character / section / semantic / delimiter splitting (Semantic Splitter)
- **Multi-representation indexing** — store the chunk *and* a summary of it, so you can retrieve on the compact summary but feed the full chunk to the model (Parent Document, Dense X)
- **Specialized embeddings** — domain fine-tuned models, ColBERT
- **Hierarchical indexing** — RAPTOR's tree of summaries at multiple abstraction levels

### Stage 5 — Retrieval

Everything applied to documents after they come back:

- **Ranking** — Re-Rank, RankGPT, RAG-Fusion: rank, filter or compress documents by relevance
- **Fusion** — combine results from multiple retrievers using RRF
- **Two-stage RAG** — retrieve wide, re-rank, pass the best few forward
- **Active retrieval / CRAG** — if the documents aren't relevant, re-retrieve or pull from new sources such as the web, then fuse that in

### Stage 6 — Generation

- Generate the answer
- **Self-RAG / RRR** — grade the answer; if it's not good enough, loop back to re-write the question or re-retrieve

---

## Summary

The single most useful idea from this session: **RAG is not one pipeline, it's a set of slots.** At each stage — question, routing, construction, indexing, retrieval, generation — there is a menu of techniques, and a real system picks the few it actually needs.

- **Chunking** is the foundation, and it exists because of the context window.
- **Query translation** fixes bad questions before they ever reach the retriever.
- **Routing** stops domains from contaminating each other.
- **Re-ranking** is a different model doing a different job from the retriever, and it's now standard practice.
- **RRF** is the tool for fusion specifically because it de-duplicates.
- **CRAG and Self-RAG** add feedback loops after retrieval and after generation.

Not all of it is required. Routing is a module you attach when you have multiple domains. Re-ranking helps but isn't mandatory. The skill is knowing which slots your problem actually needs filled.

---

## Q&A

### Q1: Is RRF the same thing as re-ranking? Does it happen before or after re-ranking, where does it fit in the pipeline, and what's the technical interview definition?

**You're right — they're genuinely different mechanisms, and RRF normally runs *before* re-ranking, not after it and not instead of it.**

#### RRF, in the simplest possible terms

RRF is a **math trick for combining several separate "top lists" into one fair combined list** — it never reads or understands anything; it just looks at *where* each item landed on each list.

> **Analogy 🍽️:** three friends each independently rank their own top-10 restaurants. RRF is the referee who combines all three lists into one fair combined ranking — using *only* each restaurant's position on each list. A restaurant that's #1 on all three friends' lists scores far higher than one that's #1 for a single friend and never mentioned by the other two. The referee never actually tastes any food — it's pure arithmetic on rank numbers.

**Re-ranking (a cross-encoder, or RankGPT) is a completely different job.** It's a food critic who actually sits down and reads the query and one document *together*, judging real relevance — much slower, but far more accurate than just counting rank positions.

| | RRF | Re-ranking |
|---|---|---|
| Input | *Multiple* separate ranked lists | *One* list of candidates |
| How it decides | Only rank *position* in each list — pure math | Reads query + document together — real judgment |
| Needs a model? | No | Yes (a cross-encoder, or an LLM like RankGPT) |
| Job | Merge + de-duplicate | Refine the ordering of what's already there |

#### Where it fits in the pipeline

RRF needs multiple lists to exist *before* it can do anything — merging is its entire job. So it naturally happens right after something has produced more than one ranked list (multiple rephrased queries in RAG-Fusion, or a keyword search list plus a vector search list in hybrid search), and *before* any optional re-ranking step, since re-ranking works on a single list, not several:

```
Query → fanned out into multiple queries, or multiple retrieval methods
       → EACH produces its OWN separate ranked list
       → RRF merges all of them into ONE combined, de-duplicated list
       → (optional) Re-ranking (cross-encoder / RankGPT) takes THAT one list
         and refines its order using real semantic judgment
       → Top-K passed to the LLM
```

#### Technical interview definition

"**Reciprocal Rank Fusion (RRF)** is a rank aggregation algorithm that combines multiple ranked result lists into a single ranking without requiring the underlying relevance scores to be comparable, normalized, or even present — it uses only each document's rank *position* in each list. For a document *d*, its RRF score is:

**RRF_score(d) = Σ, over every list *L* containing *d*, of 1 / (k + rank_L(d))**

where `rank_L(d)` is *d*'s 1-indexed position in list *L*, and *k* is a smoothing constant — commonly 60, from the original Cormack et al. (2009) paper — that dampens the impact of very high individual ranks so no single list dominates the fused result. Documents are sorted by this combined score. RRF is popular for combining heterogeneous retrieval signals — merging BM25 keyword results with dense vector results, or merging results from several reformulated queries in RAG-Fusion — because it needs no score normalization across differently-scaled retrievers, and it naturally de-duplicates any document appearing on multiple lists by accumulating its score across all of them."

**One line:** RRF and re-ranking are not the same thing — RRF is a cheap, score-free way to merge *multiple* ranked lists into one by rank position alone, and it runs *before* any re-ranking step, which instead takes that single merged list and refines it using a model that actually judges relevance.

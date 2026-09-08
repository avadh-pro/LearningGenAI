# RAG Workflow: The Three Steps

A simple breakdown of the Retrieval Augmented Generation (RAG) workflow. It consists of three steps:

1. **Query the knowledge base**
2. **Fuse the data**
3. **Generate the response**

Before the steps, one prerequisite concept: the **knowledge base**.

## What is the Knowledge Base?

Imagine you have *n* number of documents, as structured or unstructured data. As you know, LLMs work with **embeddings**. So we convert this data into embeddings and store these documents in a **vector database**. This becomes your **external knowledge database** for the LLM. This is the knowledge base we are referring to here.

> Documents (structured / unstructured) → converted to embeddings → stored in a vector database → **knowledge base** (external knowledge for the LLM)

## Step 1: Query the Knowledge Base

In the initial step of the RAG workflow, a **user submits a query**, which is routed to a **knowledge retrieval system**. This system typically employs advanced techniques such as **dense vector retrieval** or **semantic search** to process the query against the knowledge base.

The goal is to **identify and retrieve the most relevant documents or data segments** from the knowledge repository.

## Step 2: Fuse the Data

The **retrieved documents**, along with the **original user query**, are processed by a GenAI model such as **GPT** or **LLaMA**. This step involves **combining the user's query context with the retrieved information**, enabling the model to synthesize a more informed response.

Techniques such as **attention mechanisms** and **transformer-based architectures** are commonly employed to achieve optimal data integration.

## Step 3: Generate a Response

In this final step, the GenAI model produces a **coherent, contextually accurate response** based on the combined input. This response is then presented to the user via a **user interface or application**.

The model's outputs are **informed by the retrieved knowledge**, ensuring **reliability and factual grounding**.

## Summary

| Step | Input | What happens | Output |
|---|---|---|---|
| **1. Query the knowledge base** | User query | Retrieval system (dense vector retrieval / semantic search) searches the knowledge base | Most relevant documents / data segments |
| **2. Fuse the data** | User query + retrieved documents | GenAI model (GPT, LLaMA) combines query context with retrieved information | Combined, enriched input |
| **3. Generate a response** | Combined input | Model produces a coherent, grounded answer; shown via UI / application | Final response to the user |

This is the overview of a RAG system. See also the companion note *Retrieval Augmented Generation (RAG).md* in this folder for the broader "what and why" of RAG.

---

## Technical Deep Dive

Each step above is packed with technical terms. This section unpacks them one at a time, in the order they appear in the workflow.

**Roadmap:**

| # | Term | Step | Status |
|---|---|---|---|
| — | Structured vs unstructured data | Knowledge base | ✅ Basic |
| — | Embeddings | Knowledge base | ✅ Covered in *Introduction to Vector Embeddings* (Week 2) |
| — | Vector database, indexing, HNSW, ANN | Knowledge base | ✅ Covered in *Introduction to Vector Database* Q1–Q5 |
| 1 | **Dense vector retrieval** | Step 1 | ✅ Done |
| 2 | Semantic search | Step 1 | ✅ Answered directly in Step 1 Q&A (Q1) |
| 3 | Chunking ("data segments") + top-K | Step 1 | ✅ Closed — touched on in Q1's mechanics diagram; Step 1 marked complete |
| 4 | Context augmentation (how query + docs are actually "fused") | Step 2 | ✅ Done |
| 5 | Transformer-based architecture | Step 2 | ✅ Done |
| 6 | Attention mechanism | Step 2 | ✅ Done |
| 7 | Context window | Step 2 | ✅ Done |
| 8 | Factual grounding & hallucination reduction | Step 3 | ⬜ |
| 9 | Decoding (how "coherent" text is actually produced) | Step 3 | ⬜ |

---

### 1. Dense Vector Retrieval

*(Step 1: Query the Knowledge Base)*

**In one sentence:** It is search that matches **meaning** instead of **words**.

#### The problem it solves

You type into a company help desk:

> "How do I reset my password?"

The correct document in the knowledge base says:

> "Steps to recover your login credentials."

**Old keyword search finds nothing.** Not one word matches. "reset" ≠ "recover", "password" ≠ "credentials".

**Dense vector retrieval finds it instantly**, because it compares *meaning*, and both sentences mean the same thing.

That is the whole point. Everything below is just *how*.

#### Why the name: "dense" vs "sparse"

Both methods turn text into a list of numbers. The difference is what that list looks like.

**Sparse = mostly zeros.** Old keyword search gives one slot per word in the dictionary.

Tiny example with a 6-word dictionary:

```
Dictionary:  [ dog, cat, runs, fast, blue, sky ]
"dog runs"  → [  1,   0,   1,    0,    0,   0  ]
                      ↑         ↑     ↑    ↑
                          four empty slots
```

Real dictionaries have ~50,000 words. A short sentence fills ~20 slots and leaves **49,980 zeros**. Mostly empty → **sparse**.

**Dense = every slot filled.** An embedding model gives a much shorter list where *every* number carries meaning.

```
"dog runs"  → [ 0.82, -0.31, 0.55, 0.12, -0.77, 0.40, ... ]
                  ↑      ↑     ↑     ↑      ↑     ↑
                       every single one is filled
```

Usually 384, 768 or 1536 numbers, and **none of them zero** → **dense**.

| | Sparse (keyword) | Dense (embedding) |
|---|---|---|
| What the list looks like | `[1, 0, 1, 0, 0, 0]` | `[0.82, -0.31, 0.55, 0.12]` |
| Length | ~50,000 | ~768 |
| Matches on | Exact words | Meaning |
| "car" vs "automobile" | ❌ No match | ✅ Match |
| Best at | Names, IDs, error codes | Concepts, rephrasing |

Look at that last row. Keyword search still wins for things like `ORDER-88231` or `ERR_502`, where you need the *exact* string. That is why many real systems run **both** together, which is called **hybrid search**.

#### How it works, in two phases

**Phase A — before any user shows up (done once):**

```
Your documents → cut into chunks → embedding model → vectors → stored in vector DB
```

**Phase B — when a user actually asks something:**

```
"How do I reset my password?"
        ↓ same embedding model
   [0.44, -0.12, 0.98, ...]
        ↓ compare with stored vectors
   3 closest chunks come back        ← this is "top-K", here K = 3
```

Simple way to picture it: every document was given a **location on a map of meaning** in advance. Your question gets a location too. The database just hands back the nearest neighbours.

#### ⚠️ The one rule people get wrong

**Documents and the query must go through the *same* embedding model.**

Simple example: your friend rates movies out of **10**, you rate them out of **100**. Your friend says *7*, you say *70*. You both loved it equally, but compared directly the numbers look nothing alike.

Embedding models work the same way. Each one invents its own private "number language". Mix two of them and the distances become meaningless.

**What this means in practice:** if you change your embedding model, you must **re-embed every document again**. This is a common interview question.

#### Why it is fast: the bi-encoder

**Bi-encoder = the question and the documents are turned into numbers *separately*.**

That separation is what makes it fast. Your 10,000 documents were already converted **last night**. When a user asks something, you only convert *one short question*, then compare numbers. Comparing numbers is nearly instant, even across millions of them.

The slower, smarter alternative is a **cross-encoder**. It reads the question and one document *together* and judges how well they match. Much more accurate, but it has to run **once per document**. For 10,000 documents that is 10,000 runs for a single question, which is far too slow.

**So real systems use both, in order:**

```
1. Bi-encoder    → scan all 10,000 → shortlist 50    (fast, rough)
2. Cross-encoder → carefully rank those 50 → keep 5  (slow, precise)
```

That second stage is called **reranking**.

**Analogy 📚** You want the best book in a library on one topic.
- **Bi-encoder** = walking the aisles reading only the **spines**, grabbing 20 likely ones. Fast.
- **Cross-encoder** = actually **reading** those 20 to pick the best 3. Slow, and you would never do it for the whole library.

#### How this connects to your existing notes

*Introduction to Vector Database* explains the **machinery**: embeddings (Q1–Q2), indexing (Q3), and ANN (Q4). Dense vector retrieval is the **act of using** that machinery to fetch context for an LLM.

**One line:** Dense vector retrieval = your question and your documents are converted by the *same* model into short lists of numbers where every slot is filled ("dense"), and the database returns the documents whose numbers sit closest to your question's — which is how "recover your login credentials" gets found by someone asking to "reset my password".

---

### 4. Context Augmentation — How Query + Docs Actually Get "Fused"

*(Step 2: Fuse the Data)*

**In one sentence:** "fusing" isn't a special merging technique — it's just building one combined prompt out of the retrieved chunks and the user's question, then handing that to the LLM like normal input.

```
Retrieved chunks (from Step 1):
1. "Go to Settings > Security > Reset to recover your login credentials."
2. "Password resets require email verification."

User's question: "How do I reset my password?"

              ↓  glued together into one prompt  ↓

  "Context:
   1. Go to Settings > Security > Reset to recover your login credentials.
   2. Password resets require email verification.

   Question: How do I reset my password?
   Answer using only the context above."

              ↓

     sent to the LLM as one normal text input
```

That's the entire "fusion" step — there's no separate fusion module. This is called **context augmentation**: you augment (add to) the query with retrieved context *before* the LLM ever sees it. All the hard work already happened in Step 1 (finding the *right* chunks); this step is comparatively simple stitching.

So when the workflow overview said "attention mechanisms and transformer-based architectures are commonly employed to achieve optimal data integration," it isn't describing a separate fusion algorithm — it's describing what happens *inside the LLM itself* once it reads that combined prompt. That's exactly what the next two terms explain.

**One line:** Context augmentation = concatenating the retrieved chunks with the user's question into a single prompt — the "fusing" is just prompt-building, and all the real intelligence happens afterward, inside the LLM that reads this augmented prompt.

### 5. Transformer-Based Architecture

*(Step 2: Fuse the Data)*

**In one sentence:** the generative model in this step — GPT, LLaMA, etc. — *is* a transformer; "transformer-based architecture" just means the engine doing the reading and writing here is built the way your Week 1 note already covers.

You have the full deep-dive already in *1.The Evolution of Transformers to Large Language Models (LLMs).md* (Week 1). The one thing worth restating simply for this step:

A transformer reads the **entire augmented prompt at once** — question, retrieved chunks, and instructions, all together as one sequence — rather than one isolated word at a time. That "read everything together, and weigh how each part relates to every other part" ability is exactly why it can take a pile of retrieved text plus a question and produce one coherent answer. And "weighing how each part relates to every other part" is precisely the attention mechanism, covered next.

**One line:** The generative model that does the fusing and answering is a transformer, the same architecture from your Week 1 notes, and its defining trick is reading the whole augmented prompt at once rather than word by word — which is what makes combining retrieved context with a question actually work.

### 6. Attention Mechanism

*(Step 2: Fuse the Data)*

**In one sentence:** attention is how the model decides, for every word it's about to write, *which* words in the prompt matter most right now.

**Simple example.** In the sentence *"The trophy didn't fit in the suitcase because **it** was too big,"* what does "it" refer to — the trophy or the suitcase? A human instantly knows: the trophy. Attention is the mechanism that lets the model do the same — for the word "it," it looks back across the sentence and assigns a **high weight** to "trophy" and a **low weight** to "suitcase."

**In RAG specifically**, attention is what lets the model, while writing the answer, constantly glance back at the retrieved chunks and decide which sentence is actually relevant to the word it's producing right now, instead of treating the whole context as one equally-important blob:

```
Question: "How do I reset my password?"

Chunk 1: "Go to Settings > Security > Reset..."     ← high attention
Chunk 2: "Password resets require email verify."    ← medium attention
Chunk 3: (unrelated leftover text)                   ← low attention

Model writes: "Go to Settings, then Security, then Reset..."
```

The model doesn't read top to bottom like a human — for every single word it generates, it re-checks the *whole* prompt and re-weighs what matters. That re-weighing, redone at every step, is literally what "attention" computes.

**Simple analogy 🔦:** Attention is like a spotlight the model can swing anywhere across the page while writing each word — it can shine brightest on the one sentence in the retrieved context that actually answers the question, and dim everything else, without losing sight of the rest of the page.

**One line:** Attention is the mechanism that lets the model weigh which words or retrieved sentences matter most for whatever it's producing right now, which is exactly what makes it possible to fuse a pile of retrieved chunks with a question into one focused answer instead of treating everything as equally important.

### 7. Context Window

*(Step 2: Fuse the Data)*

**In one sentence:** the context window is the maximum amount of text — question, retrieved chunks, and instructions, all counted together — that the model can look at in one go; anything beyond that limit simply doesn't fit.

Text is measured in **tokens** (roughly ¾ of a word each — "reset" ≈ 1 token, "unbelievable" ≈ 2–3). Every model has a maximum token count it can accept at once. Older, smaller models cap out around a few thousand tokens; newer ones allow far more — but every model has *some* ceiling.

**Why this matters for RAG specifically:**

```
Context window budget (example): 8,000 tokens

  Instructions / system prompt          ~200 tokens
  User's question                       ~20 tokens
  Retrieved chunks (top-K)              ~??? tokens   ← the variable part
  Room left for the model's answer      ~500 tokens
```

If Step 1 retrieves too many chunks, or chunks that are too large, they can overflow the context window — meaning some retrieved information the model was *supposed* to use never actually reaches it. This is exactly why **top-K** and **chunk size** from Step 1 aren't arbitrary choices — they're picked to fit comfortably inside the context window, leaving room for the question, instructions, and the model's own answer.

**Simple analogy 🗄️:** The context window is like the size of a desk. You can only spread out so many documents on it at once. Bring more than fit, and some get pushed off the edge — the model literally never sees them, however relevant they might have been.

**One line:** The context window is the hard cap on how much text — question, instructions, and retrieved chunks together — the model can process in a single pass, measured in tokens, and it's exactly why chunk size and top-K from Step 1 have to be chosen carefully: retrieve too much and some of it simply won't fit.

---


## Q&A

Every question asked while working through this file is logged here, grouped under the step it belongs to. Each entry follows the same blog-style block, so it's easy to see where one question ends and the next begins:

- A `---` rule opens the block, and a `---` rule closes it.
- A numbered heading names the topic.
- The question is quoted **as asked**, then restated as a **Refreshed** version.
- The **Answer** follows, then an *(End of Qn)* marker before the closing rule.

### Knowledge Base

*(no questions yet)*

### Step 1: Query the Knowledge Base

---

### 🟩 Q1 · Dense Retrieval vs. Semantic Search, Sparse Retrieval vs. BM25

> **🗣️ Asked (as said):** "We have a dense vector retrieval and the sparse vector retrieval. So the dense vector retrieval is nothing but a semantic search, which searches for the meaning, and not the exact keyword. But as the sparse vector retrieval is the keyword searching, which is something like BM25. I'm not wrong?"
>
> **✍️ Refreshed:** Is dense vector retrieval the same thing as semantic search, and is sparse vector retrieval the same thing as keyword search like BM25?

**💡 Answer**

**Verdict: almost exactly right, with one small precision worth knowing.**

**Half 2 first, since it's fully correct:** Sparse vector retrieval = keyword search = things like BM25 or TF-IDF. Yes, that's exactly it. It matches on exact words, not meaning.

**Half 1, the small precision:** Dense vector retrieval and semantic search are used interchangeably almost everywhere, and for everyday purposes you're right to treat them as the same. The tiny technical difference:

- **Semantic search** = the *goal*. "Search by meaning, not exact words."
- **Dense vector retrieval** = the *method* used today to achieve that goal, using embeddings + a vector database.

**Simple analogy 🎯:** "Semantic search" is like saying "I want to find books by topic." "Dense vector retrieval" is like saying "I'll do that by turning every book into a GPS coordinate on a map of topics, and finding the ones closest to where my question sits." One is the *what*, the other is the *how*.

In practice, when anyone says "semantic search" today, they mean dense vector retrieval. There's no other popular way to do semantic search right now. So your statement is correct for all practical purposes — just remember dense vector retrieval is the technique, semantic search is the name for what that technique achieves.

**One line:** You're right — sparse retrieval is keyword search (BM25-style), and dense vector retrieval is what people mean when they say "semantic search," searching by meaning instead of exact words; the only nuance is that semantic search is the goal and dense vector retrieval is the specific technique that delivers it.

*(End of Q1)*

---

### 🟩 Q2 · Other Methods of Semantic Search *(follow-up to Q1)*

> **🗣️ Asked (as said):** "Correct me if I'm wrong — this is a follow-up to Q1. You are saying that dense vector retrieval is one of the methods of semantic search. So is there any other method that we do for semantic search? If yes, please list that down and explain each one in a one-liner with the simplest explanation."
>
> **✍️ Refreshed:** Is dense vector retrieval just one of several methods used to do semantic search — and if so, what are the other methods, each explained in one simple line?

**💡 Answer**

**Your premise is correct** — dense vector retrieval is indeed just one method for doing semantic search, not the only one. Here are the others:

| Method | One-liner explanation |
|---|---|
| **Dense vector retrieval** *(already covered)* | Turn text into a fully-filled list of numbers that captures meaning, then find the closest ones. |
| **Latent Semantic Analysis / LSI** | The pre-embeddings, statistical approach — it studies which words tend to appear *together* across many documents to figure out "car" and "automobile" are related, without any neural network. |
| **Learned sparse retrieval** (e.g. SPLADE) | Keeps BM25's fast, word-based format, but a neural network quietly adds *related* words too — so searching "car" also lights up documents about "automobile." |
| **Knowledge graph / ontology-based search** | Skips numbers entirely — it matches your query against a map of real-world facts, like "Paris → capital of → France," so it understands meaning through explicit connections instead of learned patterns. |

**Simple analogy for all three "other" methods 🗺️:**
- **LSA** = noticing that words which keep showing up in the *same rooms* of a building are probably related.
- **Learned sparse retrieval** = a smart librarian who, when you ask for "car" books, quietly also pulls the "automobile" ones off the shelf.
- **Knowledge graph search** = following a hand-drawn map of "this connects to that," rather than measuring distances at all.

**In practice today:** dense vector retrieval has become the dominant, go-to method — it's what almost every modern RAG system uses. The other three still show up (LSA in older systems, learned sparse retrieval in some hybrid search setups, knowledge graphs in enterprise/structured-data search), but if someone just says "semantic search" without more context, they almost always mean dense vector retrieval.

**One line:** No, dense vector retrieval isn't the only way to do semantic search — Latent Semantic Analysis (word co-occurrence patterns), learned sparse retrieval like SPLADE (keyword search quietly expanded with related terms), and knowledge-graph search (matching facts and relationships instead of numbers) are the other three, but dense vector retrieval is by far the most common one used today.

*(End of Q2)*

---

### 🟩 Q3 · Keyword Search vs. Meaning Search — When to Use Which

> **🗣️ Asked (as said):** "There are two methods — first is keyword searching, and the second is meaning search. So tell me, when do we use either of them, and what is a use case for each? Explain in the simplest and shortest manner."
>
> **✍️ Refreshed:** When should I use keyword search versus meaning (semantic) search, and what's one use case for each?

**💡 Answer**

**Use keyword search when the exact words matter.** Order numbers, product codes, error codes, names, IDs, legal citations — things where a "close match" is useless; you need `INV-4521`, not something similar to it.

> Use case: searching a support system for `ERROR_502` — you want that exact code, not documents "about similar errors."

**Use meaning search when the user's words won't match the document's words.** Natural-language questions, FAQs, customer support, chatbots — anywhere someone might ask something a different way than it's written.

> Use case: a user asks "how do I reset my password?" and the help doc says "steps to recover your login credentials" — no shared words, same intent, meaning search finds it.

**Simple analogy 📚:** Keyword search is looking up a book by its exact title on the spine. Meaning search is telling a librarian "I want something about not giving up" and getting a good recommendation even if no book has those exact words on the cover.

**In real systems:** most production search doesn't pick just one — it runs both together (**hybrid search**) and combines the results, since real queries often mix an exact ID with natural language.

**One line:** Use keyword search for exact identifiers (IDs, codes, names) where a near-match is worthless, and use meaning search for natural-language questions where the user's wording won't match the document's wording — real systems typically run both together as hybrid search.

*(End of Q3)*

---

### 🟩 Q4 · Where Does Each Retrieval Algorithm Actually Run? (Hybrid Search, Visualized)

> **🗣️ Asked (as said):** "The first step, when the user asks a question, is basically a retrieval stage of knowledge that we have stored using embeddings, because the LLM understands embeddings. But there could be a hybrid approach here, where keyword search plus semantic search comes into play, and each would have a different algorithm. For example, in the case of semantic search, there would be a dense vector retrieval algorithm used. So exactly where does this algorithm lie — does it lie on the vector database where the embedding is stored, or before, or after that stage? I'm confused here. Explain in the simplest manner, and if you could visually explain the answer, that would be much better."
>
> **✍️ Refreshed:** In a hybrid search setup, where does each retrieval algorithm actually run — is the dense vector retrieval algorithm part of the vector database itself, or does it happen before or after the vector database stores the embeddings?

**💡 Answer**

**One small correction first:** the LLM does not read embeddings. It only ever reads **plain text**. Embeddings are a purely *internal* tool used to *find* the right text — once the right chunks are found, the actual retrieved sentences (not the vectors) get handed to the LLM in Step 2. Keep that in mind below.

**Now the main question — where does each algorithm live?** In a hybrid setup, keyword search and semantic search are actually **two separate systems running side by side**, not one system with two modes. Here's the full picture:

```
                              USER QUERY
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                     │
          KEYWORD PATH                          SEMANTIC PATH
          (sparse / BM25)                        (dense vector)
                 │                                     │
        query used as raw text              ① Embedding Model
        (no embedding needed)                  ← runs BEFORE the
                 │                               vector database
                 ▼                                     ▼
   ② Keyword Search Engine              ③ Vector Database
      (inverted index)                     (stores the vectors AND
      ★ BM25 algorithm                       runs the ANN/HNSW
        RUNS HERE                             search algorithm)
                 │                          ★ dense retrieval
                 │                            algorithm RUNS HERE
                 │                                     │
                 └───────────────┬─────────────────────┘
                                  ▼
                    ④ Fusion / Reranking
                    ← happens in your APPLICATION code,
                      AFTER both engines reply — not
                      inside either engine
                                  ▼
                    Top-K relevant TEXT CHUNKS
                    (plain text, not vectors!)
                                  ▼
                    Passed to the LLM (Step 2: Fuse the Data)
```

**In words, the four locations:**

| # | Component | Where does it actually run? |
|---|---|---|
| ① | Embedding model (text → vector) | **Before** the vector database — a separate model, used both when the documents were first indexed and again on the live query |
| ② | Keyword algorithm (BM25) | **Not related to the vector database at all** — a completely separate search engine, built on raw text |
| ③ | Dense retrieval algorithm (ANN, e.g. HNSW) | **Inside** the vector database — running that search *is* the database's actual job |
| ④ | Merging keyword + semantic results | **After** both engines reply, in your own application/orchestration code |

**Simple analogy 🏪:** Imagine two separate shops next door to each other — a "keyword shop" (a librarian with a card catalog of exact words) and a "meaning shop" (a librarian who's memorized what every book is *about*). You send your question to both at once. Each shop does its own search using its own method. Then a manager standing outside both shops (your application code) compares the two shortlists and picks the best combined list. Neither shop knows the other exists.

**One line:** Keyword search and dense vector retrieval are two independent systems, not two settings on one database — the embedding model runs *before* the vector database, the dense-retrieval algorithm (like HNSW) runs *inside* it, BM25 runs in a completely separate keyword engine, and combining both results happens *after*, in your application code — and either way, what finally reaches the LLM is plain retrieved text, never the vectors themselves.

*(End of Q4)*

---

### 🟩 Q5 · How Does a Matched Embedding Turn Back Into Text? *(follow-up to Q4)*

> **🗣️ Asked (as said):** "Let's suppose the query comes. We embed that query using the embedding model, and the vector database already has those embeddings. Using some dense vector retrieval algorithm, we find a relevant embedding. But how does the embedding turn into a textual message? Does the vector database give us the textual message that it wants, or is there any layer between the two that converts the embedding into an actual textual representation?"
>
> **✍️ Refreshed:** Once the vector database finds the closest matching embedding, how do we get back the original text — does the vector database return the text directly, or is there a separate layer that converts the vector back into text?

**💡 Answer**

**Short answer: there is no conversion layer, because none is needed.** Embeddings are **never turned back into text**. Instead, the original text was **stored right alongside its vector from the very beginning** — retrieval is just a lookup, not a decoding process.

```
INDEXING TIME (offline, done once per document chunk)

  "Steps to recover your login credentials"     ← original text
                    │
                    ▼
            Embedding Model
                    │
                    ▼
        [0.82, -0.31, 0.55, ...]                ← vector

  Both are saved TOGETHER as one record:
  ┌────────────────────────────────────────────────┐
  │ id:     452                                     │
  │ vector: [0.82, -0.31, 0.55, ...]                │
  │ text:   "Steps to recover your login credentials"│ ← stored side-by-side
  └────────────────────────────────────────────────┘


QUERY TIME

  "How do I reset my password?"
                    │
                    ▼
       Embedding Model (same one)
                    │
                    ▼
        [0.79, -0.28, 0.51, ...]                ← query vector
                    │
                    ▼
      Vector DB compares to every stored vector,
      finds record 452's vector is closest
                    │
                    ▼
      Returns record 452's TEXT FIELD as-is
      → "Steps to recover your login credentials"
                    │
                    ▼
      No decoding happened — it was a LOOKUP,
      not a conversion
```

**Simple analogy 📇:** Think of an old library card catalog. Each card has a Dewey decimal number (that's the vector) and the book sits on the shelf at that number (that's the text). When you find the right card, you don't "decode the number back into the book" — the book was already sitting right there, placed at that spot when the library was organized. The number was only ever a *pointer*, never a compressed version of the book itself.

**One more thing worth knowing:** embeddings are **one-way and lossy by design** — you genuinely cannot mathematically reconstruct the original sentence from its vector alone. That's exactly *why* the text has to be stored alongside the vector rather than derived from it afterward.

**A small variation you'll see in practice:** some vector databases store the full text directly next to the vector (as in the diagram above). Others store only an ID + vector, and keep the actual text in a separate document store (a SQL table, a file store, etc.), fetching it afterward using that ID. Same idea either way — a stored pairing and a lookup, never a conversion.

**One line:** There's no layer that converts embeddings back into text — the original text chunk was stored right alongside its vector at indexing time (either directly or via an ID pointing to it elsewhere), so once the vector database finds the closest vector, it simply hands back the text it was paired with, the same way a library card's number points to a book that was already shelved there, not decoded from the number.

*(End of Q5)*

---

### 🟩 Q6 · Bi-Encoder → Cross-Encoder: Is It a Pipeline, and Does Cross-Encoder Read the Whole Library? *(follow-up to Q1)*

> **🗣️ Asked (as said):** "You mentioned the bi-encoder and the cross-encoder. When a question is asked, the bi-encoder matches the encoded question to the already-stored embeddings in the vector database, using some algorithm like ANN or HNSW — right? But in the cross-encoder, you match the user query with each and every document stored in the vector database. Does that mean the output of the bi-encoder could be used as the input to the cross-encoder? Also, this isn't really an encoding method — it's about how the process is done, not what is being done, correct? So does that mean the cross-encoder reads the whole library?"
>
> **✍️ Refreshed:** Does the bi-encoder match the query against stored embeddings using ANN/HNSW, while the cross-encoder compares the query against every document in the vector database? Does the bi-encoder's output feed into the cross-encoder as input? And is the bi-encoder/cross-encoder distinction really about *how* matching is done rather than a type of encoding — meaning does the cross-encoder read through the whole library?

**💡 Answer**

**Three parts right, one part to fix.**

**✅ Part 1 — correct:** The bi-encoder embeds the query, then an ANN algorithm like HNSW searches the vector database for the closest stored embeddings. Exactly right.

**✅ Part 2 — correct:** Yes, the bi-encoder's output *is* the cross-encoder's input. That's the whole pipeline — one feeds directly into the other:

```
        MILLIONS of documents (the "whole library")
                        │
        ① Bi-encoder + ANN search (HNSW)
           ← fast, approximate, scans everything
                        │
                        ▼
        Shortlist: e.g. top 50 candidates
                        │
        ② Cross-encoder reranks ONLY these 50
           ← slow, precise, query + each doc together
                        │
                        ▼
        Final: top 3–5 most relevant → sent to the LLM
```

**❌ Part 3 — needs a correction:** the cross-encoder does **not** compare the query against *every document in the vector database*. That was exactly the problem the bi-encoder exists to solve. The cross-encoder only ever runs on the small **shortlist** the bi-encoder already narrowed things down to — say, 50 documents, not millions. So no, **the cross-encoder does not read the whole library** — it only reads the shelf of books the bi-encoder already pulled out.

**On your fourth point — "this is about *how*, not *what*":** you're onto something real, worth stating precisely. Both bi-encoder and cross-encoder genuinely *are* encoding methods — both use a transformer model to turn text into a representation. So it's not that one is "encoding" and the other "isn't." The real difference is procedural:

- **Bi-encoder** = encode the query and each document **separately**, then compare the two resulting vectors with math (cosine similarity) afterward.
- **Cross-encoder** = feed the query and **one** document **together** into the model at once, so the model itself outputs a relevance score directly — no separate vectors to compare.

So your instinct is right in spirit: the names "bi-" and "cross-" describe *how many things go into the model at once and when*, not a different kind of embedding output. Same building block (a transformer encoder), two different strategies for using it.

**Simple analogy 📚:** A librarian (bi-encoder) skims book spines *ahead of time* and separately skims your request, then matches them by gist — fast, done for millions of books in advance. A second librarian (cross-encoder) sits down and reads your request *together with* one specific book at a time to judge fit precisely — accurate, but only ever done for the 50 books the first librarian already pulled off the shelf, never the whole library.

**One line:** You're right that the bi-encoder's shortlist feeds directly into the cross-encoder as its input, and right that the bi-/cross- naming describes *how* the matching happens rather than a different type of encoding — but the cross-encoder never reads the whole library, only the small shortlist the bi-encoder already narrowed down, since reading every document that way would be far too slow.

*(End of Q6)*

---

### 🟩 Q7 · Do Both Bi-Encoder and Cross-Encoder Just "Embed the Query"? *(follow-up to Q6)*

> **🗣️ Asked (as said):** "You're saying that the bi-encoder and cross-encoder use a transformer model to turn text into a representation. Here, we're simply talking about embedding the query, right? And both the bi-encoder and cross-encoder could use the same transformer model to embed the query — correct?"
>
> **✍️ Refreshed:** Since both bi-encoder and cross-encoder use a transformer model to turn text into a representation, is that representation just the query's embedding — and could both use the exact same transformer model to do that embedding?

**💡 Answer**

**Two things to correct here, both important.**

**❌ Correction 1 — "we're simply talking about embedding the query" is only true for the bi-encoder.** The cross-encoder does **not** produce a query embedding at all. It never outputs a standalone vector for the query. Instead, it glues the query and **one document together** into a single input, and outputs **one number** — a relevance score (e.g. `0.87`). There's no "query representation" sitting on its own anywhere in that process.

```
BI-ENCODER                              CROSS-ENCODER
─────────────                           ──────────────
query  → [transformer] → vector A       query + document (glued together)
doc    → [transformer] → vector B              → [transformer]
                                                → single relevance score
vector A vs vector B
→ compared afterward (cosine similarity)  (no separate vectors exist at all)
```

So: bi-encoder → produces embeddings (plural: one for the query, one for each document). Cross-encoder → produces a score, not an embedding.

**❌ Correction 2 — "the same transformer model" needs a nuance.** They can share the same *starting point* (e.g. both might begin from a base model like BERT), but in a real pipeline they end up as **two separately fine-tuned models**, not one shared model doing double duty:

| | Bi-encoder | Cross-encoder |
|---|---|---|
| Trained to do what | Produce vectors that land close together *when compared by math afterward* | Directly output a good relevance score for a *pair* fed in together |
| Can reuse the other's trained weights? | ❌ No — a model trained for joint scoring doesn't produce good standalone vectors |
| Base architecture | Often the same family (e.g. BERT) | Often the same family (e.g. BERT) |

A plain, un-fine-tuned BERT model actually produces mediocre standalone embeddings — that's a well-known finding, which is *why* bi-encoder models (like Sentence-BERT) needed their own special fine-tuning recipe to become good at it. So "same transformer *architecture* as a starting point" — often yes. "Same trained model file doing both jobs interchangeably" — no, in practice they're trained separately for their own job.

**Simple analogy 📝:** The bi-encoder librarian writes a one-line summary card for your request, and a separate one-line card for each book, then compares the two cards side by side. The cross-encoder librarian doesn't write any card at all — they just read your request and one book together in one sitting and tell you a score out of 10. No "representation of your request" exists on its own in that second case.

**One line:** Only the bi-encoder is really "embedding the query" — it produces a standalone vector; the cross-encoder skips embeddings entirely and outputs a single relevance score for the query-and-document pair jointly, and while both may start from the same base transformer architecture, they end up as two separately fine-tuned models rather than one shared model used for both jobs.

*(End of Q7)*

---




### Step 2: Fuse the Data

---

### 🟩 Q1 · "Reweighting, Redone at Every Step" — Do the Model's Weights Actually Change? *(follow-up to the Attention Mechanism deep dive)*

> **🗣️ Asked (as said):** "In the case of the attention mechanism, can you tell me what you mean by 'reweighting' and 'redone at every step'? Are the weights adjusted every time? I think no, because the pretrained model has its weights already computed — unless you fine-tune it, it does not change. But I think what I mean is the weights of the prompt. Also, can we tweak the attention mechanism, how it's configured, or is it fixed? For example, in the retrieval part we have some free hand — we can adjust things here and there, right? But the generation part, does it all depend on what kind of generation model we use — correct?"
>
> **✍️ Refreshed:** Does "reweighting, redone at every step" mean the model's trained parameters change each time, or something else, like per-prompt importance scores? And can the attention mechanism itself be configured or tweaked by us, or is it entirely fixed by whichever generation model we choose — unlike retrieval, where we have more freedom to adjust things?

**💡 Answer**

**Your instinct is exactly right, and it points at a genuine terminology clash.** There are two completely different things both called "weights," and my earlier answer used the word for the second one without flagging that.

**✅ You're correct: the model's trained parameters never change during inference.** Those are the billions of numbers set once during training (and only ever changed again through fine-tuning). They're frozen. Nothing about answering your specific question adjusts them.

**❌ What I meant by "reweighting" is something else entirely: attention scores** — and your own guess, "weights of the prompt," is exactly the right correction. Here's the distinction:

| | Model weights (parameters) | Attention weights (scores) |
|---|---|---|
| What it is | The trained W_Q, W_K, W_V matrices inside the model | A number saying "how much should this word attend to that word" |
| Where it comes from | Learned once, during training | Calculated fresh from (fixed parameters) × (your specific input) |
| Does it get stored? | Yes — it's part of the model file | No — computed, used, then thrown away |
| Does it change per-query? | ❌ No | ✅ Yes, completely different every time |

**Concrete walkthrough:** the *fixed* matrices (W_Q, W_K, W_V) take your input tokens and project them into "query," "key," and "value" vectors. The model then compares queries against keys (a dot product) and turns that into a set of scores that sum to 1 — *those scores* are the "attention weights" I meant. They're a live calculation *using* the fixed parameters, not the parameters themselves.

**Why "redone at every step":** in autoregressive generation, the model produces one word, appends it to the sequence, then has to decide the *next* word — which means re-running that score calculation, now including the newly added word. One practical nuance worth knowing: real systems use a **KV cache**, so the key/value vectors for *already-processed* words aren't recomputed from scratch each time — only the brand-new word's query gets freshly compared against everything cached so far. So it's not *all* redone every step, but the actual attention *scores* for the new token genuinely are calculated fresh, every single step.

**Simple analogy 🧮:** the model's parameters are like a fixed calculator — the buttons and their functions never change. Attention weights are like the *answer* you get when you type in a specific sum. The calculator (parameters) is frozen; the answer (attention scores) is different every time you use it, because the input is different.

---

**Now the second part — can we configure attention, and is generation truly "no free hand" compared to retrieval?**

**Right in spirit, a bit too absolute in practice.** You're correct that you can't reach in and rewire *how* attention computes (how many heads, whether it's causal, the hidden size) — that's baked into whichever model you're using, the same way you can't edit GPT's or LLaMA's source code through an API call. But "no free hand at all" overstates it. Both steps actually follow the *same* pattern: you configure a pipeline around a black-box core, and the box's internals aren't yours to touch unless you go deeper.

| | What you **can** adjust | What's **fixed**, baked into the tool you picked |
|---|---|---|
| **Step 1: Retrieval** | Embedding model choice, chunk size, top-K, hybrid search weighting, reranking | The literal math inside that embedding model / ANN algorithm |
| **Step 2: Generation** | Prompt content & structure, decoding settings (temperature, top-p, max tokens), system instructions, **which model you call**, fine-tuning (if you have the weights) | The attention mechanism's internal architecture — number of heads, layers, causal masking |

So at generation time you do still have real levers: how you write the prompt directly shapes *what* the (fixed) attention mechanism ends up focusing on, decoding parameters shape how the output is sampled, and choosing a different model is itself a form of choosing a different "attention design." And if you're working with an *open-weight* model (like the LoRA/QLoRA fine-tuning from your Week 2 notes), fine-tuning actually **does** adjust the trained W_Q/W_K/W_V matrices through further training — so even attention's *learned behavior* isn't permanently untouchable, just not something you tweak casually through a prompt.

**Simple analogy 🚗:** you can't redesign the engine (attention internals) of a car you don't own the blueprints for. But you still choose *which car* to drive (model choice), *how* you drive it (prompt + decoding settings), and if you own the engine outright (open-weight model), a mechanic *can* retune it (fine-tuning) — just not usually rebuild it from scratch.

**One line:** You're right that the model's trained parameters never change per-query — what I called "reweighting, redone at every step" is the attention *scores*, a fresh, per-prompt, per-step calculation made using those fixed parameters, exactly matching your own correction to "weights of the prompt"; and generation isn't truly "no free hand" — you can't rewire attention's internals through a prompt, but prompt design, decoding settings, model choice, and fine-tuning (on open-weight models) are all real levers, just a different *kind* of lever than retrieval's.

*(End of Q1)*

---

### 🟩 Q2 · Are Retrieval Embeddings the Same Thing as Attention, or Related to It? *(bridges Step 1 Q1 and the Attention Mechanism deep dive)*

> **🗣️ Asked (as said):** "I have a little confusion here. In order to retrieve a thing, what we do is a semantic search — and for doing the semantic search, we basically compute the embedding of the query and the already-stored embeddings, right? Is this completely different from the attention mechanism, or is it related to the attention mechanism?"
>
> **✍️ Refreshed:** Is the embedding computation used for semantic search in Step 1 the same thing as, or connected to, the attention mechanism used in Step 2 — or are they entirely unrelated?

**💡 Answer**

**Genuinely both, depending on which part of the question you mean.** Worth splitting into two very different sub-questions.

**❌ Are the *actual numbers* — Step 1's embeddings — the same as, or fed into, Step 2's attention computation? No.** These are two separate models doing two separate jobs, and no numbers cross between them. You already established this a few questions ago: the vector database hands back the retrieved *text*, never the vector. So by the time Step 2 begins, Step 1's embeddings are already gone — thrown away the moment the matching chunks were found. The generative model in Step 2 never sees them.

**✅ Is the *underlying technique* used to build those Step 1 embeddings often attention? Usually, yes.** Most modern embedding models (the ones actually used for dense vector retrieval today — BERT-based, Sentence-BERT, the embedding models behind OpenAI/Cohere-style APIs) are themselves transformers, and transformers use attention *internally* to build understanding before producing their output. So attention is working "under the hood" in Step 1 too — it's just a **separate use of the same technique**, inside a **different, dedicated model**, for a **different purpose**.

```
STEP 1 (embedding model)                    STEP 2 (generative model)
─────────────────────────                   ──────────────────────────
Text → transformer layers                   Retrieved TEXT + query
       (attention used INTERNALLY            → transformer layers
        to build understanding)               (attention used INTERNALLY
       → pooled into ONE vector                to relate every word
         (the embedding)                       to every other word)
                                              → next word, next word, ...

  vector compared via cosine similarity,     the model NEVER sees Step 1's
  then THROWN AWAY — only the                embeddings — it does its own,
  matched TEXT crosses over  ────────────►   completely fresh attention pass
                                              over the raw retrieved text
```

The key line is the arrow: **only the retrieved text crosses from Step 1 into Step 2 — never the embedding numbers, and never Step 1's attention computation.** Step 2's model reads the plain words and builds its own understanding of them from scratch, using its own attention layers, entirely independent of whichever model did the searching.

**One more precision:** not *every* embedding method uses attention — older techniques like Word2Vec or GloVe don't (they predate transformers entirely). But the dense vector retrieval you've been learning about in Step 1 — the kind that actually powers modern RAG systems — is built on transformer-based embedding models, so attention genuinely is involved on both sides of the pipeline, just twice, separately, by two different models.

**Simple analogy 📚:** think of two students independently reading the same book. Student A (the embedding model) reads it carefully and writes one summary card for a librarian to file away — once that card exists, the deep reading that produced it is discarded. Student B (the generative model), later, reads the *actual book pages* themselves — not student A's mental notes — to answer a specific question. Both students used the same underlying skill (careful, "attend to what matters" reading), but they never share notes — only the physical pages (the text) pass between them.

**One line:** They're related through a shared technique but not connected through shared data — Step 1's embedding model often uses attention internally to build the vector it searches with, and Step 2's generative model separately uses its own attention to read the retrieved text and write an answer, but the two never touch: only the plain retrieved text crosses the boundary between them, never any embedding numbers or attention computations.

*(End of Q2)*

### Step 3: Generate a Response

*(no questions yet)*

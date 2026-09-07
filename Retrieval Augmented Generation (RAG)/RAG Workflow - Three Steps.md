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
| 3 | Chunking ("data segments") + top-K | Step 1 | ⬜ |
| 4 | Context augmentation (how query + docs are actually "fused") | Step 2 | ⬜ |
| 5 | Transformer-based architecture | Step 2 | ⬜ |
| 6 | Attention mechanism | Step 2 | ⬜ |
| 7 | Context window | Step 2 | ⬜ |
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

## Q&A

*Questions asked while working through the deep dive above, with answers, kept for future reference.*

### Knowledge Base

### Step 1: Query the Knowledge Base

#### Q1

**Question (as asked):** "We have a dense vector retrieval and the sparse vector retrieval. So the dense vector retrieval is nothing but a semantic search, which searches for the meaning, and not the exact keyword. But as the sparse vector retrieval is the keyword searching, which is something like BM25. I'm not wrong?"

**Refreshed Question:** Is dense vector retrieval the same thing as semantic search, and is sparse vector retrieval the same thing as keyword search like BM25?

**Answer:**

**Verdict: almost exactly right, with one small precision worth knowing.**

**Half 2 first, since it's fully correct:** Sparse vector retrieval = keyword search = things like BM25 or TF-IDF. Yes, that's exactly it. It matches on exact words, not meaning.

**Half 1, the small precision:** Dense vector retrieval and semantic search are used interchangeably almost everywhere, and for everyday purposes you're right to treat them as the same. The tiny technical difference:

- **Semantic search** = the *goal*. "Search by meaning, not exact words."
- **Dense vector retrieval** = the *method* used today to achieve that goal, using embeddings + a vector database.

**Simple analogy 🎯:** "Semantic search" is like saying "I want to find books by topic." "Dense vector retrieval" is like saying "I'll do that by turning every book into a GPS coordinate on a map of topics, and finding the ones closest to where my question sits." One is the *what*, the other is the *how*.

In practice, when anyone says "semantic search" today, they mean dense vector retrieval. There's no other popular way to do semantic search right now. So your statement is correct for all practical purposes — just remember dense vector retrieval is the technique, semantic search is the name for what that technique achieves.

**One line:** You're right — sparse retrieval is keyword search (BM25-style), and dense vector retrieval is what people mean when they say "semantic search," searching by meaning instead of exact words; the only nuance is that semantic search is the goal and dense vector retrieval is the specific technique that delivers it.


### Step 2: Fuse the Data

### Step 3: Generate a Response

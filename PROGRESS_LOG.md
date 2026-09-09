# Progress Log

A running recap of each work session on this branch, written at the end of the day so the next session can pick up with fresh recall instead of re-reading everything. Newest entry at the top.

---

## 2026-09-09 (Tuesday), session ending ~7:30 PM IST

**Branch:** `LearningGenAI-Week3` (all file paths below are relative to this branch, unless noted). All work today is committed and pushed to `origin/LearningGenAI-Week3`, last commit `91b844b`.

### 1. RAG Workflow document
**File:** `Retrieval Augmented Generation (RAG)/RAG Workflow - Three Steps.md`

- Step 1 (retrieval) grew to **Q1–Q12** in the Q&A section: dense vector retrieval, other semantic search methods, keyword vs. meaning search, where each hybrid-search algorithm actually runs, how a matched embedding maps back to text, the bi-encoder → cross-encoder pipeline and their independence, two mind-map passes (one corrected after Q9–Q10), and how quantization differs from ANN.
- Added a full **"Step 1 Interview Prep" mock interview** — 11 interviewer questions with model answers and follow-ups, calibrated to a ~4-year AI engineer, later simplified in place (HNSW/ANN broken down with a numeric example, the MRR/NDCG evaluation-metrics answer rebuilt around a fishing analogy).
- Filled in the **Step 2 deep dive** (context augmentation, transformer architecture, attention, context window) plus Q1–Q3 there (model weights vs. attention scores, KV cache, and how retrieval embeddings relate to attention).
- **Not yet started:** Step 3 (Generate a Response) has no deep dive or Q&A content yet — this is the natural next thing to pick up.

### 2. Consolidated Q&A across all three weeks
- New branch **`LearningGenAI-ConsolidatedQA`** (branched from `main`, not from any week branch) holding one file, `Consolidated-QA.md` — every Q&A pair (122 total) from Week 1, Week 2, and Week 3, extracted verbatim and grouped by week → source file.
- Uploaded as a plain `.md` file to Google Drive (not converted to a Google Doc — that was tried, then explicitly declined in favor of the raw file).
- This is a one-time deliverable, not something actively being edited — no action needed here unless new weeks get added later.

### 3. Vector Database document
**File:** `Introduction to Vector Database/Introduction to Vector Database.md`

- Added a web-researched **11-question mock interview** (distance metrics, HNSW/IVF, choosing a vector DB, pre/post-filtering, reranking, quantization, chunking, distributed-systems concerns, a debugging scenario), then rewrote it in plainer language with an everyday example per question (Google Photos, shopping carts, food delivery, hiring pipelines, retail warehouses, GPS debugging).
- Added a **"🎯 Standard Interview Answer"** to every question — additive only, sits alongside the plain-language version rather than replacing it.
- Several deeper, additive clarifications layered in afterward: a clear decision rule for cosine vs. dot product vs. Euclidean (with real examples: customer segmentation vs. chatbot search), an even-simpler HNSW/IVF analogy plus a term-by-term IVF breakdown, a full vector-DB use/don't-use table with a jargon glossary (including a correction that Reciprocal Rank Fusion is not a search algorithm like ANN), and a mechanism-level breakdown of what metadata actually is and how pre-filtering technically narrows a search.
- New **"💬 Spontaneous Questions"** section at the end (separate from the prepared interview set by default) — currently has SQ1: is a vector database SQL, NoSQL, or its own category.
- **ChromaDB tutorial notebook** (`ChromaDB_tutorial.ipynb`) annotated cell-by-cell (30 code cells) — collections, adding by text vs. raw vectors, persistent clients, metadata filtering operators, upsert/delete.

### 4. LangChain
- New file **`LangChain/LangChain Fundamentals - Video Notes.md`** — cleaned-up notes from an intro video (the problem plain LLM calls can't solve, a support-chatbot example, and the five core components: Chains, Models, Prompts, Memory, Agents).
- **`LangChain/LangChain.md`** — added **Q2**: what LCEL is, declarative vs. imperative with a worked example, and confirming `chain = prompt | model | parser` is real code (the pipe operator explained like a Unix pipe).
- Two notebooks annotated cell-by-cell: `Langchain_Setup_and_Simple_Chain- DONE.ipynb` (note: renamed from the original filename outside this session, content unchanged) and `Langchain_Chains.ipynb` (the Mistral-7B / 4-bit quantization / HuggingFacePipeline example).
- New file **`Langchain_Setup_and_Simple_Chain_LCEL.ipynb`** — the joke-chain example rewritten in LCEL pipe style, with a side-by-side comparison table against the original `LLMChain` version.

### Open items for tomorrow
- **Step 3 of the RAG Workflow document is still empty** — no deep dive, no interview prep, no Q&A yet. Likely the next thing to tackle.
- `CLAUDE.md` at the repo root has been sitting **untracked, uncommitted** all session (an unrelated housekeeping file from an earlier `/init` task) — never explicitly asked to be committed; still an open decision.
- `Langchain_LCEL.ipynb` (the pre-existing notebook in the LangChain folder) has not been annotated yet, unlike the other three notebooks in that folder.

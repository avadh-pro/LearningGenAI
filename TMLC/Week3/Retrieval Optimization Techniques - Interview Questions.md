# Retrieval Optimization Techniques — Interview Questions

*Reproduced exactly as originally written from* Retrieval Augmented Generation (RAG)/Retrieval Optimization Techniques/Retrieval Optimization Techniques.md *— nothing reworded.*

*This set is built around the three-stage optimization framing that file is organized by — pre-retrieval, retrieval, post-retrieval — rather than RAG mechanics in general, so it deliberately avoids re-treading the RAG Workflow and Current State of RAG sets. Web-researched against current (2026) question banks and practitioner write-ups, calibrated to roughly four years of AI engineering experience. Same two-layer format as the other sections: a plain-language answer with an everyday example, then a crisp, technically precise version worth saying out loud in the room. Try answering out loud first.*

---

**🎙️ Interview Q1:** "Walk me through the three stages where you can optimize retrieval, and tell me why the order between them matters."

**✅ Strong answer:** "You get three separate chances to intervene: **before** the search (the input — how documents were chunked, how the query is phrased), **during** the search (the matching itself — hybrid, weighting), and **after** the search (the ordering — reranking, filtering). The order matters because the stages are cumulative, not alternatives: each one can only work with what the previous one handed it. A reranker is the clearest case — it reorders a list, it cannot conjure a document that retrieval never returned.

**Everyday example:** hiring. Pre-retrieval is how you word the job posting and how resumes get filed. Retrieval is the search that pulls 50 resumes off the pile. Post-retrieval is the hiring manager reading those 50 carefully and ranking them. If the best candidate never applied because the posting used the wrong words, no amount of careful reading at the end finds them — the failure happened two stages upstream and is invisible from where you're standing.

```
PRE-RETRIEVAL            RETRIEVAL              POST-RETRIEVAL
(the input)              (the matching)         (the ordering)
chunking, query      →   hybrid search      →   reranking
rewriting / expansion    BM25 + dense           cross-encoder

 ↑ shapes what CAN        ↑ decides what IS      ↑ can only reorder
   ever be found            actually found         what already arrived
```

That's also why diagnosis runs upstream-first: prove the right chunk is in the candidate set before you touch anything downstream of it."

**🎯 Standard Interview Answer:** "Retrieval optimization decomposes into three intervention points: pre-retrieval (index construction — chunking strategy — plus query conditioning via rewriting, expansion, or decomposition), retrieval (the matching function itself, typically hybrid sparse-plus-dense), and post-retrieval (reranking, filtering, compression). These are cumulative rather than substitutable, because each stage's achievable ceiling is bounded by its predecessor's recall. A reranker operating over a candidate set that never contained the relevant chunk cannot recover it — its maximum attainable precision is capped upstream. That bounding relationship is what dictates diagnostic order: establish candidate-set membership before tuning ranking."

---

**🎙️ Interview Q2:** "Why does storing a long document as one single chunk make it a weak match for almost every query — even queries it genuinely answers?"

**✅ Strong answer:** "Because the entire document gets compressed into **one** vector that has to represent everything in it simultaneously. If an article covers twelve topics, its single vector ends up a blurry average of all twelve — slightly about each, strongly about none. So it's a mediocre match for everything and a sharp match for nothing, and sharper competitors outrank it even when it's the document that actually holds the answer.

**Everyday example:** try describing a whole cookbook in one sentence. 'It's about food.' Technically true, completely useless for finding the carbonara recipe — because that one description also has to cover desserts, soups, and grilling. Cut the cookbook into individual recipes and each one gets a sharp description: 'carbonara with guanciale and pecorino.' Now the pasta query lands exactly where it should.

Concretely, take a passage covering realism, linear perspective, chiaroscuro, and oil paints:

```
ONE BIG CHUNK                       FOUR SENTENCE WINDOWS
[realism + perspective +            [realism] [perspective]
 chiaroscuro + oil paints]          [chiaroscuro] [oil paints]
        ↓                                    ↓
   one blurry vector                  four sharp vectors
"kind of about art, generally"        each about exactly one thing
        ↓                                    ↓
query: "light and shadow?"           query: "light and shadow?"
   → weak match                         → near-perfect match on #3
```

The key point for an interview: this makes chunk size a **retrieval-quality** lever, not just a context-window budgeting decision."

**🎯 Standard Interview Answer:** "A chunk's embedding is a single fixed-dimensional vector that must encode the chunk's entire semantic content. As chunk length and topical diversity grow, that vector converges toward the centroid of its constituent topics — it becomes an average rather than a sharp representation of any one of them. The measurable consequence is depressed cosine similarity against any specific query: the chunk is moderately similar to many queries and highly similar to none, so it ranks below narrower competitors even when it contains the answer. This is embedding dilution, and it's distinct from the boundary-fragmentation failure of fixed-size chunking — dilution degrades a chunk that is internally coherent but topically broad."

---

**🎙️ Interview Q3:** "Sentence-window retrieval is often described as getting the best of both worlds on chunk size. What does it actually decouple, and why isn't that just splitting the difference?"

**✅ Strong answer:** "It separates the thing you **search against** from the thing you **hand to the LLM**. You embed and match on a single sentence — tiny, sharp, no dilution — but when that sentence wins, you return it *plus its neighbours*, so the generator gets the surrounding context it needs to actually use it.

**Everyday example:** a book's index. The entry is three words — 'chiaroscuro, p. 47' — and that terseness is exactly why searching the index works. But you don't read three words; you turn to page 47 and read the whole page. Searching is precise *because* it's terse; reading is useful *because* it isn't.

```
PLAIN CHUNKING — one size forced to do both jobs
  chunk ──embed & match──►  and the SAME chunk ──► LLM
    small = sharp match, thin context
    large = rich context, blurry match     ← you must pick one

SENTENCE-WINDOW RETRIEVAL — two sizes, two jobs
  sentence ──embed & match──► wins
                                 └─► return sentence + neighbours ──► LLM
    match on the small thing, return the big thing
```

And that's why it isn't a compromise: a plain chunk-size decision is a genuine trade-off where every gain in precision costs context. Decoupling **removes the constraint** that forced one size to serve both objectives, rather than finding a midpoint on it. Structurally it's the same small-to-big idea as parent-child retrieval."

**🎯 Standard Interview Answer:** "Sentence-window retrieval decouples the embedding/matching unit from the generation/context unit. Each sentence is embedded and indexed independently — minimizing embedding dilution and maximizing match precision — while the retrieval response substitutes a surrounding window (the matched sentence plus *k* neighbours) as the context passed to the generator. It's the same small-to-big principle as parent-child retrieval: retrieve on a precise child representation, generate from a fuller parent. Because the two units are configured independently, this is not a point on the precision-versus-context curve; it removes the single-chunk-size constraint that produced the curve."

---

**🎙️ Interview Q4:** "Sliding-window chunking deliberately stores overlapping content. What does that overlap buy you, and what does it cost?"

**✅ Strong answer:** "It buys insurance against cutting a thought in half. Sentences lean on their neighbours — a chunk reading only *'It was invented in Florence'* is useless, because 'it' points at something that got left behind in the previous chunk. Overlap keeps the antecedent attached.

The cost is that you're storing the same text more than once. Every overlapping token gets embedded again, stored again, and searched again — so roughly 20% overlap is roughly a 20% increase in chunk count, embedding spend, and index footprint. It also produces near-duplicate hits: two adjacent chunks both containing the matched sentence can occupy two of your top-K slots and crowd out a genuinely different result, which is part of why MMR or dedup at fusion time exists.

**Everyday example:** photocopying a book two pages at a time with one page of overlap. You never lose a sentence across a page break — and you've made about 1.5× the copies.

Overlap is a hedge against one specific failure mode, not a free improvement."

**🎯 Standard Interview Answer:** "Overlap preserves cross-boundary coherence — anaphora, continued clauses, and sentence pairs whose meaning is jointly determined — at the cost of storing redundant content. It inflates chunk count, embedding cost, and index size roughly proportionally to the overlap ratio (common defaults sit around 10-20%), and it injects near-duplicate candidates into the top-K, consuming retrieval slots; MMR or fusion-time deduplication is the standard mitigation. Its value is corpus-dependent — it pays off in proportion to how much semantic meaning actually spans chunk boundaries."

**🔁 Interview Q4 (follow-up):** "A 2026 systematic evaluation found chunk overlap gave no measurable retrieval benefit and only raised indexing cost. Does that mean you should stop using overlap?"

**✅ Strong answer:** "It means stop using it *by default and unmeasured* — not stop using it. That result is real, but it's one corpus and one retrieval stack, and benchmarks like Natural Questions are largely self-contained factoid passages, where an answer sentence rarely depends on the sentence before it. Overlap earns its keep precisely where meaning *does* span boundaries: legal text full of 'notwithstanding the foregoing,' technical docs full of 'this configuration,' interview transcripts where an answer only makes sense attached to the question.

The honest interview position is: treat overlap as a hypothesis to test against your own eval set, not a number to copy from a blog post. And note the sharper move — sentence-window retrieval gets you the same cross-boundary protection *without* paying the storage cost, because the neighbours are fetched at read time rather than duplicated at index time."

**🎯 Standard Interview Answer:** "The finding is corpus-dependent rather than universal. Benchmarks composed of self-contained factoid passages exhibit low cross-boundary semantic dependency, so overlap adds redundancy without recall gain. Corpora with high referential density — legal, clinical, conversational, technical documentation — are where its value concentrates. The methodologically correct response is to treat overlap ratio as a tunable evaluated against a domain-specific retrieval eval set, and to prefer window-expansion-at-read-time (sentence-window or parent-child retrieval) where available, since it achieves cross-boundary context without index-time duplication."

---

**🎙️ Interview Q5:** "Query expansion and query rewriting both happen pre-retrieval and both touch the query. Why are they two separate techniques rather than one?"

**✅ Strong answer:** "Because they pull in opposite directions. Expansion **adds** terms to widen the net — synonyms, related concepts, paraphrases — which helps **recall**: you find documents that never used the user's exact words. Rewriting **restates** the query to sharpen it — fixing typos, resolving ambiguity, reordering for clarity — which helps **precision**: you stop matching things the user never meant.

**Everyday example:** you ask a librarian for 'laptop stuff.' Expansion is the librarian also checking 'notebook computer' and 'portable PC' on the shelves. Rewriting is the librarian asking 'do you mean repair manuals or buying guides?' and searching for *that* instead. One widens, one narrows.

```
                    original query
                          │
        ┌─────────────────┴─────────────────┐
    EXPANSION                           REWRITING
    add terms                           restate it
  "laptop" → laptop OR notebook      "weather Tokyo tomorrow" →
   OR portable computer               "Tokyo weather forecast for tomorrow"
        │                                    │
   widens the net                       sharpens the aim
      ↑ recall                            ↑ precision
```

Worth flagging the failure mode too: expansion isn't free. A 'helpful' rewrite that injects the wrong domain terms quietly poisons the candidate set — you widen the net and pull in confidently irrelevant content. Because the two move recall and precision in opposite directions, applying both unconditionally can cancel out; production systems usually gate them on query characteristics rather than running both every time."

**🎯 Standard Interview Answer:** "They optimize opposite sides of the precision-recall trade-off, which is why they remain distinct operators. Expansion augments the query's term set — lexical synonyms, knowledge-graph neighbours, or LLM-generated paraphrases — raising recall by increasing the probability that some surface form matches indexed content; multi-query and HyDE belong to this family, HyDE specifically embedding a generated hypothetical answer so matching occurs answer-to-answer rather than question-to-answer. Rewriting transforms the query into a better-specified single query — disambiguation, typo correction, intent normalization, multi-turn coreference resolution — raising precision. Both add an LLM call to the critical path, and expansion carries a documented precision-degradation risk when generated terms drift off-domain, so they're typically gated on query characteristics rather than applied unconditionally."

---

**🎙️ Interview Q6:** "Your hybrid search returns a BM25 score and a cosine similarity for the same document. Why can't you just average the two?"

**✅ Strong answer:** "Because they aren't on the same scale, so averaging them is meaningless arithmetic. Cosine similarity is bounded — roughly -1 to 1. BM25 is unbounded and query-dependent — it might be 2 on one query and 40 on another, depending on term rarity and document length. Average them and BM25's larger magnitudes dominate the blend regardless of whether keyword matching actually mattered for that query.

**Everyday example:** averaging a movie rating out of 5 with a temperature in Fahrenheit. You'll get a number. It will mean nothing.

```
BM25:    0 ──────────────────────────► ∞    (unbounded, query-dependent)
cosine: -1 ────────► 0 ────────► 1          (bounded)

naive average    → BM25 magnitude swamps cosine, every time
normalize + alpha → works, but needs per-corpus calibration
RRF (rank only)   → scale-free by construction: Σ 1/(k + rank)
```

Two ways out: normalize both to a common range and blend with a weight (alpha), or skip scores entirely and fuse on **rank position** — which is exactly what Reciprocal Rank Fusion does. RRF only asks 'where did this place on each list,' and rank 1 means the same thing no matter which scoring system produced it. That's why RRF is the common default: it needs no per-corpus score calibration at all."

**🎯 Standard Interview Answer:** "Sparse and dense scores occupy incomparable ranges: BM25 is an unbounded, corpus- and length-dependent sum of IDF-weighted term contributions, while cosine similarity is bounded to [-1, 1]. Unnormalized linear combination therefore lets the sparse component's magnitude dominate the fused ordering irrespective of its discriminative value. The two standard remedies are per-result-set score normalization (min-max or z-score) followed by weighted convex combination — the alpha parameter — or rank-based fusion, canonically Reciprocal Rank Fusion, computing Σ 1/(k + rank_i), which is scale-invariant by construction because it discards raw scores entirely. RRF is the common default precisely because it requires no per-corpus calibration; tuned weighted fusion can outperform it where sufficient labeled evaluation data exists."

**🔁 Interview Q6 (follow-up):** "RRF throws away the actual similarity scores and keeps only rank position. Isn't that discarding real information?"

**✅ Strong answer:** "It is, deliberately — and the information it discards is exactly the part that isn't comparable across the two systems. Keeping it is what caused the scale problem in the first place. What RRF keeps is the part both systems mean the same way: 'this was my best result, this was my second.'

The cost is genuine though: RRF is blind to margin. A document that barely edged into first place and one that won by a mile contribute identically, so you lose the confidence signal.

The practical answer is that you usually don't stop at fusion. RRF merges cheaply and scale-free, then a cross-encoder reranks the fused shortlist and puts real, directly comparable relevance scores back onto the small set that survived. You get scale-free merging *and* calibrated scoring — just at different stages. Where fusion genuinely is the terminal step, or where something downstream gates on score magnitude (a confidence threshold, say), normalized weighted fusion becomes the better choice despite the calibration burden."

**🎯 Standard Interview Answer:** "RRF's rank-only formulation deliberately discards score magnitude because magnitude is the non-comparable component across heterogeneous retrievers. The cost is loss of margin sensitivity — a dominant top-1 and a marginal top-1 contribute identically. This is acceptable because fusion is typically not the terminal ranking step: a cross-encoder applied to the fused candidate set restores calibrated, comparable relevance scores over the surviving shortlist. Where fusion is terminal, or where downstream confidence gating depends on score magnitude, normalized weighted fusion is preferable despite requiring per-corpus calibration."

---

**🎙️ Interview Q7:** "In a hybrid setup with an alpha weighting between keyword and vector search, what's the right value of alpha?"

**✅ Strong answer:** "There isn't a universal one — the right alpha is whatever matches your actual query distribution, and the only way to find it is to measure on your own queries. A parts catalogue where most queries are part numbers wants alpha near the keyword end. A support knowledge base where people describe symptoms in their own words wants it near the semantic end.

The trap is assuming higher alpha is 'smarter' because vector search sounds more sophisticated. It just shifts weight toward semantics — which actively hurts when the query was an exact identifier and a near-miss is worthless.

**Everyday example:** two libraries. One is a parts warehouse where people walk in holding a part number. One is a poetry library where people walk in describing a feeling. Same shelves, completely different optimal search strategy.

So the real answer: grid-search alpha against a labeled eval set built from production queries, and if the traffic is genuinely bimodal, route per query type rather than forcing one global alpha to serve both populations badly."

**🎯 Standard Interview Answer:** "Alpha is corpus- and workload-specific and must be calibrated empirically against a labeled evaluation set drawn from representative production traffic, typically by grid search over NDCG or Recall@K. No transferable default exists, because the optimum tracks the mix of lexical-exact versus semantic-intent queries in the actual distribution — identifier-heavy workloads optimize toward the sparse end, natural-language-intent workloads toward the dense end. Reported lifts for tuned hybrid over either single method are real but corpus-bound (on the order of a 7% NDCG improvement over BM25-alone or dense-alone on the WANDS e-commerce benchmark). For genuinely bimodal traffic, per-query-type weighting or an explicit query router outperforms any single global alpha, at the cost of adding a classification step to the critical path."

---

**🎙️ Interview Q8:** "Why can't you just use the cross-encoder for the whole search and skip first-stage retrieval entirely?"

**✅ Strong answer:** "Two reasons, and the second is the one that actually settles it.

The obvious one is cost: a cross-encoder runs a full model pass for every query-document *pair*, so it scales with corpus size. On real hardware, something like `bge-reranker-v2-m3` runs on the order of 50ms per pair — reranking 30 candidates already adds over a second of latency. Do that across a million chunks and you don't have a product.

The deeper reason is architectural: **a cross-encoder has nothing to precompute.** A bi-encoder can embed every document once, offline, because the document's vector doesn't depend on the query. A cross-encoder's entire advantage is that it reads the query and the document *together* — which means its score literally cannot exist until the query arrives. There is no index to build.

**Everyday example:** a bi-encoder is a library catalogue — written once, reused for every visitor. A cross-encoder is a librarian who reads your specific question and then reads the book with it in mind. You cannot pre-read every book against every possible question.

```
BI-ENCODER (first stage)             CROSS-ENCODER (rerank only)
doc   ──► vector  (offline, once)    (query, doc) ──► score
query ──► vector  (at query time)     needs BOTH → nothing to precompute
compare vectors: cheap, indexable     full pass per pair: O(candidates)
```

So the two-stage shape isn't a performance compromise — it's the only shape available. Something cheap and precomputable narrows a million to fifty; something expensive and query-aware reads those fifty properly."

**🎯 Standard Interview Answer:** "Cross-encoders jointly encode the query-document pair, so no document representation can be precomputed independently of the query — which makes index construction impossible and forces a full forward pass per candidate at query time. Cost scales linearly with candidate count and is prohibitive at corpus scale; representative figures are on the order of tens of milliseconds per pair, so reranking even a few dozen candidates contributes seconds of latency. Bi-encoders admit offline document embedding and ANN indexing precisely because their document representation is query-independent. Retrieve-then-rerank is therefore a structural necessity rather than an optimization: a query-independent indexable model reduces the corpus to a shortlist, and the query-dependent model — which gains accuracy by modelling term-level interaction — is applied only where its per-item cost is affordable."

**🔁 Interview Q8 (follow-up):** "Could you distill the cross-encoder into something cheap enough to run over the whole corpus?"

**✅ Strong answer:** "You can make it cheaper — distilling into smaller cross-encoders is an active line of work and it cuts per-pair cost meaningfully. But it doesn't change the shape of the problem, because the binding cost isn't the model's size, it's the **number of pairs**. Even a free cross-encoder still needs one pass per document, so you're doing a million passes per query instead of one indexed lookup.

What distillation actually buys you is a **bigger shortlist** — you can afford to rerank 200 candidates instead of 30, which raises the recall ceiling the reranking stage gets to work against. That's a real win, just not the one the question implies.

The architecture people actually reach for when they want interaction modelling at index scale is **late interaction**, ColBERT-style: precompute per-token embeddings so some of the query-document interaction survives into something you can still index. That's the genuine answer to 'cross-encoder quality without cross-encoder cost' — not distillation alone."

**🎯 Standard Interview Answer:** "Distillation reduces per-pair inference cost but does not alter the asymptotic requirement of one forward pass per candidate, so full-corpus cross-encoding remains infeasible regardless of parameter count — the binding constraint is candidate count. The practical benefit of a distilled reranker is an enlarged rerank window, raising the recall ceiling available to the reranking stage, rather than elimination of first-stage retrieval. The architecture that targets interaction modelling at index scale is late interaction — ColBERT-style per-token embeddings with MaxSim scoring — preserving partial query-document interaction while remaining precomputable and indexable, at the cost of a substantially larger index footprint."

---

**🎙️ Interview Q9:** "A RAG answer is wrong, and you've already established it's a retrieval problem rather than a generation problem. How do you work out *which* retrieval stage broke?"

**✅ Strong answer:** "Work upstream to downstream, because each check rules out everything below it.

**First — is the correct chunk even in the index?** Search for it directly by its text. If it isn't there, it's an ingestion or chunking problem, and nothing downstream matters.

**Second — if it exists, is it in the raw candidate set *before* reranking?** Log the top-50 pre-rerank. If it's missing there, first-stage retrieval failed — which points either at the query (vague, vocabulary-mismatched, would expansion or rewriting have caught it?) or at the chunk itself (diluted by being too large).

**Third — if it *was* in the candidates but didn't survive into the final K?** That's a ranking problem: the reranker or the fusion weighting.

**Everyday example:** a package didn't arrive. You check in order — was it ever shipped, did it reach the local depot, was it loaded onto the truck. Checking the truck first tells you nothing if it never shipped.

```
Is the chunk in the index?          NO → ingestion / chunking
         │ YES
Is it in the top-50 pre-rerank?     NO → retrieval: query or dilution
         │ YES
Did it survive into the final K?    NO → ranking: reranker / fusion
         │ YES
    → context assembly or generation, not retrieval at all
```

The single highest-value habit here is **logging the pre-rerank candidate set**. That one log line is what separates 'never found it' from 'found it and ranked it badly' — two problems that look identical from the output and have completely disjoint fixes."

**🎯 Standard Interview Answer:** "Diagnosis proceeds upstream-first, since each stage's output bounds the next. Step one: verify the target chunk exists in the index with expected text and metadata — failure localizes to ingestion or chunking. Step two: inspect the pre-rerank candidate set by logging top-N before any reordering — absence localizes to first-stage retrieval, implicating query formulation (ambiguity, vocabulary mismatch, absent expansion/rewriting) or chunk-level embedding dilution. Step three: if the chunk was present pre-rerank but absent from the final context, the failure is in ranking — reranker behaviour, fusion weighting, or top-K truncation. Instrumenting the pre-rerank candidate set is the highest-leverage single piece of observability in this pipeline, because it's what distinguishes a recall failure from a precision/ordering failure — indistinguishable at the output, but requiring entirely disjoint remediations."

---

**What interviewers are really scoring for, across all of the above:**
- Whether you frame optimization as three distinct intervention points with a bounding relationship between them, rather than a grab-bag of tricks
- Whether you can explain *why* a stage's ceiling is capped by the stage before it — not just assert that it is
- Whether score-scale and normalization problems surface naturally the moment fusion comes up, instead of needing to be prompted
- Whether "what's the right value for X" gets "measure it against your own query distribution" rather than a memorized default
- Whether an architectural constraint (a cross-encoder has nothing to precompute) is distinguished from a mere cost constraint
- Whether a diagnostic question produces an ordered, falsifiable procedure instead of a list of things to "try"
- Whether you volunteer the cost side of a technique (index inflation, added LLM calls, added latency) without being asked for the downside

**Sources consulted while calibrating this section:**
- [RAG_Interview_Doc — 105 consolidated RAG interview questions covering indexing, retrieval, re-ranking, and evaluation (GitHub)](https://github.com/ayusingh-54/RAG_Interview_Doc)
- [Retrieval-Augmented Generation for Large Language Models: A Survey (arXiv)](https://arxiv.org/pdf/2312.10997)
- [Modular RAG: Transforming RAG Systems into LEGO-like Reconfigurable Frameworks (arXiv)](https://arxiv.org/pdf/2407.21059)
- [RAGSmith: Finding the Optimal Composition of RAG Methods Across Datasets (arXiv)](https://arxiv.org/pdf/2511.01386)
- [Hybrid Search Alpha Tuning For RAG: How-To — LlamaIndex](https://www.llamaindex.ai/blog/llamaindex-enhancing-retrieval-performance-with-alpha-tuning-in-hybrid-search-in-rag-135d0c9b8a00)
- [DAT: Dynamic Alpha Tuning for Hybrid Retrieval in RAG (arXiv)](https://arxiv.org/html/2503.23013v1)
- [Hybrid Search and Re-ranking in Production RAG 2026: BM25, Dense, Cross-encoders, Fusion — AppScale](https://appscale.blog/en/blog/hybrid-search-and-reranking-production-rag-bm25-dense-cross-encoder-2026)
- [Hybrid Search for RAG: Combining BM25 and Dense Vector Search (2026 Guide) — Denser](https://denser.ai/blog/hybrid-search-for-rag/)
- [Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking (arXiv)](https://arxiv.org/html/2607.11933v1)
- [In Defense of Cross-Encoders for Zero-Shot Retrieval (arXiv)](https://arxiv.org/pdf/2212.06121)
- [When Query Expansion Hurts RAG — Thinking Loop](https://medium.com/@ThinkingLoop/when-query-expansion-hurts-rag-23139f06d8d4)
- [RAG chunking explained: chunk size, overlap, and what it costs — daily.dev](https://daily.dev/posts/rag-chunking-explained-chunk-size-overlap-and-what-it-costs-shmilcnmh)
- [Best Chunking Strategies for RAG (and LLMs) in 2026 — Firecrawl](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)
- [When More Documents Hurt RAG: Mitigating Vector Search Dilution (arXiv)](https://arxiv.org/pdf/2606.11350)
- [Retrieval strategies: Finding the right information — Anyscale Docs](https://docs.anyscale.com/rag/quality-improvement/retrieval-strategies)

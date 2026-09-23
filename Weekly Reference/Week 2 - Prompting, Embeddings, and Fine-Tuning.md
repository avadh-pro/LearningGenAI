# Week 2 — Prompting, Embeddings, and Fine-Tuning

> **What this week is really about:** you have a pretrained model. It is good, but it is not *yours*. This week is the complete menu of ways to make a general model behave the way your problem needs — from the cheapest (change the words you send it) to the most expensive (change the numbers inside it).
>
> Everything here hangs off one sentence: **a language model is a next-token probability machine, and every technique in this week is a different way of reshaping which token comes next.** Prompting reshapes it temporarily, at inference time. Fine-tuning reshapes it permanently, by editing weights. Embeddings are what you use to *find* the right context to reshape it with.

---

## 0. The week in one picture

There are exactly **three levers** you can pull to change what a model outputs. Everything in Week 2 is one of them.

```
                         YOU WANT A DIFFERENT OUTPUT
                                    |
        +---------------------------+---------------------------+
        v                           v                           v
  1. CHANGE THE INPUT        2. ADD KNOWLEDGE           3. CHANGE THE MODEL
     (Prompting)                (RAG - Week 3)             (Fine-tuning)
        |                           |                           |
  zero-shot, few-shot        embeddings -> vector DB     SFT, LoRA/QLoRA,
  CoT, chaining,             -> retrieve -> stuff into    DPO/PPO/GRPO
  structured output          the prompt
        |                           |                           |
  cost: ~free                 cost: low, ongoing         cost: high, one-off
  latency: instant            latency: +50-300ms         latency: none added
  changes: behaviour          changes: knowledge         changes: behaviour
           temporarily                                          permanently
```

**The rule that survives every project:** try them in that order — **prompt → retrieve → train**. Most teams that fine-tune first discover six weeks later that a better prompt would have done it. Section 10 makes this concrete.

**Where each Week 2 topic lands:**

| Topic | Which lever | Why it's in this week |
|---|---|---|
| Prompt engineering | 1 | The cheapest lever, pulled first |
| Vector embeddings | 2 | The machinery that makes retrieval possible |
| Hugging Face | — | The place all the models, data and training code live |
| BERT | 2 & 3 | The encoder family — makes embeddings, and is the cheapest thing to fine-tune |
| Open vs closed source | 3 | You can only fine-tune what you can download |
| Quantization | 3 | What makes fine-tuning big models possible on one GPU |
| LoRA / QLoRA / PEFT | 3 | The *mechanism* of cheap fine-tuning |
| PPO / DPO / GRPO | 3 | The *method* of teaching preference, not just imitation |

---

# Part 1 — Prompt Engineering

## 1.1 Why prompting works at all

**One line first:** a prompt works because the model does not "read your instruction and obey it" — it continues your text, and your text changes which continuation is most probable.

The model computes, for every possible next token, a probability. Given `"The capital of France is"`, the distribution looks roughly like:

```
"Paris"    ####################################  92%
" the"     ###                                    3%
" a"       ##                                     2%
" located" #                                      1%
...
```

A prompt is just extra text placed *before* that computation. It doesn't add knowledge and it doesn't change a single weight — it **moves probability mass around** by putting the model in a region of text where the answer you want is the likely continuation.

That is the whole theory, and it explains three things that otherwise look like magic:

1. **Why "You are an expert Python developer" helps.** In the training data, text that follows expert framing is *written differently* — more precise, more technical. You are steering toward that neighbourhood of the distribution.
2. **Why examples work so well.** Two worked examples make the third one's format overwhelmingly probable. The model is pattern-continuing, not rule-following.
3. **Why prompting cannot fix missing knowledge.** If the fact was never in training, no phrasing raises its probability. That's what RAG is for — and it's the single most useful boundary line in the whole field.

> **The restaurant framing from the course notes, kept:** saying *"food, please"* gets you a surprise dish; saying *"I'd like a Ghee Podi Idli"* gets you what you wanted. A prompt is an order, and specificity is the entire skill.

## 1.2 The anatomy of a good prompt

Almost every strong prompt has the same five parts. Missing parts are where bad answers come from.

| Part | What it does | Example |
|---|---|---|
| **Role** | Sets the register and vocabulary | `You are a senior support agent at a food-delivery company.` |
| **Task** | The actual instruction, one clear verb | `Classify the ticket into exactly one of these 10 queues.` |
| **Context** | Facts the model can't know | `Queue definitions: ... Recent policy: refunds within 30 days.` |
| **Format** | The shape of the answer | `Reply with JSON: {"queue": string, "confidence": number}` |
| **Constraints** | The guard rails | `If unsure, use "Other". Never invent a queue name.` |

A practical debugging rule: **every bad response means something was missing from one of those five boxes.** Before rewording, ask *which box was empty?*

```
BAD:  "Categorise this ticket."

GOOD: "You are a support triage agent.                               <- Role
       Classify the ticket below into exactly one queue.             <- Task
       Queues: Billing, Refunds, Delivery, Technical, Other.         <- Context
       Respond with JSON only: {"queue": "<name>"}                   <- Format
       If the ticket matches no queue, use "Other". Never explain.   <- Constraints

       Ticket: 'My payment went through twice yesterday.'"
```

## 1.3 Zero-shot prompting

**Ask, with no examples.** The course notes call it *"the YOLO of AI interactions"* — fair, but it undersells how far it goes now. Frontier models in 2026 handle zero-shot on tasks that needed five examples in 2023.

```python
from openai import OpenAI
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user",
               "content": "Explain quantum computing in simple terms."}]
)
print(resp.choices[0].message.content)
```

**Use it when:** the task is common, the output format is loose, and you're exploring. It's always the first thing to try — if zero-shot works, everything below is wasted effort.

**It breaks when:** the output format matters exactly, the task uses your private conventions, or the label set is idiosyncratic ("classify into *our* 10 queues" — the model has never seen your queues).

## 1.4 Few-shot prompting

**Show two to five worked examples, then ask for the next one.** The course's framing — *showing the AI a couple of magic tricks, then asking it to perform the next* — is exactly right.

```
Translate English to French:

English: Hello, how are you?
French: Bonjour, comment ca va?

English: What is your name?
French: Comment vous appelez-vous?

English: Where is the library?
French:                                 <- the model completes this
```

**Four things that are non-obvious and matter a lot:**

1. **Format is doing more work than content.** Research on in-context learning found that examples with *wrong* labels still improve performance substantially, as long as the label space and the format are right. The examples mostly teach *shape*, not *truth*. So: make your examples structurally perfect, and don't agonise over picking the "best" ones.
2. **Order matters, and the last example matters most.** Recency bias is real. If your classes are imbalanced across the examples, the output skews. Shuffle and re-test if one class is over-predicted.
3. **Diminishing returns hit fast.** 1 → 3 examples is a big jump; 8 → 20 usually isn't, and you pay for every token on every call.
4. **Cover the edge cases, not the easy cases.** One example of the ambiguous case is worth five of the obvious case.

**One-shot** is just few-shot with a single example — worth knowing as a term, not as a separate technique.

## 1.5 Chain-of-Thought (CoT)

**Make the model show its working before it answers.** The course's *"math-class style, show your work"* is the right picture.

Why it actually works, mechanically: the model has a fixed, small amount of computation per generated token. A hard question answered in one token has to be solved in that one forward pass. Letting it generate reasoning tokens first gives it **more compute steps**, and each intermediate conclusion becomes context that conditions the next one.

```
BAD:  "A shop has 23 apples, sells 7, buys 12 more. How many? Answer with a number."
      -> often wrong on harder variants

GOOD: "A shop has 23 apples, sells 7, buys 12 more. How many?
       Think step by step, then give the final number."
      -> 23 - 7 = 16; 16 + 12 = 28. Answer: 28
```

**The three variants worth knowing:**

| Variant | What it is |
|---|---|
| **Zero-shot CoT** | Just append *"Let's think step by step."* One sentence, surprisingly effective. |
| **Few-shot CoT** | Provide examples that *include* the reasoning, not just the answer. Stronger, more expensive. |
| **Self-consistency** | Generate the reasoning 5–10 times at temperature > 0, then take the majority answer. Big accuracy gain, linear cost increase. |

**⚠️ The 2026 caveat — the biggest change in this whole section.** On **reasoning models** (models trained to think before answering, with an internal reasoning phase), explicit CoT instructions are at best redundant and at worst harmful. These models already reason internally; telling them *how* to reason overrides a process that was specifically trained to be better than your instructions. On those models you set a **thinking budget** (how long to reason) rather than scripting the steps. See [Every AI Prompting Technique That Works on Reasoning Models (2026)](https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026).

**So the current rule is:** *prescribe goals and constraints, not reasoning paths.* CoT prompting is still correct for ordinary (non-reasoning) models and for small local models — which is most of what you fine-tune.

## 1.6 Prompt chaining

**Break one hard task into several easy calls, feeding each answer into the next.** The course's *treasure hunt* analogy holds: one clue leads to the next.

```
Call 1: "List three popular programming languages."
        -> "Python, JavaScript, Java"
                |
                v
Call 2: "Explain the primary use case for each of these:
         Python, JavaScript, Java"
        -> detailed answer
```

**Why bother instead of asking once?** Four real reasons:

1. **Each step is independently testable.** When the final answer is wrong, you can see *which* step broke. A single mega-prompt is a black box.
2. **Each step can use a different model.** Cheap model extracts, expensive model reasons, cheap model formats. Big cost savings.
3. **You can put code between the steps** — validate, filter, call an API, hit a database.
4. **Attention degrades over long, multi-instruction prompts.** Five instructions in one prompt means the model reliably follows about three.

**The cost:** more latency (calls are sequential) and more total tokens. This is also exactly where **tracing** starts to matter — with a chain you need to see each step's input and output, which is the Week 6 LLMOps topic.

> **Chaining is the direct ancestor of agents.** A chain with fixed steps is a pipeline; a chain where the *model* decides the next step is an agent (Week 4).

## 1.7 Structured output — the technique the course notes don't cover

If you are calling an LLM from code, you almost never want prose. You want JSON your program can parse. There are three levels of reliability:

| Level | How | Reliability |
|---|---|---|
| **Ask nicely** | `"Respond with JSON only."` | ~90% — and the 10% crashes your parser |
| **JSON mode** | Provider flag forcing syntactically valid JSON | Valid JSON, but the *schema* isn't guaranteed |
| **Schema-constrained decoding** | Supply a JSON Schema / Pydantic model; the decoder is constrained so invalid tokens are impossible | ~100% structurally correct |

```python
from pydantic import BaseModel

class Ticket(BaseModel):
    queue: str
    urgency: int
    summary: str

resp = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Triage: {ticket_text}"}],
    response_format=Ticket,
)
t = resp.choices[0].message.parsed   # a real Ticket object, not a string
```

**Why this belongs in a fine-tuning week:** *"the model won't reliably produce my format"* is the single most common **stated** reason teams fine-tune — and constrained decoding solves it for free. Check this before you spend a GPU day.

## 1.8 System, user, assistant — the three roles

```python
messages = [
  {"role": "system",    "content": "You are a terse support agent. Never apologise twice."},
  {"role": "user",      "content": "My order is late."},
  {"role": "assistant", "content": "I've checked - it's 12 minutes out."},   # prior turn
  {"role": "user",      "content": "Can I cancel?"},
]
```

- **system** — persistent instructions, personality, rules. Weighted more heavily by instruction-tuned models than the same text in a user turn.
- **user** — the request.
- **assistant** — what the model said before. Putting *fabricated* assistant turns here is a legitimate few-shot technique: it demonstrates the exact output shape in the exact place the model produces it.

This structure isn't cosmetic — it is the **chat template** the model was fine-tuned on. Using the wrong template on a local model (or none at all) visibly degrades quality, which is why `tokenizer.apply_chat_template()` exists and why it shows up in every fine-tuning notebook.

## 1.9 Common failure modes and the fix

| Symptom | Real cause | Fix |
|---|---|---|
| Ignores part of the instruction | Too many instructions in one prompt | Split into a chain, or number the rules |
| Invents facts | Asked for knowledge it lacks | RAG, not a better prompt |
| Output format drifts | Format described in prose | Schema-constrained decoding |
| Over-explains | No length constraint | `"Answer in at most 2 sentences."` |
| Over-predicts one class | Imbalanced or recency-biased examples | Rebalance and shuffle the shots |
| Works in the playground, fails in prod | Prod input is messier than your test input | Test on real traces, not clean examples |
| Refuses a benign request | Role framing sounds adversarial | Rephrase the role, state the legitimate purpose |

## 1.10 What changed by 2026

- **Reasoning models made CoT prompting partly obsolete.** Frontier models reason internally; you tune a *thinking budget* instead of scripting steps. Scripting the reasoning on these models measurably hurts.
- **"Context engineering" replaced "prompt engineering" as the job.** The hard part is no longer word choice — it's deciding *what goes into the window*: which retrieved chunks, which history, which tools, in what order, within a budget. The prompt is one input among several.
- **Few-shot is used less for capability, more for format.** Models got good enough that examples mostly teach shape now.
- **Structured outputs are a solved problem.** Schema-constrained decoding is standard across providers; hand-parsing JSON out of prose is a legacy pattern.
- **Model-agnostic prompting is the safer style.** Prompts that specify *goals and constraints* survive model upgrades; prompts that specify *reasoning steps* break on the next model.

## ✅ Key takeaways — prompting

1. A prompt reshapes the next-token distribution. It cannot add knowledge that isn't there.
2. Role + Task + Context + Format + Constraints. A bad answer means one box was empty.
3. Zero-shot first, always. Add shots only when format or private conventions need demonstrating.
4. CoT buys compute — but on reasoning models, let the model reason its own way.
5. Chain when steps are independently testable, cheaper apart, or need code in between.
6. Use schema-constrained decoding before you even consider fine-tuning for format.

---

# Part 2 — Vector Embeddings

## 2.1 What an embedding is

**One line:** an embedding turns a word (or sentence, image, anything) into a list of numbers, arranged so that **similar things get similar numbers**.

That's the whole idea. Computers can't compare meanings, but they can compare numbers — so we translate meaning into coordinates.

**The map analogy 🗺️** — every word is a dot on a giant map. Related words sit close; unrelated words sit far apart. The "address" of the dot *is* the embedding.

```
                    ^ dimension 2
                    |
        queen  king |
           *   *    |                * car
                    |           * truck
     apple *        |
   banana *         |
  ------------------+------------------>  dimension 1
```

- "apple" → `[0.9, 0.2, 0.1]`
- "banana" → `[0.8, 0.3, 0.1]` ← close numbers = similar meaning
- "car" → `[0.1, 0.9, 0.6]` ← very different = different meaning

Real embeddings have 384 to 4096 dimensions rather than 3, but the intuition is identical: **direction in the space encodes meaning.**

## 2.2 Why dense, and not one-hot

Before embeddings, the standard way to represent a word was **one-hot encoding**: a vector as long as your vocabulary, with a single 1.

```
vocabulary: [apple, banana, car, king, queen]   (5 words)

apple  = [1, 0, 0, 0, 0]
banana = [0, 1, 0, 0, 0]
king   = [0, 0, 0, 1, 0]
```

Two fatal problems:

1. **Size.** A real vocabulary is 50,000+ words, so every word is a 50,000-long vector that is 99.998% zeros.
2. **No meaning.** Every pair of distinct words is *exactly* equally far apart. "apple" is as related to "banana" as it is to "car". The representation carries zero semantic information.

A dense embedding fixes both: 384 numbers instead of 50,000, and distance now *means* something.

| | One-hot | Dense embedding |
|---|---|---|
| Length | vocabulary size (50k+) | 384 – 4096 |
| Contents | one 1, rest zeros | all non-zero floats |
| Distance between "apple"/"banana" | same as any other pair | small |
| Learned from data? | no | yes |

## 2.3 How similarity is actually measured

Three metrics, and it's worth being precise about which is which.

**Cosine similarity — the default.** Measures the *angle* between two vectors, ignoring their length. Range −1 (opposite) to 1 (identical direction).

```
cos(A, B) = (A · B) / (|A| × |B|)
```

Worked example with tiny vectors:

```
apple  = [0.9, 0.2]
banana = [0.8, 0.3]

dot     = 0.9*0.8 + 0.2*0.3 = 0.72 + 0.06 = 0.78
|apple| = sqrt(0.81 + 0.04) = 0.922
|banana|= sqrt(0.64 + 0.09) = 0.854

cos = 0.78 / (0.922 * 0.854) = 0.78 / 0.787 = 0.991   -> nearly identical meaning
```

Same maths against `car = [0.1, 0.9]`:

```
dot = 0.9*0.1 + 0.2*0.9 = 0.09 + 0.18 = 0.27
cos = 0.27 / (0.922 * 0.906) = 0.32                   -> unrelated
```

**Dot product.** Cosine without the normalisation, so longer vectors score higher. Faster (no division). If your vectors are already unit-length (`|v| = 1`), dot product and cosine are *mathematically identical* — which is why most embedding models normalise their output and most vector databases default to dot product.

**Euclidean (L2) distance.** Straight-line distance. Lower is better, opposite convention to the other two. Rarely the right choice for text.

| Metric | Measures | Range | Use when |
|---|---|---|---|
| **Cosine** | angle only | −1 → 1, higher better | Text. The default. |
| **Dot product** | angle + magnitude | unbounded, higher better | Normalised vectors (identical to cosine, faster) |
| **Euclidean** | straight-line gap | 0 → ∞, lower better | Coordinates, some image features |

> **The practical trap:** if you store vectors with cosine and query with Euclidean, your results are silently wrong — not an error, just worse answers. Match the metric your embedding model was trained with.

## 2.4 Static vs contextual embeddings — the important split

This is the distinction that separates 2013-era embeddings from modern ones.

**Static (Word2Vec, GloVe, FastText):** one fixed vector per word, forever. `"bank"` has a single embedding, an average of every sense of the word.

```
"I sat on the river bank"      --\
                                  >--  same vector for "bank"
"I deposited cash at the bank" --/
```

**Contextual (BERT and every transformer since):** the vector for a word depends on the sentence it's in. The same word gets different embeddings in different contexts.

```
"I sat on the river bank"       -> bank = [0.2, -0.7, ...]   (near: shore, water)
"I deposited cash at the bank"  -> bank = [0.8,  0.1, ...]   (near: money, branch)
```

That's exactly what the "B" in BERT — *bidirectional* — buys you: the representation of each token is computed from words on **both** sides.

**How each was trained:**

| Model | Trained by | Year |
|---|---|---|
| **Word2Vec** | Predicting a word from its neighbours (CBOW) or neighbours from the word (Skip-Gram) | 2013 |
| **GloVe** | Factorising a global word co-occurrence matrix | 2014 |
| **BERT** | Masking 15% of tokens and predicting them, with full bidirectional context | 2018 |
| **Modern embedding models** | Contrastive learning on (query, relevant-doc) pairs — pull matches together, push non-matches apart | 2022+ |

That last row matters and the course notes don't mention it: today's retrieval embeddings are **not** trained on "predict the masked word." They're trained **contrastively**, specifically to make queries land near their correct documents. That is why a purpose-built embedding model beats "take the mean of BERT's last layer" by a very large margin.

## 2.5 The families of embeddings

| Type | What it embeds | Examples | Typical use |
|---|---|---|---|
| **Word** | single words, static | Word2Vec, GloVe | Legacy, teaching, feature engineering |
| **Sentence / document** | whole passages, contextual | BGE, E5, Qwen3-Embedding, `text-embedding-3` | **RAG, semantic search** |
| **Code** | source code | Jina-code, Voyage-code | Code search |
| **Image / multimodal** | text and images in *one* shared space | CLIP, SigLIP | Text-to-image search, zero-shot classification |
| **Audio** | speech waveforms | Wav2Vec 2.0, Whisper encoder | Transcription, speaker ID |

**Why CLIP is worth understanding:** it puts text and images in the *same* space. So the vector for the string `"a dog on a beach"` sits near the vector for an actual photo of a dog on a beach. That single property is what makes text-to-image search and zero-shot image classification work — no classifier is trained, you just embed the candidate labels and pick the nearest one.

## 2.6 Bi-encoder vs cross-encoder

You will hit this the moment you build retrieval, and it is the concept most people get wrong.

```
BI-ENCODER (the embedding model)
  query    -> [encoder] -> vector  \
                                     cosine similarity -> score
  document -> [encoder] -> vector  /

  Documents are encoded ONCE, offline, and stored.
  A query compares against millions of vectors in milliseconds.
  Fast. Slightly less accurate.

CROSS-ENCODER (the reranker)
  (query + document together) -> [encoder] -> a single score

  Nothing can be precomputed: every pair needs a fresh forward pass.
  Far more accurate (it sees both texts jointly, with attention across them).
  Far too slow to run over a whole corpus.
```

**So the standard pipeline is both:** bi-encoder retrieves the top 100 out of a million (fast), cross-encoder reranks those 100 down to the top 5 (accurate). Embeddings are the bi-encoder half. Reranking is Week 3.

## 2.7 The practical rules

1. **Use the same model on both sides.** Embed your documents and your queries with the *same* model. Different models produce incompatible coordinate systems — the "maps" don't line up and results are garbage.
2. **Changing the embedding model means re-embedding everything.** There is no migration path. Budget for it.
3. **Normalise, then use dot product.** Most models output normalised vectors; then dot product = cosine and is faster.
4. **Chunk sensibly.** Every model has a max input length. Text beyond it is silently truncated — a 2000-token document embedded by a 512-token model quietly loses three quarters of itself.
5. **Dimensions are a cost knob, not a quality knob past a point.** 768 vs 1536 is often a small accuracy difference and a 2× storage difference.
6. **Matryoshka embeddings let you truncate.** Models trained with Matryoshka Representation Learning pack the most important information into the *first* dimensions, so you can cut a 3072-dim vector down to 256 dims by slicing it — with minimal quality loss and a huge storage saving. This is now standard in OpenAI's `text-embedding-3` family and several open models.
7. **Instruction-prefixed models exist.** Some models (E5, BGE, Qwen3-Embedding) want `"query: "` / `"passage: "` prefixes. Forgetting them costs measurable accuracy. Read the model card.

## 2.8 Choosing an embedding model in 2026

The course note asks the right question — *"for finance data, should the embedding model be finance-trained?"* — and gives the right answer: **better if, not must be.** A strong general model handles finance decently because it saw finance text; a domain model wins on jargon ("bull" = rising market, not the animal).

Here's the current landscape to choose from:

| Model | Type | Dims | Notes |
|---|---|---|---|
| **Qwen3-Embedding-8B** | Open | up to 4096 | Top of the MTEB multilingual leaderboard; runs in ~5 GB at 4-bit |
| **NV-Embed-v2** | Open (licence-restricted) | 4096 | Fine-tuned from Llama-3.1-8B; very strong English retrieval |
| **BGE-M3** | Open, Apache-2.0 | 1024 | The production default: multilingual, and produces dense **and** sparse vectors from one model — ideal for hybrid search |
| **EmbeddingGemma** | Open | 768 (Matryoshka) | Small, on-device friendly |
| **text-embedding-3-large** | Closed (OpenAI) | 3072, Matryoshka | Zero ops, pay per token |
| **voyage-3 / Cohere Embed** | Closed | varies | Strong retrieval-tuned commercial options |

**The decision rule:**

1. Prototyping or low volume → a hosted API model. Zero ops.
2. Production, self-hosted, multilingual → **BGE-M3**, and use its sparse output for hybrid search.
3. Maximum accuracy and you have a GPU → Qwen3-Embedding or NV-Embed-v2.
4. Specialised jargon domain and enough labelled pairs → fine-tune a small model contrastively. This is a genuinely underused, cheap win.

**And the caveat everyone should repeat:** [MTEB](https://huggingface.co/spaces/mteb/leaderboard) rankings are a *starting point*, not an answer. Build a 50-query evaluation set from your own data and measure. Leaderboard position frequently does not survive contact with a specific corpus.

## 2.9 Code

```python
# --- Option A: local, open, free ---
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")
vecs = model.encode(
    ["My payment failed twice", "The card was declined", "Where is my order?"],
    normalize_embeddings=True,          # so dot product == cosine
)
print(vecs.shape)                        # (3, 1024)

# similarity between the first two
import numpy as np
print(float(np.dot(vecs[0], vecs[1])))   # ~0.8 -> semantically close

# --- Option B: hosted API ---
from openai import OpenAI
client = OpenAI()
r = client.embeddings.create(
    model="text-embedding-3-large",
    input="My payment failed twice",
    dimensions=256,                      # Matryoshka truncation
)
print(len(r.data[0].embedding))          # 256
```

## ✅ Key takeaways — embeddings

1. An embedding is coordinates for meaning. Similar meaning → similar coordinates.
2. Dense beats one-hot on both size and semantics; that's the whole reason they exist.
3. Cosine is the default metric; on normalised vectors it's the same as dot product.
4. Static (Word2Vec) gives one vector per word; contextual (BERT+) gives one per *usage*.
5. Modern retrieval embeddings are trained **contrastively**, not by masked-word prediction.
6. Same model for documents and queries — always. Changing it means re-embedding everything.
7. Bi-encoder retrieves fast; cross-encoder reranks accurately. Real pipelines use both.
8. Pick from MTEB, then verify on your own data. Domain fine-tuning is a cheap, underused win.

---

# Part 3 — Hugging Face

## 3.1 What it is

**One line:** Hugging Face is the GitHub for AI — where models, datasets and demos are published, downloaded and discussed, plus the open-source Python libraries that make them usable.

It's three things at once: a **catalogue** (download ready-made models), a **social network** (follow, like, discuss), and a **toolbox** (the libraries). Scale as of now: 2M+ models, 500k+ datasets, 1M+ Spaces, 50,000+ organisations including Google, Meta, Microsoft and Amazon.

## 3.2 The three pillars

| Pillar | What it is | Analogy |
|---|---|---|
| 🧠 **Models** | Ready-made AI "brains" you download and run | Apps in an app store |
| 📊 **Datasets** | Collections of data for training and testing | The textbooks the AI learns from |
| 🚀 **Spaces** | Live AI apps running in the browser | YouTube, but for AI demos |

Everything on the site is a **Git repository** under the hood — versioned, forkable, with a README (the "model card"). That's not trivia: it's why you can pin a specific revision, and why `git lfs` shows up when you clone a model.

## 3.3 Reading a model page

Take `openai-community/gpt2`. The name is always **`owner/model-name`**.

| Element | What it tells you |
|---|---|
| **Model card** tab | The README — what it is, how to use it, its limits and biases |
| **Files** tab | The actual weights + config you'd download |
| **Community** tab | Discussions and bug reports |
| **Downloads last month** | The strongest single trust signal on the site |
| **❤️ Likes** | Popularity, weakly correlated with quality |
| **Pipeline tag** (e.g. `Text Generation`) | The *task* it does |
| **Library tags** (`Transformers`, `PyTorch`, `Safetensors`) | How to load it |
| **License** (`mit`, `apache-2.0`, `llama3.2`) | Whether you can legally use it commercially — **read this** |
| **Model tree** | Relationships: Finetunes, Adapters, Merges, Quantizations |

**The Model tree is the most underrated part of the page.** Landing on a base model and finding a `Quantizations` entry means somebody already produced the 4-bit GGUF you were about to make yourself. Finding an `Adapters` entry means somebody already LoRA-tuned it for your task.

## 3.4 The library stack — and which one does what

This is the part worth memorising, because every fine-tuning notebook is just these libraries composed together.

| Library | One-line job |
|---|---|
| **transformers** ⭐ | Load and run almost any model. The flagship. |
| **datasets** | Download, stream and preprocess data |
| **tokenizers** | Fast text ↔ token conversion |
| **peft** | Parameter-Efficient Fine-Tuning — LoRA, QLoRA, DoRA and friends |
| **trl** | The training loops for post-training: `SFTTrainer`, `DPOTrainer`, `GRPOTrainer`, `KTOTrainer`, `PPOTrainer` |
| **accelerate** | Run the same training code on 1 GPU or 8 without changes |
| **bitsandbytes** | 4-bit / 8-bit quantized loading (the thing that makes QLoRA possible) |
| **safetensors** | The safe, fast weight file format |
| **diffusers** | The image/video/audio *generation* branch (Stable Diffusion etc.) |
| **evaluate** | Metrics (accuracy, F1, BLEU...) |
| **TGI / vLLM** | Industrial-strength serving at scale |
| **transformers.js** | Run models in the browser, in JavaScript |
| **smolagents** | Build tool-using agents |

**How they compose in a real fine-tune:**

```
datasets      ->  load and format the training data
transformers  ->  load the base model (+ bitsandbytes for 4-bit)
peft          ->  attach LoRA adapters
trl           ->  run SFTTrainer / DPOTrainer
accelerate    ->  spread it across available GPUs
safetensors   ->  save the result
hub           ->  push it back to Hugging Face
```

That single flow is literally what both Week 2 fine-tuning notebooks do.

## 3.5 Three ways to run a model, from easiest to most controlled

```python
# 1. pipeline() - one line, sensible defaults, zero knobs
from transformers import pipeline
clf = pipeline("sentiment-analysis")
clf("I love this")                    # [{'label': 'POSITIVE', 'score': 0.9998}]

# 2. Auto classes - explicit model + tokenizer, full control
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tok   = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
model = AutoModelForSequenceClassification.from_pretrained(
            "microsoft/deberta-v3-base", num_labels=10)

# 3. Manual forward pass - when you need the raw tensors (e.g. embeddings)
import torch
inputs = tok("I love this", return_tensors="pt")
with torch.no_grad():
    out = model(**inputs)
print(out.logits)
```

**When to use which:** `pipeline` for demos and quick checks; Auto classes for anything you train or ship; manual when you need hidden states rather than predictions.

## 3.6 The files inside a model repo

| File | What it is |
|---|---|
| `config.json` | Architecture: layers, hidden size, attention heads. Defines the *shape*. |
| `model.safetensors` | The weights. Safetensors is preferred over `.bin` because loading a `.bin` (a pickle) can execute arbitrary code. |
| `tokenizer.json` / `tokenizer_config.json` | The tokenizer and its chat template |
| `generation_config.json` | Default decoding settings (temperature, max tokens) |
| `*.gguf` | A *quantized* single-file build for llama.cpp / Ollama / LM Studio |
| `adapter_model.safetensors` | A **LoRA adapter** — a few MB, useless without the base model |

That last row is the payoff of PEFT: you publish a 30 MB adapter, not a 6 GB model.

## 3.7 Where the compute happens

| Option | What it is | When |
|---|---|---|
| **Inference Providers** | One unified API into models hosted by many providers | Quick access, no hosting |
| **Inference Endpoints** | Your own dedicated model server on cloud hardware | Production, predictable load |
| **Spaces hardware** | Upgrade a Space to a GPU (from ~$0.60/hr) | Demos |
| **Local** (Ollama, LM Studio, llama.cpp, vLLM, SGLang) | Runs on your machine | Privacy, offline, no per-token cost |
| **Kaggle / Colab free GPU** | Free T4/P100 notebooks | Exactly what the Week 2 notebooks use |

## 3.8 Accounts, tokens and gated models

- **Access token** — a secret key proving your code is you. `huggingface-cli login`, or `HF_TOKEN` env var. **Never commit it.**
- **Gated model** — you must accept a licence on the website before downloading (Llama and Gemma families do this). Your token then carries the acceptance.
- **Organization** — a shared team account holding many repos.
- **Free tier** — unlimited public models, datasets and Spaces. The core genuinely is free.

## 3.9 What's changed recently

- **`trl` is now the centre of gravity for post-training.** It ships `SFTTrainer`, `DPOTrainer`, `GRPOTrainer`, `KTOTrainer`, `ORPOTrainer` and more, all with the same `quantization_config` and PEFT integration. See [TRL docs](https://huggingface.co/docs/trl/en/peft_integration).
- **`DPOTrainer` + PEFT no longer loads a second reference model.** It recovers reference behaviour by *temporarily disabling the adapter* — roughly halving the memory a DPO run used to need.
- **AutoGPTQ is archived**; the maintained path is **GPTQModel**. ExLlamaV2 is archived in favour of ExLlamaV3/EXL3.
- **Safetensors is effectively mandatory**; `.bin` pickles are legacy and a security risk.
- **ModernBERT landed in `transformers`** as a slot-in BERT replacement (see Part 4).

## ✅ Key takeaways — Hugging Face

1. Models, Datasets, Spaces — every one of them is a Git repo.
2. Downloads-last-month and the licence are the two things to check before trusting a model.
3. The Model tree often already has the quantization or adapter you were about to build.
4. `transformers` + `datasets` + `peft` + `trl` + `bitsandbytes` **is** the fine-tuning stack.
5. `pipeline()` to explore, Auto classes to build.
6. A LoRA adapter is a few MB and needs its base model; a merged model is the full size.

---

# Part 4 — BERT and the Encoder Family

## 4.1 The mental model that makes everything click

Transformers come in three shapes, and knowing which is which answers most "can this model do X?" questions instantly.

```
ENCODER-ONLY  (BERT, RoBERTa, DeBERTa, ModernBERT)
  Reads the whole text at once, both directions.
  Outputs: a rich representation of the input.
  Good at: classification, NER, embeddings, reranking.
  Cannot: generate fluent text.

DECODER-ONLY  (GPT, Llama, Mistral, Qwen, Claude)
  Reads left-to-right, predicting the next token.
  Outputs: more text.
  Good at: generation, chat, reasoning, everything open-ended.

ENCODER-DECODER  (T5, BART, Whisper)
  Encoder reads the input, decoder writes the output.
  Good at: translation, summarisation, speech-to-text.
```

**The one-line version: encoders *understand*, decoders *write*.**

This is why the ticket-tagger notebook uses DeBERTa and the support-bot notebook uses Llama. Different jobs, different architecture.

## 4.2 What BERT is and how it was trained

**BERT = Bidirectional Encoder Representations from Transformers** (Google, 2018).

Its trick is in the "B". Earlier models read left-to-right, so when processing `"bank"` in `"I sat on the river bank"` they hadn't seen "river" yet if it came later. BERT sees the **entire** sentence at once — every token's representation is built from context on both sides.

**How it learned, with no labels:**

1. **Masked Language Modelling (MLM)** — hide 15% of tokens at random and make the model predict them.
   ```
   Input:  "The cat sat on the [MASK]."
   Target: "mat"
   ```
   To fill that blank you need grammar, world knowledge, and both-sides context. That single objective is where BERT's understanding comes from.

2. **Next Sentence Prediction (NSP)** — given two sentences, predict whether B actually followed A. *(Later research showed NSP contributes little; RoBERTa dropped it and got better results.)*

**The `[CLS]` token.** BERT prepends a special `[CLS]` token to every input. Its final-layer vector is trained to summarise the whole sequence, so classification heads read from it. That's the mechanism behind "BERT gives you a sentence embedding" — though for *retrieval*, purpose-trained sentence-embedding models beat raw `[CLS]` by a wide margin.

## 4.3 Why fine-tuning BERT is so cheap

A pretrained BERT already understands language. To specialise it you bolt a small **head** on top and train:

```
[CLS] my payment failed twice [SEP]
   |
   v
+---------------------------+
|   BERT encoder (110M)     |   <- pretrained, understands language
+---------------------------+
   |
   v  [CLS] vector (768 numbers)
+---------------------------+
|  Linear head (768 -> 10)  |   <- brand new, random weights
+---------------------------+
   |
   v
10 department scores -> softmax -> "Billing and Payments"
```

Because the encoder already did the hard part, a few thousand labelled examples and a handful of epochs are enough. That's a **full** fine-tune of a 110–400M model — completely affordable on a free Kaggle GPU, which is exactly why the ticket-tagger notebook doesn't need LoRA.

## 4.4 The three simple tasks, with code

### Task 1 — Text classification (sentiment)

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")   # defaults to DistilBERT
print(classifier("I love using BERT for NLP tasks!"))
# [{'label': 'POSITIVE', 'score': 0.9998769}]
```

### Task 2 — Named Entity Recognition

```python
ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

for e in ner("India lay down the gauntlet to Australia with 295-run thrashing."):
    print(e)
# {'entity': 'I-LOC', 'score': 0.9998, 'word': 'India',     'start': 0,  'end': 5}
# {'entity': 'I-LOC', 'score': 0.9998, 'word': 'Australia', 'start': 31, 'end': 40}
```

Use `aggregation_strategy="simple"` to merge sub-word pieces back into whole entities — otherwise a name like "Bengaluru" can come back as three fragments.

### Task 3 — Extractive question answering

```python
qa = pipeline("question-answering")            # add device="cuda" for GPU

print(qa({
    "context":  "India won the first test against Australia",
    "question": "Who defeated Australia in the first test?",
}))
# {'score': 0.59, 'start': 0, 'end': 42, 'answer': 'India won the first test against Australia'}
```

**Note the word "extractive".** BERT-style QA can only return a **span copied from the context** — it physically cannot compose a new sentence. If the answer isn't literally present, it can't produce it. Generative QA (a decoder model with RAG) is the other approach, and this is the clearest possible illustration of the encoder/decoder divide.

### Fine-tuning your own (what the ticket-tagger does)

```python
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer)

name = "microsoft/deberta-v3-base"
tok   = AutoTokenizer.from_pretrained(name)
model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=10)

def tokenize(b):
    return tok(b["text"], truncation=True, padding="max_length", max_length=256)

ds = hf_dataset.map(tokenize, batched=True)

trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="./out", num_train_epochs=10,
                           per_device_train_batch_size=16,
                           learning_rate=2e-5, eval_strategy="epoch"),
    train_dataset=ds["train"], eval_dataset=ds["test"],
)
trainer.train()
```

`2e-5` is the canonical encoder fine-tuning learning rate — note it is **10× smaller** than the `2e-4` used for LoRA in Part 7. Full fine-tuning moves every weight, so it has to move them gently.

## 4.5 The family tree

| Model | Params | What it changed |
|---|---|---|
| **BERT-base** | 110M | The original: bidirectional encoder, MLM + NSP |
| **BERT-large** | 340M | Bigger |
| **RoBERTa** | 125M / 355M | Dropped NSP, trained longer on more data. Better BERT. |
| **DistilBERT** | 66M | Distilled: 40% smaller, 60% faster, ~97% of the quality |
| **ALBERT** | 12M+ | Shared parameters across layers — tiny, slower per step |
| **DeBERTa-v3** | 184M | Disentangled attention + better pretraining. **Long the best-in-class classifier** — which is why the ticket-tagger uses it |
| **ModernBERT** | 149M / 395M | **2024/25 rewrite.** 8192-token context (vs 512), trained on 2T tokens of text *and code*, much faster |

**ModernBERT is the update that matters here.** The course notes predate it. It's a genuine slot-in replacement — same `AutoModelForSequenceClassification` API, same recipes — with three real wins: **16× the context length**, competitive-or-better accuracy than DeBERTa-v3-large at a smaller size, and substantially faster inference. For a *new* classification project in 2026, start with ModernBERT.

```python
model = AutoModelForSequenceClassification.from_pretrained(
    "answerdotai/ModernBERT-base", num_labels=10)   # the only line that changes
```

See [Finally, a Replacement for BERT — Answer.AI](https://www.answer.ai/posts/2024-12-19-modernbert.html).

## 4.6 When to use a 150M encoder instead of a 7B LLM

This is the practical payoff of the whole section, and it's a decision people get wrong expensively.

| | Fine-tuned encoder (DeBERTa/ModernBERT) | LLM via API |
|---|---|---|
| Latency | 5–20 ms | 300–2000 ms |
| Cost at 1M classifications | Cents (your own CPU/GPU) | Tens to hundreds of dollars |
| Accuracy on a fixed label set | Usually **higher** | Good, but drifts |
| Needs labelled data | Yes, ~1–5k rows | No |
| Handles a new label | Retrain | Edit the prompt |
| Explains itself | No | Yes |

**The rule:** a **fixed** label set, high volume, latency-sensitive → fine-tune an encoder. A **changing** label set, low volume, or you need reasoning and explanation → prompt an LLM.

**And the best of both:** use an LLM to *label* 3,000 examples cheaply, have a human verify them, then train a tiny encoder on that. You get LLM-quality labels at encoder cost and speed. This pattern is everywhere in production and rarely taught.

## ✅ Key takeaways — BERT

1. Encoders understand, decoders write. That single split explains most architecture choices.
2. BERT learned from masked-word prediction with full bidirectional context — no labels needed.
3. `[CLS]` carries the sentence-level summary that classification heads read.
4. Full fine-tuning a 110–400M encoder is cheap — no LoRA required.
5. BERT-style QA is **extractive**: it copies a span, it cannot compose.
6. DeBERTa-v3 was the classification king; **ModernBERT** is the 2026 default (8192 context, faster).
7. For fixed-label, high-volume classification, a small encoder beats an LLM on cost, latency *and* accuracy.

---

# Part 5 — Open-Source vs Closed-Source Models

## 5.1 The definitions — and the correction almost everyone needs

The course notes define it cleanly:

- **Open-source models** — freely accessible; anyone can view, modify and distribute. *Mistral, LLaMA, Stable Diffusion.*
- **Closed-source models** — proprietary; accessed through an API. *GPT-4, Claude, Gemini.*

**The correction worth making: most "open-source" LLMs are actually open-*weights*, not open-source.**

| Term | What you get |
|---|---|
| **Open weights** | The trained numbers. You can download, run, fine-tune, quantize. You do **not** get the training data or the training code. |
| **Open source (strict)** | Weights **plus** training data, training code and recipe — enough to reproduce the model from scratch. |

Llama, Mistral, Qwen and DeepSeek are open-**weights**. Genuinely open-source-all-the-way-down models (OLMo, Pythia) exist but are rarer. In practice this distinction costs you nothing for *using* a model, and matters enormously for auditing, reproducing and certain compliance regimes.

**Also: "open" is not the same as "unrestricted."** Llama's licence forbids some uses and, in the Llama 4 generation, withholds multimodal rights from EU-based developers. Qwen's largest models sit under a conditional licence. Always read the licence file, not the marketing.

## 5.2 The licence spectrum

```
  MOST FREE                                                    LEAST FREE
      |                                                             |
  MIT / Apache-2.0 ---- Custom permissive ---- Conditional ---- API only
      |                       |                     |               |
  DeepSeek V4 (MIT)      Llama (community)    Qwen Max-class    GPT / Claude
  Mistral 7B (Apache)    Gemma                Kimi K-series     Gemini
  Qwen 27B (Apache)
```

| Licence | Commercial use | Redistribute | Catch |
|---|---|---|---|
| **MIT / Apache-2.0** | ✅ | ✅ | None meaningful |
| **Llama Community** | ✅ below 700M MAU | ✅ with attribution | Naming rules, use policy, regional carve-outs |
| **Gemma** | ✅ | ✅ | Use-policy restrictions |
| **Conditional / MaaS-restricted** | ✅ mostly | ✅ | Extra terms if you resell it as a service |
| **Proprietary API** | ✅ per ToS | ❌ | No weights, no self-hosting, no fine-tuning beyond what they offer |

## 5.3 The cost model — where the real decision lives

This is the part the course notes gesture at ("free but hosting costs") and it deserves actual numbers, because the shape of the cost is completely different.

**Closed (API): you pay per token. Cost scales linearly with usage, forever. Zero fixed cost.**
**Open (self-hosted): you pay per GPU-hour. Cost is fixed whether you serve 10 requests or 10 million.**

A worked break-even:

```
Assume:  1,000 tokens in + 500 tokens out per request

CLOSED API, mid-tier model  ~ $0.001 per request
OPEN, 8B model on one A10G  ~ $1.00/hr, handles ~5 req/s with batching
                            = 18,000 req/hr = $0.000056 per request

Break-even: about 1,000 requests/hour, sustained.

  Below that -> the API is cheaper AND has no ops burden.
  Above that -> self-hosting wins, and the gap widens fast.
```

**But the honest total cost of self-hosting includes** the GPU idle time (you pay at 3am too), an engineer to run it, evaluation and monitoring you'd otherwise get free, and the upgrade treadmill — a better model ships every ~3 months and you have to redo the work.

**The cost argument that actually wins** is rarely raw price. It's **privacy** (data never leaves your VPC), **determinism** (the model doesn't silently change under you), and **latency floor** (no network hop, and you can quantize aggressively).

## 5.4 Which should you choose?

| Your situation | Choose | Why |
|---|---|---|
| Prototyping, unclear requirements | **Closed API** | Fastest iteration, no infra |
| Highest reasoning quality needed | **Closed frontier** | Still ahead on the hardest tasks |
| Low/medium volume | **Closed API** | Below break-even |
| Regulated data (health, finance, legal) | **Open, self-hosted** | Data never leaves your network |
| Very high volume, stable workload | **Open, self-hosted** | Unit economics flip decisively |
| Need to fine-tune deeply | **Open** | You need the weights |
| Need offline / edge / air-gapped | **Open** | No network |
| Small team, no ML ops | **Closed API** | Self-hosting is a real job |

**The mature answer is both.** Route the easy 80% of traffic to a cheap self-hosted model and escalate the hard 20% to a frontier API. This is standard practice now, not a clever trick.

## 5.5 The 2026 landscape

The picture has shifted substantially since the course notes were written:

- **The capability gap narrowed from ~2 years to roughly 6–12 months.** Open-weight models now match frontier models from a year prior on most benchmarks.
- **The open-weight top tier is now largely Chinese labs** — DeepSeek, Zhipu (GLM), Moonshot (Kimi), Alibaba (Qwen), MiniMax — with Meta and Mistral further down the live rankings than the course notes imply.
- **OpenAI released open-weight models (`gpt-oss`)**, which would have been unthinkable when these notes were written. "Closed lab" no longer means "no weights ever."
- **Where the gap persists:** complex multi-step agentic work, the hardest reasoning benchmarks, and long-horizon reliability. Frontier closed models still lead there.
- **Where open has effectively won:** classification, extraction, summarisation, RAG generation, structured output, and anything privacy-constrained. For these, a well-chosen 7–30B open model is usually indistinguishable in output and dramatically cheaper.
- **A 27–32B dense model now runs on a single consumer GPU** and scores in the high 70s on SWE-bench-class benchmarks. That is the single most consequential fact for anyone deciding whether to self-host.

See [Best Open-Weight LLMs 2026](https://wavect.io/blog/open-weight-llm-comparison-2026/) and the [Open LLM Leaderboard](https://www.vellum.ai/open-llm-leaderboard).

## ✅ Key takeaways — open vs closed

1. Most "open source" LLMs are open-**weights**: no training data, no training code.
2. Read the licence. "Open" does not imply "unrestricted."
3. API cost is per-token and linear; self-hosting is per-hour and fixed. Break-even is around ~1,000 sustained requests/hour.
4. The real reasons to self-host are privacy, determinism and latency — not usually price.
5. The capability gap is now 6–12 months, and closed still leads on hard agentic reasoning.
6. Production systems increasingly use both: cheap open model by default, frontier API for escalation.

---

# Part 6 — Quantization

## 6.1 The problem, stated as arithmetic

A model's size on disk and in memory is just:

```
memory = number of parameters x bytes per parameter
```

Every parameter is stored at some precision. Standard training precision is **FP32** — 32 bits, 4 bytes each.

```
Llama 3.2 3B  ->  3.21B params x 4 bytes = 12.8 GB   <- won't fit a free-tier T4 (16 GB) with room to work
Mistral 7B    ->  7.24B params x 4 bytes = 29.0 GB   <- needs an A100
Llama 70B     ->    70B params x 4 bytes =  280 GB   <- needs a multi-GPU node
```

**Quantization attacks the second factor.** Same parameter count, fewer bytes each.

## 6.2 The number formats

| Format | Bits | Bytes/param | 7B model | What it's for |
|---|---|---|---|---|
| **FP32** | 32 | 4 | 29.0 GB | Original training precision |
| **FP16 / BF16** | 16 | 2 | 14.5 GB | Standard inference & training today. BF16 has FP32's range with less precision — safer for training. |
| **FP8** | 8 | 1 | 7.2 GB | Native on H100+. Near-lossless, very fast. |
| **INT8** | 8 | 1 | 7.2 GB | Classic quantization. Small quality loss. |
| **INT4 / NF4** | 4 | 0.5 | 3.6 GB | The sweet spot. Noticeable but usually acceptable loss. |
| **INT3 / INT2** | 3 / 2 | 0.375 / 0.25 | 2.7 / 1.8 GB | Quality degrades sharply. Specialist use. |

**The rule of thumb everyone uses: FP16 → 4-bit is a ~4× memory cut for a few percent quality loss.** That is an extraordinary trade, and it is why quantization is not an optimisation — it is the default.

## 6.3 How quantization actually works

The course note gives the intuition: `0.0547381020` becomes `0.05`. Here is the mechanism underneath.

You can't store arbitrary floats in 4 bits — 4 bits gives you exactly **16 possible values**. So you:

1. Find the **range** of a group of weights (say, min = −0.8, max = +0.8).
2. Divide that range into 16 buckets.
3. Store each weight as a 4-bit **bucket index** (0–15).
4. Store the **scale factor** once for the whole group, so you can reconstruct approximate values later.

```
Original FP32 weights:
  [-0.73,  0.12, -0.05,  0.68,  0.31, -0.44, ...]

Range: -0.8 to +0.8, split into 16 buckets of 0.1067 each

  -0.73 -> bucket 1   -> reconstructs as -0.747   (error 0.017)
   0.12 -> bucket 8   -> reconstructs as  0.107   (error 0.013)
  -0.05 -> bucket 7   -> reconstructs as  0.000   (error 0.050)

Stored: 4 bits per weight + ONE FP16 scale per group
```

**Three refinements that make the difference between "works" and "broken":**

1. **Blockwise quantization.** Don't use one scale for the whole 7-billion-weight model — use one per block of 64 or 128 weights. A single extreme value then only ruins its own small block instead of squashing everything.

2. **Outliers are the whole problem.** LLM weight and activation distributions have rare, very large values. Naive quantization stretches the range to fit them, leaving almost no resolution for the 99.9% of weights clustered near zero. Every serious method is fundamentally an answer to the outlier problem:
   - **LLM.int8()** keeps outlier dimensions in FP16 and quantizes the rest.
   - **AWQ** notices that ~1% of weights matter disproportionately (identified by looking at *activations*) and protects those.
   - **GPTQ** quantizes layer by layer, adjusting the remaining weights to compensate for the error already introduced.

3. **NF4 (NormalFloat4) — the clever bit in QLoRA.** Neural network weights are roughly normally distributed: most sit near zero, few sit at the extremes. So instead of spacing the 16 available values *evenly*, NF4 spaces them to match a normal distribution — **more resolution where the weights actually are.**

```
Plain INT4 (evenly spaced):
  -1.0  -0.87 -0.73 -0.60 ... 0 ... 0.60  0.73  0.87  1.0
   |     |     |     |         |         |     |     |
   wasted precision out here          most weights are HERE

NF4 (normal-distribution spaced):
  -1.0    -0.7  -0.4 -0.2 -0.08 0 0.08 0.2 0.4  0.7    1.0
   |       |     |    |    |    |   |   |   |    |      |
   few points in the tails   dense resolution in the middle
```

Same 4 bits, meaningfully better accuracy. Purely a smarter choice of *which* 16 values to allow.

4. **Double quantization.** The scale factors themselves take space (one FP32 per 64 weights ≈ 0.5 bits/param). Double quantization quantizes *the scale factors*, saving roughly another 0.4 bits per parameter. That's the `bnb_4bit_use_double_quant=True` flag in the Week 2 notebook.

## 6.4 PTQ vs QAT

| | **Post-Training Quantization (PTQ)** | **Quantization-Aware Training (QAT)** |
|---|---|---|
| When | After the model is trained | During training |
| How | Convert the weights, optionally calibrate on ~128 sample inputs | Simulate quantization in the forward pass so the model learns to tolerate it |
| Cost | Minutes to hours | A full training run |
| Quality | Good; small loss | Best; recovers most of the loss |
| Used for | ~99% of LLM quantization | Edge/mobile models, extreme low-bit |

**In practice, for LLMs, you will use PTQ.** QAT requires retraining from a checkpoint you usually don't have. It matters for on-device vision and speech models where every millisecond counts.

## 6.5 The format zoo — which one, when

The course notes name AWQ and BitsAndBytes. Here is the full current picture, which is the thing most people get confused by.

| Format | Bits | Runs on | Can you train with it? | Best for |
|---|---|---|---|---|
| **bitsandbytes (NF4 / INT8)** | 4, 8 | NVIDIA GPU | ✅ **Yes — the only one** | **QLoRA fine-tuning.** On-the-fly, no pre-conversion step. |
| **GPTQ** | 3, 4, 8 | NVIDIA CUDA only | ❌ | Mature GPU inference, huge library of pre-quantized models |
| **AWQ** | 4 | GPU (vLLM, TGI) | ❌ | **Fastest GPU serving.** Activation-aware; best accuracy/speed at 4-bit |
| **GGUF** | 2–8 | **CPU, Apple Silicon, GPU** | ❌ | Laptops and local apps: llama.cpp, Ollama, LM Studio |
| **EXL3** (ExLlamaV3) | variable | NVIDIA | ❌ | Enthusiast single-GPU, very high throughput |
| **FP8 / MXFP4** | 8 / 4 | H100, Blackwell+ | partly | Native hardware support, near-lossless |
| **MLX** | 4, 8 | Apple Silicon | ✅ limited | Mac-native training and inference |

**The decision in one sentence each:**

- **Fine-tuning on a GPU?** → bitsandbytes NF4. It's the only format you can train through, which is precisely why QLoRA uses it.
- **Serving on a GPU at scale?** → AWQ with vLLM. Activation-aware scaling cut the INT4 perplexity penalty by around 74% versus naive quantization, and it beats GPTQ on reasoning at the same bit width.
- **Running on a laptop, Mac, or CPU?** → GGUF. It is the only mainstream format that isn't NVIDIA-bound.
- **Don't** use GPTQ for a MacBook, Raspberry Pi or any non-NVIDIA GPU — the kernels are CUDA-only.
- **Don't** ship NF4 to production as a serving format. It's a *training* format; AWQ or GGUF will serve faster.

**Most real teams use more than one:** GGUF for the laptop prototype, AWQ on the inference server, bitsandbytes for the fine-tune. See [LLM Quantization Guide 2026](https://www.premai.io/blog/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/).

**Reading GGUF filenames.** `Q4_K_M` is the most common tag you'll see:
- `Q4` = 4-bit
- `_K` = "K-quant", a mixed scheme that gives more bits to the layers that matter
- `_S` / `_M` / `_L` = small / medium / large variant
- `Q4_K_M` is the standard recommendation; `Q5_K_M` if you have the RAM; `Q8_0` is near-lossless and roughly half of FP16.

## 6.6 Worked before/after — the numbers you should be able to reproduce

**Llama 3.2 3B Instruct (3.21B parameters)** — the model in the Week 2 LoRA notebook:

| Precision | Bytes/param | Weights in memory | Fits a free 16 GB T4? |
|---|---|---|---|
| FP32 | 4 | **12.84 GB** | ❌ no headroom for training |
| FP16 | 2 | **6.42 GB** | ⚠️ inference yes, training no |
| INT8 | 1 | **3.21 GB** | ✅ |
| **NF4 (4-bit)** | 0.5 | **~1.61 GB** | ✅ comfortably, with room to train |

**Mistral 7B (7.24B parameters)** — the model in the DPO notebook:

| Precision | Weights in memory |
|---|---|
| FP32 | 28.96 GB |
| FP16 | 14.48 GB |
| **NF4** | **~3.62 GB** |

Add ~0.127 bits/param for the quantization constants with double quant, so real NF4 usage runs a little above these figures — around 1.7 GB and 3.7 GB respectively. **That 4-bit row is the entire reason a 7B model can be fine-tuned on a free Kaggle GPU.**

## 6.7 What you actually lose

Be honest about this, because "4-bit is basically free" is overstated:

| Task | 4-bit impact |
|---|---|
| Casual chat, summarisation | Barely detectable |
| Classification, extraction | Small |
| Long multi-step reasoning | **Noticeable** — errors compound across steps |
| Code generation | Noticeable on long functions |
| Multilingual / low-resource languages | Often the worst-hit |
| Very small models (< 3B) | Worst-hit overall — they have no redundancy to spare |

**The rule: bigger models quantize better.** A 4-bit 70B model is usually better *and* smaller than an FP16 13B model. If you must choose between "bigger model, more quantized" and "smaller model, less quantized," bigger-and-quantized usually wins.

**Always measure on your own task.** Perplexity is a weak proxy; run your actual evaluation set at both precisions.

## 6.8 Code — exactly what the notebooks do

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                      # store weights in 4 bits
    bnb_4bit_quant_type="nf4",              # NormalFloat4, not plain int4
    bnb_4bit_compute_dtype=torch.bfloat16,  # but COMPUTE in bf16
    bnb_4bit_use_double_quant=True,         # quantize the scale factors too
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
)
```

**The line worth pausing on is `bnb_4bit_compute_dtype`.** The weights are *stored* at 4 bits, but every matrix multiply **dequantizes back to bf16 on the fly**. You save memory, not compute. This is why 4-bit inference is sometimes *slower* than FP16 on a GPU that had enough memory anyway — you've added a dequantization step. Quantization buys you **fit**, and only indirectly speed (by letting you use a bigger batch, or a GPU you could otherwise not use at all).

Also note: the notebook uses `torch.float16` where `torch.bfloat16` is now the better default on any Ampere-or-newer GPU (T4 is older, so fp16 is correct there). BF16 has a wider dynamic range and is much less prone to training instability.

## ✅ Key takeaways — quantization

1. `memory = params × bytes/param`. Quantization shrinks the second factor.
2. 4 bits = 16 possible values. You store bucket indices plus a shared scale per block.
3. Outliers are the core difficulty; LLM.int8(), AWQ and GPTQ are three different answers to it.
4. NF4 spaces its 16 values like a normal distribution — more precision where weights actually sit.
5. PTQ is what you'll use. QAT means retraining.
6. bitsandbytes to **train**, AWQ to **serve on GPU**, GGUF to **run on a laptop**.
7. FP16 → 4-bit is roughly 4× smaller for a few percent quality loss. Bigger models tolerate it better.
8. Quantization saves memory, not compute — weights are dequantized for every matmul.

---

# Part 7 — Fine-Tuning

## 7.1 What fine-tuning actually does

**The naive picture is wrong.** People imagine fine-tuning as "uploading facts into the model." It isn't. It's this:

> **Fine-tuning reshapes the model's next-token probability distribution.**

You show it examples; it adjusts its weights so that the kinds of continuations in your examples become more probable, and the ones that aren't become less probable. Worked concretely, for the input `"My order is late"`:

```
BEFORE fine-tuning (general model):
  "Not"       ####################        20%   <- "Not much I can do..."
  "Sorry"     ###############             15%
  "Please"    ############                12%
  "I"         ##########                  10%
  "Orders"    ########                     8%
  ... a long, flat tail of plausible continuations

AFTER fine-tuning on 2,000 polite support transcripts:
  "Sorry"     ############################ 60%   <- now the overwhelming default
  "I"         ##########                   18%
  "Let"       ######                       10%
  "Not"       #                             2%   <- pushed down hard
  ... the tail is much thinner
```

Nothing was "added." The probabilities were **redistributed**.

**Three things this framing immediately explains, that the naive picture cannot:**

1. **Why fine-tuning is great for style/format and unreliable for facts.** You're changing *how* the model continues text, not installing a lookup table. A fact fine-tuned in once, against a background of trillions of pretraining tokens, is a faint nudge — the model will often still say something plausible and wrong.
2. **Why catastrophic forgetting happens.** Sharpening the distribution toward your data necessarily flattens it elsewhere. Train hard enough on support tickets and the model gets worse at writing Python — you didn't delete Python, you made it less probable.
3. **Why a small, clean dataset beats a large, noisy one.** Every example votes on the shape of the distribution. Contradictory examples pull in opposite directions and produce a mushy, hedging model.

## 7.2 The three axes — the structure that prevents all confusion

This is the single most valuable diagram in the week. People get tangled because they treat these as one list; they're **three independent choices**.

```
AXIS 1 - STAGE (when in the pipeline / what you teach)
  Continued Pretraining  ->  SFT  ->  Alignment
       (new domain)      (behaviour)  (preference)

AXIS 2 - METHOD (only for the alignment stage: how preference is taught)
  PPO   |   DPO   |   GRPO   |   ORPO / KTO / SimPO

AXIS 3 - MECHANISM (how the weights are physically updated)
  Full fine-tuning   vs   PEFT (LoRA / QLoRA / DoRA / ...)
```

**They compose freely.** Any stage can use any mechanism:

| A real run | Stage | Method | Mechanism |
|---|---|---|---|
| Ticket tagger notebook | SFT | — | **Full** fine-tuning (DeBERTa, 184M) |
| LoRA Llama support bot | SFT | — | **PEFT** (QLoRA, r=4) |
| DPO Mistral security bot | **Alignment** | **DPO** | **PEFT** (QLoRA, r=64) |
| Llama 3 post-training (Meta) | SFT then Alignment | DPO | Full |

**The two mistakes this diagram prevents:**

- ❌ *"First SFT, then PEFT."* No — SFT is a *stage*, PEFT is a *mechanism*. You do SFT **using** PEFT. They're on different axes.
- ❌ *"PEFT is a fourth type of fine-tuning."* No. The **types** (by goal) are Continued Pretraining, SFT, and Preference/Alignment tuning. PEFT cuts across all three.

## 7.3 Axis 1, Stage 1 — Continued Pretraining

**What it is:** more of the *original* pretraining objective (predict the next token) but on your domain's raw text — no question/answer pairs, just documents.

**When you'd do it:** your domain has vocabulary and phrasing the base model genuinely hasn't seen. Legal contracts, clinical notes, a low-resource language, an internal codebase with unusual idioms.

**Scale:** hundreds of millions to billions of tokens. This is the expensive one, and most teams never need it.

```
Input: "The plaintiff hereby stipulates that the aforementioned covenant..."
Task:  predict the next token
Goal:  make the model fluent IN THE DOMAIN, not obedient
```

After continued pretraining you still have a **base** model — fluent in legalese, but it will continue your text rather than answer your question. You still need SFT.

## 7.4 Axis 1, Stage 2 — Supervised Fine-Tuning (SFT)

**What it is:** show the model input→output pairs and train it to produce the output. Learning by imitation.

```
{"instruction": "My order is 40 minutes late.",
 "output": "I'm sorry about the delay. I've checked your order - it's 12 minutes away.
            I've also applied a 10% credit to your account."}
```

**What "teaching it to follow instructions" actually means.** A base model completes text. Ask a base model *"What is the capital of India?"* and you might get:

```
"What is the capital of India? What is the capital of France?
 What is the capital of Japan? ..."
```

— because a *list of questions* is a very plausible continuation of a question. The model **knows** Delhi. It just doesn't know that a question is a request for an answer. SFT teaches that mapping: when the text looks like a question, the high-probability continuation is an answer.

Phrase it as a completion — *"The capital of India is"* — and the base model gets it right, which proves the knowledge was there all along. **SFT installs the convention, not the fact.**

**Yes — SFT is essentially "give it the question and the answer."** Two refinements:

1. The loss is usually computed **only on the answer tokens**. You don't want the model learning to generate your prompts.
2. The pairs must be wrapped in the model's **chat template**, the exact format it expects. Getting this wrong is the most common silent failure in a fine-tuning run.

**How much data?** 500–1,000 high-quality examples is a genuinely useful SFT set. 10,000 mediocre ones is worse. Quality and consistency dominate quantity — this is one of the most reliably reproduced findings in the field.

**What SFT leaves unsolved:** it teaches the model to imitate, so it learns *a* correct answer, not *the best* answer. Every training example is treated as equally good, and there's no signal about what's merely acceptable versus excellent. That gap is what Stage 3 fixes.

## 7.5 Axis 1, Stage 3 — Alignment (preference tuning)

**What it is:** instead of one correct answer, show the model **two** answers and tell it which is better.

```
Prompt:   "My order is late and I want a refund."

CHOSEN:   "I'm really sorry. I've issued a full refund - it'll be back
           on your card in 3-5 days. I've also added a Rs.100 credit."

REJECTED: "Refunds are processed per policy section 4.2. Please submit
           form RF-11 and allow 14 business days."
```

Both are *correct*. One is much better. SFT has no way to express that; alignment does.

**The SFT → Alignment contrast, which is the core of this whole part:**

| | **SFT** | **Alignment** |
|---|---|---|
| Teaches | What to say | What to *prefer* |
| Signal | One correct answer | A comparison between two |
| Learning style | Imitation | Judgment |
| Data | (prompt, answer) | (prompt, chosen, rejected) |
| Analogy | A trainee reading the script | A trainee getting feedback on two drafts |
| Without it | Correct but tone-deaf | — |

**The food-delivery bot, all the way through:**

```
Pretrained base   -> "My order is late" -> "...and I don't know why. Orders are
                                            sometimes late. Anyway,"      [rambling]

After SFT         -> "My order is late" -> "Your order is delayed. It will
                                            arrive soon."                 [correct, cold]

After alignment   -> "My order is late" -> "I'm sorry about that! I've checked -
                                            it's 12 minutes away. I've added a
                                            10% credit for the trouble."  [correct AND good]
```

## 7.6 Axis 3 — Full fine-tuning vs PEFT

### The memory problem, in numbers

Full fine-tuning doesn't just need the weights in memory. With the Adam optimizer you need, per parameter:

```
  2 bytes   weights (bf16)
  2 bytes   gradients (bf16)
  4 bytes   FP32 master copy of the weights
  4 bytes   Adam momentum (m)
  4 bytes   Adam variance (v)
-----------
 16 bytes per parameter    + activations (batch- and length-dependent)
```

| Model | Params | Full fine-tune (approx, weights+grads+optimizer) |
|---|---|---|
| DeBERTa-v3-base | 184M | **~3 GB** ✅ free GPU |
| Llama 3.2 3B | 3.21B | **~51 GB** ❌ needs an A100 80GB |
| Mistral 7B | 7.24B | **~116 GB** ❌ needs multiple A100s |
| Llama 70B | 70B | **~1.1 TB** ❌ a cluster |

**That table is the whole reason PEFT exists.** It's also why the ticket-tagger can do a plain full fine-tune (184M → 3 GB, fine) while the Llama and Mistral notebooks cannot.

### The PEFT idea

> **Freeze the entire pretrained model. Add a tiny number of new trainable parameters. Train only those.**

Because the frozen weights need no gradients and no optimizer state, the memory cost collapses to: frozen weights (quantized, if you like) + optimizer state for the ~0.1% you're actually training.

**The sticky-notes analogy:** full fine-tuning is rewriting the whole textbook. PEFT is leaving sticky notes on the pages that need changing. The book is unchanged; peel off the notes and you have the original back.

### The relationship, once and for all

```
Full Fine-tuning  -> update ALL weights (heavy, expensive)
        |
   PEFT (family)   -> update only a TINY subset (efficient)
        |
   LoRA (a PEFT method) -> add small trainable adapters, freeze the rest
        |
   QLoRA (LoRA + quantization) -> same, but 4-bit compress the base too -> even lighter
```

| | Full FT | LoRA | QLoRA |
|---|---|---|---|
| Weights updated | 100% | ~0.03–3% | ~0.03–3% |
| Base model | trainable, bf16 | frozen, bf16 | **frozen, 4-bit** |
| 7B memory | ~116 GB | ~20 GB | **~7 GB** |
| Output artifact | full model (14 GB) | adapter (10–300 MB) | adapter (10–300 MB) |
| Reversible | ❌ | ✅ detach the adapter | ✅ |
| Quality ceiling | highest | very close | very close |

## 7.7 LoRA, explained properly

**LoRA = Low-Rank Adaptation.** Here's what "low-rank" means, without hand-waving.

### The insight

When you fine-tune, you change every weight matrix `W` by some amount `ΔW`:

```
W_new = W + ΔW
```

For a 4096×4096 attention matrix, `ΔW` has **16.8 million** numbers. But the LoRA paper's observation is that this update has **low intrinsic rank** — the actual change is far simpler than 16.8M independent numbers. It's mostly a few directions repeated.

So: don't store `ΔW`. **Factorise** it into two skinny matrices:

```
ΔW  =  B x A

where A is (r x 4096)  and  B is (4096 x r),  with r small (say 8)

  4096 x 4096  =  4096 x 8   @   8 x 4096
  [         ]     [   ]          [        ]
  [         ]     [ B ]     @    [   A    ]
  [  ΔW     ]  =  [   ]          [        ]
  [16.8M    ]     [32,768]       [ 32,768 ]
   numbers         numbers        numbers

  16,777,216  ->  65,536 numbers.  256x fewer.
```

At inference, the forward pass becomes:

```
output = W·x  +  (alpha / r) · B·A·x
         ^^^^     ^^^^^^^^^^^^^^^^^^
      frozen          the adapter
```

`A` is initialised randomly, `B` is initialised to **zeros** — so at step 0 the adapter contributes exactly nothing and the model is bit-identical to the base. Training moves it from there.

### The four parameters that matter

| Parameter | What it controls | Plain meaning |
|---|---|---|
| **`r` (rank)** | Size/capacity of the adapter | *How much room the model has to learn something new.* Higher = more capacity, more memory, more overfit risk. |
| **`lora_alpha`** | Scaling of the adapter's contribution | *How loudly the adapter speaks.* Effective strength is `alpha / r`. |
| **`lora_dropout`** | Regularisation on the adapter | *How much it's forced to not memorise.* |
| **`target_modules`** | Which layers get adapters | *Where the sticky notes go.* |

**Practical guidance for each, with the current consensus:**

**`r` — start at 8 or 16.**
- `r = 4–8`: style, tone, output format. Small behavioural nudges.
- `r = 16–32`: the standard range for task learning. Most projects live here.
- `r = 64–128`: substantial new behaviour, or a large/diverse dataset.
- Above 128 is almost always wasteful — you're paying for capacity you can't fill with your data.

**`lora_alpha` — set it relative to `r`, not absolutely.** The common convention is `alpha = 2 × r`. For small ranks (`r = 8`), `alpha = r` often behaves better, since `alpha = 2r` can make updates too aggressive. Either way: **treat `alpha/r` as the single knob**, and start at 1–2. There's also **rsLoRA** (`use_rslora=True`), which scales by `alpha / sqrt(r)` instead of `alpha / r` — it makes high ranks behave much better and is worth enabling whenever `r > 32`.

**`lora_dropout` — 0.05–0.1 typically; 0 for large datasets.** The Week 2 notebook's `0.2` is on the high side, which is a defensible choice for a small dataset.

**`target_modules` — this matters more than `r`.**
- Minimal: `["q_proj", "v_proj"]` — the original paper's setting. Cheapest.
- **Recommended default:** all attention *and* MLP projections — `["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]`. Consistently better, and the extra cost is modest.
- Never target embeddings or layer norms.
- `target_modules="all-linear"` in `peft` does the right thing automatically for most architectures.
- **Always print your model's actual module names before setting this** — they differ between architectures, and a name that doesn't match is silently ignored, so you can "train" a model where nothing is attached.

### Worked parameter counts from the actual notebooks

**Notebook 1 — Llama 3.2 3B, `r=4`, default targets (`q_proj`, `v_proj`):**

Llama 3.2 3B has 28 layers, hidden size 3072, and grouped-query attention (24 query heads, 8 KV heads), so `q_proj` is 3072→3072 and `v_proj` is 3072→1024.

```
per q_proj:  r x (in + out) = 4 x (3072 + 3072) = 24,576
per v_proj:  r x (in + out) = 4 x (3072 + 1024) = 16,384
per layer:                                        40,960
x 28 layers:                                   1,146,880

1.15M trainable / 3.21B total = 0.036%
```

**Thirty-six thousandths of one percent of the model is being trained.** That is the entire trick.

**Notebook 2 — Mistral 7B, `r=64`, all seven projections:**

```
q_proj  64 x (4096 + 4096)  =   524,288
k_proj  64 x (4096 + 1024)  =   327,680
v_proj  64 x (4096 + 1024)  =   327,680
o_proj  64 x (4096 + 4096)  =   524,288
gate    64 x (4096 + 14336) = 1,179,648
up      64 x (4096 + 14336) = 1,179,648
down    64 x (14336 + 4096) = 1,179,648
per layer:                    5,242,880
x 32 layers:                167,772,160

168M trainable / 7.24B total = 2.3%
```

Two very different configurations, and the contrast is instructive: notebook 1 nudges style with almost no capacity; notebook 2 teaches substantially new behaviour across the whole network.

### Merging, and why adapters are the point

```python
merged = model.merge_and_unload()   # folds B·A into W permanently
merged.save_pretrained("./my-model")
```

Merging removes the small inference overhead of the extra matmuls and gives you a normal model file. But **you lose the swappability**, which is often the bigger win:

- Ship **one** base model, plus N small adapters — one per customer, per task, per language.
- Hot-swap adapters at runtime (vLLM and TGI both support serving many LoRAs against one loaded base).
- Roll back by detaching, not redeploying.
- A 30 MB artifact per task instead of a 14 GB one.

⚠️ **Don't merge a LoRA that was trained on a 4-bit base back into a 4-bit model.** Dequantize to bf16 first, merge, then re-quantize — otherwise you compound quantization error into the merged weights.

## 7.8 QLoRA

**QLoRA = LoRA + a 4-bit quantized frozen base.** One idea, stacked:

```
1. Load the base model in 4-bit NF4              -> 7B goes from 14.5 GB to ~3.6 GB
2. Freeze it completely                          -> no gradients, no optimizer state
3. Attach LoRA adapters in bf16                  -> the only trainable parameters
4. Train. Gradients flow THROUGH the frozen 4-bit
   weights (dequantized on the fly) into the adapters.
```

That third arrow is the part worth understanding: the 4-bit weights are never updated, but they are dequantized during the backward pass so gradients can reach the adapters. The base is a fixed, compressed lens; only the lens cap is being reshaped.

**The three techniques QLoRA introduced:** NF4 quantization, double quantization, and **paged optimizers** (spill optimizer state to CPU RAM on a memory spike instead of OOM-ing).

**What it costs you:** a small quality drop from the 4-bit base versus plain LoRA on a bf16 base, and slower steps (dequantization on every forward pass). What it buys you is being able to run at all on one consumer GPU. For almost everyone, that trade is obviously worth it.

## 7.9 The PEFT family beyond LoRA

LoRA dominates, but it isn't the only member:

| Method | Idea | When |
|---|---|---|
| **LoRA** | Low-rank ΔW | The default. Start here. |
| **QLoRA** | LoRA + 4-bit base | When memory is the constraint. Also basically the default now. |
| **rsLoRA** | Scale by `alpha/√r` | Whenever `r > 32`. One flag, strictly better behaviour at high rank. |
| **DoRA** | Decompose the update into magnitude + direction, LoRA only the direction | Small but consistent gains over LoRA, especially at low rank. `use_dora=True`. Slower. |
| **LoRA+** | Different learning rates for A and B | Faster convergence, one extra hyperparameter |
| **IA³** | Learn per-channel scaling vectors | Even fewer parameters than LoRA; less expressive |
| **Prefix / P-tuning / Prompt tuning** | Learn "virtual tokens" prepended to the input | Historically important; largely superseded by LoRA |
| **Adapters (Houlsby)** | Insert small bottleneck layers between blocks | The original PEFT idea (2019); adds inference latency, which LoRA avoids |

**The reason LoRA won:** after merging, it adds **zero** inference latency, because `B·A` folds straight into `W`. Adapter layers can't do that — they're extra layers in the forward pass, forever.

## 7.10 Hyperparameter starting points

| Setting | Full fine-tune (encoder) | LoRA / QLoRA (decoder) |
|---|---|---|
| Learning rate | `2e-5` | **`1e-4` – `2e-4`** |
| Epochs | 3–10 | **1–3** |
| Batch size | 16–32 | 1–4 + gradient accumulation |
| Warmup | 5–10% of steps | 5–10% |
| Scheduler | linear or cosine | cosine |
| Precision | bf16 | bf16 (fp16 on T4/older) |
| `r` | — | 8–32 |
| `alpha` | — | `r` to `2r` |

**Two things to internalise:**

- **LoRA uses a ~10× higher learning rate than full fine-tuning.** Not a typo. You're training a tiny, randomly-initialised adapter from scratch, not gently nudging pretrained weights. `2e-5` on a LoRA adapter barely moves.
- **One to three epochs.** LoRA overfits fast. If your eval loss turns upward after epoch 2, that's normal — stop there. Ten epochs, which is right for an encoder classifier, will destroy a LoRA run.

**Gradient accumulation** is how you get a large effective batch on a small GPU:
```
effective_batch = per_device_batch x grad_accum_steps x num_gpus
# DPO notebook: 2 x 3 x 1 = 6
```

## 7.11 Catastrophic forgetting — and an important nuance

**Catastrophic forgetting** is when fine-tuning on your task makes the model worse at everything else. Train hard on customer support and general reasoning degrades. It follows directly from Section 7.1: sharpening one part of the distribution flattens the rest.

**How to limit it:**
- Fewer epochs and a lower learning rate. Most forgetting comes from over-training.
- **Use LoRA instead of full fine-tuning.** The paper [*LoRA Learns Less and Forgets Less*](https://arxiv.org/pdf/2405.09673) found exactly the trade-off its title states: LoRA absorbs less from the new task than full fine-tuning, but preserves far more of the base model's general ability. Its constrained capacity acts as a regulariser.
- Mix 5–10% general instruction data into your training set.
- Evaluate on a held-out *general* benchmark, not just your task — otherwise you won't notice the damage.

**The honest framing:** if you need the model to *master* a genuinely new domain, full fine-tuning gets you further. If you need it to *specialise while staying generally capable* — which is nearly always what a product needs — LoRA is the better tool, and that's a feature, not a compromise.

## 7.12 Data — the part that actually decides whether this works

Everything above is mechanics. Data is where fine-tuning runs succeed or fail.

| Question | The honest answer |
|---|---|
| How many examples? | 500–1,000 good ones for style/format. 5–10k for a substantive new task. |
| Quality vs quantity? | **Quality, decisively.** 500 consistent examples beat 5,000 inconsistent ones. |
| What makes it "good"? | Consistent format, consistent tone, correct answers, and coverage of edge cases. |
| Biggest failure mode? | **Contradictory examples.** Two near-identical prompts with differently-styled answers teach the model to hedge. |
| Can I generate it with an LLM? | Yes, and most people do — but **have a human review it**. Unreviewed synthetic data teaches the student model the teacher's quirks and mistakes. |
| Train/test split? | Always. Without held-out eval you cannot distinguish learning from memorising. |

**A cheap sanity check before you spend a GPU hour:** take 20 of your training examples and put them in a prompt as few-shot examples. If the model does well, you don't need to fine-tune. If it does badly, look hard at whether the *task* is well-defined before assuming more data will fix it.

## 7.13 Unsloth

**One line:** Unsloth is a drop-in speed layer over the Hugging Face stack — roughly 2× faster training and up to ~70% less VRAM, using custom Triton GPU kernels.

**It is a teammate, not a rival.** It doesn't replace Hugging Face; it swaps the slow internals of specific operations.

| Job | Comes from |
|---|---|
| The model weights | 🤗 Hugging Face Hub |
| Fast 4-bit loading | ⚡ Unsloth (`FastLanguageModel`) |
| Dataset | 🤗 `datasets` |
| LoRA adapters | 🤗 `peft`, patched by ⚡ Unsloth |
| Training loop (SFT/DPO) | 🤗 `trl` (`SFTTrainer`, `DPOTrainer`) |
| The speed | ⚡ Unsloth (custom Triton kernels) |

**What actually changes in your code — one swap:**

```python
# Pure Hugging Face
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("mistral-7b", ...)

# With Unsloth
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained("mistral-7b", ...)   # fast load
model = FastLanguageModel.get_peft_model(model, r=64, ...)                # fast LoRA
```

Everything after that — `trl`, `datasets`, the DPO logic — is unchanged Hugging Face.

**The car analogy 🏎️:** Hugging Face supplies the parts (engine, wheels, seats = model, trainer, dataset); Unsloth is the turbo that makes them run faster. You don't choose between them.

**The trade-off:** Unsloth supports a specific list of architectures. If yours isn't on it, you use plain HF. And the free tier is single-GPU. For a Kaggle or Colab fine-tune, it's close to free money.

## ✅ Key takeaways — fine-tuning

1. Fine-tuning **reshapes the next-token distribution**. It doesn't install facts.
2. Three independent axes: **stage** (CPT/SFT/Alignment), **method** (PPO/DPO/GRPO), **mechanism** (Full vs PEFT). Never mix them up.
3. PEFT is a mechanism, not a type of fine-tuning.
4. SFT teaches *what to say* by imitation. Alignment teaches *what to prefer* by comparison.
5. Full fine-tuning needs ~16 bytes/param with Adam — that's ~116 GB for a 7B model. That's why PEFT exists.
6. LoRA factorises ΔW into `B·A`. `r` = capacity, `alpha/r` = strength, `target_modules` = where.
7. `target_modules` matters more than `r`. Target attention **and** MLP; use `r=8–32` to start.
8. LoRA wants a ~10× higher learning rate and far fewer epochs than full fine-tuning.
9. QLoRA = LoRA on a 4-bit frozen base. Gradients flow through the frozen weights into the adapters.
10. LoRA learns less and **forgets less** — usually the right trade for a product.
11. 500 excellent examples beat 5,000 inconsistent ones. Contradictions are the top failure mode.
12. Unsloth speeds up the HF stack; it doesn't replace it.

---

# Part 8 — Optimization Methods: PPO, DPO, GRPO and the 2026 Menu

## 8.1 RLHF — the loop everything else is a variation of

**RLHF = Reinforcement Learning from Human Feedback.** It's the process that turned a raw language model into ChatGPT, and every method in this part is either an implementation of it or a shortcut around it.

```
STEP 1 - COLLECT PREFERENCES
  Show humans the same prompt answered 2-4 ways. They rank them.
  "Answer B is better than Answer A."

STEP 2 - TRAIN A REWARD MODEL
  Train a separate model to predict those human rankings.
  Now you have an automatic judge that scores any answer 0-10.

STEP 3 - OPTIMIZE THE LLM AGAINST THE JUDGE
  The LLM writes -> the reward model scores -> the LLM updates to score higher.
  Repeat millions of times, far faster than humans could ever rank.
```

**The intern analogy 🧑‍💼:** Step 1 is a manager reviewing the intern's drafts and saying which is better. Step 2 is the intern *internalising* the manager's taste, so they can self-assess. Step 3 is the intern practising thousands of drafts against their own internalised standard.

**Why a reward model at all?** Humans can't rank millions of samples. The reward model is a scalable stand-in for human judgment. It is also the source of most of RLHF's problems — see reward hacking below.

## 8.2 PPO — the coach with a leash

**PPO = Proximal Policy Optimization.** The original RLHF optimizer, used for InstructGPT and the first ChatGPT.

**The mental model:** a coach gives your model a score after every attempt, and a **leash** stops it changing too much in any single step.

```
Prompt: "My order is late."

Model says: "Not my problem."        -> reward model: 2/10
  -> PPO nudges weights AWAY from that kind of answer

Model says: "I'm sorry - let me check."  -> reward model: 9/10
  -> PPO nudges weights TOWARD that kind of answer

...repeated millions of times
```

**What "Proximal" means, and why the leash is essential.** Without a constraint, a model optimizing against a reward model discovers **degenerate maxima** — outputs that score high with the judge but are useless or bizarre. Classic reward hacking: the model learns that apologising scores well, and starts apologising six times per reply. Or it becomes extremely long-winded because the reward model mildly prefers detail.

PPO prevents this two ways:
1. **Clipping** — no single update can move the policy more than a set amount.
2. **A KL-divergence penalty** — an explicit term that punishes drifting too far from the *original* SFT model. This is the leash, and it is the load-bearing piece.

**What PPO costs you: four models in memory at once.**

```
1. The policy       - the model being trained
2. The reference    - a frozen copy of the SFT model, for the KL penalty
3. The reward model - the judge
4. The value model  - estimates expected future reward (the "critic")
```

For a 7B policy that is roughly four 7B models resident simultaneously. PPO is also notoriously sensitive to hyperparameters — small changes cause training collapse. **It works, and it is genuinely painful to run.**

## 8.3 DPO — skip the judge

**DPO = Direct Preference Optimization** ([paper](https://arxiv.org/pdf/2305.18290)). The method that displaced PPO for most open-source work.

**The insight, and it's elegant:** you don't need to train a separate reward model, because *a language model already implicitly contains one*. The paper shows that the RLHF objective can be algebraically rearranged into a **simple classification loss over preference pairs** — no reward model, no RL loop, no value network.

```
PPO:  preferences -> train reward model -> RL loop with 4 models -> aligned model
                      ^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^
                      expensive            expensive + unstable

DPO:  preferences ------------------------> simple training loop -> aligned model
                                            (2 models, looks like SFT)
```

**What training data looks like** — exactly the format in the Week 2 DPO notebook:

```python
{
  "prompt":   "What is our password policy?",
  "chosen":   "Passwords must be at least 14 characters, include mixed case,
               numbers and symbols, and rotate every 90 days.",
  "rejected": "Use a strong password."
}
```

**What the loss actually does:** raise the probability of the `chosen` response *relative to* the `rejected` one, while a `beta` term holds the model near the reference. That relative framing is the crux — the model isn't learning "chosen is right," it's learning "chosen is **better than** rejected."

**`beta` is the one hyperparameter that matters (typical: 0.1).** It is the leash, same role as PPO's KL penalty. Too low and the model drifts and degenerates; too high and it barely learns.

**And the memory win, which is recent and significant:** with PEFT, `DPOTrainer` no longer loads a separate reference model — it recovers reference behaviour by **temporarily disabling the LoRA adapter**. Two models become one, roughly halving DPO's memory footprint.

### PPO vs DPO side by side

| | **PPO** | **DPO** |
|---|---|---|
| Separate reward model | ✅ required | ❌ not needed |
| Models in memory | 4 | 2 (or 1 with PEFT) |
| Training data | prompts + a reward model | (prompt, chosen, rejected) pairs |
| Stability | fragile, hyperparameter-sensitive | stable, behaves like SFT |
| Compute | high | moderate |
| Online exploration | ✅ generates fresh samples | ❌ learns from a fixed dataset |
| Ceiling with a great reward model | **higher** | slightly lower |
| Who uses it | frontier labs with dedicated RL teams | almost everyone else |

**Why DPO won:** it's ~10× cheaper, dramatically more stable, and gets you most of the way. Llama 3's post-training used DPO. For any team that isn't a frontier lab, DPO is the default.

**Where PPO is still right:** online exploration matters when the model needs to discover behaviours *not present in your preference dataset*. DPO can only rank what you gave it; PPO can find new things. That's why PPO-family methods came back for reasoning — see GRPO.

## 8.4 GRPO — the reasoning-era method

**GRPO = Group Relative Policy Optimization.** Introduced by DeepSeek, and the method behind DeepSeek-R1's reasoning training.

**The problem it solves:** PPO's value model (the critic) is half the memory and most of the instability. Can you keep online exploration but drop the critic?

**How GRPO works:**

```
1. For one prompt, generate a GROUP of answers (say 8).
2. Score all 8 (with a reward model, or - better - a VERIFIER).
3. Compute each answer's advantage RELATIVE TO THE GROUP AVERAGE.
      "this one scored 8; the group averaged 5; so it was above average"
4. Push up the above-average answers, push down the below-average ones.
```

**The trick:** the group average *is* the baseline. That's what the value model was estimating in PPO — so you can delete it. Hence "**Group Relative**".

```
PPO:  policy + reference + reward model + VALUE MODEL   (4 models)
GRPO: policy + reference + reward/verifier              (3, and often simpler)
```

**Why this matters enormously — RLVR.** GRPO pairs naturally with **Reinforcement Learning from Verifiable Rewards**: instead of a learned reward model, use a **deterministic checker**.

- Maths problem → is the final answer correct? ✅/❌
- Code → do the unit tests pass? ✅/❌
- Structured output → does it validate against the schema? ✅/❌

A verifier **cannot be reward-hacked**, because it isn't a learned approximation of taste — it's a fact. This removes RLHF's single biggest failure mode and is why post-2025 reasoning models are trained this way.

**The limitation:** RLVR only applies where correctness is checkable. There is no verifier for "is this a kind reply to an upset customer." For subjective quality, you're back to preference methods.

## 8.5 The 2026 menu

DPO is no longer the end of the story. The current landscape:

| Method | Core idea | Data needed | Choose it when |
|---|---|---|---|
| **PPO** | RL against a learned reward model, with a KL leash | prompts + reward model | Frontier-scale, dedicated RL team, exploration matters |
| **DPO** | Preference pairs as a classification loss | (prompt, chosen, rejected) | **The default.** You have paired preferences. |
| **KTO** | Learns from **unpaired** thumbs-up / thumbs-down | (prompt, response, good?) | **You have production feedback, not curated pairs.** More sample-efficient on noisy or imbalanced data. |
| **ORPO** | Merges SFT and alignment into **one** stage | (prompt, chosen, rejected) | You want one training run instead of two |
| **SimPO** | Length-normalised reward margin, **no reference model** | (prompt, chosen, rejected) | Memory-constrained; also reduces length bias |
| **GRPO** | Group-relative advantage, no critic | prompts + verifier/reward | **Reasoning, maths, code — anything verifiable** |
| **DAPO** | GRPO with stability fixes at scale | as GRPO | Large-scale reasoning RL |

**Three things worth knowing about that table:**

- **KTO is the underrated one for real products.** Curated (chosen, rejected) pairs are expensive to produce. Thumbs-up/thumbs-down buttons produce data for free, continuously, from real users. KTO consumes exactly that, and it handles imbalance (which production feedback always has) better than DPO.
- **SimPO removes the reference model entirely** and normalises by length, which attacks DPO's well-known tendency to make responses longer. Reported gains over DPO of ~6 points on AlpacaEval 2 and ~7.5 on Arena-Hard.
- **ORPO collapses two stages into one.** Instead of SFT → DPO, one objective does both — appealing when compute is tight.

The consensus stack in 2026 is modular: **SFT** for instruction-following → **DPO/SimPO/KTO** for taste and tone → **GRPO/RLVR** for reasoning and verifiable correctness. See [Post-Training in 2026: GRPO, DAPO, RLVR & Beyond](https://llm-stats.com/blog/research/post-training-techniques-2026).

## 8.6 Choosing, in one flowchart

```
Do you need alignment at all?
  |
  +-- No, SFT output is good enough -> stop. Most projects stop here.
  |
  +-- Yes
        |
        +-- Is correctness objectively checkable (maths, code, schema)?
        |     -> GRPO + a verifier (RLVR)
        |
        +-- Do you have paired (chosen, rejected) data?
        |     -> DPO      (or SimPO if memory is tight or replies run long)
        |
        +-- Do you only have thumbs up/down from production?
        |     -> KTO
        |
        +-- Want one stage instead of SFT-then-align?
        |     -> ORPO
        |
        +-- Frontier scale, dedicated RL team, need exploration?
              -> PPO
```

## 8.7 Model types, and how they stack up

Worth pinning down because the terms get used loosely:

| Type | How it's made | Behaviour |
|---|---|---|
| **Base** | Pretraining only | Completes text. Won't reliably answer questions. |
| **Instruct / Chat** | Base + SFT + alignment | Follows instructions, answers directly |
| **Reasoning** | Instruct + RL on reasoning (GRPO/RLVR) | Thinks at length before answering; far better at maths/code/logic |
| **Embedding** | Encoder + contrastive training | Outputs vectors, not text |
| **Reranker** | Cross-encoder | Scores (query, document) pairs |
| **Multimodal** | Text model + vision/audio encoder | Handles images/audio alongside text |

```
Base  ->  Instruction-tuned  ->  Reasoning
  |             |                    |
DeepSeek-V3   DeepSeek-V3-chat    DeepSeek-R1
Qwen3-base    Qwen3-Instruct      Qwen3-Thinking
Llama-3.1     Llama-3.1-Instruct  (reasoning variants)
```

Ask each "What's 17 × 24?": the base model continues with more arithmetic questions; the instruct model answers `408` (usually right, sometimes not); the reasoning model works it out — `17 × 24 = 17 × 20 + 17 × 4 = 340 + 68 = 408` — and is reliably right.

**When to use which:** instruct models for most things (faster, cheaper). Reasoning models for maths, complex code, and multi-step planning — they cost far more tokens and latency, and on simple tasks they're just slower.

## ✅ Key takeaways — optimization methods

1. RLHF = collect preferences → train a reward model → optimize against it.
2. PPO does that with RL and a KL leash. Four models in memory, unstable, powerful.
3. DPO proves you don't need the reward model: preferences become a classification loss. ~10× cheaper, far more stable, now the default.
4. `beta` in DPO is the leash. ~0.1.
5. GRPO drops PPO's critic by using the group average as the baseline — and pairs with **verifiable** rewards, which can't be hacked.
6. KTO learns from thumbs-up/down, which is the data products actually generate.
7. SimPO drops the reference model and fixes length bias; ORPO merges SFT and alignment into one stage.
8. SFT → preference optimization → RLVR is the modular 2026 stack.
9. Most projects should stop after SFT. Alignment is for when "correct but wrong-toned" is your actual problem.

---

# Part 9 — The Three Practical Notebooks

The week's three notebooks aren't three versions of the same thing — they're deliberately one per corner of the three-axes diagram. Reading them that way is what makes them click.

| Notebook | Model | Stage | Mechanism | Method |
|---|---|---|---|---|
| **Customer-support ticket tagger** | DeBERTa-v3-base (184M, encoder) | SFT | **Full** fine-tuning | — |
| **LoRA Llama support bot** | Llama 3.2 3B Instruct (decoder) | SFT | **PEFT** (QLoRA, r=4) | — |
| **DPO Mistral security bot** | Mistral 7B Instruct (decoder) | **Alignment** | **PEFT** (QLoRA, r=64) | **DPO** |

## 9.1 Ticket tagger — full fine-tuning an encoder

**Goal:** route a support ticket to one of 10 departments.

```
load CSV -> drop NAs -> LabelEncoder (text labels -> 0..9)
  -> train/test split -> load DeBERTa-v3-base with a 10-class head
  -> tokenize -> Trainer, 10 epochs -> evaluate -> save -> predict
```

**Why this design is right:**
- It's **classification into a fixed label set**, so an encoder beats a generative LLM on cost, latency and accuracy (see 4.6).
- At 184M parameters, **full fine-tuning is affordable** — no LoRA needed. Adding LoRA here would be cargo-culting.
- **10 epochs** is correct for an encoder classifier and would be catastrophic for LoRA.
- `LabelEncoder` maps department names to integers; `label_encoder.classes_` maps them back. Keep that mapping with the model — losing it makes the model's outputs meaningless.

**What to watch out for:** a 14.5% test split is small; with 10 classes and imbalanced data, look at per-class F1, not just accuracy. And a model trained on 10 fixed queues cannot handle an 11th without retraining — that is the real cost of choosing an encoder.

## 9.2 LoRA Llama 3.2 3B — QLoRA SFT on a decoder

**Goal:** make a 3B chat model answer customer-support FAQs in the right voice.

```python
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(base_model,
            device_map="auto", quantization_config=bnb_config)

lora_config = LoraConfig(r=4, lora_alpha=8, lora_dropout=0.2,
                         task_type="CAUSAL_LM")
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()          # ~1.15M / 3.21B = 0.036%

trainer = SFTTrainer(model=model, train_dataset=dataset["train"],
    args=TrainingArguments(num_train_epochs=1, per_device_train_batch_size=1,
                           learning_rate=2e-4, warmup_steps=5, fp16=True))
trainer.train()
```

**Line by line, why each choice:**
- `load_in_4bit` + `nf4` + `double_quant` → the 3B base drops from 12.8 GB (FP32) to ~1.7 GB. **This is what makes it fit.**
- `compute_dtype=float16` → correct for a T4; on an A100 or newer, `bfloat16` is the better choice.
- `r=4, alpha=8` → `alpha/r = 2`. A small adapter: this fine-tune is teaching *tone and format*, not new capability. Appropriate for the goal.
- `dropout=0.2` → high, but defensible on a 1k-row dataset.
- `lr=2e-4` → the LoRA rate, 10× the encoder rate in notebook 1. Not a mistake.
- `epochs=1` → also right. LoRA on 1k examples overfits by epoch 2–3.
- `batch_size=1` → memory-driven. Adding `gradient_accumulation_steps=8` would give a far more stable effective batch of 8 at no extra memory cost — the single best improvement to make to this notebook.

**One improvement worth naming:** `target_modules` is left at the default, which for Llama is `["q_proj", "v_proj"]`. Adding the MLP projections (`gate_proj`, `up_proj`, `down_proj`) is the standard recommendation now and usually gives a clear quality gain for a modest memory increase.

## 9.3 DPO Mistral 7B — alignment with Unsloth

**Goal:** teach the model to *prefer* precise, complete security-policy answers over vague ones.

```python
from unsloth import PatchDPOTrainer
PatchDPOTrainer()
from trl import DPOTrainer
from unsloth import FastLanguageModel

dataset = load_dataset("Chirag4579/security-dpo-clean", split="train")
dataset = dataset.rename_column("text", "chosen")
dataset = dataset.rename_column("rejected_text", "rejected")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-instruct-v0.3-bnb-4bit",
    max_seq_length=4096, load_in_4bit=True)

model = FastLanguageModel.get_peft_model(model, r=64,
    target_modules=["q_proj","k_proj","v_proj","o_proj",
                    "gate_proj","up_proj","down_proj"])

dpo_trainer = DPOTrainer(model=model, args=TrainingArguments(
    per_device_train_batch_size=2, gradient_accumulation_steps=3,
    warmup_ratio=0.1, num_train_epochs=1, learning_rate=5e-6))
dpo_trainer.train()
```

**What's different from notebook 2, and why every difference is deliberate:**

| | LoRA notebook | DPO notebook |
|---|---|---|
| Stage | SFT | **Alignment** |
| Data | (instruction, response) | **(prompt, chosen, rejected)** |
| `r` | 4 | **64** |
| Targets | q, v | **all 7 projections** |
| Trainable | 1.15M (0.036%) | **168M (2.3%)** |
| LR | 2e-4 | **5e-6** |
| Effective batch | 1 | 2 × 3 = **6** |

- **`r=64` with all seven projections** gives ~64× more trainable parameters than notebook 2. Alignment is reshaping judgment across the whole network, not nudging tone. *(With `r=64`, enabling `use_rslora=True` would be worth trying — it stabilises high ranks.)*
- **`lr=5e-6` is 40× lower than the SFT run.** Preference optimization is delicate: too high and the model collapses into degenerate outputs that technically satisfy the objective. Low LR is the safety margin. This contrast is the most instructive number in all three notebooks.
- **`max_seq_length=4096`** because DPO must fit *prompt + chosen + rejected* — you pay for both responses.
- **`PatchDPOTrainer()` before importing DPOTrainer** — Unsloth patches `trl`'s trainer in place. Order matters.
- Loading a pre-quantized `...-bnb-4bit` checkpoint skips the quantization step at load time.

**Why this is the right method for this problem:** both a vague and a precise security answer are "correct." SFT can't express that one is better. DPO can. That's the entire justification, and it's a clean illustration of the SFT→alignment boundary.

## 9.4 What the three teach together

```
                 ENCODER                    DECODER
              (understand)                  (generate)
                    |                           |
          Ticket tagger (SFT)          LoRA bot (SFT)  ->  DPO bot (Alignment)
          full fine-tune, 184M         QLoRA r=4, 3B      QLoRA r=64, 7B
          10 epochs, lr 2e-5           1 epoch, lr 2e-4   1 epoch, lr 5e-6
                    |                           |               |
            cheapest, fastest,       teaches format       teaches judgment
            fixed labels             and tone
```

**The three numbers to remember from this comparison:** `2e-5` (full encoder fine-tune), `2e-4` (LoRA SFT), `5e-6` (DPO). If you can explain why they differ by those factors, you understand this week.

---

# Part 10 — Fine-tune vs RAG vs Prompt Better: the honest guide

This is the decision that matters most, and the one most often got wrong. Wrong choices here cost weeks.

## 10.1 What each one can and cannot fix

| Your problem | Prompt | RAG | Fine-tune |
|---|---|---|---|
| Model doesn't know your **private data** | ❌ | ✅ **the answer** | ⚠️ unreliable |
| Data changes daily | ❌ | ✅ | ❌ retrain every time |
| Wrong **tone / voice / style** | ⚠️ partly | ❌ | ✅ **the answer** |
| Wrong **output format** | ✅ constrained decoding | ❌ | ✅ (but try prompting first) |
| Needs **domain jargon** fluency | ⚠️ | ⚠️ | ✅ |
| Needs to **cite sources** | ❌ | ✅ **the answer** | ❌ |
| Too **slow / expensive** at inference | — | ❌ adds latency | ✅ small tuned model beats big prompted one |
| Task the model plain **can't do** | ❌ | ❌ | ⚠️ maybe |
| Needs **fresh/real-time** information | ❌ | ✅ | ❌ |
| Must run **offline / air-gapped** | — | ✅ | ✅ |

**The single sharpest line in the whole week:**

> **RAG gives the model new *knowledge*. Fine-tuning gives it new *behaviour*. Prompting gives it new *instructions*.**
>
> If you're trying to fine-tune facts in, you've picked the wrong tool. If you're trying to RAG a personality in, same.

## 10.2 The ladder — climb it in order

```
RUNG 1: Better prompt                        hours       $0
        Role/Task/Context/Format/Constraints, few-shot, schema-constrained output.
        -> Solves more than people expect. ALWAYS start here.

RUNG 2: Prompt + RAG                         days        $ (low, ongoing)
        Embed your documents, retrieve, put them in the prompt.
        -> Solves 80-90% of knowledge-intensive products.

RUNG 3: RAG + a better/bigger model          hours       $$ (higher per call)
        Often cheaper than a fine-tune and instantly reversible.

RUNG 4: Fine-tune (PEFT/LoRA)                weeks       $$$ one-off + upkeep
        Only when you have a SPECIFIC, MEASURED gap the rungs above can't close.

RUNG 5: Alignment (DPO)                      weeks       $$$$
        Only when the model is correct but consistently makes the WRONG CHOICE
        between two correct answers.
```

**Do not skip rungs.** The most common expensive mistake in this field is fine-tuning at rung 4 for a problem that rung 1 solves.

## 10.3 When fine-tuning genuinely is the answer

Five situations where it's clearly right:

1. **Style/voice consistency at scale.** You need every output in your brand voice, every time, and prompting gets you 80% with occasional drift.
2. **Cost and latency.** A fine-tuned 3B model matching a prompted 70B model on *your* narrow task is 20× cheaper and 10× faster. At high volume this pays for itself quickly.
3. **A task prompting keeps failing.** You've tried 20 prompt variants with good few-shot examples and the model still can't do it reliably.
4. **Domain jargon.** Medical, legal, or an internal taxonomy the model has genuinely never seen.
5. **Shrinking the prompt.** If every call carries a 2,000-token system prompt of rules and examples, fine-tuning those rules *into* the model removes that cost from every single request. This one is quietly the strongest business case.

**And when it is clearly wrong:**
- ❌ To add facts. (RAG.)
- ❌ Because you have a lot of data and it feels wasteful not to.
- ❌ Before you have an evaluation set. You will have no way of knowing whether it helped.
- ❌ For knowledge that changes.
- ❌ Because "everyone fine-tunes."

## 10.4 They combine — and usually should

```
The mature production stack:

  Fine-tuned small model  (knows the format, tone, and domain vocabulary)
            +
  RAG                     (supplies the current facts, with citations)
            +
  Good prompting          (assembles the context and states the constraints)
            +
  Guardrails + evaluation (Week 6)
```

A fine-tuned model that is *also* given retrieved context outperforms either alone, because you've separated the two problems correctly: behaviour is baked in, knowledge is looked up.

## 10.5 Before you fine-tune — the checklist

1. ☐ Do I have a **written evaluation set** (50+ real cases with expected outputs)?
2. ☐ Do I have a **measured baseline** from the best prompt I can write?
3. ☐ Have I confirmed the gap is **behaviour**, not missing knowledge?
4. ☐ Do I have **500+ consistent, high-quality** examples?
5. ☐ Have I checked the **licence** permits fine-tuning and deployment?
6. ☐ Do I know how I'll **serve** the result (adapter swapping? merged? quantized?)?
7. ☐ Do I have a **rollback** plan?

**If any box is unticked, go back to rung 1.** Especially box 1: without an eval set you cannot tell whether the fine-tune helped, and you will end up shipping on vibes.

---

# Part 11 — Important updates since the course notes

Things that have genuinely changed, ordered by how much they should change what you do.

1. **Reasoning models made CoT prompting partly counterproductive.** On models with internal reasoning, scripting the steps overrides a better-trained process. Specify goals and constraints; set a thinking budget instead. *(Affects Part 1.)*

2. **Structured output is solved by constrained decoding.** Schema-constrained decoding gives ~100% structurally valid output for free. Since "unreliable format" is the most common reason teams cite for fine-tuning, check this first. *(Part 1.7.)*

3. **"Prompt engineering" became "context engineering."** The job is now choosing what occupies the context window — retrieved chunks, history, tool definitions — within a budget. Wording is the small part.

4. **Modern embedding models are trained contrastively, not with masked-language-modelling.** Mean-pooled BERT is not a competitive retrieval embedding. Use a purpose-built model (BGE-M3, Qwen3-Embedding, `text-embedding-3`). *(Part 2.4.)*

5. **Matryoshka embeddings let you truncate dimensions.** Slice a 3072-dim vector to 256 with minimal quality loss — a large, free storage saving. Standard in OpenAI's v3 family and several open models. *(Part 2.7.)*

6. **BGE-M3 emits dense *and* sparse vectors from one model,** which makes hybrid search (dense + BM25 + RRF) much easier to build. Directly relevant to Week 3.

7. **ModernBERT replaced DeBERTa-v3 as the encoder default.** 8192-token context (vs 512), trained on 2T tokens of text and code, faster, and a genuine drop-in. For a new classifier, start here. *(Part 4.5.)*

8. **The preference-optimization menu grew well past DPO.** ORPO (one-stage SFT+alignment), KTO (thumbs-up/down, no pairs), SimPO (no reference model, length-normalised), GRPO/DAPO (reasoning). **KTO deserves particular attention** because it consumes exactly the feedback real products already collect. *(Part 8.5.)*

9. **GRPO + verifiable rewards (RLVR) is how reasoning models are trained.** Replacing a learned reward model with a deterministic checker removes reward hacking entirely — the single biggest failure mode of classic RLHF. *(Part 8.4.)*

10. **`DPOTrainer` + PEFT no longer needs a separate reference model** — it disables the adapter to recover reference behaviour, roughly halving DPO's memory. *(Part 8.3.)*

11. **The quantization format landscape sorted itself out.** bitsandbytes to **train**, AWQ to **serve on GPU**, GGUF to **run on laptops/CPU/Apple Silicon**. AutoGPTQ is archived (use GPTQModel); ExLlamaV2 is archived (use EXL3). NF4 is a training format, not a serving format. *(Part 6.5.)*

12. **`target_modules` matters more than `r`.** Current guidance is to target attention **and** MLP projections rather than just `q_proj`/`v_proj`. Enable `use_rslora` whenever `r > 32`. **DoRA** gives small consistent gains over LoRA at low rank. *(Part 7.7.)*

13. **"LoRA learns less and forgets less" is now a documented trade-off, not folklore.** LoRA absorbs less new capability than full fine-tuning but preserves far more general ability — usually the right trade for a product. *(Part 7.11.)*

14. **The open/closed capability gap narrowed to roughly 6–12 months,** the open-weight top tier is now largely Chinese labs, and OpenAI itself ships open-weight models. A 27–32B dense model on a single consumer GPU is now genuinely strong. *(Part 5.5.)*

15. **Most "open source" models are open-*weights*.** No training data, no training code, and often real licence restrictions. *(Part 5.1.)*

---

# Part 12 — The week in twelve lines

1. Three levers: change the input (prompting), add knowledge (RAG), change the model (fine-tuning). Try them in that order.
2. A prompt reshapes the next-token distribution temporarily; fine-tuning reshapes it permanently. Neither invents knowledge.
3. Role + Task + Context + Format + Constraints. Every bad answer means one box was empty.
4. An embedding is coordinates for meaning; cosine similarity measures the angle between them.
5. Encoders understand, decoders write. Pick the architecture from the job.
6. Hugging Face = `transformers` + `datasets` + `peft` + `trl` + `bitsandbytes`. That's the whole fine-tuning stack.
7. Most "open-source" models are open-weights. Read the licence.
8. `memory = params × bytes/param`. 4-bit is ~4× smaller for a few percent quality loss.
9. Three axes: **stage** (CPT/SFT/Alignment), **method** (PPO/DPO/GRPO), **mechanism** (Full/PEFT). PEFT is not a fourth type.
10. LoRA factorises the weight update into two skinny matrices. `r` is capacity, `alpha/r` is strength, `target_modules` is where.
11. SFT teaches what to say; alignment teaches what to prefer. DPO does the second without a reward model.
12. Before fine-tuning: write the eval set, measure the prompted baseline, and confirm the gap is behaviour and not knowledge.

---

# Q&A — interview-style

### Q1: What is prompt engineering, really — and why does it work?

**It's writing input text that makes the output you want the most probable continuation.** The model doesn't obey instructions; it continues text. A prompt puts it in a region of its learned distribution where your desired answer is likely.

*Example:* `"You are a senior security auditor. List the three highest-severity issues."` works better than `"find problems"` because expert-framed text in training was followed by precise, prioritised writing.

**One line:** prompting steers the next-token probability distribution — which is exactly why it can fix behaviour and can never fix missing knowledge.

### Q2: Zero-shot vs few-shot vs CoT vs chaining — when do you reach for each?

| | Use when |
|---|---|
| **Zero-shot** | Common task, loose format. Always try first. |
| **Few-shot** | The output shape or your private conventions need demonstrating. |
| **CoT** | Multi-step reasoning on a non-reasoning model. |
| **Chaining** | Steps are independently testable, or need different models / code between them. |

**One line:** zero-shot first, few-shot for format, CoT for reasoning on ordinary models, chaining when you need to see and control each step.

### Q3: Has chain-of-thought prompting become obsolete?

**Partly — on reasoning models.** Models with an internal thinking phase already reason before answering; telling them *how* to reason overrides a process specifically trained to be better than your instructions, and measurably hurts. On those you set a **thinking budget** instead.

It remains correct on ordinary instruction-tuned models and on small local models — which is most of what you'd fine-tune yourself.

**One line:** on reasoning models specify goals and constraints, not reasoning paths; on everything else CoT still works.

### Q4: Explain embeddings and cosine similarity to a non-technical stakeholder.

An embedding gives every piece of text an **address on a map of meaning**. Related things get nearby addresses. "Refund my order" lands near "I want my money back" even though they share almost no words — that's why semantic search beats keyword search.

Cosine similarity measures the **angle** between two addresses: small angle = similar meaning. `1.0` identical, `0` unrelated.

**One line:** embeddings put meaning on a map, and cosine similarity measures how close two points on it are.

### Q5: Why can't you mix embedding models between indexing and querying?

Because each model defines **its own coordinate system**. Model A might put "refund" at `[0.7, -0.2, ...]` and model B at `[-0.4, 0.9, ...]`. Comparing them is comparing a GPS coordinate to a street address — the numbers are the same *type* but mean nothing to each other.

Nothing errors. You just get quietly bad results, which is far worse than a crash.

**One line:** different models mean different coordinate systems — mixing them silently destroys retrieval quality, and changing your embedding model means re-embedding your whole corpus.

### Q6: What's the difference between a bi-encoder and a cross-encoder?

A **bi-encoder** embeds query and document *separately*, so documents can be encoded once offline and compared in milliseconds. A **cross-encoder** reads query and document *together* in one pass, which is far more accurate but can't be precomputed.

**One line:** bi-encoders retrieve fast over millions, cross-encoders rerank accurately over dozens — production uses both, in that order.

### Q7: When would you use BERT instead of an LLM?

When the task is **classification or extraction over a fixed label set, at volume, with latency constraints**. A fine-tuned 150M encoder runs in 5–20 ms for fractions of a cent, and on a fixed label set usually *out-performs* a prompted LLM.

Use the LLM when labels change often, volume is low, or you need explanation and reasoning.

**One line:** fixed labels + high volume + low latency → fine-tuned encoder; changing labels or needing reasoning → LLM. Best of both: have the LLM label your training data, then train the encoder on it.

### Q8: What does quantization actually do, and what do you lose?

It stores each weight in fewer bits. 4 bits = 16 possible values, so you keep a bucket index per weight plus a shared scale per block of ~64 weights.

*Concretely:* Mistral 7B is 29 GB in FP32, 14.5 GB in FP16, and ~3.6 GB in NF4 — the difference between needing an A100 and running on a free Kaggle GPU.

**What you lose:** a few percent quality, concentrated in long multi-step reasoning, code, and multilingual work. Smaller models suffer more; a 4-bit 70B usually beats an FP16 13B.

**One line:** quantization trades a few percent of quality for ~4× less memory, which is what makes big models runnable at all — but it saves memory, not compute, since weights are dequantized for every matmul.

### Q9: Explain LoRA to someone who knows what fine-tuning is.

Fine-tuning changes every weight matrix `W` by some `ΔW`. LoRA's observation is that `ΔW` is **low-rank** — far simpler than its size suggests. So instead of storing a 4096×4096 update (16.8M numbers), store two skinny matrices `B (4096×r)` and `A (r×4096)` whose product approximates it. At `r=8` that's 65,536 numbers — **256× fewer**.

The base model is frozen; only `A` and `B` train. `B` starts at zero, so the model begins bit-identical to the base.

*Real number:* the Week 2 Llama 3.2 3B notebook trains **1.15M of 3.21B parameters — 0.036%**.

**One line:** LoRA freezes the model and learns a tiny low-rank correction alongside it, giving ~full-fine-tune quality at a fraction of the memory and a 30 MB artifact instead of a 14 GB one.

### Q10: What do `r`, `alpha` and `target_modules` do, and how do you pick them?

- **`r` (rank)** — the adapter's capacity. *How much room it has to learn.* Start at 8–16; 32–64 for substantial new behaviour; above 128 is almost always waste.
- **`alpha`** — how loudly the adapter speaks. Effective strength is `alpha/r`; treat that ratio as the real knob and start at 1–2. Convention is `alpha = 2r`. Enable `use_rslora` when `r > 32`.
- **`target_modules`** — where the adapters attach. **This matters more than `r`.** Target attention *and* MLP projections, not just `q_proj`/`v_proj`. Print your model's module names first — a wrong name is silently ignored.

**One line:** `r` is capacity, `alpha/r` is strength, `target_modules` is coverage — and coverage is the one people under-set.

### Q11: Why does LoRA use a 10× higher learning rate than full fine-tuning?

Because you're training a **freshly initialised** adapter from scratch, not nudging pretrained weights. Full fine-tuning at `2e-5` moves weights that already encode language — move them fast and you destroy them. A LoRA adapter starts at zero and has to learn everything it will contribute, so `2e-4` is appropriate.

Same reason epochs differ: full fine-tune an encoder for 10 epochs; run LoRA for 1–3 before it overfits.

**One line:** full fine-tuning gently adjusts knowledge that exists; LoRA trains a small new module from scratch — so it needs a bigger step and far fewer of them.

### Q12: What's the difference between SFT and alignment, and why can't SFT do alignment's job?

**SFT** shows (prompt, answer) pairs and trains imitation. Every example is treated as equally good.

**Alignment** shows (prompt, chosen, rejected) and trains *judgment*.

SFT can't do alignment's job because it has **no way to express that one correct answer is better than another correct answer**. Both *"Refunds are processed per policy 4.2, submit form RF-11"* and *"I'm sorry — I've issued your refund, it'll be back in 3–5 days"* are correct. Only one is good. SFT sees no difference; DPO does.

**One line:** SFT teaches *what to say*, alignment teaches *what to prefer* — you need the second the moment "correct but wrong-toned" is your actual problem.

### Q13: Why did DPO displace PPO?

PPO needs **four models in memory** (policy, reference, reward model, value model), a separately trained reward model, and is notoriously unstable.

DPO's insight is that the RLHF objective can be algebraically rearranged into a **simple classification loss over preference pairs** — no reward model, no RL loop, no critic. Roughly 10× cheaper, far more stable, and it trains like ordinary SFT.

**Where PPO still wins:** online exploration. DPO can only rank what's in your dataset; PPO can discover behaviours that aren't. That's why the PPO family returned as GRPO for reasoning.

**One line:** DPO proved you don't need a separate reward model to learn from preferences — same goal, a fraction of the machinery, dramatically more stable.

### Q14: What is GRPO and why does it matter now?

**GRPO = Group Relative Policy Optimization.** Generate a *group* of answers for one prompt (say 8), score them all, and compute each one's advantage **relative to the group average**. The group average replaces PPO's value model — so you delete the critic.

**Why it matters:** it pairs naturally with **verifiable rewards**. Instead of a learned reward model that can be gamed, use a deterministic checker — do the unit tests pass? is the maths answer right? does the JSON validate? **A verifier cannot be reward-hacked**, because it isn't an approximation of taste, it's a fact. That's how reasoning models are trained.

**Limitation:** only works where correctness is checkable. There's no verifier for "is this a kind reply."

**One line:** GRPO drops PPO's critic by using the group average as the baseline, and with verifiable rewards it eliminates reward hacking — which is why it's the reasoning-era default.

### Q15: When should you fine-tune instead of using RAG?

**RAG for knowledge, fine-tuning for behaviour.**

- Model doesn't know your data, or the data changes → **RAG**. Fine-tuning facts is unreliable and stale the next day.
- Model knows enough but sounds wrong, ignores your format, or is too slow/expensive → **fine-tune**.
- The strongest business case: you carry a 2,000-token system prompt on every call. Bake it into the weights and remove that cost from every request.

And the honest order: prompt → RAG → bigger model → fine-tune. Most teams that start at fine-tuning end up back at prompting.

**One line:** RAG supplies knowledge, fine-tuning supplies behaviour — and if you don't have an evaluation set yet, you're not ready to fine-tune either way.

### Q16: You have 2,000 support tickets and want the model to answer like your best agent. What do you build?

**Answer in order, and say why you're not skipping ahead:**

1. **Prompt first.** Best-agent examples as few-shot, tone rules in the system prompt, schema-constrained output. Measure on a 50-case eval set. *This often gets you most of the way.*
2. **Add RAG** over your policy documents and order database — because the facts (this customer's order, current refund policy) change and must never be baked into weights.
3. **Only then fine-tune**, and specifically **SFT with QLoRA on a 3–8B model**, using ~1,000 cleaned ticket/response pairs from your best agent. Goal: tone and format — *not* facts.
4. **Add DPO only if** the tuned model is factually right but keeps choosing the worse of two acceptable phrasings. Collect (chosen, rejected) pairs from agent edits — or use **KTO** with thumbs-up/down, since that's what you'll actually be able to collect at volume.

**Final architecture:** QLoRA-tuned small model (voice) + RAG (facts, with citations) + guardrails + eval in CI.

**One line:** prompt for the quick win, RAG for the facts, QLoRA-SFT for the voice, and DPO/KTO only once "right but badly phrased" is demonstrably your remaining problem.

---

## Sources

**Prompting**
- [Every AI Prompting Technique That Works on Reasoning Models (2026)](https://karozieminski.substack.com/p/ai-prompting-techniques-reasoning-models-2026)
- [Prompt Engineering in 2026: Techniques That Work](https://www.aibuilderclub.com/blog/prompt-engineering-guide-2026)
- [The Prompt Report: A Systematic Survey of Prompt Engineering Techniques](https://arxiv.org/pdf/2406.06608)

**Embeddings**
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Best Embedding Models for RAG (2026), ranked by MTEB score, cost and self-hosting](https://www.premai.io/blog/best-embedding-models-for-rag-2026-ranked-by-mteb-score-cost-and-self-hosting/)
- [Top embedding models on the MTEB leaderboard — Modal](https://modal.com/blog/mteb-leaderboard-article)

**BERT / encoders**
- [Finally, a Replacement for BERT: Introducing ModernBERT — Answer.AI](https://www.answer.ai/posts/2024-12-19-modernbert.html)
- [Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder (ModernBERT paper)](https://arxiv.org/abs/2412.13663)
- [ModernBERT in Transformers](https://huggingface.co/docs/transformers/v4.48.0/model_doc/modernbert)

**Hugging Face stack**
- [TRL — PEFT integration](https://huggingface.co/docs/trl/en/peft_integration)
- [TRL — DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer)
- [TRL — GRPO Trainer](https://huggingface.co/docs/trl/grpo_trainer)
- [PEFT — LoRA conceptual guide](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)

**Quantization**
- [LLM Quantization Guide: GGUF vs AWQ vs GPTQ vs bitsandbytes Compared (2026)](https://www.premai.io/blog/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/)
- [GGUF vs GPTQ vs AWQ vs EXL2: LLM Model Formats Explained (2026) — MarkTechPost](https://www.marktechpost.com/2026/09/18/gguf-vs-gptq-vs-awq-vs-exl2-llm-model-formats-explained-2026/)
- [Quantization formats compared: GGUF vs GPTQ vs AWQ vs NF4](https://dev.to/tech_nuggets/quantization-formats-compared-gguf-vs-gptq-vs-awq-vs-nf4-2mcm)

**Fine-tuning / PEFT**
- [LoRA fine-tuning Hyperparameters Guide — Unsloth](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide)
- [LoRA Learns Less and Forgets Less](https://arxiv.org/pdf/2405.09673)
- [LoRA & PEFT Fine-Tuning: Production Guide for 2026](https://thecodeforge.io/ml-ai/lora-peft-fine-tuning/)

**Alignment / preference optimization**
- [Direct Preference Optimization (DPO paper)](https://arxiv.org/pdf/2305.18290)
- [Post-Training in 2026: GRPO, DAPO, RLVR & Beyond](https://llm-stats.com/blog/research/post-training-techniques-2026)
- [DPO Isn't Enough: The Modern Post-Training Stack — SimPO, ORPO, KTO and Beyond](https://medium.com/@fahey_james/dpo-isnt-enough-the-modern-post-training-stack-simpo-orpo-kto-and-beyond-d82e52a1ee6c)
- [Which LLM Alignment Method? RLHF vs DPO vs KTO Tradeoffs Explained](https://blog.premai.io/which-llm-alignment-method-rlhf-vs-dpo-vs-kto-tradeoffs-explained/)
- [DPO vs PPO: Which RLHF Algorithm to Use for Production LLM Alignment (2026)](https://www.spheron.network/blog/dpo-vs-ppo-rlhf-algorithm-production-llm-alignment/)

**Open vs closed**
- [Best Open-Weight LLMs 2026: DeepSeek vs Qwen vs Kimi vs GLM vs Llama](https://wavect.io/blog/open-weight-llm-comparison-2026/)
- [Open Source LLM Leaderboard 2026 — Vellum](https://www.vellum.ai/open-llm-leaderboard)

**Choosing between approaches**
- [RAG vs Fine-Tuning vs Prompt Engineering: When to Use Each (2026 Guide)](https://www.elowit.com/blog/rag-vs-fine-tuning-vs-prompt-engineering)
- [Fine-Tuning vs RAG vs Prompt Engineering — 2026 Framework](https://www.kunalganglani.com/blog/fine-tuning-vs-rag-prompt-engineering)

**Course source material (branch `LearningGenAI-Week2`)**
- `Basic Prompt Engineering Techniques.md`
- `Introduction to Vector Embeddings.md`
- `Hugging Face Explained Simply.md`
- `How to use BERT for simple tasks.md`
- `Open-Source vs Closed-Source Models in Generative AI.md`
- `What is Quantization.md`
- `Advanced Fine-tuning Techniques.md` + `Fine-tuning Mindmap.md`
- `Optimization Methods for LLMs (PPO, DPO).md`
- `kaggle/customer-support-ticket-tagger.ipynb`
- `kaggle/lora-llama-customer-support/Customer_Support_LoRA_Llama_3_2_3B_Instruct.ipynb`
- `kaggle/dpo-mistral-security-protocols/dpo_optimized_mistral_7b_finetuning.ipynb` + `NOTES-Unsloth-and-HuggingFace.md`

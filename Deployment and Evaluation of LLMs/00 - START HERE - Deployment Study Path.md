# Week 5 — The Deployment Study Path

*A navigator for the deployment half of this folder: what to read, in what order, and why that order. Roughly **3 hours** for a focused pass — 2 video sessions (~3.3 hrs of recording, condensed into notes you can read in ~70 min) plus 48 pages of reading and one notebook.*

> **Scope:** this path covers **deployment only** — getting a GenAI app off your laptop and onto something other people can reach. The `Evaluation/` folder is a separate track and isn't part of this path.

---

## The order, at a glance

Every file below is named exactly as it appears on disk — open them in this order.

| # | Exact file to open | Size | Time |
|---|---|---|---|
| 1 | `Deploying Applications/AWS Deployment - Video Notes.md` | 419 lines | ~30 min |
| 2 | `Deploying Applications/Docker and Docker Compose.pdf` | 10 pages | ~25 min |
| 3 | `Deploying Applications/Deploying a GenAI Application - Video Notes.md` | 588 lines | ~40 min |
| 4 | `Hosting Platforms/AWS Bedrock.pdf` | 7 pages | ~15 min |
| 5 | `Hosting Platforms/Hugging Face Inference Endpoints.pdf` | 6 pages | ~10 min |
| 6 | `Hosting Platforms/Cerebrium.pdf` | 5 pages | ~10 min |
| 7 | `Model Serving and Formats/LLM Model Serving.pdf` | 6 pages | ~10 min |
| 8 | `Model Serving and Formats/vLLM.pdf` | 4 pages | ~8 min |
| 9 | `Model Serving and Formats/Ollama.pdf` | 10 pages | ~15 min |
| 10 | `Model Serving and Formats/GGUF (GPT-Generated Unified Format).pdf` | 6 pages | ~10 min |
| 11 | `Model Serving and Formats/Llama.cpp - Conversion from safetensors to gguf.ipynb` | notebook | ~20 min |

**Steps 7-11 are optional** — see step 5 below.

**Two files you do *not* need to open:**
- `Deploying Applications/AWS Deployment - Transcript.md` (435 lines)
- `Deploying Applications/Deploying a GenAI Application - Transcript.md` (1,232 lines)

These are the raw verbatim session transcripts. Their condensed versions — `Deploying Applications/AWS Deployment - Video Notes.md` and `Deploying Applications/Deploying a GenAI Application - Video Notes.md` — are what you should actually read. Open a transcript only if you want the full unedited detail of a specific moment.

---

## Why this order

### Step 1 — Deploy something by hand

**Open:** `Deploying Applications/AWS Deployment - Video Notes.md`

Start here even though it's the shorter session, because it's the one that builds intuition. You take a FastAPI app, put it on a bare EC2 box, and make it reachable — SSH in, install Python, run it, open a port.

Two things it teaches that everything later depends on:
- **The two classic reasons your app isn't reachable** — binding to `localhost` instead of `0.0.0.0`, and the security-group inbound rule. You *will* hit both, and after this session you'll recognise them in seconds.
- **Why automation exists.** Doing it manually once makes Docker and ECS feel like relief rather than ceremony.

No Docker needed for this step. That's deliberate.

### Step 2 — Learn containerization

**Open:** `Deploying Applications/Docker and Docker Compose.pdf` (10 pages)

Not optional, and not something to skim during step 3. The "Deploying a GenAI Application" session opens by saying, in effect, *go read the Docker material first or this won't land.* Ten pages — just do it here.

### Step 3 — Deploy it properly

**Open:** `Deploying Applications/Deploying a GenAI Application - Video Notes.md`

The biggest and most valuable session in Week 5. This is where deployment stops being "a box I SSH into" and becomes an architecture: Docker image → ECR → ECS/Fargate, with secrets management, logging, and a real cost model.

What to pay closest attention to:
- **The architecture decision table** — ECR+EC2 vs. ECR+ECS-on-EC2 vs. Fargate. Interviewers ask you to justify this choice.
- **The live IAM/secrets bug** the session hits. Watching a real permissions failure get diagnosed is worth more than reading about IAM.
- **The cost contrast** — ~$0.03 vs. ~$5/hr depending on what you provision, and the reserve-vs-use trap.

### Step 4 — Know the alternatives

**Open, in this order:**
1. `Hosting Platforms/AWS Bedrock.pdf` (7 pages)
2. `Hosting Platforms/Hugging Face Inference Endpoints.pdf` (6 pages)
3. `Hosting Platforms/Cerebrium.pdf` (5 pages)

These are managed services that do steps 1-3 *for* you. They're placed fourth on purpose: read them before you've deployed anything yourself and they sound like magic with no trade-offs. Read them after, and you can actually evaluate what you're giving up (control, cost at scale, portability) for what you're getting (no infrastructure to own).

The question they answer: **"should I even be doing this myself?"** — which is a genuinely good interview answer when someone asks how you'd deploy something.

### Step 5 — Serving your own model *(optional)*

**Only relevant if you're hosting model weights yourself** rather than calling OpenAI/Anthropic/Bedrock. If your work is API-based, skip this entirely and lose nothing from the deployment story.

**Open, in this order:**
1. `Model Serving and Formats/LLM Model Serving.pdf` (6 pages) — the general problem: why serving a model isn't just "load it and call it"
2. `Model Serving and Formats/vLLM.pdf` (4 pages) — the high-throughput production server
3. `Model Serving and Formats/Ollama.pdf` (10 pages) — the easy local-first option
4. `Model Serving and Formats/GGUF (GPT-Generated Unified Format).pdf` (6 pages) — the quantized format that makes models fit on modest hardware
5. `Model Serving and Formats/Llama.cpp - Conversion from safetensors to gguf.ipynb` — do the conversion yourself; GGUF makes far more sense once you've produced one

---

## If you're short on time

**90 minutes — the core path.** Open exactly these three, in this order:
1. `Deploying Applications/AWS Deployment - Video Notes.md`
2. `Deploying Applications/Docker and Docker Compose.pdf`
3. `Deploying Applications/Deploying a GenAI Application - Video Notes.md`

That's the complete "I can deploy a containerized GenAI app to AWS" story, and it's what an interviewer is most likely to probe.

**30 minutes — interview triage only.** Open these two files and read *only* their `## 🎤 Interview Prep` section:
1. `Deploying Applications/AWS Deployment - Video Notes.md`
2. `Deploying Applications/Deploying a GenAI Application - Video Notes.md`

That's 20 questions + 7 follow-ups between them, all web-researched. You'll be able to *talk* about deployment credibly, though you won't be able to *do* it.

**Skip entirely if API-based:** everything in `Model Serving and Formats/`. It's a real topic, just not yours unless you self-host weights.

---

## How each notes file is laid out

These two files follow the same shape, so you can navigate them the same way:

- `Deploying Applications/AWS Deployment - Video Notes.md`
- `Deploying Applications/Deploying a GenAI Application - Video Notes.md`

Inside each, in order:

- **Numbered sections** walking the session in its own order
- **`## Key Takeaways`** — the compressed version; good for a second pass or a refresher the night before
- **`## 🎤 Interview Prep`** — web-researched questions in two layers: **✅ Strong answer** (plain language, understand this one) and **🎯 Standard Interview Answer** (jargon-precise, say this one)
- **`## Q&A`** — empty by design. Log questions here as you study, numbered `### Q1:`, `### Q2:` …

**One habit worth keeping:** in the interview sections, answer out loud from memory *before* reading the answer. Reading them cold is the most reliable way to feel prepared without being prepared.

---

## Full file map of this folder

```
Deployment and Evaluation of LLMs/
├── 00 - START HERE - Deployment Study Path.md      ← you are here
│
├── Deploying Applications/
│   ├── AWS Deployment - Video Notes.md                    ← step 1
│   ├── Docker and Docker Compose.pdf                      ← step 2
│   ├── Deploying a GenAI Application - Video Notes.md     ← step 3
│   ├── AWS Deployment - Transcript.md                       (raw, skip)
│   └── Deploying a GenAI Application - Transcript.md        (raw, skip)
│
├── Hosting Platforms/                              ← step 4
│   ├── AWS Bedrock.pdf
│   ├── Hugging Face Inference Endpoints.pdf
│   └── Cerebrium.pdf
│
├── Model Serving and Formats/                      ← step 5 (optional)
│   ├── LLM Model Serving.pdf
│   ├── vLLM.pdf
│   ├── Ollama.pdf
│   ├── GGUF (GPT-Generated Unified Format).pdf
│   └── Llama.cpp - Conversion from safetensors to gguf.ipynb
│
└── Evaluation/                                     ← separate track, not this path
    ├── LLM Evaluation - Video Notes.md
    ├── LLM Evaluation.pdf
    └── LLM Evaluation - Transcript.md
```

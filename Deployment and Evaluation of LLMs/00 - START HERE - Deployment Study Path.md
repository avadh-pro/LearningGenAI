# Week 5 — The Deployment Study Path

*A navigator for the deployment half of this folder: what to read, in what order, and why that order. Roughly **3 hours** for a focused pass — 2 video sessions (~3.3 hrs of recording, condensed into notes you can read in ~70 min) plus 48 pages of reading and one notebook.*

> **Scope:** this path covers **deployment only** — getting a GenAI app off your laptop and onto something other people can reach. The `Evaluation/` folder is a separate track and isn't part of this path.

---

## The order, at a glance

| # | What | Where | Time | Why here |
|---|---|---|---|---|
| 1 | **AWS Deployment** — notes | `Deploying Applications/` | ~30 min | Deploy by hand first. Fewest new concepts, and it shows you *why* everything after it exists. |
| 2 | **Docker and Docker Compose** — 10 pp | `Deploying Applications/` | ~25 min | Hard prerequisite for step 3. The session itself tells you to read this first. |
| 3 | **Deploying a GenAI Application** — notes | `Deploying Applications/` | ~40 min | The real thing: containerized, managed, production-shaped. |
| 4 | **Hosting Platforms** — 18 pp | `Hosting Platforms/` | ~35 min | The "or just don't build it yourself" alternatives — only meaningful once you know what you'd be avoiding. |
| 5 | **Model Serving and Formats** — 26 pp + notebook | `Model Serving and Formats/` | ~50 min | Optional side-track. Only needed if you're hosting model *weights*, not calling an API. |

**Read the Video Notes, not the transcripts.** The notes are the condensed version of each session. The transcripts sit beside them if you ever want the full verbatim detail — but they're 435 and 1,232 lines respectively, and you don't need them to learn this.

---

## Why this order

### Step 1 — Deploy something by hand *(AWS Deployment)*

Start here even though it's the "lesser" session, because it's the one that builds intuition. You take a FastAPI app, put it on a bare EC2 box, and make it reachable — SSH in, install Python, run it, open a port.

Two things it teaches that everything later depends on:
- **The two classic reasons your app isn't reachable** — binding to `localhost` instead of `0.0.0.0`, and the security-group inbound rule. You *will* hit both, and after this session you'll recognise them in seconds.
- **Why automation exists.** Doing it manually once makes Docker and ECS feel like relief rather than ceremony.

No Docker needed for this step. That's deliberate.

### Step 2 — Learn containerization *(Docker and Docker Compose, 10 pages)*

Not optional, and not something to skim during step 3. The "Deploying a GenAI Application" session opens by saying, in effect, *go read the Docker material first or this won't land.* Ten pages — just do it here.

### Step 3 — Deploy it properly *(Deploying a GenAI Application)*

The biggest and most valuable session in Week 5. This is where deployment stops being "a box I SSH into" and becomes an architecture: Docker image → ECR → ECS/Fargate, with secrets management, logging, and a real cost model.

What to pay closest attention to:
- **The architecture decision table** — ECR+EC2 vs. ECR+ECS-on-EC2 vs. Fargate. Interviewers ask you to justify this choice.
- **The live IAM/secrets bug** the session hits. Watching a real permissions failure get diagnosed is worth more than reading about IAM.
- **The cost contrast** — ~$0.03 vs. ~$5/hr depending on what you provision, and the reserve-vs-use trap.

### Step 4 — Know the alternatives *(Hosting Platforms, 18 pages)*

**AWS Bedrock** (7 pp), **Hugging Face Inference Endpoints** (6 pp), **Cerebrium** (5 pp).

These are managed services that do steps 1-3 *for* you. They're placed fourth on purpose: read them before you've deployed anything yourself and they sound like magic with no trade-offs. Read them after, and you can actually evaluate what you're giving up (control, cost at scale, portability) for what you're getting (no infrastructure to own).

The question they answer: **"should I even be doing this myself?"** — which is a genuinely good interview answer when someone asks how you'd deploy something.

### Step 5 — Serving your own model *(Model Serving and Formats, 26 pages + notebook)*

**Only relevant if you're hosting model weights yourself** rather than calling OpenAI/Anthropic/Bedrock. If your work is API-based, you can skip this and lose nothing from the deployment story.

Suggested internal order:
1. **LLM Model Serving** (6 pp) — the general problem: why serving a model isn't just "load it and call it"
2. **vLLM** (4 pp) — the high-throughput production server
3. **Ollama** (10 pp) — the easy local-first option
4. **GGUF** (6 pp) — the quantized format that makes models fit on modest hardware
5. **`Llama.cpp - Conversion from safetensors to gguf.ipynb`** — do the conversion yourself; GGUF makes far more sense once you've produced one

---

## If you're short on time

**90 minutes — the core path:** step 1 notes → Docker PDF → step 3 notes. That's the complete "I can deploy a containerized GenAI app to AWS" story, and it's what an interviewer is most likely to probe.

**30 minutes — interview triage only:** read just the `## 🎤 Interview Prep` section at the bottom of both deployment Video Notes files (20 questions + 7 follow-ups between them, all web-researched). You'll be able to *talk* about deployment credibly, though you won't be able to *do* it.

**Skip entirely if API-based:** step 5. It's a real topic, just not yours unless you self-host weights.

---

## How each notes file is laid out

Every Video Notes file follows the same shape, so you can navigate them the same way:

- **Numbered sections** walking the session in its own order
- **`## Key Takeaways`** — the compressed version; good for a second pass or a refresher the night before
- **`## 🎤 Interview Prep`** — web-researched questions in two layers: **✅ Strong answer** (plain language, understand this one) and **🎯 Standard Interview Answer** (jargon-precise, say this one)
- **`## Q&A`** — empty by design. Log questions here as you study, numbered `### Q1:`, `### Q2:` …

**One habit worth keeping:** in the interview sections, answer out loud from memory *before* reading the answer. Reading them cold is the most reliable way to feel prepared without being prepared.

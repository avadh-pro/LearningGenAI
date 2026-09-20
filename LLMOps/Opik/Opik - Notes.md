# Opik — Notes

Condensed notes from the TMLC *Opik* reading (`Opik.pdf` in this folder), cross-checked against `LLMOps Overview/LLMOps - Transcript.md`. Reads naturally **after** the sibling `LLM Tracing/LLM Tracing - Notes.md` — that file explains *why* tracing matters and covers LangSmith; this one covers the tool you reach for when you're **not** in the LangChain ecosystem.

**The core idea in plain words:** Opik is an **open-source platform built by Comet** that does three jobs that usually need three separate tools — **tracing** (what happened on this request), **evaluation** (was the answer any good), and **monitoring** (how is it doing across thousands of requests). You can run it entirely on your own machine with Docker, or use the hosted version on Comet.com.

> 🏥 **The analogy:** if a trace ID is a *parcel tracking number* (from the tracing notes), then Opik is the **whole logistics control room** — the tracking system, the quality inspectors checking parcels are intact, and the wall of dashboards showing today's delivery rate, all in one place.

---

## 1. Why Opik — Two Phases

The reading splits Opik's value by *when* you use it.

### Development phase

| Feature | What it does |
|---|---|
| **Tracing** | Track all LLM calls and traces — in development *and* production |
| **Annotations** | Log feedback scores via the Python SDK or the UI |
| **Prompt Playground** | Experiment with different prompts and models |
| **Automated Evaluation** | Store test cases, run experiments, evaluate performance |
| **LLM-as-a-Judge Metrics** | Built-in metrics — hallucination detection, moderation, relevance |
| **CI/CD Integration** | Run evaluations in your pipeline via the **PyTest integration** |

**What each of those six actually means, in plain terms:**

**1. Tracing — the flight recorder.**
Records every step of one request: the prompt, each LLM call, tool calls, timings, tokens, cost. Same idea as the sibling `LLM Tracing/` folder, just Opik's implementation of it.
> *Example:* a user complains an answer was wrong. You open that one request's trace and see the retrieval returned the wrong document — so it's a retrieval bug, not a model bug. Without it, both look identical from outside.

**2. Annotations — writing a score onto a specific trace.**
A way to attach a judgment to one recorded run: thumbs up/down, a 1–5 rating, or a free-text note. You can do it by hand in the UI, or programmatically from the SDK.
> *Example:* a domain expert reviews 50 real answers in the UI and marks 12 as wrong. Those 12 annotated traces become your labelled test set — the ground truth you otherwise had to build from scratch. This is exactly the "LLM-drafted, human-verified" shortcut discussed in the Week 3 notes, except the drafts are real production answers.

**3. Prompt Playground — a scratchpad for prompts.**
Edit a prompt, swap the model, re-run, and compare outputs side by side, without touching your codebase or redeploying.
> *Example:* your summariser is too verbose. Instead of editing code and re-running the app five times, you paste the prompt into the playground, try three phrasings against the same input, and see which one actually shortens the output. Then you change the code once.

**4. Automated Evaluation — your test suite, for answers instead of code.**
Store a fixed set of test cases (question + expected answer), run your app against all of them, and get scores back. Exactly what `DeepEval_RAG_Evaluation.ipynb` does in the RAG folder, just inside Opik.
> *Example:* 50 stored questions. You change the chunk size, re-run the suite, and see faithfulness drop from 0.94 to 0.71 — so you revert. That's the difference between knowing and guessing whether a change helped.

**5. LLM-as-a-Judge Metrics — an AI grading the answers.**
Some qualities can't be checked with a formula. "Is this answer faithful to the context?" needs judgment, so another LLM reads the context and the answer and scores it. Opik ships these built in — hallucination, moderation, relevance — so you don't write the judge prompts yourself.
> *Example:* the context says *"refunds within 30 days."* The answer says *"refunds within 30 days, and you'll get email confirmation."* No formula catches that; a judge does — the email bit was invented. (Full metric list in Section 3.)

**6. CI/CD Integration — the tests run themselves on every change.**
Via the PyTest integration, your evaluation suite runs in the build pipeline like ordinary unit tests, and a quality regression **fails the build**.
> *Example:* a teammate tweaks the system prompt and opens a PR. CI runs the eval suite, faithfulness drops below the 0.8 threshold, and the PR goes red — caught before merge rather than by a customer next week.

**How the six fit together:** tracing records what happened, annotations let humans label it, the playground is where you try fixes, automated evaluation scores them at scale, judge metrics do the scoring where no formula exists, and CI/CD makes it all run automatically on every change. In short — **observe → label → experiment → measure → automate.**

### Production monitoring

| Feature | What it does |
|---|---|
| **Scalability** | High-volume logging — suitable for **millions of traces daily** |
| **Monitoring Dashboards** | Feedback scores, token usage, trace count over time |
| **Online Evaluation Metrics** | Catch issues *in production* using LLM-as-a-Judge metrics |

> 🔑 **The row that actually differentiates Opik is the last one: "Online Evaluation Metrics."** Most evaluation tooling runs *offline* — a fixed test set, in CI, before release. Opik runs the same judge metrics against **live production traffic**. That directly attacks the "metric–production gap" named in the Week 3 *Current State of RAG* notes: your offline scorecard says 0.95 while real users are having a worse time, and you never find out because nobody is scoring real traffic.

---

## 2. Installing and Getting Started

Opik ships two ways: **self-hosted open-source**, or **hosted on Comet.com**.

```bash
pip install opik
opik configure
```

For a purely local deployment, configure in code instead:

```python
import opik

opik.configure(use_local=True)

@opik.track
def my_llm_function(user_question: str) -> str:
    return llm.invoke(user_question)
```

**That `@opik.track` decorator is the entire integration story.** Put it on a function and every call gets traced — inputs, outputs, timings.

> 🆚 **Compare with LangSmith:** LangSmith needs *no* decorator at all (just `LANGSMITH_TRACING=true`), because it hooks into LangChain's shared `Runnable` interface. Opik asks for one decorator per function — but that's exactly *why* it works with any codebase, framework or not. LangSmith's zero-effort setup is bought by assuming you're inside LangChain; Opik's small explicit cost buys framework independence.

Framework integrations exist for **LangChain and LlamaIndex** if you are using them.

### Self-hosting with Docker Compose

```bash
git clone https://github.com/comet-ml/opik.git
cd opik/deployment/docker-compose
docker compose up --detach
```

Then open the UI at **http://localhost:5173**.

---

## 3. LLM-as-a-Judge Metrics

Opik ships pre-built evaluation metrics:

- **Hallucination Detection**
- **Moderation** (harmful content detection)
- **Answer Relevance & Usefulness**
- **Context Recall & Precision**
- **Heuristic-Based Metrics** (regex matching, JSON validation, etc.)

```python
from opik.evaluation.metrics import Hallucination

metric = Hallucination()
score = metric.score(
    input="What is the capital of France?",
    output="Paris",
    context=["France is a country in Europe."]
)
print(score)
```

> 📌 **Read that example carefully — it's a good illustration of what "faithfulness" really means.** "Paris" is factually correct, but the supplied context only says France is a country in Europe; it never mentions the capital. So a hallucination check can flag this *even though the answer is true*, because the claim isn't supported by the context given. That's the exact point from the Week 3 notes: **faithfulness measures agreement with the context, not with reality.**

Note also that the last bullet — **heuristic metrics** — aren't LLM-judged at all. Regex matching and JSON validation are deterministic, free, and instant. Worth using wherever they suffice, because an LLM judge costs a call and can itself be wrong.

---

## 4. Evaluating Your Application

Evaluation doesn't stop at development:

- **Datasets and Experiments** — store test cases, run experiments against them.
- **PyTest integration** — run evaluations inside your CI/CD pipeline.

**Why the PyTest integration matters more than it sounds:** it turns evaluation into a *build gate*. A prompt tweak that drops faithfulness from 1.0 to 0.7 fails the build instead of quietly shipping. Without that, an eval suite is a thing someone runs occasionally and then stops running.

---

## 5. Opik vs. DeepEval — Which to Reach For

These genuinely overlap, so it's worth being precise. The `DeepEval_RAG_Evaluation.ipynb` notebook in `Retrieval Augmented Generation (RAG)/notebook/` already scores Faithfulness, Answer Relevancy, and Contextual Precision/Recall/Relevancy — metrics Opik also offers.

| | **DeepEval** | **Opik** |
|---|---|---|
| What it is | An evaluation **library** | An evaluation + tracing + monitoring **platform** |
| Tracing | ✗ — not its job | ✓ built in |
| Offline eval in CI | ✓ (pytest-native) | ✓ (PyTest integration) |
| **Online eval on live traffic** | ✗ | **✓ — the real differentiator** |
| Dashboards | ✗ | ✓ |
| Infrastructure needed | None — `pip install` | A server (Docker locally, or hosted Comet) |

**When to pick which:**

- **DeepEval** — you only need *offline* scoring in CI, and you already get tracing elsewhere (LangSmith, say). Lightest possible option: no server, no infrastructure.
- **Opik** — you want traces, evaluations, and production dashboards in **one place**, and especially if you want the same metrics running against live traffic rather than only a frozen test set.

**They also compose:** nothing stops you using DeepEval as your CI gate and Opik for production tracing and online monitoring. The overlap is real but not exclusive.

---

## 6. Opik in Practice — From the Session

The speaker used Opik in the Perplexity-style application build (see `Perplexity-Style App/`), and the reason is a genuinely practical one worth remembering:

> *"I have this `main.py` which has all the things like Ollama, Opik to trace my chats with — because Streamlit can't persist and I'm not storing my chat data, so I'm storing all that on an Opik server."*

**Unpacking that:** Streamlit re-runs the whole script on every interaction and keeps nothing between sessions. Rather than build a database just to keep conversation history, the traces *become* the record — Opik is already capturing every call, so the trace store doubles as the chat log.

This also shows why Opik fitted that project and LangSmith wouldn't have: the app runs on **Ollama**, not LangChain. Straight back to the selection rule from the tracing notes — **LangSmith inside the LangChain ecosystem, Opik or Langfuse outside it.**

---

## Key Takeaways

1. **Opik is a platform, not a library** — tracing, evaluation, and monitoring together, open-source, self-hostable via Docker on port **5173**.
2. **`@opik.track` is the whole integration** — one decorator per function, which is what makes it framework-agnostic.
3. **Online evaluation is the standout feature** — the same LLM-as-a-Judge metrics running on live production traffic, not just an offline test set.
4. **Its hallucination example is a faithfulness lesson** — a factually-true answer can still be unsupported by the given context.
5. **Heuristic metrics are free** — regex and JSON validation need no LLM call; use them where they suffice.
6. **DeepEval vs. Opik:** library vs. platform. DeepEval if you just need CI scoring; Opik if you want traces, dashboards, and production-time evaluation in one system.
7. **Pick by ecosystem** — LangChain/LangGraph → LangSmith. Anything else (Ollama, custom code) → Opik or Langfuse.

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

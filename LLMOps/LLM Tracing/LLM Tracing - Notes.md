# LLM Tracing — Notes

Condensed notes from the TMLC *LLM Tracing* reading (`LLM Tracing.pdf` in this folder), cross-checked against what the speaker said in `LLMOps Overview/LLMOps - Transcript.md`.

**The core idea in plain words:** an LLM application is a black box. You send a question in, an answer comes out, and when the answer is wrong or slow you have no idea *which part* misbehaved — the prompt? the retrieval? the tool call? the model itself? **Tracing is what turns that black box into a glass box.** It records every step of a single request, in order, with timings attached, so you can look at one specific bad answer afterwards and see exactly where it went wrong.

> 📦 **The analogy that carries this whole file:** a trace ID is a **parcel tracking number**. One code that shows you every stop the package made, how long it sat at each one, and precisely where it got lost. Without it, you have a warehouse full of unlabelled boxes and a customer saying "my thing never arrived."

This is the same idea as the **observability layer** in the Week 4 agent architecture (`AI Agents/End to End Architecture of a Single Agent`), where one trace ID follows a request across reasoner → guardrails → tools. That week described *why* you'd want it. This file is about the tools that actually do it.

---

## 1. What LLM Tracing Actually Records

Tracing tracks and visualises every step involved in handling one request through an LLM pipeline:

| Stage | What gets captured |
|---|---|
| **Input Processing** | How the prompt was structured and passed to the model |
| **Model Invocation** | How long the model took to generate its response |
| **Intermediary Steps** | Calls to external APIs, vector database queries, function executions |
| **Response Handling** | Formatting, ranking, or post-processing applied before the answer goes back |

Notice that the middle two rows are where RAG and agents actually live — a vector DB query and a tool call are both "intermediary steps." That's why tracing matters far more for a RAG pipeline or an agent than for a single bare LLM call: **there are more places to go wrong, and only a trace tells you which one did.**

---

## 2. Why You Need It — Four Reasons

- **Debugging issues** — identify bottlenecks, failed requests, and incorrect outputs.
- **Optimizing performance** — reduce latency and resource consumption.
- **Understanding model behaviour** — see how prompt changes actually affect responses.
- **Logging and analytics** — track user interactions and improve responses over time.

> **Worth connecting:** in the Week 3 *Current State of RAG* notes, the hardest production failure was that **retrieval and generation fail identically from the outside** — both just produce a bad answer. Tracing is the mechanism that separates them, because you can open the trace and see whether the right chunk was ever retrieved in the first place.

**The three tools named in the reading:** **LangSmith**, **Opik**, and **Langfuse**.

The transcript gives a clean rule for choosing between them:

> *"If you are into a LangChain, LangGraph kind of an environment, LangSmith is a great choice. If you are using something of your custom or some other library, there are libraries like Opik, Langfuse."*

So: **LangSmith if you're inside the LangChain ecosystem; Opik or Langfuse if you're not.** Opik gets its own notes file in the sibling `Opik/` folder.

---

## 3. LangSmith — Prototype vs. Production

The reading's framing is a one-liner worth remembering:

```
🛠  LangChain / LangGraph  =  Prototyping
🏭  LangSmith             =  Production
```

LangChain was built to make *prototyping* easy. But going from prototype to production introduces a different problem — **reliability**. It's relatively easy to build an LLM app that works in a controlled environment; getting consistent, dependable performance at scale is the actual hurdle.

LangSmith targets that gap across **five areas**: ✅ Debugging ✅ Testing ✅ Evaluating ✅ Monitoring ✅ Usage Metrics

One non-obvious advantage the reading calls out: **the UI lowers the barrier to entry**, especially for people without a software-engineering background. Tracing data is useless if only one engineer can read it.

---

## 4. Setting LangSmith Up

**Step 1 — log in** to LangSmith. The landing page shows an Observability panel with Tracing Projects and Dashboards, and columns for **Feedback, Run Count, Error Rate, P50 Latency, and P99 Latency** over 7 days.

> 📊 Note those last two columns — **P50 and P99 latency, side by side, by default.** That's exactly the point from the Week 3 interview prep: an average hides the worst 1% of requests, so the tool shows you both rather than letting you fool yourself with a mean.

**Step 2 — get an API key.** Click **Setup Tracing** → **Generate API Key**, and give the project a name.

**Step 3 — wire it into an existing LangChain / LangGraph RAG or agent.**

```bash
pip install langsmith
```

**Step 4 — the `.env` file.** This is the whole integration; there is no code change needed beyond loading these:

```bash
OPENAI_API_KEY=<Add your key>
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<Add your key>
LANGSMITH_PROJECT=<Add your project name>
```

**That's the part worth internalising:** `LANGSMITH_TRACING=true` plus the keys is enough. Because every LangChain component already implements the same `Runnable` interface (the LCEL point from the Week 3 LangChain notes), tracing hooks in automatically at every step — you don't instrument each call by hand.

**The worked example from the reading — a Wikipedia agent:**

```python
import os
import dotenv
import pandas as pd
from langchain.agents import initialize_agent, AgentType, load_tools
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain import hub
from langchain.memory import ConversationBufferMemory

dotenv.load_dotenv()
os.environ['OPENAI_API_KEY']      = os.getenv('OPENAI_API_KEY')
os.environ['LANGSMITH_API_KEY']   = os.getenv('LANGSMITH_API_KEY')
os.environ['LANGSMITH_PROJECT']   = os.getenv('LANGSMITH_PROJECT')
os.environ['LANGSMITH_ENDPOINT']  = os.getenv('LANGSMITH_ENDPOINT')
os.environ['LANGSMITH_TRACING']   = os.getenv('LANGSMITH_TRACING')

llm   = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")
tools = load_tools(["wikipedia"], llm=llm)

memory = ConversationBufferMemory(memory_key="chat_history")

conversational_agent = initialize_agent(
    agent='conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
    memory=memory,
)

response = conversational_agent.run("Who won the 2022 Fifa world cup?")
print(response)
```

Two details from Week 3/4 material showing up in the wild here: **`max_iterations=3`** is the hard iteration cap that stops an agent looping forever, and **`ConversationBufferMemory`** is the full-transcript memory type — accurate but growing every turn.

---

## 5. Reading the Results — Where Tracing Earns Its Keep

Run the code (Colab or a `.py` file), then open the **Tracing panel** on the left under your project name. The top-level view shows **input, output, latency, tokens used, and probable cost**. Click **All runs** for the detailed view of every component involved.

Here's the actual run from the reading's screenshots, and it's the single most instructive thing in the whole document:

```
AgentExecutor   "Who won the 2022 Fifa world cup?"        7.30s    1,847 tokens
├── LLMChain                                              1.49s
│   └── ChatOpenAI                                        1.48s
├── wikipedia        (tool call: "2022 FIFA World Cup")   4.39s   ← 60% of total time
└── LLMChain                                              1.39s
    └── ChatOpenAI                                        1.39s
```

**Read that stack and the lesson jumps out:** the whole request took 7.30 seconds, and **4.39 seconds of it — about 60% — was the Wikipedia tool call, not the LLM.** Both model calls together cost under 3 seconds.

> 🔧 **Why this matters practically:** if you'd tried to speed this agent up by reaching for a faster model, you'd have been optimising the *smaller* half of the problem. The trace tells you the fix is caching, a faster tool, or calling Wikipedia in parallel — a conclusion you simply cannot reach from the outside, where all you see is "it took 7 seconds."

That is the entire argument for tracing in one example.

---

## 6. Datasets and Evaluation — and an Honest Caveat

LangSmith also supports creating datasets and testing against them. But the reading is refreshingly blunt about the limits:

> *"It might [not] be the best as compared to libraries created specifically for evaluation like DeepEval, Ragas, TruLens."*

**In other words: LangSmith is excellent at tracing and monitoring, merely adequate at evaluation.** For serious evaluation, reach for a purpose-built library — which is exactly what the `DeepEval_RAG_Evaluation.ipynb` notebook in `Retrieval Augmented Generation (RAG)/notebook/` does, scoring Faithfulness, Answer Relevancy, and Contextual Precision/Recall/Relevancy into one scorecard.

This is the natural seam into the sibling **`Opik/Opik - Notes.md`** — because Opik's pitch is precisely that it does *both*: tracing **and** first-class evaluation in one platform.

---

## 7. What the Transcript Adds

Two things from the session that the PDF doesn't say:

**1. Tracing is only half of "monitoring."** The speaker splits observability in two:

| Layer | What you watch | Tools |
|---|---|---|
| **LLM-level** | Tokens per day, latency, hallucination rate over time, model drift, response accuracy | LangSmith, Opik, Langfuse (+ DeepEval / TruLens for scoring) |
| **System-level** | Requests per second, input/output data size, uptime/downtime, CPU and GPU utilisation | Prometheus, Grafana (see the sibling `Grafana and Prometheus/` folder) |

**2. LLMOps monitors different things than MLOps.** In traditional MLOps you'd track R², adjusted R², MSE for regression, or F1/precision/recall for classification. In LLMOps the equivalents are **tokens, latency, GPU utilisation, and hallucination rate** — because the output is unstructured text, not a number you can score with a formula.

---

## Key Takeaways

1. **Tracing turns a black box into a glass box** — one request, every step, with timings, reviewable after the fact.
2. **The trace ID is a parcel tracking number** — it's what lets you follow a single complaint through thousands of log lines.
3. **LangSmith for the LangChain ecosystem; Opik or Langfuse otherwise** — that's the selection rule from the session.
4. **Integration is configuration, not code** — `LANGSMITH_TRACING=true` plus keys, because every LangChain component shares the same `Runnable` interface.
5. **Traces reveal where time actually goes** — in the worked example, the Wikipedia tool ate 4.39s of a 7.30s request, not the model.
6. **Tracing ≠ evaluation.** LangSmith traces brilliantly and evaluates adequately; use DeepEval, Ragas, or TruLens when scoring quality is the point.

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

### Q1: What's the difference between LangSmith, Opik, and Langfuse, and when would you prefer each?

**The one-liner for each:**

- **LangSmith** — LangChain's own tool. Zero-setup if you're inside LangChain/LangGraph, but proprietary and by far the most expensive at scale.
- **Langfuse** — the open-source, framework-agnostic default. Broadest integrations, cheapest to run.
- **Opik** — open-source too, but bets on **automated evaluation and prompt optimisation** rather than just logging.

**The cost difference is what actually decides it** (figures as of 2026):

| | Licence | Self-host | Free tier | ~1M traces/month |
|---|---|---|---|---|
| **LangSmith** | Proprietary | Enterprise plan only | 5k traces | **~$2,514/mo** |
| **Langfuse** | MIT | Free | 50k units/mo | **~$101/mo** |
| **Opik** | Apache-2.0 | Free | — | self-host cost only |

Roughly a **25× gap** between LangSmith and Langfuse at a million traces. Irrelevant for a hobby project; the whole conversation for anything real.

**What each is genuinely best at:**

- **LangSmith** — you're committed to LangChain/LangGraph and want it to *just work*. Tracing turns on with `LANGSMITH_TRACING=true` (see Section 4), plus Prompt Hub and annotation queues with zero assembly. The catch: proprietary, so self-hosting requires Enterprise, and cost climbs steeply with volume.
- **Langfuse** — mixed stack, or you want to own your data. MIT-licensed with genuinely free self-hosting and the broadest integration surface. Backed by ClickHouse (the database company) as of January 2026, which matters for infrastructure confidence. Prompt management is manual — versioning and dashboards, not auto-tuning.
- **Opik** — you want the tool to *improve* things, not just record them. Its differentiator is a built-in **Agent Optimizer with seven optimisation algorithms**, plus online evaluation on live production traffic (see the sibling `Opik/Opik - Notes.md`). A genuinely different pitch from the other two.

**The decision rule:**

1. **All-in on LangChain/LangGraph, modest volume?** → LangSmith. The zero-assembly convenience is real.
2. **Mixed stack, or cost/data-ownership matters?** → Langfuse. The safe default.
3. **Want automated prompt/agent tuning, not just observability?** → Opik.

This refines the session's own simpler rule from Section 2 — *"LangSmith if you're in the LangChain ecosystem, Opik or Langfuse if you're not"* — which is right as far as it goes, but doesn't separate Opik from Langfuse. The separator is that **Opik optimises, Langfuse observes.**

**One line:** LangSmith buys convenience inside the LangChain ecosystem at a steep price, Langfuse is the open-source framework-agnostic default that's ~25× cheaper at scale, and Opik is the one that actively tunes prompts and agents rather than only recording what happened.

**Sources:**
- [Langfuse vs LangSmith (2026): Pricing Math, Self-Host, and Lock-In Settled — Morph](https://www.morphllm.com/comparisons/langfuse-vs-langsmith)
- [Opik vs Langfuse: Self-Hosted LLM Observability in 2026 — AgenticWire](https://www.agenticwire.news/article/langfuse-vs-opik)
- [LangSmith Alternatives (2026): Open Source, Self-Host, and Cost at Scale — Morph](https://www.morphllm.com/comparisons/langsmith-alternatives)
- [LangSmith Alternative: Langfuse vs. LangSmith — Langfuse](https://langfuse.com/faq/all/langsmith-alternative)

# Prefect — Notes

Condensed notes from the TMLC reading *Prefect: Why Only Orchestrate LLM Workflows?*, with context from the session transcript (*LLMOps - Transcript.md* in the `LLMOps Overview` folder). Source PDF sits alongside this file.

**The core idea in plain words:** an LLM system isn't just "answer the user's question." There's also fetching new data, cleaning it, re-embedding it, fine-tuning, evaluating, comparing against a baseline — work that has to happen **on a schedule, reliably, with nobody watching**. Prefect is the thing that runs that work: it schedules it, retries it when a step fails, and shows you a dashboard of what ran and what broke.

> 🍳 **The analogy that makes this click:** LangGraph is the kitchen cooking your dish *while you sit at the table waiting*. Prefect is the **overnight prep crew** — restocking the pantry, making stock, receiving deliveries — so that tomorrow's kitchen has what it needs. Same restaurant, completely different shift, and neither can do the other's job.

That distinction is the single most important thing in this file, so §6 is devoted to it.

---

## 1. Why Orchestration at All?

The reading's framing: working with LLMs "is not just about inference." The lifecycle includes data ingestion, preprocessing, fine-tuning, evaluation, and deployment — and it's **not a one-time process**, it needs continuous refinement. Once those workflows grow, managing them by hand becomes impractical.

The transcript adds a sharper version of *when* you need this:

> LangChain, LlamaIndex and similar frameworks already orchestrate "LLM stuff" efficiently. But if you're **not** using an external framework — you built your own memory stored in your own database, you call your LLM from your own services — then you need to orchestrate the overall workflow yourself: when input comes in, what gets called first, how memory gets accessed.

Tools in this space: **Airflow, Prefect, Mage**. The transcript's practical note on choosing: Prefect "doesn't require something very extra" — `pip install prefect`, write a `.py` script, and run it — whereas **Airflow "might be a bit tough to get installed."**

---

## 2. Five Places Prefect Earns Its Keep

**1. Scheduled fine-tuning and retraining.** Models need periodic fine-tuning on new data to stay relevant.
> *Example from the reading:* an e-commerce platform fine-tunes its recommendation model **every week** on new user interactions. Prefect schedules it with no manual intervention.

**2. Data pipeline management.** Preprocessing at scale is several steps with dependencies between them:
- **Data extraction** — pulling from APIs, databases, cloud storage
- **Data cleaning** — removing inconsistencies, duplicates, missing values
- **Data augmentation** — synthetic or translated data
- **Tokenization and preprocessing** — converting text into training-ready format

Prefect maintains the dependencies and adds fault tolerance: **if one step fails it retries or alerts the team, without disrupting the entire pipeline.**

**3. Model evaluation and drift detection.** Models degrade as input distribution shifts away from training data. Prefect can automate evaluation runs on a schedule, compute accuracy/perplexity/other metrics, **compare new performance against a baseline**, and trigger alerts or rollbacks when degradation crosses a threshold.
> *Example from the reading:* fraud detection, where evolving fraud patterns demand continuous retraining and evaluation.

**4. Inference pipeline optimization.** Orchestrating model loading and caching, **A/B testing** (routing different requests to different model versions), and latency monitoring.
> *Example from the reading:* an AI customer-support system that switches between smaller, faster models for routine queries and larger models for intricate ones.

**5. Multi-step agent workflows.** For agents making multiple model calls — **RAG systems explicitly named** — Prefect ensures steps run sequentially or in parallel as needed, handling retries and failures gracefully across multiple APIs, embeddings, and models.

> ⚠️ Scenario 5 is exactly where Prefect and LangGraph *look* like they overlap. §6 resolves it.

---

## 3. Prefect vs. Airflow

| | Airflow | Prefect |
|---|---|---|
| **DAGs** | Static — defined up front | **Dynamic** — workflow shape can be decided at runtime, better for AI experimentation |
| **Resilience** | Available, more manual | **Built-in state management** — retry or restart from the last successful checkpoint |
| **Execution** | Typically one environment | **Hybrid** — on-premise *and* cloud |
| **API** | Heavier | **Pythonic** — plain decorators, easy to drop into existing ML pipelines |
| **Install** | "A bit tough to get installed" (transcript) | `pip install prefect` |

> 🔁 **"Restart from the last successful checkpoint"** is worth connecting to something you already know: it's the same idea as LangGraph's **checkpointer** (Week 3, Interview Q11) and CrewAI Flows' **`@persist`** — save state after each completed step so a crash doesn't mean starting over. Three different tools, one shared instinct.

---

## 4. The Code

The reading's worked example — automating periodic LLM fine-tuning:

```python
from prefect import flow, task
import os

@task(retries=3, retry_delay_seconds=60)
def load_new_data():
    # Fetch new training data
    print("Fetching latest dataset...")
    return "path/to/new/data.csv"

@task(retries=3, retry_delay_seconds=120)
def fine_tune_model(data_path):
    # Fine-tune the LLM on the latest dataset
    print(f"Fine-tuning model with data from {data_path}")
    # Fine-tuning code
    return "path/to/fine-tuned-model"

@task
def evaluate_model(model_path):
    # Run evaluation metrics after fine-tuning
    print(f"Evaluating model performance for {model_path}")
    # Evaluation code

@flow
def llm_finetuning_workflow():
    data_path = load_new_data()
    model_path = fine_tune_model(data_path)
    evaluate_model(model_path)

if __name__ == "__main__":
    llm_finetuning_workflow.serve(name="llm-retraining",
        cron="0 0 * * 6",   # runs every Saturday at midnight
    )
```

**What each piece does:**

| Piece | Meaning |
|---|---|
| `@task(retries=n, retry_delay_seconds=k)` | Marks the function a Prefect **Task**. Retries **n** times on failure, waiting **k** seconds between attempts. |
| `@flow` | Marks a function a Prefect **Flow** — the high-level container that holds tasks. |
| `.serve(name="llm-retraining", cron="0 0 * * 6")` | Registers the flow and runs it **every Saturday at midnight**, keeping it continuously available for execution. |

**Reading the cron string `0 0 * * 6` plainly:** minute `0`, hour `0`, any day of month, any month, day-of-week `6` → **midnight on Saturday**.

**Notice the retry asymmetry** — it's deliberate, not decoration. `load_new_data` waits **60s** between retries; `fine_tune_model` waits **120s**. A failed data fetch is usually a blip worth retrying quickly; a failed fine-tune is expensive and probably needs longer for whatever went wrong (GPU contention, memory) to clear.

---

## 5. Running It

Two commands, in this order:

**1. Start the server**

```bash
prefect server start
```

- The central hub for managing and monitoring workflows — provides both a **UI** and a **backend** tracking executions, logs, and scheduling.
- Reachable at `http://127.0.0.1:4200` or `http://localhost:4200`.
- **Keep this terminal running** — the server has to stay up.

**2. Run your script**

```bash
python <filename>.py
```

- Executes the script containing your flow and tasks.
- The `.serve()` call **registers the workflow with the server** and keeps it polling for scheduled runs.
- **The Prefect server must already be running** before you execute this.

Output confirms it's live, and gives you a manual trigger command:

```
Your flow 'llm-finetuning-workflow' is being served and polling for scheduled runs!

To trigger a run for this flow, use the following command:

    $ prefect deployment run 'llm-finetuning-workflow/llm-retraining'
```

**In the UI:** go to **Deployments** to see the registered workflow, its schedule ("At 12:00 AM, only on Saturday"), and status. To run it now rather than waiting for Saturday: **Run → Quick Run**.

A completed run shows the task graph in sequence, with timings:

```
load_new_data-2d2  →  fine_tune_model-b3c  →  evaluate_model-663        ✅ Completed  3s
```

Errors during a run are highlighted in the run view — scroll down for logs.

---

## 6. Prefect vs. LangGraph — The Distinction That Actually Matters

You've spent a lot of time on LangGraph, and both tools involve tasks, state, retries, and a DAG-ish shape. That resemblance is genuinely misleading. **They operate on different timescales, with different triggers.**

| | **LangGraph** | **Prefect** |
|---|---|---|
| Triggered by | A **user request** | A **schedule** (cron), or a manual/event trigger |
| Timescale | Milliseconds to seconds | Minutes to hours |
| Is anyone waiting? | **Yes** — a user is watching a spinner | **No** — it's a background job |
| Scope of state | One conversation (`thread_id`) | One pipeline run |
| Typical job | retrieve → rerank → generate, maybe loop back | re-embed the corpus, fine-tune, evaluate, compare to baseline |
| Failure means | The user gets a bad answer *now* | Tomorrow's index is stale |

**The one-line test:** *is a user waiting for this to finish?* If yes → LangGraph (in-request control flow). If no → Prefect (scheduled batch orchestration).

**They nest, and that's the cleanest way to hold it.** A Prefect flow can call a LangGraph pipeline once per item:

```
Prefect flow (runs nightly at 02:00)
  └─ task: fetch new documents
  └─ task: for each of 10,000 docs → run the LangGraph ingestion graph
  └─ task: rebuild the index
  └─ task: run the eval suite, compare against last week's baseline
  └─ task: alert if faithfulness dropped below threshold
```

Prefect owns the *outer, scheduled, batch* loop. LangGraph owns the *inner, per-item, request-shaped* loop.

> 🔗 **The most concrete connection to prior weeks:** Week 3's *Current State of RAG* flagged **"index staleness in dynamic corpora"** as a real failure mode, with the fix being **incremental indexing with TTL-based cache invalidation**. That fix describes *what* should happen — a scheduled job that re-checks sources and re-embeds only what changed. **Prefect is what actually runs it.** Likewise, `Finetuning_Embeddings_Model.ipynb` from Week 3 was run by hand; in production, that's a Prefect flow on a cron.

---

## Key Takeaways

1. **Prefect runs the work nobody is waiting for** — scheduled fine-tuning, nightly re-embedding, drift evaluation.
2. **Two decorators is the whole mental model** — `@task` for a step (with retries), `@flow` for the container.
3. **`.serve(name=..., cron=...)` registers and schedules it**; `prefect server start` must be running first.
4. **Retries are per-task and tunable** — quick retries for cheap steps, long delays for expensive ones.
5. **Prefect over Airflow** for AI work: dynamic DAGs, built-in checkpoint resilience, hybrid execution, and a far easier install.
6. **Prefect ≠ LangGraph.** Ask "is a user waiting?" — if yes it's LangGraph, if no it's Prefect. They nest: Prefect schedules the batch, LangGraph handles each item.
7. **This is the answer to index staleness** from Week 3 — the fix was "incremental indexing on a schedule," and Prefect is the scheduler.

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape:

- The heading is the question **as asked** — often phrased as a statement to confirm.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- Earlier answers are referred back to ("from Q1") so the picture stays connected.
- A bolded **One line:** summary closes the answer, restating the whole thing in a single sentence.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

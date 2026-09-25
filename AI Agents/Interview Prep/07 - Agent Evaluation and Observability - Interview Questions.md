# Agent Evaluation and Observability — Interview Questions

*Built from* Agent Evaluation and Observability - Transcript.md *and the Week 6 LLMOps material.*

*Scoped to **measuring agents** — what to measure, how to measure non-deterministic systems, and where LLM-as-judge lets you down. Production serving concerns are `08`. Two-layer answers throughout.*

---

**🎙️ Interview Q1:** "Evaluating a RAG system is hard enough. What makes evaluating an agent harder?"

**✅ Strong answer:** "Three things, and they compound.

**There's no single correct path.** A RAG pipeline always does the same steps, so you check the output. An agent might reach a correct answer in three steps or eleven, using different tools each time. Both can be right — so 'did it match the expected output' is no longer sufficient.

**You have to evaluate the trajectory, not just the answer.** An agent can produce the right answer through a terrible path — fifteen steps, four failed tool calls, twenty dollars of tokens. Output-only evaluation scores that as a pass.

**Failures are attribution problems.** When the answer is wrong, the cause could be tool selection, tool output, context management, or reasoning. The visible symptom is at the end; the cause is usually in the middle.

So agent evaluation is really two questions: **did it get there, and was the path reasonable?**"

**🎯 Standard Interview Answer:** "Three factors. Non-unique solution paths invalidate exact-match evaluation, since multiple distinct trajectories may be equally correct. Trajectory quality is an independent quality dimension from terminal correctness — an agent may produce correct output via an inefficient or error-laden path, which output-only evaluation scores as success while the production cost and latency are unacceptable. And multi-stage execution makes failure attribution non-trivial, since the observable defect is terminal while the causal fault is typically intermediate. Agent evaluation therefore requires joint assessment of goal completion and trajectory quality, with per-span scoring to enable attribution."

---

**🎙️ Interview Q2:** "What's the difference between observability and evaluation?"

**✅ Strong answer:** "**Observability is operational; evaluation is about correctness.** Different metrics, different audiences, different alerts.

| Observability | Evaluation |
|---|---|
| Latency p50/p95/p99 | Goal completion |
| Token spend | Faithfulness / hallucination rate |
| Error rate | Tool-selection accuracy |
| Trace count, span depth | Trajectory efficiency |
| Time to first token | Format compliance |

**Everyday example:** observability tells you the restaurant served 200 covers in 90 minutes with two complaints. Evaluation tells you whether the food was any good.

You need both, and they fail differently. A system can be fast, cheap and completely wrong — observability will say everything is green. Or it can be accurate and unusably slow, which evaluation won't catch.

The other distinction: observability runs continuously in production; evaluation runs against datasets, usually in CI, plus a sampled subset online."

**🎯 Standard Interview Answer:** "Observability captures operational telemetry — latency percentiles, token consumption, error rates, span-tree structure, time-to-first-token — and runs continuously against production traffic. Evaluation captures correctness — goal completion, faithfulness, tool-selection accuracy, trajectory efficiency, format compliance — and runs against curated datasets in CI plus sampled online evaluation. They are non-substitutable: a system can be operationally healthy and semantically wrong, which observability will not surface, or semantically correct and latency-noncompliant, which offline evaluation will not surface."

---

**🎙️ Interview Q3:** "What metrics would you actually track for an agent?"

**✅ Strong answer:** "I'd split them into three groups so nothing gets missed:

**Did it work?**
- Goal completion rate — the headline number
- Task success by category, because averages hide that one input type fails 40% of the time

**Was the path sensible?**
- Tool-selection accuracy — right tool for the step
- Tool-argument correctness — right tool, wrong arguments is a distinct and common failure
- Trajectory efficiency — actual steps versus minimum needed
- Loop rate — how often it repeats a failing action

**What did it cost?**
- Tokens per task, and p95 not just mean
- Latency p50/p95/p99
- Human escalation rate

The one people forget is **tool-argument correctness.** Everyone measures whether the right tool was chosen; far fewer check whether the arguments were right. A search tool called with a garbled query looks like a successful tool call in the trace and produces a wrong answer downstream."

**🎯 Standard Interview Answer:** "Three metric families. Outcome: goal completion rate, and task success segmented by input category since aggregate rates mask category-specific failure. Trajectory: tool-selection accuracy, tool-argument correctness as a distinct measure, trajectory efficiency as realised versus minimal step count, and loop or repeated-failure rate. Cost: tokens per task at both mean and p95, latency percentiles, and human escalation rate. Tool-argument correctness is commonly omitted despite being a frequent failure mode — a correctly selected tool invoked with malformed arguments registers as a successful span while corrupting downstream reasoning."

---

**🎙️ Interview Q4:** "Explain LLM-as-a-judge and its failure modes."

**✅ Strong answer:** "LLM-as-judge is using a model to score outputs that no formula can check — 'is this answer faithful to the context?', 'is this tone appropriate?'. You give the judge a rubric and it returns a score.

It's genuinely useful and it's how most agent evaluation works at scale. But it has documented biases, and naming them is what separates a good answer from a shallow one:

**Position bias.** In pairwise comparison, judges favour the first-presented answer roughly 60–65% of the time regardless of quality. **Mitigation:** run each comparison twice with the order swapped and only accept the verdict when both runs agree.

**Self-preference.** A judge tends to rate its own model family's output more highly. **Mitigation:** use a different model family as judge than the one being evaluated.

**Verbosity bias.** Longer answers get scored higher even when padded.

**Leniency drift.** Judges cluster around 'good' unless the rubric forces discrimination with concrete anchors.

The overarching mitigation is **calibration against human labels.** Score a couple of hundred examples by hand, check the judge agrees, and measure that agreement. An uncalibrated judge is a number you can't interpret."

**🎯 Standard Interview Answer:** "LLM-as-judge applies a model to score qualities not amenable to programmatic verification — faithfulness, relevance, tone, rubric adherence. Documented systematic biases: position bias, with first-presented options favoured at approximately 60–65% in pairwise settings, mitigated by order-swapped double evaluation with agreement as an acceptance condition; self-preference toward the judge's own model family, mitigated by cross-family judge selection; verbosity bias correlating length with score; and leniency drift toward the positive end absent concrete rubric anchors. The controlling requirement is calibration against human-labelled ground truth on a held-out sample, with inter-rater agreement measured and reported — an uncalibrated judge produces scores of unknown validity."

---

**🎙️ Interview Q5:** "How do you build an evaluation dataset for an agent when you have no ground truth?"

**✅ Strong answer:** "The realistic path is bootstrapping, in three stages:

**Start from production traces.** You don't need pre-existing labels — you need real inputs. Pull actual queries from traces, including the ones that failed.

**Have a human label a small set.** A domain expert reviews maybe 50–100 real traces and marks them correct or not, with a reason. This is the expensive step and it's unavoidable — this is your ground truth.

**Generate synthetic cases to broaden coverage,** then have a human verify them. Synthetic-only datasets drift from real usage; LLM-drafted, human-verified is the practical compromise.

Two things I'd add. **Deliberately include failure cases** — empty tool results, ambiguous queries, out-of-scope requests — because those are where agents break and a happy-path dataset gives false confidence. And **stratify by category**, so you can see that billing queries pass 95% while returns queries pass 60%, which an aggregate hides.

The rule of thumb from current practice is a private evaluation set of roughly 500–1,500 examples before trusting a deployment decision."

**🎯 Standard Interview Answer:** "Bootstrap from production telemetry rather than attempting dataset construction de novo. Extract real input distributions from traces including failure cases; obtain human labels on a sample of 50–100 traces with rationale, establishing ground truth — this step is irreducible; then expand coverage via synthetic generation with human verification, since purely synthetic sets diverge from production distribution. Deliberately include degraded-path cases — empty retrievals, ambiguous or out-of-scope inputs — as happy-path-only datasets systematically overstate reliability. Stratify by input category to expose category-specific failure masked by aggregate metrics. Current practice suggests 500–1,500 examples in a private evaluation set as the threshold for deployment decisions."

---

**🎙️ Interview Q6:** "Your agent's answer is wrong. Walk me through finding the cause."

**✅ Strong answer:** "**Open the trace** — without per-step traces this is guesswork, so if tracing is missing that's the real answer.

With a trace, I work cheapest-check-first:

1. **Look at the final answer versus the last tool result.** If the tool returned the right data and the answer is wrong, it's a generation problem. If the tool returned nothing useful, it's upstream.
2. **Check tool selection.** Right tool for that step?
3. **Check tool arguments.** Right tool, wrong query is extremely common.
4. **Check tool output validity.** Silent degradation — an API returning an empty list rather than an error — is the nastiest because everything looks green.
5. **Check step count and context size.** Loops, or the objective buried mid-context.
6. **Only then** the model or prompt.

The thing to say explicitly: **you're looking for the first span where the input was fine and the output wasn't.** That's the faulty stage. Everything after it is downstream damage, and tuning those prompts wastes time."

**🎯 Standard Interview Answer:** "Trace-driven attribution, proceeding from terminal span backward to locate the first span with valid input and invalid output — that span is the fault site, and subsequent anomalies are propagated consequences. Inspection order by diagnostic cost: terminal answer against final tool result to separate generation failure from upstream failure; tool selection correctness; tool argument correctness; tool output validity including silent degradation where structurally valid but semantically empty responses are returned; trajectory length and context growth to detect loops and positional degradation of the objective; and model or prompt quality last. Remediating downstream spans is a common misallocation of effort."

---

**🎙️ Interview Q7:** "What does a trace actually contain for an agent, and what's a span?"

**✅ Strong answer:** "A **trace** is one complete request end to end. A **span** is one unit of work inside it — a single LLM call, a single tool call, a retrieval. Spans nest, so a trace is really a tree.

For an agent, the trace should capture, per span: inputs and outputs, latency, token counts and cost, tool name and arguments, errors, and which step of the loop it was.

**Everyday example:** the trace is the parcel's full journey from warehouse to door; each span is one scan along the way. Without the scans you know only that it's late, not where it's stuck.

The concrete payoff: I've seen a trace where total latency was 7.30 seconds and a single Wikipedia tool call accounted for 4.39 of it — about 60%. Without the span breakdown you'd start optimising the prompt, which would have changed nothing.

Worth mentioning: **OpenTelemetry now has GenAI semantic conventions** (`gen_ai.*` attributes), so tracing is becoming vendor-neutral — though as of mid-2026 none of those attributes are marked stable yet, so pin your versions."

**🎯 Standard Interview Answer:** "A trace represents one end-to-end request; spans are nested units of work within it — individual model invocations, tool calls, retrievals — forming a tree. Per-span capture should include inputs, outputs, latency, token counts and cost, tool identity and arguments, error state, and loop iteration index. The diagnostic value is latency and cost attribution: in one instrumented example a 7.30-second trajectory attributed 4.39 seconds, approximately 60%, to a single tool call, which would be invisible to aggregate latency monitoring and would misdirect optimisation toward prompt tuning. OpenTelemetry GenAI semantic conventions provide a vendor-neutral attribute schema under the `gen_ai.*` namespace, though no attributes were marked stable as of mid-2026, so version pinning is advisable."

---

**🎙️ Interview Q8:** "How do you evaluate continuously in production rather than only offline?"

**✅ Strong answer:** "Offline evaluation tells you about the inputs you thought of. Production shows you the ones you didn't — so you need both, and they connect.

**Online evaluation:** sample a percentage of live traces and run judge metrics against them automatically. You don't score everything — that doubles your inference cost — you sample, and you oversample the suspicious ones: high step count, escalations, thumbs-down.

**Capture implicit feedback.** Explicit ratings are rare. Signals people actually give: the user rephrasing the same question immediately, abandoning the session, or escalating to support. A rephrase is a strong negative signal and it's free to collect.

**Close the loop.** Failed production traces become new evaluation cases. That's what stops your dataset going stale.

**Run the suite in CI.** Regression on a prompt change should fail the build, not reach a customer.

The metric–production gap to name: **your offline scores can improve while user satisfaction drops**, because your dataset stopped resembling reality. Continuously refreshing it from production is the only defence."

**🎯 Standard Interview Answer:** "Offline evaluation covers anticipated input distribution; production coverage requires online evaluation. Implement sampled online scoring — applying judge metrics to a traffic fraction rather than full traffic, with biased sampling toward anomalous trajectories such as high step count, escalation or negative feedback. Capture implicit feedback signals, notably immediate query reformulation, session abandonment and escalation, which have far higher collection rates than explicit ratings and where reformulation is a strong dissatisfaction indicator. Close the loop by promoting failed production traces into the evaluation set, preventing dataset staleness. Integrate the suite into CI with threshold-based build failure. The governing risk is the metric–production gap, where offline scores improve while production satisfaction degrades because the evaluation distribution has diverged from live traffic; continuous dataset refresh from production is the mitigation."

---

**🎙️ Interview Q9:** "What's the single most important thing to instrument if you can only do one?"

**✅ Strong answer:** "**Per-span tool calls with their arguments and results.**

Reason: tool interaction is where agents actually fail. Reasoning errors are less common than tool-selection errors, malformed arguments, and tools quietly returning nothing useful. If I have the tool call, its arguments, and what came back, I can diagnose the large majority of real failures.

Everything else is a distant second. Latency and token counts matter for operations, but they tell you a system is expensive, not why it's wrong.

If I could have a second thing, it'd be **step count per task** — cheap to collect and it surfaces loops immediately."

**🎯 Standard Interview Answer:** "Per-span tool invocation records comprising tool identity, arguments and returned payload. Tool interaction is the dominant failure surface — selection error, argument malformation and silent tool degradation collectively exceed pure reasoning failure in production incidence — and this instrumentation is sufficient to diagnose the majority of defects. Secondary priority is per-task step count, which is inexpensive to capture and directly exposes non-termination and loop conditions. Latency and cost telemetry address operational rather than correctness concerns and are lower priority under a single-instrument constraint."

---

## Sources

- [Top 30 AI Agent Observability Interview Questions and Answers — Medium](https://skphd.medium.com/top-30-ai-agent-observability-interview-questions-and-answers-d390b2757e1a)
- [AI Agent Evaluation (2026): Metrics, Frameworks, and Production Failures — Morph](https://www.morphllm.com/ai-agent-evaluation)
- [AI Agent Evaluation & Observability (2026) — TechJack](https://techjacksolutions.com/ai-knowledge-hub/agent-evaluation-and-observability/)
- [Agent Observability vs Evaluation vs Benchmarking (2026) — Future AGI](https://futureagi.com/blog/agent-observability-vs-evaluation-vs-benchmarking-2026/)
- [LLM-as-a-Judge in 2026: Top evaluation techniques — DeepEval](https://deepeval.com/blog/llm-as-a-judge)
- [LLM-as-a-Judge — Langfuse](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge)
- [CalibraEval: Calibrating Prediction Distribution to Mitigate Selection Bias in LLMs-as-Judges (arXiv)](https://arxiv.org/pdf/2410.15393)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)

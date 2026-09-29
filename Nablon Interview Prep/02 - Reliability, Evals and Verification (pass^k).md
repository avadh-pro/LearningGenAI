# Reliability, Evals & Verification — Interview Questions

*JD pillars: "Own the eval, verification, and decision-trace strategy that gets the system to 99.99%" and "Own rubric scoring, tiered policy enforcement, drift detection, and production gating to a **pass^k** reliability bar."*

> **This is the highest-signal file in the pack.** The JD literally names *pass^k*. Most candidates will discuss *pass@k* and quietly get it backwards. Getting this right is the single clearest way to read as the senior they're hiring.

---

**🎙️ Q1: "The JD says 'pass^k reliability bar.' What's the difference between pass@k and pass^k, and why does it matter here?"**

**✅ Strong answer:** "They sound similar and mean opposite things.
- **pass@k** = the probability the agent succeeds **at least once** in k attempts. It's a *capability* measure — good for asking 'can the model ever do this?'
- **pass^k** = the probability the agent succeeds on **all k** attempts. It's a *reliability* measure — 'will it do this consistently, unsupervised, every time?'

The gap is brutal and it's why the distinction matters. Take a task with a 70% single-run success rate. pass@3 looks great — about 97% chance of at least one success. But pass^3 is 0.7³ ≈ **34%** — the chance it handles three consecutive requests without a failure. Same agent, same task; one number says 'ship it,' the other says 'nowhere near.'

For a Fortune 500 workflow running unsupervised at scale, the user experiences *every* run, so pass^k is the honest bar. And 99.99% under pass^k is savage: if you need 0.9999 across a 10-step workflow, each step needs roughly 0.99999 reliability. You do not get there by prompting. You get there by **removing steps from the agentic path, verifying before every irreversible action, and gating.**"

**🎯 Senior signal:** "pass@k measures peak capability and is dangerously misleading for autonomous production agents; pass^k measures the consistency the user actually experiences. The architectural consequence is that reliability is a *product* over steps, so the two highest-leverage moves are (1) reduce the number of non-deterministic steps — every deterministic step is a factor of 1.0 — and (2) add verification gates that catch the failing tail before it acts. A corollary I'd raise: pass^k at 99.99% is often infeasible for a fully-autonomous path, which is exactly why escalation/HITL is in the architecture — a calibrated human gate on the low-confidence tail is how you make the number real."

---

**🎙️ Q2: "Design the eval control plane for an engagement — rubric scoring, tiered policy, drift detection, production gating. What are the pieces?"**

**✅ Strong answer:** "Four connected pieces:

1. **Rubric scoring** — a versioned set of criteria per task, scored by a mix of *deterministic checks* (schema, policy constraints, ground-truth match where it exists), *model-based judges* (faithfulness, correctness against context), and *human review* for the calibration set. Each dimension scored separately so failures are attributable.

2. **Tiered policy enforcement** — not every check is equal. Critical contracts (regulatory, irreversible-action safety) are hard gates that block deployment or execution on any failure. Softer quality metrics have regression floors. Tiering is what lets you move fast on quality without ever risking a compliance breach.

3. **Drift detection** — production input distribution drifts, and the LLM-judge itself drifts as models update. So: monitor input-distribution shift, output-quality shift, and periodically re-calibrate the judge against fresh human labels.

4. **Production gating** — the release gate. Eval scores become an automated pass/fail: a metric below its floor blocks the merge/deploy; a critical contract failure blocks it hard. This is what makes 'quality built in, not bolted on' literally true — you cannot ship past the gate.

The whole thing is a control loop: offline eval gates releases, online eval samples production, drift alerts trigger re-calibration, and failures become new eval cases."

**🎯 Senior signal:** "The control plane is what operationalises the reliability bar — it turns 'we think it's good' into an enforced pass/fail. The two subtleties that mark seniority: **judge validation** (you must audit the judge for position bias, self-preference and leniency drift, and calibrate against human labels, or your gate is measuring noise) and the **metric–production gap** (offline scores can rise while production satisfaction falls when the eval set stops resembling reality — so the eval set must be continuously refreshed from production traces)."

---

**🎙️ Q3: "How do you evaluate a non-deterministic system at all? A single passing run tells you nothing."**

**✅ Strong answer:** "Right — one run is meaningless, so the whole approach is statistical and repeated:
- **Run k times, report pass^k**, not a single result. Reliability is the distribution, not a point.
- **Golden dataset + LLM-as-judge against a rubric**, scored per dimension, calibrated against human labels, run in CI.
- **Separate trajectory from outcome** — an agent can reach a right answer through a terrible 15-step path with four failed tool calls. Score both goal-completion *and* trajectory quality (tool-selection accuracy, tool-argument correctness, step efficiency, loop rate).
- **Per-run traces** (nested spans) so a failure is attributable to a stage, not just observed at the end.
- **Deliberately include failure cases** — empty tool results, ambiguous inputs, out-of-scope requests — because happy-path-only evals systematically overstate reliability.

The philosophy: you can't make the core deterministic, so you build a deterministic *framework* of measurement and gates around it."

**🎯 Senior signal:** "The interviewer is checking whether you can engineer a stable, deterministic framework around a fundamentally non-deterministic core — that exact phrasing is what they want. The senior addition is CI integration with a train/validation/test split on your eval set, so you're not overfitting prompts to the cases you look at, plus stratification by input category so a 95% aggregate doesn't hide a 60% pass rate on the one query type that matters to the client."

---

**🎙️ Q4: "What's a decision trace, and why does the JD treat it as strategic rather than just logging?"**

**✅ Strong answer:** "A decision trace is the full, structured record of one workflow run: the inputs, every retrieval and tool call with arguments and results, every model decision with its reasoning and confidence, escalations, and the final action — as a nested span tree.

It's strategic, not just logging, because at Nablon it's the **fuel for the compounding loop**:
- In a regulated environment it's the **audit trail** — you can reconstruct exactly why the system did what it did.
- It's the raw material for **eval cases** — real production runs, especially failures and escalations, become the golden dataset.
- It's the raw material for **RL environments** — traces become the states/actions/rewards you train the domain-tuned model on.

So the same artifact serves compliance, evaluation, and training. That triple-duty is why it's a first-class part of the stack, not an afterthought."

**🎯 Senior signal:** "The trace is the single artifact that connects observability, audit, evaluation, and RL — design its schema deliberately because everything downstream reads from it. The failure I'd flag is under-capturing: if you don't log confidence, tool arguments, and the *rejected* alternatives at decision points, you can't build good eval cases or assign credit in RL later. Trace schema is an architecture decision made on day one, because you can't retro-fit signal you didn't capture."

---

**🎙️ Q5: "You're asked to get a workflow from 95% to 99.99%. Walk me through it."**

**✅ Strong answer:** "95% to 99.99% is closing a 500× gap in failure rate, so incremental prompt-tuning won't do it. My approach:
1. **Measure honestly first** — pass^k over real production distribution, stratified by input type, with per-step traces. Find *where* the 5% fails, because it's rarely uniform.
2. **Attribute failures** — is it retrieval, tool selection, tool degradation, reasoning, or a specific input segment? Usually a small number of failure modes dominate.
3. **De-agentify the fixable-deterministically** — any failing step that's actually a rules problem becomes code. Instant reliability gain and it shrinks the multiplicative chain.
4. **Add verification gates** before irreversible actions — catch the failing tail before it acts, converting a wrong action into a caught-and-escalated one.
5. **Calibrated escalation on the residual tail** — the last fraction of a percent you cannot get autonomously, you route to a human by confidence threshold. This is how the number becomes real without pretending full autonomy.
6. **Close the loop** — every caught failure becomes an eval case and RL data so the ceiling rises over time.

I'd be honest with the client that the path to 99.99% almost always includes a human gate on the low-confidence tail — anyone promising full autonomy at that bar is overselling."

**🎯 Senior signal:** "The reframe that matters: 99.99% is a *system* property achieved by verification and escalation, not a *model* property achieved by tuning. The compounding-reliability math (per-step reliability multiplies) forces you toward fewer non-deterministic steps and gates on the tail. And I'd set the expectation explicitly with client leadership — the honest architecture trades a sliver of autonomy for the reliability bar, and saying so builds more trust than promising a fully-autonomous 99.99%, which doesn't exist."

---

**🎙️ Q6: "How do you validate the LLM-as-judge itself? If the grader is wrong, the gate is meaningless."**

**✅ Strong answer:** "You treat the judge as a system under test:
- **Calibrate against human labels** — score a few hundred examples by hand, measure the judge's agreement (correlation / Cohen's kappa) with humans, and only trust the gate if agreement is high enough.
- **Audit for known biases** — *position bias* (favours the first option ~60–65% in pairwise; mitigate by running order-swapped and accepting only on agreement), *self-preference* (rates its own model family higher; use a different family as judge), *verbosity bias* (longer = higher; control for length), and *leniency drift* (clusters toward 'good' without concrete rubric anchors).
- **Re-calibrate on a schedule** — judge behaviour drifts as the underlying model updates, so calibration isn't one-time.
- **Prefer deterministic checks where they exist** — don't use a judge for anything a schema or a policy rule can verify exactly."

**🎯 Senior signal:** "An uncalibrated judge produces scores of unknown validity, so judge-validation is a precondition for the whole control plane, not a nicety. The mature version keeps a standing human-labelled calibration set, tracks judge–human agreement as a monitored metric over time, and alerts when it decays — because a judge that silently drifts turns your production gate into theatre while every dashboard stays green."

---

**🎙️ Q7: "Drift detection — what exactly are you monitoring, and what do you do when it fires?"**

**✅ Strong answer:** "Three distinct kinds of drift:
- **Input drift** — production inputs diverge from your eval distribution (new query types, new document formats, a new client subsidiary). Monitor input-feature/embedding distribution shift.
- **Output/quality drift** — quality metrics decline over time even on similar inputs, often from an upstream dependency changing or a model update.
- **Judge drift** — the evaluator's own scoring shifts as its model updates.

When it fires: alert, sample and inspect the drifted traces, refresh the eval set with the new distribution, re-calibrate the judge if needed, and if quality breached a floor, gate/roll back. The key is that drift is *expected*, not an edge case — the control loop runs continuously precisely because production never stops moving."

**🎯 Senior signal:** "The senior point is that drift detection is what keeps the offline eval honest — without it, the metric–production gap widens invisibly until a client incident. I'd wire drift alerts to the same gate that governs releases, so a production drift can automatically tighten escalation thresholds (fail safe toward human review) while the team investigates, rather than continuing to act autonomously on a distribution the system was never validated against."

---

**🎙️ Q8: "What are the failure modes unique to regulated environments, and how does your eval strategy anticipate them?"**

**✅ Strong answer:** "In regulated work the cost asymmetry is extreme — a confident wrong action can be a compliance breach, not just a bad answer. So the failure modes I design against:
- **Silent confident errors** — the worst case; caught by verification gates and per-step scoring, never by output-only checks.
- **Fabricated consensus** — the system resolving genuine disagreement silently; caught by conflict-detection and provenance-surfacing.
- **Unauditable decisions** — a right answer you can't explain; caught by mandatory decision-trace capture (a decision without a trace fails the gate).
- **Policy/regulatory violations** — caught by the ontology's constraints as hard gates, enforced in code at the action boundary, not as prompt instructions.
- **Distribution drift into an unvalidated regime** — caught by drift monitoring that fails safe toward escalation.

Anticipating failure modes 'before they become client incidents' — the JD's phrase — means building the gate for each *before* go-live, red-teaming with adversarial and out-of-scope inputs, and setting the escalation tail deliberately."

**🎯 Senior signal:** "Regulated environments invert the usual cost function — acknowledged uncertainty is cheap, confident wrong action is catastrophic — so the eval strategy optimises for *catching* failures, not just measuring them, and every irreversible action sits behind a verification gate plus an ontology-enforced policy check. The differentiator is treating auditability as a gate criterion: if a decision can't be traced and explained, it doesn't ship, because in banking or MedTech an unexplainable correct answer is still a liability."

---

## Sources
- [Pass@k vs Pass^k: Understanding Agent Reliability — Phil Schmid](https://www.philschmid.de/agents-pass-at-k-pass-power-k)
- [Beyond Pass@k: Measuring Reliability and Security of Agentic Code Generation (arXiv)](https://arxiv.org/abs/2608.14711)
- [The Reliability Gap: Agent Benchmarks for Enterprise — Paul Simmering](https://simmering.dev/blog/agent-benchmarks/)
- [Layer-Isolated Evaluation: Gating the Deterministic Scaffold of a Production LLM Agent (arXiv)](https://arxiv.org/pdf/2606.11686)
- [Acceptance-Test-Driven Evaluation Protocols for Business-Centric LLM Systems (arXiv)](https://arxiv.org/pdf/2606.02755)
- [Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents (arXiv)](https://arxiv.org/pdf/2605.09863)
- [How to Evaluate AI Agents: Reliability, Cost, Latency, and Failure Modes — DEV](https://dev.to/fernandoabishai/how-to-evaluate-ai-agents-reliability-cost-latency-and-failure-modes-2bb1)
- [Reproducible LLM Evaluation for Engineers — MLflow](https://mlflow.org/articles/llm-evaluation-harness/)

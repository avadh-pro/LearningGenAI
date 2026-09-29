# Agent Architecture & Multi-Agent Runtime — Interview Questions

> **⚡ In plain words:** This is the "engine room" that runs your agents. The golden rule: make as *little* as possible actually AI — anything with fixed rules becomes plain code (100% reliable); use an agent only when the steps genuinely depend on the input. **Checkpoint** = autosave after every step (so you can resume, pause for a human, and keep an audit trail). **Escalation** = when unsure or risky, pause and hand to a human — designed on purpose, not as an error handler. **Model routing** = sensitive data → local model, hard reasoning → OpenAI/Anthropic, easy stuff → cheapest. The nightmare to prevent: a *silent, confident, wrong answer* — caught by verification gates + traces, never by "a better prompt."

*JD pillar: "Design the multi-agent runtime — orchestration, queues, checkpoints, and escalation paths — for an entire engagement."*

*Two layers per answer: **✅ Strong answer** (what you say) and **🎯 Senior signal** (the L3 trade-off/failure-mode framing). Calibrated to someone architecting the stack, not using it.*

---

**🎙️ Q1: "Design the multi-agent runtime for a Fortune 500 workflow that has to run at 99.99%. Walk me through the architecture."**

**✅ Strong answer:** "I'd start by refusing to make the whole thing agentic. The reliability bar forces a discipline: **minimise the agentic surface.** Anything deterministic — validation, routing by explicit rules, data joins — is a plain function or a workflow step. Model-decided control flow is reserved for the genuinely ambiguous part. That's not a cost optimisation, it's a reliability one: a deterministic step contributes a factor of 1.0 to the reliability product; every LLM step multiplies your ceiling down.

Then the runtime, layer by layer:
- **Orchestrator** — a durable-execution engine (Temporal, or LangGraph's checkpointer on Postgres), not a while-loop. Every step is checkpointed so a crash resumes from the last good state, not the start.
- **Queues between stages** — decouple producers from consumers so a slow tool or a burst doesn't cascade; gives you backpressure and retry isolation.
- **Checkpoints** — state persisted after every node, keyed per workflow instance, so you get resume, replay, and time-travel debugging.
- **Escalation paths** — a first-class product surface, not an error handler. When confidence drops below threshold, an action exceeds a risk limit, or a regulatory rule triggers, the workflow *pauses durably* and hands to a human, then resumes. Plus hard caps: max handoffs, timeouts, loop detection.
- **Verification layer** — before any irreversible action, an eval/rubric gate checks the proposed action against the ontology's constraints. This is the '99.99%' machinery — you don't get there by a better prompt, you get there by gating.

The mental model I'd give the client: **a deterministic scaffold wrapped around a non-deterministic core.**"

**🎯 Senior signal:** "99.99% is a *pass^k* statement, so the architecture must be built for consistency across repeated runs, not peak capability. Concretely: durable orchestration for resumability, verification gates before irreversible actions, escalation as a designed surface with hard budgets, and aggressive de-agentification of anything that doesn't need model judgment. The failure mode I'd call out is *silent* failure — an agent producing a confident wrong answer with no exception — which is why the verification gate and decision-trace capture matter more than the happy-path orchestration."

---

**🎙️ Q2: "Orchestration patterns — how do you choose between sequential, supervisor/router, and event-driven for an engagement?"**

**✅ Strong answer:** "By the shape of the work and the failure-isolation needs:
- **Sequential pipeline** when stages are genuinely ordered and each depends on the last (extract → normalise → decide → act). Simplest to reason about and gate.
- **Supervisor/router** when input type varies — a procurement query vs a compliance query need different specialists. The supervisor classifies and delegates; you pay one extra LLM hop for routing but keep each worker's context and tool set small (which itself improves reliability, since tool-selection accuracy degrades past ~10–15 tools).
- **Event-driven** when the workflow is long-running, spans systems, and steps fire on external events (an SAP PO status change, a document landing). This is the enterprise-scale pattern — agents subscribe to events, emit events, and the queue is the backbone. It's also the most resilient because there's no central loop to be a single point of failure.

For a Fortune 500 engagement I'd usually land on **event-driven at the macro level, supervisor/router within a bounded task, sequential inside a worker.** Nesting them keeps each layer simple."

**🎯 Senior signal:** "The honest trade is failure-recovery, which research consistently flags as the least reliable capability of both DAG and ReAct architectures at enterprise scale. Event-driven with durable queues isolates failure best but costs observability complexity — you need distributed tracing across the event bus or you can't debug it. So I'd tie the pattern choice to the maturity of the observability I can stand up, not just the workflow shape."

---

**🎙️ Q3: "What does a checkpoint actually contain, and why is durable execution non-negotiable here?"**

**✅ Strong answer:** "A checkpoint is the full workflow state serialised after a step: the accumulated messages/decisions, tool inputs and outputs, retry counts, error reasons, the current node, and any human-handoff status. Keyed to a workflow-instance ID.

It's non-negotiable for three reasons the JD cares about:
1. **Resumability** — a 40-step regulated workflow can't restart from zero because a tool timed out at step 30. You resume from the last trusted checkpoint.
2. **Human-in-the-loop** — durable pause is only possible if state lives on disk; the process isn't blocking. A compliance officer can approve three days later from a different machine.
3. **Decision traces** — the checkpoint history *is* the audit trail, and in a regulated environment you need to reconstruct exactly why the system did what it did. It's also the raw material for the compounding loop — those traces become eval cases and RL environments."

**🎯 Senior signal:** "Durable execution is what turns 'resume from checkpoint' from a nice-to-have into the substrate for everything else — recovery, HITL, audit, and the RL data flywheel all read from the same persisted state. The design decision I'd flag is checkpoint *granularity*: too coarse and you lose replay precision and re-run expensive LLM calls; too fine and you drown storage and slow the hot path. I'd checkpoint at every externally-visible side effect and every model decision, and nowhere else."

---

**🎙️ Q4: "How do you design escalation paths for a regulated workflow?"**

**✅ Strong answer:** "Escalation is a product surface, so I design it like one, with explicit triggers:
- **Confidence-based** — the agent's own or a verifier's confidence falls below a calibrated threshold.
- **Risk-based** — the proposed action exceeds a value/impact limit (a refund over ₹X, a change to a booked order, anything irreversible).
- **Policy-based** — the ontology/policy layer flags a regulatory rule that mandates human review.
- **Budget-based** — max handoffs, step cap, or wall-clock exceeded → escalate rather than loop.

On escalation the workflow *pauses durably*, surfaces a structured payload to the right human (not a raw dump — the decision, the evidence, the recommended action, the confidence), captures their decision as a trace, and resumes. Every escalation is logged and becomes an eval case: if humans keep overriding the same decision, that's a signal to fix the policy or retrain."

**🎯 Senior signal:** "The senior framing is that escalation rate is itself a metric you tune, not a static config. Too eager and you've built expensive human-review software; too lax and you breach the reliability bar. I'd instrument the escalation → human-decision → outcome loop and use disagreement between agent and human as the highest-value training signal in the compounding loop. Escalation isn't the failure path — it's the data-generation path."

---

**🎙️ Q5: "Agent A and Agent B produce contradictory conclusions in a compliance workflow. How does your runtime handle it?"**

**✅ Strong answer:** "First requirement: it has to *detect* the conflict — naive pipelines are last-writer-wins and resolve it silently, which in a regulated setting is the worst outcome. So there's a reconciliation step.

Resolution in increasing cost:
- **Deterministic precedence** — if one source is authoritative by rule (the system-of-record beats an inference), the ontology encodes that and it's settled cheaply.
- **A verifier/judge agent** with an explicit rubric, run order-swapped to control position bias, accepted only on agreement.
- **Escalate to a human** when the disagreement is genuine and the stakes are high.
- **Surface both with provenance** — in compliance, 'these two sources disagree, here is each and its evidence' is often the correct output, not a fabricated consensus.

The runtime should never quietly pick one."

**🎯 Senior signal:** "In regulated work, fabricated consensus is a higher-cost failure than acknowledged uncertainty, so the default must be surfacing disagreement with provenance, not silent resolution. This is also where the ontology earns its keep — encoding source authority and policy precedence turns most conflicts into cheap deterministic resolutions and reserves human escalation for the genuinely ambiguous minority."

---

**🎙️ Q6: "Where does context management sit in a long-running agent, and how do you stop it degrading over a 40-step workflow?"**

**✅ Strong answer:** "Context bloat hits twice: cost grows superlinearly because you re-send a growing transcript, and quality drops because the original objective ends up in the low-attention middle. In a 40-step regulated workflow that's a real correctness risk.

Four levers, in order of impact:
- **Externalise state to a scratchpad** (or the durable store) instead of leaving everything in the message list — the agent reads back only what the current step needs.
- **Cap and structure tool outputs at the tool boundary** — an SAP query returning 4,000 characters of raw rows is usually the real culprit; summarise or select before it enters context.
- **Rolling summarisation** — keep recent steps verbatim, compress older ones.
- **Sub-agents with clean context** for self-contained subtasks, returning only the conclusion to the parent.

The ontology helps here too — reasoning over a compact typed representation beats stuffing raw documents into the prompt."

**🎯 Senior signal:** "The design principle is that memory is a side-store the reasoner reads from selectively, not a pipeline stage that accumulates unboundedly. Fix tool-output size first — teams reach for summarisation when one verbose tool is flooding the transcript. And note that context management interacts with caching: if you rewrite history every step you destroy the prompt-cache prefix, so I'd keep a stable, cached instruction+ontology prefix and let only the tail vary."

---

**🎙️ Q7: "Frontier models from OpenAI/Anthropic *plus* locally-deployed domain-tuned engines. How do you route between them in one runtime?"**

**✅ Strong answer:** "Model routing by the nature of the step, under two hard constraints — data residency and cost:
- **Data-sensitive steps** that touch client PII or regulated data → the locally-deployed, in-environment domain-tuned model (GRPO-tuned), so data never leaves the firewall. This is often non-negotiable for SOC 2 / GDPR reasons, not performance ones.
- **Hard open-ended reasoning** where the frontier model's capability genuinely matters and the data can be sent (or is redacted) → OpenAI/Anthropic.
- **Routine/classification/routing steps** → the cheapest model that holds quality, often the local one.

The router itself should be deterministic where possible — decide by data-classification tags and step type, not by asking an LLM. And I'd abstract the model behind an interface so a model swap is a config change, not a rewrite, because frontier models change generation every few months."

**🎯 Senior signal:** "The routing decision is driven first by data-egress policy, then by capability, then by cost — in that order for a regulated enterprise. The compounding-loop angle is that the local domain-tuned engine is the one you *own and improve*: decision traces from production become GRPO training data, so the local model gets better at the client's specific workflow over time while the frontier models stay static. That flywheel is the strategic reason to keep meaningful work on the in-environment model, not just the compliance reason."

---

**🎙️ Q8: "What breaks first when this goes to production, and how does your architecture see it coming?"**

**✅ Strong answer:** "The failures that only show up under real traffic:
- **Silent tool degradation** — an upstream system (SAP, a pricing API) starts returning empty-but-valid responses instead of errors; the agent reasons over nothing and confabulates. Caught by semantic (not just schema) validation at the tool boundary and by drift alerts on output quality.
- **Cascading decision errors** — an early wrong step is treated as fact downstream. Caught by per-step verification, not just end-to-end.
- **Distribution drift** — real inputs diverge from what you tested; offline scores stay green while production quality falls. Caught by the eval control plane running sampled online evals and by monitoring the metric–production gap.
- **Tail-latency and cost blowups** — one pathological input loops 30 times. Caught by budgets and p99 monitoring, not means.

The architecture 'sees it coming' because tracing + the eval control plane are wired in from day one — every run emits a nested-span trace, a sampled fraction is scored live, and drift/cost/quality alerts fire before a client notices."

**🎯 Senior signal:** "The unifying point: all of these are invisible to output-only, happy-path testing, which is why observability and the eval control plane are architecture, not ops. I'd design the trace schema and the drift monitors *before* the happy path, because in a 99.99% engagement the thing that ends you is the confident silent failure, and you can only catch that with per-step verification and production-distribution monitoring feeding back into the loop."

---

## Sources
- [Orchestrating AI Agents in Production — HatchWorks](https://hatchworks.com/blog/ai-agents/orchestrating-ai-agents/)
- [What is Multi-Agent Orchestration? — TrueFoundry](https://www.truefoundry.com/blog/what-is-multi-agent-orchestration)
- [Autonomous Event-Driven Multi-Agent Orchestration for Enterprise AI at Scale (arXiv)](https://arxiv.org/pdf/2606.20058)
- [Multi-Agent LLM Orchestration for Incident Response (arXiv)](https://arxiv.org/pdf/2511.15755)
- [AI Agent Orchestration: Enterprise Guide — Tyk](https://tyk.io/learning-center/ai-agent-orchestration-a-complete-enterprise-guide/)
- [The Complete Agentic AI System Design Interview Guide 2026](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)

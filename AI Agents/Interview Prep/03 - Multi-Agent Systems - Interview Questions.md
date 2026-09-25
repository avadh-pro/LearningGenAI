# Multi-Agent Systems — Interview Questions

*Built from* What is a Multi-Agent System - Video Notes.md *and the multi-agent project notebooks.*

*Scoped to **coordination between agents** — when multiple agents are justified, the named patterns, and what breaks. Single-agent internals are `02`; framework mechanics are `04`–`05`. Two-layer answers: plain language with an example, then the precise version.*

---

**🎙️ Interview Q1:** "When do you actually need multiple agents rather than one agent with more tools?"

**✅ Strong answer:** "Honestly, less often than the hype suggests — and saying that is usually a good signal in an interview.

One agent with more tools is the right default. You add agents when one of three things is true:

**Context isolation.** The task has genuinely separate phases and you don't want phase 3 reasoning over phase 1's mess. A researcher producing 10,000 words of notes, then a writer who should only see the summary — separate contexts keep both sharp.

**Different system prompts genuinely conflict.** A creative writer and a strict fact-checker want opposite instructions. Cramming both into one prompt produces an agent that's mediocre at each.

**Tool-count pressure.** Past roughly 10–15 tools, selection accuracy drops. Splitting into specialists with 4–5 tools each restores it.

What is *not* a reason: that it sounds more sophisticated. Every extra agent adds latency, cost, and a handoff that can lose information."

**🎯 Standard Interview Answer:** "The default should be a single agent with an expanded tool set; multi-agent decomposition is justified by three conditions. Context isolation, where phase-separated work benefits from bounded context per phase rather than a monotonically growing shared transcript. Prompt conflict, where required behavioural specifications are mutually inconsistent and cannot be jointly optimised in one system prompt. Tool cardinality, where selection accuracy degrades beyond roughly 10–15 tools and partitioning into specialists with smaller action spaces restores it. Each additional agent introduces handoff latency, incremental inference cost, and an information-loss boundary, so decomposition requires positive justification."

---

**🎙️ Interview Q2:** "Describe the main multi-agent coordination patterns."

**✅ Strong answer:** "Four that cover most real systems:

| Pattern | Shape | When |
|---|---|---|
| **Sequential / pipeline** | A → B → C, fixed | Stages are genuinely ordered — research, write, edit |
| **Supervisor / router** | One manager delegates to workers | Input type varies and you need routing |
| **Planner–executor** | One decomposes, others execute | Task needs breaking down before doing |
| **Critic–refiner** | Producer and reviewer loop | Output quality matters more than latency |
| **Peer-to-peer** | Agents talk directly | High-frequency exchange with no arbitration needed |

**Everyday example for the supervisor one:** a support desk. The front desk doesn't fix anything — it listens, works out whether this is billing, technical, or returns, and routes. That's a supervisor.

The one I'd flag as most over-used is critic–refiner. It genuinely improves quality, but it at least doubles cost and latency, and if the critic isn't given a concrete rubric it produces vague feedback that makes the output worse, not better."

**🎯 Standard Interview Answer:** "Principal patterns: sequential pipelines with static stage ordering; supervisor-worker, where a routing agent performs input classification and delegation, appropriate under heterogeneous input distributions; planner-executor, separating task decomposition from execution; critic-refiner, introducing an evaluation loop over produced artefacts; and peer-to-peer, where agents communicate directly without a central coordinator, suited to high-frequency low-ambiguity exchange where central arbitration adds latency without adding decision value. Critic-refiner at least doubles cost and latency and requires an explicit evaluation rubric — unrubriced critique produces non-actionable feedback and can degrade output."

---

**🎙️ Interview Q3:** "Supervisor versus peer-to-peer — why would you ever go decentralised?"

**✅ Strong answer:** "Because a supervisor is a bottleneck and a single point of failure for *every* interaction, including trivial ones.

If a knowledge agent just needs to tell a memory agent 'update this fact', routing that through a supervisor adds a full LLM call and its latency for a decision that doesn't need making. There's no arbitration required — nothing to decide.

So peer-to-peer makes sense for **high-frequency, low-ambiguity exchanges**: continuous state sync, background updates, agents reacting to each other. You give up the supervisor's global view and its conflict resolution, and you get a lighter, more reactive system.

What you lose is real though: with no central coordinator, nobody has the full picture, debugging gets much harder, and two agents can take contradictory actions with nothing to catch it."

**🎯 Standard Interview Answer:** "Centralised supervision imposes a mandatory coordination hop on every inter-agent interaction, contributing latency and constituting a single point of failure even for exchanges requiring no arbitration. Peer-to-peer coordination is appropriate for high-frequency, low-ambiguity communication — state synchronisation, autonomous background updates — where the supervisor adds no decision value. The trade-off surrenders global observability and centralised conflict resolution, increasing the difficulty of failure attribution and admitting contradictory concurrent actions without a natural arbitration point."

---

**🎙️ Interview Q4:** "What's the hardest thing about multi-agent systems in production?"

**✅ Strong answer:** "Failure attribution. When the output is wrong, **which agent was wrong?**

With one agent you read one trace. With five agents you have a chain where agent 3 produced something slightly off, agent 4 accepted it as fact, and agent 5 confidently formatted it. The visible failure is at the end; the cause is in the middle. And each agent behaved reasonably *given what it received*.

This is why per-agent evaluation matters and end-to-end evaluation isn't enough. You need to score each handoff — was the research complete? Was the draft faithful to the research? — otherwise you're guessing.

The second hardest thing is **error propagation with false confidence.** Agents don't pass along uncertainty. Agent 3 isn't sure, writes a hedge-free sentence anyway, and agent 4 has no way to know it was a guess. Nothing in the chain carries a confidence signal unless you build one."

**🎯 Standard Interview Answer:** "Failure attribution across the trajectory. End-to-end evaluation identifies that an output is incorrect but not which stage introduced the defect, and each agent's behaviour is typically locally reasonable conditioned on its input. This necessitates per-handoff evaluation — scoring each inter-agent artefact against stage-specific criteria — rather than terminal-output evaluation alone. The compounding factor is confidence erasure: uncertainty present at an upstream stage is not encoded in the natural-language artefact passed downstream, so downstream agents consume speculative content as established fact. Propagating explicit confidence or provenance metadata across handoffs is a design requirement, not an emergent property."

---

**🎙️ Interview Q5:** "How does reliability behave as you add agents?"

**✅ Strong answer:** "It compounds downward, and the arithmetic is brutal.

If each agent is 95% reliable, five in a chain gives you roughly **77%** end to end. At 90% each it's about 59%. That's the single most important number in this whole topic.

**Everyday example:** it's a relay race where each runner has a 5% chance of dropping the baton. Individually fine; across five handoffs, one in four races ends badly.

Two consequences. First, **fewer agents is usually more reliable** — which is why 'add another agent' is often the wrong fix. Second, you need checkpoints: validation between stages so a bad handoff is caught rather than propagated. A schema check or a quick relevance score between agents costs little and stops a lot.

This is also the strongest argument for doing as much as possible deterministically. A deterministic step is 100% reliable and doesn't enter the multiplication."

**🎯 Standard Interview Answer:** "Per-stage reliability compounds multiplicatively across the trajectory: five stages at 0.95 individual reliability yield approximately 0.77 end-to-end; at 0.90, approximately 0.59. Two design implications follow. Minimising stage count directly improves reliability, so decomposition must be justified against this cost. And inter-stage validation — schema conformance, relevance scoring, or explicit acceptance criteria — converts silent propagation into detectable failure at low marginal cost. Deterministic stages contribute a factor of 1.0 and are therefore strongly preferred wherever the work does not require model judgment."

---

**🎙️ Interview Q6:** "What's a hierarchical process, and when does it beat a sequential one?"

**✅ Strong answer:** "In a sequential process, you specify the order and it runs top to bottom. In a hierarchical process, a **manager agent** decides which worker handles what, in what order, and validates the result before moving on.

Hierarchical wins when the input varies enough that a fixed order would be wrong. A support system handling billing, technical and returns queries shouldn't run all three specialists every time.

It costs more, though — the manager is itself an LLM making calls, so you're paying for coordination on top of work. And the manager becomes the thing you have to debug when routing goes wrong.

Rule of thumb: **if you can write down the order and it's right every time, sequential.** If the right order depends on the input, hierarchical."

**🎯 Standard Interview Answer:** "Sequential processes execute a statically ordered task list. Hierarchical processes introduce a manager agent that performs dynamic task assignment, ordering and result validation. Hierarchical coordination is justified under input heterogeneity where a fixed execution order would be suboptimal or wasteful for some input classes. The costs are additional inference for coordination itself and the introduction of the manager as a distinct failure and debugging surface. The selection criterion is whether correct execution order is statically determinable."

---

**🎙️ Interview Q7:** "How do agents actually share information with each other?"

**✅ Strong answer:** "Three mechanisms, and they have different failure modes:

**Shared state.** All agents read and write one object — LangGraph's state is this. Everyone sees everything, which is transparent but means context grows for all of them.

**Message passing / handoff.** Agent A's output becomes agent B's input. Clean boundaries, but **lossy** — B only knows what A chose to write down. This is where the 'agent 4 doesn't know agent 3 was guessing' problem lives.

**Shared external store.** A database or vector store both read from. Scales best, survives restarts, but you now own consistency questions.

The important trade-off to name: **shared state is transparent but bloats; message passing is clean but lossy.** Most production systems use both — messages for the main flow, shared state for things everyone needs like the user ID or the original goal."

**🎯 Standard Interview Answer:** "Three mechanisms with distinct characteristics. Shared mutable state, where all agents read and write a common object, offers full transparency at the cost of context growth proportional to total system activity. Message passing, where inter-agent handoff occurs through explicit artefacts, provides clean boundaries but is lossy — downstream agents receive only what was serialised, which is the mechanism by which uncertainty and provenance are lost. External shared stores decouple persistence from execution, scale independently and survive restarts, but introduce consistency and staleness concerns. Production systems typically combine message passing for the primary workflow with shared state for cross-cutting invariants such as identity, authorisation scope, and the original objective."

---

**🎙️ Interview Q8:** "Agent A and agent B reach contradictory conclusions. How does your system handle it?"

**✅ Strong answer:** "First thing: **it has to notice.** Most naive systems don't — the last agent to write simply wins, silently. So the baseline requirement is a comparison step that can detect the disagreement at all.

Then, options in increasing cost:

**Deterministic precedence.** One source is authoritative by rule — the database beats the web search. Cheap and predictable; works when authority is genuinely rankable.

**A judge agent.** A third agent reads both and decides, with a rubric. Costs an extra call and introduces its own bias — position bias is real, judges favour the first option around 60–65% of the time, so you'd swap order and require agreement.

**Escalate to a human.** Correct answer when the stakes are high and the disagreement is genuine.

**Surface both.** Sometimes the honest output is 'these two sources disagree, here's each.' In a legal or medical context that's better than a false resolution.

The wrong answer, which I'd flag: silently picking one. That's how systems produce confident wrong answers."

**🎯 Standard Interview Answer:** "The prerequisite is detection — naive pipelines exhibit last-writer-wins semantics, resolving conflicts silently. Resolution strategies in ascending cost: deterministic source precedence, where authority is ranked a priori and applicable when sources are genuinely orderable by reliability; adjudication by a judge agent against an explicit rubric, which incurs additional inference and inherits LLM-as-judge biases — notably position bias favouring the first-presented option at roughly 60–65%, mitigated by order-swapped double evaluation requiring agreement; human escalation for high-stakes genuine disagreement; and explicit non-resolution, surfacing both positions with provenance, which is the correct output in domains where fabricated consensus carries higher cost than acknowledged uncertainty."

---

**🎙️ Interview Q9:** "You've been asked to build a multi-agent system. What do you ask before writing any code?"

**✅ Strong answer:** "Five questions, and the first two often end the conversation:

1. **Does this actually need multiple agents?** Would one agent with more tools do it? I'd genuinely try that first.
2. **Does it need agents at all, or is this a workflow?** If the steps are fixed, a pipeline is cheaper, faster and more reliable.
3. **What's the reliability target?** Because if they say 99% and the design has six stages, the arithmetic doesn't work and we need to talk about that now, not after.
4. **What's irreversible?** Anything that sends, pays, or deletes needs an approval gate designed in from the start, not bolted on.
5. **How will we know it's working?** If there's no tracing and no evaluation set, we're building something we can't operate.

The meta-point: most 'multi-agent' requirements are really 'we want this automated' requirements, and the agent count is an implementation detail the requester shouldn't be specifying."

**🎯 Standard Interview Answer:** "Requirements clarification in this order. Whether multi-agent decomposition is necessary versus a single agent with expanded tooling. Whether agentic control flow is necessary at all versus a deterministic workflow, given the cost, latency and reliability advantages of the latter. The end-to-end reliability target, evaluated against multiplicative per-stage degradation, since stated targets are frequently incompatible with proposed stage counts. The set of irreversible operations, which determines where human-approval interrupts and therefore durable execution are required. And the observability and evaluation plan, since an untraced, unevaluated agent system is not operable. Requested agent counts are typically an over-specified implementation detail rather than a genuine requirement."

---

## Sources

- [50 Agentic AI Interview Questions Asked in 2026 — AgentSwarms](https://agentswarms.fyi/blog/agentic-ai-interview-questions-2026)
- [Best Multi-Agent Frameworks in 2026: LangGraph, CrewAI — Gurusup](https://gurusup.com/blog/best-multi-agent-frameworks-2026)
- [The Complete Agentic AI System Design Interview Guide 2026](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)
- [Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems (arXiv)](https://arxiv.org/pdf/2512.12791)
- [Evaluating Agentic AI in the Wild: Failure Modes, Drift Patterns (arXiv)](https://arxiv.org/pdf/2605.01604)
- [LLM-as-a-Judge — Langfuse](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge)

# AI Agent Fundamentals — Interview Questions

*Built from* AI Agents - An Introduction *and* End to End Architecture of a Single Agent/Core Components of an AI Agent.md*.*

*Curated from current (2026) agentic-AI interview question banks and calibrated to roughly four years of AI engineering experience. Deliberately scoped to **what an agent is and when it is the wrong answer** — architecture internals are in `02`, coordination in `03`, frameworks in `04`–`05`. Same two-layer format used throughout this repo: a plain-language answer with an everyday example, then a crisp version worth saying out loud in the room. Try answering aloud before reading the model answer.*

---

**🎙️ Interview Q1:** "What actually makes something an AI agent, as opposed to a chatbot or a RAG pipeline?"

**✅ Strong answer:** "One word: **actuators.** An agent can change the world — it doesn't just produce text, it takes actions that have consequences. The second thing is **control flow**: in a chatbot or a RAG pipeline, I decide the sequence when I write the code. In an agent, the model decides what to do next at runtime.

**Everyday example:** a financial advisor who tells you 'you should move money into that fund' is a chatbot. One who has authority over your account and actually moves the money is an agent. Same intelligence, completely different risk profile — and that difference is the entire reason agents need guardrails, approval steps, and observability that chatbots don't.

```
RAG pipeline:  query → retrieve → generate → done        (I wrote the arrows)
Agent:         goal → think → act → observe → think → …  (model picks the arrows)
```

The practical consequence is that a RAG pipeline is a DAG with a fixed number of LLM calls, so I can predict its cost and latency. An agent is a loop with an unpredictable number of iterations, so I can't — which is why step budgets and timeouts are non-negotiable in production."

**🎯 Standard Interview Answer:** "An agent is distinguished by two properties: the capacity to affect external state through tool invocation, and runtime-determined control flow. A RAG pipeline is a directed acyclic graph with a statically known execution path and a bounded number of model calls; an agent is a cyclic perceive–reason–act loop where the model selects the next action from an action space at each iteration. This makes cost and latency unbounded by default, which is why production agents require explicit step budgets, wall-clock timeouts, and loop detection. The corollary is that an LLM with no tools is not an agent regardless of how it is prompted — it is a reasoner."

**🔁 Interview Q1 (follow-up):** "So is a RAG system ever an agent?"

**✅ Strong answer:** "It becomes one the moment retrieval stops being a fixed first step and becomes a *decision*. That's agentic RAG — the model looks at the query and decides whether to retrieve at all, which source to hit, whether the results were good enough, and whether to search again with a reformulated query. The pipeline version always retrieves exactly once whether or not it helps. As of 2026 agentic RAG is the production default rather than an advanced variant, mostly because 'always retrieve once' handles multi-hop questions badly."

**🎯 Standard Interview Answer:** "The boundary is whether retrieval is a static pipeline stage or a policy decision. Agentic RAG conditions retrieval on model judgment — whether to retrieve, which index or tool to query, whether retrieved context is sufficient, and whether to re-query with a reformulated request. This introduces cyclicity and makes the system agentic under the control-flow criterion, at the cost of non-deterministic latency."

---

**🎙️ Interview Q2:** "Walk me through the core components of an agent."

**✅ Strong answer:** "I think of it as a new employee on their first day — it maps one-to-one and it's hard to forget:

| Component | The employee analogy |
|---|---|
| **Environment** | The workplace — what they can affect and get feedback from |
| **Sensors / perception** | Eyes and ears — how the world reaches them |
| **Memory / knowledge base** | The handbook *plus* their own notebook |
| **Reasoning engine** | The brain — decides what to do |
| **Actuators** | Hands — thinking moves nothing, hands do |
| **Performance measure** | The appraisal — how you judge if they're good |
| **Learning** | Experience — why a five-year employee beats a day-one one |

Two things worth saying explicitly because interviewers probe them. First, **memory splits in two** — what you gave it (policies, docs) versus what it accumulated (this customer complained twice last month). Second, **learning is the optional one.** Most production LLM agents don't learn at all between runs; they're frozen weights plus retrieved context. Calling that 'learning' in an interview is a mistake."

**🎯 Standard Interview Answer:** "Seven components: environment, sensors, knowledge base/memory, reasoning engine, actuators, performance measure, and an optional learning component. The reasoning engine consumes perception and memory jointly and emits an action selection; actuators effect that action against the environment; the performance measure defines the objective that makes 'good' well-defined. Memory bifurcates into supplied knowledge — retrieval corpora, rules — and accumulated state, which is thread-scoped conversation history or cross-thread long-term memory. In contemporary LLM agents the learning component is usually absent: adaptation is achieved through in-context learning and retrieval rather than weight updates, so the deployed policy is static between training cycles."

**🔁 Interview Q2 (follow-up):** "Where does memory sit in the flow — before or after reasoning?"

**✅ Strong answer:** "Neither, and this is where a lot of diagrams mislead people. Memory isn't a *stage* you pass through between perceiving and thinking — it's a store that reasoning reads from and writes back to. Reasoning decides *what* to look up and pulls only that. A support agent doesn't load your entire order history on every message; the reasoning step decides 'I need this user's last order' and retrieves just that.

```
Perception ──► Reasoning ──► Action
                  ▲ │
                  │ ▼
               Memory  (read + write)
```

So the chain is really three stages with memory feeding the middle one from the side."

**🎯 Standard Interview Answer:** "Memory is a side-store, not a pipeline stage. The reasoning engine issues reads against it conditioned on the current percept and writes back state deltas after acting. Modelling it as a sequential stage implies unconditional full-context loading, which is both wasteful and a direct cause of context bloat in long-running agents."

---

**🎙️ Interview Q3:** "When should you *not* build an agent?"

**✅ Strong answer:** "Whenever the workflow is actually deterministic — which is more often than people admit. If you can draw the steps on a whiteboard and they're the same every time, you want a pipeline, not an agent. You'll get predictable cost, predictable latency, and a system you can actually debug.

The honest heuristic I use: **an agent earns its cost when the number of steps genuinely depends on the input.** 'Summarise this document' is always one step — that's not an agent. 'Research this topic until you have enough to write a report' has an unknowable number of steps — that's an agent.

The other three where I'd say no: when errors are irreversible and you have no approval gate; when latency budget is under a couple of seconds, because each reasoning step alone costs 1–3 seconds; and when you can't observe it, because an unobservable agent is a system you cannot operate."

**🎯 Standard Interview Answer:** "Avoid agentic architectures when the control flow is statically determinable, when the action space includes irreversible operations without a human-approval checkpoint, when the latency SLO is incompatible with multi-step sequential inference — each reasoning step contributes 1–3 seconds and steps compound — or when there is no tracing infrastructure. A deterministic pipeline offers bounded cost, bounded latency, and straightforward failure attribution; an agent trades all three for the ability to handle input-dependent step counts. The trade is only justified when that variability is intrinsic to the task."

---

**🎙️ Interview Q4:** "Explain the perceive–think–act loop, and where real agents actually break inside it."

**✅ Strong answer:** "The loop is: take input in, decide using that plus memory, act, observe what changed, repeat. Simple enough. Where it breaks in practice is almost always one of three places.

**The model picks the wrong tool.** Not a reasoning failure — usually a tool-description failure. If two tools have vaguely similar descriptions, the model coin-flips. Most 'the agent is dumb' bugs are actually badly written tool docstrings.

**The loop doesn't terminate.** The agent calls a tool, gets an error, tries the same tool the same way, gets the same error, forever. You need a loop detector and a hard step cap, not better prompting.

**Context grows until it degrades.** Every iteration appends observations. By step 15 the agent is reasoning over a transcript where the original goal is buried thousands of tokens up — the 'lost in the middle' problem. It starts forgetting what it was asked to do."

**🎯 Standard Interview Answer:** "The loop is perceive → reason → act → observe, iterated until a termination condition. Three dominant production failure modes: tool-selection error, which is typically attributable to ambiguous or overlapping tool schemas rather than model capability; non-termination, where the agent retries a failing action without state change, requiring loop detection and hard iteration caps rather than prompt remediation; and context degradation, where accumulated observations push the original objective into the low-attention middle region of the context window. Mitigations are respectively schema disambiguation, budget enforcement, and context management through summarisation or scratchpad externalisation."

---

**🎙️ Interview Q5:** "What are the classical agent types, and do they still matter?"

**✅ Strong answer:** "The textbook taxonomy is reflex, model-based (stateful), goal-based, utility-based, learning, and hierarchical. They still matter, but as a **vocabulary for describing design choices**, not as a menu you pick from.

The one distinction that genuinely earns its keep is **goal-based versus utility-based.** Goal-based means there's a binary target — booking is made or it isn't. Utility-based means you're optimising a score with trade-offs — cheapest flight *and* fewest stops *and* preferred airline, where you can't max all three.

**Everyday example:** 'get me to Delhi' is goal-based. 'Get me to Delhi as cheaply as possible without more than one stop, and I'd rather fly in the morning' is utility-based — there's no single correct answer, only a best trade-off. That distinction decides whether your evaluation is pass/fail or a scored rubric, which is a real engineering consequence."

**🎯 Standard Interview Answer:** "The Russell–Norvig taxonomy — simple reflex, model-based reflex, goal-based, utility-based, learning, and hierarchical — remains useful as descriptive vocabulary rather than as an implementation choice. The operationally significant distinction is goal-based versus utility-based: the former admits a binary success predicate and therefore binary evaluation, while the latter requires an explicit utility function over competing objectives and therefore scored, multi-dimensional evaluation. Most LLM agents are implicitly goal-based with utility considerations smuggled into the system prompt, which is a common source of unmeasurable behaviour."

---

**🎙️ Interview Q6:** "Reactive versus deliberative agents — what's the practical difference?"

**✅ Strong answer:** "A reactive agent responds to what's in front of it right now. A deliberative agent keeps an internal model and plans ahead before acting.

**Everyday example:** a thermostat is reactive — it's cold, turn on the heat, no plan involved. A GPS is deliberative — it holds a model of the whole road network and computes a route before you move.

In LLM terms this is roughly **ReAct versus plan-and-execute.** ReAct decides one step at a time, which is flexible and recovers well from surprises but can wander. Plan-and-execute writes the whole plan upfront, which is cheaper and more predictable but brittle when step 2 returns something the plan didn't anticipate. Most real systems are hybrid: plan first, then allow replanning when reality disagrees."

**🎯 Standard Interview Answer:** "Reactive agents map percepts to actions without maintaining an internal world model; deliberative agents maintain state and perform lookahead planning. In LLM agent architectures this maps onto ReAct-style incremental action selection versus plan-and-execute decomposition. ReAct offers better recovery from unexpected observations at the cost of step efficiency and potential wandering; plan-and-execute offers predictable cost and better step efficiency at the cost of brittleness under plan invalidation. Production systems typically hybridise — initial decomposition with conditional replanning triggered by execution failure."

---

**🎙️ Interview Q7:** "Your agent works in the demo and fails in production. Where do you look first?"

**✅ Strong answer:** "First thing: **I don't guess — I open a trace.** Without per-step traces this is unanswerable, so if there's no tracing that's the actual first fix.

With traces, I'm triaging in this order, because it goes cheapest-to-check first:

1. **Did it pick the wrong tool?** Usually a tool-description problem.
2. **Did the tool return something different from the demo?** Silent tool degradation — the API changed, or returns an empty list instead of an error, and the agent happily reasons over nothing.
3. **Did it loop?** Check step count against the minimum needed.
4. **Did context blow up?** Compare token counts at step 1 versus the failing step.
5. **Only then** do I suspect the model or the prompt.

The reason demos mislead is that demos use the happy path with clean inputs. Production has empty results, timeouts, rate limits, and malformed data — and agents built without explicit handling for 'the tool returned nothing useful' tend to hallucinate straight through that gap."

**🎯 Standard Interview Answer:** "Triage via trace inspection, ordered by diagnostic cost: tool-selection correctness, tool-output validity including silent degradation where an API returns structurally valid but semantically empty responses, trajectory efficiency measured as actual versus minimal step count, and context growth across iterations. Model and prompt quality are the last hypotheses, not the first. The demo-to-production gap is primarily an input-distribution problem — demos exercise the happy path, while production surfaces empty results, partial failures, timeouts and malformed payloads. Agents lacking explicit degraded-path handling tend to confabulate over missing data rather than failing loudly, which is why graceful-degradation behaviour must be specified and tested rather than assumed."

---

**🎙️ Interview Q8:** "How do you keep an agent's cost under control?"

**✅ Strong answer:** "Cost in an agent is *steps × context size*, and both grow, so I attack both.

**Cap the steps.** A hard iteration limit plus loop detection. This is the single highest-value control because an unbounded loop is also an unbounded bill.

**Route by difficulty.** Most agent requests are routine — reported numbers put it around 60–80%. Sending those to a small model and reserving the frontier model for genuinely hard steps typically saves 40–70%. It's the highest-leverage optimisation available.

**Manage context.** Every step appends to the transcript, so token cost per step grows superlinearly across a run. Summarise old steps, or keep working notes in a scratchpad outside the message list.

**Cache.** Prompt caching on the stable prefix — system prompt and tool definitions — is nearly free to implement and cuts the repeated portion substantially.

The mistake I'd flag is optimising the model choice while ignoring step count. Halving your steps beats switching models."

**🎯 Standard Interview Answer:** "Agent cost scales as the product of step count and per-step context size, both of which grow during execution, so control requires addressing both. Primary levers: hard iteration budgets with loop detection; difficulty-based model routing, since roughly 60–80% of agent steps are routine and routing those to smaller models yields 40–70% savings; context management via summarisation or externalised scratchpads to prevent superlinear token growth; and prompt caching over the stable prefix of system instructions and tool schemas. Step-count reduction dominates model-price optimisation in effect size."

---

**🎙️ Interview Q9:** "What's the difference between an agent and a workflow, and why does the distinction matter commercially?"

**✅ Strong answer:** "A workflow has the path decided by the engineer; an agent has it decided by the model at runtime. That's the whole distinction.

Why it matters commercially is **reliability compounding.** If every step in a five-step workflow is 95% reliable, the whole thing is about 77% reliable. Agents make this worse in two ways: they have *more* steps, and the number isn't fixed. That's why teams that ship agents successfully tend to shrink the agentic surface — use deterministic workflow for everything that can be deterministic, and reserve model-decided control flow for the genuinely ambiguous part.

The honest framing for an interview: **agency is a cost you pay for flexibility, not a feature you add for its own sake.** The question is always whether this particular task actually needs runtime decisions."

**🎯 Standard Interview Answer:** "The distinction is where control flow is determined: authoring time for workflows, inference time for agents. The commercial significance is multiplicative reliability degradation — per-step reliability compounds across the trajectory, so a 95%-reliable step yields roughly 77% end-to-end reliability over five steps, and agents both increase step count and make it non-deterministic. The prevailing production discipline is therefore to minimise the agentic surface area: implement deterministic segments as workflows and confine model-determined control flow to genuinely ambiguous decision points. Agency is a reliability and cost expenditure justified only by irreducible input-dependent variability."

---

## Sources

- [50 Agentic AI Interview Questions Asked in 2026 — AgentSwarms](https://agentswarms.fyi/blog/agentic-ai-interview-questions-2026)
- [Top 30 Agentic AI Interview Questions and Answers for 2026 — DataCamp](https://www.datacamp.com/blog/agentic-ai-interview-questions)
- [Top 35 Agentic AI Interview Questions and Answers (2026) — Interview Coder](https://www.interviewcoder.co/blog/agentic-ai-interview-questions)
- [The Complete Agentic AI System Design Interview Guide 2026](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)
- [Resource Constraints and Performance in Agentic AI Systems (arXiv)](https://arxiv.org/pdf/2608.27886)
- [Evaluating Agentic AI in the Wild: Failure Modes, Drift Patterns (arXiv)](https://arxiv.org/pdf/2605.01604)

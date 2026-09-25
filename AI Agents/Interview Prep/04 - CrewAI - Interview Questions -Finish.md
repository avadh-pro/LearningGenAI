# CrewAI — Interview Questions

*Built from* Multi AI Agent Blog Generator using CrewAI.ipynb, Email agent with CrewAI.ipynb *and the Market Research / Conversational BI / Document Drafter projects.*

*Scoped to **CrewAI specifically** — its primitives, its processes, and the Crews-versus-Flows distinction that most candidates get wrong. Framework-neutral coordination theory is `03`; LangGraph is `05`. Two-layer answers throughout.*

---

**🎙️ Interview Q1:** "What are CrewAI's core primitives?"

**✅ Strong answer:** "Four, and they nest:

- **Agent** — a role. Defined by `role`, `goal`, `backstory`, plus its LLM and tools.
- **Task** — a unit of work. Defined by `description` and `expected_output`, usually assigned to an agent.
- **Crew** — a group of agents executing a list of tasks under a `process`.
- **Flow** — the event-driven layer *above* crews, using `@start`, `@listen`, `@router`.

The cleanest way to hold it: **the Agent answers 'who are you?', the Task answers 'what should be done and how do I know it's done?', the Crew answers 'in what order?', and the Flow answers 'what if the order depends on the result?'**"

**🎯 Standard Interview Answer:** "Agents are role-scoped executors parameterised by role, goal, backstory, model and tool set. Tasks are work units specified by description and expected output, optionally bound to an agent. Crews compose agents and an ordered task list under a process policy. Flows are a higher-order event-driven orchestration layer that wraps crews and direct model calls, using decorator-based control flow with `@start`, `@listen` and `@router`, and providing state threading and persistence."

---

**🎙️ Interview Q2:** "What's mandatory on a Task?"

**✅ Strong answer:** "Only two: **`description`** — what to do — and **`expected_output`** — what 'done' looks like. `agent` is technically optional since the crew can assign it, but in practice you always set it.

The one worth understanding is `expected_output`. An LLM has no natural sense of 'finished', so without a stated target it either stops early or writes forever. It's the task's acceptance criterion, and it's the field that most directly controls output quality.

**Everyday example:** 'write about our product' produces anything. 'Write a 300-word product description with three bullet-point benefits and a closing call to action' produces something you can actually check."

**🎯 Standard Interview Answer:** "`description` and `expected_output` are required; `agent` is optional at the type level since the crew may perform assignment, though explicit assignment is standard practice. `expected_output` functions as the task's acceptance criterion and is the primary control over termination behaviour and output conformance — its absence produces unbounded or prematurely truncated generation, since the model has no intrinsic completion signal."

**🔁 Interview Q2 (follow-up):** "What about `max_iter` on a task?"

**✅ Strong answer:** "`max_iter` is an **Agent** parameter, not a Task one — it caps how many reasoning iterations a single agent will run before giving up. Putting it on a Task is a common mistake, and older CrewAI silently ignored unknown keyword arguments, so the bug was invisible. Current versions validate with Pydantic and will reject it, which is an improvement — it fails loudly instead of silently doing nothing."

**🎯 Standard Interview Answer:** "`max_iter` is defined on Agent and bounds the agent's internal reasoning loop. Supplying it to Task is a specification error. Earlier CrewAI releases tolerated unrecognised keyword arguments silently, producing a latent no-op; current releases enforce Pydantic validation and raise, converting a silent misconfiguration into an explicit failure."

---

**🎙️ Interview Q3:** "Sequential versus hierarchical process — explain the difference and when you'd pick each."

**✅ Strong answer:** "**Sequential** runs the tasks in the order of your list. Task 1, then 2, then 3. The list *is* the plan.

**Hierarchical** introduces a **manager agent** that decides which agent handles what, delegates, and validates results before moving on. You set `manager_llm` for it.

Pick sequential when you can write down the order and it's right every time — a blog pipeline is research → draft → review → edit → format, always. Pick hierarchical when the right order depends on the input.

The cost difference is real: hierarchical adds an LLM call per coordination decision, and the manager becomes an extra thing to debug when routing goes wrong. I'd default to sequential and only move up when a fixed order demonstrably fails."

**🎯 Standard Interview Answer:** "Sequential executes the task list in declaration order with no runtime routing. Hierarchical instantiates a manager agent, configured via `manager_llm`, which performs dynamic delegation and output validation prior to progression. Selection criterion is whether correct execution order is statically determinable. Hierarchical incurs additional inference per coordination decision and introduces the manager as a distinct failure surface; sequential is the appropriate default absent demonstrated input heterogeneity."

---

**🎙️ Interview Q4:** "Can a CrewAI crew loop back to an earlier step?"

**✅ Strong answer:** "**No — not with `Process.sequential`.** The task list runs forward and stops. If the reviewer finds an error at step 3, there's no arrow back to the writer; it just carries on to step 4.

That's the defining limitation and it's what you want to name in an interview. A crew is a **DAG** — directed, acyclic. No cycles by construction.

**Flows fix this.** A `@router` can direct execution back to an earlier step, which is exactly the looping construct crews lack. So the ladder is:

1. **Crew** — fixed ordered list, no loops
2. **Flow** — `@router` for branching and loops, plus durable pause/resume and SQLite persistence
3. **LangGraph** — full state machine with conditional edges, checkpointing, time-travel"

**🎯 Standard Interview Answer:** "Crews under sequential process are acyclic — the task list executes in order to termination with no mechanism for backward transition. Cyclic control flow requires Flows, where `@router` methods perform conditional dispatch including transitions to previously executed steps. Flows additionally provide durable state persistence and human-feedback interruption, making them the appropriate construct for revision loops, conditional branching and approval gates."

---

**🎙️ Interview Q5:** "Crews versus Flows — when do you use which?"

**✅ Strong answer:** "**Crews are for autonomous collaboration with a known shape. Flows are for controlled, event-driven execution where the path depends on results.**

The useful framing: a Crew gives agents latitude in *how* they do the work but not *when*. A Flow controls *when* precisely, and calls crews to do the work.

And they compose — that's the production pattern people miss. You don't choose one; you put **crews inside a flow**. The Flow handles branching, approval gates and persistence; each step's actual work is a Crew.

**Everyday example:** the Flow is the project manager deciding what happens next based on how the last thing went. Each Crew is the team that does one piece of work."

**🎯 Standard Interview Answer:** "Crews provide autonomous multi-agent collaboration over a statically ordered task list, appropriate where the workflow shape is known and agent latitude is desirable within steps. Flows provide event-driven orchestration with explicit control flow, state threading and persistence, appropriate where execution path is result-dependent or where approval gates and durability are required. They are composable rather than alternative: the canonical production pattern embeds crews as work units within a flow that governs sequencing, branching and persistence."

---

**🎙️ Interview Q6:** "Is Crew to Flow the same relationship as LangChain to LangGraph?"

**✅ Strong answer:** "Roughly, on the axis that matters — **in both pairs, the first is fixed-shape and the second decides the path at runtime.** But it's not a strict equivalence and I'd say so:

- **Crew is *more* than a LangChain chain.** A chain step is a function call — input in, output out — and while you *can* swap models per step (`prompt1 | gpt4 | prompt2 | claude`), you can't give a step an identity, its own tool set, or the right to delegate. A Crew agent is a persistent entity with `role`, `goal`, `backstory` and its own tools, able to loop internally before producing output. It's still a straight path — more workers, same single lane.
- **Flows is *narrower* than LangGraph, not simply less.** Flows genuinely maintains state (`self.state` with an auto UUID), genuinely checkpoints **after every method** via `@persist` (default `SQLiteFlowPersistence`), and resumes by UUID. The two real gaps are **reducers** — LangGraph declares per-field merge rules, Flows mutates state directly — and **checkpoint-history rewind**: Flows resumes from the *latest* snapshot, LangGraph can rewind to any past checkpoint and branch.

| | Fixed shape | Runtime routing |
|---|---|---|
| **LangChain / LangGraph** | LCEL chain | `StateGraph` |
| **CrewAI** | Crew (`Process.sequential`) | Flows (`@router`) |

And the honest Flows-versus-LangGraph breakdown, since 'Flows is weaker' is the lazy version of this answer:

| | CrewAI Flows | LangGraph |
|---|---|---|
| Branching / loops | ✅ `@router` | ✅ conditional edges |
| State across steps | ✅ `self.state` | ✅ typed schema |
| Save after every step | ✅ `@persist` | ✅ checkpointer |
| Resume after crash | ✅ by UUID | ✅ by `thread_id` |
| Human-in-the-loop pause | ✅ | ✅ `interrupt` |
| **Per-field merge rules** | ❌ direct mutation | ✅ reducers |
| **Rewind to any past step** | ❌ latest snapshot only | ✅ full checkpoint history |

One thing to keep straight: they're not interchangeable pairs across families. LangChain and LangGraph are one family — `create_agent` runs on LangGraph underneath. Crew and Flows are another."

**🎯 Standard Interview Answer:** "The analogy holds on the static-versus-runtime control-flow axis but not as an equivalence. A Crew exceeds an LCEL chain in providing role-differentiated agents with persistent identity, per-agent tooling and internal iteration, while remaining acyclic — note that per-step model heterogeneity is *not* the differentiator, since LCEL composes arbitrary models across a chain. Flows differs from LangGraph more narrowly than commonly stated: it provides durable state, per-method checkpointing via `@persist`, and UUID-keyed resumption, so state management and crash recovery are comparable. The genuine divergences are the absence of a typed state schema with configurable per-field reducers, and resumption semantics restricted to the latest snapshot rather than arbitrary rewind over checkpoint history. The families are also internally coupled in a way the analogy obscures — `create_agent` is implemented on LangGraph, so LangChain and LangGraph share a runtime, whereas Crews and Flows are distinct constructs within CrewAI."

---

**🎙️ Interview Q7:** "What does `allow_delegation=True` do, and what does it cost you?"

**✅ Strong answer:** "It lets an agent hand its work to another agent mid-task rather than doing it itself.

What it costs is **predictability**. With `Process.sequential` the task *order* is fixed by your list — but with delegation enabled, who actually does the work inside each task isn't. So you get extra LLM calls you didn't budget for, traces that no longer match your mental model, and per-agent quality metrics that get muddied because agents are doing each other's jobs.

I'd default it off and enable it deliberately when I've seen a specific case where an agent genuinely needs capability it doesn't have."

**🎯 Standard Interview Answer:** "Delegation permits runtime reassignment of work between agents within a task. It decouples the executing agent from the authored structure, producing unbudgeted inference cost, reduced trace interpretability, and contaminated per-agent evaluation metrics. The predictability cost is incurred on every execution while the benefit accrues only to the subset of inputs exhibiting genuine capability gaps, so it warrants deliberate rather than default enablement."

---

**🎙️ Interview Q8:** "How do you evaluate a CrewAI system?"

**✅ Strong answer:** "Per-task, not just end-to-end — because end-to-end tells you the blog post is bad but not which of the five agents caused it.

Concretely, `expected_output` gives you a natural rubric per task. So for each task I'd score: did the output satisfy its stated expected output? That turns each handoff into a checkable boundary.

Beyond that, the agent-specific metrics that matter are **tool-selection accuracy** (did the researcher use the search tool when it should have), **trajectory efficiency** (step count versus minimum), and **goal completion** at the end.

The trap to avoid: scoring only the final artefact. In a five-stage crew, a mediocre research step produces a mediocre final post, and if you only look at the post you'll spend your time tuning the writer's prompt when the problem was upstream."

**🎯 Standard Interview Answer:** "Evaluation must be per-task rather than terminal-only, since end-to-end scoring provides no failure attribution across a multi-stage crew. The `expected_output` specification functions as a per-task rubric, enabling each inter-agent handoff to be scored against stated acceptance criteria. Complementary agent-level metrics include tool-selection accuracy, tool-argument correctness, trajectory efficiency measured against minimal step count, and terminal goal completion. Terminal-only evaluation systematically misattributes upstream defects to downstream stages."

---

**🎙️ Interview Q9:** "What would make you choose CrewAI over LangGraph for a real project?"

**✅ Strong answer:** "**Speed to a working multi-agent system when the shape is known.** CrewAI's role-based abstraction is genuinely faster to write — you describe agents in natural language and it works. Getting the same thing in LangGraph means defining state, nodes and edges explicitly.

I'd correct one common framing though: it's **not** that CrewAI is for simple problems. It handles genuinely complex pipelines fine. It's that CrewAI wants the *shape* known upfront. Complex-but-predictable is exactly its sweet spot.

I'd choose LangGraph when I need runtime-decided control flow, durable checkpointing with time-travel, or fine-grained state control — long-running stateful agents, human approval mid-run, or anything where I need to resume from a specific past checkpoint.

And I'd mention the honest migration path: teams often prototype in CrewAI and move to LangGraph when complexity grows. That's a real pattern, not a criticism of either."

**🎯 Standard Interview Answer:** "CrewAI is preferred for rapid delivery of multi-agent systems with statically determinable workflow shape — its role-based declarative abstraction requires substantially less scaffolding than explicit state, node and edge definition. The common mischaracterisation is that CrewAI suits simple problems; the accurate criterion is workflow predictability, not task complexity. LangGraph is preferred where control flow is runtime-determined, where durable per-superstep checkpointing and time-travel over checkpoint history are required, or where fine-grained typed state management with custom reducers is needed — characteristically long-running stateful agents with mid-execution human approval. Prototype-in-CrewAI, harden-in-LangGraph is a documented and legitimate progression."

---

## Sources

- [Crews — CrewAI Documentation](https://docs.crewai.com/en/concepts/crews)
- [CrewAI Flows: Production Multi-Agent Guide 2026](https://www.jahanzaib.ai/blog/crewai-flows-production-multi-agent-guide)
- [CrewAI Flows: Event-Driven Agent Orchestration Tutorial 2026 — Markaicode](https://markaicode.com/crewai-flows-event-driven-agent-orchestration/)
- [What is CrewAI? Multi-Agent Framework Explained in 2026 — Future AGI](https://futureagi.com/blog/what-is-crewai-2026)
- [Building Multi-Agent Systems With CrewAI — Firecrawl](https://www.firecrawl.dev/blog/crewai-multi-agent-systems-tutorial)
- [crewAIInc/crewAI — GitHub](https://github.com/crewaiinc/crewai)

# LangChain and LangGraph Agents — Interview Questions

*Built from* LangChain Agents.ipynb, LangGraph Agents.ipynb, Designing Stateful Agents with LangGraph *and the router / CRAG / HITL notebooks.*

*Scoped to **the LangChain and LangGraph agent stack** — `create_agent`, state, nodes, edges, cycles, checkpointers, threads, interrupts. Framework-neutral theory is `01`–`03`; CrewAI is `04`. This is the deepest framework set in the folder. Two-layer answers throughout.*

---

**🎙️ Interview Q1:** "What changed between the old ReAct agents and `create_agent`?"

**✅ Strong answer:** "Two things: **how the model asks for a tool**, and **what runs the loop**.

**Old — ReAct.** The model was prompted to emit a rigid text format:
```
Thought: I need the population
Action: wikipedia
Action Input: population of India
```
LangChain then **string-parsed** that. Write `Action:wikipedia` without the space and you got `OutputParserException`. It was a prompting trick for models that couldn't call tools natively.

**New — `create_agent`.** The model returns a structured tool call through the provider's API. No text format, no parsing, no parse errors — the model was actually post-trained for this.

**The analogy:** ReAct is shouting your order across a restaurant and hoping it's heard; `create_agent` is pressing the button on the till.

**The second change is bigger than people realise:** `create_agent` runs on LangGraph underneath. The old `AgentExecutor` was a plain Python while-loop with nothing persisted. Now the loop is a graph, so memory, streaming and human-in-the-loop come for free."

**🎯 Standard Interview Answer:** "Two structural changes. Tool invocation moved from prompt-convention text parsing to native structured tool calling at the provider API layer, eliminating the `OutputParserException` failure surface entirely. And the execution substrate moved from `AgentExecutor`, an unpersisted imperative loop, to LangGraph, which provides checkpointed state, streaming and interrupt support as runtime properties rather than bolt-ons. `initialize_agent`, `AgentExecutor` and `create_react_agent` were removed in LangChain 1.0 and relocated to `langchain-classic`; `langchain.agents.create_agent` is the sole current constructor."

**🔁 Interview Q1 (follow-up):** "Does 'zero-shot' still apply?"

**✅ Strong answer:** "Yes — that part didn't change. Zero-shot means the agent selects tools from just their names and descriptions, with no task-specific training examples. That's still exactly how it works. Only the plumbing changed, not the selection paradigm."

**🎯 Standard Interview Answer:** "Zero-shot tool selection — conditioning solely on tool name and description without few-shot exemplars — remains the operative paradigm. The change was in the invocation mechanism and execution substrate, not in the selection regime."

---

**🎙️ Interview Q2:** "Explain LangGraph's three core concepts."

**✅ Strong answer:** "**Nodes, edges, state.**

- **Node** — a step. A Python function that takes the current state and returns an update.
- **Edge** — an arrow. Which node runs next.
- **State** — the shared object every node reads and writes.

**Everyday example:** a flowchart where each box is a node, each arrow an edge, and there's one clipboard passed between all the boxes — that's the state.

The thing that makes LangGraph different from a DAG tool like Airflow or a CrewAI crew is that **arrows are allowed to point backwards.** That's a cycle, and it's what makes agentic behaviour possible — think, use tool, think again, use another tool, answer.

The key detail people miss: a node returns only its **update**, a small dict, not the whole state. LangGraph merges it in using the reducer defined on each field."

**🎯 Standard Interview Answer:** "Nodes are units of work implemented as functions from state to a partial state update. Edges define transition relations between nodes. State is a typed shared object, conventionally a `TypedDict`, threaded through execution. LangGraph's distinguishing property relative to DAG orchestrators is support for cyclic transitions, which is a precondition for iterative agentic control flow. Nodes return partial updates rather than complete state; merge semantics are determined per-field by the reducer specified in the state annotation."

---

**🎙️ Interview Q3:** "What is `Annotated[list, add_messages]` doing?"

**✅ Strong answer:** "It's declaring the **merge rule** for that field.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

Without the annotation, when a node returns `{"messages": [...]}`, LangGraph would **overwrite** the field. With `add_messages`, it **appends** instead — which is what you want for a conversation.

So the annotation answers: 'when two things write to this key, how do I combine them?' That function is called a **reducer**.

`add_messages` also does something subtler — it deduplicates by message ID and handles updates to existing messages, which is what makes streaming and message editing work.

The broader point: `messages` is just the common case. You define whatever state you want — `user_id`, `retry_count`, `documents`, `approved` — each with its own reducer. A counter might use `operator.add`; a flag might just overwrite."

**🎯 Standard Interview Answer:** "The annotation specifies a reducer — a binary merge function applied when a node returns an update for that key. Default semantics are replacement; `add_messages` substitutes append semantics with message-ID-based deduplication and in-place update support, which underpins streaming and message revision. Reducers are per-field and arbitrary: `operator.add` for accumulators, replacement for scalars, custom functions for domain-specific merge logic. The state schema is user-defined; `messages` is conventional rather than required."

**🔁 Interview Q3 (follow-up):** "What happens if two parallel branches write to the same field with no reducer?"

**✅ Strong answer:** "You get an error — LangGraph raises `InvalidUpdateError` rather than silently picking one. That's deliberate and good: with no reducer, there's no defined way to combine two concurrent writes, and guessing would produce non-deterministic results. The fix is to define a reducer for that field so concurrent updates have well-defined merge semantics."

**🎯 Standard Interview Answer:** "LangGraph raises `InvalidUpdateError`. Absent a reducer, concurrent writes to a single key have no defined resolution, and the framework fails explicitly rather than applying arbitrary precedence. Remediation is specifying a reducer that defines associative merge semantics for the field."

---

**🎙️ Interview Q4:** "What's the difference between `.invoke()` and `.stream()`?"

**✅ Strong answer:** "Same graph, same execution — the difference is what you get back and when.

- **`.invoke()`** returns only the final state, once everything finishes.
- **`.stream()`** yields each node's update as that node completes.

```python
for event in graph.stream({"messages": [("user", q)]}):
    for node_name, update in event.items():
        ...   # one iteration per node that finishes
```

So the loop runs once per completed node, and each iteration hands you that node's output.

**Everyday example:** same journey either way — `invoke` tells you where you arrived, `stream` gives you live updates along the route.

Practically: use `stream` for anything user-facing, because waiting 20 seconds in silence for a multi-step agent is a bad experience. Use `invoke` when you just need the result, like a batch job."

**🎯 Standard Interview Answer:** "Both execute the identical graph; they differ in result delivery. `invoke` returns the terminal state synchronously on completion. `stream` yields incremental updates keyed by node name as each superstep completes, enabling progressive rendering. Stream modes further control granularity — `updates` for per-node deltas, `values` for full state snapshots, `messages` for token-level streaming. User-facing agents require streaming because multi-step trajectories have latency incompatible with synchronous response; batch contexts favour `invoke`."

---

**🎙️ Interview Q5:** "What is a checkpointer, and why can't state handle memory on its own?"

**✅ Strong answer:** "Because **state only lives for one invocation.** It's built at the start of the run and discarded at the end — so a follow-up call would start empty.

The checkpointer saves state and reloads it on the next call with the same `thread_id`. Crucially it saves **after every node**, not just at the end, which is what also gives you crash recovery and time-travel.

And it's not a log you read afterwards — it **rehydrates** the state, so the next invoke starts with the previous conversation already in `state["messages"]`, and the model sees full history without you re-sending anything.

The one-liner: **state is working memory during a run; the checkpointer is what makes it survive between runs.**"

**🎯 Standard Interview Answer:** "State has invocation-scoped lifetime — instantiated at graph entry and discarded at termination — so cross-invocation continuity requires external persistence. The checkpointer serialises state after each superstep, keyed on thread identifier, and deserialises it on subsequent invocation with the same key, restoring execution state as the starting point rather than merely recording it. Per-superstep granularity additionally enables fault recovery from the last durable checkpoint and time-travel to arbitrary prior checkpoints."

**🔁 Interview Q5 (follow-up):** "`InMemorySaver` versus `SqliteSaver` versus `PostgresSaver`?"

**✅ Strong answer:** "`InMemorySaver` is stateful but **not durable** — it lives in RAM, so everything is gone when the process restarts. Fine for notebooks and tests, wrong for production.

`SqliteSaver` persists to a file — good for single-instance deployments and local development.

`PostgresSaver` is the production answer when you have multiple app instances, because they all need to read the same checkpoint store. With SQLite on local disk, instance B can't see the thread instance A was serving."

**🎯 Standard Interview Answer:** "`InMemorySaver` provides in-process state continuity without durability; state is lost on process termination, restricting it to development and testing. `SqliteSaver` provides file-backed durability suitable for single-instance deployments. `PostgresSaver` provides shared durable state across horizontally scaled instances, which is required whenever request routing is not sticky — a local SQLite checkpoint is invisible to sibling instances, producing apparent memory loss under load balancing."

---

**🎙️ Interview Q6:** "Explain threads. Is a thread many conversations?"

**✅ Strong answer:** "No — inverted. **A thread *is* one conversation.** It holds many turns. One user can have many threads.

So the hierarchy is: user → many threads → many messages within each.

**Everyday example:** a thread is a single WhatsApp chat window, not your whole inbox.

Mechanically it's just a key: you pass `config={"configurable": {"thread_id": "abc"}}` and the checkpointer saves and loads under that key. Same `thread_id` continues the conversation; a new one starts fresh.

The design decision worth mentioning: **what you use as `thread_id` defines your conversation boundary.** User ID means one eternal conversation. User ID + session means a new one per visit. That's a product decision, not a technical one."

**🎯 Standard Interview Answer:** "A thread is a single conversation scope containing an ordered sequence of turns; the cardinality is user-to-many-threads, thread-to-many-messages. Operationally the thread identifier is the checkpointer partition key, supplied via the runnable config. Thread-identifier selection determines conversation boundary semantics — user-scoped identifiers produce a single unbounded conversation, session-scoped identifiers produce per-session isolation — and is a product-level rather than technical decision."

**🔁 Interview Q6 (follow-up):** "What's the difference between the checkpointer and the store?"

**✅ Strong answer:** "**Checkpointer is within-thread; store is cross-thread.**

The checkpointer holds this conversation's state. The store holds things that should outlive any single conversation — user preferences, learned facts, profile data.

Concretely: the checkpointer remembers you asked about pricing two messages ago. The store remembers you're an enterprise customer who prefers technical detail, learned three months ago in a different conversation."

**🎯 Standard Interview Answer:** "The checkpointer persists thread-scoped graph state, replayed in full at invocation. The store persists cross-thread, typically namespace-and-key-scoped data — user preferences, extracted facts, profile attributes — accessed by retrieval rather than replay, since it exceeds context capacity. Short-term versus long-term memory maps directly onto checkpointer versus store."

---

**🎙️ Interview Q7:** "What are conditional edges, and what's the difference between deterministic and agentic routing?"

**✅ Strong answer:** "A conditional edge is an arrow whose destination is decided by a function at runtime:

```python
graph.add_conditional_edges("chatbot", route_fn, {"tools": "tools", "end": END})
```

`route_fn` reads the state and returns which way to go.

The distinction that matters: **it's about what's inside the routing function, not whether the graph branches.**

- **Deterministic routing** — plain Python. `if state['messages'][-1].tool_calls: return 'tools'`. No LLM, predictable, free, testable.
- **Agentic routing** — the function asks an LLM to decide. Flexible, but costs a call and is non-deterministic.

The standard tool-calling loop is *deterministic* routing even though it looks agentic — the model decided whether to emit a tool call, but the routing function just inspects whether one exists. That's a check, not a judgment.

I'd default to deterministic and only use an LLM router when the decision genuinely needs semantic understanding of the input."

**🎯 Standard Interview Answer:** "Conditional edges delegate transition selection to a function evaluated against current state, returning a key mapped to a destination node. The deterministic-versus-agentic distinction concerns the routing function's implementation, not graph topology. Deterministic routing implements branch selection in code — inspecting state predicates such as tool-call presence — yielding zero inference cost, determinism and testability. Agentic routing delegates to a model, incurring latency, cost and non-determinism in exchange for semantic discrimination. The canonical tool-calling loop is deterministically routed despite superficially agentic appearance, since the routing predicate merely inspects whether the prior completion contained tool calls."

---

**🎙️ Interview Q8:** "How does human-in-the-loop work in LangGraph?"

**✅ Strong answer:** "Via `interrupt`, and it only works because of the checkpointer.

The mechanism: a node calls `interrupt(payload)`, execution **stops**, the current state is checkpointed, and control returns to your application. The payload is what you show the human. Later you resume with `Command(resume=value)` and the graph picks up from exactly that point.

The important part is that this is **durable, not blocking.** The process isn't sitting there waiting — state is on disk. The human can approve three days later, from a different machine, and the graph resumes correctly. That's only possible because the checkpointer saved everything.

Typical uses: approving an irreversible action before it happens, editing the agent's proposed tool arguments, or providing missing information.

The design point worth stating: **you can't add HITL to a system without durable state.** They're the same capability."

**🎯 Standard Interview Answer:** "Human-in-the-loop is implemented via `interrupt`, which suspends execution at an arbitrary point within a node, checkpoints current state, and surfaces a payload to the caller. Execution resumes through `Command(resume=value)`, reconstituting state from the checkpoint and continuing from the interrupt site. The mechanism is durable rather than blocking — no process remains resident — so approval latency is unbounded and may span process restarts or different client sessions. Applications include pre-execution approval of irreversible operations, tool-argument review and editing, and elicitation of missing information. Durable interruption is a direct consequence of checkpointing; human-in-the-loop is not implementable without it."

---

**🎙️ Interview Q9:** "What's a superstep, and why does it matter?"

**✅ Strong answer:** "LangGraph executes in **supersteps** — borrowed from the Pregel model. In one superstep, every node scheduled to run executes, potentially in parallel, and *then* their updates are merged into state through the reducers. One combined checkpoint is written per superstep.

Why it matters practically:

**Parallel nodes don't see each other's updates.** Two nodes in the same superstep both read the pre-superstep state. If you expected node B to see node A's write, it won't — they're concurrent.

**Checkpoints are per-superstep, not per-node.** So time-travel granularity is the superstep.

**This is where `InvalidUpdateError` comes from** — two parallel nodes writing the same key with no reducer defined.

People hit this when they add a parallel branch and are surprised the branches can't see each other."

**🎯 Standard Interview Answer:** "LangGraph adopts the Pregel bulk-synchronous parallel model: within a superstep, all scheduled nodes execute concurrently against the state snapshot from the preceding superstep, after which their partial updates are merged via reducers and a single checkpoint is committed. Consequences: nodes co-scheduled in a superstep observe pre-superstep state and cannot see sibling updates; checkpoint and therefore time-travel granularity is the superstep rather than the node; and concurrent writes to a reducer-less key produce `InvalidUpdateError` at merge time. This model is the source of most surprises when introducing parallel branches."

---

**🎙️ Interview Q10:** "When would you use `create_agent` versus building a `StateGraph` yourself?"

**✅ Strong answer:** "This is the live question now that the old LangChain-versus-LangGraph framing is obsolete — `create_agent` *is* LangGraph underneath.

**Use `create_agent`** when the standard loop fits: model, tools, reason until done. It's a prebuilt graph, it's well-tested, and you skip the boilerplate. Most single agents are this.

**Build a `StateGraph`** when you need something the prebuilt loop can't express: custom state fields beyond messages, a specific node order, approval gates at particular points, parallel branches, or multi-agent topologies like supervisor patterns.

The honest guidance: **start with `create_agent`, drop to `StateGraph` when you hit a wall.** Writing a custom graph for a standard tool-calling loop is reinventing something that already works."

**🎯 Standard Interview Answer:** "`create_agent` is a prebuilt LangGraph graph implementing the standard tool-calling loop, so the distinction is not framework selection but abstraction level. It is appropriate where the canonical loop suffices — model, tool set, iterate to termination. Explicit `StateGraph` construction is warranted for custom state schemas beyond message history, non-standard node ordering, interrupt placement at specific points, parallel execution branches, or multi-agent topologies such as supervisor or swarm architectures. The recommended progression is to default to the prebuilt constructor and descend to explicit graph construction when a requirement exceeds it."

---

## Sources

- [LangGraph State: Checkpoints, Threads, and Recovery](https://eastondev.com/blog/en/posts/ai/20260424-langgraph-agent-architecture/)
- [Top 35 LangGraph Interview Questions (2026) — Interview Coder](https://www.interviewcoder.co/blog/langgraph-interview-questions)
- [LangGraph Interview Questions & Answers (2026 Guide) — Cloud Soft Solutions](https://cloudsoftsol.com/interview-questions/langgraph-interview-questions-answers/)
- [LangGraph Advanced Interview Questions & Answers](https://agenticaiquestions.com/langgraph-interview-questions-answers/)
- [The best AI agent frameworks in 2026 — LangChain](https://www.langchain.com/resources/ai-agent-frameworks)
- [Comparing Open-Source AI Agent Frameworks — Langfuse](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)

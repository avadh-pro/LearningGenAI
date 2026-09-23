# Week 4 — AI Agents

**A complete, self-contained study reference.**

This file consolidates everything from Week 4 of the *Guided Projects in Generative AI* course — ten sessions and eight notebooks — into one document you can read end to end without opening anything else. Where the course material has been overtaken by events (and in one case it has been overtaken *badly*), the current 2026 position is stated inline with a source link, and collected again in [§12 Important updates since the course notes](#12-important-updates-since-the-course-notes).

**What Week 4 actually covers:** how to stop writing pipelines and start writing systems that decide their own steps.

| # | Section | The one-line version |
|---|---|---|
| 1 | [What an AI agent is](#1-what-an-ai-agent-is) | A model that *acts*, not one that answers |
| 2 | [Single-agent architecture](#2-end-to-end-architecture-of-a-single-agent) | Seven layers, arranged like a tiny operating system |
| 3 | [Multi-agent systems](#3-multi-agent-systems) | Hire a team when one worker's context window fills up |
| 4 | [LangGraph](#4-designing-stateful-ai-agents-with-langgraph) | Shared state + explicit graph = control over the flow |
| 5 | [Choosing a framework](#5-choosing-a-framework-the-four-rung-ladder) | Four rungs: LCEL → single agent → CrewAI → LangGraph |
| 6 | [MCP](#6-mcp--the-model-context-protocol) | A USB-C port for tools, so N×M integrations become N+M |
| 7 | [Evaluation & observability](#7-agent-evaluation-and-observability) | Grade the *working*, not just the answer |
| 8 | [Serving with FastAPI](#8-serving-ai-agents-with-fastapi) | The agent doesn't change; you wrap it |
| 9 | [The guided projects](#9-the-four-guided-projects) | Market research, conversational BI, document drafter, MCP server |
| 10 | [The notebooks](#10-the-eight-notebooks) | Eight runnable references, mapped to the concepts |
| 11 | [Production gaps](#11-what-every-course-build-deliberately-leaves-out) | Retry, cache, cost caps, parallelism |
| 12 | [2026 updates](#12-important-updates-since-the-course-notes) | MCP went **stateless**; read this before quoting the MCP section |
| 13 | [Interview prep](#13-interview-prep) | Twelve questions, two answer layers each |
| 14 | [Glossary](#14-glossary) | Every term in one place |

---

## The analogy that runs through this whole document 🏢

A **plain LLM** is a very well-read person locked in a room with no phone: they can tell you things, but they can't *do* anything.

A **single agent** is that person given a desk, a phone, a filing cabinet, and a to-do list. They can now look things up, call people, and take action — but they're one person doing one job at a time, and their desk only holds so much paper.

A **multi-agent system** is the moment you stop hiring one generalist and start hiring a **team**: a manager who splits the work, specialists who each own one piece, a shared filing cabinet everyone can read, and an agreed way to talk to each other.

**MCP** is the building's universal power socket: instead of every employee wiring their own custom cable to every device, everyone plugs into the same standard outlet.

**Evaluation and observability** is the CCTV plus the performance review: you record what everyone actually did, then grade the work.

**FastAPI** is the front door and reception desk that lets the outside world place an order at all.

Every section below is one of those pieces.

---

## 1. What an AI Agent Is

### 1.1 The definition that actually separates it from a chatbot

A traditional chatbot **receives a message and produces a response**. It might have conversational memory, but the interaction is fundamentally request → response. Traditional automation is **`if`/`else` code and scripts** — deterministic, and it breaks the moment reality doesn't match the branches you wrote.

An **AI agent** sits between them: the LLM is used as a **decision engine**, not a text generator. Given a goal, it decides *what to do next*, does it, looks at the result, and decides again.

> 🧑‍✈️ **The picture:** a chatbot is a phone operator reading from a script. An agent is a personal assistant who can actually go and book the flight.

### 1.2 The loop

```
   ┌─────────────────────────────────────────────────────┐
   │                                                     │
   ▼                                                     │
receive input/context                                    │
   │                                                     │
   ▼                                                     │
plan the next action  ◄── memory + tool descriptions     │
   │                                                     │
   ▼                                                     │
call a tool / query knowledge                            │
   │                                                     │
   ▼                                                     │
observe the result ──────────────────────────────────────┘
   │        (not done yet → loop again)
   ▼   (done)
produce the answer, write to memory
```

**The single most important property:** the number of iterations is **not known in advance**. A fixed pipeline always takes the same number of steps. An agent takes as many as the problem needs — which is exactly why an agent *must* have an explicit termination condition (a max-iteration cap, a "done" signal, or both) or it will loop until your budget runs out.

### 1.3 The four capabilities

| Capability | What it means | Concrete example |
|---|---|---|
| **Perception** | How the agent takes in information | Text input, API responses, database rows, file contents, sensor data |
| **Reasoning** | Deciding what to do with it | "The user wants a refund; I need the order first, so call `search_orders`" |
| **Action** | Actually doing it | Executing `initiate_refund(order_id="A77", amount=49.99)` |
| **Learning** | Getting better next time | Thumbs-up/down feedback feeding a later training or prompt-refinement loop |

> ⚠️ **The honest caveat on learning.** Of the four, learning is by far the weakest in real production agents. Most systems you will actually build **perceive, reason, and act — but do not learn**, because they don't update model weights between requests. What gets *called* learning in practice is much shallower: writing to memory so context carries forward, logging thumbs-down signals for humans to review, or retraining later on collected feedback. Learning is the only one of the four pointed at the *next* request rather than the current one, and it's the one most likely to be aspirational in your architecture diagram.

### 1.4 Agents vs RAG — the distinction interviewers are actually testing

**The one-liner: RAG makes the model *know* more; an agent makes the model *do* more.**

| Aspect | RAG | Agent |
|---|---|---|
| **Core purpose** | Ground generation in retrieved domain knowledge | Solve tasks needing reasoning, planning, tool interaction |
| **Mechanism** | Retrieval system + generative model | LLM plans, reasons, invokes tools iteratively |
| **Focus** | Information augmentation from a static knowledge base | Multi-step task-solving, real-time decisions |
| **Knowledge source** | A predefined document repository | Any tool — APIs, search, calculators, databases |
| **Control flow** | **Static** — a DAG, forward only | **Dynamic** — cycles and conditional branching |
| **Who decides the order of steps** | You, at design time | The LLM, at runtime |
| **Termination** | Implicit (end of the pipeline) | **Must be explicit** |
| **Dependency** | Retrieval quality | Tool availability + the LLM's reasoning ability |

**The same question, to both — *"Is our Q3 revenue above target?"*:**

| | What happens |
|---|---|
| **RAG pipeline** | Searches the docs once, finds a chunk mentioning Q3 revenue, answers from it. If the *target* figure lives in a different document, it never finds it and answers incompletely — it only ever gets one shot. |
| **Agent** | Queries the revenue database → sees the number → realises it still needs the target → queries the targets doc → compares → *then* answers. Three steps here; a simpler question might take one. |

**Two sharpenings worth saying out loud in an interview:**

1. Use the precise vocabulary — **static vs dynamic control flow**, a **DAG** versus a **stateful graph with cycles**. That's the phrasing the interviewer is listening for.
2. Say *"the **path** is deterministic,"* not *"it's deterministic."* RAG's generation step is still stochastic; only the control flow is fixed.

**They are not competitors.** In a multi-agent system, one agent can *be* an entire RAG pipeline wrapped as a single node — the supervisor routes to it like any other node, without caring that retrieval, reranking, and generation are all happening inside it. Week 3's Legal Query Resolution system is exactly this shape: RAG at its core, with agentic components (a confidence-gated route, query decomposition) layered on top.

> 📚 **The rule of thumb:** reach for an agent only once a fixed pipeline has actually failed you. Agents are strictly more expensive, slower, and harder to debug.

### 1.5 Single-LLM vs multi-LLM agents

| Aspect | Single-LLM agent | Multi-LLM agent |
|---|---|---|
| Architecture | One model does everything | Several models, each specialised |
| Complexity | Simple | Orchestration required |
| Task handling | Bounded by one model's strengths | Handles diverse, multi-step work |
| Cost | Lower | Higher infrastructure + coordination latency |
| Example | A support bot on GPT-class model: analyse query, fetch info, respond | Content pipeline: one model ideates, one edits grammar/style, one optimises for SEO |

**Getting it wrong in either direction has a real cost.** Over-applying multi-model orchestration to a simple task adds failure surface and latency with no capability gain. Under-applying it leaves one model straining at a job it was never suited for, with no way to specialise.

> **A practical note from the Market Research session:** mixing providers across a sequential pipeline is *not* itself a problem — each agent just receives text and acts on it, with no dependency on which model produced that text. The one real risk is when one step generates a *prompt or instruction* for the next model to follow: prompting conventions that work well for one provider don't always transfer cleanly to another.

### 1.6 The six agent types — a ladder, not a menu

**1. Simple reflex agent** — decides only from the *current* input. No memory.
> Ask *"tell me a joke"* → it tells one. Ask *"can you repeat that joke?"* → it has no idea what you mean. One perception, one condition, one action, nothing carried forward.

**2. Stateful (model-based) agent** — maintains an internal model of the world, updated each turn.
> *"What is the capital of France?"* → *"Paris."* Then *"what's its population?"* → *"about 2.1 million."* It carried "France"/"Paris" forward to resolve "its".

**3. Goal-based agent** — evaluates actions against whether they move toward an objective, considering future states.
> *"I need a flight from New York to London tomorrow."* → *"What time?"* → *"Evening."* → *"There's a 7pm flight — shall I book it?"* Every question serves the one goal.

**4. Utility-based agent** — uses a utility function to weigh **competing** objectives and maximise overall usefulness.
> *"I'm frustrated that my account was deactivated."* The agent weighs apologise / escalate to a human / reactivate immediately / offer credit, and picks the combination scoring highest for satisfaction: *"I'm very sorry — let me reactivate your account immediately, and I'll add a $10 credit."*

**5. Learning agent** — improves from experience, via four sub-components:
> - **Learning element** — updates knowledge from feedback
> - **Performance element** — makes decisions from current knowledge
> - **Critic** — evaluates how actions turned out
> - **Problem generator** — suggests exploratory actions
>
> When ChatGPT asks *"which response do you prefer?"*, that's the critic gathering the signal the learning element will use.

**6. Hierarchical agent system** — splits a task across agents at different layers.
> A marketing-campaign generator with four agents in sequence: pick the topic → plan the content → write it → quality-check it.

> 🪜 **How they connect:** reflex has no memory; stateful adds memory; goal-based adds a target; utility-based adds a way to weigh *competing* targets; learning adds improvement over time; and hierarchical is what you get when the job is big enough to split across *several* agents, each of which may internally use any of the five approaches above.

### 1.7 When *not* to build an agent

- The steps are always the same → write the pipeline. It's cheaper, faster, and debuggable.
- The rules are fully known → write the `if`/`else`. An LLM adds cost and non-determinism for nothing.
- You need a guaranteed answer shape every single time → a chain with structured output beats an agent that *might* loop.
- **You haven't tried a pipeline yet.** Build the simple thing, watch where it fails, and let the failure justify the agent.

---

## 2. End-to-End Architecture of a Single Agent

### 2.1 The mini-operating-system analogy 🖥️

A single agent is best understood as a **tiny operating system**. Every layer maps onto something you already know:

| Layer | OS equivalent | What it actually does |
|---|---|---|
| **Interface** | Keyboard & screen | Receives the request, returns the response |
| **Controller** | The kernel | Runs the loop; decides continue vs stop; enforces limits |
| **Reasoner** | The CPU | The LLM call that picks the next action |
| **Tools** | Installed programs | Functions/APIs the agent can invoke |
| **Memory** | The filesystem | Short-term, long-term, and semantic storage |
| **Policy & safety** | File permissions | Who may do what, and to which records |
| **Observability** | Task Manager + system log | Traces, latency, token usage, cost, success rate |

### 2.2 Interface — the front door

Carries the request in and the answer out. Typical fields:

| Field | Why it exists |
|---|---|
| `user_id` | Authorisation and personalisation |
| `session_id` | Ties this turn to the conversation |
| `input_text` | The actual request |
| `locale` | Language/format of the reply |
| `channel` | Web, mobile, Slack — affects formatting |
| `request_id` | The handle every log line and trace is keyed by |

It's also where **timeouts** and **iteration limits** are declared — the controller enforces them, but the interface is where the caller states them.

### 2.3 Controller — the loop that stops

The controller is the part people forget, and it's the part that keeps an agent from running forever. It:

1. Receives the validated request.
2. Assembles context (memory + tool schemas + system prompt).
3. Calls the reasoner.
4. Validates the reasoner's chosen tool against its schema.
5. Checks policy.
6. Executes the tool and captures the structured result.
7. Decides: loop again, or stop.
8. Writes the outcome to memory and returns.

**Steps 4, 5, and 7 are the controller's real job.** Step 7 in particular: the agent stops when the reasoner says `stop: true`, *or* when the iteration cap is hit, *or* when the timeout fires — whichever comes first.

### 2.4 Reasoner — structured output, not prose

The reasoner is one LLM call whose job is to pick the next action. The critical design decision is **what shape its output takes**.

```json
{
  "tool": "search_orders",
  "stop": false,
  "rationale": "Need the order record before a refund can be issued."
}
```

| | Free text | Structured JSON |
|---|---|---|
| Machine-readable | ✗ — needs parsing/guessing | ✓ — direct dispatch |
| Auditable | Hard — rationale is buried in prose | ✓ — `rationale` is its own field |
| Schema-validatable | ✗ | ✓ — reject malformed output and retry |
| Description vs execution | *Describes* what it would do | *Is* the instruction |

**One line:** free text tells you what the model was thinking; structured output *is* what the system does next.

### 2.5 Tools — and how a tool call actually executes

```
  reasoner picks a tool
          │
          ▼
  controller validates the call against the tool's JSON schema
          │            ✗ invalid → reject, feed the error back, re-reason
          ▼ ✓
  policy check: is this user allowed to call this tool, on this record?
          │            ✗ denied → return a policy error, do not execute
          ▼ ✓
  tool executes (API call / DB query / computation)
          │
          ▼
  structured response: { data, execution_time_ms, error, status }
          │
          ▼
  appended to state; controller decides loop or stop
```

**Why the response is structured, not just data:** `execution_time_ms` feeds observability, `status` and `error` let the controller distinguish "the tool failed" from "the tool returned nothing" — a distinction the LLM will happily blur if you hand it a bare string. An agent that hallucinates a plausible answer *around* a silent tool error is one of the most common production failure modes there is.

### 2.6 Memory — three kinds, three lifetimes

| Type | Lifetime | Holds | Backed by |
|---|---|---|---|
| **Short-term** | One session | The current conversation, intermediate results | Graph state, an in-process dict, Redis |
| **Long-term** | Across sessions | User preferences, past decisions, audit history | Postgres, MongoDB |
| **Semantic** | Indefinite | Domain knowledge, retrieved by meaning | A vector store — **this is where RAG plugs in** |

Semantic memory is the seam between Week 3 and Week 4: your entire RAG pipeline becomes one memory subsystem of one agent.

### 2.7 Policy & safety — three checkpoints, not one

| When | Checks |
|---|---|
| **Pre-execution** | Is this user authorised for this tool? For this record? Is the argument within allowed bounds (refund ≤ order total)? |
| **During execution** | Constraint enforcement — row-level filters, tenant scoping, rate limits per call |
| **Post-execution** | PII scrubbing, output filtering, redaction before the result reaches the user or the log |

A single "is this allowed?" gate at the top is the common mistake. The *post*-execution pass matters just as much: a tool can legitimately return data the user isn't allowed to see.

### 2.8 Observability — the minimum fields

| Field | Answers |
|---|---|
| `trace_id` | Which request was this? (the parcel-tracking number) |
| per-step latency | Where did the time go? |
| token usage in/out | Where did the context go? |
| cost | What did this request cost? |
| tool call log | Which tools, with what arguments, returning what? |
| success/failure | Did it complete, and if not, at which step? |

Without this, an agent failure is unattributable. When a plain LLM gives a wrong answer you at least know where to look. When an *agent* does, the fault could be in retrieval, planning, tool selection, argument construction, or the final synthesis — and only trace data tells you which.

### 2.9 Worked example — a refund request

> **Request:** *"I want a refund for my last order."* · `user_id: C123`

| Step | Layer | What happens |
|---|---|---|
| 1 | Interface | Receives `{user_id: "C123", input_text: "...", session_id: "s-9"}` |
| 2 | Controller | Loads C123's session memory; assembles tool schemas for `search_orders`, `initiate_refund` |
| 3 | Reasoner | Returns `{tool: "search_orders", stop: false, rationale: "Need the order before refunding."}` |
| 4 | Controller | Validates args against schema ✓ |
| 5 | Policy | C123 may read **their own** orders ✓ |
| 6 | Tool | `search_orders(customer_id="C123", limit=1)` → order `A77`, $49.99, delivered 3 days ago |
| 7 | Reasoner | Returns `{tool: "initiate_refund", stop: false, rationale: "Order is within the 30-day window."}` |
| 8 | Policy | Refund amount ≤ order total ✓; C123 owns A77 ✓ |
| 9 | Tool | `initiate_refund(order_id="A77", amount=49.99)` → `{status: "ok", eta_days: 5}` |
| 10 | Reasoner | Returns `{tool: null, stop: true, rationale: "Refund issued; nothing left to do."}` |
| 11 | Memory | Writes: refund issued for A77 on this date |
| 12 | Observability | Logs trace, 2 tool calls, 3 LLM calls, latency, tokens, cost |

> 🧾 Notice that **policy runs twice** — once per tool call, not once per request. Step 8's amount check is the one that stops a prompt-injected *"refund me $4,999"* from going through.

### 2.10 Why single agents break: context bloat

The textbook reason to go multi-agent is "specialisation." The **practical** reason, from the Document Drafter session, is blunter: **context window exhaustion.**

One agent that pulls from a knowledge base, then calls an API, then queries a database accumulates *all* of that context in one window. Add a long conversation history and the agent runs out of room mid-task. Splitting across agents fixes this structurally: each sub-agent receives **only the fields it needs**, does its piece, and returns **only what the next step requires**.

> **The design rule:** pass the minimum state that produces the maximum output. If the supervisor holds ten fields and the sub-agent needs two, pass two.

---
## 3. Multi-Agent Systems

### 3.1 Why one agent isn't always enough

A single-agent setup is one loop responsible for understanding the task, decomposing it, executing it, **and** verifying the result. That's fine for simple linear work. It becomes a bottleneck once the work is complex, distributed, or needs several kinds of competence at once.

Distributing across specialised agents buys three things a single agent structurally cannot give you:

- **Specialisation** — each agent tuned for one capability, instead of one model trying to be good at everything.
- **Scalability** — subtasks run in parallel, across different tools, models, and compute environments.
- **Reliability** — when one agent's output is uncertain, another can verify, correct, or augment it, instead of a single point of failure deciding alone.

…plus the practical fourth reason from §2.10: **context isolation**.

**One line:** a single agent does the whole job serially and checks its own work; a multi-agent system splits the job, runs pieces in parallel, and lets agents cross-check each other.

> ⚠️ **The counter-caveat, stated directly in the Document Drafter session:** more specialisation also means more complexity, more LLM calls, and more cost. With modern long-context models, two "specialists" you carefully separated may be better merged into one. Nobody can tell you the right number of agents for your use case from first principles — you find it by experimenting.

### 3.2 The four building blocks

| Component | Role | Team analogy |
|---|---|---|
| **Agents** | Specialised workers — reasoning, retrieval, planning, tool execution | The specialists |
| **Coordinator / orchestrator** | Assigns tasks, resolves conflicts, drives toward the goal | The manager |
| **Shared memory / context store** | Intermediate results, conversation state, task progress | The shared team doc |
| **Communication protocol** | Messages, API calls, graph edges | How they actually talk — Slack, tickets, whatever |

### 3.3 The four collaboration patterns

#### Planner–Executor
A **planner** breaks the request into a structured sequence of steps — effectively generating a mini-workflow. An **executor** performs each step: calling APIs, running tools, retrieving data.

*Why it's useful:* separating "decide the steps" from "carry out the steps" gives deterministic execution, clearer reasoning, and much easier debugging. This is the single most widely used pattern in real agentic systems, and it's what you're watching when ChatGPT or Claude shows a "thinking" block followed by tool calls.

#### Supervisor–Worker
The user talks to one **supervisor**, which interprets the query, breaks it into subtasks, and routes each to the best-suited **worker**. Workers each handle one capability — possibly running several internal steps — and the supervisor collects, merges, and verifies before returning.

*Why it's useful:* mirrors how real organisations work, so it scales well to tasks that genuinely need several competencies in parallel.

```
        User Request
             │
             ▼
     ┌───────────────┐
     │  Supervisor   │  interprets & decomposes
     └───────┬───────┘
      ┌──────┼──────┐
      ▼      ▼      ▼
  Worker  Worker  Worker
 (retrieval)(reason)(tools)
      └──────┼──────┘
             ▼
     ┌───────────────┐
     │  Supervisor   │  merges & verifies
     └───────┬───────┘
             ▼
      Final Response
```

#### Critic–Refiner
A **generator** produces a fast, broad first draft. A **critic-refiner** evaluates it for correctness, completeness, style, safety, or domain constraints — and can rewrite, fix hallucinations, or add missing detail.

*Why it's useful:* high-stakes domains where you need *both* fast creative generation *and* careful verification, without either degrading the other.

#### Peer-to-Peer (decentralised)
No central orchestrator. Agents trigger each other directly — a knowledge agent tells a memory agent to update a fact without waiting for a supervisor.

*Why it's useful:* a supervisor is a bottleneck **and** a single point of failure on *every* interaction, including trivial ones. For high-frequency, low-ambiguity exchanges where there's no decision to make and no conflict to resolve, routing through a manager adds latency for nothing.

| Pattern | Structure | Best for |
|---|---|---|
| **Planner–Executor** | Plan first, then execute step by step | Deterministic, well-defined multi-step tasks |
| **Supervisor–Worker** | Central supervisor delegates to specialists | Complex tasks needing several competencies in parallel |
| **Critic–Refiner** | Draft, then a second agent verifies/improves | High-stakes domains needing speed *and* verification |
| **Peer-to-Peer** | Agents trigger each other directly | Continuous state sync, autonomous background work |

**Planner–executor vs supervisor–worker — the difference people miss:** it's *what* gets delegated. Planner-executor hands over a **fixed ordered sequence** that an executor works through linearly. Supervisor-worker hands over whole **subtasks** to specialists who each have autonomy over their own internal execution, possibly in parallel, and the supervisor's real job is merging and verifying what comes back. *"Here's your checklist, go"* versus *"here's your piece of the problem, use your judgment, report back."*

> **These patterns nest.** A "specialist" behind a router can itself be a whole multi-agent system. A planner-executor's executor step can internally be supervisor-worker. Treat them as composable shapes, not mutually exclusive architectures.

### 3.4 Real-world applications

| Domain | How the work splits |
|---|---|
| **Customer support automation** | Planner identifies intent → response agent drafts → evaluator verifies accuracy and tone before sending |
| **Enterprise AI assistance** | One agent retrieves → another generates structured reports → a third validates compliance |
| **Research co-pilots** | Researcher explores sources → extractor pulls relevant info → summariser condenses |
| **Software automation** | Planner decomposes → an agent interacts with the UI/workflow → a validator checks results |

### 3.5 State, memory, and agent communication

Three distinct things that get conflated:

- **State** — the data flowing between agents *during one run*. Keep it minimal per hop (§2.10).
- **Memory** — what survives *between* runs. Conversational history for a chat agent; audit logs for a workflow agent.
- **Communication** — how an agent knows *when* to call another agent or a tool. In practice this lives in the **prompt**: you must explicitly describe, per agent, which tool or peer to reach for and under what conditions. "The agents figure it out" is not a design.

---

## 4. Designing Stateful AI Agents with LangGraph

### 4.1 What "stateful" actually buys you

> 📋 **The analogy:** without statefulness, every node is an isolated island and you hand-carry every input and output between steps. LangGraph's answer is a **shared clipboard** in the middle of the workflow: every node reads what's on it, adds its own notes, and passes it along. Nobody has to remember to hand anything over — it's just *there*.

Capabilities that fall out of having one central state object:

- **Shared memory** — every node has read/write access to the same state.
- **Automatic persistence** — a checkpointer saves state to memory, SQLite, Postgres, Redis.
- **Human-in-the-loop** — pause, get a human decision, resume from exactly where it stopped.
- **Time travel / replay** — every node's inputs and outputs are checkpointed, so you can trace precisely which node caused a failure.
- **Multi-turn conversation** — history, tool results, and intermediate reasoning persist without manual bookkeeping.

### 4.2 The core components

| Component | Role |
|---|---|
| **State** | The shared store, declared upfront via `TypedDict` or a Pydantic model |
| **Nodes** | Python functions: receive state, do work, return an update |
| **Edges** | Connect nodes; a plain edge always goes A→B |
| **Conditional edges** | Route based on a function's return value |
| **Entry point** | Which node runs first (`START` or `set_entry_point`) |
| **`END`** | The reserved sentinel meaning "stop here" |
| **StateGraph** | The container; `.compile()` produces a runnable app |
| **Checkpointer** | Persists state — `MemorySaver`, `SqliteSaver`, `PostgresSaver` |

**How state updates merge:** by default a node's return value **overwrites** that field. For fields that should accumulate (a running message list), a **reducer** controls the merge — `add_messages` is LangGraph's built-in reducer for exactly that. Write a custom reducer for any other merge behaviour.

### 4.3 The build pattern — every single time

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. Declare the state
class State(TypedDict):
    messages: Annotated[list, add_messages]   # appends, doesn't overwrite
    topic: str                                # overwrites
    outline: str

# 2. Nodes are plain functions: state in, partial update out
def plan(state: State):
    return {"outline": make_outline(state["topic"])}

def write(state: State):
    return {"messages": [draft_from(state["outline"])]}

# 3. Wire the graph
builder = StateGraph(State)
builder.add_node("plan", plan)
builder.add_node("write", write)
builder.add_edge(START, "plan")
builder.add_edge("plan", "write")
builder.add_edge("write", END)

# 4. Compile, then invoke
app = builder.compile()
app.invoke({"topic": "vector databases", "messages": []})
```

Two details worth internalising:
- A node returns a **partial** update — only the keys it changed — not the whole state.
- The checkpointer is registered **once, at compile time** (`builder.compile(checkpointer=...)`), not per node.

### 4.4 Conditional edges: deterministic vs agentic routing

This is the sharpest concept in the whole LangGraph session, and it's a favourite interview trap.

```python
builder.add_conditional_edges(
    "grade_documents",       # from this node
    decide_to_generate,      # run this function
    {                        # map its return value to a destination
        "web_search": "transform_query",
        "generate": "generate",
    },
)
```

The routing function must return **exactly one value**: a node name, or `END`. What's *inside* it decides whether the routing is agentic:

```
Routing function contains:

  if score < 0.6: return "web_search"     ← plain Python  = DETERMINISTIC routing
  else:           return "generate"

  llm.invoke("which node next?")          ← an LLM call   = AGENTIC routing
```

**Same mechanism, same graph, same `add_conditional_edges`. Only the decision-maker changes.** This is why "pipeline vs agent" is a spectrum, not a switch — and why a threshold gate like `if confidence < 0.60` is *branching*, *adaptive-looking*, and still **not agentic**: a human picked 0.60, and the same score always routes the same way.

**And even when the LLM does decide**, it almost always picks from a **predefined list** of nodes via structured output — not open-ended invention. "The LLM decides" means it chooses among paths you already built. That's why the supervisor pattern returns a schema-constrained value rather than free text:

```python
from pydantic import BaseModel, Field
from typing import Literal

class RouteDecision(BaseModel):
    tool: Literal["sql", "stats"] = Field(description="Which retriever to use")

decision = llm.with_structured_output(RouteDecision).invoke(query)
```

### 4.5 Checkpointers, threads, and human-in-the-loop

A **checkpointer** snapshots the full state after every superstep, keyed by a **thread ID**. That thread ID — passed in a `configurable` dict — is what makes "resume the *right* paused conversation" possible.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

def approval_node(state):
    decision = interrupt({"draft": state["draft"]})   # pauses here
    return {"approved": decision}

app = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "user-42-session-9"}}

app.invoke({"draft": "..."}, config)                    # runs, then pauses
# ... human reviews out of band ...
app.invoke(Command(resume="approve"), config)           # continues from the interrupt
```

**Two things must exist or interrupt/resume simply won't work:**
1. A **checkpointer**, so the paused state is actually saved somewhere rather than lost.
2. A **thread config**, so the system knows *which* paused execution to resume.

And note the resume call: you pass `Command(resume=...)`, **not** a fresh input. A plain `invoke` would re-enter the graph at its entry point instead of continuing from the interrupted node.

> 🛡️ **Why this pattern exists, in one story from the session:** an agent operating without a human checkpoint deleted a piece of AWS infrastructure code and caused roughly 13 hours of impact. Any action that is expensive, destructive, or externally visible belongs behind an interrupt.

**In production, use a durable checkpointer.** `MemorySaver` is for experimentation only — it dies with the process. `SqliteSaver` or `PostgresSaver` is what survives a restart.

### 4.6 Sub-graphs

A node can be a **compiled sub-graph**. From the parent's perspective it's one node; internally it can be an entire multi-agent system, or a whole RAG pipeline. This is the mechanism behind the "one agent can be a RAG pipeline" point from §1.4, and it's how large agentic systems stay comprehensible.

### 4.7 The eleven agent architecture patterns

The LangGraph session builds all eleven in one notebook, simplest first.

**1. Sequential (fixed linear flow)** — same path every time, no branching.
> `plan → write → review → END`. Each node reads only the state fields it needs.
> **Reach for it when:** the steps never change — pipelines, ETL, document processing.

**2. Supervisor / Router** — classify, then a conditional edge routes to the matching specialist. Unexpected category → a general-purpose fallback. Each specialist path ends directly; there's no routing back.
> **Reach for it when:** the first real decision is simply "which specialist handles this."

**3. Parallelization (fan-out / aggregate)** — call several nodes concurrently, then an aggregator waits for all of them and merges. In the session this leans on plain Python (`concurrent.futures` + a thread pool) more than on LangGraph-specific machinery.
> Pros / cons / risks analysed in parallel, then combined into one executive summary.
> **Reach for it when:** subtasks are genuinely independent and latency matters.

**4. Reflect / Critic** — generator produces, evaluator checks, fail → loop back and regenerate, pass → end. A `maxIterations` cap (3 in the session) prevents an infinite retry loop.
> ⚠️ **The caveat that matters:** if the evaluator is *also* just an LLM call, it shares the generator's blind spots — an LLM that gets a fact wrong can just as easily be fooled by its own wrong answer, because it's assessing *plausibility*, not correctness. A trustworthy retry gate needs a signal the generator doesn't have: rule-based domain checks, semantic-similarity scoring against a reference, or real precision/recall/factual-correctness metrics against ground truth.

**5. Human-in-the-Loop** — `interrupt` + `Command(resume=...)`, as in §4.5.
> Email agent drafts → pauses for review. Approve → send as-is. Edit → send the human's replacement. Reject → cancel.
> **Reach for it when:** the action is high-risk or externally visible.

**6. Tool Use** — the agent is given tools (plain Python functions registered with a `@tool` decorator); the LLM decides whether a call is needed; the result feeds back into its reasoning.
> **Reach for it when:** the answer depends on data or an action the LLM can't produce alone.

**7. Network (decentralised multi-agent)** — several agents (strategist, analyst, critic) can each call *any* of the others, with a max-iteration cap.
> Asked whether a 10-person startup should adopt microservices, the graph went strategist → analyst → strategist → analyst, hit the cap, and terminated. A prompt tweak (telling the model its current iteration count and nudging it toward the critic) shaped the behaviour without adding a stricter structural guarantee — which is exactly the trade-off of this pattern.
> **Reach for it when:** the right next agent genuinely depends on what's been discussed.

**8. Custom Multi-Agent (fixed workflow)** — multiple steps, always the same order, with an error branch.
> `intake → validate → process → format → END`, branching on validation failure.
> **Reach for it when:** you want pipeline reliability but the steps are complex enough to deserve separate nodes.

**9. Planning (planner → executor → synthesizer)** — planner emits a structured plan (JSON list of steps); executor works through them sequentially *or* in parallel (so this pattern nests #1 and #3); synthesizer merges the results.
> **Reach for it when:** the task must be decomposed and you don't know the steps in advance.

**10. ReAct (Reason + Act)** — thought → action → observation → repeat, until there's enough to answer. Iteration cap of 5 in the session.
> **One line:** ReAct is Tool Use (#6) and Reflect (#4) fused — reason, act, observe, and keep re-reasoning, instead of one tool call and one quality check.

**11. Team / Leader + specialised members** — a leader calls several member agents (marketing, engineering, legal), each with its own tools and curated prompt; a synthesizer merges their contributions and resolves overlaps.
> Planning a SaaS launch: marketing estimates go-to-market, engineering estimates a six-month timeline and cost, legal checks compliance — and the synthesizer reconciles two separate cost estimates into one total.
> **Reach for it when:** the job is genuinely large enough to need a hierarchy. The session flags this as increasingly common in production.

#### Pattern cheat sheet

| Pattern | Shape | Reach for it when… |
|---|---|---|
| Sequential | Fixed linear path | The steps never change |
| Supervisor / Router | Classify, then branch | You must pick among specialists |
| Parallelization | Fan-out, then aggregate | Subtasks are independent and speed matters |
| Reflect / Critic | Generate → evaluate → retry | The agent should self-correct against a quality bar |
| Human-in-the-Loop | Pause → human decides → resume | The action is high-risk |
| Tool Use | Agent decides whether to call a tool | The answer needs external data or action |
| Network | Agents call each other, no fixed order | The next step depends on the discussion so far |
| Custom Multi-Agent | Fixed multi-step workflow | Reliable pipeline, complex individual steps |
| Planning | Plan → execute → synthesize | Sub-steps aren't known in advance |
| ReAct | Reason → act → observe, repeat | The agent must think *and* use tools iteratively |
| Team / Leader | Leader delegates, then synthesizes | The job needs a genuine hierarchy |

**Real systems combine these.** A leader/team architecture where each specialist internally runs ReAct, one of them being a RAG sub-graph, with a human-in-the-loop gate before the final write — that's a perfectly ordinary production shape.

### 4.8 What changed in LangGraph since the session

LangChain and LangGraph both reached **v1.0 on 22 October 2025**, and LangGraph **1.2** shipped **11 May 2026** ([LangChain blog](https://blog.langchain.com/langchain-langgraph-1dot0/), [changelog](https://docs.langchain.com/oss/python/releases/changelog)). The core model taught in the session — state, nodes, edges, conditional edges, checkpointers, `interrupt`/`Command` — is unchanged and still correct. What's new around it:

- **`create_agent` is now the single idiomatic way to build a LangChain agent.** `initialize_agent`, `AgentExecutor`, and `langgraph.prebuilt.create_react_agent` are all superseded and live in `langchain-classic`, with end-of-life messaging pointing at December 2026. The Week 4 `LangChain Agents.ipynb` notebook already uses `create_agent`, so it's current.
- **Durable execution is first-class.** The pluggable checkpointer abstraction is the supported way to survive a server restart — an agent run resumes rather than restarting.
- **Middleware** lets you attach cross-cutting behaviour (prompt tweaks, tool overrides, guardrails) around an agent without editing the call site.

---

## 5. Choosing a Framework: the four-rung ladder

### 5.1 The ladder

| Use | When | Example |
|---|---|---|
| **LCEL chain** | Straight flow, every step is one fixed call | *Summarise this document* |
| **Single agent** (`create_agent`) | One worker that picks tools and loops | *Answer this, using search + calculator* |
| **CrewAI Crew** | Several specialists handing off in order, each agentic internally | *Research → analyse → write* |
| **LangGraph** (or a **CrewAI Flow**) | The handoffs themselves must loop back, branch, or pause | *Draft → review → revise until it passes → human approves* |

### 5.2 ❌ The correction that will cost you an interview

**It is wrong to say "LangChain has no agents, it's just a pipeline."**

LangChain **has** agents — that's precisely what `create_agent` is (and `AgentExecutor` before it was superseded). A LangChain agent picks its own tools, reads results, and loops until done.

The valid contrast is **LCEL chain vs CrewAI agent**, not *LangChain vs CrewAI*.

**So what does CrewAI actually add over a LangChain agent?** Not the reasoning — the **team abstraction**: roles, goals, backstories, and the handoff plumbing between *several* agents. You could wire three `create_agent` calls together and get the same result with more boilerplate. **That's ergonomics, not capability.**

### 5.3 "Straight flow" doesn't settle it — look *inside* each step

- **LCEL chain:** straight flow, and each step is **one deterministic call** — prompt → model → parse. A step cannot choose a tool or decide to try again.
- **CrewAI:** straight flow *between* agents, but each agent is **autonomous inside** — it picks which tools to call, how many times, and when it's done.

> **Example — "research the EV market and write a report."** With an LCEL chain you hardcode the research: run *these three* searches, feed the results into a summarise prompt. If one topic needs three searches and another needs eight, the chain can't adapt — you baked the number in. With CrewAI, the researcher agent gets a *goal* and a search tool and decides for itself how many queries to run. **The handoff is straight; the work inside isn't.**

### 5.4 CrewAI: Crews vs Flows

```python
# CrewAI Crew — you declare WHO and WHAT, never the flow
from crewai import Agent, Task, Crew, Process

researcher = Agent(role="Market Researcher", goal="Find EV market data",  backstory="...")
writer     = Agent(role="Report Writer",     goal="Turn findings into a report", backstory="...")

t1 = Task(description="Research the EV market",  agent=researcher)
t2 = Task(description="Write a summary report",  agent=writer)

Crew(agents=[researcher, writer], tasks=[t1, t2], process=Process.sequential).kickoff()
```

Notice what's absent: you never wrote *"after t1, go to t2."* The process handles sequencing. LangGraph makes you draw every arrow — which is the whole point:

```python
# LangGraph — you declare the FLOW explicitly
builder.add_node("research", research_fn)
builder.add_node("write", write_fn)
builder.add_edge("research", "write")
builder.add_conditional_edges("write", check_quality, {"retry": "research", "done": END})
```

**Two processes:**
- `Process.sequential` — tasks run in list order.
- `Process.hierarchical` — requires `manager_llm` or `manager_agent`; the manager LLM decides delegation and validates outputs. It does *not* freely reorder tasks.

> **A precision point worth having right:** Crews are **acyclic**, not stateless. Task outputs pass forward and memory exists. What's missing is going *backward*. And each agent inside a Crew runs its own internal tool → observe → decide loop — the crew-level flow is linear, the agent-level flow isn't.

**Flows** are CrewAI's answer to the branching/pausing gap, and are architecturally much closer to LangGraph than to Crews: `@start`, `@listen`, `@router`, `@persist`, plus `@human_feedback` (requires **CrewAI ≥ 1.8.0**). A Flow can pause durably — `kickoff()` returns `HumanFeedbackPending`, state is automatically saved at that moment (`SQLiteFlowPersistence` by default), and you continue with `flow.resume()`, or `await flow.resume_async()` inside an async framework like FastAPI (calling the sync version from a running event loop raises `RuntimeError`).

> ⚙️ **`@persist` gotcha:** put it on a single **terminal** step, not on the whole Flow class. Class-level persist saves after *every* method, and `load_state` reads the latest row — which can be a mid-run snapshot that misses handler updates from the same turn. It's the bank-transfer-mid-transaction problem: you're choosing your commit point, so choose it deliberately.

| | CrewAI **Crews** | CrewAI **Flows** | LangGraph |
|---|---|---|---|
| You define | Roles + tasks | `@start` / `@listen` / `@router` steps | State + nodes + edges |
| Control flow | Framework decides handoffs | Event-driven, you route explicitly | You decide, explicitly |
| Loops / retries | Awkward | ✅ `@router` | Native — cycles are the point |
| Conditional routing | Hard to express | ✅ `@router` | Exactly what conditional edges are for |
| Durable pause / resume | ✗ — `human_input=True` blocks | ✅ `HumanFeedbackPending` + `resume()` | ✅ checkpointer + `interrupt` |
| State persistence | — | ✅ SQLite default, pluggable | ✅ SQLite / Postgres / Redis |
| Speed to build | Fast | Medium | Slower, more verbose |

**One line:** Crews trade control for speed by hiding orchestration behind a role/task metaphor; LangGraph trades speed for control by making you write the graph; CrewAI Flows sit deliberately in between — so the real question is usually *Crews or Flows*, not *CrewAI or LangGraph*.

### 5.5 The wider field in 2026

| Framework | Abstraction | Where it fits |
|---|---|---|
| **LCEL** | Lowest-ceremony | Deterministic chains |
| **LangChain `create_agent`** | Low | One agent, tools, a loop |
| **CrewAI Crews** | High | Role-based teams, linear handoff; **AMP** adds managed deployment, observability, and governance (launched January 2026) |
| **CrewAI Flows** | Medium | Event-driven, branching, durable pause |
| **Agno** (formerly Phidata) | Medium–high | Agents / Teams / Workflows SDK plus **AgentOS**, a FastAPI-based runtime owning durable state, sessions, and traces |
| **LangGraph** | Low | Maximum explicit control; the reference implementation for cyclic stateful graphs |
| **Google ADK** | Medium | Strong when you need protocol-level interop — **MCP** and **A2A** |

**Two framework notes from the sessions:**
- *When does CrewAI stop being the right answer?* When the project's complexity outgrows what its abstractions let you customise. At that point LangGraph's lower-level control stops being extra work and starts being the thing that saves you.
- *CrewAI vs Google ADK:* CrewAI for flexible multi-agent collaboration and rapid prototyping; ADK once you're integrating multi-protocol setups (MCP, A2A agent-to-agent collaboration).

> 📌 **Naming update:** the Week 4 notebook `Agentic RAG with Phidata.ipynb` imports from `phi`. **Phidata was renamed Agno in January 2025** (GitHub org moved to `agno-agi`), and the modern package is `agno`. The notebook still works if you pin the old package, but new work should target Agno — see [§12.5](#125-phidata-is-now-agno).

---
## 6. MCP — the Model Context Protocol

> ⚠️ **Read [§12.1](#121-mcp-went-stateless--the-biggest-change-in-this-whole-document) before quoting anything from this section in an interview.** The course session is an excellent explanation of MCP as it stood, but the **2026-07-28 specification made MCP stateless at the protocol layer** and deprecated sampling. §6.1–6.9 present MCP as taught (and as most deployed servers still behave); §6.10 and §12.1 give the current position.

### 6.1 What MCP is *not*

Clearing these four confusions up front is half the battle:

| MCP is not… | Because… |
|---|---|
| **A replacement for APIs** | It's a **wrapper/integration layer on top of** APIs. An MCP server consumes existing APIs and exposes them over a standard channel. |
| **Just function calling** | It's a full **protocol** for describing, discovering, and invoking tools — the way HTTP is a protocol for the web — rather than a per-framework convention. |
| **An agent or an LLM** | An MCP server holds tools. A tool *may* be LLM-backed, or may be a plain function. The server itself is neither. |
| **An orchestration framework** | LangChain/LangGraph orchestrate the *agent*. MCP standardises the *connection between the agent and its tools*. |

> 🔌 **The one-line pitch everyone uses, and it's a good one: MCP is USB-C for AI.** A standard interface that lets a model plug into external tools, databases, files, and APIs without a bespoke adapter for each combination.

### 6.2 The N×M problem — the reason MCP exists

**Without MCP:** every application needs a custom integration for every tool. Three AI applications × four tools = **12 integrations**. Switch one app from LangChain to another library and you rewrite that app's tool-integration code for all four tools, while still maintaining the others.

**With MCP:** each application implements an MCP **client** once; each tool lives behind an MCP **server** once. Three clients + four servers = **7 connections**.

```
WITHOUT MCP  (N × M = 12)          WITH MCP  (N + M = 7)

App A ──┬──► Tool 1                App A ──► client ─┐
        ├──► Tool 2                                  │
        ├──► Tool 3                App B ──► client ─┼──► MCP ──┬──► Server 1 (Tool 1)
        └──► Tool 4                                  │  protocol├──► Server 2 (Tool 2)
App B ──┬──► Tool 1                App C ──► client ─┘          ├──► Server 3 (Tool 3)
        ├──► ...                                                └──► Server 4 (Tool 4)
App C ──┴──► ...
```

**Three consequences worth stating separately:**

1. **Swap the framework, keep the tools.** Rewrite the chatbot in a different library and you only re-implement the *client*. The servers don't change.
2. **Tools don't have to live with the agent.** The calendar API can run in Google Cloud inside an MCP server while the chatbot runs on AWS. No shared codebase.
3. **Teams stop shipping each other code.** Team A drops an MCP server on a cloud host; Team B points a client at it. No copying source, no re-implementing the integration.

### 6.3 Host, client, server

```
┌──────────────── HOST APPLICATION ────────────────┐
│  (Claude Desktop, an IDE assistant, your app)    │
│  • creates/manages/destroys clients              │
│  • owns permissions & security policy            │
│  • coordinates the LLM, aggregates context       │
│                                                  │
│   ┌──────────┐   ┌──────────┐                    │
│   │ Client 1 │   │ Client 2 │  ← one stateful    │
│   └────┬─────┘   └────┬─────┘    session each    │
└────────┼──────────────┼──────────────────────────┘
         │ JSON-RPC 2.0 │
         ▼              ▼
   ┌───────────┐  ┌───────────┐
   │ Server A  │  │ Server B  │   lightweight programs
   │ DB tools  │  │ file tools│   exposing tools/resources/prompts
   └───────────┘  └───────────┘
```

| Role | Responsibilities |
|---|---|
| **Host** | Creates, manages, and can restart/delete client instances. Owns connection lifecycle, **permissions, and security policy**. Coordinates LLM integration and aggregates context across clients. |
| **Client** | Maintains **one stateful session per server**. Handles protocol negotiation and message routing. Enforces its own security boundaries, and handles subscriptions/notifications (server ready, server blocked). |
| **Server** | Hosts the primitives — tools, resources, prompts. Executes the work. Accesses local resources *and* remote APIs. Must comply with the host's security constraints. |

**Key structural rule:** one client ↔ one server, over one persistent connection. A host may run many clients. A single-LLM workflow typically has one client; a multi-agent architecture may give **each agent its own client** with its own server access — which is also the natural place to enforce different permissions per agent.

> 🔐 **Why the permission boundary lives in the host, not the client:** the client should never be the thing that says *"this user isn't allowed to run that."* The host decides when a client is exposed to a user at all. Design your server split the same way — if one agent needs the relational DB and another needs both relational and non-relational, give each database its own server rather than handing both clients access to everything. **Server boundaries are access-control boundaries.**

### 6.4 Why JSON-RPC 2.0

MCP is built on **JSON-RPC 2.0** — an existing remote-procedure-call protocol that supports **bidirectional** communication, where either party can act as caller or callee.

As originally designed, MCP needed that two-way channel because of **sampling** (§6.6): a server mid-execution can turn around and ask the *client's* LLM to do something for it.

**The request/response shape is fixed:**

```jsonc
// client → server: "what tools do you have?"
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {} }

// server → client
{ "jsonrpc": "2.0", "id": 1,
  "result": { "tools": [ { "name": "get_weather",
                           "description": "Current weather for a city",
                           "inputSchema": { "type": "object",
                                            "properties": { "city": {"type": "string"},
                                                            "unit": {"enum": ["celsius","fahrenheit"]} },
                                            "required": ["city"] } } ] } }

// client → server: "run it"
{ "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": { "name": "get_weather", "arguments": { "city": "Paris", "unit": "celsius" } } }
```

`resources/list` and `prompts/list` follow the identical shape. Cancellation and error handling ride the same envelope: if the client can't supply a required parameter, it tells the LLM to ask the user for the missing input rather than guessing.

### 6.5 The end-to-end call flow

```
user input
   │
   ▼
HOST (+ LLM)  ── any pre-processing
   │
   ▼
CLIENT  ──1──► connect to server
        ──2──► tools/list          (discover what's available)
        ◄──3── list of tools
        ──4──► tools/call          (run the one the LLM picked)
        ◄──5── result
        ──6──► (repeat 4–5 for further tool calls as needed)
   │
   ▼
HOST + LLM  ── aggregate all tool responses → final answer to the user
```

Step 2 is the part that doesn't exist in classic function calling: **discovery happens at runtime**, not at development time.

### 6.6 The four primitives

| Primitive | Lives on | Controlled by | What it is |
|---|---|---|---|
| **Tools** | Server | The model | Callable functions the LLM invokes. **This is the one that actually gets used.** |
| **Resources** | Server, surfaced by host | The host app | Read-only static or dynamic data the LLM (or the user) can read — documents, files, database views, addressed by URI |
| **Prompts** | Server, surfaced by host | The **user** | Predefined prompt templates the end user picks before processing starts ("Summarise document", "Draft reply") |
| **Sampling** | Server → client | The client's LLM | The **server** asks the **client** to run an LLM call on its behalf |

**Tool definition** — a name, a description, and a JSON schema for arguments:

```json
{
  "name": "get_weather",
  "description": "Get current weather for a city",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" },
      "unit": { "type": "string", "enum": ["celsius", "fahrenheit"] }
    },
    "required": ["city"]
  }
}
```

**Sampling, concretely:** a tool receives unstructured text but needs it as clean markdown. Rather than embedding its own LLM, the server sends a `sampling/createMessage` request *back* to the client: *"please convert this text to markdown."* The client's LLM does it, returns the result, and the server carries on. That inversion — server acting as caller, client as callee — is the whole reason MCP chose a bidirectional protocol.

> Note: sampling was always the least-used primitive, and as of the 2026-07-28 spec it is **deprecated** in favour of Multi Round-Trip Requests. See [§12.1](#121-mcp-went-stateless--the-biggest-change-in-this-whole-document).

### 6.7 MCP vs classic tool calling

| | Classic tool/function calling | MCP |
|---|---|---|
| **Tool discovery** | Hard-coded in the prompt or the code | **Dynamic at runtime** via `tools/list` |
| **Tool location** | Same process as the LLM | Same machine, a different server, or a different cloud entirely |
| **Transport** | None — in-memory function call | `stdio`, HTTP (streamable); legacy HTTP+SSE |
| **State** | Stateless | *(as taught)* stateful session context — **see §12.1** |
| **Reusability** | Bound to the one LLM/app it was written for | Any MCP-compatible client can call any MCP server |
| **Adding a tool** | Change the application code | Add it to the server and redeploy the **server**; clients discover it automatically |
| **Auth** | Whatever you build | Protocol-level authorization (OAuth-aligned) |

**The "add a tool" row is the one that wins arguments.** A server with three tools grows a fourth; you update the server; every connected client discovers four tools on its next `tools/list`. No application code changes anywhere.

### 6.8 When to use which

| Situation | Use |
|---|---|
| Single LLM app, tools in the same codebase | **Tool calling.** MCP is overkill; convert later if you need to. |
| Tools shared across multiple apps or agents | **MCP.** Expose once, consume from many. |
| You need dynamic tool discovery at runtime | **MCP.** |
| Quick prototype, no infrastructure appetite | **Tool calling.** MCP adds a layer plus auth setup. |
| Tools need persistent state between calls | **MCP** — the protocol has a story for it; with tool calling you're picking a database yourself. *(Caveat: §12.1.)* |
| Exposing tools to external consumers | **MCP.** This is how Slack, CRM vendors, and similar now ship agent-facing capability — the agent-era equivalent of publishing a public API. |

### 6.9 Building one with FastMCP

**FastMCP** is a Python library that sits on top of the official MCP SDK and removes almost all of the protocol boilerplate. Registering a tool is a decorator:

```python
# main.py
from fastmcp import FastMCP
from faker import Faker

mcp = FastMCP("fake-user-data-api")

@mcp.tool
def get_user_profile(username: str) -> dict:
    """Return a consistent fake profile for a username."""
    fake = Faker()
    Faker.seed(hash(username) % (2**32))      # same username → same data
    return {"username": username, "full_name": fake.name(), "email": fake.email()}

@mcp.tool
def get_user_orders(username: str) -> dict:
    """Return the order history for a username."""
    ...

if __name__ == "__main__":
    mcp.run()                                  # stdio — local
    # mcp.run(transport="http", host="0.0.0.0", port=7860)   # remote
```

**Transports:**

| Transport | Use it when | Note |
|---|---|---|
| **stdio** | The server runs locally alongside the host; nothing should be exposed over a network | The default |
| **Streamable HTTP** | The server runs remotely | **The current recommendation** |
| **HTTP + SSE** | — | **Deprecated.** Some clients still require it; new work should use HTTP |

**Testing without writing a client — the MCP Inspector:**

```bash
fastmcp run main.py       # run the server
fastmcp dev main.py       # open the Inspector UI
```

The Inspector acts as a client: connect, hit **List Tools**, fill in arguments, **Run Tool**, and read the raw JSON result plus the server's notification log. It's the fastest way to confirm your schemas are right before any LLM is involved.

**Registering the local server with Claude Desktop** — one command writes the config for you:

```bash
fastmcp install claude-desktop main.py --with faker
# or, for many dependencies:
fastmcp install claude-desktop main.py --with-requirements requirements.txt
```

…which produces an entry in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fake-user-data-api": {
      "command": "uv",
      "args": ["run", "--with", "faker", "fastmcp", "run", "/abs/path/main.py"]
    }
  }
}
```

For a **remote** server you add the entry by hand:

```json
{
  "mcpServers": {
    "api-hf": {
      "command": "npx",
      "args": ["mcp-remote", "https://<your-space>.hf.space/sse", "--transport", "sse-only"]
    }
  }
}
```

**Restart Claude Desktop after every config change** — it reads the file at startup. The first tool invocation prompts for permission; "always allow" persists it.

**Deploying to Hugging Face Spaces** (free, good for demos — *not* for production traffic):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
EXPOSE 7860
CMD ["python", "main.py"]
```

Create a **Docker** Space, push `main.py`, `requirements.txt`, and the `Dockerfile`, and set the transport and port to match (`7860`). The Space gets a public HTTPS URL; grab it from **Settings → Embed this Space**.

**Connecting from a framework** — Google ADK:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

agent = Agent(
    name="user_data_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant with access to the fake user data API.",
    tools=[MCPToolset(
        connection_params=StreamableHTTPConnectionParams(url="http://localhost:8000/mcp")
    )],
)
```

LangChain/LangGraph use a different connector class, but the shape is identical: **point at a URL, get a tool set.** Whether that URL is `localhost` or a cloud host is the only thing that changes.

> 🐞 **The error you will hit:** `failed to get tools from toolset` / `failed to create MCP session` means one of exactly two things — your local server isn't running, or the remote URL is wrong/down. It is almost never a code problem.

> 🔀 **The other one:** Claude Desktop required `sse-only` in the session, while the Google ADK path used streamable HTTP. If you're serving both, check which transport each client actually supports before assuming your server is broken.

### 6.10 MCP's neighbours: A2A and the Agentic AI Foundation

**MCP standardises agent ↔ tool.** **A2A (Agent2Agent)** standardises **agent ↔ agent** — one agent talking to another *as a peer with its own capabilities*, rather than as a passive data source.

Current status: Google announced A2A in April 2025 and donated it to the **Linux Foundation** in June 2025. It reached **v1.0.0 in January 2026**, adding signed Agent Cards for cryptographic verification, and by April 2026 had passed **150 supporting organisations** ([Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents), [Google Open Source Blog](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html)).

In **December 2025** the Linux Foundation launched the **Agentic AI Foundation (AAIF)** as a neutral top-level foundation hosting **both MCP and A2A**. Both protocols are now vendor-neutral and community-governed — worth knowing, because "isn't MCP just an Anthropic thing?" is a standard interview probe, and the answer is no, not since late 2025.

---

## 7. Agent Evaluation and Observability

> 🧑‍⚖️ **The analogy:** grading a traditional ML model is checking multiple-choice answers — one correct bubble, machine-scored instantly. Grading an LLM is grading an **essay** — two students can write entirely different sentences and both deserve full marks. And once the test-taker is an **agent** rather than an essay-writer, you're no longer grading the essay at all; you're grading the **working**, step by step.

### 7.1 The feedback loop

```
dataset ──► evaluate ──► deploy ──► monitor ──┐
   ▲                                          │
   └───── human feedback, drift, regressions ─┘
```

Evaluation is what happens **before** deployment; observability is what happens **after**. They're one continuous loop, not two concerns.

**What evaluation actually buys you:**
- **Measuring improvement** — did the model swap / new prompt / different chunk size actually help, or just feel like it did?
- **Detecting regressions** — a model upgrade can quietly make answers shorter, reasoning worse, or tool selection less reliable. Only a standing evaluation suite catches that before a customer does. It is regression testing, for answers.
- **Establishing reliability** — a measured confidence threshold for what the system can be trusted to do, instead of an assumption.

> Without it you're guessing. You test ten queries and conclude the change "improved things." A domain expert testing from the angle of someone who knows where the domain actually gets tricky finds failures your ten queries never touched.

### 7.2 Why LLM evaluation is harder than traditional ML evaluation

| | Traditional ML | LLMs |
|---|---|---|
| **Inference** | Deterministic — same input, same output | Probabilistic — the next token is *sampled* |
| **Output format** | Structured (a class, a float) | Unstructured, varying length and wording every run |
| **Ground truth** | One clear label | Many differently-worded answers can all be correct |
| **Comparison** | Predicted label vs true label | Semantic correctness matters more than text overlap |

*"What is the capital of France?"* can come back as *"Paris is the capital of France"* or *"The capital city of France is Paris."* Both correct. Any metric built on word overlap will score them differently.

### 7.3 The evolution of text-comparison metrics

| Metric | Measures | Strength | Weakness |
|---|---|---|---|
| **BLEU** | N-gram overlap (from machine translation) | Exact-phrase precision | Punishes valid rewording hard |
| **ROUGE** | Recall-based overlap (from summarisation); ROUGE-1 unigram, ROUGE-2 bigram, ROUGE-L longest common subsequence | Content coverage | Same lexical blind spot |
| **METEOR** | BLEU + stemming + synonyms + alignment | Recognises "car" ≈ "automobile" | Still reference-overlap based |
| **BERTScore** | Cosine similarity of **contextual embeddings** | Captures *meaning*; correlates much better with human judgment | Slower; inherits the embedding model's cutoff and domain blind spots |

**The session's own worked run** — reference: *"The cat is sitting on the mat and looking at the window."* Generated: *"A cat sits on the mat while staring at the window."* Same meaning, different words:

| Metric | Score |
|---|---|
| BLEU | 0.29 |
| ROUGE-1 / ROUGE-L | higher (many shared single words) |
| ROUGE-2 | lower (few shared word *pairs*) |
| METEOR | 0.68 |
| **BERTScore** | **0.97** |

**But none of them — BLEU through BERTScore — measures factual correctness, reasoning quality, hallucination, usefulness, or safety.** They tell you how similar two pieces of text are. They say nothing about whether either one is *right*.

### 7.4 LLM-as-judge

Use a *second* LLM to read the question and the answer and score it against explicit criteria — correctness, completeness, relevance, groundedness — the way a human grader would, instead of comparing token overlap against a fixed reference at all.

**TruLens** uses a **ground-truth-agreement** feedback function: traditional metrics (BLEU, ROUGE) blended with an LLM-as-judge prompt, run alongside BERTScore for comparison. In the session's own run, for an answer that was semantically correct but worded very differently from the reference, BLEU/ROUGE/BERTScore landed anywhere from 0.3 to 0.9 while the judge score consistently landed at 0.9–1.0 — correctly recognising the answer as right.

**DeepEval** ships built-in metrics for common architectures — faithfulness, contextual relevancy, contextual precision/recall, hallucination, answer relevancy, bias, toxicity, latency — plus **G-Eval**, a framework for *your own* judge criteria. G-Eval gives the judge a task description and evaluation criteria, has it generate its own chain-of-thought evaluation steps, and *then* produces a score — much closer to how a human works through a rubric than one opaque number.

**The differentiator, stated directly in the session:** TruLens gives you its own fixed ground-truth-agreement score but doesn't let you define arbitrary custom judge criteria the way G-Eval does. If you need a bespoke rubric — "correctness" and "helpfulness" exactly as *your* task defines them — DeepEval is the tool.

> **Should the judge be the same model as the generator?** Usually no need. A smaller/cheaper model is generally fine for evaluation even when a larger reasoning model handles the main task — evaluation rarely needs the same depth, and the cost/latency saving is real. (Separately, see the correlated-failure caveat in §4.7 pattern #4: an LLM judging *its own kind of mistake* is the weak case.)

### 7.5 Why agent evaluation goes further still

An agent isn't a text generator — it's a **multi-step system**. Evaluating it means checking far more than the final answer.

**Typical agent failure points, from the instructor's field experience:**
- **Wrong plan at the start** — a bad initial plan poisons everything downstream.
- **Wrong tool selected**, or the right tool called with wrong arguments — producing a tool-level error the LLM then hallucinates a plausible answer around.
- **Too many reasoning steps**, or incorrect reasoning along the way.
- **"Correct but incomplete."** A SQL agent correctly queries and retrieves the right data, then silently drops a column (customer geography) when summarising the result table — despite an explicit instruction to reflect everything. The answer *looks* right and *is* sourced from real data, and it's still wrong.
- **Excessive tool-calling** — an agent that keeps re-invoking a tool hoping for a better response, with no upper bound unless you build one.

**Why fixed-reference metrics break down for agents specifically:**
- **No gold reference may exist** — creative writing, open-ended explanation, coding assistance.
- **Multiple valid answers** — the same API call is correctly written in several languages or libraries.
- **Reasoning matters, not just output** — you want to verify the intermediate reasoning was genuine, not that the model hallucinated a plausible answer from prior knowledge while skipping the work.
- **Tool usage matters** — right tool, valid arguments, schema-correct output.
- **The process matters** — the path taken, not just where it ended.

**One line:** for a plain LLM, evaluation is mostly about *outcome* quality. For an agent it must cover *execution* quality too — because a wrong answer might trace to planning, tool selection, or reasoning, and **you can't fix what you can't locate**.

**Agent-specific metrics are now first-class in the tooling.** DeepEval ships metrics for **tool selection, tool calling, tool quality, plan adherence, plan quality, logical consistency, and execution efficiency**; TruLens ships purpose-built agentic evaluators. These are the metric names to reach for, rather than trying to express agent quality in BLEU ([DeepEval](https://deepeval.com/blog/top-5-llm-evaluation-frameworks), [TruLens](https://www.trulens.org/)).

### 7.6 Observability

**Observability means capturing internal system behaviour:** user input, intermediate reasoning at every node, tool calls and their outputs, latency, token usage, errors, trace logs.

**The standard architecture:**
```
run the agent on a UAT / evaluation set
        │
        ▼
trace and log every internal parameter
        │
        ▼
extract metrics per node   (which metric depends on what that node produces —
        │                   e.g. BLEU for a node with one fixed expected response)
        ▼
monitoring dashboard: latency, alignment scores, BERTScore, per input/output pair
```

**The full production lifecycle:** offline evaluation + online monitoring + human feedback + regression testing + drift testing → feeding a continuous improvement pipeline that loops indefinitely as real usage accumulates.

> ⚠️ **A scoping rule worth memorising, from the live Q&A:** **observability** (latency, tokens, general performance) belongs in *both* dev and production. **Evaluation pipelines** belong in **dev/UAT only** — running them against live production traffic means storing real user input in ways that typically shouldn't happen.

**Custom steps need explicit instrumentation.** Framework components (LangChain/LangGraph nodes, LLM calls, tool calls) auto-instrument. A function you wrote by hand — a custom fusion step, a bespoke cleaner — appears in no trace unless you wrap it yourself. And note what is *not* in a per-request trace at all: **chunking and embedding**, because those happen during offline ingestion, not during the request.

### 7.7 MLflow for tracing and evaluation

**Automatic tracing** — one line captures every node, LLM call, and tool call:

```python
import mlflow
mlflow.langchain.autolog()
```

**Custom spans** for anything autolog can't see, because it's your business logic rather than a framework event:

```python
with mlflow.start_span(name="safety_check") as span:
    span.set_input(response)
    verdict = contains_unsafe_content(response)
    span.set_output(verdict)
    span.set_attributes({"policy_version": "v3"})
```

The session's two examples: a **safety check** span (does the response contain anything dangerous or illegal?) and a **length gate** span (is it within 200 words?) — neither of which `autolog` would ever capture.

**`mlflow.evaluate()`** runs a full evaluation batch with MLflow's built-in metrics (answer correctness, faithfulness) plus your own — including a custom LLM-as-judge "conciseness" metric with worked low/high examples to calibrate the judge. **TruLens and DeepEval functions can be registered as custom metrics inside an MLflow run**, so the three tools are complementary, not competing.

> 🐛 **A real bug hit live, worth keeping:** `mlflow.evaluate()` stored only the **averaged** score across the evaluation set, not a per-example breakdown — individual rows' scores were lost in the aggregate. The fix is a custom function capturing per-row results explicitly. **Check for this on *any* evaluation tool before assuming per-example granularity is preserved by default.** A mean of 0.82 hides whether that's "everything is mediocre" or "most are perfect and three are catastrophic," and those need completely different fixes.

**Is MLflow part of the agent?** No — it runs as its own server/UI, and the integration is code-level (`autolog()` hooking LangChain's internal events), **not** a REST call the agent makes at runtime. MLflow isn't mandatory; any custom logging, or Weights & Biases, substitutes fine.

### 7.8 The practical strategy — layer everything

No single method is sufficient alone:

| Layer | Role |
|---|---|
| **Reference metrics** (BLEU/ROUGE/BERTScore) | Cheap, fast baseline signal |
| **LLM-as-judge** | Semantic correctness reference metrics can't capture |
| **Agent-specific metrics** | Faithfulness, answer relevancy, tool-usage correctness, plan adherence |
| **Heuristic rules** | Fixed checks — length limits, safety keyword filters |
| **Human review** | Ground truth, fed back into fine-tuning or prompt refinement |

**Post-evaluation actions map to where the problem lives:** architectural changes, prompt engineering, tool argument-schema validation, RAG knowledge-base improvements, retry/recovery logic, human-in-the-loop gating, cost/latency optimisation, context-window management.

**Comparing several models for the same use case:** run the same input set through all of them, capture every response, score them all with the *same* library, store results as JSON/CSV, compare on a dashboard. Provider playgrounds are fine for comparing a plain **LLM** — but a playground can't represent an **agent's** multi-step structure, so once you're evaluating an agent you need code-based evaluation.

> **A 2026 note on plumbing:** the industry has converged on **OpenTelemetry GenAI semantic conventions** as the wire format for LLM/agent traces. TruLens, among others, now emits every function call, LLM generation, retrieval, and tool invocation as a structured OTEL span, which means traces export to Jaeger, Grafana Tempo, Datadog, or any OTLP backend rather than being locked into one vendor's UI ([OpenTelemetry](https://opentelemetry.io/blog/2026/genai-observability/)). If you're choosing a tracing stack today, "does it speak OTEL?" is a reasonable first filter.

---

## 8. Serving AI Agents with FastAPI

> 🏪 **The analogy:** a working agent in a notebook is a chef who can cook a great meal — in their own kitchen, for themselves. **Serving** it is opening a restaurant: a menu (endpoints), a front counter that takes orders in a standard format (Pydantic validation), and a door anyone can walk through. The agent never changes; you're wrapping it in a standard interface.

### 8.1 Batch vs online serving

- **Batch (static) serving** — queries accumulate and get processed together on a schedule (every 6 or 12 hours). Users wait for the next run.
- **Online serving** — a query arrives and gets a response in real time, however long the pipeline takes.

Agent serving is essentially always the **online** case.

### 8.2 HTTP in one table

| Verb | Purpose |
|---|---|
| **GET** | Retrieve data |
| **POST** | Send/create data |
| **PUT** | Update existing data |
| **DELETE** | Remove data |

For agent serving, **GET and POST cover almost everything** — you're fetching a result or sending input for the agent to process.

**Status codes matter**, and not as decoration: 200 (success), 201 (created), 400 (bad request), 404 (not found), 500 (server error). Returning the right code is what lets a *client program* — not just a human reading the body — tell success from failure.

### 8.3 FastAPI + Pydantic

**Pydantic** is the validation layer. Declare the shape valid input must take, and FastAPI rejects anything that doesn't match **before your code runs** — no manual `if` checks:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class DraftRequest(BaseModel):
    input_email: str = Field(min_length=1, max_length=10_000)
    session_id: str

class DraftResponse(BaseModel):
    drafted_email: str
    session_id: str

agent = EmailDrafter()          # built once, at import — not per request

@app.post("/draft-email", response_model=DraftResponse, status_code=200)
def draft_email(req: DraftRequest):
    try:
        result = agent.run(req.input_email)         # CrewAI's crew.kickoff() inside
        return DraftResponse(drafted_email=result["raw"], session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Run it:

```bash
uvicorn main:app --reload --port 8000
```

- `--reload` auto-restarts on save (development only).
- `--port` when 8000 is taken or your host assigns a specific port.
- **`/docs`** gives you an auto-generated interactive Swagger UI listing every endpoint, where you can fill in parameters and send real requests without writing a client. It comes free.

**Postman** is the alternative once an API isn't casually browsable — typically once auth is in front of it and developers need a documented, shareable collection. For POST requests: **Body → raw → JSON**. Postman will also generate the equivalent Python `requests` code, which is a genuinely useful handoff artefact.

### 8.4 🔑 The key insight: FastAPI doesn't *integrate* with your agent framework — it *wraps* it

FastAPI is not "talking to" CrewAI or LangGraph. The notebook code that defines and runs your agent is simply **placed inside a route function**. When a request hits that route, that code runs, like any other Python function call.

There is no integration to build. This is why the same serving pattern works unchanged whether the agent is CrewAI, LangGraph, LangChain, or hand-rolled.

**Two things to get right at startup rather than per request:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow.langchain.autolog()        # tracing, once
    app.state.db = connect_db()       # connection pool, once
    app.state.agent = build_agent()   # compile the graph, once
    yield
    app.state.db.close()

app = FastAPI(lifespan=lifespan)
```

Rebuilding a compiled LangGraph or a Crew per request is a common and expensive mistake.

### 8.5 Streamlit as the front end

```python
import requests, streamlit as st

st.title("Email Drafter")
text = st.text_area("Paste the email you received")
if st.button("Draft a reply"):
    r = requests.post("http://localhost:8000/draft-email",
                      json={"input_email": text, "session_id": "s-1"})
    st.success(r.json().get("drafted_email", "No email drafted"))
```

> ⚠️ **The bug hit live in the session:** the FastAPI server was started on port **8001** while Streamlit still pointed at **8000**. Requests silently failed. Check the port on *both* ends before debugging anything else.

> 🪆 **The other one:** CrewAI nests its final text under a `"raw"` key inside the response. Whatever your framework returns, unwrap it explicitly and provide a fallback — `.get("drafted_email", "No email drafted")` — rather than indexing blindly into a nested dict.

### 8.6 Docker and beyond localhost

A production Dockerfile for an agent service installs dependencies from `requirements.txt`, copies the app, **adds a non-root user**, exposes the port, and includes a health check.

> 🔌 **The gotcha that costs an afternoon:** inside a container, `localhost` does not mean what it means outside one. To reach Postgres or MLflow running on the *host* machine you need **`host.docker.internal`**. Running the same code locally, outside Docker? Switch it back to `localhost` in `.env`. Getting this backwards gives you a working dev setup that silently breaks the moment it's containerised.

**Two more deployment notes:**
- Use **Gunicorn** (with uvicorn workers) rather than bare `uvicorn` for production concurrency.
- Run **MLflow outside** the agent's Docker environment — locally, or on its own server writing traces to something like S3. Containerising it alongside the agent was unreliable in the session's setup.

### 8.7 A production lesson worth stealing

An agent deployed fine and ran for two days, then failed: the deployed environment's credentials didn't have permission to reach the database — something local testing never surfaced.

**The fix adopted afterwards: also expose whatever the agent depends on as its own plain endpoint.** A `GET /tables` that just lists database tables. If that endpoint can't reach the database, you know instantly that the agent can't either — a dependency check completely independent of the agent's own success or failure.

### 8.8 Where FastAPI sits in the bigger picture

FastAPI is one tool among many in an MLOps/LLMOps pipeline — alongside MLflow, EvidentlyAI, DeepChecks, Docker, Kubernetes, CI/CD, GitHub Actions, Ansible, Jenkins. **No pipeline needs every tool.** FastAPI's specific job is turning a notebook-bound agent into something reachable by *anything*: a Streamlit prototype, a real website, a mobile app. The one requirement for that to matter beyond your own machine is that it's deployed somewhere reachable — AWS, Azure, GCP — and not left on `localhost`.

---
## 9. The Four Guided Projects

### 9.1 Market Research Copilot — planner-executor, built twice

**The problem:** manual market and compliance research is slow and inconsistent — unstructured sources, 6–12 hours per topic, inconsistent sourcing, no structured validation, hard to audit. The goal isn't automating *data collection* (scraping already does that) — it's adding **structure, auditability, and repeatability**.

**The definition used:** *an orchestrated AI system that decomposes a complex research request into structured tasks and gathers verifiable evidence against which a decision-grade output can be produced.*

> 🕵️ **The analogy:** one agent asked to "research this and write a report" is one person being detective, fact-checker, and ghostwriter at once. They'll cut corners somewhere, and you'll never know which part went wrong. Split it into three: **planner** (decide what to investigate), **researcher** (find evidence), **writer/verifier** (write it, and strip anything without a source). Every claim in the final report should trace back to a URL — the whole architecture exists to make that traceability possible.

**Why planner-executor, and not the alternatives:**

| Pattern | Trade-off |
|---|---|
| Sequential | Deterministic, fully auditable — you know exactly where it failed |
| Parallel | Faster, needs an aggregation step |
| Reflective / Critic | Catches errors, costs extra LLM calls and latency |
| Hierarchical | Good for delegation, more moving parts |

**Planner-executor isn't a fifth pattern** — it's a *role split* (plan vs execute) that can itself run sequentially or in parallel internally. The session chose planner-executor **running sequentially**, because the point was demonstrating clarity and control, not speed.

**What breaks without a planner:** a do-everything agent hallucinates, drifts off the actual scope of the request, and produces output that's hard to verify against what was asked. Splitting planning out gives you explicit goals, defined focus areas, generated sub-queries, and a **repeatability factor** — the same request twice should produce a similarly-structured plan both times.

#### Build #1 — CrewAI

| Agent | Job | Tools |
|---|---|---|
| **Planner** | Turn the request into a structured plan + search queries | None |
| **Researcher** | Find reliable sources, extract facts **with URLs attached** | `SerperDevTool` + `TavilySearchTool` |
| **Writer + Verifier** | Write the report; strip or mark "uncertain" any claim with no source URL | None |

**Why two search providers, not one:** Serper and Tavily return different results and different rankings for the same query. For compliance research specifically, cross-verifiability across multiple sources matters more than using whichever single tool is fastest.

**The plan schema** — a Pydantic model, so the planner's output is validated structure rather than free text:

```python
class ResearchPlan(BaseModel):
    goal: str
    regions: list[str]          # which jurisdictions matter
    focus_areas: list[str]
    queries: list[str]          # the actual search strings
    evidence_rules: list[str]   # "every important claim must have a source URL;
                                #  if unsure, say uncertain instead of guessing"
```

**Why explicit `evidence_rules` matter:** without them, the model phrases things inconsistently between runs — the wording, structure, and completeness of "cite a source" all drift. This is the repeatability concern applied at the prompt level.

**Report structure**, defined in the writer/verifier task: scope and assumptions · key obligations · cross-border transfer notes · enforcement signals from the last 12 months · recommended actions — plus a hard rule never to give legal advice, and a claim-sources table so every claim's URL is visible at a glance.

Run with `crew.kickoff()` and `verbose=True`, which prints every stage (task started, agent's input, agent's final answer, task completed) — genuinely useful for seeing what each agent actually *received*, not just what the crew produced.

> 📋 **Note the data flow:** strictly **forward-only**. No feedback loop, no critic sending work back. Each stage depends only on the one before it. That's a deliberate simplicity choice, not a limitation of the pattern.

#### Build #2 — LangGraph

Same problem, Gemini + Serper, node-by-node, with a Streamlit front end:

```
pass_query → discover_via_serp → clean_data → scrape_news → generate_report
```

| Node | Job |
|---|---|
| `pass_query` | Research-plan generator: identifies product, category, search questions, news queries → into state |
| `discover_via_serp` | Runs the actual Google search via Serper |
| `clean_data` | Filters low-signal results (generic tutorials) and de-duplicates URLs **before** they're wasted on scraping |
| `scrape_news` | Scrapes the **full article text** (Trafilatura), not just search snippets |
| `generate_report` | Sends everything collected to Gemini to synthesise |

**Code organisation, worth copying as a pattern:** prompts in an `llm/` folder, graph structure in `graph/`, cleaning logic in `cleaners/` — separating *what the model is asked to do* from *how the workflow is wired* from *how the data is scrubbed*, so each can change independently.

**Two practical touches:**
- `draw_mermaid_png()` renders the compiled graph as an image — the fastest way to confirm the graph's actual shape matches what you intended, especially once branching appears.
- The report downloads as **JSON as well as markdown**, so the same backend can power a Streamlit prototype *or* a React front end without rework.

#### The comparison the project exists to make

| | CrewAI | LangGraph |
|---|---|---|
| Abstraction | High — Agent/Task/Crew do the wiring | Low — you define every node and edge |
| Speed to build | Faster for straightforward pipelines | Slower, more code up front |
| Control | Limited to what the abstractions expose | Full control over every step and data flow |
| Best fit | Simple, well-understood workflows; prototyping | Growing complexity, custom logic, scaling past the abstractions |

**One line from the session:** CrewAI's abstractions are great until a project's complexity outgrows what they let you customise — at that point LangGraph's lower-level control stops being extra work and starts being the thing that saves you.

---

### 9.2 Conversational Business Intelligence Agent

> 💬 **The analogy:** traditional BI is a **vending machine** — a fixed set of pre-built dashboards, and if what you want isn't a button, you file a request and wait. Conversational BI is **asking a knowledgeable colleague who already knows the database** — you ask in English, they work out which tables matter, write the query, run it, and hand you the answer with a chart if a chart helps. It doesn't replace dashboards; it adds a second path for the questions a fixed dashboard was never built to answer.

| | Traditional BI | Conversational BI |
|---|---|---|
| **Access** | Pre-built dashboards, fixed reports | Plain English, no SQL |
| **Flexibility** | Static — new questions need a technical person | Live — the agent generates the query |
| **Speed for a new question** | Slow (queued behind a data analyst) | Seconds |
| **Output** | Charts and tables | Plus a context-aware plain-English explanation |

**The problem is accessibility, not availability.** Almost every organisation already has the data. The bottleneck is that a *new* cut of it routes through someone technical who's already busy.

#### Architecture

```
Streamlit UI ──POST /chat──► FastAPI ──► LangGraph SQL agent ──► Postgres (business data)
                                │                              └─► Postgres (agent memory)
                                └────────────────────────────────► MLflow (observability)
```

Four endpoints: `chat` (text only), `chart` (text + chart if applicable), plus `history` and `tables` (mainly to verify the system is wired correctly — see §8.7). SQLAlchemy keeps the connection layer database-agnostic, so the business database is swappable.

#### The node flow

| Node | Job |
|---|---|
| **Query rewriter** | Resolves ambiguous follow-ups using conversation history |
| **Intent detector** | One LLM call, yes/no: does this need a chart? |
| **List tables / get schema** | Inspects the **live** database structure |
| **Generate query** | Writes the SQL, grounded in that schema |
| **Check query** | Validates structurally; rewrites only if actually wrong |
| **Run query** | Executes; collects rows and columns into state |
| **Chart config** | If a chart was requested: type, axes, title, as structured JSON |

**Why fetch the schema live instead of hardcoding it in the prompt:** without grounding in what tables and columns *actually exist*, the model invents plausible-sounding names and the query fails. For 10, 20, even 50 tables, listing them live is cheap and removes the failure mode entirely. At much larger scale you'd need a retrieval step instead of listing everything.

**Query rewriting, worked:** *"group all the employees by their role level"* → chart. Then *"do the same for upper management"* — without history the agent has no idea what "the same" means. The rewriter pulls the prior turn and rewrites the follow-up into something self-contained **before** intent detection ever sees it.

#### Chart generation — three approaches, one chosen

| Approach | How |
|---|---|
| **Code sandbox** | LLM generates plotting code, runs it sandboxed |
| **Text-to-chart libraries** | Library takes structured data, renders an image |
| **Templated generation** ← **chosen** | LLM decides only *type* and *what goes where*, as JSON; a fixed pre-written function draws it |

```python
# the LLM's entire contribution:
{"type": "bar", "x": "country", "y": "revenue", "title": "Revenue by Country"}
# handed to generator.py — one function per chart type (Matplotlib/Pandas)
# → PNG → base64 → into the JSON response → decoded at the Streamlit layer
```

> 🎯 **Why templated over code generation:** letting an LLM write and execute arbitrary plotting code is more flexible but riskier and slower (needs a sandbox, more to go wrong). Templated generation trades flexibility — you only get chart types you've written functions for — for **reliability**: the LLM only ever makes a small structured decision, never writes and runs free-form code.

#### Memory — built custom, deliberately not with LangGraph's checkpointer

Two stated reasons:
1. A checkpointer persists the **entire graph state**, far more data than a "who said what" log needs.
2. **Version fragility** — a library update once broke the built-in checkpointer's database connection, and diagnosing it took real effort. A small custom table has no framework dependency to break under you.

The custom approach is a plain table — `conversation_messages(id, session_id, role, content, created_at)`. Before every run, fetch the session's history and feed it to the query rewriter. After the answer, store the new Q&A pair — and specifically store the **rewritten** question, not the user's raw input, because the rewritten version is the self-contained one that's actually useful as future context.

> This is a legitimately debatable call, and worth being able to argue both sides of. The checkpointer gives you time-travel debugging, HITL, and crash recovery for free; a custom table gives you a small stable surface and full control over what's stored. The session chose the latter *for conversation memory specifically* — not as a blanket rejection of checkpointers.

#### Other notes from the live Q&A

- **Data outside the database (Excel/CSV):** needs a **separate workflow**, not a bolt-on — a router that first decides whether the data lives in the DB or in a file, shaped like a RAG pipeline for unstructured sources. One concrete option: a node that reads the CSV and joins it onto the SQL result on a shared key after the database query has run.
- **Single-agent or multi-agent?** As built, **single agent, one database**. To span independent sources (BigQuery *and* Postgres with no relationship): one LLM step deciding how much of the request maps to each, two independent agents each running this same node flow, and an aggregator (LLM or algorithmic) merging before final rendering.
- **Does every node need validation logic?** Depends on the use case. For `list_tables`, a lightweight sanity check is enough; rigorous per-node validation is a production-maturity concern, not a day-one requirement.
- **Node names:** entirely hand-designed. The core nodes (list tables, get schema, generate/check/run query) are a well-known SQL-agent pattern you'll find written up in plenty of places; the query rewriter, intent detector, and chart generator were added for *this* use case.

---

### 9.3 Multi-Agent Document Drafter

**What it does:** point it at a codebase and it drafts an HLD, LLD, software documentation, API documentation, or a README — as a downloadable `.docx`.

**The agents** (eight of them, each with one clear role):

| # | Agent | Role | Maps to |
|---|---|---|---|
| 1 | **Input validator** | Are all required inputs present? | — |
| 2 | **Requirement analyst** | Understand the request; flag missing/ambiguous info; can trigger human clarification | Observe |
| 3 | **Context planner** | Decide which code files to read; acts as retriever | Retrieve |
| 4 | **Repository analyst** | Summarise the overall codebase | Reason |
| 5 | **Document planner** | Build the document outline — which section holds what | Reason |
| 6 | **Section writer** | Generate the full content for each planned section | Act |
| 7 | **Technical + quality reviewer** | Check against the request; readability; can trigger human review | Evaluate |
| 8 | **Document exporter** | Assemble everything into the final `.docx` | Act |

**The graph, with all three human gates:**

```
validate_input
      ▼
analyze_requirements ──missing info?──► HUMAN INTERRUPT ──┐
      ▼ (complete)                                        │
context_planning ◄───────────────────────────────────────┘
      ▼
code_and_context_retrieval
      ▼
repository_understanding
      ▼
document_planning
      ▼
  ◄── HUMAN: approve the outline? ───────────────────┐
      │  more context → back to context_planning     │
      │  reject       → back to analyze_requirements │
      ▼ approve                                      │
section_drafting ◄──────── need more sections ───────┤
      ▼                                              │
technical_review ──fail──► context_planning          │
      ▼ pass                                         │
documentation_quality ──need more sections?──────────┘
      ▼ pass
document_assembly
      ▼
consistency_review
      ▼
  ◄── HUMAN: final approval?
      ▼
export .docx
```

**Why the human gates are where they are:** the requirement analyst flags *"you asked for API documentation but this codebase has no API"* **before** any drafting burns tokens. The outline gate catches a wrong plan before section writing. The final gate is the last stop before an artefact leaves the system. That's three checkpoints at the three moments where being wrong is most expensive.

#### The production code layout

This is arguably the most transferable thing in the whole project — the answer to *"my notebook works, now what?"*

```
app/
  main.py                  # FastAPI app: endpoints, lifespan
  services/
    workflow_service.py    # thread ID, collect inputs, submit(), run() → graph.invoke()
  graph/
    state.py               # the TypedDict: what flows between agents, with types
    nodes.py               # every node function
    prompts.py             # every prompt, one per node
    builder.py             # add_node / add_edge / add_conditional_edges → compile()
  tools/
    repository.py          # list_repository_files, read_repository_file,
                           # find_python_symbols, find_fastapi_routes, mask_secrets
  context/
    local_provider.py      # reading files, searching repo text
                           # ← a RAG pipeline or DB query tool would live here too
  memory/
    mongo.py               # document versions, events, human decisions
  mcp/
    server.py              # the same repository tools, exposed over MCP
  export/
    docx.py                # assemble sections into the final document
ui/
  streamlit_app.py
docker-compose.yml         # MongoDB
```

**Why split it up when the notebook was one cell?** Reuse. Multiple agents across multiple folders would otherwise each re-implement the same tool code. With `from app.tools.repository import read_repository_file`, any agent — or any *future* agent — imports it. The state definition living alone in `state.py` is the same idea: one authoritative declaration of what flows through the system.

> **Note `mcp/server.py` sitting next to `tools/`.** The *same* repository tools are exposed twice — as local Python imports for this agent, and over MCP for anything else. That's the §6.2 argument made concrete: a mobile app and a web app would otherwise each need their own integration; instead both point a client at one server.

**MongoDB's role here is auditability**, not agent memory: every human decision, every approval, every internal step logged for later inspection.

**Tooling notes:** the project uses **`uv`** rather than `pip` — it's written in Rust and is roughly 3–5× faster, and it manages the virtualenv, dependency adds, and the run command (`uv run main.py`). `docker compose up --build` brings up MongoDB; **MongoDB Compass** connects to it for inspection.

---

### 9.4 Build and Deploy Your First MCP Server

Covered in full in [§6.9](#69-building-one-with-fastmcp). The project ships three demos, and the progression is the point:

1. **Consume someone else's server** — copy a published MySQL MCP server's config block into `claude_desktop_config.json`, change the credentials, restart Claude Desktop. You now have an LLM that writes and runs SQL against your local database, with no code written at all.
2. **Build your own and run it locally** — FastMCP + `@mcp.tool` decorators, test in the Inspector, register with `fastmcp install claude-desktop`.
3. **Deploy it and connect from a framework** — Dockerfile → Hugging Face Space → public HTTPS URL → point a Google ADK agent's `MCPToolset` at it.

---

## 10. The Eight Notebooks

| Notebook | Teaches | Key API |
|---|---|---|
| `LangGraph Agents.ipynb` | The foundations: single-node graph → tools → memory → multi-agent routing | `StateGraph`, `add_messages`, `ToolNode`, `tools_condition`, `MemorySaver` |
| `LangChain Agents.ipynb` | A ReAct agent with tools and memory, the modern way | **`create_agent`**, `@tool`, `InMemorySaver` |
| `Corrective RAG (CRAG).ipynb` | Grade retrieved docs; fall back to web search when they're poor | `GradeDocuments` (structured output), `add_conditional_edges`, `TavilySearchResults` |
| `Router in Agentic RAG.ipynb` | Route a query to the right retriever via structured output | `RouteDecision` + `Literal`, `set_entry_point`, `add_conditional_edges` |
| `Human-in-Loop workflows for Agents.ipynb` | Pause for a human mid-graph and resume | `interrupt`, `Command`, `MemorySaver`, a `human_assistance` tool |
| `Agentic RAG with Phidata.ipynb` | Knowledge base + web search, agent picks the source | `phi.agent.Agent`, `LanceDb`, `PDFKnowledgeBase`, `DuckDuckGo` — **now Agno**, see §12.5 |
| `Email Generating Agent with CrewAI.ipynb` | The smallest useful Crew; the one later served via FastAPI | `Agent`, `Task`, `Crew` in a single `EmailDrafter` class |
| `Multi AI Agent Blog Generator using CrewAI.ipynb` | A five-agent sequential Crew | `Agent` × 5, `Process`, `WebsiteSearchTool` |

### 10.1 LangGraph Agents — the progression

Four builds, each adding one thing:

1. **Single LLM node** — `START → chatbot → END`. Establishes the pattern: a node receives state and returns a dict with an updated `messages` list; `add_messages` appends rather than overwriting.
2. **Add tools** — a `ToolNode` plus `tools_condition` as the conditional edge, and crucially `add_edge("tools", "chatbot")` — the tool result routes **back** to the model. That back-edge is the cycle that makes it an agent.
3. **Add memory** — `compile(checkpointer=MemorySaver())` and a `thread_id` in the config. Change the thread ID and the memory is gone, which the notebook demonstrates explicitly. It also flags the production note directly: **`MemorySaver` is for experimentation; use `SqliteSaver` or `PostgresSaver` and your own database in production.**
4. **Multi-LLM flow** — classify feedback as positive or negative, route to a dedicated handler node for each. The minimal router.

```python
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")     # ← the cycle
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=MemorySaver())
```

### 10.2 Corrective RAG (CRAG) — the canonical self-correcting retrieval graph

This is the notebook that makes §1.4 concrete: a RAG pipeline that *becomes* agentic by adding one conditional edge.

```
      START
        ▼
    retrieve
        ▼
  grade_documents          ← an LLM scores each doc relevant / not
        │
   ┌────┴────┐
   │         │
docs good   docs poor
   │         ▼
   │   transform_query     ← rewrite the question for better search
   │         ▼
   │   web_search_node     ← Tavily, to bring in outside knowledge
   │         │
   ▼◄────────┘
 generate
    ▼
   END
```

```python
class GradeDocuments(BaseModel):
    binary_score: str = Field(description="Documents are relevant: 'yes' or 'no'")

def decide_to_generate(state):
    return "transform_query" if state["web_search"] == "Yes" else "generate"

workflow.add_conditional_edges("grade_documents", decide_to_generate,
                               {"transform_query": "transform_query", "generate": "generate"})
```

**What makes it "corrective":** plain RAG retrieves once and generates from whatever came back, good or bad. CRAG **grades** what came back and, when it's poor, goes and gets better material instead of answering badly. The grading step is an LLM call, so the routing here is genuinely **agentic** by the §4.4 test.

> The notebook's own closing note: *"Making the grading strategy and when to do web search can make this more effective as per your use case."* The binary yes/no grade is the simplest possible version — a graded score with a threshold, or per-document filtering rather than an all-or-nothing switch, are both reasonable upgrades.

### 10.3 Router in Agentic RAG

Two knowledge sources (SQL docs and statistics docs), each with its own FAISS index. One LLM call picks which retriever to use:

```python
class RouteDecision(BaseModel):
    tool: Literal["sql", "stats"] = Field(description="Which knowledge source to use")
```

> `RouteDecision` + a structured-output LLM call is the LangGraph equivalent of LlamaIndex's `LLMSingleSelector`: the LLM picks exactly one choice from a list, except it returns a **Pydantic-validated label** rather than an index.

**To route to multiple sources at once:** change `tool` to `List[Literal["sql","stats"]]`, fan out to both retrieval nodes with **`Send`** (from `langgraph.constants`) instead of a single conditional edge, and concatenate the retrieved context from both branches before `generate`.

### 10.4 Human-in-Loop workflows

The build from §4.5, with one detail worth highlighting: the human is exposed to the model **as a tool**.

```python
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]
```

The model *chooses* whether to ask a human, the same way it chooses whether to search. The notebook demonstrates both outcomes: for one question the model went straight to web search without consulting anyone; for another, being told explicitly which tool to use, it invoked `human_assistance`. **Which is the honest limitation:** whether the agent asks for help is a prompting problem, not a structural guarantee. If a human *must* be consulted, put the interrupt on an edge, not inside an optional tool.

### 10.5 Agentic RAG with Agno (Phidata)

The most compact agent in the set — a knowledge base and a web search tool, and the agent decides which to use:

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=PDFKnowledgeBase(vector_db=LanceDb(search_type=SearchType.hybrid), reader=PDFReader()),
    tools=[DuckDuckGo()],
    storage=SqlAgentStorage(...),
    show_tool_calls=True,
)
```

The notebook's own point: with `show_tool_calls=True` you can see, per question, **which source was used** — one question answered from the vector DB, the next from the web. That's the routing decision made visible, with no graph written at all. It's the clearest illustration in Week 4 of what a high-abstraction framework buys you, and of what it hides.

### 10.6 The two CrewAI notebooks

**Email drafter** — the minimal Crew: one `Agent`, one `Task`, one `Crew`, wrapped in an `EmailDrafter` class with a `.run()` method. That class is exactly what §8.3's FastAPI endpoint calls, which is why this notebook is the one the serving session reuses.

**Blog generator** — five agents in sequence:

```python
crew = Crew(
    agents=[researcher, generator, technical_reviewer, copy_editor, markdown_formatter],
    tasks=[...],
    process=Process.sequential,
)
```

A clean instance of the hierarchical/assembly-line shape from §1.6 type 6: research → draft → technical review → copy edit → format. Each agent has one job and passes forward.

> The notebook's own footnote: all the coloured terminal output during generation is the framework's internal logging. `verbose=False` turns it off. Keep it **on** while developing — seeing each agent's actual input is how you discover that your task descriptions are ambiguous.

---

## 11. What Every Course Build Deliberately Leaves Out

Stated explicitly in the Market Research session, and true of every project in the week. These are not oversights — they're the next layer, and knowing them is what separates "I built an agent" from "I've run one."

| Gap | Why it bites | What to add |
|---|---|---|
| **Retry logic** | Structured output fails to parse and the run dies silently | Retry with the parse error fed back into the prompt; cap the retries |
| **Caching / memory layer** | Identical research re-runs from scratch every time | Cache by request hash; check before dispatching tools |
| **Cost governance** | Unbounded web research across many sources burns tokens fast | A token/cost budget per request, enforced by the controller |
| **Parallelisation** | Independent tool calls run one after another | Fan out independent nodes; aggregate |
| **Iteration caps** | An agent re-invokes a tool hoping for a better answer, forever | A hard max-iteration count on every loop (§4.7) |
| **Per-node validation** | A bad intermediate result propagates silently to the end | Validate where being wrong is expensive; skip where it isn't |
| **Dependency health checks** | Deployed credentials can't reach the DB; local testing never showed it | Expose dependencies as plain endpoints (§8.7) |

> **The framing worth keeping:** *architectural maturity is incremental.* You can't design all of this up front. Build the simplest working version, observe how the model behaves with real tools and real data, and add fallbacks, caching, and cost controls where the system actually needs them.

---

## 12. Important Updates Since the Course Notes

### 12.1 MCP went stateless — the biggest change in this whole document

**The 2026-07-28 MCP specification is the largest revision since the protocol launched, and it inverts one of the properties the course session presents as MCP's headline advantage over classic tool calling.** ([Spec announcement](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [Specification](https://modelcontextprotocol.io/specification/2026-07-28))

| The session says | The 2026-07-28 spec says |
|---|---|
| MCP servers maintain a **stateful context** — session IDs, incremental updates, server-remembered history — and that's a key advantage over stateless REST | **MCP is now stateless at the protocol layer.** The `initialize`/`initialized` handshake and the `Mcp-Session-Id` header are gone. Each request is self-contained, carrying protocol version, client identity, and capabilities in metadata. The same request can be answered by *any* server instance behind ordinary HTTP infrastructure. |
| **Sampling** is a core primitive and the reason MCP needs bidirectional JSON-RPC | **Sampling, roots, and logging are deprecated** (12-month minimum support window). Server-initiated requests are replaced by **Multi Round-Trip Requests (MRTR)**: the server returns `resultType: "input_required"` with the requests it needs answered, and the client retries the original call with the answers in `inputResponses`. Nothing has to stay connected between turns. |
| **SSE** is a transport option (already noted as deprecated in the session) | **HTTP+SSE is now formally deprecated.** Streamable HTTP is the transport. |
| — | **New:** header-based routing (`Mcp-Method`, `Mcp-Name`) lets gateways route and authorise without parsing JSON bodies; **cacheable list results** (`ttlMs`, `cacheScope`); **RFC 9207 issuer validation**; Dynamic Client Registration deprecated in favour of **Client ID Metadata Documents (CIMD)**; a formal **extensions framework**, with Tasks moving out of experimental core into the `io.modelcontextprotocol/tasks` extension. |

**Why they did it:** statefulness was what made MCP hard to scale. A stateful session pins a client to one server instance, which breaks load balancers, autoscaling, and serverless deployment. Going stateless means MCP servers behave like ordinary HTTP services ([Google Developers Blog](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/)).

**What this means for you, practically:**

- **The N×M argument, the host/client/server model, tools/resources/prompts, dynamic discovery, and the "USB-C for AI" framing are all still exactly right.** That's the substance of the session and none of it changed.
- **Do not claim "MCP is stateful, unlike REST" in an interview** without immediately qualifying it. The defensible version is: *"MCP was session-stateful through the 2025 revisions; the 2026-07-28 spec deliberately removed protocol-level sessions so servers scale behind ordinary HTTP infrastructure. Where a tool genuinely needs state across calls, that's now the server's own concern, not the protocol's."*
- **Don't build new servers on sampling.** Use MRTR for anything that needs mid-call user input.
- Many deployed servers still speak older revisions. The spec has a formal deprecation policy now, so the transition is managed rather than abrupt — but check which revision your client and server negotiate.

### 12.2 FastMCP has moved twice since the session

The session says *"the current latest version is version 3."* Since then:

- **FastMCP 3.0** — released 19 January 2026, GA 18 February 2026. Added component versioning, granular authorization, OpenTelemetry instrumentation, and provider types (FileSystem, Skills, OpenAPI).
- **FastMCP 4** — shipped alongside the 2026-07-28 protocol revision, on the same day. Most FastMCP 3 applications upgrade without code changes ([FastMCP updates](https://gofastmcp.com/updates) · [releases](https://github.com/PrefectHQ/fastmcp/releases)).

The `@mcp.tool` decorator pattern taught in the session is unchanged and still correct. `fastmcp install claude-desktop` and the Inspector both still work.

### 12.3 MCP and A2A are now Linux Foundation projects

The **Agentic AI Foundation (AAIF)**, launched December 2025, is a neutral top-level Linux Foundation body hosting **both MCP and A2A**. A2A reached **v1.0.0 in January 2026** with signed Agent Cards, and passed 150 supporting organisations by April 2026. If you learned MCP as "Anthropic's protocol" and A2A as "Google's protocol," both descriptions are now historical. (§6.10)

### 12.4 LangChain agents: `create_agent` is the only answer now

`initialize_agent`, `AgentExecutor`, and `langgraph.prebuilt.create_react_agent` have all collapsed into a single **`create_agent`**. The old constructors live in `langchain-classic`, with end-of-life messaging pointing at **December 2026**.

**The Week 4 `LangChain Agents.ipynb` already uses `create_agent`** — it's current. Anything you read elsewhere that opens with `from langchain.agents import AgentExecutor` is teaching a deprecated path.

### 12.5 Phidata is now Agno

The `Agentic RAG with Phidata.ipynb` notebook imports from `phi`. **Phidata was renamed Agno in January 2025**; the GitHub org moved to `agno-agi` and the package is `agno`. Beyond the rename, Agno has grown into a different proposition: **Agents / Teams / Workflows** as SDK abstractions plus **AgentOS**, a FastAPI-based runtime that owns durable state, sessions, traces, and monitoring in your own database — positioned as the missing piece between a prototype and a deployed product. Recent releases added **ReliabilityEval** for agent evaluation.

The concepts the notebook teaches (knowledge base + tools, agent picks the source) transfer directly; the imports don't.

### 12.6 CrewAI: Flows, and AMP

Two things the Crews-only framing in the course material misses:

- **Flows** close the branching/HITL/persistence gap, as covered in §5.4. The honest comparison is **Crews vs Flows vs LangGraph**, not CrewAI vs LangGraph.
- **CrewAI AMP** (Agent Management Platform) launched January 2026 — managed deployment, observability, governance, security, and enterprise support, with tracing for LLM calls, tool calls, memory activity, token usage, and deployment history ([CrewAI blog](https://blog.crewai.com/crewai-amp-the-agent-management-platform/)). It's the same category of thing as Agno's AgentOS and LangGraph Platform: the runtime layer, sold separately from the framework.

### 12.7 LangGraph 1.x

v1.0 on 22 October 2025, v1.2 on 11 May 2026. Everything the session teaches still applies. The additions worth knowing: **durable execution as a first-class concern** (the pluggable checkpointer interface — `put` / `get_tuple` / `list` — is the supported way to survive a restart), and **middleware** for attaching cross-cutting behaviour around an agent without editing the call site. (§4.8)

### 12.8 Agent evaluation has grown agent-specific metrics

The session's frame — reference metrics → LLM-as-judge → agent-specific concerns — was directionally right and the tooling has caught up. DeepEval now ships **tool selection, tool calling, tool quality, plan adherence, plan quality, logical consistency, and execution efficiency** as named metrics; TruLens ships purpose-built agentic evaluators. And the whole ecosystem has converged on **OpenTelemetry GenAI semantic conventions**, so traces are portable across backends rather than locked to one vendor's UI. The 2026 practitioner split is roughly: **RAGAS** for fast experiments, **DeepEval** for CI gates, **TruLens** for production tracing. (§7.5, §7.8)

**Sources for this section:**
- [The 2026-07-28 Specification — MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [Scaling AI Agent Infrastructure with the MCP Stateless Updates — Google Developers Blog](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/)
- [FastMCP Updates](https://gofastmcp.com/updates) · [FastMCP releases](https://github.com/PrefectHQ/fastmcp/releases)
- [Linux Foundation launches the Agent2Agent Protocol Project](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)
- [A year of open collaboration: A2A anniversary — Google Open Source Blog](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html)
- [LangChain and LangGraph reach v1.0 — LangChain Blog](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [LangChain changelog](https://docs.langchain.com/oss/python/releases/changelog)
- [CrewAI AMP — The Agent Management Platform](https://blog.crewai.com/crewai-amp-the-agent-management-platform/)
- [Top 5 LLM Evaluation Frameworks in 2026 — DeepEval](https://deepeval.com/blog/top-5-llm-evaluation-frameworks)
- [TruLens: Evals and Tracing for AI Agents](https://www.trulens.org/)
- [Inside the LLM Call: GenAI Observability with OpenTelemetry](https://opentelemetry.io/blog/2026/genai-observability/)

---
## 13. Interview Prep

*Two answer layers per question: a plain-language version with an example, then a crisp, technically precise one. Try answering out loud before reading.*

---

**🎙️ Q1: "What's the actual difference between an AI agent and a RAG system — aren't they both just 'LLM plus extra stuff'?"**

**✅ Strong answer:** "They both extend a plain LLM, but in different directions. RAG extends what the model *knows* — it retrieves relevant documents and feeds them in so the answer is grounded. An agent extends what the model can *do* — it reasons about a task, picks an action, and performs it through a tool, possibly over several steps. The structural difference is who decides the order of steps: in RAG, you did, at design time — every query takes the same path. In an agent, the LLM decides at runtime, so different questions take different numbers of steps. That's also why an agent needs an explicit stopping condition and a pipeline doesn't."

**🎯 Precise answer:** "RAG augments the *generation* step with retrieved context from a static knowledge base — information augmentation, static control flow, a DAG. Agentic systems augment the *decision* step — the LLM plans and iteratively invokes tools, giving dynamic control flow with cycles and conditional branching, which mandates explicit termination. They're complementary rather than competing: production agents routinely use RAG as one tool, and in a multi-agent system an entire RAG pipeline can be wrapped as a single node."

---

**🎙️ Q2: "Walk me through the components of a single agent."**

**✅ Strong answer:** "I think of it as a tiny operating system. The interface is the keyboard and screen — it takes the request in and hands the answer back. The controller is the kernel — it runs the loop and decides when to stop. The reasoner is the CPU — one LLM call that picks the next action, and it should return structured JSON like `{tool, stop, rationale}` rather than prose, so the system can dispatch on it and audit it. Tools are the installed programs. Memory is the filesystem — short-term for the session, long-term across sessions, semantic in a vector store, which is where RAG plugs in. Policy and safety are file permissions, and they run at three points, not one: before execution to check authorisation, during to enforce constraints, and after to scrub PII. Observability is Task Manager plus the system log."

**🎯 Precise answer:** "Seven subsystems: interface (request/response contract plus timeouts and iteration limits), controller (the orchestration loop — schema validation, policy gating, continue-or-stop), reasoner (the LLM call, emitting schema-constrained action selection), tools (typed, schema-described callables returning structured results with status and timing), memory (short-term, long-term, semantic), policy and safety (pre/during/post checkpoints), and observability (trace ID, per-step latency, token usage, cost, tool call log, success rate). The controller is the part people skip and the part that keeps the loop bounded."

---

**🎙️ Q3: "When would you reach for a multi-agent system instead of just making one agent's prompt better?"**

**✅ Strong answer:** "Two reasons, one textbook and one practical. The textbook one is that the task needs genuinely different *kinds* of competence — if one agent is retrieving, reasoning, generating, and compliance-checking, you're asking one model to be good at four jobs with nobody catching its mistakes. The practical one, which I think matters more, is context. A single agent pulling from a knowledge base, then an API, then a database accumulates all of that in one context window, and it runs out of room mid-task. Splitting means each sub-agent gets only the fields it needs. I wouldn't go multi-agent just because a task has multiple steps — a single agent with a planner loop handles that fine."

**🎯 Precise answer:** "Justified when a task requires functionally distinct competencies that benefit from independent specialisation and cross-verification, when parallel execution across tools or compute is needed for throughput, or when a single agent's accumulated context exceeds the window. Step count alone isn't the deciding factor. The counterweight is that each additional agent adds LLM calls, latency, and cost, so with long-context models the right number of agents is an empirical question, not an architectural one."

---

**🎙️ Q4: "What's the difference between planner-executor and supervisor-worker? They both sound like 'one agent tells others what to do.'"**

**✅ Strong answer:** "It's *what* gets delegated. In planner-executor, the planner produces the full sequence of steps up front and the executor works through them one after another — linear and mostly deterministic. In supervisor-worker, the supervisor hands whole *subtasks* to different specialists, who each may run several steps of their own, and the supervisor's real job is merging and verifying what comes back — which can happen in parallel. Planner-executor is 'here's your checklist, go.' Supervisor-worker is 'here's your piece, use your judgment, report back.'"

**🎯 Precise answer:** "Planner-executor decomposes into an explicit ordered sequence executed largely linearly — closer to a deterministic workflow, optimising for auditability and debuggability. Supervisor-worker decomposes into parallel subtasks routed to specialists with autonomy over internal execution, with the supervisor responsible for assignment, conflict resolution, and result aggregation. The former optimises for determinism; the latter for parallelism and specialisation."

---

**🎙️ Q5: "In a LangGraph RAG system, a conditional edge like 'if relevance score < 0.6, do a web search' — is that agentic?"**

**✅ Strong answer:** "No, that's still deterministic, and I think that's the distinction worth being precise about. It branches and it *looks* adaptive, but a human picked 0.6 and the same score always routes the same way. The cleanest way to see it is that both cases use the exact same mechanism — `add_conditional_edges` — and the only thing that differs is what's inside the routing function. Plain Python comparing a number is deterministic routing. An LLM call deciding which node comes next is agentic routing. Same graph, same edge, different decision-maker — which is why pipeline-versus-agent is a spectrum rather than a switch, and real systems mix both in one graph."

**🎯 Precise answer:** "Threshold-gated branching is deterministic control flow: the decision function is a pure predicate over state, so the routing is reproducible given the same state. Agentic routing places an LLM inference inside the same conditional-edge mechanism. Worth adding that even in the agentic case the LLM almost always selects from a predefined node set via structured output — a Pydantic-validated `Literal`, not open-ended generation — so 'the LLM decides' means it chooses among paths you already built."

---

**🎙️ Q6: "How does human-in-the-loop actually work in LangGraph? What has to be in place?"**

**✅ Strong answer:** "Two things, or it won't work at all. First a checkpointer, so the paused state is actually saved somewhere instead of lost. Second a thread config — basically a session ID — so the system knows *which* paused run to resume. When the graph hits `interrupt`, it pauses right there and checkpoints. Then, instead of calling `invoke` with new input, which would restart the graph from the top, you call it with `Command(resume=...)` carrying the human's decision and the same thread config, and it continues from exactly that node. And for anything that runs in production, use `SqliteSaver` or `PostgresSaver` — `MemorySaver` dies with the process, which defeats the point."

**🎯 Precise answer:** "`interrupt` requires a checkpointer to persist state at the pause point and a `configurable` thread ID scoping which execution is being resumed. Resumption goes through `Command(resume=<decision>)` against that thread, not a fresh `invoke`, which would re-enter at the entry point. In production the checkpointer must be durable — Sqlite or Postgres — because the entire value proposition is that the pause survives a restart."

---

**🎙️ Q7: "What problem does MCP actually solve, and when wouldn't you use it?"**

**✅ Strong answer:** "The N-times-M integration problem. Without it, three AI apps needing four tools means twelve custom integrations — and if you rewrite one app in a different framework, you rewrite its four tool integrations while still maintaining the others. With MCP, each app implements a client once and each tool sits behind a server once: three plus four, seven connections. The concrete win is that adding a fifth tool means updating the *server*; every connected client discovers it on the next `tools/list`, with no application code changing anywhere. When wouldn't I use it? A single app with its tools in the same codebase. MCP adds a protocol layer plus auth setup, and for a prototype that's overhead buying nothing — you can convert later if the tools need sharing."

**🎯 Precise answer:** "MCP standardises tool description, discovery, and invocation over JSON-RPC 2.0, collapsing N×M bespoke integrations to N+M. It decouples tool implementation from agent framework and from co-location — a tool can run in a different process, host, or cloud. The discriminating capability versus classic function calling is runtime discovery via `tools/list` rather than development-time hardcoding, plus cross-client reusability. It's not warranted for a single-consumer, co-located toolset where the protocol layer and authorization setup are pure overhead."

---

**🎙️ Q8: "Is MCP stateful?"** *(the question that catches people out)*

**✅ Strong answer:** "It was, and as of the July 2026 spec it deliberately isn't. Through the 2025 revisions MCP had protocol-level sessions — an initialize handshake and an `Mcp-Session-Id` header — and that statefulness was genuinely one of the things people cited as an advantage over stateless REST. But it's also what made MCP hard to scale, because a session pins a client to one server instance, which breaks load balancers and serverless deployment. The 2026-07-28 revision removed protocol-level sessions entirely: every request is self-contained, so any server instance behind ordinary HTTP infrastructure can answer it. Server-initiated things like sampling were replaced by Multi Round-Trip Requests, where the server returns 'input required' and the client retries with the answers attached, so nothing has to stay connected between turns. If a tool genuinely needs state across calls, that's now the server's own concern, not the protocol's."

**🎯 Precise answer:** "Not as of the 2026-07-28 revision. That spec removed the `initialize`/`initialized` handshake and the `Mcp-Session-Id` header, making each request self-contained with protocol version, client identity, and capabilities carried in metadata — enabling horizontal scaling behind standard HTTP infrastructure. Server-initiated requests — sampling, elicitation, roots — are superseded by Multi Round-Trip Requests, where the server returns `resultType: "input_required"` with an opaque `requestState` and the client re-issues with `inputResponses`. Sampling, roots, and logging are deprecated with a twelve-month support window, and HTTP+SSE is formally deprecated in favour of streamable HTTP."

---

**🎙️ Q9: "Why is evaluating an agent harder than evaluating an LLM, and what would you actually measure?"**

**✅ Strong answer:** "Because with a plain LLM you're grading one output, and with an agent you're grading the whole working. A wrong final answer could come from a bad plan at the start, the wrong tool, the right tool with wrong arguments, or faulty reasoning three steps in — and you can't fix what you can't locate. There's also a failure mode that final-answer scoring completely misses: correct but incomplete. A SQL agent that queries the right data and then silently drops a column when summarising it produces an answer that looks right and *is* sourced from real data, and it's still wrong. So beyond the usual faithfulness and answer relevancy, I'd measure tool-selection correctness, argument validity, plan adherence, and step count — all of which need per-step traces, which is why observability isn't a separate concern from evaluation, it's the prerequisite."

**🎯 Precise answer:** "Agent evaluation must cover execution quality alongside outcome quality, because failure modes distribute across planning, tool selection, argument construction, intermediate reasoning, and synthesis. Reference-based metrics degrade further than for plain generation: gold references often don't exist, multiple valid solutions exist, and the path matters independently of the endpoint. Current tooling exposes this directly — DeepEval ships tool selection, tool calling, tool quality, plan adherence, plan quality, logical consistency, and execution efficiency as named metrics. All of them depend on per-step traces, so instrumentation is a precondition rather than a parallel workstream."

---

**🎙️ Q10: "Your Reflect/Critic loop uses an LLM to evaluate an LLM. What's wrong with that, and how do you fix it?"**

**✅ Strong answer:** "They share blind spots. The evaluator isn't comparing against ground truth — it's assessing whether the answer *looks* reasonable, which is exactly the judgment the generator already made when it produced the wrong answer. So an LLM that gets a fact wrong will often happily approve its own wrong answer. The fix is giving the evaluator a signal the generator doesn't have: rule-based checks for a domain you actually understand, semantic similarity against a known-good reference, or real precision/recall/factual-correctness scoring where you have ground truth. The evaluator needs an independent source of truth, not a second opinion from the same kind of model."

**🎯 Precise answer:** "LLM-as-evaluator exhibits correlated failure modes with LLM-as-generator — both assess plausibility rather than verifiable correctness, so errors within the shared distribution pass undetected. Mitigations are anything that introduces an independent signal: deterministic domain validation, embedding-similarity against reference answers, retrieval-grounded verification, or IR metrics against ground truth. A different model family as judge reduces but does not eliminate the correlation."

---

**🎙️ Q11: "Walk me through taking an agent from a notebook to something a mobile app can call."**

**✅ Strong answer:** "The key thing is that the agent doesn't change. FastAPI doesn't *integrate* with CrewAI or LangGraph — the notebook code just goes inside a route function, and when a request hits that route, that code runs. So: define a Pydantic request model so bad input is rejected before your code ever runs, build the agent once at startup in a lifespan handler rather than per request, put the invoke inside a POST route, return real status codes so a client program can tell success from failure, and containerise it. Two things bite everyone: inside Docker, `localhost` doesn't mean the host machine — you need `host.docker.internal` — and use Gunicorn rather than bare uvicorn for real concurrency. One thing I'd add from experience: expose whatever the agent depends on as its own plain endpoint. A `GET /tables` that just lists your database tables tells you instantly whether a failure is the agent or the credentials."

**🎯 Precise answer:** "Wrap, don't integrate: the agent invocation sits inside a route handler. Pydantic models give request/response validation and OpenAPI generation for free. Expensive initialisation — graph compilation, connection pools, tracing setup — belongs in a `lifespan` handler at startup, not per request. Return semantically correct status codes so clients can branch programmatically. Containerise with a non-root user and a health check, serve via Gunicorn with uvicorn workers, and remember that container-internal `localhost` requires `host.docker.internal` for host services. Add independent liveness endpoints for the agent's own dependencies so a failure is attributable without reading traces."

---

**🎙️ Q12: "How do you choose between LangChain, CrewAI, and LangGraph?"**

**✅ Strong answer:** "I think of it as four rungs, not three options. An LCEL chain when the flow is straight and every step is one fixed call — summarise this document. A single agent via `create_agent` when one worker needs to pick tools and loop. CrewAI when you've got several *specialists* handing off in order and each one needs to be autonomous internally — research, then analyse, then write. And LangGraph when the handoffs themselves need to loop back, branch on a condition, or pause for a human. One correction I'd make to a common framing: it's wrong to say LangChain has no agents. It does — that's what `create_agent` is. The valid contrast is LCEL chain versus CrewAI agent. And what CrewAI actually adds over a LangChain agent isn't reasoning capability, it's the team abstraction — roles, goals, and handoff plumbing. You could wire three `create_agent` calls together and get the same result with more boilerplate. That's ergonomics, not capability."

**🎯 Precise answer:** "The axis is where non-determinism lives. LCEL: deterministic within and between steps. `create_agent`: non-deterministic within a single agent loop, no inter-agent structure. CrewAI Crews: non-deterministic within each agent, deterministic acyclic handoff between them. LangGraph and CrewAI Flows: non-determinism in the inter-agent control flow itself — cycles, conditional routing, durable interrupts. Since Flows landed, the branching/persistence capability gap between CrewAI and LangGraph has largely closed, so the remaining difference is how much explicit control you want over the graph rather than what's achievable."

---

## 14. Glossary

| Term | Meaning |
|---|---|
| **A2A (Agent2Agent)** | Open protocol for agent↔agent communication. Linux Foundation project; v1.0.0 January 2026 |
| **AAIF** | Agentic AI Foundation — neutral Linux Foundation body hosting MCP and A2A (Dec 2025) |
| **Agentic routing** | A conditional edge whose decision function contains an LLM call (vs a coded rule) |
| **Agno** | Agent framework, formerly Phidata; SDK (Agents/Teams/Workflows) plus the AgentOS runtime |
| **AMP** | CrewAI's Agent Management Platform — managed deployment, observability, governance |
| **BERTScore** | Similarity metric using contextual embeddings; captures meaning, not word overlap |
| **Checkpointer** | LangGraph component persisting state after every superstep, keyed by thread ID |
| **CIMD** | Client ID Metadata Documents — replaces Dynamic Client Registration in MCP auth |
| **Conditional edge** | A LangGraph edge whose destination is chosen by a routing function returning one node name or `END` |
| **Controller** | The agent subsystem running the loop: validate, gate, execute, decide continue-or-stop |
| **CRAG** | Corrective RAG — grade retrieved documents; fall back to web search when they're poor |
| **Crew** | CrewAI's role/task/team abstraction; acyclic, forward-only |
| **DAG** | Directed acyclic graph — forward only, no cycles. The shape of a RAG pipeline |
| **DeepEval** | Evaluation library; built-in RAG and agent metrics plus G-Eval custom rubrics |
| **Durable execution** | An agent run that survives a process restart, via a persistent checkpointer |
| **`END`** | LangGraph's reserved sentinel meaning "this path terminates here" |
| **Flow** | CrewAI's event-driven alternative to Crews: `@start`, `@listen`, `@router`, `@persist` |
| **FastMCP** | Python library abstracting the MCP SDK; `@mcp.tool` registers a tool. Now at v4 |
| **G-Eval** | DeepEval's framework for custom LLM-as-judge criteria with generated reasoning steps |
| **Host** | In MCP: the application owning clients, permissions, and security policy |
| **`interrupt`** | LangGraph call that pauses a graph mid-execution pending human input |
| **JSON-RPC 2.0** | The RPC protocol MCP is built on; supports bidirectional calls |
| **LCEL** | LangChain Expression Language — composes deterministic chains |
| **LLM-as-judge** | Using a second LLM to score an answer against explicit criteria |
| **MCP** | Model Context Protocol — standardises agent↔tool connection. "USB-C for AI" |
| **MRTR** | Multi Round-Trip Requests — the 2026-07-28 replacement for server-initiated MCP requests |
| **MemorySaver** | LangGraph's in-process checkpointer. Experimentation only |
| **N×M problem** | Every app needing a custom integration for every tool; MCP reduces it to N+M |
| **OTEL GenAI conventions** | OpenTelemetry semantic conventions for LLM/agent traces; the emerging portable trace format |
| **Planner-executor** | A role split: one agent produces an ordered plan, another executes it |
| **`Process.hierarchical`** | CrewAI mode where a manager LLM delegates and validates; needs `manager_llm` |
| **ReAct** | Reason + Act: thought → action → observation, looped |
| **Reducer** | A function controlling how a node's return value merges into a state field (`add_messages`) |
| **Resources** | MCP primitive: read-only data the host surfaces, addressed by URI |
| **Sampling** | MCP primitive where the server asks the client's LLM to do work. **Deprecated 2026-07-28** |
| **`Send`** | LangGraph constant for fanning out to multiple nodes from one decision |
| **State** | The shared typed object every LangGraph node reads and writes |
| **stdio / streamable HTTP / SSE** | MCP transports: local pipe / current remote standard / deprecated legacy |
| **Structured output** | Constraining an LLM's response to a validated schema (Pydantic) rather than free text |
| **Supervisor–worker** | A central agent delegating subtasks to specialists, then merging and verifying |
| **Thread ID** | The key scoping a checkpointed conversation; required to resume the right paused run |
| **Tool** | A schema-described callable the LLM can invoke |
| **Trace ID** | The per-request identifier tying every log line and span together |
| **TruLens** | Evaluation/tracing library; ground-truth-agreement scoring, OTEL-native |
| **`uv`** | Rust-based Python package manager; 3–5× faster than pip |

---

## 15. Key Takeaways

1. **An agent acts; a chatbot answers; a script follows rules.** The dividing line is whether the number of steps is decided by you at design time or by the LLM at runtime — which is also why an agent must have an explicit stopping condition and a pipeline needn't.

2. **Reach for an agent only after a fixed pipeline has failed you.** Agents are strictly more expensive, slower, and harder to debug. "It has multiple steps" is not sufficient justification.

3. **A single agent is seven subsystems arranged like a tiny operating system.** The one people skip is the controller — the loop with the iteration cap and the policy gate — and it's the one that keeps the agent from running forever or refunding $4,999.

4. **Go multi-agent for context isolation as much as for specialisation.** One agent that pulls from a knowledge base, an API, and a database fills its context window mid-task. Pass each sub-agent the minimum state that produces the maximum output.

5. **In LangGraph, "deterministic vs agentic" is decided by what's inside the routing function, not by the graph shape.** A coded threshold and an LLM call sit in the same `add_conditional_edges` call. Real systems mix both.

6. **Human-in-the-loop needs a checkpointer and a thread ID, or it silently doesn't work** — and in production it needs a *durable* checkpointer, because the whole point is surviving a restart.

7. **The framework ladder has four rungs, not two:** LCEL chain → single agent → CrewAI Crew → LangGraph or CrewAI Flow. And LangChain absolutely does have agents; the valid contrast is LCEL chain vs CrewAI agent.

8. **MCP collapses N×M integrations to N+M, and its real superpower is runtime discovery** — add a tool to the server and every connected client finds it without a single application code change. **But it went stateless in July 2026**, so don't quote its old "stateful, unlike REST" pitch without qualifying it.

9. **Agent evaluation grades the working, not just the answer** — because a wrong output could come from planning, tool selection, arguments, or reasoning, and you can't fix what you can't locate. "Correct but incomplete" is the failure mode final-answer scoring never catches.

10. **Observability is the prerequisite for evaluation, not a parallel concern.** Framework components auto-instrument; anything you wrote by hand needs explicit spans, or it's invisible.

11. **FastAPI wraps your agent; it doesn't integrate with it.** The notebook code goes inside a route function, unchanged. Build the agent once in a lifespan handler, not once per request.

12. **Production readiness is incremental and deliberately deferred in every course build:** retry logic, caching, cost governance, parallelisation, iteration caps. Build the simplest working version, watch where it actually breaks, and add controls where the evidence says you need them.

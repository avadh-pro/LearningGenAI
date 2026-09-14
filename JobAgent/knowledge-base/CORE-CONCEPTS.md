# LangChain + LangGraph — Core Concepts (synthesised)

> Source of truth: the 104 markdown pages in `langchain/` and `langgraph/`, crawled from
> `https://docs.langchain.com/oss/python/` on **2026-09-14**.
> This file is a navigational summary. **When precision matters, open the cited page.**

---

## 0. The mental model in one paragraph

**Agent = Model + Harness.** The *harness* is everything wrapped around the model loop: the
system prompt, the tools, and the middleware that shapes behaviour. **LangChain** gives you
`create_agent`, a minimal, highly configurable harness. **LangGraph** is the low-level
orchestration runtime underneath it — durable execution, persistence, streaming,
human-in-the-loop. **Deep Agents** is a batteries-included harness on top of LangChain
(planning, virtual filesystem, subagents). You pick the altitude:

| Need | Use | Page |
| --- | --- | --- |
| Batteries-included autonomous agent | Deep Agents | `langchain/philosophy.md` |
| Customisable tool-calling agent | LangChain `create_agent` | `langchain/agents.md` |
| Deterministic + agentic steps mixed, custom topology | LangGraph `StateGraph` | `langgraph/graph-api.md` |
| Trace / evaluate / debug any of the above | LangSmith | `langchain/observability.md` |

> **Critical version note.** LangChain **1.0** (2025-10-20) deleted the old chains/agents.
> There is now **exactly one** high-level abstraction: `create_agent`. Legacy code lives in
> the separate `langchain-classic` package. Anything you remember about `LLMChain`,
> `initialize_agent`, `AgentExecutor`, or `RetrievalQA` is **obsolete** — do not write it.
> See `langchain/philosophy.md` (History section).

---

## 1. LangChain

### 1.1 Creating an agent — the canonical shape

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
print(result["messages"][-1].content_blocks)
```

`create_agent` returns a **compiled LangGraph graph**. That is why it inherits persistence,
streaming, interrupts, and time-travel for free — and why you can drop the whole agent into a
larger `StateGraph` as a single node. (`langchain/middleware__overview.md`)

### 1.2 Model identifiers

Models are addressed as `"provider:model"` strings, or built with `init_chat_model()` when you
need extra kwargs. Verified examples from `langchain/overview.md` / `models.md`:

| Provider | String |
| --- | --- |
| Anthropic | `"claude-sonnet-4-6"` |
| OpenAI | `"openai:gpt-5.5"` |
| Google | `"google_genai:gemini-2.5-flash-lite"` |
| AWS Bedrock | `"bedrock_converse:us.anthropic.claude-sonnet-4-6"` |
| Azure OpenAI | `init_chat_model("azure_openai:gpt-5.5", azure_deployment=...)` |
| Ollama (local) | `"ollama:devstral-2"` |
| OpenRouter | `"openrouter:anthropic/claude-sonnet-4-6"` |
| HuggingFace | `"huggingface:microsoft/Phi-3-mini-4k-instruct"` |

```python
from langchain.chat_models import init_chat_model
model = init_chat_model("openai:gpt-5.5", temperature=0)
```

Full matrix + per-provider install extras: **`langchain/models.md`** (46k, the definitive page).

### 1.3 Import map (LangChain 1.x)

```python
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware, SummarizationMiddleware, ModelRequest, ToolCallRequest,
)
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain.chat_models import init_chat_model
```

Note `langchain.messages` — **not** `langchain_core.messages`. Provider packages stay separate:
`langchain_anthropic.ChatAnthropic`, `langchain_openai.ChatOpenAI`, `langchain_aws.ChatBedrock`,
`langchain_google_genai.ChatGoogleGenerativeAI`. Full list: `API-REFERENCE.md`.

### 1.4 Tools

```python
from langchain.tools import tool, ToolRuntime

@tool
def search_jobs(query: str, location: str) -> str:
    """Search job boards. The docstring becomes the tool description the model sees."""
    ...
```

The tool's **name defaults to the function name** — this matters because HITL policies key off
`.name`. A tool can reach runtime context via `ToolRuntime` (state, store, stream writer,
execution info). Tools can also come from **MCP servers** — see §3.
Definitive page: **`langchain/tools.md`** (54k) — covers schemas, reserved arg names, error
handling, state injection, dynamic tool selection, headless tools, prebuilt tools.

### 1.5 Structured output

Set `response_format` and read `structured_response` off the final state.

```python
from pydantic import BaseModel, Field

class JobScore(BaseModel):
    score: int = Field(ge=0, le=100)
    reasoning: str

agent = create_agent(model="claude-sonnet-4-6", tools=[...], response_format=JobScore)
result = agent.invoke({"messages": [...]})
result["structured_response"]   # -> JobScore instance
```

Three strategies:
- **`ProviderStrategy`** — provider-native structured output. Most reliable. OpenAI, Anthropic,
  Gemini, xAI support it.
- **`ToolStrategy`** — structured output via tool calling. Fallback for everything else.
- **Bare schema type** — LangChain auto-selects the best strategy from the model's profile.

Schemas may be Pydantic models (returns a validated instance), dataclasses, TypedDicts, or raw
JSON Schema (**must** be wrapped in an explicit strategy, and must carry top-level `title` and
`description`). If you also pass `tools`, the model must support tools + structured output
simultaneously. → `langchain/structured-output.md`

### 1.6 Middleware — the main extension point

Middleware hooks run *before and after* each step of the agent loop (model call → tool
selection → tool execution → finish). This is how you add cross-cutting behaviour without
rewriting the loop.

```python
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[...],
    middleware=[SummarizationMiddleware(...), HumanInTheLoopMiddleware(...)],
)
```

**Built-ins** (`langchain/middleware__built-in.md`, 46k): Tool error · Tool retry · Model retry ·
Model fallback · Summarization · **Human-in-the-loop** · Model call limit · Tool call limit ·
**PII detection** · To-do list · LLM tool selector · Provider tool search · Shell tool ·
Filesystem · Subagent · Rubric grading · File search · Context editing · LLM tool emulator.

Custom hooks: `langchain/middleware__custom.md` (32k).

Middleware is **not a separate runtime** — the hooks execute inside the compiled LangGraph, so
they keep working when the agent is embedded as a node in a bigger graph.

### 1.7 Human-in-the-loop (the part that matters most for approval gates)

`HumanInTheLoopMiddleware` checks every tool call against a policy. On a match it raises a
LangGraph `interrupt`, the state is checkpointed, and execution halts until a decision arrives.

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-5.5",
    tools=[write_file, execute_sql, read_data],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={
            "write_file": True,                                    # all 4 decisions allowed
            "execute_sql": {"allowed_decisions": ["approve", "reject"]},
            "read_data": False,                                    # auto-approve
        },
        description_prefix="Tool execution pending approval",
    )],
    checkpointer=InMemorySaver(),   # REQUIRED — prod: AsyncPostgresSaver / MongoDBSaver
)
```

**Four decision types:**

| Decision | Meaning |
| --- | --- |
| ✅ `approve` | Run the tool with the arguments as proposed |
| ✏️ `edit` | Modify the arguments, then run |
| ❌ `reject` | Skip the call; feedback goes back to the agent |
| 💬 `respond` | Return the human's message *as* the tool result (for `ask_user`-style tools) |

Pause / resume:

```python
config = {"configurable": {"thread_id": "some_id"}}
result = agent.invoke({"messages": [...]}, config=config, version="v2")
print(result.interrupts)   # GraphOutput.interrupts -> action_requests + review_configs

from langgraph.types import Command
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}),
             config=config, version="v2")     # same thread_id
```

**Conditional interrupts** (`langchain>=1.3.3`) — gate on the *arguments*, so the reviewer only
sees calls that genuinely need a decision:

```python
def is_write_query(request: ToolCallRequest) -> bool:
    return not request.tool_call["args"].get("query", "").lstrip().upper().startswith("SELECT")

interrupt_on={"execute_sql": {"allowed_decisions": ["approve", "reject"], "when": is_write_query}}
```

⚠️ **Gotchas**
- A checkpointer is **mandatory**; without one, interrupts cannot work.
- Decisions are a **list, in the same order** as the actions in the interrupt request.
- Use `reject` to deny a side-effecting tool. **Never** use `respond` for that — its message is
  treated as a *successful* tool result.
- Edit conservatively. Large argument changes can make the model re-plan and re-fire the tool.

→ `langchain/human-in-the-loop.md`, `langgraph/interrupts.md`

### 1.8 Multi-agent patterns

Not every complex task needs multi-agent — a single agent with the right dynamic tools and
prompt often matches it. The real drivers are **context management**, **distributed
development**, and **parallelisation**. (`langchain/multi-agent.md`)

| Pattern | How it works | Distributed dev | Parallel | Multi-hop | Talks to user |
| --- | --- | --- | --- | --- | --- |
| **Subagents** | Main agent calls subagents as tools; all routing through the main agent | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Handoffs** | Tool calls mutate a state var that switches the active agent | – | – | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Skills** | One agent loads specialised prompts/knowledge on demand | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Router** | A classifier routes to specialists, results synthesised | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | – | ⭐⭐⭐ |
| **Custom workflow** | Bespoke LangGraph topology mixing deterministic + agentic | — | — | — | — |

**Measured cost characteristics** (from the docs' own benchmarks):

| Pattern | One-shot | Repeat request | Multi-domain |
| --- | --- | --- | --- |
| Subagents | 4 calls | 8 calls | 5 calls, ~9K tokens |
| Handoffs | 3 calls | 5 calls | 7+ calls, ~14K+ tokens |
| Skills | 3 calls | 5 calls | 3 calls, ~15K tokens |
| Router | 3 calls | 6 calls | 5 calls, ~9K tokens |

Key insights the docs draw: stateful patterns (Handoffs, Skills) save **40–50% of calls on
repeat requests**; for **multi-domain fan-out**, Subagents and Router win because they
parallelise and isolate context (Skills accumulates context and pays for it on every later call).
Patterns compose — subagents can invoke routers, which can invoke custom workflows.

### 1.9 Streaming

`agent.stream(...)` for state updates; `agent.stream_events(..., version="v3")` for token-level
and tool-level events. Interrupt payloads surface on `stream.interrupts`, and
`stream.interrupted` is `True` while a run is paused for input.
→ `langchain/streaming.md` (45k), `langchain/event-streaming.md`

---

## 2. LangGraph

### 2.1 The runtime model

LangGraph models a workflow as a **graph**, built from three things:

1. **State** — a shared, typed snapshot of the application (usually a `TypedDict`).
2. **Nodes** — functions that receive state, do work, and return a state update.
3. **Edges** — functions/transitions deciding which node runs next.

> *Nodes do the work, edges tell what to do next.* Both are **just functions** — they may
> contain an LLM call or plain deterministic code. That mixing is LangGraph's core value.

Execution uses **message passing in discrete "super-steps"**, inspired by Google's **Pregel**.
Nodes start `inactive`; a node becomes `active` when a message arrives on an incoming edge/channel;
nodes that run in parallel share a super-step, sequential nodes occupy separate ones. The run
terminates when every node is inactive and no messages are in transit.
→ `langgraph/graph-api.md`, `langgraph/pregel.md`

### 2.2 Minimal graph

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
```

⚠️ **You MUST `.compile()` before use.** Compile validates structure (no orphan nodes) and is
where `checkpointer=` and breakpoints are attached.

Conditional routing and parallel fan-out/fan-in:

```python
workflow.add_conditional_edges("call_llm", should_continue)

workflow.add_edge(START, "fetch_news")      # these three run in parallel …
workflow.add_edge(START, "fetch_weather")
workflow.add_edge(START, "fetch_stocks")
workflow.add_edge("fetch_news", "combine")  # … and combine waits for all of them
workflow.add_edge("fetch_weather", "combine")
workflow.add_edge("fetch_stocks", "combine")
```

### 2.3 Graph API vs Functional API

Same runtime, same features (persistence, streaming, HITL, memory), two paradigms.
→ `langgraph/choosing-apis.md`

**Graph API** when you need: explicit shared state across nodes · complex conditional branching ·
parallel paths that merge · a visualisable structure for a team to reason about.

**Functional API** when you want: minimal change to existing procedural code · ordinary Python
control flow · function-scoped state · rapid prototyping · linear workflows.

```python
from langgraph.func import entrypoint, task

@task
def process_user_input(user_input: str) -> dict:
    return {"processed": user_input.lower().strip()}

@entrypoint(checkpointer=checkpointer)
def workflow(user_input: str) -> str:
    processed = process_user_input(user_input).result()
    if "urgent" in processed["processed"]:
        return handle_urgent_request(processed).result()
    return handle_normal_request(processed).result()
```

They **compose** — a `StateGraph` node can call an `@entrypoint`, and vice versa.

### 2.4 Persistence — checkpointers vs stores

Two complementary systems. Most real apps use **both**.

|  | **Checkpointer** | **Store** |
| --- | --- | --- |
| Persists | Graph state snapshots | Application-defined key-value data |
| Scope | A single thread | Across threads |
| Memory type | Short-term, thread-scoped | Long-term, cross-thread |
| Use for | Conversation continuity, HITL, time-travel, fault tolerance | User preferences, facts, shared knowledge |
| Access | `thread_id` in graph config | Read/write items from nodes or app code |

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

graph = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())
result = graph.invoke({"messages": [...]}, {"configurable": {"thread_id": "thread-1"}})
```

**Production checkpointers:** `PostgresSaver` / `AsyncPostgresSaver` (Postgres, async),
`SqliteSaver` (local file, dev), `MongoDBSaver`.

⚠️ **Persistence gotchas** (`langgraph/persistence.md`)
- `InMemorySaver` / `MemorySaver` live in RAM — **everything is lost on restart**. Never ship it.
- `PostgresSaver` stores `thread_id` in a length-limited column → keep it **under 255 chars**.
- Checkpoints **grow unboundedly** over long conversations. Prune on a schedule / retention policy.
- Subgraphs keep their **own checkpoint namespace**; a parent may not see subgraph state
  immediately. Cross that boundary with a **Store**.
- `checkpointer.setup()` creates the tables and indexes — call it once.

→ `langgraph/checkpointers.md` (40k: threads, checkpoints, get/update state, replay,
durability modes, custom checkpointers), `langgraph/stores.md`

### 2.5 Interrupts (durable human-in-the-loop)

```python
from langgraph.types import interrupt, Command

def review_node(state):
    decision = interrupt({"draft": state["draft"], "action": "Please review"})
    return {"approved": decision == "approve"}

graph.invoke(Command(resume="approve"), config={"configurable": {"thread_id": "t1"}})
```

The value passed to `interrupt()` surfaces to the caller; the value you resume with becomes
`interrupt()`'s **return value** inside the node. The graph waits **indefinitely** — state is
safely checkpointed, so "waiting for a human" can mean days.

⚠️ **Rules of interrupts** — these are the ones that silently corrupt runs:
1. **Do not wrap `interrupt()` in try/except.** It works by raising.
2. **Do not reorder `interrupt()` calls within a node.** Resume matches them positionally.
3. **Do not return complex values** from `interrupt()` calls.
4. **Any side effect performed before an `interrupt()` must be idempotent** — the node is
   **re-executed from the top** on resume. This is the single most common HITL bug: an email
   sent before the interrupt gets sent twice.

Static **breakpoints** pause before/after a named node; `interrupt()` is **dynamic** — anywhere
in your code, conditional on your own logic. → `langgraph/interrupts.md` (29k)

### 2.6 Other capabilities worth knowing exist

| Capability | Page |
| --- | --- |
| Time travel / replay / fork from a checkpoint | `langgraph/use-time-travel.md` |
| Subgraphs + checkpointer scoping | `langgraph/use-subgraphs.md` |
| Fault tolerance, retries, durability modes | `langgraph/fault-tolerance.md` |
| Streaming modes & custom stream channels | `langgraph/streaming.md`, `frontend__custom-stream-channels.md` |
| Workflows vs agents (when to hard-code the flow) | `langgraph/workflows-agents.md` |
| Agentic RAG reference implementation | `langgraph/agentic-rag.md` |
| Project layout for deployment | `langgraph/application-structure.md` |
| Local dev server | `langgraph/local-server.md` |

---

## 3. MCP

LangChain consumes MCP servers as tool sources, which is directly relevant to existing MCP work.

```
langchain/mcp.md            — install, quickstart, transports
langchain/mcp__connections.md — connection lifecycle & transport config
langchain/mcp__tools.md       — exposing MCP tools to an agent (+ HITL over them)
langchain/mcp__auth.md        — OAuth / auth flows
```

---

## 4. Cheat-sheet of things that will bite

| # | Trap | Correct behaviour |
| --- | --- | --- |
| 1 | Writing LangChain 0.x code (`LLMChain`, `AgentExecutor`, `initialize_agent`) | Gone in 1.0. Only `create_agent`. Legacy → `langchain-classic`. |
| 2 | `from langchain_core.messages import ...` | Use `from langchain.messages import ...` |
| 3 | Forgetting `.compile()` | Graph is unusable until compiled |
| 4 | `InMemorySaver` in production | Use `AsyncPostgresSaver` / `PostgresSaver` |
| 5 | HITL without a checkpointer | Interrupts require persistence — mandatory |
| 6 | Non-idempotent side effect before `interrupt()` | Node re-runs from the top on resume → duplicate action |
| 7 | `try/except` around `interrupt()` | Swallows the control-flow exception |
| 8 | Resume decisions in the wrong order | Must match the order of `action_requests` |
| 9 | Using `respond` to deny a tool | `respond` = *successful* tool result. Use `reject`. |
| 10 | Raw JSON Schema straight into `response_format` | Wrap in `ProviderStrategy`/`ToolStrategy`; needs `title` + `description` |
| 11 | `thread_id` > 255 chars with Postgres | Use a UUID |
| 12 | Assuming a parent graph sees subgraph state | Separate checkpoint namespaces — use a Store |
| 13 | Unbounded checkpoint growth | Prune / retention policy |
| 14 | Reaching for multi-agent too early | One agent + dynamic tools often matches it, cheaper |

---

## 5. How to use this knowledge base

1. **Locate** — `INDEX.md` lists all 104 pages with their section headings.
2. **Find a symbol** — `API-REFERENCE.md` maps every import and function in the docs to the
   pages that document it.
3. **Grep** — the corpus is plain markdown:
   ```bash
   grep -ril "HumanInTheLoopMiddleware" knowledge-base/
   grep -n  "interrupt_on"              knowledge-base/langchain/human-in-the-loop.md
   ```
4. **Read the page** before writing code against an API. This summary is a map, not the terrain.

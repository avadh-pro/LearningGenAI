# End to End Architecture of a Single Agent — Video Notes

Condensed, transcript-based notes from a TMLC Academy session on the internal architecture of a single AI agent. See *End to End Architecture of a Single Agent - Transcript.md* in this folder for the full source recording transcript. This session has no dedicated reading deck of its own — the architecture diagram below is borrowed from *Core Components of an AI Agent.pdf* (a companion Week 4 reading) because it illustrates the same layered structure the video walks through.

**The core idea, in one picture:**

![AI Agent Architecture Diagram](End%20to%20End%20Architecture%20of%20a%20Single%20Agent/agent-architecture-diagram.png)

**The analogy that runs through this whole document 🖥️**

Think of a single agent as a **mini operating system**. The interface is the keyboard and screen — how requests get in and answers get out. The controller is the OS kernel, running the main loop and keeping track of state. The reasoner is the CPU, actually deciding what happens next. Tools are the installed programs the OS can launch to get real work done. Memory is the filesystem — nothing survives a restart without it. Policy and safety is the permissions system, blocking a program from doing something it isn't allowed to. And observability is Task Manager plus the system log — without it, the whole machine is a black box you can't debug. This session is a tour of that OS, layer by layer.

---

## 1. The Core Loop

Every agent, no matter how it's built, runs the same basic loop:

1. **Receive input and context.**
2. **Plan the next action.**
3. **Call a tool or query knowledge**, and observe the result.
4. **Decide whether to continue or stop.**
5. **Produce an answer, and write to memory.**

This loop is what turns a single LLM call into something that can act, check its own work, and keep going until the job is actually done — rather than answering once and stopping regardless of whether the task succeeded.

---

## 2. The Six Subsystems

The video breaks a single agent down into six layers, each with its own job:

| Layer | What it does |
|---|---|
| **Interface** | Where requests come in — REST/WebSocket API, chat UI, or voice |
| **Reasoner** | The agent's "brain" — an LLM that decides what happens next |
| **Tools & connectors** | Functions/APIs the agent calls to take real action |
| **Memory** | Gives the agent continuity and recall across turns |
| **Policy & safety** | Gatekeeper — checks every action is compliant and within limits |
| **Observability** | Logging and metrics that make the agent debuggable in production |

### Interface

Standardize every incoming message with fields like **user ID, session ID, input text, locale, and channel**, then hand it to the controller, which runs the reasoning loop. Always include **timeouts, iteration limits, and a request ID** — without these, a misbehaving loop can run forever, and you'd have no way to trace what happened. Support streaming output so the agent *feels* responsive, even on a multi-step task.

### Reasoner & Prompts

The reasoner is the agent's brain — it understands the goal and decides what to do, guided by system and planning prompts. To keep responses consistent and auditable, the video's design requests **structured JSON output** rather than free text. Keep prompts short, clear, and schema-based.

**Worked example — a refund request:**

The reasoner receives a structured input packaging together everything it needs:
- **Request:** "I want to issue a refund for customer C123."
- **Context:** session info, role, recent conversation turns.
- **Memory:** known facts, e.g. "customer C123 has recent orders."
- **Available tools:** `search_orders`, `initiate_refund`.
- **Policies:** what's allowed — e.g. support agents can refund orders, but cannot delete accounts.
- **Goal:** "process the refund request safely and accurately."

Given all of that at once, the reasoner doesn't just guess — it infers that it needs the customer's order history *before* it can safely issue a refund, and outputs a structured plan: call `search_orders` with the customer ID, set `stop = false` (keep the loop going), and log the rationale ("need order history before issuing refund").

> 🧾 **Why JSON output matters:** a free-text "I'll check their orders first" is a *description* of a plan. A structured `{tool: "search_orders", stop: false, rationale: "..."}` is an *executable, auditable* plan — the difference between an agent you can trust in production and one you can only read about after the fact.

### Tools & Connectors

Tools are how the agent actually acts in the world — search a database, send an email, check a CRM, run a Python function, fetch from the web. Every tool call goes through the same validated flow:

```
Reasoner selects a tool (e.g. search_orders)
        │
        ▼
Controller validates input against the tool's schema
        │
        ▼
Controller checks policies & permissions
        │
        ▼
Tool executes
        │
        ▼
Controller receives a structured response (data, execution time, errors, status)
```

That structure — validate, check permissions, execute, return a structured result — is what keeps every tool call safe, traceable, and consistent, rather than the agent just calling arbitrary code and hoping for the best.

### Memory

Without memory, every message looks brand new to the agent — it has no idea what happened a turn ago. Three types, in increasing scope:

- **Short-term memory** — recent conversation context, scoped to the current session or task.
- **Long-term memory** — facts and outcomes that persist *across* sessions, so the agent remembers past interactions.
- **Semantic memory** — relevant information pulled from documents, databases, or knowledge graphs (this is where RAG-style retrieval plugs into an agent).

> 🧠 **Analogy:** this is genuinely just how human memory works too — short-term is what you're holding in your head *right now*, long-term is what you actually remember about someone the next time you meet them, and semantic memory is being able to go look something up when you don't already know it.

### Policy & Safety

This layer sits **between** the reasoner and the tools — nothing executes without passing through it first.

- **Before execution:** validate inputs, user roles, and permissions. Anything unsafe or out of policy is blocked, and the reason is logged for audit.
- **During execution:** confirm tools are being used correctly and within allowed limits.
- **After execution:** scan the output for sensitive data (PII, restricted info) and sanitize it before returning. Apply rate limits and usage budgets per session.

**Flow:** reasoner proposes → guardrails validate → unsafe actions blocked → valid ones execute → output checked and logged. Every action stays authorized, compliant, and secure — protecting the user *and* the system.

### Observability

Every loop turn — every prompt, tool call, and result — gets logged in a structured format. Each request gets a **trace ID**, so you can follow one request's complete path across the reasoner, guardrails, and tools. Track **latency, token usage, cost, and success rate**. Errors are captured with full context so they're actually debuggable, not just a stack trace with no story attached. All of this feeds dashboards showing accuracy, resolution rate, and time-to-answer.

> 📊 **One line:** observability is what turns the agent from a black box into something you can actually trust, monitor, and keep improving — without it, you're debugging a system you can't see inside.

---

## Key Takeaways

1. **Every agent runs the same core loop** — perceive, plan, act, decide to continue or stop, answer and write to memory — regardless of how it's implemented.
2. **Six layers do six distinct jobs:** interface (in/out), reasoner (decide), tools (act), memory (remember), policy (gatekeep), observability (see).
3. **Structured JSON reasoning output**, not free text, is what makes an agent's decisions auditable and deterministic enough to trust in production.
4. **Policy & safety sits between reasoner and tools** — every action is validated before it runs and sanitized after, not just checked once at the start.
5. **Observability is not optional** — trace IDs, metrics, and structured logs are what let you debug and improve an agent you can't otherwise see inside.

---

## 🎤 Interview Prep — Mock Interview (Single-Agent Architecture)

*Same two-layer format as the other Video Notes files in this repo: a plain-language answer with an example, then a crisp, technically precise version.*

---

**🎙️ Interview Q1:** "Why does the reasoner output structured JSON instead of just writing out its plan in natural language?"

**✅ Strong answer:** "Because a free-text plan like 'I should check their order history first' is just a description — a human can read it, but nothing downstream can safely act on it. A structured output like `{tool: search_orders, args: {customer_id: C123}, stop: false, rationale: ...}` is directly executable: the controller can validate it against the tool's schema, check it against policy, and log exactly what happened and why, all without an LLM re-parsing free text. It turns the agent's 'thinking' into something auditable."

**🎯 Standard Interview Answer:** "Structured (typically JSON) reasoning output enforces a machine-parseable action schema, which is what makes downstream validation, policy enforcement, and audit logging possible without an additional parsing or intent-extraction step. It also constrains the reasoner's output space, which improves consistency and reduces the chance of the model producing an action the rest of the system can't execute safely."

---

**🎙️ Interview Q2:** "Where exactly does the policy and safety layer sit in the request flow, and why does it check at multiple points rather than just once?"

**✅ Strong answer:** "It sits directly between the reasoner and the tools — every single action has to pass through it, not just the first one in a session. It checks at three points: before execution (is this action even allowed for this user/role), during execution (is the tool being used within its limits), and after execution (does the output contain anything sensitive that needs to be sanitized before it goes back to the user). A single check at the start wouldn't catch a tool being misused mid-call, or a legitimate action returning data that shouldn't be exposed."

**🎯 Standard Interview Answer:** "The policy/safety layer is interposed between the reasoner and the tool execution layer, and applies at three checkpoints: pre-execution authorization (role and permission validation), in-execution constraint enforcement (rate limits, usage budgets, tool-specific limits), and post-execution output sanitization (PII and sensitive-data scrubbing). Checking only once, pre-execution, would miss both misuse during a long-running tool call and sensitive data surfaced only in the tool's response."

---

**🎙️ Interview Q3:** "The video describes three types of memory — short-term, long-term, and semantic. How would you decide what belongs in each for a real production agent?"

**✅ Strong answer:** "Short-term memory is anything scoped to the current session — the last few turns of conversation, what the user just asked. That's what makes a follow-up question like 'what about the second one?' make sense. Long-term memory is facts that should survive *between* sessions — this customer's past orders, their preferences, things you'd want the agent to remember next week too. Semantic memory is different from both: it's not about *this* conversation at all, it's a retrieval layer over documents, databases, or a knowledge graph — this is literally where RAG plugs into an agent. The test I'd use: does it need to persist past this session (long-term vs short-term), and is it a fact about *this interaction* or something being looked up from an external knowledge source (short/long-term vs semantic)."

**🎯 Standard Interview Answer:** "Short-term memory is session-scoped conversational state; long-term memory is durable, cross-session state about entities (users, accounts, past outcomes); semantic memory is retrieval-based access to external knowledge sources — documents, databases, knowledge graphs — and is architecturally where RAG-style retrieval integrates with an agent rather than being a separate memory type. The design decision is driven by persistence scope (session vs. cross-session) and source (interaction-derived facts vs. external knowledge lookup)."

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

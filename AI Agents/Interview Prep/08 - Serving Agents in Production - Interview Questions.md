# Serving Agents in Production — Interview Questions

*Built from* Serving AI Agents with FastAPI *and the Week 4 deployment material.*

*Scoped to **getting an agent in front of real users** — the API layer, latency, cost, guardrails, and the failure modes that only appear under production traffic. Measurement is `07`. This is the senior-level differentiator set. Two-layer answers throughout.*

---

**🎙️ Interview Q1:** "You have a working agent in a notebook. What has to change before it serves real traffic?"

**✅ Strong answer:** "More than people expect. The notebook version is missing everything that makes a system operable:

**State goes external.** `InMemorySaver` dies with the process and isn't visible to a second instance. Postgres or equivalent.

**Streaming becomes mandatory.** A multi-step agent takes 10–30 seconds. Nobody waits that long at a blank screen — you stream, so the user sees progress.

**Budgets get enforced.** Step caps, token caps, wall-clock timeouts. In a notebook an infinite loop is an annoyance; in production it's an unbounded bill.

**Secrets leave the code.** Environment variables or a secrets manager, never the repo.

**Tracing gets turned on.** An untraced agent is unoperable — you cannot answer 'why did this user get a wrong answer' without it.

**Errors become graceful.** Tool times out, model rate-limits, retrieval returns nothing — each needs a defined behaviour, not a stack trace.

The summary I'd give: **a notebook agent optimises for demonstrating capability; a production agent optimises for bounded failure.**"

**🎯 Standard Interview Answer:** "The gap spans six areas. State persistence must move from in-process to a shared durable store, since in-memory checkpointing is neither crash-durable nor visible across horizontally scaled instances. Response delivery must become streaming, as multi-step trajectory latency of 10–30 seconds is incompatible with synchronous request-response UX. Resource budgets — step count, token consumption, wall-clock — must be enforced, since unbounded loops translate directly into unbounded cost. Credentials must externalise to environment or secrets management. Tracing must be instrumented, as failure attribution is impossible without per-span telemetry. And degraded paths — tool timeout, provider rate limiting, empty retrieval — require specified behaviour rather than unhandled propagation."

---

**🎙️ Interview Q2:** "Why FastAPI specifically, and what does it actually give you?"

**✅ Strong answer:** "It turns Python functions into HTTP endpoints with a decorator, and three things make it the default for this:

**Async native.** Agent work is almost entirely waiting — on the model, on tools, on retrieval. Async means one worker handles many concurrent requests while they wait, instead of blocking. For I/O-bound agent workloads that's a large throughput difference.

**Pydantic validation.** Request and response schemas are typed and validated at the boundary, so malformed input fails with a clear 422 rather than surfacing deep inside your agent.

**Streaming support.** Server-sent events or streaming responses map cleanly onto LangGraph's `stream`, which is exactly what you need.

Plus auto-generated OpenAPI docs, which matters when a frontend team consumes your endpoint.

The caveat worth stating honestly: **FastAPI wraps the agent, it doesn't integrate with it.** It gives you an HTTP boundary. Concurrency limits, queueing, and per-user budgets are still yours to build."

**🎯 Standard Interview Answer:** "FastAPI provides ASGI-native asynchronous request handling, which suits agent workloads since trajectory time is dominated by I/O wait on model and tool calls — async concurrency yields substantially higher throughput per worker than synchronous blocking for this profile. Pydantic-based schema validation enforces typed contracts at the boundary, converting malformed input into structured 422 responses rather than deep-stack failures. Native streaming response support maps onto graph streaming for incremental delivery. OpenAPI schema generation supports client integration. FastAPI supplies the transport and validation boundary only — concurrency control, request queueing, and per-tenant budget enforcement remain application concerns."

---

**🎙️ Interview Q3:** "How do you handle an agent request that takes 45 seconds?"

**✅ Strong answer:** "Don't hold an HTTP request open for 45 seconds — timeouts, proxies and load balancers will fight you.

Two viable patterns:

**Stream it.** Open a streaming response and emit progress as nodes complete. The connection stays open but the user sees continuous output, so perceived latency is far lower. Right for interactive chat.

**Make it a job.** `POST` returns a job ID immediately; the client polls or gets a webhook. Right for genuinely long work — a research agent running several minutes.

The decision rule is the one I'd use for Prefect versus LangGraph too: **is a user sitting there waiting for this?** If yes, stream. If no, queue it.

And regardless of pattern, put a **hard wall-clock timeout** on the trajectory. An agent with no timeout will eventually find an input that makes it run forever."

**🎯 Standard Interview Answer:** "Long-running trajectories should not occupy a synchronous request. Two patterns apply. Streaming responses maintain an open connection while emitting incremental node-level output, substantially reducing perceived latency; appropriate for interactive sessions. Asynchronous job submission returns a job identifier immediately with completion delivered by polling or webhook; appropriate where trajectory duration exceeds reasonable connection lifetime. The selection criterion is whether a user is synchronously awaiting the result. Independently, a hard wall-clock bound on trajectory execution is required — unbounded trajectories are a reliable eventual outcome of adversarial or pathological inputs."

---

**🎙️ Interview Q4:** "Where does latency actually go in an agent, and what do you do about it?"

**✅ Strong answer:** "**Sequential model calls dominate.** Each reasoning step is 1–3 seconds, and steps are serial by nature — step 2's input depends on step 1's output. So a six-step agent has a floor of maybe 10 seconds before you've done anything wrong.

Where the time goes, roughly: reasoning steps, then tool latency, then retrieval.

What actually helps:

**Cut steps.** The biggest lever by far. Better tool descriptions mean fewer wrong-tool detours. Combining two narrow tools into one removes a whole round trip.

**Parallelise independent tool calls.** If the agent needs weather *and* traffic, those don't depend on each other — issue both at once. Modern tool calling supports multiple calls in one turn.

**Use a smaller model for easy steps.** Routing and classification don't need the frontier model.

**Stream** so perceived latency drops even when actual latency doesn't.

**Cache the stable prefix.** Prompt caching on system prompt plus tool schemas.

The thing to emphasise: **measure p95 and p99, not the mean.** An agent whose mean is 4 seconds but whose p99 is 40 has a real problem that the average hides completely."

**🎯 Standard Interview Answer:** "Latency is dominated by sequential inference: each reasoning step contributes 1–3 seconds and steps are causally serial, establishing a floor proportional to trajectory length. Mitigations in order of effect size: trajectory shortening through improved tool schema disambiguation and tool consolidation, which removes entire round trips; parallel dispatch of independent tool calls, supported by multi-call tool-calling APIs; difficulty-based model routing for classification and routing steps; response streaming to reduce perceived rather than actual latency; and prompt caching over the stable instruction and schema prefix. Measurement must target tail percentiles — mean latency systematically conceals the long-tail trajectories that dominate user-perceived reliability."

---

**🎙️ Interview Q5:** "What guardrails does a production agent need, and where do they sit?"

**✅ Strong answer:** "Two layers, and the distinction matters:

**Pre-model (input):** validation, PII redaction, prompt-injection screening, rate limiting per user.

**Post-model (output and action):** schema enforcement, refusal policy, fact-checking against retrieved context — and critically, **checks on the action, not just the text.**

That last point is the agent-specific one. A chatbot's output guardrail checks what it says. An agent's has to check what it's about to *do*. Screening the text while letting an unchecked `transfer_funds` call through misses the actual risk.

Beyond content guardrails, production agents need **budget managers** — step, token, time and money counters — **loop detectors** for repeated failing actions, and **human approval gates** for irreversible operations.

The framing: **prompt-level guardrails are guidance; code-level guardrails are controls.** Only the second survives an adversarial input, and agents consume untrusted content by design."

**🎯 Standard Interview Answer:** "Guardrails operate at two layers. Pre-inference: input validation, PII redaction, prompt-injection screening, per-principal rate limiting. Post-inference: output schema enforcement, refusal policy application, groundedness verification against retrieved context, and — agent-specifically — action-level authorisation applied to the tool invocation rather than only to generated text. Text-level screening is insufficient where the consequential output is an action. Additional production controls: budget managers enforcing step, token, wall-clock and monetary limits; loop detection for repeated non-progressing actions; and human approval interrupts on irreversible operations. Prompt-level constraints are advisory and defeasible; enforcement must reside in the execution path."

---

**🎙️ Interview Q6:** "What happens when a tool fails mid-trajectory?"

**✅ Strong answer:** "It has to be a *specified* behaviour, because the default is bad — the agent reasons over a failure message and frequently confabulates around it.

The hierarchy I'd build:

**Return an actionable error, not an exception.** `"Search timed out — no results available"` rather than a stack trace or `None`. The model can act on the first and will invent around the second.

**Retry transient failures in code,** not by letting the agent retry. Rate limits and timeouts should be handled with backoff below the agent, so it never sees them.

**Degrade explicitly.** If the search tool is down, the agent should say it couldn't search — not answer from parametric memory and present it as researched.

**Cap retries.** Otherwise you get the classic loop: same call, same failure, forever.

The failure mode to name: **silent tool degradation.** An API that returns an empty list instead of an error is the nastiest case — every span looks green, the trace shows success, and the answer is wrong. Validating that tool output is *semantically* non-empty, not just structurally valid, is what catches it."

**🎯 Standard Interview Answer:** "Tool failure behaviour must be explicitly specified; default propagation produces confabulation, as models reason over error strings and generate plausible substitutes. Design hierarchy: return actionable natural-language error semantics rather than exceptions or null values, since null returns provide no signal distinguishing absence from failure; handle transient failures — rate limiting, timeout — with backoff below the agent boundary so they are not surfaced to the model at all; implement explicit degradation, where unavailability of a retrieval or search tool produces acknowledged inability rather than parametric-memory substitution presented as retrieved; and bound retry counts to prevent non-progressing loops. The highest-severity variant is silent degradation, where structurally valid but semantically empty responses render the failure invisible to both tracing and schema validation, requiring semantic non-emptiness checks at the tool boundary."

---

**🎙️ Interview Q7:** "How do you control cost once this is live?"

**✅ Strong answer:** "Cost is **steps × context size**, and both grow during a run, so I'd attack both plus add hard limits.

**Hard budgets first.** Per-request step and token caps, and a per-user daily cap. This is the control that stops a bad day becoming a bad invoice.

**Route by difficulty.** Reported figures put routine requests at 60–80% of agent traffic; sending those to a small model typically saves 40–70%. Highest-leverage single change.

**Prompt caching** on the stable prefix — system prompt and tool definitions are identical every call.

**Context management** so the transcript doesn't grow unbounded, since every step re-sends it.

**Cache at the semantic level** where inputs repeat — many production agents see the same handful of questions constantly.

The mistake I'd flag: obsessing over model price per token while ignoring step count. Halving steps beats switching models, and it usually improves latency and reliability at the same time."

**🎯 Standard Interview Answer:** "Cost scales as the product of trajectory length and per-step context size, both increasing during execution. Controls: hard per-request step and token budgets plus per-principal daily caps, which bound worst-case exposure; difficulty-based model routing, where roughly 60–80% of steps are routine and downward routing yields 40–70% savings; prompt caching over the invariant system-instruction and tool-schema prefix; context management to prevent unbounded transcript resubmission; and semantic response caching where input distributions exhibit repetition. Trajectory-length reduction dominates per-token price optimisation in effect size and additionally improves latency and reliability, whereas model substitution trades quality against cost."

---

**🎙️ Interview Q8:** "Name the production failure modes that don't show up in testing."

**✅ Strong answer:** "The ones that bite are the ones that need real traffic to appear:

**Silent tool degradation.** An upstream API starts returning empty results instead of errors. Nothing alerts; quality quietly drops.

**Cascading decision errors.** An early wrong step is treated as fact by everything downstream, so a small error becomes a confidently wrong answer.

**Distribution drift.** Real users ask things your test set didn't contain. Your offline scores stay green while satisfaction falls — the metric–production gap.

**Latency-driven correctness erosion.** Under load you shorten timeouts or truncate context to keep latency acceptable, and quality degrades as a side effect of a performance fix.

**Proxy goal convergence.** The agent optimises the measurable thing rather than the intended thing — closing tickets rather than resolving problems.

**Cost blowups on rare inputs.** One pathological query loops thirty times. Mean cost looks fine; the p99 is where the money goes.

The common thread: **all of them are invisible to output-only, happy-path testing.** They need production traces, tail-percentile monitoring, and a feedback loop from real usage."

**🎯 Standard Interview Answer:** "Production-specific failure modes include: silent tool degradation, where upstream services return structurally valid empty responses producing unalerted quality loss; cascading decision errors, where upstream inaccuracies are consumed downstream as established fact and amplified into confident incorrect output; distribution drift, where production input diverges from the evaluation set producing the metric–production gap in which offline scores improve as satisfaction declines; latency-driven correctness erosion, where load-induced timeout reduction or context truncation degrades quality as a side effect of performance remediation; proxy goal convergence, where the agent optimises the measured objective rather than the intended one; and tail-distribution cost events, where pathological inputs produce extreme trajectory lengths invisible in mean cost. All are undetectable by output-only happy-path testing and require production trace capture, tail-percentile monitoring and a production-to-evaluation feedback loop."

---

**🎙️ Interview Q9:** "Design an agent serving architecture. What are the components?"

**✅ Strong answer:** "Working outward from the agent:

```
Client
  │  (streaming)
API layer (FastAPI)    ── auth, validation, rate limit, per-user budget
  │
Guardrails (input)     ── PII redaction, injection screening
  │
Agent runtime          ── LangGraph, step + time budgets, loop detection
  ├── Checkpointer ──► Postgres        (thread state, HITL resume)
  ├── Store       ──► Postgres/vector  (long-term memory)
  ├── Tools       ──► internal APIs, search, MCP servers
  └── LLM         ──► with routing: small model for easy steps
  │
Guardrails (output)    ── schema, groundedness, ACTION authorisation
  │
Observability          ── traces (OTel), metrics (Prometheus/Grafana),
                          sampled online evaluation
```

Three decisions I'd call out:

**Checkpointer on Postgres, not SQLite** — multiple instances must see the same threads, otherwise a load balancer silently breaks conversation memory.

**Action authorisation in the output guardrail layer**, not the prompt — that's the enforcement point.

**Two observability tracks:** operational metrics in Prometheus/Grafana, and LLM quality in a tracing tool like Langfuse or Opik. They answer different questions and you need both.

And a human-approval path branching out of the agent runtime for irreversible actions, which works only because the checkpointer makes the pause durable."

**🎯 Standard Interview Answer:** "Layered architecture: client with streaming transport; an API boundary providing authentication, schema validation, rate limiting and per-principal budget enforcement; an input guardrail stage performing PII redaction and injection screening; the agent runtime with step, token and wall-clock budgets plus loop detection; a checkpointer backed by a shared relational store for thread state and interrupt resumption; a long-term memory store; a tool layer spanning internal APIs, retrieval and MCP servers; model access with difficulty-based routing; an output guardrail stage enforcing schema, groundedness and — critically — action authorisation; and an observability layer capturing OpenTelemetry traces, operational metrics, and sampled online evaluation. Three load-bearing decisions: shared durable checkpointing rather than node-local storage, since instance-local state breaks under non-sticky load balancing; action authorisation positioned in the execution path rather than expressed as prompt constraint; and separation of operational metrics from LLM quality evaluation into distinct observability tracks answering distinct questions."

---

## Sources

- [The Complete Agentic AI System Design Interview Guide 2026](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)
- [AI Agent System Design Interview: Planning, Tool Execution, Memory, and Human Approval — PracHub](https://prachub.com/resources/ai-agent-system-design-interview-planning-tool-execution-memory-and-human-approval)
- [Design an AI Agent: Agentic System Design Interview — System Design Academy](https://www.systemdesign.academy/interview/design-ai-agent)
- [Resource Constraints and Performance in Agentic AI Systems (arXiv)](https://arxiv.org/pdf/2608.27886)
- [Evaluating Agentic AI in the Wild: Failure Modes, Drift Patterns, and a Production Evaluation Framework (arXiv)](https://arxiv.org/pdf/2605.01604)
- [From Failure Modes to Reliability Awareness in Generative and Agentic AI Systems (arXiv)](https://arxiv.org/pdf/2511.05511)
- [How to Answer AI System Design Interview Questions — KDnuggets](https://www.kdnuggets.com/how-to-answer-ai-system-design-interview-questions)

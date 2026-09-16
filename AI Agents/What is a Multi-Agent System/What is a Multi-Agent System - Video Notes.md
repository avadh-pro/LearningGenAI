# What is a Multi-Agent System? — Video Notes

Condensed, transcript-based notes from a TMLC Academy session introducing multi-agent systems. See *What is a Multi-Agent System - Transcript.md* in this folder for the full source recording transcript. No dedicated reading deck exists for this session, so the diagram below is drawn from the session's own description of the supervisor-worker pattern rather than a slide image.

**The core idea, in one picture:**

```mermaid
flowchart TD
    U["User Request"] --> S["Supervisor Agent<br/>interprets & decomposes the task"]
    S --> W1["Worker Agent<br/>(retrieval)"]
    S --> W2["Worker Agent<br/>(reasoning)"]
    S --> W3["Worker Agent<br/>(tool execution)"]
    W1 --> S2["Supervisor<br/>merges & verifies outputs"]
    W2 --> S2
    W3 --> S2
    S2 --> R["Final Response"]
```

**The analogy that runs through this whole document 🏢**

A single agent is one person trying to do an entire company's work alone — task understanding, execution, and verification, all by themselves, one thing at a time. A multi-agent system is that same company once it hires a **team**: a manager who breaks the big job into pieces and hands each piece to the specialist best suited for it, specialists who each do their focused part and report back, and a way for everyone to actually talk to each other and see the same shared notes. Every concept in this session — why multi-agent systems exist, the four building blocks, the four collaboration patterns — is really just describing how you'd organize *any* team, applied to AI agents instead of people.

---

## 1. Why One Agent Isn't Always Enough

A single-agent setup is one LLM loop responsible for understanding the task, decomposing it, executing it, *and* verifying the result. That works for simple, linear tasks — but it quickly becomes a bottleneck once the work is complex, distributed, or needs several kinds of specialized intelligence at once.

A **multi-agent system** distributes that same work across several specialized agents that coordinate through message passing or shared state. This buys three things a single agent structurally can't give you:

- **Specialization** — each agent is tuned for one capability (summarization, retrieval, reasoning, API orchestration) instead of one model trying to be good at everything.
- **Scalability** — tasks run in parallel, across different tools, models, and compute environments.
- **Reliability** — if one agent's output is uncertain, another agent can verify, correct, or augment it, rather than a single point of failure deciding everything alone.

**One line:** a single agent does the whole job serially and checks its own work; a multi-agent system splits the job, runs pieces in parallel, and lets agents cross-check each other.

---

## 2. The Four Core Components

Every multi-agent system is built from the same four layers:

| Component | Role |
|---|---|
| **Agents** | Specialized workers focused on one job — reasoning, retrieval, planning, or tool execution |
| **Coordinator / Orchestrator** | The decision-maker: assigns tasks, resolves conflicts, keeps the system moving toward the final goal |
| **Shared memory / context store** | Holds intermediate results, conversation state, and task progress, so every agent sees the same source of truth |
| **Communication protocol** | Messages, API calls, or graph edges — how agents actually talk to each other and to external tools |

> 🏢 **Analogy, continued:** agents are the specialists on the team. The coordinator is the manager, deciding who does what and settling disagreements. Shared memory is the shared team doc everyone reads and writes to, so nobody's working off stale information. The communication protocol is just... how they actually talk to each other — Slack messages, a shared ticket system, whatever the mechanism is.

---

## 3. Four Collaboration Patterns

These are four different ways to organize that team, each suited to a different style of task.

### Planner–Executor

A **planner** agent breaks the user's request into a structured sequence of steps — essentially generating a mini-workflow. An **executor** agent then performs each step in that sequence: calling APIs, running tools, retrieving data, generating intermediate outputs.

**Why it's useful:** separating "decide the steps" from "carry out the steps" gives deterministic execution, clearer reasoning, and much easier debugging — which is why this is one of the most widely used patterns in real agentic systems.

### Supervisor–Worker

The user talks to a single **supervisor** agent. The supervisor interprets the query, breaks it into subtasks, and decides which specialized **worker** agents are best suited for each part. Each worker handles its own focused capability — possibly invoking several tools or steps of its own — and the supervisor collects, merges, and verifies all the intermediate outputs before returning the final response.

**Why it's useful:** this pattern mirrors how real organizations actually work, which is exactly why it scales well to complex, multi-step tasks that genuinely need several different competencies running in parallel.

### Critic–Refiner

The supervisor routes the query to a **response generator**, which produces a fast, broad first draft. That draft then goes to a **critic-refiner** agent, which evaluates it for correctness, completeness, style, safety, or domain-specific constraints — and can rewrite it, fix hallucinations, or add missing detail. The refined result goes back to the supervisor, which may run additional checks before sending the final, polished response to the user.

**Why it's useful:** this is the pattern to reach for in high-stakes domains, where you genuinely need *both* fast creative generation *and* careful verification, and don't want either quality to come at the expense of the other.

### Peer-to-Peer (Decentralized)

Not every architecture needs a central orchestrator. In a peer-to-peer setup, agents collaborate directly — for example, a knowledge agent might trigger a memory agent to update information without waiting for a supervisor to coordinate the interaction.

**Why it's useful:** this pattern is lightweight and reactive, well-suited to agents that need to synchronize state continuously or perform autonomous background updates without a manager in the loop for every single interaction.

| Pattern | Structure | Best suited for |
|---|---|---|
| Planner–Executor | Plan first, then execute the plan step by step | Deterministic, well-defined multi-step tasks |
| Supervisor–Worker | Central supervisor delegates to specialized workers | Complex tasks needing several competencies in parallel |
| Critic–Refiner | Generate a draft, then a second agent verifies/improves it | High-stakes domains needing both speed and verification |
| Peer-to-Peer | No central orchestrator — agents trigger each other directly | Continuous state sync, autonomous background work |

---

## 4. Real-World Applications

| Domain | How agents split the work |
|---|---|
| **Customer support automation** | A planner agent identifies intent → a response agent drafts the answer → an evaluator verifies accuracy and tone before sending it |
| **Enterprise AI assistance** | One agent retrieves data → another generates structured reports → a third validates compliance (especially important in regulated industries) |
| **Research co-pilots** | A researcher agent explores sources → an extractor pulls relevant information → a summarizer condenses it into a clean, usable output |
| **Software automation** | A planner breaks down tasks → an agent interacts with the UI/workflow → a validator checks the results meet expectations |

Across every one of these, the point is the same: multi-agent systems let AI behave like a **coordinated team**, not a standalone model trying to do everything itself.

---

## Key Takeaways

1. **A single agent hits a bottleneck on complex work** — one loop doing understanding, execution, and verification serially doesn't scale.
2. **Multi-agent systems buy specialization, scalability, and reliability** by distributing work across agents that can run in parallel and cross-check each other.
3. **Four components make it work:** the agents themselves, a coordinator, shared memory, and a communication protocol.
4. **Four collaboration patterns cover most real designs:** planner-executor (deterministic step-by-step), supervisor-worker (parallel specialists), critic-refiner (draft then verify), and peer-to-peer (no central orchestrator).
5. **The pattern choice should match the task** — deterministic workflows want planner-executor, high-stakes content wants critic-refiner, continuous background sync wants peer-to-peer.

---

## 🎤 Interview Prep — Mock Interview (Multi-Agent Systems)

*Same two-layer format as the other Video Notes files in this repo: a plain-language answer with an example, then a crisp, technically precise version.*

---

**🎙️ Interview Q1:** "When would you reach for a multi-agent system instead of just making one agent's prompt more sophisticated?"

**✅ Strong answer:** "When the task genuinely needs different *kinds* of competence, not just a smarter version of one competence. If a single agent is trying to retrieve data, reason over it, generate a report, *and* check that report for compliance, you're asking one model to be great at four different jobs at once — and if it gets any one of them wrong, there's nobody catching the mistake. Splitting that into a retrieval agent, a reasoning agent, a generation agent, and a compliance-checking agent means each one is only responsible for what it's actually good at, and the ones downstream can catch problems from the ones upstream. I'd reach for multi-agent specifically when reliability and parallel scaling matter, not just when a task has multiple steps — a single agent with a good planner-executor loop can already handle multi-step tasks."

**🎯 Standard Interview Answer:** "Multi-agent architectures are justified when a task requires functionally distinct competencies that benefit from independent specialization and cross-verification, or when parallel execution across tools/compute is needed for throughput. A single agent with a planning loop can still handle multi-step tasks; the deciding factor for going multi-agent is usually reliability (independent verification reduces single-point-of-failure error) and scalability (parallel execution across specialized components), not step count alone."

---

**🎙️ Interview Q2:** "What's the actual difference between the planner-executor pattern and the supervisor-worker pattern? They both sound like 'one agent tells others what to do.'"

**✅ Strong answer:** "The key difference is *what* gets delegated. In planner-executor, the planner produces a full sequence of steps up front, and the executor just carries them out one after another — it's linear and mostly deterministic. In supervisor-worker, the supervisor doesn't hand over a fixed sequence; it delegates whole *subtasks* to different specialized workers, who may each do several steps of their own internally, and the supervisor's real job is merging and verifying what comes back — which can happen in parallel, not just in sequence. Planner-executor is 'here's your checklist, go.' Supervisor-worker is 'here's your piece of the problem, use your judgment, report back.'"

**🎯 Standard Interview Answer:** "Planner-executor decomposes a task into an explicit, ordered sequence of steps executed largely linearly by a single executor role — closer to a deterministic workflow. Supervisor-worker decomposes a task into parallel subtasks routed to specialized worker agents, each with autonomy over their own internal execution, with the supervisor responsible for task assignment, conflict resolution, and result aggregation/verification rather than step-by-step sequencing. The former optimizes for determinism and debuggability; the latter optimizes for parallelism and specialization."

---

**🎙️ Interview Q3:** "Why would you ever choose a peer-to-peer, decentralized design over having a supervisor coordinate everything?"

**✅ Strong answer:** "Because a supervisor is a bottleneck and a single point of failure for every single interaction, even trivial ones. If a knowledge agent just needs to tell a memory agent 'update this fact,' routing that through a supervisor every time adds latency and complexity for no real benefit — there's no decision to make, no conflict to resolve. Peer-to-peer makes sense when agents need to sync state continuously or react to each other in the background, where waiting for a central coordinator on every exchange would make the system sluggish and heavier than it needs to be."

**🎯 Standard Interview Answer:** "Peer-to-peer coordination removes the central orchestrator as a mandatory hop for every inter-agent interaction, which reduces latency and coupling for high-frequency, low-ambiguity exchanges — cases where no arbitration or task decomposition is actually needed. It trades away the supervisor's global visibility and conflict-resolution guarantees in exchange for a lighter-weight, more reactive system, which is the right trade-off specifically for continuous state synchronization or autonomous background updates rather than for decisions that need central coordination."

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

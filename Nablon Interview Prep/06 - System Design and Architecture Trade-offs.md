# System Design & Architecture Trade-offs — Interview Questions

*This is where **Technical Round 2** is won — "Architecture, trade-offs, and depth. We test your ability to reason under constraints and defend your approach." The JD's hardest-trade-offs list is explicit: reliability, cost, latency, maintainability.*

*These are open-ended design prompts. The grading is on how you reason, decompose, and defend — not on a single right answer. Each has a **✅ How to structure the answer** and a **🎯 Senior signal**.*

---

**🎙️ Q1: "Design an agentic system to automate invoice-to-PO reconciliation for a Fortune 500 manufacturer, at 99.99%."**

**✅ How to structure the answer:**
"First I'd resolve ambiguity out loud — I'd ask about volume, the systems of record (SAP? Oracle?), what 'reconciled' means precisely, what actions are irreversible (releasing payment), and the regulatory context. Then:

1. **Clarify the reliability target as pass^k** — 99.99% consistent, so the design is about consistency and gating, not peak capability.
2. **Decompose and de-agentify** — extraction and matching where a rule works → deterministic; genuine ambiguity (fuzzy vendor names, partial matches, exceptions) → the agent. Most of this workflow is deterministic; the agent handles the exception tail.
3. **Ground in the ontology** — 'vendor,' 'PO,' 'approved-for-payment,' with the constraint that payment can't be released against a vendor on hold. The ontology is the safety interlock.
4. **Runtime** — durable orchestration with checkpoints, typed tools onto SAP/Snowflake, a verification gate before payment release.
5. **Escalation** — anything below confidence, over a value threshold, or flagging a policy constraint → human, durably paused.
6. **Eval + traces** — pass^k measured on real distribution, traces captured for audit and the compounding loop.
7. **Deployment** — in-firewall, local model on sensitive data, SOC 2 audit trail = the traces.

Then I'd state the headline trade-off: I'd rather escalate the ambiguous 3% than risk one wrong payment, because in finance a confident wrong action is far more costly than a human-reviewed exception."

**🎯 Senior signal:** "The move that separates L3 from L2 here is *leading with de-agentification and the pass^k framing* — showing you'd shrink the non-deterministic surface and gate the rest, rather than designing an impressive fully-autonomous agent. I'd close by naming what I'd measure to prove 99.99% and how I'd communicate the escalation-rate trade-off to the client's finance leadership — because at this bar, the architecture *and* the expectation-setting are the deliverable."

---

**🎙️ Q2: "Reliability, cost, latency, maintainability — you can't max all four. Walk me through how you actually trade them on a real engagement."**

**✅ How to structure the answer:**
"I'd anchor on the client's actual constraint, because the right trade is context-dependent:
- **Reliability is usually the fixed point** at Nablon — 99.99% is the contract, so I trade the other three to hold it.
- **Reliability vs latency:** more verification steps, more retries, escalation gates — all add latency. For a back-office reconciliation workflow, latency is cheap to spend; for a customer-facing agent, it isn't, so there I'd parallelise independent steps, cache the stable prefix, and route easy steps to faster/local models.
- **Reliability/latency vs cost:** the frontier model at high effort is most reliable but most expensive and slowest; routing routine steps to the local model and reserving frontier for the hard tail typically saves a large fraction with no quality loss. Reducing *steps* beats switching models.
- **Everything vs maintainability:** the seductive failure is a clever bespoke pipeline that hits the numbers and nobody can touch in six months. I weight maintainability heavily because L1/L2 engineers have to operate this, and the compounding loop only works if the system is legible.

The senior version of the answer is: I make the trade *explicitly and visibly*, quantify it, and get the client to own the call — because 'you're trading two seconds of latency for a 10x cost reduction, here's the number' is a decision they should make with me, not one I hide in the architecture."

**🎯 Senior signal:** "Naming *which* variable is fixed (usually reliability) and trading the rest against it — rather than pretending you can optimise all four — is the reasoning-under-constraint they're testing. And explicitly weighting maintainability is a senior tell: the person who owns the architecture *and* mentors the team knows the cleverest system that only they understand is a liability, not an achievement."

---

**🎙️ Q3: "How do you decide what should be an agent vs a deterministic workflow vs a plain function?"**

**✅ How to structure the answer:**
"By whether the step genuinely needs model judgment, because each rung up costs reliability:
- **Plain function** — deterministic logic, no ambiguity: validation, joins, rule-based routing. Reliability 1.0.
- **Deterministic workflow** — a fixed multi-step pipeline where the shape is known and each step is a function or a bounded model call. Predictable cost/latency, gateable.
- **Agent (model-decided control flow)** — only when the number and order of steps genuinely depends on the input and can't be known ahead: exception handling, open-ended research, multi-hop reasoning over ambiguous inputs.

The test I use: *can I draw the flowchart ahead of time?* If yes, it's a workflow, not an agent. Agency is a cost I pay for flexibility, justified only by irreducible input-dependent variability. At a 99.99% bar this discipline is a reliability strategy, not just simplicity — every step I move from agent to function multiplies my ceiling upward."

**🎯 Senior signal:** "Framing agency as a *cost paid for flexibility* rather than a default is the senior instinct — the reliability math (per-step reliability multiplies) makes minimising the agentic surface the highest-leverage architectural decision, and it's the opposite of where most engineers start. I'd add that this is also a maintainability and cost win, so it's rare that de-agentifying is the wrong call when a deterministic path exists."

---

**🎙️ Q4: "The client wants full autonomy. Your reliability analysis says you need a human in the loop. How do you resolve that?"**

**✅ How to structure the answer:**
"I treat it as an expectation-management problem backed by the numbers, not a technical argument to win:
1. **Show the pass^k math** — 'at the single-step reliability we can achieve, full autonomy across this workflow gives you X% consistent success; the failures are silent and land in production. Here's what one costs you.'
2. **Reframe the human gate** — it's not a failure of the system, it's the mechanism that makes the reliability bar *real*, and for decisions with legal effect (GDPR Art. 22) it may be legally required anyway.
3. **Show the trajectory** — the escalation rate isn't static; the compounding loop drives it down over time as the model learns from the very cases humans handle. 'We start with a human on 5%, and that shrinks as the flywheel turns.'
4. **Give them the decision with the trade quantified** — full autonomy at a lower reliability, or near-full autonomy at 99.99% with a shrinking human tail. Their call, my recommendation.

The role is as much relationship as code — winning this is about credibility and honesty, not being right in the abstract."

**🎯 Senior signal:** "This question is really testing the client-leadership dimension inside a technical wrapper. The senior answer refuses the false binary (full autonomy vs not), quantifies the trade, reframes escalation as the reliability *and* compliance mechanism, and hands the decision to the client with a clear recommendation — that's exactly 'manage expectations under pressure' and 'translate business stakes into technical strategy and back.' Being right silently loses; being right *credibly and collaboratively* wins the engagement."

---

**🎙️ Q5: "Design the observability and eval stack you'd stand up on day one of an engagement, before building any agents."**

**✅ How to structure the answer:**
"Day one, before agents, because you can't operate what you can't see and you can't retrofit signal you didn't capture:
1. **Trace schema first** — define the decision-trace structure (inputs, tool calls + args + results, model decisions + confidence + rejected alternatives, outcomes, escalations). Everything downstream — audit, eval, RL — reads from this, so it's designed before the happy path.
2. **Eval control plane skeleton** — the rubric structure, deterministic + judge + human tiers, and the CI gate wired in, even if the first rubrics are thin.
3. **Golden/calibration set seeding** — start collecting real examples and human labels immediately; the eval set is only as good as its grounding in reality.
4. **Monitoring** — nested-span tracing, cost, latency p95/p99, and drift monitors, with alerts wired to the gate.
5. **The judge-validation harness** — because an uncalibrated judge makes the whole gate meaningless.

Only then do I build agents *against* this scaffold, so from the first agent I have per-step attribution, a release gate, and the raw material for the compounding loop."

**🎯 Senior signal:** "Standing up observability and the eval gate *before* the agents is the inversion that marks seniority — juniors build the agent and add evals when it breaks; the architect builds the measurement and the gate first because 'quality built in, not bolted on' is only literally true if the gate predates the code. And designing the trace schema on day one reflects the hard-won lesson that you can't retro-fit signal — under-capture now is unattributable failures and a starved RL loop later."

---

**🎙️ Q6: "Walk me through how you'd decompose a vague, high-stakes problem a client hands you with no clear spec."**

**✅ How to structure the answer:**
"This is the core of the role, so I'd make my thinking visible:
1. **Understand the business stake first** — what outcome, what does success look like in their P&L, what's the cost of getting it wrong. Ambiguity in the *goal* is more dangerous than ambiguity in the tech.
2. **Find the bottleneck** — Nablon deploys 'at the most constraining bottleneck in the most critical workflow,' so I'd identify the single highest-leverage sub-problem rather than boiling the ocean.
3. **Identify the irreversibles and the regulated surfaces** — these set the reliability bar and the escalation design.
4. **Decompose into deterministic vs agentic**, sketch the ontology, name the systems to integrate, and the data/residency constraints.
5. **Define how I'll measure success** before building — the eval strategy is part of the spec, not an afterthought.
6. **Sequence for early, visible value** — get something real running in production in weeks (the JD's promise), starting at the bottleneck, then expand.

Throughout, I'd narrate assumptions and check them with the client, because resolving ambiguity *with* them is how you build the trust the role runs on."

**🎯 Senior signal:** "The signature FDE case-study round has the lowest pass rate and highest weight precisely because it tests this — and the failure mode is jumping to a solution before resolving the goal ambiguity. The senior pattern is: business stake → bottleneck → constraints (irreversible/regulated/residency) → decompose → *how I'll measure* → sequence for weeks-not-months value, all narrated with checked assumptions. They're watching how you think through a problem you've never seen, so thinking out loud and structuring the ambiguity *is* the answer."

---

## Sources
- [Toward Reliable Design of LLM-Enabled Agentic Workflows: Latency-Reliability-Cost Tradeoffs (arXiv)](https://arxiv.org/html/2605.23929v1)
- [How to Evaluate AI Agents: Reliability, Cost, Latency, and Failure Modes — DEV](https://dev.to/fernandoabishai/how-to-evaluate-ai-agents-reliability-cost-latency-and-failure-modes-2bb1)
- [The Complete Agentic AI System Design Interview Guide 2026 — Medium](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)
- [Forward Deployed Engineer Interview: The Definitive 2026 Guide — Exponent](https://www.tryexponent.com/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde)
- [How to Answer AI System Design Interview Questions — KDnuggets](https://www.kdnuggets.com/how-to-answer-ai-system-design-interview-questions)
- [State of AI Agents — LangChain](https://www.langchain.com/state-of-agent-engineering)

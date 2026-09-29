# ⚡ CHEAT SHEET — Skim This Before the Interview

*Everything in the 9 files, in plain words. Each concept = one simple line, then a short technical tag. Read top to bottom in ~10 minutes.*

---

## The role in one breath
You're the **technical architect + client face** for a whole Fortune 500 AI project. Half the job is building agentic systems that never fail; half is talking to their bosses and leading a small team. They do **not** want a coder who hides from clients, or a manager who stopped coding.

**Company:** Nablon builds **real production AI agents** (not demos) for big enterprises. OpenAI partner, Nexus-backed. Their magic phrase: **"each deployment compounds"** — the system gets smarter every time it runs.

---

## THE ONE THING TO NAIL: pass^k
- **pass@k** = succeeds **at least once** in k tries → measures *"can it ever do it?"*
- **pass^k** = succeeds on **every one** of k tries → measures *"is it reliable?"*
- Example: 70% success per run → pass@3 looks like 97%, but pass^3 = 0.7³ = **34%**. Same agent, opposite story.
- **Why it matters:** the JD says "pass^k reliability bar." Production users hit *every* run, so pass^k is the honest measure. 99.99% pass^k is impossible by prompting — you hit it by **removing AI steps and adding safety gates.**
- Most candidates will say pass@k. Say pass^k correctly and you sound senior instantly.

---

## THE BIG IDEA behind everything: determinism around non-determinism
You can't make an LLM reliable by itself (it's random). So you **wrap it in a deterministic cage**: fixed rules where possible, an ontology that blocks illegal actions, eval gates that stop bad output, and a human for the hard 3%. *"A deterministic scaffold around a non-deterministic core."* Say this and they'll nod.

---

## FILE 01 — Agent Architecture (the runtime)
- **Multi-agent runtime** = the system that runs your agents. Plain words: the "engine room."
- **Golden rule:** make as little as possible actually AI. Anything with fixed rules → plain code (100% reliable). Only use an agent when the steps genuinely depend on the input.
- **Orchestration** = deciding what runs next. Patterns: *sequential* (A→B→C, fixed), *supervisor/router* (a boss agent delegates), *event-driven* (things fire on events — best for big enterprise).
- **Checkpoint** = autosave after every step. Lets you resume after a crash, pause for a human, and keep an audit trail.
- **Durable execution** = the engine (Temporal / LangGraph) that does that autosaving. Non-negotiable here.
- **Escalation** = when unsure/risky, pause and hand to a human. Design it on purpose, not as an error handler.
- **Queues** = buffers between stages so a slow step doesn't crash everything.
- **Model routing** = sensitive data → local model (stays in-house); hard reasoning → OpenAI/Anthropic; easy stuff → cheapest.
- **Worst failure:** *silent confident wrong answer.* Catch it with verification gates + traces, never with "better prompt."

## FILE 02 — Reliability & Evals (MOST IMPORTANT)
- **Eval control plane** = the quality-control factory for AI output. Four parts:
  - **Rubric scoring** = a grading sheet (part exact checks, part AI-judge, part human).
  - **Tiered policy** = critical rules are hard blocks; minor quality has soft floors.
  - **Drift detection** = noticing when real traffic drifts away from what you tested.
  - **Production gating** = an automatic pass/fail that blocks a bad release. This is "quality built in, not bolted on."
- **Decision trace** = the full recorded story of one run (inputs, tool calls, decisions, outcome). Triple duty: **audit trail + eval cases + training data.**
- **How to test random systems:** run it many times (pass^k), grade against a golden set with an AI judge, check the *path* not just the answer, include failure cases.
- **LLM-as-judge caveat:** the judge is biased (favours first option ~60–65%, favours its own family, favours longer answers). Fix: swap order + require agreement + calibrate against human labels. An uncalibrated judge = a meaningless gate.
- **Getting 95%→99.99%:** measure where it fails → turn fixable steps into code → add verification gates → send the last hard 1% to a human. Be honest: full autonomy at 99.99% doesn't exist.

## FILE 03 — Reinforcement Learning & the Compounding Loop
- **Compounding loop** = runs → traces → eval cases + training data → better local model → better runs. The flywheel. Nablon's whole pitch.
- **GRPO** = the training method for their local model. Plain words: generate several answers, keep the ones better than the group average, no separate "critic" model needed → cheaper, runs inside the client's firewall. Best when rewards are **verifiable** (passed the test? matched the record?).
  - vs **PPO** (needs a critic model, heavier), vs **DPO** (learns from preference pairs, offline).
- **Reward design** = defining "good." Use verifiable outcomes. Danger: **reward hacking** — the model games a sloppy reward (e.g. "shorter = better" → it pads). Ground rewards in real outcomes + policy penalties.
- **Workflow simulator** = a safe fake copy of the client's systems so the agent can practise thousands of times without touching real SAP.
- **Offline → shadow → production:** train offline → run live but **don't execute** (shadow, watch what it *would* do) → only then go live. Because offline scores always look better than reality.
- **When NOT to use RL:** if prompting/SFT already works, or you have no verifiable reward. RL is for high-volume, verifiable, in-house workflows only.

## FILE 04 — Ontology (OWL 2 DL)
- **Ontology** = a formal rulebook of the business: what things are, how they relate, what's allowed. Plain words: the *grammar* of the domain (the knowledge graph is the *facts*; the ontology is the *rules*).
- **Why:** an agent without it can find facts but can't enforce rules → hallucination. With it, the agent literally *can't* assert something illegal. One study: hallucination 63% → 1.7%.
- **OWL 2 DL** = the standard language for this. "DL" = Description Logic = expressive **but guaranteed to finish** (decidable), so a reasoner can check consistency reliably.
- **Reasoner** = software that checks the rules and catches contradictions before an action happens.
- **Killer example:** agent about to pay a vendor, but vendor is "on hold." Rules say "paid" and "on-hold" can't both be true → reasoner **blocks it**. The LLM alone would've paid.
- **This is "neurosymbolic":** LLM handles language/ambiguity; ontology handles rules that must never break.
- **Building it** = a client conversation — you extract their tacit rules and formalise them (finding contradictions in their own policy is often the first "wow").

## FILE 05 — Data & Deployment (SOC 2 / GDPR)
- **Inside the firewall** = the AI runs inside the client's own cloud; data never leaves. So: **bring the AI to the data**, not data to the AI.
- **Why the local model exists:** so sensitive data never goes to OpenAI. Rule order: **residency first, then capability, then cost.**
- **Integrating SAP / Oracle / Databricks / Snowflake:** hide each behind clean "typed tools" so agents don't learn 4 systems' quirks. SAP/Oracle = system of record (write carefully); Databricks/Snowflake = the data lake (analyse here). Ontology reconciles their different names for the same thing.
- **MCP** = a standard plug so agents call data services without custom code (Snowflake/Databricks support it in 2026). Treat external MCP servers as untrusted.
- **SOC 2** = security/audit standard → everything logged and access-controlled (traces = your audit evidence).
- **GDPR** = EU data law → data stays in-region + **right to human review of automated decisions** (Article 22) — which is *the same human-in-the-loop* you built for reliability. One design, two wins.

## FILE 06 — System Design & Trade-offs (Technical Round 2)
- **They grade HOW you think, not the final answer.** Think out loud.
- **The 4 trade-offs:** reliability, cost, latency, maintainability — you can't max all. Usually **reliability is fixed** (it's the contract); trade the other 3 against it.
- **Design recipe for any prompt:** clarify ambiguity out loud → state assumptions → find the bottleneck → split deterministic vs agentic → ground in ontology → add verification + escalation → say how you'll measure success → name your trade-offs → sequence for value in weeks.
- **Agent vs workflow vs function:** *Can I draw the flowchart in advance?* Yes → workflow/function. No → agent. Agency is a cost you pay for flexibility.
- **"Client wants full autonomy but you need a human":** show the pass^k math, reframe the human as the thing that makes 99.99% *and* GDPR real, show escalation shrinks over time, give them the decision with numbers.
- **Weight maintainability:** the clever system only you understand is a liability — you're hired to set standards others maintain.

## FILE 07 — Client Leadership & Behavioral (HALF the job)
- Use **STAR**: Situation, Task, Action, Result. Prepare **6–8 real stories.**
- Must have ready: (1) owned an **ambiguous call end-to-end**, (2) a **hard client conversation**, (3) a **failure you owned** + systemic fix, (4) **mentoring** that outlasted you, (5) a **decision under pressure** with incomplete info.
- **Hard conversation win:** hold the technical truth *and* keep trust — "here's the constraint, here are options with trade-offs, here's my pick, your call." Not caving, not steamrolling.
- **Disagree with a founder:** understand → make the case with data → if overruled, **commit fully.** (disagree-and-commit)
- **Why Nablon:** production not pilots, the compounding loop, real ownership, and you *want* the client-facing ambiguity (not tolerate it).
- **Failure mode to avoid:** being an IC who lights up on architecture but goes quiet on clients. This role is half relationship.

## FILE 08 — Take-Home & Case Study
- They test **how you think, structure, deliver** — not feature count. A clean, honest 70% beats a sprawling 100% with no evals.
- **Always:** (1) restate the problem + **list your assumptions**, (2) name trade-offs on every choice, (3) treat it as a **production system** (evals, failure modes, verification) not a demo, (4) focus on the **bottleneck**, (5) keep it **readable**, (6) state limitations + next steps.
- **Biggest trap:** charging in without clarifying. Always frame + assume first.
- **Live case round:** clarify relentlessly → find bottleneck → decompose out loud → say how you'd measure → make the trade-off call → sequence for weeks-not-months. Silence is worse than imperfect thinking-aloud.

---

## The 5 sentences to have on the tip of your tongue
1. *"99.99% is a **pass^k** bar — consistent success every run — so I minimise the agentic surface and gate the rest, rather than chase a better prompt."*
2. *"I engineer a **deterministic scaffold around a non-deterministic core** — ontology constraints, eval gates, verification, escalation."*
3. *"The **ontology** is the safety interlock — the LLM handles language, the ontology enforces rules that must never break."*
4. *"The **compounding loop** turns production traces into eval cases and RL training, so the local model gets better at *this* client's workflow over time."*
5. *"For a 99.99% bar I'd rather **escalate the ambiguous 3% to a human** than risk one confident wrong action — and I'd give client leadership that trade-off with the numbers."*

**Breathe. You know this. Think out loud, name trade-offs, and lead the room.**

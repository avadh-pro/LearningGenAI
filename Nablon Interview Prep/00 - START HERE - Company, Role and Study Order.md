# Nablon — AI Engineer II (L3, Forward-Deployed) — Interview Prep

> ⏱️ **Short on time? Open `CHEAT SHEET - Skim Before Interview.md` first** — every concept in these files, in plain words, skimmable in ~10 minutes. Come back here for the study order and detail.

*Built from the actual JD (`Nablon_JD_L3_AI_Engineer_II.docx`) plus extensive 2026 web research on every stack term the JD names. Calibrated to a **senior, forward-deployed L3** bar — this is not a recall test, it's judgment, architecture, and client leadership under real constraint.*

---

## What this role actually is

Read the JD twice and the shape is unmistakable: **this is a forward-deployed solutions-architect role wearing an AI-engineering stack.** You own (a) the *technical architecture* of a whole Fortune 500 engagement, (b) the *reliability strategy* that gets a non-deterministic system to 99.99%, and (c) the *client-leadership relationship* with senior stakeholders. Roughly half the signal they hire on is not code — it's how you decompose ambiguity, defend trade-offs, and hold a room.

The "not a fit" paragraph is the sharpest tell:
- ❌ Pure IC who wants to go heads-down and avoid clients → rejected
- ❌ Generalist manager who has drifted from hands-on → rejected
- ✅ **Someone who still owns the architecture, still ships, *and* can be the technical face to the C-suite.**

## The company, in one paragraph (say this back to them)

Nablon builds **production-grade agentic AI** for Fortune 500s (CPG, banking, MedTech, industrial) — not services, not PoCs, not slideware. It's an **OpenAI partner**, backed by **Nexus Venture Partners**, partnered with Databricks, NVIDIA, Snowflake and Microsoft. The differentiator they repeat everywhere is **the closed loop**: ontology → agents → decision traces → evals → RL environments → better agents, so each deployment *compounds*. If you take one framing into every round, take that one — **"quality is built in, not bolted on."**

## The stack they name (and where each lives in this folder)

| JD stack pillar | What it means | File |
|---|---|---|
| Agent architecture | Multi-agent runtime: orchestration, queues, checkpoints, escalation | `01` |
| Eval control plane | Rubric scoring, tiered policy enforcement, drift detection, production gating to **pass^k** | `02` |
| RL & the compounding loop | Traces → eval cases → RL envs; reward design, simulators, offline→shadow rollout, **GRPO** | `03` |
| Ontology & domain modelling | **OWL 2 DL** — entities, constraints, KPIs, policy every agent reasons over | `04` |
| Data & platform | SAP/Oracle/Databricks/Snowflake, in-firewall on Azure/AWS, **SOC 2 / GDPR** | `05` |
| The hardest trade-offs | Reliability / cost / latency / maintainability under constraint | `06` |
| Client leadership | Stakeholder management, ambiguity, mentoring L1/L2 | `07` |
| Take-home + case study | The signature ambiguous-scoping round | `08` |

## The six-stage process (from the JD) and what each tests

| # | Stage | What they're really testing | Prep with |
|---|---|---|---|
| 1 | Profile screening | Your story, role expectations | `00`, `07` |
| 2 | Take-home assignment | *"How you think, structure, deliver"* — real work, no tricks | `08` |
| 3 | Technical Round 1 | Core technical depth via real scenarios | `01`–`05` |
| 4 | Technical Round 2 | **Architecture, trade-offs, reasoning under constraint** | `06`, `02` |
| 5 | Final & Founder round | Vision, culture, judgment, long-term | `07`, `00` |
| 6 | Offer | — | — |

## Study order

**If you have a week:** `00` → `01` → `02` → `06` → `03` → `04` → `05` → `07` → `08`.

**Why that order:** `01` and `02` are the spine — agent architecture and the reliability/eval bar are what the whole role rotates around, and they anchor every other answer. `06` (system design) is where Technical Round 2 is won and pulls from `01`/`02`. `03`/`04`/`05` are the specialist depth that separates you from a generalist. `07` is load-bearing for *half* the process — do not treat it as soft.

**If you have two days:** `00` → `02` → `06` → `07`. The reliability bar, the architecture round, and the client-leadership signal. Accept you'll be thinner on RL and ontology.

## The four things that will actually differentiate you

1. **pass^k, not pass@k.** The JD literally says "pass^k reliability bar." Most candidates will talk pass@k. Knowing *why* 99.99% means pass^k — consistent success on every attempt, not success on at least one — is the single highest-signal thing in this whole pack. (`02`)
2. **The compounding loop as a system, not a buzzword.** Be able to draw traces → eval cases → RL env → shadow → production, and say what breaks at each hop. (`03`)
3. **Determinism *around* non-determinism.** The senior insight interviewers want: you can't make an LLM deterministic, so you engineer a deterministic scaffold — ontology constraints, eval gates, verification, escalation — around a non-deterministic core. (`02`, `04`, `06`)
4. **You lead the room.** Every technical answer should carry a sentence of "…and here's how I'd communicate that trade-off to the client's engineering VP." That's the role. (`07`)

## How to use every answer file

Two layers per question, deliberately:
- **✅ Strong answer** — what you'd actually say out loud. Plain, structured, with a concrete example or number.
- **🎯 Senior signal** — the compressed, precise version plus the trade-off or failure mode that marks you as L3, not L2.

Where a question carries a ⚠️, that's a trap or a place candidates routinely say something now-outdated. Answer out loud before reading — recognising an answer and producing one are different skills, and this loop is decided on production.

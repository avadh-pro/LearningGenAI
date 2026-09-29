# Take-Home Assignment & Case Study — Prep

*JD stage 2: "A short, focused exercise that reflects real work. No trick questions — we want to see how you think, structure, and deliver." Plus the signature FDE case-study round (Technical Round 1/2), which across the industry has the lowest pass rate and highest weight of any stage.*

*You can't know the exact prompt, so this file preps the **approach** — what a strong deliverable looks like and the traps that sink candidates.*

---

## What the take-home is really testing

The JD tells you: **"how you think, structure, and deliver."** Not whether you can produce the most features. For a forward-deployed L3 the graders are reading for:

1. **Problem framing** — did you resolve the ambiguity and state your assumptions, or did you charge at the first interpretation?
2. **Architecture & trade-offs** — did you make deliberate, defended choices, and name what you traded away?
3. **Reliability thinking** — did you treat it as a production system (evals, failure modes, verification) or a demo?
4. **Communication** — is the deliverable *legible*? Could a client's engineering VP follow your reasoning?
5. **Judgment on scope** — did you do the *right* amount, focused on the bottleneck, rather than gold-plating the easy part?

A polished, honest, well-reasoned 70%-scope solution beats a sprawling 100%-scope one with no evaluation and no stated assumptions. Every time.

---

## The structure that wins (whatever the prompt)

Whether it's a doc, a repo, or both, lead with reasoning:

**1. Problem restatement & assumptions (do not skip this).**
"Here's how I read the problem, here's what was ambiguous, here are the assumptions I made and why." This single section is where forward-deployed candidates separate themselves — it shows you resolve ambiguity instead of guessing silently.

**2. Approach & architecture, with trade-offs named.**
The design, and for each significant choice: what you picked, the alternatives, and why — including what you gave up. "I used X over Y because reliability mattered more than latency here; the cost is …"

**3. The build.**
Clean, legible, production-shaped code or design. Not the most features — the *right* ones, done well. Structure and readability over cleverness.

**4. Evaluation / how you'd know it works.**
Even if lightweight: how you'd measure success, the failure modes you anticipated, how you'd verify reliability. For an agentic prompt, this is where pass^k / eval-gate thinking earns real points. Most candidates omit this; including it reads as senior.

**5. What I'd do next / limitations.**
Honest boundaries: what you didn't build and why, what would need to change for production scale, what the next iteration is. Confidence *and* honesty.

---

## If it's an agentic-build take-home

Bring the whole role's thinking, scaled down:
- **De-agentify** what's deterministic; reserve the agent for genuine ambiguity. Say so explicitly.
- **Ground it** — even a small ontology/schema or typed constraints beats free-form prompting, and shows you know why.
- **Verification & escalation** — a gate before any consequential action, and a low-confidence path. Even stubbed, it signals reliability thinking.
- **Traces & eval** — capture what happened; sketch the eval rubric even if you only run a few cases.
- **A trade-offs section** — reliability/cost/latency/maintainability, with your call and reasoning.

The single differentiator: **treat it as a production system with a reliability bar, not a demo that works once.** That's the entire ethos of the company.

---

## The live case-study round (Technical Rounds)

A vague problem, ~45–60 minutes, thinking out loud. They are **not grading your final answer — they're watching how you think through a problem you've never seen.** The winning pattern (also in `06` Q6):

1. **Clarify relentlessly first** — business stake, success definition, volume, systems, constraints, what's irreversible/regulated. Ambiguity in the *goal* is the dangerous kind.
2. **Find the bottleneck** — Nablon deploys at the single most-constraining point; solve that, don't boil the ocean.
3. **Decompose out loud** — deterministic vs agentic, the ontology, the integrations, the data/residency constraints.
4. **State how you'd measure success** before designing the solution.
5. **Name trade-offs and make the call**, then say how you'd communicate it to client leadership.
6. **Sequence for early value** — production in weeks, at the bottleneck, then expand.

Narrate assumptions and check them. Silence while you think is worse than thinking aloud imperfectly.

---

## Traps that sink candidates

- ❌ **Charging in without clarifying** — the single most common failure in FDE case rounds. Always frame and assume first.
- ❌ **A demo, not a system** — no evals, no failure modes, no verification. Fatal at a reliability-obsessed company.
- ❌ **Gold-plating the easy 80%** and ignoring the hard bottleneck — wrong scope judgment.
- ❌ **Unstated assumptions** — makes you look like you missed the ambiguity rather than resolved it.
- ❌ **Cleverness over legibility** — if the grader (or a future L1) can't follow it, it's a liability; you're being hired partly to set standards others maintain.
- ❌ **Over-claiming** — "fully autonomous, 100% reliable." The senior move is honest limits and a shrinking-escalation trajectory.
- ❌ **No trade-off reasoning** — presenting one design as obviously correct signals you didn't consider alternatives.

---

## The 60-second self-check before you submit

- [ ] Did I **restate the problem and list my assumptions** up front?
- [ ] Did I **name trade-offs** on every significant choice, including what I gave up?
- [ ] Did I treat it as a **production system** — evals, failure modes, verification — not a demo?
- [ ] Did I focus on the **bottleneck / right scope**, not the easy bulk?
- [ ] Is it **legible** — could a client's engineering VP follow my reasoning?
- [ ] Did I state **limitations and next steps** honestly?
- [ ] Does it reflect the **reliability-first, quality-built-in** ethos in some concrete way?

## Sources
- [Forward Deployed Engineer Interview: The Definitive 2026 Guide — Exponent](https://www.tryexponent.com/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde)
- [Forward Deployed Engineer Interview Questions Guide — FDE Academy](https://fde.academy/blog/forward-deployed-engineer-interview-questions)
- [Forward Deployed Engineer Interview Prep (2026) — DataInterview](https://www.datainterview.com/blog/forward-deployed-engineer-interview-prep)
- [How to Answer AI System Design Interview Questions — KDnuggets](https://www.kdnuggets.com/how-to-answer-ai-system-design-interview-questions)
- [The Complete Agentic AI System Design Interview Guide 2026 — Medium](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf)

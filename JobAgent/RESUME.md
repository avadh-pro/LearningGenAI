# JobAgent — where we stopped

**Paused:** 2026-09-14 · **Branch:** `JobAgent` · **Last commit before this note:** `bd4880c`

---

## Done

| Artefact | State |
| --- | --- |
| `knowledge-base/` | 104 pages of official LangChain 1.x + LangGraph docs, crawled and indexed |
| `resume/` | ATS-optimised master (HTML) + renderer. Score 71 → **96/100** |
| `docs/REQUIREMENTS.md` | **v0.5**, approved for spec |
| `docs/requirements-analysis.md` | 84 requirements, 37 gaps (11 critical), 24-item assumption register |
| `docs/test-plan.md` | 277 acceptance criteria, written before any design |
| `docs/ui-ux-design.md` | 19 screens, FR→UI map |
| `docs/SPEC.md` | **1,738 lines** — 17 components, 60 tasks, 8 phases |

## Not done

**Phase 4 — adversarial review of `SPEC.md`.** Stopped mid-run at the user's request; it had
written nothing. **The spec has not been independently reviewed.** It should not be implemented
from until that runs.

---

## To resume

Relaunch the review. It reads only from this branch, so nothing from the paused session is
needed. Then implementation: 60 tasks, 8 phases, Sonnet + Opus.

### Findings from a partial-review helper that completed before the stop

Treat as **unverified leads**, not conclusions:

1. ⚠️ **Checked and FALSE alarm.** It claimed `SPEC.md` never covers the submission crash window
   (gap G-C3). The spec contains `UNKNOWN_OUTCOME` ×20, `SUBMITTING` ×24, `PreClickError` ×10 and
   locking ×65. It cites the *mechanism* without citing the *gap ID* — a traceability nit, not a
   safety hole. **Do not let a re-run repeat this alarm.**
2. **Worth checking:** 7 of the 10 internal inconsistencies the analysis found in the requirements
   are still open. Three were fixed in v0.5 (daily target, the FR-6.1 numbering collision,
   FR-4.1's self-contradiction). The rest are listed in `requirements-analysis.md` §2.
3. **Worth checking:** the analysis (§4) explicitly forbids assuming a multi-agent architecture —
   "not requested", per LangChain gotcha 14. `SPEC.md` mentions multi-agent once; confirm it is a
   "not used" note rather than an architectural escalation.
4. **Worth checking:** the analysis (§5.11) permits `HumanInTheLoopMiddleware` **only** on the
   `submit_application` tool call with `allowed_decisions: ["approve","reject"]`, and requires the
   raw `interrupt()` primitive for HITL-2/3/4/5. Confirm the spec honours that split.
5. **Known bookkeeping gap:** the run lock, per-thread lock and `(job_identity)` uniqueness
   constraint (gap G-C4) never made it into the assumption register, so they have no traceable
   hook even though the spec implements locking.

---

## Blocking the user, not the work

| # | Needed | Consequence if unanswered |
| --- | --- | --- |
| **1** | **A seed list of 30–50 target companies** with career-page / ATS URLs | **The hard blocker.** Greenhouse/Lever/Workday are ATS platforms, not searchable boards. Submission is only permitted there. Without this list, the sources where applying is legal return nothing on day one. |
| **2** | `years_by_technology` table, or confirm HITL-3 each time | FR-8.1 asks for per-technology years the resume does not contain. Left alone this is the most likely way the system tells a lie a recruiter can check. |
| **3** | Work authorisation (O-2) — any EU / Canada / UAE permit? | Currently defaults to *sponsorship required*, which rejects rather than wastes. Confirming it is the single change that most widens the international pool. |
| **4** | Confirm Workday ships **assisted** in v1 | Otherwise it is the largest engineering sink in the project. |

Twelve consolidated questions (Q-A … Q-L) with assumed defaults are in
`requirements-analysis.md` §6. **None has a ratified answer** — the spec stands on defaults for
all of them. Answering Q-A … Q-L is the cheapest possible way to de-risk the build.

### Also outstanding, outside the system

- Set a LinkedIn vanity URL (`linkedin.com/in/avadhdobariya`) — the current one is long enough to
  wrap and break in some contexts. Only the user can do this.

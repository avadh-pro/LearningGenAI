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

### Findings from a second helper — UI design vs spec audit

**All four were re-checked against `SPEC.md` directly and hold up.** Unlike the finding above,
these are confirmed, not leads. They are review material, not defects the spec author agreed to.

1. 🔴 **An irreversible submission can proceed without verifying the posting is still live.**
   The UI's pre-flight *partial* state (ui-ux-design §4) says: if the *job still active* check
   cannot reach the posting, the row goes **amber, not red, and Approve is allowed**. That is the
   one documented path where an application is sent under Avadh's name without confirming the job
   still exists. The spec never reproduces the amber semantics at all (0 hits for "couldn't
   verify"), so the behaviour is currently undefined rather than decided. **Needs an explicit
   ruling: amber-and-allow, or red-and-block.**

2. 🔴 **`approved_without_review` is a real decision type in the spec** (3 occurrences), reachable
   via a Telegram `/approve` command behind an off-by-default flag. The UI ruled this out by name
   — approving from a phone has neither the diff nor the evidence trace, which is precisely the
   spot-checking Q-2 rejected. The spec keeps the letter of "no bulk approve" while creating a
   serial equivalent. **Decide whether that command exists at all.**

3. 🟠 **"The ceiling is never drawn as a progress bar" was dropped** (0 hits in the spec). It is a
   deliberate UI rule: a bar to 15 with 11 filled reads as "4 short", which nudges toward padding
   and contradicts FR-9.2's ceiling-not-quota.

4. 🟠 **Bulk actions have keybindings but no API.** The UI permits bulk reject / skip / dismiss-
   expired / re-tailor / retry-sources, each with its own guard — bulk reject must confirm with the
   company list, and bulk "mark applied manually" is explicitly forbidden. The spec exposes only
   single-resource endpoints and nowhere carries those guards.

5. 🟡 **The FR → UI map lost resolution.** The UI gave every requirement its own home; the spec
   collapses 22 rows into 5 aggregates (`HITL-R1..R5` → one row, `T-1..T-5` → one row, most TRs →
   one row). FR-13.2 is a testable assertion *about the spec document itself* — "any FR without a
   UI component is incomplete" — so this weakens the very artefact that requirement demands.

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

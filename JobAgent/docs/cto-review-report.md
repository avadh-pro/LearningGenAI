# CTO Review — JobAgent Technical Specification v1.0

**Artefact:** `docs/SPEC.md`, 2077 lines, dated 2026-09-14
**Reviewed against:** `docs/REQUIREMENTS.md` v0.5 · `docs/requirements-analysis.md` · `docs/test-plan.md` (277 AC) · `docs/ui-ux-design.md` · `kb/` (15 LangChain 1.x / LangGraph pages)
**Reviewer posture:** adversarial. Nothing below is praise, and nothing below is manufactured.

---

## Verdict

**REJECTED.**

This is a well-organised document written by someone who understood the problem. That is exactly
why it is dangerous to approve: it *reads* as though the irreversible parts are solved, and the
sections that carry the safety argument (§9, §8, §12.5) are written with more confidence than the
mechanisms deserve. Three findings alone are disqualifying:

1. **The irreversible action is not confined to the `submit` node.** §9's entire argument rests on
   "one click, in one node, behind one gate". Multi-page ATS forms are advanced by POST inside
   `fill_form`, and the spec explicitly asserts `fill_form` performs "no POST". The protocol
   protects a click that is not the only irreversible act.
2. **The one sanctioned path back to a second click — `confirmed_not_submitted` — has less friction
   than editing a cover letter sentence**, and the spec creates several ways to enter
   `UNKNOWN_OUTCOME` while the first submission is still in flight or has already landed.
3. **§18, the verification table the whole document leans on, contains three false entries.** All
   three are marked `[UNVERIFIED]` in the body; all three are answered in the supplied knowledge
   base, one of them in a section titled *Behavior with `interrupt()`*. TR-2 ("All LangChain/LangGraph
   APIs must be verified against `knowledge-base/`") is the requirement the spec most loudly claims
   to honour, and it is the requirement it breaks.

Counts: **10 CRITICAL · 24 MAJOR · 12 MINOR.**

A second, narrower point: the plan is 115–190 implementer-days for one person — six to nine months
elapsed — and it sequences the question "is there anything on these sources to apply to?"
(T-4.2, blocker Q-B) into month four. For a system whose purpose is to get its owner a job, that
ordering is backwards on the only axis that matters.

### Correction to the prior review pass

`PRIOR-FINDINGS.md` records as *confirmed* that "the spec never reproduces the amber semantics at
all (0 hits for 'couldn't verify')". That is wrong. §9.4's closing paragraph does reproduce them,
verbatim in effect:

> "Check 3 that *cannot reach* the posting (network) is recorded `unverified` and shown amber;
> approval is still allowed with the warning (UI §4 pre-flight partial state) — but a definite
> closed marker is a hard fail."

The behaviour is not undefined. It is **decided, and decided the dangerous way**, and the spec's
version is incoherent in a way the UI's was not (see **C-4**). The first half of the prior
finding — that this is the documented path where an application is sent without confirming the job
exists — stands and is escalated here.

---

## Traceability matrix

Method: every `FR-*`, `HITL-*`, `T-*`, `TR-*`, `NFR-*`, `C-*` id from REQUIREMENTS v0.5 was counted
in SPEC.md and located; every AC group was cross-read against the section that claims to satisfy it.

### Coverage by family

| Family | In REQ | Designed in a spec section | Only in the §14.4 map | Not traceable | Test group |
| --- | --- | --- | --- | --- | --- |
| FR-1.x (discovery) | 9 | 9 | — | — | DS, DD, HR |
| FR-2.x (dedup) | 3 | 1 (§4.3) | FR-2.2, FR-2.3 | — | DD |
| FR-3.x (scoring) | 4 | 2 (§4.6) | FR-3.2, FR-3.3 | — | SC |
| FR-4.x (hard reject) | 4 | 3 (§4.5) | FR-4.3 | — | HR, AF |
| FR-5.x (fraud/secrets) | 2 | 2 (§4.5, §12.1) | — | — | FD |
| FR-6.x (tailoring) | 4 | 4 (§10, §4.9) | — | — | RT |
| FR-7.x / FR-8.x | 5 | 5 (§4.10, §11) | — | — | CL, AF |
| FR-9.x (submission) | 4 | 3 (§9) | FR-9.3, FR-9.4 | — | SB, HL |
| FR-10.x / FR-11.x / FR-12.x | 5 | 4 | FR-10.2, FR-12.2 | — | TK |
| FR-13.x (visibility) | 3 | 1 (§14.4) | 13.2, 13.3 (collapsed) | — | UI |
| HITL-1..6 | 6 | 5 (§5.3 nodes) | HITL-6 | — | HL |
| HITL-R1..R5 | 5 | 0 individually | **all five, one row** | — | HL, ID |
| T-1..T-5 | 5 | 5 (§8) | **all five, one row** | — | AF |
| TR-1..TR-12 | 12 | 8 | TR-3..TR-8/10-12 collapsed | TR-4, TR-5 never named | NF |
| NFR-1..NFR-7 | 7 | 5 | **all seven, one row** | — | NF, FM |
| C-1..C-6 | 6 | 4 | C-1/C-2/C-3/C-5 one row | C-4 (resolved in REQ) | SB, NF |

**Ids appearing exactly once in 2077 lines** — i.e. their only trace is the §14.4 aggregate row:
`C-5, FR-10.2, FR-12.2, FR-13.2, FR-2.2, FR-2.3, FR-3.2, FR-3.3, FR-4.3, FR-6.2, FR-6.3, FR-8.3,
FR-9.3, FR-9.4, HITL-6, HITL-R1, HITL-R3, HITL-R5, NFR-1, NFR-2, TR-3, TR-8` (22 ids).

**Ids appearing zero times:** `C-4` (legitimately — resolved in REQ v0.3), `FR-13.3`, `HITL-R4`,
`TR-4`, `TR-5` (the last four are swallowed by the range notations `FR-13.1 / 13.2 / 13.3`,
`HITL-R1..R5`, `TR-3..TR-8`).

That **NFR-2 ("no duplicate submission") and HITL-R5 ("resuming must never re-execute a side
effect") each appear exactly once outside §1's summary table** is the finding worth keeping. The
two requirements the whole system exists to satisfy have no dedicated traceability line into §9 —
§9 argues the mechanism beautifully and never says which requirement it discharges. This is the
already-settled aggregation defect (prior finding #5), and the reason it matters is precisely this:
the aggregation hides that the two most important requirements are argued, not traced.

### Test coverage reachability

| AC group | Count | Satisfiable by this architecture | Blocked |
| --- | --- | --- | --- |
| AF (anti-fabrication) | 23 | 20 | AC-AF-08 (**C-8**), AC-AF-22 (**M-15**), AC-AF-19 partially (**M-16**) |
| ID (idempotency) | 25 | 22 | AC-ID-16 (**M-9a**), AC-ID-25 (**M-9**), AC-ID-08 partially (**C-10**) |
| SB (submission) | 20 | 18 | AC-SB-01 (**M-10**), AC-SB-15 partially (**C-1**) |
| HL (human-in-loop) | 27 | 23 | AC-HL-13 (**M-11**), AC-HL-17 (**M-12**), AC-HL-24 (**m-2**), AC-HL-26 (**M-13**) |
| NF (non-functional) | 19 | 16 | AC-NF-04 (**M-14**), AC-NF-09 (**M-23**), AC-NF-17 (**m-8**) |
| FM (failure modes) | 19 | 18 | AC-FM-18 (**M-7**) |
| DD, DS, HR, SC, RT, CL, TK, UI, FD | 125 | 125 | — |

**14 of 277 acceptance criteria cannot be satisfied by the design as specified.** Nine of the
fourteen are in the two groups (AF, ID) that the test plan's §17 names as the gate for enabling real
submission, "no exceptions, no waivers".

---

# Area A — Double submission

§9 makes a three-layer argument: a tracker gate at the top of `submit`, a `retry_on` restricted to
`PreClickError`, and startup reconciliation. Each layer is correctly reasoned **for the click inside
`submit`**. The findings below are paths where either the irreversible act happens somewhere else,
or the system manufactures the one condition (`UNKNOWN_OUTCOME`) from which a second click is
sanctioned.

I confirmed the layers that do hold, so the criticism is calibrated. The `PREFLIGHT_OK → SUBMITTING`
conditional `UPDATE` genuinely serialises two racing executions: the loser raises `IllegalTransition`
at step (3), outside the `try`, is not a `PreClickError`, and reaches `submit_error_handler`, which
never routes back into `submit`. Gate (1) genuinely catches the crash-between-click-and-record case.
§9.2's deliberate omission of `UNKNOWN_OUTCOME → SUBMITTING` and `SUBMITTING → SUBMITTING` is correct
and should survive any rewrite. The problem is not the protocol. The problem is everything the
protocol does not cover.

---

### C-1 · CRITICAL · `fill_form` performs irreversible POSTs outside the submission protocol

**Where:** §5.3 node table (`fill_form`: "browser only, **no POST**"); §4.11 (`FormModel.fields`
carries `page_index`); §13.6 row FM-05 ("Network lost mid fill → ... no POST"); §9.1–§9.3.

**Why it is wrong.** `page_index` in the `FormModel` is an admission that ATS forms are multi-page.
A multi-page form is advanced by submitting the current page — an HTTP POST. On Greenhouse's
multi-step flows, on Workday, and on a large share of career-page ATSs, that intermediate POST
creates a server-side record: a draft, a partial application, or in several tenants an application
the employer can already see. The whole of §9 rests on the premise that exactly one act is
irreversible and that it lives in `submit` behind a durable `SUBMITTING` row. That premise is false
the moment `fill_form` advances a page.

It is made worse by two details. `fill_form` inherits the graph-wide default
`RetryPolicy(max_attempts=3)` (§5.1), so a page-advancing POST can be re-issued up to three times per
node attempt. And `fill_form` is re-entered from `await_blocker`, and LangGraph restarts a node from
its first line on resume (`kb/lg-interrupts.md`, "Rules of interrupts"), so every blocker resume
replays every page advance. None of these POSTs writes `SUBMITTING`, captures evidence, or can reach
`UNKNOWN_OUTCOME`.

**Required change.**
1. Extend §9.2 with a `FILLING` status and a durable per-page `page_committed` marker written
   *before* each navigation POST, mirroring §9.3 step (3) exactly.
2. Give `fill_form` `retry_policy=RetryPolicy(max_attempts=1)` and a `fill_error_handler` that may
   never re-enter a page the tracker records as committed.
3. Delete the "no POST" claim from §5.3 and §13.6 and replace it with the real invariant: *no POST
   to a page the tracker records as already committed.*
4. Make the fake ATS in T-2.5 a multi-page form with a per-page POST counter, and extend AC-ID-23's
   200-run fuzz to kill between pages, asserting every per-page counter ≤ 1.

---

### C-2 · CRITICAL · HITL-2 offers no "I already submitted it", and `continue` re-runs `fill_form` from the top

**Where:** §5.3 (`fill_form ──(blocker)──▶ notify_blocked ─▶ [await_blocker] ─▶ fill_form`); §4.12
(the worker "leaves the page open" and the dashboard offers *Take over browser*); §7.1 Needs-you-now
(`POST /applications/{id}/blocker {action: continue|by_hand|abandon}`); §9.4.

**Why it is wrong.** The design hands a human a live, mostly-filled application form in a visible
browser and asks him to solve a CAPTCHA. Once the CAPTCHA is solved, the natural action — and the one
the UI's own *Take over browser* affordance invites — is to finish and press Submit. The resume
options are then `continue`, `by_hand`, `abandon`. There is no `i_submitted`, even though
`await_handoff` has precisely that option for the assisted path (§9.7), which proves the spec knows
the option is needed when a human is at the keyboard.

`continue` re-enters `fill_form`, which restarts from its first line: navigate, upload, fill. It then
falls through to `submit`, whose gate (1) reads `PREFLIGHT_OK` — nothing wrote `SUBMITTING`, because
the agent never clicked — and proceeds to the click. Pre-flight's `not_duplicate` check (§9.4 #5) ran
*before* `fill_form` and is never re-run after the human touched the browser. Whether this produces a
second real application depends only on where the ATS left the page: a redirect back to the job page
or a fresh form makes `locate_submit` succeed, and the agent submits again.

**Required change.**
1. Add `i_submitted` to the `await_blocker` decision set, wired to the same handling as
   `await_handoff`'s (`SUBMITTED`, `confirmation_kind=human`, evidence = statement + screenshot).
   Make it the **first** option on the card: after a human takes over a browser, it is the most
   likely thing to have happened.
2. Re-run pre-flight #3 (`still_active`) and #5 (`not_duplicate`) after any `await_blocker` resume,
   before re-entering `fill_form`.
3. Require `submit` step (2) to assert the page is the same document instance it filled — a page
   token *plus* a DOM fingerprint recorded at fill time — not merely that a submit selector exists.

---

### C-3 · CRITICAL · `confirmed_not_submitted` is a one-click path to a second irreversible submission, and carries the least friction in the product

**Where:** §9.5; §7.1 (`POST /applications/{id}/unknown-outcome {outcome: confirmed_not_submitted}`);
§9.2.

**Why it is wrong.** §9.2 is explicit that this is the *only* route from a dispatched click back to
another click, and gating it on a human is the right call. The spec then gives that decision no
friction whatsoever:

- **No confirmation text.** Editing one sentence of a cover letter requires typing
  *"I confirm this statement is true"* (§7.4, AC-AF-19). Authorising a second irreversible
  submission to a real employer requires one click. The friction gradient is inverted.
- **No minimum wait.** An ATS confirmation email routinely lags the POST by minutes. The human is
  asked "did it land?" at the moment the evidence does not yet exist, and "I don't see it" is the
  honest answer that produces the wrong outcome.
- **No re-verification.** The system does not re-fetch the ATS, does not check the candidate's ATS
  account, and requires no artefact supporting the "not submitted" conclusion.
- **No statement of consequence.** §9.5's instruction is "check the ATS / your inbox for a
  confirmation". Nowhere does it say *if you are wrong, this employer receives a second application
  under your name and there is no unsend* — which is the entire content of C-3.
- **The trigger is tuned to fire too often.** `capture_evidence(page, timeout_s=60)` is short for a
  slow ATS confirmation page, and a timeout there produces `UNKNOWN_OUTCOME` with
  `detail="no confirmation signal"` on an application that succeeded.

**Required change.**
1. Require a typed confirmation naming the employer, e.g. `NOT SUBMITTED TO <company>`, stored on the
   decision row alongside `confirmation_text` (the column already exists in §6.3).
2. Enforce a minimum elapsed time from `click_dispatched_at` before the option is *enabled* — default
   60 minutes, configurable, never zero. `confirmed_submitted` and "check again later" stay available
   immediately; only the dangerous branch waits.
3. Require an explicit checkbox — *"I checked the ATS account and the application is not there"* —
   recorded on the decision.
4. Put the irreversibility in the UI copy and in the Telegram message, not only in §9.1's prose.
5. Raise `capture_evidence` to 180 s, and raise the `submit` node timeout to accommodate it
   (see **M-7**).

---

### C-4 · CRITICAL · Pre-flight lets the click proceed when it cannot reach the posting, and the carve-out is internally incoherent

**Where:** §9.4, closing paragraph; §9.4 checks #1, #2, #3.

*This corrects and escalates prior finding #1. The spec does reproduce the amber semantics; it rules
amber-and-allow, and its version is incoherent in a way the UI's was not.*

**Why it is wrong — two defects.**

*First, the ruling is temporally impossible as written.* Pre-flight "runs after approval, immediately
before `fill_form`" (§9.4 title). At that point there is no approval left to permit. The sentence
"approval is still allowed with the warning" describes a UI state that has already passed. What the
rule actually authorises is the **click**, with nobody asked. The one thing FR-9.1 exists to prevent
— sending an application without confirming in the last sixty seconds that the posting is live — is
what it permits. If amber-and-allow is genuinely wanted, the allow must sit *before* Approve, where a
human can weigh it.

*Second, the carve-out is unreachable in the case it was written for.* Checks #1 (`company_match`)
and #2 (`job_match`) depend on the same live re-fetch and have no `unverified` path; they fail to
`PREFLIGHT_FAILED`. A network failure therefore fails at #1 and never reaches #3's amber branch. The
amber branch can only fire when the fetch *partially* succeeds — a login wall, an error page, a
redirect — which is the case where allowing a submission is least defensible, not most.

**Required change.** Rule it red: an unverifiable #3 is a hard fail to `PREFLIGHT_FAILED` with reason
`still_active_unverified`, retryable from the dashboard once connectivity returns. If amber-and-allow
is to be kept, then (a) move the full twelve-check pre-flight to run *before* `await_review` as a
preview and re-run it after approval as a gate, and (b) give #1 and #2 the same `unverified`
semantics as #3 so the three checks are coherent. Either way this is a departure from FR-9.1 and
belongs in §17 with a DEPARTURE id; it is currently untagged.

---

### C-10 · CRITICAL · No single-instance guard, and reconciliation runs before the port bind — a second process flips live `SUBMITTING` rows to `UNKNOWN_OUTCOME`

**Where:** §9.6 ("On `jobagent serve` start, **before the API accepts requests**", steps 1, 2, 3, 5);
§3.2; §13.1 (Task Scheduler, "restart on failure"); §6.1 (SQLite WAL).

**Why it is wrong.** There is no single-instance mutex anywhere in the spec. The nearest thing is
§9.6 step 5 — "verify the checkpointer file is writable and not locked by another process" — but
SQLite in WAL mode, which §6.1 mandates, is specifically designed to permit concurrent multi-process
access. That check will not detect a second instance. Meanwhile Task Scheduler is configured to
restart the service on failure, and a hung-but-alive Windows process is an everyday event, so two
live instances are reachable in normal operation.

The ordering then makes a second instance destructive rather than merely redundant. Reconciliation
runs *before* the FastAPI bind, so process B executes all of §9.6 and only afterwards fails on
`EADDRINUSE`. In those seconds it:

- steals the run lock if A's heartbeat is stale (step 1) and marks A's live run `aborted`;
- **transitions every `SUBMITTING` row to `UNKNOWN_OUTCOME` (step 2) and fires the notification** —
  including a row belonging to a click A dispatched four seconds ago and is still capturing evidence
  for;
- resumes non-terminal threads (step 3) and opens a second Playwright persistent context on the same
  profile directory.

The human is now told "we don't know if this was submitted; check the ATS" about an application that
*was* submitted and whose confirmation has not arrived. He checks, sees nothing, and clicks
`confirmed_not_submitted` — and **C-3** does the rest. This is the double-submission path the design
missed: not a retry it forgot to guard, but a manufactured `UNKNOWN_OUTCOME` feeding the one gate
that is permitted to click twice.

**Required change.**
1. Acquire an OS-level single-instance lock (named mutex, or an exclusive lock file carrying the pid)
   as the **first** action of `jobagent serve`; exit with a clear message if held.
2. Bind `127.0.0.1:8765` **before** reconciliation, so the port is a backstop if the mutex fails.
3. Make §9.6 step 2 conditional on evidence that the owning process is gone: check the `locks` holder
   pid for liveness, and require `submitting_written_at` to be older than the `submit` node timeout
   before flipping to `UNKNOWN_OUTCOME`.
4. Make the browser worker fail loudly when the profile directory is already locked, instead of
   restarting (§4.12 currently restarts on crash).
5. Extend AC-ID-08 to assert the second process refuses to start at all, not merely that it loses the
   thread lock.

---

### M-5 · MAJOR · `is_pre_click_error(exc)` cannot key the dispatch marker to an application

**Where:** §9.3 (`def is_pre_click_error(exc)` calls `_click_dispatched_marker(exc)`;
`_mark_click_dispatching(state["application_id"])`).

**Why it is wrong.** `retry_on` receives one argument, the exception (`kb/lg-fault-tolerance.md`,
Parameters table: `Callable[[Exception], bool]`). The marker is written keyed by `application_id` but
read with only an exception in hand. With the spec's own default of 2 concurrent application threads
(Q-R), the predicate cannot tell whose click was dispatched. The spec also never says when the marker
is cleared, so after the first submission of the day every subsequent pre-click `NodeTimeoutError`
may be classified as post-click and refused a retry.

Gate (1) saves this from being a double-submission bug — a wrongly-retried post-click timeout re-enters
`submit`, reads `SUBMITTING`, and returns `"unknown"` without clicking. But an implementer reading
§9.3 will write exactly what it says, and the failure mode is silent misclassification of the most
safety-critical predicate in the codebase.

**Required change.** Carry the marker in a `contextvars.ContextVar` set inside the node and read by
the predicate on the same task, or — simpler and testable — attach the marker to the exception
itself: have step (4) wrap every escaping exception in `PostClickError(original)` before it leaves the
node, and reduce `is_pre_click_error` to `isinstance(exc, PreClickError)`. Add a static check that
`submit` re-raises nothing un-wrapped.

---

### M-6 · MAJOR · The post-click `except` awaits during cancellation, and nothing sweeps rows stuck in `SUBMITTING` while the process stays alive

**Where:** §9.3 step (4) (`except BaseException as e: await tr.transition(...)`); §9.6 (startup only);
§9.5.

**Why it is wrong.** Two linked problems.

A node timeout is delivered to an `async def` node as task cancellation. The handler catches
`BaseException` — correctly, per the spec's own reasoning — and then performs `await
tr.transition(...)`. Awaiting inside an except block in a task that is being cancelled will normally
raise `CancelledError` again at the await point, so the durable transition to `UNKNOWN_OUTCOME` may
never land. The row stays `SUBMITTING`. That is fail-safe with respect to clicking — gate (1) will
catch it — but it is *not* fail-safe with respect to the human, because:

`UNKNOWN_OUTCOME` is what routes the thread to `notify_unknown ─▶ await_unknown`. A row left at
`SUBMITTING` reaches neither. §9.6 handles `SUBMITTING` rows **only at process start**. If the process
keeps running, that application sits at `SUBMITTING` indefinitely: no notification, no `needs-you`
row, no timeout (§9.5: "There is no auto-resolution and no timeout on `UNKNOWN_OUTCOME`" — and there
is none on `SUBMITTING` either), while dedup counts it as applied and the ceiling counts it as
consumed. It is invisible.

The same gap is reachable from `submit_error_handler`: it routes non-`page_lost` failures to
`NEEDS_ATTENTION` and `finalize`, but §9.2 defines no `SUBMITTING → NEEDS_ATTENTION` transition, so
the handler itself raises `IllegalTransition` from inside an error handler — behaviour the spec never
describes.

**Required change.**
1. Perform the `SUBMITTING → UNKNOWN_OUTCOME` write with `asyncio.shield(...)`, and re-raise after it
   completes rather than returning a value from a cancelled task.
2. Add a **runtime** sweep, not only a startup one: a periodic job (alongside the 10-minute
   missed-run check in §13.1) that moves any `SUBMITTING` row older than the submit node timeout to
   `UNKNOWN_OUTCOME` and enqueues the notification.
3. Add `SUBMITTING → NEEDS_ATTENTION` to the transition table or, better, make
   `submit_error_handler` route a `SUBMITTING` row to `UNKNOWN_OUTCOME` unconditionally.
4. Add an AC: kill the *node* (not the process) between click and evidence capture and assert the
   human is notified within the sweep interval.

---

### M-7 · MAJOR · The `submit` node timeout budget is not partitioned, so a slow ATS puts `NodeTimeoutError` after the click — and AC-FM-18 cannot be exercised

**Where:** §9.3 (`TimeoutPolicy(run_timeout=180)`, `capture_evidence(..., timeout_s=60)`); test plan
AC-FM-18 (`delay(120000)` on page load).

**Why it is wrong.** `run_timeout` caps the whole node, and the node's work is pre-click page
work + click + up to 60 s of evidence capture. AC-FM-18 sets a 120 s page-load delay and expects "node
timeout fires; treated as pre-click failure; retried per policy". With `run_timeout=180` the 120 s
load *succeeds*, so the timeout the AC is written to observe never fires — the criterion is not
exercisable against this design. Worse, 120 s of pre-click work plus 60 s of evidence capture lands
the node timeout exactly at the boundary, i.e. inside step (4), after dispatch — the case the spec
works hardest to avoid.

**Required change.** Partition the budget explicitly: an internal pre-click deadline
(`PRECLICK_DEADLINE`, default 90 s) enforced in step (2) and raising `PreClickError` on expiry, and a
node `run_timeout` set to `PRECLICK_DEADLINE + evidence_timeout + margin` (e.g. 90 + 180 + 60 = 330 s)
so the node timeout can only ever fire while the pre-click deadline is still the binding constraint.
Restate AC-FM-18 against the pre-click deadline rather than the node timeout.

---

### M-8 · MAJOR · A crash inside the 5-second grace window auto-submits on restart

**Where:** §9.6 step 4 ("`APPROVED_GRACE` rows older than the grace window → treated as approved:
resume"); §7.2 ("Undo within grace: DELETE decision row + `APPROVED_GRACE → PENDING_REVIEW`").

**Why it is wrong.** The grace window is the product's only undo for an irreversible act. §9.6 step 4
converts a crash during that window into an approval — and does so *because* the row is now older
than five seconds, which after any restart it always is. The human who realises mid-window that he
approved the wrong application and kills the process is the exact person this rule submits for.
Conservative handling of an irreversible action after an unexplained crash should be to re-ask, not
to proceed.

**Required change.** On restart, transition `APPROVED_GRACE → PENDING_REVIEW`, retain the decision row
as `decisions.type='approve'` with a `superseded_by_restart` flag, and surface a Needs-you row:
*"You approved X just before the service restarted. Re-confirm?"* Add an AC mirroring AC-ID-03 that
kills during the grace window and asserts the fake ATS counter is 0 until the human re-approves.

---

### M-9 · MAJOR · AC-ID-25 is silently weakened, and §5.3's claim to satisfy it is false

**Where:** §5.5 static check ("the node named `submit` ... be reachable only from `fill_form`");
§5.3 ("The graph still satisfies AC-ID-25: the click lives in `submit`, reachable only via
`record_decision → preflight → fill_form`"); test plan AC-ID-25.

**Why it is wrong.** AC-ID-25 requires that the click node "is reachable only from **the node that
records the approval decision**". The spec's own §5.3 diagram shows `submit` reachable from
`fill_form`, and `fill_form` reachable from `await_blocker` (blocker → `continue`) and from
`await_unknown` (`confirmed_not_submitted` → `preflight` → `fill_form`). So the claim in §5.3 is
false on the evidence of the diagram three paragraphs above it, and §5.5 restates the criterion as the
weaker and trivially-true "reachable only from `fill_form`". The AC exists precisely to force an
audit of every inbound path to the click — the audit that would have surfaced **C-2**.

**Required change.** Restore AC-ID-25's wording in the static check: enumerate every path to `submit`
and require each to pass through a node that writes a `decisions` row for the current attempt. Give
`await_blocker` and `await_unknown` resumes their own decision rows (the `decisions.type` enum in §6.3
already contains `continue` and `confirmed_not_submitted`), so the check passes honestly rather than
by redefinition.

---

### M-9a · MAJOR · `spawn_apps` can relaunch a thread whose application is already under review

**Where:** §4.3 rule 4 (applied-block status set `{SUBMITTED, MANUAL, UNKNOWN_OUTCOME, SUBMITTING,
REJECTED_BY_USER}`); §4.5 rule 1; §5.2 `spawn_apps` ("INSERT applications (UNIQUE job_id →
upsert-safe), enqueue thread launches"); test plan AC-ID-16.

**Why it is wrong.** The applied-block set omits every *active* status — `PENDING_REVIEW`,
`APPROVED`, `APPROVED_GRACE`, `PREPARING`, `BLOCKED`, `PREFLIGHT_OK`. A job carried over from
yesterday at `PENDING_REVIEW` is therefore not blocked by dedup rule 4 or by eligibility rule 1: it is
re-fetched, re-scored, re-ranked, consumes a ceiling slot, and reaches `spawn_apps`. The `UNIQUE(job_id)`
constraint protects the *row* and nothing else — the spec then says "enqueue thread launches", and the
thread id **is** the application id, so the supervisor invokes `ApplicationGraph.ainvoke({...}, config)`
with fresh input on a thread that currently holds a pending `await_review` interrupt. That discards the
human's pending review, re-runs `probe_form → tailor → render → letter → factguard` at full model cost,
and leaves the dashboard's Approve returning 409 against an interrupt id that no longer exists.

AC-ID-16 ("Rediscovery of a pending job creates no second thread ... the tracker returns the existing
application") fails against this design.

**Required change.** (a) Add the active statuses to the applied-block set in §4.3 rule 4, with verdict
`already_in_flight`, and mirror them in §4.5 rule 1 and in pre-flight #5's "applied-class" definition.
(b) Make `spawn_apps` skip any job with an existing `applications` row outright, rather than relying on
an upsert. (c) Forbid launching a thread with fresh input when `aget_state(config)` returns a non-empty
`tasks[*].interrupts` — resume with `ainvoke(None, config)` or do nothing.
---

# Area B — Fabrication

§8's structure is sound and, in places, better than what most teams ship: deterministic checks
before the judge, a judge stage validated `≠ generate` (D-1), a generator constrained to emit a plan
rather than prose (§10.3), and a mutation suite that must flag 40/40 or fail the build (§8.4). C1's
structural whitelist and C2's immutables genuinely make most resume fabrication impossible by
construction. None of that is in dispute.

What follows are the four routes by which a false statement still reaches an employer. Three of them
are not leaks in the verifier — they are categories of content the verifier was never pointed at.

---

### C-5 · CRITICAL · The career-page mapper agent runs on the **unwrapped** model, bypassing `PromptGuard`, `BudgetGate` and `SpendLedger`

**Where:** §5.4 (`model=get_model("analyse").inner`); §4.13 ("**Every** model call in the codebase
goes through `GuardedModel`"); §11.1 principle 1; §12.5; §1 executive summary
("a `GuardedModel` wrapper asserts on every outbound prompt").

**Why it is wrong.** `.inner` is the raw provider model. Every claim the spec makes about outbound
prompts is implemented in the wrapper that this line discards:

- **`PromptGuard.assert_clean` never runs** on the mapper's prompts. §2.1's headline property —
  "Answer-sheet values never reach an LLM" — is asserted by exactly one mechanism (§4.13), and that
  mechanism is switched off for the one agent that runs against a live, partially-filled form. The
  spec's defence is a promise about `inspect_form`'s implementation ("returns `FormModel` (labels,
  types, required) — no values"), not a mechanism. A DOM snapshot taken after `FormFiller` has typed
  into the page carries `value` attributes; the expected-CTC field is one of them. The architecture's
  answer to "what if the tool leaks a value" was `PromptGuard`, and it is not in the path.
- **`BudgetGate.check` never runs.** The mapper is permitted 60 tool calls (§5.4), each round-tripping
  the model. It can run past the $20 hard stop and past the $100 ceiling without raising
  `BudgetHardStop`, on a run where every other call is gated.
- **`SpendLedger.record` never runs.** Those calls never appear in `spend_ledger`, so the header
  meter, the per-stage cost report, and the day total are all understated whenever a career-page form
  is processed — which breaks AC-NF-09 ("matches provider usage metadata **within 1%**") by
  construction, and makes the soft alert at $5 fire late or not at all.
- The lint in §4.13 ("no direct `init_chat_model(...).invoke` outside `llm/`") does not catch this:
  the call site uses `get_model(...)`, which is the approved accessor, and then reaches through it.

**Required change.**
1. Make `GuardedModel` implement the `BaseChatModel` surface `create_agent` requires and pass the
   *wrapper*, so guard, budget and ledger sit inside the agent loop. If that is impractical, wrap the
   agent in middleware instead: a custom `before_model` middleware
   (`kb/lc-middleware__custom.md`) that calls `PromptGuard.assert_clean` and `BudgetGate.check` on
   every request, and an `after_model` middleware that records `usage_metadata` to `SpendLedger`.
2. Delete `.inner` from the codebase and add it to the static-check ban list alongside
   `init_chat_model` (T-0.3), with an AC asserting no call site reaches an unwrapped model.
3. Specify `inspect_form` as returning a **projection** — `field_id`, `label`, `type`, `required`,
   `options` — constructed field by field from the `FormModel` artefact, never a DOM serialisation, and
   assert in a unit test that a page with a filled CTC field produces a tool result containing none of
   the answer-sheet values.
4. Add `exit_behavior="error"` to `ToolCallLimitMiddleware` (see **M-3**), so the 60-call limit
   actually stops the loop.

---

### C-6 · CRITICAL · `kind="context"` claims escape provenance, entailment and company-fact checking entirely

**Where:** §4.10 (`Claim.kind: Literal["self","company","context"]`, `context → []` provenance);
§8.2 checks C9 ("Every **`self`** claim has ≥ 1 provenance key"), C10 (entailment on "claims"),
C11 ("**`company`** claims"); §8.5 ("`kind=context` markers grey").

**Why it is wrong.** The schema defines three claim kinds and the verifier checks two of them. C9 is
scoped to `self`, C11 to `company`; C10 judges a claim against "source text", and a `context` claim has
no source text to judge against. So a sentence labelled `context` passes the provenance system by
definition.

Nothing in the spec constrains what may be labelled `context`. The label is chosen by the `generate`
model, in the same structured output that contains the claim. A model that cannot find a provenance
key for a sentence it wants to write has a schema-legal escape hatch — emit it as `context` — and the
schema *rewards* that choice, because a `self` claim without a pointer fails C9 and a `context` claim
without a pointer is valid.

The residual deterministic checks do not close it. C3 catches numerals, C4 catches out-of-vocabulary
technologies and canaries, C5 catches organisations, C13 catches mandatory-qualification words. A
sentence such as *"I have shipped agentic systems that enterprise buyers trust"* or *"I've owned
delivery from discovery through production support across the customer lifecycle"* contains no
numeral, no canary, no organisation and no qualification token. Labelled `context`, it reaches the
employer as a first-person claim about the candidate's experience, verified by nothing. This is a
T-5 violation ("Every generated claim must be traceable to a specific line of the resume") that the
schema permits.

**Required change.**
1. Define `context` narrowly and enforce the definition deterministically: `context` is permitted
   **only** for sentences with no first-person subject and no assertion about the candidate — salutations,
   transitions, the closing line. Implement it as a check (call it C14): any `context` claim whose text
   contains a first-person pronoun, or any resume-vocabulary verb phrase with an implied first-person
   subject, is reclassified as `self` and must then satisfy C9 and C10.
2. Cap `context` claims per artefact (≤ 2 for a letter, 0 for a subjective answer) and surface the count
   in the review UI next to the `[n]` markers, so an artefact that has quietly become 40% grey markers is
   visible.
3. Add seeded fabrications of exactly this shape to the AC-AF-15 mutation suite — a `self` claim
   relabelled `context` must be one of the 40, and it currently is not, because the suite is organised by
   *fact class* and this is a failure of *claim kind*.

---

### C-7 · CRITICAL · The values actually sent to employers are structurally invisible to the HITL-5 reviewer

**Where:** §7.1 Review row ("`GET /applications/{id}/answers` → routed answers (answer-sheet rows show
**field name only**)"); §6.3 `answers` ("**Answer-sheet values are never stored here**"); §11.4
(HITL-3 answers written back with `status=learned`, reused automatically); §14.2 S5
(`Ctrl+Shift+V` transient reveal); HITL-5; test plan AC-HL-19.

**Why it is wrong.** HITL-5 is "full review, no spot-checking" — the requirement that this system's
safety rests on. But the review screen is designed so that the reviewer *cannot* see a whole class of
statements being made to the employer on his behalf:

- Answer-sheet routes render as the field name only. Current CTC, expected CTC, notice period, work
  authorisation and sponsorship all reach the form as literal text and all render as a label on the
  Answers tab. Seeing the value requires a per-field transient reveal keypress which is separately
  audited as a sensitive action.
- **Learned answers are the sharper problem.** §11.4: a HITL-3 answer is stored with `status=learned`,
  the label's normalised form is added to that key's alias list, and "the next form with the same label
  does not interrupt". So free-text prose written once — the schema's own example is
  `employment_termination` — is thereafter sent to every employer whose form asks a similarly-worded
  question, never re-shown, never re-reviewed, and never passed through FactGuard. FactGuard runs on
  "tailored HTML, letter claims, subjective answers, any edited version" (§8.1). Answer-sheet and
  learned values are on none of those paths.
- `answer_sheet.status` has a value `unconfirmed`, and pre-flight #9 checks only that "every route
  [is] resolvable now (answer-sheet keys still exist)" — not that the value is `decided`. An
  `unconfirmed` work-authorisation string is a statement about visa status made to an employer,
  unreviewed.

The privacy control (§2.1, "values live in one table ... never enter graph state") and the review
control (HITL-5, "full review of everything that goes out") are in direct conflict, and the spec
resolves the conflict entirely in favour of privacy without ever naming it. The threat model behind
§2.1 is *LLM providers and logs*. The reviewer is not that threat.

**Required change.**
1. Distinguish *masked in transit* from *masked from the reviewer*. On the Answers tab, render every
   value that will be typed into the form, in full, to the local loopback session — this is the one
   surface the answer sheet exists to serve. Keep the masking for LLM prompts, traces, logs,
   notifications, exports and the tracker.
2. Route every `learned` answer-sheet value through FactGuard C3/C4/C6/C7/C13 on write, and show it in
   the review artefact the first three times it is reused (`used_count` already exists in §6.3).
3. Make pre-flight #9 fail when any route resolves to a value with `status ∈ {unconfirmed, open}`.
4. Amend AC-HL-19 to require the Answers tab to show values, not sources, and add an AC asserting a
   `learned` value appears in the reviewed artefact set.

---

### C-8 · CRITICAL · Provenance is anchored to derived keys over a document with no ids, and the spec makes fixing that optional

**Where:** §4.4 ("`resume/resume-ats.html` has **no `id` attributes** (verified by grep) ... This spec
therefore defines **element keys** computed deterministically from document structure"); the key table
(`skills.sN.v1..vM` — positional, `exp.krista.li1..li4` — positional, slugs from heading text); §10.6
("Master changes"); Q-O ("Recommended; ledger works without them"); R-14 (likelihood **Low**);
T-0.4 (Phase 0, complexity S); test plan AC-AF-08.

**Why it is wrong.** AC-AF-08 requires that a claim's provenance pointer "names an existing **element
id** in the master". The master has no ids. The spec's substitute is a key derived from heading slugs
and sibling position — and then §10.6 actively supports the human editing the master while
applications are pending, and Q-O leaves adding the ids as an unratified recommendation with the
default "ledger works without them".

The failure is silent, which is what makes it critical. Insert one comma-separated value into skill
line 1 and every `skills.s1.vN` for N above the insertion point now designates a different technology.
Rename a heading and every `proj.*` key under it changes. Stored provenance — in `Claim.provenance`,
in the `fact_checks` rows, in the `decisions.artefact_hashes` audit trail, in the NFR-3 reconstruction
bundle — does not become invalid. It becomes **wrong**: it resolves, to the wrong line. C9's test
("element text shares ≥ 2 content lemmas with the claim") is a weak filter and, for adjacent
technologies in the same skill line, will frequently pass.

The mitigation the spec relies on is `master_hash` plus "The ledger is rebuilt per `master_hash` and
cached" (§10.6). But §6.3 defines no table for ledgers and no artefact kind for a master snapshot — the
artefact `kind` enum is `jd|form_model|tailored_html|pdf|letter|answers|screenshot|evidence|factguard|
preflight|plan`. A cache is not a record. Once the master changes, no historical application's
provenance can be re-resolved, and `GET /applications/{id}/bundle` cannot satisfy NFR-3.

R-14 rates this "Likelihood: Low". A job-seeker edits his résumé. The likelihood is high.

**Required change.**
1. Promote T-0.4 from a recommendation to a hard prerequisite of Phase 1. Add explicit `id` attributes
   to `resume-ats.html`, verified by an identical text diff, and make `build_ledger` **refuse** a master
   whose ids do not match the expected key set rather than falling back to derivation. Close Q-O before
   Phase 1 starts, not at go-live.
2. Store the master: add `kind='master_html'` to the artefact enum and persist the full master bytes for
   every `master_hash` ever used by an application, with a `ledgers` table keyed by `master_hash`.
   Retention §6.5 already keeps records forever; this is the record that makes the others meaningful.
3. Make the ids content-anchored rather than positional where cheap — `skills.s1.pytorch` rather than
   `skills.s1.v3` — so a reordering or insertion in the master cannot silently repoint a pointer.
4. Add an AC to the RT or AF group: insert one skill value into the master, rebuild, and assert that
   every previously-stored provenance pointer either resolves to the same text or fails loudly.

---

### M-15 · MAJOR · AC-AF-22 ("nothing ships unchecked") is enforced by a node, not by the database — unlike its sibling invariant

**Where:** §6.4 invariants table; §9.4 check #7; §9.3 step (3); test plan AC-AF-22.

**Why it is wrong.** AC-AF-22 is written as an invariant over *any* path to `SUBMITTING`: "a missing or
stale `fact_check` blocks the transition". The spec enforces it in exactly one place — pre-flight check
#7, an ordinary node. §6.4's invariant table, which does contain a trigger for the structurally
identical rule *"`SUBMITTED` implies evidence"*, has no row for *"`SUBMITTING` implies a fresh
fact_check"*. The spec built the right mechanism once and did not reuse it for the check that guards
truthfulness rather than idempotency.

The gap is reachable: the edit endpoints in §7.4 have no status guard (see **m-5**), so an edit issued
between pre-flight and `submit` creates a new `application_versions` row and a new `fact_checks` row
while `submit` step (3) writes `SUBMITTING` with no re-check.

**Required change.** Add the trigger, mirroring the evidence trigger exactly:
`BEFORE UPDATE OF status ON applications WHEN NEW.status='SUBMITTING'`, require a `fact_checks` row
whose `artefact_hashes` equal the current version's and whose status is `pass` or
`pass_with_confirmed_edits`. Add the row to the §6.4 table. This is a few lines of SQL and it converts
the spec's strongest truthfulness claim from an argument into a constraint.

---

### M-16 · MAJOR · `pass_with_confirmed_edits` overrides every fabrication class on a memorised constant phrase, and pre-flight re-checks only one of them

**Where:** §7.4; §8.3 ("Avadh is the authority on his facts"); §9.4 checks #7 and #12; A-20;
test plan AC-AF-19.

**Why it is wrong.** To be fair to the design: T-3 is genuinely protected. Pre-flight #12 recomputes
C13 (`no_false_mandatory_claim`) independently of the `fact_checks` status, so a confirmed edit
claiming a PhD is still stopped. That is good and deliberate.

But #12 is the *only* check re-run. Pre-flight #7 accepts `pass_with_confirmed_edits` wholesale, so an
edit that trips C3 (an invented metric), C4 (a canary technology — `Azure`, `Kubernetes`,
`TensorFlow`), or C7 (a years figure contradicting `years_by_technology`) ships. T-1 is as absolute as
T-3 — "**Never** invent ... technologies ... or years of experience" — and it is the class of lie a
recruiter checks first. AC-AF-19's own worked example is *"5 years with LangChain"*, a C7 violation,
and the spec's flow ships it.

The override key is a constant string — `"I confirm this statement is true"`. By the third use it is
muscle memory, and the confirmation no longer carries information about *which* statement is being
confirmed.

**Required change.**
1. Scope the override by check class. Allow `pass_with_confirmed_edits` for C9/C10 (provenance and
   entailment on achievement wording), where the human legitimately is the authority. Forbid it for C4
   (canary technologies), C7 (years) and C13 (qualifications), which are not matters of authorship.
2. Make the confirmation text restate the specific claim — *"I confirm: 5 years with LangChain"* —
   generated from the violation, so the phrase cannot be typed from memory.
3. Re-run C3, C4 and C7 at pre-flight alongside C13, expanding check #12 or adding #13.
4. Surface a rolling count of confirmed overrides in Reports; three in a week is a signal about the
   generator or about the reviewer, and either is worth knowing.

---

# Area C — Rubber-stamping

The human gate is the last defence for both of the areas above. The spec's own R-3 is honest about
this: *"Residual: Medium — the residual is the human reviewer's attention."*

The design **measures** rubber-stamping and does not **prevent** it. Every control in §14.3 and R-3 is
a post-hoc metric written into a report the reviewer generates for himself: `review_seconds`, median
review time, reject-rate, "if median review time drops under ~20 s the report flags it". There is no
mechanism anywhere in §5, §7 or §14 that makes an unexamined approval harder than an examined one.
Two specifics make it worse rather than neutral.

---

### M-22 · MAJOR · The primary approve key advances to the next application, chaining approvals and making the undo unreachable

**Where:** §14.2 S3 keys (`A`, `Shift+A`, ...); §7.2 (5-second grace, `POST /decisions/{id}/undo`);
ui-ux-design §5.2 (`A` = *Approve & next*, `Shift+A` = *Approve & stay*).

**Why it is wrong.** The spec carries both bindings into §14.2 and defines neither. In the UI design
they are *Approve & next* and *Approve & stay*. So the primary control — the unshifted key, the one
that will be used — approves the current application **and navigates away from it**. The physical
action for fifteen applications is fifteen presses of the same key, with nothing in between.

That interacts badly with the one real safeguard. The 5-second grace window and `Z` undo are both
scoped to the application being viewed; once `A` has advanced, the reviewer is looking at a different
application, and the toast for the previous one is expiring behind him. The undo affordance is
designed for a workflow the primary keybinding prevents.

Nothing gates `A` on having opened the Letter or Answers tabs. The three tabs are `1/2/3`; approval is
available from tab 1 alone. For an application whose only risk lives on tab 3 (see **C-7**), the
reviewer can approve without the risk ever having been rendered.

**Required change.**
1. Swap the bindings: `A` = *Approve & stay*, `Shift+A` = *Approve & next*, and define both in §14.2 with
   their semantics and their API calls.
2. Gate Approve on having rendered every tab that has content for this application — Letter if a letter
   exists, Answers if any answer is routed. Record which tabs were opened on the decision row; it costs
   nothing and it makes AC-NF-15's telemetry meaningful.
3. Show the grace toast in a fixed position that survives navigation, so `Z` works after `A` has
   advanced, and extend the undo window to the full grace period regardless of the current route.
4. Add an AC: approve from tab 1 without opening tab 3 on an application with routed answers, and
   assert the API returns 409 `tabs_unreviewed`.

---

### M-13 · MAJOR · AC-HL-26 cannot pass, and §12.5 asserts the opposite inside the same document

**Where:** §12.5 ("HITL-1 / HITL-5 cannot be disabled — **No setting, flag or env var exists**");
§4.1 (`telegram: Telegram  # chat_id, approve_enabled=False, ...`); §4.14; §7.3;
test plan AC-HL-26.

**Why it is wrong.** AC-HL-26 is a static inspection: "There is no setting, flag or environment
variable that disables HITL-1 or HITL-5." §4.1 defines `telegram.approve_enabled`. §7.3 says that when
it is true, `/approve <short_id>` records `approved_without_review` and proceeds. A Telegram approve
has no diff, no evidence trace, no pre-flight preview and no artefact hashes — it is HITL-5 disabled,
by a setting, for that application. The decision type's own name says so.

*That `approved_without_review` exists and should be decided is prior finding #2 and is not re-argued
here.* The new point is narrower and is about the document: **§12.5 states a falsehood about §4.1**, and
it states it in the section whose purpose is to enumerate the guarantees that are code rather than
prose. An implementer reading §12.5 will not go looking for the flag. A reviewer trusting §12.5 will
believe AC-HL-26 is satisfied.

**Required change.** Either remove `/approve` and `approved_without_review` entirely — closing Q-I as
"No", which is what the UI design and the analysis both recommend — or amend §12.5 to state the truth
("HITL-1 cannot be disabled; HITL-5 may be waived per-application via the Telegram `/approve` command
when `telegram.approve_enabled` is true, recorded as `approved_without_review`"), amend AC-HL-26 to
match, and raise a DEPARTURE in §17 against FR-9.3. The current text is the worst of the three options.

---

### m-7 · MINOR · The approved requirements still describe HITL-5 as negotiable, and the spec never notes it

**Where:** REQUIREMENTS v0.5 §5 preamble ("Gates 1–4 are non-negotiable; gates 5–6 are a posture
decision (Q-2)"); §5 HITL-3 row (still lists CTC / notice period as halt triggers, contradicting §11.2
and AC-HL-16); §4.3 scoring table ("90–100 | Exceptional — **apply immediately** (Tier 1)");
FR-4.1 (still omits geography); FR-1.1 (Wellfound, with no Q-3 policy).

**Why it is wrong.** These are five of the ten inconsistencies `requirements-analysis.md` §2 raised
against v0.4 and asked to be fixed "before the spec cites it". They are still present in the v0.5 the
spec declares approved. The spec silently builds the right behaviour over three of them (Wellfound is
assigned `discovery_only` in §4.2; geography becomes eligibility rule 10; HITL-3 defers to the answer
sheet in §11.2) without a DEPARTURE tag, and inherits the other two unaddressed.

**Required change.** Fix the five lines in REQUIREMENTS v0.6, or add five rows to §17 recording that the
spec departs from the approved text. The "apply immediately" line matters most: it is the only sentence
in the requirements that contradicts HITL-1, and it lives in the scoring table an implementer will read
while building `selection`.
---

# Area D — LangChain / LangGraph correctness, and the §18 audit

Method: every LangGraph/LangChain symbol in the spec was grepped in the fifteen supplied `kb/` pages.
Symbols whose verifying page is outside the supplied subset (`messages.md`, `observability.md`,
`use-subgraphs.md`, `use-time-travel.md`, `test__unit-testing.md`) are not challenged here — absence
from my subset is not evidence.

**What is correct.** The API usage is, on the whole, accurate, and materially more accurate than the
norm. Verified against the supplied pages and holding: `set_node_defaults(retry_policy=, error_handler=,
timeout=, cache_policy=)` (`lg-fault-tolerance.md` §401–520, including "not inherited by subgraphs");
`TimeoutPolicy(run_timeout=, idle_timeout=)` and timeouts being async-only; `add_node(error_handler=fn)`
with `NodeError(node, error)` and a `Command(update=, goto=)` return, firing only after retries are
exhausted; `RunControl` / `request_drain(reason)` / `GraphDrained` / `runtime.drain_requested` and
resume via `invoke(None, config)`; `RetryPolicy` parameters and `default_retry_on`'s exclusion list;
`Send` from conditional edges and `Send(..., timeout=TimeoutPolicy(...))` (§262); `durability="sync"`;
`AsyncSqliteSaver` from `langgraph.checkpoint.sqlite.aio` with `setup()`; `Overwrite` from
`langgraph.types`; `ProviderStrategy` / `ToolStrategy`; `with_structured_output(..., include_raw=True)`;
`HumanInTheLoopMiddleware(interrupt_on={... "allowed_decisions", "when"})` with `version="v2"`; the four
removed 1.0 symbols (`LLMChain`, `AgentExecutor`, `initialize_agent`, `RetrievalQA`) are indeed absent
from the spec. Gotcha citations 2, 11, 13 and 14 match `CORE-CONCEPTS.md` §4. The interrupt rules in
§5.1's convention table are a faithful compression of `lg-interrupts.md` "Rules of interrupts".

**The §18 verdict: three of its entries are false.** All three are listed in §18's closing paragraph as
"explicitly **not** from the knowledge base". All three are in the knowledge base. This matters beyond
the individual APIs, because §18 is the artefact that discharges TR-2, and because the spec's opening
line claims "Every LangChain/LangGraph symbol named here was grepped in `knowledge-base/` before it was
written down."

---

### M-1 · MAJOR · The §5.1 interrupt/retry `[UNVERIFIED]` is false — the knowledge base answers it explicitly, and the "defensive" mitigation is unnecessary and harmful

**Where:** §5.1, row "Interrupt node retries": "`retry_policy=RetryPolicy(max_attempts=1)` on every
`await_` node. **[UNVERIFIED]** whether the interrupt control-flow exception is excluded from
`default_retry_on`; disabling retries on those nodes removes the question | defensive". Also §18's
closing list.

**What the knowledge base actually says.** `kb/lg-fault-tolerance.md`, in a section headed
**"Behavior with `interrupt()`"**:

> "`interrupt()` raised inside a node is **not** routed to the error handler. Interrupts use the
> `GraphBubbleUp` mechanism to pause graph execution for human-in-the-loop workflows, **bypassing both
> retry policies and error handlers**. The graph pauses as usual."

The question is answered, in the same page the spec cites nine other times, under a heading that names
the question.

**Why the consequence is not cosmetic.** Because interrupts bypass retry policies, `max_attempts=1` on
the `await_*` nodes provides no interrupt protection — there was never any to provide. What it does
provide is the removal of retries from seven nodes for *genuine* transient failures, and it means any
exception in an `await_*` node fails the graph run outright rather than being retried once. The spec
adopted a behavioural change to the safety-critical HITL path on the strength of a question it did not
ask.

**Required change.** Delete the `[UNVERIFIED]` mark and the row's rationale; cite
`lg-fault-tolerance.md` "Behavior with `interrupt()`". Decide `max_attempts` on the `await_*` nodes on
its merits (the default of 3 is fine, since the nodes do no I/O before the interrupt). Remove the item
from §18's closing list. Re-run the same check against the remaining `[UNVERIFIED]` marks before the
spec is re-submitted.

---

### M-2 · MAJOR · The §6.5 checkpoint-pruning `[UNVERIFIED]` is false, and the instruction it justifies is dangerous

**Where:** §6.5: "**[UNVERIFIED — `langgraph-checkpoint-sqlite` has no documented delete-thread API in
the knowledge base; the implementer deletes rows from the saver's tables by `thread_id` and must confirm
table names against the installed package]**"; §18 closing list; R-10.

**What the knowledge base actually says.** `kb/lg-checkpointers.md` documents `adelete_thread` as part
of the checkpointer interface (§407, in the method signature block) and gives it its own subsection at
§544:

> "#### delete_thread / adelete_thread — Delete all checkpoints and writes for a thread. Both checkpoint
> rows and write rows must be deleted."

The same page's "Extended capabilities" table also lists `aprune` ("Thread history pruning").

**Why the consequence is not cosmetic.** The spec's instruction is to hand-delete rows from an
undocumented internal schema and then `VACUUM` the file. The KB's own schema notes warn that a
checkpoint and its `writes` rows must be deleted together, and that metadata must be stored in full
because "LangGraph adds new metadata fields ... in minor releases". Hand-rolled deletion against
inferred table names is the single most likely way to corrupt `checkpoints.db` — the risk R-10 rates
"Likelihood: Low" on the assumption that nothing writes to that file except the library.

**Required change.** Replace §6.5's retention implementation with `await checkpointer.adelete_thread(thread_id)`
per terminal thread, falling back to `aprune` if the installed saver exposes it. Keep the `VACUUM`.
Remove the item from §18's closing list. Amend AC-NF-12 to assert the API was used rather than that rows
disappeared.

---

### M-3 · MAJOR · The §5.4 `ToolCallLimitMiddleware` `[UNVERIFIED]` is false, and the default `exit_behavior` means the 60-call limit does not stop the mapper

**Where:** §5.4: "`ToolCallLimitMiddleware` is verified in `middleware__built-in.md` (name only;
constructor parameters **[UNVERIFIED]** — the implementer must read the page for the exact kwargs)";
§18 closing list.

**What the knowledge base actually says.** `kb/lc-middleware__built-in.md` §591–660 gives a worked
example — `ToolCallLimitMiddleware(thread_limit=20, run_limit=10)` and
`ToolCallLimitMiddleware(tool_name="search", thread_limit=5, run_limit=3)` — followed by a full
configuration table for `tool_name`, `thread_limit`, `run_limit` and `exit_behavior`.

**Why the consequence is not cosmetic.** `exit_behavior` defaults to `'continue'`, documented as:
"Block exceeded tool calls with error messages, let other tools and the model continue. **The model
decides when to end** based on the error messages." The spec passes `run_limit=60` and nothing else, so
on hitting the limit the agent keeps looping — each blocked call still costs a model round-trip — until
the model chooses to stop. The middleware was chosen as the runaway-loop guard for the one agentic
component in the system, and as configured it is not one. Combined with **C-5** (the mapper bypasses
`BudgetGate` entirely), there is no bound at all on that loop.

**Required change.** `ToolCallLimitMiddleware(run_limit=60, thread_limit=120, exit_behavior="error")`,
with `ToolCallLimitExceededError` handled in `fill_form` as an `unsupported_form` fallback. Remove the
item from §18's closing list.

---

### M-4 · MAJOR · §5.1 forbids a graph-wide `error_handler`; §5.3 and §13.3 require one — and `BudgetHardStop` is retried three times before any handler fires

**Where:** §5.1 ("Retry defaults ... **No graph-wide `error_handler`** ... handlers are attached per
node"); §5.3 diagram ("Any node raising `BudgetHardStop` / `PauseRequested` ──error_handler──▶
[await_pause]"); §13.3 ("the raising node's `error_handler` stores `resume_target=<node>` and routes to
`await_pause`"); §5.5 (only `submit` is shown with a handler); test plan AC-HL-25, AC-FM-09.

**Why it is wrong.** Three linked defects.

*The contradiction.* For "any node" to route to `await_pause`, every node needs the handler — that is a
graph-wide default, which §5.1 explicitly forbids. §5.5's reference wiring attaches a handler to exactly
one node, `submit`. So as specified, `BudgetHardStop` raised in `tailor`, `generate_letter`,
`generate_answers` or `factguard` has no handler, exhausts its retries, and fails the run. AC-HL-25
(`/pause` → "in-flight node completes; state persisted; `/resume` continues") and AC-FM-09 are both
written against the behaviour §5.3 describes and §5.1 prohibits.

*The retry interaction.* `default_retry_on` retries **any** exception except a fixed list
(`ValueError`, `TypeError`, `ArithmeticError`, `ImportError`, `LookupError`, `NameError`, `SyntaxError`,
`RuntimeError`, `ReferenceError`, `StopIteration`, `StopAsyncIteration`, `OSError`), per
`kb/lg-fault-tolerance.md` "Default behavior". `BudgetHardStop` and `PauseRequested` are custom
exceptions on none of those lists, so with the graph-wide `RetryPolicy(max_attempts=3)` each is retried
twice with exponential backoff before any handler runs. A pause takes effect after up to three attempts
per node; a budget stop is re-evaluated three times.

*The unresolved mechanics.* §5.1's stated reason for banning a graph-wide handler — that an `await_` node
must never have a handler that could swallow the interrupt — is **unfounded**, per the same KB section
that answers **M-1**: interrupts bypass error handlers entirely. The real constraint is the one the KB
does state: error-handler nodes are excluded from certain defaults (`lg-fault-tolerance.md` §514–520).

**Required change.**
1. Derive `BudgetHardStop` and `PauseRequested` from an exception class on the non-retryable list (e.g.
   `RuntimeError`), or set a graph-wide `retry_on` wrapping `default_retry_on` that returns `False` for
   both — so control-flow exceptions are never retried.
2. Use `set_node_defaults(error_handler=pause_or_fail_handler)` and override per node where different
   behaviour is needed (`submit`). Correct §5.1's rationale to cite the real constraint.
3. Add an AC exercising `/pause` during `tailor` and asserting the node is not retried before the pause
   takes effect.

---

### m-9 · MINOR · Error handlers must be idempotent, and the spec never says so

**Where:** §9.3 (`submit_error_handler`); §5.1.

`kb/lg-fault-tolerance.md`, "Resume-safe failures": *"Failure provenance is checkpointed. If the graph
is interrupted or the process crashes after a node fails but before the handler completes, the handler
sees the same `NodeError` context when the graph resumes from its checkpoint."* So an error handler can
run twice. The spec reasons carefully about node re-execution and says nothing about handler
re-execution. `submit_error_handler` writes `NEEDS_ATTENTION`, which is idempotent by luck rather than
design.

**Required change.** Add a row to §5.1's convention table: error handlers are re-executed on resume and
must be idempotent; state writes inside them use the same conditional-`UPDATE` discipline as
`Tracker.transition`. Extend the AC-ID-13 static check to cover functions registered as `error_handler`.

---

### m-6 · MINOR · `include_raw=True` returns a parsed/raw pair; a validator failure will not raise to the caller

**Where:** §4.6 ("`with_structured_output(Score, include_raw=True)` ... Pydantic validators cap each
dimension and reject totals ≠ sum (AC-SC-01)"; "One retry on schema failure, then `evaluation_failed`");
§4.13 (`GuardedModel.ainvoke(...) -> AIMessage`); §4.10.

`kb/lc-models.md` §718: *"Set `include_raw=True` to get both the parsed output and the raw AI message."*
The return is a pair, not an `AIMessage` — so `GuardedModel.ainvoke`'s annotated return type is wrong for
every structured-output call site, and the "reject / retry on schema failure" logic must **inspect** the
result rather than catch an exception. The knowledge base does not document the failure path for
`include_raw=True`, so the implementer must confirm it against the installed package — this is a
legitimate `[UNVERIFIED]` that the spec did not mark.

**Required change.** Type `GuardedModel.with_structured_output(...).ainvoke` as returning the
parsed/raw pair; specify that §4.6's retry branches on the parse-failure field, not on an exception;
mark the failure-path semantics `[UNVERIFIED]` in §18 and confirm at build time.

---

### m-12 · MINOR · `fetch_and_extract` and `score` are 30-minute monolithic nodes under `durability="sync"`, and their timeout is retryable by default

**Where:** §5.2 ("`fetch_and_extract` / `score`: `timeout=TimeoutPolicy(run_timeout=1800)`"; per-job
`asyncio.Semaphore(4)`); §5.1 (`durability="sync"`, default `max_attempts=3`).

`durability="sync"` checkpoints between super-steps, so a node processing 140 jobs writes no checkpoint
for up to thirty minutes; `NodeTimeoutError` is retryable by default (`lg-fault-tolerance.md`), so the
worst case is three 30-minute attempts. The internal per-job idempotent writes make each retry cheap, so
this is a latency and observability problem rather than a correctness one — but the Run console's "live
step" (§13.5) will sit on one node for half an hour, and AC-NF-16's 60-minute budget has no headroom for
it.

**Required change.** Either fan out per job with `Send` and a bounded dispatcher, or record per-job
progress to `job_evaluations` as it happens and surface it to the Run console; set
`retry_on` on these two nodes to exclude `NodeTimeoutError`, since a timeout there means the batch is
too large, not that it is transient.

---

# Area E — Requirements traceability

The matrix is in the header of this report. Findings not already raised:

### M-19 · MAJOR · Ledger and master snapshots are never persisted, so NFR-3 reconstruction degrades to unusable after any master edit

**Where:** §6.3 (artefact `kind` enum; no `ledgers` table); §10.6 ("The ledger is rebuilt per
`master_hash` and cached"); §7.1 (`GET /applications/{id}/bundle` → "NFR-3 reconstruction"); §6.5
("Records are kept forever").

**Why it is wrong.** NFR-3 is the requirement that any past application can be reconstructed. The bundle
lists PDF, HTML, letter, answers, form payload, evidence, score and decisions — every element of which
references provenance via element keys, and none of which includes the ledger or the master those keys
resolve against. §10.6 calls the ledger a cache. A cache is not a record. Once the master changes, the
`[n]` markers in an archived letter cannot be resolved, and `element_text(html, key)` has no `html` to
read. This is the same root as **C-8**, but the requirement it breaks is different, so the fix has to be
specified in §6, not only in §4.4.

**Required change.** Add `kind='master_html'` to the artefact enum and persist the master bytes per
`master_hash`; add a `ledgers(master_hash PK, facts JSON, built_at)` table; include both in the NFR-3
bundle; add an AC asserting a bundle exported after a master change still resolves every provenance
pointer.

### M-18 · MAJOR · A source that breaks silently is indistinguishable from a quiet day

**Where:** §4.2 (adapters, `extraction_rule JSON` on the watchlist); §6.3 `source_runs`
(`status ok|partial|failed|rate_limited|skipped`); §13.6 (failure table covers "down / 429 / 403"); R-5,
R-6.

**Why it is wrong.** The most likely real-world failure for a scraping system is not a 403 — it is a
board changing its HTML so a CSS/JSON extraction rule matches nothing while the request returns 200. In
this design that produces `source_runs.status='ok'`, `results=0`, a smaller funnel on the Today
dashboard, and no alert of any kind. FR-1.8's audit log records it faithfully and nothing reads the
record. The system quietly stops finding jobs, on a product whose entire value is finding jobs, and the
signal is a number that also means "slow day".

**Required change.** Keep a per-source trailing yield baseline (median results over the last 14 runs) on
the `company_watchlist` / source config. On a run where a source returns 0 with a non-zero baseline, or
drops more than ~70% against it, set `source_runs.status='suspect'`, write an `audit_events` row, and
put it on the morning report's attention list and in M4. Add an AC to the DS group: serve a board whose
selector no longer matches and assert the run is flagged, not merely recorded.

### m-1 · MINOR · Pre-flight check names do not match the test plan's

AC-SB-08 expects the failing check to be named `artefacts_match_approved`; §9.4 names checks #8 and #9
`letter_tailored` and `answers_accurate`. `preflight_results.check_name` is declared as "12 enums" and
AC-SB-01 requires the checks to be *named*, so the mismatch is testable. Align the names in §9.4 with
the test plan, or amend AC-SB-08.

### m-2 · MINOR · AC-HL-24 is narrowed

AC-HL-24: *"Payload ... Contains everything the reviewer needs (artefact ids, hashes, summary);
reviewer actions require no new LLM call."* §5.3 keeps the second half and discards the first: "The
dashboard never needs the payload to render", with a payload of `{kind, application_id,
artefact_hashes}` and no summary. Defensible as a design choice, but it is a change to an approved
acceptance criterion made in a parenthesis. Either add the summary fields to the payload or amend
AC-HL-24 and note it in §17.

### m-3 · MINOR · `GET /ledger` is used by two screens and is absent from the endpoint map

§8.5 and §14.2 S6 both call `GET /ledger` ("facts and element keys only, no answer sheet") for the
edit-mode live guard. §7.1's endpoint map does not list it. Add it, with its response schema, and state
explicitly that it is the one endpoint that must never include answer-sheet data.

### m-4 · MINOR · `dismiss_expired` / `expired` has no handler in `record_decision`

§7.1 accepts `type: dismiss_expired` on `POST /decisions`; §7.2 says it "cancels the thread by resuming
with `{type: "expired"}`". §5.3's `record_decision` routes `reject`, `regenerate`, `postpone` and
`approve` only. Add the `expired` branch (straight to `finalize`), or the resume will fall through to an
undefined route.

### m-11 · MINOR · Two authorities write the `decisions` row and the status transition

§7.2 step 5 has the API insert the `decisions` row and step 6 transition to `APPROVED_GRACE`; §5.3's
`record_decision` node also "writes `decisions` row; status → `APPROVED` / `REJECTED_BY_USER` /
re-queue". The `UNIQUE(application_id, interrupt_id)` constraint makes the double-write safe, but two
components owning one row and one transition is how state machines rot. Name one owner — the API for
recording, the node for transitioning — and say so in §7.2.
---

# Area F — Test plan alignment

Fourteen of 277 acceptance criteria cannot be satisfied by this architecture. Nine are covered above
(AC-AF-08 → C-8; AC-AF-22 → M-15; AC-AF-19 → M-16; AC-ID-16 → M-9a; AC-ID-25 → M-9; AC-ID-08 → C-10;
AC-HL-24 → m-2; AC-HL-26 → M-13; AC-FM-18 → M-7). The remainder:

### M-10 · MAJOR · AC-SB-01's 60-second pre-flight-to-click bound is unachievable with a serialised browser worker, and no throughput budget exists for 20 applications/day

**Where:** §9.4 ("the whole pre-flight completes within 60 s of the click (`fill_form` and `submit`
follow immediately; the browser worker queue is FIFO)"); §3.2 (`browser_worker` — "serialised (one form
at a time)"); §5.3 (`fill_form` `timeout=600`, `probe_form` `timeout=180`); Q-R (2 concurrent
application threads); test plan AC-SB-01, AC-NF-16.

**Why it is wrong.** Pre-flight runs over HTTP through `PacedClient`, not through the browser worker, so
nothing orders the two. When pre-flight finishes, `fill_form` enters a FIFO queue behind whatever form
is currently being filled — up to its 600-second timeout. "FIFO" describes the ordering; it does not
bound the wait. With two application threads and a single serialised browser, the click can occur ten
minutes after `still_active` was last verified. AC-SB-01's 60-second bound is the freshness guarantee
that makes pre-flight meaningful, and the architecture cannot hold it.

The same serialisation is unbudgeted for the day as a whole. Twenty applications, each needing
`probe_form` (up to 180 s) and `fill_form` (up to 600 s) on one browser, is up to 4.3 hours of strictly
serial browser time before any human review. §15 never performs this calculation, and AC-NF-16's
60-minute end-to-end budget does not survive it.

**Required change.**
1. Re-verify freshness inside the browser worker: move the `still_active` re-fetch (and #1, #2) to a
   final pre-click check performed by `submit` step (2), immediately before `locate_submit`, and store
   its result in `preflight_results` as a thirteenth row. Then AC-SB-01's window is structurally
   satisfied rather than hoped for.
2. Add a §15 throughput budget for 20 applications through one browser; if it does not fit, either raise
   browser concurrency (with a separate profile per worker and an explicit statement of what that does
   to HITL-2 hand-off) or lower the recommended ceiling.
3. Amend AC-SB-01 to bind the *final* freshness check to the click, not the whole twelve-check sweep.

### M-11 · MAJOR · AC-HL-13 ("no re-navigation loses the entered fields") contradicts LangGraph resume semantics

**Where:** §5.3 (`await_blocker ─▶ fill_form`); §5.1 ("node restarts from the top on resume"); §5.3
`fill_form` ("Browser: navigate, upload PDF, fill routed values"); test plan AC-HL-13.

**Why it is wrong.** AC-HL-13 requires that after a human solves a CAPTCHA and clicks `continue`,
"form-filling continues in the same session; **no re-navigation loses the entered fields**". Per
`kb/lg-interrupts.md`, resume restarts the node from its first line, and `fill_form`'s first action is
navigation. The spec carries an opaque `fill_session` token in state but never specifies that
`fill_form` inspects the live page and skips work already done. As written, the resume re-navigates,
losing the fields and quite possibly re-triggering the challenge — and the alternative implementation
(resume mid-form on the existing page) is the one that creates **C-2**.

**Required change.** Specify `fill_form` as explicitly resumable: at entry, ask the browser worker
whether `fill_session` still holds a live page for this application and what its URL, page index and
filled-field set are; skip navigation and any field already recorded `filled=True`; re-navigate only
when the session is gone. State this in §5.3's node table as a contract, and pair it with C-2's
`i_submitted` option and the pre-click DOM fingerprint so that "resume on the live page" is safe.

### M-12 · MAJOR · AC-HL-17 (< 10% of forms halt) is unreachable given the spec's own defaults

**Where:** §11.2 routing table; §11.3 (`relocation_stance`, `preferred_start_date` — "HITL-3 until
filled"; non-INR currency — "**HITL-3**, never converted"); §11.5 / D-7 (`years_by_technology` "Empty by
default"); §19 Q-D, Q-F, Q-K (all defaulted to HITL-3, all unratified); test plan AC-HL-17, and Phase 3's
exit gate "AC-HL-14..17 green".

**Why it is wrong.** Three of the most common questions on an application form — earliest start date,
willingness to relocate, and years with a named technology — are all defaulted to a halt, and a fourth
(expected CTC in a non-INR currency) halts on every international application. On a realistic 40-form
corpus the halt rate will be well above 50%, not below 10%. Phase 3 cannot exit against its own gate.

The halt-on-unknown behaviour is *correct* — it is T-4, and it is the right call. The defect is that a
target of < 10% was accepted alongside defaults that guarantee the opposite, and the plan schedules the
gate before the data that would satisfy it exists.

**Required change.** Make Q-D, Q-F and Q-K **blocking prerequisites of Phase 3**, not open questions
carried to go-live — they are four table rows the owner can fill in an hour, and they are the single
cheapest de-risking available (`PRIOR-FINDINGS.md` says as much). Restate AC-HL-17 as conditional:
"< 10% with a fully populated answer sheet including `years_by_technology`, relocation stance and start
date; measured and reported, not gated, until those are supplied."

### M-14 · MAJOR · AC-NF-04 fails by design, and the exception is untagged

**Where:** §4.13 ("The phone number is on the resume and is a *contact* constant, not answer-sheet data");
§10.3 ("The `generate` model receives: **the ledger** (facts with element keys and text)"); §4.4
(`hdr.contact.{location,phone,email,linkedin,github}` are ledger elements); test plan AC-NF-04.

**Why it is wrong.** AC-NF-04 scans every LLM request body in the E2E suite for "`19.8`, `32 LPA`, `₹32`,
`1 month notice`, **the phone number**, or any answer-sheet value" and requires zero occurrences. §4.13
deliberately exempts the phone number, and §10.3 puts the whole ledger — including
`hdr.contact.phone` — into the `generate` prompt. The suite will fail, correctly, on the spec's own
design. The reasoning in §4.13 is defensible (the number is on a résumé that goes to employers anyway),
but it is a departure from an approved acceptance criterion, made in a parenthetical sentence, with no
DEPARTURE id.

**Required change.** Either exclude `hdr.contact.*` from the ledger projection sent to models — trivial,
since no tailoring operation touches the header, which C2 holds byte-identical — or raise a DEPARTURE in
§17 and amend AC-NF-04 to drop the phone number from its scan list. The first option is better: it costs
nothing and keeps the acceptance criterion intact.

### m-8 · MINOR · AC-NF-17 is unachievable under the spec's own widened definition of a rescue event

§13.5 defines `rescue_events` as "any transition `by='reconcile'`, any lock steal, any
`NEEDS_ATTENTION`, any manual DB edit". The test plan defines a rescue as an "intervention outside
HITL-1..5". R-11 rates "PC asleep / service not running" at likelihood **High**, and every service
restart produces reconcile transitions. So the spec's definition counts ordinary Windows behaviour as a
rescue and makes "≥ 18 of 20 runs rescue-free" unreachable. Narrow the definition to human interventions
outside the designed gates, and track reconcile transitions separately as a health metric.

---

# Area G — Security and privacy

**What holds.** Loopback bind plus CSRF plus `Origin` check (§7, §12.2); the outbound allowlist enforced
in `PacedClient` and proven by the E2E proxy (AC-NF-03); one Telegram `chat_id` with the sender check
preceding parsing (§7.3) and `unauthorised_telegram` logging; allowlisted notification template
variables (§4.14); prompt hashes rather than prompts in the DB; secrets read from `HKCU\Environment` via
`winreg` rather than the process env, which matches the operator's own recorded constraint; `.gitignore`
plus a pre-commit secret scan; the browser profile excluded from export.

**What does not.**

- **C-5** is the security finding of record: the one mechanism that enforces "answer-sheet values never
  reach an LLM" is bypassed for the one agent that runs against a live form. The guarantee in §1's
  headline table, in §2.1 and in §11.1 is aspirational for that path, not enforced.
- **C-7**: the privacy control defeats the review control, and the spec does not acknowledge the
  trade-off.
- **M-14**: the phone number is exempted from the prompt scan by fiat.

### M-23 · MAJOR · The budget hard stop is a floor, not a ceiling, and the spend figure is wrong whenever a career-page form is processed

**Where:** §4.13 / §13.3 (`BudgetGate.check` reads the *completed* day total before each call;
`SpendLedger.record` writes after); §5.2 (`asyncio.Semaphore(4)` inside discovery nodes); Q-R (2
concurrent application threads); §5.4 (**C-5**); test plan AC-NF-09, AC-FM-09, TR-12.

**Why it is wrong.** Two defects. First, there is no reservation: the gate compares the sum of
*recorded* spend against the threshold, so with four in-flight calls in a discovery node plus two
application threads, up to six calls can be dispatched after the total crosses `hard_stop_usd`. On the
`generate` stage with long ledger+JD prompts that is a meaningful overshoot of a control whose purpose
(TR-12) is to catch a runaway loop early. Second, and worse: the mapper agent's calls never reach
`SpendLedger` at all (**C-5**), so the day total, the header meter, the per-stage report and the soft
alert are all understated by an unbounded amount on any day with career-page forms. AC-NF-09 requires
the cost report to match provider usage metadata "within 1%".

**Required change.** Reserve before the call: `BudgetGate.check` writes a pending `spend_ledger` row with
an estimated cost (tokens estimated from prompt length × price) and reconciles it against
`usage_metadata` afterwards; the gate sums recorded + pending. Route the mapper agent's calls through the
ledger (see **C-5**). Add an AC asserting that with `hard_stop_usd=$20` and six concurrent calls, the
day total never exceeds $20 by more than one call's cost.

### M-17 · MAJOR · At the budget hard stop the reviewer can approve and reject but cannot edit — the cost control disables the truthfulness control

**Where:** §7.4 ("FactGuard.check(...) (synchronous, **judge model**)" on every `PUT /letter`,
`/resume-text`, `/answers/{field_id}`); §13.3 ("approvals, pre-flight, fill and submit make no LLM call
and are unaffected (AC-FM-09)"); §4.13 (`BudgetGate.check` on every model call).

**Why it is wrong.** §13.3's claim enumerates approvals, pre-flight, fill and submit — and omits *edit*,
which is part of the same HITL-R2 decision set and which does make a model call, once per save, through
the judge. At `hard_stop_usd` the edit endpoints raise `BudgetHardStop` inside a synchronous API request.
The reviewer is then presented with an application he wants to correct one line of, and his options are
to approve it as-is or reject it. A budget control has disabled the mechanism by which a human fixes a
false claim.

It is also an unbounded, user-driven cost path: a reviewer editing a letter sentence by sentence
triggers a full judge pass per keystroke-save, on top of the repair loop's up-to-two regenerations
(§8.3), each of which re-runs FactGuard.

**Required change.** Split FactGuard's edit path: run C1–C9, C12 and C13 (all deterministic) synchronously
on every save, and run C10/C11 (judge) once, on demand, when the reviewer requests approval. Exempt the
edit path from the hard stop with a small dedicated reserve, and say so in §13.3. Debounce and cache
judge results per claim hash so unchanged claims are never re-judged. Correct §13.3's sentence to name
edit explicitly.

### m-5 · MINOR · The edit endpoints have no status guard

§7.4's `PUT /letter`, `/resume-text` and `/answers/{field_id}` validate the payload and run FactGuard but
never check the application's status. They are therefore callable during `APPROVED_GRACE`, `APPROVED`,
`PREFLIGHT_OK` and `SUBMITTING`. The submission itself is protected — `fill_form` uploads the `pdf_ref`
carried in graph state, and content-addressed artefacts mean the approved bytes still exist — so this is
not a fabrication path. It is an audit-integrity path: `current_version_id` and `resume_version` can end
up describing a version that was never submitted, which is exactly what NFR-3's reconstruction promises
they describe. Require status `∈ {PENDING_REVIEW, TAILORING_FAILED}` and return 409 otherwise.

---

# Area H — Operational readiness

**What holds.** The lock design in §13.2 (`INSERT OR FAIL`, heartbeat, expiry-guarded steal, rescue
logging) is correct and the `skipped_lock_held` run row is the right outcome. The catch-up rule and the
09:15 / M8 escalation are well specified. `synchronous=FULL` on the record DB with checkpoints in a
separate file is the right call and the rationale given (A-17) is sound. `%LOCALAPPDATA%` over a
OneDrive-synced Desktop path (D-5) is correct and well argued — and note that it is the same trap
recorded in the operator's own working-repo memory, so the departure is well founded.

**What does not,** beyond **C-10** (no single-instance guard) and **M-18** (silent source breakage):

### C-11 · CRITICAL · There is no "real submission disabled" master switch, which the test plan's own go-live gate presumes

**Where:** test plan §17 (gate: "**Enable real submission**"); §15 T-7.3 ("Supervised first live week:
ceiling 1/day"); §12.5 (guard-rails table); §4.1 `Settings`.

**Why it is wrong.** The test plan's exit gate is phrased as a switch being thrown — "Enable real
submission ... 100% of AF and ID groups pass ... No exceptions, no waivers" — and the entire
pre-go-live test strategy depends on the system being incapable of clicking at a real employer while the
suite runs. No such setting exists. `Settings` has `daily_ceiling`, and T-7.3's plan is to set it to 1.
A ceiling of 1 is not "cannot submit": it permits one real submission per day from the moment the code
first runs, including during a developer's manual test on a real URL, including on day one of Phase 2
when `submit` is first wired up, and including any accidental run against a real posting in the
watchlist.

The consequence is not hypothetical for this project specifically: the fake ATS (T-2.5) arrives in Phase
2, the real source adapters (T-4.2) arrive in Phase 4, and the two will coexist on one machine with one
settings row for three phases.

**Required change.** Add `settings.submission_enabled: bool = False` and check it inside `submit` gate
(1) — before any browser work, raising `SubmissionDisabled` and routing to `NEEDS_ATTENTION` — and again
in `fill_form` before the first page-committing POST (**C-1**). Require a typed confirmation to enable
it in Settings, log an `audit_events` row on every change, and add a static check plus an AC asserting a
fresh install has it `false`. Make T-7.3's first live week the act of turning it on, with the ceiling
at 1 as a second, independent limit rather than the only one.

### M-20 · MAJOR · Phase exit gates cite acceptance criteria that later phases implement

**Where:** §15 Phase 1 ("exit: AC-AF-01..13, AC-AF-15, AC-AF-16 green"); Phase 2 ("exit: AC-ID-01..25,
AC-FM-05..07, AC-FM-14, AC-FM-18 green against the fake ATS").

**Why it is wrong.** The gates reach forward into work that has not been scheduled yet:

- **AC-AF-11** (a form field asking years-with-a-technology halts at HITL-3) needs the question router
  and form probe — T-3.6, Phase 3. **AC-AF-12** requires "the pre-submit check FR-9.1 #12 fails the
  application" — pre-flight is T-2.9, Phase 2. Neither can be green at the end of Phase 1.
- **AC-ID-16** (rediscovery creates no second thread) needs dedup and discovery — T-4.5 and T-4.9,
  Phase 4. **AC-ID-22** (`applied manually` blocks automation) needs the fallback surface — Phase 4/5.
  **AC-ID-18** (two threads, two companies, distinct tailored PDF hashes in the POST bodies) needs
  tailoring — T-3.1/T-3.2, Phase 3. None can be green at the end of Phase 2.

Since Phase 2's exit is the gate that certifies the submission protocol, a gate that cannot be met will
either be waived — against a test plan whose §17 says "no exceptions, no waivers" — or will silently
redefine what "green" means at the exact point where that matters most.

**Required change.** Re-derive each phase gate from the tasks in that phase. Split the forward-reaching
criteria explicitly: Phase 2 exits on `AC-ID-01..15, 17, 19..21, 23..25`; `AC-ID-16, 18, 22` move to
Phase 4's gate; `AC-AF-11, 12` move to Phase 3's. State the *deferred* criteria in each phase's row so
the omission is visible rather than implied.

### M-21 · MAJOR · The schedule is six to nine months for one person and never says so, and the yield question is sequenced last

**Where:** §15 ("**Totals:** 60 tasks ... ≈ 115–190 implementer-days"); §15 T-4.2 (all eight source
adapters, one **XL** task); Phase 4; R-5 ("Discovery yield too low ... Likelihood: **High initially**");
`PRIOR-FINDINGS.md` blocker #1 (the seed watchlist); §19 Q-B.

**Why it is wrong.** Three things.

*The elapsed time is never stated.* 115–190 implementer-days for a single operator is six to nine months
of calendar time. §15 presents the figure as a total and then says "Phase 4 can proceed in parallel with
Phase 3 after Phase 2" and "Phase 6 can start after T-5.2 stabilises the API" — parallelism that means
nothing with one implementer. §16's risk register, which lists fifteen risks, does not list schedule.

*The upper bound is soft.* XL is defined as "> 5 days" with no ceiling, and the three XL tasks are
T-4.2 (eight source adapters, four of them adversarial scrapers), T-5.2 (every endpoint in §7.1) and
T-6.3 (the entire review screen). Each is plausibly 15+ days. The 190-day figure is optimistic by
construction.

*The ordering is inverted against the project's purpose.* The single biggest uncertainty is R-5: whether
the submit-capable sources (Greenhouse/Lever/career pages, gated on a watchlist that Q-B says is empty)
yield anything at all. That question is answered by T-4.2/T-4.3 in Phase 4 — after roughly 100 days of
work on safety machinery whose value is zero if the answer is "nothing to apply to". This is a
job-search tool for someone who needs a job now.

**Required change.**
1. State the elapsed estimate in §15 and add "schedule / opportunity cost" to §16 with an honest
   severity.
2. Pull a **discovery spike into Phase 0**: Greenhouse and Lever board JSON for ten seed companies, no
   scoring, no tailoring, no UI — a script that prints how many eligible-looking AI roles exist per week
   on submit-capable sources. Two days. It either de-risks the whole project or kills it before day 100.
   Make it the trigger for answering Q-B.
3. Decompose the three XL tasks into per-adapter / per-endpoint-group / per-component items so the
   estimate has a real upper bound.
4. Consider a defensible staged scope: Phases 0–3 plus documents-only output and a by-hand list is a
   useful product that never submits anything, ships far sooner, and carries none of Area A's risk. The
   spec already contains it as D-3.

### m-10 · MINOR · §18 citation hygiene

§18 attributes `claude-haiku-4-5-20251001` to `langchain/models.md §1053`. In the supplied subset that
exact string appears in `lc-middleware__custom.md` (§724, §745); `models.md` carries
`claude-sonnet-4-6`. The full 104-page knowledge base may well contain it where claimed, so this is not
a false verification — but §18 is a table whose value is that a reader can check it, and one bad line
number costs more than it saves. Re-derive §18's citations mechanically from a grep script committed to
the repo, so the table can be regenerated and diffed rather than maintained by hand.

---

# Closing verdict

## REJECTED

Not because it is a weak specification — it is a strong one, and much of §8, §9.2, §10 and §13.2
should survive intact into v1.1. It is rejected because the document's confidence outruns its
mechanisms in precisely the three places where this system can hurt a real person, and because the
table that certifies its API correctness contains three demonstrable falsehoods.

### Blocking issues — all must be closed before implementation begins

| # | Issue | Area |
| --- | --- | --- |
| **C-1** | `fill_form`'s multi-page POSTs are irreversible acts outside the submission protocol; §5.3 and §13.6 assert "no POST" | Double submission |
| **C-2** | HITL-2 has no `i_submitted`; `continue` re-runs `fill_form` from the top and falls through to a second click | Double submission |
| **C-3** | `confirmed_not_submitted` authorises a second irreversible submission with less friction than editing one sentence | Double submission |
| **C-4** | Pre-flight `still_active` that cannot reach the posting does not block the click, and the carve-out is unreachable in the case it was written for | Double submission |
| **C-10** | No single-instance guard; reconciliation runs before the port bind and converts live `SUBMITTING` rows into `UNKNOWN_OUTCOME`, feeding C-3 | Double submission |
| **C-5** | The mapper agent runs on `.inner`, bypassing `PromptGuard`, `BudgetGate` and `SpendLedger` | Fabrication / privacy / budget |
| **C-6** | `kind="context"` claims escape C9, C10 and C11 entirely | Fabrication |
| **C-7** | Answer-sheet and `learned` values reach employers but are structurally invisible to the HITL-5 reviewer | Fabrication / review |
| **C-8** | Provenance anchored to derived positional keys over a master with no ids; fixing it is left optional in Q-O | Fabrication / audit |
| **C-11** | No `submission_enabled` master switch, which the test plan's own go-live gate presumes | Operational |

Plus four MAJORs that must be closed in the same pass because they change the same code:
**M-1, M-2, M-3** (the three false `[UNVERIFIED]` entries — TR-2 is not satisfied until §18 is
re-derived) and **M-15** (make "nothing ships unchecked" a database trigger, as its sibling invariant
already is).

### Counts

| Severity | Count |
| --- | --- |
| **CRITICAL** | 10 |
| **MAJOR** | 24 |
| **MINOR** | 12 |
| **Total** | 46 |

Acceptance criteria unsatisfiable as designed: **14 of 277**, nine of them inside the AF and ID groups
that the test plan names as the gate for enabling real submission.

### The single most dangerous flaw

**C-10 feeding C-3.** Every other finding is a hole to be patched; this pair is a machine for producing
double submissions out of ordinary Windows behaviour.

A hung process, a Task Scheduler restart, a second `jobagent serve` — none of them exotic. The second
instance runs §9.6 before it discovers the port is taken, and flips a live `SUBMITTING` row (a click
dispatched seconds ago, evidence still being captured) to `UNKNOWN_OUTCOME`. The human receives a
notification saying the outcome is unknown and to check the ATS. He checks. The confirmation email has
not arrived. He clicks `confirmed_not_submitted` — one click, no confirmation text, no waiting period,
no warning that the consequence is irreversible — and the system does exactly what it was designed to
do: returns to `APPROVED`, increments `submit_attempt`, re-runs pre-flight, and submits a second
application to a real employer under a real name.

Every layer behaves correctly. The protocol in §9 is not defeated; it is *fed*. That is what makes it
the most dangerous flaw in the document: it is invisible to the design's own safety argument, because
the design treats `UNKNOWN_OUTCOME` as an input and never asks what manufactures it.

### Can one person safely operate this system?

**Not as specified. Yes, with conditions, after the blocking issues are closed — and only in a reduced
form at first.**

The honest assessment has three parts.

*The machine can be made safe.* None of the eleven CRITICALs is architectural. Every one has a concrete,
bounded fix listed above; most are a day's work. The submission protocol, the fact ledger, the
plan-not-prose generator and the tracker state machine are the right structures, and they were designed
by someone who understood what could go wrong. Closing the eleven is a matter of finishing the argument,
not restarting it.

*The human cannot be made safe by measurement alone.* The design's answer to rubber-stamping is
telemetry: `review_seconds`, a median, a flag in a report the reviewer writes for himself. Meanwhile the
primary approve key advances to the next application, approval is reachable from tab 1 without ever
rendering tab 3, the undo window is five seconds and is left behind by the very keystroke that starts
it, and the values actually sent to employers are hidden from the person certifying them. One person
reviewing fifteen applications a day, every day, will converge on the cheapest motion the interface
permits. That is not a character flaw; it is what interfaces do. Until Approve costs something
proportionate to its consequence — tabs rendered, values visible, next-item navigation separated from
approval — the last line of defence is the one the spec itself rates **Medium** residual risk, and it is
the line that both Area A and Area B ultimately fall back on.

*The scope is wrong for one person.* Six to nine months of solo work, with the question "is there
anything here to apply to?" answered in month four, on a project whose purpose is to get its author
employed. The spec already contains a safer product: Phases 0–3 plus D-3's documents-only mode and the
by-hand list. That system tailors, verifies, prepares and hands over — and never clicks. It ships
months earlier, it cannot double-submit because it cannot submit, and it turns the entire Area A risk
surface into a deliberate v2 decision made with real operating experience rather than a v1 assumption.

**Recommendation:** close the eleven blocking issues and the four coupled MAJORs; answer Q-B, Q-D, Q-F,
Q-I and Q-K before Phase 3; run the two-day discovery spike before committing to Phase 4; and ship the
non-submitting product first. Enable real submission only behind `submission_enabled`, at one
application per day, with the AF and ID groups at 100% and no waivers — which is what the test plan
already says, and which this specification does not yet make possible.

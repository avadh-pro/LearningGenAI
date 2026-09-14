# JobAgent — UI/UX Design

**Project:** Autonomous AI/ML Job Search & Application Agent
**Owner:** Avadh Dobariya
**Input:** `REQUIREMENTS.md` v0.4 (approved for spec)
**Status:** Draft for spec consumption
**Version:** 0.1 · 2026-09-14

> This document designs the **experience** of the JobAgent dashboard. It says what the user sees,
> where it lives, how it behaves, and which requirement each element exists to satisfy. It does
> not say how it is built. The technical specification consumes §6 (the FR → UI component map,
> required by FR-13.2) directly.

---

## 0. Design stance

Six decisions govern everything below. They are stated once here so the rest of the document
can be specific instead of defensive.

| # | Decision | Why |
| --- | --- | --- |
| D-1 | **The product is a review queue. Everything else is evidence.** | HITL-5 makes reviewing 10–20 applications the only daily interaction that matters. Discovery, scoring and tracking exist to make each review decision fast and defensible. |
| D-2 | **A review is budgeted at 60 seconds.** 5 s orient · 20 s resume · 25 s cover letter · 5 s answers · 5 s decide. | 15 reviews × 60 s = 15 minutes/day. Past that the ritual gets skipped, approvals age, and postings close. The Review screen (§3.4–3.8) is designed against this budget line by line. |
| D-3 | **Show what changed, not what exists.** The resume tab defaults to a **diff against the master**; the cover letter carries **evidence markers** to the resume line each claim rests on. | Avadh knows his own resume. Reading a full page to find three reordered bullets is the single biggest waste of time in the whole system. Diff + trace is also how T-2 / T-5 become *verifiable* in 20 seconds instead of asserted. |
| D-4 | **Keyboard-first, mouse-optional.** Every action on the daily path has a single-key binding. | One technical user, a local machine, a repetitive daily task. |
| D-5 | **Three visibility tiers, one dashboard.** Tier A (daily) · Tier B (investigation) · Tier C (system). FR-13.1 is met by giving every requirement a home — not by putting every requirement on the front page. | Sixty-odd requirements with a counter each would bury the one number that matters (pending reviews). |
| D-6 | **No bulk approve. Ever.** Bulk reject, bulk skip, bulk dismiss-expired are fine. | C-3 (irreversible) + HITL-5 (full review, no spot-checking) make bulk approval a requirement violation dressed as a convenience. See §5.4. |

**Visual register.** Dense, monochrome-neutral, one accent colour for the primary action, tier
colours for scores (Tier 1 / Tier 2 / Tier 3 / rejected), monospace for identifiers and diffs.
No cards-with-shadows, no illustrations, no empty-state mascots. It should feel like a good
CI dashboard, not a consumer app. Light and dark theme both supported; dark is default because
the review screen is text-heavy and read in the morning.

**Vocabulary used throughout.**

| Term | Meaning |
| --- | --- |
| **Run** | One scheduled execution (09:00 daily) or one manual trigger. Has a date, stages, cost. |
| **Job** | A deduplicated posting (FR-2.1). Has a score, verdict, source cluster. |
| **Application** | A Job that passed threshold and has (or is getting) tailored documents. Has a gate state. |
| **Gate** | A HITL pause. Approval (HITL-1/5), Blocked (HITL-2), Question (HITL-3/4). |
| **Fallback** | A Job the agent could not auto-apply to (FR-1.9). Has a manual state. |
| **Verdict** | Machine outcome for a Job: `queued` · `deferred (over ceiling)` · `by hand` · `rejected: <rule>` · `expired` · `duplicate`. |

---

## 1. User journeys

Times are targets, not estimates. Each journey names the screens it crosses (§3 numbering).

### J1 — The daily review ritual (primary — optimise everything for this)

**Trigger:** Telegram message ~09:40: *"14 applications ready for review (est. 13 min)."*
Avadh sits at the PC sometime between 09:40 and lunch.

| Step | Screen | What happens | Budget |
| --- | --- | --- | --- |
| 1 | Dashboard §3.2 | Opens `localhost` bookmark. First thing on screen: **14 waiting · 3 carried over · est. 13 min · [Start review ⏎]**. Glances at *Needs you now* (0) and spend ($3.82). Presses Enter. | 10 s |
| 2 | Review §3.4 | Lands on the **oldest carry-over first** (O-5). Left rail: company, role, score 91 Tier 1, watch-flags (travel 25%). Centre: resume **diff** — 6 changes highlighted. Skims them. | 20 s |
| 3 | Review §3.5 | Presses `2`. Cover letter, four short paragraphs, each claim footnoted `[1]…[11]` to a resume line. Reads it as prose; hovers one marker to check the "20+ hrs/week" figure. | 25 s |
| 4 | Review §3.6 | Presses `3`. Four screening answers: 2 from resume, 1 from answer sheet (masked: *Expected CTC · from answer sheet*), 1 generated. Reads the generated one. | 5 s |
| 5 | Review §3.4 | Right panel shows pre-flight 12/12 green. Presses `A`. Toast: **"Approved — submitting in 5 s · Z to undo"**. Screen advances to 2/14 automatically. | 5 s |
| 6 | Review §3.7 | Application 5: cover letter paragraph 2 overstates ("led a team of 4") — resume says *mentors 4 engineers*. Presses `E`, clicks into the paragraph, changes one word, `Ctrl+Enter`. Trace re-validates; pre-flight still green. Presses `A`. | +30 s |
| 7 | Review §3.8 | Application 9: a "Senior ML Engineer" posting where the JD is mostly classical ML. Presses `R`, `1` (*Not relevant — scoring should have caught this*), Enter. Job moves to tracker as `rejected by Avadh`. | 10 s |
| 8 | Review | Application 12 flagged **EXPIRED** (posting closed since Friday). Right panel offers only `X Dismiss expired`. Presses `X`. | 3 s |
| 9 | Queue §3.3 | Queue empty. Screen shows the completion state: **13 approved · 1 rejected · 1 expired · 12 submitted, 1 submitting…** with the one in progress ticking. Any submission that hits a CAPTCHA will appear under *Needs you now* and ping Telegram. | — |
| 10 | Dashboard | Notices **By hand 6**. Decides whether to do those now or at lunch (J3). | — |

**Total for 14 applications: ≈ 14 minutes.** The design must protect this number; every feature
added to the Review screen is measured against it.

### J2 — Investigating why a job was rejected

**Trigger:** A friend mentions Harvey is hiring an "Applied AI Engineer — India". Avadh
wonders whether JobAgent saw it and, if so, why it isn't in his queue.

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Audit log → Jobs §3.10 | Types `harvey` in the filter. One row: **Harvey · Applied AI Engineer · 74 · rejected: FR-4.2 mandatory qualification**. |
| 2 | Job detail §3.13 | Opens it. Score breakdown shows 74 (Tier 3), but the **Hard rules** panel shows `FR-4.2 ✗ — "JD, US law degree or 3+ years legal-tech required" · quoted from JD line 41`. Below it the dedup cluster shows the same posting seen on LinkedIn and Greenhouse (merged). |
| 3 | Job detail | Reads the per-dimension reasoning; agrees with the rejection. Closes. *(If he disagreed with a soft rejection — score < 70 but no hard rule — the **Promote to queue** action is available and logged as an override. Hard-rule rejections have no override; the button is absent and the panel says why — FR-4.1, FR-4.3.)* |

**Target: under 90 seconds from question to answer.** The critical requirement is that the
rejection reason is quoted from the JD, not paraphrased — otherwise Avadh has to open the JD
himself, which doubles the time.

### J3 — Handling a job the agent could not apply to

**Trigger:** Dashboard shows **By hand 6**. Four are Naukri/LinkedIn discovery-only postings
(Q-3), one hit a CAPTCHA on a Workday tenant, one has an unsupported custom form.

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Apply by hand §3.11 | Sorted by score. Each row: company, role, score, **reason** (`discovery-only: Naukri`), a link, and **download chips** for the tailored resume PDF and cover letter the agent already prepared. |
| 2 | Browser | Clicks the link (opens in new tab), applies on Naukri by hand, uploading the downloaded PDF. |
| 3 | Apply by hand | Back on the row, presses `M` (*applied manually*). Row greys, moves to the *Done* group, and a **tracker entry is created** with channel `manual`, today's date, resume version. This is what prevents the same job being re-queued tomorrow (FR-2.2). |
| 4 | Apply by hand | The Workday CAPTCHA row has a different affordance: **`Resume with agent`** — reopens the automation with the browser visible so Avadh solves the CAPTCHA and the agent continues (HITL-2, TR-6). |
| 5 | Apply by hand | Skips the last two with `S` + reason. They stay filterable under *Skipped* indefinitely (Q-9). |

**UX problem, stated plainly:** FR-6.1 only requires tailoring "where a resume upload is
allowed". If the agent does *not* prepare documents for fallback jobs, J3 becomes "do the whole
application yourself", and Avadh will stop doing them. **Recommendation to the spec:** tailor for
every fallback job scoring ≥ 80, and make the downloads the centre of this screen. This is a
design recommendation that slightly exceeds the letter of FR-6.1; flagged in §8.

### J4 — Adjusting settings and the answer sheet

**Trigger:** Avadh receives confirmation that he holds no EU permit but *does* want to consider
Dubai roles that require relocation. He also wants to raise the daily ceiling from 15 to 18.

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Settings → Answer sheet §3.14 | Values are **masked** by default (`₹•• LPA`); a single *Reveal* toggle shows them. Sets *Relocation stance* to `Yes — Dubai/UAE only`. Beside *Work authorisation* an **impact line** reads: *"Under the current setting 23 jobs were rejected for sponsorship in the last 30 days — 19 Europe, 4 Canada."* He leaves it at the default. |
| 2 | Settings → Targets §3.15 | Moves the *Daily ceiling* from 15 to 18. The label beneath says *"Ceiling, not quota — the agent applies to fewer when fewer qualify (FR-9.2)."* |
| 3 | Settings | Presses `Ctrl+S`. Toast: *"Saved · takes effect next run (09:00 tomorrow) · [Run now]"*. |

The answer sheet screen is the only place §2.1 values are ever rendered, and they are never
rendered in a log, toast, report or Telegram message (§2.1 sensitivity rule).

### J5 — Reviewing the day's report

**Trigger:** Telegram digest at ~09:45 (after the run) or, if he prefers, end of day.

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Telegram §7 | Digest: discovered / evaluated / queued / submitted / by hand / rejected / spend, plus the top 3 matches with one-line *why*. Link to the full report. |
| 2 | Reports §3.17 | Full FR-11.1 report for the date, with every section as a collapsible block. *Rejected with reasons* is grouped by rule so 106 rejections read as 8 groups. *Items needing attention* links straight into the gate that needs him. |
| 3 | Reports | Uses the date strip at the top to compare with yesterday; the *Trend* strip shows 14 days of discovered / queued / submitted / spend. |

### J6 — Unblocking a live run (HITL-2)

**Trigger:** Telegram at 09:31: *"Blocked — Careem (Workday) needs login/OTP. Run continues with
other jobs. [Open]"*. This is the gate that, if nobody sees it, stalls an application forever.

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Dashboard §3.2 | *Needs you now* card is red with one row: **Careem · Senior AI Engineer · Workday login · blocked 12 min**. |
| 2 | Needs-you-now panel §3.19 | Presses Enter. Panel shows: what the agent was doing, the last screenshot of the browser, and **`Take over browser`** which brings the automated browser window to the foreground. Avadh logs in. Presses **`Continue`**; the agent resumes from the exact step (HITL-R5 — no step re-executed). |
| 3 | Panel | Alternative: **`Send to by-hand`** if he'd rather finish manually, or **`Abandon`**. |

### J7 — Answering a genuinely novel question (HITL-3 / HITL-4)

**Trigger:** A Lever form asks *"Have you ever been terminated from employment? Explain."*
Not on the answer sheet, not derivable from the resume (FR-8.3, T-4).

| Step | Screen | What happens |
| --- | --- | --- |
| 1 | Needs-you-now §3.19 | Row: **Postman · Senior AI Platform Engineer · Question needs your answer**. The panel shows the question verbatim, the field type (free text, 500 chars), and what the agent *would not* do (*"Not answerable from resume or answer sheet — halted per FR-9.4"*). |
| 2 | Panel | Avadh types the answer. A checkbox **"Add to answer sheet as `employment_termination`"** is ticked by default, so the question never halts again (HITL-R3). Presses `Ctrl+Enter`. Application proceeds to tailoring and then to the normal approval queue. |

---

## 2. Information architecture

### 2.1 Navigation tree

```
JobAgent  (local web app · http://localhost:<port>)
│
├─ Today                    /                      Tier A   Dashboard: CTA, funnel, needs-you-now, spend
├─ Queue            [14]    /queue                 Tier A   Approval queue (HITL-1/5), carry-over first
│    └─ Review              /queue/:appId          Tier A   Single application: resume · letter · answers · decide
├─ By hand          [6]     /by-hand               Tier A   Manual-fallback list (FR-1.9) — a pinned view of the audit log
├─ Audit log                /audit                 Tier B   Per-run: Sources · Queries · Jobs (FR-1.8)
│    ├─ Sources             /audit/:runDate/sources
│    ├─ Queries             /audit/:runDate/queries
│    └─ Jobs                /audit/:runDate/jobs?verdict=&source=&tier=&geo=&fallback=
├─ Tracker                  /tracker               Tier B   Every application, durable (FR-10)
├─ Jobs                     /jobs/:jobId           Tier B   Job detail: score breakdown, rules, dedup cluster, JD
├─ Reports                  /reports/:date         Tier B   Daily report (FR-11), 14-day trend
├─ Runs                     /runs/:runDate         Tier C   Run console: stages, per-stage cost, traces, source health
└─ Settings                 /settings              Tier C
     ├─ Answer sheet        /settings/answers               §2.1 values (masked), work authorisation + impact
     ├─ Targets             /settings/targets               Daily ceiling, thresholds (display), geography priority
     ├─ Models & budget     /settings/models                Per-stage model (TR-10), ceiling, soft alert (TR-12)
     ├─ Sources             /settings/sources               Enable/disable, board policy badges (Q-3)
     ├─ Schedule            /settings/schedule              09:00, run now, rollover policy (O-5)
     ├─ Notifications       /settings/notifications         Telegram chat, message types, base URL for links
     └─ Data & secrets      /settings/data                  Storage path, retention (Q-9), key sources (TR-8), export

Overlays (no route of their own)
├─ Needs you now            slide-over from any screen      HITL-2 handoff · HITL-3/4 question
├─ Reject reason            overlay on Review
├─ Keyboard help            `?` anywhere
└─ Command palette          `Ctrl+K` — jump to company / job / setting
```

Nav badges: **Queue** shows pending count; **By hand** shows `pending` count. Both go plain
when zero. A red dot on the app title appears only for *Needs you now* items — it is the one
interrupt-class signal in the UI.

### 2.2 Global chrome (present on every screen)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ JobAgent ●   Run 14 Sep · finished 09:41 · 212 found   Next 09:00 Tue   LLM $3.82 / $100 ▕██▏ soft $5  ⌨ ? │
├────────────┬─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Today     │                                                                                              │
│  Queue  14 │                                                                                              │
│  By hand 6 │                                                                                              │
│  Audit log │                          ( screen content )                                                  │
│  Tracker   │                                                                                              │
│  Reports   │                                                                                              │
│  Runs      │                                                                                              │
│  Settings  │                                                                                              │
└────────────┴─────────────────────────────────────────────────────────────────────────────────────────────┘
```

The header strip is the permanent home of three system-level requirements so they never have to
compete for dashboard space: **run state** (FR-12.1), **next run** (Q-6) and **running LLM spend
against ceiling with the soft-alert mark** (FR-13.3, TR-11, TR-12). The spend meter turns amber
past $5 and red past $50; the header run dot is grey (idle), pulsing blue (running), green
(finished), amber (finished with source failures — NFR-4), red (failed / missed).

---

## 3. Wireframes

All wireframes use real-looking data from the same fictional run of **Monday 14 Sep 2026**, so
counts reconcile across screens. Companies are illustrative.

### 3.1 Reconciling numbers for the sample run

```
Discovered 212 → Unique 143 (69 merged as duplicates)
             → Rejected 106  (hard rule 41 · score < 70 58 · visa/sponsorship 7)
             → Passed ≥ 70: 37
                  → By hand 6        (Naukri 3 · LinkedIn 1 · CAPTCHA 1 · unsupported form 1)
                  → Auto-capable 31
                        → Ceiling 15 − 3 carry-over = 12 slots
                        → Tailored 11 · 1 failed ATS check (needs attention)
                        → Deferred (over ceiling) 19 — re-evaluated tomorrow if still active
Queue this morning: 3 carry-over + 11 new = 14 (1 carry-over now flagged expired)
```

### 3.2 Daily Dashboard — `/`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ JobAgent ●   Run 14 Sep · finished 09:41 · 212 found   Next 09:00 Tue   LLM $3.82 / $100 ▕██▏ soft $5  ⌨ ? │
├────────────┬─────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▸Today     │  Monday 14 September 2026                                                                    │
│  Queue  14 │                                                                                              │
│  By hand 6 │  ┌─────────────────────────────────────────────────────────────────────────────────────────┐ │
│  Audit log │  │  14 applications waiting for your review                       est. 13 min             │ │
│  Tracker   │  │  3 carried over from Fri 11 Sep (oldest 3 days) · 11 new · 1 flagged expired           │ │
│  Reports   │  │                                                             [ Start review     ⏎ ]     │ │
│  Runs      │  └─────────────────────────────────────────────────────────────────────────────────────────┘ │
│  Settings  │                                                                                              │
│            │  NEEDS YOU NOW ─────────────────────────────────────────────────────────────────────── 1 ──  │
│            │  ● Postman · Senior AI Platform Engineer · question needs your answer · 22 min      [Open ⏎] │
│            │                                                                                              │
│            │  TODAY'S FUNNEL ────────────────────────────────────────────────────────────────────────────  │
│            │   Discovered   Unique    Rejected   Passed ≥70   Tailored   Awaiting you   Submitted         │
│            │      212  ──►   143  ──►   106   ──►   37    ──►   11   ──►     14     ──►     0             │
│            │              −69 dupes   hard 41           by hand 6   1 failed ATS                          │
│            │                          <70  58           deferred 19  (over ceiling 15)                    │
│            │                          visa  7                                                             │
│            │                                                                                              │
│            │  ┌── BY HAND ───────────── 6 pending ──┐  ┌── SOURCES ─────────────────── 7 / 8 ok ─────────┐ │
│            │  │ Naukri 3 · LinkedIn 1 · CAPTCHA 1   │  │ ✓ Greenhouse 41  ✓ Lever 18  ✓ Workday 22      │ │
│            │  │ Unsupported form 1                  │  │ ✓ Career pages 37  ✓ Wellfound 9  ✓ LinkedIn 48│ │
│            │  │ Best: Sprinklr 88 · Uniphore 84     │  │ ✓ Naukri 31   ⚠ Indeed — 429 rate-limited,     │ │
│            │  │                    [Open list  B ]  │  │   partial (6 of ~20 pages)        [Retry]      │ │
│            │  └─────────────────────────────────────┘  └────────────────────────────────────────────────┘ │
│            │                                                                                              │
│            │  ┌── TOP MATCHES TODAY ─────────────────────────────────────────────────────────────────────┐ │
│            │  │ 94  Glean         Senior Forward Deployed Engineer      Bengaluru · Hybrid   in queue   │ │
│            │  │ 91  Sierra        Forward Deployed AI Engineer          Remote (India ok)    in queue   │ │
│            │  │ 89  Careem        Senior AI Engineer, Agentic Platforms Dubai · Onsite       in queue   │ │
│            │  │ 88  Sprinklr      Senior GenAI Engineer                 Gurugram             by hand    │ │
│            │  │ 87  Icertis       AI Solutions Architect                Pune · Hybrid        in queue   │ │
│            │  └──────────────────────────────────────────────────────────────────────────────────────────┘ │
│            │                                                                                              │
│            │  ┌── SPEND TODAY ──────────────────────────────────┐  ┌── LAST 14 DAYS ─────────────────────┐ │
│            │  │ $3.82 of $100 ceiling · soft alert $5           │  │ submitted  ▂▃▅▃▄▂▁▅▆▃▄▅▃▂   47      │ │
│            │  │ screen $0.41 · analyse $0.96 · tailor $2.45     │  │ queued     ▃▅▆▅▅▃▁▆▇▅▅▆▅▄   61      │ │
│            │  │ [Run console]                                   │  │ spend/day  ▂▂▃▂▂▂▁▃▃▂▂▃▂▂   $2.9 avg│ │
│            │  └─────────────────────────────────────────────────┘  └─────────────────────────────────────┘ │
└────────────┴─────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- **The primary CTA is the only large element.** Its estimate is `pending × 55 s` tuned by
  Avadh's measured median review time once there is data.
- **The funnel is the daily FR-visibility spine.** Each number is a link into the audit log
  pre-filtered to that verdict. "Deferred 19 (over ceiling)" makes FR-9.2's ceiling behaviour
  visible without implying a shortfall.
- **The ceiling is never drawn as a progress bar.** A bar to 15 with 11 filled reads as "4
  short"; FR-9.2 says the number is a ceiling, and the UI must not nag toward it.
- *Needs you now* collapses to a single grey line when empty (*"Nothing blocked. Last handoff:
  Fri 11 Sep 09:27 — Workday login (Careem), resolved in 4 min."*).

### 3.3 Approval Queue — `/queue`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Queue · 14 waiting                        Sort: carry-over first ▾   Filter: all ▾         [Start review ⏎]│
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  CARRIED OVER (3) ── queued ahead of today's batch (O-5) ─────────────────────────────────────────────── │
│  Age  Score  Company        Role                                  Location            Via         Docs   │
│▸ 3d   87     Icertis        AI Solutions Architect                Pune · Hybrid       Greenhouse  R L Q3 │
│  3d   82     Whatfix        Senior LLM Engineer                   Bengaluru           Lever       R L Q2 │
│  3d   79 ⚠   Yellow.ai      Senior Agentic AI Engineer            Remote · India      Greenhouse  R – Q4 │
│       EXPIRED — posting closed 13 Sep · only action: dismiss                                   [X Dismiss]│
│                                                                                                          │
│  TODAY (11) ─────────────────────────────────────────────────────────────────────────────────────────── │
│  0d   94  T1 Glean          Senior Forward Deployed Engineer      Bengaluru · Hybrid  Greenhouse  R L Q4 │
│  0d   91  T1 Sierra         Forward Deployed AI Engineer          Remote (India ok)   Career page R L Q6 │
│  0d   89  T2 Careem         Senior AI Engineer, Agentic Platforms Dubai · Onsite ✈    Workday     R L Q5 │
│  0d   86  T2 Druva          Senior GenAI Engineer                 Pune                Lever       R – Q3 │
│  0d   85  T2 Observe.AI     Staff AI Engineer (LLM Platform)      Bengaluru           Greenhouse  R L Q2 │
│  0d   84  T2 Property Finder Lead AI Engineer                     Dubai · Hybrid ✈    Workday     R L Q4 │
│  0d   83  T2 Innovaccer     Senior Applied AI Engineer            Noida · Hybrid      Greenhouse  R L Q3 │
│  0d   81  T2 Kore.ai        Senior AI Platform Engineer           Hyderabad           Career page R – Q2 │
│  0d   80  T2 Freshworks     Senior AI Engineer — Freddy Copilot   Chennai · Remote    Career page R L Q5 │
│  0d   76  T3 Zeta           Senior ML Engineer (LLM Apps)         Bengaluru           Greenhouse  R L Q3 │
│       Tier 3 — "apply only if no obvious gaps": 1 gap flagged (Kubernetes) — review with care             │
│  0d   72  T3 Sirion         Applied AI Engineer                   Gurugram            Lever       R L Q4 │
│                                                                                                          │
│  NOT IN QUEUE ────────────────────────────────────────────────────────────────────────────────────────── │
│  1 failed tailoring (ATS check 13/15 — letter-spacing) → Needs attention · Uniphore 84    [Retry tailor] │
│  19 deferred over ceiling · 6 by hand · 106 rejected                                        [Audit log →] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  J/K move · ⏎ open · X dismiss expired · Shift+R bulk reject selected · Space select · ? help            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- **Docs column** `R L Qn` = tailored resume ready · cover letter ready (– when the form has no
  letter field, FR-7.1 "when requested") · n screening answers prepared. It tells Avadh how long
  the row will take before he opens it.
- `✈` marks international roles; the row's Review screen will carry the visa/sponsorship line
  (FR-1.3a). Tier 3 rows carry the FR-3 rubric caveat inline so HITL-6 is folded into HITL-5
  visibly (O-3).
- The queue is a list, not the workspace. The expected path is `⏎` on the first row and never
  coming back until the queue is empty.

### 3.4 Application Review — Resume tab (the most important screen)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ← Queue   3 of 14    K prev · J next                    Glean · Senior Forward Deployed Engineer   Tier 1  94 │
├──────────────────────────┬───────────────────────────────────────────────────────┬───────────────────────────┤
│ JOB                      │ [1] Resume · diff    [2] Cover letter    [3] Answers  │ DECISION                  │
│                          │                                                       │                           │
│ Glean                    │  6 changes vs master (2026-09-12)      D: full view   │ Pre-flight FR-9.1  12/12  │
│ Senior Forward Deployed  │                                                       │ ✓ company    ✓ job        │
│ Engineer                 │  PROFESSIONAL SUMMARY                                 │ ✓ active     ✓ score 94   │
│ Bengaluru · Hybrid 3d/wk │  − Senior AI Solution Engineer with 4+ years building │ ✓ not dup    ✓ facts 49/49│
│ Greenhouse · auto-apply  │    enterprise AI automation across 25+ deployments.   │ ✓ no fabrication          │
│ Posted 13 Sep · active   │  + Senior AI Solution Engineer with 4+ years          │ ✓ letter tailored         │
│                          │    delivering production GenAI for enterprise         │ ✓ answers    ✓ contact    │
│ SCORE 94 ───────────── T1│    customers end-to-end — requirements to production  │ ✓ location   ✓ no false   │
│ Skills       ████████ 29 │    support — including an MCP server that lets        │               qualification│
│ AI/LLM exp   ████████ 24 │    Claude / ChatGPT / Cursor call governed tools.     │ ✓ ATS 3-parser 15/15      │
│ Seniority    ███████  14 │                                                       │                           │
│ Domain       ████████ 10 │  SKILLS  reordered · nothing added                    │ Evidence trace  T-5       │
│ Company      ███████   9 │  ~ ↑ Agentic AI · MCP · RAG · LLM Integrations        │ 11 claims · 11 traced ✓   │
│ Location     ██████    4 │  ~ ↑ Python · LangChain · LangGraph                   │                           │
│ Keywords     ████████  4 │  ~ ↑ Jira · Slack · Salesforce · Zoho · Datadog · MS  │ Resume version            │
│ [Full breakdown →]       │      Teams/Graph                                      │ master 2026-09-12 →       │
│                          │  ~ ↓ Cloud & DevOps (unchanged content)               │ tailored glean-a1 (v1)    │
│ WATCH                    │                                                       │                           │
│ ⚠ Travel up to 25%       │  EXPERIENCE · Krista Software · Senior AI Solution    │ ┌───────────────────────┐ │
│   (JD line 18)           │  Engineer · Aug 2022 – Present                        │ │  A   Approve & next   │ │
│ ✓ GenAI substantial      │  ~ ↑ moved to #1: Built a production MCP server …     │ └───────────────────────┘ │
│   (FR-1.6 pass)          │  ~ ↑ moved to #2: Architected 25+ enterprise AI …     │ [ E  Edit ]  [ R Reject ] │
│ ✓ India role — no visa   │  · (unchanged) Core engineer on AIQA enterprise RAG … │ [ P  Postpone ]           │
│ · No gaps flagged        │  · (unchanged) AI Risk & Compliance Sync Engine …     │                           │
│                          │                                                       │ Age 0d · found today      │
│ WHY IT MATCHES           │  PROJECTS · EDUCATION · AWARDS — unchanged            │ Submits via Greenhouse    │
│ FDE role with explicit   │                                                       │ Est. submit ≈ 45 s        │
│ "customer-facing LLM     │                                                       │                           │
│ deployments" and "MCP    │                                                       │ Approvals today  2 / 15   │
│ / tool-calling" in JD;   │                                                       │ ceiling                   │
│ 25+ enterprise deploy-   │                                                       │                           │
│ ments is the exact ask.  │  [ Open JD ↗ ]   [ Open tailored PDF ↗ ]              │                           │
└──────────────────────────┴───────────────────────────────────────────────────────┴───────────────────────────┘
│  A approve · E edit · R reject · P postpone · 1/2/3 tabs · D diff/full · J/K next/prev · O open JD · ? help │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Design notes — this screen is where the 60-second budget lives:

- **Left rail is orientation (5 s).** Score bars are the FR-3.1 rubric, reasoning is one click
  away, *Watch* lists only things the agent thinks Avadh should know before approving: travel
  (FR-1.7), GenAI-substance check (FR-1.6), visa/sponsorship (FR-1.3a), Tier 3 gaps.
- **Centre is a diff by default (20 s).** Three change classes: `−/+` rewritten text (summary),
  `~ ↑↓` reordered (skills, bullets), `·` unchanged and collapsed. The **"nothing added"** label
  on Skills is a T-1/T-2 assertion the agent makes and the diff proves: a `+` line inside Skills
  would be a fabrication and the pre-flight *facts 49/49* check would fail.
- **Right panel is the decision (5 s).** Pre-flight is FR-9.1's twelve verifications, each a
  green tick or a red cross with the reason. Approve is disabled when any is red, and the panel
  says which. *ATS 3-parser 15/15* is FR-6.4's re-verification. *Evidence trace 11/11* is T-5.
- **Approve & next is the default action.** There is no confirmation modal — the 5-second undo
  toast (§5.1) is the safety net. A modal on every one of 15 approvals would cost 15 × 3 s and,
  worse, train the reflex of clicking through.
- **Approvals today 2 / 15 ceiling** is deliberately small and in the corner: information, not a
  goal.

### 3.5 Application Review — Cover letter tab

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ← Queue   3 of 14    K prev · J next                    Glean · Senior Forward Deployed Engineer   Tier 1  94 │
├──────────────────────────┬───────────────────────────────────────────────────────┬───────────────────────────┤
│ (job rail as §3.4)       │ [1] Resume · diff    [2] Cover letter ●  [3] Answers  │ EVIDENCE TRACE  T-5       │
│                          │                                                       │                           │
│                          │  Dear Glean Hiring Team,                    218 words │ [1] Krista · role line    │
│                          │                                                       │ [2] Summary · 4+ years    │
│                          │  I'm applying for the Senior Forward Deployed         │ [3] Krista bullet 1 · 25+ │
│                          │  Engineer role. For the past four years at Krista     │     enterprise AI         │
│                          │  Software I have owned enterprise AI solutions        │ [4] Krista bullet 1 ·     │
│                          │  end-to-end — from the first scoping call through     │     up to 80%             │
│                          │  architecture, integration, demos and production      │ [5] Krista bullet 2 · MCP │
│                          │  support[1] — which is the shape of the FDE role      │     server, JSON-RPC 2.0  │
│                          │  you describe.[2]                                     │ [6] JD line 22 (context,  │
│                          │                                                       │     not a claim)          │
│                          │  Concretely: I architected 25+ enterprise AI          │ [7] Krista bullet 3 ·     │
│                          │  automation solutions[3] that cut manual workflows    │     AIQA hybrid retrieval │
│                          │  by up to 80%[4], and built a production MCP server   │ [8] Krista bullet 4 ·     │
│                          │  over JSON-RPC 2.0 that lets Claude, ChatGPT and      │     20+ hrs/week          │
│                          │  Cursor call governed enterprise tools[5] — directly  │ [9] Skills · Jira, Slack, │
│                          │  relevant to your "agents that act inside customer    │     Salesforce, Datadog   │
│                          │  systems" mandate.[6]                                 │ [10] Summary · mentors 4  │
│                          │                                                       │ [11] Awards · 2× Shining  │
│                          │  On the retrieval side I was a core engineer on       │     Star                  │
│                          │  AIQA, an enterprise RAG platform with 50+ ingestion  │                           │
│                          │  formats and hybrid lexical + vector retrieval[7],    │ All 11 claims resolve to  │
│                          │  and I shipped a compliance sync engine that removed  │ a resume line.  ✓         │
│                          │  20+ hours a week of manual reconciliation[8]. I've   │                           │
│                          │  integrated LLMs with Jira, Slack, Salesforce and     │ Hover a marker to see the │
│                          │  Datadog[9] and mentor four engineers[10].            │ source; click to jump.    │
│                          │                                                       │                           │
│                          │  I'd welcome the chance to show how this maps onto    │ ┌───────────────────────┐ │
│                          │  Glean's customer deployments.                        │ │  A   Approve & next   │ │
│                          │                                                       │ └───────────────────────┘ │
│                          │  Avadh Dobariya · avadhdobariya@gmail.com             │ [ E  Edit ]  [ R Reject ] │
│                          │                                                       │ [ P  Postpone ]           │
│                          │  ┌─ hover [8] ───────────────────────────────────┐    │                           │
│                          │  │ resume-ats.html › Krista › bullet 4           │    │                           │
│                          │  │ "AI Risk & Compliance Sync Engine — eliminated│    │                           │
│                          │  │  20+ hrs/week of manual reconciliation"       │    │                           │
│                          │  └───────────────────────────────────────────────┘    │                           │
└──────────────────────────┴───────────────────────────────────────────────────────┴───────────────────────────┘
```

Notes:

- Word count is shown because FR-7.1 says *concise*; anything over ~300 gets an amber count.
- Markers are unobtrusive superscripts in the real rendering; in the wireframe they are `[n]`.
  An **unresolved** marker (a claim the agent could not trace) renders red and fails pre-flight
  *no fabrication* — Approve is disabled until it is edited out. This is the UI form of T-1/T-5.
- JD-context markers (`[6]`) are visually distinct (grey) because they are not claims about
  Avadh and do not need a resume source.

### 3.6 Application Review — Answers tab

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ (header as §3.4)                                                                                             │
├──────────────────────────┬───────────────────────────────────────────────────────┬───────────────────────────┤
│ (job rail as §3.4)       │ [1] Resume · diff    [2] Cover letter    [3] Answers ●│ DECISION (as §3.4)        │
│                          │                                                       │                           │
│                          │  4 form questions · 2 from resume · 1 answer sheet ·  │ Sources                   │
│                          │  1 generated                                          │ ▣ resume       2          │
│                          │                                                       │ ▣ answer sheet 1          │
│                          │  Q1  Years of experience building LLM applications?   │ ▣ generated    1          │
│                          │      A  4                     ← resume · Krista dates │ ▢ halted       0          │
│                          │                                                       │                           │
│                          │  Q2  Experience with MCP or tool/function calling?    │ Answer-sheet values are   │
│                          │      A  Yes — built a production MCP server (JSON-RPC │ shown as their field name │
│                          │         2.0) enabling Claude/ChatGPT/Cursor to call   │ only. The value is sent   │
│                          │         governed enterprise tools.  ← resume · bullet │ to the form and nowhere   │
│                          │                                                       │ else (§2.1).              │
│                          │  Q3  Expected compensation (INR, annual)?             │                           │
│                          │      A  ‹ Expected CTC · from answer sheet ›  🔒       │                           │
│                          │                                                       │                           │
│                          │  Q4  Why Glean?                               generated│                           │
│                          │      A  Glean's agents have to act inside customers'   │                           │
│                          │         existing systems with permissions intact —     │                           │
│                          │         the same constraint I've solved with a         │                           │
│                          │         governed MCP layer and 25+ enterprise          │                           │
│                          │         deployments at Krista. FDE is the role where   │                           │
│                          │         that experience compounds.           92 words  │                           │
│                          │         [1][3] traced ✓                                │                           │
│                          │                                                       │                           │
│                          │  Fields the form asks that will be filled from your   │                           │
│                          │  profile (no review needed): name · email · phone ·   │                           │
│                          │  LinkedIn · GitHub · location                          │                           │
└──────────────────────────┴───────────────────────────────────────────────────────┴───────────────────────────┘
```

The answer-sheet row shows the **field name, never the value** (§2.1: "never volunteered", "never
logged to a shared surface"). Avadh can reveal it with `Ctrl+Shift+V` if he genuinely needs to
check; the reveal is not persisted.

### 3.7 Application Review — Edit mode (`E`)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ← Queue   5 of 14   EDITING — Ctrl+⏎ save · Esc cancel        Observe.AI · Staff AI Engineer   Tier 2  85    │
├──────────────────────────┬───────────────────────────────────────────────────────┬───────────────────────────┤
│ (job rail)               │ [1] Resume    [2] Cover letter ● editing   [3] Answers│ EDIT                      │
│                          │                                                       │                           │
│                          │  ┌───────────────────────────────────────────────┐    │ Direct edit — type in the │
│                          │  │ Concretely: I architected 25+ enterprise AI   │    │ document. Markers re-     │
│                          │  │ automation solutions[3] that cut manual       │    │ validate on save.         │
│                          │  │ workflows by up to 80%[4], and I led a team   │    │                           │
│                          │  │ of four engineers|                            │    │ ⚠ Claim without source:   │
│                          │  │        ▲ no resume source — will block approve│    │   "led a team of four"    │
│                          │  │                                               │    │   Resume says: "Mentors 4 │
│                          │  └───────────────────────────────────────────────┘    │   engineers" (Summary)    │
│                          │                                                       │   [Use resume wording]    │
│                          │  ── or ask the agent ─────────────────────────────    │                           │
│                          │  ┌───────────────────────────────────────────────┐    │ Version                   │
│                          │  │ Make paragraph 2 shorter and mention LangGraph│    │ observe-b2 v1 → v2 (edit) │
│                          │  │ explicitly. Keep every claim traceable.       │    │                           │
│                          │  └───────────────────────────────────────────────┘    │ On save                   │
│                          │  [ Revise with agent · ≈ $0.04 · ~8 s ]               │ · re-trace claims (T-5)   │
│                          │                                                       │ · re-run pre-flight       │
│                          │                                                       │ · resume edits → re-render│
│                          │                                                       │   PDF + ATS 3-parser check│
│                          │                                                       │                           │
│                          │                                                       │ [ Ctrl+⏎ Save ] [Esc]     │
└──────────────────────────┴───────────────────────────────────────────────────────┴───────────────────────────┘
```

Notes:

- **Two edit modes, one screen.** *Direct edit* for a word or a line — the common case (HITL-R2:
  "fix one line without discarding the application"). *Revise with agent* for structural changes;
  it shows an estimated cost because it spends against the ceiling (TR-11). Neither leaves the
  Review screen, and neither loses the other tabs' content.
- **Live fabrication guard.** As Avadh types a claim the tracer cannot resolve, it is underlined
  and the right panel offers the resume's own wording. Avadh *can* save an untraceable claim
  (it is his letter and he is the source of truth about himself) — but the pre-flight goes red and
  the panel says: *"Approve blocked: 1 untraced claim. If this is true, add it to the master
  resume first (T-1/T-5)."* This is the UI teeth for §6.
- **Resume edits** operate on the tailored HTML's text blocks (not raw HTML). Save triggers
  re-render and the FR-6.4 three-parser check; a failing check (e.g. a heading pushed over the
  letter-spacing threshold) is shown as a red pre-flight row with the parser output.
- Every edit creates a new tailored version (`v2 (edit)`), and it is the version recorded on the
  tracker (FR-6.3).

### 3.8 Application Review — Reject (`R`)

```
                       ┌──────────────────────────────────────────────────────────────┐
                       │  Reject  Zeta · Senior ML Engineer (LLM Apps) · 76 Tier 3   │
                       │                                                              │
                       │  Why? (one key)                                              │
                       │  1  Not relevant — scoring should have caught this          │
                       │  2  Weak fit — real gap I don't want to argue                │
                       │  3  Company / opportunity — not interested                  │
                       │  4  Location / travel / onsite                              │
                       │  5  Tailoring quality — regenerate instead of reject        │
                       │  6  Other  ┌────────────────────────────────────────────┐   │
                       │            │                                            │   │
                       │            └────────────────────────────────────────────┘   │
                       │                                                              │
                       │  Job goes to tracker as  rejected by Avadh · <reason>        │
                       │  and is never re-queued (FR-2.2). Documents are kept (Q-9).  │
                       │                                                              │
                       │                                   [ Esc cancel ] [ ⏎ Reject ]│
                       └──────────────────────────────────────────────────────────────┘
```

Reason `5` is not a rejection: it discards the tailored documents, re-runs tailoring with the
optional note, and returns the application to the queue as `regenerating` — the job's score
and verdict are untouched. Reasons `1`–`4` are logged against the job so the reject-reason
distribution is visible in Reports (a scoring-quality signal, §3.17).

### 3.9 Search Audit Log — Sources & Queries — `/audit/2026-09-14/sources`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Audit log   ◂ Sun 13   Mon 14 Sep 2026   Tue 15 ▸        [Sources] [Queries] [Jobs]          run 09:00–09:41│
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SOURCES · 8 queried · 7 ok · 1 partial                                                     NFR-4 · NFR-5│
│  Source          Policy          Status     Queries  Results  New   Dupes  Duration  Pacing   Note        │
│  Greenhouse      auto-apply      ✓ ok          24       41     19     22    3m 12s   1.8 s/req            │
│  Lever           auto-apply      ✓ ok          24       18      9      9    2m 05s   2.0 s/req            │
│  Workday         auto-apply      ✓ ok          11       22     11     11    6m 40s   4.1 s/req  3 tenants │
│  Career pages    auto-apply      ✓ ok          37       37     21     16    9m 18s   3.0 s/req  37 domains│
│  Wellfound       auto-apply      ✓ ok          12        9      4      5    1m 30s   2.5 s/req            │
│  LinkedIn        discovery-only  ✓ ok          24       48     31     17    4m 55s   6.0 s/req  C-1 policy│
│  Naukri          discovery-only  ✓ ok          24       31     22      9    3m 44s   5.0 s/req  C-1 policy│
│  Indeed          discovery-only  ⚠ partial     24        6      6      0    2m 10s   backoff    HTTP 429  │
│                                                                                     after page 6 [Retry ↻]│
│  Totals                                       180      212    123     89                                  │
│                                                                                                          │
│  QUERIES · 180 issued · 24 templates × sources                                              FR-1.5 · FR-1.1│
│  Template                                                            Sources  Results  New  Best score   │
│  "Senior AI Engineer" + (RAG | LLM | Agentic | MCP | GenAI)              8       41     23     94 Glean   │
│  "Forward Deployed Engineer" + (AI | LLM | GenAI)                        8       17     12     94 Glean   │
│  "FDE" + (AI | LLM)                                                      6        9      4     91 Sierra  │
│  "Senior Generative AI Engineer"                                          8       22     14     88 Sprinklr│
│  "AI Solutions Architect" + (LLM | Enterprise AI)                         8       19      9     87 Icertis │
│  "Senior Agentic AI Engineer"                                              8       11      8     89 Careem │
│  "LLM Engineer" + (LangChain | LangGraph | LLMOps)                         8       26     15     85 Observe │
│  "AI Platform Engineer" + (LLM | Agents)                                   8       14      7     81 Kore.ai│
│  "RAG Engineer" · "Applied AI Engineer" · "AI Automation Engineer" …       8       53     31     83 Innov. │
│  Geography filter applied per query: Remote-India → Pune → Bengaluru → Hyderabad → Mumbai → Delhi NCR → │
│  other India → Dubai/UAE → Europe → Canada  (FR-1.3)                                                    │
│  [Show all 180 raw queries ▾]                                                                             │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

*Policy* column is the Q-3 board policy made visible; *Pacing* is NFR-5 (rate limiting) — the
one place it needs to be seen. The partial Indeed row is NFR-4 (one board failing does not
abort the run) and its *Retry* is the recovery affordance.

### 3.10 Search Audit Log — Jobs with filtering — `/audit/2026-09-14/jobs`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Audit log   Mon 14 Sep 2026        [Sources] [Queries] [Jobs ●]                            143 unique jobs│
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Verdict  [all ▾]   Source [all ▾]   Tier [all ▾]   Geo [all ▾]   Fallback state [all ▾]   🔍 harvey        │
│ ● queued 14  ● deferred 19  ● by hand 6  ● rejected 106 (hard 41 · <70 58 · visa 7)  ● expired 1  ● dup 69│
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Score  Company           Role                              Geo        Source(s)    Verdict          Reason │
│  94    Glean             Senior Forward Deployed Engineer  BLR        GH+LI        queued                  │
│  91    Sierra            Forward Deployed AI Engineer      Remote     Career       queued                  │
│  89    Careem            Sr AI Engineer, Agentic Platforms Dubai      WD+LI        queued                  │
│  88    Sprinklr          Senior GenAI Engineer             Gurugram   Naukri       by hand   discovery-only│
│  87    Icertis           AI Solutions Architect            Pune       GH+LI+Naukri queued    carry-over 3d │
│  84    Uniphore          Sr Conversational AI Engineer     Chennai    Career       attention ATS 13/15     │
│  79    Turing            Senior LLM Engineer               Remote     Career       deferred  over ceiling  │
│  78    Persistent Sys.   GenAI Solution Architect          Pune       WD           deferred  over ceiling  │
│  74    Harvey            Applied AI Engineer — India       BLR        GH+LI        rejected  FR-4.2 mand. │
│                                                                                    qualification (law/legal│
│                                                                                    tech 3+ yrs, JD l.41)   │
│  71    Aleph Alpha       Senior LLM Engineer               Heidelberg Career       rejected  FR-1.3a no    │
│                                                                                    sponsorship (JD l.12)   │
│  68    Fractal           Lead Data Scientist — GenAI       Mumbai     Naukri+LI    rejected  score <70     │
│  66    Quantiphi         Senior ML Engineer                BLR        GH           rejected  FR-4.1 trad.  │
│                                                                                    ML, no GenAI            │
│  61    Razorpay          Senior Backend Engineer (AI team) BLR        Career       rejected  FR-4.1 non-AI │
│  —     "AI Engineer — WFH ₹4L/month, pay for laptop"       Remote     Indeed       rejected  FR-5.1 fraud: │
│                                                                                    equipment purchase      │
│  —     Palantir          Forward Deployed Engineer (Delta) London     Career       rejected  FR-1.6 FDE   │
│                                                                                    without GenAI; FR-1.3a  │
│  —     Cohere            Member of Technical Staff, Junior Toronto    LI           rejected  FR-1.4 junior │
│  ⋯ 127 more                                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ⏎ open job · F filter to fallback · Space select · Shift+X bulk mark skipped (fallback rows only)        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- **Reason column quotes the rule ID and the JD line.** FR-3.4 says record reasoning for
  rejected jobs; the UX requirement on top of that is that the reason must be *specific enough
  to disagree with* without opening the JD.
- `—` in Score for hard rejections (FR-4.1/4.2/5.1) that short-circuited before scoring: the
  UI must not show a fake number. Where the rule fired *after* scoring (Harvey, 74), the score
  is shown so Avadh can see it was otherwise a plausible match.
- *Source(s)* shows the dedup cluster compactly (`GH+LI+Naukri`) — FR-2.1/2.3 visible on every
  row.
- The verdict chips are the filter — click one to filter. The count chips are also the FR-4 and
  FR-1.3a daily visibility counters.

### 3.11 Apply by Hand (manual fallback) — `/by-hand`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ By hand · 6 pending · 3 done this week                                          Show: pending ▾  all runs ▾│
│ Jobs the agent found but cannot submit for you (FR-1.9). Documents are ready where score ≥ 80.           │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PENDING (6)                                                                                             │
│  Score  Company        Role                             Reason                    Link      Docs   Found │
│▸ 88 T2  Sprinklr       Senior GenAI Engineer            discovery-only · Naukri   ↗ open   📄 R 📄 L  today│
│         Est. by hand ≈ 6 min · Naukri profile already has your master resume                              │
│         [ M applied manually ]  [ S skip ]  [ ⏎ job detail ]                                              │
│  84 T2  Uniphore       Sr Conversational AI Engineer    unsupported form (custom  ↗ open   📄 R 📄 L  today│
│                                                          React form, no ATS)                              │
│  83 T2  Mindtickle     Senior AI Engineer               discovery-only · LinkedIn ↗ open   📄 R 📄 L  today│
│         (Easy Apply)                                                                                     │
│  81 T2  G42            Senior Applied AI Engineer       CAPTCHA · Workday (Abu    ↗ open   📄 R 📄 L  today│
│                        (Abu Dhabi ✈ visa: sponsored)    Dhabi tenant)                                     │
│         [ ↻ Resume with agent — solves CAPTCHA in visible browser, agent continues ]                      │
│  77 T3  Gupshup        Senior LLM Engineer              discovery-only · Naukri   ↗ open   —      today   │
│         Below 80 — no documents prepared. [Prepare documents ≈ $0.20]                                    │
│  72 T3  Sirion (alt)   Applied AI Engineer              discovery-only · Naukri   ↗ open   —      Sat 12  │
│         Also in your queue via Lever (same job, FR-2.1) — apply there instead.   [S skip as duplicate]   │
│                                                                                                          │
│  DONE (3 this week)                                                                                      │
│  86     Chargebee      Senior AI Engineer               applied manually · Fri 11 · in tracker ✓         │
│  80     Yellow.ai      Staff AI Engineer                skipped · "already spoke to recruiter" · Thu 10   │
│  74     Wipro Holmes   GenAI Architect                  skipped · "not interested" · Thu 10              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  J/K move · M applied manually · S skip · ⏎ detail · O open link · Space select · Shift+S bulk skip       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- This screen is a **pinned, pre-filtered view of the audit log's Jobs table** (`fallback state
  = pending`, all runs), so FR-1.9's "the audit log is the manual-fallback surface" holds
  literally while the list gets first-class navigation.
- **Reason is typed**, from a fixed set: `discovery-only · <board>` (Q-3/C-1), `CAPTCHA / OTP /
  login` (C-2), `unsupported form`, `missing data` (a HITL-3 halt Avadh chose not to answer).
  The reason determines the affordance: only CAPTCHA/login rows get **Resume with agent**.
- `M` (applied manually) writes a **tracker row** immediately with `channel: manual`, so
  FR-2.2 dedup works for hand-applied jobs too. It optionally asks for a date (defaults to now)
  and a note.
- Duplicate detection reaches into this list: the Sirion row is the same job as a queued Lever
  posting (FR-2.3), and the UI says so rather than letting Avadh apply twice.

### 3.12 Application Tracker — `/tracker`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tracker · 61 applications · 47 submitted · 9 rejected by you · 3 manual · 2 pending    🔍     [Export CSV] │
│ Status [all ▾]  Channel [all ▾]  Tier [all ▾]  Geo [all ▾]  Date range [30 days ▾]  Follow-up due [3] ▾ │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Applied   Score  Company        Role                        Loc        Channel     Status       Follow-up │
│ 14 Sep    94 T1  Glean          Sr Forward Deployed Eng     BLR        Greenhouse  submitted ✓   28 Sep   │
│ 14 Sep    91 T1  Sierra         Forward Deployed AI Eng     Remote     Career      submitted ✓   28 Sep   │
│ 14 Sep    89 T2  Careem         Sr AI Eng, Agentic Platf.   Dubai ✈    Workday     submitting…   —        │
│ 14 Sep    76 T3  Zeta           Sr ML Engineer (LLM Apps)   BLR        —           rejected by   —        │
│                                                                                    Avadh · not relevant  │
│ 14 Sep    79     Yellow.ai      Sr Agentic AI Engineer      Remote     —           expired       —        │
│ 11 Sep    86 T2  Chargebee      Senior AI Engineer          Chennai    manual      applied ✓     25 Sep   │
│ 11 Sep    87 T2  Icertis        AI Solutions Architect      Pune       Greenhouse  submitted ✓   25 Sep   │
│ 10 Sep    90 T1  Databricks     Sr Specialist SA — GenAI    BLR        Greenhouse  interview 🎯  —        │
│ 09 Sep    85 T2  Postman        Sr AI Platform Engineer     BLR        Lever       pending Q     —        │
│                                                                                    (HITL-3, 22 min)      │
│ 08 Sep    88 T2  Freshworks     Sr AI Engineer — Freddy     Chennai    Career      no response   ⚠ 22 Sep │
│                                                                                                  overdue  │
│ ⋯                                                                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ Glean · Senior Forward Deployed Engineer                                            [Job detail →]     │
│   URL          https://boards.greenhouse.io/glean/jobs/7712…  ↗       Discovered 14 Sep 09:12            │
│   Applied      14 Sep 10:03 via Greenhouse · confirmation email received 10:04                            │
│   Resume       glean-a1 v1  [view diff] [PDF ↗]       Cover letter  yes · 218 words  [view]              │
│   Answers      4 (2 resume · 1 answer sheet · 1 generated)  [view]                                        │
│   Key skills   MCP · Agentic AI · enterprise integrations · RAG · end-to-end ownership                   │
│   Status       submitted → [ mark: recruiter reply | interview | offer | rejected by company | withdrawn ]│
│   Follow-up    28 Sep  [change]         Notes  ┌──────────────────────────────────────────────────────┐ │
│                                                │                                                      │ │
│                                                └──────────────────────────────────────────────────────┘ │
│   What was sent (NFR-3)  [Open submission bundle: resume PDF · letter · answers · form screenshot]       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- Every FR-10.1 column is present: the table carries the scannable ones; the expansion row
  carries URL, dates, resume version, cover letter, key matching skills, notes, follow-up.
- **Status is Avadh's to advance** after submission (recruiter reply / interview / offer /
  rejected by company / withdrawn). This is what makes the §9 primary metric — interview rate —
  measurable in Reports. It is the one place the tracker needs user input.
- *Follow-up due* is a filter chip with a count, and overdue rows carry ⚠. The follow-up date
  defaults to applied + 14 days.
- **What was sent** opens the submission bundle — NFR-3 auditability as a single click.

### 3.13 Job Detail with score breakdown — `/jobs/:id`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ← back     Harvey · Applied AI Engineer — India                              rejected · FR-4.2 · 14 Sep    │
├─────────────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│ SCORE 74 · Tier 3 (would have qualified)             │ HARD RULES  (FR-4 · FR-5 · FR-1.3a · FR-1.6)       │
│                                                     │ ✗ FR-4.2 Mandatory qualification absent            │
│ Technical skill match        ██████▌   22 / 30      │   JD line 41: "JD or LLM degree, or 3+ years in   │
│  Python, LangChain, RAG pipelines, eval harnesses    │   legal-tech product engineering, is required."   │
│  present; TypeScript/Next.js front-end absent        │   Resume holds neither. No override (FR-4.3).      │
│ Relevant AI/LLM experience   ███████▌  19 / 25      │ ✓ FR-4.1 not junior · AI-primary · not expired     │
│  Enterprise RAG (AIQA), citation-grounded answers    │ ✓ FR-5.1 no fraud signals · harvey.ai domain ok    │
│  map directly; no legal-domain corpora experience    │ – FR-1.3a n/a — India role                         │
│ Seniority match              ██████▌   13 / 15      │ – FR-1.6 n/a — not an FDE posting                  │
│  "Senior/Applied" IC, 4–7 yrs asked                  │ – FR-1.7 no travel/onsite requirement stated        │
│ Project / domain relevance   ████       5 / 10      │                                                    │
│  Legal domain unfamiliar; RAG pattern identical      │ WHY REJECTED — plain English                       │
│ Company / opportunity        █████████  9 / 10      │ Otherwise a reasonable Tier 3 match, but the JD    │
│  Well-funded, strong AI brand, India expansion       │ makes legal-domain credentials mandatory. Applying │
│ Location / remote fit        █████      4 / 5       │ would require claiming a qualification you don't    │
│  Bengaluru hybrid                                    │ hold — barred by T-3.                              │
│ Resume keyword alignment     ████       2 / 5       │                                                    │
│  Missing: "legal", "contracts", "Next.js"            │ [ Promote to queue ]  — unavailable: hard rule     │
│                                                     │                                                    │
│ Scored by  haiku-4.5 (screen) → sonnet-4.5 (deep)   │ SEEN ON  (FR-2.1 · FR-2.3)                        │
│ Cost $0.018 · 14 Sep 09:17 · trace ↗                │ ● greenhouse.io/harvey/jobs/5521…  canonical ↗     │
│                                                     │ ● linkedin.com/jobs/view/40917…   same ATS id ↗    │
│ FIRST-PASS vs DEEP                                  │ Matched by ATS job id + title similarity 0.91      │
│ screen 78 → deep 74 (−4: legal-domain weighting)     │                                                    │
├─────────────────────────────────────────────────────┴────────────────────────────────────────────────────┤
│ TIMELINE                                                                                                 │
│ 09:12 discovered (Greenhouse) · 09:12 duplicate merged (LinkedIn) · 09:14 screened 78 · 09:17 deep 74 ·  │
│ 09:17 rejected FR-4.2 · — no tailoring · — not in tracker (rejected pre-application)                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ JOB DESCRIPTION  (captured 14 Sep 09:12 · 1,842 words · posted 12 Sep · active as of 09:41)   [Raw ↗]   │
│  …                                                                                                       │
│  41  ▌A JD or LLM degree, or 3+ years in legal-tech product engineering, is required.   ◄ FR-4.2        │
│  …                                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:

- **Every dimension has a one-line reason** directly under its bar — FR-3.4 at the granularity
  the rubric is scored. The lines that fired hard rules are highlighted in the captured JD with
  the rule ID in the gutter, which is how FR-3.2 ("read the actual JD") is made auditable.
- **Promote to queue** exists for soft rejections (score < 70, or a Tier 3 gap Avadh disagrees
  with) and is logged as an override. It is *absent*, with the reason spelled out, for FR-4.1,
  FR-4.2 and FR-5.1 rejections. This is the one place the design deliberately refuses the user
  something — FR-4.3 and T-3 require it.
- *Scored by* and *Cost* make TR-10/TR-11 visible per job; *First-pass vs deep* shows the tiered
  model strategy (§7.1) doing its job.

### 3.14 Settings — Answer sheet — `/settings/answers`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Settings   [Answer sheet ●] [Targets] [Models & budget] [Sources] [Schedule] [Notifications] [Data & secrets]│
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ANSWER SHEET  §2.1                                                     🔒 Sensitive · [ Reveal values ]  │
│  Filled into application forms only when a form asks. Never logged, never in reports or Telegram,        │
│  never volunteered. Stored locally.                                                                      │
│                                                                                                          │
│  Field                    Value                              Used      Last used             Status      │
│  Current CTC              ₹ ••.• LPA                         31×       today · Careem        ✓ decided   │
│  Expected CTC             ₹ •• LPA                           29×       today · Glean         ✓ decided   │
│  Notice period            • month                            38×       today · Glean         ✓ decided   │
│  Relocation stance        [ Yes — Dubai/UAE only         ▾ ]  4×       Sat 12 · G42          ⬜ open O-2  │
│                           options: No · Yes — Dubai/UAE only · Yes — anywhere in scope · Ask me each time│
│  Preferred start date     [ Per notice period (1 month)  ▾ ]  6×       Fri 11 · Icertis      ⬜ open O-2  │
│  Work authorisation       [ Indian citizen — sponsorship required ▾ ]  12×  today · Aleph Alpha ⚠ unconf.│
│     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│     │ Impact of this setting (last 30 days): 23 international jobs rejected for no sponsorship —      │   │
│     │ Europe 19 · Canada 4 · Dubai/UAE 0 (UAE roles sponsor by default). If you hold any permit,       │   │
│     │ change this — it is the single setting that most widens your eligible pool (FR-1.3a, O-2).      │   │
│     │ [ See the 23 jobs → ]                                                                            │   │
│     └────────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                          │
│  LEARNED FROM HALTS  (HITL-R3 — added when you answered a novel question)                                │
│  employment_termination   "No."                               1×       today · Postman       ✓ you added │
│  willing_to_work_shifts   "No — standard IST hours; overlap    2×      Wed 09 · Turing        ✓ you added │
│                            with US/EU mornings is fine."                                                 │
│  [ + Add field ]                                                                                         │
│                                                                                                          │
│  HALTS THIS MONTH  3  (goal: → 0 as the sheet fills in)                                                  │
│                                                                                                          │
│                                                                              [ Ctrl+S Save ]  unsaved ●  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The *Used* / *Last used* columns are how FR-8.1 and HITL-3 stay visible without ever printing a
value anywhere else. *Halts this month* is the HITL-R3 success counter.

### 3.15 Settings — Targets · Models & budget

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Settings   [Answer sheet] [Targets ●] [Models & budget] …                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  DAILY CEILING  FR-9.2                                                                                   │
│  Applications per day   [ ◂ 15 ▸ ]   range 10–20 default · allowed 1–40                                  │
│  Ceiling, not quota. The agent applies to fewer when fewer qualify — it never pads. Carry-over          │
│  approvals count toward the day's ceiling (O-5). Last 7 days: 11 · 14 · 9 · 15 · 6 · 13 · 12 applied.   │
│                                                                                                          │
│  SCORE THRESHOLDS  FR-3  (fixed by requirements — display only)                                          │
│  90–100 Tier 1 apply immediately · 80–89 Tier 2 apply · 70–79 Tier 3 apply if no gaps · <70 do not apply │
│  Tier 3 handling: [ fold into approval review (default, O-3) ▾ ]                                         │
│                                                                                                          │
│  GEOGRAPHY PRIORITY  FR-1.3  (drag to reorder · toggle to exclude)                                        │
│  ☑ Remote (India)  ☑ Pune  ☑ Bengaluru  ☑ Hyderabad  ☑ Mumbai  ☑ Delhi NCR  ☑ Other India                 │
│  ☑ Dubai / UAE  ☑ Europe  ☑ Canada          International remote: ☑ only where working from India allowed│
│                                                                                                          │
│  SENIORITY  FR-1.4   ☑ Senior ☑ Staff ☑ Lead ☑ Architect ☑ Senior IC  ☐ Mid (exceptional companies only) │
│  Never: junior · entry · intern · graduate · trainee  (not configurable)                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Settings   … [Models & budget ●] …                                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  MODELS PER STAGE  TR-10 · §7.1                                    Provider keys: ✓ Anthropic ✓ OpenAI    │
│  Stage                         Model                          Today      Calls   Tokens     Cost         │
│  Bulk screening                [ claude-haiku-4-5        ▾ ]   143 jobs    143    1.9M      $0.41        │
│  Deep JD analysis / rationale  [ claude-sonnet-4-5       ▾ ]    37 jobs     37    0.6M      $0.96        │
│  Tailoring · letters · answers [ claude-opus-4-1         ▾ ]    12 apps     41    0.4M      $2.45        │
│  Edit / revise (on demand)     [ same as tailoring       ▾ ]     1 edit      1    12k       $0.04        │
│                                                                                     Total   $3.86        │
│                                                                                                          │
│  BUDGET  Q-8 · TR-11 · TR-12                                                                              │
│  Daily ceiling   [ $ 100 ]    hard stop — run pauses, Telegram alert, resumes tomorrow                   │
│  Soft alert      [ $   5 ]    Telegram alert + amber header; run continues                               │
│  Today  $3.86 ▕█▏ soft $5 ▕                                                        ▏ $100                 │
│  Last 14 days avg $2.90 · max $6.10 (Sat 5 Sep — soft alert fired, cause: 2 retry loops on Workday)      │
│  [ Open run console for cost per stage per run → ]                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.16 Settings — Sources · Schedule · Notifications · Data & secrets

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Settings   … [Sources ●] …                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SOURCES  FR-1.1 · FR-1.2 · Q-3                                                                          │
│  Source          Enabled   Policy               Why                                        Last ok       │
│  Greenhouse        ☑       auto-apply           ATS, direct — preferred (FR-1.2)           today 09:41   │
│  Lever             ☑       auto-apply           ATS, direct                                today         │
│  Workday           ☑       auto-apply           ATS, direct · needs your login per tenant  today         │
│  Career pages      ☑       auto-apply           37 tracked domains  [manage list]          today         │
│  Wellfound         ☑       auto-apply                                                      today         │
│  LinkedIn          ☑       discovery-only 🔒     C-1 ToS + bot detection — never automated  today         │
│  Naukri            ☑       discovery-only 🔒     C-1                                       today         │
│  Indeed            ☑       discovery-only 🔒     C-1                                       ⚠ partial     │
│  Policy is fixed by decision Q-3 and is not a toggle. Disabling a source only stops discovery there.     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  SCHEDULE  FR-12.1 · Q-6 · O-5                                                                            │
│  Daily run at  [ 09:00 ]  local (IST)      Next: Tue 15 Sep 09:00 · scheduler: Windows Task ✓ registered │
│  If the PC is asleep/off at 09:00:  [ run as soon as it wakes ▾ ]                                        │
│  Pending approvals: carried over · never auto-submitted · never auto-expired · closed postings → expired  │
│  [ ▶ Run now ]   [ ■ Pause scheduling ]     Last 7 runs: ✓ ✓ ✓ ⚠ ✓ ✓ ✓                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  NOTIFICATIONS  Q-7                                                                                       │
│  Telegram chat   ✓ connected (@avadh…)   [ Send test ]                                                    │
│  Send:  ☑ approvals ready   ☑ blocked (login/CAPTCHA)   ☑ question needs answer   ☑ daily report          │
│         ☑ cost soft alert   ☑ run failed / missed   ☑ stale approvals reminder after [ 48 ] h             │
│  Links in messages point to  [ http://localhost:8765            ]                                        │
│  ⚠ localhost links only work on this PC. Set a LAN or Tailscale URL if you want them to open from your    │
│    phone. Messages are written to be useful without opening the link.                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DATA & SECRETS  Q-9 · TR-8 · NFR-7                                                                       │
│  Storage  C:\Users\Avado\Desktop\LearningGenAI\JobAgent\data\   2.3 GB · 61 applications · 1,904 jobs     │
│  Retention  keep everything, indefinitely (Q-9)                                    [ Export all (zip) ]   │
│  Secrets  read from Windows user registry at run start · never written to disk or logs · never displayed  │
│           ANTHROPIC_API_KEY ✓ present   OPENAI_API_KEY ✓ present   TELEGRAM_BOT_TOKEN ✓ present            │
│  Third parties contacted  LLM provider(s) above · Telegram · the job boards/ATS you apply through. Nothing │
│           else (NFR-7).                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.17 Daily Report — `/reports/2026-09-14`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Reports    ◂ Sun 13   Mon 14 Sep 2026   Tue 15 ▸       sent to Telegram 09:43 ✓        [Copy as text]     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Discovered 212 · Evaluated 143 unique · Queued 14 · Submitted 12 (+1 manual) · By hand 6 · Rejected 106 │
│  Spend $3.86 · Run 41 min · Sources 7/8 ok                                                               │
│                                                                                                          │
│  ▼ TOP APPLICATIONS (12 submitted)                                                                       │
│  94  Glean         Sr Forward Deployed Engineer   Bengaluru · Hybrid   FDE + MCP + enterprise integrations│
│                                                                        — JD asks for exactly the Krista  │
│                                                                        lifecycle ownership.              │
│  91  Sierra        Forward Deployed AI Engineer   Remote (India ok)    Agentic customer deployments;      │
│                                                                        tool-calling depth is the edge.   │
│  89  Careem        Sr AI Engineer, Agentic Platf. Dubai · Onsite ✈     Agentic platform build-out;       │
│                                                                        sponsorship offered.              │
│  ⋯ 9 more ▾                                                                                              │
│                                                                                                          │
│  ▼ REJECTED (106) — grouped by reason                                                                    │
│  Score below 70 ……………………………………………… 58   FR-4.1 primarily non-AI / classical ML ……… 23                    │
│  FR-4.1 junior / entry ……………………………… 9    FR-4.2 mandatory qualification ……………… 6                        │
│  FR-1.3a no sponsorship ………………………… 7    FR-4.1 expired / already applied ………… 2                         │
│  FR-5.1 fraud / suspicious ……………………… 1    [ open in audit log → ]                                          │
│                                                                                                          │
│  ▼ NEEDS YOUR ATTENTION (3)                                                                              │
│  ● Postman — screening question needs your answer (22 min)                              [Answer →]       │
│  ● Uniphore — tailoring failed ATS check (letter-spacing on heading)                    [Retry / edit →] │
│  ● Indeed returned 429 after page 6 — 14 pages unsearched                               [Retry →]        │
│                                                                                                          │
│  ▼ TRACKER UPDATES (6)                                                                                   │
│  12 submitted · 1 marked applied manually (Chargebee) · 1 rejected by you (Zeta) · 1 expired (Yellow.ai) │
│  · follow-ups due this week: 3                                                                           │
│                                                                                                          │
│  ▼ YOUR REVIEW TODAY                                                                                     │
│  14 reviewed in 13 m 40 s · median 52 s · 12 approved · 1 edited · 1 rejected (not relevant) · 1 expired │
│  Reject reasons, 30 days: not relevant 4 · weak fit 2 · location 2 · company 1  → scoring signal: watch  │
│  "Senior ML Engineer" titles (3 of 4 not-relevant rejects)                                              │
│                                                                                                          │
│  ▼ 14-DAY TREND                                                                                          │
│  discovered ▃▄▅▄▅▃▁▅▆▄▄▅▄▄   queued ▂▃▅▃▄▂▁▅▆▃▄▅▃▂   submitted ▂▃▄▃▄▂▁▄▅▃▄▄▃▂   spend ▂▂▃▂▂▂▁▃▃▂▂▃▂▂          │
│  Callback rate (submitted ≥ 14 d ago): 3 of 29 = 10.3%  · interviews 2                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

*Your review today* is not in FR-11.1 but is the cheapest instrument for the §9 metric *"Avadh's
time per application"* and for detecting the rubber-stamp reflex (§8). *Callback rate* is the
§9 primary metric and depends on Avadh advancing statuses in the tracker.

### 3.18 Run Console — `/runs/2026-09-14`

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Runs    ◂ Sun 13   Mon 14 Sep 2026 · 09:00 → 09:41 · finished with warnings   Tue 15 ▸      [▶ Run now]   │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  STAGES                                    Status      Items    Duration   Model            Cost   Trace │
│  1 Discover (8 sources, 180 queries)       ⚠ partial   212      33m 34s    —                —      ↗     │
│  2 Deduplicate                             ✓           143      0m 04s     —                —      ↗     │
│  3 Screen (first pass)                     ✓           143      2m 10s     haiku-4.5        $0.41  ↗     │
│  4 Hard rules + fraud                      ✓           143→102  0m 02s     —                —      ↗     │
│  5 Deep analysis + score                   ✓           37       3m 40s     sonnet-4.5       $0.96  ↗     │
│  6 Select (ceiling 15, carry-over 3)       ✓           12       0m 01s     —                —      ↗     │
│  7 Tailor + letter + answers               ⚠ 1 failed  12       4m 50s     opus-4.1         $2.45  ↗     │
│  8 Render + ATS verify                     ⚠ 1 failed  12       0m 40s     —                —      ↗     │
│  9 Queue for approval                      ✓           11       —          —                —      ↗     │
│ 10 Submit (after approval)                 ● 1 running 12/13    —          —                —      ↗     │
│ 11 Report + notify                         ✓           1        0m 06s     haiku-4.5        $0.04  ↗     │
│                                                                                     Total  $3.86         │
│                                                                                                          │
│  LIVE  10:14:32  Submit · Careem (Workday)  step 6/9  "upload resume"  ✓   step 7/9 "answer 5 questions"…│
│  Idempotency: submission id careem-c3-s1 · not yet submitted · safe to retry (NFR-2)                     │
│                                                                                                          │
│  EVENTS (filter: warnings ▾)                                                                             │
│  09:33:12  ⚠ Indeed  HTTP 429 after page 6 → backoff 60 s ×3 → gave up · 14 pages unsearched  [Retry]     │
│  09:38:41  ⚠ Uniphore  ATS check 13/15 — heading "PROFESSIONAL SUMMARY" letter-spacing 8.4% (>8%)         │
│  09:40:02  ● Postman  HITL-3 halt — "Have you ever been terminated…" not answerable → Telegram sent       │
│  09:41:10  ✓ Report sent to Telegram                                                                     │
│  09:41:10  ✓ State checkpoint written (run resumable)                                                    │
│                                                                                                          │
│  SECRETS GUARD  FR-5.2 · TR-8   0 fields refused today · lifetime 2 (both "password" fields on a fraud   │
│  posting, 3 Sep)                                                                                         │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This is the Tier C home for TR-7 (traceability), TR-11 (per-stage cost), NFR-2 (idempotency
shown as submission ids), NFR-4 (partial source), FR-5.2 (secrets guard), FR-12.2/TR-5
(checkpoint). Avadh will open it a few times a month; it must be complete, not pretty.

### 3.19 Needs-you-now slide-over (HITL-2 · HITL-3 · HITL-4)

```
                              ┌──────────────────────────────────────────────────────────────────┐
                              │ NEEDS YOU NOW · 2                                          Esc ✕ │
                              ├──────────────────────────────────────────────────────────────────┤
                              │ ● BLOCKED · Careem · Senior AI Engineer · Workday        14 min  │
                              │   Login / OTP required to continue (C-2)                         │
                              │   Agent was at step 3/9 "sign in to careem.wd3.myworkdayjobs"    │
                              │   ┌────────────────────────────────────────────────────┐         │
                              │   │  [ browser screenshot — Workday sign-in page ]     │         │
                              │   └────────────────────────────────────────────────────┘         │
                              │   [ Take over browser ]  brings the agent's window forward;      │
                              │                          sign in, then                           │
                              │   [ ▶ Continue ]  resumes at step 3 — nothing re-executed        │
                              │   [ Send to by-hand ]   [ Abandon ]                              │
                              │   Run continues with other jobs meanwhile.                       │
                              ├──────────────────────────────────────────────────────────────────┤
                              │ ● QUESTION · Postman · Sr AI Platform Engineer · Lever   22 min  │
                              │   Form asks (free text, max 500 chars):                          │
                              │   "Have you ever been terminated from employment? If yes,        │
                              │    please explain."                                              │
                              │   Not answerable from resume or answer sheet — halted (FR-9.4,   │
                              │   T-4). The agent will not guess.                                │
                              │   ┌────────────────────────────────────────────────────┐         │
                              │   │ No.                                                │         │
                              │   └────────────────────────────────────────────────────┘         │
                              │   ☑ Save to answer sheet as  [ employment_termination ]          │
                              │     so this never halts again (HITL-R3)                          │
                              │   [ Ctrl+⏎ Answer & continue ]   [ Skip this job ]               │
                              └──────────────────────────────────────────────────────────────────┘
```

HITL-4 (a claim that could misrepresent) uses the same *Question* card shape with the proposed
claim, the conflicting resume line, and **Use resume wording / Edit / Skip job** actions.

---

## 4. UI states

Every major component, six states. "Overflow" means more items than the layout was designed for.

| Component | Empty | Loading | Error | Partial | Success | Overflow |
| --- | --- | --- | --- | --- | --- | --- |
| **Dashboard CTA** | *"Nothing to review. Next run Tue 09:00."* Card shrinks to one line; nav badge disappears. | Skeleton with last known count greyed; never shows `0` while loading. | *"Couldn't load queue — backend unreachable."* Retry button; header dot red. | Run still in progress: *"7 ready so far · run in progress (stage 7/11)"* — reviewing can start before the run ends. | *"14 waiting · est. 13 min"*. | > 30 pending (missed several days): CTA adds *"Oldest 6 days · 4 may have closed — [Check for expired first]"*. |
| **Funnel** | Run hasn't happened today: yesterday's funnel shown greyed with *"Yesterday"* label; never blank. | Stage-by-stage fill as the run progresses. | Failed stage marked ✗ with the error; downstream stages *"not reached"*. | Discovery partial (⚠ Indeed) — the Discovered number carries a ⚠ and tooltip. | All stages ✓. | Not applicable — fixed 7 columns. |
| **Needs you now** | Single grey line with last resolved handoff. | — | Backend can't reach browser worker: *"Browser worker offline — [Restart]"*. | Some items resolved, others waiting — resolved ones fade after 10 s. | Item resolved → toast *"Careem resumed"*. | > 5 items: list scrolls inside card, count in red; suggests *"Pause scheduling until cleared?"* |
| **Approval queue** | *"Queue empty. 12 submitted today, 1 submitting."* with live tick. | Row skeletons. | *"Failed to load application X — [Retry] [Skip]"* per row; others still usable. | Some applications still tailoring: rows show *"preparing… 40 s"* and are not openable yet. | Full list, carry-over first. | > 40 rows: sticky group headers; *"Bulk reject Tier 3?"* suggestion appears (never bulk approve). |
| **Review — resume diff** | Master unchanged for this job (rare): *"No changes — master resume used as-is. D for full view."* | Diff computing: show master text immediately, changes highlight in when ready. | Tailored HTML failed to parse: full fallback to raw text side-by-side; pre-flight *ATS* row red. | Diff ready, PDF still rendering: *Open PDF* disabled with spinner; approve still allowed only when ATS check has run. | 6 changes, all classified. | > 40 changes (agent rewrote too much): banner *"Heavy rewrite — 41 changes. Consider Reject → 5 regenerate with 'minimal changes'"*. |
| **Review — cover letter** | Form has no letter field: tab greyed *"Not requested by this form (FR-7.1)"*. | Text visible, markers resolving. | 1+ unresolved marker → red, pre-flight blocks approve. | Some markers JD-context (grey). | 11/11 traced. | > 350 words: word count amber; > 500 red with *"Concise — FR-7.1"*. |
| **Review — answers** | Form has no questions: *"No screening questions — profile fields only."* | — | Answer references a deleted answer-sheet field: red row, *"Field removed — [Add back] [Answer now]"*. | 1 halted question → row *"awaiting your answer"* links to Needs-you-now; approve disabled. | All sourced. | > 12 questions: collapsed to sourced-from-resume group + expanded generated group. |
| **Pre-flight (FR-9.1)** | — | Rows tick in as checks run (≤ 2 s). | Any ✗ → Approve disabled, row explains, `E` jumps to the offending tab. | *Job still active* check could not reach the posting: row amber *"couldn't verify — last seen active 09:41"*; approve allowed with the warning. | 12/12 green. | — |
| **Approve toast** | — | — | Submission failed after grace: toast becomes persistent red *"Glean — submission failed at step 5: <reason> · [Retry] [Send to by-hand]"* and Needs-you-now gets a row. | Submitting (progress ticks in queue empty-state). | *"Submitted · confirmation received"*. | Multiple submissions queued: toasts stack to a single *"3 submitting…"* pill. |
| **Audit log — jobs** | Run had no results (source outage): *"0 jobs found — see Sources tab"* with the failing rows linked. | Skeleton table. | Run data missing/corrupt: *"Audit data for 14 Sep unavailable — [Open run console]"*. | Filter yields 0: *"No jobs match · [Clear filters]"*. | Table. | 143 rows: virtualised scroll; export CSV; filters sticky. |
| **By hand** | *"Nothing to apply by hand. 3 done this week."* | — | Link dead (404 on open): row gains *"posting closed?"* and a *Mark expired* action. | Documents still preparing for a row: chips show spinner. | List with docs. | > 15 pending: grouped by reason with collapse; *"Bulk skip Tier 3?"* suggestion. |
| **Tracker** | First run ever: *"No applications yet. First run Tue 09:00 · [Run now]"*. | Skeleton. | Write failed (durability!): red banner *"Tracker write failed — retrying · data is safe in checkpoint"* — this is NFR-1 made visible. | Status `submitting…` rows live-update. | Full table. | > 500 rows: paginated 100/page; filters + search; export. |
| **Job detail — score** | Hard-rejected before scoring: score panel shows *"Not scored — FR-4.1 fired first"* with the rule. | Skeleton bars. | Reasoning missing (LLM error): *"Reasoning unavailable — [Re-score ≈ $0.02]"*. | Screened but not deep-scored (deferred): *"First-pass 78 · deep analysis not run (over ceiling)"*. | Full breakdown. | — |
| **Settings** | — | — | Save failed: banner, unsaved indicator stays; values never silently revert. | Some fields open (O-2): ⬜ status, still saveable. | *"Saved · effective next run · [Run now]"*. | — |
| **Spend meter (header)** | $0.00 before first run. | — | Cost tracking unavailable: meter shows *"$ ?"* in amber — never silently $0. | Mid-run running total. | Under soft alert: neutral. | Over $5: amber + Telegram; over $100: red, run paused, header says *"Ceiling hit — run paused"*. |
| **Run console** | No run today yet: *"Next 09:00 · [Run now]"* and yesterday's console. | Stages fill live. | Crash: last stage ✗, *"State checkpoint from 09:38 · [Resume run]"* (FR-12.2). | ⚠ stages. | All ✓. | > 200 events: filter default *warnings*, full log downloadable. |
| **Telegram link** | — | — | Chat unreachable: Settings shows ✗, dashboard banner *"Telegram not delivering since 09:41"* — a silent notification failure would stall gates. | — | *sent 09:43 ✓*. | — |

**Missed run** (PC asleep at 09:00) deserves its own state because it will happen: header dot
red, dashboard banner *"Today's run did not start (PC was asleep at 09:00) · [Run now] · change
policy in Settings › Schedule"*, and a Telegram *run missed* message at 09:15.

---

## 5. Interaction patterns

### 5.1 Approve · Edit · Reject · Postpone

```
              ┌────────────┐   A    ┌─────────────────────────┐  5 s   ┌────────────┐   ok   ┌───────────┐
   Review ───►│ pre-flight │──────►│ approved · grace window │───────►│ submitting │──────►│ submitted │
              │ 12/12 ✓ ?  │        │ "Z to undo"             │        │ (worker)   │        │ + tracker │
              └─────┬──────┘        └──────────┬──────────────┘        └─────┬──────┘        └───────────┘
                    │ any ✗                    │ Z                           │ fail / CAPTCHA
                    ▼                          ▼                             ▼
              Approve disabled;         back to Review,               Needs-you-now row
              E jumps to the            nothing sent                  (retry · by-hand · abandon)
              failing tab
```

| Action | Key | Behaviour | Safety |
| --- | --- | --- | --- |
| **Approve & next** | `A` | Marks approved, starts 5 s grace, advances to next application immediately. Submission is picked up by the browser worker after the grace window. | Grace window with `Z` undo (visible toast with countdown). Pre-flight must be all green. No modal. |
| **Approve & stay** | `Shift+A` | Same, without advancing — for when he wants to watch the submission. | Same. |
| **Edit** | `E` | Enters edit mode on the current tab. `Ctrl+⏎` saves and re-validates; `Esc` cancels. Does not change queue position. | Live fabrication guard; approve blocked on untraced claims; resume edits re-run ATS check. Creates new doc version. |
| **Reject** | `R` then `1–6`, `⏎` | Reason required. Job → tracker `rejected by Avadh`. Reason `5` regenerates instead. | Reversible from Job detail (*Un-reject → back to queue*) because nothing was sent. |
| **Postpone** | `P` | Moves the application to the end of the queue; keeps carry-over status and age. | — |
| **Dismiss expired** | `X` | Only offered when the posting is detected closed. Tracker status `expired`. | — |
| **Undo last** | `Z` | Within grace: cancels approval. After: for reject/postpone/dismiss, reverses. For a completed submission: not possible — toast says *"Already submitted (C-3) — no unsend"*. | Honest about irreversibility. |

**Why a grace window and not a confirm dialog.** A dialog on the 15th approval is clicked
through by reflex; it protects nothing and costs 3 seconds each. A grace window costs nothing
when he is right and gives him 5 seconds when the *"wait—"* arrives a beat after the keypress,
which is when it actually arrives.

### 5.2 Keyboard map

Global (any screen):

| Key | Action |
| --- | --- |
| `G` then `T` / `Q` / `B` / `A` / `R` / `S` | Go to Today / Queue / By hand / Audit / Reports / Settings |
| `Ctrl+K` | Command palette: jump to company, job, setting; *"run now"*, *"retry indeed"* |
| `N` | Open Needs-you-now slide-over |
| `?` | Keyboard help overlay |
| `Esc` | Close overlay / cancel edit |

Review screen:

| Key | Action |
| --- | --- |
| `A` / `Shift+A` | Approve & next / Approve & stay |
| `E` | Edit current tab · `Ctrl+⏎` save · `Esc` cancel |
| `R` → `1`–`6` → `⏎` | Reject with reason |
| `P` | Postpone to end of queue |
| `X` | Dismiss expired (when offered) |
| `Z` | Undo (see table above) |
| `1` `2` `3` | Resume / Cover letter / Answers tab |
| `D` | Toggle diff ↔ full resume |
| `J` / `K` | Next / previous application (without deciding) |
| `O` / `Shift+O` | Open JD / open tailored PDF in new tab |
| `Ctrl+Shift+V` | Reveal answer-sheet value in Answers tab (transient) |
| `Tab` | Cycle focus through markers in the letter; `⏎` on a marker jumps to the resume line |

Lists (Queue, By hand, Audit jobs, Tracker):

| Key | Action |
| --- | --- |
| `J` / `K` | Move · `⏎` open · `Space` select · `Ctrl+A` select all visible |
| `M` / `S` | By hand: applied manually / skip |
| `Shift+R` / `Shift+S` / `Shift+X` | Bulk reject / bulk skip / bulk dismiss expired on selection |
| `/` | Focus search/filter |

### 5.3 Edit — what can be edited and what happens

| Target | Edit surface | On save |
| --- | --- | --- |
| Cover letter | Direct text edit in place; or *Revise with agent* instruction | Re-trace claims; re-run pre-flight; new version `vN (edit)` |
| Resume (tailored) | Text blocks of the tailored HTML (summary, bullets, skills order via drag) — not raw HTML | Re-render PDF via `render.py`; re-run three-parser ATS check; re-run facts check (49/49); new version |
| Screening answer (generated) | Direct text edit | Re-trace; pre-flight |
| Screening answer (from resume) | Editable with a warning *"Derived from resume — editing may misrepresent"* | Pre-flight *answers accurate* flips amber until confirmed |
| Screening answer (answer sheet) | Not editable here — link to Settings › Answer sheet | — |
| Master resume | Not editable here — link opens `resume-ats.html` in the editor; banner *"Master changed — N pending applications were tailored from the old master · [Re-tailor all ≈ $x]"* | — |

### 5.4 Bulk actions — what is safe

| Bulk action | Allowed? | Rationale |
| --- | --- | --- |
| **Bulk approve** | **No.** Not offered, not in the command palette, not via multi-select. | HITL-5 is *full review of every tailored resume and cover letter, no spot-checking*. A bulk approve is by definition approving documents unread; combined with C-3 (irreversible, under his name) it converts the system's central safeguard into a checkbox. The design instead makes *serial* approval fast enough (≈ 50 s each) that bulk approval has no legitimate use. If Avadh ever asks for it, the right response is to make the review faster, not to add the button. |
| Bulk reject (with one reason) | Yes, on selection, with a confirm that lists the companies. | Nothing is sent; reversible from Job detail. |
| Bulk dismiss expired | Yes, one key from queue. | Postings are closed; nothing to decide. |
| Bulk skip (by hand) | Yes, on selection, reason required. | Reversible. |
| Bulk mark applied manually | No. | Each creates a tracker row asserting he applied; requires per-row intent. |
| Bulk re-tailor after master change | Yes, with cost estimate. | Spends money, sends nothing. |
| Bulk retry failed sources | Yes. | — |

### 5.5 Carry-over and ageing

- Carry-over applications sort first (O-5) and show age in days. At 3+ days the row gets a
  clock icon; at 5+ days the *job still active* pre-flight is re-run before opening.
- Expired detection is run at 09:00 and on queue open; expired rows lose Approve/Edit and gain
  only Dismiss.
- The dashboard CTA always states the oldest age so a neglected queue is visible in one glance.
- A Telegram *stale approvals* reminder fires after 48 h (configurable) — see §7.

### 5.6 Live updates

The run may still be going when Avadh starts reviewing (09:00 → 09:41). Queue and dashboard
receive live updates; new applications append to the *Today* group without reordering what he
is looking at; a small *"+2 new"* pill appears rather than rows jumping.

---

## 6. FR → UI component map

Required by FR-13.2. **Home** is the primary component; **Also** lists secondary surfaces.
Tier: A = daily, B = investigation, C = system. Rows marked ⚑ have a weak or indirect home and
are discussed below the table.

### 6.1 Functional requirements

| ID | Requirement (short) | Home component | Also | Tier |
| --- | --- | --- | --- | --- |
| FR-1.1 | Search daily across 8 source types | Audit › Sources table (per-source status, counts) §3.9 | Dashboard › Sources card; Settings › Sources | B |
| FR-1.2 | Prefer direct/ATS over aggregators | Audit › Sources *Policy* column + Settings › Sources *Why* column | Queue *Via* column | B |
| FR-1.3 | Geography priority India → Dubai → Europe → Canada | Settings › Targets › Geography priority (ordered toggles) §3.15 | Audit › Queries geography line; Geo column/filter on Jobs; ✈ badge | C |
| FR-1.3a | Extract visa/sponsorship; reject non-sponsoring | Job detail › Hard rules row `FR-1.3a` with JD line §3.13 | Review › Watch (*"visa: sponsored"*); Audit verdict chip *visa 7*; Answer sheet › work-auth impact box | B |
| FR-1.4 | Seniority targeting, never junior | Settings › Targets › Seniority §3.15 | Audit › Jobs reason `FR-1.4 junior`; Job detail Seniority dimension | C |
| FR-1.5 | Title × GenAI keyword queries incl. FDE/"Forward Deployed" | Audit › Queries table (templates, sources, results, best score) §3.9 | — | B |
| FR-1.6 | FDE requires substantial GenAI | Job detail › Hard rules row `FR-1.6` | Review › Watch *"✓ GenAI substantial"* | B |
| FR-1.7 | Surface travel/onsite/client-site | Review › Watch *"⚠ Travel up to 25% (JD line 18)"* §3.4 | Job detail › Hard rules `FR-1.7`; Queue ✈/onsite tag | A |
| FR-1.8 | Daily search audit log: sources, queries, jobs, score, verdict, reason | Audit log screen — Sources / Queries / Jobs tabs §3.9–3.10 | Dashboard funnel links into it | B |
| FR-1.9 | Manual-fallback surface with link and state pending/applied manually/skipped | By hand screen §3.11 (pinned view of Audit › Jobs, fallback filter) | Dashboard › By hand card; Audit › Jobs *Fallback state* filter; Tracker channel `manual` | A |
| FR-2.1 | One position on several boards = one job | Audit › Jobs *Source(s)* cluster column; Job detail › Seen on §3.13 | Dashboard funnel *"−69 dupes"* | B |
| FR-2.2 | Never apply twice; check tracker | Review › Pre-flight *"✓ not duplicate"* §3.4 | By hand duplicate notice (Sirion row); Tracker as authority; Reject/Manual writes tracker | A |
| FR-2.3 | Identity survives cosmetic differences | Job detail › Seen on *"matched by ATS id + title similarity 0.91"* | — | B |
| FR-3.1 | Score 0–100 on rubric | Review › left rail score bars §3.4; Job detail › Score breakdown §3.13 | Score column everywhere | A |
| FR-3.2 | Score from the JD, not the title | Job detail › captured JD with rule-firing lines highlighted; dimension reasons cite JD lines | — | B |
| FR-3.3 | Rank by differentiators | Review › *Why it matches* §3.4; Job detail › Skills/AI-LLM dimension reasons naming differentiators | Report › Top applications *why* | A |
| FR-3.4 | Record score + reasoning for every job incl. rejected | Job detail › per-dimension one-line reasons + *Why rejected* §3.13 | Audit › Jobs reason column | B |
| FR-4.1 | Hard reject list | Job detail › Hard rules panel; Audit › Jobs reason `FR-4.1 <sub-rule>`; verdict chip *hard 41* | Report › Rejected grouped by reason | B |
| FR-4.2 | Reject on absent mandatory qualification (quoted) | Job detail › Hard rules `FR-4.2` with quoted JD line | Review › Pre-flight *"no false qualification"* | B |
| FR-4.3 | Never circumvent mandatory qualification | Job detail › *Promote to queue* **absent** for hard rules, reason shown §3.13 | Pre-flight row | B |
| FR-5.1 | Flag and skip fraud | Audit › Jobs reason `FR-5.1 fraud: <signal>`; Job detail › Hard rules `FR-5.1` | Report › Rejected group | B |
| FR-5.2 | Never provide secrets to forms | Run console › Secrets guard counter §3.18 | Job detail Hard rules when triggered | C |
| FR-6.1 | Tailor by reorder/re-emphasise/reword | Review › Resume **diff** with change classes `−/+`, `~↑↓` §3.4 | — | A |
| FR-6.2 | Factually accurate + visually consistent | Review › Pre-flight *"facts 49/49"* + *Open tailored PDF*; Skills *"nothing added"* label | Edit mode fabrication guard | A |
| FR-6.3 | Record resume version per application | Review › Version block; Tracker › expansion *Resume glean-a1 v1* §3.12 | Edit creates `vN (edit)` | A |
| FR-6.4 | HTML master → render → ATS properties re-verified | Review › Pre-flight *"ATS 3-parser 15/15"*; Run console stage 8; Needs-attention row on failure | Edit mode re-check on save | A |
| FR-7.1 | Concise targeted letter, when requested | Review › Cover letter tab with word count; greyed *"not requested"* state §3.5 | Queue *Docs* column `L`/`–` | A |
| FR-7.2 | Concrete evidence, no filler | Review › Evidence trace markers `[n]` → resume line §3.5 | — | A |
| FR-8.1 | Auto-answer resume-derivable questions | Review › Answers tab, source tag *← resume · <line>* §3.6 | Answer sheet › Used counts | A |
| FR-8.2 | Generate grounded subjective answers | Review › Answers tab, *generated* rows with trace markers | — | A |
| FR-8.3 | Never fabricate; halt | Needs-you-now › Question card §3.19 | Answers tab *halted* count; Dashboard Needs-you-now | A |
| FR-9.1 | 12-point pre-submit verification | Review › Pre-flight checklist (12 rows) §3.4 | Approve disabled on any ✗ | A |
| FR-9.2 | Configurable daily ceiling, never padded | Settings › Targets › Daily ceiling §3.15 | Dashboard funnel *"deferred 19 (over ceiling 15)"*; Review *"Approvals today 2/15 ceiling"*; never a progress bar | A |
| FR-9.3 | Submission requires approval | Approve action + grace window §5.1; Queue | — | A |
| FR-9.4 | Halt and ask rather than guess | Needs-you-now › Question card; Telegram *question* message | Report › Needs attention | A |
| FR-10.1 | Tracker fields (13) | Tracker table + expansion row §3.12 | — | B |
| FR-10.2 | Tracker survives restarts; authority for dedup | Tracker error state banner (write failure visible); Pre-flight *not duplicate* cites tracker | Run console checkpoint events | B |
| FR-11.1 | Daily report (8 sections) | Reports screen §3.17, one collapsible per section | Telegram digest | B |
| FR-12.1 | Run daily without initiation | Header run state + next run; Settings › Schedule §3.16 | Missed-run banner | C |
| FR-12.2 | Resumable runs; multi-day pauses | Run console › checkpoint + *Resume run*; Queue carry-over group with age | Needs-you-now *Continue* | C |
| FR-13.1 | Every FR has a UI component | This table | — | — |
| FR-13.2 | Explicit FR → UI map in spec | This table (§6), to be carried into the spec | — | — |
| FR-13.3 | Minimum surfaces (9 listed) | Audit §3.9–3.10 · Queue §3.3 · Tracker §3.12 · Report §3.17 · Score+reasoning §3.13 · Rejected+reasons §3.10/3.13 · Spend header §2.2 · Ceiling §3.15 · Answer sheet §3.14 | — | — |

### 6.2 Human-in-the-loop requirements

| ID | Requirement | Home component | Also |
| --- | --- | --- | --- |
| HITL-1 | Final submit gate | Review › Approve with grace window §5.1 | Queue |
| HITL-2 | Login/OTP/CAPTCHA handoff | Needs-you-now › Blocked card: *Take over browser · Continue* §3.19 | Telegram *blocked* message; By hand *Resume with agent* |
| HITL-3 | Missing personal data | Needs-you-now › Question card with *Save to answer sheet* | Settings › Answer sheet › Learned from halts |
| HITL-4 | Claim that could misrepresent | Needs-you-now › Question card (claim vs resume line, *Use resume wording*) | Edit mode fabrication guard |
| HITL-5 | Approve tailored resume + letter, every application | Review screen §3.4–3.6; no bulk approve §5.4 | Report › Your review today |
| HITL-6 | Borderline 70–79 (folded into HITL-5, O-3) | Queue › Tier 3 inline caveat *"1 gap flagged"*; Review › Watch gaps | Settings › Targets › Tier 3 handling |
| HITL-R1 | Paused application reviewable/resumable from dashboard | Needs-you-now slide-over from every screen; Queue carry-over | Tracker status `pending Q` |
| HITL-R2 | approve · edit · reject | Review decision panel; Edit mode §3.7; Reject overlay §3.8 | — |
| HITL-R3 | Answer sheet eliminates most HITL-3 | Settings › Answer sheet › *Halts this month* counter + *Learned from halts* | Question card default-checked *Save to answer sheet* |
| HITL-R4 | Pauses may last days; durable | Queue age column; carry-over group; dashboard *oldest N days* | Telegram stale reminder |
| HITL-R5 | Resume never re-executes a side effect | Run console › *Idempotency: submission id … not yet submitted · safe to retry* §3.18; Needs-you-now *Continue — nothing re-executed* | — |

### 6.3 Truthfulness constraints

| ID | Constraint | Home component |
| --- | --- | --- |
| T-1 | Never invent | Review › Pre-flight *"no fabrication"*; diff `+` inside factual sections fails *facts 49/49*; Edit guard §3.7 |
| T-2 | Only reorder/re-emphasise/reword facts | Review › Resume diff change classes; Skills *"reordered · nothing added"* |
| T-3 | Never falsely claim mandatory qualification | Pre-flight *"no false qualification"*; Job detail hard-rule with no override |
| T-4 | Unknown → halt | Needs-you-now › Question card |
| T-5 | Every claim traceable to a resume line | Review › Evidence trace `[n]` markers + *11/11 traced* panel §3.5; unresolved marker blocks approve |

### 6.4 Technical and non-functional requirements

| ID | Requirement | Home component | Note |
| --- | --- | --- | --- |
| TR-1 | Built with LangChain/LangGraph | — | ⚑ Development constraint. No UI. See below. |
| TR-2 | APIs verified against knowledge-base | — | ⚑ Development process. No UI. |
| TR-3 | Backend + frontend dashboard | This document | — |
| TR-4 | Dashboard shows queue, tracker, reports, scores | §3.3 · §3.12 · §3.17 · §3.13 | — |
| TR-5 | Durable state | Run console checkpoint events; Tracker write-failure banner | — |
| TR-6 | Browser automation with handoff | Needs-you-now › *Take over browser* §3.19; Run console live step | — |
| TR-7 | Every LLM/tool call traceable | Run console › per-stage *Trace ↗*; Job detail *trace ↗* | — |
| TR-8 | Secrets never committed/logged/sent | Settings › Data & secrets (presence only, never value); Run console Secrets guard | — |
| TR-9 | Committed to `JobAgent` branch | — | ⚑ Repository process. No UI. |
| TR-10 | Per-stage model configurable | Settings › Models per stage §3.15 | Job detail *Scored by* |
| TR-11 | Per-stage tokens/cost vs ceiling | Settings › Models table (today's calls/tokens/cost); Run console stage costs; header meter | Dashboard spend card |
| TR-12 | Soft alert ~$5 | Header meter soft mark + amber; Settings › Budget; Telegram *cost alert* | — |
| NFR-1 | Durability | Tracker write-failure banner; Run console checkpoint | Visible only on failure — correct for a non-functional property |
| NFR-2 | Idempotency | Run console › submission id + *safe to retry* line | — |
| NFR-3 | Auditability | Tracker expansion › *What was sent* bundle §3.12 | Job detail timeline |
| NFR-4 | One board failing doesn't abort | Audit › Sources ⚠ partial row + Retry; header amber dot | Dashboard Sources card |
| NFR-5 | Rate limiting | Audit › Sources *Pacing* column §3.9 | — |
| NFR-6 | Cost visibility per run | Run console total; Reports spend line | Header |
| NFR-7 | Privacy, no third parties beyond need | Settings › Data & secrets › *Third parties contacted* list §3.16 | — |

### 6.5 Constraints and decisions that need a visible home

| ID | Item | Home component |
| --- | --- | --- |
| C-1 / Q-3 | Discovery-only boards | Settings › Sources *Policy* 🔒 (not a toggle); Audit Sources Policy column; By hand reason `discovery-only` |
| C-2 | CAPTCHAs/OTP need Avadh | Needs-you-now Blocked card; By hand reason `CAPTCHA` |
| C-3 | Submission irreversible | Grace-window undo; *"no unsend"* toast text; no bulk approve |
| C-5 / §2.1 | Answer sheet, sensitive | Settings › Answer sheet masked §3.14; Answers tab shows field name only §3.6 |
| §7.1 | Tiered models | Settings › Models per stage; Job detail *first-pass vs deep* |
| Q-6 / O-5 | 09:00 schedule; carry-over policy | Settings › Schedule §3.16; Queue carry-over group |
| Q-7 | Telegram | Settings › Notifications; §7 |
| Q-8 | $100 ceiling | Header meter; Settings › Budget |
| Q-9 | Keep everything | Settings › Data & secrets retention line; Done group in By hand; Tracker 500+ overflow |
| O-2 | Work authorisation unconfirmed | Answer sheet ⚠ *unconfirmed* status + impact box |
| §9 | Success metrics | Reports › *Your review today*, *Callback rate*; Tracker status advancement |

### 6.6 Requirements without a UI home

Three requirements have **no UI component, by design**, and should be recorded in the spec's map
as *"N/A — development constraint"* rather than left blank:

- **TR-1** (LangChain/LangGraph), **TR-2** (API verification against knowledge-base), **TR-9**
  (commit to the `JobAgent` branch). These constrain how the system is built, not what it does
  for the user. Surfacing them in a dashboard would be theatre. FR-13.1 says *"every functional
  requirement"*; these are not functional requirements.

Two requirements have **indirect homes that the spec should keep honest about**:

- **NFR-1 durability** and **TR-5 durable state** are visible only through failure states (the
  tracker write-failure banner, the run-console checkpoint line). That is correct — a durability
  property that needs a green badge every day is noise — but the spec should not claim a richer
  component than exists.
- **FR-5.2** (never provide secrets) is surfaced as a refusal counter in the run console. It
  will read `0` almost every day. That is the point.

Every other FR, HITL, T, TR and NFR row above has a concrete component.

---

## 7. Telegram notification design

Telegram is the *only* channel that reaches Avadh when he is not at the PC, and every gate that
nobody sees is a stalled application. Design principles:

1. **Each message is useful without opening the link.** The link may be dead (see the localhost
   problem below). The message must let him decide *whether* to go to the PC.
2. **One message per event class per run; batch within a class.** Fourteen "approval ready"
   pings are a mute button waiting to happen.
3. **Never include an answer-sheet value, a secret, or a CTC figure** (§2.1).
4. **Telegram is notify-only in v1.** No approve/reject buttons. Approving from a phone without
   the diff and the trace is spot-checking, which Q-2 rejected. Reject-from-phone is harmless but
   half a feature; leave it out until the review ritual is proven.
5. Deep links carry the route and the id so they work as soon as the base URL is reachable.

**The localhost problem, stated plainly.** The app runs on Avadh's PC; `http://localhost:8765/…`
means nothing on his phone. Settings › Notifications exposes the base URL so a LAN address or a
Tailscale hostname makes the links live from anywhere on his network. Until he does that, the
links only work when he is already at the PC — which is why principle 1 exists.

### 7.1 Message types

**M1 — Approvals ready** (once per run, after tailoring finishes; suppressed if 0)

```
🟢 JobAgent · Mon 14 Sep

14 applications ready for review · est. 13 min
 3 carried over from Fri (oldest 3 d) · 11 new · 1 expired

Top of the queue
 94  Glean — Senior Forward Deployed Engineer · Bengaluru hybrid
 91  Sierra — Forward Deployed AI Engineer · Remote (India ok)
 89  Careem — Senior AI Engineer, Agentic Platforms · Dubai ✈

Also: 6 to apply by hand (best Sprinklr 88) · 1 question needs you (Postman)

Review → http://localhost:8765/queue
```

**M2 — Blocked: needs you now** (immediately, per blocked job; the run continues)

```
🔴 Blocked — Careem · Senior AI Engineer (Workday)

Needs your login/OTP to continue. Agent paused at step 3/9 (sign-in).
Other jobs continue. Nothing has been submitted for this job.

At the PC: Take over browser → sign in → Continue.
Or: send it to the by-hand list.

Open → http://localhost:8765/?needs=careem-c3
```

**M3 — Question needs your answer** (immediately, per halt)

```
🟠 Question — Postman · Senior AI Platform Engineer (Lever)

The form asks:
"Have you ever been terminated from employment? If yes, please explain."
(free text, max 500)

Not answerable from your resume or answer sheet — I won't guess.
Answer once at the PC and it can be saved to the answer sheet.

Answer → http://localhost:8765/?needs=postman-p1
```

**M4 — Daily report digest** (after report stage; always sent, even on a quiet day)

```
📋 JobAgent report · Mon 14 Sep · run 09:00–09:41

Found 212 · Unique 143 · Rejected 106 · Passed 37
Queued 14 · By hand 6 · Submitted 0 (awaiting your review)
Spend $3.86 of $100 · Sources 7/8 (Indeed partial — 429)

Top matches
 94 Glean · Sr FDE · BLR — FDE + MCP + enterprise integrations
 91 Sierra · FDE AI · Remote — agentic customer deployments
 89 Careem · Sr AI Eng · Dubai ✈ — agentic platform, sponsors

Rejected: <70 ×58 · non-AI/classical ML ×23 · junior ×9 · no sponsorship ×7
 · mandatory qual ×6 · expired ×2 · fraud ×1

Needs you: Postman question · Uniphore ATS fix · Indeed retry
Follow-ups due this week: 3

Full report → http://localhost:8765/reports/2026-09-14
```

**M5 — Submissions done** (once, after the last approved application submits — closes the loop
on J1 so he knows nothing is stuck)

```
✅ 12 submitted · Mon 14 Sep 10:31

Glean · Sierra · Careem · Druva · Observe.AI · Property Finder · Innovaccer
· Kore.ai · Freshworks · Icertis · Whatfix · Sirion

1 rejected by you (Zeta) · 1 expired (Yellow.ai) · 0 failed
Confirmations received: 11 of 12 (Kore.ai — none yet, will re-check)

Tracker → http://localhost:8765/tracker
```

**M6 — Submission failed** (immediately)

```
🔴 Submission failed — Kore.ai · Senior AI Platform Engineer

Failed at step 7/9 ("answer questions"): form changed since tailoring —
new required field "Preferred work location".
Nothing was submitted. Safe to retry.

Options at the PC: Answer & retry · Send to by-hand · Abandon
Open → http://localhost:8765/?needs=koreai-k1
```

**M7 — Cost soft alert** (once per run when crossing $5; again at $25, $50; hard stop at $100)

```
🟡 LLM spend $5.12 today — over the $5 soft alert

Run continues. Ceiling $100.
Where it went: screen $0.41 · deep $1.30 · tailor $3.41
Unusual: 2 retry loops on Workday tailoring (Careem, Property Finder).

Run console → http://localhost:8765/runs/2026-09-14
```

**M8 — Run failed / missed** (09:15 if not started; immediately on crash)

```
🔴 Today's run did not start — Mon 14 Sep

Scheduled 09:00 · PC appears to have been asleep.
Policy: run when it wakes → it will start automatically.
Pending approvals from Fri are unaffected (3 waiting).

Or run now → http://localhost:8765/runs
```

**M9 — Stale approvals reminder** (after 48 h with pending items; then every 48 h)

```
⏳ 5 applications have waited 2+ days

Oldest: Icertis · AI Solutions Architect (3 d). Postings do close —
2 of the 5 were last seen active on Fri.

Review → http://localhost:8765/queue
```

### 7.2 Message ↔ gate coverage

| Gate / event | Message | Latency |
| --- | --- | --- |
| HITL-1/5 approvals waiting | M1 (batched), M9 (stale) | End of tailoring; 48 h |
| HITL-2 blocked | M2 | Immediate |
| HITL-3/4 question | M3 | Immediate |
| Submission outcome | M5 (batched), M6 (failure) | After last submit; immediate |
| FR-11 report | M4 | End of run |
| TR-12 soft alert | M7 | Immediate |
| FR-12.1 missed / crash | M8 | 09:15 / immediate |

Every gate in §5 of the requirements has a message; no gate relies on Avadh happening to look at
the dashboard.

---

## 8. UX problems created by the requirements — said plainly

| # | Problem | Consequence | Design response |
| --- | --- | --- | --- |
| P-1 | **HITL-5 full review × 10–20/day is a reading task.** If tailoring rewrites whole sections, the "diff" is the whole page and the 60-second budget dies. | Review fatigue → approve reflex → the gate protects nothing. This is the single biggest UX risk in the system. | Diff-by-default; heavy-rewrite banner (> 40 changes) nudging *regenerate with minimal changes*; evidence markers so the letter is skimmed for `[n]` not read for truth; *Your review today* median-time and reject-rate telemetry in Reports so rubber-stamping is measurable. **The spec should also constrain tailoring output to be diff-friendly** (reorder > rewrite; rewrite summary only). |
| P-2 | **Telegram links point at localhost.** | Every gate message has a dead link on the phone; a blocked application waits until he happens to sit down. | Messages self-sufficient; base URL setting with LAN/Tailscale guidance; stale reminders. Not fully solvable in UI. |
| P-3 | **§2.1 must be in the UI (FR-13.3) but never shown on a shared surface.** | Any place the answer sheet leaks (Answers tab, log, report) is a privacy defect. | Values rendered only in Settings › Answer sheet behind a reveal toggle; every other surface shows the field *name*. |
| P-4 | **FR-9.2 "ceiling, not quota" versus a dashboard's instinct to draw progress.** | A progress bar to the ceiling reads as a shortfall and nudges toward padding. | Ceiling shown as a small label, deferred count shown as *"over ceiling"*; no bar. |
| P-5 | **FR-1.9 fallback list without prepared documents is a to-do list Avadh won't do.** FR-6.1 only mandates tailoring where upload is allowed. | High-score Naukri/LinkedIn jobs — often the best Indian roles — get skipped. | Recommend tailoring for fallback jobs ≥ 80 and making downloads the centre of the By hand screen. Exceeds FR-6.1's letter; the spec should adopt or reject explicitly. |
| P-6 | **FR-4.1/4.3 forbid override; users expect an override.** | Frustration when the agent hard-rejects a job Avadh wants. | *Promote to queue* exists for soft rejections only; for hard rules the button is absent and the reason is quoted from the JD, so the disagreement is with the JD, not the software. |
| P-7 | **FR-13.1 taken literally produces a dashboard of sixty counters.** | The one number that matters (pending reviews) drowns. | Three visibility tiers; funnel as the daily spine; system requirements live in Run console and Settings. |
| P-8 | **The 09:00 run on a PC that may be asleep.** | Silent no-run days. | Explicit missed-run state, banner and M8. |
| P-9 | **O-2 work authorisation unconfirmed but load-bearing.** | Silently rejecting 20+ jobs a month on an unconfirmed assumption. | Answer sheet impact box quantifies the cost of the default setting and links to the rejected jobs. |

---

## 9. Handoff notes for the specification

- Adopt §6 as the FR → UI map required by FR-13.2; record TR-1/TR-2/TR-9 as *N/A — development
  constraint* rather than leaving them unmapped.
- Two design recommendations exceed the requirements and need an explicit decision: tailoring
  for fallback jobs ≥ 80 (P-5), and constraining tailoring output to be diff-friendly (P-1).
- Two telemetry items are not in FR-11.1 but are needed for §9 metrics: review time per
  application and reject-reason distribution (§3.17 *Your review today*); callback rate from
  tracker status advancement.
- Keyboard map (§5.2), grace-window approve (§5.1) and the no-bulk-approve rule (§5.4) are
  design decisions, not options; the spec should treat them as requirements of the frontend.
- Route scheme in §2.1 is illustrative; ids and ports are the spec's to define.

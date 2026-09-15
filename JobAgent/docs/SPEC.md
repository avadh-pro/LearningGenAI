# JobAgent — Technical Specification

**Project:** Autonomous AI/ML Job Search & Application Agent
**Owner:** Avadh Dobariya
**Inputs:** `docs/REQUIREMENTS.md` v0.5 (approved) · `docs/requirements-analysis.md` (assumption register §7 adopted; exceptions in §17) · `docs/test-plan.md` (277 acceptance criteria — every one must be satisfiable by this design) · `docs/ui-ux-design.md` (19 screens, FR→UI map) · `knowledge-base/` (LangChain 1.x / LangGraph API truth)
**Status:** Phase 3 — specification for implementation by Sonnet/Opus
**Version:** 2.3 · 2026-09-15 (supersedes v1.0, REJECTED by CTO review 2026-09-15)
**Revision:** v2.0 closed the ten CRITICAL findings (C-1..C-8, C-10, C-11) and the four MAJORs
the review required in the same pass (M-1, M-2, M-3, M-15). **v2.1 answers Q-S on measured
evidence and re-cuts the plan into two releases (§15.0). v2.2 closes M-16 and M-19, and v2.3 closes
M-22 and M-13 — every MAJOR that sat inside Release 1's own path.** Changelog: §20. Findings *not* closed
are listed in §21 — they are open, not resolved.

> This document says **how**. Every LangChain/LangGraph symbol named here was grepped in
> `knowledge-base/` before it was written down; §18 is the verification table. Anything that
> could not be verified is marked **[UNVERIFIED]** rather than asserted — and in v2 every
> `[UNVERIFIED]` mark that names a LangChain/LangGraph behaviour has been re-derived against
> `knowledge-base/` and either verified with a citation or deleted (§18, §20 M-1/M-2/M-3).
> Where this spec departs
> from the requirements, the assumption register or the UI design, the departure is tagged
> **DEPARTURE D-n** inline and collected in §17.

---

## Table of contents

1. Executive summary
2. Objectives and non-goals
3. System architecture
4. Component design
5. LangGraph graph design
6. Data model and persistence
7. API specification (serving the 19 screens)
8. The anti-fabrication verifier (FactGuard)
9. The submission protocol
10. Tailoring contract (diff-friendly by construction)
11. Form filling, the answer sheet and `years_by_technology`
12. Security, secrets and privacy
13. Operations: scheduling, run lock, budget, observability
14. Frontend specification and FR → UI map
15. Phased implementation plan
16. Risk register
17. Departures from requirements / assumptions / UI design
18. Knowledge-base verification table
19. Open questions
20. Changelog — what v2 changed, and which finding it closes
21. Findings not closed in v2

---

## 1. Executive summary

JobAgent is a single-user, local-PC system that runs once a day at 09:00 IST, discovers AI
engineering roles across eight source types, evaluates them against a fixed rubric, prepares
tailored application documents for the 10–20 best, and — only after Avadh has reviewed every
document — submits applications on Greenhouse, Lever and direct career pages (Workday assisted).
The objective function is interview probability per application; the system is built to refuse
work rather than pad, and to halt rather than guess.

Four properties dominate the design and are treated as architecture, not as behaviour to be
asked of a model:

| Property | Mechanism | Where |
| --- | --- | --- |
| **No double submission, ever** (NFR-2, HITL-R5, C-3) | Three-state submission protocol in the tracker (`SUBMITTING` written durably *before* the click; `SUBMITTED` only after evidence is stored); a submit node that never clicks when it finds `SUBMITTING`; `RetryPolicy.retry_on` restricted to a `PreClickError` class; **the same durable-marker discipline applied to every page-advancing POST in `fill_form`** (§9.8); `UNKNOWN_OUTCOME` hands the question to a human, is never manufactured by a second process (§9.6), and costs a typed confirmation and a waiting period to resolve the one way that clicks again (§9.5). | §9 |
| **No fabrication, ever** (T-1..T-5) | A deterministic fact ledger built from the master resume; a generator that emits a *plan* (element keys + provenance pointers), never free HTML; a verifier (FactGuard) that runs on every artefact, fails closed, and blocks the `SUBMITTING` transition without a fresh pass on the exact artefact hashes. | §8, §10 |
| **Answer-sheet values never reach an LLM** (§2.1, NFR-7) | Values live in one table, are loaded only inside the deterministic `FormFiller`, never enter graph state (hence never checkpoints), and a `GuardedModel` wrapper asserts on every outbound prompt — **with no unwrapped path: `.inner` is banned by static check, and the one agentic component is guarded by middleware** (§4.13, §5.4). Masked *in transit*; **never masked from the reviewer** — every value that will be typed into a form is rendered in full on the review screen (§11.7, C-7). | §11, §12 |
| **Review stays a 60-second task** (HITL-5, UI D-2) | Tailoring is reorder-first; only the professional summary may be rewritten; the change budget is enforced by the plan schema; the diff the reviewer sees is the diff the verifier checked, and the values the reviewer sees are the values the employer receives. | §10, §11.7 |

**Release 1 does not submit.** On measured evidence (§15.0) the system ships first as a
discovery, tailoring, verification and hand-over tool: it finds the roles, produces the documents,
proves they contain no fabrication, and hands them to Avadh to send. `submission_enabled` stays
`false` and the `submit` node is not built until Release 2. Everything below is specified for the
complete system; §15.0 says which parts are in which release.

The runtime is **exactly one** Python process (`jobagent serve`) — a named OS mutex makes a
second instance refuse to start before it can touch a record (§9.6, C-10) — hosting a FastAPI backend bound to
`127.0.0.1`, two LangGraph graphs on an on-disk SQLite checkpointer, a Playwright browser
worker with a persistent profile, a Telegram poller, and an in-process scheduler. The frontend is
a keyboard-first single-page dashboard served by the same process. State that matters
(tracker, audit log, artefacts, decisions, spend) lives in a relational SQLite database that is
the system of record; LangGraph checkpoints are execution scaffolding and are pruned.

---

## 2. Objectives and non-goals

### 2.1 Objectives (what "done" means)

| # | Objective | Measured by |
| --- | --- | --- |
| O1 | Every acceptance criterion in `docs/test-plan.md` is implementable against this design; the AF and ID groups pass 100% before any real submission. | test-plan §17 exit criteria |
| O2 | 10–20 applications/day ceiling, never padded, each fully reviewed by Avadh in ~60 s. | AC-SB-17..20, AC-NF-15 |
| O3 | Zero fabricated claims, zero duplicate submissions, zero sub-70 submissions. | AC-AF-14, AC-ID-23, AC-SC-07 |
| O4 | Runs survive process kills and multi-day pauses with no lost or duplicated work. | AC-ID-19, AC-FM-05..07 |
| O5 | Spend visible per stage; a runaway loop is caught at $5 and stopped at $20. Every model call in the system is counted, including the career-page mapper's. | AC-FM-08..10, AC-NF-09 |
| O7 | A fresh install cannot submit to a real employer. `submission_enabled` is `false` until Avadh types the confirmation to enable it. | AC-SB-21 (new), test-plan §17 gate |
| O6 | Every FR has a UI home (map in §14.4). | AC-UI-01 |

### 2.2 Non-goals (v1)

- Non-AI/ML roles; interview prep; recruiter outreach; paid boards (REQ §3.2).
- Automated submission on LinkedIn / Naukri / Indeed / Wellfound (discovery-only, A-18).
- Fully automated Workday (assisted only, A-18, analysis §5.1).
- Multi-agent orchestration. One `StateGraph` per concern with deterministic nodes and a small number of model calls (analysis §4; CORE-CONCEPTS gotcha 14).
- Remote access to the dashboard (binds to loopback, A-16). LAN/Tailscale exposure is a documented manual step, not a feature.
- Hosted tracing (off by default; local trace store, A-15/G-C5).
- Learning from Avadh's rejections (recorded and reported, not acted on, G-I7).

---

## 3. System architecture

### 3.1 Context

```
                         ┌──────────────────────────────────────────────────────┐
   09:00 IST             │             Avadh's Windows PC (local only)          │
   Task Scheduler ──────▶│  jobagent serve  (one Python 3.13 process)           │
   (at logon: start      │                                                      │
    service)             │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
                         │  │ Scheduler    │  │ FastAPI      │  │ Telegram   │  │
   Avadh (browser) ─────▶│  │ 09:00 + wake │  │ 127.0.0.1:   │  │ long-poll  │◀─┼──▶ api.telegram.org
   http://127.0.0.1:8765 │  │ catch-up     │  │ 8765 + SSE   │  │ 1 chat_id  │  │
                         │  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  │
                         │         └──────────┬───────┴───────────────┘         │
                         │                    ▼                                 │
                         │        ┌───────────────────────┐                     │
                         │        │  Orchestrator         │                     │
                         │        │  run lock · thread    │                     │
                         │        │  locks · budget gate  │                     │
                         │        └───┬───────────────┬───┘                     │
                         │            ▼               ▼                         │
                         │  ┌──────────────────┐ ┌──────────────────┐           │
                         │  │ DiscoveryGraph   │ │ ApplicationGraph │  LangGraph│
                         │  │ 1 thread / run   │ │ 1 thread / app   │  StateGraph
                         │  └────────┬─────────┘ └────────┬─────────┘           │
                         │           │  AsyncSqliteSaver  │  durability="sync"  │
                         │           ▼                    ▼                     │
                         │  ┌─────────────────────────────────────────────┐     │
                         │  │ Services: SourceAdapters · Dedup · Eligibility│    │
                         │  │ Scorer · Ledger · Tailor · FactGuard · Forms │    │
                         │  │ BrowserWorker(Playwright) · Notifier · Spend │    │
                         │  └─────────────────────────────────────────────┘     │
                         │           │                    │                     │
                         │  ┌────────▼────────┐  ┌────────▼─────────┐           │
                         │  │ jobagent.db     │  │ checkpoints.db   │  SQLite   │
                         │  │ (system of      │  │ (LangGraph       │  WAL      │
                         │  │  record)        │  │  scaffolding)    │           │
                         │  └─────────────────┘  └──────────────────┘           │
                         │  art/ <sha256[:16]>.{html,pdf,txt,png,json}          │
                         │  browser-profile/   traces/ (local only)             │
                         └──────────────────────────────────────────────────────┘
                                   │                       │
                LLM providers ◀────┘                       └────▶ job sources / ATS
             (Anthropic, OpenAI —                               (Greenhouse, Lever, Workday,
              keys from Windows                                  career pages; LinkedIn/Naukri/
              user registry)                                     Indeed/Wellfound read-only)
```

Outbound hosts are exactly: configured LLM providers, configured job sources, `api.telegram.org`.
Nothing else (AC-NF-03). The E2E suite runs everything through a capturing proxy to prove it.

### 3.2 Process model

One process, several cooperating asyncio tasks. Rationale: a single Windows PC, a single user,
SQLite as the store — multiple processes would only add lock contention and a second failure
domain. The one thing that *must* be isolated is the browser, which Playwright already runs as a
child process.

**Exactly one process — enforced, not assumed (C-10).** SQLite in WAL mode is *designed* to allow
concurrent multi-process access, so the store will not reject a second instance; and Task Scheduler
is configured to restart the service on failure, so a hung-but-alive process plus a restart is an
everyday path to two live instances. `jobagent serve` therefore takes a **named OS mutex**
(`Global\JobAgent.serve`, via `win32event.CreateMutex`; a pid-bearing exclusive lock file is the
cross-platform fallback) as its **first action, before any database connection is opened**, and
exits with a clear message naming the holding pid if it is already held. Binding
`127.0.0.1:8765` is the second action and a backstop if the mutex ever fails. Only after both
succeed does startup reconciliation run (§9.6). The ordering is the point: v1 reconciled first and
discovered the port collision afterwards, which gave a doomed second process a window in which to
rewrite live rows.

| Task | Responsibility | Concurrency |
| --- | --- | --- |
| `api` | FastAPI/uvicorn on `127.0.0.1:8765`; REST + SSE; serves the SPA | async |
| `scheduler` | Fires the 09:00 run; catch-up on start if missed and before 20:00; 21:00 evening digest; 48 h stale reminder; retention job | async |
| `run_supervisor` | Holds the process-wide run lock; drives `DiscoveryGraph` for one run; fans out `ApplicationGraph` threads (bounded, default 2 concurrent tailorings) | async |
| `resume_worker` | Consumes decisions (dashboard/Telegram) → acquires thread lock → `Command(resume=...)` on the right thread | async, 1 per thread |
| `browser_worker` | Owns the single Playwright persistent context; executes form-fill and submit steps requested by application threads; serialised (one form at a time — NFR-5 and hand-off simplicity) | 1 |
| `telegram_poller` | `getUpdates` long-poll; accepts commands only from the configured `chat_id` | async |
| `notifier` | Drains the `notifications_outbox` table with back-off (AC-FM-11) | async |

Every task is supervised: a crash is logged, an `audit_events` row written, and the task
restarted with back-off. A crash of the whole process is recovered on next start by the
**startup reconciliation** routine (§9.6, §13.4).

### 3.3 Technology choices

| Concern | Choice | Alternatives considered | Why |
| --- | --- | --- | --- |
| Orchestration | LangGraph `StateGraph` (Graph API) | Functional API (`@entrypoint`/`@task`) | TR-1. Graph API gives an inspectable topology that AC-ID-25 (static inspection of nodes/edges) and AC-ID-13/14 (static checks on node functions) can test. Functional API hides topology in control flow. |
| LLM access | `init_chat_model("provider:model")` per stage; `create_agent` only for the form-filling agent | `create_agent` for everything | Scoring, tailoring and letter generation are single structured-output calls with no tool use — an agent loop adds cost and nondeterminism. Form filling genuinely needs tool-calling autonomy (inspect form → map fields → fill) and benefits from `HumanInTheLoopMiddleware` on the submit tool. |
| Checkpointer | `AsyncSqliteSaver` (`langgraph-checkpoint-sqlite`) on `checkpoints.db` | `SqliteSaver` (sync); Postgres | Backend is async (FastAPI); Postgres is a server on a PC that should have none (Q-5). `InMemorySaver` is refused at boot outside tests (AC-ID-24). |
| System of record | SQLite (WAL) via SQLAlchemy 2.x Core, `jobagent.db` | Same file as checkpoints; Postgres | A-2 separates records from scaffolding; separate files let checkpoints be pruned/vacuumed without touching records (A-17) and keep the checkpoint file's growth off the tracker's fsync path. |
| Browser | Playwright (Python) persistent context | Selenium; requests-only | Already required by `render.py`; persistent profile satisfies TR-6 (AC-SB-16); hand-off by simply leaving the window open (AC-HL-12/13). |
| Backend | FastAPI + uvicorn, SSE for live updates | Flask; WebSockets | Async fits the graph runtime; SSE is one-directional and enough for AC-UI-15 (≤ 5 s). |
| Frontend | Vite + React + TypeScript SPA, served statically by the backend | Server-rendered templates | Keyboard-first review screen with live diff/markers is interaction-heavy; a SPA is the honest choice. |
| Scheduler | APScheduler (in-process) + Windows Task Scheduler to start the service at logon | Task Scheduler alone | The process must be alive anyway for approvals and Telegram; an in-process scheduler can implement the wake catch-up rule (A-19) and the 21:00 digest. **[UNVERIFIED — APScheduler is outside the knowledge base; any cron-capable async scheduler is acceptable.]** |
| PDF rendering | `resume/render.py` (Chromium via Playwright) called as a subprocess | Reimplement | FR-6.4 names it. It takes `[input.html] [output.pdf]` (verified by reading the file). |
| Three-parser ATS test | `pdfminer.six`, `pypdf`, `PyMuPDF` | — | FR-6.4 / resume README name them. |

Python 3.13 (resume README). Pin `langchain>=1.3.3` (conditional interrupts) and
`langgraph>=1.2` (per-node `timeout=`, `error_handler=`, `RunControl` drain) — both minimums
appear in the knowledge base.

### 3.4 Data flow for one day

```
09:00  DiscoveryGraph(thread=run_id)
       discover ─▶ dedup ─▶ extract_facts(screen model) ─▶ eligibility rules ─▶ score(analyse model)
       ─▶ select(ceiling, carry-over) ─▶ spawn ApplicationGraph threads ─▶ report ─▶ notify M4/M1
                                              │
       for each selected job:                 ▼
       ApplicationGraph(thread=application_id)
       load ─▶ probe_form ─▶ answer_questions ─▶ tailor ─▶ render+ats_check ─▶ letter ─▶ factguard
       ─▶ notify_review_ready ─▶ [await_review: interrupt] ─▶ record_decision ─▶ preflight
       ─▶ submit (browser) ─▶ [await_unknown_resolution: interrupt if UNKNOWN_OUTCOME] ─▶ finalize
                 ▲
09:40+ Avadh reviews on the dashboard; each Approve → resume_worker → Command(resume=decision)
21:00  Evening digest M5
```

---
## 4. Component design

Each component: purpose · interface · behaviour · dependencies · error handling. Module paths are
under `src/jobagent/`. Names are binding for the implementers because the static checks in the
test plan (AC-ID-13/14/24/25, AC-NF-11) grep for them.

### 4.1 `config` — Settings and model registry

**Purpose.** Single typed source for every configurable value (FR-9.2, TR-10, TR-12, A-15, A-19, A-21).

**Interface.**
```python
class Settings(BaseModel):            # persisted in table `settings`, hot-reloaded (AC-SB-19)
    submission_enabled: bool = False  # C-11 master switch: false ⇒ the system cannot click at a real employer
    daily_ceiling: int = 20           # 0..40 (UI §3.15); 0 allowed (AC-SB-20)
    models: dict[Stage, str]          # {"screen": ..., "analyse": ..., "generate": ..., "judge": ...}
    budget: Budget                    # soft_alert_usd=5, hard_stop_usd=20, ceiling_usd=100 (max)
    schedule: Schedule                # run_at="09:00", tz="Asia/Kolkata", catch_up_until="20:00", digest_at="21:00"
    geography_priority: list[str]     # FR-1.3 order; toggles
    strong_companies: list[str] = []  # A-12
    telegram: Telegram                # chat_id, base_url="http://127.0.0.1:8765", stale_hours=48  (no approve flag — M-13)
    sources: dict[str, SourceConfig]  # enabled, daily_request_cap, min_interval_s=(3,8)
    tailor_fallback_min_score: int = 80   # DEPARTURE D-3, §17
    rate_limit: RateLimit             # A-21
    retention_days_checkpoints: int = 30
    hosted_tracing: bool = False
    data_dir: Path                    # default %LOCALAPPDATA%\JobAgent  (§6.6)
```
`Stage = Literal["screen", "analyse", "generate", "judge"]`.

**DEPARTURE D-1.** A-23 defines three stage keys. This spec adds a fourth, `judge`, because
AC-AF-08 requires the entailment judge to be *a different model from the generator*. Default:
`judge` = the `analyse` model; validation refuses `judge == generate`.

**Model registry.** `get_model(stage) -> GuardedModel` wraps
`init_chat_model(settings.models[stage])` (§4.13). Default strings — the only Anthropic strings
verified in the knowledge base are `claude-haiku-4-5-20251001` (`models.md`), `claude-sonnet-4-6`
(many pages) and `anthropic:claude-opus-4-8` (`middleware__built-in.md`):

| Stage | Default | Note |
| --- | --- | --- |
| `screen` | `anthropic:claude-haiku-4-5-20251001` | bulk; ~140 calls/run |
| `analyse` | `anthropic:claude-sonnet-4-6` | ~40 calls/run |
| `generate` | `anthropic:claude-opus-4-8` | ≤ 20 apps × ~3 calls |
| `judge` | `anthropic:claude-sonnet-4-6` | must differ from `generate` |

Model availability and pricing are provider facts the implementer must confirm at build time; the
price table (`config/prices.yaml`) is configuration, not code (AC-NF-09 "within 1%").

**`submission_enabled` — the real-submission master switch (C-11).** The test plan's go-live gate
("Enable real submission … no exceptions, no waivers") is phrased as a switch being thrown, and v1
had no switch: its only limiter was `daily_ceiling`, and a ceiling of 1 is not "cannot submit" — it
permits one real application per day from the moment the code first runs, including during a
developer's manual test against a real URL and including the day `submit` is first wired up in
Phase 2. This matters concretely for this project: the fake ATS (T-2.5) arrives in Phase 2 and the
real source adapters (T-4.2) in Phase 4, so the two coexist on one machine under one settings row
for three phases.

- Default `false`, on a fresh install and after any settings reset (AC-SB-21).
- Checked in **two** places: `submit` gate (1), before any browser work (§9.3), and `fill_form`
  before the first page-committing POST (§9.8). Either raises `SubmissionDisabled` → status
  `NEEDS_ATTENTION`, a guard event, and no browser action. Both checks are required because after
  C-1 the irreversible surface is not only the final click.
- Turning it **on** requires a typed confirmation in Settings (`ENABLE REAL SUBMISSION`) and writes
  an `audit_events` row on every change, on or off.
- A static check asserts the default literal is `False`; an AC asserts a fresh install refuses to
  submit; `daily_ceiling` remains a second, independent limit rather than the only one.
- Exempt: `documents_only` threads, which never reach `fill_form` or `submit`, run normally with
  the switch off. That is what makes the non-submitting product shippable on its own (§21, Q-S).

**Error handling.** Invalid settings are rejected at the API with field-level errors; the
previous value stays effective (UI §4 Settings error state). `hard_stop_usd > ceiling_usd` is
refused (AC-FM-10).

### 4.2 `sources` — Source adapters and the company watchlist

**Purpose.** FR-1.1, FR-1.2, FR-1.5, FR-1.8, NFR-4, NFR-5, G-C11, A-18, A-21.

**Interface.**
```python
class SourceAdapter(Protocol):
    name: str                      # greenhouse | lever | workday | career_page | wellfound | linkedin | naukri | indeed
    policy: Literal["auto_apply", "assisted", "discovery_only"]   # fixed per source (Q-3); not a setting
    async def search(self, queries: list[Query], ctx: SourceContext) -> AsyncIterator[RawPosting]
    async def fetch_posting(self, url: str) -> PostingPage        # full JD body; raises JdUnavailable
```
`RawPosting = {source, url, title, company, location_text, posted_at?, ats_job_id?, snippet}`.
`PostingPage = {url_final, http_status, html, text, title, closed_markers: list[str], fetched_at}`.

**Behaviour.**
- The **query matrix** is generated from §4.1.1 titles × FR-1.5 keywords, plus both
  `Forward Deployed Engineer` and `FDE` forms, per geography bucket (AC-DS-01). Every issued
  query string is written to `queries` before the request is sent.
- **Greenhouse / Lever / Workday** adapters do not "search the platform"; they iterate the
  **company watchlist** (`company_watchlist` table, UI-editable, seeded by Avadh, auto-grown from
  companies seen on aggregators with a discoverable board URL). Greenhouse and Lever expose public
  board JSON feeds per company slug **[UNVERIFIED — external APIs outside the knowledge base; the
  implementer must confirm endpoints and terms]**. Workday tenants are fetched via their public
  `*.myworkdayjobs.com` listing pages.
- **Career pages** adapter: per-domain listing URL + CSS/JSON extraction rule stored on the
  watchlist row; falls back to sitemap/`/careers` heuristics.
- **LinkedIn / Naukri / Indeed / Wellfound**: best-effort, **logged-out public pages only**,
  never Avadh's session (G-I8). Any challenge (CAPTCHA page, 403, 429) → source marked
  `rate_limited` for 24 h, run continues (AC-FM-02, AC-NF-02).
- **Pacing** (A-21): per-domain semaphore of 1; jittered 3–8 s gap; exponential back-off on
  429/403 starting at 60 s, doubling, pause after 3 consecutive (AC-NF-01/02); daily request cap
  per source from settings. Implemented once in `PacedClient` (httpx), shared by all adapters and
  by `fetch_posting`.
- Per-source isolation: each adapter runs in its own coroutine under
  `asyncio.gather(return_exceptions=True)`; a failure writes `source_runs.status='failed'` and
  never aborts the run (AC-FM-01).

**Error handling.** `JdUnavailable` → job recorded with `verdict=jd_unavailable`, never scored
(AC-SC-02, AC-DS-13, AC-FD-14). Network errors → back-off then `source_failed`.

### 4.3 `dedup` — Job identity

**Purpose.** FR-2.1..2.3, A-10, G-C9.

**Interface.**
```python
def canonical_url(url: str) -> str          # strips utm_*, gh_src, ref, fragment, trailing slash; https; lowercase host (AC-DD-02)
def normalise_company(name: str) -> str     # legal-suffix strip, case-fold, punctuation (AC-DD-06); "Acme Technologies" stays distinct
def title_family(title: str) -> str         # strips seniority tokens, level suffixes, parentheticals; "Sr."→"Senior" (AC-DD-03)
def jd_similarity(a: str, b: str) -> float  # 5-shingle Jaccard on normalised text
def identity_for(posting: RawPosting, page: PostingPage | None) -> JobIdentity
async def resolve(posting, page) -> tuple[Job, bool]   # (job, created)
```
`JobIdentity = {ats_job_id?, company_norm, title_family, location_norm}` hashed to `identity_key`.

**Behaviour (in order).**
1. If the posting carries an ATS job id (Greenhouse/Lever/Workday URL patterns, or an aggregator
   page linking to one), identity = `(ats, ats_job_id)`; the ATS URL becomes `canonical_url`
   and the apply target (AC-DD-01, AC-DS-09).
2. Else identity = `(company_norm, title_family, location_norm)`.
3. **Merge pass**: for a new record, compare JD text with existing records of the *same
   company* within 180 days; similarity ≥ 0.85 → merge as `duplicate_repost` (AC-DD-04); JD
   similarity never merges across companies (AC-DD-13). 0.4 stays separate (AC-DD-05).
4. **Applied block**: if the tracker holds an application for the same `(company_norm,
   title_family)` with status in {SUBMITTED, MANUAL, UNKNOWN_OUTCOME, SUBMITTING,
   REJECTED_BY_USER} within 180 days → verdict `already_applied` / `duplicate_repost`, never
   queued (AC-HR-11, AC-ID-22, AC-DD-09, AC-HL-03). After 180 days with similarity < 0.85 →
   `possible_repost`, surfaced, neither auto-queued nor auto-rejected (AC-DD-11).
5. Same requisition posted for two locations with identical JD → one **position family**;
   the higher-priority location is the application target; the other is stored in
   `job_sources` as an alternative (AC-DD-07).
6. Agency postings naming the client merge with the client's ATS record; "confidential client"
   postings stay separate with flag `agency_confidential` (AC-DD-12).

The database enforces `UNIQUE(identity_key)` on `jobs` and `UNIQUE(job_id)` on `applications`
(AC-ID-17) — the last line of defence, independent of this module.

### 4.4 `ledger` — Fact ledger and element keys

**Purpose.** The oracle for T-1..T-5 and the addressing scheme for provenance pointers (AC-AF-01).

**Finding.** `resume/resume-ats.html` has **no `id` attributes** (verified by grep). T-5 and the
test plan speak of "element ids", and AC-AF-08 requires a claim's provenance pointer to name *an
existing element id in the master*.

**v2 ruling (C-8): the ids are a hard prerequisite of Phase 1, not a recommendation.** v1 defined
keys derived from heading slugs and sibling position, made the `id` attributes optional (Q-O:
"Recommended; ledger works without them"), rated the drift risk R-14 *Low*, and separately
supported the human editing the master while applications are pending (§10.6). Those four
decisions together produce a **silent** failure, which is what makes it critical rather than
untidy: insert one comma-separated value into skill line 1 and every `skills.s1.vN` above the
insertion point designates a different technology; rename a heading and every `proj.*` key beneath
it changes. Stored provenance — in `Claim.provenance`, in `fact_checks`, in
`decisions.artefact_hashes`, in the NFR-3 reconstruction bundle — does not become invalid. It
resolves, to the **wrong line**. C9's lemma-overlap test is a weak filter and will frequently pass
for two adjacent technologies in the same skill line. A job-seeker edits his résumé; R-14's
likelihood is **High**, not Low.

Therefore:

1. **T-0.4 is promoted to a blocking prerequisite of Phase 1.** `resume-ats.html` receives explicit
   `id` attributes matching the key set — a zero-text-change edit verified by an identical text
   diff and an unchanged three-parser ATS result. **Q-O is closed before Phase 1 starts** (§19).
2. **`build_ledger` refuses, rather than falls back.** A master whose `id` set does not match the
   expected key set raises `MasterIdsMissing`; there is no derivation path in production. Key
   derivation survives only as the Phase-0 migration tool that *generates* the ids, run once,
   under review.
3. **Keys are content-anchored where that is cheap**, so that reordering or insertion cannot
   silently repoint a pointer: `skills.s1.pytorch`, not `skills.s1.v3`. Positional keys remain only
   where the content is a sentence rather than a token (`exp.krista.li1..li4`), and those elements
   carry their own ids in the master.
4. **The master is stored, not merely hashed** — see §6.3 (`artefacts.kind='master_html'`, table
   `ledgers`) and §10.6. A cache keyed by `master_hash` is not a record; without the bytes, no
   historical application's provenance can be re-resolved and `GET /applications/{id}/bundle`
   cannot satisfy NFR-3.

**Element key scheme** (document order; slugs from heading text):

| Key | Element |
| --- | --- |
| `hdr.name`, `hdr.role`, `hdr.tag`, `hdr.contact.{location,phone,email,linkedin,github}` | header |
| `summary.p1` | Professional Summary `<p>` |
| `exp.krista.h3`, `exp.krista.meta`, `exp.krista.li1..li4` | Work Experience |
| `proj.mcp.h3`, `proj.mcp.li1..li2` · `proj.aiqa.h3`, `proj.aiqa.li1` · `proj.grc.h3`, `proj.grc.li1` | Key AI Projects |
| `skills.s1..s7` (line) · `skills.sN.label` · `skills.sN.v1..vM` (comma-separated value) | Skills |
| `edu.p1` · `awards.p1` | Education, Awards |

Keys are **declared in the master as `id` attributes** (rule 1 above), so they are stable across
edits by construction rather than by luck. The ledger records
`master_hash = sha256(resume-ats.html)`, every application stores the `master_hash` it was tailored
from (AC-AF-20), and the master bytes for every `master_hash` ever used by an application are kept
forever (§10.6).

**New acceptance criterion (AF group, C-8).** Insert one skill value into the master, rebuild the
ledger, and assert that every previously-stored provenance pointer either resolves to the same text
or **fails loudly** — never resolves to different text.

**Interface.**
```python
class Fact(BaseModel):
    fact_id: str; klass: FactClass; value: str; qualifier: str | None; context: str; element_key: str
class Ledger(BaseModel):
    master_hash: str; facts: list[Fact]; technologies: set[str]; synonyms: dict[str, str]
    canaries: set[str]; organisations: set[str]; projects: set[str]; numbers: list[NumberFact]
    immutable: dict[str, str]        # title, date ranges, degree line, contact fields (byte-exact)
    scope_verbs: dict[str, int]      # verb → scope rank, from config (AC-AF-09)
def build_ledger(html: str) -> Ledger                  # byte-stable across runs (snapshot test); raises MasterIdsMissing if the master's id set != expected keys
def element_text(html: str, key: str) -> str
```
`FactClass = organisation | title | date_range | number | technology | degree_cert | project | achievement | award`.

**Behaviour.** Parses with a deterministic HTML parser; extracts the nine T-1 classes exactly
as test-plan §1.1 lists them (≥ 49 facts); loads `config/synonyms.yaml` and
`config/canaries.yaml` (versioned, reviewed by Avadh). Numbers keep their qualifier token
(`25+`, `up to 80%`, `~`, `2x`) and 3-word context.

### 4.5 `eligibility` — Facts extraction and hard rules

**Purpose.** A-9: eligibility is a hard filter *before* scoring. FR-1.3, FR-1.3a, FR-1.4, FR-1.6,
FR-1.7, FR-4.1, FR-4.1a, FR-4.2, FR-5.1, A-11, A-12, G-C10.

**Interface.**
```python
class JobFacts(BaseModel):           # structured output of the `screen` stage; every field cites JD spans
    seniority: Literal["junior","mid","senior","staff","lead","architect","unstated"]; seniority_evidence: list[Span]
    primary_domain: Literal["genai_llm","traditional_ml","cv_classical","data_analytics","devops","non_ai_software","other"]
    genai_substantial: bool; genai_evidence: list[Span]
    is_fde: bool
    travel_pct: int | None; onsite: Literal["remote","hybrid","onsite","client_site"] | None; client_base: str | None
    candidate_location_rule: Literal["india_ok","must_reside","unstated"]; location_evidence: list[Span]
    country: str | None; city: str | None
    visa_requirement: str | None; sponsorship: Literal["offered","not_offered","unstated"]
    mandatory: list[Mandatory]       # {kind: degree|certification|core_technology|other, text, span}
    preferred: list[str]
    fraud_signals: list[FraudSignal] # {kind, quoted_text}
    posted_at: date | None
    contact_domains: list[str]; apply_domain: str | None

def deterministic_signals(page: PostingPage, posting: RawPosting) -> list[FraudSignal]   # free-mail, lookalike, payment keywords, WhatsApp-only
def evaluate(facts: JobFacts, page, tracker, settings) -> Eligibility   # {eligible, reason: RejectReason|None, flags: list[Flag], evidence: list[Span]}
```
`Span = {start, end, quote}` into the captured JD text (UI J2: reasons quoted, not paraphrased).

**Rule order** (first hit wins; deterministic rules before model-derived ones):

| # | Rule | Reason enum | Source |
| --- | --- | --- | --- |
| 1 | Tracker says applied / manually applied / repost within 180 d | `already_applied`, `duplicate_repost` | FR-4.1, AC-HR-11 |
| 2 | Fetch failed / closed marker / 404 / redirect to careers home | `expired_closed` | A-11, AC-HR-10 |
| 3 | `posted_at` older than 45 days with no "still accepting" evidence | `expired_age` | A-11, AC-HR-09 |
| 4 | Deterministic fraud signal OR model fraud signal | `fraud_suspected:<kind>` (never scored) | FR-5.1, AC-FD-01..07 |
| 5 | Keywords `junior`, `intern`, `graduate`, `trainee`, `0–2 yrs`, or `seniority=junior` from the body | `junior` | FR-1.4, AC-HR-01/02/27 |
| 6 | `seniority=mid` and company not in `strong_companies` (company-quality ≥ 9 checked after scoring) | `seniority_mid_not_strong_company` | A-12, AC-HR-25/26 |
| 7 | `primary_domain ∈ {non_ai_software, data_analytics, devops}`; FDE without `genai_substantial` → `non_ai_software` | `non_ai_software`, `non_ai_data_analytics`, `devops_no_ai` | FR-4.1, FR-1.6, AC-HR-05/06/07 |
| 8 | `cv_classical` | `traditional_ml_no_genai` | AC-HR-03 |
| 9 | `traditional_ml` → **deferred to scoring**: reject unless total ≥ 90, in which case flag `traditional_ml_exceptional` and continue to review | `traditional_ml_no_genai` | FR-4.1a, AC-HR-04 |
| 10 | Country outside {India, UAE, EU/EEA/UK, Canada} or `must_reside` outside India for remote | `outside_geography` | G-C10, AC-HR-21/23 |
| 11 | International and `sponsorship=not_offered` and `work_authorisation` does not cover the country | `no_sponsorship` | FR-1.3a, AC-HR-16/17/28 |
| 12 | Europe/Canada and `sponsorship=unstated` → `no_sponsorship_unstated`; UAE unstated → eligible with flag `sponsorship_unstated_assumed_offered` | | AC-HR-19/20 |
| 13 | Any `mandatory` item Avadh lacks: any certification; degree beyond B.Tech; core technology absent from ledger ∪ synonyms | `mandatory_qualification_missing:<kind>` | FR-4.2, AC-HR-12..15 |
| 14 | International remote with `candidate_location_rule=unstated` → eligible, location score forced 0/5, flag `location_unverified` | | AC-HR-24 |

Every rejected job still gets a `job_evaluations` row with `reasoning` (the fired rule and its
quoted span) — FR-3.4, AC-SC-05, AC-HR-22. Hard-rejected jobs are not scored except for rules 6/9
which need the rubric; the UI shows `—` for unscored (UI §3.10).

### 4.6 `scoring` — Rubric scoring and tiering

**Purpose.** FR-3.1..3.4, §4.3 thresholds, TR-10, A-12.

**Interface.**
```python
class SubScore(BaseModel): points: int; reasoning: str; jd_spans: list[Span]
class Score(BaseModel):
    technical_skill: SubScore        # ≤30
    ai_llm_experience: SubScore      # ≤25
    seniority: SubScore              # ≤15
    domain_relevance: SubScore       # ≤10
    company_quality: SubScore        # ≤10
    location_fit: SubScore           # ≤5
    keyword_alignment: SubScore      # ≤5
    gaps: list[Gap]                  # {text, klass: core|preferred, span}
    key_matching_skills: list[str]   # must ⊆ ledger technologies ∪ synonyms (AC-SC-13)
    differentiator_hits: list[str]   # from the ranked §2 list, for tie-break (AC-SC-04)
    total: int                       # validator: equals the sum; each part within cap
async def score(job, facts, ledger, settings) -> Score          # `analyse` stage, with_structured_output(Score, include_raw=True)
def tier(total: int) -> Literal["T1","T2","T3","below"]
def rank(scored: list[ScoredJob], settings) -> list[ScoredJob]  # total desc → differentiator order → geography priority (AC-DS-15)
```

**Behaviour.**
- Structured output via `model.with_structured_output(Score, include_raw=True)` (verified,
  `models.md`); Pydantic validators cap each dimension and reject totals ≠ sum (AC-SC-01).
  `include_raw=True` returns the `AIMessage` whose `usage_metadata` feeds the spend ledger.
- The prompt embeds the **ledger facts** (never the answer sheet) and the JD text; it instructs
  sub-score reasoning to cite JD phrases; AC-SC-13 is checked by asserting every technology
  named in reasoning ∈ ledger ∪ synonyms ∪ JD vocabulary.
- One retry on schema failure, then `evaluation_failed`; run continues (AC-SC-12, AC-FM-03).
- Tier 3 with any `core` gap → `rejected: tier3_gap`; only `preferred` gaps → queued with flag
  `borderline` (AC-SC-09, AC-HL-20). Tiers affect **ordering only**, never gating
  (analysis §5.9).
- The `screen` stage produces `JobFacts` (extraction); the `analyse` stage produces `Score`.
  The UI's "first-pass vs deep" shows the screen-stage tier hint against the final score.

### 4.7 `selection` — Ceiling, carry-over and deferral

**Purpose.** FR-9.2, O-5, AC-SB-17..20, AC-HL-21/22, AC-TK-10.

**Behaviour.**
```
slots    = daily_ceiling − count(PENDING_REVIEW applications created before today, still active)
queue    = rank(eligible ∧ total ≥ 70 ∧ ¬tier3_gap ∧ source.policy ≠ discovery_only)
selected = queue[:max(slots, 0)]          # may be fewer than slots — never padded
deferred = queue[slots:]                  # verdict deferred_over_ceiling; re-evaluated tomorrow if still active
```
Carry-over applications are re-verified active when the queue is opened and at 09:00 (UI §5.5);
closed → `EXPIRED`. `daily_ceiling = 0` → discovery and scoring proceed, nothing selected,
report notes `ceiling_zero`. A job on a discovery-only source with total ≥ 70 is **not** selected
for a submitting application; it becomes a fallback row (§4.15) and — **DEPARTURE D-3** — if
total ≥ `tailor_fallback_min_score` (80) a *documents-only* application thread is spawned
(`mode='documents_only'`) that stops after FactGuard, so the By-hand screen has downloads (UI P-5).
Documents-only threads count against the daily ceiling like any other (they consume review time).

### 4.8 `tailor` — Tailoring plan generator and applier

Full contract in §10. Interface summary:
```python
class TailoringPlan(BaseModel):      # LLM output (generate stage); no HTML in it
    skill_line_order: list[str]                 # permutation of skills.s1..s7
    skill_value_order: dict[str, list[str]]     # per line: permutation of its value keys
    bullet_order: dict[str, list[str]]          # per <ul> (exp.krista, proj.mcp): permutation of li keys
    emphasise: list[Emphasis]                   # ≤ 3: {element_key, phrase} → wrap existing text in <b>
    summary: SummaryRewrite | None              # {sentences: [{text, provenance: [element_key]}]}
    rationale: str
def apply_plan(master_html: str, plan: TailoringPlan) -> str      # deterministic DOM edits only
def structural_diff(master_html, tailored_html) -> list[Change]  # classes: reorder | rewrite_summary | emphasis | violation
```

### 4.9 `render` — PDF render and ATS verification

**Purpose.** FR-6.4, AC-RT-03..07, AC-RT-10, AC-FM-12, G-I10.

**Interface.**
```python
async def render_pdf(tailored_html_path: Path, out_pdf: Path) -> RenderResult   # subprocess: python resume/render.py <in> <out>
def ats_check(pdf: Path, tailored_html: str, master_html: str) -> AtsReport
```
`AtsReport = {pages, probes_passed: int, headings_detected: dict[parser,int], nw_intact: bool, images: int, high_codepoints: int, right_column_blocks: int, fonts: list[str], letter_spacing_ok: bool, passed: bool}`.

**Behaviour.** Pass requires: exactly 1 page; 15/15 reading-order probes across pdfminer,
pypdf, PyMuPDF; 6/6 headings by all three; every master `.nw` span present on one line;
0 images; 0 chars ≥ U+2100; 0 right-column blocks; named fonts only; `<style>` identical to
master except `letter-spacing`, each < 8% of the element's `font-size` (AC-RT-05/07/10).
Failure → application `TAILORING_FAILED`, guard event, Telegram, not queued (AC-RT-06).
`render.py` failure (Chromium missing) → same, other applications unaffected (AC-FM-12).
Artefacts written as `art/<sha256[:16]>.pdf` (AC-RT-13, AC-FM-19).

### 4.10 `letters` — Cover letter and subjective answers

**Purpose.** FR-7.1, FR-7.2, FR-8.2, A-13, G-I15, AC-CL-01..04, AC-AF-18/21.

**Interface.**
```python
class Claim(BaseModel):
    text: str
    kind: Literal["self", "company", "context"]
    provenance: list[str]             # self → element keys; company → "jd:<start>-<end>" or "page:<start>-<end>"; context → []
class Letter(BaseModel):
    sections: dict[Literal["why_role","relevant_experience","evidence","why_ai_background","close"], list[Claim]]
    word_count: int                   # ≤ 300 validated
class SubjectiveAnswer(BaseModel): question_id: str; claims: list[Claim]; word_count: int   # ≤ 150
```
**`kind="context"` is a narrow, enforced category (C-6).** v1 defined three claim kinds and
verified two: C9 was scoped to `self`, C11 to `company`, and C10 judged a claim against source text
that a `context` claim by definition does not have. Since the **generating model chooses the label**,
a model that cannot find a provenance key for a sentence it wants to write had a schema-legal escape
hatch — emit it as `context` — and the schema *rewarded* the choice, because a `self` claim without a
pointer fails C9 while a `context` claim without a pointer is valid. The deterministic residue does
not close it: a sentence such as *"I have shipped agentic systems that enterprise buyers trust"*
carries no numeral (C3), no canary or out-of-vocabulary technology (C4), no organisation (C5) and no
qualification token (C13), yet reaches the employer as a first-person claim about the candidate,
verified by nothing. That is a T-5 violation the schema permitted.

v2 defines the kind and enforces the definition deterministically:

> **`context` is permitted only for sentences that make no assertion about the candidate** — the
> salutation, a transition, the closing line. No first-person subject, explicit or implied.

- **Check C14** (§8.2) reclassifies any `context` claim containing a first-person pronoun, or a
  resume-vocabulary verb phrase with an implied first-person subject, as `self` — after which it
  must satisfy C9 and C10 or fail. Reclassification is a verifier act, not a request to the model.
- **Caps**: ≤ 2 `context` claims per letter, **0** per subjective answer. The count is surfaced in
  the review UI next to the `[n]` markers (§8.5), so an artefact that has quietly become 40% grey
  markers is visible to the reviewer rather than merely legal.
- The mutation suite (§8.4) is re-cut so that a `self` claim relabelled `context` is one of its 40
  seeded fabrications. v1's suite could not catch this class because it was organised by *fact
  class*, and this is a failure of *claim kind*.

**Behaviour.** Generated only when the form has a cover-letter field or `always_generate`
(AC-CL-05). The prompt embeds ledger facts, the JD text with span offsets, and the banned-filler
list; the model must return sentence-level claims with provenance — free prose is not accepted.
The rendered letter is assembled deterministically from claims, so the `[n]` markers in the UI
*are* the provenance list rather than a post-hoc annotation. Every artefact goes through
FactGuard (§8).

### 4.11 `forms` — Form probe, question router and deterministic filler

Full design in §11. Interface summary:
```python
async def probe_form(url) -> FormModel        # fields: {field_id, label_norm, type, required, options, page_index}, has_resume_upload, has_cover_letter, supported_ratio
def route(field: FormField, sheet_keys: set[str]) -> Route   # profile | answer_sheet:<key> | years_total | years_tech:<tech> | eeo_decline | subjective | credential_refuse | otp_refuse | unknown
def fill_value(route, field, sheet, ledger) -> FilledValue | Halt
```

### 4.12 `browser` — Browser worker (Playwright)

**Purpose.** TR-6, C-2, HITL-2, NFR-5, AC-HL-12/13, AC-SB-16, AC-FM-13.

**Interface.**
```python
class BrowserWorker:
    async def open(self, url) -> Page
    async def fill(self, page, plan: FillPlan) -> FillResult        # stops at first blocker: captcha | login | otp | unmapped_required
    async def upload(self, page, field, path)
    async def detect_blocker(self, page) -> Blocker | None
    async def commit_page(self, page, page_index: int) -> PageResult # advances a multi-page form: an irreversible POST; see §9.8
    async def page_fingerprint(self, page) -> Fingerprint           # {page_token, dom_hash} — recorded at fill time, re-asserted before the click (C-2)
    async def click_submit(self, page, selector) -> None            # the point of no return; see §9
    async def capture_evidence(self, page, timeout_s: int = 180) -> Evidence
    async def screenshot(self, page) -> Path
```
**Behaviour.** One persistent context under `data_dir/browser-profile/` (cookies survive,
AC-SB-16). **The profile directory is opened with an exclusive lock, and a lock failure is fatal to
the worker, not a restart trigger (C-10)**: a locked profile means another process owns this
browser, and restarting into it would give two instances a second Playwright context over the same
cookies. The worker logs, raises, and the application lands in `NEEDS_ATTENTION`; only a crash with
the profile *free* restarts the worker (AC-FM-13). Headed (visible) so Avadh can take over; the
worker never closes a page that is blocked — it leaves it open, screenshots it, and the application
thread interrupts at HITL-2.

**Page identity (C-2).** `page_fingerprint` returns an opaque `page_token` plus a DOM hash over the
form's field set, recorded when `fill_form` finishes and re-asserted by `submit` step (2). A human
who took over the browser, solved a CAPTCHA and pressed Submit himself leaves behind a *different*
document — a confirmation page, a redirect, a fresh blank form — and the fingerprint mismatch makes
that detectable instead of invisible. v1 asserted only that *a* submit selector existed, which a
fresh blank form satisfies.
Blocker detection is heuristic (iframes from known CAPTCHA vendors, `input[type=password]` on a
login form, OTP labels, "verify your email"). The worker never calls any solver service
(AC-HL-12, checked by the proxy). Browser crash → application `NEEDS_ATTENTION`, browser
restarted for the next application (AC-FM-13).

### 4.13 `llm` — GuardedModel, spend ledger, budget gate, tracing

**Purpose.** TR-7, TR-11, TR-12, NFR-6, NFR-7, A-6, A-15, A-24, AC-NF-04/05/07/09.

**Interface.**
```python
class GuardedModel:                      # wraps the BaseChatModel returned by init_chat_model
    def __init__(self, inner, stage: Stage, guard: PromptGuard, budget: BudgetGate, tracer: Tracer): ...
    async def ainvoke(self, messages, *, thread_id, node, **kw) -> AIMessage
    def with_structured_output(self, schema, include_raw=True) -> "GuardedModel"
class PromptGuard:
    def assert_clean(self, messages) -> None   # raises SensitiveLeakError if any answer-sheet value / secret pattern appears
class BudgetGate:
    def check(self, stage) -> None             # raises BudgetHardStop / PauseRequested; emits soft alert once per day
class SpendLedger:                             # table spend_ledger; per call: run_id, thread_id, node, stage, model, in/out tokens, usd, latency
```
**Behaviour.**
- Every model call in the codebase goes through `GuardedModel` (lint AC-NF-11 extended: no
  direct `init_chat_model(...).invoke` outside `llm/`).
- **There is no unwrapped path, and `.inner` is banned (C-5).** v1 exposed `GuardedModel.inner`
  and §5.4 passed it to `create_agent`, which switched off `PromptGuard`, `BudgetGate` and
  `SpendLedger` for the one agent that runs against a live, partially-filled form — the single
  place where a DOM snapshot can carry an answer-sheet value in an element's `value` attribute, the
  single place permitted 60 tool calls, and therefore the single place that could run past the $20
  hard stop while every other call in the system was gated. The v1 lint did not catch it because
  the call site used the approved accessor `get_model(...)` and then reached *through* it.
  Accordingly: `GuardedModel` implements the `BaseChatModel` surface `create_agent` requires and is
  passed as the model itself (§5.4); the `.inner` attribute is **removed from the class**, and
  `.inner` joins `init_chat_model` on the static-check ban list (T-0.3), with an AC asserting that
  no call site anywhere reaches an unwrapped model. Where wrapping cannot be complete, the
  equivalent guarantee is supplied by middleware inside the agent loop, never by omission.
- `PromptGuard.assert_clean` renders the messages to text and scans for every current
  answer-sheet value and its formatting variants (`19.8`, `₹19.8`, `19,80,000`, `32 LPA`,
  `1 month`, `30 days`, per-currency figures, `years_by_technology` values in a "years" context),
  the API-key regexes and the Telegram token. The phone number is on the resume and is a
  *contact* constant, not answer-sheet data. Raising here fails the node — fail closed (AC-NF-04).
- `BudgetGate.check` reads today's IST total from `spend_ledger` (AC-FM-17 day boundary):
  ≥ soft → one alert (M7) per day; ≥ hard_stop → raise `BudgetHardStop`; global pause flag set →
  raise `PauseRequested` (A-24, AC-HL-25). Approvals, pre-flight and submission make no LLM call
  and are unaffected (AC-FM-09).
- Cost = tokens × `prices.yaml`; `usage_metadata` is read from the returned `AIMessage`
  (`messages.md`, token usage). The header meter is updated via SSE within 5 s (AC-UI-08).
- `Tracer` writes `llm_calls`, `tool_calls`, `transitions` locally (AC-NF-07). LangSmith is
  enabled only if `hosted_tracing=true` sets `LANGSMITH_TRACING` / `LANGSMITH_API_KEY`
  (verified env var names in `observability.md`); default off (AC-NF-08).

### 4.14 `notify` — Telegram

**Purpose.** Q-7, G-C6, A-14, AC-HL-09..11, AC-FM-11, UI §7.

**Behaviour.** All messages go through `notifications_outbox` (idempotency key per event, e.g.
`review_ready:<run_id>`, `blocked:<application_id>:<interrupt_id>`); the notifier delivers with
back-off and marks `delivered_at`; never duplicates (AC-FM-11). Message templates M1–M9 exactly
as UI §7.1; **no answer-sheet value or secret is ever interpolated** (template variables are an
allowlist). Inbound: only `settings.telegram.chat_id` is honoured; others logged
`unauthorised_telegram` (AC-HL-09). Commands: `/reject <app_short_id> <reason_code>` (recorded
channel `telegram`), `/pause`, `/resume`, `/status`. **There is no `/approve` command and no
`approve_enabled` setting (M-13)**: `/approve` replies with the dashboard link and records nothing.
Approving is a dashboard act, because it is the one decision that needs the diff, the letter
provenance and the values on screen — none of which fits in a chat message.

**DEPARTURE D-4** from UI §7 principle 4 ("notify-only"): the test plan requires
Telegram reject to work; A-14 is adopted over the UI note. **This also departs from AC-HL-10/11**,
which describe an approve-over-Telegram path; see §17.

### 4.15 `audit` — Search audit log, fallback surface, guard events

**Purpose.** FR-1.8, FR-1.9, FR-13.1 (G-M1), NFR-3.

**Behaviour.** Tables `runs`, `source_runs`, `queries`, `jobs`, `job_sources`,
`job_evaluations` form the audit log. A job is a **fallback row** when
`verdict = by_hand` with `fallback_reason ∈ {discovery_only:<source>, captcha, login,
unsupported_form, missing_data}` and `fallback_state ∈ {pending, applied_manually, skipped}`.
Setting `applied_manually` inserts a tracker `applications` row with `channel='manual'`,
`status='MANUAL'` (AC-DS-06, feeds dedup rule 1). Links are verified at logging time (HEAD/GET
200 + title present) else `link_unverified` (AC-DS-07). `audit_events` records every guard
firing (rule, job, offending text, outcome) for the guard-events panel (AC-AF-23, AC-UI-11) and
every HITL decision (AC-HL-27).

### 4.16 `tracker` — Application state machine (system of record)

Full state machine in §9.2. Interface:
```python
class Tracker:
    async def create_application(job_id, run_id, mode) -> Application            # UNIQUE(job_id) enforced
    async def transition(app_id, from_states: set[State], to: State, **fields) -> Application
        # one UPDATE ... WHERE id=? AND status IN (...); raises IllegalTransition if 0 rows
    async def get(app_id) -> Application
```
Every transition is one SQL statement with a `WHERE status IN (from_states)` guard and a row in
`transitions`; that makes the state machine race-safe without application-level locks and gives
AC-TK-11 its reconstruction trail.

### 4.17 `frontend` — Dashboard SPA

See §14.

---
## 5. LangGraph graph design

Two compiled `StateGraph`s share one `AsyncSqliteSaver`. They are **not** parent/child: an
application thread outlives the run that created it by days, and subgraph checkpoints live in
the parent's namespace (`use-subgraphs.md`), which would couple lifetimes and make per-thread
pruning impossible. The discovery graph *creates tracker rows*; the run supervisor launches
application threads from those rows.

### 5.1 Shared conventions

| Convention | Rule | Why / verified where |
| --- | --- | --- |
| Thread ids | `run_id` and `application_id` are `uuid4()` strings, used verbatim as `thread_id` | gotcha 11, AC-NF-13 |
| Checkpointer | `from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver`; `await checkpointer.setup()` once at boot; production refuses `InMemorySaver`/`MemorySaver` | `checkpointers.md` §278/294, AC-ID-24, AC-NF-14 |
| Durability | Every `ainvoke` passes `durability="sync"` | `checkpointers.md` Durability modes; AC-ID §2.1 |
| Runtime context | `StateGraph(State, context_schema=AppContext)`; nodes take `(state, runtime: Runtime[AppContext])`; `runtime.context` carries service handles (tracker, browser worker, model registry, settings snapshot); `runtime.execution_info.thread_id` is the thread id | `graph-api.md` Runtime context |
| State size | State holds **ids and hashes**, never JD bodies, HTML, PDFs or answer-sheet values. Content lives in `jobagent.db` / `art/`. Checkpoints stay small (gotcha 13) and can never leak §2.1 values | A-6, A-17 |
| Interrupt nodes | Prefix `await_`; body = read state → **one** `interrupt(payload)` → return the resume value into state (optionally as `Command(goto=...)`); no I/O before the interrupt; not in a loop; not in `try` | `interrupts.md` Rules; AC-ID-13/14 |
| Notifications | Sent by the node *preceding* an `await_` node, through the outbox with an idempotency key | AC-ID-12 |
| Retry defaults | `builder.set_node_defaults(retry_policy=RetryPolicy(max_attempts=3))`. **No graph-wide `error_handler`**; handlers are attached per node. *Note (M-4, open — §21): v1's stated rationale for this ban — that a handler on an `await_` node could swallow the interrupt — is **false** for the same reason as M-1: interrupts bypass error handlers. The ban is retained in v2 only because §5.3's "any node raising `BudgetHardStop`/`PauseRequested`" routing genuinely needs a graph-wide default, which is a contradiction v2 does not resolve and M-4 must.* | `fault-tolerance.md` §401; §389–391 |
| Interrupt node retries | **Verified, and the v1 mitigation is withdrawn (M-1).** `interrupt()` uses the `GraphBubbleUp` mechanism and *bypasses both retry policies and error handlers*, so a retry policy could never have re-executed an interrupt. The `await_*` nodes therefore keep the graph default `max_attempts=3`, decided on its merits: they perform no I/O before the interrupt, so a retry is harmless, and v1's `max_attempts=1` removed retries from seven nodes for *genuine* transient failures on the safety-critical HITL path. | `langgraph/fault-tolerance.md` §389–391, "Behavior with `interrupt()`" |
| Timeouts | `timeout=TimeoutPolicy(run_timeout=...)` on browser and model nodes; all nodes are `async def` (timeouts are async-only) | `fault-tolerance.md` Limitations |
| Pause / drain | Graph invocations receive a `RunControl`; `/pause` calls `control.request_drain("user_pause")`; `GraphDrained` is caught by the supervisor and the thread is resumed later with `ainvoke(None, config)` | `fault-tolerance.md` Graceful shutdown; A-24, AC-HL-25 |
| Crash recovery | Startup reconciliation: for each non-terminal application, `snapshot = await graph.aget_state(config)`; if `snapshot.next` is non-empty and no task carries `interrupts` → `ainvoke(None, config)`; if an interrupt is pending → leave it (the dashboard reads it) | `checkpointers.md` StateSnapshot fields; `use-time-travel.md` `invoke(None, ...)` |
| Reading a pending interrupt | `snapshot.tasks[i].interrupts[j].value` and `.id` | `checkpointers.md` §157, `interrupts.md` §188 |
| Resuming | `ainvoke(Command(resume=<dict>), config)`; a single interrupt per thread at any time, so a plain value (not an id-map) is sufficient | `interrupts.md` |

### 5.2 DiscoveryGraph

**Thread:** one per run. **Purpose:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-9.2, FR-11.

```python
class DiscoveryState(TypedDict):
    run_id: str
    trigger: Literal["scheduled", "manual", "catch_up"]
    source_results: Annotated[list[SourceResult], operator.add]   # {source, status, count, error?}
    job_ids: list[str]                 # after dedup
    eligible_ids: list[str]
    selected_ids: list[str]
    deferred_ids: list[str]
    fallback_ids: list[str]
    errors: Annotated[list[str], operator.add]
```

```
                    ┌────────────┐
   START ──────────▶│ start_run  │ writes runs row, run lock heartbeat, snapshot settings + master_hash
                    └─────┬──────┘
                          │ conditional edge: [Send("discover_source", {source}) for enabled sources]
          ┌───────────────┼──────────────────────────────┐
          ▼               ▼                              ▼
   ┌───────────┐   ┌───────────┐                  ┌───────────┐
   │discover_  │   │discover_  │      …×8         │discover_  │   per source: queries → postings → raw rows
   │source(gh) │   │source(li) │                  │source(wd) │   (isolated; failure → source_results status=failed)
   └─────┬─────┘   └─────┬─────┘                  └─────┬─────┘
         └───────────────┴──────────────┬───────────────┘
                                        ▼
                                 ┌─────────────┐
                                 │ dedup       │ identity resolution, merge, position families → job_ids
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ fetch_and_  │ for job in job_ids (bounded 4-way): fetch_posting → JobFacts (screen model)
                                 │ extract     │ idempotent: skips jobs with facts already stored for this run
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ apply_rules │ eligibility §4.5 → eligible_ids; reasons recorded for the rest
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ score       │ for job in eligible_ids (bounded 4-way): Score (analyse model); traditional_ml gate
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ select      │ rank → ceiling/carry-over → selected / deferred / fallback (§4.7)
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ spawn_apps  │ INSERT applications (UNIQUE job_id → upsert-safe), enqueue thread launches
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │ report      │ FR-11.1 morning report row; outbox M4
                                 └──────┬──────┘
                                        ▼
                                       END
```

**Design decision — `Send` fan-out only per source, not per job.** `Send` (verified,
`graph-api.md` §748) runs all dispatched nodes in one super-step; 140 parallel model calls would
hit provider rate limits and produce a 140-way checkpoint write. Per-job work is done *inside*
`fetch_and_extract` and `score` with an `asyncio.Semaphore(4)` and per-job idempotent DB writes,
so a crash mid-node re-runs the node and skips completed jobs. Sources are 8 at most, so `Send`
per source is bounded and gives NFR-4 isolation for free.

**Node policies.** `discover_source`: `timeout=TimeoutPolicy(run_timeout=900)`,
`error_handler=record_source_failure` (writes `source_results` failed, `goto="dedup"` is *not*
needed — the fan-in waits for all branches; the handler just returns the update).
`fetch_and_extract` / `score`: `timeout=TimeoutPolicy(run_timeout=1800)`; provider 429/5xx are
retried per call inside the node (`ModelRetryMiddleware` is for `create_agent`; here a small
tenacity-style retry around `GuardedModel.ainvoke` **[UNVERIFIED — plain Python; not a LangChain
API]**) and exhaustion marks that job `evaluation_failed` (AC-FM-03/04). `BudgetHardStop` inside
these nodes → the node stops processing further jobs, marks the remainder `paused_budget`, and
returns normally (discovery does not need an interrupt for budget; tomorrow's run re-evaluates).

**Invocation.** `await discovery.ainvoke({"run_id": ..., "trigger": ...}, config={"configurable": {"thread_id": run_id}}, durability="sync", context=ctx, control=run_control)`.
A kill during discovery (AC-DS-14) leaves a checkpoint; the *next* run is a new `run_id` — the
aborted run's audit rows are marked `run_aborted` by startup reconciliation, and the new run's
dedup pass finds the already-inserted jobs (no duplicates).

### 5.3 ApplicationGraph

**Thread:** one per application (`application_id`). **Modes:** `auto` (Greenhouse, Lever,
career page), `assisted` (Workday), `documents_only` (fallback ≥ 80, D-3).

```python
class ApplicationState(TypedDict):
    application_id: str
    job_id: str
    run_id: str
    mode: Literal["auto", "assisted", "documents_only"]
    master_hash: str
    form_ref: str | None                 # artefact id of FormModel JSON
    fill_session: str | None             # browser worker page token (opaque)
    fill_fingerprint: str | None         # dom_hash recorded when fill_form completed; re-asserted by submit (C-2)
    pages_committed: list[int]           # page_index values whose advancing POST is durably recorded (C-1, §9.8)
    answers: list[AnswerRef]             # {field_id, route, source, artefact_ref | None}  — never a value from the answer sheet
    halts: list[Halt]                    # open HITL-3 items: {field_id, label, field_type, question_text}
    blocker: Blocker | None              # {kind: captcha|login|otp|credential_field, step, screenshot_ref}
    tailored_ref: str | None; pdf_ref: str | None; letter_ref: str | None; answers_ref: str | None
    ats_report_ref: str | None
    factguard_ref: str | None; factguard_pass: bool
    repair_count: int
    hitl4: Hitl4Item | None
    decision: Decision | None            # {type, decision_id, artefact_hashes, channel, at}
    preflight_ref: str | None
    submit_result: Literal["submitted", "unknown", "preclick_failed"] | None
    resume_target: str | None            # node name to jump back to after await_pause
    paused_reason: str | None
```

```
 START ─▶ load ─▶ (mode==documents_only) ─────────────────────────────┐
           │                                                          │
           ▼                                                          │
        probe_form ──(blocker)──▶ notify_blocked ─▶ [await_blocker] ──┼──▶ probe_form (retry after hand-off)
           │                                            │ send_to_by_hand / abandon ──▶ finalize
           ▼ (unsupported: <90% required mappable)                    │
        mark_unsupported ─▶ finalize                                  │
           │                                                          │
           ▼                                                          │
        route_questions ──(halts)──▶ notify_question ─▶ [await_question] ─▶ route_questions
           │                                                          │ skip_job ──▶ finalize
           ▼                                                          ▼
        tailor  (skipped if !has_resume_upload; master PDF used) ◀────┘
           │
           ▼
        render_check ──(fail)──▶ finalize(TAILORING_FAILED)
           │
           ▼
        generate_letter (if form has letter field) ─▶ generate_answers (subjective only)
           │
           ▼
        factguard ──(fail, repair_count<2)──▶ repair ──▶ tailor|generate_letter|generate_answers (targeted)
           │  └──(fail, repair_count≥2)──▶ notify_hitl4 ─▶ [await_hitl4] ─▶ apply_hitl4_fix ─▶ factguard
           │                                                    │ skip_job ─▶ finalize
           ▼ (pass)
        (mode==documents_only) ─▶ finalize(DOCS_READY)
           │
           ▼
        notify_review_ready ─▶ [await_review]  ◀── HITL-1 + HITL-5 (one decision)
                                     │
                                     ▼
                              record_decision ──(reject)──▶ finalize(REJECTED_BY_USER)
                                     │           ──(regenerate)──▶ tailor
                                     │           ──(postpone)──▶ notify_review_ready (re-queue; no new notification, same idempotency key)
                                     ▼ (approve)
                                 preflight ──(fail)──▶ finalize(PREFLIGHT_FAILED | EXPIRED)
                                     │
                                     ▼
                                 fill_form ──(blocker)──▶ notify_blocked ─▶ [await_blocker] ──┬─(i_submitted)─▶ finalize(SUBMITTED, human)
                                     │                                                        ├─(continue)───▶ recheck_after_blocker ─▶ fill_form
                                     │                                                        └─(by_hand|abandon)─▶ finalize
                                     │  (mode==assisted) ─▶ notify_handoff ─▶ [await_handoff] ─▶ finalize(SUBMITTED_BY_HUMAN | BY_HAND)
                                     ▼
                                 submit  ────────────────(submitted)──────────────▶ finalize(SUBMITTED)
                                     │  (page lost) ─▶ fill_form
                                     ▼ (unknown)
                              notify_unknown ─▶ [await_unknown] ──(confirmed_submitted)──▶ finalize(SUBMITTED)
                                                       └──(confirmed_not_submitted)──▶ preflight ─▶ fill_form ─▶ submit

 Any node raising BudgetHardStop / PauseRequested ──error_handler──▶ [await_pause] ─▶ Command(goto=resume_target)
```

**Node table.** All nodes are `async def node(state, runtime: Runtime[AppContext])`.

| Node | Does | LLM | Side effects | Policy |
| --- | --- | --- | --- | --- |
| `load` | Reads job, application, settings snapshot; verifies `master_hash` equals on-disk master (else `MASTER_CHANGED` flag) | – | none | default |
| `probe_form` | Browser: open apply URL, enumerate fields → `FormModel` artefact; detect blocker; compute `supported_ratio` | – | artefact write (content-addressed, idempotent) | `timeout=TimeoutPolicy(run_timeout=180)` |
| `mark_unsupported` | Fallback row `unsupported_form`; status `BY_HAND` | – | upsert | default |
| `route_questions` | Deterministic routing §11; fills `answers[]` with routes and sources; collects `halts` | classify unknown labels only (`screen`), label text only | none | default |
| `notify_question` | Outbox M3 (`question:<app>:<field>`) | – | outbox (idempotent key) | default |
| `await_question` | `interrupt({"kind":"hitl3", ...halts})` → stores answers/`skip_job` | – | **none before interrupt** | default (M-1) |
| `tailor` | Build `TailoringPlan` (`generate`), `apply_plan`, write tailored HTML artefact | generate | artefact write | `timeout=300` |
| `render_check` | `render.py` subprocess; `ats_check`; artefacts | – | artefact write | `timeout=180` |
| `generate_letter` | `Letter` claims (`generate`) | generate | artefact | `timeout=300` |
| `generate_answers` | `SubjectiveAnswer` per subjective field (`generate`) | generate | artefact | `timeout=300` |
| `factguard` | §8 verifier; judge model for entailment | judge | `fact_checks` row, guard events | `timeout=300` |
| `repair` | Feed violations back; `repair_count += 1`; `Command(goto=<offending stage>)` | – | none | default |
| `notify_hitl4` / `await_hitl4` / `apply_hitl4_fix` | HITL-4 payload: sentence, fact class, nearest ledger facts; fix = use resume wording / edit / skip | – | outbox; none; artefact | – |
| `notify_review_ready` | Status `PENDING_REVIEW`; outbox is **batched** at supervisor level (M1 once per run) | – | upsert | default |
| `await_review` | `interrupt({"kind":"review", "application_id", "artefact_hashes"})` → `{type, decision_id, ...}` | – | **none before interrupt** | default (M-1) |
| `record_decision` | Validates decision vs current artefact hashes; writes `decisions` row; status → `APPROVED` / `REJECTED_BY_USER` / re-queue | – | insert (idempotent by `decision_id`) | default |
| `preflight` | Twelve FR-9.1 checks §9.4; live re-fetch; status `PREFLIGHT_OK` | – | `preflight_results` rows | `timeout=120`, `retry_on=is_network_error` |
| `fill_form` | Browser: navigate, upload PDF, fill routed values (answer-sheet values loaded **here**, inside `FormFiller`, from the table); **advances multi-page forms under the §9.8 per-page commit protocol**; refuses to start when `submission_enabled` is false; stop on blocker | – | **page-advancing POSTs — irreversible; `page_commits` row written before each** | `retry_policy=RetryPolicy(max_attempts=1)`, `timeout=600`, `error_handler=fill_error_handler` |
| `submit` | §9.3 protocol: check `submission_enabled` → read tracker state → re-assert the page fingerprint → write `SUBMITTING` → click → evidence → `SUBMITTED` | – | **the irreversible click** | `RetryPolicy(max_attempts=3, retry_on=is_pre_click_error)`, `timeout=TimeoutPolicy(run_timeout=300)` (evidence capture is now 180 s — C-3), `error_handler=submit_error_handler` |
| `notify_unknown` / `await_unknown` | Outbox (unknown outcome); `interrupt({"kind":"unknown_outcome", ...})` → `confirmed_submitted` / `confirmed_not_submitted` / `check_again_later`. The dangerous branch is gated by §9.5's friction (typed confirmation, waiting period, checkbox) | – | outbox; none | default (M-1) |
| `notify_handoff` / `await_handoff` | Assisted mode: M2-style message; `interrupt({"kind":"handoff"})` → `i_submitted` / `by_hand` / `abandon` | – | outbox; none | default (M-1) |
| `notify_blocked` / `await_blocker` | HITL-2: screenshot ref, step; `interrupt({"kind":"blocked", ...})` → **`i_submitted`** / `continue` / `by_hand` / `abandon`. `i_submitted` is the **first** option on the card and is wired to exactly the `await_handoff` handling: `SUBMITTED`, `confirmation_kind=human`, evidence = statement + screenshot (C-2) | – | outbox; none | default |
| `recheck_after_blocker` | Re-runs pre-flight #3 (`still_active`) and #5 (`not_duplicate`) after any `await_blocker` resume, **before** re-entering `fill_form`; a fail routes to `finalize(PREFLIGHT_FAILED\|EXPIRED)`. Both checks last ran before the human touched the browser (C-2) | – | `preflight_results` rows | `timeout=120` |
| `await_pause` | `interrupt({"kind":"paused", "reason"})` → `Command(goto=state["resume_target"])` | – | none | default (M-1) |
| `finalize` | Terminal status write; evening-digest counters | – | update | default |

**Interrupt payloads** are plain JSON dicts of ids, hashes and short strings (rule 3 of
interrupts: no complex values). The dashboard never needs the payload to render — it reads the
tracker and artefacts by `application_id` (AC-HL-24: no new LLM call to review).

**Why one interrupt for HITL-1 and HITL-5.** The requirements list them as separate gates; the
UI (J1) collapses them into one `A` keypress. This spec follows the UI: the decision that
approves the documents *is* the decision to submit, because nothing else about the submission is
reviewable — the form values are shown on the Answers tab, and the FR-9.1 pre-flight re-verifies
everything after the grace window and immediately before the click. A second modal gate would
add 3 s × 15 and train click-through (UI §3.4 notes). The graph still satisfies AC-ID-25: the
click lives in `submit`, reachable only via `record_decision → preflight → fill_form`.

**Why edits do not resume the graph.** `edit` (HITL-R2) is handled by the API (§7.4): it writes
a new artefact version, runs FactGuard synchronously, and updates the application row; the
thread stays paused at `await_review`. Resuming on every edit would re-run the node and re-issue
a decision id. When Avadh finally approves, the resume payload carries the artefact hashes he saw;
`record_decision` refuses a payload whose hashes are stale (`409`), and `preflight` #6–#9
compare the on-disk artefacts against the approved hashes (AC-SB-07/08).

**Regenerate** (reject reason 5, UI §3.8) resumes with `{"type": "regenerate", "note": ...}` →
`record_decision` routes to `tailor` with the note in state; queue position and score untouched.

### 5.4 Form-filling agent (inside `fill_form`) — where `create_agent` is used

Field mapping on unfamiliar career-page forms is the one genuinely agentic task. Inside
`fill_form`, for **career-page** forms only (Greenhouse and Lever have stable, hand-mapped
schemas), a `create_agent` instance runs with tools:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, ToolCallLimitMiddleware
from langchain.tools import tool, ToolRuntime

@tool
def inspect_form(runtime: ToolRuntime[FillContext]) -> str: ...        # returns FormModel (labels, types, required) — no values
@tool
def propose_mapping(field_id: str, route: str, runtime: ToolRuntime[FillContext]) -> str: ...  # validated against §11 router; deterministic filler writes the value
@tool
def request_human(field_id: str, question: str) -> str: ...           # records a HITL-3 halt; never guesses

mapper = create_agent(
    model=get_model("analyse"),                # the GuardedModel ITSELF — never `.inner` (C-5)
    tools=[inspect_form, propose_mapping, request_human],
    system_prompt=FILL_MAPPER_PROMPT,
    middleware=[
        GuardMiddleware(),                     # before_model: PromptGuard.assert_clean + BudgetGate.check
                                               # after_model:  SpendLedger.record(usage_metadata)
        ToolCallLimitMiddleware(run_limit=60, thread_limit=120, exit_behavior="error"),   # M-3
    ],
    context_schema=FillContext,
)
```
**The guards are inside the loop, not around it (C-5).** v1 passed `get_model("analyse").inner`
— the raw provider model — with the comment "GuardedModel-wrapped provider model". It was not:
`.inner` discards the wrapper, and with it every mechanism this spec's claims rest on.
`PromptGuard.assert_clean` never ran on the prompts of the one agent that reads a live,
partially-filled page (a DOM snapshot taken after `FormFiller` has typed carries `value`
attributes — the expected-CTC field is one of them, and "`inspect_form` returns no values" was a
promise about an implementation, not a mechanism). `BudgetGate.check` never ran, so 60 tool calls
× one model round-trip each could run past the $20 hard stop and the $100 ceiling. `SpendLedger`
never recorded, so the header meter, the per-stage cost report and the day total were all
understated whenever a career-page form was processed — breaking AC-NF-09 ("within 1% of provider
usage metadata") *by construction* and making the $5 soft alert fire late or not at all.

v2 removes `.inner` from `GuardedModel` entirely (§4.13) and passes the wrapper, which implements
the `BaseChatModel` surface `create_agent` requires. `GuardMiddleware` is belt-and-braces for the
agent loop specifically: a custom middleware whose `before_model` hook calls
`PromptGuard.assert_clean` and `BudgetGate.check` on every request and whose `after_model` hook
records `usage_metadata` to `SpendLedger` (`langchain/middleware__custom.md`). A static check bans
`.inner` alongside `init_chat_model` (T-0.3).

**`inspect_form` returns a projection, never a serialisation (C-5).** Its return value is built
field by field from the `FormModel` artefact — `field_id`, `label`, `type`, `required`, `options`
— and never by serialising the DOM. A unit test asserts that a page whose CTC field has been
filled produces a tool result containing none of the answer-sheet values.

The agent **never sees or emits a value**: `propose_mapping` takes a *route* (e.g.
`answer_sheet:expected_ctc`), and the deterministic `FormFiller` resolves the route to a value
outside the model loop. That is what makes A-6 hold even where an LLM is in the loop. No
`submit` tool exists in this agent — the click is in the `submit` node, not a tool call, so
`HumanInTheLoopMiddleware` is **not** needed here (the analysis §5.11 suggestion is superseded by
the stronger separation; the middleware stays available if a future ATS needs an in-agent
irreversible action).

**`ToolCallLimitMiddleware` must exit, not merely complain (M-3).** Its kwargs are documented in
`langchain/middleware__built-in.md` §591–660 (`tool_name`, `thread_limit`, `run_limit`,
`exit_behavior`), so v1's `[UNVERIFIED]` was false. It matters: `exit_behavior` defaults to
`'continue'`, which *"[blocks] exceeded tool calls with error messages, [lets] other tools and the
model continue. The model decides when to end based on the error messages."* v1 passed
`run_limit=60` and nothing else, so on hitting the limit the agent kept looping — each blocked call
still costing a model round-trip — until the model chose to stop. The middleware was chosen as the
runaway-loop guard for the system's only agentic component and, as configured, was not one;
combined with C-5 (no `BudgetGate` in the path) the loop had no bound at all. v2 sets
`exit_behavior="error"`, and `fill_form` handles the resulting `ToolCallLimitExceededError` as an
`unsupported_form` fallback.

### 5.5 Compile and wiring (reference shape)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy, TimeoutPolicy, Command, interrupt, Send
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.runtime import Runtime, RunControl
from langgraph.errors import NodeError, GraphDrained

builder = StateGraph(ApplicationState, context_schema=AppContext)
builder.set_node_defaults(retry_policy=RetryPolicy(max_attempts=3))
builder.add_node("load", load)
...
builder.add_node("await_review", await_review)          # graph default retry: interrupts bypass it (M-1)
builder.add_node("fill_form", fill_form,
                 retry_policy=RetryPolicy(max_attempts=1),      # a page-advancing POST is irreversible (C-1)
                 timeout=TimeoutPolicy(run_timeout=600),
                 error_handler=fill_error_handler)
builder.add_node("recheck_after_blocker", recheck_after_blocker,
                 timeout=TimeoutPolicy(run_timeout=120))        # C-2
builder.add_node("submit", submit,
                 retry_policy=RetryPolicy(max_attempts=3, retry_on=is_pre_click_error),
                 timeout=TimeoutPolicy(run_timeout=300),
                 error_handler=submit_error_handler)
builder.add_edge(START, "load")
builder.add_conditional_edges("load", route_after_load)            # documents_only → tailor
builder.add_conditional_edges("factguard", route_after_factguard)  # pass / repair / hitl4
...
application_graph = builder.compile(checkpointer=checkpointer)
```
Static checks (AC-ID-13/14/25, AC-NF-11) run against this module: every function containing
`interrupt(` must be named `await_*`, contain exactly one call, have no `side_effects` registry
call before it, no loop, no `try`; the node named `submit` must contain no `interrupt(` and be
reachable only from `fill_form`; **no module may reference `.inner` or `init_chat_model` outside
`llm/` (C-5); `Settings.submission_enabled` must default to `False` (C-11); and the only edge into
`fill_form` from `await_blocker` must pass through `recheck_after_blocker` (C-2)**.

---
## 6. Data model and persistence

### 6.1 Storage layout

```
%LOCALAPPDATA%\JobAgent\            (default data_dir; ~38 chars; not cloud-synced — AC-NF-19)
├─ jobagent.db                      system of record (SQLite, WAL, synchronous=FULL)
├─ checkpoints.db                   AsyncSqliteSaver (pruned 30 d after terminal, A-17)
├─ art\                             content-addressed artefacts: <sha256[:16]>.<ext>   (flat; C-6)
├─ browser-profile\                 Playwright persistent context (git-ignored, never copied)
├─ traces\                          local trace files (jsonl per day) — TR-7
└─ logs\
```
**DEPARTURE D-5.** UI §3.16 shows storage under the repo (`...\LearningGenAI\JobAgent\data\`).
The Desktop folder on Windows 11 may be OneDrive-synced (Known Folder Move) and the repo path is
already long; `%LOCALAPPDATA%\JobAgent` is shallow, local-only and satisfies AC-NF-19 and C-6.
The path is configurable; the Settings › Data screen shows whichever is in effect.

Path budget: `C:\Users\Avado\AppData\Local\JobAgent\art\0123456789abcdef.html` = 67 chars. Any
computed path > 200 chars is refused at write time (AC-FM-19).

### 6.2 Entity-relationship overview

```
runs 1──* source_runs        runs 1──* queries        runs 1──* jobs (discovered_in)
jobs 1──* job_sources        jobs 1──1 job_evaluations (per run; history kept)
jobs 1──0..1 applications    applications 1──* application_versions 1──* artefacts
applications 1──* answers    applications 1──* decisions      applications 1──* preflight_results
applications 1──0..1 submission_evidence     applications 1──* transitions
applications 1──* fact_checks
company_watchlist            answer_sheet (1 row per field)   years_by_technology
settings (1 row)             spend_ledger                     llm_calls / tool_calls
notifications_outbox         audit_events                     locks       reports
```

### 6.3 Tables (columns that matter; `id` is TEXT uuid4 unless noted)

**runs** — `id, trigger, started_at, finished_at, status (running|finished|finished_warnings|failed|aborted|skipped_lock_held|missed), settings_snapshot JSON, master_hash, counts JSON (discovered, unique, rejected_by_reason, passed, selected, deferred, fallback), spend_usd, rescue_events INT`.

**source_runs** — `run_id, source, policy, status (ok|partial|failed|rate_limited|skipped), queries INT, results INT, new INT, dupes INT, duration_ms, avg_gap_ms, note`. (AC-DS-02, UI §3.9)

**queries** — `id, run_id, source, template, query_text, geography, results INT, issued_at`. (AC-DS-03)

**jobs** — `id, identity_key UNIQUE, ats, ats_job_id, company_norm, company_display, title, title_family, location_norm, location_display, country, canonical_url, first_seen_run_id, last_seen_run_id, posted_at, jd_text_ref (artefact), jd_hash, facts JSON (JobFacts), fetch_status, position_family_id, agency_confidential BOOL`.

**job_sources** — `job_id, source, url, ats_job_id, seen_at, is_canonical BOOL, is_alternative_location BOOL`. (FR-2.1 cluster)

**job_evaluations** — `id, job_id, run_id, verdict (queued|deferred_over_ceiling|by_hand|rejected|expired|duplicate|jd_unavailable|evaluation_failed|possible_repost), reason_enum, reason_text, evidence JSON (spans), score JSON (Score) NULL, total INT NULL, tier, flags JSON, fallback_reason, fallback_state (pending|applied_manually|skipped) NULL, fallback_note, link_verified BOOL, override JSON NULL`. Indexed on `(run_id, verdict)`, `(fallback_state)`.

**applications** — `id (=thread_id), job_id UNIQUE, run_id, mode (auto|assisted|documents_only|manual), channel (greenhouse|lever|workday|career_page|manual), status (§9.2 enum), status_changed_at, created_at, applied_at, score_total, tier, key_skills JSON, master_hash, current_version_id, resume_version (sha256 of PDF) , cover_letter_generated BOOL, notes TEXT, follow_up_date DATE, outcome (none|recruiter_reply|interview|offer|rejected_by_company|withdrawn), submit_attempt INT DEFAULT 0, review_started_at, review_seconds INT, carry_over_from DATE NULL`.
Constraint: `UNIQUE(job_id)` (AC-ID-17). FR-10.1 fields all present (AC-TK-01).

**application_versions** — `id, application_id, version INT, created_by (agent|edit|regenerate|hitl4_fix), tailored_html_ref, pdf_ref, letter_ref, answers_ref, ats_report_ref, fact_check_id, note`. The reviewer always sees `current_version_id`.

**artefacts** — `id (sha256[:16]), kind (jd|form_model|tailored_html|pdf|letter|answers|screenshot|evidence|factguard|preflight|plan|**master_html**), sha256 FULL, bytes INT, path, created_at`. `master_html` (C-8) persists the full bytes of every master ever used by an application, so that stored provenance stays resolvable after the master is edited. Content-addressed; two applications never share a path by accident (AC-RT-13).

**answers** — `application_id, version_id, field_id, label, field_type, route, source (resume:<key>|answer_sheet:<field>|jd:<span>|human:<decision_id>|profile), value_ref (artefact) NULL for answer_sheet routes, halted BOOL`. **Answer-sheet values are never stored here** — `route` names the field; the value is resolved at fill time (AC-CL-18, AC-NF-05). *This is a storage rule, not a display rule (C-7):* `GET /applications/{id}/answers` resolves each route against `answer_sheet` at request time and returns the value in full to the loopback session, so the reviewer certifies what the employer will receive without the value ever being duplicated into this table (§11.7).

**decisions** — `id, application_id, interrupt_kind, interrupt_id, type (approve|reject|regenerate|postpone|edit|hitl3_answer|hitl4_fix|continue|by_hand|abandon|confirmed_submitted|confirmed_not_submitted|i_submitted), reason_code, reason_text, channel (dashboard|telegram|system), actor (session id | chat_id), artefact_hashes JSON, confirmation_text, tabs_reviewed JSON, at`. `approved_without_review` is **gone** (M-13); `tabs_reviewed` records which review tabs were rendered before the decision (M-22). `UNIQUE(application_id, interrupt_id)` → second decision returns "already decided" (AC-HL-08, AC-ID-07).

**preflight_results** — `id, application_id, version_id, run_at, check_name (13 enums), passed BOOL, evidence TEXT, phase (preview|gate|post_blocker)`. (AC-SB-01; `post_blocker` rows are the C-2 re-checks)

**page_commits** (new, C-1) — `application_id, attempt INT, page_index INT, url_hash, committed_at, PRIMARY KEY(application_id, attempt, page_index)`. One row written **before** each page-advancing POST in `fill_form` (§9.8). The row is the durable record that makes an intermediate POST replay-safe, exactly as `SUBMITTING` does for the final click.

**ledgers** (new, C-8) — `master_hash PRIMARY KEY, master_artefact_id (kind='master_html'), built_at, facts JSON, key_set JSON`. The ledger for a `master_hash` is a **record**, not a cache: it is never evicted, and `GET /applications/{id}/bundle` (NFR-3) reconstructs provenance from the row for the application's own `master_hash`.

**submission_evidence** — `application_id, attempt INT, submitting_written_at, click_dispatched_at, final_url, page_text_excerpt, screenshot_ref, http_status, confirmation_kind (page_text|url|email_hint|human), captured_at`. Written in the **same transaction** as the `SUBMITTED` transition (AC-SB-12).

**transitions** — `application_id, from_status, to_status, at, by (node name | api | reconcile), detail JSON`. (TR-7, AC-TK-11)

**fact_checks** — `id, application_id, version_id, artefact_hashes JSON, status (pass|fail|pass_with_confirmed_edits), violations JSON, judge_model, at`. Pre-flight requires a row whose `artefact_hashes` equal the current version's (AC-AF-22).

**confirmations** (new, M-16) — `violation_id PRIMARY KEY, fact_check_id, application_id, version_id, check_name, claim_text, generated_text, typed_text, at, actor`. One row per overridden violation; `typed_text` must equal `generated_text`. A `fact_checks` row may be `pass_with_confirmed_edits` only if every violation it carries is overridable **and** has a row here — enforced in code and re-verified at pre-flight #13. Indexed on `(at, check_name)` for the override count in Reports.

**company_watchlist** — `id, company_display, company_norm, ats (greenhouse|lever|workday|career_page), board_url, extraction_rule JSON, added_by (user|auto), enabled, last_ok_at`.

**answer_sheet** — `key TEXT PRIMARY KEY, value_enc BLOB, kind (currency_inr|months|days|enum|text|bool|date), currency, status (decided|open|unconfirmed|learned), sensitive BOOL, added_by, added_at, used_count, last_used_at, last_used_company`. Values are stored encrypted at rest with a key from the Windows user registry (§12.3); the API returns them only on the Settings › Answer sheet reveal endpoint.

**years_by_technology** — `technology TEXT PRIMARY KEY, years INT, note, added_at`. Empty by default (A-7).

**settings** — single JSON row + `version` for optimistic concurrency; every save appends to `settings_history`.

**spend_ledger** — `id, at, day_ist DATE, run_id, thread_id, node, stage, model, input_tokens, output_tokens, usd, latency_ms`. Index `(day_ist, stage)`.

**llm_calls / tool_calls** — trace rows (prompt hash, not prompt text, in the DB; full prompts in `traces/*.jsonl` after `PromptGuard`, redacted for secrets).

**notifications_outbox** — `idempotency_key PRIMARY KEY, kind (M1..M9|unknown_outcome|handoff), payload JSON (allowlisted variables), created_at, delivered_at, attempts, next_attempt_at, error`.

**audit_events** — `id, at, run_id, application_id, job_id, kind (guard|hitl_decision|source|system|override|rescue), rule, text, outcome, detail JSON`. Guard-events panel = `kind='guard'`.

**locks** — `name PRIMARY KEY, holder, acquired_at, heartbeat_at, expires_at`. `run` and `thread:<application_id>`.

**reports** — `date, kind (morning|evening), body JSON, telegram_message_id, sent_at`.

### 6.4 Invariants enforced by the database

| Invariant | Mechanism |
| --- | --- |
| One application per job | `applications.job_id UNIQUE` |
| One job per identity | `jobs.identity_key UNIQUE` |
| One decision per interrupt | `decisions (application_id, interrupt_id) UNIQUE` |
| Legal transitions only | `Tracker.transition` uses `UPDATE … WHERE status IN (allowed)`; trigger rejects direct status writes not matching the transition table (`CHECK` via trigger on `applications`) |
| `SUBMITTED` implies evidence | Trigger: `AFTER UPDATE OF status` when `NEW.status='SUBMITTED'` requires a `submission_evidence` row for `(application_id, submit_attempt)` — same transaction |
| `SUBMITTING` implies a fresh fact-check (M-15) | Trigger: `BEFORE UPDATE OF status ON applications WHEN NEW.status='SUBMITTING'` requires a `fact_checks` row whose `artefact_hashes` equal the current version's and whose status is `pass` or `pass_with_confirmed_edits`. v1 enforced AC-AF-22 in pre-flight check #7 alone — an ordinary node — although the AC is written as an invariant over *any* path to `SUBMITTING`, and although the structurally identical evidence rule already had a trigger. The gap was reachable: the §7.4 edit endpoints have no status guard, so an edit issued between pre-flight and `submit` creates a new version and a new `fact_checks` row while `submit` writes `SUBMITTING` with no re-check |
| No POST to an already-committed page (C-1) | `page_commits (application_id, attempt, page_index)` PRIMARY KEY; `FormFiller` inserts before the POST, so a replay collides instead of re-posting |
| Provenance resolves or fails loudly (C-8) | `ledgers.master_hash` FK from `applications.master_hash`; `build_ledger` raises `MasterIdsMissing` rather than deriving keys |
| No answer-sheet values outside their table | `answers.value_ref` must be NULL when `route LIKE 'answer_sheet:%'` (CHECK) |

### 6.5 Retention

Records are kept forever (Q-9). `retention_job` (03:00 daily): for each thread whose application
reached a terminal status ≥ 30 days ago, call **`await checkpointer.adelete_thread(thread_id)`** —
falling back to `aprune` if the installed saver exposes it — then `VACUUM` `checkpoints.db`
(AC-NF-12).

**M-2.** v1 marked this `[UNVERIFIED]` and instructed the implementer to hand-delete rows from the
saver's tables by `thread_id` after confirming table names against the installed package. That was
false and dangerous. `langgraph/checkpointers.md` documents `adelete_thread` in the checkpointer
interface (§407) and gives it its own subsection (§544: *"delete_thread / adelete_thread — Delete
all checkpoints and writes for a thread. Both checkpoint rows and write rows must be deleted"*), and
the same page's extended-capabilities table lists `aprune` for thread-history pruning. Hand-rolled
deletion against an inferred internal schema — where a checkpoint and its `writes` rows must be
removed together — is the most likely way to corrupt `checkpoints.db`, which is precisely the
assumption R-10 rated *Low* on. **AC-NF-12 is amended to assert the API was called**, not merely
that rows disappeared.

### 6.6 Windows `MAX_PATH`

All generated files are content-addressed in one flat directory; no per-company folders; no
filenames derived from job titles. Repo paths stay shallow: `src/jobagent/<module>.py`,
`tests/<group>/test_<name>.py`, `fixtures/jds/<slug>.md`. A test asserts no path in the repo or
data dir exceeds 200 characters (AC-FM-19).

---

## 7. API specification

Base: `http://127.0.0.1:8765/api/v1`. JSON. No authentication in v1 (loopback only, A-16); a
per-process CSRF token is required on every mutating request and is embedded in the SPA at load
(defence against a malicious page in the same browser hitting `127.0.0.1`). Errors:
`{error: {code, message, field?}}`; `409` for state conflicts, `404` unknown id, `400`
validation, `423` locked.

Live updates: `GET /api/v1/events` (SSE) emits `{type, id, at, data}` for
`run.stage`, `application.status`, `spend.update`, `needs_you.changed`, `queue.changed`,
`settings.changed`, `notification.status`. Every mutation that changes a table the UI shows
emits an event within 1 s (AC-UI-15).

### 7.1 Endpoint map by screen

| Screen (UI §) | Endpoints |
| --- | --- |
| Today `/` (3.2) | `GET /dashboard/today` → CTA counts (pending, carry-over, oldest age, estimate), needs-you list, funnel, by-hand summary, sources health, top matches, spend today/14-day |
| Header chrome (2.2) | `GET /status` → run state, next run, spend vs soft/hard/ceiling, pause flag, telegram health |
| Queue (3.3) | `GET /queue?sort=carry_over_first` → rows with docs flags; `GET /queue/not-in-queue` |
| Review (3.4–3.6) | `GET /applications/{id}/review` → job rail, score, flags, watch items, pre-flight preview, versions; `GET /applications/{id}/diff` → structural diff (change classes); `GET /applications/{id}/letter` → claims with provenance; `GET /applications/{id}/answers` → routed answers **with the values that will be typed into the form, in full** (C-7; loopback session only — see §11.7); `GET /artefacts/{id}` (PDF/HTML download); `POST /applications/{id}/reveal-answer` (transient; audited) |
| Decide (5.1) | `POST /applications/{id}/decisions` `{type: approve|reject|postpone|regenerate|dismiss_expired, reason_code?, reason_text?, artefact_hashes}` → `202 {decision_id, effective_at}`; `POST /applications/{id}/decisions/{decision_id}/undo` (within grace) |
| Edit (3.7) | `PUT /applications/{id}/letter` `{claims}`, `PUT /applications/{id}/resume-text` `{block_edits}`, `PUT /applications/{id}/answers/{field_id}` `{text}` → each returns new `version_id`, `fact_check`, `ats_report?`, `preflight_preview`; `POST /applications/{id}/revise` `{instruction}` → agent revise (costs; returns estimate first with `?estimate=1`); `POST /applications/{id}/confirm-edit` `{confirmation_text}` (AC-AF-19) |
| Reject overlay (3.8) | part of decisions; `reason_code ∈ {not_relevant, weak_fit, company, location, regenerate, other}`; reject without reason → `400` (AC-HL-04) |
| Audit › Sources/Queries (3.9) | `GET /runs/{date}/sources`, `GET /runs/{date}/queries`, `POST /runs/{date}/sources/{source}/retry` |
| Audit › Jobs (3.10) | `GET /runs/{date}/jobs?verdict&source&tier&geo&fallback_state&q` (paginated, < 1 s at 500 rows — AC-DS-12); `POST /jobs/{id}/fallback-state` `{state, note, applied_at?}` |
| By hand (3.11) | `GET /fallback?state=pending&runs=all`; `POST /jobs/{id}/fallback-state`; `POST /jobs/{id}/prepare-documents` (spawns documents_only thread; returns cost estimate on `?estimate=1`); `POST /applications/{id}/resume-with-agent` (HITL-2 continue) |
| Tracker (3.12) | `GET /applications?status&channel&tier&geo&from&to&follow_up_due`; `GET /applications/{id}` (expansion: URL, dates, versions, answers, key skills); `PATCH /applications/{id}` `{outcome?, notes?, follow_up_date?}`; `GET /applications/{id}/bundle` → NFR-3 reconstruction (zip of PDF, HTML, letter, answers with sources, form payload record, evidence, score, decisions, **plus the `master_html` artefact and the `ledgers` row for this application's `master_hash`, and its `confirmations` rows** — M-16/M-19: without the master and ledger the archived letter's `[n]` markers cannot be resolved, and `element_text(html, key)` has no `html` to read); `GET /applications.csv` |
| Job detail (3.13) | `GET /jobs/{id}` → score breakdown, hard rules with spans, dedup cluster, timeline, JD text with highlighted spans, scored-by/cost; `POST /jobs/{id}/promote` (soft rejections only — §17 D-6; `409` for hard rules); `POST /jobs/{id}/rescore` |
| Settings › Answer sheet (3.14) | `GET /answer-sheet` (masked; usage counts; impact box `GET /answer-sheet/work-auth-impact`); `POST /answer-sheet/reveal` (returns values once; audited); `PUT /answer-sheet/{key}`; `GET/PUT /answer-sheet/years-by-technology` |
| Settings › Targets, Models, Sources, Schedule, Notifications, Data (3.15–3.16) | `GET /settings`, `PUT /settings` (validated; `409` on version mismatch); `GET /settings/models/usage-today`; `GET/PUT /watchlist`, `POST /watchlist/import`; `POST /telegram/test`; `GET /data/summary`, `POST /data/export` |
| Reports (3.17) | `GET /reports/{date}` (morning + evening), `GET /reports/trend?days=14`, `GET /reports/{date}.txt` |
| Runs (3.18) | `GET /runs/{date}` → stages, per-stage cost, live step, events, secrets-guard counter; `GET /runs/{date}/events?level`; `GET /traces/{thread_id}`; `POST /runs` (run now) → `202` or `409 lock_held`; `POST /runs/{id}/resume` |
| Needs-you-now (3.19) | `GET /needs-you` → blocked (HITL-2), questions (HITL-3), claims (HITL-4), unknown outcomes, failed submissions; `POST /applications/{id}/hitl3` `{answers: [{field_id, text, save_as?}], skip_job?}`; `POST /applications/{id}/hitl4` `{action: use_resume_wording|edit|skip_job, text?}`; `POST /applications/{id}/blocker` `{action: i_submitted|continue|by_hand|abandon}` (C-2); `POST /applications/{id}/take-over-browser` (brings window to front); `POST /applications/{id}/unknown-outcome` `{outcome: confirmed_submitted|confirmed_not_submitted|check_again_later, confirmation_text?, checked_ats_account?}` — the `confirmed_not_submitted` branch requires both extra fields and a minimum elapsed time, or `409` (C-3, §9.5); `POST /applications/{id}/handoff` `{action: i_submitted|by_hand|abandon}` |
| Controls (UI-13) | `POST /control/pause`, `POST /control/resume`, `GET /control` |
| Guard events (UI-11) | `GET /audit-events?kind=guard&from&to` |

### 7.2 Decision semantics (the contract the graph relies on)

```
POST /applications/{id}/decisions {type: approve, artefact_hashes, tabs_reviewed}
  1. Load application; require status ∈ {PENDING_REVIEW}; else 409 {code: "not_pending"}.
  2. Require a pending interrupt on the thread (aget_state → tasks[*].interrupts non-empty, kind=review); else 409.
  3. Compare artefact_hashes with current version's hashes; mismatch → 409 {code: "stale_artefacts"} (reviewer reloads).
  4. Require fact_checks row for these hashes with status pass|pass_with_confirmed_edits; else 409 {code: "fact_check_required"} — and Approve is disabled in the UI anyway.
  5. (M-22) Require tabs_reviewed ⊇ tabs_with_content(application): always "resume"; "letter" if a letter
     artefact exists; "answers" if any field is routed. Else 409 {code: "tabs_unreviewed", missing: [...]}.
  6. INSERT decisions (interrupt_id = pending interrupt id, tabs_reviewed). UNIQUE violation → 200 {already_decided: true, decision_id}.
  7. Transition PENDING_REVIEW → APPROVED_GRACE (effective_at = now + 5 s). Emit SSE.
  8. After effective_at, resume_worker: acquire thread lock → ainvoke(Command(resume={...decision}), config, durability="sync").
Undo within grace: DELETE decision row + APPROVED_GRACE → PENDING_REVIEW. After grace: 409 {code: "already_submitting"}.
The undo is addressed by decision_id and is NOT scoped to the current route (M-22): Z undoes the most
recent decision still inside its grace window, whichever application the reviewer is now looking at.
```
**Why approval is gated on rendering, and why the undo is global (M-22).** v1 carried two
keybindings from the UI design into §14.2 — `A` and `Shift+A` — and defined neither. In the UI they
are *Approve & next* and *Approve & stay*, so the **primary, unshifted key approved the current
application and navigated away from it**. The physical action for fifteen applications was fifteen
presses of one key with nothing in between, which is not review, it is a counter.

That interacted badly with the only real safeguard. The 5-second grace and the `Z` undo were both
scoped to the application on screen; once `A` had advanced, the reviewer was looking at something
else while the previous toast expired behind him. The undo affordance was designed for a workflow
the primary keybinding prevented.

And nothing gated Approve on having *looked*. The three tabs are `1/2/3`, and approval was reachable
from tab 1 alone — so for an application whose only risk lives on tab 3, which after **C-7** is
where the values actually sent to the employer are rendered, the reviewer could approve without that
risk ever being drawn on screen.

v2.3 therefore: swaps the bindings so the unshifted key **stays** (§14.2); refuses the approval at
the API unless every tab with content was rendered; records the tab set on the decision row, which
costs nothing and makes AC-NF-15's telemetry mean something; and makes the grace toast a fixed
element addressed by `decision_id`, so `Z` still works after advancing.

This is a real mitigation, not a solution. A determined reviewer can press `1`, `2`, `3`, `A` as a
four-key chord and learn nothing. What the gate removes is the *cheapest* path — approval without
the evidence ever being rendered — which is the specific failure the review identified. The residual
is still the one R-3 names, and it is still rated Medium.

`reject` skips the grace window and resumes immediately; `postpone` and `dismiss_expired` are API-only
(no resume; `dismiss_expired` transitions to `EXPIRED` and cancels the thread by resuming with
`{type: "expired"}` so the thread reaches `finalize`).

`POST /applications/{id}/hitl3` etc. follow the same pattern: validate pending interrupt kind,
insert decision (idempotent), resume. Malformed payloads → `400` with no state change (AC-HL-23).
Decisions for terminal or unknown threads → `404`/`409` (AC-HL-07).

### 7.3 Telegram command mapping

`/reject <short_id> <1-6> [text]` → same handler as the dashboard reject with `channel=telegram`.
`/approve <short_id>` → **not a command.** It replies with the dashboard link and nothing else;
there is no flag that changes this (M-13). `/pause`, `/resume`, `/status`. Everything else → help.
Sender check precedes parsing.

### 7.4 Edit pipeline (server side)

```
PUT /applications/{id}/letter {claims}
  → validate claim schema (provenance present or kind=context)
  → FactGuard.check(letter=claims, tailored=current, answers=current)  (synchronous, judge model)
  → new application_versions row (created_by=edit) + artefacts + fact_checks row
  → if fail: response includes violations, each with violation_id, class and its GENERATED confirmation string;
     application flag `needs_confirmation`; Approve stays disabled until every overridable violation is confirmed:
       POST /confirm-edit {violation_id, confirmation_text}   # text must equal the generated string verbatim
     A violation in a non-overridable class (§8.3) cannot be confirmed: 409 {code: "not_overridable", check}.
     When all violations are confirmed → fact_checks.status = pass_with_confirmed_edits (A-20, AC-AF-19, M-16)
PUT /applications/{id}/resume-text {block_edits: [{element_key, new_text}]}
  → apply to tailored HTML (text nodes only; structure immutable) → render.py → ats_check → FactGuard → new version
```
**Status guard (m-5, closed as part of M-15).** Every edit endpoint requires
`applications.status ∈ {PENDING_REVIEW, TAILORING_FAILED}`; anything at or beyond
`APPROVED_GRACE` returns `409 {code: "not_editable"}`. Without it, an edit issued between
pre-flight and `submit` silently created a new version and a new `fact_checks` row while `submit`
wrote `SUBMITTING` against the old ones — the path that made M-15's missing database trigger
reachable. The guard and the trigger are independent; both are required.

Edits never touch the master (AC-RT-01).

---
## 8. The anti-fabrication verifier (FactGuard)

### 8.1 Position in the pipeline

FactGuard is a **deterministic-first, judge-second** verifier that runs on every generated
artefact (tailored HTML, letter claims, subjective answers, any edited version) and returns
`pass | fail` with a typed violation list. It is not advisory: a failing result blocks the
artefact from `PENDING_REVIEW` (repair loop) and blocks the `SUBMITTING` transition
(pre-flight #6–#9 and AC-AF-22). The generator is *constrained* (plans and claims, §10) so that
most violations are impossible by construction; FactGuard exists for the residue and for
Avadh's edits.

```
 artefacts ──▶ C1 structural diff ──▶ C2 immutables ──▶ C3 numbers ──▶ C4 technologies/canaries
           ──▶ C5 organisations/projects ──▶ C6 degrees/certs ──▶ C7 years ──▶ C8 scope verbs
           ──▶ C9 provenance resolution ──▶ C10 entailment (judge) ──▶ C11 company facts ──▶ C12 filler
           ──▶ C13 mandatory-gap claims ──▶ C14 claim-kind integrity (runs before C9 on claims)
           ──▶ result {status, violations[]}
 Deterministic C1–C9, C12–C14 (no model). C10–C11 use the `judge` stage. Any single violation → fail.
```

### 8.2 Checks

| # | Check | Input | Rule | AC |
| --- | --- | --- | --- | --- |
| C1 | Structural diff whitelist | master HTML, tailored HTML | Every DOM change ∈ {reorder `<li>` within same `<ul>`; reorder `.skill` lines; reorder values within one skill line; rewrite of `summary.p1`; toggle `<b>`/`.nw` on existing text; removal of an `<li>`}. Any insertion of `<li>`, `<h3>`, `.skill`, skill value, or any text change inside `<li>` other than whitelisted rewordings with provenance → `structure_violation` | AF-06, RT-02 |
| C2 | Immutables | tailored HTML | `hdr.role` == "Senior AI Solution Engineer"; `exp.krista.meta` dates, `edu.p1`, all `hdr.contact.*` byte-identical; `<style>` identical modulo letter-spacing rule; every master `.nw` span present | AF-05, RT-07/10/11 |
| C3 | Numeric invariant | every artefact | Each numeral token + qualifier + 3-word context must (a) match a ledger number with the **same qualifier**, or (b) sit in a sentence whose provenance is a JD/page span (company-fact), or (c) be a current-year date in a letter header. `25+`→`25`, `up to 80%`→`80%` fail | AF-02, AF-07 |
| C4 | Technology vocabulary | every artefact | Extracted tech terms ⊆ ledger ∪ synonym table (exact, versioned); any canary → fail; canary allowed only inside a company-fact sentence with JD provenance ("your Azure-based platform") | AF-03 |
| C5 | Organisations / projects | every artefact | Organisations ⊆ {Krista Software, MITAOE forms, target company, tools on the resume}; projects ⊆ ledger projects | AF-04 |
| C6 | Degrees / certifications | every artefact | Zero matches of the cert/degree pattern list in self-descriptive text (ledger has none beyond B.Tech) | AF-13 |
| C7 | Years | every artefact + form answers | `(\d+)\+?\s*(years?|yrs?)` → value ≤ floor(years since Aug 2022)+1, `+` only while `4+` remains true, attached to *total* experience; a technology-attached years value must equal the `years_by_technology` entry exactly | AF-10 |
| C8 | Scope verbs | reworded sentence vs source element | Verb scope rank (config table: `mentor < lead < manage < head < found`) may not increase; `founded`, `CTO`, `Head of`, `managed a team of N≠4` → fail. Source `exp.krista.li2` ("Lead engineer on two flagship…") permits "led" for MCP server and AIQA | AF-09 |
| C9 | Provenance resolution | claims | Every `self` claim has ≥ 1 provenance key that exists in the ledger for `master_hash`; element text shares ≥ 2 content lemmas with the claim; claims without pointer → fail | AF-08, T-5 |
| C10 | Entailment | claims | Judge model (`judge` stage ≠ `generate`) answers `ENTAILED | PARTIAL | NOT_ENTAILED` to "Does the source text fully support every claim in this sentence?" per claim; anything but `ENTAILED` → fail. Structured output; the judge sees only source text + claim (never the answer sheet) | AF-08 |
| C11 | Company facts | `company` claims | Provenance must be a `jd:` or `page:` span fetched this run; span text must entail the claim (judge) | AF-18 |
| C12 | Filler | letter, answers | Banned-phrase list (config) → 0 hits; word caps (letter ≤ 300, answer ≤ 150); five sections present in order | CL-01/02/04 |
| C13 | Mandatory-gap claims | all artefacts + job's `mandatory` list | No artefact may present a missing mandatory qualification as held (`PhD`, `doctorate`, `certified`, the certification name, the core technology) | AF-12, T-3 |
| **C14** | **Claim-kind integrity (C-6)** | claims | A `kind="context"` claim whose text contains a first-person pronoun, or a resume-vocabulary verb phrase with an implied first-person subject, is **reclassified to `self`** and must then satisfy C9 and C10. Caps: ≤ 2 `context` claims per letter, 0 per subjective answer; exceeding a cap is a `claim_kind_violation`. Deterministic; runs **before** C9 so that a relabelled claim cannot skip provenance | AF-08, T-5 |

**Extractors** are shared with the ledger builder (same tokenisers, same synonym table) so that
"what counts as a number/tech/org" is defined once.

### 8.3 Result and repair

```python
class Violation(BaseModel): check: str; fact_class: FactClass | None; artefact: str; location: str; text: str; nearest_facts: list[str]; severity: Literal["fail"]
class FactGuardResult(BaseModel): status: Literal["pass","fail","pass_with_confirmed_edits"]; violations: list[Violation]; artefact_hashes: dict[str,str]; judge_model: str; at: datetime
```
- **Repair loop** (graph `repair` node): violations are fed back to the generator for the
  offending artefact only, with the offending sentence and the nearest ledger facts; at most
  **2** regenerations (`repair_count`), then `HITL-4` with the sentence highlighted (AC-AF-17).
  No artefact that failed is ever placed in the queue as ready.
- **Edits**: run synchronously (§7.4); failure → `needs_confirmation`; explicit confirmation
  text stored; status `pass_with_confirmed_edits` (A-20). Avadh is the authority on his facts,
  but the confirmation is logged and pre-flight shows it.

**Which checks a confirmation may override, and which it may not (M-16).** v1 let one constant
phrase — `"I confirm this statement is true"` — override *every* fabrication class, and pre-flight
re-ran exactly one of them (#12, C13). So an edit that tripped C3 (an invented metric), C4 (a
canary technology such as `Azure` or `TensorFlow`) or C7 (a years figure contradicting
`years_by_technology`) shipped. T-1 is as absolute as T-3 — *"**Never** invent … technologies … or
years of experience"* — and it is the class of lie a recruiter checks first. AC-AF-19's own worked
example, *"5 years with LangChain"*, is a C7 violation, and v1's flow shipped it.

The distinction v2.2 draws is **authorship versus fact**. Avadh is the authority on how his own
achievements are worded. He is not an authority on whether a technology appears on his résumé, or
on arithmetic over his own employment dates.

| Class | Override | Why |
| --- | --- | --- |
| C9 provenance · C10 entailment · C12 filler | **Allowed** | Genuine authorship: the judge can be wrong about whether his own sentence is supported by his own résumé line |
| C3 numbers | **Allowed, per violation** | He may legitimately know a figure the résumé does not carry — but the confirmation must name the figure, and pre-flight re-checks it (§9.4 #13) |
| C1 structure · C2 immutables · C4 technologies/canaries · C5 organisations · C6 degrees/certs · C7 years · C8 scope verbs · C13 mandatory gaps · C14 claim kind | **Never** | None of these is a matter of authorship. A confirmation cannot make a technology appear on the résumé or change a date range |

A `fact_checks` row may therefore reach `pass_with_confirmed_edits` **only** if every violation it
carries is in an overridable class and has its own stored confirmation. One non-overridable
violation means `fail`, and no amount of typing changes it.

**Confirmations are per violation, and the text is generated, not memorised (M-16).** Each
`Violation` gets a stable `violation_id` (check + artefact + location + sha256 of the text). The
confirmation string is **generated from the violation** and must be typed verbatim — *"I confirm:
5 years with LangChain"*, not a constant. A phrase that names the specific claim cannot become
muscle memory the way a fixed sentence does by its third use, and it puts the disputed statement in
front of the person confirming it.

**Overrides are counted (M-16).** The evening report and the weekly summary carry a rolling count
of confirmed overrides by class (§13.5). Three in a week is a signal — about the generator or about
the reviewer — and either is worth surfacing rather than discovering later.
- **Guard events**: every violation → `audit_events(kind='guard')` with job, rule, text,
  outcome (repaired / paused_hitl4 / rejected / confirmed_by_user) (AC-AF-23).

### 8.4 Testing the verifier harder than the generator

FactGuard ships with its own fixture suite: 40 seeded fabrications must all be flagged with the
correct `fact_class` (AC-AF-15, 40/40 or the build fails), and 10 legitimate tailorings plus the
unmodified master must produce 0 flags (AC-AF-16). **The 40 are re-cut in v2 (C-6):** v1 organised
them one per fact class and sub-rule, which is why the suite could not catch a failure of *claim
kind*. Two of the 40 are now claim-kind mutations — a `self` claim relabelled `context`, and a
`context` claim over the cap — and the count stays 40 so AC-AF-15 is unchanged.
The synonym and canary tables are versioned; a change to either re-runs the suite.

### 8.5 How the UI plugs in

| UI element | Data |
| --- | --- |
| Resume tab diff (`−/+`, `~↑↓`, `·`) | `GET /applications/{id}/diff` = C1's change list; a `violation` class renders red and disables Approve |
| Skills "reordered · nothing added" | C1 result for `.skill` lines |
| Pre-flight "facts 49/49", "no fabrication", "no false qualification" | `fact_checks.status`, C3–C8 counts, C13 |
| Letter `[n]` markers; unresolved marker red | `Claim.provenance` and C9/C10 per claim; `kind=context` markers grey, **with a running count "context 2/2" beside them** so an artefact that has quietly become mostly grey is visible (C-6) |
| Edit mode live guard ("no resume source — will block approve") | C9 executed client-side on keystroke against the ledger shipped to the SPA (`GET /ledger` — facts and element keys only, no answer sheet), authoritative check on save |
| HITL-4 card (claim vs resume line, "Use resume wording") | `Violation.text`, `nearest_facts`, `element_text(key)` |
| Guard-events panel | `audit_events kind=guard` |

---

## 9. The submission protocol

This is the safety-critical mechanism. It is specified as a state machine in the tracker, a node
contract in the graph, and a recovery routine at startup — three independent layers that each
prevent a second click.

### 9.1 The problem

LangGraph restarts a node from its first line on resume and retries a failed node per its
`RetryPolicy`. Between the ATS accepting a POST and the tracker recording `SUBMITTED`, a crash,
timeout, `500`, or dropped connection leaves the outcome unknown. A naive retry sends a second
application; not retrying may lose one. C-3 says there is no unsend. Therefore: **once a click
has been dispatched, the system never clicks again for that application without a human saying
the first click did not land.**

**Two corrections v2 makes to that framing.**

*The irreversible act is not only the final click (C-1).* `FormModel.fields` carries `page_index`
because ATS forms are multi-page, and a multi-page form is advanced by **submitting the current
page** — an HTTP POST that on Greenhouse's multi-step flows, on Workday and on many career-page
ATSs creates a server-side record: a draft, a partial application, or in several tenants an
application the employer can already see. v1 asserted `fill_form` performs "no POST" (§5.3, §13.6
FM-05) and built the whole of §9 on the premise that exactly one act was irreversible. The premise
was false, and two details made it worse: `fill_form` inherited the graph-wide
`RetryPolicy(max_attempts=3)`, so a page-advancing POST could be re-issued three times per node
attempt; and `fill_form` is re-entered from `await_blocker`, where LangGraph restarts a node from
its first line, so every blocker resume replayed every page advance. None of those POSTs wrote
`SUBMITTING`, captured evidence, or could reach `UNKNOWN_OUTCOME`. §9.8 extends the protocol to
cover them.

*The question is not only "who may click twice" but "what manufactures the condition that permits
it" (C-10 → C-3).* `UNKNOWN_OUTCOME` is the one state from which a second click is sanctioned. v1
treated it purely as an input. In fact the system could **produce** it spuriously — a second
process flipping a live `SUBMITTING` row four seconds after a real click — and then resolve it
through a one-click path with less friction than editing a sentence of a cover letter. Every layer
behaved correctly; the protocol was not defeated, it was *fed*. §9.5 and §9.6 close both ends.

### 9.2 Application state machine

```
                       create             tailoring ok / docs           (documents_only) ─▶ DOCS_READY ─▶ (by hand) MANUAL
 [new] ──▶ PREPARING ──────────────────────────────▶ PENDING_REVIEW ◀─────────────────┐
              │ tailoring/ATS fail                       │ approve (API)               │ undo (Z, ≤5 s)
              ▼                                          ▼                             │
        TAILORING_FAILED                            APPROVED_GRACE ────────────────────┘
              │ retry tailor (API)                       │ effective_at reached → resume
              ▼                                          ▼
          PREPARING                                  APPROVED ──preflight fail──▶ PREFLIGHT_FAILED ──(fix/retry)──▶ APPROVED
                                                         │                       └──posting closed──▶ EXPIRED
                                                         ▼ preflight ok
                                                    PREFLIGHT_OK ──fill starts──▶ FILLING ──blocker──▶ BLOCKED ──┬─i_submitted──▶ SUBMITTED(human)
                                                         │                            ▲                        └─continue──▶ recheck ──▶ FILLING
                                                         │                            └── per-page commits recorded in `page_commits` (§9.8)
                                                         │  (assisted) ──▶ HANDOFF ──i_submitted──▶ SUBMITTED(human)  / by_hand ──▶ BY_HAND
                                                         ▼ fill complete, about to click
                                                     SUBMITTING   ◀── written durably BEFORE the click; carries submit_attempt
                                                         │
                          ┌──────────────────────────────┼──────────────────────────────┐
                          ▼ evidence captured             ▼ any doubt after dispatch      ▼ (never from here: a retry)
                      SUBMITTED                      UNKNOWN_OUTCOME
                                                         │ human: confirmed_submitted ──▶ SUBMITTED (confirmation_kind=human)
                                                         │ human: confirmed_not_submitted ──▶ APPROVED (submit_attempt+1) ──▶ preflight ─▶ …
 Other terminals: REJECTED_BY_USER · EXPIRED · BY_HAND · ABANDONED · NEEDS_ATTENTION (recoverable) · PAUSED_BUDGET (recoverable)
 Dedup treats {SUBMITTING, UNKNOWN_OUTCOME, SUBMITTED, MANUAL, REJECTED_BY_USER} as "applied".
```

**`FILLING` (new in v2, C-1).** Written when `fill_form` begins browser work and before any
page-advancing POST, so that the tracker — not a process-local variable — knows an application is
mid-form. It carries `submit_attempt` like `SUBMITTING`, and the per-page markers live in
`page_commits`. A crash in `FILLING` is recoverable (§9.6 step 3) because a page commit is
individually recorded; a crash in `SUBMITTING` is not, and still goes to `UNKNOWN_OUTCOME`.

**Legal transitions** are a fixed table in `tracker/transitions.py`; `Tracker.transition` is a
single conditional `UPDATE` plus a `transitions` row plus (for `SUBMITTED`) the evidence insert,
all in one SQLite transaction. There is deliberately **no** transition `UNKNOWN_OUTCOME → SUBMITTING`
and **no** transition `SUBMITTING → SUBMITTING`.

### 9.3 The `submit` node

```python
class PreClickError(Exception): ...      # navigation, page load, selector missing, network before dispatch
class PostClickError(Exception): ...     # anything after click_dispatched — never retried

def is_pre_click_error(exc: BaseException) -> bool:
    return isinstance(exc, PreClickError) or (isinstance(exc, NodeTimeoutError) and not _click_dispatched_marker(exc))

async def submit(state: ApplicationState, runtime: Runtime[AppContext]) -> dict:
    tr, bw = runtime.context.tracker, runtime.context.browser
    app = await tr.get(state["application_id"])

    # (0) Master switch — before any browser work (C-11).
    if not runtime.context.settings.submission_enabled:
        await tr.transition(app.id, {"PREFLIGHT_OK", "FILLING"}, "NEEDS_ATTENTION",
                            detail="submission_enabled=false")
        raise SubmissionDisabled(app.id)

    # (1) Idempotency gate — the node may be re-entered by retry, resume, or crash recovery.
    if app.status == "SUBMITTED":
        return {"submit_result": "submitted"}
    if app.status in ("SUBMITTING", "UNKNOWN_OUTCOME"):
        # A previous execution reached the point of no return. Never click again.
        await tr.transition(app.id, {"SUBMITTING", "UNKNOWN_OUTCOME"}, "UNKNOWN_OUTCOME",
                            detail="re-entered submit after click dispatch")
        return {"submit_result": "unknown"}
    if app.status != "PREFLIGHT_OK":
        raise IllegalTransition(app.status)

    # (2) Pre-click work — retryable, side-effect free with respect to the ATS.
    page = await bw.page_for(state["fill_session"])           # raises PreClickError if the page is gone → Command(goto="fill_form") via error handler
    fp = await bw.page_fingerprint(page)                      # (C-2) same document instance we filled?
    if fp.dom_hash != state["fill_fingerprint"]:
        # A human took over and the page moved on — or the ATS replaced it. Never click a page we did not fill.
        return Command(update={"blocker": {"kind": "page_changed"}}, goto="notify_blocked")
    await bw.verify_filled(page, state["answers"])            # PreClickError on mismatch
    selector = await bw.locate_submit(page)                   # PreClickError if not found
    if await bw.detect_blocker(page):
        return Command(update={"blocker": ...}, goto="notify_blocked")

    # (3) Point of no return — durable BEFORE the click. synchronous=FULL, fsync'd.
    await tr.transition(app.id, {"PREFLIGHT_OK"}, "SUBMITTING", submit_attempt=app.submit_attempt + 1,
                        submitting_written_at=now())
    _mark_click_dispatching(state["application_id"])          # process-local marker read by is_pre_click_error

    # (4) The click and everything after it. Any exception here is PostClickError.
    try:
        await bw.click_submit(page, selector)
        evidence = await bw.capture_evidence(page, timeout_s=180)  # final URL, confirmation text, screenshot, status (C-3: 60 s was short for a slow ATS and manufactured UNKNOWN_OUTCOME on successes)
    except BaseException as e:
        # includes asyncio.CancelledError and NodeTimeoutError: outcome unknown
        await tr.transition(app.id, {"SUBMITTING"}, "UNKNOWN_OUTCOME", detail=repr(e))
        return {"submit_result": "unknown"}

    # (5) Evidence and SUBMITTED in ONE transaction (trigger enforces evidence presence).
    if evidence.confirms_submission:
        await tr.transition(app.id, {"SUBMITTING"}, "SUBMITTED", applied_at=now(), evidence=evidence)
        return {"submit_result": "submitted"}
    await tr.transition(app.id, {"SUBMITTING"}, "UNKNOWN_OUTCOME", detail="no confirmation signal", evidence=evidence)
    return {"submit_result": "unknown"}
```

`submit_error_handler(state, error: NodeError) -> Command` (verified: `fault-tolerance.md`
Error handling) runs after retries are exhausted: if the failure is a `PreClickError` of kind
`page_lost` → `Command(goto="fill_form")`; any other pre-click failure → status
`NEEDS_ATTENTION`, `Command(goto="finalize")`; it **never** routes back into `submit`, and it
never fires for a post-click failure because step (4) converts those into a normal return.

**Why the `try` is acceptable here.** AC-ID-14 bans `try` around `interrupt()`; `submit`
contains no `interrupt()`. The `try` exists precisely to convert *every* post-dispatch exception,
including cancellation, into `UNKNOWN_OUTCOME` rather than letting the retry policy see it.

**Timeouts.** `TimeoutPolicy(run_timeout=300)` covers the whole node — raised from 180 s so that
the 180-second evidence capture (C-3) cannot itself be cut short by the node budget. A timeout during (2) is
`NodeTimeoutError` with no dispatch marker → retryable (AC-FM-18, `delay(120000)` on page load).
A timeout during (4) is caught by the `try` → `UNKNOWN_OUTCOME`. If the process is killed between
(3) and (4), the marker is gone but the tracker row says `SUBMITTING` → gate (1) → `UNKNOWN_OUTCOME`
(AC-ID-04). If killed after the click but before (5), same path (AC-ID-05). If killed after (5),
gate (1) returns immediately (AC-ID-06).

### 9.4 Pre-flight (FR-9.1) — runs after approval, immediately before `fill_form`

| # | Check | How | Fail → |
| --- | --- | --- | --- |
| 1 | `company_match` | Live re-fetch of `canonical_url`; company name on page normalises to the record's | `PREFLIGHT_FAILED` |
| 2 | `job_match` | ATS job id / title family matches record (`title_changed` fixture) | `PREFLIGHT_FAILED` |
| 3 | `still_active` | HTTP 200, no closed marker, not redirected to careers home. **Unreachable ⇒ `still_active_unverified` ⇒ hard fail (C-4)** | `EXPIRED`, or `PREFLIGHT_FAILED` when unverifiable |
| 4 | `score_sufficient` | `applications.score_total ≥ 70` re-read from DB | `PREFLIGHT_FAILED` |
| 5 | `not_duplicate` | Tracker query for same identity / company+title-family with applied-class status other than this application | `PREFLIGHT_FAILED` |
| 6 | `resume_hash_matches_approved` | sha256 of PDF on disk == `decisions.artefact_hashes.pdf` | `PREFLIGHT_FAILED` |
| 7 | `no_fabrication` | `fact_checks` row with status pass/pass_with_confirmed_edits for exactly these hashes | `PREFLIGHT_FAILED` |
| 8 | `letter_tailored` | Letter present iff form has letter field; hash matches approved | `PREFLIGHT_FAILED` |
| 9 | `answers_accurate` | Answers hash matches approved; every route resolvable now **and resolving to a value whose `answer_sheet.status` is `decided` or `learned` — `unconfirmed` or `open` is a hard fail (C-7)** | `PREFLIGHT_FAILED` |
| 10 | `contact_correct` | Profile fields to be filled equal §2 constants | `PREFLIGHT_FAILED` |
| 11 | `location_acceptable` | Eligibility rules 10–12 recomputed from stored facts + current settings | `PREFLIGHT_FAILED` |
| 12 | `no_false_mandatory_claim` | C13 recomputed against the job's `mandatory` list | `PREFLIGHT_FAILED` |
| 13 | `no_unconfirmed_fabrication` | **C3, C4 and C7 recomputed from the artefacts, independently of `fact_checks.status` (M-16).** Any C4 or C7 violation is a hard fail — those classes are never overridable. A C3 violation passes only if a `confirmations` row exists for its `violation_id` | `PREFLIGHT_FAILED` |

**Why #13 exists (M-16).** Check #7 accepts `pass_with_confirmed_edits` wholesale, and v1's #12
was the *only* class recomputed at the gate. That was correct for T-3 and silently insufficient for
T-1: a confirmed edit carrying an invented metric, a canary technology or a false years figure
passed #7 and was never re-examined. #13 recomputes the three T-1 classes from the artefacts
themselves, so the gate no longer trusts a status that a human could have waived. Together #12 and
#13 mean the two absolute requirements — *never claim a qualification you lack*, *never invent
technologies or years* — are both re-derived immediately before the irreversible act, not inherited
from an earlier decision.

All 13 rows are stored with evidence (AC-SB-01). Pre-flight runs immediately before `fill_form`
(`fill_form` and `submit` follow; the browser worker queue is FIFO).

**An unverifiable posting is a red, not an amber (C-4).** v1's closing rule was: *"Check 3 that
cannot reach the posting (network) is recorded `unverified` and shown amber; approval is still
allowed with the warning."* That ruling was withdrawn in v2, for two reasons.

*It was temporally impossible as written.* Pre-flight runs **after** approval, immediately before
`fill_form` — the section title says so. At that moment there is no approval left to permit;
"approval is still allowed with the warning" described a UI state that had already passed. What the
rule actually authorised was **the click, with nobody asked** — which is the one thing FR-9.1 exists
to prevent.

*The carve-out was unreachable in the case it was written for.* Checks #1 (`company_match`) and #2
(`job_match`) depend on the same live re-fetch and have no `unverified` path, so a network failure
fails at #1 and never reaches #3's amber branch. The amber branch could only fire when the fetch
*partially* succeeded — a login wall, an error page, a redirect — which is the case where submitting
is *least* defensible, not most.

**v2 rule.** An unverifiable #3 records `still_active_unverified` and hard-fails to
`PREFLIGHT_FAILED`. The application is retryable from the dashboard the moment connectivity
returns; nothing is lost but time. Checks #1 and #2 keep their existing hard-fail semantics, so all
three re-fetch checks now behave alike. **No DEPARTURE id is required, because v2 no longer departs
from FR-9.1** — v1's carve-out did, and was untagged.

**Pre-flight is also rendered as a preview before Approve** (`phase='preview'` rows), so the
reviewer sees the same twelve checks while he still has a decision to make; the authoritative run
after approval is `phase='gate'`. The preview is advisory and never authorises anything.

### 9.5 `UNKNOWN_OUTCOME` resolution

The `await_unknown` node holds the thread. Telegram + dashboard show the job link, the last
screenshot, the exact timestamps of `submitting_written_at` and `click_dispatched_at`, and the
instruction "check the ATS / your inbox for a confirmation". Meanwhile dedup treats the job as
applied (§4.3 rule 4). Resolution:

- `confirmed_submitted` → `SUBMITTED` with `confirmation_kind=human`; evidence row records the
  human confirmation (AC-ID-04 second branch). Available immediately.
- `check_again_later` → the thread stays at `await_unknown`; a reminder is re-queued. Available
  immediately.
- `confirmed_not_submitted` → `APPROVED` with `submit_attempt+1` → `preflight` → `fill_form` →
  `submit`, whose gate (1) now sees `PREFLIGHT_OK` and may click exactly once.

**The `confirmed_not_submitted` branch carries real friction (C-3).** §9.2 is explicit that this is
the *only* route from a dispatched click back to another click, and gating it on a human is right.
v1 then gave that decision no friction at all: **one click**, while editing a single sentence of a
cover letter required typing *"I confirm this statement is true"* (§7.4, AC-AF-19 — a constant that
v2.2 has since replaced with a generated, claim-specific string, M-16). The friction
gradient was inverted — the cheaper action was the irreversible one. Worse, the human was asked
"did it land?" at the moment the evidence could not yet exist, since an ATS confirmation email
routinely lags the POST by minutes, and "I don't see it" is the honest answer that produces the
wrong outcome. v2 requires **all four** of:

1. **A typed confirmation naming the employer** — `NOT SUBMITTED TO <company>` — stored in
   `decisions.confirmation_text` (the column already exists, §6.3).
2. **A minimum elapsed time from `click_dispatched_at` before the option is even enabled** —
   default **60 minutes**, configurable, never zero. `confirmed_submitted` and `check_again_later`
   stay available immediately; only the dangerous branch waits. Attempting it early returns `409`.
3. **An explicit checkbox** — *"I checked the ATS account and the application is not there"* —
   recorded on the decision row (`checked_ats_account`).
4. **The consequence stated where the decision is made**, in the dashboard card and in the Telegram
   message, not only in §9.1's prose: *"If you are wrong, this employer receives a second
   application under your name, and there is no unsend."*

The trigger is also tuned down: evidence capture rises from 60 s to 180 s (§9.3), because a slow
ATS confirmation page was producing `UNKNOWN_OUTCOME` with `detail="no confirmation signal"` on
applications that had in fact succeeded — manufacturing the very condition this branch resolves.

There is no auto-resolution and no timeout on `UNKNOWN_OUTCOME`.

### 9.6 Startup reconciliation (crash recovery)

**Order matters, and v1 had it wrong (C-10).** v1 ran reconciliation *before* the FastAPI bind, so
a second instance executed every step below and only afterwards failed on `EADDRINUSE`. In those
seconds it stole the run lock and aborted the live run, **transitioned every `SUBMITTING` row to
`UNKNOWN_OUTCOME` and fired the notification** — including a row belonging to a click the first
process had dispatched four seconds earlier and was still capturing evidence for — and opened a
second Playwright context on the same profile directory. The human was then told "we don't know if
this was submitted; check the ATS" about an application that *was* submitted and whose confirmation
had not yet arrived. He checks, sees nothing, and clicks `confirmed_not_submitted`; in v1 that was
one click with no confirmation text, no waiting period and no warning. This is the double-submission
path the design missed — not a retry it forgot to guard, but a **manufactured `UNKNOWN_OUTCOME`
feeding the one gate permitted to click twice**. v1's only defence, §9.6 step 5, could not work:
SQLite in WAL mode (§6.1) is designed to permit concurrent multi-process access, so "not locked by
another process" does not detect a second instance.

On `jobagent serve` start, in this order:

0. **Acquire the named single-instance mutex** (§3.2). Held ⇒ print the holding pid and exit
   non-zero. Nothing below has run; no record has been touched.
1. **Bind `127.0.0.1:8765`** — a backstop if the mutex ever fails — but do not serve requests yet.
   Only now does reconciliation begin.
2. Acquire `locks.run` if stale (heartbeat older than 5 min) **and the holder pid is not alive** →
   mark the previous run `aborted`, mark its audit rows `run_aborted`.
3. For every application with status `SUBMITTING`, transition to `UNKNOWN_OUTCOME`
   (detail `process_died_during_submit`) and enqueue the notification **only if both**: the
   `locks` holder pid is not alive, **and** `submitting_written_at` is older than the `submit` node
   timeout (300 s). A row younger than that belongs to a click that may still be in flight in a
   living process; leave it alone. The graph thread, when resumed, hits gate (1) and lands in
   `await_unknown` — so nothing is lost by waiting.
4. For every application with status `FILLING` (C-1): consult `page_commits` for the highest
   committed `page_index` and resume `fill_form` **after** it; never re-post a committed page.
5. For every application with a non-terminal status: `snapshot = await graph.aget_state(config)`.
   If a task has pending `interrupts` → nothing to do (dashboard shows it). Else if
   `snapshot.next` non-empty → `ainvoke(None, config, durability="sync")` under the thread lock
   (bounded concurrency; browser-dependent nodes queue on the worker).
6. `APPROVED_GRACE` rows older than the grace window → treated as approved: resume.
7. Verify the checkpointer file is writable and not corrupt; refuse to start otherwise (AC-FM-14).
   This is a corruption check, **not** an instance check — step 0 is the instance check.
8. Start serving on the already-bound socket.

**AC-ID-08 is extended (C-10):** the second process must refuse to start at all, and must be shown
to have written no row — not merely to have lost the thread lock.

### 9.7 Assisted mode (Workday)

`fill_form` opens the tenant page, uploads the PDF, pre-fills every mappable field, and stops at
the first account/verification step or unmappable required field → `notify_handoff` →
`await_handoff`. Avadh completes and clicks submit in the visible browser. On the dashboard he
records `i_submitted` (→ `SUBMITTED`, `confirmation_kind=human`, evidence = his statement +
screenshot) or `by_hand`/`abandon`. The agent never clicks in assisted mode (AC-SB-13). HITL-1
is satisfied by the earlier approval; the human click is the submission.

### 9.8 Multi-page forms: the per-page commit protocol (C-1)

`fill_form` advances multi-page ATS forms, and each advance is an HTTP POST that can create a
server-side draft or partial application. That is an irreversible act outside v1's protocol. v2
gives it the same discipline as the final click, one level down.

```python
async def commit_page(state, page, page_index: int, tr, bw) -> None:
    if page_index in state["pages_committed"]:
        return                                     # replay after resume: never re-post (§9.6 step 4)
    if not runtime.context.settings.submission_enabled:
        raise SubmissionDisabled(state["application_id"])          # C-11, second check point
    await tr.record_page_commit(state["application_id"], attempt=app.submit_attempt,
                                page_index=page_index, url_hash=sha256(page.url))   # durable BEFORE the POST
    await bw.commit_page(page, page_index)         # the POST
```

The rules, mirroring §9.3 exactly:

1. **`FILLING` is written before browser work begins**, and the durable `page_commits` row is
   written **before** each page-advancing POST — the same "record then act" ordering as
   `SUBMITTING` before the click (§9.3 step 3). `page_commits` has a composite primary key, so a
   replay collides at the database rather than at the ATS (§6.4).
2. **`fill_form` retries at most once — `RetryPolicy(max_attempts=1)`.** Under v1's inherited
   `max_attempts=3`, one node attempt could re-issue a page-advancing POST three times.
3. **`fill_error_handler` may never re-enter a page the tracker records as committed.** It resumes
   after the highest committed index, or routes to `NEEDS_ATTENTION` if the page identity no longer
   matches.
4. **The "no POST" claim is deleted** from §5.3 and §13.6 and replaced by the real invariant:
   *no POST to a page the tracker records as already committed.*
5. **`submission_enabled` is checked here too** (C-11), because after this finding the final click
   is no longer the only way to reach an employer.

**Test changes.** The fake ATS (T-2.5) becomes a **multi-page** form with a per-page POST counter.
AC-ID-23's 200-run kill fuzz is extended to kill **between pages**, asserting every per-page counter
is ≤ 1 — the same assertion the suite already makes for the final submit.

---

## 10. Tailoring contract (diff-friendly by construction)

### 10.1 The constraint

HITL-5 is a full review of 10–20 tailored resumes a day at ~60 s each. If tailoring rewrites
sections, the diff is the page and the review degrades into rubber-stamping (UI P-1). FR-6.1
permits "improving wording" broadly; this spec **narrows** it (analysis §4 hard/hint table and UI
§9 handoff both ask for this):

> **Reorder over rewrite. Rewrite only the professional summary. Skills and bullets may be
> reordered and re-emphasised, never re-authored.**

### 10.2 Allowed operations (and only these)

| Op | Target | Constraint | Diff class |
| --- | --- | --- | --- |
| Reorder skill lines | `skills.s1..s7` | permutation | `~↑↓` |
| Reorder values within a skill line | `skills.sN.v*` | permutation; the bold label stays first | `~↑↓` |
| Reorder bullets within one `<ul>` | `exp.krista.li*`, `proj.mcp.li*` | permutation within the same list | `~↑↓` |
| Reorder project blocks | `proj.mcp`, `proj.aiqa`, `proj.grc` (h3 + ul as a unit) | permutation | `~↑↓` |
| Emphasise | any `li` / skill value | wrap an **existing** contiguous phrase in `<b>`; ≤ 3 per tailoring; no text change | `~b` |
| Rewrite summary | `summary.p1` only | ≤ 4 sentences, ≤ 70 words; every sentence carries ≥ 1 provenance key; passes FactGuard C3–C10 | `−/+` |

Not allowed by the plan schema: any new `<li>`, `<h3>`, skill line or skill value; any text
change inside a bullet; removal of anything (**DEPARTURE D-2**: AC-AF-06 *permits* removal of an
`<li>`; the generator is not given the operation because removal is a one-page-layout risk and
adds review load; the checker still follows AC-AF-06 exactly, so hand-made legitimate tailorings
with removals pass AC-AF-16). Header, experience heading/meta, education, awards, contact and
`<style>` are immutable (FactGuard C2).

### 10.3 Generation is a plan, not a document

The `generate` model receives: the ledger (facts with element keys and text), the JD text with
span offsets, the score's `key_matching_skills`, `gaps` and `differentiator_hits`, and the
schema. It returns a `TailoringPlan` (§4.8) via `with_structured_output(TailoringPlan)`:

```json
{
  "skill_line_order": ["skills.s1","skills.s2","skills.s3","skills.s7","skills.s5","skills.s4","skills.s6"],
  "skill_value_order": {"skills.s1": ["skills.s1.v3","skills.s1.v5","skills.s1.v1", "..."]},
  "bullet_order": {"exp.krista": ["exp.krista.li2","exp.krista.li1","exp.krista.li3","exp.krista.li4"]},
  "emphasise": [{"element_key": "exp.krista.li2", "phrase": "governed MCP server"}],
  "summary": {"sentences": [
     {"text": "Senior AI Solution Engineer with 4+ years delivering production GenAI for enterprise customers end-to-end - requirements to production support.", "provenance": ["hdr.tag","exp.krista.li3"]},
     {"text": "Built a governed MCP server over MCP JSON-RPC 2.0 that lets Claude, ChatGPT and Cursor call enterprise tools.", "provenance": ["proj.mcp.li1"]}
  ]},
  "rationale": "JD leads with FDE lifecycle ownership and MCP/tool-calling."
}
```
Pydantic validators reject: unknown keys; non-permutations; `emphasise.phrase` not found verbatim
in the element; summary over budget; sentences without provenance. `apply_plan` performs the DOM
edits deterministically; the LLM never sees or writes HTML. The rendered `<style>` is copied from
the master byte-for-byte.

**Change budget.** `apply_plan` counts change units (each moved element = 1, each emphasis = 1,
summary rewrite = 1 per changed sentence). The plan is accepted when units ≤ 12; the UI shows the
heavy-rewrite banner at > 40 changes (UI §4) which can then only happen through Avadh's own edits.

### 10.4 Minimal-diff diffing

`structural_diff(master, tailored)` produces the reviewer's change list from element keys, not
from text diffing: moved elements (`~↑↓` with from/to index), emphasis toggles, and the summary as
a sentence-level `−/+`. Unchanged elements collapse to `·`. This is the same computation
FactGuard C1 uses, so "what the reviewer sees" and "what the verifier checked" are one artefact
(`GET /applications/{id}/diff`).

### 10.5 When there is no upload

Forms without a resume upload use the **master PDF** (`resume_version = master PDF hash`, note
`upload_not_supported`); letters and answers are still generated (AC-RT-12). Documents-only
threads (D-3) tailor normally so the by-hand download is useful.

### 10.6 Master changes

`load` compares `master_hash` with the on-disk master. If the master changed while applications
are pending, the application is flagged `MASTER_CHANGED`; the UI banner offers "Re-tailor all
≈ $x" (UI §5.3).

**The master is snapshotted, not cached (C-8).** v1 said "the ledger is rebuilt per `master_hash`
and cached" — but §6.3 defined no table for ledgers and no artefact kind for a master snapshot, and
a cache is not a record. The moment the master changed, no historical application's provenance could
be re-resolved and `GET /applications/{id}/bundle` could not satisfy NFR-3. v2: on first use of any
`master_hash`, the **full master bytes** are written as an artefact with `kind='master_html'` and a
row is inserted into `ledgers` (§6.3). Both are kept forever — §6.5 already keeps records forever;
this is the record that makes the others meaningful. Provenance for an application is always
resolved against the ledger row for *that application's* `master_hash`, never against the current
file on disk.

**And the bundle carries them (M-19).** C-8 made the master and ledger durable; M-19 is the
separate requirement that NFR-3 reconstruction actually *includes* them. `GET /applications/{id}/bundle`
therefore ships the `master_html` artefact and the `ledgers` row alongside the documents (§7.1).
**AC (new, RT or AF group):** edit the master, then export a bundle for an application tailored
before the edit, and assert every provenance pointer in the archived letter still resolves — from
the bundle alone, with no access to the live master.

---

## 11. Form filling, the answer sheet and `years_by_technology`

### 11.1 Principle

Two independent guarantees:
1. **Answer-sheet values never enter an LLM prompt** — enforced by data placement (values live
   only in `answer_sheet`, are read only by `FormFiller.fill_value`, are never put in graph
   state, artefacts, logs, notifications or exports) and
   by `PromptGuard` scanning every outbound prompt (AC-NF-04/05, AC-CL-10/11). **This is masking
   *in transit*, and it is not masking from the reviewer — see §11.7 (C-7).**
2. **Numbers about experience are never generated** — total years is computed from resume
   dates; per-technology years come only from `years_by_technology`; anything else halts
   (AC-AF-10/11, AC-CL-06..08).

### 11.2 Field routing (deterministic first)

`route(field, sheet_keys)` normalises the label (lowercase, strip punctuation, collapse
whitespace, expand common abbreviations) and matches, in order:

| Route | Match (label ontology, `config/field_ontology.yaml`) | Value source | LLM? |
| --- | --- | --- | --- |
| `credential_refuse` | `type=password`, or label ∋ {password, passcode} | — → HITL-3 with `credential_field_in_form`, guard event | no |
| `otp_refuse` | label ∋ {otp, one-time, verification code} | — → HITL-2 | no |
| `sensitive_refuse` | label ∋ {bank, ifsc, account number, pan, aadhaar, passport, card} | — → HITL-3 with warning, guard event (AC-FD-10) | no |
| `profile:<field>` | name, email, phone, linkedin, github, city/location, current company, current title | §2 constants from the ledger | no |
| `years_total` | {total, overall, professional} × {years, experience} | `floor(years since 2022-08-01)` as integer; source `resume:dates` | no |
| `years_tech:<tech>` | `years … with|in|of <tech>`; tech resolved via synonym table | `years_by_technology[tech]` exactly; missing → **HITL-3** with the field name (AC-AF-11) | no |
| `answer_sheet:<key>` | current ctc, expected ctc / salary, notice period, relocation, start date, work authorisation, sponsorship, plus any `learned` key by normalised label | `answer_sheet[key]` formatted by `field.kind` (§11.3) | no |
| `eeo_decline` | gender, race/ethnicity, veteran, disability, pronouns | select the "decline to self-identify / prefer not to say" option if present; else HITL-3 (AC-CL-14/15) | no |
| `resume_upload`, `cover_letter` | file inputs / long text with cover-letter label | artefacts | no |
| `subjective` | why company / why fit / describe / tell us / what interests | `SubjectiveAnswer` via `generate`, FactGuarded | yes (claims only) |
| `unknown` | none of the above | `screen` model classifies the **label text only** into one of the routes above or `unknown`; `unknown` → HITL-3 with question text (AC-HL-14) | label only |

`FormModel.supported_ratio = mapped_required / total_required`; below 0.9 → `unsupported_form`
fallback (AC-SB-14). The HITL-R3 target (< 10% of forms halt, AC-HL-17) is measured on the
fixture corpus per release.

### 11.3 Answer-sheet formatting (deterministic)

| Key | Kind | Formats produced on demand |
| --- | --- | --- |
| `current_ctc`, `expected_ctc` | `currency_inr` | `19.8 LPA`, `₹19,80,000`, `1980000`, `19.8 Lakhs` — chosen by field hints (placeholder, pattern, options); non-INR currency asked → **HITL-3**, never converted (AC-CL-12, G-M10) |
| `notice_period` | `months` | `1 month`, `30 days`, earliest start = today + 30 (AC-CL-13, G-M9) |
| `work_authorisation` | `enum` | configured string verbatim; sponsorship question answered from the same setting (AC-CL-16) |
| `relocation_stance`, `preferred_start_date` | open (O-2) | HITL-3 until filled (AC-CL-17) |
| learned keys (`employment_termination`, …) | `text` | verbatim |

### 11.4 HITL-3 and learning

`await_question` payload: `[{field_id, label, field_type, max_len, options}]` — question text only.
The dashboard card (UI §3.19) offers "Save to answer sheet as `<key>`" (default on). The answer is
written to `answer_sheet` with `status=learned`, and the label's normalised form is added to that
key's alias list so the next form with the same label does not interrupt (AC-HL-15).

**Learned values are verified and re-shown (C-7).** A `learned` answer is free text written once by
a human — the schema's own example is `employment_termination` — and v1 then sent it to every
employer whose form asked a similarly-worded question, **never re-shown, never re-reviewed, and
never passed through FactGuard**, which runs only on "tailored HTML, letter claims, subjective
answers, any edited version" (§8.1). That is a statement to an employer that no control in the
system ever inspected. v2:

- Every `learned` value is passed through FactGuard checks **C3, C4, C6, C7 and C13 on write**, and
  a failure blocks the save with the violation shown, exactly as an edit would.
- A `learned` value is included in the reviewed artefact set for the **first three reuses**
  (`used_count` already exists in §6.3), after which it is shown on the Answers tab like any other
  value (§11.7) but no longer forced into the diff.

### 11.5 `years_by_technology` (FR-8.1 restated)

**DEPARTURE D-7 (challenge to FR-8.1 as written).** FR-8.1 asks the agent to auto-answer years
of experience with AI / RAG / LLMs / Python / MCP / LangChain / enterprise AI. The resume carries
only "4+ years" total and one dated role; any per-technology figure would be invented (T-1).
Restated: *auto-answer questions whose answer is on the resume or the answer sheet; total years
from resume dates; per-technology years only from `years_by_technology`, filled once by Avadh;
absent an entry → HITL-3.* The Settings › Answer sheet screen carries the table; the halt card
offers "add to years table" for a `years_tech` halt. No LLM is ever asked for a number in this
category (C7 in FactGuard is the backstop).

### 11.6 Fill-time isolation

```
fill_form node ─▶ FormFiller.plan(answers routes) ─▶ for route in plan:
                     value = resolve(route)            # answer_sheet read happens HERE, in process memory only
                     await browser.type(field, value)  # value goes to the form and nowhere else
                     record answers.filled=True         # no value written
```
`PromptGuard` holds the current answer-sheet values in memory for scanning; they are refreshed on
each settings change. The E2E proxy scan (AC-NF-04) and the log/trace scan (AC-NF-05) are the
external proofs; CTC may appear in exactly one place outside the form itself — the encrypted
`form_payload` blob of the submission evidence, masked in the UI.

### 11.7 What the reviewer sees (C-7)

HITL-5 is *"full review, no spot-checking"* — the requirement the safety of this system rests on.
v1's review screen made a whole class of statements-to-employers structurally invisible to the
person certifying them: answer-sheet routes rendered as the **field name only**, and seeing a value
required a per-field transient keypress (`Ctrl+Shift+V`) that was separately audited as a sensitive
action. Current CTC, expected CTC, notice period, work authorisation and sponsorship all reach the
employer as literal text; all rendered as a label.

The cause was a conflict the spec never named. §2.1's privacy control and HITL-5's review control
pulled in opposite directions, and v1 resolved it silently in favour of privacy. But **the threat
model behind §2.1 is LLM providers, traces, logs and notifications. The reviewer is not that
threat** — he is the author of the values and the person accountable for them.

**v2 rule: masked in transit, never masked from the reviewer.**

| Surface | Values |
| --- | --- |
| Review screen, Answers tab (loopback session) | **Rendered in full**, every value that will be typed into the form. No keypress. This is the one surface the answer sheet exists to serve |
| LLM prompts, traces, logs, Telegram, exports, tracker, screenshots | Masked, exactly as v1 — unchanged, and still proved by the proxy and log scans |
| Settings › Answer sheet | Masked by default with an audited reveal (unchanged — that screen is for editing, not certifying) |

Consequences: **AC-HL-19 is amended** to require the Answers tab to show values rather than
sources, and a new AC asserts that a `learned` value appears in the reviewed artefact set.
Pre-flight #9 additionally fails when any route resolves to a value whose `status` is `unconfirmed`
or `open` (§9.4) — v1 checked only that the key still existed, so an `unconfirmed`
work-authorisation string, which is a statement about visa status, could be sent unreviewed.

---

## 12. Security, secrets and privacy

### 12.1 Secrets

| Secret | Source | Handling |
| --- | --- | --- |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | Windows **user** registry environment scope (`HKCU\Environment`), read at process start via `winreg` (the memory note: the session env goes stale — always read the registry) | Held in process memory; passed to `init_chat_model` via env; never logged; `PromptGuard` and log filters scrub `sk-`, `sk-ant-` patterns (AC-FD-12, AC-NF-05) |
| `TELEGRAM_BOT_TOKEN` | same | same; never in outbox payloads |
| Answer-sheet values | `answer_sheet.value_enc` | AES-GCM with a key derived from a random secret stored in `HKCU\Software\JobAgent\dek` (created on first run); decrypted only in `FormFiller` and the reveal endpoint. **[UNVERIFIED — cryptography library choice outside the knowledge base; `cryptography` package is the standard choice.]** |
| Browser profile | `data_dir/browser-profile/` | git-ignored, excluded from export; contains ATS session cookies |

Repository: `.gitignore` covers `.env`, `data/`, `browser-profile/`; a pre-commit secret scan
(AC-NF-06). No secret is ever a form value (FR-5.2): `FormFiller` refuses any value matching a
secret pattern regardless of route.

### 12.2 Network

- Backend binds `127.0.0.1` only; a LAN port scan finds nothing (AC-UI-12). Telegram deep links
  use `settings.telegram.base_url` (UI §7 "localhost problem") — changing it does **not** change
  the bind address; exposing the dashboard is a manual, documented step (reverse proxy /
  Tailscale) outside v1.
- Outbound allowlist enforced in `PacedClient` and the LLM client: configured provider hosts,
  configured source domains + watchlist domains, `api.telegram.org`. Anything else raises
  `OutboundDenied` (AC-NF-03). No CAPTCHA-solver, no hosted tracer unless `hosted_tracing=true`.
- CSRF token on mutating API calls; `Origin` must be `http://127.0.0.1:8765`.

### 12.3 Privacy (NFR-7)

- Resume text and JDs go to the configured LLM providers — this is the accepted third-party
  disclosure (analysis §1.5 NFR-7); it is listed on Settings › Data & secrets.
- Answer-sheet values go only to application forms (§11).
- Traces are local; prompts in `traces/*.jsonl` pass through the same scrubber; the DB stores
  prompt hashes, not prompts.
- Telegram messages carry counts, company names, roles, scores and links — never CTC, never
  answers, never secrets (allowlisted template variables).
- Export (`POST /data/export`) excludes the browser profile and decrypts nothing; the answer
  sheet is exported masked unless `include_answer_sheet=true` is passed explicitly.

### 12.4 Authorisation of decisions

Only two principals may decide: the dashboard session (loopback + CSRF) and the configured
Telegram `chat_id`. Every decision row stores the principal (AC-HL-27). A decision on a
non-pending interrupt is refused; a replayed decision returns `already_decided` (AC-NF-18).

### 12.5 Guard rails that are code, not prompts

| Rule | Enforcement |
| --- | --- |
| HITL-1 / HITL-5 cannot be disabled | No setting, flag or env var exists — **true as of v2.3, and it was not true before (M-13)**: v1 shipped `telegram.approve_enabled`, which let `/approve` record `approved_without_review` with no diff, no evidence trace, no pre-flight preview and no artefact hashes. That is HITL-5 disabled by a setting, for that application, and §12.5 asserted the opposite *in the section whose purpose is to enumerate guarantees that are code rather than prose*. The command and the flag are removed rather than documented, which is the only version of this row that is worth having. `record_decision` requires a `decisions` row; the graph has no edge from `notify_review_ready` to `preflight` (AC-HL-26) |
| Approval requires the evidence to have been rendered (M-22) | `POST /decisions {approve}` returns `409 tabs_unreviewed` unless every tab with content for this application has been opened; the tab set is recorded on the decision row |
| Discovery-only sources never submit | `SourceAdapter.policy` is a class attribute; `selection` never creates a submitting application for `discovery_only`; `submit` refuses if `applications.channel` is not in `{greenhouse, lever, career_page}` (AC-SB-15) |
| No bulk approve | No endpoint accepts a list of approvals; the UI has no control (UI D-6) |
| Hard rejections have no override | `POST /jobs/{id}/promote` returns `409` for `reason_enum` in the FR-4.1/4.2/5.1 sets |
| **A fresh install cannot submit (C-11)** | `settings.submission_enabled` defaults `False`; checked in `submit` gate (0) and in `commit_page` (§9.8); enabling requires a typed confirmation and writes an `audit_events` row; static check asserts the default literal |
| **No model call escapes the guards (C-5)** | `GuardedModel` has no `.inner`; `.inner` and `init_chat_model` are both on the static-check ban list outside `llm/`; the mapper agent carries `GuardMiddleware` inside its loop |
| **No POST to an already-committed page (C-1)** | `page_commits` composite primary key + `RetryPolicy(max_attempts=1)` on `fill_form` + `fill_error_handler` that resumes only after the highest committed page |
| **Only one process (C-10)** | Named OS mutex acquired before any database connection; port bind before reconciliation; reconciliation's `SUBMITTING` sweep additionally requires a dead holder pid and an aged `submitting_written_at` |

---
## 13. Operations

### 13.1 Scheduling (FR-12.1, Q-6, A-19, G-I1)

| Element | Design |
| --- | --- |
| Service start | Windows Task Scheduler task `JobAgent` → `jobagent serve` at user logon, restart on failure. The dashboard, Telegram and approvals need the process alive all day, so the *service* is what Task Scheduler owns, not the run. **"Restart on failure" is exactly why the single-instance mutex is mandatory (C-10): a hung-but-alive process plus a scheduled restart is an ordinary Windows event, and it is the everyday path to two live instances.** The task is configured `IfRunningRule=IgnoreNew` as a second line of defence; the mutex is the first. |
| Daily run | In-process scheduler fires `run(trigger="scheduled")` at `settings.schedule.run_at` (09:00 Asia/Kolkata). |
| Missed run | On service start and every 10 min, if today's run has not started and now < `catch_up_until` (20:00 IST) → `run(trigger="catch_up")` (AC-TK-07); if ≥ 20:00 → `runs` row `missed`, Telegram M8 (AC-TK-08). At 09:15 with no run started (machine awake but blocked) → M8 as well. |
| Evening digest | 21:00 IST: `reports(kind=evening)` — approved / edited / rejected (with reasons) / submitted / unknown-outcome counts; Telegram M5 (AC-TK-05). |
| Stale approvals | Every `telegram.stale_hours` (48 h) with pending items → M9. |
| Retention | 03:00 daily (§6.5). |
| Follow-ups | Applications with `follow_up_date ≤ today` and outcome `none` appear in the morning report attention list; no outreach (AC-TK-13). |
| Spend day | Calendar day in IST for `spend_ledger.day_ist`; a run crossing midnight splits accordingly (AC-FM-17). |

### 13.2 Run lock and thread locks (G-C4)

```
acquire(run):     INSERT OR FAIL locks(name='run', holder=pid:uuid, acquired_at, heartbeat_at, expires_at=now+10min)
                  on conflict: if expires_at < now → UPDATE ... WHERE name='run' AND expires_at < now (steal, log rescue_event) else 409 lock_held
heartbeat:        every 60 s UPDATE expires_at=now+10min WHERE holder=me
release:          DELETE WHERE name='run' AND holder=me
thread lock:      same table, name='thread:<application_id>', held only for the duration of one ainvoke
```
A second `run` trigger (scheduled while manual is running) → `runs` row `skipped_lock_held`, audit
row (AC-ID-15, AC-TK-09). Two resumes of one thread → one acquires, the other returns `423`
without touching the graph (AC-ID-08). Discovery threads and application threads never share a
lock, so a pending approval never blocks discovery (AC-TK-12).

### 13.3 Budget enforcement (Q-8, TR-11, TR-12, A-15, G-C7)

```
per call:   BudgetGate.check(stage)
              total = SUM(spend_ledger.usd WHERE day_ist = today)
              if total ≥ ceiling_usd (100):        raise BudgetHardStop("ceiling")      # absolute
              if total ≥ hard_stop_usd (20):       raise BudgetHardStop("hard_stop")
              if total ≥ soft_alert_usd (5) and not alerted_today: outbox M7; header amber
after call: SpendLedger.record(usage_metadata × prices)
```
Behaviour on `BudgetHardStop`: the raising node's `error_handler` stores `resume_target=<node>`
and routes to `await_pause` (application graph) or marks remaining jobs `paused_budget`
(discovery). In-flight nodes finish; approvals, pre-flight, fill and submit make no LLM call and
continue to work (AC-FM-09). At 00:00 IST the scheduler resumes `await_pause` threads with
`Command(resume="continue")`. Settings validation: `soft < hard ≤ ceiling ≤ 100` (AC-FM-10).
Alerts fire once per day per level (M7 again at $25 and $50 per UI §7.1).

### 13.4 Global pause (G-I11, A-24)

`POST /control/pause` or Telegram `/pause` sets `settings.paused=true` and calls
`request_drain("user_pause")` on every live `RunControl`. `BudgetGate.check` and
`BrowserWorker` refuse new work while paused (`PauseRequested`). `GraphDrained` is caught by the
supervisor; threads resume on `/resume` via `ainvoke(None, config)` (AC-HL-25).

### 13.5 Observability (TR-7, NFR-6)

**Confirmed-override counter (M-16).** The evening digest and the weekly summary carry a rolling
count of `confirmations` rows by `check_name` over 7 days. A confirmation is a legitimate act — the
human overruling a judge about his own wording — but a *rate* of them is diagnostic: several C9/C10
overrides a week means the generator or the entailment judge is miscalibrated, and several C3
overrides means numbers are being asserted that the résumé does not carry. Neither is visible from
a per-application view, which is why it is a report rather than a flag.

| Signal | Store | Surface |
| --- | --- | --- |
| LLM calls (model, stage, tokens, usd, latency, thread, node) | `llm_calls` + `spend_ledger` | Run console per stage; Job detail "scored by / cost"; header meter |
| Tool calls (browser steps, source requests) | `tool_calls` | Run console live step; traces |
| State transitions | `transitions` | Job detail timeline; tracker expansion |
| Node events | `traces/YYYY-MM-DD.jsonl` (redacted) | `GET /traces/{thread_id}` |
| Guard events, HITL decisions, rescues | `audit_events` | Guard-events panel; Reports |
| Health | `GET /status` | Header dot; missed-run banner |

`rescue_events` (G-I12): any transition `by='reconcile'`, any lock steal, any `NEEDS_ATTENTION`,
any manual DB edit detected by the settings/history checksum. Reported weekly from month 2
(AC-NF-17).

### 13.6 Failure-mode behaviour (test plan §14)

| Failure | Behaviour |
| --- | --- |
| One source down / 429 / 403 | Isolated; `source_failed` / `rate_limited` 24 h; run continues (FM-01/02) |
| Provider 429/5xx on one call | Retry with back-off; then `evaluation_failed` for that job (FM-03) |
| Provider down all run | Discovery + audit complete; all `evaluation_failed`; report says so; nothing queued (FM-04) |
| Network lost mid fill | `PreClickError`; thread resumes at `fill_form` **after the highest `page_commits` index — no POST to an already-committed page** (FM-05, C-1). The v1 wording "no POST" was false for multi-page forms |
| Second instance started | Refuses at the mutex before touching any record; no `SUBMITTING` row is disturbed (C-10, AC-ID-08) |
| `submission_enabled` false | `submit` and `commit_page` raise `SubmissionDisabled`; `NEEDS_ATTENTION`; guard event; documents-only threads unaffected (C-11) |
| Disk full on tracker write | Transaction rolls back (SQLite atomic); run aborts `disk_full`; Telegram; no submission (FM-06) |
| Disk full on checkpoint write | Graph fails loudly; last complete checkpoint intact; resumable (FM-07) |
| `render.py` fails | `TAILORING_FAILED`; others unaffected (FM-12) |
| Browser crash | `NEEDS_ATTENTION`; worker restarts for next application (FM-13) |
| Checkpointer locked/corrupt at start | Refuse to start (FM-14) |
| Telegram unreachable | Outbox retries with back-off; dashboard unaffected; no duplicates (FM-11) |
| Run killed mid-discovery | New `run_id` on re-run; aborted rows marked; dedup prevents duplicates (FM-16, DS-14) |

### 13.7 Test harness hooks (test plan §0.2)

- **Fault injector**: `JOBAGENT_FAULT=<point>` env var read by `faults.maybe_kill(point)` at the
  named points (`after_approval_recorded`, `after_submitting_written`,
  `after_click_before_record`, `after_submitted_written`, `during_tailoring`,
  `during_discovery`); in production the function is a no-op. The harness runs `jobagent` in a
  subprocess and hard-kills it (`os._exit`) at the point.
- **Injectable clock**: all `now()` calls go through `jobagent.clock`, overridable in tests.
- **Fake ATS / boards**: `tests/fakes/` localhost servers with the fault modes of test plan §0.2.
- **Outbound proxy**: `HTTPS_PROXY` honoured by `PacedClient` and the LLM client in test mode.
- **Cassette LLM**: `GenericFakeChatModel` (`langchain_core.language_models.fake_chat_models`,
  verified in `test__unit-testing.md`) for U; recorded cassettes for I/E; live models for V.
- **Static checks**: `tests/static/` — interrupt rules (AC-ID-13/14), node topology (AC-ID-25),
  import lint (AC-NF-11, AC-ID-24), path length (AC-FM-19), `GuardedModel`-only model calls.

---

## 14. Frontend specification and FR → UI map

### 14.1 Stack and structure

Vite + React 18 + TypeScript; TanStack Query for data; SSE subscription for live invalidation;
`react-router` routes exactly as UI §2.1; keyboard handling via a single global key-map module
implementing UI §5.2; dark default, light supported; monospace for ids and diffs; no bulk
approve control anywhere (UI D-6). Served from `/` by FastAPI as static files; API under `/api/v1`.

### 14.2 Screen → route → data

| # | Screen (UI §) | Route | Primary data | Keys |
| --- | --- | --- | --- | --- |
| S1 | Today dashboard (3.2) | `/` | `GET /dashboard/today`, `/status` | `⏎` start review, `B`, `N` |
| S2 | Approval queue (3.3) | `/queue` | `GET /queue` | `J/K`, `⏎`, `X`, `Shift+R`, `Space` |
| S3 | Review — Resume diff (3.4) | `/queue/:appId` tab 1 | `/applications/{id}/review`, `/diff` | **`A` = Approve & stay** (M-22; the unshifted key does not navigate), **`Shift+A` = Approve & next**, `E`, `R`, `P`, `X`, **`Z` = undo the most recent in-grace decision, route-independent**, `1/2/3` tabs, `D`, `J/K`, `O`, `Shift+O`. Approve is refused — client-side and at the API — until every tab with content has been rendered |
| S4 | Review — Cover letter (3.5) | tab 2 | `/letter` (claims + provenance) | `Tab` cycles markers, `⏎` jumps |
| S5 | Review — Answers (3.6) | tab 3 | `/answers` — **every value shown in full** (C-7, §11.7) | — (the transient-reveal keypress is retired here; it survives only on S13) |
| S6 | Review — Edit mode (3.7) | tab n, `E` | `PUT /letter`, `/resume-text`, `/answers/{f}`, `POST /revise`, `/confirm-edit`; `GET /ledger` for live guard | `Ctrl+⏎`, `Esc` |
| S7 | Reject overlay (3.8) | overlay | `POST /decisions {reject, reason_code}` | `R`, `1–6`, `⏎` |
| S8 | Audit — Sources/Queries (3.9) | `/audit/:date/sources`, `/queries` | `/runs/{date}/sources`, `/queries`; retry | — |
| S9 | Audit — Jobs (3.10) | `/audit/:date/jobs` | `/runs/{date}/jobs?…` | `⏎`, `F`, `Space`, `Shift+X` |
| S10 | By hand (3.11) | `/by-hand` | `/fallback`; `POST /jobs/{id}/fallback-state`; downloads; `resume-with-agent`; `prepare-documents` | `M`, `S`, `⏎`, `O`, `Shift+S` |
| S11 | Tracker (3.12) | `/tracker` | `/applications?…`, `/applications/{id}`, `PATCH`, `/bundle`, CSV | `J/K`, `⏎`, `/` |
| S12 | Job detail (3.13) | `/jobs/:jobId` | `/jobs/{id}`; `promote` (soft only); `rescore` | — |
| S13 | Settings — Answer sheet (3.14) | `/settings/answers` | `/answer-sheet` (masked), `/reveal`, `PUT`, `/years-by-technology`, `/work-auth-impact` | `Ctrl+S` |
| S14 | Settings — Targets (3.15) | `/settings/targets` | `/settings` | `Ctrl+S` |
| S15 | Settings — Models & budget (3.15) | `/settings/models` | `/settings`, `/settings/models/usage-today` | `Ctrl+S` |
| S16 | Settings — Sources/Schedule/Notifications/Data (3.16) | `/settings/sources|schedule|notifications|data` | `/settings`, `/watchlist`, `/telegram/test`, `/data/*`, `POST /runs` | `Ctrl+S` |
| S17 | Reports (3.17) | `/reports/:date` | `/reports/{date}`, `/trend` | — |
| S18 | Run console (3.18) | `/runs/:date` | `/runs/{date}`, `/events`, `/traces`, `POST /runs` | — |
| S19 | Needs-you-now slide-over (3.19) | overlay | `/needs-you`; `hitl3`, `hitl4`, `blocker`, `take-over-browser`, `unknown-outcome`, `handoff` | `N`, `⏎`, `Ctrl+⏎`, `Esc` |
| — | Keyboard help / Command palette | overlays | — | `?`, `Ctrl+K` |

Approve is **disabled** when: any pre-flight preview row is red; `fact_checks.status` is not
pass/pass_with_confirmed_edits for the current version; any letter marker is unresolved; any
answer is halted; the application is `EXPIRED` (only `X` offered). The 5-second undo toast
implements `APPROVED_GRACE` (§7.2). All six UI states (empty/loading/error/partial/success/
overflow) per UI §4 are required for each component.

### 14.3 Telemetry the UI must record

`review_started_at` on opening a review; `review_seconds` on decision; **`tabs_reviewed` — which
tabs were actually rendered, and for how long (M-22)** → Reports "Your review today" (median time,
reject-reason distribution, UI §3.17) — the instrument for §9 "minutes not hours" and for detecting
rubber-stamping (AC-NF-15). Recording the tab set turns AC-NF-15 from a stopwatch into something
that can distinguish a fast reviewer from a reviewer who never opened the page where the risk was. Callback rate from tracker `outcome`.

### 14.4 FR → UI component map (FR-13.2)

Adopted from UI §6 with spec-level component ids. Every FR, HITL, T, TR and NFR has a home;
TR-1, TR-2, TR-9 are recorded as *N/A — development constraint* (UI §6.6).

| ID | Home component (screen) | Also |
| --- | --- | --- |
| FR-1.1 | Audit › Sources table (S8) | Today › Sources card (S1); Settings › Sources (S16) |
| FR-1.2 | Audit › Sources *Policy* column (S8); Settings › Sources *Why* (S16) | Queue *Via* column (S2) |
| FR-1.3 | Settings › Targets › Geography priority (S14) | Audit › Queries geography line (S8); Geo filter (S9); `✈` badge |
| FR-1.3a | Job detail › Hard rules `FR-1.3a` with JD span (S12) | Review › Watch visa line (S3); Audit verdict chip *visa* (S9); Answer sheet impact box (S13) |
| FR-1.4 | Settings › Targets › Seniority (S14) | Audit reason `junior` (S9); Job detail seniority dimension (S12) |
| FR-1.5 | Audit › Queries table (S8) | — |
| FR-1.6 | Job detail › Hard rules `FR-1.6` (S12) | Review › Watch "GenAI substantial" (S3) |
| FR-1.7 | Review › Watch travel/onsite/client-base (S3) | Job detail (S12); Queue `✈`/onsite tag (S2) |
| FR-1.8 | Audit log Sources/Queries/Jobs (S8, S9) | Today funnel links (S1) |
| FR-1.9 | By hand (S10) | Today › By hand card (S1); Audit fallback filter (S9); Tracker channel `manual` (S11) |
| FR-2.1 | Audit › Jobs *Source(s)* cluster (S9); Job detail › Seen on (S12) | Today funnel "−N dupes" (S1) |
| FR-2.2 | Review › Pre-flight *not duplicate* (S3) | By hand duplicate notice (S10); Tracker authority (S11) |
| FR-2.3 | Job detail › Seen on "matched by …" (S12) | — |
| FR-3.1 | Review › score bars (S3); Job detail breakdown (S12) | Score columns everywhere |
| FR-3.2 | Job detail › captured JD with rule spans highlighted (S12) | — |
| FR-3.3 | Review › Why it matches (S3) | Job detail differentiator hits (S12); Report top applications (S17) |
| FR-3.4 | Job detail › per-dimension reasons + Why rejected (S12) | Audit reason column (S9) |
| FR-4.1 / FR-4.1a | Job detail › Hard rules (S12); Audit reason `FR-4.1 <sub>` (S9) | Report rejected groups (S17); `traditional_ml_exceptional` flag in Review (S3) |
| FR-4.2 | Job detail › Hard rules `FR-4.2` quoted (S12) | Pre-flight *no false qualification* (S3) |
| FR-4.3 | Job detail › *Promote to queue* absent for hard rules (S12) | Pre-flight row (S3) |
| FR-5.1 | Audit reason `FR-5.1 fraud:<signal>` (S9); Job detail (S12) | Report rejected group (S17) |
| FR-5.2 | Run console › Secrets guard counter (S18) | Guard events panel; Job detail when triggered |
| FR-6.1 | Review › Resume diff change classes (S3) | — |
| FR-6.2 | Review › Pre-flight *facts 49/49*, *Open tailored PDF*, Skills "nothing added" (S3) | Edit guard (S6) |
| FR-6.3 | Review › Version block (S3); Tracker expansion resume version (S11) | Edit creates `vN` (S6) |
| FR-6.4 | Review › Pre-flight *ATS 3-parser* (S3); Run console stage 8 (S18); Needs attention row | Edit re-check (S6) |
| FR-7.1 | Review › Cover letter tab with word count / "not requested" (S4) | Queue Docs `L`/`–` (S2) |
| FR-7.2 | Review › Evidence markers `[n]` (S4) | — |
| FR-8.1 | Review › Answers tab source tags (S5) | Answer sheet › Used counts; years table (S13) |
| FR-8.2 | Review › Answers *generated* rows with markers (S5) | — |
| FR-8.3 | Needs-you-now › Question card (S19) | Answers *halted* count (S5); Today (S1) |
| FR-9.1 | Review › Pre-flight 12 rows (S3) | Approve disabled on ✗ |
| FR-9.2 | Settings › Targets › Daily ceiling (S14) | Today funnel "deferred (over ceiling)" (S1); Review "Approvals today n / ceiling" (S3) |
| FR-9.3 | Review › Approve + grace window (S3) | Queue (S2) |
| FR-9.4 | Needs-you-now › Question card (S19); Telegram M3 | Report attention (S17) |
| FR-10.1 | Tracker table + expansion (S11) | — |
| FR-10.2 | Tracker write-failure banner (S11); Pre-flight cites tracker (S3) | Run console checkpoint events (S18) |
| FR-11.1 | Reports (S17) | Telegram M4/M5 |
| FR-12.1 | Header run state + next run; Settings › Schedule (S16) | Missed-run banner |
| FR-12.2 | Run console checkpoint + Resume run (S18); Queue carry-over age (S2) | Needs-you-now *Continue* (S19) |
| FR-13.1 / 13.2 / 13.3 | This table; the nine minimum surfaces: S8/S9 · S2 · S11 · S17 · S12 · S9/S12 · header meter · S14 · S13 | — |
| HITL-1 | Review › Approve + grace (S3) | Queue (S2) |
| HITL-2 | Needs-you-now › Blocked card *Take over browser · Continue* (S19) | Telegram M2; By hand *Resume with agent* (S10) |
| HITL-3 | Needs-you-now › Question card with *Save to answer sheet* (S19) | Answer sheet › Learned from halts (S13) |
| HITL-4 | Needs-you-now › claim vs resume line, *Use resume wording* (S19) | Edit guard (S6) |
| HITL-5 | Review (S3–S5); no bulk approve | Report › Your review today (S17) |
| HITL-6 | Queue Tier-3 inline caveat (S2); Review Watch gaps (S3) | Settings › Targets (S14) |
| HITL-R1..R5 | Needs-you-now (S19); Review decision panel (S3); Reject overlay (S7); Answer sheet halts counter (S13); Queue age (S2); Run console idempotency line (S18) | — |
| T-1..T-5 | Pre-flight *no fabrication* / *facts* / *no false qualification* (S3); diff `+` violations; markers `[n]` (S4); Question card (S19); Edit guard (S6) | Guard events panel |
| TR-3..TR-8, TR-10..TR-12 | S1–S19 overall; Run console (S18); Settings › Models (S15); header meter; Settings › Data & secrets (S16) | — |
| TR-1, TR-2, TR-9 | N/A — development constraint | — |
| NFR-1..NFR-7 | Tracker banner (S11); Run console idempotency (S18); Tracker bundle (S11); Audit partial rows (S8); Audit pacing (S8); Run console total (S18); Settings › Data third parties (S16) | — |
| C-1/Q-3, C-2, C-3, C-5/§2.1, §7.1, Q-6/O-5, Q-7, Q-8, Q-9, O-2, §9 | Settings › Sources policy 🔒 (S16); Needs-you-now (S19); grace undo + "no unsend" toast (S3); Answer sheet masked (S13) + field-name-only rows (S5); Settings › Models (S15); Settings › Schedule (S16); Settings › Notifications (S16); header meter; Settings › Data retention (S16); Answer sheet ⚠ unconfirmed + impact (S13); Reports review/callback metrics (S17) | — |

---
## 15. Phased implementation plan

Complexity: **S** ≤ ½ day · **M** 1–2 days · **L** 3–5 days · **XL** > 5 days (for a strong
implementer with this spec). Each phase names its exit gate from the test plan. Phases 1–3 are
the safety core and must be green before any browser touches a real ATS.

### 15.0 Release plan — Q-S, decided on measured evidence

**The decision.** Release 1 is the **non-submitting** product. Release 2 adds automated
submission, entered deliberately rather than by default.

**The evidence, not the taste.** The discovery spike (`spike/`, run 2026-09-15) probed 50 seeded
companies against four public board APIs and then verified every unresolved slug:

| Measurement | Value |
| --- | --- |
| Boards reachable by the spec's auto-submit adapters (Greenhouse/Lever) | 20 of 50 |
| Reachable AI/ML roles on those boards | **40** |
| Of which dated within 30 days | 38 → **~7.0 roles/week** |
| Unresolved boards that turned out to be wrong slugs | **0 of 29** |
| Companies on ATSs outside all four probed (Workday, Darwinbox, Keka, in-house) | 21 |
| Share of the reachable pool from the top four companies | 60% |

Two things follow. First, **~7 roles/week is an upper bound** — it is a title/location regex, not
the ≥ 70 rubric of §4.6, and the hard rules of §4.5 cut it further; the realistic queue is a
handful a week. Second, **that number is not an artefact of a lazy seed list**: none of the 29
unresolved boards were wrong Greenhouse/Lever slugs, so fixing slugs does not move it.

Against a system whose ceiling is 10–20 applications *per day*, supply is one to two orders of
magnitude below the constraint the design optimises for. The submission protocol — the part
carrying every irreversible action, five of the ten CRITICALs, and nine of the fourteen
unsatisfiable acceptance criteria — would be built to automate work that takes a human minutes.

**What Release 1 contains.**

| Phase | In Release 1 | Deferred to Release 2 |
| --- | --- | --- |
| 0 Foundations | all (T-0.1 … T-0.8) | — |
| 1 Ledger + FactGuard | all (T-1.1 … T-1.7) | — |
| 2 Tracker + graphs | T-2.1, T-2.2, T-2.3, T-2.7, T-2.8 | T-2.4, T-2.4a/b/c, T-2.5, T-2.6, T-2.9, T-2.10 — the whole submission protocol |
| 3 Tailoring + docs | T-3.1, T-3.2, T-3.3, T-3.4, T-3.9, T-3.10 | T-3.5, T-3.6, T-3.7, T-3.8 — form probe, router, filler, mapper agent |
| 4 Discovery | all (T-4.1 … T-4.10) | — |
| 5 API + reports | all, minus the submission endpoints | pre-flight, unknown-outcome, blocker and handoff endpoints |
| 6 Frontend | **thin cut** — see below | the rest of the 19 screens |
| 7 Hardening / go-live | — | all (T-7.1 … T-7.4) |

**The honest arithmetic, because the review's "ships months earlier" overstates it.** Deferring
submission removes roughly **25–40 implementer-days of 120–200 — about 20%**. The risk reduction is
far larger than the time saved: it removes every irreversible action from v1, and with it the
entire class of defect that got v1.0 rejected. But if *time to first usable output* is the goal,
the bigger lever is elsewhere, and it should be pulled in the same pass:

> **Phase 6 is the largest non-safety cost in the plan** — a 19-screen keyboard-first SPA
> (T-6.3 alone is XL) for a **single user**. Release 1 ships a **thin cut**: the review screen
> (S3–S7, where the whole value is), the by-hand list (S10), the tracker (S11) and settings
> (S13–S16). Today/queue/audit/reports/run-console (S1, S2, S8, S9, S12, S17, S18, S19) are
> Release 2 or later; their data is reachable from the API and, at a handful of applications a
> week, a table is enough.

Combined, Release 1 is roughly **half the total plan** and produces the thing that actually helps:
tailored, fact-checked documents for the right roles, ready to send.

**What Release 1 must still honour.** Everything in §8 (FactGuard), §10 (tailoring contract) and
the C-6/C-7/C-8 fixes. Documents-only does not weaken the truthfulness argument — it *is* the
truthfulness argument, with the click removed. HITL-5 still applies: Avadh reviews every artefact,
and §11.7 puts the real values in front of him.

**Entering Release 2.** Not a date — a trigger. Re-open Q-S when any holds: measured tier-1 supply
exceeds ~20 reachable roles/week; or Release 1 has run for a month and the hand-over step is the
demonstrated bottleneck; or the Ashby/SmartRecruiters adapters (tier 2, a further ~1.9 roles/week,
including Sarvam AI) are wanted, which is the cheaper adjacent move. Release 2 then begins with
the deferred Phase 2 tasks, and `submission_enabled` is turned on only at T-7.3.

### Phase 0 — Foundations (exit: repo builds, static checks run, master snapshot recorded)

| Task | Description | Cx |
| --- | --- | --- |
| T-0.1 | Repo layout `src/jobagent/`, `tests/`, `fixtures/`, `config/`; pyproject with pinned `langchain>=1.3.3`, `langgraph>=1.2`, `langgraph-checkpoint-sqlite`, `langchain-anthropic`, `langchain-openai`, FastAPI, Playwright, SQLAlchemy, pdfminer.six, pypdf, PyMuPDF | S |
| T-0.2 | `config` module: `Settings`, `Stage`, `prices.yaml`, `synonyms.yaml`, `canaries.yaml`, `field_ontology.yaml`, banned-filler list; registry-scoped secret loading via `winreg` | M |
| T-0.3 | Static checks: import lint (AC-NF-11), `InMemorySaver` ban (AC-ID-24), interrupt rules (AC-ID-13/14), topology (AC-ID-25), path length (AC-FM-19), `GuardedModel`-only calls | M |
| T-0.4 | **BLOCKING prerequisite of Phase 1 (C-8)** — element-key scheme + `id` attributes on `resume-ats.html` (zero text change; verify by identical text diff); content-anchored keys where cheap; `build_ledger` refuses a master whose ids do not match; rebuild PDF; three-parser test unchanged. **Q-O must be closed before Phase 1 starts, not at go-live** | M |
| T-0.7 | Single-instance mutex + port-bind-before-reconcile startup sequence (§3.2, §9.6) (C-10) | S |
| T-0.8 | `settings.submission_enabled` with typed-confirmation enable, audit row, static check on the default (C-11) | S |
| T-0.5 | `clock`, `faults.maybe_kill`, logging with secret scrubber | S |
| T-0.6 | Fixture corpus skeleton: ≥ 120 JDs by category tags, ≥ 40 forms, dup groups (test plan §0.2) — content authored across phases | L |

### Phase 1 — Ledger and FactGuard (exit: AC-AF-01..13, AC-AF-15, AC-AF-16 green)

| Task | Description | Cx |
| --- | --- | --- |
| T-1.1 | `ledger.build_ledger` with extractors for the nine fact classes; snapshot test; ≥ 49 facts | L |
| T-1.2 | FactGuard C1 structural diff whitelist + `structural_diff` change classes | L |
| T-1.3 | FactGuard C2–C8 deterministic checks | L |
| T-1.4 | FactGuard C9 provenance resolution; C12 filler/word caps; C13 mandatory-gap | M |
| T-1.5 | FactGuard C10/C11 entailment via `judge` stage (`with_structured_output`), with cassette tests | M |
| T-1.6 | Mutation suite: 40 seeded fabrications (AC-AF-15); 10 legitimate tailorings (AC-AF-16) | L |
| T-1.7 | `GuardedModel`, `PromptGuard`, `SpendLedger`, `BudgetGate`, local `Tracer` | L |

### Phase 2 — Tracker, graphs, submission protocol (exit: AC-ID-01..25, AC-FM-05..07, AC-FM-14, AC-FM-18 green against the fake ATS)

| Task | Description | Cx |
| --- | --- | --- |
| T-2.1 | SQLite schema (§6.3), triggers (§6.4), `Tracker.transition`, transitions table | L |
| T-2.2 | `AsyncSqliteSaver` wiring, boot refusal of in-memory saver, `durability="sync"` invocation helpers, thread/run locks | M |
| T-2.3 | `ApplicationGraph` skeleton: all nodes as stubs, edges, policies, `await_*` nodes, `context_schema` | L |
| T-2.4 | `submit` node protocol §9.3 + `PreClickError`/`PostClickError` + `submit_error_handler` + page fingerprint assertion (C-2) | L |
| T-2.4a | `page_commits` + §9.8 per-page commit protocol + `fill_error_handler` (C-1); `FILLING` status | M |
| T-2.4b | §9.5 `confirmed_not_submitted` friction: typed confirmation, 60-minute minimum, ATS checkbox, consequence copy (C-3) | S |
| T-2.4c | `recheck_after_blocker` node + `i_submitted` on HITL-2 (C-2) | S |
| T-2.5 | Fake ATS — **multi-page**, with a per-page POST counter and fault modes (C-1); fake boards | M |
| T-2.6 | Fault injector harness (subprocess kill at named points); AC-ID-02..06, AC-ID-09..11, AC-ID-23 (200-run fuzz, **extended to kill between form pages and assert every per-page POST counter ≤ 1** — C-1); AC-ID-08 extended to assert a second process writes nothing (C-10) | L |
| T-2.7 | Decision API (§7.2) with grace window, idempotent decisions, thread lock, `409/423` semantics; AC-ID-07/08, AC-HL-07/08/23 | M |
| T-2.8 | Startup reconciliation §9.6; `RunControl` pause/drain; AC-HL-25 | M |
| T-2.9 | Pre-flight (§9.4) with live re-fetch; AC-SB-01..11 | M |
| T-2.10 | `UNKNOWN_OUTCOME` resolution endpoints + `await_unknown`; AC-ID-04 second branch, AC-UI-14 | S |

### Phase 3 — Tailoring, render, letters, forms (exit: AC-RT-*, AC-CL-*, AC-AF-14/17/18/19/21/22, AC-HL-14..17 green)

| Task | Description | Cx |
| --- | --- | --- |
| T-3.1 | `TailoringPlan` schema + validators + `apply_plan`; change budget | L |
| T-3.2 | `render_pdf` subprocess wrapper + `ats_check` (three parsers, probes, headings, nw, fonts, letter-spacing) | L |
| T-3.3 | `Letter` / `SubjectiveAnswer` claim generation with provenance; deterministic assembly | M |
| T-3.4 | Repair loop + HITL-4 nodes | M |
| T-3.5 | `probe_form` (Playwright field enumeration), `FormModel`, `supported_ratio` | L |
| T-3.6 | Question router + field ontology + answer-sheet formatting + `years_by_technology` + EEO decline | L |
| T-3.7 | `FormFiller` fill-time isolation; `fill_form` node; blocker detection; HITL-2 nodes | L |
| T-3.8 | Career-page mapper `create_agent` on the **wrapped** model with `GuardMiddleware` and `ToolCallLimitMiddleware(..., exit_behavior="error")`; `inspect_form` projection + its leak test (C-5, M-3) | M |
| T-3.9 | Edit pipeline (§7.4) incl. confirm-edit; AC-AF-19, AC-HL-02 | M |
| T-3.10 | Adversarial JD suite AC-AF-14 with live `generate` model | M |

### Phase 4 — Discovery, dedup, eligibility, scoring (exit: AC-DS-*, AC-DD-*, AC-HR-*, AC-SC-*, AC-FD-*, AC-FM-01..04 green)

| Task | Description | Cx |
| --- | --- | --- |
| T-4.1 | `PacedClient` (per-domain concurrency, jitter, back-off, daily caps, outbound allowlist) | M |
| T-4.2 | Source adapters: Greenhouse, Lever (board JSON), Workday listing, career pages (rules), Wellfound, LinkedIn/Naukri/Indeed logged-out best-effort | XL |
| T-4.3 | Company watchlist table + API + auto-grow | M |
| T-4.4 | Query matrix generator; `queries` logging | S |
| T-4.5 | `dedup` module (canonical URL, company/title normalisation, shingled similarity, merge, position families, agency handling) | L |
| T-4.6 | `JobFacts` extraction (`screen`) + deterministic fraud signals | M |
| T-4.7 | Eligibility rules engine §4.5 with spans | M |
| T-4.8 | `Score` structured output, validators, ranking, tiering, tier-3 gap rule, traditional-ML exceptional flag | M |
| T-4.9 | `DiscoveryGraph` with `Send` per source, bounded per-job loops, `select`, `spawn_apps`, `report` | L |
| T-4.10 | Run supervisor: scheduler, catch-up, lock, application-thread launcher (bounded), M1 batching | M |

### Phase 5 — Backend API, notifications, reports (exit: AC-TK-*, AC-HL-01..11, AC-FM-08..11, AC-NF-01..14 green)

| Task | Description | Cx |
| --- | --- | --- |
| T-5.1 | FastAPI app, loopback bind, CSRF, SSE events, static SPA serving | M |
| T-5.2 | Endpoints §7.1 (dashboard, queue, review, diff, letter, answers, artefacts, tracker, jobs, audit, fallback, settings, answer sheet, reports, runs, needs-you, controls) | XL |
| T-5.3 | Telegram outbox, poller, sender check, commands, templates M1–M9 with allowlisted variables | M |
| T-5.4 | Reports (morning/evening), trend, review telemetry, weekly reject-reason summary | M |
| T-5.5 | Retention job; export; data summary | S |
| T-5.6 | Outbound proxy E2E harness; AC-NF-03/04/05 scans | M |

### Phase 6 — Frontend (exit: AC-UI-01..15, AC-NF-15 manual)

| Task | Description | Cx |
| --- | --- | --- |
| T-6.1 | App shell, routes, header chrome, global keymap, SSE client, six-state components | L |
| T-6.2 | Today dashboard (S1), Queue (S2) | M |
| T-6.3 | Review screen: diff renderer, letter markers, answers tab, decision panel, grace toast, edit mode with live guard, reject overlay (S3–S7) | XL |
| T-6.4 | Audit log Sources/Queries/Jobs (S8, S9), By hand (S10) | L |
| T-6.5 | Tracker + bundle view (S11), Job detail (S12) | L |
| T-6.6 | Settings screens (S13–S16) incl. masked answer sheet, years table, impact box | L |
| T-6.7 | Reports (S17), Run console (S18), Needs-you-now (S19), keyboard help, command palette | L |

### Phase 7 — Hardening and go-live (exit: test plan §17 "Enable real submission" and "First live week")

| Task | Description | Cx |
| --- | --- | --- |
| T-7.1 | Full E2E suite through proxy; AC-AF-14, AC-AF-15, AC-ID-05, AC-ID-23 as release blockers | M |
| T-7.2 | Windows Task Scheduler registration script; service restart; missed-run behaviour on a real sleeping PC | S |
| T-7.3 | Supervised first live week: **the act of turning `submission_enabled` on** (C-11), with ceiling 1/day as a second and independent limit, ATS confirmation reconciliation daily; raise only after 5 clean days | M |
| T-7.4 | Month-2 metrics: rescue events, callback rate | S |

**Totals:** 65 tasks (11 S · 29 M · 22 L · 3 XL) — v2 adds T-0.7, T-0.8, T-2.4a, T-2.4b, T-2.4c
and upgrades T-0.4 from S to M. Summing the complexity bands gives ≈ 120–200
implementer-days; the safety core (Phases 1–3, 32 tasks) is roughly half of that. Phases 1–3 are
sequential; Phase 4 can proceed in parallel with Phase 3 after Phase 2; Phase 6 can start after
T-5.2 stabilises the API.

---

## 16. Risk register

| # | Risk | Severity | Likelihood | Mitigation | Residual |
| --- | --- | --- | --- | --- | --- |
| R-1 | **Double submission** via an unforeseen re-execution path (retry, resume, reconciliation, human double-click) | Critical | Low (by design) | Three independent layers (§9): tracker state gate at node top, `PreClickError`-only retries, startup reconciliation → `UNKNOWN_OUTCOME`; DB triggers; 200-run kill fuzz; first live week at 1/day with ATS reconciliation | Low |
| R-2 | **Fabrication slips past FactGuard** (novel phrasing, synonym drift, judge false-`ENTAILED`) | Critical | Medium | Generator emits plans/claims not prose; deterministic checks first; judge ≠ generator; mutation suite 40/40; adversarial live suite; Avadh's review is the last gate and the UI makes traces visible | Medium — the residual is the human reviewer's attention |
| R-3 | **Review degrades into rubber-stamping** as volume settles | High | Medium | Diff-first tailoring (§10), change budget, no bulk approve, review-time telemetry and reject-rate in Reports; if median review time drops under ~20 s the report flags it | Medium |
| R-4 | **Answer-sheet leak** through an unexpected channel (error message, trace, screenshot OCR, Telegram) | High | Low | Values isolated to one table, encrypted, decrypted only in `FormFiller`/reveal; `PromptGuard`; log scrubber; allowlisted notification variables; proxy and log scans in CI | Low |
| R-5 | **Discovery yield too low** on the submit-capable sources | High | **MEASURED, 2026-09-15: fired.** ~7 reachable roles/week on Greenhouse/Lever, upper bound, from 20 of 50 seeded boards; 21 companies are on ATSs the spec cannot auto-submit to | Q-S decided accordingly (§15.0): ship the non-submitting product first, so the plan no longer depends on this risk not firing. Seed list (Q-B) verified; auto-grow from aggregators; per-source yield in the audit log | Accepted, and designed around rather than mitigated |
| R-6 | **Aggregator scraping is challenged/banned** (LinkedIn/Naukri/Indeed) | Medium | High | Logged-out only, 24 h back-off, best-effort; never the personal session; measured yield decides whether to keep | Medium |
| R-7 | **Workday assisted mode still consumes Avadh's time** | Medium | High | Explicit assisted flow with pre-fill; by-hand fallback; promote to automation only if audit shows a repeatable pattern | Medium |
| R-8 | **Career-page forms too varied** — `supported_ratio` < 0.9 on most | Medium | Medium | Mapper agent (route-only tools) + fallback with prepared documents (D-3) | Medium |
| R-9 | **Model/provider drift** (model ids retired; structured-output behaviour differs per provider) | Medium | Medium | Stage strings in settings; `with_structured_output` tests per configured model; V-level nightly evals; fallback provider configurable | Low |
| R-10 | **Checkpoint DB growth / corruption** | Medium | Low | Small state (ids only); 30-day pruning; `synchronous=FULL`; boot check refuses corrupt file | Low |
| R-11 | **PC asleep / service not running** → silent missed days | Medium | High | Catch-up rule, M8 at 09:15, header missed state, Task Scheduler restart | Low |
| R-12 | **`render.py`/Chromium path drift** breaks tailoring | Low | Medium | `PW_CHROME` override; `TAILORING_FAILED` isolates; alert | Low |
| R-13 | **Judge model cost** on 10–20 apps × ~15 claims/day | Low | Low | Judge on `analyse` tier; batched per artefact; well under $5/day | Low |
| R-14 | **Element keys drift** if the master is edited — provenance silently resolves to the *wrong* line | Critical | **High** (a job-seeker edits his résumé) | C-8: explicit `id`s are mandatory before Phase 1; `build_ledger` refuses a mismatched master instead of deriving; content-anchored keys; master bytes and ledger persisted per `master_hash`; AC asserts a pointer resolves to the same text or fails loudly | Low |
| R-15 | **Localhost Telegram links** leave blocked gates unseen for hours | Medium | Medium | Self-sufficient messages; stale reminders; configurable base URL | Medium |

**Three highest-severity risks: R-1 (double submission), R-2 (fabrication past the verifier),
R-3 (review rubber-stamping).** R-1 and R-2 are the two test groups that gate real submission;
R-3 is why the tailoring contract is narrowed.

---

## 17. Departures from requirements, assumptions and UI design

| # | Departs from | What this spec does instead | Why |
| --- | --- | --- | --- |
| D-1 | A-23 (three model stage keys) | Adds a fourth stage `judge`, defaulting to the `analyse` model, validated ≠ `generate` | AC-AF-08 requires an independent judge model; without a stage key it cannot be configured (TR-10) |
| D-2 | AC-AF-06 whitelist permits `<li>` removal | Generator's `TailoringPlan` offers no removal op; FactGuard still accepts removal per the AC | Removal risks the one-page constraint and adds review load; the checker stays test-plan-exact so legitimate hand tailorings pass |
| D-3 | FR-6.1 "where a resume upload is allowed" | Documents-only tailoring for discovery-only / unsupported-form jobs scoring ≥ 80 (`tailor_fallback_min_score`) | UI P-5: a by-hand list without prepared documents will not be used; the best Indian roles are on Naukri/LinkedIn. Costs review time; counted against the ceiling |
| D-4 | UI §7 principle 4 "Telegram notify-only" | Telegram supports `/reject`, `/pause`, `/resume`. **`/approve` does not exist** (M-13) | A-14 wants inbound commands and the test plan requires Telegram *reject*; approve is a different matter. **This departs from AC-HL-10/11**, which describe an approve-over-Telegram path: those two ACs are amended to assert `/approve` returns a dashboard link and records nothing. The test plan was internally inconsistent here — AC-HL-26 forbids any setting that disables HITL-5 while AC-HL-10/11 describe one — and v2.3 resolves it in favour of AC-HL-26, which is the one carrying the safety property |
| D-5 | UI §3.16 storage path under the repo | Default `data_dir = %LOCALAPPDATA%\JobAgent` | AC-NF-19 (not cloud-synced), C-6 (shallow paths); Desktop may be OneDrive-synced on Windows 11 |
| D-6 | UI J2 / §3.13 "Promote to queue" for score < 70 | Promote allowed only for `tier3_gap` and `deferred_over_ceiling`; **not** for total < 70 | §9 success metric "below-threshold applications: zero" is a requirement; a < 70 override would violate it. Hard rules never promotable (unchanged) |
| D-7 | FR-8.1 per-technology years | `years_by_technology` table filled by Avadh; deterministic; HITL-3 when absent; no LLM ever produces the number | G-C2 / analysis §5.3: the resume has no such figures; anything else is fabrication |
| D-8 | Requirements §5 lists HITL-1 and HITL-5 as separate gates | One `await_review` interrupt satisfies both; pre-flight re-verifies after the grace window and before the click | UI J1/§3.4; a second modal trains click-through; the click remains in its own node (AC-ID-25) |
| D-9 | HITL-R2 `edit` as a resume decision | Edits are API-side (new version + FactGuard) while the thread stays paused; only approve/reject/regenerate/postpone resume the graph | Resuming per edit re-runs the node and burns decision ids; API-side edits are simpler and testable (AC-HL-02, AC-AF-19) |
| D-10 | Analysis §5.11 suggests `HumanInTheLoopMiddleware` on a `submit_application` tool | No submit tool exists; the click is a graph node after the gate | Stronger separation; the middleware would put the irreversible action inside an agent loop |
| D-11 | Analysis interpretation "screen → analyse two-pass scoring" | `screen` extracts `JobFacts`; `analyse` produces the single `Score` (no numeric first-pass score) | Avoids two scores to reconcile; rules run on facts, rubric runs once |
| D-12 | UI §3.15 "Score thresholds — display only" vs analysis "configurable with defaults" | Thresholds and rubric weights are constants in code, displayed in Settings | FR-4.1 "never overridable by score" and §9 metrics depend on fixed thresholds |

Everything else in the assumption register (A-1..A-24) is adopted as written.

---

## 18. Knowledge-base verification table

Every LangChain/LangGraph symbol used in this spec, with the page that verifies it. Symbols
marked **[UNVERIFIED]** in the body are *not* LangChain/LangGraph APIs (third-party or external).

| Symbol / behaviour | Verified in |
| --- | --- |
| `from langchain.agents import create_agent, AgentState`; `system_prompt=`, `tools=`, `middleware=`, `response_format=`, `state_schema=`, `context_schema=`, `checkpointer=` | `langchain/agents.md` §204–406, §653–696; `CORE-CONCEPTS.md` §1.1–1.3 |
| `from langchain.chat_models import init_chat_model`; `"provider:model"` strings | `langchain/models.md`; `CORE-CONCEPTS.md` §1.2 |
| `model.with_structured_output(Schema, include_raw=True)` | `langchain/models.md` §647–725 |
| `from langchain.agents.structured_output import ProviderStrategy, ToolStrategy` | `langchain/structured-output.md` §162, §244 |
| `result["structured_response"]` (agent) | `langchain/agents.md` §273 |
| `AIMessage.usage_metadata` (`input_tokens`, `output_tokens`) | `langchain/messages.md` §263–271; `langchain/models.md` §1056–1101 |
| `from langchain_core.callbacks import get_usage_metadata_callback` | `langchain/models.md` §1081 |
| `from langchain.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage` (not `langchain_core.messages`) | `CORE-CONCEPTS.md` §1.3, gotcha 2 |
| `from langchain.tools import tool, ToolRuntime`; `runtime.state`, `runtime.context`, `runtime.tool_call_id`; tools returning `Command(update=...)` | `langchain/tools.md` §154–266 |
| `HumanInTheLoopMiddleware(interrupt_on={... "allowed_decisions", "when"})`; `Command(resume={"decisions": [...]})`; `version="v2"` → `GraphOutput.interrupts` | `langchain/human-in-the-loop.md` §47–251 |
| `ToolCallLimitMiddleware(tool_name=, thread_limit=, run_limit=, exit_behavior=)`; `exit_behavior` defaults to `'continue'` (blocked calls + error messages, model decides when to end); `'error'` raises `ToolCallLimitExceededError` and stops execution immediately; `'end'` only for a single limited tool | `langchain/middleware__built-in.md` §591–660 (M-3 — v1 marked the kwargs `[UNVERIFIED]`; they are documented with a worked example) |
| `ModelRetryMiddleware`, `ModelFallbackMiddleware`, `PIIMiddleware(... strategy=block\|redact\|mask\|hash, detector=...)` | `langchain/middleware__built-in.md` |
| Custom middleware hooks `before_model` / `after_model` (the C-5 `GuardMiddleware`) | `langchain/middleware__custom.md` |
| **`interrupt()` bypasses both retry policies and error handlers** (`GraphBubbleUp`); it is not routed to the error handler and the graph pauses as usual | `langgraph/fault-tolerance.md` §389–391, "Behavior with `interrupt()`" (M-1 — v1 marked this `[UNVERIFIED]`; it is answered under a heading that names the question) |
| **`delete_thread` / `adelete_thread(thread_id)`** on the checkpointer interface — deletes all checkpoints *and* write rows for a thread; `aprune` for thread-history pruning | `langgraph/checkpointers.md` §407 (signature), §544 (subsection), extended-capabilities table (M-2 — v1 marked this `[UNVERIFIED]` and instructed hand-deletion from inferred tables) |
| `from langgraph.graph import StateGraph, START, END`; `add_node`, `add_edge`, `add_conditional_edges`, `.compile(checkpointer=)` | `langgraph/graph-api.md`; `CORE-CONCEPTS.md` §2.2 |
| `StateGraph(State, context_schema=...)`; `Runtime[Context]` from `langgraph.runtime`; `runtime.context`, `runtime.execution_info.thread_id`; `invoke(..., context=...)` | `langgraph/graph-api.md` §498–935 |
| Reducers `Annotated[list, operator.add]`; `Overwrite` from `langgraph.types` | `langgraph/graph-api.md` §155–269 |
| `from langgraph.types import Send`; `Send("node", {...})` from conditional edges; `Send(..., timeout=TimeoutPolicy(...))` | `langgraph/graph-api.md` §748–758; `langgraph/fault-tolerance.md` |
| `from langgraph.types import interrupt, Command`; node restarts from the top on resume; `Command(resume=...)` is the only Command input; `Interrupt(value, id)`; rules of interrupts (no try/except, no loops, idempotent side effects, one per node) | `langgraph/interrupts.md` §11–615 |
| `result["__interrupt__"]` with `invoke`; `stream_events(version="v3")` `.interrupts` / `.interrupted` | `langgraph/interrupts.md` §46, §54–75 |
| `from langgraph.types import RetryPolicy, default_retry_on`; params `max_attempts`, `initial_interval`, `backoff_factor`, `max_interval`, `jitter`, `retry_on` (type, sequence or callable); default excludes `ValueError`, `OSError`… and retries `NodeTimeoutError` | `langgraph/fault-tolerance.md` §27–84; `langgraph/use-graph-api.md` §522–534 |
| `from langgraph.types import TimeoutPolicy`; `timeout=TimeoutPolicy(idle_timeout=, run_timeout=)`; `NodeTimeoutError` (`langgraph.errors`); timeouts async-only | `langgraph/fault-tolerance.md` §240–275, Limitations; `langgraph/use-graph-api.md` §587–598 |
| `add_node(..., error_handler=fn)`; `from langgraph.errors import NodeError` (`error.node`, `error.error`); handler returns `Command(update=, goto=)`; handler fires after retries exhausted | `langgraph/fault-tolerance.md` §276–337 |
| `builder.set_node_defaults(retry_policy=, error_handler=, timeout=, cache_policy=)`; per-node overrides win; not inherited by subgraphs | `langgraph/fault-tolerance.md` §401–520 |
| `from langgraph.runtime import RunControl`; `control.request_drain(reason)`; `from langgraph.errors import GraphDrained`; drain between super-steps; resume with `invoke(None, config)`; `runtime.drain_requested` | `langgraph/fault-tolerance.md` Graceful shutdown |
| `graph.get_state(config)` → `StateSnapshot(values, next, config, metadata, created_at, parent_config, tasks)`; `tasks[i].interrupts`; `get_state_history`; `update_state(config, values, as_node=)` | `langgraph/checkpointers.md` §120–160, §287–290; `langgraph/use-time-travel.md` §81–161 |
| `invoke(None, config)` resumes from the last checkpoint | `langgraph/fault-tolerance.md` §590–593; `langgraph/use-time-travel.md` §87 |
| `durability="sync"` on execution methods; modes `exit` / `async` / `sync` | `langgraph/checkpointers.md` §246–261 |
| `langgraph-checkpoint-sqlite`; `from langgraph.checkpoint.sqlite import SqliteSaver`; `from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver`; `checkpointer.setup()` | `langgraph/checkpointers.md` §278, §294, §326–329; `langgraph/persistence.md` §71 |
| `InMemorySaver` loses everything on restart — never in production; `thread_id` < 255 chars → UUID; checkpoint growth → prune | `langgraph/persistence.md`; `CORE-CONCEPTS.md` §2.4, gotchas 4, 11, 13 |
| Subgraph checkpoint namespaces; parent must have checkpointer; per-invocation vs per-thread (`checkpointer=True`) | `langgraph/use-subgraphs.md` §124–432 |
| Version floors: `langchain>=1.3.3` (conditional interrupts), `langgraph>=1.2` (timeouts, error handlers, drain) | `langchain/human-in-the-loop.md`; `langgraph/fault-tolerance.md` |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY` env vars | `langchain/observability.md` §27–28 |
| `from langchain_core.language_models.fake_chat_models import GenericFakeChatModel` | `langchain/test__unit-testing.md` §13–26 |
| Model strings `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `anthropic:claude-opus-4-8` | `langchain/models.md` §1053; many pages; `langchain/middleware__built-in.md` §948 |
| LangChain 1.0 removed `LLMChain`, `AgentExecutor`, `initialize_agent`, `RetrievalQA` — none used | `CORE-CONCEPTS.md` critical version note |

Items explicitly **not** from the knowledge base (standard libraries / external services, marked
[UNVERIFIED] where they appear): FastAPI, uvicorn, SQLAlchemy, APScheduler, Playwright API
details, httpx, `cryptography`, pdfminer.six/pypdf/PyMuPDF, Greenhouse/Lever board JSON
endpoints, Windows Task Scheduler options, `winreg`, `win32event.CreateMutex`.

**Three entries were removed from this list in v2 (M-1, M-2, M-3).** Each was marked
`[UNVERIFIED]` in v1 and each is in fact answered in the supplied knowledge base — one of them
under a heading that names the question. They are now rows in the table above, with citations. This
matters beyond the three fixes: TR-2 ("All LangChain/LangGraph APIs must be verified against
`knowledge-base/`") is the requirement this document most loudly claims to honour, and v1 broke it
while asserting it. Every remaining `[UNVERIFIED]` mark in this document was re-derived during the
v2 pass and names a third-party or external API, not a LangChain/LangGraph one.

---

## 19. Open questions

Carried from the analysis (§6) with the default this spec builds on; plus new ones raised here.

| # | Question | Default built | Impact if changed |
| --- | --- | --- | --- |
| Q-A | Resume tailoring in scope for v1? | Yes | Phase 3 shrinks to letters/answers; HITL-5 view loses the diff |
| Q-B | Seed company watchlist (30–50 companies with board URLs)? | Empty → discovery limited to aggregators until filled | Directly determines day-one yield on submit-capable sources (R-5) |
| Q-C | Workday assisted in v1? | Yes | Full automation would add an XL task and HITL-2 on most tenants |
| Q-D | `years_by_technology` values for AI / RAG / LLMs / Python / MCP / LangChain / enterprise AI? | Empty → HITL-3 each time | Fewer halts; values must be Avadh's own statement |
| Q-E | Any EU / Canada / UAE work permit (O-2)? | None → sponsorship required | Widens eligible pool; single setting |
| Q-F | Relocation stance and earliest start date (O-2)? | HITL-3 when asked | Fewer halts |
| Q-G | Hosted tracing acceptable? | No (local only) | Would ship resume/JD text to LangSmith |
| Q-H | Hard-stop spend level? | $20 | — |
| Q-I | Approve from Telegram? | **CLOSED 2026-09-15: No, and the capability is removed** (M-13). Not merely defaulted off — one-tap approve is spot-checking by another name, and a flag that can disable HITL-5 makes §12.5's central guarantee false | Re-opening it means re-opening AC-HL-26, and would need a DEPARTURE against FR-9.3 |
| Q-J | Repost block window? | 180 days | — |
| Q-K | Expected CTC in AED/EUR/CAD? | HITL-3 | Add per-currency answer-sheet keys |
| Q-L | Auto-select "prefer not to say" on EEO? | Yes | — |
| **Q-M (new)** | Accept D-3 (documents-only tailoring for fallback jobs ≥ 80) and its review-time cost? | Yes, threshold 80, counted against ceiling | Off → by-hand list has no downloads |
| **Q-N (new)** | Accept D-6 (no promote-to-queue for score < 70)? | Yes | Allowing it breaks the §9 zero-below-threshold metric |
| **Q-O** | May the master `resume-ats.html` receive `id` attributes matching the element keys (zero text change)? | **RATIFIED in v2 — yes, and required. Must be closed before Phase 1 begins** (C-8). The "ledger works without them" default is withdrawn: without ids, stored provenance silently resolves to the wrong line after any master edit | Blocking. If refused, AC-AF-08 cannot pass and NFR-3 reconstruction is unsound |
| **Q-P (new)** | Data directory `%LOCALAPPDATA%\JobAgent` acceptable (D-5)? | Yes | Repo-relative path risks OneDrive sync and long paths |
| **Q-Q (new)** | Default `generate` model — confirm the strongest currently available Anthropic model id at build time (only `claude-opus-4-8` appears in the knowledge base) | `anthropic:claude-opus-4-8` | Config change only |
| **Q-R** | Bounded parallel tailoring (2 concurrent application threads) acceptable, or strictly serial for easier hand-off? | 2 | Serial lengthens the 09:00 run; parallel complicates HITL-2 browser hand-off (browser worker is serial regardless) |
| **Q-S** | Ship the **non-submitting product first** and treat automated submission as a later decision made with real operating experience? | **DECIDED 2026-09-15: yes.** Release 1 is documents-only; automated submission is Release 2, entered deliberately (§15.0). Decided on the discovery spike's measured supply, not on taste — see `spike/out/summary.md` | Reversible at low cost: v2 already made documents-only a first-class configuration, so Release 2 is additive rather than a rewrite. If measured supply rises materially, re-open it |
| **Q-T (new)** | Minimum wait before `confirmed_not_submitted` is enabled — 60 minutes (C-3 default)? | 60 min, configurable, never zero | Shorter increases the chance of authorising a second submission before the ATS confirmation has had time to arrive |

---

## 20. Changelog — what v2 changed, and which finding it closes

v1.0 was **REJECTED** by adversarial CTO review on 2026-09-15: 10 CRITICAL · 24 MAJOR · 12 MINOR,
with 14 of 277 acceptance criteria unsatisfiable as designed. This revision closes the ten
CRITICALs and the four MAJORs the review required in the same pass. Every row below is a change to
this document, not a plan to change it.

| # | Finding | What v2 does | Sections |
| --- | --- | --- | --- |
| **C-1** | `fill_form`'s multi-page POSTs are irreversible acts outside the submission protocol; §5.3 and §13.6 asserted "no POST" | New `FILLING` status and `page_commits` table; a durable per-page marker written **before** each page-advancing POST; `fill_form` drops to `max_attempts=1` with a `fill_error_handler` that may never re-enter a committed page; the "no POST" claim deleted and replaced by *no POST to an already-committed page*; the fake ATS becomes multi-page and AC-ID-23's fuzz kills between pages | §9.8 (new), §9.1, §9.2, §5.3, §5.5, §6.3, §6.4, §13.6, T-2.4a, T-2.5, T-2.6 |
| **C-2** | HITL-2 had no "I already submitted it"; `continue` re-ran `fill_form` from the top and fell through to a second click | `i_submitted` added to `await_blocker` as the **first** option, wired to the `await_handoff` handling; new `recheck_after_blocker` node re-runs pre-flight #3 and #5 before re-entering `fill_form`; `submit` re-asserts a page token + DOM fingerprint recorded at fill time | §5.3, §7.1, §9.3, §4.12, T-2.4c |
| **C-3** | `confirmed_not_submitted` authorised a second irreversible submission with less friction than editing one sentence | Typed `NOT SUBMITTED TO <company>` confirmation; 60-minute minimum from `click_dispatched_at` before the option is enabled; mandatory "I checked the ATS account" checkbox; irreversibility stated in the card and the Telegram message; `check_again_later` added; evidence capture 60 s → 180 s so slow successes stop being misreported as unknown | §9.5, §9.3, §7.1, T-2.4b |
| **C-4** | Pre-flight let the click proceed when it could not reach the posting, and the carve-out was internally incoherent | Amber-and-allow withdrawn: an unverifiable #3 is `still_active_unverified` → hard fail, retryable from the dashboard. #1/#2/#3 now behave alike. Pre-flight additionally renders as a *preview* before Approve, where a human still has a decision to make. No DEPARTURE id is needed — v2 no longer departs from FR-9.1 | §9.4 |
| **C-5** | The mapper agent ran on `.inner`, bypassing `PromptGuard`, `BudgetGate` and `SpendLedger` | `.inner` removed from `GuardedModel` and added to the static-check ban list; the wrapper itself is passed to `create_agent`; `GuardMiddleware` (`before_model`/`after_model`) enforces guard, budget and ledger inside the agent loop; `inspect_form` specified as a field-by-field projection, never a DOM serialisation, with a leak test | §5.4, §4.13, §12.5, T-0.3, T-3.8 |
| **C-6** | `kind="context"` claims escaped C9, C10 and C11 entirely | `context` defined narrowly (no assertion about the candidate) and enforced by new deterministic check **C14**, which reclassifies offenders to `self` *before* C9 runs; caps of ≤ 2 per letter and 0 per subjective answer, surfaced in the review UI; two of the 40 mutation fixtures re-cut as claim-kind mutations | §8.2, §4.10, §8.4, §8.5 |
| **C-7** | Answer-sheet and `learned` values reached employers but were structurally invisible to the HITL-5 reviewer | *Masked in transit, never masked from the reviewer*: the Answers tab renders every value in full to the loopback session; masking for prompts, traces, logs, Telegram and exports is unchanged; `learned` values pass FactGuard C3/C4/C6/C7/C13 on write and appear in the reviewed set for three reuses; pre-flight #9 fails on `unconfirmed`/`open` values; AC-HL-19 amended | §11.7 (new), §11.1, §11.4, §9.4, §7.1, §14.2 |
| **C-8** | Provenance anchored to derived positional keys over a master with no ids; fixing it was left optional in Q-O | T-0.4 promoted to a blocking prerequisite of Phase 1 and **Q-O ratified**; `build_ledger` refuses a mismatched master instead of deriving; keys content-anchored where cheap; master bytes persisted as `artefacts.kind='master_html'` with a new `ledgers` table; new AC requires a stored pointer to resolve to the same text or fail loudly; R-14 re-rated Critical / High | §4.4, §6.3, §6.4, §10.6, §16, §19, T-0.4 |
| **C-10** | No single-instance guard; reconciliation ran before the port bind and converted live `SUBMITTING` rows into `UNKNOWN_OUTCOME`, feeding C-3 | Named OS mutex as the **first** action of `jobagent serve`, before any database connection; port bind **before** reconciliation as a backstop; the `SUBMITTING` sweep now requires both a dead holder pid and a `submitting_written_at` older than the submit timeout; the browser worker fails loudly on a locked profile instead of restarting; AC-ID-08 extended to require the second process to write nothing | §3.2, §9.6, §4.12, §13.1, §12.5, T-0.7, T-2.6 |
| **C-11** | No `submission_enabled` master switch, which the test plan's own go-live gate presumes | `settings.submission_enabled: bool = False`, checked in `submit` gate (0) **and** in `commit_page` (because after C-1 the click is not the only irreversible act); typed confirmation to enable, audit row on every change, static check on the default; documents-only threads exempt; T-7.3 becomes the act of turning it on, with the 1/day ceiling as a second independent limit | §4.1, §9.3, §9.8, §12.5, §15, O7 |
| **M-1** | The §5.1 interrupt/retry `[UNVERIFIED]` was false, and the "defensive" mitigation was harmful | `interrupt()` bypasses retry policies and error handlers (`fault-tolerance.md` §389–391) — so `max_attempts=1` never provided interrupt protection and only removed genuine retries from seven HITL nodes. All `await_*` nodes return to the graph default | §5.1, §5.3, §5.5, §18 |
| **M-2** | The §6.5 checkpoint-pruning `[UNVERIFIED]` was false, and the instruction it justified was dangerous | Retention uses `await checkpointer.adelete_thread(thread_id)` (`checkpointers.md` §407, §544), falling back to `aprune`; hand-deletion from inferred tables removed; AC-NF-12 amended to assert the API was called | §6.5, §18 |
| **M-3** | The §5.4 `ToolCallLimitMiddleware` `[UNVERIFIED]` was false, and the default `exit_behavior` meant the 60-call limit did not stop the mapper | `ToolCallLimitMiddleware(run_limit=60, thread_limit=120, exit_behavior="error")`, with `ToolCallLimitExceededError` handled as an `unsupported_form` fallback | §5.4, §18 |
| **M-15** | AC-AF-22 was enforced by a node, not by the database, unlike its sibling invariant | `BEFORE UPDATE OF status … WHEN NEW.status='SUBMITTING'` trigger requires a matching `fact_checks` row with status `pass` / `pass_with_confirmed_edits`; added to the §6.4 table | §6.4 |
| **M-16** | `pass_with_confirmed_edits` overrode every fabrication class on a memorised constant phrase, and pre-flight re-checked only one of them | Overrides are scoped by class (§8.3): allowed for C9/C10/C12 and, per violation, C3; **never** for C1, C2, C4, C5, C6, C7, C8, C13, C14 — authorship is his, arithmetic and vocabulary are not. Confirmations become per-violation rows in a new `confirmations` table with a **generated** string naming the claim (*"I confirm: 5 years with LangChain"*) instead of a constant sentence. New pre-flight check **#13** recomputes C3/C4/C7 independently of `fact_checks.status`. Rolling override counts land in Reports | §8.3, §7.4, §6.3, §9.4, §13.5 |
| **M-19** | Ledger and master snapshots were never in the NFR-3 bundle, so reconstruction degraded to unusable after any master edit | C-8 made the master and ledger durable; v2.2 puts them **in the bundle**: `GET /applications/{id}/bundle` now ships the `master_html` artefact, the `ledgers` row for that application's `master_hash`, and its `confirmations` rows. New AC: edit the master, export a bundle for an application tailored before the edit, and assert every provenance pointer still resolves from the bundle alone | §7.1, §10.6 |
| **M-22** | The primary approve key advanced to the next application, chaining approvals and making the undo unreachable; nothing required the evidence to have been rendered | Bindings swapped — **`A` = Approve & stay**, `Shift+A` = Approve & next — and both defined in §14.2. `POST /decisions {approve}` returns **409 `tabs_unreviewed`** unless every tab with content was opened, with the tab set recorded on the decision row and surfaced in AC-NF-15 telemetry. The grace toast is addressed by `decision_id` and survives navigation, so `Z` works after advancing. Stated plainly as mitigation, not a fix: a `1`,`2`,`3`,`A` chord still defeats it, and R-3's residual stays Medium | §7.2, §14.2, §14.3, §6.3, §12.5 |
| **M-13** | AC-HL-26 could not pass — §4.1's `telegram.approve_enabled` let `/approve` record `approved_without_review`, disabling HITL-5 by a setting, while §12.5 asserted no such setting existed | **`/approve`, `approve_enabled` and `approved_without_review` are removed**, not documented. Q-I closed as "No"; §12.5's row becomes true; D-4 records that this departs from AC-HL-10/11 and resolves the test plan's own internal conflict in favour of AC-HL-26, which is the AC carrying the safety property. `/approve` now returns a dashboard link and records nothing | §4.1, §4.14, §7.3, §12.5, §17, §19 |
| *m-5* | The edit endpoints had no status guard — the path that made M-15 reachable | Edits require `status ∈ {PENDING_REVIEW, TAILORING_FAILED}`; anything later returns `409 not_editable`. Closed incidentally, because M-15's fix is incoherent without it | §7.4 |

**One thing this revision deliberately does *not* do.** It does not accept a criticism it believes
to be wrong without saying so — see §5.1's note on M-4, where v1's *rationale* is false but the
*rule* is retained, because removing it creates a contradiction that M-4 must resolve properly.

### v2.1 — Q-S answered, plan re-cut

v2.0 recorded the review's closing recommendation as **Q-S** and left it open, on the grounds that
re-scoping was Avadh's call rather than the spec's. It is now **decided: yes, ship the
non-submitting product first** (§15.0, §19).

What changed between v2.0 and v2.1 is not an opinion but a measurement. The discovery spike
(`spike/`) put a number on R-5, the risk the whole plan leaned on not firing: **~7 reachable
roles/week** on the Greenhouse/Lever adapters, an upper bound before the ≥ 70 rubric, against a
design whose ceiling is 10–20 applications *per day*. The follow-up slug verification closed the
obvious objection — **0 of 29 unresolved boards were wrong slugs**, so the number does not move by
tidying the seed list. Building the submission protocol, which carries every irreversible action
and five of the ten CRITICALs, to automate a handful of applications a week is not a good trade.

§15.0 carries the release split, and is candid about two things the review was not: deferring
submission saves only ~20% of implementer-days, and the larger lever on time-to-first-output is
the 19-screen SPA, which Release 1 cuts to four screens for what is a single-user system.

---

## 21. Findings not closed in v2

The review raised 46 findings. v2 closes **19** of them — the ten CRITICALs, eight MAJORs (M-1,
M-2, M-3, M-15 in v2.0; M-16 and M-19 in v2.2; M-22 and M-13 in v2.3) and one MINOR, all listed in
§20. **The remaining 27 are open, not resolved**, and this section exists so that no reader mistakes
a v2 badge for a clean bill of health. A re-review should assume every item below still stands.

**MAJOR, open (16).** M-4 (§5.1 forbids a graph-wide `error_handler` while §5.3 and §13.3 require
one; `BudgetHardStop` and `PauseRequested` are retried three times before any handler fires — v2
corrects the false *rationale* in §5.1 but not the contradiction) · M-5 (`is_pre_click_error`
cannot key the dispatch marker to an application) · M-6 (the post-click `except` awaits during
cancellation, and nothing sweeps rows stuck in `SUBMITTING` while the process stays alive) · M-7
(the `submit` timeout budget is not partitioned — v2 raises it to 300 s for C-3 but does not
partition it) · M-8 (a crash inside the 5-second grace window auto-submits on restart) · M-9
(AC-ID-25 is silently weakened) · M-9a (`spawn_apps` can relaunch a thread already under review) ·
M-10 (AC-SB-01's 60-second bound is unachievable with a serialised browser worker, and no
throughput budget exists) · M-11 (AC-HL-13 contradicts LangGraph resume semantics) · M-12
(AC-HL-17's "< 10% of forms halt" is unreachable under the spec's own defaults) · M-14 (AC-NF-04
fails by design and the exception is untagged) · M-17 (at the budget hard stop the reviewer can approve and reject but cannot
edit) · M-18 (a source that breaks silently is indistinguishable from a quiet day) · M-20 (phase
exit gates cite acceptance criteria that
later phases implement) · M-21 (the schedule is six to nine months for one person and never says
so) · M-22 (the primary approve key advances to the next application, chaining approvals and making
the undo unreachable) · M-23 (the budget hard stop is a floor, not a ceiling).

**MINOR, open (11).** m-1, m-2, m-3, m-4, m-6, m-7, m-8, m-9, m-10, m-11, m-12 — as listed in the
review report.

**What the Release 1 split does to this list.** The split itself closes nothing, and must not be
read as doing so. What it does is move most of them out of the critical path: M-5, M-6, M-7, M-8,
M-9, M-9a, M-10, M-11, M-14 and M-23 live in the submission protocol and the form-filling path,
which Release 1 does not build. They must be closed before Release 2 begins, and §15.0's entry
trigger is the point at which that work becomes due.

**Every MAJOR that sat inside Release 1's own path is now closed**: M-16 and M-19 in v2.2
(FactGuard's override and NFR-3 reconstruction, both Phase 1), M-22 and M-13 in v2.3 (the
rubber-stamping pair, both in the review screen Release 1 builds). That was deliberate sequencing —
each was cheaper to fix in the spec than in shipped code, and Phase 1 and the review screen are the
first two things Release 1 builds.

**What is not fixed is the thing R-3 has always named.** M-22 removes the cheapest rubber-stamping
path — approval without the evidence being rendered — and M-13 removes the flag that could disable
HITL-5 outright. Neither makes a careful reviewer out of a tired one. A `1`,`2`,`3`,`A` chord still
approves in four keystrokes, and under the thin-cut UI (§15.0) Approve is fewer keystrokes away than
it was, not more. Release 1's real backstop is structural rather than behavioural: it is
documents-only, so a rubber-stamped artefact is not sent anywhere by the machine — Avadh still has
to send it himself. **That backstop disappears in Release 2**, which is the strongest argument in
this document for not entering Release 2 casually.

**The reviewer's structural objection, unanswered.** The review's sharpest point is not on this
list, because it is not a defect to patch: *"The human cannot be made safe by measurement alone."*
The design's answer to rubber-stamping is telemetry — `review_seconds`, a median, a flag in a
report the reviewer writes for himself — while the primary approve key advances to the next
application (M-22), approval is reachable from tab 1 without ever rendering tab 3, and the undo
window is five seconds and is left behind by the very keystroke that starts it. v2 closes C-7, so
the reviewer can now *see* the values he is certifying, which was the most concrete part of that
objection. The rest — making Approve cost something proportionate to its consequence — is M-22,
M-13 and the UI work behind them, and it remains open.

---

*End of specification.*

# JobAgent — Technical Specification

**Project:** Autonomous AI/ML Job Search & Application Agent
**Owner:** Avadh Dobariya
**Inputs:** `docs/REQUIREMENTS.md` v0.5 (approved) · `docs/requirements-analysis.md` (assumption register §7 adopted; exceptions in §17) · `docs/test-plan.md` (277 acceptance criteria — every one must be satisfiable by this design) · `docs/ui-ux-design.md` (19 screens, FR→UI map) · `knowledge-base/` (LangChain 1.x / LangGraph API truth)
**Status:** Phase 3 — specification for implementation by Sonnet/Opus
**Version:** 1.0 · 2026-09-14

> This document says **how**. Every LangChain/LangGraph symbol named here was grepped in
> `knowledge-base/` before it was written down; §18 is the verification table. Anything that
> could not be verified is marked **[UNVERIFIED]** rather than asserted. Where this spec departs
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
| **No double submission, ever** (NFR-2, HITL-R5, C-3) | Three-state submission protocol in the tracker (`SUBMITTING` written durably *before* the click; `SUBMITTED` only after evidence is stored); a submit node that never clicks when it finds `SUBMITTING`; `RetryPolicy.retry_on` restricted to a `PreClickError` class; `UNKNOWN_OUTCOME` hands the question to a human and blocks dedup meanwhile. | §9 |
| **No fabrication, ever** (T-1..T-5) | A deterministic fact ledger built from the master resume; a generator that emits a *plan* (element keys + provenance pointers), never free HTML; a verifier (FactGuard) that runs on every artefact, fails closed, and blocks the `SUBMITTING` transition without a fresh pass on the exact artefact hashes. | §8, §10 |
| **Answer-sheet values never reach an LLM** (§2.1, NFR-7) | Values live in one table, are loaded only inside the deterministic `FormFiller`, never enter graph state (hence never checkpoints), and a `GuardedModel` wrapper asserts on every outbound prompt. | §11, §12 |
| **Review stays a 60-second task** (HITL-5, UI D-2) | Tailoring is reorder-first; only the professional summary may be rewritten; the change budget is enforced by the plan schema; the diff the reviewer sees is the diff the verifier checked. | §10 |

The runtime is one Python process (`jobagent serve`) hosting a FastAPI backend bound to
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
| O5 | Spend visible per stage; a runaway loop is caught at $5 and stopped at $20. | AC-FM-08..10, AC-NF-09 |
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
    daily_ceiling: int = 20           # 0..40 (UI §3.15); 0 allowed (AC-SB-20)
    models: dict[Stage, str]          # {"screen": ..., "analyse": ..., "generate": ..., "judge": ...}
    budget: Budget                    # soft_alert_usd=5, hard_stop_usd=20, ceiling_usd=100 (max)
    schedule: Schedule                # run_at="09:00", tz="Asia/Kolkata", catch_up_until="20:00", digest_at="21:00"
    geography_priority: list[str]     # FR-1.3 order; toggles
    strong_companies: list[str] = []  # A-12
    telegram: Telegram                # chat_id, approve_enabled=False, base_url="http://127.0.0.1:8765", stale_hours=48
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
test plan speak of "element ids". This spec therefore defines **element keys** computed
deterministically from document structure, and recommends (Phase 0 task T-0.4) adding matching
`id` attributes to the master — a zero-text-change edit verified by an identical text diff.

**Element key scheme** (document order; slugs from heading text):

| Key | Element |
| --- | --- |
| `hdr.name`, `hdr.role`, `hdr.tag`, `hdr.contact.{location,phone,email,linkedin,github}` | header |
| `summary.p1` | Professional Summary `<p>` |
| `exp.krista.h3`, `exp.krista.meta`, `exp.krista.li1..li4` | Work Experience |
| `proj.mcp.h3`, `proj.mcp.li1..li2` · `proj.aiqa.h3`, `proj.aiqa.li1` · `proj.grc.h3`, `proj.grc.li1` | Key AI Projects |
| `skills.s1..s7` (line) · `skills.sN.label` · `skills.sN.v1..vM` (comma-separated value) | Skills |
| `edu.p1` · `awards.p1` | Education, Awards |

Keys are stable as long as headings and element order are stable; the ledger records
`master_hash = sha256(resume-ats.html)` and every application stores the `master_hash` it was
tailored from (AC-AF-20).

**Interface.**
```python
class Fact(BaseModel):
    fact_id: str; klass: FactClass; value: str; qualifier: str | None; context: str; element_key: str
class Ledger(BaseModel):
    master_hash: str; facts: list[Fact]; technologies: set[str]; synonyms: dict[str, str]
    canaries: set[str]; organisations: set[str]; projects: set[str]; numbers: list[NumberFact]
    immutable: dict[str, str]        # title, date ranges, degree line, contact fields (byte-exact)
    scope_verbs: dict[str, int]      # verb → scope rank, from config (AC-AF-09)
def build_ledger(html: str) -> Ledger                  # byte-stable across runs (snapshot test)
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
    async def click_submit(self, page, selector) -> None            # the point of no return; see §9
    async def capture_evidence(self, page) -> Evidence
    async def screenshot(self, page) -> Path
```
**Behaviour.** One persistent context under `data_dir/browser-profile/` (cookies survive,
AC-SB-16). Headed (visible) so Avadh can take over; the worker never closes a page that is
blocked — it leaves it open, screenshots it, and the application thread interrupts at HITL-2.
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
channel `telegram`), `/pause`, `/resume`, `/status`; `/approve` only when
`telegram.approve_enabled` (default false) and then recorded `approved_without_review`
(AC-HL-10/11). **DEPARTURE D-4** from UI §7 principle 4 ("notify-only"): the test plan requires
Telegram reject to work; A-14 is adopted over the UI note.

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
| Retry defaults | `builder.set_node_defaults(retry_policy=RetryPolicy(max_attempts=3))`. **No graph-wide `error_handler`** — an `await_` node must never have a handler that could swallow the interrupt; handlers are attached per node | `fault-tolerance.md` §401 |
| Interrupt node retries | `retry_policy=RetryPolicy(max_attempts=1)` on every `await_` node. **[UNVERIFIED]** whether the interrupt control-flow exception is excluded from `default_retry_on`; disabling retries on those nodes removes the question | defensive |
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
                                 fill_form ──(blocker)──▶ notify_blocked ─▶ [await_blocker] ─▶ fill_form
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
| `await_question` | `interrupt({"kind":"hitl3", ...halts})` → stores answers/`skip_job` | – | **none before interrupt** | `max_attempts=1` |
| `tailor` | Build `TailoringPlan` (`generate`), `apply_plan`, write tailored HTML artefact | generate | artefact write | `timeout=300` |
| `render_check` | `render.py` subprocess; `ats_check`; artefacts | – | artefact write | `timeout=180` |
| `generate_letter` | `Letter` claims (`generate`) | generate | artefact | `timeout=300` |
| `generate_answers` | `SubjectiveAnswer` per subjective field (`generate`) | generate | artefact | `timeout=300` |
| `factguard` | §8 verifier; judge model for entailment | judge | `fact_checks` row, guard events | `timeout=300` |
| `repair` | Feed violations back; `repair_count += 1`; `Command(goto=<offending stage>)` | – | none | default |
| `notify_hitl4` / `await_hitl4` / `apply_hitl4_fix` | HITL-4 payload: sentence, fact class, nearest ledger facts; fix = use resume wording / edit / skip | – | outbox; none; artefact | – |
| `notify_review_ready` | Status `PENDING_REVIEW`; outbox is **batched** at supervisor level (M1 once per run) | – | upsert | default |
| `await_review` | `interrupt({"kind":"review", "application_id", "artefact_hashes"})` → `{type, decision_id, ...}` | – | **none before interrupt** | `max_attempts=1` |
| `record_decision` | Validates decision vs current artefact hashes; writes `decisions` row; status → `APPROVED` / `REJECTED_BY_USER` / re-queue | – | insert (idempotent by `decision_id`) | default |
| `preflight` | Twelve FR-9.1 checks §9.4; live re-fetch; status `PREFLIGHT_OK` | – | `preflight_results` rows | `timeout=120`, `retry_on=is_network_error` |
| `fill_form` | Browser: navigate, upload PDF, fill routed values (answer-sheet values loaded **here**, inside `FormFiller`, from the table); stop on blocker | – | browser only, no POST | `timeout=600` |
| `submit` | §9.3 protocol: read tracker state → write `SUBMITTING` → click → evidence → `SUBMITTED` | – | **the irreversible click** | `RetryPolicy(max_attempts=3, retry_on=is_pre_click_error)`, `timeout=TimeoutPolicy(run_timeout=180)`, `error_handler=submit_error_handler` |
| `notify_unknown` / `await_unknown` | Outbox (unknown outcome); `interrupt({"kind":"unknown_outcome", ...})` → `confirmed_submitted` / `confirmed_not_submitted` | – | outbox; none | `max_attempts=1` |
| `notify_handoff` / `await_handoff` | Assisted mode: M2-style message; `interrupt({"kind":"handoff"})` → `i_submitted` / `by_hand` / `abandon` | – | outbox; none | `max_attempts=1` |
| `notify_blocked` / `await_blocker` | HITL-2: screenshot ref, step; `interrupt({"kind":"blocked", ...})` → `continue` / `by_hand` / `abandon` | – | outbox; none | `max_attempts=1` |
| `await_pause` | `interrupt({"kind":"paused", "reason"})` → `Command(goto=state["resume_target"])` | – | none | `max_attempts=1` |
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
    model=get_model("analyse").inner,          # GuardedModel-wrapped provider model
    tools=[inspect_form, propose_mapping, request_human],
    system_prompt=FILL_MAPPER_PROMPT,
    middleware=[ToolCallLimitMiddleware(run_limit=60)],
    context_schema=FillContext,
)
```
The agent **never sees or emits a value**: `propose_mapping` takes a *route* (e.g.
`answer_sheet:expected_ctc`), and the deterministic `FormFiller` resolves the route to a value
outside the model loop. That is what makes A-6 hold even where an LLM is in the loop. No
`submit` tool exists in this agent — the click is in the `submit` node, not a tool call, so
`HumanInTheLoopMiddleware` is **not** needed here (the analysis §5.11 suggestion is superseded by
the stronger separation; the middleware stays available if a future ATS needs an in-agent
irreversible action).

`ToolCallLimitMiddleware` is verified in `middleware__built-in.md` (name only; constructor
parameters **[UNVERIFIED]** — the implementer must read the page for the exact kwargs).

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
builder.add_node("await_review", await_review, retry_policy=RetryPolicy(max_attempts=1))
builder.add_node("submit", submit,
                 retry_policy=RetryPolicy(max_attempts=3, retry_on=is_pre_click_error),
                 timeout=TimeoutPolicy(run_timeout=180),
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
reachable only from `fill_form`.

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

**artefacts** — `id (sha256[:16]), kind (jd|form_model|tailored_html|pdf|letter|answers|screenshot|evidence|factguard|preflight|plan), sha256 FULL, bytes INT, path, created_at`. Content-addressed; two applications never share a path by accident (AC-RT-13).

**answers** — `application_id, version_id, field_id, label, field_type, route, source (resume:<key>|answer_sheet:<field>|jd:<span>|human:<decision_id>|profile), value_ref (artefact) NULL for answer_sheet routes, halted BOOL`. **Answer-sheet values are never stored here** — `route` names the field; the value is resolved at fill time (AC-CL-18, AC-NF-05).

**decisions** — `id, application_id, interrupt_kind, interrupt_id, type (approve|reject|regenerate|postpone|edit|hitl3_answer|hitl4_fix|continue|by_hand|abandon|confirmed_submitted|confirmed_not_submitted|i_submitted|approved_without_review), reason_code, reason_text, channel (dashboard|telegram|system), actor (session id | chat_id), artefact_hashes JSON, confirmation_text, at`. `UNIQUE(application_id, interrupt_id)` → second decision returns "already decided" (AC-HL-08, AC-ID-07).

**preflight_results** — `id, application_id, version_id, run_at, check_name (12 enums), passed BOOL, evidence TEXT`. (AC-SB-01)

**submission_evidence** — `application_id, attempt INT, submitting_written_at, click_dispatched_at, final_url, page_text_excerpt, screenshot_ref, http_status, confirmation_kind (page_text|url|email_hint|human), captured_at`. Written in the **same transaction** as the `SUBMITTED` transition (AC-SB-12).

**transitions** — `application_id, from_status, to_status, at, by (node name | api | reconcile), detail JSON`. (TR-7, AC-TK-11)

**fact_checks** — `id, application_id, version_id, artefact_hashes JSON, status (pass|fail|pass_with_confirmed_edits), violations JSON, judge_model, at`. Pre-flight requires a row whose `artefact_hashes` equal the current version's (AC-AF-22).

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
| No answer-sheet values outside their table | `answers.value_ref` must be NULL when `route LIKE 'answer_sheet:%'` (CHECK) |

### 6.5 Retention

Records are kept forever (Q-9). `retention_job` (03:00 daily): delete checkpoints for threads
whose application reached a terminal status ≥ 30 days ago, via the checkpointer's tables by
`thread_id` (**[UNVERIFIED — `langgraph-checkpoint-sqlite` has no documented delete-thread API in
the knowledge base; the implementer deletes rows from the saver's tables by `thread_id` and must
confirm table names against the installed package]**), then `VACUUM` `checkpoints.db` (AC-NF-12).

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
| Review (3.4–3.6) | `GET /applications/{id}/review` → job rail, score, flags, watch items, pre-flight preview, versions; `GET /applications/{id}/diff` → structural diff (change classes); `GET /applications/{id}/letter` → claims with provenance; `GET /applications/{id}/answers` → routed answers (answer-sheet rows show **field name only**); `GET /artefacts/{id}` (PDF/HTML download); `POST /applications/{id}/reveal-answer` (transient; audited) |
| Decide (5.1) | `POST /applications/{id}/decisions` `{type: approve|reject|postpone|regenerate|dismiss_expired, reason_code?, reason_text?, artefact_hashes}` → `202 {decision_id, effective_at}`; `POST /applications/{id}/decisions/{decision_id}/undo` (within grace) |
| Edit (3.7) | `PUT /applications/{id}/letter` `{claims}`, `PUT /applications/{id}/resume-text` `{block_edits}`, `PUT /applications/{id}/answers/{field_id}` `{text}` → each returns new `version_id`, `fact_check`, `ats_report?`, `preflight_preview`; `POST /applications/{id}/revise` `{instruction}` → agent revise (costs; returns estimate first with `?estimate=1`); `POST /applications/{id}/confirm-edit` `{confirmation_text}` (AC-AF-19) |
| Reject overlay (3.8) | part of decisions; `reason_code ∈ {not_relevant, weak_fit, company, location, regenerate, other}`; reject without reason → `400` (AC-HL-04) |
| Audit › Sources/Queries (3.9) | `GET /runs/{date}/sources`, `GET /runs/{date}/queries`, `POST /runs/{date}/sources/{source}/retry` |
| Audit › Jobs (3.10) | `GET /runs/{date}/jobs?verdict&source&tier&geo&fallback_state&q` (paginated, < 1 s at 500 rows — AC-DS-12); `POST /jobs/{id}/fallback-state` `{state, note, applied_at?}` |
| By hand (3.11) | `GET /fallback?state=pending&runs=all`; `POST /jobs/{id}/fallback-state`; `POST /jobs/{id}/prepare-documents` (spawns documents_only thread; returns cost estimate on `?estimate=1`); `POST /applications/{id}/resume-with-agent` (HITL-2 continue) |
| Tracker (3.12) | `GET /applications?status&channel&tier&geo&from&to&follow_up_due`; `GET /applications/{id}` (expansion: URL, dates, versions, answers, key skills); `PATCH /applications/{id}` `{outcome?, notes?, follow_up_date?}`; `GET /applications/{id}/bundle` → NFR-3 reconstruction (zip of PDF, HTML, letter, answers with sources, form payload record, evidence, score, decisions); `GET /applications.csv` |
| Job detail (3.13) | `GET /jobs/{id}` → score breakdown, hard rules with spans, dedup cluster, timeline, JD text with highlighted spans, scored-by/cost; `POST /jobs/{id}/promote` (soft rejections only — §17 D-6; `409` for hard rules); `POST /jobs/{id}/rescore` |
| Settings › Answer sheet (3.14) | `GET /answer-sheet` (masked; usage counts; impact box `GET /answer-sheet/work-auth-impact`); `POST /answer-sheet/reveal` (returns values once; audited); `PUT /answer-sheet/{key}`; `GET/PUT /answer-sheet/years-by-technology` |
| Settings › Targets, Models, Sources, Schedule, Notifications, Data (3.15–3.16) | `GET /settings`, `PUT /settings` (validated; `409` on version mismatch); `GET /settings/models/usage-today`; `GET/PUT /watchlist`, `POST /watchlist/import`; `POST /telegram/test`; `GET /data/summary`, `POST /data/export` |
| Reports (3.17) | `GET /reports/{date}` (morning + evening), `GET /reports/trend?days=14`, `GET /reports/{date}.txt` |
| Runs (3.18) | `GET /runs/{date}` → stages, per-stage cost, live step, events, secrets-guard counter; `GET /runs/{date}/events?level`; `GET /traces/{thread_id}`; `POST /runs` (run now) → `202` or `409 lock_held`; `POST /runs/{id}/resume` |
| Needs-you-now (3.19) | `GET /needs-you` → blocked (HITL-2), questions (HITL-3), claims (HITL-4), unknown outcomes, failed submissions; `POST /applications/{id}/hitl3` `{answers: [{field_id, text, save_as?}], skip_job?}`; `POST /applications/{id}/hitl4` `{action: use_resume_wording|edit|skip_job, text?}`; `POST /applications/{id}/blocker` `{action: continue|by_hand|abandon}`; `POST /applications/{id}/take-over-browser` (brings window to front); `POST /applications/{id}/unknown-outcome` `{outcome: confirmed_submitted|confirmed_not_submitted}`; `POST /applications/{id}/handoff` `{action: i_submitted|by_hand|abandon}` |
| Controls (UI-13) | `POST /control/pause`, `POST /control/resume`, `GET /control` |
| Guard events (UI-11) | `GET /audit-events?kind=guard&from&to` |

### 7.2 Decision semantics (the contract the graph relies on)

```
POST /applications/{id}/decisions {type: approve, artefact_hashes}
  1. Load application; require status ∈ {PENDING_REVIEW}; else 409 {code: "not_pending"}.
  2. Require a pending interrupt on the thread (aget_state → tasks[*].interrupts non-empty, kind=review); else 409.
  3. Compare artefact_hashes with current version's hashes; mismatch → 409 {code: "stale_artefacts"} (reviewer reloads).
  4. Require fact_checks row for these hashes with status pass|pass_with_confirmed_edits; else 409 {code: "fact_check_required"} — and Approve is disabled in the UI anyway.
  5. INSERT decisions (interrupt_id = pending interrupt id). UNIQUE violation → 200 {already_decided: true, decision_id}.
  6. Transition PENDING_REVIEW → APPROVED_GRACE (effective_at = now + 5 s). Emit SSE.
  7. After effective_at, resume_worker: acquire thread lock → ainvoke(Command(resume={...decision}), config, durability="sync").
Undo within grace: DELETE decision row + APPROVED_GRACE → PENDING_REVIEW. After grace: 409 {code: "already_submitting"}.
```
`reject` skips the grace window and resumes immediately; `postpone` and `dismiss_expired` are API-only
(no resume; `dismiss_expired` transitions to `EXPIRED` and cancels the thread by resuming with
`{type: "expired"}` so the thread reaches `finalize`).

`POST /applications/{id}/hitl3` etc. follow the same pattern: validate pending interrupt kind,
insert decision (idempotent), resume. Malformed payloads → `400` with no state change (AC-HL-23).
Decisions for terminal or unknown threads → `404`/`409` (AC-HL-07).

### 7.3 Telegram command mapping

`/reject <short_id> <1-6> [text]` → same handler as the dashboard reject with `channel=telegram`.
`/approve <short_id>` → if `telegram.approve_enabled` false: reply with dashboard link; else record
`approved_without_review` and proceed. `/pause`, `/resume`, `/status`. Everything else → help.
Sender check precedes parsing.

### 7.4 Edit pipeline (server side)

```
PUT /applications/{id}/letter {claims}
  → validate claim schema (provenance present or kind=context)
  → FactGuard.check(letter=claims, tailored=current, answers=current)  (synchronous, judge model)
  → new application_versions row (created_by=edit) + artefacts + fact_checks row
  → if fail: response includes violations; application flag `needs_confirmation`; Approve stays disabled
     until POST /confirm-edit {confirmation_text == "I confirm this statement is true"} → fact_checks.status = pass_with_confirmed_edits (A-20, AC-AF-19)
PUT /applications/{id}/resume-text {block_edits: [{element_key, new_text}]}
  → apply to tailored HTML (text nodes only; structure immutable) → render.py → ats_check → FactGuard → new version
```
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
           ──▶ C13 mandatory-gap claims ──▶ result {status, violations[]}
 Deterministic C1–C9, C12–C13 (no model). C10–C11 use the `judge` stage. Any single violation → fail.
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
- **Guard events**: every violation → `audit_events(kind='guard')` with job, rule, text,
  outcome (repaired / paused_hitl4 / rejected / confirmed_by_user) (AC-AF-23).

### 8.4 Testing the verifier harder than the generator

FactGuard ships with its own fixture suite: 40 seeded fabrications (one per fact class and
sub-rule) must all be flagged with the correct `fact_class` (AC-AF-15, 40/40 or the build
fails), and 10 legitimate tailorings plus the unmodified master must produce 0 flags (AC-AF-16).
The synonym and canary tables are versioned; a change to either re-runs the suite.

### 8.5 How the UI plugs in

| UI element | Data |
| --- | --- |
| Resume tab diff (`−/+`, `~↑↓`, `·`) | `GET /applications/{id}/diff` = C1's change list; a `violation` class renders red and disables Approve |
| Skills "reordered · nothing added" | C1 result for `.skill` lines |
| Pre-flight "facts 49/49", "no fabrication", "no false qualification" | `fact_checks.status`, C3–C8 counts, C13 |
| Letter `[n]` markers; unresolved marker red | `Claim.provenance` and C9/C10 per claim; `kind=context` markers grey |
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
                                                    PREFLIGHT_OK ──blocker──▶ BLOCKED ──continue──▶ PREFLIGHT_OK
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
        evidence = await bw.capture_evidence(page, timeout_s=60)   # final URL, confirmation text, screenshot, status
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

**Timeouts.** `TimeoutPolicy(run_timeout=180)` covers the whole node. A timeout during (2) is
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
| 3 | `still_active` | HTTP 200, no closed marker, not redirected to careers home | `EXPIRED` |
| 4 | `score_sufficient` | `applications.score_total ≥ 70` re-read from DB | `PREFLIGHT_FAILED` |
| 5 | `not_duplicate` | Tracker query for same identity / company+title-family with applied-class status other than this application | `PREFLIGHT_FAILED` |
| 6 | `resume_hash_matches_approved` | sha256 of PDF on disk == `decisions.artefact_hashes.pdf` | `PREFLIGHT_FAILED` |
| 7 | `no_fabrication` | `fact_checks` row with status pass/pass_with_confirmed_edits for exactly these hashes | `PREFLIGHT_FAILED` |
| 8 | `letter_tailored` | Letter present iff form has letter field; hash matches approved | `PREFLIGHT_FAILED` |
| 9 | `answers_accurate` | Answers hash matches approved; every route resolvable now (answer-sheet keys still exist) | `PREFLIGHT_FAILED` |
| 10 | `contact_correct` | Profile fields to be filled equal §2 constants | `PREFLIGHT_FAILED` |
| 11 | `location_acceptable` | Eligibility rules 10–12 recomputed from stored facts + current settings | `PREFLIGHT_FAILED` |
| 12 | `no_false_mandatory_claim` | C13 recomputed against the job's `mandatory` list | `PREFLIGHT_FAILED` |

All 12 rows are stored with evidence (AC-SB-01); the whole pre-flight completes within 60 s of
the click (`fill_form` and `submit` follow immediately; the browser worker queue is FIFO). Check
3 that *cannot reach* the posting (network) is recorded `unverified` and shown amber; approval is
still allowed with the warning (UI §4 pre-flight partial state) — but a definite closed marker is
a hard fail.

### 9.5 `UNKNOWN_OUTCOME` resolution

The `await_unknown` node holds the thread. Telegram + dashboard show the job link, the last
screenshot, the exact timestamps of `submitting_written_at` and `click_dispatched_at`, and the
instruction "check the ATS / your inbox for a confirmation". Meanwhile dedup treats the job as
applied (§4.3 rule 4). Resolution:

- `confirmed_submitted` → `SUBMITTED` with `confirmation_kind=human`; evidence row records the
  human confirmation (AC-ID-04 second branch).
- `confirmed_not_submitted` → `APPROVED` with `submit_attempt+1` → `preflight` → `fill_form` →
  `submit`, whose gate (1) now sees `PREFLIGHT_OK` and may click exactly once.

There is no auto-resolution and no timeout on `UNKNOWN_OUTCOME`.

### 9.6 Startup reconciliation (crash recovery)

On `jobagent serve` start, before the API accepts requests:

1. Acquire `locks.run` if stale (heartbeat older than 5 min) → mark the previous run `aborted`,
   mark its audit rows `run_aborted`.
2. For every application with status in `{SUBMITTING}` → transition to `UNKNOWN_OUTCOME`
   (detail `process_died_during_submit`), enqueue the unknown-outcome notification. The graph
   thread, when resumed, hits gate (1) and lands in `await_unknown`.
3. For every application with a non-terminal status: `snapshot = await graph.aget_state(config)`.
   If a task has pending `interrupts` → nothing to do (dashboard shows it). Else if
   `snapshot.next` non-empty → `ainvoke(None, config, durability="sync")` under the thread lock
   (bounded concurrency; browser-dependent nodes queue on the worker).
4. `APPROVED_GRACE` rows older than the grace window → treated as approved: resume.
5. Verify the checkpointer file is writable and not locked by another process; refuse to start
   otherwise (AC-FM-14).

### 9.7 Assisted mode (Workday)

`fill_form` opens the tenant page, uploads the PDF, pre-fills every mappable field, and stops at
the first account/verification step or unmappable required field → `notify_handoff` →
`await_handoff`. Avadh completes and clicks submit in the visible browser. On the dashboard he
records `i_submitted` (→ `SUBMITTED`, `confirmation_kind=human`, evidence = his statement +
screenshot) or `by_hand`/`abandon`. The agent never clicks in assisted mode (AC-SB-13). HITL-1
is satisfied by the earlier approval; the human click is the submission.

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
≈ $x" (UI §5.3). The ledger is rebuilt per `master_hash` and cached.

---

## 11. Form filling, the answer sheet and `years_by_technology`

### 11.1 Principle

Two independent guarantees:
1. **Answer-sheet values never enter an LLM prompt** — enforced by data placement (values live
   only in `answer_sheet`, are read only by `FormFiller.fill_value`, are never put in graph
   state, artefacts, logs, notifications or API responses other than the reveal endpoint) and
   by `PromptGuard` scanning every outbound prompt (AC-NF-04/05, AC-CL-10/11).
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
external proofs; CTC may appear in exactly one place — the encrypted `form_payload` blob of the
submission evidence, masked in the UI.

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
| HITL-1 / HITL-5 cannot be disabled | No setting, flag or env var exists; `record_decision` requires a `decisions` row; the graph has no edge from `notify_review_ready` to `preflight` (AC-HL-26) |
| Discovery-only sources never submit | `SourceAdapter.policy` is a class attribute; `selection` never creates a submitting application for `discovery_only`; `submit` refuses if `applications.channel` is not in `{greenhouse, lever, career_page}` (AC-SB-15) |
| No bulk approve | No endpoint accepts a list of approvals; the UI has no control (UI D-6) |
| Hard rejections have no override | `POST /jobs/{id}/promote` returns `409` for `reason_enum` in the FR-4.1/4.2/5.1 sets |

---
## 13. Operations

### 13.1 Scheduling (FR-12.1, Q-6, A-19, G-I1)

| Element | Design |
| --- | --- |
| Service start | Windows Task Scheduler task `JobAgent` → `jobagent serve` at user logon, restart on failure. The dashboard, Telegram and approvals need the process alive all day, so the *service* is what Task Scheduler owns, not the run. |
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
| Network lost mid fill | `PreClickError`; thread resumes at `fill_form`; no POST (FM-05) |
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
| S3 | Review — Resume diff (3.4) | `/queue/:appId` tab 1 | `/applications/{id}/review`, `/diff` | `A`, `Shift+A`, `E`, `R`, `P`, `X`, `Z`, `1/2/3`, `D`, `J/K`, `O`, `Shift+O` |
| S4 | Review — Cover letter (3.5) | tab 2 | `/letter` (claims + provenance) | `Tab` cycles markers, `⏎` jumps |
| S5 | Review — Answers (3.6) | tab 3 | `/answers` (field names for answer-sheet rows) | `Ctrl+Shift+V` transient reveal |
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

`review_started_at` on opening a review; `review_seconds` on decision → Reports "Your review
today" (median time, reject-reason distribution, UI §3.17) — the instrument for §9 "minutes not
hours" and for detecting rubber-stamping (AC-NF-15). Callback rate from tracker `outcome`.

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

### Phase 0 — Foundations (exit: repo builds, static checks run, master snapshot recorded)

| Task | Description | Cx |
| --- | --- | --- |
| T-0.1 | Repo layout `src/jobagent/`, `tests/`, `fixtures/`, `config/`; pyproject with pinned `langchain>=1.3.3`, `langgraph>=1.2`, `langgraph-checkpoint-sqlite`, `langchain-anthropic`, `langchain-openai`, FastAPI, Playwright, SQLAlchemy, pdfminer.six, pypdf, PyMuPDF | S |
| T-0.2 | `config` module: `Settings`, `Stage`, `prices.yaml`, `synonyms.yaml`, `canaries.yaml`, `field_ontology.yaml`, banned-filler list; registry-scoped secret loading via `winreg` | M |
| T-0.3 | Static checks: import lint (AC-NF-11), `InMemorySaver` ban (AC-ID-24), interrupt rules (AC-ID-13/14), topology (AC-ID-25), path length (AC-FM-19), `GuardedModel`-only calls | M |
| T-0.4 | Element-key scheme + recommended `id` attributes on `resume-ats.html` (zero text change; verify by text diff); rebuild PDF; three-parser test unchanged | S |
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
| T-2.4 | `submit` node protocol §9.3 + `PreClickError`/`PostClickError` + `submit_error_handler` | L |
| T-2.5 | Fake ATS with POST counter and fault modes; fake boards | M |
| T-2.6 | Fault injector harness (subprocess kill at named points); AC-ID-02..06, AC-ID-09..11, AC-ID-23 (200-run fuzz) | L |
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
| T-3.8 | Career-page mapper `create_agent` with route-only tools and `ToolCallLimitMiddleware` | M |
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
| T-7.3 | Supervised first live week: ceiling 1/day, ATS confirmation reconciliation daily; raise only after 5 clean days | M |
| T-7.4 | Month-2 metrics: rescue events, callback rate | S |

**Totals:** 60 tasks (8 S · 27 M · 22 L · 3 XL). Summing the complexity bands gives ≈ 115–190
implementer-days; the safety core (Phases 1–3, 27 tasks) is roughly half of that. Phases 1–3 are
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
| R-5 | **Discovery yield too low** on the submit-capable sources because the watchlist is empty / boards are sparse | High | High initially | Seed list (Q-B), auto-grow from aggregators, per-source yield in the audit log to steer effort | Medium |
| R-6 | **Aggregator scraping is challenged/banned** (LinkedIn/Naukri/Indeed) | Medium | High | Logged-out only, 24 h back-off, best-effort; never the personal session; measured yield decides whether to keep | Medium |
| R-7 | **Workday assisted mode still consumes Avadh's time** | Medium | High | Explicit assisted flow with pre-fill; by-hand fallback; promote to automation only if audit shows a repeatable pattern | Medium |
| R-8 | **Career-page forms too varied** — `supported_ratio` < 0.9 on most | Medium | Medium | Mapper agent (route-only tools) + fallback with prepared documents (D-3) | Medium |
| R-9 | **Model/provider drift** (model ids retired; structured-output behaviour differs per provider) | Medium | Medium | Stage strings in settings; `with_structured_output` tests per configured model; V-level nightly evals; fallback provider configurable | Low |
| R-10 | **Checkpoint DB growth / corruption** | Medium | Low | Small state (ids only); 30-day pruning; `synchronous=FULL`; boot check refuses corrupt file | Low |
| R-11 | **PC asleep / service not running** → silent missed days | Medium | High | Catch-up rule, M8 at 09:15, header missed state, Task Scheduler restart | Low |
| R-12 | **`render.py`/Chromium path drift** breaks tailoring | Low | Medium | `PW_CHROME` override; `TAILORING_FAILED` isolates; alert | Low |
| R-13 | **Judge model cost** on 10–20 apps × ~15 claims/day | Low | Low | Judge on `analyse` tier; batched per artefact; well under $5/day | Low |
| R-14 | **Element keys drift** if headings are edited in the master | Medium | Low | Keys derive from heading slugs; recommended `id` attributes make them explicit; ledger snapshot test fails loudly | Low |
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
| D-4 | UI §7 principle 4 "Telegram notify-only" | Telegram supports `/reject`, `/pause`, `/resume`; `/approve` behind an off-by-default flag | A-14 and AC-HL-10/11 require it; approve stays dashboard-only by default |
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
| `ToolCallLimitMiddleware`, `ModelRetryMiddleware`, `ModelFallbackMiddleware`, `PIIMiddleware(... strategy=block|redact|mask|hash, detector=...)` | `langchain/middleware__built-in.md` |
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
endpoints, Windows Task Scheduler options, `winreg`, checkpoint table names for pruning,
`ToolCallLimitMiddleware` constructor kwargs, whether the interrupt control-flow exception is
excluded from `default_retry_on`.

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
| Q-I | Approve from Telegram? | Off (reject only) | One-tap approve is spot-checking by another name |
| Q-J | Repost block window? | 180 days | — |
| Q-K | Expected CTC in AED/EUR/CAD? | HITL-3 | Add per-currency answer-sheet keys |
| Q-L | Auto-select "prefer not to say" on EEO? | Yes | — |
| **Q-M (new)** | Accept D-3 (documents-only tailoring for fallback jobs ≥ 80) and its review-time cost? | Yes, threshold 80, counted against ceiling | Off → by-hand list has no downloads |
| **Q-N (new)** | Accept D-6 (no promote-to-queue for score < 70)? | Yes | Allowing it breaks the §9 zero-below-threshold metric |
| **Q-O (new)** | May the master `resume-ats.html` receive `id` attributes matching the element keys (zero text change)? | Recommended; ledger works without them | Without ids, key stability depends on heading text |
| **Q-P (new)** | Data directory `%LOCALAPPDATA%\JobAgent` acceptable (D-5)? | Yes | Repo-relative path risks OneDrive sync and long paths |
| **Q-Q (new)** | Default `generate` model — confirm the strongest currently available Anthropic model id at build time (only `claude-opus-4-8` appears in the knowledge base) | `anthropic:claude-opus-4-8` | Config change only |
| **Q-R (new)** | Bounded parallel tailoring (2 concurrent application threads) acceptable, or strictly serial for easier hand-off? | 2 | Serial lengthens the 09:00 run; parallel complicates HITL-2 browser hand-off (browser worker is serial regardless) |

---

*End of specification.*

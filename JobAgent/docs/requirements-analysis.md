# JobAgent — Requirements Analysis

**Input:** `docs/REQUIREMENTS.md` v0.4 (2026-09-14), `knowledge-base/CORE-CONCEPTS.md`, `knowledge-base/langgraph/interrupts.md`, `knowledge-base/langchain/human-in-the-loop.md`, `knowledge-base/langgraph/checkpointers.md`, `resume/README.md`, `resume/resume-ats.html`
**Role:** System architect — analysis phase. This document does **not** design the system.
**Companion:** `docs/test-plan.md` (acceptance criteria, written before design)
**Status:** Draft for review

> Every requirement in v0.4 is restated below with an interpretation and a testability verdict.
> Where the requirements document contradicts itself, is silent on something load-bearing, or
> asks for something that will not work well, that is said plainly with an alternative. Nothing
> here is a transcription.

---

## 0. How to read this document

| Column | Meaning |
| --- | --- |
| **Interpretation** | What the spec will take the requirement to mean. If Avadh disagrees, this is the line to correct. |
| **Testable** | **Y** — verifiable as written · **P** — verifiable once a named term is defined (the definition is proposed in §3 or §7) · **N** — not verifiable by the system (process requirement, or unmeasurable) |
| **Test refs** | Acceptance-criteria groups in `test-plan.md` |

Requirement counts restated: **43 FR · 11 HITL (6 gates + 5 R-rules) · 5 T · 12 TR · 7 NFR · 6 C = 84**, plus the scoring rubric, thresholds, §9 success metrics and the §10 decisions/assumptions (§1.7).

---

## 1. Complete restatement

### 1.1 Functional requirements

#### 4.1 Discovery

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-1.1** | Every day, search LinkedIn, Indeed, Wellfound, Naukri, Greenhouse, Lever, Workday and direct career pages for newly posted and still-active roles. | "Search" ≠ "apply". Q-3 makes LinkedIn / Naukri / Indeed (and by omission Wellfound) discovery-only. Greenhouse / Lever / Workday are not boards but ATS platforms — "searching" them means querying each target company's board endpoint (e.g. `boards.greenhouse.io/<company>`), which requires a **company list** the requirements never provide (G-C11). | P | DS |
| **FR-1.2** | Prefer direct career pages and ATS links over aggregators. | When the same job is found on an aggregator and on an ATS, the ATS record is canonical and the ATS URL is the apply target. Aggregator-only jobs are kept but marked. | Y | DS, DD |
| **FR-1.3** | Location priority: Remote → Pune → Bengaluru → Hyderabad → Mumbai → Delhi NCR → other Indian hubs; plus Dubai/UAE, Europe, Canada; international remote only where the posting permits working from India. | Priority feeds the 5-point location dimension and tie-breaking. Whether a posting "permits candidates working from India" is an LLM extraction with three outcomes — yes / no / unstated. The **unstated** case is undefined (G-C10). | P | SC, HR |
| **FR-1.3a** | For every international role, extract visa / work-authorisation requirements and whether sponsorship is offered; reject (FR-4.2) roles that require authorisation Avadh lacks and do not sponsor. | Eligibility = f(extracted requirement, extracted sponsorship, configured `work_authorisation`). Default config: Indian citizen, no foreign permit, sponsorship required. "Sponsorship unstated" must be defined (default: treat as **not offered** for Europe/Canada, **offered** for UAE where visa-on-hire is normal — see §7). | P | HR |
| **FR-1.4** | Target Senior / Staff / Lead / Senior IC / Architect. Mid-level only for exceptionally strong companies. Never junior, entry, intern, graduate, trainee. | Seniority is read from the JD (years, scope), not the title alone (FR-3.2). "Exceptionally strong company" is undefined (G-I3). | P | HR, SC |
| **FR-1.5** | Query the §4.1.1 titles crossed with GenAI keywords (RAG, LLM, Agentic AI, MCP, GenAI, AI Agents, LangChain, LangGraph, LLMOps, Enterprise AI); include both `Forward Deployed` and `FDE`. | The query matrix is generated, not hand-written, and every issued query is logged (FR-1.8). Per-source query budgets are needed for NFR-5. | Y | DS |
| **FR-1.6** | An FDE role qualifies only with substantial GenAI/LLM work; otherwise it is non-AI software delivery under FR-4.1. | "Substantial" = the JD's core responsibilities name LLM/GenAI/agent work, not a passing "exposure to AI a plus". Encoded as a rubric rule, verifiable on fixtures. | P | HR, SC |
| **FR-1.7** | Extract travel %, onsite expectation and client-site base for FDE roles; surface before applying; treat "relocate abroad" under FR-1.3. | Three nullable fields on the job record, shown in the approval view. | Y | SC, UI |
| **FR-1.8** | Per run, log every source queried, every query issued, every job found with score, verdict and — where not applied — the reason. | One append-only audit table keyed by `run_id`. "Reason" is an enum plus free text so it is filterable. | Y | DS, UI |
| **FR-1.9** | The audit log is the manual-fallback surface: any job the agent could not auto-apply to (discovery-only source, CAPTCHA, unsupported form, missing data) appears there, filterable, with a working link and an Avadh-settable state `pending` / `applied manually` / `skipped`. | `applied manually` must feed FR-2.2 — a manually applied job is a duplicate for all future runs. That link is implied, not stated. | Y | DS, DD, UI |

**§4.1.1 target titles** — restated as a controlled list plus the clause "closely related titles qualify if the responsibilities genuinely match", which is an LLM judgement and therefore only testable on a fixture set (P).

#### 4.2 Deduplication

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-2.1** | One position on several boards is one job. | A job record has one identity and *n* source URLs. | P — needs the identity definition (G-C9) | DD |
| **FR-2.2** | Never apply to the same position twice; check the tracker before every application. | The check is a **pre-submit gate inside the submit path**, not a discovery-time filter only. It must also cover `applied manually` (FR-1.9). | Y | DD, ID, SB |
| **FR-2.3** | Identity survives differing titles, reposts and differing board URLs for the same ATS listing. | Needs a canonical identity: ATS job id when present, else normalised (company, title-family, location) plus JD-text similarity. A repost with a new ATS id but near-identical JD is the same position. Whether a *genuinely new* opening 6 months later is "the same position" is undefined (G-C9). | P | DD |

#### 4.3 Evaluation and scoring

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-3.1** | Score every discovered job 0–100 on the seven-dimension rubric. | Structured output with per-dimension sub-scores whose sum is the total; each capped at its weight. | Y | SC |
| **FR-3.2** | Score from the JD body, never the title. | Scoring must fail closed when the JD body is unavailable (blocked fetch, login wall) — the job is queued as `jd_unavailable`, not scored. | Y | SC |
| **FR-3.3** | Rank by the §2 differentiators. | The ranked differentiator list is a configured input to the scoring prompt and the tie-break order. | P | SC |
| **FR-3.4** | Record score and reasoning for every job including rejected ones. | Hard-rejected jobs still get a reasoning string (the rejection rule fired) even if the rubric was skipped. | Y | SC, UI |

**Rubric weights** (30/25/15/10/10/5/5) and **thresholds** (≥90 Tier 1, 80–89 Tier 2, 70–79 Tier 3 "apply only if no obvious qualification gaps", <70 do not apply) are restated as configuration with defaults. "Obvious qualification gaps" is undefined (G-I2). "Apply immediately" for Tier 1 cannot literally hold — HITL-1 and HITL-5 apply to every tier (§5.9).

#### 4.4 Hard rejection

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-4.1** | Reject with no scoring override when: clearly junior · primarily non-AI software · primarily data analytics · primarily DevOps · primarily traditional ML with no meaningful GenAI/LLM component *(unless overall match is exceptional)* · expired · already applied · fraudulent/suspicious. | The parenthetical **is** a scoring override and contradicts "no scoring override". Interpretation: the traditional-ML clause becomes a *flag for human decision* rather than an auto-reject or an auto-pass (§5.4). "Expired" needs a definition (G-I14). | P | HR |
| **FR-4.2** | Reject when a mandatory qualification is absent: a required degree/certification Avadh lacks, or a technology central to the role and wholly absent from his background. | "Mandatory" = the JD says required / must / minimum. "Preferred / nice to have" never triggers FR-4.2. Avadh holds exactly: B.Tech CSE; no certifications listed. Any "required certification" therefore rejects. | Y | HR |
| **FR-4.3** | Never attempt to circumvent an explicit mandatory qualification. | Neither the resume, the letter nor any answer may claim, imply or paper over a missing mandatory qualification. Enforced by the anti-fabrication checks. | Y | AF, HR |

#### 4.5 Fraud and scam detection

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-5.1** | Flag and skip postings requesting payment, equipment via unknown vendors, unusual financial/crypto arrangements, passwords/credentials; or using suspicious email or fake company domains. | Two layers: deterministic signals (free-mail domain for a named enterprise, domain-age, lookalike domains, payment keywords) and an LLM classification. Flagged jobs are rejected under FR-4.1 with reason `fraud_suspected` and shown in the rejected list. | Y | FD |
| **FR-5.2** | Never provide passwords, OTPs, auth codes, banking credentials or any secret to a posting or form. | Form fields of type `password`, or labelled OTP/bank/IFSC/card/PAN/Aadhaar, are never filled by the agent; encountering one raises HITL-2/HITL-3. The agent's own API keys are never in any form-fill payload (TR-8). | Y | FD, NF |

#### 4.6 Resume tailoring

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-6.1** | Where upload is allowed, tailor from the master by reordering skills, re-emphasising existing experience, rewording, foregrounding projects, adjusting the summary. | **Status is contradictory in v0.4** — see G-C1. This analysis assumes FR-6.1 **stands** because FR-6.2, 6.3, 6.4, HITL-5 and T-2 all presuppose tailoring. The allowed-operation list is the whitelist the anti-fabrication checker enforces. | Y | RT, AF |
| **FR-6.2** | Tailored resume stays factually accurate and visually consistent with the master. | "Factually accurate" = passes the fact-ledger check (T-1/T-2/T-5). "Visually consistent" = same stylesheet, same section set, still one page (README rule 3 — not in FR-6, G-I10). | Y | RT, AF |
| **FR-6.3** | Record which resume version was used per application. | Content-hash of the rendered PDF plus the tailored HTML stored with the application. | Y | TK, NF |
| **FR-6.4** | Master is `resume/resume-ats.html`; the agent edits the HTML, runs `render.py`, attaches the PDF; edits preserve ATS properties (single column, no emoji, `.nw` on key phrases, letter-spacing < 8% of font-size) and pass the three-parser test. | The three-parser test (pdfminer, pypdf, PyMuPDF) is an automated gate per tailored PDF; failure blocks the application. The master is never mutated — tailoring writes a copy. | Y | RT |

#### 4.7 Cover letters

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-7.1** | When requested, generate a concise targeted letter in the order: why this role → most relevant experience → evidence of impact → why the AI/LLM/agentic/RAG background applies → short close. | "When requested" = the form has a cover-letter field (G-I4). Structure is checkable by section presence; "concise" needs a word cap (default ≤ 300 words). | P | CL |
| **FR-7.2** | Use concrete §2 evidence only where relevant; no generic filler. | Self-claims trace to the resume; **company-claims trace to the JD** (G-I15). "Filler" is checked by a banned-phrase list and an LLM judge. | P | CL, AF |

#### 4.8 Application questions

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-8.1** | Auto-answer questions determinable from the resume — years of experience with AI / RAG / LLMs / Python / MCP / LangChain / enterprise AI. | **The resume does not carry per-technology years** — only "4+ years" total and one dated role (Aug 2022–present). "Years with MCP" or "years with LangChain" are not derivable; answering them is fabrication (G-C2). Interpretation: total experience is derivable; per-technology years are derivable only from an extended answer sheet that Avadh fills once. | P | CL, AF |
| **FR-8.2** | Generate concise, specific answers to subjective questions grounded in the JD and real experience. | Same provenance rules as cover letters. | Y | CL, AF |
| **FR-8.3** | Never fabricate an answer to complete an application; halt instead. | Any required field the agent cannot fill from resume + answer sheet raises HITL-3 and the application waits. | Y | AF, HL |

#### 4.9 Submission

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-9.1** | Pre-submit verification: correct company · correct job · still active · sufficient score · not duplicate · resume accurate · no fabrication · letter tailored · answers accurate · contact details correct · location acceptable · no false mandatory claim. | Twelve named checks, each producing a pass/fail row stored with the application. **All twelve run after approval and immediately before the click** — approval can be days old. "Still active" = the posting URL re-fetched returns the same job and no closed marker (G-I6). | Y | SB |
| **FR-9.2** | Daily target configurable from the UI, default 10–20, a ceiling not a quota; never pad. | A single integer `daily_ceiling` (default 20) plus an informational lower band. Below-threshold jobs are never promoted to fill the number. | Y | TK, UI |
| **FR-9.3** | Submission requires human approval (§5). | HITL-1 on every submission; no configuration may disable it. | Y | HL |
| **FR-9.4** | Halt and ask when required information is unavailable or a statement could misrepresent Avadh. | HITL-3 / HITL-4 triggers. | Y | HL, AF |

#### 4.10 Tracker

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-10.1** | Durable per-application record: company · title · URL · location · date discovered · date applied · score · key matching skills · status · resume version · cover letter generated · notes · follow-up date. | Plus (implied by NFR-3) the exact submitted payload, screening answers, confirmation evidence and `run_id`. "Follow-up date" has no consumer in v1 (G-I7) — stored, shown, not acted on. | Y | TK |
| **FR-10.2** | The tracker is the duplicate-prevention authority and survives restarts. | Tracker = the system of record (a local relational DB), distinct from the LangGraph checkpointer. Dedup never consults in-memory state. | Y | TK, DD, ID |

#### 4.11 Daily report

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-11.1** | End-of-run report: date · discovered · evaluated · submitted · top applications (company, role, match, location, why) · rejected with reasons · items needing attention · tracker updates. | Persisted as a record and delivered via Telegram (Q-7) and the dashboard. Because submissions happen *after* approval, often hours later, "applications submitted" at run end is usually 0 — the report needs a second "approvals processed" summary or a rolling view (G-M6). | Y | TK, UI |

#### 4.12 Scheduling

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-12.1** | Run daily without manual initiation. | 09:00 local (Q-6). On a personal Windows PC this depends on the machine being awake; the missed-run policy is undefined (G-I1). | P | TK |
| **FR-12.2** | Resumable: an application paused for approval may wait days without losing state or blocking other work. | One LangGraph **thread per application** with a durable checkpointer; the daily discovery run is a separate thread. A pending approval never blocks discovery, scoring or other applications. | Y | HL, TK |

#### 4.13 UI visibility

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **FR-13.1** | Every FR has a UI component reflecting its state and output for the day. | Read literally this includes negative constraints (FR-4.3, FR-5.2, FR-8.3) — interpreted as a **guard-events log** showing when each guard fired (G-M1). | Y | UI |
| **FR-13.2** | The spec carries an explicit FR → UI component map; any FR without one is incomplete. | A spec deliverable, checkable by inspection. | Y (inspection) | UI |
| **FR-13.3** | Minimum surfaces: audit log · approval queue · tracker · daily report · per-job score with reasoning · rejected jobs with reasons · running LLM spend vs ceiling · daily target control · answer sheet. | Nine named surfaces. The answer sheet surface displays **sensitive** values (§2.1) — the dashboard must be local-only (G-I13). | Y | UI |

### 1.2 Human-in-the-loop

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **HITL-1** | Every final submission pauses for approval. | The submit action is behind an `interrupt()`; there is no code path to the ATS submit control that does not pass through a recorded approval. | Y | HL, ID |
| **HITL-2** | Login / OTP / CAPTCHA / phone verification hand control to Avadh. | Detection of these controls pauses the browser session in place and notifies; Avadh completes it in the *same* browser, then resumes. The agent never attempts a CAPTCHA solver. | Y | HL |
| **HITL-3** | Missing personal data (salary, notice, CTC, relocation, work authorisation, sponsorship, termination details, sensitive/demographic data) halts. | **Conflicts with §2.1 as written** — CTC / expected CTC / notice period are on the answer sheet and are filled automatically. Interpretation: HITL-3 fires only for fields **not** on the answer sheet. Demographic / EEO fields default to "prefer not to say" where offered, else HITL-3. | Y | HL |
| **HITL-4** | Any claim that could misrepresent Avadh halts. | Fired by the anti-fabrication checker when it finds a non-traceable claim the generator could not repair, and by FR-4.3 scenarios. | Y | HL, AF |
| **HITL-5** | Every tailored resume + cover letter is reviewed by Avadh — full review, no spot-checking. | One review gate per application presenting resume diff, rendered PDF, letter and all screening answers. Decided; no longer "a posture decision" (§2 inconsistency 3). | Y | HL |
| **HITL-6** | Borderline (70–79) gate — open, recommended to fold into HITL-5. | Adopted as folded: Tier 3 applications are marked `borderline` in the HITL-5 view with the gap list highlighted; no extra gate. | Y | HL |
| **HITL-R1** | A paused application is reviewable and resumable from the dashboard. | The dashboard reads the interrupt payload from the checkpointer (`graph.get_state(config)`) and resumes with `Command(resume=...)` on the same `thread_id`. | Y | HL, UI |
| **HITL-R2** | Approval offers approve · edit · reject; edit lets Avadh fix one line without discarding the application. | Edit applies to letter text, screening answers and the tailored HTML. Whether Avadh's edits are re-checked for fabrication is undefined (G-I5). | Y | HL |
| **HITL-R3** | HITL-3 is largely eliminated by the answer sheet; interrupt only for genuinely novel questions. | Measured as: on the fixture form corpus, HITL-3 fires on < 10% of forms. | P | HL, CL |
| **HITL-R4** | Pauses may last days; state is durable, not in-memory. | Durable checkpointer (`SqliteSaver` / `AsyncSqliteSaver` locally, or Postgres). `InMemorySaver` is forbidden outside tests (gotcha 4). | Y | HL, NF |
| **HITL-R5** | Resuming never re-executes a side effect; an application submitted before a pause is never submitted twice. | Per `langgraph/interrupts.md`, a node restarts from its first line on resume. Therefore: no non-idempotent side effect may precede an `interrupt()` in the same node; the submit click lives in its own node after the gate; the tracker state machine is the idempotency key. | Y | ID |

### 1.3 Truthfulness constraints

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **T-1** | Never invent experience, companies, projects, certifications, degrees, titles, technologies, achievements, responsibilities or years. | Nine fact classes. Each has an extractor and a ledger built from the master. Any output fact of any class not in the ledger is a violation. | Y | AF |
| **T-2** | Tailoring may only reorder, re-emphasise, reword and foreground facts already in the resume. | Whitelisted edit operations on the HTML; rewording is allowed only if the reworded sentence entails no new fact. | Y | AF, RT |
| **T-3** | Never falsely claim a mandatory qualification. | Subset of T-1 targeted at the FR-4.2 gap list for the specific job. | Y | AF, HR |
| **T-4** | Where the truthful answer is unknown, halt and ask. | HITL-3 / HITL-4; no "best guess" mode exists. | Y | HL, AF |
| **T-5** | Every generated claim traces to a specific line of the resume. | Every sentence in generated self-descriptive text carries a provenance pointer to an element id in `resume-ats.html`; the pointer must exist and the sentence must be entailed by that element's text. Company-facts point to a JD span instead. | Y | AF |

### 1.4 Technical requirements

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **TR-1** | Built with LangChain and LangGraph (Python). | LangChain 1.x + LangGraph. Orchestration in a `StateGraph`; LLM steps via `create_agent` or direct model calls; no `langchain-classic`. | Y (inspection + import scan) | NF |
| **TR-2** | All LangChain/LangGraph APIs verified against `knowledge-base/`. | A CI check greps the source for the 14 gotcha patterns (e.g. `langchain_core.messages`, `AgentExecutor`, `InMemorySaver` in non-test code). | Y | NF |
| **TR-3** | Backend plus frontend dashboard. | Local HTTP backend; browser dashboard. | Y | UI |
| **TR-4** | Dashboard shows approval queue, tracker, daily reports, per-job scores with reasoning. | Subset of FR-13.3. | Y | UI |
| **TR-5** | Agent state durably persisted across restarts and multi-day pauses. | Checkpointer on disk with `durability="sync"` on the application thread; tracker in a transactional DB. | Y | HL, ID, NF |
| **TR-6** | Browser automation for ATS forms, against an authenticated session, handing control to Avadh when blocked. | Persistent browser profile so cookies survive; Greenhouse and Lever rarely need login; Workday needs a per-tenant account (§5.1). | P | HL, SB |
| **TR-7** | Every LLM call, tool call and state transition is traceable for debugging and cost. | Local trace store. **Conflicts with NFR-7 if traced to a hosted service** (G-C5) — hosted LangSmith would ship resume text and JDs off-machine. | Y | NF |
| **TR-8** | Secrets never committed, logged, or sent to a posting. | Secret scanning in CI, log redaction, and the form-fill payload validator. | Y | NF, FD |
| **TR-9** | All work committed and pushed to `JobAgent` branch of `avadh-pro/LearningGenAI`. | Process requirement; not a property of the running system. | N | — |
| **TR-10** | Model per stage configurable, not hardcoded. | Three stage keys (`screen`, `analyse`, `generate`) each holding a `provider:model` string consumed by `init_chat_model`. | Y | NF |
| **TR-11** | Per-stage token usage and cost tracked and shown against the daily ceiling. | Usage metadata from every response accumulated per stage per run per day, priced by a configurable price table. | Y | NF, UI |
| **TR-12** | Soft alert well below the ceiling (~$5/day) so a runaway loop is caught early. | Alert via Telegram + dashboard at `soft_limit` (default $5). Behaviour at the hard ceiling is undefined (G-C7). | P | NF, FM |

**§7.1 model strategy** — tiered: cheapest capable model for bulk screening, mid-tier for deep analysis, strongest for anything that goes out under Avadh's name. Restated as the default values of TR-10's three keys. Part B (Fable for spec, Sonnet/Opus for code) is a development-process note, not a system requirement.

### 1.5 Non-functional requirements

| ID | Requirement (restated) | Interpretation | Testable | Test refs |
| --- | --- | --- | --- | --- |
| **NFR-1** | Durability — no loss of application state across restarts or day-long pauses. | Kill at any point; on restart every application is in a well-defined state and resumable or explicitly failed. | Y | FM, HL |
| **NFR-2** | Idempotency — no duplicate submission under any retry, resume or crash-recovery path. | The single most safety-critical property. Proved by fault injection against a counting fake ATS. | Y | ID |
| **NFR-3** | Auditability — reconstruct what was sent, when, on what evidence. | Stored: tailored HTML, PDF hash, letter, answers, form payload, confirmation evidence, score reasoning, approval record with timestamp and decision. | Y | NF, TK |
| **NFR-4** | Recoverability — one board failing does not abort the run. | Per-source isolation; failures land in the audit log as `source_failed`. | Y | FM |
| **NFR-5** | Rate limiting — respectful pacing, nothing resembling an attack. | Per-domain concurrency 1, configurable min-interval with jitter (default 3–8 s), exponential back-off on 429/403, daily request cap per source. | P | NF |
| **NFR-6** | Cost visibility — per-run LLM spend observable. | Same data as TR-11 grouped by run. | Y | NF, UI |
| **NFR-7** | Privacy — resume and personal data stay in Avadh's control; no third-party services beyond those required to apply. | Outbound host allowlist: configured LLM providers, job sources, Telegram API. Nothing else. **LLM providers are third parties that receive the resume and JD** — this is accepted by Q-8/O-4 but should be stated. Answer-sheet values are **never** included in LLM prompts (§2.1 "never sent anywhere but the application form"). | Y | NF |

### 1.6 Hard external constraints

| ID | Restated | Consequence for the system |
| --- | --- | --- |
| **C-1** | LinkedIn, Naukri, Indeed prohibit automated applying and detect bots; risk to Avadh's personal accounts. | Q-3: discovery-only. **Automated scraping of these sites is also against their terms and is login-walled** — the risk C-1 describes applies to discovery too, only less severely (§5.2). |
| **C-2** | CAPTCHA, OTP, SMS, login flows cannot be completed by the agent. | HITL-2; the browser must be hand-off-able mid-session. |
| **C-3** | Submission is irreversible. | HITL-1, NFR-2, and the "unknown outcome" rule in G-C3: after a click whose result is unknown, never retry — ask. |
| **C-4** | Resolved: `resume-ats.html` is the editable master; `render.py` renders. | FR-6 is buildable. `render.py` needs Playwright + Chromium (README). |
| **C-5** | Indian forms demand CTC / expected CTC / notice / relocation, absent from the resume. | Answer sheet (§2.1); HITL-3 residual. |
| **C-6** | Windows `MAX_PATH` 260 chars breaks deep paths. | Artefact storage must use short hashed filenames in a shallow directory; the checkpointer and tracker are DB files, not trees of files. |

### 1.7 Decisions and assumed defaults restated as requirements

| Source | Restated requirement | Testable |
| --- | --- | --- |
| Q-3 | Automated submission only on Greenhouse, Lever, Workday and direct career pages; every other source is discovery-only and lands in FR-1.9. | Y |
| Q-5 | Runs on Avadh's local Windows PC; no server. | Y (inspection) |
| Q-6 | Daily run at 09:00 local. | Y |
| Q-7 | Telegram carries approval notifications and the daily report. | Y |
| Q-8 | $100/day LLM ceiling, running spend visible. | Y |
| Q-9 | Keep all JDs, letters, tracker history indefinitely, locally. | Y |
| O-2 | `work_authorisation` configurable; default "Indian citizen — sponsorship required"; relocation and start date remain open and trigger HITL-3 when asked. | Y |
| O-3 | HITL-6 folded into HITL-5. | Y |
| O-5 | Pending approvals carry over; never auto-submit, never auto-expire; queued ahead of the new batch; closed postings flagged `expired`. | Y |
| §9 | Zero fabricated claims · zero duplicate applications · zero below-threshold applications · minutes per application · > 90% runs without manual rescue. | First three Y; "minutes" and "manual rescue" need definitions (G-I12). |

---

## 2. Internal inconsistencies in v0.4

These are defects in the requirements document itself. Each needs a one-line fix in v0.5 before the spec cites it.

| # | Where | Inconsistency | Proposed fix |
| --- | --- | --- | --- |
| 1 | FR-9.2 vs §9 vs §10.1 | Daily target appears as **10–20** (FR-9.2, changelog), **5–15** (§9 "Applications per day"), and **30–40** (§10.1 "New — Daily target"). | Make §9 and §10.1 read 10–20. Treat FR-9.2 as authoritative. |
| 2 | FR-6.1 vs changelog / O-1 / §11 | The changelog says "FR-6.1 dropped"; O-1 says "~~FR-6.1 incomplete~~ Dropped — not pursued"; §11 says "FR-6.1 dropped (O-1)". Yet FR-6.1 is still in §4.6 as **Must**, and FR-6.2–6.4, T-2 and HITL-5 all depend on tailoring existing. | Clarify that the **open item** (whether FR-6.1's operation list was incomplete) was dropped, and FR-6.1 stands as written. If tailoring itself is dropped, FR-6.2–6.4 and HITL-5 must be rewritten. See G-C1. |
| 3 | §5 preamble | "Gates 1–4 are non-negotiable; gates 5–6 are a posture decision (Q-2)" — but Q-2 is decided and HITL-5 is now full review. | "Gates 1–5 are non-negotiable; HITL-6 is folded into HITL-5 (O-3)." |
| 4 | HITL-3 vs §2.1 | HITL-3 lists salary, notice, CTC as halt triggers; §2.1 says these are filled automatically from the answer sheet. | HITL-3: "…**not present on the answer sheet (§2.1)**". |
| 5 | C-5 | Says "Under FR-9.4 every one of these would halt an application" — true before the answer sheet, stale after it. | Mark resolved by Q-1 with residual HITL-3. |
| 6 | FR-4.1 | "no scoring override" and "(unless overall match is exceptional)" in the same sentence. | Move the traditional-ML clause to a human flag (§5.4). |
| 7 | Tier 1 wording | "apply immediately" contradicts HITL-1/HITL-5 which gate every application. | "Exceptional — queue for approval first." |
| 8 | §11 | "§3 scope and constraints — updated for international, needs re-read" is unchecked while status is "Approved for spec". | Either tick it or state the approval is conditional. |
| 9 | §3.2 vs FR-4.1 | §3.2 puts roles outside India/UAE/Europe/Canada out of scope, but FR-4.1's hard-rejection list omits geography. | Add "outside FR-1.3 geography" to FR-4.1. |
| 10 | FR-1.1 vs Q-3 | Wellfound is listed as a search source but is neither on the discovery-only list nor the submission list. | Add Wellfound to discovery-only. |

---

## 3. Gap analysis

Severity: **Critical** — the spec cannot be written safely without an answer or a stated default · **Important** — the spec can proceed on a default but the default changes user-visible behaviour · **Minor** — cosmetic or process.

### 3.1 Critical

| ID | Gap | Impact | Question or default |
| --- | --- | --- | --- |
| **G-C1** | FR-6.1 status is contradictory (§2 #2). | If tailoring is out, the anti-fabrication surface shrinks to letters and answers and HITL-5 changes shape; if in, the whole RT test group applies. | **Default: FR-6.1 stands.** Question: "Confirm resume tailoring is in scope for v1." |
| **G-C2** | FR-8.1 asks for per-technology years (MCP, LangChain, RAG…) that the resume does not contain. Dates on the resume: role Aug 2022–present, degree 2018–2022. MCP was published in late 2024, so "years with MCP" cannot exceed ~2 regardless. | Any numeric answer to "years with X" that is not on the resume is fabrication under T-1 and is the most likely way this system lies. | **Default:** total experience = years since Aug 2022, rounded down, answered as an integer; every per-technology years question raises HITL-3 until Avadh adds that technology to an **answer-sheet extension** (`years_by_technology`), after which it is filled deterministically from that table, never by the LLM. Question: "Provide years per technology for the FR-8.1 list, or confirm HITL-3 on each." |
| **G-C3** | The requirements never define **what proves a submission happened**. Between the click and the tracker write there is a window in which a crash leaves the outcome unknown. C-3 says there is no unsend. | Retrying after an unknown outcome is exactly how one application becomes two. Not retrying may lose an application. | **Default:** three-state submit — `SUBMITTING` written durably before the click; the click; confirmation evidence captured (success page text, confirmation email hint, screenshot, ATS "application received" URL) and `SUBMITTED` written. On recovery from `SUBMITTING` the system **never re-clicks**; it moves the application to `UNKNOWN_OUTCOME`, notifies Avadh, and treats the job as applied for dedup purposes until Avadh says otherwise. |
| **G-C4** | Concurrency is unaddressed: the 09:00 scheduled run, a dashboard "run now", and approvals resuming application threads can overlap, all writing the tracker. | Two discovery runs can create two application threads for one job; two resumes of one thread can double-submit. | **Default:** one process-wide run lock (discovery runs are serialised); one lock per application thread on resume; the tracker's `(job_identity)` uniqueness constraint is the last line of defence. A duplicate approval for the same thread is acknowledged and ignored. |
| **G-C5** | §2.1 says answer-sheet values are "never sent anywhere but the application form", and NFR-7 forbids third-party services beyond those required to apply. But TR-7 traceability, if implemented with a hosted tracer, ships prompts (resume, JDs, letters) off-machine; and if answer-sheet values are given to the LLM to fill forms, they are sent to a third party. | Privacy breach by construction. | **Default:** answer-sheet fields are filled by deterministic code from field-label matching, never included in any LLM prompt (enforced by a prompt-payload assertion in tests); tracing is stored locally; hosted tracing is off by default and, if enabled, documented as a third-party disclosure. Question: "Is a hosted tracing service acceptable given NFR-7?" |
| **G-C6** | Approval channel security and duality. Q-7 puts approvals on Telegram; HITL-R1 puts them on the dashboard. Nothing says who may approve, or what happens when both channels answer. | An unauthenticated Telegram bot lets anyone who finds it submit applications under Avadh's name. Two channels can deliver conflicting decisions. | **Default:** Telegram accepts commands only from one configured `chat_id`; Telegram supports approve/reject only (no edit — a PDF cannot be reviewed on a phone); the dashboard supports all three. First recorded decision wins; later decisions for the same interrupt are acknowledged as "already decided". |
| **G-C7** | Behaviour at the $100 ceiling and at the $5 soft alert is undefined. Does the run stop? Are half-tailored applications abandoned? Are pending approvals still resumable (resuming costs nothing if no LLM call is needed)? | A runaway loop could be caught by the alert and still burn $95 before anything stops. | **Default:** soft alert notifies; a configurable **hard stop** (default $20, ceiling $100 is the max the control allows) refuses new LLM calls for the day, finishes in-flight nodes, marks unfinished applications `paused_budget`, and keeps approval/submission of already-generated applications working because they need no LLM call. |
| **G-C8** | "Direct career pages" and "unsupported form" are undefined. Workday requires a **per-company account** with email verification, resume parsing into structured fields, and multi-page forms that change per tenant. | Workday will trigger HITL-2 on nearly every application and is the largest engineering sink in the project (§5.1). | **Default:** a form is "supported" if the agent can map ≥ 90% of required fields without human input; otherwise it is an FR-1.9 fallback row. Workday ships in v1 as **assisted** (agent pre-fills what it can in a hand-off browser, Avadh completes). Question: "Accept Workday as assisted rather than fully automated in v1?" |
| **G-C9** | Job identity (FR-2.1/2.3) is undefined, and so is the repost policy. | Too loose: two distinct roles at one company merge and one is never applied to. Too strict: the same role reposted with a new id is applied to twice. | **Default:** identity = ATS job id when present; else normalised company + title-family + location; plus JD-text similarity ≥ 0.85 (shingled Jaccard) merges records with different ids. An **applied** company+title-family is blocked from re-application for 180 days regardless of id; after that it is surfaced to Avadh as "possible repost", never auto-applied. |
| **G-C10** | Out-of-geography roles are out of scope (§3.2) but not in the FR-4.1 reject list; and FR-1.3's "posting permits working from India" has an undefined **unstated** case. | Either a silent filter (untestable) or wasted applications. | **Default:** add `outside_geography` to hard rejections. For international remote roles with no statement about candidate location, do **not** auto-reject; score location 0/5 and show a `location_unverified` flag in HITL-5. |
| **G-C11** | FR-1.1 lists Greenhouse / Lever / Workday as things to search, but they are ATS platforms hosting thousands of company boards. Without a **company list** or a way to discover boards, "search Greenhouse" is meaningless. | Discovery on the very sources where submission is allowed cannot start. | **Default:** a configurable, UI-editable **company watchlist** (seeded by Avadh, grown automatically from companies seen on aggregators), each with its ATS board URL; plus public ATS board search where an index exists. Question: "Provide a seed list of 30–50 target companies." |

### 3.2 Important

| ID | Gap | Impact | Default |
| --- | --- | --- | --- |
| **G-I1** | Missed-run policy, timezone and day boundary are undefined. A personal PC may be asleep at 09:00. | Silent missed days; "daily spend" ambiguous across midnight. | Timezone = Asia/Kolkata. If the 09:00 run did not start, the scheduler runs it at next wake if before 20:00, else skips and logs `run_missed`. Spend day = calendar day IST. |
| **G-I2** | Tier 3 "obvious qualification gaps" undefined. | Untestable threshold. | A Tier 3 job proceeds to tailoring if the scorer's `gaps` list contains no item classed `core` (technology central to the role). Otherwise `rejected: tier3_gap`. |
| **G-I3** | FR-1.4 "exceptionally strong companies" undefined. | Mid-level roles are either always or never considered. | Company-quality dimension ≥ 9/10 **and** company on a configurable `strong_companies` list. Default list empty → mid-level never considered until Avadh adds names. |
| **G-I4** | FR-7.1 "when requested" — by whom. | Letters either always generated (cost, review time) or never. | Generate when the form has a cover-letter field (required or optional). Configurable `always_generate` off by default. |
| **G-I5** | Are Avadh's HITL-R2 edits fact-checked? | Avadh could, in a hurry, type "5 years with LangChain". | Edits are re-run through the anti-fabrication checker; a failure **warns and requires a second explicit confirm** ("I confirm this is true"), which is logged. It does not block — Avadh is the authority on his own facts. |
| **G-I6** | FR-9.1 "still active" verification method. | Approval days later; posting closed; wasted or errored submission. | Re-fetch the canonical URL immediately before submit; require HTTP 200, same job id/title, and none of a configurable closed-marker list ("no longer accepting", "position filled", 404 redirect). Failure → `expired`, notified. |
| **G-I7** | `follow-up date` has no behaviour; Avadh's rejections at HITL-5 have no feedback path. | Field is dead weight; the system never learns why Avadh rejects. | Store and display follow-up date; reject at HITL-5 requires a reason enum (`not_interested`, `bad_tailoring`, `fabrication`, `wrong_role`, `other`) which is stored and reported weekly. No automated learning in v1. |
| **G-I8** | C-1 covers *applying* on LinkedIn/Naukri/Indeed. **Scraping** them is also against their terms, login-walled, and bot-detected. | The three biggest sources may yield nothing or get Avadh's accounts restricted. | Treat them as best-effort: use logged-out public search pages and job-alert emails where available; back off hard on any challenge; never use Avadh's logged-in session for automated discovery. Surface per-source yield in the audit log so the decision to keep them is data-driven. |
| **G-I9** | Q-9 "keep everything indefinitely" vs LangGraph checkpoint growth (gotcha 13) vs C-6 `MAX_PATH`. | Checkpoint DB grows without bound; deep artefact paths break git. | Business records (tracker, JDs, letters, PDFs, audit) are kept forever. **Checkpoints** are pruned 30 days after a thread reaches a terminal state — they are execution scaffolding, not records. Artefacts stored as `artifacts/<sha256[:16]>.<ext>` in one flat directory. |
| **G-I10** | The tailored resume must stay on **one page** (README rule 3) — not stated in FR-6. | A tailored resume that spills to page 2 is "visually inconsistent" but passes FR-6 as written. | Add to FR-6.4's preserved properties: exactly one page. |
| **G-I11** | No global pause / kill switch. | A misbehaving run can only be stopped by killing the process. | Dashboard and Telegram `/pause` sets a persisted flag checked before every LLM call and every browser action; `/resume` clears it. |
| **G-I12** | §9 "runs completing without manual rescue" is undefined in a system where every application requires a human. | Metric cannot be computed. | Manual rescue = any intervention **outside the designed gates** (HITL-1..5): a crash, a stuck browser, a corrupted state, a manual DB edit. Tracked as `run.rescue_events`. |
| **G-I13** | Dashboard exposure. FR-13.3 shows the answer sheet (sensitive). | If the backend binds to all interfaces, CTC and contact data are on the LAN. | Bind to `127.0.0.1` only; no remote access in v1. |
| **G-I14** | "Expired" is undefined. | Applications to closed roles. | Expired = posting fetch fails the G-I6 check, **or** posted date > 45 days ago with no "still accepting" evidence, **or** the board marks it closed. |
| **G-I15** | Cover letters contain **company** facts ("your Series B", "your platform serves 400 hospitals"). T-5 only covers claims about Avadh. | Hallucinated company facts embarrass the applicant as much as fabricated experience. | Company-facts must trace to a JD span or the company page fetched in the same run; otherwise the sentence is rewritten or removed. |
| **G-I16** | EEO / demographic / disability / veteran fields (common on Greenhouse for US companies). | HITL-3 on every such form defeats HITL-R3. | Where a "decline to self-identify / prefer not to say" option exists, select it deterministically; otherwise HITL-3. Configurable per field on the answer sheet. |

### 3.3 Minor

| ID | Gap | Default |
| --- | --- | --- |
| **G-M1** | FR-13.1 literally requires UI for negative constraints (FR-4.3, FR-5.2, FR-8.3). | One **guard-events** panel listing every time a guard fired, with the job and the rule. |
| **G-M2** | §9 "5–15 applications/day" stale. | Update to 10–20. |
| **G-M3** | §10.1 "30–40" stale. | Update to 10–20. |
| **G-M4** | TR-9 is a process requirement. | Not tested by the system; noted for the delivery checklist. |
| **G-M5** | §7.1 names "Haiku 4.5" as an example. | Kept as a default config value, not a requirement; model strings follow the `provider:model` form consumed by `init_chat_model`. |
| **G-M6** | FR-11.1 via Telegram — message length limits; and "submitted" at run end is usually 0 because approvals come later. | Report = summary message + dashboard link; a second "approvals processed today" digest at 21:00. |
| **G-M7** | FR-10.1 "cover letter generated" — boolean or content? | Both: flag plus stored text. |
| **G-M8** | README recommends a LinkedIn vanity URL. | Out of system scope; personal to-do. |
| **G-M9** | Notice period "1 month" — forms often ask in days or as a date. | Deterministic conversion table on the answer sheet (30 days; earliest start = today + 30). |
| **G-M10** | Expected CTC ₹32 LPA for Dubai/Europe/Canada forms asking in AED/EUR/CAD. | HITL-3 for non-INR currency until Avadh adds per-currency expectations to the answer sheet. Never auto-convert. |

### 3.4 Note on O-2 (work authorisation)

O-2 is knowingly open. The default — Indian citizen, no foreign permit, sponsorship required — is the **safe** direction: it rejects rather than wastes. The system must make the setting visible on the answer-sheet surface with a one-line explanation of what changing it does, and log the count of jobs rejected as `no_sponsorship` per run so the cost of leaving it unconfirmed is visible in the daily report. Relocation stance and preferred start date stay open and raise HITL-3 when a form asks.

---

## 4. Design hints vs hard constraints

| Item | Class | Basis | Architect's position |
| --- | --- | --- | --- |
| LangChain 1.x + LangGraph, Python (TR-1, TR-2) | **Hard** | Explicit, repeated; knowledge base built for it | Accept. Verify every API in the knowledge base; CI-lint the 14 gotchas. |
| Local Windows PC runtime (Q-5) | **Hard** | Decided | Accept. Drives: SQLite over Postgres, Task Scheduler, `MAX_PATH` care, missed-run policy. |
| Discovery-only on LinkedIn / Naukri / Indeed; automated submit only on Greenhouse / Lever / Workday / direct (Q-3, C-1) | **Hard** | Decided; ToS risk to personal accounts | Accept, and extend discovery-only to Wellfound. Push back on Workday (§5.1). |
| Full human review of every application (HITL-1, HITL-5, Q-2) | **Hard** | Decided; C-3 irreversibility | Accept. No configuration may bypass either gate. |
| Truthfulness (§6 T-1..T-5, FR-4.3, FR-8.3) | **Hard** | "Override every other requirement" | Accept. This is the design centre of the generation pipeline, not a post-check. |
| Idempotent submission (NFR-2, HITL-R5) | **Hard** | Safety-critical under LangGraph's node-restart semantics | Accept. Submit is its own node after the gate; tracker state machine is the key. |
| Durable state (TR-5, HITL-R4, NFR-1) | **Hard** | Days-long pauses | Accept. On-disk checkpointer; `InMemorySaver` banned outside tests. |
| Ceiling not quota (FR-9.2) | **Hard** | Objective function (§1) | Accept. |
| Telegram for notifications and daily report (Q-7) | **Hard** | Decided | Accept for notify, approve, reject. Evaluate: **edit and full review belong on the dashboard** (§5.5). |
| $100/day ceiling (Q-8) | **Hard as a maximum**, hint as an operating level | C-D says it is a ceiling, not a budget | Accept the control; propose a lower default hard-stop (§5.7). |
| Keep everything indefinitely (Q-9) | **Hard for business records** | Decided | Accept for records; exclude checkpoints (G-I9). |
| Every FR has a UI component (FR-13.1) | **Hard** | Explicit | Accept; interpret negative constraints as guard-events (G-M1). |
| Tiered model strategy (§7.1) | **Hint** | "e.g. Haiku 4.5"; TR-10 says configurable | Agree with the tiering; the three stage keys are the requirement, the models are defaults. |
| "LangChain makes this a one-line change" (TR-10) | **Hint** | Commentary | True for `init_chat_model("provider:model")`; not true for provider-specific structured-output behaviour, which must be tested per model. |
| Board list in FR-1.1 | **Hint** | Sources are means, not ends | Evaluate yield per source via FR-1.8; drop or demote sources that yield nothing or trigger challenges. |
| Location priority order (FR-1.3) | **Hint** | Feeds a 5-point dimension | Accept as configurable ordering. |
| Rubric weights (§4.3) | **Hint** | Reasonable defaults | Configurable; keep defaults. Location as a 5-point dimension is too weak for eligibility — eligibility is a hard filter (§5.4). |
| Fold HITL-6 into HITL-5 (O-3) | **Hint, adopted** | Recommended in the doc | Agree. |
| "Search Greenhouse / Lever / Workday" (FR-1.1) | **Hint** | These are ATS platforms, not boards | Replace with a company watchlist (G-C11). |
| "Authenticated session" for browser automation (TR-6) | **Hint** | Greenhouse/Lever rarely need login | Persistent browser profile; login only where a tenant requires it. |
| 09:00 schedule (Q-6) | **Hint** | Decided but arbitrary | Accept; make it configurable with the missed-run policy (G-I1). |
| Multi-agent structure | **Not requested** | Gotcha 14: "reaching for multi-agent too early" | Do not assume multi-agent. A single `StateGraph` with deterministic nodes and a small number of model calls is the default posture; `create_agent` is used where tool-calling autonomy is genuinely needed (form filling), not for scoring or generation. |

---

## 5. Requirements to challenge

Honest assessment of what will not work well as written, with an alternative each.

### 5.1 Workday as a fully automated submission target (Q-3, FR-1.1, TR-6)

**Problem.** Every Workday tenant is a separate site with its own account, email verification (C-2 → HITL-2 on first contact with each company), multi-page forms, resume-parsing that pre-fills fields wrongly, and per-tenant custom questions. Public experience with automating Workday is uniformly poor. It will consume more engineering than the rest of the submission layer combined and will still hand off to Avadh most of the time.

**Alternative.** Ship Workday in v1 as **assisted**: the agent opens the posting in the hand-off browser, uploads the tailored PDF, pre-fills every field it can map, and stops at the first unmappable field or verification step with a Telegram ping. The application is still tracked, still deduplicated, still HITL-1 gated (Avadh clicks submit). Promote to fully automated in v2 only if the audit log shows a repeatable pattern.

### 5.2 LinkedIn / Naukri / Indeed as automated discovery sources (FR-1.1, C-1)

**Problem.** C-1 is written about applying, but scraping these sites also violates their terms, and their bot detection does not distinguish "just reading". Using Avadh's logged-in session for automated search puts the account at the same risk C-1 warns about; using a logged-out session yields degraded results and challenges within a day.

**Alternative.** Make them **best-effort** with explicit guardrails: never use the personal logged-in session for automation; prefer their email job alerts (parsed from a dedicated mailbox) and public search pages; back off for 24 hours on any challenge. Measure yield per source in FR-1.8 for the first two weeks and let the data decide whether to keep them. Invest the saved effort in the company watchlist (G-C11), which is where submissions can actually happen.

### 5.3 Per-technology years of experience (FR-8.1)

**Problem.** As written, FR-8.1 instructs the system to answer "years with MCP / LangChain / RAG" from a resume that contains no such figures. It is an invitation to fabricate, in the one category (numbers) that recruiters can and do verify at interview.

**Alternative.** Rewrite FR-8.1: "Auto-answer questions whose answer is **on the resume or the answer sheet**. Total years of experience is derivable from resume dates. Per-technology years are answered **only** from an answer-sheet table Avadh fills once; absent an entry, HITL-3." The LLM never produces a number for these fields.

### 5.4 Location as a 5-point rubric dimension; the traditional-ML override (FR-1.3, FR-3.1, FR-4.1)

**Problem.** A role in São Paulo can score 95 and pass every threshold because location is worth 5 points. Eligibility is being modelled as a preference. Separately, FR-4.1's "(unless overall match is exceptional)" reintroduces the scoring override it forbids in the same sentence.

**Alternative.** Split **eligibility** (hard filter: geography, work authorisation, seniority floor, expiry, fraud, duplicate — all yes/no, all before scoring) from **fit** (the rubric). Move the traditional-ML clause out of hard rejection: score it normally; if it scores ≥ 90 despite thin GenAI content, show it in HITL-5 with a `traditional_ml` flag and let Avadh decide. Auto-reject below that.

### 5.5 Telegram as the approval surface for HITL-5 (Q-7, HITL-R1, HITL-R2)

**Problem.** HITL-5 is a full review of a rendered PDF, a diff against the master, a cover letter and screening answers. That cannot be done on a phone chat, and `edit` (HITL-R2) cannot be done there at all. If Telegram offers a one-tap approve, Avadh will use it, and "full review" becomes spot-checking by another name — the outcome Q-2 explicitly rejected.

**Alternative.** Telegram = **notify + link + reject**. Approve and edit require the dashboard, where the diff and PDF are rendered. If a one-tap approve on Telegram is wanted anyway, gate it behind a setting that is off by default and logged as `approved_without_review`.

### 5.6 FR-13.1 read literally

**Problem.** Forty-three FRs each with their own component produces a dashboard nobody uses. Several FRs are constraints, not features.

**Alternative.** Keep the **FR → UI map** (FR-13.2) as the contract but let many FRs map to one surface: the audit log covers FR-1.1–1.9, the approval view covers FR-6–8 and HITL-1–5, the guard-events panel covers FR-4.3, FR-5.2, FR-8.3, T-1..T-5. The map proves coverage; the design stays usable.

### 5.7 $100/day ceiling as the only stop (Q-8, TR-12)

**Problem.** At the tiered model strategy's expected spend (well under $5/day at 10–20 applications), a run that reaches $100 is broken by definition. A soft *alert* at $5 does not stop anything; a human asleep at 03:00 does not read it.

**Alternative.** Three levels: soft alert (default $5, notify), **hard stop** (default $20, refuse new LLM calls, finish the run gracefully, approvals still work), absolute ceiling ($100, the maximum the hard-stop control accepts). All UI-configurable (FR-13.3).

### 5.8 "Keep everything indefinitely" applied to checkpoints (Q-9)

**Problem.** LangGraph checkpoints write the full state every super-step (gotcha 13). A thread that carried a JD, a resume HTML, a letter and a browser log through twenty nodes stores twenty copies. Over a year on a personal PC this is gigabytes of scaffolding that nobody reads.

**Alternative.** Keep every **record** forever (tracker rows, artefacts, audit log, approval decisions). Prune checkpoints 30 days after a thread reaches a terminal state. NFR-3 auditability is satisfied by the records, not by replayable checkpoints.

### 5.9 "Apply immediately" for Tier 1

**Problem.** Nothing is immediate — every application waits for HITL-5 and HITL-1. The wording will mislead a reader of the spec into designing a fast path.

**Alternative.** Tiers affect **ordering** in the approval queue and the tailoring model budget, never gating.

### 5.10 The daily report at run end (FR-11.1)

**Problem.** The run finishes at ~09:30 with N applications *queued*; Avadh approves at 21:00; submissions happen at 21:05. The 09:30 report says "0 submitted" every day, and the true daily story is never told.

**Alternative.** Two messages: the morning **discovery report** (found / evaluated / queued / rejected) and an evening **submission digest** (approved / submitted / edited / rejected with reasons). The dashboard shows both.

### 5.11 Using `HumanInTheLoopMiddleware` for every gate

**Problem.** `HumanInTheLoopMiddleware` (verified in `langchain/human-in-the-loop.md`) reviews **tool calls** proposed by an agent loop — its decisions are approve / edit / reject / respond on a tool call's arguments. HITL-5 is a review of **generated state** (a resume diff, a letter), not a tool call; HITL-2 is a review of a **browser condition**. Forcing these through tool-call middleware means the "tool" is a fake wrapper whose arguments are an entire resume, and `edit` becomes editing a JSON blob.

**Alternative (design hint, not design).** Use the middleware where it fits — the `submit_application` tool call inside a form-filling agent is a textbook `interrupt_on={"submit_application": {"allowed_decisions": ["approve", "reject"]}}` case — and the raw `interrupt()` primitive from `langgraph.types` in dedicated review nodes for HITL-2, HITL-3, HITL-4 and HITL-5, each node containing exactly one `interrupt()` and no side effect before it (rules of interrupts, `langgraph/interrupts.md`).

### 5.12 §9 "> 90% of runs without manual rescue"

**Problem.** Undefined (G-I12) and, in the first month, unachievable while form mappings are being learned. Measuring it from day one will read as failure.

**Alternative.** Define manual rescue as intervention outside designed gates; report it weekly; set the 90% target from month 2.

---

## 6. Consolidated questions for Avadh

Ordered by how much the answer changes the design.

| # | Question | Gap | If unanswered, the spec assumes |
| --- | --- | --- | --- |
| Q-A | Is resume tailoring (FR-6.1) in scope for v1? | G-C1 | Yes |
| Q-B | Provide a seed company watchlist (30–50 companies with career-page / ATS URLs). | G-C11 | Empty list; discovery limited to aggregators until filled |
| Q-C | Accept Workday as *assisted* (agent pre-fills, you submit) in v1? | G-C8 | Yes |
| Q-D | Years of experience per technology for the FR-8.1 list (AI, RAG, LLMs, Python, MCP, LangChain, enterprise AI) — or HITL-3 each time? | G-C2 | HITL-3 each time |
| Q-E | Do you hold any EU / Canada / UAE work permit? (O-2) | O-2 | No — sponsorship required |
| Q-F | Relocation stance and earliest start date. (O-2) | O-2 | HITL-3 when asked |
| Q-G | Is a hosted tracing service (which receives prompts) acceptable, or local-only tracing? | G-C5 | Local-only |
| Q-H | Hard-stop spend level (proposed $20/day) in addition to the $5 alert and $100 ceiling? | G-C7 | $20 |
| Q-I | Approve-from-Telegram: allowed (one tap, logged as unreviewed) or dashboard-only? | G-C6, §5.5 | Dashboard-only for approve/edit; Telegram for reject |
| Q-J | Repost policy: block re-application to the same company + title-family for how long? | G-C9 | 180 days |
| Q-K | Expected CTC in AED / EUR / CAD for international forms, or HITL-3? | G-M10 | HITL-3 |
| Q-L | EEO / demographic questions: auto-select "prefer not to say" where offered? | G-I16 | Yes |

---

## 7. Assumption register

Defaults the specification will adopt unless overruled. Each is a testable statement.

| # | Assumption | Source |
| --- | --- | --- |
| A-1 | FR-6.1 stands; tailoring is in scope. | G-C1 |
| A-2 | The tracker (relational DB) is the system of record; the LangGraph checkpointer is execution state only. | FR-10.2, TR-5 |
| A-3 | One LangGraph thread per application; one per discovery run; `thread_id` is a UUID (gotcha 11). | FR-12.2 |
| A-4 | Submit is a dedicated node that runs after the HITL-1 interrupt node; nothing before any `interrupt()` in the same node has a non-idempotent side effect. | HITL-R5, `langgraph/interrupts.md` |
| A-5 | Submission states: `PENDING_REVIEW → APPROVED → SUBMITTING → SUBMITTED | FAILED | UNKNOWN_OUTCOME | EXPIRED | REJECTED_BY_USER`. Recovery from `SUBMITTING` never re-clicks. | G-C3 |
| A-6 | Answer-sheet values are filled by deterministic code and never appear in any LLM prompt. | §2.1, G-C5 |
| A-7 | Total years of experience is computed from resume dates; per-technology years come only from an answer-sheet table; otherwise HITL-3. | G-C2 |
| A-8 | Every generated self-claim carries a provenance pointer to an element in `resume-ats.html`; every company-claim to a JD/company-page span. | T-5, G-I15 |
| A-9 | Eligibility (geography, authorisation, seniority floor, expiry, fraud, duplicate) is a hard filter before scoring; the rubric measures fit only. | §5.4 |
| A-10 | Job identity = ATS id when present, else normalised company + title-family + location, with JD similarity merge at ≥ 0.85; applied company + title-family blocked 180 days. | G-C9 |
| A-11 | Expired = fetch fails / closed marker / > 45 days old. | G-I14 |
| A-12 | Tier 3 proceeds only with no `core` gap. Mid-level considered only for companies on a configured `strong_companies` list with company quality ≥ 9. | G-I2, G-I3 |
| A-13 | Cover letter generated when the form has a cover-letter field; ≤ 300 words; five-part structure. | FR-7.1, G-I4 |
| A-14 | Telegram: single authorised `chat_id`; notify / link / reject; approve and edit on the dashboard. First decision wins. | G-C6 |
| A-15 | Spend: soft alert $5, hard stop $20, ceiling $100, day = IST calendar day; approvals and submissions of already-generated applications keep working after a hard stop. | G-C7 |
| A-16 | Dashboard binds to `127.0.0.1`. | G-I13 |
| A-17 | Records kept forever; checkpoints pruned 30 days after terminal state; artefacts stored flat under hashed names. | G-I9, C-6 |
| A-18 | Discovery-only sources: LinkedIn, Naukri, Indeed, Wellfound. Automated submit: Greenhouse, Lever, direct career pages. Workday: assisted. | Q-3, §5.1 |
| A-19 | Missed 09:00 run executes at next wake before 20:00 IST, else logged as missed. | G-I1 |
| A-20 | Avadh's HITL-R2 edits are re-checked; failures require an explicit logged confirmation, not a block. | G-I5 |
| A-21 | Rate limits: per-domain concurrency 1, 3–8 s jittered interval, exponential back-off on 429/403, daily cap per source. | NFR-5 |
| A-22 | Pre-submit verification (FR-9.1) runs after approval and immediately before the click, including a live re-fetch of the posting. | FR-9.1, G-I6 |
| A-23 | Model stage keys `screen` / `analyse` / `generate`, each a `provider:model` string for `init_chat_model`. | TR-10 |
| A-24 | Global `/pause` flag checked before every LLM call and browser action. | G-I11 |

---

## 8. Traceability into the test plan

Every ID above maps to at least one acceptance-criteria group in `docs/test-plan.md` §16 (coverage matrix). The two groups that carry the project's risk are **AF** (anti-fabrication) and **ID** (idempotency); a release in which any AC in those two groups fails must not be allowed to submit a real application.

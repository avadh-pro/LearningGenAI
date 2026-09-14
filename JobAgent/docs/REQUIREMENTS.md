# JobAgent — Requirements

**Project:** Autonomous AI/ML Job Search & Application Agent
**Owner:** Avadh Dobariya
**Status:** 🟡 Draft — awaiting review
**Version:** 0.3 · 2026-09-14

> **Changes since 0.2** — Decisions logged from review: the answer sheet (§2.1), board policy,
> runtime, schedule, notifications, budget and retention are now **decided** (§10.1). Adds the
> daily search audit log (FR-1.8), geographic expansion to Dubai / Europe / Canada (FR-1.3),
> a UI-visibility requirement for every functional requirement (§4.13), and a configurable
> daily application target (FR-9.2). **§10.3 records four conflicts between decisions that must
> be resolved before the spec.** Five questions remain open (§10.2).
>
> **Changes since 0.1** — Added Forward Deployed Engineering (FDE) as a first-class target job
> family: title variants in §4.1.1, rationale and two scoring caveats in §4.1.2 (FR-1.6, FR-1.7),
> and abbreviation search in FR-1.5.

> This document states **what** the system must do and **why**. It deliberately does not state
> **how**. Once approved, it becomes the input to the technical specification.
>
> Open decisions are collected in **§10**. Nothing in §10 has been guessed at — each one
> genuinely changes the design and needs an answer before the spec can be written.

---

## 1. Objective

Every day, find the best realistic AI engineering opportunities for Avadh and submit
high-quality, truthful, highly targeted applications.

**The objective function is interview probability per application — not application count.**

This distinction drives most requirements below. A system optimising for volume would be
easier to build and would actively work against the goal. Where the two conflict, relevance
and factual accuracy win.

| | |
| --- | --- |
| ✅ Goal | Maximise interviews from a limited number of highly relevant applications |
| ❌ Non-goal | Apply to as many jobs as possible |

---

## 2. Candidate profile — the source of truth

The resume is the **single source of truth**. Every claim the system makes on Avadh's behalf
must be supported by it.

`Avadh_Dobariya_Senior_AI_Solution_Engineer.pdf`

| Field | Value |
| --- | --- |
| Name | Avadh Dobariya |
| Current role | Senior AI Solution Engineer, Krista Software (Aug 2022 – Present) |
| Experience | 4+ years |
| Location | Pune, India |
| Education | B.Tech CSE, MIT Academy of Engineering (MITAOE), Pune · Jul 2018 – Jul 2022 · CGPA 8.50/10 |
| Awards | 2× Shining Star of Krista |
| Contact | avadhdobariya@gmail.com · +91 8779092749 |
| Links | linkedin.com/in/avadh-dobariya368935208 · github.com/avadhdobariya |

**Evidence available for tailoring** (use only where relevant to the specific role):

- Architected **25+ enterprise AI automation solutions**, reducing manual workflows by **up to 80%**
- Production **MCP server** over MCP JSON-RPC 2.0, letting Claude / ChatGPT / Cursor call governed enterprise tools
- Core engineer on **AIQA**, an enterprise RAG platform: 50+ format ingestion readers, chunking/embedding pipelines, hybrid lexical + vector retrieval, citation-grounded multi-turn answers
- **AI Risk & Compliance Sync Engine** — eliminated **20+ hrs/week** of manual reconciliation
- Owns full solution lifecycle: requirements → architecture → integration → demos → optimisation
- Mentors 4 engineers

### 2.1 The answer sheet

Values the resume does not carry but application forms demand (C-5). The agent fills these
automatically instead of halting at HITL-3.

| Field | Value | Status |
| --- | --- | --- |
| Current CTC | **₹19.8 LPA** | ✅ decided v0.3 |
| Expected CTC | **₹32 LPA** | ✅ decided v0.3 |
| Notice period | **1 month** | ✅ decided v0.3 |
| Relocation stance | — | ⬜ open (O-2) |
| Work authorisation | — | ⬜ open (O-2) — **now load-bearing**, see FR-1.3a |
| Preferred start date | — | ⬜ open (O-2) |

**Treat every value here as sensitive.** It is never logged to a shared surface, never sent
anywhere but the application form it is required by, and CTC figures are never volunteered when
a form does not ask.

**Differentiators, in ranked order** — these drive opportunity ranking (§4.3):
production GenAI · agentic AI · MCP · enterprise RAG · enterprise AI automation ·
LLM integrations · tool/function calling · enterprise API integrations ·
production AI architecture · measurable automation impact

---

## 3. Scope

### 3.1 In scope

Daily discovery, evaluation, scoring, deduplication, resume tailoring, cover letter generation,
screening-question answering, application submission, human approval gates, an application
tracker, a review dashboard, and a daily report.

### 3.2 Out of scope (v1)

- Non-AI/ML roles
- Interview scheduling, interview prep, salary negotiation
- Recruiter outreach or messaging
- Job boards requiring paid subscriptions
- Roles in geographies outside India, Dubai/UAE, Europe and Canada (FR-1.3)
- Roles requiring work authorisation Avadh does not hold where no sponsorship is offered (FR-1.3a)

### 3.3 Hard external constraints

These are facts about the environment, not design choices. They bound what is buildable.

| ID | Constraint |
| --- | --- |
| C-1 | LinkedIn, Naukri and Indeed prohibit automated applying in their terms of service and run bot detection. Automating submission there carries a real risk of account restriction on Avadh's personal accounts. |
| C-2 | CAPTCHAs, OTPs, SMS/phone verification and login flows cannot be completed by the agent. They require Avadh. |
| C-3 | Application submission is **irreversible**. There is no unsend. |
| C-4 | ~~The resume exists only as a PDF.~~ **RESOLVED v0.3** — `JobAgent/resume/resume-ats.html` is the editable master; `render.py` regenerates the PDF. FR-6 is unblocked. |
| C-5 | Most Indian application forms demand data absent from the resume — current CTC, expected CTC, notice period, relocation willingness. Under FR-9.4 every one of these would halt an application. |
| C-6 | This repo hits the Windows 260-char `MAX_PATH` limit. Deep nested paths break git operations. |

---

## 4. Functional requirements

### 4.1 Discovery

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1.1 | Search daily for newly posted and still-active roles across LinkedIn, Indeed, Wellfound, Naukri, Greenhouse, Lever, Workday, and direct company career pages. | Must |
| FR-1.2 | Prioritise **direct company career pages and ATS links** over aggregators — better data, and outside the C-1 risk. | Must |
| FR-1.3 | **India:** Remote → Pune → Bengaluru → Hyderabad → Mumbai → Delhi NCR → other major Indian tech hubs. **International (added v0.3):** Dubai / UAE, Europe, Canada. International remote allowed where the posting permits candidates working from India. | Must |
| FR-1.3a | For every international role, extract and surface **visa / work-authorisation requirements and whether sponsorship is offered**. Roles requiring authorisation Avadh does not hold and that do not sponsor are ineligible and must be rejected under FR-4.2, not queued. | Must |
| FR-1.4 | Seniority: target Senior / Staff / Lead / Senior IC / Architect. Consider mid-level only for exceptionally strong companies. Never junior, entry-level, internship, graduate or trainee. | Must |
| FR-1.5 | Search the target titles (§4.1.1) crossed with GenAI keywords: RAG, LLM, Agentic AI, MCP, GenAI, AI Agents, LangChain, LangGraph, LLMOps, Enterprise AI. Search both `Forward Deployed` and the abbreviation `FDE` — postings use either. | Must |
| FR-1.8 | Maintain a **daily search audit log**: for each run, record every **source** queried (LinkedIn, Naukri, Indeed, Wellfound, Greenhouse, Lever, Workday, career pages), every **query** issued, and every **job found**, with its score, its verdict, and — where not applied to — the reason. | Must |
| FR-1.9 | The audit log is the **manual-fallback surface**. Any job the agent could not auto-apply to (C-1 discovery-only source, CAPTCHA, unsupported form, missing data) must appear in it, filterable, with a working link, so Avadh can apply by hand. Each such row carries a state Avadh can set: `pending` / `applied manually` / `skipped`. | Must |

**§4.1.1 Target titles.** Senior AI Engineer · Senior Generative AI Engineer · Senior LLM Engineer ·
Senior AI/ML Engineer · Senior Agentic AI Engineer · Senior AI Solution Engineer ·
AI Solutions Architect · Generative AI Engineer · LLM Engineer · Agentic AI Engineer ·
AI Platform Engineer · AI Automation Engineer · RAG Engineer · Applied AI Engineer ·
AI Architect · **Forward Deployed Engineer (FDE)** · **Senior Forward Deployed Engineer** ·
**Forward Deployed AI Engineer** · **Forward Deployed Software Engineer** ·
Senior ML Engineer *(only where there is substantial GenAI/LLM work)*.
Closely related titles qualify if the responsibilities genuinely match.

**§4.1.2 Forward Deployed Engineering — why it is a first-class target.** FDE roles map directly
onto what Avadh already does: owning the full solution lifecycle for enterprise customers
(requirements → architecture → integration → demos → optimisation → production support),
integrating LLMs with third-party enterprise systems, and building customer-facing AI solutions.
The 25+ enterprise AI automation deployments and the enterprise API integration work (Jira,
Slack, Salesforce, Zoho, Datadog, Microsoft Teams/Graph) are the strongest possible evidence for
this job family. Search for the expanded form and the abbreviation — postings use both.

Two caveats apply when scoring an FDE role:

- **FR-1.6** — An FDE role qualifies only where there is **substantial GenAI/LLM work**. Some FDE
  postings are conventional software delivery or data engineering with no AI component; those
  fall under FR-4.1 (primarily non-AI software development).
- **FR-1.7** — FDE postings frequently carry **significant travel or onsite client requirements**.
  Extract and surface any travel percentage, onsite expectation or client-site base location in
  the job record so it is visible before applying, and treat a requirement to relocate abroad
  under the FR-1.3 rule.

### 4.2 Deduplication

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-2.1 | Treat one position appearing on several boards as **one job**. | Must |
| FR-2.2 | Never apply to the same position twice. Check the tracker before every application. | Must |
| FR-2.3 | Identity must survive cosmetic differences — differing titles, reposts, differing board URLs for the same ATS listing. | Must |

### 4.3 Evaluation and scoring

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-3.1 | Score every discovered job 0–100 on the rubric below. | Must |
| FR-3.2 | **Read the actual job description — never score from the title.** An "ML Engineer" doing LLM/RAG/agent work is a strong match; an "AI Engineer" doing computer vision or classical ML is not. | Must |
| FR-3.3 | Rank using the §2 differentiators — prefer roles where Avadh's production experience is a genuine competitive advantage. | Must |
| FR-3.4 | Record the score and its reasoning for every job, including rejected ones. | Must |

**Scoring rubric** (totals 100):

| Dimension | Points |
| --- | --- |
| Technical skill match | 30 |
| Relevant AI/LLM experience | 25 |
| Seniority match | 15 |
| Project / domain relevance | 10 |
| Company / opportunity quality | 10 |
| Location / remote fit | 5 |
| Resume keyword alignment | 5 |

**Thresholds:**

| Score | Action |
| --- | --- |
| 90–100 | Exceptional — apply immediately (Tier 1) |
| 80–89 | Strong — apply (Tier 2) |
| 70–79 | Reasonable — apply only if no obvious qualification gaps (Tier 3) |
| < 70 | Do not apply |

Effort concentrates on Tier 1 and Tier 2.

### 4.4 Hard rejection rules

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-4.1 | Reject outright — no scoring override — when the role is: clearly junior · primarily non-AI software development · primarily data analytics · primarily DevOps with little/no AI · primarily traditional ML with no meaningful GenAI/LLM component (unless overall match is exceptional) · expired · already applied to · fraudulent or suspicious. | Must |
| FR-4.2 | Reject when a **mandatory** qualification is absent — a required degree or certification Avadh does not hold, or a technology central to the role and wholly absent from his background. | Must |
| FR-4.3 | **Never attempt to circumvent an explicit mandatory qualification.** | Must |

### 4.5 Fraud and scam detection

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-5.1 | Flag and skip postings that request payment, equipment purchases through unknown vendors, unusual financial or crypto arrangements, passwords or credentials; or that use suspicious email domains or fake-looking company domains. | Must |
| FR-5.2 | **Never** provide passwords, OTPs, authentication codes, banking credentials or any secret to a job posting or application form. | Must |

### 4.6 Resume tailoring

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-6.1 | Where a resume upload is allowed, tailor from the master resume by **reordering skills, re-emphasising existing experience, improving wording, foregrounding relevant projects, and adjusting the professional summary**. | Must |
| FR-6.2 | The tailored resume must remain **factually accurate** and visually consistent with the master. | Must |
| FR-6.3 | Record which resume version was used for each application. | Must |
| FR-6.4 | ✅ **Unblocked.** The master is `JobAgent/resume/resume-ats.html`. The agent edits the HTML, runs `render.py`, and attaches the generated PDF. Any edit must preserve the ATS properties documented in `JobAgent/resume/README.md` (single column, no emoji, nowrap on key phrases, letter-spacing under 8% of font-size) and be re-verified with the three-parser test. | Must |

### 4.7 Cover letters

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-7.1 | When requested, generate a concise, targeted letter: why this role → most relevant experience → specific evidence of impact → why the AI/LLM/agentic/RAG background applies → short close. | Must |
| FR-7.2 | Use concrete evidence from §2, **only where relevant to that job**. No generic corporate filler. | Must |

### 4.8 Application questions

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-8.1 | Auto-answer questions determinable from the resume — years of experience with AI / RAG / LLMs / Python / MCP / LangChain / enterprise AI. | Must |
| FR-8.2 | Generate concise, specific answers to subjective questions ("why this company?", "why are you a good fit?") grounded in the JD and real experience. | Must |
| FR-8.3 | **Never fabricate an answer in order to complete an application.** Halt instead (see §5). | Must |

### 4.9 Submission

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-9.1 | Before submitting, verify: correct company · correct job · job still active · sufficient score · not a duplicate · resume accurate · no fabricated information · cover letter tailored · answers accurate · contact details correct · location acceptable · no mandatory qualification falsely claimed. | Must |
| FR-9.2 | Daily application target is **configurable from the UI**, never hardcoded. Default **30–40/day** per the v0.3 decision. The target is a **ceiling, not a quota**: it is scaled down to genuine availability, and if only 2 jobs clear the threshold, only 2 are applied to. **Never pad to hit a number.** See §10.3 C-A — the threshold and the supply of eligible roles are expected to bind well before this setting does. | Must |
| FR-9.3 | Submission requires human approval — see §5. | Must |
| FR-9.4 | Halt and ask rather than guess whenever required information is unavailable or a statement could materially misrepresent Avadh. | Must |

### 4.10 Application tracker

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-10.1 | Maintain a durable tracker recording, per application: company · job title · job URL · location · date discovered · date applied · match score · key matching skills · status · resume version used · cover letter generated · notes · follow-up date. | Must |
| FR-10.2 | The tracker is the authority for duplicate prevention (FR-2.2) and must survive restarts. | Must |

### 4.11 Daily report

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-11.1 | At the end of each run, report: date · jobs discovered · jobs evaluated · applications submitted · top applications (company, role, match, location, why it matches) · rejected jobs with reasons · items needing Avadh's attention · tracker updates. | Must |

### 4.12 Scheduling

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-12.1 | Run daily without manual initiation. | Must |
| FR-12.2 | A run must be resumable — an application paused for approval may wait days without losing state or blocking other work. | Must |

### 4.13 UI visibility

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-13.1 | **Every functional requirement must have a corresponding UI component.** No requirement may be invisible — each needs a dashboard element (table, counter, toggle, log or state badge) reflecting its state and output for the day. | Must |
| FR-13.2 | The spec must carry an explicit **FR → UI component map**, and any FR without one is treated as incomplete. | Must |
| FR-13.3 | Minimum surfaces: daily search audit log (FR-1.8/1.9) · approval queue (§5) · application tracker (FR-10) · daily report (FR-11) · per-job score with reasoning (FR-3.4) · rejected jobs with reasons (FR-4) · **running LLM spend against the daily ceiling** (§10.1) · the configurable daily target (FR-9.2) · the answer sheet (§2.1). | Must |

---

## 5. Human-in-the-loop requirements

The agent pauses and waits for a decision at these points. Gates 1–4 are non-negotiable;
gates 5–6 are a posture decision (Q-2).

| ID | Gate | Why |
| --- | --- | --- |
| HITL-1 | **Final submit** — every submission | Irreversible, goes out under Avadh's name (C-3) |
| HITL-2 | **Login / OTP / CAPTCHA / phone verification** | Agent cannot perform these (C-2) |
| HITL-3 | **Missing personal data** — salary expectation, notice period, current CTC, relocation commitment, work authorisation, sponsorship, employment-termination details, sensitive personal or demographic data | Not derivable from the resume; guessing risks misrepresentation |
| HITL-4 | **Any claim that could misrepresent Avadh** | Truthfulness is absolute (§6) |
| HITL-5 | **Tailored resume + cover letter approval — EVERY application** | **Decided v0.3:** full review, no spot-checking. See §10.3 C-B for the time cost at the chosen daily target. |
| HITL-6 | **Borderline scores (70–79)** | **Open** — see §10.2 O-3. Recommendation: fold into HITL-5 rather than add a second gate. |

**HITL-R1** — A paused application must be reviewable and resumable from the dashboard.
**HITL-R2** — Approval must offer at least: **approve · edit · reject**. `edit` matters — it is
how Avadh fixes one line of a cover letter without discarding the whole application.
**HITL-R3** — HITL-3 should be largely eliminated by a one-time **answer sheet** (Q-1). Without
it, nearly every application stalls (C-5). The agent should interrupt only for genuinely
novel questions.
**HITL-R4** — Pauses may last **days**. State must be durable, not in-memory.
**HITL-R5** — Resuming must never re-execute a side effect. An application submitted before a
pause must never be submitted twice.

---

## 6. Truthfulness constraints — non-negotiable

These override every other requirement, including daily targets.

| ID | Constraint |
| --- | --- |
| T-1 | **Never** invent experience, companies, projects, certifications, degrees, job titles, technologies, achievements, responsibilities, or years of experience. |
| T-2 | Tailoring may only reorder, re-emphasise, reword and foreground **facts already in the resume**. |
| T-3 | Never falsely claim a mandatory qualification (FR-4.3). |
| T-4 | Where the truthful answer is unknown, halt and ask (FR-9.4). Never fabricate to complete a form. |
| T-5 | Every generated claim must be traceable to a specific line of the resume. |

---

## 7. Technical requirements

| ID | Requirement |
| --- | --- |
| TR-1 | The agent must be built with **LangChain and LangGraph** (Python). |
| TR-2 | All LangChain/LangGraph APIs must be verified against `JobAgent/knowledge-base/` — LangChain 1.0 removed the legacy chain/agent abstractions, so recalled API shapes are unreliable. |
| TR-3 | The system needs a **backend** and a **frontend dashboard**. |
| TR-4 | The dashboard must show: the approval queue, the application tracker, daily reports, and per-job scores with reasoning. |
| TR-5 | Agent state must be **durably persisted** — runs survive process restarts and multi-day pauses (HITL-R4, FR-12.2). |
| TR-6 | Browser automation is required for ATS forms. It must operate against an authenticated session and hand control to Avadh when blocked (C-2). |
| TR-7 | Every LLM call, tool call and state transition must be traceable for debugging and cost tracking. |
| TR-8 | Secrets (API keys, credentials) must never be committed, logged, or sent to a job posting. |
| TR-9 | All work is committed and pushed to the `JobAgent` branch of `avadh-pro/LearningGenAI`. |

---

## 8. Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-1 | **Durability** — no loss of application state across restarts or day-long pauses. |
| NFR-2 | **Idempotency** — no duplicate submissions under any retry, resume or crash-recovery path. |
| NFR-3 | **Auditability** — for any application, reconstruct what was sent, when, and on what evidence. |
| NFR-4 | **Recoverability** — one board failing must not abort the run. |
| NFR-5 | **Rate limiting** — respectful request pacing; no behaviour resembling an attack. |
| NFR-6 | **Cost visibility** — per-run LLM spend must be observable. |
| NFR-7 | **Privacy** — resume and personal data stay in Avadh's control; no third-party services beyond those required to apply. |

---

## 9. Success metrics

| Metric | Target |
| --- | --- |
| Interview / callback rate per application | **Primary metric.** Beat manual applying. |
| Applications per day | 5–15, scaled to genuine availability |
| Fabricated claims | **Zero. Non-negotiable.** |
| Duplicate applications | **Zero** |
| Below-threshold applications (< 70) | **Zero** |
| Avadh's time per application | Minutes, not hours |
| Runs completing without manual rescue | > 90% |

---

## 10. Decisions, open items and conflicts

### 10.1 Decided (v0.3)

| # | Decision |
| --- | --- |
| **Q-1** | **Answer sheet** — Current CTC ₹19.8 LPA · Expected ₹32 LPA · Notice 1 month. Three fields still open (O-2). See §2.1. |
| **Q-2** | **Review posture** — **full human review of every tailored resume and cover letter.** No spot-checking. HITL-6 still open (O-3). |
| **Q-3** | **Board policy** — LinkedIn / Naukri / Indeed are **discovery-only**. Automated submission is restricted to **Greenhouse, Lever, Workday and direct career pages**. Accepts the safe posture under C-1. |
| **Q-4** | **Resume master** — ✅ **CLOSED.** `JobAgent/resume/resume-ats.html` is the single master; `render.py` regenerates the PDF. No DOCX, no LaTeX. C-4 resolved. |
| **Q-5** | **Runtime** — Avadh's **local PC**, not a server. |
| **Q-6** | **Schedule** — daily run at **09:00**. Rollover policy still open (O-5). |
| **Q-7** | **Notifications** — **Telegram**, for both approvals and the daily report. |
| **Q-8** | **Budget** — **$100/day ceiling**, with running spend visible in the UI. Provider still open (O-4). |
| **Q-9** | **Data retention** — **keep everything, indefinitely**, stored locally. JDs, generated letters and tracker history. |
| **New** | **Daily target** — **30–40 applications/day, configurable from the UI.** See FR-9.2 and §10.3 C-A. |
| **New** | **UI visibility** — every functional requirement needs a UI component. See §4.13. |
| **New** | **Geography** — expand to Dubai/UAE, Europe and Canada. See FR-1.3, FR-1.3a. |
| **New** | **Search audit log** — daily per-source, per-query, per-job log doubling as the manual-fallback surface. See FR-1.8, FR-1.9. |

### 10.2 Still open

| ID | Question | Why it matters |
| --- | --- | --- |
| **O-1** | **FR-6.1 is incomplete** — the sentence was cut off at *"you are saying that when the…"*. Needs finishing. | Cannot be specified as written. |
| **O-2** | **Relocation stance · work authorisation · preferred start date.** For work authorisation, confirm: Indian citizen, no existing EU/Canada/UAE work permit, sponsorship required? | **Now load-bearing.** With FR-1.2 adding Europe and Canada, this is the hard filter deciding which international roles are even eligible (FR-1.3a). Without it the agent cannot tell an applicable role from an impossible one. |
| **O-3** | **HITL-6** — is a borderline 70–79 score a separate gate before a resume is even generated, or covered by the full HITL-5 review? | **Recommendation: fold into HITL-5.** A second gate doubles the interruptions to reject work that the first gate would reject anyway. The one argument for a separate gate is cost — it avoids paying to tailor a resume that then gets rejected. At the §10.1 budget, that cost is not material. |
| **O-4** | **LLM provider.** | Both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are already set at User scope on this machine. **Recommendation: Anthropic Claude** as the default, given the resume-tailoring and JD-reasoning workload, with the provider configurable — LangChain makes this a one-line change (`model="claude-sonnet-4-6"` vs `"openai:gpt-5.5"`). |
| **O-5** | **Pending-approval rollover.** What happens to yesterday's unapproved applications when 09:00 hits today? | **Recommendation: carry over, never auto-submit, never auto-expire.** Queue them ahead of the new batch, and flag any posting that has since closed as `expired` so Avadh is not reviewing dead jobs. Auto-expiry silently discards work; auto-submission violates HITL-1. |

### 10.3 ⚠️ Conflicts between decisions — resolve before the spec

These are not new questions. They are places where two decisions already made cannot both hold.

| ID | Conflict |
| --- | --- |
| **C-A** | **30–40/day vs. every other constraint.** §1 sets the objective as *interview probability per application, not volume*, and FR-9.2 says never pad to hit a number. FR-3 rejects anything under 70. Q-3 restricts auto-submission to Greenhouse / Lever / Workday / career pages. **Finding 30–40 genuinely matching Senior/Staff AI roles per day on ATS platforms alone is very unlikely** — realistic supply is single digits most days. The target is therefore recorded as a **ceiling, not a quota**, and the honest expectation is that actual daily volume will be far lower. If the intent is genuinely to apply to 30–40 per day, something must give: the 70 threshold, the seniority filter, or the discovery-only board policy. **Recommendation: keep it as a ceiling and let supply decide.** |
| **C-B** | **30–40/day vs. full manual review.** Q-2 requires Avadh to review every tailored resume and cover letter. At 30–40/day that is 30–40 documents to read daily — plausibly 2–4 hours, which is more time than applying manually would take. **Recommendation: keep full review for the first week to calibrate, then move to spot-checking above a score threshold.** Alternatively accept that C-A caps real volume low enough that full review stays cheap. |
| **C-C** | **Europe / Canada vs. work authorisation.** If Avadh needs sponsorship, the large majority of European and Canadian postings are ineligible and must be rejected under FR-4.2 — not applied to. Until O-2 is answered, FR-1.2 cannot be implemented correctly, and implementing it wrongly wastes the daily budget on applications that cannot succeed. **Dubai/UAE is the exception** — employer-sponsored work permits are the norm there, so it is the highest-value part of this expansion. |
| **C-D** | **$100/day vs. expected usage.** The ceiling is roughly ₹8,300/day, about ₹2.5L/month. Realistic spend for 30–40 scored jobs with tailored documents is likely **one to two orders of magnitude below** that. Recorded as a generous ceiling rather than a budget. **Recommendation: add a soft alert at a far lower threshold** (say $5/day) so a runaway loop is caught by the alert rather than by the ceiling. |

### 10.4 Note on the suggested resume phrasing

The v0.3 review proposed this line for the resume:

> *"Owned an AI-driven job application agent end-to-end at a startup — from requirements and
> architecture through integration, demos, optimisation, and production support — as sole engineer."*

⚠️ **This describes JobAgent — this project — not the Krista work.** Presenting it as Krista
work experience would breach **T-1**. The end-to-end lifecycle claim is already on the resume,
correctly attributed to Krista, and was strengthened in the v3 resume:

> **End-to-end solution ownership** in a startup environment — requirements, architecture,
> integration, demos, optimization and production support — across enterprise customer
> engagements, from first scoping call to live production.

Once JobAgent is actually built and running, it is a legitimate and strong **personal project**
entry — a LangGraph multi-agent system with durable HITL. It just belongs under Projects, not
under Krista Software.

---

## 11. Approval

**Blocking the spec:** the five open items in §10.2 and the four conflicts in §10.3.
**O-2 (work authorisation) and C-A / C-B are the ones that change the architecture.**

- [x] §1–2 objective and profile are correct
- [x] §2.1 answer sheet — 3 of 6 fields decided, 3 open (O-2)
- [ ] §3 scope and constraints — updated for international, needs re-read
- [ ] §4 functional requirements — FR-6.1 incomplete (O-1)
- [x] §5 HITL gates — HITL-5 decided, HITL-6 open (O-3)
- [x] §6 truthfulness constraints
- [ ] §7–8 technical and non-functional requirements
- [x] §9 success metrics — ⚠️ see C-A, the daily target contradicts §1's stated objective
- [ ] §10.2 five open items answered
- [ ] §10.3 four conflicts resolved

**On approval → technical specification.**

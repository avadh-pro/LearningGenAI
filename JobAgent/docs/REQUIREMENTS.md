# JobAgent — Requirements

**Project:** Autonomous AI/ML Job Search & Application Agent
**Owner:** Avadh Dobariya
**Status:** 🟡 Draft — awaiting review
**Version:** 0.2 · 2026-09-14

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
- Roles requiring relocation outside India (see FR-1.3 for the narrow exception)

### 3.3 Hard external constraints

These are facts about the environment, not design choices. They bound what is buildable.

| ID | Constraint |
| --- | --- |
| C-1 | LinkedIn, Naukri and Indeed prohibit automated applying in their terms of service and run bot detection. Automating submission there carries a real risk of account restriction on Avadh's personal accounts. |
| C-2 | CAPTCHAs, OTPs, SMS/phone verification and login flows cannot be completed by the agent. They require Avadh. |
| C-3 | Application submission is **irreversible**. There is no unsend. |
| C-4 | The resume exists only as a PDF today. Per-application tailoring (FR-6) requires an editable master. **This blocks FR-6.** |
| C-5 | Most Indian application forms demand data absent from the resume — current CTC, expected CTC, notice period, relocation willingness. Under FR-9.4 every one of these would halt an application. |
| C-6 | This repo hits the Windows 260-char `MAX_PATH` limit. Deep nested paths break git operations. |

---

## 4. Functional requirements

### 4.1 Discovery

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1.1 | Search daily for newly posted and still-active roles across LinkedIn, Indeed, Wellfound, Naukri, Greenhouse, Lever, Workday, and direct company career pages. | Must |
| FR-1.2 | Prioritise **direct company career pages and ATS links** over aggregators — better data, and outside the C-1 risk. | Must |
| FR-1.3 | Location priority: Remote → Pune → Bengaluru → Hyderabad → Mumbai → Delhi NCR → other major Indian tech hubs. International remote allowed only where the posting explicitly permits candidates working from India. Reject roles requiring relocation abroad unless relocation is explicitly supported **and** the opportunity is exceptional. | Must |
| FR-1.4 | Seniority: target Senior / Staff / Lead / Senior IC / Architect. Consider mid-level only for exceptionally strong companies. Never junior, entry-level, internship, graduate or trainee. | Must |
| FR-1.5 | Search the target titles (§4.1.1) crossed with GenAI keywords: RAG, LLM, Agentic AI, MCP, GenAI, AI Agents, LangChain, LangGraph, LLMOps, Enterprise AI. Search both `Forward Deployed` and the abbreviation `FDE` — postings use either. | Must |

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
| FR-6.4 | ⛔ **Blocked by C-4** — requires an editable master (DOCX, or an HTML/LaTeX source rendering to a near-identical PDF). Producing that master is a prerequisite deliverable. | Must |

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
| FR-9.2 | Target **5–15 high-quality applications per day**, scaled to genuine availability. If only 2 good jobs exist, apply to 2. Never pad to hit a number. | Must |
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
| HITL-5 | **Tailored resume + cover letter approval** | Posture decision — Q-2 |
| HITL-6 | **Borderline scores (70–79)** | Judgement call under FR-3; a human glance may be worth it |

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

## 10. Open questions — needed before the spec

Each of these changes the design. None has been guessed at.

| ID | Question | Why it matters |
| --- | --- | --- |
| **Q-1** | **The answer sheet.** Current CTC, expected CTC, notice period, relocation stance, work authorisation (Indian citizen, no sponsorship required?), preferred start date. | Without it, C-5 means nearly every application halts at HITL-3. This is the single highest-value unblock. |
| **Q-2** | **Review posture.** Full review of every tailored resume + cover letter (HITL-5), or spot-check after the agent proves itself? And do borderline 70–79 scores (HITL-6) need a human yes/no? | Determines how much of Avadh's time the system costs, and how autonomous v1 really is. |
| **Q-3** | **Board policy under C-1.** Should LinkedIn / Naukri / Indeed be **discovery-only** (safe), with automated submission restricted to Greenhouse / Lever / Workday / career pages? Or accept the account-restriction risk? | Directly bounds reachable volume, and risks Avadh's personal accounts. **Recommendation: discovery-only.** |
| **Q-4** | **Resume master format** (C-4). Supply a DOCX, or have an HTML/LaTeX source generated from the current PDF? | Hard blocker on FR-6. |
| **Q-5** | **Where does it run?** Avadh's Windows machine, or a server? | Browser automation (TR-6) needs an authenticated session; a server complicates C-2 handoffs. |
| **Q-6** | **Daily run time**, and what happens to a run still awaiting approval when the next day starts? | Shapes scheduling and concurrency. |
| **Q-7** | **Notification channel** for approvals and the daily report — dashboard only, email, or Telegram? | A gate nobody sees is a stalled application. |
| **Q-8** | **LLM provider and budget ceiling** per day. | Anthropic and OpenAI keys are already available on this machine. |
| **Q-9** | **Data retention** — how long are scraped JDs, generated letters and tracker history kept? | Privacy (NFR-7) and storage growth. |

---

## 11. Approval

Review §10 first — those answers unblock the spec. Everything above §10 is a restatement of
intent and should be corrected wherever it misses.

- [ ] §1–2 objective and profile are correct
- [ ] §3 scope and constraints are accepted
- [ ] §4 functional requirements are complete
- [ ] §5 HITL gates are right
- [ ] §6 truthfulness constraints are right
- [ ] §7–8 technical and non-functional requirements are accepted
- [ ] §9 success metrics are right
- [ ] §10 open questions answered

**On approval → technical specification.**

# Resume — ATS-optimised master

The editable master resume for JobAgent, and the fix for the parser defects measured in the
original PDF. This also unblocks **FR-6 / Q-4** in [`../docs/REQUIREMENTS.md`](../docs/REQUIREMENTS.md):
the agent cannot tailor a PDF, but it can tailor this HTML source.

| File | What it is |
| --- | --- |
| `resume-ats.html` | **The master.** Edit this, never the PDF. |
| `render.py` | Renders the HTML to PDF via headless Chromium. `python render.py` |
| `Avadh_Dobariya_Senior_AI_Solution_Engineer_ATS.pdf` | Generated output — the file to upload |

The original design (`Avadh_Dobariya_Senior_AI_Solution_Engineer.pdf`) is still the better
**human-facing** resume — keep sending it to recruiters and warm intros. This variant is for
**ATS submission**.

---

## Measured results

Tested with three parsers — **pdfminer**, **pypdf** and **PyMuPDF** — because ATS pipelines are
built on different ones and they disagree.

| Metric | Original | ATS variant |
| --- | --- | --- |
| Pages | 1 | 1 |
| Layout | 23 left / 16 right blocks (two-column) | 19 left / **0 right** (single column) |
| Images (photo + icons) | 3 | **0** |
| Emoji in text layer | 10 | **0** |
| **Reading-order probes passed** | **7/15 (47%)** | **15/15 (100%)** |
| LinkedIn URL | `linkedin.com/in/avadh-dobariya-` ❌ truncated | `...avadh-dobariya368935208` ✅ intact |
| Keywords (raw text) | 67/74 | **74/74** |
| Keywords (normalised) | 70/74 | **74/74** |
| Clickable links | 2 | 3 |
| Unnamed font subsets | 6 | **0** |
| **Factual integrity** | — | **49/49 original facts preserved** |

**Score: 71/100 → 96/100.** The remaining 4 points are a deliberate trade: the page is 94% full
at 9.3pt body text, which is dense for a human reader. That is the cost of one page.

---

## What was wrong, and what fixed it

### 1. Two-column layout scrambled reading order

pdfminer coped; **pypdf and PyMuPDF did not**. Skill labels landed in one block and their values
in another. Measured gaps between a heading and its own content:

| Heading | Distance to its content |
| --- | --- |
| `EDUCATION` → "MIT Academy" | **757 chars** |
| `Languages & Backend` → "PostgreSQL" | 682 chars |
| `Retrieval & Vector Stores` → "Qdrant" | 416 chars |

→ **Fixed: single column.** All 15 probes now pass across all three parsers.

### 2. The LinkedIn URL was a dead link

```
linkedin.com/in/avadh-dobariya-
368935208
```

The URL wrapped mid-string and the renderer inserted a soft hyphen. Any ATS capturing the link
field got `linkedin.com/in/avadh-dobariya-`, which resolves to nothing.

→ **Fixed:** `white-space: nowrap` on the URL, and it is now a real `<a href>` so it is clickable
as well as extractable.

> ⚠️ **Still worth doing on LinkedIn's side:** set a custom vanity URL
> (e.g. `linkedin.com/in/avadhdobariya`). Shorter, more memorable, and structurally incapable of
> wrapping. The current URL was kept verbatim rather than invented.

### 3. The narrow sidebar snapped keywords in half

The sidebar was ~30 characters wide, so multi-word terms broke across lines and exact-phrase
matching failed:

| Keyword | Original | ATS variant |
| --- | --- | --- |
| `Hybrid Search` | `Hybrid\nSearch` — **split** | intact |
| `Function Calling` | `Function\nCalling` — **split** | intact |
| `production support` | `production\nsupport` — **split** | intact |
| `Tool Calling` | absent | intact |

→ **Fixed:** wider single column, plus `.nw` (nowrap) spans around every multi-word term that
matters for matching.

### 4. Emoji and symbols in the text layer

10 emoji, glued directly to headings — `🛠SKILLS`, `👤PROFESSIONAL SUMMARY`, `💼WORK EXPERIENCE`.
Substring matching survived; exact heading matching did not. They also pulled in **6 unnamed font
subsets** (`F9`–`F14`). The U+2192 arrows (`→`) in the summary carried the same risk.

→ **Fixed:** zero characters above U+2100. Two named fonts only (`Arial-BoldMT`, `ArialMT`).

### 5. The photo

A 400×400 headshot. Fine for India; a liability for US/global roles, where bias-avoidance
policies mean some pipelines strip or flag resumes containing photos.

→ **Fixed:** removed from this variant. Keep the original for markets where a photo helps.

---

## Content changes

Only **three** terms were added, each already evidenced elsewhere in the resume:

| Added | Justification |
| --- | --- |
| `LLM Observability` | Already lists LLM Tracing (Opik), Grafana/Prometheus, Datadog |
| `AI Orchestration` | Already describes multi-agent systems and agent orchestration work |
| `Semantic Search` | Already describes hybrid lexical + vector retrieval |

**`End-to-end solution ownership`** was promoted from a buried clause to its own bolded bullet,
with `production support` restored to the lifecycle chain (it was already in the resume, in a
different bullet). This is deliberate: it is the single strongest signal for
**Forward Deployed Engineering** roles (§4.1.2 of the requirements), where owning the customer
lifecycle from scoping to production *is* the job.

**Nothing was invented.** Verified: 49/49 original facts preserved, and a token-level diff against
the original shows no new claims beyond the three terms above.

Deliberately **not** added, despite being common in job descriptions: Azure, GCP, Weaviate, FAISS,
pgvector, MLOps, TypeScript, Terraform. They are not in the resume, and adding them would violate
constraint **T-1** (no fabrication) in the requirements.

---

## Editing

```bash
# edit resume-ats.html, then:
python render.py
```

**Rules when editing:**

1. **Never add a claim not supported by the source resume.** (T-1)
2. Wrap any multi-word keyword that matters for matching in `<span class="nw">`.
3. Keep it to one page — `render.py` output is checked; page 2 means trim.
4. No emoji, no arrows, no characters above U+2100.
5. Stay single-column. No tables, no text boxes, no images.

**Requirements:** Python 3.13 · `playwright` · Chromium. `render.py` pins the executable path;
override with the `PW_CHROME` environment variable if your Playwright revision differs.

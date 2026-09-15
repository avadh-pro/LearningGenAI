# Discovery spike

**Status:** throwaway. Nothing here is production code, nothing here is on the phase plan, and
none of it should be imported by `src/jobagent/`.

## Why this exists

The CTO review of SPEC v1.0 raised ten CRITICALs, all of which v2 closes. Its sharpest *non*-defect
criticism was about sequencing, and v2 does not answer it:

> the plan is 115–190 implementer-days for one person — six to nine months elapsed — and it
> sequences the question "is there anything on these sources to apply to?" (T-4.2, blocker Q-B)
> into month four. For a system whose purpose is to get its owner a job, that ordering is backwards
> on the only axis that matters.

Risk **R-5** ("discovery yield too low on the submit-capable sources because the watchlist is
empty / boards are sparse") is rated **High likelihood** in SPEC §16. If it fires, most of the
Area A machinery — the submission protocol, the double-submission guards, the whole of §9 — is
elaborate plumbing for a trickle. That is a two-day question being answered in month four.

This spike answers it in minutes.

## What it does

For every company in `watchlist-seed.csv`, probe the public board feeds:

* Greenhouse — `https://boards-api.greenhouse.io/v1/boards/<slug>/jobs`
* Lever — `https://api.lever.co/v0/postings/<slug>?mode=json`

then count postings that clear a cheap AI/ML title filter and land in a reachable location
(India, remote, or an FR-1.3 target geography).

**Every slug in the seed file is a guess.** Turning those guesses into verified facts is half the
value: a company that resolves nowhere is telling you it is not auto-submittable through the two
ATSs this system can actually submit to, which is a finding, not an error.

## What it is not

* **Not the rubric.** The real gate is a ≥ 70 LLM score across seven weighted dimensions
  (SPEC §4.6), plus fourteen hard eligibility rules (§4.5). This is a regex. **Every number it
  prints is an upper bound** on what would reach the review queue — in practice, expect the rubric
  and hard rules to cut it substantially.
* **Not dedup.** One requisition posted to three locations counts three times.
* **Not a freshness oracle.** Greenhouse exposes `updated_at`, not `posted_at`, so its ages are
  soft. Lever's `createdAt` is real.

## Running it

```
python discovery_spike.py                 # stdlib only; no install needed
python discovery_spike.py --delay 2.0     # gentler pacing
python discovery_spike.py --seed my.csv --out out2
```

Sequential, jittered delay, identifying User-Agent. These are public JSON endpoints, but there is
no reason to hammer them.

## Reading the output

| File | What it holds |
| --- | --- |
| `out/boards.csv` | one row per company — which ATS resolved, the working slug, total postings |
| `out/roles.csv` | one row per matching posting — title, location, bucket, age, URL |
| `out/summary.md` | the decision numbers, and how to read them for **Q-S** |

The number that matters is **reachable matching roles dated within 30 days, expressed per week**.

* **Thin** (< ~5/week *before* the rubric cuts it) → ship the non-submitting product first
  (SPEC Q-S). Documents-only mode plus the by-hand list tailors, verifies and hands over; it
  cannot double-submit because it cannot submit; it ships months earlier; and it turns the entire
  Area A risk surface into a later decision made with real operating experience.
* **Healthy** (comfortably double digits/week pre-rubric) → supply is not the constraint, the
  10–20/day ceiling is, and the full build earns its keep.

## Fixing the seed list

A company showing `unresolved` means one of two things:

1. **Wrong slug.** Open the company's careers page, look at the apply link — if it points at
   `boards.greenhouse.io/<slug>` or `jobs.lever.co/<slug>`, put that slug in the CSV and re-run.
   This is the common case and is worth ten minutes.
2. **Different ATS.** Workday, Ashby, SmartRecruiters, Darwinbox and in-house boards are not
   probed here. Workday is *assisted* mode in the spec (SPEC §9.7) and the rest are career-page
   or discovery-only — real supply, but not auto-submittable, which is exactly the distinction
   Q-S turns on.

When the list is right, it becomes the seed for **Q-B** and drops into `company_watchlist`
(SPEC §4.2, §6.3) largely as-is.

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

For every company in `watchlist-seed.csv`, probe the public board feeds, then count postings that
clear a cheap AI/ML title filter and land in a reachable location (India, remote, or an FR-1.3
target geography).

Boards are probed in two **tiers**, and the summary never blends them:

| Tier | ATS | Endpoint | Why it is its own tier |
| --- | --- | --- | --- |
| **1** | Greenhouse | `boards-api.greenhouse.io/v1/boards/<slug>/jobs` | SPEC §4.2 auto-submit adapter |
| **1** | Lever | `api.lever.co/v0/postings/<slug>?mode=json` | SPEC §4.2 auto-submit adapter |
| **2** | Ashby | `api.ashbyhq.com/posting-api/job-board/<slug>` | structured, but **not** in the v1 adapter set |
| **2** | SmartRecruiters | `api.smartrecruiters.com/v1/companies/<slug>/postings` | same |

**Tier 1 is the number Q-S turns on** — it is the supply the system can submit to *as specified*.
Tier 2 is real supply that today lands in the by-hand list; adding those adapters is a v1.1
question, and quantifying them is how you decide whether it is worth asking.

**Every slug in the seed file started as a guess.** `slug_hunt.py` turns the guesses into facts:
it generates slug variants per company and probes all four ATSs, so that an unresolved company can
be diagnosed rather than merely counted. That distinction is the point —

* **wrong slug** → fixable in seconds, and the company *is* auto-submittable;
* **different ATS** → real supply, but assisted or by-hand mode, not auto-submit.

```
python slug_hunt.py            # only companies unresolved in out/boards.csv
python slug_hunt.py --all      # re-verify everything
python slug_hunt.py --apply    # write the verified slugs back into the seed CSV
```

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
| `out/boards.csv` | one row per company — which ATS resolved, its tier, the working slug, total postings |
| `out/roles.csv` | one row per matching posting — title, location, bucket, age, URL |
| `out/slug-hunt.csv` | per-company verdict from `slug_hunt.py`: found on which ATS, or `not_found` |
| `out/summary.md` | the decision numbers, and how to read them for **Q-S** |

The number that matters is **reachable matching roles dated within 30 days, expressed per week**.

* **Thin** (< ~5/week *before* the rubric cuts it) → ship the non-submitting product first
  (SPEC Q-S). Documents-only mode plus the by-hand list tailors, verifies and hands over; it
  cannot double-submit because it cannot submit; it ships months earlier; and it turns the entire
  Area A risk surface into a later decision made with real operating experience.
* **Healthy** (comfortably double digits/week pre-rubric) → supply is not the constraint, the
  10–20/day ceiling is, and the full build earns its keep.

## What the slug hunt settled

The first run left 29 of 50 companies unresolved, and the obvious hope was that most were typos —
which would have raised the tier-1 number. `slug_hunt.py` tested that hope directly and killed it:

> **0 of the 29 were wrong Greenhouse/Lever slugs.** Nine were on Ashby or SmartRecruiters
> (tier 2), and 21 are on ATSs outside all four probed.

So the tier-1 supply figure is not an artefact of a sloppy seed list. It is the real ceiling for
the adapters the spec actually builds, and it does not move by fixing slugs.

A company still showing `not_found` is on Workday, Darwinbox, Keka, Taleo, iCIMS or an in-house
board. Workday is *assisted* mode (SPEC §9.7); the rest are career-page or discovery-only. All of
it is real supply — none of it is auto-submittable — and that is precisely the distinction Q-S
turns on.

When the list is right, it becomes the seed for **Q-B** and drops into `company_watchlist`
(SPEC §4.2, §6.3) largely as-is — with `ats_guess` now carrying a *verified* value rather than a
guess, which is worth more than the column name suggests.

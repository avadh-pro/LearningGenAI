# Discovery spike — results

Run: 2026-09-15T12:38:56+00:00  ·  seed: `watchlist-seed.csv`

**Read the caveats in `discovery_spike.py` before quoting any number.** This is a
title/location prefilter, not the rubric, so every count below is an **upper bound**
on what would actually reach the review queue.

## Board reachability (this is the half that is a hard fact)

- Companies probed: **50**
- Boards resolved **with live postings**: **29** — **20 on tier 1** (Greenhouse/Lever — the spec's auto-submit adapters) and **9 on tier 2** (Ashby/SmartRecruiters — structured, but not in the v1 adapter set)
- Boards resolved but **empty**: **0** — a board counts as resolved only if it returns postings. SmartRecruiters answers 200 with `totalFound: 0` for any unknown company, so an empty response is not evidence a board exists.
- Unresolved (not on Greenhouse/Lever under the guessed slug): **21**
- Total postings visible across resolved boards: **4898**

## Supply after the AI/ML prefilter

- Matching roles, all locations: **395**

Now the location haircut, which is where the naive reading goes wrong:

- India-based: **58**
- Remote **and naming India**: **0**
- Remote but country-scoped elsewhere (Remote-US, Portugal-Remote, …): **58** — these die at eligibility rule 10/11
- Target geographies (UK/EU/Canada/UAE): **53** — rules 11/12 reject these unless sponsorship is offered, which the listings do not state

**Genuinely reachable: 58**, of which **38** are dated within 30 days
→ **~8.9 roles/week**, and that is still an upper bound: the ≥ 70 rubric, the
seniority rules, the mandatory-qualification rule and dedup all cut it further.

Split by what the system can actually do with them:

- **Tier 1 — auto-submittable today** (Greenhouse/Lever): **40** reachable, **~7.0/week**. *This is the number Q-S turns on.*
- **Tier 2 — structured but out of scope** (Ashby/SmartRecruiters): **18** reachable, **~1.9/week**. Adding these adapters is a v1.1 question; until then they are by-hand supply.

Concentration: the top four companies supply **60%** of the reachable pool.

## Top companies by reachable matching roles

| Company | Reachable matching roles |
| --- | --- |
| Databricks | 12 |
| Sarvam AI | 10 |
| Meesho | 7 |
| Glean | 6 |
| MongoDB | 5 |
| Freshworks | 4 |
| Swiggy | 3 |
| Elastic | 2 |
| GitLab | 2 |
| Rubrik | 2 |
| Observe.AI | 2 |
| Snowflake | 1 |
| Twilio | 1 |
| Stripe | 1 |

## How to read this for Q-S

The decision this spike exists to inform is **Q-S** (SPEC §19): ship the
non-submitting product first, or build automated submission now.

- **Thin pool** (< ~5 reachable fresh roles/week *before* the rubric cuts it):
  automated submission is months of work for a trickle. Ship documents-only, use
  the by-hand list for Naukri/LinkedIn, and revisit with real operating data.
- **Healthy pool** (comfortably into double digits/week pre-rubric): the daily
  ceiling of 10-20 is the binding constraint rather than supply, and the full
  build earns its keep.

**Measurement completeness is the caveat that matters.** Read the unresolved list
below before concluding anything: every unresolved board is supply this run could
not see. If a meaningful share of them are wrong slugs rather than other ATSs,
the reachable number moves. Fixing the slugs costs about thirty minutes and is
worth doing *before* this result is used to settle Q-S.

## Unresolved companies

These are not on Greenhouse or Lever under the slugs guessed in the seed file.
Either the slug is wrong (fixable — check the company's careers page and correct
`watchlist-seed.csv`) or they use another ATS (Workday, Ashby, SmartRecruiters,
Darwinbox), which means discovery-only or assisted mode, not auto-submit.

- HashiCorp (`hashicorp`)
- Atlassian (`atlassian`)
- Nutanix (`nutanix`)
- Weights & Biases (`weightsandbiases|wandb`)
- Razorpay (`razorpay`)
- PhonePe (`phonepe`)
- Sprinklr (`sprinklr`)
- Chargebee (`chargebee`)
- Hasura (`hasura`)
- Harness (`harness`)
- BrowserStack (`browserstack`)
- Innovaccer (`innovaccer`)
- Uniphore (`uniphore`)
- Yellow.ai (`yellowai|yellowmessenger`)
- Gupshup (`gupshup`)
- Fractal Analytics (`fractalanalytics|fractal`)
- Quantiphi (`quantiphi`)
- Icertis (`icertis`)
- MoEngage (`moengage`)
- Darwinbox (`darwinbox`)
- Zepto (`zepto|kiranakart`)

# Discovery spike — results

Run: 2026-09-15T12:02:44+00:00  ·  seed: `watchlist-seed.csv`

**Read the caveats in `discovery_spike.py` before quoting any number.** This is a
title/location prefilter, not the rubric, so every count below is an **upper bound**
on what would actually reach the review queue.

## Board reachability (this is the half that is a hard fact)

- Companies probed: **50**
- Boards resolved **with live postings**: **20** — these are the auto-submittable surface
- Boards resolved but **empty**: **1** (slug likely right, nothing posted publicly right now)
- Unresolved (not on Greenhouse/Lever under the guessed slug): **29**
- Total postings visible across resolved boards: **4069**

## Supply after the AI/ML prefilter

- Matching roles, all locations: **306**

Now the location haircut, which is where the naive reading goes wrong:

- India-based: **40**
- Remote **and naming India**: **0**
- Remote but country-scoped elsewhere (Remote-US, Portugal-Remote, …): **50** — these die at eligibility rule 10/11
- Target geographies (UK/EU/Canada/UAE): **48** — rules 11/12 reject these unless sponsorship is offered, which the listings do not state

**Genuinely reachable: 40**, of which **30** are dated within 30 days
→ **~7.0 roles/week**, and that is still an upper bound: the ≥ 70 rubric, the
seniority rules, the mandatory-qualification rule and dedup all cut it further.

Concentration: the top four companies supply **75%** of the reachable pool.

## Top companies by reachable matching roles

| Company | Reachable matching roles |
| --- | --- |
| Databricks | 12 |
| Meesho | 7 |
| Glean | 6 |
| MongoDB | 5 |
| Elastic | 2 |
| GitLab | 2 |
| Rubrik | 2 |
| Observe.AI | 2 |
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

- Confluent (`confluent`)
- HashiCorp (`hashicorp`)
- Snowflake (`snowflakecomputing|snowflake`)
- Atlassian (`atlassian`)
- Nutanix (`nutanix`)
- Weights & Biases (`weightsandbiases|wandb`)
- LangChain (`langchain`)
- Temporal (`temporaltechnologies|temporal`)
- Airbyte (`airbyte`)
- Razorpay (`razorpay`)
- Swiggy (`swiggy`)
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
- Sarvam AI (`sarvamai|sarvam`)
- Fractal Analytics (`fractalanalytics|fractal`)
- Quantiphi (`quantiphi`)
- Icertis (`icertis`)
- MoEngage (`moengage`)
- Whatfix (`whatfix`)
- Darwinbox (`darwinbox`)
- Zepto (`zepto|kiranakart`)

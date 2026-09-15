"""
JobAgent discovery spike — two-day throwaway, NOT production code.

Question it answers
-------------------
"Is there anything on the submit-capable sources worth applying to?"

The CTO review's sharpest non-defect finding was that the v1 plan sequences this
question (T-4.2, blocker Q-B) into month four of a six-to-nine-month build, on a
project whose purpose is getting its author hired. R-5 rates the risk of a thin
pool as HIGH. This script answers it in minutes instead, by probing the public
board feeds of a seed watchlist and counting roles that clear a cheap prefilter.

What it is NOT
--------------
* It is NOT the rubric. The real gate is a >= 70 LLM score across seven weighted
  dimensions (SPEC §4.6). This uses a title/location regex, so every number it
  prints is an UPPER BOUND on the real queue. It answers "is the pool big enough
  to be worth scoring", not "how many score >= 70".
* It is NOT the dedup module. The same requisition posted to two locations counts
  twice here.
* `updated_at` on Greenhouse is not `posted_at`. Freshness from Greenhouse is
  therefore soft; Lever's `createdAt` is a real creation date.

Design notes
------------
* Standard library only, so it runs on a clean Python 3.13 with no install.
* Sequential with a jittered delay. These are public JSON endpoints, but there is
  no reason to hammer them; pacing mirrors SPEC §4.2 in spirit (A-21).
* Every slug in the seed list is a GUESS. The script's first job is to turn those
  guesses into verified facts: it probes Greenhouse and then Lever for each
  candidate and records which, if either, resolved. A row that resolves nowhere is
  data ("this company is not on a board we can auto-submit to"), not a failure.

Usage
-----
    python discovery_spike.py                     # uses watchlist-seed.csv
    python discovery_spike.py --delay 2.0         # be gentler
    python discovery_spike.py --seed other.csv --out out2

Outputs (UTF-8, under --out):
    boards.csv    one row per company: which ATS resolved, slug, total postings
    roles.csv     one row per matching posting
    summary.md    the decision numbers
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "JobAgent-discovery-spike/0.1 (personal job search; contact via repo owner)"
GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER = "https://api.lever.co/v0/postings/{slug}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
SMARTRECRUITERS = "https://api.smartrecruiters.com/v1/companies/{slug}/postings"

# Tier 1 is what SPEC §4.2 can actually auto-submit to. Tier 2 is structured and
# plausible for the career-page mapper agent (§5.4) but is NOT in the v1 adapter
# set, so its supply must never be blended into the tier-1 number.
TIER = {"greenhouse": 1, "lever": 1, "ashby": 2, "smartrecruiters": 2}

# --- the prefilter -----------------------------------------------------------
# Deliberately generous: this is a supply question, not a scoring question.
AI_RE = re.compile(
    r"\b("
    r"ai|a\.i\.|artificial intelligence|machine learning|\bml\b|mlops|ml ops|"
    r"gen ?ai|generative ai|llm|llms|nlp|deep learning|data scien(ce|tist)|"
    r"applied scien(ce|tist)|computer vision|\bcv\b|rag|agentic|agents?"
    r")\b",
    re.I,
)
# Roles shaped like his: solution/forward-deployed/applied engineering.
SHAPE_RE = re.compile(
    r"\b("
    r"forward[- ]deployed|solutions? (engineer|architect|consultant)|"
    r"ai engineer|applied (ai|ml)|platform engineer|software engineer|"
    r"technical (account|program) manager|developer advocate|sales engineer"
    r")\b",
    re.I,
)
EXCLUDE_RE = re.compile(
    r"\b(intern|internship|graduate|trainee|apprentice|junior|working student|"
    r"phd student|fresher|campus)\b",
    re.I,
)

INDIA_RE = re.compile(
    r"\b(india|bengaluru|bangalore|mumbai|pune|hyderabad|chennai|gurgaon|"
    r"gurugram|noida|delhi|kolkata|ahmedabad|jaipur|indore|trivandrum|kochi)\b",
    re.I,
)
REMOTE_RE = re.compile(r"\bremote|anywhere|work from home|distributed\b", re.I)
# FR-1.3 target geographies beyond India.
TARGET_GEO_RE = re.compile(
    r"\b(uae|dubai|abu dhabi|united kingdom|\buk\b|london|ireland|dublin|"
    r"germany|berlin|munich|netherlands|amsterdam|france|paris|spain|madrid|"
    r"barcelona|poland|warsaw|portugal|lisbon|sweden|stockholm|canada|toronto|"
    r"vancouver|montreal|europe|emea)\b",
    re.I,
)


def fetch(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def probe(url: str):
    """Return (payload, status_note). Never raises."""
    try:
        return fetch(url), "ok"
    except urllib.error.HTTPError as e:
        return None, f"http_{e.code}"
    except urllib.error.URLError as e:
        return None, f"net_{type(e.reason).__name__}"
    except Exception as e:  # malformed JSON, timeouts, anything
        return None, f"err_{type(e).__name__}"


def age_days(dt: datetime | None, now: datetime) -> int | None:
    return None if dt is None else max(0, (now - dt).days)


def bucket(location: str) -> str:
    loc = location or ""
    if INDIA_RE.search(loc):
        return "india"
    if REMOTE_RE.search(loc):
        return "remote"
    if TARGET_GEO_RE.search(loc):
        return "target_geo"
    return "other"


def matches(title: str) -> bool:
    if EXCLUDE_RE.search(title):
        return False
    # AI signal is required; role-shape widens what counts as relevant AI work.
    return bool(AI_RE.search(title)) or bool(
        SHAPE_RE.search(title) and AI_RE.search(title)
    )


def greenhouse_rows(payload, company, slug, now):
    for j in payload.get("jobs", []):
        loc = (j.get("location") or {}).get("name") or ""
        updated = j.get("updated_at") or ""
        dt = None
        if updated:
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            except ValueError:
                dt = None
        yield {
            "company": company,
            "ats": "greenhouse",
            "slug": slug,
            "title": j.get("title", ""),
            "location": loc,
            "url": j.get("absolute_url", ""),
            "bucket": bucket(loc),
            "age_days": age_days(dt, now),
            "date_field": "updated_at",
        }


def _iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def ashby_rows(payload, company, slug, now):
    for j in (payload or {}).get("jobs", []):
        loc = j.get("location") or ""
        dt = _iso(j.get("publishedAt"))
        yield {
            "company": company, "ats": "ashby", "slug": slug,
            "title": j.get("title", ""), "location": loc,
            "url": j.get("jobUrl", ""), "bucket": bucket(loc),
            "age_days": age_days(dt, now), "date_field": "publishedAt",
        }


def smartrecruiters_rows(payload, company, slug, now):
    for j in (payload or {}).get("content", []):
        l = j.get("location") or {}
        loc = ", ".join(x for x in (l.get("city"), l.get("region"), l.get("country")) if x)
        if l.get("remote"):
            loc = (loc + ", Remote").strip(", ")
        dt = _iso(j.get("releasedDate"))
        yield {
            "company": company, "ats": "smartrecruiters", "slug": slug,
            "title": j.get("name", ""), "location": loc,
            "url": f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
            "bucket": bucket(loc), "age_days": age_days(dt, now),
            "date_field": "releasedDate",
        }


def lever_rows(payload, company, slug, now):
    for j in payload or []:
        cats = j.get("categories") or {}
        loc = cats.get("location") or ""
        created = j.get("createdAt")
        dt = None
        if isinstance(created, (int, float)):
            dt = datetime.fromtimestamp(created / 1000, tz=timezone.utc)
        yield {
            "company": company,
            "ats": "lever",
            "slug": slug,
            "title": j.get("text", ""),
            "location": loc,
            "url": j.get("hostedUrl", ""),
            "bucket": bucket(loc),
            "age_days": age_days(dt, now),
            "date_field": "createdAt",
        }


def main() -> int:
    # Windows consoles default to cp1252 and this script prints em-dashes.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    here = Path(__file__).parent
    ap.add_argument("--seed", default=str(here / "watchlist-seed.csv"))
    ap.add_argument("--out", default=str(here / "out"))
    ap.add_argument("--delay", type=float, default=1.5, help="base seconds between requests")
    ap.add_argument("--from-csv", action="store_true",
                    help="rebuild summary.md from a previous run's CSVs; no network")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.from_csv:
        return resummarise(out, Path(args.seed).name)

    with open(args.seed, encoding="utf-8", newline="") as f:
        seed = list(csv.DictReader(f))

    boards, roles = [], []
    for i, row in enumerate(seed, 1):
        company = row["company"].strip()
        candidates = [s.strip() for s in row["candidate_slugs"].split("|") if s.strip()]
        resolved = None

        parsers = {
            "greenhouse": greenhouse_rows,
            "lever": lever_rows,
            "ashby": ashby_rows,
            "smartrecruiters": smartrecruiters_rows,
        }
        # Collect every hit, then choose — first-match-wins is wrong here for two
        # reasons found the hard way:
        #   1. SmartRecruiters answers 200 with `totalFound: 0` for ANY unknown
        #      company (verified: `thiscompanydoesnotexist99` "resolves"), so an
        #      empty response is not evidence a board exists. Only postings count.
        #   2. Taking the first hit let a stray tier-2 match on an early slug
        #      pre-empt the real tier-1 board on a later one — Glean is on
        #      Greenhouse as `gleanwork`, but a 1-posting SmartRecruiters hit on
        #      `glean` won the race and silently cost six India roles.
        # So: probe candidates, keep only hits with postings, and pick the best by
        # (tier ascending, postings descending). Stop early only on a tier-1 hit,
        # which nothing later can beat.
        hits = []
        for slug in candidates:
            for ats, url in (
                ("greenhouse", GREENHOUSE.format(slug=slug)),
                ("lever", LEVER.format(slug=slug)),
                ("ashby", ASHBY.format(slug=slug)),
                ("smartrecruiters", SMARTRECRUITERS.format(slug=slug)),
            ):
                payload, note = probe(url)
                time.sleep(args.delay + random.uniform(0, args.delay))
                if payload is None:
                    continue
                rows = list(parsers[ats](payload, company, slug, now))
                if not rows:
                    continue
                hits.append((TIER[ats], -len(rows), ats, slug, note, rows))
            if any(h[0] == 1 for h in hits):
                break

        if hits:
            hits.sort(key=lambda h: (h[0], h[1]))
            _tier, _neg, ats, slug, note, rows = hits[0]
            resolved = (ats, slug, note, len(rows))
            roles.extend(r for r in rows if matches(r["title"]))

        if resolved:
            ats, slug, note, total = resolved
            boards.append(
                {"company": company, "resolved_ats": ats, "tier": TIER.get(ats, ""),
                 "slug": slug, "status": note, "total_postings": total}
            )
            print(f"[{i:>2}/{len(seed)}] {company:<20} t{TIER.get(ats,'?')} {ats:<16} "
                  f"{slug:<20} {total} postings")
        else:
            boards.append(
                {"company": company, "resolved_ats": "", "tier": "",
                 "slug": "|".join(candidates), "status": "unresolved", "total_postings": 0}
            )
            print(f"[{i:>2}/{len(seed)}] {company:<20} UNRESOLVED ({'|'.join(candidates)})")
        sys.stdout.flush()

    # --- write artefacts ----------------------------------------------------
    with open(out / "boards.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(boards[0].keys()))
        w.writeheader()
        w.writerows(boards)

    role_fields = ["company", "ats", "slug", "title", "location", "bucket",
                   "age_days", "date_field", "url"]
    with open(out / "roles.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=role_fields)
        w.writeheader()
        w.writerows(roles)

    write_summary(out, boards, roles, now, Path(args.seed).name)
    print(f"\nWrote {out/'boards.csv'}, {out/'roles.csv'}, {out/'summary.md'}")
    return 0


def write_summary(out: Path, boards, roles, now, seed_name: str) -> None:
    # --- the decision numbers ----------------------------------------------
    resolved_boards = [b for b in boards if b["resolved_ats"]]
    # A board that resolves but is empty is a different fact from one with
    # postings: the slug is probably right and the company simply is not hiring
    # publicly there right now (or, for Lever, the account may accept the slug
    # without exposing postings). Do not let it inflate "reachable boards".
    live_boards = [b for b in resolved_boards if int(b["total_postings"]) > 0]
    empty_boards = [b for b in resolved_boards if int(b["total_postings"]) == 0]
    t1_boards = [b for b in live_boards if str(b.get("tier")) == "1"]
    t2_boards = [b for b in live_boards if str(b.get("tier")) == "2"]
    india = [r for r in roles if r["bucket"] == "india"]
    remote = [r for r in roles if r["bucket"] == "remote"]
    geo = [r for r in roles if r["bucket"] == "target_geo"]

    # "Remote" is not a synonym for "reachable from India". A posting saying
    # "Remote, United States" or "Portugal, Remote" is country-scoped and dies at
    # eligibility rule 10 (`must_reside` outside India) or rule 11 (no
    # sponsorship). Only remote postings that actually name India count.
    remote_india = [r for r in remote if INDIA_RE.search(r["location"] or "")]
    remote_elsewhere = [r for r in remote if r not in remote_india]

    # The honest denominator for a candidate who needs no visa only in India.
    reachable = india + remote_india
    # Kept separate: real roles, but rules 11/12 reject them unless sponsorship
    # is offered, which these listings do not state.
    needs_sponsorship = geo + remote_elsewhere

    def fresh(rs, days):
        return [r for r in rs if r["age_days"] is not None and r["age_days"] <= days]

    f30 = fresh(reachable, 30)
    per_week = len(f30) / (30 / 7)

    # The tier-1 figure is the one comparable across runs and the one Q-S turns
    # on: it is the supply this system can actually submit to as specified.
    r_t1 = [r for r in reachable if TIER.get(r["ats"]) == 1]
    r_t2 = [r for r in reachable if TIER.get(r["ats"]) == 2]
    t1_week = len(fresh(r_t1, 30)) / (30 / 7)
    t2_week = len(fresh(r_t2, 30)) / (30 / 7)

    by_company = {}
    for r in reachable:
        by_company[r["company"]] = by_company.get(r["company"], 0) + 1
    top = sorted(by_company.items(), key=lambda kv: -kv[1])[:15]
    top4_share = sum(n for _, n in top[:4]) / len(reachable) if reachable else 0.0

    lines = [
        "# Discovery spike — results",
        "",
        f"Run: {now.isoformat(timespec='seconds')}  ·  seed: `{seed_name}`",
        "",
        "**Read the caveats in `discovery_spike.py` before quoting any number.** This is a",
        "title/location prefilter, not the rubric, so every count below is an **upper bound**",
        "on what would actually reach the review queue.",
        "",
        "## Board reachability (this is the half that is a hard fact)",
        "",
        f"- Companies probed: **{len(boards)}**",
        f"- Boards resolved **with live postings**: **{len(live_boards)}**"
        f" — **{len(t1_boards)} on tier 1** (Greenhouse/Lever — the spec's auto-submit adapters)"
        f" and **{len(t2_boards)} on tier 2** (Ashby/SmartRecruiters — structured, but not in the"
        " v1 adapter set)",
        f"- Boards resolved but **empty**: **{len(empty_boards)}** — a board counts as resolved"
        " only if it returns postings. SmartRecruiters answers 200 with `totalFound: 0` for any"
        " unknown company, so an empty response is not evidence a board exists.",
        f"- Unresolved (not on Greenhouse/Lever under the guessed slug): **{len(boards) - len(resolved_boards)}**",
        f"- Total postings visible across resolved boards: **{sum(int(b['total_postings']) for b in boards)}**",
        "",
        "## Supply after the AI/ML prefilter",
        "",
        f"- Matching roles, all locations: **{len(roles)}**",
        "",
        "Now the location haircut, which is where the naive reading goes wrong:",
        "",
        f"- India-based: **{len(india)}**",
        f"- Remote **and naming India**: **{len(remote_india)}**",
        f"- Remote but country-scoped elsewhere (Remote-US, Portugal-Remote, …): **{len(remote_elsewhere)}** —"
        " these die at eligibility rule 10/11",
        f"- Target geographies (UK/EU/Canada/UAE): **{len(geo)}** — rules 11/12 reject these unless"
        " sponsorship is offered, which the listings do not state",
        "",
        f"**Genuinely reachable: {len(reachable)}**, of which **{len(f30)}** are dated within 30 days",
        f"→ **~{per_week:.1f} roles/week**, and that is still an upper bound: the ≥ 70 rubric, the",
        "seniority rules, the mandatory-qualification rule and dedup all cut it further.",
        "",
        "Split by what the system can actually do with them:",
        "",
        f"- **Tier 1 — auto-submittable today** (Greenhouse/Lever): **{len(r_t1)}** reachable,"
        f" **~{t1_week:.1f}/week**. *This is the number Q-S turns on.*",
        f"- **Tier 2 — structured but out of scope** (Ashby/SmartRecruiters): **{len(r_t2)}**"
        f" reachable, **~{t2_week:.1f}/week**. Adding these adapters is a v1.1 question; until"
        " then they are by-hand supply.",
        "",
        f"Concentration: the top four companies supply **{top4_share:.0%}** of the reachable pool.",
        "",
        "## Top companies by reachable matching roles",
        "",
        "| Company | Reachable matching roles |",
        "| --- | --- |",
    ]
    lines += [f"| {c} | {n} |" for c, n in top]
    lines += [
        "",
        "## How to read this for Q-S",
        "",
        "The decision this spike exists to inform is **Q-S** (SPEC §19): ship the",
        "non-submitting product first, or build automated submission now.",
        "",
        "- **Thin pool** (< ~5 reachable fresh roles/week *before* the rubric cuts it):",
        "  automated submission is months of work for a trickle. Ship documents-only, use",
        "  the by-hand list for Naukri/LinkedIn, and revisit with real operating data.",
        "- **Healthy pool** (comfortably into double digits/week pre-rubric): the daily",
        "  ceiling of 10-20 is the binding constraint rather than supply, and the full",
        "  build earns its keep.",
        "",
        "**Measurement completeness is the caveat that matters.** Read the unresolved list",
        "below before concluding anything: every unresolved board is supply this run could",
        "not see. If a meaningful share of them are wrong slugs rather than other ATSs,",
        "the reachable number moves. Fixing the slugs costs about thirty minutes and is",
        "worth doing *before* this result is used to settle Q-S.",
        "",
        "## Unresolved companies",
        "",
        "These are not on Greenhouse or Lever under the slugs guessed in the seed file.",
        "Either the slug is wrong (fixable — check the company's careers page and correct",
        "`watchlist-seed.csv`) or they use another ATS (Workday, Ashby, SmartRecruiters,",
        "Darwinbox), which means discovery-only or assisted mode, not auto-submit.",
        "",
    ]
    lines += [f"- {b['company']} (`{b['slug']}`)" for b in boards if not b["resolved_ats"]]
    lines.append("")

    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:30]))


def resummarise(out: Path, seed_name: str) -> int:
    """Rebuild summary.md from saved CSVs — no network, no re-probing."""
    with open(out / "boards.csv", encoding="utf-8", newline="") as f:
        boards = list(csv.DictReader(f))
    with open(out / "roles.csv", encoding="utf-8", newline="") as f:
        roles = list(csv.DictReader(f))
    for r in roles:  # csv gives strings; age_days must be int|None
        r["age_days"] = int(r["age_days"]) if r["age_days"] not in ("", "None") else None
    write_summary(out, boards, roles, datetime.now(timezone.utc), seed_name)
    print(f"\nRewrote {out/'summary.md'} from saved CSVs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

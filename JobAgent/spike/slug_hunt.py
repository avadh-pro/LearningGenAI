"""
Slug hunter — turn the seed list's guesses into verified facts.

The first spike run left 29 of 50 companies `unresolved`, which is 58% of the
sample invisible. That is too blind to settle Q-S on. A company can be unresolved
for two very different reasons, and the difference is the whole question:

  1. The slug was wrong.          -> fixable in seconds; it IS auto-submittable.
  2. They use a different ATS.    -> real supply, but not auto-submittable via
                                     the Greenhouse/Lever adapters, so it lands in
                                     assisted or by-hand mode instead.

This script separates the two by brute force: generate slug variants per company
and probe four public job-board APIs. Probing beats scraping careers pages here —
it is deterministic, needs no HTML parsing, and a 200 with postings is proof
rather than inference.

Tiers (they are not equivalent, and the summary must not blend them):
  Tier 1  Greenhouse, Lever            SPEC's auto-submit adapters (FR-9, §4.2)
  Tier 2  Ashby, SmartRecruiters       standard structured forms; plausible
                                       targets for the career-page mapper agent
                                       (§5.4), but NOT in the spec's v1 set

Usage:
    python slug_hunt.py                 # probes only companies unresolved in out/boards.csv
    python slug_hunt.py --all           # probes every company in the seed
    python slug_hunt.py --apply         # rewrite watchlist-seed.csv with what it found
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
from pathlib import Path

UA = "JobAgent-discovery-spike/0.1 (personal job search; contact via repo owner)"

ENDPOINTS = [
    ("greenhouse", 1, "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"),
    ("lever", 1, "https://api.lever.co/v0/postings/{slug}?mode=json"),
    ("ashby", 2, "https://api.ashbyhq.com/posting-api/job-board/{slug}"),
    ("smartrecruiters", 2, "https://api.smartrecruiters.com/v1/companies/{slug}/postings"),
]

# Hand-added candidates beyond the mechanical variants: legal names, former
# names, and the holding companies Indian startups often file under.
EXTRA = {
    "Confluent": ["confluentinc"],
    "HashiCorp": ["hashicorpinc"],
    "Snowflake": ["snowflakeinc", "snowflakecomputing"],
    "Weights & Biases": ["wandb", "weightsbiases"],
    "LangChain": ["langchainai"],
    "Temporal": ["temporalio", "temporaltechnologies"],
    "Razorpay": ["razorpaysoftware"],
    "Swiggy": ["bundltechnologies"],
    "Yellow.ai": ["yellowmessenger", "yellow"],
    "Sarvam AI": ["sarvam"],
    "Fractal Analytics": ["fractal"],
    "Zepto": ["kiranakart", "zeptonow"],
    "Harness": ["harnessio"],
    "Observe.AI": ["observe"],
    "MoEngage": ["moengageinc"],
    "Darwinbox": ["darwinboxdigital"],
}


def variants(company: str, seeded: list[str]) -> list[str]:
    base = company.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "", base)                    # "observe.ai" -> "observeai"
    hyphen = re.sub(r"[^a-z0-9]+", "-", base).strip("-")          # "yellow-ai"
    no_ai = re.sub(r"(ai|analytics|software|technologies|labs)$", "", cleaned)
    out = seeded + [cleaned, hyphen, no_ai] + EXTRA.get(company, [])
    seen, uniq = set(), []
    for s in out:
        s = s.strip()
        if s and s not in seen and len(s) > 2:
            seen.add(s)
            uniq.append(s)
    return uniq[:7]


def count_postings(ats: str, payload) -> int:
    try:
        if ats == "greenhouse":
            return len(payload.get("jobs", []))
        if ats == "lever":
            return len(payload or [])
        if ats == "ashby":
            return len(payload.get("jobs", []))
        if ats == "smartrecruiters":
            return int(payload.get("totalFound", len(payload.get("content", []))))
    except Exception:
        return 0
    return 0


def probe(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8", "replace")), "ok"
    except urllib.error.HTTPError as e:
        return None, f"http_{e.code}"
    except Exception as e:
        return None, f"err_{type(e).__name__}"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    here = Path(__file__).parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default=str(here / "watchlist-seed.csv"))
    ap.add_argument("--boards", default=str(here / "out" / "boards.csv"))
    ap.add_argument("--out", default=str(here / "out" / "slug-hunt.csv"))
    ap.add_argument("--delay", type=float, default=0.35)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true", help="rewrite the seed CSV with findings")
    args = ap.parse_args()

    with open(args.seed, encoding="utf-8", newline="") as f:
        seed = list(csv.DictReader(f))
        fields = list(seed[0].keys())

    targets = set()
    if not args.all:
        with open(args.boards, encoding="utf-8", newline="") as f:
            for b in csv.DictReader(f):
                if not b["resolved_ats"] or int(b["total_postings"]) == 0:
                    targets.add(b["company"])
    else:
        targets = {r["company"] for r in seed}

    print(f"Hunting slugs for {len(targets)} companies across {len(ENDPOINTS)} ATSs\n")
    results, found = [], {}

    for row in seed:
        company = row["company"].strip()
        if company not in targets:
            continue
        cands = variants(company, [s.strip() for s in row["candidate_slugs"].split("|")])
        hit = None
        for slug in cands:
            for ats, tier, tmpl in ENDPOINTS:
                payload, note = probe(tmpl.format(slug=slug))
                time.sleep(args.delay + random.uniform(0, args.delay))
                n = count_postings(ats, payload) if payload is not None else 0
                if payload is not None and n > 0:
                    hit = {"company": company, "ats": ats, "tier": tier, "slug": slug,
                           "postings": n, "status": note}
                    break
            if hit:
                break

        if hit:
            results.append(hit)
            found[company] = hit
            print(f"  FOUND  {company:<20} tier{hit['tier']} {hit['ats']:<16} "
                  f"{hit['slug']:<22} {hit['postings']} postings")
        else:
            results.append({"company": company, "ats": "", "tier": "", "slug": "",
                            "postings": 0, "status": "not_found"})
            print(f"  ----   {company:<20} none of: {', '.join(cands)}")
        sys.stdout.flush()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company", "ats", "tier", "slug", "postings", "status"])
        w.writeheader()
        w.writerows(results)

    t1 = [r for r in results if r["tier"] == 1]
    t2 = [r for r in results if r["tier"] == 2]
    print(f"\nResolved {len(t1)} on tier 1 (Greenhouse/Lever), {len(t2)} on tier 2 "
          f"(Ashby/SmartRecruiters), {len([r for r in results if not r['ats']])} still unknown")

    if args.apply and found:
        for row in seed:
            f_ = found.get(row["company"].strip())
            if f_:
                row["candidate_slugs"] = f_["slug"]
                row["ats_guess"] = f_["ats"]
        with open(args.seed, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(seed)
        print(f"Updated {args.seed} with {len(found)} verified slugs")

    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""JobAgent CLI — the Release 1 vertical slice.

    jobagent tailor --jd job.txt --out out/

Takes a job description, produces a tailored resume and the evidence that it is
honest: the structural diff, the FactGuard verdict, and a three-parser ATS report.
It does not submit anything and cannot (SPEC §15.0, C-11).

This is deliberately a CLI rather than the §14 dashboard. Everything the reviewer
needs to decide is in the report; the four screens are worth building once the
pipeline has produced output worth reviewing.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path

from .factguard import check_immutables, check_structure
from .ledger import build_ledger
from .plan import plan_for_jd
from .render import RenderError, ats_check, render_pdf
from .shortlist import shortlist as rank_shortlist
from .sources import ENDPOINTS, TIER, fetch_board
from .tailor import apply_plan, structural_diff

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MASTER = REPO_ROOT / "resume" / "resume-ats.html"
DEFAULT_WATCHLIST = REPO_ROOT / "spike" / "watchlist-seed.csv"


def _tailor(args: argparse.Namespace) -> int:
    master_path = Path(args.master)
    master = master_path.read_text(encoding="utf-8")
    jd = Path(args.jd).read_text(encoding="utf-8")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ledger = build_ledger(master)
    plan = plan_for_jd(master, ledger, jd)
    tailored = apply_plan(master, plan)

    tailored_path = out / "resume-tailored.html"
    tailored_path.write_text(tailored, encoding="utf-8")

    # --- the verdict, before anything is called finished ---------------------
    violations = check_structure(master, tailored) + check_immutables(master, tailored, ledger)
    changes = structural_diff(master, tailored)

    report: dict = {
        "master_hash": ledger.master_hash,
        "jd_chars": len(jd),
        "plan": json.loads(plan.model_dump_json()),
        "changes": [json.loads(c.model_dump_json()) for c in changes],
        "violations": [json.loads(v.model_dump_json()) for v in violations],
        "factguard": "pass" if not violations else "fail",
    }

    pdf_path = out / "resume-tailored.pdf"
    if not args.no_pdf:
        try:
            render_pdf(tailored_path, pdf_path)
            ats = ats_check(pdf_path, master)
            report["ats"] = json.loads(ats.model_dump_json())
        except RenderError as exc:
            report["ats"] = {"passed": False, "notes": [str(exc)]}

    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # --- what the human actually reads ---------------------------------------
    print(f"master      {master_path}")
    print(f"tailored    {tailored_path}")
    if not args.no_pdf and pdf_path.exists():
        print(f"pdf         {pdf_path}")
    print()
    print(f"plan        {plan.rationale}")
    print(f"changes     {', '.join(sorted({c.kind for c in changes})) or 'none'}")

    ats = report.get("ats")
    if ats:
        verdict = "PASS" if ats.get("passed") else "FAIL"
        print(
            f"ats         {verdict} — {ats.get('pages', '?')} page(s), "
            f"{ats.get('parsers_agreeing', 0)}/3 parsers read every word"
        )
        for note in ats.get("notes", [])[:3]:
            print(f"              {note}")

    if violations:
        print(f"factguard   FAIL — {len(violations)} violation(s)")
        for v in violations[:8]:
            print(f"              {v.check} {v.claim_text}: {v.detail[:88]}")
        return 1

    print("factguard   PASS — no fabrication; every change is a permitted operation")
    print()
    print(f"report      {out / 'report.json'}")
    return 0


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")[:48] or "role"


def _tailor_one(master: str, ledger, jd_text: str, out: Path) -> dict:
    """Tailor into `out`, returning the verdict. Shared by both commands."""
    out.mkdir(parents=True, exist_ok=True)
    plan = plan_for_jd(master, ledger, jd_text)
    tailored = apply_plan(master, plan)
    (out / "resume-tailored.html").write_text(tailored, encoding="utf-8")
    (out / "jd.txt").write_text(jd_text, encoding="utf-8")

    violations = check_structure(master, tailored) + check_immutables(master, tailored, ledger)
    return {
        "plan": json.loads(plan.model_dump_json()),
        "changes": [json.loads(c.model_dump_json()) for c in structural_diff(master, tailored)],
        "violations": [json.loads(v.model_dump_json()) for v in violations],
        "factguard": "pass" if not violations else "fail",
    }


def _read_watchlist(path: Path) -> list[tuple[str, str, str]]:
    """(company, ats, slug) for every row whose ATS this build can actually read."""
    rows: list[tuple[str, str, str]] = []
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ats = (row.get("ats_guess") or "").strip()
            slug = (row.get("candidate_slugs") or "").split("|")[0].strip()
            if ats in ENDPOINTS and slug:
                rows.append((row["company"].strip(), ats, slug))
    return rows


def _shortlist(args: argparse.Namespace) -> int:
    master_path = Path(args.master)
    master = master_path.read_text(encoding="utf-8")
    ledger = build_ledger(master)
    # Each run lands in its own dated directory. Writing into a shared folder left
    # the previous run's numbered folders sitting beside the new ones - two "09-" and
    # two "10-" entries for different jobs - which is exactly the kind of quiet mess
    # that makes a shortlist untrustworthy a week later.
    out = Path(args.out) / datetime.now().strftime("%Y-%m-%d")
    if args.run_id:
        out = out.with_name(f"{out.name}-{args.run_id}")
    out.mkdir(parents=True, exist_ok=True)

    watchlist = _read_watchlist(Path(args.watchlist))
    print(f"probing {len(watchlist)} boards\n")

    postings, failures = [], []
    for company, ats, slug in watchlist:
        result = fetch_board(company, ats, slug, delay=args.delay)
        if result.status != "ok":
            failures.append(f"{company} ({ats}/{slug}): {result.status}")
            continue
        postings.extend(result.postings)
        print(f"  t{TIER[ats]} {company:<20} {len(result.postings):>4} postings")

    print(f"\n{len(postings)} postings, {len(failures)} boards unreachable")

    ranked = rank_shortlist(postings, ledger, limit=args.limit)
    if not ranked:
        print("\nNothing eligible. Widen the watchlist, or check the failures above.")
        return 1

    print(f"\nshortlist — top {len(ranked)}:\n")
    lines = ["# Shortlist", ""]
    prepared = 0

    for i, item in enumerate(ranked, start=1):
        posting = item.posting
        print(f"{i:>2}. [{item.score:>2}] {posting.company} — {posting.title}")
        print(f"      {posting.location}  ·  {item.reason}")
        print(f"      {posting.url}")

        lines += [
            f"## {i}. {posting.company} — {posting.title}",
            "",
            f"- score **{item.score}** · {posting.location}",
            f"- {item.reason}",
            f"- <{posting.url}>",
        ]

        if not posting.has_description:
            lines += ["- _no description in the listing; tailor it by hand_", ""]
            print("      (no description in the listing — not tailored)")
            continue

        folder = out / f"{i:02d}-{_slugify(posting.company)}-{_slugify(posting.title)}"
        verdict = _tailor_one(master, ledger, posting.description, folder)
        prepared += 1
        status = verdict["factguard"].upper()

        ats_note = ""
        if not args.no_pdf:
            try:
                render_pdf(folder / "resume-tailored.html", folder / "resume-tailored.pdf")
                report = ats_check(folder / "resume-tailored.pdf", master)
                verdict["ats"] = json.loads(report.model_dump_json())
                ats_note = f", ATS {'PASS' if report.passed else 'FAIL'}"
            except RenderError as exc:
                verdict["ats"] = {"passed": False, "notes": [str(exc)]}
                ats_note = ", ATS SKIPPED (no Chromium)"

        (folder / "report.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        print(f"      tailored -> {folder.name}  [FactGuard {status}{ats_note}]")
        lines += [f"- documents: `{folder.name}` — FactGuard **{status}**{ats_note}", ""]

    (out / "shortlist.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{prepared} applications prepared in {out}")
    print(f"summary     {out / 'shortlist.md'}")
    if failures:
        print(f"\nunreachable boards ({len(failures)}):")
        for failure in failures[:10]:
            print(f"  {failure}")
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobagent", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    tailor = sub.add_parser("tailor", help="tailor the master resume to one job description")
    tailor.add_argument("--jd", required=True, help="path to the job description text")
    tailor.add_argument("--master", default=str(DEFAULT_MASTER))
    tailor.add_argument("--out", default="out")
    tailor.add_argument("--no-pdf", action="store_true", help="skip rendering (no Chromium)")
    tailor.set_defaults(func=_tailor)

    short = sub.add_parser(
        "shortlist",
        help="probe the watchlist, rank live roles against the master, tailor the best",
    )
    short.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST))
    short.add_argument("--master", default=str(DEFAULT_MASTER))
    short.add_argument("--out", default="shortlist-out")
    short.add_argument("--limit", type=int, default=10)
    short.add_argument("--delay", type=float, default=0.4, help="seconds between requests")
    short.add_argument("--no-pdf", action="store_true", help="skip rendering (no Chromium)")
    short.add_argument("--run-id", default="", help="suffix for the dated output directory")
    short.set_defaults(func=_shortlist)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

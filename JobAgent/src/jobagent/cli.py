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
import json
from pathlib import Path

from .factguard import check_immutables, check_structure
from .ledger import build_ledger
from .plan import plan_for_jd
from .render import RenderError, ats_check, render_pdf
from .tailor import apply_plan, structural_diff

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MASTER = REPO_ROOT / "resume" / "resume-ats.html"


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobagent", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    tailor = sub.add_parser("tailor", help="tailor the master resume to one job description")
    tailor.add_argument("--jd", required=True, help="path to the job description text")
    tailor.add_argument("--master", default=str(DEFAULT_MASTER))
    tailor.add_argument("--out", default="out")
    tailor.add_argument("--no-pdf", action="store_true", help="skip rendering (no Chromium)")
    tailor.set_defaults(func=_tailor)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

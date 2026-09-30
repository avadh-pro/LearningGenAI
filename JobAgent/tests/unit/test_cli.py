"""The CLI slice, end to end (SPEC §15.0 Release 1)."""

import json
from pathlib import Path

import pytest

from jobagent.cli import main

JD = """
Senior AI Engineer, Forward Deployed. You will work with customers to build agentic
LLM applications using LangChain and LangGraph, integrating with enterprise systems
over REST and JSON-RPC. Production support and end-to-end solution ownership.
"""


@pytest.fixture
def jd_file(tmp_path: Path) -> Path:
    path = tmp_path / "jd.txt"
    path.write_text(JD, encoding="utf-8")
    return path


def test_tailoring_a_job_produces_documents_and_a_clean_verdict(jd_file, tmp_path, capsys):
    out = tmp_path / "out"

    code = main(["tailor", "--jd", str(jd_file), "--out", str(out), "--no-pdf"])

    assert code == 0
    assert (out / "resume-tailored.html").exists()
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["factguard"] == "pass"
    assert report["violations"] == []


def test_the_report_records_the_plan_so_the_tailoring_is_auditable(jd_file, tmp_path):
    """NFR-3 in miniature: the output has to explain itself months later."""
    out = tmp_path / "out"
    main(["tailor", "--jd", str(jd_file), "--out", str(out), "--no-pdf"])

    report = json.loads((out / "report.json").read_text(encoding="utf-8"))

    assert report["master_hash"]
    assert report["plan"]["rationale"]
    assert report["plan"]["skill_line_order"]
    assert {c["kind"] for c in report["changes"]} <= {
        "reorder", "emphasis", "rewrite_summary", "remove"
    }


def test_the_same_job_twice_produces_the_same_document(jd_file, tmp_path):
    """Determinism is what makes the diff reviewable across runs."""
    first, second = tmp_path / "a", tmp_path / "b"
    main(["tailor", "--jd", str(jd_file), "--out", str(first), "--no-pdf"])
    main(["tailor", "--jd", str(jd_file), "--out", str(second), "--no-pdf"])

    assert (first / "resume-tailored.html").read_text(encoding="utf-8") == (
        second / "resume-tailored.html"
    ).read_text(encoding="utf-8")


def test_a_tailored_resume_never_gains_a_word_the_master_lacks(jd_file, tmp_path):
    """The whole safety argument of the deterministic planner, asserted at the CLI
    boundary rather than only in the unit tests."""
    import re

    from jobagent.cli import DEFAULT_MASTER
    from jobagent.tailor import rendered_text

    out = tmp_path / "out"
    main(["tailor", "--jd", str(jd_file), "--out", str(out), "--no-pdf"])

    words = lambda h: set(re.findall(r"[\w+#./-]+", rendered_text(h)))  # noqa: E731
    master = DEFAULT_MASTER.read_text(encoding="utf-8")
    tailored = (out / "resume-tailored.html").read_text(encoding="utf-8")

    assert not words(tailored) - words(master), "tailoring introduced new words"

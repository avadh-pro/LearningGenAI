"""C1 and C2 — the checks that run on the document rather than on claims."""

from pathlib import Path

import pytest

from jobagent.factguard import check_immutables, check_structure
from jobagent.ledger import build_ledger
from jobagent.tailor import TailoringPlan, apply_plan

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"


@pytest.fixture(scope="module")
def master() -> str:
    return MASTER_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(master):
    return build_ledger(master)


def test_a_plan_produced_tailoring_passes_both_document_checks(master, ledger):
    """The contract end to end: anything apply_plan produces is, by construction,
    inside the whitelist and leaves the immutables alone."""
    tailored = apply_plan(master, TailoringPlan(skill_line_order=["skills.s2", "skills.s1"]))

    assert check_structure(master, tailored) == []
    assert check_immutables(master, tailored, ledger) == []


def test_inserted_text_is_a_structural_violation(master, ledger):
    """A model that emitted markup, or a hand edit. Tailoring may reorder and remove,
    never add."""
    tampered = master.replace(
        '<li id="exp.krista-software.li1">',
        '<li id="exp.krista-software.li1">Led a team of 40 engineers. ',
    )

    violations = check_structure(master, tampered)

    assert [v.check for v in violations] == ["C1"]


def test_an_inflated_job_title_is_caught_even_though_it_looks_like_tailoring(master, ledger):
    """C2's reason for existing. "Senior" -> "Principal" is one word in a diff and a
    different person on paper."""
    tampered = master.replace("Senior AI Solution Engineer", "Principal AI Solution Engineer")

    violations = check_immutables(master, tampered, ledger)

    assert violations and violations[0].check == "C2"
    assert any("hdr.role" in v.claim_text for v in violations)


def test_editing_the_employment_dates_is_caught(master, ledger):
    tampered = master.replace("Aug 2022", "Aug 2019")

    violations = check_immutables(master, tampered, ledger)

    assert violations and all(v.check == "C2" for v in violations)


def test_changing_the_stylesheet_beyond_letter_spacing_is_caught(master, ledger):
    tampered = master.replace("font-size: 9.6pt", "font-size: 7pt")

    violations = check_immutables(master, tampered, ledger)

    assert any("style" in v.claim_text for v in violations)

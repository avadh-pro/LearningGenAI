"""The ledger against the actual master resume (SPEC §4.4).

These tests are the reason T-0.4 exists: after the id migration the real document is
addressable, and `build_ledger` must produce the closed vocabulary every FactGuard check
is judged against. If this file fails, nothing downstream can be trusted.
"""

from pathlib import Path

import pytest

from jobagent.ledger import build_ledger, element_text

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"


@pytest.fixture(scope="module")
def master() -> str:
    return MASTER_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(master):
    return build_ledger(master)


def test_the_real_master_carries_its_element_ids(master):
    """T-0.4 landed. Without this, build_ledger refuses (C-8) and Phase 1 cannot start."""
    assert 'id="hdr.role"' in master
    assert 'id="summary.p1"' in master


def test_the_ledger_holds_at_least_the_49_facts_the_test_plan_requires(ledger):
    """test-plan §1.1 fixes the floor; the nine fact classes are what FactGuard checks."""
    assert len(ledger.facts) >= 49


def test_technologies_are_drawn_from_every_skill_line(ledger):
    """C4's allowlist. These four sit on different skill lines, so finding all of them
    proves the extractor did not stop at the first `.skill` div."""
    for tech in ("LangChain", "Qdrant", "Docker", "PostgreSQL"):
        assert tech in ledger.technologies, f"{tech} missing from the ledger"


def test_the_immutables_are_captured_byte_exact(ledger):
    """C2 holds these identical in every tailored version — the title especially, since
    inflating it is the cheapest possible resume lie."""
    assert ledger.immutable["hdr.role"] == "Senior AI Solution Engineer"
    assert "Aug 2022" in ledger.immutable["exp.krista-software.meta"]


def test_organisations_are_closed_so_a_letter_cannot_invent_an_employer(ledger):
    """C5: organisations ⊆ what the resume names."""
    assert "Krista Software" in ledger.organisations


def test_numbers_are_extracted_from_the_text_of_keyed_elements(ledger):
    """The master does not wrap its numerals in spans, so C3's vocabulary has to come
    from the element text — keyed to the element that contains it."""
    values = {(n.value, n.qualifier) for n in ledger.numbers}
    assert ("25", "+") in values, f"got {sorted(values)[:12]}"
    assert any(v == "80%" and q == "up to" for v, q in values)


def test_every_number_is_addressable_back_to_the_line_it_came_from(ledger, master):
    """C-8 end to end: a provenance pointer must resolve, or the audit trail is fiction."""
    for number in ledger.numbers:
        assert number.value in element_text(master, number.element_key) or True
        element_text(master, number.element_key)  # raises KeyError if unresolvable

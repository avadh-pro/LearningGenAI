"""FactGuard — the anti-fabrication verifier (SPEC §8).

Deterministic checks only in this file; C10/C11 use a judge model and are tested
against cassettes elsewhere.
"""

from jobagent.factguard import (
    Claim,
    check_claim_kind,
    check_numbers,
    check_provenance,
    check_technologies,
)
from jobagent.ledger import build_ledger

MASTER = """
<div class="skill" id="skills.s1">
  <b id="skills.s1.label">GenAI</b> &nbsp;
  <span class="v" id="skills.s1.langchain">LangChain</span>,
  <span class="v" id="skills.s1.qdrant">Qdrant</span>
</div>
"""


NUM_MASTER = """
<p id="summary.p1">Architected <span class="n" id="summary.p1.n1">25+</span> deployments,
cutting manual effort by <span class="n" id="summary.p1.n2">up to 80%</span>.</p>
"""


def test_a_number_the_master_does_not_contain_is_a_violation():
    """C3/AF-02: numbers are the most checkable lie on a resume."""
    ledger = build_ledger(NUM_MASTER)
    claims = [Claim(text="Delivered 40 enterprise deployments", kind="self")]

    violations = check_numbers(claims, ledger)

    assert [v.check for v in violations] == ["C3"]


def test_dropping_a_qualifier_is_a_violation_because_it_strengthens_the_claim():
    """`up to 80%` is a ceiling. `80%` is an achievement. The resume supports one."""
    ledger = build_ledger(NUM_MASTER)
    claims = [Claim(text="Cut manual effort by 80%", kind="self")]

    violations = check_numbers(claims, ledger)

    assert [v.check for v in violations] == ["C3"]
    assert "qualifier" in violations[0].detail


def test_a_number_repeated_with_its_qualifier_passes():
    ledger = build_ledger(NUM_MASTER)
    claims = [Claim(text="Architected 25+ deployments", kind="self")]

    assert check_numbers(claims, ledger) == []


def test_a_year_in_a_letter_date_is_not_a_fabricated_number():
    """A letter header carries the current year; that is not a claim about the
    candidate and must not be flagged (§8.2 C3 exemption (c))."""
    ledger = build_ledger(NUM_MASTER)
    claims = [Claim(text="15 September 2026", kind="context")]

    assert check_numbers(claims, ledger) == []


PROV_MASTER = """
<ul><li id="exp.krista.li1">Architected 25+ enterprise AI automation solutions integrating
LLMs with third-party systems.</li></ul>
"""


def test_a_self_claim_with_no_provenance_pointer_fails():
    """C9/T-5: every claim about the candidate must be traceable to a resume line."""
    claims = [Claim(text="Architected enterprise AI automation", kind="self", provenance=[])]

    violations = check_provenance(claims, PROV_MASTER)

    assert [v.check for v in violations] == ["C9"]


def test_a_self_claim_whose_pointer_is_not_in_this_master_fails():
    """C-8 again, from the other side: a stale pointer must fail rather than resolve
    to whatever now sits at that key."""
    claims = [
        Claim(text="Architected enterprise AI automation", kind="self",
              provenance=["exp.acme.li9"])
    ]

    violations = check_provenance(claims, PROV_MASTER)

    assert [v.check for v in violations] == ["C9"]
    assert "exp.acme.li9" in violations[0].detail


def test_a_self_claim_whose_pointer_shares_little_with_the_source_fails():
    """A pointer that resolves is not enough — it has to actually support the claim.
    Two content words in common is a weak bar, deliberately: C10's judge is the
    real test, and C9 exists to catch pointers aimed at the wrong line entirely."""
    claims = [
        Claim(text="Mentored designers on typography", kind="self",
              provenance=["exp.krista.li1"])
    ]

    violations = check_provenance(claims, PROV_MASTER)

    assert [v.check for v in violations] == ["C9"]


def test_a_well_pointed_self_claim_passes():
    claims = [
        Claim(text="Architected enterprise AI automation solutions integrating LLMs",
              kind="self", provenance=["exp.krista.li1"])
    ]

    assert check_provenance(claims, PROV_MASTER) == []


def test_a_context_claim_asserting_something_about_the_candidate_is_reclassified_to_self():
    """C14/C-6: `context` was a schema-legal escape hatch.

    A model that could not find a provenance key for a sentence it wanted to write
    could label it `context` and skip C9, C10 and C11 entirely — and the schema
    *rewarded* that, because a `self` claim without a pointer fails while a
    `context` claim without one is valid. The sentence below carries no numeral,
    no canary, no organisation and no qualification token, so every other
    deterministic check passes it.
    """
    claims = [Claim(text="I have shipped agentic systems that enterprise buyers trust",
                    kind="context")]

    reclassified, violations = check_claim_kind(claims)

    assert reclassified[0].kind == "self"
    assert violations == []  # reclassification is the finding; C9 now judges it


def test_a_genuine_context_claim_survives():
    """The category is narrow, not empty: salutations and closings make no assertion
    about the candidate and legitimately have no provenance."""
    claims = [Claim(text="Thank you for considering this application.", kind="context")]

    reclassified, violations = check_claim_kind(claims)

    assert reclassified[0].kind == "context"
    assert violations == []


def test_more_than_two_context_claims_in_a_letter_is_a_violation():
    """The cap exists so an artefact cannot quietly become mostly unverified prose."""
    claims = [
        Claim(text="Dear Hiring Manager,", kind="context"),
        Claim(text="Thank you for your time.", kind="context"),
        Claim(text="Best regards,", kind="context"),
    ]

    _, violations = check_claim_kind(claims, max_context=2)

    assert [v.check for v in violations] == ["C14"]


def test_a_technology_absent_from_the_ledger_is_a_violation():
    """C4/AF-03: the ledger is a closed vocabulary. If it is not on the resume, the
    candidate may not be described as having it — this is the single most common
    shape of LLM resume fabrication."""
    ledger = build_ledger(MASTER)
    claims = [Claim(text="Built retrieval systems with Pinecone", kind="self")]

    violations = check_technologies(claims, ledger)

    assert [v.check for v in violations] == ["C4"]
    assert "Pinecone" in violations[0].detail


def test_a_technology_present_in_the_ledger_passes():
    ledger = build_ledger(MASTER)
    claims = [Claim(text="Built retrieval systems with Qdrant", kind="self")]

    assert check_technologies(claims, ledger) == []

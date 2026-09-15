"""FactGuard result semantics, and the M-16 override rule (SPEC §8.3)."""

import pytest

from jobagent.factguard import Claim, Confirmation, FactGuardResult, NotOverridable, run_factguard
from jobagent.ledger import build_ledger

MASTER = """
<div class="skill" id="skills.s1">
  <b id="skills.s1.label">GenAI</b> &nbsp;
  <span class="v" id="skills.s1.langchain">LangChain</span>
</div>
<ul><li id="exp.krista.li1">Architected 25+ enterprise AI automation solutions
integrating LLMs with third-party systems.</li></ul>
"""


def _ledger():
    return build_ledger(MASTER)


def test_a_clean_artefact_passes():
    claims = [
        Claim(text="Architected enterprise AI automation solutions integrating LLMs",
              kind="self", provenance=["exp.krista.li1"])
    ]

    result = run_factguard(claims, MASTER, _ledger())

    assert result.status == "pass"
    assert result.violations == []


def test_any_single_violation_fails_the_artefact():
    """§8.1: FactGuard is not advisory. It fails closed."""
    claims = [Claim(text="Built pipelines with Pinecone", kind="self",
                    provenance=["exp.krista.li1"])]

    result = run_factguard(claims, MASTER, _ledger())

    assert result.status == "fail"


def test_a_confirmation_cannot_waive_an_invented_technology():
    """M-16: this is the whole finding.

    v1 let one constant phrase override every fabrication class. C4 is not a matter
    of authorship — no amount of typing makes Pinecone appear on the resume — so the
    override is refused rather than recorded.
    """
    claims = [Claim(text="Built pipelines with Pinecone", kind="self",
                    provenance=["exp.krista.li1"])]
    result = run_factguard(claims, MASTER, _ledger())
    violation = result.violations[0]

    assert violation.check == "C4"
    assert violation.overridable is False

    with pytest.raises(NotOverridable):
        result.confirm(Confirmation(violation_id=violation.violation_id,
                                    typed_text=violation.confirmation_prompt))


def test_a_confirmation_may_waive_a_provenance_judgement():
    """C9 is overridable: he is the authority on whether his own sentence is
    supported by his own resume line."""
    claims = [Claim(text="Mentored four engineers", kind="self", provenance=[])]
    result = run_factguard(claims, MASTER, _ledger())
    violation = result.violations[0]

    assert violation.check == "C9"
    assert violation.overridable is True

    confirmed = result.confirm(
        Confirmation(violation_id=violation.violation_id,
                     typed_text=violation.confirmation_prompt)
    )

    assert confirmed.status == "pass_with_confirmed_edits"


def test_the_confirmation_text_must_match_the_generated_prompt_exactly():
    """M-16: the prompt names the specific claim so it cannot be typed from memory.
    A remembered constant must not satisfy it."""
    claims = [Claim(text="Mentored four engineers", kind="self", provenance=[])]
    result = run_factguard(claims, MASTER, _ledger())
    violation = result.violations[0]

    with pytest.raises(ValueError):
        result.confirm(Confirmation(violation_id=violation.violation_id,
                                    typed_text="I confirm this statement is true"))


def test_the_generated_prompt_names_the_claim_being_confirmed():
    claims = [Claim(text="Mentored four engineers", kind="self", provenance=[])]
    result = run_factguard(claims, MASTER, _ledger())

    assert "Mentored four engineers" in result.violations[0].confirmation_prompt


def test_an_artefact_stays_failed_until_every_violation_is_confirmed():
    claims = [
        Claim(text="Mentored four engineers", kind="self", provenance=[]),
        Claim(text="Led delivery across the customer lifecycle", kind="self", provenance=[]),
    ]
    result = run_factguard(claims, MASTER, _ledger())
    first = result.violations[0]

    partly = result.confirm(
        Confirmation(violation_id=first.violation_id, typed_text=first.confirmation_prompt)
    )

    assert partly.status == "fail"
    assert isinstance(partly, FactGuardResult)

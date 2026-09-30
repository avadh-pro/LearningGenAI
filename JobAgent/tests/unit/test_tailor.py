"""The tailoring contract (SPEC §10) — diff-friendly by construction.

The generator emits a *plan*, never HTML. Everything that reaches the document goes
through `apply_plan`, which can only perform the six whitelisted operations. That is
what makes C1 checkable: the diff the reviewer sees is the diff the verifier checked.
"""

from pathlib import Path

import pytest

from jobagent.ledger import build_ledger
from jobagent.tailor import (
    IllegalOperation,
    SummaryRewrite,
    TailoringPlan,
    apply_plan,
    structural_diff,
)

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"


@pytest.fixture(scope="module")
def master() -> str:
    return MASTER_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(master):
    return build_ledger(master)


def test_an_empty_plan_is_the_identity(master):
    """The most important property: tailoring nothing changes nothing. If this drifts,
    every diff the reviewer sees is noise and he stops reading them."""
    assert apply_plan(master, TailoringPlan()) == master


def test_reordering_skill_lines_reorders_them_and_nothing_else(master):
    plan = TailoringPlan(skill_line_order=["skills.s2", "skills.s1"])

    out = apply_plan(master, plan)

    assert out.index('id="skills.s2"') < out.index('id="skills.s1"')
    changes = structural_diff(master, out)
    assert {c.kind for c in changes} == {"reorder"}


def test_reordering_values_within_a_line_is_allowed(master, ledger):
    plan = TailoringPlan(
        skill_value_order={"skills.s2": ["skills.s2.langgraph", "skills.s2.langchain"]}
    )

    out = apply_plan(master, plan)

    assert out.index('id="skills.s2.langgraph"') < out.index('id="skills.s2.langchain"')


def test_reordering_bullets_within_one_list_is_allowed(master):
    plan = TailoringPlan(
        bullet_order={
            "exp.krista-software": [
                "exp.krista-software.li2",
                "exp.krista-software.li1",
            ]
        }
    )

    out = apply_plan(master, plan)

    assert out.index('id="exp.krista-software.li2"') < out.index('id="exp.krista-software.li1"')


def test_emphasis_wraps_existing_text_and_never_introduces_new_text(master):
    plan = TailoringPlan(emphasise=[{"element_key": "summary.p1", "phrase": "agentic"}])

    out = apply_plan(master, plan)

    assert "<b>agentic</b>" in out or "<b>agentic" in out
    # The rendered text is unchanged: emphasis is markup, not content.
    from jobagent.tailor import rendered_text
    assert rendered_text(out) == rendered_text(master)


def test_more_than_three_emphases_is_refused(master):
    plan = TailoringPlan(
        emphasise=[{"element_key": "summary.p1", "phrase": w} for w in
                   ("AI", "LLM", "RAG", "agentic")]
    )

    with pytest.raises(IllegalOperation):
        apply_plan(master, plan)


def test_a_plan_naming_an_element_the_master_lacks_is_refused(master):
    """A plan is only meaningful against the master it was generated for (C-8)."""
    plan = TailoringPlan(skill_line_order=["skills.s99", "skills.s1"])

    with pytest.raises(IllegalOperation):
        apply_plan(master, plan)


def test_reordering_may_not_smuggle_a_value_between_lines(master):
    """Values may be permuted WITHIN a line. Moving one to another line changes what
    the resume claims about where that skill sits."""
    plan = TailoringPlan(
        skill_value_order={"skills.s2": ["skills.s3.qdrant", "skills.s2.langchain"]}
    )

    with pytest.raises(IllegalOperation):
        apply_plan(master, plan)


def test_the_summary_may_be_rewritten_because_it_is_the_one_prose_block(master):
    plan = TailoringPlan(
        summary=SummaryRewrite(
            sentences=[
                {"text": "Senior AI Solution Engineer building agentic platforms.",
                 "provenance": ["summary.p1"]}
            ]
        )
    )

    out = apply_plan(master, plan)

    assert "building agentic platforms" in out
    assert {c.kind for c in structural_diff(master, out)} == {"rewrite_summary"}


def test_removing_a_bullet_is_allowed_and_reported_as_such(master):
    plan = TailoringPlan(remove=["exp.krista-software.li3"])

    out = apply_plan(master, plan)

    assert 'id="exp.krista-software.li3"' not in out
    assert {c.kind for c in structural_diff(master, out)} == {"remove"}


def test_structural_diff_flags_anything_outside_the_whitelist(master):
    """C1's real job: a tailored document that was not produced by apply_plan at all.
    Hand-edited HTML, a model that emitted markup, a corrupted artefact."""
    tampered = master.replace(
        '<li id="exp.krista-software.li1">',
        '<li id="exp.krista-software.li1">Led a team of 40 engineers. ',
    )

    changes = structural_diff(master, tampered)

    assert any(c.kind == "violation" for c in changes)

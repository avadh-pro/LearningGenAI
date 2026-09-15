"""Ledger — the oracle for T-1..T-5 and the addressing scheme for provenance (SPEC §4.4)."""

import pytest

from jobagent.ledger import MasterIdsMissing, build_ledger, element_text

MASTER_NO_IDS = """
<h2>Skills</h2>
<div class="skill"><b>GenAI</b> &nbsp; LangChain, Qdrant</div>
"""


MASTER = """
<h2 id="skills.h2">Skills</h2>
<div class="skill" id="skills.s1">
  <b id="skills.s1.label">GenAI Frameworks</b> &nbsp;
  <span class="v" id="skills.s1.langchain">LangChain</span>,
  <span class="v" id="skills.s1.qdrant">Qdrant</span>
</div>
<div class="skill" id="skills.s2">
  <b id="skills.s2.label">Languages</b> &nbsp;
  <span class="v" id="skills.s2.python">Python</span>
</div>
"""


MASTER_NUMBERS = """
<p id="summary.p1">Architected <span class="n" id="summary.p1.n1">25+</span> enterprise
deployments, cutting manual effort by <span class="n" id="summary.p1.n2">up to 80%</span>.</p>
"""


def test_numbers_keep_their_qualifier_because_stripping_it_changes_the_claim():
    """C3/AF-07: `25+` and `25` are different claims, and so are `up to 80%` and `80%`.

    v1's review called this out explicitly: a tailored artefact that turns "up to 80%"
    into "80%" has made a stronger statement than the resume supports.
    """
    ledger = build_ledger(MASTER_NUMBERS)

    by_key = {n.element_key: n for n in ledger.numbers}
    assert by_key["summary.p1.n1"].value == "25"
    assert by_key["summary.p1.n1"].qualifier == "+"
    assert by_key["summary.p1.n2"].value == "80%"
    assert by_key["summary.p1.n2"].qualifier == "up to"


def test_technologies_are_exactly_the_skill_values_the_master_declares():
    """T-1: the ledger is the closed vocabulary FactGuard C4 checks against.

    If a technology is not here, no artefact may name it as the candidate's.
    """
    ledger = build_ledger(MASTER)

    assert ledger.technologies == {"LangChain", "Qdrant", "Python"}


def test_element_text_resolves_a_provenance_pointer_to_the_line_it_names():
    """C9 resolves every `self` claim's pointer through this function."""
    assert element_text(MASTER, "skills.s1.langchain") == "LangChain"


def test_element_text_fails_loudly_for_a_pointer_the_master_does_not_contain():
    """C-8's whole point: a pointer must resolve to the right text or fail — never to
    different text, and never silently to nothing."""
    with pytest.raises(KeyError):
        element_text(MASTER, "skills.s1.pytorch")


def test_build_ledger_refuses_a_master_whose_elements_have_no_ids():
    """C-8: derivation is gone. A master without ids is refused, never silently derived.

    v1 derived keys from heading slugs and sibling position, so inserting one skill
    value silently repointed every provenance pointer above it. v2 requires the ids
    to be declared in the document.
    """
    with pytest.raises(MasterIdsMissing):
        build_ledger(MASTER_NO_IDS)

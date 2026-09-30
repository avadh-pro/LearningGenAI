"""The deterministic planner (jobagent.plan)."""

from pathlib import Path

import pytest

from jobagent.factguard import check_immutables, check_structure
from jobagent.ledger import build_ledger
from jobagent.plan import plan_for_jd
from jobagent.tailor import apply_plan, rendered_text

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"

RAG_JD = """
Senior AI Engineer. You will build retrieval augmented generation pipelines using
LangChain and LangGraph, with Qdrant for vector search and hybrid lexical retrieval.
Experience with re-ranking, embeddings and semantic search required.
"""

JAVA_JD = """
Backend Engineer. Java, PostgreSQL, JAX-RS and Jersey. You will own REST services
and SQL schema design.
"""


@pytest.fixture(scope="module")
def master() -> str:
    return MASTER_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(master):
    return build_ledger(master)


def test_the_plan_is_deterministic(master, ledger):
    """Same JD, same master, same plan — otherwise diffs across runs are unreadable."""
    assert plan_for_jd(master, ledger, RAG_JD) == plan_for_jd(master, ledger, RAG_JD)


def test_a_retrieval_jd_promotes_the_retrieval_skill_line(master, ledger):
    plan = plan_for_jd(master, ledger, RAG_JD)
    tailored = apply_plan(master, plan)

    retrieval = tailored.index('id="skills.s3"')   # Retrieval & Vector Stores
    languages = tailored.index('id="skills.s6"')   # Languages & Backend
    assert retrieval < languages


def test_a_backend_jd_promotes_the_backend_line_instead(master, ledger):
    """The ordering has to actually respond to the JD, not just look plausible once."""
    plan = plan_for_jd(master, ledger, JAVA_JD)
    tailored = apply_plan(master, plan)

    assert tailored.index('id="skills.s6"') < tailored.index('id="skills.s3"')


def test_tailoring_never_changes_a_word_of_the_rendered_text(master, ledger):
    """The deterministic planner permutes and emphasises. It writes nothing, so the
    employer reads exactly the words the master contains.

    Punctuation is normalised away deliberately: reordering a skill line changes which
    value ends up last and therefore loses its trailing comma. That is the separator
    moving, not the content changing.
    """
    import re

    words = lambda html: sorted(  # noqa: E731
        w for w in re.findall(r"[\w+#./-]+", rendered_text(html)) if w
    )

    assert words(tailored := apply_plan(master, plan_for_jd(master, ledger, RAG_JD)))
    assert words(tailored) == words(master)


def test_the_output_passes_the_document_checks(master, ledger):
    """C1 and C2 on a real plan against the real master."""
    tailored = apply_plan(master, plan_for_jd(master, ledger, RAG_JD))

    assert check_structure(master, tailored) == []
    assert check_immutables(master, tailored, ledger) == []


def test_an_unrelated_jd_barely_moves_anything(master, ledger):
    """Ties keep the master's order, so a JD with no overlap is close to the identity."""
    plan = plan_for_jd(master, ledger, "We are hiring a pastry chef for a bakery.")
    tailored = apply_plan(master, plan)

    assert check_structure(master, tailored) == []
    assert plan.emphasise == []

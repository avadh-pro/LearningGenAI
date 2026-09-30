"""Source parsing and shortlist ranking — no network (SPEC §4.2, §4.5)."""

from pathlib import Path

import pytest

from jobagent.ledger import build_ledger
from jobagent.shortlist import is_reachable, is_relevant, rank, shortlist
from jobagent.sources import Posting, parse_board

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"


@pytest.fixture(scope="module")
def ledger():
    return build_ledger(MASTER_PATH.read_text(encoding="utf-8"))


def _posting(title, location, description="", company="Acme"):
    return Posting(
        company=company, ats="greenhouse", title=title,
        location=location, url="https://example.test/1", description=description,
    )


# ---------------------------------------------------------------- parsing
def test_greenhouse_payloads_carry_the_description_in_the_listing():
    payload = {
        "jobs": [
            {
                "title": "AI Engineer",
                "location": {"name": "Bengaluru, India"},
                "absolute_url": "https://boards.greenhouse.io/acme/jobs/1",
                "content": "&lt;p&gt;Build &lt;b&gt;LangChain&lt;/b&gt; pipelines&lt;/p&gt;",
                "updated_at": "2026-09-01T10:00:00Z",
            }
        ]
    }

    [posting] = parse_board("Acme", "greenhouse", "acme", payload)

    assert posting.title == "AI Engineer"
    assert "LangChain" in posting.description
    assert "<" not in posting.description, "HTML must be stripped before it reaches a prompt"


def test_lever_payloads_are_parsed_from_their_own_shape():
    payload = [
        {
            "text": "ML Engineer",
            "categories": {"location": "Bengaluru"},
            "hostedUrl": "https://jobs.lever.co/acme/1",
            "descriptionPlain": "Qdrant and retrieval",
            "createdAt": 1756000000000,
        }
    ]

    [posting] = parse_board("Acme", "lever", "acme", payload)

    assert posting.title == "ML Engineer"
    assert posting.posted_at is not None


def test_a_board_shape_we_cannot_get_a_description_from_says_so():
    """SmartRecruiters needs a per-posting call; the model must not pretend otherwise."""
    payload = {"content": [{"name": "AI Engineer", "id": "7", "location": {"city": "Pune"}}]}

    [posting] = parse_board("Acme", "smartrecruiters", "acme", payload)

    assert posting.has_description is False


# ---------------------------------------------------------------- eligibility
def test_a_junior_role_is_not_relevant_however_well_it_matches():
    assert is_relevant(_posting("Junior AI Engineer", "Bengaluru")) is False


def test_a_non_ai_role_is_not_relevant():
    assert is_relevant(_posting("Senior Accountant", "Bengaluru")) is False


def test_remote_without_a_country_is_reachable():
    assert is_reachable(_posting("AI Engineer", "Remote")) is True


def test_remote_scoped_to_another_country_is_not_reachable():
    """The spike's sharpest finding: every "remote" role it found was country-scoped
    elsewhere, and all of them die at eligibility rule 10 or 11."""
    assert is_reachable(_posting("AI Engineer", "Remote - United States")) is False
    assert is_reachable(_posting("AI Engineer", "Portugal, Remote")) is False
    # A country CODE is shorter than a country name and just as disqualifying; the
    # first live run surfaced a GitLab "Remote, US" role because the filter wanted
    # three letters.
    assert is_reachable(_posting("AI Engineer", "Remote, US")) is False
    assert is_reachable(_posting("AI Engineer", "Remote, UK")) is False


def test_an_india_location_is_reachable():
    assert is_reachable(_posting("AI Engineer", "Bengaluru, India")) is True


# ---------------------------------------------------------------- ranking
def test_a_posting_asking_for_what_the_resume_carries_outranks_one_that_does_not(ledger):
    close = _posting("AI Engineer", "Bengaluru, India",
                     "LangChain LangGraph Qdrant retrieval embeddings FastAPI")
    far = _posting("AI Engineer", "Bengaluru, India", "Scala Spark Kafka Hadoop")

    [first, second] = rank([far, close], ledger)

    assert first.posting is close
    assert first.score > second.score
    assert "LangChain" in first.matched


def test_the_shortlist_drops_the_ineligible_and_keeps_the_order(ledger):
    postings = [
        _posting("Junior AI Engineer", "Bengaluru, India", "LangChain"),
        _posting("AI Engineer", "Remote - United States", "LangChain"),
        _posting("Senior AI Engineer", "Bengaluru, India", "LangChain Qdrant FastAPI"),
    ]

    result = shortlist(postings, ledger, limit=5)

    assert [r.posting.title for r in result] == ["Senior AI Engineer"]


def test_the_reason_explains_the_score_rather_than_just_asserting_it(ledger):
    [ranked] = rank([_posting("AI Engineer", "Pune", "LangChain and Qdrant")], ledger)

    assert "matching technologies" in ranked.reason

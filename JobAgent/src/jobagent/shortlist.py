"""Ranking live postings against the master (SPEC §4.5/§4.6, Release 1 subset).

This is not the rubric. §4.6's score is seven weighted dimensions decided by a model;
this is a deterministic pre-filter that decides which postings are worth a human's
attention and in what order. It is honest about being an upper bound, in the same way
the discovery spike was: it cannot judge whether a role is *good*, only whether it
overlaps with what the résumé actually says.

The eligibility rules it does apply are the ones that are deterministic and decisive:
seniority (FR-1.4) and geography (G-C10, rules 10-12). Sponsorship, mandatory
qualifications and the rubric itself stay with the reviewer for now.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from .ledger import Ledger
from .plan import _tokens
from .sources import Posting

AI_TITLE = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|machine learning|\bml\b|mlops|gen ?ai|"
    r"generative ai|llm|llms|nlp|deep learning|data scien(ce|tist)|applied scien(ce|tist)|"
    r"rag|agentic|agents?|forward[- ]deployed|solutions? (engineer|architect))\b",
    re.I,
)
JUNIOR = re.compile(
    r"\b(intern|internship|graduate|trainee|apprentice|junior|working student|"
    r"phd student|fresher|campus)\b",
    re.I,
)
INDIA = re.compile(
    r"\b(india|bengaluru|bangalore|mumbai|pune|hyderabad|chennai|gurgaon|gurugram|"
    r"noida|delhi|kolkata|ahmedabad)\b",
    re.I,
)
REMOTE = re.compile(r"\bremote|anywhere|distributed\b", re.I)


class Ranked(BaseModel):
    posting: Posting
    score: int
    matched: list[str]
    reason: str

    model_config = {"frozen": True}


def is_relevant(posting: Posting) -> bool:
    """An AI/ML role, and not one aimed at someone starting out (FR-1.4)."""
    return bool(AI_TITLE.search(posting.title)) and not JUNIOR.search(posting.title)


def is_reachable(posting: Posting) -> bool:
    """Reachable from India without a visa.

    "Remote" alone is not enough and the spike proved it: every remote-bucket role it
    found was country-scoped elsewhere ("Remote - United States", "Portugal, Remote"),
    which dies at eligibility rule 10 or 11. A remote posting counts only if it names
    India, or names no country at all.
    """
    location = posting.location or ""
    if INDIA.search(location):
        return True
    if REMOTE.search(location):
        # "Remote" with no other place name is worth surfacing; "Remote, Canada" is not.
        # Two letters, not three: the first live run let through "Remote, US", because
        # a country code is shorter than a country name and just as disqualifying.
        others = re.sub(REMOTE, "", location)
        return not re.search(r"[A-Za-z]{2,}", others)
    return False


def rank(postings: list[Posting], ledger: Ledger) -> list[Ranked]:
    """Order by how much of the résumé the posting actually asks for.

    Technologies the master carries are worth more than generic title overlap, because
    they are the part a tailored résumé can genuinely speak to.
    """
    ranked: list[Ranked] = []

    for posting in postings:
        haystack = _tokens(f"{posting.title} {posting.description}")
        matched = sorted(
            tech
            for tech in ledger.technologies
            if _tokens(tech) and _tokens(tech) <= haystack
        )
        score = len(matched) * 3
        if AI_TITLE.search(posting.title):
            score += 2
        if INDIA.search(posting.location or ""):
            score += 2
        if posting.has_description:
            score += 1

        reason = (
            f"{len(matched)} matching technologies"
            + (f" ({', '.join(matched[:6])})" if matched else "")
            + ("" if posting.has_description else "; no description in the listing")
        )
        ranked.append(Ranked(posting=posting, score=score, matched=matched, reason=reason))

    ranked.sort(key=lambda r: (-r.score, r.posting.company, r.posting.title))
    return ranked


def shortlist(postings: list[Posting], ledger: Ledger, *, limit: int = 10) -> list[Ranked]:
    eligible = [p for p in postings if is_relevant(p) and is_reachable(p)]
    return rank(eligible, ledger)[:limit]

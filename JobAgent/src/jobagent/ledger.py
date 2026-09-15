"""Fact ledger and element keys (SPEC §4.4).

The ledger is the oracle for T-1..T-5: every claim FactGuard checks is resolved
against it, and every provenance pointer names an element key that must exist in
it. C-8 is the reason this module refuses rather than derives.
"""

from __future__ import annotations

import hashlib

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class MasterIdsMissing(Exception):
    """The master's declared `id` set does not match the expected key set (C-8)."""


class NumberFact(BaseModel):
    """A numeral the resume actually contains, with the qualifier that bounds it.

    The qualifier is part of the fact. `25+` claims "at least 25"; `25` claims
    exactly 25. `up to 80%` is a ceiling; `80%` is an achievement. Dropping the
    qualifier during tailoring is fabrication, which is why C3 compares both.
    """

    element_key: str
    value: str
    qualifier: str | None = None
    context: str = ""

    model_config = {"frozen": True}


class Ledger(BaseModel):
    """Every fact the candidate may truthfully claim, addressed by element key."""

    master_hash: str
    technologies: set[str] = Field(default_factory=set)
    numbers: list[NumberFact] = Field(default_factory=list)

    model_config = {"frozen": True}


# Leading qualifiers that weaken or bound the number that follows.
_LEADING_QUALIFIERS = ("up to", "approximately", "approx", "about", "around", "over", "under", "~")

#: Re-exported for FactGuard C3, so the text extractor and the ledger split agree.
LEADING_QUALIFIERS_TEXT = _LEADING_QUALIFIERS


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def master_hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def build_ledger(html: str) -> Ledger:
    soup = _soup(html)
    if not soup.find(attrs={"id": True}):
        raise MasterIdsMissing(
            "the master declares no element ids; run the Phase 0 id migration (T-0.4). "
            "Key derivation is not a fallback — see C-8."
        )

    technologies = {
        el.get_text(strip=True)
        for el in soup.select(".skill span.v[id]")
        if el.get_text(strip=True)
    }

    numbers = [
        _number_fact(el["id"], el.get_text(" ", strip=True))
        for el in soup.select("span.n[id]")
        if el.get_text(strip=True)
    ]

    return Ledger(master_hash=master_hash(html), technologies=technologies, numbers=numbers)


def element_text(html: str, key: str) -> str:
    """Resolve a provenance pointer to the master text it names.

    Raises `KeyError` when the key is absent. That is deliberate and is the whole of
    C-8: a pointer must resolve to the right text or fail loudly. v1's derived keys
    could resolve to *different* text after an edit, which is worse than either.
    """
    el = _soup(html).find(id=key)
    if el is None:
        raise KeyError(f"no element with id {key!r} in this master")
    return el.get_text(" ", strip=True)


def _number_fact(element_key: str, text: str) -> NumberFact:
    """Split a declared numeral into the value and the qualifier that bounds it."""
    raw = " ".join(text.split())
    lowered = raw.lower()

    qualifier: str | None = None
    value = raw

    for lead in _LEADING_QUALIFIERS:
        if lowered.startswith(lead):
            qualifier = lead
            value = raw[len(lead) :].strip()
            break

    if value.endswith("+"):
        # A trailing "+" is its own qualifier and survives independently of a leading one.
        qualifier = f"{qualifier} +".strip() if qualifier else "+"
        value = value[:-1].strip()

    return NumberFact(element_key=element_key, value=value, qualifier=qualifier, context=raw)

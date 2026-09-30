"""Fact ledger and element keys (SPEC §4.4).

The ledger is the oracle for T-1..T-5: every claim FactGuard checks is resolved
against it, and every provenance pointer names an element key that must exist in
it. C-8 is the reason this module refuses rather than derives.
"""

from __future__ import annotations

import hashlib
import re
from typing import Literal

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

FactClass = Literal[
    "organisation",
    "title",
    "date_range",
    "number",
    "technology",
    "degree_cert",
    "project",
    "achievement",
    "award",
]


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


class Fact(BaseModel):
    fact_id: str
    klass: FactClass
    value: str
    element_key: str
    qualifier: str | None = None
    context: str = ""

    model_config = {"frozen": True}


class Ledger(BaseModel):
    """Every fact the candidate may truthfully claim, addressed by element key."""

    master_hash: str
    facts: list[Fact] = Field(default_factory=list)
    technologies: set[str] = Field(default_factory=set)
    organisations: set[str] = Field(default_factory=set)
    projects: set[str] = Field(default_factory=set)
    numbers: list[NumberFact] = Field(default_factory=list)
    #: Byte-exact strings C2 holds identical in every tailored version.
    immutable: dict[str, str] = Field(default_factory=dict)
    #: alias -> canonical skill value, derived from the master (see _synonyms_for).
    synonyms: dict[str, str] = Field(default_factory=dict)
    #: Technologies deliberately absent from the resume, used as tripwires (config).
    canaries: set[str] = Field(default_factory=set)
    #: verb -> scope rank; a reworded sentence may never increase it (C8, AC-AF-09).
    scope_verbs: dict[str, int] = Field(default_factory=dict)

    model_config = {"frozen": True}


# Leading qualifiers that weaken or bound the number that follows.
_LEADING_QUALIFIERS = ("up to", "approximately", "approx", "about", "around", "over", "under", "~")

#: Re-exported for FactGuard C3, so the text extractor and the ledger split agree.
LEADING_QUALIFIERS_TEXT = _LEADING_QUALIFIERS

_QUALIFIER_ALT = "|".join(re.escape(q) for q in _LEADING_QUALIFIERS)
_NUMERAL = re.compile(
    rf"(?:(?P<qual>{_QUALIFIER_ALT})\s+)?(?P<num>\d[\d,]*(?:\.\d+)?\s*%?)(?P<plus>\+)?",
    re.IGNORECASE,
)

#: Default scope ladder (AC-AF-09). Config may extend it; it may never be reordered
#: without re-running the mutation suite, because C8 compares ranks numerically.
DEFAULT_SCOPE_VERBS: dict[str, int] = {
    "mentor": 1, "mentored": 1,
    "lead": 2, "led": 2,
    "manage": 3, "managed": 3,
    "head": 4, "headed": 4,
    "found": 5, "founded": 5,
}


def numerals_in(text: str) -> list[tuple[str, str | None, str]]:
    """Pull (value, qualifier, context) triples out of free text.

    One extractor, used by both the ledger and FactGuard C3 — "what counts as a
    number" has to be defined exactly once or the check and the oracle disagree.
    """
    out: list[tuple[str, str | None, str]] = []
    for m in _NUMERAL.finditer(text):
        value = m.group("num").replace(" ", "")
        qualifier = m.group("qual").lower() if m.group("qual") else None
        if m.group("plus"):
            qualifier = f"{qualifier} +".strip() if qualifier else "+"
        start, end = max(0, m.start() - 40), min(len(text), m.end() + 40)
        out.append((value, qualifier, " ".join(text[start:end].split())))
    return out


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def master_hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


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


def _synonyms_for(value: str) -> set[str]:
    """Aliases a skill value legitimately answers to, derived from the value itself.

    Two shapes, both present in the master and both deterministic:
      "Model Context Protocol (MCP)"  -> MCP
      "Kubernetes / Helm"             -> Kubernetes, Helm

    This replaces an earlier substring heuristic that was quietly too generous: it
    would have accepted a claim to "JAX" because the resume lists "JAX-RS / Jersey",
    which is a different technology entirely. §8.2 C4 asks for ledger + synonym table,
    matched exactly, and deriving the table from the document keeps it versioned with it.
    """
    aliases: set[str] = set()
    paren = re.search(r"\(([A-Za-z][\w.+#-]{1,20})\)\s*$", value.strip())
    if paren:
        aliases.add(paren.group(1))
        aliases.add(value[: paren.start()].strip())
    for part in re.split(r"\s*/\s*", re.sub(r"\s*\([^)]*\)\s*$", "", value)):
        part = part.strip()
        if part and part != value:
            aliases.add(part)
    return {a for a in aliases if len(a) > 1}


def _organisation_from_heading(text: str) -> str:
    """The employer's name, without the parenthetical gloss or the location."""
    return re.split(r"\s+[-–—]\s+|\s*\(", text.strip(), maxsplit=1)[0].strip()


def build_ledger(html: str, *, canaries: set[str] | None = None) -> Ledger:
    soup = _soup(html)
    if not soup.find(attrs={"id": True}):
        raise MasterIdsMissing(
            "the master declares no element ids; run the Phase 0 id migration (T-0.4). "
            "Key derivation is not a fallback — see C-8."
        )

    facts: list[Fact] = []

    def add(klass: FactClass, value: str, key: str, qualifier=None, context="") -> None:
        seed = f"{klass}|{value}|{key}"
        facts.append(
            Fact(
                fact_id=hashlib.sha256(seed.encode()).hexdigest()[:12],
                klass=klass,
                value=value,
                element_key=key,
                qualifier=qualifier,
                context=context,
            )
        )

    # --- technologies: one per declared skill value -------------------------
    technologies: set[str] = set()
    synonyms: dict[str, str] = {}
    for el in soup.select(".skill span.v[id]"):
        value = el.get_text(strip=True)
        if value:
            technologies.add(value)
            for alias in _synonyms_for(value):
                synonyms[alias] = value
            add("technology", value, el["id"])

    # --- immutables: what C2 holds byte-exact -------------------------------
    immutable: dict[str, str] = {}
    for key in ("hdr.name", "hdr.role", "hdr.tag"):
        el = soup.find(id=key)
        if el:
            immutable[key] = el.get_text(" ", strip=True)
    for el in soup.select('[id^="hdr.contact."]'):
        immutable[el["id"]] = el.get_text(" ", strip=True)
    for el in soup.select('[id$=".meta"]'):
        immutable[el["id"]] = el.get_text(" ", strip=True)
    for key in ("edu.p1", "awards.p1"):
        el = soup.find(id=key)
        if el:
            immutable[key] = el.get_text(" ", strip=True)

    if "hdr.role" in immutable:
        add("title", immutable["hdr.role"], "hdr.role")

    # --- date ranges live in the .meta lines and the education line ---------
    date_range = re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}"
        r"\s*[-–—]\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}))",
        re.IGNORECASE,
    )
    for key, text in immutable.items():
        for match in date_range.findall(text):
            add("date_range", match, key)

    # --- organisations and projects -----------------------------------------
    organisations: set[str] = set()
    for el in soup.select('[id^="exp."][id$=".h3"]'):
        org = _organisation_from_heading(el.get_text(" ", strip=True))
        if org:
            organisations.add(org)
            add("organisation", org, el["id"])

    edu = soup.find(id="edu.p1")
    if edu:
        text = edu.get_text(" ", strip=True)
        # "B.Tech, ... - MIT Academy of Engineering (MITAOE), Pune | ..."
        inst = re.search(r"[-–—]\s*([A-Z][^(|]+?)\s*(?:\(|\||$)", text)
        if inst:
            organisations.add(inst.group(1).strip())
            add("organisation", inst.group(1).strip(), "edu.p1")
        degree = re.match(r"\s*([^,]+,[^-–—]+)", text)
        if degree:
            add("degree_cert", degree.group(1).strip(), "edu.p1")

    projects: set[str] = set()
    for el in soup.select('[id^="proj."][id$=".h3"]'):
        name = _organisation_from_heading(el.get_text(" ", strip=True))
        if name:
            projects.add(name)
            add("project", name, el["id"])

    award = soup.find(id="awards.p1")
    if award:
        add("award", award.get_text(" ", strip=True), "awards.p1")

    # --- numbers, from the text of every keyed element ----------------------
    # The master does not wrap its numerals in spans, so the number's address is the
    # element that contains it. An explicit `span.n[id]` wrapper still wins if present.
    numbers: list[NumberFact] = []
    seen_numbers: set[tuple[str, str, str | None]] = set()

    def collect(key: str, text: str) -> None:
        for value, qualifier, context in numerals_in(text):
            if (key, value, qualifier) in seen_numbers:
                continue
            seen_numbers.add((key, value, qualifier))
            numbers.append(
                NumberFact(element_key=key, value=value, qualifier=qualifier, context=context)
            )
            add("number", value, key, qualifier=qualifier, context=context)

    for el in soup.select("span.n[id]"):
        collect(el["id"], el.get_text(" ", strip=True))

    for el in soup.select('p[id], li[id], div.meta[id], div[id^="skills.s"]'):
        if el.select_one("span.n[id]"):
            continue  # already addressed at finer granularity
        collect(el["id"], el.get_text(" ", strip=True))

    # --- achievements: the experience bullets themselves --------------------
    for el in soup.select('li[id^="exp."], li[id^="proj."]'):
        add("achievement", el.get_text(" ", strip=True)[:200], el["id"])

    return Ledger(
        master_hash=master_hash(html),
        facts=facts,
        technologies=technologies,
        organisations=organisations,
        projects=projects,
        numbers=numbers,
        synonyms=synonyms,
        immutable=immutable,
        canaries=canaries or set(),
        scope_verbs=dict(DEFAULT_SCOPE_VERBS),
    )

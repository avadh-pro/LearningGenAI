"""Tailoring contract — diff-friendly by construction (SPEC §10).

The generator never emits HTML. It emits a `TailoringPlan`: element keys, orderings,
and at most one rewritten paragraph. `apply_plan` is the only thing that touches the
document, and it can perform exactly six operations. Everything else is impossible
rather than merely forbidden, which is what lets C1 verify the result cheaply and
what keeps the reviewer's diff small enough to actually read (§10.1, D-2).

The six allowed operations (§10.2):
  1. reorder `<li>` within the same `<ul>`
  2. reorder `.skill` lines
  3. reorder values within one skill line
  4. rewrite `summary.p1`
  5. toggle `<b>` on existing text
  6. remove an `<li>`
"""

from __future__ import annotations

import re
from typing import Literal

from bs4 import BeautifulSoup, NavigableString
from pydantic import BaseModel, Field

MAX_EMPHASIS = 3


class IllegalOperation(Exception):
    """The plan asked for something outside the six allowed operations."""


class Emphasis(BaseModel):
    element_key: str
    phrase: str

    model_config = {"frozen": True}


class Sentence(BaseModel):
    text: str
    provenance: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}


class SummaryRewrite(BaseModel):
    sentences: list[Sentence]

    model_config = {"frozen": True}


class TailoringPlan(BaseModel):
    """What the `generate` stage is allowed to say. No HTML appears anywhere in it."""

    skill_line_order: list[str] = Field(default_factory=list)
    skill_value_order: dict[str, list[str]] = Field(default_factory=dict)
    bullet_order: dict[str, list[str]] = Field(default_factory=dict)
    emphasise: list[Emphasis] = Field(default_factory=list)
    remove: list[str] = Field(default_factory=list)
    summary: SummaryRewrite | None = None
    rationale: str = ""

    model_config = {"frozen": True}


class Change(BaseModel):
    kind: Literal["reorder", "rewrite_summary", "emphasis", "remove", "violation"]
    element_key: str
    detail: str = ""

    model_config = {"frozen": True}


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def rendered_text(html: str) -> str:
    """What the reader actually sees, whitespace collapsed."""
    return " ".join(_soup(html).get_text().split())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IllegalOperation(message)


def _find(soup: BeautifulSoup, key: str):
    el = soup.find(id=key)
    _require(el is not None, f"the master has no element {key!r}; the plan does not fit it")
    return el


def _reorder_siblings(parent, keys: list[str], *, label: str) -> None:
    """Permute existing children **in place**, leaving everything else untouched.

    Two things make this subtler than it looks. Appending the children in the new
    order moves them to the END of their parent, which for a flat document means the
    skill lines would land after Education and Awards. And the whitespace between
    block elements lives in text nodes *between* them, so moving only the tags strands
    the separators and the rendered text runs together ("(AIQA)AI").

    So the elements are swapped through placeholders: each target keeps the exact slot
    its predecessor occupied, and every surrounding node stays where it was.
    """
    existing = [c for c in parent.find_all(id=True, recursive=False)]
    by_key = {c["id"]: c for c in existing}
    _require(
        set(keys) <= set(by_key),
        f"{label}: {sorted(set(keys) - set(by_key))} are not children of this element — "
        "values may be permuted within a line, never moved between lines",
    )

    targets = [c for c in existing if c["id"] in set(keys)]
    ordered = [by_key[k] for k in keys]

    placeholders = []
    for child in targets:
        marker = BeautifulSoup("", "lxml").new_tag("jobagent-slot")
        child.replace_with(marker)
        placeholders.append(marker)

    for marker, child in zip(placeholders, ordered, strict=True):
        marker.replace_with(child)



def _reorder_skill_values(line, value_keys: list[str]) -> None:
    """Permute the values on one skill line, keeping the ", " separators intact.

    A skill line is `<b>label</b>&nbsp; <span>A</span>, <span>B</span>, ...` — the
    commas are text nodes *between* the spans, so moving only the spans strands the
    separators and produces ", , , , AB C". The line is rebuilt instead: label, the
    original gap after it, then the values joined by the separator they already used.
    """
    spans = {v["id"]: v for v in line.select("span.v[id]")}
    _require(
        set(value_keys) <= set(spans),
        f"{sorted(set(value_keys) - set(spans))} are not values on {line.get('id')!r} — "
        "values may be permuted within a line, never moved between lines",
    )

    ordered = [spans[k] for k in value_keys]
    ordered += [span for key, span in spans.items() if key not in set(value_keys)]

    label = line.find("b")
    gap = None
    if label is not None:
        nxt = label.next_sibling
        if isinstance(nxt, NavigableString):
            gap = str(nxt)

    for node in list(line.contents):
        if node is not label:
            node.extract()

    if gap:
        line.append(NavigableString(gap))
    for i, span in enumerate(ordered):
        if i:
            line.append(NavigableString(", "))
        line.append(span)

def apply_plan(master_html: str, plan: TailoringPlan) -> str:
    """Apply a plan deterministically. Same plan + same master = same bytes, always."""
    _require(
        len(plan.emphasise) <= MAX_EMPHASIS,
        f"{len(plan.emphasise)} emphases exceeds the change budget of {MAX_EMPHASIS}; "
        "a tailored resume the reviewer cannot scan in a glance defeats the purpose",
    )

    soup = _soup(master_html)

    # 2. reorder skill lines (they share a parent with the other section content)
    if plan.skill_line_order:
        first = _find(soup, plan.skill_line_order[0])
        _reorder_siblings(first.parent, plan.skill_line_order, label="skill lines")

    # 3. reorder values within one line
    for line_key, value_keys in plan.skill_value_order.items():
        line = _find(soup, line_key)
        for key in value_keys:
            _find(soup, key)
        _reorder_skill_values(line, value_keys)

    # 1. reorder bullets within one list
    for list_key, bullet_keys in plan.bullet_order.items():
        first = _find(soup, bullet_keys[0])
        _require(
            all(k.startswith(list_key) for k in bullet_keys),
            f"bullets {bullet_keys} do not all belong to {list_key!r}",
        )
        _reorder_siblings(first.parent, bullet_keys, label=f"bullets in {list_key}")

    # 6. remove a bullet
    for key in plan.remove:
        _find(soup, key).decompose()

    # 4. rewrite the summary — the one prose block tailoring may touch
    if plan.summary is not None:
        target = _find(soup, "summary.p1")
        target.clear()
        target.append(NavigableString(" ".join(s.text for s in plan.summary.sentences)))

    # 5. emphasis: wrap existing text, never introduce any
    for item in plan.emphasise:
        el = _find(soup, item.element_key)
        _emphasise(el, item.phrase)

    return str(soup)


def _emphasise(el, phrase: str) -> None:
    """Wrap an existing occurrence of `phrase` in <b>. Adds markup, never content."""
    for node in list(el.descendants):
        if not isinstance(node, NavigableString):
            continue
        text = str(node)
        idx = text.lower().find(phrase.lower())
        if idx == -1:
            continue
        bold = BeautifulSoup("", "lxml").new_tag("b")
        bold.string = text[idx : idx + len(phrase)]
        node.replace_with(
            NavigableString(text[:idx]), bold, NavigableString(text[idx + len(phrase) :])
        )
        return
    raise IllegalOperation(
        f"{phrase!r} does not appear in {el.get('id')!r}; emphasis may only mark text "
        "the master already contains"
    )


def _index_elements(html: str) -> dict[str, tuple[str, str]]:
    """key -> (tag name, rendered text) for every addressable element."""
    return {
        el["id"]: (el.name, " ".join(el.get_text().split()))
        for el in _soup(html).find_all(id=True)
    }


def structural_diff(master_html: str, tailored_html: str) -> list[Change]:
    """C1 (AF-06, RT-02) — classify every change, and flag anything unclassifiable.

    This runs on the *artefact*, not on the plan, so it catches a tailored document
    that `apply_plan` never produced: hand-edited HTML, a model that emitted markup,
    a corrupted artefact. Any change that is not one of the six allowed operations is
    a `violation`, and a single violation fails the artefact.
    """
    before, after = _index_elements(master_html), _index_elements(tailored_html)
    changes: list[Change] = []

    for key in before.keys() - after.keys():
        changes.append(Change(kind="remove", element_key=key, detail="element removed"))

    for key in after.keys() - before.keys():
        changes.append(
            Change(
                kind="violation",
                element_key=key,
                detail="element introduced; tailoring may reorder and remove, never add",
            )
        )

    containers = _containers(master_html) | _containers(tailored_html)
    for key in before.keys() & after.keys():
        (btag, btext), (atag, atext) = before[key], after[key]
        if key in containers:
            # A container's text is the concatenation of its children's, so permuting
            # them changes it by definition. Reordering is detected by document order
            # below; reading it here as well would report every allowed reorder as a
            # violation. Leaf text is still compared exactly.
            continue
        if btag != atag:
            changes.append(
                Change(kind="violation", element_key=key, detail=f"tag {btag} -> {atag}")
            )
        elif btext != atext:
            if key == "summary.p1":
                changes.append(Change(kind="rewrite_summary", element_key=key))
            else:
                changes.append(
                    Change(
                        kind="violation",
                        element_key=key,
                        detail=f"text changed: {btext[:60]!r} -> {atext[:60]!r}",
                    )
                )

    # Order and emphasis are compared over the elements that exist in BOTH documents.
    # Otherwise a removal reports itself three times - as a remove, as a reorder (the
    # id sequence necessarily changed) and as an emphasis change (the deleted bullet
    # took its <b> with it) - and a reviewer reading three findings for one edit stops
    # trusting the diff.
    survivors = before.keys() & after.keys()
    if _order_of(master_html, survivors) != _order_of(tailored_html, survivors):
        changes.append(Change(kind="reorder", element_key="*", detail="document order changed"))

    if _bold_count(tailored_html, survivors) != _bold_count(master_html, survivors):
        changes.append(Change(kind="emphasis", element_key="*", detail="emphasis toggled"))

    return changes


def _containers(html: str) -> set[str]:
    """Addressable elements that contain other addressable elements."""
    return {
        el["id"]
        for el in _soup(html).find_all(id=True)
        if el.find(id=True) is not None
    }

def _order_of(html: str, keys: set[str]) -> list[str]:
    return [el["id"] for el in _soup(html).find_all(id=True) if el["id"] in keys]


def _bold_count(html: str, keys: set[str]) -> int:
    soup = _soup(html)
    return sum(len(soup.find(id=k).find_all("b")) for k in keys if soup.find(id=k))


def letter_spacing_deltas(master_html: str, tailored_html: str) -> list[str]:
    """C2 support: the only CSS difference §8.2 permits is letter-spacing."""
    pattern = re.compile(r"<style>(.*?)</style>", re.S)
    a = pattern.search(master_html)
    b = pattern.search(tailored_html)
    if not a or not b:
        return ["<style> block missing"]
    strip = lambda css: re.sub(r"letter-spacing\s*:[^;]+;?", "", css)  # noqa: E731
    if strip(a.group(1)) == strip(b.group(1)):
        return []
    return ["<style> changed beyond letter-spacing"]

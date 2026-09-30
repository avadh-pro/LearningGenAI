"""Deterministic tailoring planner.

SPEC §10.3 has the `generate` stage emit the plan. This is the model-free version of
that stage, and it is not a placeholder: reordering by relevance is most of what
tailoring *is* (§10.1 — "tailoring is reorder-first"), and doing it deterministically
has three properties a model cannot offer.

It cannot fabricate. It only permutes what the master already says, so C1-C14 have
nothing to catch. It costs nothing, so it runs before any budget question arises. And
it is reproducible: the same JD and the same master produce the same plan, byte for
byte, which makes the diff reviewable and the output diffable across runs.

The summary rewrite is deliberately left to a model (`summary=None` here). It is the
one operation that produces new prose, and new prose is the only thing in the
tailoring contract that can lie.
"""

from __future__ import annotations

import re

from .ledger import Ledger
from .tailor import Emphasis, TailoringPlan, _soup

MAX_EMPHASIS = 3

_STOPWORDS = frozenset(
    """a an and are as at be by for from has have in into is it its of on or that the
    their this to with will you your we our us role team work working experience years
    strong ability able across using use used including etc job apply please""".split()
)


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9+#.]{2,}", text.casefold())
    return {w.strip(".") for w in words if w not in _STOPWORDS and len(w) > 2}


def _mentions(jd_tokens: set[str], phrase: str) -> int:
    """How much of a phrase the JD actually contains. Multi-word values score higher
    when fully present, so "Model Context Protocol (MCP)" outranks a stray "protocol".
    """
    parts = _tokens(phrase)
    return len(parts & jd_tokens)


def plan_for_jd(master_html: str, ledger: Ledger, jd_text: str) -> TailoringPlan:
    """Rank the master's own content against one job description.

    Ordering is stable: ties keep the master's order, so an unrelated JD produces a
    near-identity plan rather than an arbitrary shuffle.
    """
    jd = _tokens(jd_text)
    soup = _soup(master_html)

    # --- skill lines, most relevant first -----------------------------------
    lines = [el for el in soup.select("div.skill[id]")]
    line_scores: dict[str, int] = {}
    value_orders: dict[str, list[str]] = {}

    for line in lines:
        values = [v for v in line.select("span.v[id]")]
        scored = [(v["id"], _mentions(jd, v.get_text(strip=True))) for v in values]
        line_scores[line["id"]] = sum(score for _, score in scored)
        if any(score for _, score in scored):
            ordered = sorted(range(len(scored)), key=lambda i: (-scored[i][1], i))
            value_orders[line["id"]] = [scored[i][0] for i in ordered]

    line_order = [
        lines[i]["id"]
        for i in sorted(range(len(lines)), key=lambda i: (-line_scores[lines[i]["id"]], i))
    ]

    # --- bullets within each list, most relevant first -----------------------
    bullet_orders: dict[str, list[str]] = {}
    for ul in soup.find_all("ul"):
        bullets = [li for li in ul.find_all("li", recursive=False) if li.has_attr("id")]
        if len(bullets) < 2:
            continue
        scored = [(li["id"], len(_tokens(li.get_text()) & jd)) for li in bullets]
        if not any(score for _, score in scored):
            continue
        ordered = sorted(range(len(scored)), key=lambda i: (-scored[i][1], i))
        list_key = bullets[0]["id"].rsplit(".", 1)[0]
        bullet_orders[list_key] = [scored[i][0] for i in ordered]

    # --- emphasis: the technologies this JD actually asks for ----------------
    wanted = [
        tech
        for tech in sorted(ledger.technologies, key=len, reverse=True)
        if _tokens(tech) and _tokens(tech) <= jd
    ]
    emphasise: list[Emphasis] = []
    for tech in wanted[:MAX_EMPHASIS]:
        el = soup.find(string=re.compile(re.escape(tech), re.IGNORECASE))
        if el is None:
            continue
        holder = el.parent
        while holder is not None and not holder.has_attr("id"):
            holder = holder.parent
        if holder is not None:
            emphasise.append(Emphasis(element_key=holder["id"], phrase=tech))

    matched = sorted({t for t in ledger.technologies if _tokens(t) and _tokens(t) <= jd})
    rationale = (
        f"Deterministic relevance ordering against {len(jd)} JD terms. "
        f"Matched technologies: {', '.join(matched[:12]) or 'none'}."
    )

    return TailoringPlan(
        skill_line_order=line_order,
        skill_value_order=value_orders,
        bullet_order=bullet_orders,
        emphasise=emphasise[:MAX_EMPHASIS],
        rationale=rationale,
    )

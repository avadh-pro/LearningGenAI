"""T-0.4 — give the master resume explicit element ids (SPEC §4.4, C-8).

Run once, under review. After this, `build_ledger` REFUSES a master whose id set does
not match the expected keys; there is no derivation path in production, because a
derived key silently repoints to different text the moment the resume is edited.

What it changes: `id` attributes, and `<span class="v">` wrappers around individual
skill values so a provenance pointer can name one technology rather than a whole line.
What it must NOT change: a single character of rendered text. The script asserts that
itself and refuses to write if the normalised text differs.

    python tools/migrate_resume_ids.py resume/resume-ats.html
    python tools/migrate_resume_ids.py resume/resume-ats.html --check   # verify only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

# Content-anchored where cheap (C-8 rule 3): `skills.s1.langchain`, not `skills.s1.v3`,
# so inserting a value cannot repoint an existing pointer.
CONTACT_ORDER = ["location", "phone", "email", "linkedin", "github"]


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    return s or "x"


def heading_slug(text: str, max_len: int = 26) -> str:
    """A short, stable slug for an <h3>: drop the subtitle, never truncate mid-word."""
    head = re.split(r"\s+[-–—]\s+|\s*\(", text.strip(), maxsplit=1)[0]
    s = slug(head)
    if len(s) <= max_len:
        return s
    kept: list[str] = []
    for word in s.split("-"):
        if len("-".join([*kept, word])) > max_len:
            break
        kept.append(word)
    return "-".join(kept) or s[:max_len].rstrip("-")


def normalised_text(html: str) -> str:
    """Rendered text with all whitespace collapsed — the thing that must not change."""
    return " ".join(BeautifulSoup(html, "lxml").get_text().split())


def _wrap_skill_values(div, line_key: str) -> None:
    """Wrap each comma-separated value after the <b> label in its own keyed span.

    Existing `.nw` spans are given an id in place rather than double-wrapped. Text nodes
    are split on commas only — never inside a span — so `Java (Core, 21)` stays one value.
    """
    label = div.find("b")
    started = label is None
    seen: set[str] = set()

    for node in list(div.contents):
        if node is label:
            started = True
            continue
        if not started:
            continue

        if getattr(node, "name", None) == "span" and "nw" in (node.get("class") or []):
            key = f"{line_key}.{slug(node.get_text())}"
            if key in seen:
                key = f"{key}-{len(seen)}"
            node["id"] = key
            node["class"] = list(node.get("class") or []) + ["v"]
            seen.add(key)
            continue

        if isinstance(node, NavigableString):
            parts = re.split(r"(,)", str(node))
            replacement: list = []
            for part in parts:
                if part == ",":
                    replacement.append(NavigableString(","))
                    continue
                core = part.strip()
                if not core:
                    replacement.append(NavigableString(part))
                    continue
                lead = part[: len(part) - len(part.lstrip())]
                trail = part[len(part.rstrip()) :]
                key = f"{line_key}.{slug(core)}"
                if key in seen:
                    key = f"{key}-{len(seen)}"
                seen.add(key)
                span = BeautifulSoup("", "lxml").new_tag("span")
                span["class"] = ["v"]
                span["id"] = key
                span.string = core
                if lead:
                    replacement.append(NavigableString(lead))
                replacement.append(span)
                if trail:
                    replacement.append(NavigableString(trail))
            node.replace_with(*replacement)


def migrate(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "lxml")
    keys: list[str] = []

    def put(el, key: str) -> None:
        if el is None:
            return
        el["id"] = key
        keys.append(key)

    # --- header -----------------------------------------------------------
    header = soup.find("header")
    if header:
        put(header.find("h1"), "hdr.name")
        put(header.find(class_="role"), "hdr.role")
        put(header.find(class_="tag"), "hdr.tag")
        contact = header.find(class_="contact")
        if contact:
            put(contact, "hdr.contact")
            spans = contact.find_all("span", class_="nw")
            for name, span in zip(CONTACT_ORDER, spans, strict=False):
                put(span, f"hdr.contact.{name}")

    # --- sections, keyed by their heading ---------------------------------
    section_slugs = {
        "professional summary": "summary",
        "work experience": "exp",
        "key ai projects": "proj",
        "skills": "skills",
        "education": "edu",
        "awards": "awards",
    }

    for h2 in soup.find_all("h2"):
        name = section_slugs.get(h2.get_text(strip=True).casefold())
        if not name:
            continue
        put(h2, f"{name}.h2")

        # Walk siblings until the next <h2>.
        block, node = [], h2.next_sibling
        while node is not None and getattr(node, "name", None) != "h2":
            if getattr(node, "name", None):
                block.append(node)
            node = node.next_sibling

        if name in ("summary", "edu", "awards"):
            for i, p in enumerate([n for n in block if n.name == "p"], start=1):
                put(p, f"{name}.p{i}")

        elif name in ("exp", "proj"):
            current = None
            for el in block:
                if el.name == "h3":
                    current = heading_slug(el.get_text())
                    put(el, f"{name}.{current}.h3")
                elif el.name == "div" and "meta" in (el.get("class") or []):
                    put(el, f"{name}.{current}.meta")
                elif el.name == "ul":
                    for i, li in enumerate(el.find_all("li", recursive=False), start=1):
                        put(li, f"{name}.{current}.li{i}")

        elif name == "skills":
            for i, div in enumerate(
                [n for n in block if n.name == "div" and "skill" in (n.get("class") or [])],
                start=1,
            ):
                line_key = f"skills.s{i}"
                put(div, line_key)
                label = div.find("b")
                if label is not None:
                    put(label, f"{line_key}.label")
                _wrap_skill_values(div, line_key)
                keys.extend(
                    s["id"] for s in div.find_all("span", class_="v") if s.has_attr("id")
                )

    return str(soup), keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = ap.parse_args()

    original = args.path.read_text(encoding="utf-8")
    migrated, keys = migrate(original)

    before, after = normalised_text(original), normalised_text(migrated)
    if before != after:
        # Show the first divergence rather than a wall of text.
        for i, (a, b) in enumerate(zip(before, after, strict=False)):
            if a != b:
                print(f"TEXT CHANGED at char {i}:\n  before: ...{before[max(0,i-60):i+60]}...\n"
                      f"  after:  ...{after[max(0,i-60):i+60]}...", file=sys.stderr)
                break
        else:
            print(f"TEXT LENGTH CHANGED: {len(before)} -> {len(after)}", file=sys.stderr)
        return 1

    print(f"text identical ({len(before)} chars), {len(keys)} element keys assigned")
    if args.check:
        return 0
    args.path.write_text(migrated, encoding="utf-8")
    print(f"wrote {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

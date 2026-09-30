"""PDF render and ATS verification (SPEC §4.9).

The tailored resume is only useful if an applicant tracking system can read it. Three
independent parsers have to agree, because they disagree in practice: a layout that
pdfminer reads in order can come out scrambled in pypdf, and an ATS will use whichever
one it happens to use.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER_SCRIPT = REPO_ROOT / "resume" / "render.py"


class RenderError(RuntimeError):
    """Chromium could not produce a PDF. R-12: usually a browser path drift."""


class AtsReport(BaseModel):
    pages: int = 0
    parsers_agreeing: int = 0
    missing_content: list[str] = Field(default_factory=list)
    nw_intact: bool = True
    images: int = 0
    high_codepoints: int = 0
    passed: bool = False
    notes: list[str] = Field(default_factory=list)


def render_pdf(html_path: Path, out_pdf: Path) -> Path:
    """Drive `resume/render.py`, which owns the Chromium print settings.

    `PW_CHROME` is honoured because the hardcoded browser build drifts — R-12 predicted
    it and it has already happened once (render.py points at chromium-1208; the machine
    had 1200).
    """
    env = {**os.environ}
    if "PW_CHROME" not in env:
        pattern = "ms-playwright/chromium-*/chrome-win64/chrome.exe"
        guess = sorted(Path(env.get("LOCALAPPDATA", "")).glob(pattern))
        if guess:
            env["PW_CHROME"] = str(guess[-1])

    result = subprocess.run(
        [sys.executable, str(RENDER_SCRIPT), str(html_path), str(out_pdf)],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0 or not out_pdf.exists():
        raise RenderError(
            f"render.py failed ({result.returncode}). "
            f"Set PW_CHROME to an installed Chromium. stderr: {result.stderr[-400:]}"
        )
    return out_pdf


def _extract(pdf: Path) -> dict[str, tuple[str, int]]:
    """Text and page count from each parser, independently."""
    out: dict[str, tuple[str, int]] = {}

    from pdfminer.high_level import extract_text

    out["pdfminer"] = (extract_text(str(pdf)), 0)

    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    out["pypdf"] = ("\n".join(p.extract_text() or "" for p in reader.pages), len(reader.pages))

    import fitz

    doc = fitz.open(str(pdf))
    out["pymupdf"] = ("\n".join(p.get_text() for p in doc), doc.page_count)
    images = sum(len(doc[i].get_images()) for i in range(doc.page_count))
    doc.close()
    out["_images"] = ("", images)

    return out


def _words(text: str) -> set[str]:
    """Case-folded, because the stylesheet uppercases the name and every heading.

    The HTML says "Skills"; the PDF says "SKILLS". An ATS that extracted the heading
    has read it, and a comparison that calls that a failure is measuring the wrong
    thing - which it did, on the first real run, for all ten headings at once.
    """
    return {w.casefold() for w in re.findall(r"[A-Za-z][\w+#./-]{2,}", text)}


def ats_check(pdf: Path, master_html: str) -> AtsReport:
    """Verify the rendered PDF is machine-readable and complete (AC-RT-03..07).

    The content test is the one that matters: every substantive word in the master has
    to survive into the extracted text. A resume that renders beautifully and extracts
    as ligature soup is worse than a plain one, because it looks fine to the human who
    sends it.
    """
    report = AtsReport()
    extracted = _extract(pdf)
    report.images = extracted["_images"][1]
    report.pages = extracted["pypdf"][1] or extracted["pymupdf"][1]

    texts = {name: text for name, (text, _) in extracted.items() if not name.startswith("_")}
    from .tailor import rendered_text

    expected = _words(rendered_text(master_html))

    agreeing = 0
    worst_missing: set[str] = set()
    for name, text in texts.items():
        got = _words(text)
        missing = expected - got
        if not missing:
            agreeing += 1
        else:
            if len(missing) > len(worst_missing):
                worst_missing = missing
            report.notes.append(f"{name}: {len(missing)} words missing")

    report.parsers_agreeing = agreeing
    report.missing_content = sorted(worst_missing)[:20]
    report.high_codepoints = sum(1 for c in texts["pymupdf"] if ord(c) >= 0x2100)
    report.nw_intact = all(
        span in texts["pymupdf"].replace("\n", " ")
        for span in re.findall(r'class="[^"]*\bnw\b[^"]*"[^>]*>([^<]{3,40})<', master_html)[:10]
    )

    report.passed = (
        report.pages == 1
        and report.parsers_agreeing == 3
        and report.images == 0
        and report.high_codepoints == 0
    )
    return report

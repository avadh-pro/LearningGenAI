"""Source adapters — public job-board feeds (SPEC §4.2, Release 1 subset).

Release 1 reads boards; it never posts to them. The spike proved which boards are
reachable (`spike/out/boards.csv`: 20 of 50 on Greenhouse or Lever, 9 more on Ashby
or SmartRecruiters, 21 on ATSs none of these adapters can see), so this module
covers those four and is honest about which of them carry a job description in the
listing response.

Fetching is sequential and paced. These are public JSON endpoints, but there is no
reason to hammer them, and A-21's pacing discipline applies to reads as much as to
anything else.
"""

from __future__ import annotations

import html
import json
import random
import re
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

from pydantic import BaseModel, Field

UA = "JobAgent/0.1 (personal job search; contact via repo owner)"

ENDPOINTS: dict[str, str] = {
    # Greenhouse and Lever return the full description in the listing, so one request
    # per board yields everything. Ashby and SmartRecruiters do not, which is why
    # `has_description` is part of the contract rather than an assumption.
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{slug}/postings",
}

TIER = {"greenhouse": 1, "lever": 1, "ashby": 2, "smartrecruiters": 2}


class Posting(BaseModel):
    company: str
    ats: str
    title: str
    location: str
    url: str
    description: str = ""
    posted_at: datetime | None = None

    @property
    def has_description(self) -> bool:
        return len(self.description) > 200

    model_config = {"frozen": True}


class SourceResult(BaseModel):
    company: str
    ats: str
    slug: str
    status: str
    postings: list[Posting] = Field(default_factory=list)


def _strip_html(raw: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html.unescape(raw or "")).split())


def _get(url: str, timeout: int = 25):
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def _iso(value) -> datetime | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=UTC)
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_board(company: str, ats: str, slug: str, payload) -> list[Posting]:
    """Turn one board's payload into postings. Pure, so it is testable without network."""
    out: list[Posting] = []

    if ats == "greenhouse":
        for job in (payload or {}).get("jobs", []):
            out.append(
                Posting(
                    company=company,
                    ats=ats,
                    title=job.get("title", ""),
                    location=(job.get("location") or {}).get("name", ""),
                    url=job.get("absolute_url", ""),
                    description=_strip_html(job.get("content", "")),
                    posted_at=_iso(job.get("updated_at")),
                )
            )

    elif ats == "lever":
        for job in payload or []:
            categories = job.get("categories") or {}
            out.append(
                Posting(
                    company=company,
                    ats=ats,
                    title=job.get("text", ""),
                    location=categories.get("location", ""),
                    url=job.get("hostedUrl", ""),
                    description=job.get("descriptionPlain")
                    or _strip_html(job.get("description", "")),
                    posted_at=_iso(job.get("createdAt")),
                )
            )

    elif ats == "ashby":
        for job in (payload or {}).get("jobs", []):
            out.append(
                Posting(
                    company=company,
                    ats=ats,
                    title=job.get("title", ""),
                    location=job.get("location", ""),
                    url=job.get("jobUrl", ""),
                    description=_strip_html(job.get("descriptionHtml", "")),
                    posted_at=_iso(job.get("publishedAt")),
                )
            )

    elif ats == "smartrecruiters":
        for job in (payload or {}).get("content", []):
            loc = job.get("location") or {}
            parts = [loc.get("city"), loc.get("region"), loc.get("country")]
            out.append(
                Posting(
                    company=company,
                    ats=ats,
                    title=job.get("name", ""),
                    location=", ".join(p for p in parts if p),
                    url=f"https://jobs.smartrecruiters.com/{slug}/{job.get('id', '')}",
                    description="",  # requires a per-posting fetch
                    posted_at=_iso(job.get("releasedDate")),
                )
            )

    return out


def fetch_board(company: str, ats: str, slug: str, *, delay: float = 0.4) -> SourceResult:
    """One board, one request. Failure is recorded, never raised: a source that is
    down must not abort the run (AC-FM-01)."""
    url = ENDPOINTS[ats].format(slug=slug)
    try:
        payload = _get(url)
        status = "ok"
    except urllib.error.HTTPError as exc:
        return SourceResult(company=company, ats=ats, slug=slug, status=f"http_{exc.code}")
    except Exception as exc:  # noqa: BLE001 — any failure is a source failure
        return SourceResult(company=company, ats=ats, slug=slug, status=f"err_{type(exc).__name__}")
    finally:
        time.sleep(delay + random.uniform(0, delay))

    postings = parse_board(company, ats, slug, payload)
    return SourceResult(
        company=company,
        ats=ats,
        slug=slug,
        status=status if postings else "empty",
        postings=postings,
    )

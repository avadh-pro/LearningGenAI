"""FactGuard — the anti-fabrication verifier (SPEC §8).

Deterministic-first, judge-second. C1-C9 and C12-C14 are pure functions over the
artefacts and the ledger; only C10 (entailment) and C11 (company facts) call a
model, and they call a *different* model from the generator (D-1).

Nothing here is advisory. A single violation fails the artefact, and a failing
artefact cannot reach PENDING_REVIEW or the SUBMITTING transition (§6.4, M-15).
"""

from __future__ import annotations

import hashlib
import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from .ledger import LEADING_QUALIFIERS_TEXT as _LEADING_QUALIFIERS_TEXT
from .ledger import Ledger, element_text

ClaimKind = Literal["self", "company", "context"]

# Classes a human confirmation may waive, and classes it may never waive (M-16).
# The line is authorship versus fact: he is the authority on how his achievements
# are worded, not on whether a technology appears on his resume.
OVERRIDABLE_CHECKS = frozenset({"C3", "C9", "C10", "C12"})


class Claim(BaseModel):
    """One sentence destined for an employer, with the pointers that support it."""

    text: str
    kind: ClaimKind = "self"
    provenance: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}


class NotOverridable(Exception):
    """A confirmation was offered for a class no confirmation may waive (M-16)."""


class Violation(BaseModel):
    check: str
    claim_text: str
    detail: str

    @property
    def overridable(self) -> bool:
        """Whether a typed confirmation may waive this violation (M-16, §8.3)."""
        return self.check in OVERRIDABLE_CHECKS

    @property
    def violation_id(self) -> str:
        """Stable across re-runs of the same check on the same text."""
        seed = f"{self.check}|{self.claim_text}|{self.detail}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    @property
    def confirmation_prompt(self) -> str:
        """The exact string the reviewer must type to waive this violation (M-16).

        Generated from the violation so that it names the claim. v1 used one constant
        sentence for everything, which by its third use carried no information about
        *which* statement was being confirmed.
        """
        return f"I confirm: {self.claim_text}"

    model_config = {"frozen": True}


class Confirmation(BaseModel):
    violation_id: str
    typed_text: str

    model_config = {"frozen": True}


# The versioned extraction vocabulary. C4 can only flag a technology it can *see*,
# so this list is the detector, and the ledger is the allowlist. Terms here that
# are absent from the ledger are exactly the fabrication surface we care about;
# several (Azure, Kubernetes, TensorFlow) double as canaries.
DEFAULT_TECH_VOCABULARY: frozenset[str] = frozenset(
    {
        "LangChain", "LangGraph", "CrewAI", "LlamaIndex", "Haystack", "Semantic Kernel",
        "Qdrant", "Pinecone", "ChromaDB", "Weaviate", "Milvus", "FAISS", "OpenSearch",
        "Elasticsearch", "Redis", "PostgreSQL", "MySQL", "MongoDB", "Cassandra",
        "PyTorch", "TensorFlow", "JAX", "Keras", "scikit-learn", "XGBoost",
        "Hugging Face", "vLLM", "Ollama", "Triton", "ONNX",
        "AWS", "AWS Bedrock", "Azure", "GCP", "Vertex AI", "SageMaker",
        "Docker", "Kubernetes", "Helm", "Terraform", "Ansible", "Jenkins",
        "Python", "Java", "Go", "Rust", "TypeScript", "JavaScript", "C++", "Scala",
        "FastAPI", "Flask", "Django", "Spring", "Node.js", "React", "Vue",
        "Kafka", "RabbitMQ", "Airflow", "Prefect", "Dagster", "Spark", "Databricks",
        "Grafana", "Prometheus", "Datadog", "Opik", "LangSmith", "MLflow", "Weights & Biases",
        "Model Context Protocol", "MCP", "RAGAS", "DeepEval",
    }
)


# A first-person subject, explicit or implied. The second group catches the
# subjectless resume voice — "Architected a platform", "Owned delivery" — which
# asserts just as much about the candidate as "I architected".
_FIRST_PERSON = re.compile(r"\b(i|i'?ve|i'?m|my|me|mine|we|our|us)\b", re.IGNORECASE)
_RESUME_VERBS = (
    "architected|built|owned|shipped|led|delivered|designed|implemented|developed|"
    "engineered|scaled|migrated|automated|mentored|managed|drove|launched|created|"
    "have shipped|have built|have led|have owned|have delivered"
)
_IMPLIED_FIRST_PERSON = re.compile(rf"(^|[.;:]\s*)({_RESUME_VERBS})\b", re.IGNORECASE)


def _asserts_about_the_candidate(text: str) -> bool:
    return bool(_FIRST_PERSON.search(text) or _IMPLIED_FIRST_PERSON.search(text))


def check_claim_kind(
    claims: list[Claim], *, max_context: int = 2
) -> tuple[list[Claim], list[Violation]]:
    """C14 (C-6) — `context` is narrow, and the verifier decides, not the generator.

    `context` is permitted only for sentences that make no assertion about the
    candidate: the salutation, a transition, the closing line. Anything else that
    arrives labelled `context` is reclassified to `self` here, *before* C9 runs, so
    it must then produce a provenance pointer like any other claim about him.

    Returns the corrected claims and any cap violations. Reclassification itself is
    not a violation — it is the correction. The violation arrives later, from C9, if
    the sentence genuinely has nothing behind it.
    """
    corrected: list[Claim] = []
    for claim in claims:
        if claim.kind == "context" and _asserts_about_the_candidate(claim.text):
            corrected.append(claim.model_copy(update={"kind": "self"}))
        else:
            corrected.append(claim)

    violations: list[Violation] = []
    context_count = sum(1 for c in corrected if c.kind == "context")
    if context_count > max_context:
        violations.append(
            Violation(
                check="C14",
                claim_text=f"{context_count} context claims",
                detail=(
                    f"{context_count} `context` claims exceeds the cap of {max_context}; "
                    "an artefact that is mostly unverified prose is not a tailored artefact"
                ),
            )
        )
    return corrected, violations


_STOPWORDS = frozenset(
    """a an and are as at be by for from has have in into is it its of on or that the their
    this to with was were will would across both end both""".split()
)


def _content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9+#.]+", text.casefold())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def check_provenance(
    claims: list[Claim], master_html: str, *, min_shared_words: int = 2
) -> list[Violation]:
    """C9 (AF-08, T-5) — every `self` claim resolves to a line of *this* master.

    Three ways to fail, and they are different failures:
      * no pointer at all — the claim is unsupported by construction;
      * a pointer this master does not contain — stale, and after C-8 it fails
        loudly here rather than resolving to whatever now occupies that key;
      * a pointer that resolves but shares almost nothing with the claim — aimed
        at the wrong line.
    """
    violations: list[Violation] = []

    for claim in claims:
        if claim.kind != "self":
            continue

        if not claim.provenance:
            violations.append(
                Violation(
                    check="C9",
                    claim_text=claim.text,
                    detail="claim about the candidate carries no provenance pointer",
                )
            )
            continue

        claim_words = _content_words(claim.text)
        supported = False
        unresolved: list[str] = []

        for key in claim.provenance:
            try:
                source = element_text(master_html, key)
            except KeyError:
                unresolved.append(key)
                continue
            source_words = _content_words(source)
            # Two shared words, OR the whole source appears in the claim. The second
            # rule is what lets a claim point at a single skill value: "Built retrieval
            # pipelines on Qdrant" -> `skills.s3.qdrant` shares exactly one word, and
            # requiring two would make every technology pointer unusable.
            if len(claim_words & source_words) >= min_shared_words or (
                source_words and source_words <= claim_words
            ):
                supported = True
                break

        if unresolved and not supported:
            violations.append(
                Violation(
                    check="C9",
                    claim_text=claim.text,
                    detail=(
                        f"provenance {unresolved!r} does not exist in this master "
                        "(master_hash mismatch, or the pointer is stale)"
                    ),
                )
            )
        elif not supported:
            violations.append(
                Violation(
                    check="C9",
                    claim_text=claim.text,
                    detail=(
                        f"provenance {claim.provenance!r} resolves but shares fewer than "
                        f"{min_shared_words} content words with the claim"
                    ),
                )
            )

    return violations


def _mentioned_technologies(text: str, vocabulary: frozenset[str]) -> list[str]:
    """Find vocabulary terms in the text, longest first so `AWS Bedrock` wins over `AWS`."""
    found: list[str] = []
    consumed: list[tuple[int, int]] = []

    for term in sorted(vocabulary, key=len, reverse=True):
        for match in re.finditer(rf"(?<![\w.]){re.escape(term)}(?![\w.])", text, re.IGNORECASE):
            span = match.span()
            if any(span[0] < end and start < span[1] for start, end in consumed):
                continue  # already covered by a longer term
            consumed.append(span)
            found.append(term)

    return found


def check_technologies(
    claims: list[Claim],
    ledger: Ledger,
    *,
    synonyms: dict[str, str] | None = None,
    vocabulary: frozenset[str] = DEFAULT_TECH_VOCABULARY,
) -> list[Violation]:
    """C4 (AF-03) — every technology named must be one the master actually carries.

    `company` claims are exempt: describing the employer's Azure platform is a fact
    about them, not a claim about the candidate. That exemption is why C11 checks
    company claims against a JD span fetched this run.
    """
    synonyms = {**ledger.synonyms, **(synonyms or {})}
    allowed = {t.casefold() for t in ledger.technologies}
    allowed |= {canonical.casefold() for canonical in synonyms.values()}
    allowed |= {alias.casefold() for alias in synonyms}

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "company":
            continue
        for term in _mentioned_technologies(claim.text, vocabulary):
            if term.casefold() not in allowed:
                violations.append(
                    Violation(
                        check="C4",
                        claim_text=claim.text,
                        detail=(
                            f"{term!r} is not in the master's skill vocabulary; "
                            "the resume does not support describing it as the candidate's"
                        ),
                    )
                )
    return violations


class FactGuardResult(BaseModel):
    """The verdict on one artefact set, plus the confirmations waiving part of it."""

    violations: list[Violation] = Field(default_factory=list)
    confirmed_ids: frozenset[str] = frozenset()

    model_config = {"frozen": True}

    @property
    def outstanding(self) -> list[Violation]:
        return [v for v in self.violations if v.violation_id not in self.confirmed_ids]

    @property
    def status(self) -> Literal["pass", "fail", "pass_with_confirmed_edits"]:
        if self.outstanding:
            return "fail"
        return "pass_with_confirmed_edits" if self.confirmed_ids else "pass"

    def confirm(self, confirmation: Confirmation) -> FactGuardResult:
        """Record one per-violation confirmation (M-16).

        Refuses two things v1 allowed: waiving a class that is not a matter of
        authorship, and satisfying the prompt with a remembered constant.
        """
        by_id = {v.violation_id: v for v in self.violations}
        violation = by_id.get(confirmation.violation_id)
        if violation is None:
            raise KeyError(f"no violation {confirmation.violation_id!r} in this result")

        if not violation.overridable:
            raise NotOverridable(
                f"{violation.check} is not a matter of authorship; a confirmation cannot "
                f"waive it. {violation.detail}"
            )

        if confirmation.typed_text.strip() != violation.confirmation_prompt:
            raise ValueError(
                "confirmation text must match the generated prompt exactly; "
                "a remembered phrase does not confirm a specific claim"
            )

        return self.model_copy(
            update={"confirmed_ids": self.confirmed_ids | {violation.violation_id}}
        )


def run_factguard(
    claims: list[Claim],
    master_html: str,
    ledger: Ledger,
    *,
    synonyms: dict[str, str] | None = None,
    max_context: int = 2,
    target_company: str | None = None,
    years_by_technology: dict[str, int] | None = None,
    mandatory: list[str] | None = None,
    max_words: int | None = None,
    today: date | None = None,
) -> FactGuardResult:
    """Run the deterministic checks in the order §8.1 fixes.

    C14 runs before C9 deliberately: reclassifying a `context` claim to `self` is
    what forces it to produce a pointer, so doing it afterwards would let exactly
    the C-6 escape hatch through.
    """
    corrected, violations = check_claim_kind(claims, max_context=max_context)
    violations = list(violations)
    violations += check_numbers(corrected, ledger)
    violations += check_technologies(corrected, ledger, synonyms=synonyms)
    violations += check_organisations(corrected, ledger, target_company=target_company)
    violations += check_degrees(corrected, ledger)
    violations += check_years(
        corrected, ledger,
        years_by_technology=years_by_technology or {},
        today=today or date.today(),
    )
    violations += check_scope_verbs(corrected, ledger, master_html)
    violations += check_provenance(corrected, master_html)
    violations += check_filler(corrected, max_words=max_words)
    if mandatory:
        violations += check_mandatory_gap(corrected, ledger, mandatory=mandatory)
    return FactGuardResult(violations=violations)


_QUALIFIER_ALT = "|".join(re.escape(q) for q in _LEADING_QUALIFIERS_TEXT)
_NUMERAL_IN_TEXT = re.compile(
    rf"(?:(?P<qual>{_QUALIFIER_ALT})\s+)?(?P<num>\d[\d,]*(?:\.\d+)?\s*%?)(?P<plus>\+)?",
    re.IGNORECASE,
)


def _numerals_in(text: str) -> list[tuple[str, str | None, tuple[int, int]]]:
    """Pull (value, qualifier, span) triples out of free text, mirroring the ledger."""
    found: list[tuple[str, str | None, tuple[int, int]]] = []
    for m in _NUMERAL_IN_TEXT.finditer(text):
        value = m.group("num").replace(" ", "")
        qualifier = m.group("qual").lower() if m.group("qual") else None
        if m.group("plus"):
            qualifier = f"{qualifier} +".strip() if qualifier else "+"
        found.append((value, qualifier, m.span()))
    return found


def check_numbers(claims: list[Claim], ledger: Ledger) -> list[Violation]:
    """C3 (AF-02, AF-07) — every numeral must match a ledger number *and its qualifier*.

    The qualifier half is the part that matters in practice. A tailored sentence that
    turns "up to 80%" into "80%" has not invented a number; it has quietly promoted a
    ceiling into an achievement, which is the same lie in a form that survives a
    careless read.
    """
    allowed = {(n.value.replace(" ", ""), n.qualifier) for n in ledger.numbers}
    allowed_values = {value for value, _ in allowed}
    # A numeral attached to "years" is an experience claim, which C7 owns and judges
    # against the resume dates and the years_by_technology table. Flagging it here too
    # would report one fabrication as two, and send the repair loop to the wrong check.
    years_numeral = re.compile(
        r"\d[\d,.]*\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE
    )

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "context":
            continue  # letter dates and salutations assert nothing about the candidate
        years_spans = [m.span() for m in years_numeral.finditer(claim.text)]
        for value, qualifier, span in _numerals_in(claim.text):
            if any(a <= span[0] < b for a, b in years_spans):
                continue
            if (value, qualifier) in allowed:
                continue
            if value in allowed_values:
                supported = sorted(
                    {q or "(none)" for v, q in allowed if v == value}
                )
                violations.append(
                    Violation(
                        check="C3",
                        claim_text=claim.text,
                        detail=(
                            f"{value!r} appears in the master only with qualifier "
                            f"{', '.join(supported)} — dropping or changing the qualifier "
                            "makes a stronger claim than the resume supports"
                        ),
                    )
                )
            else:
                violations.append(
                    Violation(
                        check="C3",
                        claim_text=claim.text,
                        detail=f"{value!r} does not appear in the master",
                    )
                )
    return violations


# ============================== C5 — organisations and projects ==============
_ORG_HINT = re.compile(
    r"\b(?:at|with|for|joined|from)\s+([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*)*)", re.UNICODE
)


def check_organisations(
    claims: list[Claim], ledger: Ledger, *, target_company: str | None = None
) -> list[Violation]:
    """C5 (AF-04) — no employer the master does not name, except the one being applied to.

    Inventing a former employer is the most consequential lie on a resume and the
    easiest to check, so the allowlist is closed: the organisations the ledger found,
    plus the target company, plus technologies and projects (a tool is not an employer).
    """
    allowed = {o.casefold() for o in ledger.organisations}
    allowed |= {t.casefold() for t in ledger.technologies}
    allowed |= {p.casefold() for p in ledger.projects}
    if target_company:
        allowed.add(target_company.casefold())

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "company":
            continue
        for match in _ORG_HINT.finditer(claim.text):
            name = match.group(1).strip().rstrip(".,")
            if not name or name.casefold() in allowed:
                continue
            if " " not in name and match.start(1) == 0:
                continue
            violations.append(
                Violation(
                    check="C5",
                    claim_text=claim.text,
                    detail=f"{name!r} is not an organisation the master names",
                )
            )
    return violations


# ============================== C6 — degrees and certifications ==============
_CERT_PATTERN = re.compile(
    r"\b(certified|certification|certificate|ph\.?d|doctorate|doctoral|"
    r"m\.?tech|mba|pmp|cissp)\b",
    re.IGNORECASE,
)
_DENIAL = re.compile(r"\b(no|not|without|lack|lacks|never)\b", re.IGNORECASE)


def check_degrees(claims: list[Claim], ledger: Ledger) -> list[Violation]:
    """C6 (AF-13) — the ledger carries one degree and no certifications.

    Any self-descriptive certification language is therefore fabrication by
    definition. A sentence that denies holding one is not a claim to hold it.
    """
    held = " ".join(f.value.casefold() for f in ledger.facts if f.klass == "degree_cert")

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "company":
            continue
        for match in _CERT_PATTERN.finditer(claim.text):
            token = match.group(0)
            if token.casefold() in held:
                continue
            window = claim.text[max(0, match.start() - 40) : match.start()]
            if _DENIAL.search(window):
                continue
            violations.append(
                Violation(
                    check="C6",
                    claim_text=claim.text,
                    detail=(
                        f"{token!r} is a qualification the master does not carry "
                        "(the ledger holds one degree and no certifications)"
                    ),
                )
            )
    return violations


# ============================== C7 — years ===================================
_CAREER_START = date(2022, 8, 1)          # from exp.*.meta; the only dated role
_TOTAL_YEARS = re.compile(r"(\d+)\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)
_TECH_YEARS = re.compile(
    r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+|with\s+|in\s+|using\s+)([A-Za-z][\w+.# ]{1,30})",
    re.IGNORECASE,
)


def check_years(
    claims: list[Claim],
    ledger: Ledger,
    *,
    years_by_technology: dict[str, int],
    today: date,
) -> list[Violation]:
    """C7 (AF-10, AF-11) — no number about experience is ever generated.

    Total years is computed from the resume dates. Per-technology years come only
    from the table the owner filled in; absent an entry the answer is a halt, never
    an interpolation (T-4, D-7). AC-AF-19's worked example, "5 years with LangChain",
    is exactly this check, and v1's override flow would have shipped it (M-16).
    """
    supportable = (today - _CAREER_START).days // 365 + 1
    table = {k.casefold(): v for k, v in years_by_technology.items()}

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "company":
            continue

        tech_spans: list[tuple[int, int]] = []
        for match in _TECH_YEARS.finditer(claim.text):
            tech_spans.append(match.span())
            claimed, tech = int(match.group(1)), match.group(2).strip().rstrip(".,")
            known = table.get(tech.casefold())
            if known is None:
                violations.append(
                    Violation(
                        check="C7",
                        claim_text=claim.text,
                        detail=(
                            f"no years_by_technology entry for {tech!r}; the system halts "
                            "rather than estimating a figure"
                        ),
                    )
                )
            elif claimed != known:
                violations.append(
                    Violation(
                        check="C7",
                        claim_text=claim.text,
                        detail=f"{claimed} years with {tech!r}; the table says {known}",
                    )
                )

        for match in _TOTAL_YEARS.finditer(claim.text):
            if any(a <= match.start() < b for a, b in tech_spans):
                continue
            if int(match.group(1)) > supportable:
                violations.append(
                    Violation(
                        check="C7",
                        claim_text=claim.text,
                        detail=(
                            f"{match.group(1)} years exceeds what the resume dates support "
                            f"({supportable} as of {today})"
                        ),
                    )
                )
    return violations


# ============================== C8 — scope verbs =============================
def check_scope_verbs(claims: list[Claim], ledger: Ledger, master_html: str) -> list[Violation]:
    """C8 (AF-09) — a rewording may not promote the verb.

    The source says "Mentor 4 engineers". "Managed a team of 4" is a larger claim
    about the same fact, and it is the kind of inflation that survives a casual read.
    """
    ranks = {k.casefold(): v for k, v in ledger.scope_verbs.items()}
    if not ranks:
        return []
    pattern = re.compile(rf"\b({'|'.join(map(re.escape, ranks))})\b", re.IGNORECASE)

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind != "self" or not claim.provenance:
            continue
        claimed = max(
            (ranks[m.group(1).casefold()] for m in pattern.finditer(claim.text)), default=0
        )
        if not claimed:
            continue

        source_rank = 0
        for key in claim.provenance:
            try:
                source = element_text(master_html, key)
            except KeyError:
                continue
            source_rank = max(
                source_rank,
                max((ranks[m.group(1).casefold()] for m in pattern.finditer(source)), default=0),
            )

        if claimed > source_rank:
            violations.append(
                Violation(
                    check="C8",
                    claim_text=claim.text,
                    detail=(
                        f"verb scope {claimed} exceeds the source's {source_rank}; "
                        "a rewording may narrow a claim but never widen it"
                    ),
                )
            )
    return violations


# ============================== C12 — filler and caps ========================
DEFAULT_BANNED_PHRASES: tuple[str, ...] = (
    "results-driven", "team player", "proven track record", "think outside the box",
    "hit the ground running", "go-getter", "synergy", "dynamic professional",
    "detail-oriented", "self-starter", "value add", "wealth of experience",
)


def check_filler(
    claims: list[Claim],
    *,
    max_words: int | None = None,
    banned: tuple[str, ...] = DEFAULT_BANNED_PHRASES,
) -> list[Violation]:
    """C12 (CL-01, CL-02) — the phrases that make every cover letter the same one."""
    violations: list[Violation] = []
    for claim in claims:
        lowered = claim.text.casefold()
        for phrase in banned:
            if phrase in lowered:
                violations.append(
                    Violation(
                        check="C12",
                        claim_text=claim.text,
                        detail=f"banned filler phrase {phrase!r}",
                    )
                )

    if max_words is not None:
        total = sum(len(c.text.split()) for c in claims)
        if total > max_words:
            violations.append(
                Violation(
                    check="C12",
                    claim_text=f"{total} words",
                    detail=f"{total} words exceeds the cap of {max_words}",
                )
            )
    return violations


# ============================== C13 — mandatory-gap claims ===================
_MANDATORY_STOPWORDS = frozenset(
    {"the", "and", "with", "for", "in", "of", "years", "experience", "strong", "plus"}
)


def check_mandatory_gap(
    claims: list[Claim], ledger: Ledger, *, mandatory: list[str]
) -> list[Violation]:
    """C13 (AF-12, T-3) — never present a qualification you lack as one you hold.

    Pre-flight #12 recomputes this independently of `fact_checks.status`, so a
    confirmed edit cannot ship it. A sentence that acknowledges the gap is fine:
    honesty about a requirement is not a claim to meet it.
    """
    held = " ".join(
        f.value.casefold() for f in ledger.facts if f.klass in ("degree_cert", "technology")
    )

    # Only credential words and technology names are evidence of a CLAIM to hold the
    # qualification. v1 tokenised the whole requirement, so "AWS Certified Solutions
    # Architect" put "Solutions" on the watch list and flagged "enterprise AI automation
    # solutions" - an ordinary sentence from the resume itself. A check that fires on
    # true statements trains the reviewer to click through violations, which is the one
    # habit this design cannot afford.
    tokens: set[str] = set()
    for requirement in mandatory:
        for word in re.findall(r"[A-Za-z.+#]{3,}", requirement):
            folded = word.casefold()
            if folded in _MANDATORY_STOPWORDS:
                continue
            is_credential = _CERT_PATTERN.fullmatch(word) is not None
            is_technology = any(
                word.casefold() == t.casefold() for t in DEFAULT_TECH_VOCABULARY
            )
            if is_credential or is_technology:
                tokens.add(word)

    violations: list[Violation] = []
    for claim in claims:
        if claim.kind == "company":
            continue
        for token in sorted(tokens):
            if token.casefold() in held:
                continue
            match = re.search(rf"\b{re.escape(token)}\b", claim.text, re.IGNORECASE)
            if not match:
                continue
            if _DENIAL.search(claim.text[: match.start()]):
                continue
            violations.append(
                Violation(
                    check="C13",
                    claim_text=claim.text,
                    detail=(
                        f"{token!r} is a mandatory qualification the master does not carry, "
                        "and this sentence presents it as held"
                    ),
                )
            )
            break
    return violations

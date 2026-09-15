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
from typing import Literal

from pydantic import BaseModel, Field

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
        digest = hashlib.sha256(f"{self.check}|{self.claim_text}|{self.detail}".encode()).hexdigest()
        return digest[:16]

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
    return {w for w in re.findall(r"[a-z0-9+#.]+", text.casefold()) if w not in _STOPWORDS and len(w) > 2}


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
            if len(claim_words & _content_words(source)) >= min_shared_words:
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
    synonyms = synonyms or {}
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
) -> FactGuardResult:
    """Run the deterministic checks in the order §8.1 fixes.

    C14 runs before C9 deliberately: reclassifying a `context` claim to `self` is
    what forces it to produce a pointer, so doing it afterwards would let exactly
    the C-6 escape hatch through.
    """
    corrected, violations = check_claim_kind(claims, max_context=max_context)
    violations = list(violations)
    violations += check_technologies(corrected, ledger, synonyms=synonyms)
    violations += check_provenance(corrected, master_html)
    return FactGuardResult(violations=violations)

"""The mutation suite — AC-AF-15 and AC-AF-16 (SPEC §8.4).

"Testing the verifier harder than the generator." 40 seeded fabrications must every
one be flagged with the correct check, or the build fails; and 10 legitimate
tailorings plus the unmodified master must produce zero flags.

Two of the 40 are claim-kind mutations rather than fact-class ones (C-6): v1's suite
was organised purely by fact class, which is exactly why it could not have caught a
`self` claim relabelled `context`.
"""

from datetime import date
from pathlib import Path

import pytest

from jobagent.factguard import Claim, run_factguard
from jobagent.ledger import build_ledger

MASTER_PATH = Path(__file__).resolve().parents[2] / "resume" / "resume-ats.html"
TODAY = date(2026, 9, 30)
YEARS_TABLE = {"LangChain": 3, "Python": 4}
MANDATORY = ["PhD in Machine Learning", "AWS Certified Solutions Architect"]

# A real bullet from the master, used as a valid pointer for mutations that need one.
SRC = "exp.krista-software.li1"
MENTOR_SRC = "exp.krista-software.li4"


def _claim(text, kind="self", prov=(SRC,)):
    return Claim(text=text, kind=kind, provenance=list(prov))


#: (id, claim, expected check). Each must be flagged, and flagged as that class.
MUTATIONS: list[tuple[str, Claim, str]] = [
    # ---- C3 numbers -------------------------------------------------------
    ("num-invented", _claim("Delivered 97 enterprise integrations"), "C3"),
    ("num-inflated", _claim("Architected 250+ enterprise AI solutions"), "C3"),
    ("num-qualifier-dropped", _claim("Cut manual effort by 80%"), "C3"),
    ("num-team-size", _claim("Mentored 40 engineers", prov=(MENTOR_SRC,)), "C3"),
    # ---- C4 technologies --------------------------------------------------
    ("tech-canary-azure", _claim("Built the platform on Azure"), "C4"),
    ("tech-canary-spark", _claim("Processed the corpus with Spark"), "C4"),
    ("tech-canary-tensorflow", _claim("Trained models in TensorFlow"), "C4"),
    ("tech-canary-milvus", _claim("Indexed embeddings in Milvus"), "C4"),
    ("tech-adjacent-weaviate", _claim("Ran Weaviate for hybrid retrieval"), "C4"),
    # ---- C5 organisations -------------------------------------------------
    ("org-invented-employer", _claim("While at Infosys Limited I led delivery"), "C5"),
    ("org-invented-client", _claim("Shipped a platform for Goldman Sachs"), "C5"),
    ("org-plausible-startup", _claim("I built retrieval systems at Scale AI"), "C5"),
    # ---- C6 degrees and certifications ------------------------------------
    ("cert-phd", _claim("My PhD work informs how I design retrieval"), "C6"),
    ("cert-aws", _claim("I am AWS certified for solution architecture"), "C6"),
    ("cert-mba", _claim("An MBA taught me to speak to buyers"), "C6"),
    ("cert-generic", _claim("I hold a certification in enterprise AI"), "C6"),
    # ---- C7 years ---------------------------------------------------------
    ("years-total-inflated", _claim("9 years of experience in AI engineering"), "C7"),
    ("years-total-slightly-over", _claim("7 years building production systems"), "C7"),
    ("years-tech-wrong", _claim("6 years with LangChain"), "C7"),
    ("years-tech-untabled", _claim("4 years with Qdrant"), "C7"),
    # ---- C8 scope verbs ---------------------------------------------------
    ("scope-managed", _claim("Managed four engineers", prov=(MENTOR_SRC,)), "C8"),
    ("scope-headed", _claim("Headed AI solution delivery", prov=(MENTOR_SRC,)), "C8"),
    ("scope-founded", _claim("Founded the AI practice", prov=(MENTOR_SRC,)), "C8"),
    # ---- C9 provenance ----------------------------------------------------
    ("prov-absent", _claim("Owned architecture for enterprise customers", prov=()), "C9"),
    ("prov-stale-key", _claim("Architected enterprise AI automation",
                              prov=("exp.acme.li7",)), "C9"),
    ("prov-wrong-line", _claim("Designed the typography of the brand system",
                               prov=(SRC,)), "C9"),
    # ---- C12 filler -------------------------------------------------------
    ("filler-results-driven", _claim("A results-driven engineer"), "C12"),
    ("filler-team-player", _claim("I am a team player above all"), "C12"),
    ("filler-track-record", _claim("I bring a proven track record"), "C12"),
    ("filler-self-starter", _claim("A self-starter who needs no direction"), "C12"),
    # ---- C13 mandatory gaps ----------------------------------------------
    ("mand-phd-implied", _claim("My doctoral research is directly relevant"), "C6"),
    ("mand-aws-implied", _claim("Certified on AWS Solutions Architecture"), "C6"),
    # ---- C14 claim kind (the C-6 shape v1's suite could not catch) ---------
    ("kind-relabelled-self", Claim(
        text="I have shipped agentic systems that enterprise buyers trust",
        kind="context"), "C9"),
    ("kind-implied-subject", Claim(
        text="Owned delivery from discovery through production support",
        kind="context"), "C9"),
    # ---- mixed / adversarial ---------------------------------------------
    ("mixed-number-and-tech", _claim("Ran 12 Kafka clusters"), "C4"),
    ("mixed-years-and-cert", _claim("8 years and a PhD in the field"), "C7"),
    ("subtle-scope-creep", _claim("Led the engineering organisation",
                                  prov=(MENTOR_SRC,)), "C8"),
    ("subtle-org-possessive", _claim("Delivered work for Accenture clients"), "C5"),
    ("subtle-invented-metric", _claim("Improved latency by 43%"), "C3"),
    ("subtle-tech-in-passing",
     _claim("Comfortable with Terraform and infrastructure as code"), "C4"),
]

#: AC-AF-16 — legitimate tailorings that must produce zero flags.
LEGITIMATE: list[Claim] = [
    _claim("Architected enterprise AI automation solutions integrating LLMs"),
    _claim("Integrated LLMs with third-party enterprise systems"),
    _claim("Reduced manual workflows by up to 80%", prov=(SRC,)),
    _claim("Architected 25+ enterprise AI automation solutions", prov=(SRC,)),
    _claim("Mentor engineers across AI solution delivery", prov=(MENTOR_SRC,)),
    _claim("3 years with LangChain", prov=("skills.s2.langchain",)),
    _claim("Built retrieval pipelines on Qdrant", prov=("skills.s3.qdrant",)),
    Claim(text="Dear Hiring Manager,", kind="context"),
    Claim(text="Thank you for your consideration.", kind="context"),
    Claim(text="Acme's published work on agent evaluation is why I am writing",
          kind="company", provenance=["jd:0-40"]),
]


@pytest.fixture(scope="module")
def master() -> str:
    return MASTER_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(master):
    return build_ledger(master)


def _run(claims, master, ledger):
    return run_factguard(
        claims, master, ledger,
        target_company="Acme",
        years_by_technology=YEARS_TABLE,
        mandatory=MANDATORY,
        today=TODAY,
    )


def test_the_suite_has_the_forty_mutations_the_ac_requires():
    assert len(MUTATIONS) == 40, f"suite has {len(MUTATIONS)}"


@pytest.mark.parametrize("mid,claim,expected", MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_every_seeded_fabrication_is_flagged(mid, claim, expected, master, ledger):
    """AC-AF-15: 40/40 or the build fails. Flagged with the RIGHT check, because a
    violation attributed to the wrong class sends the repair loop somewhere useless."""
    result = _run([claim], master, ledger)

    assert result.status == "fail", f"{mid} passed unflagged"
    assert expected in {v.check for v in result.violations}, (
        f"{mid} expected {expected}, got {sorted({v.check for v in result.violations})}"
    )


def test_legitimate_tailorings_produce_no_flags(master, ledger):
    """AC-AF-16. False positives are not a safe failure here: they train the reviewer
    to click through violations, which is the one habit this design cannot afford."""
    result = _run(LEGITIMATE, master, ledger)

    assert result.status == "pass", "; ".join(
        f"{v.check}: {v.claim_text[:60]} -> {v.detail[:90]}" for v in result.violations
    )


def test_the_unmodified_master_passes_its_own_verifier(master, ledger):
    """The resume as written must not violate the rules derived from it."""
    claims = [
        Claim(text=f.value, kind="self", provenance=[f.element_key])
        for f in ledger.facts
        if f.klass == "achievement"
    ]

    result = _run(claims, master, ledger)

    assert result.status == "pass", "; ".join(
        f"{v.check}: {v.detail[:100]}" for v in result.violations[:6]
    )

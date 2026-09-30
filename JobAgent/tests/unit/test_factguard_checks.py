"""The remaining deterministic FactGuard checks (SPEC §8.2): C5-C8, C12, C13."""

from datetime import date

from jobagent.factguard import (
    Claim,
    check_degrees,
    check_filler,
    check_mandatory_gap,
    check_organisations,
    check_scope_verbs,
    check_years,
)
from jobagent.ledger import build_ledger

MASTER = """
<h3 id="exp.krista-software.h3">Krista Software (AI Automation Startup) - Pune, India</h3>
<div class="meta" id="exp.krista-software.meta">Senior AI Solution Engineer
 | Aug 2022 - Present</div>
<ul>
  <li id="exp.krista-software.li2">Lead engineer on two flagship platform initiatives.</li>
  <li id="exp.krista-software.li4">Mentor 4 engineers across AI solution delivery.</li>
</ul>
<h3 id="proj.enterprise-rag.h3">Enterprise RAG Platform (AIQA)</h3>
<p id="edu.p1">B.Tech, Computer Science &amp; Engineering
 - MIT Academy of Engineering (MITAOE), Pune</p>
<div class="skill" id="skills.s1">
  <b id="skills.s1.label">GenAI</b>
  <span class="v" id="skills.s1.langchain">LangChain</span>
</div>
"""


def _ledger():
    return build_ledger(MASTER)


# ---------------------------------------------------------------- C5
def test_an_employer_the_resume_never_names_is_a_violation():
    """C5/AF-04: inventing a former employer is the most consequential resume
    lie there is, and the easiest for a recruiter to check."""
    claims = [Claim(text="While at Infosys I built retrieval systems", kind="self")]

    violations = check_organisations(claims, _ledger(), target_company="Acme")

    assert [v.check for v in violations] == ["C5"]


def test_the_target_company_may_be_named():
    """Naming the employer is the point of a cover letter."""
    claims = [Claim(text="Acme's platform work is why I am applying", kind="self")]

    assert check_organisations(claims, _ledger(), target_company="Acme") == []


# ---------------------------------------------------------------- C6
def test_claiming_a_certification_the_resume_does_not_carry_fails():
    """C6/AF-13: the ledger has no certifications beyond the B.Tech, so any
    self-descriptive certification language is fabrication by definition."""
    claims = [Claim(text="I am an AWS Certified Solutions Architect", kind="self")]

    violations = check_degrees(claims, _ledger())

    assert [v.check for v in violations] == ["C6"]


def test_the_degree_the_resume_does_carry_is_fine():
    claims = [Claim(text="B.Tech in Computer Science and Engineering", kind="self")]

    assert check_degrees(claims, _ledger()) == []


# ---------------------------------------------------------------- C7
def test_total_years_may_not_exceed_what_the_dates_support():
    """C7/AF-10. Employment began Aug 2022, so on 2026-09-30 anything past 5 is
    invented — and years of experience is the first number a recruiter checks."""
    claims = [Claim(text="8 years of experience in AI engineering", kind="self")]

    violations = check_years(claims, _ledger(), years_by_technology={}, today=date(2026, 9, 30))

    assert [v.check for v in violations] == ["C7"]


def test_a_supportable_total_passes():
    claims = [Claim(text="4+ years building production AI systems", kind="self")]

    assert check_years(claims, _ledger(), years_by_technology={},
                       today=date(2026, 9, 30)) == []


def test_years_with_a_named_technology_must_match_the_table_exactly():
    """AC-AF-19's own worked example — "5 years with LangChain" — is a C7 violation,
    and v1's confirmation flow would have shipped it (M-16)."""
    claims = [Claim(text="5 years with LangChain", kind="self")]

    violations = check_years(claims, _ledger(), years_by_technology={"LangChain": 3},
                             today=date(2026, 9, 30))

    assert [v.check for v in violations] == ["C7"]
    assert "3" in violations[0].detail


def test_years_with_a_technology_absent_from_the_table_fails_rather_than_guesses():
    """T-4: absent an entry the system halts. It never interpolates a number."""
    claims = [Claim(text="3 years with Qdrant", kind="self")]

    violations = check_years(claims, _ledger(), years_by_technology={},
                             today=date(2026, 9, 30))

    assert [v.check for v in violations] == ["C7"]


# ---------------------------------------------------------------- C8
def test_a_reworded_claim_may_not_promote_the_verb_scope():
    """C8/AF-09: the source says "Mentor 4 engineers". "Managed a team of 4" is a
    different and larger claim."""
    claims = [Claim(text="Managed a team of 4 engineers", kind="self",
                    provenance=["exp.krista-software.li4"])]

    violations = check_scope_verbs(claims, _ledger(), MASTER)

    assert [v.check for v in violations] == ["C8"]


def test_keeping_the_source_verb_passes():
    claims = [Claim(text="Mentored 4 engineers across AI delivery", kind="self",
                    provenance=["exp.krista-software.li4"])]

    assert check_scope_verbs(claims, _ledger(), MASTER) == []


# ---------------------------------------------------------------- C12
def test_banned_filler_is_a_violation():
    """C12/CL-01: the phrases that make a cover letter read like every other one."""
    claims = [Claim(text="I am a results-driven team player with a proven track record",
                    kind="self")]

    violations = check_filler(claims)

    assert violations and violations[0].check == "C12"


def test_a_letter_over_the_word_cap_is_a_violation():
    claims = [Claim(text=" ".join(["word"] * 320), kind="self")]

    violations = check_filler(claims, max_words=300)

    assert any("300" in v.detail for v in violations)


# ---------------------------------------------------------------- C13
def test_presenting_a_missing_mandatory_qualification_as_held_fails():
    """C13/AF-12/T-3: the job demands a PhD, the candidate has none, and the letter
    must not imply otherwise. Pre-flight #12 recomputes this independently."""
    claims = [Claim(text="My PhD research prepared me for this role", kind="self")]

    violations = check_mandatory_gap(claims, _ledger(), mandatory=["PhD in Machine Learning"])

    assert [v.check for v in violations] == ["C13"]


def test_acknowledging_the_gap_is_not_a_violation():
    """Saying you lack it is honest; the check is about presenting it as held."""
    claims = [Claim(text="I do not hold a PhD, though I have shipped research systems",
                    kind="self")]

    assert check_mandatory_gap(claims, _ledger(), mandatory=["PhD in Machine Learning"]) == []

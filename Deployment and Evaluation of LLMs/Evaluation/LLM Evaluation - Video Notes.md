# LLM Evaluation — Video Notes

Condensed, transcript-based notes from a TMLC Academy session on evaluating LLMs and LLM systems. See *LLM Evaluation - Transcript.md* in this folder for the full source recording transcript, and *LLM Evaluation.pdf* for the companion reading.

**Where this sits in the course:** you've already met evaluation twice — evaluating an OpenAI model back in Week 1, and RAGAS for RAG evaluation in Week 3. Both answered *"how good is this specific thing I built?"* This session widens the lens: **what can be evaluated at all**, what the approaches are, and which libraries actually do the work.

**The core idea, in one line:**

> An LLM doesn't fail like normal software. Normal software throws an error. An LLM returns a confident, fluent, well-formatted paragraph that happens to be wrong — and *nothing in the system notices*. Evaluation is the machinery you build so that something notices.

**The analogy that runs through this whole document 🎓**

Think of evaluating an LLM like **assessing a student**. A *benchmark* is a standardized exam — comparable across everyone, but easy to cram for. *Human evaluation* is a teacher reading the actual essay — expensive, slow, and the only thing that catches "technically correct but misses the point." *LLM-as-judge* is having a senior student grade the juniors — fast and scalable, but they carry their own blind spots. *Adversarial testing* is the trick question designed to catch someone who memorized without understanding. No single one of these tells you whether the student can actually do the job — which is exactly why this session walks through six approaches rather than one.

---

## 1. Why Evaluate — and the Guardrails Distinction

The session opens with five reasons evaluation matters:

1. **Accuracy** — is the response actually right?
2. **Bias** — what prejudices did the training data bake in?
3. **Efficiency** — does it answer fast enough to be usable?
4. **Hallucination** — especially in RAG, where the model can invent things the retrieved context never said.
5. **Ethical/compliance considerations** — including the very real problem of employees pasting organizational data into a third-party model.

Then comes a distinction that's worth getting exactly right, because it's a common interview question:

**Evaluation and guardrails are not the same thing, and they happen at different times.**

```
        BEFORE deployment                    AFTER deployment
    ┌─────────────────────┐            ┌─────────────────────┐
    │     EVALUATION      │            │     GUARDRAILS      │
    │                     │            │                     │
    │  "Is this model     │  ───────►  │  "Catch the cases   │
    │   good enough       │            │   where it's        │
    │   to ship?"         │            │   still wrong."     │
    │                     │            │                     │
    │  Result: a score    │            │  Result: a block,   │
    │  e.g. 82% accurate  │            │  rewrite, or refusal│
    └─────────────────────┘            └─────────────────────┘
```

> 🚦 **The session's own framing:** you evaluate, and the model comes out 82% accurate. Great — but what about the other 18%? You can't evaluate your way out of that. **Guardrails are what you put in front of the remaining 18% at runtime.** Evaluation measures; guardrails intervene.

**Example:** you evaluate a customer-support bot and find it's rude 4% of the time. Evaluation gave you that number. A guardrail is the runtime check that scans each outgoing message for hostile tone and rewrites it before the customer ever sees it.

**One line:** evaluation is a pre-launch measurement that produces a score; guardrails are a live safety net that produces an intervention — you need both, and conflating them is a classic interview stumble.

---

## 2. What You Can Actually Evaluate

Most people think "evaluation" means accuracy. The session lists seven dimensions, and accuracy is only one:

| Dimension | The question it asks | Concrete example from the session |
|---|---|---|
| **Language understanding** | Does it work in *this* language, not just English? | Gemma 2B beat Llama 3 on non-English tasks while losing on English — no model is uniformly best across languages |
| **Creativity** | Is the creative output actually good, or just weird? | It can write jokes — but are the jokes *lame*? |
| **Accuracy** | Is the fact right? | Asked for the 2023 World Cup result, it shouldn't answer about 2019 |
| **Consistency** | Same question twice → same substance? | Re-asking often makes a model assume you wanted something *different* and drift |
| **Efficiency** | Is it fast enough to be usable? | 30s–2min response time means users leave, regardless of answer quality |
| **Ethical alignment** | Does it match *your organization's* rules? | A company that ships a Python library may not want its bot recommending competitor libraries |
| **Harmfulness** | Does it produce offensive or unsafe content? | Assessed largely by human reviewers |

> 💡 **The consistency nuance worth remembering:** consistency does *not* mean identical wording. Tone, structure, and phrasing can vary freely — what must stay stable is **the substance of the answer**. A model that says "Paris" one time and "the capital is Paris, a city of 2.1 million" the next is consistent. One that says "Paris" then "Lyon" is not.

> ⚠️ **On organizational alignment:** the session is honest that this one is hard to *train* for — competitors keep appearing, and you can't fine-tune against a list that changes weekly. **This is a case where a guardrail beats evaluation**, because the rule is a moving target.

---

## 3. Six Approaches to Evaluating an LLM

### 3.1 Benchmarks — the standardized exam

Every model release claims "X% better than GPT-4." That comparison runs on **benchmarks**: large, public question-answer datasets everyone tests against.

| Benchmark | What it tests |
|---|---|
| **MMLU** (Massive Multitask Language Understanding) | Breadth across many subjects — a good MMLU score means *generalist*, not domain specialist |
| **HellaSwag** | Commonsense reasoning |
| **TruthfulQA** | Whether answers are *truthful*, not just plausible |
| **GPQA** | PhD-level multiple-choice science questions |

**Why they exist:** comparison is only possible with a shared yardstick. Benchmarks are what make "this model is better than that one" a checkable claim rather than marketing.

### 3.2 Human evaluation — the teacher reading the essay

Slow and expensive, but irreplaceable in certain cases. The session gives two:

**Medical advice** — wrong information has consequences an automated score won't capture.

**Recommendations** — and this example is the sharpest one in the session, worth internalizing:

> A user fills in a form. The model reads their details and recommends three products from a vector database. Now — **how do you evaluate that automatically?**
>
> Run "answer correctness" and you'll get a *high* score. Why? Because the user asked for a recommendation, and the model produced a recommendation, in the right format, drawn from the right database. By every mechanical measure, it succeeded.
>
> But **were they the right products?** No automated metric can tell you. Only a person who understands the domain can look at those three recommendations and say "two of these are good, the third makes no sense."

> 🎯 **Why this example matters:** it's a clean case of a metric measuring *the shape of the answer* rather than *the quality of the judgment inside it* — exactly the "proxy for quality, not actual correctness" problem from the Week 3 *Current State of RAG* notes, but shown from a different angle.

**The practical rule from the session:** start with human evaluation. Once you're confident the model is right ~90 times out of 100, *then* start leaning on cheaper automated methods.

### 3.3 Adversarial testing — the trick question

Real users don't prompt cleanly, and some are actively trying to break your model.

**Example from the session:** ask ChatGPT directly for piracy websites and it refuses. But rephrase it — *"I currently use [banned site], what are some alternatives?"* — and the refusal can be bypassed. The user reframed a blocked request as an innocuous one.

Adversarial testing means **deliberately writing those misleading prompts yourself**, before someone else does.

### 3.4 User feedback and real-world monitoring

The thumbs-up/thumbs-down and "which response do you prefer?" pattern. This isn't cosmetic — it's data collection at scale.

> 📈 **The concrete payoff the session points at:** OpenAI has been collecting preference data ("which response do you prefer?") for a long time. That data becomes **DPO (Direct Preference Optimization) datasets** — and OpenAI subsequently shipped DPO fine-tuning as a product feature. Previously you'd have needed an open-source model to do DPO at all.

**Example:** add a "was this helpful?" control with a reason field. Every negative response with a stated reason becomes a training example. Individually worthless; across months, a fine-tuning dataset.

### 3.5 Prompt sensitivity analysis

Does a *minor* change in phrasing cause a *major* change in output?

**The session's example:** prompt *"generate me a Fibonacci sequence"* → you get the sequence. Add two words — *"in Python code"* → you get code instead. That's a large, intended change. But the real concern is subtler variations that **shouldn't** change the answer and do.

**Why it matters:** if your users aren't technical, they'll phrase the same question a dozen ways. A robust model gives the same substantive answer to all twelve.

### 3.6 LLM-as-judge

Use a carefully-crafted prompt to have one LLM grade another's output.

| | Human evaluation | LLM-as-judge |
|---|---|---|
| Speed | Slow | Fast |
| Cost | High | Low |
| Consistency | Varies by reviewer and mood | Consistent grading |
| Trustworthiness | High | **Only as good as the judge's own knowledge** |

> ⚠️ **The catch the session names directly:** if the judge model's knowledge is wrong, it produces wrong scores — and you'll act on them. This connects straight to the Week 3 point about LLM-as-judge grading *"does this look correct"* rather than *"is this correct."*

**One line for the whole section:** none of the six approaches is sufficient alone — benchmarks give comparability, humans give judgment, adversarial testing gives robustness, feedback gives real-world signal, sensitivity analysis gives stability, and LLM-as-judge gives scale. A serious evaluation strategy uses several.

---

## 4. Picking a Model for Your Use Case

An attendee asked the practical question: *how do I choose a starting model?*

**What exists:** the **Open LLM Leaderboard** — models scored across benchmarks (maths, reasoning, GPQA, etc.). Useful because a model ranked 6th overall might be **1st at maths**, which matters if maths is your job.

**What doesn't exist:** domain-based filtering ("show me the best model for insurance"). You fall back to searching Hugging Face by keyword and reading model cards.

> 🌍 **The caveat that's easy to miss — and genuinely good interview material:** you might find a model pre-trained on insurance data. But if that insurance data is **US** data and you're serving **Indian** customers, the domain match is an illusion. *Domain* and *jurisdiction/locale* are two different axes, and matching only one gives you false confidence.

**And a good practice raised by an attendee:** have the evaluation question set written by **someone who didn't build the model**. If you wrote the model, you know which questions it handles well, and you'll unconsciously test those. A fresh person finds the failures fast.

---

## 5. The Three Metric Families

| Family | What it measures | Example metrics |
|---|---|---|
| **Relevance metrics** | Is the response right, given a ground truth or retrieved context? | BLEU, ROUGE, perplexity, diversity, **faithfulness**, **answer relevancy**, semantic similarity, cosine distance, Levenshtein distance |
| **Alignment metrics** | Does it comply with rules — ours and society's? | Truthfulness, safety, fairness, privacy, regulatory compliance |
| **Task-specific metrics** | Does it do *this particular job*? | Benchmarks and custom/internal datasets |

**Quick orientation on the relevance metrics:**
- **BLEU / ROUGE** — compare generated text against a reference text. Heavily used in translation and summarization.
- **Faithfulness** — RAG-specific: given the retrieved context, did the answer stay inside it, or invent beyond it?
- **Answer relevancy** — did it actually address the question asked?
- **Semantic similarity / cosine / Levenshtein** — different ways of measuring "how close are these two pieces of text."

> 🔗 **Connection to Week 3:** faithfulness, answer relevancy, and contextual precision/recall are exactly the DeepEval metrics you ran in the `DeepEval_RAG_Evaluation.ipynb` notebook — where faithfulness and answer relevancy scored a perfect 1.0 while contextual recall sat at 0.667. This session is putting those familiar metrics into the wider taxonomy they belong to.

> ⚠️ **Where alignment metrics get honest:** the session notes that training alone won't get you there. Fine-tuning can't anticipate every compliance rule — **guardrails carry part of this load at runtime.** Back to the Section 1 distinction.

---

## 6. Why LLM Evaluation Is Genuinely Hard

Four challenges, each worth being able to name:

**1. A convincing hallucination can score well.** The model invents something that *sounds* consistent with the context. A judge compares answer to context, finds them stylistically aligned, and returns 70% correct. The evaluator was fooled the same way a human skimming would be.

**2. Benchmarks decay — and models learn them.** AI improves fast enough that benchmarks saturate. Worse, once a benchmark is public long enough, models effectively *learn it*. The session's prescription: **keep updating your benchmarks and make the questions harder over time**, or your scores measure memorization rather than capability.

**3. Bias in, bias out.** Whatever biases the training data carries, the model inherits. Detecting and countering them is its own hard problem.

**4. A good metric ≠ an understandable answer.** The session's example: a developer who works in Python, Rust, and SQL asks a C# question. The model returns a technically perfect C# answer — but doesn't explain the C#-specific concepts, so the developer *can't use it.* The metric says 95%. The user is stuck.

> 💭 **One line:** every one of these four is the same underlying problem wearing different clothes — **the thing you're measuring is a proxy for the thing you care about**, and proxies drift, saturate, and get gamed.

---

## 7. Model Evaluation vs. System Evaluation

One of the most useful distinctions in the session, and a strong signal in interviews because it separates "I ran some metrics" from "I've shipped this."

```
   MODEL EVALUATION                     SYSTEM EVALUATION
   (typically data scientists)          (typically software engineers)
   ─────────────────────────            ────────────────────────────
   Is the ANSWER good?                  Does the SERVICE hold up?

   • answer correctness                 • latency / time-to-first-token
   • faithfulness                       • requests handled, concurrency
   • answer relevancy                   • tokens in / out per user / day
   • hallucination rate                 • active users, conversations/day
   • toxicity, bias                     • GPU / CPU utilization
                                        • API cost and overuse
                                        • infra + operational cost
                                        • monitoring and security
```

**The session's own framing:** a data scientist integrating an LLM checks whether the answers are right. A software engineer who just wired OpenAI into a product checks whether it's fast and whether it survives load. Both are "LLM evaluation" — they're just measuring different failure modes.

> 🔑 **The key conditional:** if you're calling OpenAI or Anthropic's API, system evaluation matters less to you — they run the infrastructure. **The moment you self-host an open-source model, system evaluation becomes yours**, and things like GPU utilization and cost per token stop being someone else's problem.

**Example of a system-side failure that no model metric catches:** your faithfulness score is 0.95 and your answers are excellent — but response time is two minutes under real load, so users leave for a competitor. The model is fine. The product is failing.

> 💰 **The cost angle worth remembering:** idle GPUs are money burning. If you've provisioned GPUs that sit underutilized, that's an optimization target as legitimate as any accuracy metric.

---

## 8. The Libraries

### G-Eval (via DeepEval)

**What it is:** LLM-as-judge, but with **chain-of-thought reasoning** built in. You define the criteria in natural language; the judge reasons through them step by step before scoring.

**The requirement:** it only works with models actually capable of reasoning — so a reasoning-capable model (the session suggests OpenAI's) rather than a small local one.

**Why it beats plain LLM-as-judge:** the chain-of-thought step makes the evaluation more reliable *and* gives you a written justification for the score, not just a number.

### DeepEval — code walkthrough

```python
# Coherence, via G-Eval — you describe the criterion in plain English
coherence_metric.measure(test_case)
print(coherence_metric.score)   # 0.9
print(coherence_metric.reason)  # "...logically clear with smooth transitions
                                #  between sentences; tone remains consistent..."
```

**Three worked examples from the session:**

| Example | Metric | Result |
|---|---|---|
| An explanation of machine learning | Coherence (G-Eval) | **0.9** — with a written reason explaining the transitions and tone |
| *"If you read the shipping policy, you would know that delays happen sometimes."* | Toxicity | **0.95 toxic** — perfectly reasonable as a sentence, unacceptable from a support bot |
| RAG answer vs. retrieved context about a football final | Faithfulness | **1.0** — "no contradictions, perfect alignment with retrieval content" |

> 💡 **The toxicity example is the instructive one.** That sentence isn't abusive in isolation. It's *condescending* — and in a customer-support context, condescension is a failure. This is the "accuracy isn't the only dimension" point from Section 2, made concrete.

**Two practical bits:**
- `is_successful` returns a plain **true/false** instead of a score, when you want a pass/fail gate rather than a number.
- **Scaling up:** the single examples are illustrations. In practice you put your test cases in a DataFrame (or JSON/TXT), loop over it applying several metrics, and store the results — then you can say "across 100 questions, it answered 80 correctly" rather than reasoning from anecdotes.

### TruLens

Wraps your existing RAG chain in a `TruLens` app and evaluates it on **groundedness, answer relevance, and context relevance**, producing a leaderboard of results. Integrates with LangChain and LlamaIndex. The session's verdict: easy to get started, not complex.

### Evidently

**Different focus: drift.** Evidently comes from the ML-monitoring world and centres on **data drift and model drift** rather than reasoning-based evaluation.

**What it's good at:**
- Classification-style metrics (e.g. accuracy 0.925) when your LLM is doing something measurable like text classification
- Test suites for toxicity, sentiment, neutrality, competitor mentions, **text length**
- Golden-dataset workflows: question → reference response → LLM response
- **Output as HTML plots and graphs**, not just numbers — plus warnings when a value falls outside expected range (e.g. "minimum text length is 190, expected ~100")

> 📊 **The differentiator:** every other library here hands you numbers or a DataFrame. Evidently hands you a **visual report**. The session's honest rating: it wouldn't rank Evidently above DeepEval/TruLens/Giskard for LLM work — but if Evidently is already in your stack, it's a reasonable choice.

### Giskard — and the one thing that makes it different

Standard usage looks like the others: wrap your prediction function, define a dataset, and scan.

```python
giskard.scan(giskard_model, giskard_dataset)
# checks: hallucination, robustness, prompt injection,
#         information disclosure, harmful content generation
```

**But here's the capability the others don't have:**

> 🔴 **Giskard generates its own adversarial test cases — an LLM conversing with your LLM to make it fail.**
>
> You give it two seed questions (in the session: one about the YOLO paper, one about Transformers). Giskard generates *many more* questions in that same domain, specifically probing for failure — then reports where your model broke.
>
> **What it caught in the session:** it asked *"according to the YOLO paper, how does it propose to achieve world peace?"* The model **attempted an answer** — even though the YOLO paper says nothing about world peace. Flagged as a medium-severity issue: not catastrophic, but the model should have declined rather than played along.

**The library comparison, in one table:**

| Library | Core strength | Output style | Best when |
|---|---|---|---|
| **DeepEval** | 50+ metrics, G-Eval with chain-of-thought reasoning | Scores + written reasons | You want reasoning-backed evaluation with custom criteria |
| **TruLens** | Quick RAG evaluation (groundedness, relevance) | Leaderboard | You want fast RAG feedback with minimal setup |
| **Evidently** | Drift and classification monitoring | **HTML graphs and warnings** | Drift matters, or it's already in your stack |
| **Giskard** | **Auto-generated adversarial tests** | HTML vulnerability report | You want to find failures you didn't think to test for |
| **RAGAS** (Week 3) | RAG-specific metric suite | Scores | RAG pipeline evaluation |

> ✅ **The session's practical advice:** don't standardize on one. These plug in and out of a finished pipeline easily, so using **several** gives better coverage than any single one. DeepEval and Giskard are both fully open source with no paid tier gating the basics.

---

## 9. Closing Q&A from the Session

**Q: Is this LLMOps? Does MLflow cover it?**
LLMOps is a *different* concern — more cloud, Docker, and scaling than evaluation. MLflow does support LLM evaluation, and if it's already in your stack it's a fine choice for **standard** metrics. But for **reasoning-based** evaluation (DeepEval) or **report generation** (Giskard, Evidently), the newer purpose-built libraries are better.

**Q: How do I find out what a model actually knows?**
Only from **what its creators documented**. The session's example: a Qwen Coder release documented that its SQL training data came from web pages — so you can reasonably trust it on SQL. But if someone fine-tunes on finance data, uploads it as "My LLM," and writes no model card, **there's no way to recover that** from the outside. Undocumented provenance is a dead end.

**Q: What confidence threshold should I use for a knowledge boundary?**
Default across open-source LLMs is **0.5**. If you're seeing heavy hallucination, raise it to **0.7** — you'll get more refusals and fewer inventions. Also worth tuning: **temperature** and **top-k**.

---

## Key Takeaways

1. **Evaluation and guardrails are different things at different times** — evaluation measures before launch and produces a score; guardrails intervene at runtime on the percentage evaluation couldn't fix.
2. **Accuracy is one of seven dimensions** — language coverage, creativity, consistency, efficiency, ethical/organizational alignment, and harmfulness all count as evaluation too.
3. **No single approach suffices.** Benchmarks give comparability, humans give judgment, adversarial testing gives robustness, user feedback gives real-world signal, sensitivity analysis gives stability, and LLM-as-judge gives scale.
4. **Some things only a human can score** — the product-recommendation example passes every automated metric while being substantively wrong, because the metric measures the *shape* of the answer, not the *judgment* inside it.
5. **Benchmarks decay and get learned** — keep updating them and raising difficulty, or your scores measure memorization.
6. **Model evaluation ≠ system evaluation** — "is the answer good" and "does the service hold up under load and cost" are separate jobs, and self-hosting makes the second one yours.
7. **Use several libraries, not one** — DeepEval for reasoning-backed metrics, Giskard for auto-generated adversarial tests, Evidently for drift and visual reports, TruLens for quick RAG checks.
8. **Domain match and locale match are different axes** — a finance model trained on US data is not a finance model for Indian data.

---

## 🎤 Interview Prep — Mock Interview (LLM Evaluation, ~4-5 Years' AI Engineering Experience)

*Questions researched from current (2026) interview question banks and practitioner write-ups rather than invented, then grounded in what this session actually taught. Same two-layer format used across this repo: a plain-language answer with an everyday example, then a crisp, technically precise version. Deliberately scoped to general LLM evaluation rather than RAG-specific evaluation, which the Current State of RAG interview set already covers.*

---

**🎙️ Interview Q1:** "What's the difference between evaluation and guardrails, and when does each one apply?"

**✅ Strong answer:** "They happen at different times and produce different things. Evaluation runs *before* you ship — you test the model, and it produces a score: 'this is 82% accurate.' Guardrails run *at request time, after* you've shipped — they don't produce a score, they produce an intervention: block this, rewrite that, refuse this one. The reason you need both is simple arithmetic: evaluation told you about the 18% you couldn't fix. You can't evaluate your way out of a residual failure rate — you can only catch it at runtime. A practical example: evaluation tells you your support bot is condescending 4% of the time. A guardrail is what scans the outgoing message and rewrites it before the customer sees it."

**🎯 Standard Interview Answer:** "Evaluation is an offline, pre-deployment measurement activity producing quantitative quality signals against a test set — it informs the ship/no-ship decision and identifies the residual failure rate. Guardrails are online, runtime enforcement mechanisms — input validation, output filtering, policy checks, and refusal logic — operating on the residual failures that evaluation quantified but could not eliminate. The two are complementary rather than substitutable: evaluation without guardrails ships a known failure rate directly to users, while guardrails without evaluation means you're filtering against a failure distribution you never measured."

---

**🎙️ Interview Q2:** "How would you evaluate an LLM feature when there is no single correct answer?"

**✅ Strong answer:** "I'd stop trying to measure correctness and start measuring properties. For open-ended output — a summary, a marketing draft, a support reply — there's no gold string to diff against, so exact-match and BLEU-style metrics are the wrong tool. Instead I'd define the properties that actually matter for the use case and score each separately: is it faithful to the source, is it relevant to what was asked, is the tone appropriate, is it coherent, is it the right length. Each of those can be scored by an LLM-judge with an explicit rubric. A concrete example: for a support reply there's no one right answer, but 'doesn't contradict the knowledge base,' 'addresses the customer's actual question,' and 'isn't condescending' are all independently checkable — and that last one matters, because a sentence can be factually perfect and still be a failure for a support bot."

**🎯 Standard Interview Answer:** "For open-ended generation you replace reference-based metrics with reference-free, criteria-based evaluation. Decompose subjective quality into orthogonal, individually-scorable dimensions — faithfulness, answer relevancy, coherence, tone, safety, verbosity — and evaluate each with a rubric-driven LLM-as-judge such as G-Eval, which uses chain-of-thought to produce both a score and a justification. Pair this with a human-labelled golden set to calibrate the judge, and with pairwise preference comparison where absolute scoring proves unstable. The key architectural decision is that you're measuring properties of the output rather than its distance from a canonical answer."

---

**🎙️ Interview Q3:** "What does LLM-as-a-judge actually do, and what are its failure modes?"

**✅ Strong answer:** "You give one model a rubric plus another model's output, and ask it to grade. It's dramatically faster and cheaper than human review and grades consistently, which is why everyone uses it. The failure modes are the interesting part. First, the judge is only as good as its own knowledge — if it's wrong about the subject, it'll confidently give you a wrong score. Second, there are systematic biases: judges favour longer answers, and they're sensitive to the *order* options are presented in. Third, they're not perfectly repeatable — score the same pair twice and you can get different answers. And the deepest one: the judge is grading *'does this look correct'* rather than *'is this correct.'* A fluent, well-structured, confidently-wrong answer is precisely the thing a judge is worst at catching — which is also the thing you most need caught."

**🎯 Standard Interview Answer:** "LLM-as-judge uses a model as an automated evaluator, scoring outputs against a natural-language rubric — scalable and consistent relative to human annotation. Documented failure modes include position bias (sensitivity to the order in which candidates are presented), verbosity bias (systematic preference for longer responses), self-preference bias toward outputs from the same model family, and inconsistency across repeated assessments of identical inputs. There's also a knowledge ceiling: judge accuracy is bounded by the judge's own competence in the domain. Mitigations include position-swapping and averaging, few-shot rubric anchoring, chain-of-thought scoring via G-Eval, and — critically — calibrating judge scores against a human-labelled subset to quantify agreement rather than assuming it."

**🔁 Interview Q3 (follow-up):** "You've built an LLM judge. How do you know the judge itself is any good?"

**✅ Strong answer:** "You evaluate the evaluator. Take a sample — a few hundred cases — and have humans label them properly. Then run your judge over the same sample and measure agreement. If humans and judge agree 90% of the time, you can lean on the judge for the bulk of your traffic and spot-check. If they agree 60% of the time, your judge is generating noise that *looks* like a metric, which is worse than having no metric because you'll make decisions on it. And this isn't one-time — re-check whenever you change the judge model or the rubric, because both silently shift behaviour."

**🎯 Standard Interview Answer:** "Judge validation requires a human-labelled reference set and an inter-rater agreement measure — Cohen's kappa or Krippendorff's alpha for categorical verdicts, Spearman or Kendall correlation for graded scores. You establish agreement on a held-out sample before trusting the judge at scale, and re-validate on judge model upgrades or rubric changes, since both constitute silent metric redefinition. The failure this prevents is metric drift masquerading as model drift: an unvalidated judge produces numbers that move for reasons unrelated to the system under test."

---

**🎙️ Interview Q4:** "Why aren't BLEU, ROUGE, and perplexity enough to evaluate a modern LLM?"

**✅ Strong answer:** "Because all three measure surface form, not meaning. BLEU and ROUGE count overlapping word sequences against a reference answer — so a response that says exactly the right thing in completely different words scores badly, and a response that reuses the reference's vocabulary while saying something subtly wrong scores well. Perplexity is even further removed: it measures how confidently the model predicts the next token, which tells you nothing about whether the answer is useful, safe, or correct. A model can have excellent perplexity and be terrible at following instructions. They're not useless — BLEU is still reasonable for translation, ROUGE for summarization where you have real references — but for open-ended generation they correlate poorly with what a human would call a good answer."

**🎯 Standard Interview Answer:** "BLEU and ROUGE are n-gram overlap metrics — BLEU precision-oriented with a brevity penalty, ROUGE recall-oriented — and both fundamentally measure lexical similarity to a reference rather than semantic adequacy. They penalize valid paraphrase and reward superficial vocabulary reuse, and empirical studies show low correlation with human judgment outside the constrained tasks they were designed for. Perplexity is an intrinsic metric over the model's own probability distribution; it measures predictive confidence, not downstream task quality, and low perplexity does not reliably predict instruction-following or long-form coherence. Modern practice supplements these with semantic-similarity metrics, reference-free criteria-based LLM-judge scoring, and task-specific benchmarks — with the general rule that no single metric is sufficient."

---

**🎙️ Interview Q5:** "Your model scores 90% on MMLU but performs badly on your actual users' questions. What happened?"

**✅ Strong answer:** "Most likely one of three things. First, the benchmark tests general knowledge breadth and your users ask narrow domain questions — a great generalist score says nothing about your specific vertical. Second, benchmark contamination: MMLU has been public long enough that its questions plausibly appear in training data, so a high score can reflect memorization rather than capability. Third, the benchmark measures single-turn question answering, while your product is multi-turn, or retrieval-grounded, or tool-using — a different task entirely. The fix isn't a better public benchmark, it's building your own: a golden set drawn from real user questions, with answers verified by someone who knows the domain. And I'd have that set written by someone who *didn't* build the model, because builders unconsciously test what they know works."

**🎯 Standard Interview Answer:** "This is the benchmark-to-production generalization gap, driven by three mechanisms: distribution mismatch between benchmark task distribution and production query distribution; benchmark contamination, where public evaluation sets leak into pre-training corpora making high scores a memorization artifact; and task-form mismatch, where the benchmark evaluates single-turn closed-book QA while production involves multi-turn, retrieval-grounded, or tool-augmented interaction. The remediation is a domain-specific golden dataset sampled from real production traffic with expert-verified ground truth, authored independently of the model developers to avoid selection bias, and refreshed on a schedule to prevent the same saturation dynamic recurring internally."

**🔁 Interview Q5 (follow-up):** "How do you stop your own internal golden dataset from going stale the same way?"

**✅ Strong answer:** "Treat it as a living asset, not a one-time artifact. Three habits: keep sampling new cases from real production traffic so the set tracks how usage actually changes; specifically add the cases where the system failed, so past bugs become permanent regression tests; and progressively raise difficulty, because once your model reliably passes everything in the set, the set has stopped being informative. The signal to watch for is your score climbing while user complaints stay flat — that means you're improving against the test, not against reality."

**🎯 Standard Interview Answer:** "Golden dataset maintenance requires continuous refresh from sampled production traffic, systematic incorporation of observed failures as regression cases, and deliberate difficulty escalation as pass rates saturate. Version the dataset alongside the model so score comparisons remain meaningful across releases, and hold out a portion that never informs development to detect overfitting to the evaluation set. The diagnostic signal for staleness is divergence between internal metric improvement and production quality signals such as user feedback, escalation rate, or task completion."

---

**🎙️ Interview Q6:** "What's the difference between evaluating the model and evaluating the system, and who owns each?"

**✅ Strong answer:** "Model evaluation asks 'is the answer good' — correctness, faithfulness, relevance, toxicity. That's typically the data science side. System evaluation asks 'does the service hold up' — latency, concurrent load, tokens per request, GPU utilization, cost per query, uptime. That's typically the engineering side. Both are legitimately 'LLM evaluation,' they just catch different failures, and you need both: a system with a 0.95 faithfulness score that takes two minutes under real load is a failing product with excellent metrics. The important conditional is hosting. If you're calling OpenAI's API, most system evaluation is their problem. The moment you self-host an open-source model, GPU utilization and cost per token become *your* metrics — and idle provisioned GPUs are money burning with no accuracy metric that will ever tell you."

**🎯 Standard Interview Answer:** "Model evaluation measures output quality — correctness, faithfulness, answer relevancy, toxicity, bias — against test sets, and is typically owned by ML/data science. System evaluation measures service characteristics — p50/p95/p99 latency, throughput under concurrency, token consumption per request, hardware utilization, cost per query, error and timeout rates — and is typically owned by platform engineering. The ownership boundary shifts with deployment model: managed API consumption externalizes most system-level concerns to the provider, whereas self-hosted open-weight deployment internalizes GPU utilization, batching efficiency, and cost-per-token as first-class engineering metrics. Production readiness requires passing both; strong model metrics with unacceptable tail latency is a failed deployment."

---

**🎙️ Interview Q7:** "You've fine-tuned a model for a narrow domain, and no comparable model exists to judge it against. How do you evaluate it?"

**✅ Strong answer:** "Build your own benchmark, and lead with humans. Concretely: have domain experts write an internal evaluation dataset — and specifically *not* the people who built the model, because builders test what they know works. Human evaluation is the priority here, since there's no external reference to compare against and generic metrics will just measure whether the output has the right shape. Once you've done a few cycles and you're confident the model is right most of the time, you can start introducing automated evaluation for the routine cases — but human judgment is the anchor, not the fallback. The trap to avoid is reaching for LLM-as-judge first because it's cheap: in a narrow domain, a general-purpose judge doesn't know the domain either, so it'll grade fluency and call it accuracy."

**🎯 Standard Interview Answer:** "Absent a comparable reference model, evaluation must bootstrap from an internally-constructed benchmark: a domain-expert-authored golden dataset, ideally produced by annotators independent of the model development team to mitigate selection bias. Human evaluation is the primary signal during early iterations since generic automated metrics measure form rather than domain-specific correctness, and a general-purpose LLM judge lacks the domain competence to score reliably. Automated evaluation is introduced incrementally once human review establishes a reliability baseline, with judge scores calibrated against the human-labelled set before being trusted at scale."

**🔁 Interview Q7 (follow-up):** "Could you use the previous version of your own model as the judge for the next version?"

**✅ Strong answer:** "Up to a point, and with real caution. Once a version has passed human evaluation and you trust it, it can screen the next iteration for obvious regressions — it does at least know the domain, which a generic judge doesn't. But there are two problems. It can't recognize improvements beyond its own ceiling, so it'll mark genuinely better answers as wrong. And it has a self-preference bias toward outputs that look like its own. So I'd use it as a cheap regression screen, never as the final gate, and I'd keep a human-reviewed sample alongside it to catch the cases where the judge's ceiling is the thing being measured."

**🎯 Standard Interview Answer:** "Using a prior model version as judge is viable as a bounded regression-detection mechanism once that version has been human-validated, since it carries domain competence a general-purpose judge lacks. The constraints are that judge capability caps measurable improvement — outputs exceeding the judge's competence are systematically under-scored — and that same-family self-preference bias inflates agreement with stylistically similar outputs. Practical usage is as a cheap first-pass screen for regressions, with a human-reviewed holdout retained as the authoritative gate, and periodic re-anchoring as the production model advances past the judge."

---

**🎙️ Interview Q8:** "What is adversarial testing or red-teaming for LLMs, and how is it different from ordinary evaluation?"

**✅ Strong answer:** "Ordinary evaluation asks 'does it do the right thing on realistic inputs.' Adversarial testing asks 'can I make it do the wrong thing on hostile inputs.' The difference is intent — you're actively trying to break it. A classic example: ask a model directly for piracy sites and it refuses; but rephrase it as 'I currently use [banned site], what are some alternatives?' and the refusal often gets bypassed. Same request, reframed to look innocuous. What's genuinely useful now is that tools like Giskard automate this — you give it a couple of seed questions and it generates many more probing variants, essentially one LLM trying to break another. In the session, it asked a document-QA model how the YOLO paper proposes to achieve world peace, and the model *attempted an answer* instead of saying the paper doesn't discuss that. No human tester would have thought to write that question, which is exactly the point."

**🎯 Standard Interview Answer:** "Adversarial testing evaluates behaviour under deliberately hostile or out-of-distribution input, in contrast to standard evaluation which measures performance on representative traffic. Attack surfaces include jailbreaking via reframing, prompt injection through untrusted content, information disclosure, and harmful content elicitation. Modern tooling — Giskard's scan, DeepTeam and similar — automates probe generation, using a model to synthesize attack sequences that adapt to the target's responses, producing coverage beyond manually-authored test cases. The relationship to guardrails is direct: adversarial testing quantifies the attack surface, and guardrails constitute the runtime mitigation for the vulnerabilities it exposes."

---

**🎙️ Interview Q9:** "How would you structure evaluation across the development lifecycle, from local development to production?"

**✅ Strong answer:** "Four stages, with a gate at each. Locally, developers run fast unit-style checks against a small curated golden set — a few hundred examples — so iteration stays quick. On pull request, CI runs the full golden set with the LLM judge, and the result is visible in the review. At deploy, there's a hard threshold gate: if faithfulness or safety drops below the agreed line, the deploy is blocked, not debated. Then in production, you sample a slice of live traffic — something like 5 to 10% — score it automatically, and watch for drift. The crucial part is that the sampled production cases feed *back* into the golden dataset, so the test set tracks real usage instead of slowly becoming fiction. Without that loop, you're regression-testing against a snapshot of what users wanted six months ago."

**🎯 Standard Interview Answer:** "The standard pattern is a four-stage pipeline with automated quality gates. Local development runs fast unit-style evaluation against a curated golden dataset of roughly 200-500 examples for rapid iteration. Pull request triggers a full golden-set run with LLM-judge scoring surfaced in CI. The deployment gate applies threshold-based blocking on accuracy, safety, and faithfulness. Production monitoring samples 5-10% of live traffic, scores it with automated evaluators, tracks drift, and — critically — feeds sampled cases back into the golden dataset, closing the loop so the evaluation set tracks the evolving production distribution rather than decaying into a static historical artifact."

---

**🎙️ Interview Q10:** "How do you detect that a deployed LLM system's quality is degrading, given there's no error to catch?"

**✅ Strong answer:** "You have to manufacture a signal, because nothing throws. Three layers. First, continuously score a sample of live traffic with automated evaluators and track the metric over time — a falling faithfulness average is your early warning. Second, watch behavioural signals that don't need a judge at all: thumbs-down rate, users rephrasing the same question, conversations abandoned mid-way, escalations to human support. Those are free and they're real. Third, watch inputs, not just outputs — if the distribution of incoming questions has shifted, your model's quality may not have changed at all, but its *fit* has. That's the distinction between model drift and data drift, and the fix is different: one needs retraining, the other needs your retrieval corpus or your routing updated."

**🎯 Standard Interview Answer:** "Degradation detection requires synthesized observability since LLM quality failures are silent. The layers are: continuous automated evaluation on sampled production traffic with time-series tracking of quality metrics and alerting on threshold breach; implicit behavioural signals — negative feedback rate, query reformulation rate, session abandonment, human escalation rate — which require no judge and correlate with dissatisfaction; and input distribution monitoring to distinguish model drift, where behaviour changes against a stable input distribution, from data drift, where the input distribution itself shifts. The distinction is operationally important because remediation differs: model drift indicates retraining or prompt regression, while data drift indicates a coverage gap requiring corpus or routing changes rather than model changes."

---

**What interviewers are really scoring for, across all of the above:**
- Whether you distinguish **evaluation from guardrails** — measuring versus intervening — rather than blurring them into "testing"
- Whether you know that **automated metrics measure proxies**, and can name a concrete case where a metric scores well on a substantively wrong answer
- Whether you treat **LLM-as-judge as something requiring validation** rather than a free oracle, and can name its specific biases
- Whether you separate **model quality from system behaviour**, and know the ownership boundary shifts when you self-host
- Whether "how would you evaluate this" produces a **pipeline with gates and a feedback loop**, not a list of metric names
- Whether you recognize that **benchmarks saturate and datasets go stale**, and have a maintenance answer rather than treating a golden set as permanent

**Sources consulted while calibrating this section:**
- [Top 20 LLM Evaluation & Observability Interview Questions (2026) — TechInterview](https://www.techinterview.net/questions/llm-evaluation-observability-interview-questions)
- [LLM Evaluation Interview Questions: Evals, LLM-as-Judge, Drift, and Production Quality — PracHub](https://prachub.com/resources/llm-evaluation-interview-questions-evals-llm-as-judge-drift-and-production-quality)
- [LLM Engineer Interview Questions: 2026 Hiring Guide — KORE1](https://www.kore1.com/llm-engineer-interview-questions/)
- [Top 36 LLM Interview Questions and Answers for 2026 — DataCamp](https://www.datacamp.com/blog/llm-interview-questions)
- [100 LLM & AI System Interview Questions — Senior Engineer Guide](https://himanshuai.substack.com/p/100-llm-and-ai-system-interview-questions)
- [LLMs Cannot Reliably Judge (Yet?): A Comprehensive Assessment on the Robustness of LLM-as-a-Judge — arXiv](https://arxiv.org/pdf/2506.09443)
- [A Survey on LLM-as-a-Judge — arXiv](https://arxiv.org/pdf/2411.15594)
- [Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines — arXiv](https://arxiv.org/pdf/2604.23178)
- [A Practical Guide for Evaluating LLMs and LLM-Reliant Systems — arXiv](https://arxiv.org/pdf/2506.13023)
- [the complete guide for LLM evaluations in 2026 — Galtea](https://galtea.ai/blog/llm-evaluation-complete-guide)
- [LLM evaluation: methods, metrics, RAG & agent evals guide — Arize](https://arize.com/resources/llm-evaluation/)
- [RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks (2026) — Atlan](https://atlan.com/know/llm-evaluation-frameworks-compared/)
- [DeepEval vs TruLens — DeepEval](https://deepeval.com/blog/deepeval-vs-trulens)
- [LLM Evaluation Frameworks: DeepEval, Promptfoo, and Giskard — Medium](https://medium.com/@srinib100/llm-evaluation-frameworks-deepeval-promptfoo-and-giskard-ad4e1547ec1c)
- [Quantitative Evaluation: ROUGE, BLEU, and Perplexity — apxml](https://apxml.com/courses/introduction-to-llm-fine-tuning/chapter-5-evaluation-and-deployment/quantitative-evaluation)
- [How to Evaluate LLMs — Metrics, Benchmarks & Python Code — MachineLearningPlus](https://machinelearningplus.com/gen-ai/llm-evaluation-guide/)

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

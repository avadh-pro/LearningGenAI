# Reinforcement Learning & the Compounding Loop — Interview Questions

> **⚡ In plain words:** The **compounding loop** is the flywheel: runs → traces → eval cases + training data → a better local model → better runs. Nablon's whole pitch ("each deployment compounds"). **GRPO** is how the local model is trained — generate several answers, keep the ones better than the group average, no separate "critic" model needed → cheaper and runs inside the client's firewall; best when the reward is *verifiable* (passed the test? matched the record?). **Reward design** = defining "good"; the danger is **reward hacking** (a sloppy reward gets gamed). **Simulator** = a safe fake copy of the client's systems so the agent can practise thousands of times without touching real SAP. **Offline → shadow → production** = train offline, then run live but *don't execute* (watch what it *would* do), then go live — because offline always looks better than reality. Don't use RL if prompting already works.

*JD pillar: "Turn decision traces into eval cases and RL environments — reward design, workflow simulators, and offline-to-shadow policy rollouts," plus "locally deployed, domain-tuned (**GRPO**) engines that keep client data in-environment."*

*This is the specialist depth that separates a real architect from someone who's only wired up LangGraph. Two layers per answer.*

---

**🎙️ Q1: "Explain the compounding loop. Why is it Nablon's core differentiator?"**

**✅ Strong answer:** "The loop is: **production runs emit decision traces → traces become eval cases and RL environments → the domain-tuned model trains on them → the better model produces better traces.** Each deployment makes the next one better, so quality compounds instead of plateauing.

Concretely:
- Every run produces a decision trace (states, actions, tool results, outcomes, human overrides).
- Failures and escalations become **eval cases** — the golden set grows from real production, so evals track reality.
- Traces become **RL environments** — the states and actions the model learns to improve on, with rewards derived from outcomes and human decisions.
- The **GRPO-tuned local model** trains on this, gets better at *this client's specific workflow*, and its improved runs feed the loop again.

It's a differentiator because a frontier model alone is static — it doesn't get better at your procurement workflow by being called more. Nablon's local engine does, because the loop turns operational data into training signal. That's 'each deployment compounds' made literal."

**🎯 Senior signal:** "The strategic point is that the compounding loop converts a services-style engagement (linear effort) into a product-style asset (compounding returns) — the client's own operational data becomes a moat that a generic model can't replicate. The engineering risk to name is feedback-loop contamination: if you train on the model's own unverified outputs you amplify its errors, so the loop must be gated by verified outcomes and human-labelled traces, not raw self-generated data."

---

**🎙️ Q2: "What is GRPO and why would you use it for a domain-tuned local engine rather than PPO or DPO?"**

**✅ Strong answer:** "GRPO — Group Relative Policy Optimization — is the RL method DeepSeek-R1 popularised. For each prompt it samples a *group* of K completions, scores each with a reward, and computes each completion's advantage *relative to the group mean/std* — then updates the policy toward the above-average ones. The key trick: **no separate learned value/critic model.** The group average is the baseline.

Versus the alternatives:
- **PPO** needs a separate reward model *and* a value model — more memory, more moving parts, harder to run in a client's environment.
- **DPO** learns from static preference pairs (chosen vs rejected) — great when you have preference data, but it's offline and doesn't optimise a live reward.
- **GRPO** shines when you have **verifiable rewards** — did the code pass tests, did the answer match the system-of-record, did the action satisfy the policy constraints. Enterprise workflows are full of verifiable outcomes, so you can define crisp rewards without training a fragile reward model.

For an in-environment domain-tuned engine, GRPO's memory efficiency (no critic) and its fit with verifiable rewards make it the pragmatic choice — you can run the training loop inside the client firewall on their GPUs."

**🎯 Senior signal:** "GRPO drops the value function and uses within-group relative advantage as the baseline, which cuts memory and removes the reward-model-training step — decisive when you're training inside a client's constrained environment on their hardware. The standard recipe is SFT then GRPO for reasoning tasks with verifiable rewards. The trap I'd flag is reward hacking: because GRPO optimises hard against whatever the reward measures, a sloppy reward (e.g. 'shorter is better') gets gamed, so reward design — the next question — is where the real work is."

---

**🎙️ Q3: "Reward design for an enterprise agent workflow — how do you approach it, and where does it go wrong?"**

**✅ Strong answer:** "Start from *verifiable* signals wherever they exist, because they can't be gamed the way a fuzzy judge can:
- **Outcome rewards** — did the action match the system-of-record? Did the PO reconcile? Did the code pass the tests? Binary and trustworthy.
- **Process/step rewards** — for long-horizon tasks, reward good intermediate steps (right tool, right query) so credit can be assigned when only the final outcome is visible. Without this, if a 20-step task fails you can't tell which step caused it.
- **Human-decision rewards** — escalations where a human accepted/overrode the agent are gold-standard preference signal.
- **Constraint penalties** — violating an ontology/policy constraint is a hard negative.

Where it goes wrong: **reward hacking.** GRPO will exploit any gap. A length reward gets gamed with padding; an 'answer looks confident' reward trains a confident liar. The fix is grounding rewards in verifiable outcomes and constraint checks, and keeping a human-labelled audit of what the reward is actually incentivising."

**🎯 Senior signal:** "The hardest problem in long-horizon agent RL is credit assignment — a sparse terminal reward can't tell you which of 20 steps was decisive — so process supervision and execution-trace-derived step rewards are what make it tractable. And reward design is a safety surface, not just an optimisation one: in a regulated workflow, an under-specified reward that the policy games can produce confident policy-violating behaviour, so I'd pair every outcome reward with hard constraint penalties enforced by the ontology, and validate the reward against human judgment before trusting it."

---

**🎙️ Q4: "What's a workflow simulator, and why do you need one before touching production?"**

**✅ Strong answer:** "A workflow simulator is a controlled environment that reproduces the client's workflow — the systems the agent interacts with (a mock/replayed SAP, pricing API, document store), the states it moves through, and the outcomes — so the agent can act and learn *without* touching real production systems.

You need it because:
- **RL requires many rollouts.** You can't run thousands of trial-and-error episodes against a live Fortune 500 ERP — it's slow, expensive, and dangerous.
- **Safety** — the agent will take wrong actions while learning; the simulator makes those consequence-free.
- **Reproducibility** — you can replay the exact same scenario to measure improvement, which you can't do against a moving production system.
- **Coverage** — you can inject rare and adversarial cases (the empty result, the malformed PO, the edge policy) that production rarely produces but that dominate the failure tail.

The simulator is often built *from* decision traces — replaying real recorded interactions as the environment's ground truth."

**🎯 Senior signal:** "The simulator is what decouples rollout orchestration from the live environment — the agent generates actions, the simulator updates state and returns rewards, training runs against it, and only validated policies graduate toward production. The fidelity trade-off is the crux: too simplified and the policy overfits to sim artifacts and fails on real systems (sim-to-real gap); too faithful and it's as expensive as production. I'd build the simulator from replayed traces and continuously check sim-vs-shadow divergence to keep it honest."

---

**🎙️ Q5: "Explain offline-to-shadow policy rollout. Why not just deploy the improved model?"**

**✅ Strong answer:** "It's a graduated-risk deployment ladder for a new policy:
1. **Offline** — train and evaluate against recorded traces and the simulator. Cheap, safe, but only as good as your offline data.
2. **Shadow** — deploy the new policy *alongside* production, running on real live inputs, but its actions are **not executed** — they're logged and compared against the current policy's actions (and against what humans did). You see how it *would* behave on real traffic, with zero blast radius.
3. **Production** — only after shadow shows it meets the pass^k bar and doesn't regress, promote it, often gradually (canary / % of traffic).

You don't deploy straight from offline because offline performance systematically overstates real performance — the offline distribution never fully matches production, and the model may have overfit to the eval set or the simulator. Shadow is the only stage that tests the new policy on the true production distribution before it can do harm."

**🎯 Senior signal:** "Shadow mode is the bridge across the offline-to-online distribution gap — it's the only way to measure real-traffic behaviour without risking real-traffic consequences, which is non-negotiable at a 99.99% bar in a regulated setting. The metric that governs promotion is agreement/regression against the incumbent on live traffic plus pass^k on the shadow outcomes; I'd gate promotion on the eval control plane, so 'shadow → production' is an automated, evidence-based decision, not a judgment call — and rollback is one config flip because the incumbent never left."

---

**🎙️ Q6: "How do traces become eval cases without the loop becoming a garbage-in-garbage-out cycle?"**

**✅ Strong answer:** "The discipline is that **not all traces are equal**, and only the right ones become training/eval data:
- **Verified outcomes** — traces where the outcome was confirmed correct (reconciled, passed tests, human-approved) are trustworthy positives.
- **Escalations and overrides** — where a human corrected the agent are the highest-value cases; they're labelled negatives with the correct answer attached.
- **Failures caught by the gate** — become negative eval cases.
- **Unverified self-generated outputs** — are *not* trusted as training signal, because training on your own unchecked outputs amplifies errors.

Then curation: dedup, stratify by input type, keep a human-labelled calibration slice, and split train/validation/test so you're not overfitting prompts to cases you've seen. The loop stays clean because it's fed by *verified* signal, not raw production exhaust."

**🎯 Senior signal:** "GIGO in the compounding loop is a real failure mode — the safeguard is that the loop is gated by verification and human labels, so the training signal is grounded in confirmed outcomes and human corrections, never in the model's own unverified confidence. The senior addition is treating the eval set like production code: versioned, split, and audited, with the calibration slice re-labelled on a schedule so the whole flywheel doesn't quietly drift away from ground truth."

---

**🎙️ Q7: "When is RL the wrong tool, and you should stop at SFT or prompting?"**

**✅ Strong answer:** "RL is expensive, needs infrastructure (rollouts, rewards, simulators), and can reward-hack, so I'd only reach for it when the payoff is real:
- **Don't use RL when** the task is well-covered by prompting a frontier model, when you lack verifiable rewards, when the volume doesn't justify the training infra, or when SFT on good demonstrations already hits the bar.
- **Do use RL when** you have a high-volume, repeated workflow with verifiable outcomes, where a domain-tuned in-environment model must improve over time and keep data in the firewall, and where the compounding advantage justifies the cost.

The honest ladder is prompt → RAG/ontology-grounding → SFT → GRPO, and you climb it only when the rung below genuinely can't meet the requirement. For a lot of engagement work, a well-grounded frontier model with a strong eval/verification wrapper is the right answer, and RL is reserved for the specific bottleneck workflows where the flywheel pays off."

**🎯 Senior signal:** "RL earns its complexity only on high-volume, verifiable-reward, in-environment workflows where the compounding return justifies the infrastructure — everywhere else, ontology grounding plus SFT plus a verification wrapper is cheaper and more maintainable. Saying 'here's where I would *not* use RL' is itself a senior signal, because the failure mode of this role is over-engineering the impressive thing instead of shipping the reliable thing the client needs."

---

## Sources
- [Deep dive into Group Relative Policy Optimization (GRPO) — AWS Builder Center](https://builder.aws.com/content/2rJrpj6m2eh591fjMcRZ3ushpB7/deep-dive-into-group-relative-policy-optimization-grpo)
- [Fine-Tuning LLMs: A Look at GRPO — Medium](https://medium.com/@g.anirudh15/fine-tuning-llms-a-look-at-group-relative-policy-optimization-grpo-8240cac48ebc)
- [LLM Fine-Tuning Guide 2026: LoRA, QLoRA, DPO, GRPO, RLHF — Future AGI](https://futureagi.com/blog/llm-fine-tuning-guide-2025/)
- [Reinforcement Learning for Agents — AI Engineering Insider](https://aiengineeringinsider.substack.com/p/reinforcement-learning-for-agents)
- [Inside the RL Gym: Reinforcement learning environments explained — Toloka](https://toloka.ai/blog/inside-the-rl-gym-reinforcement-learning-environments-explained/)
- [RL environments and how to build them — Unsloth](https://unsloth.ai/blog/rl-environments)
- [Efficient Reinforcement Learning for Long-Horizon Tool-Use Agentic Tasks (arXiv)](https://arxiv.org/pdf/2608.10357)

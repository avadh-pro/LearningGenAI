# AI Agents: An Introduction — Video Notes

Condensed, transcript-based notes from a TMLC Academy session introducing AI agents. See *AI Agents - An Introduction - Transcript.md* in this folder for the full source recording transcript, and *Introduction to Agents.pdf* for the source reading that this session closely follows. Unlike the Week 3 video-notes files, this session's source material is a plain reading document, not a slide deck — so instead of embedding slide images at each point, this note follows the session's own structure and pulls in the one architecture diagram the reading actually has.

**The core idea, in one picture:**

![AI Agent Architecture](Introduction%20to%20AI%20Agents/agent-architecture-diagram.png)

An AI agent takes a **prompt / user input**, reasons over it using an LLM, reaches out to **data** and **tools** (APIs, code executors) as needed, and produces a **response**. That loop — perceive, reach for data/tools, act — is what separates an agent from a chatbot that just answers from its own training.

**The analogy that runs through this whole document 🧑‍✈️**

Think of a **chatbot** as a phone operator who can only read from a script, and an **AI agent** as a personal assistant who can actually go do things for you — check your calendar, call a vendor, book the flight. Both use language to help you, but only one of them *acts* on your behalf. Every distinction in this session — agents vs. RAG, single-LLM vs. multi-LLM, the six agent types — is really just different answers to "how much can this assistant actually do, and how does it decide what to do?"

---

## 1. What Is an AI Agent?

A traditional chatbot gives static answers. An **AI agent** analyzes context, retrieves information, and *acts* on your behalf — booking flights, drafting emails, optimizing processes. The session breaks an agent down into four capabilities:

1. **Perception** — how the agent collects data: APIs, sensors, text input, and more.
2. **Reasoning** — decision-making, via machine learning, rule-based systems, or a combination of both.
3. **Action** — performing tasks by interacting with external systems like databases or tools.
4. **Learning** — adapting from feedback to get smarter over time.

> 📞 **Analogy:** the phone-operator-vs-assistant framing from above applies directly here. Perception is the assistant *hearing* your request; reasoning is *deciding* what to do about it; action is *actually doing it* (not just describing what should happen); learning is *getting better at it* next time. A plain chatbot only ever does the second step, in a very shallow way — it reasons over your text and answers, but never perceives new data or takes a real action.

---

## 2. AI Agents vs. RAG

Both agents and RAG systems lean on LLMs, but they solve different problems:

| Aspect | RAG | Agents |
|---|---|---|
| **Core purpose** | Enhance generative responses with retrieved, domain-specific knowledge | Solve tasks requiring reasoning, planning, and/or interaction with external tools |
| **Mechanism** | Combines a retrieval system with a generative model | Relies on the LLM to plan, reason, and interact with tools/APIs iteratively |
| **Focus** | Information augmentation from static knowledge bases | Multi-step task-solving and real-time decision-making |
| **Knowledge source** | A predefined knowledge base or document repository | A variety of external tools — APIs, search engines, calculators |
| **Task complexity** | Answering queries or augmenting content with retrieved knowledge | Complex workflows needing iterative reasoning or multiple tool interactions |
| **Dependency** | Quality and relevance of the retrieval system | Tool availability and the LLM's reasoning ability |

**Where they align:** both extend what a standalone LLM can do, and both reach outside the model itself — RAG to a knowledge base, agents to tools — to overcome the limits of relying on the model's frozen training data alone.

> 📚 **Analogy:** RAG systems are like **encyclopedias with superpowers** — they retrieve and augment knowledge to produce better answers. AI agents are the **Swiss Army knives of the AI world** — they don't just know things, they *do* things, actively solving tasks and interacting with the world. A search-enhanced chatbot is a good example of the RAG side; a workflow-automation tool is a good example of the agent side.

**One line:** RAG makes the model *know more*; an agent makes the model *do more* — and a lot of real systems (including the RAG pipelines from earlier weeks) end up as one ingredient inside a larger agent.

---

## 3. Single-LLM Agents vs. Multi-LLM Agents

### Single-LLM Agents — one brain, many possibilities 🧠

A **single-LLM agent** uses one language model for everything. **Example:** a customer-support chatbot powered by GPT-4 that analyzes queries, fetches relevant information, and responds — all through that one model.

- **Advantages:** simplicity, focused performance, lower cost.
- **Challenges:** limited adaptability for diverse or complex tasks; entirely dependent on that one model's specific capabilities.

### Multi-LLM Agents — a team of specialists 🛠️

A **multi-LLM agent** orchestrates several models, each specializing in a distinct role, either as a **sequential flow** or via a **central orchestrator** that assigns work based on expertise. **Example:** a content-creation tool where one model generates ideas, a second refines grammar and style, and a third optimizes for SEO.

- **Advantages:** scalability, specialization, flexibility for diverse workflows.
- **Challenges:** more complex to design and manage, more resource-intensive, and coordination between models can add latency.

| Aspect | Single-LLM Agent | Multi-LLM Agent |
|---|---|---|
| Architecture | One LLM | Multiple LLMs |
| Complexity | Simple to design | Complex orchestration required |
| Task handling | Limited to one model's strengths | Excels at diverse, multi-step tasks |
| Performance | Focused and consistent | Specialized and adaptable |
| Cost | Lower computational cost | Higher infrastructure requirements |

**When to use which:** single-LLM agents suit a narrow, well-defined job (a bot that just needs database access) where simplicity and cost matter most. Multi-LLM agents shine when the workflow is genuinely complex or highly variable — the kind of job no one model is equally good at end to end.

---

## 4. The Six Types of Agents

Understanding these types helps you design the right agent for the job — from simple automation to complex decision-making. They form a rough ladder of increasing sophistication.

**1. Simple Reflex Agent** — decides based only on the *current* input, with no memory of history.
> **Example:** ask "tell me a joke," it tells a joke. Ask "can you repeat the joke?" and it has no idea what you mean — it never stored the first exchange. One perception, one condition, one action, nothing carried forward.

**2. Stateful (Model-Based) Agent** — maintains an internal model of the world, tracking state across a conversation and updating it with each new input.
> **Example:** ask "what is the capital of France?" → "Paris." Then ask "can you tell me its population?" → "around 2.1 million." The agent carried "France" and "Paris" forward from the first exchange to make sense of "its" in the second.

**3. Goal-Based Agent** — evaluates potential actions against whether they move toward a specific objective, considering future states, not just the current one.
> **Example:** booking a flight. User: *"I need a flight from New York to London tomorrow."* Agent: *"What time?"* User: *"Evening."* Agent: *"There's a 7pm flight available — want me to book it?"* Every question the agent asks is in service of the one goal: getting that booking done.

**4. Utility-Based Agent** — uses a utility function to weigh and prioritize actions, aiming to maximize overall usefulness when there are competing objectives.
> **Example:** a support assistant handling *"I'm frustrated that my account was deactivated."* It weighs options — apologize and escalate to a human, reactivate immediately, offer a discount — and picks whichever combination scores highest for user satisfaction: *"I'm very sorry — let me reactivate your account immediately, and I'll add a $10 credit for the inconvenience."*

**5. Learning Agent** — improves over time from past experience, via four components: a **learning element** (updates knowledge from feedback), a **performance element** (makes decisions from current knowledge), a **critic** (evaluates how actions turned out), and a **problem generator** (suggests exploratory actions to try).
> **Example:** this is exactly what's happening when ChatGPT asks *"which response do you prefer?"* — that's the critic gathering feedback the learning element will use.

**6. Hierarchical Agent System** — divides a task into subtasks handled by different agents at different layers, simplifying complex problems and improving modularity.
> **Example:** a marketing-campaign content generator with four agents in sequence — one picks the topic, one plans the content, one writes it based on that plan, and one does quality control, reviewing the output for errors and coherence.

> 🪜 **How the six connect:** reflex agents have no memory; stateful agents add memory; goal-based agents add a target to work toward; utility-based agents add a way to weigh *competing* targets; learning agents add the ability to improve over time; and hierarchical systems are what you get when a job is big enough to split across *several* agents, each possibly using any of the five approaches above internally.

---

## 5. Building an AI Agent

Five steps, from the session's closing walkthrough:

1. **Define your objective** — what will this agent actually do?
2. **Choose a framework** — tools like LangChain, AutoGPT, or the OpenAI APIs.
3. **Integrate tools** — APIs, databases, or other external systems the agent needs to interact with.
4. **Develop and test** — build it, then test the agent's results across a real test set.
5. **Iterate** — refine the agent based on what testing shows.

---

## Key Takeaways

1. **An agent acts; a chatbot answers.** Perception → reasoning → action → learning is the loop that makes something an agent rather than a static Q&A system.
2. **RAG and agents solve different problems** — RAG makes a model know more, an agent makes it do more, and the two are complementary, not competing.
3. **Single-LLM agents trade capability for simplicity; multi-LLM agents trade simplicity for capability** — pick based on how narrow or complex the actual job is.
4. **The six agent types form a ladder of sophistication** — memory, then goals, then weighing competing goals, then learning, then splitting the whole job across multiple agents.
5. **Building one is a five-step loop, not a one-shot build** — define, choose a framework, integrate tools, test, and iterate.

---

## 🎤 Interview Prep — Mock Interview (AI Agent Fundamentals)

*Same two-layer format as the other Video Notes files in this repo: a plain-language answer with an example, then a crisp, technically precise version. Try answering out loud first.*

---

**🎙️ Interview Q1:** "What's the actual difference between an AI agent and a RAG system — aren't they both just 'LLM plus extra stuff'?"

**✅ Strong answer:** "They both extend a plain LLM, but in different directions. RAG extends what the model *knows* — it retrieves relevant documents and feeds them in so the answer is grounded in real information. An agent extends what the model can *do* — it reasons about a task, decides on an action, and actually goes and performs it through a tool or API, possibly across several steps. A RAG system is like an encyclopedia with superpowers: better answers from better knowledge. An agent is more like a Swiss Army knife: it doesn't just know things, it does things."

**🎯 Standard Interview Answer:** "RAG and agents both compensate for a frozen LLM's limitations, but along different axes. RAG augments the *generation* step with retrieved, domain-specific context from a static knowledge base — it's fundamentally about information augmentation. Agentic systems augment the *decision* step — the LLM plans, reasons, and iteratively invokes tools or APIs to accomplish a task, which may span multiple steps and real-world side effects. In practice, many production agents use RAG internally as one of their tools, rather than the two being mutually exclusive architectures."

---

**🎙️ Interview Q2:** "When would you choose a single-LLM agent over a multi-LLM agent, and what's the real cost of getting that choice wrong?"

**✅ Strong answer:** "Single-LLM makes sense when the job is narrow and well-defined — a support bot that just needs to look things up in one database, where simplicity and low cost matter more than flexibility. Multi-LLM makes sense when the workflow is genuinely varied — content creation needing ideation, editing, and SEO optimization, each better suited to a differently-tuned model or role. Getting it wrong in one direction means over-engineering a simple bot with unnecessary orchestration complexity and latency; getting it wrong the other way means a single model straining to do a job it was never well-suited for, with no way to specialize."

**🎯 Standard Interview Answer:** "The decision hinges on task variability and complexity. Single-LLM agents minimize architectural complexity and cost but are bounded by that one model's capability profile — fine for narrow, consistent workloads. Multi-LLM agents introduce orchestration (sequential handoff or a central router) that lets each sub-task go to a specialized model, at the cost of higher infrastructure requirements and coordination latency. Over-applying multi-LLM orchestration to a simple task is a common anti-pattern — it adds failure surface and latency without a corresponding capability gain."

---

**🎙️ Interview Q3:** "Walk me through the difference between a goal-based agent and a utility-based agent — isn't 'achieving a goal' always about maximizing something?"

**✅ Strong answer:** "A goal-based agent is working toward one target and evaluates actions purely on whether they move it closer — like a flight-booking assistant chasing down destination, time, and options until the booking is made. A utility-based agent comes in when there isn't just one clean goal, but several *competing* ones that have to be weighed against each other. The account-deactivation example is the clearest case: the agent isn't just picking 'the' response, it's weighing apologizing, escalating to a human, and offering a discount against each other to find whichever combination scores highest for actual user satisfaction. Goal-based is 'do I reach the target,' utility-based is 'which path best balances several targets at once.'"

**🎯 Standard Interview Answer:** "Goal-based agents perform binary-style evaluation of actions against a defined goal state, considering future states but along essentially one dimension. Utility-based agents add a scalar utility function that scores actions across multiple, potentially conflicting objectives, enabling explicit trade-off management — this is what's required whenever 'success' isn't a single achievable state but a balance between competing outcomes, such as user satisfaction versus cost versus resolution speed in a support scenario."

---

**Sources consulted while calibrating this section:** none beyond the session's own transcript and its companion reading (*Introduction to Agents.pdf*) — this session is foundational/definitional rather than claim-heavy, so no external verification was needed the way the production-RAG sessions required.

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

### Q1: How would you differentiate a RAG pipeline from an agent, and where would you use each?

**RAG pipeline = fixed steps, decided by you. Agent = variable steps, decided by the LLM at runtime.**

A RAG pipeline sends every query down the identical path — retrieve → (rerank) → generate → done. One retrieval, one answer, always the same shape. You wrote the sequence; the LLM just fills in the final text. An agent instead looks at the question, picks a tool, sees the result, and *then* decides what to do next — so different questions take different numbers of steps, and you don't know how many in advance.

**Example — the same question to both: "Is our Q3 revenue above target?"**

| | What happens |
|---|---|
| **RAG pipeline** | Searches the docs once, finds a chunk mentioning Q3 revenue, answers from it. If the target figure lives in a *different* document, it never finds it and answers incompletely — it only ever gets one shot. |
| **Agent** | Queries the revenue database → sees the number → realises it still needs the target → queries the targets doc → compares → *then* answers. Three steps here; a simpler question might take one. |

**Where each belongs:** RAG when the shape of the work is predictable (Q&A over documents, support-article lookup) — cheaper, faster, debuggable. Agent when you genuinely can't pre-plan the steps (multi-hop questions, several tools, retry-until-right loops). The rule of thumb is to reach for an agent only once a fixed pipeline has actually failed you, since agents are strictly more expensive, slower, and harder to debug.

**One line:** RAG answers "what does my knowledge base say about X" with a fixed pipeline; an agent answers "go figure X out" by choosing its own steps — and an agent very often uses RAG as one of those steps.

---

### Q2: In a multi-agent system, could one agent be a RAG pipeline itself?

**✅ Correct.** One specialist agent can be an entire RAG pipeline wrapped as a single node — the supervisor routes to it like any other agent, without caring that retrieval, reranking, and generation are all happening inside it.

This is the same point as the LangGraph material in *LangChain.md* (Interview Q13 follow-up): a node can hide one LLM call *or* a whole compiled sub-graph, and the supervisor routes at node granularity either way. The Legal Query Resolution system from Week 3 is exactly this shape — RAG at its core, with agentic components (confidence-gated routing, query decomposition) layered on top, which is why it was described honestly as *"a RAG system with agentic components, not a fully autonomous agent."*

**One line:** yes — from the supervisor's point of view a RAG pipeline is just one more node to route to, and hiding a whole pipeline behind a single node is the normal way multi-agent systems are built.

---

### Q3: In the four-component breakdown above, what does "learning is getting better at it next time" actually mean?

**It means the agent changes its future behaviour based on how past attempts turned out** — the same request handled better the second time because the first attempt taught it something.

**Example:** when ChatGPT shows two responses and asks *"which do you prefer?"*, that click is feedback. It does nothing for your current answer — it feeds a training loop so similar requests go better later. That's the learning component in action, and it's the same *critic* role described in the Learning Agent above.

Contrast with the other three components, which are all about *this* request: perceive it, decide, act. Learning is the only one pointed at the *next* request.

**⚠️ The honest caveat:** of the four components, learning is by far the weakest in real production agents. Most systems you'll actually build perceive, reason, and act — but don't genuinely learn, because they don't update weights between requests. What usually gets *called* learning in practice is much shallower: writing to memory so context carries forward, logging thumbs-down signals for humans to review, or a human retraining later on collected feedback.

**One line:** learning is the only one of the four components aimed at future requests rather than the current one — real in research and feedback pipelines, but mostly aspirational in the agents you'd ship today.

---

### Q4: For an interview — is "fixed/deterministic path → RAG, non-deterministic path → agentic" the right framing?

**✅ Correct, and it's the distinction interviewers are actually testing.** The *pieces* are predefined in both cases; what differs is **who decides the order** — you (pipeline) or the LLM at runtime (agent).

Two sharpenings worth adding, since the concept is already right:

- **Use the precise vocabulary:** static vs. **dynamic control flow**. A RAG pipeline is a **DAG** — it moves forward only, never loops back. An agent has **cycles and conditional branching**, which is exactly why it needs an explicit termination condition.
- **Say "the *path* is deterministic," not "it's deterministic."** RAG's generation step is still stochastic; only the control flow is fixed.

**One line:** the framing is right — just land it as "static vs. dynamic control flow, a DAG versus a stateful graph with cycles," which is the wording the interviewer is listening for.

---

### Q5: In a RAG system built on LangGraph, a conditional edge like "if relevance score < 0.6 → web search" — is that agentic, or still deterministic?

**✅ Still deterministic — and spotting that is a genuinely sharp distinction.** Branching and adaptive-*looking*, but not agentic: a human picked 0.60, and the same score always routes the same way.

The cleanest way to see it: **both cases use a conditional edge** — the difference is only *what's inside the routing function*.

```
Routing function contains:
  if score < 0.6: return "web_search"     ← plain Python  = deterministic routing
  else:           return "generate"

  llm.invoke("which node next?")          ← an LLM call   = agentic routing
```

Same mechanism, same graph, same `add_conditional_edges`. Only the decision-maker changes — a coded rule, or a model reasoning about it. This is why "pipeline vs. agent" is a spectrum rather than a switch, and the Legal Query Resolution system's τ = 0.60 confidence gate is exactly the deterministic side of it.

**Worth adding to the mental model:** even when the LLM *does* decide, it almost always picks from a **predefined list of nodes** via structured output — not open-ended invention. "The LLM decides" means it chooses among paths you already built, which is why the supervisor pattern returns a schema-constrained value rather than free text.

**One line:** deterministic routing is a coded rule inside the conditional edge, agentic routing is an LLM call inside that same edge — and real systems mix both in one graph.

---

### Q6: What is CrewAI, and how is it different from LangGraph for building agents?

**CrewAI = you describe a team; it runs them. LangGraph = you draw the flowchart; it follows it.**

CrewAI is built around one metaphor — a *crew of coworkers*. You define **Agents** (each with a role, goal, and backstory), **Tasks** (what needs doing, and which agent does it), and a **Crew** (the team plus a process: sequential or hierarchical). Then `kickoff()` handles the handoffs.

```python
# CrewAI — you declare WHO and WHAT, not the flow
researcher = Agent(role="Market Researcher", goal="Find EV market data", backstory="...")
writer     = Agent(role="Report Writer",     goal="Turn findings into a report", backstory="...")

t1 = Task(description="Research the EV market", agent=researcher)
t2 = Task(description="Write a summary report", agent=writer)

Crew(agents=[researcher, writer], tasks=[t1, t2], process=Process.sequential).kickoff()
```

Notice what's missing: you never wrote "after t1, go to t2." The process handles sequencing. LangGraph makes you draw every arrow — which is the whole point:

```python
# LangGraph — you declare the FLOW explicitly
graph.add_node("research", research_fn)
graph.add_node("write", write_fn)
graph.add_edge("research", "write")
graph.add_conditional_edges("write", check_quality, {"retry": "research", "done": END})
```

| | CrewAI | LangGraph |
|---|---|---|
| You define | Roles + tasks | State + nodes + edges |
| Control flow | Framework decides handoffs | You decide, explicitly |
| Loops / retries | Awkward | Native — cycles are the point |
| Conditional routing (`if score < 0.6`) | Hard to express | Exactly what conditional edges are for |
| Human-in-the-loop, resume after crash | Limited | Built in (checkpointers, interrupts) |
| Speed to build | Fast | Slower, more verbose |
| Debuggability | More opaque | State inspectable at every step |

**Where each fits:** CrewAI when the shape genuinely *is* a team of specialists passing work along in order — the Market Research Copilot (planner → executor) and the blog generator are exactly this. LangGraph the moment you need cycles, retries, confidence-gated routing, or approval pauses — which is why Legal Query Resolution is LangGraph.

**One line:** CrewAI trades control for speed by hiding orchestration behind a role/task metaphor; LangGraph trades speed for control by making you write the graph.

---

### Q7: If the flow is straight, why not just use LangChain instead of CrewAI?

**"Straight flow" alone doesn't justify CrewAI — the missing variable is what happens *inside* each step.**

- **LCEL chain:** straight flow, and each step is **one deterministic call** — prompt → model → parse. A step can't choose a tool or decide to try again.
- **CrewAI:** straight flow *between* agents, but each agent is **autonomous inside** — it picks which tools to call, how many times, and when it's done.

**Example — "research the EV market and write a report":** with an LCEL chain you must hardcode the research (run *these 3 searches*, feed results into a summarize prompt). If one topic needs 3 searches and another needs 8, the chain can't adapt — you baked the number in. With CrewAI, the researcher agent gets a *goal* and a search tool, and decides for itself how many queries to run and when it has enough. The handoff is straight; the work inside isn't.

**So the ladder has four rungs, not two:**

| Use | When |
|---|---|
| **LCEL chain** | Straight flow, every step is one fixed call — *summarize this document* |
| **Single agent** (`create_agent`) | One worker that picks tools and loops — *answer this, using search + calculator* |
| **CrewAI** | Several *specialists* handing off in order, each agentic internally — *research → analyze → write* |
| **LangGraph** | The flow *between* them must loop back, branch on a condition, or pause for a human |

**❌ One correction worth burning in, because it would draw a flag in an interview:** it is *wrong* to say "LangChain has no agents, it's just a pipeline." **LangChain has agents** — that's exactly what `create_agent` is (and `AgentExecutor` before it was deprecated). A LangChain agent picks its own tools, reads results, and loops until done. The valid contrast is **LCEL chain vs. CrewAI agent**, not *LangChain* vs. CrewAI.

So what does CrewAI actually add over a LangChain agent? Not the reasoning — the **team abstraction**: roles, goals, backstories, and handoff plumbing between *several* agents. You could wire three `create_agent` calls together and get the same result with more boilerplate. That's ergonomics, not capability.

**One line:** LCEL when each step is a fixed call; CrewAI when each step must be an autonomous specialist but the handoffs stay linear; LangGraph when the handoffs themselves need to branch or loop — and never claim LangChain can't do agents, because it can.

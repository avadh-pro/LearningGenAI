# Core Components of an AI Agent

**Guided Project in AI Agents**
*TMLC Academy*

## TABLE OF CONTENTS

01. OVERVIEW
02. LEARNING OBJECTIVES
03. WHAT IS AN AI AGENT?
04. CORE COMPONENTS OF AN AI AGENT
05. AI AGENT ARCHITECTURE DIAGRAM
06. EXAMPLE: CHAT-BASED AI AGENT
07. ADVANCED INSIGHTS
08. SUMMARY
09. REFERENCES

---

## 01. OVERVIEW

Every intelligent agent, from a simple rule-based chatbot to a complex autonomous multi-agent system, is built upon a set of **core components** that allow it to perceive, reason, learn, and act within its environment.

These components work together to create a continuous **sense–think–act loop**, enabling the agent to interpret incoming data, make informed decisions, and perform actions that achieve defined goals.

In this module, we explore these foundational building blocks that define **how AI agents operate, interact, and evolve**, whether in traditional symbolic AI systems, reinforcement learning environments, or modern LLM-based agentic workflows.

By mastering these concepts, you will be able to **design structured, modular, and scalable agent architectures** that are explainable, reusable, and adaptable across industries such as customer support, process automation, healthcare, manufacturing, and finance.

---

## 02. LEARNING OBJECTIVES

By the end of this module, you will be able to:

- Identify and describe the **core components** that make up an AI agent.
- Explain how the **flow of information** moves between perception, reasoning, memory, and action.
- Understand how **environment, sensors, and actuators** work in coordination to create an intelligent feedback loop.
- Map these theoretical components to **real-world agent architectures**, from classical rule-based systems to LLM-driven autonomous agents.
- Evaluate how **learning, memory, and performance measures** enhance agent intelligence and adaptability.
- Establish design principles for creating **modular and composable agent frameworks** using tools such as LangChain, LangGraph, CrewAI, or custom orchestrators.

---

## 03. WHAT IS AN AI AGENT?

An **AI Agent** is an autonomous or semi-autonomous entity that can:

1. **Perceive** its environment through inputs or sensors,
2. **Reason or decide** what action to take based on its internal model, rules, or goals, and
3. **Act** upon the environment using actuators or output mechanisms.

This continuous cycle, **Perceive → Think → Act**, forms the fundamental operational loop of any AI system.

In advanced setups, agents may also:

- **Learn** from their experiences (Learning Component),
- **Communicate** with other agents (in multi-agent systems), and
- **Adapt** their strategies dynamically based on feedback or performance scores.

**Real-World Examples**

- A **chatbot** perceives user text, reasons using NLP or LLM logic, and acts by replying with text output.
- A **self-driving car** perceives the environment through cameras and LiDAR, reasons using AI models, and acts by controlling acceleration or steering.
- A **business process automation agent** perceives structured data, reasons through business rules, and acts by triggering APIs or workflow updates.

---

## 04. CORE COMPONENTS OF AN AI AGENT

Each AI agent, regardless of complexity, is composed of several interdependent components that define how it interacts with its environment and makes intelligent decisions.

| Component | Description | Detailed Explanation & Examples |
| --- | --- | --- |
| **1. Environment** | The external world in which the agent operates. It provides data and feedback, and receives the agent's actions. | The environment can be static (unchanging), dynamic (changes over time), discrete (turn-based), or continuous (real-time). Examples: In a chatbot, the environment is the ongoing conversation context. In a trading agent, it is the financial market data stream. In robotics, it is the physical worldsensed through devices. |
| **2. Sensors (Perception)** | Mechanisms that allow the agent to sense or receive input from the environment. | Sensors capture percepts, which are structured or unstructured information about the environment. For a chatbot: text input, voice-to-text, or API signals. For an AI support bot: WhatsApp message payloads or ticketing data. For an industrial robot: temperature, pressure, or camera feed. |
| **3. Knowledge Base / Memory** | A structured repository that stores information, experiences, or rules used by the agent to make decisions. | Memory can be short-term (conversation context or working memory) or long-term (facts, embeddings, or fine-tuned model weights). Example: a retrieval database such as FAISS or Chroma used by LLM agents to recall prior knowledge. In classic AI: a rule table or ontology. |
| **4. Reasoning / Decision-Making Engine** | The agent's brain responsible for interpreting inputs, evaluating possible actions, and selecting the most appropriate response. | This component transforms perception into action using logic, algorithms, or learned models. Approaches include: rule-based inference (IF–THEN rules), search algorithms (A*, Minimax), machine learning classifiers, LLM reasoning and prompt orchestration, or reinforcement learning for continuous control. |
| **5. Learning Component (Optional)** | Enables the agent to improve its performance over time using new data, experiences, or rewards. | This component distinguishes intelligent agents from static automation. Learning can be supervised (learns from labeled examples), reinforcement-based (learns via trial, error, and reward signals), or few-shot / in-context learning (as in LLM agents). Example: an AI assistant that refines its recommendations using user feedback. |
| **6. Actuators (Actions)** | The output channels through which the agent interacts or influences its environment. | Actuators translate the agent's decisions into tangible actions. Examples: text or voice responses in a chatbot, API calls in workflow automation, mechanical control in a robot arm, or GUI actions in a software bot (clicks, form submissions). |
| **7. Performance Measure (Goal / Utility Function)** | Defines the success criteria that evaluate how effectively the agent is achieving its goals. | This could be an explicit metric (accuracy, reward) or an implicit objective (user satisfaction, minimal error). In reinforcement learning, this is a reward score. In dialogue systems, it is user satisfaction rating. In predictive agents, it is precision, recall, or latency. |

---

## 05. AI AGENT ARCHITECTURE DIAGRAM

This diagram represents a **closed feedback loop** where the outcome of each action influences future perceptions and decisions, forming an adaptive, learning-driven system.

```
                    ┌─────────────────┐
                    │   Environment   │
                    └────────┬────────┘
                             │
                      ( Percepts / Inputs )
                             │
                             ▼
    ┌────────────────────────────────────────────────────┐
    │                      Agent                         │
    │                                                    │
    │        ┌─────────────────────┐                     │
    │        │      Sensors        │ ------> Capture Inputs
    │        └──────────┬──────────┘                     │
    │                   │                                │
    │                   ▼                                │
    │  ┌──────────────────────────────────┐              │
    │  │  Reasoning / Decision Engine     │              │
    │  └──────────────┬───────────────────┘              │
    │                 │                                  │
    │                 ▼                                  │
    │  ┌──────────────────────────────────┐              │
    │  │  Knowledge Base / Learning       │ <------ Memory
    │  └──────────────┬───────────────────┘              │
    │                 │                                  │
    │                 ▼                                  │
    │        ┌─────────────────────┐                     │
    │        │      Actuators      │ <------ Execute Actions
    │        └─────────────────────┘                     │
    │                                                    │
    └────────────────────────┬───────────────────────────┘
                             │
                             ▼
                    ( Actions / Outputs )
```

---

## 06. EXAMPLE: CHAT-BASED AI AGENT

Let's map the components to a real-world customer support chatbot:

| Component | Chatbot Example | Detailed Notes |
| --- | --- | --- |
| **Environment** | The user conversation | The evolving dialogue acts as the agent's environment, providing continuous context that influences subsequent responses. |
| **Sensors (Perception)** | User messages (text input) | The chatbot receives input through APIs such as WhatsApp or web chat, or speech recognition modules. |
| **Knowledge Base / Memory** | FAQs, product database, vector embeddings | Stores company information, prior chat history, and contextual embeddings to generate accurate and relevant answers. |
| **Reasoning Engine** | Rule-based logic or LLM (e.g., GPT-4, Claude, Gemini) | Interprets queries, selects relevant data from memory, and generates an appropriate response. |
| **Learning Component** | Reinforcement learning from feedback | Continuously improves using satisfaction scores, user ratings, or retraining based on logs. |
| **Actuators** | Chat interface, API response | Outputs text to the chat UI or triggers workflow automation such as booking creation or ticket updates. |
| **Performance Measure** | Accuracy, user satisfaction, response time | Evaluates how effectively the chatbot meets business and user goals. |

---

## 07. ADVANCED INSIGHTS

**Reactive vs. Deliberative Agents:**
Reactive agents respond directly to stimuli, while deliberative agents maintain internal models to plan future actions.

**Single-Agent vs. Multi-Agent Systems:**
In multi-agent environments, agents may cooperate, compete, or negotiate to achieve shared or individual goals.

**Memory-Augmented LLM Agents:**
Modern LLM-based agents use vector databases such as FAISS, Pinecone, or Chroma as long-term memory to recall facts, context, and previous interactions.

**Memory-Augmented LLM Agents:**
Agents can be goal-driven (explicit objectives), utility-based (maximize expected utility), or hybrid (weighted multi-objective optimization).

---

## 08. SUMMARY

- Every AI agent follows the **Perceive → Reason → Act** cycle.
- The seven core components (Environment, Sensors, Memory, Reasoning Engine, Learning, Actuators, and Performance Measure) define how an agent interacts with the world.
- These components form a modular structure that supports extensibility, debugging, and scaling to multi-agent ecosystems.
- Understanding these foundations prepares you to design advanced **LLM-driven agentic workflows**, integrate memory stores, and orchestrate actions intelligently using frameworks like **LangGraph, CrewAI, or OpenDevin.**

---

## 09. REFERENCES

1. Russell, S. & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson Education.
2. Wooldridge, M. (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.
3. IBM Research AI (2023). *Understanding AI Agents: Architecture and Components.*
4. LangChain Documentation (2024). *Understanding Agent Architectures in LLM Systems.*
5. OpenAI Technical Report (2023). *Language Models as Autonomous Agents.*

---

# Q&A

*Discussion notes recorded while working through this document. Everything above this line is the original PDF content, unchanged.*

---

### Q1. Explain how the flow of information moves between perception, reasoning, memory, and action.

*(Relates to: Section 02 — Learning Objectives, bullet 2; and Section 05 — Architecture Diagram)*

**One line:** Perception takes the world in, memory supplies what you already know, reasoning decides using both, action changes the world — and that change becomes the next perception.

**The everyday example — driving up to a traffic light:**

| Step | What happens |
| --- | --- |
| **Perception** | Your eyes see a red glow ahead. Raw input, no meaning attached yet. |
| **Memory** | You already know *red = stop*. You didn't work that out now; you learned it years ago. |
| **Reasoning** | Combine the two → "that's a red light, I should brake." |
| **Action** | Your foot presses the brake. The world actually changes. |
| **Back to perception** | The car slows, you see the speedometer drop — new input, and the loop runs again. |

None of the four is skippable: eyes without memory see a meaningless glow, memory without eyes has nothing to apply, and reasoning without action changes nothing.

**The same thing in the chatbot from Section 06:**

- **Perception** — the user types *"Where's my order?"*
- **Memory** — pulls up their order history and the FAQ on shipping.
- **Reasoning** — the LLM reads both and decides to answer with the tracking status.
- **Action** — sends the reply, and may also call the courier API.
- **Loop** — the user's next message is shaped by that reply.

**⚠️ One place the Section 05 diagram is slightly misleading**

The diagram draws a straight line: `Sensors → Reasoning → Knowledge Base → Actuators`. That reads as though memory comes *after* thinking.

In reality **memory sits beside reasoning, not after it.** Reasoning *reads from* memory to decide, and *writes back to* memory afterwards. It is a notebook on the desk, not a station on a conveyor belt:

```
Perception ──► Reasoning ──► Action
                  ▲ │
                  │ ▼
               Memory
            (read + write)
```

That is why a chatbot remembers what you said three messages ago — reasoning wrote it down, and reads it back on the next turn.

---

### Q2. (Follow-up to Q1) "So there are four stages: perception, memory, reasoning, action — and the action becomes the next perception. Perception is raw input, you don't yet know the next step; you infer it by looking into memory, so memory plus perception becomes the input to the reasoning model, and based on the reasoning you take the next step. Correct me if I'm wrong."

**✅ Correct** — the mechanics described are right, and the key part is exactly right: **memory + perception together form the input to reasoning.**

**One nudge:** memory isn't a *stage* you pass through. It's a store that reasoning reads from and writes back to. So it's really **three stages in the chain — perception → reasoning → action — with memory feeding reasoning from the side.**

The distinction matters in practice: you don't "visit" memory between perceiving and thinking. Reasoning decides *what* to look up and pulls only that. The chatbot doesn't load your entire order history on every message — the reasoning step decides "I need this user's last order" and retrieves just that.

**One line:** Right on the flow, but memory is a side-store reasoning consults, not a step in the line.

---

### Q3. Explain each core component with a real-world use case, in the easiest possible manner.

*(Relates to: Section 04 — Core Components of an AI Agent)*

One running example is used throughout so the pieces connect: a **food-delivery refund agent**.

**1. Environment — *the world the agent works in***
Whatever the agent affects and gets feedback from.
- *Everyday picture:* a taxi driver's environment is the road — traffic, signals, weather.
- *Real use case:* the live order system — order status, delivery timestamps, the customer's chat window.

**2. Sensors (Perception) — *how it takes input in***
The channels through which the world reaches the agent.
- *Everyday picture:* your eyes and ears.
- *Real use case:* the customer types *"food arrived cold"*; the agent also receives the order ID and delivery time from the API. Text + data = its senses.

**3. Knowledge Base / Memory — *what it already knows***
Stored facts, past experience, and rules it can look up.
- *Everyday picture:* a doctor's memory of medicine, plus your file on their desk.
- *Real use case:* the refund policy document, this customer's past 20 orders, and whether they have claimed 5 refunds this month.

**4. Reasoning / Decision Engine — *the brain***
Takes perception + memory and decides what to do.
- *Everyday picture:* the doctor thinking "these symptoms + this history = this diagnosis."
- *Real use case:* "Food was 40 minutes late, policy allows a refund, this customer is not a repeat abuser → approve the refund."

**5. Learning Component — *how it gets better***
Improves from feedback instead of staying frozen.
- *Everyday picture:* a new driver who slowly learns which lane jams at 6pm.
- *Real use case:* the agent notices refunds it approved for "cold food" get reversed by managers 70% of the time, and starts asking for a photo first.
- *Why the document marks it optional:* an agent works without it — it just never improves.

**6. Actuators — *how it actually does things***
The output channels that change the world.
- *Everyday picture:* your hands and voice. Thinking "pass the salt" does nothing; reaching does.
- *Real use case:* sends the reply message **and** calls the payments API to credit the refund. The API call is the real action — the message is just narration.

**7. Performance Measure — *how you score it***
The definition of "doing well."
- *Everyday picture:* a student's exam marks — without them, "studying hard" is unmeasurable.
- *Real use case:* % of refunds resolved without a human, customer satisfaction, and money wrongly refunded. These **fight each other** — approving every refund makes customers happy and bankrupts the business. That tension is the whole reason the measure exists.

**All seven in one sentence:**

> The customer complains in the chat *(environment)*, the agent reads the message and order data *(sensors)*, looks up the refund policy and their history *(memory)*, decides it qualifies *(reasoning)*, credits the money via API *(actuators)*, gets scored on resolution rate and wrongful refunds *(performance measure)*, and adjusts its behaviour from those scores over time *(learning)*.

**The one that trips people up:** reasoning gets called "the agent," but it is only one of the seven. An LLM with no tools is *just* reasoning — it can decide to refund you, but it cannot actually move the money.

**One line:** Actuators are what separate an agent from a chatbot.

---

### Q4. If you had to rename each core component in layman terms, what would you call them?

*(Relates to: Section 04 — Core Components of an AI Agent. Recall aid.)*

One consistent picture holds all seven together: **a new employee on their first job.**

| Textbook name | Layman name | Why it fits |
| --- | --- | --- |
| **Environment** | **The workplace** | The place they work and the things they can affect. |
| **Sensors (Perception)** | **Eyes and ears** | How the outside world reaches them. |
| **Knowledge Base / Memory** | **The handbook + their notebook** | Handbook = rules given to them. Notebook = what they have picked up since. |
| **Reasoning Engine** | **The brain** | Where "what should I do here?" gets answered. |
| **Learning Component** | **Experience** | Why a 5-year employee beats a day-one one. |
| **Actuators** | **Hands** | Thinking does not move anything; hands do. |
| **Performance Measure** | **The appraisal** | How the boss decides if they are actually good. |

**The recall sentence:**

> A new employee at a workplace uses **eyes and ears** to notice things, a **handbook and notebook** to know things, a **brain** to decide, **hands** to act, an **appraisal** to be judged, and **experience** to get better.

**Two worth locking in:**

1. **Memory splits in two.** Handbook = given to it (refund policy, FAQs). Notebook = accumulated (this customer complained twice last month). In LLM terms: the handbook is your retrieval corpus, the notebook is conversation / long-term memory.
2. **Hands are the dividing line.** An employee who can only *talk* is an advisor; one who can actually *do* things is an agent. Same with LLMs — this is the same point as Q3's closing line.

**One line:** Workplace, eyes and ears, handbook and notebook, brain, hands, appraisal, experience.

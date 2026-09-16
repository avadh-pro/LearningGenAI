# AI Agents: An Introduction — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [AI Agents: An Introduction](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/61998704-ai-agents-an-introduction)
> · Video lesson, 11 min (`0:11:13`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:00]

Hello all. Welcome to this session on AI agents where we will explore what they are, how they work
and their exciting applications in the world of AI. AI agents go beyond traditional automation by
combining adaptability, learning and decision making. Think of them as digital beings capable of
understanding their environment and acting intelligently. For instance, a traditional chatbot
provides static answers. Whereas an AI agent analyzes the context, retrieves information and acts on
your behalf. Whether that's booking flights, drafting emails or optimizing processes. Let's dissect
what makes an AI agent. First thing is perception, how agent collects the data using API sensors or
text input or then there can be many more. Second is reasoning. In reasoning, decision making using
machine learning, rule-based system or combination of both. Third is action, performing tasks by
interacting with external systems like databases or tools. And fourth is learning, adopting from
feedback to get smarter. This is a breakdown of an AI agent. Now, what's the difference between AI
agents and systems like RAG? While both leverage LLMs, they serve distinct purpose. The core purpose
of RAG is that it enhances generative responses with retrieved knowledge. Whereas AI agent solves
tasks requiring reasoning and interaction. Mechanism wise, RAG combines retrieval with generative
model and AI agents iteratively plans reasons and interacts with tools, even RAG.

### [2:05]

One of the examples of RAGs is search enhanced chatbots. Whereas example of AI agents can be
workflow automation tools. When building AI agents, you can choose between single LLM agents and
multi-LLM agents. To simply put, it's more like in single agent LLMs or single LLM agents, one
single agent is working in multiple LLM agents, multi-agents working. A single LLM agent uses one
language model for all the tasks. Example, a chatbot powered by GPT-4 that answers customer queries.
The advantages of single LLM agents are simplicity, lower cost and focused performance. Also, it has
some challenges like limited adaptability for diverse or complex workflows. A multi-LLM agent, on
the other hand, orchestrates multiple models, each specializing in its task. Example, a content
creation tool with models for idea generation, grammar refinement and SEO optimization. The
advantages of multi-LLM agents are scalability, specialization and flexibility. Whereas the
challenges are for higher complexity, resource requirement and potential latency. Now, let's look at
the types of agents. Understanding these types of agents helps us to design better AI systems for
everything from simple automation to complex decision making. Starting with simple reflex agent.
Simple reflex agents are based solely on the current percept. They do not consider the history of
previous states and don't store any memory. These agents takes rule-based decisions and they don't
have memory.

### [4:07]

They are based solely on the current percept. They do not consider the history of previous states
and don't store any memory. These agents takes rule-based decisions and they don't have memory or
learning capabilities. Example is, when user inputs tell me a joke, the chatbot responds by telling
a joke. The limitation is, if the user asks, can you repeat the joke, it won't remember the previous
interaction. Simply, it's more of a single perception, single condition and single action. Now,
coming to the second type, stateful memory agent. These agents maintain an internal model of the
world, allowing them to track state of the environment and make decision accordingly. Their
characteristics are, they maintain memory of previous states, also updates its model with each new
percept. Example, a conversational AI system that maintains a context window, where if the
conversation starts like, what is the capital of France? The model will respond, the capital of
France is Paris. And when again the user will ask, can you tell me its population? The model will
respond, the population of Paris is around 2.1 million. Here, you can clearly see that the agent
takes reference from its prior context, that is France and Paris, to provide a relevant response.
Then coming to the third type, goal-based agent. Goal-based agents are designed to achieve specific
objectives. They evaluate potential actions based on whether they helped achieve a given goal. Their
characteristics are, they require knowledge of goals and consider future states as well.

### [6:16]

Example is a task-oriented chatbot helping a user book a flight. Here is an example of the
conversation. When user asks, I need to book a flight from New York to London for tomorrow. Then it
responds with, what time would you like to depart? And then user responds with evening. And after
that, LLM responds with, there's a flight at 7pm with availability, would you like me to book it?
The LLM evaluates intermediate steps, destination, time, flight options to achieve the goal, that's
booking a flight. So this is goal-based agent. Then there's utility-based agent. These agents use a
utility function to evaluate and prioritize actions aiming to maximize overall usefulness of an
outcome. Characteristics are, they balance trade-offs and also work well in scenarios with multiple
competing objectives. Example, a customer support assistant prioritizing user satisfaction. When
user says, I'm frustrated that my account was deactivated. LLM evaluates possible responses, that
is, apologize and escalate to a human or provide instruction to reactivate the account, station or a
discount. It selects the response with the highest predicted satisfaction. I'm very sorry to hear
that, let me reactivate your account immediately. I will also add a $10 credit for the
inconvenience. Learning agents improve their performance over time by learning from past
experiences. The components are learning element that is used to update knowledge based on the
feedback.

### [8:23]

Then there is performance element. It makes decisions based on the current knowledge. There's
critics, which evaluates actions and a problem generator. Suggest exploratory actions. Example,
chatbots improving through user interaction. Remember how chatgpt asks for which answer you prefer.
Hierarchical agent system. Hierarchical agents divide tasks into smaller subtasks and assign them to
different layers or agents within a hierarchy. The advantages are it simplifies complex problems and
also it enhances modularity and efficiency. Some of the examples of hierarchical agent systems are
topic generator agent. An example of hierarchical agent system is a hierarchical content generation
system for creating marketing campaign where one agent is dedicated for topic generation. Second
agent is dedicated to plan the content. Third agent, which writes content according to the earlier
planned content by earlier agent. Then fourth agent, which is used for quality control, which mostly
reviews the generated content for errors and coherence. In short, in hierarchical agent system, the
agents work in certain hierarchy. Now building AI agents. Building an AI agent involves several
steps. First, define your objective. What will your agent do? Second, choose a framework. Tools like
Langchain, AutoGPT or OpenAI APIs.

### [10:23]

Third, integrate tools, APIs, databases or external systems for interaction. Fourth, develop and
test. Use LLMs and test the results of the agent across a test set. Fifth, iterate, refine the agent
based on the results. It's a challenging but rewarding process. As we have seen, AI agents are more
than just tools. They are transforming the way we work, communicate and solve problems. From simple
reflex agent to sophisticated multi-agent systems, these digital assistants have the potential to
redefine entire industries. Let us look how to build these agents in the next videos.

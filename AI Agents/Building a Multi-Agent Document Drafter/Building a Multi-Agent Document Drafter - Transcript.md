# Building a Multi-Agent Document Drafter — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Building a Multi-Agent Document Drafter](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76977919-building-a-multi-agent-document-drafter)
> · Video lesson, 127 min (`2:07:01`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:12]

All right, yeah. Hi, everyone, welcome to today's session on the idea of building a multi-agent
document draft. OK, so now in this session, we're going to kind of move from an idea, like basic
idea. We'll just try to first understand a few basic things about AI agent and designing and
implementation of the agents with respect to tools, MCP, and different services that we can connect
to it. And we'll use this document drafting system as a running example. So the idea would be like
the whole flow for the session would be like first we'll just go through the basics of this multiple
topics with respect to the agents. And at the very end, I will give a brief overview of the overall
code, like code in respect to it has multiple components. For example, the code will have the
LandGraph-based code for the main agents. Then for the APIs, we're using FastAPI, Streamlit for the
UI, and a few other things that might be relevant around the architecture. So we'll discuss all of
that in terms of theoretical aspects, because all of these things is like kind of you would have
already experienced during the previous sessions or the course materials, everything that are
available to you. A lot of things like FastAPI, Streamlit, all of those recordings, materials will
already be available to you all. So you guys can make use of those if you are not comfortable with
FastAPI or Streamlit. So majorly our focus would totally be around the agents part, like just
understanding the basics of it, single-agent, multi-agent, architectures of the agents, and just a
brief overview

### [2:15]

of the code. That is what our target for today's session is. OK, all right. And those who are
joining from the GenA program, so for the fourth week, they would have a project. So for that
project, which is based on the agent, we have kept it open-ended, open-ended particularly, because
developing a full-fledged agent could be a little difficult for anyone getting started with the
agent, because the first confusion point itself is what? Some of you might find it difficult to
understand what's the difference between drag, agent, or fine-tuning, or a few things around that.
So keeping that in mind, that is an open problem. You can pick your own custom problem. You can also
use the same problem that we're showcasing here. And based on it, you can go ahead, create your
project. Now, just a few things to take care of when building the project. Like, you can take any
public use cases, like personal, like if you have to automate something, or let's say, in your
organizations, there are multiple small problems or small tasks that you do it repeatedly without
any sort of automation. So something like that, if you think that could be automated with using some
sort of an LLM, an agent could be one of the best options to implement that kind of an automation.
Okay, and not necessarily that you always go for this multi-agent architecture or setup. You can
start with single agent if you feel, and as you get hands-on experience with LandGraph and the
libraries, try to pick up this, like start working towards multi-agent setups, how you can connect
multi-agents.

### [4:15]

Then there are a few things like MCP tools and everything, that how you would be able to connect.
And as the end solution of your agentic system, you should give an input to the oral LandGraph, and
you would be getting a suitable output from the agent. So like kind of a showcase with respect for
some of the previous two sessions, like fast API stream, like build API, build a UI to complete out
the full project. Okay, just a minute. I guess I'm getting some comments here. There are two
projects in week four. Yes, there are two projects in week four. One is like the conversational VN,
other one is this, like this is just an open-ended one. You can build around and work on it. So
yeah, now starting with just the basic understanding of the agents. So an AI agent is a model, like
that is something more than just a model that produces text. Okay, like this is something to
remember. Now the difference between the previous two ideologies around the LLM, that was fine
tuning and rag, they both are something where you tend to see that we like tune different things in
that, like fine tuning, we try to change the model's internal weights to generate the output. Or if
it is a rag, in terms of rag, we try to add external knowledge base and that is what is supposed to
generate the response for any user query, right? Now that is the system or the model is producing
text, but the AI agent is something that can make use of both fine tuning and rag as a sub system to
the main agentic system. So like you can think of that agent

### [6:16]

is just a architectural style in which the model is acting as a intelligence engine where this
engine can decide what kind of action to take. Now, what kind of an action to take, like we'll see
components of the agent, but before that, like from the model's perspective, intelligence engine's
perspective, they may try to directly answer, they may try to call something like extra knowledge
bases, they may try to call a vector database, they can request more information back from the user,
continue the flow, and there are something more sub agents as well, like one main agent, there could
be sub agents, there could be a parallel set of agents all working together. So they all can
simultaneously work or work in a sequential order, like that is what up to you to decide how to
architect that agent, but there are those kinds of architectures as well where the main supervisor
agent is there which is looking at other agents, they're reviewing the intermediate results, and
when finally the system goal is achieved. So system goal is something like, let's say for example,
like in our case, like the example you've taken here is document drafting. So when the main
supervisor agents finally finds that our main goal of document drafting is completed, like the human
has approved, all the other sub agents, they have completed their work, created a final draft, that
means the supervisor agent is supposed to call the end of the process. So that is like each of the
multiple agents would have some sort of role, would have some sort of like actions to take. So this
is what a general agent is, what they do as a task, right? So like, let's say,

### [8:17]

we can also compare these things to two different things, like for example, here we have taken like
chatbot and traditional automation, because these are two places I have seen people getting a little
confused, right? So technically, like before a period of two years or three years, there was
something we used to call it as chatbots, like chatbots with the basic LLMs or chat GPT, GPT 3.5
models and all, they were available. So chatbot is something that normally receives a message and
produces a response, right? And it might have some sort of a conversational memory, but the basic
interaction between the human and the system is still a request response type of a system and the
traditional automation. So there might be something like if else conditions, code, and let's say
maybe something like scripts return to get some data, so like some libraries like Playwright,
Selenium also exists to do or perform some sort of an automation. So this is what like the
traditional automation was. Now, with respect to AI agent, we tend to like both of this are still
getting used in the industry, but let's suppose we take an use case where with respect to chatbot,
user can ask some random queries or there are multiple paths, like user can ask about something like
task A, task B, or task C, something like that. In that case where we do not have some definite
rules or there could be a single query containing multiple things in that. So in those kinds of
cases, an agent is more useful when, like as I mentioned, when the path cannot be completely
specified in a specific order or in a substantial manner. So, like let's say the user asks something
like a documentation for a particular code base,

### [10:17]

like that is like an unfamiliar code base. So system should be like, taking our today's use case
example, the system like kind of determine which files are relevant, inspect them and then identify
what is missing, ask the user back. So with respect to traditional chatbot or the automation
services, this kind of multiple things are not directly possible. So that is where we take up agents
as like an LLM acting as a main intelligence head. And there are multiple components around that,
which the main agent or the supervisor agent tries to communicate with, fetch the results and try to
generate the final response. So that is how the overall agentic setup works in today's date. But
again, one more thing to remember would be that, agent is still a kind of a software system. Like it
should not have unlimited freedom. And we also shouldn't describe the agent as like acting as in
behalf of a human employee or something like that, because it is seen in multiple cases, like you
can replace or like you can use an agent for code purpose and everything. But at the very end,
whatever output they tend to generate, there could be more N number of issues because either the LLM
or the intelligence engine which you're using, it might not have all the information available to
build the project. So even as an agent or whatever AI model is available, they're still limited in
its knowledge, like with respect to the model's context and the information it can retrieve. And it
can also make wrong decisions as we know, like with respect to any model, even if we find T when we
use RAC, the models can still hallucinate and can create issues, right? Now, how an agent
technically works

### [12:17]

in terms of like, let's say when a user query comes in, so first like the idea should be that they
should observe. Observe in the sense like this is like five points that like the agent as a task
should complete. So when I say observe, observe would mean that whatever the current state of the
system setup and the user input is. So for example, let's say in terms of, let's say user query
comes in, okay. Now at that point, the main agent should look at like, is this query relevant to the
system? Is the user authorized to request the system? All of these things it can take a look and
based on it, the next action or thing that should trigger is the reason. Reason meaning it should
kind of reason that all of these things around, like what the user is asking, can the agent try to
provide the response to it? What are the other subagents available? What agent can generate the
response for the user? So after all of this reasoning, it goes to the next stage of that is act. Act
meaning like if there is sufficient information already available to the main agent or if there is
only single agent, then either it can generate the response or it can take help from some other
external services like a tool or directly pass the input to another sub agent and get the response
back from that sub agent to generate the final response for the user. Then after all of this, there
are a few architectures in agentic systems as well that is to evaluate. So before passing the final
response to the user, now this is not relevant in use cases where you are having a conversational
interface. Conversational interface like let's say, you have some kind of,

### [14:17]

you're working with a fintech setup or a healthcare setup where it is usually seen that you might
have some sort of a chatbot architecture, you upgraded it with the agentic capability. So like user
can query the databases, user can ask more information available onto the net about some extra
things. But what happens is that when you try to add all of these things, evaluate and some repeat
or stop kind of a steps, the time to inference, like the time the user gets its response back if it
exceeds over a certain limit. Now let's say I type in a question, it takes five minutes to generate
the response for me. Then in those cases, it is usually not advisable on the conversational
interfaces. But in case if an agent is designed to particularly process certain things, maybe for
some internal use case or let's say this kind of agents are well in demand these days, like this is
one is called as ICP, like ideal candidates profile finding kind of things like used by marketing
teams, lead generation teams where they kind of build agents, put queries to it and the agent has
multiple sub agents like the searches for the leads onto LinkedIn, finds companies via Google. So
multiple agents work around tries to grab data and then come and in that processes, you can add
things like evaluate repeat meaning let's say, there is an evaluation stage where you have some
basic, let's say non LLM flow as well, like based on the user query versus the fetched data, you can
set up something like, let's say, semantic similarity score, something you can set up or you can use
an LLM to identify is each piece of text retrieved

### [16:17]

to generate the user response, if is it relevant to any setup. So in those cases, you can set up
this kind of evaluation steps and after evaluation, if it flags that particularly in case that it is
not relevant or not useful to generate the user query, then in that case, we come to this particular
stage, repeat or stop. Now, if you keep a continuous repeat, maybe let's say user asks some complex
query and our agents are not designed to generate or are not efficient to generate response for
that. In that case, what would happen is, if you just have a repeat loop, meaning let's say
evaluation agent flags of like incomplete information, then in that case, ideally it should go back
to observe, reason and act. But if you do not have a stop condition, it will keep looping over the
whole system, a whole code again and again. In that case, it will take infinite time. So maybe there
is a particular thing like you should have max to max three loops or five loops. After that, it
should automatically flag that the agent cannot generate the response. That is what kind of a
response should be sent back to the user. So there are a few things that the main five things that
in the agent that you should consider is that your agent should be able to understand the system
well, what its capabilities are. Then it should be able to reason with itself, meaning some sort of
intelligent model, intelligent LLM is required, some sort of a bigger LLM that can look over the
system, try to identify all the sub-agents, tools and everything. Should be able to act, meaning
call a tool, call an MCP server, call an API, all of those things. Should be able to evaluate itself
like as a critic agent, internal sub-agent that acts as a critic to evaluate. And finally, maybe
loop over a few times like to look into more information or just stop it.

### [18:17]

Or like if the evaluation stage gives that information is correct, then the overall flow will
automatically end up, right? So that is how your agent should be supposed to be able to work. Now
the core components of an agentic system, okay? First one is like the main component is like, as I
already mentioned, model, okay? Because that will act as the main thinking agent, like all of the
processes, reason, act, observe is what the model should be able to do. Now here, like one more
thing to notice, like in this observation case, right? So in this observation case, there could be
multiple things like user query comes in, you could have some guardrails, validations and things to
run. So observe case could be only that, like you validate the input data, the current authorization
of the user, that could also be considered as an observe stage. Or under certain cases, like let's
say, for example, the user sends a request that needs to be set up for to identify which agent to
send the request in that case, that observation part and LLM can also be there, which will guide the
system to pick a correct agent. Like if it is a multi-agentic setup, like there could be N number of
agents with agents to pick first is not decided or is open. Then in that case, something like a
router LLM or a basic routing setup is what would be set up at the observe stage to move the path of
the oral system flow. Then instructions, so each of the main agent, or whatever. internal flows are
there, wherever you have LLM calls and everything. All each of them should have some sort of a
independent role and it should be able to achieve some single goal. Like let's say, for example,
supervisor agent is a general agent that can delegate tasks to other agent or there is

### [20:19]

a router agent which can help to identify which agent to call first. But after that, whatever agent
gets called in sequential flow, parallel flow, or there are multiple flows where one agent calls two
agents and they might be able to generate the response. It is better if you keep all of these agents
independent. They all have their own roles already set up. They are going to work towards a single
task or a goal. The role are particularly well-specified and you also define the constraints and the
output structure. That is what will make your overall agent system more powerful because there is no
chance of a confusion there for an agent to make a wrong output or a wrong decision because their
goals and constraints are very well cleared and provided very accurately in the system prompt or the
user prompt, all of those things. Then tools. Tools is something like normal Pythonic functions,
like maybe let's say a calculator tool is there, which can calculate subtract, additional, all of
those things. The other example for tools could be, let's say there is an API. API is existing,
let's say in Java or Node.js, and your system is required based on user query. Let's say you have
some sort of a calendar agent where it is supposed to fix an appointment for a certain user.
Whenever that calendar agent gets the request, then it should be able to call that API. To add that
API, we connect it as something called in terms of the agent terminology, we call it a tool. The
agent connects to that API tool where we particularly define the structure, what should be input to
the API,

### [22:20]

what output we will get from the API, and how to call it. What request library we are going to use,
all of these things we particularly mention. That is what tools would be there, and the state and
memory. Now, this is also somewhere important because state is somewhere over the whole agentic
flow, multiple agents are there, there will be multiple data is going to flow. If you've already
gone through those Lang graph and all this stuff, then you would particularly understand. We
preserve the useful inputs across the different steps, across agents, so that whenever the
information is required, we can fetch it during the single agent run. We do not need to keep asking
the user again and again for that information. Memory depends, let's say, you want to have a
conversational memory or a short-term memory or a long-term memory. Long-term memory in this case
would take an example like, for example, chat jpt, you have like you chat with it, and it stores
your memory for a very long period of time, so until you delete or after six days, whenever that
gets deleted. That is what types of memory could be there. That is how state and memory are also
useful. Sometimes not like state if you're building with Lang graph, then that would be there, but
memory is something like depends. For our use case today, we won't be requiring any memory, but we
would have some sort of a logging system where whatever document it is generating, whatever internal
steps the agent is taking, that is what we will store it as a part of a logging memory or just for
audit purposes, like how the agent is working, maybe just for our testing setup or those kinds of
cases. Then the knowledge of context. Now, an agent, as I was mentioning, you could have the fine-
tuned models and the rag pipelines inside the agent. So when we have a rag pipeline setup and there
is an agent that is requiring some external knowledge,

### [24:22]

you can set that particular rag pipeline as a sub-agent for the main agent or either that rag agent
would be some sort of a, like the main agent, like if it is a single agent architecture, like there
is just one agent that is existing. In that case, that single agent is what is supposed to be
calling up that rag pipeline. So now, like if you guys are getting confused in terms of what would
be the difference between this normal rag pipeline versus the agent pipeline where it is having
access to that rag pipeline. Okay, so just to clear up the doubts, so let's say I have a rag
pipeline, so how the pipeline we designed in the previous week, okay, the previous week, the
pipeline designed was, let's say user request comes in, it gets sent to a vector DB. Vector DB is
what will give us some chunks, which what will happen in this case is, we call this as a retrieval
stage. Then after the retrieval stage, we like build up the context that needs to be passed. So
context like the user prompt, system prompt, and this chunks all combined together to create our
augmentation stage. And finally, all the information gets passed to the LLM, final response is
generated. So that is what used to build a rag pipeline, okay. Now, this was a simple
straightforward flow, like user query comes in, we retrieve chunks, we get the data, generate the
response. Now, in terms of agent, let's say I have my agent. To this agent, I have given it excess
of the rag pipeline either as a sub agent or either as a tool. So the agent can call this as a tool
or a sub agent, both the ways are possible. Now, when do you can call this rag agent as a tool is
when let's say you have a single agent setup.

### [26:23]

So it is better you just add this rag as a tool. So there is only single agent taking an action,
communicating, there is no need of communication between multiple agents. But let's say you have a
architecture setup where it requires multiple agents to be working together, like, so in those
cases, this rag pipeline would be added as a part of a sub agent, like wherever the information is
required, it will call that particular sub agent for the information. Now, the difference here would
be that, let's say a user query comes in. And after the user query comes in, if the agent feels that
it does not require the rag pipeline to generate the response, it can call some other tool to
generate the response. In that case, the agent will call this tool, generate the response. So that
would be the difference between these two setups where in our rag pipeline setup, it is a fixed flow
that it will always go to check the chunks, generate the response with the LLM. But in case of an
agent, the agent will decide whether to call the rag pipeline or not. So that is how the difference
here would be. Like, are we supposed to call the rag or not is what the decision agent would make.
And that is what makes this agent as a intelligence setup. Like the LLM will act as a intelligence
engine here to identify the need of the users based on the user's request. Now, let me just check.
Yeah, core commands, right. Then there is something like this guardrails. Now, guardrails, just to
understand, it has some sort of a setup where it tries to identify whatever user input is coming in.
Like, is it not like harmful words or a certain setup? For example, let's say we have built an agent
for an internal use case or a public use case where you want to specifically block the questions
coming

### [28:25]

with respect to your competitors. So it is something like, no, let's say you ask Google's model for
some information about OpenAI or Anthropic, and maybe Google can set up some sort of a guardrail
whenever they catch up words like OpenAI or Anthropic that does not allow the user to respond back
to the user that they could not generate a response for that. So that is one example of a guardrail,
just an assumption like that. So those kind of like you can control either unsafe or invalid user
behaviors you also control, and there are other types of guardrails as well that you can set up
there. So there are two types of guardrails, input guardrail, like whatever is coming from the user
end, and there could also be an output guardrail where whatever response the agent generates, we can
take like if the output is a specified format or is the particular like, even there you can set up a
small NLP model that kind of verifies is the particular response like well-polished is not like,
let's say it's a conversational agent, the output is not like looking like a violent response, rude
response. So all of those things, when we check it, we call it as guardrails, but like when we tend
to use some sort of a metrics or some sort of a use case like DPVAL as a library, a true lens, when
we use set up like that, it will fall under the evaluation category, meaning we are generating some
score values and based on the score values, we are like either looping up the agent again or we are
just. terminating the full agent also. That is what the difference between guardrails and evaluation
here be. Now, when should you use an agent? Now, this is also something like, which you should take
care of is because nowadays as agents is very much trending into the market. I've seen organizations
directly jumping to conclusion

### [30:27]

that agent is only what is going to help them. And they might look at some data, their architecture
and things. And then they're just going to select that, let's build an agent to solve this problem.
But in the end, what the build is, maybe something like a rag pipeline or just an LLM generating the
response as a chat, something like that is like, there is a confusion between the terms or the way
to approach a problem. So agent should always be taken into consideration when you want your system
to take certain independent actions based on user input. While if you have something like, let's say
the user input some Excel sheet and it needs to take something like five things as a setup and
generate the response, it is much more better to prepare a software setup or an automation software,
deterministic software. When the rules are complete, known and stable to perform an action, that is
when deterministic software would be much more better to complete the particular task. And a few
things where you would require an agent, like whenever, let's say nowadays, there are things like,
let's say the conversational chatbots, like the organizations are making it open-ended, like you can
throw in a PDF, you can throw in a documentation, you can ask some random query. When to respond to
all of these things, then there would be a requirement of agent because you have unstructured input,
you have unstructured documents types, you don't have control over what the user will ask. So at
that point is where the agents can come in handy because they can take a decision on what to do with
the user input. Then as I was mentioning, different inputs require different tools or steps. So like
inside the main agent itself, you could have some agents where one agent is calling a database,

### [32:28]

another agent is calling an API. So under all of those cases, based on the user request, some agent
is thinking, reasoning, and trying to act on top of that. That is where also agent can be useful.
But again, like let's say if the user passes in an input and let's say you have three stable goals,
either call the API to generate the response, either update the database value or modify the
database value. In those cases, if those cases are directly verifiable or can be directly
approached, I will still suggest don't go for agent much more better to use deterministic software
because when we try to build agents, it is seen that multiple edge cases started coming up. Like the
more freedom you give to the users, the more they try to use up the system, they try to experiment
different things here and there. And that is what causes wrong responses, issues with the outputs
and a lot of things. And like users start complaining that you gave the system but it is not working
as expected and all because you designed the agents to do only a few tasks, but users started using
that for 20, 30 more tasks. So that is also something that you need to take care of. And like let's
say human reviews and all are also something. Like let's say you had a LLM fine-tuned setup or a rag
pipeline, but in those cases, they don't directly provide an human review architecture setup. Like
those pipelines are directly designed in a way that they're going to generate response for the
users. So let's say based on LLM's response, you need a critic setup, you need a human in the loop
setup in those cases, go and approach agent with an internal fine-tuned LLM or a rag pipeline.
Inside the agent that is running. So that is how like you can use this four to five rules to pick
like either you're going to use the agent

### [34:28]

or you're just going to go with a deterministic software. Now talking about the single agent
architecture. So any queries till here, like you can drop in the chat. So like we are good before
moving ahead. Okay, so I believe no queries. In this case, discussing onto the single agent
architecture. So here, like as I was mentioning earlier, one agent is what is going to do all the
things like calling the tool, calling the knowledge base, calling the databases, everything to
generate the response. That is how the architecture is. The single agent itself will act as a main
thinking engine and it will act like it does not have access to any other sub agent where it can
call. So main advantage is if you have one single goal oriented task like updating, deleting or
creating some values in the database, you can pick up a single agent well and fine. You can go ahead
with it. But where you have multiple things to do like calling APIs, calling databases, using a rag
pipeline to generate the response. In those kinds of cases, usually single agents will not be
preferred because there will be a need of much context that would need to be getting passed into the
oral state flow.

### [36:31]

Like from the single agent, if it is there, let's say it fetches information from the knowledge
base. Now, based on the user query, if it needs to call an API, it will call an API, it might use
some database. In that case, what would happen is that one single agent which have the LLM as a main
thinking agent will have context from multiple sources. Now, as we know, LLM has a context window
limit. If it gets all that context from multiple setups, then there is a chance that the context
window, the token limits get filled up, and the agent cannot run anymore to generate the response.
So due to that, in those cases as well, we try to avoid single agent because context bloating or
context limitations is where the agent could get stuck in. But yeah, for easier tasks, a single
goal-oriented task, you can go with the single agent architecture. But as I was mentioning, when you
have multiple things, multiple context needs to be passed. In those cases, try to provide clear goal
role to each of the agents. You would have multiple agents. And there should be a supervisor or a
workflow coordinator that can handle all the things because it is much more advisable. While multi-
agent architectures are there, certain architectures are there where we do not have a supervisor,
where we only have an entry point to one agent, and then the cycle flows. So supervisor may be or
may not be required. That is something you need to experiment on the architectural level. Then you
need to, like another setup is that this multi-agent architecture is also going to solve that
context problem for you because it will exchange context between multiple agents, data will flow,
and whatever data is required is only what is going to be shared with another sub-agent

### [38:34]

or whatever LLM is going to call a particular API. So context-related issues will also not arise.
And the main agent that will generate the response, maybe let's say you have a supervisor agent. It
gets the input. It can call this, like first the research agent, based on the research agent, it
gets the response. Then it passes that information to planning agent. Planning agent, like formats
on top of that generates the response. There's something, x, y, that few things, right? So each of
the agents will take a turn, will generate some response, and only share necessary response that is
required, okay. And each of these agent is also something like, they can use different tools for
context. So let's say research agent is calling web search tool, planning agent is like normal, does
not require the tool. Writing agent is making use of something like a Python library like document
writer, PDF writer. And the review agent is just reviewing the format, like any sort of corrections
or that to be made. So these are multiple things that it can have multiple tools or multiple setups
to be called. And one thing to note here would be that more specialization can also get complexity.
Now it could be that you create multiple independent agents, but in that there is a very much chance
that that the tasks are too easy or small for the modern LLMs to complete it. So maybe like, let's
say, you could have a single planning and writing agent. There is also possibility like that, like
with the modern LLMs that have a context and a little bit of over one lakh tokens, you could merge
it. So like you, again, you need to experiment with the architecture, like you need to identify, can
you merge two agents? Can you merge the ideology? Is it, will it be suitable? So these all things
will only and only come when you experiment, when you play around. Otherwise, someone could suggest
you need two agents,

### [40:36]

someone could suggest you need one agent. But for your use case, for whatever data you're doing it,
I would say, go ahead, experiment with it. Then and then only you would know what would work and
what will not work. Because let's say you have two agents, there would be multiple LLM calls. In
that case, your budget will also increase. But if you can merge it, the tokens usage can decrease.
And that is what, like your overall project cost or something that can also be reduced, right? Now,
single agent versus multi-agent, I guess we kind of discussed everything. So I'm just going to skip
this, but yeah. Like PDF will be shared, you can read more around it. And talking about the most
common agentic patterns. Okay, so what is a sequential? Like we get the input, there are multiple
agents, like we'll call each of a single individual agent. There is no mean agent, supervisor agent
or something. Each does a specific task, like calls a tool, does X, Y, Z things, sends the result
forward to generate the response. This is what a sequential pattern would look like. One is a
router-based pattern. So like it identifies which particular agent to call. So depending on it, the
particular agent will get called and it will generate the response. Now, also one thing I would like
to highlight here is that in terms of this router or the sequential, like wherever I'm talking about
this patterns, wherever I'm talking about this particular agent or setup, it could be a single agent
or it could be a multi-agent architecture setup as well. So let's say here router, like you could
have a system where there is a router which points to three different agents, like single agents.
But it could also be a case that specialist A and B, they are single agents at itself, but the
specialist C is a multi-agent architecture. So those kinds of setups are also there. Like this
patterns can be mixed match,

### [42:37]

like mixed with each other, anything can happen with it. But these are just a common patterns that
we've identified that they work, right? Then there is a supervisor worker. Like supervisor is the
main coordinator, ask each of the agent to complete a task. And supervisor is what is supposed to
finally say that the task is complete and it is going to generate a combined output or the output
based on the overall knowledge that is received from this N number of workers. Then one other common
pattern is the planner executor where based on the user input, it first just creates a plan and the
executor. Executor could be single agent, multiple agents, which will execute this plan step-by-step
and generate the response. Now, this is planner executor pattern. You might see it very commonly
onto the latest versions of chat GPT and cloud. Like you take in a input, like you pass input and
you would see onto the screen those thinking icons or like the cloud also is thinking. When you
click on that, you would see it. It is trying to generate some text where it is thinking like what
to do. So that is what plan is. And then like with respect to cloud, you might have seen that it is
using some web search features or it is using some JavaScript-based or Python-based code to generate
the output. So that is what the executor setup should be there. Then the generator review, like
there could be single agent, multi-agent architecture that generates some output. And there is a
reviewer agent which reviews and like says like, is this output ready to be shared with the user or
not? Something like of an evaluation stage itself. So generator review architecture also exists. And
you want in the loop architectures as well. So like wherever, let's say for a particular agent or
let's say there is a sub agent where the LLM thinks that whatever information the current state of
the system has,

### [44:39]

it is incomplete or it is not possible to generate the response or whatever the user requires. So
let's say we ask the system to generate the documentation for an API, but the code base we gave to
it doesn't contain any API. So in that case, the LLM should be able to ask a question back to the
user that your current system does not have any sort of an API involved in whatever code base the
user is pointing to. So what action to take? So based on whatever human gives the response, the
whole system will flow in that direction. Either the user can approve, reject, or maybe the user can
also give an information. Okay, I'm sorry. This is like, I'm pasting it another code base that you
should use to generate the response. So that is how like human in the loop setups could work. Now
talking about our use case, for today's use case. So for today's use case, like the document
drafter, so like we can create something like, with this today's use case, we can create like
documentations, like HLDs, low-level designs, or the software documentation, API documentation, read
Bs, all of those things. So that is what like kind of our supported outputs, that is what like we
have designed the document drafter agent to be. And the system flow would be, it takes in a request,
like what code base we are pointing to, where the particular code base is located. Either it is
located locally, or is it locally, or like located over web, then it kind of plans and calls
multiple tools to generate the document. It finally like with multiple stages, it request human
approval, and that finally generates a .docs file, like as a word file, as a final output.

### [46:40]

So that is how the whole process would look like for our use case. Now, the agents we are using here
is, like these are not all the agents here particularly, like there is just a input validator that
is trying to just check, it has all the inputs that is necessary. Then we have a requirement
analyst, which is going to kind of understand the user input, and like what kind of code base we
have, it identifies missing or ambiguous information, and it can also trigger a human clarification
step. So that is what the role for the requirement analyst would be. Then the context planner. Okay,
so context planner, like what code files to read, or finally like kind of what exact files it can
read or something, it would try to identify, and it also acts as a retriever, meaning let's say if
I'm pointing to a local code base, so it will like fetch in all the files, it will generate, or it
will have a tool which reads through all of these files, and maybe gets all of that collected as a
part of a context, as a string to be passed to the other agent. Then I guess we also have a
repository analyst, so which is like kind of generating the summary of the overall code base, and
then we'll finally have the document planner. So document planner is going to write the documents
based on these files collected and its information. It will build the outline of the overall
document. It will like say, like this particular section should contain this information or exercise
its things, and then finally there will be the section writer. So the section writer is what is
going to generate the full content for that particular section

### [48:41]

that this document planner has built as an outline. Then we have like from the evaluation
perspective, technical and quality reviews, like it is going to go back, check, like how is the
response based on the user query and everything, like it will check the readability of the document,
everything. And this can also trigger human review, like if required, like if it identifies any
specific thing that say the user in a query asked for, like as I was taking the example, user asked
for API documentation, but let's say this like at that point requirement analyst should itself flag
the issue as like, you know, human approval to be called upon, but let's say the human still
approves, the flow goes through, but then in that case, the technical quality review is going to
review all the outputs and all that is generated by the other agents. And here it is what, like kind
of verify, qualify, and if there is any questions it needs to ask, like the LLM needs to ask to the
user, it will ask, clarify, and then it will generate the final response that can be like. So we
would have a final Docs agent that is just going to export out the full output in a document format.
Okay, so Pramananda has mentioned, does it mean we need eight agents? Yeah, like we would have
multiple agent architecture setup because we have cleaned out the roles for each of the agent, like
one is just going to observe, like the requirement analyst you can think of just doing the observer
part, the context planner repository kind of analyst agent, they would kind of retrieve reason, the
document planner section writers are like your action, acting, like taking acts, like calling the
tools, calling services, and then finally the technical is the

### [50:41]

evaluation stage. So that is how like trying to try to cover all the components of the agent system.
So like just for the use case and to showcase how to build a multi-agent architecture is what we
have taken here, otherwise simple agent could also be used, but again like context plotting issues
and everything can come up. So like you can also play around with architecture, like the code would
be shared with you, you can merge, match multiple agents, you can experiment with it, like as I
mentioned, that is up to you to decide what can generate a better output for you. Now, just to
understand the high-level architecture of the overall system, Streamlit UI would be there that will
send the input to the FastAPI workflow API, where this FastAPI would be connected to a MongoDB, like
there is a database where it will store the state of the agent, the events it has done, and any
human approval decisions and all of those things. So that is what the MongoDB is doing. The FastAPI
will send the request, like the FastAPI will be inside the FastAPI endpoint, the overall LandGraph
code will be wrapped up, so like technically whenever you call this FastAPI workflow API, it will
call these different agents we have, and finally onto the screen we would have the option for
document exporter, where you would be able to download the final document and all of those things.
And inside this orchestrator, like this agent, as per the requirement, will be getting connected to
local tools or the MCP server and language models as well, like wherever required. And in terms of
end-to-end architecture workflow, like very simple, like you might have all already guessed by now,
like we would send a request, validate and clarify, like if anything needs to be clarified

### [52:43]

from the user to generate the document, retrieve the files information, build a repository summary,
generate a outline of the draft, then the draft, the section agent would run, will generate the full
section by section draft, then there will be an LLM which will auto-review the output without
asking, like without going directly to the user, so it will verify if anything is there, it will
first ask the user if it needs to modify anything like that of an information, if everything is
done, so quality review is done and like the human can say, then it will finally ask for the human
approval, like do you want to approve this draft or you want to make changes in it and based on that
human's input, it can revise when needed and finally, like whenever the final, like even after the
human gives some input, it generates an output as an agent, it is again going to ask for a human
approval, when final time and when the human finally approves, then and then only it is going to
export the document, so that is how the full flow would connect and I also added a link here, so you
can also call up this link, this will open up this full Lang graph architecture setup, ok, not equal
to move, right, so like I was mentioning, streamlit form would be there and this is what the oral
flow after the fast API receives the input and passes it to the Lang graph's main graph, so like
input validation, requirement analysis, then it checks for missing

### [54:45]

information if any, human interrupt is called, if no information is missing, context planning agent
is called, then the code and context retrieval agent will retrieve all the files information, then
this repository understanding agent is what it will lay around, will generate the summary for the
overall code base, document planning agent as I was mentioning, will generate the plan outline and
here it will ask for a human outline approval, if the human gives more context, goes back to context
planning, if the human rejects it completely, it will go for the rework part where it will again
restart from the requirement analysis agent, so that kind of a setup is also added, then once the
human approves, goes to the section drafting agent where it will kind of pass it to the technical
review agent, like after all the sections are drafted, if the technical review passes it or if it
rejects it, gets passed to the context agent again, if it kind of passes it, then documentation
quality agent, meaning kind of checks the format and all of those things, even if that thing passes
or if we want more sections, go back to the section drafting agent, if no, then finally document
assembly agent which will combine everything, this consistency review agent, meaning one final
check, one final human approval, human approves, then in that case document will be able to base up,
like the doc publishing agent or the exporter function will finally generate the .docx file, so that
is how the whole LandGraph code works here in this case, right, now just going to discuss few things
around this code before we take any particular action, alright, so now the state membrane
communication section, now here I am also

### [56:46]

discussing a few things, like that would be relevant for our next session, like the next session
will try to discuss onto the we will discuss more towards the deployment and a few other setups,
right Kiran has asked a question, is LandGraph like a set of agents, so LandGraph is a particular
framework that helps us build these agents, okay, so like if you are unsure or if you haven't got
time yet to check this LandGraph based setup, so the last session or the last two last sessions, I
guess there are a few materials related to LandGraph, you can check out their recordings to
understand the full-fledged flow of the LandGraph, but yeah, LandGraph is just a Python library or
framework you can also say that helps us build these agents, it is just coding platform you can
think through which we can give the agents capability of connecting to tools, connecting to LLMs,
generating outputs, taking in inputs for example as a kind of an idea, as fast API is used to build
API, LandGraph is used to build agents, like there are other libraries also outside of LandGraph
through which you can build agents, but as of now, right now at this point, LandGraph is one of the
leading frameworks with which we can create coded agents, like there are a few services through
which you can create no code, no code platforms are there, through which you can also create agents,
but that does not give you much flexibility with multiple options, like you want to create something
custom, things and all, in those cases, we tend to use LandGraph to build our agents, right, now
talking about this,

### [58:47]

the state memory and the agent communication, so the state as we know is part of the LandGraph setup
only, like whatever information flows from one agent to agent, if a U1 interruption was required by
the agent, U1 gives approval or something, so all of that information passes through the state, so
that is what state here is what we are mentioning, so let's say supervisor agent gets the input, so
at this point the supervisor agent has all the inputs, now let's say there is another sub-agent, it
requires only two inputs from what all the, let's say ten inputs the supervisor agent has, so you
need to build a code like that, such that the supervisor agent just only passes that two inputs to
the sub-agent, so that is how you need to create the state workflows, that minimal information that
can be passed to generate the maximum output, so that is one thing you need to take care with the
state, but otherwise the idea is simple, the data that flows through your overall agent system, the
agent code is what we call a state, next is memory, Memories can be used for multiple tasks, like
let's say it is a conversational agent. In those cases, you tend to store the conversational history
of the setup, so your agent can remember what conversations the user did in the past, and based on
it, can store user's preferences, what things the user does with the agentic setup and everything.
If it is a non-agentic setup, we use memory to store the logs, like to audit the agent for future
use cases. So that is also use cases of the memory in our case. Then let's say the agent
communication part.

### [1:00:48]

Now, when I say the agent communication part, that would technically also mean that, let's say we
have something like MCP tools and all of that. How do you explain to the agent when to call a tool,
when to call that MCP server? So all of that internal communication processes, you also need to
define as a part of the prompt, you need to explain everything very clearly, that for this kind of
use cases, this tool can be used or whenever there is a requirement, this to the supervisor agent,
like let's say whenever user ask for something for a particular review of a code base, they can
directly call the repository analyst agent. So that is what you need to prove as a part of the
prompt, you need to explain so that the agents can call, they can act with a particular tool, they
can communicate with it. Now, in terms of modern protocols, there are two modern protocols with
agents as well, one is MCP and one is A2A. So you might find the MCP sessions recording, we just had
it like a month back. So with all the latest MCP tools and everything, we have covered it in there,
how to create an MCP client server, everything. So if you have not yet looked into the session, do
look into the session so you would understand MCP more, because otherwise that session itself will
also take another two hours, one hour more to just explain the MCP part, right? So just think of it
MCP as a service that allows us to simply connect an agent with tools, here in this session itself,
there is a separate slide for MCP as well, where you'll just understand the difference between an
MCP and tool as well, okay? So don't worry about that. Next thing is guardrails and failure
handling, so like the human approvals or the human interruptions which I was mentioning during the
architectural flow and everything, so that is what the same thing

### [1:02:51]

is what the guardrails and failure handling would be, like whenever the agent generates not a
required output or let's say the agent generates some wrong outputs if a guardrail can or the
evaluation stage can flag it that this output is not correct, maybe the agent needs to rework, so
this is what the guardrails and failure handling setups is what you need to have majorly, okay? Then
the tools in the agentic applications, so examples, like you could have multiple tools, like let's
say read a file tool, then you have a database connected, so how to connect to the database and
write a SQL query and get the data from the database, if there is a calculation requirement, like if
there is a calculator tool, if there is a document creation requirement, so there would be like
let's say an API is there where it will take the user's complaint and generate a ticket ID or
something like that, the user complaint, so something like that, all of these are examples of tools,
like multiple things that we can do, so now a good tool should clearly have a name and purpose, like
you should give a clear name what the tool represents, so let's say particularly it is a document
exporting agent, so just checking and verifying the document is correctly possible in correct format
and everything and finally generates the document, so you could name it like doc exporter agent,
something like that, clear name and purpose, purpose meaning whenever you set up the system prompt
for all of those things, in that case you particularly mentioned that this agent has this particular
capabilities, like you list down everything, like it can take one or two to three actions and this
is the kind of output it will generate, so whatever main agent, supervisor agent

### [1:04:51]

or a sequential flow, whatever it is working, it can clearly pick up that tool to particular, like
call it whenever the usage appears, then the validated input, structured output or whatever is
there, each tool you also should design in a way that it takes some input, like you also define that
as a part of the prompt itself, that this tool requires two inputs, like argument A, argument B, so
the LLM, the thinking engine will only pass those two inputs, so validation of input for the tool
and output is also necessary because let's say if you're calling an API, now that API requires five
specific inputs and in that if let's say there is a case where only some registered authorized users
can only call it, so during the tool access only, you should be able to pass that information to the
tool that is a validated user or not and if it is a not validated user, whatever response the API is
going to give us, that should be properly communicated back to the users, so input and output
validation and what kind of structure the output will come in is also necessary, minimum required
permissions, that means that it should not be a case that the agent tries to call the tool, 10 after
of nine times it is not able to call the tool, that is also something that should not be there, so
easy to connect or it should have all the required permissions under which the agent should be able
to easily call the tool, then useful error messages like let's say if it is calling an API, API is
down, the database is down, so those error messages should be also built particularly well and
logging is also an important aspect, meaning let's say you ran the agent, agent generated the
output, now in your testing stages, you see that your agent is failing,

### [1:06:51]

now to see where that agent is failing, it is important to log each and every step of the agent and
what tools it called, what input it shared with the tool and what output the tool gave in, so
logging is also important and timeouts, like let's say it called the API, API is taking three
minutes, so that should also be there, that should be a limit to the API as well, now this logging
and things we'll cover in the LLM Ops, the AI Ops section, like where we'll explore, like that might
be after two sessions from now where we'll discuss some tools like MLflow so to identify how we can
capture the agent's internal states as a part of logging setups, tools, inputs, outputs and
everything, so like debugging can be easier, so but that is all included as a part of the deployment
LLM Ops stages, now talking about the MCP, so MCP is a protocol like we have the STTP protocols and
everything for the web, so similar to that MCP is also a protocol designed for the AI applications
to connect to any external tools, now it also gives you capabilities with prompts and resources, but
the main task that major people use for is connecting to tools, so the architectures looks like is,
it is an AI application, it has an MCP client, so this client is something like is already provided
by the like let's say as a land graph, it gives you a particular syntax directly like five, 10 lines
of code setup, it automatically acts as a client, that whole client setup is created, now this MCP
server is something that would be designed either by you or either by some external entity or
individual, and your client connects to the server, now the server can has multiple tools,

### [1:08:51]

like it could have database tool, it could have let's say some API call and everything, so the
difference between this MCP and tool, like the tool does the same thing, the AI agent according to
the requirement calls a tool directly to generate the response, while here we are adding an MCP
layer in between the AI and the tool call, when like whenever the AI system requires to call a tool,
so why was a requirement for this kind of a setup, so to understand this, now let's say you have an
agentic setup, you have all the things locally, like the database is running locally, then it is a
normal local function, so when all of these things are there, you can directly integrate as a tool,
that is fine, but let's say, you already have some APIs that are built and is running onto the other
servers or the other setups. It is usually more advice that it should be exported as an MCP server.
In case you have multiple agents like separate agents, let's say your organization has team A, B,
multiple teams are there. They all want to access same database. Instead of everyone setting up
their own MCP client servers or tools locally with the agents, it would be much more beneficial if
you just expose your database as the MCP server, and each of the teams will just need to set up an
MCP single client, and each team would be able to query this to the same MCP server. So there would
be less requirement of resources, setups, and everything to be done, and multiple people, multiple
teams all can query to the same MCP server. So this is what the MCP versus direct tools from the
architectural perspective, like the major use cases only from the architecture perspective. We are
trying to ease the usage of tools.

### [1:10:51]

There are a few more other things like bi-directional communication, few of the other settings like
the MCP can act as a client and send the request back to the server. So these are multiple things.
But before that, I would suggest you to go through the MCP server to understand all of the things in
detail. But just from architecture perspective, MCP tries to solve a problem where your tools are
existing onto other servers, other cloud servers, and if multiple teams need to maintain a single
tool, they can also expose it as a MCP server, and each of them then can call just a simple MCP
server once. Now we will talk about something about moving from notebooks from the ID. So in the
last few sessions, we just technically just worked with the notebooks, like fine-tuning done with
the notebooks, rack pipeline built on the notebooks. Now as we might go onto the next few sessions
around deployment and LLM Ops, so those who are not very much well used to using tools like VS Code
or other IDs like IntelliJ or some text editors like Sublime or all of those things. So for them,
just to understand the basic differences that notebooks gives you good access to fast
experimentation like where you can run each piece of code and try to check for the internal steps,
internal output steps of a pipeline. But in case of Python files, it is more like you run a file, it
runs the full cases like you need to write and print statement in between to check what happened
during the flow and once a single flow is executed in a Python.py file, that flow will complete and
then only stop. While in case of notebooks, you can kind of check an internal function,

### [1:12:52]

you can just generate the output for that particular function and then decide if that function needs
to be placed inside the main code. So ideal cases like as an AI developer or a data scientist or ML
engineer, what our usual practice is that first, you design your oral pipeline in notebooks. So like
it allows to experiment with the architecture and everything. You get an interactive output. You can
easily trials with different prompt and everything and for exploration purpose like multiple models
if you're exploring everything, like you're going to have a messy code and everything. So notebook
is much more like easier to maintain. Once you identify and complete your oral process, then you
would need to convert the whole notebook flow code to a Python codeways function setup and
functionality because when you deploy it, notebooks cannot be directly deployed, right? So when you
will deploy your code either with Docker containers or onto cloud services, everything, when those
things happen, you need to convert your notebooks to Python codeways like .py files. So that is when
like we move to an ID kind of a setup. So like debugging, logging, error handling, repeatable
execution environments, all of these things would come into picture when we move to kind of code
basis. Now, like here we have given just a few setups into the PDF itself for people to understand
like what they would need. So you would technically need like, as I'm going through the setup of VS
code, you can just go to like kind of go to VS code. So let's say I'm going to go here, you can just
go to Google, go to VS code and here just go to download and here according to your system, just go
ahead, download VS code, whatever is required like Windows, Mac or Linux, whatever is there,
download VS code and whatever Python version that you are going to use, I would suggest like, you
know, you can go to python.org

### [1:14:53]

and then from here, let's say like the latest version is 3.14, but you can also look around other
versions or so, but instead of going with this plain Python installation, I would suggest you go for
this particular service, which is called as UV. Okay, so I guess I might have explained it into
other. Yeah, UV part, right? So Python is a language as we understand now, like with respect to
other like, you know, like users who are coming from other languages like JavaScript, I think you
would have like those node modules or the JVM toolkit and everything. So like this UV is something
like a Python's project manager or a library manager through which you can install libraries,
install frameworks and all of those things. So for example, we are going to take an example of how
to run this UV. So I'm just going to share my full screen here. Just give me a minute. Screen, hope
my full screen will be visible. I'm just going to go to my VS code and let's say I'm just going to
add that. I'm just going to create a new folder here. Yes, UV, just add it. So this is a blank
folder. Now we'll click on this folder. My terminal is open activated then what as a few basic
functions of you now first to install UV is what like, you know, you would need to go to this link
and like just go to the main code base installation. So here it will give you list of the commands
for Windows or Mac OS or Linux like either you need to use it in PowerShell or everything. So based
on it just copy this commands like just you just copy

### [1:16:55]

it open up your PowerShell just paste it and once it says process completed you should be able to go
here and do something like this UV version it will show you the version. So once you it shows the
version that when UV is perfectly in install into your system now a few basic commands around you
now look like don't worry like if you don't still understand here like when I'm going through all of
these things is also So like like when to download the UV from everything is listed out in the read
me so you can also go through the read me understand pick up everything later as well. Okay, then
few commands like there is one is UV in it. So when I do UV in it, you would notice here a few files
would be generated here. So you can see here Python version. So like my UV when I installed the UV
Python 3.3 was running. So here we particularly like my default is running with 3.3 then this is the
main.py it just generates a main.py file this I guess you should delete it. That is not an issue
with it. Then there will be this by project dot 2ml file which will list down all the libraries that
you have installed into a system and everything. So let's say now there could be two things. Let's
say you can also do something like this. Let's say UV add fast API. Okay, so you will notice here in
the dependencies what particular fast API version it is downloaded it will add up here. Okay, so
that is how you can install a library in UV that is UV add fast API like instead of in the pip we
used to do pip install here in case of UV you will do UV add now. There is also another possibility
of installing libraries. Let's say you have a long list so you can also create requirements.txt.
Let's say I'm mentioning streamlit. I'm mentioning pandas and then you can simply also do UV add
hyphen are requirement.txt and if I go to my project 2ml you

### [1:18:58]

will notice pandas and streamlist are added. So that is how you can also add like more libraries
like bulk number of libraries using a requirement.txt file then other cases few round. Let's say you
have a code file. Okay main.py. I'm just going to say print hello world now to run this file. You
can do something like this. Okay. Yeah, before this before running this code. You might have noticed
it is just created this dot vnv whenever I added any library here it created this dot vnv. So what
you would not to do is you click on this dot vnv slash scripts slash activate. This is window
specific command. Now it may read me. readme here, if you would search for this dot vnv, sorry, you
would notice command from Mac, OS, or Linux, and also for the Windows PowerShell. So based on your
setup, based on your OS, just go through the readme, pick up what command is there. So this is how
in Windows you can activate the environment and where the libraries are added. Now, to run this
main.py file, what you can do is UV run main.py, and you can see it has printed. So that is how you
run a file in UV. So these are the basic steps to use the UV as a library or UV as a Python's
package manager, where it manages the libraries, the run command and everything for the Python. With
respect to who all might be familiar with PIP and everything, so why we need to go for UV is because
I guess written in C or C++,

### [1:20:58]

and UV is written in Rust language, that is another language, and UV has seen to be three times to
five times more faster than PIP. So installing the libraries, running codes and everything, UV is
faster. So we have seen people started moving from PIP to UV. So that is why nowadays in all the new
projects, we're going to use UV as much as possible. Then talking about the FastAPI and Streamlit
basics. So FastAPI is used to create the backend APIs for our system. Streamlit, while Streamlit is
used to create UI. With it, we can create UI that can connect to the FastAPI's backend. So for
example, I will go to my same code base, and what I'm going to do is, I guess already added
Streamlit and I will just add this back, testUV. So I've already added FastAPI and Streamlit. I will
also add one more setup here, uv-add-uvcon. So uv-con is a service that allows the FastAPI endpoints
to run. So what I'm going to do here is in my main.py, I'm just going to, from FastAPI import, or I
will just quickly ask my codex to do it. Wait, I will just copy a few things from here then.

### [1:23:14]

This should work. Now to run this, ideal case, you should do uv-con app. So this app is what I'm
pointing at that. I will just clear this first. So the command will look like this, uv-con app. So
this app is something that they just point to this app. Then I'm going to not print it, I will
return it. Main and port equals to 8,000. Should be main app in that case, should not be. Just copy
it. Put it in my bit test. FastAPI import is still at FastAPI. I have to get function and yes.

### [1:25:21]

So now you would notice you get this URL. So I will just go here. I will just go to this URL. You
would notice there is this default function. I'm just going to click on Try It Out, Execute. You'd
notice hello as output is returned here. So that is how you create an API as a getPost function. You
define a function, what output it will give if you have some input. So you can also mention an input
here, that input will be processed via this function. Everything would be included as a part of this
FastAPI structure. Next is what would be, let's say my streamlit as a services. So streamlit, let's
say I'm just going to write it up here. Let's say import streamlit as st.st.title, test
st.textInput. I'm just going to store it in a variable, let's say a equal to textInput st.success a.
Let me ask about it. To run the streamlit, the command is streamlit run whatever the file name is.
So let's say I'm just going to do streamlit run main.py, let's say one, okay, label. Labels equal to
input. So here you can see an output like this. The test, so this is what we set up as a title, then
this input, so textInput is what taking as a text box that will take the input, and st.success a,
this is something like whatever

### [1:27:21]

I'm going to type here is going to be typed here. Now, this is something like whenever you get a
response from the API, you use something like st.success, let's say st.error, it is going to be red.
So depending, there's kind of a UI library in Python, which you can at least create some basic POCs,
MVPs, get an UI attached to your libraries like whenever you need to demo your agents or anything.
So most of this open source projects out there, people who put it onto the GitHub and everything,
you might majorly see like basic streamlit UIs would be connected because much easier to build,
might take half an hour or so to build out the full process. You just need to create a form, headers
and everything, and just call the back-end FastAPI structures, everything in process. So this is how
this streamlit would work normally. So in our case, how we would design is that you would have a
streamlit UI, which sends the request to FastAPI endpoint. This endpoint is what is going to trigger
this agent workflow, which will like multiple agents, supervisor, everything will complete and
whatever output it generates, it gets collected inside this FastAPI endpoint itself, which will
convert the output into final particular structure and pass it back to the streamlit UI. So
streamlit UI, you'll be able to see all the responses that you get from the agent. So that is how
the overall flow structure would be designed. Now, a few things around Docker. So not going much in
depth, I guess, as majority of you have a few experience around the software. So Docker, as we know,
helps us run services inside a container, like based on an image, meaning which has all the packaged
codes, like the files, whatever language, code language you're using and everything, packaged and
set together. And the container is that what the running service

### [1:29:21]

for that image would be. So into the next sessions, before the next session, a few of the files
would be released for you, like if you don't know Docker or anything, you can read more onto the
Docker, like why it is a good usable service when we are going to deploy whatever agents and not
just with respect to agents, any kind of a software setup or anything. We require a kind of a
containerization process or something to deploy the service, for cloud, there are N number of
containerization, like with respect to AWS, ECS, EKS, or like the ECR repository services. So
multiple things are there, which can accept Docker services as a container and run it over the cloud
as a deployed managed services. So just for our today's use case, I have just created a normal
Docker file that has running MongoDB from here, and to just run this at your local end, this Docker
compose file and everything, I'm not going to go in much more depth. To run it at your end, you just
need to go here to this particular setup. I've already installed UV libraries and everything. After
that, you also need to install Docker. For that, you might need to do some few multiple steps. You
need to go to the Dockers here, go to Install Docker Desktop, and for that, as I mentioned, it will
automatically identify what OS you are on, and for Windows or for whatever setup. Install Docker
Desktop, and once it is installed, you would be able to see a Docker desktop here, and if I open up,
let's say, it will find a little bit of stuff. When you open it up,

### [1:31:21]

you would notice something like this, like containers, images, and everything. So these are multiple
images that I have used, some Qtran vector stores, Redis vector stores, then here in this case,
containers, there is this document drafter, container that is running, and inside this is what my
MongoDB is running. So when I'm going to run this command, Docker compose up build here, what it
will do is it will refer to this Docker compose file automatically. It will download the MongoDB
from the Docker hub. So Docker hub is a open service where people publish their images, so from
here, it will install the latest MongoDB and everything. So I'm just going to run this now, like if
you're running it for the first time, it will kind of download the MongoDB and it will take certain
time, but as I've already used this, downloaded it, so it directly went into a running state. So
that is how for my fast TP, all the logging and everything, I'm doing it here with respect to the
MongoDB. So all my services and output will be stored inside MongoDB. And now once that my MongoDB
is running inside the Docker container, I also have MongoDB Compass already installed. So this
MongoDB Compass is something that can connect to any MongoDB server or local connection that is
running. So for example, if I want to add or just to view the things that are going inside my
MongoDB, so let's say it is running at a port localhost 2708. So what I do here is onto my MongoDB
Compass, this also again a downloadable tool, free tool, just install it, go to here, this
connections, click on this plus setup plus, here you will get this my default URI, just change it to
this port value, localhost 2708, save and connect, you would get it here, this particular connection
is connected. And here inside that, you will identify

### [1:33:22]

that this document drafter is there. So I've experimented a few things with my document drafter
agent code. So here you might see multiple things, like what it is stored during when I use the
agents. So human decisions like has all the human approvals, action acceptance, all the internal
logging processes that the agents has taken at each of the steps. So that is what I'm using my
MongoDB for, just for auditability purpose of my agent. I'm just talking this from a lot of
different perspectives like architecture, because agents and everything is just software, as I
mentioned, right? You just design the software and these are the different tools that might be
helpful for you to design that full software. The main agent setup like multi-agent architecture or
your single agent architecture, the cool, the tools calling and everything, everything will be done
by the LandGraph as a library in itself. So if you understand LandGraph as a library and everything,
please make sure if you do not understand LandGraph, there would be a session on LandGraph that is I
guess something called as designing stateful applications with LandGraph. That particular is showing
LandGraph, like with LandGraph how you can create multiple architectures like sequential, parallel,
human in the loop, multiple things go through that session. It will explain how the multiple things
you can design with LandGraph. Without it, it would be very much difficult to understand the overall
flow, right? And here with the code walkthrough, I attached an image or something, right? So I guess
this image is pointing to like my overall system architecture that we have built here. So like user
input goes through the Streamlit UI, Streamlit UI sends that to FastAPI. FastAPI calls this workflow
service, which indirectly has my LandGraph code that is agents.

### [1:35:24]

And these are like LandGraph agent has multiple document nodes, like the OpenAI calls, the tools,
MCP services and everything, MongoDB connection with the FastAPI service, everything. And then this
document exporter, which generates the final document, generated document, sends it back to the
FastAPI. And FastAPI will finally send back the response to the Streamlit UI that will be shown onto
the Streamlit's output, the front-end output. So that is how my overall code directory, like the
code structure would be there. Okay, I guess now we can move to the code part, the main code part,
okay. So to understand this particular code, how I would suggest to you that you go around this code
base and try to understand is, first you go through a few particular steps. First, how you try to go
through is, try to go through this app directory, inside the app directory, just look out at this
particular sections, main.py, which is the full FastAPI setup. Like we initialize the FastAPI
service, we are importing from the services via this workflow service. Now, if you would notice this
workflow service is just a graph, sorry, not a graph, a class function, which is connecting all of
these things, MongoDB client, the different nodes available from the land graph, and it is just
running this create and start function. So in this create and start function, what it is doing it,
it is initializing a thread ID, like for maintaining a session, and then it is collecting all the
inputs from the stream root, like session ID, event type, agent name, title, input summary and
everything. And then it is finally calling the submit function. So the submit function is something,
just checking if this particular session ID is there,

### [1:37:28]

or is already part of an existing graph run, if it validates this perfectly, it is going to call
this run function. So what this run function is doing it, if you notice it, it is calling my
graph.invoke function, which is essentially by land graph agents code. So it is going to pass
through all graph input, meaning all the input that I view through the stream root UI. It is going
to pass all those inputs to here, and it is going to check for multiple things. If there is any
interrupt by the agent asking for any human approval, it will run this function, it will show in the
UI that it is awaiting a particular human's approval. If not, then it is going to show this final
status, like as completed, completed meaning the oral agent structure is completed, and it will
return the final output, or if it shows canceled, meaning that output could not be generated due to
maybe some APIs there, or some error is there during the oral process. So this is the oral workflow,
this class setup I have done, which will indirectly, this main.py file, the fast API service will be
calling. And inside that, let's say we'll go through one by one thing, I will go to my readme, I'm
just going to run this service, fast API.

### [1:39:34]

Once it shows application startup complete, I'm just going to reload it, you would notice a setup
like this, my full, the API service is ready. And now here, you would be able to see this multiple
options like get session, get events, stream events, this is all with respect to connected to the
MongoDB. And this session is not like we're going to take this input, like document type, what kind
of document I want to get it drafted from my agent, the technology stack, the repository path I'm
pointing to. So all of this, what it is. like the sessions API is going to take in all the input and
going to invoke the main Landgraf code. Then what you do next, once you complete this and understand
this FastAPK code is go through this UI folder where my Streamlit code is there. So as Streamlit
code was shared in, I guess the week two of the session. So it is just that we have created forms,
input structures and everything. So what you will essentially get is UV run UI slash, sorry, slash
Streamlit app. Sorry, UV run Streamlit run. Yeah, you'll notice like this, this kind of UI would be
generated where like some by default values are already added into the structure, like document that
default values. You can just edit it if you want according to your use case. And what we have done
again, another next thing is that have added a sample code base already for a particular product
API, like a few APIs around some product services

### [1:41:35]

is already added. So this sample code base can be used to for you, like notice check out, test the
agents, like how it is going to generate the document for your output. Or you can also create your
own sample code base as a service and everything. And just paste in the part to that particular
repository path. Then next, what I would suggest you to go through is the next thing is obvious,
like you might have already till the part understood fast API, the UI that is your Streamlit UI and
the Docker compose, you would have initialized the MongoDB if you're not understanding Docker well.
The next week, like whenever the Docker things would be covered, feel free to, just wait for it, or
just for now, just go through the readme, just run the steps, required steps to run the Docker file
and just complete the flow. But otherwise, if you want to understand it more depth, please wait for
the next week. Now that these things are done, the only thing that is pending here for you would be
to understand this graph folder. So graph folder, like our previous notebook sessions, what we have
essentially done is, you copy all of those nodes and paste it here, each of the node pasted here,
like as a node files. So here we take certain actions, like when we consider it from a production
point of view, like in your notebooks, the whole flow is now into same section, like you write a
class, inside that class, you create nodes, you compile, do and everything in together. But when it
comes into production, when we create some reusable components, in terms of easy to read files and
everything, inside that you create a notes.py file, put in all the nodes, all the individual
functions, your prompts.py file would be there where you type in prompts for each of your individual
agents, individual nodes that you have defined in your LandGraph. Then this state file, state file
meaning

### [1:43:36]

what the state, the LandGraph expects, like input state that I mentioned during the explanation or
the presentation, like what data moves between multiple agent. So that state definitions, like what
particular variable is, what kind of an data type, everything would be mentioned inside this
state.py, and you will finally build this, build a file which will combine all of this thing
together. So if you notice, LandGraph.graph, we're importing nodes, we're importing all the nodes,
and one of the state we're importing. And inside this builder is what will create all the edges,
like builder.edge, like start with validate input, analyze requirements from analyze requirements,
either it can go to requires human approval, or it can pass to the next agent that is context agent,
context agent here can either, like if it requires human approval based on the human approval, it
can again go to requiring or analyze the requirements again, or it can go to like a plan context. So
this is the same architecture that I showed you here as a agent's architecture graph here first. So
this whole flow, the same flow is created here inside this builder.py flow as using this LandGraph's
particular functionality like add edges, add conditional edges to complete that same architecture.
So go to this particular architectural flow and other folders around this here contains the tools
and services. So this tool folders contains all the different types of tools, like what kind of
files it can read, like text extensions, like .py, .js, you can edit up and modify this tools
repository as well, that is fine. And then there would be multiple functions here, like list
repository files, mark secrets. So it is something like just reading through the local repository,
listing out all the files,

### [1:45:36]

and reading this files, grabbing out the text from that. So there will be a read repository file as
well, where it will kind of use certain service to read, like maybe .py file, .js file, everything.
And so this is how all the tools are listed here, read file, then find Python symbols, find fast API
routes, so multiple tools. So all the tools you want to add to your agents, you can add it via this
kind of a setup. You just write down all the functions and where exactly are these tools used? Now,
this one question you might have. So when I go to my graph inside my notes, you would notice that I
have imported kind of all the tools here, like app.tools.repository import, like wherever any tool
requirement is there, I'm going to import it. So like wherever the services are required, so why do
we, like one more question, right? One more thing here is that you might think our notebook were
much easier, but why we're complicating stuff here, like making too many codes, too many files. So
let's say there are multiple agents I need to mention that could be like independent and I'm
creating it across different folders. So in that case, instead of creating or writing tool codes
again and again for each of the agent, what we tend to do is create a tools folder inside it, list
out all the tools. And whenever another agent requires a tool, you can directly do from
tools.repository import that particular tool. So that is how simple reusable components is what we
are trying to build with this kind of a structure, the code structure, okay? Then this memory folder
defines all the functions to store the data into your MongoDB. So whatever MongoDB, the data you see
here, all of those functions are written here,

### [1:47:36]

like the document version, events, human decisions, all of this store functions are mentioned here.
Then MCP-related services also written here. We'll also check MCP setting, like how to run that as
well. If you have not yet gone through the MCP session and this block files is the document exporter
agent, which will combine the output of all the sections, combine, create a final .docs file and
will give us the output onto the streamed UI. And this context is like a local provider, again,
calling the tools, like reading the local files, searching a repository text, like reading text from
the files. So all of these local tools and context provider to the agent is provided under the
context folder. So anything like, if you have a rag pipeline that will also fall under this context
folder. If you have some database tools, query tool, that thing will also fall under this context
folder. So that is how your usual agentic structure or code database structure would look like,
okay? Now that my FastAPS service is running, Streamlit service is running, this particular MongoDB
services, everything is running. One last thing that you would require is to run the MCP service. So
I'm going to go here, FastMCP, yeah. So this is a FastMCP inspector that will open up a similar UI
for the MCP service you have created. Now, as I mentioned, like I will not go too much in depth with
the MCP service because it will require another hour to go through. So go through the MCP recorded
session. If any doubts, please feel free to ask queries on top of that.

### [1:49:36]

But yeah, the whole MCP code is given here and it is just going to start and MCP service here. And
how that MCP service looks like is what, no, it will open up here. So this is an MCP inspector. What
you're supposed to do, like, no, how to test out your MCP tools is that you click on connect here.
So once it shows connected, you need to click on this tools, list tools. Here, you will find
multiple things like, no, read. Repository file tool. So let's say I'm or let's say I'm going here.
Okay, list repository files tools. I need to provide a repository path. So let's say like right now
it is by default pointing to my local repository only. So let's say I'm just passing it this. Okay,
or I'm going to pass this sample code base of a relative path sample code base. I'm just going to
run this tool. So here you can see product API main dot py. So if I'm going to look at here sample
code base this app or yeah, this is the product folder and this app for the main dot py. So app main
dot py models dot py. So this is how no this MCP is like no running this tool and how you can have
how you actually use it. Is this you can deploy this MCP as a separate service onto some server and
all so multiple agents across or let's say your some agent is running in mobile application. Someone
some application is running in websites both of this service can also call this MCP tools that are
running onto some other server while let's say if I had to build an agent with a local tools onto
app or a local tools onto the website both will require their separate integrations and separate
setups. So instead of that better to expose tools as a MCP service

### [1:51:40]

it put it onto some server. So all multiple agents multiple websites multiple applications can call
the same tools if required via the MCP gateway server. So it makes calling the tools much easier
compared to embedding the tool as a hard-coded code along with your agent. So that's how the
infrastructure is is what the this MCP service is going to provide to you all right. So now let's go
ahead and run this agent as the final demo for this today's session. So in the readme of like no few
examples are already given so sample streamlet input now I have given here two inputs are given one
is for a high-level document design and one is for API document. Let's say I'm just going to take up
this. So let's say product management API documentation document type API documentation purpose. I'm
just going to mention audience python first API by identical is already there repository path
already mentioned provider local required sections. I will just replace and file in product API
reference is I will just paste it here additional instructions are just replace it here and I'm just
going to click on start document flow. So now when you click on this you will notice a few things
our main graph is started. You will get to see a few things around here like current agent here
working and what current sub agent is running what it is kind of document planning agent is running
plan document node inside your land graph is running and this is no internal output studies is
generating during the flow now why I created all of this is because just to show for all of you
know, what things it is done and everything now this all things.

### [1:53:42]

Naturally, like if you are there's a first-timer doing all of these things you might find it complex
to understand and everything but like just try to understand it intuitively like as I was mentioning
during the code like this is all we do it for auditing purpose logging purpose and until and until
you are no someone like moved into a more of a managerial role or have started understanding the
solutions from a system architectural perspective it Might be a little hard for you to grasp all of
these things. So like if you are working on building agents and everything so this all things might
be difficult for you to understand under the first start. So just try to understand it from the
intuitive purpose like know the code and how the code is designed and everything could be a little
difficult to understand and this is no it is also showing us this agent execution history like know
what particular agent is started when it completed process number what activity did so like know
what agent it ran it also going to show by a particular time and right now you can see here it is
stuck at a awaiting human flow. So it it says that review the proposed document outline. So it is
proposed a document outline and look there is a few options like you can also edit this JSON file or
you can directly approve. So I'm just going to give approval resume workflow. It is again going to
look look reconnected to the land graph workflow using the session ID like it has an human in the
loop interrupt service. So it again connected to the agent and it is running here. So you can see
like here this particular table it will keep updating so like know this particular section drafting
agent is running next it should show completed here. You can see completed now with the review agent
is reviewing so it will keep running until and until it is going to show was a document here with
the final approval to generate the document. So I like I believe now like the reviewer agent will
not flag

### [1:55:42]

any inconsistencies in the document it can or it might do it but yeah multiple agents are running
here. So let's just wait till it runs and I'm just going to open up as we are already with the very
end of the session. I'm just going to open up the microphones for everyone any queries till the
workflow runs you can ask. I will enable. Thanks for this session. Just one question. This is
similar to the rag implementation right if I'm not mistaken. No, no not totally right as I mentioned
it here, right like I don't know if you had there during the session but under certain cases like
our rag flow was fixed process like user input comes in it was always going to take the first step
as retrieve from the vector database. It will assemble everything and passes to LLM now here in our
agent case like at least I have given it power that it will act as a workflow and there will be an
LLM LLM acting as a review agent or a technical review agent where it will flag inconsistencies
during the output generation and when it generates this flag there should be a human input or human
Interruption to guide the agent or guide the workflow. So when we do this kind of a process, this is
one that makes this as a agent now one more thing is that we have added tools. So let's say there is
an LLM that got an input is that that it needs to analyze the requirements from this particular
repository to how it could like no fetch files from this code base or everything it needs to call
tools where it

### [1:57:43]

Calls the tools like communicates with external services that is again also part of an agent setup.
So again, like this is how we use multiple tools or components of this agent setup to define or like
to say that this is an agent while with our rag. Let's say here if I make one change here into a rag
flow, let's say there is an LLM where upon the user request the LLM can decide if to initiate the
rag pipeline or not. This will make my rag setup as a agentic red rag setup. So that that is how the
difference between rag and agent would be. Yeah, so I mean like this is more. I mean, this is the
agentic rag and what we saw last week was just a rag implementation, right just a rag implementation
correct like a flow implementation where we do not give the power to LLM to make a decision. In
agents the idea is that we let LLM take a decision. Now here in our case, let's say LLM had five but
LLM like based on the user's requirement may only call three tools two tools based on the user's
request. So that is something we have even power to the LLM to decide and work upon. That's what
makes it agentic. Yeah, yeah, clear. Now, so I have a use case where I have for my product multiple
documents, right? It could be user guide. It could be release note installation guide security guide
and this kind of around 10 to 20 documents. So I'll put this in a folder and then create the rag
application that we did last week and then you know kind of a key in the question telling how can I
you know, let's say set up the application so that they I don't need this agentic implementation
like that would be a pure rag implementation what these are yes, they're pure I can be is correct.
Like if all the queries head to that system is going to be

### [1:59:45]

all about whatever is there inside your setup, then that could be rag. But yeah, if you have
multiple code bases what code base to read and everything then in that case you might look at some
sort of an adding an agentic intelligence. Okay, and then if I have to let's say generally when we
make this release notes, right? So we capture some of the known issues fixed issues on these kind of
things. So I'll have a let's say Excel or some kind of a ticket manager and I point to this and then
I want the document to be created automatically. So for that also I can go with the previous plain
ragging implementation. Right, right, right. So in those cases maybe you can kind of experiment like
maybe you can have Excel setup and everything maybe can add as a tool to the setup like after your
whatever like you mentioned the release notes and everything. If the LLM generates it, it can
directly call some API and share it on the Excel Google Docs or something. That kind of setup like
you can try like maybe if you want to. But if the process is going through some automation where it
is automatically adding all the things, maybe in that case like you can even avoid the agentic
setup. That is fine. So whenever deterministic steps can be taken, I would always suggest take
deterministic steps. It involves less mishaps that the AI can do. And I guess here our technical
review agent has flagged something. Maybe he is asking some thing like response example, severity
medium, stating that the draft shows the route decorator with some status code. Maybe it has flagged
some issue with my code.

### [2:01:46]

So I'm not going to do much thing. I'm just going to say decision except risk, resume workflow. So
like when some actual user might be using this, maybe they might themselves review the files, maybe
give some inputs here as a conditions and everything. Like some information that might the users or
the code writers have would have taken as assumptions or like they might have needed to do that
things which the LLM have flagged as a technical severity. So till that it completes, let us just go
through the final key thing. So from the overall process as the session, we understood like first
starting with agent, how, what is an agent, the components, everything around that understood the
observed reason, act, evaluate cycle, then looked at single agent, multi agent architecture,
understood a few of the setups. Like fast APS team, connecting all of that together, MCP versus
tools different, the basic tools, the basic MCP difference. And then we went ahead with the code,
like how to design the code structure, how to move from notebooks to the VS code setup and
everything. Now we spent much less time into the code setup because the full materials for the
session, like there are around like 20 videos separately on the agent, like going through multiple
libraries with code. There is already a full project setup with respect to conversational BI setup
and everything. So I believe the code part, you all would be able to easily figure out how to write
and connect and everything. And then we also discussed some common patterns around routing,
planning, supervisor, human approval setup. And finally, as the code setup demo, the use case would
took. So finally it is asking for the review, the completed document.

### [2:03:47]

You can see it has generated this full document. Like you can see some, I guess around five, 10
pages of document it might have generated. I'm just going to hit it like one final approval. So it
is going to give me a docs file. Most probably document publishing agent collected all the data and
download editable docs. So I'll just put it here and download and maybe not open it up. You can see
it has generated a document like this. So few edits might be required, but as it is a draft, I guess
good enough to as a first version or something. That was it from the full use case. Any queries?
Anyone else? Anyone else is having any queries? Just one more small help. I mean, in the context I
could understand, but then if you can kindly please from the code perspective, if you can just list
out what first has to be done, second has to be done, it will really help for people like me who
doesn't come from coding background. Sure. So what I will do is I will put a file here. Startup.txt.
Here we will write uvcon step one. Next goes streamlet run. Sorry, the docker also needs to be done.
Docker compose up build.

### [2:05:57]

These three functions should do and for these three functions, three things to run. Let's say if you
want to run docker, you can go through here like how to install docker and everything is included.
So first just go with and install docker and try to run this. Once this setup is completed, maybe go
through here, install what is uv, install this uv and initialize the environment, install all the
libraries. Then you would be able to run this command and then run this command. So your UI backend,
everything will complete and you would be able to execute. Sure. I believe there are no more queries
in this case then. So I guess I'm stopping the recording.

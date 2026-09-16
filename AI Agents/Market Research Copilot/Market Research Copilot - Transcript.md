# Market Research Copilot — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Market Research Copilot](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76727297-market-research-copilot)
> · Video lesson, 82 min (`1:21:49`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:00]

Hi everyone, good evening. So today we're going to have a look at how to build a structured market
research agent using a pattern, an agentic pattern, which is a sequential pattern identically. We
call it as a planner executor pattern. This session is more focused on designing the planner
execution pattern workflow properly using an orchestration model. So every step in the workflow
would be explicit, traceable, and we can abstract out a lot of things using a framework like a CREO
AI. So we are going to have a look at all of these things. So in today's session, what we're going
to learn, so we're going to learn is the planner executor agent architecture working with the CREO
AI framework and adding web search capabilities to the LLMs. Apart from this, we would also have a
look at another similar solution via another framework called as LandGraph. So that will be a bit
more advanced one. So till now in our AI agents program, we would have seen different sorts of
agentic architectures, as well as in the last few sessions, we had a look at, I can say, how to
access run LLMs. Then we had a Healthrise agent project. So right now, as we are in the
architectural stage, we are taking up an example of one of the most used architectural patterns that
is in planner executor agent pattern and going to have a look at a code walkthrough for the same. So
first, trying to understand the exact problem,

### [2:03]

like what is the problem we're talking about. So the problem is with respect to market research and
why do we require specialized market research agents? So when someone talks about market research,
so it kind of sounds quite simple until some of the organizations. So let's say, for example, a
market research agent could be, let's say, a kind of a lead scoring system, but lead management
research or something like that. If you take it as an example, there will be a lot of problems when
you're going to systemize or when you're going to orchestrate the overall system. There will be a
lot of problems at multiple levels. Like, let's say, for example, if the organization was doing it
manually, then there will be an overall team of people over there who might be dealing with
unstructured data, data coming from multiple sources. The people need to find data from different
websites. They might need to check if the data we are collecting or that has been collected, is it
compliance sensitive? Then we need to check the evidence. The process would be quite time consuming.
The manual research kind of could take up to six to 12 hours per topic, whatever research you are
doing on. We could lead to inconsistent sources, no structured validation, meaning multiple person,
someone can pass in through a validation, someone does not allow to go pass through that validation.
The process would be hard to audit, and no systematic rule-based architecture would be there. Now,
in terms of, let's say, something like compliance,

### [4:10]

research compliance kind of idea, we would be dealing with multiple jurisdictions, regulatory
bodies, a lot of compliances, competitive positioning, and a lot of different enforcement. Again,
the same thing. When humans would be going to do this, different types of data would come up, and a
lot of different interpretations could happen. Here, what the end goal with the market research
agent would be, that we are not just trying to automate the process of collecting the data, because
the data collection earlier could have been automated via scraping or other sorts of resources, but
with respect to agents, we could add a structure, we could add auditability, we could add a kind of
repetitive consistent workflow into the research structure. What is a market research agent? If I
have to say it in short, a market research agent would be an orchestrated AI system that decomposes
a complex research request into structured tasks and gathers verifiable evidence against which a
decision-grade output can be produced. Chirag, pausing you for a bit. I think there is a lag. Are
you sharing another screen? Because few people are commenting that there is a lag. I am on the same
screen. Okay, so I think there is no lag. Anshul and TS, I don't think there is a lag.

### [6:12]

Please go on, Chirag. I guess they are saying I can't hear as well. Is it an audio problem? I don't
think so because it's clear at my end. We are working now. Okay, Chirag. So as I was mentioning, to
brief what is a market research agent, it would be an orchestrated AI system that decomposes a
complex research request into structured tasks. Meaning here we are talking about the planner stage,
meaning whatever user request comes in, we would divide it into tasks, gathers verifiable evidence,
meaning we are going to make use of web search capability that the LLM can utilize to gather
evidence based on the user request and produce a decision-grade output, meaning the executor part
would collect all this data, formulate a report, and then present it back to the user. So this is
what we are trying to achieve here, because this is what in short a market research agent would
mean. And when we say how or why we are making this system agent-ic, so how we can say that this
system would be agent-ic is we are referring to a system that operates with goals and multiple
steps. Now, first point is, as I said, goals, right? So each step in the pipeline for an agent-ic
system would be goal-driven, meaning each node. For example, as we are going to run on a planner-
executor architecture,

### [8:15]

each step would be goal-driven. Like each would have its own goal, each would have its own input to
be considered, and an output to be generated. It would be a multi-step, meaning certain sections,
say the models, the LLMs, they would reason and generate output after multiple reasoning steps. And
it won't be a normal single prompt-response interaction. We'll go through a chain of multiple steps.
Then an agent-ic system has intent, meaning it uses tools, it has multiple roles, so we have clear
defined responsibilities. And more importantly, in our case, like where we don't want to generate a
paragraph. As a market research agent, usually the output would look like, you know, kind of a
report kind of a structure, so it won't be a one-paragraph or one-liner output. So how structured
outputs we can generate and overall controlled execution flow. So as I mentioned, we would be having
a sequential pattern, the planner-executor, meaning how we would be able to control flow in a
sequential direction. So all of these different sorts of characteristics that we would be able to
generate all of these different sorts of characteristics that we'll define into the code will make
the overall process an agent-ic system. So this layered execution is what makes our system agent-ic.
Right. So before jumping into the overall different parts of just the Planet Executor pattern, we'd
like to also discuss a few other patterns. So just to understand why this pattern would help us in
this current use case of market research versus what

### [10:18]

the other patterns, like if they can be used in this case or why they might not be helpful. So first
of all, talking about sequential pattern. Now, sequential pattern and Planet Executor pattern. Now,
both could differ as well. Now, a Planet Executor pattern, for example, there could be multiple
parallel planners and a single executor or a single planner, multiple executors could be there. So
the Planet Executor pattern could make use of a sequential pattern and parallel pattern, both as
well. So with respect to sequential pattern, the flow would be like task ABC. The flow would be
deterministic. We know how the flow goes. We would have a full high control, easy to audit, meaning
wherever the flow fails, we know at what point at what task the system flow failed. In case of
parallel pattern, multiple agents would be running at a single point of time, and there would be a
requirement for aggregation step. Now, when I talk about the Planner Executor pattern, if the
Planner Executor pattern was running on a sequential pattern inside it, meaning there would be a
planner, there would be an executor. But if it was sequential, meaning there would be a pipeline of
planner or executor or a single planner or a single executor running there, the planner creates the
task, and the executor is defined there to execute the task that the planner is defined. Now, in
case it was a parallel one, meaning we have identified that even though we are having a Planner
Executor pattern, we require to plan it multiple steps, meaning the task can be further divided into
more subtasks. So we divide all the tasks, maybe could be at the planner stage or the executor
stage, and then we find a probable aggregation step involved

### [12:22]

where it combines the output of multiple agents, either at the planner stage or executor stage. So
planner can make use of a sequential pattern or a parallel pattern, both. The other two important
types would be a reflective and a critic pattern. It means that the agent pattern, they can generate
the response. And we would have another agent that identifies, is it the actual output that the user
is looking for? Is it the response is relevant to the user query? How is the factual correctness of
the response? Based on all of this, the other agent that we call as a critic agent or a reflective
agent could ask the main agent to do a revision loop, meaning retry generating the response. Now,
you can control how many times you want to retry all of these things. And then the last pattern,
another major pattern is a hierarchical pattern, meaning there would be a manager agent that
delegates to work to other tasks. Meaning, let's say there would be a router node, or there could be
different points of node there, where there would be a requirement of splitting the task further
into multiple parts. Now, how the multiple parts are decided, will they run in parallel or in a
particular sequence that all things come under the hierarchical pattern, meaning the overall idea is
to delegate tasks to other worker agents. So for this session, we're choosing the planner executor
pattern combined with the sequential workflow, because right now at this particular point of time,

### [14:24]

we are trying to understand when building a system, why clarity and control over the workflow is
important. We want to make the system auditable, realable, and we need to have a process where we
can find if a particular node fails, how it fails, and when it is failing. Now, putting more light
onto the planner executor pattern and our choice. So if we have a single LLM or a single LLM agent
where we do not have multiple subtasks or division of tasks, what would happen is the LLM could, I
was mentioning that if we have a single agent that we want to directly research, like we want to
have that single agent research and write and do not divide the task into multiple tasks or a
particular workflow, what would happen is sometimes the planning might not be 100% correct.
Sometimes it might plan something, execute some of the parts, but might not call the tool. Meaning
we kind of would have all the things together, like multiple subtasks combined together, and the
response quality would decrease as we start having more tools, more complex level of market research
that we are trying to get. So the planner and executor, when we divide them both separately, the
planner part, what it would give us is a structure,

### [16:24]

and it would give us also a repeatability factor where we can always have a plan. Then we can again
further, like when we talk about from an improvisation point of say, when the executor fails to do
something, we can go and again improvise the plan, kind of adding a critic part back to the planner.
So there would be inside a pattern itself, there would be more types of failure handling cases, edge
cases that we can handle. So when you divide one simple task into multiple subtasks, there is a
reason to make each of the subtasks or each of the complex tasks to give each of them structure, to
give each of them an auditable characteristic, and add a repeatability structure such that when you
have a good system, whenever you will ask the system to do a same kind of research, they might plan
something similar for the same request. So a repeatability factor is very important when you talk
about an agentic AI system. So without planner, so if you visualize without planner, what would
happen is LLMs can hallucinate. There is a concept called a scope drift, meaning based on the user
input, if the LLM may not be able to read the prompt perfectly, could not understand it, there might
be a scope drift and it would generate a response that is not very much required or has no
structure, plus the response could also be very hard to verify whether this response was actually
requested by the user, versus with planner, we would be having explicit goals

### [18:27]

into a system that what each of the tasks would have, we could also define focus areas where we are
focusing, we can generate sub-queries and we can also add in some rules as required. Now, this is
the architecture that we would be going to see in today's code walkthrough with respect to the
market research agent where we would be having a structure to get the user request, a planner agent.
So the planner agent would convert the input to a structured JSON and there would be a research
agent. So what the research agent would do is, it has access to web tools from the web, it would
gather evidence-based data on that plan and then there is a writer plus verifier agent. So the
writer will transform this data collected by the research agent versus the plan given by the planner
agent to write a report, plus what the verifier agent here is supposed to do is, there are cases
where the model could have hallucinated or generated some data without actually getting the data
from a URL. So the verifier agent, we have writer plus verifier, meaning we have asked in the
particular task itself for the LLM to remove all of those data that could not be verified or are not
backed by any URL. So here you would see the data flow is always forward going. We're not
improvising here, meaning there is no feedback loop or no critic loop. Each stage depends on the
output of the previous stage and this linear dependency, when we test it actually.

### [20:31]

So how usually we test it is, we have certain sets of test benches where we try to identify whether
the planner agent is how well it is generating the plans, how the research agent is collecting the
data over the web. Do you require a different strategy to get the data from the web? And the writer
plus verifier agent, do you want the output in a different structure or we want to have some
algorithmic logic to have this data verified instead of getting it verified by the LLM? And then
finally, out of all this, we would be getting a final structured report or the final output
generated by the last writer plus verifier agent that we can consider directly as a report if it is
generated a markdown format. This is the structure that we would see. And the auditability factor
that I mentioned is this is how that at each node of the step, the divided subtask, you can identify
why something would have worked, why something would have failed. And based on it, you can keep
improvising the pipeline based on also the domain knowledge you're working on. Why domain knowledge?
Meaning for a health care, the planner, for a health care use case, the planner might have used
different steps of planning the research for something like, let's say compliance kind of a research
compliance kind of a problem. It might need to plan it differently. So based on the domain,
different plans, different research kind of tools, all are required. So based on that, you can
further improvise the architecture as well as how are you going to use the tools allocated to LLM,
how you're scraping the data or how you are calling the agents. You can even maybe have a critic
loop

### [22:32]

or you can improvise on the architecture further as well. Right, now the framework that we're going
to use is Kriui, right? So Kriui, why we are going to use Kriui? Because Kriui is a kind of a
framework that supports multi-agent orchestration. Kriui gives us a lot of different sorts of
abstractions that map well to how we can simply create workflows. So here we have multiple
abstractions like an agent. So an agent defines a role and capability. Then we have another
abstraction for task meeting. The task defines a contract of work, meaning what exactly to work
upon. Then Kriui meeting binds different agents together and the process, like the execution mode,
the overall Kriui is supposed to do. Here, there could be multiple execution modes. The mode which
we're going to have is a sequential flow. And the oral idea, if I were to say about Kriui, it would
be to make all the abstractions as simple as possible, such that we can simply separate out
intelligence, like that means the LLM roles, executions task and tools as well. So when we have all
of this independent of each other, not binded together via some code flow, if all are there into
multiple pieces across abstractions, what we can do, we can, at any point of time, we can plug in,
plug out this particular, all the abstractions together to create and form a workflow. So this makes
it perfect for creating certain kind of agentic flows where we are having a requirement for multi-
agent sequential hierarchical flows or even simple multi-agent pipelines can be created

### [24:33]

with the Kriui framework. So what we're going to do next is, we will now have a proper code to walk
through for the Kriui pipeline. So let me just share the VS Code screen. So hope my VS Code screen
would be visible. Can someone confirm into the chat? All right, thank you. Great, so first of all,
talking about the project structure. So like when you would be given this code base, so this code
base along with the session recording would be provided to you onto the LMS in the AI agents
program. So from that, you would be able to download this file and everything required to run and
execute the code, right? So what we are having here is and .env file in which we have configured the
OpenAI API key. You can also make use of Gemini model if you want to work the free model, then we
are defining what is the OpenAI model we are using. And there are two other API keys. There is one
is Tevely API key and the other is Serpa API key. So these are two web search tools available, both
are web tools. So the Serpa tool is with which we can get Google results and Tevely, that is another
like tool

### [26:35]

that gives us results by searching through the web. So we are going to have this mode allocated for
the LMS to call and get data from the web for the tasks. Now, the requirements of TXT would require
KriuAI as a library, OpenAI library, Pydantic to structure a few of the things, KriuAI tools that
will help us connect with Serpa and Tevely tools. And to run the Tevely, we will require the Tevely
Python library. So that is all we have defined here in the requirements of TXT. Now, coming to the
main code base where we have defined our actual code flow pipeline. Okay, so as I mentioned, instead
of one do everything agent, here we have split responsibilities into three different roles, a
planner agent, a research agent and a writer agent. So we would see how we are going to define all
of these three. And so yeah, at the very top, you would be seeing that we have put at the standard
Python utilities, like OS, the typing.env, Pydantic. So the Pydantic is here because we are having,
like we are requesting the planner agent to generate the response into a structured format. So for
that, we have just simply created a Pydantic structure. The KriuAI imports you would see is agent,
task, Kriu and process agent to define the LLM, the task to define what this particular agent is
supposed to do. The agent will also contain the role definition. The Kriu, Kriu would connect both
agent and task together. And the process import is with which we will define

### [28:35]

the flow would be sequential. And with the KriuAI tools import, we are defining the support tool and
Tevely tool. So they're in inbuilt tools already abstracted here. We just need to have the API keys
and we can call this tools, right? So now to load this particular keys from our .env file, we are
here making use of load.env. So from .env, it is like, you know, when you call this load.env, it
loads all the variables that is here into the .env file along with their API keys, wherever
required, it would load into our environment. And then what we're doing is from this environment
variables, we are assigning whatever value is required. So for say we are assigning a variable open
a model and whatever value we would have to find here in .env, we would have it stored. If there is
no open a model defined in .env, by default, we're going to pick GPT-401-Winnie. Now, For Creeware
tools, Surper and Tevely, we would need to use this OS.Environ. Surper API keys one will define,
Tevely API keys what will define. And the OpenA keys anyway kind of, you know, already embedded
there into wherever the OpenA client call would make, right? Now, the first thing we are doing here
is, okay, before this, this Surper and Tevely tool, why we are having these two different search
tools is because both the tools can return different results and different ranking on the web. So
for a use case, like here the use case we have, right? The research compliance.

### [30:35]

So for compliance intelligence, we would like to have more number of results as possible so that the
results, the facts that we're going to include in the report, it would be like, you know, fact
verified across multiple resources. Now, there is also a dependency that the model can call with the
tools if it is not able to, you know, get all the information. Sometimes it may call only the Surper
tool. So it depends on the model as well. We can, however, explicitly mention in the prompt request
that we want to call both, get the data from the both end, generate the results, that is also a
possibility. But you can leave it to the LLM to also to decide, you can give it a test, whether the
LLM is able to produce the results, grade that or you can play around with the prompt, which tools
to call. You can also, like there are certain ways, you can also overwrite the already created
tools. You can define your own custom tool where you're going to call the Surper API or Tevel API,
that kind of a procedure is also possible. Now coming to the plan schema. So now this is a pidentic
model through which we are asking the planner to output a structure where we want a goal, like what
the user wants, like this is what we are going to define through the goal. Regions meaning the, like
for a compliance, research compliance report in what jurisdictions, like in what regions the
particular compliance is active is what, what are also important. And then focus areas, meaning for
a particular compliance research, what are the focus areas queries, meaning this queries would be
used for the LLM to find explicit search queries run on the web. And then here we have evidence
rules.

### [32:37]

So here we are mentioning for primary sources, every important claim must be a source URL, if
unsure, use uncertain instead of guessing. So all of this basic few evidence rules we are providing.
Then now we're going to define all the three agents. So first agent we're defining is the planner.
So here we are defining the goal along with the planner, turn the user request into a small research
plan and search queries. You create a simple auditable plan that beginners can understand. So this
is the kind of backstory we are providing. So the planner knows what kind of a plan to do. And we're
also defining verbose equal to true, meaning whatever run the model is going to do, we will be able
to see it into the terminal. So you can turn off the verbose, then it will be directly generating
the final response into the particular variable only. And we won't be able to see the output into
the terminal. When we will run this program, right? We will see what kind of output or the verbose
equal to true, it generates a kind of an output. And here we're defining LLM equal to open a model,
like which model we want to use. Then a researcher. So again, a role of researcher along with a goal
we would define, find reliable sources, extract facts with the URL. And here we have a bit of a
different input here along with the input as with the planner agent, we're defining a tools equal to
value. Here tools equal to, we're passing both the tools which you have defined, support and
heavily. So meaning this particular agent can call any of these tools to extract data from the web.
And then the third agent, where we ask it to write a clean report and ensure each claim has a source
URL, meaning kind of a verifier. We are also adding a verification mark that if a claim has no URL,
you remove or mark it uncertain.

### [34:37]

So this is what we want to do via the writer and verifier agent. Now all of the agents would be
having this open a model, same model. So to keep it consistent, otherwise in some cases it is also
noted that for certain tasks, some model might perform well, some model can, so let's say for
example, for the research part, you might choose a reasoning GPT reasoning model, like a GPT-5 model
versus the writer agent where it does not need to think much, it just need to rewrite the overall
architecture and give it a structure. So for those things you can use a model like GPT-4.1 where it
can help you rewrite, add some creativity. So based on different agents, you can maybe change the
model as well. But for now we are only keeping all the LLMs same as it to make it consistent and
easy to configure. Now defining the crew. So, sorry, yeah, but before defining the crew, we will
define each of the tasks here inside this function. So we are just simply making a function build
crew and inside this, we are defining all the tasks. So for the plan task, the task which we
imported from CREU, right? We are passing a description where we are giving in all the information
like a make a simple JSON plan with a user request, whatever user input comes in, we are passing it
and we are asking it to return only valid JSON that can match the schema and we're passing the JSON
schema generated by the pydantic structure. The expected output would be valid JSON only and the
agent we are assigning to this task is the planner. Similarly, for the research task, we have kind
of put in a bit of a different prompt

### [36:42]

where we're asking it that the output must be JSON with this structure, meaning the tools are
definitely going to call the web search, we'll get results from Google search engines and we'll get
the data. But to structure this data for the writer agent, what we're asking it is like this is also
another way of asking for a JSON output in the structure, either you define kind of a pydantic
structure and embed it here, or you can explicitly mention the JSON structure here. So what here we
are doing is we are building a JSON structure with sources, findings, enforcement signals and
competitive posture. Like what does the vendors claim, the URLs, confidence, the actions, like
whatever compliance kind of rules might have changed, whatever summaries it has given. So all of
these things would be curated across this, four different keys. And here we are explicitly telling
it what to do. And also we have added two rules here, use primary sources when possible. And if you
can't find enforcement or competitor evidence, include an item saying not found. So this is kind of
a rule. Now, if we don't define this rule, there are high chances the model might add some different
wording, might add some different terminology that might make it, I would say incorrect, but that
will not be having a consistent result structure. The expected JSON output here will be a JSON
evidence pack. Now, here you can change it according to a string, like this is a string base, so you
can explicitly mention you require a JSON output, something like that. And the agent we are
attaching to it is the researcher. Same way, the final report task here, we are defining the hard
rules, do not give any legal advice,

### [38:42]

write every important claim must show at least one URL, include a small claim sources table then in
the report section, what report, what headers we are requiring for scope and assumptions, key
obligations, concentration, cross border transfer, like with respect to compliance, what are the
same enforcement signals in the last 12 months, recommended actions, any kind of actions to take on
based on the compliance changes, all of these things has been included in the writer and verifier
prompt. And the final expected output we require is a markdown report. Agent we are attaching is the
writer agent. And then we'll return the crew. So what crew would have is agents where we define all
the three agents, the tasks that we are going to define is all the three tasks that we have. Now
this both should be in the same sequential structure and then the process. So the process that we
imported right above, right? This particular process part. Yeah, you can simply different process
dot sequential which will make it a sequential plan meaning all this task would be executed in a
sequential format. And here again, we are doing verbose equal to true now that we have our overall
crew build. What we will do is we are going to make a request to this particular market research
copilot agent. So we are going to define a user request in the user request we are specifically
defining like kind of an input that should be passed. So build so we are just asking build
compliance intelligence on research compliance for AI systems in EU and India. So we are asking for
research onto two regions and we are like this could be different sorts of user inputs like focus on
content retention include enforcement signals.

### [40:42]

So all of this like and also competitive competitive posture for three major SAS vendors. These are
the kind of prom that has been defined and here from here we are calling this build crew function
and passing in the user request and once we get this crew like that was returned from here you can
do a simple crew dot kickoff and we are going to finally print the result. So to run this if you're
going to run it via the UV package manager. You could run it like UV run copilot. If you are using
the pip package manager what you would require is you would need to write Python copilot.py. So both
the ways are fine. Either use pip or UV both are fine. So when I'm going to run this I would just
make it. So here you will see when like this is the outputs this colored boxes and task started this
messages we are seeing this is all due to this verbose equal to true. If you turn it off this all
outputs we are seeing here into the terminal we wouldn't be able to see. So now what it does is it
says task started what input it got then the agent work started meaning agent planner started what
input it requested. Then agent final answer meaning what was the answer of the planner. So planner
build this part gold build compliance intelligence regions focus areas queries. So these are the
queries the planner has generated to fetch the result from the web the evidence rules. Then it says
task completed then it will go again to another task called the second agent researcher. So this is
how it keeps

### [42:44]

running and now here it is calling the search tool to get some data. So it called upon these are all
the web results. So this is data we are getting from the web URL title content. So all of these
things is captured and this is the overall procedure going on. So now right now all the web scraping
web searching is going on. So if I go a bit more down. So this is the final answer from the
researcher and all the data will further be processed by the final writer agent. So now it's going
to write like the writer and verifier agent is working on and here it might still be running. So
yeah this is the kind of response it has generated and you would be able to see like this is the
final markdown response structure it has generated. So it would be very similar to what we have here
is scope and assumptions like scope and assumptions. So what kind of report it has done the key
obligations. So like the all the sections content retention everything data retention. So like
whatever format we ask the report in it defines the overall report structure in the same way as we
are requested. So this is the final response generated by the overall career structure. So now this
was with respect to using a framework like CREU AI where we have kind of abstracted a lot of nodes
abstracted a lot of formats and we can simply move in different code pieces arranged in a way via
the CREU

### [44:46]

format task agent format so that we can know like the overall idea of CREU AI is to make the process
abstracted more simpler now in cases where people like having more control over the code base having
more efficient workflows we have more better frameworks like called as Langraph or other ones. So
what I will do is I will import and another project rate so this is and another file so the code
base for this will also be shared so first of all let me know what I will do is I will just run this
we will see and demo along with the UI let me restart the screen there are a few questions in the
chat please sure questions in parallel pattern are the agents executing sequential planner executor
as plan of action so for now like as I was mentioning in parallel pattern are the executing
sequential planner executor as plan of action

### [46:47]

so the thing is planner executor parallel pattern and sequential pattern are all three different
patterns sequential and parallel as they suggest sequential meaning it would be flow of workflow
from point A to let's say some certain point CDE in terms of parallel meaning multiple tasks are
running in a at the same point of time now when I say the planner executor pattern can have both
meaning inside the planner executor pattern like you have two different sections defined one is
planner one is executor and in that you can again choose a pattern for both of the cases whether you
want some parallel execution or let's say you have a restriction for the inference time where you
might require certain response in a very limited time so if you can parallelize the task then that
means you are adding in parallel running pattern inside the planner executor pattern so you can test
around that based on how fast you want the results from the system or if there are certain tasks
that can be executed in parallel they are independent of each other then you can also create a
particular planner executor pattern where it is utilizing both the sequential and parallel pattern
as well now mayor is asking how the planner agent's output is ensured consistence across multiple
call or period of temperate so there would be two to three different ways one is that from the
planner agent we would like to have a same structure output because a same structure output would
ensure that whatever data output we are going to get they all will always be in a structure in a
structure meaning it returns goals

### [48:50]

it returns the queries to be that we can use to get the data from the web so all of this is there so
that particular structure is one important which we are anyhow have added a pidentic structure and
example structure to it but in case you can add in another explicit verification layer that whatever
output is we are getting from the planner agent we can add in a checker that is the output a json
structure a python dictionary structure if not can you convert the structure into a json structure
and if that particular format fails meaning the planner agent gave wrong results in this case you
can have a retry mechanism where it can retry a certain number of times till we receive a particular
json structure from the planner agent so this is how you can kind of add more verification plus and
logic through which you can generate output in the same structure always task can be llm call data
scraping data cleaning yes usually tasks uh would be could be llm call could call a function or
could be an llm that is calling an external tool like here for in a case surfer tivoli surfer and
tivoli apis are there free right so surfer tivoli i guess both provide up to thousand free web
requests per month so uh you can use it until you exhaust free uh limits and then they will get
refreshed the next month and how creo is different from google adk right i guess sorab is already
answered uh yeah so as sorab mentioned as already mentioned creo is built for

### [50:54]

more flexible multi-agent collaboration rapid prototyping right meaning it has abstracted a lot of
things and you can simply easily build a structure while google adk right google adk has came up
with their own versions of how to connect with the multiple protocols like mcpa2a so when you're
going to utilize more complex agentic architectures where you're involving uh different databases
you're involving uh mcp kind all of those kind of different latest tools then in those case uh
google adk is something you might look up to uh but for some simpler systems where you don't require
to have this no exist all sorts of different mcp servers a2 agent collaboration structures then in
that case creo is a good choice to go ahead how can deploy such agent program in my internal server
what will the project structure look like then uh so the question is how will i make in production
api using fast api uh how will the docker file look uh what will be the size of docker image and how
feasible it will be for deploying okay so for this any case uh there will be a lot of different
things you would have to look at as one is uh now now whatever code base you might receive right uh
so here in this case it is already as a .py file so what you can do is you can simply create a fast
api endpoint and based on any user input query you can make make a call to this creo ai's particular
function and you will be able to get the answer right now uh you want to dockerize it right now you
now if you're going to use the same structure as given in the code base then you can use something
like any python 3.10 3.11 slim image because

### [52:57]

here we are not going to have any some sort of a hard hardware constraint or we require some sort of
uh i would say uh like need to install some gpu servers inside the docker or something so normal
slim image would work and the size of the docker image would depend on to the what is the final size
of the slim image plus the four to five libraries that we are going to install so those libraries
are not very much uh uh i would say some 100 mb 200 mb uh libraries they are smaller libraries but
in case you are going to use a non uh close source model like not a model from open ai uh
anthropical google uh and you're going to deploy or use a model like an open source model from
hugging face olama or something then in that case you would need to configure the olama or hugging
face as a uh in into the docker compose where uh it has access to your uh systems gpu or if you are
going to upload it on an internal server then make sure it has a gpu hardware enabled and the nvidia
drivers are all up to date so that the model is able to access gpu and how feasible it will be for
deploying so if you're going to use this close source models like open a it would be quite easy like
you can just know uh deploy it anywhere you can close it but in case you're going to have open
source models then you would have to figure out how the infrastructure you require based on the
model size what particular uh uh llm open source llm library you want to use because each library
will provide a different inferior speed someone would provide more better speed but they would
provide quantized versions which will make

### [54:59]

the model's accuracy uh like decrease in accuracy of the model right so uh all of these things
depend and then based on this uh you can know like maybe create a dockerized version and deploy it
onto an internal system then then the question is do you recommend any sources to add a systematic
prompt for each task right so first of all uh in this case you would need to identify what each task
needs to do what model you're using and based on this there are different prompting techniques so uh
prompting techniques would be zero shot prompting few shot prompting chain of thought prompting uh
or kind of asking the model to reason if you are going to use a reasoning model so there is a site
promptingguide.ei you can look onto the website it has all the prompting uh structures already
defined with a few examples uh you can make use of those patterns improve your prompts in a way that
the models are becoming more effective so 3v8 takes care of tool integration here uh and uh that's
an abstracted version for us yes that's an abstraction already given otherwise what you would have
done is you would have needed to write uh uh request post structure to the server or api or you need
to uh specifically have the tivoli library installed write the code for that but in case uh you want
to even further customize what the query already gives uh you would need to uh write some custom
code and convert that to a creo ai uh tool so now if you would go to creo documentation you would
find certain sections where they uh there would be examples of how to create custom tools uh so that
is how you can define where can i exist

### [57:03]

this code and i mean like is there a github repository or a website all right so uh this particular
uh no uh session is part of the ai agents guided projects in ai agents uh from tmc academy and this
code will be made available onto the uh learning management system onto onto that particular courses
uh section uh of the agent architecture uh do you like to add something here sorab no i think chirag
we are good yeah okay yeah you can continue with the rest of this rest questions uh can take at last
yeah uh great so this uh is a bit of a more uh uh customized version i would say from the previous
one where we had a lot of uh uh abstracted things uh by ourselves this is uh the another uh code a
code base which has been built uh with lang graph so let's say this this is more for a uh kind of a
market research for a sass product and we're using gemini and serp api so i would just do a run
research so it has planner executor and summarizer so planner has completed certain tasks so product
identified zoom category video conferencing it has generated five search questions three news
queries now what the executor is doing is collecting market data doing a google search news trend
api that is running all of the

### [59:06]

things so scrape 10 full articles and now the summarizer would be executing sending all collected
data to gemini for synthesis and then finally it is generating a summary at this particular point of
time once it gets completed we'll be able to see a full report once it's generated the final report
uh we'll know i quickly have a look at how this particular land graph code is structured against the
qi code how it is different and how much amount of control it can give to us okay so you would see
here Kind of this is the overall report it gives, like what Zoom, key strengths, primary challenges,
strategic recommendations, pricing analysis, like did all the analysis, finds the competitors, when
I guess I've teamed with Google Mute Slack, and all other information related to the product,
product research, whatever data we've got from the website, news, trends API, any recent
developments. So it's fetched certain different reports from the 24 number, 25, what are the market
trends and momentum at this moment, this is what kind of analysis, and all of this would be
available, and you can also download the report as a JSON or a markdown format. So if I go here and
say this is the final report.json, so what it will do is it will capture like this, the full report
in JSON. So from here, what one can simply do is this JSON report can be passed into any kind of a
front end where the front end can make use of this JSON structure, fetch the data and present it on
the screen, meaning if you remove the stream with UI, then also it's generating JSON structure, and
then all of the structure can be made directly available onto any kind of a front end,

### [1:01:07]

you can build with React, Angular, any particular framework you like. Now, I will quickly go through
this particular structure built with Lang graph. So the update py when the code files will be
shared, you will see that this particular is the overall stream with codes and structure, and here
you will find a run pipeline function where it is running the Lang graph pipeline. So it is calling
this build graph, it is defining all the initial state where it's defining whatever product name,
category, keywords, search questions, like all of the different types of variables that will be
assigned during the overall agent execution process, and these are like, again, kind of stream with
codes and whenever each of the nodes would be running, we would be able to like kind of, it's like a
planner waiting, executor waiting, like whatever the statuses we saw on the screen, right? And here
all the executions will do, and like I said, there's a simple stream with a front end workflow
process where it is calling each of the nodes as in required from Lang graph, getting the data and
presenting it onto the screen, right? So all the planner, summarizer, all the stages are defined
here. Now, what we'll go and do is we'll go here, we'll first see the graph part because that is the
backbone of the overall Lang graph structure. So in the build graph part, we have particularly
defined the structure like this, pass query, discovery via SERP node, meaning the SERP or APA, it
can find the next part. Here, this is also a sequential flow, then clean data, meaning whatever data
we got from the web, clean the data, scrape the news. Now here, instead of kind of just getting

### [1:03:09]

the web search snippets from the web, we are going to make use of the URL and also scrape the
overall news we get from it. Then we are going to do a generate report node. So this all five nodes
will run into the process. The entry point would be the pass query and it will end at generate
report part. So all of these five steps would execute and in a sequential flow. The nodes file will
contain all of this node, the pass query node, if you want to check the pass query node. So what it
does is it calls this research plan generator. The plan generator is going to generate the plan and
it stores the different variables in our state, the graph state, what is the product name, category.
Now you can relate it to this if I go ahead. Here you will see product identified zoom, category,
video conferring category, search questions, news queries, all of these things would be created and
stored here into the state of the graph. Now, if you want to go and check this research plan
generator, so everything related to LLM calls and everything would lie here in this LLM file, query
parser and research copilot. So all the LLM prompts, so here you would find the prompt for the final
report that we are generating, market research synthesizer, the query parser would be the one that
is generating the research plan generator. So all the calls, the functions and everything related to
LLM will be present inside the LLM folder. The graph folder is just the land graph structure. The
cleaners folder will contain different set of data cleaners like the extract AI snippet, the
parallel LLM prompt and with respect to Google News, no, we can just filter out certain thing.

### [1:05:10]

There will be a clean Google News function, meaning we can remove out certain information if
required. We will remove any must not contain low signal tutorial keywords, so all of these things.
If there are URL duplications, we will remove, we will not scrape those links, so all of these
things, clean and all the things are present inside the cleaners folder. With respect to overall
process and the tools process, the SERP meaning it searches onto the Google and the web scraping
part where it make users of a library called as Trefila Tura, which based on a URL will give you all
the text based data and whatever text data we would be getting, we can pass it to the LLM to
generate the report and stuff. So this is how the overall, the structure we have given. So you can
see how like with respect to CREU AI, we had simple structured flow, but with the issues that might
come up with CREU AI when you scale up particular project or when you start increasing the
complexity, you would find that you want to customize a lot of different points into the code base
and at that particular point of time, the abstracted things like CREU AI might allow some things to
customize, might not allow some things to be customized. So Langraph kind of a framework, they can
help us out to define everything into a certain kind of sections, but now you have control over how
you can define each node in a particular way, you have all the customization available. The only
abstractions they provide us is for example,

### [1:07:10]

they would kind of, let's say with respect to Lang chain, there would be certain abstractions
already available in Lang chain, like you can call up a chat model, normal model, there would be
certain again tools, predefined tools already there into Lang graph, now the server heavily tools
are already available as a tools into the Lang chain, Lang graph libraries. We might have already
directly used it, but why we define this as a particular function by function part is because we
want to like kind of show you how this process can also be defined from the very base, from the very
scratch, and then we can convert it into a proper structure connected all together into a graphical
structure like this, a simple sequential flow. Now here, you can also define multiple flows where
you can define hierarchical structures and a lot of different structures, right? So all of these
things can be controlled by a Lang graph. Great, so this code base also will be shared with you all.
Further, as we go ahead into more sessions where we would get introduced with Lang graph, you can
revisit this course, you would be able to understand more about how a particular piece of code is
written, why it follows a certain structure, why you would, like for those who don't know why Lang
graph has the word graph in the name, because it helps us build graphical workflows like could be
like all the patterns we saw earlier into the session, hierarchical patterns, parallel patterns, all
of those patterns can be built simply via graphical structure, like the way you like.

### [1:09:11]

And in that case, you would not have to depend on two predefined patterns that would have been given
already into the Krivi framework. So Lang graph allows us a lot of customizations, flexibility to
write the code the way we want to define. So now just talking about the limitations during this
architecture, okay. Now the system, both the code bases we saw, the first code base we saw. was kind
of more simpler, more the next code base, which we saw was how we defined each use cases or each
piece of node code step-by-step and then how we can connect all of them together into a graphical
structure. Now, here there are a lot of things when we think from a total production complete agent,
there are a few things which would be missing. Now, why these are not included is because a lot of
concepts are still yet to be covered. So when the LLM Ops part, the deployment part, and a lot of
things would be covered, all of these things you would be able to understand, you will be able to
build by your own, and at that point of time you might add this particular logic automatically into
the system. But just to understand what things we would like to add into this particular structure
would be to having a retry logic, like I mentioned retry logic multiple times. Whenever the planner
structure might fail, you would like to add a retry logic so that it can re-plan. Another reason, no
caching layer, meaning you might have already generated some research

### [1:11:11]

already for some particular company or particular let's say compliance. You identified this as the
same request, so caching layer, a memory layer where you can recall previously generated
researchers, have a look at them, and with that particular memory you can help the model itself to
give more information based on previous memories. You can add cost governance, meaning the model is
doing multiple researches, it is doing web search, getting data from multiple sources. Now it might
have collected a lot of data, so there might be a particular budget for one single request. If there
are let's say 20 sources created by the LLM, there would be a lot of processing, a lot of number of
tokens might be used. There is something called cost governance which we will talk about during the
deployment evaluation phases of the LLM OAPS pipeline. To add this cost governance, like cutting of
certain sources which might not be required, cutting of certain processes, budgeting related cost
governance things, then you also didn't have any sort of a parallelization, meaning the tool calls
might have been parallelized or a lot of different things, or if we add more number of nodes here,
more number of tools to look into, we can have also added a parallel execution flow. Just to think
it from a perspective, like when we try to achieve some sort of architectural maturity into an
agentic system, it will always be incremental. You won't be able to figure out all of these things
at once because the agentic, like you would need to experiment with an AI LLM model, you would need
to experiment with how the model

### [1:13:14]

is interacting with the tool, you wouldn't identify how is the results coming in, are the results
good to serve it back to the users, do you need to fine tune the model. So during all of these
processes, automatically you would understand, you would start having that architectural maturity
over time, the oral architecture will also mature and you would have all of these different things
in places such that fallback approaches, different sorts of feedback mechanisms, everything will
come together into places. So the way how we find an agentic architecture would be a step-by-step
sequential process in itself as well. So yeah, before concluding, right? So like we read the last
slide, but I guess there was this one question, can you visualize graphs generated by LandGraph,
right? Okay, fine. So just give me a second, I will try to generate the graphs generated by it. So I
added this, so once the graph is compiled, what we just need to do is we need to ask the, so like
this is an inbuilt LandGraph function itself, do draw mermaid PNG, and from it we can simply store
it as a PNG workflow file. So I have simply done it, so you can see how sequential it goes, whatever
function names are given, pass query, discover, serve, clean data, scrape news, generate report. The
same flow it will follow, pass query, clean data, generate report, and the start means the graph got
user input,

### [1:15:16]

and end means whatever final result, like the final node we had, this generate report node, once the
particular generate report node's execution is done, meaning this end node is hit. So this is how
the particular LandGraph graph is this, yes. So, right, so what we built today, right, like we saw
like two different code bases, one is by Creo AI, one is by LandGraph. With respect to Creo AI, we
built a schema-driven planning layer, implemented role-based agents, added tools like support, we
added evidence-backed reporting, meaning like we added that few rules, right, where we removed the
URLs from the, like, or add not available, something like that, and executed via sequential Creo
orchestration. And apart from this, with respect to LandGraph, we just got introduced to the
LandGraph structure, just to show how the graphical workflow it gives, and for tasks or for cases
where we want to have custom control over the code base, where there are a lot of things we want to
define by ourselves, have a lot of control, in those cases, LandGraph would be a better choice
compared to the Creo AI framework. And then at last, we also saw to just, just to generate the image
of the workflow, there is already an inbuilt LandGraph function, you can simply call it, and this
kind of a moment diagram will get generated. Yeah. Yes, Saurabh, you can give them access to mics.

### [1:17:17]

Yeah, it's already given. Already given, okay. Yeah, you already will be there. Go ahead, MS. Hi,
Charan. My question here is, we have multiple, in this example, we have multiple agents. Each will
do a particular task, and it is sequential. So if I have a decide, agent one will go for one LLM,
and agent two will go for a different LLM, will have any collusions between the results from the
agent one to the agent two, since the task is sequential, but the results are coming from different
model, will there be any debate between them? Identically, no, there won't be any debate because at
the next step, whatever different LLM is there, it is anyhow just receiving a text input, right? It
is not dependent on the architecture of the other model, the only thing that might be required to
check in this case is, like kind of, let's say, you are having a pipeline where you are generating
prompt or you are generating some sort of action to be done by the next LLM. In those cases, it is
usually observed that, let's say, you have the first model of open A model, the next model you have
open A model, the next model you are choosing is from Anthropic. In those cases, maybe the way the
prompting open A does, that might not be suitable for Anthropic, but in case you are just having
executions or task-based agents where they are getting some certain input,

### [1:19:17]

could be a text input, could be a kind of a form-based input that they are receiving this five
particular inputs and based on that, it has to act. Then in those cases, there won't be any issue to
work around. Okay, thank you. That is question, where can we find free API keys? Okay, just give me
a second, I will show that as well. So if you want to go with LLM, you might need to choose Gemini
because OpenA won't allow you a free API keys access. So for that, you can use Google Gemini's free
version. And for the web search keys, there are three different services. I will show all the three.
Yeah. So this is one sub API. The sub API is used for in the LandGraph code base. So it would give
you all the research and everything. And all of these things have a limit per month. Same goes for
Tevely. Once you log into the Tevely, you can create a API keys here, create a new API key. And it
will show you right limited to 100 tickets per minute, limit monthly usage. Thousand is already
given.

### [1:21:18]

And this is the other server, like the server and sub API, both are different. Both are eventually
the same makes Google search, but they are just two different setups. And here you can have your API
key. Whatever credits would be left would be shown here. So from this, you can get access to any of
the web search API keys you like.

# Building a Perplexity-Style GenAI Application with LLMOps — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Building a Perplexity-Style GenAI Application with LLMOps](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/77482006-building-a-perplexity-style-genai-application-with-llmops)
> · Video lesson, 103 min (`1:43:18`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:04]

Hi, everyone. Good evening. Welcome to the session. So please confirm if my audio and recorded
screen both are proper. Thanks. So yeah, as you all know, today's session is particularly based on
LLM MOOCs. And in this, we are technically going to take an example of a perplexity kind of a clone
styled workflow that we'll see in the code base. But apart from that, our major point to understand
throughout the session would be that where exactly is the LLM MOOCs, what are the tools available,
and what kind of things do we actually track by using different kinds of LLM tools during the
production setup. So that is what the major target should be in the session. So let's say you have a
productionized and LLM application. But there are certain things that a lot of, as I would say,
let's say earlier times we used to have things like web applications and different kinds of
applications that after they have been published, usually there are certain kind of similar
technologies where you are still used to maintain the overall production workflow, like auto
evaluations,

### [2:04]

CICD pipelines, and a lot of different similar things. So the idea here is very similar that once a
GENI application is into production, or it's been published, or it's into testing stage, UAT stages,
in those cases, apart from evaluating the overall setup, how the production system can also answer
the operational questions or operational qualities of the system. So something like, was the
response grounded in whatever tool it is used to do a web search, to fetch information from
VectorDB? At what step the agent failed, or the rack pipeline failed, how long the request
processing took place, the number of model tokens consumed during the overall process, the estimated
cost, guardrails, when were the guardrails triggered, and how is the quality of the system, is it
improving, or is it declining over time? So these are different kind of questions from the system
perspective is where we try to look. So that is where we try to use a few six-step methodology, as
you can see on the screen. Our oral process generally is data. We prepare the data either for
storing into Vector Database, or for fine-tuning, or concrete context for our agents. Then we build
around the data, like prompting, rack models, tools, agents, and everything. Then we tend to deploy
it, APIs, whatever format we want to build it into. Then we kind of deploy it, kind of running,

### [4:05]

managing the operations of deployment and everything. Then comes the last, is anyone else not able
to hear me? Just a minute. So as I was mentioning, we have seen a total of these four steps in the
previous last four to five weeks. Now that once we complete these steps, what our essential idea
would be to build around how we can actually improvise the system over time. Now, this is the most
basic or fundamental idea that we have developed over time from the point when we started using
machine learning, deep learning, and everything. So for example, when we used to have machine
learning systems in 2017, 2019, 2020, at that point of time, we used to call this term as MLOps.
Over the time we had certain more types of operations, data ops, deep learning, whatever deep
learning models and everything that was present there, they also combined with the overall idea of
MLOps. So the idea of the overall setup,

### [6:06]

whatever kind of setup we build, considering two things, monitoring, like observing the overall
stage or status of the current system, and how it is performing under different users. Like we do
not collect everything, like users input versus our systems output. We do not collect those, but we
collect different metadata around all of these things, like what was the model's average time to
respond, like how is the agent getting used, how many times a particular sub-agent is used, what is
the amount of tokens getting spent during the overall process. If there is a certain change in the
model or change in the overall pipeline, after making that particular deployment, has there any
change in the production quality, let's say after a week or whenever, is a perfect time to make out
conclusions from the captured data over time. So that is like how we define the monitoring stage and
the evaluation stage. So like most probably evaluation and guidance. Now, previously we saw with
respect to fine-tuning rag or even with the deployment stages, how we can manage the evaluation
part. So same evaluation, how we can automate that into a live running application, and also the
guardrails part. Guardrails part, whenever the input query comes in or whenever a kind of, let's say
there is a cron job kind of a service that runs every, maybe a few hours, a few days, or a few
weeks. So when it runs, the inputs get automatically checked, whatever kind of output it generates
to check that out, everything. So everything as a loop forms the overall LLM kind of a system, and
eventually at the end, the feedback and logs that gets captured

### [8:06]

as a part of the data that contributes to the continuous feedback loop like to improve our system,
right? Now, before starting to the major parts, like the code we'll see today could be a little bit
overwhelming like from the perspective of, if you all have not gone through yet, through the week
six materials, like the MLflow parts and sections, everything could be a little overwhelming to
understand how the things are moving in here and there. So I would suggest just try to understand
from the perspective of how a tool is used, how it is integrated, and the code part, the exact
syntaxes and everything. You can try to practice by yourself. The more you practice, the more you'll
understand that. So just try to take the intuition today, all right? So yeah, now let's start with
this, what exactly is LLM, LLM Ops trying to do here, right? So let's say, right, like DevOps, as I
was mentioning, right, helps us operate software services. On top of that, ML Ops came into picture
that to add data model training, model monitoring, all of those kinds of different processes came
into picture. So DevOps plus maintenance of the machine learning models, the training process and
everything, combined together forms the ML Ops. Now, LLM Ops tries, like kind of inherits both the
processes, but introduces certain level of new failure modes, like prompts can regress over time,
meaning changes in the prompt, or even the same prompt due to certain kind of changes in the. model
quality okay now very known fact that let's say once you take a model into your current setup like
let's say considering two different kinds of setups one is using open source and one is using
proprietary models so let's

### [10:09]

consider using open source models in those cases it is seen that depending on the hardware kind of a
setup the model can also get affected meaning how better are your GPUs the more better processing
power and everything the model can show and it is also seen that a change in the hardware or how the
hardware is processing it let's say we move to a lower end GPU due to certain kind of let's say
budget constraints or anything even though doing that with the same prompt there is a chance that
the model outputs can degrade so that is one noticeable point that has been seen with different
kinds of models the other is proprietary model so you see like all of the times in the news that the
model was like not released by opening anthropic after sometimes a new model got released some of
you might also have experienced this the previous model starts behaving differently or let's say for
example if I remember last year Chad GPT made certain changes to their guardrails into the system
and due to that the model which was previously generating a few things for me started behaving
differently for the same problem so that was very something like certain things that the model pro
it is change at the end due to which there can be a difference in the model outputs that we used to
get so that the same reason we say that prompts can regress or the system that we're accepting the
prompts can also regress like the how what kind of model providers or hardware you're using
retrieval can be weak right the other part model output is also non deterministic in terms of
failure modes for LLM hopes then a tool maybe if you're using some API database can fail midway
during an workflow of an LLM or agent and answer that might be perfect or correct but is taking too
low or too

### [12:11]

much time or is costing too much in terms of the prepared budget or something so all of these
different kind of things is what we try to take it as an answer as a operational quality or the
process quality after we deploy the overall like generative a system or thing and that is what we
call as LLM ops and now the life cycle as we see here is a circular process deployment won't be our
end point production traffic and the evaluation data that we get through by adding integrating this
different kinds of LLM tools and everything when we add up the improvement pipeline based on the
feedback iterative processes and continuously improve so that there's a saying like production
traffic and the should change the next version of the application kind of based on the all the
collected data what do you need to change into a system so before this whatever we did was to
evaluate whether the model is answering correctly refining work perfectly rag happened everything
now once we complete that process model agent that evaluation works and you deploy the system the
system evaluation is also important and that is what we call as observability and the monitoring of
the overall system okay right now let's move towards the core pillars of the LLM ops now this
pillars technically you see here right the six pillars they are all interdependent so for example an
evaluation score without any sort of observability like the trace observing everything will leave us
kind of unable to diagnose what is a bad case what is a good case a trace without any sort of metric
cannot show whether the incident

### [14:12]

is occurring frequently or something right so all of these pillars are interdependent they all
provide certain kind of a measurable decision that can make a new change into the overall
application now the six pillars I guess I was mentioning observability like the one like tries to
provide the request level evidence so it is more like let's say whenever from the front end a user
has added an input that goes to fast API fast API or any other framework you're using for creating
APIs or anything of your system whenever it accepts the request and sends to the agent what happens
inside the agent or the rag pipeline and when it gives the output what is the overall the internal
things that has happened what's the metadata across all of that is what will fall like you know
prepare the request level evidence and the oral idea to take from it would be to what happened
during this particular request like we collect all the metadata that is what observability of the
system would be evaluation evaluation is like when the system generates the response is that
particular like no let's say for example for the same question is the system generating a correct
response a safe response every time is it something like let's say the next step is guardrail right
so guardrail is technically when the input comes in guardrail runs tries to identify whether the
input kind of type is correct whether the source of input is correct or let's say if it is a kind of
a chat word how what is the users input like is the user input relevant for the agent and in terms
of the output guardrails as the system generates the response those response are relevant to use a
query or let's say

### [16:15]

are not something like let's say in certain cases you might have seen for a particular organization
they kind of try to block any references to other competitive organizations information or something
through that AI right so input guardrails output guardrails combined and also as a part of the
evaluation setup that let's say evaluation you do generally at the testing phase of the setup
guardrails is where when you add it after your full main system is developed so you technically try
to only give good information to the system and try to ensure that the system is generating also
good output so that is what the difference between the two would be and then cost and performance
the main part where because all the setups all the systems you would have budget right so let's say
you're an agent each input query to the system should might only be let's say you be using 0.0 5.25
kind of amount of inputs like that is based on how much maybe your monthly spend or maybe a million
tickets how much you should be able to afford all of those different kind of things like no cost is
there and cost versus performance trade off is where the main thing comes off so let's say during
the testing scenario of the overall system you have when you have prepared the cost versus
performance trade-offs are usually seen like let's say what happens if we use a lower hardware what
happens if we use a higher hardware what happens if we use this model what happens if we use the
other model do we require fine-tuning like all this kind of mix and match questions during the
testing phase forms the overall cost to us is performance trade-off so it is also something which is
very experimental like let's say if you're starting a project it would be

### [18:17]

very uncertain to maybe you know like kind of quarter number that our overall system setup would
cost maybe this X amount of dollars or something because at the very end let's say you develop
something you guarantee certain level of performance let's say the stakeholders and everyone
requires a 90% accurate let's say answer relevancy in terms of generating application so to achieve
that if you are burning two dollars and that is not what the budget constraint out there is allowing
you like let's say if the if the if the overall management says you can only spend one dollar per
request or something then in that case there has to be a decision taken on to the cost versus
performance trade-off so these are the kind of things you can look into the cost and performance
part of the world system like this all opens up more clearly during the testing phase when the
results of this testing are maybe not used by the team leads management managers and everything
around how do we develop all of these overall things then configuration management like as I was
mentioning which prompt model provider limits and everything was used and in it another part is that
let's say when the system is built like now the genuine systems are not overall perfect so there are
certain retry loops or in terms of there are certain let's say if we have a land graph workflow in
those cases there is something like repair answers kind of a setup as well so the overall idea is
that let's say the system failed at certain point let's say some API connection got disturbed during
the calling during the call made by the agent or certain service did not give us the response So how
many number of times we can retry or how many like let's say the system generated a response. If
that's a generated response, the guard will say that this is not relevant response. Should we
trigger and like another round

### [20:18]

of the overall workflow maybe in a hope that the system might generate a correct response the second
time because LLMs are probabilistic systems, right? So that retry or repair policies, those kind of
managements and everything also kind of a false under the configuration management and feedback and
improvement part. Now all of these things different details collected usually would be used along
with tools like Grafana and Prometheus like most probably Prometheus you can think as like, you
know, whatever information is getting generated out of all of these pillars. Prometheus is going to
collect the metadata of all of that and Grafana is a tool that can be used to develop the dashboard
for them. So kind of a normal dashboard, a systematic dashboard showing different graphs, matrices
that this is the average token cost. This is the latency of the system and everything. So that is
how the Grafana dashboard would be created and the feedback and improvement will start kicking in
that we need to change certain points here or do we need to make any additions to maybe, you know,
more guardrails or why is the guardrails kicking frequently? Why in certain cases the cost is high?
Why the evaluation is failing for certain cases? So all of this is different things and all
everything. We try to combine, check in together, try to make an overall improvement to a system
using the collected matrices. So this is the overall setup that you should build around the LLM Ops
as an idea, right? Now the project that we'll consider into the system, like we just understood the
LLM Ops, the pillars around LLM Ops, what actually we are trying to see. Now the point would be that
all of those are just different terms or things that we should do.

### [22:18]

Now all of those main six things can be done via different sets of tools, different way or how your
overall production setup works. Like someone might be working with AWS setup, someone with Azure or
someone with open source tools, depending on the kind of setup your organization needs. So depending
on that, you might need to use a readymade system setups or you might need to use whatever setups
your cloud produce gives or you might also need to create your own internal setups to all of that,
right? So these are the different things that you would face issues into. Like if it is just try to
go by using the tools as a setup, let's say for model tracing, if you just learn ML flow, just stick
to it, it might be a problem, but if you just understand the process of what ML flow is trying to
solve, you might be able to use other tools, alternate tools to ML flow or even kind of can build
your own internal tool like an ML flow to trace the setup and everything. Now, for example, ML flow
storing the trace of your overall system is just like storing the data in a kind of a dashboard the
ML flow provides, right? So similar kind of internal applications can also be built by you using,
let's say, maybe something like a small MongoDB database or collection you can have, store the data
and show it over a dashboard similar to ML flow. So it is not something quite hard, but yeah,
certain cases like databases or queuing systems or mechanisms in those kind of cases, you would need
to kind of be dependent on two available tools because creating those kind of similar tools locally
could be more hard than creating tools like ML flow and everything, right? So the application setup
which we would have today is something like that accepts a kind of a research query

### [24:18]

like the public city, like most of you must have used public city, so kind of queries that we put as
an input. Based on the system setup, plans a few number of searches using Tevely, so we are just
using a free Tevely service to get web data. It searches or kind of performs targeted web searches,
generates the output, validate using certain guardrails and if guardrails passes and everything, we
deliver the answer and during the overall process, the idea is to record and store operational data
like logs, traces, cost information, feedback information, any sort of evaluation like if executed
like during the run or outside of the run or system like maybe runs a weekly, monthly evaluation
setup or a manual evaluation was done. So capturing the overall operational data is what our overall
target would be during this project, okay? Next, just going through the overall setup of the
project, so the user experience and main features, okay? So we just have a basic streamlet setup
through which we can ask a pass and just pass in a query. It will go through a process, will
generate the output like this and answer will show us this kind of a message, yes or no, like was
this answer helpful? Show us the sources that were captured through Tevely and the MLflow Grafana
Prefect dashboards are also integrated in the streamlet UI itself. So I will just give you a quick
show to the streamlet UI, right? So like if you're just like after the session when I will share the
code, if you just run the overall Docker setup, this is how you would be able to see your main
streamlet screen. Now here, if you can see here, I have particularly mentioned deterministic demo
mode or live OpenAI plus Tevely mode.

### [26:21]

So technically that is being controlled by the ENV where demo mode is given, like if we put demo
mode equals to true, then in that case, it is going to go through a certain, like without using any
API or my OpenAPI keys, it is going to follow and it is going to just accept a few questions and
going to always generate a fixed answers for that. While if I put demo equal to false and pro at the
OpenAPI key, it is going to fall to the live OpenAI mode. So the idea is to just have some
repeatable inputs, just taking that the system is working in terms of front-end and everything. And
live mode is from the perspective that front-end, back-end and everything is working. So I have set
my current setup to live mode. GPT-4.0 mini is the model that is getting used. Memory that is
associated with the LandGraph workflow is Postgres. And this is how my MLflow, Grafana and
PerfectLagro, the three setups are connected here. So let's say if I just ask a question, how does
MLflow trace a LandGraph agent? So like, as you can see, it is starting the research. It is taking
the query, planning the research. It might take a couple of seconds to just generate the response.
So you can see the sources are listed. So from what source it is taking the information from. And
this is the main response. MLflow traces a LandGraph agent, what kind of inputs. So this is how it
has generated the response. And the feedback, like, is it a good response or a bad response? I'm
just marking it as feedback recorded, right? Now, what things we will look from the perspective of
either MLflow or Grafana? Okay. And also the perfect part. We'll just go through the dashboards. So
this is the main publicity agent. When I click on it into MLflow. So here you would see the basic
dashboard provided by MLflow, like the traces,

### [28:22]

how many times a request was made, what is the average latency, any errors if it has occurred, what
is the token usage, average tokens used per trace. That is around, like, you can see right now it is
2640 around tokens used per trace. What is the overall cost by model and cost over time as well.
Like maybe depending on the day and everything. And if you want to go through a trace, you can click
on traces here, click on any particular trace. And here you will see what inputs were passed. Or you
can also click on this details and timeline. We'll just click on table. So what input came and what
output came through the overall particular node. So let's say input guard, what input came, what
output. Now here, all of these things is what you can define. This is not what MLflow defines. If
you want to store any particular input and you want to store any particular output, that is the
whole control is in your own hand. Like if you want to, let's say internally some database is
working. So let's say that database, how much time it took to give you the data, what data was
requested and what data was generated in the output. If you want to capture all of that, those kinds
of details MLflow can also capture. So this is just MLflow level setting that needs to be altered.
And the overall setup can be easily captured. So that is what, when I mentioned we capture metadata.
So this is how the overall basic metadata is what we'll try to capture. Next is, This is Grafana, so
we can create dashboards. So let's say, I've already created a dashboard like this. So let's say, it
is more like the MLflow dashboard was more towards the usage of the systems in terms of LLM. The
Grafana or the Prometheus setups

### [30:24]

is more towards the API side of it. So what is the API requested, how many requests are coming, what
is the overall latency of the API, guardrail decisions, like any amount of, I would say, like is the
guardrail passing or if it is failing. If it was failing anywhere, it would have shown some red
marks here. What is the node level latency also? That is what we have captured. Search web node is
there inside LandGraf. What is the latency for that and what are the latency for different nodes?
What is the general latency for LLM? Let's say, multiple nodes might be calling multiple LLMs. So
during each of the LLM calls, what is the general latency for that? What is the heavily searched
latency? What are the agent outcomes? Is it overall success over time or is it failing or something
like that? So from a systems perspective, what are the different data that is collected, the data in
the LLM is captured here, and Prefect we are having that is used as a weekly evaluation setup for my
system. So you can see now, we have a scheduled evaluation setup that will run tomorrow. There's a
weekly last run executed on 10.8, so if I just click on this one evaluation. So we have just added a
few data points into Prefect is just like Cron service, or you can kind of think as an alternative
to Airflow, like runs workflows based on time, times or scheduled runs and everything like that. And
you can also check on different things, like if a little case, right. So right, so here in this
case,

### [32:24]

Prefect, like if you want to also log something out of Prefect, like what was the result of the
Outflow and everything, that is also what you can store as an artifact. But usually, as we are just
going through the evaluation, the overall output would be, is the evaluation passing? Like whatever,
let's say library, you're using maybe TP-Val, TrueLens, or you are having a custom setup that is
measuring a percentage of quality. When, like you can just have a if-else kind of a statement. If
that particular value is fine, that means your overall setup is running. And now here in this case,
Prefect is not going to show you is the particular evaluation perfectly fine or wrong. It is just
going to show you has the weekly evaluation setup executed, completed or not, right. And to check it
in terms of weekly evaluation, I guess this is not capturing it, yeah. But the overall idea would be
to whatever output they're generating that should be stored somewhere, either as a JSON or whatever
library you're using. And based on that number is what you're going to take the action as a next
step. Like once the evaluation is completed, like we all know, like from a fine tuning perspective,
rack perspective, how do we try to implement changes in the prompt, change the model or something.
So that is what different kinds of things which you will take into consideration. So these are the
three different kinds of setups which we have included. And going to the next step, that is the
technology stack that we have in our overall code base. So in the code base, like you can see, we
have like the stream data and fast API that forms the product or the project's main application
layer, the UI and the backend or frontend. Land graph, like you used to set up the main agent.

### [34:27]

Then there is also provider adapter. So this is not through any library or something. This is just
that we have created a kind of a setup through which the overall idea is that there should be
provider abstraction. Why? Because what majorly happens is that let's say you wrote a code that is
with integrated into OpenAI. Now, after a certain time, there is an anthropic model, Google model
that you think is performing well or you want to switch to OpenSUSE model. In those cases, it is
more better to have something like an adapter setting, an adapter way of coding where you kind of
isolate the model setups and also along with it, any kind of API services, search API and
everything. And once you abstract it, the overall idea should be that the agent is going to call a
particular piece of code and that piece of code is calling this provider. So the overall idea would
be, let's say you wrote a code, you had LLM calls at 12 points. Now, instead of replacing the code
at 12 points, what you do is you add a new provider into your system setup and just replace the
provider equals to configuration value. Let's say provider equal to OpenAI, instead of OpenAI, you
put it into Anthropic. The whole, the other 12 points that were depending onto the LLM will use the
same code, will just switch to an alternate provider. So there will be some code addition definitely
in terms of provider settings, but that would be less harder considering instead of changing the
code at 12 different points. So that is why we have certain level of provider abstraction to be
added. For guardrails, we are using guardrails AI, but one thing to point here is that we're just
using the validator framework from guardrail

### [36:29]

that is kind of like, you know, just working as a main base pipeline, like as a main class. There
are other kinds of guardrails also available onto guardrails AI. So for example, if I go to their
main website, so I just came through this main website. So here you'd see a lot of different kinds
of validators that is being into public by the users. So something like banlist, bias check. So
let's say banlist is something like the output does not contain any bad words, that users are fuzzy
search, bias check is there that validates in terms of age, gender, so output is or not in terms of
that. So what kind of setting is used? So here you might notice now some kind of a model is used. So
you can see some TensorFlow kind of a service is used. So most basically it is using a small model
to identify if there is any biases or everything. So similar to this, guardrails AI provides a
framework, like provides a basic validator kind of a services and all. And these are of the few
basic validators they provide, or you can also create a validator like this, just you need to import
the guardrails AI setup and whatever I would say the guardrails setup that you generate, you just
use the guardrail architecture and put that code inside that as a function. So that will kind of
make a part of the overall guardrails AI framework. So we'll also go through the code that the setup
is there. It's a very simple setup, but yeah, just for understanding, we'll also go through that
particular code setup once.

### [38:31]

Then for tracing, we're using MLflow as we just saw the dashboard. Monitoring, we're going through
Prometheus plus Grafana. Prometheus is capturing the matrices. Grafana is showing that dashboards.
Automation, the evaluation automation that we have is through Prefect, like Prefect as I mentioned
is kind of a similar to Airflow kind of an alternative. Data, we are using Postgres to store the
data into a database. Redis is also involved. Redis is, we are not using anywhere with the agent or
our production setup. Redis is kind of used along with Prefect. So all of the Prefect's internal
messaging happens via Redis. So Redis is added as a part of the automation that Prefect requires.
And our main runtime is a Docker Composer. So Docker Composer is having all of this information
combined collectively, okay. Now coming to our main codeway structure, okay. Before that, just
please give me a minute. I think someone is at my door. Just give me a minute, I will just be back.

### [40:36]

Yeah, so so yeah now in terms of our code with structure like just how the code structure is defined
into the project. We have an apps folder that has the API and front end all the code associated with
faster faster API and stream it there is a packages folder that has all the like, you know agent
providers like major LLM packages that we have so agent folder contains all the code with respect to
Lang graph providers has all the information with respect to the adapters as I was mentioning the
LLM adapters guardrails has all the input output guardrails setup observability defines the MLflow
tracing setup and the Prometheus matrices storage just the Postgres storage with respect to know
whatever information we want to store automation consist of the perfect setup inside the flows and
the data sets has the golden evaluation like the golden data set that would be used by the perfect
automation monitoring is like no kind of you can think the Grafana dashboard setup and everything
and in phrase just a Postgres visualization that is just a script that will define the tables inside
the Postgres database next is to understand the overall end-to-end system architecture. So just to
understand it like you can read this diagram from the main input point the user point. So the
request path technically begins at stream lit the interface sends question to faster pay and keeps
the connection the connection is used as an API service the fast API invokes the input guard

### [42:36]

before the land graph workflow like invokes any sort of LLM call or anything and inside the main
land graph workflow the different kinds of nodes work like plan search search web grading of the
sources generate answer the output guard everything works in if it generates a validated answer
sends back to fast API and which gets shown on to the stream.io as we already saw on to the
stream.io how the response comes up and during the two process one is like no we know that during
the one is refine and one is repair or retry right so grading of the sources like whenever it
searches on to the web it like no like grade the source if are the source relevant to the input
query if they are but if they are not there is a refine search meaning it retries for a web search
if in case the output guardrail fails in that case the system will tend to repair the answer like
make an LLM call stating that this was the input query this were the web sources how do you produce
a correct response or the earlier response that was generated was wrong please refine your
particular or repair the particular response and once it passes that then only the validation answer
will go and there is only like in the current configuration we only added max one refinement or max
one repair otherwise usually systems have seen to have three repair setups like looping setup so it
might try a couple of times because sometimes an API could be failing sometimes LLM output could be
failing sometimes web search could be failing so depending on all of the different things there is a
couple of repair retry setups that is being added now the provider adapters are connected across all
of the nodes could be demo mode or live mode and here how the MLflow and everything connects is

### [44:38]

MLflow is connected with the main agentic structure like with the fast API structure so when the
fast API kicks in the land graph agent MLflow also gets integrated with the overall setup so it
creates the traces of the overall land graph agent and whatever information the system and it
generates the fast API system that information metadata gets sent to Prometheus Prometheus shares it
with Grafana Grafana shows us the dashboards like as we saw and in terms of Postgres Postgres has
three databases one is app databases that is storing the like you can think from the chat like the
AI user input output Postgres stores so app DB is configured in that particular format MLflow DB is
there that stores the information of MLflow Prefect DB is there which is storing the information
that we see under the Prefect and Prefect uses the Redis for the Prefect messaging inputs and
outputs like it is an internal dependency so this is how the overall end to end system architecture
would look like and to understand a single request flow like as I was mentioning user question comes
in fast API receives the request plus request ID generated by the system input guard works the land
graph service kicks in searching of the plan the web searches grading that evidence or if any
refinement is needed final answer is generated output guard kicks in repair if the output is not
good enough for the end user even if it passes validated answer gets sent back to the user at the
same time all of the LLM processes works the MLflow tracing the collection of matrices via
Prometheus the land graph checkpointing that is getting stored with the Postgres feedback is also

### [46:40]

persisted like the thumbs up thumbs down button we saw on to the stream that also gets persisted and
perfect automation is also there that gets executed weekly using the golden data set that is
restored into the data set folder so all of these things kind of happens at the same time whenever
user question kicks in now just understanding it from the docker perspective so we have a docker
file and also docker compose.yml so this is just like a diagram like what we have into our main
docker setup so we have front end API MLflow is also container perfect is also container Prometheus
Grafana are also separate containers they have got both different tools in all together Postgres is
there and Redis is also there and there is a docker file that is for the main backend so kind of
installs python installs all the libraries and from there it runs the main fast API backend and
instead of pip here we have particularly added code to use UV because UV is a much more faster
library setup like you have seen like even I am using UV more frequently than pip because UV like if
I compare it particularly let's say for pip is installing a library in a minute UV is going to
install the same library in 15 minutes 20 minutes like UV is written in Rust versus the pip that is
written already quite decade old setup with C, C++ libraries and to just run the stack you can just
simply do download the overall project repository docker compose up build and this will start all
the containers so I will just show you the number of containers so you can see Redis Prometheus
working MLflow, Grafana, Frontend, API, Postgres is working

### [48:41]

and in respect to prefect multiple servers are running this is due to because prefect is a
combination of multiple things like a prefect dashboard is there so there is a prefect server that
is the dashboard what we saw behind this dashboard is a prefect worker so prefect worker is what is
going to execute a scheduled task and there is also a prefect deployer so this prefect deployer is
technically used for manual trigger so whenever I make a manual trigger this prefect deployer
container would start run that manual task and will automatically stop so this is why we have
multiple prefect services because the architecture of the overall prefect system is designed in that
particular format so that is how overall all the services are set up and even if we go and see the
Dockerfile, this is the main Dockerfile as I was mentioning for the FastAPS service which triggers
the uvcon command and docker compose has all the other sorts of information like the Postgres
database setup, the Redis setup, the MLflow setup so it contains all the information on what things
the MLflow would use so MLflow dbupgrade, Postgres, so MLflow is going to use Postgres database,
MLflow run command so MLflow server so this command would be used to start the MLflow dashboard
where on what a port it is going to do, what is the health check command, so checking the MLflow
health, the local running health check command to identify if the particular container is running
perfectly or not. Similar to that, our API service, front-end service, prefect server is there, so
prefect server start, and the way we separate it, the prefect deployer, so prefect deployer is there
as a different setup,

### [50:42]

prefect worker, so that is how all the different containers, images, services, so Prometheus,
Grafana, images are being captured from the latest versions, and the command to run this are also
given here. So that is our overall Docker Compose setup is there, and that is going to trigger all
of the services. Next is our main fast API. So fast API is technically built as a main.py file of
our code-based setup, so you would be able to find it inside the apps folder, API folder, main.py,
front-end is there in our app.py, so this is all what's going to trigger our Streamlit workflow. The
main.py file, like if you directly start observing it, you would see different settings here, like
from the packages folder, we have imported multiple things, like the agent service, packages.core
configuration, we are importing the configuration settings directly via the nvar.env file. All these
schemas necessary, like in terms of fast API, API, like what should be the input request, feedback
request, feedback response, service status of the overall application, answer response, how to
generate the response JSON, then from the guardrails, we're importing the guardrails, and from the
observability package folder, we're importing the feedback metrics, HTTP, so these are all from the
Prometheus services, these are different observability metrics that we're capturing, and here you
would also notice, maybe not here, this research service, so this research service,

### [52:43]

so from the agent is what is going, like I'm just trying to explain you one way of how it is
importing, so this goes to packages, inside the packages.agent is goes to this service file, so it
is technically going through the service file, so inside service file, you will find this class
research service, so what does this research service is, it's having like the run function that is
taking the input that is coming from streamlet, you would be able to notice here, graph.invoke, all
the commands related to the land graph agent, so all the folders follow a very similar structure,
each folder has kind of all the necessary codes for a particular LLM Ops tool or a technology to be
combined into a main setup, one is like the main agent is there, observability, guardrails, provider
storage is different, and if you let's say, here observe from the observability part, let's say
here, it is tracing context, or maybe we'll look at something, let's say provider is there, yeah, so
this service file indirectly calls our main agent state, and if you notice the other files, graph,
state and nodes, what you will find is, it is all using this different kind of packages, the agent,
core packages, the core is technically defining, or calling up the pidentix settings to import
different variables from the ENV file, and the other files you'll notice as I was mentioning, all
the matrices that needs to be captured for a particular setting in the agent, so here you will
notice, here we are capturing sources,

### [54:45]

observe node in this file from the observability, where did it go, estimate, so many files, so yeah,
here in this case, you might see agent duration, different observable matrix were imported, so
depending on the file, depending on what matrices needs to be imported, we have separated them all
along, and in the nodes.py where it is going to make LLM calls, we're also importing this LLM
provider here, you would be able to see here, so this all connects to this LLM provider, if I show
you, and this connects to the base file, now this base file is again connecting to multiple files,
like the live file, where all the providers are added, so live file is only technically the live web
search, and the OpenAI file, so OpenAI LLM provider, what model name, input cost, what is the
setting, what is the method of calling this OpenAI model, so chat OpenAI from the Langton service we
are using, then this is the function for recording LLM usage, so provider is equal to OpenAI
calculation of output cost per million tokens, so N number of functions and everything are all
combined together to form this provider adapters, like as you see, so here I would suggest you go
through, each of these folders, go through all the code connections one by one, so then and then
only you'll be majorly able to understand the code connections, explaining it is a little too, going
from one file to another file could be a very much time consuming process, so the whole idea, like
as I was mentioning, I just showed you how all of this is connected, each of the files is calling
important imports from the other folders that is as in when necessary required,

### [56:48]

and the provider adapters, how they're defined, here in the packages setup, like we defined all the
providers and the other main files that require that particular provider, so let's say you wanted to
have entropic LLM provider, so you can design a similar class, all the code might still remain the
same, only you might need to change the self dot model, change with instead of chat open it, chat
entropic AI, depending on what kind of library you're using, so let's say here it is LandGraph, you
might need to change to chat entropic AI, so that is how the oral setup will change, that is how
also the adapters help us out, right? Now, the FastAPA technically has this basic endpoints, the
search one that is going to send the input to the LandGraph in the input guard, everything kicks in,
gets validated, everything gets combined, and the final response gets generated, there is also SCC
streaming, that is more towards like the streaming endpoint that generates the output in streams,
feedback, whatever user submits, just API to store the output in Postgres DB status, so how many
services are running and everything correctly, health, just API is up, and Matrices, Matrices is
technically just a Prometheus metadata that is collected, so technically, whatever Matrices gets
generated during the FastAPA processes, Prometheus gets the information from this Matrices endpoint,
Streamlet, I guess I already discussed, now the main LandGraph workflow, so the LandGraph workflow
is pretty simple, like as we've discussed in the previous slides as well, the plan search node is
there, which passes the information to search web, now plan search is technically either one search
or multiple searches, so the search web executes those number of searches, collects results,

### [58:48]

the grade sources node grades the information, if it is sufficient information is there, or the
retry or refine limit is reached, the information gets sent to generate answer, the output guard
validates it if it is valid, the answer is considered completed, if it is not valid, it gets sent to
the repair answer node, which is also LLM, so an LLM will try to reformat the answer, such that the
output guard should be able to process it, and there is also this refine search, so if the grade
sources, if it says that this is a weak web sources, weak evidence is collected, a refine search
meaning a new plan search could be there, or new web searches would be executed, and it will again
regrade the sources, so that is how the oral LandGraph flow works in our code, now a few of the
things to be discussed here in terms of bounded loops, now when to use this loops and all, is also
something to be like as I was discussing, so let's say in terms of our current setup, we have this
kind of weak evidence setup, So we are having one search refinement that is just to cover in case
web search fails or some good information is not considered. Now instead of a retry there are a few
other mechanisms as well maybe let's say you have a by default search of Tevely if it fails you can
switch to a more costlier service maybe you know like you have a setup where you use a cost-
effective service if it is able to provide information if it does not provide you move to a more
costly service maybe something like let's say server service google service so that gives you maybe
you know maybe give you more information or same retry service for Tevely those kind of different
options you can also generate here in terms of these loops invalid output is also one of the very
important problems is there like as we know LLMs are probabilistic for the same input they can

### [1:00:53]

generate different outputs as well depending upon the load that the load is there onto a system onto
a setup how complex is your setup and everything so just to give a chance to recover from the
overall setup we can set up a few retries mechanism under setup maybe a single retry or a multiple
retries could be added then the prompt injection is there so maybe let's say you can like we saw it
in the earlier setups agents and all we used to have those query rewriters or the router nodes so in
those cases along with guardrails can also be used so maybe let's say the guardrail checks if the
input and everything is correct or not if even that passes maybe the input was not as per our
systems requirement or something so in that case an LLM at the router node and anything can kind of
define or route to a particular state that this is not a system related input or something and route
it to maybe some kind of a different U1 in the loop setup or everything then unsafe source so
getting it filtered the retrieval so maybe again some kind of a guardrail setup is there persistent
invalid answer so even after multiple tries or let's say three tries guardrail still says the output
answer is invalid not according to the user input or is a not a good response so maybe you know you
should have some sort of a output that throws a predefined message that currently the system is
under certain load or not able to generate response like instead of giving a wrong response it is
better to not give a response that that should also be a part of the system settings and slower
failing provider so maybe let's say if a provider fails how do you change to the other provider so
you

### [1:02:57]

could have a back-end call let's say there is a maybe a health check with respect to a particular
provider or if or let's say you have an API you keep checking it you have a container you keep
checking if the container is running if any of the things fails what is the number of retries you
want to do and if they also fail what is the fallback approach you want to maybe you would have a
fallback API you would have a fallback response you would have a fallback model provider so all of
these things also needs to be defined that is what we called as bounded loops like different kind of
loops that like once a thing fails how do you try to have a fallback approach on refining the
overall process so this is also what like maybe we call it as a part of the loop engineering
nowadays as people are calling or how to make your system more reliable in terms of different types
of failures so these are all just concepts everything is like you know how do you code it out how do
you want to do it but this is something a few of the things that from a genuine architecture
perspective you should be building upon next the provider abstraction as we were discussing so
technically like the main you you would be defining a main protocol like as you as we saw right the
main answer generating LLM there is a there is another function for planning like let's say there
are multiple different types of LLM that is to be called there is also going to be a repair
statement so maybe you know even I believe our setup also has repair statements you can see here
there is a repair setup as well so this repair setup what is does is in case of guardrail triggers
any output answer validation fails in that case from the model this repair function would run and
you would have a different input prompt like repair the answer so every cited number map so this is
like just how you can define the prompt

### [1:04:58]

for the repair condition so it gets the question evidence draft response and any sort of answer that
it needs to build so all of the different level LLM calls and everything also gets added to your
main LLM provider abstraction so abstraction is very necessary because this is going to handle lots
of different LLMs different tools different API service all you can abstract it up here and your
main Langer of orchestrator is going to just call in this different abstractions behind the
abstractions whatever integrations plugins that you want to do you do so thus to save the effort in
changing a code a number of times could be saved like changing an LLM the time could be saved
changing an API service it also can also save so that is the overall idea of the provider
abstraction next is guardrails as I was mentioning so technically we have three different types of
guards in any kind of a generated system input output and retrieval input is technically we try to
check things like is the query size width and limit are there any like the the basic guardrail
setups as we saw also also so on to the guardrail hub any kind of a competitor checking any kind of
bias checking any kind of prompt injection patterns now for example the user like in the chatbot
systems also the user tries to add something you know jail breaks and all like we continuously see
on to linkedin and other platforms as well people try to mess around with the AI systems so if any
kind of prompt injection patterns are detected so guardrails like that any personal information
email addresses mobile numbers api's if any kind of those things are detected usually they are
hidden or they're removed from the prompt and that prompt is passed to the further system settings
any sensitive content any kind of a self-harm

### [1:07:02]

illegal activity questioning questions like how to make a bomb or anything kind of a input question
those kind of questions are passed to the system how to reject answering those questions or how to
send a response to the user stating that we cannot provide a response to this kind of questions or
something so how to pass those certain level of inputs how to mask or remove sensitive parts from
the inputs or how to block and provide a safe message to illegal sensitive content categories that
is what our task should be there for with respect to input guardrails with respect to output
guardrails this is more like you know what was the user question and how is the answer relevancy if
the if the output that is generated by the final llm is it generating the answer based on the tools
it has used during the process it is it is generating the response from the retrieved sources that
is also a few things need to be checked and any kind of like you know secrets leakage key leakage or
any kind of code level information the model is outputting any hallucination is detected by any llm
as a judge kind of a setup and also if your system has certain level of length and format settings
so if the output is in markdown format checking if the output is in markdown is generated so all of
these things would be part of the output guardrails so again pass redactant block settings would be
there if it is passing if you need to retry an output generation again or you need to just provide a
safe message that we are not able to currently process your request you may try after sometime
something like responses you also see and the final type of guardrails that is the retrieval so
retrieval is technically could be from the kind of services so what level of retrievals your systems
can do from where to

### [1:09:09]

fetch the information what tools to use when it makes a web search are all the web results unique or
you need to go through a deduplication information so something like that let's say you make 10
searches on web it gives you three to four duplicate content so deduplication is necessary otherwise
llm would be biased towards that same three to four duplicated content could be from web search
could be from vector db is the vector db generated responses like do you need to rerank it after re-
ranking how is the retrieval quality and all that is also you need to check and any kind of let's
say vector db output is there what is the confidence score of that retrieval if the confidence score
is low maybe you can you can make a retry for retrieval so that is what the retrieval level
guardrails would be Now, in terms of guardrail code, as I was mentioning, if you're going to use
guardrails directly from the guardrails AI, they just have a certain level setups there. So you can
basically use those setups as given, but if you want to create your own, so for example, this is one
example. Let's say we're importing rejects patterns and we're just making a reject setup, asking it,
stating that patterns, if this particular patterns pass or fail, if any, then we're just going to
return fail result or return pass result. So this is all connected to a guardrail setup. So for
example, if I would show you, this service when the validators part. So here you can see from
guardrails library we're importing a few things, like guardrails with validators, import, fail
result, pass result, and validator. So whenever we write any validator function, whenever we create
the class, we are wrapping up that class inside the base class for validator. And output of this
would always be wrapped inside

### [1:11:11]

either the fail result or pass result. So what it is going to do is that whenever you import this
guardrails anywhere across the code, whenever we call this particular guardrail, the output which
will receive it will always be either true or false. So that is what we're going to be using it here
because that abstracts our way of having the if else conditions to identify whether the system is
passing, like even after let's say this validate function runs, we just get the information that
what is the number of max characters. After that, we return that value to the agent at the agent
level. We write certain setups and everything. So this is just a level of abstraction and this
abstraction pro access with metadata. Metadata like this particular query length function was called
and the output of it is it passed or failed. So just to kind of copy the level of code base that the
I would say guardrails AIS build around their framework, the same kind of framework we can use to
create one local similar kind of guardrail setups that can easily fetch and use the information
again and again. So this has come some kind of reusable code setups that you can connect it to the
oops level setups, like we have our main validator as a base class that is imported and we generate
output in a certain format that can be reused across the oral code base. So that is how we create
reusable guardrail codes that we can use across the setup. So there's two type of example of
guardrails that we have seen here. One is prompt injection and one is this output validation policy.
So difference between the two is this prompt injection you see is the main guardrails AIS setup.

### [1:13:12]

It just generates the output as a pass or a fail result. So like input is safe, the Landgraaf
process continues the process, fail result, input is blocked and some sort of a safe response gets
sent back to the user. And this is the output validation. So here, technically this is an inside
Landgraaf workflow where if the final answer is, let's say it's correct, we just state the output is
valid if the output requires some reattempts. So just checking if there are any repair attempts
available depending on your configuration, one reattempt, three reattempts. So based on that max
repair value, we're just checking if the max attempts are reached. If not, then we can make another
repair attempt. If not, then just block true, meaning the final generated answer even after repair
attempts could not be passed. So two type of different guardrails, one is using the guardrail setup
and one is the repair or refine output that works inside the Landgraaf workflow. So these are the
two different kind of guardrails you'll be able to find inside the overall code base. Next is the
MLflow tracing architecture. So the MLflow tracing architecture, so here as I was showing, so like
we'll just try to understand the architecture first and we'll go through the code. So the Landgraaf
workflow is running, so it receives information like this request ID, session ID, what is the mode
it is running on, is it like demo service or live API calls are done, what are the different values
are there, so start time, end time. So these are just different examples I'm giving here, what we
can capture, inputs, what is the count size of the input, length of the input, what is the decisions
of guardrails at certain points, if there is any router setup, so what are the routing choices,
number of retry or loop that has happened, what are the outcome, outcome is a success or a failures,

### [1:15:13]

what is the latency, what is the tokens used, so these are the different kinds of things that the
MLflow can capture. Now, how is the MLflow setup done here? So if I go to this tracing here, you
will notice we have imported this MLflow and inside the MLflow, we're just configuring the MLflow
here with the MLflow tracking URI, so MLflow tracking URI is just simply, is it inside my ENV file,
not here, then more config. Yeah, so basic MLflow tracking URI is a localhost 5000 port, we set a
experiment to it and MLflow is enabled as well, so like we are tracing or we are not tracing is
also, you can kind of set it up from here, so MLflow is kind of a service that will run at this
particular 5000 port, so all the information during the code when it is running, the LAN chain has
an integration with MLflow and it will send the information to this host and we'll be able to see
whatever information the MLflow stores as a dashboard at this particular tracking URI port, okay, so
this is like we're just configuring the MLflow, so setting the tracking URI, setting the experiment,
what is the experiment name and everything, then comes the main part, this is the tracing context,
so when we start this span, so this span is something like inside MLflow, the idea is that once it
starts the span, inside that span, whatever comes, we can just define MLflow.log, MLflow.set or
capture this value and it captures, so by default we're just going to capture the request ID,
session ID mode, is it a live mode or demo mode, everything gets captured and apart from this,

### [1:17:17]

it kind of captures it at different levels, so for example, so here inside the matrices, you would
notice this, we have again this node span that we imported from this particular tracing file, so
what we are doing it here is this agent trans, agent duration, LLM request, LLM duration, all of
these different things are there and inside this node span, we're setting this, span.set outputs,
summarize agent state and everything, so this is what kind of setting up the values to the main
MLflow setup, so that is how the whole LLMflow runs, everything gets captured, all the information,
then it passes through the main tracing file, matrix file and this span is just going to set out the
value, so the same values as we saw onto the stream radio, in this single trace as we saw,

### [1:19:19]

this all things gets captured, like for example, what was the request ID, this is the overall flow,
in terms of land graph research, like what was the request ID, session mode, everything, then in
terms of input guard, what was the information, like request ID, search attempt, this all would be
zero, as we go forward, you would see the values change, like search attempt is one. Evidence is
sufficient. So like during the land graph workflow, the grade source node worked. It stated the
state of evidence sufficient to true output is valid equals to true. So all of this different works
in the answer character. So this is the guardrail output. So guardrail output was these are the
number of characters has any errors guardrail. How many guardrail events total past? What was the
sources count? So all of those things as you see all of those different kind of informations get
captured here in terms of the tracers. So that is how this multiple files are interconnected then
going back here. So this is how the oral idea of MLflow is that which you need to take the code can
change as per how your code base is structured how you are defining everything but the oral idea
would be that one thing for sure into production. You should not be capturing the actual users input
output the other metadata is what you should capture like all the information about guardrails how
many number of times it kicked in during the process how many times retrieval worked. What was the
number of search attempts made? How many retry refined loops done? What was the outputs of node like
so in terms of success and failure answers? What is the latency tokens everything all of those
different kind of things that you can capture and it can help you have a trace like this and then
overall dashboard like this how many traces captured what was the average latency?

### [1:21:20]

What was the tokens used? What was the tokens but race and based on the number of how many models
you are using or what is the single model you are using as per that model? What is the cost over
time? So here you can also have multiple models and multiple models used to calculate the cost over
time that can also be integrated here. Next thing is the token usage and cost tracking. So this is
also usually directly available via library like the token but here in our setup we have technically
added a function like you might have seen in our provider setup itself the provider adapter. So here
you can see extract token usage to input tokens output tokens how many it got used and here we are
also recording the LLM usage. So based on how much input output tokens and all are used we are just
having this input cost per million tokens and the output. So we're just kind of calculating it here.
You can also use library selected token and other libraries which also provide you or give you the
information of approximate how much token could be used by a model if you're using some other model
service. So for example, OpenEIS API in the output apart from the answer also provides us with
information like what are the input token output token and all but let's say if we're using some
open source models like different models. So in those cases what particular I would say the
embedding model the what is called the I just submit this is called the token tokenizer model and
everything. So like what tokenizer the model uses based on the tokenizer a library-elected token
would be able to give you approximate

### [1:23:21]

number of tokens that the input has the output over it kind of calculates the number of tokens you
have and based on it you can calculate a cost. So here in our case like we are just manually defined
it using the OpenEIS API process. Otherwise, like whatever library are using we are using open
source material anything you would be able to maybe write a function or something kind of a setup
and you can get an approximate cost based on that. So token usage cost tracking is also an important
part of any system as we know because any system would run on a particular budget a set up a
constraint certain information and there will also be an overall project budget right as we know
MLflow code work through. I think we already went through this like you know the overall setup. So
just to understand like those who have not gone through the maybe not the previous MLflow session
just for them MLflow technically uses this pan structure. So we just start the span and inside this
pan we can record inputs in we can use set inputs then we can run a land graph workflow whatever
output the generate we can directly store it as a record output. So there are two options set input
set outputs inputs to be stored using dot set inputs outputs can be stored using set outputs. I just
defines for a particular land graph node. What were the inputs? What were the outputs? So this is
just a simple example of how we are storing the input and output and across our overall code base
the same code structure is used for at different nodes to capture different things and if we want to
record some other information apart from input and outputs we can also store it like this dot set
attribute where we define what kind of attribute it is. So maybe is it a token you say is it is a
LLM cost is this number of search refinement attempts made and whatever their values we need to
store comma their value.

### [1:25:22]

So this works like a key value pair. So this is what was the particular attribute that we are
storing and this is the value. So this is three different ways input and output by default storing
is available any other kind of storing into MLflow requires a key value pair using the dot set
attribute function and usually as I was mentioning the idea we capture is we kind of capture the
basic correlations with the database. So like let's say user was chatting so user session ID and all
that can be stored we store input outputs token usage cost is important workflow signals. So across
your overall land graph workflow everything that were part of the node that is not any personal
information associated with the user that can be there privacy as I was mentioning we do not store
them like prompt evidences answers and anything. So overall metadata of the main land graph workflow
should be the one that needs to be stored. All right now coming to the final Prometheus and graphina
monitoring. Okay, so overall idea would be that Prometheus is connected to the fast api's matrices
end point the things basically that we check in a general application are the api health. So how
much time a request how many request api's getting like we're trying to identify the traffic's the
api latency errors that are occurring with respect to api like is the api's hardware or the setup
sufficient or we need to change the cloud architecture setup that we have defined. So what were the
request duration settings? What is the latency and everything we capture in terms of agent health?
So how many times the agent executed how many agents are in progress? What was the time agent takes
to generate the response then the provider level behavior information. So LLM level information like
how much time LLM takes

### [1:27:22]

to generate the response is there a difference in LLM latencies as well based on the number of
users. So maybe let's enter the system more users are there we see a latency in terms with LLM if
there are less users there is a lesser latency top all of this different kind of information we try
to capture also the guard information and any sort of evaluation setups which we have we also can
capture through it like no agent answers if if any agent feedbacks are given if evaluation runs are
made does the evaluation runs passed in everything. So Prometheus technically captures all of that.
So maybe not if I can show anything related to promises is let me check 9090 right? Maybe not. So
you can just think Prometheus is capturing all of that and in terms of Grafana, I will show you how
also to use Grafana to capture it. Okay, so let's say this is a pre ready-made dashboard. So as a
part of the code itself, I have provided a basic setting to just build this Grafana dashboard
service. This is a whole JSON architecture that is used to set up all of this but before I create a
JSON like this what technically you can also do is you can go to dashboard select create new a new
dashboard.

### [1:29:26]

Let's say I'm going to add visualization a default data source would always be Prometheus. I'm
selecting Prometheus now here you would need to make a few changes. For example, let's say here are
different matrices available. So let's say Agent runs total I'm selecting. I'm selecting a label.
Let's say I'm selecting job value equal to purpose at ABI. I'm going to run queries. So you can see
based on the time. What are the number of requests it has received? I can also kind of know you can
also define multiple things. This is just a source. Then I'll just see this dashboard maybe test
one. Great now here I can add more visualizations. So for example, it's I'm adding new visualization
can add another. So let's say I'm adding something like all the matrices multiple matrices are
there. So let's say search request created for this other number of searches request created. You
can see there are this is how I'm creating different visualizations adding give it all together and
that is how you can also create it as a my default setting. Like you see here know all of these
things are created and all and then also you can export it. So export is Jason is how I was able to
get this basic Jason structure. And also you can also use an another way like nowadays.

### [1:31:28]

I would say any AI is very efficient in creating this kind of adjacent structures as well. So what
basically the idea would be once you have your Prometheus fast DPS settings and everything and all
you can maybe also integrate an AI along with it and the AI like maybe you know any latest version
of open your anthropic model will be able to generate a direct dot Jason file for you, which you can
directly import here into your graph on our added here and you would be able to easily create
dashboards like this. So that kind of a possibility also now exists, right? Next would be our
perfect settings. So perfect here in our case in our code base perfect has a golden set that it is
scheduled every Monday 9 a.m. It fetches the golden set. It calls the fast DPS service gets the
information output per case and stores the result and by default it is like whenever I can also do
two things. So let's say as I was showing you on to the dashboard. Yeah, prefect server. So this
deployment is ready like this is true. No, the effect server that we are seeing at four zero double
zero port whenever a particular weekly evaluation run works that get executes by a prefect worker.
Okay, so let's say if I'm still want to make it and I can also make a quick run. It says this
particular run is scheduled running just a minute.

### [1:33:32]

Yeah, I see you can see it is running. So it is just going to be multiple process, right? So it
might be fetching up the data set and everything. So might take a couple of minutes to go through.
So this is how the oral workflow with respect to prefect runs. There's one weekly scheduler already
running the other setup. Also is that you can also make a direct run from a docker setup. So in case
you might not have a direct connection with the UI or something a direct run from the docker compose
can also be made from the docker compose inside from the docker prefect. Weekly evaluation not
found. Okay, maybe there might be some code issue. So you can see a case count for term recall is
one citation. Validity is one guardrail accuracy is one. So this is just numbers that I have added
into my prefect setting. This is what you need to recall. Sorry, not recall. We need to evaluate. So
this has a few basic evaluation. I've added guardrail accuracy citation validity. So the retrieval
it is doing through web search. What is the validity of those citations? What is the basic latency
in microseconds from the LLM? And this is what the prefect run is capturing. So over time as we make
multiple runs over time, let's say every couple of days every day prefect runs the evaluation to
check the system and everything how the system is running. So based on the overall dashboard level
value, we have captured we try to identify if there is any change in performance evaluation
performance of the setup. So usually any changes to model we kind of monitor this kind

### [1:35:36]

of things for a couple of days or a couple of weeks just to ensure any change into the system like
prompt model new tool new technology is not harming the overall model system could be something like
let's say overtime latencies increasing everything. So all of those independent evaluation runs can
be scheduled inside the prefect or a manual trigger calls can also be made. I will check for just
for this particular function. I will update in the readme later just to ensure this particular
Docker command also directly runs earlier. It was working but right now not working. Maybe some
issue with the prefect depler setup, but I will check and update that particular setting. But yeah,
that is how the overall format of prefect works, right? So that was it majorly from the session. So
all the different things we saw we saw the core pillars of LLM Oaks. What are the different basic
things that we should check in terms of MLflow tracing guardrails how we can add guardrail bounded
loops combined at lang graph level plus refinery tri loops how to use the guardrails framework
structure to create our own custom guardrails apart from that prefect automation was one part then
the Prometheus Grafana setup the token and cost tracking provider abstraction is also a must-have
setting and apart from this I get the other parts was basically Docker fast tape and the stream rate
setting that is the part of the deployment settings. So these are the major things that you should
start looking into consideration once you understand the deployment of any JNA application and
everything the idea then would still be that do not be dependent on a single tool to

### [1:37:40]

create or write this kind of workflows because organization to organization product to product the
setup of doing or using a library could change maybe some cases you would be using service from AWS
you will be using open source to like MLflow you would be using some internal tool, but if you just
get the concept changing libraries is become much more easier nowadays due to know all the AI coding
agents we have Claude code or codex from OpenAI Google Gemini people are heavily using it. So
creating codes has now become easy. So major factor I would still say strive focusing onto the
concepts of building the overall architecture because once the deployment happens what happened is
what is running inside the production of a JNA system. It is very tricky to capture all of these
things. So capturing the observability matrices tracing guardrails everything becomes very much
important. So that would be the main takeover from the session. I'll just allow the microphones for
everyone to ask any queries, please feel free to ask any queries because this is the last session of
the program. The last week is for the JNA program students. So any one of them if they have any
queries please feel free to ask, I'll just allow the microphones. I have allowed the microphones for
everyone. Please feel free to ask any queries if you have.

### [1:40:09]

Alright, I believe we do not have any questions. Okay, so I'm just stopping the recording as well So
Chiraghai Ganesh here Hi Ganesh So this would be just Overview that you have given or is there any
practical stuff that we are performing on top of it or how it would be? Just trying to understand So
you will get the full code full code set up So during the week 6 there are multiple materials
provided separately for each of the module Grafana Prometheus, the guardrails setup and everything
go through all of that different Modules one by one then what you need to do is the full code setup
Try to understand the full code setup that will be the most important part So just try to run it
practically and the last project for week 6 would be The creating your own version of the similar
setup that you need to do So that would be a practical exercise for you where you will whatever you
learn and whatever you understood by Working on the code that I would share today. You need to
create your own similar setup So that would be your practical activity But yeah The overall
objective of the session was to give you an overall brief of different tools and their main
intuition behind it, right? Okay And any queries if you have Please feel free to drop it on to Maybe
the platform or on to the whatsapp, but both places would be fine Okay

### [1:42:16]

Any more queries anyone? Okay, I believe no more queries Then in that case I will end the session on
it. Thank you everyone for joining Please try to complete up the projects Any doubts feel free to
even you can even drop me a message on to whatsapp. That will also be a fine Anywhere you are stuck
in terms of project any Queries, please drop your message. I will try to resolve it at the max
capacity. I would be able to okay Thanks for joining. Have a nice Okay, I guess the weekend is
already over Alright, thanks Arashio. Thanks everyone for joining. I'm ending the session. Thank you
for joining

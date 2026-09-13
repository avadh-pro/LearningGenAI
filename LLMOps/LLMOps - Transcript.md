# LLMOps — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [LLMOps](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/62977041-llmops)
> · Video lesson, 77 min (`1:17:21`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:08]

So what we're going to discuss today is like till different weeks we saw different methods fine-
tuning rag agentic approaches the week 5 covered things like VLLM how to deploy model with fast API
Dockerizing it using Docker compose and a few more tools some methods so after all of this if we
want to kind of let's say for software we have DevOps for MLops sorry for machine learning deep
learning we have something called as MLops similarly for LLMs we got this term LLM operations kind
of operationalizing large language models so large language operations practice of managing
deploying maintaining large language models efficiently in production that is the whole idea of
LLMops like similar to any operations with regard to software machine learning similarly same
concept to be applied on LLMs why is it important like what it is its importance is like to ensure
the scalability reliability efficiency of the system like considering example like if is GPU used
properly has the users like are they balanced across multiple nodes if it is served on Kubernetes
then if your cost are increasing you can get a reason behind why higher cost using some monitoring
observability tools model drift can occur and when you put something like you

### [2:10]

research you created some LLM system and you put into production to increase improve or scale its
performance there are certain not not we won't call it direct approaches but we can call it certain
reasons and based on the reasons we can take certain improvements on the infrastructure or the
current methods we have been using for building the LLM system okay so first of all let's just talk
a bit of standard difference between MLops and LLMops so MLops is more designed and the tools for
MLops are also more towards the traditional ML models like MLflow and all stuff it is more designed
to work with stuff like scale on tensorflow pytorch with respect to LLMops it is more we are more
concentrating on large language models the compute of MLops system would be moderate LLMops we know
like there are like people can have tens of GPUs running to power their LLM applications the data
handling with respect to MLops would be more structured with LLMops it is unstructured text you can
generate codes you can input json output json a lot of stuff monitoring with respect to MLops it was
more with respect to how let's say we were running a regression problem we would calculate r square
adjusted r square msc errors with respect to classification f1 score precision recalls so those kind
of evaluation matrix we will monitor over time what is the how is the model drifting with respect to
LLMops we will like monitor more focus towards the tokens the latency

### [4:14]

of the LLM the hallucination how do we improve the LLM responses how we can retrain or further fine-
tune the model to improve so that's how there is a like conceptual difference between the monitoring
the data handling part and LLMops is kind of an extended MLops with added complexities of LLMs like
working with bigger higher compute models so talking about challenges like if you build some LLM
model and are going to deploy that in a cloud server or your own local on-premise system the
challenges majorly are compute cost like requires many gpus so for example we have been in a
situation where uh there was a client who particularly could not afford more than a 24 gb gpu and
the lower LLMs who could fit perfectly into that gpu size and can serve to multiple users those LLMs
results were not up to the mark there were a few LLMs who were performing i won't say 100 accurate
but up to a level like 75 percent 84 80 percent but to scale that LLM into a single 24 gb gpu was so
hard so you might have to balance out on accuracy how much it would be according to your budget
latency and scalability the more higher model you choose the more resources you would require to
make that model infer fast like models LLM

### [6:18]

models work on tokens per second how many tokens per second it can generate if you are working with
a 7 billion model it might be generating let's say 100 tokens per second 30 billion model on the
same hardware might generate only 10 tokens per second then security privacy how do you like if
you're training the fine-tuning the models how you can have this GDPR the european HIPAA the
american data policy securities and how do you handle this sensitive data handling how we are going
to remove those kind of data if you have some data collection process where those data also get
collected so how do you handle that is also a major challenge then model drift model drift will
usually mean let's say for an example i take you created a agent LLM agent you gave it web search
capability and it was working with let's say some kind of inputs now over time uh prompts are same
the model is same but the kind of inputs they can vary or they started getting more variations into
the inputs at that point of time maybe the agentic system might show some degradations in whatever
it is doing maybe scoring something or trying to recommend something maybe there might be some small
levels of degradation but over time one year two year three years down the line it will be required
to do some retraining fine-tuning of the model or changing prompts or restructuring the architecture
of the agent hallucinations bias

### [8:18]

unreliable responses totally evaluating the models and a lot of things to uh to do there so that was
with like challenges with respect to deploying LLMs so hallucinations and bias you can take it as a
part of uh how do you evaluate how well you evaluate your LLM and how much sure you are that uh it
will be 80 percent correct 70 percent correct we all know uh even if we go with statutory responses
open air responses there might be some bias there might be some hallucinations included in that no
LLM to this date we can tell that okay it is very good or producing 100 percent accurate results
okay uh any doubts uh tell here one question is if i run the last round uh so is it like before
maybe there will be a team testing that before like a plan like they will make sure it's uh
performing as expected or isn't it something which they are going to notice after like their 100
production okay uh so with respect to hallucination or model drifting the last one one of them yeah
hallucinations and bias right yeah right so you fine-tune the LLM and then what you need to do is
you need to create certain data set maybe hundreds thousands of samples across which you cover all
the cases all the edge cases in which the LLM might fail. So if you run the test set and the results
like let's say you can just simply take hundred like for example,

### [10:18]

we are taking hundred questions. You pass that to LLM it generates the result. Now you use some
evaluation library like dpval or prulence and based on the question the context and the response
from the LLM you generate certain score that how faithful or how accurate the response was generated
with respect to the context or with respect to the question was it a straightforward answer or the
LLM hallucinated like that way those kind of libraries can give you certain score. Now if out of
hundred you get in factual score of 85, but let's say you get a hallucination score that out of
hundred 30 times the model got hallucinated that is still fine up to certain point but you might
want to decrease the hallucination levels it not it might not be that out of four sentences the LLM
is generating to our some random stuff it has generated. Okay, so that is how create an test data
set pass to the LLM maybe can have some library evaluate the results or if some human can evaluate
those results very good that that would be very good thing. Okay, basically that means if that
evaluation team is not giving it better score then you'll have to go back and more data sets fine-
tuned the mark. Yes, maybe try to fine-tune with a different way. Maybe if you are just doing plain
fine-tuning you might go with DPO maybe trying to make a model understand what is a better answer
and what might be a like it could be an answer, but not a pretty good answer that way. So now coming
to some of the core parts

### [12:52]

like if you are working with LLM system then what and overall different components or there is like
a printing mistake here. It should have been six core components. So you would have a model. So like
model is also very important part of an LLM system because the overall final response would be
dependent on how capable your model is. It can be pre-trained fine-tuned model serving way like how
you are intending to serve the model. Is it just a simple LLM you are serving for other people to
integrate them integrate your LLM into their systems or you are serving your model as part of some
rag chat bot or agentic system, whatever way you like then the search part search part typically
means vector search databases external knowledge or kind of a tool capability of the model to find
its own resources the data input output managers management meaning what kind of data is incoming
the trading data. What are the LLM responses includes guardrails for the LLMs as well. Then we have
infrastructure deployment with optimizations like what kind of infra you would have for your system.
How do you deploy that on that particular infra like with Docker with Kubernetes we are using VLM,
Olama particular way and then the last part is monitoring and observability like once all of this is
set up what you can monitor monitor model monitor models performance calculate models course like
hallucinations then like if model is served as an API endpoint

### [14:55]

for talking more into that. Let's just quickly go into each function one by one. So model is simply
something like developing and creating managing LLMs. So the overall idea like we have seen in the
first two weeks how you have options like open source models closed source models pre-trained fine-
tuned models. Then you have certain fine-tuning methods. How do you choose a right model? What could
be the trade-offs between accuracy the cost of running the model and what is the feasibility
deployment feasibility on your current hardware, which you are having or which you are going to
acquire from a cloud source or you're going to have some serverless method. So all of these
considerations you will finally reach to a particular model which you will find that it is accurate
in the given conditions that I'm going to run the particular model and model serving. How do you
search the model you use VLLM to use TGI the hugging face service. Do you run the model as a batch
inference like it will accumulate request and then at a particular instant of time it will pick
request and start responding one by one or it will be more of a real-time online kind of a streaming
service the token efficiency how efficiently the current your inference method the model setting
method can handle the tokens your deployment choices. Like what would be the cloud you would have so
that is how you are going to create a serving method. So if you're going to go for a serverless
method, you might not create a fast AP endpoint if you're going

### [16:55]

for a servered method creating a WCC to instance or GCP virtual machine. You might create a fast API
endpoint and put your end point on that servers. Then how are you going to go for a low latency
responses like are you going to have some Kubernetes or some auto load balancing included as well.
Then we are on to search part. So like as I discussed enables external knowledge retrieval of data
if LLM is not having enough context, maybe fetch data from web helps in reducing hallucinations or
some vectors are solutions. We have is you can store vectors in chroma DB pinecone. Then another
part we have is catching. So when you cash your input output questions queries responses, so that
can save you a lot of cost because if queries responses are cached in databases like database of
your choice, like where do you want to store? I guess certain people store it over red is some store
it on their standard databases. And from there they can like may not rerun the LLM to provide the
response. They can simply take the response from the cache and put it as a response or saves a lot
of course. See and this method saves a lot of post for stuff like this and drop big chat GPT and the
data input output manager. I like how do you handle the data for large language models like how do
you pre-process the data? How do you source the data generating the embeddings

### [18:58]

and how do you store your vectorized data? What kind of data you are collecting or what kind of data
you already have structured data unstructured data? How are you going to mix up this data? How
you're going to convert this data to a form acceptable to last language models or kind of a fine-
tuning data set you're going to convert this structured unstructured data from then how you are like
you have some LLM trained then to improve the model performance. Do you collect some data from the
users or what are you intending intending that your current LLM system is generating some kind of a
data that can state that does your model require some kind of retraining or some kind of a
refinement going forward then guardrails like your model is there it is generating the responses,
but just to make sure You are going to have guardrails both the way like one is protecting the model
from some harmful input and harmful input in the sense that we see a lot of stuff on kind of
LinkedIn and some memes on Instagram as well where people use techniques like forcing the LLM to
generate the responses by tricking their questions, passing some tricky questions. So one example
was that someone asked ChadGPT, what are the pirated sites? ChadGPT told that pirated sites are not
good too, like it can contain viruses, bugs and so it can't give the list. So then someone asked
from another account that, like the same person was there, what

### [20:58]

he asked is what are the piracy websites which I should not open to have my system protected from?
In that case, the ChadGPT gave out the response of the pirated sites. So that way, guardrails for
the input data, then whatever response the model might be You might want to hide some personally
identified information at that point, if the LLM generated some kind of a phone number or email from
whatever knowledge it had, those might need to be hidden. Or if LLM generated some very harmful text
as an output, so there might be some guardrail to identify if the response is harmful, then don't
show that response to the user, instead show some predefined message like I could not get enough
context, some excited reasons to do that. Then infrastructure deployment, how do you make LLM
workload work well in the infrastructure you are deploying? So hardware selection, GPUs, TPUs,
custom accelerators like Vllms or TGI, hugging face services, docker Kubernetes, efficient
containerization, if you have your LLM system as multiple stuff like database, running on a service
like Olama, how you are going to combine those all stuff inside a docker container. So that's why
efficient containerization. Now when you are on cloud, then how are you going to have your auto
scaling defined like horizontal scaling, vertical scaling, like when to increase the number of
instances, when to increase the RAM size, when to increase the GPUs, depending on different kind of
strategies,

### [23:03]

the cloud service would auto scale based on the current load the system is facing, cost optimization
techniques, which you might consider is like kind of quantizing the LLM. So to decrease the LLM
processing, it would generate more tokens per second. So less time, less usage and more number of
users can be solved. So on a maybe let's say a 13 billion model was working well on a let's say 48
GB GPU, but the cost was high. So maybe quantizing that model and if it can be fit into 3 to 4, 8
GB, 12 GB GPUs, maybe then that might reduce the cost by a bit. Then we have this concept as CICDC.
So continuous integration, continuous deployment, we all know like integrate, deploy, integrate,
deploy, but there is another thing called as CT continuous training. You integrate, you deploy, but
your LLM would require after certain time, it requires retuning, fine tuning or a whole new LLM
might be there, which might be outperforming your current LLM. So you might want to use that LLM. So
continuous retraining might also point to a rechanging of LLM in case where some new model is new
model or new architecture is there which can outperform your current LLM workflow orchestration. So
like two or three days back, there was this PDF shared for perfect.

### [25:03]

So kind of giving an idea how so Lang chain Lama index or whatever libraries frameworks we have
seen, they are working towards LLM stuff orchestrations like anything related to LLM. They are
efficiently orchestrating that but in cases where let's say you don't want to external framework and
you are creating your own framework. So you have your own custom memory where you are storing in the
database for LLMs. You are calling your LLM from your own services, your own set up certain library.
So in that case, you might need to orchestrate your overall workflow like when the input is coming,
what should be called first, how the memory should be accessed. So all of this would come under
workflow orchestration. So workflow orchestration, we have tools like airflow, prefect, mage. So
perfect is kind of very easy to use, doesn't require something very extra installations like airflow
airflow might be a bit tough to get it installed and work very straightforward. Perfect is pretty
straightforward. You just do pip install perfect and you can just simply write a dot by script, set
up your stuff and it will run then monitoring and observability. So what to monitor like what kind
of stuff you can monitor. It is not a very exhaustive list, just ideas like security threats, data
privacy risk. If someone like this might be coming from guardrails, then response, accuracy, model
drift, you are for every chat with LLM, you are taking out some average score by using

### [27:04]

library like DPL, true lens that what is the amount of hallucination the model did over time. So a
combined hallucination report from the model over a week or a month, then token usage, how many
tokens are getting used every day, what is the latency, should you replace the model with a slower
model, how much amount of GPU percentage is getting used, if the GPU is not getting utilized
totally, you might want to change some library or you might want to change in a way that your GPU is
fully utilized, you might look into GPU utilization techniques, then what are the monitoring tools
for you, if you are into a Lang chain, Lang graph kind of an environment, Lang Smith is a great
choice, if you are using something of your custom or some other library, there is libraries like
OPIC, LangFuse and this was with respect to LLMs. Now if you are monitoring and observing stuff like
if you had a fast EP endpoint, how many requests are coming to your endpoint every second, every
hour daily, what is the amount of data size input, what is the amount of data in KBs in megabytes
generated as an output, how much amount of time your system is up or how much amount of time the
system is going down. So all those stuff can be captured by using tools like Prometheus Grafana,
there are a lot of tools like one is Prompte, LogStash and a lot of stuff, then based on Prometheus
Grafana, you can set up certain alerts that if the system is down, there can be an alert setup that
the system is down, detecting certain anomalies into the system, if the GPU usage

### [29:07]

goes too high, I guess this kind of anomaly detection is already provided by any kind of cloud
server if you are using like if the instance usage goes above CPU usage goes about 80% 90% you can
have those settings in there to identify the right, so it will give you an email that your system is
having 90% usage, it might crash if it continues, so with the help of these kind of alerts, you can
monitor, you can see how is your model performing and kind of you can produce some reports that what
might be your future actions based on those reports, so that is how. uh monitoring and observability
is also very critical part uh the thing uh with respect to an LLM system just doesn't end where you
just deployed no uh even after that there are a lot of things which you should do to keep running
the LLM and to ensure accuracy and good results for your users for your clients so this was the six
particular uh components now if i have to talk from a perspective of how would you be developing
this kind of a flow so what the ideal flow might be would be you would be having some training data
you are creating a model how you created a model serving system rag agentic way then how do you add
the search capability tools so i have added two way arrow here because the requirements or the way
you are going to improve in a research phase might keep changing so this part would be some two-way

### [31:09]

process where it would keep getting improved then you fix certain stuff in the data management what
kind of guarantees you want to put on your model what uh how we are going to store your external
data you're going to fix your vector database then your infra and deployment part will come and then
you will set up your monitoring and observability part any doubts here was it too much of
information i think it's a great session actually so i i just joined later well like i missed few uh
yes i have got an issue if you have some doubts you can ask not an issue nothing else of no uh i
need to catch a few things i the last assignment is still pending with me um yeah so i'll be
completing back today um so again uh based on the whatever so far all the tools i i feel again we
are adding more and more tools today yeah i know it's going to add value but again it's a lot of a
lot of tools of getting

### [33:10]

added so we said something i mean it's not really fine i feel it's now adding more layers to the
process so it does when you have to monitor like the power it's like a little unnoticed right i mean
on the previous one yesterday i was going to that okay right right yeah you are absolutely right on
that uh like the number of tools that are getting coming out are too much but uh i guess uh the
floor idea should be still the same like the components which i just showed me maybe there might be
more components to it as well but uh uh you can keep it very simple uh if you have a less number of
users if you have a lot of number of users you there will be something very complex you will keep
building so uh like again this is a very kind of a gray area i would say like what might work for
some organization some for other that might not work same tool might not be efficient right yeah
you're saying something no i'm saying that's correct one size fits all kind of solution uh so maybe
let's say uh for my use case or something i might have been working on at my organization i might uh
only need to check the factual correctness in your case

### [35:15]

when you are doing evaluation or generating or monitoring at llm you might need to have three to
four different sets of evaluations if i was working with an open sorry closed source model like open
ai my i might not spend too much time on this dockerization gpu accelerators because open a does
that already right so i don't need to spend time on that but if someone is going to consider using
only open source models then for them monitoring their gpu usage and stuff becomes important because
they might not want to just have the gpus added and having them underutilized based on the space as
well as tools we are using like maybe for someone a system with two tools might be more might be
working way better than someone uh with a project with 20 tools that might fail yeah thanks so next
uh this is kind of just a example or a visualization of what and uh from an architectural point of
view something might look like so you have some data collection data structuring processes with
which you are fine tuning or some extra knowledge you have which are going to pass to the model you
are creating some llm system out of that adding certain tool capabilities extract some guardrails or
search capabilities to that system

### [37:16]

that is overall wrapped uh and you deploy that you can deploy that as a fast ap endpoint on docker
communities with more optimizers if you are going for some open source models again that would be
wrapped up in uh infra cloud maybe server serverless system or even on premise thing might also be
there but mostly uh it is more these days what i am seeing or whatever projects i have worked upon
it is more server serverless solutions and if you observe uh i have put monitoring and observability
between both the sections because you would be monitoring uh the deployment parts the fast ap
endpoints the model performance as well as the cloud side like gpu utilization the kind of uh load
the system is taking the kind of load uh certain particular activity like let's say uh when uh only
when there is like in your system there was some particular activity only that particular activity
adds load onto your gpu uh something like that so monitoring observability would be over both the
areas or maybe even it would be spread across all the three areas where you will be monitoring
observing something to improve your system in the future so this kind of example uh like overall
structure which uh you can build upon like not the case someone might not require regular data
collection keep retraining fine tuning the model someone might not be requiring extra tools if
someone is going for on premises

### [39:19]

they might be just creating a fast ap endpoint or docker service uh passing them to everyone in the
team or have an internal kind of ap endpoints working which all the people can access so multiple
variations of this can be possible now uh part uh so this particular thing so one thing which kind
of amazed a lot of us was perplexity right So how many of you use perplexity regularly or might have
used it once or twice also that is also fine. I'm not used it. Not used, okay. So I'm considering
this as known as used perplexity. So in this case, what perplexity did differently is what it tried
to do. We had chat GPTs and all, but what they developed is they developed and added a good web
search functionality to their model. So they kind of claim that they have created or fine-tuned
their own model. Don't know what is the exact model they're using. They added a web search
functionality to it. They created their whole system to run their LLMs,

### [41:22]

their web search functionality. And what they created is it's kind of something with which they
wanted to replace Google search. So if you go on Google, you search something, you will get lots of
results. What their idea was to, if you drop a simple question, they will pick you the five best
results or top 10 results will summarize the content for you and will pass you the links which you
can refer to get more information. So thing worked not to an extent where they used to compare
themselves with Google that they can replace web search that kind of couldn't work exactly how they
wanted to. But yeah, so what we are done here is kind of replicate something very similar. So this
is a simple Lang graph kind of a code. The code is shared in the PPT. You can have a look, but we
will directly jump to the image part or we can walk through the workflow as well. So what, I open
the image here, yeah. So what idea is here like when an input is passed, the model will identify
whether any extra information or more questions are required from the user to generate a response.
So it identifies, if it identifies that it requires more information, it will ask the question to
the user and the user will pass a new question and then it will go to query generator. If it doesn't
require any extra information, then it will directly go to query generator. Now, what query
generator is doing is it will generate multiple similar stuff

### [43:25]

and it will do a kind of a web search. So here in this example, we are using DuckDuckGo as a web
scraper. Then what it will do is based on the question, based on the context extracted from
DuckDuckGo, it will generate a summary along with the final result. And this is kind of a human in
the loop service. So what kind of a demo here it is like we have taken here is what I'm doing is I'm
just passing first champions trophy 2025 match. So what output it gave me is additional input is
required to clarify what specific information the user is seeking regarding champions trophy 2025
match. And when I displayed the last output from the AI, it gave me an answer like this, like this
was with respect to the tool and this is the AI response which it gave us. So to provide the more
information, it is asking me like if I can clarify details, any details from this. So was it with
the champions trophy tournaments or the 2025 edition, any kind of information if I can pass to the
model. So then what I did is I passed it that I'm referring to the recent cricket match between
Australia and Afghanistan. So in this case, what I'm doing is I'm updating the state. So this is how
the Lang graph human in the loop system works. I will update the state of my graph. I will pass this
latest input. And then when I invoke my system, what it does is based on my extra additional
information, it will rewrite my original query, generate more queries and this fetching pages means
it is running DuckDuckGo search

### [45:27]

and based on the DuckDuckGo search, it has generated me this particular final response and I say
champions trophy Afghanistan there. In Lahore, the game was ultimately called off due to drain and
it is providing me with the links as well. So if I go open a link, I hope yeah. So how it provided
us the links is because in the DuckDuckGo part, the context we are generating is we are getting the
information from the website as well as we're passing it the link as well. So this response was
generated by chat GPT and it has given the links as well, whatever DuckDuckGo has created. So this
is how you can build some kind of own custom web search functionality module for you. So what
happens is some cases, some people want to search something very specific. So now in this particular
flow itself, you can add maybe if you have some PDFs, you can just simply add a vector database web
search. So external, your own custom external knowledge database, then you can add kind of a lot of
tools like with respect to web search, heavily search, Google search. If you have some coding
required, like where the LLM might want to run the code, you might add a Python ripple tool. So the
LLM would whatever code the LLM generates, it would run and produce you the direct output that
whatever code the LLM has generated, it is working or it might work. Like that way, the model can
work. So any doubts on this Public City clone?

### [47:28]

Like do you guys want me to go through some of the coding part, like how that flow was created or
like even if you are familiar with Lang graph, if you are not familiar, you can go to that agentic
weak core, you can see the Lang graph there. There is a good explanation on that. Yes, Srinivasan,
you are asking something? Yeah, you know, I'm just asking on that for Public City. So in this case,
the example is shown. So you're using that to do a web search for your personal. No, no, no, with
respect to Public City, we are just trying to clone it, like the functionality. Public City's
functionality we just cloned. Okay, I'm trying to do a web search for your personal. Yes, yes. And
is it like similar to a group page of open source or do we need to stay like open app? So here in
this case, I'm using open API, but if you want to use, you can use Olam as well. Olam or any hugging
face open source LLM, you like. If you have Anthropic or whatever you want, you can just simply
integrate that. Okay. The only thing that you might face here is any kind of a web search tool, like
NuckDuckGo, Google search. Those tools has a rate limit from a particular IP. So what you might have
to do is if you're actually looking to create something for yourself or your internal tool for your
organization, you might need to have some proxy IP switch rotating proxies to work with. Or more
appropriate solution would be to take server API,

### [49:30]

the official kind of a Google search API where you won't need to have those switching proxies for
you. Otherwise, if you don't have switching proxies and if you use the free Google Scaper or
NuckDuckGo, they will block you after 10, 20 queries and they block you from starting from 24 hours
to it can go for months as well. Okay. I have one more demo with me trying to just use up a few
tools here and there, trying to just create something with open source tools. Before going to that
demo, any doubts still now with respect to PPT or the Public City clone we just tried? If we have to
change from the OpenAPI to Ollama, where is the changes we need to make? Can you quickly walk us
through that in your Public City clone code base? Sure. Thank you. Here I have this Lang chain open
here. I have chat open here.

### [51:31]

So let's say if you want to replace this with Ollama, then you would have Lang chain Ollama with
you. What you simply need to do is replace instead of this, you need to replace it with this chat
Ollama, and here what you simply need to do is model equal to chat Ollama, and pass it to your
Ollama's model name, whichever you are using. Got it. Okay. That helps. You're doing chains here.
You're not using Langs, what is it? Lang Graph we are using. Okay. Got it. We're using Lang Graph,
but as Lang chain was already providing the endpoints or functionality to integrate the LLMs, Lang
chain didn't create a separate integration for Lang Graph. They're just told import the same module
as Lang chain, and use that in Lang Graph. Got it. This helps. Thank you. Okay. Quickly open this
data. So we use Travely, so is that like a possibility is better or it's almost like a different,
it's a competition with them?

### [53:31]

It really is good, but that is like every month it just forwards you with 1000 free requests, and
then after that it is paid service. Okay. Free services, they just have a library, but you need to
add proxies to it so that you won't get blocked. Now, proxies again would be paid like good proxies
are paid, and if you don't want to go for that integrating proxies to some other libraries, and that
stuff, you would go with Travely or Serper API, and they are paid over a certain monthly limits. But
better to use them because handling proxies and all can be quite, and we don't know like the proxy
distributors, they are like my experience has mixed review with respect to proxies, like with
respect to web scraping and all. So proxy providers, they consume a lot of money from you. So
instead, go for a paid solution from Serper Travely, that would be a much cheaper option. We'll go
to this demo. So here, what I tried to create was,

### [55:37]

I tried to create my like this particular perplexity clone was with totally with respect to relying
on Landgraaf functionality, relying on DuckTuckGo as a tool to scrape. So before this, like this
Landgraaf and all, this was all built recently, but kind of eight to nine months back where I wanted
to do something with perplexity. I kind of created this total custom, and even the versions used
here are a bit older versions. Even the Lang chain versions are a bit old, but like as I created
this code longer back. But what my overall idea was, just a minute if I can, you know, so this was
what I was trying to build for myself. So I had a few books. I was learning some kind of a bit of a
mixture of data engineering.

### [57:41]

So what I wanted to do is I have a rag module with those data stored up there. I wanted to do some
web search as well. So this was my some part, internal parts like storing the query, sending to the
scraper module, the scraper module will scrape online articles for me with respect to that
particular thing. The rag module will identify relevant articles for me and only store the relevant
articles. And those relevant articles would be then stored in VectorDB after generating the
embeddings. And then I can query over that relevantly stored. What I will say, I can just quickly
question and use the articles for me. So same thing, I'm going to demo here. Like the code is not
totally optimized, but yeah. So what I have is I will just open my Docker compose. So what I have is
one is a fast API. Like this is the end point, which is running the olama service. In the back end,
I'm using a simple gamma 2 billion model to generate the responses. Then I was streamlit app, which
works as a chat kind of a UI where I can chat and it shows some kind of a dashboard to me, like what
kind of data I have collected and information like that. And then I also integrated Prometheus and
Grafana to it. So how much amount of usage I am doing with fast API, how much amount of times I'm
calling the model, what is the number of output bytes of data it is generating. So all of kind of
information can be captured using Prometheus and Grafana. So this was with respect to Docker
compose. Now, if you go to like one of the PDFs I shared recently onto the LMS, it shows how you can
create this Prometheus Grafana

### [59:44]

dashboard into the system. So I won't be explaining this much here, but you need to create this
Prometheus.yml files so that you can store your data here. Then this app folder, this is intended to
work for my streamlit UI. Along with that, I have a dockerfile which runs my streamlit and this is
my main folder which has all the different modules like query processing. So this is kind of a
class-based code I have developed where it stores the queries into Postgres then it has options like
from which tool to scrape use Google use DuckDuckGo only scrape the snippets so with snippets what I
mean is if I go to Google and if I search simply what is the match today South Africa is England I
guess yeah so if I just search this it will show me so many articles here right so do I just want to
scrape this information given here or I want to click the full article and want to scrape the total
information so that kind of options I have for me then this was the query processing the part then
we have relevance check so for relevant checks I am using a similarity search kind of a thing I am
checking the relevance with respect to my query and kind of a chunk which I have scraped from the
web if it is similar to my query then I will store it or I will not store that then storage is just
simply my Postgres database connection local connection I have the web scraping part is my main code
where I have used simple beautiful soup to scrape simple HTML CSS and I have defined categories for
me so

### [1:01:48]

what this categories intended to do is so one good feature with respect to Google search is if I
search something okay and if I add something like site Creek bus dot-com it only shows me the result
with respect to Creek bus so what I have added that as there is an category identifier module which
identifies the category and from that category I will only scrape the data from the particular sites
which I have mentioned here because they're easily scrapable with respect to beautiful soup and
normal HTML scraping so this is my full different sites data scraping with respect to Google duck
duck go and all and this is a utility scraper tool this is an Dockerfile simple installations like
NLTK downloads requirements then I have this guardrails configuration to install the output
guardrails then I have this main.py which has all the things like olama, OPEC to trace my chats with
like because streamlit can't persist and I'm not storing my chat data so I'm storing all that on a
OPEC server then olama calls and all are made from this main.py so if I have to show some working
demo of this there was last time when I tried running this there was some error with respect to
guardrail don't know how it might turn out so like they were on pause so I have restarted them
simply I can do it is

### [1:04:47]

running on 8 0 8 0 just let me check what port it is running on it's working 090 so this is kind of
a Prometheus which are connected to fast dpi to collect my data and if I were to open Grafana this
is already a kind of a dashboard I have so if I pick seven days so it will show me the information
how many times I have used is all I've used rag prediction one time how many bytes I used when I use
so it will show me the date 27th Feb I used so this is how Grafana will show my fast dpi and system
matrices how many of input output data it came what was the request size how many times the CPU
usage was there what particular end fast AP endpoint was accessed then this fast API works like

### [1:06:47]

processing the query which I have integrated it here with streamlet so data collector is like you
can just pass in any query you can select Google's doctor search engine you want to scrape full
article or just have snippet intelligence scraper is simply like that site you give site and
particular set so intelligence scraper yes will means that that particular category finder would
work in the back end and only scrape from the sites which I want then here I can have chats so here
I can just put any question and it will just give me the response now here like I don't think this
is working because there was some error with guardrails but it's the latest updates on CM there is
some response error Olam I stopped sorry right now it is trying to fetch data whichever I collected
and stored in vector DB and gamma to be trying to generate an response but I believe yeah the
response generated failed to meet our content guidelines so this is an response from guardrails
which I have been generating here in the code the response failed to meet our content

### [1:08:51]

guidelines because the output the model generated looked bad and there is an response here no the
response I think is logged into OPEC so we'll just see that OPEC part but let me just go back here
then on this here particular I can view what kind of queries I have collected over time November 7th
and number 6 I have been collecting queries what kind of scraping I have done like on duck duck go
what I have preferred more do I have gone for half scraping full article scraping what kind of
informations I have scraped on particularly if I have scraped full articles then I only scraped for
champions trophy 2025 so this kind of information I am showing for me here for my own then what kind
of words were the most frequently used in my queries like what things I'm continuously looking for
so this is kind of a demo app cloned version of my same thing which I filled with Random queries so
doesn't show what exactly I am using for my personal use case. But yeah, then I have this chunk. So
you shows me information about the kind of data I have stored. So chunk length like what for what
query I have stored the most data and let's say with respect to like my overall storage. What is the
size I have stored something and I have this query wise analysis. So if I just go to UCL what
website I scraped the most from so it's showing one one scrapes from all if I go to maybe US
elections.

### [1:10:53]

Yeah, so different scrapings from all the different sets. So like this way it will give you
different kind of information on the data collected whatever you queried like that way and Grafana
shows you the information regarding your fast API endpoint usage and stuff. And the OPIC part which
I have integrated is as with streamlit I cannot store or I don't want to store my chats here. So
what I have is have this comment to OPIC is a service which where you can store your so I have this
data aggregation platform here and my all my olama calls are stored here. So is it show today's?
Yeah, what is the latest updates on the UCL? So this one document it was able to fetch and this kind
of response it is generated the number of participating teams has increased from 32 to 36 with the
addition of a group stage featuring Asia North of America. So this is the response that generated
somehow the guardrail fail guardrail whatever I have attached filled that the response was not up to
the mark and it gave a tag as the response was not good and thereby a automated system response was
given as an output. So this was with respect to the overall demo. I kind of have built with using
few open source tools

### [1:12:56]

and whatever I can use back then when I created this but this was all kind of more of a fun project
self-learning project. Yeah, that's it. It's an excellent. So you know that data aggregation where
you showed that with the statistics and that's coming from OPIC is it which that streamlit
statistics. Yes. No, no, this is all I have stored in my Postgres database. So this is the only one.
Yes, OPIC is only saving my LLM input and LLM output and it is also showing how much time it took.
So it can also show me like I guess all the responses are generated within a minute. So it's showing
a start time end time like that. Yeah, so it is capturing the durations as well like what time it
took to generate the response. So four seconds point eight seconds 14 seconds. So this kind of
information it can give and it's also providing me some metadata. But I don't think I have been
storing any metadata. Okay, yeah, it's just Olam and Lang chain, whatever tools I have used from. So
OPIC is simply the usage of my LLMs. This particular streamlit part is with respect to my data
collected and stored into Postgres and the Grafana part was with respect to the API I have created
and the API usage I have done.

### [1:14:58]

So that is it. This graph is again from the data set coming from the data coming from Postgres. But
is it like you are using like LLM data? No, no, no, this is I have set up the queries that select
this from my Postgres database. It gives me data and I am using Pandas and Matplotlib to show this
chart. I have predefined these things. Chirag, please share the code and data. Code for what? This
particular project. I have to do some modifications on this. I have not yet decided to make it open
source on my GitHub. It is there on my GitHub, but I am just trying to fix this guardrail and stuff.
Like whenever I get free, maybe in the next 10 to 15 days, I will put this on GitHub. I will put the
link on to Slack whenever I open source this.

### [1:17:04]

So I think we don't have any more doubts. In this case, I will just stop the recording.

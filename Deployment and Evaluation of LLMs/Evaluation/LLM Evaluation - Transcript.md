# LLM Evaluation — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [LLM Evaluation](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/62386957-llm-evaluation)
> · Video lesson, 78 min (`1:17:31`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:01]

with some confidence. Yeah, so let's get started. So till now, kind of all the stuff we did was
regarding fine-tuning rag or creating some agents or just doing some sort of prompting to the
models. We did have two stuff like kind of evaluation. First one was in week one, like how to
evaluate an OpenA model. And then in week three, rag. We saw a library called us Ragaz, right? So
both were kind of how to evaluate your current existing model. Today, we'll kind of do a bit of
exploration of what we can evaluate. And also, like we'll see two to three library examples as well,
like a few coding examples, how you can use a specific. Chirag, you are not audible.

### [2:34]

Hello, am I audible now? My network just went down. Yes, yes, yeah. So yeah, we were talking about
how we saw different sets of techniques, how we can utilize large language models and saw two
examples on how to evaluate them. And today, what we are trying to do is what are the different
libraries? What are the things you can calculate? And what kind of evaluations? Not only with
respect to LLM, but with respect to an oral LLM system as well. So let's get started. So when you
kind of open any kind of social media, Instagram, LinkedIn, even LinkedIn is kind of a social media
nowadays, Reddit or anything, you will see everyone with kind of a different opinions on AI, right?
Someone, like even with the current deep sick release, people are like they will steal the data and
a lot of stuff, right? Due to the way like kind of it is. So lots of opinions we have on AI. So the
main question at the end comes where how do you evaluate the model's performance? Not only
performance, but with what amount of detail it can craft the response? Like the answer may be
accurate, but for this particular use case you are trying. Is it, let's say for a customer support,
you don't want your agent to be a very aggressive response, right? So that kind of checks along with
the model response is also important. So lots of like methods we have.

### [4:39]

But before that, like kind of multiple reasons why we need to evaluate the elements would be like
ensuring the accuracy. One is the main point, like the response accuracy. Then biases, like even if
we see a lot of models, if you ask it something controversial, they may not answer that. Like the
bias they have in their data. What is their efficiency? Efficiency in terms of the system. Like it
shouldn't take more than like too many seconds to answer. So in that case, you might need to change
your LLM, something like that. Then hallucinations, right? Like a lot of hallucinations AI can make,
especially when using RAC where it has some context given to it. So based on the context, it can
hallucinate if the context is not totally fulfilling the user query. Then ethical considerations,
like we know that sometimes people push their organizational data onto OpenAI, and a lot of things
can happen. So all these things needed to be checked. So now, again, there is a very like two points
here. One would be evaluation, and one would be guardrails. So not to confuse between these two,
guardrails is something which will come after evaluating LLMs. Like you evaluated your LLMs. Your
LLM came out, let's say, on the test which you have defined, like maybe three to four different
methods of evaluation you have defined. The LLM came out as, let's say, 82% accurate, something like
that. The remaining 80%, you still want to make sure that it doesn't make a mistake. So that is the
point where you add a guardrail while making the response. So like two different points, like one

### [6:41]

is before production deployment, one is after the production deployment. So not to mix these two. So
like what could be the main things you can evaluate an LLM's response from? One would be like the
language understanding. With respect to fine-tuning, let's say you are fine-tuning it on a different
language. Can it properly read, summarize in the other language, or even the English language as
well? So let's say if you talk about a model like Gamma 2B, like this is kind of a personal
experience to me. So a Gamma 2B model and a LLM 3B model. So what experience I had between these two
is like I was trying with English language. So LLM 3 was producing better results, but when I
switched to a different language, Gamma 2B was producing better result in other languages. Those
kind of things, evaluations, are required. No model would be perfect on all languages. Then
creativity, like a lot of people use it in content creation, tasks, and all like. So we see a lot of
AI videos and scripts, like these days, Instagram and all that. So that creative writing also, there
needs to be a check on creative writing. In the name of creativity, it doesn't produce something
weird. It can produce jokes, but maybe the jokes are too lame, or something can happen. Then
accuracy, accuracy we know like if someone asked for World Cup 2023 result, it shouldn't give answer
for World Cup 2015, 2019, like that way. Then consistency, consistency meaning that same question,
does it produce the same answer, or it deviates from the answer?

### [8:41]

We can even see this, like you can put a question to chat GPT, if you again put the same question,
the model might sometimes tend to think that you want a different answer, so you are repeating the
same question. So that consistency in response should be that maybe in a different way of
responding, the language, the tone, the structure of response might be different, but the overall
idea should be the same. Efficiency, does it give the answer faster? If you have a use case where
you are giving some service to a client, and if the person or the users have to wait, let's say, 30
seconds, minutes, two minutes to get the answer, then that might be insufficient, rather than maybe
you might start looking to change the model who can perform faster. So kind of a different based off
evaluation, but still considered a kind of an LLM evaluation, maybe not from the perspective of
answer or the response it generate, but how faster it can generate. Then ethical alignment, like
does it align with not only ethical alignment, but with your, let's say, you're working for an
organization. the organizations might also have some particular alignment that the model should not
maybe respond this or let's say I'm running something let's say I am running an organization that
has produced a library in python and users come and ask about the let's say some competitor library
I don't want in that case that kind of an alignment evaluation you can also put so here you need to
provide that training data you need to do that maybe even if it doesn't like

### [10:43]

libraries will keep coming maybe you cannot handle all the competitors all the time so maybe
guardrails could even be a better option here so this kind of evaluations like a lot of dimensions
like not only this based on the use cases a lot of different things can be explored right so like
we'll now look at a few approaches like so we have a few approaches how to evaluate the LLM so one
would be the standard procedure in which every research paper when they like sorry every model when
they get published along with this that if they have produced a research paper or a single page
website or on their github you will find that this model performed 10 5 percent or 10 percent better
than compared to ggpt or a mistral model so has anyone came across this kind of scenario like if
they have seen the papers or some github open source links of models yeah right yes yeah for deep
sea they were comparing right yes recently so like how do they compare so they compare on something
like a benchmark but what is the benchmark so what people have done is they have created massive
data sets that can evaluate an

### [12:43]

LLM on different tasks so let's say we have a benchmark as a mmlu massive multitask language
understanding so it has a lots of diverse subjects and across that it tests a model so a good mmlu
score meaning a model is kind of a well generalized model across different subjects not particularly
aligned to a single domain then there is a hella swag benchmark which tests the reasoning then we
have a truthful queue like it works on like a question answer assignments and how truthful the
answer is so this is called standard data sets question answer data sets which people have prepared
so what they can do is get the questions from this data sets test their model across and compare the
results by comparing the original answers and their their models generated answers so like this is
one way to you know like automatically test like taking data sets from already created data sets on
which most of the large language models are currently being tested on that can be a way to you know
like kind of prove so let's say all the models chatgpt, cohere, mistral, deep sick, gamma, gemini
all the models that came they always come with some of the top benchmarks people have created so
that is kind of a way to understand like it's very easy to compare it if we have something for
comparison out there it's very easy to pick a model for us so that was one way another way kind of a
human evaluation so when we test with the models right so we we know like when we do prompting on
chatgpt with anything like coding

### [14:49]

document generating documents or maybe just doing kind of any research so we try to see how correct
the information is or is the response generated useful and one more thing if like you are drafting
some document like you check it like the response tone of it doesn't sound too ai written right some
changes you make on that so how does human like response it gives then harmfulness that is to
produce any offensive or unsafe content so all these things human reviewers can assess on the lms
outputs so where would you require a human evaluation can someone answer that any scenario where you
can think of you requiring a human evaluation maybe related to medical one good scenario and in
medical can you expand any particular use case or maybe if uh lm is giving some response to your
general type of things like the statements it should be it's going to impact of the wrong
information which can come to light

### [16:50]

you're right correct so one case as uh one more case one interesting case like kind of which i have
came across is was to make recommendations based on the user input so so that recommendation right
so that recommendation is made by lm based on the data we have put in a vector database now there
were certain products inside the vector database that should be recommended but how to evaluate it
right let someone asked for that uh my like someone filled a form they put all their information
there then the lm recommends them like the model was fine-tuned was given certain rules on how to
recommend but can any lm or any kind of a function determine whether the recommendation are correct
or not mostly those kind of tests won't be successful so in this case you can only rely on a human
to actually make a evaluation it shouldn't be like uh that three recommendations you are giving two
are correct one is not correct maybe even human can make that kind of a mistake but uh using an lm
or any like there there won't be any library or any particular function to detect this kind of a
response like you can maybe uh use something like how was the answers correctness using some library
the the answers correctness would still give you a kind of a very high probability that it is
correct why because the person filled in details asked for recommendation the model generated
recommendation so according to the standards the response is correct but what is the correctness of
the response should be kind of you know

### [18:53]

evaluated by a person like let's say you're working on something uh maybe if you're confident once
you're confident that okay uh 90 times out of 100 it is generating better then maybe you can start
relying on uh different uh methods of evaluating but at the starting a human evaluation would be a
good thing to get started with when comes adversarial testing so you have a model uh you even tested
human questions and all now a lot of times you will see not everyone can prompt well uh someone
might uh try to we see regularly on chat gpt like there are examples on linkedin where someone asks
for what are the piracy website the model won't give directly but the person will then ask that uh
i'm using this site uh which is banned what are the other alternatives the chat gpt will maybe give
the alternatives which are not like it is kind of a trick for like used by the person to get the
answer from the model so this kind of testing also you should be an ad should be added so that wrong
information or some informations that are very critical should not be you know responded by the
model so this kind of tricky questions or misleading prompts should be also made then user feedback
real-world model trick like when we use chat GPT a lot of times you get a response once a response
to and you select a particular response one response so I prefer this response so now if you see by
the time when we

### [20:56]

released the open AI fine-tuning demo in the week one when we were in week two somewhere at the same
time open a released their own DPO fine-tuning so how was opening I able to do that is like they are
collecting this kind of a data from a long time and they have created their own DPO data sets and as
well and now opening also supports DPO fine-tuning as well so if someone like till now what was
happening is for if you want to do a DPO maybe you would have always opt for open source model
because open AI and maybe even anthropic is not supporting that but now opening is supporting so
maybe that would be a better alternative if like organization doesn't have an issue with the data
compliance data privacy and all so that is one thing but yeah kind of an example where you you ask
the user that what response you prefer or was the response great or like you add a kind of a like a
user setting where user can click on the response and say that the answer was not correct what was
the reason so you collect all the data feedback to the model maybe create a new data set again
feedback to the model to fine-tune so that is how even a user feedback and real-world monitoring
evaluation like evaluating in real-time can help to make the model more better like in a not maybe
in a very short time but on a longer run you can improve a model by collecting these sorts of data
but this is also like maybe not from the perspective that you did all kinds of evaluation on your
evaluations the model worked well but when you give it to the

### [23:00]

user even allowing users to do some kind of evaluation is also one of the way like you can do like
evaluate and improve your model then one more method would be to like prompt analysis sensitivity
analysis so sometimes you can see that adding even a single word so like let's say I just wrote
prompt like to a model that say it generate me a Fibonacci sequence so it might only generate the
sequence now if I add something like Python code so it will give me the code for Fibonacci sequence
in Python so that is how even like small changes in the prompt can change the whole response so that
kind of an evaluation is also like where you are when you are working in a use case where users
might not be very technically sound with LLMs so in that case it would be better if you prepare your
model in a way that it handles the difference in prompt it handles the differences in tone the way
they have they were they're asking the question and how consistently the model responds to those
different sets of prompt that are actually trying to get the same answer so like why we do it is
like a robust model should maintain consistency despite minor variations right so that is one way
like the example I give surely had a big variation like as one time asking it to get just a
Fibonacci sequence and once asking it to get a code is totally different but like that was just for
like an example and one like kind of the latest would be an LLM assisted LLM

### [25:05]

evaluation you have an LLM you get the user prompt you get the user the LLM response now instead of
an human evaluation what you can do is you can specifically craft a prompt and pass it that you like
beautifully crafted prompt to an LLM to judge another LLM so like this can like with human
evaluation we have that it was very time-consuming maybe this method you will get faster results
consistent grading like LLMs won't be biased towards something but at the end like you can't trust
LLM like maybe if it's knowledge knowledge is not 100% correct it might produce wrong evaluations it
might produce wrong scores and which can impact the response or the way you are trying to find in
the model so kind of this were all the different methods that can be thought of while doing the
evaluation not every method is 100% correct or 100% accurate but every kind of checks can like if
you make every kind of checks from the six methods we can maybe then start thinking towards a more
better model we can create a more better model with a more accurate data set that can handle many
different cases correct so any doubt still now or we will quickly move towards the next section even
if anyone has any experiences doing anything if not at the code level just like experience like
someone might be in a project but someone other has done that so even if they can share that that
can

### [27:08]

be valuable I have one doubt actually in a LLM as a judge model can I ask yeah sure sure okay so
let's say if we fine-tune a model that is very specific to the domain and no other LLM in that
domain is available for the testing in this case is the human evaluation is only option or we can
move forward like benchmark data set you have shared or LLM as a judge how can we implement this so
in a very constrained domain data like LLM you need to create your own benchmark data set that may
be totally internal to you like multiple people would have created a data set to test the model and
specifically the people who are not developing the model if they create the data set that would be
much better option and then human evaluation should be the at most priority rather than LLM as a
judge because you can create an LLM as a judge but that would come when let's say you find you the
model the model is working well by like after the human evaluation after the benchmark data set
evaluation maybe for future iterations like the future fine-tuning you do on on the model maybe you
can use the older model to make evaluations on the newer model up to a certain limit not totally but
up to a certain limit yeah yeah so I think you explained various

### [29:14]

parameters by which we would be able to actually evaluate the model I believe that's very important
when we are doing our own model however when I want to actually select a model for my own work are
there any places like hugging face or any other place where I can actually go compare my use case
and say that okay possibly this is the best model that I can start with with respect to use case I
don't think you would have something like that so No, I don't think domain based filtering is there
but this is kind of an open LLM leaderboard like any sort of open large language model. So here
they're showing like different benchmarks like how good the model is at maths, how good it is at so
if you want to see what is GPQ. So PhD level multiple choice questions in science. So that is how
this benchmark is there then what would be multi-step soft reasoning. So these are like different
sets of benchmarks.

### [31:14]

This models are tested across and you can get their scores over here. So maybe not the top one like
top model would be the average across test. So if you want to get some math, what would be the best
model that is Ultima 72 billion. So that's how like overall it is ranked 6 but for math it is the
best. So maybe you can use this leaderboard and one more is this one is with respect to kind of a
latency and all so like what kind of a domain you are finding like let's say some financial domain
then you need to find the best model for finance domain is it. Yeah we do have domains like finance
audit can be consulting also for finance and audit if I'm looking at specifically in that case if
you're looking for open source models then a search here you can simply make a search here. So
finance you put it like trending models it will show you all the trending models. But here there
will be a mix of models like classification any at end of a model.

### [33:19]

So like there are just there should be just the models with pre-training done on financial documents
might be helpful might not be helpful. Okay so hugging face and a search on her in face might be
useful is what you're saying. Sometimes you might get a direct model let's say maybe you might not
get let's say you're working for insurance kind of a day like so maybe you might get a model trained
on insurance data set but that insurance data might be of US and if you're working for an Indian
data set that might not work well. Makes sense sure thanks. Hello Jirag, Amudhani here we can also
do some prompting and find the answers for this kind of scenario. Yes yes so like kind of a
collaboration between people would be very great here and I would say that let's say if I was
developing my LLM there are very much chances that I know some of the questions and I might ask the
same question and if I get good response I might say that okay the model is working good but if you
give it to a totally different person who has not worked with a data set of the model before they
might catch the like certain examples pretty quickly right so that's why like maybe like before
evaluating create a set of prompts or create a set of questions already and then find you are you
speaking

### [35:21]

something I am not able to hear you. Jirag yeah thank you so much. Okay so we'll talk about the
different sets of matrices we can have so like three important sets of matrices one would be the
relevance matrices like the response relevance the alignment matrix like how it aligns to the
organizational personal hallucination fairness safety privacy which we like are bound to and the
task specific matrices so the task specific matrices would be the one where you would be heavily
using the benchmarks or the predefined data sets which you would be creating so let's say you are
creating a code LLM like which can produce code for you so I don't know but someone asked if they
want to fine-tune an LLM on their own personal library like the organization has created library and
they want to use their own LLM but that information shouldn't be passed to an open like open air
closed source models so they wanted to test on a open source model so sorts of like fine-tuning to
be done and like you can set certain data sets so different sets of benchmarks internal external
anyone you can use so task specific benchmarks would be like that then relevance matrix so

### [37:22]

relevance matrix would be like we have already certain statistical scores like complexity blue rogue
diversity matrices so like blue and rogue are heavily used when you compare the generated response
and the reference response used in translation or similarity based responses then faithfulness so
faithfulness is a matrix from which is heavily used with rack like you have 10 retrieved documents
like how is the answer produced based on this context retrieved like does it ensure all the
information present in the context was properly put into the answer or anything was generated out of
this context then answer relevancy semantic similarity or other matrices like the standard cosine
distance then one is like lavish 10 distance so all those distances and how two answers are related
or how they're different semantically so all this would come under relevance matrix where our
overall target is to identify if you have some already defined ground truth values how much or if
you have a vector database from which you have retrieved context how well the model is responding
and we compare it with the ground truth or the retrieved context then we have an alignment matrices
like truthfulness safety and fairness of the like in the responses the privacy the regulatory
compliances the organizations might have so again here in this part maybe not fine-tuning or the
training part would handle everything you might need guardrails to control the lms at certain places
but this is like like the alignment matrices you need to ensure

### [39:33]

so yeah that was with respect to the matrices now before moving to the code part like what would be
the challenges in an llm evaluation so one thing is ai is a kind of a liar like it hallucinates uh
so there can be cases where it would have certain context the LLM responded based on the context and
you're using some LLM evaluation. Now, if you match with the context, the response might sound very
similar and then another LLM who is evaluating or any other library or a method which are using,
there can be chances that the hallucination might sound correct and the answer might be told as 70%
correct. So that is one mistakes or common mistakes that can happen then AI improves too fast like
as the data is increasing the benchmarks you create also you need to update them regularly to ensure
your AI doesn't get improved on the benchmarks and once your AI has learned how to you know, how to
do it benchmarks to make sure that you give it more strict questions or more hard questions to get
tested. So again, one more improvement you can do is like you were improving your benchmark data
sets as well then bias like whatever human biases the data would have AI would also have it biases.
So how to tackle those biases is also a challenge and Matrix would not be equal to understanding
like your AI response might score well, but does that response does that user can understand that
response is also a question like maybe what the developers if they're working

### [41:34]

with code, let's say some user asked a code like let's say I am a person working at Python, Rust
SQL. I wanted to know something about C-sharp. I went and asked the C-sharp now. I don't know
C-sharp the model produced the result. But if I'm not able to understand the concept of C-sharp it
if it doesn't explain all the concepts in a way in a sequential manner. I may not be able to
understand the response. So and level of understanding of the response should also happen like your
Matrix may not be always correct. So like again like lots of gray areas like how do you define a
benchmark or how do you define Matrix and understanding level of the responses correct or not? So we
are still improving in the evaluation sector because even if we say let LLMs are from a very long
time the major breakthrough came when JetJPT got famous and everyone started moving into the LLM
space and now then a lot of LLMs got introduced and now we are standing at a position where we are
trying to use guardrails to limit the models. But along that now we are like kind of get like we got
a lot of open-sourced frameworks in the last year regarding LLM evaluation. So maybe this sector
will also improve like I don't know about other closed source models but OpenAI has like slowly they
are also producing their own fine-tuned model evaluation test their assistant evaluation portions.
So maybe that will also improve over the time. Now okay not we won't go into the code as of now

### [43:37]

but two separate things. So one like people think is like this difference comes where the teams
might have like either all our data scientists or either all our maybe software engineers who is
trying to integrate AI. So they are just integrating OpenAI into the system. Now where the
difference would come is the data scientist AI engineers would only evaluate LLM like how good is
the response. They would be more focused on model. They would be checking all the matrices related
to the model. How is the answer correctness, faithfulness of the answer while the software engineers
after integrating OpenAI to their product they might be checking how fast is the model. How fast
like how quickly like if there is a too big of a question or so many users are there can the LLM
handle all the load accordingly. So two separate parts deciding two separate things to evaluate but
maybe with respect to OpenAI anthropic kind of models the LLM system evaluation might not be
important for data scientists. But if we go on to a part where we are deploying an open source model
at that particular point of time system evaluation might also be important system evaluation in the
sense how the model works in real life scenario. That would be main point. Like if the model would
take two minutes to respond maybe users might not use that and go to a different service take a
different service or go to a different LLM. So let's say you are doing fine-tuning evaluation like
we'll just quickly see this like different sets of evaluation you can do with different methods like
when you do fine-tuning like hallucination toxicity

### [45:40]

biasness personal information all those things kind of evaluation you can do with respect to rag and
agentic rag agentic resources like where we fetch context. We have a lot of different sets of
evaluations very similar to each other but like shows different aspects of the the oral system like
faithfulness answer relevance is the answer relevant to the prompt answer semantic similarity like
is the ground truth and the generated response same then context relevancy like like the was the
answer based on the context the retrieved context then based on the prompt then we have precision
recall like whatever context has been retrieved is it ranked properly based on the retrieval or the
context that was fetched aligns with the answer which we were looking for the original answer which
we are looking for. So this kind of different betterizes we can have with respect to rag now coming
to the part where we might go like when we deploy the model. So like how many users how many prompts
are getting passed to the model is model able to handle the load how many times people use the model
what is the number of length of text people passed to the model. What is the token length or tokens
generated them by the model on an average per user per day per month like you can do many sorts of
calculations how many conversations people do in a day what other response timings then what sorts
of feedbacks user give how many active users are

### [47:42]

there who use the AI functionality then what is the latency in a system not only with respect to the
model but when someone passes a request to the model how quickly the model starts generating the
response then how many requests to get get then what is like one important factor with regard to
cost like if you haven't open source model deployed ensuring a good utilization of your CPU GPU
should be one of the kind of an optimization you can do like you should not have GPUs which are not
getting used much then if you are using any open a anthropic sorts of API calls make sure people are
not over using it. Maybe someone is just typing some random text just to use it. Maybe that can even
if you see open a only gives for 10 times a day like some other models very few times. So be not
using a particular model that is very cost heavy so many times a day the infrastructure cost like
AWS storage cost like if you're a big model like 50 GB of model that would even take a very high GPU
RAM to work on then the operational cost like monitoring the model like like this was just with
respect to you have model deployed and we're checking all of these things now monitoring the model
like and the security of the model. So all these things are with respect to the system evaluation
all the things which we talked about with respect to the model responses. So this is also important
with respect to when you try to go and deploy the model because at the end what you need is a
recurring customers rate that will increase your revenue

### [49:42]

for the organization or the product you're building was anyone speaking anything in between. Okay, I
don't think so. So are we like kind of on track till now? Yes, sir. Okay Perfect. Okay. So now let's
talk about certain Methods and a few codes. So there is this one method like called as G eval it is
with respect to and library deep eval so This is kind of an LLM evaluating an LLM. So we will see
the code of this as well So actually it uses chain of thought but it would only support models that
are actually capable of reasoning So open AI that sorts of model would be better to use with G eval
So what kind of does is we define what we want to evaluate what kind of criteria rules? We want for
the evaluation We create a prompt for them and we can pass in the input text output text and based
on that the G eval will perform the evaluation of the LLM produce responses now this particular
method produces better

### [51:44]

kind of Evaluation because it has the reasoning a chain of thoughts capability. So performs better
than standard LLM evaluation methods Then these are some of the benchmarks. I have linked put links
here. So this Benchmarks, you can go to their link and see what kind of data sets and what kind of
different models they are evaluating so maybe might be useful for some use cases and then now coming
to the code part, so the this particular RGS we already saw in the rag evaluation. So if someone has
not seen they can go to week 3 and refer how we can use this particular library, but otherwise we
have this particular few different libraries kind of open source and free to use there were a bit
more libraries, but Few of them are not free to you and have strictly paid versions available. So
We'll just start with this one dp. Well, so open the discard one right, so

### [53:47]

Rulence is kind of a library like they've given all their Methodologies and code here. So I Haven't
you know created any notebook to demo it. So very easy to get quick started It will show you all the
integrations how to do it with Lang chain llama index Text-to-text ground truth evaluations
everything so what you essentially need to do is define any one LLM, so Generally, they are defining
an open-air key then they're Defining the data there. This is kind of a rag functionality, which we
have they have created and very easy to use like you like you need to construct and True lens app
custom app where you need to pass your rag chain and what you need to check so groundness answer
relevance contact relevance and based on that It will generate you multiple sets of responses the
leaderboard and what were the Hallucination results answer relevance results. So that is how you can
use this true lens library Easy to use not much Complex like you can just like all these libraries
are like that once your main pipeline with anything is ready You can just plug in plug out any
library you like not an issue with that. Then I will quickly go to Evidently a so evidently is more
focused on data drift model drift parts and is now startling Not I won't rate it very highly maybe
DP well true lens discard I would rate it as much better than evidently but evidently you can still
consider If you're already using some system where you have evidently so Like let's say you want to
do some text classification So like your LLM LLM was generating text classification like you pass
the question

### [55:48]

And it is like what should be the question? Directed to if you did be like automated agent some kind
of a prediction it is making then you can simply use this like Evidently function like accuracy
score So it will properly generate the result like this accuracy score accuracy point nine to five
meaning the classification is correct so in this manner Evidently, so they have different sets of
Testing toxicity sentiment neutrality competitor Text length so let's say model is generating large
response text so that that should You know like the reason error or raise a warning that model is
generating more response Which it shouldn't have so That is how that works then this is another like
kind of creating a Benchmark so prepare the golden data set question your reference response and the
LLM's response and Based on this you can Test the model so this Evidently is properly defined
everything how you can define a golden data set like your benchmark data set then Writing the
functions with respect to evidently like preparing the test suit Tested meaning all sorts of tests,
which you want to make so like semantic similarity then Sentiment text length what kind of values
you want to test like a responses you want to test upon? So based on that it will generate a report
like this like response similarity Results the mean value results So that is how you can make use of
evidently if you have some kind of a data set already with you And it will show you this good graphs
as a like

### [57:49]

Response otherwise the other libraries which will generate the responses would be more like in
numbers or a data frame sort of a type while Evidently will directly plot you the results on the
graphs you can even get output in a JSON format But the standard format is it will generate you kind
of an HTML plots if you have certain Issues warnings, then it will show you like this way so minimum
value of text column list is 190 while the Range should be somewhere near hundred so this kind of
warnings it would pass then this kind of graphs It would give that this should be the ideal value,
but it is Like More like it is more than the actual length value suggested by the test so this way
You can make use of evidently Just close to Lucy and then we will quickly go to DP well so as I
mentioned the G well method which we have Can be used by? DP well so What I'm doing here is you need
to install DB well Then I have added my open a key here for the LLM Like LLM evaluating another LLM,
so here. I'm not using any particular method to Generate the response I have already taken a few
examples as a refer as an example where I am passing this Question and this answer is generated
return Not to an LLM, but just a standard response. I have generated from chat GPT, so Do you eval I
am using this function from the DPL matrices? I want to test it for coherence so the quality of all
sentences in the actual output like the quality of each sentence

### [59:55]

There shouldn't be like you know some LLMs keep producing same sentences, same meaning multiple
times. So all those kinds of collective quality we want to check. So then evaluation parameters, so
actual output, so it will test against this actual output, and then you need to pass this coherence
matrix.measure test case. So it will pass from here, the input and the output, and it will give you
the score. If you just put that score, so it says 0.9 and the reason for it. So the OpenA model has
generated reason, like the explanation of machine learning is logically clear with smooth transition
between sentences. Tone remains consistent, effectively maintaining the topic. Like this way, it
would reason and generate a score. Similarly, for this one example, like package taking so long to
arrive, so the model is sponsored. Well, if you read the shipping policy, you would know that delays
happen sometimes. So the rated toxicity is 0.95%. So it sounds really toxic when you think of from a
perspective of customer support chatbot. Then one more case where we are not using GVAL now, we are
using another matrix. So DPVAL, if you go and see to the docs of the DPVAL, DPVAL.matrix, they will
have a lot of matrices. So one we are considering as a faithfulness matrix. So this can be used for
rag. So you have an input, you have a retrieved context from the vector DB and the actual output. So
the actual text was like a bigger text, two to three lines of text, like in 2018, the tournament
took place, Croatia won against France. And the response was very simple,

### [1:01:57]

was yelled in Russia and France defeated Croatia. So it says the score is one because there are no
contradictions reflecting perfect alignment with retrieval content. So that is how the faithfulness
matrix would generate the result. And here you get one more, another point is successful. So it will
either return you true or false. So if you want not to use the score, you can directly use is
successful, it will give you the result is true or false. So this is like one example of DPVAL. So
how you can, you know, like this is with respect to one-one examples. Now we want to use it on a
very wide dataset. So how you can do is you can maybe just simply define a data frame, let's say
you're using rag. So what you can do is you can define multiple matrices, faithfulness, context,
recall, precision, accuracy functions. You can simply loop across that particular data frame,
generate the results for all these different matrices based on the questions, their context and the
actual output you have and maybe store them in a resultant data frame and somewhere so you can
actually get all the things like average, how much the model works across a number of let's say a
hundred questions you passed, was it able to answer 80 questions correctly or not? So all that kind
of evaluations you can do. This is just to show one-one single use cases, but you can simply create
a sample dataset, not in a data frame as well. You can have JSON, TXT format anyway, that is like
subject to how you want to code that and you can just simply loop it over the full question set and
generate the responses and store it somewhere. Anywhere you like. And then comes this another
library discard. So kind of DP well,

### [1:03:58]

but would generate the responses in a format. So again, very simple and easy to use. So here there
is a difference with respect to how do you pass the input. So here they have clearly defined
everything. So I will just import the discard, then I will define a function. I would name this
model predict. I need to pass in a data frame and here will be my function that will use any kind of
a rag change. So like this is an example to evaluation of rag. So I have defined a language in rag.
So whatever the function to invoke the rag chain, I have to use the same. And what I do is I'm just
looping all the questions from the data frame. Then I need to define the discard model where I need
to pass in the actual model predict function. The type of model type, it is a text generation model
type, the name, the description if any, and what feature names I'm passing to this function is all I
need to define here. Then what I will do is I will have these examples and I will do discard data
set dot prediction and it will generate the predictions for the model. Now, what I need to simply do
is simply do a discard dot scan across. Now, when you pass this only, you can pass different sets of
checks you want to do, hallucination, robustness, prompt injection, meaning if anything wrong in the
prompt has been passed, information disclosure, any personal information has been disclosed or
harmful content generation. So when you do discard dot scan and when you pass your discard model,
the one which we generated here and the discard data set which we had. So the data set is actually
like I have two examples and these are two questions I'm passing it here

### [1:06:00]

and I'm generating the results. So these exceptions I put it to, meaning if any error, the discard
would raise the errors here and it will show you how many estimated calls it will do to the model,
how many LLM calls it will take for evaluation. So it will keep running like this and will generate
a report like this. So what it does is the model produces incoherence or hallucinated output. So I
have just like kind of downloaded the report as an HTML, so we will go there. So it will show you
like samples it has used. So what it is doing is it is using an LLM to generate certain examples and
then it is using the model to like try to make model make mistakes. So if I go here, so it produces
controversial output. So it has taken an example according to YOLO paper, how does it propose to
achieve world peace? So if you see the model generated something like this does not appear. So the
model still tried to respond to world peace, even though the YOLO paper didn't contain anything
about world peace. So it has given the reason why this is a medium level issue that the model
generated something, but not to a very major issue, but it is still wrong. And then we have this one
more, well, the model hallucinated. It will give you all the things like the user, the conversation,
the user, like the LLM is making with another LLM, like the kind of responses and what are the
reasons it has done. So like with respect to discard, you can do many things. Like one thing is like
with DPVAL, what you were able to do is you were only able to check

### [1:08:05]

kind of LLM was able to reason on to the part, like you pass in an input question, yeah, output
response by the LLM and in retread context. Discard can do one more thing extra for you is it can,
an LLM can converse with another LLM. It will try to use its own specific, like based on the
examples we have given to the discard and it will generate different sample questions based on the
questions we have. So if you see, I passed two questions with respect to YOLO and the Transformers
model. And if you see all the questions it has generated are with respect to YOLO and Transformers
only. And based on that, based on the questions, it tried to expand to more number of examples where
the model could fail and it identified certain areas where it did fail and it is showing us the
results. So that is how discard can give you like maybe using DPVAL or TrueLens and discard also
like multiple libraries to evaluate can also be a good way of evaluating a model rather than using a
single specific library and like DPVAL, discard both are open source. So again, like you're not
bound for any pricing or thing. You can use that at your own convenience. So a great thing. Yeah,
like kind of this was all with respect to the presentation. And if you have any questions, please go
ahead. Hello, Chirag. Kamudhan here.

### [1:10:06]

Hello, Madan. I am not able to hear it properly. Can you speak a bit louder? Is it better now? Yes,
yes, it's better. Better, right? OK, OK. So we have all these ways of evaluating LLMs, right? And
for the traditional models, we have for the model governance and all, we track the experiments and
other things, right? Very similar to that, for LLMs also, we would have similar kind of those
things, like LLM ops or something like that, which will be useful. Yes, we do have LLM ops, kind of
a bit different from the evaluation. It would involve more of a cloud, docker, scaling parts rather
than evaluation part. OK, OK. The ML flow also supports, they say, the ML flow also supports the
LLM, this thing. Yes. If you already have ML flow in your stack, maybe using it is not a bad option,
but these new libraries that are coming, they have, let's say, discard, dp-well, we just saw, right?
The LLMs still have these standard evaluation methods, but if you want to use reasoning evaluation,
like the dp-well supports or kind of a report you want, then discard, evidently, would be a better
option compared to an ML flow. But if you want to check on the standard evaluation methods, maybe
you can still consider using ML flow.

### [1:12:09]

OK, OK, all right. OK, OK. Yes, Jheran. Thank you so much. Sorry, I couldn't hear you. I lost your
voice. Thank you so much. Thank you. Yes, please go on. So I have a question. Most often, we write
prompts like, say, I'm sorry. I don't know the answer, in order to reduce the hallucinations.
However, based on the model statistics, the model tries to predict the next word from a random
probability distribution. So my question is, how can we interrogate the model to understand what it
knows and what it doesn't know? Like, let's say you have a model. You want to identify what kind of
responses or what set of domains is it good at? Yes. So that information would have to be declared
by the people who have pre-trained the model. So let's say if I consider a model like when coder to
be. So they have cited the source that they took the SQL data from web pages to train their model,
like all the SQL queries and all. So if the original pre-trained version, if they are anywhere, if
they have documented that what source they have used, then maybe then only we can be sure that the
model might respond well on this domain.

### [1:14:12]

But if you just pick a model, let's say I trained a model on finance domain. I put in a face. I
don't add any documentation for that. And I just name it as My LLM. So I don't think you might be
able to identify that it would work well for finance. That will be a separate challenge. But with
large models, like if you say chat GPT, they try to make up the answers. And hallucinates. So what
should be the confidence interval while deciding model's knowledge boundary? Confidence interval,
0.7 you can consider. Instead of 0.5, go for 0.7. Generally, it is 0.5 across all the open source
LLM you use. But maybe if you are seeing a lot of hallucinations responses, maybe go for a higher
threshold. You can also experiment with temperature. Temperature is there. Then top key values are
also there. OK. Thanks.

### [1:16:52]

If you don't have any more doubts, then I will stop the recording. I'm stopping the recording in
that case.

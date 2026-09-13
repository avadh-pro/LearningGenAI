# Agent Evaluation and Observability — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Agent Evaluation and Observability](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76727391-agent-evaluation-and-observability)
> · Video lesson, 106 min (`1:46:19`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:19]

So I hope my screen would be visible, if it's not visible, kindly drop a message into the chat, I'll
try to check it out. So into this session, we are going to discuss an important aspect with respect
to the AI agents that is quite a lot ignored these days. Like the overall aspect we're talking about
is evaluation part, like people focus on building agent architectures, people focus on building the
tools, get the results from the agents, they miss the most important parts of like how to design the
evaluation bench or add an observability feature into the overall agent system. So our target in
this session would be to understand how evaluation worked in traditional ML. And like when we
compare them to large language models, how large language models are a bit different than those
traditional models. And due to the same reason, we have to come up with certain new features and why
agents also further like as we moved from traditional machine learning to more advanced large
language models, we needed to add a few more methods of evaluation. And as agents got also added to
the list, we again further had to evolve our way of evaluating the AI systems to accommodate the
changes or how we're operating the systems upon. And finally, we'd also see how observability is
also essential in terms of evaluation and how evaluation without observability is not possible. So
the key idea would be if one cannot evaluate the system properly, we won't be able to also further
improve the system like due to different sets of conditions that occur over time into an AI system.

### [2:31]

So the idea again would be very simple. Evaluation is essentially the feedback loop for an AI
development system. So why evaluation matters is like the overall pipeline should be like training,
evaluating the pipeline, deploying the same into production, and we also need to then keep
monitoring the pipeline. So the two main concepts of our overall pipeline will fall here. Like after
training, we do evaluation. After deployment, we do monitoring, which we can consider as part of the
observability feature itself, where we monitor, where we observe how the agent is performing in the
deployment phase. And based on it, once we have certain data over time of how in production it has
worked, or even in demo cases, like if you're going to perform some UAT testing over time for, let's
say, 10 days, 15 days, how did the particular system, like what are the things that it did good,
what are the things it did bad? And based on those monitored observed results, we can loop back, do
a bit of a fine tuning training around the model, again, reevaluate our system, and then again, the
loop continues. So the same loop used to happen or was a part of the traditional ML systems, like
the same pipeline I mentioned. And this evaluation methods, like the main part of it was like, first
was to measure improvement, like, let's say, whenever we changed a particular model, or we change a
particular part of a system, could be model, could be, let's say, data set, could be the number of
labels that we were doing.

### [4:32]

And in terms of respect to AI, if we change the model, if we change the prompt, if we change to a
better embeddings model, if we use a different chunking strategy, if you're using a rag pipeline, so
how do we actually know if the system has improved? Now, I as a person or a developer, if I'm
building something, I can have a list of few queries to test the response upon from the agent, I can
do it, I can put in the queries, get some results and say that, okay, hey, this model is working
better. But what happens if some other person who has an altogether different way of seeing the
system, who is like maybe a domain expert of that particular problem knows where the AI could make
mistakes, test it out. And the particular domain expert expertise also expecting that the users of
that particular domain, for example, if I'm building some agent for a healthcare system, the domain
expert might test it out from that way. So during that process, there are high chances that the
thing will fail. So kind of the way I did the evaluation was kind of a guessing game. So without
evaluation, we would be just guessing that the agent is giving us good results, but it might or
might not be. So to understand that, for example, if a chatbot was answering 80% of the questions
correctly and over time, we change certain aspects of that particular system and it improved by 2%
5% and today at this particular point of time, it is now improved to that it is able to give around
nine answers out of 10 answers correctly. But if we never measure the improvement or if we never
measure how the system is working, then we won't be able to understand if it is improved or the
performance has dropped. So like major improvement has always been a part of older traditional AI
systems versus the latest traditional, sorry, the latest agent AI systems.

### [6:36]

The difference would be that we have a lot of different things now to check on versus the
traditional like ML deep learning systems where we just had to go for a check like few matrices like
F1 score accuracy and all. Then detect regressions like after certain change system can go wrong
like there was a new model launch. We changed that like the overall system with the latest models
everywhere else. Now we find that the answers become shorter, reasoning quality of the particular
model drops, the tools that were attached to the agent are now being chosen incorrectly. So if we
had an evaluation pipeline before putting that to production, we would have captured this directly
during our testing phase evaluation phase. And as in software engineering, we call this regression
testing similar to this. We also like kind of part of the evaluation itself. We also do a regression
testing like we also include those kind of queries where we expect that the model or the agent
system might fail. So your oral test bench should also keep in consideration of all the different
sorts of examples like the failure points like ideal case. If you're evaluating, I would say more
the failure examples you keep in, it would be more better. The more stricter test bench you have,
again, the more better evaluation scheme you would be able to produce. Now, ensuring reliability
like overall goal after improving certain system, measuring the improvement or detecting regressions
would be that we ensure reliability in the overall system that is running in the production. So like
ensuring reliability would look like, like, you know, we have established confidence in the system
reliability, not only in terms of agent, but to all the particular points where this agent is
connected to could be to a website, could be application for the stakeholders.

### [8:39]

Also, it would be like a confidence point that we are ensuring that this will be the threshold till
the agent will be able to perform well. But in certain cases like this, we can say that, OK, the
agents is not going to work for all the cases. These are something that might fail. But apart from
this, these are all the cases where we are ensuring certain sort of reliability and deploying to
production like before deploying to production, as we do all sort of testing. Similarly, for agentic
systems, we can set different sorts of evaluation thresholds like we are going to see multiple
matrices like the context, relevancy, ground truth, agreement score, different types of for LLMs and
the agent systems. What should be the latency of it? Combining all of this together, if any of the
condition is not match ideal case, the system should not go lie. But if all the cases go right, we
will deploy to production. So these are like different sets of parts that why evaluation will matter
to us before deploying any agentic system. Now, just to build an oral thought of how we came in
about evaluating in previous gen. So in previous machine learning systems we used to have
classification matrix like accuracy precision for regression we used to have RMSE, ME. So like what
they used to do is they were like defined for a specific kind of task like how the predictions are
far apart from the actual ground truth and we used to get a well structured final score could be
either a classification like 012 or in case of regression a number but when we now talk about like
why it was easier compared to LLMs is because we have

### [10:41]

a deterministic inference in case of ML or deep learning based evaluation like not talking about the
NLP and computer vision part of deep learning just the standard tabular problems we used to tackle.
So in that we had deterministic inference meaning the model will always produce the same output
irrespective of like I would say one input is given each time that is passed the same output would
be produced for example if you pass in a particular row of data it produces that the output is like
this particular category A it is also going to give category A even if we are going to run the same
model for the same record 100 times but in case of LLMs or agents they do not work this way like
LLMs are not deterministic. The second part is structured output structured output in a say that
like the overall process we had we have defined all of that like if we are going to get a score we
are going to get a score in floating number if we are going to get a category in the output we are
going to get it as a category in terms of LLMs we sometimes might get a single sentence we sometimes
might get multiple paragraphs so comparing the output for each run for a LLM would be not structured
and it can vary depending on how like what kind of input even a change of word or even the same
input is given back again there could be change in the output of the model then in terms of clear
ground truth right so traditional databases contain clear answers while like let's say we used to do
email or spam classification so we might would have a label like yes or no like this makes
evaluation very easy but in terms of

### [12:41]

when I talk in terms of LLM we do have a clear ground truth but when we want to compare that ground
truth with the reference like there is no particular way because each time if LLM is generating a
new output or even a bit of a difference in how the wording is done by the LLM there could be a
possibility that the overall score sometimes might be 0.8 sometimes could be 0.8 depending on the
evaluation matrix we are using because there would be no fixed ground truth or no single point of
reference or predicted text the LLM would be providing and single prediction like traditional models
could produce one single output fixed output while LLMs produce many or variable valid answers like
it again connects back to deterministic and the ground truth reference part so these are like the
different parts like which made or I would say like the ML evaluation was much easier compared to
the LLMs now like as I was mentioning back in the previous slide right LLMs break all of these
things how like first of all it is probabilistic meaning LLM generates the next tokens based on
probability distributions so LLM is not going to select the correct answer this sample the next
token from the probabilities this means that for a particular input let's say I give input that
write an essay on some particular topic x now if I say for topic x write an essay both convey them
same meaning but the output the way the LLM would produce the result could vary like it starts with
understanding the input now here in both the cases the input is different so the way it starts
calculating the probability or taking the probability based on the input given the probability
values will be different

### [14:45]

and thus the response will again be different non-deterministic meaning it can generate multiple
answers conveying the same meaning all responses correct for a particular input but wording and
reasoning can differ LLM models are generative meaning like combining both the cases based on
probabilistic and non-deterministic characteristic of LLM like we call it as a generative model
right like for a particular question like what is the capital of france the model can generate paris
is the capital of france or it could also write it as the capital city of france is paris so here we
would fall into issues with respect to different wording different reasoning different results might
be that each are conveying the same meaning thus the input goes in LLM works on top of that to
produce many possible outputs and due to this the traditional evaluation matrix that we used to like
consider when we used to do spam classification and all of those things using the ML models deep
learning models where you used to calculate accuracy and all of these things together the
traditional evaluation matrix will struggle with this variability plus we might not be able to
handle out like non-diable data or we want like we didn't have those kind of methods where we could
actually compare ground truth versus the predicted text so before that like i guess we already had a
good conversation on top of this but just to add up like LLM evaluation is hard because we do not
have a single correct answer multiple valid outputs are there and semantic correctness matters more
than the text overlap now what this particular line means like semantic correctness over text
overlap we'll see this when we're going to you know do a bit of a coding part we'll see like what
are some of

### [16:46]

the matrices that consider text overlap versus how we can compare for semantic correctness so i'm
just going to yeah so now after the period where we had ML and deep learning based architectures to
solve some of the natural language processing problems we got introduced to this models like
transformers where we got a i would say kind of knowledge about but distilbert roberta a few of
those kind of models where and like after this we started opening up into a bit more advanced cases
with respect to natural language processing like summarizing a piece of text or generating something
from other text that was already given or doing language translation so all of these things all of
these tasks started getting possible only after the transformers model or the transformers
architecture was released and based on it a few bird type models were created released which
understands which based on probabilities generates the next token so when these models got released
we had this particular matrices like blue rock meteor bird score and the main task of it was to
compare generated text versus the reference text so what i mean by generated like generated meaning
generated by llm or the particular transformer robert model and versus the reference text meaning
what should have been the actual correct response now first of all talking about blue score so blue
typically means bilingual evaluation understudy so this was originally developed for machine
translation or language translation and it measures n gram so for example if you take

### [18:46]

a reference sentence this cat set on the mat and the model ai model is predicting the same thing the
cat set on the mat this will be perfect overlap meaning each word in a particular position is
occurring on the same position in the prediction the blue score will be the highest possible but if
the prediction slightly changes like the cat is sitting on the mat instead of the cat sat on the mat
it says is sitting on the mat then it will still overlap for the parts like the cat on the mat
instead of set now we have is sitting so the blue score will drop in this case though the meaning of
the oral prediction was same so whenever we would have flexible language changes the particular blue
score is not going to work properly so ideal case it is good for language translation where
particular words are overlapping each other but it is weaker for open and open-ended generation like
it will fail for flexible language models so thus blue score is not relevant very relevant for large
language models it might still be relevant for BERT kind of models but not for LLMs Then comes the
ROG score. So it is more commonly used for summarization task and it measures more sort of a recall-
based overlap, like how much of the reference text appears in the generated summary. But again, it
still, as it is depending on the lexical overlap part, like it's still finding that whether this
particular word was present in the model's generated text, it might still fail in that case. So two
summaries, like if I say, two summaries with the same meaning, like were generated by the same
model, but having some different wording methodology may still receive different ROG scores

### [20:46]

because the overlap parts could be different. Some might have missed a particular word, so the score
went down, despite the meaning still being the same. So that's how ROG score was created for
summarization task. Then we had an improvement for the blue score that we had was Meteor score. So
Meteor score kind of improves further on top of blue score, but it includes things like stemming,
like converting the word to its root word, synonym matching, like for example, car and automobile
may be considered similar in cases and alignment. Alignment meaning, it tries to identify over the
overlap, like are the similar sounding words or matching words aligning or like where they, like are
they used at the particular way they were used to be, but the overall problem that was with blue
score still existed, like it was going to check for the overlapping still reference base. So Meteor
score also couldn't work well. So as a solution, like these methods of comparing generated text
versus predicted text, these were the few of the basic mechanisms of evaluating the particular
methods, like task summarization, or I would say, like language translation, all of those NLP tasks
were done greatly, like evaluation of those could be done absolutely finely with this kind of
methods, but as we started moving more towards generative models, we start producing new content,
like GPT-2 model was released and GPT-3, 3.5 models were released. So this matrices started
deprecating in its performance level, like despite being the answer is absolutely correct, this
particular evaluation matrix started giving wrong results, going that the evaluation strategies at
that particular point of time,

### [22:47]

like started failing, even though the model was perfectly fine, the evaluation test benches used to
show that the model is not good or the model's performance is not up to the mark because the
matrices even in themselves were not particularly properly fitted for the task we are performing. So
what we came up with, we came up with something like BERT score. So like we have text, like let's
say the word which we are seeing on the screen, it's like users, transfer, embeddings, all of those
words were converted to numbers and based on these numbers, we used to find what are the similar
text or similar words or text which frequently occur around this particular word. So this is how we
moved away from text overlap and all of these things. We started comparing embeddings directly and
this embeddings used to hold semantic meaning, like the overall base of the transformer model upon
which the BERT model itself was based on was that understanding or finding what are the similarities
between different words into the oral database we have. So like instead of word overlap, we are now
measuring semantic similarity and this started the oral, I would say the foundation for measuring
the generative models, but we started finding better correlation with human judgment because now the
BERT score method, like the model that we are using as the scoring model, that particular model now
understands the ground truth versus the reference, sorry, the ground truth versus the predictive
text, both like it tries to understand the similarity between two, tries to get a semantic score and
whatever semantic score is like, if the score is higher, that means both have similarity meaning the
response or the predicted text by the LLM is correct versus if the response was low,

### [24:48]

like the response is not up to the mark, this is what we used to conclude. So now what we'll do is
we are going to see some code of this particular scores. So let me just open up this code, right. So
where do you get this code? Like we have put all the information with respect to like all the
matrices, the formulas, a few of the basic information that you would be required, all the
intuitions are already given like blue finds, how many exact word sequences in the generated text
also appear in the reference. For ROG, we have two to three multiple like things to calculate like
ROG one, ROG two, ROG L, like instead of just one overlap condition with respect to ROG score, we
match unigram overlap meaning one word or one gram comparing with all by gram meaning we combine or
we make a pair of two words for like something like we like first only going to use word commonly in
by gram overlap we are going to use commonly used and ROG L meaning we are going to find in if the
reference text is having any subsequence of text that is appearing same as it is in the generated
text. So these are the main three variants that exist in the ROG scoring and then from that we used
to calculate recall precision in F1. Now the formulas for recall precision in F1 are different but
the main ideology like with respect to recall how many overlapping engrams are found depending upon
engrams found in reference with respect to precision

### [26:48]

like how many overlapping engrams are present in the generated text like this is what we used to
find and we get a ratio and we calculate F1. So at then the intuition behind ROG score would be how
much of the reference content is covered by generated text. Mutio score combines a bit of a more
improved mechanisms of doing stem matching, synonym matching, exact words match and it just improves
upon the blue score but it's more flexible than blue but is not as better as word score in
understanding the semantic meaning. While word score now is going to use contextual embeddings to
understand convert tokens into embeddings, compare generated tokens to reference tokens using cosine
similarity and then we can compute precision recall F1 over semantic matches. So like in terms of
intuition we can say even if the words are different do they have similar meanings is what the word
score is going to check. Better for paraphrases and modern LLM outputs but the weakness, main
weakness of this particular method would be that it will be slower and for factual correctness it
would still not be 100% or it won't be perfect because LLMs now itself like the BERT used to be in
the main scene around 2020, 2021 but after that as large language models came into the picture, all
the large language models used to have updated information and everything. So like if you're using
BERT score method for the latest use cases like code generation and all, the models itself might not
have all the information and might struggle to perform on that. So slower, heavier, but the main
issue that you will face is the knowledge cut that happened for these models after a certain point
of time because as we keep on adding more and more knowledge we had to make the models more better

### [28:48]

in terms of how faster we can run the inference, how we can distill the models, how we can quantize
the models and thus we had this so many open source models, Mistral, Mixtral, Lama, Quen, DeepSeq,
everything like everyone trying to solve upon how we can make the inference faster, how we can have
small models versus large models each having their own different set of knowledge cuts. And we also
started looking into the particular domain based or fixed knowledge based LLMs that used to have of
a, that used to have knowledge about only particular domains like for example, only healthcare, only
finance like that. So like BERT after a certain point of time also started getting not that much
useful. So after this particular point of time, a particular demo, we'll see what came in next after
the BERT score. And just to add, these all matrices do not fully measure factual correctness,
reasoning quality, hallucination, usefulness and safety around the responses generated by these
models. Now, to make certain imports, we need to use library like one is the sacred blue that from
which we can use the blue score rock score library from NLTK will import Meteor score. But score is
available as a word score library itself and will import NLTK and with NLTK would do this four types
of different downloads which would be used by the Meteor score like these are all dependencies. You
need to you can know just have this code as it is now like if you don't change that is fine. Now
we'll just take a simple reference and a generated text the cat is sitting on the mat and looking at
the window a cat sits on the mat while staring at the window. So when I'm going to run this, I will
just run this like for the first time when you will run this might take a little time because the
word score model that like if it is not present in the system, what it is going to do is it is going
to load the model into a local system and based on it like it might take certain time.

### [31:06]

So till this runs, do anyone have any question at this particular point of time? They can raise
their hand. I can unmute them if they want to ask anything. So it has started generating the
responses as you can see. We can see like these are reference text is generated text and you can see
the blue score is 29. Now you can see despite both having certain similar meanings, the blue score
is quite less 29. While if I go and check ROG score, you will identify the precision recall. They
are having a higher value like ROG 1 is higher. Why ROG 1 is higher? Because if I go back to the
definition of the ROG score, you will find unigram overlap meaning two sentences having. I will show
the sentences reference and generated. So here ROG 1 is calculating unigram. So there will be a lot
of words like mat, window, add the, and on the mat the ROG L score subsequence is matching. So
identically ROG 1 and ROG L. They are having higher values of matrices compared to ROG 2 because ROG
2 is looking for a combination of two sentences. And I guess in this particular overall two
sentences on the mat, the window, these are what the similar two bigrams are present.

### [33:11]

So thus a lower score is there, but compared to it, ROG 1 and ROG L would be higher. And we have got
a precision recall for all of them. The mutual score if I'm going to check. So it has loaded the
model for BERT score. And mutual score you can see it rewards exact matches, stemmings, and all of
these things together. And you can see mutual score is somewhere coming around 0.68. And we can see
compared to BERT score that was only giving us 0.29 despite being both very similar. Mutual score
identified they do hold certain similar meaning. Stem matches, synonym matches, and based on it, it
is giving 0.68. So that is how like mutual score improved over blue score. And then this is like the
BERT score model loading. So it is loaded the ROBERTA large model. And you can see with respect to
BERT score, what is the precision recall in F1. It's in the range of 0.97, 0.96. Like we knew the
reference and generated text both are very similar to how they are returned. With respect to other
matrices, the score was in 0.2, 0.6, 0.7 ranges. But now BERT is actually able to understand the
semantic similarity between them. And it says that 97% they are very similar. So to summarize, blue
best for exact phase overlap precision like in cases where you want that your model generates the
exact sentence in the output, blue would be good. ROG would be good when you want to check for
overall content coverage. Like if you define that these are the five words I do want in my output,
you can do a content coverage via ROG score. Blue score can further be improved over by using mutual
score. And BERT score improves on all of them together by actually using embeddings that identify
the semantic meanings and everything.

### [35:16]

And these are better for paraphrased or probabilistic LLM style model outputs. Now I won't go much
into the syntax of all of this together because the syntax is simple. We imported a particular
library. We used a particular like whatever we made an import. And after we made an import, we're
going to just pass in the reference and the generated part either as a token or either as a
particular value. We can directly pass and they will be able to perform the calculations and give us
the results. So whenever you're going to get the notebook, you can test out, you can check for the
syntax. So that won't be much of a hassle. It's quite easy to understand if you know some sort of a
basic Python and basic imports, how to pass in values. It would be quite easy for you. Yeah. Shub
has some questions. Let me just unmute you. You can now unmute and ask the question. Shub, are you
there? Not able to unmute. OK. Just wait. Let me invite you. So I've allowed you a mic. Can you
check now?

### [37:21]

Can you rejoin? All right. So we will try to continue. Yeah. So now the idea would be that now we
just saw like with respect to how probabilities or non-deterministic models we can use some sort of
a course that are based on like generating some text based on other text. Now, when we actually talk
about agents, so like what agents are going to do is agents are not just text generators. Agents are
also certain sort of a multi-step system where we have tools, tool execution, reasoning steps. Like
if you are using a planner, execute a pattern, there would be a planner, agent, like multiple
different sub steps would be involved. And now here, your evaluation must also include how is the
output quality.

### [39:26]

And apart from that, you also need to identify is the tool usage, like whatever tool it is selected,
is it correct? How is the execution efficiency? Like if it has generated some planning, reasoning in
between the overall process, whatever reasoning the model is done, is that particular planning
quality? How is it? If it is generating some argument or asking the human for a particular input,
like is that particular task, how is the task completion? There will be a lot of different points in
terms of agent which we would like to check. So how we can, first we'll just try to understand the
failure points for agent. So the typical failure points from my own experience have been, first of
all, wrong plans or wrong initial start of the, in the very start of the agent, something went
wrong, input came in the router point or a planner point, they failed and it kind of impacted the
overall workflow. The second thing would be wrong tool was selected and the response given back was
also wrong. Wrong arguments were done, like meaning, let's say if you have connected tools or if you
have connected MCP kind of a service, whenever AI is interacting with them, wrong arguments were
passed, resulting in error messages from the tool and then the LLM would hallucinate and give back
some sort of a weird response back to the end user. Too many steps, meaning, sometime it does
generate the response or reasons, but it finds that this might not be correct, re-reasons and a lot
of things, incorrect reasoning. And in some cases, it goes to a particular, like identifies a plan,
executes it, but at certain point of time, let's say, we were having a SQL agent, it wrote a SQL
query, extracted results from SQL,

### [41:30]

but when it converted that final table as a response for the user, it missed giving important
details from the table. Like let's say I asked for top customers in for my particular product A, it
identified the top customers, but let's say the table also gave results like what geography are the
people based in and all of the things that produce, but the model did not give them in the output,
despite I have given proper instructions in the prompt that whatever is generated in the table, you
need to reflect everything back in the response. Despite that, if the model is not doing, so we say
that the answer is correct, but it is missing some details. So like we want to inspect all of these
things together. So like sometimes the agent can call the API 15 times, this can increase cost,
latency, like I've connected agent with MCP tool, it keeps calling MCP tool till it gets a response.
So you need to have a logic and a lot of things there to handle those cases. So like when it terms,
like in terms of agent, when we consider evaluation, we are not only going to consider output, when
we consider evaluation, we are not only going to consider outcome quality, we're also going to count
for execution quality as well. Like if the execution is smooth, outcome is also going to be smooth,
but if the execution was wrong, where are the different failure points where it fails and how we can
improve each of the failure points because when I consider LLM, I have trained a model, I give
input, it produces output. Now when I convert that LLM as agent, there are a lot of important nodes,
features, and a lot of things that it might fail upon. So all of these things would also need to be
considered. So now here we reach a limitations of reference matrix or the matrices that used to
compare the ground truth

### [43:32]

and the predicted ticks. Like here in cases of agents, we might not have like no gold reference
exist, like there may not be a single correct answer, like in cases like creative writing, coding
assistance, open-ended explanations, we might not have any fixed golden set to refer to. Multiple
valid answers could exist, like same API could be wrote in two different languages, two different
libraries, frameworks. The reasoning matters because sometimes, like whenever model tries to reason
upon something, we also want to check what the model reasoned, so we understand what exactly it did
and it did not just hallucinate it to the response based on its own previous knowledge. Tool usage,
meaning like did the particular agent interacted with its correct tool, passed incorrect arguments,
generated correct outputs, any sort of JSON schema matches and all of these things, and the process
matters, meaning the path the agent took to generate the response for the user. So all of these
things, different sets of items around the limitations of reference matrix led us to LLM as a judge
part. Now, till the point of time I considered LLM or a particular model, I only used to talk about
evaluation, evaluation in itself that we will evaluate the part, we will do the evaluation, we'll
get a response either as a number or yes or no kind of a thing. Now, when I considered agent, I'm
not only going to consider evaluation, I'm also going to consider observability. So like agent
evaluation with observability is what we are going to try to achieve. But before that, we'll just
understand the concept of LLM as a judge. So the idea is to use another LLM to evaluate the output
and with this we can identify multiple things

### [45:35]

like correctness, completeness, relevance, groundedness. So like we can write some prompts, we can
make in some strict checks and then we can say that given the question and answer, read the answer
and correctness from one to five. Now this, what it does it with this, the judge LLM can evaluate
multiple things like as I just mentioned, correctness, completeness and this kind of methods are
already available as in different libraries already we have like the OpenA have their own evaluation
suite onto the OpenA platform from which like once you have OpenA model, fine tune on your data or
the OpenA's base model itself, you can test by uploading some Excel sheet and run their own
evaluation suite matrices available there. Or if you want to do some code, you want to try out some
custom methods, you have libraries like dpval, truelens, you can test it out where you can use their
own matrices like for example, truelens has something like ground, truth, alignment, score. Like
let's say if you're a test bench that this is the input and this is the output you're extracting
from the agent, you can use a method like truelens, it uses a combination of old traditional NLP
matrices like blue score, words score, all of them along with the LLM as a judge parameter and they
give a weighted output based on all of these scores together. So methods like this exist and along
with it there does exist methods like dpval, gval method and a lot of different other scores are
also available. So this allows for flexible evaluation of complex outputs which we receive from the
agents. Now, when I talk about observability for the agents, so the point would be observability
means capturing internal system behavior

### [47:36]

and evaluation without observability for agents would seem to be impossible and we must capture
things like user input, intermediate reasoning that happens for all the nodes in the workflow, the
tool calls happening, tool outputs, latency, token usage, error, trace locks, everything we can
consider adding into a part of an observability exercise and without this data we may not be able to
debug failures. Now, let's say, for example, the user is receiving the wrong answer. Now in terms of
LLM, I would know that, okay, LLM is not fine tuned for this domain, so LLM cannot answer, we got to
know. But in terms of agent, we don't know what node something went wrong, like for a rag pipeline,
did the retrieval went wrong? Was the prompt complex enough for the LLM to operate on? Was the agent
made a wrong tool call? So all of these things we can only know when we have an observability
pipeline and having this pipeline will reveal all the root causes of different sorts of error that
are happening and your testing would become more easier or you will be able to make your agents more
debuggable when you add an observability pipeline. So standard observability architecture would be,
you would have an agent running, like you have a UAT system or evaluation set, like where you're
testing it internally. You run the agent, you trace, log all the internal settings, internal
parameters are there. Then you extract the matrices, meaning here, at this point, for any particular
node, you define, let's say, you define a blue score because you're expecting one particular
response from the particular node. That might be a fixed response, so you use something like blue
score. So all of this for particular different nodes, there would be multiple matrices. So what
matrices to use, where and where you can define, and then you do an evaluation and then you can put
all of that together

### [49:37]

on a monitoring dashboard. So like it shows all the things, latency, for a particular input-output
pair, what was the alignment score, what was the BERT score, everything together on a monitoring
dashboard, meaning on a dashboard, you can see observability score along with the evaluation
matrices for the agent's results. So this is how the overall observability architecture would be
defined. Now, just to talk a few things in terms of production lifecycle. So for a production AI
system, you would like to have an offline evaluation, meaning that whenever a user is using, you are
having an evaluation running at the backend. Online monitoring, meaning whenever the user does
something, you monitor all the traces. You can also have some human feedback. In case you take
feedback from the user, what the responses are correct, you can keep collecting it and improve the
system over time. Then next few other things you can do around here is regression testing, drift
testing, these are all things. Once you have in your system, you would be able to identify why some
model fails or when it is the time to improve or change the model's prompts and everything. Based on
all of this, you can have a continuous improvement pipeline. So overall pipeline now will look like
your dataset, you evaluate the particular model, you deploy, you monitor, and when and when
required, you retrain the overall pipeline and this pipeline will continue in the loop till either
you achieve a good set of results or you can let's say, like your agent is running 80 percent fine.
As you receive more data in the future based on human feedbacks and all of these combinations
together, you can improve the agent for the future. Then you can go ahead further improve the
particular overall system. So that is how in actual productions, the systems keep updating, keep
improving. That is how you should also ideally follow the cases where you may not

### [51:41]

have enough data to create an agent or create a LLM. You can take use of this approach, like you
create something, evaluate, deploy, collect all sorts of extra data you can collect and retrain the
model on top of that to improve the overall system. Now, we'll have a code walkthrough where we
would see LLM as a judge in action. The idea would be to see the two libraries which I mentioned,
TrueLensDB well and along with it, how observability can be added in together. So we will try to see
all of these things together. So let me go back. First, I will open up the TrueLens part. So here,
ideal case, you would need a few libraries here with respect to TrueLens. What I'm having is BERT
score evaluate OpenAI I'm already having. The main libraries would be TrueLens, TrueLens providers
OpenAPI and OpenAI library in itself, meaning TrueLens will give us the access to all the TrueLens
components, and TrueLens provider OpenAI will act as an integration between TrueLens and the OpenAI.
Once I have both of this, what you need to do is you can take a look at this code file. We are going
to import all of these things together. TrueLens will import this TrueSession metric, will import
OpenAI from TrueLens as TrueOpenAI, will import an app, and we'll also import this ground press
agreement that we are going to use as dot feedback. Now, what are these different imports right now
we made? We'll just have intuition over that. Now, once you have this,

### [53:41]

what you will need to do is first thing is check if the OpenAI is existing into your environment,
generate a client, and once this is done, the next thing better you would need to do is you need to
define session equal to TrueSession. Now, what this does is it starts a TrueLens session that
creates a basic database for you. It will be like by default a SQLite default database. It will
generate all of these things together. You will have some multiple apps and everything. So whatever
runs you make with this TrueLens session or in this particular session, it is going to capture all
the results, matrices, or values that were generated. Now here, I'm just going to define a normal
test function, QA app, and I am going to give a simple prompt, factual assistant answer the question
in one concise sentence. We are just going to use this QA app function. Then we are defining a
golden set. So here what we are doing is now we are giving a scenario, we are giving a query, we are
giving an expected response. So we are asked, we have given a few simple questions and a few simple
expected responses. Then like in the golden set, I have particularly defined different sets of
values. Now here, we are also going to compare this result generated by LLM against the traditional
score. So in the golden set where you will have a look at the code, you will find different types of
scenarios with different types. So this would be exact match, meaning the idea would be to provide a
short canonical answers. And here in this case, the traditional matrix will receive a higher score.
The type two would be semantically correct, lexically different. Here what we'll see is blue score
drops, but will still stay high. Different results from rock score. And the LLM messages concept
would start coming into the picture

### [55:41]

that when we have semantically correct, but lexically different responses from models, the LLM as a
concept would have a higher results that we're going to get. Then something like partially correct
responses where the output is partially correct, but will not 100% correct in this cases, even BERT
starts failing, gives low agreements, scores and all. So all of these different types of responses
would be appearing here. You can check for it. Then what now Trulence actually accepts is it
requires a golden set that has a query and expected response. And then what you need to define is we
need to define a feedback provider. So this feedback provider, we are going to use true open A,
meaning we'll be going to use an open A model to give us a feedback on our query and expected
response by running the QA app which we have defined. So now what we need to do is this particular
feedback provider will pass in this ground truth agreement function inside, like which we imported
from Trulence as a feedback. So now what this ground truth agreement. Now there is not much
information available on this, but when you will go and check this particular function onto Trulence
GitHub, it makes use of traditional matrices like blue, ROG and all combined with a prompt, like
they have a prompt that says that these are all the scores available, match all of these scores
together and understand the user's input, the output generated and match all of this together to
identify the final response. So this how the ground truth agreement was defined. And then we are
just using this particular method where we define a metric. Now this is all particular fixed syntax
that is provided by the Trulence as a library. Here we'll pass our ground truth, like implementation
would be ground truth

### [57:42]

that agreement score the final score that is what we require as output. And when I do this dot input
output meaning it is going to use a combination of input and output both to generate this particular
ground truth agreement score. Then I'm just defining BERT, BLU, ROG just for our reference that this
course versus how the ground truth agreement score works. Then what we need to define is we need to
define a true app where we wrap our run function, the QA app, the Python function, which we defined
to call the LLM. Along with it, we pass our matrices. So all the matrices were defined here, ground
truth agreement, BERT, BLU. And then what I need to do is this particular true app which I defined,
I need to write a for loop stating that with true app as recording. And that here inside it, I need
to loop over the golden set and whatever query I have, I need to just call it answer true app dot
app and pass in the query. So what it does is it is going to generate the output and based on it, it
is going to get a score for all of these matrices. So now this is how simple as it, you can just run
it out and then you can just simply export a leaderboard like session dot get leaderboard and
whatever true app you are using, if you just put true app dot app ID for that particular true app,
it is going to give you the final leaderboard response. And you can also generate a per example,
like for each record, you can generate a score as well. So when we scroll over the golden set, we
generate a prediction and based on the prediction, we can also get a score of each particular matrix
and what I'm doing here is I'm storing all of that together in a particular row as a list of
multiple dictionaries and converting to a pandas data frame.

### [59:42]

And when it is all stored, like these are just the simple functions I've returned to just generate
an averages across all of them together and store it as a trulence mixed per example. So for
example, if I'm going to see the per example, So this was like a mixed leaderboard. Okay, I guess
this won't be much. So, yeah. So this is like different queries and predictions like the particular
inputs we're giving, like what is the chemical symbol for gold? This chemical symbol for gold is AU.
Here it is going to generate responses like the ground truth response, like the chemical, this is
the response by the model. A hexagon is six sides. So all of these things together. Now, the main
differences you will start noticing is that for this particular query, the model generated this. The
rainbow appear when sunlight is refracted, dispersed by water droplets. And these were the ground
truth response which are expected from the model. Now here you see the scores start dropping. So
like with respect to different scores, I will notice the scores are different, but the idea is as
the expected responses I give in, the LLM is producing something very near to it. I am going to see
the score ranges from 0.9 to one. But when I see the traditional matrices, you will see scores like
0.61, 0.87, 0.93, 0.59, 0.36. So you will see the LLM as a judge is producing 0.9 because it is the
meaning of the responses quite semantically similar, but the BERT as a metric is not able to capture
that. And similarly with some things like, sorry, this was the BERT score. Like it is still much
more better than compared to blue scores. And blue score you will add a lot of point, you will
identify 0.0, 0.0, 0.61, and a lot of issues you will find with the rock score also, you will
identify 0.47, 0.34, all of these things running together. So here from this, what we see is BERT
score was a more advanced metric,

### [1:01:44]

but again, further advancement on the BERT score was made using LLM as a judge in itself, where we
are using an LLM to judge another LLM itself. This is how you can run the TrueLens library. And now
what we'll do is we'll go back. We're going to go for a DP-VAL based metrics. So DP-VAL is another
library that has their own GE-VAL methodology. So we're going to talk more onto that GE-VAL, but
what usually the DP-VAL does is it gives us a lot of different metrics we can test upon. So with
respect to rags, SQL agent, or any metrics where we compare certain response against something
extracted from a particular source, we could have multiple metrics like faithfulness is the answer
grounded in the retrived context. Meaning let's say there is an agent that is getting some data from
web and generating the response for the user. So did the LLM generated the response based on the
results that were retrieved from the web? Or did the LLM then hallucinated and generated? So
faithfulness can be used as a metric there. Then contextual relevancy, meaning whatever context was
retrieved, is it relevant to the question? Does the context that was retrieved cover the ground
truth, contextual precision? So all of these things can be answered. Then LLM as a judge. So we have
this GE-VAL method. So here you can define any custom criteria judge for your particular task. Like
for this particular case, I am only defining correctness and helpfulness. And here in this case, I
am particularly defining what correctness means and what helpfulness means in like what my end goal
is.

### [1:03:45]

So like with respect to DP-VAL, how they have generated this GE-VAL function is also we are going to
see. And apart from this, they also provide things like hallucination, answer relevancy, biasness,
toxicity, like is the output from the LLM toxic or from the agent? And the latency as well. This is
all we can check. Now, similar to TrueLens, here we have also like generated a test bench with
different scenarios like ABCD, which where we are going to test like correct context,
straightforward answer. Another type is a hallucination bait, like good context, but the model added
more information. So we'll see how the things performed. Then irrelevant context, like the context
are incorrect, but we'll see how the model generated the response, conflicting or misleading
context. Like it's all of this thing combining together for DP-VAL to check upon. Then we just
simply defined a rag pipeline that also had retrieved context versus the current context. So like
agent, as we know, during the overall processes gets multiple references or multiple things taken
from APIs tools. A lot of these things to show, just to simulate that kind of an idea. I'm just
defining a rag pipeline and where in the initial test bench itself, I have given all the things like
question, ground truth, context, everything defined. So we are just trying to imitate the pipeline.
We have not actually used any pipeline here. So this all the code, you can like just see it as a
reference and how I have defined, but when you're going to add these things together into your
actual agent pipeline, you would need to only consider this code starting here. Like we are
importing all the matrices and here I'm registering all the matrices that are available in DP-VAL.
And here this is how I'm defining the GE-VAL. So what I'm doing is I'm giving a name for this
particular GE-VAL matrix that is correctness

### [1:05:48]

and I'm defining the criteria of how this particular matrix should work. Evaluation parameters is
structural output and the expected output. And if you want to read more upon this, so this is a very
defined, like Confident AI is the one who have released the DP-VAL as a framework. And this is what
it explains everything onto how the DP-VAL, sorry, GE-VAL as a particular idea is existing. So it
uses LLM as a judge with a chain of thoughts to evaluate LLM outputs based on any custom criteria we
as the users want to do. So it generates something like this, like we give them a task introduction
and evaluation criteria. It receives an input, input target and based on all of this together. So it
generates this kind of auto evaluation steps. Like they have already given some prompts into the
internal systems which generate this kind of evaluation steps like a chain of thoughts to generate a
particular score for the end user. So this is how you can make use of something like frameworks that
other libraries or other users have already created. So you can know like make use of already
defined methods. So one famous method is GE-VAL where I have defined correctness and helpfulness as
two particular matrix methods. I will register all of this as a matrices here into the set. And what
I'm going to do next is I'm just going to do a for loop, call my pipeline, we'll call like whatever
answer I get from it. And here now I have to defend this LLM test case where I will give input,
actual answer, expected output, retrieved context, what would be the context. And whenever I'm going
to run this particular evaluation set, I will also call this metric

### [1:07:48]

and this metric.measure whenever I pass this TC. So this TC will be containing all the information
like the expected output, actual output, all of this thing together, it will generate a matrix score
for me. And I'm going to append all of this score together again as a list of dictionaries. So now
again, my main point would be not to show too much of the syntax because like syntax and all, you
can learn by yourself quite easy. The main focus would be to show the final scores here now. So at
the end when all of the scores are collected together as a particular JSON file, it will be stored
here as a deep eval results.json. So we can definitely going to check it. So what I will do is I'm
just going to save it as results.json and what I can do here is I will do uvrun evaluation.py. So
just going to see how evaluation is performed here. So it is going to start like testing the open A
connectivity, open A connectivity is okay. And it has now started generating the prediction for all
the questions like what is the latency for each of the generated responses for that particular
question. And here if I come back to my results.json, how it will look like is it will contain a
particular scenario question. What was the ground truth? What was the predicted? What was the
latency for it? Now all the matrices like faithfulness, contextual relevancy, recall, precision,
every score will be there from zero to one. One meaning the response is good, zero meaning the
response is not good. So here you can see contextual recall is zero in this case. Contextual recall
path is false. Hallucination path is true. Answer relevance is true. Biasness like it does not
contain any biasness is not toxic. Correctness, you see like this correctness is based on comparison
between the expected response

### [1:09:49]

like ground truth versus the reference text. In this it says 0.98 helpfulness meaning how helpful
the response was is 0.99. So helpfulness is also passed through. So here now you can see. for each
of the particular question and answer is going to generate this course. So here you can see
contextual relevancy fields, like you can see pass field, pass field here into the terminal itself.
Because while the relevant statements like here, it is generating all the sentences, but it is like
trimming to show that into the terminal. So as you can see, for each of the question-answer pair,
how for each of the response, it can see hallucination, pass, bias, toxicity. So this is how you can
just run a dp-val test bench to identify all the responses. You can get in all the questions,
answers versus the expected response. If you already have a defined test bench defined. Otherwise,
you can define this G-val matrices without any golden set or expected test benches. You can just
simply define how the LLM fields is the response correct. In terms of the user query and based on
that, you can also have your own custom test bench without defining any actual reference set for the
model to refer to. That kind of possibilities also there. But the main idea apart from Trulence for
using dp-val would be that, you can define your own custom criteria-based LLM as a judge method,
like G-val, while Trulence provides its own ground truth alignment score, but you cannot actually
create your own LLM as a judge there. While with dp-val, you'll be able to achieve that process by
using the G-val methodology. So you can have a look at dp-val. Now, coming to the main part of the
overall process where we talked about, I'm just going to stop this part. I'll go back. We'll go to
the MLflow part.

### [1:11:56]

Now, here I've taken an idea for MLflow. MLflow for machine learning used to be an experiment
tracking library, but for LLMs, we can also use it as a tracing pipeline. Here what you can do is
I'm just imitated a Lang graph workflow, like a tool, get population, get weather, and I have simply
defined the react agent from Lang chain. How I can actually trace all of these processes is, here
one thing is by default, there is one autolog already available in MLflow, where I can do is
mlflow.langchain.autolog. So with this single end, what it does is it captures every node, every LLM
call and tool call made by the Lang chain library. So we can do is as simple as that, it does all
the things by itself. That is one possibility. The other thing is we can also define a span. So what
span does is we can define our custom items apart from the by-default logins that the Lang chain
will do. So we can define things like as span using this, the mlflow.gif.startSpan function. Inside
it, we can define span.setInput, setOutput, setAttributes. So these are the three main things we can
add in span, and this will also be logged along with whatever Lang chain by default used to log. So
we can have an automatic login, a logging by the MLflow itself. If we want to add something more as
a custom item apart from whatever Lang chain used to us as by default items, we can use span as a
part of it. So here we have given length gate and safety check, both of them together. So if
something like dangerous, illegal, or harmful words appear, we'll say that, no, this particular
doesn't

### [1:14:00]

cross the safety check. The length, like we were saying that, is the particular response within a
word count limit of 200. So these are all the different spans I have added. And then this is the
simple Langraph agent I have created kind of as a workflow. Checks does all the post processes. And
against these three queries, I'm going to run. So what you can simply do is one thing. Before
actually running these files, what I will need to do is I will need to run this MLflow query. So now
I can do is I will need to write this MLflow server host at this particular host. It is running on
port 8080. So it is going to start an MLflow server at this particular local host at port 8080. So
what my ideal use case would be. So it has started, and I would need to remove this docs part. So
this is the kind of UI I would be able to see. Now, inside this experiment section, I would be able
to see all of the logins that has already been done. So now if I go back here, and if I do UV run
tracing.py. So when I do tracing.py, what it is going to do is it is going to run for all of these
queries, the particular agent I have defined, and it would autolog all the values. So if I go back
here, so here how you can find at what particular location is the MLflow storing is whenever I'm
going to start the experiment, I would say MLflow.set experiment demo tracing. And here instead, I
would need to find demo tracing. I will go here and demo tracing. Here you can see I have three
traces. Here it captures latency for all the three queries.

### [1:16:00]

It is going to show the number of tokens used. Total 1,000 tokens are used. How many tokens per
trace? So 360 average per trace is used. And if I click on Traces, I will find. So I guess it has
already started running. So I guess we would now have five or six traces, you can see. It shows by
date how many traces I had. I will go back to Traces. I will do, let's say, the last 24 hours. I can
filter it out. So these are the three questions. So let's say I click on this. What's the weather in
Equia Mumbai? So this is, you can see the input. What's the weather in Equia Mumbai? Now here you
can see OpenChat, OpenAI was called. How many tokens were used? Then get weather. So this particular
tool was used. So the input was Mumbai. The output it gave was this particular tool ID, name of the
call, tool ID call. Again, then get Equia was called. Chat OpenAI was called. And after all of this
thing, process was done. And safety check was done. So it's safe, true. Length check was done.
Within limit is true. So this is how all the internal processes, like as I mentioned, we added the
spans. So the spans were registered. Now here you can see here. This has a safety check length gate
here. If I had not added them as a span, they would not have captured this particular workflow. So
this is how you can capture extra utilities outside of it. And here you can see how many tokens were
used, execution time, request time, everything here added together. So this is all the trace ID you
can check. And here if you click on details and timeline, for each of the timeline, it will show
everything. Any attributes are even, like these are like more advanced functions. We might see them
later. But for now you can check on like this, how it captures all of these things together. Now,
okay, the evaluation run would be in the other file.

### [1:18:02]

So other possibility with MLflow is that you can use by default MLflow evaluation pipelines itself.
That MLflow flow, it's like answer correctness, faithfulness as a matrix itself in its own set. So
we can have our own, what I can say, agent. And inside it, I can also log the evaluation flow, like
I can create a evaluation data set. We have added a few of the function, like one of the matrix is
keyword coverage matrix, like this is a custom matrix I'm defining. Now, inside this custom matrix,
you can add in TrueLens, dpVal, that is also absolutely fine. So inside my MLflow pipeline itself,
you can add the dpVal function so that it gets registered as a custom function in the MLflow. And
you will be able to integrate dpVal or TrueLens further into the MLflow pipeline. Here, what we have
defined is, we have simply defined a keyword coverage function that just checks the overall keyword,
how is the keyword coverage. And then I can define custom LLM as a judge, definition is also
possible. So low concise, concise, high, like input, output, like this is all the things I can
define, make generic matrix, name, conciseness, definition of this is measure whether the answer
conveys the key facts without padding or repetition. And I can give a grading score, like the score
from zero to one, I'm providing a model GPT 4.1 mini. And along with it, I'm providing two examples
of it, like concise low and concise high, where I can say what is the input, what is the output,
what is the score and justification for it. So now this particular custom LLM as a judge matrix
would also able to understand how to do this grading depending on the examples I've given. and all
of these things combined together could be used.

### [1:20:04]

Like this would be ran as a part of a evaluation run whenever we are going to run this pipeline.
Next, what we'll do is we'll do is with mlflow.startrun, we'll give a run name tracing plus eval,
and inside this we'll invoke our graph, and we'll also going to log all of these matrices like mean,
latency, and once we receive all the results from this graph.invoke meaning at this particular point
of time, but tracing like the previous notebook where we saw, all the tracing was done. Once this
all tracing is done, we'll need to use mlflow.evaluate, pass in our evaluation data, pass in all the
matrices we have defined, like the faithfulness, concise matrix, everything together, and then once
you do this, what it is going to do is all the matrices, the default matrices in mlflow versus all
the extra custom matrices you're defined in mlflow. All of these things would be ran under the
evaluation batch, and then I simply use the print functions to print all the outputs here. But
instead of that, what we can simply do is I can go here, I can go here at this part demo tracing
plus eval. There you can see eight traces I have defined. Again, it shows all the latency, token
usage, everything. If I go to traces, it is going to show me everything like messages, shows the
overall trace, all the checks, how the model was called, response was generated, everything. But
instead of this now, I will also be able to go and check this evaluation runs. If I go on this, you
see, I had these four queries. Let me go back. Once I click on this chart,

### [1:22:05]

here you will see what is the values for toxicity. I guess it should also show it here. Just a
minute. I guess there is some limitation to it. Not really sure. Fine. What would happen usually
around here is, for most particular chart, just a minute. Yeah. Whenever, got it. This is where I
can filter it out. Yeah. This is it. Here you can see the particular run name, whatever data set it
might have created, and all the scores it can show it, meaning answer correctness value,
faithfulness value, all the concise functions that I have defined, so what was the concise mean that
was 2.57, meaning across all the eight queries that I gave, where my concise score would be in the
range of 0 to 3, my average concise mean is 2.75 and the variance is, 0.18, meaning it is varying by
pointed for different items, and when I click on this, I guess here I would be able to have a better
score for each, for example, just a minute. That is only showing the trace. In that case, it should
also show it for everything, just a minute. Okay. Got it.

### [1:24:13]

So this was the overview, and in the artifacts part, yeah, Gen A custom matrix. So here I can see
all the definitions of the artifacts. Just give me a second. I need to find. So I guess what we'll
do is we will, I will have this checked where I can produce per row output, and we'll update that as
a part of the next session, but yeah, for now, what we're getting here is, I guess there was a
mistake here when we calculated the final result set. So what happened is when we stored all of the
results together, we just stored the overall average values for each of the results. So whenever I
did MLflow evaluate, what it simply did was it only saved the average value around it and did not
store it for each exam. So what we'll need to do is we'll need to write a custom function to store
the particular value for each of the example. So what I will do next is I will add one more code
file to this whenever you are going to receive the recording of the file, and in that extra code
file, you can run it. So what you will get is for each of the row into the input, you will be able
to get a particular score for each of the rows, and this by default values, you can anyway use it.

### [1:26:17]

So you are going to get average score and row by row score, both would be possible there. So either
I'm going to share a notebook, and if required in the next session before the main topic of the next
session, I can simply explain the particular file if required, if anyone has any doubt, but
otherwise, you can have a look at the particular file. So now I will come back to the main
presentation. So like, yeah, that was overall part of the code walkthrough, like TrueLens, dpVal as
true metric file, and MLflow as a particular observability file where either we can trace out
everything, all the LLM calls. Another one would be where apart from tracing, we can add an
evaluation pipeline along with the MLflow itself where we can attach our custom functions as well,
maybe we can add the integration of TrueLens dpVal with MLflow, that is also a possibility, or we
can write an LLM as a judge in the MLflow itself, but my point would be that dpVal has their own
custom framework for LLM as a judge, which is far more better than MLflow's module. So using dpVal
for LLM as a judge would be much better to do it. Okay, yeah, now when it terms in terms of
practical evaluation strategy and recommended approach would be to use all of this together, like
each method captures different aspect of the system behavior, so a better would be to use them
together because the together will be able to provide a complete evaluation framework. So idea would
be to combine all of this, like a reference matrix, LLM as a judge, certain kind of an agent matrix,
like defining conciseness, the faithful relevance, faithfulness, answer relevancy, which we defined.
The heuristic rules could be some rules that you want to do.

### [1:28:17]

We can also have some human review, meaning if the agent generates the responses, and there would be
some humans who would be able to give that the LLM or agent generated the correct response, and we
can feedback that together as a fine-tuning approach for the model or the agent, and that all of
these things approach combined together will form a more better practical evaluation strategy. And
this particular image will provide as a separate image into the codefiles itself. So this shows all
the post-evaluation actions we can take for LLM optimization, what architectural changes we can do,
what we can do at level of prompt engineering, what we can change at the tool and action layer, like
when we want to improve tool usage, like if something at the tool level fails, maybe we can add
better argument schema validation, what you can improve at the rack knowledge-based level, how you
can improve the operations part of the agent, like add retry recovery logic, add human in the loop,
optimize for cost and latency, improve context window management, and how to ensure quality. So all
of these things you can take as a part of post-evaluation actions. You can have a look at the
overall image, have any questions, you can drop it as a part of your Slack question, anything is
fine. I would be able to help you out, like otherwise this whole image would itself take another 15,
20 minutes or half an hour to discuss. So... Key takers from the session would be that agent
evaluation is fundamentally different from the traditional model evaluation. Not only agent
evaluation, but even the LLM evaluation is quite different from the traditional ML evaluation. Agent
introduces multiple failure points and evaluation across these multiple dimensions

### [1:30:17]

is necessary. And this particular necessity can be facilitated by adding an observability layer.
Agent evaluation at the end, the best strategy would be to use a hybrid strategy that is combining
older methods, newer LLM as a judge method, along with human in the loop, heuristic rules,
everything combined together. And evaluation at the end enables a continuous improvement of the
agent systems and production like the two main goals of the session, like agent evaluation and
observability when we talk about evaluation. Evaluation will allow continuous improvement of the
system and to do continuous improvement of the system will require continuous monitoring, which can
be facilitated by observability. Like the end goal for a production agent system should be you can
add an evaluation pipeline as well as an observability pipeline. So yeah, this was the main concepts
that we wanted to introduce you all this like we as we already saw different agent architectures,
definitions, how we created a few projects around them, planner, executor patterns and a lot of
things. So like we are now moving a little towards the deployment part, but before that, a few of
the LLM Ops things where we talk about monitoring, observability, evaluation parts before the final
production phase. So yeah, that was it from the session. I will just open the mic for all of you so
you can ask any questions if you have. Just give me a second.

### [1:32:33]

So I hope everyone might be able to unmute themselves and if they have any queries, yeah surely you
can go ahead and ask any questions you like. There are one question. Yeah, yeah, Mayur. So in the
entire pipeline integration that you mentioned, this will run in the in the initial pipeline in the
lower environment or it can run also in the production room? What is the standard practice? Standard
practice would only be to run this in dev environment. You can have an observability feature where
it traces the tokens and everything together like what is the average time the agent generates the
response and everything, but the evaluation pipeline is only meant to be run in the UAT or the
testing phase. So in that ideal case, you should not be storing the user's input and everything,
right? So observability pipeline can be set up in both dev environment, production environment,
while evaluation pipeline is essentially only to be used until you put your final system into
production. Absolutely. Some of the libraries that you mentioned would be part of the agent or they
are separate because for ML of size, so it's a separate UI with separate server component. In terms
of architecture, how this would fit together? So here also, these libraries, these dashboards will
also be different from the overall agent architecture itself. Like it will be like a plug and play,
you will have your own agent architecture. Then you can pick a library, you can change it, like
let's say after three months, you get a better option, you can change the evaluation strategy. So
ideal case, it should be overall separate, independent of your overall agent architecture, but yeah,
evaluation would be a part of it.

### [1:34:33]

My question is this MLOps UI that you showed is a separate component of the agent, right? Not
running on the agent. No, it's not part of the agent. It's not part of the agent architecture. It's
separate from the agent. So it's like the agent is feeding the MLOps server, which is running and
storing entire. So it's kind of how they talk to each other, agent and MLOps server, they use some
kind of REST API? No, no, no. So AI agent is there, we're using MLflow as a library, like there is
simple things we can add. Like we can just add some code there into the main agent architecture or
the API architecture, which we have defined for our agent and just a few lines of additions via the
MLflow code line. The MLflow will be able to trace everything into the agent, that the UI is
separate, independent of the agent, but there will be an integration level, integration at the code
level. This is how they will be integrated via RESTful API, how this event is sent to the ML. So
when this particular line in MLflow, there is this line exists where we say MLflow.autolog.agent. So
it's kind of working as a decorator. So every point where Langchain as a library is used, the
Langchain shares its event results with MLflow and MLflow stores it in their own database. But in
the end, it's not using any sort of API calls or something like that.

### [1:36:38]

It's not totally necessary to use MLflow only. You can design your own setup to store the results as
well. That is also fine. Like MLflow just gives an abstract way to all of these things together, is
easy to use open source as well. So a lot of people prefer MLflow or something like it's in biases
where you can simply plug and play that pipeline to the main agent architecture. So maybe if you can
cover maybe in the next topic of deployment of how this entire library and server and agent
architecture and integration would work together, that would be really nice. Yeah. Sure. Sure. Sure.
I will note it down. Hi Chirag. I have one question on eval. So is it an offline library? How does
it work? It uses LLM to evaluate, right? So is it offline or how is it? So it uses OpenEA as its by
default LLM. But if you want, you can use other LLMs from OLAM or LM Studio and connect them as
well.

### [1:38:42]

That is also a possibility. Oh, okay. So in our example, we configured it as OpenEA. One follow up.
What if the same LLMs are used for processing as well as evaluation? It won't be a good idea, right?
Just thinking. No, no, no. So depends, let's say for example, for evaluation and mini or nano model
can also be used because during the evaluation phase, our ideal idea would be, for example, if I
take an example from the agent architecture as well, when we want to do some action, we want some
LLM to take an action, we usually use a reasoning model, like for example, GPT 5.2 or GPT 4.1, the
bigger model. But when we use something like router nodes or a functions which require... just
little action from the LLM, like not some major action. Ideal thing would be to use a GPT 4.1 nano
mini models because it will give you a benefit of that it saves certain amount of cost, it uses less
tokens, and it will be able to do inference more quickly compared to bigger models. So like you get
two benefits, inference speed is higher, cost is less, but in case those models are not performing
well,

### [1:40:44]

you can maybe have a check out with some larger model, but ideal would be to use a different model
and a non-reasoning model during the evaluation phase. Understood, thank you. In the overall
ecosystem, if I have three different model and I want to see which one performs best in a particular
use case that I have, so which library would be ideally useful here? So how you want to test it?
Let's say if I have a use case and I want to see which out of three model performs best and compare
them and then decide which model I should go into current production, right? Which particular model
you should put in production? Yeah, I have a use case. For that use case, whether Llama performs
better or Cloud A model performs better, right? So in terms of all the various parameters. So how
can I evaluate that different model performing compared to each other? Understood. So idea would be
that we, I showed you that MLflow UI, right? So either you can use something like that, or you can
just simply, like let's say you're using BP well as a library to evaluate the, let's say factual
correctness of the model's responses. Let's say you have three models, you give 10 same inputs to
each of the model, you capture all of the model responses,

### [1:42:45]

run the evaluation using BP well for all of those three models, store it either as a JSON or CSV
file, and then you can use some dashboard, you can write some stimulate code check, what model
performs best. Like you can make a choice from there. Okay, so BP well library will come in here,
right? That's what I meant. Correct, correct. It would be quick and easier to use here. Okay. I
think playground also can be used for quick comparison, right? Isn't it? Which one? Playground. Open
AI playground. Open AI or anything on the cloud, which offers multiple LLMs comparison. In that
case, maybe open router is a website which can allow you to use any model from any provider, but
let's say if you are only going to work, like let's say with one particular, let's say open AI,
right? In that case, if you have access to open AI playground, that is great. In case you want to
use models from multiple providers but you don't have access to tools like open router or something,
then I guess you would need to write custom code. But otherwise, yeah, definitely. You can use
providers like open router and all, but once you use those playground based mechanisms, you would
need to know, like maybe copy paste all of these things together. And the other thing or other issue
would be, let's say my problem was to use a LLM. Now let's say if you had an agent, right? How you
can put that particular agent into playground would be another issue.

### [1:44:46]

So I guess you would need to, like if you're going to use plain LLM, then playground is fine, but
when you have agent, you would need to add in some code there. Understood. I mean, it is Azure
Playground. So wherein we get access to all LLMs available in the market. That is correct. What I
meant was, let's say you wrote a code with, let's say- Yeah, I got that one. You got that, right?
Yeah. Okay, fine. Understood. No, no, I also understood your idea about playground. That's also,
yeah. That's also a good idea to do it. Any more questions? Okay, I will stop the recording.

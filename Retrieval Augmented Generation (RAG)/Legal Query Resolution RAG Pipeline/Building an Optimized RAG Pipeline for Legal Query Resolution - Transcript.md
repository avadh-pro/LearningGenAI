# Building an Optimized RAG Pipeline for Legal Query Resolution — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy), Week 3: RAG —
> [Building an Optimized RAG Pipeline for Legal Query Resolution](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76791263-building-an-optimized-rag-pipeline-for-legal-query-resolution)
> · Live hands-on session recording, 133 min (`2:13:06`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> fourteen silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated from a live screen-shared coding session. Prose
> explanation transcribes well; **code identifiers do not** — package names, method names and
> variable names are frequently mangled, and stretches where the instructor is typing in silence
> produce no text. Treat code references here as pointers to look up, never as something to copy.

---

### [0:18]

So yes, hi, everyone. Welcome to today's session on building the RAG solution for a particular
problem use case that we have picked up as the legal query resolution. OK, so just taking up a few
of the basics of RAG right now, just so that going forward into the session, we are all clear with
the basic terminologies with RAG. So just first of all, understanding the system in terms of RAG,
usually a query would be asked with respect to the difference between the fine tuning or the LLM
workflows. They both, let's say, for example, LLM workflow. LLM work is something where the users
send or from a particular system, a query gets sent in, and the system acts on top of that to
fulfill a particular task. That is what the LLM workflow would be. What is opposite to that with
respect to LLM fine tuning, usually whenever we identify cases where our model does not understand
the terminologies, the domain knowledge, anything associated with the particular domain that we're
working on. For example, we took a few examples previous week, like healthcare, finance, insurance-
based, different types of particular specific domains where each and every organization has a chance
of having their own separate document styles, variety of terminologies, everything associated. In
those cases, we try to fine tune our models. But in cases where you have frequently changing data,

### [2:20]

and let's say you fine tuned your model once, based on your documents, based on your terminologies,
whatever domain you're working on. But then you have a case where technically you have a
continuously updating knowledge base. Users might be asking queries, and to answer the queries, you
have to depend on new documents, like Word documents, PDF documents, databases, explicit things. And
to keep up with that continuously updating knowledge, or maybe after a few months of gap, certain
level of knowledge changes or something, that is what you're targeting at. So in those cases,
repeatedly fine tuning the model again and again could be a very difficult task. Like, it's also not
efficient in terms of the time you spend on to preparing the new data set, like having
infrastructure or GPU usage, that budget goes in separately. You fine tune the model, the whole
cycle goes through. You evaluate the model. If the model does not turn out good, how do you make
changes to your data set, evaluation changes, there would be some manual human level evaluation
setups, everything. So continuously fine tuning models for your continuously updating data could be
a very not so efficient task. So what we came up with a task like RAG. So what the idea is LLM will
stay at its place, fine tuned, not fine tuned, whatever. The user can ask a query, then the LLM,

### [4:20]

what it will do is as a main thinking engine of the whole system, it will try to find the sources
from an external database. Now here, there are two different types of models used in RAG. I will
just name them right now, we'll explain them later. So first is the main LLM, that is the thinking
engine. Other one is the embedding model, embedding model that will help us find these trusted
sources and pass the information to LLM. And LLM will be the one that is going to generate the final
answer for our use case. And there could be other different types of models, usage and everything
also, they're like, you know, re-ranking models, hybrid models and everything, all included to
generate the final solution with respect to RAG. Now, one thing going forward before into the
session, like I would like to highlight is if you all would have gone through the material of week
three, you might have noticed that a few of the sessions, like one of the sessions which we have
conducted in the past was on current state of RAG. If you would have kind of have gone through that
session, you might know that there is no particular RAG method that serves with guaranteed accuracy.
Like if you're eyeing that for any of my use case, I'm going to apply RAG, I'm going to get 80, 90,
90% accuracy, will solve my customer's problem, make sure that things, if we're going to look at
that way, then majority of the times, RAG is something that will, not easily also going to work out.
So RAG is also something which have its own share of failures. Most of the times, if you go around,
just go and search on Google, like RAG solutions, accuracy or something, you'll find lots of people
complaining that RAG

### [6:21]

in the systems has an suboptimal accuracy, like 50%, 60% overall in general. So in case of very
complex data, RAG is still something that is lagging behind, we do not have any state of the art
mechanism or a guaranteed RAG structure that will guarantee that RAG is going to give you accuracy.
So RAG still now, it's into like, each and every part of RAG is experimental. Like you can't commit
a result until and until you have developed the pipeline, tested it. Before that, if you say, my RAG
is going to get 80%, that could be an absolute wrong statement, okay. And even, and so I also do not
claim any sort of accuracy, that is also, please note that here. So now what we'll try to do is,
like we'll just understand the problem statement and we'll go ahead with understanding how the
architecture we have defined, okay. So starting with this point, like what is our particular kind of
data? So we have picked a data set that was available onto Hugging Face as open source data, where
like you can think is a majority of all over Indian laws data, like Aadhaar Act, Administrative Act,
and all those acts are present in the data set. There are an approximate 27,000 different acts of
data available. And in that like the main points that, how that data is defined is like, it has a
very high metadata collision, meaning the section numbers for each of the law

### [8:22]

or act is not different. Like for a same act, there are multiple sections, multiple sub rows,
multiple amounts of data available because the data itself is divided onto many levels of paragraphs
and a lot of different points. Then the second part is, it is also deeply nested document structure,
meaning like as I was mentioning, one act, multiple chapters, multiple section, multiple subclause,
each and everything, all the divisions, they're being provided in the data set. That also causes a
problem when we are going to do a normal chunking of the overall rack setup. Like if I was just
going to go and just put all the data into the vector database in a single point, there is a very
high chance that we'll never be able to identify good data or like good retrieval from the vector
database that is to be provided to the LLM. So that is how, again, a lot of issues can arise during
the retrieval due to this kind of a document structure. Third, the multi-turn query resolutions. So
this is not just a problem with this particular use case, but this will be a problem with any of the
majority of it use cases you do anywhere when you have a conversational type of agent setup. So
follow-up questions, like this is a very known pattern that users, when they ask a query, for
example, let's say user asks, what are the provisions under section six? It is widely noticeable
fact that the next query, like whenever the user wants to ask something, they usually don't provide
full information. They just treat it like how they chat with the human, so they don't provide full
information back to the LLM or the agent. They might just give a short response or an additional
added query

### [10:23]

without mentioning are they continuing from the previous query or what. Based on that, we need to
actually create certain setups that for the previous queries that the user have asked, how do we
connect that back with the newer queries or for the newer query, how do we want to connect the
memory from previous queries so that we maintain a particular continual flow of the responses going
on. It is not that first response is on one act, the other response is on another act, and there is
a total disconnect between both the sentences. So the conversational continuity should be
maintained. So these are the few things that we'll try to solve through a few of the known methods.
So now coming to the architecture. So with respect to RAG now, now those who might have not gone
through the week three, for them, if they want to just understand RAG in simpler terms, RAG
technically means Retrieval Augmented Generation. That is like just three terminologies, R,
retrieval, A, augmented, G for generation. That is how we define it. R technically means that, like
the retrieval part, that whatever data we have, documents or could be like PDF files, Word files,
.md files, text files, HTML pages, any kind of information, we store that in a database. That
database is what particularly we call it, vector database, because when we store this data all
together into a vector database, they are going to go through a process of chunking and embedding.
So if we look at the first step here, what happens is, let's say I have this data in a CSV format,
Excel format, I'm just going to load clean and validate this data,

### [12:24]

like I'm just going to drop any sort of empty rows in the data, any data points where there is so
much patterned text, or if there is any missing or anything is like that, I'm just going to drop
those kinds of data. Then once I particularly validate that all the data, all the acts and the
subtraction, every information exists in the database, I will go ahead with chunking. Now, chunking
is a strategy where we split our text into short chunks. So why do we need to do chunks is, like
there are multiple reasons with it. One is that an LLM cannot have an infinite token window when it
is processing. So it might have a particular token limit under which it needs to process the input
context and the output. So in that case, like during that particular process, let's say in the input
itself, so like as we know from the Rags, idea is that LLM is going to receive information from an
external source that is VectorDB. Now, when LLM receives it, if we pass so much of information, LLM
will not have any more token window to generate the output. So we chunk out the text based on the
LLM's token window length, and let's say we create chunks of size 2000 tokens, 4000 tokens, 8000
tokens or so, and based on the small chunks, we create embeddings. Now, embeddings is what is going
to convert these tokens into numerical vectors, like chunks were still like text pieces, pieces of
text, but when you apply embeddings, they get converted into numbers, particularly called as vector
embeddings. And here we are going to have two types of embeddings.

### [14:25]

One is dense embedding and one is sparse embeddings. So the difference between the two is that the
dense embeddings is something like created with models that are based on transformers. So like going
back to the previous two sessions, it would be much more like the transformers architecture that you
understood and during the data conversion processes. What happens is the tokens get converted to
numbers and that in the transformer architectures, the self-attention mechanism kicks in. It tries
to identify the semantic similarity between the different words and data points. Similar pattern
like that, this dense embeddings also perform the same thing. So there are different types of
models. One is the kind of from OpenAI, Google, all this kind of, they provide embedding models. Or
you can also use open source embedding models from Hugging Face, Olama, those kinds of services.
Now, these embedding models are a perfect example of what we learned about encoder-only transformer
models in the session one that we looked at. So this encoder-only transformer model, they just try
to understand the relation between the data points, the different types of words and sentences that
is available in the data. That is what dense embeddings would be. Sparse embeddings is more like
derived from the BM-25 algorithm, which is more focusing towards the keyword-based search
algorithms. So usually why we like earlier rag solutions used to only have dense embeddings. It was
believed that vector embeddings as a solution, as they understand the meaning between words,
sentences and all, so they might perform better. But generally, over time, what people noticed is,

### [16:25]

when we have some complex data, in that complex data, if the vector embeddings model does not
understand the terms, terminologies, the kind of, I would say, let's say, for example, in
healthcare, that could be different words for medicines, different major body organs and everything.
If the model is not trained to understand those kind of things, what happens is despite having a
good accuracy over general data, the vector embeddings model might still fail, the dense embeddings
model. So as a combination, they started adding the BM-25 algorithm that came out as a sparse
embedding. So what it does is, so our idea would be that we create vector embedding, we create dense
embeddings, two embeddings, one embeddings, try to understand how the data is connected or when a
user asks a query based on the user's query, what kind of data is there, which we can fetch from my
vector database. That is one thing. The BM-25, the sparse embedding model, that will guide the
system to fetch what is relevant with respect to the input, like the keywords that are there in the
input. So for example, let's say I'm taking from a healthcare perspective. Let's say there is a
model that does not understand something like glycosylated hemoglobin. So let's say I as a user ask
the query, what is glycosylated hemoglobin? So in this case, let's say the dense embeddings
retrieved from the vector store a lot of different things, like hemoglobin, glucose, diabetes, XYZ,
but it did not fetch information for glycosylated hemoglobin because it could not understand or it
could not form the relation between that particular term, glycosylated hemoglobin,

### [18:26]

with any of the data that is there inside my vector database. So there comes the BM-25 or the sparse
embeddings model which tries to match the data into the vector store based on the keywords. So it
will particularly identify that there is a keyword, glycosylated hemoglobin in the user's query, and
will try to fetch the data based on that. So when we have these two things, two different types of
embedding models, we get the best of both the worlds, the keyword search and the semantic search. So
we merge both of them together and fetch top three, top five results from both of them, combine
together, and then pass it to the LLM as a context to generate the response for the user. So this is
the whole part on how we load the data, like whatever you need to pre-process on the top of the
data. You just create small chunks from the data. If the data is too large, if the data is too
small, you might never need to chunk the data itself. Like you can just simply pass the whole
paragraph or the whole whatever two lines, three lines of data you have, goes to the embedding
models. Two types of embedding models get applied, dense embeddings, sparse embeddings. The
embeddings get created, and we store it in a particular vector store. Here we are going to use a
vector store called as Qdrent. So Qdrent provides their own BM-25 sparse embeddings algorithm. So
using that and OpenAIS Text Embedding 3 model, we're going to store it inside the Qdrent vector
store. Now, the second part of the overall solution. Now, we just completed from the retrieval
augmented generation. We just completed the retrieval part, like we defined the vector store. Now,
the augmentation part. Augmentation part is something simple. Whenever a user query comes in, so we
do a hybrid retrieval from the queued rent.

### [20:27]

What happens here is technically, the user query is first converted to embeddings, like embedding
models are applied on top of user query, and it fetches the information from the vector store, and
that information is considered as a context for the LLM. So that is what is augmented, meaning we
augment the new context into the system. So that is what RA, retrieval augmented would mean, and
generation is that. This is what the system we will have a look at in terms of RAC today. So with
terms memory, what we're going to have is, let's say, as soon as the user query comes in, we load
previous history from the user's chat that will be stored inside the SQLite memory, and we would
have a rewrite query node. So rewrite query node is like using a small LLM, could be anything like
if you're using some closed source models, proprietary models could be just GPT 4.0 model, 4.1 mini
models, and in terms of open source models, could be small models like Gemma 1 billion, Lama 1
billion, 3 billion models. What the idea is that whatever new users query is, and comparing with the
previous user queries, the user has passed, and also based on the responses from the LLM, the final
responses generate, we will rewrite the query. So that query is then passed to the vector store. So
for example, let's say I'm going to take this example here. Let's say my first query is, what is
other act? Now, the LLM generates a response for me that other act is something, something xyz
things, it was released in this particular year. Then as a user, I will ask it,

### [22:27]

what is another act released in the same year? Now, if that query goes directly to the vector store,
what is there for the vector store to retrieve? Based on the query, the thing will happen is, what
was the act that was released the same year? So the vector store can give data from any act, any
year, any information, vector store will retrieve and just give it back to you. So that will be a
problem because there is now no continuation in the setup. So when we rewrite the query, what
rewrite query will do is, based on the previous memory, it will read the response of the LLM and the
user's previous query. This rewrite query node is supposed to rewrite the query into, like the
original query was, what is then another act released same year? It will rewrite this as what are
the other available acts that were released along the other act in the year, whatever year, like
2000, 2005, XYZ, it will reformulate the query. So it has now enough context to fetch correct data
from the vector store. So that is one retrieval optimization technique that we are going to add.
Then we also have decompose query. So decompose query, what it will do is, it will split into
multiple sub-questions. So there is one another fact that is noted that if we add too many multiple,
two to three different types of questions into the query itself, the vector store can or has a high
chance that, let's say, for my question, like what are the other acts released alongside other act
in particular year? So maybe it might fetch data for that particular year, it might fetch data for
the other act, but it might miss certain information or something.

### [24:27]

So when we decompose the query, what it will do is, it will maybe try to formulate two different
queries, like other act in 2022, other similar acts like other act, other similar acts with other
act released in particular year. So based on these multiple queries, we'll fetch the data from the
quidrant, like the vector store, and the quidrant will return me all the information, all the
different top K number of results for that particular each of the query that was decomposed. And
let's say I get 15 different results, I will try to apply some sort of a different, again, another
pre-retrieval optimizations. So I might add something, few methods like MMR, RRF fusion. So these
are different methods that try to identify what information might be relevant for my user query. And
if there are multiple copies, so let's say when the queries were decomposed, like three queries were
generated, two queries retrieved almost three to four chunks of same information. So when we apply
MMR, that is Maximum Marginal Relevance, it removes the duplicated chunks from the let's say out of
15, if there are four chunks that is repeating, it will remove those four irrelevant chunks or
duplicated chunks. And then finally, we do something what we call as, we call it as this post
retrieval optimization methods.

### [26:28]

So these were all pre-retrieval optimization methods, like going through all this, we finally get an
N number of chunks, then we have a re-ranking system. So what re-ranking does is re-ranking will,
based on the user query, these are kind of models that are trained to rank results according to
relevance of how much information they can generate to complete the response for the user's query.
So let's say there could be chances that the first 10 chunks, out of the first 10 chunks, Sandesh, I
will come back to your question, just wait a minute. So let's say we have 10 questions, and from
those 10 chunks, so out of those 10 chunks that we have here, let's say chunk four, chunk six were
the highest information providers, but all of these earlier methods didn't rank that chunk six or
chunk four higher into the rank. So now LLMs have a tendency to pick up the first few chunks as the
main information to generate the response. So there is a chance that the chunks that are lower into
the retrieved phase, if even they have enough information, their information might never be there
into the response generated by the LLM. So re-ranker ensures that the chunk four, six, nine, 10,
whatever is there, they all will be pushed at the top of the rank list that we have. So chunk four
goes chunk one, chunk nine might go to chunk two, chunk six might go to chunk three. And based on
that, LLM will receive relevant information

### [28:29]

first to generate the response. Then we have a few things here, like confidence threshold and
everything. Now confidence threshold is set that if the confidence is high, that information
directly goes to the context assembly, like the augmented part gets passed to the LLM. If the
confidence is low, we will have a fallback mechanism where that information goes, sorry, where a
particular web search, like Google web search, like server web search, or let's say, there are
different tools like Tevely, Bing, Brave, all those web browser, like Google search engines you can
pick up and those web search, they will retrieve relevant information from the websites and will
pass that information to the LLM to generate the response. Now all of this information will combine,
will get sent to the LLM. LLM will combine all that information, user query input, the information
from the vector store or the web search, and will generate the final response. And the final user
query and the response will get committed to the memory, so to load them as a chat memory in the
next turn. So this is how the overall flow of the retrieval, the augmentation, and the generation
phase, all three will combine together to finally form the. overall RAG architecture, R-A-G, okay.
Now, I'll just take up a question. So what is query SQL? Query is any text, right? As I've already
shown here,

### [30:29]

user query, raw query, text, it is text, it is not SQL query. We are not writing SQL here. So SQL,
if you're confusing the SQL with respect to the database here, so VectorStore, as I was mentioning,
it is going to store numbers. Now, on top of numbers, we have this embedding models that provide us
power to kind of search or match the user query that is raw text, not any SQL query or something,
like select, rank, from, all of those things won't come here. It will be like, as I was mentioning,
when I was explaining, like what is other act, those kind of things would be passed into the input,
and those embedding models will convert those inputs also into numbers, and those numbers will be
matched against the numbers that is stored into this vector database, and any relevant information
that is there, that will be fetched and passed to the LLM. So that is how the whole process goes,
but that SQL part, it is nowhere related here. How do you decide the embedding model in first place?
Would that be according to the use case? For example, in this legal use case, does the embedding
model need to be trained on legal terms or any general embedding model would work? Okay. So now with
respect to embedding models, okay. Choosing an embedding model would depend majorly, like with
respect to LLMs, you might have seen that we see that different organizations, like let's say
Google, they release lots of different models into medical field.

### [32:31]

Anthropic has released multiple models into code. Mistral has also released multiple codes into, I'm
sorry, multiple models into code spaces. So with respect to embedding models, there is not something
like organizations have released domain specific models. So majorly all the embedding models
available in the market are open source models only, the open knowledge models or something like
that, while certain organizations like OpenAI and Google, they have released their own closed source
proprietary embedding models as well. Now, to pick an embedding model, I would suggest best thing
you can do is go to hugging phase or just go to Google, search, what is the best model according to
the leaderboard or onto hugging phase, something like that. Let's say if I have to show you, right.
So let's say I go to this MTB leaderboard. Now, let's say English, right. So this is English
language. So it will just list out all the different types of models for English that there are not
top performing. So now here you can specifically choose if you want an open source model,
proprietary model, let's say go to open source model, it will list out majority of the public models
that you can just download. So GINA embeddings, the Quen 3 embeddings that were just released a few
months back. These are like some of the top good models that are out there that you can pick up
directly start using them. And you just need to test out how the retrieval things

### [34:33]

and work if in case like, you know, your system is like not performing well, then at that point, you
need to start looking at different embedding models, try to identify, that will be totally
experimental thing. Like you pick up a embedding model, test it out how the responses are there, how
is the retrieval quality, is it picking up correct chunks from the vector database, all of those
things usually goes through or is done by human manual intervention. And there would be a deal that
you can have a team who would check out like, is it correctly fetching the information? So yeah,
like human intervention would be needed at this particular point. And I guess you also passed
another question, is this architecture fix or we can change it? So architecture is not fixed. In
RAG, as I was mentioning, when I started the session, in RAG, there is no fixed method. Now, if we
have to list out now, as I was mentioning, like pre-optimization or post-retrieval optimization. So
there are a hundred methods for pre-optimization, there are hundreds of methods for post-
optimization, which there is no particular, I would say, way to identify what particular method
would work best and when do we need to change it, right? So like, as I've just mentioned, there is
no particular way to identify what thing will work in a sequential way. So at the end, everything is
experimentation, like you need to make your own research, like based on what domain you're working.
So for example, if I'm working with medical domain, okay. I might be preferring the BG embedding
models, like when I experimented for the first time

### [36:34]

with respect to Quen, Jena embedding models, BG was working better for me. So like over time, I
would have my own set of stack where I would be preferring certain models, certain technologies like
query decomposition. For example, let's say I go to an agentic rag setup, right? Where
conversational rag does not fit, right? Like it is more like a user query goes in, LLM generates the
response. There is no continuity in conversation. In those cases, query rewrite, the query
decomposition, all of these things might not matter as much as that those things matter in
conversational rag setups. Then like as you experiment with rag, as you evolve, as you identify kind
of different methods, experiment with them and finally reach a stage where you kind of figure out
that these are the things that should be there in your setup. Then what you do is you go evaluate
this kind of different things over different kind of different things. Let's say you add a new pre-
retrieval optimization, you remove a post-retrieval optimization and you keep on evaluating it until
and until now, you're satisfied with a certain level of performance or the accuracy of responses
that you get. And if we want to improve the performance, what do we do? Again, like there is no
specific answer to that. Like Arpan, did you see that session, the current state of rag? Arpan's
there. So the current state of rag session,

### [38:36]

I have discussed over 25 to 30 different rag methods in that discussed where they should be used,
where they might be helpful and failure points of majority of the rag methods, like where there is a
chances that this particular rag method will fail. So if you just go through that session, you will
have all the majority of the idea that in retrieval, what methods might be useful in generation,
what methods might be useful. But yeah, if you want to just like ask me what should be the minimum
baseline setup for a rag architecture, then in that case, a hybrid retrieval setup should be there
for sure. A re-ranker setup should be there and some sort of a memory, contextual memory should be
there. These three things should almost be there in majority of the rag architectures that you would
create. All the other things out there in the architecture, you need to play around, you need to
experiment and figure out yourself, like what would work best for your use case. Now, Aniket is
asking, does the rag support multiple data sets or knowledge basis? If yes, how is the architecture
designed to retrieve relevant information from the correct data set? Is there a separate vector
database for each data set or are they stored together with metadata filtering? Now, For this
question, this will particularly depend upon how you have designed your architecture, your system,
your overall, how many number of different LLMs are operating. So for example, you might need only
one single vector store, if LLM is going to retrieve all the important information from that,

### [40:43]

like all the knowledge around that single topic has to be stored together, we put it all together in
the same vector store. Now, let's say there is a chance that there are independent information
available to us. So inside a vector store, we have something called as collection, like as we have
MongoDB, we have the database in that we have different collections. Similar to that, if you have
independent information, we can store it all separately in different collections, and then you can
create a router-based setup that as soon as the user query comes in, that router will tell the LLM
that the user query is asking for, let's say, information source one, information source two,
information source three. And based on that, you can just design it programmatically, that at that
point, the LLM is only going to receive information from the information source once vector store
collection. So that is how, if the information is dependent, you store it in the same place. If
there are independent information stores, you can store it in multiple collections and play around
with the LLM workflow, like the user's input workflow setup, like router-based setup, like how or
when you want to give access of a particular collection for information to be retrieved. Then
Shrikant is asking, when we use hybrid retrieval, should it be embedded using sparse model or dense
and sparse? So ideally, best retrieval nowadays that we have seen that we can achieve is using dense
and sparse. Earlier, we used to just use dense embeddings for retrieval,

### [42:45]

but over time, like for complex queries, it is seen that based on the keywords, there are a lot of
information that is missed to be retrieved. So we use sparse embeddings. Both have their own set of
negative points that dense embeddings can miss information based on keywords. Sparse embeddings miss
relevant information based on meaning of the text or semantic similarity. So combining them both
together should be the best option that you should consider. Then is it possible to retrieve chat
history directly from the LLM when merging with the current query? So LLM does not store chat
history. LLM is just an architecture mathematical formula function that receives an input, generates
the output. Now, LLM is not going to store the memory. So we need to maintain the memory into a
separate space like SQLite or MongoDB Postgres, whatever kind of database you want to use. You can
use the data store to store the memory on behalf of LLM. You mentioned for retrieval, we should use
both dense and sparse in offline data ingestion, which embedding model is used in that case. Okay,
so all of the major BM-25 models, they're all available as offline models. And for the dense models,
for that, you can use models like the MXBI models, BG models, sentence transformer models, or models
from Quinn, Gama. They're all open source models. So once you just download it into a system, you
would be able to continuously use it for offline usage.

### [44:57]

So yeah, and after this whole flow works, we'd go to the evaluation stage where we do retrieval
evaluation, where we check things like few matrices, like recall at the rate k, the MRR rate
meaning. Recall at the rate k meaning whatever top information is retrieved. Is it relevant in terms
of contextual relevance? Is it relevant to the user query? That is recall at the rate k. And how do
we actually do it in evaluation phases that we create a golden data set where we pass in the user
query. And we also say that this is the, let's say, the actual input and the actual output. So based
on it, whenever we retrieve some information from the vector database, and let's say five chunks are
retrieved, are those chunks equivalent to the chunks that were being created during the golden data
set. So both this number of chunks get matched. And based on how they're ranked, this recall at the
rate k score we will get. So it is just that how much of the correct retrieval occurs compared to
the golden data set we have prepared. MRR is going to be based on how much duplicated content we
have. And then we'll go through a few DPPL methods like in the past previous session that we saw for
fine-tuning, where we created few LLM as a judge to get the quality of responses similar to that.
Answer quality, citation checking, contextual relevancy, all of those things we'll check as, through
LLM as a judge method. And just for like how we can also get, like check how information is stored
in QDrint and SQLite.

### [46:58]

There would be a few other sections, code sections that will be available into the code notebook
when I will show you. And like you can also experiment around all of these things like how to store
the data, SQLite and everything. Haripun is asking after every query, do we have to reload history?
Yes, you need to kind of fetch the last five turns of information or last 10 turns of information.
You can also put them in cache to know, like kind of somehow like instead of getting frequently
calling the database again and again, you can also cache those things for better efficiency of the
system. Can we have some local model updates that gets augmented to LLM that reconsumes tokens? Yes,
that is going to reconsume token because as LLM does not have its own memory, when we fetch the
memory and we pass it to the LLM, those extra information that gets passed, that will reconsume
token. Can we have some local model updates that gets augmented to LLM? Sorry, I could not get you
this question. Have some local model updates that gets augmented to LLM? Okay. So now we'll do one
thing. We'll walk through the PPT and the code side by side here. So in here, like as I was
mentioning, our data set has, I guess, it has around 34,000 records. And for our use case, like
whenever you're using,

### [48:59]

you might be using open AS API or maybe the open source models. In those cases, like it might take a
lot of time when you're going to run the code and so. So we're just going to pick up around 100 or
200 first records. We'll just push them to the vector DB. So you can just quickly run the notebook
experiment with it. Then the schema of the data set is, it has three columns, like act, title,
section, and law. So act, title just mentions the title, section, what section it refers to. And the
law is technically the full text data it has. And we did a manual data inspection on top of it. So
we identified, and if there are certain records that have near empty text or certain level of
malformed entries that are there, maybe the data was fetched or scraped from a website. And during
that, some rows cannot be filled or certain wrong information was filled. And the thing which we saw
was. that the record lens, the lens in the law part, is having around almost 490K characters of data
to almost zero. So those information having that many high number of characters, we will apply some
splitting for other smaller size of records. We'll directly pass it as a piece of chunk to the
embedding model, to chunk and like embed it and pass it to the vector store. So ideal case, my
chunking strategy was derived from just a manual inspection of the data set, not any sort of
configuration or a pre prior best practice method. So ideal case is you always inspect the data set,
try to figure out how is your chunk size, length, length sizes,

### [51:02]

how much of information is there that can be used, good information, bad information based on like,
you also might need some human expert to see like, is this all information ready to go into database
or there is some unwanted information that we can just remove out to improve the inference speed of
vector database and everything. So you define all of these things and you define the final chunking
strategy and kind of you can just run through across the code then. And now with respect to all of
this analysis, how I set up my chunking strategy here is that, each individual section I'm
considering as a default unit of chunk, but in case if it is too long text, I'm going to apply a
recursive character splitter on top of it and we'll split the chunk into multiple parts, like chunk
one, two, three, maybe a few multiple chunks will be created. Then I'm also setting like, no, the
splitting is going to happen, like the recursive character splitter, it is based on this particular
order. It first breaks the information on paragraphs, then if like there is only single paragraph,
it will break the chunk based on some points are there or sub clauses are there. Then even after
that point based splitting is not possible, it is going to split on sentence. Even if sentence
cannot be split, it is split in word. So that is how this recursive character splitter works. And
then we have created a little small custom code setup where we are going to connect each of the
parent with each of the child chunk through a particular parent document ID. So in cases like this,
legal cases, let's say there was one big chunk that got splitted into five chunks. Now chunk one has
information about when that information was released.

### [53:05]

Chunk two has information about the main clauses and the other three has information about who
created the sub clauses and everything. Now what happens is that whenever a user query gets passed
to the system, let's say chunk three was fetched during the retrieval mechanism. Now it is seen that
if the LLM generates just based on the information from chunk three, it might generate some
information, but not complete or fully correct information. So to provide that fully correct
information of whatever answer or the response that LLM is generating, what we do is based on this
parent doc ID, we will fetch full parent information as well, not just single chunk that is formed
from that parent. Like once that particular information or this particular child chunk is fetched,
we will fetch the full parent chunk so we'll try to provide full enough information for the LLM to
generate the actual response. So that is how it is. We will call it as a parent-child architecture
or a small to big chunk architecture. That is how we will define it. So this is how my chunking
method is defined. Then before going to embedding or vector store, I will just quickly go to the
code. I'm just going to connect my Google Collab. I was thinking if we can have some adjusted
weights that augment based on chat history. Maybe I will take this query later on. So to run this,
the things that we have used here is that the main framework that we're going to use it is Langra.

### [55:06]

The embedding models is, I'm considering this MXBEI, just let me confirm this. The same model is
there. If you are going to use this open source model, it will be this mixed-bred organization's
MXBEI embed large model. If it is going to be open AI model, it is going to be text embedding, three
large model. Then this pass model is the Qdruns BM25 algorithm, VectorDB I'm considering as Qdrun,
retrieval optimization methods that we discussed during the architecture is RRF Fusion, MMR. I also
provided an option for metadata-based filtering. Like if the user use that, I'm going to just ask
queries based on this particular act. Then based on that metadata pre-filtering can also be done.
Query decomposition architecture is there and the small to big context. The previous slide we saw,
the parent-child architecture. Then re-ranker, we'll just get back to this re-ranker. I'm just going
to install all of the necessary libraries we'll import. So from Langchain text splitters, we're
going to import this recursive text splitter for my chunking. I'm just going to import open AI and
server. So whoever who do not have access to open AI API key, if they're using Gemini or Grok API,
they can just switch the code here, comment and comment out the sections here, like whatever model
that you want to use. Next year, like we're just defining a few things like number of characters in
a chunk, the chunk overlap, the minimum characters that a loss should have. So five minimum
characters that I'm defining. Then just a few functions like creating IDs for the document like
let's say for this particular document,

### [57:06]

what is the particular reference ID? So I'm just using the hashlib library that it is going to
create a 40 character hex ID for me. Then this strip boilerplate, what they do is that if you go and
see the data, you might find that the act title is repeating multiple times in the information. So
to remove that, we're just going to run this text. So it will just strip up the act title from the
loss text. So like now that repeating information is not passed to the vector store. Then load and
chunk, what it will do is it is going to load the data set from hugging face, the Indian loss. So we
can also go to Google search for this. So this is how the data look like, the act title section and
the law. So as I was mentioning right here, the act title keeps getting repeated here in the law
multiple n number of times. So we can also like kind of remove that. So that is what a few things we
did there, just the pre-processing of the data. Then here we are selecting number of samples to
select from the data set. We're just going to select 200 for now. Then we are going to apply
splitter. So this recursive text splitter. So to apply this recursive text splitter, what we do is
we loop all the data set. We'll select all these three things, act title, section, law. We'll just
confirm that the law contains minimum characters. Otherwise we'll just skip this law that does not
capture enough information. Then the other two functions like the strip, the boilerplate and create
document ID. And we'll store all of this data into the records list where I would have this ID, the
document ID, act title, section, the parent's document ID.

### [59:07]

And this like for a parent ID, if a small chunk ID is created, then this I is also passed. So like
parent ID, chunk ID, those can be separated. Chunk text, whatever chunk is there is passed and
parent text, original parent text is also associated here. So this parent text and all that will
also only be a part of the metadata. Main thing that when user query comes in and we need to match
it in the vector store, this chunk text is what that will get matched. So all of this thing, I'm not
going to run like all the outputs that I have already captured here. So you would be able to notice
here, like it has downloaded the data set and out of the data set, I have fetched first 200 samples.
So those 200 samples has given me 255 chunk text. And this is the first chunk text. Sorry, that's
the first. part of the data that we can see, this ID, egg title, this is the first chunk text and
whatever parent text is associated with it. Now, as this parent text was much smaller, the full
chunk text is also the same size of the parent text. In case if this parent text was much bigger,
like two paragraphs, three paragraphs, in those cases only, we would have multiple chunk text. Now,
let's go to the embeddings part. Embedding strategy, as we discussed already, a few things like
dense embeddings, sparse embeddings we're going to have, like hybrid search we'll do with respect
to, the dense embeddings is going to capture concepts, meaning relationships of the data, versus
this sparse embeddings captures exact terms, numbers, keywords, all of these things is what these
sparse embeddings is supposed to capture. We combine both of these two, we harness the power, both
like semantic similarity and the keyword similarity.

### [1:01:07]

So using both of them will give us more better retrieval results than using any one of the single
method. It's what we have seen over the time, like for the previous past three to four years, as the
rag has evolved, combining both of these method is what that is usually suggested. And the vector
store configuration for this would be, vector store, we would be using a single collection with two
different types of vector, dense and sparse. Now, in case you're using some other vector store, not
the qudrant one, so qudrant has a capacity where, inside the single store collection, it can store
both, like for a particular record, it can store the dense vector and sparse vector both, and the
metadata associated with it. But in case you're using other vector stores, like pine, cone, chrome,
rdb, in those cases, you need to maintain two different collections, one for dense and one for
sparse. So that is how, based on the vector stores, you might be needing different collection, same
collection and so. And now inside the BM25 sparse embeddings method, qudrant provides us with one
thing that is called this IDF modifier, it is term frequency, inverse document frequency modifier.
So what it tries to do is, it tries to capture the words that is frequently getting repeated inside
the information. So it tries to do that, whatever BM25 algorithm is there, like the whole idea is
that, based on the keyword mechanism search, it tries to identify term frequency that is occurring
frequently, and it captures that. So that is how the keyword will give importance

### [1:03:09]

to a particular keyword, keyword matching will happen. So this IDF modifier is kind of an algorithm
that is helping out in finding important keywords for the algorithm. So that is how, like there is
one modifier available for BM25, so we have also added this modifier in the code. And for each of
the information that goes inside my vector store, act title, section, parent document ID, chunk
text, and the parent text. This all information will be going to be passed to my vector store. So
here, those who are going to use OpenAI, they can select OpenAI, if they're going to use the local
mixed-breed model, they can just here replace the value with local. The code will automatically pick
up the OpenAI embedding model or the text embedding dense model. For the sparse embedding model,
we're going to use this Qdrain's BM25 model. Then we have two particular functions. One is embed
dense local, embed dense OpenAI. For OpenAI, it is going to use this function. For the local model,
it is going to use this dense local function. And then we'll finally have another two functions,
dense that is acting as a switch provider based on what provider it will call the particular
function. And this embed sparse, it is just going to return as a list of all these sparse embeddings
that will be generated. Then I will write my main vector store code. We'll import the Qdrain client,
we'll write all of this. So like this, all codes, I'm not going in much depth because the few of the
document and the other previous code parts that are there in the week three covers all of this
configuration, settings, information, and everything. So you can look into the syntax later, but
just try to focus onto the concepts that we're discussing here, okay? So we'll just initialize our
Qdrain client

### [1:05:10]

where we're just going to store all of this information into in process, into my RAM only, we're
going to store. Then we'll define the collection name that will be Indian laws, I'm just defining.
The dimension of the dense embeddings that is 1024 because the OpenAI's models, the embedding
dimension size is of 1024 size. Then the client.recreate collection, meaning if the collection
exists, it will drop it and create a fresh one. Or you can also, if you don't want to do something,
you can also do just a simple create collection. Both the methods are valid. We'll pass the
collection name, the vector configuration here, I'm going to pass dense vector parameters, size
equal to whatever this dense dimension was equal to, and distance is what, cosine. So it will going
to use a cosine similarity, distance mathematical function to identify the semantic similarity
between two vectors. And in case of sparse vectors, we are going to, like as I mentioned, we're
going to use this IDF modifier. So modifier.idf is where we're mentioning the IDF for sparse
vectors. Then just a UID creation. So Qdrain will, like the point IDs that I mentioned here, we're
just going to create this UIDs that Qdrain will consider as point IDs for each of the record that is
going to be passed. And I just have the simple absurd record function. What it will do is, it will
go through this dataset that I had. It will go over the dataset. It will call the embedDense and
embedSparse functions so my vector embeddings and sparse embeddings would be collected. And I'm
going to collect all of this as a part of points. So here you will notice no dense embeddings
collected here, sparse embeddings collected here. And then I'm putting it all like the information
like actitle section, parent doc ID,

### [1:07:10]

all of them I'm collecting as a part of payload. And then finally, when I hit this client.absurd
collection name, so in the Indian laws, it will add all of this points data that I've collected
here. So all of the information will be stored inside my vector store. So it will show absurd 256
records. Then we'll come to my retrieval and re-ranking point. So here, now there is a particular
method called as rank fusion. So when we do dense retrieval and sparse retrieval, what will happen
is that it will both have top five, top 10 or top N number of results that are fetched. Now
retrieval rank fusion algorithm is something that combines not based on the scores. It tries to, you
know, like kind of figure out the duplicate content and tries to merge. Like let's say we have top
10, 10 in both dense and sparse. What it will try to do is kind of it will try to capture the best
of the semantic, like the dense methods and the sparse methods. So let's say, let's just take an
example from the dense vector store, it fetched document A, B and D. And from BM25, let's say it
captured, like BM25, the sparse vector store, it fetched document A, C and D. So what it will do is
it will try to find what is the frequently occurring document that is there in both the search
results and will rank them first. Like in my case, dense one A, B and D

### [1:09:11]

and in sparse it was A, C and D. So it will identify that A and D are occurring in both. So RRF will
give result as A and D as top two and then B and C will depend on what were the scores from this,
the scores here that were given. So based on it, it will kind of give a ranking to B and C. So that
is how RRF is an algorithm that will give us this and it is going to use this particular
mathematical function here. So that is how this RRF works. Then we have this maximum marginal
relevancy. It is kind of an algorithm that tries to filter out diverse information. So all in all,
it tries to find information that is duplicated across multiple chunks and kind of like, you can
select it after MMR, how many number of chunks you want. So let's say you had 20, 30 results and you
want top four to six. So MMR will maintain that the top four to six chunks with. all having
different variety information, diverse information is captured. This algorithm is used to do it.
Then the adaptive retrieval width. This is where we're going to put up the re-ranking algorithm. Re-
ranking algorithm is a similar model with respect to embeddings model, just that the embedding model
can convert text into numbers. The re-ranking is something that tries to understand, based on the
user's input, how they could be ranked. So that is how re-ranking works. So maybe out of your top
four to six results, we will re-rank it and maybe from this diverse to different chunks, the re-
ranking can put last chunk as the first chunk in the rank, depending on how well the re-ranking
model is also trained.

### [1:11:11]

Re-ranking model is also something that requires training and everything. Usually, mostly they're
trained onto several types of different re-ranking datasets already. So usually re-ranking models is
not something where you might require more fine-tuning to go on top of that. Can you please explain
MMR one more time? So MMR is something, let's say, we have 20 chunks of information. Now, when we
store information in vector store, there can be chances that. So what we did was, we fetch
information through dense embeddings and sparse embeddings. Let's say we take top 10 from both, and
let's say out of this top 10, both of those retrievers, they have almost five to six same chunks
that are being loaded. So MMR will try to ensure that any information that is repeating or
duplicated, it is just going to drop it. So maximum marginal relevancy. What it technically means
that out of all the chunks, the chunks that is having different information that can help LLM
formulate the response. Let's say I have five chunks, each giving the same information about other
act, that will not help LLM to generate the full response. Versus if there are five different chunks
that has other information, other act information, other act when it was built information, the LLM
will be able to formulate much better answer. So that is what MMR tries to produce here. Diverse
candidates, all the candidates with different information, that can be provided to LLM. Then just
metadata pre-filtering, just for case that the user already knows

### [1:13:11]

what act or what clause they want to ask the information on. It is something like if you have built
up a UI or some system like that, we can just simply create a button or information where the user
can select the act and based on it. This information is passed to the VectorStore, will filter on
top of the metadata. So as we saw in the code as well, this all information goes through it, act,
title, section, and everything. Let's say the user selected a particular act title based on it, only
those chunks having act title equal to will get fetched and will be passed to the LLM. All this
ranking method also refers to user query correct. Yes, all these ranking methods like for example,
the re-ranking will match the chunks with respect to the compare with the user query, so they can
re-rank it properly. MMR will not compare it with user query, it will just going to look through the
information around the chunks they have. This RRF is also is not going to look at the user query,
only re-ranking is the one that needs to look at the user query to identify if all the information
out there is relevant with respect to the user query. Then we would have this query decomposition,
idea is very simple. We will have a LLM setup where an LLM will create multiple queries out of the
single main user query. We will have multiple queries for each query, we will do an independent
retrieval, and then we'll merge all of them together. And based on our previous methods like MMR,
RRF, merge and deduplication of retrieved results will happen. So we'll finally have N number of
queries that will be diverse in information,

### [1:15:11]

where that information will exist. We will have gone through across re-ranking stages, hybrid
retrieval, everything would have happened. So we would have some good information to generate the
response. So this final merge set of merge and deduplicated context that is passed through all of
these previous two slides of methods that we discussed, and that will pass as a context to the LLM.
And re-ranking usually would kick in after this whole retrieval stage has been completed. So once we
have all of the MMR, RRF, everything collected, re-ranking is just going to re-rank the chunks. So
let's say I have my final 10 chunks after query decomposition, independent retrievals, RRF, MMR,
hybrid retrieval, if any metadata pre-filtering to be applied after all of these things is done, re-
ranking will just ensure that whatever top K chunks are there, if we can re-rank them. So you can
see chunk three is the top one, chunk one is second one, chunk seven is the third one. So it will
re-rank it. So usually LLM has a tendency that it kind of treats the top chunks as having the
highest information or information relevant to generate the information for the user's queries. That
is our reason we need to apply re-ranking. So all the relevant information, we put it as a top of
the list of context that we're going to pass it to the LLM. Now here we are having another mechanism
that this re-ranker will also give us a confidence signal. So if it has a high confidence, this
information gets directly passed to the LLM. But if it says it is low on confidence, we have another
section of web search. So here we have particularly a setup of surfer API. So surfer API is like API
to search

### [1:17:11]

on the Google search engine. So it will take the user query and search on, make a web search with
its surfer API and will fetch data from the web source. Like let's say if I go on Google and search
what is other act, what is the information on the first page, 10 different pages information, all
that information will be taken as a context for the LLM. So now this can be something that might not
be usually used. So for example, you are in a setup where internet is not allowed. Like you don't
want to have internet to be used with your rack pipeline. You're only focusing on offline models. In
those cases, you can't use web search. Web search is usually just treated or used in fallback cases
where when the data, so like usually like from my personal experience as well, I have seen that
users sometimes ask queries out of the bounds of whatever we have in our database. So either like if
that is a business decision to make, like based on the how the stakeholders, the main teams who are
the stakeholders of the product, like they have to make this decision. Do they want to treat to the
user queries where we do not have information in our database? Do we need to generate the response
for that? That is up to like, as I mentioned, is a business use case, but like all in all, you can
also implement things like this. Let's say user query is not something relevant to the data we have
in our vector database and we cannot respond to that. You can set up input guardrails and things
like that as well, where the LLM will directly respond to the user that no, I do not have
information

### [1:19:12]

or I'm not allowed to speak on this particular topic. So both the things are possible. So that is
all in all a business use case to be considered. Usually different domains, finance, fintech,
different stakeholders, like if it is a conversational chat bot for some website, usually web
searches are allowed. So depending on your use case, business case, business decision, you need to
figure out, you need a web search, you do not need a web search. If you need the LLM to say no back
to the user. So that is something as a decision. Developers should not be making, like business
people should be the ones that should make this kind of decisions. Then coming to the memory and
orchestration. Yeah, just give me a minute. Yeah. So. With respect to memory and orchestration, I'm
going to use SQLite as my main memory store where each conversational history would be stored. So
something like this original query, rewritten query, and the response from the LLM. This is what I
will store. There will be a query rewriting node in the LandGraph code where upon every new user
query, a last n turns history would be fetched. We can set last three turns, last five turns, last
10 turns. Then we can set and then an LLM query rewriter node will run, which will be based on the
user's previous query and the new query. If there is any relation between those queries, it will
rewrite the query. Now, in this particular LLM query rewriter, you need to mention specific
instructions. That if the new query is not relevant with the previous query, just respond with the
same new user query.

### [1:21:12]

But if there is any connection, then you need to rewrite the query. So all of these instructions are
also to be provided to this LLM query rewriter so it knows when to change the user query or when to
keep the same user query. So this is also need to be taken care of as a part of the prompting there.
What will usually happen here is that the system will then use the rewritten query, will retrieve
relevant documents, and the process will go the same sequential flow. Documents will be retrieved,
re-ranking would happen, top chunks would be passed to the LLM, and will generate the final answer.
Step 2, will it be rewritten for previous or some sort of summarizer? So we don't call it summarizer
because summarizer is supposed to summarize here, it will try to formulate a new user query. So as I
was previously giving examples. So what is generally a user's tendency is that, let's say, I will
ask what is other act? The LLM generates the response based on the data in the vector store, like
giving information on the other act. Let's say the LLM asks something like, if you need information
on other act updated clause in last year, should I give you the response? That is what LLM gave you
as a suggestion, as a final response line. As a user, the user might have tendency that the user
will respond with yes, go ahead. So if I'm just going to use that yes, go ahead and retrieve from
the vector database, the response will always be wrong because what is there with yes, go ahead and
to be matched with vector store. So idea is based on the previous user query, I will write a prompt
that use the user's previous query and try to connect with the latest user query.

### [1:23:13]

If there is any connection in there, then please rewrite the query that would be suitable for the
retriever mechanism to retrieve enough information from the vector store. So that is how you write
the prompt. So the query rewrite the query, but we will not summarize it because summarizing would
mean that it would be something like user discuss these things and all of these things. So that
summarizer will not tend to make good enough retriever from the vector store. Is the LLM query
rewriter implemented as another LLM or is it written in Python code? Yeah, it is going to be an LLM
call with a prompt. As a context, we pass the latest user query and the user memory, the previous
memory. So based on that, that LLM will give us the output. Now, the state schema. So this is how my
whole LandGraph architecture looks like. These are all the different inputs. The LandGraph
architecture would have session ID for memory purpose. So my SQLite memory will store session by
session. So let's say in session one, I'm talking about session two. So I'm separating memory based
on sessions. Then the raw query, raw user query, rewritten query, list of decomposed subqueries,
retrieved chunks, re-ranked chunks. So all of these things are my state schema for LandGraph to
collect all the information and generate the final response. So I won't go much in depth of
LandGraph here. Like you can go through a few of the materials provided in the session three.
Understand LandGraph as a whole. Like what is this state schema? How does this data flow through the
different shared state across the graph? Like this is a simple thing that you can just simply learn
in 15 minutes, 30 minutes.

### [1:25:17]

So just try to look over there into the document. And this is how my orchestrated graph would look
like. Query rewriter, query decomposer. The retrieval mechanism will work. Reranking will happen.
Then the confidence gate would be there. Either generate the response or fall back to web search.
And LLM will generate the final output. This is how my full LandGraph code will look like. So I will
go. So this is all my codes. That is all I've mentioned. Like a few of the theories, like a few of
the examples, mathematical sections I also provided here in the notebook itself with respect to RRF,
MMR, everything. So you can also read it to get more idea about how it will transform the data. And
then this is all the mathematical formulas for RRF, like scores, payloads. And then we are kind of
sorting it with respect to now this hybrid search is there. So we are like fetching data, like the
chunks from the dense vector store and the sparse vector store. And we're passing it through the
RRF. So RRF kind of like as we're discussing, right? It will select as the frequently occurring
chunks in both the dense and sparse embedding vector stores. Then we'll apply this MMR. So MMR again
is a pure kind of mathematical function where we are going to see, you know, like multiple things
like dot functions will be applied, like linear algorithms will be applied, lambda parameters,
everything. This whole mathematical stuff will be applied. We'll get MMR scores. And based on the
top N value, like this will also sort the candidates into based on the MMR scores. So whatever top N
chunks we want, based on that chunk size,

### [1:27:22]

this MMR will give us the best N number of chunks based on that MMR score. And this is retrieve
function, which is like combining all of these things together. So kicks on hybrid search. Inside
the hybrid search is where I'm running the RRF. After hybrid search is completed, I'm going to do
this MMR. And this is my full retrieval setup is done. Then I have a few functions written for re-
ranking. So I'm loading the BGE re-ranker model from sentence transformer. And re-ranker is
something simply is going to take input like this, the user query and the text, the text inside the
chunks that is there. And whenever the re-ranker gets applied, it will re-rank, like it will apply a
score to each of the query and the chunk pair. And we can just loop over a for loop and we'll just
sort it out, like sort the candidates based on the re-rank score. Reverse equal to true means in the
descending order, high score to low score. And we'll cut off this list based on top N. So let's say
my top N is six, meaning in the descending order, top six chunks would be finally passed from the
re-ranker to the LLM. So that is how the re-ranker will work. Then this is just my LLM part where
I'm just loading up my OpenAI model. Like you can also select the GROC client, GENAI client for
GROC. This LAMA 3 model will be used, Gemini 2.5 Flash will be used. And this generate function is
just that based on the provider you choose, OpenAI, GROC or Gemini, it will call that particular LLM
client and will return the response for that. Then the web search fallback function for that, like
the SERPR. So it is going to use this URL, google.serpr.dev.

### [1:29:23]

We'll use the SERPR's API key. So you will need to create an account on this SERPR, the SERPR. So
you need to go here, sign in. And through the API keys, you will be able to get your default API
key. Just get that API key, paste it here in your Google Collab. And that same API key is supposed
to be used here. And the SERPR is free, of course, for around 25 user queries, 2,500 user queries
per month. Why do you use three different LLMs? So this is just an option for you to run. If you do
not have paid OpenAI account, you can choose any one of the service here. When I call this generate
function, if I select provider is OpenAI, then it is just going to use the OpenAI model. If I select
Gemini, it is going to just use the Gemini LLM to generate the response. Now, after this web search
is done, we'll define this memory based on SQLite. So the same SQLite code is also explained in more
depth with respect to memory. In LLM, there is one session, so you can look into that. So that will
give you an idea like how this memory, MongoDB memory, SQLite memory, that we configured and we did
it. So the main functions that we usually do here is, one is getConnection, that connects us to our
SQLite store. Another function would be getChatStory, that runs a SQL query in here from our memory
store. This will select the previous memory information

### [1:31:25]

that will be used for the query rewriter. Then there will be an append return. So any new user and
the rag pipeline conversation is happening. That session and return, meaning the user and the LLM's
response, that both will be inserted into that particular session ID. So these three main functions
is usually whatever kind of data store you use, SQLite, Mongo, Postgres, anything you use. One
connection function, one loading the ChatStory function, and one adding information to the database
is what we need to add. Then the main LLM pipeline would be there. So all of the state schema, as I
was mentioning, the same state schema is mentioned here. Now here my full architecture, the
architecture that we saw initially and also in the LandGraph slide here, the query rewriter
decompose user. All the nodes in LandGraph I have mentioned here, like load node, the load history,
the rewrite query, the decompose. So inside this, it is doing the same thing. So for example, in the
rewrite query. So what it is doing is, it is having this particular prompt, as you can see, is
accessing this history text and based on the new user query and the history query, it is calling
this generate function where my provider is OpenAI and we're passing this prompt. So what it is
doing is rewrite the follow-up question into standalone fully specified question. Output only the
rewrite question, nothing else. So this is going to rewrite the query with the new user query based
on the previous history text. So this is how I'm written this, all the nodes, rewrite query.
Decompose is also similar. We have a prompt that asks us to

### [1:33:25]

generate sub-questions based on the original queries, and we're going to get multiple sub-queries,
which I will pass through the LandGraph graph state. Then we'll kick on this node retrieve, which
will retrieve for each of the sub-query from my dense and sparse vector stores. Then the rerank node
will work, so it will give me the final N chunks that can be passed to the LLM. But here, we're also
getting this confidence score. So based on the confidence score, I have this route confidence. So
web search, if the confidence is less than confidence threshold. So I have particularly set the
confidence threshold as around 0.35. So if the confidence is less than 35%, web search will be
executed, else we can directly use this, reranked chunks to be passed to the LLM. This web search,
in case we want to do web search, context assembly node is what it is doing is, the outform, it is
looping over this reranked chunks. It is combining all of these chunks as a list, and finally, it is
all collected as a list. It is just going to combine all of this together as a final string, like as
a whole paragraph, as a bunch of paragraph. It is going to join everything. And here, we're also
adding the citations. Citations is something that's the title of the act title. So like when the LLM
generates the response, what act titles it is referred to to generate the response is what will be
covered inside the citations. And inside this node generate, where the final LLM will generate the
response. So here I have the prompt, like you are a legal assistant answering questions, here I'm
providing the context, and the question, like the new user question, it will be passed here, and the
LLM will generate the response.

### [1:35:25]

And the final node, that is the persist memory node, where the original user query, rewritten query,
the final answer from the LLM, the source of the response, and the citations, like where the LLM
generated the response, all of these things would be stored inside my SQL at store for the next user
turn to be considered as a part of the memory. Then I'm going through all of this, like all nodes
are just functions. So to register all of them as nodes, as a graphical flow, we first do .addNodes,
so all of these functions will be registered as nodes. Then we set an entry point, meaning what will
be the, like whenever a user query is passed, what will be the first function that will receive that
input? So loadHistory is the one that will receive the input. And then we are mentioning edges,
meaning what node connects to which node. So loadHistory gets connected to rewrite query, rewrite,
like whatever function rewrite will do, that information will get passed to decompose, so decompose
to retrieve, retrieve to rerank. And here in case of rerank, after rerank as we were discussing
that, right, based on the confidence score. If the confidence score is low, we'll do web search. If
it is like confidence score is okay, we'll pass it to context assembly node. So here what we do is
we, instead of .addEdge, we use .addConditionalEdge. So here we are going to use this route
confidence. So this route confidence node here you see is giving us this particular like decision,
is making this decision. Web search if confidence score is less or context assembly. So based on it,
we're giving it here like decision to make, like which particular node to go through after rerank
node is completed. So after rerank node is completed, if this route confidence node gives me output
as web search or context assembly.

### [1:37:27]

So based on it, I will map it to web search node or context assembly node. So after rerank, it can
either go to web search or context assembly. And after like, you know, if it goes to any one of
that, the idea would be it should go like from this, it should, both the path will merge it,
generate. So that is how the flow would also work. Like web search is done, it will go to generate,
that is LLM will generate the final response. Context assembly as well, it will go to the same
generate node, like both branches converge back to the same node that is generate. After generate
node generates the response, the response goes back to the user as the final response. And it also
goes back to the persist memory node, which will store the data into SQLite. And we just mark the
end here, end will mean that lang graphs graph run is finished. So that is how my full graph is
there. And then when I do graph.compile, so the whole graph is like registered, created with all the
node edges, everything defined. And then I have just marked a few queries like this. What is the
punishment for murder? What about minus like this? So just for example, let's say, I'm just looping
over this queries data frame you see here with multiple queries. And yeah, so like once all of this
is done, all the session ID query, everything is kind of captured. We'll just loop over this data
frame. We'll kind of, what I say, we'll run the full, okay, just a minute.

### [1:39:48]

I guess we need to run this. Okay, right. So when we compile the graph, we call this as a app,
right? So we will use this app to invoke this particular lang graph. to generate the final response.
Here, in this case, as you see, once I have this dummy set of inputs that should be passed as a
query to this Lang graph graph, what we'll do is that I'm going to call this app.invoke, so that is
what's going to invoke my Lang graph. I will pass a few things like this, like session ID that is
what we'll consider this as a turns, let's say for session one, if I'm asking something, if I use a
different session ID, then that memory for the different session ID should not be fetched. So that
is why session ID is used to differentiate between multiple sessions of how a user chats, then the
raw user query, act filter if the user has selected any act filter, and I'm providing a provider
here. Provider just to mention that use OpenA LLM to generate the response. Then whatever response
this gives, so from my Lang graph output, I will be able to get all of this query, rewritten query,
source path, confidence score, answer, and citations. I'm going to store all of this together into
my demo results list, and when you run this, how you will notice it here is the original query, then
this is alongside my Lang graph code, at certain points, I have put certain print statements. So the
same print statements, it is just going to show here what subqueries are generated, what retrieve
did,

### [1:41:48]

like embedded query, how much time it took to fetch or retrieve data from the vector store, the
sparse vector store, the MMR, how much time it took to filter out the text, and finally, if it does
not find information, so you can see confidence was less than 0.35, 35 percent. So it took the
source path as web search, so it did a web search, and this is the answer it generated. So this is
all a few of the examples I have taken with low confidence score, so you will notice it is all web
searches here. But let's say, let's say, query, what is Aadhaar app? Okay, maybe we'll just see that
in a different setup, where we will be fetching that from the vector store. But for now, I guess how
the flow runs, the MMR select does, and based on the confidence, it will either point to web search,
or it will either point to vector store, that is how it will do. And then there is, we have given a
section here, inspect the database from where, it is kind of going to just showcase to you, like the
collection level information, how many records are there, information on vector configurations, pass
configuration. Then if you want to load data from the, like the QDron store, so client.scroll, so
collection name, you can keep, limit how much data you want to fetch,

### [1:43:48]

and you can also select, have an option like this, with vectors equal to false or true. If it's
vectors equal to true, it will generate a very huge response, because vectors would be like 1024
numbers. So your output could be quite big, so you can just keep vectors equal to false, and when
you print it, you will notice like this, all the things that is stored inside your vector store.
Next is, just getting a SQLite dump. So this is all the memory that is stored inside my SQLite, like
session demo murder, like this one session I did, then another session I did. So across those
different sessions, what are the memories are stored is what, like I'm taking from the SQL. So this
is again also something very simple, like we just connect to the SQLite store, execute this query,
like to fetch the data from the SQL store, and just looping over the particular information to print
this out. Like that's all, like how we have done it. Next is, now here, we're going to go through
the evaluation phase. So evaluation phase, we have a few things here like recall at the six, so like
we are trying to identify whether the correct pair appears within the top six re-ranked results. So
something like let's say, I have created a golden dataset with the kind of query, and if any results
are retrieved from the vector store, what should be an ideal act title that should be responsible to
generate the response. So out of my top six re-ranked results, if this pair is found in that, so
recall at the six value would be equal to one. If nothing is found, it will be equal to zero. So
that is how we define if your retrieval mechanism is able to retrieve correct information or not. So
that is one way to do it. Next is when is this mean reciprocal re-ranked,

### [1:45:49]

that is like a kind of measures ranking quality, like it's very similar to the kind of RRF. So it is
just not going to re-rank, like we'll give you a rank for each of the chunks that were retrieved
from there. And the evaluation step where we will curate 20 golden dataset across 10 different acts
that were like not taken from the original dataset. And on that we are running three different types
of evaluations. One is like a custom LLM as a judge, the citation correctness, like if the citations
that are like cited, like no, the LLM is citing any particular act title or any information, it
makes any citation. Does that citation is relevant to the response and the data that is retrieved?
That is one thing we'll check. Answer relevancy, like is the answer relevant to the user query? So
this is like kind of like, you know, previous fine-tuning session where we discussed, right? That
these are like pre-built LLM as a judge functions that is already provided by DPVL as a library. So
this answer relevancy and faithfulness are like already LLM as a judge provided, like they have both
their own prompts, like prompt written to identify the user query, like the responses relevant to
the user query. And faithfulness, faithfulness is something that does not check for any sort of
correctness with respect to user query, but it tries to check. If like, let's say user asked for, or
a user stated that to follow any particular thing. So if in the response is like, let's say user
asked that, explain in brief the other act.

### [1:47:49]

So if the output was in two paragraphs, so faithfulness score would be low because what the user
asked as a thing to follow, the model did not follow. So that is how there will be a different
between answer relevancy and faithfulness. Okay, we'll just go to this evaluation stage where this
golden set is defined, like this query is there. Golden sections is defined for it to kind of know
this different other acts are defined and what section we need to refer to, to generate a response
for it. So this is how a golden set is prepared. And on top of it, like the recall at the rate K,
this particular function is returned, the MMR function is returned. This is all kind of the
retrieval scores and everything this is calculating. So the output of this would be a data frame
like this, query the gold sections, top it, and it is showing like in the retrieved data, like was
my correct information or correct section, the correct act title was retrieved or not. So we can see
like majority of my titles, my recall is correct, meaning across my top six, it is actually
retrieving the correct act title in the section that I want, but the MMR here somewhere would be
less, like here you can see one example, it is point two, somewhere along with that, I guess, okay,
it is just one. So what this point two here mentions is that, that even though my section and that
particular act title is mentioned, but that is ranked low into the top six chunks. So that is what
MMR will show. So this is just with respect to the retrieval evaluation, like if you want to check
on that. So we can check it with this recall,

### [1:49:49]

like just identify if the actual correct data is present in the retrieved context and what rank it
is on, we check it through the MMR. So there is two ways you can like check. the relevancy or how to
evaluate the retrieval mechanism. Then on top of this, this part, the LLM is a judge part, that when
we're checking for citation correctness, so here we have defined a criteria. Check whether, now this
all legal claims, outputs, and everything is mentioned here. Like just a prompt, we have defined it,
how to check if the citation is correctly cited, is given. What things to test it on is, is to test
it on user input, the output, and the retrieved context. So combination of these three would be used
to see, like the LLM say based on that, that is the citation correct or not. Then the by default,
rebuilt answer relevancy and faithfulness matrix I'm importing. Threshold is being set to 0.7,
meaning this should be the threshold like the LLM feels that if it gives a score above 0.8, meaning
it is relevant, like the answer is relevant above 0.7. Above 0.7 as well, the answer is faithful to
whatever user asked in the query. Then we'll do a simple use case, like we'll loop over the gold
set, we'll invoke the LandGraph cases, and in those cases, we'll have this test case, we'll pass the
input, output, and the retrieved context all along together through this result. So we're just
trying to capture this test cases here, and then we'll just run this evaluate function from dpval,
we'll pass my test cases and all the evaluation functions. So what we'll do in the fine-tuning
section,

### [1:51:50]

we also saw, it is going to run through this multiple setups through all the 20 test cases, and
wherever it is failing, it is actually going to show us like this was the input, this was the
output, and what failed here was that the answer relevancy failure, though it gave it a score of
0.62. So the score is 0.62 because the answer appears to address the question about special measures
for issuing other. So I guess the question was, what special measures must be taken to issue other
numbers to children, senior citizen and person with disabilities, and this was the kind of response
that give the special measures for other certain categories, women, children, the authority is
required to take special measure and any other identified individual. So I guess it is going to say
that it is saying here, persons with disabilities, but it is not higher because it includes
irrelevant groups such as women and skilled and organized workers. So it gave extra information that
might be irrelevant to the user. So here it is mentioning that why the score was low. So this is how
the LLM as a judge has gone through all the sections. So I guess in terms of faithfulness, it is
almost going to be one because there was no specific instruction on the output format. So
faithfulness would be usually high. Answer relevancy is the one which you will notice that is
consistently certain times failing, and this is the final average score, like citation correctness.
The average score is 0.7, passed for all the inputs, answer relevancy, pass rate is 90 percent. So
two cases it failed. So here you can also see pass rate overall is 90 percent. Eighteen test cases
successfully passed for all the tests, but failed on two cases where answer relevancy did not pass
correctly. This final section is just the outputs of all the LLM graph in box that is run.

### [1:53:50]

So this is irrelevant for you, you can just skip this. This is just printed outputs that has been
generated here. Here we are just showcasing the full written view, for loops and print statements
just to put everything, all the evaluation steps together as a final data frame to comparison like
query, gold section, recall, MMR values, citation, G-val scores, and everything. Based on the score,
does the answer relevancy thing passed? So two cases you will notice it is false. All the other
cases is it true? So general, whenever we do evaluation and all of these things all in all together,
generally it is seen that even after production, or before you go live in production, whenever you
develop this evaluation setups and everything, the general idea is that we do create this kind of
dashboards or data frames just for everyone to see, everyone to be on the same page, everyone can
track a certain level of models, information, models, idea, or how a particular version of the RAG
system worked. So just to keep all of those tracks, we maintain different data frames and
dashboards. Now, this was all from with respect to today's use case RAG pipeline. This is like total
relevant with your third project, the legal query resolution. So you can also use this notebook as a
reference notebook that you will create as a solution for the project three. Now we'll discuss just
a few of the topics relevant to the next week, that is agents. So fine tuning and RAG, as we
understood was, fine tuning is totally around changing the information or the data pattern the model
is already captured through training process.

### [1:55:50]

So when we want to change the models, tone, behavior, thinking process, we fine tune. When fine tune
is technically not efficiently possible due to repetitive data updates or incoming data, we use
things like RAG where we don't want to fine tune. And then comes the part agent where agents is what
something that is powering most of the systems. Even if I have to say the current chat GPT and cloud
code desktop, they're agent setups in themselves. Why? Because upon every user query, they first
observe the information, observe the environment, gather information, like what is the query? What
extra documents are there? What the user has given the information? Anything like that. And based on
it, it first plans, it plans it reasons with itself, it decides what to do. Like if the model is to
call a tool, if the model has to call an API, and based on this plan, it acts. And based on the act,
it generates the result, gives back to the user. But here is also a change that the modern agents
are now also capable, like in terms of observation, that if it has taken a plan and action, if
needed before just responding back directly to the user, they can check their outcome. And if they
decide that maybe they can improve the result, they will go back to the plan and just continue the
loop till they want to generate the response back for the user. So usually there are a few
techniques like how many loops you allow for the agent to take maybe three loops, five loops, and
inside those three to five loops itself, agents should be able to generate the response. But yeah,
agents are more towards understanding the system environment, where they can interact with setups

### [1:57:51]

outside of their environment as well, if they have been given connections to it. So the rag pipeline
we saw today was all a sequential flow. Like we give access to different nodes, different like SQL
database, everything. We coded out everything so that it flows through a particular path. Now agent
tech behavior will be different here. LLM would be connected to all the nodes, but we will not
particularly define a workflow that the LLM needs to take, call this thing first, call re-ranking
next or so. The agent or the main thinking engine of the LLM, it will be designed in a way that
through prompt and other information, it will be given access to all of this different database,
tools, nodes, everything. And based on the user query, it should be self-sufficient enough to
understand what to call and how to formulate the response for the user. So that is how we call it
agent tech behavior that is different with respect to LLM workflow or the rag pipeline behavior. So
like primary function, like how to configure, when to select which method based on our use case,
like whenever we used to change the domain behavior, tone behavior, styling, output format of the
LLM, how the LLM thinks, we do fine tuning. If we want to just provide external knowledge, in this
case rag, and if you want the system to think by itself, do a multi-step reasoning, call external
tools and everything, we create an agent tech kind of a system. So just for our understanding today,
what we did was a rag pipeline or a rag system with a few agent tech components, like database
connection or memory setup and everything. But in actual use case, like if it was total agent, the
system should have been fully autonomous.

### [1:59:52]

Like the LLM should itself decide when to write into memory, when to load from the memory. It should
not be something like we write in the code as a sequential flow to complete all the process. So that
is like today's thing. We saw a few agentic components, but the system was not fully autonomous. We
will only call it RAG system with a few agentic components. Okay. Yes. Now, the main key takeaways
from the session, we started the session with understanding the architecture for the use case, the
legal query resolution. We understood a few parts of the data. Then we went through a few sections
like, why did we take a particular decision of chunking? We went through retrieval setups like RRF,
MRR, then small to big size chunking is also one chunking method we saw. Then all those re-ranking
algorithms, when they kick in, we saw the land graph, full graphical flow, how do we connect
different nodes as edges and everything? Why do we require query rewriter? The memory setup, all
things together, and then we saw the evaluation stage with DP-VAL and the two custom functions, like
Recall at the Rate Key and MMR, combined them with LLM as a judge, like answer relevancy,
faithfulness, matrices to figure out if our pipeline is generating good responses for us. Finally,
we just tried to understand the difference between the fine-tuning RAG and the agent setup and how
agent that will be coming up in the next week. This is something that is different in terms of the
setup, then RAG setup that we did today. That was the major key takeovers from the session and from
this week that you should take. I'm just going to allow microphones for everyone. If you have any
queries, feel free to ask.

### [2:01:52]

Just give me a minute. Can you please check if microphones are enabled? In that notebook, you have
mentioned about some graphs, I think that line graph. Can you explain that? Yes. Why do you use
that? Line graph as a full framework? Yes. That is explaining that full stuff might take over half
an hour or so. I would suggest to you, there is a previous notebook and full line graph setup also
available. Go through that. If you have any queries, please just drop me that separately because
explaining full line graph as a framework, libraries, nodes, and edges, that might itself will take
over 30 minutes, 45 minutes from now. Yes, but can you just explain in a short way what is actually
data we are storing? Data we are storing? Why we are using that? Earlier, we used to have these
libraries

### [2:03:58]

like Lang chain and all. They all had a certain level of things that we used to create. The Lang
chain name itself came from chain. We used to create chains of different LLMs or different steps
combined together to generate a response. Lang graph, in opposed to that, provides us with a few
things like this state schema where once we define this information, so once the information gets
passed through as an input to the main graph, as an input to the graph, the same information can be
reused across the full graph. So when I say something like this, when I did graph.compile and these
were different nodes, and let's say I pass in an input as a user query to this load history node. So
this is like whenever I pass the input to this app, okay, this app graph.compile, whatever input it
receives, that input would be passed across this full graph, like all the nodes, all the
information. And what you can do is, like let's say at this particular point, what I'm doing here is
history text, you can see here, here as this particular function, I'm defining state, a rag state.
And in history text, I'm loading from my full this node, like this inputs that I've defined, I'm
loading this query, this answer, from where I'm loading this, I'm loading this from the state
itself, like state chat history. So this state, like if you know this context from APS, like
statefulness, state, that thing, so we're trying to just replicate the same statefulness that once
an input is received for a particular graph state, for that full graph state until it completes, all
the inputs will stay in the memory. So that is what we call it as a statefulness. And then we can
also overwrite certain inputs,

### [2:06:00]

like let's say rewritten query would be blank when we first pass the input query, but as soon as we
have some data for the rewritten query, we can just simply mention state rewritten query equal to
generate. Like so, whatever output is there for the rewritten query variable will be stored inside
my state. And the same value can be used across, let's say I'm in my node decompose. So I will not
need to separately, call this node rewrite query function or this rewritten query function from my
this state that I have defined, I can simply write this thing, this state rewritten query. So it
will automatically fetch the information from the environment for this rewritten query variable. So
this is one way of LandGraph's benefit of statefulness provides. And another benefit is that this
add node and add edges you see. So it kind of tries to replicate flow like this here in this PPD. So
here you can see like here like goes in a sequential flow then here there are two flows. So two
parts it can divide two. So there could be a case where no, you could have also connections like
this, like let's say entry point, then two flows from here, one node, another node, multiple nodes
coming through like this. So this kind of graphical structure is also possible with LandGraph. But
with respect to other libraries in generative AI, like Lang chain, Lama index, Crewe AI, Phi data,
this kind of structure is not easily possible as easily we do it with LandGraph. So even if you know
kind of we'll see on to Google or somewhere or even like a few of the job descriptions

### [2:08:01]

you might see. LandGraph is a kind of a framework that is repeatedly asked as an experience. So like
it gives a lot of benefits like this, like statefulness and this graphical structures are the two
main points that they provide. So like there's two main major differences it will provide across
the, in comparison to other frameworks. So main purpose is to use in data visualization and
analytics, right? All right, like provides a kind of more abstractive way to represent our workflow.
But in some way, can we show that graph on that notebook, the form of data? The notebook? Yeah. All
right, so what I will do is, like after the session, I will later on add the image in here. Like
when I share this notebook, I will share it with the image here. Anyone has any more queries? So
first in the rag architecture, first it search in the vector database, right? Then if confidence
level is low, then it will search in the web search, like search in the APIs or web APIs.

### [2:10:03]

So it is searching parallelly or it is doing like if confidence score is low, then it will search in
the web search APIs. No, if the confidence will be low, then only it will go for web search. If
confidence is high, web search will never be touched. Then suppose web search call is also low,
confidence score is low, then what will happen in this case? With respect to web search, we have not
added any confidence score as search because that is as I was mentioning, that is some sort of a
business call to make, that in case our system is not able to generate the response, in case can we
use web search to just give some related response to the user if we can. If that is some
possibility, so just to do that, we do a web search. In certain cases like if the main vector
database is not giving enough information, you could also omit web search like a business use case,
like if we do not want to provide any information, the LLM can also respond with that it does not
have enough information to generate the responses. Sorry, so something like that can also be done.
But in the web search, we are not checking the confidence score. We're just relying that our data
we're not able to do that, so maybe that can do it. Why we are using only SQL database, can we use
other database also? You can use other database as well. You can use MongoDB, anything like
Postgres, anything you can connect. As it was a Google Collab Notebook, so I cannot connect it to
Mongo or Postgres. Maybe I could have connected to Cloud versions, but all of you might not have it,

### [2:12:04]

so I just added SQL so everyone can run the Notebook. I believe we do not have any more queries now.
I'll just stop the recording.

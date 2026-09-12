# Current State of RAG — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy), Week 3: RAG —
> [Current State of RAG](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76590199-current-state-of-rag)
> · Live session recording, 97 min (`1:36:53`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> ten silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated from a live Teams recording with crosstalk and accented
> speech. Technical terms and proper nouns are the least reliable parts — verify anything you
> quote before building notes on it.

---

### [0:14]

Hi everyone good evening. So as you know today's session is going to be about the current state of
rag or as we know it's called as retrieval augmented generation. The most important thing we'll try
to look from the session is that why majority of the rag projects fail like we will not be talking
about creating rag system how they are built or we'll also not be talking about how to improve or
trying to look at certain methods or anything we'll try to cover different failure points in a rag
pipeline like at each stage of rag what kind of problems can arise what could be the possible
solution but how the possible solution can also put a negative effect to the overall solution so
we'll have a look at them as well and this will be more like a discussion discussion session
compared to like our previous sessions on like end-to-end codes or agent building sessions so I will
just open the mics for everyone today in between the session if anyone has any queries or anything
to share related to whatever we are talking please like you know feel free to unmute and you can
share your findings details anything so just give me a minute I will just open up the chat is
enabled I will just enable the mics for everyone so everyone mics would be enabled now

### [2:21]

so yes let's get started with the session right so what do we know about rag at this point of time
like I hope everyone is very cleared on to the basics of what is rag or does anyone here does not
understand the concept of rag please do let me know if we are not clear on that part then it would
become difficult into the little slides to understand why some problem is there so is anyone there
who does not understand the basic rag pipeline okay so mostly believe everyone does so you're not
going in depth just understanding how a rag pipeline works so basically we have two different stages
in a rag pipeline one is a knowledge ingestion pipeline and another is a retrieval and generation
pipeline so how this two differ is through the ingestion pipeline we add data to our vector indexes
how does the process go is that we have a lots of data that data could be either in the form of pdf
word documents could be there on html websites anywhere and from there we use certain methods like
chunking and everything so to create a proper flow everything in together we generate the embeddings
using the embedding models so we vectorize the text data and all and store it into our vector
database and whenever a user query comes in at this stage the retrieval pipeline kicks in it gets it
finds the nearest data that is available into our vector database according to the user query and
there are a few things like

### [4:25]

re-ranking the modern rag pipelines involved like re-ranking whatever chunks are retrieved from
vector database everything and then based on that context received from the vector database the llm
or the thinking engine generates the final response answer written could be right could be wrong
like depends on how well your rag pipeline has been defined right now here the problem that usually
arises is that even if the failures at each of these stages different stages are just 10% so let's
say even if every stage in the rag pipeline is 90% reliable then across this basic five to six
stages or six stages to be precise the overall reliability of the system can come down to only 53%
meaning let's say for a one user input query there has been a issue with re-ranking so it
automatically decreases the relevancy right so due to this there are certain issues with rag that
why majorly rag during the testing phase or small data sets works great but over time when you add
more data when we try to convert the rag systems to production systems they start struggling really
like you know in a production environment the rag systems has been seen to be the most useless thing
i would say from my personal experience as well in a lot of cases over large scale data rag systems
has not turned out to be quite fruitful and the struggle under real user traffic at real world
domain specific data as well so we'll try to discuss different parts going through the journey of
this rag pipeline like issues with ingestion chunking indexing retrieval re-ranking generation and a
lot of different things and also from the architecture

### [6:29]

point of view as well great so starting with the ingestion and index quality failures so like going
through the very root cause of any issue that can arise with any of the AI domain specific types
like machine learning deep learning latest in AI applications everything requires data so thus
everything starts with some sort of a source data and if this ingestion of source data is poor later
on in the stages of rag pipelines the retrieval quality automatically collapses right so in the
ingestion and index quality failures few of the most common issues first is like ocr based errors
hdmi artifacts that boilerplate noise in the source documents so it is very much seen that let's say
if you are working with some sort of a insurance kind of a data or some company specific
organization data it has been seen that there are certain things across the documents that might be
repeated a lot of times there is a lot of things that that is in like old documents formatting is
not there and due to that all over that no issues images are there we need to apply ocr ocr models
how well are they able to read it how they're processing the data causes a lot of issues
particularly with respect to the ingestion of the data so to solve this what it is usually seen that
people are using libraries like unstructured dockling or custom data cleaners over these documents
and generating the data for chunking but what happens is that this does improve the chunk quality
when we say but the overall issue that comes with this solution is that it is quite expensive to
maintain why expensive is because

### [8:31]

for different types of documents you would need to create different types of domain specific rules
for each document type right like you have pdfs too here tomorrow you would have word documents and
html pages so a lot of different document types according to whatever kind of now let's say this is
with respect to only one organization let's say you are developing a rack pipeline for multi
organizational data so in that case multi-organize each organization having their own setup rules
setups and everything so again the maintain the cleaning pipelines everything will also have more
number of rules to be included and this will pile up into a huge code that can be slow to generate
the chunks and everything so this is one of the major problems that happens always with the
ingestion side of the data then duplicate and near duplicate content so again across data it has
been seen that when we create chunks a lot of chunks from across the documents are created in number
of times creating near duplicate data so the solutions has been there multiple things like mmr based
indexing min hash indexing or setting up something like semantic similarity thresholds to handle
this near duplicate data they does reduce the retrieval bias like getting the near duplicate content
and everything but the issue would be that they usually add certain level of reduction into the
inference speed, and threshold tuning is yet not proven to be a good solution for this. They can or
work as a kind of duplicate removal techniques are there, but they do add a level of, they would
say, the speed reduction in the inference time. That issue, if your pipeline can handle or if you
are in

### [10:33]

a use case where the time to response for the user is one, two, three seconds or something, in those
cases, it would be very hard to maintain this deduplication indexes. Instead of that, what people
have started coming up with is that once the index is ready, vector in vector index, they start
implementing deduplication at that stage only before actually moving the solution to production.
Next, the index staleness, meaning when you have something like dynamic corpus, where your knowledge
keeps getting updated. In those cases, if you are adding data across, let's say, two days, three
days, 10 days or something, you have that. In that case, the problem would be that, I would say, the
real-time synchronization with the data that is coming in new would not be exist because those data
has never been added to the vector index. So more solutions like incremental indexing with something
like time-based approaches to add whenever there are a set of batches of documents has been
collected, you run the pipeline, so the idea is to keep the index reasonably fresh. But this near-
time or near-real-time synchronization of the data could be architecturally complex and continuously
adding the data into the vector index can put a load on the vector index, not only on that but also
you would have to maintain a pipeline or a server running that keeps running the cron job to add the
data. So that can also be an added complexity on top of your overall solution. The final part would
be multimodal parsing. First point was more about documents having a lot of things that cannot be
read properly.

### [12:37]

The last point is also about that, but it is more about during the PDF conversion. So there was
recently a very famous post on Twitter, Reddit, it was going across that. It was seen that most of
the document conversion libraries like PDF, Word, everything, one issue is seen that, let's say if
I'm parsing, there was one experiment done that if I'm parsing around 100 documents, data of
estimated five to 10 documents would be lost during the process. So there is a loss of data and we
do not know what data got lost during this conversations cleaning of the documents that happened. So
what better solutions was there? We identify certain structures in the documents and everything, and
based on multimodal parsing methods using vision models, Gemini vision models, we extract this
visual chunks, structured table data, everything to generate. But the main problem with this is that
they are quite expensive. The models that would be getting used for this, even if you're using open-
source models, those models are quite large. So to host those models into a local service, it would
be like you would need to have very high-end GPUs to run them. Again, either you pay for the token
cost or you pay for the infrastructure cost. But it is seen that these methods do apply and good
information can be extracted from the documents. But at a level of very high cost. The next is
chunking strategy. Now that we talked about ingestion issues and everything, like when we're going
to ingest data with a vector index, what things can happen. Now, let's say you're building a rack
pipeline and you are somehow

### [14:40]

able to solve the overall ingestion or what data you're pushing, you come to a solution like a good
reasonable solution. I would never say that you would always land at a solution in a rack pipeline.
It is always seen that rack pipelines fail miserably at every stage. No matter what you do,
something or some edge cases will always exist. So let's say somehow you reached a good level at
ingestion level, cleaning and everything has been done. The next part comes at the chunking
strategy. So lots of chunking strategies exist like fixed-size chunking, reciprocal-based chunking
methods, semantics chunking, everything. Each method having their own good things, bad things,
everything. So chunking in ideal case sounds like for a beginner, sounds very simple like you split
document into smaller pieces. But chunking, I would say is the major fact that will hold your
overall rack pipeline as a solution because a bad chunking meaning bad data quality retrieval
indirectly and thus breaks a lot of thing, no proper retrieval could happen and your solution will
again fail. So let's say something like a fixed-size chunking. The first problem that beginners tend
to use is fixed-size chunking. The idea is that we chunk based on n number of tokens. So let's say
you chunk based on first 500 characters, next 500 characters. This tends to break the semantic
units, meaning there can be a paragraph that is broken into two parts. Both the chunks are
connected, but they lose the semantic meaning when they were associated. So here as a solution, the
major approaches has been founded around the semantic chunking by splitting on meaningful boundaries
instead of character count. So the idea is to preserve context integrity by using semantic chunking.
But the problem would be it requires an additional embedding model

### [16:45]

to be used during chunking, increasing upfront vector index cost and also latency during the
preparation of vector index, meaning chunking with embedding models like normal document chunking
could take like let's say for a 20-page PDF, it's taking three seconds. Using embedding, semantic
chunking or embedding based chunking could take 10-15 seconds. So there will be an increase in the
time to create the chunks out of documents and the cost involved associated with it as well. Next is
chunk and embedding context window mismatch, meaning let's say different embedding models perform
better with different chunk sizes. So very small chunks lose context, very large chunks dilute
meaning. So chunk size selection also becomes empirical and domain specific. Like we have this very
famous problem with large language model is that lost in the middle problem, meaning the LLMs
usually tend to pay less attention to the information placed in the middle of long context. So here
I'm also mentioning like these two things are connected, lost in the middle effect. So let's say you
chose a big chunk. Now the chunks or tokens in the middle, they're given less importance in terms,
like it is usually seen through experiment, it is not a generalized concept. So what we tend to do
is like we reorder retrieved chunks by placing the most relevant, like when we have a lot of chunks,
we reorder the chunks in case of a large context. The idea would be that we choose the optimal chunk
size depending on what's the model capacitor. Let's say the model is a big reasoning model. So
reasoning models would be more better at figuring out what to look at from a chunk while non-
reasoning models.

### [18:48]

So earlier models like GPT-40, 401 mini, the non-reasoning models, they might start looking at the
paragraph or the chunk at the start and they say that, okay, hey, I have found my solution. I may
not read other chunks or other part of the chunk to generate the response. So in that case, they
lose the data. So that is again a problem. So simple re-ranking approaches, all those things can be
implemented, but it still does not solve the root problem that it only is going to provide certain
level of marginal improvement. It is still not going to solve the problem of loss in the middle
effect. Next is metadata poverty. So when you create these chunks, usually like again another
mistake that beginners tend to do is that we do not create metadata like sources, what date of the
document is associated, what section, document type, and this makes the filtered retrieval. Now,
filtered retrieval is again a very famous topic going around here that once we identify what kind of
domain the user is looking into, we use a small routing-based, LLM-based decision that let's say we
had hundreds of documents, we put it in a vector database and in there we specifically say that this
document belongs to this category, other documents belong to this category. So whenever the user
puts in a question or a query, we identify what is the category and we're only going to extract
chunks from the documents of those five or ten documents depending on the category. So the idea
would be to attach rich metadata during ingestion such as source, date, section, document type,
everything in together for a better filtered retrieval mechanism. It also enhances towards stronger
traceability and better citations but metadata schema design would be an additional effort. There
could be inconsistent upstream data like not all the documents would have everything that can be

### [20:51]

added as a part of metadata so inconsistent data and it could also reduce reliability meaning let's
say for certain document type you're not able to establish category like during the automation or
LLM losers or LLM misstacks a particular document as a different document type that kind of cases
can also happen like if you have thousands of documents no human can tag all the metadata across the
document so LLMs are heavily used for metadata generation but again LLM due to biasness
hallucination issues and everything can have issues during the creation of metadata. Next sliding
windows also tend to I would say improve context content. Now across different chunking strategy it
is seen that people usually add a sliding window meaning chunks overlapping with the other chunks so
a chunk continuity can be maintained but what happens is that it increases the context can have
useless information added to a particular chunk that might not have been connected to the chunk or
so many things can happen usually an additional extra information is added and that can also reduce
the quality of response. So now many systems use something like hierarchical indexing meaning store
summaries and row chunks and retrieve at the summary level meaning you have n number of raw chunks
we summarize it and we retrieve the summary and according to like when let's say during the
retrieval stage we find that these summaries are good so for those summaries we retrieve on-demand
chunks based on whatever summary document that we created so that is how and hierarchical indexing
approach has been in consideration I will say it is not yet totally developed like I haven't
personally seen

### [22:55]

anywhere that that sort of solution already exists it has been experimental many libraries have been
trying to add there is another one solution called as HYDE particularly a library is being seen but
haven't personally seen it working well or nobody I know has been using it across certain solution
that is working well so it balances context coverage with manageable index size but it adds two
level of retrieval here so adds latency so let's say if your solution was taking 30 seconds to
respond to the user it might start taking 45 seconds 50 seconds which can hamper the user experience
so depending on to the user experience and everything in consideration you need to also define how
this particular hierarchical indexing or how we are going to define your architecture next is query
understanding failures now the part that the data is being added the data is created the data has
been cleaned and has been chunked and added to vector database now the problem comes is that is your
LLM good enough or I would say when there is a retrieval happens is this all processes good enough
that they can understand user queries so what happens is let's say even if your indexing is good
your data is good everything is good but if the user queries are vague or ambiguous so let's say for
example user asks something like how do I improve this but improve what like what what kind of
improvement the user is asking for is it for revenue is it for accuracy or is it for a particular
document so the retrieval level information can be in sufficient context so it has been identified

### [24:56]

that there are certain techniques like query rewriting or expansion using an LLM before retrieval
like even before the user even before the retrieval pipeline gets triggered there would be an LLM
setting there that will identify like if there is any extra information that should be taken from
the user rewrite the query expand the query and then the LLM based on the user's additional inputs
merges them and then generates the or triggers the retrieval pipeline so it improves the recall for
vague and unspecified queries but it adds an LLM call to retrieval path which will again increase
the latency increase the cost of your pipeline and rewriting the query can also introduce incorrect
incorrect assumptions like due to LLM hallucinations that can be incorrect assumptions added to the
pipeline so those kind of problems will also exist then vocabulary mismatch between user queries and
document language so for example a very classic example I have seen users type heart attack while I
was working with a medical document the team has returned heart attack as myocardial infarction
right so there is a document like there is a mismatch between the languages of how the users will
use versus what is that in the document so how we tend to see since we start to move towards more
towards hybrid retrieval combining bm25 keyword search with lens semantic search retrieval so two
types of retrieval working in together even take a fusion of them and on top of that certain kind of
a re-ranking process and everything could be applied so they tend to capture both lexical matches
and semantic relationship lexical matches meaning keyword based matching and semantic meaning words
or synonyms capturing or data that is similar in terms of language in terms of meaning

### [27:00]

everything would be captured but they require certain algorithms like reciprocal rank fusion which
will again involve some sort of a algorithmic way you need to have a fine-tuned algorithm that can
maintain a good I would say what I would say during the process maintaining the flow like let's say
you have an algorithm you taken basic open source algorithm that open source algorithm might not
even know your specific domain you are working on so even if the algorithm is trained to do
reciprocal rank fusion or the other or the re-ranking on top of your hybrid search it can still fail
in a lot of cases because it also does not a domain loader so you ideally technically require some
tuning on top of that to maintain so that is again an additional process to be done like giving the
algorithm the knowledge of your data and everything that is to be also separately maintained then
multi-intent queries receive incomplete retrieval so let's say for example a user query something
like compare AWS lambda pricing and explain deployment limitation so there are two different intents
here one is pricing and one is deployment limitations so a few methods like query decomposition and
multiple retrievers like we split one query into multiple queries and on top of that we retrieve
multiple times for different queries and then we merge and rank those chunks that has been retrieved
so this method is very useful I have personally seen experience this actually works handles complex
and multi-part questions more effectively but it it would face problem like there will be a lower
like reduction into the inference speed sorry increase in the

### [29:03]

inference speed like let's say five seconds but it would be like something like 10 seconds
dramatically it would be increased just a slight increase like seven seconds eight seconds so it
multiplies the retrieval calls merging and ranking this results is not so difficult I guess in this
case so it is still going to hold up and I guess this method is something I would say that it is
proven and would work well so you can think of adding these things into your systems as a
consideration then the last point in the query and understanding is language drift dialect variation
of domain specific jargon meaning there is some expert that is chatting with the system something so
if it is a multi-language document or like if you're if you're working in some specialist domains
like legal biotech finance it is usually seen that there is a wide difference between the users who
are using there could be let's say some experienced people who use that terms into short form. They
ask the query in short form while the document do not have an analogy stored for what is the full
form for this particular short form anything and that can also be a bottleneck to a solution. So
domain specific fine-tuned embedding models have been seen as a solution and they tend to always
deliver more stronger retrieval performance in specialized domains. But the fine-tuning could be
expensive depending on your data set size and embedding performance may drift when the BS model
changes. Next is retrieval mechanism failures. Now the last slide was based on top of the query
understanding like how the embedding models and all understanding will happen but even if the
queries are reasonably understandable it is easy to interpret how or when would the retrieval
mechanism would fail. But before this any queries till now anyone who wants to share anything?
Nothing to discuss on this part here.

### [31:36]

Okay I guess a question for data injection can we use airflow? Okay so airflow can be used like if
you're going for certain like that airflow is architectural solution I would say this is not like
airflow would be independent of this like the solution part and everything like suppose that I would
say that is an architectural so decision to be made by the development team depending on how you're
solution architecting the solution visualization documents failure visualization of documents
failure you're going to say using airflow to visualize documents failure like I have both of the
points connected okay I have not seen anyone personally use airflow to visualize documents failure
would be a thing to check okay just give a minute okay I have a question for you associate what is
that so like are you trying to say

### [33:38]

like let's say you we are ingest ingest ingesting 100 documents and during that process we want to
see what document didn't get added to our vector database using the airflow ui or something like
that is what you are trying to say okay if that's the case then like that can be done with airflow
that's not an issue like the airflow ui and all can provide you but the problem when let's say your
full document let's say you had a 100 page document and in that two pages data was not properly
cleaned up or that could not be properly added up to the vector database so that thing could not be
actually visualized by airflow like you can only check at the document level that does this document
got added but what happened during the process inside the document for that you would need to create
some custom pipeline or something so we can take a look into that like that would be creating
certain specified custom functions and so on all right all right then let's move to the retrieval
failures so retrieval mechanism failures usually are more towards how the vector database you are
using or something so with respect to the query like this pass retrieval so you can connect it with
here the hybrid search mechanism which we created it so a normal pass retrieval can miss semantic
relationships while dense retrieval can miss exact keywords so the solution is hybrid search and
hybrid search has been now very common in all the basic rag setups because without them lexical data
exact keyword data semantic match data both can be missed if we are going to just use a sparse
retrieval or a dense retrieval so

### [35:39]

the idea will be to use hybrid search that involves both keyword based search and semantic based
search and applying a reciprocal fusion algorithm on top of that on top of the retrieved data or
retrieved chunks to formulate a final list of chunks so first we know that it's going to do lexical
precision with semantic coverage but it will require two indexes to be maintained one is like let's
say if you're using vm-25 algorithm for keyword matching then one vm-25 index would be maintained
one vector index would need to be maintained would require separate infrastructure separate tuning
and separate scaling of both so that thing needs to be maintained another issue is like there has
been certain things like if you're if you have experience setting up chroma db and all there has
been few search spaces like hnsw like a few parameters like ef search n prob and everything so
usually in vector databases we see that the approximate nearest neighbor recall loss that how the
vector database is defined depending upon the complexity of your data this the the way we find the
nearest neighbors that accuracy can be lost so we tend to have these things into solution like hnsw
vector space creation we increase these two parameters and what this is we get a better recall which
turns into better responses but what happens is that higher efficiency like ef search or n prob they
tend to search for higher number of parameters into the chunks which increases the latency and here
in this case if you're going for something like vm-25 index or something then it won't scale very
efficiently meaning at a very large scale this particular idea won't scale so maybe a little

### [37:41]

improvement on these parameters to increase can be done but that will only sort of know might be
giving you two to five percent of increase in the overall solution right next part fixed top k
retrieval either can produce insufficient context or very excessive context insufficient context in
cases where let's say you have the user queried something and that data is present or available in
like five chunks now your top case only three meaning it is only going to retrieve three chunks so
the context from two chunks is and let's say if you have k equal to 20 meaning there is 15 extra
chunks which adds noise which adds more tokens to be processed by the model so it adds cost and also
adds long longer latency to the response time so something more like dynamic k based on score
thresholds or query confidence so like top p or top k this kind of parameters can be uh like you
know little bit of tuned around a dynamic key retrieval can be included so it can adapt to more
better retrieval depth according to query difficulty so users minimal context for easy queries and
more for harder queries so like if it is multi-query multi-intent query set k to high simple query
set k to a low so dynamic k can be calibrated that way but the score calibration will be model
dependent meaning an LLM would be there to decide is the query difficult or simple depending on that
what should be the ideal key value and something so this model dependent score calibration is there
and this thresholds need certain also like it should not be that model would say that let's take k
equal to 50 or something so to add a proper

### [39:41]

threshold give the proper instruction the model is all also very necessary and query document
distribution mismatch meaning documents could be written very well versus the user query could be
very informal meaning this can also lead to very poor retrieval so fine tuning of the embedding
model your actual LLM model that is going to generate the responses is also two different fine-
tuning methods like embedding model as well as the LLM, both are seen in the process. So it is
usually seen fine-tuning both the models adds very strong improvements for domain specific rag
systems because they're going to add a factor of relevancy to the understanding of models between
how the users might query versus what the data is in there and improves the answer query quality in
the end. But it requires labeled training pairs, you need to create the data set, you annotate the
data, the data preparation will be time-consuming, there will be human experts who would check the
data quality and everything and then you fine-tune the models which might also take time depending
on what is the size of your data and everything. So could be expensive and time-consuming to create
these things. Then, yes. So let's say absence of recency bias, like there could be documents that
are getting updated at regular intervals but what happens is that, let's say there is a document
with 20 pages, document got updated, you ingest that new document, let's say it had only two pages
of updated content, the other pages are still the duplicated content. So it adds issues because it
could be that the older document could, the vector database can retrieve the data

### [41:41]

in order of like older document comes up first, then the new document, so new data chunks are listed
lower into the retrieve, top key might miss that and in all of the process, you would lose the data.
So something like metadata filtering based on date combination, which can identify for this
particular document, what is the latest version, what is the date and everything. So that kind of
solution can be maintained. Now, it makes it very relatively simple to implement because we are
going to be more about what time a document was updated or if a document was re-ingested. We already
might have that as a part of metadata. So based on that, we can do something like latest date-wise
filtering or something to get the latest fresh relevant results with minimal duplication of data
around it. But we would need to design this extra function and there could be a risk of, let's say,
down-weighting certain important historical content. There could be even cases that sometimes the
user asks certain questions like, let's say, compare the new document with the old document. So in
that case, there could be a failure that we need to specifically get all the chunks that were
different among the same document updated in the old document and maybe the metadata filtering might
miss or something could happen and that historical content can get lost and LLM will generate a
wrong response. So something like that can also happen. And one of the main problems with respect to
the rag, the multi-hop queries, like a response to one query could be present across different
documents, across different chunks, across different pages everywhere. And it is usually seen that
we do not have any multi-hop,

### [43:44]

like considering this one chunk, other chunk, other chunk. LLM has been very inefficient to work on
problems which involve multi-hop queries. So technically with the latest models, like reasoning
models and everything, this issue has now been getting solved a little, but still not the best. And
the solutions right now that exist for this multi-hop queries is that iterative or agent-reg where a
particular model reasons among itself over the retrieved data. It takes that if the things are good,
if not, then do another retrieval for finding maybe another better chunk or a similar different
chunk that can answer the query. So retrieve reason, re-query, and repeat as per the need to fulfill
the user's response. But latency will increase with every hope. When should we terminate this
particular loop of repetition process? Like how many times to do it, how many times? So that kind of
loop control should also be maintained. But the benefit of this is that handles very complex
reasoning chains and finds connected evidence more precisely. So better answers for multi-step
questions here. When cross-lingual retrieval quality degrades in mixed language corpora? So again,
this is we have already discussed. So what we tend to use is we tend to use multi-lingual embedding
models or so. So they're going to provide more reasonable retrieval across languages like right now
these days, we have a lot of models from Google and all. They allow multi-lingual models. But these
models are usually seen that they're not the best models for each of the languages. They have their
downsides that you could either have the best of the English embedding model versus an English
embedding model

### [45:45]

that works around with 80% accuracy, but also supports other different languages. So there could be
quality gaps for lower resource languages within a single language could have decreased accuracy or
something like all of these different issues with respect to the accuracy of the model could be
there in a multi-lingual model. Then off-topic but semantically similar chunks. So let's say query
something like how to reset my router password. It can retrieve chunks like router configuration
guide and also it can retrieve something like encryption guides, security-based practices and all.
So off-topic, semantically similar sounding chunks and all can also reduce the chunk relevance that
has been extracted from the vector database and the LLM, if it hallucinates, if it gets a lot of
context, gets confused, can generate a very wrong answer. So a relevant score thresholding with a
particular, like identifying what threshold would be the best for our domain specific use case.
There is no specific domains for all the use cases. Sometimes it will be 0.9, sometimes it could be
0.7 or anything. So a threshold set would be very identical thing here, ideal thing to do here. And
like very low confidence scores below the threshold would be removed based on irrelevant evidence.
But this threshold calibration, as I mentioned, is quite fragile and legitimate, like proper execute
queries may be incorrectly rejected. So this could turn out to be a very bad user experience with
this inconsistent behavior rejection or no good response when the LLM generates. So these things
like with respect to threshold handling

### [47:46]

will always be present. Then context assembly prompt construction failures, meaning like you
retrieve the data, now you would have a system prompt, you would have context engineer, like we also
saw during the previous sessions, like when we took the context engineering session. So in that,
with respect to rag, how we get the data context from different sources, we merge all of them
together into a prompt and everything in together is something we already seen. So the most basic
issue is context stuffing, like we can either dump a very large unstructured blocks of text into
prompts, but the LLM will struggle to identify important evidence. So the idea would be to have more
structured prompting like clear sections, source labels, citations, separated blocks and everything,
like in the proper structure, like you can have a for loop to create this kind of formatting
structure when added as a part of context as a prompt. So it helps LLM process the data more
efficiently, but the template performance can vary model by model, like even a model upgrade or a
version change can impact the model. So changes in model can require prompt updates, okay. Then it
can also be seen that contradictory chunks are passed without conflict resolution. So we do not
control what chunks are retrieved from the detail. We can best max try that N number of chunks or X
number of chunks are retrieved from the database, but we do not tend to check that if all the chunks
are good or not. So we tend to apply a re-ranker or an LLM based certain sort of conflict detector
where it removes a particular conflict or removes certain type of data that might not associate well
with the user query. So using that, we use this method to explicitly

### [49:47]

give important to certain chunks or others and only pass relevant context to the prompt in
inevitably to the LLM to generate better responses. But again, ads, latency, cost factor, conflict
detection can itself produce incorrect judgment again again as it is a part of LLM-based methodology
can produce incorrect generates so the chances are there we are adding more steps to the process but
also are increasing the chances of more failure at that particular point as well so that can be says
that certain chunk might be important but the LLM says this is not important remove it so that kind
of cases can also happen then attribution loss occurs when source metadata strip before generation
so let's say sometimes metadata level information is being removed due to let's say there is a limit
to what kind of information you can pass in as a part of a prompt so sometimes people tend to strip
metadata or something in a lot of things so during that process if some things are missed metadata
is not passed that can also create an issue for the model to understand certain things so pass
metadata also as a part of the structured annotations alongside the retrieved chunks and prompt
templates now we discussed that the prompt templates needs to be changed across models but prompt
templates can also change depending upon user query depending upon whenever you add new data
depending on new edge cases and everything different models and everything so prompt templates
should also be continuously like under an iterative cycle so let's say every a few months you would
go through a process of finding better models in the previous to increase the user experience or
something so during that process it is also very important to

### [51:47]

go through a cycle of prompt engineering iteration as well identify for what kind of prompt works
best with a model if a single prompt is there can that single prompt work with the base model and
also the fallback model and everything let's say open a model service breaks and the fallback model
can also work with that prompt everything you consider and based on it you select a particular
prompt everything should be identified so what it also is that during model upgrade or anything
model changes or whenever the fallback model is running that kind of during those kind of
regressions the accuracy of the systems can be maintained but the testing matrix that you would need
to like the testing team would need to expand like what supported model they are going to support
you would need to identify what model what particular like are you going to support open source
models are you going to have only open a anthropic based model so all of these things to be
considered and then you develop a table for what all things you would need to test upon then the
generation side failures of the solution like you have your can you please explain about p uml from
microsoft okay we'll take that as at the very last not an issue so yeah coming back here now that we
talked about in data ingestion data chunking cleaning everything query understanding before
retrieval after retrieval failures and everything now when llm is going to generate the final
response what kind of failures happen so it is usually seen that

### [53:48]

llm sometimes tends to fill evidence gap with hallucinated detail so even though there is something
available in the chunk the llm might not if it is not able to understand that or there is a language
like from the previous slides you can think of n number of things can happen when the llm is reading
the retrieved data versus the user query and if llm finds something is missing and it fills that
with certain hallucinated details that that is something issue for the final user because they will
get incorrect details so idea would be that you use a reasoning model that cites the sources and we
also explicitly state to the model that you specifically say i do not know when there is
insufficient evidence and the reasoning models these days latest ones are seen that like if they do
not find any suitable evidence they are very reliable and they do say that they do not have enough
information to generate the response so one thing better would be that let the llm know that if it
does not find any relevant details just say that it cannot fulfill the user query it reduces
hallucination rates up to a certain level and improves answer reliability but enforcing this
consistently at interference times cannot happen models can still hallucinate can still generate
unsupported claims those kind of issues will still stay relevant then in the instructions that you
stated right so could be lots of instructions could be less number of instructions but if you are
have a long context lots of instructions it is usually seen that a large language models if you
let's say have 10 instructions next time you add 20 instructions it is seen that llms do not tend to
read all the instructions and work on top of that so idea would be to repeat critical instructions
near

### [55:49]

the end of the prompt rather than relying only on the system prompt so this is one way that has been
seen to improve the instruction following capability of the models but they still do not address the
root cause that is like why the model do not see or follow certain instructions or something losing
the text that is presented the middle and everything and it is also going to increase token usage
due to the repetition of certain information during the prompt again and again then again another
issue another issue where llm assumes certain incorrect things so for example user ask certain
questions so this is like something kind of no like we have seen some issues like jailbreaking
prompt or something where people tend to use prompts in a way that it can confuse llm so like input
guardrails and everything to be set up like and also on certain side of adversarial eval suit like
questions that can lead the llm to generate incorrect responses or so so in those cases you create a
test bench for that as well something like and when should the llm trigger refusal behavior or fall
back so that kind of an input guard rail setup if it is there it would be much more better then
coming to the latency and optimization side of it so now if if we go back and think on all the
previous slides one of the main components i have been consistently talking about is that the
latency always even if you do something here and there latency increases latency added this that and
everything right so like when you develop a very complex rag pipeline latency will be there so idea
will be that wherever you can add a synchronous or

### [57:54]

parallel retrieval parts along with your pipeline it is going to lower the main wall clock time
reducing the retrieval but this level of complex orchestration or identifying what things can be
executed parallel that could also be at sometimes you can get stuck in a case where there is no
chance of any parallelism to be involved so that thing can also happen then you add caching like
semantic caching semantic caching we had one of the previous session where we discussed something
like redis lang cache and everything we can have so this kind of semantic caching or other side
other sides of caching they can fail in dynamic or personalized corpora like even though like let's
say there is certain similar question user is asking but the way the model understands two different
words separately there could be a difference in intent or something and in that process the semantic
cache cannot happen so even you if you have added the cache part there sometimes the whatever cache
mechanism you added can miss and can have the model repeat the process so ideal case like it would
lead the query as a new query generate the response and everything all together so again just
involvement of cost will be there but the answer if it finds correct retrieval and everything the
response will still be correct the user experience will not degrade but the user might take certain
time to get the response and also one of the important parts p99 latency also what is this p99
latency right so p99 latency is something you think of like let's see in terms of software if i have
to say we like

### [1:00:01]

even in software EPS or something that 99th percentile of response times in a computer system or an
API. So that means that 99% of requests resolve at a value faster than this. So to achieve something
like this ideal case, what most people do is that we people try to go for something like have a test
bench, we check for the latency, we run through in particular pipeline everything but we really do
not define what kind of cases we can generate good responses quicker responses versus so let's say
you have thousand documents multiple categories you have multiple vector index and everything
incurred there. So ideal case would be to find if your system is hitting one vector index or if
you're hitting multiple vector index so across all this permutation combination of matches you
calculate the latency across all of them so you when when you are at the debugging stage or where
there are customer complaints and everything you know for what kind of categories of data there is
latency and versus what so let's say you identify that this particular category has always been less
latency but suddenly somehow it's now into the higher latency side so you can try to go and debug
only for that one particular vector index or one side of the pipeline so helps you debug much more
faster and conduct load testing it good like the testing team can also work quite well upon top of
that so produces honest and product production relevant performance because it is really seen that
the developer team can say that we can generate the responses under two minutes they start the
testing and does all the process and n number of documents have been added and then when the

### [1:02:03]

stakeholders go and test it they identify that the response time is five minutes because the
developer team never cared to check outside of the testing bench so something like that can also
happen so teams usually as I said often delay this work until production issues start arising so
it's always better to start checking it before actually releasing it into production the next part
is the evaluation and observability failures so again as similar to the other domains of ai like ml
data science everything evaluation of whatever data or processes you are doing is very important so
in many cases when you design a test bench no ground truth evaluation data set is available so what
we do is we generate synthetic evaluation data using llms with frameworks like ragas or llm as a
judge and why we do is we tend to be more cost effective to bootstrap the evaluation stage but what
problem here is that llm generated evaluations in they introduce their own biases in the input data
set and everything and whatever proxy data set is generated without the human interference or
without any human cross checking they might give better score but it could be a possibility that the
llm due to its over added biasness added questions responses and everything is tending to say that
this is a good response but in reality the user might not be satisfied with that response then other
evaluation problem could be that retrieval and generation are evaluated in independent sources so
there is a very classical scene that the llm is generating a bad response but people do not ever
check for if the retrieval quality was good then we tend to check if the retrieval quality is good
but we people do not check the generation pipeline so interdependency between the two that checking
both of them together that

### [1:04:09]

let's say for one query retrieval is good why generation is not good if the retrieval is not good
obviously the generation would not be good but if let's say retrieval was not good generation is
good so just to check if llm is hallucinating at that point is it hallucinating why is it
hallucinating well and if you can improve the retrieval so both to be tested independently and as an
interconnected source is also very important so identify failures at important component level
evaluations should never be missed and certain human level interference should always be there at
each of the stages of rag pipeline i would suggest because there are many stages here and evaluating
all of this should there should be a domain expert team to cross check and cross verify all the
things and also important thing is that no feedback loop usually exists from the production stages
so like right now i guess majority of the people have started involving feedback loops and we all
know about feedback loops i'm not going to discuss on top of that but could be that the users might
give wrong or false signals so identifying whatever user tags as wrong response in the feedback loop
or something before putting that as a part of fine tuning process for the model or the pipeline you
should also consider checking that if that particular user annotation is correct or not then
production gap meaning there can be like developers usually tend to think from something like let's
say they will check at the library they will say that okay we have context relevancy scores and xy
things all the matrix are check it is performing good but from a stakeholder's perspective or from
the marketing team sales team they might have certain custom kps so this custom kps and all might be
missed certain level of human evaluation stages can be missed so this particular custom matrices has
to be involved in the process based on the stakeholders requirement everything so

### [1:06:09]

that we can improve the evaluation results with real world expectations right but this process could
be slow and expensive because that has to be not only performed consistently continuously but
certain level of human inputs kpis certain level of knowledge outside of maybe you know what the
development team may know may not know has to be involved so sales team marketing team sales
stakeholders everything might need to be involved during the process then the systematic and the
architecture failures particularly so issue with this is that many organizations sometimes tend to
use monolithic pipeline for the overall rag setup but would be more better if you have multiple
databases multiple agents rag agentic rag pipeline everything it would be more better to have
routing kind of a query layer that classifies intents distributes to multiple vector indexes and
everything so each pipeline can be optimized for that particular specific query class so idea would
be to separate out as a microservice architecture at the oral rag pipeline i'm not talking about the
infrastructure cloud setup those kind of monolithic pipeline microservice pipeline but to distribute
create independent sub rag setup sub vector indexes to split everything but we will need to add a
classification step and incorrect routing can also turn out for poor response generation so a
separate routing layer routing system should also need to be maintained here in this case and when
the retrieval fails the output guardrails should also be into consideration like a fallback method
fallback mechanism what to response how the lm should response not a plain i don't know response
should

### [1:08:14]

be given a particular user satisfactory response like a follow-up question or acknowledge the limits
of the system should let those kind of fallback messages should be there so gives a better user
experience but like the output guardrails that you have developed how good the guardrails are and
all that also needs to be specified verified separately prompt injection by the users again
malicious content in the data or whatever data that has been added to the vector database that
particular database has not corrupted and everything should also be taken care of so this is all
about corrupted data injection corrupted issues like how whatever different agents or systems that
can be involved and cold start issue like whenever your vector database setup and everything like
whenever there is a user queries there if you have let's say very small corpus like you are just
putting as a beta solution of your rag and is everything is passed into production the user will say
that due to a very limited corpus the user do not get all the information so despite you say that
your system is designed like currently designed at a better stage or mvp stage the user might be
expecting more or something so make sure that you cover little to little cases of every solution so
whenever you're putting into production or something you have highly curated data and everything so
the user experience will be better due to a good retrieval coverage even if your response gives only
a little information of the state but the user can still be into consideration that the system can
be improved and later versions of the system, it can be improved further with more number of data
additions and everything. Now, talking about the,

### [1:10:14]

now we've talked about all the stages, like from ingestion, chunking, data cleaning, all the parts
to retrieval stage, generation stage, and finally the architecture point of view of the Rack
pipeline. But what still does not work today or what exactly is working out of all the methods we
talked, we talked about latency and everything. What works today is a simple hybrid retrieval plus
the ranking most reliable base setup of a Rack pipeline. This is something you should not miss.
Metadata is chunking again, another meta import metadata level filtering is very important. And
evaluation pipeline should exist for all the independent component in the Rack pipeline. If you do,
if you miss anything from this three, there is very high chances that your Rack pipeline will have a
below 70% accuracy. Like I have seen Rack pipelines that achieve 30%, 50% accuracy altogether,
because there has been lots of X, Y, Z things going here and there. So these three setups, you
should not never miss, should always be part of your Rack setup. Other parts, depending on to your
latency, use case and everything, your complexity of the solution, your infrastructure setup
requirement, everything, based on it, constraints and everything, you should add the other
components. But what still remains unsolved is the multi-hop reasoning. Multi-hop reasoning is still
unsolved. Like every hop is going to add latency and everything. There does exist a few solutions
around graph rig and all caching to handle all of these things at a multiple level, fetching more
context across different data sources, combining them together as a context to solve this, but still
multi-hop reasoning at a low latency is not yet solved. Then truly dynamic corpora without retrieval
lag, meaning continuously indexing for large scale updates in real time without any sort of lag into
retrieval process.

### [1:12:17]

It is still not possible because maintaining a pipeline for data ingestion in the same vector
database and using the same vector database to generate the retrieval. So there are a few solutions
around that. We have two versions of vector database, one to update. When you get the updated one,
replace or change it with the one that is being used in real time. The next version of that,
maintain a copy of it separately and then start updating on top of it, will create a lot of issues
or confusion around which replica to maintain, which to update, which to delete. So could be an
infrastructure issue, like if the developers, the cloud team are not in sync around all the process.
And hallucination prevention is something I would say will always persist. You would never get a
good rag pipeline that would be 90, 95% never seen any pipeline. If you have a very small base like
10, 15 documents, you can achieve something like that. But over a large scale rag solution, good
responses are very hard to find. And cross model retrieval, like you have text image table, we do
not have good rag setup, which can handle all the data sources in mix and match across them to
generate good responses for the users. So that is also another problem that is usually seen. So key
takeaways from the session. So we understood that rag systems fail because every stage introduces
independent failure. Production quality rag is not just about embeddings, models, capability, or
vector database, but it requires a lot of data engineering, retrieval engineering, prompt
engineering, evaluation guidelines at terms, observability and systems architecture, or everything
working together. So like dynamic or parameter of queries,

### [1:14:17]

as we discussed, is a very relevant problem that might not be solved very easily. So you need to
figure out certain solutions to handle it up to a certain level, add more, better fallback options
and everything. The address, architecture, they all matter. But after adding all of that, the
latency increase and everything, like depending on the user experience, all should also be
maintained. So at the very end, I would just say that the most important takeaway I would say is
that a fluent answer that might be generated by rag pipeline might not always be the correct answer,
but also to generate a correct answer using a rag pipeline might not always lead it to a good user
experience. The more complex the pipeline, the more issues can arise with the latency. So yeah,
that's it from the session. Thank you. We are open to questions from you guys. Please shoot your
queries and I hope to answer them one by one. Okay. Please go ahead. Anyone has any queries? If not,
then I will take some of the queries from the chat. Yeah, Malar. Hi, Jayak. Am I audible? Yes,
you're audible. Yeah. So first of all, beautiful session. Thank you. Nice to have one place to see
all the failure modes in the rag pipeline, because many cutting through the noise is very difficult
these days from Twitter and all the internet. So very childish thought. If vector is essentially the
problem at the heart, why can't we just drop the vector and go back to our traditional proper data
engineering thing, building a proper data warehouse,

### [1:16:19]

making things like good documents, markdown documents are really working well, HTML documents are
really working well with the models, even open source models. And also the part of the second
question is that we have something called as pageindex.ai, which has come up, which is popularly
advocating for vectorless rag. So have you used that? And what are you seeing the pattern is that we
might have gone too deep and we have bet on vectors too much rather than simple data engineering. So
true, so true. So with respect to vectors, pretty right. You're pretty right that I still believe
even after, if we are still find solutions to multi-hop queries and everything, all of this around,
I still believe rag will not be ever a solution or will not be able to achieve 90%. There won't be
any generalized solution for rag out there. Next part, for the vectorless rag, like you guys were
saying, pageindex, I guess there are also hashindex and a few other solutions out there in the
market on to get updates states for vectorless rag. But the only problem I have seen with them, I
have tested it and I also taken like a few of my fellow developers who tend to develop similar
solutions around. I asked them, I connected with a few people also around on to Reddit and LinkedIn.
It is seen that they're much more slower when we're operating them on a large scale data. So they
tend to create a very large documentary for all the multiple documents in that process of finding
the best documents and everything. It tends to slow at a large scale. For a very small scale,
vectorless rag might be better compared to vector,

### [1:18:22]

maybe around 100 documents, 50 documents or so. But if you're targeting for very large data source
rag, the vectorless rag is much more slower compared to vector drag. Got it, got it, thanks. So the
latency and the size of the data matters to choose whether to go ahead with vectorless rag or not.
Yes, and usually what I have seen in all the rag projects I worked upon, be it in healthcare,
finance, anything, everyone, all the stakeholders require only one thing, user experience. User
should get answer as early as possible. Now you create a rag problem, let's say we're going to take
30 seconds, stakeholders will never be happy over five seconds. Some might even complain that why
we're taking more than two seconds, but explaining to them the world process, the hard process of
getting the good quality data to generate the response, that is something also very tricky to
explain to them. But yeah, these things will exist. That's, I don't think like user experience
should always be at the priority for the marketing team, sales team, everyone. So there is nothing
we can change on top of that. Right, now there are a few queries into the chat, right? So one query
was taking this first, POML, right? So POML is something like, we have this markup languages, right?
So, Something similar to in, let's say we are in Lang chain or something we used to create prompt
templates and all. Similar to that, you can think like an HTML or the latex languages we have. This
is also kind of a language, I would say markdown language that has specific rules like you can
define the content from image inside

### [1:20:24]

an image tag content from table and inside and table tag. So it is just acting as a context
engineering language even without using POML. You can develop your own custom template language for
your use case. That is like independent like Microsoft has just launched that as an idea case like
as a markdown language. If that goes like if everyone start using that, I believe POML might turn
out to be the base markdown language for all the LLM. If all the LLM providers agree to use that as
the base language of it. So we're trying to build a rack in a 16 GB GPU machine just to show as a
proof of concept to leadership team. Can you recommend me the models which we can use? I need the
rack system to be able to learn images too. So in that case, three things I would say you do please
consider. One is as a POC, are you supposed to use open-source models? If yes, then in that case,
open-source models are usually seen to be not that good with domains. So I would suggest for POC, go
with an closed-source model, bigger models from OpenA Anthropic. After that, you can convince the
leadership team. Maybe you still want to use open-source models, then you would need to add some
fine-tuning for open-source models for domains, specific use cases, and all. I guess if you're
speaking something, I'm not able to hear you actually, Mahadev. Okay. Am I audible now? Yeah, you're
audible now. If I go with OpenA Anthropic model, can my 16 GB machine be able to run that? Yeah, it
will be easily able to run it. Okay. The additional question was about images.

### [1:22:26]

So in that case, you would need to use models, or you would need to use something like, if your
documents have a specific structure, that images will be always present at those stages. What you do
is break it down, like images and the associated text with it. Apply an image embedding model on top
of image, convert that to vector, and store it in vector database. There is one way. Other way would
be, do you need to send the image back into the user response? No. Just say we should be able to run
some images and give the answer in text format. Understood. So I guess that should do for you. Use
image types embedding models, embedding models that supports embedding images, use that which embeds
image and text both, and that should be sufficient to inject image knowledge into the vector
database. Okay. Yesterday, there was a news that Gemma 4B model Google has released that can run on
16 GB machine. It's multi-modal. Do you have any idea on that? Just a minute. Gemma, what 4B model,
right? So, okay. Here, what the issue is usually is the 4B. 4B model, like whenever you are going to
see the model parameters. So how do we see Gemma 4B, Gemini, let's say 100 billion parameter model.
So usually the models which have higher number associated with it, 70, 100 or something, they would
be more intelligent compared to smaller models. Now, it could be that this, the model you're talking
about that could run into a 16 GB GPU machine, but it might not be intelligent enough for your
domain. If you have something very custom domain that it might fail to generate the responses

### [1:24:28]

versus some very big models like the OpenA's latest models are around, I guess, into over 100
billion parameter model. They would be more intelligent and might be able to generate better
responses. So for POC, I would still suggest to be on a safer side use bigger or larger models that
can easily run into your systems and that can be accessed by APS. Do not download the full models
like 20, 30 GB models that will further increase the latency like 16 GB GPU machine might have good
latency. Like if you're using three billion parameter model or four billion parameter model, it can
easily run those models. Since here data is confidential, I cannot use the APS. Understood, okay, so
in that case, I guess your best chances would be to use three billion to four billion parameter
models. And for that, I would suggest you go to OLAMA, pick up the latest models between DeepSeq,
Quen or Gemma. Only the models from these three might work best for your use case. Okay, okay, thank
you, thank you so much. All right, is this session going to be available later to you? So all those
who are part of the TMSE Academy, like who have a subscription to that, they all will get the
recording of it along with the PPT as well. So if you're part of it, you will get it onto the LMS.
If not, I can still share you the link to the TMSE Academy. If you wish to enroll, you can enroll
it.

### [1:26:31]

I'm sharing the link here into the chat. Sushil Pal will explain for you. Okay, thanks Sushil Pal.
All right, any more queries? I'm sure, this is Sathish here. We just saw the latest news about the
Anthropic Colts, which calls for possible global AI development. Is that something, is it normal?
Like if these models are used in the co-pilots, now if such things happens on the enterprises, so is
there, these things are, how you will see this? Just I based, this is actually from a fifth of June,
I saw that in the news. Pause for global AI development, right? So I guess the call for pause has
been for over two years now, but no one seems to pause it actually. Which we are just entering into
this world, but is that we have any, what they claim is it escapes the human control. So is there
this kind of restrictions, whatever it's all inside the framework, right? If they provide, it's a
human in loop, if you decide it cannot do, we are trusting that, is that right?

### [1:28:33]

So one thing for sure is the models still do not have any intelligence of their own. They're just
following patterns from the data from a mathematical perspective. Now, if Anthropic says that we do
stop the process of the AI development or slow down the process of the main models, I do believe
that is because of the cost involved in continuously updating the models. Now, what has happened is
in the previous last one year, the model updates, whatever has happened has very, like the increase
in the accuracy or the response quality has been very minimal, like 90% to 92% or so. So like in
certain cases, like the coding, the coding models have improved immensely, but the standard models,
I do not see anything that has improved very drastically. So I think there is pauses would be from
the point of view of cost involved in creating, updating the models versus the chances of this
models becoming intelligent on their own. I still believe that there would be inter... to newer
stages of models, like a Transformers model that was created by Google as the base of all these
models. I think that technology is now dead. There is no improvement on top of them for the large
language models to have the human thinking capability, the AGI or whatever we claim, that thing
would not be controlled even if you pause it. So someone might come with a very altogether different
algorithm that might be able to achieve this. But I don't think like right now we have any case for
that. Okay. And if I request you to go to the slide which you've shown the last slide before the key
takeaway.

### [1:30:34]

Okay. Can you show that one before the key takeaway slide? How it works today? Yeah, what works
today? So here what you are explaining, maybe I was a little bit confused about this one just to get
clarification. Like the point one is the important one here about the hybrid retrieval. Like it's
normally in the picture, it's a semantic search. Say for example, if I want to search, my example is
I want to retrieve a particular specific ID. So is that going into the semantic search or it should
not bring the nearest IDs, right? No, it will be a combination of both. Keyword search, semantic
search, both. We extract data using both. And then we use a RRF algorithm, meaning we remove
duplicate content from both the indexes and we just have unique data. So let's say this gives me
five, this gives me five. We get 10 chunks for the LLM to respond to. And on top of that, the
reciprocal fusion model, like it will tend to reorder them whatever at the best according to user
query to generate the response. And we tend to remove the duplicate content that might have been
captured by both. So that is how we are going to use them parallelly. Oh, okay. So that means it
will do duplicate search for a specific ID. So the BM25, what you are saying you predicted here, it
is a keyword search and the semantic search, it will bring the next to possible nearest search. So
both may have a duplicate and that too filtered by this RRF. Okay. Yes, correct.

### [1:32:36]

Okay. So this is the working model what you trying to provide. This is the way for improving the rag
systems, right? For the quality. These days, these three methods would be like, the least set up
that we should do for the rag. Okay. And these, another question is on the evaluation or observation
side, is there any way we can track through the dashboards or something about these evaluation? How
the, because I don't know, could not able to understand how the prompt, because what we give the
prompt as a query and the results fetched as a prompt to the LLM. So that means it is a one complete
solution, one complete question and the queries and the responses goes as a prompt to the LLM. How
we can evaluate using a normal dashboards or something? Understood. So you can search for something
like this, like the pipeline tracing or something, LLM pipeline tracing. For that, we have certain
tools like ML flow, weights and biases, certain things like comets, like OPIC, O-P-I-K, there is one
product. So they're all like free versions available, paid versions available and everything. So
what they do is like, when we code the rag pipeline and everything, there are a few additions we
take from this library's frameworks. And what they do is the oral pipeline, from the user input to
the LLM's final output, whatever internal steps it has taken, this library store all of them
altogether onto a dashboard. They provide UI for capturing all of that. And the evaluation things
that you do, you just add code for evaluation and whatever numbers you get,

### [1:34:37]

you push that to the records onto the dashboard. So you will get the dashboard with all the
information associated with the pipeline. So you can look for something like this, a LLM pipeline
tracing. So what is that one? I will just, can you able to type here in the chat about any one of
the methods we can try that? That will greatly help actually. This is, okay, thanks. Thanks, Jirag.
Jirag, and one more query from last week, I just requested about the workflows or agents we want to
create using a copilot, get up copilot, we are trying to use it. So I sent a text or the WhatsApp,
so you could not find your available time. So is there any, is there a Monday you will be okay based
on your time? I can check. My month is tomorrow, right? Yeah. It will be a Sunday for you? No, no,
it's, we are in the same time zones, but only five and a half hours behind. Okay, Monday. What time
would you have five hours behind me? Yeah, four and a half hours. Four and a half hours. For you,
does 12 p.m. or some, for you works? Yeah, works, that's fine. Evening for me. Whatever the time is
comfortable for you. All right, fine, fine, sure works. So I'll just share you a Google Meet link.
Okay, thanks, thanks Jirag.

### [1:36:40]

Thank you so much. All right. Mahendra, okay, fine. Let me just stop the recording. Recording.

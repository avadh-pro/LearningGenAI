# Building Conversational Business Intelligence Agent — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Building Conversational Business Intelligence Agent](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76727400-building-conversational-business-intelligence-agent)
> · Video lesson, 81 min (`1:20:40`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:01]

to confirm if my screen is visible. Audio is also properly audible. All right, perfect, thanks.
Right, so today's session, we will focus more towards certain practical aspects like for the past
few sessions, we saw a few sessions that were like theory plus code heavy in both the terms. Now, in
this particular session, we're going to focus more a little bit on to the code aspect, like we know
a lot of architecture part, we know a lot of memory and other parts of the agentic structure
architecture. So today's session, we're going to have a look at what we call as conversational
business intelligence agent. So essentially, we're trying to create a system that allows user to ask
questions about business data, like internal data in plain English and get meaningful answers along
with certain charts if possible. So without, like for a person, like if I try to understand problem,
there will be a lot of teams that have their internal dashboards. Now, if they want to customize,
someone from other team might require that to update that particular dashboard or something. So that
is essentially the problem that we're trying to solve it via having an agent that fetches the data
from DB and pulls the data, identifies what kind of chart can be created and returns back a chart as
well. So now there will be a few challenges here, like the challenges, like how do we convert
certain results into something visual chart or something like that? And how can we, as we're also
moving towards the very last phases

### [2:02]

of the cohort, that how the deployment and all the stages would also be done. So we'll focus more
also, but on that, like the FastAP Docker part and how do we connect that as well, instead of just
going and having a look at the agent, we'll also have a look at those aspects as well. So at the end
of the session, we'll understand what is conversational BI, why it matters, certain real world use
cases where conversational BI right now is already getting applied. The architecture behind the
conversational BI system, how the system automatically generates charts from the data. Now there is
a few tricks around that that we can use LLM to generate the overall graph, create a code sandbox or
have certain templates through which charts can be generated. So we are going to see the templated
method for chart generation. Then how to expose this particular agent as a REST API with FastAP and
how do we containerize it and we can maybe take this Docker further forward into maybe AWS GCP. So
this is the overall process we will have a look at today. Now, first of all, just noticing the
difference, like what is the difference between traditional BI versus the conversational BI. So
traditional BI, it is like in place for many of the years, we have built dashboards, we have like
KPS created, visual reports, everything, but the limitation is it is like kind of predefined, static
and it's always dependent on someone technical to create and modify the overall dashboard. Now,
let's say if a user wants a report that wasn't built

### [4:02]

or they want some particular data from joints of a two table or something like that, usually the
non-technical people would need to get help from the technical team, either from a data analyst or a
BI developer, data engineer kind, and like if they require some urgent data, this will cause some
sort of a delay in the overall process. Now, when I talk about conversational BI, the advantage is
now here, I'm not talking that traditional BI is not useful at all in this time. For very quick use
cases, traditional BI will always be there, but as an additional layer, conversational BI use cases
are evolving. Where, for example, the main idea is that apart from the dashboard, let the users chat
with the data. So the idea is asking the question in plain English, we can ask simple questions. For
a non-technical person who will be chatting with this kind of agent, they won't be required to any
particular technical skills apart from certain sort of an idea that how to operate the agent, what
kind of input it would require. Conversational BI would give live responses or live data from the
current database. Answer would be made available as required, like if we just remove the thought
that the agent would go in a case where it just won't be able to identify or fetch the data. In
those cases, apart from that, whatever data is live in the database, the user would be able to fetch
that in seconds. And it can also create personalized content-aware, context-aware answers, meaning
apart from just a table visualization, it can also generate some sort of a wording that this is how
the data, so like context-aware answers can also be generated. So this particular flow will be quite
natural for a human being rather than a static dashboard for system.

### [6:03]

So the idea is reducing, or let's say, for example, let's say I as a person wants to get some data,
so I would need to go out and identify what tables are there, which table connects to which table. I
would write some query, fetch the data, share it with some other person. Instead of that, if I
already have an agent created on top of my database, now I as a technical person will know a lot of
things about the table. So I can even assist the agent in saying that these are the tables that you
can use, something like that, and this will make the solution more effective, while a non-technical
person can still ask for certain types of data. So the agent, if created very promptly, like over,
like given certain guidance during the development stage, properly given all the schema details and
everything, it would be able to fetch us the data. So that is what our target is. Now, in what
spaces right now, currently, the conversational BI is highly used. So, first is like a retail and
e-commerce, a lot of like, I personally have worked in this space, like a lot of people or a lot of
organizations are kind of like trying to identify, like what, like for a particular manager, they
can check out what are the orders or what are the products in the inventory, how many people are
working on that, how many employees are there, how many employees are on leave, they can track
certain revenue across regions, countries, chart, and all of these things. Then manufacturing,
supply chain, finance banking, something very similar, just ideas different, even in those cases, or
even human resource, the oral ideas, we have a database, how are we letting the final user

### [8:06]

extract the data from it? And the main core idea is that in all of our, almost certainly all of the
major companies, the data already exist. The real problem is whenever someone wants to access to
data or wants to extract some particular data, the process can become slow, slow, or there might be
dependence on a technical person who might be involved in some other work already. So here, what
we're doing is we're not trying to solve a data availability problem, we're like kind of with a
conversational BI, solve a data accessibility problem, majorly for the non-technical folks, right?
So, like I would like to know, like in any of you guys' organization, do you have some sort of a
setup already where you can chat with your database? If someone is already having a system like
that, I would be very happy to know. Is there anyone whose organization has a conversational BI
setup? Great. I guess a few of you already have, right? Yeah, that's great to hear. So, would you
guys like to share how is it helping your team so everyone gets an idea of the overall process? You
can just raise your hand, I will give you access to unmute, and you can just share your inputs
there. I allowed the microphone access to you can you try to unmute maybe now you can

### [10:40]

unmute yourself can you hear me yeah can you hear now so basically there were two two cases in which
it helped one was that in terms of sales it was very much helpful to understand the sales pipeline
and at what stage certain sales deal stands in this case it was fetching data from the CRM system
and allowing the sales reps you know to have a Q&A based on that data and in terms of end users
basically this was an insurance domain it helped them to actually do some operational tasks like
creation of policies or let's say the payments of policies renewals those kinds of things without
actually you know using the UI understood okay great to hear thanks for sharing yes so continuing
the the quick we're discussing so now as I've already mentioned we'll focus more towards the code
part so let's try to understand the overall first system architecture that we are going to try to
build so like at the very top as we all know we would have a client layer or a particular layer
which takes in the

### [12:40]

input so a browser a user would be sitting on the browser will be sending some input for now we are
going to use a streamlit UI that which we can take in the input it would send it HTTP post request
to the fast API backend now this fast API backend is multiple APIs like chat then what there is one
chart API when it's history when it's tables so this history and tables are just for our purposes to
check if like those functions are working properly the chat and chat functions particularly like the
chat will just written text if we use the chart API it is going to also return a graph if also
possible now the main architecture behind this both of this particular API is chat and chat is a
single agent so it is a land graph SQL agent that has multiple layers of functions there so first
one it will go it is going to use the query rewriter that checks the history the previous history
and tries to understand rewrite the input so we make it a bit of more context aware then we have an
intake intent detector so the intent detector is specifically to understand if the user wants a
graph or not so like we just want to check like if the data can be like a graph can be generated or
the user particularly asked for a graph so this particular intent detector will help us identify
that then we have a standard SQL calls like list tables call get schema so using this both our idea
majorly is that we get all the information about our tables and the schema that we have like this
will be the short call it would be a just a few information about the tables in case where you have
a lot of tables already into the system maybe at that point of time instead of listing the tables

### [14:42]

getting information from that instead of that a better way would be to use a prompt but as if you
have some limited number of tables it's a 50 or something even like 10 20 it is better to just not
fetch it the tables get a schema get all the information in live point of time then we're going to
generate a query based on the input shared by the user then we're going to check the query check the
query like to just validate it run the query whatever execution level like whatever final results
are there we also generate a chart config along with it so using the chart config we are able to
going to generate a chart and there will be three types of different layers one is observability
layer where ML flow will be tracking the oral agent collecting everything and along with that we
have added a few matrices as well custom matrices and the main part from which the agent will be
running the query on is the database in postgres so for now we are going to use a Northwind DB that
is like a business use case database and there will be an agent memory also that is also going to be
stored in the postgres so this is how the oral architecture will look like so this particular
conversation memory helps us have the persistent database storage and for example this ML flow like
in the last session we also saw right so if anyone has missed the last session just to help them get
a clear picture with the ML flow tracking what we are trying to do is that all the things that
happen inside the agent we're trying to track all the inputs outputs at each stage of the state so
we know what prompts were executed what sql was generated how long the each step took at what node
something failed and what kind of thing succeeded so using this now tracking layer helps us out
debugging the agent in cases of failure

### [16:42]

then onto the UI part you can swap it later you can attach it with your own UI whenever you will get
the code after the session you can change the database DB you can replace it with your db like you
can like this will be like a plug and play kind of a code for you you can change the business db
here in postgres you can or maybe you can make a attachment to my sql it is all everything connected
via sql alchemy so it will act like a plug and play you just need to make make the connection to the
database and a few minor changes here and there you'll be able to access whatever database you want
to connect to and all of these things would be further wrapped inside a dock container now the agent
part like how it works so query rewriter as i was mentioned it results in the ambiguous follow-ups
using the conversational history so let's say i ask something and i just say let's say for example i
said uh give me a chart for all the employees in the organization so or let's say group all the
employees by their role level like who are how many managers are there how many uh senior tech leads
are there it generates a chart then i said if i say do the same thing for uh upper management so how
will it understand what i needed so that's why we have a query rewriter that fetches history from
the conversational memory we have already stored and using it to rewrite the overall query that will
be passed to the intent detector the intent detector classifies the chart needed yes or no via a llm
call we're going to use a mini model here then we have a database inspection where we do list tables
get schema so it inspects the overall database structure so here why we need to do it that we could
have provided this in the prompt itself but what happens is

### [18:46]

uh sometimes in cases where you ask some question and you don't have a validation check the thing
that gets worse is that the model invents table names or column names and it goes into an error
state so to give the model an actual awareness of what tables exist and what the schema look like we
have these two functions get tables and get schema through which we would be able to get all the
necessary information about the database we are going to query on then we have the generate query
node so this particular node will help us uh like uh write sql natural language answer all of these
things would be uh via this like it will help us write the query then uh we have one one validation
layer check query with which we're going to check does the sql structure are there or if something
is missing if any rule is failing something like that we can all check it by the check query then a
run query would be there so this will be the one responsible to execute this sql query and collect
all the rows and columns into a particular state like it will just store everything all the results
so we can display the final result back to the user and along with it one more chart configuration
would be there like once the intent detector says the chart is needed the chart config will try to
identify what kind of chart can be generated so decides chart type access and title all the
information and it returns a structured json for rendering and this particular output is sent to a
custom code that we have already returned that it receives information like this chart type access
title and it generates the chart so at the final point what you will have is a final response from
the executed sql and chart like the json information of chart that will be sent to a chart generator
that generates the chart as an

### [20:49]

image and that image would be further encoded as base 64 sent back as the final output in the json
structure so under the front end we would need to use base 64 to decode that image again okay yeah
anyone has any questions at this point of time can surely unmute and ask any questions yes shibu uh
chirag in this you're saying that safe example my company uses big query as the database okay so
there are like a thousand different tables not all thousand different tables would be used to do the
sales analysis right there would be only hardly six or seven because there are staging tables and
there are only view tables and different kind of tables right now my question is uh what if i have
other excel files and csv files which would also be part of this whole you know ecosystem right say
for example i have 10 different stores which is not there in query but i have an excel file which
has a store code and store id and something like that can we incorporate that into this entire
system or it will only search data yeah no uh that could be incorporated but as a separate workflow
in itself that we will first need to identify whatever data the user is requested either is the data
available in database or will we need to fetch the data from csv or any other data source so first
in uh router like that would need to be set up and the pipeline like this we have set up for the
database agent similar to that we will need to set up one uh for uh the unstructured data csv pdf
document could be anything uh like the rack pipeline setup we would need to do something like that
okay so i'll give an example so that you know uh it's better to understand so i have all the data
for an e-commerce

### [22:56]

platform okay but the company is saying that i can't give you the cost from the vendor for example
right so i have the sales price i have the quantity everything but we can't disclose the cost to
everyone so we will give you an excel file only to you okay now how do i incorporated this cost into
my analysis so if i have skew ids and i have cost on a monthly basis so today so this is march month
so i have cost right now i have to incorporate this into my analysis rest everything is on the big
query so i guess in that case uh what best thing would be that you would need to add some coding
configuration here that whenever uh some query is generated some results are generated from the uh
like once the sql query is generated results are like the queries executed results are there maybe
you can write like there is already a node that uh like reads the csv uh gets the information like
connects the product with the product id or something product cost gets the cost and attaches it
back to the final result of sql that could be one way or you would need to figure out uh in the oral
process where you can read the csv and add the data wherein were required so this kind of thing
could be done okay thank you yes your voice is very low not too good very low on a scale of zero to
ten your voice is like one how about now chirag

### [25:12]

yeah it's perfect now okay so you you are basically giving us the direction about how the
orchestration of agents right so what you're currently showing is like a single agent system or
multi-agent system in a forward or a feedback system in place so right now you mentioned as
different nodes right so is it a single agent going to do all the things or it's like multi-system
in place that is my question right now it is only single agent because it will be only working with
one single database in case you want it to for multiple things right so how it can be done is the
same uh flow could be uh implemented for let's say two different databases that do not have any
connection with them they're two independent one is let's say on big query one is let's say on some
mysql postgres and you have an aggregator agent that takes in response from both aggregates the
result or let's say how the workflow would change in that particular place would be that there is
first one one just an llm that identifies how much data we need from big query how much data we need
from other data source then two different agents like this workflow is there uh two workflows like
this two agents are existing with this kind of workflows one fetches the data from big query one
fetches the data from postgres and then would be an aggregator node could be llm could be just an
algorithm and the final result is aggregated charts are generated that way it could be done but
right now as we are only having one database it is just a single simple agent okay okay so if it's a
single simple agent for each node there is a action involved or as a process right so there is a
logic beneath in each node and we are making agent to execute right so how are you making sure that
it is properly obeying the instruction being provided there so is there any uh uh validate section
in

### [27:18]

place i could see there is a validation but uh don't we need to do uh have a validation logic
beneath in every node that the agent pursues uh it is definitely that is uh what will depend on kind
of business use case you're doing so let's say for things like list tables get schema like the the
most validation you can apply there is uh just like a few sentences that ideal case it should only
list five tables are these five tables listed so all of these things algorithmic level coding i
guess uh that should be automatically handled when you are uh working for an uh full production
level uh code base so but yeah your idea to add validation at each node uh like that that would be
in place okay okay okay yeah thank you thank you all right so let's continue right now with respect
to the conversation memory like how we have defined is that uh like as you all know like the llm
api's or the land graph agents we usually create a stateless uh and what usually happens is uh in
cases like this where we need a conversational memory or a conversational context to continue for
some limited time or a longer time we can store some information into a database and extract to
maintain the conversational uh context so here instead of like uh like a few of the learners have
asked in the previous sessions that why we did not use land graphs inbuilt postgres check pointer
that we can

### [29:22]

connect store it so the problem would happen is it is going to store the entire graph like a lot of
information which we might not require so what we do is we create a simple uh function simple files
through which we can store in the conversation messages for example we can create a table like this
conversation messages with id session id role content created it so how it essentially works is
before every agent run we call up this particular function that uh fetches the data from
conversation messages it fetches the history, depends the history to the current question. Now
either you can just let the history data be sent as it is to the prompt or you can use something
like query rewriter to add this history element to the incoming input so it becomes a more context
aware input. Now as I mentioned query rewriter node can be used and after the agent answers whatever
new user question and answer pair was generated we can store that back to the database now here one
thing you need to keep in mind is that this new user question would be most likely be this one the
rewritten history if you're going to use the by default input user question like you can obviously
use the input question but just to maintain a more overall better I would say the context it would
be better to store the rewritten query. So this is how conversation memory would look like so we got
a few questions why the inbuilt Landgraf methods cannot be used like so first thing would be that if
we're going to use a Landgraf inbuilt methods the problem usually occurs is whenever there is a
library update sometimes some connection issues happen like I have an experience that we're using
something like locus equivalent connector data was stored there and initially it stopped working so
like we tried something

### [31:24]

a few things here and there and identified that the problem was due to version change like it was
not able to properly connect to its store memory and extract the context we then started moving
towards the custom functions where we do not depend on any framework to extract the context as we
say everything because this is like a very really important part of the overall agent application
structure then the charge generation pipeline so the overall pipeline for this like there could be
multiple ways now like there is no fixed way this is one way that I'm showing there could be
multiple ways in the market like there are a few famous ways to do it like one is have your own code
sandbox where all the python libraries are installed you use an llm to generate the code that code
is sent to that sandbox the particular image is created and it is returned and you show that image
well another way is there are certain libraries that accepts the text data and generates the output
from it and one other way that we have figured out all the ways we identify the intent from the user
that there's a user wants a chart or not we generate a chart config that what kind of chart can be
created what kind of data could be there on the x-axis y-axis what should be the title of the chart
and it goes to a particular chart generator function this is this would be a custom reader functions
in some cases for some cases you might only need a bar chart pie chart and a few other charts in
that case only those functions would be there if you want to obtain custom functions all of the
things would be saved as inside the generated.py file then we would have the sql generation
execution the sql is generated executed all the information that is there we will pass it through
the generator.py and like the agent state rows and columns are saving all the information not much
on that so the main part

### [33:25]

here would be the chart config and generator.py the chart config would be the one deciding what
chart type is best what should go and excesses as i already mentioned right and let's say for
example if someone asked if the result or let's say a particular user asked for a revenue by country
so like there will be an llm which identifies that okay this can be shown as a bar chart so the type
would be bar chart what goes on x-axis would be country on the y-axis it would go is the revenue
numbers count something like that and in that way the configuration would be created as a json and
this would be passed to the chart renderer which creates the image and stores it as a png and
returns the full image in form of a b64 format so this is how a chart generation pipeline would work
then in our oral code system what we have so as a agent framework we're using lang graph llm we are
across the oral system we are using gpt 4.1 vini but one important thing to note here would be that
we would have a lot of different like when we work in actual case we would identify that some llm
generates better chart config some llm maybe not even from open here from some other provider
generates better sql query in that case it is better to use those models use a mix of models that
would be better then the database we are having we have stored into postgres memory store is also
stored in postgres and we're using sql lkm as a library to connect our code with the postgres like
work size are just a kind of a layer that we can use to access postgres api layer we'll be creating
with fast api to create rest api's chart rendering would be done by metrotrip pandas and chart would
be stored as a png the observability we are having ml flow trick matrices and a few other different
experiment the values will be locked on the front

### [35:29]

end we're just creating a simple streamlit ui containerization we are going to use docker plus
docker compose setup now we'll go move towards the main part that is our project code so so starting
like i was starting from the very scratch that how i would have written this code okay so first of
all i would have this kind of a formation where i would start creating initializing what all
environment variables or what epic is i would be dependent on and basis on this i'm creating this
configured py file where we are using the pedantic settings where our every environment variables
whatever is stored inside the dot env file i'm going to capture that and this particular settings
would be used across my oral application and here all the postgres related urls open api key any
memory agent database key ml flow tracking uri the application host port any information related to
models everything will be calculated here and here also i'm defining one business db url like the
final url if i want to extract i can just simply call this function to get the url for connecting to
the database and a memory db url that will help me connect to the conversation memory database and
this full i will like use a lru cache meaning it is loaded once at the startup it won't be called
again again so these settings can be reused reused across all the other files that we want to use we
do

### [37:30]

not need to do uh like kind of load dot env in each and every file we can just import this
particular settings in each of the file and simply do settings dot whatever particular uri or
particular environment variable we want to extract now the next point next part would be before even
uh defining the agent uh what i will start doing is i will start defining by defining the main
memory because uh how i be going to uh uh like the conversation memory system and everything so i'll
just go to memory uh all the information here um like uh is already defined so i'm going to use
sequel alchemy here uh like like i'm just going to take in few of the information uh what are the
orm fields and everything i'm defining here uh in the lang chain core uh ai message human message
all i'm calling so like whenever the chat history is sent back to the agent we will define what is
the human message what is the ai message everything and uh whenever i'm defining the overall
structure so what would be the conversation message uh or before that let me walk you through one by
one yeah so firstly this any database function so this particular database function is called at the
start of the api part of it that it creates conversation messages and let's say it first calls this
db url safe uh url like just checking uh like stripping the credentials for logging and we create
this engine so this engine is what will help us allow uh i would say uh if the table is not there it
would it will help us to create the particular table and then we are saying that memory db is ready
table conversation message just to ensure that the table is existing everything is fine and we can
connect to this particular table then the other

### [39:34]

part of it important part would be storing the message so storing the messages like we're going to
uh uh like uh the conversation messages so this is the other function conversation messages we're
defining everything id session id role so this is a actual paediatric class and using this Pydantic
class, we're just kind of defining everything, what things could be there. So I will go back to the
main function, storeMessage function, where we are going to pass in all these values. We will store
it as a raw. I will add it to the db, db.add, db.commit. So this particular value should be
committed to my database. And the next part would be, this is how I commit the values to the
database. Then the next part would be getting the history. So simple function, it queries the
particular database. We'll pass in the conversation message. We'll do all the filter order by
descending, so the latest messages would be first into the list and reverse the list so the order is
chronological, like oldest to newest. So this is how we will be getting the history. The other
function would be that whenever we're using the main agent, we'll be using this as well,
getHistory's lang chain messages. So it will take in the session ID, like this will be the main
function. So we'll call the guest history, we'll pass in the session ID. All the messages that I
get, I will convert into the format that is more better for the LLM to read. So I will convert it,
say, what is the human message, what is the AI message. So clearly defining the separation, what
would be the AI message, what would be the human message. So these are all the different sets of
functions that I'm going to use, and there is also one optional clear history function

### [41:34]

in case you want to delete all the messages from the session. So these are just the extra functions
that we already defined. Now, once you have defined both of this, the next main part would be the
agent.py. So here we have defined a graphical flow, and here all the nodes would be defined here. So
we're starting by importing the main config settings, the memory, all the history is lang chain
messages and store messages. So this lang chain messages will get the history and format of the AI
message, human message. Store message would be used to store message into the database. And all the
necessary lang chain, lang graph imports, like state graph, what all things you would be able to
create using the lang graph functionality. The next important thing would be to import mlflow and do
mlflow.lang chain autolog. So it traces all the lang graph related calls into the mlflow trace, and
would be setting the tracking URI set experiment. Now, all of these things would be going and stored
inside like this particular API would be running inside a Docker file. So the important thing would
be here to do is, like as the my mlflow and streamlit would be running and or the Postgres also is
running inside my local P system, I would use the particular host URLs, host.docker.internal. But in
case if they were running on particular URL, you would need to add here URL, whatever URL is there,
wherever they're running into your .env file. Now that I'm going to define my class, main class, it
consists of messages, wants chart, like this would be set by the intent detector and read by the
generate query and after generate, like what kind of charts would be generated, the SQL rows,
meaning the raw result rows, SQL columns, what are the columns available,

### [43:35]

chart config that will be decided by the chart config node. So this is how my lang graph state graph
looks like. Then there are a few helper functions like pass SQL results, like stripping out the
results into a list of tuples, then extract columns. So extract column alias names from select
clause. So like if some error occurs, like we can use this. So fallbacks to column zero, column ones
in case any issue happens. So we can use this to extract column names from the select clause. All of
these things, a few helper functions if we require. Then we are going to make the main build agent
function where we are initializing the chart model, main model, the chart model, everything. We are
loading the database. So SQL database from URI will pass business DB URI and that URL that will
connect us to the Postgres. Everything will be defined. Now we'll be defining this toolkit, get
schema tool, run tool, list table tools, everything. Get schema node, everything as a tools. And
then we'll initially define every node. So first we are going to go with the rewriter system node
now. I will not be doing much into the agent architecture because this is all we have seen in the
past session. So I'll just go through it, how it goes into a sequential manner. So we have the main
query rewriter node. We know the function. It's going to rewrite the query based on the previous
conversation context. Then we have the intent detector. So what we say is, given the user questions,
decide if they want a chart, graph or visualization, written only one word, yes or no. And we
explicitly state some rules. The user explicitly mentioned, the user asks for a comparison, trend,
distribution ranking. In those cases, try to generate the graph configuration. Then the list tables
function, get schema function, everything. The base generate system. So, or we are going to use that
for a generate query part

### [45:38]

where we are passing at the system content. And we're going to connect all two tools to it. So it is
going to get the schema and everything here in the generate query. Then we'll check the query. Like
again, binding the tools, calling the LLM. And we're just trying to verify that all of these things
are correct. Like not none in any of the null type mismatches, anything. Rewrite only if there are
mistakes, meaning if the LLM finds there are any mistakes in the query, rewrite it. Otherwise,
reproduce, unchange the same query. The next part would be to run the query. So we collect all the
things, the SQL query, everything. We parse the SQL result. Like once we call the run query tool, we
invoke it. And we'll parse the SQL query result, extract all the columns, and we'll return as a tool
message. So content, what was the tool call ID, the name of it. What was the last SQL that was
generated? What are the SQL rows and SQL columns? Meaning, what are the column names and what are
the values for this rows will be returned here. And this values will be like retrieved by this chart
config node, where it will try to know, like we have given guidelines, what charts it can generate,
like bar, line, pie, scatter, everything. It's going to identify, read it. And using this prompt, it
is going to identify what is the best chart. And it is going to create a JSON for us. And we're
doing a simple kind of a JSON stripping from whatever response it generates. And we'll load it back
as a JSON configuration. And this is what our final chart configuration would look. And we would
return something like this, chart type. If some error occurs, we're just going to use this fallback
method. And just for a fallback method, I have just kept a sample data here.

### [47:38]

In your cases, you can maybe directly say, the graph cannot be generated or something like that. And
the final part, after everything is done, after the chart config, we'll just simply end the oral
workflow. So from it, the oral agent will execute, will return a particular response. After running
the query, it is going to generate the response. If required, it will generate this particular chart
configuration. And using the chart configuration, if any chart is available, it can return as a
chart. So all of these things will be there. And this run agent function is what is going to call
this particular agent. It will invoke the agent, whatever responses it gets, it will receive all the
messages. And it will store to memory DB, all the like extract rewritten question and store it to
the memory DT. And it will log, like we are also having a logger that it will run inside the Docker,
logs everything into Docker. And then finally, we're going to return this answer, the final answer,
chart configuration, want charts, what is the last SQL, rewritten query, SQL rows, everything. And
after this, the main part, where we have defined all the things as an API, like the oral agent. So I
wanted to know how many of you are already aware of the fast API and how many don't know. So I could
know how to explain it in simple terms. How many don't know what exactly fast API would be? Okay,
one person. Well, it's fine. So I will explain it, okay, two person. I'll explain it in simple
terms. So fast API is like a framework in Python

### [49:42]

that will allow us create APIs, similar to how we create APIs for our node use cases, or sorry, the
node.js, or maybe we create the APIs with any other libraries, right? any other programming
languages. So similar thing, FastAPI allows us to create APIs through which we can call something,
maybe get request, post request. If I do a post request, it will do some processing and it is going
to return me the value that I can return it back as the main response. So a few things related to
FastAPI that are important is, from FastAPI, we'll import FastAPI. This coarse middleware meaning
will allow all the users, all the users with different IP addresses to access this particular API.
And this JSON response to send back the final API response. And all the things related to my agent
and the chart renderer. So I would have this now, charts generated.py file, as I was mentioning.
This file contains all the functions and what it takes is, it takes the rows and columns of the SQL
result and along with the config. So config is the one that the LLMS generated, what chart type we
want to do, what will be the titles for X label, Y label, X column, Y column. And based on it, it is
going to return me a image base64, like this is really a string and that particular encoded base64
string would be decoded at the stream to TY level. And these are now all the functions written to
generate pie charts by bar charts. Then we have some functions for line charts, everything mentioned
here in the generator.py file. Now you can customize it according to your need. So maybe if you want
to do more advanced charts, you can add more custom functions to that.

### [51:48]

Then we're just setting up a simple logger. Then we're kind of defining just a lifespan where we are
initializing the ML flow and initializing the database. So all of these things would be captured
here into my lifespan till the fast API exists, this particular things would be running. And I will
also trigger the build agent function so my agent would now be existing and I made it global. So
across the overall API file, my main.py will be able to use my agent and the database values. Then I
define my fast API, the title for it would be conversational BI agent. I can define some
description, version, what lifespan I want. Using lifespan, ideal case, using lifespan we can also
define cron jobs. Like if you want to run certain cron jobs at a particular interval of time, those
kinds of things can also be defined in lifespan. And in the app, I'm just adding in middleware,
allowing that from all IP addresses, I'm going to allow access to the particular APIs. Then I will
define some schemas, like what input message this particular API would take as an input would be
message and session ID. This chart meta, like what chart configuration I have. These are like
schemas I would define for the API. So the APIs would be able to receive the data in this format if
anything can act as a validation layer. The chat response, what I want, that would be answer, SQL,
session ID, rewritten question, once chart. The chart response would be everything together, just
like apart from the chat response, we would have another output variable that will be a chart, that
will be consisting of the base 64 encoded image value. Then a few of the schemas for my history,

### [53:48]

what it will have would be the session ID, how many, what is the count of the history entities in
case of new history entry. It would be ID, what role, like is it a user assistant, what is the
content for it, and when it was created. So all of these kinds of schemas we have defined. Then we
can just define a simple health endpoint that says the endpoints are active. Then I'm having a list
tables endpoint that I can take any time to ensure that my particular API or agent is connected to
the database successfully. So if I'm able to list the tables here as an API endpoint, my agent
should also be able to access this particular tables because sometimes it happens is, I'm telling
this from a personal experience that I had a particular agent, I deployed it, it ran it production
for two days and after that, I found out that that particular agent was not able to connect to the
database because it didn't have enough access or enough permissions to run inside the deployed
environment. So as a precautionary action, what we started doing is we, whatever things the
particular agent is accessing over the particular deployed servers, we also deploy the simple normal
functions as an API. So if my API is able to access this particular things, my agent would also be
able to access. If they cannot access, that means my agent will also not be able to access and will
result in some error or users won't be able to run the agent. Now, my two important functions, chat
and chat. So I will directly go into the chat. So what chat does is we are going to call the run
agent function that is defined here, which calls the final, it invokes the agent, it gets me
everything and I'm going to get the results out of it, like my chat configuration, I will pass it to
my render chat function

### [55:48]

and the render chat function, if it returns me a base 64 image, I would log this particular chat,
these are all the chat values. If not, I will say that like chat rendering failed or render chat
returned no image, like the image generation could not be possible. As an exception, like in case if
try to generate the image it failed, we can share a proper message that chat could not be rendered.
Something could not happen now in this cases. You can try to figure out certain different messages
that for this query, the chat cannot be generated, something like this. But as I was testing it out
for testing purposes, I clearly mentioned different messages that if it fails, I clearly say chat
render failed. If it returned no image, I would say return no image in this cases like this. And
final response from this API would be answer, the SQL session ID rewritten question once chat and
the final chat whatever was there as a base 64 of the encoded version. And these are a few more
helper APIs again, to get the history, to delete history, just to check this all the things are
working, like connecting the database and everything is happening. Now, the main part would be here
is how are we going to deploy this particular FastAPI endpoint as in a particular Docker space. So
we would need to create Docker, right? So we would have a few things here is, like those who are not
aware of Docker. So Docker is a kind of a service that allows us to deploy across multiple services,
like we can deploy it in some custom servers, we could connect it to Kubernetes, we can connect it
to different services like ECS, EKS, or Google's containerize, or I would say Kubernetes management
service, I don't remember the exact name, but in all of these things, we can just push a Docker
container

### [57:51]

and we'll be able to run that particular Docker container into their specified server. So this is
how Docker can help us. So instead of copy pasting or pulling pushing the code everywhere, we can
convert the oral code structure into Docker container and we can pass in that particular image
wherever required. So that particular instance of the particular application, we can run it across
multiple or like in a particular server safely. So how we do it is we define a Docker file. So like
we define all the necessary installations we need to do inside our Docker image or a container. So
we define what Python version we require, we define like, so this will, this container will act as a
kind of a local system that will have Python installed. All the other libraries related to Python
will install via this particular functions. Then I will install all the functionalities related to
my Python or my agent using the requirements.txt. So I have defined everything here, all the
required libraries and requirements.txt. Then I will copy my main application code. I will make
certain scripts importable like MLflow track, the scripts file and all. Then I will just add a non-
root user for security. So kind of like this is for security purpose, we create a user that do not
have the root access to the overall Docker container, like it cannot change it. We will expose the
8,000 node at which the FastTP endpoints would be running. We're just adding a health check that
checks the health for kind of a certain interval and it will do a timeout through an error that the
particular Docker container is now not working. And finally, we'll give a command that runs the API,
the FastAPI APS we have created. So we can trigger them by using the UVCon command. UVCon will do
app, in it there is a main file

### [59:51]

and inside the main file is our main app handler that says app equal to FastAPI. So what this
app.main call an app means is inside our app folder, there is a file main and inside the main again,
there is this app equal to fasttp which it is it should refer to. Then we defined host 0.0.0 that
says it is open for all ips to access a port 8000. So this expose 8000 and this port also should be
the same. And here depending on your load balancing everything we can define like workers how many
workers we want. So one worker two worker and there are certain ways how you can like from the cloud
itself you can set out load balances as well horizontal scaling vertical scaling all that things
could be controlled by the cloud as well. Or there is one another better option is that you can use
G-Unicorn instead of G-Uvcon that is a bit of a better way to run the fasttp endpoints because it
can handle certain concurrency better than the uvcon as a library. Now one thing I try to do here is
like I have defined this docker compose here why I have defined this. So I wanted to show is inside
the docker compose we can run multiple services. So right now we'll be only having one service that
is bi-agent. So this bi-agent would be built using the context of this root level docker file. So I
am defining docker file that I want to use. Then what would be the container name it would be bi-
agent what ports I am using that will be the port 8000 same as it here 8000 8000. If you have more
ports how you need to do add it is let's say you can add it like this 5000 sorry 5000 5000 like this
you can add and this is how it is going to work. Okay sorry I did not need to add it here yeah like
this so more ports you can add more ports like this what env file it used to refer you can also
define dot env

### [1:01:54]

whatever will be my environment variables like postgres host everything would be going through host
dot docker dot internal to my local host. Now in case you wanted to add another service let's say
for me right now my postgres service is running outside of my container in case you wanted a
database to be there so there are already few ways to set up you can go to go in on google and
search postgres docker they will give you a similar kind of a structure like this what you need to
do is you just need to copy paste it here postgres and here all the particular information you would
get it here like how like what would be the image name how is the restart policy everything and this
postgres service should also run both in your docker along with your agent so docker compose will
help you run multiple different agents it can help you run single agent along with an different
database could be mongo db postgres could be some other service maybe the streamlet application can
also be made a part of this particular docker service as well like both the backend ui both the
things are running inside this docker container or like docker compose which will be running
multiple images and multiple containers so this is how you can also use docker compose something
like this now any doubts here in this particular case you are you can ask or will move to the final
demo for the session i believe it was not a lot lots of code or whether a few things that you guys
were not able to understand do let me know if someone has

### [1:04:00]

raised a hand do you have any question i guess no all right fine so i hope we'll be clear up to this
part so now when you will receive the code you will need to run a few important things first things
a few things would be how are you going to set up your own database now in case you already have a
database you can directly use that or another approach would be like we already defined the set
steps here like database setup database load how you can do everything so as a part of step one you
can create a database we'll initialize a database two database northwind agent memory and then from
my files you can simply define something like this like in what libraries you need to install and
then once you run this loader file python scripts load northwind it is going to push all of the data
to a database like it is just a normal sample database you can push it and it will generate some
output like this database northwind already exists or something like database it or it does not have
and from that it is going to show something like this these are the table created how many rows of
data is being pushed and northwind loaded successfully it is going to generate an output message
something like that and then you can check onto your postgres if everything kind of a data is there
you can go here click on customers scripts select script i can run and these are all the data i have
available here so you can run something like this as well now as a part of the next action like i
have added two setups here one is running locally like you can directly copy paste the code here you
need to make sure of a

### [1:06:01]

few things that from the dot env you make all the host as local host and in case you are using
docker as a service like running with docker you need to make sure that you are using the host as
host dot docker dot internal if you don't use host dot docker dot internal what will happen is
docker won't be able to connect to the pc's local host and that will result in errors at multiple
levels with streamlit ui postgres and the other layer so make sure to whenever you are using docker
use host dot docker dot internal and whenever you are you are running all the files locally like
running the api locally outside of docker make sure in the dot env you replace this with local host
once everything is set up what you simply need to do is you need to run this command docker compose
up build it will take certain time if your net is slow it can take some more time maybe five ten
minutes if your system is also slow it could take more time but once it is done at this particular
url your particular apis would be working on so if i go here sorry if i go here i run this copy
paste this i'll be able to see my apis working here so for example if i click on tables tight out it
is listing all the tables in my database so this is how all my apis would be working then like these
are certain other docker commands i have mentioned in case you want to check out certain logs for
your docker like if you change certain code and if you want to rebuild your particular agent you can
simply do docker compose up build again to rebuild your overall agent if you want to stop your agent
you can do docker compose down it will stop everything and then like i just mentioned all the
environment variables you're using so this is kind of acting as all

### [1:08:03]

the overall code structure you can just read it along whenever you are trying to set it up at your
end locally in your system and this will like kind of guide you to set up the overall project now
once your docker container is up and running how are you going to chat with it and how you can see
the ml flow ui where we are tracing all of the chats that we have done right so one thing would be
we have this streamlit underscore app dot py that acts as a ui so now this code is like a standard
code i have given as a template which will act as a ui you can chat with it how you run it is you
simply do streamlit run streamlit app dot py it would start up the startup service like this and for
the ml flow there is a few things you need to take care of when you will be running ml flow so that
is also mentioned in the readme so when you are in readme search for something like this set ml flow
so this set ml flow is like okay wait a little bit i will show you you need to paste this set ml
flow allowed host run this and then and then only run this particular function ml flow server
otherwise ml flow will not accept incoming requests from the docker container to store the traces in
the ml flows database so i can now go back to my ml flow service so here my particular service will
be registered con will gonna be an agent so this particular thing you can find it the original code
in the agent dot py file all the traces will be captured here Now, once everything is running,

### [1:10:03]

you will go to Streamlit, you need to add session ID, let's say I put test one. With the codefile
itself, I have provided a few example queries. Let's say which country has the most suppliers, let's
say I ask something like this. What it does is, it's calling this particular APS that are running
inside the Docker. This particular APS are running the Langraph agents and whatever response we get
from the agent, this APS will be the one returning the result to my Streamlit UI. It has generated,
the country with most suppliers is USA having four suppliers, and it says that I also prepared a pie
chart. This is the pie chart, it is showing the overall distribution by percentage. This is how it
would be generating multiple graphs for multiple queries. For my queries, let's say if we can try a
few more samples, like who supplies those products, it will try to figure out, write a SQL query.
For example, you can also check out what SQL query it has generated. So ideal case, you should
remove the SQL query when it is at the final end user. This is just for our case, our use case.
Here's a list of suppliers, who are the suppliers and who are supplying all these products, it will
give us a list like this. This is all that is being captured from the database. Now, to access this,
if I go here, I can go to my traces, it would have seven traces. This is my last trace it has
captured. I can go here, I will show all. This is the output it gave me, Australia, this particular,
all of it.

### [1:12:05]

This is the output from my SQL table. If you click on the SQL DB query, it would show you this, what
input it came, what output the SQL query generated. This is how you can trace all of the things
happening inside your agent. We also added a few custom evaluation functions using this particular
file, that is mlflow track, tracker.py file. In it, we are tracking all of these things, like a
query tracker is there that tracks a few things, like, for example, answer length, what is the
message count, is the chart generated or not? All of these things will be tracked. Here, if I go to
my evaluation run pages, if I go to my latest run, I click on it. Then from here, from this
dashboard, you will need to go here, overview. Here, you will be able to find, chart generated,
zero, means the chart was not generated, message count, 20, answer length, how many, like the big
answer was generated. Like, so this is the answer that it generated. So what is the latency? So 19
seconds it took to generate of the oral response. So this is how you can do a tracing of your agent,
as well as you can write custom functions to capture your custom matrices as well. So this is the
overall flow of my code structure. And I'll just share with you all the main key takeaways and then
we'll just have an open conversation regarding the oral project. So the main key takeaways from the
session here would be that we understood how we can ask business questions for non-technical
persons, especially. They can ask in plain English, no SQL, no dashboards would be required. Then we
saw the certain famous cases where, like from any person department,

### [1:14:05]

technical, non-technical, and in multiple domains, we also saw where this kind of use cases are
applicable. Then we saw process where AI agent converts question into SQL queries, how the memory is
connected. We converted this into a fast API endpoint. We saw a methodology of generating chats from
the SQL result. We used Postgres to connect for both our main business data and the conversation
memory. You could have used MongoDB for conversation memory as well, no issue with that. But as we
were already using Postgres, we just kept it the same source for the conversation memory as well.
And then we containerized the main agent as a Docker for easy deployment. This could be deployed
into any of the server. And like for MLflow, I would suggest that regarding MLflow tracking, it
would be way better if you run it outside the Docker environment because the Docker environment in
MLflow is facing certain issues. So MLflow running locally in a cloud environment would be better in
a server where you can store everything. Maybe you can store in S3 or a particular table. And MLflow
structure would work like that. And as an additional, like as an activity, what you can do or what I
would suggest it if you work on to the Docker, I would suggest the Streamlit code which you're going
to receive. What you guys do is, what you would need to do is you would need to go to the code. You
would need to create a Docker file, something like this, Docker file.streamlit. Add one more service
to the Docker compose for this and create a service that whenever you're Docker, like whenever you
run Docker compose up build, your main agent as well as Streamlit, both gets triggered, like both
gets activated. You do not need to run Streamlit outside of it locally. So this is, you can take up
as an exercise. So yeah, that was the main part from it.

### [1:16:09]

So we are open to conversations. If you guys have any doubts, you can surely ask. Yes, Amina sir.
Yeah, one question, I think thanks for the brief walkthrough about this conversation, P.I. So one
thing I just wanted to know, you're creating those nodes, right, for a land graph. So how do you
decide the node names? So is it getting automatically generated or where you're building the graph,
right? So... Understood. No, like a few things, like this all the names, right? This one, query,
rewrite, intent detector, list tables, everything. Yes, so these are like a separate module
altogether, right? Get schema means there is a separate module within that process and it does what
needs to be done. Okay. Right, so what we're actually trying to do here is, we are actually trying
to kind of first figure out, we create a design in head that if this is my agent, if I'm trying to
solve this problem now, this particular architecture you see right here, this is quite a famous
architecture for a SQL agent. So a few things we already get from there, like if you go and search
on that, what would be the ideal structure for a SQL agent, it will show you all the things. It
might not show you something like query, rewrite, intent detector, graph, the graph generator,
everything. So a few things, according to your need, you can add, but these things like this, list
tables, this is like an open knowledge at this point of time, you would find a lot of sources,
GitHub codes, medium, like blogs, everything around this to set up this kind of agentic structure.

### [1:18:10]

Okay, so some things we can also seek help from cloud code itself, right? Okay, this is the
planning, give me the plan and what can, so a few things, so nowadays even we were asked to use
cloud or GitHub copilot to have some kind of system in ready and try to validate those systems,
right? So that is how I think industry is moving towards, right? Right, if you have a cloud, I would
suggest like the ideas cloud is suggesting these days. Now I was working on something, I don't
remember right now, but I was not able to figure out. I went to chat.jpt, chat.jpt was not able to
figure out. I checked out stack overflow. I went to the traditional method of searching on Google.
No one was able to figure out, but somehow I kept chatting with cloud half an hour. It gave me a few
ideas and I was able to create out an idea out of that and it kind of actually worked. So cloud, I
guess, when it comes to coding ideas, it will surely going to help you out, okay. I would suggest
for the main part, like trying to figure out new code parts or trying to figure out the
architecture, you can take out help with cloud for things like database setup, API setup, Docker,
everything. You can go with this free chat.jpt, chat.jpt works quite well on those things. No need
to like use cloud for that. Oh, okay. Cloud uses a lot of tokens, a lot of, it would also incur a
lot of cost. Yes, yes, and I could really see that context window being consumed so quickly. Yes.
Okay, thank you, thank you, Chirag.

### [1:20:13]

Anyone else is having any particular doubts? Please feel free to ask. All right, I believe no doubts
in that case, I will stop the recording.

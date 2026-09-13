# Build and Deploy Your First MCP Server — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Build and Deploy Your First MCP Server](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/65150612-build-and-deploy-your-first-mcp-server)
> · Video lesson, 108 min (`1:47:53`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:08]

So I hope my voice would be audible clearly and my stream's also audible to everyone. So alright,
yeah, thanks everyone. So yeah, let's get started. So today's topic is MCB, alright. So in the last
year, like there was a lot of hype if you have seen onto LinkedIn, Instagram, a lot of different
social media platforms where people talked about MCB, how it could help the AI systems, the AI
agents and everything around that. So we'll try to understand how exactly MCB is helping us out on
that particular front and we will not only understand the architecture but also see from a
perspective of tool design how MCB is very similar to tool design but also and extended, I would say
an extended capability the MCB has over the tools, the standard agentic tools. Then we'll have a
look at the fast MCB library through which we can create MCB servers and then we'll look at how we
can publish the servers, run the servers locally and also put them into cloud services. For example,
hugging free spaces that gives us free hosting capabilities and everything. So that is what we'll go
and try to have a look at. Right, right. So particularly like how the flow of the session would go
is we'll understand the MCB basics first like what exactly MCB is, its architecture, the L cross T
problem and the host and client server model. Then we'll have a look at the MCB primitives or the
features that MCB gives us, that is

### [2:10]

tools, resources, prompts, sampling, what each of these particular primitives does. Then we'll have
a basic difference between the MCB versus tool calling. Then we'll look at the library fast MCB
version 2 plus. Right now the current latest version is version 3 and then we'll work around onto
the code part where we'll discuss how to use fast MCB to create a server, how to connect it to cloud
desktop as one of the MCB clients and also to any of the frameworks. For example, today we will be
taking the Google ADK library to connect the MCB server with the agent created in the Google ADK. So
that is how the oral process will take a look at. So before understanding what exactly MCB is, it is
something very important to understand what MCB is not. Because there are a lot of topics people
tend to confuse MCB with and that is the very main reason we'll clear out what exactly MCB is not in
terms of the other similar sounding EI capabilities or services. So the first one would be like a
few of you might be thinking something like it is a service MCB service that you can use as an EPA
or something because the fast MCB structure or the people who have seen how the MCB server requests
and connections are made. A lot of you confuse MCB with something like an EPA, but MCB is not
something that is going to replace the API. You can think of MCB as something like that acts as a
wrapper kind of a service on top of the API. So technically the MCB servers would be the ones that
let's example this is the MCB server. It will have access to a lot of different types of APIs. So
these MCB servers will consume the existing APIs and think of MCB as an integration layer

### [4:11]

that will allow the AI systems LLM models to call these APIs through a particular specific
communication channel. So MCB is designed to improve the communication channel between the AI
systems and the APIs that we're going to have. Then the next is like the tool calling or the
function calling. So like people who have used OpenAI function calling or the Langtains traditional
tool calling with respect to that MCB is like as I was mentioning is has taken a bit like kind of an
extended version of that. So MCB provides us with a full protocol. So like similar to how for web we
have the HTTP protocols, HTTPS and everything right the transfer protocols everything similar to
that MCB is also providing us with a full protocol for describing invoking this particular tool when
the AI agent or the AI system is running. So how the traditional LLM function calling works is like
there is a user query the LLM reads it the LLM finds what are the tools available to me and LLM runs
those tools with respect to how the MCB server connection would happen is the LLM is connected with
MCB server where it can discover what are the different types of MCB server tools are available
through the MCB server gateway and through this particular gateway that acts as a protocol for data
security how the particular tool is described everything also the tool invocation access everything
is with respect to the MCB server. So the MCB server will act as a gateway between a protocol that
will help us maintain everything as a proper procedure. So that is the basic difference between them
but ideal case tool calling MCB is essentially we're trying to do the same thing MCB along with the
tools provides two to three more primitives are two to three more features but they're not that very
important the major

### [6:15]

capacity that or the major capability right now that we are using from MCB is the MCB tool services
then MCB is also not any particular agent is not an LLM so at the MCB servers and where your tool is
residing it can be that that particular tool is an LLM based tool intelligent tool or it can be a
tool that simply runs certain particular function and returns a result so MCB is not something like
you know the MCB server is not exactly any LLM or an agent framework MCB particularly is just and
like you know the communication protocol between the agent and the different tools services and
everything together so acts as a gateway so MCB also like if you're comparing it with Lang chain
Lang graph or something it doesn't fall into that category because MCB is like you can think of
something like the Lang chain Lang graph kind of libraries they act as an orchestration system for
the overall AI architecture MCB you can think of as an orchestration architecture for the

### [10:11]

codex or the cloud code, cloud desktop, everything comes with an inbuilt MCP client kind of a
service. This client, we can connect it to the MCP server. So this MCP server, so there is a mistake
here, this I have mistakenly put in MCP client, so here it would have been MCP server. So each
server, so now it is not also necessary that inside the MCP protocol, there can be only one server,
there could be multiple servers. So one client can make and one single persistent JSONRPC connection
with one server. So remember this line, each host application would have a client, this client can
make a persistent JSONRPC connection with an MCP server. Now there could be multiple MCP servers,
could be one, two, 10, 15, 20. The MCP client will have an independent connection with each of the
server over a JSONRPC connection. Now a few details about the MCP servers. So MCP servers are
designed in a way that they are lightweight programs having specific capabilities, can have some
access like data tools, resources, can have certain basic prompt mechanisms, everything including
that. And servers would be able to access local resources as well as the remote APS. While the
client, client is the one that will maintain the session state or the negotiation capabilities with
the server. So as the client is the one that is going to receive the inputs from the host
application, client will maintain the connection with the server, also will process everything, like
calling the server when a tool is required and everything. So what idea did we got at this
particular point is, MCP client would also be the one that would be having an LLM as its thinking
engine. So there would be a host application that will have some sort of a UI, user puts in some
queries or some action has been processed.

### [12:11]

The MCP client with a particular LLM, LLM could be Gemini, OpenAI LLM or any sort of an Anthropic
LLM. So this MCP client would act as a thinking engine, will have access to single server with
multiple tools or multiple server with single tools, multiple tools, all sorts of architectural
possibilities are present. And this client will communicate with each of the server whenever a
particular tool residing in that server is required. So we have one question here, MCP client should
be single for host application. So yeah, I guess it will be single only because multiple MCP clients
would mean that we'll have multiple MCP processes. So let's say if you have a multi-agent
architecture, in that case, you could have a possibility that each of the particular agent could
have a separate MCP client which access to different sorts of MCP server. So that kind of an
architecture can be built, but yeah, host application could have only one MCP client if it is more
of an, I would say LLM workflow kind of a setup, but in sorts of agentic, multi-agent structure, you
might need to define the MCP clients for each of the agents separately with a server access and
everything. So that is how there could be a little bit of a difference in the architecture way of
creating the MCP clients. Now, how or why this particular MCP uses the JSONRPC? So what exactly is
JSONRPC? JSONRPC is like kind of a protocol. So that is an existing, already existing protocol in
particular. So like previously before this, there were also other protocols that are designed on top
of the same JSONRPC protocols.

### [14:12]

So what exactly is this JSONRPC? So ideally, the MCP is something that requests bidirectional
communication continuously, like MCP client connecting to MCP server, MCP server working back or
returning some value to client, client again calling back the server. There could be multiple to and
fro communication between them. So JSONRPC is something like the full form of will be like the
JSONRPC standing for the remote procedure call. So this is kind of a protocol that allows two-way
communication, and MCP as it requires two-way communication. MCP, the protocol got built on top of
the JSONRPC version 2.0 technology. So LLMs need to call external tools and these tools may need to
call back into the LLMs. So that is the reason for this particular two-way communication model.
JSONRPC suited perfectly, supports bidirectional communication model, enabling dynamic interaction
where both parties can act as a client and a server when needed. So like with respect to JSONRPC, we
can also see possibilities where the client acts as a server, the server acts as a client. That sort
of a capability is also there. So this is the kind of a way why MCP chose JSONRPC at the base
protocol to build the extended capabilities for the MCP client, tools, services, protocols, servers,
everything to build upon. Now, how in practice this whole process would look like? Let's say there
is a host application, you have a chat, you have ID assistant, anything could be that. There could
be single client, multiple client, MCP client one, client two, more clients you have. These clients
would be connected to the MCP servers over the JSONRPC version two protocol. Now there could be
multiple servers as well. Server one, server two, server three,

### [16:13]

n number of servers could be there. Now there is a specific, I would say, for example, it is also
very important when you design the server. So like each server having an access to particular tools
will also be important. So let's say you have a server design particularly for all the databases you
want your AI agent to connect to. So you put all of those particular database tools into one server.
Now you have another server where you want to put all the files. So you make all the servers also
independent of how the services require it. Now this is also one another case. Let's say you have
two types of database, one type of database is like the relational database, another kind of non-
relational database. Now you have multiple agents running into the oral system and one agent
requires both, another agent requires only the relational request. So in that case, it is advisable
to have one server only having access to relational database, the other server having access only to
the non-relational database because giving both the MCP clients access to all the databases
available, there could be in some cases that there could be certain data privacy settings or
configurations that needed to be controlled. So that's why separation of what access to be given
inside the MCP servers exposing the capabilities like file access, database access, AP access is
also very important how you design it. So, and yeah, another point to note would be and host
application creates and manages this multiple clients as well. So when you have something like,
let's say Claude desktop, so Claude desktop, when you install it, it was going to be having an
inbuilt MCP client

### [18:16]

attached with it and the case would be, let's say you're designing an agent within something like
library or a framework like Google ADK. In that case, you can create the clients whenever the host
application starts running. So due to it, we say that a host application creates and manages this
multiple clients with each client having one-on-one relation with a particular server. So like in
the last slide, as we saw each client or one client can connect to servers with a one-on-one
connection persistent JSON RPC version 2.0 connection. Now, understanding the roles of the different
like in the model, we had host, client and the servers. So each of them have a certain specific role
or I would say each of them have certain control access or the overall system. So one of the few of
the things that the host gets to do is create, manage and control multiple client instances. So like
you can think of something like, host has created a client, the host depending on certain
programmatic or certain rule-based system can restart, delete a particular client as well. That sort
of capability the host should have. The next part would be handles connections, lifecycle,
permissions, security policies. Now, with respect to permissions and security policies, something
let's say for example, you have certain tool. Now you want only give the MCP access to the clients
who have like authenticated certain payments or who have been logged into your service properly. So
all those permissions, lifestyles, security policies should be controlled via the host. It won't be
able to be managed by the client. The client won't be able to say that

### [20:17]

I cannot fulfill the request and this user is not allowed to run the particular MCP server. The MCP
client should not be the one doing that. Your host should be the one controlling when the MCP client
gets exposed to the user to use it, right? And coordinates, AILM integration and aggregates context
across clients. Now, as we know, the host could have a front end. The host could also have a back
end, for example, and that back end would be the one, like your open source models, closed source
models, like let's say you have the Lama 3.2 model running again, and this model is now like having
the MCP client where your LLM system is there, the code you have returned, the LLM where it is
residing, along with that, whatever MCP client it is connected to, that client LLM integration and
everything would also be maintained by the main program host. Now, with respect to client, the
client would maintain one stateful session per server, as we already know, manages protocol
negotiation and message routing. So in the further slides, we'll see how it negotiates with the MCP
server and creates a message routing kind of a system. And it also enforces certain sort of security
boundaries and handles subscription and notification. So the subscriptions are not, with respect to
what the kind of host-based security we're talking about, these are subscriptions or notifications,
particularly with respect to the MCP servers, like when the MCP server is ready, when the MCP server
is blocked or not working. So this kind of security setups and things the client would be able to
manage upon, but not the one that is related to the host-specific controls. And the MCP server would
have the main primitives or the main features, tools, resources, prompts.

### [22:17]

It is focused and it is more focused towards the independent services, local or remote. And it
interacts with the client also for sampling. Now this is, again, another concept and sampling is the
one major reason why we wanted to have a bidirectional communication in our MCP protocol. The two-
way communication model requirement came also due to the sampling process. And also the execution
part is also what the server will do. So let's say there is a tool that runs a function and returns
the response back to the client. So that kind of execution would happen at the MCP server end. And
MCP server also must comply with the host-different security constraints, if any other, like data
request access or data table access or something, all those kinds of different security constraints
MCP server has to fulfill. Now the point which I was saying, the sampling parts. So the sampling is
something where, for example, let's say if I have to give a particular example, let's say the MCP,
like there was a user that was working on a UI, the UI you considered as a MCP host, sent a request,
that request got passed to the LLM, the LLM agent is working, the LLM thought that, okay, I need a
MCP tool to use upon. So the LLM agent uses the MCP client to connect to the server and run the
particular tool over the MCP server. So in that process, whenever the server is running something,
the server identifies it has some unstructured text, like the server received unstructured text, but
the server wants certain sort of a string-based or a markdown kind of a structure to respond back to
the client. So here what the server does is, server sends this sampling request to the client

### [24:19]

and host to trigger LLM. So LLM decided it needed a MCP tool to run, it sends the request. Now the
MCP server says that, hey, I can do this, but I need the input in certain specific form if the LLM
can provide it. So MCP server sends the request back to the client, the MCP client here, along with
the LLM, the host invokes the LLM, processes the request, like the request, let's say for example,
requiring the particular text into markdown. So what will happen here, the LLM at this particular
point would get a request something like, please turn this particular text to a markdown format, it
will convert to markdown format. And then again, the client will send the updated markdown format to
the server, so you can see server receives the result, reviews the output, and can make follow-up
requests to the client back, or will run the tool and send back the final response of the MCP tool
back to the client. And if the response is correct, the LLM will process it and create the final
response for the LLM to generate the response upon. So that is how the sampling works. And the same
reason why we wanted to have a bidirectional flow here, when we talked about here, like the JSON RPC
2.0 allows two-way bidirectional communication model. And the sampling is the one where server
initiates and acts as a client, the client acts as a server, processes certain requests from the
server, the LLM runs certain kind of action based on the MCP server's request, and returns back the
results back to the server to process the tool request or any sort of request the server wanted to
work upon. Now, this was with respect to the overall MCP architecture, what we have. Now, still, a
lot of you might have queries like why we still don't use this traditional

### [26:19]

or the standard MCP, sorry, the standard function calling or tool calling like our services we had.
So we'll try to see the L cross T problem and how MCP is solving it, right? So, for example, without
MCP, what we needed to actually do is that each MCP should, sorry, each of the application or an LLM
or an agent required to build a separate integration for every tool. So let's say we have an LLM, we
have four tools need to connect with everyone. So it used to be one LLM connect to one tool, same
LLM connect to another tool, same to third tool. So this used to make N number of connections. But
with respect to MCP, what we will have as a more better version is that the LLM will connect or have
an MCP client. This MCP client connects to the MCP protocol. The MCP protocol, the gateway connects
to the MCP server. So each of the client makes a one-on-one connection with MCP server. So to
understand it more simply, let's say we have three AI applications and four tools. Now here, if you
see, one needs to connect with all four. So one, two, three, four, and three, four. So the 12
connections or 12 integrations we need to make with all the four tools. Now, one of the, another
also important thing would be, let's say I created this chatbot. This is particularly in Lang chain,
this created in Lang chain. Now I switch to another library. Now that library has a different way of
integrating the particular tools. So I would need to rewrite certain code for these tools through
which I can attach my tool to this particular chatbot. While also I need to maintain the other AI
applications

### [28:20]

that are already existing. I would also need to maintain a way that these tools, even if I'm
accommodating a way to connect to the chatbot that is now written in a different specific language
or a different specific library, I need to also maintain it. So there would be a lot of issues with
different libraries or when you have different multiple AI agents, each of them requiring separate
connections. So the cross connections would require a lot of different integrations difficulties
when you have different libraries, frameworks, all coming into play together. But with MCP, what the
benefit you would get is each of the application would connect to the MCP protocol once so one-on-
one connection and MCP protocol connects with each of the server one-on-one. So what would happen is
you would only have three plus four that is like this total seven connections would be made, three
from the client side, four from the server side. So MCP client connected to MCP protocol once done,
the servers connected once done. So now even let's say I wanted to change this particular chatbot to
a different library. I would only need to implement the MCP client and connect to the protocol. I
did not have to make any changes to my servers because now the servers are independent of what the
particular library, this chatbot works upon everything because the client is something I have
created attached to my AI application. The client connects to the server protocol, server protocols
gives the access to the server. So adding MCP decreases your number of integrations you need to make
or the complexities you need to handle while you want to have multiple agents, some agents built in
different library, some agents also could be residing locally, some agents running in cloud. some
tools also running in Cloud, some tools might be there available locally. All of these things,
different versioning,

### [30:20]

different libraries, different issues, integrations of issues, everything can be easily handled when
you have something like MCP protocol, which could not have been easily done when we are not using
MCP, and we have something like a standard tool calling and everything. Also, another important
point would be, let's say I have this AI application for this particular Calendar API tool to work
upon. The code should also reside with whatever library I have written with Chatbot. So let's say
Chatbot is written in LangChain, I would need to write the Calendar API. The API is already written,
I would need to write a code to call this particular API in LangChain and integrate with Chatbot.
Now, in case of MCP, the Calendar API inside the MCP server can let's say run in Google Cloud. The
Chatbot is running in AWS, even though they're both running separately in different spaces, the code
is not at all residing along with Chatbot. Via simple MCP connection, they can still work like the
integrations can still be made. So MCP will also give you power for tools to run locally or to run
the tools on the remote service and still able to connect with them. So that is how MCP gives you a
lot of, I would say, independence over how you want to create a system tools, like where you want to
put them. And I guess another important idea would be let's say, there are multiple teams working on
a project, some teams built a particular tool service, then other team was working on a different
agent, now they want access to the tool. So the first team can simply drop in the MCP server into a
cloud and the another team, they won't need to get the code from the other team, implement the
service into their local system and connect to the agent. They would just need to set up an MCP
client

### [32:20]

and they can directly connect with the MCP server from the team one. So that sort of a possibility
also exists. So multi-team collaborations or multiple projects or two independent projects calling
the same MCP server, that sort of a process can also be applied here. Now, the oral communication
flow, like what happens exactly when someone is calling or when someone gives an input request and
how that request reaches the MCP server. So the host application plus the LLM, it like we get the
input request, like whatever input request, if there is an, there could be LLM, there could not be
LLM here, it's kind of like dependent on how the host application is there, something like let's say
cloud desktop. It has the host application with the LLM itself. So if there is any post-processing
required, the LLM post-process it, it gets sent to the MCP client. MCP client makes the connections
with the server. So how does it start it? It's first connects, makes the request to the MCP server
to connect, it connects. Then once the successful connection is made, it makes a query to discover
tools to the server. The server returns a lot of tools. The MCP client now based on whatever the
input was there from the host application that was received, based on it, it will send certain
requests to run the tool. The MCP server will then return, or I would say will execute the
particular tool what was requested and return the response. And once it has returned the response,
MCP client will now check, like if there are multiple tool calls required or single tool calls based
on it, it might now request for some multiple tool calls. Once all of them are there, it will send
back the final result to the host application. The LLM will aggregate all the tool responses and
generate the final response for the user.

### [34:20]

So this was with respect to how the communication flow will happen between host client and server.
The communication flow with respect to JSON RPC would be just between the client and the server
would be. The client will create a JSON RPC request with method, parameters, IDs, a lot of different
things, like the inbuilt features, the JSON kind of a structure it will build. It will send the
request to the server. The server will process the request. It will create a response. The response
gets sent back to the client. The client acknowledges that it has received the response, response
receives, and passes the response message and sends back to the host application. So whatever tool
call results there will be there, it will send back to the specific client. So this is how the
communication will flow between the client and the server. Now what exactly this JSON RPC request
response structure would look like is, so when the client sends the request, it is going to send the
request in this particular format. So JSON RPC version two, what is the ID of this particular call,
what method it is saying the tool slash list, meaning it is calling for what are the tools the MCP
server has. If it was resources or prompts, it was going to send something like resources slash
list, tools slash list, something like that. And if any parameters are there, it will also send the
parameters. Now this particular request gets sent, the MCP server receives it and starts processing.
When it has processed the request, it is going to return the result back to the client. So it is
going to return a response like this. JSON RPC, the ID, the result of the tool calls. So like
something like name, what tool call was there. So get together, what was the description. So like as
the client requested, what are the list of tools available for me. So MCP server here is just simply
returning the list of tools for the MCP client to pick from and again ask the MCP server, which tool
the MCP client or the host application the LLM wants to run. So this is the process like the request
response structure

### [36:21]

exact JSON RPC response request structure would look like. Now, a few things like this structure
what you see here right now would always be the same. Like this is the structured standard format
the JSON RPC requires. And as MCP is also built on top of that, it is going to follow the same
structure. Now, one thing about the MCP servers is they have some sort of incremental updates,
meaning what the previous tool call happened or a previous MCP client has sent in a request, all of
these things, the MCP server takes it and stores it as a stateful process. So when it stores them,
they can send notification or stream partial results as they become available. So for the same
reason, we also call MCP servers as having a stateful context. Error handling, so MCP server already
like whenever we go through the programmatic way of building the servers, we define all the steps,
like this would be the input parameters, this should be an integer input value, this should be a
string input value. So the MCP client, if it does not get all the parameters that the MCP server
requires for a tool to run, the client will specifically say to the LLM to ask the user what exact
inputs it is missing and based on those missing inputs, like whenever the user provides them, the
MCP client can again forward that process back for the server to work upon. And like it also has
certain processes like cancellation handling, like request can be canceled. So like whenever from
the host application, user cancels a particular request, the MCP client can cut off the connection.
So all of these things, other things like, all the cancellation handling, error handling,
incremental handling, the request response structure, everything happens by the same JSONRPC
structure, like JSONRPC ID result or the method parameter structure.

### [38:23]

Now, there are also a few things you might have noticed when reading about MCP, one is like MCP is
also equated something very similar to the USB port for AI, why? Because as USB port is something
like we considered as a universal port kind of a service, like it can connect to any sort of, I
would say it is sort of a standard interface that allows us seamless connections. Same way MCP is
also something very similar that acts as a standard interface that allows us connections along with
protocols, procedures, services, everything mentioned between the LLMs and all the MCP server access
that we have. So in short, MCP is going to allow the AI models to interact with external tools,
databases, files, APIs, everything without some sort of a very extensive configuration, similar to
how the USB-C devices connects different types of multiple electronic devices seamlessly. Then
stateful context, the one I was talking about when I was mentioning the incremental updates part. So
we will compare it with the stateless REST APIs. So if we know what the REST API is, like let's say
you have built an API with some sort of a Python framework, like fast API. So in that case, for each
request you share, if you don't have something like a memory or something, each API request will be
independent request with respect to MCP. MCP also maintains a particular session ID or ID through
which it takes some, I would say incremental updates. So here, if you see, if I zoom in a bit, so
let's say there was this particular session ID, it's going to store certain histories, like yeah,
whatever. a process that happened, so like history A, history A, like server remembers the certain
context, so less data is sent by the,

### [40:25]

I would say client across calls and there would be certain incremental updates. So let's say
whatever the multiple conversational calls are happening between the client and server, the MCP
server would keep a track of them. So whenever the LLM is going to read of all the calls made, so
LLM like residing at the host place client side could identify that MCP server tried to run this,
but it was not successful because there was an error with the input, the LLM via the MCP client
sent. So due to this incremental interaction updates or the states that the MCP server stores, the
LLM can figure out what exactly issues are happening and the MCP and can send in proper requests and
everything. So these are also a few features that are also missing from the tool calling or the
function calling side as well. Now comparing the main MCP versus the tool calling part. So the main
comparison points we would have is, so let's say schema design, like how do you define the discovery
of the process? So with respect to tool calling, it is usually hard-coded in the prompt or the code
with respect to MCP like we saw here into the process. The host application, when it has access to
the client, the access connects to the server, gives us a list of tools and everything by this
multiple connections that is made with the server. So same reason, it would be discovered
dynamically during the particular call process that whenever the user gives a query, the MCP server,
tools, access, everything would be discovered dynamically during the ongoing process. Tool location,
so tool location for the, like when we have certain tools, so same process or the same location as
LLM. So tool will be located there. For MCP, it could be residing at the same location

### [42:27]

or it could be residing separately on a particular different server or it could be altogether
different server process. Now the transport, so tool calling does not have a transport protocol. It
is an in-memory service. While MCP provides us with three different types of transport protocol,
these standard input-output protocol. So whenever, let's say, you are having some agent running
locally, you don't want to expose the agent via the protocols. We can use something like STDI
protocol. And it has two protocols, SSC HTTP for like whenever your MCP is running on this
particular server and from that particular server, we want to have the LLM and the MCP connection
running. So in that case, we would have SSC and HTTP web protocols where it can communicate with the
web. But to note, the point to note would be SSC is now deprecated. HTTP is the one that the latest
Fast MCP or the MCP documentation sees to use for the web protocol. Now with respect to the state
side. So tool calling, as we know, or as I already mentioned, it is stateless while MCP maintains
the stateful context, like here in the example, as we saw. Then reusability. So tool calling is like
one LLM only while any MCP compatible client can call this particular any other MCP server. So the
same L cross T problem. So one tool we have, the particular one LLM I have connected to. So that
single LLM is only going to call the tool for the another LLM. If I want to attach the tool, I want
to make another integration request for it. While with respect to MCP, once and MCP client is
connected to one MCP server. So let's say for example here, let's take one important example. I
guess I missed it during the previous slides. So when an MCP client is connected to a server,

### [44:28]

the server can have multiple tools. So let's say a server had three tools. Tomorrow I want to add
one more tool. So in that case, I do not need to make any code changes to the host application. I
can just add a tool to the MCP server and just update the MCP server. Now tomorrow or whenever the
update is scheduled after the update runs successfully, the MCP client will automatically
dynamically discover during the process that now it has four tools. So it can call the four tools if
required. So that is how once you connect your client to the server, that becomes a very easy
integration process. Like it is not bounded by one particular LLM or the integration will not be
totally specific or hard coded to use it. And discovery, like the manual per integration discovery
of the tool calling happens. Like there's also something we discussed during the first point and the
reusability point. And discovery quite automatic by the tool slash list. So the tool slash list we
saw here when the client sends in the request to the MCP server. So that is how the oral process
will work upon. Now when exactly to use what? Now MCP is something that might not work the best in
all the cases. So for example, let's say you have some single LLM application tools also available
in the same code base. It will be more better or easier I would say to initialize a tool calling
request. In future, if you get some external server access or something kind of a requirement in
that process, you could convert the tool calling to MCP particular scenario, but it would be an
oracle for the simple application. Then if your tools need to be shared across multiple apps or
agent, MCP would be more easy. Like once it is set up, tools can be exposed once and can be used by
many clients across apps or agents. Your system requires dynamic tool discovery at runtime.

### [46:28]

So MCP would be better because it can do dynamic discovery at runtime instead of the tools that
would be hardcoded at the development of the application. You want to have some quick prototype
without any extra infrastructure overhead. In that case, tool calling would be the one very fastest
to build and iterate upon the experimentations. No additional setup would be required. MCP would
require an additional extra layer setup, authentication setup, and everything you might need to add.
Then tools need persistent state between calls. Like with respect to tool calling, you can add a
state, but you would need to also then figure out where you want to store, maybe could be something
like MongoDB or something like Postgres, where you store the state of the tool calling. While with
respect to MCP, the protocol comes with an inbuilt persistent state mechanism there to handle this
kind of a thing. So if that kind of particular tool persistent state requirement is there, go for
MCP. And exposing tools to external consumers. So nowadays, we also see a lot of companies. For
example, let's say we take an example of Slack or certain things like ZIP or the CRM tools. They all
have now started building their MCP servers. So those MCP servers can be consumed by any MCP client.
So in case you want your tools to be consumed by agents publicly, you can build an MCP server and
put it on a web service or a cloud and expose it to any number of consumers you want. So this MCP
now here will be acting something like very similar to how your APIs, like earlier people used to
expose APIs, people used to call APIs. But that was with more respect to the web-based, or I would
say the web services kind of architecture. For agents, similar thing we now have is what we call as
MCP. That would be exposed as a tools prompt resources

### [48:32]

services over web. And any agent, if it is publicly available behind a paywall, that is kind of a
connection you would need to figure out. Certain MCP servers would be paid. So they would require
some key to check if the particular user is authenticated or has the usage rights, the paid plan
rights or something. And based on that, the AI agents from over the web would be able to connect to
the MCP servers. Now, coming to the main four features of the MCP. So the main four features would
be the resources, tools, prompts, and sampling. Tools being the one very highly used, or the, I
would say, service that is continuously used. Like, or I would say the majorly used, the other
primitive features are not that much used. So for example, resources. So resources is something that
is controlled by the host application. So in the host application itself, the people will be given
certain example documents, certain database access, everything. And people can read those documents
and everything based on it, like work with the agent or the application. So that's why it represents
static or dynamic data the LLM can read, or even the users can read access through URLs like files
and everything. They read only in nature, and it is controlled by the host application. Same to
that, prompts. So they act like the predefined prompt templates or workflow that developers would
have exposed. And they are also residing in the application UI, like you would have multiple
available prompts, summarize document, draft, reply. So they can be also controlled by the user, the
human that is working on top of the application, like the end user would also be able to check out
the prompt, send in the request, select a prompt, and add the user's input to the prompt.

### [50:35]

And that particular new prompt would be sent to the LLM to process upon. So selected by the user
before the processing begins, helps at the initial context of the LLM response. Then coming to the
main part, tools part. Tools would be residing over to the server side, not to the host application
side. So usually the tools are identified by unique name. They're defined with the JSON schema for
input arguments. So for example, this is a tool definition, like what is the name of the tool,
description, what is the input schema. So this particular tool takes the input, city, unit, and
enum, like what exactly Celsius or Fahrenheit is required and is required city, meaning what is the
required parameter, what are the optional parameters. Those all things can be defined here in the
tool call. And this tools would be executed by the server, which returns results in text or a
structured JSON format. So example, client sends the input request. First, the client will read the
JSON schema of the server, or sorry, the particular tool, then it will send the request. Request
from client sends like this, name, tool, get with the argument. So it would have city, Paris, unit,
Celsius, it will send it. Then it goes, the response from the server would be based on the input,
like it will process the input and this kind of response will be generated, the temperature unit. So
this kind of a response, it could be different, but the response would be wrapped in a JSON RPC
structure. So it would be like JSON RPC ID and response. And inside that response, this particular
JSON would be available for the MCP client to consume and send back to the host. So that is how the
tools process work. Their callable functions or actions, the LLM can invoke through the MCP client.
Then the, sorry, yeah, the MCP sampling part.

### [52:39]

So the sampling part where a mechanism with the server can ask the client process and action using
the LLM. So like, let's say a client set in and input request the server read it and now it requests
some LLM help. So the MCP server is going to request sampling, ask client to run LLM with a prompt,
sends it to the client. The client runs on it, like the LLM generates some response and the client
sends back that response, either text or JSON back to the MCP server. So it enables more dynamic and
coordinated bidirectional two-way communication between the client and server. So this is how an
example of the server-client interaction works. The server sends something like sampling, create
message, parameters prompt, write a follow-up email to the customer. The client, like the LLM will
generate a response and the client will send back a response to the server like this. Results
subject your order confirmation like this. This is how a sampling process would work. Now, start
with the code walkthrough, but before the code walkthrough, I will walk you through a few of the
technologies that we're going to use just right now. So, with respect to the code, we'll be using
the official MCP SDK along with the fast MCP. So initially when the MCP protocol was released, it
had an official SDK. Then in a few days, fast MCP as a library was released in Python to help
simple, I would say creation of MCP servers and clients. So what fast MCP, the version one did was,
it allowed all the possible things that we have discussed till now, creation of MCP clients,
servers, creating MCP servers that can expose tools, resources, prompts, give us access to use
standard transport protocols

### [54:41]

like STDIO, SSC, HTTP protocols, handling all the MCP protocol, lifecycle events, stateful context
and everything, and provided a simple and unified API for MCP development. Like you can think of,
like fast MCP is built as an abstraction over the official MCP SDK to reduce the coding efforts to
build the MCP client. Then we got the version two and version three is the one latest that is
running right now. So they added more MCP client features on the MCP server side, they started
giving the MCP authentication systems and everything like how we used to authenticate a particular
user request using API, same kind of authentication setups and everything is now been included with
MCP. It is still under improvement, but the JWT authentication setups or everything, or third party
authentication setups are now being a part of the fast MCP process. It also allows the integration
with open API and the fast API. So fast API, APIs that you might already have that can be converted
to MCP servers quite easily. So there's those kinds of native integrations are also available. They
have also improved the modularity and extensibility, meaning a lot of code was or a lot of code
syntax was changed from the first version. So you would see a lot of more simplified commands like
you might today, you might not need to work up on with fast MCP version one, we'll directly work
with the version three here in this case. And it gives a better performance reliability developer
experience compared to the version one because earlier the docs were like scrambled a bit and there
was a lot of theoretical portions and the actual practical portion. Well, the latest version will
give you documentation about everything that is available and possible. And also as for the official
repository, GitHub repository,

### [56:41]

fast MCP version two or more is a recommended upgrade part for any developers who are building any
sort of a new MCP systems. And whenever you're going to receive the particular PDF and the code of
parts, you can take a look at the original GitHub repo where the fast MCP is there. Now, once we use
the fast MCP as I would say library to create and I would say MCP server, we would be running that
locally first and we'll also be using cloud desktop to call the MCP server, the MCP tool that we've
built inside that and like cloud desktop that will be running locally. Now, to give you all an
experience of how this can be deployed to cloud, we'll be using Hugging Face Spaces. So Hugging Face
Spaces is a free hosting platform. They can run machine learning, deep learning, generative AI, MCP
kind of a service. So they technically support Docker, Gradle and Stimulate interfaces. So we'll
convert our MCP server to a Docker small container and that Docker container would be pushed to
Hugging Face Spaces. So every space gets a public HTTP URL. So whenever we're going to publish into
the Hugging Face Spaces, we'll either expose our MCP server through SSC protocol or the HTTP
protocol. While when our MCP server is running locally, that could be simply exposed by the STDI
protocol. Then like a few of the features of Hugging Face Spaces are they run on a shared CPU, like
there is a paid packages where you can run your Hugging Face Spaces on GPUs, like how the AWS GCP
Clouds allow you to. Apart from that, like Docker runtime, you can run Python based servers in the
Docker here, or you can also run servers in other languages as well.

### [58:45]

We'll give you public HTTP URL, so accessible remote MCP server endpoint. And by default support
that would be explored here is 7860. And there are a few things to consider is that it is only going
to be great for demos and learning. The grid is not certain scalable service. So production or high
traffic things that you should not be putting here, you can definitely do it while learning. Once
you know how to put it in Hugging Face Spaces, the same process you would need to do for any sort of
other clouds like AWS GCP. And then you can build it more towards the production side of it. Then
using the Cloud desktop as the MCP client. So first thing would be to install the Cloud desktop. So
you can simply visit or go to Google search Cloud desktop from the official Cloud Entropic website,
install Cloud desktop. So this is the logo you can see this, once you have this Cloud desktop
installed, it acts as the MCP host plus client. Any local server, MCP local server you have, it will
connect to it via the STDIO protocol. For any remote server, it will connect via the SSC or HTTP.
And the LLM will process everything. So like any MCP processor, it will work here. And let's say.
like how this MCP or sorry, the Cloud Desktop connects to the MCP servers. It has a server
configuration file, Cloud Desktop Config.json file. In that, we have certain structure like this. So
it is like a JSON structure where MCP server, you have your name of the server, what command we have
to run. So for example, if you have a local server, we define the command Python argument, what file
to run for this particular server to run. And let's say if you have a remote server, like the server
residing on a particular different server over a URL. So you would need to provide a URL and it can
connect to the particular URLs directly if it has the access.

### [1:00:45]

So by this, by just changing the JSON inputs here, you can allow the Cloud Desktop to connect to any
sort of different MCP servers that are available publicly or running into a local setup. So it
automatically discovers and surfaces tools for the LLM to use. And the Google ADK library. So we'll
use Google ADK library to just start an ADK agent, basic agent, and whatever server that would be
using for our use case today, for the code MCP server demo that we'll see. The same server will
connect with the Google ADK library. So to give you an example of how certain tools that already
comes with a inbuilt MCP client, how you can use it. And also if you're programming it, so let's say
you're programming with some library like Google ADK, how you can, based on the syntax given by the
library, for example, Google ADK, they would have a particular syntax. So based on the secret
syntax, how we can just create initialize the client in the Google ADK and connect to any MCP server
that is running locally or onto the remote. So what exactly is Google ADK? Google ADK is an open
source Python framework that is built by Google. So Google ADK also has an A2A protocol. So A2K is
something similar to how MCP is. MCP is communication between LLM or agents with the tools. The
Google built a protocol A2A for communication between multiple agents. So for people who are already
a part of Academy Live, they would have seen the A2A protocol session and they would understand what
exactly I'm talking about, how Google ADK garants the A2A protocol. And agents are built as
composable, like a standard units of logic and supports for tools,

### [1:02:47]

local tools and everything, also allows connection with the MCP server. So you can also have
multiple agents connected via A2A and each of the agents separately connecting with the MCP servers,
that kind of a setup is also possible. So yeah, let's jump to the code part. So like after the
session, you will receive this particular folder, will have three different sorts of demos here. So
the first one, so okay, before that, what we'll do is let me show you this. So let's say you go to
Google, search for Claude Desktop and go to main website, download Claude and just install Claude
from here, download for Windows, you would have Claude Desktop here, install Mac, Windows or
whatever you want to install. Once that is particularly installed, when you open it, so this is how,
you would have the structure and you go here onto the right side, sorry, not here, not exactly. You
click on the very top left here, click on file, click on here, settings, you will go to this page.
Onto the developer part, you will have this local MCP service setting. So this particular local MCP
service would specifically be only available for the Claude Desktop to use. And when you click this
edit config, it will take you to the location where exactly the Claude Desktop config file is
located in your system. So this Claude Desktop config file will be located here and you can just
click it and this is kind of Claude Desktop config.json is here. So we have a question, what's the
use case of the demo?

### [1:04:47]

So use case of the demo is how exactly you can connect Google ADK library with the MCP server, how
we are going to use Fast MCP as a library to create MCP server and also deploy it over the hugging
face spaces. This is not exactly a demo of building AI into something. This is directly specifically
concerning only with how do you create an MCP server and how do you connect the client to the
server. So now starting with the first part is the first demo. So let's say I have something like a
MySQL database now there are certain MCP servers that are already pre-built by the companies. For
example, MySQL, they already provide an MCP server for them to build to. So in case I want to use
those pre-built servers directly, what I can do is, so let's say in my Claude configuration, so each
of these folders will have a separate readme, you need to go through the readme. So let's say I go
to the first readme. So what exactly does is we're trying to connect a MySQL MCP server to Claude
desktop. And what access we will give to the Claude is, the Claude will be able to read and query
any table in the connected database, describe tables, schemas, run queries and everything. So that
will be the access we will be giving to the Claude via the MCP server access. So you would need to
install Claude desktop, you would need to have the MySQL running locally and once you have MySQL
running locally perfectly, if you do not have any database into a system, there is a SQL file given
to you, you can use the bash command of MySQL, this will load a MCP demo database table into your
system, customer products and orders. Or if you have already and pre-built tables,

### [1:06:47]

databases into a system, so let's say if I have, open a MySQL workbench, let's open this. So let's
say I'm going to use this particular store, which has certain tables, like a customer manufacture,
products, region, sales, managers and everything. So this is the store database that I want to
connect to. So how will I be able to have my Claude desktop connect to the database that is running
locally inside my MySQL database? So how I will be able to do it is, inside my Claude desktop
config, so for example, when for the very first time, when I would have this, this server
configuration would be looking something like this, so this is how it would be. Now, when I'm
working on top of this, like for the very first time, when you have not connected any MCP servers
here, this is how the servers would look like. Now, when you're using some MCP servers that are
being provided by other providers, what you would need to do is, you would need to either visit the
documentation, visit the GitHub, and from the GitHub, you would be able to find the configuration.
So what you can do is, you can simply copy and paste to your JSON configuration here directly. So
for example, I have copied this directly here and pasted it here, the few changes I have made here
is, the password, the MySQL database access, so let's say my user is root, my password is root, my
database name is tool, and once you add this here, so for example, let's say, if I want to actually
do something, what I will do is, I will just delete everything. I would close, or I would not
actually delete everything, I would just delete these parts. So this is my MCP server at this point.

### [1:08:48]

I will close Cloud, I will quit it, I will open the Cloud desktop. So now here, you need to click on
this plus symbol, you will go to here, add connectors, you will see, it will show you, like you
know, it will open up a screen like this, that means it does not right now have any MCP servers
connected to the Cloud desktop's client. So what you will need to do is, go here, copy this, we'll
go here, we'll paste this, now I will change this root, root, I'll put this store, so what this will
do is, it will locally install this MCP server MySQL, and it will connect my local database using
this environmental settings that I have provided. So what I will need to do is, I will need to quit
the Cloud desktop, I will need to reconnect with the, or I would need to restart my Cloud desktop,
so here, you would see particularly, it will take certain time, but yeah, now you see an error here,
you would see. MySQL it has started now you can turn off turn on like the MCP server like you want
to maintain the connection or not So let's say it is like I have started late. We just close the web
search now This my particular MySQL is running. I will just turn it off and I would say What are the
tables available in my DB? Store so it says I don't have access to database directly, right? Now,
let's say if I go if I start MySQL and just recent the message Just put it to hike

### [1:10:49]

So you can see for the very first time very very pretty using it would ask you certainly turn on
connector discovery So what do you need to just do you need to go turn on? But now here you would
see it has started writing and then SQL query so you can see the show and show tables So you can see
this tables response like what I did here was it gave me a pop right so turn on or something So for
the very first time when you do you would have a turn on setting like that So you would need to turn
it on for the client to discover tools So here you would we see that you would get all the same as
sales manager sales representation Transactions all the seven tables that was present in my
particular Database so let's say if I go to customers And let's say if I select customers where
let's say city equals to something like let's say Allen Park You can see there are five people right
so what I would ask it is How many? customers are from Allen Park City there is a question. I'm
putting it okay, so I made a mistake just a minute You can see it clearly says there are five
customers from Allen Park City. Would you like more details about this customers name? so that is
how look like the MCP client residing at the cloud desktop will be Connecting with the MCP server it
will write this particular SQL query this SQL query was sent at a request and this is what how

### [1:12:51]

The response it is graded and the response Execution time was being 3.3 micro milliseconds, so that
is how we can connect and server That is already created by someone and they have already given us a
excess via the NPX command settings So using the NPX command we would be able to directly install
this locally and we will be able to run it now The other type of MCP server where we create the MCP
server So let's say I have this MCP server, which I am using the fast MCP as a service to run it So
I have just tried to create or create a setting where I'm using a library Faker library From which I
will be generating certain fake data Like get basic profile of the user the user activity user
orders information So you can think of like each of these functions is there to is an API something
that returns certain information based on the username so Like that is how the API have created and
we also seeded it So consistent seed so same username always returns the same data So once I would
have this particular server running once it is started So for each of the same input or the output
will always be going to be the same So we'll also test it like running it locally running it across
the web service deployed over the I would say deployed over the hugging for spaces So how I'm going
to do is these are the functions which is like my programmatic functions that allows me to run All
these particular functions the main things we were talking about this from fast MCP import MCP So in
this case here, first of all also you would have this Recommended TXT you would need to install this
particular fast MCP and Faker As a library is into an environment first and once that those are
installed from fast MCP import fast MCP

### [1:14:51]

Then we will initialize the fast MCP as a MCP equal to fast MCP you would need to give a name to the
server So I'm just naming fake user data API Then for all the functions you want to create as a tool
you simply do is that MCP dot tool? The other tools everything you would notice it MCP dot tool MCP
dot tool So all of this these tools are now registered now To run it locally. So I have all this now
four different types of MCP variants I have created here one is MCP running locally one is MCP
running locally over HTTP for Google ADK library to call upon and MCP particular functions running
on hugging face spaces for plot desktop to connect or the Google ADK library to connect to so we'll
start with the MCP dot run that will run the MCP server locally so all the basic local setup
instructions are already given installing the UV library Creating the environment creating fast MCP.
I would just mention it Faker here Faker and to run the server We can simply do something like this
fast MCP run main dot py Sorry, I would need to go to demo to API MCP fast MCP run main dot py So
now here you can see what it is doing is it is running the server locally or the STLDI or standard
protocol now This don't give you any UI to work with So what we do is fast MCP also gives a basic UI
to interact with the tools that you have given without Even actually using any MCP client to connect
with so what exactly this inspector gives is so this inspector So this inspector will just know
we'll open it locally. So this is the kind of

### [1:16:54]

UI MCP inspector will give you so transport type STLDI or command fast MCP or running the main dot
py file You can do something like this connect here. So we'll connect to the MCP server So this MCP
inspector you can think of acting as a MCP client So now we've connected with our fake user data API
server You need to go to tools list tools. So here you can also see now like server notifications
Tools list so this is like kind of a method tools list parameters so this history shows something
that I have sent in as a client this server notification is something you would see what the Logs or
something information the server is generated during the process. Now, let's say I'm clicking on get
user data I'm going to click go to and say let's say I'm going to put user name as Chirag or
something and I would go here and we'll say run tool Here the output schema is type object
additional properties anything if like it depends on to your the schema that is the output schema is
very simple it is going to be JSON output and Once you click on the run tool tool result will be
success or failure now here for the username Chirag It will give you some data. So let's say full
name Daniel Davis. So like this is like as I mentioned already mentioned This is a fake data
generator service. So any time I would going to Put input as user name Chirag input This is the same
output because that is how I have designed my API to be consistent even though this is a fake data
So this is the same data that would be getting generated for all the calls Even if I'm going to call
from hugging face or any kind of a service So this is how tool requests like it will get the tool
and it is going to send back the data To the MCP client the MCP client will process the data with
the LLM And final response will get so if I want to add this particular MCP server to my cloud
desktop How I would be able to do is is let's say

### [1:18:56]

I'll open a new so CD demo to API MCP paste this So fast MCP install cloud desktop main dot py with
faker So what this does it it is going to add and server here directly fake user data API the name
of your server command UV where exactly this particular File is located when that py and with faker
we added is because what? Libraries my server depends on so if you have multiple libraries You can
say with faker or let's say you have multiple tens or twenty libraries So what you can do is you can
create a requirements dot txt file like this and you can say with Requirements dot txt something
like this also you can add so in this way it will also have your server running along with all the
Libraries that the server depends on So you would see command, UV arguments, everything, main.py,
file, transport, type, sg, dd, io, and what you will need to do is here, this one is close your
cloud desktop. I'll go to my cloud. Now, what I will do is, you can see fake user, data IP is now
active. I just close this MySQL one. I'll go back to my queue, and what I put in the request is, so
what tools are available for me? Also, you can check first. So let's say, order history is there,
right? So let's say, give me the order history for Shunack. So here it's asking, for the very first
time, any MCP server that you're going to use

### [1:20:57]

from the cloud desktop, it will request for an access. So you just select always allow once, or
something like that. I will just allow always. So for this particular fake user data API, it is
always going to directly send the request to the MCP server. So you can see, whatever post-message
request are getting generated, you would see an incremental post messages here. And here you can see
Chirag's order history is like this, laptop stand three, mechanical keyboard two. So total orders
five, total spent. So like this way, now you would be able to see. And the same thing, you can also
note it here as well. So let's say I go to user orders, so to Chirag, run tool. You can see, right?
Laptop stand, mechanical keyboard, same data that I got it here. The difference you can see is the
MCP server is returning this sort of a data, like it's a JSON structure. LLM is reading this JSON
data and it's generating a response for me like this. Summary, total orders, total spent. It also
give me a total of all the money spent across the order. So that is how the LLM calls the MCP tool,
gets the data from it and generates a response for the user of how the user like it. I can say it
give me something like, let's say most, or let's say the least price order for Chirag, please. Okay,
here it did not call the tool. It just used the previous memory and give me the list from here. So
let's say if I use it for someone else. Okay, let's say I will just use the name from someone from,
let's say Vedant, all right. So it called the tool, used the name

### [1:22:58]

and based on it, it has given the results. So let's say here you can see, it gave quite like five,
four, five products in the history. But as I only requested for one product, it only gave me results
for one product because that is what the user asked for. So that is how MC server can give a lot of
results, but based on the user's input requirement, the LLM would be the one what exact final
response to give to the user back is what the LLM as a tool will decide. So that is how the process
works here. Now that this thing was running locally, now put it for the cloud desktop to use, or I
would say to deploy the server onto a remote service. So what we usually do is we have hugging face
spaces. Let me just go to hugging face. I'll go to spaces. So I'll case, if I can see my spaces.
Yeah, so these are all my spaces already there. So let's say I have my EPM CPU already created. So
for the very first time, you are let's say creating and space, all right. So what you do is go to
your profile, click on new space. Yeah, you would need to give a space name. Like if you want to
give a description or something, select Docker, CPU basic, keep it everything public, everything
safe, and just go ahead and create the space. So this will create a space. The next step you would
require to do is you would need to go to your file and upload all the files that you want to push it
here. So now what here we are doing is I have my main.py, I have my requirements.txt. I definitely
need to push both of these files to my hugging face space. Apart from this, I also need to create
this Docker file because this Docker file will be the one working as a container that will run my
server. So what I need to do here is I would install a Python 3.11 slim version work directory
application.

### [1:25:00]

So there's all Docker specific commands, copy the requirements.txt, install all the requirements
that are mentioned here, copy main.py file, expose the 7860 port, and the command will be python
main.py. Now here, note that inside it here for my hugging face server, I have exposed it via the
HTTP transport protocol, right? So for my cloud desktop to use it particularly, I would need to run
it with an SSE only, right? So cloud desktop has a particular requirement that whatever server I'm
running, it has to be SSE. So here, what I would change is I would change it to SSE, host 0.0.0,
port 7860, because that is also the same port we are exposing via the Docker file. So I'll just
commit changes to main. So whenever you are going to add this for the very first time, the hugging
face space will read the Docker file and will start the process. So you can see something like this,
it is building. So building your Docker file and everything, it will be running. So when it gets
start pushing image, exporting cache, yeah, when it shows a message like this, it's running at this
particular port, that means here with transport SSE, it is running, okay. So we need to do one
thing, go to here, like this particular settings, the right icon to the settings, click on embed
this face, and then from here, you need to copy this particular link. So copy this link, and you
would need to save this particular link somewhere, let's say I just copy this link and copy this
here. Then the next part is you need to update your cloud configuration. So let's say I'm just going
to find here,

### [1:27:01]

this is my here, and I would need to add a particular configuration to the service. So we need to do
this manually. So I've already added the command to do it, how, what exactly is the structure you
need to provide. So the structure you need to exactly provide is you need to copy it from this API
HF, copy it till here, and we'll just paste it. So what goes here is API HF, that is the name I'm
giving it, like this is like a hugging face, like this particular API is running over the hugging
spaces, command NPX, argument would be MCP remote, the URL that I copied, and whatever protocol that
I was using would be followed by that. So slash SSC, then I would add transport. So this is the
whole URL, slash SSC, what transport I'm using, SSC only, environment, this is you can keep false or
true, that is fine. And once you add it to again, once you again add it to your cloud, I would say
configuration, we'll just restart the cloud, so that this particular MCP server is registered with
the cloud desktop. So I'll go here, it will take some time to restart every processes. Yeah, and now
you can see API HF, it is successfully connected. So as both the services, fine, both the fake user
data API HF both are same, just that the fake user data API is running locally, here inside my
service, and the API HF is the one running on hugging face. So for example, if I want to check if it
is actually making a call here, so you can click on the locks you can see here, and as soon as I
let's say make a request from here, so let's say I'm going to go here, let's say you me profile
information for Chirac,

### [1:29:07]

allow it to use the server. Now here you will notice you would get a post request here, or did it
use the local one? Just a minute. Okay, maybe not here, okay, got it. I guess that particular
service will only work in case of an HTTP service, okay, got it. Okay, right. So you can see it has
got give you the details, Chirac, profile information, username Chirac, Daniel Davis, so this is all
what is coming from the, okay, maybe I would close it. I'd use it for someone else. Let's say, but
it should be done now. So yeah, here you can see, it has give you a new post request. So that means
now this cloud desktop went search for available tools. It made get user profile for EPHF. Now you
can clearly see loaded for EPHF tools. These are all the tools that should show, it saw the function
profiles. Then it goes back to the client. The client says that it needs to use the get profile. So
then it goes and calls the tool, this particular username, for getting the with us browser. This is
how it is working for the, like first it get a list of tools, then it sent a request for a
particular tool to run a console. That is how it can take multiple tool calls, one tool call, two
call, three tool calls. So that is how the client server can continuously work bidirectionally. Now
in case the third part of the demo,

### [1:31:08]

sorry, I closed that cloud desktop, reopen it. Now this was with all respect to the cloud desktop.
Now let's say you already have some agent. So let's say you have some agent like Google ADK. So
Google ADK, we have some like agent and everything, all the things created from Google ADK library.
Let me just also open, read me agent. So Google ADK directly gives you the MCP tool set as a library
part. And it also gives you another service, streamable HTTP connection parameters. And these are
all the other libraries. So let's say, I'll just put it separately. So these are all the imports
that allows me to create an agent in Google ADK. And these are two imports that allows me to create
the MCP connection with the service. So with respect to how I create the agent is, basically, I
would create an agent, give an app name, give a model instruction, what the agent does is, so agent
that queries user data, I give an instruction that you're a helpful assistant with access to fake
user data API and what the things it can do. And in the tools, I will specifically pass the input
for MCP tool set. So MCP tool set, I would create like this, MCP tool set equal to MCP tool set
connection parameters. I will specifically mention streamable HTTP connection parameters. Now here,
you need to give URL. URL for the one that is running locally or the service that is running onto
the Huggings for Spaces. So to run this, I would need to actually make two changes. So let's say I
go to Google ADK, I want to run this locally, right? So when I'm running this locally, sorry, yeah,
the main.py file, I would not run it over STDIO, I would run it over the transport HTTP locally.

### [1:33:10]

I will go here. I would say uv-run-main.py, sorry. I need to pause this. I would need to do uv-run-
main.py or it could be python-main.py. So it would be able to run the fast MCP server over local
host, local service port 8000 over the transport protocol HTTP. So you can listen with transport
protocol HTTP and it also going to give you the URL, same URL. You're going to copy paste here, here
in the URL section of the streamable HTTP connection parameters. Then I will start the agent. So I
have designed the agent in a way that it is a continuous loop where it takes the user input and
based on the user input, it is going to call the agent. The agent will run. You can see here, the
agent is running, the event it is creating and like this runner is running in async parameter. It
will call the agent. It will run the agent service. Agent in its back end will call the MCP tool
sets and like it will be controlling all the client server information from there. So let's say if I
make a request, you may order history for let's say I'm calling someone else. Let's say the cast. So
you can see here, it will receive this. Here's the order history for the cast, gives me all the
order history, summary, output, everything here, here. And here you can also see it has also made
post request to MCP. So this is how you can see. Made a post request to MCP, might have identified
the tools available, made another post request to the MCP, stating what particular tool to use. So
that is how you can see like it is successfully making tool calls here.

### [1:35:10]

And when you want to run the same service on to hugging face, one thing you would need to simply
change is go to your main.py, edit the file. Instead of running it on the SSC protocol, you will
simply change it to HTTP. Commit the changes. We'll start running. It'll just rebuild in a minute.
And here in the agent service, we'll just change the URL. And also in case if you don't have any URL
connected properly, that is also one of the cases. So here, first thing, if you do not have any URL,
it is going to turn an error. In case you have a URL, and if I stop this locally serving URL and I'm
still pointing to the local server, if I run the agent, and if I say something like this, hi, it is
specifically going to say failed on, failed to get tools from tool set, MCP tool set, failed to
create MCP session. It'll give you the error. So if you get this sort of error, understand that
either your local server is not running or either your server hosted onto the web is not running. I
will just change the URL back. You run agent.py. So give me user profile for Chirac. And we'll see
here container. You can see here it is only get SSC as its point. I will go, I will run here. You'll
see post MCP request, post MCP request, multiple requests made here.

### [1:37:13]

And you can see it has generated the response. So this is how the three ways we saw someone has
already created an MCP server. You go to their GitHub, you go to the service, you get the command
like this directly. You can copy paste in your cloud desktop. Another way is you create your own
server. So you created a server like this, fake data API server for the demo use case here. And to
use it with cloud desktop, we saw two methods, particularly one is where you run the locally
directly itself. So if you're running it locally, we can directly use a function, for example, like
fast API install, cloud desktop, main.py with Faker. It will automatically add the particular MCP
server to the cloud desktop setting default. But if you're running it over some web service and it
is running with SSC transport protocol, you would need to add it like this, add npxmcpremote,
provide the URL and whatever transport it is running on. So for cloud desktop, use only the SSC,
only one transport process. Then the next we saw was the Google ADK one, where what we did was we
had the server, we created an agent, and we can simply connect to the agent. Now let's see if you're
running it with lang chain or lang graph. So this particular syntax will be different. Lang chain
will be calling it like MCP connector, will have a different HTTP connection setting. But the idea
would be the same that you would need to provide a URL. So it could be a local URL or it could be
one running into the web server. You just copy paste the URL and you can run it by the agent as
required. You just connect your MCP tool, the MCP tool set, which are the main agent that you
created, be it any framework or any server that your MCP server is running. Your agent would be able
to connect to the server based on the URL access you provide it to. And all the instructions are
also mentioned

### [1:39:13]

in the readme file. You can read it more specifically for all the commands that we have, python
agent.py or uveagent.runpy. So you can read it from the readme, that won't be an issue. But if you
still have the issue, you can post your doubts to me, that would be fine. Right. So yeah, that was
it majorly from the session. So the key takers from the session would be, MCP is a protocol that
standardizes how the LLMs discover and invoke the tools, solving us a lot of problems, specifically
the integration, LXT integration problem. We also saw how MCP differs than the tool calling, then.
we saw the implementation of a MCP server with Fast MCP, and then we saw a few different demos of
the same server running locally with the STDI protocol and same server running remotely with SSC and
HTTP protocol and we also saw connecting it to some UI-based MCP client and also some client that
can be directly integrated with an AI library like Google ADK or any other. You can use it similarly
across any other AI frameworks like Lang graph links and everything. MCP is particularly client
agnostic, CloudX of Google ADK, it can run anything once it has access to client, it can run any MCP
server, any MCP compliant host can consume the same server without any changes to a server code.
That was it from the session. I will open the mic control access for everyone if they have any
doubts. Just give me a minute. Yeah. So everyone will be able to use the mics now.

### [1:41:16]

If there are any doubts, please ask them. Yeah, Dhananjay. Hi, Sherak. First of all, I want to thank
you for the session. It was really insightful and there was a lot to cover. I mean, in this session,
there was a lot of information that was there. I just want to thank you for that. The thing with
this is how do we, I mean, I understand the whole part of it, like how we are integrating MCP tool
and why it is used in the industry. My question is, how do we actually use it in the production
environment? Let's say we have how the security plays into picture, and since we are giving the
power for the MCP to access tools, I mean, the security part comes into a picture, right? I just
wanted to understand what are the use cases and how does it actually works? Just an overview. So
ideal case, MCP is going to run inside any server, ideal case because there will be multiple agents
that will be running over web. Let's say you have server in AWS, you have multiple agents, one agent
could be running in GCP something. Now, there is an authentication or authorization feature also
with MCP. So let's say you created an MCP server, you also create some authentication method like
let's say GWT verifier, or you can use any remote authentication methods. So anytime your particular
client is sending the request, you only allow certain clients to make request to the server.

### [1:43:18]

So that is one way you can protect your MCP server from unrecognized requests. Okay. That makes
sense. So when it comes to traceability of such inputs, so let's say what clients are using my MCP
tools, how the observability part plays into picture, that also I wanted to understand. Understood.
So for that, it would be something very similar to how we use the APIs, right? You would need to
maybe have some database or what? No, no. Sorry. Please go ahead. Yeah. So it would be something
very similar to APIs, how you have the MCP server that a client can consume 1,000 times over a
month. So how the same way we used to have with APIs that we add some credits for a particular,
let's say you have an API key or something. So when the MCP client gets that API key, like the MCP
host would have the login access of the host, would have the certain API key or the subscription key
associated with it, it will send to the client. Whenever MCP client sends that request to the MCP
server, you just stick in with the database or service that is the user having enough credits to run
the server or not, and based on it, you can send the response. So like that way, the traditional API
way, you need to control it. Okay. Makes sense. Sorry, one more question. So how do you see it
forward going? Because now as we see, the LLM has the power to make tool changes and take some
action onto it. Going forward, is it the way that, I mean, one application which I understand is
usually the chatbot and maybe you might have seen other applications where we are just taking some
input from the users and then

### [1:45:20]

invoking the LandGraph API or something like that. But going forward, do you see that? I mean, I
just wanted to know what are all the possibilities while accessing or consuming such LLM
applications from the front-end perspective? So is it one which I can see as one is the chat
template or the other is, maybe a form, user form, which we take some user interaction and then
invoke some flow. So what do you see in future, like how? Yeah, sorry. So apart from the chatbot
parts you mentioned, so apart from the chatbot parts, the major applications of LLM or this kind of
service, I'm saying is under the automation side of the system. So I have seen a few of the projects
where people are automating routine work, where people are using libraries like Selenium Playwright
to automate certain applications. Like, do you remember certain things like we used to have like UPI
path or something like the robotic RPA processes? So same thing people have now started doing with
LLM plus MCP. So they create MCP servers for Playwright or Selenium. The user requests that go to
this website, log in with these credentials, download multiple 510 files. So LLM with the MCP
Playwright or Selenium access opens up the website, does every process and returns back the user. So
that kind of application automation processes is also something that is going, that is gaining
traction into the industry right now. OK, that helps. Thanks, thanks a lot.

### [1:47:23]

Any more queries, anyone? In this case, I'll stop the recording.

# Designing Stateful AI Agents using LangGraph — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Designing Stateful AI Agents using LangGraph](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/76825043-designing-stateful-ai-agents-using-langgraph)
> · Video lesson, 86 min (`1:26:06`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:06]

Hi, everyone, welcome to the session, designing stateful AI agent architectures using LandGraph. So
in this session, we'll learn about what is statefulness in LandGraph, what are the core components
of LandGraph workflow, and how we would build different agent architectures. We will be seeing a
number of 10 to 11 different architectures that we can build with LandGraph, that are the core agent
architectures that we use in production systems. So first of all, trying to understand what is the
statefulness in LandGraph. So statefulness like any others, like when we say statefulness in context
of any software engineering, like with respect to software or a library or a framework, it is the
same thing here with respect to LandGraph as well, meaning in a stateful system, we want our
information to be persisted and shared across all the steps of a particular workflow or a particular
agent architecture. So like as the LandGraph name suggests, it is kind of a graphical architecture.
And in that graphical architecture, there will be many number of nodes, and each of the nodes can
read from the other node or write to a particular central state object where all the information is
persisted. Without statefulness, each step in a pipeline would be isolated and we would be required
to manually pass inputs, outputs, whenever there is a chain of workflow required or a particular
multiple agents, like communication between multiple agents is concerned. So here, what we do is we
maintain a particular central state object, and using that, we give access to every node to read and
write to that particular central state object. That is what allows the LandGraph to be a stateful
library.

### [2:07]

And if we compare it to other different libraries, like for example, Lang chain, or other libraries
where the flow moves into a particular direction, in that we need to kind of have a particular
section where we store the memory into a particular database, and we need to write custom functions
to maintain that the variables value are passed between multiple sequential flow or parallel flow,
whatever is executing in a particular workflow section. Then for the core components in the
LandGraph architecture, like as I mentioned, state, which acts as a shared data store where each of
the node can access, read and write to it. Nodes would be the one that would do all the work in the
particular graphical structure. Edges would be the one that would connect all the nodes, like there
could be cases that one node can give work access to multiple nodes. Then conditional edges are also
possible, meaning whenever a particular certain condition is hit, then and then only that particular
route happens, like this is one of the most famously used routing-based architecture. Then the state
graph, meaning the state was a data store, but the state graph would maintain all the storage store
to which particular database. And then there is also an end function, which asserts that when to end
the execution of any particular workflow. And the last main component would be check pointer, with
which we can save any particular state at any particular point of time. Work similar to how the
TensorFlow or PyTorch check pointers used to work for like kind of ML deep learning model trainings,
because we want to save all the instances of a node

### [4:09]

so we can pause the execution workflow, restart it. So kind of a pause and restart human-in-the-loop
functionality is also possible. So what we'll do next is we'll directly go to the main code
notebook, we'll see all of these things in action, like how all of these core components of the
LandGraph architecture combines with each other, how the overall LandGraph workflows are created and
what are these different 10 to 11 agentic patterns that I was talking about, all right. So you all
would be able to see my Google Collab screen. If someone just confirm into the chat, that would be
great. Thanks, Smokul. So let me just connect to the kernel, right. So first of all, as you all
know, to like enter the Google Collab, what we require is like this LandGraph, LandChain, OpenA,
this libraries do not come pre-installed. So what we'll need to do is first of all, install the
specific dependencies to run the overall code. So in case you are going to run this notebook outside
of Google Collab, you would need to install this particular libraries into your own custom
environment, could be a kind of a Python environment, Conda environment or a UV environment,
anything it could be. So I will just simply run this. It installs LandGraph, LandChain, LandChain
OpenA and OpenA. So these are kind of all the interdependent libraries that we need to do. LandGraph
will serve as the main library with which we'll be able to create all the graphical agentic
workflows. And with OpenA, we would be using the OpenA API kind of calling the OpenA models,
everything could be possible by the OpenA library.

### [6:11]

And then the next part we need to do is, we need to add our OpenA API key into the environment so
that whenever we make the API call using our API key, it gets authenticated and we would be able to
access and run the OpenA's models. So here, my API key is already stored into the secrets here onto
the Google Collabs, I would say secrets manager. And here, like this is the particular custom code
already given as a useful utility by the Google Collab. Like you just need to import google.collab
from it import user data. And when you do user data.get, it will access these particular secrets
value and it would assign that particular value to the environment variable, OpenA underscore API
underscore key, so that any call via the OpenA client, it would be using this particular API key and
whatever amount of credits you have added to your OpenA account, from that the particular credits
would be used as in how many number of tokens you are consuming based on input and output. Now,
talking more about the statefulness part with respect to LandGraph as I was discussing, statefulness
is the major part of the LandGraph score system in any sort of a stateful system. The main idea is
to persist information and share it across all the steps of a particular workflow. Now, in any sort
of agent architecture, what usually happens is earlier, we used to work with Lang chain. Now, with
respect to Lang chain, what we used to have is a long chains or long processes where we call an LLM,
get some output, pass it as an input to the next output. Now, all of these things would be separated
out in different fragments and we need to have some sort

### [8:11]

of a logic to validate input output at each and every step and we can't create a particular perfect
flow. Even though the flow can still be created with Lang chain, but LandGraph was also created from
the creators of Lang chain itself to provide us more power of generating the workflows, abstract
certain workflows that were harder to create with Lang chain. So all of these things could make it
happen and that's how LandGraph came into the picture. So without statefulness, what would happen is
that each step in the pipeline would be isolated and we would need to manually pass input and
output, as I mentioned. So to maintain this particular input output structures across all the nodes
in a particular workflow, what we do is we use statefulness provided by the LandGraph. So it
provides a shared memory like all the nodes has read and write capability to the same state
dictionary, automatic persistence, meaning Lang chain also provides another component check pointer
using which we can store the particular shared memory into like a local database or for example,
something like cloud, MySQL, Postgres, then with statefulness, there is another capability which we
can unlock is human in the loop support, meaning there could be some agentic architectures where you
need some input from the human to continue working on the particular request given by a particular
user. Like sometimes it would happen that, for example, for a planner and executor architecture, as
we saw into the last session, what usually happens is the planner would generate a plan and they can
ask back the user if they want to continue working on to executing the plan that the AI has created
or they want to edit it. So this kind of human in the loop supports can be done when we have a.
shared memory state kind of a system

### [10:14]

with which we can access the previous states, edit the previous details, and then continue working
on to the whatever task the agent was performing. Then time travel and replay, meaning whenever all
the nodes has generated the outputs, we can do a time trial, time trial in the sense that all the
nodes has the inputs, outputs check-pointed at a particular point of time. These are useful when we
talk in terms of LLM Ops, where we want to check how the overall agentic system is performing.
Whenever the particular agent is failing, is it due to a single node, multiple nodes, or a combined
failure of the overall agentic architecture? With this kind of a graphical workflow architecture,
where each node stores its memory, it can be very helpful to understand where something is failing,
where something is not working. Multi-turn conversations gets enabled, meaning we can save previous
conversation history, tool results, intermediate reasoning across many turns without we need to
managing it manually, meaning once we just connected the graph to a database, the graph has their
own abstracted versions of, let's say you connect it to Postgres, it already has a Postgres check-
pointer with which it can access any Postgres table with which you have connected. It will query the
Postgres, it will get results from it, returns as a memory. For example, you can write something
like, read the previous five turns of the conversation history to continue responding to the user.
All of these things would be enabled due to statefulness, meaning persisting certain shared memory
state into the overall AI agentic architecture.

### [12:14]

So how state works in LandGraph? Now, talking from a coding perspective, we either use a typed tick
or a particular pedantic model. We declare the fields that would be required for the overall AI
agent, meaning we define that the response would be a string, there would be an intermediate
variable, let's call it something like tools, which will return a list of particular elements or
some other results. So these all things will be declared upfront. So whenever during the process,
let's say some AI tries to query for a certain unknown variable or an unknown memory state, which
will be going to throw an error. So all of these things would be declared in the like whenever
you're defining the overall state. So like here you can see, first of all, the overall state is
defined, and then what we do is we define nodes. So each node would act as a Python function. It
receives the current state of whatever execution has been done, and whatever result it will
generate, you can either just return the result if that is the end of your agent or you can just
pass in whatever updates has happened to a particular state. So for example, state has here now
three keys, messages, results, step. Now let's say node A receives some input, you update this
particular step variable. So what you need to do is you need to pass the state variable as a return
value, and node B would receive this particular state, and let's say the node B now generates the
final result. So node B can only return the result, or node B can return the state as well, and from
the state at the very end, you would need to extract out the result component from the overall type
of the current Python function. Now controlling how state updates are much right.

### [14:15]

So by default, any node's return value will override the particular state field. So for example,
kind of let's say, whenever like let's say you have a list of item, for example, messages by default
in a Langer of architecture is a list. So any new items coming in are appended, they're not
replaced. And in case you want to replace the older value, then you need to write your custom
functions. So this reducer functions is nothing but just a way that how you replace the previous
value. If you replace the previous value or not, all these things will depend on how we define the
new particular node. So for example, this is one example of how to define a particular LandGraph
state. So from typing, we import type dict, and from LandGraph.graph, we import this particular add
messages, meaning this would be an only append only. And this final answer, when we define it as
string, whenever in a particular node, we say that state final answer equal to this particular
something value, in that case, that particular value will be overwritten, that will not get
appended. So this is how like classes, sorry, a particular state is defined, you go via the class
kind of method, class state passing this particular type dict that was imported from typing, and
this particular structure would be created. Now, whenever you want to do add some sort of a
checkpointing or persistence, so checkpoints can be created like this, memory saver, SQLite saver,
Postgres saver. So using all of this, you can create different sorts of database. Usually the memory
saver will store the internal, whatever state's persisted into your local memory, SQLite will save
it in the local SQLite database, Postgres would save that into a particular Postgres table

### [16:16]

which you're assigned to. So it will help you with resuming any particular, like from a particular
checkpoint, if the node is failed, you can continue from that particular checkpoint. If like you
have added a human in the loop kind of a functionality, so pause the particular workflow, ask the
human, get the human's approval, and then continue if the human says yes. Multi-session memory,
meaning persisting conversation state across multiple session to have a proper context of what the
agent was conversing with the particular user so that the agent can answer with respect to the
previous context that the conversation has happened, right? Now, the second part where we were
talking about the core components of a LandGraph workflow. So like the first part we already
discussed, the state which we defined. So like you can define any number of variables you like,
could be 10, 15, 20, but usually you only need to define all of these variables depending on the
number of nodes, meaning for each node, there could be a input-output separate variable, or you
might have only single variable that is being updated across all the different nodes, that kind of a
structure is also possible. But usually the state would act as a central data structure through
which all the input-outputs of the graphical workflow are passed through. Each node can read or
write to it, and at the very end of the agentic workflow, this particular state would be there from
whatever final response, like let's say for example, here we have an output variable. So the idea
would be that whatever final node would be, let's say you have something like a result node or
something, whatever final response is generated, we would append it to this particular output
variable.

### [18:16]

And once the LandGraph workflow end, we should be extracting our output from this particular output
variable stored in this particular class, MyState. Then nodes, nodes as I mentioned, are essentially
the Python functions which perform certain particular work and they receive the current state,
whichever is being generated by previous node or the first user input it can also access and returns
the values as an updated dictionary or an updated state. So like any node defined as like a Python
function, it would do something and return a particular dictionary. So this is how a node would be
defined. Then edges, so edges would define how the overall graphical flow acts, meaning how the
control flows between nodes. So LandGraph now has three types of edges. First is like a normal edge,
meaning connects two nodes and conditional edge, meaning let's say you have three nodes, A, B and C.
Now, A can either assign the work to either of the B or C. So in that case, you would use something
like a conditional edge that upon a particular condition would route the particular control to the
particular, let's say node C. Then the most and foremost, that is the entry point, meaning whenever
we enter the graph, which particular node would act as the entry point. So which node runs first
will be declared via the entry point edge in the state graph. So state graph would be the container
that would hold all the nodes edges together and will also import the type to take state that we
have defined. Here what we'll need to do is from Lang graph, we would import this particular state
graph function. Then we would define a particular graph variable,

### [20:17]

graph equal to state graph which is imported from Lang graph, and here we will pass the state, my
state which we have defined with all the variables here defined. Here this graph would now have
access to all these particular variables, input messages, output that we have defined. Next is we
will define all the nodes and edges that we want to do. First, what we do is we define all the
nodes. Here we are, for example, defining step 1, step 2, two nodes, node 1 and node 2, and then
what we do is we define the entry point. Step 1 is whenever a user inputs something, the step 1 will
act as the first node to be executed, and whatever input it is getting, it will just take in the
same as it is, and it would start working on that particular user input. Now you define the edges,
meaning how the particular workflow will go. What I will here do is graph.edged and step 1 to step
2, meaning now we are declaring that whatever input step 1 receives and output it generates, the
overall state should also be shared with step 2 in a sequential flow. Here the overall workflow will
work as first user input something, that input goes to step 1. From step 1, it is always guaranteed
that it will always move to step 2. After step 2, we are defining the end, meaning the particular
workflow will end at this particular point. Then what we can define is we need to compile this
overall graph. You can define it as app equal to graph.compile. Then whenever you want to invoke
this particular graph, you just need to do app.invoke and you need to pass the input here. Now here
there would be one thing is, here you can also make certain variables optional, meaning whenever you
don't get an input for that particular variable, the graph will still run.

### [22:17]

So here, for example, if you don't pass in the input, the particular graph will throw an error that
input isn't required input, otherwise without the input variable, the graph cannot be executed. So
whatever input variable we have defined, we need to use it. So we would use app.invoke input inside
a dictionary and whatever input from the user is coming, you can simply pass it here. And whatever
the final output would be generated will be stored here into the result. Now the end, as I already
mentioned, it kind of points to the end of the overall workflow. The execution stops and the final
state is returned. For example, in this particular flow, the final result would be returned to this
particular result variable. Then talking about the conditional edge. So conditional edges, so
instead of doing add underscore edge, we do add underscore conditional underscore edges like this.
We define the name of the particular function, like what we want to call this particular node. Then
here we can pass the function, so this router function would be passed. And here we can define that,
let's say if done is being returned, meaning let's say this is kind of a score evaluator, it checks
that in the current state if the score value is greater than 0.8, meaning we would just complete the
workflow. So done, end, meaning the workflow would end. In case it particularly returns retry, so
retry it will generate, meaning generate will call another node. So this is how conditional edge
would work. So this particular workflow with regards to this workflow, until the AI agent workflow
does not get a score of greater than 0.8, it will always going to return retry, which will call this
particular generate function in loop continuously till we get this particular return done value.

### [24:18]

And this conditional edge triggers the end execution, like the forceful stop execution of the
workflow. So this is how you can define conditional edges used to implement routing loops and
dynamic branching across the workflows. Then check pointers, for example, so if you want to just
store the memory into your local, what you can do is from lang-graph.checkpoint.memory, you can
import the memory saver, and here what we can simply do is graph.compile, and here you need to pass
in what type of check pointer you're using. If you're using Postgres or something, you need to
define Postgres saver, and then you would need to pass in certain username password link that
connects to the particular Postgres table or something. So using that links, this particular
database kind of check pointer can also be enabled. Then type of an input can also be defined for
using kind of a human in the loop architecture. So apart from check pointer, you'd need to pass
interrupt, or there is another way that when we are defining the graph itself, we can use two
different functions, one is interrupt and one is resume command, so we will see that when we go
ahead into the notebook. But for now, this kind of graph.compile interrupt before you can define to
interrupt a particular flow that is running. Now to get a visual overview of how any particular
LandGraph flow would work, so let's say it gets started, user sends in some input, it gets received
by node A, node A processes something, now there is an edge between node A and node B, the state
gets passed from node A to node B, node B works on something, if the condition is true, then the
flow goes from node B to node C, node C receives the same state that node A and node B can access,

### [26:20]

so node C would work on it and it would end the execution, while with respect to node B, if the
condition does not happen, like if the condition is equal to false, then it will go back to node A,
ask it to give it a retry to the user function, so this will continue loop until node B receives a
true condition, and then and then only node C will get triggered to end the particular AI workflow.
Now what we'll do is, now that we understand the components and the statefulness, what we're going
to do is, we're going to see different types of design patterns that we can create using LandGraph
for multiple types of agents, so first of all, the most simplest of one path first pattern that is a
controlled sequential flow, meaning we all know what would be the exact workflow the particular
system is going to perform, and the sequence will also be defined, what variables would be there,
everything would be defined. Every invocation follows the same path here, for example, step one,
two, and three, and there would be end, there will be no branching, looping, no particular
structure, like we always know that this would go as an input, the AI generates some, let's say,
summary, and passes it back as a result. So, for example, we already saw that during the last
session as well when we discussed on to the market research co-pilot, where we created a planner,
executor kind of architecture where planner receives the input, generates output, passes it to the
executor, and from that we would get the final result, and it would be shared back with the user.
Now, how to create this particular workflow, right? So, what we'll need to do is, from Typing, we
would import Typedec as we already saw,

### [28:20]

then we would define all the important Langra functions. So, from chain OpenAI, we'd need to import
chat OpenAI, from core messages we'd need to import human message, system message, just to define
that for the model, what exactly is a system message, what exactly is a human message. And then,
what we can do is, from the Langra, we would import state graph that will connect all the nodes,
variables, the state, everything together, it kind of binds everything together. And this add
messages will also have where we want to append anywhere if we're going to append. But, yeah, these
are all the important imports that we would do. And then, first of all, thing we would define is a
LLM equal to chat OpenAI model, we can select any. So, let's say for here, we'll be choosing a GPT-4
mini, temperature 0.7. These things, whenever you'll receive the notebook, you can play around the
temperature models, the state nodes and everything. So, for example, first of all, we are going to
define a normal class, sequential state, topic, outline, draft, final. So, what we are going to do
is, we are going to have a plan node that receives any input. It first generates an outline. So, we
are passing in a prompt, create a brief three-point outline for an article, whichever, for a
particular topic the human has given an instruction upon. Then, we are going to have a write node
that generates a draft, then a review node which generates the final response. So, this is the
particular three input functions that we are going to have. And then, what we can have is simple.
So, for example, here you would notice that. topic we're here considering as an input state
variable. So for example, I will show you here. So when you're building the graph, note that we're
setting the entry point at plan node.

### [30:20]

So whenever plan node would be getting executed, here it is getting the state topic which acts as an
input for the plan node. Then whenever you will see, we might not be using state topic because at
the right node, we wanted to use what plan the plan node has already generated. So the plan node is
generating outline state. So here in the right particular node, we are only accessing the state
outline. So this is how the variables are getting passed in the state among different nodes. Once
you have defined all the nodes, like you have added nodes into the graph, you need to define the
edges. So we set entry point at plan, add an edge between plan right, between right review, and
review and end. Then what we do is graph.compile. Then here, this is a function inbuilt in Lang
graph that allows us to save this overall graph as a mermaid PNG. Whenever I'm going to run this,
we'll see what value it stores. Then what we simply need to do is sequential app.invoke. We will
pass the topic. So let's say we are just passing the benefits of daily exercise and outline like
this is the way you can access the final value. So when you get this particular result, so from this
result variable, you can access any of the variables that were defined into the state in the output
by just simply giving a square brackets. You can just simply define outline final. So it will return
that particular variables value here. So what I will do is I will just run it. Until the time it
runs, it must have generated the image here.

### [32:24]

It generated the image right. So if you double-click on it, it will show you the sequential flow
that we have got here. So it goes from start, plan, write, review, and end. So this is the
sequential flow we just created. Here, it's just simply showing what outline it created, and what
was the final article the particular review node has generated. So this is the final response this
particular sequential flow has generated. Now, coming to the second flow, that is a supervisor or
router flow. Meaning, we will try to understand as simple as possible from the image itself. Let's
say there exists a supervisor node that has an LLM that identifies based on user input, where the
next flow of the system should flow. If it is a coding question, pass it to code agent. If it is a
mathematical question, pass it to math agent. If it is general, then general agent. Whatever
response the particular agent, like here instead of an agent, there could be a separate workflow
itself here working. Let's say this general agent is calling some web tool or anything, that kind of
things can be possible. Whatever result is being generated by the agent, it would end and will be
returned to the user. Let me just expand the section. Same things here we are doing. Having an LLM,
having the state, where we would be having query, category, and response. Query, meaning what input
we are having. Category, meaning what category we are allotting it. Is it a coding agent? Is it a
math agent? Or is it general agent? Response, meaning whatever final response from the overall agent
system we're getting. In the supervisor, you would notice that here now, we would have a prompt that
says, classify the user query into exactly one category, code, math, or general, respond with only
the category word. So this is how you can experiment with the prompt, ask the LLM to generate a
particular specific

### [34:30]

node's value that we can use to execute or we can control the overall workflow. And then we would
define each of the nodes with their own particular prompt. For example, for a coding agent, you can
define, you are an expert engineer, provide clear, concise code answers. And with respect to
different, different sorts of agents, you can define how you want to call the LLM in case you want
to add a tool, if you want to add an action, everything, you can add up here. And then here, we are
going to define the route function, meaning we will first extract the state, the variable category
from the state. And if the value is code, we'll pass it to code agent. If it is math, we will pass
it to math agent. If it is not in the both category, if let's say model hallucinates and generates
some different category also, as a fallback, we can pass the particular agent's workflow into
general agent also. So we'll define all the nodes, supervisor, and all the three agents. We'll set
entry point at supervisor. Then we will have the conditional edge added here. So for example, we
will have this route function here. It will call the route function. And based on the value returned
from the route function, what we'll do here is we will pass the, like we will control what the next
node should be called in our particular workflow. And then we can just create edges that after each
of these agentic nodes, we're going to end the workflow. So once code agent is executed, we won't be
routing back to the math agent or general agent, we will just end the overall workflow. Then you can
compile the graph. And I already added three sample questions, which I will just run it.

### [36:30]

So you can see as the architecture shows from supervisor, it can go to any of the three particular
nodes and all the three nodes end at the end node. And that means the execution of the overall
workflow is stopped. So now here are all the three examples I've added. Like we ask a code question.
So it's routing to code specialist. We ask a mathematical question routes to math specialist. We ask
a general question, it routes to a general specialist value. Then talking about the parallel pattern
workflow. Here, what we do is instead of routing to a single node and working on a particular
sequential flow or something, we can have some sort of a coding structure where we call all the
three functions together and aggregate the final results generated from all of three. So here, now
this particular thing, it's not more towards the Lang graph side, it would be more towards how you
can write efficient Python code, okay. So here, you need to define all the nodes, the aggregator
node as well. So what the aggregator node does it, it takes all the outputs of the pros, cons and
risks nodes or the agents that you have defined. And then using the Python's inbuilt
concurrent.futures library, we're going to just have a thread pool where we submit all the workflows
in parallel and wait for them to return the result and whatever return we receive, we just simply
return all the outputs of the three nodes and then we just combine all of that together like the
parallel analysis function we're defining using this fan out function and we pass all the values to
the aggregate function and after once we aggregate all the values together,

### [38:32]

we'll just end the workflow. So I will just run it. So here you will notice here inside the parallel
analysis, you won't be seeing all of these nodes, pros, cons, risk, because all of these things are
now abstracted inside the parallel analysis function where it is executing all the three at a single
point of time. So you will notice when I'm printing result pros, so it's printing all of these
things and then executive summary, which is the final response. This is what it has generated
combining all the pros, cons and risk together. Right, now talking about the fourth pattern, which
is a reflect or a critic pattern, right? So for example, now this particular like reflect and critic
pattern as it suggests, we are now trying to identify whether the particular result by a particular
agent or an LLM call has resulted into a correct response. If not a correct response, then we'll
sort of reject the response and return that back or loop the flow back so that we can ask the agent
or LLM to regenerate the response in case it generates a better response or a better. response for
the user. Let's say you have some evaluation matrix defined there which checks how is the factual
correctness of the response. It says that the factual correctness is less than 50 percent, so we
route back to the previous agent, ask it to regenerate the response in a particular format that,
let's say we are hoping it might generate a better response, and if it does generate the better
response from the evaluate node, the result will get passed, and we can end the overall workflow.

### [40:35]

The same thing here we would be able to do is, what we can here simply do is, we can define here now
a particular state. So here what we're defining is a generator node, evaluator node, and we're
having a router that says should continue. So here we are having conditional edge as well, using
which we'll create a looping structure, means if the particular evaluator node says that if it is
accepted or rejected, if rejected or if it is not accepted, then we return retry value, meaning from
the evaluate node, we go back to the generate node. Now here you would see that I have defined
something like maxIterations equal to 3, and in one of the cases inside the should continue, I'm
also using maxIterations function because what our overall goal will be that, we should not let the
agent run infinitely. There would be cases there where the overall system would go into a state
there, where it won't be able to answer the user's question, and in case it goes into infinite
iteration, that would be just loss of input-output tokens, and you might exhaust all your credit. So
it is necessary to have some sort of retry mechanism where we say that only retry for three times,
and even after three times, if the particular generator node is not able to generate a good
response, then just stop the flow and return whatever the particular generator node is generated. Or
you can have some fallback message stating that, sorry, we could not generate the response for your
query, please retry later, something like that, fallback options you can have. So here what we are
going to define is write a three-senders product description for a smart water bottle that tracks
hydration.

### [42:37]

So here it says, hydration two, it got accepted. So final daft, whatever response was there, it has
generated. Now in case if it was not able to generate, now here it is a normal evaluated node. So in
most of the cases, it will be anyway going to kind of, just pass in or accept the response. But in
case you are working on some domain specific stuff, that let's say you are generating some
recommendations based on a product list or something, now only your custom algorithm or something
can evaluate particular response by the LLM. So in those cases, this evaluation retry mechanisms do
work better. But in case we are just simply going to use LLM as a generator and evaluator, there are
a lot of chances that even if the answer is wrong, the evaluator node might feel that the LLM has
generated a correct response. So in cases like this, evaluator retry mechanism is always better to
make use of your domain knowledge, write certain if-else sort of conditions or use something like
traditional NLP matrices that check for semantic similarity between the input query output or we
have certain particular LLM matrices like precision, recall, factual correctness, ground truth, if
all of these things are available. You can also define a different particular evaluator function
that checks all of these things and would be able to give you a better retry evaluator mechanism for
you. The next pattern would be human in the loop. So now, as I was mentioning, we can use an
interrupt before or after function directly from the LLM or there is a different interrupt and
resume pattern also available. So just for example, whenever the LLM generates something,

### [44:41]

so let's say we have an email generator, it generates an email. Now, it asks for the human to either
edit the particular mail or approve something. So if the human approves, it will go and send the
mail and it will end the flow. If the human edits it, then it will just edit out the text and can
directly send the particular mail. So this is how you can define something like human in the loop
flow. So this now will have some different inputs. So now, from langraft.types, you would be
importing two things. One is command and one is interrupt. And here, we would also have one
different variable, which we will call as human decision. Here, we are going to use three values,
approved, rejected, edited, like that. So here, we can have a node, draft email, which generates an
email draft. Then we'll have a human review node, which takes in this draft email. And then we're
going to use this interrupt, which we imported. And here, what we'll do is we'll just call this
interrupt. We'll pass in this draft instructions, reply with decision, approve, reject, or edit.
These are the instructions we can just pass in. And then whatever particular decision the human will
give back, so this human input dot get decision. If a human does not give any particular decision,
we will by default select as a reject. But in case we get something from the human node, so we can
do something like if decision equal to approve. So send the final email as draft email. If the human
gives edit and passes in some new text, so that new edited text would be sent as the final email. If
rejected, then just do reject and cancel the flow. Do not send the email. Now, we will have just two
simple nodes, send email, which will just print a simulated environment, sending email.

### [46:41]

If canceled, email rejected by human, workflow canceled. So just two normal print statements we
would be having here. And now here, the graph structure would remain the same, just that we would be
adding a check pointer here just to store the previous memory states, which will help the particular
interrupt and the command function to work upon the overall, like checking the previous state and
continuing from that particular node. Now here, when you add a check pointer, could be a local
memory check pointer or a postgres check pointer, you need to add a thread configuration. So this
thread configuration would always be in this particular structure. Configurable and inside the
configurable, you can define any sort of a particular variable, could be a thread ID, session ID,
anything. And you can just simply pass in a particular value for it. So let's say I'm a user one. So
my thread ID that is assigned is a email thread one. Now what you need to do is, we will can simply
invoke the graph, invoke the graph, pass in the request, whatever request I needed to do. And then
whatever thread config I defined, I will insert the dot invoke function. After this dictionary ends,
I will add a comma config equal to thread config is what I need to pass. Now this graph will get
posed at human review node. And here now again, we need to invoke. So this is now how wherever you
are, you have deployed this into production, you have deployed as API or a particular workflow. You
need to control this flow that whenever interrupt is hit, you can store it in some variable that
this particular thread ID was hit by an interrupt. So whenever the next input comes in, you do not
call this particular dot invoke function instead of that, we call this command here. Inside that we
particularly pass in something like resume equal to,

### [48:41]

and whatever the human input value has been given, approve, reject, edit, anything could be given
here. And whatever thread was given, thread config, so that we can access like this particular app
can access the previous states and continue working on it. So whatever final result will be
generated, it will generate the final state. So here I'm going to run this. And here you would see
phase one drafting email, then draft email awaiting human review. So now here the graph was paused
and we kind of passed in decision approve here. So this command function is just resuming the
overall graph. So resuming with approval. So whatever email that was given previously as a draft
email, that would be send here and we can here see simulated sending email, like it's kind of
sending the email. Now the edit functionality, if we want to look at it, so we can just create a
different thread ID, let's say email thread three, we would invoke with a particular new request to
generate a email. And then here, instead of taking a user input, what I'm doing is I'm just have
designed a static email that I want to edit it with. So I'm going to give you this edit text and
inside here you will see something different instead of decision approve, here you will see I have
passed decision approve. Now instead of it, what I will pass is decision edit and I will also pass
another variable that is new text, which will be whatever edits I have done. So here. If I run this,
what you will notice is, first it has drafted some email, then it's now waiting for human approval.
Now here you would see subject, launch of our new product. Now, wait a minute. Here you will see I
made some edit and whatever email it finally sent. So here if I go and see the draft email, the
subject you will notice is launch of our new product. Now in the edit, I did launch of our new
product on Friday. So whenever you will see it sends its simulated function,

### [50:44]

you would see launch of our new product on Friday, meaning whatever edits I as a user sent in, those
edits were accepted and now that particular email is being sent further via the send email node. So
this is how human in the loop can be used to ask the user, ask the particular human for a review to
either accept, reject, or edit the particular values generated by the agent or LLM call and using
which you can further control the flow. Now, the flow control would be not in the control of the
agent. Human can also make a little bit of control changes to the flow. If it rejects, the flow
would be stopped, then the user can again ask for a new particular email structure or something.
Based on it, it will continue working, like the agent will again trigger from the very start, it
will generate a draft email again ask to the user for a review, and if approved, then it will send
the email. Now, a particular pattern where we attach a tool to the particular architecture. So an
agent is now equipped with a tool again a Python function, which the LLM call decide if to use the
particular tool and if it uses the tool, whatever results are being generated by the tools, it can
process, and if the information is good, it can be used to generate a final response. So here in
this case, the architecture would look like the agent is there, it calls the tool if the tool call
is required, so the tool is executed, the results are sent back to the agent. If the agent says no
tool required, just end it. So here what we'll see is now first I will just run this code,

### [52:44]

we're going to see, I guess we missed the last the particular human, right? So what I will do is
I'll just give a second. So here you will see like start, draft email, human review, end, and it
also has two functions, meaning after human review, if something works, we use send email or cancel.
So this is how another flow can also be created. And now if I go back to the tool pattern, so with
respect to the tool pattern here, what we are doing is we are simply defining two functions, we call
them as tool. Here with using this tool decorator provided by lang chain code or tools, when we
define add the rate tool, meaning now these are defined as a tool, and how we can attach this tool
to the LLMS

### [1:00:05]

call this make agent node and here we are passing the information like what this particular agent is
supposed to do. So high-level strategy planning the analyst will do analysis critic will identify
flows improve and suggest improvements. Then next what you need to do is define a for loop for each
of the node you need to define a particular conditional edge and here in this case sometimes
strategy can also call a particular strategy. This is how we need to define so each of the node call
can call each of the node and in case of then we'll just end the particular workflow. That is how we
need to define so this is instead of doing each like for each particular node graph dot add
conditional edges. You can just simply create a loop and for each of the nodes which we have defined
we can just simply create conditional edges for all of them. But now here what I'm going to do is
I'm just going to do go and run it. I'm asking it should a startup with 10 employees adopt
microservices architecture. And the first agent that I want to work up on is I'm just passing
current agent strategist. Oh, it starts from the strategist node at work. So here you will see it
goes start goes to strategist. Now strategist can go to done completed strategist can go back to
strategist strategist can go to analyst strategist can go to critic. So all of this interconnected
or with together. So now here you will see first the strategist work. It called next as analyst
analyst again called strategist it again called analyst and I guess after this particular fourth
call kind of like we hit the four iterations number right? So it kind of just went into the done
mode and it just returned done meaning the execution was stopped now here you can make

### [1:02:07]

changes to the prompt stating that once like here you can add here into the prompt itself where it
can access the value of the number of current iteration here inside the prompt you can state that if
the current iteration is number three simply say state that the next agent is the end done node or
state that no if it has called not called the critic node call critic node once and then in the
final just call the analyst node and just complete the workflow all of these things can be no kind
of handled by a prompt or certain if else conditionals using the state state of iterations, but in
case you want that each of the node does guarantee that it is ran like minimum once so you need to
know kind of create an architecture separately to that. So this kind of things you can obviously
practice like whatever kind of domain problem you're working on maybe in your case, you might you
might be able to run for five times ten times depending on that you can obviously change the
strategy of how you want to create your overall architecture then coming to the eighth pattern that
is multi-agent custom meaning there are multiple agents and then you are just defining a single
workflow that is a custom workflow and that would be always executed as you have defined. So for
example takes in some input validates invalid just calling the error handler stating no can cannot
kind of respond and the workflow if it is valid process it format something for the end user and
just return the value. So it does not call each other or it's that does not it's just acts as a
simple workflow as in defined by the developer programmer and each time an input is received it
would the workflow will execute same as in given in there.

### [1:04:08]

So if I go and just simply run this where you can see I have just printed out I have just added this
print statements here print formatter. So just to identify the overall process has been ran across
all the nodes that I wanted it. So intake validate process of formatter and once the formatter is
done. This is the final output we have generated. So just a map here. You can see intake validate
processes formats and end. So this is how you can just define a fixed workflow that you want and
that fixed workflow will always execute in the same flow as in you have defined it now the pattern
planning pattern, which we saw right. So like the idea is very simple. We would have a planner and
an executor here in case we are kind of adding another synthesizer that know like if there are
multiple execution steps, we can simply synthesize them all together to summarize all the
intermediate step results and let's say here we are also defined a condition that if the current
state if the state of the current step, so it is more than the kind of length of plan. So let's say
in the plan we are what we are doing is we have defined a Jason we are getting a Jason in the plan
and we are just getting out a length of steps. So once all of the steps are completed and the length
of current step is in is more than or equal to the length of steps that were generated in the plan.
We just go to synthesize or we continue running the execute. So this is kind of a single plan
multiple executor nodes if required so loop execute next step all steps then so it will go to
synthesizer and synthesizer will

### [1:06:09]

kind of know synthesize all the steps together all the results of the step together now with respect
to planning pattern planning pattern can make use of previous patterns as well. Like we like what
the planning pattern suggest is that we have a planning node and executor node now how you structure
is the planning and executor node cool also where I like it could be sequential process plan it and
execute is executed across multiple sequential steps or planet ones executed ones could also be
there. It could be like planet ones and if there are multiple steps generated the execution steps
all occur parallelly and then they're aggregated together. So there are numerous ways with which you
can define the internal structure of planning executor pattern, but in general the plan planner
executor pattern simply means that you have a planner and executor two nodes which plans and execute
something into the overall formation. Now here you will see goes to planner executes it keeps
executing all the steps once all the steps are executed goes to synthesizer and ends the overall
workflow. Okay, I guess it might have a bit of more number of steps. So maybe taking time to execute
all the intermediate steps, right? So till then what we'll do is we'll discuss on to the react
pattern till the output is generated. So react pattern simply says that think about something if the
agent wants to act call a tool or something whatever output was generated like observed like meaning
process

### [1:08:10]

the tool result and keep repeating it until we have some enough information to generate the final
answer. So if done meaning final answer can be generated then end the process. So this is how a
react or a reasoning plus acting agent works meaning it combines tool use plus the reflective
reasoning. Now here you will see the react pattern in itself is a combination of two patterns like
that is a LLM with tools plus the reflective method with well it revalidates or rechecks the
response that if the response is what the user wanted if not then like recall the tool or the ask
the LLM to regenerate the result. So we'll try to run it. But before that here you can see like it
generated five step plan and the final report like the synthesizer has combined all the outputs of
five steps and generated kind of a plan to study the machine learning concepts now coming back to
the react pattern, right? So here again, we are doing it something like we are defining a tool now
here. We are pre-defining certain facts like for Python machine learning default. So for something
like let's say like it's kind of a lookup that if a particular we are looking up some information of
Python will just simply use this information. If you're for machine learning will just use this
information for machine learning if default then like we are just stating that this is a simulated
fact lookup result. So this that's it like nothing we're not calling some web tool or something. We
have already some predefined results already, you know, stated here into a lookup Factory and then
we are defining also two other tools count towards summarized topics and we are defining all the
tools together binding those tools with the LLM and then we are generating a prompt like for a react
system. We are stating that for each step, user thought, action, and observation process,

### [1:10:11]

like process the tool result, and we're also asking us always prefix your thinking with thought
before calling tools. Then we define the React state messages, all the messages will keep getting
appended and whatever number of iterations we have done. Then we define the React main agent which
calls the tools, and then we will have a React router, which will if the agent makes tool calls,
execute those tool calls, return say the tool was called, so we need to return tools. If max number
of five iterations are done, just complete the overall workflow so you don't end up in an infinite
loop. Here what we'll do is we'll just simply set an entry point to agent, and inside it will just
have this tools and end, meaning the agent can keep calling on tools for maximum of five times, five
times or if the agent says that, okay, five times or three times is fine, two times call was fine,
just end the tool call and the overall process is done. Now here again, I have written a custom for
loop that will kind of shows all the overall process the model is done upon, and we'll be printing
the final answer as well. So until and until we will keep receiving tool calls, we'll keep printing
the tool calls. Once all the tool calls end, we'll go into this else function and we will get this
final answer, whatever was generated as the overall process. So we'll let me execute it. Right, so
here you can see thought plus action was taken, tool calls, lookup fact, summarize topic was done.
So our input was what is Python and can you summarize machine learning in 30 words, right? Then it
made an observation, Python was created and from the lookup fact it also given observation of
summary of machine learning, like here you will see,

### [1:12:11]

here we are just cutting off the response to 200 letters into the output. So let's say if I just
remove this condition, I will just rewrite it, just remove this part. So we'll be able to see the
full output. So here you would see, okay, I guess it is only generated in 200 words itself. Okay,
fine. So the final answer or thought it has done is, it is like kind of thinking, like after both
the observations are done, it is trying to generate the final response. It says, I have information
about Python as summary of machine learning, I need to present this information clearly. And then
once this final thought is done, all the tool calls are done, it goes back and this final answer is
generated like kind of Python is a programming language created, machine learning is a field of
artificial intelligence. So this is the final answer it generates and response back with this
particular done value, like after all the tool calls are done, just return done. So means the
workflow is ended and we get the final answer, whatever agent has generated as a response. I'll just
delete this, okay. Right, and now we will talk about the last pattern that is a leader plus
specialized member agents, meaning we have a leader and we would have multiple specialized agents.
Each agent will report back to the leader whenever the leader calls those particular specialized
agents. Now this particular specialized agents can run sequentially, can run parallely, depends how
you want to design the architecture upon. And here we also give the access to the leader that
whatever particular agents the leader agent wants to select based on it. So this is like kind of a
team kind of architecture

### [1:14:12]

where there is a team lead can ask a particular specialized agent to run something and report back.
And then whatever response we get, the leader will collect all the response and send them together
to the synthesize node to generate the final report. So this can be, for example, the example here
we are taking is we are having three team members, marketing, engineering, legal, and we want to do
some sort of a research kind of activity. So the leader, we have given the access to the leader to
call this different sorts of members. And based on it, whenever all the kind of data is collected,
we are defining the synthesizer node. We are a senior executive synthesizing team inputs into
comprehensive project report. So let's say, for example, we are creating, working on a project, we
pass in all the information like the particular code agent might have access or the engineering
agent has access to all the engineering documents, code, the legal has all the idea of the legal
aspects of the particular project. All of these things, the leader node will be kind of
communicating with all the specialized agents. And when you define the team router, if the phase is
synthesizing, like this kind of just acting as a conditional edge routing. And whenever we are not
getting any particular phase, we are just going to call that meaning like there is no more calls
from the leader to generate something. That means the overall workflow has been completed. And here,
what we'll do is we have written a specialist function, make member node. So all the members we are
adding is a node and what this make member node does is each of the LLM with tools get a binded via
all the tools we have defined. So all the tools kind of analyze market, estimate development costs,
check compliance, everything kind of those kind of tools we have defined. And each of this will have
certain sort of like,

### [1:16:14]

let's say we have already found kind of information for all the members, like what a marketing
strategist agent does, what is its expertise. So whenever we'll be defining this nodes, we will be
extracting those information. So kind of curating prompt for each of the agents. So a marketing node
only acts as a marketing agent, not like a coding agent or something. And if it calls any of the
tools, those tool executions will be saved, final prompt will be generated and the final response
can also be curated. So all of this process would be completed and a particular member nodes would
be defined. And then we can define this particular add conditional edges, where we will define
conditional edges to marketing, engineering, legal synthesizer. And when completed, just end the
workflow so we can get the final report that we require to generate. So what I'm asking it is,
launch an AI powered SAS tool for automated code review. Okay. So I'm just going to run this, sorry.
Okay. So as kind of, you know,

### [1:18:14]

you can see we are not made all the calls parallel. So they might be executing in sequential and you
can see it's taking time. So when it comes to agentic architectures, it's also kind of important to
identify where you can make parallel calls, where you need to make sequential calls only. And
depending on that, the sequential parallel patterns can kind of exist inside different patterns
itself. So now here you would see, so team contributions here, you can see what the marketing. So
now here, what I'm doing is from all the completed sub tasks, meaning for each of the member, we
have stored their contribution. So what the marketing agent has generated, what the engineering
agent has generated, what the legal agent has generated. And based on all of these generations, the
synthesizer agent is finally generating this particular output. So we might see something
similarities. Let's say here they're saying there's six months for development, the engineering
report might also say the same. So here let's say it says six months of engineering effort. So here
you can see, you know, like the similarities which you will see. And you might also see, let's say
foundation infrastructure, $300K, AI part features, another $300K. So combining all of that together
in the final report, it says $600K split between foundation infrastructure and AI features. So this
is how we got multiple reports across different nodes for the leader. Then the leader kind of sent
it to the synthesizer. This was the final project overview report that was generated. Right. So to
summarize like the different flows in together, I will just zoom in so we can see it better. All
right, so we saw different patterns like 11 patterns here, like if we are talking about the key
traits,

### [1:20:15]

so sequential flow, it has a fixed linear path. It's best for pipelines, ETL workflows, document
processing, where each step should work in a particular format. Router nodes, meaning you require
routing to where you want to identify what should be the best possible next step. So multi-category
queries, customer support, this particular patterns are most used there. Parallelization, like
whenever you require concurrent execution, so when speed, inference speed, all those things are
required, we need to use this kind of a setup. Reflect and critic, meaning wherever you want to have
some setup where you want to identify, let the agent refine its results, still possible. Then
talking about human in the loop architecture, so requiring human inputs to continue performing. So
at this point of time, you need to define, have a particular architecture that is straight for a
human checkpoint. So human in the loop is the kind of pattern we use. Then tool use, meaning call
external tools, could be APIs, could be database execution, could be a code execution node,
something like that. So all of these tools can be called and used upon. Then to multi-agent kind of
a network where we have a decentralized collaboration effort, each agent can call each other to
generate the response. Then you can have a custom setup as well. So you can define a specific strict
workflows which do not change its workflow at any point of time. It will always go into a same
execution flow. Planning, meaning it plans first, executes then something. Here you can, as I
mentioned, already mentioned, the execution steps you can define like sequential parallel, make use
of another different patterns inside the executor planner workflows as well. The react flow where
the agent access, like the reason set itself acts, maybe call tools,

### [1:22:17]

uses something, observe the tool results, and maybe again result, sorry, again reasons with itself
before generating the final response. The team's architecture, meaning, performs a hierarchical
structure more better used for large projects, enterprise workflows. You might be seeing that this
particular library is where so much in use these days that create a team of agents that work
together, creates some particular overall projects by itself. So all of these things fall under this
team's pattern where they perform hierarchical structure. I'll go back to my presentation. Right, so
to kind of just to give a overall conclusion to the overall notebook we saw. So the main key
takeaways that we saw was how Landgraf manages the shared states across the nodes, how nodes do the
work, it just control the flow, and the conditional edges can enable branching structures, looping
structures, and the overall idea we would suggest is pick a simplest pattern first and then keep on
adding complexity as in you understand for your domain how important is the speed for you, where you
need parallel execution, sequential flow. Then we also got an idea about human in the loop, how it
is critical for high risk or sensitive automated actions. Like let's say we recently saw for AWS how
an agent found that this particular piece of code that is running a particular cloud service can be
changed. So the agent directly deleted a particular piece of code that had like kind of a 13 hours
impact onto the AWS servers. So without human in the loop, this kind of risk can happen. And most
production systems if you talk about like the last pattern we saw, the leader pattern,

### [1:24:19]

it would have multiple agents each with different patterns together combining and there might be
leader agent who would be controlling everything together, team kind of a hierarchical structure
like that. So when you keep evolving the agent architectures you will end up having kind of an
architecture that is combining multiple patterns together. So that is the overall idea that we would
try to take from today's session. These are the key takeaways. So yeah, that was it from the overall
notebook and the presentation. So I guess Saurabh, you can now allow the mics to be, in case Saurabh
is not there. Give me a second, I will change the settings. So this notebook would be shared with
the LMS platform for whoever are enrolled into the AI agents program, guided projects in AI agents.
Yeah, so I think the session is open for Q and A. If you have anything, feel free to unmute and ask
your questions. Thank you.

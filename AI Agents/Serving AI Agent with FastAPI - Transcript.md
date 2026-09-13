# Serving AI Agent with FastAPI — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Serving AI Agent with FastAPI](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/61819144-serving-ai-agent-with-fastapi)
> · Video lesson, 60 min (`1:00:14`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:01]

Anyone has any prior experience with FastAPI Flask or something? Not really, sir. I don't have.
Okay. Fine. Then let's start. So this is one presentation which I had for particularly for MLOps.
Not very much related to like what we're going to see today, but just for a general idea. So we're
talking about like serving something. Serving in the sense serving to customers such that other
people, other users can access our model.

### [2:09]

Model or in our case here as of now, let's say some agent or a rag pipeline, something like that.
Okay. So like you prepared agent, agent is working fine. But what would be the next step after that?
So what we call that as like developing a model or in our case, developing an agent rag pipeline is
like one separate thing. But putting that to a production like on a cloud or something or how do you
serve that particular agent? That can be a bit of a like challenge for any kind of a new person. So
generally we have two sets of models serving. One is what we call as batch and one is online. So
batch we call it as a static learning, meaning there is some agent, some rag pipeline present where
a lot of queries would be passed on. But that the result of the queries won't be shared at the same
instant. It would be running at some particular interval, like every six hours, every 12 hours. So
people have to wait to get the response online means users would be sending their query and they
would be getting the response at the same instant. Like some seconds, a first two seconds, five
seconds, whatever the pipeline or agent takes the time to run. So like this was the whole idea of
model serving. Now going to the actual part of fast API. So I have already prepared a code. So what
fast API is? First, let's talk on that. So fast API is a library or a framework in Python. So
technically it's a high performance framework and it is a very suitable thing. Like earlier people
used to use Django then came the flash.

### [4:10]

But fast API has certain features that makes it a bit more better and it is highly scalable
framework. So here, how many of you know about the get, post, put, delete concepts like with respect
to API requests to people? Yes. So anyone would like to explain for people who don't know?
Basically, we have means what I know there are four type of request. There is a get request, which
is just used to get the data from the server. Yes, that's right. There is put request, which is just
to update the data in the database. Third is the post request, which is just to post the request
means like posting the data to the server or maybe a database. And there is a delete request. That's
what I know. So you meant to say post request can only be used to post something to a database or
any storage or you can do something else with the post request? We can do something else also, but I
have just used in terms of database means it is just to post the information to the server. It's
like there is a form field. Once user field that form, then we can send that particular thing with
the post request. Okay. Okay.

### [6:10]

So any sort of API application programming interface supports these four basic terminologies like
get, post, delete. So for our use case, mostly like for we people who are more towards the side of
deploying agents model, we more of work with get, post or put request. Delete might not be that much
useful. Put might also not be that much frequently required, but get and post would be the most used
kind of request services. But technically the idea is like if I say, let's see, they have it here.
So get request is technically like something accessing some data from a particular place like a
server where you have your data stored. You can get your like as the name suggests, get something
from someplace. So like some data stored on server, we put a get request to the server to access the
details. Then you have a post request. Post request technically means you post something to the
server. And if needed, the server would send some particular message or some particular stuff based
on your data you have posted to the server. So we will just see like what I mean by posting
something to the server and all. So this is a general idea. And fast EP as of now is one of the most
fastest growing EP frameworks when we talk about Python. So just let me close this and I'll just get
back to this full code. But before that, let me show you like if anyone is going to perform this
exercise like this particular code would be shared with you.

### [8:15]

I have mentioned all the requirements like TXT, like all those things you would need to run this
particular code. So just make sure you create this in a new environment, whether you're using Python
V and V or a conda environment, something create a new environment and run this. Because if you
already have some libraries installed, there are chances that there would be some clashes. So what I
have done is I already have anaconda with me. I have already created an environment. I'm just going
to activate that particular environment. So what we are going to do today is like this is the first
demo code that we will walk through to learn like what we can do with respect to fast API. So we
have fast API from fast API. We are importing fast API, then some exceptions like when we get some
error, how to throw an exception, then we have Pydantic. So anyone knows what is Pydantic? OK, fine.
So Pydantic is another library which we can use to have a strict validation for our API endpoints.
Let's say there is some endpoint that is getting some. numerical input from a particular user. So to
make sure that a numerical input is always received as a numerical, like an integer or a float
value, but it should never be a string value.

### [10:15]

So that sort of a validation we can apply using Pydantic. So like there are some particular steps we
need to follow. So to start a FastEPA application, we need to write app equal to FastEPA, the one
which we imported from here. So this app would be responsible to run all the stuff which we would be
declaring here. So first thing what we are doing is we are creating a class as an item where we are
passing this base model here. So what we'll be doing is we'll be using this item class to have this
four values, name, description, price, and on offer as particular fields that can accept only
certain type of a data type. Like name would always be a string where I'm passing like a title, like
what is the name of the item? What is the max length? So name would not like if the value crosses
50, then it will turn error that it is a bigger name. Then I will have description. So description I
have put it as an optional. So when you pass an optional, you need to pass a none here. Or let's say
you have a Boolean. So Boolean you can by default make it as false. Then you would have like we have
a price. So price I have put it as flawed. So here I have put greater than zero condition, meaning
if any value less than zero is put then that will also turn error. So that is how we can create
validations that no random input or no wrong input should be received from the user and client side.
And we make sure that if any wrong input is like received we would throw in particular error. Then
what we are doing is we are just creating a simple dictionary for now. We are not going to connect
this to a database. We are just creating a dictionary where we will be storing all our variables

### [12:17]

for this particular app. So what we have now is like now what I'm doing is I will be creating URLs
like so how you can think is like whenever we connect to a website, let's say google.com. So when we
go to google.com, so let's say go to here google.com. So we will land up at this particular page. So
now this is a particular domain connected to a particular IP address or URL something. Now on this I
got this particular screen, right? So this is rendered by html, but in case there was no html here,
then what would happen, Yash? I actually wanted to know what is the role of title in that particular
code means what it does actually. This one, right? Yeah, that one. Yeah, that when I run the
application, we will see at that particular point. Okay. So same way like we had this particular
Google. So what we are going to do is we are just going to start this particular application for
now. So to start to run an fast API service, you have to use this command uvcon, the .py name of
your file, for me it is main colon app and just enter. So it will automatically start at this
particular point. So I will just click this. Yeah. So if you can see, welcome to the fast API demo,
the same message which I have printed here.

### [14:18]

In case I had some html file with me, what I could have done is I could have rendered an html. So
that you can look onto the fast API documentation if you want to render an html here. Otherwise for
us, like if we are creating an API, this is normal, like this is fine up to this point here. Then
what we have done is we have created certain functions. So one function is app.get on this get, what
we are doing is we are fetching data, all the data present here in our database. So our database is
a simple dictionary. So in case someone tries to access this get request for the first time, it
would be empty. So for that, we have created a post request. So using the post request, what we can
do is we can add data to our database. Similarly, we have put like to update any kind of item we
have added to our database. Then we have delete in case we want to delete. And then we have one more
get request where we can pass in particular item ID. So we'll just see what I mean by item ID. So
I'm just hoping this is fine. We will just have a look at all this particular piece of code one by
one, like till here we are fine. And we will see each of this one by one and try to, you know, just
walk through the code. So one of the very interesting points about fast API is it comes with an
inbuilt swagger UI. So to access the swagger UI, what you have to do is you have to type in docs
docs slash docs. So when you do it, all your APIs would come here as an view, like you can use them
from this particular point. So this read root would be the one which was at your default location.

### [16:20]

If I would execute this, this would land me here message. Welcome to fast API demo, right? So this
was your basic, like when you hit this particular URL, this is what you get. Now, in case you want
to access, let's say I'm going to items code. So this was my app.get items. And what I'm kind of
requesting is I would fetch like list all the items from my dictionary. So I'm returning a list that
is containing the values from my dictionary database, right? So if I just go here, try it out. So I
don't have any values to send to the server. Like this is a predefined function, like get request is
like this. I will just execute this. And what I received is an empty list because I don't have right
now anything in my dictionary. So what I can do is, for example, this post request we have. So what
we can do with this post request is we can actually add an item to a database. So I will give it,
try it out. I need to pass in an item ID. So I will put item ID as one. Then we have this multiple
options here, name, description, price, on offer, okay. So what I will do is name, I need to pass a
string. Description also I need to pass a string. So it's kind of any kind of an item. So what I
will do is I will add something like, let's say monitor. I would put a description as ultra HD
screen for now. Price, let's say put it as 10,000 on offer as false. I'll just execute this.

### [18:20]

And if you see it has returned me this particular stuff. Whatever I posted, it returned me the same
and it hasn't throwed any error to me. That means it is added. 201 for me. So what I had done here
is on this post request, I have put particularly status code as 201, meaning if my request to the
server is successful, return me a 201 code. That means it is successful. If it was false, like,
sorry, if it throwed an error, then I would have written 400. So let's say on the same post request,
if I try to, instead of monitor, let's say I put a keyboard, if I will try to execute, it would
throw me this error, 400 item ID already exist. So that is what I have already hard coded here. If
there is an error, throw me the code as 400, item ID already exist. So that is how one can use post
request. Now, if we go back to our get request of items, if I just execute this, you will see, I am
now getting my one database already stored. And now there is one thing like with respect to get
request. So get request, you can actually access via URL. So let's say I have already created this
another get request. So here what I can do is I can access any single one particular ID. If I pass
ID one, so what it does is it gives me the ID one. details from our dictionary. So in case if I put
this here as well, so get request can be accessed from the URL like this way, but post request can't
be accessed like this. So that is the one of the difference between like a get request and post
request.

### [20:22]

So what happens if I try to access any particular different item ID? So here I have already defined
404 error item not found. So destroying the same meaning this also working fine now to update any
particular record. So let's say first what I will do. I will just create an another entry with
keyboard but I says 1500 I will not pass any description on offer. I will make it as true. Yeah, so
this got added just to confirm. I will just execute this so we can see now. There are two items in
our database. So now let's say I want to update any particular item. So what I can do is I can pass
in the item ID. Let's say put in one for the first idea. We had monitor right? So instead of monitor
I want to put a laptop here. So laptop description. Let's say I would put it as GPU supported laptop
price. I will put it as let's say 65,000 on offer. I will make it is true if I execute now if this
is executed perfectly with a status code 200 meaning the item is updated. So what I will try to do
is I will try to fetch the ID one because I just updated it and see if it is a monitor or a laptop.
So as you see we already updated that so it will return us laptop and not the monitor here right and
to delete something we can just like put it in one instead of one.

### [22:25]

I will put it item ID to execute this item deleted successfully will go back to full data access and
you can see that keyword is deleted. So this is how like basic flow of all the four methods we have
with respect to client server request and all post to post something add to a database or to send
certain requests to the server and receive something if something can be processed get to get item
from the server put to update something delete meaning to delete something right. So yes, so can you
move to the code? Yeah, here there is a response model is equal to item. So it's like what that
thing is. What is this validation item? Okay, so we are validating it right from the start itself.
Correct the like let's say item ID we had right. So item ID received to us should be like an integer
here. So actually let's say that is all fine. Where is my post request right? Yeah, so here my
response model if you see response model equal to item and I'm assigning item call an item that
means anything received for this item value if anything goes wrong here like let's say name if I
pass as in some number one. So then here at this point it will raise an error for get request if I
remove this that doesn't like that that won't make any difference because here in this particular
function.

### [24:26]

I'm not using this item at any point here if you see but for post request I'm using that so that
would be done. Okay, so I miss for the anything which we want to push to the server. We should use
this validation. But it and you are talking about this title, right? So this title is nothing more
like for the code person like let's say you created something and you are like now next some other
person is reading your code. So for that person it would be much easier if you have put in some
title here like what it is doing this particular field, right? Okay, sir. And yeah, we have one more
thing called as postman anyone ever worked with the postman. Okay, one fine. Okay, so postman is
kind of service. So let's say somehow you can't access this fast epi docs. So technically like when
some organization is created they would have put an authentication here like people cannot access
this. So what they do is for the developers they would share some kind of a list of API is needed
for them to work around.

### [26:27]

So same way like we did so what I will do is I will try to replicate what we did here to this
particular place like on a postman. So let's say going to file I will create a new on my postman
screen here. I what I will do is I will create an HTTP request now for my get service. So what my
get service was slash items so I need to copy my URL the localhost slash I need to put items. I
don't have to provide any here as of now because there is no validation or something. I won't see
you this I will just send the request. Yeah, so if you see I received the request here then let's
say I had post correct. So post is also having the same but here now in this case I need to pass so
this parameter is there. So I am just a bit unsure. How would I pass this but it would be like this
if I guess Yeah, let me try this once. Oh, sorry. We are not yet to post sing item ID. Okay, sorry.
What was my name here?

### [29:15]

Let me just check this. Just give me a minute. Yes, you're asking something. Sir, I have not raised
the hand. Oh, there are two harsh here. Sorry, I mistakenly raised my hand. no issues yeah so this
parameter this particular parameter whatever you have so this request body which you have so if you
see we have application Jason so in postman go to body go to row click on Jason and whatever value
was present here you can pass it in here like this way and all your parameters here will go to this
particular params place on this params you need to pass in your item ID

### [31:16]

and your value too so that will get processed so now if I go to here and put items I would feel like
I have created the same request so it like for item ID one and two it is giving me both laptop here
so this is the way how you can actually use postman instead of fast EPI this way swagger UI so
postman like there are a lot of alternatives to postman as well but generally like postman is like
from a very long time and like already most of the people are using postman only so hope we are
clear till this with the post request in okay got it sure so one main thing with postman what you
will get is so you can go to postman add your params I have my stuff in body here you can click this
particular point like it says code you can go here and you can select Python request and it will
give you a request as a Python code so you need to generate this payload like this JSON dumps then
whatever your parameter is is would be passed by your URL so it would contain your URL slash the
actual location slash items and then parameters so parameters would always be followed by a question
mark question mark item ID and equal to 2 now here in case if there were oh sorry I guess I made a
mistake here oh no this is fine yeah so this is how like you can add the parameter here and can make
your payload work like this

### [33:19]

and you need to pass in your headers like content type application JSON so this would be working
correctly like this is what you are passing it input as in JSON and use this particular request
library already given by Python so when you install Python it is automatically installed no need to
install it separately but in case it throws an error then you can just simply pip install request
that would work so request that request post request you need to pass URL headers and your payload
data here like this so that is how you can use Python code now if we are fine with this then what
we'll do is we will quickly go to see a demo of the first agent we had like in the email generator
agent to our crew AI we will serve that as in fast AP endpoint yes sir how this all ties with if we
connect databases let's say you have my sequel okay so there is a like my sequel connector you have
so import my sequel connector then instead of this items to DB what you can do is you can simply
like there would be two things one is a connection cursor so you need to create a connection with my
sequel connector and a cursor on top of this connection to the my sequel and that every point of
time here so let's say I was making a post request here okay so I was adding that to my dictionary
here so instead of dictionary what I can do is my cursor cursor would be the main point which can
execute sequel queries so cursor dot execute then whatever your query would be so

### [35:24]

let's say my items are here right so it would be like insert values into your DB sorry table name
and your values all the values from here so item dot name item dot like that way so we will be
storing these item in our dictionary for now for this particular demo I had showed that as a
dictionary but like as you asked for particularly a database right so I was showing you how to store
this and my sequel database like of like that way we just need to replace that code with any of the
respective particular database code functionality exists yeah there exists a functionality we
actually like we don't have a needed to connect like fast TPA to streamlet we have a request library
that is like a universal thing you just need to import the request into streamlet and from their
streamlet you would be able to access the fast TPA so let's quickly what we will do is just close
the postman let it be like this now we will go to our main thing for today so I have this crew dot
buy with me where I have used the same code from the Google collab notebook I had so the only thing
I have done differently here is I have created a class for my email drafter I have defined my agent
and in the other I have put a run description here so I have

### [37:25]

added my description the input email the task I have created and I have created a queue from which I
will return the result of whatever email is drafted from the what I guess by the agent AI agent
right I have added my open AI keys via the load dot ENV library then what I need to do is I will you
know in initiate two classes here one would be my email drafter and one would my fast API without
this your fast API won't work then I'm creating of like validation that my input email will be a
string then I have created a post function and a get function get function is just for the simple
root functionality like welcome to the email drafter API my post would be the main one where I can
pass in my actual email the input email now to handle the exception I have put status course as 500
like in case of any error it throws and what you can do here is like from the class initiated here
the email drafter email drafter dot run because I have this dot run function where I will pass the
input email so how you can access any particular element that is defined by an identity validation
so request call an email request and whatever the name of the particular type you have given here so
email request so here as I already put request I can directly use this request element instead of
email request so this request will be passed on request dot input email here so this input email
name should be same here so whatever input is received would be passed here and this input email
will be passed to my email

### [39:27]

drafter class so it would be passed here the agent would run and give me the final response email
generated by the AI agent so what I will do is I will just quickly stop this instead of main like
this particular file name is crew so I will put crew and we have one more functionality with respect
to fast API is one is reload so that means like when I'm doing an experimentation If I don't add
this reload argument, what would happen is if I made change to my API, I need to stop this function
like uvcon command and rerun it to reflect the changes. But if I have this reload argument given
here, then just when I save this particular file, the command will be automatically it would rerun
whenever I save this file with a change. There is one more command like let's say port. So port if I
pass in let's say 8001. So by default, it runs at 8,000. Then here you can pass in any port you want
and the particular service would run on that particular port. So helpful when you're deploying it to
any cloud service or any sort of place where particular port is already being used by other service
and you need to assign a new port. So this is running here. So I'll just click this. And if I just
go to docs here, that means draft evil is here. So now as someone already asked about Streamlit,
what I have here is I already created a Streamlit app. So what I've done is Streamlit app is

### [41:27]

I only have a basic Streamlit imported and a request. So this import request would be passed to my,
like my particular endpoint is served on localhost. This is the particular URL for localhost and the
post record would be posted to drafting mill. So slash drafting mill, like these are all the
Streamlit functionalities for the UI part. Here I am taking my string input as a text area. Then I
am using the request library from Python to make the post request. So request.post, the URL of this
particular API and my JSON input will be passed here, like input email. And whatever my input email
was here, I can pass it here like this way. So I will just quickly run this, Streamlit run app.py.
And like here, after you post this request, you would receive your generated response in a JSON
format or mostly it would be JSON format because I'm passing the response as a dictionary.
Dictionary meaning JSON only. So drafted email and my response. So whatever QA's response would be,
sometimes you might need to access an element inside the dictionary. So what I have to do here is
response.json to access the output of this particular post request from the server side,
response.json, then get this drafted email. So what this .get does is, if I don't get this drafted
email element from the JSON response from the server, I would throw an error, no email drafted. If I
get the drafted email, then it will be stored in drafted email variable. Now QA's response was like
the final response

### [43:27]

was stored inside this row key. So I again had to put this, like I had to access the row key from
this particular drafted email variable. So here you would be able to see drafted email and I'm
accessing the row key here. So I will get the values from the particular row key. So I'll just go
here and I need to pass in an email. So what I will do is I already have an email here, sample
email, I'll go my streamlit application, I will paste it here and I can just click on draft email.
So we just saw like, what I did here was, I put it port 8001 and now with respect to my streamlit
application, I'm posting my request to port 8001. So this won't work. So what you need to do is you
need to change that to 8001. So I will go back here, always rerun and now I will draft my email. So
if it is running, you would see post draft email 200, okay, meaning this actually ran and you're
getting a response here. Here is a drafted email. So that is how streamlit connected to FastEPA
endpoints and you can pass in your input via the UI. So that is how this particular thing would
work. Oh, Chirag Harsh, this time I have a question. So can you please brief it like, how this QAIN,
this in-memory DB and this FastEPA and all these things and how these things are interacting with
each other. If we can just show in some time, I might get a few or something like that. Interacting,
okay. QAIN, FastEPA? Yeah, QAIN, FastEPA and one more thing,

### [45:28]

like here we are using any sort of DB, isn't it? In this port? No, no, no database here. Okay. So
what we had was a notebook of code with QAIN, okay. What we need to do is we need to define an
FastEPA, like import FastEPA, define the FastEPA, initialize your FastEPA, create a post request.
Now, whatever code you had to run your QAIN, you need to put it in here. Now, anytime any user make
a request to the FastEPA endpoint, so let's say my endpoint was draft email. So when any person is
on this particular URL slash draft email, when they pass in and request, that request would be
captured here in this particular request element and this particular code would run. So whenever
someone access draft email, any code you write here inside the function would run. So that is how
FastEPA is responsible to run the code of Krivi. They are not actually like interacting with each
other. We had a code, we are just wrapping it in a FastEPA wrapper. Does it make sense? Yeah, and
like this QAIN as you mentioned, like it is working as an agentic tool. So where are we ensuring
that we are using it in a code and it is working as an agent, okay, in this one. Yeah, we already
defined a class, like all the full flow of like defining the agent, defining the task, everything.
Okay, understood, understood.

### [48:00]

Okay, with the deployment tool. So like FastEPA, if you talk from a broad perspective of let's say
MLOps, LLMOps, AIOps, DataOps, like that way, then FastEPA is a way to serve the model. Now there
could be multiple tools like that. Let's say MLflow, EvidentlyAI, DeepChecks, Docker, Kubernetes,
CICD pipelines, GitHub Actions, Ansible, Jenkins, a lot of tools. So each tool would be serving a
particular idea in a MLOps, LLMOps pipeline. Not necessary, everything has to be used in every
pipeline, but each tool has its own purpose. So for now, at this point, FastEPA we used to, now you
know, like sort that to like you created a model, but you can't share your notebook with other
person. Like you have your database stored internally or in your local system. If you want to share
it, like make people use that, you need to sort that in a particular way. So we use FastEPA to sort
that as an API endpoint, such that the same APIs you can use to connect with anything. Like you can
create a stream lit quick prototype, you can connect with an actual website or an Android
application, iOS application, anything. Just that your FastEPA sort agent model should not be on
your local host. It should be deployed on AWS, Azure, GCP type of a cloud.

### [50:06]

So any doubts with regards to Fast API or streamlined way we connected to Fast API? So Criu AI is
actually using this email drafter tool, right? What is using what? Criu AI uses this email drafter
tool that you created, right? No. Email drafter tool is what is where we have defined Criu AI, not
Criu AI is using email drafter. OK, so you have defined a class. Yes, inside that, I defined my
agent first and then I defined a function where I wrote the task where I created my Criu and like my
Criu.kickoff function, which is used to generate the response. It's like written here and it will
return the response. So Chirag, in this when you were running the application, so I noticed that you
were providing already a created email, right? And then it is just improving that email or what? No,
no. So what it did is like Dear John, it was sent by person Alex. So here it is like generating a
like responding email. Dear Alex, thank you for reaching out like this way. OK, that is just
responding that email to the sender, right? Correct. So here, as the AI agent only had information
about John as like name, what it did is like it only did best record John. And here you can add your
own position company email like this way. OK, so whatever information it had on the basis of that
information,

### [52:06]

it just drafted an email for you. So might not be necessary that you need to send it fully, but this
is one of an area like where use of AI agents is increasing, like any place someone got an email. So
the agents are now getting connected to Gmail outlooks. So whenever someone receives an email, if
necessary, the AI agent might respond to something if required on an urgent basis. OK, what all
things can we do with this agents? It's like, what are the use cases of it? Any sort of an
automation idea you get? So any idea you are getting right now to automate something? Mostly like
YouTube automation or blog writing automation, you can say. Right. Blog writing. I guess that code
is already shared. Blog writer on the portal. YouTube one is not there. Blog one is there. YouTube
one is also kind of like pretty simple. There would be multiple elements to it. One difference would
be that there would be some transcription tool there that can that would extract out the text from
the YouTube video. And on top of that, you can, you know, use your agents to summarize the whole
YouTube content or have a rag pipeline type chat service for users where people can just enter the
YouTube URL. The model will process for a bit of a time. It would create some data out of the
YouTube and store it in a vector database,

### [54:07]

temporary database, and users can chat on that YouTube video, like what was discussed in the YouTube
video and stuff like that. Actually, I'm looking for the other way around for if I am a creator and
I want to upload, so to automate the entire process, it's like they have a video idea, they just
feed in the video idea and the video itself, the title, the thumbnail, the description. And if there
is another thing that is links and all those things, if they are, they all automatically gets
created and uploaded to YouTube. All the things can be done entirely. Can we do that? Yes, that can
also be possible for that, like generation part. You need to see what models, like, I guess, OpenA
has released SORA model, Google just released some video model, right? So you might need something
like, let's say, you add a title. There would be one agent who is generating the title, then one
agent who would generate the script based on that particular title. Then based on the script, any
model from OpenA or Google will generate a video for you. After that video is created, if you have
YouTube APIs available, from the APIs, if you can directly post onto a particular YouTube account,
then that video would be automatically posted via that YouTube API. An agent like that can also be
designed. OK, so this can also be automated? Correct. Just that the models which you are using, like
video generation models, that should be actually capable to generate stuff like that. OK. So in
essence, I can say that Creo AI actually gives us a way to create multiple agents and automate the
task.

### [56:10]

Correct. You can have sequential agents, like five agents working one by one, or you can have a
hierarchical structure where agent one works, then agent two, three works, agent four works, the
output of agent two, three gets combined by agent five, then agent five and fours again would be
compiled together to generate the final response. So that way also, that can work. A multi-agent
type of thing? Correct. OK. Where can I learn about these, like any YouTube tutorial or
documentation other than Creo AI? Other than Creo AI, like other frameworks? Other frameworks. So
onto the portal, we already have code for Lang chain, Lama index, Lang graph, Phi data. Phi data,
I'm seeing that its usage has increased recently. There are a lot of tutorials on that. Yes. So they
have created a more simpler version compared to Lang chain, Lama index. Yes. But in case you want a
good control over the flow, then Lang graph is a better version. So let's say, why Lang graph is
better? Because it lets you have control over the whole flow, like this way. You can create graphs,
you can create nodes,

### [58:10]

you can define how the nodes are connected with each other, like chatbot, it will request the tools,
it will return the response back from tools to the chatbot. A lot of things can be done via Lang
graph. And Lang graph would be the part where we would see the corrective rag, agentic rag, a lot of
different things in this coming week. Like modern rag architectures, modern agentic rag
architectures is what we're looking to see on Lang graph. Okay, no problem. I will be looking
forward to that. Sure. Okay. In case you still want some resources, you can kind of drop me a
personal DM on Slack or WhatsApp. I can share you some resources there. Okay. The main flow is
completed. In case you don't have doubts, you can drop off. Okay. Thank you. Thank you.

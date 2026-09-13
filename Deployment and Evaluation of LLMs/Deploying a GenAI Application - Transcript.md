# Deploying a GenAI Application — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Deploying a GenAI Application](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/77321866-deploying-a-genai-application)
> · Video lesson, 135 min (`2:14:51`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:06]

All right, how are you doing? Good evening. So, right. So the previous four sessions, we saw a lot
of things like fine-tuning rag, agents, and multiple things around those basics, how can we
implement those kinds of solutions, got an idea about the project level structure, evaluations, and
different things, right? So after that, we are going to today look around the deployment of the
things, how they happen and all. So with respect to the materials given, you all might have probably
gone through Docker and all of those kinds of materials. If not, please make sure you go through
those materials first and then try to have a look at the session because Docker, FastDPS, Streamlit,
all that would be important. FastDPS, Streamlit, I guess, is covered a lot of time, so it won't be a
trouble. Docker is also something like in the last session that we had in that a few basics were
covered and creation of Docker container and everything is there. So that also should not be a
problem right now. So the major part of the session, we are going to focus on AWS part and what made
it had, let's say, think about the architecture of the solution or pick one part. Like there are a
few architecture, a few ways of deploying a solution. So what are those few ways and how did we go
ahead with one particular solution is how we'll try to move around in the lecture, right? So how the
whole setup is there,

### [2:11]

we have three kinds of layers today. One is the application stack, deployment stack, and the
operational stack. So the application stack is majorly like, you know, our basic things set up,
Python, Streamlit, FastAP and all. Deployment stack is the Docker, the AWS services like ECR, ECS,
Fargate, and the support level or the supportive setups around that like from the AWS, like Secrets
Manager, CloudWatch, AI and everything, all of that combined together to form out a complete, like
one baseline solution for the deployment part, right? And also at the very end of the session, I
will give you ideas like how you can scale up more onto the same architecture and going forward what
few things you should learn to maybe improve your at least basics. But in those cases, you should
also understand that, like if you are already a data scientist or maybe somewhere in the role of AI
or somewhere and going to move forward into directions where you want to start developing end-to-end
solutions, remember that, like if you are in a more role of towards the deployment of solutions,
then in those cases, you need to put more focus onto different things into cloud services, maybe
look out more things into GCP, Azure, and a lot of things. But if your role is majorly towards
building the solutions, then that would mean that you would be focusing more onto developing those
kind of fine-tuning, rag, agents kind of a structure, and you would help out the team into like
building around the architecture structure of this cloud. But there would be a dedicated, maybe a
person in the team

### [4:12]

or a DevOps team would be involved where they would figure out the architecture at a high level,
what services, how the data movement and all that would be required for the cloud to happen. That
would be kind of a more of a collaborated solution at the end of the architecture, and there are
obviously like now architectural roles in a special architectural roles in AI, like people who
specialize in having architectures of their full stack, how to develop them, generate them. So it
depends on how structured you, your team, your setup and everything is. But yeah, majorly depending
on the role, like there would be a difference in how you're going to develop or what part of the
solution you're going to develop at whatever team you're working with, right? That is from the
developer's perspective. From the perspective of like if you're an architect or if you're a manager,
project manager, product manager somewhere. So how you can look at the session is more like, you try
to understand what things are there in the cloud, what things we might be able to be used and like
you can try to look at, like if you already have that understanding of software level deployment
solution and everything. Majorly, I believe the same things goes here. You won't need to focus much
more there because at the end the AI products are also software, right? So the idea or like you
already have the architecture idea and everything, then in those cases, I believe you already might
have all the sufficient knowledge to understand why we did a particular step and why a particular
service was chosen, right? So let's start with the session. We'll start it very quickly with the
code architectural,

### [6:15]

like just understand what is there in our code and we have chosen a very basic code service today,
like just for a demo use case, that is a simple LLM service where we are calling an OpenAI client
and this is how my structure looks like, like the main file where the whole of the FastAPI backend
services and everything is there, the entry point of the FastAPI, where it defines the connections,
routes and everything, the LLM service, the connecting to OpenAI, like calling the OpenAI as an API,
generating the response and everything. The similar files that as we already know, like schemas
where we define the identical level structures for whatever you might be using, let's say the
FastAPI or LandGraph everything, so whatever those kind of request response models and everything
you have, we put it down there. The validation file, technically for like input guard, this input
validation, we have just put it just to check for the data that is coming from the FastAPI. Prompts,
any kind of a prompt that you can, you could also version the prompts if you have a LandGraph level
structure or a setup. So in that case, there would be multiple graph nodes, agents, everything
involved in the overall process. So like multiple prompts and everything you have, you can handle it
via the prompts file. The config file, like kind of reading from the environment file, loading that
environment file. So technically the kind of, you can say, like is a kind of a file that reads the
settings variable particular,

### [8:16]

like you might have noticed in a lot of code ways there is a settings variable through which we read
all our environment variables, that config file is just a settings class that is going to read out
all the environmental files, maybe whatever kind of file, your .env file or anything, and then a few
supporting files like logging configuration. So like, how are we going to store the logs and
everything? And the evaluation.py file that is just going to generate a small evaluation over the
main.py file, like running our simple, so the main code, the main part that is going to run inside
the main.py is a kind of a customer support tries tool. So that is kind of a user query comes in and
that particular request is tries based on some urgency level and everything. So that is the kind of
idea. And for that evaluation is done on that particular tries, how correct is the tries that is
happening. So based on it, some kind of a score and all would be evaluated. So that is for that what
evaluation.py file is. Now, each of this file is made very simple, like just a few Python functions.
In actual productions, they would be much more, like with all the tools that were used previously,
like deep eval for evaluation, land graph based codes and a lot of different things. Like so, not
included all of this here because that would have made the code base more longer, more complex. So
just to make it focus totally on the AWS part, this. the app folder has been made simple so you can
just have it run it like as some simple services and just focus on to these parts docker and the AWS
parts that will look and apart from that with this front-end folder would have our stream list
structure this data folder is just storing the

### [10:16]

evaluation output the test folder is kind of a pi test that is written so we'll also discuss the pi
test and settings like you know why it is also important for the structure setup docker and docker
compose as we know these are totally for the containerization of the services like how we can let's
say for example this whole app we can put it into as a container for a back end front end also we
can put it as a container for the front end so like with the containers like two images can be
created they both will run as a container so for like you know a single unit from where multiple
containers can be created executed so for that we use docker compose instead of a single single
docker file set for multiple services we can club all the services through docker compose so docker
compose like you can think as a kind of a service through which we can club multiple containers all
in all together using one single command we can start each of those containers without again and
again like you know calling those their docker files so like kind of a automation file of a setup
you can say it now just going through a few basics of the system what we have here so like we'll
have simple three API endpoints that you would see one is the health one like just checking the
health of the fast ap application the generate is the main business endpoint like it is kind of a
user is user or the front end application is going to send a json object with one single request
that is going to be the message the like user message whatever like could be anything complain or
anything and the application returns a category intent and priority or again also along with that
the reply for the customer

### [12:16]

so this is what they're triaging so behind the scenes customer triaging like you know whatever the
complaint issue is based on the triaging is happening so this is with all respect to the generate
endpoint the last endpoint is the docs as we know like you know fast ap gives us a open api kind of
a documentation setup like where we can directly see it like you know we can also execute and
everything so that is just a inbuilt fast api kind of a lever service right now coming to this
generate a flow code so what happens behind this particular exact generate endpoint whenever we're
going to hit okay so why i'm explaining this through the slides why not to the code is because this
is all we have seen lots of time right so like just going to show you the overall code flow we're
not going to just run to the app folder we are not going inside the full code structure inside it
we're just going to focus under the aws code part so we'll just take a look at from the theoretical
perspective of the app document the fast ap and stream structure okay so inside the generate flow
like whenever a request reaches the generate endpoint pydantic is the first setup that is going to
run that will first take the validation step if the input json is wrong or the message field is
missing extra field or anything is present fast ap is going to give us an sttp error with a
particular error code 422 like fix the input like in input is incorrect that is what we are going to
trying to show so this is now here we are also playing with the uh sttp error codes so that is also
like you know very important like you know what error code

### [14:17]

along with that what particular message to be sent because like there could be multiple different
levels of error that can be involved maybe somewhere open ea your open game might be still working
but uh somehow uh some version change or something has happened so open a levels issues errors what
to show it with which kind of error code anything like that so that is all you need to particularly
specify different types maybe database error with a separate code and everything so that is also
something you need to define set up with certain number of error codes and everything so apart from
that like after the pidentic setup the application will then kind of know will check for any white
space or anything and if it finds white space removes it just try to check it and validate and then
builds the user prompt the structure so kind of a prompt building structure and everything happens
gets sent to the opening api and opening it already has this structured output structure the
category intent priority that we saw so using that support response kind of a structure it is going
to generate the output in that particular format will validate the outputs category intent priority
in a proper structure like it is defined as per the rules we have given and finally we'll return the
output json so this is how the overall flow would work and the other error codes that we have is
like no if any api key is missing connection fails or timeouts we'll just give 503 any api failure
or structured output anything kind of that is missing we're going to provide error code 502 so that
is how the generate endpoint overall flow is going to work next is understanding the docker so we
can also run our code in two ways now one is which we have seen in the like you know fine tuning or
the rack sessions like

### [16:23]

running it through a local processor like using uvcon to start api fast api endpoint services and
streamlet like streamlet run command but then in the last session we saw how we can also use docker
so let's see if i'm just going to hit docker compose up build what it will technically do is we
would have already given a docker file or inside the docker compose file itself different things are
mentioned at what port what section and everything we're going to have so we'll just have a look at
this docker file right now how they are structured for front-end backend services and what we'll
essentially do is when we hit docker compose it is going to use this images that is python version
3.12 it opens up two ports 8000 for fast api and 8501 for the streamlet front end and like the
connection between them both would be like the streamlet is going to call this particular api 8000
from the inside of the docker network and there will also be a health check present so now there are
a couple of things more that i guess we would need to look at is the byte test so here we have a
testing setup a basic unit testing setup that is trying to check or i would say you know making mock
test so just to understand like you know if our api is receiving the input correctly generating the
response and everything so this kind of pie test checks you can also do so pie test checks are like
you know kind of deterministic software behavior so the llm like as i mentioned is a kind of a
mocked so the tester fast repeatable and do not make paid model calls so the oral idea is no to
check or cover cases

### [18:30]

like health behavior validated structure validate structured output outputs any kind of a blank
input missing configurations unexpected field inputs so all of these things would be covered under
the pie test test like the more and more test you can add the more secure you can make your
development setup all the cases you can try to cover up then there is also something like a rough
check so rough is technically kind of no kind of catches any common coding level mistakes and it
tries to generate like warnings errors in case it sees any wrong i would say function written
somewhere or like maybe some certain indentation or something you might have performed wrongly so
that rough is going to give warning or edit up out of there so that is how rough is there then
finally the live evaluation so evaluation as we have seen in fine tuning rag discuss also in the
agents part evaluations is technically the most important part in terms of the AI's perspective,
like the AI solution we have. But testing it out, like is it working correctly and everything? So
before the deployment, live evaluation or the evaluation set is very much important to understand
the capability of our Gen. AI setup. So once all of this kind of different checks are done, you can
start building go towards the Docker part. So let me just share my VS code and I'm going to share my
full screen.

### [20:42]

So inside the readme, all of the basic instructions to run the setup and everything is already
given. So let me just start Docker. Let's just start by running with the commands like individually,
uvicon and streamlet. All right, our Docker is started. I just started the FastAPay services. You
can see application startup complete and streamlet is also ready. This is our kind of a basic setup
message you would see. So let's say if I just type my order is late by two days. Well, we're just
trying to check if our current structure is working fine, right? Category intent priority medium,
right? So the set is working. So what we're going to check next is the Docker setup, right? Before
that, let me just show you one of the outputs of this evaluation report, right? So if you're going
to run this particular file from this evaluation.py file, the command is already included here,
app.evaluation output as a evaluation report.json. So it is going to read this particular file

### [22:42]

from the data, evaluation.dataset.json, like covers the message and the expected output. And the
evaluation report that is going to be generated is kind of what output it predicted and the category
intent priority will be matched. So it will show field accuracy. What is the field accuracy? 87% and
exact match accuracy, 62%, meaning like against the evaluation data set, our system was able to
reach somewhere around 63% of the overall accuracy. So that is like a separate discussion onto
improving the setup and everything. But yeah, this is how evaluation is added, evaluation is done.
And then finally, you what you need to check before moving for the AWS or the main deployment part.
Yeah, we can also check this actually. Let's say this rough check, screen it out. Yeah. So you can
see here, it's showing a few things, like import block is unsorted or unformatted. So kind of, it
shows things like this, like in terms of coding perspective. So this is from OpenAI structures, it's
kind of recommending a more better way of writing this code part, like from OpenAI import and
everything. So this is, I don't know, like rough check shows any kind of a coding level, minor
issues, warnings, and anything that needs to be done. If any major issues that like you have written
a wrong function, like that function does not exist in the library or anything, those kind of
errors, it will also show it out, okay. And the PyTest, PyTest, we would have a separate test file,
like this test API and test validation. So the whole kind of PyTest is that we have this kind of a
functions, and in that, what it is going to do is,

### [24:43]

it is going to kind of start an app, then this test client is there. So it is kind of calling the
health of the health endpoint of the fast API endpoint. If it returns correct status code, meaning
our API, the fast API service is running perfectly. So it is like kind of giving these asserts and
everything. We could have also done this without the PyTest, but the overall difference is that,
when we create a folder like this test, inside that, we put all of our testing configurations, like
let's say this was one function, test help without API key, then test generate returns, structured
responses, like we're checking for structured output. So let's say, if my structured output setup is
like this category intent, and then I'm going to put a variety reply like this, is what I'm
expecting. So we can type in all the functions together, and then we'll just need to type in PyTest
into the terminal, it will automatically identify there is a test folder. Inside the test folder,
there are multiple functions, like it will also check for kind of the PyTest level settings and
everything, and it will just try to run those files. So when it runs all of those files, it will
also show you finally the output like this, how many tests passed, warning, everything. So that is
like, we're kind of consolidating all the tests into single files or multi files, with respect to
the structure, like all the API-related tests, all the validation-related tests, everything, we
consolidated together into a file, and then we just run PyTest, it is going to run everything, and
any kind of warning. So let's say it's showing this error, something like library level. So this
HTTPx2 should have been installed instead of HTTPx. So warnings, like if it is major something
around library function, deprecation, and everything, make sure you change that, but apart from
that, usually the oral idea,

### [26:44]

like whenever you are going for deployment, is that all the tests should ideally pass correctly.
Okay, like there should not be any kind of test that fails, you still push it to production, because
if you know things like CI, CD, and all, even whenever there is a new code that is being pushed to
the setup onto the services, like GitHub or everything, where your code repositories and all are
maintained, the test would be ran, and if any of the tests fails, that CI, CD part in itself, that
all also fails, right? So kind of looking at it from that perspective, before pushing out your code,
all these test level things and whatever are predefined should be validated, all the tests should be
passed, and then and then only the code should move from your local to kind of a GitHub service or
should go for deployment. Maybe for services like, let's say, like today's case, which we'll see is,
my local code will directly be built as a Docker container, and that container particularly goes
directly to the AWS structure setup, right? So when like, you would be kind of building a full
overall solution or something like involving DevOps team and everything, you'd have a more bigger
code base and everything, obviously CI, CD on those kinds of services is going to be involved. So in
those cases, this kind of test validation, test all the tests passing as a fulfillment and
everything would be necessary, okay. So that is how our local demo looks like. Now, let's move
towards the main part of the solution. All right, the AWS settings part. So what are the possible
AWS deployment architectures

### [28:44]

that could have been selected? So, like you know, the most basic one, like for that recording was
already shared, right? For the JNI program participants, the recording was already shared of using a
basic EC2 server. So EC2 server is the most direct option, like we create a virtual server, install
Python, Docker, or if it is a non-Docker solution. So we install our system setup there inside that
virtual machine, and we start our process, port it with the outside network, so that other external
users would be able to use it. But this is also something that we are going to have our own OS
system, we're going to set up all the things, like what happens when the server goes down, like this
is kind of still suitable for small setups. or small teams who want to just have a server, launch
something like that can be done quickly. But as we move more towards the production side, the more
better architecture is like from the simple easy to would be something like let's say you move
towards the containerization because your code setup has too many things. So you containerize the
overall setup with multiple services, let's say database, backend, frontend, some Redis service,
some caching service, all of them, all the five, six, seven, eight different services in a single
Docker compose file. So in those cases when you have those, we have something like ECR. So ECR in
AWS is a service where all those versioned containers, specifically the Docker containers, they get
stored or the images of those containers

### [30:47]

particularly get stored in the ECR. Whenever any service requires it, for example, let's say EC2
here in this case, whenever it requires it, it can pull the image from ECR when required. So how it
changes the overall setup is let's say, you are working on your local, you develop your Docker
container and everything. We create local Docker containers, confirm that it is working fine, and
then using certain commands, we can directly push that container image to ECR. Now, this all would
be versioned across multiple levels, and you can define something like this. Whenever you have new
code setup and everything, you design it, you run the Docker, and you send the latest version to
ECR. And through EC2, that EC2 would be like ECR is just for storage purposes. EC2 would be
something like that is going to act as a running server, as a solution that is going to run the
Docker services. So like EC2 will fetch the image from ECR and will start running the service of the
Docker onto its server. Now, apart from this, two other services like runner or Beanstalk are also
there. So they are more of a managed application platform, where they are identically designed for
standard web services. But for AI services, they're not majorly more that well, like they have
certain limitations and all. And certain types of trade-offs are also there, like you have a very
less control over the setup, like if you want to have some kind of a server or anything. And it has
a certain own setup, so we'd need to be kind of working the platform-supported patterns or
workflows. So usually app-runner or Beanstalk is something what you might not go with using it.

### [32:50]

So that leads us to options like ECS, ECR combination, or combination of ECS with Fargate or
EC2-managed instances. So now there are a couple of architectures that you would see around ECS.
Before that, we'll go for this now. We'll see this EKS. So EKS is kind of providing Kubernetes on
AWS. It is kind of a good, ready setup for teams who already are working or have set up their
ecosystems in Kubernetes. But having that sort of setup would mean that your codebase, your oral
structure is also large enough such that that kind of a large operational structure or the
operational surface, maybe it could be your overall full code setup or that is some kind of large-
level data engineering. A lot of different things are happening. So usually in those kind of cases,
this Kubernetes kind of solutions and everything is going to come into picture. So if you already
have that, then you can go ahead, continue using those EKS kind of services. Apart from that, the
Lambda and SageMaker services are also there. So Lambda is a kind of API gateway for short event-
driven services. So let's say if we only have OpenAI endpoint to be called for certain prompt or
something, it is something like you can simply create a Lambda function, deploy it as a running
service. So all the users will come to an API gateway, will send their input to the Lambda function.
Lambda function will run and return the response. So for all the simple setups or things like this,
something like you only have one prompt or multiple prompts, you do not have something like a big
Lang graph kind of a service. You have a simple OpenAI calls,

### [34:53]

simple Lang chain setups or everything that all you can combine as a Lambda, like AWS Lambda
services, most easiest to use. It will also be on demand. So let's say whenever the user is going to
pass in a query, it will quickly invoke and will call the OpenAI, generate the responses. But for
cases where it is going to be more complex, more complex towards the architecture, like you have a
whole Lang graph, involves databases and a lot of different things, in those cases, you will start
moving back towards this kind of services, ECS, Fargate, ECS Managed Instances and everything. And
SageMaker is also there. SageMaker is more traditionally relevant with ML kind of inference services
running from the Notebook, SageMaker Notebook and everything. So there is something like not usually
heavily used nowadays. So let's go back to this, talking on these portions. ECR, ECS, EC2 Managed
Instances. So these two are the important, I would say, kind of architectures that could help. What
is the ECS with Fargate option? So for applications which we have, like in today's case, let's say
we have a front-end, back-end, containerized services, maybe we could have also added, like if it
was a more complex solution, let's say from the previous session, the agent solution or the rack
solution, if we would have particularly picked. So in those cases, let's say, we would have multiple
things like memory with MongoDB, one service is running the agent, front-end is running, certain
kind of caching and all, everything is running. So in those cases, ECS with Fargate is option. If
we're going with a proprietary or a closed source model.

### [36:55]

So you can think of it like this, ECS is kind of a service that handles container orchestration,
meaning all the Docker container and the level, like if what happens if a container stops, how to
restart it, when to restart. So all that kind of container orchestration, the ECS will handle onto
AWS itself, we define, like these are the containers, these are the tasks, health checks for the
containers and everything we define in the ECS setup. And Fargate is something like that is going to
run the main compute part. So compute part, meaning let's say in ECS, we define the Docker container
setup, the part how, like we define a thing called a task. So once we define the task to run the
task, Fargate comes into the picture. So Fargate is just going to read the task definition from ECS,
like what Docker containers or everything is there defined in the particular task. And that
particular full task will be picked by Fargate and will be executed. So you can think like ECS is
just an orchestration service, Fargate is the one that is going to execute it. So there is a
difference between that. Versus the other part like ECS on EC2 managed instances. Now Fargate is a
kind of a service that does not have GPU workloads. So in case you have setups where you need to
involve GPU, like you are having open source models or you need to use GPU at certain sections in
your code to maybe handle a few things. In those cases, Fargate won't be used, but instead of that,
you're going to use EC2 based managed instances. So we'll also see like during the session, like
there is an option to select going for Fargate or EC2 managed instances. When we select and go for
EC2 managed instances, we would need to particularly select

### [38:55]

what kind of OS system, what kind of, I would say, GPU based source selection, everything to be
done. So that is kind of two differences of architectural differences like we can make on ECS
orchestration, like all happens during the selection of ECS creation of ECS task definition and
everything. So ECS is something you can think is a major service here. Like once we define
everything in ECS, only and then from either Fargate will get executed or EC2 will execute. So most
acts as an executor for any kind of plans that is defined on the ECS. And ECS kind of orchestrates
all the process between all the containers, services and everything, like just acts as a controller.
Okay, so I hope that from the architecture perspective, it will be cleared. Now, like I guess, yeah,
okay. Basic difference, we'll just try to recap. So let's say a simple EC2, like how the things
happen is that the whole application level codes need to be copied to the server. While with ECR
plus EC2, like whatever container image we have developed, we pass it to ECR. Same goes for ECR plus
ECS file head, that also goes the same, like we send it to ECR. Then at the runtime, so in EC2, you
need to manage everything, like starting scripts, SSS files, what particular command to run, versus
the ECR plus EC2, whatever associated Docker command is associated, you need to enter it so EC2 can
run it from the ECR. With respect to the ECS kind of a managed mode, you can consider Fargate or EC2
managed instances here. Now there is a difference here. Please note, ECR plus EC2 and ECR plus ECS
along with EC2 managed instances,

### [40:55]

both are two separate things. The ECR plus EC2 is something like EC2 is just pulling Docker image
from ECR, versus ECR plus ECS EC2 managed instances, that is something like ECS is going to do all
the Docker level service setup and everything for the EC2. So ECS plus EC2 setup is going to be more
better compared to this ECR plus EC2 setup, just kind of noted down. Okay, so this runtime or start
setup and everything, ECS task definition will handle everything for us. ECR plus EC2 Docker
commands need to be executed onto simple EC2 server, all the scripts and everything, you need to
mention it separately, like you need to note it down everything. Server patching, like any issues on
the server, you need to do it everything. ECR plus EC2 also, you need to do everything, like ECR
will manage Docker, but running Docker and everything, any issue with Docker. EC2, at the EC2 level,
you need to manage. While with respect to ECS services, AWS is going to manage all the different
things that are going to run, like this is kind of AWS managed services. Okay, desired state
recovery. So in the first two cases, we build it by ourselves, how we are going to recovery states
and everything. ECS also already has kind of a setup where if some kind of a task service fails, it
kind of restarts the task and everything, by default itself, it has this capabilities. In terms of
scaling EC2, the basic ECR kind of cases, we need to configure everything, scaling parts or the load
balances, everything. With respect to ECS and everything, task count or auto scaling can be
configured automatically. So it will make scaling much more easier in terms of like going from 10
users to 1000 lakhs of users, it would make it more easier. And just we'll discuss the important
part, the GPU access.

### [42:57]

First two cases, you can have GPU. If you're going with Fargate, GPU will not be supported. So
instead of that, as I mentioned, ECS on EC2 managed instances would be more better option when you
are involving, I would say the GPU level or the open source model kind of things you are involving.
ECR plus ECS plus EC2 managed instances would be the recommended architecture to pick when you want
the GPU workloads to be involved. Okay, Brahmananda asked a question, is there a cost associated
with AWS EC2? As I understand, if you don't configure this properly, then the cost can be enormous,
right? Yes, so whenever we are going to deploy this also, there is a minor cost associated. So when
I set it up this, I tested it out a couple of days back. So I had this running for an hour and a
half or something. So it costed me around 0.03 dollars, right? But this was with respect to very
small kind of app scale. Now, let's say if I have more number of containers, if I am having some
sort of a GPU workload and everything, then for sure, like those estimations would go to something
like $5 per hour or so. So surely, like if you do not select what server, like let's say if you are
choosing a small language model like Gemma 3 and you are taking a GPU that can run a 70 billion
model, then the cost would not be associated with how much part of the GPU you use, but the amount
of GPU you have reserved for yourself, right? So that cost could scale up. So whatever resources you
select with respect to cloud setups and everything, make sure you select necessary setups and
everything. There can be certain level of buffer resources

### [44:58]

and everything involved where you define everything. Also services like auto scaling and are also
important, meaning whenever there is more number of users or request are coming to your resources,
the auto scaling part where you have something like vertical scaling or horizontal scaling, meaning
when to increase the resources or the, let's say you have one server with 30 GB of RAM, more
requests are coming, you have set up a vertical scaling. If we identify that our resources are
getting used, how much to scale it, like scale it to 50 GB RAM, or if it is a horizontal scaling, if
you have one container running, how many more containers, like split one container into five
containers, each container handling 100 different user requests. So all of those auto scaling and
everything should be also properly handled. So that is all, as I was mentioning, right? The devops
teams or the dedicated architectural persons of how we're going to build a full setup of scaling for
ends of users should be considered. Can you kindly share any optimized configuration guide that
helps please? Sure, after the session, like, no, all of this different selecting the proper kind of
GPU level workloads, scaling and everything, we'll send it as a different document altogether, apart
from whatever today's session documents are there, we'll give a different document for those things,
optimized configuration guide, not an issue. Right. Now, coming to the EPR plus ECR Fargate, right?
Like, I guess we already discussed a lot of things on it, just to visualize it from the terms of
this arrow,

### [46:58]

like you can see all the user level request will come up here, ECR should be there with the Fargate
launch step selected, so it will be running one task, that particular task would be the one holding
the Docker level containers, and they will be fetching secrets. So you would have all those secrets,
right? The OpenAI API keys and everything. So all of the secrets and everything that is there, we
store it here, so whenever any kind of container service is running, which requires this secret APS
keys and all, AWS already provides a secret manager, well, it will fetch the secrets from there, so
how to configure the secret manager, and that is also included in the code setup that we'll see,
okay? Amazon CloudWatch would be kind of connected with the containers, which will store the logs
and everything, the input, output logs and everything, so that is something that we can configure,
whatever logs are there, we can just connect it to CloudWatch to store them, like the container logs
and everything. Amazon ECR would be the one that ECS would be using to fetch the latest container
from, and IM is mostly kind of a, you can say identity-provided service, like all the clouds have
different kinds of IAMs, so for example, let's say the identity and access management that the AWS
names as IAM is kind of a service through which the users, or like a particular user controls, or
let's say there is an organizational account, and all the developers, they get certain AWS accounts
through which they would be given certain basic privileges around, let's say, who can create
services, who can work with the services,

### [48:59]

who can run on the services, who can monitor services, so IAM is like an identity provider for all
the developers, people involved in the project, so they all can kind of have certain level of access
to different AWS services that particular main, or the root account is running on, so that is how
the things work, and... whenever we create IAM roles or users, particularly users, like whenever we
create IAM user and give it to a particular developer, we also specifically say that, let's say if
the user is going to work on, let's say just the ECS or EC2 services, we just kind of give access to
only to those services. So our main idea is that isolate all the users so whenever any service goes
out, we kind of trace it back from where exactly, maybe a wrong code push was done or something and
kind of not only it helps with the traceability, but also all the developers will have the dedicated
functions only which they can control. So that is what the main function of IAM is there. All right,
and just a few of the AWS clouds or the basic cloud basics, like those who are not very well aware
with the cloud setups. So right, now a few basics on the AWS terminologies, one is region, okay, so
AP South one. So AWS or any major cloud provider, they have data centers, as we know, lots of data
centers across the globe. They would have availability zones, like for example, in India, they have
Hyderabad, Mumbai, Kolkata, and a few more, I believe. So the idea is there, they have an
availability zone, inside that availability zone, there will be regions,

### [51:00]

like maybe AP South one, AP North one, East one, like those, similar to US, US would be US East one,
US East two, a lot of regions would be there. Now, ideal case, your main solution, wherever you're
developing you, like based on what geography of users your users are from, you would develop that
solution in that particular region because deploying the solution in different region, maybe there
might be a certain different level of latency in world. So whatever kind of backups of your services
or anything is there, or kind of a, let's say if your main service fails, what you do, you create
another backup service into a different region, why? Because there could be certain cases that,
let's say there is some sort of environmental impact onto a particular region, let's say there is a
tsunami in Mumbai, it affects certain data centers. So let's say you have another backup service in
Hyderabad, so when the AWS system identifies if you have the proper setup and everything, so if
Mumbai service goes down, the Hyderabad service would be used as a kind of a second service where
all the users queries would be routed to. So that is how the DevOps teams and everything would be
majorly playing a role there, defining all of this kind of setup, the backup services, what happens
when the service goes down totally, the downtime, how to handle the downtime and everything
configured. So these are all the things, but the basics of regions are there that wherever you're
deploying, you should have the one. Apart from that, you'd also have some backup services running in
separate regions and everything where maybe your secondary users all of those are working on, okay.
Then ECR, so as discussed, ECR is kind of a container registry where it kind of has a repository

### [53:03]

which stores the Docker images and these images are tagged with a label. It's like what current
version or what kind of, let's say, whenever a user pushes. So what version of the commit it, so
kind of like an identifier, image identifier you can also see. So all of these things is what ECR is
mainly for and ECS is a container orchestrator. So inside the ECS, we have a main cluster and like
this cluster is an area where ECS runs the workloads and apart from the cluster, we have one service
called a task definition. So task definition is kind of a versioned blueprint. Sorry, it kind of
acts as a blueprint where all the, like as I mentioned, how the containers runs and everything gets
defined through the task definition. So a task definition technically sees which image to use to run
a particular service, which command to run, all the health checks to do, which ports to expose, how
many CPU would be used, if you're using Fargate or if you're using EC2 managed instances, everything
goes or all the setups gets happened by the task definition, okay. And after you define the task
definition and whenever the task definition runs, so we call it as a task. So a task is a kind of a
running copy of the blueprint. So whenever a service runs a sample number of tasks, so services like
the ECS's main controller, like maintaining, running task, if a task fails due to health check or
everything, restarting the task and everything happens where the service and cluster, as I
mentioned, is a kind of a whole combination that controls the workflow. Fargate, as I said, is a
compute layer on top of ECS.

### [55:05]

EC2 managed service instances are also in similar compute layer. Fargate is a serverless service. So
all the non-GPU workloads can be handled by Fargate for GPU workloads will more probably focus onto
EC2 managed instances, okay. So apart from that, Secrets Managers is where we can store the OpenAI
keys and all the other secrets. CloudWatch is for storing the logs and everything. Here you can
define how many days you want to store the logs for, maybe seven days a month, permanent storage and
everything. And also there are a few things like VPC and everything. So VPC is also something like
Virtual Private Cloud where it poses an isolated network. So all these things like when we discuss
something like data residency that our data should not leave from our particular region and
everything. So for that, this kind of VPC services are all defined. So this is like network level
rules, like your project security and all would be defined here. DevOps teams will be the one
defining all of those things, VPC and everything, how many subnets, how many zones to define what
zone, like zone technically meaning the inside a zone, there will be regions. So this region level
services and everything running inside all of this VPC level settings will be defined. And then
there will also be security groups, security groups defining what IPs have the access to this
particular services. So if it is an internal service only request coming from the internal IPs would
be accepted. If it is on public networks, all the user requests will be accepted. So all of these
things of respect to networking, like all the firewall definitions and everything would be done by
the security groups. Okay, so that is how like the basics of AWS services that you should know.
Okay, now the current AWS development architecture

### [57:08]

that would have is the build path. We already like saw partially till the Docker build. Next step
which we'll take is we'll push this Docker to the AWS ECR onto the AWS side of it, like how the
overall whole flow would work is. I have more better flow. This is how full architecture works. So
for example, let's say like I opened a Docker Streamlit UI onto port 8.5.0.1, like acting as a user
browser, the user sends in the request. This gets sent to this front end container. Now user browser
does not have access to this FastAPI API. This backend container access is only given to the
Streamlit UI. So Streamlit calls this the FastAPI API through an internet gateway because like there
are certain cases as well where you can also block this internal gateway

### [59:38]

along with certain minimal AWS permissions as well, whatever container generates as output logs that
would be stored inside the CloudWatch logs. So this is how the whole of our deployment architecture
looks like. Great. All right. Okay, now we'll move to the full final deployment of our setup. Okay,
so aws.amazon.com. This is the particular URL that you would need to do a visit. And the first thing
you would need to do, let's see, if you do not have an AWS account, you would need to create an AWS
account. You can kind of go here, create an account. It will ask for basic things, the Google
account or whatever organization account you want to connect it with. Then it will kind of verify
your email addresses and everything. And then it will particularly ask you to connect your credit
card for payment level information or something. So without that, usually, like you won't be able to
start working on the account, so a credit card would be a necessity. Once you connect that, your
account will be created. So then you can go ahead, connect to the account. So I'm just going to
connect through my main root account. Okay, and after once you have a setup and everything is
running, usually after a couple of days, they would ask for an authenticated app connection to be
made for security purposes. So the authentication part is also, you would need to be complete to
continue having the access. Okay, so once you log in and everything happens perfectly, this is how
your AWS basic console setup would look like. Okay, so you would have all of these things like the
left panel.

### [1:01:43]

When you click all services, it will show all the AWS services, different services are there. So
let's say they list the compute part, like you can see EC2, Lambda, everything, then containers.
This is ECS, Elastic Container Service, Elastic Container Registry, that is the ECR. Okay, so
they're all defining different services by whatever they're kind of categorized. They have
categorized all the services. We will just click here, go back to the main dashboard of the console,
so lists out all the services we have recently used and everything. Then the main things to look out
for is, one is this, your account number, your account ID. So we would connect our terminal like
through the terminal, we'll be connecting with our AWS account, and we should be able to confirm
that this account ID is same. Then a few of the things that you would check is like, if you're a
first time user, this billing and cost management, please take a look out like, no, this will going
to show you what is the total month's forecast or how much amount of cost that is going to be used.
Okay, so here once you have all the active services, it is also going to list you down what services
has used what amount of credits, like in terms of cost, in terms of USD. So if you have any running
services or anything, it is going to show you out here so you can look out the service if you have
forgot to close the service, please go and close the service so any unnecessary cost won't be
generated. So like if you're going to perform today's session hands on, I would suggest you try to
do it in a single session, like you quickly complete everything out in one hour and close or delete
all the services that you've created. So any unnecessary cost over at least a dollar would want to
be incorporated for your case.

### [1:03:46]

But otherwise, if you start it, you stop it for a few hours. If any service has stored anything or
kept it still there, you'd be charged for those services. Okay, so that could be one case. Now the
region where I was mentioning, so here let's say when you go here global, you will see here multiple
regions and everything are there. So that is where you would be able to select Asia, Pacific,
Hyderabad, Mumbai, other two basic regions. We have AP South and AP South too. So similarly, you
would have different regions. As I mentioned, whatever your target user group is based on that,
you'd be able to select this region. Now I have already selected the AP South and Mumbai region.
Now, once your AWS basic login setup is done, you are able to log in, you can see this console.
Inside our code base, there would be this one folder, docs folder, which would have this MD file,
AWS console deployment guide. Now, I have added all the instructions, functions, everything inside
this single file, because there is a lot of different things that we need to configure. So it was
better that I added it up all there. So you can just follow out this single MD file as well. Like if
you want to do, if you do not want to go back to the recording, that can also be done, like just go
through this MD file, and you would be able to make a total deployment in a single go. And apart
from this, I also have this one file. I will just split this out. Let's kill this. Okay. Great.
Great.

### [1:05:46]

So we have gone all through basics, all the basics, service level information, everything,
terminologies, which I talked about. Everything is explained up here with a few more AWS basics are
also mentioned here. So you can read it out, anyone having any queries about cloud computing and
all. So basic information on cloud computing, everything is also explained here, more details on
regions, availability zone, everything is mentioned. So you can read it to get more information on
cloud level setups. So let's start with the main code part now. There will be step one. Yeah, okay,
right. We got to the step one. So open the AWS console and choose a region. So like we already
selected AP South one, right? So let's just have it. So like this is a step one, log into the
console. Second is connecting your terminal to the same AWS account. Now there are two ways of
logging in. One is we can just make a simple logging like this. But before that, we need to install
an AWS CLI. Okay, so you can visit this link, AWS CLI. Here, based on your OS, you can simply go
Windows. Just make sure you can click on this MSI installer. I have installed this MSI like any
normal application that we install with Windows. I have installed it and to verify if it is
installed perfectly, you can do AWS version. Yeah, it shows current AWS CLI version 2.36. I'm just
confirming the AWS is currently installed. Sorry, right, yeah. So like once we confirm AWS CLI is
properly installed, Docker is also something you should confirm that Docker is installed.

### [1:07:48]

So my current Docker version is 28. The Docker container services and everything is running, right?
So next thing, sorry, what I'm going to do is I'm going to log it now there are two ways one is we
can just simply do AWS login like this AWS login region, AP South one. So what it's going to do is
it is going to open me this link. I can just select the user and it will show your credentials have
been shared successfully meaning it has been connected to a container. Sorry, it has been connected
to a terminal. So this is one with logging in other way. Other way is that through which like let's
say, there was a main root account, like I have a root account. And let's say I'm going to this
service. So we can also search for services like this IAM. So IAM identity and access management. So
let's say maybe whoever project manager team lead is there, they would be the one having the access
to root accounts. What they will do is they will kind of create IAM users. Okay, so let's say I'm
going to just click here, create user. Let's say user, dev user, next. I'm just going to click next,
create user. Let's say we have created a user like this, dev user. And through it, onto the security
credentials, you will see an option like access keys. So these access keys are keys through which
and user can connect to AWS account via the AWS CLI. So it will have something like two things,
access key and a secret access key. So how it happens is we need to run this AWS configure command.
So it will ask for this access key, secret access key, default region, default region output, and
through this, it creates a login to a particular user. So as I mentioned,

### [1:09:49]

so like it's a root user gives you an access key, secret access key, you need to do AWS configure to
connect to the account. Otherwise, if you are the one with the root account, simply do AWS login and
it will connect to a root account. So that is how two ways to log into your particular correct AWS
service that you should be able to perform, right? Next is once you have properly logged in, just
run this AWS STS get caller identity, just to confirm the current account ID. So you can see this
particular 3975, last is 2958 should match with my particular user account. You can see 2958
matches, meaning I'm logged into my correct account with the terminal, okay? Then the next step
would be to create the Amazon ECR repository, okay? So what we're going to do is enter the AWS
search console bar, enter ECR. So I'm just going to go to my search console bar. We'll search for
ECR, open elastic contain registry. Then inside, once we are inside the ECR, we need to create a
repository. Inside the repository, we'll name the repositories, OpenAI LLM app, okay? So onto the
right side, private repository, click on repositories. Here, if no repositories are found, click on
create repository, give the name, OpenAI LLM app, you can see I've given the name. And I guess here
there would be no other options to do. Yeah, keep the remaining settings at default, choose create
repository. And then when the repository is created, the main thing we need to copy is the
repository's URI, okay? So this URI would be kind of this particular format. There will be a number
dot ECR, the region, amazon.com slash whatever name you have given to this particular ECR
repository. So kind of this URI, like as we know,

### [1:11:50]

it's kind of an identifier, what exact repository we have given, right? So let's just create it,
right? So this particular URI is what I'm going to copy and I'm going to paste it inside it here.
ECR URI, step three, okay? Then now what we just did is we set up the ECR repository. So inside this
repository only, any Docker image that we push from our terminal will be stored inside this
particular repository. So if I click here, you can see images, no active images. So what we're going
to do is we are going to push our first image to here. So now next part would be instead of going
through our command, like the CMD, we are going to go through the PowerShell. So if you're onto VS
Code, click on PowerShell because PowerShell will allow us to store basic variables, okay? So I'm
going to set up this, like when I run this, what it does is that it is inside the PowerShell, it is
going to register the variable AWS region equal to AP South one. I will just enter it. The AWS
account ID, you can see, we are adding up a command here. So what it will do, it will run this
command, whatever my account ID number is, it will store with the key value pairs, the key value
pair, like AWS account ID, my, whatever account ID is there, it will store with that particular key.
Then ECR registry. So here you can see like why we went for PowerShell is let's say if you're with
command prompt, what you had needed to do is you had needed to write out this full values into the
command, like whatever the account ID, whatever the region is. So over the multiple commands that we
build, instead of adding all of those values again and again,

### [1:13:52]

so like you can also do it like kind of, you can also maintain a TXT file, write down all the
commands, but that would be usually too hard to maintain. So go to PowerShell, write this. So
whatever ECR registry name is there, so what it will do is it will create this same, the ECR URI, it
is going to create here. So all of the three basic key value pairs are there, AWS region, account
ID, and ECR registry name. Next, what we are going to do is using this command, AWS ECR will connect
to the region and inside that, it will do Docker login, username, and AWS part also. This is like
ECR's basic input setup where it will, inside the registry, it is going to make a Docker login. So
when we run this, it will take a couple of seconds, it will show login succeeded. Login succeeded
meaning Docker and ECR is connected, like with whatever account you have, it would be connected. And
when we do this command particularly, right, Docker build what platform we want to build for, the
Linux image it is, and we're also tagging it with the image URI. So why the image URI is because you
can say it's like that, let's say when we add a tag, you can also tag like versions and all
everything. So the tag would be useful in those cases. So let's say for example, we're going to do
Docker build. You can see it has started the Docker build and the Docker build will create an image
up here, like whatever, yeah. So you can see it has given the name this particular because this
image URI is what it is equal to,

### [1:15:53]

like here, you know, right, ECR registry slash OpenAI LLM app. So your ECR registry URI slash the
OpenAI LLM app latest, so this is what the Docker will tag the image to. Now here, the latest
versions and everything could be managed. And here you'll also be able to see if I'm going to
refresh it. Okay, maybe it is the same build that I did. So it does not look kind of shows. Not in
here, fine, that's fine. So whenever you're going to create it for the first time inside your Docker
hub, you would get a local image like this with your image URI. And at the end, it will be this
OpenAI LLM app latest. So any kind of a new Docker build you do, this same image will keep getting
updated. And then when we run this command, Docker push image URI, what it will do is Docker is
going to push this to our ECR service because we connected our Docker to AWS ECR. So when we ran
this, so you all saw that, it showed login succeeded, meaning our Docker was connected to ECR. So
whenever we are executing this particular commands, Docker push, Docker build and anything, it is
kind of building it for the ECR. So whenever we did Docker push, I would like once this particular
command completes, we'll be able to see inside our, yeah. So we'll go to here, and if I refresh it,
so you can see here, image tags latest, my Docker image was successfully pushed to my ECR. Now,
ECR's role end here, like whenever you would be having new Docker image, you push it to your Amazon
ECR, and that is the only role of Amazon ECR here, just to store the image for the ECS,

### [1:18:01]

either with Fargate or EC2 Managed Instance Service to run, so all the main part of ECR here is only
to store the Docker image, okay. Next, we're going to store our OpenAI API key into AWS Secrets
Manager. So what we're going to do is go to Secrets Manager, onto Secrets Manager, I already have
added a key, OpenAI API key, like we can also create a new key. So to create a new key, click here,
store a new secret. Here, the secret type would be other type, like API key and everything. Here,
what you do is you add your values, like let's say, for example, OpenAI API key, okay, or whatever
your API key value is there, right, the SK values and everything, so that is what is supposed to be
set up here, the SK, the full API key, inside your plain text is where you will put it, and once you
put your actual API key, click Next, I will change the name, okay, name, huh, and the secret name,
maybe I'll just, I'll put OpenAI test, and all the things, all the values, others are default, so
you can just leave it as default values. You can also maybe, you know, add a tag to it, like if
you're using this key for multiple services or something, you can also add a tag, but right now,
it's not necessary. Just click on Next, and this all values also, you can put it as default. Just
click next and one more thing I guess I should mention. So there is this automatic rotation setup is
also there. So this is kind of a setup to protect against API keys and everything.

### [1:20:01]

There is this automatic rotation where you kind of have new API keys will be created via some Lambda
function or something. So there is this Lambda rotation function. So idea is there after every few
hours. So you can also select no hours 23 hours. What is the time and at the time there will be an
AWS Lambda function that will run will create new API key fetch that API and will store it for this
particular secret key. So that is how no kind of to protect against like you do not have single API
key stored for longer time. Also, this is a kind of no rotation services are also the Secrets
Manager and then finally when everything is set up just scroll down create store. So what it will do
is it is going to create the secret name. So I already the original secret is already stored inside
this open a LLM app open a API key with this here. So once it is stored it is never going to kind of
show the secret by default under the screen someone would need to click this retrieve secret value
make sure your correct account ID and everything is there and let's say instead of the root user
instead of the root user it has some I am user account is given and it does not have access to read
the secrets values and all they would not be able to retrieve the secret value while the root user
usually have all the excesses. So they might still be able to retrieve the values and everything out
correctly. Okay, so now our secrets is set up next would be to create the easiest task execution
role. Okay, so we need to go to I am it to click on this roles. So roles is something you can think
like now whenever an account has an added role that role allows you to kind of have access

### [1:22:04]

to any service or something. So let's say I guess I would already have one role for it. Okay, I do
not have role. Okay, fine. So I will just click on create role. The next step would be to select AWS
services any service that we would like to select here. So from here you can search for elastic
elastic container service like we're creating it for ECS and inside this we're going to select is
for easy elastic container service task. Okay, so what it will allow us like as a main root user of
this account it will allow ECS task to call other AWS services meaning fetching service from AWS ECR
or from secrets managers fetching that AWS secrets whenever we have this role running. This is what
like this will allow like the ECS task to do so that is why this roles are necessary through which
we kind of add functions through which we can add permissions roles to a particular account. So now
ECS task is give done next and then I'm also going to add this thing inline policy later on but task
execution role policy. Yeah, so this is another role policy that needs to be add. So what it gives
access to is it gives access to all the ECR level things like get download URL for layer batch get
image. So kind of this role will also allow to download and send the ECR image. So ECS level
permissions are given. This is how we are giving the ECR level information for the ECS to run the
task through ECR will select next role name

### [1:24:07]

needs to be given. So role name is OpenAI LLM ECS task execution role will just create the role now
apart from this basic things and setup is there there is also inline policy setup is also available
through which like when I clicked on here not here when I clicked here you can see this kind of a
JSON version, right? So add permissions if I go here click create inline policy. This is I'm just
showing as an example. This is an editor this kind of inline policies can also be added now here.
Okay, I guess I will need to open another now here what I'm giving here is is a secrets manager
resource ARN. So from secrets manager like we configured ECS ECR permissions. We also need to
configure secrets manager permission. So for secrets manager to get the secret value now usually all
of this information like now if you're thinking that how did I get all of this information and all
everything is there with the AWS documentation everything you can just simply go search for secrets
manager inline policy role for the AWS user this will list out all the you know, this kind of
different actions and everything if you are not still sure you can make use of any GPT cloud. They
will list out all the perfect policies all the information out out there as well. They can also do
it now here this thing particular action secrets manager get value it requires one resource level
information that is what particular secret that I have stored which particular secrets I need to do
so just go to my secrets manager. I will select the particular secret that I want to read

### [1:26:07]

the value from and you said that there will be a secret ARN. I'm just going to copy it. I'm going to
paste it here and I'm just going to click next create policy policy name is invalid. Okay, policy
name. I will name it as read open a API key create policy, right? So this policy is also created as
you can see your main role the inside I am open AI LLM ECS task execution role the basic ECS level
permissions and the read open a key permission both are added. Okay, so this is how like, you know,
if multiple services some database services are involved some easy to services are involved. This is
how you can attach more policies policies allows you to add permissions around services. Now there
could be also something like creating server service deleting server service. So instead of deleting
server service, if you want to just allow only or you can think it from a perspective usually there
are read write accesses to anything if you only want to add read accesses to anything you can only
add read access if you only want to add write service access. So let's say for example, add
permission attach policies. So here you can see that there will be n number of policies. You can
find in 61 pages of around 1200 services are there. So this administrator access is the most famous
one that allows you to do all the things all the things across the full AWS account it can do like
kind of use administrator access to the full account. So this is usually kind of you can get AWS
roles give roles to other users and through that roles only the other users will have limited access
to perform actions inside this AWS account.

### [1:28:07]

So let's see if I search for something like easy to okay, so you can see easy to sorry easy to full
access easy to power user read only user. So this is kind of different kind of accesses. You can
also control for the permissions of a user next would be to configure CloudWatch. Okay, so we'll go
to CloudWatch log groups and will create a log group named ECS slash open a LLM app. Okay,
CloudWatch logs log management create log group log group with name ECS open a LLM app then I guess
no other configurations is required. Yes. Okay retention retention is something like you can set it
up here like how many days you want to retain let's I'm just going to select three days. So all the
logs will only be stored for three days after that they will be automatically discarded from the log
group. All right, fine. Perfect. Now just create so this will set up our CloudWatch logs. So all
those ECS level tasks that will run will generate the logs everything will get stored inside the
CloudWatch logs next would be to create a security group. So security group is something like.
giving access to inbound rules, meaning maybe we'll better do it, so we'll go to EC2. Inside EC2 as
a service, there will be a different setup here onto the left-hand pane, Network and Security, where
you will see this security group, we'll create on security groups. Click Create New Security Group,

### [1:30:08]

OpenAI LLM Demo, I'm going to name it. Description is Stimulate Demo from my IP. Any description for
your service that you want to maintain, you can just paste it up here, Stimulate Demo. A basic VPC
by default, whatever VPC is created for your account, any account can never run without a VPC, a
basic VPC will always be added. So that basic VPC default you would need to select. Then the main
thing is we need to define the inbound rules. Inbound rules, add a rule. You see P Port Range 8501
through which any input user, like let's say any external user from internet is sending requests to
the streamlit URL. So when they hit the URL 8501, do you want to block it? So let's say if you
select 0.0.0, that will allow all the IPs in the world to have access to your streamlit application.
but if you don't want to do it, you can also select my IP and whatever your current IP would be
there, it would get configured for that only. So only I would be able to use these streamlit
applications. I'm just for my security purposes, I'm just going to select my IP because I'm just
doing it for experimentation purpose. Now that is done. Now, please note that we are not adding any
inbound rule for our API endpoint because we do not want any external user from the internet to
access my backend API endpoint like they can make free input API calls to my backend API. So no
inbound rule will be added for port 8,000 where my FastAPI service will be running. As streamlit and
FastAPI are running inside the same Docker Compose setup, the streamlit will be able to call

### [1:32:09]

FastAPI through the internal local host call inside the same Fargate task. So that is how streamlit
and FastAPI will be connected. No extra setup would be required. Whenever we start the Fargate
setup, they will be able to connect and streamlit will be able to call the FastAPI service
correctly. Now, once the setup is done, just create security group. So inbound rule for a user to
call the streamlit service is created. Next is would be to create the ECS levels things. So we're
also going to first create a ECS service linked role. So we'll again go to IAM. We're just checking
if this particular role exists, AWS service role for ECS. This is a by default role, so it is
already existing. If it does not exist for your account, what you would need to do is, if it does
not exist, you need to create a role, choose the AWS service. You can just follow out the steps,
search for this AWS service role. Let me just show you. This is how you would be able to add this
AWS service role for EC2. So if you do not have an by default value added, please make sure you
create a custom role, but otherwise mostly usually all the AWS accounts would have this particular
role already active, AWS service role for ECS. Once this is done, what we would need to do is,

### [1:34:09]

and also this thing can also be created from the terminal. If you do not want to go through the
steps, you can also directly just copy, paste this command, paste it in your terminal, and that
particular role would also be created into your account. Both the ways are fine. Then the next thing
you would need to do, what would have happened if this role is not added? So if your account do not
have role for ECS, what would happen is when I go and create a cluster in ECS, it will not allow me
to create a cluster. So if you do not have a role, this particular ECS role is active, it will not
allow you to create a cluster. So this role is required for you to properly create or use the ECS
service properly. Okay. So I will go to ECS, go to cluster, create a new cluster. So this cluster,
as we discussed, handles all the workloads. So I'm just going to name cluster, OpenAI, LLMCluster.
Here you would see Fargate only, managed instances and everything are mentioned here. So let's say
I'm just selecting Fargate only, in that case, it is going to go for serverless setup, no extra
information it is going to ask. Let's say if I go for this managed instances and everything. So
here, it is not going to ask me what EC2 instance type I want to do. So here, the GPU level
information and everything, you would be able to select. So here, whatever particular EC2 GPU type
is there, if I can, yeah, you can see four GPUs. So for GPU level cases, you would be able to select
this, self-managed instances, but as it is a serverless, we do not need GPU, just select this
Fargate only setup

### [1:36:09]

and keep all the things as default, click on create. So this basic ECS cluster has been created.
Next would be to go to the task definitions, right? Now, inside the task definition, we'll create a
new task definition. So as I mentioned, this task definition acts as a blueprint. So this blueprint
will define what container level information and everything we need to do. So this blueprint is
active. Now here, I've added all of the values here in the form. So like task family name, open a
LLM app. Next is launch type, that would be AWS Fargate because we have selected Fargate, right?
Then this is with respect to infrastructure inputs, the basic one, so how many CPUs I require for
the Fargate service, how many memory I want to use. So if it is very small, you can just select more
smaller value. If you had something like more complex code and everything, or you want to scale it
up, usually a bigger machine, 4 GB RAM, 8 GB RAM would be selected. That's the usual value, right?
I'm selecting just a basic default value, one CPU and 3 GB. Next would be operating system. Linux is
already selected by default. Everything is fine. Okay, I guess, okay, maybe more. Okay, we'll select
more lesser resources because like this, hello, let me re-share.

### [1:38:37]

I guess I lost my network in between. Yeah, I hope my screen would be visible. Please mention in the
chat. All right, thank you, right. Right, so yeah, we were just configuring this CPU values. So we
just put 0.5 CPUs or 0.5 CPUs, something like shared CPU instances where maybe from the backend, the
same CPU would be utilized by two separate users or something. So if you select and go for this
higher value, so that would be dedicated CPU would be alerted. If you go for this 0.5, 0.25 sub
values, that would be like shared CPU services would be allocated for maybe multiple AWS users or
something. But that is how the shared service works. Next would be like setting up the values for
this containers. So we would add two containers. First will be the FastAPI container, we would name
API. So we're just going to name it as API. The image URI would be the one where we'll select the
repository. So inside your ECR service, it will allow you to select any ECR image. So I'm going to
select this repository, the latest image, select image. Essential container, yes, meaning this
container is essential, like this container should run perfectly, that is, we are trying to indicate
with essential container, yes. Port, need to mention 8,000, protocol TCP, HTTP, everything
mentioned, and under environment variable, add environment variable. So these are any kind of
environment variables

### [1:40:40]

that you might have added or created in your code. So let's say you have this kind of values, or
more environment variables your oral system would be using. So whatever environment variables for a
particular service or a particular backend or front-end service that you have allocated to, you can
add it via this particular setup here. So this will pass in this variables to the container with
hover.env file and setup works. Okay. Here it's setup nine, maybe, yeah, fast API container, then
next would be log level, add the value info, openEIModel, next would be, and one more secret
environment, right. Now, this openAAPI key, the secret where we are going to add is, for this, the
value would be the one equals to the ARN of the secrets manager service. Okay. So what we're going
to do is, we'll go to secrets manager, secrets manager, openAAPI key, we'll copy the ARN. Here's the
ARN, here is also same.

### [1:42:40]

Yeah. Paste this ARN here. So what it will notify it to the EC is that, this particular key should
be fetched from the, and select value from, so this particular value should be fetched from the
secrets manager. So that is how you can define key value pair, and if any value to be fetched from
secrets manager or any other different AWS service, you can set up it like this from using value
from. Next. Yeah. And also you can also, for the container set up things like, health check or
something. So let's say, command functions like this, like command shell functions. So what we will
do is, whatever container is running, it is going to check inside that container, if this particular
fast API input is running perfectly fine. So you can also set up things like interval, checks at
every 30 seconds interval, timeout, five seconds, retries and everything. So this is all the
different services. I'm not going to add it up here. Like this is more valuable when you have to
keep consistently checking the health of the container. Like if you're, if you know that your
container might be down or something happens. So usually for those cases, this container health
checks is maintained. Usually happens every time in the production. So that is also something you
need to mention. And inside the log collection, use log collection, you need to select Amazon
CloudWatch. The main AWS logs group would be pointing to ECS OpenA LLM app. Meaning for this
particular fast API container, we'll store the logs inside this particular CloudWatch log group. So
that is how we define and region, whatever stream it is coming for.

### [1:44:40]

So the stream prefix, I will put API meaning this logs are coming through the API container service.
So that is what it defines, the stream prefix, right? Next we'll set up the stream with container in
a similar format. So add container, container two, front end, essential container years. Select the
same image, container port 8501, 8501. Okay, and inside Docker configuration. Yeah, you can also
define an entry point like this for any container that you want to run. So if any entry point that
you want to pass to the container, you can also define it like this. So what it will do is it will
run the container with this particular command, stream it run, go inside this front end folder,
stream app.py at this particular port host and this kind of a services. And to add any sort of a
health checks, like as I mentioned, so let's say we are just going to put the health check for our
front end. So what is simply doing is it is just calling the 8501 port to check if the particular
service is running perfectly fine or not. So I'm just going to add this particular service. I'm not
going to add any interval or something, like I don't want to have it keep continuously checking it
every 30 seconds or something.

### [1:46:41]

So it will just check it at the start of the container once the health check is confirmed. Okay, or
maybe let me just put 30 seconds. That's not an issue. Time out five, start period also 30 seconds.
Retries, retries meaning whenever the service is not called properly, how many times to retry
calling the health check command before considering the container is unhealthy. So that is also
something like once this container is shown unhealthily, what ECS will do is, ECS will stop this
container, it will restart the new container. So that is how ECS orchestration will also work based
on these health checks and everything. It configures all of those different things. And a few more
environment variables to this. ECURL, demo, use log collection coming from front end. Right, and now
we'll just create this out. So what we did here is we defined the task definition and everything,
defined the values, ports, health checks, logging connected to CloudWatch, connected to ECR, like
where to pull the image from. Everything is defined inside this particular task definition. Once
this is defined, when I go here, click on this task definition, and when I click on here, you would
notice task definition and revision number. So this revision number shows the number of times I have
edited or created a new version of it. So as I use this, a couple of days back,

### [1:48:42]

it started with revision one, but I edited it a couple of times, so it is now showing revision four.
If I go back and let's say, I go to this particular health check for this. Okay, we'll take this as
a new revision later after we run these service ones, okay. Next thing, what we'll need to do is
we'll need to go to this clusters. Open your LLM cluster. Inside our services tab, we'll need to
click create. Now here, open LLM app, task definition, revision. What revision do you want to
select? So I'm just selecting four. Capacity provider already know this Fargate is selected. Sorry,
launch type, launch type Fargate is selected. Anything else we might need to change here? I do not
think service name, huh. service name will just change, OpenAI LLM service. These are tasks, so like
number of tasks to launch. So as we only have one single task definition, it is only going to be one
task that is executed. So only one task, we're going to launch it up here, and I get this should do
right. Yes, that is fine. Rolling update, that is already there. Expand the networking tab. Let's
check it out here if the basic VPC is connected, and inside this VPC, a few of the subnets are
selected. So inside this basic subnet, sorry, the basic VPC, whatever subnets are given to you, just
select them. Like because VPC, like this setup requires subnetworks

### [1:50:44]

to be used, so kind of selects AP South, regions and everything. Once this is done, I believe
security group, yes, and security group, yeah, security group, OpenAI LLM demo. So this is just, we
have added it because this will mean that to this particular Fargate service, only from my IP, the
request will be coming. So that is why we created the security group, and we're adding this security
group to this particular cluster definition. So whenever the Fargate service or the task gets
running from the task definition blueprint, it will only be accepting inputs from my IP. So that is
how we created the security group for, and we're adding a security group here along with the Fargate
launch tab, okay. I guess this turn public IP on, public IP is turned on. All of these things are
fine, and we're just going to click on choose create. Now, once you do it, it will show this OpenAI
service deployment is in progress. It will take a couple of minutes, okay. So, okay, I guess service
is running. Here, health, task, and everything, it will show. So here you can see it is showing one
task is running, provisioning, and two containers are running for the task, front-end and AP, as
we've already defined in the task definition, right.

### [1:52:47]

Let's just wait till it confirm. Here in the sequence manager, identity is all you see. Let me just
go back, that's the definition.

### [1:55:06]

Okay, I guess we made a mistake up here. So you can see here, like we created the task execution
role, but here we needed to select a different one. This, the one we created, OpenAI, LLM, ECS, task
execution role, because inside this only, you remember, we added that particular secrets manager
reading role, right. So I just added up this role because incorrect role was selected, and I will
just create it with this so it would have correct permissions to read from the, oh, let's see, if it
is okay, it has started a new deployment. Let's just wait for a new deployment. Yeah, and okay,
after service, like now the task definition we updated, we'd also need to update this service that
we did. So just update it, select the latest revision that we created for the task definition, and
then we're just going to update it. So it is going to fetch the latest task definition. So you can
see deployment, we just started a new deployment,

### [1:57:20]

pending, right. So you can see the particular service is now running, and to actually run this, you
would have this public IP value here for this task, 8.5.0.1. So Fargate service setup is also
completed. Once everything cloud watch and everything is connected, we would just check for this
public IP where it is not opening at the port. It is also healthy. Is my IP incorrect or what? Okay,
okay, I got it. Now I switched the network in between the session correct.

### [1:59:22]

So what I will do is I will go to my security group. So this kind of issues can arise, right,
because my network, I changed it. I'll go to EC2, I'll go to security group. I'll search for OpenEI
LLM Demo 1. I'll edit the inbound rules. Let's say instead of, I'll just put it custom. You can see
I edited the inbound rules and I was able to access the account. Now we're just going to test it
out, order is delayed. Here you would see that though I'm able to access the streamlet, I might
never be able to access the FAST API endpoint because FAST API, we did not give it the access for
anyone to, like from the container, no one would be able to call upon that particular container or
the container is not out in the public. But we did allow through the security group for anyone to
access the streamlet port, so we are able to access the streamlet port. That is how you can see like
streamlet still works because streamlet and FAST API both are working inside the same Docker
container inside the Fargate task and through the internal settings, the streamlet is calling the
local host of the FAST API. That is how streamlet is connected to the FAST API. That is how we have
created it and connected. For example, let's say you had two different Fargate tasks, both are in a
different services. Maybe it would be more like whatever IP

### [2:01:24]

or whatever service the stream running on through the security group, you can control the inbound
rule for the FAST API service that is maybe running in different Fargate tasks, where through the
inbound rules or either via some maybe authentication or something, you can approve whether it can
accept or not, so that is a kind of architecture decision you can make. That is how we just
completed the full deployment, like we just did a full deployment from local to the AWS ECR plus ECS
Fargate setup and once everything is done, so let's say I already showed it, let's say if I want to
make any changes to the task definition, let's say if I make any change, maybe I add one more
container, I made any change to any container level settings, then once I make that container level
settings change, I go to cluster, I go to service, I need to update the service change to the latest
task definition and then just update it so the latest, any change in the blueprint would be
executed, everything would happen correctly and the new task containers and everything would be
created. Okay, that is how the overall setup would work. And here also you can see inside the task
as we added the health check for the front-end container, it is showing healthy because it is
continuously running that health check command to give us the health status of this container.
Similarly, if we add for API as well, it will also give us the health status of the API container as
well, right? Now, once you have built this everything all in all together, the next thing would be,
like also for anything, as I mentioned, any changes you do, this will be the steps that we need to
perform. Select ECS cluster, select the services tab,

### [2:03:26]

force any new deployment, update the service task, so new deployment will be created and then you
can again re-access your latest changes through the public IP. If any changes are made and any new
deployment is created, the public IP will change, so you would need to copy paste the new public IP
and access the port 8501. So that will be a little change. And apart from these things, once you
have completed all of these things, at the very end of this file, I have added the guide of what
things you would need to delete. Okay, so yeah, clean up after the demo. So here in this case, all
of these things you need to do, let's say ECS, what you will do is go to ECS, update OpenALM service
to zero desired tasks. So let's say if I go to service, I update the service, I select task equal to
zero and just click on update. So it will take certain time. So once the service is completed, we'll
just select delete service, delete. So you can see that service is deleted. So that is how just
perform all the steps to delete all the services so you do not get incurred with any other
extrajudices, right? Okay, so now this was the overall AWS demo walkthrough. Now a few of the more
slides are added here, like this is all with respect to information on VPC, operational quality,

### [2:05:27]

and what if we change our service via the, I would say, sorry. What if we replace our setup with an
open weight model instead of this open AI setup, like now we use the Fargate. So as I was
mentioning, what things usually would not change is that the stream lead fast API structure and
everything will be the same, the logging, cloud watch, evaluation, everything would be the same. The
only difference would be that instead of the Fargate service, we'll start seeing or looking at
further will be a self-managed server. So now in terms of Fargate, we do move to easy to manage
services, but in that as well, we maybe, we would have something like OLAMA or a service like VLLM
installed. So VLLM, like there is a separate document on it available as well. So VLLM is kind of a
service through which it acts as a GPU accelerator. It has something services like KV caching
mechanism and everything through which they accelerate a particular model. So it is kind of OLAMA,
but more focused on to scaling the throughput. So whenever you are having or in a particular case
where you identify the basic model or via the OLAMA service, you're not able to scale furthermore,
start looking into direction into services like tools like VLLM through which in general,
acceleration of the models can be achieved. So that is a few of the things I've added right here
into the presentation. So you can read out more onto the things like OLAMA and VLLM document are
already there. So I believe you would all would have gone through it to understand the basics of it.
And one more things like more topics to learn next. Once you understand this ECR, ECS,

### [2:07:28]

Fargate services and everything, more things to learn to make your cloud basics more cleared up
around VPC, load balancer, auto scaling groups, routing rules, GitHub level, CICD. So this will all
would make you a more often full end to end complete setup. Like once you add GitHub actions, auto
scaling and everything, like this is all about like auto scaling and everything about when you have
more users coming to your application, how to reach the desired task counts to serve the proper
users properly without any reduction in the inference time or something. And GitHub actions in terms
of the CICD workflow setup. So whenever a new code is pushed, the AWS console, like right now what
we did was we created all the things manually on the AWS console, but GitHub actions and all this
kind of services are more around that whenever we make a new push, they by default control actions
like this, make a new push to the ECR, deploy a new task revision and automatically update the ECS
cluster service. So GitHub actions is kind of automating all the things that we did manually. So
these are the things I would suggest you take on as the next step of learning because if you're
going to move towards a roll off around, maybe, let's say, LLM Ops developer or something, this
would be the topics that you would need to have hands on knowledge upon. So like these things also,
you can start looking into the direction of learning. And yes, that was it, majorly from the
session. So the session, we just understood things around the FastAPS Treeblu Docker. We saw a local
demo. Then we learned about a few of the AWS services, learned about ECR, ECS, Fargate, the
difference between the Fargate as a serverless component

### [2:09:29]

versus the easy to manage services. And then we went through a full demo on how to configure the
Secrets Manager, IAM roles. We also got to see if incorrect IAM role is there selected then how
the... Issues can occur with reading the secrets. Like if you are involved with multiple services,
you need to have permissions for all the services to perfectly run your ECS services and everything,
right? Then setting up all of these different settings in the ECS, like VPC settings, ports, task
definition, security groups, everything. I just mentioned you out all topics to learn next if you're
going to move more towards the direction of an LLMO ops, AI ops kind of a role. Lastly, open-source
models, just a minor small change from the architectural perspective. Instead of Fargate, you can
start looking into easy to manage the instances. ECS, ECR will stay there. The only change would be
there instead of Fargate, it would be an easy to manage services where GPU workloads can be handled.
To run those models, instead of the basic models you run through HuggingFace or something, maybe in
model acceleration service like OLAMA or VLM would be much more preferred to scale the service to
more number of users. All right. That was it. Majorly from the session, I will allow the microphones
now for everyone to ask any questions, if you want to ask, just give me a minute.

### [2:11:37]

I guess Ganesh has already added something. I wanted to float an idea. Could we package these steps
into a structured prompt so that an LLM executes most of the deployment workflow with a human-in-
the-loop checkpoint for approval? Right. I believe Cloud code is something that would help you out
with this. Like if you just list out the steps, the same MD file to it, it would be able to execute
all these steps manually. But instead of giving an LLM power to that, there are a few other services
like Terraform, that gives a developer automation power to it, or the GitHub Actions, which I also
mentioned. Like you can think as I push the code, GitHub Actions run, go there, update the setups,
update the AWS console level items, and there would be Terraform services as well. Whenever, let's
say you want to quickly create ECS and all the services, list out all that there, the Terraform
level automation like infrastructure as a code automation is also available. But yeah, I guess your
idea of using LLM can also be executed, like Cloud code is already doing that. For example, I have a
few setups where it can automatically fetch the latest code from my codebase, push it to my GitHub,
and also make a deployment onto Vercel. Same thing can also happen with AWS, I believe, but you
would only need to give it access to your AWS account login and everything, which is what you would
need to do. Now that comes as also as a risk to security portion, like how Cloud code is going to
use that console and all. So that is something that's account security things and everything would
be there into consideration, but if that particular role, IAM role and everything is maintained, I
believe Cloud code can still handle. All right, what you have also mentioned,

### [2:13:39]

happy to put together quick proof of concept if there's interest. If you would like to go ahead, if
you would try to build something around that, we'll all would be happy to see how you're going to
build that, and you can share it with us onto a WhatsApp group. We all would be happy to see, and
maybe in the next session, next session at the end of the session, you can discuss how you build
something like that. Anyone else has any queries? If there are no more queries in that case, just
stop the sharing and stop the recording as well. Ganesh, if you're speaking something I'm not able
to hear you properly. No Chirag, am I audible?

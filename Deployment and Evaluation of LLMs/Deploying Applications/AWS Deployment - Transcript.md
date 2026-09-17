# AWS Deployment — Video Transcript

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [AWS Deployment](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/62579850-aws-deployment)
> · Video lesson, 62 min (`1:02:12`).
>
> **How this was produced:** the lesson ships no captions or transcript, so the audio was
> transcribed locally with `faster-whisper` (`medium`, beam 5, VAD) on GPU. Audio was cut into
> silence-aligned chunks and timestamps re-based onto the full timeline.
>
> **Accuracy caveat:** machine-generated. Technical terms, package names, and proper nouns are
> the least reliable parts — verify anything you quote before building notes on it.

---

### [0:08]

So what we're going to see today is like we already had a fast API session two weeks back. We are
going to use the same setup, but instead we're going to use and deploy that particular setup onto an
AWS such that people can access that via a particular link. It won't be hosted on your local and
limited up to you, but multiple people can use that. So that is what we're trying to do. This is not
like a full DevOps level functionality where you will be attaching a domain and working on the
domain, but the basic setup of what a machine learning Gen A developer should know on how to deploy
something onto cloud like particularly selecting AWS for now, but the approach would be same on any
cloud platform made to be Azure, GCP or any other local cloud providers as well. So how many of you
are familiar with the AWS? I am not aware of it. Okay. Yes, I guess we have few people who know and
lot of people who don't. So technically AWS is a cloud platform or if people who know already, if
they want to share what it is, please share then I will add more points to it.

### [2:19]

It is a cloud provider. We can host applications in our cloud. So AWS is a cloud computing platform
and that is provided by AWS. So AWS, Amazon kind of like we the full name is and any cloud platform
be it AWS, Azure, Google cloud platform that is GCP. They offer multiple services like storage,
database, machine learning, general capability, security services to the hosted services you have
onto the clouds. Now some of the very key things with AWS like for any beginner would be to know
EC2. EC2 is elastic compute cloud on which we can run applications and those applications can be
served to different people via domain. Then one service is S3 where we can store the data like those
are kind of buckets where we can store our data such that any different AWS services can access
that. Then we have Lambda service. So Lambda is kind of a serverless compute where you don't need to
manage anything all the load balancing. So load balancing is something like, let's say you have
hundred users on your application. Your application can work fine. But what if thousand users come
together at a time if your application is not able to handle that load there would be a load balance
which will create replica of your sites and divert the users to multiple different parts of your
site.

### [4:23]

So the load can be balanced like we usually see like the government websites whenever there is a
college website results get published the site immediately gets hanged when lots of students start
seeing the results. Like this way we have different sets of services and then there is this one
service also Amazon Bedrock. We will see how that also works but not for now. For today we will only
focus on EC2. So what we are going to do is like when I will share you the whole code part you will
get this readme. So have given all the step-by-step things how you can deploy this fast API end
point and how you can use that or like you can use some other one to access that particular
endpoint. So one thing whenever you would log in to AWS the first thing like if you log in they
provide you with free credits for a year. So but those free credits are not for each service they're
limited and won't allow you to use high-end services. So if I consider EC2 they will let you use
very small level of services for free but not high-level services. You have to pay some money to
access those if you see my monthly cost comes up around $50 like that and here you can eventually
see like this is not like there's my organizational account. So from my account this kind of
services are getting used then coming to the part. Yeah, one more thing is would be like if you are
going to use your own personal account you might be required to add your own credit card or a valid
debit card

### [6:26]

valid debit card in the sense it will only accept a Visa or MasterCard debit cards not any other
rupee debit cards like that and if it is an organizational account then you would be provided with
that account and you can access that where you don't manage the billing part for you the billing
will always be shown as zero except that you go to the main billing page they will show you the
bills but you won't have the option to pay it like that way. So that is one part now when you log
into the account and add your credit card the first thing you need to do is search for EC2 like when
you first go you won't have anything here in the recently visited section. So you can simply click
here go and click easy to you'll get this easy to virtual servers in the cloud. So when you open it
you would see like a dashboard like this. Sorry. Yeah, you would have instance instance type launch
templates all many kind of like network security load balancers volumes like volumes are kind of
place where we store the data of the EC2 instances so not focusing on everything as of now what you
can simply do is click on instances like this running part 0 so you will see that there are no
instances found in actually I have a lot of instances here. Okay. Sorry one more thing when you have
this here, there would be the country specific mentioned. So please make sure you choose Hyderabad
or Mumbai

### [8:26]

because that will cost you less money compared to the US or European counterparts. So you will see I
have a lot of services running but if I just go back or if I just want to put like what are the
instances running you can get all other my services are stopped. So to start a new actual instance
what I can do is I will click on this launch instance button. This will take me to a place where I
can initiate a new EC2 instance. So once you go to the like once you click launch instances, what
you need to do is you need to add a name to the instance add necessary details or select necessary
details like what OS you want to choose what the disk size you want to choose it, right? So I will
just name it fast API test simplest OS to use would be Ubuntu instead of windows. So make sure you
get familiar with the Linux commands as well because they would be much more useful now here for
people who don't want to spend the like and they have created a new AWS account. They can continue
with t2.micro but those who are using any open source model, sorry those who are using any kind of
open source model or Large models they might not use t2 for them. We have different sets of like
G4dn this kind of Servers which provide certain GPUs 10p4. I guess is one more kind of a Instance
type which provides the GPUs. So for now as we are only operating on the opening API We don't
require such an GPU But I will still choose t2 medium

### [10:29]

and also yes, if you have a requirement you're working with an open source model and You have a
requirement for entry Nvidia drivers So in those cases what you can do is you can clear click that
browse more a mice a mice is like Machine images. So what you can do is you can marketplace a mice
and then What you can do is you can simply put GPU here So you will get the instances where the
Nvidia drivers are already pre-installed and You don't need to install The driver separately so you
can make use of this You'll just answer it because we don't need an GPU instance for now. So this is
how like you select a Ubuntu You can also even select Ubuntu specific version 22 20 anything. I will
just keep it to the latest version Then I chose t2 medium now one more important part is key pair So
with key pair this process would make it easier to connect Like let's say I have Amazon account. I
want someone other to log into the account They can make use of this key pair or let's say I want to
transfer files from my local to them This particular server can be done via SCP as well But if you
have something like win SCP or then that makes it much more easier So I already have one keeper
created So I will just select it Otherwise, if you don't have a keeper what you can do is you can
select create new key pair It will prompt you with this enter any key pair name select dot PPK and
create the key pair So what it will do is it will generate a file like this fast API test dot PPK

### [12:29]

Which you need to store it somewhere so it's somewhere safe then you will be Showing some network
settings. We want to be Experiment with anything for now and for storage They will allot 8 GB for By
default onto the Ubuntu servers. It depends like whenever you change the server type windows it will
Require some by default It requires some storage. So that particular storage space is already
captured So what you can do is you can increase 1 to 2 GB or based on the task we're going to do so
if we are going to like Install so many libraries install some model then in that case you need to
increase this size So I will just keep it as 12 for now just for a safe safer side and for people
who have a new account And are eligible for free tire they get they get 30 GB of this particular
storage access every month every month They can have a 30 GB of free storage for them so once all
this information are filled up what you can Eventually do is just launch the instance. So just click
launcher launch instance, but before that any doubts Actually, I don't have a doubt I just want to
know Where we are going to use this? I mean we are doing this all enrollment here enrollment Yeah, I
mean to say we have we are doing this process, but where it will be applicable where we will be
using this so You created an

### [14:29]

Model you like any organization like let's say deep trick. Okay deep trick created a model They want
that model to be publicly available for users or even let's say we take an example of open a open a
created a model Now, how are you able to access that Jupiter? How are you able to use the open a API
that is via? Somewhere that that model is stored and it is sold to users. So we are trying to
replicate the same We have some solution. We are trying to deploy on a cloud server such that Users
across across the globe can use that you can think of it like You created a website put it on the
Cloud server so that multiple people can access your website Okay Not in the marketplace. We will
just push it till the access part Okay, I will just launch the instance So depending on this is like
this is a very low-end instance So it won't take much time to start but if you have a high-end
instance It can take two minutes five minutes if it has a GPU It doesn't have have a GPU requires
more RAM or more storage. So it will work accordingly like that so once Your instance is launched.
You can simply click on this instance ID. So this is what we call this instance ID starts with I

### [16:34]

if you see it will properly navigate me to this instance, which I just created fast API test and Now
to start using this instance what I can do is I guess we will simply click on this instance ID again
So this gives me all the information like what is the IP before address instance state it is running
the host name the security details So not like as you learn more on cloud as you like Keep getting
experience with it You will get Like the more services you use or more you are getting involved in
the MLOPS processes You will start knowing a lot of things but for now, let's just keep it simple
This gives us information about the instances. So now what major thing? We need to do is so till now
what we did was went to EC2 launched in particular instance added a dot PPK file to it and once
instance is created we Now would be connecting to the instance. So how you can simply do it is you
have a connect button This connect button when you click you first of all, you will have multiple
options but you simply click on this connect button again and This will lead you to a terminal. So
this is the terminal of a Different Linux OS that is hosted somewhere in Mumbai by the AWS team so
it has its own IP and your exit accessing a Different system from your own system. So that is how
you can think of it like this

### [18:38]

so Now there are certain commands before actually starting to code the stuff here. So What generally
is preferred is you up you run these two commands update and upgrade To ensure everything in the
server is updated because sometimes it can be that some driver is required for by certain library
That it should be in the latest updated. So You will simply run these two commands for now when is
update and the other one is upgrade it will take some time Once update is done Then the upgrade
command it will ask for you want to yes or no. I'll just put yes so this is done now one thing is
all these servers nowadays comes with an pre-installed Python okay so no need to spend time
installing Python but we do

### [20:43]

need to install the pip and the virtual environments whatever we want to create but before directly
jumping there what we will first do is we will move our code from our local system to this cloud
server so people on Windows they can use this WinSCP service there is also similar service for Linux
as well but with a different name so what the tools like WinSCP does is you need to go to your
instant details I'm sorry not the instant detail yeah I will just click this connect button yeah
onto this connect button copy your public IPv4 address this would be your hostname Ubuntu is your
username now you don't have a password but I will go to advanced and on the advanced in SSH click on
authentication here is where we would be passing that installed dot ppk file the first APA test
click ok login and this is like an key key addition so just put it as yes so this has actually
opened the same instance we have we have here so if I just put LS it is nothing so what I will do is
I will do mkdir app here and if you go here you'll just refresh so you see I created and directory
here and just directory is reflected here so now what I will simply do here is I will just copy all
my major files from here I will put it all inside the app folder so now if I go to CD app and do LS
you will see all my files are

### [22:51]

copied from my local system to my virtual server any doubts on this yeah hi Jirag so what to do for
Macbook okay just a minute you know about SCP yeah I'm for Windows SC win SCP and this putty as I'm
aware of but I have Macbook so there is there is a filezilla that Mac and Linux both supports can
you share the link of sure there might be other alternatives as well but this is the one I have came
across and for a secure shell we can use our terminal right in Mac it works yeah you can use that
there's not an issue with that okay thank you not terrible we can't use drag-and-drop I guess we are
good so now as we have pushed our files to the server I can close win SCP now not

### [24:54]

needed now what I will do is I will install tip because there is only Python there there is no tip
there so what I need to do is this is the command like when I will share the code with you will get
this command and similarly we will install the VNV which is Python functionality that allows us to
create virtual environments so how to do or how to create a virtual and I'll just create my terminal
is the font too small I will just increase the size yeah to create a virtual environment like we
just installed VNV so what you can do is Python 3 dash M V ENV ENV that's it enter and what it does
eventually is if you go and just put LS it has created this ENV folder right so that ENV folder is
where our activate file is activate file meaning that is where the source of our environment is and
we can activate the environment from there so to activate an environment like if you are not using
Conda so source the folder the environment folder that is ENV for us bin and activate source the

### [27:00]

folder any environment instead of ENV let's say if you have named it my environment then my
environment slash bin slash activate enter so if the environment name comes up like this that means
your environment is activated so this shall be the standard process of doing this install pip
install VNV create environment and then activate the environment now what you can essentially do is
install all your required libraries using the requirements.txt now to check what is inside my
requirements.txt I can simply use vim command vim requirements.txt I can enter a font not matching
just a minute so vim requirements.txt so all the stuff that I have mentioned here like what kind of
bridge I require now sometimes for beginners exist like exiting from the vim can be a hassle so what
you need to actually do is shift colon so if you see here shift colon type QA and enter this will
exit from the vim now I am just again trying so if you want to edit you can simply just type
anywhere so I by mistake I print printed I so it happened but otherwise just a minute did I put
anything wrong 8.0.0 yeah so by default you can just type it anything so anyone is speaking so what
if you want

### [29:12]

to edit any file what you can do is you can simply press I in the bottom it will show you insert
when it shows you insert we can you can you please what senior I said I couldn't hear properly yeah
it was from the audio coming from me I don't know like your voice is not very clear to me like the
person who's the mic was on he muted now oh okay okay now when the insert mode is active we can see
that on the bottom left there is this insert so you can add something now to exit after the insert
mode just simply press escape now if you have let's say made changes to your file what you need to
do is colon W that means this will write something to the file and to exit again colon QA that is
done now simply installing the libraries so remember here on Windows we people have an idea of using
pip Python but for Linux or Mac users they would be familiar with pip 3 Python 3 so when on a Ubuntu
system we need to install pip 3 sorry we need to use pip 3 so the command here would be pip 3
install-r requirements.txt so this will install all the libraries from requirements.txt of taking a
lot more time than usual successfully installed yes so I will

### [33:13]

just clear the terminal yeah so we just installed all the necessary libraries and what would be the
next step is we would now actually run so we'll just start with the demo run so we can main app now
when on cloud remember to mention this host 0 0 0 because then only other people would be able to
access if you run it on the local host of the cloud then that might not work properly and even if
you want to add any particular port for your application you can let's say I want to run this on
8000 only or 8080 particularly then what you you can add a port like this I will just run this so to
confirm that this is working in the same host would be like this 0.0.0 and 8080 like this now to
actually access this application out of this terminal so there's anyone has an idea how can I access
this I'll just go back to my running instance be public before and the port we have we are running
8080 that I have to put sorry I have add STTPS now if you see this is not working any reason why
this is not working STTPS will only work sorry STTPS will work in a case where you add a

### [35:30]

domain and official SSL certificate otherwise by default it will be running at HTTP only so the
point is like when you connect to these server for the first time it by default blocks all the
incoming requests so what you need to do is on your instance information you need to go to the
security there would be inbound rules you go to that particular security group click on the security
group ID edit inbound rules and here on this you need to add your port number as a custom TCP so for
I had a port number of 8080 add like as we mentioned host 0.0.0 so add that see rules now if I go
back I'll run this you will see welcome to fast API demo it is now working right so and if I want to
go to the swagger UI I can access it like this so now what we will do is I'll just stop this and
what we will see is yeah we just edited the inbound rules okay fine now I will run the actual that
CREU AI email generator application we had so you can CREU running on the same port yeah now we have
this draft email where we can pass in this read route but now this fast API service is working now
what if like I created the application I run I use the run command to run the application now what
happens if I go to my terminal I just close this terminal will this particular service keep working
or will it stop like what do you guys think will

### [38:05]

it keep working I have closed my AWS terminal it will work okay it will work I'll just try to
refresh it's gone why because as soon as you close the terminal the run command also got terminated
along with that so how to handle that any ideas anyone and in background mode okay right so now just
let me start the moment again this was a command which we used to simply run it we can access it but
as soon as the terminal closes or I put control C here this stops working so to run it in a
background mode we have command as no hub so what you can simply do is the writer original command
and add nohub as a prefix to it and just keep enter

### [40:10]

now you can see if i run this this will work now if i go and close the terminal we'll refresh on the
first refresh it might take some load but let's say we just close it it will still keep running
anytime you want yeah what i don't know why but i guess i need to increase the sound it's already in
full sound i'm saying terminal screen is not visible i think you closed it yeah i closed it so like
i closed it the reason i just wanted to demonstrate even if you close the terminal the fast api will
still keep working now once the nohub is running how do you actually stop that from running so now
what will happen is let's say there's already a service running at port 8080 and i want to uh like i
updated my code and i want to rerun that particular code now if i go and run the same command there
is already a service running at port 8080 right so it will throw me an error that address already in
use so how do you stop the already running nohub

### [42:11]

process so for that there's a command that lets you check so this is this ps-ef that straight line
grip and whatever uh command like i was using a unicorn service so i just need to type uvcon if it
was python then i need to type python or whatever stream it then stream it so once i enter this it
will the command which you run here the one function which has the same command here you need to
check its first id so what it gives is one one two four zero so now you need to kill this particular
id so you just can simply type kill one one two four zero if you see it this particular full of uh
that uh command that was running is now stopped running so now when you rerun so i'll just stop this
in a case so now we just killed the nohub process so if i go back here this particular fast api has
now stopped working because we killed the nohub background process if i again started this will
again start working so as simple as that nothing very uh extraordinary but now let's say you have
certain case where you need to run multiple applications so either what you would do is run each
through a nohub but that will increase the like complexity like tracking where all the nohub
processors are running or else even you can use something called as tmux so tmux is also a kind of a
service that lets you run the functions into

### [44:19]

the background so how you can use it is like let's say we'll just walk through through the basic
examples uh the like you can just simply write tmux it is already installed on linux tmux enter so
this kind of a green colored uh like here in the background it will be zero zero bash like this so
this is we have entered a different terminal inside the terminal we were accessing of the linux so
if i want to exit out of this terminal what you need to do is you need to do press ctrl plus b and
press d so this will detach you from this particular session so now to list all the uh what i will
say list the number of tmux sessions you are running in your uh machine tmux list session so it will
show you how many uh sessions are running now so let's say you uh create a tmux session you
connected and you ran some service there now what if you want to attach back like you detach from it
so to attach back to it tmux attach dash t and the terminal name so here it is zero so i'll just put
it zero so it again attached back to the original session so i just again press ctrl b and d and now
to actually kill a session that is running that is again also simple like tmux kill session dash t
zero now if i list session there is no server running or tmux that means uh we just kill that
particular session but now when you you know just you just type tmux and press enter uh it will give
numbers like zero one two three in a sequential manner and that is not very readable so what you can
eventually do is you can use this uh command tmux new dash s give a name so i will give name as

### [46:25]

fast api now here on to this point what you can do is activate your environment uh and then i will
keep the code running here ctrl b plus d detached from the fast api session if i run rerun this this
is still working now same way what i can do is i can create another tmux session i will name it
streamlit here i will so when you create a new separate uh tmux terminal you need to again connect
to the uh environment so i'll just like each each tmux terminal will separate terminal all together
i will simply now i started the streamlit service but if i go it is running on eight five zero one
if i try to access this this won't work why any reasons why it won't work we just did something to
make fast api work we can add the rules i'll go back to my security group add another rule to accept
eight five zero one port see rules i'll go back and this will make my streamlit service running as
well so i can detach from

### [48:30]

the service and now if you look at this session you will find fast api streamlit more readable
formats like what uh particular terminal what service is running so to test it we can simply take an
example same example we had last time as well so this throws an error okay an error occurred what do
you think why this throws an error because port is eight thousand so that was an error with respect
to port patch back here i will run this on eight thousand port let me just change my security rules
again so in the streamlit file it was accepting Shall work now Yeah, it's now working. So yeah, even
the email generator is working properly So that is how you can use Tmux now, I will just detach it
and even if I close this

### [50:32]

This shall keep running so you see It is still working fast TPA is taking a load. I might just close
it and give it a restart It generally happens when you close a terminal It might slow down for a
bit, but it would still keep working not an issue with that Let's stop there. Just a minute. You
know, it is still working Yes, you know, it is still working. Oh I'm running on ATT. We just change
it, right? Yeah, it has a little walk So you close the terminal still with the services will keep
working at the respective ends So that is how we can deploy any kind of a service now We just did
with any kind of application with fast API now what you can do is any project till now you have
created Into the program if you have created any fast API service or even if you have created a
streamlet UI You can go and experiment how to deploy it on AWS even if you have a GCP cloud or Azure
like if you have credits if you're a student or you have some learning credits Added to your account
then in that case You can make use of those credits and whatever cloud platform it is. The rules
would be simple You go to the terminal of that particular instance Add your code run it and open
your ports that will allow access

### [52:34]

To the IP address and this is how you can deploy an application On to a cloud service now from here
the domain connection part Yahvee Yeah, so my question is that like can you again it is just been
show how to Open up the EC2 server like a terminal on cloud and the second question is why do we
need virtual environment on? A server where it is already an individual like a separate server so
let's say In a server if I'm running two services or if in a single server I have so there can be
dependence like let's say I have one legacy system or a legacy format where a Application is running
and to update that is is hard and there is another Python service Which requires a newer library? So
if there is a clash between both the versions, I would specifically Use two different environments.
So that is one thing and then to run this instance So when you go like I'll just go to back to the
main dashboard of AWS You you want to see how it is launched or connect only so I go back to EC2
click on instances running so It will show you your instances that are running. We created this fast
API test click on the instance ID and Here there will be a connect button over here click on connect
and Click on connect button here, which will land you to the terminal screen

### [54:35]

Okay, okay got it and there is something called secure shell right there such as such so do we we
don't need that if But right if it if this works then if No, no, even SSS SSH you need to use if
let's say There is only one main account like let's say you're working in a team And on a once
account you will create the main This what I say Like easy to service and if they want to share it
others they might create an SSH key and then you need to Like onto a normal command prompt you need
to access this terminal using the SSH Okay, good Usually the devops team would handle Yeah, so they
would give just Credentials and PPK file and And now coming to the most important part is
Remembering to terminate your instances Otherwise you will be built. I have built build for
thousands like when I was learning in college, but I had free credits so It was not eventually
charged anything So click on the service that is running instance state terminate delete instance So
if anyone has doubts, I will not terminate this now, but I will terminate after the session. So I'll
go back to instance ID if you have doubts Surely, please ask

### [57:07]

So we also need to enable this multi-factor authentication, right? So I even I was build for around
2.5 lakhs once and got it Because my ID was being hacked. They're running all the places so yeah, so
I Think it's what going with multi-factor authentication as well. Yes. Yes Yeah, so she runs one
just question is like So can we run Docker image like the same as we run on our local system on EC2
server So does this work the same way like on the server like the image is a Yes, you just need to
have Docker on your system and you can simply Like upload your files from local to the cloud the
Docker file or Docker compose whatever you have and Use the Docker and commands make sure the ports
are active for that and it should work perfectly on Okay, I know you see to there shouldn't be there
is no need to any Docker installation or any image or any other So I I believe Docker is needed
there

### [59:10]

Docker won't be there by default you would need so This will give you all the commands to install
Docker Hmm just to run this command and Docker would be there for you and even if you want to use a
different service you can also make use of AWS ECR and GitHub actions to actually push all of this
on easy to So this is one project just for my personal learning. I just created it. I'll just add
this link here into the chat. It involves GitHub actions, awcc2, awccr.

### [1:01:20]

I believe there are no more doubts. Then I will terminate the instance and also stop the recording.
Thank you. I think we are all good. Stop the recording.

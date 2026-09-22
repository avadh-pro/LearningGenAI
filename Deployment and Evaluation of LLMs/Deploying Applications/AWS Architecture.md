# Possible AWS Deployment Architectures

**One-liner verdict:** this slide is a menu of nine ways to run the same app on AWS, sorted loosely by *how much of the machine you have to babysit* — and the whole point is that moving down the list trades **control** for **convenience**.

---

# Part 1 — The legend first

Every mini-diagram is built from six icons. Learn these and the diagrams read themselves.

| Icon | Name | What it actually means |
|---|---|---|
| ☁️ cloud | **Internet** | Where the request comes from — your users' browsers |
| 👥 people | **Users** | Same thing, drawn differently in options 8 & 9 |
| ⊗ circle with arrows | **Load Balancer** | A traffic cop sitting in front of your app. One public address, spreads requests across however many copies are running, and stops sending to copies that are sick |
| ▦ orange grid | **Container / Tasks** | Your running containers |
| 📦 ECR icon | **ECR — Elastic Container Registry** | AWS's private warehouse for Docker images |
| ⎈ ship's wheel | **Kubernetes** | The industry-standard container orchestrator (the wheel is its actual logo) |

**Arrow direction = request flow.** Internet → load balancer → your containers.

**Dotted line to ECR** = not request traffic. It means *"this thing pulls its image from ECR at startup."*

---

# Part 2 — The core jargon, before the nine options

### Virtual Machine (VM) / EC2 instance
A whole computer you rent — OS and all. You install things, you patch things, you restart it.
> 🏠 **Renting an empty flat.** Furniture, plumbing, security: yours.

### Container / Docker image
A sealed box holding your code + its exact dependencies. Runs identically anywhere.
> 📦 **A shipping container.** The ship doesn't care what's inside.

**Image vs container:** image = the recipe on disk. Container = the dish, actually cooking. One image → many containers.

### Registry (ECR)
Where images are stored so AWS can fetch them. Docker Hub is the public one; ECR is your private one.
> 📚 **A library.** You push the book in; anything that needs it borrows a copy.

### Orchestrator
The software that decides *which machine runs which container*, restarts dead ones, and replaces them during deploys. **ECS** and **Kubernetes** are the two on this slide.
> 👨‍🍳 **The head chef.** Doesn't cook — decides what gets cooked, notices when a dish is dropped, orders it remade.

### "Managed" / "Serverless"
Servers still exist. They're just **Amazon's problem**, not yours. No SSH, no OS patching, no capacity planning.

### Task
ECS's word for **one running unit** — one or more containers started together, sharing a network. Your lab's task = FastAPI container + Streamlit container together.

### Stateless
The app remembers nothing between requests. Any copy can serve any request. Memory goes to a database instead.
> This is why you can run 5 copies behind a load balancer without users noticing.

### Patching
Installing OS security updates. Boring, endless, and **entirely yours** on options 1, 2, and 6.

---

# Part 3 — The nine options

## The spine that explains all of them

```
YOU MANAGE MORE                                    AWS MANAGES MORE
◄─────────────────────────────────────────────────────────────────►

1 Simple EC2                                            8 Lambda
   2 ECR+EC2                                     3 App Runner
      6 ECS on EC2                            5 ECS Fargate
         7 EKS                          4 Elastic Beanstalk
                                             9 SageMaker
```

---

## 1️⃣ Simple EC2 server

**Diagram:** Internet → EC2 (Application). Nothing else. The simplest possible picture.

**What you do:** rent a Linux box, SSH in, `git clone`, `pip install`, `uvicorn main.py`, open a port. Done.

> 🏠 **Renting an empty flat and moving in yourself.**

| | |
|---|---|
| **Best fit** | Your first deployment; maximum host control |
| **Trade-off** | *"You patch, secure, monitor, and recover the server"* |

**What that trade-off really costs you:** at 3am the process crashes and **nothing restarts it**. A security patch comes out — you install it. Traffic doubles — you manually resize the box and take downtime doing it.

**Example:** a college project or internal demo. Works fine, and teaches you why every other option exists.

---

## 2️⃣ ECR + Docker on EC2

**Diagram:** Internet → EC2 running Docker, with a dotted line to ECR.

**What you do:** same rented box, but instead of installing Python and dependencies by hand, you `docker pull` your image from ECR and `docker run` it.

> 🏠 **Same flat — but your furniture arrives pre-assembled in a sealed crate.**

| | |
|---|---|
| **Best fit** | Repeatable image, familiar VM operations |
| **Trade-off** | *"Container lifecycle and host scaling remain your job"* |

**The gain over option 1:** no more "works on my machine." The image that ran on your laptop is byte-for-byte what runs on the server.

**What you still own:** ⚠️ **there is no orchestrator here.** Container dies → it stays dead. You're the orchestrator, manually.

> This is the one people most often mistake for needing Kubernetes. It's the opposite — it has the *least* automation of any container option.

---

## 3️⃣ AWS App Runner

**Diagram:** Internet → App Runner. One box. Notably **no load balancer drawn** — because it's built in.

**What you do:** point App Runner at your ECR image. It gives you an HTTPS URL, autoscaling, and health checks. No cluster, no networking, no task definition.

> 🏨 **A serviced apartment.** Walk in, everything works, you touch nothing.

| | |
|---|---|
| **Best fit** | Simple **stateless** web container |
| **Trade-off** | *"Less infrastructure control; fit and pricing must be checked"* |

**"Fit must be checked"** is the warning: it expects one container serving HTTP on one port. Your lab has **two** containers (API + UI) that need to talk privately — awkward here.

**"Pricing must be checked":** it bills for provisioned memory even while idle, so a low-traffic service can cost more than Fargate.

**Example:** a single FastAPI microservice that just needs a public HTTPS URL fast.

---

## 4️⃣ Elastic Beanstalk

**Diagram:** Internet → Elastic Beanstalk (Platform).

**What you do:** upload your code (or a Dockerfile). Beanstalk quietly creates EC2 instances, a load balancer, an autoscaling group, and health monitoring **for you** — and you can still open the hood and look at them.

> 🚚 **A moving service.** They pack and drive, but it's still your truck and your stuff — you can open the back.

| | |
|---|---|
| **Best fit** | Managed application platform |
| **Trade-off** | *"Platform conventions and less explicit container orchestration"* |

**"Platform conventions"** = it has opinions about your folder layout, config files, and lifecycle hooks. Fight them and it fights back.

**Reality check:** this is the *older* AWS answer. Most new container work goes to Fargate or App Runner instead. Worth recognising — you'll meet it in legacy systems.

---

## 5️⃣ ECR + ECS Fargate ⭐ **← this is what your lab uses**

**Diagram:** Internet → Load Balancer → ECS Fargate (Tasks), with ECR feeding down into it.

**What you do:** push image to ECR → write a task definition (the blueprint) → ECS runs it on Fargate. **No EC2 instance ever appears in your account.**

> 🚕 **Uber instead of owning a car.** It shows up, does the job, disappears. You never think about the engine.

| | |
|---|---|
| **Best fit** | Managed container orchestration **without managing hosts** |
| **Trade-off** | *"More AWS concepts than one VM; no GPU task support"* |

**The division of labour — memorise this, it's an interview staple:**

| Piece | Role | Four words |
|---|---|---|
| **ECR** | storage | stores the image |
| **Task definition** | blueprint | declares what runs |
| **ECS** | control plane 🧠 | decides and watches |
| **Fargate** | data plane 💪 | provisions and runs |

**"More AWS concepts"** is honest — you'll touch ECR, IAM roles, Secrets Manager, CloudWatch, security groups, VPC subnets, cluster, task definition, and service. That's your Batches 2-6.

**"No GPU task support"** ⚠️ — Fargate cannot attach a GPU. Perfect for your app (it *calls* OpenAI, it doesn't host a model). Immediately disqualifying if you wanted to serve your own Llama weights.

> 📌 **Note for your lab:** the slide draws a load balancer. **Your lab skips it** and hits the task's public IP directly. That's a deliberate simplification — it's also why you get no HTTPS and no stable DNS.

---

## 6️⃣ ECS on EC2 / ECS Managed Instances

**Diagram:** Internet → Load Balancer → ECS (EC2/Managed Instances), ECR feeding in. **Same picture as option 5** — with EC2 boxes underneath.

**What you do:** identical ECS concepts, but the containers land on **EC2 instances you own** instead of invisible Fargate capacity.

> 🚗 **Uber vs. hiring a driver for your own car.** Same experience in the back seat — but the car, the fuel, and the servicing are yours.

| | |
|---|---|
| **Best fit** | Containers needing **special instance types or GPUs** |
| **Trade-off** | *"Capacity and hardware decisions return"* |

**Why anyone chooses this over Fargate — three real reasons:**

| Reason | Detail |
|---|---|
| **GPUs** | The big one. Serving your own model? Fargate can't. This can (`g5.xlarge` etc.) |
| **Cost at scale** | Steady 24/7 load is cheaper on Reserved/Spot EC2 than per-second Fargate |
| **Special hardware** | Huge RAM, local NVMe, ARM/Graviton |

**"Capacity decisions return"** means you're back to: how many instances, what size, when to scale, who patches the AMI.

*(**ECS Managed Instances** is the newer middle ground — real EC2 instances, but AWS handles the patching and lifecycle.)*

---

## 7️⃣ Amazon EKS

**Diagram:** Internet → Load Balancer → Amazon EKS (Kubernetes ⎈), ECR feeding in.

**What you do:** run **managed Kubernetes**. AWS runs the Kubernetes control plane; you define Deployments, Services, Ingresses, ConfigMaps, and so on in YAML.

> 🏗️ **Hiring a full construction crew with its own project-management system.** Enormously capable. Also a whole discipline to learn.

| | |
|---|---|
| **Best fit** | Teams **already standardized on Kubernetes** |
| **Trade-off** | *"Highest orchestration flexibility and operational complexity"* |

**Why it exists:** Kubernetes is the only option here that's **cloud-portable**. The same manifests run on EKS, GKE, AKS, or on-premises. That's the real argument — not features.

> ⚠️ **This is the only row where Kubernetes appears.** Options 2, 5, and 6 are all containers with *no* Kubernetes anywhere. People conflate "containers" with "Kubernetes" constantly — they're separate things.

**The honest interview answer:** *"For one app with two containers, EKS is significant complexity for no benefit. It earns its cost when many teams share a platform, or when portability across clouds is a hard requirement."*

---

## 8️⃣ Lambda + API Gateway

**Diagram:** Users 👥 → API Gateway → Lambda. **No ECR, no load balancer, no container icon.**

**What you do:** write a function. API Gateway turns an HTTP request into a function call. Nothing runs when nobody's asking.

- **API Gateway** = the front door — receives HTTP, handles auth/throttling/routing, then invokes your function.
- **Lambda** = your function, run on demand, billed per millisecond.

> 🚖 **Calling a cab per trip** — versus options 1-7, where a car sits parked costing you money.

| | |
|---|---|
| **Best fit** | Short, **event-driven, stateless** functions |
| **Trade-off** | *"Streamlit and long model calls are not a natural fit"* |

**Unpacking that trade-off — it's specifically about *your* app:**

| Problem | Why |
|---|---|
| **Streamlit doesn't fit** | Streamlit holds a **persistent connection** and per-user session state. Lambda is one-request-in, one-response-out. Fundamentally incompatible |
| **Long model calls** | Lambda caps at 15 minutes, and API Gateway cuts off at ~30 **seconds**. A slow LLM generation can blow that |
| **Cold starts** | Idle function → AWS builds the environment from scratch → 1-3 second delay on the first request |

**Where Lambda *is* perfect:** PDF lands in S3 → Lambda chunks it, embeds it, writes vectors. Bursty, short, stateless. **Lambda is great for *calling* an LLM, wrong for *hosting* one.**

---

## 9️⃣ SageMaker AI endpoint

**Diagram:** Users 👥 → SageMaker Endpoint → a model icon.

**What you do:** hand SageMaker your **model weights**. It gives you a managed, autoscaling, GPU-backed inference endpoint with versioning and A/B traffic splitting.

> 🍽️ **A professional kitchen built only for one cuisine.** Superb at that. Useless for anything else.

| | |
|---|---|
| **Best fit** | Hosting and scaling **owned/open models** |
| **Trade-off** | *"ML-specific platform, endpoint, and compute cost decisions"* |

**When this is the right answer:** you fine-tuned Llama 3 and need it served on GPUs with autoscaling. Options 1-8 make you build that yourself; SageMaker hands it to you.

**Why it's wrong for your lab:** ⚠️ **you don't own a model.** Your app calls OpenAI's API over HTTPS. SageMaker would be an expensive GPU box serving nothing.

**"Compute cost decisions"** is a polite warning: GPU endpoints bill **per hour, always-on** — easily $1-5/hr. Forget one for a weekend and that's a real bill.

---

# Part 4 — Reading the whole slide at once

| # | Option | Containers? | Orchestrator | Who owns the server | GPU | Your app? |
|---|---|---|---|---|---|---|
| 1 | Simple EC2 | ❌ | none | **you** | ✅ | works, fragile |
| 2 | ECR + EC2 | ✅ | **none** | **you** | ✅ | works, fragile |
| 3 | App Runner | ✅ | built-in | AWS | ❌ | awkward — 2 containers |
| 4 | Beanstalk | either | built-in | AWS-ish | ✅ | dated |
| **5** | **ECR + Fargate** | ✅ | **ECS** | **AWS** | ❌ | ⭐ **chosen** |
| 6 | ECS on EC2 | ✅ | ECS | **you** | ✅ | overkill |
| 7 | EKS | ✅ | **Kubernetes** | you | ✅ | overkill |
| 8 | Lambda + APIGW | ❌ | n/a | AWS | ❌ | ❌ Streamlit breaks |
| 9 | SageMaker | n/a | n/a | AWS | ✅ | ❌ no model to host |

### The four questions that pick your row

```
Do you host your own model weights?  ──YES──►  9 SageMaker, or 6 (GPU)
              │ NO
              ▼
Is the work short, bursty, stateless? ──YES──►  8 Lambda
              │ NO
              ▼
Is your team already on Kubernetes?  ──YES──►  7 EKS
              │ NO
              ▼
Do you want to manage servers?  ──NO──►  5 ECS FARGATE  ⭐
                                │ YES
                                ▼
                        1 / 2 / 6
```

### Why option 5 won for your lab

> **"The app was already containerized and needed real orchestration — self-healing, rolling deploys, secrets, logging — without owning a server or learning Kubernetes. It calls OpenAI rather than hosting a model, so Fargate's lack of GPU costs nothing."**

The two things it dodged:
- ❌ **EKS** — avoided *Kubernetes*
- ❌ **ECS on EC2** — avoided *servers*

Fargate is the only row that dodges **both**.

---

# Part 5 — The interview version

> *"AWS deployment options are a spectrum of managed responsibility. A plain EC2 instance gives maximum control and maximum operational burden — you patch it, you monitor it, you restart it. At the other end, Lambda and App Runner remove all host management but constrain you to short, stateless, single-container workloads. In the middle, ECS gives real orchestration, and Fargate versus EC2 launch type decides whether you own the hosts. EKS is only justified when a team is already invested in Kubernetes or needs cross-cloud portability.*
>
> *For a containerized GenAI app that calls a hosted model API, ECR plus ECS Fargate is usually the right default: orchestration without server management, native Secrets Manager and CloudWatch integration. The dealbreaker to check first is GPU — Fargate has none, so anything self-hosting model weights moves to ECS on EC2 or a SageMaker endpoint."*

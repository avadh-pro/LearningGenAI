# Deploying a GenAI Application — Video Notes

Condensed, transcript-based notes from a TMLC Academy session on taking a working GenAI app off your laptop and onto AWS. See *Deploying a GenAI Application - Transcript.md* in this folder for the full source recording transcript, and *Docker and Docker Compose.pdf* for the containerization reading the session assumes you've already done. This is the longest session in Week 5 (135 min) and the most hands-on — roughly a third is concept, two-thirds is a live click-through of the AWS console.

> **Source:** *Guided Projects in Generative AI* (TMLC Academy) — [Deploying a GenAI Application](https://courses.tmlcacademy.in/courses/take/genaigp/lessons/77321866-deploying-a-genai-application) · Video lesson, 135 min (`2:14:51`).

**The one-sentence version:** everything in Weeks 1-4 produced code that runs on *your* machine; this session turns that code into a container, stores the container in the cloud, and has AWS run it so other people can reach it over the internet.

**The analogy that runs through this whole document 🍽️**

Think of a **restaurant kitchen**. Your code is a *recipe*. **Docker** packs the recipe plus every ingredient into a sealed meal-kit box, so it cooks identically in any kitchen. **ECR** is the warehouse where those boxes are stored, each with a version label. **ECS** is the shift manager — it holds the master instruction sheet, decides how many meals to cook, and restarts anything that burns. **Fargate** is the cook who actually does the work, using a kitchen you never have to own or clean. Every AWS service below is one of those roles, and the confusing part of the session is almost entirely "who does what" rather than anything conceptually hard.

---

## 1. The Three Stacks

The session frames the whole deployment as three layers. Keeping them separate is what stops the AWS console from feeling like an undifferentiated wall of services.

| Stack | What lives here | In this session |
|---|---|---|
| **Application stack** | The thing you actually built | Python, FastAPI, Streamlit |
| **Deployment stack** | What packages and runs it | Docker, ECR, ECS, Fargate |
| **Operational stack** | What keeps it safe and observable | Secrets Manager, CloudWatch, IAM |

**A note on roles, which the session is refreshingly blunt about:** if your job leans toward *building* solutions (RAG, agents, fine-tuning), you'll typically contribute to the architecture rather than own it, and a DevOps or dedicated architecture person handles the cloud design. If your job leans toward *deploying*, that's where you go deep on cloud services. Either way the expectation isn't "own all of AWS" — it's "understand enough to know why each service was chosen."

**One line:** application stack = what you wrote, deployment stack = what runs it, operational stack = what keeps it alive and auditable.

---

## 2. The Demo Application

The session deliberately uses a *simple* app so attention stays on AWS rather than the code. It's a **customer-support triage tool**: a user message comes in, and the app returns a category, an intent, and a priority, plus a reply.

The code structure is worth knowing because it's the shape most production GenAI services take:

```
app/
├── main.py            FastAPI entry point — routes, connections
├── llm_service.py     the actual OpenAI call + response generation
├── schemas.py         request/response models (Pydantic)
├── validation.py      input guards on incoming data
├── prompts.py         prompt templates, versioned if you have many
├── config.py          a settings class that reads your .env
├── logging_config.py  how logs get written
└── evaluation.py      scores the triage against a labelled dataset
frontend/              the Streamlit UI
tests/                 pytest suite
data/                  evaluation dataset + output
docker-compose.yml
```

> 📦 **Why separate these at all?** Because `config.py` reading environment variables is exactly what lets the *same* code run on your laptop with a `.env` file and on AWS with secrets injected by Secrets Manager — no code change. That single design choice is what makes the deployment later so uneventful.

### The three endpoints

| Endpoint | Purpose |
|---|---|
| `/health` | Is the service alive? Used by container health checks, not humans |
| `/generate` | The real business endpoint — takes a user message, returns triage JSON |
| `/docs` | FastAPI's free OpenAPI documentation page |

### What happens inside `/generate`

```
Request arrives
     │
     ▼
Pydantic validates the JSON       ── wrong/missing field? → 422
     │
     ▼
Strip whitespace, validate content
     │
     ▼
Build the prompt
     │
     ▼
Call OpenAI (structured output)   ── key missing / timeout? → 503
     │                               malformed structure?   → 502
     ▼
Validate category/intent/priority
     │
     ▼
Return output JSON
```

**The bit worth internalising is the error codes.** The session makes a point of it: different failure classes get *different* codes — `422` for bad input, `503` for connection or timeout failures, `502` for a structured-output or upstream API failure. That's not pedantry. When something breaks at 2am, the status code is the first thing that tells you *whose* problem it is.

**One line:** keep config in one place, validate at the boundary, and give each failure class its own status code — those three choices are what make a service deployable rather than just runnable.

---

## 3. Quality Gates Before You Deploy

The session spends real time here, and it's the part most people skip. Three checks run before anything touches AWS.

**1. `pytest` — deterministic behaviour checks.** The LLM call is *mocked*, deliberately: tests should be fast, repeatable, and must not make paid model calls. Coverage targets the boring-but-fatal cases — health endpoint responds, structured output has the right shape, blank input is rejected, missing config is caught, unexpected fields don't crash it.

> 🧪 **Why a `tests/` folder rather than scattered asserts:** you write many small test functions, then type `pytest` once. It discovers the folder, finds every test function, runs them all, and reports pass/fail/warnings together. It's consolidation, not magic.

**2. `ruff` — a linter.** Catches coding-level mistakes and style problems: unsorted imports, odd indentation, a function that doesn't exist in the library you imported. Warnings are advisory; a genuinely wrong function reference is an error you want *before* deploy.

**3. Live evaluation.** The `evaluation.py` run scores the triage against a labelled dataset and reports **field accuracy** and **exact-match accuracy** — in the demo, 87% and 62% respectively. The session is honest that improving those numbers is a separate conversation; the point is that you *measured* before shipping.

> ⚠️ **The rule the session states plainly:** every test should pass before code leaves your machine. In a real setup with CI/CD, a failing test fails the pipeline, and the deploy never happens. Shipping with red tests isn't a shortcut, it's a decision to find out in production.

**One line:** mocked tests for behaviour, a linter for code smells, and an evaluation run for actual model quality — all three before the word "deploy" comes up.

---

## 4. Docker and Docker Compose

Two ways to run the same app:

| Approach | How | When |
|---|---|---|
| **Local processes** | `uvicorn` for FastAPI, `streamlit run` for the UI | Development |
| **Containers** | `docker compose up --build` | Everything else |

The app becomes **two images** — one for the FastAPI backend, one for the Streamlit frontend — each running as its own container, with ports `8000` and `8501` respectively. Streamlit calls FastAPI from *inside* the Docker network, and a health check watches each container.

**Why Compose rather than plain Docker?** Because you have more than one service. Without Compose you'd start each container by hand, every time, with its own command. Compose clubs them into one file and one command.

> 🧰 **Everyday example:** running containers individually is like starting your dishwasher, oven, and kettle by walking to each one and pressing its button. Docker Compose is the single "start dinner prep" button that does all three in the right order. Nothing new happens — you just stop doing it manually.

**One line:** Docker makes one service portable; Compose makes a *set* of services start together as one unit.

---

## 5. Choosing an AWS Deployment Architecture

This is the conceptual heart of the session. There are many ways to put a container on AWS, and the session walks the menu before picking one.

| Option | What it is | Verdict for GenAI |
|---|---|---|
| **EC2 alone** | A virtual server you install everything on | Fine for small teams and quick launches; you own the OS, patching, restarts |
| **ECR + EC2** | Store the image in ECR, EC2 pulls and runs it | Better, but *you* still run the Docker commands and manage failures |
| **App Runner / Beanstalk** | Managed platforms for standard web apps | Usually not — limited control, and AI workloads fit their patterns poorly |
| **EKS** | Kubernetes on AWS | Only if your org already lives in Kubernetes; heavy operational surface otherwise |
| **Lambda + API Gateway** | Serverless, event-driven functions | Great for *simple* setups — a prompt or two, plain OpenAI calls. Not for a full LangGraph app with databases |
| **SageMaker** | Traditional ML inference/notebooks | Less commonly used for this now |
| **ECS + Fargate** | Orchestration + serverless compute | ✅ **Chosen here** — multi-container, no GPU needed |
| **ECS + EC2 managed instances** | Orchestration + your own instance types | ✅ The GPU answer — open-weight models live here |

### The distinction people get wrong

**`ECR + EC2` is not the same as `ECR + ECS with EC2 managed instances`**, even though both mention EC2. The session calls this out explicitly:

```
ECR + EC2
   EC2 pulls the image and you run Docker yourself.
   You write the start scripts. You handle failures.

ECR + ECS (EC2 managed instances)
   ECS handles the Docker-level setup FOR the EC2 instances.
   Task definitions, restarts, health checks — all managed.
```

The second is meaningfully better. Same raw ingredients, completely different amount of work.

### Fargate vs. EC2 managed instances

| | Fargate | EC2 managed instances |
|---|---|---|
| Model | Serverless — you specify CPU/memory, AWS provides compute | You choose instance type, OS, hardware |
| GPU | ❌ **Not supported** | ✅ Supported |
| Ops burden | Lower | Higher |
| Use it for | API-based models (OpenAI, Anthropic) | Open-weight models you host yourself |

**That GPU row is the whole decision.** If you're calling a hosted model API, Fargate is simpler and you're done. The moment you self-host an open-weight model, Fargate is off the table and you're on EC2 managed instances.

**One line:** ECS is always the orchestrator; the only real question is whether Fargate or EC2 instances do the actual computing, and GPU need is what decides it.

---

## 6. The AWS Vocabulary You Actually Need

The session's glossary, in plain terms.

**Region & availability zone.** AWS has data centres worldwide, grouped into regions (`ap-south-1` = Mumbai). Deploy near your users — a distant region adds latency. Teams also run backup services in a *second* region, so a regional outage doesn't take the product down.

**ECR (Elastic Container Registry).** Storage for Docker images, each tagged with a version label. That's its entire job here: hold the image so ECS can fetch it.

**ECS (Elastic Container Service)** — the orchestrator, with four nested concepts:

```
Cluster            the area where workloads run
  └── Service      the controller — keeps N tasks running, restarts failures
        └── Task   a running copy of the blueprint
              └── Task definition   the versioned blueprint itself
```

The **task definition** is the important one. It specifies which image to use, which command to run, health checks, exposed ports, CPU and memory, environment variables, and where logs go. Every edit creates a new **revision** — revision 1, 2, 3 — so you always know which version is live and can roll back.

> 📋 **Everyday example:** the task definition is a recipe card; a task is the dish actually being cooked from it. Editing the recipe doesn't change the dish already on the stove — you have to cook a new one, which is exactly why updating a service means pointing it at the new revision.

**Fargate.** The serverless compute layer that reads the task definition and executes it. No servers to manage; no GPU available.

**Secrets Manager.** Where your OpenAI key lives. Containers fetch it at runtime. It also supports **automatic rotation** — a Lambda function periodically generates and stores a fresh key, so no single key sits around indefinitely.

**CloudWatch.** Log storage, with a configurable retention window (the session sets 3 days). Each container streams its logs here with a prefix identifying which container they came from.

**IAM (Identity and Access Management).** Users, roles, and policies. A **role** grants a service permission to call other services — the ECS task execution role is what lets ECS pull from ECR and read from Secrets Manager. Scope each user or role to only the services they need.

> 🔑 **Why bother scoping:** two reasons the session gives. Traceability — when something breaks, you can tell who or what did it. And blast radius — a compromised or careless account can only touch what it was granted.

**VPC (Virtual Private Cloud).** Your isolated network. Where data-residency rules get enforced.

**Security groups.** Firewall rules — which IPs may reach which ports. Inbound rules are the ones that matter here.

---

## 7. The Target Architecture

What actually gets deployed:

```
        User's browser
              │
              │  port 8501  (allowed by security group)
              ▼
    ┌─────────────────────────────────────────┐
    │   ONE Fargate task                      │
    │                                         │
    │   ┌───────────────┐   ┌──────────────┐  │
    │   │  Streamlit    │──▶│   FastAPI    │  │
    │   │  container    │   │  container   │  │
    │   │  :8501        │   │  :8000       │  │
    │   └───────────────┘   └──────────────┘  │
    │        internal localhost call          │
    └─────────────────────────────────────────┘
          │              │              │
          ▼              ▼              ▼
    Secrets Manager  CloudWatch       ECR
    (OpenAI key)     (logs)      (image source)
```

**The security decision worth copying:** an inbound rule is created for port **8501** (Streamlit) but deliberately **not** for port 8000 (FastAPI). The backend is never exposed to the internet. Streamlit reaches FastAPI over localhost *inside the same task*, so no external user can hit the API directly and burn your OpenAI credits.

> 🚪 **Everyday example:** it's a restaurant with a public dining room and a closed kitchen. Customers enter the dining room (8501). Waiters walk into the kitchen (8000) through an internal door. There's no street entrance to the kitchen — by design.

**One line:** expose only the front door, keep the backend on the internal network, and let the security group enforce it.

---

## 8. The Deployment Walkthrough

The session's actual click-through, condensed. Every step exists for a reason, and the reasons are more useful than the clicks.

**1. Install and authenticate the AWS CLI.** Two login paths: `aws login` if you hold the root account, or `aws configure` with an access key + secret access key if you're an IAM user. Verify with `aws sts get-caller-identity` — the account ID it returns must match the console. (Cheap, and it catches deploying into the wrong account.)

**2. Create an ECR repository.** Name it, take the **repository URI** — that URI is how Docker knows where to push.

**3. Build and push the image.**

```powershell
# PowerShell, because variables survive between commands
$AWS_REGION     = "ap-south-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REGISTRY   = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
docker build --platform linux/amd64 -t $IMAGE_URI .
docker push $IMAGE_URI
```

> 💡 **Why PowerShell over `cmd`:** it holds variables, so you type the account ID and region once instead of pasting them into every subsequent command. A small thing that removes a whole category of typo.

**4. Store the OpenAI key in Secrets Manager.** Secret type "other", the key as plain text. Copy its **ARN** — the task definition will reference it.

**5. Create the ECS task execution role in IAM.** This is the step that bites people. The role needs *two* permission sets:
- The standard task execution policy → lets ECS pull images from ECR
- An **inline policy** for `secretsmanager:GetSecretValue`, scoped to your secret's ARN → lets ECS read the key

> 🐛 **The session hits this bug live.** The service is created with the wrong execution role, the container can't read the secret, and the deployment fails. The fix is to attach the correct role and redeploy. Genuinely useful to watch: *"permission denied on a secret"* is the single most common first-deploy failure.

**6. Create a CloudWatch log group.** `/ecs/openai-llm-app`, retention set to 3 days.

**7. Create a security group.** Inbound rule on **8501** only. Source can be `0.0.0.0/0` (the whole internet) or "My IP" for a demo. The session uses My IP — and then has to edit the rule mid-session after switching networks, which is a nice illustration of why that setting bites you.

**8. Create the ECS cluster.** Choose Fargate-only (serverless) or managed instances (where you'd pick GPU instance types).

**9. Create the task definition.** Family name, launch type Fargate, CPU and memory (0.5 vCPU / small memory for the demo). Then define **two containers**:

| | API container | Frontend container |
|---|---|---|
| Image | The ECR image | The same ECR image |
| Port | 8000 | 8501 |
| Essential | Yes | Yes |
| Env vars | `LOG_LEVEL`, model name | `API_URL` |
| Secret | `OPENAI_API_KEY` → *valueFrom* the Secrets Manager ARN | — |
| Entry point | default | `streamlit run frontend/app.py …` |
| Health check | curl the port, 30s interval, 5s timeout, N retries | same |
| Logs | CloudWatch, stream prefix `api` | CloudWatch, stream prefix `frontend` |

> ❤️ **What health checks actually buy you:** if the check fails more than `retries` times, ECS marks the container unhealthy, stops it, and starts a fresh one. That's the self-healing behaviour you'd otherwise have to build.

**10. Create the service.** Pick the cluster, the task definition revision, launch type Fargate, number of tasks (1 here), the VPC and subnets, the security group, and turn public IP on. ECS provisions the task and both containers start.

**11. Open the app.** Grab the task's **public IP**, hit port 8501. Streamlit loads; FastAPI is unreachable from outside — exactly as designed.

**To ship a change:** rebuild → push to ECR → create a new task-definition revision → update the service to that revision. Note the public IP changes on redeploy, which is precisely the problem a load balancer solves later.

---

## 9. Cost and Cleanup

The session is refreshingly concrete: the demo ran about **90 minutes for roughly $0.03**. But that's a tiny Fargate task with no GPU. Add GPU workloads and you're into **~$5/hour** territory.

> 💸 **The cost trap worth remembering:** you're billed for what you **reserve**, not what you **use**. Pick a GPU that could run a 70B model and then serve a small model on it, and you pay for the big GPU regardless. Right-size deliberately.

**Cleanup checklist** (the session insists on this, and it's how people avoid surprise bills):
1. Update the ECS service to **0 desired tasks**
2. Delete the service
3. Delete the cluster
4. Delete the ECR repository/images if no longer needed
5. Check **Billing & Cost Management** for anything still running

**One line:** the demo is genuinely cheap, GPU workloads are not, and the bill is driven by reservation rather than utilisation — so delete everything when you're done experimenting.

---

## 10. Scaling, and What Changes for Open-Weight Models

**Autoscaling, in two directions:**

| | What it does | Example |
|---|---|---|
| **Vertical** | Make the machine bigger | 30 GB RAM → 50 GB RAM |
| **Horizontal** | Make more machines | 1 container → 5 containers, ~100 users each |

ECS supports configuring task count and autoscaling policies — one of the concrete advantages over hand-managing EC2.

**If you swap OpenAI for a self-hosted open-weight model, surprisingly little changes:**

| Stays the same | Changes |
|---|---|
| Streamlit + FastAPI structure | Fargate → **EC2 managed instances** (GPU) |
| Docker / Compose | Add a serving layer: **Ollama** or **vLLM** |
| ECR, ECS, task definitions | Instance type selection matters a lot |
| CloudWatch logging, evaluation | Cost profile shifts substantially |

**Ollama vs. vLLM, briefly:** both serve open-weight models, but vLLM is built for **throughput** — KV caching and related optimisations to serve many concurrent users. The session's guidance: start with Ollama, move to vLLM when you can't scale further. (Both have their own PDFs in `Model Serving and Formats/`.)

**What the session recommends learning next**, if you're heading toward an LLMOps/AIOps role: VPC design, load balancers, auto-scaling groups, routing rules, **GitHub Actions for CI/CD**, and **Terraform** for infrastructure-as-code. The framing is useful — everything done manually in the console here is exactly what GitHub Actions and Terraform automate.

---

## Key Takeaways

1. **Three stacks, not one pile of services** — application (FastAPI, Streamlit), deployment (Docker, ECR, ECS, Fargate), operational (Secrets Manager, CloudWatch, IAM).
2. **Quality gates come before deployment** — mocked pytest suite, a linter, and an evaluation run. In a CI/CD setup, failing tests must fail the pipeline.
3. **ECS orchestrates; Fargate or EC2 executes.** The only real architecture question is which compute layer, and **GPU need is the deciding factor** — Fargate has no GPU.
4. **`ECR + EC2` ≠ `ECR + ECS with EC2 managed instances`.** The second lets ECS manage container lifecycle for you; the first leaves it to you.
5. **The task definition is a versioned blueprint.** Every change creates a revision, and deploying means pointing the service at a new one — which is also your rollback path.
6. **Never bake secrets into images.** Secrets Manager holds the key; the task definition references it by ARN; IAM grants the task permission to read it — and a wrong role here is the most common first-deploy failure.
7. **Expose only what must be exposed.** Streamlit's port is open, FastAPI's is not; they talk over internal localhost inside the same task.
8. **Health checks are free self-healing** — ECS restarts unhealthy containers automatically once you configure them.
9. **You pay for reserved capacity, not used capacity.** Right-size, and delete everything after experimenting.
10. **What's manual here is what CI/CD automates later.** GitHub Actions and Terraform replace the console clicking, which is the natural next step.

---

## 🎤 Interview Prep — Mock Interview (GenAI Application Deployment, ~4-5 Years' AI Engineering Experience)

*Questions below are drawn from current (2026) interview-question banks and practitioner write-ups on LLM deployment, containerization, and AWS container services — sources listed at the end — then grounded in what this session actually taught. Same two-layer format as the other Video Notes files: a plain-language answer with an example, then a crisp, technically precise version. Try answering out loud first.*

---

**🎙️ Interview Q1:** "Walk me through how you'd deploy a GenAI service, and why containerize it at all rather than just running it on a server?"

**✅ Strong answer:** "Containerizing solves the 'works on my machine' problem. Docker bundles the app, the model-serving code, and every dependency into one image, so the same artifact runs identically on my laptop, a colleague's machine, and production. Without that, you're reinstalling Python versions and library pins on a server and hoping they match.

**Everyday example:** it's the difference between mailing someone a recipe and mailing them a sealed meal kit. The recipe assumes their kitchen has the same ingredients; the meal kit doesn't assume anything.

The flow is: build the image locally, push it to a registry like ECR, then have an orchestrator pull and run it. For a multi-service app — a FastAPI backend and a Streamlit frontend — I'd use Docker Compose locally so both start with one command, then define both containers in a single ECS task definition for production."

**🎯 Standard Interview Answer:** "Containerization provides environment parity and dependency isolation: the image encapsulates application code, runtime, and transitive dependencies as an immutable, versioned artifact. The deployment path is build → push to a registry (ECR) → pull and execute via an orchestrator (ECS). Multi-service applications are composed locally with Docker Compose and mapped to a multi-container task definition in production, keeping the local and deployed topologies equivalent. The immutability is what makes rollback tractable — you redeploy a previous image tag rather than attempting to reverse a mutation on a live server."

---

**🎙️ Interview Q2:** "How do you structure a FastAPI service for production, and how do you handle malformed input?"

**✅ Strong answer:** "I separate concerns into predictable files — routes in the entry point, the LLM call in its own service module, request/response models as Pydantic schemas, and a config module that reads environment variables. That config separation is the important one: it's what lets identical code read a `.env` file locally and injected secrets in production without a code change.

For malformed input, Pydantic validates at the boundary before any business logic runs. A missing or wrong-typed field returns **422** automatically. Beyond that, I map failure classes to distinct status codes — **503** for upstream connection failures or timeouts, **502** when the model returns something that doesn't match the expected structured output.

**Why distinct codes matter:** when you're paged at 2am, the status code is the first signal of *whose* problem it is. A blanket 500 tells you nothing."

**🎯 Standard Interview Answer:** "Production FastAPI structure separates routing, service logic, schema definitions, validation, and configuration into discrete modules, with configuration read from environment variables via a settings class so the artifact is environment-agnostic. Input validation is enforced declaratively at the boundary through Pydantic models, yielding automatic 422 responses on schema violation. Beyond schema validation, failure modes are mapped to semantically distinct status codes — 503 for upstream unavailability or timeout, 502 for malformed upstream responses including structured-output violations — which makes failures triageable from logs and metrics alone rather than requiring reproduction."

---

**🎙️ Interview Q3:** "You need to deploy a containerized GenAI app on AWS. Walk me through the options and justify your choice."

**✅ Strong answer:** "The realistic menu is EC2, Lambda, ECS with Fargate, ECS on EC2 instances, or EKS.

- **Lambda + API Gateway** is great when the app is genuinely simple — one or two prompts, a plain API call. It's on-demand and cheap. But it doesn't fit a multi-service app with databases and long-running state.
- **Plain EC2** works, but you own the OS, patching, restarts, and startup scripts.
- **EKS** only makes sense if the organisation already runs Kubernetes; otherwise the operational surface is disproportionate.
- **ECS with Fargate** is where I'd land for a containerized app calling a hosted model API. ECS handles orchestration — restarts, health checks, desired task count — and Fargate runs the compute serverlessly.
- **ECS on EC2 managed instances** is the choice the moment I need a GPU, because **Fargate doesn't support GPU**.

So my decision rule is: hosted model API → Fargate; self-hosted open-weight model → ECS on EC2 instances."

**🎯 Standard Interview Answer:** "The evaluation axes are operational ownership, workload shape, and hardware requirements. Lambda suits stateless, short-duration, event-driven inference with API-based models but is poorly matched to multi-container stateful services. Self-managed EC2 maximises control at the cost of undifferentiated heavy lifting — patching, process supervision, recovery. EKS is justified only where Kubernetes expertise and ecosystem already exist. ECS provides managed orchestration — task lifecycle, desired-state reconciliation, health-based replacement — decoupled from the compute layer, which is either Fargate (serverless, no GPU support) or EC2 managed instances (instance-type control including GPU). For API-model-backed containerized workloads Fargate is the default; GPU-bound self-hosted inference forces EC2 managed instances."

**🔁 Interview Q3 (follow-up):** "You said `ECR + EC2` and `ECR + ECS on EC2` both use EC2. Aren't they the same thing?"

**✅ Strong answer:** "No, and it's a genuinely easy confusion. In **ECR + EC2**, the EC2 instance just pulls the image and you run Docker on it yourself — you write the start scripts, you handle a crashed container, you manage recovery. In **ECR + ECS with EC2 managed instances**, ECS does the container-level management *for* those instances: it reads the task definition, starts containers, runs health checks, and replaces failures automatically.

Same underlying hardware, very different amount of work. The second gives you desired-state recovery and configurable autoscaling; the first gives you a server and a to-do list."

**🎯 Standard Interview Answer:** "ECR + EC2 treats the instance as a plain Docker host — image pull and container lifecycle are operator responsibilities, with no desired-state reconciliation. ECR + ECS on EC2 managed instances places the instances under ECS control as cluster capacity, delegating task placement, health-check-driven replacement, and scaling policy to the orchestrator. The distinction is control-plane presence: the latter provides declarative desired-state management, the former is imperative and manual."

---

**🎙️ Interview Q4:** "Explain Fargate versus the EC2 launch type. When does the choice actually matter?"

**✅ Strong answer:** "Fargate is serverless — I declare CPU and memory, and AWS provisions the compute. No instances to patch or scale. EC2 launch type means I run a cluster of instances and I'm responsible for the OS, capacity, and patching.

For most container work Fargate is simpler and I'd default to it. The choice becomes forced in two situations:

1. **GPU** — Fargate doesn't support it. Self-hosting an open-weight model means EC2.
2. **Cost at sustained scale** — Fargate's per-task pricing is convenient but can exceed well-utilised reserved EC2 capacity for steady, predictable load.

**Everyday example:** Fargate is renting a car by the hour — zero maintenance, slightly more per mile. EC2 is owning the car — cheaper if you drive constantly, but you handle the servicing."

**🎯 Standard Interview Answer:** "Fargate abstracts the compute substrate: the task specifies vCPU and memory, and AWS handles provisioning, patching, and capacity — eliminating instance management at a per-task price premium. The EC2 launch type exposes the underlying instances as managed cluster capacity, requiring OS patching and capacity planning but permitting instance-type selection, including GPU-backed families, reserved or spot pricing, and higher utilisation density through bin-packing. The decision is forced by GPU requirements — unsupported on Fargate — and becomes cost-driven at sustained high utilisation, where amortised reserved EC2 capacity outperforms per-task Fargate pricing."

**🔁 Interview Q4 (follow-up):** "You've deployed with an OpenAI API. Your company now wants a self-hosted open-weight model instead. What actually changes?"

**✅ Strong answer:** "Less than people expect. The FastAPI and Streamlit structure, the Docker setup, ECR, ECS, task definitions, CloudWatch logging, and the evaluation harness all stay.

Three things change:
1. **Fargate → ECS on EC2 managed instances**, because you now need a GPU.
2. **A serving layer appears** — Ollama for simplicity, or vLLM when you need throughput. vLLM adds optimisations like KV caching specifically to serve many concurrent users.
3. **The cost model shifts sharply.** GPU instances are billed on what you *reserve*, not what you use — so a 70B-capable GPU serving a small model still costs like a 70B-capable GPU.

The architecture is basically intact; the compute layer and the economics are what move."

**🎯 Standard Interview Answer:** "The application and orchestration layers remain unchanged — container topology, ECR/ECS, task definitions, logging, and evaluation are model-agnostic. The compute layer migrates from Fargate to ECS on EC2 managed instances to obtain GPU capacity, and an inference-serving layer is introduced: Ollama for straightforward local serving, or vLLM where throughput matters, given its continuous-batching and paged-KV-cache optimisations for concurrent request handling. The dominant change is economic: GPU capacity is billed on reservation rather than utilisation, making instance right-sizing and utilisation monitoring materially more important than in the API-backed configuration."

---

**🎙️ Interview Q5:** "How does an ECS deployment actually fit together — ECR, cluster, task definition, service?"

**✅ Strong answer:** "Four pieces with clear jobs:

- **ECR** stores versioned Docker images. That's all it does here.
- **The cluster** is the logical area where workloads run.
- **The task definition** is a versioned blueprint — which image, which command, health checks, ports, CPU/memory, environment variables, secret references, log destination.
- **The service** is the controller that keeps N tasks running and replaces failures. A **task** is one running copy of the blueprint.

**Everyday example:** the task definition is a recipe card; a task is the dish currently cooking; the service is the manager making sure there are always three dishes on the pass, cooking a replacement whenever one is dropped.

Every task-definition edit creates a new **revision**, and deploying a change means updating the service to point at that revision — which also gives you rollback for free, since the old revision still exists."

**🎯 Standard Interview Answer:** "ECR provides the immutable, tagged image artifact store. An ECS cluster is the logical grouping of compute capacity. The task definition is an immutable, versioned specification — container images, resource allocation, port mappings, environment variables, secret references by ARN, health-check definitions, and log configuration. A task is a running instantiation of a specific task-definition revision; a service is the desired-state controller maintaining a target task count, performing health-based replacement and rolling deployments. Because revisions are immutable and retained, deployment is a pointer update from one revision to another, making rollback a symmetric operation rather than a recovery procedure."

---

**🎙️ Interview Q6:** "Where do you put the OpenAI API key, and what's wrong with the obvious approaches?"

**✅ Strong answer:** "It goes in a secrets manager — AWS Secrets Manager here — and the task definition references it by **ARN**, so the container receives it as an environment variable at runtime.

What's wrong with the obvious alternatives:
- **Baked into the image** — anyone who can pull the image has your key, and it's now in every layer of image history.
- **Committed in a `.env` file** — that's the classic way keys end up on GitHub.
- **Stored in CI variables as static credentials** — better, but still long-lived and broadly readable.

The key never appears in the image or the repository. Secrets Manager also supports **automatic rotation** via a Lambda function, so a fresh key is generated periodically instead of one key living forever.

**The failure this causes in practice:** the container needs IAM permission to *read* that secret. If the ECS task execution role lacks `secretsmanager:GetSecretValue` for that ARN, the deploy fails with a permissions error — and this is probably the most common first-deployment failure there is."

**🎯 Standard Interview Answer:** "Credentials are stored in a dedicated secret store — AWS Secrets Manager or equivalent — and injected at runtime via task-definition `valueFrom` references to the secret ARN, never embedded in images, source control, or static CI variables. Image-embedded secrets persist in layer history and are exposed to anyone with pull access; repository-committed secrets are the dominant source of credential leakage. Runtime injection requires the task execution role to hold `secretsmanager:GetSecretValue` scoped to the specific secret ARN — least privilege rather than wildcard — and rotation should be enabled so credential lifetime is bounded. Insufficient IAM scoping on this path is the most frequent initial deployment failure."

**🔁 Interview Q6 (follow-up):** "How would you scope IAM for this, and how do you keep it from drifting?"

**✅ Strong answer:** "A dedicated role per service, scoped to exact resource ARNs rather than wildcards. The ECS task execution role here needs exactly two things: pull from ECR, and read *that one* secret — not all secrets.

For drift, I'd audit periodically with IAM Access Analyzer to find over-permissive or unused grants. And for CI/CD specifically, I'd use OIDC federation so GitHub Actions assumes a role rather than holding long-lived static access keys.

The reason to bother is blast radius: if a credential leaks, the damage is bounded by what that role could reach. 'AdministratorAccess because it was quicker' turns a small incident into a large one."

**🎯 Standard Interview Answer:** "Least privilege is implemented as dedicated per-service roles scoped to explicit resource ARNs, avoiding wildcard resources and broad managed policies such as AdministratorAccess. Permission drift is controlled through periodic review with IAM Access Analyzer to surface unused or over-broad grants. CI/CD authentication should use OIDC federation to assume roles dynamically rather than storing static long-lived access keys in the pipeline, and Secrets Manager access logs should be monitored for anomalous retrieval patterns. The objective is bounded blast radius and attributable access, both of which degrade when roles are shared or over-scoped."

---

**🎙️ Interview Q7:** "Your GenAI app is public. How do you stop someone hammering your backend and running up an OpenAI bill?"

**✅ Strong answer:** "The architectural answer first: **don't expose the backend at all.** In this deployment, the security group opens port 8501 for Streamlit but deliberately leaves port 8000 closed. The frontend calls FastAPI over internal localhost inside the same task, so there's no route from the internet to the API.

**Everyday example:** a restaurant with a public dining room and no street door into the kitchen.

Beyond network isolation, the layers I'd add: rate limiting per client, authentication on the endpoint, request-size and token caps, caching for repeated queries, and billing alarms so runaway spend is noticed in hours rather than at month end."

**🎯 Standard Interview Answer:** "Primary mitigation is network-level: the backend is not assigned an ingress path — the security group permits inbound traffic only on the frontend port, with frontend-to-backend communication over the loopback interface within the shared task. Defence in depth adds authentication and per-principal rate limiting at the ingress, input token and request-size caps to bound per-request cost, response caching for repeated queries, and billing alarms with anomaly detection for spend monitoring. Where frontend and backend are separated into distinct tasks, security-group rules restrict backend ingress to the frontend's security group rather than to CIDR ranges."

---

**🎙️ Interview Q8:** "How would you design this to handle a traffic spike, and how do you think about cost at scale?"

**✅ Strong answer:** "Two scaling directions. **Vertical** makes the machine bigger — more RAM or CPU. **Horizontal** runs more copies — one container becomes five, each serving a share of traffic. For request-driven web workloads horizontal is usually the right answer, and ECS supports scaling task count on metrics like CPU or request count.

For cost, the thing that catches people is that **you pay for what you reserve, not what you use**. The session's example is blunt: pick a GPU capable of running a 70B model, serve a small model on it, and you still pay for the big GPU. Right-sizing matters more than it feels like it should.

The other levers at scale: cache aggressively, since repeated queries are common; route simple requests to cheaper models; and trim context, because with LLMs the unit you're scaling isn't really users — it's **tokens**."

**🎯 Standard Interview Answer:** "Horizontal scaling — increasing task count behind a load balancer with target-tracking policies on CPU, memory, or request-count metrics — is preferred for stateless request-driven inference, with vertical scaling reserved for memory-bound single-instance constraints. Capacity planning for LLM workloads is token-driven rather than user-driven, since cost and throughput scale with tokens processed; for self-hosted inference, GPU throughput is the binding constraint, motivating continuous batching and concurrency-aware serving. Cost control combines right-sizing — reserved capacity is billed irrespective of utilisation — with semantic and exact-match caching, intent-based routing to lower-cost models, and dynamic context trimming. Warm pools mitigate cold-start latency under bursty load."

**🔁 Interview Q8 (follow-up):** "You redeploy and the public IP changes. Is that acceptable in production?"

**✅ Strong answer:** "No — and it's a good illustration of why load balancers exist. In the demo, each new deployment produces a new task with a new public IP, so you copy the new address to reach the app. That's fine for a walkthrough and unacceptable for anything real.

In production you put an Application Load Balancer in front. The ALB has a stable DNS name, and ECS registers and deregisters tasks with it as they come and go. Users hit one unchanging address, the ALB spreads traffic across healthy tasks, and rolling deployments become invisible rather than a URL change."

**🎯 Standard Interview Answer:** "Task-level public IPs are ephemeral and re-assigned per task, making them unsuitable as a client-facing endpoint. Production topology places an Application Load Balancer in front of the ECS service, with the service registered to a target group; ECS handles registration and deregistration through task lifecycle events, and the ALB provides a stable DNS endpoint, health-check-based routing, and connection draining during rolling deployments. This also decouples deployment from client configuration, enabling blue-green and canary release strategies."

---

**🎙️ Interview Q9:** "What runs before a deploy, and what belongs in CI/CD?"

**✅ Strong answer:** "Three gates before anything ships:

1. **Unit tests with the LLM mocked.** Tests must be fast, repeatable, and must not make paid model calls. They cover the deterministic parts — does the health endpoint respond, is structured output shaped correctly, is blank input rejected, is missing config caught.
2. **A linter** for code-level mistakes — unsorted imports, a function that doesn't exist in the library.
3. **An evaluation run** against a labelled dataset, reporting accuracy. This is the AI-specific gate the other two don't cover: tests tell you the service *works*, evaluation tells you the answers are *good*.

In CI/CD, all of that runs on push, and a failure fails the pipeline so the deploy never happens. Then the pipeline builds the image, pushes to ECR, registers a new task-definition revision, and updates the service. GitHub Actions automates exactly the steps done manually in the console; Terraform does the same for the infrastructure itself."

**🎯 Standard Interview Answer:** "Pre-deployment gating comprises deterministic unit and integration tests with external model calls mocked for speed, repeatability, and cost avoidance; static analysis and linting; and a model-quality evaluation against a labelled dataset producing accuracy metrics. The first two validate service correctness, the third validates output quality — a distinction specific to ML systems, where a fully-passing test suite is compatible with unacceptable model performance. In CI/CD these execute as pipeline gates on push, with failure blocking promotion. The deployment stage builds and tags the image, pushes to ECR, registers a new task-definition revision, and updates the ECS service, with image scanning and progressive delivery — canary or blue-green — for production. Infrastructure is managed declaratively through Terraform rather than console operations, making environments reproducible and reviewable."

---

**🎙️ Interview Q10:** "It's live and a user reports a wrong answer. How do you debug it?"

**✅ Strong answer:** "Logs first. Each container streams to CloudWatch with a stream prefix identifying which one it came from — `api` versus `frontend` — so I can see which layer the request reached and what it returned. Retention is configurable; the demo uses three days, production would be longer.

Then I separate the failure classes, because they need different fixes:
- **Did the request even arrive?** If not, it's networking or the security group.
- **Did the container die?** Health-check failures and ECS restarts show up as task-level events.
- **Did the API return an error?** The status code tells me which class — 422 bad input, 503 upstream unavailable, 502 malformed model output.
- **Did the model return a valid-but-wrong answer?** That's not an infrastructure problem at all; it goes to the evaluation harness.

That last split is the one people miss. A wrong answer with a 200 status is a *model quality* issue, and no amount of log-reading fixes it."

**🎯 Standard Interview Answer:** "Diagnosis begins with centralised logs — per-container CloudWatch streams with distinguishing prefixes, retained per policy — correlated with ECS task-level events for health-check failures and replacements. Triage separates infrastructure failures from model-quality failures: absent requests indicate ingress or security-group misconfiguration; task churn indicates health-check or resource issues; non-2xx responses are classified by status semantics (422 validation, 503 upstream unavailability, 502 malformed upstream response). A semantically incorrect response returned with 200 is a model-quality regression and is addressed through the evaluation pipeline rather than infrastructure debugging. Production maturity adds request-level tracing with correlation IDs spanning frontend, backend, and model call, plus latency and token-cost metrics per request."

---

**What interviewers are really scoring for, across all of the above:**
- Whether you reach for the right *term* naturally — task definition, revision, launch type, execution role, least privilege — rather than describing around it
- Whether you can name a **decision rule** (GPU need → EC2 managed instances) instead of listing services without a basis for choosing
- Whether secrets, IAM scoping, and network exposure come up **unprompted** — production awareness is the main thing separating 4-5 years from 1-2
- Whether you distinguish **infrastructure failure** from **model-quality failure**, and route each to the right remedy
- Whether cost surfaces as a real engineering constraint — reserved-versus-used, right-sizing, caching — rather than an afterthought
- Whether you know what's **manual here but automated in production** (CI/CD, Terraform, load balancers) and can say why that matters

**Sources consulted while calibrating this section:**
- [LLM Interview Questions and Answers (2026) — InterviewBit](https://www.interviewbit.com/llm-interview-questions-answers/)
- [MLOps Engineering Interview Questions and Answers — Dr. Sanjay Kumar](https://skphd.medium.com/mlops-interview-questions-and-answers-0e25e2200dfc)
- [LLMOps: Docker Practices for Large Language Model Deployment — DZone](https://dzone.com/articles/llmops-docker-practices-llm-deployment)
- [Your First Containerized Machine Learning Deployment with Docker and FastAPI — MachineLearningMastery](https://machinelearningmastery.com/your-first-containerized-machine-learning-deployment-with-docker-and-fastapi/)
- [LLM Deployment with FastAPI + Docker + uv in 2026 — PyInns](https://www.pyinns.com/python/llm-and-generative-ai/llm-deployment-fastapi-docker-uv-python-2026-complete-guide-best-practices)
- [Master AWS ECS, EC2 and Fargate — Interview Preparation Questions and Answers](https://medium.com/@_____129/master-aws-ecs-ec2-and-fargate-interview-preparation-questions-and-answers-bbf37450a876)
- [AWS Interview Questions and Answers (2026) — Devinterview.io](https://github.com/Devinterview-io/aws-interview-questions)
- [Top 50+ AWS ECS Interview Questions & Answers — Cloud Soft Solutions](https://cloudsoftsol.com/aws/top-50-aws-ecs-interview-questions-answers-latest-2025/)
- [Generative AI System Design Interview (questions, tips, prep) — IGotAnOffer](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- [GenAI & LLM System Design Interview Guide (2026) — PracHub](https://prachub.com/resources/genai-llm-system-design-interview-guide-2026)
- [GenAI System Design Interview — Worked Examples & Framework (2026) — MyEngineeringPath](https://myengineeringpath.dev/genai-engineer/system-design-interview/)
- [How would you design the system architecture for deploying an LLM in production? — DesignGurus](https://www.designgurus.io/answers/detail/how-would-you-design-the-system-architecture-for-deploying-a-large-language-model-llm-in-production)
- [50+ DevSecOps Interview Questions and Answers for 2026 — Practical DevSecOps](https://www.practical-devsecops.com/devsecops-interview-questions/)
- [Secrets Management for LLM Tools: Don't Let Your OpenAI Keys End Up on GitHub — DEV Community](https://dev.to/parth_sarthisharma_105e7/secrets-management-for-llm-tools-dont-let-your-openai-keys-end-up-on-github-38c0)
- [Cloud Engineer Interview Questions: 10 Technical Questions — Wiz](https://www.wiz.io/academy/cloud-careers/cloud-engineer-interview-questions)

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

# Week 5 — Deployment and Evaluation of LLMs

**A complete, self-contained study reference.** Everything Week 5 covers — taking a GenAI application off your laptop and onto AWS, containerising it, choosing a hosting platform, serving open-weight models, and evaluating the whole thing — is explained here from first principles, with worked examples and the 2026 state of each tool.

---

**The one-sentence version:**

> Weeks 1–4 produced code that runs on *your* machine. Week 5 turns that code into a container, puts it somewhere that stays switched on, decides who runs the model, and builds the machinery that notices when the answers are wrong.

**The two analogies that run through this whole document**

🍽️ **For deployment — a restaurant kitchen.** Your code is a *recipe*. **Docker** packs the recipe plus every ingredient into a sealed meal-kit box so it cooks identically in any kitchen. **ECR** is the warehouse where those boxes are stored, each with a version label. **ECS** is the shift manager — holds the master instruction sheet, decides how many meals to cook, restarts anything that burns. **Fargate** is the cook, using a kitchen you never have to own or clean. Almost every confusing AWS service below is one of those roles.

🎓 **For evaluation — assessing a student.** A *benchmark* is a standardised exam: comparable across everyone, easy to cram for. *Human evaluation* is a teacher reading the actual essay — slow, expensive, and the only thing that catches "technically correct but misses the point." *LLM-as-judge* is a senior student grading juniors: fast and scalable, with their own blind spots. *Adversarial testing* is the trick question designed to catch someone who memorised without understanding.

**Why the two halves belong in one week.** Deployment answers *"does the service stay up?"*. Evaluation answers *"are the answers any good?"*. A GenAI system can pass one perfectly and fail the other completely — a 0.95 faithfulness score means nothing if p99 latency is two minutes, and 50 ms responses mean nothing if the content is invented. Week 5 is where you learn that these are two separate jobs and you own both.

---

## Contents

| Part | What it covers |
|---|---|
| **I** | From laptop to server — the fundamentals |
| **II** | Docker and Docker Compose |
| **III** | AWS — the nine architectures, EC2, and ECS/Fargate |
| **IV** | Hosting platforms — Bedrock, HF Endpoints, Cerebrium |
| **V** | Model serving and formats — GGUF, llama.cpp, Ollama, vLLM |
| **VI** | LLM evaluation |
| **VII** | What changed since the course notes (2026) |
| **VIII** | Rapid-fire interview recall |

---
---

# Part I — From Laptop to Server

## 1. What "deployment" actually means

Your app works beautifully — on your laptop, for exactly one person: you. Close the lid and it's gone. Deployment is the act of moving it onto a computer that someone else rents out, keeps switched on, and connects to the internet.

```
BEFORE                                AFTER
┌──────────────┐                      ┌──────────────────────┐
│ your laptop  │                      │ a box in Mumbai      │
│ localhost    │  ← only you          │ 13.234.x.x:8080      │ ← anyone with the link
│ :8000        │                      │ always on            │
└──────────────┘                      └──────────────────────┘
```

Everything in Parts I–III is the mechanics of that one move. AWS is the example, but the *shape* of the process — pick a region, get a machine, get the code there, install dependencies, run it, open the port — transfers directly to Azure, GCP, or a rack in your own building.

**One line:** deployment is moving your code onto a computer someone else keeps switched on, and every cloud provider is a different set of buttons for the same five steps.

---

## 2. The three stacks

Keeping these separate is what stops the AWS console from feeling like an undifferentiated wall of services.

| Stack | What lives here | Concretely |
|---|---|---|
| **Application stack** | The thing you actually built | Python, FastAPI, Streamlit |
| **Deployment stack** | What packages and runs it | Docker, ECR, ECS, Fargate |
| **Operational stack** | What keeps it safe and observable | Secrets Manager, CloudWatch, IAM |

**A note on roles, worth being honest about.** If your job leans toward *building* solutions (RAG, agents, fine-tuning), you'll contribute to the architecture rather than own it — a DevOps or platform engineer handles the cloud design. If your job leans toward *deploying*, that's where you go deep. Either way the expectation is not "own all of AWS." It is **"understand enough to know why each service was chosen."** That sentence is also the honest answer to most deployment interview questions at 4–5 years' experience.

**One line:** application stack = what you wrote, deployment stack = what runs it, operational stack = what keeps it alive and auditable.

---

## 3. The reference application — the shape of a production GenAI service

Week 5 uses a deliberately *simple* app so attention stays on the infrastructure: a **customer-support triage tool**. A user message comes in; the app returns a category, an intent, a priority, and a reply.

### File layout

```
app/
├── main.py            FastAPI entry point — routes, lifespan, connections
├── llm_service.py     the actual OpenAI call + structured parsing
├── schemas.py         request/response models (Pydantic)
├── validation.py      input guards on incoming data
├── prompts.py         prompt templates, versioned if you have many
├── config.py          a Settings class that reads environment variables
├── logging_config.py  how logs get written
└── evaluation.py      scores the triage against a labelled dataset
frontend/              the Streamlit UI
tests/                 pytest suite
data/                  evaluation dataset + output
docker-compose.yml
Dockerfile
```

> 📦 **Why separate these at all?** Because `config.py` reading environment variables is exactly what lets the *same* code run on your laptop with a `.env` file and on AWS with secrets injected by Secrets Manager — **with no code change**. That single design choice is what makes the deployment later so uneventful. It is the most important architectural decision in the whole application.

### The config module, in full

```python
from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )

    app_name: str = "OpenAI Customer Support Classifier"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: SecretStr | None = None          # SecretStr -> never printed by repr()
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    openai_max_retries: int = Field(default=2, ge=0, le=5)
    max_input_chars: int = Field(default=4000, ge=100, le=20_000)

@lru_cache
def get_settings() -> Settings:
    return Settings()          # one cached settings object per process
```

Three details worth copying:

- **`SecretStr`** — Pydantic wraps the value so an accidental `print(settings)` or a logged traceback shows `SecretStr('**********')` instead of your key. Free protection against the most common leak.
- **`Field(gt=0, le=120)`** — bounds on the timeout mean a typo in an environment variable fails at startup, not at 2am under load.
- **`@lru_cache`** — reading and validating environment variables once per process, not once per request.

### The three endpoints

| Endpoint | Purpose |
|---|---|
| `/health` | Is the service alive? Used by container health checks, not humans |
| `/generate` | The real business endpoint — takes a message, returns triage JSON |
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
Call the model (structured output) ── key missing / timeout? → 503
     │                                malformed structure?   → 502
     ▼
Validate category/intent/priority
     │
     ▼
Return output JSON
```

**The bit worth internalising is the error codes.** Different failure classes get *different* codes: `422` for bad input, `503` for connection or timeout failures, `502` for a structured-output or upstream API failure. That's not pedantry. **When something breaks at 2am, the status code is the first thing that tells you whose problem it is.** A blanket `500` tells you nothing.

### Structured output, and how errors get classified

```python
class LLMServiceError(RuntimeError): ...
class LLMRateLimitError(LLMServiceError): ...
class LLMUnavailableError(LLMServiceError): ...

async def generate(self, message: str) -> SupportResponse:
    try:
        response = await self.client.responses.parse(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=build_user_prompt(message),
            text_format=SupportResponse,        # the Pydantic model IS the schema
        )
    except RateLimitError as exc:
        raise LLMRateLimitError("rate limit reached") from exc
    except (APIConnectionError, APITimeoutError) as exc:
        raise LLMUnavailableError("temporarily unavailable") from exc
    except APIError as exc:
        raise LLMServiceError("request failed") from exc

    parsed = response.output_parsed
    if parsed is None:
        raise LLMServiceError("no structured response returned")
    return parsed
```

The pattern here is worth naming explicitly, because it generalises to every LLM-backed service:

1. **The Pydantic schema is passed to the model**, so the provider enforces the shape server-side rather than you regex-parsing a JSON blob out of prose.
2. **Provider exceptions are translated into your own exception types** at the boundary. The route layer then maps *your* exceptions to status codes and never imports the OpenAI SDK. Swap the provider and the routes don't change.
3. **`output_parsed is None` is treated as a failure**, not as `None` flowing downstream. Structured output can come back empty; a defensive check converts a silent bug into a loud 502.

### The response schema — enums, not strings

```python
class Category(str, Enum):
    ORDER = "ORDER"; PAYMENT = "PAYMENT"; ACCOUNT = "ACCOUNT"
    PRODUCT = "PRODUCT"; OTHER = "OTHER"

class SupportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")     # unknown fields are rejected
    category: Category
    intent: Intent
    priority: Priority
    reply: str = Field(min_length=1, max_length=1000)
```

> 🔒 **Why `extra="forbid"` matters.** Without it, a model that invents an extra field quietly passes validation and that field flows into your database. With it, the invention is a validation error you see immediately. Enums do the same job for values: the model cannot return `"urgent-ish"` as a priority, because `URGENT` is the only thing that parses.

**One line:** keep config in one place, validate at the boundary with enums and `extra="forbid"`, translate provider errors into your own types, and give each failure class its own status code — those four choices are what make a service *deployable* rather than just *runnable*.

---

## 4. Quality gates before you deploy

Three checks run before anything touches AWS. This is the part most people skip, and the part that separates "I deployed something" from "I ship things."

### Gate 1 — `pytest`, with the LLM mocked

Tests must be **fast, repeatable, and free**. Mocking the model call is deliberate, not lazy: a test suite that makes paid API calls is a test suite nobody runs.

Coverage targets the boring-but-fatal cases:

| Test | Catches |
|---|---|
| Health endpoint responds | The container starts at all |
| Structured output has the right shape | Schema drift after a prompt or model change |
| Blank input is rejected | The most common malformed request |
| Missing config is caught | Deploying without the API key set |
| Unexpected fields don't crash it | Clients sending extra JSON |

> 🧪 **Why a `tests/` folder rather than scattered asserts:** you write many small test functions, then type `pytest` once. It discovers the folder, finds every test function, runs them all, and reports pass/fail/warnings together. It's consolidation, not magic.

### Gate 2 — `ruff`, a linter

Catches coding-level mistakes and style problems: unsorted imports, odd indentation, a function that doesn't exist in the library you imported. Warnings are advisory; a genuinely wrong function reference is an error you want *before* deploy, not in a container log.

### Gate 3 — a live evaluation run

`evaluation.py` scores the triage against a labelled dataset and reports two numbers:

| Metric | Meaning | This app's score |
|---|---|---|
| **Field accuracy** | Of all individual fields across all examples, how many were right? | **0.875** |
| **Exact-match accuracy** | How many examples got *every* field right simultaneously? | **0.625** |

**The gap between those two numbers is the interesting part, and it generalises.** 87.5% of fields correct but only 62.5% of examples fully correct means most errors are *isolated* — one field wrong in an otherwise-right answer — rather than whole examples collapsing. With three graded fields per example, independent errors would predict roughly 0.875³ ≈ 0.67 exact-match; the observed 0.625 sits close to that, which tells you errors are largely independent rather than clustering on a few hopeless examples.

> 📉 **The same compounding arithmetic appears everywhere in GenAI.** A six-stage RAG pipeline where each stage is 90% reliable is 0.9⁶ ≈ 53% reliable end to end. Per-component accuracy always looks better than the number your user experiences. Quote whichever one is honest for the question being asked, and know the difference.

> ⚠️ **The rule, stated plainly:** every test should pass before code leaves your machine. With CI/CD, a failing test fails the pipeline and the deploy never happens. Shipping with red tests isn't a shortcut — it's a decision to find out in production.

**One line:** mocked tests for behaviour, a linter for code smells, and an evaluation run for actual model quality — the first two tell you the service *works*, the third tells you the answers are *good*, and only all three together are a gate.

---
---

# Part II — Docker and Docker Compose

## 5. Docker: the image, the container, the Dockerfile

**The problem Docker solves** is "works on my machine." Your laptop has Python 3.12, a particular OpenSSL, and forty libraries at exact versions. The server has none of that. Docker bundles the app, its runtime, and every dependency into one immutable artifact that runs identically anywhere.

> 📦 **Analogy:** it's the difference between mailing someone a recipe and mailing them a sealed meal kit. The recipe assumes their kitchen already has the ingredients. The meal kit assumes nothing.

**Image vs container:** the image is the recipe on disk. The container is the dish, actually cooking. One image → many containers.

### The Dockerfile, line by line

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app app ./app
COPY --chown=app:app frontend ./frontend
COPY --chown=app:app data ./data

USER app

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

| Instruction | What it does |
|---|---|
| `FROM python:3.12-slim` | Minimal Linux + Python 3.12. `slim` strips docs and build tools (~150 MB vs ~1 GB) — **and has no `curl`**, which is why the health checks below use Python instead |
| `ENV PYTHONUNBUFFERED=1` | **The important one.** Python buffers stdout by default; in a container that means logs sit in memory and *vanish on crash*. This forces them out so CloudWatch actually receives them |
| `ENV PYTHONDONTWRITEBYTECODE=1` | Skip `.pyc` files — pointless in a disposable container |
| `ENV PIP_NO_CACHE_DIR=1` | Don't keep pip's download cache, which would only bloat the image |
| `WORKDIR /app` | Every later command runs from `/app` |
| `RUN groupadd … useradd … app` | Create a **non-root** user. Containers run as root by default, so an exploited app would have root inside the container |
| `COPY requirements.txt .` then `RUN pip install` | ⭐ See below — this ordering is deliberate |
| `COPY --chown=app:app …` | Copy source owned by `app`, not root. Note what's **not** copied: `tests/`, `.env`, `docs/` — secrets never enter the image |
| `USER app` | Switch to the unprivileged user before the app runs |
| `EXPOSE 8000 8501` | **Documentation only.** Declares which ports the image listens on — it opens no firewall and publishes nothing |
| `CMD [...]` | The *default* startup command. `--host 0.0.0.0` = listen on all interfaces, without which nothing outside the container could reach it |

### ⭐ Layer caching — the classic interview question

Docker caches each instruction as a layer and reuses the cache when that instruction's inputs haven't changed.

```
Edit app/main.py       → requirements.txt unchanged → pip layer CACHED → build ~2s
Edit requirements.txt  → pip install re-runs                          → build ~60s
```

Copy code and requirements together and **every one-character code edit reinstalls every dependency.** The rule generalises: *order Dockerfile instructions from least-frequently-changed to most-frequently-changed.*

### `--proxy-headers`, briefly

Behind a load balancer, the app sees the balancer's IP rather than the user's, and sees `http` even when the user connected over `https`. `--proxy-headers` tells uvicorn to trust `X-Forwarded-For` and `X-Forwarded-Proto` and report the real values. Without it, generated redirect URLs come out as `http://` and your logs record one client IP for every request.

**One line:** the Dockerfile is a build recipe — base image, container-appropriate env settings, a non-root user, dependencies cached separately from code, and a default command — and `docker build` runs it to produce an immutable, versioned artifact.

---

## 6. Docker Compose: more than one service

The app becomes **two running services** — FastAPI on `8000`, Streamlit on `8501`. Without Compose you'd start each container by hand, every time, with its own long command.

> 🧰 **Analogy:** running containers individually is like starting your dishwasher, oven, and kettle by walking to each one and pressing its button. Docker Compose is the single "start dinner prep" button that does all three in the right order. Nothing new happens — you just stop doing it manually.

```yaml
services:
  api:
    build: .
    image: openai-llm-app:local
    env_file: [.env]
    environment:
      APP_ENV: local-docker
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  frontend:
    image: openai-llm-app:local        # the SAME image
    env_file: [.env]
    environment:
      API_BASE_URL: http://api:8000    # service name as hostname
    command:
      - streamlit
      - run
      - frontend/streamlit_app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    ports:
      - "8501:8501"
    depends_on:
      api:
        condition: service_healthy     # wait for HEALTHY, not just started
    restart: unless-stopped
```

### Five things in that file worth understanding

**1. `ports: "8501:8501"` is `HOST:CONTAINER`.** "Take port 8501 on my laptop and forward it into the container's port 8501." The two numbers need not match — `"9000:8501"` means you browse to `localhost:9000` while the container still runs on 8501 internally. **Left number = yours, right number = the container's.**

**2. `API_BASE_URL: http://api:8000` — why `api`, why 8000.** Compose gives every service an internal DNS name equal to its service name, so `api` resolves to that container. Port 8000 because that's where uvicorn binds.

> **The subtle part:** this traffic never uses the published `"8000:8000"` mapping. That mapping exists so *you* can reach the API from your laptop. The frontend talks **container-to-container** on Docker's internal network, straight to the container's own port.

**3. The health check uses Python, not `curl`** — because `python:3.12-slim` has no `curl`. A `curl`-based health check on a slim image fails forever with "executable not found" and the container dies in a restart loop. A real and frequently-hit trap.

**4. `depends_on: condition: service_healthy`** is stronger than plain `depends_on`, which only waits for the container to *start*. Waiting for *healthy* means Streamlit doesn't come up and immediately fail its first API call.

**5. `start_period: 10s`** is a grace window: health-check failures during startup don't count toward `retries`. Without it, a slow-booting app gets killed before it ever becomes healthy.

### ❗ The distinction people get wrong: local vs AWS exposure

| | Local (Compose) | AWS (ECS) |
|---|---|---|
| Port 8501 | published, reachable | allowed inbound — the only open port |
| Port 8000 | **published, reachable** | **no inbound rule — unreachable from the internet** |

Locally, exposing 8000 is deliberate: it lets you open FastAPI's `/docs` and `curl /health` while developing. **Only on AWS does the backend become private.** Saying "docker-compose keeps the API internal" is a common and wrong claim.

**One line:** Docker makes one service portable; Compose makes a *set* of services start together as one unit, with service names as hostnames and health-gated startup ordering.

---

## 7. The one-image-two-commands trick

**One image, not two** — and this is the central trick of the reference app.

```
        ONE `docker build`
               │
               ▼
     openai-llm-app:local              ← a single image, pushed to ECR once
               │
       ┌───────┴───────┐
       ▼               ▼
  container "api"   container "frontend"
  uses the CMD →     overrides it →
  uvicorn :8000      streamlit :8501
```

**Why it works:** the image contains *both* codebases — `COPY app ./app` **and** `COPY frontend ./frontend`. Everything for either role is already inside; the only runtime difference is which command you give it.

> 🧰 **Analogy:** one toolbox holding both a hammer and a screwdriver. Hand the same box to two workers, tell one "hammer" and the other "screwdriver."

**Could it have been two images?** Yes — two Dockerfiles, two ECR repos, two builds. The honest trade-off: this single image carries Streamlit into the API container and FastAPI into the UI container, neither of which uses the other. **Production systems whose components release or scale independently normally build two separate, smaller images.** One image is right for a teaching lab and for small services that always ship together; two is right the moment the halves have different release cadences or scaling profiles.

**One line:** one image built and pushed once, run twice with different commands — because `CMD` is only a default you can override; two images is the production choice when the halves need to ship independently.

---

## 8. Production Dockerfile practices (2026)

The Dockerfile above is correct and teachable. Here is what a 2026 production version adds.

### Multi-stage builds

Build tools (compilers, headers, pip's machinery) are needed to *install* dependencies and never needed to *run* them. A multi-stage build installs in one stage and copies only the result into a clean runtime stage.

```dockerfile
# ---- stage 1: build ----
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.4 /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# ---- stage 2: runtime ----
FROM python:3.12-slim
RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app app ./app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

Reported effect: multi-stage builds typically cut 60–80% of the removable weight, with one measured FastAPI case going from 306 MB to 223 MB ([OneUpTime](https://oneuptime.com/blog/post/2026-02-08-how-to-containerize-a-fastapi-application-with-docker/view), [digon.io](https://digon.io/en/blog/2025_07_28_python_docker_images_with_uv)).

### `uv` instead of `pip`

[`uv`](https://docs.astral.sh/uv/) (from Astral, the `ruff` authors) is a Rust-based installer that is dramatically faster than pip and resolves from a lockfile. Two rules when using it in a Dockerfile:

- **Pin the version** — `ghcr.io/astral-sh/uv:0.12.4`, never `:latest`, or your "reproducible" build isn't.
- **`uv sync --frozen`** — fail if the lockfile doesn't match `pyproject.toml`, rather than silently resolving something new inside a build.

### Workers: uvicorn alone, or Gunicorn + uvicorn workers?

| Setup | When |
|---|---|
| **One uvicorn process per container** | ✅ The container-orchestrator default. ECS/Kubernetes already handles "run N copies and restart the dead ones" — a second process supervisor inside the container duplicates that and hides crashes from the orchestrator |
| **Gunicorn with `uvicorn.workers.UvicornWorker`** | When you are *not* using an orchestrator and want several workers on one VM, or you need per-worker recycling (`--max-requests`) to paper over a leak |

Rough sizing when you do run multiple workers: **2–4 × CPU cores** for I/O-bound work, and budget **~50–100 MB of memory per worker** ([LogicLoop](https://www.logiclooptech.dev/fastapi-in-production-the-complete-deployment-guide-docker-workers-scaling-and-best-practices/)). For an LLM proxy service the work is almost entirely *waiting on the network*, so async concurrency inside one process does most of the job and extra workers buy less than people expect.

### The rest of the production checklist

| Practice | Why |
|---|---|
| Pin base image by digest (`python:3.12-slim@sha256:…`) | Tags move; digests don't |
| `.dockerignore` for `.git`, `.venv`, `.env`, `tests/`, `data/` | Smaller build context, and a second line of defence against shipping secrets |
| Non-root `USER` | Already in the lab Dockerfile — keep it |
| Image scanning in CI (Trivy, Grype, ECR scan-on-push) | CVEs in base layers are the most common finding |
| A real orchestrator health check | Free self-healing; see §12 |
| Never `ENV OPENAI_API_KEY=...` | It persists in image layer history forever |

**One line:** the teaching Dockerfile is correct; production adds a multi-stage build, a pinned lockfile-based installer, a pinned base digest, image scanning, and one process per container so the orchestrator — not a supervisor inside the image — owns restarts.

---
---

# Part III — AWS

## 9. The AWS vocabulary you actually need

Plain definitions first. Everything after this section assumes them.

**Region & availability zone.** AWS has data centres worldwide, grouped into regions (`ap-south-1` = Mumbai, `ap-south-2` = Hyderabad). An EC2 instance is a real machine in a real building. Deploy near your users — choosing Virginia because it was the default means every request from an Indian user crosses an ocean and back. An **availability zone** is one isolated data centre within a region; teams also run backup capacity in a *second region* so a regional outage doesn't take the product down.

**EC2 (Elastic Compute Cloud).** A rented virtual computer. Renting a PC in a data centre and getting the keys.

**S3.** Bucket storage for files, reachable by other AWS services. A shared hard drive in the cloud.

**Lambda.** Serverless compute — you supply a function, AWS runs it, no server to manage. A vending machine: it only does something when someone presses a button.

**ECR (Elastic Container Registry).** Private storage for Docker images, each tagged with a version label. That's its entire job: hold the image so something else can fetch it. Docker Hub is the public equivalent.

**ECS (Elastic Container Service)** — the orchestrator, with four nested concepts:

```
Cluster            the area where workloads run
  └── Service      the controller — keeps N tasks running, restarts failures
        └── Task   a running copy of the blueprint
              └── Task definition   the versioned blueprint itself
```

The **task definition** is the important one. It specifies which image to use, which command to run, health checks, exposed ports, CPU and memory, environment variables, secret references, and where logs go. Every edit creates a new **revision** — 1, 2, 3 — so you always know which version is live and can roll back.

> 📋 **Analogy:** the task definition is a recipe card; a task is the dish actually being cooked from it; the service is the manager making sure there are always three dishes on the pass, cooking a replacement whenever one is dropped. Editing the recipe doesn't change the dish already on the stove — which is exactly why updating a service means pointing it at the *new revision*.

**Fargate.** The serverless compute layer that reads a task definition and executes it. No servers to manage. **No GPU.**

**Secrets Manager.** Where your API key lives. Containers fetch it at runtime by ARN. Supports **automatic rotation** via a Lambda function, so no single key sits around indefinitely.

**CloudWatch.** Log storage with a configurable retention window. Each container streams logs here with a prefix identifying which container they came from.

**IAM (Identity and Access Management).** Users, roles, policies. A **role** grants a *service* permission to call other services — the ECS task execution role is what lets ECS pull from ECR and read from Secrets Manager.

> 🔑 **Why scoping matters, in two words:** *traceability* (when something breaks you can tell who or what did it) and *blast radius* (a compromised account can only touch what it was granted).

**VPC (Virtual Private Cloud).** Your isolated network. Where data-residency rules get enforced.

**Security groups.** Firewall rules — which IPs may reach which ports. **Inbound rules are the ones that matter**; they are deny-by-default.

**ALB (Application Load Balancer).** One stable public address that spreads requests across however many healthy copies are running, and stops sending to sick ones.

> 🎓 **The load-balancer example everyone recognises:** a university results website that crashes the instant results are published and every student refreshes at the same second. That's exactly the failure a load balancer exists to prevent.

---

## 10. The nine deployment architectures, and how to choose

There are many ways to run the same container on AWS, sorted loosely by **how much of the machine you have to babysit**. Moving down the list trades **control** for **convenience**.

```
YOU MANAGE MORE                                    AWS MANAGES MORE
◄─────────────────────────────────────────────────────────────────►

1 Simple EC2                                            8 Lambda
   2 ECR+EC2                                     3 App Runner
      6 ECS on EC2 / Managed Instances        5 ECS Fargate
         7 EKS                          4 Elastic Beanstalk
                                             9 SageMaker
```

### 1️⃣ Simple EC2

Rent a Linux box, SSH in, `git clone`, `pip install`, `uvicorn`, open a port. Done.

> 🏠 **Renting an empty flat and moving in yourself.** Furniture, plumbing, security: yours.

**What that costs you:** at 3am the process crashes and **nothing restarts it**. A security patch comes out — you install it. Traffic doubles — you manually resize and take downtime doing it.

**Good for:** your first deployment, an internal demo, and learning why every other option exists.

### 2️⃣ ECR + Docker on EC2

Same rented box, but you `docker pull` your image from ECR and `docker run` it instead of installing Python by hand.

> 🏠 **Same flat — but your furniture arrives pre-assembled in a sealed crate.**

**The gain over option 1:** no more "works on my machine." **What you still own:** ⚠️ **there is no orchestrator here.** Container dies → it stays dead. *You* are the orchestrator, manually. This is, paradoxically, the container option with the *least* automation.

### 3️⃣ AWS App Runner

Point it at your ECR image. It gives you an HTTPS URL, autoscaling, and health checks. No cluster, no networking, no task definition.

> 🏨 **A serviced apartment.** Walk in, everything works, you touch nothing.

**Two catches.** *"Fit must be checked"*: it expects **one** container serving HTTP on **one** port — a two-container app that needs private internal traffic is awkward. *"Pricing must be checked"*: it bills for provisioned memory even while idle, so a low-traffic service can cost more than Fargate.

**Good for:** a single stateless FastAPI microservice that just needs a public HTTPS URL fast. **This is the fastest path to HTTPS on AWS** — worth remembering, because the Week 5 lab deliberately skips HTTPS.

### 4️⃣ Elastic Beanstalk

Upload code (or a Dockerfile). Beanstalk quietly creates EC2 instances, a load balancer, an autoscaling group, and health monitoring for you — and you can still open the hood.

> 🚚 **A moving service.** They pack and drive, but it's still your truck and your stuff.

**Reality check:** this is the *older* AWS answer. Most new container work goes to Fargate or App Runner. Worth recognising — you'll meet it in legacy systems.

### 5️⃣ ECR + ECS Fargate ⭐ — what the lab uses

Push image to ECR → write a task definition → ECS runs it on Fargate. **No EC2 instance ever appears in your account.**

> 🚕 **Uber instead of owning a car.** It shows up, does the job, disappears. You never think about the engine.

**The division of labour — memorise this, it's an interview staple:**

| Piece | Role | Four words |
|---|---|---|
| **ECR** | storage | stores the image |
| **Task definition** | blueprint | declares what runs |
| **ECS** | control plane 🧠 | decides and watches |
| **Fargate** | data plane 💪 | provisions and runs |

**Trade-offs:** more AWS concepts than one VM (ECR, IAM roles, Secrets Manager, CloudWatch, security groups, VPC subnets, cluster, task definition, service) — and ⚠️ **no GPU**.

### 6️⃣ ECS on EC2 / ECS Managed Instances

Identical ECS concepts, but the containers land on **EC2 instances** instead of invisible Fargate capacity.

> 🚗 **Uber vs. hiring a driver for your own car.** Same experience in the back seat — but the car, the fuel, and the servicing are yours.

| Reason to choose it | Detail |
|---|---|
| **GPUs** | The big one. Serving your own model? Fargate can't. This can (`g5.xlarge`, `g6e`, etc.) |
| **Cost at sustained scale** | Steady 24/7 load is cheaper on Reserved/Spot EC2 than per-second Fargate |
| **Special hardware** | Huge RAM, local NVMe, ARM/Graviton |
| **Privileged containers / eBPF agents** | Security and observability agents that Fargate's isolation model forbids |

**ECS Managed Instances** (see Part VII) is the newer middle ground: real EC2 instances with GPU access, but AWS handles patching and lifecycle.

### 7️⃣ Amazon EKS — managed Kubernetes

AWS runs the Kubernetes control plane; you define Deployments, Services, Ingresses, ConfigMaps in YAML.

> 🏗️ **Hiring a full construction crew with its own project-management system.** Enormously capable. Also a whole discipline to learn.

**Why it exists:** Kubernetes is the only option here that's **cloud-portable**. The same manifests run on EKS, GKE, AKS, or on-premises. That's the real argument — not features.

> ⚠️ **This is the only row where Kubernetes appears.** Options 2, 5, and 6 are all containers with *no* Kubernetes anywhere. People conflate "containers" with "Kubernetes" constantly; they're separate things.

**The honest interview answer:** *"For one app with two containers, EKS is significant complexity for no benefit. It earns its cost when many teams share a platform, or when portability across clouds is a hard requirement."*

### 8️⃣ Lambda + API Gateway

Write a function. API Gateway turns an HTTP request into a function call. Nothing runs when nobody's asking.

> 🚖 **Calling a cab per trip** — versus options 1–7, where a car sits parked costing you money.

| Problem for a GenAI web app | Why |
|---|---|
| **Streamlit doesn't fit** | Streamlit holds a **persistent connection** and per-user session state. Lambda is one-request-in, one-response-out. Fundamentally incompatible |
| **Long model calls** | Lambda caps at 15 minutes, and API Gateway cuts off at ~**30 seconds**. A slow generation can blow that |
| **Cold starts** | Idle function → AWS builds the environment from scratch → 1–3 second delay on the first request |

**Where Lambda *is* perfect:** a PDF lands in S3 → Lambda chunks it, embeds it, writes vectors. Bursty, short, stateless.

> 💡 **The line to remember: Lambda is great for *calling* an LLM, wrong for *hosting* one.**

### 9️⃣ SageMaker AI endpoint

Hand SageMaker your **model weights**. It gives you a managed, autoscaling, GPU-backed inference endpoint with versioning and A/B traffic splitting.

> 🍽️ **A professional kitchen built only for one cuisine.** Superb at that. Useless for anything else.

**Right when:** you fine-tuned Llama and need it served on GPUs with autoscaling. **Wrong when you don't own a model** — a SageMaker endpoint fronting an OpenAI API call is an expensive GPU box serving nothing. ⚠️ GPU endpoints bill **per hour, always-on** — easily $1–5/hr.

### Reading the whole menu at once

| # | Option | Containers? | Orchestrator | Who owns the server | GPU | Fits the lab app? |
|---|---|---|---|---|---|---|
| 1 | Simple EC2 | ❌ | none | **you** | ✅ | works, fragile |
| 2 | ECR + EC2 | ✅ | **none** | **you** | ✅ | works, fragile |
| 3 | App Runner | ✅ | built-in | AWS | ❌ | awkward — 2 containers |
| 4 | Beanstalk | either | built-in | AWS-ish | ✅ | dated |
| **5** | **ECR + Fargate** | ✅ | **ECS** | **AWS** | ❌ | ⭐ **chosen** |
| 6 | ECS on EC2 / MI | ✅ | ECS | you (AWS-patched on MI) | ✅ | overkill here |
| 7 | EKS | ✅ | **Kubernetes** | you | ✅ | overkill |
| 8 | Lambda + APIGW | ❌ | n/a | AWS | ❌ | ❌ Streamlit breaks |
| 9 | SageMaker | n/a | n/a | AWS | ✅ | ❌ no model to host |

### 🎯 The four questions that pick your row

```
Do you host your own model weights?   ──YES──►  9 SageMaker, or 6 (GPU)
              │ NO
              ▼
Is the work short, bursty, stateless? ──YES──►  8 Lambda
              │ NO
              ▼
Is your team already on Kubernetes?   ──YES──►  7 EKS
              │ NO
              ▼
Do you want to manage servers?        ──NO───►  5 ECS FARGATE  ⭐
                                │ YES
                                ▼
                        1 / 2 / 6
```

### ❗ The distinction people get wrong

**`ECR + EC2` is not the same as `ECR + ECS with EC2 instances`**, even though both mention EC2.

```
ECR + EC2
   EC2 pulls the image and you run Docker yourself.
   You write the start scripts. You handle failures.

ECR + ECS (EC2 / Managed Instances)
   ECS handles the Docker-level lifecycle FOR those instances.
   Task definitions, restarts, health checks — all managed.
```

The difference is **control-plane presence**: the second gives declarative desired-state management; the first is imperative and manual. Same hardware, completely different amount of work.

### Why Fargate won for this lab

> *"The app was already containerised and needed real orchestration — self-healing, rolling deploys, secrets, logging — without owning a server or learning Kubernetes. It calls OpenAI rather than hosting a model, so Fargate's lack of GPU costs nothing."*

It's the only row that dodges **both** Kubernetes *and* servers.

**One line:** ECS is always the orchestrator; the only real question is whether Fargate or EC2 instances do the computing, and **GPU need is what decides it.**

---

## 11. The EC2 path — and the two bugs that catch everyone

Before containers, the baseline path. Worth doing once, because the two failure modes below recur forever.

### Launching the instance

| Decision | What to pick, and why |
|---|---|
| **Operating system** | **Ubuntu**, not Windows. Lighter, standard for servers |
| **Instance type** | `t2.micro` free-tier; `t2.medium` for a real small API; **`G4dn`/`G5`/`G6` family** only if running an open-weight model yourself |
| **Key pair** | A `.pem`/`.ppk` file that proves who you are. Download and **store it safely** — it's also how you'd let a teammate in, or move files with `scp` |
| **Storage** | Ubuntu defaults to **8 GB**; bump to **12 GB+** because libraries and model weights eat space fast. Free tier allows 30 GB |

> 🔑 **The key insight about instance size:** use a *tiny* box if your app only calls a hosted model API — the heavy lifting happens on someone else's hardware. The moment you host your own open-weight model, you need a GPU instance and the economics change completely.

**GPU shortcut:** under **Browse more AMIs → AWS Marketplace**, search "GPU" for machine images with **NVIDIA drivers pre-installed**, so you skip driver installation entirely.

### Getting set up

```bash
sudo apt update && sudo apt upgrade     # always first — later installs depend on it
sudo apt install python3-pip python3-venv

python3 -m venv env
source env/bin/activate                 # prompt changes to show (env)
pip3 install -r requirements.txt
```

> ❓ **Why bother with a virtual environment on a server dedicated to one app?** Because "one server, one app" often stops being true. Run two Python services on the same box — a legacy app that's painful to upgrade and a newer one needing a later library version — and their dependencies collide. **You're isolating against the *future* state of the server, not the current one.**

Moving files up: **WinSCP** (Windows, plus PuTTY for the shell) or **FileZilla**/`scp` (Mac/Linux). Host = the **Public IPv4 address**, username = `ubuntu`, no password — point the SSH authentication setting at your key file.

### ⚠️ The two bugs

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

Open `http://<Public-IPv4>:8080` and it fails. There are **two distinct reasons**, and both bite on nearly every first deployment.

**Bug 1 — bound to localhost instead of `0.0.0.0`.**

> 🚪 **Analogy:** `localhost` (`127.0.0.1`) is like answering the door only for people already inside the house. `0.0.0.0` means "accept knocks from any door, including the street." On your laptop you're always inside, so localhost works. On a server, everyone is outside.

**Bug 2 — AWS blocks the port by default.** A new instance refuses all incoming traffic:

```
Instance → Security → click the Security Group ID
        → Edit inbound rules
        → Add rule:  Custom TCP  |  Port 8080  |  Source: 0.0.0.0/0
        → Save rules
```

> ⚠️ **And a third trap:** `https://` will not work. HTTPS needs a domain and a real SSL certificate. Without those it's plain `http://` — which is exactly why this path stops short of "production."

**One line:** if a deployed app is unreachable, it's almost always one of these two — bound to localhost, or the port isn't open in the security group. Check both first, every time.

### Keeping it alive after you disconnect

Close the terminal and the app dies — the process was a child of that shell session.

| | `nohup` | `tmux` |
|---|---|---|
| What it does | Detaches one command from the terminal | Gives you whole terminal sessions you can leave and re-enter |
| Can you go back and look? | No — it's just a background process | Yes, `attach` returns you to the live session |
| Good for | One service, fire and forget | Several services, each in a named session |
| Stopping it | `ps -ef \| grep uvicorn` then `kill <pid>` | `tmux kill-session -t <name>` |

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8080 &

tmux new -s fastapi          # named — far better than the default 0, 1, 2…
# Ctrl+B then D              → detach, leaving it running
tmux list-sessions
tmux attach -t fastapi
```

> 🔁 **Why you'll do the kill dance constantly:** update your code, try to restart, and you get `address already in use` — the old process is still holding the port. Find, kill, rerun.

> ⚠️ **Neither of these is production-grade.** `nohup` handles hangup signals; `tmux` gives a re-attachable session. **Neither restarts your app if it crashes, and neither survives a server reboot.** Real deployments use **systemd** (process supervision, auto-restart, log handling, starts on boot) or **Docker with a restart policy**. For learning and demos, `nohup`/`tmux` are exactly right — just don't mistake them for the finished answer.

**Running several services:** each `tmux` session is a fresh terminal, so **re-activate the virtual environment inside every one**, and **every new port needs its own inbound rule**. Two services means two rules.

### The two things that actually hurt: billing and security

| Action | What happens | Still charged? |
|---|---|---|
| **Stop** | Instance shuts down, EBS disk kept | **Yes** — you still pay for storage |
| **Terminate** | Instance and its storage deleted | No |

> 💸 **Terminate, don't just stop.** And **turn on MFA on the root account** — a compromised AWS account gets mined for crypto across every region simultaneously, and the bills from that are the stuff of horror stories. MFA is the cheapest insurance in cloud computing.

---

## 12. The ECS + Fargate deployment, step by step

Every step exists for a reason, and the reasons are more useful than the clicks.

### Target architecture

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

**The security decision worth copying:** an inbound rule exists for port **8501** (Streamlit) but deliberately **not** for port 8000 (FastAPI). Streamlit reaches FastAPI over **localhost inside the same task**, so no external user can hit the API directly and burn your credits.

> 🚪 **Analogy:** a restaurant with a public dining room and a closed kitchen. Customers enter the dining room (8501). Waiters walk into the kitchen (8000) through an internal door. There is no street entrance to the kitchen — by design.

> 🔌 **Note the hostname difference, it's a favourite interview detail.** Under Compose, two separate containers on a shared network address each other by **service name** (`http://api:8000`). Under Fargate, two containers in **one task share a single network namespace**, so the same variable becomes `http://localhost:8000`. Same port, different hostname, because the topology changed.

### The eleven steps

**1. Install and authenticate the AWS CLI.** `aws configure` with an access key + secret for an IAM user. Verify:

```bash
aws sts get-caller-identity
```

The account ID it returns must match the console. Cheap, and it catches deploying into the wrong account.

**2. Create an ECR repository.** Name it, take the **repository URI** — that URI is how Docker knows where to push.

**3. Build and push the image.**

```powershell
# PowerShell, because variables survive between commands
$AWS_REGION     = "ap-south-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REGISTRY   = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
$IMAGE_URI      = "$ECR_REGISTRY/openai-llm-app:v1"

aws ecr get-login-password --region $AWS_REGION |
    docker login --username AWS --password-stdin $ECR_REGISTRY

docker build --platform linux/amd64 -t $IMAGE_URI .
docker push $IMAGE_URI
```

> ⚠️ **`--platform linux/amd64` is not optional on Apple Silicon.** Build on an M-series Mac without it and you push an `arm64` image that Fargate's default x86 platform cannot run — the task fails with `exec format error`, which is a genuinely confusing message the first time you see it.

> 💡 **Tag with a version, not `latest`.** `:latest` makes rollback ambiguous and makes "which image is actually running?" unanswerable.

**4. Store the API key in Secrets Manager.** Secret type "other", the key as plain text. Copy its **ARN**.

**5. Create the ECS task execution role in IAM.** ⚠️ **This is the step that bites people.** The role needs *two* permission sets:

- The AWS-managed `AmazonECSTaskExecutionRolePolicy` → lets ECS pull images from ECR and write logs
- An **inline policy** for `secretsmanager:GetSecretValue`, **scoped to your secret's ARN** → lets ECS read the key

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:openai-key-AbCdEf"
  }]
}
```

> 🐛 **This is the single most common first-deploy failure there is.** The service is created with the wrong or under-scoped execution role, the container can't read the secret, and the task dies before your code ever runs. The log line names the secret ARN and says `AccessDeniedException` — recognise it and you save an hour.

> 🧭 **Execution role vs task role — know the difference.** The **task execution role** is used by the ECS *agent* to set the container up: pull the image, fetch secrets, write logs. The **task role** is assumed by *your application code* at runtime to call other AWS services (S3, DynamoDB, Bedrock). Putting an S3 permission on the execution role does nothing for your code. Interviewers ask this.

**6. Create a CloudWatch log group.** `/ecs/openai-llm-app`, retention 3 days for a demo (longer in production — retention is a cost and a compliance decision).

**7. Create a security group.** Inbound rule on **8501** only. Source `0.0.0.0/0` (the whole internet) or "My IP" for a demo. Note that "My IP" breaks the moment you change network — a laptop moving from office wifi to a phone hotspot locks itself out.

**8. Create the ECS cluster.** Fargate-only (serverless), or EC2/Managed Instances if you need GPU.

**9. Create the task definition.** Family name, launch type Fargate, CPU and memory (0.5 vCPU / 1 GB is plenty for the demo). Then define **two containers**:

| | API container | Frontend container |
|---|---|---|
| Image | the ECR image | **the same ECR image** |
| Port | 8000 | 8501 |
| Essential | Yes | Yes |
| Env vars | `LOG_LEVEL`, model name | `API_BASE_URL=http://localhost:8000` |
| Secret | `OPENAI_API_KEY` → *valueFrom* the Secrets Manager ARN | — |
| Command | default (`CMD`) | `streamlit run frontend/streamlit_app.py …` |
| Health check | hit the port; 30s interval, 5s timeout, N retries | same |
| Logs | CloudWatch, stream prefix `api` | CloudWatch, stream prefix `frontend` |

> ❤️ **What health checks actually buy you:** if the check fails more than `retries` times, ECS marks the container unhealthy, stops it, and starts a fresh one. **That's self-healing you would otherwise have to build.** It is also why `essential: true` matters — an essential container dying takes the whole task down and triggers replacement, rather than leaving a half-dead task serving errors.

**10. Create the service.** Cluster, task definition revision, launch type Fargate, desired count (1 here), VPC and subnets, security group, public IP on.

**11. Open the app.** Grab the task's **public IP**, hit port 8501. Streamlit loads; FastAPI is unreachable from outside — exactly as designed.

### Shipping a change

```
rebuild → push to ECR → new task-definition revision → update service to that revision
```

Because revisions are **immutable and retained**, rollback is symmetric: point the service at the previous revision. That's a pointer update, not a recovery procedure.

> ⚠️ **The public IP changes on every redeploy.** Fine for a walkthrough, unacceptable for production — which is precisely the problem an **Application Load Balancer** solves. The ALB has a stable DNS name; ECS registers and deregisters tasks with its target group as they come and go. Users hit one unchanging address, traffic spreads across healthy tasks, and rolling deployments become invisible rather than a URL change. It also unlocks blue-green and canary releases, and is where you attach an ACM certificate to finally get HTTPS.

---

## 13. Secrets, IAM, and network exposure

### Where the API key goes, and what's wrong with the alternatives

| Approach | Verdict |
|---|---|
| **Baked into the image** (`ENV OPENAI_API_KEY=…`) | ❌ Anyone who can pull the image has your key, and it persists in every layer of image history |
| **Committed in a `.env` file** | ❌ The classic way keys end up on GitHub |
| **Static credentials in CI variables** | ⚠️ Better, but long-lived and broadly readable |
| **Secrets Manager, referenced by ARN in the task definition** | ✅ Injected at runtime; never in the image or the repo; supports rotation |

> 🔐 **A real-world note that matters more than the theory.** If a key *does* leak — a CSV of access keys committed to a public repo, a key pasted into a chat — **rotation is the only fix**. Deleting the commit does not help; the value was published. Rotate first, investigate second.

### Scoping IAM, and keeping it from drifting

- **A dedicated role per service**, scoped to **exact resource ARNs** rather than wildcards. The ECS task execution role here needs exactly two things: pull from ECR, and read *that one* secret — not all secrets.
- **Audit with IAM Access Analyzer** periodically to surface over-permissive or unused grants.
- **For CI/CD, use OIDC federation** so GitHub Actions *assumes* a role rather than holding long-lived static access keys.

**Why bother:** blast radius. If a credential leaks, the damage is bounded by what that role could reach. "`AdministratorAccess` because it was quicker" turns a small incident into a large one.

### Stopping someone hammering your backend

The architectural answer first: **don't expose the backend at all** (§12). Then defence in depth:

| Layer | What it does |
|---|---|
| Authentication on the endpoint | No anonymous access to a paid resource |
| Per-principal rate limiting | Bounds requests per user per minute |
| Request-size and max-token caps | Bounds the *cost* of any single request |
| Response caching | Repeated queries cost nothing |
| Billing alarms + cost anomaly detection | Runaway spend noticed in hours, not at month end |

> 🌐 **When frontend and backend are separate tasks**, don't open the backend to a CIDR range — set its security-group inbound rule to **allow the frontend's security group** as the source. The rule then follows the service rather than an IP that changes.

---

## 14. Cost, scaling, and cleanup

### Scaling, in two directions

| | What it does | Example |
|---|---|---|
| **Vertical** | Make the machine bigger | 30 GB RAM → 50 GB RAM |
| **Horizontal** | Make more machines | 1 container → 5 containers |

For stateless request-driven web workloads, **horizontal is almost always right** — ECS scales task count on target-tracking policies (CPU, memory, or ALB request count per target). Vertical is for genuinely memory-bound single-instance constraints.

### The cost model, and the trap

The reference demo ran about **90 minutes for roughly $0.03**. That's a tiny Fargate task with no GPU. Add GPU workloads and you're into **~$1–5/hour** territory.

> 💸 **The trap worth memorising: you are billed for what you *reserve*, not what you *use*.** Pick a GPU that could run a 70B model and then serve a 7B model on it, and you pay for the big GPU regardless. Right-size deliberately.

**The levers that actually move LLM cost at scale:**

1. **Right-size** — reserved capacity bills whether busy or idle.
2. **Cache aggressively** — exact-match and semantic caching; repeated queries are far more common than people expect.
3. **Route by difficulty** — send simple requests to a cheaper/smaller model.
4. **Trim context** — with LLMs, the unit you're scaling isn't really *users*, it's **tokens**. Cost and throughput both scale with tokens processed, so an unnecessary 4 KB of context in every prompt is a permanent tax.
5. **Scale to zero where the platform allows it** (App Runner, HF Endpoints, serverless-GPU providers) for bursty traffic.

### Cleanup checklist

1. Update the ECS service to **0 desired tasks**
2. Delete the service
3. Delete the cluster
4. Delete the ECR repository/images if no longer needed
5. **Terminate** (not stop) any EC2 instances
6. Check **Billing & Cost Management** for anything still running

### What to learn next, if you're heading toward LLMOps

VPC design, load balancers, auto-scaling groups, routing rules, **GitHub Actions for CI/CD**, and **Terraform** for infrastructure-as-code.

> 📌 **The useful framing: everything done manually in the console here is exactly what GitHub Actions and Terraform automate.** Console clicking is how you *learn* the resources; IaC is how you *keep* them reproducible and reviewable.

**One line for Part III:** ECS orchestrates, Fargate or EC2 executes, GPU need decides which; secrets go in Secrets Manager by ARN with a least-privilege execution role; expose only the front door; and you pay for reserved capacity, so right-size and delete everything afterwards.

---
---

# Part IV — Hosting Platforms

Part III assumed you run the container. This part is about the layer above: platforms that run the *model* for you, so you never see a GPU.

## 15. The three tiers of "who runs the model"

```
TIER 1  ── Managed model API ──────────────────────────────────
         OpenAI, Anthropic, Amazon Bedrock
         You send text, you get text. No infrastructure at all.
         Pay per token.

TIER 2  ── Managed model hosting ──────────────────────────────
         HF Inference Endpoints, SageMaker endpoints,
         Cerebrium / Modal / RunPod / Baseten
         You bring weights; the platform provides the GPU,
         the autoscaling, and the endpoint. Pay per GPU-minute.

TIER 3  ── Self-hosted serving ────────────────────────────────
         vLLM / Ollama / TGI on EC2, ECS-on-EC2, or EKS
         You bring weights AND run the server.
         Pay per GPU-hour, whether busy or not.
```

**The single most useful question for placing yourself on this ladder:** *do you own model weights?* If no, Tier 1 and you are done. If yes, the next question is *is your GPU busy most of the time?* — that's what separates Tier 2 from Tier 3.

---

## 16. Amazon Bedrock — Tier 1, inside AWS

**What it is:** a managed service giving one API over pre-trained models from multiple providers — Anthropic, Meta, Mistral, AI21, Cohere, Amazon's own Nova/Titan family, and others. No training, no infrastructure, no model management.

**Why it exists when OpenAI's API already does the same thing:** because everything stays inside your AWS account and its security boundary. Requests don't leave your VPC if you use a VPC endpoint, IAM governs access, CloudTrail logs it, and the bill arrives with your other AWS charges. For a regulated organisation that is often the whole argument.

### Key benefits

| Benefit | What it means concretely |
|---|---|
| **Ease of use** | No infrastructure to manage |
| **Versatility** | Multiple providers behind one API — swap models without changing vendors |
| **Scalability** | AWS absorbs the load |
| **Security & privacy** | Your prompts aren't used to train the underlying models; IAM + VPC endpoints + CloudTrail |
| **Customisability** | Fine-tune foundation models on your own data, or use Bedrock Knowledge Bases for managed RAG |

### Getting access

Bedrock models are **opt-in per model per region**. Search Bedrock in the console → left pane → **Model Access** → select models → submit. Approval can take **minutes to hours**. This trips up first-time users: your code is correct and you still get `AccessDeniedException` because the model was never enabled.

### The code — the old way and the current way

The course materials show `invoke_model`, which takes a **model-specific** payload:

```python
import boto3, json

bedrock = boto3.client(service_name="bedrock-runtime")

payload = {                                  # ← this shape is Mistral-specific
    "prompt": "[INST]" + prompt_data + "[/INST]",
    "max_tokens": 2048,
    "temperature": 0.1,
    "top_p": 0.9,
}

response = bedrock.invoke_model(
    body=json.dumps(payload),
    modelId="mistral.mistral-7b-instruct-v0:2",
    accept="application/json",
    contentType="application/json",
)
print(json.loads(response["body"].read())["outputs"][0]["text"])
```

> ⚠️ **The problem with this, and why it matters:** `invoke_model` is a raw passthrough. Every model family expects a different JSON body and returns a different JSON shape — Anthropic wants `messages` and `anthropic_version`, Mistral wants `prompt` with `[INST]` tags, Titan wants `inputText` and `textGenerationConfig`. Switching models means rewriting the payload **and** the parser.

**The current default is the Converse API**, which normalises all of that:

```python
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

response = bedrock.converse(
    modelId="mistral.mistral-7b-instruct-v0:2",   # swap this line, nothing else
    messages=[{"role": "user", "content": [{"text": prompt_data}]}],
    inferenceConfig={"maxTokens": 2048, "temperature": 0.1, "topP": 0.9},
)
print(response["output"]["message"]["content"][0]["text"])
```

One request shape, one response envelope, for **every Bedrock model that supports messages**. It also handles multi-turn conversation state, tool use (function calling), and streaming (`converse_stream`) uniformly. As of February 2026 the Converse format also works for **batch inference**, so the same prompts run real-time or batched without rewriting ([AWS](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-bedrock-batch-inference-supports-converse-api-format/)).

> ✅ **The rule:** default to `converse` for chat, tool use, and agents. Drop to `invoke_model` only where a model exposes a native field that Converse doesn't surface. `invoke_model` is not deprecated — it's just no longer the thing you reach for first.

**One line:** Bedrock is "OpenAI's API, but it's an AWS service" — multiple model providers, one IAM-governed endpoint, and you should call it through `converse` so that changing models is a one-line change.

---

## 17. Hugging Face — Tier 1 and Tier 2 in one account

Hugging Face offers two different things that get confused constantly.

| | **Inference Providers** | **Inference Endpoints** |
|---|---|---|
| What it is | A routed, pay-per-token API over models hosted by partner providers | **Your own dedicated** auto-scaling GPU instance running **your** model |
| Billing | **Per token** | **Per minute** of instance time |
| You choose | The model | The model, the hardware, the region, the scaling policy |
| Scale to zero | n/a (nothing is yours) | ✅ Yes, after an idle period |
| Analogy | Ordering takeaway | Renting a kitchen by the hour |

### Inference Endpoints, step by step

1. **Add a payment method** — the Create button doesn't work until billing is set up.
2. Go to `https://endpoints.huggingface.co/<USERNAME>/new`.
3. **Repository ID & endpoint name** — which model, what to call it.
4. **Cloud provider, region, instance type** — AWS/Azure/GCP, and CPU vs GPU.
5. **Scale-to-zero** — on or off.
6. **Security level** — public, protected (token required), or private (VPC/PrivateLink).
7. **Advanced** — replica autoscaling bounds, task type, framework, container type.
8. **Create**, review the cost estimate, launch. Initialisation takes **1–5 minutes**.

### Autoscaling behaviour

| Event | Rule |
|---|---|
| Scale **up** (CPU instance) | New replica when CPU utilisation hits 80% |
| Scale **up** (GPU instance) | New replica when GPU utilisation exceeds 80% for 1 minute |
| Scale **down** | Checked every 2 minutes once utilisation drops below the threshold |
| Scale **to zero** | After a configurable idle window (1 hour by default) |

> 💰 **Scale-to-zero is the feature that makes this economically sane for bursty traffic.** An always-on A100 is roughly $2.50/hour ≈ $1,800/month whether anyone uses it or not. With scale-to-zero, an endpoint serving 40 requests a day costs a few dollars. The price is a **cold start** on the first request after idle.

**2026 indicative hourly pricing on AWS-backed endpoints**, billed per minute: CPU ~$0.033, NVIDIA T4 ~$0.50, L4 ~$0.80, L40S ~$1.80, A100 ~$2.50, H200 ~$5.00 ([techjacksolutions](https://techjacksolutions.com/ai-tools/hugging-face/hugging-face-pricing/), [eesel](https://www.eesel.ai/blog/hugging-face-pricing)).

### Calling it

```bash
curl https://your-endpoint-url \
  -X POST \
  -d '{"inputs": "Deploying my first endpoint was an amazing experience."}' \
  -H "Authorization: Bearer <Token>"
```

Also available through the UI widget and the `huggingface_hub` / `@huggingface/inference` libraries in Python and JavaScript.

> ⚠️ **One operational gotcha:** you can change instance type, autoscaling bounds, task type, and model revision on a live endpoint via the Settings tab. But **if an endpoint has entered a failed state, you must create a new one** — it cannot be repaired in place.

### 💡 The volume thresholds worth memorising

| Monthly volume | Cheapest option |
|---|---|
| Pilot / low | **Inference Providers** (per-token) — no idle cost at all |
| ~10M–100M+ tokens | **Inference Endpoints** with scale-to-zero |
| 500M+ tokens | **Self-hosting** on your own GPUs starts to win |

That ladder is a good template for the general question *"when should we self-host?"* — the answer is always a utilisation threshold, never a principle.

---

## 18. Cerebrium and the serverless-GPU class

**Cerebrium** is a cloud GPU platform that manages the unglamorous parts — GPUs, Kubernetes, queues, monitoring, and scaling — so you deploy a Python file and get an endpoint. It advertises cold starts **under ~5 seconds**, autoscaling from 1 to 10,000+ concurrent requests, and 99.9% uptime.

### The deployment flow, end to end

```bash
pip install cerebrium
cerebrium login                 # opens a browser for auth

cerebrium init my-llama-app
cd my-llama-app
```

Two files matter:

| File | Contains |
|---|---|
| `main.py` | All your code — a model, a RAG system, an agent, whatever |
| `cerebrium.toml` | App metadata **and the hardware spec** — GPU type, vRAM, memory, CPU — plus the list of libraries to install |

That second file is the interesting one: **hardware is declared as config, not provisioned as infrastructure.** You change `gpu = "AMPERE_A10"` to `gpu = "HOPPER_H100"` and redeploy.

Secrets (e.g. `HF_AUTH_TOKEN`) go in the dashboard, not the repo. Then:

```bash
cerebrium deploy
```

The CLI streams build logs and prints the **endpoint URL** on success. The dashboard shows total requests, per-request latency, and cost, and the app overview page generates the Python inference snippet for you.

### The wider category, compared (2026)

| Platform | Cold start | Character |
|---|---|---|
| **Cerebrium** | **2–4 s** | Config-declared hardware; fastest-tier cold starts |
| **Beam** | **2–4 s** | Cold-start latency is the explicit product KPI |
| **Modal** | fast | Python-native, strong for batch + inference mixed workloads |
| **RunPod** | mid | Cheapest control, least lock-in; **Flex** workers scale to zero, **Active** workers stay warm at ~20% discount (H100 ≈ $4.18/hr Flex → $3.35/hr Active) |
| **Baseten** | **16–60 s** | Polished production serving; the expectation is you keep replicas warm |

Snapshot-restore techniques cut cold starts by an average of **71%**, with the largest gains on vLLM workloads ([Modal](https://modal.com/resources/best-serverless-gpu-platforms-inference), [buildmvpfast](https://www.buildmvpfast.com/blog/serverless-gpu-ai-inference-platform-comparison-2026)).

> 💡 **The counter-intuitive costing rule:** differences in autoscaling, idle billing, startup time, and platform fees can make a **higher-priced** serverless GPU cheaper overall than a **lower-priced** dedicated instance that stays billable while idle. Compare cost-per-served-request, never cost-per-GPU-hour.

---

## 19. The decision framework: managed API vs managed hosting vs self-hosted

This is the question Week 5 is really asking, and it's the one interviews return to. Answer it with **reasons**, not preferences.

```
Do you need a specific open-weight or fine-tuned model?
        │ NO                                    │ YES
        ▼                                       ▼
  ┌──────────────────┐            Is your GPU busy > ~50% of the time?
  │ MANAGED API      │                  │ NO                  │ YES
  │ OpenAI / Bedrock │                  ▼                     ▼
  │ Pay per token    │        ┌──────────────────┐  ┌──────────────────┐
  └──────────────────┘        │ MANAGED HOSTING  │  │ SELF-HOSTED      │
                              │ HF Endpoints,    │  │ vLLM on ECS-EC2, │
                              │ Cerebrium, etc.  │  │ EKS, or bare EC2 │
                              │ Scale to zero    │  │ Cheapest per tok │
                              └──────────────────┘  └──────────────────┘
```

### The five axes that actually decide it

| Axis | Pushes you toward managed API | Pushes you toward self-hosting |
|---|---|---|
| **Data residency / privacy** | Vendor with the right compliance posture, or Bedrock inside your VPC | Data cannot leave your network at all |
| **Model requirement** | A frontier model you can't host anyway | A specific open-weight or fine-tuned model |
| **Volume** | Low or spiky | High and steady — per-token pricing becomes the dominant cost |
| **Latency floor** | Fine — network hop is small next to generation time | You need control over batching, KV cache, and quantisation |
| **Team capacity** | No GPU/infra expertise | You have (or are building) LLMOps capability |

### The thing people get wrong

> ❌ *"Self-hosting is cheaper."* Only above a utilisation threshold. A $2.50/hour A100 costs **$1,800/month** whether it serves a million requests or none. At low volume, per-token pricing wins by an enormous margin — and the hidden cost of self-hosting is not the GPU, it's the **engineer-hours** spent on driver versions, OOM tuning, and 3am restarts.

### What actually changes when you swap a hosted API for a self-hosted model

| Stays the same | Changes |
|---|---|
| Streamlit + FastAPI structure | Fargate → **ECS on EC2 / Managed Instances** (GPU) |
| Docker / Compose | Add a serving layer: **Ollama** or **vLLM** |
| ECR, ECS, task definitions | Instance-type selection now matters a lot |
| CloudWatch logging, evaluation harness | **System evaluation becomes yours** (§27) |
| The application code, mostly | Cost profile shifts from per-token to per-hour |

**One line for Part IV:** call a managed API unless you need a specific model; if you need a specific model, use managed hosting until your GPU is busy enough that owning it is cheaper — and remember that the hidden cost of self-hosting is engineer-hours, not GPU-hours.

---
---

# Part V — Model Serving and Formats

## 20. What "model serving" means

**Model serving** is hosting and managing a model so it can respond to requests. It's putting the model into production: ensuring reliability, scalability, and efficiency while meeting latency and throughput requirements.

Two axes divide the whole field.

### Axis 1 — batch vs online

| | **Batch serving** | **Online serving** |
|---|---|---|
| Shape | Predictions for a large dataset all at once | Requests processed as they arrive |
| Latency | Minutes to hours; irrelevant | Milliseconds to seconds; critical |
| Examples | Overnight personalised recommendations for millions of users; fraud scoring on transaction logs; embedding a document corpus | Chatbots; e-commerce recommendations adapting to live behaviour |
| ✅ Advantages | Cheap — schedule during off-peak; GPU runs at 100% utilisation with no idle | Interactive, adaptive experiences |
| ❌ Challenges | Useless for real-time | 24/7 availability cost; needs careful latency optimisation |

> 💡 **Batch is dramatically cheaper and nobody uses it enough.** Most providers price batch at roughly half of real-time (OpenAI's Batch API, Bedrock batch inference). If a workload tolerates a few hours of delay — nightly summarisation, backfilling embeddings, evaluating a dataset — moving it to batch is the single easiest cost win available.

### Axis 2 — server-based vs serverless

| | **Server-based** (EC2, dedicated VMs) | **Serverless** (Lambda, Cloud Run, Cerebrium) |
|---|---|---|
| ✅ Pros | Control over hardware; suits high-throughput consistent load | Pay-per-use; scales elastically with traffic |
| ❌ Cons | Needs DevOps expertise; resources idle during quiet periods | Cold-start latency; limited support for long-running processes and very large models |

### The tool landscape

| Server-based | What it's for |
|---|---|
| **vLLM** | High-throughput, low-latency GPU LLM inference. The 2026 default |
| **Ollama** | Simple local/private-server serving of GGUF models |
| **HF TGI (Text Generation Inference)** | HF's production server for HF models |
| **NVIDIA Triton** | High-performance multi-framework GPU serving (TensorFlow, PyTorch, ONNX) |
| **Ray Serve** | Distributed serving; multi-model workflows needing coordination |
| **BentoML** | Packaging and deploying models as services |
| **MLflow** | Model versioning and deployment workflows |
| **SageMaker** | AWS's managed training + deployment platform |

| Serverless | What it's for |
|---|---|
| **AWS / Azure / GCP serverless** | Lambda, Cloud Run, Functions |
| **HF Inference Endpoints** | Managed HF model serving (§17) |
| **Cerebrium / Modal / RunPod / Baseten** | Serverless GPUs — the GPU without managing it (§18) |

### The four things to weigh

1. **Scalability** — can it absorb a spike? Serverless shines; server-based gives predictable performance.
2. **Latency** — GPU acceleration, caching, and quantisation are the levers.
3. **Cost efficiency** — batch for non-critical work; understand the pricing model before committing.
4. **Model updates** — how easily can you roll out a new version or roll back? MLflow and task-definition revisions both exist for this.

---

## 21. GGUF — the format

### The predecessor: GGML

**GGML** (GPT-Generated Model Language), by Georgi Gerganov, was a tensor library that made LLMs run on consumer hardware — especially **CPUs** — by enabling quantisation and shrinking models.

| GGML pros | GGML cons |
|---|---|
| Early, widely adopted | Limited flexibility — couldn't easily support new features |
| **Single-file** distribution | Updates often caused **breaking changes** |
| Ran without a GPU | Manual tweaking of `rope-freq-base`, `rope-freq-scale`, `rms-norm-eps` |

### GGUF: what it fixed

**GGUF (GPT-Generated Unified Format)** is the community successor.

| Advantage | What it means |
|---|---|
| **Extensibility** | New metadata and features can be added **without breaking compatibility** |
| **Stability** | Backward compatible — old files keep working |
| **Versatility** | Works beyond LLaMA: Falcon, Bloom, Mistral, Phi, Qwen, Gemma |
| **Self-describing** | Tokeniser, chat template, architecture, and hyperparameters travel *inside the file* — no separate config to lose |

### File structure

```
┌─────────────────────────────────────────┐
│ Header                                  │  magic number, version, tensor count
├─────────────────────────────────────────┤
│ Metadata key-value pairs                │  architecture, context length,
│                                         │  tokeniser, chat template, rope params
├─────────────────────────────────────────┤
│ Tensor information                      │  name, dimensions, type, offset, padding
├─────────────────────────────────────────┤
│ Tensor data                             │  the weights themselves
└─────────────────────────────────────────┘
```

> 🗝️ **Why "self-describing" is the real win.** With `safetensors` you need the weights *plus* `config.json`, `tokenizer.json`, `tokenizer_config.json`, and a chat template to run anything. With GGUF it's **one file**. That's why `ollama run <model>` works with no configuration — everything it needs is inside.

**The trade-offs, honestly:** converting existing models takes time, and there's a learning curve around quantisation naming.

### Quantisation

Quantisation stores weights at lower precision to shrink the model and speed it up. Original weights are typically FP16 (2 bytes each); a 4-bit quant is ~4× smaller.

**The course-level summary:**

| Level | Character |
|---|---|
| **Q2, Q3** | Smallest, lowest quality |
| **Q4, Q5** | Balanced performance and memory |
| **Q6, Q8** | Best quality, highest resource demand |

**What the names actually mean in 2026** — you will see `Q4_K_M` and `IQ4_XS`, not bare `Q4`:

```
Q4_K_M
│ │ │
│ │ └── M = Medium size variant within the K family (S = Small, L = Large)
│ └──── K = "K-quant": super-blocks of scales, and attention vs feed-forward
│        layers are compressed differently because they tolerate it unequally
└────── 4 = ~4 bits per weight

IQ4_XS
││ │
││ └── XS = extra small
│└──── 4 bits
└───── I = "I-quant": uses an importance matrix (imatrix) plus non-linear
        quantisation to pack more quality into fewer bits
```

**The practical selection guide:**

| Choose | When |
|---|---|
| **Q4_K_M** ⭐ | The default. Fits a 7–8B model in ~6 GB VRAM, loses roughly 1% on benchmarks vs FP16, and is supported by every tool |
| **Q5_K_M / Q6_K** | 8–12 GB VRAM and you want better quality on things that expose quantisation error: multilingual text, structured output, long reasoning chains |
| **Q8_0** | Within rounding error of FP16; use when VRAM isn't a constraint and you want to eliminate quantisation as a variable while testing |
| **IQ4_XS** | You are a few hundred MB short of fitting with K-quants. Smaller than Q4_K_M at comparable quality — **but only with a good imatrix from a trusted author**, and it can be slightly slower on some hardware |

Sources: [TinyWeights](https://tinyweights.dev/posts/gguf-quantization-levels-q4-q5-q8/), [Kaitchup](https://kaitchup.substack.com/p/choosing-a-gguf-model-k-quants-i), [mustafa.net](https://mustafa.net/llm-quantization-explained/).

> ⚠️ **The mistake worth avoiding:** a **bigger model at a lower quant usually beats a smaller model at a higher quant.** A 13B at Q4_K_M generally outperforms a 7B at Q8_0 in the same memory budget. Pick the biggest model that fits at Q4_K_M before reaching for a higher quant of a smaller one.

### llama.cpp — the engine underneath

The **llama.cpp** project is the backbone of GGUF execution. It pioneered running large models efficiently on CPUs through quantisation and memory optimisation. **Ollama, LM Studio, and most desktop LLM apps are wrappers around llama.cpp.**

Its conversion script is how a Hugging Face model becomes a GGUF file:

```bash
git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp
pip install -r requirements.txt

# 1. safetensors (FP16) → GGUF (still FP16, just reformatted)
python convert_hf_to_gguf.py /path/to/hf-model \
       --outfile model-f16.gguf --outtype f16

# 2. FP16 GGUF → quantised GGUF
./llama-quantize model-f16.gguf model-Q4_K_M.gguf Q4_K_M
```

> 🧭 **The two-step shape is the thing to remember**, because it explains a common confusion: *conversion* (change the container) and *quantisation* (reduce the precision) are separate operations. The intermediate FP16 GGUF is large and usually thrown away.

---

## 22. Ollama — the easy one

**What it is:** a platform that makes running open-source LLMs locally trivial. It handles model weights, configuration, and dependencies so you can focus on using the model.

### Why run models locally at all

| Reason | Detail |
|---|---|
| **Data privacy** | Sensitive data never leaves your machine |
| **Customisation** | Modify models and parameters freely |
| **Offline capability** | Once downloaded, no internet needed |
| **Cost** | No per-token billing while prototyping |

### The whole workflow

```bash
ollama --version                    # verify install (macOS, Linux, Windows)

ollama pull llama3.2:1b             # download
ollama run llama3.2:1b              # chat in the terminal
ollama list                         # what's downloaded
```

### Customising with a Modelfile

```dockerfile
# Reuse an existing model with different parameters
FROM llama3.2:1b
# When using a local file instead:  FROM ./my-model.gguf

# higher = more creative, lower = more coherent
PARAMETER temperature 1

# context window: how many tokens the model can use to generate the next one
PARAMETER num_ctx 4096

SYSTEM You are a helpful customer support assistant.
```

```bash
ollama create support-bot -f ./Modelfile
ollama run support-bot
```

> 🧰 **The Modelfile is deliberately Dockerfile-shaped** — `FROM` a base, layer configuration on top, `create` produces a named artifact. If you understand Docker, you already understand this.

### Using it from code

```python
from ollama import chat

response = chat(
    model="llama3.2:latest",
    messages=[{"role": "user", "content": "Solve 2x + 5 = 10. What is x?"}],
)
print(response["message"]["content"])
```

### The HTTP API — the part that actually matters for deployment

Ollama serves on **port 11434** of localhost. Visit `http://localhost:11434/` to confirm it's running. **Any language can call it**, which is what makes Ollama a serving layer and not just a CLI toy:

```python
import requests, json

def ollama_embed(prompt):
    url = "http://127.0.0.1:11434/api/embeddings"
    payload = json.dumps({"model": "bge-m3:latest", "prompt": prompt})
    headers = {"Content-Type": "application/json"}
    return requests.post(url, headers=headers, data=payload).json()

print(ollama_embed("What is the standard value of gravity?"))
```

Ollama also supports plain text generation, **embedding models**, streaming output, and an **OpenAI-compatible endpoint** at `/v1/chat/completions` — which means you can point an existing OpenAI client at a local model by changing `base_url` alone. That's the single most useful fact about Ollama for anyone building on it.

> ⚠️ **Correction to a common claim.** Older material (including the Week 5 PDF) describes Ollama as "designed for developers working with LLMs on **CPUs**." That is out of date. Ollama supports **NVIDIA CUDA, Apple Silicon/Metal, and AMD Radeon GPUs**, and uses them automatically when present ([SitePoint](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/), [Spheron](https://www.spheron.network/blog/ollama-vs-vllm/)). The real distinction from vLLM is **concurrency**, not hardware.

---

## 23. vLLM — the throughput one

**What it is:** a Python library that optimises LLM inference and serving, originally from UC Berkeley's Sky Computing Lab, now community-driven. **By 2026 it is the default serving engine across most open-source LLM deployments** ([aifoss](https://aifoss.dev/blog/vllm-review-2026/)).

### PagedAttention — the core idea

Every input token generates attention keys and values (the **KV cache**), which must be kept for the rest of the generation. Naively, you reserve a contiguous block of memory sized for the *maximum* sequence length for every request — and most requests never use most of it.

**PagedAttention borrows virtual memory paging from operating systems:** the KV cache is split into small, fixed-size, **non-contiguous blocks** allocated on demand.

```
WITHOUT PagedAttention                WITH PagedAttention
┌────────────────────────┐            ┌──┬──┬──┬──┐
│ req A: reserved 4096   │            │A1│A2│B1│C1│   blocks allocated
│ ████░░░░░░░░░░░░░░░░░░ │ 80% waste  ├──┼──┼──┼──┤   on demand,
├────────────────────────┤            │A3│B2│C2│D1│   shared where
│ req B: reserved 4096   │            ├──┼──┼──┼──┤   possible
│ ██░░░░░░░░░░░░░░░░░░░░ │ 90% waste  │B3│C3│D2│..│
└────────────────────────┘            └──┴──┴──┴──┘
```

Memory waste drops to **under 4%**, which means far more requests fit on the same GPU simultaneously.

> 🅿️ **Analogy:** reserving memory the old way is booking a whole hotel floor for every guest in case they bring a large family. PagedAttention hands out individual rooms as people actually arrive, and lets two guests share a room when they're identical (prefix sharing — two requests with the same system prompt reuse the same blocks).

### Continuous batching — the other core idea

Static batching waits for a whole batch to finish before starting the next; the batch runs as slowly as its longest sequence, and finished slots sit idle. **Continuous (rolling) batching** admits a new sequence the instant an old one completes.

```
STATIC BATCHING                     CONTINUOUS BATCHING
slot1 ████████░░░░░░  idle          slot1 ████████▓▓▓▓▓▓  new req admitted
slot2 ███░░░░░░░░░░░  idle          slot2 ███▒▒▒▒▒▒▓▓▓▓▓  immediately
slot3 ██████████████                slot3 ██████████████
      └── all wait for slot3 ──┘          └── GPU never idles ──┘
```

This is the single biggest reason vLLM's throughput dwarfs naive serving.

### The rest of the feature list

- **CUDA-optimised execution**, plus FlashAttention / FlashInfer integration
- **Quantisation support** — GPTQ, AWQ, INT4, INT8, FP8
- **Speculative decoding** — a small draft model proposes tokens, the big model verifies several at once
- **Chunked prefill** — long prompts are processed in pieces so one huge prompt doesn't stall everyone else's decoding
- **An OpenAI-compatible server** — `vllm serve <model>` exposes `/v1/chat/completions`

### Performance

| Comparison | Reported gain |
|---|---|
| vs Hugging Face Transformers | **14–24× higher throughput** |
| vs HF Text Generation Inference (TGI) | **~3.5× faster** |
| Practical effect | **~5× more traffic on the same GPUs** |

Head-to-head against Ollama in 2026: **8,033 tokens/sec vs 484**, with vLLM holding **100% success at 128 concurrent requests** — but **below about 5 concurrent users, Ollama wins** ([tech-insider](https://tech-insider.org/vllm-vs-ollama-2026/), [SitePoint](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/)).

### Where vLLM is in 2026

Stable release **v0.28.0** (August 2026). The **V1 engine** has grown well past PagedAttention: a fault-tolerance layer, **multi-tier KV cache offload** (spill cache to CPU RAM or NVMe instead of evicting), compute/communication overlap for MoE models, an async-pipelined scheduler, and **adaptive speculative decoding** ([bro-code](https://www.bro-code.in/blog/vllm-v1-engine-beyond-pagedattention), [vLLM docs](https://docs.vllm.ai/en/latest/)).

### Minimal server

```bash
pip install vllm

vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --tensor-parallel-size 1
```

```python
from openai import OpenAI                       # the OpenAI client, pointed elsewhere
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
print(client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello"}],
).choices[0].message.content)
```

| Flag | What it controls |
|---|---|
| `--max-model-len` | Maximum context. **Lower it if you OOM** — KV cache scales with it |
| `--gpu-memory-utilization` | Fraction of VRAM vLLM may claim (default 0.90) |
| `--tensor-parallel-size` | How many GPUs to shard the model across |
| `--quantization awq` / `fp8` | Load a quantised checkpoint |

---

## 24. Choosing a serving stack

| | **Ollama** | **vLLM** | **llama.cpp** | **TGI** | **Triton** |
|---|---|---|---|---|---|
| Primary goal | Ease of use | **Throughput** | CPU/edge efficiency | HF-model serving | Multi-framework GPU serving |
| Hardware | NVIDIA, Apple Metal, AMD, CPU | **NVIDIA GPU** (CUDA), some ROCm | CPU-first, GPU offload | NVIDIA GPU | NVIDIA GPU |
| Format | GGUF | safetensors / HF, AWQ, GPTQ, FP8 | GGUF | HF | ONNX, TensorRT, PyTorch, TF |
| Memory | Static per model load | **Dynamic paging** | Static + mmap | Paged | Configurable |
| Concurrency | Low (wins below ~5 users) | **Very high** | Low | High | High |
| Setup | One binary, 2 minutes | pip install + flags | Compile or binary | Docker | Docker + config |

### The decision rule

```
Prototyping, or a private single-user assistant?      → Ollama
Serving real concurrent traffic on a GPU?             → vLLM
Running on a laptop / CPU / edge device, no GPU?      → llama.cpp (or Ollama)
Already deep in the Hugging Face ecosystem?           → TGI
Serving many models across ML frameworks, not just LLMs? → Triton
```

> 🔁 **The 2026 hybrid that most teams actually land on:** prototype with **Ollama**, serve production traffic with **vLLM**. Model files are largely interchangeable, so the migration is mostly a config change rather than a rewrite.

---

## 25. The numbers: latency, throughput, and GPU memory

This is the vocabulary that separates "I deployed a model" from "I operate a model." Interviewers probe here.

### The two phases of inference

```
PREFILL                              DECODE
Process the entire prompt at once.   Generate one token at a time,
Produces the KV cache and the        each depending on the last.
first output token.
COMPUTE-bound  ──────────────────►   MEMORY-BANDWIDTH-bound
```

That split explains almost every performance observation you'll make: long prompts hurt **TTFT**, long outputs hurt **total latency**, and the fixes are different.

### The metrics

| Metric | Definition | 2026 rule of thumb |
|---|---|---|
| **TTFT** (Time To First Token) | Prompt submitted → first token appears. Dominated by prefill compute + queuing | **< 500 ms** for prompts up to 4K tokens in a chat UI |
| **TPOT / ITL** (Time Per Output Token / Inter-Token Latency) | `decode_seconds / completion_tokens`. Dominated by HBM bandwidth | **≤ ~200 ms** acceptable; **> 250 ms** and streaming feels choppy |
| **Total latency** | `TTFT + (TPOT × output_tokens)` | The number the user actually feels |
| **Throughput** | Tokens/sec or requests/sec across all concurrent users | The number that determines your bill |
| **Goodput** | Throughput **filtered by SLO** — only requests that met their latency target | ⭐ **Track this, not raw throughput** |

Sources: [Modular LLM Inference Handbook](https://handbook.modular.com/llm-inference-basics/llm-inference-metrics/), [Gradient Update](https://gradientupdate.substack.com/p/llm-inference-metrics-reference).

> ⚖️ **The throughput-vs-latency tension, stated plainly.** Bigger batches raise throughput and *also* raise per-request latency, because each request waits behind more work. Tuning a server is choosing a point on that curve. **Goodput** exists because a server can report magnificent throughput while violating its latency SLO on most requests — high throughput, near-zero goodput.

> 🔗 **Connection to the p99 discussion from Week 3/6.** Report p99 **segmented by pipeline stage** (retrieval, rerank, generation) *and* by **workload segment** (short vs long prompts, cached vs uncached). An aggregate p99 hides the fact that one segment is fine and another is unusable.

### GPU memory math

**Rule of thumb for weights:**

| Precision | Bytes/param | 7B model | 70B model |
|---|---|---|---|
| FP32 | 4 | 28 GB | 280 GB |
| FP16 / BF16 | 2 | **14 GB** | **140 GB** |
| INT8 / FP8 | 1 | 7 GB | 70 GB |
| INT4 (Q4) | 0.5 | **3.5 GB** | **35 GB** |

> 🧮 **The shortcut: `params (in billions) × bytes-per-param = GB of weights`.** A 7B at FP16 is 14 GB. Then **add 15–25% overhead** for activations, CUDA context, and fragmentation — so a 7B FP16 model wants ~17–18 GB, which is why it does *not* fit comfortably on a 16 GB card but is fine on a 24 GB one.

**And then the KV cache, which is the part people forget:**

```
KV cache bytes ≈ 2 × layers × kv_heads × head_dim × seq_len × batch × bytes_per_element
                 ↑
                 2 = one K and one V
```

For Llama-3-8B (32 layers, 8 KV heads with GQA, head_dim 128) at FP16, 8K context, one sequence:

```
2 × 32 × 8 × 128 × 8192 × 2 bytes ≈ 1.07 GB  per concurrent sequence
```

> 💥 **This is the number that kills deployments.** 16 GB of weights looks like it fits on a 24 GB card — until 20 concurrent users need 20 GB of KV cache. PagedAttention (§23) exists precisely to make this allocation efficient, and **Grouped-Query Attention (GQA)** — 8 KV heads instead of 32 — is a ~4× reduction baked into modern model architectures for the same reason.

**The three levers when you don't fit:**

1. **Quantise the weights** — Q4 cuts weight memory ~4× (§21).
2. **Lower `--max-model-len`** — KV cache scales linearly with context length.
3. **Quantise the KV cache itself** — vLLM supports FP8 KV cache, roughly halving it.

**One line for Part V:** GGUF is a self-describing single-file format whose quantisation level (default `Q4_K_M`) trades size for quality; llama.cpp executes it and Ollama wraps llama.cpp for easy local use; vLLM is the GPU throughput engine via PagedAttention and continuous batching; and the numbers that matter are TTFT, TPOT, goodput, and the KV-cache arithmetic that decides how many users fit on your card.

---
---

# Part VI — LLM Evaluation

**The core idea, in one line:**

> An LLM doesn't fail like normal software. Normal software throws an error. An LLM returns a confident, fluent, well-formatted paragraph that happens to be wrong — and *nothing in the system notices*. **Evaluation is the machinery you build so that something notices.**

---

## 26. Evaluation vs guardrails — get this distinction exactly right

```
        BEFORE deployment                    AFTER deployment
    ┌─────────────────────┐            ┌─────────────────────┐
    │     EVALUATION      │            │     GUARDRAILS      │
    │                     │            │                     │
    │  "Is this model     │  ───────►  │  "Catch the cases   │
    │   good enough       │            │   where it's        │
    │   to ship?"         │            │   still wrong."     │
    │                     │            │                     │
    │  Result: a SCORE    │            │  Result: a BLOCK,   │
    │  e.g. 82% accurate  │            │  rewrite, or refusal│
    └─────────────────────┘            └─────────────────────┘
```

> 🚦 **The framing that makes it click:** you evaluate, and the model comes out 82% accurate. Great — but what about the other 18%? **You cannot evaluate your way out of that.** Guardrails are what you put in front of the remaining 18% at runtime.

**Example:** you evaluate a customer-support bot and find it's rude 4% of the time. *Evaluation gave you that number.* A **guardrail** is the runtime check that scans each outgoing message for hostile tone and rewrites it before the customer ever sees it.

**Why evaluation matters at all — five reasons:**

1. **Accuracy** — is the response actually right?
2. **Bias** — what prejudices did the training data bake in?
3. **Efficiency** — does it answer fast enough to be usable?
4. **Hallucination** — especially in RAG, where the model can invent things the retrieved context never said.
5. **Ethics/compliance** — including employees pasting organisational data into a third-party model.

**One line:** evaluation is a pre-launch measurement that produces a score; guardrails are a live safety net that produces an intervention — you need both, and conflating them is a classic interview stumble.

---

## 27. The seven dimensions you can evaluate

Most people think "evaluation" means accuracy. Accuracy is one of seven.

| Dimension | The question it asks | Concrete example |
|---|---|---|
| **Language understanding** | Does it work in *this* language, not just English? | Gemma 2B beat Llama 3 on non-English tasks while losing on English — **no model is uniformly best across languages** |
| **Creativity** | Is the creative output actually good, or just weird? | It can write jokes — but are the jokes *lame*? |
| **Accuracy** | Is the fact right? | Asked for the 2023 World Cup result, it shouldn't answer about 2019 |
| **Consistency** | Same question twice → same substance? | Re-asking often makes a model assume you wanted something *different* and drift |
| **Efficiency** | Is it fast enough to be usable? | 30s–2min response time means users leave, regardless of answer quality |
| **Ethical alignment** | Does it match *your organisation's* rules? | A company that ships a Python library may not want its bot recommending competitor libraries |
| **Harmfulness** | Does it produce offensive or unsafe content? | Assessed largely by human reviewers |

> 💡 **The consistency nuance worth remembering:** consistency does **not** mean identical wording. Tone, structure, and phrasing can vary freely — what must stay stable is **the substance**. A model that says "Paris" one time and "the capital is Paris, a city of 2.1 million" the next is *consistent*. One that says "Paris" then "Lyon" is not.

> ⚠️ **On organisational alignment:** this one is hard to *train* for — competitors keep appearing, and you can't fine-tune against a list that changes weekly. **This is a case where a guardrail beats evaluation**, because the rule is a moving target.

---

## 28. Six approaches to evaluating an LLM

### 28.1 Benchmarks — the standardised exam

Every model release claims "X% better." That comparison runs on **benchmarks**: large, public question-answer datasets everyone tests against.

| Benchmark | What it tests |
|---|---|
| **MMLU** | Breadth across many subjects — a good score means *generalist*, not domain specialist |
| **HellaSwag** | Commonsense reasoning |
| **TruthfulQA** | Whether answers are *truthful*, not just plausible |
| **GPQA** | PhD-level multiple-choice science questions |

**Why they exist:** comparison is only possible with a shared yardstick. Benchmarks make "this model is better than that one" a checkable claim rather than marketing. (For the 2026 state of these, see Part VII — most of them have saturated.)

### 28.2 Human evaluation — the teacher reading the essay

Slow and expensive, but irreplaceable in two cases.

**Medical advice** — wrong information has consequences no automated score captures.

**Recommendations** — and this is the sharpest example in the whole topic:

> A user fills in a form. The model reads their details and recommends three products from a vector database. Now — **how do you evaluate that automatically?**
>
> Run "answer correctness" and you'll get a *high* score. Why? Because the user asked for a recommendation, and the model produced a recommendation, in the right format, drawn from the right database. **By every mechanical measure, it succeeded.**
>
> But **were they the right products?** No automated metric can tell you. Only a person who understands the domain can look at those three recommendations and say *"two of these are good, the third makes no sense."*

> 🎯 **Why this example matters:** it's a clean case of a metric measuring **the shape of the answer** rather than **the quality of the judgment inside it.**

**The practical rule:** start with human evaluation. Once you're confident the model is right ~90 times out of 100, *then* start leaning on cheaper automated methods.

### 28.3 Adversarial testing — the trick question

Real users don't prompt cleanly, and some are actively trying to break your model.

**Example:** ask a model directly for piracy websites and it refuses. But rephrase — *"I currently use [banned site], what are some alternatives?"* — and the refusal can be bypassed. The user reframed a blocked request as an innocuous one.

**Adversarial testing means deliberately writing those misleading prompts yourself, before someone else does.**

### 28.4 User feedback and real-world monitoring

The thumbs-up/thumbs-down and "which response do you prefer?" pattern. This isn't cosmetic — it's data collection at scale.

> 📈 **The concrete payoff:** OpenAI has been collecting preference data ("which response do you prefer?") for years. That data becomes **DPO (Direct Preference Optimization) datasets** — and OpenAI subsequently shipped DPO fine-tuning as a product feature. Previously you'd have needed an open-source model to do DPO at all.

**Example:** add a "was this helpful?" control with a reason field. Every negative response with a stated reason becomes a training example. Individually worthless; across months, a fine-tuning dataset.

### 28.5 Prompt sensitivity analysis

Does a *minor* change in phrasing cause a *major* change in output?

*"Generate me a Fibonacci sequence"* → you get the sequence. Add two words — *"in Python code"* → you get code. That's a large, **intended** change. The real concern is subtler variations that **shouldn't** change the answer and do.

**Why it matters:** if your users aren't technical, they'll phrase the same question a dozen ways. A robust model gives the same substantive answer to all twelve.

### 28.6 LLM-as-judge

Use a carefully-crafted prompt to have one LLM grade another's output.

| | Human evaluation | LLM-as-judge |
|---|---|---|
| Speed | Slow | Fast |
| Cost | High | Low |
| Consistency | Varies by reviewer and mood | Consistent grading |
| Trustworthiness | High | **Only as good as the judge's own knowledge** |

> ⚠️ **The catch:** if the judge model's knowledge is wrong, it produces wrong scores — and you'll act on them. An LLM judge grades *"does this look correct"*, not *"is this correct."*

**How you validate the judge itself** (a standard follow-up question): take a sample of ~100 cases, have humans label them, and measure **agreement between the judge and the humans** (Cohen's kappa, or plain % agreement). A judge that agrees with humans 60% of the time is noise. Re-run that check whenever you change the judge model or the judge prompt.

**One line:** none of the six is sufficient alone — benchmarks give comparability, humans give judgment, adversarial testing gives robustness, feedback gives real-world signal, sensitivity analysis gives stability, and LLM-as-judge gives scale. A serious strategy uses several.

---

## 29. Picking a model for your use case

**What exists:** the **Open LLM Leaderboard** — models scored across benchmarks. Useful because a model ranked 6th overall might be **1st at maths**, which matters if maths is your job.

**What doesn't exist:** domain-based filtering ("show me the best model for insurance"). You fall back to searching Hugging Face by keyword and reading model cards.

> 🌍 **The caveat that's easy to miss, and genuinely good interview material:** you might find a model pre-trained on insurance data. But if that insurance data is **US** data and you're serving **Indian** customers, the domain match is an illusion. **Domain and jurisdiction/locale are two different axes**, and matching only one gives you false confidence.

> 🧪 **A good practice worth stealing:** have the evaluation question set written by **someone who didn't build the model**. If you wrote it, you know which questions it handles well, and you'll unconsciously test those. A fresh person finds the failures fast.

**And on knowing what a model actually knows:** only from **what its creators documented**. A Qwen Coder release documented that its SQL training data came from web pages — so you can reasonably trust it on SQL. If someone fine-tunes on finance data, uploads it as "My LLM," and writes no model card, **there's no way to recover that** from the outside. Undocumented provenance is a dead end.

---

## 30. The three metric families

| Family | What it measures | Example metrics |
|---|---|---|
| **Relevance** | Is the response right, given ground truth or retrieved context? | BLEU, ROUGE, perplexity, **faithfulness**, **answer relevancy**, semantic similarity, cosine distance, Levenshtein distance |
| **Alignment** | Does it comply with rules — ours and society's? | Truthfulness, safety, fairness, privacy, regulatory compliance |
| **Task-specific** | Does it do *this particular job*? | Benchmarks and custom/internal datasets |

Quick orientation on the relevance metrics:

- **BLEU / ROUGE** — compare generated text against a reference text. Heavy use in translation and summarisation.
- **Faithfulness** — RAG-specific: given the retrieved context, did the answer stay inside it, or invent beyond it?
- **Answer relevancy** — did it actually address the question asked?
- **Semantic similarity / cosine / Levenshtein** — different ways of measuring "how close are these two pieces of text."

> ⚠️ **Where alignment metrics get honest:** training alone won't get you there. Fine-tuning can't anticipate every compliance rule — **guardrails carry part of this load at runtime.** Back to §26.

> 🔗 **Connection to Week 3:** faithfulness, answer relevancy, and contextual precision/recall are exactly the DeepEval metrics from the RAG evaluation notebook. This section puts those familiar metrics into the wider taxonomy they belong to.

---

## 31. Why LLM evaluation is genuinely hard

Four challenges, each worth being able to name:

**1. A convincing hallucination can score well.** The model invents something that *sounds* consistent with the context. A judge compares answer to context, finds them stylistically aligned, and returns 70% correct. The evaluator was fooled the same way a human skimming would be.

**2. Benchmarks decay — and models learn them.** AI improves fast enough that benchmarks saturate. Worse, once a benchmark is public long enough, models effectively *learn it*. The prescription: **keep updating your benchmarks and make the questions harder over time**, or your scores measure memorisation rather than capability.

**3. Bias in, bias out.** Whatever biases the training data carries, the model inherits. Detecting and countering them is its own hard problem.

**4. A good metric ≠ an understandable answer.** A developer who works in Python, Rust, and SQL asks a C# question. The model returns a technically perfect C# answer — but doesn't explain the C#-specific concepts, so the developer *can't use it.* The metric says 95%. The user is stuck.

> 💭 **All four are the same underlying problem in different clothes: the thing you're measuring is a proxy for the thing you care about**, and proxies drift, saturate, and get gamed.

---

## 32. Model evaluation vs system evaluation ⭐

One of the most useful distinctions in the topic, and a strong signal in interviews because it separates "I ran some metrics" from "I've shipped this."

```
   MODEL EVALUATION                     SYSTEM EVALUATION
   (typically data scientists)          (typically software engineers)
   ─────────────────────────            ────────────────────────────
   Is the ANSWER good?                  Does the SERVICE hold up?

   • answer correctness                 • latency / time-to-first-token
   • faithfulness                       • requests handled, concurrency
   • answer relevancy                   • tokens in / out per user / day
   • hallucination rate                 • active users, conversations/day
   • toxicity, bias                     • GPU / CPU utilisation
                                        • API cost and overuse
                                        • infra + operational cost
                                        • monitoring and security
```

**Example of a system-side failure that no model metric catches:** your faithfulness score is 0.95 and your answers are excellent — but response time is two minutes under real load, so users leave for a competitor. **The model is fine. The product is failing.**

> 🔑 **The key conditional, and it ties Part V to Part VI:** if you're calling OpenAI or Anthropic's API, system evaluation matters less to you — they run the infrastructure. **The moment you self-host an open-weight model, system evaluation becomes yours**, and GPU utilisation, KV-cache pressure, and cost per token stop being someone else's problem.

> 💰 **Idle GPUs are money burning.** If you've provisioned GPUs that sit underutilised, that's an optimisation target as legitimate as any accuracy metric.

---

## 33. The libraries

### G-Eval (via DeepEval)

**What it is:** LLM-as-judge, but with **chain-of-thought reasoning** built in. You define the criteria in natural language; the judge reasons through them step by step before scoring.

**The requirement:** it only works with models actually capable of reasoning — a reasoning-capable frontier model, not a small local one.

**Why it beats plain LLM-as-judge:** the chain-of-thought step makes the evaluation more reliable *and* gives you a **written justification** for the score, not just a number.

```python
coherence_metric.measure(test_case)
print(coherence_metric.score)   # 0.9
print(coherence_metric.reason)  # "logically clear with smooth transitions
                                #  between sentences; tone remains consistent..."
```

**Three worked examples:**

| Input | Metric | Result |
|---|---|---|
| An explanation of machine learning | Coherence (G-Eval) | **0.9** — with a written reason about transitions and tone |
| *"If you read the shipping policy, you would know that delays happen sometimes."* | Toxicity | **0.95 toxic** |
| A RAG answer vs its retrieved context | Faithfulness | **1.0** — "no contradictions, perfect alignment" |

> 💡 **The toxicity example is the instructive one.** That sentence isn't abusive in isolation. It's **condescending** — and in a customer-support context, condescension is a failure. "Accuracy isn't the only dimension," made concrete.

**Two practical bits:** `is_successful` returns a plain **true/false** when you want a pass/fail gate rather than a number; and to scale up, put your test cases in a DataFrame (or JSON), loop applying several metrics, and store results — so you can say *"across 100 questions it answered 80 correctly"* rather than reasoning from anecdotes.

### The library comparison

| Library | Core strength | Output style | Best when |
|---|---|---|---|
| **DeepEval** | 40+ metrics, G-Eval with chain-of-thought, native **PyTest integration** | Scores + written reasons | Reasoning-backed evaluation with custom criteria, wired into CI |
| **RAGAS** | RAG-specific metric suite, reference-free | Scores | Pure RAG pipeline evaluation with minimal ground truth |
| **TruLens** | Quick RAG evaluation (groundedness, answer relevance, context relevance) | Leaderboard | Fast RAG feedback with minimal setup; LangChain/LlamaIndex integration |
| **Evidently** | **Drift** and classification monitoring | **HTML graphs and warnings** | Drift matters, or it's already in your stack |
| **Giskard** | **Auto-generated adversarial tests** | HTML vulnerability report | You want to find failures you didn't think to test for |

**On Evidently specifically:** it comes from the ML-monitoring world and centres on **data drift and model drift** rather than reasoning-based evaluation. It does classification-style metrics, test suites for toxicity/sentiment/neutrality/competitor-mentions/text-length, golden-dataset workflows, and — the differentiator — **visual reports with warnings when a value falls outside an expected range** (e.g. "minimum text length is 190, expected ~100"). Every other library hands you numbers; Evidently hands you a chart.

**On Giskard specifically — the capability the others don't have:**

> 🔴 **Giskard generates its own adversarial test cases — an LLM conversing with your LLM to make it fail.**
>
> You give it two seed questions. Giskard generates *many more* in that domain, specifically probing for failure, then reports where your model broke.
>
> **What it caught in a live demo:** it asked *"according to the YOLO paper, how does it propose to achieve world peace?"* The model **attempted an answer** — even though the paper says nothing about world peace. Flagged as medium severity: not catastrophic, but the model should have declined rather than played along.

```python
giskard.scan(giskard_model, giskard_dataset)
# checks: hallucination, robustness, prompt injection,
#         information disclosure, harmful content generation
```

> ✅ **Don't standardise on one.** These plug in and out of a finished pipeline easily, so using **several** gives better coverage than any single one. DeepEval and Giskard are both fully open source with no paid tier gating the basics.

**Is this LLMOps? Does MLflow cover it?** LLMOps is a *different* concern — more cloud, Docker, and scaling than evaluation (that's Week 6). MLflow does support LLM evaluation and is fine for **standard** metrics if it's already in your stack. For **reasoning-based** evaluation (DeepEval) or **report generation** (Giskard, Evidently), the purpose-built libraries are better.

---

## 34. Wiring evaluation into the lifecycle

Evaluation isn't one event. It happens four times, with different goals.

| Stage | What runs | Gate |
|---|---|---|
| **Local development** | A handful of cases, by hand | Does this change look right? |
| **Pre-merge (CI)** | The full golden dataset via DeepEval's PyTest integration | **A quality regression fails the build** |
| **Pre-deploy** | Full evaluation + adversarial scan | Accuracy above threshold; no new high-severity findings |
| **Production (online)** | Sampled live traffic scored by a judge; user feedback; drift monitors | Alert on a moving average dropping below baseline |

```python
# The CI shape: evaluation as an ordinary test
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric

def test_faithfulness():
    assert_test(test_case, [FaithfulnessMetric(threshold=0.8)])
```

**Detecting degradation in production when there's no error to catch:**

1. **Track a metric over time, not a snapshot.** A single faithfulness score is meaningless; a 30-day moving average that falls from 0.91 to 0.78 is a page.
2. **Watch proxies that need no ground truth** — refusal rate, average answer length, retrieval-score distribution, thumbs-down rate, escalation-to-human rate. All of these move *before* anyone files a bug.
3. **Keep a fixed canary set** running against production daily. Same questions, same expected answers, every day — so a change in score means a change in the system, not a change in the questions.
4. **Sample real traffic and have a judge score it**, with humans reviewing the judge's low-scoring picks.

> ⚠️ **And keep the golden dataset from going stale.** A dataset written eighteen months ago tests the product you had then. Continuously fold in real questions your system got wrong — the annotated production traces from your tracing tool are the cheapest source of new test cases you will ever find.

**One line for Part VI:** evaluation measures before launch and guardrails intervene after; accuracy is one of seven dimensions; no single approach or library suffices; model evaluation and system evaluation are separate jobs that become *both yours* the moment you self-host; and evaluation only counts as engineering once it runs in CI and against live traffic.

---
---

# Part VII — What Changed Since the Course Notes (2026)

The Week 5 materials are accurate for the concepts and slightly behind on several specifics. Each item below is a real change, not a nuance.

### 1. ⭐ ECS Managed Instances is now a distinct third compute option

The course presents a binary: **Fargate** (serverless, no GPU) or **ECS on EC2** (you own and patch the instances). Since late 2025 there is a third: **ECS Managed Instances** — real EC2 instances with full instance-type selection **including GPUs**, but AWS handles patching and lifecycle.

What it enables that Fargate cannot: **GPU workloads, privileged containers, eBPF-based observability and security agents, and tasks needing more than 120 GB of memory.** March 2026 added FIPS-certified Graviton and GPU instances in GovCloud, and EC2 instance-store volumes as a data volume option. **Fractional GPU scheduling** is available on both Managed Instances and ECS on EC2 ([AWS Containers blog](https://aws.amazon.com/blogs/containers/how-ramp-runs-gpu-ai-workloads-at-scale-with-ecs-managed-instances/), [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ecs-mi-supports-fips-graviron-gpu), [InfoQ](https://www.infoq.com/news/2025/10/aws-ecs-managed-instances)).

**Why it matters for the interview answer:** the old rule was *"need a GPU → leave Fargate for ECS on EC2 and accept the ops burden."* The current rule is *"need a GPU → ECS **Managed Instances**, which keeps most of Fargate's operational simplicity."* **Fargate still has no GPU** — that part is unchanged.

### 2. ⭐ Bedrock: `converse` is the default API, not `invoke_model`

The course code uses `invoke_model` with a Mistral-specific `[INST]` payload. The **Converse API** now provides one message-based request and response shape across every Bedrock model that supports messages, plus uniform tool use and streaming — making a model swap a **one-line change**. As of February 2026 the Converse format also works for **batch inference** ([AWS](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-bedrock-batch-inference-supports-converse-api-format/), [AWS docs](https://docs.aws.amazon.com/bedrock/latest/userguide/models-api-compatibility.html)). `invoke_model` is not deprecated, but it is no longer the thing you reach for first.

### 3. ⭐ Ollama is not CPU-only

The course PDF says *"Ollama: designed for developers working with LLMs on **CPUs**, offering greater flexibility but lower performance."* Ollama supports **NVIDIA CUDA, Apple Silicon/Metal, and AMD Radeon** GPUs and uses them automatically. The real vLLM-vs-Ollama distinction is **concurrency**, not hardware: vLLM reaches ~8,000 tok/s at 128 concurrent requests where Ollama reaches ~484 — but **below roughly 5 concurrent users Ollama is actually faster**, because vLLM's batching machinery has fixed overhead ([SitePoint](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/), [tech-insider](https://tech-insider.org/vllm-vs-ollama-2026/)).

### 4. vLLM has moved well beyond PagedAttention

Stable **v0.28.0** (Aug 2026). The **V1 engine** adds a fault-tolerance layer, **multi-tier KV cache offload** (spill to CPU RAM or NVMe rather than evict), compute/communication overlap for MoE models, an async-pipelined scheduler, and **adaptive speculative decoding**. By 2026 vLLM is **the default serving engine for most open-source LLM deployments** ([vLLM docs](https://docs.vllm.ai/en/latest/), [bro-code](https://www.bro-code.in/blog/vllm-v1-engine-beyond-pagedattention), [aifoss](https://aifoss.dev/blog/vllm-review-2026/)).

### 5. GGUF quantisation naming has moved on from "Q2…Q8"

The course lists Q2/Q3 → Q4/Q5 → Q6/Q8. In practice you choose between **K-quants** (`Q4_K_M`, `Q5_K_M`, `Q6_K`) and **I-quants** (`IQ4_XS`, `IQ3_XS`). **`Q4_K_M` is the default recommendation** — a 7–8B model in ~6 GB VRAM, roughly 1% benchmark loss vs FP16, and universal tool support. `IQ4_XS` is smaller at comparable quality *but only with a good importance matrix*, and can be slower on some hardware ([TinyWeights](https://tinyweights.dev/posts/gguf-quantization-levels-q4-q5-q8/), [Kaitchup](https://kaitchup.substack.com/p/choosing-a-gguf-model-k-quants-i)).

### 6. ⭐ Every benchmark the course names has saturated

This is the biggest change in the evaluation half.

| Benchmark | 2026 status |
|---|---|
| **MMLU** | **Saturated.** Frontier models above 88–90%; no longer differentiates ([Stanford HAI AI Index 2026](https://atlan.com/know/llm-benchmarks-explained/)) |
| **HumanEval** | Saturated quickly |
| **GPQA Diamond** | Replaced MMLU as the frontier differentiator — and is **itself now approaching saturation** above 90% |
| **SWE-bench Verified** | Climbed from 60% to near 100% of human baseline in about a year |
| **Humanity's Last Exam** | Built *because* MMLU, MMLU-Pro and GPQA all saturated. 2,500 public questions from ~1,000 domain experts, each designed to stump every frontier model at submission. Best scores rose from **<20% at launch to 46.9% by May 2026** |

> 💬 **The interview-ready version:** *"Public benchmarks saturate and then get learned, so a headline MMLU number tells you almost nothing in 2026. I'd use them for coarse model shortlisting, then evaluate on an internal golden dataset built from my own domain, refreshed continuously from production failures."* That answer demonstrates you know why the course's benchmark list is no longer sufficient.

### 7. DeepEval and RAGAS have diverged in scope

The course presents them as peers. In 2026: **RAGAS stays narrowly focused on RAG** (the triad — faithfulness, answer relevancy, context precision/recall — largely reference-free). **DeepEval has broadened well past RAG** into agent and chatbot evaluation, multi-turn metrics, synthetic data generation, red-teaming, component-level tracing, and **native PyTest/CI integration**. If RAG is part of a larger agent, DeepEval is the better fit; if you want a focused RAG metric suite with minimal ground truth, RAGAS still wins ([DeepEval](https://deepeval.com/blog/deepeval-vs-ragas), [QASkills](https://qaskills.sh/blog/deepeval-vs-ragas-llm-evaluation-2026)).

### 8. Serverless GPU is now a mature category, and cold start is the differentiator

The course covers Cerebrium alone. The category (Cerebrium, Modal, RunPod, Baseten, Beam, Replicate) now competes primarily on **cold start**: Cerebrium and Beam at **2–4 s**, RunPod and Cloud Run mid-range, Baseten at **16–60 s**. Snapshot-restore cuts cold starts by ~71% on average, with the biggest gains on vLLM. RunPod splits **Flex** (scale-to-zero) from **Active** (always warm, ~20% cheaper per hour) ([Modal](https://modal.com/resources/best-serverless-gpu-platforms-inference), [buildmvpfast](https://www.buildmvpfast.com/blog/serverless-gpu-ai-inference-platform-comparison-2026)).

### 9. Hugging Face split into two products worth distinguishing

**Inference Providers** (pay per token, routed to partner providers) vs **Inference Endpoints** (your dedicated GPU, billed per minute, scale-to-zero). The economic crossover: **Providers** at pilot volume, **Endpoints** from roughly **10M–100M+ tokens/month**, **self-hosting** above roughly **500M/month** ([eesel](https://www.eesel.ai/blog/hugging-face-pricing), [techjacksolutions](https://techjacksolutions.com/ai-tools/hugging-face/hugging-face-pricing/)).

### 10. `uv` and multi-stage builds are the 2026 Python container default

`pip install -r requirements.txt` in a single-stage image is correct and slow. Current practice: **multi-stage build** + **`uv` with a pinned version and `uv sync --frozen`** + a pinned base digest + image scanning. Measured effect: 60–80% of removable image weight, with one FastAPI case going 306 MB → 223 MB ([OneUpTime](https://oneuptime.com/blog/post/2026-02-08-how-to-containerize-a-fastapi-application-with-docker/view), [pydevtools](https://pydevtools.com/handbook/tutorial/build-a-production-docker-image-for-a-uv-project/)).

### 11. "Goodput" has entered the standard serving vocabulary

Raw throughput can be high while most requests violate their latency SLO. **Goodput** — throughput filtered to requests that actually met the SLO — is now the metric practitioners report ([Modular](https://handbook.modular.com/llm-inference-basics/llm-inference-metrics/)). Current rules of thumb: **TTFT < 500 ms** for prompts up to 4K tokens; **ITL ≤ ~200 ms**, with **> 250 ms** feeling broken.

---
---

# Part VIII — Rapid-Fire Interview Recall

Twenty questions, one-or-two-line answers. If you can answer all of these out loud, Week 5 is solid.

| # | Question | The answer |
|---|---|---|
| 1 | Why containerise at all? | Environment parity and an immutable, versioned artifact — the image that ran on your laptop is byte-for-byte what runs in production, which also makes rollback a redeploy rather than a repair |
| 2 | Why copy `requirements.txt` before the code? | Layer caching. Otherwise every one-character code edit reinstalls every dependency |
| 3 | `ECR + EC2` vs `ECR + ECS on EC2`? | Control-plane presence. The first is a plain Docker host you babysit; the second delegates task placement, health-based replacement, and scaling to ECS |
| 4 | Fargate vs EC2 launch type — what forces the choice? | **GPU.** Fargate has none. Secondarily, sustained high utilisation makes reserved EC2 cheaper than per-task Fargate |
| 5 | ECR / cluster / task definition / task / service? | Storage / logical compute area / versioned blueprint / one running instance of a revision / the desired-state controller that keeps N running |
| 6 | Where does the API key live? | Secrets Manager, referenced by ARN in the task definition, injected at runtime. Never in the image (it persists in layer history) or the repo |
| 7 | Most common first-deploy failure? | The task execution role lacks `secretsmanager:GetSecretValue` scoped to that secret's ARN |
| 8 | Execution role vs task role? | Execution role = the ECS agent setting the container up (pull image, fetch secrets, write logs). Task role = your *code* calling AWS services at runtime |
| 9 | App is deployed but unreachable — first two checks? | Bound to `localhost` instead of `0.0.0.0`; and no security-group inbound rule for that port |
| 10 | Public IP changes on redeploy — acceptable? | No. Put an ALB in front: stable DNS, health-based routing, connection draining, and it's where HTTPS terminates |
| 11 | Stop vs terminate an EC2 instance? | Stop keeps the EBS volume and you still pay for storage; terminate deletes both |
| 12 | How do you stop someone running up your OpenAI bill? | Don't expose the backend at all (no inbound rule on 8000); then auth, per-principal rate limiting, token caps, caching, billing alarms |
| 13 | What changes if you swap a hosted API for a self-hosted model? | Fargate → ECS Managed Instances/EC2 for GPU; add a serving layer (vLLM/Ollama); cost moves from per-token to per-reserved-hour; **system evaluation becomes yours** |
| 14 | vLLM vs Ollama? | Throughput vs simplicity. vLLM: PagedAttention + continuous batching, ~8,000 tok/s at 128 concurrent. Ollama: one binary, wins below ~5 concurrent users. Both use GPUs |
| 15 | What is PagedAttention? | KV cache split into small non-contiguous blocks allocated on demand, like OS virtual memory. Cuts memory waste to under 4%, so far more requests fit on one GPU |
| 16 | What is GGUF, and which quant? | A self-describing single-file model format (weights + tokeniser + chat template + config). Default to **Q4_K_M** |
| 17 | TTFT vs TPOT vs goodput? | TTFT = prefill, compute-bound. TPOT = per-token decode, memory-bandwidth-bound. Goodput = throughput counting only requests that met the SLO |
| 18 | Evaluation vs guardrails? | Evaluation measures before launch and produces a *score*; guardrails intervene at runtime and produce a *block or rewrite*. You need both |
| 19 | Model evaluation vs system evaluation? | "Is the answer good" vs "does the service hold up under load and cost." Both are LLM evaluation; self-hosting makes the second one yours |
| 20 | Your model scores 90% on MMLU but fails on real users. What happened? | MMLU is saturated and possibly in the training data; it measures generalist breadth, not your domain. Build an internal golden dataset from real traffic and refresh it continuously |

---

## Key Takeaways

1. **Three stacks, not one pile of services** — application (FastAPI, Streamlit), deployment (Docker, ECR, ECS, Fargate), operational (Secrets Manager, CloudWatch, IAM).
2. **Config from environment variables is the design decision that makes deployment boring** — identical code, `.env` locally and injected secrets in production.
3. **Quality gates come before deployment** — mocked pytest, a linter, and an evaluation run. Failing tests must fail the pipeline.
4. **Order Dockerfile instructions least-changed to most-changed**, and never bake a secret into an image.
5. **ECS orchestrates; Fargate, Managed Instances, or EC2 executes** — and **GPU need is the deciding factor**, since Fargate has none.
6. **The task definition is a versioned blueprint**; deploying is a pointer update to a new revision, which is also your rollback path.
7. **Expose only the front door.** Streamlit's port is open, FastAPI's is not; they talk over internal localhost inside the same task.
8. **You pay for reserved capacity, not used capacity.** Right-size, cache, route by difficulty, trim context, and delete everything after experimenting.
9. **Whoever owns the model owns the serving problem.** Managed API → no GPU concerns. Self-hosted → vLLM, KV-cache math, and GPU utilisation become your job.
10. **`Q4_K_M` is the default quant, and a bigger model at Q4 beats a smaller model at Q8** in the same memory budget.
11. **TTFT, TPOT, and goodput** are the serving numbers; **KV cache**, not weights, is what actually limits concurrency.
12. **Evaluation measures, guardrails intervene** — and they happen at different times, on different sides of the deploy.
13. **Accuracy is one of seven dimensions**, and some things (a product recommendation) only a human can score.
14. **Public benchmarks have saturated.** Use them for coarse shortlisting; evaluate on an internal golden dataset refreshed from production failures.
15. **Model evaluation ≠ system evaluation**, and a 0.95 faithfulness score means nothing at a two-minute p99.
16. **What's manual in the console is what CI/CD and Terraform automate later** — and knowing which is which is most of the interview.

---

## Glossary

| Term | Meaning in one line |
|---|---|
| **ALB** | Application Load Balancer — one stable DNS name in front of many healthy tasks |
| **AMI** | Amazon Machine Image — the disk image an EC2 instance boots from |
| **ARN** | Amazon Resource Name — the globally unique ID of any AWS resource |
| **Continuous batching** | Admitting a new sequence the instant an old one finishes, instead of waiting for the whole batch |
| **ECR** | Elastic Container Registry — private Docker image storage |
| **ECS** | Elastic Container Service — AWS's container orchestrator |
| **EKS** | Elastic Kubernetes Service — managed Kubernetes on AWS |
| **Fargate** | Serverless compute for ECS tasks. No servers, no GPU |
| **G-Eval** | LLM-as-judge with chain-of-thought reasoning and a written justification |
| **GGUF** | Self-describing single-file model format: weights + tokeniser + chat template + config |
| **Goodput** | Throughput counting only requests that met their latency SLO |
| **GQA** | Grouped-Query Attention — fewer KV heads than query heads, shrinking the KV cache ~4× |
| **Guardrail** | A runtime intervention that blocks, rewrites, or refuses — as opposed to a measurement |
| **imatrix** | Importance matrix — calibration data that makes I-quants viable |
| **KV cache** | Stored attention keys/values for every token so far; the thing that actually limits concurrency |
| **llama.cpp** | The C++ engine that executes GGUF; Ollama and LM Studio wrap it |
| **Managed Instances** | ECS compute on real EC2 (GPU-capable) where AWS handles patching and lifecycle |
| **PagedAttention** | OS-style paging applied to the KV cache; cuts memory waste to under 4% |
| **Prefill / Decode** | Processing the whole prompt (compute-bound) / generating token-by-token (bandwidth-bound) |
| **Q4_K_M** | The default GGUF quantisation: ~4 bits, K-quant super-blocks, medium variant |
| **Revision** | An immutable version of an ECS task definition; the unit of deploy and rollback |
| **Security group** | Deny-by-default firewall rules on a resource; inbound rules are the ones that bite |
| **Task / Task definition / Service** | A running dish / the recipe card / the manager keeping N dishes on the pass |
| **TTFT / TPOT** | Time To First Token / Time Per Output Token |
| **vLLM** | The 2026 default GPU serving engine: PagedAttention + continuous batching |

---

## Sources

**Course material:** TMLC Academy *Guided Projects in Generative AI* — Week 5 sessions (*AWS Deployment*, 62 min; *Deploying a GenAI Application*, 135 min; *LLM Evaluation*), the `openai-llm-app` reference implementation, and the *Docker and Docker Compose*, *AWS Bedrock*, *Cerebrium*, *Hugging Face Inference Endpoints*, *GGUF*, *LLM Model Serving*, *Ollama*, and *vLLM* readings.

**Web research (2026):**
- [vLLM documentation](https://docs.vllm.ai/en/latest/) · [vLLM V1 Engine: Beyond PagedAttention](https://www.bro-code.in/blog/vllm-v1-engine-beyond-pagedattention) · [vLLM Review 2026](https://aifoss.dev/blog/vllm-review-2026/)
- [Ollama vs vLLM Performance Benchmark 2026 — SitePoint](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/) · [vLLM vs Ollama 2026 — tech-insider](https://tech-insider.org/vllm-vs-ollama-2026/) · [Ollama vs vLLM — Spheron](https://www.spheron.network/blog/ollama-vs-vllm/)
- [How Ramp runs GPU AI workloads with ECS Managed Instances — AWS](https://aws.amazon.com/blogs/containers/how-ramp-runs-gpu-ai-workloads-at-scale-with-ecs-managed-instances/) · [ECS MI supports FIPS Graviton & GPU — AWS](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ecs-mi-supports-fips-graviron-gpu) · [AWS ECS Managed Instances — InfoQ](https://www.infoq.com/news/2025/10/aws-ecs-managed-instances)
- [Bedrock batch inference supports Converse API — AWS](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-bedrock-batch-inference-supports-converse-api-format/) · [Bedrock API compatibility — AWS docs](https://docs.aws.amazon.com/bedrock/latest/userguide/models-api-compatibility.html)
- [GGUF Quantization Levels Explained — TinyWeights](https://tinyweights.dev/posts/gguf-quantization-levels-q4-q5-q8/) · [Choosing a GGUF Model: K-Quants, I-Quants — Kaitchup](https://kaitchup.substack.com/p/choosing-a-gguf-model-k-quants-i) · [IQ4 vs Q4, K_M vs K_S — mustafa.net](https://mustafa.net/llm-quantization-explained/)
- [Hugging Face pricing 2026 — eesel](https://www.eesel.ai/blog/hugging-face-pricing) · [Hugging Face Pricing: The 5 Bills You Actually Pay — TechJack](https://techjacksolutions.com/ai-tools/hugging-face/hugging-face-pricing/)
- [Best Serverless GPU Platforms for Inference 2026 — Modal](https://modal.com/resources/best-serverless-gpu-platforms-inference) · [Serverless GPU Inference Platforms Compared 2026 — buildmvpfast](https://www.buildmvpfast.com/blog/serverless-gpu-ai-inference-platform-comparison-2026)
- [LLM Benchmarks Explained — Atlan](https://atlan.com/know/llm-benchmarks-explained/) · [The Complete Guide to LLM Benchmarks 2026 — AiCE-Lab](https://www.aice-lab.org/posts/features/llm-benchmarks-complete-guide-2026/)
- [DeepEval vs Ragas](https://deepeval.com/blog/deepeval-vs-ragas) · [Top 5 LLM Evaluation Frameworks in 2026](https://deepeval.com/blog/top-5-llm-evaluation-frameworks) · [DeepEval vs Ragas 2026 — QASkills](https://qaskills.sh/blog/deepeval-vs-ragas-llm-evaluation-2026)
- [Key metrics for LLM inference — Modular Handbook](https://handbook.modular.com/llm-inference-basics/llm-inference-metrics/) · [LLM Inference Metrics Reference — Gradient Update](https://gradientupdate.substack.com/p/llm-inference-metrics-reference)
- [Containerizing FastAPI with Docker — OneUpTime](https://oneuptime.com/blog/post/2026-02-08-how-to-containerize-a-fastapi-application-with-docker/view) · [Build a production Docker image for a uv project — pydevtools](https://pydevtools.com/handbook/tutorial/build-a-production-docker-image-for-a-uv-project/) · [Multistage Python Docker Images Using uv — digon.io](https://digon.io/en/blog/2025_07_28_python_docker_images_with_uv) · [FastAPI in Production — LogicLoop](https://www.logiclooptech.dev/fastapi-in-production-the-complete-deployment-guide-docker-workers-scaling-and-best-practices/)

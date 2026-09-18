# Week 5: Baseline Production Deployment of an OpenAI LLM Application

```text
User
  ↓
Streamlit frontend
  ↓
FastAPI backend
  ↓
Prompt and input validation
  ↓
OpenAI Responses API (gpt-4.1-mini)
  ↓
Structured response
  ↓
JSON application logs
```

## API

- `POST /generate` accepts `{"message": "..."}`.
- `GET /health` reports process health and whether OpenAI is configured.
- Interactive API documentation is available at `/docs`.

Example response:

```json
{
  "category": "ORDER",
  "intent": "DELIVERY_DELAY",
  "priority": "MEDIUM",
  "reply": "I’m sorry your order has been delayed. Please share your order number so we can check it."
}
```

## Run locally

Requires Python 3.10+ (the container and CI use Python 3.12).

```powershell
cd openai-llm-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set your real `OPENAI_API_KEY` in `.env`, then start each process in a separate terminal:

```powershell
uvicorn app.main:app --reload --port 8000
```

```powershell
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501`. The API docs are at `http://localhost:8000/docs`.

## Run with Docker Compose

Create `.env` as described above, then run:

```powershell
docker compose up --build
```

- Streamlit: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Stop the stack with `docker compose down`.

## Test and lint

Tests replace the OpenAI service with a mock and do not make paid API calls.

```powershell
ruff check .
pytest
```

## Run the evaluation dataset

This command makes live OpenAI API calls and can incur usage charges:

```powershell
python -m app.evaluation --output evaluation-report.json
```

The report contains field-level accuracy for `category`, `intent`, and `priority`, plus
exact-match accuracy. The generated reply is retained for inspection but is not graded by
exact string matching.

## Deploy

The [beginner AWS Console deployment guide](docs/aws-console-deployment-guide.md) walks through the
complete ECS Fargate setup in the AWS Console. It uses the local terminal only to build and push
the Docker image, and explains how to deploy later updates manually from the ECS Console.

## Project layout

```text
openai-llm-app/
├── app/                      # FastAPI, validation, OpenAI client, evaluation
├── data/                     # Evaluation examples
├── docs/                     # Follow-along AWS deployment guide
├── frontend/                 # Streamlit application
├── tests/                    # API and validation tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Production notes

- The API key is read only from the environment locally and from AWS Secrets Manager on ECS.
- Logs go to stdout as JSON and are collected by the ECS `awslogs` driver.
- Request bodies and API keys are never logged.
- `/health` is a local process/configuration check; it does not call OpenAI or consume tokens.
- The model is configurable with `OPENAI_MODEL` and defaults to `gpt-4.1-mini`.
- The documented direct-public-IP deployment is for a short demo. A production deployment
  should add HTTPS, stable routing, restricted networking, and temporary CI credentials.

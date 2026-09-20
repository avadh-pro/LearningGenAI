# Grafana and Prometheus — Notes

Condensed notes from the TMLC *Grafana and Prometheus* reading, with context from the session transcript (*LLMOps - Transcript.md* in the `LLMOps Overview` folder). Source PDF sits alongside this file.

**The core idea in plain words:** these are two tools doing two different jobs, and the split is the whole thing to understand. **Prometheus collects and stores numbers over time.** **Grafana draws pictures of those numbers.** Prometheus knows that your `/predict` endpoint was hit 9 times and took 340ms on average; Grafana is what turns that into a line on a screen you actually look at.

> 📋 **Everyday analogy:** Prometheus is the nurse who walks the ward every 15 minutes writing vitals onto a chart. Grafana is the chart on the wall at the foot of the bed — the same numbers, arranged so a human can see the trend at a glance. Neither one does the other's job.

**Why this matters here:** Week 3's *Current State of RAG* spent a lot of time on **p99 latency and why you segment it** — by pipeline stage (retrieval vs. reranking vs. generation) and by workload (which index, which tenant) — and set SLO targets like **P50 ≤ 400ms, P90 ≤ 900ms, P95 ≤ 1.5s, P99 ≤ 2.5s**. Week 4's agent architecture then listed **observability** as its seventh layer (latency, token usage, cost, success rate). Both of those were descriptions of *what you should measure*. Prometheus and Grafana are where that measuring physically happens.

---

## 1. Why Monitoring Matters in LLMOps

Running LLMs in production means handling real-time inference, scaling, latency, and GPU usage. Skip monitoring and you get three specific outcomes named in the reading: **unexpected downtime, resource inefficiency, and degraded model performance**.

The transcript sharpens *what* you watch, and it differs from classic MLOps:

| | MLOps monitored | LLMOps monitors |
|---|---|---|
| Typical metrics | R², adjusted R², MSE (regression); F1, precision, recall (classification) | **Tokens, latency, hallucination rate, cost** |
| Drift question | Is the input distribution shifting from training? | Same — plus "are responses degrading, and should we re-tune?" |

> The transcript's framing: *"LLMOps is kind of an extended MLOps with added complexities of LLMs — working with bigger, higher-compute models."*

---

## 2. Prometheus — The Time-Series Database

Prometheus is an open-source monitoring and alerting system built for **time-series data** (a number, tagged with labels, at a timestamp — over and over).

**Four key features from the reading:**

- **Pull-based metrics collection** — Prometheus *scrapes* metrics from your LLM inference endpoints, API servers, and GPU stats.
- **Multi-dimensional data model** — query efficiently with **PromQL** (Prometheus Query Language).
- **Alerting and rule-based monitoring** — trigger on latency spikes, GPU overheating, memory overflows.
- **Long-term storage integrations** — pair with remote storage for extended retention.

> 🔔 **"Pull-based" is the one worth pausing on.** Most people assume the app *sends* its metrics somewhere. Prometheus works the other way round: your app just publishes a `/metrics` page, and Prometheus comes and reads it on a timer.
>
> *Everyday version:* instead of every employee interrupting the manager to report progress, the manager does a round every 15 minutes and reads everyone's whiteboard. If an employee is asleep, the manager notices there's nothing to read — which is itself useful information.

---

## 3. Instrumenting a FastAPI App

For an inference server running FastAPI with a model like Llama 3, you expose a `/metrics` endpoint for Prometheus to scrape. Create `main.py`:

```python
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {"response": "Hello"}

@app.post("/predict")
def read_root():
    response = None   # Call your LLM here
    return response
```

That's the whole instrumentation step — **two lines** (`Instrumentator().instrument(app).expose(app)`) and Prometheus can now collect API metrics automatically. This connects directly to the Week 4 *Serving AI Agent with FastAPI* material: the same FastAPI app that serves your agent becomes the thing being monitored.

---

## 4. Setting Up Prometheus with Docker

`docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

`prometheus.yml` — this is where you tell Prometheus *who to scrape and how often*:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

**Reading that config in plain words:** every **15 seconds**, go to `host.docker.internal:8000/metrics` and write down whatever numbers you find, filing them under the job name `fastapi`.

> ⚠️ `host.docker.internal` is the hostname a container uses to reach the *host machine* — needed because Prometheus is inside Docker but FastAPI is running on your laptop. Getting this wrong is the most common reason the target shows as "down".

---

## 5. Grafana — The Visualization Layer

Grafana is the open-source analytics and dashboarding platform that plugs into Prometheus.

**Why Grafana for LLMOps (from the reading):**

- **Rich visualization** — plot inference latency, GPU utilization, memory consumption.
- **Custom dashboards** — AI-specific panels for token generation speed, API request counts, user query distribution.
- **Alerting and notifications** — integrate with Slack, email, or PagerDuty.
- **Data correlation** — compare multiple metrics side by side to find bottlenecks.

**Adding Grafana to `docker-compose.yml`:**

```yaml
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  grafana-data:
```

**Persisting Grafana data:** mounting the `grafana-data` volume is what makes your dashboards and settings **survive a container restart**. Skip it and every dashboard you built disappears the next time the container cycles — an easy and very annoying mistake.

---

## 6. Wiring Grafana to Prometheus

From the reading, the click path:

1. Open Grafana at `http://localhost:3000` — default credentials **admin / admin**.
2. Go to **Configuration → Data Sources** and select **Prometheus**.
3. Set the URL to `http://prometheus:9090` and save.
4. Create a new dashboard and add visualizations.

Then, when adding a panel:

```
Create Dashboard → Add Visualization → Configure New Data Source
   → paste  http://host.docker.internal:9090/
   → scroll down → Save & Test
```

> 📝 Note the deck uses **two different URLs** for the same Prometheus, and both are correct depending on where you're connecting from: `http://prometheus:9090` works container-to-container (Docker's internal DNS resolves the service name), while `http://host.docker.internal:9090/` routes out via the host. If one fails, try the other.

---

## 7. Project Layout and Running It

The reading restructures the demo into this shape:

```
Grafana-Prometheus Demo
├── src
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
└── prometheus.yml
```

Then, with Docker installed:

```bash
docker-compose up -d
```

Three containers come up — `prometheus-demo`, `grafana-demo`, `fastapi-demo`. Check them in Docker Desktop under **Containers**.

**Access points:**

| Service | URL | Notes |
|---|---|---|
| FastAPI | `http://localhost:8000/docs#/` | Swagger UI — `/metrics`, `/`, `/predict` visible |
| Grafana | `http://localhost:3000/login` | admin / admin |
| Prometheus | `http://localhost:9090/query` | Raw PromQL query interface |

---

## 8. A Real Panel — What You Actually See

Make some random requests to the FastAPI endpoints, then build a panel. The deck's worked example uses the metric **`http_requests_total`** with the legend set to `{{handler}}`, which splits the count out per endpoint:

```
   /      /docs    /metrics   /openapi.json   /predict    none
   2        1         62            1            9          1
```

**Read that like a story:** `/metrics` was hit **62** times — that's Prometheus itself, scraping every 15 seconds. `/predict` got **9** real inference calls. The `{{handler}}` label is what makes this breakdown possible at all, and it's the same idea as **segmenting p99 by workload** from Week 3 — one metric, sliced by a label, so you can see *which* part is misbehaving instead of one blended average.

Once queries are added, save the dashboard; you can keep going back to add more visualization panels.

---

## 9. Beyond the Deck — Where p99 Actually Comes From

*(Not in the reading, but it's the missing bridge to the Week 3 latency material, so worth knowing.)*

A plain counter like `http_requests_total` gives you volume, not latency percentiles. Percentiles come from a **histogram** metric plus PromQL's `histogram_quantile`:

```promql
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, handler)
)
```

That reads as: *"the 99th-percentile request duration over the last 5 minutes, broken out per endpoint."* Swap `0.99` for `0.50` and you have P50. **This is the literal query behind the SLO table from Week 3** — P50 ≤ 400ms, P90 ≤ 900ms, P95 ≤ 1.5s, P99 ≤ 2.5s. The `by (handler)` clause is the segmentation.

---

## 10. What To Monitor, and With Which Tool

The transcript gives a non-exhaustive list of what's worth watching, and — importantly — splits the tooling into **two layers**:

**LLM-level (quality and behaviour):** security threats, data privacy risk, response accuracy, model drift, hallucination scores averaged over a week or month, token usage per day, latency.
→ Tools: **LangSmith** (if you're in a LangChain/LangGraph environment), **Opik**, **LangFuse**.

**System-level (infrastructure and traffic):** requests per second/hour/day, input payload size, output size in KB/MB, uptime vs. downtime, GPU utilization.
→ Tools: **Prometheus + Grafana**, plus things like LogStash.

> 🧭 **This two-layer split is the thing to carry away.** Prometheus and Grafana will happily tell you your endpoint served 9 requests at 340ms — and will tell you *nothing* about whether those 9 answers were hallucinated. That's a different tool (Opik, covered in its own folder). You need both layers; neither substitutes for the other.

**On alerting**, the transcript adds: set alerts for system-down, and for anomalies like GPU usage crossing 80–90% — you get an email warning that the system may crash if usage continues. Note that cloud providers often supply this instance-level anomaly detection natively, so check before rebuilding it.

**On scope**, the speaker deliberately drew monitoring as spanning *both* the deployment side (FastAPI endpoints, model performance) *and* the cloud/infra side (GPU utilization, system load) — "or maybe even spread across all three areas."

---

## Key Takeaways

1. **Two tools, two jobs** — Prometheus collects and stores; Grafana visualizes. Neither replaces the other.
2. **Pull, not push** — your app publishes `/metrics`; Prometheus comes and reads it every `scrape_interval` (15s in the demo).
3. **Instrumenting FastAPI is two lines** — `Instrumentator().instrument(app).expose(app)`.
4. **Mount the `grafana-data` volume**, or your dashboards vanish on restart.
5. **Labels are what make metrics useful** — `{{handler}}` turns one number into a per-endpoint breakdown, the same segmentation logic as p99-by-stage from Week 3.
6. **This layer is blind to answer quality** — Prometheus/Grafana watch the system; Opik/LangFuse/LangSmith watch the LLM. Production needs both.

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape:

- The heading is the question **as asked** — often phrased as a statement to confirm.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- Earlier answers are referred back to ("from Q1") so the picture stays connected.
- A bolded **One line:** summary closes the answer, restating the whole thing in a single sentence.

*(No questions logged yet — the first one asked will be added below as `### Q1:`.)*

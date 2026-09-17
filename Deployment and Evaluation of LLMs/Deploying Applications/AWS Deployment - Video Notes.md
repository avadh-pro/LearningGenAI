# AWS Deployment — Video Notes

Condensed, transcript-based notes from a TMLC Academy session (*Guided Projects in Generative AI*, 62 min) on deploying a GenAI application to AWS. See *AWS Deployment - Transcript.md* in this folder for the full source recording transcript.

**What this session is, and what it deliberately isn't.** It picks up the exact FastAPI setup built in the earlier *Serving AI Agent with FastAPI* session and puts it on AWS so other people can reach it through a link. The instructor is explicit about the scope: this is **not** full DevOps — no custom domain, no SSL certificate, no CI/CD. It's the baseline cloud knowledge a GenAI engineer is expected to have. AWS is the example, but the shape of the process transfers directly to Azure, GCP, or any other provider.

**The one-sentence problem being solved 🌍**

Your app works beautifully — on your laptop, for exactly one person: you. The moment you close the lid, it's gone. Deployment is the act of moving it onto a computer that someone else rents out, keeps switched on, and connects to the internet. Everything below is the mechanics of that one move.

```
BEFORE                                AFTER
┌──────────────┐                      ┌──────────────────────┐
│ your laptop  │                      │ EC2 box in Mumbai    │
│ localhost    │  ← only you          │ 13.234.x.x:8080      │ ← anyone with the link
│ :8000        │                      │ always on            │
└──────────────┘                      └──────────────────────┘
```

---

## 1. AWS in Plain Terms — and the Four Services Worth Knowing

AWS is a **cloud platform**: Amazon rents you computers, storage, and services by the hour so you don't have to buy and run your own. Azure and GCP are the same idea from Microsoft and Google.

The session names four services a beginner should recognise, and focuses entirely on the first:

| Service | What it is | Everyday framing |
|---|---|---|
| **EC2** (Elastic Compute Cloud) | A rented virtual computer you can run anything on | Renting a PC in a data centre and getting the keys |
| **S3** | Bucket storage for files, reachable by other AWS services | A shared hard drive in the cloud |
| **Lambda** | Serverless compute — you supply a function, AWS runs it, no server to manage | A vending machine: it only does something when someone presses a button |
| **Bedrock** | Managed access to foundation models | (Mentioned only; not covered in this session) |

**Load balancing, explained the way the session does it:** imagine your app handles 100 users fine. Then 1,000 arrive at once. A load balancer spins up replicas of your app and spreads the traffic across them so nothing falls over.

> 🎓 **The example everyone recognises:** a university results website that crashes the instant results are published and every student refreshes at the same second. That's exactly the failure a load balancer exists to prevent.

**One line:** EC2 is the one you'll touch first, because it's the least magical — it's just a Linux computer you rent, and everything you already know about Linux still applies.

---

## 2. Before You Click Anything: Account, Free Tier, and Region

Three practical things that catch people out before any code is written:

**Free credits are real, but narrow.** A new account gets a year of free-tier access — but not across every service, and only at the low end. On EC2 that means small instances only; anything powerful is billed. The instructor's own (organisational) account runs around **$50/month**.

**You need a card, and it's picky.** A personal account requires a valid **Visa or MasterCard** credit/debit card — rupee-only debit cards are rejected. On an organisational account, billing shows as zero for you and someone else handles payment.

**Pick your region deliberately.** Choose **Mumbai** or **Hyderabad** rather than a US or European region — it's cheaper, and it's physically closer, so latency is lower.

> 💡 **Why region matters more than it sounds:** an EC2 instance is a real machine in a real building. "Mumbai" means your code runs on hardware in Mumbai. Choosing Virginia because it was the default means every request from an Indian user crosses an ocean and back.

---

## 3. Launching Your First EC2 Instance

From the EC2 dashboard → **Launch instance**. The decisions you're asked to make:

**Name** — anything; the session uses `fastapi-test`.

**Operating system** — **Ubuntu**, not Windows. Lighter, standard for servers, and it's why Linux command familiarity matters.

**Instance type** — this is the "how big a computer" choice:

| Type | When | Note |
|---|---|---|
| `t2.micro` | New account, free-tier eligible | Fine for a small API |
| `t2.medium` | What the session actually uses | Calling the OpenAI API — the heavy lifting happens elsewhere |
| `G4dn`, `P4`-family | Running an **open-source model yourself** | These are the GPU instances |

> 🔑 **The key insight in that table:** the session uses a *tiny* box because the app only calls the OpenAI API — the model runs on OpenAI's hardware, not yours. The moment you host your own open-source model, you need a GPU instance and the cost changes completely.

**GPU shortcut:** under **Browse more AMIs → AWS Marketplace**, search "GPU" for machine images with **NVIDIA drivers pre-installed**, so you skip the driver installation entirely.

**Key pair** — a `.ppk` (or `.pem`) file that proves who you are when connecting. Create one, download it, and **store it somewhere safe** — it's also how you'd let a teammate into the box, or move files with SCP.

**Storage** — Ubuntu defaults to **8 GB**. The session bumps it to **12 GB** as a safety margin, since installing libraries and models eats space fast. Free-tier accounts get **30 GB**.

---

## 4. Connecting to the Box

Select the instance → **Connect** → **Connect** again, and a terminal opens in your browser.

> 🖥️ **The mental model that makes this click:** that terminal is a Linux machine physically sitting in an AWS data centre in Mumbai, with its own IP address. You're operating someone else's computer from yours. Nothing mystical — it's the same Linux you'd run locally, just somewhere else.

**The alternative, for teams:** the browser button works when you own the account. In a real team, you'd get an **SSH key** and connect from your own terminal instead — which is usually how a DevOps team hands out access (credentials plus the `.ppk` file).

**First commands, every time:**

```bash
sudo apt update
sudo apt upgrade      # answer "yes" when prompted
```

Because a library you install later may need a driver or package that's only in the updated repositories.

**Python is already there. `pip` and `venv` are not:**

```bash
sudo apt install python3-pip
sudo apt install python3-venv
```

---

## 5. Getting Your Code Onto the Server

You need to move files from your laptop to the remote box. The tool depends on your OS:

| Your machine | Tool |
|---|---|
| Windows | **WinSCP** (plus PuTTY for the shell) |
| Mac / Linux | **FileZilla**, or plain `scp` from the terminal |

**How to connect WinSCP/FileZilla** — take these from the instance's **Connect** page:

```
Host name  →  the Public IPv4 address
Username   →  ubuntu
Password   →  (none — you use the key instead)
             Advanced → SSH → Authentication → point at your .ppk file
```

Then it's drag and drop. The session creates a folder first (`mkdir app`), refreshes the file browser, and copies the project in — `cd app && ls` on the server confirms the files arrived.

---

## 6. Setting Up Python on the Server

```bash
python3 -m venv env          # create the environment
source env/bin/activate      # activate it — prompt changes to show (env)
pip3 install -r requirements.txt
```

Note **`pip3`** and **`python3`**, not `pip`/`python` — that's the Linux/Mac convention and a common Windows-user stumble.

> ❓ **A genuinely good question from the session: why bother with a virtual environment on a server that's already dedicated to this one app?**
>
> Because "one server, one app" often stops being true. Run two Python services on the same box — say a legacy app that's painful to upgrade and a newer one needing a more recent library version — and their dependencies collide. Separate environments keep that collision from ever happening. You're isolating against the *future* state of the server, not the current one.

**Surviving `vim`** (you'll need it to read or edit `requirements.txt`):

| Goal | Keys |
|---|---|
| Start editing | `i` — "INSERT" appears bottom-left |
| Stop editing | `Esc` |
| Save | `:w` |
| Quit | `:qa` |

---

## 7. Running the App — and the Two Reasons It Won't Work

Run it:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

Then open `http://<Public-IPv4>:8080` in a browser — and it fails. There are **two** distinct reasons, and the session hits both:

**Gotcha 1 — bind to `0.0.0.0`, not localhost.**

> 🚪 **Analogy:** `localhost` (`127.0.0.1`) is like answering the door only for people already inside the house. `0.0.0.0` means "accept knocks from any door, including the street." On your laptop you're always inside, so localhost works. On a server, everyone is outside.

**Gotcha 2 — AWS blocks the port by default.** A new instance refuses all incoming traffic. You must open the port explicitly:

```
Instance → Security → click the Security Group ID
        → Edit inbound rules
        → Add rule:  Custom TCP  |  Port 8080  |  Source: 0.0.0.0/0
        → Save rules
```

Now the page loads: *"Welcome to FastAPI demo"* — and `/docs` gives you the Swagger UI.

> ⚠️ **And a third trap worth naming:** `https://` will not work. HTTPS needs a domain and a real SSL certificate. Without those, it's plain `http://` — which is exactly why this session stops short of "production."

**One line:** if a deployed app is unreachable, it's almost always one of these two — bound to localhost, or the port isn't open in the security group.

---

## 8. Keeping It Alive After You Disconnect

Close the terminal and the app dies. The run command was a child of that shell session, so it's terminated along with it.

**Fix 1 — `nohup`** ("no hangup"): prefix the command and it detaches from the terminal.

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8080 &
```

Close the terminal now and the app keeps serving.

**Stopping a `nohup` process** — you can't just Ctrl-C it, because you no longer have its terminal. Find it and kill it:

```bash
ps -ef | grep uvicorn      # find the process; note the PID (e.g. 11240)
kill 11240
```

> 🔁 **Why you'll do this constantly:** update your code, try to restart, and you get `address already in use` — the old process is still holding port 8080. Find, kill, rerun.

**Fix 2 — `tmux`**, once you're running more than one service. `nohup` works but becomes untrackable: several background processes, no clear picture of what's running where.

```bash
tmux new -s fastapi        # named session — far better than the default 0, 1, 2...
# ... activate env, run your service ...
# Ctrl+B then D            → detach, leaving it running
tmux list-sessions         # what's running?
tmux attach -t fastapi     # go back into it
tmux kill-session -t fastapi
```

| | `nohup` | `tmux` |
|---|---|---|
| What it does | Detaches one command from the terminal | Gives you whole terminal sessions you can leave and re-enter |
| Can you go back in and look? | No — it's just a background process | Yes, `attach` returns you to the live session |
| Good for | One service, fire and forget | Several services, each in a named session |
| Stopping it | `ps -ef \| grep` then `kill <pid>` | `tmux kill-session -t <name>` |

> ⚠️ **Worth knowing beyond the session — neither of these is production-grade.** `nohup` handles hangup signals; `tmux` gives you a re-attachable session. Neither restarts your app if it **crashes**, and neither survives a **server reboot**. Real deployments use **systemd** (process supervision, auto-restart, log handling, starts on boot) or **Docker** with a restart policy. For learning and demos, `nohup`/`tmux` are exactly right — just don't mistake them for the finished answer.

---

## 9. Running Several Services Side by Side

The session runs FastAPI and Streamlit together, one `tmux` session each:

```
tmux session "fastapi"    → uvicorn on port 8080
tmux session "streamlit"  → streamlit on port 8501
```

Two things to remember:

1. **Each `tmux` session is a fresh terminal** — you must re-activate the virtual environment inside every one.
2. **Every new port needs its own inbound rule.** Streamlit on 8501 won't be reachable until you add that port to the security group too — the same step as before, repeated per port.

Named sessions pay off immediately here: `tmux list-sessions` showing `fastapi` and `streamlit` tells you what's running at a glance, where `0` and `1` would tell you nothing.

---

## 10. The Two Things That Actually Hurt: Billing and Security

**Terminate your instances.** The single most important habit. An instance you forgot about bills continuously.

| Action | What happens | Still charged? |
|---|---|---|
| **Stop** | Instance shuts down, disk (EBS) kept | Yes — you still pay for storage |
| **Terminate** | Instance and its storage deleted | No |

> 💸 **Learn from the session's own stories:** the instructor racked up bills in college (saved only by free credits), and separately was billed **₹2.5 lakh** when their account was compromised and attackers spun up instances across every region.

**Turn on MFA.** That second story is exactly why. Multi-factor authentication on the root account is the cheapest insurance in cloud computing.

---

## 11. Where This Goes From Here

The session closes by pointing at the next rungs:

- **Docker on EC2** — works exactly as it does locally. Docker isn't pre-installed; install it, copy your `Dockerfile`/`docker-compose.yml` up, open the ports, and run. Same rules.
- **ECR + GitHub Actions** — push images to Amazon's container registry and automate deployment on every commit, instead of dragging files over WinSCP.
- **Domains and SSL** — the piece deliberately skipped, and what turns `http://13.234.x.x:8080` into `https://yourapp.com`.

---

## Key Takeaways

1. **Deployment is just "move it onto a computer someone else keeps switched on."** EC2 is a rented Linux box; every Linux skill you have still applies.
2. **Instance size follows where the model runs.** Calling an external API? A tiny `t2.medium` is plenty. Hosting your own open-source model? You need GPU instances, and the economics change entirely.
3. **Two gotchas cause nearly every "it's not loading":** binding to `localhost` instead of `0.0.0.0`, and forgetting the security-group inbound rule. Check both first, every time.
4. **A process dies with its terminal** — `nohup` for one service, `tmux` for several. Neither is production-grade; that's `systemd` or Docker.
5. **Every new port needs its own inbound rule.** Two services means two rules.
6. **Terminate, don't just stop** — stopped instances still bill for storage. And enable MFA, because a compromised account gets mined across every region.
7. **The process transfers.** Pick a region, launch a box, copy code, install deps, run it, open the port. That sequence is the same on Azure, GCP, or anywhere else.

---

## 🎤 Interview Prep — Mock Interview (Cloud Deployment for GenAI, ~4-5 Years' AI Engineering Experience)

*Curated from current (2026) AWS and AI-engineering interview question banks, calibrated to what's expected of a GenAI engineer — not a dedicated DevOps or infrastructure engineer. Same two-layer format as this repo's other Video Notes files: a plain-language answer with an everyday example, then a crisp, technically precise version. Try answering out loud first.*

---

**🎙️ Interview Q1:** "You've built a GenAI service. Walk me through choosing between EC2, Lambda, and SageMaker to host it."

**✅ Strong answer:** "It comes down to how much control I need, how predictable the traffic is, and how much infrastructure I want to own. **EC2** is a plain rented machine — maximum flexibility, I install whatever I want, but I'm responsible for keeping it running, patched, and scaled. **Lambda** is serverless: I hand over a function and pay only while it's actually executing, which is ideal for sporadic, bursty traffic — but it has execution time limits and cold starts, so it's a bad fit for anything long-running or latency-sensitive. **SageMaker** is the managed ML path — endpoints, blue-green deployment, and monitoring come built in, which is where I'd go for a production model endpoint that needs to be reliable without me building that plumbing myself. For a first deployment or something unusual, EC2; for spiky lightweight inference, Lambda; for a production ML endpoint, SageMaker."

**🎯 Standard Interview Answer:** "The decision is driven by operational ownership, traffic profile, and customization requirements. EC2 offers full control over the runtime environment at the cost of undifferentiated heavy lifting — patching, scaling, and supervision are yours. Lambda eliminates idle cost and scales automatically, but its execution ceiling, cold-start latency, and stateless model make it unsuitable for long-running or GPU-bound inference. SageMaker endpoints provide managed deployment primitives — autoscaling, blue-green and canary rollout, and CloudWatch integration — and are the default for production ML serving. A common pattern is EC2 or a container service for custom inference stacks (vLLM, TGI) where SageMaker's abstractions get in the way, and SageMaker where its lifecycle tooling earns its overhead."

---

**🎙️ Interview Q2:** "Your FastAPI service runs fine in the EC2 terminal, but the browser can't reach it. Debug it for me."

**✅ Strong answer:** "There are two classic causes and I'd check them in order. First, **what address is the app bound to?** If it's bound to `127.0.0.1`, it only accepts connections originating on that machine — it's answering the door only for people already inside the house. On a server everyone is outside, so it has to bind `0.0.0.0` to listen on all interfaces. Second, **is the port open in the security group?** A new EC2 instance blocks all inbound traffic by default. You add a Custom TCP inbound rule for that port before anything external can reach it. If both are correct and it's still failing, I'd check I'm using `http://` not `https://` — HTTPS needs a domain and a real certificate, which a bare IP doesn't have. Beyond that, confirm the process is actually alive with `ps -ef | grep`."

**🎯 Standard Interview Answer:** "Debug from the inside out. (1) Binding: confirm the server binds `0.0.0.0` rather than the loopback interface — `--host 0.0.0.0` for uvicorn. (2) Security group: inbound rules default-deny, so the listening port needs an explicit Custom TCP allow rule scoped to an appropriate CIDR. (3) Scheme: without an attached domain and ACM/Let's Encrypt certificate, only HTTP will resolve. (4) Verify the process is running and bound as expected — `ps -ef | grep`, `ss -tlnp`. Escalating further: NACL rules at the subnet level, route table and internet gateway attachment, and whether the instance has a public IPv4 at all."

**🔁 Interview Q2 (follow-up):** "You said security groups default-deny inbound. How do they differ from network ACLs, and when would a request get through one but not the other?"

**✅ Strong answer:** "Security groups sit at the **instance** level and are **stateful** — if you allow traffic in, the reply is automatically allowed back out, you don't write a return rule. They only support *allow* rules. Network ACLs sit at the **subnet** level and are **stateless** — every direction needs its own explicit rule, including the ephemeral return ports — and they support both *allow* and *deny*, evaluated in rule-number order. So a request can pass the security group and still be dropped by a NACL deny rule on the subnet, or the inbound request can succeed while the *response* is blocked because the NACL has no outbound rule for the ephemeral port range. Security groups are the fine-grained tool; NACLs are the coarse subnet-wide guardrail."

**🎯 Standard Interview Answer:** "Security groups are stateful, instance-level, allow-only, and evaluated as a union across all attached groups. NACLs are stateless, subnet-level, support explicit deny, and are evaluated in ascending rule-number order with first-match semantics. The classic asymmetry: a stateless NACL requires an explicit outbound rule covering the ephemeral port range (1024-65535) for return traffic, so a permissive inbound NACL with a restrictive outbound one will complete the handshake inbound and drop the response. Practically, NACLs are used for broad subnet-level denies — blocking a CIDR — while security groups carry per-workload access policy."

---

**🎙️ Interview Q3:** "How should an EC2 instance get credentials to call S3 or another AWS service?"

**✅ Strong answer:** "Through an **IAM role attached to the instance**, never by putting access keys in a file or environment variable. The instance picks up temporary, automatically-rotating credentials from the instance metadata service, so there's no long-lived secret sitting on disk that can leak in a backup, a log, or a git commit. The role gets only the permissions that workload actually needs — if it reads one S3 bucket, that's what the policy grants, not blanket S3 access. And I'd enforce IMDSv2, which requires a session token and blocks the SSRF-style attacks that could otherwise read credentials off the metadata endpoint."

**🎯 Standard Interview Answer:** "Attach an IAM instance profile. The instance retrieves short-lived STS credentials via the Instance Metadata Service, eliminating static key material on the host and giving automatic rotation. The role's policy should follow least privilege — resource-scoped ARNs and specific actions rather than wildcard grants — and IMDSv2 should be enforced (`HttpTokens: required`) to mitigate credential exfiltration through SSRF. Long-lived IAM user access keys on an instance are an anti-pattern: they don't rotate, they persist in AMIs and snapshots, and they're a top source of credential leakage."

---

**🎙️ Interview Q4:** "You discover AWS access keys have been committed to a public GitHub repo. What do you do?"

**✅ Strong answer:** "Treat it as an active compromise, not a mistake to quietly fix. **Deactivate and delete those keys immediately** — rotating is the priority, before anything else, because automated scanners find public keys within minutes. Then **look at what was done with them**: CloudTrail to see every API call made with that key, and check every region for resources you didn't create — compromised accounts typically get used to spin up expensive GPU instances everywhere at once. Remove the offending commit, but understand that git history means the key is still recoverable from the repo — which is exactly why revocation comes first and rewriting history second. Then fix the cause: move to IAM roles so there's no static key to leak, and enable MFA and billing alerts to catch it faster next time."

**🎯 Standard Interview Answer:** "Immediate containment: deactivate then delete the exposed key pair via IAM — revocation precedes remediation, since public keys are harvested by automated scrapers in minutes. Then scope the blast radius: query CloudTrail for all activity attributable to that access key ID, and audit every region (not just your usual one) for anomalous resource creation, particularly GPU instance families. Purge the credential from git history (BFG or filter-repo) recognising that history rewriting is not a containment control. Root cause: replace static user keys with instance profiles or IAM Identity Center short-lived credentials, enable MFA, add GuardDuty and budget alarms, and add pre-commit secret scanning to prevent recurrence."

---

**🎙️ Interview Q5:** "Your app stops the moment you close the SSH session. Explain why, how you'd fix it quickly, and what you'd actually run in production."

**✅ Strong answer:** "The process is a child of the shell session, so when the session ends it receives a hangup and dies with it. The quick fixes are **`nohup`**, which detaches a single command from the terminal, or **`tmux`**, which gives you a whole terminal session you can detach from and re-attach to later — much better once you're running several services, especially with named sessions. But neither is what I'd run in production. `nohup` handles the hangup signal; `tmux` handles session persistence. Neither one restarts the app if it **crashes**, and neither survives a **server reboot**. For production I'd use **systemd** — it supervises the process, restarts on failure, handles logging, and starts the service on boot — or run the app in **Docker** with a restart policy, which gets you the same guarantees plus a reproducible environment."

**🎯 Standard Interview Answer:** "Terminating the controlling terminal sends SIGHUP to its foreground process group. `nohup` suppresses SIGHUP for a single command; `tmux`/`screen` reparent the process into a persistent multiplexer session that survives disconnection. Neither provides process supervision: no automatic restart on non-zero exit, no boot-time startup, no cgroup-scoped resource limits, no integrated log management. Production requires a supervisor — a systemd unit with `Restart=always` and journald integration, or a container orchestrated with a restart policy — plus a health endpoint so the supervisor or load balancer can detect a hung-but-alive process, which a bare restart policy will not catch."

**🔁 Interview Q5 (follow-up):** "If `tmux` keeps the session alive, why isn't that enough?"

**✅ Strong answer:** "Because `tmux` solves the wrong half of the problem. It keeps the *session* alive, not the *program*. If the app throws an unhandled exception and exits, `tmux` faithfully preserves an empty shell where your service used to be — it has no idea anything was supposed to be running. And if the box reboots for a patch, every `tmux` session is gone with it. Session persistence and process reliability are two different guarantees, and only a supervisor gives you the second one."

---

**🎙️ Interview Q6:** "How would you pick an EC2 instance type for an LLM workload, and how would you keep the bill under control?"

**✅ Strong answer:** "First question: **is the model running on my hardware at all?** If the app just calls the OpenAI or Anthropic API, the heavy compute is on their side and a small CPU instance is plenty — paying for a GPU would be pure waste. If I'm hosting an open-source model myself, then I need GPU instances, and the family depends on the job: the **G-series** (G5/G6) is the cost-effective choice for inference, the **P-series** (P4d/P5) is for serious training, and **Inf2** with AWS's Inferentia chips often beats GPUs on price-performance for pure inference. For cost control: right-size rather than guessing big, use **spot instances** for training since they're 60%-plus cheaper and training can checkpoint and resume through an interruption — but never for a live endpoint, because a two-minute eviction notice takes your service down. Pick a nearby region, and terminate anything idle."

**🎯 Standard Interview Answer:** "Start by locating the compute: API-based inference is network-bound and needs no accelerator, so CPU instances suffice. Self-hosted inference is memory-bandwidth and VRAM-bound — size to model weights plus KV cache, favouring G-family (A10G/L4) for cost-effective serving, P-family (A100/H100) for training and very large models, and Inf2 where the model is supported, given its price-performance advantage for inference. Cost levers in order of impact: spot capacity for interruption-tolerant training (60%+ discount, requires checkpointing and eviction handling), right-sizing informed by observed utilisation rather than provisioned peak, Savings Plans or Reserved Instances for steady-state baseline load, regional selection, and rigorous teardown of idle capacity. Spot is inappropriate for stateful serving endpoints without a fallback capacity pool."

**🔁 Interview Q6 (follow-up):** "You stopped your instances over the weekend. Are you still being charged?"

**✅ Strong answer:** "Yes — for storage. **Stopping** an instance releases the compute, so you stop paying hourly for the machine, but the EBS volume attached to it still exists and is still billed, because AWS is holding your disk for you. **Terminating** deletes the instance and, assuming delete-on-termination is set, the volume with it — that's when the charges genuinely end. There are other things that quietly bill while 'stopped' too, like an Elastic IP that isn't attached to a running instance. The habit that matters is: stop when you'll be back tomorrow, terminate when you're done."

---

**🎙️ Interview Q7:** "You're deploying to a server dedicated entirely to this one application. Why still bother with a virtual environment?"

**✅ Strong answer:** "Because 'dedicated to one app' has a habit of not staying true. The moment a second Python service lands on that box — a small internal tool, a scheduled job, an older service nobody wants to migrate — their dependencies compete. One needs an older library pinned, the other needs the latest, and without isolation one of them breaks. A virtual environment costs nothing to create and removes that entire class of failure. It also makes the deployment reproducible: `requirements.txt` plus a fresh venv rebuilds the exact environment anywhere, rather than depending on whatever happens to be installed system-wide. And it keeps you out of the system Python, which the OS itself depends on."

**🎯 Standard Interview Answer:** "Isolation is about the future state of the host, not its current state. Co-tenanted Python services create transitive dependency conflicts that are unresolvable at the system-packages level, and mutating the distribution's Python can break OS tooling that depends on it. A venv gives per-application dependency resolution, reproducible rebuilds from a pinned manifest, and a clean uninstall path. Containers solve the same problem more completely by isolating the OS layer too — a venv is the minimum viable isolation when you're deploying directly onto a host."

---

**🎙️ Interview Q8:** "Take the deployment we just described — FastAPI on EC2, started with nohup, port opened to the world — and tell me what's wrong with it for production."

**✅ Strong answer:** "Quite a lot, and that's fine because it was never meant to be production. **Availability:** one instance means one point of failure, and `nohup` means no restart on crash and nothing after a reboot. **Security:** the port is open to `0.0.0.0/0`, so anyone on the internet can hit it — it should be restricted, ideally behind a load balancer, with the instance itself in a private subnet. There's no HTTPS, so traffic is unencrypted. **Scalability:** no load balancer, no autoscaling, so a traffic spike takes it down. **Operations:** no monitoring, no alerting, no centralised logs, and deployment is dragging files over WinSCP by hand rather than a repeatable pipeline. The upgrade path is: containerise it, put it behind an Application Load Balancer with a certificate, run it under systemd or in an orchestrator across at least two availability zones, wire up CloudWatch, and automate deploys through ECR and GitHub Actions."

**🎯 Standard Interview Answer:** "Gaps across four axes. Availability: single instance, single AZ, no supervision or restart policy. Security: unrestricted ingress CIDR, no TLS termination, public subnet exposure, and manual file transfer as the deployment mechanism. Scalability: no horizontal scaling or load distribution; vertical capacity is the only lever. Operability: no metrics, structured logging, alerting, or health checks, and no reproducible deployment artifact. Remediation path: containerise for a reproducible artifact, push to ECR, deploy across multi-AZ behind an ALB with ACM-managed TLS, run instances in private subnets fronted by the load balancer, add an autoscaling group with health-check-driven replacement, and automate the release through CI/CD."

---

**🎙️ Interview Q9:** "What's the difference between an AMI, an instance, and an EBS volume?"

**✅ Strong answer:** "An **AMI** is the template — a snapshot of an operating system and whatever's pre-installed on it, like a fresh OS install image. You don't run an AMI; you launch *from* it. The **instance** is the running machine created from that template. The **EBS volume** is the virtual hard disk attached to that instance, where its data actually lives. The relationship is: AMI is the blueprint, instance is the house built from it, EBS is the house's storage. This matters practically — a GPU AMI from the marketplace is just a blueprint with NVIDIA drivers already baked in, which saves you installing them. And it's why stopping an instance still bills you: the instance is off, but the EBS volume is still sitting there holding your data."

**🎯 Standard Interview Answer:** "An AMI is an immutable launch template comprising a root volume snapshot, launch permissions, and block device mapping. An instance is a running virtualised compute resource instantiated from an AMI. EBS volumes are network-attached block storage devices bound to an instance, persisting independently of the instance lifecycle subject to the delete-on-termination flag. Practically: custom AMIs bake dependencies to cut boot and configuration time (the marketplace GPU AMIs pre-install CUDA/NVIDIA drivers), EBS persistence explains continued storage charges for stopped instances, and snapshots of EBS volumes are the basis for creating new AMIs."

---

**🎙️ Interview Q10:** "How would you deploy the same application to Azure or GCP instead? How much of what you know transfers?"

**✅ Strong answer:** "Almost all of it, because the shape of the process is identical — only the product names change. Pick a region near your users, launch a virtual machine (EC2 → Azure Virtual Machines → GCP Compute Engine), connect over SSH, copy your code up, install dependencies, run the service bound to all interfaces, and open the port in the provider's firewall — security groups on AWS, network security groups on Azure, VPC firewall rules on GCP. The managed-service equivalents map across too: S3 to Blob Storage or Cloud Storage, Lambda to Azure Functions or Cloud Functions. What genuinely differs is the IAM model and the specifics of managed ML services, which is where you'd actually need to relearn. That's exactly why the session taught EC2 rather than a managed service — the fundamentals port everywhere."

**🎯 Standard Interview Answer:** "The IaaS abstraction is near-identical across providers: region selection, VM provisioning from an image, key-based SSH access, host-level firewall configuration, and process supervision. Service mapping is largely one-to-one — EC2/Azure VMs/Compute Engine, S3/Blob Storage/Cloud Storage, Lambda/Azure Functions/Cloud Functions, security groups/NSGs/VPC firewall rules. Meaningful divergence appears in identity models (IAM roles versus Azure managed identities versus GCP service accounts), networking primitives, and the managed ML platforms (SageMaker versus Azure ML versus Vertex AI), where abstractions and pricing differ substantially. Deploying at the IaaS layer maximises portability at the cost of assuming operational burden the managed platforms would absorb."

---

**What interviewers are really scoring for, across all of the above:**
- Whether you debug with a **method** (binding → security group → scheme → process) rather than guessing service by service
- Whether you know the difference between what works in a demo and what holds in production — and can say so without being asked
- Whether security answers reach for **IAM roles and least privilege** naturally, instead of "put the key in an environment variable"
- Whether cost awareness is concrete (spot economics, stop-versus-terminate, right-sizing) rather than a vague "use the cheapest instance"
- Whether you can locate where the compute actually happens — calling an API versus hosting weights yourself completely changes the infrastructure answer
- Whether you can name a trade-off rather than declaring one service universally correct

**Sources consulted while calibrating this section:**
- [50+ AWS Interview Questions and Answers — GeeksforGeeks](https://www.geeksforgeeks.org/cloud-computing/aws-interview-questions/)
- [Top 50+ AWS Interview Questions and Answers for 2026 — DataCamp](https://www.datacamp.com/blog/top-aws-interview-questions-and-answers)
- [AWS Interview Questions and Answers (2026) — Devinterview.io (GitHub)](https://github.com/Devinterview-io/aws-interview-questions)
- [50 AWS AI Engineer Interview Questions (2026) — Digiqt](https://digiqt.com/blog/interview-questions-for-aws-ai-engineers/)
- [Amazon Machine Learning Engineer Interview Guide (2026) — Exponent](https://www.tryexponent.com/guides/amazon-machine-learning-engineer-interview)
- [SageMaker and beyond: Exploring options for deploying ML models on AWS](https://annpastushko.substack.com/p/sagemaker-and-beyond-exploring-options)
- [EC2 vs Containers vs Lambda: How I Think About AWS Compute](https://ravindrasinghshah.substack.com/p/ec2-vs-containers-vs-lambda-how-i)
- [EC2 GPU Instances: A Full Guide to AWS GPUs (2026) — Thunder Compute](https://www.thundercompute.com/blog/ec2-gpu-instances)
- [AWS GPU Instance Pricing: P5, P4d, G5, Inf2 — Wring](https://wring.co/blog/aws-gpu-instance-pricing-guide)
- [How To Choose AWS EC2 Instance Types For Cost Optimization — nOps](https://www.nops.io/blog/aws-ec2-instance-types/)
- [After SSH Disconnects, Is Your Program Still Running? nohup vs tmux vs systemd — Termark](https://www.termark.app/blog/ssh-session-persistence)
- [Run Python in Production with systemd: 2026 Guide](https://khimananda.com/blog/run-python-in-production-with-systemd)
- [Deploying Server Applications the Right Way: Why systemd Quietly Powers Production — Stackademic](https://blog.stackademic.com/deploying-server-applications-the-right-way-why-and-how-systemd-quietly-powers-production-system-8a2b24d8c81c)

---

## Q&A

Every question asked while working through this file gets logged here, numbered sequentially as `### Q1:`, `### Q2:` … Each answer follows the same shape used across this repo's other Video Notes files:

- The heading is the question **as asked**.
- A one-sentence **bolded verdict** opens the answer, using ✅ / ❌ for confirm-or-correct questions.
- A concrete **analogy** carries the explanation, plus a comparison table when two concepts are being contrasted.
- A bolded **One line:** summary closes the answer.

### Q1: If we learn AWS deployment, does it transfer to GCP, Azure, or any other cloud?

**✅ Correct at the concept level, ❌ not at the command level.** The mental model transfers almost completely; almost none of the specific names or commands do.

**What genuinely transfers — the shape:**
- Rent a machine → SSH in → install your runtime → run the app → open a port. Identical everywhere.
- The building blocks are the same six on every cloud: **compute, storage, networking, identity, secrets, logs**.
- The two "why isn't it reachable" bugs — binding to `localhost` instead of `0.0.0.0`, and the firewall rule not being open. Every cloud, same two bugs.
- The container workflow: build image → push to a registry → run it on an orchestrator.
- Cost instincts: billed per hour, and *stopped* ≠ *deleted* (you still pay for the disk).

**What doesn't transfer — every proper noun:**

| Concept | AWS | GCP | Azure |
|---|---|---|---|
| Virtual machine | EC2 | Compute Engine | Virtual Machines |
| Image registry | ECR | Artifact Registry | ACR |
| Run containers | ECS / Fargate | Cloud Run / GKE | Container Apps |
| Firewall rule | Security Group | VPC firewall rule | Network Security Group |
| Permissions | IAM | Cloud IAM | Entra ID + RBAC |
| Secrets | Secrets Manager | Secret Manager | Key Vault |
| Logs / metrics | CloudWatch | Cloud Logging | Azure Monitor |

**⚠️ One caveat the session's claim glosses over:** the *easiest path* differs per cloud. GCP's Cloud Run is genuinely simpler than AWS's ECS/Fargate — you hand it a container and it runs. Someone who learned the AWS way can end up over-engineering on GCP, building cluster/service/task-definition scaffolding that Cloud Run doesn't need. It's not a clean 1:1 mapping; some clouds have a meaningfully shorter route.

**And the thing that actually makes you portable isn't the AWS knowledge — it's Docker.** A container image runs unchanged on any of the three. The container is the portable artifact; the cloud is just where you point it.

**One line:** learning AWS deployment means you'll know *what to look for* on GCP or Azure within an hour of reading their docs — but you'll be looking up every command, because the concepts are shared and the vocabulary isn't.

---

### Q2: What is an EC2 instance, in one line?

**An EC2 instance is a computer you rent from Amazon by the hour** — you pick the CPU/RAM/GPU size, it boots in the cloud, and you SSH into it and use it like any Linux machine.

**Example:** instead of your FastAPI app running on your laptop at `localhost:8000` — where only you can reach it, and it dies when you close the lid — it runs on an EC2 instance with a public IP: always on, reachable by anyone you give the link to.

**One line:** it's a rented Linux box in Amazon's data centre, billed by the hour, that you treat exactly like a normal server.

---

### Q3: Explain Lambda ("serverless compute") well enough to discuss it in an interview.

**Lambda means you don't rent a computer at all — you hand AWS a function, AWS runs it only when something triggers it, then it disappears. You pay per run, measured in milliseconds.**

**🚗 The analogy:** EC2 is **buying a car** — yours, parked outside, costing you money whether you drive it or not. Lambda is **calling an Uber** — it appears when you need it, it's gone when you're done, and you pay per trip.

**Worked example — a Slack bot answering questions with an LLM.** The function does three things: receive the message → call the LLM API → post the reply. It runs about 2 seconds.

| | EC2 | Lambda |
|---|---|---|
| Running when nobody messages | A server, idling, billing you | Nothing |
| Cost for ~10k messages/month | ~$15/mo (always-on t3.small) | Cents |
| Spike to 500 at once | You scale it yourself | Scales automatically, no config |
| Who patches the OS | You | Nobody — there's no OS you own |

**More real-world cases** — the pattern is always *something happens → Lambda wakes up → does one short job → disappears*:

- **Thumbnail generation** — photo uploaded to S3 → Lambda resizes it → saves it back. 1,000 uploads at once spawn 1,000 parallel runs with zero configuration.
- **RAG document ingestion** *(most relevant to this repo)* — a PDF lands in S3 → Lambda extracts text, chunks it, calls the embedding API, writes vectors to Qdrant/Pinecone. Event-driven, seconds long, and bursty — 50 uploads at 10am, nothing until Thursday.
- **Scheduled daily report** — 8:00am trigger → query the DB, have an LLM summarise it, email the team. Thirty seconds of work per day.
- **Payment webhook** — Stripe posts "payment succeeded" → Lambda updates the DB and sends the receipt.
- **Slack slash command** — `/summarize` → Lambda → LLM → reply posted back.

**The limits — knowing these is what makes the answer sound used rather than read:**
1. **Cold starts.** If the function hasn't run recently, AWS spins the environment up first — a 1-3 second delay on that first request. Fine for a Slack bot, painful for a user watching a spinner.
2. **15-minute maximum runtime.** Long jobs can't live here.
3. **No GPU**, plus tight package-size limits.

**Where Lambda is the wrong tool:**

| Task | Why it fails |
|---|---|
| Fine-tuning a model | Takes hours; Lambda caps at 15 minutes, and there's no GPU |
| Serving your own Llama weights | Weights exceed the package limit, no GPU, and cold-starting gigabytes per request is brutal |
| WebSocket chat server | Lambda is request-in/response-out — it can't hold a connection open |
| Steady 24/7 traffic | At constant load Lambda costs *more* than simply renting an EC2 box |

That last row is the nuance interviewers like: **Lambda isn't automatically cheaper.** It wins on *bursty* traffic.

**🎯 The GenAI-specific point worth landing in an interview:** *"Lambda is great for **calling** an LLM and wrong for **hosting** one. A thin function that takes a request, hits the OpenAI or Bedrock API, and returns the answer is a perfect Lambda — short, bursty, stateless. But serving your own model weights there doesn't work: no GPU, the model won't fit the package limits, and the cold start would mean loading gigabytes of weights before answering. That's when you move to EC2 with a GPU, or a managed endpoint."*

**One line:** EC2 is a computer you rent by the hour; Lambda is a function AWS runs on demand and bills by the millisecond — use Lambda for the glue around a model, EC2 or a managed endpoint for the model itself.

---

### Q4: So Lambda is for stateless, quick tasks — correct? And where is the Lambda function written: in the application code, or inside AWS?

**✅ Correct on the first part, with one addition: the trigger matters as much as the speed.** Lambda suits work that's **event-triggered, stateless, and fast** (hard ceiling: 15 minutes). *Stateless* is the load-bearing word — each run starts fresh knowing nothing about the last one, so anything that must be remembered goes to a database, S3, or a cache.

**On where it's written: you write it as ordinary code in your own repo. AWS is only where it *runs*.**

```python
# handler.py — lives in YOUR repo, YOUR editor, YOUR git
def lambda_handler(event, context):
    file = event["Records"][0]["s3"]["object"]["key"]   # what triggered it
    text = extract_text(file)
    embed_and_store(text)
    return {"statusCode": 200, "body": "indexed"}
```

Then you **ship it to AWS** one of three ways:
1. **Zip upload** — zip the folder and upload it (console or CLI)
2. **Container image** — package as Docker and push to ECR (up to 10 GB, which is how bigger dependencies get in)
3. **Infrastructure-as-code** — Terraform, AWS SAM, CDK, or Serverless Framework, which is what real teams use

AWS's side of the deal is purely the **runtime**: it stores your function, watches for the trigger, and calls `lambda_handler` when it fires.

**The contract worth knowing:** AWS calls *one* named function, handing it two arguments — `event` (what happened: the S3 object, the HTTP body, the schedule tick) and `context` (runtime info such as time remaining). Writing that single entry point is your job.

> You *can* type code straight into the AWS console's inline editor, but that's for throwaway experiments — no version control, no dependencies, no tests. Nobody ships that way.

**Is it "inside the application code"?** Usually it's a **separate small codebase**, often its own folder in the same repo (`/lambdas/ingest-pdf/`) rather than woven into the main app — because it gets packaged and deployed as its own unit with its own dependencies.

**One line:** the Lambda function is ordinary code you write and version-control yourself; AWS just supplies the environment that runs it on demand — you're renting execution, not authorship.

---

### Q5: I'd use EC2 for the whole application, but write Lambda functions for specific jobs inside it — PDF parsing, photo resizing — each self-contained with its own dependencies. That reduces overall cost, correct?

**✅ The architecture is right and genuinely common. Two things need sharpening.**

**Sharpening 1 — "the Lambda functions would be in the application code."** They live in your **repo**, but they are *not* part of your running app. The EC2 app doesn't call them like a normal in-process function — it invokes them **over the network**, or an event (an S3 upload) triggers them directly. Separate deploy, separate dependencies, separate logs. *Same house, different rooms — not the same room.*

**Sharpening 2 — "this reduces cost" is conditional, not automatic.** It depends entirely on how often the task runs.

**When it genuinely saves money — bursty work:**
> A doc-Q&A app runs on a `t3.small` (~$15/mo). PDFs arrive maybe 200 times a month, each needing 30 seconds of heavy CPU. To absorb those bursts on EC2 alone you'd size up to a `t3.large` (~$60/mo) purely for occasional spikes. Offload to Lambda instead: keep the `t3.small` + roughly $1 of Lambda = **~$16/mo instead of ~$60**.

**When it doesn't — constant work:**
> Same app, but PDFs stream in all day, every day. Now Lambda fires nonstop and you're paying per-invocation **on top of** an EC2 box that's already running. Cheaper to size the EC2 correctly and do it in-process.

**The argument that's actually stronger than cost — spike absorption:**
> 100 PDFs land at once. On EC2 they queue, the box maxes out, and web requests start timing out because parsing is eating the CPU. With Lambda, 100 functions run in parallel and the EC2 doesn't notice. **Isolation** — a heavy background job can't degrade what users are looking at.

**The cost you're adding:** complexity — network hops, IAM permissions, a second deploy pipeline, harder local testing, and cold starts on the first call.

**One line:** EC2 runs the always-on application; bursty or CPU-heavy side jobs split out into Lambdas — separate deployables in the same repo, triggered by events — and it saves money when those jobs are infrequent, but the better reason is keeping a spike in background work from degrading the main app.

---

### Q6: So EC2 and Lambda work side by side, each expert at its own thing — like a Big Billion Day sale with heavy traffic. EC2 is one deployment, all the Lambdas another, triggered by events, with separate deployment cycles. Correct?

**Mostly right — the resume-parsing instinct is excellent. Two corrections.**

**✅ Right:** EC2 and Lambda as complementary specialists; **resume parsing is a textbook Lambda case** (200 resumes land at 9am, nothing at 3am); memory/CPU configured per function (128 MB → 10 GB, CPU scaling with memory); and **separate deployment cycles** — you can redeploy the PDF parser without touching the main app.

**❌ Correction 1 — Big Billion Day is the wrong example for Lambda.** Two different things got mixed: **infrequent** and **spiky-then-idle**. A big sale is neither — it's **sustained peak**, 10x traffic for five days straight.

| | Shape | Right tool |
|---|---|---|
| Resume uploads | Burst at 9am, idle overnight | **Lambda** |
| Big Billion Day storefront | 10x traffic, sustained for days | **EC2 auto-scaling** |

At sustained volume Lambda gets *expensive* — you're paying per invocation for millions of continuous requests. Cheaper to spin up 20 EC2 instances for five days and scale back down.

> Lambda still has a place during that sale, just not for the storefront: the *side jobs* fit perfectly — generating invoice PDFs, sending order-confirmation emails, resizing new product images. Event-triggered and bursty even while main traffic is steady.

**❌ Correction 2 — it's not "one deployment for all the Lambdas."** Each Lambda is typically **its own deployment unit** with its own package and dependencies. You can *group* them in one infrastructure-as-code stack (Terraform, AWS SAM) so they deploy together, but that's convenience — they remain independent functions you can update one at a time. Practically: `/lambdas/parse-resume/` and `/lambdas/send-email/` are two packages, not one bundle.

**One line:** EC2 runs the always-on application while bursty event-triggered side jobs become individual Lambdas, each its own deployable with its own memory config and release cycle — but sustained high traffic like a sale event belongs on auto-scaling EC2, not Lambda.

---

### Q7: EC2 is always up, but Lambda isn't — it sits in a kind of hibernated mode, needs a cold start when a request arrives, and the process is killed once execution finishes. Correct?

**✅ Correct, and "hibernated" is a good instinct — with one refinement.**

It isn't that *your* function is asleep and wakes up. **Nothing of yours exists at all** until a request arrives. AWS then builds an environment from scratch, loads your code into it, and runs it.

```
Request arrives
   │
   ├─ Is there a warm environment already running?
   │
   ├─ NO  → COLD START: AWS provisions a micro-container,
   │        loads your runtime (Python), imports your code
   │        and dependencies, THEN runs your function   ← the 1-3s delay
   │
   └─ YES → run immediately (~milliseconds)
```

**❌ The one correction — AWS does not kill it immediately after execution.** It keeps the environment **warm** for a while (roughly 5-15 minutes; AWS doesn't guarantee the number) in case another request arrives. Only after real idleness is it torn down.

> **Example — the resume parser.** First upload of the morning: 3 seconds (container built, Python loaded, PDF libraries imported). The next nine resumes that hour: ~400 ms each, because the environment is still warm and it just reruns your function. Come back after lunch: 3 seconds again.

So "hibernated" is close, but more precisely: **the environment is recycled, not your process resumed.** Every invocation starts with fresh memory — which is exactly why Lambda is stateless. A global variable set in one run *might* survive into the next if it lands on the same warm container, but you can never rely on it.

**Worth knowing for an interview:** you can pay for **provisioned concurrency** to keep N environments permanently warm and eliminate cold starts — but you're then paying for idle capacity, which is precisely what Lambda was supposed to save you from. That trade-off is a neat summary of the whole model.

**One line:** EC2 is always on; Lambda has nothing running until a trigger arrives, pays a 1-3 second cold start to build an environment, then keeps it warm for a few minutes of follow-up requests before discarding it — so state never survives reliably between runs.

---

### Q8: So a PDF-parsing Lambda carries all its own parsing dependencies inside its own package, because it's deployed and run independently?

**✅ Correct.** That Lambda ships with its own PDF-parsing dependencies bundled into its own package, because it's deployed and run independently in its own container with no access to whatever the EC2 app has installed.

**One line:** each Lambda is self-contained — its own code, its own dependencies, its own package — because nothing else is in the container with it.

---

### Q9: Does Lambda need an EC2 instance running? And is EC2 also serverless?

**❌ No on both counts.**

**Lambda is completely independent of EC2** — you can have Lambda functions with zero EC2 instances in your account. They appeared together above only because *that* architecture had a long-running app plus bursty side jobs; the pairing is a design choice, not a requirement.

> Plenty of real systems are 100% Lambda with no EC2 anywhere: a resume-parsing site could be S3 for the frontend, API Gateway for requests, Lambda for parsing, DynamoDB for storage — nothing running when nobody's using it. The reverse holds too: run everything on EC2 and never touch Lambda.

**And EC2 is the opposite of serverless** — it *is* the server. You pick its size, patch its OS, keep it running, and pay by the hour whether anyone uses it or not.

| | EC2 | Lambda |
|---|---|---|
| You manage the machine | Yes | No |
| Running when idle | Yes (and billing) | Nothing exists |
| Billing unit | Per hour | Per request + ms |

**The nuance worth knowing:** AWS *does* run Lambda on physical machines underneath (Firecracker micro-VMs) — but that's **Amazon's** infrastructure, never yours. You don't see, configure, or pay for it when idle. That's the whole meaning of "serverless": servers exist, they're just not your problem.

**One line:** Lambda needs no EC2, and EC2 is not serverless — serverless means the servers are Amazon's concern, not that no servers exist.

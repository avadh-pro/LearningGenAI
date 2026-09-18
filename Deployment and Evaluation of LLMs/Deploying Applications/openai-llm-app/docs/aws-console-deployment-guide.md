# Deploy a containerized LLM application to AWS

This guide explains the cloud, container, identity, and networking ideas behind each action and
then walks you through deploying this repository to Amazon ECS on AWS Fargate. Each section
combines a short **Concept and purpose** explanation, practical steps, and a **Checkpoint** so you
can connect what you configure with why it is needed.

There are no deployment scripts in this lab. We deliberately create the AWS resources in the
AWS Management Console so that every moving part is visible. We use a terminal only to build
and push the Docker image.

> **Warning:** AWS resources in this guide can incur charges, and OpenAI API calls can also incur
> charges.
> Complete the cleanup section when the lab is over. Never paste a real API key into this
> document, source code, a screenshot, or a screen recording.

## Guide map

- Start with [the two architecture flows](#what-you-will-finish-with) and the
  [service-purpose map](#aws-services-used-and-why).
- Understand [cloud, container, IAM, and networking foundations](#foundation-the-ideas-behind-this-deployment).
- Compare the [lab and production choices](#lab-architecture-versus-production-architecture).
- Complete [Steps 1–4](#1-open-the-aws-console-and-choose-a-region) to authenticate and publish
  the image.
- Complete [Steps 5–8](#5-store-the-openai-key-in-aws-secrets-manager) to configure secrets,
  permissions, logs, and the firewall.
- Complete [Steps 9–12](#9-confirm-the-ecs-service-linked-role-and-create-the-cluster) to define,
  run, and test the application.
- Use [Step 13](#13-deploy-a-code-update-manually) to demonstrate the deployment lifecycle.
- Finish with [layered troubleshooting](#troubleshooting-diagnose-by-layer),
  [cleanup](#cleanup-after-the-demo), and the [knowledge check](#knowledge-check).


## What you will finish with

The deployment has two distinct flows. Keeping them separate makes the architecture easier to
reason about.

### Build and deployment flow

```text
Dockerfile + application code
            |
            | docker build
            v
Local container image
            |
            | docker push (authenticated by AWS CLI)
            v
Amazon ECR private repository
            |
            | ECS task execution role permits image pull
            v
Amazon ECS service -> AWS Fargate starts one task
```

### Runtime request flow

```text
Your browser
       |
       | HTTP, TCP port 8501
       | allowed only from your public IP
       v
Public IP on the Fargate task's network interface
       |
       v
Streamlit container :8501
       |
       | HTTP over localhost:8000
       v
FastAPI container :8000
       |
       | HTTPS, TCP port 443 (outbound)
       v
OpenAI API

Secrets Manager --injects OPENAI_API_KEY at startup--> FastAPI container
Both containers --send stdout/stderr--> CloudWatch Logs
```

Both containers run in **one ECS task**. On Fargate, containers in the same task share the
task's network interface and can communicate through `localhost`. That is why the browser needs
access to port `8501`, while port `8000` remains closed to the internet.

## AWS services used and why

| Service or tool | What it provides | Why this lab uses it |
|---|---|---|
| AWS Management Console | Web interface to AWS APIs | Makes every resource and relationship visible while completing the lab |
| AWS CLI | Terminal interface to AWS APIs | Authenticates Docker to ECR and confirms which AWS identity is active |
| AWS STS | Temporary security credentials and identity information | `get-caller-identity` proves which account and identity the CLI is using |
| Docker | Image build format and container runtime | Packages the code and dependencies into a repeatable artifact |
| Amazon ECR | Private, managed container image registry | Stores the image where ECS can retrieve it |
| AWS Secrets Manager | Encrypted secret storage with IAM-controlled access | Keeps `OPENAI_API_KEY` outside code and the image |
| AWS IAM | Authentication and authorization | Grants ECS only the permissions it needs to pull, log, and retrieve the secret |
| Amazon CloudWatch Logs | Central log storage and search | Preserves container output after a task stops or is replaced |
| Amazon VPC | Isolated virtual network | Supplies subnets, routes, IP addressing, and network boundaries for the task |
| Security group | Stateful virtual firewall | Allows the demo UI from your IP while leaving the API port private |
| Amazon ECS | Container orchestrator | Turns the container configuration into running, replaceable tasks |
| AWS Fargate | Serverless compute engine for containers | Runs the task without provisioning or patching EC2 instances |

## Foundation: the ideas behind this deployment

### Cloud computing and managed services

Cloud computing means consuming compute, storage, networking, and higher-level services on
demand through APIs. Instead of buying a server first, we describe the resources an application
needs and AWS provisions them in minutes.

There is still a server somewhere. **Serverless** means the cloud provider manages the server
fleet, capacity placement, and host maintenance for you. With Fargate, we choose task CPU,
memory, image, and networking; AWS manages the underlying machines. We still own the
application code, configuration, identity permissions, data, and network exposure. This is an
example of the cloud **shared responsibility model**.

This lab combines several service levels:

- Docker provides a portable application package.
- ECS provides orchestration: placement, lifecycle, replacement, and deployment.
- Fargate provides managed compute on which ECS runs the containers.
- ECR, Secrets Manager, and CloudWatch provide managed supporting capabilities.

The important design lesson is that a cloud application is rarely “on one service.” It is a
small system whose services each have a focused responsibility.

### Regions and Availability Zones

An **AWS Region** is a separate geographic area identified by a code such as `ap-south-1`.
Most resources in this lab-including ECR repositories, ECS clusters, tasks, secrets, and log
groups-are regional. A resource created in another Region will appear to be missing when the
console is set to Mumbai.

Each Region contains multiple isolated **Availability Zones (AZs)** connected by high-speed,
low-latency links. A subnet belongs to exactly one AZ. Production systems commonly run multiple
tasks across multiple AZs so that the application can survive a task or AZ failure. This lab
uses one task to control cost, so it demonstrates deployment but does not provide high
availability.

We use Mumbai to keep every regional resource in one place and reduce latency for users located
near that Region. In a real project, Region selection also considers service availability, data
residency, compliance, resilience, and cost.

### Containers: image versus container

A **container image** is an immutable package of application code, runtime, libraries, and
default startup instructions. A **container** is a running instance of that image. The same image
can create many containers.

In this repository, the `Dockerfile` creates one image containing both FastAPI and Streamlit.
The image's default command starts FastAPI. The frontend container uses the same image but
overrides that default command to start Streamlit. Reusing the image keeps the lab simple;
larger systems often build a separate, smaller image for each independently deployed service.

Images are built in layers and identified in a registry by a repository plus a tag, for example:

```text
123456789012.dkr.ecr.ap-south-1.amazonaws.com/openai-llm-app:latest
| account |       registry + Region       | repository | tag |
```

A tag such as `latest` is a movable label. An image **digest** such as `sha256:...` identifies
exact image content. The movable tag is convenient for this demo, while unique version tags or
digests are safer for production because they make deployments reproducible and rollbacks clear.

### The ECS mental model

These names sound similar but represent different layers:

| ECS term | Mental model | In this lab |
|---|---|---|
| Cluster | Logical home for workloads | `openai-llm-cluster` |
| Task definition | Versioned blueprint describing containers, resources, roles, ports, and logs | Family `openai-llm-app`, revision `1` |
| Task | One running copy of a task definition | One FastAPI container plus one Streamlit container |
| Service | Controller that maintains the desired number of tasks and deploys replacements | `openai-llm-service`, desired count `1` |
| Fargate | Compute engine used to run each task | `.5 vCPU` and `1 GB` memory |

The task definition is comparable to a class or recipe; a task is an instance made from it. A
service continuously compares **desired state** with **actual state**. If desired count is `1`
and the task stops, ECS starts a replacement. This control loop is a central cloud and
orchestration concept.

### IAM: who can do what to which resource

AWS Identity and Access Management (IAM) answers three questions:

1. **Who** is making the request? An IAM user, federated identity, role, or AWS service.
2. **What** action is requested? For example, `secretsmanager:GetSecretValue`.
3. **Which** resource is targeted? Usually identified by an Amazon Resource Name (ARN).

An ARN is AWS's globally unambiguous resource identifier. It normally includes a service,
Region, account ID, and resource name. We use the secret ARN in a policy so the role can read
that one secret rather than every secret in the account. This is **least privilege**: grant only
the actions and resources needed for the task.

Three ECS-related roles appear in this lab:

| Role | Used by | Purpose |
|---|---|---|
| Your signed-in identity | You in the console and CLI | Creates and manages the lab resources |
| Task execution role | ECS/Fargate agent during task startup | Pulls the ECR image, retrieves the secret, and sends logs |
| ECS service-linked role | The ECS service itself | Lets ECS manage AWS resources such as task network interfaces |

The task definition also has a **task role** field. A task role gives application code inside a
container permission to call AWS APIs. This application calls the OpenAI API, not an AWS API,
so no task role is needed. The execution role's credentials are not intended for application
code inside the container.

An IAM role contains two complementary ideas:

- a **trust policy** says who is allowed to assume the role;
- a **permissions policy** says what the role may do after it is assumed.

A managed policy is maintained as a reusable policy object. An inline policy belongs directly
to one identity. This lab attaches AWS's managed execution policy and adds a narrow inline policy
for the one secret.

### Networking: follow the packet

A **VPC (Virtual Private Cloud)** is an isolated virtual network in one Region. Its IP address
range is written in **CIDR** notation, such as `172.31.0.0/16`. A **subnet** is a smaller range
inside the VPC and belongs to one Availability Zone.

A subnet is called **public** when its route table has a route to an **internet gateway**. A
route table answers “where should a packet with this destination go?” For IPv4 internet access,
the resource also needs a public IPv4 address. A public IP without the route-or a route without a
public IP-is insufficient.

With Fargate's required `awsvpc` network mode, each task receives an **Elastic Network Interface
(ENI)** and a private IP in the selected subnet. In this lab, assigning a public IP to that ENI
allows two things:

- inbound browser traffic can reach Streamlit; and
- outbound traffic can reach ECR, Secrets Manager, CloudWatch, and the OpenAI API through the
  internet gateway.

A **port** identifies a process-level endpoint at an IP address. TCP provides reliable,
connection-oriented delivery. HTTP is an application protocol carried here over TCP:

- Streamlit listens on TCP `8501`.
- FastAPI listens on TCP `8000`.
- HTTPS requests to service APIs use TCP `443` outbound.

A **security group** is a stateful allow-list firewall attached to the task's ENI. “Stateful”
means response traffic for an allowed connection is automatically permitted. Security groups
have no explicit deny rules: traffic is blocked unless an allow rule matches. “My IP” creates a
`/32` rule for one public IPv4 address, which is safer for this lab than `0.0.0.0/0`
(the entire IPv4 internet).

Port `8000` needs no inbound rule because both containers are in the same task and the frontend
uses `http://localhost:8000`. Declaring a container port documents what the container listens on;
it does not by itself grant internet access. The subnet route, public IP, and security-group rule
must all agree before an external connection succeeds.

## Lab architecture versus production architecture

This deployment intentionally favors visibility and low setup time. Do not copy every choice
unchanged into a production system.

| Lab choice | Why it is useful here | Typical production direction |
|---|---|---|
| Default VPC and public subnet | Avoids building a network before learning ECS | Dedicated VPC; tasks in private subnets |
| Public task IP and HTTP on `8501` | Direct and easy to inspect | Application Load Balancer, HTTPS certificate, stable DNS; no public task IP |
| Source restricted to “My IP” | Limits access during a live demo | Authenticated application plus carefully designed ingress, WAF where appropriate |
| One task | Controls cost and makes the lifecycle visible | At least two tasks across multiple AZs for availability |
| `latest` image tag | Makes manual updates short | Unique version tag or image digest, automated CI/CD, tested rollback |
| Manual console creation | Makes each resource visible | Infrastructure as code with reviewable, repeatable changes |
| Rotation disabled | Avoids requiring an external API-key rotation workflow | Documented rotation and redeployment procedure |
| One image for API and UI | Simple build and registry workflow | Separate images if components release or scale independently |

## Values used throughout the guide

Use these names so every step and troubleshooting instruction matches:

| Resource | Value |
|---|---|
| AWS Region | `ap-south-1` (Asia Pacific, Mumbai) |
| ECR repository | `openai-llm-app` |
| Secret | `openai-llm-app/openai-api-key` |
| Task execution role | `openaiLlmEcsTaskExecutionRole` |
| CloudWatch log group | `/ecs/openai-llm-app` |
| Security group | `openai-llm-demo` |
| ECS cluster | `openai-llm-cluster` |
| Task-definition family | `openai-llm-app` |
| ECS service | `openai-llm-service` |

Keep a temporary worksheet during the lab. These values are safe to record, but never record the
secret value itself:

```text
AWS account ID:       ______________________________________________
ECR repository URI:   ______________________________________________
Secret ARN:           ______________________________________________
Execution role ARN:   ______________________________________________
Running task public IP: ____________________________________________
```

## Prerequisites

You need:

- access to an AWS account through an IAM or federated identity;
- permission to create the resources in this guide and pass the execution role to ECS;
- an OpenAI API key with suitable project access and budget;
- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html);
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running locally; and
- PowerShell opened in this repository's root directory.

AWS occasionally changes console labels and page layouts. Follow the resource name and purpose
when a button has moved; the underlying concepts and configuration fields remain the guideposts.

## 1. Open the AWS Console and choose a Region

### Concept and purpose

The console is a graphical client for AWS service APIs. The Region selector controls which
regional resources the console displays and where new regional resources are created. IAM is
largely global, but the application's ECR, ECS, Secrets Manager, CloudWatch, and VPC resources
must be created in the same Region for this lab.

### Perform the steps

1. Open [https://console.aws.amazon.com/](https://console.aws.amazon.com/).
2. Choose **Sign in to the Console**.
3. Sign in with the IAM user or federated identity provided for the lab.
4. In the upper-right corner, open the Region selector.
5. Select **Asia Pacific (Mumbai) `ap-south-1`**.
6. Keep the console in `ap-south-1` while creating every regional resource in this guide.

**Checkpoint:** the upper-right Region selector shows **Mumbai**.

> **Key takeaway:** A correct resource name in the wrong Region is still the wrong
> resource. Region is one of the first things to check when an AWS resource appears to be
> missing.

## 2. Connect your terminal to the same AWS account

### Concept and purpose

The console and CLI are two clients for the same AWS APIs, but they can be authenticated as
different identities or point at different Regions. `aws sts get-caller-identity` returns the
current principal's account ID and ARN, making the active CLI context explicit before we create
or push anything.

AWS credentials prove identity; IAM policies determine authorization. An authentication success
does not imply permission to perform every action. Prefer temporary credentials to long-lived
access keys.

### Perform the steps

Verify the required local tools:

```powershell
aws --version
docker --version
docker info
```

For AWS CLI `2.32.0` or newer, browser-based login can create and refresh temporary local
credentials. Your AWS administrator must allow this sign-in method:

```powershell
aws login --region ap-south-1
```

If your organization uses IAM Identity Center, use its configured profile instead:

```powershell
aws sso login --profile YOUR_PROFILE_NAME
```

If you were explicitly supplied access-key credentials, configure the intended profile:

```powershell
aws configure
```

Enter the supplied credentials, `ap-south-1` for the default Region, and `json` for output.
Never configure a root-user access key. Do not paste an access key or secret key into this guide.

Verify the active identity:

```powershell
aws sts get-caller-identity
```

The output contains:

- `Account`: the 12-digit AWS account ID;
- `Arn`: the IAM user or assumed role currently active; and
- `UserId`: an internal unique identifier for that principal/session.

Write the `Account` value in the worksheet. If you used a named profile, append
`--profile YOUR_PROFILE_NAME` to subsequent AWS CLI commands or set that profile for the shell.

**Checkpoint:** `aws sts get-caller-identity` returns the expected account ID and identity ARN
without an error.

## 3. Create the Amazon ECR repository

### Concept and purpose

Amazon Elastic Container Registry (ECR) is managed storage for container images. A **registry**
belongs to an AWS account in a Region; a **repository** groups versions of one application image.
ECS needs a durable image location that it can authenticate to and pull from whenever it starts
or replaces a task.

ECR stores images but does not build the application in this workflow. Enabling image scanning
helps detect known operating-system and language-package vulnerabilities. A clean scan is useful
evidence, but it is not a guarantee that the application is secure.

### Perform the steps

1. In the AWS Console search bar, enter `ECR`.
2. Open **Elastic Container Registry**.
3. In the left navigation, choose **Private registry > Repositories**.
4. Choose **Create repository**.
5. For **Repository name**, enter `openai-llm-app`.
6. Enable **Scan on push** if that option is available.
7. Keep the remaining settings at their defaults.
8. Choose **Create repository**.
9. Open the new repository and copy its repository URI into the worksheet.

The URI has this shape:

```text
123456789012.dkr.ecr.ap-south-1.amazonaws.com/openai-llm-app
```

It contains the AWS account ID, ECR registry domain, Region, and repository name. A tag will be
appended after a colon when we push the image.

**Checkpoint:** the ECR console lists an empty private repository named `openai-llm-app` in
`ap-south-1`.

## 4. Build, authenticate, and push the first image

### Concept and purpose

`docker build` reads the repository's `Dockerfile`, executes its instructions, and produces a
local image. Tagging gives that image the remote ECR name. `docker push` uploads any image layers
that the repository does not already contain.

ECR is private. `aws ecr get-login-password` obtains a short-lived authorization token using the
current AWS identity; piping it to `docker login --password-stdin` lets Docker authenticate
without placing the token directly in the command line. The identity still needs ECR push
permissions.

### Perform the steps

From the repository root, run:

```powershell
$AwsRegion = "ap-south-1"
$AwsAccountId = aws sts get-caller-identity --query Account --output text
$EcrRegistry = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$ImageUri = "$EcrRegistry/openai-llm-app:latest"

aws ecr get-login-password --region $AwsRegion |
    docker login --username AWS --password-stdin $EcrRegistry

docker build --platform linux/amd64 --tag $ImageUri .
docker push $ImageUri
```

What each important part means:

- `--query Account --output text` extracts only the account ID from the STS response.
- `:latest` is the image tag used by this lab.
- `--platform linux/amd64` matches the `Linux/X86_64` architecture selected in the ECS task
  definition, including when the image is built on an ARM-based laptop.
- the final `.` in `docker build` is the build context-the files Docker may read during build.
- `docker push` transfers the local tagged image to the ECR repository.

Return to the ECR repository and refresh the page. If scanning is enabled, the scan result may
take a short time to appear.

**Checkpoint:** an image tagged `latest` appears in ECR, with a digest and push timestamp.

> **Key takeaway:** ECR is the artifact store, not the running environment. At this point
> the application is stored in AWS but no AWS compute is running it yet.

## 5. Store the OpenAI key in AWS Secrets Manager

### Concept and purpose

A secret is sensitive configuration such as an API key, password, or token. Putting it into a
Docker image, Git repository, normal task-definition environment value, or shared document
would make it hard to control and rotate.

Secrets Manager encrypts secret values at rest using AWS KMS and controls retrieval through IAM.
We store only the key value because ECS will inject the full secret into the environment variable
named `OPENAI_API_KEY`. The secret name and ARN are identifiers, not secret values, and can be
used in configuration and IAM policies.

### Perform the steps

1. Search the AWS Console for **Secrets Manager** and open it.
2. Choose **Store a new secret**.
3. For **Secret type**, choose **Other type of secret**.
4. Select the **Plaintext** view.
5. Paste only the OpenAI API key, for example `sk-...`.
6. Do not store a JSON object and do not include `OPENAI_API_KEY=`.
7. Keep the default AWS-managed encryption key.
8. Choose **Next**.
9. For **Secret name**, enter `openai-llm-app/openai-api-key`.
10. Choose **Next**.
11. Leave automatic rotation disabled for this lab.
12. Finish creating the secret.
13. Open the secret and copy its **Secret ARN** into the worksheet. Do not reveal or record the
    secret value.

**Checkpoint:** Secrets Manager lists `openai-llm-app/openai-api-key` in `ap-south-1`.

> [!NOTE]
> ECS reads and injects the secret when a container starts. If you change or rotate the secret,
> an already-running container does not receive the new value automatically. Start a new ECS
> deployment after changing this key.

## 6. Create the ECS task execution role

### Concept and purpose

The Fargate agent must perform startup operations on our behalf: authenticate to ECR, pull the
private image, retrieve the referenced secret, and send container logs. The **task execution
role** authorizes these platform operations.

`AmazonECSTaskExecutionRolePolicy` supplies the common ECR pull and CloudWatch Logs permissions.
It does not grant access to our particular secret, so we add `secretsmanager:GetSecretValue` for
exactly one secret ARN. This demonstrates least privilege and the difference between a broad
service capability and access to application-specific data.

### Perform the steps

1. Search for **IAM** and open it.
2. In the left navigation, choose **Roles**.
3. Choose **Create role**.
4. For **Trusted entity type**, choose **AWS service**.
5. For the service/use case, choose **Elastic Container Service Task**.
6. Choose **Next**.
7. Search for and select `AmazonECSTaskExecutionRolePolicy`.
8. Choose **Next**.
9. For **Role name**, enter `openaiLlmEcsTaskExecutionRole`.
10. Choose **Create role**.
11. Open the newly created role.
12. Choose **Add permissions > Create inline policy**.
13. Select the **JSON** editor and paste the following policy.
14. Replace `PASTE_SECRET_ARN` with the Secret ARN copied in Step 5. Keep the quotation marks.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "PASTE_SECRET_ARN"
    }
  ]
}
```

15. Choose **Next**.
16. Name the policy `ReadOpenAIKey`.
17. Create the policy.
18. On the role summary page, copy the role ARN into the worksheet.

The policy's `Version` identifies the IAM policy-language version; it is not a date on which this
lab policy expires. The default is implicit deny, and this statement adds one explicit allow.

**Checkpoint:** the role trusts ECS tasks and has both of these permissions policies:

- `AmazonECSTaskExecutionRolePolicy` (AWS managed); and
- `ReadOpenAIKey` (inline, limited to one secret ARN).

## 7. Create the CloudWatch log group

### Concept and purpose

Containers are disposable. A task can stop and its local filesystem can disappear, so useful
logs must be shipped outside the task. The `awslogs` log driver sends the containers' standard
output and standard error to CloudWatch Logs.

A **log event** is one timestamped record. A **log stream** is a sequence from one source, such
as one container in one task. A **log group** collects streams that share retention, access, and
monitoring settings. The `api` and `frontend` stream prefixes will make their output easy to tell
apart.

Retention is both a cost and governance decision. CloudWatch otherwise retains many log groups
indefinitely, so this short-lived lab uses one week.

### Perform the steps

1. Search for **CloudWatch** and open it.
2. Choose **Logs > Log groups** (in some console layouts, **Log Management**).
3. Choose **Create log group**.
4. Enter `/ecs/openai-llm-app`.
5. Choose **Create**.
6. Open the log group.
7. Choose **Actions > Edit retention setting**, or select the value in the **Retention** column.
8. Select **1 week** and save.

**Checkpoint:** `/ecs/openai-llm-app` appears in CloudWatch Logs with seven-day retention.

> **Operational rule:** Never log API keys, access tokens, passwords, or complete sensitive
> user input. Centralizing logs makes troubleshooting easier, but it also centralizes whatever
> the application writes.

## 8. Create the security group

### Concept and purpose

This is the main network-access decision in the lab. The default VPC already supplies an IP
range, subnets, route tables, and an internet gateway. The security group supplies the task-level
firewall policy.

The one inbound rule can be read as a sentence: “Allow TCP connections to the task's port `8501`
when the source is my current public IPv4 address.” The default outbound rule lets the task make
requests to AWS services and the OpenAI API. Because the firewall is stateful, reply packets do
not require a separate inbound rule.

### Perform the steps

1. Search for **EC2** and open it. Security groups are visible in the EC2 console even though we
   are not creating an EC2 instance.
2. In the left navigation, choose **Network & Security > Security Groups**.
3. Choose **Create security group**.
4. For **Security group name**, enter `openai-llm-demo`.
5. Enter a description such as `Streamlit demo from my IP`.
6. For **VPC**, choose the default VPC.
7. Under **Inbound rules**, choose **Add rule**.
8. Configure the rule:

   | Field | Value |
   |---|---|
   | Type | Custom TCP |
   | Port range | `8501` |
   | Source | My IP |

9. Keep the default outbound rule.
10. Choose **Create security group**.

Do not add an inbound rule for port `8000`. Streamlit calls FastAPI through
`http://localhost:8000` inside the same Fargate task.

**Checkpoint:** `openai-llm-demo` belongs to the default VPC and allows inbound TCP `8501` only
from your current public IP.

> [!NOTE]
> Your public IP can change when you change networks, reconnect a router, enable a VPN, or use a
> corporate proxy. If the UI worked earlier and later times out, refresh the “My IP” source in
> this rule. Do not solve the problem by permanently opening `8501` to `0.0.0.0/0`.

## 9. Confirm the ECS service-linked role and create the cluster

### Concept and purpose

An ECS **cluster** is a Region-specific logical grouping of tasks and services. With Fargate, it
does not represent a fleet of EC2 machines that we must provision. We choose Fargate as the
compute engine later, and AWS supplies the underlying capacity.

Before ECS can manage resources such as task network interfaces, it needs its AWS-managed
**service-linked role**, `AWSServiceRoleForECS`. This account-level role is linked to the ECS
service and has an AWS-defined trust relationship and permissions. It is different from our task
execution role:

- service-linked role: ECS manages AWS infrastructure for the service;
- task execution role: the ECS/Fargate agent prepares and operates this application's task.

Do not create a normal custom role with the service-linked role's reserved name.

### Confirm or create the service-linked role

1. Open **IAM > Roles**.
2. Search for `AWSServiceRoleForECS`.
3. If the role exists, open it and confirm:

   - its ARN contains `/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS`;
   - it has the AWS-managed policy `AmazonECSServiceRolePolicy`; and
   - its trusted service is `ecs.amazonaws.com`.

4. If it does not exist, choose **Create role**.
5. Choose **AWS service**.
6. Select **Elastic Container Service** and the `AWSServiceRoleForECS` service-linked-role use
   case. AWS supplies the role name and permissions.
7. Create the role, wait about 30 seconds, and return to Amazon ECS.

If that use case is not shown in your IAM console, create the same AWS-managed role from the
connected terminal:

```powershell
aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
```

If this returns `AccessDenied`, your identity needs `iam:CreateServiceLinkedRole`. Ask the
AWS administrator to create the role or grant that permission.

### Create the cluster

8. Search for **ECS** and open **Amazon Elastic Container Service**.
9. Choose **Clusters**.
10. Choose **Create cluster**.
11. For **Cluster name**, enter `openai-llm-cluster`.
12. Choose or keep **AWS Fargate (serverless)** as the infrastructure option.
13. Keep the remaining defaults.
14. Choose **Create**.

**Checkpoint:** the cluster status is `ACTIVE`. No EC2 container instances are required.

## 10. Create the ECS task definition

### Concept and purpose

A task definition is an immutable, versioned blueprint. It declares which images to run, startup
commands, CPU and memory, environment configuration, secrets, ports, logging, health checks, and
IAM roles. Editing it creates a new revision rather than mutating a running task.

Fargate requires `awsvpc` networking. The `.5 vCPU` and `1 GB` values are a valid Fargate task
size and apply to the task as a whole. Both containers share that task-level capacity, network
interface, lifecycle, and localhost namespace.

An **essential container** is part of the task's required workload. If an essential container
stops, ECS stops the task, and the service can replace it. This is appropriate here because the UI
is not useful without the API and vice versa.

### Configure the task-level settings

1. In Amazon ECS, choose **Task definitions**.
2. Choose **Create new task definition**.
3. Use the form, not the JSON editor.
4. Configure the task:

   | Field | Value | Why |
   |---|---|---|
   | Task definition family | `openai-llm-app` | Groups revisions of this blueprint |
   | Launch type | AWS Fargate | Uses managed, serverless container compute |
   | Operating system/architecture | Linux/X86_64 | Matches the image built from `python:3.12-slim` on common lab machines |
   | Network mode | `awsvpc` | Gives the Fargate task an ENI and VPC IP address |
   | CPU | `.5 vCPU` | Shared task compute allocation |
   | Memory | `1 GB` | Shared task memory limit |
   | Task role | None | Application code does not call AWS APIs |
   | Task execution role | `openaiLlmEcsTaskExecutionRole` | Lets the agent pull, retrieve the secret, and log |

### Add the FastAPI container

The Dockerfile's default `CMD` starts Uvicorn, which serves the FastAPI application on `8000`.
No command override is needed for this container.

5. Under **Container details**, configure the first container:

   | Field | Value |
   |---|---|
   | Name | `api` |
   | Image URI | Your ECR URI ending in `:latest` |
   | Essential container | Yes |
   | Container port | `8000` |
   | Protocol | TCP |
   | App protocol | HTTP |

6. Under **Environment variables**, add these non-secret values:

   | Key | Value | Purpose |
   |---|---|---|
   | `APP_ENV` | `production` | Labels the runtime environment in health output/log context |
   | `LOG_LEVEL` | `INFO` | Selects useful operational logging without debug verbosity |
   | `OPENAI_MODEL` | `gpt-4.1-mini` | Selects the model used by the application |

Normal environment variables are visible in the task definition, so they are suitable for
configuration but not credentials.

7. Add one secret environment variable:

   | Key | Value type | ValueFrom |
   |---|---|---|
   | `OPENAI_API_KEY` | ValueFrom | Secret ARN copied in Step 5 |

Use the ARN, not the actual OpenAI key. At task startup, ECS retrieves the secret value using the
execution role and injects it under the variable name expected by the application.

8. If the console shows **Health check**, configure:

   | Field | Value |
   |---|---|
   | Command | `CMD-SHELL,python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` |
   | Interval | `30` seconds |
   | Timeout | `5` seconds |
   | Retries | `3` |
   | Start period | `20` seconds |

The command runs inside the container. It uses Python's standard library because this project's
slim image does not install `curl`. A successful HTTP response exits with code `0`; a connection
or HTTP error makes the check fail.

9. Enable **Use log collection**.
10. Set the log driver to `awslogs` and configure:

   | Option | Value |
   |---|---|
   | `awslogs-group` | `/ecs/openai-llm-app` |
   | `awslogs-region` | `ap-south-1` |
   | `awslogs-stream-prefix` | `api` |

### Add the Streamlit container

The same image defaults to FastAPI, so this second container must override the Docker image's
startup command. This demonstrates the distinction between an image and its runtime
configuration.

11. Choose **Add more containers**.
12. Configure the second container:

    | Field | Value |
    |---|---|
    | Name | `frontend` |
    | Image URI | The same ECR URI ending in `:latest` |
    | Essential container | Yes |
    | Container port | `8501` |
    | Protocol | TCP |
    | App protocol | HTTP |

13. In the **Command** field under Docker configuration, enter this comma-separated value:

```text
streamlit,run,frontend/streamlit_app.py,--server.address=0.0.0.0,--server.port=8501,--server.headless=true
```

`0.0.0.0` means “listen on all interfaces inside the task,” which is required for traffic sent
to the task ENI to reach Streamlit. `localhost` as a listening address would accept only local
connections.

14. Configure the frontend health check:

    | Field | Value |
    |---|---|
    | Command | `CMD-SHELL,python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"` |
    | Interval | `30` seconds |
    | Timeout | `5` seconds |
    | Retries | `3` |
    | Start period | `30` seconds |

A container health check runs from inside the container. It is different from a load-balancer
health check, which would test the service across the network. Health checks answer “is the
process responding?”, while logs help answer “why is it not responding?”

15. Add this normal environment variable:

    | Key | Value | Purpose |
    |---|---|---|
    | `API_BASE_URL` | `http://localhost:8000` | Sends UI API calls to FastAPI in the same task |

16. Enable log collection and configure:

    | Option | Value |
    |---|---|
    | `awslogs-group` | `/ecs/openai-llm-app` |
    | `awslogs-region` | `ap-south-1` |
    | `awslogs-stream-prefix` | `frontend` |

17. Keep storage and other advanced settings at their defaults.
18. Choose **Create**.

**Checkpoint:** the task-definition family `openai-llm-app` has revision `1`, and its container
definitions list both `api` and `frontend`.

> **Key takeaway:** We have now described runnable compute but have not requested a running
> copy. Registering a task definition alone does not run or bill for Fargate compute.

## 11. Create the Fargate service

### Concept and purpose

Running a standalone task is useful for one-off work. An ECS **service** is appropriate for a web
application because it continuously maintains a desired number of tasks. If the task exits or is
reported unhealthy, the scheduler launches a replacement from the service's task definition.

The **Replica** strategy means “maintain this count.” A **rolling update** gradually replaces old
tasks with new tasks. With desired count `1` and no load balancer, this lab may have a short
interruption during replacement.

This is also where the abstract task definition is connected to a real VPC, subnets, security
group, and public-IP choice. The task definition says `awsvpc`; the service says which network.

### Perform the steps

1. Open **ECS > Clusters > openai-llm-cluster**.
2. Open the **Services** tab.
3. Choose **Create**.
4. Configure the service:

   | Field | Value |
   |---|---|
   | Compute option | Launch type |
   | Launch type | FARGATE |
   | Platform version | LATEST |
   | Task definition family | `openai-llm-app` |
   | Revision | Latest |
   | Service name | `openai-llm-service` |
   | Service type | Replica |
   | Desired tasks | `1` |
   | Deployment type/controller | Rolling update / ECS |

5. Expand **Networking**.
6. For **VPC**, select the same default VPC used by `openai-llm-demo`.
7. Select one or more default/public subnets. Selecting subnets in multiple AZs gives the
   scheduler placement options, although one running task is still not highly available.
8. For **Security group**, select the existing `openai-llm-demo` group. Remove the default
   security group if the console selected it as well.
9. Turn **Public IP** on.
10. Leave Service Connect off.
11. Leave service discovery off.
12. Leave VPC Lattice off.
13. Leave load balancing off.
14. Leave service auto scaling off.
15. Choose **Create**.
16. Open the service and wait until **Desired tasks = 1** and **Running tasks = 1**.

Why the optional features are off:

- **Service Connect/service discovery** help separate ECS services find and communicate with
  one another. Both processes here are in one task and already use `localhost`.
- **VPC Lattice** provides application networking across services and VPCs; this single demo
  service does not need that layer.
- A **load balancer** provides a stable endpoint, health-based routing, TLS termination, and
  distribution across tasks. It is the usual production direction but adds setup and cost.
- **Service auto scaling** changes desired count from metrics. One fixed task is enough for this
  controlled lab.

**Checkpoint:** the service reaches a steady state with one running Fargate task. Open the task
and confirm that both containers show `RUNNING` and become `HEALTHY`.

## 12. Open and test the deployed application

### Concept and purpose

The task's public IPv4 address is the internet-routable side of its ENI. The URL combines a
protocol (`http`), host (the public IP), and destination port (`8501`). The browser's source IP,
subnet route, public IP, security-group rule, listening process, and healthy task must all align.

The address belongs to the current task, not to the ECS service as a permanent endpoint. It can
change whenever ECS replaces the task. A production load balancer and DNS name would give clients
a stable endpoint.

### Perform the steps

1. In `openai-llm-service`, open the **Tasks** tab.
2. Select the running task.
3. Find **Networking** and copy the **Public IP** into the worksheet.
4. Open this address in your browser:

```text
http://PUBLIC_IP:8501
```

5. Submit a customer message, for example:

```text
My order was due yesterday, but it has not arrived.
```

6. Confirm the application returns a category, intent, priority, and suggested reply.
7. Open **CloudWatch > Logs > Log groups > `/ecs/openai-llm-app`** and inspect the `api` and
   `frontend` streams. Relate the browser action to the resulting request log.

**Checkpoint:** the browser receives a generated result, the task remains healthy, and both
containers have CloudWatch log streams.

### Trace one successful request

1. The browser opens a TCP connection to `PUBLIC_IP:8501`.
2. The public subnet route and internet gateway deliver it to the task ENI.
3. The security group allows it because the source IP and destination port match.
4. Streamlit accepts the HTTP request and renders the UI.
5. When the form is submitted, Streamlit posts to `http://localhost:8000/generate`.
6. FastAPI validates the request and calls the OpenAI API over outbound HTTPS.
7. The response returns along the same path, and both applications write operational logs.

## 13. Deploy a code update manually

### Concept and purpose

Pushing new bytes to the movable `latest` tag does not modify an already-running container. A
container continues to run the image content it started with. **Force new deployment** tells the
ECS service to replace its task even though the service configuration and task-definition
revision did not change. The replacement pulls the current image associated with the tag.

This is useful for a short demo but weakens traceability: two deployments can show the same tag
while containing different code. In production, tag images with a unique version or commit ID,
register a new task-definition revision, and deploy that revision through CI/CD.

### Build and push the changed image

After changing code, run from the repository root:

```powershell
$AwsRegion = "ap-south-1"
$AwsAccountId = aws sts get-caller-identity --query Account --output text
$EcrRegistry = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$ImageUri = "$EcrRegistry/openai-llm-app:latest"

aws ecr get-login-password --region $AwsRegion |
    docker login --username AWS --password-stdin $EcrRegistry

docker build --platform linux/amd64 --tag $ImageUri .
docker push $ImageUri
```

### Replace the running task

1. Open **ECS > Clusters > openai-llm-cluster**.
2. On the **Services** tab, select `openai-llm-service`.
3. Choose **Update**.
4. Enable **Force new deployment**.
5. Keep the current task-definition revision and other settings unchanged.
6. Choose **Update**.
7. Watch **Deployments**, **Tasks**, and **Service events** until the service again has one healthy
   running task and the deployment reaches a successful state.
8. Open the new task, copy its new public IP, and visit `http://PUBLIC_IP:8501`.

**Checkpoint:** ECR shows a newer push time/digest for `latest`, the old task is stopped, and the
replacement task runs the updated application.

> [!NOTE]
> Updating the Secrets Manager value follows the same lifecycle rule: force a new deployment so
> the replacement task retrieves and injects the current secret during startup.

## Troubleshooting: diagnose by layer

Randomly changing settings makes cloud failures harder to understand. Start at the control plane
and move toward the user-facing request path:

```text
Identity -> Artifact -> Task startup -> Process health -> Network path -> Application dependency
   IAM        ECR       roles/secret       logs           VPC/SG/IP       OpenAI API
```

### 1. Identity and authorization

**Symptom:** the console or terminal reports `AccessDenied`.

1. Run `aws sts get-caller-identity` and verify the account and ARN.
2. Confirm that the CLI and console use the intended identity.
3. Read the denied action and resource in the error.
4. Use the provided deployment identity or ask the administrator for that specific permission.

Authentication answers “who are you?” `AccessDenied` usually means that the authenticated
identity is not authorized for the requested action.

### 2. Local Docker and image build

**Symptom:** Docker cannot connect.

- Start Docker Desktop and wait until `docker info` succeeds.
- Confirm Docker Desktop is using Linux containers.

**Symptom:** ECR login or push fails.

- Confirm `$EcrRegistry` contains the expected account ID and `ap-south-1`.
- Re-run `aws sts get-caller-identity` and the ECR login command.
- Confirm the repository exists and the identity has ECR push permissions.

### 3. ECS service-linked role

**Symptom:** ECS says `Unable to assume the service linked role`.

1. Open **IAM > Roles** and search for `AWSServiceRoleForECS`.
2. If the correctly named service-linked role was just created, wait 30–60 seconds and retry.
3. If absent, use Step 9 or run:

   ```powershell
   aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
   ```

4. If creation returns `AccessDenied`, ask the administrator for
   `iam:CreateServiceLinkedRole` or ask them to create the role.
5. If a role with that name exists but its ARN does not contain
   `/aws-service-role/ecs.amazonaws.com/`, do not delete it yourself; ask the administrator to
   resolve the conflict.

### 4. Task image, secret, and logging startup

**Symptom:** ECS reports `CannotPullContainerError`.

Confirm that:

- the tagged image exists in ECR;
- ECR and ECS are both in `ap-south-1` and the same account;
- the image URI in both container definitions is exact;
- the task execution role has `AmazonECSTaskExecutionRolePolicy`; and
- the task is in a public subnet, has a public IP, and has outbound access.

**Symptom:** ECS reports a secret-access or resource-initialization error.

Confirm that:

- the secret ARN in the task definition is exact;
- the secret is in `ap-south-1`;
- `ReadOpenAIKey` is attached to the selected execution role; and
- its `Resource` matches the full secret ARN, including the generated suffix.

### 5. Container process and health

**Symptom:** the task starts and then stops or cycles repeatedly.

Open **ECS > Clusters > openai-llm-cluster > openai-llm-service** and check in this order:

1. **Tasks > Stopped**: stopped reason and container exit code.
2. **Service events**: placement, role, networking, image, secret, and health messages.
3. **CloudWatch Logs > `/ecs/openai-llm-app`**: Python tracebacks and startup output.
4. Task definition: command, environment variables, secret ARN, and log settings.

If a health check reports `curl: not found`, an older task-definition revision is still using the
previous curl-based command. Create a new revision using the Python health check in Step 10 and
update the service to it.

If a stopped container reports `exec format error`, the image architecture does not match the
task definition. Rebuild and push with `--platform linux/amd64`, then force a new deployment.

### 6. Browser-to-task network path

**Symptom:** the browser times out or refuses the connection.

Confirm that:

- the task is `RUNNING` and the `frontend` container is `HEALTHY`;
- you copied the current task's public IP, not the stopped task's address;
- Public IP assignment is on;
- the selected subnet is public and its route table reaches an internet gateway;
- `openai-llm-demo` is attached to the task ENI;
- it allows TCP `8501` from your current public IP; and
- the URL begins with `http://` and includes `:8501`.

A timeout often suggests that packets are being dropped by routing or a firewall. An immediate
connection refusal more often suggests that the host is reachable but no process is listening on
that port. Treat these as clues, not absolute rules.

### 7. Frontend-to-API and API-to-OpenAI paths

**Symptom:** Streamlit opens but reports that it cannot reach the backend.

- Confirm `API_BASE_URL` is exactly `http://localhost:8000`.
- Confirm the `api` container is running and healthy.
- Inspect the API log stream for startup errors.

**Symptom:** the UI opens but generation returns an API error.

- Use the API log stream and HTTP status code to distinguish invalid input, authentication,
  rate-limit, timeout, and upstream service errors.
- Confirm the secret contains only the key, with no `OPENAI_API_KEY=` prefix or surrounding
  quotation marks.
- Confirm the OpenAI project/key is active and has suitable access and budget.
- Never print the key while diagnosing it.

## Cleanup after the demo

### Why order matters

Cloud resources have dependencies. The service owns running tasks; a running task owns an ENI;
the ENI uses the security group. Delete the controller first and wait for dependents to disappear
before deleting the resources they reference.

Stopping compute prevents further Fargate runtime cost, but stored images, logs, and secrets can
continue to incur charges until removed.

### Delete the resources

1. **ECS service:** update `openai-llm-service` to zero desired tasks, wait for the task to stop,
   and delete the service.
2. **ECS cluster:** delete `openai-llm-cluster` after its service is gone.
3. **EC2 > Network Interfaces:** if needed, wait until the stopped task's ENI disappears.
4. **EC2 > Security Groups:** delete `openai-llm-demo` after no ENI uses it.
5. **ECR:** delete the `openai-llm-app` repository and all contained images.
6. **CloudWatch Logs:** delete `/ecs/openai-llm-app`.
7. **Secrets Manager:** delete `openai-llm-app/openai-api-key` using the recovery window required
   by the lab/account. Do not use force deletion unless the lab owner explicitly requires it.
8. **IAM > Roles:** remove `ReadOpenAIKey`, detach
   `AmazonECSTaskExecutionRolePolicy`, and delete `openaiLlmEcsTaskExecutionRole`.
9. **Task definitions:** deregister unused `openai-llm-app` revisions if desired. Registered task
   definitions do not run compute by themselves.

Do not delete the default VPC, its subnets, route tables, or internet gateway. Do not delete the
ECS service-linked role in a shared AWS account unless the administrator explicitly asks you
to do so.

**Cleanup checkpoint:** the ECS service has no running tasks, and the lab's ECR repository,
secret, log group, security group, and custom execution role are gone or scheduled for deletion.

## Knowledge check

Try to answer these without looking back:

1. Why can the frontend call port `8000` even though the security group does not allow inbound
   `8000`?
2. What is the difference between an ECR repository and an ECS cluster?
3. What is the difference between a task definition and a task?
4. Why does the execution role need a secret-specific inline policy?
5. Why are a public subnet and a public IP both needed in this lab?
6. What does the ECS service do when its only task stops?
7. Why does pushing a new `latest` image not change the running task?
8. Which lab choices would you change first for production?

### Suggested answers

1. The containers are in one `awsvpc` task and communicate over `localhost`; the security group
   controls traffic reaching the task ENI, not same-task loopback traffic.
2. ECR stores image artifacts; an ECS cluster logically groups running tasks and services.
3. A task definition is a versioned blueprint; a task is one running instance of that blueprint.
4. The managed execution policy covers common pull/log actions but deliberately does not allow
   arbitrary secret retrieval; the inline policy grants one required action on one secret.
5. The public subnet supplies a route to an internet gateway, and the public IP supplies an
   internet-routable address for IPv4 traffic. Either one alone is insufficient.
6. The service scheduler starts a replacement to restore desired count `1`.
7. Running containers keep the image content with which they started; a new deployment is needed
   to start replacement containers from the updated tag.
8. Use private tasks behind an HTTPS load balancer, multiple tasks across AZs, immutable image
   versions, automated deployment, stronger application access control, and infrastructure as
   code.

## Glossary

| Term | Meaning in this lab |
|---|---|
| Account ID | Twelve-digit number that scopes AWS ownership and appears in ARNs and the ECR URI |
| ARN | Amazon Resource Name; an unambiguous identifier used in references and IAM policies |
| Availability Zone | Isolated infrastructure location within a Region |
| AWS CLI | Command-line client that signs and sends requests to AWS APIs |
| CIDR | Notation for an IP network range, such as `172.31.0.0/16` or one IP as `/32` |
| Cluster | Logical ECS grouping for tasks and services |
| Container | Running instance of an image |
| Desired count | Number of task copies an ECS service tries to keep running |
| Digest | Content-addressed, immutable identifier for an image |
| ECR | Managed registry that stores the application's container image |
| ECS | AWS container orchestration service |
| ENI | Elastic Network Interface; the task's virtual network card in the VPC |
| Environment variable | Runtime key/value configuration supplied to a process |
| Execution role | IAM role used by the ECS/Fargate agent for image pull, secrets, and logs |
| Fargate | Managed compute engine that runs containers without customer-managed hosts |
| Health check | Repeated command or request used to decide whether a container is responding |
| IAM | AWS system for identities, roles, trust, and authorization policies |
| Image | Packaged application filesystem and startup metadata used to create containers |
| Internet gateway | VPC component used as the route target for internet traffic |
| Least privilege | Granting only the required actions on only the required resources |
| Log group | Collection of CloudWatch log streams sharing retention and access settings |
| Port | Numeric process endpoint at an IP address; this lab uses `8000`, `8501`, and outbound `443` |
| Public subnet | Subnet whose route table contains a route to an internet gateway |
| Region | Separate AWS geographic area, here `ap-south-1` |
| Repository | Named ECR collection of image versions |
| Route table | Rules that decide the next network hop for destination ranges |
| Secret | Sensitive value stored and retrieved under controlled access |
| Security group | Stateful allow-list firewall attached here to the task ENI |
| Service | ECS controller that deploys and maintains a desired number of tasks |
| Service-linked role | AWS-managed IAM role linked to a service, here ECS |
| Subnet | Range of VPC IP addresses located in one Availability Zone |
| Tag | Movable image label such as `latest`; also a separate AWS resource-labeling concept |
| Task | Running instance of an ECS task definition, containing both lab containers |
| Task definition | Immutable, revisioned ECS blueprint for containers and runtime settings |
| Task role | Optional IAM role whose permissions are available to application code in the task |
| TCP | Reliable, connection-oriented transport protocol used by HTTP/HTTPS in this lab |
| VPC | Isolated virtual network containing the task's subnets, routes, and security controls |

## Further reading

- [AWS Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html)
- [What is Amazon ECR?](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [Amazon ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [Fargate task networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html)
- [Amazon ECS task execution IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)
- [Pass Secrets Manager secrets to ECS containers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html)
- [CloudWatch Logs concepts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogsConcepts.html)
- [Internet gateways and public subnets](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
- [ECS container health checks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/healthcheck.html)
- [ECS rolling deployments and image resolution](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html)

# Model Context Protocol (MCP) — Interview Questions

*Built from* Build and Deploy an MCP Server *and the Week 4 MCP project material.*

*Scoped to **MCP** — what it is, its architecture, its primitives, and the 2026 protocol changes that invalidate most older material. Generic tool calling is `02`. Two-layer answers throughout.*

> **⚠️ Read this first.** The July 2026 specification revision **removed MCP's session handshake**, making the protocol stateless. Most tutorials, and the course material this folder is built from, describe MCP as offering "stateful context, unlike stateless REST." That is now wrong, and "is MCP stateful?" has become a trap question. Details in Q4.

---

**🎙️ Interview Q1:** "What problem does MCP actually solve?"

**✅ Strong answer:** "The **N×M integration problem.** Before MCP, every AI application had to write its own custom integration for every tool. Five apps and ten tools meant fifty separate integrations, each maintained separately.

MCP makes it N+M. Each tool exposes one MCP server; each application speaks MCP once. Ten servers, five clients, and any client can use any server.

**Everyday example:** it's USB. Before USB, every peripheral had its own port and its own cable. After, one standard — and a device manufacturer implements it once rather than once per computer brand.

The genuinely useful framing for an interview: **MCP is not a new capability, it's a standardisation.** Function calling already let models use tools. MCP standardises *how tools describe and expose themselves*, so integrations become reusable across applications rather than bespoke per application."

**🎯 Standard Interview Answer:** "MCP addresses combinatorial integration cost. Bespoke tool integration scales as the product of applications and tools; a standard protocol reduces this to a sum, since each tool implements one server and each application implements one client. The protocol does not introduce new model capability — native tool calling already provides invocation — it standardises capability discovery, schema description and transport, making integrations portable across host applications rather than application-specific."

---

**🎙️ Interview Q2:** "Describe MCP's architecture."

**✅ Strong answer:** "Three roles:

- **Host** — the application the user interacts with. Claude Desktop, an IDE, your own app. It owns the LLM context and the UI.
- **Client** — lives inside the host, one per server connection. Handles the protocol.
- **Server** — exposes the actual capability. Wraps a database, an API, a filesystem.

```
Host (your app)
 ├── Client A ──► Server: GitHub
 ├── Client B ──► Server: Postgres
 └── Client C ──► Server: Slack
```

Communication is **JSON-RPC**. Transport is either **stdio** for local servers — the host spawns the process and talks over standard input/output — or **streamable HTTP** for remote ones.

The design point worth stating: **servers are LLM-agnostic.** An MCP server knows nothing about which model is calling it. It exposes typed capabilities; the host decides what to do with them. That's what makes servers reusable across Claude, an IDE, or your own application."

**🎯 Standard Interview Answer:** "Three-role architecture. The host is the user-facing application owning LLM context and presentation. Clients are per-connection protocol handlers instantiated within the host, maintaining one-to-one correspondence with servers. Servers expose capabilities over a standard schema and are entirely model-agnostic — they have no knowledge of the invoking model, which is what makes them portable across hosts. Message encoding is JSON-RPC; transports are stdio for locally spawned server processes and streamable HTTP for remote servers. HTTP+SSE is formally deprecated as of the 2026 revision."

---

**🎙️ Interview Q3:** "What are MCP's primitives?"

**✅ Strong answer:** "Three, and the distinction between the first two gets asked a lot:

- **Tools** — actions the **model** chooses to call. `create_issue`, `run_query`. Model-controlled.
- **Resources** — read-only data the **application** supplies as context. A file's contents, a database row. Application-controlled.
- **Prompts** — reusable templates the **user** invokes. Slash commands, essentially. User-controlled.

**The clean way to remember it: who is in control.** Tools = model decides. Resources = app decides. Prompts = user decides.

**Everyday example:** in an IDE — a tool is 'run the tests' (the AI decides to), a resource is 'the file you currently have open' (the IDE supplies it), and a prompt is a '/review' command you type.

The mistake I'd avoid is treating resources as tools. A resource shouldn't have side effects — it's a read. If it changes something, it's a tool."

**🎯 Standard Interview Answer:** "Three primitives differentiated by control locus. Tools are model-controlled executable operations with side effects, selected by the model from schema descriptions. Resources are application-controlled read-only context supplied by the host — file contents, records, documents — addressed by URI and free of side effects. Prompts are user-controlled parameterised templates surfaced as explicit user actions. Conflating resources with tools is a common design error: side-effecting operations belong in the tool primitive, and resources must remain idempotent reads."

---

**🎙️ Interview Q4:** "Is MCP stateful?"

**✅ Strong answer:** "**Not any more — and this is the question most candidates get wrong because the material hasn't caught up.**

The **July 2026 specification revision removed the `initialize` handshake and the `Mcp-Session-Id` header entirely.** Every request is now self-contained, so any server instance can serve any request.

Why they did it matters more than the fact: the session handshake meant a client was pinned to a specific server instance. That breaks horizontal scaling — you need sticky routing, and a server restart drops every session. Stateless requests let you put servers behind an ordinary load balancer and scale them like any other web service.

Also deprecated in that revision, on a twelve-month window: **sampling, roots, and logging**, replaced by Multi Round-Trip Requests. And **HTTP+SSE** as a transport.

So the correct answer is: MCP *was* session-based, is now stateless by design, and if you need conversational state that lives in your host application, not in the protocol."

**🎯 Standard Interview Answer:** "As of the 2026-07-28 specification revision, no. The `initialize` handshake and `Mcp-Session-Id` header were removed, making every request self-contained and allowing any server replica to service any request. The motivation is horizontal scalability: session affinity required sticky routing and made server restarts session-destroying, whereas stateless requests permit conventional load-balanced deployment. The same revision deprecated sampling, roots and logging on a twelve-month sunset in favour of Multi Round-Trip Requests, and formally deprecated the HTTP+SSE transport. Conversational state is consequently the host application's responsibility, not the protocol's."

---

**🎙️ Interview Q5:** "How is MCP different from just writing function-calling tools?"

**✅ Strong answer:** "Function calling is the **mechanism**; MCP is the **distribution standard**. They're not alternatives — an MCP tool ends up as a function call to the model.

The difference is reuse and ownership:

| | Function calling | MCP |
|---|---|---|
| Where the tool lives | In your application code | In a separate server process |
| Who can use it | Only your app | Any MCP-speaking client |
| Who maintains it | You | Whoever owns the server |
| Discovery | Hardcoded | Queried at runtime |

The real-world consequence: if GitHub publishes an MCP server, I don't write GitHub integration code at all. I point my client at their server and their tools appear. When they add a capability, I get it without a code change.

**When plain function calling is still right:** a tool tightly coupled to your own application logic, or where the extra process hop costs more than it's worth. MCP adds a network boundary — not free."

**🎯 Standard Interview Answer:** "Function calling is the invocation mechanism; MCP is a distribution and discovery standard layered above it — MCP tools are ultimately surfaced to the model as function calls. The differentiators are process isolation, cross-host reusability, externalised maintenance ownership, and runtime capability discovery rather than compile-time registration. The practical implication is that vendor-published servers eliminate integration code entirely and propagate new capabilities without client changes. Plain function calling remains preferable for tools tightly coupled to host application state, or where the additional process and transport boundary is not justified by reuse."

---

**🎙️ Interview Q6:** "What are the security concerns with MCP?"

**✅ Strong answer:** "Several, and they're taken seriously enough that NSA/CISA published guidance on it in 2026.

**Untrusted servers.** Connecting to a third-party MCP server means giving it a channel into your AI application. A malicious server can return tool descriptions crafted to manipulate the model — 'tool poisoning'. The tool description *is* prompt content.

**Over-broad scope.** MCP servers frequently request wide access — a filesystem server pointed at your home directory. Least privilege applies: scope the server to the narrowest path or dataset that works.

**Prompt injection via resources.** A resource's *content* enters the model's context. A document containing instructions is an injection vector, and MCP makes fetching such documents routine.

**Confused deputy.** The server acts with *its* credentials, not the end user's. If your server holds a database connection with broad rights, every user of that server effectively has those rights unless you enforce per-user authorisation inside the server.

The one I'd emphasise: **authorisation belongs in the server, at the point of execution**, and it must be keyed to the actual requesting user — not assumed from the fact that a request arrived."

**🎯 Standard Interview Answer:** "Four principal concerns. Untrusted server connection, where tool descriptions constitute model-visible prompt content and can be adversarially crafted — tool poisoning. Excessive capability scope, where servers request broader filesystem or data access than required, mitigated by least-privilege configuration. Indirect prompt injection through resource content entering context. And confused-deputy exposure, where the server executes under its own credentials rather than the requesting user's, effectively granting every client the server's full authority absent per-request authorisation. Mitigation requires authorisation enforcement inside the server at dispatch time, bound to verified caller identity. NSA and CISA published formal MCP security design guidance in 2026 reflecting these concerns."

---

**🎙️ Interview Q7:** "Walk me through building a minimal MCP server."

**✅ Strong answer:** "With FastMCP it's genuinely small:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool
def get_order_status(order_id: str) -> str:
    \"\"\"Look up the delivery status of an existing order.

    Args:
        order_id: The alphanumeric order reference, e.g. ORD-48219
    \"\"\"
    return db.lookup(order_id)

if __name__ == "__main__":
    mcp.run()
```

The decorator does the work — it introspects the type hints to generate the JSON schema and uses the docstring as the description the model reads.

Which means **the docstring is not documentation, it's the model's interface contract.** Same rules as any tool: say when to use it, describe every parameter, state what it doesn't do.

Then you register it with the host — for a local stdio server that's a config entry naming the command to run. FastMCP is at v4 as of 2026; material referencing v2 patterns is dated, though the `@mcp.tool` decorator itself is unchanged."

**🎯 Standard Interview Answer:** "Using FastMCP, a server is a `FastMCP` instance with functions registered via the `@mcp.tool` decorator, which derives the JSON schema from type annotations and the tool description from the docstring. The docstring is therefore an interface specification consumed by the model rather than developer documentation, and is subject to the same design requirements as any tool schema — usage conditions, per-parameter description, explicit negative scope. Local deployment uses stdio transport with host configuration specifying the launch command; remote deployment uses streamable HTTP. FastMCP is at major version 4 as of 2026, though the decorator API is stable across recent versions."

---

**🎙️ Interview Q8:** "Who owns MCP now?"

**✅ Strong answer:** "This trips people up. **MCP is a Linux Foundation project**, under the Agentic AI Foundation established in December 2025. Anthropic created it and donated it.

Same for **A2A** — Google's agent-to-agent protocol — which is also under the same foundation and reached v1.0.0 in January 2026.

So saying 'Anthropic's protocol' or 'Google's protocol' in an interview is now out of date. Both are vendor-neutral governance.

The distinction between them is worth knowing: **MCP connects an agent to tools and data. A2A connects agents to each other.** They're complementary layers, not competitors."

**🎯 Standard Interview Answer:** "MCP is governed by the Linux Foundation under the Agentic AI Foundation, established December 2025, following donation by Anthropic. A2A is under the same foundation and reached version 1.0.0 in January 2026. Characterising either as a single vendor's protocol is outdated. Functionally they are complementary rather than competing: MCP standardises agent-to-tool and agent-to-data connectivity, while A2A standardises inter-agent communication and capability discovery."

---

## Sources

- [MCP Interview Questions: Beginner to Advanced (2026) — DataCamp](https://www.datacamp.com/blog/mcp-interview-questions)
- [Top MCP Interview Questions & Answers: AI Agents & Tool Calling (2026) — Hirist](https://www.hirist.tech/blog/top-mcp-interview-questions-answers-ai-agents-tool-calling/amp/)
- [Top 20 Model Context Protocol (MCP) Interview Questions: 2026 — TechInterview](https://www.techinterview.net/questions/model-context-protocol-mcp-interview-questions)
- [Model Context Protocol (MCP) — GeeksforGeeks](https://www.geeksforgeeks.org/artificial-intelligence/model-context-protocol-mcp/)
- [MCP Security Design — NSA/CISA (PDF)](https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF)
- [MCP specification revision, 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

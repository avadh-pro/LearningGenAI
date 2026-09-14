---
source: https://docs.langchain.com/oss/python/langchain/mcp/tools
title: Tools
package: langchain
---

# Tools

The `langchain.mcp` namespace requires `langchain[mcp]>=1.4.0` and is in beta. The API may change.

[`MCPAdapter`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter) bridges MCP servers and LangChain agents: it discovers the tools a server advertises and adapts them into standard LangChain tools. Pass the tools from `list_tools()` to [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) as you would any other LangChain tool.

This page covers what is specific to that bridge: identifying MCP tools, controlling their execution, handling their outputs, and responding when a server needs input during a call. For the runnable discovery-and-agent example, see the [MCP quickstart](/oss/python/langchain/mcp).

## Use MCP tools in an agent

Discover the server’s catalog with [`MCPAdapter.list_tools`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter/list_tools), then give the returned tools to [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent). From the agent’s perspective, they behave like LangChain tools: the model chooses a tool, LangChain invokes it, and the resulting [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) returns to the model.

```
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

async def run_agent(server) -> dict:
    # Discover the server's tools, then hand them to the agent like any other
    # LangChain tools. The tools hold the client, so the agent stays usable
    # for the life of the adapter context.
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        return await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": "What is the forecast for Oslo?"}
                ]
            }
        )
```

[View example traceOpen a public LangSmith run for this example.](https://smith.langchain.com/public/025418ad-e7bc-43a3-b700-d1a78b3a4856/r)

For general guidance on defining, binding, and using LangChain tools, see [Tools](/oss/python/langchain/tools). For several MCP servers and their namespaced tool catalogs, see [Connections](/oss/python/langchain/mcp/connections#multiple-servers).

## Tool metadata

Each adapted tool may carry its MCP provenance under an `mcp` namespace on the LangChain tool’s metadata:

```
tool.metadata
# {
#     "mcp": {
#         "tool": {
#             "annotations": {
#                 "destructive_hint": True,
#                 "read_only_hint": False,
#             },
#             "_meta": {"origin": "crm"},
#         },
#         "server": {
#             "name": "crm",
#             "version": "2.1.0",
#         },
#     },
# }
```

Every nested field is optional: a server may provide tool annotations, `_meta`, server identity, any combination of those, or none. `annotations` contains MCP hints such as `read_only_hint` and `destructive_hint`; `_meta` is opaque metadata supplied by the server; and `server` identifies the MCP implementation that advertised the tool.

Read optional metadata defensively, so a missing field returns a default rather than raising:

```
from langchain.tools import BaseTool

def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata."""
    # Chain `.get` with defaults so a tool missing any nested field returns
    # False rather than raising.
    annotations = (
        (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    )
    return annotations.get("destructive_hint", False)
```

## Handle tool outputs

MCP tool results become LangChain-native values: content the model can read, an artifact for structured output, and a [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) status that distinguishes a server-reported error from a transport failure.

### Multimodal content

An MCP tool result arrives as LangChain [content blocks](/oss/python/langchain/messages#standard-content-blocks). Image and file content convert into standardized `image` and `file` blocks alongside `text`, so a tool that returns a screenshot reaches the model as an image block:

```
from langchain.mcp import MCPAdapter

async def access_multimodal_tool_content(server) -> None:
    async with MCPAdapter(server) as adapter:
        [screenshot] = await adapter.list_tools()

    # An MCP result arrives as LangChain content blocks. Image and file content
    # convert into standardized `image`/`file` blocks alongside `text`.
    message = await screenshot.ainvoke(
        {"name": "take_screenshot", "args": {}, "id": "1", "type": "tool_call"}
    )
    for block in message.content_blocks:
        if block["type"] == "text":
            print(f"Text: {block['text']}")
        elif block["type"] == "image":
            print(f"Image mime type: {block.get('mime_type')}")
            print(
                f"Image base64: {block.get('base64', '')[:20]}..."
            )
```

### Structured content

When a tool returns structured content, the adapter attaches it to the [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) as an artifact rather than folding it into the model-visible text. Read it off `message.artifact`:

```
message = await tool.ainvoke({"name": "...", "args": {...}, "id": "1", "type": "tool_call"})
if message.artifact is not None:
    structured = message.artifact["structured_content"]
```

The artifact is an `MCPToolArtifact`, whose `structured_content` field holds the tool result’s `structuredContent`.

### Errors

An MCP tool result carries an `isError` flag. When a server reports `isError=True`, the adapter converts it into a [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) with `status="error"` carrying the server’s own message, so the agent can read it and correct itself:

```
from langchain.mcp import MCPAdapter

async def divide_by_zero(server):
    async with MCPAdapter(server) as adapter:
        [divide] = await adapter.list_tools()

    # A server error (isError=True) reaches the model as a failed ToolMessage,
    # so the agent can read the server's own message and retry. Transport
    # failures still raise, because a model cannot act on those.
    return await divide.ainvoke(
        {"name": "divide", "args": {"a": 10, "b": 0}, "id": "1", "type": "tool_call"}
    )
```

A server-reported error reaches the model as a failed tool message, but a transport or session failure raises instead, because a model cannot act on a dropped connection.

## Human-in-the-loop

Reading annotations lets you gate a tool based on what the server declares about it, rather than hardcoding tool names. An MCP server can flag a tool as destructive with the `destructiveHint` annotation, which [`MCPAdapter`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter) surfaces under `metadata["mcp"]["tool"]["annotations"]["destructive_hint"]`.

Give an [`InterruptOnConfig`](https://reference.langchain.com/python/langchain/agents/middleware/human_in_the_loop/InterruptOnConfig) a `when` predicate: a callable that receives the pending [`ToolCallRequest`](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/ToolCallRequest) and returns whether that call needs approval. Read the destructive hint from metadata once at load time, then let the callable decide per call, so one config covers whatever destructive tools a server exposes without hardcoding tool names:

```
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
from langchain.tools import BaseTool
from langchain.tools.tool_node import ToolCallRequest

def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata."""
    annotations = (
        (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    )
    return annotations.get("destructive_hint", False)

async def gate_destructive_tools(server):
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()

        # Read the destructive hint from metadata once, then let a callable
        # decide per call. One config covers whatever destructive tools a
        # server exposes, without hardcoding tool names.
        destructive = {tool.name for tool in tools if is_destructive(tool)}

        def needs_approval(request: ToolCallRequest) -> bool:
            return request.tool_call["name"] in destructive

        gate = InterruptOnConfig(
            allowed_decisions=["approve", "reject"], when=needs_approval
        )
        interrupt_on: dict[str, bool | InterruptOnConfig] = {
            tool.name: gate for tool in tools
        }
        return create_agent(
            "claude-sonnet-5",
            tools,
            middleware=[HumanInTheLoopMiddleware(interrupt_on=interrupt_on)],
            checkpointer=InMemorySaver(),
        )
```

When the agent calls a tool the predicate gates, the run pauses. Approve it to let the tool run, or reject it to skip the tool and tell the model:

```
from langgraph.types import Command

# Approve the pending destructive call and resume.
resumed = await agent.ainvoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
```

The predicate also sees the call’s arguments through `request.tool_call["args"]`, so a tool can run freely for safe inputs and pause only for risky ones, such as a `delete_file` call targeting a protected path. Combine both to gate a tool only when its type and its arguments warrant it.

For the full approval workflow, see [Human-in-the-loop](/oss/python/langchain/human-in-the-loop).

## Server requests during tool execution

Most tools finish without asking the client for anything mid-call. When a server does need input, [`MCPAdapter`](https://reference.langchain.com/python/langchain/mcp/adapter/MCPAdapter) answers [elicitation](https://modelcontextprotocol.io/specification/draft/client/elicitation) automatically through a LangGraph [`interrupt`](https://reference.langchain.com/python/langgraph/types/interrupt).

### Elicitation

[Elicitation](https://modelcontextprotocol.io/specification/draft/client/elicitation) is the MCP mechanism for a server to request input in the middle of a tool call. When a server needs input, the request surfaces as a LangGraph interrupt so the person already reviewing the agent’s work answers it and the run resumes:

```
from typing import Any

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

async def book_with_elicitation(server) -> dict:
    # Elicitation is handled automatically: when a server needs input mid-call,
    # the adapter surfaces the question as a LangGraph `interrupt()`, so the
    # person already reviewing the agent's work answers it and the run resumes.
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()

        # Resuming a paused run needs persistence, so the interrupted run has
        # somewhere to wait.
        agent = create_agent("claude-sonnet-5", tools, checkpointer=InMemorySaver())
        config: Any = {"configurable": {"thread_id": "booking-1"}}

        paused = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Book a table for 4."}]}, config
        )
        [interrupt] = paused["__interrupt__"]
        [question] = interrupt.value["requests"]

        # Answers are keyed by the server's own request key, so nothing has to
        # be tracked across the pause. `decline` or `cancel` would refuse.
        answer = {"action": "accept", "content": {"date": "2026-09-14"}}
        return await agent.ainvoke(
            Command(resume={"responses": {question["key"]: answer}}), config
        )
```

A few things to note:

- **Elicitation is on by default.** The adapter arms every client it builds to advertise the capability and drives the interrupt loop. A prebuilt client that already carries its own elicitation handler is honored instead of overridden.
- **Resuming needs persistence.** Attach a [checkpointer](/oss/python/langchain/short-term-memory) so the interrupted run has somewhere to wait.
- **Answers are keyed by the server’s request key.** Resume with `Command(resume={"responses": {key: answer}})`. Each answer’s `action` is `accept` (with `content` matching the request’s schema), `decline` (answer refused, call continues), or `cancel` (the whole call is abandoned).

The interrupt payload and answer types live in `langchain.mcp.elicitation`.

Only elicitation is answered this way. A server that instead asks for [sampling](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling) (running an LLM completion) or [roots](https://modelcontextprotocol.io/specification/2025-06-18/client/roots) (reachable local paths) raises `NotImplementedError`, because the modern, sessionless protocol has no live back-channel for those requests. See [Sampling and roots](/oss/python/migrate/langchain-mcp-adapters#sampling-and-roots).

Interrupt-driven elicitation answers a server that returns its request as an `InputRequiredResult` (the modern protocol’s input-required round). A server that only pushes elicitation over a legacy handshake session cannot be answered this way.

## See also

- [Content blocks](/oss/python/langchain/messages#standard-content-blocks)
- [Tools](/oss/python/langchain/tools)
- [Human-in-the-loop](/oss/python/langchain/human-in-the-loop)
- [FastMCP calling tools](https://gofastmcp.com/clients/tools)
- [FastMCP client elicitation](https://gofastmcp.com/clients/elicitation)
- [FastMCP server elicitation](https://gofastmcp.com/servers/elicitation)
- [MCP elicitation specification](https://modelcontextprotocol.io/specification/draft/client/elicitation)
- [MCP tool annotations](https://modelcontextprotocol.io/specification/draft/server/tools)

---

[Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.

[Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/mcp/tools.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).

Was this page helpful?

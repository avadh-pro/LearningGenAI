---
source: https://docs.langchain.com/oss/python/langchain/test/evals
title: Agent Evals
package: langchain
---

# Agent Evals

Evaluations (“evals”) measure how well your agent performs by assessing its execution trajectory, the sequence of messages and tool calls it produces. Unlike [integration tests](/oss/python/langchain/test/integration-testing) that verify basic correctness, evals score agent behavior against a reference or rubric, making them useful for catching regressions when you change prompts, tools, or models.

An evaluator is a function that takes agent outputs (and optionally reference outputs) and returns a score:

```
def evaluator(*, outputs: dict, reference_outputs: dict):
    output_messages = outputs["messages"]
    reference_messages = reference_outputs["messages"]
    score = compare_messages(output_messages, reference_messages)
    return {"key": "evaluator_score", "score": score}
```

The [`agentevals`](https://github.com/langchain-ai/agentevals) package provides prebuilt evaluators for agent trajectories. You can evaluate by performing a **trajectory match** (deterministic comparison) or by using an **LLM judge** (qualitative assessment):

| Approach | When to use |
| --- | --- |
| [Trajectory match](#trajectory-match-evaluator) | You know the expected tool calls and want fast, deterministic, cost-free checks |
| [LLM-as-judge](#llm-as-judge-evaluator) | You want to assess overall quality and reasoning without strict expectations |

## Install AgentEvals

```
pip install -U agentevals
```

```
uv add agentevals
```

Or, clone the [AgentEvals repository](https://github.com/langchain-ai/agentevals) directly.

## Trajectory match evaluator

AgentEvals offers the `create_trajectory_match_evaluator` function to match your agent’s trajectory against a reference. There are four modes:

| Mode | Description | Use case |
| --- | --- | --- |
| `strict` | Exact match of message structure and tool calls in the same order (message content can differ) | Testing specific sequences (e.g., policy lookup before authorization) |
| `unordered` | Same message structure and tool calls as reference, but tool calls can happen in any order | Verifying information retrieval when order doesn’t matter |
| `subset` | Agent calls only tools from reference (no extras) | Ensuring agent doesn’t exceed expected scope |
| `superset` | Agent calls at least the reference tools (extras allowed) | Verifying minimum required actions are taken |

The examples below share a common setup, an agent with a `get_weather` tool:

```
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from agentevals.trajectory.match import create_trajectory_match_evaluator

@tool
def get_weather(city: str):
    """Get weather information for a city."""
    return f"It's 75 degrees and sunny in {city}."

agent = create_agent("claude-sonnet-4-6", tools=[get_weather])
```

Strict match

The `` mode ensures trajectories contain identical messages in the same order with the same tool calls, though it allows for differences in message content. This is useful when you need to enforce a specific sequence of operations, such as requiring a policy lookup before authorizing an action.

Unordered match

The `` mode allows the same tool calls in any order. This is helpful when you want to verify that specific information was retrieved but don’t care about the sequence. For example, an agent that checks both weather and events for a city with different tool calls.

Subset and superset match

The `` and `` modes match partial trajectories. The `` mode verifies that the agent called at least the tools in the reference trajectory, allowing additional tool calls. The `` mode ensures the agent did not call any tools beyond those in the reference.

You can also set the `tool_args_match_mode` property and/or `tool_args_match_overrides` to customize how the evaluator considers equality between tool calls in the actual trajectory vs. the reference. By default, only tool calls with the same arguments to the same tool are considered equal. Visit the [repository](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#tool-args-match-modes) for more details.

## LLM-as-judge evaluator

You can use an LLM to evaluate the agent’s execution path with the `create_trajectory_llm_as_judge` function. Unlike trajectory match evaluators, it doesn’t require a reference trajectory, but one can be provided if available.

Without reference trajectory

With reference trajectory

If you have a reference trajectory, use the prebuilt `` prompt:

For more configurability over how the LLM evaluates the trajectory, visit the [repository](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#trajectory-llm-as-judge).

### Async support

All `agentevals` evaluators support Python asyncio. Async versions are available by adding `async` after `create_` in the function name.

Async judge and evaluator example

## Run evals in LangSmith

For tracking experiments over time, log evaluator results to [LangSmith](https://smith.langchain.com?utm_source=docs&utm_medium=cta&utm_campaign=langsmith-signup&utm_content=oss-langchain-test-evals). First, set the required environment variables:

```
export LANGSMITH_API_KEY="your_langsmith_api_key"
export LANGSMITH_TRACING="true"
```

LangSmith offers two main approaches for running evaluations: [pytest](/langsmith/pytest) integration and the `evaluate` function.

Use pytest integration

Run the evaluation with pytest:

Use the evaluate function

Create a [LangSmith dataset](/langsmith/manage-datasets) and use the `` function. The dataset must have the following schema:

- **input**: `{"messages": [...]}` input messages to call the agent with.
- **output**: `{"messages": [...]}` expected message history in the agent output. For trajectory evaluation, you can choose to keep only assistant messages.

To learn more about evaluating your agent, see the [LangSmith docs](/langsmith/pytest).

---

[Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.

[Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/test/evals.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).

Was this page helpful?

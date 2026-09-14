---
source: https://docs.langchain.com/oss/python/langchain/middleware/built-in
title: Prebuilt middleware
package: langchain
---

# Prebuilt middleware

LangChain and [Deep Agents](/oss/python/deepagents/overview) provide prebuilt middleware for common use cases. Each middleware is production-ready and configurable for your specific needs.

## Provider-agnostic middleware

The following middleware work with any LLM provider:

| Middleware | Description |
| --- | --- |
| [Tool error](#tool-error) | Catch tool execution exceptions and convert them to error messages for the model. |
| [Tool retry](#tool-retry) | Automatically retry failed tool calls with exponential backoff. |
| [Model retry](#model-retry) | Automatically retry failed model calls with exponential backoff. |
| [Model fallback](#model-fallback) | Automatically fallback to alternative models when primary fails. |
| [Summarization](#summarization) | Automatically summarize conversation history when approaching token limits. |
| [Human-in-the-loop](#human-in-the-loop) | Pause execution for human approval of tool calls. |
| [Model call limit](#model-call-limit) | Limit the number of model calls to prevent excessive costs. |
| [Tool call limit](#tool-call-limit) | Control tool execution by limiting call counts. |
| [PII detection](#pii-detection) | Detect and handle Personally Identifiable Information (PII). |
| [To-do list](#to-do-list) | Equip agents with task planning and tracking capabilities. |
| [LLM tool selector](#llm-tool-selector) | Use an LLM to select relevant tools before calling main model. |
| [Provider tool search](#provider-tool-search) | Defer tools behind providers’ server-side tool search, surfacing them on demand. |
| [Shell tool](#shell-tool) | Expose a persistent shell session to agents for command execution. |
| [Filesystem](#filesystem-middleware) | Provide agents with a filesystem for storing context and long-term memories. |
| [Subagent](#subagent) | Add the ability to spawn subagents. |
| [Rubric grading (Beta)](#rubric-grading) | Apply LLM-as-a-judge grading so agents self-evaluate and iterate until a rubric is satisfied. |
| [File search](#file-search) | Provide Glob and Grep search tools over filesystem files. |
| [Context editing](#context-editing) | Manage conversation context by trimming or clearing tool uses. |
| [LLM tool emulator](#llm-tool-emulator) | Emulate tool execution using an LLM for testing purposes. |

### Tool error

Catch exceptions raised during tool execution and convert them into error `ToolMessage`s that the model can see and recover from, instead of halting the agent run. Tool error is useful for the following:

- Letting the model retry a failed tool call with corrected arguments.
- Surfacing controlled, sanitized error messages instead of raw exception details.
- Preventing unexpected tool exceptions from crashing the agent.

Tool error middleware does not automatically retry failed calls. For retries, compose with [Tool retry](#tool-retry) middleware placed *inner* (earlier in the `middleware` list) and configured with `on_failure="error"` so that exceptions reach the tool error middleware. See the [full example](#tool-error-full-example) below.

**API reference:** [`ToolErrorMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/tool_error/ToolErrorMiddleware)

`ToolErrorMiddleware` requires `langchain>=1.3.14`.

```
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware

def on_error(exc: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exc, ValueError):
        return f"`{request.tool_call['name']}` failed with {type(exc).__name__}."
    # propagate everything else

agent = create_agent(
    model="gpt-5.5",
    tools=[your_tools],
    middleware=[ToolErrorMiddleware(on_error)],
)
```

Configuration options

[​](#param-on-error)

Callable[[Exception, ToolCallRequest], str | list[ContentBlock] | None]

Sync handler called for each exception raised by tool execution. Return content (a `` or list of content blocks) to convert the exception into a ``. Return `` or omit a return statement to let the exception propagate. Used on the sync path and, unless `` is given, on the async path.

[​](#param-aon-error)

Callable[[Exception, ToolCallRequest], Awaitable[str | list[ContentBlock] | None]]

Optional async handler, used on the async execution path. Falls back to `` when not provided.

[​](#param-tools)

list[BaseTool | str]

Optional list of tools or tool names to apply error handling to. If ``, applies to all tools.

Tool error full example

The `` handler receives the exception and the `` (which includes the tool call dict with name, args, and call ID). Return `` for exceptions you do not want to handle, and they will propagate normally.

Prefer returning content that names the exception type over the raw exception message, which may carry sensitive or internal detail. The `` handler controls disclosure: the raw exception message is never sent to the model unless you choose to include it.

### Tool retry

Automatically retry failed tool calls with configurable exponential backoff. Tool retry is useful for the following:

- Handling transient failures in external API calls.
- Improving reliability of network-dependent tools.
- Building resilient agents that gracefully handle temporary errors.

**API reference:** [`ToolRetryMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/tool_retry/ToolRetryMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

Configuration options

[​](#param-max-retries)

number

default:"2"

Maximum number of retry attempts after the initial call (3 total attempts with default)

[​](#param-tools-1)

list[BaseTool | str]

Optional list of tools or tool names to apply retry logic to. If ``, applies to all tools.

[​](#param-retry-on)

tuple[type[Exception], ...] | callable

default:"default_retry_on"

Either a tuple of exception types to retry on, or a callable that takes an exception and returns `` if it should be retried. With ``, the default retries retryable [model errors](/oss/python/langchain/models#model-exceptions) and all unclassified exceptions, and no longer retries model errors marked non-retryable.

[​](#param-on-failure)

string | callable

default:"continue"

Behavior when all retries are exhausted. Options:

- `'continue'` (default) - Return a `ToolMessage` with error details, allowing the LLM to handle the failure
- `'error'` - Re-raise the exception, stopping agent execution
- Custom callable - Function that takes the exception and returns a string for the `ToolMessage` content

**Deprecated values:** `` (use `` instead) and `` (use `` instead).

[​](#param-backoff-factor)

number

default:"2.0"

Multiplier for exponential backoff. Each retry waits `` seconds. Set to `` for constant delay.

[​](#param-initial-delay)

number

default:"1.0"

Initial delay in seconds before first retry

[​](#param-max-delay)

number

default:"60.0"

Maximum delay in seconds between retries (caps exponential backoff growth)

[​](#param-jitter)

boolean

default:"true"

Whether to add random jitter (``) to delay to avoid thundering herd

Full example

The middleware automatically retries failed tool calls with exponential backoff.

**Key configuration:**

- `max_retries` - Number of retry attempts (default: 2)
- `backoff_factor` - Multiplier for exponential backoff (default: 2.0)
- `initial_delay` - Starting delay in seconds (default: 1.0)
- `max_delay` - Cap on delay growth (default: 60.0)
- `jitter` - Add random variation (default: True)

**Failure handling:**

- `on_failure='continue'` (default) - Return error message
- `on_failure='error'` - Re-raise exception
- Custom function - Function returning error message

### Model retry

Automatically retry failed model calls with configurable exponential backoff. Model retry is useful for the following:

- Handling transient failures in model API calls.
- Improving reliability of network-dependent model requests.
- Building resilient agents that gracefully handle temporary model errors.

**API reference:** [`ModelRetryMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/model_retry/ModelRetryMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

Configuration options

[​](#param-max-retries-1)

number

default:"2"

Maximum number of retry attempts after the initial call (3 total attempts with default)

[​](#param-retry-on-1)

tuple[type[Exception], ...] | callable

default:"default_retry_on"

Either a tuple of exception types to retry on, or a callable that takes an exception and returns `` if it should be retried. With ``, the default retries retryable [model errors](/oss/python/langchain/models#model-exceptions) and all unclassified exceptions, and no longer retries model errors marked non-retryable.

[​](#param-on-failure-1)

string | callable

default:"continue"

Behavior when all retries are exhausted. Options:

- `'continue'` (default) - Return an `AIMessage` with error details, allowing the agent to potentially handle the failure gracefully
- `'error'` - Re-raise the exception (stops agent execution)
- Custom callable - Function that takes the exception and returns a string for the `AIMessage` content

[​](#param-backoff-factor-1)

number

default:"2.0"

Multiplier for exponential backoff. Each retry waits `` seconds. Set to `` for constant delay.

[​](#param-initial-delay-1)

number

default:"1.0"

Initial delay in seconds before first retry

[​](#param-max-delay-1)

number

default:"60.0"

Maximum delay in seconds between retries (caps exponential backoff growth)

[​](#param-jitter-1)

boolean

default:"true"

Whether to add random jitter (``) to delay to avoid thundering herd

Full example

The middleware automatically retries failed model calls with exponential backoff.

### Model fallback

Automatically fallback to alternative models when the primary model fails. Model fallback is useful for the following:

- Building resilient agents that handle model outages.
- Cost optimization by falling back to cheaper models.
- Provider redundancy across OpenAI, Anthropic, etc.

**API reference:** [`ModelFallbackMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/model_fallback/ModelFallbackMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-5.4-mini",
            "claude-3-5-sonnet-20241022",
        ),
    ],
)
```

Watch this [video guide](https://www.youtube.com/watch?v=8rCRO0DUeIM) demonstrating Model Fallback middleware behavior.

Configuration options

[​](#param-first-model)

string | BaseChatModel

required

First fallback model to try when the primary model fails. Can be a model identifier string (e.g., ``) or a `` instance.

[​](#param-additional-models)

string | BaseChatModel

Additional fallback models to try in order if previous models fail

### Summarization

Automatically summarize conversation history when approaching token limits, preserving recent messages while compressing older context. Summarization is useful for the following:

- Long-running conversations that exceed context windows.
- Multi-turn dialogues with extensive history.
- Applications where preserving full conversation context matters.

Summarization is text-oriented context compression. It does not resize, downsample, or otherwise compress image/audio/video payloads. Recent messages retained by `keep` still include their original multimodal blocks, while older multimodal messages that are summarized are represented only by the generated text summary. For image-heavy applications, store media in a filesystem or object store and pass URLs or file references through message history.

**API reference:** [`SummarizationMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
```

Configuration options

The `` conditions for `` and `` (shown below) rely on a chat model’s [profile data](/oss/python/langchain/models#model-profiles) if using ``. If data are not available, use another condition or specify manually:

[​](#param-model)

string | BaseChatModel

required

Model for generating summaries. Can be a model identifier string (e.g., ``) or a `` instance. See [``](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model) for more information.

[​](#param-trigger)

ContextSize | TriggerClause | list[ContextSize | TriggerClause] | None

Condition(s) for triggering summarization. Can be:

- A single [`ContextSize`](https://reference.langchain.com/python/langchain/agents/middleware/summarization/ContextSize) tuple (the specified threshold must be met)
- A single [`TriggerClause`](https://reference.langchain.com/python/langchain/agents/middleware/summarization/TriggerClause) dict (all specified thresholds must be met - AND logic)
- A list mixing either form (any item must be met - OR logic)

Supported thresholds are:

- `fraction` (float): Fraction of model’s context size (0-1)
- `tokens` (int): Absolute token count
- `messages` (int): Message count

A [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/ContextSize) tuple expresses exactly one threshold. A [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/TriggerClause) dict can include one or more thresholds, e.g. ``, and all thresholds in the dict must be met (AND).

Each [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/TriggerClause) dict must specify at least one threshold. If `` is not provided, summarization will not trigger automatically.

See the API reference for [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/ContextSize) and [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/TriggerClause) for more information.

[​](#param-keep)

ContextSize

default:"('messages', 20)"

How much context to preserve after summarization. Specify exactly one of:

- `fraction` (float): Fraction of model’s context size to keep (0-1)
- `tokens` (int): Absolute token count to keep
- `messages` (int): Number of recent messages to keep

See the API reference for [``](https://reference.langchain.com/python/langchain/agents/middleware/summarization/ContextSize) for more information.

[​](#param-token-counter)

function

Custom token counting function. Defaults to character-based counting.

[​](#param-summary-prompt)

string

Custom prompt template for summarization. Uses built-in template if not specified. The template should include `` placeholder where conversation history will be inserted.

[​](#param-trim-tokens-to-summarize)

number

default:"4000"

Maximum number of tokens to include when generating the summary. Messages will be trimmed to fit this limit before summarization.

[​](#param-summary-prefix)

string

deprecated

**Deprecated:** Use `` to provide the full prompt instead.

[​](#param-max-tokens-before-summary)

number

deprecated

**Deprecated:** Use `` instead. Token threshold for triggering summarization.

[​](#param-messages-to-keep)

number

deprecated

**Deprecated:** Use `` instead. Recent messages to preserve.

Full example

The summarization middleware monitors message token counts and automatically summarizes older messages when thresholds are reached.

**Trigger conditions** control when summarization runs:

- A single threshold triggers when that threshold is met
- A trigger clause with multiple thresholds triggers only when all thresholds are met (AND logic)
- A list of trigger conditions triggers when any item is met (OR logic)
- Each threshold can use `fraction` (of model’s context size), `tokens` (absolute count), or `messages` (message count)

**Keep condition** control how much context to preserve (specify exactly one):

- `fraction` - Fraction of model’s context size to keep
- `tokens` - Absolute token count to keep
- `messages` - Number of recent messages to keep

### Human-in-the-loop

Pause agent execution for human approval, editing, or rejection of tool calls before they execute. [Human-in-the-loop](/oss/python/langchain/human-in-the-loop) is useful for the following:

- High-stakes operations requiring human approval (e.g. database writes, financial transactions).
- Compliance workflows where human oversight is mandatory.
- Long-running conversations where human feedback guides the agent.

**API reference:** [`HumanInTheLoopMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/human_in_the_loop/HumanInTheLoopMiddleware)

Human-in-the-loop middleware requires a [checkpointer](/oss/python/langgraph/checkpointers#checkpoints) to maintain state across interruptions.

```
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def your_read_email_tool(email_id: str) -> str:
    """Mock function to read an email by its ID."""
    return f"Email content for ID: {email_id}"

def your_send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Mock function to send an email."""
    return f"Email sent to {recipient} with subject '{subject}'"

agent = create_agent(
    model="gpt-5.5",
    tools=[your_read_email_tool, your_send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "your_read_email_tool": False,
            }
        ),
    ],
)
```

For complete examples, configuration options, and integration patterns, see the [Human-in-the-loop documentation](/oss/python/langchain/human-in-the-loop).

Watch this [video guide](https://www.youtube.com/watch?v=SpfT6-YAVPk) demonstrating Human-in-the-loop middleware behavior.

### Model call limit

Limit the number of model calls to prevent infinite loops or excessive costs. Model call limit is useful for the following:

- Preventing runaway agents from making too many API calls.
- Enforcing cost controls on production deployments.
- Testing agent behavior within specific call budgets.

**API reference:** [`ModelCallLimitMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/model_call_limit/ModelCallLimitMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-5.5",
    checkpointer=InMemorySaver(),  # Required for thread limiting
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior="end",
        ),
    ],
)
```

Watch this [video guide](https://www.youtube.com/watch?v=nJEER0uaNkE) demonstrating Model Call Limit middleware behavior.

Configuration options

[​](#param-thread-limit)

number

Maximum model calls across all runs in a thread. Defaults to no limit.

[​](#param-run-limit)

number

Maximum model calls per single invocation. Defaults to no limit.

[​](#param-exit-behavior)

string

default:"end"

Behavior when limit is reached. Options: `` (graceful termination) or `` (raise exception)

### Tool call limit

Control agent execution by limiting the number of tool calls, either globally across all tools or for specific tools. Tool call limits are useful for the following:

- Preventing excessive calls to expensive external APIs.
- Limiting web searches or database queries.
- Enforcing rate limits on specific tool usage.
- Protecting against runaway agent loops.

**API reference:** [`ToolCallLimitMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/tool_call_limit/ToolCallLimitMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        # Global limit
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),
        # Tool-specific limit
        ToolCallLimitMiddleware(
            tool_name="search",
            thread_limit=5,
            run_limit=3,
        ),
    ],
)
```

Watch this [video guide](https://www.youtube.com/watch?v=6gYlaJJ8t0w) demonstrating Tool Call Limit middleware behavior.

Configuration options

[​](#param-tool-name)

string

Name of specific tool to limit. If not provided, limits apply to **all tools globally**.

[​](#param-thread-limit-1)

number

Maximum tool calls across all runs in a thread (conversation). Persists across multiple invocations with the same thread ID. Requires a checkpointer to maintain state. `` means no thread limit.

[​](#param-run-limit-1)

number

Maximum tool calls per single invocation (one user message → response cycle). Resets with each new user message. `` means no run limit.**Note:** At least one of `` or `` must be specified.

[​](#param-exit-behavior-1)

string

default:"continue"

Behavior when limit is reached:

- `'continue'` (default) - Block exceeded tool calls with error messages, let other tools and the model continue. The model decides when to end based on the error messages.
- `'error'` - Raise a `ToolCallLimitExceededError` exception, stopping execution immediately
- `'end'` - Stop execution immediately with a `ToolMessage` and AI message for the exceeded tool call. Only works when limiting a single tool; raises `NotImplementedError` if other tools have pending calls.

Full example

Specify limits with:

- **Thread limit** - Max calls across all runs in a conversation (requires checkpointer)
- **Run limit** - Max calls per single invocation (resets each turn)

Exit behaviors:

- `'continue'` (default) - Block exceeded calls with error messages, agent continues
- `'error'` - Raise exception immediately
- `'end'` - Stop with ToolMessage + AI message (single-tool scenarios only)

### PII detection

Detect and handle Personally Identifiable Information (PII) in conversations using configurable strategies. PII detection is useful for the following:

- Healthcare and financial applications with compliance requirements.
- Customer service agents that need to sanitize logs.
- Any application handling sensitive user data.

With `apply_to_output=True`, `PIIMiddleware` also redacts streamed wire output—text deltas, tool-call args, tool outputs, and state snapshots—via a registered stream transformer. Requires `langchain>=1.3.2`. See [Register transformers on middleware](/oss/python/langchain/event-streaming#register-transformers-on-middleware).

**API reference:** [`PIIMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/pii/PIIMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

#### Custom PII types

You can create custom PII types by providing a `detector` parameter. This allows you to detect patterns specific to your use case beyond the built-in types.

**Three ways to create custom detectors:**

1. **Regex pattern string** - Simple pattern matching
2. **Custom function** - Complex detection logic with validation

```
import re

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMatch, PIIMiddleware

# Method 1: Regex pattern string
agent1 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
        ),
    ],
)

# Method 2: Compiled regex pattern
agent2 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "phone_number",
            detector=re.compile(r"\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}"),
            strategy="mask",
        ),
    ],
)

# Method 3: Custom detector function
def detect_ssn(content: str) -> list[PIIMatch]:
    """Detect SSNs with validation."""
    matches: list[PIIMatch] = []
    pattern = r"\d{3}-\d{2}-\d{4}"
    for match in re.finditer(pattern, content):
        ssn = match.group(0)
        # Validate: first 3 digits shouldn't be 000, 666, or 900-999
        first_three = int(ssn[:3])
        if first_three not in [0, 666] and not (900 <= first_three <= 999):
            matches.append({
                "type": "ssn",
                "value": ssn,
                "start": match.start(),
                "end": match.end(),
            })
    return matches

agent3 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "ssn",
            detector=detect_ssn,
            strategy="hash",
        ),
    ],
)
```

**Custom detector function signature:**

The detector function must accept a string (content) and return matches:

Returns a list of `PIIMatch` objects:

```
from langchain.agents.middleware import PIIMatch

def detector(content: str) -> list[PIIMatch]:
    return [
        {
            "type": "custom_type",
            "value": "matched_text",
            "start": 0,
            "end": 12,
        },
        # ... more matches
    ]
```

For custom detectors:

- Use regex strings for simple patterns
- Use RegExp objects when you need flags (e.g., case-insensitive matching)
- Use custom functions when you need validation logic beyond pattern matching
- Custom functions give you full control over detection logic and can implement complex validation rules

Configuration options

[​](#param-pii-type)

string

required

Type of PII to detect. Can be a built-in type (``, ``, ``, ``, ``) or a custom type name.

[​](#param-strategy)

string

default:"redact"

How to handle detected PII. Options:

- `'block'` - Raise exception when detected
- `'redact'` - Replace with `[REDACTED_{PII_TYPE}]`
- `'mask'` - Partially mask (e.g., `****-****-****-1234`)
- `'hash'` - Replace with deterministic hash

[​](#param-detector)

function | regex

Custom detector function or regex pattern. If not provided, uses built-in detector for the PII type.

[​](#param-apply-to-input)

boolean

default:"True"

Check user messages before model call

[​](#param-apply-to-output)

boolean

default:"False"

Check AI messages after model call. With ``, also redacts streamed wire output (text deltas, tool-call args, tool outputs, state snapshots) via a registered stream transformer. See [event streaming](/oss/python/langchain/event-streaming#register-transformers-on-middleware).

[​](#param-apply-to-tool-results)

boolean

default:"False"

Check tool result messages after execution

### To-do list

Equip agents with task planning and tracking capabilities for complex multi-step tasks. To-do lists are useful for the following:

- Complex multi-step tasks requiring coordination across multiple tools.
- Long-running operations where progress visibility is important.

This middleware automatically provides agents with a `write_todos` tool and system prompts to guide effective task planning.

**API reference:** [`TodoListMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/todo/TodoListMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[read_file, write_file, run_tests],
    middleware=[TodoListMiddleware()],
)
```

Watch this [video guide](https://www.youtube.com/watch?v=yTWocbVKQxw) demonstrating To-do List middleware behavior.

Configuration options

[​](#param-system-prompt)

string

Custom system prompt for guiding todo usage. Uses built-in prompt if not specified.

[​](#param-tool-description)

string

Custom description for the `` tool. Uses built-in description if not specified.

### LLM tool selector

Use an LLM to intelligently select relevant tools before calling the main model. LLM tool selectors are useful for the following:

- Agents with many tools (10+) where most aren’t relevant per query.
- Reducing token usage by filtering irrelevant tools.
- Improving model focus and accuracy.

This middleware uses structured output to ask an LLM which tools are most relevant for the current query. The structured output schema defines the available tool names and descriptions. Model providers often add this structured output information to the system prompt behind the scenes.

**API reference:** [`LLMToolSelectorMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/tool_selection/LLMToolSelectorMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[tool1, tool2, tool3, tool4, tool5, ...],
    middleware=[
        LLMToolSelectorMiddleware(
            model="gpt-5.4-mini",
            max_tools=3,
            always_include=["search"],
        ),
    ],
)
```

Configuration options

[​](#param-model-1)

string | BaseChatModel

Model for tool selection. Can be a model identifier string (e.g., ``) or a `` instance. See [``](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model) for more information.Defaults to the agent’s main model.

[​](#param-system-prompt-1)

string

Instructions for the selection model. Uses built-in prompt if not specified.

[​](#param-max-tools)

number

Maximum number of tools to select. If the model selects more, only the first max_tools will be used. No limit if not specified.

[​](#param-always-include)

list[string]

Tool names to always include regardless of selection. These do not count against the max_tools limit.

### Provider tool search

Defer selected tools behind model providers’ server-side tool search, so the model discovers them on demand instead of receiving every tool schema up front. Provider tool search is useful for:

- Reducing context bloat when using many tools.
- Improving tool selection accuracy by surfacing only relevant tools.

Requires a model with server-side tool search support: Anthropic (Claude Sonnet 4+/Opus 4+/Haiku 4.5+) or OpenAI (gpt-5.5+). Other providers raise a `ValueError`.

**API reference:** [`ProviderToolSearchMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/provider_tool_search/ProviderToolSearchMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware

agent = create_agent(
    model="anthropic:claude-opus-4-8",
    tools=[get_weather, lookup_order],
    middleware=[
        ProviderToolSearchMiddleware(searchable_tools=["lookup_order"]),
    ],
)
```

Configuration options

[​](#param-searchable-tools)

list[str | BaseTool]

Tools to defer behind the provider’s tool search, given by name or instance. Deferred tools are withheld from the model until its search surfaces them. Tools constructed with `` are deferred regardless of this option; if `` is omitted, only those pre-marked tools are deferred.

Full example

The middleware opts-in all tools included in `` for deferral and search. A tool can also opt into deferral at construction time by setting ``.

### Shell tool

Expose a persistent shell session to agents for command execution. Shell tool middleware is useful for the following:

- Agents that need to execute system commands
- Development and deployment automation tasks
- Testing and validation workflows
- File system operations and script execution

**Security consideration**: Use appropriate execution policies (`HostExecutionPolicy`, `DockerExecutionPolicy`, or `CodexSandboxExecutionPolicy`) to match your deployment’s security requirements.

**Limitation**: Persistent shell sessions do not currently work with interrupts (human-in-the-loop). We anticipate adding support for this in the future.

**API reference:** [`ShellToolMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/shell_tool/ShellToolMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
)

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ],
)
```

Configuration options

[​](#param-workspace-root)

str | Path | None

Base directory for the shell session. If omitted, a temporary directory is created when the agent starts and removed when it ends.

[​](#param-startup-commands)

tuple[str, ...] | list[str] | str | None

Optional commands executed sequentially after the session starts

[​](#param-shutdown-commands)

tuple[str, ...] | list[str] | str | None

Optional commands executed before the session shuts down

[​](#param-execution-policy)

BaseExecutionPolicy | None

Execution policy controlling timeouts, output limits, and resource configuration. Options:

- `HostExecutionPolicy` - Full host access (default); best for trusted environments where the agent already runs inside a container or VM
- `DockerExecutionPolicy` - Launches a separate Docker container for each agent run, providing harder isolation
- `CodexSandboxExecutionPolicy` - Reuses the Codex CLI sandbox for additional syscall/filesystem restrictions

[​](#param-redaction-rules)

tuple[RedactionRule, ...] | list[RedactionRule] | None

Optional redaction rules to sanitize command output before returning it to the model.

Redaction rules are applied post execution and do not prevent exfiltration of secrets or sensitive data when using ``.

[​](#param-tool-description-1)

str | None

Optional override for the registered shell tool description

[​](#param-shell-command)

Sequence[str] | str | None

Optional shell executable (string) or argument sequence used to launch the persistent session. Defaults to ``.

[​](#param-env)

Mapping[str, Any] | None

Optional environment variables to supply to the shell session. Values are coerced to strings before command execution.

Full example

The middleware provides a single persistent shell session that agents can use to execute commands sequentially.

**Execution policies:**

- `HostExecutionPolicy` (default) - Native execution with full host access
- `DockerExecutionPolicy` - Isolated Docker container execution
- `CodexSandboxExecutionPolicy` - Sandboxed execution via Codex CLI

### Filesystem middleware

Context engineering is a main challenge in building effective agents. This is particularly difficult when using tools that return variable-length results (for example, `web_search` and RAG), as long tool results can quickly fill your context window.

`FilesystemMiddleware` from [Deep Agents](/oss/python/deepagents/overview) provides four tools for interacting with both short-term and long-term memory:

- `ls`: List the files in the filesystem
- `read_file`: Read an entire file or a certain number of lines from a file
- `write_file`: Write a new file to the filesystem
- `edit_file`: Edit an existing file in the filesystem

```
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

# FilesystemMiddleware is included by default in create_deep_agent
# You can customize it if building a custom agent
agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        FilesystemMiddleware(
            backend=None,  # Optional: custom backend (defaults to StateBackend)
            system_prompt="Write to the filesystem when...",  # Optional custom addition to the system prompt
            custom_tool_descriptions={
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            },  # Optional: Custom descriptions for filesystem tools
            tools=["read_file", "ls", "glob", "grep"],  # Optional: Allowlist restricting which filesystem tools are exposed
        ),
    ],
)
```

#### Short-term vs. long-term filesystem

By default, these tools write to a local “filesystem” in your graph state. To enable persistent storage across threads, configure a `CompositeBackend` that routes specific paths (like `/memories/`) to a `StoreBackend`.

```
from langchain.agents import create_agent
from deepagents.middleware import FilesystemMiddleware
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_agent(
    model="claude-sonnet-4-6",
    store=store,
    middleware=[
        FilesystemMiddleware(
            backend=CompositeBackend(
                default=StateBackend(),
                routes={"/memories/": StoreBackend()}
            ),
            custom_tool_descriptions={
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            }  # Optional: Custom descriptions for filesystem tools
        ),
    ],
)
```

When you configure a `CompositeBackend` with a `StoreBackend` for `/memories/`, any files prefixed with **/memories/** are saved to persistent storage and survive across different threads. Files without this prefix remain in ephemeral state storage.

### Subagent

Handing off tasks to subagents isolates context, keeping the main (supervisor) agent’s context window clean while still going deep on a task.

The subagents middleware from [Deep Agents](/oss/python/deepagents/overview) allows you to supply subagents through a `task` tool.

```
from langchain.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-6",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": "Use the get_weather tool to get the weather in a city.",
                    "tools": [get_weather],
                    "model": "gpt-5.5",
                    "middleware": [],
                }
            ],
        )
    ],
)
```

A subagent is defined with a **name**, **description**, **system prompt**, and **tools**. You can also provide a subagent with a custom **model**, or with additional **middleware**. This can be particularly useful when you want to give the subagent an additional state key to share with the main agent.

For more complex use cases, you can also provide your own prebuilt LangGraph graph as a subagent.

```
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import CompiledSubAgent
from langgraph.graph import StateGraph

# Create a custom LangGraph graph
def create_weather_graph():
    workflow = StateGraph(...)
    # Build your custom graph
    return workflow.compile()

weather_graph = create_weather_graph()

# Wrap it in a CompiledSubAgent
weather_subagent = CompiledSubAgent(
    name="weather",
    description="This subagent can get weather in cities.",
    runnable=weather_graph
)

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-6",
            default_tools=[],
            subagents=[weather_subagent],
        )
    ],
)
```

In addition to any user-defined subagents, the main agent has access to a `general-purpose` subagent at all times. This subagent has the same instructions as the main agent and all the tools it has access to. The primary purpose of the `general-purpose` subagent is context isolation—the main agent can delegate a complex task to this subagent and get a concise answer back without bloat from intermediate tool calls.

### Rubric grading

`RubricMiddleware` requires `deepagents>=0.6.5`. It is in [**beta**](/oss/python/versioning); the API may change in the future.

Some tasks have a clear definition of “done” that an agent cannot reliably hit on the first try. `RubricMiddleware` lets you declare *what done looks like* as a rubric and have the agent self-evaluate and iterate until the rubric is satisfied or a maximum iteration cap is hit.

**API reference:** [`RubricMiddleware`](https://reference.langchain.com/python/deepagents/middleware/rubric/RubricMiddleware)

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

For full configuration options, streaming events, and a complete code generation example, see [Grading rubrics](/oss/python/deepagents/rubric).

### File search

Provide Glob and Grep search tools over a filesystem. File search middleware is useful for the following:

- Code exploration and analysis
- Finding files by name patterns
- Searching code content with regex
- Large codebases where file discovery is needed

**API reference:** [`FilesystemFileSearchMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/file_search/FilesystemFileSearchMiddleware)

```
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path="/workspace",
            use_ripgrep=True,
        ),
    ],
)
```

Configuration options

[​](#param-root-path)

str

required

Root directory to search. All file operations are relative to this path.

[​](#param-use-ripgrep)

bool

default:"True"

Whether to use ripgrep for search. Falls back to Python regex if ripgrep is unavailable.

[​](#param-max-file-size-mb)

int

default:"10"

Maximum file size to search in MB. Files larger than this are skipped.

Full example

The middleware adds two search tools to agents:

**Glob tool** - Fast file pattern matching:

- Supports patterns like `**/*.py`, `src/**/*.ts`
- Returns matching file paths sorted by modification time

**Grep tool** - Content search with regex:

- Full regex syntax support
- Filter by file patterns with `include` parameter
- Three output modes: `files_with_matches`, `content`, `count`

### Context editing

Manage conversation context by clearing older tool call outputs when token limits are reached, while preserving recent results. This helps keep context windows manageable in long conversations with many tool calls. Context editing is useful for the following:

- Long conversations with many tool calls that exceed token limits
- Reducing token costs by removing older tool outputs that are no longer relevant
- Maintaining only the most recent N tool results in context

**API reference:** [`ContextEditingMiddleware`](https://reference.langchain.com/python/langchain/agents/middleware/context_editing/ContextEditingMiddleware), [`ClearToolUsesEdit`](https://reference.langchain.com/python/langchain/agents/middleware/context_editing/ClearToolUsesEdit)

```
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100000,
                    keep=3,
                ),
            ],
        ),
    ],
)
```

Configuration options

[​](#param-edits)

list[ContextEdit]

default:"[ClearToolUsesEdit()]"

List of [``](https://reference.langchain.com/python/langchain/agents/middleware/context_editing/ContextEdit) strategies to apply

[​](#param-token-count-method)

string

default:"approximate"

Token counting method. Options: `` or ``

**[``](https://reference.langchain.com/python/langchain/agents/middleware/context_editing/ClearToolUsesEdit) options:**

[​](#param-trigger-1)

number

default:"100000"

Token count that triggers the edit. When the conversation exceeds this token count, older tool outputs will be cleared.

[​](#param-clear-at-least)

number

default:"0"

Minimum number of tokens to reclaim when the edit runs. If set to 0, clears as much as needed.

[​](#param-keep-1)

number

default:"3"

Number of most recent tool results that must be preserved. These will never be cleared.

[​](#param-clear-tool-inputs)

boolean

default:"False"

Whether to clear the originating tool call parameters on the AI message. When ``, tool call arguments are replaced with empty objects.

[​](#param-exclude-tools)

list[string]

default:"()"

List of tool names to exclude from clearing. These tools will never have their outputs cleared.

[​](#param-placeholder)

string

default:"[cleared]"

Placeholder text inserted for cleared tool outputs. This replaces the original tool message content.

Full example

The middleware applies context editing strategies when token limits are reached. The most common strategy is ``, which clears older tool results while preserving recent ones.

**How it works:**

1. Monitor token count in conversation
2. When threshold is reached, clear older tool outputs
3. Keep most recent N tool results
4. Optionally preserve tool call arguments for context

### LLM tool emulator

Emulate tool execution using an LLM for testing purposes, replacing actual tool calls with AI-generated responses. LLM tool emulators are useful for the following:

- Testing agent behavior without executing real tools.
- Developing agents when external tools are unavailable or expensive.
- Prototyping agent workflows before implementing actual tools.

**API reference:** [`LLMToolEmulator`](https://reference.langchain.com/python/langchain/agents/middleware/tool_emulator/LLMToolEmulator)

```
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model="gpt-5.5",
    tools=[get_weather, search_database, send_email],
    middleware=[
        LLMToolEmulator(),  # Emulate all tools
    ],
)
```

Configuration options

[​](#param-tools-2)

list[str | BaseTool]

List of tool names (str) or BaseTool instances to emulate. If `` (default), ALL tools will be emulated. If empty list ``, no tools will be emulated. If array with tool names/instances, only those tools will be emulated.

[​](#param-model-2)

string | BaseChatModel

Model to use for generating emulated tool responses. Can be a model identifier string (e.g., ``) or a `` instance. Defaults to the agent’s model if not specified. See [``](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model) for more information.

Full example

The middleware uses an LLM to generate plausible responses for tool calls instead of executing the actual tools.

## Provider-specific middleware

These middleware are optimized for specific LLM providers. See each provider’s documentation for full details and examples.

[AnthropicPrompt caching, bash tool, text editor, memory, and file search middleware for Claude models.](/oss/python/integrations/middleware/anthropic)

[AWSPrompt caching middleware for Amazon Bedrock models.](/oss/python/integrations/middleware/aws)

[OpenAIContent moderation middleware for OpenAI models.](/oss/python/integrations/middleware/openai)

---

[Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.

[Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/middleware/built-in.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).

Was this page helpful?

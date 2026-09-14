# LangChain + LangGraph — API / Symbol Reference

Auto-extracted from every code block in the crawled docs. Use this to find *which page* documents a symbol, then read that page.

## Canonical imports

| Import | Documented in |
| --- | --- |
| `from langchain.agents import create_agent` | `langchain/agents.md`, `langchain/context-engineering.md`, `langchain/deep-agent-from-scratch.md`, `langchain/event-streaming.md`, `langchain/frontend__integrations__copilotkit.md` …(+35) |
| `from langchain.tools import tool` | `langchain/agents.md`, `langchain/context-engineering.md`, `langchain/frontend__headless-tools.md`, `langchain/long-term-memory.md`, `langchain/middleware__built-in.md` …(+21) |
| `from langgraph.checkpoint.memory import InMemorySaver` | `langchain/agents.md`, `langchain/guardrails.md`, `langchain/human-in-the-loop.md`, `langchain/mcp__tools.md`, `langchain/middleware__built-in.md` …(+21) |
| `from langgraph.graph import StateGraph` | `langchain/middleware__built-in.md`, `langchain/middleware__overview.md`, `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/add-memory.md` …(+20) |
| `from langgraph.types import Command` | `langchain/context-engineering.md`, `langchain/guardrails.md`, `langchain/human-in-the-loop.md`, `langchain/mcp__tools.md`, `langchain/middleware__custom.md` …(+20) |
| `from langgraph.graph import START` | `langchain/middleware__overview.md`, `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/add-memory.md`, `langgraph/agentic-rag.md` …(+15) |
| `from langchain.chat_models import init_chat_model` | `langchain/context-engineering.md`, `langchain/event-streaming.md`, `langchain/guardrails.md`, `langchain/messages.md`, `langchain/middleware__custom.md` …(+14) |
| `from langgraph.graph import END` | `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/agentic-rag.md`, `langgraph/backward-compatibility.md`, `langgraph/checkpointers.md` …(+11) |
| `from langchain.messages import HumanMessage` | `langchain/agents.md`, `langchain/messages.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md` …(+9) |
| `from langchain.messages import AIMessage` | `langchain/agents.md`, `langchain/guardrails.md`, `langchain/messages.md`, `langchain/middleware__custom.md`, `langchain/models.md` …(+8) |
| `from langchain.tools import ToolRuntime` | `langchain/context-engineering.md`, `langchain/frontend__headless-tools.md`, `langchain/long-term-memory.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__handoffs.md` …(+7) |
| `from langchain_anthropic import ChatAnthropic` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+7) |
| `from langchain_openai import ChatOpenAI` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+6) |
| `from langchain.messages import ToolMessage` | `langchain/messages.md`, `langchain/middleware__custom.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__handoffs.md`, `langchain/short-term-memory.md` …(+5) |
| `from langgraph.graph import MessagesState` | `langgraph/add-memory.md`, `langgraph/agentic-rag.md`, `langgraph/frontend__overview.md`, `langgraph/graph-api.md`, `langgraph/observability.md` …(+5) |
| `from langgraph.runtime import Runtime` | `langchain/guardrails.md`, `langchain/middleware__custom.md`, `langchain/runtime.md`, `langchain/short-term-memory.md`, `langchain/streaming.md` …(+5) |
| `from langchain.agents.middleware import HumanInTheLoopMiddleware` | `langchain/agents.md`, `langchain/guardrails.md`, `langchain/human-in-the-loop.md`, `langchain/mcp__tools.md`, `langchain/middleware__built-in.md` …(+4) |
| `from langchain.agents.middleware import ModelRequest` | `langchain/context-engineering.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__skills-sql-assistant.md` …(+3) |
| `from langchain_aws import ChatBedrock` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langchain_core.utils.uuid import uuid7` | `langchain/agents.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/streaming.md`, `langchain/tools.md` …(+3) |
| `from langchain_google_genai import ChatGoogleGenerativeAI` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langchain_huggingface import ChatHuggingFace` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langchain_huggingface import HuggingFaceEndpoint` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langchain_openai import AzureChatOpenAI` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langchain_openrouter import ChatOpenRouter` | `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `from langgraph.types import interrupt` | `langchain/frontend__headless-tools.md`, `langgraph/functional-api.md`, `langgraph/graph-api.md`, `langgraph/interrupts.md`, `langgraph/sql-agent.md` …(+3) |
| `from langchain.agents import AgentState` | `langchain/agents.md`, `langchain/middleware__overview.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__subagents.md`, `langchain/runtime.md` …(+2) |
| `from langgraph.checkpoint.memory import MemorySaver` | `langchain/frontend__headless-tools.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/frontend__overview.md`, `langgraph/streaming.md`, `langgraph/test.md` …(+2) |
| `from langgraph.func import entrypoint` | `langgraph/choosing-apis.md`, `langgraph/fault-tolerance.md`, `langgraph/functional-api.md`, `langgraph/pregel.md`, `langgraph/quickstart.md` …(+2) |
| `from langgraph.func import task` | `langgraph/choosing-apis.md`, `langgraph/fault-tolerance.md`, `langgraph/functional-api.md`, `langgraph/graph-api.md`, `langgraph/quickstart.md` …(+2) |
| `from langgraph.store.memory import InMemoryStore` | `langchain/context-engineering.md`, `langchain/long-term-memory.md`, `langchain/middleware__built-in.md`, `langchain/tools.md`, `langgraph/add-memory.md` …(+2) |
| `from langchain.agents.middleware import ModelResponse` | `langchain/context-engineering.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__skills-sql-assistant.md` …(+1) |
| `from langchain.agents.middleware import wrap_model_call` | `langchain/context-engineering.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md` …(+1) |
| `from langchain.messages import SystemMessage` | `langchain/messages.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langgraph/quickstart.md` …(+1) |
| `from langgraph.types import Send` | `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__router.md`, `langgraph/fault-tolerance.md`, `langgraph/graph-api.md`, `langgraph/use-graph-api.md` …(+1) |
| `from langchain.agents.middleware import AgentMiddleware` | `langchain/event-streaming.md`, `langchain/guardrails.md`, `langchain/middleware__custom.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/tools.md` |
| `from langchain.agents.middleware import SummarizationMiddleware` | `langchain/context-engineering.md`, `langchain/middleware__built-in.md`, `langchain/middleware__overview.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/short-term-memory.md` |
| `from langchain.mcp import MCPAdapter` | `langchain/mcp.md`, `langchain/mcp__auth.md`, `langchain/mcp__connections.md`, `langchain/mcp__tools.md`, `langchain/tools.md` |
| `from langchain.messages import AnyMessage` | `langchain/runtime.md`, `langchain/streaming.md`, `langgraph/graph-api.md`, `langgraph/quickstart.md`, `langgraph/use-graph-api.md` |
| `from langchain_core.runnables import RunnableConfig` | `langchain/short-term-memory.md`, `langgraph/checkpointers.md`, `langgraph/fault-tolerance.md`, `langgraph/graph-api.md`, `langgraph/sql-agent.md` |
| `from langchain.agents.middleware import PIIMiddleware` | `langchain/agents.md`, `langchain/event-streaming.md`, `langchain/guardrails.md`, `langchain/middleware__built-in.md` |
| `from langgraph.checkpoint.postgres import PostgresSaver` | `langchain/short-term-memory.md`, `langgraph/add-memory.md`, `langgraph/checkpointers.md`, `langgraph/persistence.md` |
| `from langgraph.types import RetryPolicy` | `langgraph/fault-tolerance.md`, `langgraph/thinking-in-langgraph.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `from langchain.agents.middleware import AgentState` | `langchain/guardrails.md`, `langchain/middleware__custom.md`, `langchain/streaming.md` |
| `from langchain.agents.middleware import TodoListMiddleware` | `langchain/agents.md`, `langchain/deep-agent-from-scratch.md`, `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import after_model` | `langchain/middleware__custom.md`, `langchain/runtime.md`, `langchain/short-term-memory.md` |
| `from langchain.agents.middleware import before_model` | `langchain/middleware__custom.md`, `langchain/runtime.md`, `langchain/short-term-memory.md` |
| `from langchain.agents.middleware import dynamic_prompt` | `langchain/context-engineering.md`, `langchain/runtime.md`, `langchain/short-term-memory.md` |
| `from langchain.tools.tool_node import ToolCallRequest` | `langchain/mcp__tools.md`, `langchain/middleware__custom.md`, `langchain/tools.md` |
| `from langgraph.cache.memory import InMemoryCache` | `langgraph/graph-api.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `from langgraph.config import get_stream_writer` | `langchain/streaming.md`, `langgraph/event-streaming.md`, `langgraph/streaming.md` |
| `from langgraph.errors import NodeError` | `langgraph/fault-tolerance.md`, `langgraph/thinking-in-langgraph.md`, `langgraph/use-graph-api.md` |
| `from langgraph.graph import add_messages` | `langgraph/quickstart.md`, `langgraph/use-functional-api.md`, `langgraph/workflows-agents.md` |
| `from langgraph.graph.message import add_messages` | `langgraph/graph-api.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `from langgraph.prebuilt import ToolNode` | `langgraph/agentic-rag.md`, `langgraph/sql-agent.md`, `langgraph/workflows-agents.md` |
| `from langgraph.types import CachePolicy` | `langgraph/graph-api.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `from langchain import create_agent` | `langchain/frontend__headless-tools.md`, `langchain/frontend__overview.md` |
| `from langchain.agents.middleware import ModelRetryMiddleware` | `langchain/agents.md`, `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ToolCallLimitMiddleware` | `langchain/middleware__built-in.md`, `langgraph/use-subgraphs.md` |
| `from langchain.agents.middleware import ToolCallRequest` | `langchain/human-in-the-loop.md`, `langchain/tools.md` |
| `from langchain.agents.middleware import ToolRetryMiddleware` | `langchain/agents.md`, `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import after_agent` | `langchain/guardrails.md`, `langchain/streaming.md` |
| `from langchain.agents.middleware import before_agent` | `langchain/frontend__integrations__copilotkit.md`, `langchain/guardrails.md` |
| `from langchain.agents.middleware import hook_config` | `langchain/guardrails.md`, `langchain/middleware__custom.md` |
| `from langchain.agents.middleware import wrap_tool_call` | `langchain/middleware__custom.md`, `langchain/tools.md` |
| `from langchain.agents.structured_output import ProviderStrategy` | `langchain/frontend__integrations__copilotkit.md`, `langchain/structured-output.md` |
| `from langchain.embeddings import init_embeddings` | `langgraph/add-memory.md`, `langgraph/stores.md` |
| `from langchain.messages import RemoveMessage` | `langchain/short-term-memory.md`, `langgraph/add-memory.md` |
| `from langchain_core.documents import Document` | `langchain/knowledge-base.md`, `langgraph/agentic-rag.md` |
| `from langchain_core.messages import BaseMessage` | `langgraph/quickstart.md`, `langgraph/workflows-agents.md` |
| `from langchain_core.runnables import Runnable` | `langchain/long-term-memory.md`, `langchain/streaming.md` |
| `from langchain_core.vectorstores import InMemoryVectorStore` | `langchain/knowledge-base.md`, `langgraph/agentic-rag.md` |
| `from langchain_openai import OpenAIEmbeddings` | `langchain/knowledge-base.md`, `langgraph/agentic-rag.md` |
| `from langchain_text_splitters import RecursiveCharacterTextSplitter` | `langchain/knowledge-base.md`, `langgraph/agentic-rag.md` |
| `from langgraph.errors import GraphRecursionError` | `langgraph/graph-api.md`, `langgraph/use-graph-api.md` |
| `from langgraph.errors import NodeTimeoutError` | `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `from langgraph.graph.message import REMOVE_ALL_MESSAGES` | `langchain/short-term-memory.md`, `langgraph/add-memory.md` |
| `from langgraph.store.postgres import PostgresStore` | `langchain/long-term-memory.md`, `langgraph/add-memory.md` |
| `from langgraph.stream import ProtocolEvent` | `langgraph/event-streaming.md`, `langgraph/frontend__custom-stream-channels.md` |
| `from langgraph.stream import StreamChannel` | `langgraph/event-streaming.md`, `langgraph/frontend__custom-stream-channels.md` |
| `from langgraph.stream import StreamTransformer` | `langgraph/event-streaming.md`, `langgraph/frontend__custom-stream-channels.md` |
| `from langgraph.types import Overwrite` | `langgraph/graph-api.md`, `langgraph/use-graph-api.md` |
| `from langgraph.types import TimeoutPolicy` | `langgraph/fault-tolerance.md`, `langgraph/use-graph-api.md` |
| `from langgraph_sdk import #` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langgraph_sdk import async` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langgraph_sdk import for` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langgraph_sdk import get_client` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langgraph_sdk import get_sync_client` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langgraph_sdk import or` | `langchain/deploy.md`, `langgraph/deploy.md` |
| `from langchain.agents.middleware import ClearToolUsesEdit` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ContextEditingMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import FilesystemFileSearchMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import LLMToolEmulator` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import LLMToolSelectorMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ModelCallLimitMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ModelFallbackMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import PIIMatch` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ProviderToolSearchMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import ToolErrorMiddleware` | `langchain/middleware__built-in.md` |
| `from langchain.agents.middleware import TracePolicy` | `langchain/middleware__custom.md` |
| `from langchain.agents.middleware import configure_trace_policy` | `langchain/middleware__custom.md` |
| `from langchain.agents.middleware import omit_payload` | `langchain/middleware__custom.md` |
| `from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig` | `langchain/mcp__tools.md` |
| `from langchain.agents.structured_output import MultipleStructuredOutputsError` | `langchain/structured-output.md` |
| `from langchain.agents.structured_output import StructuredOutputValidationError` | `langchain/structured-output.md` |
| `from langchain.agents.structured_output import ToolStrategy` | `langchain/structured-output.md` |
| `from langchain.messages import AIMessageChunk` | `langchain/streaming.md` |
| `from langchain.messages import BaseMessage` | `langgraph/use-functional-api.md` |
| `from langchain.messages import ToolCall` | `langchain/test__unit-testing.md` |
| `from langchain.tools import BaseTool` | `langchain/mcp__tools.md` |
| `from langchain.tools import InjectedToolCallId` | `langchain/multi-agent__subagents.md` |
| `from langchain_astradb import AstraDBVectorStore` | `langchain/knowledge-base.md` |
| `from langchain_aws import BedrockEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_chroma import Chroma` | `langchain/knowledge-base.md` |
| `from langchain_cohere import CohereEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_core.callbacks import UsageMetadataCallbackHandler` | `langchain/models.md` |
| `from langchain_core.callbacks import get_usage_metadata_callback` | `langchain/models.md` |
| `from langchain_core.embeddings import DeterministicFakeEmbedding` | `langchain/knowledge-base.md` |
| `from langchain_core.exceptions import ModelTimeoutError` | `langchain/models.md` |
| `from langchain_core.language_models.fake_chat_models import GenericFakeChatModel` | `langchain/test__unit-testing.md` |
| `from langchain_core.load import dumpd` | `langchain/messages.md` |
| `from langchain_core.load import load` | `langchain/messages.md` |
| `from langchain_core.messages import convert_to_messages` | `langgraph/agentic-rag.md` |
| `from langchain_core.runnables import RunnableGenerator` | `langchain/voice-agent.md` |
| `from langchain_core.runnables import chain` | `langchain/knowledge-base.md` |
| `from langchain_core.runnables.graph import CurveStyle` | `langgraph/use-graph-api.md` |
| `from langchain_core.runnables.graph import MermaidDrawMethod` | `langgraph/use-graph-api.md` |
| `from langchain_core.runnables.graph import NodeStyles` | `langgraph/use-graph-api.md` |
| `from langchain_core.tracers.langchain import LangChainTracer` | `langgraph/observability.md` |
| `from langchain_google_genai import GoogleGenerativeAIEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_google_vertexai import VertexAIEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_huggingface import HuggingFaceEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_ibm import WatsonxEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_isaacus import IsaacusEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_milvus import Milvus` | `langchain/knowledge-base.md` |
| `from langchain_mistralai import MistralAIEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_mongodb import MongoDBAtlasVectorSearch` | `langchain/knowledge-base.md` |
| `from langchain_nomic import NomicEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_ollama import OllamaEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_openai import AzureOpenAIEmbeddings` | `langchain/knowledge-base.md` |
| `from langchain_pinecone import PineconeVectorStore` | `langchain/knowledge-base.md` |
| `from langchain_postgres import PGEngine` | `langchain/knowledge-base.md` |
| `from langchain_postgres import PGVector` | `langchain/knowledge-base.md` |
| `from langchain_postgres import PGVectorStore` | `langchain/knowledge-base.md` |
| `from langchain_qdrant import QdrantVectorStore` | `langchain/knowledge-base.md` |
| `from langgraph.channels import BinaryOperatorAggregate` | `langgraph/pregel.md` |
| `from langgraph.channels import DeltaChannel` | `langgraph/pregel.md` |
| `from langgraph.channels import EphemeralValue` | `langgraph/pregel.md` |
| `from langgraph.channels import LastValue` | `langgraph/pregel.md` |
| `from langgraph.channels import Topic` | `langgraph/pregel.md` |
| `from langgraph.checkpoint.conformance import checkpointer_test` | `langgraph/checkpointers.md` |
| `from langgraph.checkpoint.conformance import validate` | `langgraph/checkpointers.md` |
| `from langgraph.checkpoint.serde.encrypted import EncryptedSerializer` | `langgraph/checkpointers.md` |
| `from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer` | `langgraph/checkpointers.md` |
| `from langgraph.checkpoint.sqlite import SqliteSaver` | `langgraph/checkpointers.md` |
| `from langgraph.constants import START` | `langgraph/pregel.md` |
| `from langgraph.errors import GraphDrained` | `langgraph/fault-tolerance.md` |
| `from langgraph.graph.state import START` | `langgraph/use-subgraphs.md` |
| `from langgraph.graph.state import StateGraph` | `langgraph/use-subgraphs.md` |
| `from langgraph.managed import RemainingSteps` | `langgraph/graph-api.md` |
| `from langgraph.prebuilt import ToolCallTransformer` | `langgraph/event-streaming.md` |
| `from langgraph.pregel import ChannelWriteEntry` | `langgraph/pregel.md` |
| `from langgraph.pregel import NodeBuilder` | `langgraph/pregel.md` |
| `from langgraph.pregel import Pregel` | `langgraph/pregel.md` |
| `from langgraph.runtime import RunControl` | `langgraph/fault-tolerance.md` |
| `from langgraph.store.base import BaseStore` | `langgraph/stores.md` |
| `from langgraph.store.base import IndexConfig` | `langchain/long-term-memory.md` |
| `from langgraph.store.postgres import #` | `langchain/long-term-memory.md` |
| `from langgraph.store.postgres import ignore[import-not-found]` | `langchain/long-term-memory.md` |
| `from langgraph.store.postgres import type:` | `langchain/long-term-memory.md` |
| `from langgraph.types import GraphOutput` | `langgraph/streaming.md` |
| `from langgraph.types import Interrupt` | `langchain/streaming.md` |
| `from langgraph.types import StreamWriter` | `langgraph/use-functional-api.md` |
| `from langgraph.types import default_retry_on` | `langgraph/fault-tolerance.md` |

## Most-used functions & methods

| Symbol | Pages | Documented in |
| --- | --- | --- |
| `invoke()` | 48 | `langchain/agents.md`, `langchain/context-engineering.md`, `langchain/event-streaming.md`, `langchain/guardrails.md`, `langchain/human-in-the-loop.md` …(+43) |
| `create_agent()` | 44 | `langchain/agents.md`, `langchain/context-engineering.md`, `langchain/deep-agent-from-scratch.md`, `langchain/event-streaming.md`, `langchain/frontend__headless-tools.md` …(+39) |
| `compile()` | 28 | `langchain/middleware__built-in.md`, `langchain/middleware__overview.md`, `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/add-memory.md` …(+23) |
| `add_edge()` | 23 | `langchain/middleware__overview.md`, `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/add-memory.md`, `langgraph/agentic-rag.md` …(+18) |
| `add_node()` | 23 | `langchain/middleware__overview.md`, `langchain/multi-agent__custom-workflow.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/add-memory.md`, `langgraph/agentic-rag.md` …(+18) |
| `init_chat_model()` | 20 | `langchain/context-engineering.md`, `langchain/event-streaming.md`, `langchain/guardrails.md`, `langchain/messages.md`, `langchain/middleware__custom.md` …(+15) |
| `return()` | 19 | `langchain/frontend__branching-chat.md`, `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__integrations__ai-elements.md` …(+14) |
| `stream_events()` | 19 | `langchain/agents.md`, `langchain/deep-agent-from-scratch.md`, `langchain/event-streaming.md`, `langchain/human-in-the-loop.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+14) |
| `join()` | 17 | `langchain/context-engineering.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md`, `langchain/frontend__markdown-messages.md`, `langchain/frontend__reasoning-tokens.md` …(+12) |
| `append()` | 13 | `langchain/context-engineering.md`, `langchain/deep-agent-from-scratch.md`, `langchain/messages.md`, `langchain/middleware__built-in.md`, `langchain/multi-agent__skills-sql-assistant.md` …(+8) |
| `interrupt()` | 12 | `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/mcp__tools.md`, `langgraph/choosing-apis.md`, `langgraph/functional-api.md` …(+7) |
| `add_conditional_edges()` | 11 | `langchain/middleware__overview.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/agentic-rag.md`, `langgraph/backward-compatibility.md`, `langgraph/choosing-apis.md` …(+6) |
| `get_weather()` | 11 | `langchain/event-streaming.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/messages.md`, `langchain/middleware__built-in.md`, `langchain/models.md` …(+6) |
| `messages()` | 11 | `langchain/frontend__branching-chat.md`, `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__join-rejoin.md` …(+6) |
| `stream()` | 9 | `langchain/deploy.md`, `langchain/messages.md`, `langchain/models.md`, `langchain/streaming.md`, `langgraph/agentic-rag.md` …(+4) |
| `submit()` | 9 | `langchain/frontend__branching-chat.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__integrations__ai-elements.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md` …(+4) |
| `uuid7()` | 9 | `langchain/agents.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/streaming.md`, `langchain/tools.md` …(+4) |
| `getpass()` | 8 | `langchain/knowledge-base.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__router-knowledge-base.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/multi-agent__subagents-personal-assistant.md` …(+3) |
| `__init__()` | 7 | `langchain/guardrails.md`, `langchain/middleware__custom.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langgraph/event-streaming.md`, `langgraph/frontend__custom-stream-channels.md` …(+2) |
| `async()` | 7 | `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/frontend__time-travel.md` …(+2) |
| `bind_tools()` | 7 | `langchain/messages.md`, `langchain/models.md`, `langchain/streaming.md`, `langgraph/agentic-rag.md`, `langgraph/quickstart.md` …(+2) |
| `entrypoint()` | 7 | `langgraph/choosing-apis.md`, `langgraph/fault-tolerance.md`, `langgraph/functional-api.md`, `langgraph/pregel.md`, `langgraph/quickstart.md` …(+2) |
| `filter()` | 7 | `langchain/frontend__headless-tools.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md`, `langchain/frontend__reasoning-tokens.md`, `langchain/frontend__structured-output.md` …(+2) |
| `handler()` | 7 | `langchain/context-engineering.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md` …(+2) |
| `import()` | 7 | `langchain/deep-agent-from-scratch.md`, `langchain/middleware__built-in.md`, `langchain/middleware__custom.md`, `langgraph/add-memory.md`, `langgraph/checkpointers.md` …(+2) |
| `override()` | 7 | `langchain/context-engineering.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/middleware__custom.md`, `langchain/models.md`, `langchain/multi-agent__handoffs-customer-support.md` …(+2) |
| `pretty_print()` | 7 | `langchain/multi-agent__handoffs-customer-support.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/short-term-memory.md`, `langgraph/agentic-rag.md`, `langgraph/quickstart.md` …(+2) |
| `search()` | 7 | `langchain/agents.md`, `langchain/long-term-memory.md`, `langchain/tools.md`, `langgraph/add-memory.md`, `langgraph/choosing-apis.md` …(+2) |
| `tool()` | 7 | `langchain/context-engineering.md`, `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__tool-calling.md`, `langchain/multi-agent__subagents.md` …(+2) |
| `find()` | 6 | `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__integrations__ai-elements.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__structured-output.md`, `langchain/frontend__tool-calling.md` …(+1) |
| `interleave()` | 6 | `langchain/event-streaming.md`, `langchain/multi-agent__subagents-personal-assistant.md`, `langchain/sql-agent.md`, `langchain/streaming.md`, `langgraph/event-streaming.md` …(+1) |
| `result()` | 6 | `langgraph/choosing-apis.md`, `langgraph/functional-api.md`, `langgraph/graph-api.md`, `langgraph/quickstart.md`, `langgraph/use-functional-api.md` …(+1) |
| `string()` | 6 | `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/frontend__tool-calling.md` …(+1) |
| `ainvoke()` | 5 | `langchain/mcp.md`, `langchain/mcp__tools.md`, `langgraph/functional-api.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `call_model()` | 5 | `langgraph/add-memory.md`, `langgraph/stores.md`, `langgraph/streaming.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `close()` | 5 | `langchain/frontend__integrations__copilotkit.md`, `langchain/sql-agent.md`, `langchain/voice-agent.md`, `langgraph/event-streaming.md`, `langgraph/sql-agent.md` |
| `computed()` | 5 | `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__markdown-messages.md`, `langchain/frontend__message-queues.md`, `langchain/frontend__structured-output.md`, `langgraph/frontend__graph-execution.md` |
| `draw_mermaid_png()` | 5 | `langgraph/agentic-rag.md`, `langgraph/quickstart.md`, `langgraph/sql-agent.md`, `langgraph/use-graph-api.md`, `langgraph/workflows-agents.md` |
| `from_conn_string()` | 5 | `langchain/long-term-memory.md`, `langchain/short-term-memory.md`, `langgraph/add-memory.md`, `langgraph/checkpointers.md`, `langgraph/persistence.md` |
| `get_graph()` | 5 | `langgraph/agentic-rag.md`, `langgraph/quickstart.md`, `langgraph/sql-agent.md`, `langgraph/use-graph-api.md`, `langgraph/workflows-agents.md` |
| `get_state()` | 5 | `langgraph/add-memory.md`, `langgraph/checkpointers.md`, `langgraph/use-functional-api.md`, `langgraph/use-subgraphs.md`, `langgraph/use-time-travel.md` |
| `get_user_info()` | 5 | `langchain/long-term-memory.md`, `langchain/short-term-memory.md`, `langchain/tools.md`, `langgraph/use-graph-api.md`, `langgraph/workflows-agents.md` |
| `list_tools()` | 5 | `langchain/mcp.md`, `langchain/mcp__auth.md`, `langchain/mcp__connections.md`, `langchain/mcp__tools.md`, `langchain/tools.md` |
| `next()` | 5 | `langchain/multi-agent__handoffs.md`, `langchain/multi-agent__subagents-personal-assistant.md`, `langgraph/checkpointers.md`, `langgraph/sql-agent.md`, `langgraph/use-time-travel.md` |
| `object()` | 5 | `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__headless-tools.md`, `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__tool-calling.md`, `langchain/structured-output.md` |
| `send_email()` | 5 | `langchain/multi-agent__subagents-personal-assistant.md`, `langchain/observability.md`, `langchain/studio.md`, `langgraph/interrupts.md`, `langgraph/studio.md` |
| `startswith()` | 5 | `langchain/context-engineering.md`, `langchain/human-in-the-loop.md`, `langchain/sql-agent.md`, `langchain/tools.md`, `langgraph/sql-agent.md` |
| `stop()` | 5 | `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/frontend__join-rejoin.md`, `langgraph/quickstart.md`, `langgraph/workflows-agents.md` |
| `useState()` | 5 | `langchain/frontend__branching-chat.md`, `langchain/frontend__join-rejoin.md`, `langchain/frontend__reasoning-tokens.md`, `langchain/frontend__time-travel.md`, `langgraph/frontend__graph-execution.md` |
| `values()` | 5 | `langchain/frontend__integrations__openui.md`, `langchain/multi-agent__handoffs-customer-support.md`, `langgraph/frontend__custom-stream-channels.md`, `langgraph/frontend__graph-execution.md`, `langgraph/frontend__overview.md` |
| `writer()` | 5 | `langchain/deep-agent-from-scratch.md`, `langchain/streaming.md`, `langchain/tools.md`, `langgraph/event-streaming.md`, `langgraph/streaming.md` |
| `astream_events()` | 4 | `langchain/event-streaming.md`, `langchain/voice-agent.md`, `langgraph/event-streaming.md`, `langgraph/functional-api.md` |
| `display()` | 4 | `langgraph/agentic-rag.md`, `langgraph/quickstart.md`, `langgraph/use-graph-api.md`, `langgraph/workflows-agents.md` |
| `extend()` | 4 | `langchain/multi-agent__handoffs-customer-support.md`, `langchain/streaming.md`, `langgraph/checkpointers.md`, `langgraph/pregel.md` |
| `get_state_history()` | 4 | `langgraph/add-memory.md`, `langgraph/checkpointers.md`, `langgraph/use-functional-api.md`, `langgraph/use-time-travel.md` |
| `isLoading()` | 4 | `langchain/frontend__reasoning-tokens.md`, `langchain/frontend__structured-output.md`, `langchain/frontend__time-travel.md`, `langgraph/frontend__graph-execution.md` |
| `my_node()` | 4 | `langgraph/checkpointers.md`, `langgraph/fault-tolerance.md`, `langgraph/graph-api.md`, `langgraph/use-graph-api.md` |
| `node_a()` | 4 | `langgraph/checkpointers.md`, `langgraph/graph-api.md`, `langgraph/interrupts.md`, `langgraph/use-graph-api.md` |
| `process()` | 4 | `langchain/frontend__reasoning-tokens.md`, `langgraph/event-streaming.md`, `langgraph/fault-tolerance.md`, `langgraph/frontend__custom-stream-channels.md` |
| `push()` | 4 | `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md`, `langgraph/event-streaming.md`, `langgraph/frontend__custom-stream-channels.md` |
| `setup()` | 4 | `langchain/long-term-memory.md`, `langchain/short-term-memory.md`, `langgraph/checkpointers.md`, `langgraph/persistence.md` |
| `should_continue()` | 4 | `langgraph/choosing-apis.md`, `langgraph/quickstart.md`, `langgraph/sql-agent.md`, `langgraph/workflows-agents.md` |
| `sleep()` | 4 | `langgraph/functional-api.md`, `langgraph/graph-api.md`, `langgraph/use-functional-api.md`, `langgraph/use-graph-api.md` |
| `state()` | 4 | `langchain/frontend__join-rejoin.md`, `langchain/streaming.md`, `langgraph/use-graph-api.md`, `langgraph/use-subgraphs.md` |
| `task()` | 4 | `langchain/multi-agent__subagents.md`, `langgraph/fault-tolerance.md`, `langgraph/functional-api.md`, `langgraph/use-functional-api.md` |
| `with_structured_output()` | 4 | `langchain/models.md`, `langchain/multi-agent__router-knowledge-base.md`, `langgraph/agentic-rag.md`, `langgraph/workflows-agents.md` |
| `add_messages()` | 3 | `langgraph/quickstart.md`, `langgraph/use-functional-api.md`, `langgraph/workflows-agents.md` |
| `agent()` | 3 | `langgraph/quickstart.md`, `langgraph/use-functional-api.md`, `langgraph/workflows-agents.md` |
| `aput()` | 3 | `langgraph/add-memory.md`, `langgraph/checkpointers.md`, `langgraph/stores.md` |
| `boolean()` | 3 | `langchain/frontend__declarative-generative-ui.md`, `langchain/frontend__headless-tools.md`, `langgraph/graph-api.md` |
| `call_api()` | 3 | `langgraph/fault-tolerance.md`, `langgraph/graph-api.md`, `langgraph/use-functional-api.md` |
| `call_tool()` | 3 | `langgraph/quickstart.md`, `langgraph/use-functional-api.md`, `langgraph/workflows-agents.md` |
| `connect()` | 3 | `langchain/sql-agent.md`, `langgraph/checkpointers.md`, `langgraph/sql-agent.md` |
| `create()` | 3 | `langchain/voice-agent.md`, `langgraph/checkpointers.md`, `langgraph/stores.md` |
| `create_deep_agent()` | 3 | `langchain/frontend__integrations__copilotkit.md`, `langchain/middleware__built-in.md`, `langchain/quickstart.md` |
| `execute()` | 3 | `langchain/sql-agent.md`, `langgraph/checkpointers.md`, `langgraph/sql-agent.md` |
| `fetchall()` | 3 | `langchain/sql-agent.md`, `langgraph/checkpointers.md`, `langgraph/sql-agent.md` |
| `fetchone()` | 3 | `langchain/sql-agent.md`, `langgraph/checkpointers.md`, `langgraph/sql-agent.md` |
| `generate_joke()` | 3 | `langgraph/streaming.md`, `langgraph/use-graph-api.md`, `langgraph/workflows-agents.md` |
| `get_stream_writer()` | 3 | `langchain/streaming.md`, `langgraph/event-streaming.md`, `langgraph/streaming.md` |
| `hasattr()` | 3 | `langchain/frontend__integrations__copilotkit.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/test__integration-testing.md` |
| `info()` | 3 | `langchain/deep-agent-from-scratch.md`, `langchain/runtime.md`, `langgraph/fault-tolerance.md` |
| `interrupts()` | 3 | `langgraph/interrupts.md`, `langgraph/use-subgraphs.md`, `langgraph/use-time-travel.md` |
| `items()` | 3 | `langchain/mcp__connections.md`, `langchain/streaming.md`, `langgraph/streaming.md` |
| `lower()` | 3 | `langchain/guardrails.md`, `langchain/streaming.md`, `langgraph/choosing-apis.md` |
| `main()` | 3 | `langchain/mcp.md`, `langgraph/checkpointers.md`, `langgraph/use-functional-api.md` |
| `my_workflow()` | 3 | `langgraph/fault-tolerance.md`, `langgraph/functional-api.md`, `langgraph/use-functional-api.md` |
| `node()` | 3 | `langgraph/event-streaming.md`, `langgraph/streaming.md`, `langgraph/use-graph-api.md` |
| `node_b()` | 3 | `langgraph/checkpointers.md`, `langgraph/interrupts.md`, `langgraph/use-graph-api.md` |
| `number()` | 3 | `langchain/frontend__human-in-the-loop.md`, `langchain/frontend__integrations__copilotkit.md`, `langgraph/graph-api.md` |
| `payment_error_handler()` | 3 | `langgraph/fault-tolerance.md`, `langgraph/thinking-in-langgraph.md`, `langgraph/use-graph-api.md` |
| `replace()` | 3 | `langchain/frontend__integrations__openui.md`, `langchain/sql-agent.md`, `langgraph/sql-agent.md` |
| `reversed()` | 3 | `langchain/multi-agent__handoffs.md`, `langchain/tools.md`, `langgraph/checkpointers.md` |
| `signal()` | 3 | `langchain/frontend__join-rejoin.md`, `langchain/frontend__markdown-messages.md`, `langgraph/fault-tolerance.md` |
| `slice()` | 3 | `langchain/frontend__integrations__openui.md`, `langchain/frontend__reasoning-tokens.md`, `langchain/frontend__time-travel.md` |
| `split()` | 3 | `langchain/frontend__integrations__openui.md`, `langchain/sql-agent.md`, `langgraph/sql-agent.md` |
| `stringify()` | 3 | `langchain/frontend__headless-tools.md`, `langchain/frontend__integrations__copilotkit.md`, `langchain/frontend__time-travel.md` |
| `strip()` | 3 | `langchain/sql-agent.md`, `langgraph/choosing-apis.md`, `langgraph/sql-agent.md` |
| `trim()` | 3 | `langchain/frontend__integrations__openui.md`, `langchain/frontend__reasoning-tokens.md`, `langgraph/frontend__graph-execution.md` |
| `update()` | 3 | `langchain/frontend__join-rejoin.md`, `langgraph/graph-api.md`, `langgraph/pregel.md` |
| `useCallback()` | 3 | `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md`, `langchain/frontend__join-rejoin.md` |
| `useEffect()` | 3 | `langchain/frontend__integrations__openui.md`, `langchain/frontend__time-travel.md`, `langgraph/frontend__graph-execution.md` |
| `useStream()` | 3 | `langchain/frontend__integrations__ai-elements.md`, `langchain/frontend__integrations__assistant-ui.md`, `langchain/frontend__integrations__openui.md` |
| `uuid4()` | 3 | `langgraph/add-memory.md`, `langgraph/persistence.md`, `langgraph/stores.md` |
| `workflow()` | 3 | `langgraph/choosing-apis.md`, `langgraph/functional-api.md`, `langgraph/use-functional-api.md` |
| `wrap_model_call()` | 3 | `langchain/middleware__custom.md`, `langchain/multi-agent__skills-sql-assistant.md`, `langchain/tools.md` |
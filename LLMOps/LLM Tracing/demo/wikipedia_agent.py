"""Wikipedia agent with LangSmith tracing — the example from LLM Tracing.pdf, modernised.

The PDF's code targets LangChain 0.x and will NOT run on LangChain 1.x:
  - `initialize_agent` was removed          -> `create_agent`
  - `AgentType` was removed                 -> no longer needed
  - `ConversationBufferMemory` deprecated   -> LangGraph checkpointer (InMemorySaver)
  - ChatOpenAI moved out of community       -> `langchain_openai`

Tracing itself is unchanged and is still pure configuration: set LANGSMITH_TRACING=true
plus the keys in .env, and every step is captured automatically — no per-call
instrumentation, because every component implements the same Runnable interface.
"""

import os
import time

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

for required in ("OPENAI_API_KEY", "LANGSMITH_API_KEY"):
    if not os.environ.get(required):
        raise SystemExit(f"Missing {required} in .env")

print(f"Tracing to LangSmith project: {os.environ.get('LANGSMITH_PROJECT')}\n")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
tools = load_tools(["wikipedia"])

# InMemorySaver is the modern replacement for ConversationBufferMemory: the graph
# checkpoints state per thread_id instead of replaying a transcript string.
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful research assistant. Use Wikipedia to answer factual questions.",
    checkpointer=InMemorySaver(),
)

QUESTIONS = [
    "Who won the 2022 Fifa world cup?",
    "And who was the top scorer in that tournament?",  # tests memory via thread_id
]

config = {"configurable": {"thread_id": "demo-session-1"}}

for i, q in enumerate(QUESTIONS, 1):
    started = time.perf_counter()
    result = agent.invoke({"messages": [{"role": "user", "content": q}]}, config=config)
    elapsed = time.perf_counter() - started

    answer = result["messages"][-1].content
    tool_calls = sum(
        len(getattr(m, "tool_calls", []) or []) for m in result["messages"]
    )

    print(f"--- Q{i} ({elapsed:.2f}s, {tool_calls} tool call(s)) ---")
    print(f"Q: {q}")
    print(f"A: {answer}\n")

print("Done. Open the LangSmith project to inspect the traces.")

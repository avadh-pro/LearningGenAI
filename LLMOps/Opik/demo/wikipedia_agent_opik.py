"""The same Wikipedia agent as the LangSmith demo, traced with Opik instead.

Deliberately identical work to `LLMOps/LLM Tracing/demo/wikipedia_agent.py` so the
two tools can be compared on the same task.

The contrast worth noticing:
  - LangSmith  -> configuration only. Set LANGSMITH_TRACING=true and every LangChain
                  step is captured automatically, because it hooks the Runnable interface.
  - Opik       -> explicit. You either attach the OpikTracer callback, or decorate
                  functions with @opik.track. That is *why* Opik is framework-agnostic:
                  it doesn't depend on LangChain internals, so it works with anything.

Self-hosted: `opik.configure(use_local=True)` points the SDK at http://localhost:5173.
"""

import os
import sys
import time

import opik
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from opik.integrations.langchain import OpikTracer

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise SystemExit("Missing OPENAI_API_KEY in .env")

# Point the SDK at the locally self-hosted Opik server rather than Comet cloud.
opik.configure(use_local=True, force=True)

PROJECT = "wikipedia-agent-opik-demo"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
tools = load_tools(["wikipedia"])

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful research assistant. Use Wikipedia to answer factual questions.",
    checkpointer=InMemorySaver(),
)

# The explicit bit: Opik rides along as a LangChain callback.
opik_tracer = OpikTracer(project_name=PROJECT, tags=["wikipedia-agent", "demo"])

# Pass your own questions as command-line args, e.g.
#     python wikipedia_agent_opik.py "Who invented the telephone?"
# With no args it runs the default two-turn conversation.
QUESTIONS = sys.argv[1:] or [
    "Who won the 2022 Fifa world cup?",
    "And who was the top scorer in that tournament?",
]

# A fresh thread_id per run, so each run shows up as its own conversation in the
# UI instead of appending to the previous one.
THREAD_ID = f"opik-demo-{int(time.time())}"

config = {
    "configurable": {"thread_id": THREAD_ID},
    "callbacks": [opik_tracer],
}

print(f"Tracing to local Opik project: {PROJECT}\n")

for i, q in enumerate(QUESTIONS, 1):
    started = time.perf_counter()
    result = agent.invoke({"messages": [{"role": "user", "content": q}]}, config=config)
    elapsed = time.perf_counter() - started

    answer = result["messages"][-1].content
    tool_calls = sum(len(getattr(m, "tool_calls", []) or []) for m in result["messages"])

    print(f"--- Q{i} ({elapsed:.2f}s, {tool_calls} tool call(s)) ---")
    print(f"Q: {q}")
    print(f"A: {answer}\n")

opik_tracer.flush()
print("Done. Open http://localhost:5173 and look for project:", PROJECT)

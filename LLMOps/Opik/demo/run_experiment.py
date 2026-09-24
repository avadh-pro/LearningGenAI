"""Batch 4 — Automated Evaluation: a DATASET of test cases + an EXPERIMENT that
runs the REAL agent (tools and all) against every one of them.

This is the honest answer to "the Prompt Playground doesn't call tools":
here the task function invokes your actual LangGraph agent, so tool calls,
latency and traces are all real.

Metrics used here are HEURISTIC (no LLM, free, deterministic):
    Contains        - is the expected keyword present in the answer?
    LevenshteinRatio- how close is the text to the reference?
LLM-as-a-judge metrics are Batch 5.

Run:
    python run_experiment.py                 # uses the default system prompt
    python run_experiment.py strict          # uses the stricter prompt variant
"""

import sys

import opik
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
from opik.evaluation import evaluate
from opik.evaluation.metrics import Contains, LevenshteinRatio
from opik.integrations.langchain import OpikTracer

load_dotenv()
opik.configure(use_local=True, force=True)

PROJECT = "wikipedia-agent-opik-demo"

# Two prompt VARIANTS, so you can run two experiments and compare them.
PROMPTS = {
    "default": "You are a helpful research assistant. Use Wikipedia to answer factual questions.",
    "strict": (
        "You are a research assistant. Answer in ONE short sentence. "
        "Only search Wikipedia if you are genuinely unsure - if you already know "
        "the fact, answer directly without searching."
    ),
}
variant = sys.argv[1] if len(sys.argv) > 1 else "default"
system_prompt = PROMPTS[variant]

client = opik.Opik(project_name=PROJECT)

# ---------------------------------------------------------------- the DATASET
# A dataset is just a list of test cases: an input, and what a good answer
# should contain. get_or_create means re-running this script won't duplicate it.
dataset = client.get_or_create_dataset(name="wikipedia-qa")
dataset.insert(
    [
        {"input": "Who won the 2022 FIFA world cup?", "expected_output": "Argentina"},
        {"input": "Who wrote the novel 1984?", "expected_output": "Orwell"},
        {"input": "What is the capital of Australia?", "expected_output": "Canberra"},
        {"input": "Who invented the telephone?", "expected_output": "Bell"},
        {"input": "What is the tallest mountain in the world?", "expected_output": "Everest"},
    ]
)

# ------------------------------------------------------------------- the TASK
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
tools = load_tools(["wikipedia"])
agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)


def task(item):
    """Run the REAL agent on one dataset row. Tools included."""
    tracer = OpikTracer(project_name=PROJECT, tags=["experiment", variant])
    result = agent.invoke(
        {"messages": [{"role": "user", "content": item["input"]}]},
        config={"callbacks": [tracer]},
    )
    return {"output": result["messages"][-1].content}


# ------------------------------------------------------------- the EXPERIMENT
evaluation = evaluate(
    dataset=dataset,
    task=task,
    scoring_metrics=[Contains(), LevenshteinRatio()],
    experiment_name=f"wikipedia-qa-{variant}",
    project_name=PROJECT,
    scoring_key_mapping={"reference": "expected_output"},
)

print(f"\nExperiment '{f'wikipedia-qa-{variant}'}' complete.")
print("Open Evaluation -> Experiments in the Opik UI to compare runs.")

"""Batch 2 — log feedback scores (annotations) from the SDK instead of by hand.

An annotation answers the question tracing cannot: "was that answer any GOOD?"
Tracing records what happened; a feedback score records whether it was acceptable.

Run:
    python annotate_traces.py            # score the most recent trace
    python annotate_traces.py 5          # score the 5 most recent traces
"""

import sys

import opik

PROJECT = "wikipedia-agent-opik-demo"

client = opik.Opik(project_name=PROJECT)

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1
traces = client.search_traces(project_name=PROJECT, max_results=limit)

if not traces:
    raise SystemExit(f"No traces found in '{PROJECT}'. Run wikipedia_agent_opik.py first.")

scores = []
for t in traces:
    # In real life these values come from a human reviewer, a thumbs-up button
    # in your product, or an automated judge (that's Batch 5).
    scores.append(
        {
            "id": t.id,
            "name": "correctness",
            "value": 1.0,
            "reason": "Answer is factually correct and cites Wikipedia.",
        }
    )
    # Categorical scores still need a NUMERIC value; the human-readable label
    # goes in category_name. Passing the emoji as `value` is rejected.
    scores.append(
        {
            "id": t.id,
            "name": "User feedback",
            "value": 1.0,
            "category_name": "👍",
        }
    )

client.log_traces_feedback_scores(scores)
client.flush()

print(f"Logged {len(scores)} feedback scores across {len(traces)} trace(s):")
for t in traces:
    print(f"  trace {t.id}")
print(f"\nOpen the project and look at the 'Feedback scores' column / tab.")

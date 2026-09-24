"""Batch 2 follow-up — CONDITIONAL annotation, computed from the trace's own data.

`annotate_traces.py` hardcoded value=1.0, which is only useful as a demo. Real
annotation is a RULE: you read what the span actually did and derive the score.

This scores every span against a latency SLA, and annotates the SPAN (not the
trace), so a slow tool call gets flagged on the exact step that was slow.

Run:
    python annotate_by_rule.py
"""

import opik

PROJECT = "wikipedia-agent-opik-demo"

# The SLA. Anything slower than FAIL_OVER seconds is a failure.
WARN_OVER = 3.0
FAIL_OVER = 5.0

client = opik.Opik(project_name=PROJECT)
spans = client.search_spans(project_name=PROJECT, max_results=200)

scores = []
for s in spans:
    secs = (s.end_time - s.start_time).total_seconds()

    # THE RULE — the score is computed, not hardcoded.
    if secs > FAIL_OVER:
        value, verdict = 0.0, f"SLA breach: {secs:.1f}s > {FAIL_OVER}s"
    elif secs > WARN_OVER:
        value, verdict = 0.5, f"Slow: {secs:.1f}s"
    else:
        value, verdict = 1.0, f"OK: {secs:.1f}s"

    scores.append(
        {"id": s.id, "name": "latency_sla", "value": value, "reason": verdict}
    )

    # A second rule: did the step error out?
    scores.append(
        {
            "id": s.id,
            "name": "no_error",
            "value": 0.0 if s.error_info else 1.0,
            "reason": "errored" if s.error_info else "clean",
        }
    )

client.log_spans_feedback_scores(scores)
client.flush()

print(f"Scored {len(spans)} spans against the latency SLA:\n")
for s in sorted(spans, key=lambda x: (x.end_time - x.start_time).total_seconds(), reverse=True)[:8]:
    secs = (s.end_time - s.start_time).total_seconds()
    flag = "FAIL" if secs > FAIL_OVER else ("WARN" if secs > WARN_OVER else "ok  ")
    print(f"  [{flag}]  {secs:6.2f}s   {s.name}  ({s.type})")

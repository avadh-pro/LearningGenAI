# Interview Prep — Study Order (Week 4: AI Agents)

*Eight topic documents, 72 interview questions plus 9 follow-ups, roughly 21,000 words. This file answers one question — what do I read first?*

**The files are numbered `01` through `08` in the order you should read them, so just go top to bottom.** This document explains *why* that order, and what to cut if you're short on time.

The one thing not to do: **don't jump to the framework files.** `04` and `05` assume you already know what a cycle is, why reliability compounds, and what a handoff loses. Read them cold and you'll memorise API surface without understanding why the API looks like that — which is exactly what an interviewer probes.

---

## The order, at a glance

| # | Document | Q + follow-ups | Time | Why here |
|---|---|---|---|---|
| 1 | **AI Agent Fundamentals** | 9 + 2 | ~30 min | What an agent is, and when it's the wrong answer. Every other file assumes this. |
| 2 | **Agent Architecture and Tools** | 9 + 2 | ~30 min | One agent's internals — tool calls, memory, context. |
| 3 | **Multi-Agent Systems** | 9 | ~25 min | Coordination theory, framework-neutral. Read before any framework. |
| 4 | **CrewAI** | 9 + 1 | ~20 min | The simpler framework. Makes LangGraph's extra machinery make sense. |
| 5 | **LangChain and LangGraph Agents** | 10 + 4 | ~35 min | The deepest set. State, cycles, checkpointers, interrupts. |
| 6 | **Model Context Protocol (MCP)** | 8 | ~20 min | Standalone — movable, but read `02` first for tool-calling basics. |
| 7 | **Agent Evaluation and Observability** | 9 | ~25 min | How you know any of it works. |
| 8 | **Serving Agents in Production** | 9 | ~30 min | The senior differentiator. Assumes everything above. |

**One focused pass: roughly 3.5 hours.** Realistically two or three sessions, not one sitting.

---

## Why this order — the dependency chain

```
01 Fundamentals ──────────► what an agent is, perceive-think-act,
   │                        agent vs workflow, reliability compounding
   ▼
02 Architecture & Tools ──► how a tool call works, memory vs state,
   │                        context bloat, tool schema design
   ├──────────────► 06 MCP  (needs tool calling from 02)
   ▼
03 Multi-Agent ───────────► coordination patterns, handoff loss,
   │                        failure attribution
   ├──► 04 CrewAI ────────► the patterns, concretely (Crew = fixed shape)
   └──► 05 LangGraph ─────► the patterns, with runtime routing
        │                   (05 is easier once you've seen 04's limits)
        ▼
   07 Evaluation ─────────► measuring all of the above
        ▼
   08 Production ─────────► everything, under real traffic
```

Three dependencies worth naming explicitly:

- **`01` before everything.** The reliability-compounding arithmetic (0.95⁵ ≈ 77%) shows up in `03`, `04` and `08`. Learn it once here.
- **`03` before `04` and `05`.** Both frameworks are implementations of the patterns in `03`. Learn the pattern, then the syntax — not the reverse.
- **`04` before `05`.** CrewAI's limitation (a Crew can't loop) is the cleanest possible motivation for LangGraph's cycles and conditional edges. Reading `05` first makes LangGraph look needlessly complex.

---

## If you're short on time

**90 minutes, interview tomorrow:** `01` → `03` → `05`. Fundamentals, coordination theory, and the framework you'll actually be asked about.

**One hour:** `01` → `05`. Accept that you'll be weak on multi-agent design questions.

**You already build agents daily, want the gaps:** `07` → `08` → `06`. Evaluation, production failure modes, and the MCP changes. These are where experienced candidates most often have blind spots, because they're the parts you can avoid learning while still shipping.

**Interview is specifically about a framework:** read `03` first regardless, then the relevant one. Interviewers routinely ask "why this framework?" and a framework-only answer is weak.

---

## ⚠️ Things in here that contradict older material

Three items where the course material and most online tutorials are now wrong. These are high-value precisely *because* most candidates repeat the outdated version:

1. **MCP is stateless.** The 2026-07-28 revision removed the `initialize` handshake and `Mcp-Session-Id`. "Stateful, unlike REST" was MCP's headline pitch and is now false. `06`, Q4.
2. **`AgentExecutor`, `initialize_agent` and `create_react_agent` are removed** in LangChain 1.0, not deprecated — moved to `langchain-classic`. `create_agent` is the only constructor, and it runs on LangGraph. `05`, Q1.
3. **CrewAI Flows closes most of the gap** the course notes imply. Crews can't loop; Flows can, via `@router`, with durable pause and persistence. `04`, Q4–Q5.

---

## How to actually use these

The format is two layers per question, deliberately:

- **✅ Strong answer** — what you'd actually say. Plain language, an everyday example, sometimes a diagram. This is the one to internalise.
- **🎯 Standard Interview Answer** — the compressed, precise version. Useful for the senior-sounding follow-up, but reciting it cold sounds rehearsed.

**Answer out loud before reading.** Reading an answer and thinking "yes, I knew that" is the most common way to feel prepared and then stall in the room. The gap between recognising an answer and producing one is where interviews are lost.

Where a question says *correct me if I'm wrong* or gives a ⚠️, that's a deliberate trap — those are the questions interviewers use to separate memorised answers from understood ones.

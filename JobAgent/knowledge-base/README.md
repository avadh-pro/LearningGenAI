# LangChain + LangGraph Knowledge Base

Local, offline, greppable copy of the **official Python documentation** for LangChain and
LangGraph — captured so that every design and implementation decision on this project can be
checked against the real docs instead of recalled from memory.

**Captured:** 2026-09-14 · **Source:** `https://docs.langchain.com/oss/python/`
**Method:** headless Chromium (Playwright) render of every page, DOM → markdown

| | |
| --- | --- |
| Pages | **104** (69 LangChain · 35 LangGraph) |
| Size | **~1.72M characters** |
| Code blocks | ~1,900 |
| Failures | 0 |

---

## Layout

```
knowledge-base/
├── README.md            ← you are here
├── CORE-CONCEPTS.md     ← START HERE. Synthesised guide + gotcha cheat-sheet
├── INDEX.md             ← all 104 pages, with section headings, linked to source
├── API-REFERENCE.md     ← every import & function in the docs → which page documents it
├── langchain/           ← 69 pages of raw markdown
├── langgraph/           ← 35 pages of raw markdown
├── _pages.json          ← machine-readable page metadata
└── _tools/              ← the crawler, so this can be refreshed
    ├── discover.py      ← walks the docs nav + sitemap → urls.json
    ├── crawl.py         ← headless render + DOM→markdown for every URL
    ├── build_index.py   ← regenerates INDEX.md and API-REFERENCE.md
    ├── browser.py       ← Chromium launch config
    └── refresh.sh       ← runs all three in order
```

Every page file carries YAML frontmatter with its canonical source URL:

```yaml
---
source: https://docs.langchain.com/oss/python/langgraph/graph-api
title: Graph API overview
package: langgraph
---
```

---

## How to use it

**1. Orient** → read `CORE-CONCEPTS.md`. It covers the agent model, `create_agent`, middleware,
structured output, human-in-the-loop, the LangGraph runtime, persistence, interrupts, the
multi-agent pattern comparison, and a 14-item table of traps that silently break agents.

**2. Locate a topic** → `INDEX.md` is a table of all 104 pages with their section headings.

**3. Locate a symbol** → `API-REFERENCE.md` maps imports and functions to the pages that use them.

**4. Grep** — it is all plain markdown:

```bash
grep -ril "HumanInTheLoopMiddleware" .
grep -n  "interrupt_on"  langchain/human-in-the-loop.md
grep -rn "PostgresSaver" langgraph/
```

**5. Read the actual page** before writing code against an API. `CORE-CONCEPTS.md` is a map;
the pages are the terrain.

---

## Why this exists

LangChain **1.0** (released 2025-10-20) removed every legacy chain and agent abstraction. There
is now exactly one high-level entry point, `create_agent`; the old `LLMChain`, `AgentExecutor`,
`initialize_agent`, and `RetrievalQA` APIs have moved to a separate `langchain-classic` package.

Most LangChain knowledge in circulation — tutorials, blog posts, model training data — predates
that break. Writing 0.x-shaped code against a 1.x install fails in confusing ways. This
knowledge base is the guard against that: **when there is any doubt about a LangChain or
LangGraph API, the answer comes from these files, not from recall.**

---

## Refreshing

The docs change. To re-capture:

```bash
bash _tools/refresh.sh
```

This rediscovers the page list (nav crawl + sitemap), re-renders every page headless, and
rebuilds `INDEX.md` and `API-REFERENCE.md`. `CORE-CONCEPTS.md` is hand-written — review it
manually if the docs have changed shape.

**Requirements:** Python 3.13 · `playwright` 1.57 · Chromium headless shell. `browser.py` pins
the executable path; override with the `PW_CHROME` environment variable if your Playwright
browser revision differs.

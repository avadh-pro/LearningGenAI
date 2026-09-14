#!/usr/bin/env bash
# Re-crawl the LangChain/LangGraph docs and rebuild the knowledge base.
# Usage:  bash _tools/refresh.sh
set -e
cd "$(dirname "$0")"
python discover.py      # rediscover page URLs -> urls.json
python crawl.py         # crawl every page    -> ../langchain/*.md, ../langgraph/*.md
python build_index.py   # rebuild INDEX.md + API-REFERENCE.md
echo "Knowledge base refreshed. Review CORE-CONCEPTS.md by hand if the docs changed shape."

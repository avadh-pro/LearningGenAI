import io, os, re, json, collections

KB = r"C:/Users/Avado/OneDrive/Desktop/Final-Destination/options-magic/knowledge-base"

def read(p): return io.open(p, encoding="utf-8").read()

pages = []
for pkg in ("langchain", "langgraph"):
    d = os.path.join(KB, pkg)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        txt = read(os.path.join(d, fn))
        m = re.search(r"^source: (.+)$", txt, re.M)
        t = re.search(r"^title: (.*)$", txt, re.M)
        body = txt.split("---", 2)[-1]
        heads = re.findall(r"^(#{2,3}) (.+)$", body, re.M)
        code = re.findall(r"^```(\w*)\n(.*?)^```", body, re.M | re.S)
        pages.append({
            "pkg": pkg, "file": fn, "url": m.group(1) if m else "",
            "title": (t.group(1) if t else fn).strip(),
            "slug": fn[:-3].replace("__", "/"),
            "chars": len(body), "heads": [h[1].strip() for h in heads],
            "n_code": len(code), "code": [c[1] for c in code],
        })

# ---------- INDEX.md ----------
out = ["# LangChain + LangGraph Knowledge Base — Index", "",
       f"Crawled from the official Python docs at `https://docs.langchain.com/oss/python/`.",
       f"**{len(pages)} pages · {sum(p['chars'] for p in pages):,} characters · "
       f"{sum(p['n_code'] for p in pages):,} code blocks**", "",
       "Every page below is a local markdown file. Grep this directory before answering any "
       "LangChain/LangGraph question.", "",
       "```bash", f'grep -ril "create_agent" "{KB}"', "```", ""]

for pkg in ("langchain", "langgraph"):
    ps = [p for p in pages if p["pkg"] == pkg]
    out += [f"## {pkg}  ({len(ps)} pages)", "",
            "| Page | File | Size | Key sections |", "| --- | --- | --- | --- |"]
    for p in ps:
        heads = ", ".join(p["heads"][:6]) or "—"
        if len(p["heads"]) > 6: heads += f", …(+{len(p['heads'])-6})"
        heads = heads.replace("|", "\|")
        out.append(f"| [{p['title']}]({p['url']}) | `{pkg}/{p['file']}` | {p['chars']//1000}k | {heads} |")
    out.append("")

io.open(os.path.join(KB, "INDEX.md"), "w", encoding="utf-8").write("\n".join(out))

# ---------- API-REFERENCE.md : symbol -> pages ----------
SYM = re.compile(r"\b([a-z_][a-z0-9_]{3,})\s*\(", re.I)
IMPORTS = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\s+(.+)|import\s+([\w.]+))", re.M)

sym_pages = collections.defaultdict(set)
imp_pages = collections.defaultdict(set)
NOISE = {"print", "range", "len", "str", "int", "list", "dict", "set", "type", "super",
         "isinstance", "format", "input", "open", "enumerate", "zip", "getattr", "setattr"}

for p in pages:
    ref = f"{p['pkg']}/{p['file']}"
    for block in p["code"]:
        for m in IMPORTS.finditer(block):
            mod = m.group(1) or m.group(3)
            if not mod or not mod.startswith(("langchain", "langgraph")): continue
            names = m.group(2) or ""
            for n in re.split(r"[,\s]+", names.replace("(", "").replace(")", "")):
                n = n.strip()
                if n and n != "as":
                    imp_pages[f"from {mod} import {n}"].add(ref)
            if not names: imp_pages[f"import {mod}"].add(ref)
        for m in SYM.finditer(block):
            s = m.group(1)
            if s.lower() in NOISE or s[0].isupper(): continue
            sym_pages[s].add(ref)

out = ["# LangChain + LangGraph — API / Symbol Reference", "",
       "Auto-extracted from every code block in the crawled docs. "
       "Use this to find *which page* documents a symbol, then read that page.", "",
       "## Canonical imports", "", "| Import | Documented in |", "| --- | --- |"]
for imp, refs in sorted(imp_pages.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    if len(refs) < 1: continue
    r = ", ".join(f"`{x}`" for x in sorted(refs)[:5])
    if len(refs) > 5: r += f" …(+{len(refs)-5})"
    out.append(f"| `{imp}` | {r} |")

out += ["", "## Most-used functions & methods", "", "| Symbol | Pages | Documented in |", "| --- | --- | --- |"]
for s, refs in sorted(sym_pages.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    if len(refs) < 3: continue
    r = ", ".join(f"`{x}`" for x in sorted(refs)[:5])
    if len(refs) > 5: r += f" …(+{len(refs)-5})"
    out.append(f"| `{s}()` | {len(refs)} | {r} |")

io.open(os.path.join(KB, "API-REFERENCE.md"), "w", encoding="utf-8").write("\n".join(out))

json.dump(pages, io.open(os.path.join(KB, "_pages.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(f"INDEX.md + API-REFERENCE.md written")
print(f"pages={len(pages)} imports={len(imp_pages)} symbols={len(sym_pages)}")

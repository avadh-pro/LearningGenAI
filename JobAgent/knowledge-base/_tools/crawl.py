import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
from browser import launch, UA

OUT = r"C:/Users/Avado/OneDrive/Desktop/Final-Destination/options-magic/knowledge-base"
BASE = "https://docs.langchain.com/oss/python/"
CONC = 5

JS_EXTRACT = r"""
() => {
  const root = document.querySelector('#content-area') || document.querySelector('main') ||
                document.querySelector('article') || document.body;
  if (!root) return {title:'', md:''};
  const title = (document.querySelector('h1')?.innerText || document.title || '').trim();

  const SKIP = new Set(['NAV','ASIDE','SCRIPT','STYLE','NOSCRIPT','SVG','BUTTON','FOOTER','HEADER','FORM']);
  const inline = (el) => {
    let out = '';
    el.childNodes.forEach(n => {
      if (n.nodeType === 3) { out += n.textContent.replace(/\s+/g,' '); return; }
      if (n.nodeType !== 1) return;
      const t = n.tagName;
      if (SKIP.has(t)) return;
      if (t === 'CODE') out += '`' + n.innerText.trim() + '`';
      else if (t === 'STRONG' || t === 'B') out += '**' + inline(n).trim() + '**';
      else if (t === 'EM' || t === 'I') out += '*' + inline(n).trim() + '*';
      else if (t === 'A') {
        const txt = inline(n).trim(); const href = n.getAttribute('href') || '';
        out += href && txt ? `[${txt}](${href})` : txt;
      }
      else if (t === 'BR') out += '\n';
      else out += inline(n);
    });
    return out;
  };

  const BLOCK = /^(P|DIV|UL|OL|PRE|TABLE|H[1-6]|BLOCKQUOTE|SECTION|ARTICLE|MAIN|HR|FIGURE|DL|DETAILS)$/;
  const hasBlock = (el) => [...el.children].some(c => BLOCK.test(c.tagName) && !SKIP.has(c.tagName));

  const lines = [];
  const emitProse = (el) => {
    const txt = inline(el).replace(/[ \t]+/g, ' ').replace(/ ?\n ?/g, '\n').trim();
    if (txt) lines.push(txt + '\n');
  };
  const walk = (el, depth) => {
    el.childNodes.forEach(n => {
      if (n.nodeType === 3) {
        const s = n.textContent.replace(/\s+/g, ' ').trim();
        if (s) lines.push(s + '\n');
        return;
      }
      if (n.nodeType !== 1) return;
      const t = n.tagName;
      if (SKIP.has(t)) return;
      if (n.getAttribute && n.getAttribute('aria-hidden') === 'true') return;

      if (/^H[1-6]$/.test(t)) {
        const lvl = +t[1];
        const txt = n.innerText.replace(/\s*\u200b\s*/g, '').replace(/^#\s*/, '').trim();
        if (txt) lines.push('\n' + '#'.repeat(lvl) + ' ' + txt + '\n');
      }
      else if (t === 'PRE') {
        const codeEl = n.querySelector('code');
        let lang = '';
        const cls = (codeEl?.className || n.className || '');
        const m = cls.match(/language-([\w+-]+)/); if (m) lang = m[1];
        const code = (codeEl || n).innerText.replace(/\u200b/g, '').replace(/\s+$/, '');
        if (code.trim()) lines.push('\n```' + lang + '\n' + code + '\n```\n');
      }
      else if (t === 'HR') { lines.push('\n---\n'); }
      else if (t === 'UL' || t === 'OL') {
        const ordered = t === 'OL';
        let i = 1;
        n.querySelectorAll(':scope > li').forEach(li => {
          const nested = [...li.children].filter(c => /^(UL|OL|PRE|TABLE)$/.test(c.tagName));
          const clone = li.cloneNode(true);
          [...clone.children].forEach(c => { if (/^(UL|OL|PRE|TABLE)$/.test(c.tagName)) c.remove(); });
          const txt = inline(clone).replace(/\s+/g, ' ').trim();
          const bullet = ordered ? (i++) + '.' : '-';
          if (txt) lines.push('  '.repeat(depth) + bullet + ' ' + txt);
          if (nested.length) {
            nested.forEach(c => {
              if (/^(UL|OL)$/.test(c.tagName)) walk(li, depth + 1);
              else walk(li, depth);
            });
          }
        });
        lines.push('');
      }
      else if (t === 'TABLE') {
        const rows = [...n.querySelectorAll('tr')];
        if (rows.length) {
          lines.push('');
          rows.forEach((r, ri) => {
            const cells = [...r.querySelectorAll('th,td')].map(c => inline(c).replace(/\s+/g, ' ').replace(/\|/g, '\|').trim());
            if (!cells.length) return;
            lines.push('| ' + cells.join(' | ') + ' |');
            if (ri === 0) lines.push('|' + cells.map(() => ' --- ').join('|') + '|');
          });
          lines.push('');
        }
      }
      else if (t === 'P') { emitProse(n); }
      else if (t === 'BLOCKQUOTE') {
        const txt = inline(n).replace(/[ \t]+/g, ' ').trim();
        if (txt) lines.push('> ' + txt.replace(/\n/g, '\n> ') + '\n');
      }
      else if (t === 'IMG') { /* skip */ }
      else {
        if (!hasBlock(n)) emitProse(n);
        else walk(n, depth);
      }
    });
  };
  walk(root, 0);
  let md = lines.join('\n');
  md = md.replace(/\n{3,}/g, '\n\n').trim();
  return {title, md};
}
"""

def slug(url):
    rel = url.replace(BASE, "")
    pkg, rest = rel.split("/", 1)
    return pkg, rest.replace("/", "__") + ".md"

async def grab(ctx, url, idx, total, results):
    pkg, fname = slug(url)
    pg = await ctx.new_page()
    method = "dom"
    try:
        await pg.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            await pg.wait_for_selector("#content-area, main, article", timeout=20000)
        except Exception:
            pass
        await pg.wait_for_timeout(1200)
        data = await pg.evaluate(JS_EXTRACT)
        title, md = data.get("title", ""), data.get("md", "")
        if len(md) < 200:
            await pg.wait_for_timeout(2500)
            data = await pg.evaluate(JS_EXTRACT)
            title, md = data.get("title", ""), data.get("md", "")
        header = f"---\nsource: {url}\ntitle: {title}\npackage: {pkg}\n---\n\n# {title}\n\n"
        os.makedirs(os.path.join(OUT, pkg), exist_ok=True)
        with open(os.path.join(OUT, pkg, fname), "w", encoding="utf-8") as f:
            f.write(header + md + "\n")
        results.append({"url": url, "pkg": pkg, "file": fname, "title": title, "chars": len(md), "ok": len(md) >= 200})
        print(f"[{idx}/{total}] {'OK ' if len(md)>=200 else 'THIN'} {len(md):>6}c  {pkg}/{fname}", flush=True)
    except Exception as e:
        results.append({"url": url, "pkg": pkg, "file": fname, "title": "", "chars": 0, "ok": False, "err": str(e)[:160]})
        print(f"[{idx}/{total}] FAIL {url} :: {str(e)[:120]}", flush=True)
    finally:
        await pg.close()

async def main():
    urls = json.load(open("urls.json", encoding="utf-8"))
    total = len(urls)
    results = []
    async with async_playwright() as p:
        b = await launch(p)
        ctx = await b.new_context(user_agent=UA, viewport={"width": 1440, "height": 2400})
        sem = asyncio.Semaphore(CONC)
        async def bound(u, i):
            async with sem:
                await grab(ctx, u, i, total, results)
        await asyncio.gather(*[bound(u, i + 1) for i, u in enumerate(urls)])
        await b.close()
    json.dump(results, open("crawl_report.json", "w", encoding="utf-8"), indent=1)
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    print(f"\n=== DONE  ok={len(ok)}  problem={len(bad)}  totalchars={sum(r['chars'] for r in results):,}")
    for r in bad:
        print("  PROBLEM:", r["url"], r.get("err", f"only {r['chars']}c"))

asyncio.run(main())

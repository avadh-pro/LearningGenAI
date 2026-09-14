import asyncio, json, re
from playwright.async_api import async_playwright
from browser import launch, UA

SEEDS = [
    "https://docs.langchain.com/oss/python/langchain/overview",
    "https://docs.langchain.com/oss/python/langgraph/overview",
]
KEEP = re.compile(r"^https://docs\.langchain\.com/oss/python/(langchain|langgraph)/")

async def main():
    found = set()
    async with async_playwright() as p:
        b = await launch(p)
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        for seed in SEEDS:
            await pg.goto(seed, wait_until="networkidle", timeout=60000)
            await pg.wait_for_timeout(2500)
            # expand every collapsible nav group so hidden children render
            for _ in range(6):
                btns = await pg.query_selector_all('nav button, #sidebar button, [id*="sidebar"] button, aside button')
                clicked = 0
                for btn in btns:
                    try:
                        exp = await btn.get_attribute("aria-expanded")
                        if exp == "false":
                            await btn.click(timeout=1500)
                            clicked += 1
                    except Exception:
                        pass
                if clicked == 0:
                    break
                await pg.wait_for_timeout(600)
            hrefs = await pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            for h in hrefs:
                h = h.split("#")[0].split("?")[0].rstrip("/")
                if KEEP.match(h + "/") or KEEP.match(h):
                    found.add(h)
            print(f"[seed] {seed} -> running total {len(found)}", flush=True)
        # sitemap supplement
        try:
            r = await ctx.request.get("https://docs.langchain.com/sitemap.xml", timeout=30000)
            if r.ok:
                body = await r.text()
                for m in re.findall(r"<loc>(.*?)</loc>", body):
                    u = m.split("#")[0].split("?")[0].rstrip("/")
                    if KEEP.match(u + "/") or KEEP.match(u):
                        found.add(u)
                print(f"[sitemap] ok -> total {len(found)}", flush=True)
            else:
                print(f"[sitemap] status {r.status}", flush=True)
        except Exception as e:
            print(f"[sitemap] failed: {e}", flush=True)
        await b.close()
    urls = sorted(found)
    with open("urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=1)
    lc = [u for u in urls if "/langchain/" in u]
    lg = [u for u in urls if "/langgraph/" in u]
    print(f"\nTOTAL={len(urls)}  langchain={len(lc)}  langgraph={len(lg)}")
    for u in urls:
        print(" ", u.replace("https://docs.langchain.com/oss/python/", ""))

asyncio.run(main())

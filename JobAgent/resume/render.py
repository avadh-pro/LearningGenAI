"""Render resume-ats.html to PDF via headless Chromium.

Usage:  python render.py [input.html] [output.pdf]

Chromium is used rather than a PDF library so the output is a real text-layer
PDF with selectable text - the single most important ATS property.
"""
import asyncio
import os
import sys

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get(
    "PW_CHROME",
    "C:/Users/Avado/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe",
)


async def main(src: str, dst: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROME)
        page = await browser.new_page()
        await page.goto("file:///" + src.replace("\\", "/"), wait_until="networkidle")
        await page.pdf(
            path=dst,
            format="Letter",
            print_background=True,
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.55in", "right": "0.55in"},
            prefer_css_page_size=True,
        )
        await browser.close()
    print(f"rendered -> {dst}  ({os.path.getsize(dst):,} bytes)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "resume-ats.html")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "Avadh_Dobariya_Senior_AI_Solution_Engineer_ATS.pdf")
    # relative paths must resolve before being turned into a file:// URL
    asyncio.run(main(os.path.abspath(src), os.path.abspath(dst)))

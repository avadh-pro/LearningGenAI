import os
CHROME = os.environ.get(
    "PW_CHROME",
    "C:/Users/Avado/AppData/Local/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-win64/chrome-headless-shell.exe",
)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

async def launch(p):
    return await p.chromium.launch(headless=True, executable_path=CHROME)

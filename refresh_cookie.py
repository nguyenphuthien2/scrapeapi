import json, os, asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def grab_cookie(save_path="cookies.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=80)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto("https://www.facebook.com/login")
        await page.fill('input[name="email"]', os.getenv("FB_USER"))
        await page.fill('input[name="pass"]', os.getenv("FB_PASS"))
        await page.click('button[name="login"]')
        await page.wait_for_url("https://www.facebook.com/?*")  # home loaded
        cookies = await ctx.storage_state()   # returns dict with cookies
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cookies["cookies"], f, ensure_ascii=False, indent=2)
        await browser.close()
        

if __name__ == "__main__":
    asyncio.run(grab_cookie())

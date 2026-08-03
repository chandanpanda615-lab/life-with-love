import asyncio
from playwright.async_api import async_playwright
import json

PAGES = [
    "index.html",
    "land.html",
    "photographs.html",
    "days.html",
    "visit.html"
]
BASE_URL = "https://chandanpanda615-lab.github.io/life-with-love/"

async def run_review():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        report = {}

        for page_name in PAGES:
            url = BASE_URL + page_name
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            console_logs = []
            failed_requests = []
            
            page.on("console", lambda msg: console_logs.append({"type": msg.type, "text": msg.text}))
            page.on("requestfailed", lambda req: failed_requests.append({"url": req.url, "error": req.failure.error_text if req.failure else "unknown"}))
            
            # Response listener for 400+ status codes
            page.on("response", lambda res: failed_requests.append({"url": res.url, "status": res.status}) if res.status >= 400 else None)

            print(f"Auditing {url} (Desktop)...")
            await page.goto(url, wait_until="networkidle")

            # Check initial state before scroll
            initial_hidden_reveals = await page.evaluate('''() => {
                const reveals = Array.from(document.querySelectorAll('.reveal'));
                return reveals.filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.opacity === '0' || style.visibility === 'hidden';
                }).length;
            }''')

            # Scroll to bottom to trigger reveals
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

            # Check state after scroll
            post_scroll_hidden_reveals = await page.evaluate('''() => {
                const reveals = Array.from(document.querySelectorAll('.reveal'));
                return reveals.filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.opacity === '0' || style.visibility === 'hidden';
                }).length;
            }''')

            # Take full desktop screenshot after scroll
            desktop_img = f"screenshot_{page_name.replace('.html','')}_desktop.png"
            await page.screenshot(path=desktop_img, full_page=True)

            # Mobile Audit
            mobile_context = await browser.new_context(viewport={"width": 390, "height": 844})
            mobile_page = await mobile_context.new_page()
            await mobile_page.goto(url, wait_until="networkidle")
            await mobile_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await mobile_page.wait_for_timeout(1000)

            mobile_overflow = await mobile_page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            mobile_img = f"screenshot_{page_name.replace('.html','')}_mobile.png"
            await mobile_page.screenshot(path=mobile_img, full_page=True)

            # Extract page info
            info = await page.evaluate('''() => {
                return {
                    title: document.title,
                    h1: document.querySelector('h1')?.innerText?.trim() || 'NO H1',
                    navLinksCount: document.querySelectorAll('.nav-links a').length,
                    imagesCount: document.querySelectorAll('img').length,
                    brokenImages: Array.from(document.querySelectorAll('img')).filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src),
                    links: Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim(), href: a.getAttribute('href') }))
                }
            }''')

            report[page_name] = {
                "title": info["title"],
                "h1": info["h1"],
                "initial_hidden_reveals_before_scroll": initial_hidden_reveals,
                "hidden_reveals_after_scroll": post_scroll_hidden_reveals,
                "mobile_has_horizontal_overflow": mobile_overflow,
                "failed_requests": failed_requests,
                "console_errors": [c for c in console_logs if c["type"] == "error"],
                "broken_images": info["brokenImages"],
                "images_count": info["imagesCount"]
            }

            await context.close()
            await mobile_context.close()

        await browser.close()

        with open("playwright_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\nSUCCESS: Audit completed! Saved to playwright_report.json")

if __name__ == "__main__":
    asyncio.run(run_review())

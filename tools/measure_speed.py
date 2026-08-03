import asyncio
from playwright.async_api import async_playwright
import json

async def measure_performance():
    url = "https://chandanpanda615-lab.github.io/life-with-love/index.html"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to page and measuring performance...")
        
        # We will track all responses to calculate total asset weight
        assets = []
        page.on("response", lambda res: assets.append(res))

        await page.goto(url, wait_until="networkidle")

        # Get Navigation Timing API data
        timing = await page.evaluate("JSON.stringify(window.performance.timing)")
        timing_data = json.loads(timing)

        # Calculate metrics
        dns_time = timing_data['domainLookupEnd'] - timing_data['domainLookupStart']
        tcp_time = timing_data['connectEnd'] - timing_data['connectStart']
        ttfb = timing_data['responseStart'] - timing_data['requestStart']
        dom_content_loaded = timing_data['domContentLoadedEventEnd'] - timing_data['navigationStart']
        load_time = timing_data['loadEventEnd'] - timing_data['navigationStart']

        print(f"\\n--- Performance Metrics (ms) ---")
        print(f"DNS Lookup Time: {dns_time} ms")
        print(f"TCP Connection Time: {tcp_time} ms")
        print(f"Time to First Byte (TTFB): {ttfb} ms")
        print(f"DOM Content Loaded: {dom_content_loaded} ms")
        print(f"Total Page Load Time: {load_time} ms")

        # Get Paint metrics (FP and FCP)
        paint_timing = await page.evaluate('''() => {
            return JSON.stringify(performance.getEntriesByType('paint'));
        }''')
        paint_data = json.loads(paint_timing)
        for metric in paint_data:
            print(f"{metric['name']}: {round(metric['startTime'])} ms")

        # Analyze Assets
        total_size = 0
        image_size = 0
        js_size = 0
        css_size = 0
        font_size = 0

        for res in assets:
            try:
                headers = await res.all_headers()
                content_length = int(headers.get('content-length', 0))
                
                # if content-length is missing, try to get buffer length
                if content_length == 0:
                     body = await res.body()
                     content_length = len(body)
                
                total_size += content_length
                content_type = headers.get('content-type', '')
                
                if 'image' in content_type:
                    image_size += content_length
                elif 'javascript' in content_type or 'json' in content_type:
                    js_size += content_length
                elif 'css' in content_type:
                    css_size += content_length
                elif 'font' in content_type:
                    font_size += content_length
            except Exception as e:
                pass # Ignore errors from aborted/redirected requests

        print(f"\\n--- Asset Weight ---")
        print(f"Total Download Size: {total_size / 1024:.2f} KB")
        print(f"Images: {image_size / 1024:.2f} KB")
        print(f"CSS: {css_size / 1024:.2f} KB")
        print(f"JavaScript: {js_size / 1024:.2f} KB")
        print(f"Fonts: {font_size / 1024:.2f} KB")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(measure_performance())

const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    const consoleErrors = [];
    const failedRequests = [];

    page.on('console', msg => {
        if (msg.type() === 'error') {
            consoleErrors.push(msg.text());
        }
    });

    page.on('requestfailed', request => {
        failedRequests.push(`${request.url()} - ${request.failure().errorText}`);
    });

    page.on('response', response => {
        if (response.status() >= 400) {
            failedRequests.push(`${response.status()} ${response.url()}`);
        }
    });

    console.log('Navigating to website...');
    await page.goto('https://chandanpanda615-lab.github.io/life-with-love/index.html', { waitUntil: 'networkidle' });

    // Desktop Screenshot Full
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.screenshot({ path: 'screenshot_desktop_full.png', fullPage: true });

    // Mobile Screenshot Full
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'screenshot_mobile_full.png', fullPage: true });

    // Check DOM elements and components
    const auditResults = await page.evaluate(() => {
        const results = {};
        
        // 1. Navigation items
        const navLinks = Array.from(document.querySelectorAll('nav a, header a')).map(a => ({
            text: a.innerText.trim(),
            href: a.getAttribute('href')
        }));
        results.navLinks = navLinks;

        // 2. Images check
        const images = Array.from(document.querySelectorAll('img')).map(img => ({
            src: img.src,
            alt: img.alt,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            displayedWidth: img.clientWidth,
            displayedHeight: img.clientHeight,
            isLoaded: img.complete && img.naturalWidth > 0
        }));
        results.images = images;

        // 3. Overflow / Horizontal Scroll Check
        results.hasHorizontalScroll = document.documentElement.scrollWidth > window.innerWidth;
        results.documentScrollWidth = document.documentElement.scrollWidth;
        results.windowWidth = window.innerWidth;

        // 4. Component sections present
        const sections = Array.from(document.querySelectorAll('section, header, footer, main > div')).map(sec => ({
            tag: sec.tagName,
            id: sec.id,
            className: sec.className,
            heading: sec.querySelector('h1, h2, h3, h4')?.innerText?.trim() || ''
        }));
        results.sections = sections;

        // 5. Check interactive buttons / CTAs
        const buttons = Array.from(document.querySelectorAll('button, a.btn, a.cta, input[type="submit"]')).map(btn => ({
            text: btn.innerText.trim(),
            href: btn.getAttribute('href') || null,
            tag: btn.tagName
        }));
        results.buttons = buttons;

        return results;
    });

    console.log('\n--- AUDIT SUMMARY ---');
    console.log('Console Errors:', consoleErrors);
    console.log('Failed Network Requests / Broken Resources:', failedRequests);
    console.log('Has Horizontal Scroll (Mobile):', auditResults.hasHorizontalScroll);
    console.log('Sections Found:', auditResults.sections);
    console.log('Nav Links:', auditResults.navLinks);
    console.log('Images Found:', auditResults.images.length);
    console.log('Broken Images:', auditResults.images.filter(i => !i.isLoaded));

    await browser.close();
})();

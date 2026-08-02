"""Did the fixes actually work, in a real browser?

Success criteria:
  1. no console errors, no failed requests
  2. the 4 woff2 fetch as separate files with 200
  3. no .reveal element sits at opacity 0 after a human-paced scroll
  4. opening an album leaves none of its photographs invisible
  5. an anchor jump does not strand everything above it at opacity 0
  6. with JavaScript disabled, all content is still visible
"""
import http.server
import functools
import socketserver
import threading
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index", "land", "days", "photographs", "visit"]

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

# Two things are legitimately at opacity 0 and must not count as failures:
#   - a photograph inside a collapsed album (Chrome still reports offsetParent for it)
#   - anything below the fold, which is the reveal animation waiting its turn
# What must never be hidden is content at or above the fold.
HIDDEN = """() => [...document.querySelectorAll('.reveal')]
    .filter(e => e.offsetParent !== null
              && !e.closest('details:not([open])')
              && e.getBoundingClientRect().top < innerHeight
              && +getComputedStyle(e).opacity === 0).length"""

# site.css sets html { scroll-behavior: smooth }. A harness driving the page races
# that animation and reports elements as stuck that a real user sees fade in fine.
# This produced a false positive in an earlier run — force instant scrolling so we
# measure the site and not the test.
NO_SMOOTH = """() => {
  const s = document.createElement('style');
  s.textContent = 'html,*{scroll-behavior:auto !important}';
  document.documentElement.appendChild(s);
}"""

fail = []


def fresh(browser, js=True):
    ctx = browser.new_context(java_script_enabled=js,
                              viewport={"width": 390, "height": 844})
    return ctx, ctx.new_page()


with sync_playwright() as p:
    browser = p.chromium.launch()

    for name in PAGES:
        ctx, pg = fresh(browser)
        errs, bad, fonts = [], [], []
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: (
            bad.append(f"{r.status} {r.url.split('/')[-1]}") if r.status >= 400 else None,
            fonts.append(r.url.split("/")[-1]) if ".woff2" in r.url else None))

        pg.goto(f"http://127.0.0.1:{PORT}/{name}.html", wait_until="networkidle")
        pg.evaluate(NO_SMOOTH)
        for _ in range(40):                       # scroll like a person, not one jump
            pg.mouse.wheel(0, 600)
            pg.wait_for_timeout(60)
        pg.wait_for_timeout(1200)

        hidden = pg.evaluate(HIDDEN)
        print(f"{name:14} errors={len(errs)} 404s={len(bad)} "
              f"fonts={len(set(fonts))} hidden={hidden}")
        if errs:
            fail.append(f"{name}: console {errs[:3]}")
        if bad:
            fail.append(f"{name}: failed requests {bad[:3]}")
        if hidden:
            fail.append(f"{name}: {hidden} on-screen .reveal still at opacity 0")
        ctx.close()

    # --- albums: open every <details>, scroll through, nothing may stay invisible ---
    ctx, pg = fresh(browser)
    pg.goto(f"http://127.0.0.1:{PORT}/photographs.html", wait_until="networkidle")
    pg.evaluate(NO_SMOOTH)
    n = pg.locator("details.album").count()
    pg.eval_on_selector_all("details.album", "els => els.forEach(e => e.open = true)")
    for _ in range(60):
        pg.mouse.wheel(0, 600)
        pg.wait_for_timeout(50)
    pg.wait_for_timeout(1200)
    hidden = pg.evaluate(HIDDEN)
    print(f"\nalbums opened={n}  hidden_after_open={hidden}")
    if hidden:
        fail.append(f"albums: {hidden} photographs invisible after opening")
    ctx.close()

    # --- anchor jump: what threshold 0.18 with no top<0 catch used to strand -------
    ctx, pg = fresh(browser)
    pg.goto(f"http://127.0.0.1:{PORT}/photographs.html#school", wait_until="networkidle")
    pg.evaluate(NO_SMOOTH)
    pg.wait_for_timeout(1500)
    hidden = pg.evaluate(HIDDEN)
    print(f"anchor #school hidden={hidden}")
    if hidden:
        fail.append(f"anchor jump: {hidden} elements stranded above the anchor")
    ctx.close()

    # --- JS off: the page must not be blank ---------------------------------------
    ctx, pg = fresh(browser, js=False)
    pg.goto(f"http://127.0.0.1:{PORT}/photographs.html", wait_until="load")
    vis = pg.evaluate("""() => [...document.querySelectorAll('.reveal')]
        .filter(e => +getComputedStyle(e).opacity > 0).length""")
    total = pg.locator(".reveal").count()
    print(f"js disabled  : {vis}/{total} .reveal visible")
    if vis != total:
        fail.append(f"js-off: only {vis}/{total} visible")
    ctx.close()
    browser.close()

srv.shutdown()
print("\n" + ("FAILED\n  " + "\n  ".join(fail) if fail else "ALL CHECKS PASSED"))
sys.exit(1 if fail else 0)

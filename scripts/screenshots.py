"""Capture README screenshots from the running stack: docker compose up, then run this."""
from playwright.sync_api import sync_playwright

WEB, API, OUT = "http://localhost:8080", "http://localhost:8000", "docs/screenshots"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    pg.goto(WEB); pg.wait_for_selector(".cluster"); pg.wait_for_timeout(600)
    pg.screenshot(path=f"{OUT}/dashboard-overview.png")
    pg.screenshot(path=f"{OUT}/dashboard-full.png", full_page=True)
    pg.locator(".grid2").first.screenshot(path=f"{OUT}/clusters-segments.png")
    form = pg.locator(".assign")
    inputs = form.locator("input")
    inputs.nth(0).fill("200"); inputs.nth(1).fill("2"); inputs.nth(2).fill("350")
    form.locator("button").click(); pg.wait_for_selector(".result")
    pg.locator(".grid2").nth(1).screenshot(path=f"{OUT}/assign-customer.png")
    pg.locator(".heat").screenshot(path=f"{OUT}/cohort-retention.png")
    pg.goto(f"{API}/docs"); pg.wait_for_selector(".opblock"); pg.wait_for_timeout(500)
    pg.screenshot(path=f"{OUT}/api-docs.png")
    b.close()

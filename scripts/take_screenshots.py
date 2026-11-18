"""Captures application screenshots for the report -> report/figures/ui_*.png (app must run on :8000)"""
from playwright.sync_api import sync_playwright

URL, OUT = "http://localhost:8000/", "report/figures"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
    pg.goto(URL); pg.wait_for_timeout(2500)
    def shot(name, clip_full=False):
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
        pg.screenshot(path=f"{OUT}/ui_{name}.png", full_page=clip_full); print("saved", name)
    pg.evaluate("loadCropPreset('rice')"); pg.wait_for_timeout(2000); shot("crop")
    pg.evaluate("switchTab('fertilizer')"); pg.evaluate("loadFertPreset('wheat')"); pg.wait_for_timeout(2000); shot("fertilizer")
    pg.evaluate("switchTab('geo')"); pg.wait_for_timeout(2500)
    pg.evaluate("selectGeoLocation('thanjavur')"); pg.wait_for_timeout(5000); shot("satellite")
    pg.evaluate("switchTab('crop')"); pg.evaluate("loadCropPreset('rice')"); pg.wait_for_timeout(1500)
    pg.evaluate("syncSoilReportLive()"); pg.evaluate("switchTab('report')"); pg.wait_for_timeout(2500); shot("report")
    pg.evaluate("switchTab('data')"); pg.wait_for_timeout(2500); shot("dataset")
    b.close()

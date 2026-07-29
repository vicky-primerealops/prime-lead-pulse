import time
import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError

# --- CONFIGURATION ---
URL = "https://matrix.beachesmls.com/"
EMAIL = "Support@homelystic.com"
PASSWORD = "Onepiece@1234#!"
EXPORT_FORMAT_NAME = "LA" 
DATE_CHUNKS = ["07/25/2025-07/31/2025"] # Just testing one chunk for diagnostic

def run_bot():
    print("Starting Diagnostic Bot...", flush=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Run invisibly so it doesn't disturb user
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(10000)
        
        try:
            print("Navigating to Beaches MLS...", flush=True)
            page.goto(URL)
            page.screenshot(path="debug_1_start.png")
            
            print("Looking for Email radio button...", flush=True)
            page.get_by_text("Email", exact=True).click()
            time.sleep(1)
            
            print("Entering credentials...", flush=True)
            page.locator("input[type='email'], input[type='text']").first.fill(EMAIL)
            page.locator("input[type='password']").first.fill(PASSWORD)
            
            print("Clicking Login...", flush=True)
            page.get_by_role("button", name="LOG IN", exact=True).click()
            page.wait_for_load_state("networkidle")
            page.screenshot(path="debug_2_after_login.png")
            
            print("Checking for pop-ups...", flush=True)
            try:
                page.locator("a, button").filter(has_text="Read Later").click(timeout=2000)
            except: pass
            
            print("Navigating to Search > Quick...", flush=True)
            page.get_by_text("Search", exact=True).hover(timeout=5000)
            page.get_by_text("Quick", exact=True).click(timeout=5000)
            page.wait_for_load_state("networkidle")
            page.screenshot(path="debug_3_search_page.png")
            
            print("SUCCESS! DIAGNOSTIC COMPLETE.", flush=True)
            
        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            page.screenshot(path="debug_error.png")
            print("Saved debug_error.png", flush=True)

if __name__ == "__main__":
    run_bot()

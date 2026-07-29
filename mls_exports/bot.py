import time
import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError

# --- CONFIGURATION ---
URL = "https://matrix.beachesmls.com/"
EMAIL = "Support@homelystic.com"
PASSWORD = "Onepiece@1234#!"
EXPORT_FORMAT_NAME = "LA" # The name of your custom export format

# The 13 date chunks to cover the last 12 months
DATE_CHUNKS = [
    "07/25/2025-07/31/2025",
    "08/01/2025-08/31/2025",
    "09/01/2025-09/30/2025",
    "10/01/2025-10/31/2025",
    "11/01/2025-11/30/2025",
    "12/01/2025-12/31/2025",
    "01/01/2026-01/31/2026",
    "02/01/2026-02/28/2026",
    "03/01/2026-03/31/2026",
    "04/01/2026-04/30/2026",
    "05/01/2026-05/31/2026",
    "06/01/2026-06/30/2026",
    "07/01/2026-07/25/2026"
]

STATUSES_TO_PULL = ["Closed", "Active", "Pending"]

EXPORT_FOLDER = os.path.join(os.getcwd(), "mls_exports")
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def run_bot():
    print(f"Starting Ultimate Autonomous Bot. Files will be saved to: {EXPORT_FOLDER}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(15000)
        
        # 1. LOGIN SEQUENCE
        print("Navigating to Beaches MLS...")
        page.goto(URL)
        
        try:
            print("Looking for Email radio button...")
            page.get_by_text("Email", exact=True).click(timeout=10000)
            time.sleep(1)
            
            print("Entering credentials...")
            page.locator("input[type='email'], input[type='text']").first.fill(EMAIL)
            page.locator("input[type='password']").first.fill(PASSWORD)
            
            print("Pressing Enter to Login...")
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Login sequence skipped or failed: {e}")
        
        # 2. BYPASS POPUPS
        print("Checking for pop-ups...")
        for _ in range(2):
            try:
                page.locator("a, button").filter(has_text="Read Later").click(timeout=2000)
            except: pass
            try:
                page.locator("a, button").filter(has_text="I Agree").click(timeout=2000)
            except: pass

        # 3. NAVIGATE TO SEARCH
        print("Navigating to Search > Quick directly...")
        try:
            page.goto("https://matrix.beachesmls.com/Matrix/Search/CrossProperty/Quick")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        except Exception as e:
            print(f"\n[!] Navigation error: {e}")
            print("Please navigate to the Search criteria page manually.")
            input("Press ENTER here once you see the Criteria page...")

        # 4. START EXTRACTION LOOP
        # Identify the main frame (Matrix puts the search form inside a frame)
        time.sleep(3)
        frame = page.frames[1] if len(page.frames) > 1 else page.main_frame
        
        for status in STATUSES_TO_PULL:
            print(f"\n=============================================")
            print(f"STARTING BATCH FOR STATUS: {status.upper()}")
            print(f"=============================================")
            
            for date_range in DATE_CHUNKS:
                print(f"\n---> Processing: {status} | {date_range}")
                
                try:
                    # Make sure we are on Criteria tab (might fail if already active or hidden)
                    try:
                        criteria_tab = frame.locator("a, li").filter(has_text="Criteria").first
                        criteria_tab.click(timeout=3000)
                        time.sleep(1)
                    except TimeoutError:
                        pass
                    
                    # Click the "Clear" button at the bottom left to wipe previous search
                    clear_btn = frame.locator("a, button, span").filter(has_text="Clear").first
                    clear_btn.click(timeout=3000)
                    time.sleep(2)
                    
                    # Uncheck all statuses first
                    print("Clearing default statuses...")
                    # Usually there is a "Select None" link next to statuses in Matrix
                    try:
                        frame.get_by_text("Select None", exact=True).click(timeout=2000)
                    except:
                        # Fallback: find all checked checkboxes in the status area and uncheck them
                        pass 
                    
                    # Check our target status and fill its date box
                    print(f"Selecting '{status}' and entering date: {date_range}...")
                    
                    # Matrix structure: a checkbox next to a label, and a textbox nearby.
                    # We will use JavaScript injection to precisely find the textbox next to the status label.
                    js_code = f"""
                    () => {{
                        let labels = Array.from(document.querySelectorAll('label, span, td, div'));
                        let targetLabel = labels.find(el => el.textContent.trim() === '{status}');
                        if (!targetLabel) return 'Label not found';
                        
                        // Find the closest parent container (usually a row)
                        let parent = targetLabel.closest('tr') || targetLabel.closest('div');
                        if (!parent) return 'Parent not found';
                        
                        // Check the checkbox
                        let checkbox = parent.querySelector('input[type="checkbox"]');
                        if (checkbox && !checkbox.checked) checkbox.click();
                        
                        // Fill the date input
                        let dateInput = parent.querySelector('input[type="text"]');
                        if (dateInput) {{
                            dateInput.value = '{date_range}';
                            // Trigger change events so Matrix registers it
                            dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            dateInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                            return 'Success';
                        }}
                        return 'Date input not found';
                    }}
                    """
                    result = frame.evaluate(js_code)
                    if result != 'Success':
                        print(f"Failed to set status/date via JS: {result}")
                        print("Please set it manually and press ENTER.")
                        input("Press ENTER to continue...")
                    
                    time.sleep(2)
                    
                    # Click Results
                    print("Clicking Results...")
                    frame.locator(".m_btnResults, a:has-text('Results'), button:has-text('Results')").last.click()
                    time.sleep(5)
                    
                    # Check if there are results
                    # Sometimes matrix shows "0 matches" or throws an alert
                    
                    # Check All
                    print("Selecting all results...")
                    try:
                        # Top-left checkbox in the results grid is usually Check All
                        frame.locator("input[type='checkbox']").first.check(timeout=3000)
                    except:
                        # Matrix has a link for "All"
                        frame.get_by_text("All", exact=True).first.click(timeout=3000)
                        
                    # Click Export
                    print("Opening Export Menu...")
                    frame.locator("a, button, span").filter(has_text="Export").last.click()
                    time.sleep(2)
                    
                    # Select Format
                    print(f"Selecting Format: {EXPORT_FORMAT_NAME}...")
                    try:
                        frame.locator("select").last.select_option(label=EXPORT_FORMAT_NAME)
                    except:
                        try:
                            frame.locator("select").last.select_option(value=EXPORT_FORMAT_NAME)
                        except:
                            print("Could not select the LA format automatically. Please select it in the dropdown.")
                            
                    # Download
                    print("Downloading file...")
                    with page.expect_download(timeout=45000) as download_info:
                        frame.locator("a, button").filter(has_text="Export").last.click()
                        
                    download = download_info.value
                    filename = f"MLS_Export_{status}_{date_range.replace('/','-')}.csv"
                    filepath = os.path.join(EXPORT_FOLDER, filename)
                    download.save_as(filepath)
                    print(f"Saved: {filename}")
                    
                except Exception as e:
                    print(f"\n[!] Error processing {status} | {date_range}: {str(e)}")
                    print("Please get the bot back to the Criteria screen, or hit CTRL+C to stop.")
                    input("> Press ENTER to attempt the next batch...")

        print("\n*** ALL CHUNKS COMPLETED! ***")
        time.sleep(5)

if __name__ == "__main__":
    run_bot()

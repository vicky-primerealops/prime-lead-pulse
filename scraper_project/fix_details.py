import asyncio
from playwright.async_api import async_playwright
import csv
import time
import random
import os

async def main():
    input_file = 'houzeo_mls_data_full.csv'
    output_file = 'houzeo_mls_data_fixed.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Read the existing data
    all_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_data = list(reader)
        fieldnames = reader.fieldnames

    if not all_data:
        print("No data found in the CSV.")
        return

    print(f"Loaded {len(all_data)} records from {input_file}.")

    # Create output file and write header immediately
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        print("="*50)
        print("ACTION REQUIRED:")
        print("1. A browser window will open.")
        print("2. Please log in to your Houzeo Dashboard.")
        print("3. ONCE YOU ARE LOGGED IN AND ON THE DASHBOARD, press Enter in this terminal.")
        print("="*50)
        
        await page.goto("https://www.houzeo.com/")
        input("\nPress Enter here ONLY AFTER you are logged in...\n")

        print("Resuming extraction of details...")
        
        for i, record in enumerate(all_data):
            # If the row doesn't have an edit URL, we skip
            edit_url = record.get('edit_url')
            if not edit_url or edit_url.strip() == '':
                # Save as is
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    csv.DictWriter(f, fieldnames=fieldnames).writerow(record)
                continue

            if edit_url.startswith('/'):
                edit_url = f"https://www.houzeo.com{edit_url}"

            print(f"[{i+1}/{len(all_data)}] Fetching details for {record.get('MLS Name', 'Unknown')}...")
            
            # Add a small delay to prevent being flagged
            delay = random.uniform(2.5, 4.0)
            await asyncio.sleep(delay)
            
            detail_page = await context.new_page()
            try:
                await detail_page.goto(edit_url, wait_until='networkidle')
                await detail_page.wait_for_timeout(2000) # Give UI time to render Select2 tags

                # Advanced extractor script
                extractor_js = """
                (fieldName) => {
                    const labels = Array.from(document.querySelectorAll('label'));
                    const targetLabel = labels.find(l => l.textContent.trim().includes(fieldName));
                    
                    if (!targetLabel) return '';
                    
                    const parent = targetLabel.parentElement;
                    
                    // For Counties and Cities
                    if (fieldName.includes('Counties') || fieldName.includes('Cities')) {
                        // 1. Standard select
                        const select = parent.querySelector('select');
                        if (select && select.selectedOptions && select.selectedOptions.length > 0) {
                            let res = Array.from(select.selectedOptions).map(o => o.text.trim());
                            res = res.filter(t => t && !t.includes('Cities') && !t.includes('Select'));
                            if (res.length > 0) return [...new Set(res)].join(', ');
                        }
                        
                        // 2. Select2 chips
                        const grandParent = parent.parentElement;
                        let chips = parent.querySelectorAll('.select2-selection__choice');
                        if (chips.length === 0 && grandParent) {
                            chips = grandParent.querySelectorAll('.select2-selection__choice');
                        }
                        
                        let res = [];
                        if (chips.length > 0) {
                            let leafChips = Array.from(chips).filter(c => c.querySelectorAll('.select2-selection__choice').length === 0);
                            res = leafChips.map(c => {
                                if (c.title) return c.title.trim();
                                let clone = c.cloneNode(true);
                                let closes = clone.querySelectorAll('[class*="remove"], [class*="close"], span');
                                closes.forEach(el => el.remove());
                                return clone.textContent.replace('×', '').replace('x', '').trim();
                            });
                        }
                        // 3. Fallback
                        else {
                            let fallbackChips = parent.querySelectorAll('[class*="choice"], [class*="tag"], [class*="chip"]');
                            if (fallbackChips.length > 0) {
                                res = Array.from(fallbackChips).map(c => c.textContent.replace('×', '').trim());
                            }
                        }
                        
                        // BULLETPROOF TEXT FILTERING
                        if (res.length > 0) {
                            // 1. Remove placeholders
                            let cleanRes = res.filter(t => t && !t.toLowerCase().includes('cities') && !t.toLowerCase().includes('select'));
                            
                            // 2. Deduplicate exact matches
                            let finalRes = [...new Set(cleanRes)];
                            
                            // 3. Remove merged container strings (e.g. "County A County B")
                            // If a string contains at least TWO other distinct strings from the list, it's a merged container.
                            finalRes = finalRes.filter(str => {
                                let containedCount = finalRes.filter(other => other !== str && str.includes(other)).length;
                                return containedCount < 2;
                            });
                            
                            return finalRes.join(', ');
                        }
                    } 
                    // For Input fields
                    else {
                        const input = parent.querySelector('input');
                        if (input) return input.value;
                        
                        if (targetLabel.nextElementSibling && targetLabel.nextElementSibling.tagName === 'INPUT') {
                            return targetLabel.nextElementSibling.value;
                        }
                    }
                    
                    return '';
                }
                """
                
                # Re-extract the fields
                counties = await detail_page.evaluate(extractor_js, "Choose Counties")
                if counties: record['Detail_Counties'] = counties
                
                included = await detail_page.evaluate(extractor_js, "Only Cities Included")
                if included: record['Detail_Cities_Included'] = included
                
                excluded = await detail_page.evaluate(extractor_js, "Only Cities Excluded")
                if excluded: record['Detail_Cities_Excluded'] = excluded
                
                login_link = await detail_page.evaluate(extractor_js, "MLS Login Link")
                if login_link: record['Detail_MLS_Login_Link'] = login_link
                
                checklist = await detail_page.evaluate(extractor_js, "MLS Checklist")
                if checklist: record['Detail_Checklist'] = checklist

            except Exception as e:
                print(f"Error scraping {record.get('MLS Name')}: {e}")
            finally:
                await detail_page.close()
                
            # Write row to output file immediately so progress is saved
            with open(output_file, 'a', newline='', encoding='utf-8') as f:
                csv.DictWriter(f, fieldnames=fieldnames).writerow(record)
                
        print(f"\nSUCCESS: All missing details have been extracted and saved to {output_file}!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

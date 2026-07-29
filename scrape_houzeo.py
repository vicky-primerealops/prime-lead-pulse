import asyncio
from playwright.async_api import async_playwright
import csv
import time
import random

async def main():
    async with async_playwright() as p:
        # Launch browser in headed mode so you can see it and log in
        # Slow_mo helps ensure clicks and navigation register properly
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        print("="*50)
        print("ACTION REQUIRED:")
        print("1. A browser window will open. Please log in to your Houzeo Dashboard.")
        print("2. Navigate to the 'MLS Coverage Master' page where the list of 506 MLSs is.")
        print("3. Ensure the list page is fully loaded.")
        print("4. ONCE YOU ARE ON THE PAGE, press Enter in this terminal to start scraping.")
        print("="*50)
        
        # We start at the login page or main page
        await page.goto("https://www.houzeo.com/")
        
        # Wait for user to log in and navigate to the list page manually
        input("\nPress Enter here ONLY AFTER you are on the MLS Coverage Master list page...\n")

        print("Starting list scraping...")
        all_data = []
        previous_first_row_id = None

        # Scrape the main list with pagination
        current_page = 1
        while current_page <= 100:  # Hard limit to prevent infinite loops
            print(f"Scraping page {current_page} of the list...")
            
            # Wait for the table rows to be present
            await page.wait_for_selector('table tbody tr')
            await page.wait_for_timeout(2000) # Give it an extra moment to render fully
            
            rows = await page.locator('table tbody tr').all()
            
            page_data = []
            for row in rows:
                tds = await row.locator('td').all()
                if len(tds) < 15:
                    continue # Skip invalid rows
                    
                row_info = {
                    'Sr. No': await tds[0].inner_text(),
                    'MLS Name': await tds[1].inner_text(),
                    'State': await tds[2].inner_text(),
                    'List_Counties': await tds[3].inner_text(),
                    'List_Included_Cities': await tds[4].inner_text(),
                    'List_Excluded_Cities': await tds[5].inner_text(),
                    'List_MLS_Login_Link': await tds[6].inner_text(),
                    'List_Checklist': await tds[8].inner_text(),
                    'Commission': await tds[11].inner_text(),
                }
                
                # Get the edit link from the Actions column (usually the 15th column)
                edit_link_locator = tds[14].locator('a').first
                if await edit_link_locator.count() > 0:
                    row_info['edit_url'] = await edit_link_locator.get_attribute('href')
                else:
                    row_info['edit_url'] = None
                    
                page_data.append(row_info)
                
            if not page_data:
                print("No data found on this page. Stopping list scrape.")
                break
                
            # Check if the page actually changed by looking at the first row's Serial No
            current_first_row_id = page_data[0]['Sr. No']
            if current_first_row_id == previous_first_row_id:
                print("Reached the end of the list (page data didn't change). Moving on...")
                break
            previous_first_row_id = current_first_row_id
                
            all_data.extend(page_data)
            print(f"Extracted {len(page_data)} records from page {current_page}.")
            
            # Look for the 'Next' button
            # We look for an element with text Next. Usually pagination has class 'next' or similar.
            next_button = page.locator('a:has-text("Next"), li.next a, button:has-text("Next")').last
            
            if await next_button.count() > 0:
                # Check if it's disabled (e.g. at the end of the list)
                is_disabled = await next_button.evaluate('el => el.hasAttribute("disabled") || el.parentElement.classList.contains("disabled")')
                if not is_disabled:
                    print("Navigating to next page...")
                    # Human-like hesitation before clicking next
                    await asyncio.sleep(random.uniform(1.5, 3.5))
                    await next_button.click()
                    # Wait for table to update (assuming first row's SR No changes or just wait)
                    await page.wait_for_timeout(3000) 
                    current_page += 1
                else:
                    print("Reached the last page.")
                    break
            else:
                print("No 'Next' button found. Stopping list scraping.")
                break
                
        print(f"\nFinished scraping list. Total records found: {len(all_data)}")
        print("Now navigating to individual MLS pages to extract detailed fields...")
        
        # Now visit each edit page to get the specific details requested
        for i, record in enumerate(all_data):
            if not record.get('edit_url'):
                print(f"Skipping {record.get('MLS Name')} - No edit link found.")
                continue
                
            edit_url = record['edit_url']
            
            # Make sure the URL is absolute
            if edit_url.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(page.url)
                edit_url = f"{parsed_url.scheme}://{parsed_url.netloc}{edit_url}"
                
            print(f"[{i+1}/{len(all_data)}] Visiting details for {record['MLS Name']}...")
            
            # Human-like delay between profile visits to prevent getting flagged
            delay = random.uniform(2.5, 5.0)
            print(f"Resting for {delay:.1f} seconds to simulate human reading...")
            await asyncio.sleep(delay)
            
            detail_page = await context.new_page()
            try:
                await detail_page.goto(edit_url, wait_until='networkidle')
                await detail_page.wait_for_timeout(2000) # Ensure fields populate
                
                # JavaScript to extract selected tags from multiple select elements
                # It finds a label with specific text, then looks for the next element that contains the selected chips
                extract_script = """
                (labelText) => {
                    // Find the label
                    const labels = Array.from(document.querySelectorAll('label'));
                    const targetLabel = labels.find(l => l.textContent.includes(labelText));
                    if (!targetLabel) return '';
                    
                    // The container is usually a parent or sibling. 
                    // Let's search the parent's parent for selected choices (like select2)
                    const container = targetLabel.parentElement.parentElement;
                    if (!container) return '';
                    
                    // Look for standard selected options in case it's a normal select
                    const select = container.querySelector('select');
                    if (select && select.selectedOptions && select.selectedOptions.length > 0) {
                        return Array.from(select.selectedOptions).map(o => o.text.trim()).join(', ');
                    }
                    
                    // Look for chips/tags UI (like select2)
                    const chips = container.querySelectorAll('.select2-selection__choice, li.search-choice, .chip, .tag');
                    if (chips.length > 0) {
                        return Array.from(chips).map(c => c.textContent.replace('×', '').replace('x', '').trim()).join(', ');
                    }
                    
                    return '';
                }
                """
                
                # 1. Counties selected
                record['Detail_Counties'] = await detail_page.evaluate(extract_script, "Choose Counties")
                
                # 2. Only Cities Included
                record['Detail_Cities_Included'] = await detail_page.evaluate(extract_script, "Only Cities Included")
                
                # 3. Only Cities Excluded
                record['Detail_Cities_Excluded'] = await detail_page.evaluate(extract_script, "Only Cities Excluded")
                
                # 4. MLS Login Link
                login_link = await detail_page.evaluate("""
                    () => {
                        const labels = Array.from(document.querySelectorAll('label'));
                        const label = labels.find(l => l.textContent.includes("MLS Login Link"));
                        if (label && label.nextElementSibling && label.nextElementSibling.tagName === 'INPUT') {
                            return label.nextElementSibling.value;
                        }
                        // Fallback selector
                        const input = document.querySelector('input[name*="login_link"], input[placeholder*="Login Link"]');
                        return input ? input.value : '';
                    }
                """)
                record['Detail_MLS_Login_Link'] = login_link

                # 5. MLS Checklist
                checklist = await detail_page.evaluate("""
                    () => {
                        const labels = Array.from(document.querySelectorAll('label'));
                        const label = labels.find(l => l.textContent.includes("MLS Checklist"));
                        if (label && label.nextElementSibling && label.nextElementSibling.tagName === 'INPUT') {
                            return label.nextElementSibling.value;
                        }
                        // Fallback selector
                        const input = document.querySelector('input[name*="checklist"], input[placeholder*="Checklist"]');
                        return input ? input.value : '';
                    }
                """)
                record['Detail_Checklist'] = checklist
                
            except Exception as e:
                print(f"Error scraping {record['MLS Name']}: {e}")
            finally:
                await detail_page.close()
                
        # Save results
        if all_data:
            filename = 'houzeo_mls_data_full.csv'
            keys = all_data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_data)
            print(f"\nSUCCESS: Data saved to {filename}")
        else:
            print("\nNo data was collected.")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

import csv
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def safe_get(driver, url, max_retries=5):
    for attempt in range(max_retries):
        try:
            driver.get(url)
            # Fast check for Cloudflare 502 Bad Gateway
            if "502" in driver.title or "504" in driver.title or "Bad gateway" in driver.title.lower():
                raise Exception("502/504 Bad Gateway detected in title")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 15 * (attempt + 1)
                print(f"Connection error or Bad Gateway loading {url}: {e}. Waiting {wait_time}s and retrying {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                print(f"Failed to load {url} after {max_retries} retries.")
                raise Exception("Fatal block/timeout detected. Halting script to prevent skipping data.")

def get_agent_details(driver, agent_url):
    """
    Visits an individual agent's profile page and extracts their detailed information.
    """
    if not safe_get(driver, agent_url):
        raise Exception("Failed to load agent URL")
    
    # Wait for the main profile container to load (e.g., waiting for the name to appear)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(@class, 'agent-name')] | //*[contains(text(), 'About Me')]"))
            )
            break
        except TimeoutException:
            if attempt < max_retries - 1:
                wait_time = 15 * (attempt + 1)
                print(f"Timeout loading agent page: {agent_url}. Server might be rate-limiting. Waiting {wait_time}s and retrying {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                driver.refresh()
            else:
                print(f"Failed to load agent page after retries: {agent_url}")
                raise Exception("Fatal block/timeout detected on profile page. Halting script to prevent skipping data.")

    # Simulate human reading/scrolling to build trust with Cloudflare
    try:
        driver.execute_script(f"window.scrollTo(0, {random.randint(300, 800)});")
        time.sleep(random.uniform(1.0, 2.0))
        driver.execute_script(f"window.scrollTo(0, {random.randint(800, 1500)});")
    except Exception:
        pass
    
    time.sleep(random.uniform(4.0, 8.0))  # Increased randomized delay for rate-limit mitigation

    def safe_get_text(by, selector):
        try:
            return driver.find_element(by, selector).text.strip()
        except NoSuchElementException:
            return ""

    def safe_get_attribute(by, selector, attribute):
        try:
            return driver.find_element(by, selector).get_attribute(attribute)
        except NoSuchElementException:
            return ""

    agent_data = {'URL': agent_url}
    
    # 1. Name
    name = safe_get_text(By.XPATH, "//h1")
    if not name:
        name = safe_get_text(By.XPATH, "//div[contains(@class, 'name') or contains(@class, 'title')]")
    agent_data['Name'] = name

    # 2. License Number
    agent_data['License'] = safe_get_text(By.XPATH, "//*[contains(text(), 'License #')]")

    # 3. Phone Number
    agent_data['Phone'] = safe_get_text(By.XPATH, "//a[contains(@href, 'tel:')]")

    # 4. Email
    agent_data['Email'] = safe_get_text(By.XPATH, "//a[contains(@href, 'mailto:')]")

    # 5. Website
    agent_data['Website'] = safe_get_attribute(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'kw.com'))]", "href")

    # 6. Location / Market Center
    agent_data['Location'] = safe_get_text(By.XPATH, "//*[contains(@class, 'location') or contains(text(), ', TX')]")
    
    # 7. Languages
    try:
        lang_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Languages')]/following-sibling::*")
        agent_data['Languages'] = lang_element.text.strip()
    except NoSuchElementException:
        agent_data['Languages'] = ""

    return agent_data


def scrape_kw_directory(base_url, max_pages=None):
    """
    Navigates the main directory list, finds agent profile links, and paginates through results.
    """
    # Setup Chrome options for undetected_chromedriver
    options = uc.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    # Add a random User-Agent to avoid fingerprinting
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Setting version_main=150 to match your current Chrome browser version
    driver = uc.Chrome(options=options, version_main=150)
    driver.maximize_window()
    driver.set_page_load_timeout(45)
    
    all_agents_data = []
    
    import os
    start_page = 1
    if os.path.exists("scraper_state.txt"):
        try:
            with open("scraper_state.txt", "r") as f:
                start_page = int(f.read().strip())
                print(f"Resuming from page {start_page}...")
        except Exception:
            pass

    if start_page > 1:
        current_list_url = f"{base_url}?page={start_page}"
    else:
        current_list_url = base_url

    # Navigate to the starting directory page
    if not safe_get(driver, current_list_url):
        print("Fatal error: Could not load the initial directory page.")
        return all_agents_data
    
    time.sleep(random.uniform(3, 6))
    
    # Create a dedicated tab for profile scraping to avoid driver.close() bugs
    main_window = driver.current_window_handle
    driver.switch_to.new_window('tab')
    profile_window = driver.current_window_handle
    driver.switch_to.window(main_window)
    page = start_page
    while True:
        # Always ensure we are on the main list tab when starting a new page loop
        driver.switch_to.window(main_window)
        print(f"--- Scraping List Page {page} ---")
        
        max_retries = 3
        list_loaded = False
        for attempt in range(max_retries):
            try:
                # Wait for agent cards or links to load on the list page
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/agent/')]"))
                )
                list_loaded = True
                break
            except TimeoutException:
                if attempt < max_retries - 1:
                    wait_time = 15 * (attempt + 1)
                    print(f"Timeout loading list page {page}. Waiting {wait_time}s and retrying {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    driver.refresh()
                else:
                    break
        
        if not list_loaded:
            print("Could not find agent cards on this page after multiple retries. Assuming end of directory or fatal error.")
            break
            
        time.sleep(random.uniform(2.5, 4.5)) # Extra buffer for complete rendering with randomized delay
        
        # 1. Collect all agent profile links on the current list page
        agent_links = []
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/agent/')]")
        for link in links:
            href = link.get_attribute('href')
            if href and "kw.com" in href and "/agent/" in href and href not in agent_links:
                agent_links.append(href)
                
        print(f"Found {len(agent_links)} agent profiles on page {page}.")
        
        # 2. Open each agent profile in the dedicated profile tab
        for idx, link in enumerate(agent_links):
            print(f"[{idx+1}/{len(agent_links)}] Scraping Profile: {link}")
            
            # Switch to the dedicated profile tab and navigate
            driver.switch_to.window(profile_window)
            
            try:
                data = get_agent_details(driver, link)
                if data:
                    all_agents_data.append(data)
            except Exception as e:
                print(f"FATAL ERROR during scraping: {e}")
                print("Halting script so no agents are skipped. Run the script again to resume from this page.")
                driver.quit()
                return all_agents_data
                
            # Be polite to the server with a randomized delay
            time.sleep(random.uniform(5.0, 10.0))
            
        # Save progress and state after every page
        if all_agents_data:
            save_to_csv(all_agents_data, "kw_agents_data.csv", append=True)
            all_agents_data = [] # Reset memory
        with open("scraper_state.txt", "w") as f:
            f.write(str(page + 1))
            
        # Switch back to the main list tab to prepare for clicking Next
        driver.switch_to.window(main_window)
            
        # 3. Navigate to the next page directly via URL
        if max_pages and page >= max_pages:
            break
            
        try:
            # Check if there are no agents on this page (meaning we've gone past the last page)
            if len(agent_links) == 0:
                print("No agents found on this page. Assuming we reached the end of the directory.")
                break
                
            # If we successfully scraped agents, forcefully inject the next page number into the URL
            page += 1
            
            # Safely parse and update the URL query parameters
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed_url = urlparse(current_list_url)
            query_params = parse_qs(parsed_url.query)
            query_params['page'] = [str(page)]
            new_query = urlencode(query_params, doseq=True)
            current_list_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))
            
            print(f"Navigating directly to: {current_list_url}")
            if not safe_get(driver, current_list_url):
                print("Failed to navigate to next page.")
                break
            
            # Wait for the next page to initiate loading
            time.sleep(random.uniform(4.0, 7.0))
            
        except Exception as e:
            print(f"Error trying to navigate to the next page: {e}")
            break
            
    try:
        driver.quit()
    except Exception:
        pass


def save_to_csv(data, filename, append=False):
    import os
    if not data:
        return
        
    keys = data[0].keys()
    mode = 'a' if append else 'w'
    write_header = not append or not os.path.exists(filename)
    
    with open(filename, mode, newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if write_header:
            dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Successfully saved {len(data)} agent records to {filename}")


if __name__ == "__main__":
    TARGET_START_URL = "https://www.kw.com/agents" 
    PAGES_TO_SCRAPE = None # Set to None to scrape all available pages
    OUTPUT_FILE = "kw_agents_data.csv"
    
    print("Starting KW Agent Scraping Job...")
    scraped_data = scrape_kw_directory(TARGET_START_URL, PAGES_TO_SCRAPE)
    save_to_csv(scraped_data, OUTPUT_FILE)

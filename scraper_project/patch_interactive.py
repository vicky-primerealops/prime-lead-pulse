import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add get_all_cities_for_state function
city_fetcher_code = """
def get_all_cities_for_state(state_abbr):
    print(f"  [+] Fetching comprehensive list of cities for {state_abbr.upper()} from US database...")
    import urllib.request
    import csv
    url = "https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv"
    cities = []
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                if row['STATE_CODE'].lower() == state_abbr.lower():
                    cities.append(row['CITY'])
        cities = sorted(list(set(cities)))
        print(f"  [+] Discovered {len(cities)} unique cities in {state_abbr.upper()}!")
    except Exception as e:
        print(f"  [!] Error fetching cities: {e}")
    return cities

def main():"""

content = content.replace("def main():", city_fetcher_code)

# 2. Modify main() to ask for input
old_main_top = """def main():
    print("=" * 70)
    print("  ZILLOW REAL ESTATE AGENT SCRAPER")
    print(f"  States: {', '.join(STATES_TO_SCRAPE.keys())}")
    print("=" * 70)
    print()
    print("  [WARNING]  Keep the browser window VISIBLE (not minimized).")
    print("     The CAPTCHA solver needs to control the mouse cursor.")
    print("     You can use other windows, just don't minimize the browser.")
    print()

    progress = load_progress()
    scraped_urls = get_scraped_urls()
    completed = progress.get("completed_cities", [])

    print(f"  Already scraped: {len(scraped_urls)} agents in CSV")
    print(f"  Completed cities: {len(completed)}")
    print()

    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:

        for state_name, state_abbr in STATES_TO_SCRAPE.items():
            cities = list(CITIES.get(state_abbr, []))"""

new_main_top = """def main():
    print("=" * 70)
    print("  ZILLOW REAL ESTATE AGENT SCRAPER")
    print("=" * 70)
    print()
    
    # INTERACTIVE PROMPT
    state_abbr = input("  Enter State Abbreviation to scrape (e.g., AL, IL, TX): ").strip().lower()
    if not state_abbr:
        print("  Invalid state abbreviation. Exiting.")
        return
        
    state_name = input("  Enter State Full Name (e.g., Alabama, Illinois): ").strip().title()
    if not state_name:
        state_name = state_abbr.upper()

    print()
    print("  [WARNING]  Keep the browser window VISIBLE (not minimized).")
    print("     The CAPTCHA solver needs to control the mouse cursor.")
    print("     You can use other windows, just don't minimize the browser.")
    print()

    progress = load_progress()
    scraped_urls = get_scraped_urls()
    completed = progress.get("completed_cities", [])

    print(f"  Already scraped: {len(scraped_urls)} agents in CSV")
    print(f"  Completed cities: {len(completed)}")
    print()

    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        # We only do one state per run now based on user input
        STATES_TO_SCRAPE_DYNAMIC = {state_name: state_abbr}
        
        for state_name, state_abbr in STATES_TO_SCRAPE_DYNAMIC.items():
            # Dynamically fetch ALL cities instead of relying on hardcoded list
            cities = get_all_cities_for_state(state_abbr)
            if not cities:
                # Fallback to hardcoded if fetch fails
                cities = list(CITIES.get(state_abbr, []))
"""

if "def main():" in content: # It might have been modified by the previous replacement, wait!
    pass # I already replaced "def main():" with the new function + "def main():"
    # So I need to replace the old main top with the new main top.
    
    # Actually let's just do a targeted regex or simple replace
    content = content.replace("""    print("=" * 70)
    print("  ZILLOW REAL ESTATE AGENT SCRAPER")
    print(f"  States: {', '.join(STATES_TO_SCRAPE.keys())}")""", """    print("=" * 70)
    print("  ZILLOW REAL ESTATE AGENT SCRAPER")""")
    
    content = content.replace("""    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:

        for state_name, state_abbr in STATES_TO_SCRAPE.items():
            cities = list(CITIES.get(state_abbr, []))""", """    
    # INTERACTIVE PROMPT
    state_abbr = input("  Enter State Abbreviation to scrape (e.g., AL, IL, TX): ").strip().lower()
    if not state_abbr:
        print("  Invalid state abbreviation. Exiting.")
        return
        
    state_name = input("  Enter State Full Name (e.g., Alabama, Illinois): ").strip().title()
    if not state_name:
        state_name = state_abbr.upper()
        
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:

        STATES_TO_SCRAPE_DYNAMIC = {state_name: state_abbr}
        
        for state_name, state_abbr in STATES_TO_SCRAPE_DYNAMIC.items():
            cities = get_all_cities_for_state(state_abbr)
            if not cities:
                cities = list(CITIES.get(state_abbr, []))""")

with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Applied interactive prompt and dynamic city fetching.")

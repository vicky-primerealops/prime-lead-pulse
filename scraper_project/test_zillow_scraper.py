"""
Quick test of the Zillow scraper on a single small city (Auburn, AL).
Scrapes just 1 page and visits up to 3 agent profiles.
"""
import sys
import os

# Patch the config before importing main
import Zillow_Agents_Scraper as scraper

# Override config for testing
scraper.STATES_TO_SCRAPE = {"Alabama": "al"}
scraper.CITIES = {"al": ["Auburn"]}
scraper.MAX_PAGES_PER_CITY = 1
scraper.BATCH_SAVE_SIZE = 3
scraper.OUTPUT_FILE = "zillow_test_output.csv"
scraper.STATE_FILE = "zillow_test_state.json"
scraper.DELAY_BETWEEN_PROFILES = (5, 8)  # Slightly faster for testing

# Clean up previous test files
for f in [scraper.OUTPUT_FILE, scraper.STATE_FILE]:
    if os.path.exists(f):
        os.remove(f)

print("=" * 60)
print("  TEST RUN: Auburn, AL — 1 page, up to 3 profiles")
print("=" * 60)

# Monkey-patch to limit profile visits to 3
original_main = scraper.main

def test_main():
    """Modified main that caps profile visits at 3."""
    from seleniumbase import SB
    import time
    import random

    progress = scraper.load_progress()
    scraped_urls = scraper.get_scraped_urls()

    print(f"\n  Testing with SeleniumBase UC mode...\n")

    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        state_abbr = "al"
        city = "Auburn"
        city_slug = scraper.slugify_city(city, state_abbr)
        city_url = f"{scraper.BASE_URL}/{city_slug}/"
        location_str = f"{city}, {state_abbr.upper()}"

        print(f"  Step 1: Loading listing page: {city_url}")
        if not scraper.safe_open(sb, city_url):
            print("  FAILED to load listing page!")
            return

        time.sleep(random.uniform(3, 5))

        # Scroll to load content
        try:
            sb.execute_script("window.scrollTo(0, 800);")
            time.sleep(1.5)
            sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
        except Exception:
            pass

        urls = scraper.collect_profile_urls(sb)
        print(f"  Step 2: Found {len(urls)} profile URLs on page 1")

        if not urls:
            print("  No profile URLs found. The page might have loaded incorrectly.")
            print("  Page title:", sb.get_title())
            # Print a snippet of the page to debug
            try:
                body = sb.get_text("body")[:500]
                print(f"  Page text preview: {body}")
            except Exception:
                pass
            return

        # Only test first 3 profiles
        test_urls = urls[:3]
        print(f"  Step 3: Scraping {len(test_urls)} test profiles...\n")

        results = []
        for i, url in enumerate(test_urls):
            print(f"  [{i+1}/{len(test_urls)}] {url}")
            record = scraper.scrape_profile(sb, url, location_str)
            if record:
                results.append(record)
                print(f"    Name:       {record.get('Agent Name', '?')}")
                print(f"    Office:     {record.get('Office/Realty', '?')}")
                print(f"    Sales 12m:  {record.get('Sales Last 12 Months', '?')}")
                print(f"    Total:      {record.get('Total Sales', '?')}")
                print(f"    Mobile:     {record.get('Mobile Phone', '?')}")
                print(f"    Office Ph:  {record.get('Office Phone', '?')}")
                print(f"    Email:      {record.get('Email', '?')}")
                print(f"    Location:   {record.get('Location', '?')}")
                print(f"    Svc Areas:  {record.get('Service Areas', '?')[:80]}...")
                print(f"    Website:    {record.get('Website', '?')}")
                print()
            else:
                print(f"    FAILED to extract data\n")

            time.sleep(random.uniform(4, 7))

        if results:
            scraper.save_batch_to_csv(results)
            print(f"\n  TEST COMPLETE: {len(results)}/{len(test_urls)} profiles scraped")
            print(f"  Output: {scraper.OUTPUT_FILE}")
        else:
            print("\n  TEST FAILED: No profiles could be scraped")

test_main()

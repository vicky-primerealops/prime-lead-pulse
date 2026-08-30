import sys
import Zillow_Agents_Scraper as scraper

scraper.STATES_TO_SCRAPE = {"Alabama": "al"}
scraper.CITIES = {"al": ["Mobile"]}
scraper.OUTPUT_FILE = "zillow_test_mary.csv"
scraper.STATE_FILE = "zillow_test_mary.json"
scraper.DELAY_BETWEEN_PROFILES = (2, 3)

def test_mary():
    from seleniumbase import SB
    print("Testing Mary Carpenter profile...")
    url = "https://www.zillow.com/profile/Mary-Carpenter"
    
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        record = scraper.scrape_profile(sb, url, "Mobile, AL")
        if record:
            print(f"Name:       {record.get('Agent Name')}")
            print(f"Office:     {record.get('Office/Realty')}")
            print(f"Mobile:     {record.get('Mobile Phone')}")
            print(f"Office Ph:  {record.get('Office Phone')}")
            print(f"Website:    {record.get('Website')}")
        else:
            print("Failed to scrape.")

if __name__ == "__main__":
    test_mary()

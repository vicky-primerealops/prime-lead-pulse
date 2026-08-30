import sys
import Zillow_Agents_Scraper as scraper

scraper.STATES_TO_SCRAPE = {"Alabama": "al"}
scraper.CITIES = {"al": ["Mobile"]}

def find_mary():
    from seleniumbase import SB
    print("Searching for Mary Carpenter in Mobile AL listings...")
    
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        city_url = "https://www.zillow.com/professionals/real-estate-agent-reviews/mobile-al/"
        sb.uc_open_with_reconnect(city_url, reconnect_time=5)
        
        # Collect profiles
        import time
        time.sleep(3)
        sb.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
        urls = scraper.collect_profile_urls(sb)
        
        mary_url = None
        for u in urls:
            if "mary" in u.lower() and "carpenter" in u.lower():
                mary_url = u
                break
                
        if not mary_url:
            print("Could not find Mary Carpenter on page 1 of Mobile AL. Will try the first agent instead.")
            if urls:
                mary_url = urls[0]
            else:
                return
                
        print(f"Testing URL: {mary_url}")
        record = scraper.scrape_profile(sb, mary_url, "Mobile, AL")
        if record:
            print(f"Name:       {record.get('Agent Name')}")
            print(f"Office:     {record.get('Office/Realty')}")
            print(f"Mobile:     {record.get('Mobile Phone')}")
            print(f"Office Ph:  {record.get('Office Phone')}")
            print(f"Website:    {record.get('Website')}")
        else:
            print("Failed to scrape.")

if __name__ == "__main__":
    find_mary()

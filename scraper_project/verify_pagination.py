import sys
from seleniumbase import SB
import Zillow_Agents_Scraper as scraper

def test_pagination():
    url = "https://www.zillow.com/professionals/real-estate-agent-reviews/saraland-al/"
    
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        print(f"Loading {url}")
        sb.uc_open_with_reconnect(url, reconnect_time=5)
        
        import time
        time.sleep(4)
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        max_page = scraper.detect_max_page(sb)
        print(f"\nDETECTED MAX PAGE: {max_page}")

if __name__ == "__main__":
    test_pagination()

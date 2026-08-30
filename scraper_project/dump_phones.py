import sys
from seleniumbase import SB
import re

def dump_phones():
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        city_url = "https://www.zillow.com/professionals/real-estate-agent-reviews/mobile-al/"
        sb.uc_open_with_reconnect(city_url, reconnect_time=5)
        
        import time
        time.sleep(3)
        sb.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
        
        links = sb.find_elements("a[href*='/profile/']")
        if not links:
            return
            
        # Try to find Mary Carpenter, otherwise first profile
        profile_url = links[0].get_attribute("href")
        for u in links:
            href = u.get_attribute("href")
            if "mary" in href.lower():
                profile_url = href
                break
                
        print(f"Testing URL: {profile_url}")
        
        sb.uc_open_with_reconnect(profile_url, reconnect_time=5)
        sb.wait_for_element("h1", timeout=15)
        time.sleep(2)
        
        print("\n=== PHONE LINKS HTML ===")
        phone_links = sb.find_elements("a[href^='tel:']")
        for i, link in enumerate(phone_links):
            try:
                # Go up 2 levels to capture the icon container as well
                parent = link.find_element("xpath", "../..")
                print(f"\n--- Phone {i} ---")
                print(parent.get_attribute("outerHTML"))
            except Exception as e:
                print(e)
            
if __name__ == "__main__":
    dump_phones()

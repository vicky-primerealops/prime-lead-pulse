import sys
from seleniumbase import SB

def dump_dom():
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        city_url = "https://www.zillow.com/professionals/real-estate-agent-reviews/mobile-al/"
        sb.uc_open_with_reconnect(city_url, reconnect_time=5)
        
        import time
        time.sleep(3)
        sb.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        links = sb.find_elements("a[href*='/profile/']")
        if not links:
            print("No links found")
            return
            
        profile_url = links[0].get_attribute("href")
        print(f"Testing URL: {profile_url}")
        
        sb.uc_open_with_reconnect(profile_url, reconnect_time=5)
        sb.wait_for_element("h1", timeout=15)
        time.sleep(2)
        
        print("\n=== H1 SIBLINGS ===")
        siblings = sb.find_elements("h1 ~ div, h1 ~ span, h1 ~ p, h1 ~ h2, h1 ~ h3, h1 ~ h4")
        for i, s in enumerate(siblings):
            print(f"[{i}] tag:{s.tag_name} class:{s.get_attribute('class')} text:{s.text.strip()}")
            
        print("\n=== H1 PARENT ===")
        parent = sb.find_element("h1").find_element("xpath", "..")
        print(f"tag:{parent.tag_name} class:{parent.get_attribute('class')}")
        print(f"text:\n{parent.text}")
        
        print("\n=== H1 PARENT'S SIBLINGS ===")
        p_siblings = parent.find_elements("xpath", "following-sibling::*")
        for i, s in enumerate(p_siblings[:3]):
            print(f"[{i}] tag:{s.tag_name} text:{s.text.strip()}")
            
if __name__ == "__main__":
    dump_dom()

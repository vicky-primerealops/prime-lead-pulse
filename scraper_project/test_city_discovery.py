import sys
from seleniumbase import SB
import re

def test_city_discovery():
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        url = "https://www.zillow.com/professionals/real-estate-agent-reviews/al/"
        print(f"Loading {url}")
        sb.uc_open_with_reconnect(url, reconnect_time=5)
        import time
        time.sleep(3)
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        extra = []
        links = sb.find_elements("a[href*='/professionals/real-estate-agent-reviews/'][href*='-al/']")
        for link in links:
            href = link.get_attribute("href") or ""
            m = re.search(r'/real-estate-agent-reviews/(.+)-al/?$', href)
            if m:
                city_name = m.group(1).replace("-", " ").title()
                if city_name and city_name not in extra:
                    extra.append(city_name)
                    
        print(f"Discovered {len(extra)} cities")
        print(extra[:20])

if __name__ == "__main__":
    test_city_discovery()

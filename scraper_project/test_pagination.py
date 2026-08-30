from seleniumbase import SB
import re
import time

def detect_max_page(sb):
    """Detect the highest pagination page number on the current page."""
    max_page = 1
    time.sleep(1)
    
    try:
        # Method 1: Look directly at the text inside the Pagination nav element
        for selector in ["nav[class*='Pagination']", "nav[class*='aginat']", "[class*='Pagination']", "[aria-label*='Page']", "nav a"]:
            try:
                elements = sb.find_elements(selector)
                for el in elements:
                    text = (el.text or "").strip()
                    if text:
                        numbers = re.findall(r'\b\d+\b', text)
                        for num in numbers:
                            max_page = max(max_page, int(num))
                    
                    href = el.get_attribute("href") or ""
                    m = re.search(r'/(\d+)_p/?', href)
                    if m:
                        max_page = max(max_page, int(m.group(1)))
            except Exception:
                continue

        # Method 2: Check page source for pagination patterns
        try:
            src = sb.get_page_source()
            for m in re.finditer(r'/(\d+)_p/', src):
                max_page = max(max_page, int(m.group(1)))
        except Exception:
            pass
            
    except Exception:
        pass
        
    return max_page

def test_pagination():
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
        url = "https://www.zillow.com/professionals/real-estate-agent-reviews/huntsville-al/"
        print(f"Loading {url}")
        sb.uc_open_with_reconnect(url, reconnect_time=5)
        time.sleep(5)
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        max_pg = detect_max_page(sb)
        print(f"Detected max page: {max_pg}")

if __name__ == "__main__":
    test_pagination()

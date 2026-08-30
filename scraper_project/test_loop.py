from seleniumbase import SB
import test_pagination

def run_loop():
    with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
        city_base_url = 'https://www.zillow.com/professionals/real-estate-agent-reviews/abbeville-al/'
        page = 1
        import time
        while True:
            page_url = city_base_url if page == 1 else f"{city_base_url}{page}_p/"
            print(f"Loading {page_url}")
            sb.uc_open_with_reconnect(page_url, 5)
            time.sleep(3)
            sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            urls = []
            links = sb.find_elements("a[href*='/profile/']")
            for link in links:
                href = link.get_attribute("href")
                if href and "/profile/" in href:
                    if not href.startswith("http"):
                        href = "https://www.zillow.com" + href
                    href = href.split("?")[0].split("#")[0]
                    if href not in urls:
                        urls.append(href)
                        
            print(f"Found {len(urls)} profiles on page {page}")
            
            max_pg = test_pagination.detect_max_page(sb)
            print(f"Max page detected: {max_pg}")
            
            if page >= max_pg:
                break
            page += 1

if __name__ == "__main__":
    run_loop()

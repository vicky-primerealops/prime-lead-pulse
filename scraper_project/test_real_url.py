from seleniumbase import SB
import time, re

def test_fast_scroll():
    with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
        sb.uc_open_with_reconnect('https://www.zillow.com/professionals/real-estate-agent-reviews/mobile-al/', 5)
        time.sleep(2)
        links = sb.find_elements("a[href*='/profile/']")
        if links:
            url = links[0].get_attribute('href')
            print("Found URL:", url)
            
            sb.uc_open_with_reconnect(url, 5)
            # FAST WAIT
            time.sleep(2)
            
            try:
                page_text = sb.get_text('body')
                m = re.search(r'(\d[\d,]*)\s+(?:team\s+)?sales?\s+last\s+12\s+months', page_text, re.IGNORECASE)
                print('Sales:', m.group(1) if m else 'Not found')
                
                phones = []
                for link in sb.find_elements("a[href^='tel:']"):
                    ph = (link.text or "").strip()
                    if not ph:
                        href = link.get_attribute("href")
                        if href and href.startswith("tel:"):
                            ph = href.replace("tel:", "").strip()
                    if ph and ph not in phones:
                        phones.append(ph)
                print('Phones:', phones)
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    test_fast_scroll()

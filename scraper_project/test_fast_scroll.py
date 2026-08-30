from seleniumbase import SB
import time, re

def test_fast_scroll():
    with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
        sb.uc_open_with_reconnect('https://www.zillow.com/profile/Mary%20Carpenter', 5)
        time.sleep(1)
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        try:
            page_text = sb.get_text('body')
            m = re.search(r'(\d[\d,]*)\s+(?:team\s+)?sales?\s+last\s+12\s+months', page_text, re.IGNORECASE)
            print('Sales:', m.group(1) if m else 'Not found')
            
            phones = []
            for link in sb.find_elements("a[href^='tel:']"):
                ph = (link.text or "").strip()
                if ph and ph not in phones:
                    phones.append(ph)
            print('Phones:', phones)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    test_fast_scroll()

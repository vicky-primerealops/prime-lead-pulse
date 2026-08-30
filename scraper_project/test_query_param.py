from seleniumbase import SB
with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
    url = "https://www.zillow.com/professionals/real-estate-agent-reviews/birmingham-al/?page=2"
    sb.uc_open_with_reconnect(url, 5)
    import time; time.sleep(4)
    print("Title:", sb.get_title())
    print("Page 2 agents found:", len(sb.find_elements("a[href*='/profile/']")))

from seleniumbase import SB

with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
    url = "https://www.zillow.com/professionals/real-estate-agent-reviews/birmingham-al/2_p/"
    sb.uc_open_with_reconnect(url, 5)
    import time; time.sleep(4)
    sb.save_screenshot("birmingham_page2.png")
    
    # check if there's any text on the page
    print("Page title:", sb.get_title())
    print("Page text snippet:", sb.get_text("body")[:200])

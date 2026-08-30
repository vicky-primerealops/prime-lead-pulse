from seleniumbase import SB

with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
    url = "https://www.zillow.com/professionals/real-estate-agent-reviews/birmingham-al/"
    sb.uc_open_with_reconnect(url, 5)
    import time; time.sleep(4)
    sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    links = sb.find_elements("nav[class*='Pagination'] a")
    if not links:
        links = sb.find_elements("a")
        for link in links:
            if link.text.strip() == "2":
                print("Page 2 href:", link.get_attribute("href"))
    else:
        for link in links:
            print("Pagination link text:", link.text.strip(), "href:", link.get_attribute("href"))

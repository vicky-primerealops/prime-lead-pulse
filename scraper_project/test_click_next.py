from seleniumbase import SB

with SB(uc=True, headed=True, chromium_arg='--disable-gpu') as sb:
    url = "https://www.zillow.com/professionals/real-estate-agent-reviews/birmingham-al/"
    sb.uc_open_with_reconnect(url, 5)
    import time; time.sleep(4)
    sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("Initial URL:", sb.get_current_url())
    
    # Try clicking the "Next" button or button with text "2"
    try:
        sb.click("nav[class*='Pagination'] button[aria-label='Next page']")
        time.sleep(3)
        print("URL after Next button:", sb.get_current_url())
    except Exception as e:
        print("Could not click next:", e)
        try:
            # Maybe it's a link with title Next page
            sb.click("a[title='Next page']")
            time.sleep(3)
            print("URL after Next link:", sb.get_current_url())
        except:
            pass
            
    # Print out html of the pagination element
    try:
        nav = sb.find_element("nav[class*='Pagination']")
        print(nav.get_attribute('outerHTML'))
    except:
        print("Nav not found")

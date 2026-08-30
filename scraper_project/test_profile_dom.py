"""
Test script to analyze a specific profile page for Mary Carpenter.
"""
import time
from seleniumbase import SB

PROFILE_URL = "https://www.zillow.com/profile/Mary-Carpenter"

print("Starting test...")

with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:
    print(f"Loading {PROFILE_URL} ...")
    sb.uc_open_with_reconnect(PROFILE_URL, reconnect_time=5)
    
    # Wait for the page to load
    sb.wait_for_element("h1", timeout=15)
    time.sleep(3)
    
    # Scroll to load all content
    sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("\n--- Extracting Data ---")
    
    # 1. Office Name
    print("\nLooking for Office Name (around h1):")
    try:
        elements = sb.find_elements("h1 ~ div, h1 ~ span, h1 ~ p")
        for i, el in enumerate(elements[:5]):
            print(f"  Sibling {i}: '{el.text}' (Class: {el.get_attribute('class')})")
    except Exception as e:
        print(f"  Error: {e}")
        
    try:
        # Also look in the top card area
        parent = sb.find_element("h1").find_element("xpath", "..")
        print(f"\nParent text of h1:\n{parent.text}")
    except Exception:
        pass

    # 2. Phones
    print("\nLooking for Phone Numbers:")
    try:
        # Let's find all phone links
        phone_links = sb.find_elements("a[href^='tel:']")
        for i, link in enumerate(phone_links):
            phone_text = link.text or link.get_attribute("href").replace("tel:", "")
            
            # Let's inspect the parent or previous sibling to find an icon
            try:
                parent = link.find_element("xpath", "..")
                parent_html = parent.get_attribute("outerHTML")
                
                # Check for svg icons to differentiate
                icon_type = "Unknown"
                if "IconMobile" in parent_html or "cell" in parent_html.lower() or "smartphone" in parent_html.lower():
                    icon_type = "Mobile"
                elif "IconOffice" in parent_html or "building" in parent_html.lower() or "office" in parent_html.lower():
                    icon_type = "Office"
                else:
                    # just print the svg classes or paths
                    import re
                    svgs = re.findall(r'<svg[^>]*class="([^"]*)"', parent_html)
                    if svgs:
                        icon_type = f"SVG class: {svgs[0]}"
                
                print(f"  Phone {i}: {phone_text} (Icon logic: {icon_type})")
            except Exception as e:
                print(f"  Phone {i}: {phone_text} (Error checking icon: {e})")
    except Exception as e:
        print(f"  Error finding phones: {e}")

    # 3. Website
    print("\nLooking for Website Links:")
    try:
        # The correct website button often has text "Website" or specific data-testids
        links = sb.find_elements("a")
        for link in links:
            href = link.get_attribute("href")
            text = link.text
            if href and text and "website" in text.lower():
                print(f"  Found 'Website' text link: {href}")
            
            if href and "sellingsouthalabama" in href.lower():
                print(f"  Found the wrong link previously extracted: {href} (Text: '{text}')")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- Test Finished ---")

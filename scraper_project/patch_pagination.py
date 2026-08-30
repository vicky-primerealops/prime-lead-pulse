import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

old_detect = """def detect_max_page(sb):
    \"\"\"Detect the highest pagination page number on the current page.\"\"\"
    max_page = 1
    try:
        # Method 1: Look for pagination links with page numbers in href
        for selector in ["nav a", "a[href*='_p']", "[class*='aginat'] a",
                         "[class*='Pagination'] a", "[aria-label*='Page'] a"]:
            try:
                elements = sb.find_elements(selector)
                for el in elements:
                    text = (el.text or "").strip()
                    if text.isdigit():
                        max_page = max(max_page, int(text))
                    href = el.get_attribute("href") or ""
                    m = re.search(r'/(\\d+)_p/?', href)
                    if m:
                        max_page = max(max_page, int(m.group(1)))
            except Exception:
                continue

        # Method 2: Check page source for pagination patterns
        try:
            src = sb.get_page_source()
            for m in re.finditer(r'/(\\d+)_p/', src):
                max_page = max(max_page, int(m.group(1)))
        except Exception:
            pass

    except Exception:
        pass
    return max_page"""

new_detect = """def detect_max_page(sb):
    \"\"\"Detect the highest pagination page number on the current page.\"\"\"
    max_page = 1
    
    # Let page settle so pagination component can render
    import time
    time.sleep(1)
    
    try:
        # Method 1: Look directly at the text inside the Pagination nav element
        for selector in ["nav[class*='Pagination']", "nav[class*='aginat']", "[class*='Pagination']", "[aria-label*='Page']", "nav a"]:
            try:
                elements = sb.find_elements(selector)
                for el in elements:
                    # The pagination component usually has text like "1\\n2\\n3\\n4\\n5"
                    text = (el.text or "").strip()
                    if text:
                        # Extract all numbers from the text block
                        numbers = re.findall(r'\\b\\d+\\b', text)
                        for num in numbers:
                            max_page = max(max_page, int(num))
                    
                    # Also fallback to checking hrefs just in case it's an a-tag based layout
                    href = el.get_attribute("href") or ""
                    m = re.search(r'/(\\d+)_p/?', href)
                    if m:
                        max_page = max(max_page, int(m.group(1)))
            except Exception:
                continue

        # Method 2: Check page source for pagination patterns
        try:
            src = sb.get_page_source()
            for m in re.finditer(r'/(\\d+)_p/', src):
                max_page = max(max_page, int(m.group(1)))
        except Exception:
            pass

    except Exception:
        pass
    return max_page"""

if old_detect in content:
    content = content.replace(old_detect, new_detect)
    with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched pagination logic.")
else:
    print("Could not find old detect_max_page logic in the file.")

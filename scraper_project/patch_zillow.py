import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSV Headers
old_headers = """CSV_HEADERS = [
    "Agent Name",
    "Office/Realty",
    "Sales Last 12 Months",
    "Total Sales",
    "Phone",
    "Email",
    "Location",
    "Service Areas",
    "Website",
    "Zillow Profile URL",
]"""
new_headers = """CSV_HEADERS = [
    "Agent Name",
    "Office/Realty",
    "Sales Last 12 Months",
    "Total Sales",
    "Mobile Phone",
    "Office Phone",
    "Email",
    "Location",
    "Service Areas",
    "Website",
    "Zillow Profile URL",
]"""
content = content.replace(old_headers, new_headers)

# 2. Update Phone Extraction
old_phone = """    # ── 5. Phone Numbers ──
    phones = []
    # Method A: <a href="tel:..."> links (most reliable)
    try:
        for link in sb.find_elements("a[href^='tel:']"):
            ph = (link.text or "").strip()
            if not ph:
                ph = (link.get_attribute("href") or "").replace("tel:", "").strip()
            if ph and ph not in phones:
                phones.append(ph)
    except Exception:
        pass
    # Method B: Regex fallback on page text
    if not phones:
        phones = list(dict.fromkeys(
            re.findall(r'\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}', page_text)
        ))
    agent["Phone"] = "; ".join(phones)"""

new_phone = """    # ── 5. Phone Numbers ──
    mobile_phones = []
    office_phones = []
    
    try:
        # Find all tel links
        for link in sb.find_elements("a[href^='tel:']"):
            ph = (link.text or "").strip()
            if not ph:
                ph = (link.get_attribute("href") or "").replace("tel:", "").strip()
            
            if not ph:
                continue
                
            # Try to determine if it's office or mobile by inspecting parent HTML for icons
            try:
                parent = link.find_element("xpath", "..")
                parent_html = parent.get_attribute("outerHTML").lower()
                
                # Zillow usually uses a building icon for office, and a regular phone/mobile icon for direct
                if "office" in parent_html or "building" in parent_html or "business" in parent_html:
                    if ph not in office_phones:
                        office_phones.append(ph)
                else:
                    if ph not in mobile_phones:
                        mobile_phones.append(ph)
            except Exception:
                # If we can't tell, assume mobile/direct
                if ph not in mobile_phones:
                    mobile_phones.append(ph)
                    
    except Exception:
        pass
        
    # Regex fallback if no links found
    if not mobile_phones and not office_phones:
        found_phones = list(dict.fromkeys(
            re.findall(r'\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}', page_text)
        ))
        mobile_phones = found_phones
        
    agent["Mobile Phone"] = "; ".join(mobile_phones)
    agent["Office Phone"] = "; ".join(office_phones)"""
content = content.replace(old_phone, new_phone)

# 3. Update Website Extraction
old_website = """    # ── 8. Website ──
    # Look for an explicit website link
    for sel in [
        "a[data-testid*='website']", "a[class*='website' i]",
        "[class*='website' i] a",
    ]:
        try:
            if sb.is_element_visible(sel):
                href = sb.get_attribute(sel, "href")
                if href and "zillow.com" not in href.lower():
                    agent["Website"] = href
                    break
        except Exception:
            continue

    # Fallback: scan all external links for agent websites
    if not agent["Website"]:
        skip_domains = [
            "zillow.com", "facebook.com", "twitter.com", "linkedin.com",
            "instagram.com", "google.com", "yelp.com", "youtube.com",
            "pinterest.com", "tiktok.com", "apple.com", "play.google.com",
            "trulia.com", "hotpads.com",
        ]
        try:
            for link in sb.find_elements("a[href^='http']"):
                href = (link.get_attribute("href") or "")
                if not href or any(d in href.lower() for d in skip_domains):
                    continue
                text = (link.text or "").lower()
                # Prioritize links with "website" or "visit" in the anchor text
                if any(kw in text for kw in ["website", "visit", "site", "web", "home"]):
                    agent["Website"] = href
                    break
        except Exception:
            pass"""

new_website = """    # ── 8. Website ──
    # Strictly look for explicit website links/buttons only.
    # Removed aggressive fallback to avoid scraping ads or random sponsored links.
    for sel in [
        "a[data-testid*='website']", "a[class*='website' i]",
        "[class*='website' i] a", "a[aria-label*='website' i]",
        "a[title*='website' i]"
    ]:
        try:
            if sb.is_element_visible(sel):
                href = sb.get_attribute(sel, "href")
                if href and "zillow.com" not in href.lower():
                    agent["Website"] = href
                    break
        except Exception:
            continue"""
content = content.replace(old_website, new_website)

# 4. Improve Office Extraction
old_office_fallback = """    # Fallback: look for text siblings of h1
    if not agent["Office/Realty"]:
        try:
            # The office name is typically the element right after the agent name
            siblings = sb.find_elements("h1 ~ div, h1 ~ span, h1 ~ p")
            for sib in siblings[:6]:
                text = (sib.text or "").strip()
                if (text
                    and text != agent["Agent Name"]
                    and len(text) < 150
                    and not re.match(r'^[\d.]+\s', text)   # Not "5.0 ★..."
                    and "review" not in text.lower()
                    and "sales" not in text.lower()
                    and "premier agent" not in text.lower()
                    and "more about" not in text.lower()):
                    agent["Office/Realty"] = text.split("\\n")[0].strip()
                    break
        except Exception:
            pass"""

new_office_fallback = """    # Fallback: parse the entire header text block
    if not agent["Office/Realty"]:
        try:
            # Get the parent container of the h1 (usually the agent's profile card)
            header_container = sb.find_element("h1").find_element("xpath", "..")
            header_lines = [line.strip() for line in header_container.text.split("\\n") if line.strip()]
            
            # Find where the agent's name is in the lines
            name_idx = -1
            for idx, line in enumerate(header_lines):
                if agent["Agent Name"].lower() in line.lower() or line.lower() in agent["Agent Name"].lower():
                    name_idx = idx
                    break
            
            # The office is usually the very next line after the name, or the line after that
            if name_idx != -1 and name_idx + 1 < len(header_lines):
                for i in range(1, 4):  # Check up to 3 lines below the name
                    if name_idx + i >= len(header_lines):
                        break
                    candidate = header_lines[name_idx + i]
                    # Exclude stats/ratings lines
                    if (len(candidate) < 100
                        and not re.match(r'^[\d.]+\s', candidate)
                        and "review" not in candidate.lower()
                        and "sales" not in candidate.lower()
                        and "premier agent" not in candidate.lower()
                        and "more about" not in candidate.lower()
                        and "lead of" not in candidate.lower()
                        and "team" != candidate.lower()):
                        agent["Office/Realty"] = candidate
                        break
        except Exception:
            pass"""
content = content.replace(old_office_fallback, new_office_fallback)

with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updates applied to scraper script.")

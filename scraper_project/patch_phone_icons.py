import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

old_phone_logic = """                # Zillow usually uses a building icon for office, and a regular phone/mobile icon for direct
                if "office" in parent_html or "building" in parent_html or "business" in parent_html:
                    if ph not in office_phones:
                        office_phones.append(ph)
                else:
                    if ph not in mobile_phones:
                        mobile_phones.append(ph)"""

new_phone_logic = """                # Zillow's office (building) icon uses SVG rects for windows, or a specific path starting with M24
                if "<rect" in parent_html or "m24 2h8" in parent_html:
                    if ph not in office_phones:
                        office_phones.append(ph)
                else:
                    if ph not in mobile_phones:
                        mobile_phones.append(ph)"""

if old_phone_logic in content:
    content = content.replace(old_phone_logic, new_phone_logic)
    with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched phone icon logic.")
else:
    print("Could not find old phone logic in the file.")

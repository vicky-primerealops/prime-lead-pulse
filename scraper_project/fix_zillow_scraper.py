import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace emojis with text equivalents
content = content.replace('\\U0001F512', '[CAPTCHA]')
content = content.replace('\\u2705', '[OK]')
content = content.replace('\\u26A0\\uFE0F', '[WARNING]')
content = content.replace('\\u23F3', '[WAIT]')
content = content.replace('\\u274C', '[ERROR]')
content = content.replace('\\U0001F50D', '[SEARCH]')
content = content.replace('\\u23ED\\uFE0F', '[SKIP]')
content = content.replace('\\U0001F3D9\\uFE0F', '[CITY]')
content = content.replace('\\U0001F4C4', '[PAGE]')
content = content.replace('\\U0001F4CA', '[STATS]')
content = content.replace('\\U0001F464', '[AGENT]')
content = content.replace('\\U0001F4BE', '[SAVED]')

# Fix the office name extraction to ignore "Zillow Premier Agent"
old_office_logic = """
                if (text
                    and text != agent["Agent Name"]
                    and len(text) < 150
                    and not re.match(r'^[\d.]+\s', text)   # Not "5.0 ★..."
                    and "review" not in text.lower()
                    and "sales" not in text.lower()):
"""

new_office_logic = """
                if (text
                    and text != agent["Agent Name"]
                    and len(text) < 150
                    and not re.match(r'^[\d.]+\s', text)   # Not "5.0 ★..."
                    and "review" not in text.lower()
                    and "sales" not in text.lower()
                    and "premier agent" not in text.lower()
                    and "more about" not in text.lower()):
"""

content = content.replace(old_office_logic, new_office_logic)

with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed emojis and office extraction.")

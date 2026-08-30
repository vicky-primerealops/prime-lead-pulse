with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace dashes with standard ascii hyphens to prevent CP1252 console crashes
content = content.replace("—", "-").replace("─", "-")

with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced unicode dashes with ascii hyphens.")

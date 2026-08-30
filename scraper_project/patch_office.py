import re

with open("Zillow_Agents_Scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

old_office_fallback = """    # Fallback: parse the entire header text block
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

new_office_fallback = """    # Fallback: Zillow DOM structure traversal
    if not agent["Office/Realty"]:
        try:
            # The h1 (name) is in a div. The next sibling div contains the office info.
            h1_parent = sb.find_element("h1").find_element("xpath", "..")
            next_sibling = h1_parent.find_element("xpath", "following-sibling::div")
            
            if next_sibling:
                lines = [line.strip() for line in next_sibling.text.split("\\n") if line.strip()]
                for line in lines:
                    # Ignore badges like "Zillow Premier Agent"
                    if "premier agent" not in line.lower() and "more about" not in line.lower():
                        agent["Office/Realty"] = line
                        break
        except Exception:
            pass"""

content = content.replace(old_office_fallback, new_office_fallback)

with open("Zillow_Agents_Scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Office Name logic.")

import pyautogui
import time
import re

def process_options(filename):
    """Universal parser that extracts descriptions from Tables, Grids, and Code lists."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            raw_lines = file.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{filename}'. Make sure it is in the same folder.")
        return []

    clean_options = []
    
    for line in raw_lines:
        line = line.strip()
        
        # Skip blank lines or Table Headers
        if not line:
            continue
        if line.lower().startswith("data") and "description" in line.lower():
            continue
            
        # 1. HANDLE WEB TABLES (like the HUDOW table)
        # If there is a Tab, it throws away the left column and keeps the Description
        if '\t' in line:
            columns = line.split('\t')
            if len(columns) >= 2:
                line = columns[1].strip() 
        
        # 2. HANDLE PDF GRIDS (like the Townhouse / Flat Condo grids)
        # Splits the line if it sees a Tab, 2+ spaces, or a comma
        parts = re.split(r'\t|\s{2,}|,', line)
        
        for part in parts:
            clean_part = part.strip()
            
            # 3. HANDLE CODE LISTS (like "AU1 - Central")
            # If it sees a hyphen with spaces, it checks if the left side is a short code
            if ' - ' in clean_part:
                left_side = clean_part.split(" - ", 1)[0]
                # If the left side has no spaces (e.g. "AU1"), it's a code. Remove it.
                if " " not in left_side:
                    clean_part = clean_part.split(" - ", 1)[1].strip()
                    
            if clean_part:
                clean_options.append(clean_part)
        
    return clean_options

def automate_propzu_entry(options):
    """Types the extracted options into Propzu instantly."""
    if not options:
        print("⚠️ No options were found in the text file. Exiting.")
        return

    print(f"\n🤖 Automation loaded {len(options)} perfectly cleaned items!")
    print("👉 You have 5 seconds to switch to Chrome and click inside the Propzu 'Options' input box...")
    
    # 5-second countdown timer
    time.sleep(5) 
    
    for option in options:
        # Types the option instantly
        pyautogui.write(option, interval=0) 
        
        # Hits enter to add it
        pyautogui.press('enter')
        
        # To let Propzu process it
        time.sleep(0) 

    print("\n✅ Finished adding all items!")

if __name__ == "__main__":
    options_to_add = process_options('mls_data.txt')
    automate_propzu_entry(options_to_add)
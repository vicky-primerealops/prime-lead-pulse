import pyautogui
import time
import re

def process_options(filename):
    """Reads the text file and automatically extracts options based on large spacing."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            raw_lines = file.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{filename}'. Make sure it is in the same folder.")
        return []

    clean_options = []
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        # Detects the next option anywhere there is a Tab or 2+ consecutive spaces
        parts = re.split(r'\t|\s{2,}', line)
        
        for part in parts:
            clean_part = part.strip()
            
            # Removes "AA1 - " style codes if they happen to be there
            if ' - ' in clean_part and not clean_part.startswith("Manufactured-") and not clean_part.endswith("-Attached"):
                clean_part = clean_part.split(" - ", 1)[1]
                
            if clean_part:
                clean_options.append(clean_part)
        
    return clean_options

def automate_propzu_entry(options):
    """Types the extracted options into Propzu instantly."""
    if not options:
        print("⚠️ No options were found in the text file. Exiting.")
        return

    print(f"\n🤖 Automation loaded {len(options)} items!")
    print("👉 You have 5 seconds to switch to Chrome and click inside the Propzu 'Options' input box...")
    
    # 5-second countdown timer
    time.sleep(5) 
    
    for option in options:
        # Types the option instantly
        pyautogui.write(option, interval=0) 
        
        # Hits enter to add it
        pyautogui.press('enter')
        
        # 0.15-second pause to let Propzu process it
        time.sleep(0.15) 

    print("\n✅ Finished adding all items!")

if __name__ == "__main__":
    # Reads the file, splits by large spaces, and immediately starts typing
    options_to_add = process_options('mls_data.txt')
    automate_propzu_entry(options_to_add)
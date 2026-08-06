import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

print("Opening browser to inspect KW pagination...")
options = uc.ChromeOptions()
# options.add_argument('--headless=new')
driver = uc.Chrome(options=options, version_main=150)
driver.get("https://www.kw.com/agents")

# Give it 10 seconds to fully render the React page
time.sleep(10)

with open("kw_page_source.txt", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("Saved page source to kw_page_source.txt")
driver.quit()

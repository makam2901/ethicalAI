from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import json
import re
import os

# 1. Configure Chrome
options = Options()
options.add_experimental_option("detach", True)  # <-- Keeps browser open after script ends
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoids automation detection

# 2. Start Chrome using WebDriver Manager (auto-matches ChromeDriver)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 3. Open Kaggle
driver.get("https://www.kaggle.com")

print("✅ Kaggle opened successfully. Browser will stay open.")
print("You can interact with the browser manually now.")

# 4. Handle cookie consent
try:
    wait = WebDriverWait(driver, 5)
    ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='OK, Got it.']")))
    ok_button.click()
    print("✅ Cookie consent given.")
except Exception as e:
    print("⚠️ Could not find or click cookie consent button:", e)

# 5. Click on Competitions tab
try:
    competitions_tab = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/competitions']"))
    )
    competitions_tab.click()
    print("✅ Clicked on Competitions tab.")
except Exception as e:
    print("⚠️ Could not find or click Competitions tab:", e)

# 6. Search for data science competitions
try:
    search_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search competitions']"))
    )
    search_box.clear()  # Just to be safe
    search_box.send_keys("data science")
    print("✅ Typed 'data science' and searched.")
except Exception as e:
    print("⚠️ Could not find or type into search bar:", e)

# 7. Click on Filters button
try:
    filters_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Filters']]")
        )
    )
    filters_button.click()
    print("✅ Clicked on Filters button.")
except Exception as e:
    print("⚠️ Could not find or click Filters button:", e)

# 8. Select Monetary prize filter
try:
    # Wait for the Monetary checkbox to appear and click it
    monetary_checkbox = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Monetary']"))
    )
    monetary_checkbox.click()
    print("✅ Selected 'Monetary' prize filter.")

    # Wait for the Done button to appear and click it
    done_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Done']]"))
    )
    done_button.click()
    print("✅ Clicked Done button to apply filters.")
except Exception as e:
    print("⚠️ Could not apply 'Monetary' filter:", e)

# 9. Extract competitions list and save to JSON
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "kaggle_competitions.json")

results = []

try:
    # Wait for the competitions list to render and select items robustly
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='list']"))
    )
    ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul[role='list']")
    list_root = ul_elements[0] if ul_elements else None

    if list_root is None:
        raise TimeoutException("Competitions list <ul role='list'> not found")

    li_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='list'] > li[aria-label]"))
    )
except TimeoutException:
    li_elements = []
    print("⚠️ Competitions list did not load in time")

base_url = "https://www.kaggle.com"

for comp in li_elements:
    try:
        a_tag = comp.find_element(By.CSS_SELECTOR, "a[aria-label]")
        name = a_tag.get_attribute("aria-label")
        link = a_tag.get_attribute("href") or ""
        if link.startswith("/"):
            link = base_url + link

        try:
            prize_tag = comp.find_element(By.CSS_SELECTOR, "div.cecTRc")
            prize_text = prize_tag.text.strip()
            prize = int(re.sub(r"[^\d]", "", prize_text)) if prize_text else 0
        except NoSuchElementException:
            prize = 0

        results.append({
            "name": name,
            "link": link,
            "prize": prize
        })

    except (StaleElementReferenceException, TimeoutException, NoSuchElementException) as e:
        print(f"⚠️ Skipping a competition due to parsing error: {e}")
        continue

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"✅ Extracted {len(results)} competitions and saved to {output_path}")
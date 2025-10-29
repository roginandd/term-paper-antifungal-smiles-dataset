# =======================================
# DrugBank Antifungal Scraper (Page URL method)
# Scrapes all pages by incrementing &page= query parameter
# =======================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

# --- Chrome setup ---
options = Options()
# options.add_argument("--headless")  # uncomment for background run
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# --- Base URL ---
base_url = "https://go.drugbank.com/unearth/q?utf8=✓&searcher=drugs&query=antifungal&page="

all_drugs = []
page = 1

while page < 6:
    print(f"📄 Scraping page {page}...")

    url = base_url + str(page)
    driver.get(url)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "unearth-search-hit")))
    except:
        print("⚠️ No more results found.")
        break

    hits = driver.find_elements(By.CLASS_NAME, "unearth-search-hit")
    if not hits:
        print("🚫 No hits on this page, stopping.")
        break

    for hit in hits:
        try:
            # --- Drug name and link ---
            name_el = hit.find_element(By.CSS_SELECTOR, "h2.hit-link a")
            name = name_el.text.strip()
            link = name_el.get_attribute("href")

            # --- Description ---
            try:
                desc = hit.find_element(By.CLASS_NAME, "hit-description").text.strip()
            except:
                desc = ""

            # --- Badges (status) ---
            try:
                badges = [b.text for b in hit.find_elements(By.CSS_SELECTOR, ".hit-groups .badge")]
                badges = ", ".join(badges)
            except:
                badges = ""

            all_drugs.append({
                "name": name,
                "link": link,
                "description": desc,
                "badges": badges
            })
        except Exception as e:
            print("⚠️ Skipped one entry:", e)

    # --- Try next page ---
    page += 1
    time.sleep(2)

driver.quit()

# --- Save to CSV ---
with open("antifungal_drugs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "link", "description", "badges"])
    writer.writeheader()
    writer.writerows(all_drugs)

print(f"✅ Done! Scraped {len(all_drugs)} drugs across {page-1} pages.")
print("💾 Saved to antifungal_drugs.csv")

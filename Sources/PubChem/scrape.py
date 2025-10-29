from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv, time, random

# --- Setup Chrome ---
options = Options()
options.add_argument("--headless=new")  # comment this out if you want to see the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# --- Base URL ---
base_url = "https://pubchem.ncbi.nlm.nih.gov/#query=antifungal&page="

results = []
max_pages = 77  # adjust if needed

for page in range(1, max_pages + 1):
    print(f"📄 Scraping page {page}...")
    url = base_url + str(page)
    driver.get(url)

    # Wait for compound blocks to load
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.p-md-bottom")))
    except:
        print("⚠️ No more results.")
        break

    compounds = driver.find_elements(By.CSS_SELECTOR, "li.p-md-bottom")

    for compound in compounds:
        try:
            name = compound.find_element(By.CSS_SELECTOR, "a[data-ga-label*='Result Title Link']").text.strip()
            cid = compound.find_element(By.CSS_SELECTOR, "a[data-ga-label*='Result Secondary Link']").text.strip()
            link = compound.find_element(By.CSS_SELECTOR, "a[data-ga-label*='Result Title Link']").get_attribute("href")
            mf = mw = smiles = inchi = create_date = ""

            for line in compound.text.split("\n"):
                if line.startswith("MF:"): mf = line.replace("MF:", "").strip()
                if line.startswith("MW:"): mw = line.replace("MW:", "").strip()
                if line.startswith("SMILES:"): smiles = line.replace("SMILES:", "").strip()
                if line.startswith("InChI:"): inchi = line.replace("InChI:", "").strip()
                if line.startswith("Create Date:"): create_date = line.replace("Create Date:", "").strip()

            results.append({
                "Name": name, "CID": cid, "Link": link,
                "MF": mf, "MW": mw, "SMILES": smiles,
                "InChI": inchi, "Create Date": create_date
            })
        except Exception as e:
            print("⚠️ Skipped one entry:", e)

    time.sleep(random.uniform(2, 5))

driver.quit()

# --- Save results ---
with open("pubchem_antifungal.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "CID", "Link", "MF", "MW", "SMILES", "InChI", "Create Date"])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Done! Scraped {len(results)} compounds across {page} pages.")

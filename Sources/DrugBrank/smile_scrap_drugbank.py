# =========================================
# DrugBank Antifungal Details Scraper
# Visits each link from your CSV
# Extracts UNII, CAS, InChI Key, InChI, IUPAC, SMILES
# =========================================

import pandas as pd
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Load your CSV ---
input_file = "drugbank_antifungal_drugs.csv"
df = pd.read_csv(input_file)

# --- Selenium setup ---
options = Options()
# options.add_argument("--headless")  # uncomment for headless mode
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# --- Prepare results ---
results = []

for idx, row in df.iterrows():
    name = row['name']
    link = row['link']
    print(f"🔗 [{idx+1}/{len(df)}] Visiting {name}...")

    try:
        driver.get(link)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "dl")))
        time.sleep(2)  # short wait for the data to render

        # --- Initialize fields ---
        unii = cas = inchi_key = inchi = iupac = smiles = ""

        # Find all <dt> elements inside the <dl>
        dts = driver.find_elements(By.CSS_SELECTOR, "dl dt")
        for dt in dts:
            field_name = dt.get_attribute("id")
            try:
                dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                value = dd.text.strip()
            except:
                value = ""

            if field_name == "unii":
                unii = value
            elif field_name == "cas-number":
                cas = value
            elif field_name == "inchi-key":
                inchi_key = value
            elif field_name == "inchi":
                inchi = value
            elif field_name == "iupac-name":
                iupac = value
            elif field_name == "smiles":
                smiles = value
        print(smiles)
        results.append({
            "name": name,
            "link": link,
            "UNII": unii,
            "CAS_number": cas,
            "InChI_Key": inchi_key,
            "InChI": inchi,
            "IUPAC_Name": iupac,
            "SMILES": smiles
        })

    except Exception as e:
        print(f"⚠️ Skipped {name} due to error: {e}")
        results.append({
            "name": name,
            "link": link,
            "UNII": "",
            "CAS_number": "",
            "InChI_Key": "",
            "InChI": "",
            "IUPAC_Name": "",
            "SMILES": ""
        })

# --- Close browser ---
driver.quit()

# --- Save results ---
output_file = "drugbank_antifungal_details.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "name", "link", "UNII", "CAS_number", "InChI_Key", "InChI", "IUPAC_Name", "SMILES"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Scraping completed! Saved {len(results)} entries to {output_file}.")

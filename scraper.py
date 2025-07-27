# scraper.py

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os

def scrape_yellowpages(search_term, location):
    search_term = search_term.replace(" ", "+")
    location = location.replace(" ", "+")

    base_url = f"https://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page="

    # ✅ Chrome options
    options = Options()
    options.add_argument("--headless")  # Remove this if you want to see the browser
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")

    # ✅ Automatically download ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    current_directory = os.getcwd()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(current_directory, f"yellowpages_data_{timestamp}.csv")

    page_num = 1
    business_listings = []

    try:
        while True:
            url = base_url + str(page_num)
            driver.get(url)
            time.sleep(random.uniform(3, 6))

            business_cards = driver.find_elements(By.CLASS_NAME, "result")
            if not business_cards:
                break

            for business in business_cards:
                try:
                    name = business.find_element(By.CLASS_NAME, "business-name").text.strip()
                    address = business.find_element(By.CLASS_NAME, "street-address").text.strip() if business.find_elements(By.CLASS_NAME, "street-address") else "-"
                    locality = business.find_element(By.CLASS_NAME, "locality").text.strip() if business.find_elements(By.CLASS_NAME, "locality") else "-"
                    phone = business.find_element(By.CLASS_NAME, "phones").text.strip() if business.find_elements(By.CLASS_NAME, "phones") else "-"
                    website = business.find_element(By.CLASS_NAME, "track-visit-website").get_attribute("href") if business.find_elements(By.CLASS_NAME, "track-visit-website") else "-"

                    business_listings.append({
                        "Business Name": name,
                        "Address": f"{address}, {locality}",
                        "Phone": phone,
                        "Website": website
                    })

                except Exception as e:
                    print(f"❌ Error extracting data: {e}")
                    continue

            if business_listings:
                df = pd.DataFrame(business_listings)
                df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)
                print(f"✅ Data saved to {filename}")
                business_listings.clear()

            page_num += 1

    except Exception as e:
        print(f"❌ Error during scraping: {e}")

    finally:
        driver.quit()
        print("✅ Scraping finished.")
        return filename

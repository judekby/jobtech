import csv
import time
import sys
import random
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def read_existing_offers(filename):
    existing_offers = set()
    if not os.path.exists(filename):
        return existing_offers
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['title'], row['description'], row['location'])
            existing_offers.add(key)
    return existing_offers

def create_firefox_driver(geckodriver_path):
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    selected_user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={selected_user_agent}")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override", selected_user_agent)
    options.set_preference("permissions.default.desktop-notification", 2)
    options.set_preference("fission.webContentIsolationStrategy", 0)
    options.set_preference("webgl.disabled", True)
    options.set_preference("media.peerconnection.enabled", False)
    options.set_preference("privacy.trackingprotection.enabled", True)
    options.set_preference("network.http.referer.XOriginPolicy", 0)
    options.set_preference("network.http.referer.defaultPolicy", 3)
    options.set_preference("network.http.referer.defaultPolicy.pbmode", 2)
    options.set_preference("permissions.default.image", 2)
    options.set_preference("browser.privatebrowsing.autostart", True)
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr', 'en-US', 'en']});
        window.chrome = {runtime: {}};
    """)
    return driver

def wait_for_jobs_to_load(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.PageContent_results__zSSNO[data-testid='job-ads-wrapper']"))
        )
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.PageContent_results__zSSNO[data-testid='job-ads-wrapper'] li")) > 0
        )
        WebDriverWait(driver, timeout).until(
            lambda d: any(
                li.text.strip() 
                for li in d.find_elements(By.CSS_SELECTOR, "ul.PageContent_results__zSSNO[data-testid='job-ads-wrapper'] li")
            )
        )
        time.sleep(3)
        return True
    except TimeoutException:
        return False

def scrape_jobteaser_multiple_pages(start_page, end_page, output_csv_file="jobteaser_offers.csv"):
    geckodriver_path = 'C:\\Users\\PC\\Downloads\\geckodriver-v0.36.0-win32\\geckodriver.exe'
    existing_offers = read_existing_offers(output_csv_file)
    
    all_new_offers = []
    successful_pages = 0
    failed_pages = 0
    start_time = time.time()
    
    for page_num in range(start_page, end_page + 1):
        driver = None
        page_start_time = time.time()
        
        try:
            driver = create_firefox_driver(geckodriver_path)
            page_data = scrape_single_page(driver, page_num)
            
            if page_data:
                new_offers = []
                for offer in page_data:
                    key = (offer['title'], offer['description'], offer['location'])
                    if key not in existing_offers:
                        new_offers.append(offer)
                        existing_offers.add(key)
                all_new_offers.extend(new_offers)
                
                successful_pages += 1
                page_time = time.time() - page_start_time
            else:
                failed_pages += 1
        except Exception:
            failed_pages += 1
        finally:
            if driver:
                driver.quit()
    
    total_time = time.time() - start_time

    if all_new_offers:
        write_to_csv(all_new_offers, output_csv_file)

def scrape_single_page(driver, page_num):
    try:
        page_url = f"https://www.jobteaser.com/fr/job-offers?query=informatique&page={page_num}"
        driver.get(page_url)

        if not wait_for_jobs_to_load(driver):
            return []

        try:
            job_list_ul = driver.find_element(By.CSS_SELECTOR, "ul.PageContent_results__zSSNO[data-testid='job-ads-wrapper']")
            job_lis = job_list_ul.find_elements(By.TAG_NAME, "li")
        except NoSuchElementException:
            return []

        if not job_lis:
            return []

        page_job_data = []
        
        for i, job_li in enumerate(job_lis):
            if i == 5 or i == 6:
                continue
            job_info = {'title': '', 'description': '', 'type': '', 'location': ''}
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_li)
                time.sleep(0.2)
            except Exception:
                pass
            extracted_fields = 0
            
            try:
                title_element = job_li.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > header:nth-child(1) > p:nth-child(1)")
                title_text = title_element.text.strip()
                if title_text:
                    job_info['title'] = title_text
                    extracted_fields += 1
            except NoSuchElementException:
                pass

            try:
                description_element = job_li.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > header:nth-child(1) > h3:nth-child(2) > a:nth-child(1)")
                description_text = description_element.text.strip()
                if description_text:
                    job_info['description'] = description_text
                    extracted_fields += 1
            except NoSuchElementException:
                pass

            try:
                type_element = job_li.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)")
                type_text = type_element.text.strip()
                if type_text:
                    job_info['type'] = type_text
                    extracted_fields += 1
            except NoSuchElementException:
                pass

            try:
                location_element = job_li.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(2)")
                location_text = location_element.text.strip()
                if location_text:
                    job_info['location'] = location_text
                    extracted_fields += 1
            except NoSuchElementException:
                pass

            if any(value.strip() for value in [job_info['title'], job_info['description']]):
                page_job_data.append(job_info)

        return page_job_data
    except Exception:
        return []

def write_to_csv(data, filename):
    if not data:
        return
    
    file_exists = os.path.exists(filename)
    write_header = not file_exists or os.path.getsize(filename) == 0
    
    try:
        keys = data[0].keys()
        with open(filename, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            if write_header:
                dict_writer.writeheader()
            dict_writer.writerows(data)
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) == 4:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
        csv_filename = sys.argv[3]
        
        if start_page > end_page:
            sys.exit(1)
            
        scrape_jobteaser_multiple_pages(start_page, end_page, csv_filename)
        
    elif len(sys.argv) == 3:
        page_number = int(sys.argv[1])
        csv_filename = sys.argv[2]
        
        scrape_jobteaser_multiple_pages(page_number, page_number, csv_filename)
    else:
        sys.exit(1)

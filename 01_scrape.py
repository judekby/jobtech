import requests
from bs4 import BeautifulSoup
import time
import csv

base_url = 'https://www.meteojob.com/jobs?what=data&where=europe&page={}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

def extract_offers(soup):
    offers_data = []
    offers = soup.find_all('li', id=lambda x: x and x.startswith('job-offer-'))
    for offer_li in offers:
        title = offer_li.find('h2', class_='cc-job-offer-title')
        title_text = title.get_text(strip=True) if title else 'N/A'

        company = offer_li.find('p', id=lambda x: x and 'company-name' in x)
        company_text = company.get_text(strip=True) if company else 'N/A'

        location_div = offer_li.find('div', id=lambda x: x and 'job-locations' in x)
        location = location_div.find('span').get_text(strip=True) if location_div else 'N/A'

        contract_div = offer_li.find('div', id=lambda x: x and 'contract-types' in x)
        contract = contract_div.find('span').get_text(strip=True) if contract_div else 'N/A'

        salary_span = offer_li.find('span', class_='cc-tag-primary-light')
        salary = salary_span.get_text(strip=True) if salary_span else 'N/A'

        offers_data.append({
            'Titre': title_text,
            'Entreprise': company_text,
            'Lieu': location,
            'Contrat': contract,
            'Salaire': salary
        })
    return offers_data

all_offers = []

for page_num in range(1, 86):
    print(f"Scraping page {page_num}...")
    url = base_url.format(page_num)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_offers = extract_offers(soup)
        if not page_offers:
            print("Aucune offre trouvée sur cette page, arrêt.")
            break
        all_offers.extend(page_offers)
        time.sleep(2)  
    else:
        print(f"Erreur page {page_num}: statut {response.status_code}")
        break

print(f"Total offres récupérées : {len(all_offers)}")
#csv
with open('meteojob_offres.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Titre', 'Entreprise', 'Lieu', 'Contrat', 'Salaire'])
    writer.writeheader()
    writer.writerows(all_offers)

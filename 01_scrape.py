import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

countries = [
    'france', 'allemagne', 'espagne', 'italie', 'belgique',
    'pays-bas', 'portugal', 'suede', 'autriche', 'irlande'
]

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

def make_offer_key(offer):
    # Clé unique pour identifier une offre : titre + entreprise + lieu
    return (offer['Titre'], offer['Entreprise'], offer['Lieu'])

def main():
    all_offers = []
    keywords_list = ["data", "développeur"] 

    for country in countries:
        for keywords in keywords_list:
            print(f"\n=== Scraping pays: {country} avec mot-clé: {keywords} ===")
            page_num = 1
            while True:
                url = f'https://www.meteojob.com/jobs?what={keywords}&where={country}&page={page_num}'
                print(f"Scraping page {page_num} pour {country} avec keywords '{keywords}' ...")
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_offers = extract_offers(soup)
                    if not page_offers:
                        print(f"Aucune offre trouvée sur la page {page_num} de {country} avec '{keywords}'. Passage au suivant.")
                        break
                    all_offers.extend(page_offers)
                    page_num += 1
                    time.sleep(random.uniform(2, 4))
                else:
                    print(f"Erreur HTTP {response.status_code} sur {country} page {page_num} avec '{keywords}'")
                    break

    print(f"\nTotal offres récupérées : {len(all_offers)}")

    csv_filename = 'raw/offres_meteojob_multi_keywords.csv'

    existing_offers = set()
    if os.path.exists(csv_filename):
        with open(csv_filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_offers.add(make_offer_key(row))

    new_offers = []
    for offer in all_offers:
        if make_offer_key(offer) not in existing_offers:
            new_offers.append(offer)

    print(f"Offres nouvelles à ajouter : {len(new_offers)}")

    mode = 'a' if os.path.exists(csv_filename) else 'w'

    with open(csv_filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Titre', 'Entreprise', 'Lieu', 'Contrat', 'Salaire'])
        if mode == 'w':
            writer.writeheader()
        writer.writerows(new_offers)

if __name__ == "__main__":
    main()

import os
import json
import time
import requests
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

RAW_DATA_DIR = "raw/"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def scrape_adzuna_api():
    """Collecte via API Adzuna"""
    logger.info("Démarrage API Adzuna")

    app_id = os.getenv("ADZUNA_APP_ID")
    api_key = os.getenv("ADZUNA_API_KEY")

    if not app_id or not api_key:
        logger.warning("Clés Adzuna manquantes dans .env")
        return

    countries = ["fr", "de", "nl", "es", "it", "gb", "us", "at", "au", "be", "br", "ca", "ch", "in", "mx", "nz", "pl", "sg", "za"]
    tech_queries = ["python developer", "javascript developer", "react developer"]
    adzuna_data = []

    for country in countries:
        for query in tech_queries:
            try:
                url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
                params = {
                    "app_id": app_id,
                    "app_key": api_key,
                    "what": query,
                    "results_per_page": 50,
                    "content-type": "application/json",
                }

                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()

                    for job in data.get("results", []):
                        job_data = {
                            "source": "adzuna",
                            "country": country,
                            "query": query,
                            "title": job.get("title"),
                            "company": job.get("company", {}).get("display_name"),
                            "location": job.get("location", {}).get("display_name"),
                            "salary_min": job.get("salary_min"),
                            "salary_max": job.get("salary_max"),
                            "description": job.get("description"),
                            "created": job.get("created"),
                            "scraped_at": datetime.now().isoformat(),
                        }
                        adzuna_data.append(job_data)

                time.sleep(1)

            except Exception as e:
                logger.error(f"Erreur Adzuna {country}/{query}: {e}")
                continue

    filename = f"{RAW_DATA_DIR}/adzuna_latest.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(adzuna_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Adzuna terminé: {len(adzuna_data)} offres collectées")


if __name__ == "__main__":
    scrape_adzuna_api()

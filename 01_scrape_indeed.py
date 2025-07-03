import os
import json
import time
import logging
import pandas as pd
from datetime import datetime

from jobspy import scrape_jobs

RAW_DATA_DIR = "/raw"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def scrape_indeed_jobs():
    """Collecte des offres d'emploi Indeed"""
    logger.info("Démarrage collecte Indeed Europe")
    
    countries_config = {
        'France': {'country': 'France', 'location': 'Paris, France'},
        'Germany': {'country': 'Germany', 'location': 'Berlin, Germany'},
        'UK': {'country': 'UK', 'location': 'London, UK'},
        'Italy': {'country': 'Italy', 'location': 'Milan, Italy'},
        'Spain': {'country': 'Spain', 'location': 'Madrid, Spain'},
        'Netherlands': {'country': 'Netherlands', 'location': 'Amsterdam, Netherlands'},
        'Belgium': {'country': 'Belgium', 'location': 'Brussels, Belgium'},
        'Switzerland': {'country': 'Switzerland', 'location': 'Zurich, Switzerland'}
    }
    
    tech_keywords = [
        '"software engineer" python',
        '"data scientist" machine learning',
        '"devops engineer" cloud',
        '"full stack developer" javascript',
        '"backend developer" API',
        '"frontend developer" react',
        '"mobile developer" android ios',
        '"data engineer" ETL'
    ]
    
    indeed_jobs_data = []
    
    for country_name, config in countries_config.items():
        logger.info(f"Collecte Indeed {country_name}")
        
        for keyword in tech_keywords:
            try:
                jobs = scrape_jobs(
                    site_name=["indeed"],
                    search_term=keyword,
                    location=config['location'],
                    country_indeed=config['country'],
                    results_wanted=30,
                    hours_old=168,
                    job_type='fulltime',
                    description_format='html',
                    enforce_annual_salary=True,
                    verbose=1
                )
                
                if not jobs.empty:
                    jobs['search_keyword'] = keyword
                    jobs['target_country'] = country_name
                    jobs['scraped_at'] = pd.Timestamp.now()
                    indeed_jobs_data.append(jobs)
                    logger.info(f"Indeed {country_name}/{keyword}: {len(jobs)} offres")
                
                time.sleep(3)
                    
            except Exception as e:
                logger.error(f"Erreur Indeed {country_name}/{keyword}: {e}")
                continue
    
    if indeed_jobs_data:
        all_jobs = pd.concat(indeed_jobs_data, ignore_index=True)
        all_jobs = all_jobs.drop_duplicates(subset=['title', 'company', 'location'])
        jobs_json = all_jobs.to_dict('records')
        # Remplace le fichier précédent à chaque exécution pour usage pipeline
        filename = f"{RAW_DATA_DIR}/indeed_latest.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(jobs_json, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Indeed terminé: {len(all_jobs)} offres collectées")
    else:
        logger.warning("Aucune donnée Indeed collectée")


if __name__ == "__main__":
    scrape_indeed_jobs()

# JobTech Data Pipeline

Ce projet automatise la collecte, le nettoyage et l’exportation de données provenant de différentes sources d’offres d’emploi et tendances, afin de construire un data warehouse exploitable.

---

## Structure du projet

### Scripts de scraping :

- `01_scrape_adzuna_api.py` : Scraper via l’API Adzuna
- `01_scrape_google_trends.py` : Collecte des tendances Google
- `01_scrape_indeed.py` : Scraper les offres sur Indeed
- `01_scrape_jobteaser.py` : Scraper les offres sur JobTeaser
- `01_scrape_meteojob.py` : Scraper les offres sur MeteoJob

### Scripts de nettoyage (préparation des données) :

- `02_clean_adzuna_api.py`  
- `02_clean_google_trends.py`  
- `02_clean_indeed.py`  
- `02_clean_jobteaser.py`  
- `02_clean_meteojob.py`  
- `02_clean_survey_result_public.py` : Nettoyage des résultats d’enquête publique

### Autres fichiers importants :

- `Api_datalake_challenge.postman_collection.json` : Collection Postman pour tester l’API
- `datawarehouse_export.sql` : Script SQL pour créer/exporter les tables dans le data warehouse
- `run_pipeline.bat` : Script batch pour lancer automatiquement le pipeline complet

### Dossiers :

- `row/` : Données brutes scrappées, stockées ici
- `api/` : Contient les scripts et fichiers liés à l’API

---

## ⚙️ Prérequis

- Python 3.x  
- Firefox installé (pour Selenium)  
- Geckodriver configuré (pour les scripts Selenium)  
- Modules Python listés dans `requirements.txt`
- Clés API Adzuna configurées dans un fichier .env à la racine du projet (variables ADZUNA_APP_ID et ADZUNA_API_KEY)
- beautifulsoup4 (pour parser le HTML)
- Un serveur MySQL accessible (host, user, password, base) configuré et prêt à l’emploi
- Base de données MySQL créée avec droits d’écriture pour l’utilisateur
  

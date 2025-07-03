import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = "raw/adzuna_latest.json" 

MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

MAIN_TABLE = "job_offers_clean"
AGGREGATION_TABLE = "job_aggregations"

def create_tables():

    create_main_table_sql = """
    CREATE TABLE IF NOT EXISTS job_offers_clean (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        country VARCHAR(10),
        query_term VARCHAR(100),
        title VARCHAR(255),
        company VARCHAR(255),
        location VARCHAR(255),
        ville VARCHAR(100),
        region VARCHAR(100),
        salary_min DECIMAL(10,2),
        salary_max DECIMAL(10,2),
        salary_avg DECIMAL(10,2),
        description TEXT,
        created DATETIME,
        scraped_at DATETIME,
        age_offre_jours INT,
        inserted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_offer (source, title, company, created)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    create_agg_table_sql = """
    CREATE TABLE IF NOT EXISTS job_aggregations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        aggregation_date DATE,
        source VARCHAR(50),
        country VARCHAR(10),
        query_term VARCHAR(100),
        total_offers INT,
        offers_with_salary INT,
        avg_salary_min DECIMAL(10,2),
        avg_salary_max DECIMAL(10,2),
        avg_salary_avg DECIMAL(10,2),
        top_company VARCHAR(255),
        top_company_count INT,
        top_location VARCHAR(255),
        top_location_count INT,
        avg_age_days DECIMAL(10,2),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_agg (aggregation_date, source, country, query_term)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_main_table_sql))
        conn.execute(text(create_agg_table_sql))
        conn.commit()
    
    logger.info("Tables créées ou vérifiées")

def load_and_clean_data():
    logger.info("Lecture du fichier JSON...")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    logger.info(f"{len(df)} lignes chargées")
    
    for col in ["title", "company", "location", "description"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    initial_count = len(df)
    df = df.dropna(subset=["title", "company"])
    logger.info(f"{initial_count - len(df)} lignes supprimées (données manquantes)")
    
    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)
    
    df["created"] = pd.to_datetime(df["created"], errors="coerce", utc=True).dt.tz_localize(None)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True).dt.tz_localize(None)
  
    today = pd.to_datetime(datetime.now()).tz_localize(None)
    df["age_offre_jours"] = (today - df["created"]).dt.days

    df[["ville", "region"]] = df["location"].str.extract(r"([^,]+)[,]?\s?(.*)?")
    df["ville"] = df["ville"].fillna("")
    df["region"] = df["region"].fillna("")
    
    df = df.rename(columns={"query": "query_term"})
    
    df = df.drop_duplicates(subset=["source", "title", "company", "created"])
    
    logger.info(f"{len(df)} lignes nettoyées")
    return df

def get_existing_offers():
    try:
        query = """
        SELECT source, title, company, created 
        FROM job_offers_clean
        """
        existing_df = pd.read_sql(query, engine)
        existing_df["created"] = pd.to_datetime(existing_df["created"])
        logger.info(f"{len(existing_df)} offres existantes trouvées")
        return existing_df
    except Exception as e:
        logger.warning(f"Aucune offre existante trouvée: {e}")
        return pd.DataFrame(columns=["source", "title", "company", "created"])

def find_new_offers(df_clean, df_existing):
    if df_existing.empty:
        logger.info("Première insertion - toutes les offres sont nouvelles")
        return df_clean

    df_merged = df_clean.merge(
        df_existing[["source", "title", "company", "created"]], 
        on=["source", "title", "company", "created"], 
        how="left", 
        indicator=True
    )
    
    new_offers = df_merged[df_merged["_merge"] == "left_only"].drop("_merge", axis=1)
    logger.info(f"{len(new_offers)} nouvelles offres trouvées")
    
    return new_offers

def insert_new_offers(df_new):
    if df_new.empty:
        logger.info("Aucune nouvelle offre à insérer")
        return False

    columns_to_insert = [
        "source", "country", "query_term", "title", "company", "location",
        "ville", "region", "salary_min", "salary_max", "salary_avg",
        "description", "created", "scraped_at", "age_offre_jours"
    ]
    
    available_columns = [col for col in columns_to_insert if col in df_new.columns]
    df_to_insert = df_new[available_columns].copy()
    
    try:
        df_to_insert.to_sql(
            MAIN_TABLE, 
            engine, 
            if_exists="append", 
            index=False, 
            method="multi"
        )
        logger.info(f"{len(df_to_insert)} nouvelles offres insérées")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion: {e}")
        return False

def create_aggregations():
    logger.info("Création des agrégations...")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM job_offers_clean"))
            count = result.fetchone()[0]
            if count == 0:
                logger.warning("Aucune donnée dans job_offers_clean")
                return
    except Exception as e:
        logger.error(f"Erreur lors de la vérification: {e}")
        return

    agg_query = """
    SELECT 
        CURDATE() as aggregation_date,
        source,
        country,
        query_term,
        COUNT(*) as total_offers,
        SUM(CASE WHEN salary_min IS NOT NULL OR salary_max IS NOT NULL THEN 1 ELSE 0 END) as offers_with_salary,
        AVG(salary_min) as avg_salary_min,
        AVG(salary_max) as avg_salary_max,
        AVG(salary_avg) as avg_salary_avg,
        AVG(age_offre_jours) as avg_age_days
    FROM job_offers_clean
    GROUP BY source, country, query_term
    """

    top_company_query = """
    SELECT 
        source, country, query_term,
        company as top_company,
        COUNT(*) as company_count
    FROM job_offers_clean
    GROUP BY source, country, query_term, company
    ORDER BY source, country, query_term, COUNT(*) DESC
    """

    top_location_query = """
    SELECT 
        source, country, query_term,
        ville as top_location,
        COUNT(*) as location_count
    FROM job_offers_clean
    WHERE ville IS NOT NULL AND ville != ''
    GROUP BY source, country, query_term, ville
    ORDER BY source, country, query_term, COUNT(*) DESC
    """
    
    try:
 
        agg_df = pd.read_sql(agg_query, engine)

        top_companies = pd.read_sql(top_company_query, engine)
        top_companies = top_companies.groupby(['source', 'country', 'query_term']).first().reset_index()

        top_locations = pd.read_sql(top_location_query, engine)
        top_locations = top_locations.groupby(['source', 'country', 'query_term']).first().reset_index()

        agg_df = agg_df.merge(
            top_companies[['source', 'country', 'query_term', 'top_company', 'company_count']],
            on=['source', 'country', 'query_term'],
            how='left'
        )
        
        agg_df = agg_df.merge(
            top_locations[['source', 'country', 'query_term', 'top_location', 'location_count']],
            on=['source', 'country', 'query_term'],
            how='left'
        )

        agg_df = agg_df.rename(columns={
            'company_count': 'top_company_count',
            'location_count': 'top_location_count'
        })

        delete_today = """
        DELETE FROM job_aggregations WHERE aggregation_date = CURDATE()
        """
        
        with engine.connect() as conn:
            conn.execute(text(delete_today))
            conn.commit()

        agg_df.to_sql(
            AGGREGATION_TABLE,
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )
        
        logger.info(f"{len(agg_df)} agrégations créées")
        
        print("=" * 60)
        for _, row in agg_df.iterrows():
            print(f"Source: {row['source']} | Pays: {row['country']} | Recherche: {row['query_term']}")
            print(f" Total offres: {row['total_offers']}")
            print(f" Offres avec salaire: {row['offers_with_salary']}")
            if pd.notna(row['avg_salary_avg']):
                print(f" Salaire moyen: {row['avg_salary_avg']:.2f}€")
            print(f" Âge moyen: {row['avg_age_days']:.1f} jours")
            print(f" Top entreprise: {row['top_company']} ({row['top_company_count']} offres)")
            if pd.notna(row['top_location']):
                print(f"   Top ville: {row['top_location']} ({row['top_location_count']} offres)")
            print("-" * 40)
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des agrégations: {e}")

def main():
    try:
        logger.info("Début du traitement des données d'emploi...")

        create_tables()

        df_clean = load_and_clean_data()

        df_existing = get_existing_offers()

        df_new = find_new_offers(df_clean, df_existing)

        insertion_success = insert_new_offers(df_new)

        create_aggregations()
        
        logger.info("Traitement terminé avec succès!")

        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM job_offers_clean"))
                total_count = result.fetchone()[0]
                print(f"\n TOTAL EN BASE: {total_count} offres d'emploi")
        except Exception as e:
            logger.error(f"Erreur lors du comptage final: {e}")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise

if __name__ == "__main__":
    main()

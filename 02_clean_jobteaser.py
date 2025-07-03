
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

# --- Chargement du fichier CSV ---
df = pd.read_csv("raw/jobteaser_offers.csv", encoding="utf-8")

# --- Renommage des colonnes ---
df.rename(columns={
    "title": "company",
    "description": "title",
    "type": "contract_type"
}, inplace=True)

# --- Séparation de la colonne 'location' en 'city' et 'country' ---
df[['city', 'country']] = df['location'].str.split(',', expand=True)

# --- Nettoyage des espaces inutiles ---
df['city'] = df['city'].str.strip()
df['country'] = df['country'].str.strip()

# --- Fonction d'extraction de la catégorie de contrat ---
def extract_contract_category(value):
    value = str(value).lower()
    if "alternance" in value:
        return "Alternance"
    elif "stage" in value:
        return "Stage"
    elif "cdi" in value:
        return "CDI"
    elif "cdd" in value:
        return "CDD"
    else:
        return "Autre"

# --- Application de la fonction sur la colonne contract_type ---
df["contract_category"] = df["contract_type"].apply(extract_contract_category)

# --- Analyses ---
offers_country = df['country'].value_counts(dropna=False)
offers_per_contract_cat = df['contract_category'].value_counts(dropna=False)
offers_per_country_city = df.groupby(['country', 'city']).size().reset_index(name='offers_count')
idx = offers_per_country_city.groupby('country')['offers_count'].idxmax()
top_cities_per_country = offers_per_country_city.loc[idx]

# --- Connexion MySQL ---
MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# --- Création et insertion table job_offers ---
create_job_offers_table = """
CREATE TABLE IF NOT EXISTS jobteaser_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(255),
    title TEXT,
    contract_type VARCHAR(255),
    location VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    contract_category VARCHAR(50)
)
"""
with engine.connect() as conn:
    conn.execute(text(create_job_offers_table))
    conn.commit()

df.to_sql(name='jobteaser_offers', con=engine, if_exists='append', index=False)

# --- Création et insertion table offers_per_country ---
offers_per_country_df = offers_country.reset_index()
offers_per_country_df.columns = ['country', 'offers_count']

create_offers_per_country_table = """
CREATE TABLE IF NOT EXISTS offers_country (
    country VARCHAR(255) PRIMARY KEY,
    offers_count INT
)
"""
with engine.connect() as conn:
    conn.execute(text(create_offers_per_country_table))
    conn.commit()

offers_per_country_df.to_sql(name='offers_per_country', con=engine, if_exists='replace', index=False)

# --- Création et insertion table offers_per_contract_cat ---
offers_per_contract_cat_df = offers_per_contract_cat.reset_index()
offers_per_contract_cat_df.columns = ['contract_category', 'offers_count']

create_offers_per_contract_cat_table = """
CREATE TABLE IF NOT EXISTS offers_per_contract_cat (
    contract_category VARCHAR(50) PRIMARY KEY,
    offers_count INT
)
"""
with engine.connect() as conn:
    conn.execute(text(create_offers_per_contract_cat_table))
    conn.commit()

offers_per_contract_cat_df.to_sql(name='offers_per_contract_cat', con=engine, if_exists='replace', index=False)

# --- Création et insertion table top_cities_per_country ---
create_top_cities_per_country_table = """
CREATE TABLE IF NOT EXISTS top_cities_per_country (
    country VARCHAR(255) PRIMARY KEY,
    city VARCHAR(255),
    offers_count INT
)
"""
with engine.connect() as conn:
    conn.execute(text(create_top_cities_per_country_table))
    conn.commit()

top_cities_per_country.to_sql(name='top_cities_per_country', con=engine, if_exists='replace', index=False)

print("Données principales et agrégations insérées avec succès.")


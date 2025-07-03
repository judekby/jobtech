import pandas as pd
import re
import numpy as np
from sqlalchemy import create_engine, text
import unicodedata  
from unidecode import unidecode

df = pd.read_csv("raw/offres_meteojob_multi_keywords.csv", encoding="latin1")

df.drop_duplicates(inplace=True)
df.columns = ["title", "company", "location", "contract_type", "salary"]

df["JobCategory"] = None
df["country"] = None
df = df[["JobCategory", "country", "title", "company", "location", "contract_type", "salary"]]

def clean_text(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = text.replace('�', 'e')  
    text = unidecode(text)  
    text = re.sub(r'\s+', ' ', text)  
    return text.strip()

for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(clean_text)

def clean_salary(value):
    if pd.isna(value) or str(value).lower() == 'n/a':
        return None

    value = str(value).lower()
    value = re.sub(r'par an|annuel|€|\s|\u20ac', '', value)
    value = re.sub(r'[^\d\.,\-\–]', '', value)
    value = value.replace(',', '.')

    parts = re.split(r'[\-\–]', value)
    nums = [float(p) for p in parts if p.replace('.', '', 1).isdigit()]

    return np.mean(nums) if nums else None

df['salary'] = df['salary'].apply(clean_salary)

def normalize_contract_type(ct):
    if pd.isna(ct):
        return None
    ct = ct.lower().strip()
    ct = re.sub(r'[\-\,].*', '', ct)  
    ct = re.sub(r'\s+', ' ', ct)

    if 'alternance' in ct or 'apprentissage' in ct:
        return 'Alternance'
    if 'cdi' in ct and 'interim' not in ct and 'alternance' not in ct:
        return 'CDI'
    if 'cdd' in ct:
        return 'CDD'
    if 'stage' in ct:
        return 'Stage'
    if 'benevolat' in ct:
        return 'Benevolat'
    if 'cdic' in ct:
        return 'CDIC'
    if 'engagement' in ct:
        return "Contrat d'Engagement Educatif"
    if 'interim' in ct:
        return 'Interim'
    if 'vie' in ct or 'vte' in ct:
        return 'VIE - VTE'
    if 'independant' in ct or 'freelance' in ct or 'franchise' in ct:
        return 'Indépendant / Franchise'

    return ct.title()

df['contract_type'] = df['contract_type'].apply(normalize_contract_type)

offers_per_country = df['country'].value_counts(dropna=False).rename_axis('country').reset_index(name='offer_count')
offers_per_country = offers_per_country.dropna(subset=['country'])

offers_per_contract = df['contract_type'].value_counts(dropna=False).rename_axis('contract_type').reset_index(name='offer_count')
salary_mean_per_contract = df.groupby('contract_type')['salary'].mean().reset_index(name='avg_salary')
salary_mean_per_country = df.groupby('country')['salary'].mean().reset_index(name='avg_salary')

top_companies = df['company'].value_counts().head(5).rename_axis('company').reset_index(name='offer_count')
salary_mean_top_companies = df[df['company'].isin(top_companies['company'])].groupby('company')['salary'].mean().reset_index(name='avg_salary')

MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

create_table_query = """
CREATE TABLE IF NOT EXISTS job_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    JobCategory VARCHAR(255),
    country VARCHAR(100),
    title TEXT,
    company VARCHAR(255),
    location VARCHAR(255),
    contract_type VARCHAR(255),
    salary DECIMAL(10,2)
)
"""

create_agg_tables_queries = [
    """
    CREATE TABLE IF NOT EXISTS offers_per_country (
        country VARCHAR(100),
        offer_count INT,
        PRIMARY KEY (country)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS offers_per_contract (
        contract_type VARCHAR(255),
        offer_count INT,
        PRIMARY KEY (contract_type)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS salary_mean_per_contract (
        contract_type VARCHAR(255),
        avg_salary DECIMAL(10,2),
        PRIMARY KEY (contract_type)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS salary_mean_per_country (
        country VARCHAR(100),
        avg_salary DECIMAL(10,2),
        PRIMARY KEY (country)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS top_companies (
        company VARCHAR(255),
        offer_count INT,
        PRIMARY KEY (company)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS salary_mean_top_companies (
        company VARCHAR(255),
        avg_salary DECIMAL(10,2),
        PRIMARY KEY (company)
    )
    """
]

with engine.connect() as conn:
    conn.execute(text(create_table_query))
    for query in create_agg_tables_queries:
        conn.execute(text(query))
    conn.commit()

with engine.connect() as conn:
    result = conn.execute(text("SELECT title, company, location FROM job_offers"))
    existing_keys = set((row[0], row[1], row[2]) for row in result)

def make_key(row):
    return (row['title'], row['company'], row['location'])

df['key'] = df.apply(make_key, axis=1)
df_new = df[~df['key'].isin(existing_keys)].copy()
df_new.drop(columns=['key'], inplace=True)

print(f"\nNombre d'offres nouvelles à insérer : {len(df_new)}")

if not df_new.empty:
    df_new.to_sql(name="job_offers", con=engine, if_exists="append", index=False)
    print("Nouvelles données insérées avec succès.")
else:
    print("Aucune nouvelle offre à insérer.")

def upsert_table(df_agg, table_name, key_columns):
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table_name}"))
        df_agg.to_sql(name=table_name, con=conn, if_exists="append", index=False)
    print(f"Données agrégées insérées dans {table_name}")

upsert_table(offers_per_country, 'offers_per_country', ['country'])
upsert_table(offers_per_contract, 'offers_per_contract', ['contract_type'])
upsert_table(salary_mean_per_contract, 'salary_mean_per_contract', ['contract_type'])
upsert_table(salary_mean_per_country, 'salary_mean_per_country', ['country'])
upsert_table(top_companies, 'top_companies', ['company'])
upsert_table(salary_mean_top_companies, 'salary_mean_top_companies', ['company'])

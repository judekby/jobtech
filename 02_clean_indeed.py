import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine, text, inspect

MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

with open('raw/indeed_latest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df.replace({np.nan: None}, inplace=True)

# === Crée la table jobs si elle n'existe pas ===
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS jobs (
            id VARCHAR(255) PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            date_posted DATE,
            is_remote BOOLEAN,
            search_keyword TEXT,
            scraped_at DATETIME
        )
    """))

with engine.connect() as conn:
    existing_ids_df = pd.read_sql("SELECT id FROM jobs", conn)
    existing_ids_set = set(existing_ids_df['id'].tolist())

new_rows = df[~df['id'].isin(existing_ids_set)]

if new_rows.empty:
    print("No new jobs to insert.")
else:
    inspector = inspect(engine)
    with engine.begin() as conn:
        existing_cols = [col["name"] for col in inspector.get_columns("jobs")]
        for col in new_rows.columns:
            if col not in existing_cols:
                conn.execute(text(f'ALTER TABLE jobs ADD COLUMN `{col}` TEXT'))

    new_rows.to_sql('jobs', engine, if_exists='append', index=False)
    print(f"{len(new_rows)} new jobs inserted.")

    with engine.begin() as conn:
        # Jobs by company
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agg_jobs_by_company (
                company TEXT,
                count INT
            )
        """))
        conn.execute(text("DELETE FROM agg_jobs_by_company"))
        conn.execute(text("""
            INSERT INTO agg_jobs_by_company (company, count)
            SELECT company, COUNT(*) FROM jobs GROUP BY company
        """))

        # Jobs by location
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agg_jobs_by_location (
                location TEXT,
                count INT
            )
        """))
        conn.execute(text("DELETE FROM agg_jobs_by_location"))
        conn.execute(text("""
            INSERT INTO agg_jobs_by_location (location, count)
            SELECT location, COUNT(*) FROM jobs GROUP BY location
        """))

        # Jobs by date
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agg_jobs_by_date (
                date_posted DATE,
                count INT
            )
        """))
        conn.execute(text("DELETE FROM agg_jobs_by_date"))
        conn.execute(text("""
            INSERT INTO agg_jobs_by_date (date_posted, count)
            SELECT date_posted, COUNT(*) FROM jobs GROUP BY date_posted
        """))

        # Jobs by remote
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agg_jobs_by_remote (
                is_remote BOOLEAN,
                count INT
            )
        """))
        conn.execute(text("DELETE FROM agg_jobs_by_remote"))
        conn.execute(text("""
            INSERT INTO agg_jobs_by_remote (is_remote, count)
            SELECT is_remote, COUNT(*) FROM jobs GROUP BY is_remote
        """))

        # Jobs by keyword
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agg_jobs_by_keyword (
                search_keyword TEXT,
                count INT
            )
        """))
        conn.execute(text("DELETE FROM agg_jobs_by_keyword"))
        conn.execute(text("""
            INSERT INTO agg_jobs_by_keyword (search_keyword, count)
            SELECT search_keyword, COUNT(*) FROM jobs GROUP BY search_keyword
        """))

    print("Aggregation tables updated.")

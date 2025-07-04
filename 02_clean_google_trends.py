import pandas as pd
from sqlalchemy import create_engine, text

final_df = pd.read_csv('raw/google_trends_data.csv')

filtered_df = final_df[final_df['isPartial'] == False]

MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

mean_interest = filtered_df.groupby(['country', 'keyword'])['interest'].mean().reset_index()

idx = mean_interest.groupby('country')['interest'].idxmax()
top_languages = mean_interest.loc[idx].reset_index(drop=True)

table_name = 'top_languages_by_country'

with engine.connect() as conn:
    conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            country VARCHAR(255),
            keyword VARCHAR(255),
            interest FLOAT,
            PRIMARY KEY (country)
        );
    """))

with engine.connect() as conn:
    existing_df = pd.read_sql_table(table_name, conn)

merged = top_languages.merge(existing_df, on=['country', 'keyword', 'interest'], how='left', indicator=True)
new_rows = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])

if not new_rows.empty:
    new_rows.to_sql(name=table_name, con=engine, if_exists='append', index=False)

import pandas as pd
from sqlalchemy import create_engine

final_df = pd.read_csv('data/google_trends_data.csv')  

# Filtrer les données où isPartial est False : isPartial signifie que le scrapping n'as pas réussit à recuperer la données completes du jour
filtered_df = final_df[final_df['isPartial'] == False]

MYSQL_USER = "root"
MYSQL_PASSWORD = "taous"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "gold"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Calcule l'intérêt moyen par pays et mot-clé
mean_interest = filtered_df.groupby(['country', 'keyword'])['interest'].mean().reset_index()

# mot-clé le plus populaire par pays
idx = mean_interest.groupby('country')['interest'].idxmax()
top_languages = mean_interest.loc[idx].reset_index(drop=True)

top_languages.to_csv('data/languagePopulaireParPays_data.csv', index=False)
print("Fichier 'languagePopulaireParPays_data.csv' créé avec succès.")

table_name = 'top_languages_by_country'
top_languages.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print(f"Table '{table_name}' insérée avec succès dans la base MySQL '{MYSQL_DATABASE}'.")

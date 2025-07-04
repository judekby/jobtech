import pandas as pd
import hashlib
import os
import sqlalchemy
from collections import Counter

CSV_PATH = "raw/survey_results_public.csv"
HASH_PATH = "raw/.last_hash"
DB_URI = "mysql+pymysql://root:taous@localhost:3306/gold"

EUROPE_COUNTRIES = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina",
    "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia",
    "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein",
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway",
    "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden",
    "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"
]

def compute_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def is_new_file(file_path):
    new_hash = compute_file_hash(file_path)
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, 'r') as f:
            old_hash = f.read()
        if old_hash == new_hash:
            return False
    with open(HASH_PATH, 'w') as f:
        f.write(new_hash)
    return True

def table_exists(engine, table_name):
    return engine.dialect.has_table(engine.connect(), table_name)

df = pd.read_csv(CSV_PATH, low_memory=False)

df = df[["Country", "EdLevel", "YearsCodePro", "LanguageHaveWorkedWith", "RemoteWork"]].dropna()

df["YearsCodePro"] = df["YearsCodePro"].replace({
    "Less than 1 year": "0",
    "More than 50 years": "51"
})
df["YearsCodePro"] = df["YearsCodePro"].astype(float)

df = df[df["Country"].isin(EUROPE_COUNTRIES)]

agg_by_country = df.groupby("Country").agg({
    "YearsCodePro": "mean",
    "LanguageHaveWorkedWith": "count"
}).rename(columns={
    "YearsCodePro": "AvgYearsCodePro",
    "LanguageHaveWorkedWith": "ResponseCount"
}).reset_index()

agg_by_remote = df.groupby("RemoteWork").agg({
    "YearsCodePro": "mean",
    "LanguageHaveWorkedWith": "count"
}).rename(columns={
    "YearsCodePro": "AvgYearsCodePro",
    "LanguageHaveWorkedWith": "ResponseCount"
}).reset_index()

language_counter = Counter()
for langs in df["LanguageHaveWorkedWith"]:
    for lang in langs.split(";"):
        language_counter[lang.strip()] += 1

top_languages = pd.DataFrame(language_counter.most_common(), columns=["Language", "Count"])

engine = sqlalchemy.create_engine(DB_URI)
first_time = not table_exists(engine, 'agg_by_country')

if not is_new_file(CSV_PATH) and not first_time:
    print("Pas de nouvelles données. Arrêt du script.")
    exit()

agg_by_country.to_sql("agg_by_country", engine, index=False, if_exists="replace")
agg_by_remote.to_sql("agg_by_remote", engine, index=False, if_exists="replace")
top_languages.to_sql("top_languages", engine, index=False, if_exists="replace")

print("Données insérées avec succès.")

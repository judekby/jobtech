from pytrends.request import TrendReq
import pandas as pd
import time

pytrends = TrendReq(hl='en-US', tz=360, requests_args={'verify': False})

# Liste des mots-clés 
keywords = [
    'Python', 'Java', 'JavaScript', 'Go', 'Rust', 'C++',
    'C#', 'Kotlin', 'React', 'Vue.js', 'Angular', 'Node.js',
    'Docker', 'Kubernetes'
]

# Liste des pays
countries = [
    'FR', 'DE', 'NL', 'ES', 'PL', 'IT', 'BE', 'SE', 'FI',
    'PT', 'IE', 'CZ', 'AT', 'DK'
]

results = []

# Scrapping
for country in countries:
    for kw in keywords:
        try:
            pytrends.build_payload([kw], geo=country, timeframe='today 12-m')
            data = pytrends.interest_over_time()

            if not data.empty:
                data = data.reset_index()
                data = data.rename(columns={kw: 'interest'})
                data['keyword'] = kw
                data['country'] = country
                results.append(data)

            time.sleep(1)  
        except Exception as e:
            print(f"Erreur pour {kw} en {country} : {e}")
            continue

if results:
    final_df = pd.concat(results)
    final_df = final_df[['date', 'interest', 'keyword', 'country', 'isPartial']]
    final_df.to_csv('data/google_trends_data.csv', index=False)
    print(" Données enregistrées dans 'google_trends_data.csv'")
else:
    print("Aucune donnée récupérée.")

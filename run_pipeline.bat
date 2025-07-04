@echo off
cd /d C:\Users\taoza\Downloads\Challange_datalake

D:\applictaions\python.exe 01_scrape_meteojob.py
D:\applictaions\python.exe 01_scrape_jobteaser.py
D:\applictaions\python.exe 01_scrape_indeed.py
D:\applictaions\python.exe 01_scrape_google_trends.py
D:\applictaions\python.exe 01_scrape_adzuna_api.py
D:\applictaions\python.exe 02_clean_meteojob.py
D:\applictaions\python.exe 02_clean_jobteaser.py
D:\applictaions\python.exe 02_clean_indeed.py
D:\applictaions\python.exe 02_clean_google_trends.py
D:\applictaions\python.exe 02_clean_adzuna_api.py
D:\applictaions\python.exe 02_clean_survey_results_public.py

pause

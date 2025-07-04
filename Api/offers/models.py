from django.db import models

class JobOffer(models.Model):
    title = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    country = models.CharField(max_length=100)

    class Meta:
        db_table = 'job_offers'
        managed = False


class OffersPerCountryMeteojob(models.Model):
    country = models.CharField(max_length=255, primary_key=True)
    offers_count = models.IntegerField()

    class Meta:
        db_table = 'offers_per_country'
        managed = False


class OffersPerContract(models.Model):
    contract_type = models.CharField(max_length=255, primary_key=True)
    offer_count = models.IntegerField()

    class Meta:
        db_table = 'offers_per_contract'
        managed = False


class SalaryMeanPerContract(models.Model):
    contract_type = models.CharField(max_length=255, primary_key=True)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'salary_mean_per_contract'
        managed = False


class SalaryMeanPerCountry(models.Model):
    country = models.CharField(max_length=100, primary_key=True)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'salary_mean_per_country'
        managed = False


class TopCompanies(models.Model):
    company = models.CharField(max_length=255, primary_key=True)
    offer_count = models.IntegerField()

    class Meta:
        db_table = 'top_companies'
        managed = False


class SalaryMeanTopCompanies(models.Model):
    company = models.CharField(max_length=255, primary_key=True)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'salary_mean_top_companies'
        managed = False

class JobteaserOffer(models.Model):
    company = models.CharField(max_length=255)
    title = models.TextField()
    contract_type = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    contract_category = models.CharField(max_length=50)

    class Meta:
        db_table = 'jobteaser_offers'
        managed = False


class OffersPerCountryJobteaser(models.Model):
    country = models.CharField(max_length=255, primary_key=True)
    offers_count = models.IntegerField()

    class Meta:
        db_table = 'offers_country'  
        managed = False


class OffersPerContractCategory(models.Model):
    contract_category = models.CharField(max_length=50, primary_key=True)
    offers_count = models.IntegerField()

    class Meta:
        db_table = 'offers_per_contract_cat'
        managed = False


class TopCitiesPerCountry(models.Model):
    country = models.CharField(max_length=255, primary_key=True)
    city = models.CharField(max_length=255)
    offers_count = models.IntegerField()

    class Meta:
        db_table = 'top_cities_per_country'
        managed = False

class JobOfferClean(models.Model):
    source = models.CharField(max_length=50)
    country = models.CharField(max_length=10)
    query_term = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salary_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    description = models.TextField()
    created = models.DateTimeField()
    scraped_at = models.DateTimeField(null=True)
    age_offre_jours = models.IntegerField()
    inserted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_offers_clean'
        managed = False  
        unique_together = ('source', 'title', 'company', 'created')

class JobAggregation(models.Model):
    aggregation_date = models.DateField()
    source = models.CharField(max_length=50)
    country = models.CharField(max_length=10)
    query_term = models.CharField(max_length=100)
    total_offers = models.IntegerField()
    offers_with_salary = models.IntegerField()
    avg_salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    avg_salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    avg_salary_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    top_company = models.CharField(max_length=255, null=True)
    top_company_count = models.IntegerField(null=True)
    top_location = models.CharField(max_length=255, null=True)
    top_location_count = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_aggregations'
        managed = False
        unique_together = ('aggregation_date', 'source', 'country', 'query_term')

class Job(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    title = models.TextField(null=True)
    company = models.TextField(null=True)
    location = models.TextField(null=True)
    date_posted = models.DateField(null=True)
    is_remote = models.BooleanField(null=True)
    search_keyword = models.TextField(null=True)
    scraped_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'jobs'
        managed = False

class AggJobsByCompany(models.Model):
    company = models.TextField()
    count = models.IntegerField()

    class Meta:
        db_table = 'agg_jobs_by_company'
        managed = False

class AggJobsByLocation(models.Model):
    location = models.TextField()
    count = models.IntegerField()

    class Meta:
        db_table = 'agg_jobs_by_location'
        managed = False

class AggJobsByDate(models.Model):
    date_posted = models.DateField()
    count = models.IntegerField()

    class Meta:
        db_table = 'agg_jobs_by_date'
        managed = False

class AggJobsByRemote(models.Model):
    is_remote = models.BooleanField()
    count = models.IntegerField()

    class Meta:
        db_table = 'agg_jobs_by_remote'
        managed = False

class AggJobsByKeyword(models.Model):
    search_keyword = models.TextField()
    count = models.IntegerField()

    class Meta:
        db_table = 'agg_jobs_by_keyword'
        managed = False
class TopLanguageByCountry(models.Model):
    country = models.CharField(primary_key=True, max_length=255)
    keyword = models.CharField(max_length=255)  
    interest = models.FloatField()

    class Meta:
        db_table = 'top_languages_by_country'
        managed = False

class AggByCountry(models.Model):
    country = models.CharField(primary_key=True, max_length=255)
    avgyearscodepro = models.FloatField()
    responsecount = models.IntegerField()

    class Meta:
        db_table = 'agg_by_country'
        managed = False


class AggByRemote(models.Model):
    remotework = models.CharField(primary_key=True, max_length=255)
    avgyearscodepro = models.FloatField()
    responsecount = models.IntegerField()

    class Meta:
        db_table = 'agg_by_remote'
        managed = False


class TopLanguage(models.Model):
    language = models.CharField(primary_key=True, max_length=255)
    count = models.IntegerField()

    class Meta:
        db_table = 'top_languages'
        managed = False

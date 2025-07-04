from rest_framework import serializers
from .models import (
    JobOffer,
    OffersPerCountryMeteojob,
    OffersPerContract,
    SalaryMeanPerContract,
    SalaryMeanPerCountry,
    TopCompanies,
    SalaryMeanTopCompanies,
    JobteaserOffer,
    OffersPerCountryJobteaser,
    OffersPerContractCategory,
    TopCitiesPerCountry,
    JobOfferClean, 
    JobAggregation,
    Job,
    AggJobsByCompany,
    AggJobsByLocation,
    AggJobsByDate,
    AggJobsByRemote,
    AggJobsByKeyword,
    TopLanguageByCountry,
    AggByCountry, 
    AggByRemote, 
    TopLanguage,
)

class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'

class OffersPerCountryMeteojobSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffersPerCountryMeteojob
        fields = '__all__'

class OffersPerContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffersPerContract
        fields = '__all__'

class SalaryMeanPerContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryMeanPerContract
        fields = '__all__'

class SalaryMeanPerCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryMeanPerCountry
        fields = '__all__'

class TopCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopCompanies
        fields = '__all__'

class SalaryMeanTopCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryMeanTopCompanies
        fields = '__all__'

class JobteaserOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobteaserOffer
        fields = '__all__'

class OffersPerCountryJobteaserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffersPerCountryJobteaser
        fields = '__all__'

class OffersPerContractCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OffersPerContractCategory
        fields = '__all__'

class TopCitiesPerCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopCitiesPerCountry
        fields = '__all__'

class JobOfferCleanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOfferClean
        fields = '__all__'

class JobAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAggregation
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class AggJobsByCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AggJobsByCompany
        fields = '__all__'

class AggJobsByLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggJobsByLocation
        fields = '__all__'

class AggJobsByDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggJobsByDate
        fields = '__all__'

class AggJobsByRemoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggJobsByRemote
        fields = '__all__'

class AggJobsByKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggJobsByKeyword
        fields = '__all__'

class TopLanguageByCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopLanguageByCountry
        fields = '__all__'

class AggByCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AggByCountry
        fields = '__all__'


class AggByRemoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggByRemote
        fields = '__all__'


class TopLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopLanguage
        fields = '__all__'
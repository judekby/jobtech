from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
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
    AggByCountry, AggByRemote, TopLanguage,
)
from .serializers import (
    JobOfferSerializer,
    OffersPerCountryMeteojobSerializer,
    OffersPerContractSerializer,
    SalaryMeanPerContractSerializer,
    SalaryMeanPerCountrySerializer,
    TopCompaniesSerializer,
    SalaryMeanTopCompaniesSerializer,
    JobteaserOfferSerializer,
    OffersPerCountryJobteaserSerializer,
    OffersPerContractCategorySerializer,
    TopCitiesPerCountrySerializer,
    JobOfferCleanSerializer, 
    JobAggregationSerializer,
    JobSerializer,
    AggJobsByCompanySerializer,
    AggJobsByLocationSerializer,
    AggJobsByDateSerializer,
    AggJobsByRemoteSerializer,
    AggJobsByKeywordSerializer,
    TopLanguageByCountrySerializer,
    AggByCountrySerializer, AggByRemoteSerializer, TopLanguageSerializer,
)

class AuthenticatedListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

# Tes vues héritent maintenant de cette classe
class JobOfferList(AuthenticatedListAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer

class OffersPerCountryMeteojobList(AuthenticatedListAPIView):
    queryset = OffersPerCountryMeteojob.objects.all()
    serializer_class = OffersPerCountryMeteojobSerializer

class OffersPerContractList(AuthenticatedListAPIView):
    queryset = OffersPerContract.objects.all()
    serializer_class = OffersPerContractSerializer

class SalaryMeanPerContractList(AuthenticatedListAPIView):
    queryset = SalaryMeanPerContract.objects.all()
    serializer_class = SalaryMeanPerContractSerializer

class SalaryMeanPerCountryList(AuthenticatedListAPIView):
    queryset = SalaryMeanPerCountry.objects.all()
    serializer_class = SalaryMeanPerCountrySerializer

class TopCompaniesList(AuthenticatedListAPIView):
    queryset = TopCompanies.objects.all()
    serializer_class = TopCompaniesSerializer

class SalaryMeanTopCompaniesList(AuthenticatedListAPIView):
    queryset = SalaryMeanTopCompanies.objects.all()
    serializer_class = SalaryMeanTopCompaniesSerializer

class JobteaserOfferList(AuthenticatedListAPIView):
    queryset = JobteaserOffer.objects.all()
    serializer_class = JobteaserOfferSerializer

class OffersPerCountryJobteaserList(AuthenticatedListAPIView):
    queryset = OffersPerCountryJobteaser.objects.all()
    serializer_class = OffersPerCountryJobteaserSerializer

class OffersPerContractCategoryList(AuthenticatedListAPIView):
    queryset = OffersPerContractCategory.objects.all()
    serializer_class = OffersPerContractCategorySerializer

class TopCitiesPerCountryList(AuthenticatedListAPIView):
    queryset = TopCitiesPerCountry.objects.all()
    serializer_class = TopCitiesPerCountrySerializer

class JobOfferCleanFilter(filters.FilterSet):
    country = filters.CharFilter(lookup_expr='iexact')
    source = filters.CharFilter(lookup_expr='iexact')
    created = filters.DateFromToRangeFilter()  
    query_term = filters.CharFilter(lookup_expr='icontains')
    company = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = JobOfferClean
        fields = ['country', 'source', 'created']

class JobOfferCleanListView(generics.ListAPIView):
    queryset = JobOfferClean.objects.all()
    serializer_class = JobOfferCleanSerializer
    filterset_class = JobOfferCleanFilter

class JobAggregationFilter(filters.FilterSet):
    country = filters.CharFilter(lookup_expr='iexact')
    source = filters.CharFilter(lookup_expr='iexact')
    aggregation_date = filters.DateFromToRangeFilter()

    class Meta:
        model = JobAggregation
        fields = ['country', 'source', 'aggregation_date']

class JobAggregationListView(generics.ListAPIView):
    queryset = JobAggregation.objects.all()
    serializer_class = JobAggregationSerializer
    filterset_class = JobAggregationFilter

class JobListView(AuthenticatedListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class AggJobsByCompanyListView(AuthenticatedListAPIView):
    queryset = AggJobsByCompany.objects.all()
    serializer_class = AggJobsByCompanySerializer

class AggJobsByLocationListView(AuthenticatedListAPIView):
    queryset = AggJobsByLocation.objects.all()
    serializer_class = AggJobsByLocationSerializer

class AggJobsByDateListView(AuthenticatedListAPIView):
    queryset = AggJobsByDate.objects.all()
    serializer_class = AggJobsByDateSerializer

class AggJobsByRemoteListView(AuthenticatedListAPIView):
    queryset = AggJobsByRemote.objects.all()
    serializer_class = AggJobsByRemoteSerializer

class AggJobsByKeywordListView(AuthenticatedListAPIView):
    queryset = AggJobsByKeyword.objects.all()
    serializer_class = AggJobsByKeywordSerializer

class TopLanguageByCountryListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopLanguageByCountrySerializer
    queryset = TopLanguageByCountry.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']

class AggByCountryListView(ListAPIView):
    queryset = AggByCountry.objects.all()
    serializer_class = AggByCountrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']


class AggByRemoteListView(ListAPIView):
    queryset = AggByRemote.objects.all()
    serializer_class = AggByRemoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['remotework']


class TopLanguageListView(ListAPIView):
    queryset = TopLanguage.objects.all()
    serializer_class = TopLanguageSerializer
    permission_classes = [IsAuthenticated]
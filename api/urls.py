from django.contrib import admin
from django.urls import path, include
from .views import CountryListAPIView, RegionListAPIView, GlobalListAPIView, LastUpdateAPIView

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('country/', CountryListAPIView.as_view(), name='country-list-api'),
    path('region/', RegionListAPIView.as_view(), name='region-list-api'),
    path('global/', GlobalListAPIView.as_view(), name='global-list-api'),
    path('last-up/', LastUpdateAPIView.as_view(), name='last-list-api'),
]

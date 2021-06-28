from typing import List
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from stats.models import Country, Region, Global, Last_update
from .serializers import CountrySerializer, RegionSerializer, GlobalSerializer, LastUpdateSerializer

# Create your views here.


class CountryListAPIView(ListCreateAPIView):
    """
    API view to retrieve list of posts or create new
    """
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class RegionListAPIView(ListCreateAPIView):

    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class GlobalListAPIView(ListCreateAPIView):

    serializer_class = GlobalSerializer
    queryset = Global.objects.all()


class LastUpdateAPIView(ListCreateAPIView):

    serializer_class = LastUpdateSerializer
    queryset = Last_update.objects.all()


"""
Sample view for put, delete operations

class PostDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.active()
"""

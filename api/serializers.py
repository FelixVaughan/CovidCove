from stats.models import Country, Region, Global, Last_update
from rest_framework import fields, serializers


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['iso', 'name', 'active', 'recoveries',
                  'deaths', 'confirmed', 'time', 'fatality_rate']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name', 'in_country', 'active', 'recoveries',
                  'deaths', 'confirmed', 'time', 'fatality_rate']


class GlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Global
        fields = ['name', 'active', 'recoveries',
                  'deaths', 'confirmed', 'time', 'fatality_rate']


class LastUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Last_update
        fields = ['time']

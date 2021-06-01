from django.db import models
from django.db.models.deletion import CASCADE

class Time(models.Model):
    time = models.TimeField(auto_now=False, auto_now_add=False)

class Location(models.Model):
    name = models.CharField(max_length=20, blank=False)
    total_cases = models.IntegerField(null=False, default = -1)
    current_cases = models.IntegerField(null=False, default = -1)
    recoveries = models.IntegerField(null=False, default = -1)
    deaths = models.IntegerField(null=False, default = -1)
    time = models.ForeignKey(Time, on_delete=CASCADE)

class Country(Location):
    iso = models.CharField(max_length=3, default="N/A")

class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    coordinates = models.CharField(max_length=3)


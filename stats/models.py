from django.db import models
from django.db.models.deletion import CASCADE
import datetime
import sys
class Time(models.Model):
    time = models.TimeField(auto_now=False, auto_now_add=False)

class Location(models.Model):
    name = models.CharField(max_length=20, blank=False)
    total_cases = models.IntegerField(default = -1)
    current_cases = models.IntegerField(default = -1)
    recoveries = models.IntegerField(default = -1)
    deaths = models.IntegerField(default = -1)
    time = models.ForeignKey(Time, on_delete=CASCADE)

class Country(Location):
    iso = models.CharField(max_length=3, default="N/A")

class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    coordinates = models.CharField(max_length=3)


class Last_time(models.Model): #should only ever be one entry in this table. Stores the date the db was last refreshed
    time = models.CharField(default="2019-12-30", max_length=8)

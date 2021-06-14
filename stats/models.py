from django.db import models
from django.db.models.deletion import CASCADE
import datetime
import sys
class Time(models.Model):
    time = models.TimeField(auto_now=False, auto_now_add=False)

class Location(models.Model):
    name = models.CharField(max_length=20, blank=False, editable=False, default="N/A")
    active = models.IntegerField(default = -1)
    recoveries = models.IntegerField(default = -1)
    deaths = models.IntegerField(default = -1)
    confirmed = models.IntegerField(default = -1)
    time = models.ForeignKey(Time, on_delete=CASCADE)
    fatality_rate = models.DecimalField(default=0.00)

    class Meta:
        abstract = True

class Country(Location):
    iso = models.CharField(max_length=3, editable=False, default="N/A")

class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    coordinates = models.CharField(max_length=3)

class Global(Location):#Stores the global total
    pass

class Last_update(models.Model): #should only ever be one entry in this table. Stores the date the db was last refreshed
    time = models.CharField(default="2019-12-31", max_length=8)

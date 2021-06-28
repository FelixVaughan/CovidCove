from django.db import models
from django.db.models.deletion import CASCADE
import datetime
import sys


"""
# model to store daily stats for every country, region
# if used, we donot need the day model above

class DailyRecords(models.Model):
    date =  models.DateField(default=datetime.date.today)
    new_cases = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    country = models.ForeignKey(Country, on_delete=CASCADE)
    region = models.ForeignKey(Region, on_delete=CASCADE, null=True)
"""


class Location(models.Model):
    name = models.CharField(max_length=20, blank=False, editable=False)
    active = models.IntegerField(default=-1)
    recoveries = models.IntegerField(default=-1)
    deaths = models.IntegerField(default=-1)
    confirmed = models.IntegerField(default=-1)
    time = models.CharField(max_length=10)
    fatality_rate = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=4)

    class Meta:
        abstract = True


class Country(Location):
    iso = models.CharField(max_length=3, editable=False)

    def __str__(self):
        return f"{self.name} ({self.iso}) with {self.active} active cases, {self.recoveries} recoveries, {self.deaths} deaths, {self.confirmed} confirmed and a fatality rate of {self.fatality_rate} for {self.time}"


class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}', in country {self.in_country} has {self.active} active cases, {self.recoveries} recoveries, {self.deaths} deaths, {self.confirmed} confirmed and a fatality rate of {self.fatality_rate} for {self.time}"


class Global(Location):  # Stores the global total
    def __str__(self):
        return f"The world has {self.active} active cases, {self.recoveries} recoveries, {self.deaths} deaths, {self.confirmed} confirmed and a fatality rate of {self.fatality_rate} for {self.time}"


# should only ever be one entry in this table. Stores the date the db was last refreshed
class Last_update(models.Model):
    time = models.CharField(default="2019-12-31", max_length=10)

    def __str__(self):
        return self.time

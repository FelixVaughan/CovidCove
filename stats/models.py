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
    active = models.IntegerField(default=0)
    recoveries = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    confirmed = models.IntegerField(default=0)
    total_active = models.IntegerField(default=0)
    total_recoveries = models.IntegerField(default=0)
    total_deaths = models.IntegerField(default=0)
    total_confirmed = models.IntegerField(default=0)
    time_as_string = models.CharField(max_length=10, default="n/a")
    time = models.DateField(max_length=10) 
    fatality_rate = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=4)

    class Meta:
        abstract = True



class Country(Location):
    iso = models.CharField(max_length=3, editable=False, default="N/A")
    regions = models.IntegerField(default=-1)
    pop = models.IntegerField(default=-1) #population
    def __str__(self):
        return f"{self.name} ({self.iso}) on {self.time}"


class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"'{self.name}', in country {self.in_country} on {self.time}"


class Global(Location):  # Stores the global total
    def __str__(self):
        return f"World on: {str(self.time)}"


# should only ever be one entry in this table. Stores the date the db was last refreshed
class Last_update(models.Model):
    time = models.DateField(default=datetime.date(2019,12,31), max_length=10)
    country = models.CharField(default="Palau", max_length=20)
    def __str__(self):
        return self.time

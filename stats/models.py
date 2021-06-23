from django.db import models
from django.db.models.deletion import CASCADE
import datetime
import sys


class Time(models.Model):
    time = models.CharField(default="N/A", max_length=10)

    def __str__(self):
        return str(self.time)


"""
# model to store daily stats for every country, region
# if used, we donot need the Time model above

class DailyRecords(models.Model):
    date =  models.DateField(default=datetime.date.today)
    new_cases = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    country = models.ForeignKey(Country, on_delete=CASCADE)
    region = models.ForeignKey(Region, on_delete=CASCADE, null=True)
"""


class Location(models.Model):
    name = models.CharField(max_length=20, blank=False,
                            editable=False, default="N/A")
    active = models.IntegerField(default=-1)
    recoveries = models.IntegerField(default=-1)
    deaths = models.IntegerField(default=-1)
    confirmed = models.IntegerField(default=-1)
    time = models.ForeignKey(Time, on_delete=CASCADE)
    fatality_rate = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=4)

    class Meta:
        abstract = True


class Country(Location):
    iso = models.CharField(max_length=3, editable=False, default="N/A")

    def __str__(self):
        return f"name: {self.name} iso: {self.iso} active: {self.active} recoveried: {self.recoveries} deaths: {self.deaths} confirmed: {self.confirmed} fr: {self.fatality_rate}"


class Region(Location):
    in_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    coordinates = models.CharField(max_length=3)

    def __str__(self):
        return f"country: {self.in_country} name: {self.name} active: {self.active} recoveried: {self.recoveries} deaths: {self.deaths} confirmed: {self.confirmed} fr: {self.fatality_rate}"


class Global(Location):  # Stores the global total
    def __str__(self):
        return f"active: {self.active} recoveried: {self.recoveries} deaths: {self.deaths} confirmed: {self.confirmed} fr: {self.fatality_rate}"


# should only ever be one entry in this table. Stores the date the db was last refreshed
class Last_update(models.Model):
    time = models.CharField(default="2019-12-31", max_length=10)
    
    def __str__(self):
        return self.time
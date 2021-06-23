from django.test import TestCase
import datetime

from requests.api import delete
from .utilities import *
from .models import * 
import json 
import sys
import time

def populate_tables():
    credentials = get_api_info()
    dates = [int(digit) for digit in get_last_time().split("-")] #integer list compression of last updated date 
    start = datetime.date(dates[0], dates[1], dates[2])
    end = datetime.date.today()
    if start == end:
        return
    delta = datetime.timedelta(days=1)
    current_date = start

    headers=credentials['headers']
    #print(f"COMMENCING LOOP\n current_date: {current_date} credentials: {credentials}")
    while current_date < end:
        #print(f"Current time is {str(current_date)}")
        current_date_object = Time.objects.create(time=str(current_date))
        try:
            global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": start})
        except requests.exceptions.ConnectionError:
            time.sleep(30)
            global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": start})
            #sometimes due to too many connections a timeout occurs. This remedies that.
        if(global_data_request.status_code == 200):
            data = global_data_request.json()['data']
            entry = Global()
            #print("retrieved global stats with", end=" ")
            if(data):
                #print(entry)
                entry.confirmed = data['confirmed']
                entry.deaths = data['deaths'] 
                entry.recoveries = data['recovered']
                entry.active = data['active']
                entry.fatality_rate = data['fatality rate']
                #print(entry)
            #entry.save()
            else:
                #print("no data")
                pass
                #log could not get data for date            
        else:
            #print("global data not recieved at all")
            #log failure
            pass

        try:
            locations = json.load(open("cleaned_data.json","r"))
        except FileNotFoundError:
            sys.stderr.write("There does not appear to be a 'cleaned_data.json' (location) file")
            sys.exit(1)
        for location in locations:
            country_name = locations[location]['name']
            #print(f"current country is {country_name}")
            try: 
                country_data_request = requests.get(credentials['countries_endpoint'], headers=headers, params={"date": current_date, "iso": location})
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                country_data_request = requests.get(credentials['countries_endpoint'], headers=headers, params={"date": current_date, "iso": location})
            total_deaths = total_recovered = total_active = total_confirmed = total_fr = total_regions = 0 
            if country_data_request.status_code == 200:
                #print("country request success")
                country = Country.objects.create(iso=location, name=country_name, time=current_date_object)
                areas = country_data_request.json()['data'] #note sometimes area IS the country in the case of only one entry
                for area in areas:
                    #print(f"\tarea {area} stats")
                    confirmed = area['confirmed']
                    deaths = area['deaths']
                    recoveries = area['recovered']
                    active = area['active']
                    f_rate = area['fatality_rate']
                    coords = f"{area['region']['lat']} {area['region']['long']}" 
                    province = area['region']['province']
                    total_deaths += deaths
                    total_recovered += recoveries
                    total_active += active
                    total_confirmed += confirmed
                    total_fr += f_rate
                    total_regions += 1
                    #print(f"province is: {province}")
                    if province == "": #means these are country level stats, not provincial
                        continue
                    reg = Region.objects.create(name=province, active=active, recoveries=recoveries, deaths=deaths, confirmed=confirmed, fatality_rate=f_rate, coordinates=coords, in_country=country, time=current_date_object) 
                    #print(reg)
                country.active = total_active
                country.recoveries = total_recovered
                country.deaths = total_deaths
                country.confirmed = total_confirmed
                if(total_regions):
                    country.fatality_rate = (total_fr)/total_regions
                #print(country)
            else:
                #log could not get data for date
                pass
        current_date += delta
        print(current_date)
    now = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Pull time updated FROM {start} to {now}")
    #update_time()

def clear_tables():
    Global.objects.all().delete()
    Country.objects.all().delete()
    Region.objects.all().delete()

try:
    populate_tables()
except Exception as e:
    print(f"There was an exception: \n{e}")
    uin = input("Would you like to clear Global, Country and Region tables (y/n)? ")
    if(uin.upper() == "y"):
        clear_tables()
    uin = input("Would you like to update time (y/n)? ")
    if (uin.upper() == "y"):
        update_time()
    sys.exit(1)

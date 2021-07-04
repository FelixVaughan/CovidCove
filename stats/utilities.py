import os
from requests.models import HTTPBasicAuth, HTTPError
from .models import * 
import sys 
import requests
import json
import time
from dotenv import load_dotenv
import datetime
load_dotenv()




##############################################################################
#                            Last_time Model Helper                          #
##############################################################################
def get_last_time():
        if(len(Last_update.objects.all()) < 1):
            Last_update.objects.create()
        last_date = Last_update.objects.get(pk=1)
        return last_date.time

def update_time(): 
    if(len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    current_time = datetime.date.today()
    last_date.time = current_time
    last_date.save()

def reset():
    if(len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty. Aborted reset.")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    last_date.time = datetime.date(2019,12,31)
    last_date.save()


##############################################################################
#                            Data Fetching Functions                         #
##############################################################################
def get_credentials():
    try:
        api_info = {
            "countries_endpoint": os.environ['countries_endpoint'],
            "location_endpoint": os.environ['location_endpoint'],
            "provinces_endpoint": os.environ['province_location_endpoint'],
            "totals_endpoint": os.environ['total_states_endpoint'],
            "population_endpoint": os.environ['population_endpoint'],
            "headers": {os.environ['api_key']: os.environ['key'], os.environ['host_addr']: os.environ['host']}
        }
    except KeyError:
        sys.stderr.write("FATAL ERROR: could not obtain api credentials!")
        sys.exit(1)
    return api_info

def fetch_location_properties():
    credentials = get_credentials()
    headers=credentials['headers']
    countries_request = requests.get(credentials['location_endpoint'], headers=headers)
    if[countries_request.status_code == "ok"]:
        countries = countries_request.json()['data']
        new_data = {}
        for country in countries:
            iso = country['iso']
            new_data[iso] = {}
            new_data[iso] = country['name']
        save_as = open("./cleaned_data.json","w")
        save_as.write(json.dumps(new_data))
        save_as.close()
    else:
        raise HTTPError


#######################################################################################################
#                                        Table Population Methods                                     #
#######################################################################################################
def populate_tables():
    credentials = get_credentials()
    #date = [int(digit) for digit in get_last_time().split("-")] #integer list compression of last updated date 
    start = get_last_time() 
    #start = datetime.date(date[0], date[1], date[2])
    end = datetime.date.today()
    if start == end:
        return
    day = datetime.timedelta(days=1)
    current_date = datetime.date(2021, 3, 20) #STRICTLY FOR TESTING
    headers=credentials['headers']
    while current_date <= end:
        print(f"Retrieving for: {current_date}")
        try:
            global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": current_date})
        except requests.exceptions.ConnectionError:
            time.sleep(15)
            global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": current_date})
            #sometimes due to too many connections a timeout occurs. This remedies that.
        if(global_data_request.status_code == 200):
            data = global_data_request.json()['data']
            entry = Global()
            if(data):
                entry.total_confirmed = data['confirmed']
                entry.total_deaths = data['deaths'] 
                entry.total_recoveries = data['recovered']
                entry.total_active = data['active']
                entry.confirmed = data['confirmed_diff']
                entry.deaths = data['deaths_diff'] 
                entry.recoveries = data['recovered_diff']
                entry.active = data['active_diff']
                entry.fatality_rate = data['fatality_rate']
                entry.time = current_date
                entry.time_as_string = str(current_date)

            else:
                pass
                #log could not get data for date       
            entry.save()

        else:
            #log failure
            pass

        try:
            locations = json.load(open("cleaned_data.json","r"))
        except FileNotFoundError:
            fetch_location_properties()
            locations = json.load(open("cleaned_data.json","r"))
        for iso in locations:
            country_name = locations[iso]
            try: 
                country_data_request = requests.get(credentials['countries_endpoint'], headers=headers, params={"date": current_date, "iso": iso})
            except requests.exceptions.ConnectionError:
                time.sleep(15)
                country_data_request = requests.get(credentials['countries_endpoint'], headers=headers, params={"date": current_date, "iso": iso})
            country_total_deaths_on_day = country_total_recovered_on_day = country_total_active_on_day = country_total_confirmed_on_day  = country_total_fr = total_regions = 0 
            country_deaths_overall = country_recovered_overall = country_active_overall = country_confirmed_overall = 0
            if country_data_request.status_code == 200:
                country = Country.objects.create(iso=iso, name=country_name, time=current_date, time_as_string=str(current_date))
                areas = country_data_request.json()['data'] #note sometimes area IS the country in the case of only one entry
                for area in areas:
                    confirmed = area['confirmed_diff']
                    deaths = area['deaths_diff']
                    recoveries = area['recovered_diff']
                    active = area['active_diff']
                    total_confirmed = area['confirmed']
                    total_deaths = area['deaths']
                    total_recoveries = area['recovered']
                    total_active = area['active']
                    f_rate = area['fatality_rate']
                    province = area['region']['province']
                    country_total_deaths_on_day += deaths
                    country_total_recovered_on_day += recoveries
                    country_total_active_on_day += active
                    country_total_confirmed_on_day += confirmed
                    country_deaths_overall += total_deaths
                    country_active_overall += total_active
                    country_confirmed_overall += total_confirmed
                    country_recovered_overall += total_recoveries
                    country_total_fr += f_rate
                    total_regions += 1
                    if province == "": #means these are country level stats, not provincial
                        continue
                    reg = Region.objects.create(name=province, active=active, recoveries=recoveries, deaths=deaths, confirmed=confirmed, total_active=total_active, total_recoveries=total_recoveries, total_deaths=total_deaths, total_confirmed=total_confirmed, fatality_rate=f_rate, in_country=country, time=current_date, time_as_string=str(current_date)) 
                country.active = country_total_active_on_day
                country.recoveries = country_total_recovered_on_day
                country.deaths = country_total_deaths_on_day
                country.confirmed = country_total_confirmed_on_day
                country.total_active = country_active_overall
                country.total_deaths = country_deaths_overall
                country.total_recoveries = country_recovered_overall
                country.total_confirmed = country_confirmed_overall
                country.regions = total_regions
                if(total_regions):
                    country.fatality_rate = (country_total_fr)/total_regions
            else:
                #log could not get data for date
                pass
            population_req = requests.get(f"{credentials['population_endpoint']}/{iso}")
            if(population_req.status_code == 200):
                pop = int(population_req.json()["population"])
                country.pop = pop 
            else:
                sys.stderr.write("could not get population data for {country} on {current_date}")
            country.save()
        current_date += day
    now = datetime.date.today().strftime("%Y-%m-%d")
    #update_time()

def clear_tables():
    Global.objects.all().delete()
    Country.objects.all().delete()
    Region.objects.all().delete()

#populate_tables()
uin = input("clear tables (y/n)?")
if uin.lower() == "y":
    clear_tables()
populate_tables()





#jsonify model objects
#add method that converts json to csv
#add method that creates iso IDs for countries in chloropleth map. 
#add function to get data by month
#add function to get data by year
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import time
import os
from requests.models import HTTPBasicAuth, HTTPError
from requests.sessions import PreparedRequest
from .models import *
import sys
import requests
import json
import time
from dotenv import load_dotenv
import datetime
from .credentials import get_credentials

day = datetime.timedelta(days=1)
credentials = get_credentials()


def fetch_global_stats(date):
    try:
        global_data_request = requests.get(credentials['totals_endpoint'], headers=credentials['headers'], params={"date": date})
    except requests.exceptions.ConnectionError:
        time.sleep(15)
        global_data_request = requests.get(credentials['totals_endpoint'], headers=credentials['headers'], params={"date": date})
        #sometimes due to too many connections a timeout occurs. This remedies that.
    except Exception:
        pass
    if(global_data_request.status_code == 200):
        data = global_data_request.json()['data']
        entry = Global(time=date, time_as_string=str(date))
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
        else:
            pass
            #log could not get data for date
        entry.save()
    else:
        #log failure
        pass

def country_worker(date, country_name, iso):
    global credentials
    try:
        country_data_request = requests.get(credentials['countries_endpoint'], headers=credentials['headers'], params={"date": date, "iso": iso})
    except requests.exceptions.ConnectionError:
        time.sleep(15)
        country_data_request = requests.get(credentials['countries_endpoint'], headers=credentials['headers'], params={"date": date, "iso": iso})
    except Exception as e:
        raise e
    country_total_deaths_on_day = country_total_recovered_on_day = country_total_active_on_day = country_total_confirmed_on_day  = country_total_fr = total_regions = 0
    country_deaths_overall = country_recovered_overall = country_active_overall = country_confirmed_overall = 0
    if country_data_request.status_code == 200:
        country = Country.objects.create(iso=iso, name=country_name, time=date, time_as_string=str(date))
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
            reg = Region.objects.create(name=province, active=active, recoveries=recoveries, deaths=deaths, confirmed=confirmed, total_active=total_active, total_recoveries=total_recoveries, total_deaths=total_deaths, total_confirmed=total_confirmed, fatality_rate=f_rate, in_country=country, time=date, time_as_string=str(date))

        country.active = country_total_active_on_day
        country.recoveries = country_total_recovered_on_day
        country.deaths = country_total_deaths_on_day
        country.confirmed = country_total_confirmed_on_day
        country.total_active = country_active_overall
        country.total_deaths = country_deaths_overall
        country.total_recoveries = country_recovered_overall
        country.total_confirmed = country_confirmed_overall
        country.regions = total_regions
        # if (iso == "CAN"):
        #     print(
        #         f"{threading.current_thread().ident }   {country.deaths} {date}"
        #     )
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
        pass
        # sys.stderr.write(f"could not get population data for {country} on {date}")
    country.save()


def get_last_time():
    if (len(Last_update.objects.all()) < 1):
        Last_update.objects.create()
    last_date = Last_update.objects.get(pk=1)
    return last_date


def update_time(time, country):
    if (len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    current_time = datetime.date.today()
    last_date.time = time
    last_date.country = country
    last_date.save()
    print(
        f"State save complete. time is {last_date.time}. Country is {last_date.country}"
    )


def reset():
    if (len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty. Aborted reset.")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    last_date.time = datetime.date(2019, 12, 31)
    last_date.country = "Palau"
    last_date.save()


def populate_tables():
    locations = json.load(open("cleaned_data.json", "r"))
    countries = []
    for iso in locations:
        country_name = locations[iso]
        tup = [None,None]
        tup[0] = country_name
        tup[1] = iso
        countries.append(tup)

    country_index = 0
    last_time = get_last_time()
    date = last_time.time
    end_date = datetime.date.today()
    ###
    date = datetime.date(2020, 12, 31)
    end_date = datetime.date(2021,2,27) #remember to delete
    if date == end_date:
        return
    num_threads = multiprocessing.cpu_count() * 2
    pool = ThreadPoolExecutor(num_threads)
    try:
        while date <= end_date:
            print(f"retreiving for {date}")
            fetch_global_stats(date)
            for i in range(country_index, len(countries) - 1):
                country = countries[i][0]  #get iso
                iso = countries[i][1]
                pool.submit(country_worker,date=date, country_name=country ,iso=iso)
            date += day
    except Exception as e:
        print(e)

    finally:
        print("waiting on shutdown...")
        pool.shutdown()
        print("shutdown completed.")
        update_time(date, "n/a")

user_input = input("delete tables and repopulate? ")
if user_input.lower() == "y":
    Global.objects.all().delete()
    Country.objects.all().delete()
    populate_tables()

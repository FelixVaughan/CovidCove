import os
from requests.models import HTTPBasicAuth, HTTPError
from .models import * 
import sys 
import requests
import json
from dotenv import load_dotenv
import datetime
load_dotenv()




##############################################################################
#                            Time Model Helper                               #
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
    current_time = datetime.date.today().strftime("%Y-%m-%d")
    last_date.time = current_time
    last_date.save()

def reset():
    if(len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    last_date.time = "2019-12-31"
    last_date.save()


##############################################################################
#                            Data Fetching Functions                         #
##############################################################################
def get_api_info():
    try:
        api_info = {
            "countries_endpoint": os.environ['countries_endpoint'],
            "location_endpoint": os.environ['location_endpoint'],
            "provinces_endpoint": os.environ['province_location_endpoint'],
            "totals_endpoint": os.environ['total_states_endpoint'],
            "headers": {os.environ['api_key']: os.environ['key'], os.environ['host_addr']: os.environ['host']}
        }
    except KeyError:
        sys.stderr.write("FATAL ERROR: could not obtain api credentials!")
        sys.exit(1)
    return api_info
    
def transform_data(countries):
        new_data = {}
        print("in transform data")
        f = open('custom.geo.json')
        coords_data = json.load(open('custom.geo.json', 'r'))['features']
        for country in countries:
            iso = country['iso']
            new_data[iso] = {}
            new_data[iso]['name'] = country['name']
            new_data[iso]['provinces'] = []
            new_data[iso]['coordinates'] = []
            provinces = country['provinces'] 
            if provinces: 
                for province in provinces:
                    new_data[iso]['provinces'].append(province['province'])

        for data in coords_data:
            try:
                iso = data['properties']['iso_a3']
                coords = data['geometry']['coordinates'] #might not even need this, could possibly do a cross reference. Might be good to have tho
                new_data[iso]['coordinates'] = coords
            except KeyError:
                print(f"Error occured on iso {iso} for coored {coords}")
                continue
        save_to_file = open("./cleaned_data","w")
        save_to_file.write(json.dumps(new_data))
        save_to_file.close()
        f.close()
        
def get_api_data():
    credentials = get_api_info()

    headers=credentials['headers']
    countries_request = requests.get(credentials['locations_endpoint'], headers=headers)
    if[countries_request.status_code == "ok"]:
        countries = countries_request.json()['data']
        cnt = countries
        counter = 0
        for c in cnt:
            prov_params = {'iso': c['iso']}
            provs = requests.get(credentials['province_location_endpoint'], headers=headers, params=prov_params).json()['data']
            countries[counter]['provinces'] = provs
            counter += 1
        transform_data(countries)
    else:
        raise HTTPError


def populate_tables():
    last_update = get_last_time()
    start = datetime.datetime.strptime(last_update, "%Y-%m-%d")
    end = datetime.today().strptime("%Y-%m-%d")



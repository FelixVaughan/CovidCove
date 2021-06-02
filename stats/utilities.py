import os
from requests.models import HTTPBasicAuth, HTTPError
from .models import * 
import sys 
import requests
import json

class Populator:
    CRED = ""
    HOST = ""

    def __init__(self):
        try:
            self.CRED = os.environ['CovidCoveCred']
            self.HOST = os.environ['CovidCoveHost']
        except KeyError as e:
            print("Could Not Obtain API credentials!")
            sys.exit(2)

    def get_location_data(self):
        headers={"x-rapidapi-key": self.CRED, "x-rapidapi-host": self.HOST}
        countries_endpoint = "https://covid-19-statistics.p.rapidapi.com/regions"
        countries_request = requests.get(countries_endpoint, headers=headers)
        if[countries_request.status_code == "ok"]:
            countries = countries_request.json()['data']
            cnt = countries
            counter = 0
            for c in cnt:
                prov_params = {'iso': c['iso']}
                provinces_endpoint = "https://covid-19-statistics.p.rapidapi.com/provinces"
                provs = requests.get(provinces_endpoint, headers=headers, params=prov_params).json()['data']
                countries[counter]['provinces'] = provs
                print(countries)
                counter += 1
            self.transform_data(countries)
        else:
            raise HTTPError

    def transform_data(self, countries):
        new_data = {}
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
            iso = data['properties']['iso_a3']
            coords = data['geometry']['coordinates'] #might not even need this, could possibly do a cross reference. Might be good to have tho
            new_data[iso]['coordinates'] = coords
        
        

pop = Populator()
pop.get_location_data()

#TODO
# get longtitude and latitude data for countries
# get data according to time
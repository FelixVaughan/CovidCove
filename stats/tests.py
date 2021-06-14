from django.test import TestCase
import datetime
from .utilities import *
from .models import * 
import json 
import sys


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
    while current_date < end:
        # global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": start})
        # if(global_data_request.status_code == 200):
        #     data = global_data_request.json()['data']
        #     entry = Global()
        #     if(data):
        #         entry.confirmed = data['confirmed']
        #         entry.deaths = data['deaths'] 
        #         entry.recoveries = data['recovered']
        #         entry.active = data['active']
        #         entry.fatality_rate = data['fatality rate']
        #     #entry.save()
        #     else:
        #         pass
        #         #log could not get data for date            
        # else:
        #     #log failure
        #     pass

        try:
            locations = json.load(open("cleaned_data.json","r"))
        except FileNotFoundError:
            sys.stderr.write("There does not appear to be a 'cleaned_data.json' (location) file")
            sys.exit(1)
        for location in locations:
            country_name = locations[location]['name']
            country_data_request = requests.get(credentials['countries_endpoint'], headers=headers, params={"date": current_date, "iso": location})
            total_deaths = total_recovered = total_active = total_confirmed = total_fr = total_regions = 0 
            if country_data_request.status_code == 200:
                country = Country.objects.create(iso=location, name=country_name, time=current_date)
                areas = country_data_request.json()['data'] #note sometimes area IS the country in the case of only one entry
                for area in areas:
                    confirmed = area['confirmed']
                    deaths = area['deaths']
                    recoveries = area['recovered']
                    active = area['active']
                    f_rate = area['fatality']
                    coords = area['region']['lat']+ " "+area['region']['long'] 
                    province = area['region']['province']
                    total_deaths += deaths
                    total_recovered += recoveries
                    total_active += active
                    total_confirmed += confirmed
                    total_fr += f_rate
                    total_regions += 1 
                    if province == "": #means these are country level stats, not provincial
                        continue
                    Region.objects.create(name=province, active=active, recoveries=recoveries, deaths=deaths, confirmed=confirmed, fatality_rate=f_rate, coordinates=coords, in_country=country, time=current_date) 
                country.active = total_active
                country.recoveries = total_recovered
                country.deaths = total_deaths
                country.confirmed = total_confirmed
                country.fatality_rate = (total_fr)/total_regions
            else:
                #log could not get data for date
                pass
        current_date += delta
    #update_time()

#populate_tables()

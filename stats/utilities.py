from functools import wraps
import os
from requests.models import HTTPBasicAuth, HTTPError
from .models import *
import sys
import requests
import json
import time
from dotenv import load_dotenv
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math
from .  credentials import get_credentials
credentials = get_credentials()
load_dotenv()



def create_line_plot(df, x, column, attr, title, themes):
    print(f"\n\n\nTITLE IS {title}\n\n\n")
    fig = px.scatter(df,
                     y=column,
                     x=x,
                     color=attr,
                     title=title,
                     custom_data=[attr])

    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear')
    fig.update_layout(
        font_color=themes["sundance_yellow"],
        height=300,
    )
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    return fig


def create_bar_plot(df, x, y, title, themes):
    fig = px.bar(df, x=x, y=y, color=x, title=title)
    fig.update_layout(font_color=themes["sundance_yellow"])
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    return fig


def create_pie_plot(df, value, names, title, themes):
    fig = px.pie(df,
        values=value,
        names=names,
        title=title,
        hover_data=['name', 'deaths', 'recoveries']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(font_color=themes["sundance_yellow"], height=650, width=880)
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    return fig

def create_choro_plot(df, value, themes):
    fig = px.choropleth(
        df,
        locations='iso',
        color=value,
        color_continuous_scale="Viridis",
        range_color=(0, 12),
        hover_data=['name', 'deaths','recoveries', 'active', 'fatality_rate']
    )  #used to negate a 'divide by zero' error on countries with 0 cases, deaths, recoveries, etc...
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.layout.update(dragmode=False)
    fig.update_layout(
        font_color=themes["sundance_yellow"],
        template = "plotly_dark",
        hoverlabel=dict(
                bgcolor="rgb(215,226,40)",
                font=dict(color='#ffffff', size=14
            ),
        ),
        height=600
    )

    return fig

def create_radar_plot(df, themes):
    categories = [
        "Total Active/Total Recoveries", "Total deaths/Total Recoveries", "Total Confirmed / Total Active", "Population"
    ]
    fig = go.Figure()
    for frame in df.itertuples():
        if ((frame.total_recoveries == 0 or frame.total_active == 0) or (frame.total_deaths == 0 or frame.fatality_rate == 0)): #oof
            continue
        y = abs(math.log(frame.total_active / frame.total_recoveries,10))
        x = abs(math.log(frame.total_deaths / frame.total_recoveries, 10))
        z = abs(math.log(frame.total_confirmed / frame.total_active, 10))
        z0 = math.log(frame.pop, 10)/10
        fig.add_trace(
            go.Scatterpolar(r=[x, y, z, z0],
            theta=categories,
            name=frame.name,
            fill="toself"),
        )
    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(visible=True, range=[0.0, 3.0])),
        font_color=themes["sundance_yellow"],
        height=650,
        width=871)
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    return fig

def create_dataset(date, country):
    prov = pd.DataFrame.from_records(Country.objects.get(name=country, time_as_string=date).region_set.all().values())
    columns = [{"name": i, "id": i} for i in prov.columns]
    data = prov.to_dict("records")
    return columns, data




##############################################################################
#                            Last_time Model Helpers                          #
##############################################################################
def get_last_time():
    if(len(Last_update.objects.all()) < 1):
        Last_update.objects.create()
    last_date = Last_update.objects.get(pk=1)
    return last_date

def update_time(time, country):
    if(len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    current_time = datetime.date.today()
    last_date.time = time
    last_date.country = country
    last_date.save()
    print(f"State save complete. time is {last_date.time}. Country is {last_date.country}")

def reset():
    if(len(Last_update.objects.all()) < 1):
        sys.stderr.write("'Last_update' table is empty. Aborted reset.")
        sys.exit(1)
    last_date = Last_update.objects.get(pk=1)
    last_date.time = datetime.date(2019,12,31)
    last_date.country = "Palau"
    last_date.save()


##############################################################################
#                            Data Fetching Functions                         #
##############################################################################

def fetch_location_properties():
    global credentials
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
    global credentials
    last_time = get_last_time()
    start = last_time.time
    last_country = last_time.country
    country_set = False
    if(last_country == "Palau"):
        country_set = True
    end = datetime.date.today()
    if start == end:
        return
    day = datetime.timedelta(days=1)
    current_date = datetime.date(2021, 1, 1) #start
    country_name = ""
    headers=credentials['headers']
    try:
        while current_date <= end:
            print(f"collecting data for {current_date}")
            try:
                global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": current_date})
            except requests.exceptions.ConnectionError:
                time.sleep(15)
                global_data_request = requests.get(credentials['totals_endpoint'], headers=headers, params={"date": current_date})
                #sometimes due to too many connections a timeout occurs. This remedies that.
            if(global_data_request.status_code == 200):
                data = global_data_request.json()['data']
                entry = Global(time=current_date, time_as_string=str(current_date))
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
            try:
                locations = json.load(open("cleaned_data.json","r"))
            except FileNotFoundError:
                fetch_location_properties()
                locations = json.load(open("cleaned_data.json","r"))
            for iso in locations:
                country_name = locations[iso]
                if(country_set == False):
                    print(f"skipping {country_name}")
                    if(country_name == last_country):
                        country_set = True
                    continue
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
                    sys.stderr.write(f"could not get population data for {country} on {current_date}")
                country.save()

            current_date += day
        now = datetime.date.today().strftime("%Y-%m-%d")
    except Exception as e:
        sys.stderr.write(f"Unexpected error:\n{e}\nSaving state...")
        sys.stdout.write(f"Unexpected error:\n{e}\nSaving state...")
    finally:
        update_time(current_date,country_name)


def clear_tables():
    Global.objects.all().delete()
    Country.objects.all().delete()
    Region.objects.all().delete()

def populator():
    uin = input("clear tables (y/n)? ")
    reset_r = input("reset update records (y/n)? ")
    # if uin.lower() == "y":
    #     clear_tables()
    # if reset_r.lower() == "y":
    #     reset()
    populate_tables()
#populator()
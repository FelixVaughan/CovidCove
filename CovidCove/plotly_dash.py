import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Div import Div
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
import sys
from datetime import date
from datetime import datetime
import pandas as pd
import numpy as np
from stats.models import *
import plotly.express as px
import plotly.graph_objects as go
import time

############################################Init/Server Wide Variables############################################

country_dataset = pd.DataFrame.from_records(Country.objects.all().values())
country_dataset['deaths'] = country_dataset['deaths'].apply(lambda x : 0 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db
country_dataset['pop'] = country_dataset['pop'].apply(lambda x : 1000000 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db
global_dataset = pd.DataFrame.from_records(Global.objects.all().values())
global_dataset['deaths'] = global_dataset['deaths'].apply(lambda x : 0 if x < 0 else x)
global_dataset['pop'] = 1000000
available_dates = country_dataset['time'].drop_duplicates().tolist() #note, data is sorted by default

##########################################End Init/Server Wide Variables##########################################



#####################Graph Creators####################

def create_line_plot(df, x, column, attr, title):
    fig = px.scatter(df, y=column, x=x, color=attr,  title=title, custom_data=[attr])
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear')
    return fig


def create_bar_plot(df, x, y, title, attr):
    fig = px.bar(df, x=x, y=y, color=attr, title=title)
    return fig


def create_pie_plot(df, plot_val, names, title):
    fig = px.pie(df,
                 values=plot_val,
                 names=names,
                 title=title,
                 hover_data=['name', 'deaths', 'recoveries'])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

######################End Graph Creators######################


app = DjangoDash('dash_app')
app.layout = html.Div([
    html.Div(
        [
            html.Div(
                [
                    dcc.DatePickerRange(
                        id="date_range_picker",
                        min_date_allowed=available_dates[0],
                        max_date_allowed=available_dates[len(available_dates) -
                                                         1],
                        initial_visible_month=available_dates[0],
                        end_date=date.today()),
                    dcc.Dropdown(id='stat_to_plot_choice',
                                 options=[{
                                     'label': i,
                                     'value': i
                                 } for i in country_dataset.columns],
                                 value=country_dataset.columns[0]),
                    dcc.Store(id="data_store"),
                ],
                id="data_picker_container",
            ),
            html.Div([
                dcc.Graph(id="country_data_line_plot"),
                dcc.Graph(id="global_data_line_plot"),
            ],
                     id="line_plots_container"),
            html.Div([
                dcc.Graph(id="country_bar_chart"),
                dcc.Graph(id="country_pie_chart"),
                dcc.Graph(id="global_choropleth_map"),
                dcc.Graph(id='radar_chart'),
                dash_table.DataTable(
                    id="province_display",
                    columns=[{
                        "name": i,
                        "id": i
                    } for i in [""]],
                    data=country_dataset.head().to_dict('records'),
                ),
            ],
                     id="discrete_plots_container"),
        ],
        id="stat_component_div",
    )
])




@app.callback(Output('country_data_line_plot', 'figure'),
              Output('global_data_line_plot', 'figure'),
              Input('stat_to_plot_choice', 'value'),
              Input('date_range_picker', 'start_date'),
              Input('date_range_picker', 'end_date')
    )
def display_line_graphs(column, start, end):
    time_query = True
    country_fig = {}
    global_fig = {}
    if column:
        if start and end:
            start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            time_query = ((country_dataset.time >= start) & (country_dataset.time <= end))
        elif start:
            start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            time_query = country_dataset.time >= start
        elif end:
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            time_query = country_dataset.time >= end
        data = country_dataset[time_query]
        data2 = global_dataset[time_query]
        country_fig = create_line_plot(data, "time", column, "name", f"Time vs. {column.capitalize()} by Nation")
        global_fig = create_line_plot(data2, "time", column, "name" ,f"Time vs. {column.capitalize()} (Wordlwide)")
    return country_fig, global_fig

@app.callback(
    Output("global_choropleth_map","figure"),
    Input("global_data_line_plot","clickData"),
    Input('stat_to_plot_choice', 'value'),
)
def update_world_map(data, value):
    date =  data['points'][0]['x']
    query = country_dataset.time_as_string == date
    df = country_dataset[query]
    df[value] = df[value].apply(lambda x: 1 if x < 1 else x)
    df[value] = np.log10(df[value])
    fig = px.choropleth(df, locations='iso', color=value, hover_data=['name','deaths']) #used to negate a 'divide by zero' error on countries with 0 cases, deaths, recoveries, etc...
    return fig




@app.callback(
    Output("country_pie_chart", "figure"),
    Output("country_bar_chart", "figure"),
    Input("global_data_line_plot", "clickData"),
    Input('stat_to_plot_choice', 'value'),
)
def update_global_pie_and_graph_chart(data, value):
    pie = bar = {}
    date = data['points'][0]['x']
    query = country_dataset.time_as_string == date
    df = country_dataset[query]
    pie = px.pie(df, values=value, names='name', title=f"{value} by Country")
    pie.update_traces(textposition='inside')
    bar = px.bar(df, x='name', y=value, color='name')
    return pie, bar

@app.callback(
    Output("province_display", "columns"),
    Output("province_display", "data"),
    Input("country_data_line_plot", "clickData"),
)
def province_display(data):
    date = data['points'][0]['x']
    country = data['points'][0]['customdata'][0]
    prov = pd.DataFrame.from_records(Country.objects.get(name=country, time_as_string=date).region_set.all().values())
    columns = [{"name": i, "id": i} for i in prov.columns]
    data = prov.to_dict("records")
    return columns, data

@app.callback(
    Output("radar_chart", "figure"),
    Input("global_data_line_plot", "clickData"),
)
def update_radar_chart(data):
    date = data['points'][0]['x']
    query = country_dataset.time_as_string == date
    df = country_dataset[query]
    categories = ["total_deaths","total_active", "fatality_rate"]
    fig = go.Figure()
    for frame in df.itertuples():
        fig.add_trace(go.Scatterpolar(
            r=[frame.total_deaths, frame.total_active, frame.fatality_rate],
            theta=categories,
            fill='toself',
            name=frame.name
        ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
    return fig

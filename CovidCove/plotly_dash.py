import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Div import Div
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
import sys
from datetime import date
from datetime import datetime
import pandas as pd
from stats.models import *
import plotly.express as px


######################################################################################################
#                                     Init/Server Wide Variables                                     #
######################################################################################################

country_dataset = pd.DataFrame.from_records(Country.objects.all().values())
country_dataset['deaths'] = country_dataset['deaths'].apply(lambda x : 0 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db
global_dataset = pd.DataFrame.from_records(Global.objects.all().values())
global_dataset['deaths'] = global_dataset['deaths'].apply(lambda x : 0 if x < 0 else x)
available_dates = country_dataset['time'].drop_duplicates().tolist() #note, fata is sorted by default

######################################################################################################
#                                    End Init/Server Wide Variables                                  #
######################################################################################################

app = DjangoDash('dash_app')   # replaces dash.Dash
app.layout = html.Div([
    html.Div(
        [
            html.Div(
                [
                    dcc.DatePickerRange(
                        id="date_range_picker",
                        min_date_allowed=available_dates[0],
                        max_date_allowed=available_dates[len(available_dates) - 1],
                        initial_visible_month = available_dates[0],
                        end_date=date.today()
                    ),

                    dcc.Dropdown(
                        id='stat_to_plot_choice',
                        options=[{'label': i, 'value': i} for i in country_dataset.columns],
                        value=country_dataset.columns[0]
                    ),

                    dcc.Store(id="data_store"),
                ],
                id="data_picker_container",
            ),

            html.Div(
                [
                    dcc.Graph(id="country_data_line_plot"),
                    dcc.Graph(id="global_data_line_plot"),
                ],
                id="line_plots_container"
            ),
        ],
        id="stat_component_div",
    )

])


def create_line_plot(df, x, column, attr, title):
    fig = px.scatter(df, y=column, x=x, color=attr, title=title)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear')
    return fig

@app.callback(Output('country_data_line_plot', 'figure'),
              Output('global_data_line_plot', 'figure'),
              Input('stat_to_plot_choice', 'value'),
              Input('date_range_picker', 'start_date'),
              Input('date_range_picker', 'end_date'))
def display_country_line_graph(column, start, end):
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
        global_fig = create_line_plot(data2, "time", column, "name", f"Time vs. {column.capitalize()} (Wordlwide)")
    return country_fig, global_fig


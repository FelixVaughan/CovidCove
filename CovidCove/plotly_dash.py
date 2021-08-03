import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Div import Div
from django.db.models.expressions import Col
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
from datetime import date
from datetime import datetime
import pandas as pd
import numpy as np
from stats.models import *
from stats.utilities import *
import plotly.express as px
import plotly.graph_objects as go
############################################Init/Server Wide Variables############################################
themes = {
    "abyss_blue": "#0c1c34",
    "dark_blue": "#00005a",
    "ink_blue": "#000072",
    "deep_ocean_blue": "#1e345a",
    "sundance_yellow": "#fdc30a",
    "banana_yellow": "#fce036",
    "caesar_red": "#Ff0c11",
    "angel_white": "#Ffffff",
    #note: not actual color names (as far as I know)
}
country_dataset = pd.DataFrame.from_records(Country.objects.all().values())
country_dataset['deaths'] = country_dataset['deaths'].apply(lambda x : 0 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db
country_dataset['pop'] = country_dataset['pop'].apply(lambda x : 1000000 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db
global_dataset = pd.DataFrame.from_records(Global.objects.all().values())
global_dataset['deaths'] = global_dataset['deaths'].apply(lambda x : 0 if x < 0 else x)
global_dataset['pop'] = 1000000
available_dates = country_dataset['time'].drop_duplicates().tolist() #note, data is sorted by default
min_date = available_dates[0]
max_date = available_dates[len(available_dates) - 1] #usually the current day
default_plot_value = "deaths"
default_country = "Canada"
excluded_option_values = ["id", "name", "time", "time_as_string", "iso", "regions", "pop"]
# default_country_time_dataset = country_dataset[(country_dataset.time >= min_date) & (country_dataset.time <= max_date)]
# default_global_time_dataset = global_dataset[(global_dataset.time >= min_date) & (global_dataset.time <= max_date)]
# default_country_line_plot = create_line_plot(default_country_time_dataset, "time", default_plot_value, "name", f"Time vs. {default_plot_value.capitalize()} by Nation", themes)
# default_global_line_plot = create_line_plot(default_global_time_dataset, "time", default_plot_value, "name", f"Time vs. {default_plot_value.capitalize()} (Wordlwide)", themes)
# default_pie_plot = create_pie_plot(default_country_time_dataset, default_plot_value, "name", f"{default_plot_value} by Country", themes)
# default_bar_plot = create_bar_plot(default_country_time_dataset, "name", default_plot_value, f"{default_plot_value}", themes)
# default_choro_plot = create_choro_plot(default_country_time_dataset, default_plot_value, themes)
# default_radar_plot = create_radar_plot(default_country_time_dataset, themes)
# default_data_set = create_dataset(max_date, default_country)
##########################################End Init/Server Wide Variables##########################################


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.layout.plot_bgcolor = themes["deep_ocean_blue"]
    fig.layout.paper_bgcolor = themes["deep_ocean_blue"]
    fig.update_layout(font_color=themes["sundance_yellow"])
    return fig

def select_dataset(input_dataset):
    dataset = {}
    if input_dataset["df"]:
        dataset = pd.read_json(input_dataset['df'])
    else:
        dataset = country_dataset
    return dataset

app = DjangoDash(
    'dash_app',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width initial-scale=1.0"}]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.DatePickerRange(
                            id="date_range_picker",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            initial_visible_month=available_dates[0],
                            end_date=date.today()
                        ),
                    ],
                    width=3,
                ),

                dbc.Col(
                    [
                        dcc.Dropdown(id='stat_to_plot_choice',
                            options=[{
                                'label': i,
                                'value': i
                            } for i in country_dataset.columns.difference(
                                excluded_option_values)],
                            value=country_dataset.columns[0]
                        ),
                    ],
                    width=3,
                ),

                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='countries_to_plot',
                            multi=True,
                            options=[{
                                'label': i,
                                'value': i
                            } for i in country_dataset.name],
                            value=['Canada', 'Brazil'],
                        ),
                    ],
                    width=6
                ),
            ],
            align="center",
            style={
                "padding-top": "10px",
                "padding-bottom": "10px"
            }
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="global_data_line_plot",
                            figure=blank_fig(),
                            style={"padding-bottom": "1em"}
                        ),

                        dcc.Graph(
                            id="country_data_line_plot",
                            figure=blank_fig(),
                        ),
                    ],
                    className="col-md-6",
                ),

                dbc.Col(
                    [
                        dcc.Graph(
                            id="global_choropleth_map",
                            figure=blank_fig(),
                            style={"height":"99%"},
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
            className="justify-content-start",
            style={"padding-bottom": "2em"},
            id="line_plot_container",
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="country_pie_chart",
                            figure=blank_fig(),
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id='radar_chart',
                            figure=blank_fig(),
                        ),
                    ],
                    width=6,
                ),
            ],
            className="row align-items-center",
            style={"padding-top": "0.5em", "padding-bottom": "1em"}
        ),
        dcc.Store(id="data_store"),


        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="country_bar_chart",
                            figure=blank_fig(),
                        ),
                    ],
                ),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dash_table.DataTable(
                            id="province_display",
                            columns=[{
                                "name": i,
                                "id": i
                            } for i in [""]],
                            style_header={
                                'backgroundColor': themes["deep_ocean_blue"],
                                'color': themes["sundance_yellow"],
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'backgroundColor': themes['deep_ocean_blue'],
                                'color': themes['banana_yellow'],
                            },
                            data=country_dataset.head().to_dict('records'),
                        ),
                    ],
                ),
            ],
        ),     
    ],
    style={"backgroundColor": themes["abyss_blue"]},
    fluid=True,
)



@app.callback(
    Output('country_data_line_plot', 'figure'),
    Output('global_data_line_plot', 'figure'),
    Input('stat_to_plot_choice', 'value'),
    Input('date_range_picker', 'start_date'),
    Input('date_range_picker', 'end_date'),
    Input("data_store", "data"),
)
def display_line_graphs(column, start, end, countries=None):
    dataset=select_dataset(countries)
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
        data = dataset[time_query]
        data2 = global_dataset[time_query]
        country_fig = create_line_plot(data, "time", column, "name", f"Time vs. {column.capitalize()} by Nation", themes)
        global_fig = create_line_plot(data2, "time", column, "name" ,f"Time vs. {column.capitalize()} (Worldwide)", themes)
    return country_fig, global_fig

@app.callback(
    Output("global_choropleth_map", "figure"),
    Input("global_data_line_plot", "clickData"),
    Input('stat_to_plot_choice', 'value'),
    Input("data_store", "data"),
)
def update_world_map(data, value, countries=None):
    date =  data['points'][0]['x']
    query = country_dataset.time_as_string == date
    df = country_dataset[query]
    df[value] = df[value].apply(lambda x: 1 if x < 1 else x)
    df[value] = np.log10(df[value])
    fig = create_choro_plot(df, value, themes)
    return fig


@app.callback(
    Output("country_pie_chart", "figure"),
    Output("country_bar_chart", "figure"),
    Input("global_data_line_plot", "clickData"),
    Input("stat_to_plot_choice", "value"),
    Input("data_store", "data"),
)
def update_global_pie_and_graph_chart(data, value, countries=None):
    dataset = select_dataset(countries)
    pie = bar = {}
    date = data['points'][0]['x']
    query = dataset.time_as_string == date
    df = dataset[query]
    title = f"{value.capitalize()} by Country"
    pie = create_pie_plot(df, value, 'name', title, themes)
    bar = create_bar_plot(df, 'name', value, title, themes)
    return pie, bar

@app.callback(
    Output("province_display", "columns"),
    Output("province_display", "data"),
    Input("country_data_line_plot", "clickData"),
    Input("data_store", "data"),
)
def province_display(data, countries=None):
    date = data['points'][0]['x']
    country = data['points'][0]['customdata'][0]
    return create_dataset(date, country)

@app.callback(
    Output("radar_chart", "figure"),
    Input("global_data_line_plot", "clickData"),
    Input("data_store", "data"),
)
def update_radar_chart(data, countries=None):
    dataset = select_dataset(countries)
    date = data['points'][0]['x']
    query = dataset.time_as_string == date
    df = dataset[query]
    fig = create_radar_plot(df, themes)
    return fig


@app.callback(
    Output("data_store", "data"),
    Input("countries_to_plot","value"),
)
def create_filtered_dataframe(countries):
    data = {}
    data['df'] = ""
    if countries:
        df = country_dataset[country_dataset.name.isin(countries)]
        data["df"] = df.to_json(date_format='iso')
    return data

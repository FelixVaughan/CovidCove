import dash
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
import pandas as pd
from stats.models import *
import plotly.express as px
app = DjangoDash('dash_app')   # replaces dash.Dash

dataset = pd.DataFrame.from_records(Country.objects.all().values())
dataset['deaths'] = dataset['deaths'].apply(lambda x : 0 if x < 0 else x) #should be removed when we do a fresh scrape as the issue has been fixed in the db


fig = px.scatter(dataset, x="time", y="pop", size="deaths", color="name")
app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig)
])

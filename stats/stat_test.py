from math import log10
from .models import *
import pandas as pd
import json
import plotly.express as px 
import dash
import dash_core_components as dcc
import dash_html_components as html


geo_data = json.load(open("custom.geo.json","r"))
app = dash.Dash(__name__, external_stylesheets='https://codepen.io/chriddyp/pen/bWLwgP.css')
cdf = pd.DataFrame(list(Country.objects.all().values())) #country dataframe

#from stats import stat_test
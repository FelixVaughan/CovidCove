import pandas as pd
from . models import *

def get_country_dataframe(): #cleans and validates country data and presents usable datset with proper types and values
    country_dataset = pd.DataFrame.from_records(Country.objects.all().values())
    
def get_global_dataframe():
    global_dataset = pd.DataFrame.from_records(Global.objects.all().values())

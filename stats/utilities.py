import os
from requests.models import HTTPBasicAuth, HTTPError
from .models import * 
import sys 
import requests

class populator:
    CRED = ""
    HOST = ""

    def __init__(self):
        try:
            CRED = os.environ['CovidCoveCRED']
            HOST = os.environ['CovidCoveHOST']
        except KeyError as e:
            print("Could Not Obtain API CREDentials!")
            sys.exit(2)

    def populate_with_countries(self):
        headers={
            "x-rapidapi-key": self.CRED,
            "x-rapidapi-HOST": self.HOST
        }
        req = requests.get("https://covid-19-statistics.p.rapidapi.com/regions", headers=headers)
        if[req.status_code == "ok"]:
            response = req.json()
            print(response)
        else:
            raise HTTPError


    def populate_with_regions_and_coordinates(self):
        pass

    def populate_db(self):
        pass

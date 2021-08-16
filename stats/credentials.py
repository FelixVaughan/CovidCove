import os
import sys

def get_credentials():
    try:
        api_info = {
            "countries_endpoint": os.environ['countries_endpoint'],
            "location_endpoint": os.environ['location_endpoint'],
            "provinces_endpoint": os.environ['province_location_endpoint'],
            "totals_endpoint": os.environ['total_states_endpoint'],
            "population_endpoint": os.environ['population_endpoint'],
            "headers": {
                os.environ['api_key']: os.environ['key'],
                os.environ['host_addr']: os.environ['host']
            }
        }
    except KeyError:
        sys.stderr.write("FATAL ERROR: could not obtain api credentials!")
        sys.exit(1)
    return api_info

from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .utilities import get_last_time, update_time, reset, get_credentials, fetch_location_properties, populate_tables, clear_tables


@shared_task(name=get_last_time)
def get_last_time_bg():
    return 1

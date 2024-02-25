import os

import requests
from quarter_lib.logging import setup_logging

from helper.caching import ttl_cache

logger = setup_logging(__file__)

HABIT_TRACKER_MAPPING_URL = os.getenv("habit_list")
TASKER_MAPPING_URL = os.getenv("tasker_mapping")

@ttl_cache(ttl=60 * 60)
def get_habit_tracker_mapping_from_web():
    logger.info("getting habit tracker mapping from web")
    response = requests.get(HABIT_TRACKER_MAPPING_URL, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
    return response.json()

@ttl_cache(ttl=60 * 60)
def get_tasker_mapping_from_web():
    logger.info("getting habits from web")
    response = requests.get(TASKER_MAPPING_URL, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
    return response.json()

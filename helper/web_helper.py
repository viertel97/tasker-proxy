import requests
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging

from helper.caching import ttl_cache

logger = setup_logging(__file__)

MASTER_KEY, HABIT_TRACKER_MAPPING_BIN, TASKER_MAPPING_BIN, REWORK_EVENTS_BIN, ONENOTE_PAGES_BIN = get_secrets(
    [
        "jsonbin/masterkey",
        "jsonbin/habit_tracker_mapping-bin",
        "jsonbin/tasker_mapping-bin",
        "jsonbin/Rework-Events-bin",
        "jsonbin/OneNote-Pages-bin",
    ]
)

BASE_URL = "https://api.jsonbin.io/v3"

HABIT_TRACKER_MAPPING_URL = f"{BASE_URL}/b/{HABIT_TRACKER_MAPPING_BIN}/latest"
TASKER_MAPPING_URL = f"{BASE_URL}/b/{TASKER_MAPPING_BIN}/latest"
REWORK_EVENTS_URL = f"{BASE_URL}/b/{REWORK_EVENTS_BIN}/latest"
ONENOTE_PAGES_URL = f"{BASE_URL}/b/{ONENOTE_PAGES_BIN}/latest"


@ttl_cache(ttl=60 * 60)
def get_rework_events_from_web():
    logger.info("getting rework events from web")
    response = requests.get(
        REWORK_EVENTS_URL,
        headers={"User-Agent": "Mozilla/5.0", "X-Master-Key": MASTER_KEY},
    )
    return response.json()["record"]


@ttl_cache(ttl=60 * 60)
def get_habit_tracker_mapping_from_web():
    logger.info("getting habit tracker mapping from web")
    response = requests.get(
        HABIT_TRACKER_MAPPING_URL,
        headers={"User-Agent": "Mozilla/5.0", "X-Master-Key": MASTER_KEY},
    )
    return response.json()["record"]


@ttl_cache(ttl=60 * 60)
def get_tasker_mapping_from_web():
    logger.info("getting habits from web")
    response = requests.get(
        TASKER_MAPPING_URL,
        headers={"User-Agent": "Mozilla/5.0", "X-Master-Key": MASTER_KEY},
    )
    return response.json()["record"]


@ttl_cache(ttl=60 * 60 * 24)
def get_onenote_default_ids():
    logger.info("getting onenote pages")
    response = requests.get(
        ONENOTE_PAGES_URL,
        headers={"User-Agent": "Mozilla/5.0", "X-Master-Key": MASTER_KEY},
    )
    return response.json()["record"]

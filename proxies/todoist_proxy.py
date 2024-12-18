import requests

from helper.network_helper import get_url

URL = get_url("todoist-service")

async def run_todoist_sync_commands(commands):
    while True:
        requests.post(URL + "/sync", json={"commands": commands}).json()

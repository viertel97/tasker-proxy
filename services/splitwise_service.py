import requests
from quarter_lib.logging import setup_logging

logger = setup_logging(__file__)


def add_placeholder_to_splitwise(title : str) -> requests.Response:
    response = requests.post(
        "http://splitwise-service.custom.svc.cluster.local:80/add_expense_to_group",
        json={"group_name": "Inbox", "title": title},
    )
    return response
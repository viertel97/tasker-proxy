import requests

from helper.network_helper import get_url

URL = get_url("transcriber-service")

URL = "http://192.168.178.49:9200"


async def get_bookmark_transcriptions(path, xml_data):
	return requests.post(URL + "/bookmark_transcriptions", json={"path": path, "xml_data": xml_data}).json()

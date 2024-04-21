import requests

from config.configuration import TRANSCRIBER_SERVICE_URL


async def get_bookmark_transcriptions(path, xml_data):
    return requests.post(TRANSCRIBER_SERVICE_URL + "/bookmark_transcriptions",
                         json={"path": path, "xml_data": xml_data}).json()

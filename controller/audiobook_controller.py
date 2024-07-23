import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from json import dumps
from typing import Annotated

from fastapi import APIRouter, Form, UploadFile
from quarter_lib.logging import setup_logging

from models.tasks import audiobook_finished, zotero_task
from proxies.todoist_proxy import run_todoist_sync_commands
from proxies.transcriber_proxy import get_bookmark_transcriptions
from services.audiobook_service import add_audiobook_finished_task, add_audiobook_task

logger = setup_logging(__file__)
router = APIRouter(tags=["audiobook"])


@logger.catch
@router.post("/audiobook_bookmark")
async def create_todoist_zotero_task(item: zotero_task):
    await add_audiobook_task(item)


@logger.catch
@router.post("/audiobook_finished")
async def audiobook_finished(item: audiobook_finished):
    await add_audiobook_finished_task(item)


@logger.catch
@router.get("/test")
async def test():
    print("test")
    print("test")


@logger.catch
@router.post("/file/bookmark_file")
async def upload_file(path: Annotated[str, Form()], bookmark_file: UploadFile):
    contents = bookmark_file.file.read()
    xml_data = xml_to_dict(contents)

    transcription_result = await get_bookmark_transcriptions(path, xml_data)
    result_list = transcription_result["result_list"]
    title = transcription_result["title"]
    author = transcription_result["author"]
    command_list = []
    for transcribed_bookmark in result_list:
        content = transcribed_bookmark["title"] + " - add highlight to Zotero"

        if (
            "timestamp" in transcribed_bookmark
            and transcribed_bookmark["timestamp"] is not None
        ):
            transcribed_bookmark["timestamp"] = datetime.fromisoformat(
                transcribed_bookmark["timestamp"]
            )
            recording_timestamp = transcribed_bookmark["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            recording_timestamp = None
        description_dict = {
            "recognized_text_de": transcribed_bookmark["de"],
            "recognized_text_de_confidence": transcribed_bookmark["de_confidence"],
            "recognized_text_en": transcribed_bookmark["en"],
            "recognized_text_en_confidence": transcribed_bookmark["en_confidence"],
            "recording_timestamp": recording_timestamp,
            "author": author,
            "title": title,
            "file_name": bookmark_file.filename,
            "file_position": transcribed_bookmark["file_position"],
            "annotation": transcribed_bookmark["annotation"],
        }
        desc = (
            dumps(description_dict, indent=4, sort_keys=True, ensure_ascii=False)
            .encode("utf8")
            .decode()
        )
        generated_temp_id = "_" + str(uuid.uuid4())
        command_list.append(
            {
                "type": "item_add",
                "temp_id": generated_temp_id,
                "args": {
                    "content": content,
                    "description": desc,
                    "project_id": "2281154095",
                },
            }
        )
        command_list.append(
            {
                "type": "note_add",
                "args": {
                    "content": "",
                    "item_id": generated_temp_id,
                    "file_attachment": {
                        "file_name": transcribed_bookmark["upload_result"]["file_name"],
                        "file_size": transcribed_bookmark["upload_result"]["file_size"],
                        "file_type": transcribed_bookmark["upload_result"]["file_type"],
                        "file_url": transcribed_bookmark["upload_result"]["file_url"],
                    },
                },
            }
        )

    sync_command_results = await run_todoist_sync_commands(command_list)
    if sync_command_results.status_code != 200:
        logger.error("Error while adding to Todoist")
        raise Exception("Error while adding to Todoist " + sync_command_results.text)
    logger.info(sync_command_results)
    message = (
        "Transcribed {} bookmarks for {} by {}".format(len(result_list), title, author)
        + " and added them to Todoist"
    )

    logger.info(message)
    return message


def xml_to_dict(data):
    root = ET.XML(data)
    data = []
    for item in root.findall("./bookmark"):  # find all projects node
        data_dict = {}  # dictionary to store content of each projects
        data_dict.update(item.attrib)  # make panelist_login the first key of the dict
        for child in item:
            data_dict[child.tag] = child.text
        data.append(data_dict)
    logger.info(data)
    return data

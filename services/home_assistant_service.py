import os

from loguru import logger

from services.todoist_service import add_task

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


async def add_washer_finished_task():
    task = await add_task(
        "Waschmaschine leeren + Wäsche aufhängen", due="in 0 minute", project_id="2244725398"
    )
    logger.info(task)
    task = await add_task(
        "Wäsche abhängen", due="in 2 days", project_id="2244725398"
    )
    logger.info(task)


async def add_dishwasher_finished_task():
    task = await add_task(
        "Spülmaschine öffnen", due="in 0 minute", project_id="2244725398"
    )
    logger.info(task)
    task = await add_task(
        "Spülmaschine ausräumen + einräumen", due="tomorrow", project_id="2244725398"
    )
    logger.info(task)

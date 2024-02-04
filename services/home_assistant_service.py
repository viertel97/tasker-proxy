import os

from loguru import logger

from services.todoist_service import add_task_with_check

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


async def add_washer_finished_task():
    task = await add_task_with_check(
        "Waschmaschine leeren + Wäsche aufhängen", due="in 0 minute", project_id="2244725398"
    )
    logger.info(task)
    task = await add_task_with_check(
        "Wäsche abhängen", due="in 2 days", project_id="2244725398"
    )
    logger.info(task)

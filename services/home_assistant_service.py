from quarter_lib.logging import setup_logging

from services.todoist_service import add_task_with_check

logger = setup_logging(__file__)


async def add_washer_finished_task():
    task = await add_task_with_check(
        "Waschmaschine leeren + Wäsche aufhängen",
        due="in 0 minute",
        project_id="2244725398",
    )
    logger.info(task)
    task = await add_task_with_check(
        "Wäsche abhängen", due="in 2 days", project_id="2244725398"
    )
    logger.info(task)

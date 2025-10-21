from quarter_lib.logging import setup_logging

from services.todoist_service import add_task_with_check, THIS_WEEK_PROJECT_ID

logger = setup_logging(__file__)


async def add_washer_finished_task():
	task = await add_task_with_check(
		"Waschmaschine leeren + Wäsche aufhängen",
		due="in 0 minute",
		project_id=THIS_WEEK_PROJECT_ID,
		labels=["Analogue", "filtered"],
	)
	logger.info(task)
	task = await add_task_with_check("Wäsche abhängen", due="in 2 days", project_id=THIS_WEEK_PROJECT_ID, labels=["Analogue", "filtered"])
	logger.info(task)


async def add_dishwasher_finished_task():
	task = await add_task_with_check(
		"Spülmaschine leeren",
		due="in 0 minute",
		project_id=THIS_WEEK_PROJECT_ID,
		labels=["Analogue", "filtered"],
	)
	logger.info(task)

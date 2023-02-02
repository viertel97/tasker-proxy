# Tasker-Proxy

This application acts as a proxy between the Tasker Android app and other services.
* It receives POST requests from Tasker, refines them, and
  * writes them in the correct format to a database
  * generates Todoist tasks from them
  * transcribes the voice message and writes the output to a Monica micro-journal
* The GET requests from Tasker are for retrieving data from the database or Todoist to generate dynamic notifications.

Tasker can also be used on Tablet or Android TV, which is also used to gather data and implement processes.
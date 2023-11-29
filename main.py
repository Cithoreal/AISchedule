import json
import asyncio
from datetime import datetime, timedelta
from caldav_api import *

from openai_process import *


cal_dict = {"personal": 0, "school": 1, "work": 2, "time blocks": 3, "holidays": 4}
async def main():
    print("Start Messaging!")
    while True:
        input_message = input()
        print(await message_ai(input_message))


async def message_ai(message):
  
    send_message(message)
    run = start_run()
    run = await retrieve_run(run)
    #If completed, send the message to the user
    run_status = get_run_status(run)
    # This is the main part of the program that needs significant work
    #Check action parameters to see if it is a create, update, query, or delete
    while (run_status == "requires_action"):
        #if name is list_upcoming, then get the list from caldav, format it, and send it as a message to the thread

        if ("event" in run.required_action.submit_tool_outputs.tool_calls[0].function.arguments):
            #print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            #process_event(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            schedule_event(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            complete_tool_run(run, "Event already exists and information was updated.")

            #schedule_event(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
        elif ("task" in run.required_action.submit_tool_outputs.tool_calls[0].function.arguments):
            #print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            #schedule_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            process_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            complete_tool_run(run)
            #run = retrieve_run

            #schedule_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
        run_status = get_run_status(run)

    message = retrieve_message()
    return(message)

#async def message_ai(message):
#    ai_response = send_message(message, "user", "Chris")

    return ai_response

def process_event(args):
    args = json.loads(args)
    print(args)
    if args["action"] == "create" or args["action"] == "update":
        #query the calendar to see if the event exists
        #if it does, update it
        #if not, create it
        pass
        schedule_event(args)
    elif args["action"] == "delete":
        cal_delete_event(args["CALENDAR"], args["url"])
    elif args["action"] == "query":
        cal_list_events(args["CALENDAR"], args["dtstart"], args["dtend"])
    #if query
    #Check if it exists
    #Just return details if so
    #if delete
    #delete if exists, fine if otherwise
    print(args)

def process_task(args):
    print(args)


def list_events():

    # Get the current time and the end time for the event listing
    now = datetime.now()
    end_time = now + timedelta(days=7)  # List events for the next 7 days

    # Call the list_events function from the CalDav interaction code
    events = cal_list_events(1, now, end_time)

    # Format the list of events for Discord
    response_message = "*FROM THE CALENDAR API. USE THIS FOR REFERENCE. DON'T SHARE THE UIDs.* \n EVENTS:\n"
    if events:
        for event in events:
            response_message += f"**{event['summary']}**: {event['start'].strftime('%Y-%m-%d %H:%M')} - {event['end'].strftime('%Y-%m-%d %H:%M')} - URL:{event['url']} \n"
    else:
        response_message = "No upcoming events."

    # Send the list of events to the user
    return(response_message)


def list_tasks():
    tasks = cal_list_tasks(1)
    response_message = "TASKS:\n"
    if tasks:
        for task in tasks:
            response_message += f"**{task['summary']}** - Due Date: {task['due']} - URL:{task['url']}\n"
    return response_message
# Error handling


def schedule_event(event_details):
    event_summary = None
    event_date_start = None
    event_date_end = None
    event_description = None
    event_location = None
    event_category = None
    event_rrule = None
    print(event_details)
    cal = cal_dict[json.loads(event_details)["event"]["CALENDAR"]]
    if ("SUMMARY" in json.loads(event_details)["event"].keys()):
        event_summary = json.loads(event_details)["event"]["SUMMARY"]

    if ("DTSTART" in json.loads(event_details)["event"].keys()):
        event_date_start = datetime.fromisoformat(json.loads(event_details)["event"]["DTSTART"])

    if ("DTEND" in json.loads(event_details)["event"].keys()):
        event_date_end = datetime.fromisoformat(json.loads(event_details)["event"]["DTEND"])

    if ("DESCRIPTION" in json.loads(event_details)["event"].keys()):
        event_description = json.loads(event_details)["event"]["DESCRIPTION"]

    if ("LOCATION" in json.loads(event_details)["event"].keys()):
        event_location = json.loads(event_details)["event"]["LOCATION"]

    if ("CATEGORY" in json.loads(event_details)["event"].keys()):
        event_category = json.loads(event_details)["event"]["CATEGORY"]

    if ("RRULE" in json.loads(event_details)["event"].keys()):
        event_rrule = json.loads(event_details)["event"]["RRULE"]

    cal_create_event(cal, event_summary, event_date_start, event_date_end, event_description, event_location, event_category, event_rrule)

def schedule_task(task_details):

    task_summary = None
    task_due = None
    task_percent = None
    task_priority = None
    task_status = None
    task_description = None
    task_location = None
    task_category = None
    task_rrule = None
    cal = cal_dict[json.loads(task_details)["task"]["CALENDAR"]]
    if ("SUMMARY" in json.loads(task_details)["task"].keys()):
        task_summary = json.loads(task_details)["task"]["SUMMARY"]

    if ("DUE" in json.loads(task_details)["task"].keys()):
        task_due = datetime.fromisoformat(json.loads(task_details)["task"]["DTSTART"])

    if ("PERCENT" in json.loads(task_details)["task"].keys()):
        task_percent = json.loads(task_details)["task"]["PERCENT"]

    if ("PRIORITY" in json.loads(task_details)["task"].keys()):
        task_priority = json.loads(task_details)["task"]["PRIORITY"]
    
    if ("STATUS" in json.loads(task_details)["task"].keys()):
        task_status = json.loads(task_details)["task"]["STATUS"]

    if ("DESCRIPTION" in json.loads(task_details)["task"].keys()):
        task_description = json.loads(task_details)["task"]["DESCRIPTION"]

    if ("LOCATION" in json.loads(task_details)["task"].keys()):
        task_location = json.loads(task_details)["task"]["LOCATION"]

    if ("CATEGORY" in json.loads(task_details)["task"].keys()):
        task_category = json.loads(task_details)["task"]["CATEGORY"]

    if ("RRULE" in json.loads(task_details)["task"].keys()):
        task_rrule = json.loads(task_details)["task"]["RRULE"]

    cal_create_todo(cal, task_summary, task_due, task_percent, task_priority, task_status, task_description, task_location, task_category, task_rrule)


# Initialize and run the bot
if __name__ == "__main__":
    asyncio.run(main())
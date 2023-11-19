import json
import asyncio
from datetime import datetime, timedelta
from caldav_connection import *

from openai_process import *


async def main():
    print("Start Messaging!")
    while True:
        input_message = input()
        await message_ai(input_message)


async def message_ai(message):
    try:
        send_message(message)
        run = start_run()
        run = await retrieve_run(run)
        #If completed, send the message to the user
        while (run.status != "completed"):
            #if name is list_upcoming, then get the list from caldav, format it, and send it as a message to the thread
            if ("list_upcoming" in run.required_action.submit_tool_outputs.tool_calls[0].function.name):
                #print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                tasks = list_tasks()
                events = list_events()
                process_message(run)
                #print(events + tasks)
                send_message(events + tasks)
                run = start_run()
                run = await retrieve_run(run)
            elif ("event" in run.required_action.submit_tool_outputs.tool_calls[0].function.arguments):
                print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                process_message(run)
                #schedule_event(data.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            elif ("task" in run.required_action.submit_tool_outputs.tool_calls[0].function.arguments):
                print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                process_message(run)
                #schedule_task(data.required_action.submit_tool_outputs.tool_calls[0].function.arguments)

        data = retrieve_message()
        print(data)
        return(data)

    except Exception as e:
        error_message = f"An error occurred while processing your message: {str(e)}"
        print(error_message)



def list_events():
    try:
        # Get the current time and the end time for the event listing
        now = datetime.now()
        end_time = now + timedelta(days=7)  # List events for the next 7 days

        # Call the list_events function from the CalDav interaction code
        events = cal_list_events(now, end_time)

        # Format the list of events for Discord
        response_message = "*FROM THE CALENDAR API. USE THIS FOR REFERENCE. DON'T SHARE THE UIDs.* \n EVENTS:\n"
        if events:
            for event in events:
                response_message += f"**{event['summary']}**: {event['start'].strftime('%Y-%m-%d %H:%M')} - {event['end'].strftime('%Y-%m-%d %H:%M')}\n"
        else:
            response_message = "No upcoming events."

        # Send the list of events to the user
        return(response_message)

    except Exception as e:
        # Handle any errors that occur during event listing
        error_message = f"An error occurred while retrieving your events: {str(e)}"
        print(error_message)


def list_tasks():
    tasks = cal_list_tasks()
    response_message = "TASKS:\n"
    if tasks:
        for task in tasks:
            response_message += f"**{task['summary']}** - Due Date: {task['due']} - UID:{task['uid']}\n"
    return response_message
# Error handling


def schedule_event(event_details):
    event_summary = None
    event_date_start = None
    event_date_end = None
    event_description = None
    event_location = None
    event_category = None
    print(event_details)
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

    cal_create_event(event_summary, event_date_start, event_date_end, event_description, event_location, event_category)

def schedule_task(task_details):

    task_summary = None
    task_due = None
    task_percent = None
    task_priority = None
    task_status = None
    task_description = None
    task_location = None
    task_category = None

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

    cal_create_todo(task_summary, task_due, task_percent, task_priority, task_status, task_description, task_location, task_category)


# Initialize and run the bot
if __name__ == "__main__":
    asyncio.run(main())
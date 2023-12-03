import json
import asyncio
from datetime import datetime, timedelta
from caldav_api import *

from openai_schedule_assistant import *
from openai_chat_completion import *
import pytz

timezone = pytz.timezone("America/New_York")

cal_dict = {"personal": 0, "school": 1, "work": 2, "time blocks": 3, "holidays": 4}
#As caldav events and tasks get processed, add to the message cache with results that can be sent to the 
#AI once the current run is completed and start a new run to get the final message
message_cache = []
async def main():
    print("Start Messaging!")
    while True:
        input_message = input()
        print(await message_ai(input_message))


async def message_ai(message):
  
    assistant_send_message(message)
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


            process_event(json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments))
            run = complete_tool_run(run)

            #schedule_event(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
        elif ("task" in run.required_action.submit_tool_outputs.tool_calls[0].function.arguments):
            #print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            #schedule_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)

            process_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            run = complete_tool_run(run)
            #run = retrieve_run

            #schedule_task(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
        run_status = get_run_status(run)
    for (index, message) in enumerate(message_cache):
        assistant_send_message(message["content"], message["role"])
    run = start_run()
    run = await retrieve_run(run)
    message_cache.clear()
    message = retrieve_message()
    return(message)


def process_event(args):

    #Query the calendar for relevant list of events that match the criteria
    #If there is a list of events, send it to the chat completions API to determine if the event exists
    #Recieve the url if it exits
    print(args)
    #args to string
    dtstart = args["event"]["DTSTART"]
    #dtstart = datetime.strptime(dtstart, '%m/%d/%Y %H:%M:%S')
    #dtstart = timezone.localize(dtstart)
    dtend = args["event"]["DTEND"]
    #dtend = datetime.strptime(dtend, '%m/%d/%Y %H:%M:%S')
    #dtend = timezone.localize(dtend)
    event_list = query_events(datetime.fromisoformat(dtstart), datetime.fromisoformat(dtend))
    print(event_list)
    calendar_ai_add_message(json.dumps(args), "system", "Calendar")
    calendar_ai_add_message(event_list, "system", "Calendar")
    ai_response = calendar_ai_process_messages()
    print("AI Response", ai_response)
   #print(args)
    if args["action"] == "create" or args["action"] == "update":
        #query the calendar to see if the event exists
        if ("URL" not in ai_response["calendar_item"]): #not ai_response["calendar_item"]["URL"].startswith("https://")
            schedule_event("create",args)
            message_cache.append({"role": "system", "name": "Calendar", "content": "Event has been created."})
        else:
            message_cache.append({"role": "system", "name": "Calendar", "content": "Event already exists."})

            #Check if there is new information worth updating the event
            #Compare the args with the details from the event list
           # schedule_event("update",args, ai_response["calendar_item"]["URL"])
        #if it does, update it
        #if not, create it

    elif args["action"] == "delete":
        print("Deteling event")
        if ("URL" in ai_response["calendar_item"]):
            cal_delete_event(cal_dict[args["CALENDAR"]], ai_response["calendar_item"]["URL"])
            message_cache.append({"role": "system", "name": "Calendar", "content": "Event successfuly deleted."})
        else: 
            message_cache.append({"role": "system", "name": "Calendar", "content": "Event does not exist."})
    elif args["action"] == "query":
        cal_list_events(cal_dict[args["CALENDAR"]], args["dtstart"], args["dtend"])
    #if query
    #Check if it exists
    #Just return details if so
    #if delete
    #delete if exists, fine if otherwise

def process_task(args):
    print(args)
    #if create or update
    #check if exists
    #list all tasks and share with AI to determine if it exists



def query_events(dtstart, dtend):
    #print(dtstart , dtend)
    # Call the list_events function from the CalDav interaction code
    events = cal_list_events(dtstart, dtend)

    # Format the list of events for Discord
    response_message = "EVENT LIST:\n"
    if events:
        for event in events:
            response_message += f"**{event['summary']}**: {event['start'].strftime('%Y-%m-%d %H:%M')} - {event['end'].strftime('%Y-%m-%d %H:%M')} - URL: {event['url']} \n"
    else:
        response_message = "Empty"

    # Send the list of events to the user
    return(response_message)


def query_tasks():
    tasks = cal_list_tasks(1)
    response_message = "TASKS:\n"
    if tasks:
        for task in tasks:
            response_message += f"**{task['summary']}** - Due Date: {task['due']} - URL:{task['url']}\n"
    return response_message
# Error handling


def schedule_event(action, event_details, url = ""):
    event_summary = None
    event_date_start = None
    event_date_end = None
    event_description = None
    event_location = None
    event_category = None
    event_rrule = None
    print(event_details)
    cal = cal_dict[event_details["event"]["CALENDAR"]]
    if ("SUMMARY" in event_details["event"].keys()):
        event_summary = event_details["event"]["SUMMARY"]

    if ("DTSTART" in event_details["event"].keys()):
        event_date_start = datetime.fromisoformat(event_details["event"]["DTSTART"])

    if ("DTEND" in event_details["event"].keys()):
        event_date_end = datetime.fromisoformat(event_details["event"]["DTEND"])

    if ("DESCRIPTION" in event_details["event"].keys()):
        event_description = event_details["event"]["DESCRIPTION"]

    if ("LOCATION" in event_details["event"].keys()):
        event_location = event_details["event"]["LOCATION"]

    if ("CATEGORY" in event_details["event"].keys()):
        event_category = event_details["event"]["CATEGORY"]

    if ("RRULE" in event_details["event"].keys()):
        event_rrule = event_details["event"]["RRULE"]
    if action == "create":
        cal_create_event(cal, event_summary, event_date_start, event_date_end, event_description, event_location, event_category, event_rrule)
    elif action == "update":
        cal_update_event(cal, url, event_summary, event_date_start, event_date_end, event_description, event_location, event_category, event_rrule)

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
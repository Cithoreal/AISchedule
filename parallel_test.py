from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def schedule_task(summary):
    """Schedule a task"""
    return json.dumps({"result": "Successful", "task_summary": summary})
 

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "Schedule tasks for french homework tomorrowat 5pm and biology homework at 6pm the day after"}]
    tools = [
{
  "type": "function",
  "function": {
    "name": "manage_caldav_task",
    "description": "Create, update, or query CalDAV tasks",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": [
            "create",
            "update",
            "delete",
            "query"
          ],
          "description": "The action to be performed on the CalDAV task"
        },
        "task": {
          "type": "object",
          "properties": {
            "UID": {
              "type": "string",
              "description": "Unique identifier for the task"
            },
            "DTSTART": {
              "type": "string",
              "description": "Start time of the task in UTC format"
            },
            "DTEND": {
              "type": "string",
              "description": "End time of the task in UTC format"
            },
            "DUE": {
              "type": "string",
              "description": "Due time of the task in UTC format"
            },
            "PERCENT": {
              "type": "string",
              "description": "Percent complete of the task"
            },
            "PRIORITY": {
              "type": "string",
              "description": "Priority of the task"
            },
            "Status": {
              "type": "string",
              "description": "Status of the task"
            },
            "SUMMARY": {
              "type": "string",
              "description": "A brief description or summary of the task"
            },
            "DESCRIPTION": {
              "type": "string",
              "description": "A more detailed description of the task"
            },
            "LOCATION": {
              "type": "string",
              "description": "The location of the task"
            },
            "RRULE": {
              "type": "object",
              "description": "The recurrence rule for the task",
              "properties": {
                "FREQ": {
                  "type": "string",
                  "enum": [
                    "DAILY",
                    "WEEKLY",
                    "MONTHLY",
                    "YEARLY"
                  ],
                  "description": "The frequency of the task"
                },
                "INTERVAL": {
                  "type": "integer",
                  "description": "The interval between tasks"
                },
                "COUNT": {
                  "type": "integer",
                  "description": "The number of times the task will occur"
                },
                "UNTIL": {
                  "type": "string",
                  "description": "The date on which the task will stop recurring"
                },
                "BYDAY": {
                  "type": "string",
                  "description": "The day(s) of the week on which the task will occur"
                },
                "BYMONTHDAY": {
                  "type": "integer",
                  "description": "The day of the month on which the task will occur"
                },
                "BYMONTH": {
                  "type": "integer",
                  "description": "The month in which the task will occur"
                }
              }
            },
            "CATEGORIES": {
              "type": "string",
              "description": "The categories of the task. Comma separated list."
            },
            "CALENDAR": {
              "type": "string",
              "enum": [
                "personal",
                "school",
                "work",
                "time blocks"
              ],
              "description": "The calendar to which the task belongs."
            }
          },
          "required": [
            "UID",
            "DTSTART",
            "SUMMARY",
            "CATEGORIES",
            "CALENDAR"
          ]
        }
      },
      "required": [
        "action",
        "task"
      ]
    }
  }
}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        print(tool_calls)
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "manage_caldav_task": schedule_task,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                summary=function_args.get("SUMMARY"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
print(run_conversation())
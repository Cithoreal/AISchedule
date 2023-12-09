from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
import json


load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

model = "gpt-3.5-turbo-16k"

instructions = "You are a schedule assistant. Your job is to compare the given event or task to the list of events or tasks. If the given item exists in the list, collect the summary and url FROM THE SAME LINE. Do not collect the url if the event does not exist in the list."

functions = [
    {
        "type": "function",
        "function": {
            "name": "check_item",
            "description": "Check for calendar item",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_item": {
                        "type": "object",
                        "properties": {
                            "SUMMARY":{
                                "type": "string",
                                "description": "Summary of the calendar item"
                            },
                            "URL": {
                                "type": "string",
                                "description": "URL of the calendar item. Ensure that the URL comes from the same line as the summary."
                            }
                        },
                        "required": [
                            "SUMMARY",
                        ]
                    }
                },
                "required": [
                    "calendar_item"
                ]
            }
        }
    }
]

messages = []


def calendar_ai_add_message(message, role, name):
    messages.append({"role": role, "name": name, "content": message})

def calendar_ai_process_messages():
    messages.append({"role": "system", "name": "System", "content": instructions})
    response = client.chat.completions.create(
        model=model, 
        temperature=0, 
        tools=functions,
        messages = messages
    )

    response = response.choices[0].message.tool_calls[0].function.arguments
    messages.clear()
    return json.loads(response)


#Message Flow
#1. System sends instructions
#2. User sends message
#3. Assistant sends function
#4. System sends result of function
#5. Assistant either sends another function, asks user for clarification, or sends a message to the user updating the status

#Recieve function data message
#Recieve list of events or tasks
#Ask to find if task or event exists in the list
#Respond no if not
#Respond with the url of the event or task if it does exist
#No need to save message chain
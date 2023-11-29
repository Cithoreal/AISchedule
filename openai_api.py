from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
import json


load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

model = "gpt-3.5-turbo-1106"

instructions="You are a schedule assistant. Your job is to help the user add events and tasks to their calendar. \
    You should help them maintain a healthy time balance. \n \
    There are three calendars to work with: Personal, School, and Projects. \n \
    Additionally there is a Time Blocks calendar that defines when different categories of events and tasks should be planned in the day.\n \
    The current date and time is " + datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " \n \
    Prefer the day of the week name over the date when referring to near dates. \n \
    Don't make up information, use only the information provided by the user."
    
messages = []   
messages.append({"role": "system", "name": "System", "content": instructions})


def send_message(message, role, name):
    messages.append({"role": role, "name" : name, "content":message})
    response = client.chat.completions.create(
        model=model, 
        temperature=0, 
        tools=functions, 
        messages = messages
    )

    response = response.choices[0].message

    messages.append(response)
    #print(messages)
    return response



def load_functions():
    #Load functions from the functions folder "openai_functions"
    #loop through all .json files in the folder and load them into a list
    functions = []
    for filename in os.listdir('openai_functions'):
        if filename.endswith(".json"):
            #open the file and add the contents to the list
            with open('openai_functions/' + filename) as f:
                functions.append(json.load(f))
    return functions



functions = load_functions()

'''message = input("Enter a message: ")

while message != "exit":
    assistant_message = send_message(message)
    if(assistant_message.choices[0].message.tool_calls != None):
        print(assistant_message.choices[0].message.tool_calls)
        assistant_message = assistant_message.choices[0].message.tool_calls[0].function.arguments
        messages.append({"role": "assistant", "content": assistant_message})
       # assistant_message = system_message("There is a conflict at that time.")
       # assistant_message = assistant_message.choices[0].message.content
        print(assistant_message)
    elif (assistant_message.choices[0].message.content != None):
        assistant_message = assistant_message.choices[0].message.content
        print(assistant_message)
        messages.append({"role": "assistant", "content": assistant_message})


    message = input()'''


#Message Flow
#1. System sends instructions
#2. User sends message
#3. Assistant sends function
#4. System sends result of function
#5. Assistant either sends another function, asks user for clarification, or sends a message to the user updating the status
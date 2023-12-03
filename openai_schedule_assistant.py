from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
thread = client.beta.threads.create()

def start_run():
  run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
    instructions="You are a schedule assistant. Your job is to help the user add events and tasks to their calendar. \
    You should help them maintain a healthy time balance. \n \
    There are three calendars to work with: Personal, School, and Projects. \n \
    Additionally there is a Time Blocks calendar that defines when different categories of events and tasks should be planned in the day.\n \
    The current date and time is " + datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " \n \
    Prefer the day of the week name over the date when referring to near dates. \n \
    Don't make up information, use only the information provided by the user.",
  ) #Rather than explicitly telling the calendars here or in the function jsons, the program should grab a list of the calendars 
  return run

def assistant_send_message(message, role="user"):
  client.beta.threads.messages.create(
      thread_id=thread.id,
      role=role,
      content=message,
  )

def get_run_status(run):
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )
  return run.status

async def retrieve_run(run):
  while run.status != 'requires_action' and run.status != 'completed':
    run = client.beta.threads.runs.retrieve(
      thread_id=thread.id,
      run_id=run.id
    )
  return run

def retrieve_message():
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  return(messages.data[0].content[0].text.value)


def complete_tool_run(run):
  #tool_call_id=run.required_action.submit_tool_outputs.tool_calls[0]
  if (run.status == "requires_action"):
    run = client.beta.threads.runs.submit_tool_outputs(
      thread_id=thread.id,
      run_id=run.id,
      tool_outputs=[
        {
          "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
          "output": run.required_action.submit_tool_outputs.tool_calls[0].function.arguments
        }
      ]
    )

  while run.status != 'completed':
    run = client.beta.threads.runs.retrieve(
      thread_id=thread.id,
      run_id=run.id
    )
    if run.status == 'requires_action':
      return run

  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  return(run)

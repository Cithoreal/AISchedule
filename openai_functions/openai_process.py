from datetime import datetime, timedelta
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
    instructions="You are a schedule assistant. Your job is to help the user add events and tasks to their calendar. You should help them maintain a healthy time balance. The current date and time is " + datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
  )
  return run

def send_message(message):
  client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
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

def process_caldav(user_request):

  message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=user_request,
  )

  run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
    instructions="The current date and time is " + datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
  )

  while run.status != 'requires_action':
    run = client.beta.threads.runs.retrieve(
      thread_id=thread.id,
      run_id=run.id
    )
    if run.status == 'completed':
      print("Run moved to completed, something went wrong.")
      break
 

  #print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
  return run


def process_message(run):
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
  return(messages.data[0].content[0].text.value)

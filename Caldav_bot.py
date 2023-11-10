import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I have Sociology homework due on the 18th of November."
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id='asst_JtqkI7InsyKuXYo95gH9tCjI',
)
#print(run)
while run.status != 'requires_action':
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )
print(run.required_action)


#print(run.messages[0].content)
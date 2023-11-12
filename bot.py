import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import bot
import discord
from discord.ext import commands
from caldav_connection import cal_create_event, cal_list_events
from openai import OpenAI

from openai_process import process_request



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot with a command prefix

bot = commands.Bot(command_prefix='!',intents=discord.Intents.default())
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    activity = discord.Game(name="Scheduling your events | !help")
    await bot.change_presence(status=discord.Status.idle, activity=activity)

@bot.event
async def on_message(message):
    # If the bot is mentioned, respond with a helpful message
    if bot.user.mentioned_in(message):
        help_message = "Hi there! I can help you schedule your events. Try using the `!schedule` command!"
        await message.channel.send(help_message)
    
    # This line is important, it ensures that other commands can be processed
    await bot.process_commands(message)

# Example usage in the schedule command
@bot.command(name='schedule', help='Schedules a new event. Usage: !schedule [event details]')
async def schedule(ctx, *, event_details: str):
   
    message = process_request(event_details)
    await bot.process_commands(message)


@bot.command(name='list', help='Lists scheduled events.')
async def list_events(ctx):
    try:
        # Get the current time and the end time for the event listing
        now = datetime.now()
        end_time = now + timedelta(days=7)  # List events for the next 7 days

        # Call the list_events function from the CalDav interaction code
        events = cal_list_events(now, end_time)

        # Format the list of events for Discord
        if events:
            response_message = "Here are your upcoming events:\n"
            for event in events:
                response_message += f"**{event['summary']}**: {event['start'].strftime('%Y-%m-%d %H:%M')} - {event['end'].strftime('%Y-%m-%d %H:%M')}\n"
        else:
            response_message = "You have no upcoming events."

        # Send the list of events to the user
        await ctx.send(response_message)

    except Exception as e:
        # Handle any errors that occur during event listing
        error_message = f"An error occurred while retrieving your events: {str(e)}"
        await ctx.send(error_message)


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I didn't understand that command.")
    else:
        await ctx.send("An error occurred: {}".format(str(error)))

# Helper functions would go here

""" def extract_event_details(text):
    # Use the NLP model to extract named entities
    entities = nlp(text)

    # Initialize placeholders
    event_name = None
    event_date = None
    event_time = None

    # Example logic to extract entities for event details (this will likely need to be more robust in practice)
    for entity in entities:
        if entity['entity'] == 'B-TIME' or entity['entity'] == 'I-TIME':
            event_time = entity['word']
        elif entity['entity'] == 'B-DATE' or entity['entity'] == 'I-DATE':
            event_date = entity['word']
        # You can expand this to look for other entities, such as location or people

    # Process extracted entities to construct the event details
    # This may involve converting the date and time to a datetime object
    # You may also want to use additional parsing to get the event name

    return event_name, event_date, event_time """

# Initialize and run the bot
if __name__ == "__main__":
    bot.run(TOKEN)

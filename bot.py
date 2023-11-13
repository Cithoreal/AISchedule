import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import bot
import discord
from discord.ext import commands
from caldav_connection import cal_create_event, cal_list_events
from openai import OpenAI

from openai_process import process_caldav, process_message



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
    try:
        data = process_caldav(event_details)

        # Process the event details to extract the event name, date, and time
       # print(data.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
        schedule_event(data.required_action.submit_tool_outputs.tool_calls[0].function.arguments)

        message = process_message(data)


        await ctx.send(message)
    except Exception as e:
        # Handle any errors that occur during event listing
        error_message = f"An error occurred while scheduling your events: {str(e)}"
        await ctx.send(error_message)



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



def schedule_event(event_details):
    event_summary = None
    event_date_start = None
    event_date_end = None
    event_description = None
    event_location = None
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

    cal_create_event(event_summary, event_date_start, event_date_end, event_description, event_location)



# Initialize and run the bot
if __name__ == "__main__":
    bot.run(TOKEN)

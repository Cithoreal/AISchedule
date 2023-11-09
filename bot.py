import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import bot
import discord
from discord.ext import commands
from transformers import pipeline
from caldav_connection import cal_create_event, cal_list_events



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot with a command prefix

bot = commands.Bot(command_prefix='!',intents=discord.Intents.default())



# Load NLP model
#nlp = pipeline('fill-mask', model='bert-base-uncased')

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

# Command to schedule an event
@bot.command(name='schedule', help='Schedules a new event. Usage: !schedule [event details]')
async def schedule(ctx, *, event_details: str):
    try:
        # Use the NLP model to extract date, time, and event name from event_details
        # Here we'll just mock this up as static values for demonstration
        # In practice, you'd replace these with the parsed values from the NLP output
        event_name = "New Event"
        event_start = datetime(2023, 11, 10, 15, 0)
        event_end = datetime(2023, 11, 10, 16, 0)
        event_description = "This is a test event"

        # Convert to server's timezone if necessary
        # event_start = event_start.astimezone(pytz.timezone("Your/Timezone"))
        # event_end = event_end.astimezone(pytz.timezone("Your/Timezone"))

        # Call the create_event function from the CalDav interaction code
        cal_create_event(event_name, event_start, event_end, event_description)

        # Confirm event creation to the user
        confirmation_message = f"Your event '{event_name}' has been scheduled for {event_start.strftime('%Y-%m-%d %H:%M')}!"
        await ctx.send(confirmation_message)

    except Exception as e:
        # Handle any errors that occur during scheduling
        error_message = f"An error occurred while scheduling your event: {str(e)}"
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

# Helper functions would go here


# Initialize and run the bot
if __name__ == "__main__":
    bot.run(TOKEN)

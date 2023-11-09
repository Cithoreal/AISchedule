import os
from dotenv import load_dotenv
from datetime import datetime
import pytz  # for timezone conversion
import bot
import discord
from discord.ext import commands
from transformers import pipeline
import caldav
from caldav.elements import dav, cdav
from datetime import datetime, timedelta
from icalendar import Event as ICalendarEvent


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#bot = discord.Client()
# Create the bot with a command prefix


bot = commands.Bot(command_prefix='!',intents=discord.Intents.default())

# Load NLP model
nlp = pipeline('fill-mask', model='bert-base-uncased')

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    activity = discord.Game(name="Scheduling your events | !help")
    await bot.change_presence(status=bot.Status.idle, activity=activity)

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
        event_start = datetime(2023, 11, 8, 15, 0)
        event_end = datetime(2023, 11, 8, 16, 0)
        event_description = "This is a test event"

        # Convert to server's timezone if necessary
        # event_start = event_start.astimezone(pytz.timezone("Your/Timezone"))
        # event_end = event_end.astimezone(pytz.timezone("Your/Timezone"))

        # Call the create_event function from the CalDav interaction code
        create_event(event_name, event_start, event_end, event_description)

        # Confirm event creation to the user
        confirmation_message = f"Your event '{event_name}' has been scheduled for {event_start.strftime('%Y-%m-%d %H:%M')}!"
        await ctx.send(confirmation_message)

    except Exception as e:
        # Handle any errors that occur during scheduling
        error_message = f"An error occurred while scheduling your event: {str(e)}"
        await ctx.send(error_message)


# Command to list events
@bot.command(name='list', help='Lists scheduled events.')
async def list_events(ctx):
    # Fetch events from CalDav
    # Format events for Discord
    # Send the list of events to the user
    pass

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I didn't understand that command.")
    else:
        await ctx.send("An error occurred: {}".format(str(error)))

# Helper functions would go here


# Initialize the CalDav client
client = caldav.DAVClient(url=os.getenv('CALDAV_SERVER'), username=os.getenv('CALDAV_USER'), password=os.getenv('CALDAV_PASSWORD'))
principal = client.principal()

# Get the calendar you'll be working with
calendars = principal.calendars()
if calendars:
    # Assuming you want to work with the first calendar
    calendar = calendars[0]

# Function to create an event on the calendar
def create_event(summary, start_datetime, end_datetime, description=''):
    # Create the event
    event = ICalendarEvent()
    event.add('summary', summary)
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('dtstamp', datetime.utcnow())
    event.add('description', description)

    # Create a calendar event
    calendar_event = caldav.Event(client=calendar.client, data=event.to_ical(), parent=calendar)
    
    # Save the event to the calendar
    calendar_event.save()

# Function to list events on the calendar
def list_events(start_datetime, end_datetime):
    # Search for events within a time range
    results = calendar.date_search(start=start_datetime, end=end_datetime)

    # Process the results and return them
    events = []
    for event in results:
        ical_event = ICalendarEvent.from_ical(event.data)
        events.append({
            'summary': ical_event.get('summary'),
            'start': ical_event.get('dtstart').dt,
            'end': ical_event.get('dtend').dt,
            'description': ical_event.get('description')
        })
    return events

# Usage example:
# create_event('Meeting with Bob', datetime(2023, 11, 8, 15, 0), datetime(2023, 11, 8, 16, 0), 'Discuss project milestones.')
# events = list_events(datetime.now(), datetime.now() + timedelta(days=7))



# Initialize and run the bot
if __name__ == "__main__":
    bot.run(TOKEN)

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
#nlp = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english', tokenizer='dbmdz/bert-large-cased-finetuned-conll03-english')

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
    print("schedule dis")
    #try:
        # Extract event details from the input
        #event_name, event_date, event_time = extract_event_details(event_details)

        # TODO: Convert event_date and event_time to a datetime object
        # TODO: You'll likely need additional parsing logic to handle event_name extraction properly

        # After parsing the details, interact with CalDav to schedule the event
        # And check for any conflicts before finalizing the event

        # For now, let's just assume the parsing went well and confirm back to the user
        #confirmation_message = f"Your event '{event_name}' has been scheduled for {event_date} at {event_time}!"
        #print(confirmation_message)
        #await ctx.send(confirmation_message)

    #except Exception as e:
    #    # Handle any errors that occur during scheduling
    #    error_message = f"An error occurred while scheduling your event: {str(e)}"
    #    await ctx.send(error_message)


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

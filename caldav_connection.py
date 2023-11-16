import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz  # for timezone conversion
import caldav
from icalendar import Calendar, Event, Timezone, Todo, Journal


load_dotenv()

# Initialize the CalDav client
caldav_client = caldav.DAVClient(url=os.getenv('CALDAV_SERVER'), username=os.getenv('CALDAV_USER'), password=os.getenv('CALDAV_PASSWORD'))
principal = caldav_client.principal()

# Get the calendar you'll be working with
calendars = principal.calendars()

if calendars:
    # Assuming you want to work with the first calendar
    calendar = calendars[1]
    
# Function to create an event on the calendar
def cal_create_event(summary, start, end, description, location, category):
    # Create the event
    event = Event()
    timezone = Timezone()
    timezone.add('tzid', 'America/New_York')
    event.add_component(timezone)
    if summary is not None:
        event.add('summary', summary)
    if start is not None:
        event.add('dtstart', start)
    if end is not None:
        event.add('dtend', end)
    if description is not None:
        event.add('description', description)
    if location is not None:
        event.add('location', location)
    if category is not None:
        event.add('category', category)
    
     # Create the event on the CalDav server
    try:
        
        calendar.add_event(event.to_ical())
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


# Function to list events on the calendar
def cal_list_events(start_datetime, end_datetime):
    # Search for events within a time range
    results = calendar.date_search(start=start_datetime, end=end_datetime)
    # Process the results and return them
    events = []
    for event in results:

        ical_event = Calendar.from_ical(event.data)
        for component in ical_event.walk():
            if component.name == "VEVENT":
                events.append({
                    'summary': component.get('summary'),
                    'start': component.get('dtstart').dt,
                    'end': component.get('dtend').dt,
                    'time': component.get('dtstamp').dt,
                    'description': component.get('description')
                })
    return events

# Usage example:
# create_event('Meeting with Bob', datetime(2023, 11, 8, 15, 0), datetime(2023, 11, 8, 16, 0), 'Discuss project milestones.')
# events = list_events(datetime.now(), datetime.now() + timedelta(days=7))

# Function to create an event on the calendar
def cal_create_todo(summary, due, percent, priority, status, description, location, category):
    # Create the todo
    todo = Todo()
    timezone = Timezone()
    timezone.add('tzid', 'America/New_York')
    todo.add_component(timezone)
    if summary is not None:
        todo.add('summary', summary)
    if due is not None:
        todo.add('due', due)
    if percent is not None:
        todo.add('percent', percent)
    if priority is not None:
        todo.add('priority', priority)
    if status is not None:
        todo.add('status', status)
    if description is not None:
        todo.add('description', description)
    if location is not None:
        todo.add('location', location)
    if category is not None:
        todo.add('category', category)
    
     # Create the todo on the CalDav server
    try:
        calendar.add_todo(todo.to_ical())
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


#cal_create_todo("test",datetime(2023, 11, 15, 15, 0),"test","test",23,2,"NEEDS-ACTION")
#cal_create_event("test",datetime(2023, 11, 15, 15, 0),datetime(2023, 11, 15, 16, 0),"test","test","test")
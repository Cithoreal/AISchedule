import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz  # for timezone conversion
import caldav
from icalendar import Calendar, Event
from icalendar import Event as ICalendarEvent

load_dotenv()

# Initialize the CalDav client
caldav_client = caldav.DAVClient(url=os.getenv('CALDAV_SERVER'), username=os.getenv('CALDAV_USER'), password=os.getenv('CALDAV_PASSWORD'))
principal = caldav_client.principal()

# Get the calendar you'll be working with
calendars = principal.calendars()
if calendars:
    # Assuming you want to work with the first calendar
    calendar = calendars[0]

# Function to create an event on the calendar
def cal_create_event(summary, start_datetime, end_datetime, description=''):
    # Create the event
    event = Event()

    event.add('summary', summary)
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('dtstamp', datetime.utcnow())
    event.add('description', description)

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
                    'description': component.get('description')
                })
    return events

# Usage example:
# create_event('Meeting with Bob', datetime(2023, 11, 8, 15, 0), datetime(2023, 11, 8, 16, 0), 'Discuss project milestones.')
# events = list_events(datetime.now(), datetime.now() + timedelta(days=7))

print(cal_list_events)
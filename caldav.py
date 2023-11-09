import os
from dotenv import load_dotenv
import caldav
from caldav.elements import dav, cdav
from datetime import datetime, timedelta
from icalendar import Event as ICalendarEvent

load_dotenv()

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

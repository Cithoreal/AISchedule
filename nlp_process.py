from transformers import pipeline
from dateutil.parser import parse
import re

# Load the NLP model for entity recognition
#nlp = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english', tokenizer='dbmdz/bert-large-cased-finetuned-conll03-english')
#nlp = pipeline("token-classification", model="Jean-Baptiste/camembert-ner-with-dates")
nlp = pipeline("token-classification", model="satyaalmasian/temporal_tagger_DATEBERT_tokenclassifier")
def extract_event_details(text):
    # Use the NLP model to extract named entities
    entities = nlp(text)
    print(entities)
    # Initialize variables to hold the extracted details
    event_date = None
    event_time = None
    event_name_parts = []

    # Process entities and extract date, time, and potentially other details
    for entity in entities:
        print(entity)
        # Extract dates
        if entity['entity'] == 'I-DATE':
            event_date = entity['word'].replace("##", "")
        # Extract times
        elif entity['entity'] == 'I-TIME':
            event_time = entity['word'].replace("##", "")

    # Attempt to parse the date and time into datetime objects
    try:
        if event_date:
            event_date = parse(event_date)
        if event_time:
            # If there's a date and a time, combine them into a single datetime object
            if event_date:
                event_time = parse(event_time, default=event_date)
            else:
                event_time = parse(event_time)
    except ValueError as e:
        # Handle cases where the date or time couldn't be parsed
        print(f"Date/time parsing error: {e}")

    # Extract the event name by removing recognized date and time entities from the text
    # This is a rudimentary approach; a more sophisticated method might be necessary for complex sentences
    event_text = text
    for entity in entities:
        event_text = event_text.replace(entity['word'], '')

    # Clean up the event text to extract a clear event name
    # This regex is looking for one or more non-word characters (like spaces and punctuation) at the start or end of the string and replacing them with nothing
    event_name = re.sub(r"^\W+|\W+$", "", event_text)

    return event_name, event_date, event_time

# Example usage:
text = "I have a meeting with Bob next Tuesday at 3 PM"
event_name, event_date, event_time = extract_event_details(text)
print(f"Event: {event_name}, Date: {event_date}, Time: {event_time}")

from models import *
from context import AppContext
import datetime

def create_event_action(context: AppContext, event_model: EventCreateRequest):
    """
    This is the Protocol for creating an envent.#
    """
    print(f"Excecuting protocol_create_event for '{event_model.summary}'")

    if event_model.start.dateTime is None or event_model.end.dateTime is None:
        raise ValueError("Invalid event: Start and end times must not be None.")
    if event_model.end.dateTime <= event_model.start.dateTime:
        raise ValueError("Invalid event: End time must be after the start time.")

    if context.calendar_service is None:
        raise AttributeError("calendar_service is not initialized in AppContext.")

    # Pass the event_model as a dictionary instance, not its type
    created_event = context.calendar_service.insert_event(event_body=event_model.model_dump(by_alias=True, exclude_none=True))

    return created_event

def find_event_action(context: AppContext, time_min: datetime.datetime, time_max: datetime.datetime, find_model: FindEventRequest):
    """
    This function searches for events in the user's calendar based on the provided query.
    """
    if not context.calendar_service:
        raise Exception ("Calendar service not initialized.")
    
    found_events_raw = context.calendar_service.search_events(query=find_model.query)

    return [GoogleCalendarEvent(**event) for event in found_events_raw]

def delete_event_action(context: AppContext, delete_model: DeleteEventRequest):
    """
    This function deletes events in the user's calendar based on the provided event id.
    """
    if not context.calendar_service:
        raise Exception("Calendar service not initialized.")
    
    context.calendar_service.delete_event(event_id=delete_model.event_id)

    return {
        "status": "success", 
        "message": f"The event with ID '{delete_model.event_id}' was successfully deleted."
    }

def update_event_action(context: AppContext, update_model:EventUpdateRequest):
    """
    This function updates events in the user's calendar based on the provided data.
    """
    if not context.calendar_service:
        raise Exception("Calendar service is not initialized.")
    
    updated_event = context.calendar_service.update_event(event_id=update_model.event_id, updated_data=update_model.model_dump(by_alias=True, exclude_none=True))

    return updated_event
from .models import *
from .context import AppContext
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

    created_event = context.calendar_service.insert_event(
        summary=event_model.summary,
        description=event_model.description,
        start_time=event_model.start.dateTime,
        end_time=event_model.end.dateTime,
        timezone=event_model.start.timeZone
    )

    return created_event
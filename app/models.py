import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

# Based on Google Calendar API v3 Event resource documentation:
# https://developers.google.com/calendar/api/v3/reference/events#resource

class EventDateTime(BaseModel):
    """Represents the start or end time of an event."""
    date: Optional[datetime.date] = None
    dateTime: Optional[datetime.datetime] = None
    timeZone: Optional[str] = None

class EventReminderOverride(BaseModel):
    method: Optional[str] = None
    minutes: Optional[int] = None

class EventReminders(BaseModel):
    useDefault: bool = Field(..., alias="useDefault")
    overrides: Optional[List[EventReminderOverride]] = None

# --- Main Event Model --- 

class GoogleCalendarEvent(BaseModel):
    """Pydantic model representing a Google Calendar event resource."""
    kind: str = "calendar#event"
    id: Optional[str] = Field(None, description="Opaque identifier of the event.")
    status: Optional[str] = Field(None, description="Status of the event ('confirmed', 'tentative', 'cancelled').")
    html_link: Optional[str] = Field(None, alias='htmlLink', description="URL for the event in the Google Calendar UI.")
    created: Optional[datetime.datetime] = Field(None, description="Creation time of the event (RFC3339 format).")
    updated: Optional[datetime.datetime] = Field(None, description="Last modification time of the event (RFC3339 format).")
    summary: Optional[str] = Field(None, description="Title of the event.")
    description: Optional[str] = Field(None, description="Description of the event. Optional.")
    location: Optional[str] = Field(None, description="Geographic location of the event. Optional.")
    color_id: Optional[str] = Field(None, alias='colorId', description="Color of the event. Optional.")
    start: Optional[EventDateTime] = Field(None, description="The start time of the event.")
    end: Optional[EventDateTime] = Field(None, description="The end time of the event.")
    end_time_unspecified: Optional[bool] = Field(None, alias='endTimeUnspecified', description="Whether the end time is actually unspecified.")
    recurrence: Optional[List[str]] = Field(None, description="List of RRULE, EXRULE, RDATE or EXDATE properties for recurring events.")
    recurring_event_id: Optional[str] = Field(None, alias='recurringEventId', description="For an instance of a recurring event, this is the id of the recurring event itself.")
    original_start_time: Optional[EventDateTime] = Field(None, alias='originalStartTime', description="For an instance of a recurring event, this is the original start time of the instance before modification.")
    calendar_id: str = 'primary'
   
    reminders: Optional[EventReminders] = Field(None, description="Information about the event's reminders.")
    # Add other fields as needed (e.g., attachments, conferenceData, gadget, source, etc.)

# --- Models for API Requests/Responses --- 

class EventCreateRequest(BaseModel):
    """Model for the request body when creating a detailed event."""
    summary: str
    start: EventDateTime
    end: EventDateTime
    description: Optional[str] = None
    location: Optional[str] = None
    recurrence: Optional[List[str]] = Field(None, description="List of RRULEs, EXRULEs, RDATEs or EXDATEs for recurring events.")
    reminders: Optional[EventReminders] = Field(None, description="Notification settings for the event.")
    # Visual theme/color support
    colorId: Optional[str] = Field(None, alias='colorId', description="Google Calendar color ID (1-11).")
    theme: Optional[str] = Field(None, exclude=True, description="High-level theme (e.g., 'Work', 'Study', 'Exercise') used to infer color.")
    # Add other creatable fields as needed

class QuickAddEventRequest(BaseModel):
    """Model for the request body when using the quickAdd endpoint."""
    text: str = Field(..., description="The text describing the event to be parsed by Google Calendar.")

class EventUpdateRequest(BaseModel):
    """Model for the request body when updating an event.
       Contains only the fields that can be updated.
    """
    event_id: str
    summary: Optional[str] = None
    start: Optional[EventDateTime] = None
    end: Optional[EventDateTime] = None
    description: Optional[str] = None
    location: Optional[str] = None
    colorId: Optional[str] = Field(None, alias='colorId', description="Google Calendar color ID (1-11).")
    theme: Optional[str] = Field(None, exclude=True, description="High-level theme to infer color.")
    # Add other updatable fields

# Define NotificationSettings first as it's used in CalendarListEntry
class NotificationSettings(BaseModel):
    """Represents notification settings for a calendar."""
    notifications: Optional[List[Dict[str, str]]] = None # List of {'type': 'eventCreation', 'method': 'email'} etc.

    class Config:
        populate_by_name = True # Changed from allow_population_by_field_name

class CalendarListEntry(BaseModel):
    """Represents an entry in the user's calendar list."""
    kind: str = "calendar#calendarListEntry"
    etag: str
    id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    timeZone: Optional[str] = None # Renamed from 'time_zone'
    summaryOverride: Optional[str] = None # Renamed from 'summary_override'
    colorId: Optional[str] = None # Renamed from 'color_id'
    backgroundColor: Optional[str] = None # Renamed from 'background_color'
    foregroundColor: Optional[str] = None # Renamed from 'foreground_color'
    hidden: Optional[bool] = None
    selected: Optional[bool] = None
    accessRole: Optional[str] = None # Renamed from 'access_role'
    defaultReminders: Optional[List[EventReminderOverride]] = None # Renamed from 'default_reminders'
    notificationSettings: Optional[NotificationSettings] = None # Renamed from 'notification_settings'
    primary: Optional[bool] = None
    deleted: Optional[bool] = None

class CalendarListResponse(BaseModel):
    """Response containing a list of calendars."""
    kind: str = "calendar#calendarList"
    items: List[CalendarListEntry] = []
    nextPageToken: Optional[str] = None
    nextSyncToken: Optional[str] = None

# Re-inserting EventsResponse definition
class EventsResponse(BaseModel):
    """Response containing a list of events."""
    kind: str = "calendar#events"
    summary: Optional[str] = None
    description: Optional[str] = None
    updated: Optional[datetime.datetime] = None
    timeZone: Optional[str] = None
    accessRole: Optional[str] = None
    defaultReminders: Optional[List[EventReminderOverride]] = []
    items: List[GoogleCalendarEvent] = []
    nextPageToken: Optional[str] = None
    nextSyncToken: Optional[str] = None

class CalendarList(BaseModel):
    """Represents the user's list of calendars."""
    kind: str = "calendar#calendarList"
    etag: str
    nextPageToken: Optional[str] = None
    nextSyncToken: Optional[str] = None
    items: List[CalendarListEntry]

    class Config:
        populate_by_name = True

# --- Find Availability (Free/Busy) ---
class FreeBusyRequestItem(BaseModel):
    id: str # Calendar ID

class FreeBusyRequest(BaseModel):
    time_min: datetime.datetime = Field(..., alias='timeMin')
    time_max: datetime.datetime = Field(..., alias='timeMax')
    items: List[FreeBusyRequestItem]
    # Optional: timeZone, groupExpansionMax, calendarExpansionMax
    time_zone: Optional[str] = Field(None, alias='timeZone')

class TimePeriod(BaseModel):
    start: datetime.datetime
    end: datetime.datetime

class FreeBusyError(BaseModel):
    domain: str
    reason: str

class CalendarBusyInfo(BaseModel):
    errors: Optional[List[FreeBusyError]] = None
    busy: List[TimePeriod] = []

class FreeBusyResponse(BaseModel):
    kind: str = "calendar#freeBusy"
    time_min: datetime.datetime = Field(..., alias='timeMin')
    time_max: datetime.datetime = Field(..., alias='timeMax')
    calendars: Dict[str, CalendarBusyInfo] = {}

# --- Project Recurring Events ---
class ProjectRecurringRequest(BaseModel):
    time_min: datetime.datetime
    time_max: datetime.datetime
    calendar_id: str = 'primary'
    event_query: Optional[str] = None

# Define ProjectedEventOccurrence within models.py for consistency
class ProjectedEventOccurrenceModel(BaseModel):
    original_event_id: str
    original_summary: str
    occurrence_start: datetime.datetime
    occurrence_end: datetime.datetime

class ProjectRecurringResponse(BaseModel):
    projected_occurrences: List[ProjectedEventOccurrenceModel]

# --- Analyze Busyness ---
class AnalyzeBusynessRequest(BaseModel):
    time_min: datetime.datetime
    time_max: datetime.datetime
    calendar_id: str = 'primary'

class DailyBusynessStats(BaseModel):
    event_count: int
    total_duration_minutes: float

class AnalyzeBusynessResponse(BaseModel):
    # Use string representation for date keys in JSON
    busyness_by_date: Dict[str, DailyBusynessStats] = Field(..., description="Mapping of date string (YYYY-MM-DD) to busyness stats")

# --- Tool Calling Model ---
class AIToolCall(BaseModel):
    """Represents the tool the AI has decided to use and its parameters."""
    tool_name: str = Field(..., description="The name of the tool to be called (e.g., 'create_event', 'reply_text').")
    parameters: dict[str, Any] = Field(default_factory=dict, description="The arguments for the tool, as a dictionary.")

class FindEventRequest(BaseModel):
    """Represents a request to find an event."""
    query: str
    time_min: datetime.datetime = Field(..., alias='timeMin')
    time_max: datetime.datetime = Field(..., alias='timeMax')

class DeleteEventRequest(BaseModel):
    """Represents a request to delete an event."""
    event_id: str


from dataclasses import dataclass
from app.backend.log.models.enum_types import EventType


@dataclass
class EventModel:
    name: str
    event_type: EventType
    incoming_ids: [str]
    outgoing_ids: [str]
    all_reachable_events: [str]  # The name of all the events that *could* happen after this event
    parallel_or_xor_id: int

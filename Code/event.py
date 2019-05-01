from enum import Enum
import util


class EventType(Enum):
    create_request = 1  # Attributes : id, timeout, service_time
    end_quantum = 2     # Attributes : core_id
    switch_context = 3  # Attributes : core_id
    departure = 4       # Attributes :
    timeout = 5
    drop_request = 6


class Event:
    def __init__(self, id, event_type, start_time, attr):
        self.event_id = id              # Event ID
        # type of the event (1..6) using eventType class
        self.event_type = event_type
        self.start_time = start_time    # time at which to start the event
        # attributes of the event (can be different for each type of event)
        self.attr = attr


class EventList:
    """
    A specialized priority queue for handling events
    """

    def __init__(self):
        self.queue = util.PriorityQueue()
        self.counter = 0

    def getNextEvent(self):
        """
        Returns the most imminent event from the list
        """
        return self.queue.pop()

    def addEvent(self, event_type, start_time, event_attr):
        """
        Add an event to event list (which is a priority queue)
        """
        event = Event(self.counter, event_type, start_time, event_attr)
        self.queue.push(event)
        self.counter += 1

    def isEmpty(self):
        """
        Returns whether event list is empty
        """
        return len(self.queue) == 0

    def __repr__(self):
        return str(self.counter) + str(self.queue)

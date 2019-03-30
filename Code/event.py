from enum import Enum
import util


class EventType(Enum):
    create_request = 1
    end_quantum = 2
    switch_context = 3
    departure = 4
    timeout = 5
    drop_request = 6


class Event:
    def __init__(self, id, event_type, start_time, attr):
        self.event_id = id
        self.event_type = event_type
        self.start_time = start_time
        self.attr = attr

class EventList:
    def __init__(self):
        self.queue = util.PriorityQueue()
        self.counter = 0

    def getNextEvent(self):
        return self.queue.pop()

    def addEvent(self, event_type, start_time, event_attr):
        event = Event(self.counter, event_type, start_time, event_attr)
        self.queue.push(event)
        self.counter += 1

    def __str__(self):
        return str(self.counter) + str(self.queue)

EVENT_LIST = EventList()
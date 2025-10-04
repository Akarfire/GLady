
from Event import Event

# This class is meant to map received events to functions in a plugin
class EventMapper:

    def __init__(self):

        # Event to function map < Event Name -> Processor function >
        # Processor function must receive
        event_map = {}

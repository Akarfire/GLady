from Plugin import Plugin
from Core.Event import Event

from Core.EventProcessing import EventProcessing

# Submodule of GLady Core, responsible for enabling inter-plugin communication.
class CommunicationBus:

    def __init__(self, core):
        self.core = core

        self.core.logger.log("Communication Bus initialized")


    # INTERNAL

    def __broadcast_event(self, event : Event):
        
        event_processing : EventProcessing = self.core.eventProcessing

        try:
            event_processing.process_event(event)

        except Exception as e:
            self.core.logger.log(f"Failed to process event {event.eventName} : \n{str(e)}\nEvent Details:\n{event.get_details_string()}", message_type=1)


    # INTERFACE
        
    # Initializing (Calling, Triggering, Firing) an event
    def init_event(self, event : Event):

        if not "Local" in event.tags:
            # Routing event to network
            self.core.networkManager.route_event_to_network(event)

        self.__broadcast_event(event)
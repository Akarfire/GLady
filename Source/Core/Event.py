# Inter-plugin communication is executed through Events - special messages,
# travelling over the communication bus from their sender to any recipient,
# willing to hear them. Senders and Recipients are plugins.
class Event:

    def __init__(self, event_name = "defaultEvent", initiator = "NaN", tags = None, data = None):

        # Name/type of the event
        self.eventName : str = event_name

        # Name of the component/plugin that initiated the event
        self.initiator : str = initiator

        # List of event's tags
        self.tags : set = tags

        if self.tags is None:
            self.tags = set()

        # Data, contained in the event
        self.data : dict = data

        if self.data is None:
            self.data = dict()

    # Returns debug information about the event
    def get_details_string(self):
        return f"Name: {self.eventName};\nInitiator: {self.initiator};\nTags: {str(self.tags)};\nData: {str(self.data)}."
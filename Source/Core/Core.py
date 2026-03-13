import time

from Core.PluginManager import PluginManager
from Core.CommunicationBus import CommunicationBus
from Core.NetworkManager import NetworkManager
from Core.ControlServer import ControlServer
from Core.Logger import Logger
from Core.Configuration import ConfigurationParser
from Core.ResourceHttpServer import ResourceHttpServer
from Core.EventProcessing import EventProcessing

# Current GLady version (change for major updates)
version = "Early Access 1.0"

# GLady's core is the mandatory module, that cannot be disabled, it is responsible for:
#   - Loading plugins;
#   - Processing inter-plugin communications;
#   - Processing network communication with other instances of GLady core;
#   - Receiving and rerouting commands from control servers;
#   - Handling execution logs.

class GLadyCore:

    def __init__(self):

        # Path to core's config files
        self.coreConfigPath = "./Config"

        # Flag that marks a successful initialization
        self.canRun = True

        # Flag, marks whether the program is still running
        self.running = False

        # Time elapsed from the previous update
        self.deltaTime = 0.0

        # Default core's config options
        self.defaultOptions = {
            "UpdatePeriod": 0.2,
            "ResourceHttpServerAddress": "localhost",
            "ResourceHttpServerPort": 8000
        }

        try:
            self.logger = Logger(self)

            self.logger.log("GLady ver " + version + " now launching!")
            self.logger.log(" ")
            self.logger.log(" ")

            self.configurationParser = ConfigurationParser(self)        
            self.communicationBus = CommunicationBus(self)
            self.eventProcessing = EventProcessing(self)
            self.networkManager = NetworkManager(self)
            self.controlServer = ControlServer(self)
            self.resourceHttpServer = ResourceHttpServer(self)
            
            # Loading core configs
            self.options = self.defaultOptions
            self.reload_config()
            
            self.resourceHttpServer.start_server()
            
            # Plugin manager & Loading the plugins
            self.pluginManager = PluginManager(self)
            
            # Core control commands
            self.controlServer.register_control_command("Core_ReloadConfig", self.command_core_reload_config)
            self.controlServer.register_control_command("ReloadConfig", self.command_reload_config)

        except Exception as e:
            self.logger.log("CRITICAL   :   GLady initialization failed!\n" + str(e), message_type=1)
            self.canRun = False
        

    # Reads core's config files
    def reload_config(self):
        self.options = self.configurationParser.read_options_file(f"{self.coreConfigPath}/Config.txt",
                                                                  default_options=self.defaultOptions)
        self.resourceHttpServer.reload_config()
        self.eventProcessing.reload_config()
        
        
    # Access Core's options with default value support and proper error naming
    def get_option(self, option_name : str):
        
        if option_name in self.options:
            return self.options[option_name]
        
        elif option_name in self.defaultOptions:
            return self.defaultOptions[option_name]
        
        else:
            raise LookupError(f"Core has no option '{option_name}'")
        
    # Checks if the option is valid
    def is_option_valid(self, option_name : str) -> bool:
        return (option_name in self.options) or (option_name in self.defaultOptions)
        

    # Starts an instance of GLady core application
    def run(self):
        if self.canRun:

            self.running = True
            self.logger.log("GLady is up and running!\n\n")

            # Main program loop
            while self.running:

                try:
                    update_start_time = time.perf_counter()

                    # Update logic
                    #   {

                    self.controlServer.update(self.deltaTime)
                    self.pluginManager.update_plugins(self.deltaTime)

                    #   }

                    # Time calculations
                    update_time = time.perf_counter() - update_start_time
                    
                    wait_time = max(0.0, self.options.get("UpdatePeriod") - update_time)
                    time.sleep(wait_time)

                    self.deltaTime = update_time + wait_time

                except Exception as e:
                    self.logger.log("CRASH DETECTED   :   " + str(e), message_type=1)
                    self.running = False

            # Program exit
            self.controlServer.close_connection()
            self.pluginManager.unload_plugins()


    # Commands
    
    def command_core_reload_config(self, data):
        self.reload_config()
        
    def command_reload_config(self, data):
        self.reload_config()
        
        for plugin_name in self.pluginManager.pluginsTable:
            self.pluginManager.pluginsTable[plugin_name].reload_config()
        
    
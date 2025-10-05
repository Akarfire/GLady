import pathlib

from Core.Event import Event
from Core.PluginListeningData import PluginListeningData

# Base class for all GLady plugins
# A non-mandatory module, that is responsible for a specific GLady function.
class Plugin:

    pluginList = []

    def __init__(self, core):

        # BASIC

        self.core = core

        # Dictionary of plugin's processor functions < Display function name -> Processor function >
        # Processor function must receive Event class as input
        self.eventProcessorFunctions : dict = dict()

        self.pluginName : str = "plugin"
        self.directory : str = ""

        self.listeningConfiguration : PluginListeningData = PluginListeningData()

        # CONFIGURABLE

        # Event to function map < Event Name -> list [Processor function display name] >
        self.eventMap : dict[str, list[str]] = dict()


    # Adding plugin to the global plugin list
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.pluginList.append(cls)

    # Plugin listening configuration

    # The plugin will START listening for the specified event
    # Only works if white or black list is enabled
    def __listen_to(self, event_name):
        self.listeningConfiguration.whiteList.add(event_name)
        self.listeningConfiguration.blackList.remove(event_name)

    # The plugin will STOP listening for the specified event
    # Only works if white or black list is enabled
    def __stop_listening_to(self, event_name):
        self.listeningConfiguration.whiteList.remove(event_name)
        self.listeningConfiguration.blackList.add(event_name)


    # Called when the plugin is loaded by the Plugin Manager
    def load(self):

        # Loading configuration
        # Event mappings
        self.eventMap = self.core.configurationParser.read_event_mapping_file(f"{self.directory}/Config/EventMapping.txt")


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        None

    # Called when the plugin has received an event from the communication bus
    def received_event(self, event : Event):

        # Determine event mapping name (if eventName is mapped, then use that mapping, otherwise try using default mapping)
        event_mapping_name = event.eventName

        if not event_mapping_name in self.eventMap:

            # If no possible mapping exist (including default one), then exit the function
            if not "*" in self.eventMap: return
            event_mapping_name = "*"

        # Running processor functions
        processor_function_names = self.eventMap[event_mapping_name]
        for function_name in processor_function_names:
            if function_name in self.eventProcessorFunctions:
                self.eventProcessorFunctions[function_name](event)
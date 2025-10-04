from Source.Core.Core import GLadyCore
from Source.Plugin import Plugin


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

        # Data, contained in the event
        self.data : dict = data


# Contains per-plugin configurable event listening settings
class PluginListeningData:

    def __init__(self):
        self.useWhiteList : bool = False
        self.whiteList : set = set()

        self.useBlackList : bool = False
        self.blackList : set = set()

        self.blockListening : bool = False



# Submodule of GLady Core, responsible for enabling inter-plugin communication.
class CommunicationBus:

    def __init__(self, core):
        self.core : GLadyCore = core
        self.pluginListeningConfiguration : dict = dict()


    # INTERNAL

    def __broadcast_event(self, event : Event):

        plugins = self.core.pluginManager.pluginsTable()
        for plugin_name in plugins:
            plugin : Plugin = plugins[plugin_name]

            # Checking plugin listening configuration, if the plugin should NOT receive this event, go to the next iteration
            if plugin_name in self.pluginListeningConfiguration:

                if self.pluginListeningConfiguration[plugin_name].useWhiteList:
                    if not event.eventName in self.pluginListeningConfiguration[plugin_name].whiteList: continue

                if self.pluginListeningConfiguration[plugin_name].useBlackList:
                    if event.eventName in self.pluginListeningConfiguration[plugin_name].blackList: continue

            # "SpecificReceiver" tag implementation
            if "SpecificReceiver" in event.tags:
                if not plugin.pluginName in event.data.get("SpecificReceiver_Names"): continue

            # If none of the above conditions were met, then the plugin is listening to this event
            plugin.received_event(event)


    # INTERFACE

    # Initializing (Calling, Triggering, Firing) an event
    def init_event(self, event : Event):

        if not "Local" in event.tags:
            # Routing event to network
            # PLACEHOLDER {
            print("Routing to network")
            # }

        self.__broadcast_event(event)


    # Plugin listening configuration

    # Enables the use of event white list for the plugin
    def use_listening_white_list(self, plugin_name, should_use_white_list):
        self.pluginListeningConfiguration.get(plugin_name).useWhiteList = should_use_white_list


    # Enables the use of event black list for the plugin
    def use_listening_black_list(self, plugin_name, should_use_black_list):
        self.pluginListeningConfiguration.get(plugin_name).useBlackList = should_use_black_list


    # The plugin will START listening for the specified event
    # Only works if white or black list is enabled
    def listen_to(self, plugin_name, event_name):
        self.pluginListeningConfiguration.get(plugin_name).whiteList.add(event_name)
        self.pluginListeningConfiguration.get(plugin_name).blackList.remove(event_name)


    # The plugin will STOP listening for the specified event
    # Only works if white or black list is enabled
    def stop_listening_to(self, plugin_name, event_name):
        self.pluginListeningConfiguration.get(plugin_name).whiteList.remove(event_name)
        self.pluginListeningConfiguration.get(plugin_name).blackList.add(event_name)


    # The plugin will no longer be listening to any events
    def block_events(self, plugin_name):
        self.pluginListeningConfiguration.get(plugin_name).blockListening = True


    # Reverts "block_events" flag
    def unblock_events(self, plugin_name):
        self.pluginListeningConfiguration.get(plugin_name).blockListening = False




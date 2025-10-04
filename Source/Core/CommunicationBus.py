#from Source.Core.Core import GLadyCore
from Source.Plugin import Plugin
from Source.Core.Event import Event
#from Source.Core.PluginListeningData import PluginListeningData

# Submodule of GLady Core, responsible for enabling inter-plugin communication.
class CommunicationBus:

    def __init__(self, core):
        self.core = core

        self.core.logger.log("Communication Bus initialized")


    # INTERNAL

    def __broadcast_event(self, event : Event):

        plugins = self.core.pluginManager.pluginsTable
        for plugin_name in plugins:
            plugin : Plugin = plugins[plugin_name]

            # Checking plugin listening configuration, if the plugin should NOT receive this event, go to the next iteration
            if plugin.listeningConfiguration.useWhiteList:
                if not event.eventName in plugin.listeningConfiguration.whiteList: continue

            if plugin.listeningConfiguration.useBlackList:
                if event.eventName in plugin.listeningConfiguration.blackList: continue

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
            None
            # }

        self.__broadcast_event(event)







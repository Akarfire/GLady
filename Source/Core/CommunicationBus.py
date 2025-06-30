
# Inter-plugin communication is executed through Events - special messages,
# travelling over the communication bus from their sender to any recipient,
# willing to hear them. Senders and Recipients are plugins.
class Event:

    def __init__(self, event_name = "defaultEvent", initiator = "NaN", tags = None, data = None):
        self.eventName = event_name
        self.initiator = initiator
        self.tags = tags
        self.data = data


# Contains per-plugin configurable event listening settings
class PluginListeningData:

    def __init__(self):
        self.useWhiteList = False
        self.whiteList = set()

        self.useBlackList = False
        self.blackList = set()

        self.blockListening = False



# Submodule of GLady Core, responsible for enabling inter-plugin communication.
class CommunicationBus:

    def __init__(self, core):
        self.core = core
        self.pluginListeningConfiguration = dict()


    # Initializing (Calling, Triggering, Firing) an event
    def init_event(self, event):
        None


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




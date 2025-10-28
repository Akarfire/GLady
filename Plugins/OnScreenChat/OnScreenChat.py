import Plugin as PluginAPI

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["OnChatMessageReceived"] = self.on_chat_message_received
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()


    # Example event processor function
    def on_chat_message_received(self, event : PluginAPI.Event):

        # TO DO : Sending chat message to the UI clients

        return;


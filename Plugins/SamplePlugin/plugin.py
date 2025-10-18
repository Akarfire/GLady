import Plugin as PluginAPI

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["SampleEventProcessorFunction"] = self.sample_event_processor_function
        self.eventProcessorFunctions["TestEventProcessorFunction"] = self.test_event_processor_function
        #...

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

        # # TEST MAPPING
        # self.eventMap["TestEvent"] = ["Sample Event Processor Function"]
        # # ^^^ REMOVE THIS ^^^


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()


    # Example event processor function
    def sample_event_processor_function(self, event : PluginAPI.Event):

        self.core.logger.log(f"Plugin {self.pluginName} received event {event.eventName}")


    def test_event_processor_function(self, event : PluginAPI.Event):

        self.core.logger.log(f"Test Plugin {self.pluginName} received event {event.eventName}")

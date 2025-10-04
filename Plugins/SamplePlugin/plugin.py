import Source.Plugin as PluginAPI

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        self.pluginName = "Sample Plugin Gen 2.0"
        #...

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):

        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["Sample Event Processor Function"] = self.sample_event_processor_function

        # TEST MAPPING
        self.eventMap["TestEvent"] = "Sample Event Processor Function"
        # ^^^ REMOVE THIS ^^^


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        None


    # Example event processor function
    def sample_event_processor_function(self, event : PluginAPI.Event):

        self.core.logger.log(f"Plugin {self.pluginName} received event {event.eventName}")

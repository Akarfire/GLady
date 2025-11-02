import Plugin as PluginAPI

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["SampleEventProcessorFunction"] = self.sample_event_processor_function
        #...

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        None


    # Example event processor function
    def sample_event_processor_function(self, event : PluginAPI.Event):

        self.core.logger.log(f"Plugin {self.pluginName} received event {event.eventName}")


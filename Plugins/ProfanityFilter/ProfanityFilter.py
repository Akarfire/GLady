import Plugin as PluginAPI

from profanity_check import predict_prob

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        
        self.defaultOptions : dict = {
            "SafetyThreshold": 0.97,
            "DataSelector": [],
            "FilteredMessageSubstitution": "FILTERED",
            "OutputEventName": "OnDataFiltered"
        }

        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["FilterData"] = self.filter_data
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
    def filter_data(self, event : PluginAPI.Event):
        
        filtered_event = PluginAPI.Event()
        filtered_event.eventName = event.eventName
        filtered_event.initiator = event.initiator
        filtered_event.tags = event.tags
        
        for elem in event.data:
            if elem in self.options["DataSelector"] and type(event.data[elem]) == str \
                and predict_prob([event.data[elem]])[0] > self.options["SafetyThreshold"]:
                    
                    filtered_event.data[elem] = self.options["FilteredMessageSubstitution"]
                    self.core.logger.log(f"PROFANITY FILTER : Filtered '{event.data[elem]}'")
                    
            else:
                filtered_event.data[elem] = event.data[elem]
                
        self.core.communicationBus.init_event(self.options["OutputEventName"], self.pluginName, filtered_event.tags, filtered_event.data)
                    


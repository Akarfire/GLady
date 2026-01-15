import Plugin as PluginAPI

from profanity_check import predict_prob

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        
        self.defaultOptions : dict = {
            "SafetyThreshold": 0.97,
            "DefaultDataSelector" : [],
            "FilteredMessageSubstitution": "FILTERED"
        }

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["FilterData"] = self.filter_data
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
    def filter_data(self, event : PluginAPI.Event, arguments : dict = {}):

        data_selector = self.get_option("DefaultDataSelector")
        safety_threshold = self.get_option("SafetyThreshold")
        
        if "DataSelector" in arguments:
            data_selector = arguments["DataSelector"]
            
        if "SafetyThreshold" in arguments:
            safety_threshold = arguments["SafetyThreshold"]

        for elem in event.data:
            if elem in data_selector and type(event.data[elem]) == str \
                and predict_prob([event.data[elem]])[0] > safety_threshold:
                    
                    self.core.logger.log(f"PROFANITY FILTER : Filtered '{event.data[elem]}'")                                 
                    event.data[elem] = self.get_option("FilteredMessageSubstitution")
                    


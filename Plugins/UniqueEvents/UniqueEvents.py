import Plugin as PluginAPI

class UniqueEvents(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["StartUniqueEvent"] = self.start_unique_event
        self.eventProcessingFunctions["StopUniqueEvent"] = self.stop_unique_event
        self.eventProcessingFunctions["StopAllUniqueEvents"] = self.stop_all_unique_events
        #...
        
        # Defining default options
        self.defaultOptions : dict = {
            "UniqueEvents" : {
                "ExampleUniqueEvent" : 
                {"StartEventCall" : "$UniqueEventName$_Start",
                 "StartEventCustomData" : dict(),
                 "EndEventCall" : "$UniqueEventName$_End",
                 "EndEventCustomData" : dict()
                },}
        }
        
        # Defining default event generation settings
        self.defaultGeneratedEventNames = {
            "TestEchoEvent" : ["EchoEvent_1", "EchoEvent_2"]
        }
        
        # Unique Events timers
        self.uniqueEvents : dict[str, float] = dict()
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)

        for event in self.uniqueEvents:
            if self.uniqueEvents[event] > 0.0:
                # Updating timer
                self.uniqueEvents[event] -= delta_time
                # Activity check
                if self.uniqueEvents[event] <= 0.0:
                    self.__end_event(event)


    # Loading (and Reloading) configuration files
    def reload_config(self):
        super().reload_config()
        
        for event in self.get_option("UniqueEvents"):
            if not event in self.uniqueEvents:
                self.uniqueEvents[event] = -1.0
            
        events_to_delete = []    
        for event in self.uniqueEvents:
            if not event in self.get_option("UniqueEvents"):
                events_to_delete.append(event)
                
        for event in events_to_delete:
            self.uniqueEvents.pop(event)
        
    
    def __start_event(self, event : str, duration : float):
        if not event in self.uniqueEvents:
            self.core.logger.log(f"UNIQUE EVENTS: Can't start unknown unique event '{event}'")
            return
        
        self.core.logger.log(f"UNIQUE EVENTS: Starting event `{event}`")
        
        self.uniqueEvents[event] = duration
        
        unique_event_data = self.get_option("UniqueEvents")[event]
        start_event_name = unique_event_data["StartEventCall"]
        start_event_name = start_event_name.replace("$UniqueEventName$", event)
        
        start_event_data = unique_event_data["StartEventCustomData"].copy()
        start_event_data["UniqueEvent"] = event
        
        start_event = PluginAPI.Event(start_event_name, self.pluginName, {}, start_event_data)
        self.generate_event(start_event)
        
    
    def __end_event(self, event : str):
        if not event in self.uniqueEvents:
            self.core.logger.log(f"UNIQUE EVENTS: Can't end unknown unique event '{event}'")
            return
        
        self.core.logger.log(f"UNIQUE EVENTS: Ending event `{event}`")
        
        unique_event_data = self.get_option("UniqueEvents")[event]
        end_event_name = unique_event_data["EndEventCall"]
        end_event_name = end_event_name.replace("$UniqueEventName$", event)
        
        end_event_data = unique_event_data["EndEventCustomData"].copy()
        end_event_data["UniqueEvent"] = event
        
        end_event = PluginAPI.Event(end_event_name, self.pluginName, {}, end_event_data)
        self.generate_event(end_event)
    

    # Example event processor function
    def start_unique_event(self, event : PluginAPI.Event, arguments : dict = {}):
        unique_event = ""
        if "UniqueEvent" in event.data:
            unique_event = event.data["UniqueEvent"]
            
        if "UniqueEvent" in arguments:
            unique_event = arguments["UniqueEvent"]
            
        duration = 0.0
        if "Duration" in event.data:
            duration = event.data["Duration"]
        
        if "Duration" in arguments:
            duration = arguments["Duration"]
            
        combine_duration = True
        if "CombineDuration" in event.data:
            combine_duration = event.data["CombineDuration"]
            
        if "CombineDuration" in arguments:
            combine_duration = arguments["CombineDuration"]
            
        if not unique_event in self.uniqueEvents:
            self.core.logger.log(f"UNIQUE EVENTS: Unknown unique event `{unique_event}`!")
            return
        
        if self.uniqueEvents[unique_event] > 0.0:
            if combine_duration:
                self.uniqueEvents[unique_event] += duration
            
        else:
            self.__start_event(unique_event, duration)


    def stop_unique_event(self, event : PluginAPI.Event, arguments : dict = {}):
        unique_event = ""
        if "UniqueEvent" in event.data:
            unique_event = event.data["UniqueEvent"]
            
        if "UniqueEvent" in arguments:
            unique_event = arguments["UniqueEvent"]
            
        if not unique_event in self.uniqueEvents:
            self.core.logger.log(f"UNIQUE EVENTS: Unknown unique event `{unique_event}`!")
            return
        
        self.uniqueEvents[unique_event] = 0.0
        self.__end_event(unique_event)
        
        
    def stop_all_unique_events(self, event : PluginAPI.Event, arguments : dict = {}):
        for event in self.uniqueEvents:
            self.uniqueEvents[event] = 0.0
            self.__end_event(event)
        
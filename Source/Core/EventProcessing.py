from pathlib import Path
import copy

from Core.Event import Event
from Core.EventProcessingPipelineNode import EventProcessingPipelineNode
import Core.DefaultEventProcessingFunctions as DefaultEventProcessingFunctions
from Core.Configuration import ConfigurationParser

# Handles event processing pipelines
class EventProcessing:
    
    def __init__(self, core):
        self.core = core
        
        # Mapping of events to pipelines
        self.eventMapping : dict[str, list[str]] = dict()
        
        # Table of pipelines <Pipeline Name, Pipeline Entry Point>
        self.pipelines : dict[str, EventProcessingPipelineNode] = dict()
        
        # Core EPFs
        self.coreEPFs : dict[str, callable] = {
            "If" : DefaultEventProcessingFunctions.condition_epf,
            "SetEventDataField" : DefaultEventProcessingFunctions.set_event_data_field,
            "SetLocalValues" : DefaultEventProcessingFunctions.set_local_var,
            "SetGlobalValues" : DefaultEventProcessingFunctions.set_global_var
        }
        
        # Global cache
        self.globalCache : dict = dict()
        
        
    def __run_pipeline_recursive(self, event : Event, node : EventProcessingPipelineNode, global_cache : dict, local_cache : dict):
    
        # Argument resolution
        arguments = dict()
        argument_string = node.functionArguments
        
        # @event keyword
        argument_string = argument_string.replace("@event", "event")
        
        # Local cache variables
        for local_v in local_cache:
            argument_string = argument_string.replace(f"@{local_v}", str(local_cache[local_v]))
            
        # Global cache variables
        for global_v in global_cache:
            argument_string = argument_string.replace(f"@{global_v}", str(global_cache[global_v]))
        
        arguments = eval("{" + argument_string + "}")
        
        self.core.logger.log(f"EVENT PROCESSING : Running pipeline node '{node.moduleName}:{node.functionName}' for event '{event.eventName}' : {str(arguments)}", should_print=False)
        
        
        # Cache and Flow access arguments
        arguments["node"] = node
        arguments["global_cache"] = global_cache
        arguments["local_cache"] = local_cache
        
        # Core functions
        if node.moduleName == "Core":
            next_node = self.coreEPFs[node.functionName](event, arguments, node, global_cache, local_cache)
            if next_node != None:
                self.__run_pipeline_recursive(event, next_node, global_cache, local_cache)
        
        # Plugin functions
        else:
            next_node = self.__call_plugin_epf(event, arguments, node, global_cache, local_cache)
            if next_node != None:
                self.__run_pipeline_recursive(event, next_node, global_cache, local_cache)
        
     
    def __call_plugin_epf(self, event : Event, arguments : dict, node : EventProcessingPipelineNode, global_cache : dict, local_cache : dict) -> EventProcessingPipelineNode:
        
        plugin_manager = self.core.pluginManager
        
        if not node.moduleName in plugin_manager.pluginsTable:
            raise Exception(f"EVENT PROCESSING : Failed to process pipeline node '{node.moduleName}:{node.functionName}': NO SUCH MODULE!")
        
        if not node.functionName in plugin_manager.pluginsTable[node.moduleName].eventProcessingFunctions:
            raise Exception(f"EVENT PROCESSING : Failed to process pipeline node '{node.moduleName}:{node.functionName}': Module '{node.moduleName}' has no EPF named {node.functionName}!")
        
        next_node = None
        
        try:
            next_node = plugin_manager.pluginsTable[node.moduleName].eventProcessingFunctions[node.functionName](event, arguments)
            
        except Exception as e:
            raise Exception(f"EVENT PROCESSING : Failed to process pipeline node '{node.moduleName}:{node.functionName}', with arguments {str(arguments)}: {str(e)}")
        
        if next_node == 0: return None # Special value for stopping the pipeline
        if next_node == None: # When epf didn't return a next node reference
            if len(node.nextNodeList) > 0:
                return node.nextNodeList[0]
            else:
                return None
            
        return next_node
        
        
    # Attempts to determine and execute a suitable pipelines for the specified event
    def process_event(self, event : Event):
        
        if not event.eventName in self.eventMapping:
            self.core.logger.log(f"EVENT PROCESSING : No suitable pipeline for event {event.eventName}")
            return
        
        for pipeline in self.eventMapping[event.eventName]:
            
            self.core.logger.log(f"EVENT PROCESSING : Starting pipeline '{pipeline}' for event '{event.eventName}'", should_print=False)
            
            event_copy = copy.deepcopy(event)
            local_cache = dict()
            self.__run_pipeline_recursive(event_copy, self.pipelines[pipeline], self.globalCache, local_cache)
        
    
    # Reads Event mapping file and pipeline files (called by the Core)
    def reload_config(self):
        
        config_dir = self.core.coreConfigPath
        config_parser : ConfigurationParser = self.core.configurationParser
        
        # Pipeline files
        self.pipelines.clear()
        
        # Gathering all files from the directory
        path = Path(config_dir + "/Pipelines")
        files = [f for f in path.rglob("*") if f.is_file()]
        
        # Looping over files and passing them to the ConfigurationParser module
        for file in files:
            pipeline_name, entry_point = config_parser.read_event_processing_pipeline_file(file)
            
            self.core.logger.log(f"EVENT PROCESSING : Loaded event processing pipeline '{pipeline_name}'")
            self.pipelines[pipeline_name] = entry_point
            
        #self.__debug_print_pipelines()
            
        # Event mapping file
        self.eventMapping = config_parser.read_event_mapping_file(config_dir + "/EventMapping.txt")
        
        # Checking validity of the event mapping
        for event in self.eventMapping:
            invalid_pipelines = []
            for pipeline in self.eventMapping[event]:
                if not pipeline in self.pipelines:
                    invalid_pipelines.append(pipeline)
                    self.core.logger.log(f"EVENT PROCESSING : event '{event}' is mapped to a non-existant pipeline '{pipeline}', removing the mapping!")
                    
            for inv_pipeline in invalid_pipelines:
                self.eventMapping[event].remove(inv_pipeline)
                
    
    def __debug_print_pipelines(self):
        
        for pipeline in self.pipelines:
            print("\n\n" + pipeline + ": \n{")
            self.__recursive_print_pipeline(self.pipelines[pipeline], 1)

    def __recursive_print_pipeline(self, node : EventProcessingPipelineNode, level):
        
        print("   " * level + f"{node.moduleName}:{node.functionName}({str(node.functionArguments)});")
        
        child_level = level
        if len(node.nextNodeList) == 0: 
            print("   " * (level - 1) + "}")
            child_level -= 1
        if len(node.nextNodeList) > 1: 
            print("   " * level + "{")
            child_level += 1
        
        for i, next in enumerate(node.nextNodeList):
            self.__recursive_print_pipeline(next, child_level)
            
            if i < len(node.nextNodeList) - 1:
                print("   " * level + "{")
                
        if len(node.nextNodeList) > 1:
            print("   " * (level - 1) + "}")
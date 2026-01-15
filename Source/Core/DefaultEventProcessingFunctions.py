from Core.Event import Event
from Core.EventProcessingPipelineNode import EventProcessingPipelineNode

# Input: event, pipeline node, global cache, local cache
# Output: next pipeline node

def condition_epf(event : Event, arguments : dict, pipeline_node : EventProcessingPipelineNode, global_cache, local_cache) -> EventProcessingPipelineNode:
    
    if len(pipeline_node.nextNodeList) == 0: return None
    if len(pipeline_node.nextNodeList) == 1: return pipeline_node.nextNodeList[0]
    
    condition = True
    for arg in arguments:
        if arg not in ["node", "global_cache", "local_cache"]:
            condition = condition and bool(arguments[arg])
    
    if (condition): return pipeline_node.nextNodeList[0]
    else: return pipeline_node.nextNodeList[1]
    
def set_event_data_field(event : Event, arguments : dict, pipeline_node : EventProcessingPipelineNode, global_cache, local_cache) -> EventProcessingPipelineNode:

    for arg in arguments:
        if arg not in ["node", "global_cache", "local_cache"]:
            event.data[arg] = arguments[arg]
        
    if len(pipeline_node.nextNodeList) == 0: return None
    return pipeline_node.nextNodeList[0]
    
def set_local_var(event : Event, arguments : dict, pipeline_node : EventProcessingPipelineNode, global_cache, local_cache) -> EventProcessingPipelineNode:

    for arg in arguments:
        if arg not in ["node", "global_cache", "local_cache"]:
            local_cache[arg] = arguments[arg]
        
    if len(pipeline_node.nextNodeList) == 0: return None
    return pipeline_node.nextNodeList[0]


def set_global_var(event : Event, arguments : dict, pipeline_node : EventProcessingPipelineNode, global_cache, local_cache) -> EventProcessingPipelineNode:

    for arg in arguments:
        if arg not in ["node", "global_cache", "local_cache"]:
            global_cache[arg] = arguments[arg]
        
    if len(pipeline_node.nextNodeList) == 0: return None
    return pipeline_node.nextNodeList[0]
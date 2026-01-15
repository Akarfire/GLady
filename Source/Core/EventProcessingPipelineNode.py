from dataclasses import dataclass, field

# Dataclass, containing data about a single step in an event processing pipeline, contains a link to the next node(s)
@dataclass
class EventProcessingPipelineNode:
    moduleName : str = ""
    functionName : str = ""
    functionArguments : str = ""
    nextNodeList : list = field(default_factory=list)
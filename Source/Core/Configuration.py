from pathlib import Path
import json

from Core.EventProcessingPipelineNode import EventProcessingPipelineNode

# This class is responsible for parsing standard configuration files:
# - Event Mapping;
# - Options;
class ConfigurationParser:

    def __init__(self, core):
        self.core = core

    # Parses event mapping file lines
    @staticmethod
    def __parse_event_mapping(lines : list[str]):

        # Parsing result
        # Event to function map < Event Name -> list [Processor function display name] >
        event_mapping : dict[str, list] = dict()

        for line in lines:

            # Ignoring spaces in lines
            line = line.replace(' ', '')
            line = line.strip()

            # Ignore empty lines
            if len(line) == 0: continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no "->" sign
            if not "->" in line: continue

            # Actual parsing
            event_name, function_names = line.split("->")

            function_list = [i for i in function_names.split(',')]

            # If specified event has not been mapped yet, then create a new entry in event mapping
            if not event_name in event_mapping:
                event_mapping[event_name] = function_list

            # Otherwise, append functions to an existing mapping
            else:
                for function in function_list:
                    event_mapping[event_name].append(function)

        return event_mapping


    # Parses event generation file lines
    @staticmethod
    def __parse_event_generation(lines : list[str]):

        # Parsing result
        # Event to function map < Inner Event : List of External Events >
        event_mapping : dict[str, list] = dict()

        for line in lines:

            # Ignoring spaces and new line symbols
            line = line.replace(' ', '')
            line = line.strip()

            # Ignore empty lines
            if len(line) == 0: continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no ":" sign
            if not ":" in line: continue

            # Actual parsing
            inner_event_names, generated_event_names = line.split(":")

            inner_event_names_list = [i for i in inner_event_names.split(',')]
            generated_event_names_list = [i for i in generated_event_names.split(',')]

            for inner_event_name in inner_event_names_list:
                
                # If specified event has not been assigned generated names yet, then create a new entry
                if not inner_event_name in event_mapping:
                    event_mapping[inner_event_name] = generated_event_names_list

                # Otherwise, append generated event names to an existing generation list
                else:
                    for generated_name in generated_event_names_list:
                        event_mapping[inner_event_name].append(generated_name)

        return event_mapping


    # Parses option config lines
    @staticmethod
    def __parse_options(lines : list[str]):

        # Resulting options
        options = dict()

        for line in lines:

            line = line.strip()

            # Ignore empty lines
            if len(line) == line.count(' '): continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no "->" sign
            if not "=" in line: continue

            # Actual parsing
            option_name, option_value = line.split("=")
            options[option_name.replace(' ', '')] = eval(option_value) # Evaluating option values to make values more flexible

        return options
    
    
    # Parses event processing pipeline code
    @staticmethod
    def __parse_event_processing_pipeline(lines : list[str]) -> tuple[str, dict]:
        
        # Result
        pipeline_name = ""
        entry_point : EventProcessingPipelineNode = None
        
        # Parsing
        
        # Joining lines
        code_line = ""
        
        for line in lines:
            line = line.strip()
            
            # Ignoring empty lines and comments
            if len(line) == 0: continue
            if line.startswith('#'): continue
            
            code_line += line.replace('\n', '')
            
        # Analyzing code line
        current_token = ""
        current_node : EventProcessingPipelineNode = None
        previous_node_stack : list[EventProcessingPipelineNode] = list()
        
        # '{' -> +1, '}' -> -1
        flow_bracket_counter = 0
        # '(' -> +1, ')' -> -1
        argument_bracket_counter = 0
        
        first_in_branch_flag = False
        
        for c in code_line:

            # Pipeline name
            if pipeline_name == "" and c == '{':
                pipeline_name = current_token
                
                flow_bracket_counter += 1
                current_token = ""
                continue
            
            # Finilizing node
            if (c == ';' or (c == '{' and current_node != None)) and argument_bracket_counter == 0:
                if current_node == None: raise Exception("';' with no function call prior to it!")
                
                if len(previous_node_stack) == 0:
                    entry_point = current_node
                else:
                    previous_node = previous_node_stack[-1]
                    previous_node.nextNodeList.append(current_node)
                    
                    if not first_in_branch_flag:
                        previous_node_stack.pop()
                    first_in_branch_flag = False
                    
                previous_node_stack.append(current_node)
                
                if c == '{':
                    flow_bracket_counter += 1
                    first_in_branch_flag = True
                
                current_node = None
                current_token = ""
                continue
            
            # Brackets
            if c == '{' and argument_bracket_counter == 0: 
                flow_bracket_counter += 1
                if flow_bracket_counter > 1:
                    first_in_branch_flag = True
                continue
            if c == '}' and argument_bracket_counter == 0:
                flow_bracket_counter -= 1
                
                # End of branch
                if flow_bracket_counter > 0 and not first_in_branch_flag:
                    previous_node_stack.pop()
                
                # End of pipeline
                if flow_bracket_counter == 0:
                    break
                
                continue
            
            # Module name
            if c == ':' and argument_bracket_counter == 0:
                if len(current_token) == 0: raise Exception("Empty module name!")
                
                current_node = EventProcessingPipelineNode()
                current_node.moduleName = current_token
                current_token = ""
                continue
            
            # Arguments
            if c == '(':
                argument_bracket_counter += 1
                
                # Function name & arguments start
                if argument_bracket_counter == 1:
                    if current_node == None: raise Exception("No module specified in function call!")
                    if len(current_token) == 0: raise Exception("No name function name specified in function call!")
                    
                    current_node.functionName = current_token
                    current_token = ""
                    continue
                
            if c == ')':
                argument_bracket_counter -= 1
                
                # Function arguments end
                if argument_bracket_counter == 0:
                    if current_node == None: raise Exception("No module and name specified in function call!")
                    
                    arguments = current_token # Arguments are resolved during interpretation
                    current_node.functionArguments = arguments
                    
                    current_token = ""
                    continue
            
            current_token += c
        
        return pipeline_name, entry_point
        

    # Reads event mapping config file at the specified path
    def read_event_mapping_file(self, path: str) -> dict[str, list[str]]:

        # Checking if the file exists and creating it if it does not
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"Event Mapping config file at {path} was not found! Creating one now!", message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                file.write("# Each line is a mapping of an event to a list of processor functions <Event Name> -> <Event Processing Pipeline Name>, <Event Processing Pipeline Name>, ...\n\n")

        # Reading data form the file
        with open(path) as file:
            # Actual reading of the file
            lines = file.readlines()
            mapping = self.__parse_event_mapping(lines)

            return mapping
    
    
    # Reads event generation config file at the specified path
    def read_event_generation_file(self, path: str, default_event_generation_config : dict[str, list[str]] = {}):

        # Checking if the file exists and creating it if it does not
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"Event Generation config file at {path} was not found! Creating one now!", message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                file.write("# Specifying custom names for events that are generated by this plugin\n# <InnerEventName> : <GeneratedEventName_1>, <GeneratedEventName_2>, ...\n\n")
                
                # Writing default event generation config into the new file
                for default_event in default_event_generation_config:
                    file.write(f"{default_event} : ")
                    
                    num_names = len(default_event_generation_config[default_event])
                    for index, event_name in enumerate(default_event_generation_config[default_event]):
                        file.write(event_name)
                        if index != num_names - 1:
                            file.write(", ")

        # Reading data form the file
        with open(path) as file:
            # Actual reading of the file
            lines = file.readlines()
            mapping = self.__parse_event_generation(lines)

        return mapping


    # Reads options config file at the specified path
    def read_options_file(self, path: str, default_options: dict = {}) -> dict:

        # Checking if the file exists and creating it if it does not
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"Options config file at {path} was not found! Creating one now!",
                                 message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                file.write(
                    "# Configuration options are defined here: <OptionName> = <Value>\n\n")

                for default_option in default_options:
                    
                    if type(default_options[default_option]) == str:
                        file.write(f'{default_option} = "{default_options[default_option]}"\n')
                        
                    else:
                        file.write(f'{default_option} = {default_options[default_option]}\n')

        # Actual reading of the file
        with open(path) as file:
            lines = file.readlines()
            options = self.__parse_options(lines)

            return options


    # Reads event processing pipeline file at the specified path
    def read_event_processing_pipeline_file(self, path: str) -> tuple[str, dict]:
        
        # Checking if the file exists and creating it if it does not
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"EVENT PROCESSING : Event Processing Pipeline file at {path} was not found!", message_type=1)
            return
        
        with open(path) as file:
            lines = file.readlines()
            
            pipeline_name = ""
            entry_point = None
            try:
                pipeline_name, entry_point = self.__parse_event_processing_pipeline(lines)
                
            except Exception as e:
                self.core.logger.log(f"EVENT PROCESSING : Failed to parse event processing pipeline file '{path}': {str(e)}", message_type=1)
                
            return pipeline_name, entry_point
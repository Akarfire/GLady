from pathlib import Path

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


    # Parses event mapping file lines
    @staticmethod
    def __parse_event_generation(lines : list[str]):

        # Parsing result
        # Event to function map < Event Name -> list [Processor function display name] >
        event_mapping : dict[str, list] = dict()

        for line in lines:

            # Ignoring spaces and new line symbols
            line = line.replace(' ', '')
            line = line.strip()

            # Ignore empty lines
            if len(line) == 0: continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no "->" sign
            if not ":" in line: continue

            # Actual parsing
            inner_event_name, generated_event_names = line.split(":")

            generated_event_names_list = [i for i in generated_event_names.split(',')]

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


    # Reads event mapping config file at the specified path
    def read_event_mapping_file(self, path: str):

        # Checking if the file exists and creating it if it does not
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"Event Mapping config file at {path} was not found! Creating one now!", message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                file.write("# Each line is a mapping of an event to a list of processor functions <Event Name> -> <Event Processor Function Name>, <Event Processor Function Name>, ...\n\n")

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
    def read_options_file(self, path: str, default_options: dict = {}):

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

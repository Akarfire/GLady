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

            # Ignore empty lines
            if len(line) == 0: continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no "->" sign
            if not "->" in line: continue

            # Actual parsing
            event_name, function_names = line.split("->")

            function_list = [i.replace("\n", "") for i in function_names.split(',')]

            # If specified event has not been mapped yet, then create a new entry in event mapping
            if not event_name in event_mapping:
                event_mapping[event_name] = function_list

            # Otherwise, append functions to an existing mapping
            else:
                for function in function_list:
                    event_mapping[event_name].append(function)

        return event_mapping


    # Parses option config lines
    @staticmethod
    def __parse_options(lines : list[str]):

        # Resulting options
        options = dict()

        for line in lines:

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

        # Opening file (or creating it if it does not exist)
        try:
            file = open(path)

        except:
            self.core.logger.log(f"Event Mapping config file at {path} was not found! Creating one now!", message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            file = open(path, "w")
            file.write("# Each line is a mapping of an event to a list of processor functions <Event Name> -> <Event Processor Function Name>, <Event Processor Function Name>, ...\n")
            file.close()

            file = open(path)

        # Actual reading of the file
        lines = file.readlines()
        mapping = self.__parse_event_mapping(lines)

        file.close()

        return mapping


    # Reads options config file at the specified path
    def read_options_file(self, path: str, default_options: dict = {}):

        # Opening file (or creating it if it does not exist)
        try:
            file = open(path)

        except:
            self.core.logger.log(f"Options config file at {path} was not found! Creating one now!",
                                 message_type=1)

            # Creating directory and initializing config file
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            file = open(path, "w")
            file.write(
                "# Configuration options are defined here: <OptionName> = <Value>\n")

            for default_option in default_options:
                
                if type(default_options[default_option]) == str:
                    file.write(f'{default_option} = "{default_options[default_option]}"\n')
                    
                else:
                    file.write(f'{default_option} = {default_options[default_option]}\n')

            file.close()

            file = open(path)

        # Actual reading of the file
        lines = file.readlines()
        options = self.__parse_options(lines)

        file.close()

        return options

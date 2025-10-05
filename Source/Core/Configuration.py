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
            if line.count(' ') == len(line): continue

            # Ignore comment lines
            if line.startswith('#'): continue

            # Ignore lines with no "->" sign
            if not " -> " in line: continue

            # Actual parsing
            event_name, function_names = line.split(" -> ")

            function_list = [i.replace("\n", "") for i in function_names.split(', ')]

            # If specified event has not been mapped yet, then create a new entry in event mapping
            if not event_name in event_mapping:
                event_mapping[event_name] = function_list

            # Otherwise, append functions to an existing mapping
            else:
                for function in function_list:
                    event_mapping[event_name].append(function)

        return event_mapping



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
            file.write("# Each line is a mapping of an event to a list of processor functions <Event Name> -> <Event Processor Function Name>, <Event Processor Function Name>, ...")
            file.close()

            file = open(path)

        # Actual reading of the file
        lines = file.readlines()

        return self.__parse_event_mapping(lines)

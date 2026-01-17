import Plugin as PluginAPI
import copy
from pathlib import Path

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        self.commandFilePath = "Config/Commands.txt"

        self.defaultOptions : dict = {
            "GeneratedEventCommandNameField" : "Command",
            "MessageEventField" : "Message",
            "RemoveCommandsFromMessages" : True
        }

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["ProcessMessageCommands"] = self.process_message_commands
        #...
        
        # <Command Word : <Event Name, Additional Event Parameters>>
        self.commands : dict[str, tuple[str, dict]] = dict()

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)

    def reload_config(self):
        super().reload_config()
        
        self.commands.clear()
        self.__read_commands_config()


    def __read_commands_config(self):
        file_path = self.directory + "/" + self.commandFilePath
        path = Path(file_path)
        
        if not path.exists():
            self.core.logger.log(f"SIMPLE MESSAGE COMMANDS : No commands config file found at '{file_path}'! Creating one now.", message_type=1)
            
            path.mkdir(exist_ok=True)
            with open(file_path, 'w') as file:
                file.write('# List of commands <Command Keyword>, <Command Keyword>, ... -> <Event Name>(<Additional Event Parameters>)\n \
                            # SAMPLE_COMMAND -> SampleCommandEvent("param_1" : 1, "param_2" : "Hello!")')
        
        with open(file_path) as file:
            lines = file.readlines()
            self.commands = self.__parse_commands_config_lines(lines)
            
            
    def __parse_commands_config_lines(self, lines : list[str]) -> dict[str, tuple[str, dict]]:
        
        # Result
        commands = dict()
        
        # Parsing
        for line in lines:
            line = line.strip()
            line = line.replace('\n', '')
            
            # Skipping comments
            if line.startswith('#'): continue
            # Skipping empty lines
            if len(line) == 0: continue
            # Skipping lines without '->' symbol
            if line.count("->") != 1: continue
            
            command_names, event = line.split("->")
            command_names_list = [i.replace(' ', '') for i in command_names.split(",")]
            
            event_data = None
            if not '(' in event:
                event_data = (event.strip(), {})

            else:
                event_name, arguments_line = event.split('(', 1)
                
                bracket_counter = 1
                for c in arguments_line:
                    if c == '(': bracket_counter += 1
                    elif c == ')': bracket_counter -= 1
                    
                if bracket_counter != 0:
                    self.core.logger.log(f"SIMPLE MESSAGE COMMANDS : Brackets error in line '{line}'", message_type=1)
                    continue
                
                if not arguments_line.endswith(')'):
                    self.core.logger.log(f"SIMPLE MESSAGE COMMANDS : Line '{line}' does not end with a ')'", message_type=1)
                
                arguments_line = arguments_line[:-1]
                
                arguments = {}
                try:
                    arguments = eval('{' + arguments_line + '}')
                except Exception as e:
                    self.core.logger.log(f"SIMPLE MESSAGE COMMANDS : Failed to evaluate arguments: '{arguments_line}' in line '{line}' : {str(e)}", message_type=1)

                event_data = (event_name.strip(), arguments)

            for name in command_names_list:
                commands[name] = event_data
        
        return commands
    
    
    # Removes all valid commands from the message
    def __remove_message_commands(self, message : str) -> str:
        
        stripped_message = message
        for command in self.commands:
            stripped_message = stripped_message.replace(f"!{command}!", "")
            
        return stripped_message
        

    # Example event processor function
    def process_message_commands(self, event : PluginAPI.Event, arguments : dict = {}):

        generated_event_command_name_field = self.get_option("GeneratedEventCommandNameField")
        message_field = self.get_option("MessageEventField")
        
        if "GeneratedEventCommandNameField" in arguments:
            generated_event_command_name_field = arguments["GeneratedEventCommandNameField"]
        
        if "MessageEventField" in arguments:
            message_field = arguments["MessageEventField"]
            
        if message_field in event.data and type(event.data[message_field]) == str:

            # Splitting message into segments and looking up each one in the commands list
            segments = event.data[message_field].split('!')
            
            # Removing commands from messages
            should_remove_commands = self.get_option("RemoveCommandsFromMessages")
            if "RemoveCommandsFromMessages" in arguments:
                should_remove_commands = arguments["RemoveCommandsFromMessages"]
                
            if should_remove_commands:
                event.data[message_field] = self.__remove_message_commands(event.data[message_field])
            
            for seg in segments:
                seg = seg.strip()
                seg = seg.replace('\n', '')
                seg = seg.replace(' ', '_')
                seg = seg.upper()
                
                if seg in self.commands:
                    self.core.logger.log(f"SIMPLE MESSAGE COMMANDS : Detected '!{seg}!' in message '{event.data[message_field]}'", should_print=False)
                    
                    data = copy.deepcopy(event.data)
                    data[generated_event_command_name_field] = seg
                    
                    for param in self.commands[seg][1]:
                        data[param] = self.commands[seg][1][param]
                    
                    command_event = PluginAPI.Event(self.commands[seg][0], self.pluginName, event.tags, data)
                    self.generate_event(command_event)
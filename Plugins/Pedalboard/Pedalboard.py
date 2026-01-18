import pedalboard
import Plugin as PluginAPI

from pedalboard.io import AudioFile
from pedalboard import Pedalboard, Chorus, Compressor, Gain, PitchShift, Reverb

class PedalboardPlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        self.defaultOptions : dict = {
            "SampleRate" : 44100.0,
        }

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["Chorus"] = self.effect_chorus
        #...
    

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)


    # Returns <Input File, Output File>
    def __get_files_from_event_data(self, event : PluginAPI.Event, arguments : dict = {}) -> tuple[str, str]:
        
        input_file = ""
        output_file = ""
        
        if "File" in event.data:
            input_file = event.data["File"]
            output_file = event.data["File"]
            
        if "InputFile" in event.data:
            input_file = event.data["InputFile"]
            
        if "Output" in event.data:
            output_file = event.data["Output"]
            
            
        if "File" in arguments:
            input_file = arguments["File"]
            output_file = arguments["File"]
            
        if "InputFile" in arguments:
            input_file = arguments["InputFile"]
            
        if "Output" in arguments:
            output_file = arguments["Output"]
            
        return input_file, output_file
        

    # Example event processor function
    def effect_chorus(self, event : PluginAPI.Event, arguments : dict = {}):
        
        input_file, output_file = self.__get_files_from_event_data(event, arguments)

        if input_file == "" or output_file == "":
            raise Exception(f"Input or output unspecified: I : '{input_file}', O : '{output_file}'!")

        samplerate = self.get_option("SampleRate")

        audio = None
        with AudioFile(input_file).resampled_to(samplerate) as f:
            audio = f.read(f.frames)
            
            board = Pedalboard(
                [
                    
                ]
            )

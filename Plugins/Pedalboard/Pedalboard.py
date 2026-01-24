import pedalboard
import Plugin as PluginAPI

from pedalboard.io import AudioFile
from pedalboard import Pedalboard, Chorus, Compressor, Gain, PitchShift, Reverb

class PedalboardPlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        self.defaultOptions : dict = {
            "SampleRate" : 44100.0,
            "EffectsList_EventField" : "AudioEffects"
        }

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["ApplyEffects"] = self.apply_effects
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
    def __get_files_from_data(self, event : PluginAPI.Event, arguments : dict = {}) -> tuple[str, str]:
        
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
        

    # Applies all effects specified in the arguments / specific event field
    def apply_effects(self, event : PluginAPI.Event, arguments : dict = {}):
        
        # File parameters
        input_file, output_file = self.__get_files_from_data(event, arguments)
        
        if input_file == "" or output_file == "":
            raise Exception(f"Input or output unspecified: I : '{input_file}', O : '{output_file}'!")
        
        # Audio effect parameters
        audio_effects_event_field = self.get_option("EffectsList_EventField")
        if "EffectsList_EventField" in event.data:
            audio_effects_event_field = event.data["EffectsList_EventField"]
        if "EffectsList_EventField" in arguments:
            audio_effects_event_field = arguments["EffectsList_EventField"]
        
        audio_effects = ""
        if audio_effects_event_field in event.data:
            audio_effects = event.data[audio_effects_event_field]
        if "EffectsList" in arguments:
            append_effects = False
            if "AppendEffects" in arguments:
                append_effects = arguments["AppendEffects"]
            
            if append_effects:
                audio_effects.extend(arguments["EffectsList"])
            else:
                audio_effects = arguments["EffectsList"]
               
        if audio_effects == "": return
                    
        # Audio effects list
        audio_effects_list = eval(audio_effects)
        if not type(audio_effects) != list:  raise Exception(f"Incorrect argument : audio effects are not specified as a list: {audio_effects_list}")
                        
        # Sample rate
        samplerate = self.get_option("SampleRate")
        if "SampleRate" in event.data:
            samplerate = event.data["SampleRate"]
        if "SampleRate" in arguments:
            samplerate = arguments["SampleRate"]

        # Processing audio
        try:
            audio = None
            with AudioFile(input_file).resampled_to(samplerate) as f:
                audio = f.read(f.frames)
                
            board = Pedalboard(audio_effects_list)

            processed_audio = board(audio, samplerate)
            
            with AudioFile(output_file, 'w', samplerate, processed_audio.shape[0]) as f:
                f.write(processed_audio)
                
        except Exception as e:
            raise Exception(f"Failed to process audio : {str(e)}")
                

    # # Example event processor function
    # def effect_chorus(self, event : PluginAPI.Event, arguments : dict = {}):
        
    #     input_file, output_file = self.__get_files_from_data(event, arguments)

    #     if input_file == "" or output_file == "":
    #         raise Exception(f"Input or output unspecified: I : '{input_file}', O : '{output_file}'!")

    #     samplerate = self.get_option("SampleRate")

    #     audio = None
    #     with AudioFile(input_file).resampled_to(samplerate) as f:
    #         audio = f.read(f.frames)
            
    #         board = Pedalboard(
    #             [
                    
    #             ]
    #         )

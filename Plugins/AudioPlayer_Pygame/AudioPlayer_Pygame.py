import Plugin as PluginAPI

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

class AudioPlayer_Pygame(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["PlayAudio"] = self.play_audio
        #...
        
        # Defining default event generation settings
        self.defaultGeneratedEventNames = {
            "FinishedPlaying" : ["AudioFinishedPlaying"]
        }
        
        # Defining default options
        self.defaultOptions : dict = {
            "VolumeMultiplier" : 1,
            "AuthDataFilepath" : "$PluginDirectory$/Config/AuthData.txt"
        }
        
        self.audioTimers : dict[str, float] = dict()

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        # Default AudioPlayer events
        self.generatedEventNames["FinishedPlaying"].append("AUDIO_FINISHED_PLAYING")
        
        # Initialize the mixer
        pygame.mixer.init()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)
        
        # Updating audio timers
        for audio in self.audioTimers:
            self.audioTimers[audio] -= delta_time
            if self.audioTimers[audio] <= 0:
                
                event = PluginAPI.Event(
                    "FinishedPlaying", 
                    self.pluginName, 
                    set(), 
                    {"audio_file" : audio}
                )
            
                self.generate_event(event)


    # Plays a sound, specified in the event description
    def play_audio(self, event : PluginAPI.Event, arguments : dict = {}):

        if not "audio_file" in event.data:
            raise LookupError("No 'audio_file' entry in event's data!")
        if type(event.data["audio_file"]) != str:
            raise LookupError("'audio_file' entry in event's data is not a string!")
        
        # Loading audio file
        sfx = pygame.mixer.Sound(event.data["audio_file"])
        
        # Playback volume
        volume = self.get_option("VolumeMultiplier")
        
        if "volume" in event.data and type(event.data["volume"]) in [float, int]:
            volume *= event.data["volume"]
        
        if "Volume" in arguments and type(arguments["Volume"]) in [float, int]:
            volume *= arguments["Volume"]
            
        sfx.set_volume(volume)
        
        # Playing sfx
        sfx.play()
        
        # Setting up a timer
        audio_entry = event.data["audio_file"] + "_" + event.initiator
        self.audioTimers[audio_entry] = sfx.get_length()
        
        


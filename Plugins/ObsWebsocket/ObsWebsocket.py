import Plugin as PluginAPI

from pathlib import Path
import logging

import obsws_python as obs
from obsws_python.error import OBSSDKError, OBSSDKTimeoutError

class ObsWebsocket(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["SetScene"] = self.set_scene
        self.eventProcessingFunctions["SetSourceVisibility"] = self.set_source_visibility
        self.eventProcessingFunctions["SetInputMute"] = self.set_input_mute
        self.eventProcessingFunctions["SetInputVolume"] = self.set_input_volume
        self.eventProcessingFunctions["ControlMedia"] = self.control_media
        self.eventProcessingFunctions["ReloadBrowserSource"] = self.reload_browser_source
        #...
        
        # Defining default options
        self.defaultOptions : dict = {
            "AuthDataFilepath" : "$Private$/Auth/ObsAuthData.txt",
            "ConnectionTimeout" : 0.5,
            "AutoReconnect" : True,
            "AutoReconnectTimeout" : 5
        }
        
        # Defining default event generation settings
        self.defaultGeneratedEventNames = {
            "OBS_Connected" : ["OBS_Connected"]
        }
        
        # Authentication info
        self.obsIp : str = ""
        self.obsPort : int = 0
        self.obsPassword = ""
        
        # Connection info
        self.client : obs.ReqClient = None
        
        self.firstConnection = True
        self.reconnectTimer = 0.0
        
        # Silencing weird logging
        logging.getLogger("websocket").setLevel(logging.CRITICAL)
        logging.getLogger("obsws_python").setLevel(logging.CRITICAL)
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)

        # Connection / Reconnection
        if self.client is None:
            if self.firstConnection or self.get_option("AutoReconnect") and self.reconnectTimer > self.get_option("AutoReconnectTimeout"):
                self.firstConnection = False
                self.reconnectTimer = 0.0
                
                self.__connect()
                    
                
            else:
                self.reconnectTimer += delta_time
                

    # Loading (and Reloading) configuration files
    def reload_config(self):
        super().reload_config()
        self.__read_auth_data()


    # Attempts to connect to OBS websocket server
    def __connect(self):
        try:
            self.client = obs.ReqClient(
                host=self.obsIp, 
                port=self.obsPort, 
                password=self.obsPassword, 
                timeout=self.get_option("ConnectionTimeout")
            )
            
            self.core.logger.log(f"OBS WEBSOCKET : Connection succesful!")
            
            notify_event = PluginAPI.Event("OBS_Connected", self.pluginName, {}, {})
            self.generate_event(notify_event)
            
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : Failed to connect : {str(e)}", message_type=1)
    

    # Reades authentication data file (or creates a new one)
    def __read_auth_data(self):
        path = self.get_option("AuthDataFilepath").replace("$Private$", self.core.privateDataPath)
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"OBS WEBSOCKET : Authentication data file at '{path}' doesn't exist, creating now")
            
            Path(Path(path).parent.resolve()).mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as auth_data_file:
                auth_data_file.write(
                   "ip: localhost\n\
                    port: 4455\n\
                    password: ".replace('    ', '')
                )

        else:
            with open(path) as auth_data_file:
                lines = auth_data_file.readlines()
                
                for line in lines:
                    line = line.strip()
                    
                    if line.startswith("ip:"):
                        self.obsIp = line.replace('ip:', '').replace(" ", "")
                    
                    if line.startswith("port:"):
                        self.obsPort = line.replace('port:', '').replace(" ", "")
                        
                    if line.startswith("password:"):
                        self.obsPassword = line.replace('password:', '').replace(" ", "")
            

    # Changes current OBS Scene
    def set_scene(self, event : PluginAPI.Event, arguments : dict = {}):
        # Obtaining Arguments
        new_scene = ""
        # From event
        if "NewScene" in event.data: new_scene = event.data["NewScene"]
        
        # From Arguments
        if "NewScene" in arguments: new_scene = arguments["NewScene"]
        
        if new_scene == "":
            self.core.logger.log(f"OBS WEBSOCKET : SET SCENE : No scene specified", message_type=1)
            return
        
        # Running command
        if self.client is None:
            self.core.logger.log(f"OBS WEBSOCKET : SET SCENE : Not connected to OBS", message_type=1)
            return
        
        try:
            self.client.set_current_program_scene(new_scene)
            
        except (obs.error.OBSSDKTimeoutError, obs.error.OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error!", message_type=1)
            self.client = None
            
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : SET SCENE : {str(e)}", message_type=1)
            
            
    # Toggles or sets the visibility of a source in a scene
    def set_source_visibility(self, event: PluginAPI.Event, arguments: dict = {}):  
        # Obtaining Arguments
        scene_name = ""
        source_name = ""
        visible_state = None  # None = toggle, True = visible, False = hidden

        # From event
        if "SceneName" in event.data: scene_name = event.data["SceneName"]
        if "SourceName" in event.data: source_name = event.data["SourceName"]
        if "Visible" in event.data: visible_state = event.data["Visible"]

        # From arguments (override event)
        if "SceneName" in arguments: scene_name = arguments["SceneName"]
        if "SourceName" in arguments: source_name = arguments["SourceName"]
        if "Visible" in arguments: visible_state = arguments["Visible"]

        if not scene_name or not source_name:
            self.core.logger.log("OBS WEBSOCKET : SET VISIBILITY : Missing SceneName or SourceName", message_type=1)
            return

        if self.client is None:
            self.core.logger.log("OBS WEBSOCKET : SET VISIBILITY : Not connected to OBS", message_type=1)
            return

        # Running command
        try:
            # Get the scene item ID for the source
            resp = self.client.get_scene_item_id(scene_name, source_name)
            scene_item_id = resp.scene_item_id

            # Determine desired visibility state
            if visible_state is None:
                current = self.client.get_scene_item_enabled(scene_name, scene_item_id)
                visible_state = not current.scene_item_enabled

            # Apply the visibility
            self.client.set_scene_item_enabled(scene_name, scene_item_id, visible_state)
            
        except (obs.error.OBSSDKTimeoutError, obs.error.OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error! {e}", message_type=1)
            self.client = None
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : SET VISIBILITY : {str(e)}", message_type=1)
                
            
    # Mutes or unmutes an audio input
    def set_input_mute(self, event: PluginAPI.Event, arguments: dict = {}):
        # Obtaining Arguments
        input_name = ""
        muted_state = None  # None = toggle, True = mute, False = unmute

        if "InputName" in event.data: input_name = event.data["InputName"]
        if "Muted" in event.data: muted_state = event.data["Muted"]

        if "InputName" in arguments: input_name = arguments["InputName"]
        if "Muted" in arguments: muted_state = arguments["Muted"]

        if not input_name:
            self.core.logger.log("OBS WEBSOCKET : SET MUTE : Missing InputName", message_type=1)
            return

        if self.client is None:
            self.core.logger.log("OBS WEBSOCKET : SET MUTE : Not connected to OBS", message_type=1)
            return

        # Running command
        try:
            if muted_state is None:
                self.client.toggle_input_mute(input_name)
            else:
                self.client.set_input_mute(input_name, muted_state)

        except (obs.error.OBSSDKTimeoutError, obs.error.OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error! {e}", message_type=1)
            self.client = None
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : SET MUTE : {str(e)}", message_type=1)
            
            
    # Sets the volume of an audio input (1.0 = 100%)
    def set_input_volume(self, event: PluginAPI.Event, arguments: dict = {}):
        # Obtaining Arguments
        input_name = ""
        volume_multiplier = 1.0

        if "InputName" in event.data: input_name = event.data["InputName"]
        if "Volume" in event.data: volume_multiplier = event.data["Volume"]

        if "InputName" in arguments: input_name = arguments["InputName"]
        if "Volume" in arguments: volume_multiplier = arguments["Volume"]

        if not input_name:
            self.core.logger.log("OBS WEBSOCKET : SET VOLUME : Missing InputName", message_type=1)
            return

        if self.client is None:
            self.core.logger.log("OBS WEBSOCKET : SET VOLUME : Not connected to OBS", message_type=1)
            return

        # Running command
        try:
            self.client.set_input_volume(input_name, volume_multiplier)

        except (obs.error.OBSSDKTimeoutError, obs.error.OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error! {e}", message_type=1)
            self.client = None
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : SET VOLUME : {str(e)}", message_type=1)


    # Controls a media input (Play, Pause, Stop, Restart)
    def control_media(self, event: PluginAPI.Event, arguments: dict = {}):
        # Obtaining Arguments
        input_name = ""
        action = ""  # "PLAY", "PAUSE", "STOP", "RESTART"

        if "InputName" in event.data: input_name = event.data["InputName"]
        if "Action" in event.data: action = event.data["Action"].upper()

        if "InputName" in arguments: input_name = arguments["InputName"]
        if "Action" in arguments: action = arguments["Action"].upper()

        if not input_name or not action:
            self.core.logger.log("OBS WEBSOCKET : MEDIA CONTROL : Missing InputName or Action", message_type=1)
            return

        if self.client is None:
            self.core.logger.log("OBS WEBSOCKET : MEDIA CONTROL : Not connected to OBS", message_type=1)
            return

        # Running command
        try:
            if action == "PLAY":
                self.client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY")
            elif action == "PAUSE":
                self.client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE")
            elif action == "STOP":
                self.client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP")
            elif action == "RESTART":
                self.client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
            else:
                self.core.logger.log(f"OBS WEBSOCKET : MEDIA CONTROL : Unknown action '{action}'", message_type=1)

        except (obs.error.OBSSDKTimeoutError, obs.error.OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error! {e}", message_type=1)
            self.client = None
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : MEDIA CONTROL : {str(e)}", message_type=1)
            
            
    # Reloads a browser source by pressing its "refreshnocache" properties button
    def reload_browser_source(self, event: PluginAPI.Event, arguments: dict = {}):
        browser_source = ""
        
        if "BrowserSource" in event.data:
            browser_source = event.data["BrowserSource"]
            
        if "BrowserSource" in arguments:
            browser_source = arguments["BrowserSource"]
        
        if not browser_source:
            self.core.logger.log("OBS WEBSOCKET : RELOAD BROWSER : Missing BrowserSource", message_type=1)
            return

        if self.client is None:
            self.core.logger.log("OBS WEBSOCKET : RELOAD BROWSER : Not connected to OBS", message_type=1)
            return

        try:
            # "refreshnocache" is the internal name of the "Refresh cache of current page" button
            self.client.press_input_properties_button(browser_source, "refreshnocache")
            
        except (OBSSDKTimeoutError, OBSSDKError) as e:
            self.core.logger.log(f"OBS WEBSOCKET : Connection error! {e}", message_type=1)
            self.client = None
        except Exception as e:
            self.core.logger.log(f"OBS WEBSOCKET : RELOAD BROWSER : {str(e)}", message_type=1)
import Plugin as PluginAPI

from gtts import gTTS
import json
import asyncio
import websockets
import threading
from pathlib import Path

class TextToSpeechPlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
    
        # Defining default options
        self.defaultOptions : dict = {
            "ip" : "localhost",
            "port" : 8003,
            "DefaultDataSelector" : "Message",
            "DefaultLanguage" : "en",
            "DefaultEngine" : "GTTS",
            "TTS_FileName" : "TTS.mp3",
            "LogTTS" : False,
            "AudioVolume" : 1,
            "SpeakingImageName" : "TTS_Speak.png",
            "SilentImageName" : "TTS_Silent.png"
        }
        
        self.savePath = "./Resources/TTS"
    
        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["PlayTTS"] = self.play_text_to_speech
        
        # Actual plugin data
        
        self.clients : set[websockets.WebSocketServerProtocol] = set()
        
        self.serverThread : threading.Thread = None
        
        self.asyncEventLoop = None
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        # Resource sub directory
        resource_path = Path(self.savePath)
        resource_path.mkdir(exist_ok=True)
        
        def __start_loop():
            self.asyncEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.asyncEventLoop)
            self.asyncEventLoop.run_until_complete(self.__async_server_loop())
        
        self.serverThread = threading.Thread(target=__start_loop, daemon=True)
        self.serverThread.start()


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()


    # Converts text to speech, returns path to the file relative to "Resources/TTS"
    def __convert_tts(self, text : str, event : PluginAPI.Event, arguemnts : dict) -> str:
        
        language = self.get_option("DefaultLanguage")
        
        if "Language" in event.data:
            language = event.data["Language"]
        if "Language" in arguemnts:
            language = arguemnts["Language"]
        
        my_gtts = gTTS(text=text, lang=language, slow=False)
        
        file_name = self.get_option("TTS_FileName")
        if "TTS_FileName" in event.data:
            file_name = event.data["TTS_FileName"]
        if "TTS_FileName" in arguemnts:
            file_name = arguemnts["TTS_FileName"]
            
        my_gtts.save(self.savePath + "/" + file_name)
        return file_name
        

    # Converts tts and sends data to the client
    def play_text_to_speech(self, event : PluginAPI.Event, arguments : dict = {}):
        
        data_selector = self.get_option("DefaultDataSelector")
        if "DataSelector" in arguments:
            data_selector = arguments["DataSelector"]
        
        if not data_selector in event.data or len(event.data[data_selector]) == 0: return
        
        if self.get_option("LogTTS"):
            if "UserName" in event.data:
                self.core.logger.log(f"TTS : {event.data["UserName"]} : {event.data[data_selector]}")
            else:
                self.core.logger.log(f"TTS : {event.data[data_selector]}")
        
        if not "Volume" in event.data: 
            event.data["Volume"] = 1
            
        if "Volume" in arguments and type(arguments["Volume"]) in [float, int]:
            event.data["Volume"] *= arguments["Volume"]
        
        # Converting tts and storing file path
        event.data["TTS_File"] = self.__convert_tts(event.data[data_selector], event, arguments)
        event.data["Text"] = event.data[data_selector]
        
        # Sending command to ui
        if self.asyncEventLoop and self.asyncEventLoop.is_running():
            asyncio.run_coroutine_threadsafe(self.__broadcast(event.data), self.asyncEventLoop)
            
    
    # Sends data to all of the clients
    async def __broadcast(self, data : dict):
        
        json_data = json.dumps(data)  
        for client in list(self.clients):
            try:
                await client.send(json_data)
                          
                self.core.logger.log(f"TTS : Sending message '{json_data}' to client '{client.remote_address}'", should_print=False)
                
            except Exception as e:
                self.clients.remove(client)
                
                self.core.logger.log(f"TTS : Failed to send data to client {client.remote_address}! Removing it from clients!",
                                     message_type=1)


    # Handles connecting clients
    async def __handler(self, websocket : websockets.WebSocketServerProtocol):
            
        self.clients.add(websocket)
        self.core.logger.log(f"TTS : Client connected: {websocket.remote_address}")
        
        try:
            # Sending resource server address
            resource_server_address = f"http://{self.core.get_option('ResourceHttpServerAddress')}:{self.core.get_option('ResourceHttpServerPort')}"
            data = {
                "TTS_Command" : "SetResourceServerAddress",
                "ResourceServerAddress" : resource_server_address
            }
            await websocket.send(json.dumps(data))
            
            # Sending image names
            data = {
                "TTS_Command" : "SetImageNames",
                "SpeakingImageName" : self.get_option("SpeakingImageName"),
                "SilentImageName" : self.get_option("SilentImageName")
            }
            await websocket.send(json.dumps(data))
            
            # Keeping connection open
            await websocket.wait_closed()
             
        finally:
            self.clients.remove(websocket)
            self.core.logger.log(f"TTS : Client disconnected: {websocket.remote_address}")


    # Asynchronous server loop
    async def __async_server_loop(self):
        
        async with websockets.serve(self.__handler, self.get_option("ip"), self.get_option("port")):
            await asyncio.Future()  # Run server loop forever
    
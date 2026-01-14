import Plugin as PluginAPI

import json
import asyncio
import websockets
import threading
from pathlib import Path

class MemeEffectsPlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
    
        # Defining default options
        self.defaultOptions : dict = {
            "ip" : "localhost",
            "port" : 8001,
            "AudioFileTypes" : [".mp3", ".wav"],
            "LogMemes" : True
        }
    
        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["ShowMeme"] = self.on_meme_event_received
        
        # Actual plugin data
        
        self.clients : set[websockets.WebSocketServerProtocol] = set()
        
        self.serverThread : threading.Thread = None
        
        self.asyncEventLoop = None
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        # Listening to audio finished playing events
        self.eventMap["AUDIO_FINISHED_PLAYING"] = []
        
        def __start_loop():
            self.asyncEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.asyncEventLoop)
            self.asyncEventLoop.run_until_complete(self.__async_server_loop())
        
        self.serverThread = threading.Thread(target=__start_loop, daemon=True)
        self.serverThread.start()


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()


    # Shows a meme and plays a sound!
    def on_meme_event_received(self, event : PluginAPI.Event):
        
        if self.options["LogMemes"]:
            
            if "MemeName" in event.data and "UserName" in event.data:
                self.core.logger.log(f"MEME EFFECTS : {event.data["UserName"]} : {event.data["MemeName"]}")
        
        if not "MemeName" in event.data or len(event.data["MemeName"]) == 0: return
        
        # Playing audio
        #self.__play_audio(event.data["MemeName"])
        
        # Sending command to ui
        if self.asyncEventLoop and self.asyncEventLoop.is_running():
            asyncio.run_coroutine_threadsafe(self.__broadcast(event.data), self.asyncEventLoop)
            
    
    # Sends data to all of the clients
    async def __broadcast(self, data : dict):
        
        json_data = json.dumps(data)  
        for client in list(self.clients):
            try:
                await client.send(json_data)
                          
                self.core.logger.log(f"MEME EFFECTS : Sending message '{json_data}' to client '{client.remote_address}'", should_print=False)
                
            except Exception as e:
                self.clients.remove(client)
                
                self.core.logger.log(f"MEME EFFECTS : Failed to send data to client {client.remote_address}! Removing it from clients!",
                                     message_type=1)


    # Handles connecting clients
    async def __handler(self, websocket : websockets.WebSocketServerProtocol):
            
        self.clients.add(websocket)
        self.core.logger.log(f"MEME EFFECTS : Client connected: {websocket.remote_address}")
        
        try:
            # Keeping connection open
            await websocket.wait_closed()
             
        finally:
            self.clients.remove(websocket)
            self.core.logger.log(f"MEME EFFECTS : Client disconnected: {websocket.remote_address}")


    # Asynchronous server loop
    async def __async_server_loop(self):
        
        async with websockets.serve(self.__handler, self.options["ip"], self.options["port"]):
            await asyncio.Future()  # Run server loop forever
        
    
    # Locates and plays the meme sound
    def __play_audio(self, meme_name : str):    
        
        audio_file = ""
        
        # Locating meme audio file
        for file_type in self.options["AudioFileTypes"]:
            path_str = self.directory + f"/Data/{meme_name}{file_type}"
            path = Path(path_str)
            if path.exists():
                audio_file = path_str
                break

        # Generating event
        event = PluginAPI.Event(
            "PLAY_AUDIO", 
            self.pluginName, 
            set(), 
            {"audio_file" : audio_file}
        )
    
        self.generate_event(event)
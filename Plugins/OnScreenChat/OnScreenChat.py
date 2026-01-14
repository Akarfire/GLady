import Plugin as PluginAPI

import json
import asyncio
import websockets
import threading

class OnScreenChatPlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
    
        # Defining default options
        self.defaultOptions : dict = {
            "ip" : "localhost",
            "port" : 8001,
            "LogMessages" : True
        }
    
        # Registering event processor function for later mapping configuration
        self.eventProcessorFunctions["ShowMessage"] = self.on_chat_message_received
        
        # Actual plugin data
        
        self.clients : set[websockets.WebSocketServerProtocol] = set() 
        self.serverThread : threading.Thread = None    
        self.asyncEventLoop = None     
        self.messageCache : list[dict] = []
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        # Control commands
        self.core.controlServer.register_control_command("OnScreenChat_DeleteLastMessage", self.delete_last_message_command)
        self.core.controlServer.register_control_command("OnScreenChat_ClearChat", self.clear_chat_command)
        
        # Starting server
        def __start_loop():
            self.asyncEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.asyncEventLoop)
            self.asyncEventLoop.run_until_complete(self.__async_server_loop())
        
        self.serverThread = threading.Thread(target=__start_loop, daemon=True)
        self.serverThread.start()


    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()


    # Example event processor function
    def on_chat_message_received(self, event : PluginAPI.Event):
        
        if self.get_option("LogMessages"):
            
            if "Message" in event.data and "UserName" in event.data:
                
                source = "Unknown Source"
                if "Source" in event.data: source = event.data["Source"]
                
                self.core.logger.log(f"ON SCREEN CHAT: {source} -> {event.data["UserName"]} : {event.data["Message"]}")
        
        if not "Message" in event.data or len(event.data["Message"]) == 0: return
        
        self.messageCache.append(event.data)
        
        if len(self.messageCache) > 100:
            self.messageCache.pop(0)
        
        if self.asyncEventLoop and self.asyncEventLoop.is_running():
            asyncio.run_coroutine_threadsafe(self.__broadcast(event.data), self.asyncEventLoop)
    
    
    # Sends data to all of the clients
    async def __broadcast(self, data : dict):
        
        json_data = json.dumps(data)
        
        for client in list(self.clients):
            try:
                await client.send(json_data)
                
                self.core.logger.log(f"ON SCREEN CHAT : Sending message '{json_data}' to client '{client.remote_address}'", should_print=False)
                
            except Exception as e:
                self.clients.remove(client)
                
                self.core.logger.log(f"ON SCREEN CHAT : Failed to send data to client {client.remote_address}! Removing it from clients!",
                                     message_type=1)


    # Handles connecting clients
    async def __handler(self, websocket : websockets.WebSocketServerProtocol):
            
        self.clients.add(websocket)
        self.core.logger.log(f"ON SCREEN CHAT : Client connected: {websocket.remote_address}")
        
        try:
            # Syncing with cached messages
            for message in self.messageCache:
                await websocket.send(json.dumps(message))
                
            await websocket.send(json.dumps({"Command" : "ScrollDown"}))
            
            # # Keeping connection open
            # await websocket.wait_closed()
            
            # Waiting for messages from the client
            async for msg in websocket:
                self.core.logger.log(f"ON SCREEN CHAT: Message from client: {msg}")

                try:
                    data = json.loads(msg)
                    print(data)
                    
                    # Processing commands
                    if "command" in data:
                        command = data["command"]
                        
                        if command == "DeleteLastMessage":
                            asyncio.run_coroutine_threadsafe(self.delete_last_message_command(), self.asyncEventLoop)
                            
                        elif command == "ClearChat":
                            asyncio.run_coroutine_threadsafe(self.clear_chat_command(), self.asyncEventLoop)
                                 
                except:
                    pass
             
        finally:
            self.clients.remove(websocket)
            self.core.logger.log(f"ON SCREEN CHAT : Client disconnected: {websocket.remote_address}")


    # Asynchronous server loop
    async def __async_server_loop(self):
        
        async with websockets.serve(self.__handler, self.get_option("ip"), self.get_option("port")):
            await asyncio.Future()  # Run server loop forever
            
    
    def delete_last_message_command(self):
        
        # Removing last message from the cache
        if self.messageCache:
            self.messageCache.pop(-1);
        
        # Sending the command to all clients (visually deleting the message)
        asyncio.run_coroutine_threadsafe(self.__broadcast({"Command" : "DeleteLastMessage"}), self.asyncEventLoop)
        
        
    def clear_chat_command(self):
        
        # Clearing message cache
        self.messageCache.clear()
        
        # Sending the command to all clients (visually deleting the messages)
        asyncio.run_coroutine_threadsafe(self.__broadcast({"Command" : "ClearChat"}), self.asyncEventLoop)
        
        
        
                    


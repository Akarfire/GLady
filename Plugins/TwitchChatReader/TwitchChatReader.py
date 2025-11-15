import Plugin as PluginAPI

from pathlib import Path
import time
from queue import Queue
import socket
import select
import threading
import re
from dataclasses import dataclass

# Data used for authenticating in Twitch API
@dataclass
class TwitchAuthData:
    server : str = ""
    port : int = 0
    nickname : str = ""
    token : str = ""
    channel : str =""
    

class TwitchChatReader(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        
        # Defining default event generation settings
        self.defaultGeneratedEventNames = {
            "Twitch_ChatMessageFetched" : ["OnChatMessageFetched"]
        }
        
        # Defining default options
        self.defaultOptions : dict = {
            "FetchFrequency" : 1,
            "AuthDataFilepath" : "$PluginDirectory$/Config/AuthData.txt",
            "TwitchServer" : "irc.chat.twitch.tv",
            "TwitchPort" : 6667,
            "AutoReconnect" : True,
        }

        self.authenticationData : TwitchAuthData = None
        self.twitchSocket : socket.socket = None
        self.chatFetchThread : threading.Thread = None
        
        self.queueAccess : threading.Lock = threading.Lock()
        self.messageQueue : Queue = Queue()
        
        # Whether the connection thread should perform the exit procedure
        self.stoppingFlag = False
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        self.read_auth_data()
        
        if self.authenticationData == None:
            return
        
        # Starting fetch thread
        self.chatFetchThread = threading.Thread(target=async_chat_fetch, args=(self,), daemon=False)
        self.chatFetchThread.start()
        

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
        self.stoppingFlag = True
        
        
     # Called every core's main loop update
    def update(self, delta_time : float):
        
        self.queueAccess.acquire()
        
        while not self.messageQueue.empty():
            
            event = PluginAPI.Event(
                self.options["Twitch_ChatMessageFetched"], 
                self.pluginName, 
                set(), 
                self.messageQueue.get())
            
            self.generate_evnet(event)
            
        self.queueAccess.release()
        
     
    # Parsses data received from Twitch API, converting it into a data dictionary   
    def parse_twitch_message(self, message):

        message_data = {"Source" : "Twitch"}

        msg = message.split("PRIVMSG")

        if len(msg) > 1:
            username, channel, message = re.search(r':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', message).groups()

            message_data["UserName"] = username
            message_data["Message"] = message

        return message_data
    
    
    # Reades authentication data file (or creates a new one)
    def read_auth_data(self):

        path = self.options["AuthDataFilepath"].replace("$PluginDirectory$", self.directory)

        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"TWITCH CHAT READER : Authentication data file at '{path}' doesn't exist, creating now")
            
            with open(path, 'w') as auth_data_file:
                auth_data_file.write(
                    "nickname: \n\
                    token: \n\
                    channel: ".replace('    ', '')
                )

        else:
            with open(path) as auth_data_file:
                lines = auth_data_file.readlines()

                self.authenticationData = TwitchAuthData()
                
                self.authenticationData.server = self.options["TwitchServer"]
                self.authenticationData.port = self.options["TwitchPort"]
                
                for line in lines:
                    
                    line = line.strip()
                    
                    if line.startswith("nickname:"):
                        self.authenticationData.nickname = line.replace('nickname:', '').replace(" ", "")
                    
                    if line.startswith("token:"):
                        self.authenticationData.token = line.replace('token:', '').replace(" ", "")
                        
                    if line.startswith("channel:"):
                        self.authenticationData.channel = line.replace('channel:', '').replace(" ", "")
        

# Checks if the socket is still connected
def is_socket_connected(sock: socket.socket) -> bool:
    
    try:
        # Use select to check for readability
        ready_to_read, _, _ = select.select([sock], [], [], 0)
        
        if ready_to_read:
            
            data = sock.recv(1, socket.MSG_PEEK)
            if not data:
                return False  # Empty -> connection closed
        
        return True
    
    except:
        return False
    
  
# Asynchronously receives data from Twitch API's socket, parses messages and puts them into the queue    
def async_chat_fetch(chat_reader : TwitchChatReader):

    while True:
        
        # Stopping logic
        if chat_reader.stoppingFlag:
            chat_reader.twitchSocket.close()
            return
        
        try:
            # Connecting to twitch api
            chat_reader.twitchSocket = socket.socket()
            chat_reader.twitchSocket.connect((chat_reader.authenticationData.server, chat_reader.authenticationData.port))
            chat_reader.twitchSocket.setblocking(False)

            chat_reader.twitchSocket.send(f"PASS {chat_reader.authenticationData.token}\n".encode('utf-8'))
            chat_reader.twitchSocket.send(f"NICK {chat_reader.authenticationData.nickname}\n".encode('utf-8'))
            chat_reader.twitchSocket.send(f"JOIN {chat_reader.authenticationData.channel}\n".encode('utf-8'))

            chat_reader.core.logger.log(f"TWITCH CHAT READER : Connected to twitch chat: {chat_reader.authenticationData.channel}")
                    
            # Message Fetch loop
            while True:
                
                if chat_reader.stoppingFlag: break
                
                try:
                    ready = select.select([chat_reader.twitchSocket], [], [], 1)
                    if ready[0]:
                        resp = chat_reader.twitchSocket.recv(2048).decode('utf-8')
                        
                        if resp.startswith('PING'):
                            chat_reader.twitchSocket.send("PONG\n".encode('utf-8'))

                        elif len(resp) > 0:
                            
                            message_data = chat_reader.parse_twitch_message(resp)
                            
                            if "Message" in message_data:
                                
                                chat_reader.queueAccess.acquire()
                                chat_reader.messageQueue.put(message_data)
                                chat_reader.queueAccess.release()
                                
                            else:
                                chat_reader.core.logger.log(f"TWITCH CHAT READER : Unusual response message: {resp}", should_print=False)
                                

                    time.sleep(1 / chat_reader.options["FetchFrequency"])
                    
                except Exception as e:
                    chat_reader.core.logger.log(f"TWITCH CHAT READER : Twitch fetch iteration : {str(e)}", message_type=1)
                    
                    if not is_socket_connected(chat_reader.twitchSocket):
                        raise e
                    
                    time.sleep(2)
                
        except Exception as e:
            chat_reader.core.logger.log(f"TWITCH CHAT READER : Twitch connection failed : {str(e)}", message_type=1)
            
            time.sleep(2)
            
            if not chat_reader.options["AutoReconnect"]:
                break
    

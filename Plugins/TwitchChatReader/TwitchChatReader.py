import Plugin as PluginAPI

import Core.Event

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
    server : str
    port : int
    nickname : str
    token : str
    channel : str
    

class TwitchChatReader(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        
        # Defining default options
        self.defaultOptions : dict = {
            "FetchFrequency" : 1,
            "AuthDataFilepath" : "$PluginDirectory$/Config/AuthData.txt",
            "TwitchServer" : "irc.chat.twitch.tv",
            "TwitchPort" : 6667,
            "AutoReconnect" : True,
            "OnMessageFetchedEventName" : "OnChatMessageFetched"
        }

        self.authenticationData : TwitchAuthData = None
        self.twitchSocket : socket.socket = None
        self.chatFetchThread : threading.Thread = None
        
        self.messageQueue : Queue = Queue()
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        self.read_auth_data()
        
        if self.authenticationData == None : return
        
        # Starting fetch thread
        self.chatFetchThread = threading.Thread(target=async_chat_fetch, args=(self,), daemon=True)
        self.chatFetchThread.start()
        

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        
     # Called every core's main loop update
    def update(self, delta_time : float):
        
        while not self.messageQueue.empty():
            
            event = Event(self.options["OnMessageFetchedEventName"], self.pluginName, set(), self.messageQueue.get())
            
            self.core.communicationBus.init_event(event)
        
     
    # Parsses data received from Twitch API, converting it into a data dictionary   
    def parse_twitch_message(self, message):

        message_data = {"Source" : "Twitch"}

        msg = message.split("PRIVMSG")

        if len(msg) > 1:
            username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', message).groups()

            message_data["UserName"] = username
            message_data["Message"] = message

        return message_data
    
    
    # Reades authentication data file (or creates a new one)
    def read_auth_data(self):

        path = self.options["AuthDataFilepath"].replace("$PluginDirectory$", self.directory)

        try:
            auth_data_file = open(path)
            found = True

        except:
            self.core.logger.log(f"TWITCH CHAT READER : Authentication data file at '{path}' doesn't exist, creating now")
            auth_data_file = open(path, 'w')
            auth_data_file.write(
                "nickname: \n\
                token: \n\
                channel: ".replace('    ', '')
            )
            auth_data_file.close()

            found = False
            pass

        if found:
            lines = auth_data_file.readlines()

            if len(lines) >= 3:
                self.authenticationData = TwitchAuthData(
                    server = self.options["TwitchServer"],
                    port = self.options["TwitchPort"],
                    nickname = lines[0].replace('nickname: ', ''),
                    token = lines[1].replace('token: ', ''),
                    channel = lines[2].replace('channel: ', '')
                )
                
                auth_data_file.close()

        else:
            self.core.logger.log("TWITCH CHAT READER : Authentication data not found or invalid!", message_type=1)
        
        
# Asynchronously receives data from Twitch API's socket, parses messages and puts them into the queue    
def async_chat_fetch(chat_reader : TwitchChatReader):

    while True:
        
        # Connecting to twitch api
        try:
            chat_reader.twitchSocket = socket.socket()
            chat_reader.twitchSocket.connect((chat_reader.authenticationData.server, chat_reader.authenticationData.port))
            chat_reader.twitchSocket.setblocking(False)

            chat_reader.twitchSocket.send(f"PASS {chat_reader.authenticationData.token}\n".encode('utf-8'))
            chat_reader.twitchSocket.send(f"NICK {chat_reader.authenticationData.nickname}\n".encode('utf-8'))
            chat_reader.twitchSocket.send(f"JOIN {chat_reader.authenticationData.channel}\n".encode('utf-8'))
  
            # Message Fetch loop
            while True:
                    ready = select.select([chat_reader.twitchSocket], [], [], 1)
                    if ready[0]:
                        resp = chat_reader.twitchSocket.recv(2048).decode('utf-8')

                        if resp.startswith('PING'):
                            chat_reader.twitchSocket.send("PONG\n".encode('utf-8'))

                        elif len(resp) > 0:
                            
                            message_data = chat_reader.parse_twitch_message(resp)
                            
                            if "Message" in message_data:
                                chat_reader.messageQueue.put(message_data)

                    time.sleep(1 / chat_reader.options["FetchFrequency"])
                
        except Exception as e:
            chat_reader.core.logger.log(f"TWITCH CHAT READER : Twitch connection failed : {str(e)}", message_type=1)
            
            if not chat_reader.options["AutoReconnect"]:
                break
    

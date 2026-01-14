import Plugin as PluginAPI

from pathlib import Path
import pytchat
import time
from queue import Queue
import requests
import threading
import re
from dataclasses import dataclass

@dataclass
class YouTubeAuthData:
    videoID = ""
    channelLink = ""
    

class YouTubeChatReader(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        
        # Defining default event generation settings
        self.defaultGeneratedEventNames = {
            "YT_ChatMessageFetched" : ["OnChatMessageFetched"]
        }
        
        # Defining default options
        self.defaultOptions : dict = {
            "FetchFrequency" : 1,
            "AuthDataFilepath" : "$PluginDirectory$/Config/AuthData.txt",
            "AutoReconnect" : True,
        }

        self.authData : YouTubeAuthData = None
        
        self.chat : pytchat.LiveChat = None

        self.chatFetchThread : threading.Thread = None
        
        self.queueAccess : threading.Lock = threading.Lock()
        self.messageQueue : Queue = Queue()
        
        # Used to determine whether this connection is a first-connect or a re-connect
        self.firstConnection = True
        

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()
        
        # Control commands
        self.core.controlServer.register_control_command("YTChat_Reconnect", self.command_reconnect)
        
        # Initializiation
        
        self.read_auth_data()
        
        if self.authData is None : return
        
        # Connecting to yt chat
        # self.connect_to_chat()
        
        # Starting fetch thread
        self.chatFetchThread = threading.Thread(target=async_chat_fetch, args=(self,), daemon=True)
        self.chatFetchThread.start()
        

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
         
        self.chat.terminate()
        
        
     # Called every core's main loop update
    def update(self, delta_time : float):
        
        # Maintaining chat connection
        if self.get_option("AutoReconnect") or self.firstConnection:
            if self.chat is None or not self.chat.is_alive():
                self.firstConnection = False
                try:
                    self.connect_to_chat() 
                    
                except Exception as e:
                    self.core.logger.log(f"YOUTUBE CHAT READER : Failed to connect to YT chat: {str(e)}", message_type=1)
            
        # Processing queed messages
        self.queueAccess.acquire()
        
        while not self.messageQueue.empty():
            
            event = PluginAPI.Event(
                "YT_ChatMessageFetched", 
                self.pluginName, 
                set(), 
                self.messageQueue.get())
            
            self.generate_event(event)
            
        self.queueAccess.release()
    
    
    # Creates pytchat chat, tries to connecto to yt chat and puts created chat into self.chat
    def connect_to_chat(self):
                
        if self.authData is None: return        
        
        # Determine video id
        video_id = self.authData.videoID
        
        if video_id == "":

            # Auto fetch video id using /live redirect
            live_url = self.authData.channelLink + "/live"
            response = requests.get(live_url, allow_redirects=True)
            print(live_url)
            
            match = re.search(r"v=([a-zA-Z0-9_-]{11})", response.url)

            if match:
                video_id = match.group(1)
                self.core.logger.log(f"YOUTUBE CHAT READER : Found live stream at '{response.url}'")
                
            else:
                self.core.logger.log(f"YOUTUBE CHAT READER : No live stream found at '{response.url}'", message_type=1)
        
        # Connecting to chat
        self.chat = pytchat.create(video_id=video_id)
        
        self.core.logger.log(f"YOUTUBE CHAT READER : Connected to YT chat, video id: {video_id}")
        
     
    # Parsses data received from Twitch API, converting it into a data dictionary   
    def parse_youtube_message(self, message):

        message_data = {"Source" : "YouTube"}

        message_data["UserName"] = message.author.name.replace("@", "")
        message_data["Message"] = message.message

        return message_data
    
    
    # Reades authentication data file (or creates a new one)
    def read_auth_data(self):

        path = self.get_option("AuthDataFilepath").replace("$PluginDirectory$", self.directory)
        
        path_ = Path(path)
        if not path_.exists():
            self.core.logger.log(f"YOUTUBE CHAT READER : Authentication data file at '{path}' doesn't exist, creating now")
            
            with open(path, "w") as auth_data_file:
                auth_data_file.write(
                    "# If video_id is left black, automatic id fetching will be attempted using channel_link\n\nvideo_id: \nchannel_link: \n"
                )

        else:
            with open(path) as auth_data_file:
                lines = auth_data_file.readlines()

                self.authData = YouTubeAuthData()
                
                for line in lines:
                    
                    line = line.strip()
                    
                    if line.startswith("video_id:"):
                        self.authData.videoID = line.replace('video_id:', '').replace(' ', '')
                        
                    if line.startswith("channel_link:"):
                        self.authData.channelLink = line.replace('channel_link:', '').replace(' ', '')
            
    
    def command_reconnect(self, data : dict):
        
        if "video_id" in data:
            self.authData.videoID = data["video_id"]
            
        self.connect_to_chat()
        
        
# Asynchronously receives data from Twitch API's socket, parses messages and puts them into the queue    
def async_chat_fetch(chat_reader : YouTubeChatReader):

    while True:
        try:
            
            # Message Fetch loop
            while chat_reader.chat != None and chat_reader.chat.is_alive():
                try:
                    
                    for message in chat_reader.chat.get().sync_items():
                        message_data = chat_reader.parse_youtube_message(message)
                            
                        if "Message" in message_data:
                            
                            chat_reader.queueAccess.acquire()
                            chat_reader.messageQueue.put(message_data)
                            chat_reader.queueAccess.release()
            
                    time.sleep(1 / chat_reader.options["FetchFrequency"])
                    
                except Exception as e:
                    chat_reader.core.logger.log(f"YOUTUBE CHAT READER : Fetching failed : {str(e)}", message_type=1)
                    
                    if not chat_reader.chat.is_alive():
                        raise e 
                
        except Exception as e:
            chat_reader.core.logger.log(f"YOUTUBE CHAT READER : Connection failed : {str(e)}", message_type=1)
            
            time.sleep(2)
             
            if not chat_reader.options["AutoReconnect"]:
                break
    

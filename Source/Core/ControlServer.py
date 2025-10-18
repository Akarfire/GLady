import socket
import threading
import queue

from Core.Event import Event

class CommandMessage:
    def __init__(self):
        self.messageType : str = ""
        self.senderAddress : str = ""
        self.data : dict = {}

#
class ControlServer:

    def __init__(self, core):

        self.core = core

        # Connection info
        self.host = "127.0.0.1"
        self.port = 22222

        self.serverSocket = None

        # Command queue
        self.commandQueue = queue.Queue()
        
        self.queueAccessLock : threading.Lock = threading.Lock()

        # Server loop thread
        self.asyncLoopThread = threading.Thread(target=async_server_loop, args=(self,), daemon=True)
        self.asyncLoopThread.start()
        
        self.client_threads : dict[str, threading.Thread] = {}

        # Control Commands registry
        self.commandsMap = dict()

        self.core.logger.log("Control Server initialized")


    def register_client(self, connect, address):
        
        self.core.logger.log(f"Control Server: control client registered: {address}")
        
        thread = threading.Thread(target=async_receiving_loop, args=(self, connect, address,), daemon=True)
        self.client_threads[address] = thread;
        
        thread.start()


    def client_connection_closed(self, address):
        
        if address in self.client_threads:
            self.client_threads[address]
    

    def update(self, delta_time : float):

        # Processing command queue
        while not self.commandQueue.empty():
            command_message : CommandMessage = self.commandQueue.get()

            # Event commands
            if command_message.messageType == "E":
                if "Event" in command_message.data:
                    self.core.communicationBus.init_event(command_message.data["Event"])
                    
            # General Commands
            if command_message.messageType == "C":
                if "CommandName" in command_message.data and command_message.data["CommandName"] in self.commandsMap:
                    
                    data = dict()
                    if "Data" in command_message.data:
                        data = command_message.data["Data"]
                    
                    self.commandsMap[command_message.data["CommandName"]](data)
    
    
    # Registers a control command, 
    # Command_function is a function that will be called when this control command is received
    # Command function will receive a data dictionary as it's argument
    def register_control_command(self, command_name : str, command_function):
        
        if command_name in self.commandsMap:
            self.core.logger.log(f"Control command '{command_name}' already exists!", message_type = 1)
            return
            
        self.commandsMap[command_name] = command_function
    

    # Parses received string message and attempts constructing a CommandMessage out of it
    # Returns tuple< IsMessageValid, CommandMessage >
    def parse_command_message(self, message : str, sender : str):
        result = CommandMessage()
        result.senderAddress = sender

        # Message examples:
        # E : EventName, /tag_1, /tag_2, ... data_name_1 = data_1, data_name_2 = data_2, ...
        # C : CommandName, data_name_1 = data_1, data_name_2 = data_2, ...

        if not ':' in message: return False, result

        message_type, tail = message.split(':')
        message_type = message_type.replace(' ', '')

        if not message_type in "C E": return False, result

        result.messageType = message_type

        # Processing C (Command) type messages
        if message_type == 'C':
            tail += ','
            segments = tail.split(',')

            for seg in segments:
                
                # Skip empty segments
                if seg.count(' ') == len(seg): continue
                
                # Data entries
                if '=' in seg:
                    data_name, data_value = seg.split('=')

                    if not "Data" in result.data:
                        result.data["Data"] = dict()

                    result.data["Data"][data_name.replace(' ', '')] = eval(data_value)

                # CommandName
                elif not "CommandName" in result.data:
                    
                    # Checking if the command is valid
                    if not seg.replace(' ', '') in self.commandsMap: return False, result
                    
                    result.data["CommandName"] = seg.replace(' ', '')      

                else: return False, result

        # Processing E (Event) type messages
        elif message_type == "E":
            tail += ','
            segments = tail.split(',')
            
            event = Event()

            for seg in segments:
                
                # Skip empty segments
                if seg.count(' ') == len(seg): continue
                
                # Tags
                if seg.startswith('/'):
                    event.tags.add(seg.replace('/', ''))

                # Data entries
                elif '=' in seg:
                    data_name, data_value = seg.split('=')

                    event.data[data_name.replace(' ', '')] = eval(data_value)

                elif event.eventName == "":
                    event.eventName = seg.replace(' ', '')

                else: return False, result

            result.data["Event"] = event

        return True, result



# Contains main server loop: establishes connections with clients
def async_server_loop(server : ControlServer):

    # Establishing connection (trying until success)
    while True:

        try:
            server.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.serverSocket.bind((server.host, server.port))
            server.serverSocket.listen()

            connect : socket.socket = None
            connect, address = server.serverSocket.accept()
            
            server.register_client(connect, address)               


        except Exception as e:
            server.core.logger.log(f"CONTROL SERVER: {str(e)}!", message_type = 1)
            

# Contains receiving loop: receives data from a single client
def async_receiving_loop(server : ControlServer, connect : socket.socket, address):
    
     # Receiving loop
    while True:
        
        try:
            data = connect.recv(1024).decode("utf-8")

            if not data:
                server.core.logger.log(f"Control Server connection closed: {address}")
                break

            server.core.logger.log(f"Control Server received message: '{data}'")

            valid, command_message = server.parse_command_message(data, address)

            if valid:
                
                # Critical section - queue access
                server.queueAccessLock.acquire()
                # {
                server.commandQueue.put(command_message)
                # }
                server.queueAccessLock.release()
                
                connect.sendall(b"Control Server : Command processed!")
                
            else:
                connect.sendall(b"Control Server : Invalid Command!")
                
        except Exception as e:
            server.core.logger.log(f"CONTROL SERVER - Client Thread {address}: {str(e)}!", message_type = 1)
            break
import socket

host = "127.0.0.1"
port = 22222

print("Welcome to GLady Console Control Panel!")
print("---------------------------------------")
print('''
      Command syntax:
        E : EventName | /tag_1 | /tag_2 | ... data_name_1 = data_1 | data_name_2 = data_2 | ...
        C : CommandName | data_name_1 = data_1 | data_name_2 = data_2 | ...
        R : RequestName | data_name_1 = data_1 | data_name_2 = data_2 | ...
      
      Example Commands:
         C : ReloadConfig
         E: OnChatMessageFetched | UserName="AkarFire" | Message="Hey There!"
         R : Requests
         R : Commands
      ''')
print("---------------------------------------")

cached_command : str = ""

while True:
    
    try:
        controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        controlSocket.connect((host, port))
        
        print(f"Connected to GLady control server!")
        
        # Main loop
        while True:
        
            if (cached_command == ""):
                cached_command = input()
            
            if len(cached_command) == 0:
                continue

            controlSocket.sendall(cached_command.encode("utf-8"))
            
            response = controlSocket.recv(1024)
            
            print(response.decode("utf-8"))
            
            cached_command = ""
            
    except Exception as e:
        print(f"CONNECTION ERROR: {str(e)}\n")

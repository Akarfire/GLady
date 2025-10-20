import socket

host = "127.0.0.1"
port = 22222

while True:
    
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controlSocket.connect((host, port))
    
    print(f"Connected to GLady control server!")
    
    # Main loop
    while True:
       
        command = input()

        controlSocket.sendall(command.encode("utf-8"))
        
        response = controlSocket.recv(1024)
        
        print(response.decode("utf-8"))

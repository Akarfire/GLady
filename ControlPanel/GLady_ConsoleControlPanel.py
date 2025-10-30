import socket

host = "127.0.0.1"
port = 22222

while True:
    
    try:
        controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        controlSocket.connect((host, port))
        
        print(f"Connected to GLady control server!")
        
        # Main loop
        while True:
        
            command = input()
            
            if len(command) == 0:
                continue

            controlSocket.sendall(command.encode("utf-8"))
            
            response = controlSocket.recv(1024)
            
            print(response.decode("utf-8"))
            
    except Exception as e:
        print(f"CONNECTION ERROR: {str(e)}\n")

import http.server
import socketserver
import threading

DIRECTORY = "./"

# Hosts an http server with user defined resource files 
class ResourceHttpServer:

    def __init__(self, core):
        self.core = core
        
        self.address = "localhost"
        self.port = 8000
        
        self.isRunning = False
        self.httpdServer : socketserver.TCPServer = None
        self.serverThread : threading.Thread = None


    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)
        
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header('Cache-Control', 'no-store, must-revalidate')
            self.send_header('Expires', '0')
            super().end_headers()
        
        def copyfile(self, source, outputfile):
            try:
                super().copyfile(source, outputfile)
            except (ConnectionAbortedError, BrokenPipeError):
                pass
        
        # Remove default logging
        def log_message(self, format, *args):
            pass


    def __http_server(self):     
        with socketserver.ThreadingTCPServer((self.address, self.port), self.Handler) as httpd:
            self.core.logger.log(f"RESOURCE HTTP SERVER : HTTP server running at http://{self.address}:{self.port}")
            self.httpdServer = httpd
            httpd.serve_forever()
            
        self.httpdServer = None
        
    def __shutdown_server(self):
        self.isRunning = False
        if not self.httpdServer is None:
            self.httpdServer.shutdown()
            
        if not self.serverThread is None:
            self.serverThread.join()
    
    def start_server(self):
        
        self.address = self.core.get_option("ResourceHttpServerAddress")
        self.port = self.core.get_option("ResourceHttpServerPort")
        
        threading.Thread(target=self.__http_server, daemon=True).start()
        self.isRunning = True
            
    def reload_config(self):   
        new_address = self.core.get_option("ResourceHttpServerAddress")
        new_port = self.core.get_option("ResourceHttpServerPort")
        
        if (self.address != new_address or self.port != new_port) and self.isRunning:
            self.address = new_address
            self.port = new_port
            self.__shutdown_server()
            self.__start_server()
                
                
        

        
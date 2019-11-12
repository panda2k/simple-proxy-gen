import json

class Proxy:
    ip_address = None
    username = None
    password = None
    port = None

    def __init__(self, ip_address, port, username, password):
       self.ip_address = ip_address
       self.username = username
       self.password = password
       self.port = port 
    
    def to_string(self):
        return self.ip_address + ':' + self.port + ':' + self.username + ':' + self.password
    
    def write_to_json(self, file_name):
        return

class Server:
    ip_address = None
    username = None
    password = None
    provider = None

    def __init__(self, ip_address, username, password, provider):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.provider = provider
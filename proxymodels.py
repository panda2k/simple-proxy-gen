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

class AzureServer:
    ip_address = None
    username = None
    password = None
    disk_name = None
    ip_name = None
    nic_name = None
    vm_name = None
    resource_group_name = None

    def __init__(self, ip_address, username, password, disk_name, ip_name, nic_name, vm_name, resource_group_name):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.disk_name = disk_name
        self.ip_name = ip_name
        self.nic_name = nic_name
        self.vm_name = vm_name
        self.resource_group_name = resource_group_name
    
    def write_to_json(self, file_name):
        server = {
            'vm_name': self.vm_name,
            'resource_group_name': self.resource_group_name,
            'username': self.username,
            'password': self.password,
            'ip_address': self.ip_address,
            'ip_name': self.ip_name,
            'nic_name': self.nic_name,
            'disk_name': self.disk_name
        }
        with open(file_name, 'w') as json_file:
            json.dump(server, json_file)

class Server100TB:
    location_id = None
    server_id = None
    label = None
    username = None
    password = None
    ip_address = None

    def __init__(self, location_id, server_id, label, ip_address, username, password):
        self.location_id = location_id
        self.server_id = server_id
        self.label = label
        self.username = username
        self.password = password
        self.ip_address = ip_address
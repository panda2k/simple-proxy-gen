import json

class AWSProxy:
    ip_address = None
    username = None
    password = None
    port = None
    spot_fleet_id = None

    def __init__(self, ip_address, port, username, password, spot_fleet_id):
       self.ip_address = ip_address
       self.username = username
       self.password = password
       self.port = port 
       self.spot_fleet_id = spot_fleet_id
    
    def to_string(self):
        return self.ip_address + ':' + str(self.port) + ':' + self.username + ':' + self.password
    
    def write_to_json(self, file_location):
        proxy = {
            'spot_fleet_id': self.spot_fleet_id, 
            'ip_address': self.ip_address,
            'proxy_username': self.username,
            'proxy_password': self.password,
            'proxy_port': self.port
        }
        json_file = open(file_location, 'a')
        json.dump(proxy, json_file)
        json_file.close()

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
    
    def write_to_json(self, file_location):
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
        json_file = open(file_location, 'a')
        json.dump(server, json_file)
        json_file.close()

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
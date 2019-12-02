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
    
    def to_dict(self):
        proxy = {
            'spot_fleet_id': self.spot_fleet_id, 
            'ip_address': self.ip_address,
            'proxy_username': self.username,
            'proxy_password': self.password,
            'proxy_port': self.port
        }
        return proxy

class AzureServer:
    ip_address = None
    proxy_username = None
    proxy_password = None
    proxy_port = None
    disk_name = None
    ip_name = None
    nic_name = None
    vm_name = None
    resource_group_name = None

    def __init__(self, ip_address, proxy_username, proxy_password, proxy_port, disk_name, ip_name, nic_name, vm_name, resource_group_name):
        self.ip_address = ip_address
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_port = proxy_port
        self.disk_name = disk_name
        self.ip_name = ip_name
        self.nic_name = nic_name
        self.vm_name = vm_name
        self.resource_group_name = resource_group_name
    
    def to_dict(self):
        server = {
            'vm_name': self.vm_name,
            'resource_group_name': self.resource_group_name,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'proxy_port': self.proxy_port,
            'ip_address': self.ip_address,
            'ip_name': self.ip_name,
            'nic_name': self.nic_name,
            'disk_name': self.disk_name
        }
        return server
    
    def to_string(self):
        return self.ip_address + ':' + str(self.proxy_port) + ':' + self.proxy_username + ':' + self.proxy_password


class Server100TB:
    location_id = None
    server_id = None
    label = None
    username = None
    password = None
    ip_address = None
    proxy_username = None
    proxy_password = None
    proxy_port = None

    def __init__(self, location_id, server_id, label, ip_address, username, password, proxy_username, proxy_password, proxy_port):
        self.location_id = location_id
        self.server_id = server_id
        self.label = label
        self.username = username
        self.password = password
        self.ip_address = ip_address
        self.proxy_password = proxy_password
        self.proxy_username = proxy_username
        self.proxy_port = proxy_port

    def to_dict(self):
        server = {
            'location_id': self.location_id,
            'server_id': self.server_id,
            'label': self.label,
            'username': self.username,
            'password': self.password,
            'ip_address': self.ip_address,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'proxy_port': self.proxy_port
        }
        return server
    
    def to_string(self):
        return self.ip_address + ':' + str(self.proxy_port) + ':' + self.proxy_username + ':' + self.proxy_password

class UpcloudServer:
    uuid = None
    ip_address = None
    proxy_username = None
    proxy_password = None
    proxy_port = None

    def __init__(self, uuid, ip_address, proxy_username, proxy_password, proxy_port):
        self.uuid = uuid
        self.ip_address = ip_address
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_port = proxy_port
    
    def to_dict(self):
        server = {
            'uuid': self.uuid,
            'ip_address': self.ip_address,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'proxy_port': self.proxy_port
        }
        return server
    
    def to_string(self):
        return self.ip_address + ':' + str(self.proxy_port) + ':' + self.proxy_username + ':' + self.proxy_password

class LinodeServer:
    server_id = None
    ip_address = None
    proxy_username = None
    proxy_password = None
    proxy_port = None

    def __init__(self, server_id, ip_address, proxy_username, proxy_password, proxy_port):
        self.server_id = server_id
        self.ip_address = ip_address
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_port = proxy_port
    
    def to_dict(self):
        server = {
            'server_id': self.server_id,
            'ip_address': self.ip_address,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'proxy_port': self.proxy_port
        }
        return server
    
    def to_string(self):
        return self.ip_address + ':' + str(self.proxy_port) + ':' + self.proxy_username + ':' + self.proxy_password

class VpsieServer:
    server_id = None
    ip_address = None
    proxy_username = None
    proxy_password = None
    proxy_port = None
    username = None
    password = None

    def __init__(self, server_id, username, password, ip_address, proxy_username, proxy_password, proxy_port):
        self.server_id = server_id
        self.ip_address = ip_address
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_port = proxy_port
        self.username = username
        self.password = password

    def to_dict(self):
        server = {
            'server_id': self.server_id,
            'ip_address': self.ip_address,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'proxy_port': self.proxy_port
        }
        
        return server
    
    def to_string(self):
        return self.ip_address + ':' + str(self.proxy_port) + ':' + self.proxy_username + ':' + self.proxy_password
    

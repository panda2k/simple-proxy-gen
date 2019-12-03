import os
import base64
import requests
import time
import json
import proxymodels

class VultrProxyGen:
    access_token = None
    base_url = 'https://api.vultr.com'
    auth_header = {
        'API-Key': None
    }

    def __init__(self):
        self.access_token = os.environ.get('VULTR_ACCESS_TOKEN')
        self.auth_header['API-Key'] = self.access_token

    def create_server(self, location_id, startup_script_id):
        server = {
            'DCID': location_id,
            'VPSPLANID': 201,
            'OSID': 215, # ubuntu 16.04
            'SCRIPTID': startup_script_id
        }
        response = json.loads(requests.post(self.base_url + '/v1/server/create', server, headers=self.auth_header).text)

        return response['SUBID']
    
    def create_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password, startup_script_name):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)

        startup_script_params = {
            'name': startup_script_name,
            'script': startup_script
        }
        response = json.loads(requests.post(self.base_url + '/v1/startupscript/create', startup_script_params, headers=self.auth_header).text)

        return response['SCRIPTID']
    
    def delete_server(self, sub_id):
        request = {
            'SUBID': sub_id
        }
        response = requests.post(self.base_url + '/v1/server/destroy', request, headers=self.auth_header)
        
        return response.status_code
    
    def delete_script(self, script_id):
        request = {
            'SCRIPTID': script_id
        }
        response = requests.post(self.base_url + '/v1/startupscript/destroy', request, headers=self.auth_header)

    def get_server_ip_address(self, sub_id):
        ip = json.loads(requests.get(self.base_url + '/v1/server/list_ipv4?SUBID=' + sub_id, headers=self.auth_header).text)[sub_id][0]['ip']
        while(ip == '0.0.0.0'):
            time.sleep(5)
            ip = json.loads(requests.get(self.base_url + '/v1/server/list_ipv4?SUBID=' + sub_id, headers=self.auth_header).text)[sub_id][0]['ip']

        return ip
    
    def create_proxies(self, location_id, proxy_count, proxy_username, proxy_password):
        servers = []
        server_ids = []
        script_id = self.create_startup_script('proxystartupscript', 'username', proxy_username, 'password', proxy_password, 'proxysetup-' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        #script_id = 651517
        for x in range(proxy_count):
            server_ids.append(self.create_server(location_id, script_id))
        for x in server_ids:
            ip_address = self.get_server_ip_address(x)
            servers.append(proxymodels.VultrServer(x, ip_address, proxy_username, proxy_password, 80, script_id))
        
        return servers

def main():
    proxy_gen = VultrProxyGen()
    servers = proxy_gen.create_proxies(4, 5, 'tester', 'passtest')
    for x in servers:
        print(x.to_string())
    input('ready to delete?')
    proxy_gen.delete_script(servers[0].startup_script_id)
    for x in servers:
        proxy_gen.delete_server(x.server_id)

if __name__ == "__main__":
    main()

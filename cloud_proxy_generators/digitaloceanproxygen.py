import requests
import json
import os
import haikunator
import time

from . import proxymodels

class DigitalOceanProxyGen:
    access_key = None
    request_headers = {
        "Content-Type": "application/json",
        "Authorization": None
    }
    base_url = 'https://api.digitalocean.com'

    def __init__(self):
        self.access_key = os.environ.get('DIGITAL_OCEAN_ACCESS_TOKEN')
        self.request_headers['Authorization'] = f"Bearer {self.access_key}"
    
    def create_vm(self, region, startup_script):
        name_gen = haikunator.Haikunator()
        server = {
            "name": name_gen.haikunate(),
            "region": region,
            "size": "1gb",
            "image": 49549315,
            "user_data": startup_script,
        }
        response = json.loads(requests.post(self.base_url + '/v2/droplets', json.dumps(server), headers=self.request_headers).text)

        return response['droplet']['id']

    def get_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)

        return startup_script
    
    def get_vm_ip_address(self, vm_id):
        response = json.loads(requests.get(self.base_url + f'/v2/droplets/{vm_id}', headers=self.request_headers).text)
        while(True):
            try:
                ip = response['droplet']['networks']['v4'][0]['ip_address']
                break
            except IndexError as error:
                time.sleep(5)
                response = json.loads(requests.get(self.base_url + f'/v2/droplets/{vm_id}', headers=self.request_headers).text)

        return ip

    def delete_vm(self, vm_id):
        response = requests.delete(self.base_url + f'/v2/droplets/{vm_id}', headers=self.request_headers)

        return response
    
    def create_proxies(self, region, proxy_count, proxy_username, proxy_password):
        server_ids = []
        servers = []
        startup_script = self.get_startup_script('proxystartupscript', 'username', proxy_username, 'password', proxy_password)
        for x in range(proxy_count):
            server_ids.append(self.create_vm(region, startup_script))
        for x in server_ids:
            ip = self.get_vm_ip_address(x)
            servers.append(proxymodels.DigitalOceanServer(x, ip, proxy_username, proxy_password, 80))
        
        return servers

def main():
    proxy_gen = DigitalOceanProxyGen()
    servers = proxy_gen.create_proxies('sfo2', 3, 'testuser', 'testpass')
    for x in servers:
        print(x.to_string())
    input("ready to delete?")
    for x in servers:
        proxy_gen.delete_vm(x.server_id)

if __name__ == "__main__":
    main()
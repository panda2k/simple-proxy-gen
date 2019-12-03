import os
import requests
import json
import proxymodels
import time
from requests.auth import HTTPBasicAuth
import haikunator

class UpcloudProxyGen:
    api_authentication = None
    base_url = 'https://api.upcloud.com/1.3'

    def __init__(self):
        api_username = os.environ.get('UPCLOUD_API_USERNAME')
        api_password = os.environ.get('UPCLOUD_API_PASSWORD')
        self.api_authentication = HTTPBasicAuth(api_username, api_password)

    def create_server(self, zone, startup_script_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password):
        name_generator = haikunator.Haikunator()
        title = name_generator.haikunate()
        server = {
            "server": {
                "zone": zone,
                "title": title,
                "hostname": title,
                "plan": "1xCPU-1GB", # smallest plan
                "storage_devices": {
                    "storage_device": [
                        {
                            "action": "clone",
                            "storage": "01000000-0000-4000-8000-000030060200", # ubuntu 16.04 lts
                            "title": title + "-disk", 
                            "size": 25,
                            "tier": "maxiops"
                        }
                    ]
                },
                "user_data": self.get_startup_script(startup_script_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password)
            }
        }
        response = json.loads(requests.post(self.base_url + '/server', json.dumps(server), auth=self.api_authentication, headers={"content-type": "application/json"}).text)

        return proxymodels.UpcloudServer(response['server']['uuid'], response['server']['ip_addresses']['ip_address'][1]['address'], proxy_username, proxy_password, 80)

    def get_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)
        startup_script = startup_script.encode()
        startup_script = startup_script.decode("utf-8")

        return startup_script

    def shutdown_server(self, server_uuid):
        request = {
            "stop_server": {
                "stop_type": "hard",
                "timeout": "60"
            }
        }
        response = requests.post(self.base_url + f'/server/{server_uuid}/stop', json.dumps(request), auth=self.api_authentication, headers={"content-type": "application/json"})

    def wait_for_server_shutdown(self, server_uuid):
        while(json.loads(requests.get(self.base_url + f'/server/{server_uuid}', auth=self.api_authentication).text)['server']['state'] != 'stopped'):
            time.sleep(10)
    
    def delete_server(self, server_uuid):
        delete_result = requests.delete(self.base_url + f'/server/{server_uuid}/?storages=1', auth=self.api_authentication)

    def create_proxies(self, zone, proxy_count, proxy_username, proxy_password):
        servers = []
        for x in range(proxy_count):
            servers.append(self.create_server(zone, 'proxystartupscript', 'username', proxy_username, 'password', proxy_password))
        
        return servers

def main():
    proxy_gen = UpcloudProxyGen()
    #servers = proxy_gen.create_proxies("us-chi1", 1, 'pwbo', 'pwno')
    #input('type anything to delete servers')
    #for x in servers:
    #proxy_gen.shutdown_server('0066f236-84d4-4b28-bba8-aeb11c897e58')
    proxy_gen.wait_for_server_shutdown('0066f236-84d4-4b28-bba8-aeb11c897e58')
    proxy_gen.delete_server('0066f236-84d4-4b28-bba8-aeb11c897e58')

if __name__ == "__main__":
    main()

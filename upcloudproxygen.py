import os
import requests
import json
import proxymodels
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
        response = requests.post(self.base_url + '/server', json.dumps(server), auth=self.api_authentication, headers={"content-type": "application/json"})

        return proxymodels.UpcloudServer()

    def get_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)
        startup_script = startup_script.encode()
        startup_script = startup_script.decode("utf-8")

        return startup_script

    def delete_server(self, server_uuid):
        delete_result = requests.delete(self.base_url + f'/server/{server_uuid}/?storages=1', auth=self.api_authentication)

def main():
    proxy_gen = UpcloudProxyGen()
    #proxy_gen.create_server('us-chi1', 'proxystartupscript', 'username', 'testuser', 'password', 'testpassword')
    proxy_gen.delete_server('00354591-4517-4bce-92f7-e300cbf2151c')

if __name__ == "__main__":
    main()

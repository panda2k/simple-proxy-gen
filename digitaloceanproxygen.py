import requests
import json
import os
import haikunator

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
    
    def create_vm(self, region, startup_script_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password):
        name_gen = haikunator.Haikunator()
        server = {
            "name": name_gen.haikunate(),
            "region": region,
            "size": "1gb",
            "image": 49549315,
            "user_data": self.get_startup_script(startup_script_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password),
        }
        response = json.loads(requests.post(self.base_url + '/v2/droplets', json.dumps(server), headers=self.request_headers).text)

        return 

    def get_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)

        return startup_script

def main():
    proxy_gen = DigitalOceanProxyGen()
    proxy_gen.create_vm('sfo2', 'proxystartupscript', 'username', 'testuser', 'password', 'testpass')

if __name__ == "__main__":
    main()
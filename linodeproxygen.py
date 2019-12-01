import os
import requests
import json
import haikunator
import proxymodels

class LinodeProxygen():
    access_token = None
    base_url = 'https://api.linode.com/v4'

    def __init__(self):
        self.access_token = os.environ.get('LINODE_ACCESS_TOKEN')
    
    def create_server(self, location, proxy_username, proxy_password):
        name_gen = haikunator.Haikunator()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "content-type": "application/json"
        }
        server = {
            "region": location,
            "type": "g6-nanode-1",
            "backups_enabled": False,
            "booted": True,
            "image": "linode/ubuntu16.04lts",
            "root_pass": name_gen.haikunate()
            #"stackscript_id": ''
        }
        response = json.loads(requests.post(self.base_url + '/linode/instances', json.dumps(server), headers=headers).text)

        return proxymodels.LinodeServer(response['id'], response['ipv4'][0], proxy_username, proxy_password, 80)

    def delete_server(self, server_id):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.delete(self.base_url + f'/linode/instances/{server_id}', headers=headers)    
    
    def create_stack_script(self, startup_script, stack_script_name):
        headers={
            "Authorization": f"Bearer {self.access_token}", 
            "content-type": "application/json"
        }
        request = {
            "images":[
                "linode/ubuntu16.04lts"
            ],
            "label": stack_script_name,
            "description": "installs a squid proxy server",
            "is_public": False,
            "script": startup_script 
        }
        response = requests.post(self.base_url + '/linode/stackscripts', json.dumps(request), headers=headers)

    def get_stack_script_id(self, stack_script_name):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        print(headers)
        response = requests.get(self.base_url + '/linode/stackscripts', headers=headers)
        print(response.text)
        print(response)
        #print(json.loads(response.text))
        #for x in json.loads(response.text)['data']:
        #    print(x['label'])

    def get_startup_script(self, file_name, proxy_username_identifier,  proxy_username, proxy_password_identifier, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)

        return startup_script

def main():
    proxy_gen = LinodeProxygen()
    startup_script = proxy_gen.get_startup_script('proxystartupscript', 'username', 'tester', 'password', 'testpass')
    #proxy_gen.create_stack_script(startup_script, 'proxysetup')
    #print(proxy_gen.get_stack_script_id('proxysetup'))
    proxy_gen.create_server("us-east")

if __name__ == "__main__":
    main()
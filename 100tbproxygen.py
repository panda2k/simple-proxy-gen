import requests
import json
import os
import time
import haikunator
from fabric import Connection
from fabric import Config
from invoke.exceptions import UnexpectedExit
import proxymodels


class ProxyGen100TB:
    api_key = None
    def __init__(self, api_key):
        self.api_key = api_key

    def delete_vms(self, servers):
        for x in servers:
            request_url = f'https://cp.100tb.com/rest-api/vps.json/servers/{x.server_id}'
            delete_result = requests.delete(request_url)
            print(delete_result)

    def setup_squid(self, servers, startup_script_file_location):
        for x in servers:
            sudo_config = Config(overrides={'sudo': {'password': x.password}})
            server_connection = Connection(host=x.ip_address, user=x.username, connect_kwargs={"password": x.password}, config=sudo_config)
            file_transfer_result = server_connection.put(startup_script_file_location, remote='/usr/bin/')
            server_connection.sudo('chmod +x /usr/bin/' + startup_script_file_location)
            file_transfer_result = server_connection.put('squidsetup.service', remote='/etc/systemd/system/')
            server_connection.sudo('systemctl enable squidsetup')
            try:
                server_connection.sudo('reboot')
            except UnexpectedExit as e:
                print("Caught error while rebooting machine")
    
    def create_vm(self, location_id):
        name_generator = haikunator.Haikunator()
        vm_name = name_generator.haikunate()
        password = name_generator.haikunate()
        request_url = f'https://cp.100tb.com/rest-api/vps.json?api_key={self.api_key}'

        request_params = {
            'planId': 2698, # v1-19 server
            'locationId': location_id, # a number 2-20 corresponding to a location
            'templateId': self.get_template_id(location_id),
            'label': vm_name,
            'hostname': vm_name,
            'password': password,
            'billHourly': True
        }
        creation_result = json.loads(requests.post(request_url, request_params).text)
        print(creation_result)

        return proxymodels.Server100TB(location_id, creation_result['server'], vm_name, 'root', password)
    
    def get_vm_status(self, vm_id):
        request_url = f'https://cp.100tb.com/rest-api/vps.json/servers/{vm_id}/status/?api_key={self.api_key}'
        vm_status = json.loads(requests.get(request_url).text)

        return vm_status['status']


    def get_template_id(self, location_id):
        # gets the ubuntu x64 plan id for the location
        request_url = f"https://cp.100tb.com/rest-api/vps.json/templates/{location_id}?api_key={self.api_key}"
        plans = json.loads(requests.get(request_url).text)
        for x in plans:
            if(x['label'] == 'Ubuntu 16.04 x64'):
                return x['id']
    
    def get_new_startup_script(self, old_script_location, new_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password):
        startup_script = open(old_script_location, 'r')
        startup_script_content = startup_script.read()
        startup_script_content = startup_script_content.replace(proxy_username_identifier, proxy_username)
        startup_script_content = startup_script_content.replace(proxy_password_identifier, proxy_password)

        new_startup_script = open(new_location, 'w')
        new_startup_script.write(startup_script_content)
        
        new_startup_script.close()
        startup_script.close()

    def create_proxies(self, proxy_count, location_id):
        proxy_list = []
        servers = []
        name_generator = haikunator.Haikunator()
        proxy_username = name_generator.haikunate()
        proxy_password = name_generator.haikunate()

        for x in range(proxy_count):
            servers.append(self.create_vm(location_id))
            proxy_list.append(servers[x].ip_address + f":80:{proxy_username}:{proxy_password}")
        for x in servers:
            print(self.get_vm_status(x.server_id))
        time.sleep(30)
        for x in servers:
            print(self.get_vm_status(x.server_id))
        self.get_new_startup_script('proxystartupscript', 'squidsetupscript', 'username', proxy_username, 'password', proxy_password)
        self.setup_squid(servers, 'squidsetupscript')

        return proxy_list

def main():
    proxy_gen = ProxyGen100TB(os.environ.get('100TB_API_KEY'))
    proxy_gen.create_proxies(1, 2)


if __name__ == '__main__':
    main()

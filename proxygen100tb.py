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
    def __init__(self):
        self.api_key = os.environ.get('100TB_API_KEY')

    def delete_vm(self, server_id):
        request_url = f'https://cp.100tb.com/rest-api/vps.json/servers/{server_id}?api_key={self.api_key}'
        delete_result = requests.delete(request_url)

    def setup_squid(self, servers, startup_script_file_location, squid_service_location):
        service_name = squid_service_location.replace('.service', '')
        for x in servers:
            sudo_config = Config(overrides={'sudo': {'password': x.password}})
            server_connection = Connection(host=x.ip_address, user=x.username, connect_kwargs={"password": x.password}, config=sudo_config)
            server_connection.sudo('apt-get install dos2unix')
            time.sleep(1)
            file_transfer_result = server_connection.put(startup_script_file_location, remote='/usr/bin/')
            server_connection.sudo('chmod +x /usr/bin/' + startup_script_file_location)
            server_connection.sudo('dos2unix /usr/bin/' + startup_script_file_location)
            file_transfer_result = server_connection.put(squid_service_location, remote='/etc/systemd/system/')
            server_connection.sudo(f'systemctl enable {service_name}')
            try:
                server_connection.sudo('reboot')
            except UnexpectedExit as e:
                print("Caught error while rebooting machine")
    
    def create_vm(self, location_id, proxy_username, proxy_password):
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
            'billHourly': 'true'
        }
        creation_result = json.loads(requests.post(request_url, request_params).text)

        return proxymodels.Server100TB(location_id, creation_result['server'], vm_name, creation_result['ip'], 'root', password, proxy_username, proxy_password, 80)
    
    def get_vm_status(self, vm_id):
        request_url = f'https://cp.100tb.com/rest-api/vps.json/servers/{vm_id}/status/?api_key={self.api_key}'
        vm_status = json.loads(requests.get(request_url).text)

        return vm_status['status']

    def wait_for_vms(self, servers):
        ready = False
        while(ready == False):
            for x in range(len(servers)):
                if(self.get_vm_status(servers[x].server_id) != 2):
                    break
                if(x == len(servers) - 1):
                    ready = True
            if(ready == False):
                time.sleep(10)

    def get_template_id(self, location_id):
        # gets the ubuntu x64 plan id for the location
        request_url = f"https://cp.100tb.com/rest-api/vps.json/templates/{location_id}?api_key={self.api_key}"
        plans = json.loads(requests.get(request_url).text)
        for x in plans:
            if(x['label'] == 'Ubuntu 16.04 x64'):
                return x['id']
    
    def get_new_squid_setup_service(self, old_script_location, new_location, old_startup_script_identifier, startup_script_name):
        service = open(old_script_location, 'r')
        service_script = service.read()
        service_script = service_script.replace(old_startup_script_identifier, startup_script_name)

        new_service = open(new_location, 'w')
        new_service.write(service_script)

        new_service.close()
        service.close()
    
    def get_new_startup_script(self, old_script_location, new_location, proxy_username_identifier, proxy_username, proxy_password_identifier, proxy_password):
        startup_script = open(old_script_location, 'r')
        startup_script_content = startup_script.read()
        startup_script_content = startup_script_content.replace(proxy_username_identifier, proxy_username)
        startup_script_content = startup_script_content.replace(proxy_password_identifier, proxy_password)

        new_startup_script = open(new_location, 'w')
        new_startup_script.write(startup_script_content)
        
        new_startup_script.close()
        startup_script.close()

    def create_proxies(self, location_id, proxy_count, proxy_username, proxy_password):
        servers = []

        for x in range(proxy_count):
            servers.append(self.create_vm(location_id, proxy_username, proxy_password))
        self.wait_for_vms(servers)
        self.get_new_startup_script('proxystartupscript', 'squidsetupscript', 'username', proxy_username, 'password', proxy_password)
        self.get_new_squid_setup_service('squidsetup.service', 'proxysetup.service', 'proxystartupscript', 'squidsetupscript')
        self.setup_squid(servers, 'squidsetupscript', 'proxysetup.service')

        return servers

def main():
    name_generator = haikunator.Haikunator()
    proxy_gen = ProxyGen100TB()
    proxy_count = int(input('How many proxies do you want? '))
    proxies, servers = proxy_gen.create_proxies(proxy_count, 2, name_generator.haikunate(), name_generator.haikunate())
    for x in proxies:
        print(x)
    input('type anything when ready to delete vms')
    proxy_gen.delete_vms(servers)
if __name__ == '__main__':
    main()

import json
import requests
import os
import haikunator
from fabric import Connection
from fabric import Config
from invoke.exceptions import UnexpectedExit
import time

from . import proxymodels


class VpsieProxyGen:
    client_id = None
    client_secret = None
    access_token = None
    base_url = 'https://api.vpsie.com/v1'

    def __init__(self):
        self.client_id = os.environ.get('VPSIE_CLIENT_ID')
        self.client_secret = os.environ.get("VPSIE_CLIENT_SECRET")
        self.access_token = self.get_access_token()
    
    def create_vm(self, location_id, proxy_username, proxy_password):
        name_gen = haikunator.Haikunator()
        header = {
            "Authorization": f"Bearer {self.access_token}"
        }
        request = {
            'hostname': name_gen.haikunate(),
            'offer_id': '9a0e49c6-9f22-11e3-8af5-005056aa8af7', # 1 cpu, 768mb ram
            'datacenter_id': location_id,
            'os_id': 'fbbb3371-283b-11e8-b4ba-005056aadd24' # ubuntu 16.04  
        }
        response = json.loads(requests.post(self.base_url + '/vpsie', request, headers=header).text)

        return proxymodels.VpsieServer(response['vpsie_id'], 'root', response['password'], response['ipv4'], proxy_username, proxy_password, 80)
    
    def setup_squid(self, server, startup_script_file_location, squid_service_location):
        service_name = squid_service_location.replace('.service', '')
        sudo_config = Config(overrides={'sudo': {'password': server.password}})
        server_connection = Connection(host=server.ip_address, user=server.username, connect_kwargs={"password": server.password}, config=sudo_config)
        try:
            server_connection.sudo('reboot')
        except UnexpectedExit as e:
            print("Caught error while rebooting machine")
        self.wait_for_server(server)
        server_connection.sudo('apt-get update')
        server_connection.sudo('apt-get install dos2unix')
        file_transfer_result = server_connection.put(startup_script_file_location, remote='/usr/bin/')
        server_connection.sudo('chmod +x /usr/bin/' + startup_script_file_location)
        server_connection.sudo('dos2unix /usr/bin/' + startup_script_file_location)
        file_transfer_result = server_connection.put(squid_service_location, remote='/etc/systemd/system/')
        server_connection.sudo(f'systemctl enable {service_name}')
        try:
            server_connection.sudo('reboot')
        except UnexpectedExit as e:
            print("Caught error while rebooting machine")
    
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

    def get_access_token(self):
        data = {
            "grand_type": "bearer",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = json.loads(requests.post('https://api.vpsie.com/v1/token', data).text)

        return response['token']['access_token']

    def delete_server(self, server_id):
        header = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.delete(self.base_url + f'/vpsie/{server_id}', headers=header)

    def wait_for_server(self, server):
        server_connection = Connection(host=server.ip_address, user=server.username, connect_kwargs={"password": server.password})
        while(True):
            try:
                server_connection.run('echo "this works"')
                break
            except TimeoutError as error:
                time.sleep(5)
                print('done sleeping')
    
    def create_proxies(self, location_id, proxy_count, proxy_username, proxy_password):
        servers = []
        self.get_new_startup_script('proxystartupscript', 'squidsetupscript', 'username', proxy_username, 'password', proxy_password)
        self.get_new_squid_setup_service('squidsetup.service', 'proxysetup.service', 'proxystartupscript', 'squidsetupscript')

        for x in range(proxy_count):
            servers.append(self.create_vm(location_id, proxy_username, proxy_password))
        for x in servers:
            self.wait_for_server(x)
            self.setup_squid(x, 'squidsetupscript', 'proxysetup.service')

        return servers

def main():
    proxy_gen = VpsieProxyGen()
    servers = proxy_gen.create_proxies('55f06b85-c9ee-11e3-9845-005056aa8af7', 3, 'testuser', 'testpassword')
    for x in servers:
        print(x.to_string())
    input('ready to delete')
    for x in servers:
        proxy_gen.delete_server(x.server_id)
    #server = proxymodels.VpsieServer('test', 'test', 'test', '192.168.1.100', 'test', 'test', 80)
    #proxy_gen.wait_for_server(server)

if __name__ == "__main__":
    main()

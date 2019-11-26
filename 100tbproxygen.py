import requests
import json
import os
from fabric import Connection
from fabric import Config
import proxymodels


class ProxyGen100TB:
    api_key = None
    def __init__(self, api_key):
        self.api_key = api_key

    def setup_squid(self, servers, startup_script_file_location):
        for x in servers:
            sudo_config = Config(overrides={'sudo': {'password': x.password}})
            server_connection = Connection(host=x.ip_address, user=x.username, connect_kwargs={"password": x.password}, config=sudo_config)
            file_transfer_result = server_connection.put(startup_script_file_location, remote='/usr/bin/')
            server_connection.sudo('chmod +x /usr/bin/' + startup_script_file_location)
            file_transfer_result = server_connection.put('squidsetup.service', remote='/etc/systemd/system/')
            server_connection.sudo('systemctl enable squidsetup')
            server_connection.sudo('reboot')
    
    def create_vm(self, location_id):
        request_params = {
            'planId': 2698, # v1-19 server
            'locationId': location_id, # a number 2-20 corresponding to a location
            
        }
    
    def get_plan(self, location_id):
        # gets the ubuntu x64 plan id for the location
        request_url = 'https://cp.100tb.com/rest-api/vps.json/templates/4?api_key=' + self.api_key


def main():
    proxy_gen = ProxyGen100TB(os.environ.get('100TB_API_KEY'))
    server = proxymodels.Server('73.83.96.224', 'pi', 'Jumbobean123', 'test')
    proxy_gen.setup_squid([server], 'proxystartupscript')

if __name__ == '__main__':
    main()

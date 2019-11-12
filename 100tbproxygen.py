import requests
import json
import os
from fabric import Connection
from fabric import Config
import proxy_models


class ProxyGen100TB:
    api_key = None
    def __init__(self):
        api_key = os.environ.get('100TB_API_KEY')

    def setup_squid(self, servers, startup_script_file_location):
        for x in servers:
            sudo_config = Config(overrides={'sudo': {'password': x.password}})
            server_connection = Connection(host=x.ip_address, user=x.username, connect_kwargs={"password": x.password}, config=sudo_config)
            file_transfer_result = server_connection.put(startup_script_file_location, remote='/home/' + x.username)
            server_connection.sudo('chmod +x /home/' + x.username + '/' + startup_script_file_location)

    
def main():
    proxy_gen = ProxyGen100TB()
    server = proxy_models.Server('192.168.1.7', 'pi', 'Jumbobean123', 'test')
    proxy_gen.setup_squid([server], 'proxystartupscript')

if __name__ == '__main__':
    main()

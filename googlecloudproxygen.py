import googleapiclient.discovery
import haikunator
import os
import time
import proxymodels

class GoogleCloudProxyGen:
    compute_client = None
    project = None
    
    def __init__(self):
        self.compute_client = googleapiclient.discovery.build('compute', 'v1')
        self.project = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    def create_vm(self, zone, startup_script):
        name_gen = haikunator.Haikunator()
        image_response = self.compute_client.images().getFromFamily(project='ubuntu-os-cloud', family='ubuntu-1604-lts').execute()
        vm_name = name_gen.haikunate()
        server = {
            'name': vm_name,
            'machineType': f"zones/{zone}/machineTypes/n1-standard-1",
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': image_response['selfLink']
                    }
                }
            ],
            'networkInterfaces': [
                {
                    'network': '/global/networks/default',
                    'accessConfigs': [
                        {'type': 'ONE_TO_ONE_NAT', 'name': 'external nat'}
                    ]
                }
            ],
            'metadata': {
                'items': [
                    {
                        'key': 'startup-script',
                        'value': startup_script
                    }
                ]
            }
        }
        creation_result = self.compute_client.instances().insert(project=self.project, zone=zone, body=server).execute()
        return vm_name

    def delete_vm(self, zone, server_name):
        return self.compute_client.instances().delete(project=self.project, zone=zone, instance=server_name).execute()
    
    def get_vm_ip_address(self, zone, server_name):
        while(True):
            try:
                server_ip = self.compute_client.instances().get(project=self.project, zone=zone, instance=server_name).execute()['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                return server_ip
            except KeyError as identifier:
                time.sleep(5)

    def get_startup_script(self, startup_script_location, username_identifier, username, password_identifier, password):
        startup_script_file = open(startup_script_location, "r")
        startup_script = startup_script_file.read()
        startup_script = startup_script.replace(username_identifier, username)
        startup_script = startup_script.replace(password_identifier, password)

        return startup_script
    
    def create_proxies(self, region, proxy_count, proxy_username, proxy_password):
        startup_script = self.get_startup_script('proxystartupscript', 'username', proxy_username, 'password', proxy_password)
        servers = []
        for x in range(proxy_count):
            server_name = self.create_vm(region, startup_script)
            server_ip = self.get_vm_ip_address(region, server_name)
            servers.append(proxymodels.GoogleCloudServer(region, server_name, server_ip, proxy_username, proxy_password, 80))
        
        return servers

def main():
    proxy_gen = GoogleCloudProxyGen()
    servers = proxy_gen.create_proxies('focal-maker-240918', 'us-east4-c', 5, 'testuser', 'testpass')
    for x in servers:
        print(x.to_string())
    input('type anything to delete')
    for x in servers:
        proxy_gen.delete_vm('focal-maker-240918', 'us-east4-c', x.server_name)

if __name__ == "__main__":
    main()

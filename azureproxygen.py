import os
import base64
import time

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from haikunator import Haikunator
import proxytester
import proxymodels

class AzureProxyGen:
    compute_client = None
    network_client = None
    resource_client = None

    def __init__(self):
        self.network_client = NetworkManagementClient(self.get_credentials(), self.get_subscription())
        self.compute_client = ComputeManagementClient(self.get_credentials(), self.get_subscription())
        self.resource_client = ResourceManagementClient(self.get_credentials(), self.get_subscription())
    
    def create_resource_group(self, location, name):
        resource_group_params = {'location': location}
        self.resource_client.resource_groups.create_or_update(name, resource_group_params)

    def create_security_group(self, group_name, location, name):
        security_rule = {
            'name': 'http-port-access',
            'description': "allows port 80 for http proxies",
            'protocol': 'Tcp',
            'source_port_range': '*',
            'destination_port_range': '80',
            'source_address_prefix': '*',
            'destination_address_prefix': '*',
            'access': 'Allow',
            'priority': 100,
            'direction': 'Inbound'
        }
        security_group_params = {
            'location': location, 
            'security_rules': [security_rule]
        }
        self.network_client.network_security_groups.create_or_update(group_name, name, security_group_params)

    def create_virtual_network(self, group_name, location, name):
        vnet_params = {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/20']
            }
        }
        self.network_client.virtual_networks.create_or_update(group_name, name, vnet_params)        

    def create_subnet(self, group_name, vnet_name, name):
        subnet_params = {
            'address_prefix': '10.0.0.0/20'
        }
        self.network_client.subnets.create_or_update(group_name, vnet_name, name, subnet_params)

    def get_vm_ip_address(self, group_name, ip_name):
        public_ip = self.network_client.public_ip_addresses.get(group_name, ip_name)
        while public_ip.ip_address == None:
            public_ip = self.network_client.public_ip_addresses.get(group_name, ip_name)
            time.sleep(5)
        return public_ip.ip_address

    def get_credentials(self):
        credentials = ServicePrincipalCredentials(client_id = os.environ.get('AZURE_CLIENT_ID'), secret = os.environ.get('AZURE_CLIENT_SECRET'), tenant = os.environ.get('AZURE_TENANT_ID'))
        return credentials

    def get_subscription(self):
        subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
        return subscription_id

    def get_startup_script(self, file_name, proxy_username_identifier, proxy_password_identifier, proxy_username, proxy_password):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.replace(proxy_username_identifier, proxy_username)
        startup_script = startup_script.replace(proxy_password_identifier, proxy_password)
        startup_script = startup_script.encode()
        startup_script = base64.b64encode(startup_script, altchars=None)
        startup_script = startup_script.decode("utf-8")

        return startup_script

    def get_subnet_info(self, group_name, vnet_name, subnet_name):
        subnet_info = self.network_client.subnets.get(group_name, vnet_name, subnet_name)

        return subnet_info

    def get_security_group_info(self, group_name, security_group_name):
        security_group_info = self.network_client.network_security_groups.get(group_name, security_group_name)

        return security_group_info

    def create_public_ip(self, group_name, ip_location, ip_name):
        public_ip_params = {
            'location': ip_location,
            'public_ip_allocation_method': 'Dynamic'
        }
        ip_creation_result = self.network_client.public_ip_addresses.create_or_update(group_name, ip_name, public_ip_params)
        public_ip = self.network_client.public_ip_addresses.get(group_name, ip_name)
        return public_ip
    
    def create_nic(self, group_name, nic_name, nic_location, public_ip, subnet_info, security_group_info):
        nic_params = {
            'location': nic_location,
            'ip_configurations': [{
                'name': nic_name + "-ipconfig",
                'public_ip_address': public_ip,
                'subnet': {
                    'id': subnet_info.id
                }
            }],
            'network_security_group': security_group_info
        }
        nic_creation_result = self.network_client.network_interfaces.create_or_update(group_name, nic_name, nic_params)
        nic = self.network_client.network_interfaces.get(group_name, nic_name)
        return nic
    
    def create_vm(self, group_name, vm_location, vm_name, vm_password, startup_script, nic_info):
        vm_parameters = {
            'location': vm_location,
            'os_profile': {
                'computer_name': vm_name,
                'admin_username': vm_name,
                'admin_password': vm_password,
                'custom_data': startup_script
            },
            'hardware_profile': {
                'vm_size': 'Standard_B1ls'
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': 'Canonical',
                    'offer': 'UbuntuServer',
                    'sku': '16.04.0-LTS',
                    'version': 'latest'
                },
                'os_disk': {
                    'name': vm_name + "-osdisk",
                    'caching': 'None',
                    'create_option': 'FromImage',
                    'disk_size_gb': 30,
                    'managed_disk': {
                        'storage_account_type': 'Standard_LRS'
                    }
                }
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': nic_info.id
                }]
            },
            'tags': {
                'expiration_date': 'expirationdatehere'
            }
        }
        createVMResponse = self.compute_client.virtual_machines.create_or_update(group_name, vm_name, vm_parameters)
    
    def delete_vm_completely(self, group_name, disk_name, nic_name, ip_name, vm_name):
        self.compute_client.virtual_machines.delete(group_name, vm_name)
        self.compute_client.disks.delete(group_name, disk_name)
        self.network_client.network_interfaces.delete(group_name, nic_name)
        self.network_client.public_ip_addresses.delete(group_name, ip_name)

    def initialize_account(self, location):
        default_resource_group_name = 'sneaker-tools-proxy-resource-group'
        self.create_resource_group(location, default_resource_group_name)
        self.create_virtual_network(default_resource_group_name, location, 'sneaker-tools-proxy-virtual-network')
        self.create_subnet(default_resource_group_name, 'sneaker-tools-proxy-virtual-network', 'sneaker-tools-proxy-subnet')
        self.create_security_group(default_resource_group_name, location, 'sneaker-tools-proxies-security-group')

    def create_proxies(self, proxy_count, location, startup_script_name, first_time_setup, proxy_username, proxy_password):
        if(first_time_setup):
            self.initialize_account(location) # initialize account to make sure all requirements are satisfied
        # general purpose objects
        name_generator = Haikunator()
        server_list = []

        # default required azure resources
        group_name = 'sneaker-tools-proxy-resource-group'
        vnet_name = 'sneaker-tools-proxy-virtual-network'
        subnet_name = 'sneaker-tools-proxy-subnet'
        security_group_name = 'sneaker-tools-proxies-security-group'
        
        # get startup script
        startup_script = self.get_startup_script(startup_script_name, 'username', 'password', proxy_username, proxy_password)
        
        # one time networking variables
        security_group = self.get_security_group_info(group_name, security_group_name)
        subnet = self.get_subnet_info(group_name, vnet_name, subnet_name)
        
        for x in range(proxy_count):   
            # vm specifc variables
            vm_name = name_generator.haikunate()
            public_ip = self.create_public_ip(group_name, location, vm_name + "-ip")
            nic = self.create_nic(group_name, vm_name + "-nic", location, public_ip, subnet, security_group)

            # create vm
            self.create_vm(group_name, location, vm_name, name_generator.haikunate(), startup_script, nic)
            server_list.append(proxymodels.AzureServer(self.get_vm_ip_address(group_name, vm_name + "-ip"), proxy_username, proxy_password, 80, vm_name + "-osdisk", vm_name + "-ip", vm_name + "-nic", vm_name, group_name))

        return server_list

def main():
    # general purpose objects
    name_generator = Haikunator()

    # azure objects
    proxy_gen = AzureProxyGen()

    LOCATION = 'eastus'

    # ask user for inputs
    proxy_count = int(input("How many proxies would you like to be created? "))
    proxy_username = input("What do you want the proxy authentication username to be? ")
    proxy_password = input("What do you want the proxy authentication password to be? ")
    print("Now creating " + str(proxy_count) + " proxies")

    ip_list = proxy_gen.create_proxies(proxy_count, LOCATION, 'proxystartupscript', False, proxy_username, proxy_password)
    proxy_list = []

    # test proxies
    for x in range(len(ip_list)):
        while proxytester.test_proxy(ip_list[x], proxy_username, proxy_password, "80") == False:
            print(ip_list[x] + " not yet ready. waiting 5 seconds before testing again")
            time.sleep(5)
        proxy_list.append(ip_list[x] + ":80:" + proxy_username + ":" + proxy_password)
    print("All proxies ready.")
    print('\n'.join(map(str, proxy_list)))

if __name__ == '__main__':
    main()


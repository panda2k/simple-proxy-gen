import os
import base64
import time

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from haikunator import Haikunator
import proxytester

class AzureProxyGen:
    compute_client = None
    network_client = None
    def __init__(self):
        self.network_client = NetworkManagementClient(self.get_credentials(), self.get_subscription())
        self.compute_client = ComputeManagementClient(self.get_credentials(), self.get_subscription())
    
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

    def read_startup_script(self, file_name):
        startup_script_file = open(file_name, "r")
        startup_script = startup_script_file.read()
        startup_script_file.close()
        startup_script = startup_script.encode()
        startup_script = base64.b64encode(startup_script, altchars=None)
        startup_script = startup_script.decode("utf-8")
        return startup_script

    def get_subnet_info(self, group_name, vnet_name, subnet_name):
        subnet_info = self.network_client.subnets.get(group_name, 'proxyvnet', 'proxysubnet')

        return subnet_info

    def get_security_group_info(self, group_name, security_group_name):
        security_group_info = self.network_client.network_security_groups.get(group_name, 'proxy-ports')

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

def main():
    # general purpose objects
    name_generator = Haikunator()

    # azure objects
    proxy_gen = AzureProxyGen()

    LOCATION = 'eastus'
    GROUP_NAME = 'proxies'
    VNET_NAME = 'proxyvnet'
    SUBNET_NAME = 'proxysubnet'
    SECURITY_GROUP_NAME = 'proxy-ports'
    STARTUP_SCRIPT = proxy_gen.read_startup_script("proxystartupscript.txt")

    # one time networking variables
    security_group = proxy_gen.get_security_group_info(GROUP_NAME, SECURITY_GROUP_NAME)
    subnet = proxy_gen.get_subnet_info(GROUP_NAME, VNET_NAME, SUBNET_NAME)
    
    # ask user for inputs
    proxy_count = int(input("How many proxies would you like to be created? "))
    print("Now creating " + str(proxy_count) + " proxies")

    proxy_list = []

    # create proxies
    for x in range(proxy_count):   
        # vm specifc variables
        vm_name = name_generator.haikunate()
        public_ip = proxy_gen.create_public_ip(GROUP_NAME, LOCATION, vm_name + "-ip")
        nic = proxy_gen.create_nic(GROUP_NAME, vm_name + "-nic", LOCATION, public_ip, subnet, security_group)

        # create vm
        proxy_gen.create_vm(GROUP_NAME, LOCATION, vm_name, name_generator.haikunate(), STARTUP_SCRIPT, nic)
        proxy_list.append(proxy_gen.get_vm_ip_address(GROUP_NAME, vm_name + "-ip"))
        print("finished creating proxy #" + str(x + 1))

    # test proxies
    for x in range(len(proxy_list)):
        while proxytester.test_proxy(proxy_list[x], "pwbo", "pwbo", "80") == False:
            print(proxy_list[x] + " not yet ready. waiting 5 seconds before testing again")
            time.sleep(5)
        proxy_list[x] += ":80:pwbo:pwbo"
    print("All proxies ready.")
    print('\n'.join(map(str, proxy_list)))

if __name__ == '__main__':
    main()


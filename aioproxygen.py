from cloud_proxy_generators import awsproxygen
from cloud_proxy_generators import azureproxygen
from cloud_proxy_generators import proxygen100tb
from cloud_proxy_generators import upcloudproxygen
from cloud_proxy_generators import googlecloudproxygen
from cloud_proxy_generators import linodeproxygen
from cloud_proxy_generators import vultrproxygen
from cloud_proxy_generators import digitaloceanproxygen
from cloud_proxy_generators import vpsieproxygen
from cloud_proxy_generators import proxymodels

import os
import haikunator
import json

def print_intro():
    print("   _____ _      ____  _    _ _____    _____  _____   ______   ____     __   _____ ______ _   _ ")
    print("  / ____| |    / __ \| |  | |  __ \  |  __ \|  __ \ / __ \ \ / /\ \   / /  / ____|  ____| \ | |")
    print(" | |    | |   | |  | | |  | | |  | | | |__) | |__) | |  | \ V /  \ \_/ /  | |  __| |__  |  \| |")
    print(" | |    | |   | |  | | |  | | |  | | |  ___/|  _  /| |  | |> <    \   /   | | |_ |  __| | . ` |")
    print(" | |____| |___| |__| | |__| | |__| | | |    | | \ \| |__| / . \    | |    | |__| | |____| |\  |")
    print("  \_____|______\____/ \____/|_____/  |_|    |_|  \_\\\____/_/ \_\   |_|     \_____|______|_| \_|")

def print_menu_options():
    print("1. View Proxy Lists")
    print("2. View Analytics")
    print("3. Generate Proxies")

def print_proxy_options():
    print("1. Amazon Web Services")
    print("2. Microsoft Azure")
    print("3. 100tb")
    print("4. Google Cloud")
    print("5. Upcloud")
    print("6. Linode")
    print("7. Vultr")
    print("8. Digital Ocean")
    print("9. VPSie")

def print_proxy_list_options():
    print("1. Terminate proxies in list")
    print("2. List proxies")
    print("3. View proxy list analytics")

def get_region_select(user_option):
    cloud_providers = ['aws', 'azure', '100tb', 'gcs', 'upcloud', 'linode', 'vultr', 'digitalocean', 'vpsie']
    cloud_provider = cloud_providers[user_option - 1]
    valid_input = False
    region_dict_file = open('./proxy_gen_lib/cloudlocations.json', 'r')
    region_dict = json.load(region_dict_file)
    region_dict_file.close()
    print('Locations:')
    for x in region_dict[cloud_provider]:
        print(x.title())
    region = input("Select your location by typing the locations name: ").lower()
    while(valid_input == False):
        if(region in region_dict[cloud_provider]):
            valid_input = True
        else:
            region = input("Invalid region. Select your location by typing the locations name: ").lower()
    
    return region_dict[cloud_provider][region]

def check_for_credentials():
    credentials = [['Azure', '100tb', 'Google Cloud Services', 'Amazon Web Services', 'Upcloud', 'Linode', 'Vultr', 'Digital Ocean', 'VPSie'], [True, True, True, True, True, True, True, True, True]]
    if(os.environ.get('AZURE_CLIENT_ID') == None or os.environ.get('AZURE_CLIENT_SECRET') == None or os.environ.get('AZURE_TENANT_ID') == None or os.environ.get('AZURE_SUBSCRIPTION_ID') == None):
        credentials[1][0] = False
    if(os.environ.get('100TB_API_KEY') == None):
        credentials[1][1] = False
    if(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') == None or os.environ.get('GOOGLE_CLOUD_PROJECT') == None):
        credentials[1][2] = False
    if(os.path.exists(os.path.expanduser('~') + "\\.aws") == False):
        credentials[1][3] = False
    if(os.environ.get('UPCLOUD_API_USERNAME') == None or os.environ.get('UPCLOUD_API_PASSWORD') == None):
        credentials[1][4] = False
    if(os.environ.get('LINODE_ACCESS_TOKEN') == None):
        credentials[1][5] = False
    if(os.environ.get('VULTR_ACCESS_TOKEN') == None):
        credentials[1][6] = False
    if(os.environ.get('DIGITAL_OCEAN_ACCESS_TOKEN') == None):
        credentials[1][7] = False
    if(os.environ.get('VPSIE_CLIENT_ID') == None or os.environ.get('VPSIE_CLIENT_SECRET') == None):
        credentials[1][8] = False

    return credentials

def get_credentials(credentials_list):
    if(credentials_list[1][0] == False):
        if(bool(input("You are missing Azure credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['AZURE_CLIENT_ID'] = input("Input your Azure Client ID: ")
            os.environ['AZURE_CLIENT_SECRET'] = input("Input your Azure Client Secret: ")
            os.environ['AZURE_TENANT_ID'] = input("Input your Azure Tenant ID: ")
            os.environ['AZURE_SUBSCRIPTION_ID'] = input("Input your Azure Subscription ID: ")
            print("Now finished collecting Azure credentials")
    if(credentials_list[1][1] == False):
        if(bool(input("You are missing 100tb credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['100TB_API_KEY'] = input("Input your 100tb API key: ")
    if(credentials_list[1][2] == False):
        if(bool(input("You are missing Google Cloud credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = input("Input the direct file location to your Google Cloud credentials file. Use \\ instead of / in the file path. ")
            os.environ['GOOGLE_CLOUD_PROJECT'] = input("Input the Google Cloud project you want the proxies to be generated in: ")
    if(credentials_list[1][3] == False):
        if(bool(input("You are missing Amazon Web Services credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            aws_access_key = input("Input your AWS Access Key ID: ")
            aws_secret_accesss_key = input("Input your Secret AWS Access Key")
            aws_folder_directory = os.path.expanduser('~') + "\\.aws"
            os.mkdir(aws_folder_directory)
            credentials_file = open(aws_folder_directory + "\\credentials", "w")
            credentials_file.write(f"[default]\naws_access_key_id = {aws_access_key}\naws_secret_access_key = {aws_secret_accesss_key}")
            credentials_file.close()
            config_file = open(aws_folder_directory + "\\config", "w")
            config_file.write("[default]\nregion = us-east-1\noutput = json")
            config_file.close()
    if(credentials_list[1][4] == False):
        if(bool(input("You are missing Upcloud API credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['UPCLOUD_API_USERNAME'] = input("Input your Upcloud API Username: ")
            os.environ['UPCLOUD_API_PASSWORD'] = input("Input your upcloud API Password: ")
    if(credentials_list[1][5] == False):
        if(bool(input("You are missing Linode credentials. Would you like to set them now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['LINODE_ACCESS_TOKEN'] = input("Input your Linode API Access Token: ")
    if(credentials_list[1][6] == False):
        if(bool(input("You are missing your Vultr access key. Would you like to set it now?Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['VULTR_ACCESS_TOKEN'] = input("Input your Vultr access key: ")
    if(credentials_list[1][7] == False):
        if(bool(input("You are missing your Digital Ocean access token. Would you like to set it now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['DIGITAL_OCEAN_ACCESS_TOKEN'] = input("Input your Digital Ocean access token")
    if(credentials_list[1][8] == False):
        if(bool(input("You are missing your VPSie credentials. Would you like to set it now? Hit enter if you don't want to, enter anything if you want to set it now. "))):
            os.environ['VPSIE_CLIENT_ID'] = input("Input your VPSie client ID")
            os.environ['VPSIE_CLIENT_SECRET'] = input("Input you VPSie client secret")

def get_user_input(minimum_option, maximum_option, base_message, error_message):
    user_input = int(input(base_message))
    while(user_input > maximum_option or user_input < minimum_option):
        user_input = int(input(error_message))
    
    return user_input

def get_proxies_from_list(proxy_list_location):
    proxy_dict = read_proxy_list(proxy_list_location)
    proxy_list = []
    for x in range(len(proxy_dict['proxies'])):
        proxy_list.append(proxy_dict['proxies'][x]['ip_address'] + ':' + str(proxy_dict['proxies'][x]['proxy_port']) + ':' + proxy_dict['proxies'][x]['proxy_username'] + ':' + proxy_dict['proxies'][x]['proxy_password'])
    
    return proxy_list

def read_proxy_list(proxy_list_location):
    proxy_list_file = open(proxy_list_location, 'r')
    proxy_dict = json.load(proxy_list_file)
    proxy_list_file.close()

    return proxy_dict

def get_proxy_lists():
    proxy_lists = os.listdir('proxylists')
    for x in range(len(proxy_lists)):
        proxy_lists[x] = proxy_lists[x].replace('.json', '')
    
    return proxy_lists

def get_proxy_price(provider, location_id):
    proxy_price_file = open('./proxy_gen_lib/cloudpricing.json', 'r')
    proxy_prices = json.load(proxy_price_file)
    proxy_price_file.close()

    return proxy_prices[provider][location_id]

def get_total_proxy_cost():
    proxy_lists = get_proxy_lists()
    total_hourly_cost = 0

    for x in range(len(proxy_lists)):
        proxy_list_dict = read_proxy_list(os.path.join(os.path.realpath(''), f'proxylists\\{proxy_lists[x]}.json'))
        total_hourly_cost += proxy_list_dict['hourly_cost']
    
    return total_hourly_cost

def get_proxy_list_cost():
    proxy_lists = get_proxy_lists()
    proxy_lists_hourly_costs = { }
    for x in range(len(proxy_lists)):
        proxy_list_dict = read_proxy_list(os.path.join(os.path.realpath(''), f'proxylists\\{proxy_lists[x]}.json'))
        proxy_lists_hourly_costs[proxy_lists[x]] = proxy_list_dict['hourly_cost']
    
    sorted_proxy_lists_hourly_costs = sorted(proxy_lists_hourly_costs.items(), key=lambda x: x[1]) # sort proxy lists by hourly cost
    
    return sorted_proxy_lists_hourly_costs

def terminate_proxies(proxy_list_location):
    proxy_list_dict = read_proxy_list(proxy_list_location)
    if(proxy_list_dict['cloud_provider'] == 'aws'):
        proxy_gen = awsproxygen.AWSProxyGen()
        proxy_gen.cancel_spot_fleet(proxy_list_dict['proxies'][0]['spot_fleet_id'])
    elif(proxy_list_dict['cloud_provider'] == 'azure'):
        proxy_gen = azureproxygen.AzureProxyGen()
        servers = []
        for x in proxy_list_dict['proxies']:
            servers.append(proxymodels.AzureServer(x['ip_address'], 'doesntmatter', 'doesntmatter', 80, x['disk_name'], x['ip_name'], x['nic_name'], x['vm_name'], x['resource_group_name']))
        proxy_gen.delete_vms(servers)
    elif(proxy_list_dict['cloud_provider'] == '100tb'):
        proxy_gen = proxygen100tb.ProxyGen100TB()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_vm(x['server_id'])
    elif(proxy_list_dict['cloud_provider'] == 'upcloud'):
        proxy_gen = upcloudproxygen.UpcloudProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.shutdown_server(x['uuid'])
        for x in proxy_list_dict['proxies']:
            proxy_gen.wait_for_server_shutdown(x['uuid'])
            proxy_gen.delete_server(x['uuid'])
    elif(proxy_list_dict['cloud_provider'] == 'linode'):
        proxy_gen = linodeproxygen.LinodeProxygen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_server(x['server_id'])
    elif(proxy_list_dict['cloud_provider'] == 'vultr'):
        proxy_gen = vultrproxygen.VultrProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_server(x['server_id'])
        proxy_gen.delete_script(proxy_list_dict['proxies'][0]['startup_script_id'])
    elif(proxy_list_dict['cloud_provider'] == 'digitalocean'):
        proxy_gen = digitaloceanproxygen.DigitalOceanProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_vm(x['server_id'])
    elif(proxy_list_dict['cloud_provider'] == 'vpsie'):
        proxy_gen = vpsieproxygen.VpsieProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_server(x['server_id'])
    elif(proxy_list_dict['cloud_provider'] == 'gcs'):
        proxy_gen = googlecloudproxygen.GoogleCloudProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_vm(x['zone'], x['server_name'])

def create_proxies(user_option, region):
    name_gen = haikunator.Haikunator()
    proxy_list = []
    proxy_list_name = input("Proxy list name: ")
    proxy_count = int(input("How many proxies would you like to generate: "))
    proxy_list_file = open(os.path.join(os.path.realpath(''), f'proxylists\\{proxy_list_name}.json'), 'a')
    if(user_option == 1):
        proxy_gen = awsproxygen.AWSProxyGen()
        cloud_provider = 'aws'
    elif(user_option == 2):
        proxy_gen = azureproxygen.AzureProxyGen()
        cloud_provider = 'azure'
    elif(user_option == 3):
        cloud_provider = '100tb'
        proxy_gen = proxygen100tb.ProxyGen100TB()
    elif(user_option == 4):
        cloud_provider = 'gcs'
        proxy_gen = googlecloudproxygen.GoogleCloudProxyGen()
    elif(user_option == 5):
        cloud_provider = 'upcloud'
        proxy_gen = upcloudproxygen.UpcloudProxyGen()
    elif(user_option == 6):
        cloud_provider = 'linode'
        proxy_gen = linodeproxygen.LinodeProxygen()
    elif(user_option == 7):
        cloud_provider = 'vultr'
        proxy_gen = vultrproxygen.VultrProxyGen()
    elif(user_option == 8):
        cloud_provider = 'digitalocean'
        proxy_gen = digitaloceanproxygen.DigitalOceanProxyGen()
    elif(user_option == 9):
        cloud_provider = 'vpsie'
        proxy_gen = vpsieproxygen.VpsieProxyGen()
    servers = proxy_gen.create_proxies(region, proxy_count, name_gen.haikunate(), name_gen.haikunate())

    print("Here are your generated proxies: ")
    for x in servers:
        proxy_list.append(x.to_dict())
        print(x.to_string())

    proxy_list_dict = {
        'cloud_provider': cloud_provider,
        'region': region,
        'hourly_cost': len(proxy_list) * get_proxy_price(cloud_provider, str(region)),
        'proxies': proxy_list
    }
    json.dump(proxy_list_dict, proxy_list_file)
    proxy_list_file.close()

def main():
    print_intro()
    print_menu_options()
    menu_choice = int(input("Input the number corresponding to the menu item you'd like to select: "))
    if(menu_choice == 1):
        base_input_message = "Select a proxy list: "
        invalid_input_message = "Invalid choice. Try again: "
        base_proxy_list_option_choice_message = "Select what'd you like to do: "
        proxy_lists = get_proxy_lists()
        for x in range(len(proxy_lists)):
            print(f'{x + 1}. {proxy_lists[x]}')
        if(len(proxy_lists) == 0):
            print("No proxy lists found")
        else:
            proxy_list_choice = get_user_input(1, len(proxy_lists) + 1, base_input_message, invalid_input_message)
            print(proxy_lists[proxy_list_choice - 1])
            proxy_list_file_location = os.path.join(os.path.realpath(''), f'proxylists\\{proxy_lists[proxy_list_choice - 1]}.json')
            print_proxy_list_options()
            proxy_list_option_choice = get_user_input(1, 3, base_proxy_list_option_choice_message, invalid_input_message)
            if(proxy_list_option_choice == 1):
                if(input(f"Confirm the deletion of these proxies by typing the list name ({proxy_lists[proxy_list_choice - 1]}): ") == proxy_lists[proxy_list_choice - 1]):
                    terminate_proxies(proxy_list_file_location)
                    os.remove(proxy_list_file_location) # delete proxy list
            elif(proxy_list_option_choice == 2):
                proxy_list = get_proxies_from_list(proxy_list_file_location)
                for x in proxy_list:
                    print(x)
            elif(proxy_list_option_choice == 3):
                print("ANALYTICS")
                print("Hourly cost: $" + str(round(read_proxy_list(proxy_list_file_location)['hourly_cost'], 5)))
    elif(menu_choice == 2):
        proxy_list_cost = get_proxy_list_cost()
        print("ANALYTICS")
        print("Hourly proxy cost: $" + str(round(get_total_proxy_cost(), 5)))
        print("Proxy lists sorted by hourly cost:")
        if(len(get_proxy_lists()) == 0):
            print("No proxy lists found")
        else:
            for x in range(len(proxy_list_cost) - 1, -1, -1):
                print(proxy_list_cost[x][0] + " - $" + str(round(proxy_list_cost[x][1], 5)))
    elif(menu_choice == 3):
        base_input_message = "Which cloud provider would you like to choose? Input a number 1 - 9: "
        invalid_input_message = "Invalid input. Which cloud provider would you like to choose? Input a number 1 - 9: "
        get_credentials(check_for_credentials())
        print_proxy_options()
        user_option = get_user_input(1, 9, base_input_message, invalid_input_message)
        region = get_region_select(user_option)
        create_proxies(user_option, region)
 
if __name__ == "__main__":
    main()

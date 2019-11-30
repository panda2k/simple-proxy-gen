import awsproxygen
import azureproxygen
import proxygen100tb
import proxymodels
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

def print_proxy_list_options():
    print("1. Terminate proxies in list")
    print("2. List proxies")
    print("3. View proxy list analytics")

def check_for_credentials():
    credentials = [['Azure', '100tb', 'Google Cloud Services', 'Amazon Web Services'], [True, True, True, True]]
    if(os.environ.get('AZURE_CLIENT_ID') == None or os.environ.get('AZURE_CLIENT_SECRET') == None or os.environ.get('AZURE_TENANT_ID') == None or os.environ.get('AZURE_SUBSCRIPTION_ID') == None):
        credentials[1][0] = False
    if(os.environ.get('100TB_API_KEY') == None):
        credentials[1][1] = False
    if(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') == None):
        credentials[1][2] = False
    if(os.path.exists(os.path.expanduser('~') + "\\.aws") == False):
        credentials[1][3] = False

    return credentials

def get_credentials(credentials_list):
    if(credentials_list[1][0] == False):
        if(bool(input("You are missing Azure credentials. Would you like to set them now? True or False "))):
            os.environ['AZURE_CLIENT_ID'] = input("Input your Azure Client ID: ")
            os.environ['AZURE_CLIENT_SECRET'] = input("Input your Azure Client Secret: ")
            os.environ['AZURE_TENANT_ID'] = input("Input your Azure Tenant ID: ")
            os.environ['AZURE_SUBSCRIPTION_ID'] = input("Input your Azure Subscription ID: ")
            print("Now finished collecting Azure credentials")
    if(credentials_list[1][1] == False):
        if(bool(input("You are missing 100tb credentials. Would you like to set them now? True or False "))):
            os.environ['100TB_API_KEY'] = input("Input your 100tb API key: ")
    if(credentials_list[1][2] == False):
        if(bool(input("You are missing Google Cloud credentials. Would you like to set them now? True or False "))):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = input("Input the direct file location to your Google Cloud credentials file. Use / instead of \\ in the file path. ")
    if(credentials_list[1][3] == False):
        if(bool(input("You are missing Amazon Web Services credentials. Would you like to set them now? True or False "))):
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

    return proxy_dict

def get_proxy_lists():
    proxy_lists = os.listdir('proxylists')
    for x in range(len(proxy_lists)):
        proxy_lists[x] = proxy_lists[x].replace('.json', '')
    
    return proxy_lists

def terminate_proxies(proxy_list_location):
    proxy_list_dict = read_proxy_list(proxy_list_location)
    if(proxy_list_dict['cloud_provider'] == 'aws'):
        proxy_gen = awsproxygen.AWSProxyGen()
        proxy_gen.cancel_spot_fleet(proxy_list_dict['proxies'][0]['spot_fleet_id'])
    if(proxy_list_dict['cloud_provider'] == 'azure'):
        proxy_gen = azureproxygen.AzureProxyGen()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_vm_completely(x['resource_group_name'], x['disk_name'], x['nic_name'], x['ip_name'], x['vm_name'])
    if(proxy_list_dict['cloud_provider'] == '100tb'):
        proxy_gen = proxygen100tb.ProxyGen100TB()
        for x in proxy_list_dict['proxies']:
            proxy_gen.delete_vm(x['server_id'])
    

def create_proxies(user_option):
    name_gen = haikunator.Haikunator()
    proxy_list = []
    proxy_list_name = input("Proxy list name: ")
    proxy_count = int(input("How many proxies would you like to generate: "))
    proxy_list_file = open(os.path.join(os.path.dirname(os.path.realpath('__file__')), f'proxylists\\{proxy_list_name}.json'), 'a')
    if(user_option == 1):
        proxy_gen = awsproxygen.AWSProxyGen()
        cloud_provider = 'aws'
        proxies = proxy_gen.create_proxies(proxy_list_name, proxy_count, name_gen.haikunate(), name_gen.haikunate())
        print("Here are your generated proxies:")
        for x in proxies:
            proxy_list.append(x.to_json())
            print(x.to_string())
    elif(user_option == 2):
        proxy_gen = azureproxygen.AzureProxyGen()
        cloud_provider = 'azure'
        servers = proxy_gen.create_proxies(proxy_count, 'eastus', 'proxystartupscript', False, name_gen.haikunate(), name_gen.haikunate())
        print("Here are your generated proxies:")
        for x in servers:
            proxy_list.append(x.to_json())
            print(x.to_string())
    elif(user_option == 3):
        cloud_provider = '100tb'
        proxy_gen = proxygen100tb.ProxyGen100TB()
        servers = proxy_gen.create_proxies(proxy_count, 2, name_gen.haikunate(), name_gen.haikunate())
        print("Here are your generated proxies: ")
        for x in servers:
            proxy_list.append(x.to_json())
            print(x.to_string())
    proxy_list_dict = {
        'cloud_provider': cloud_provider,
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
            proxy_list_file_location = os.path.join(os.path.dirname(os.path.realpath('__file__')), f'proxylists\\{proxy_lists[proxy_list_choice - 1]}.json')
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
                print("work in progress")
    elif(menu_choice == 3):
        base_input_message = "Which cloud provider would you like to choose? Input a number 1 - 4: "
        invalid_input_message = "Invalid input. Which cloud provider would you like to choose? Input a number 1 - 4: "
        get_credentials(check_for_credentials())
        print_proxy_options()
        user_option = get_user_input(1, 4, base_input_message, invalid_input_message)
        create_proxies(user_option)

    
if __name__ == "__main__":
    main()
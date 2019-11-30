import awsproxygen
import azureproxygen
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

def get_user_input(minimum_option, maximum_option):
    user_input = int(input(f"Which cloud provider would you like to choose? Input a number {minimum_option} - {maximum_option}: "))
    while(user_input > maximum_option or user_input < minimum_option):
        user_input = int(input(f"Invalid input. Which cloud provider would you like to choose? Input a number {minimum_option} - {maximum_option}: "))
    
    return user_input

def create_proxies(user_option):
    name_gen = haikunator.Haikunator()

    if(user_option == 1):
        proxy_list = []
        proxy_gen = awsproxygen.AWSProxyGen()
        proxy_list_name = input("Proxy list name: ")
        proxy_count = int(input("How many proxies would you like to generate: "))
        proxies = proxy_gen.create_proxies(proxy_list_name, proxy_count, name_gen.haikunate(), name_gen.haikunate())
        proxy_list_file = open(os.path.join(os.path.dirname(os.path.realpath('__file__')), f'proxylists\\{proxy_list_name}.json'), 'a')
        print("Here are your generated proxies:")
        for x in proxies:
            proxy_list.append(x.to_json())
            print(x.to_string())
        proxy_list_dict = {
            'proxies': proxy_list
        }
        json.dump(proxy_list_dict, proxy_list_file)
        proxy_list_file.close()

def main():
    print_intro()
    print_menu_options()
    menu_choice = int(input("Input the number corresponding to the menu item you'd like to select: "))
    if(menu_choice == 3):
        get_credentials(check_for_credentials())
        print_proxy_options()
        user_option = get_user_input(1, 4)
        create_proxies(user_option)

    
if __name__ == "__main__":
    main()
import googleapiclient.discovery
import haikunator

class GoogleCloudProxyGen:
    compute_client = None
    
    def __init__(self):
        self.compute_client = googleapiclient.discovery.build('compute', 'v1')
    
    def create_vm(self, project, zone, startup_script_location, username_identifier, username, password_identifier, password):
        name_gen = haikunator.Haikunator()
        image_response = self.compute_client.images().getFromFamily(project='ubuntu-os-cloud', family='ubuntu-1604-lts').execute()
        startup_script = self.get_startup_script(startup_script_location, username_identifier, username, password_identifier, password)
        server = {
            'name': name_gen.haikunate(),
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
        creation_result = self.compute_client.instances().insert(project = project, zone=zone, body=server).execute()



    def delete_vm(self, project, zone, name):
        return self.compute_client.instances().delete(project=project, zone=zone, instance=name).execute()
    
    def get_startup_script(self, startup_script_location, username_identifier, username, password_identifier, password):
        startup_script_file = open(startup_script_location, "r")
        startup_script = startup_script_file.read()
        startup_script = startup_script.replace(username_identifier, username)
        startup_script = startup_script.replace(password_identifier, password)

        return startup_script

def main():
    proxy_gen = GoogleCloudProxyGen()
    #proxy_gen.create_vm('focal-maker-240918', 'us-east4-c', 'proxystartupscript', 'username', 'testuser', 'password', 'testpass')
    proxy_gen.delete_vm('focal-maker-240918', 'us-east4-c', 'divine-base-8146')

if __name__ == "__main__":
    main()

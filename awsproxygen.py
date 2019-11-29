import boto3
import random
import string
import time
import pytz
import datetime
import base64
import proxymodels
from botocore.exceptions import ClientError

class AWSProxyGen:
    ec2_client = None
    ec2_resource = None

    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.ec2_resource = boto3.resource('ec2')
    
    def cancel_spot_fleet(self, spot_fleet_id):
        cancel_response = self.ec2_client.cancel_spot_fleet_requests(
            DryRun=False,
            SpotFleetRequestIds=[spot_fleet_id],
            TerminateInstances=True
        )

    def generate_random_string(self, string_length):
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(string_length)])
        return random_string

    def create_ec2_instance(self, image_id, instance_type, keypair_name, tags):
        try:
            response = self.ec2_client.run_instances(ImageId = image_id,
                                                     InstanceType = instance_type,
                                                     MinCount = 1,
                                                     MaxCount = 1,
                                                     TagSpecifications = tags,
                                                )
        except Exception as e:
            print(e)
            return None
        return response['Instances'][0]

    def create_on_demand_proxies(self, proxy_count, tags):
        proxies = []
        for x in range(proxy_count):
            # Assign these values before running the program
            image_id = 'ami-080fe8964dffb2222'
            instance_type = 't3.nano'
            keypair_name = 'KEYPAIR_NAME'

            # Provision and launch the EC2 instance
            instance_info = create_ec2_instance(image_id, instance_type, keypair_name, tags)
            
            # sleep to allow instance to get public ip
            time.sleep(1)
            instance = self.ec2_resource.Instance(instance_info["InstanceId"])
            proxies.append(instance.public_ip_address + ':80:pwbo:pwbo')
        
        return proxies

    def get_startup_script(self, startup_script_location, username_identifier, username, password_identifier, password):
        startup_script_file = open(startup_script_location, "r")
        startup_script = startup_script_file.read()
        startup_script = startup_script.replace(username_identifier, username)
        startup_script = startup_script.replace(password_identifier, password)

        return startup_script
    
    def create_security_group(self, security_group_name):
        vpc_response = self.ec2_client.describe_vpcs()
        vpc_id = vpc_response['Vpcs'][0]['VpcId']
        security_group_creation_result = self.ec2_client.create_security_group(GroupName=security_group_name, Description="proxy port 80", VpcId=vpc_id)
        security_group_id = security_group_creation_result['GroupId']
        security_group_rules = self.ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
            ]
        )

        return security_group_id

    def create_spot_instance_proxies(self, proxy_list_name, proxy_count, startup_script_location, startup_script_username_identifier, proxy_username, startup_script_password_identifier, proxy_password, security_group_id, security_group_name):
        spot_fleet_response = self.ec2_client.request_spot_fleet(
            DryRun=False,
            SpotFleetRequestConfig={
                'AllocationStrategy': 'lowestPrice',
                'OnDemandAllocationStrategy': 'lowestPrice',
                'ClientToken': self.generate_random_string(63),
                'ExcessCapacityTerminationPolicy': 'noTermination',
                'OnDemandFulfilledCapacity': 0,
                'IamFleetRole': 'arn:aws:iam::780702615922:role/aws-ec2-spot-fleet-tagging-role',
                'LaunchSpecifications': [
                {
                    'SecurityGroups': [
                        {
                            'GroupId': security_group_id
                        },
                    ],
                    'ImageId': 'ami-04763b3055de4860b',
                    'InstanceType': 't3.nano',
                    'UserData': base64.b64encode(self.get_startup_script(startup_script_location, startup_script_username_identifier, proxy_username, startup_script_password_identifier, proxy_password).encode("utf-8")).decode("utf-8"),
                    'TagSpecifications': [
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': 'list_name',
                                    'Value': proxy_list_name
                                },
                            ]
                        },
                    ]
                },
                ],
                'TargetCapacity': proxy_count,
                'OnDemandTargetCapacity': 0,
                'TerminateInstancesWithExpiration': True,
                'Type': 'request',
                'ReplaceUnhealthyInstances': False,
                'InstanceInterruptionBehavior': 'terminate',
                'InstancePoolsToUseCount': 11
            }
        )

        return spot_fleet_response
    def wait_for_spot_fleet_fulfillment(self, request_id):
        fulfilled = False
        while(fulfilled == False):
            fleet_description = self.ec2_client.describe_spot_fleet_requests(
                DryRun=False,
                SpotFleetRequestIds=[
                    request_id,
                ]
            )
            if(fleet_description['SpotFleetRequestConfigs'][0]['ActivityStatus'] == 'fulfilled'):
                fulfilled = True
            else:
                time.sleep(15)
        return fulfilled
    def get_spot_instance_ip(self, request_id, instance_count):
        ip_list = []
        instance_id = []
        instance_description = self.ec2_client.describe_spot_fleet_instances(
            DryRun = False,
            MaxResults = 1000,
            SpotFleetRequestId = request_id
        )
        for x in range(len(instance_description['ActiveInstances'])):
            instance_id.append(instance_description['ActiveInstances'][x]['InstanceId'])
        while 'NextToken' in instance_description:
            token = instance_description['NextToken']
            instanceDescription = self.ec2_client.describe_spot_fleet_instances(
                DryRun = False,
                MaxResults = 1000,
                NextToken = token,
                SpotFleetRequestId=request_id
            )
            for x in range(len(instanceDescription['ActiveInstances'])):
                instance_id.append(instanceDescription['ActiveInstances'][x]['InstanceId'])
        for x in range(len(instance_id)):
            instances = self.ec2_client.describe_instances (
                Filters=[
                    {
                        'Name': 'tag:aws:ec2spot:fleet-request-id',
                        'Values': [
                            request_id,
                        ]
                    },
                ],
                InstanceIds=[
                    instance_id[x],
                ],
                DryRun=False,
            )
            ip_list.append(instances['Reservations'][0]['Instances'][0]['PublicIpAddress'])

        return ip_list

    def get_security_group_id(self, security_group_name):
        security_group_response = self.ec2_client.describe_security_groups(GroupNames=[security_group_name])
        security_group_id = security_group_response['SecurityGroups'][0]['GroupId']
        
        return security_group_id
    
    def create_proxies(self, proxy_list_name, proxy_count, proxy_username, proxy_password):
        proxies = []
        try:
            security_group_id = self.create_security_group("simple-sneaker-tools-proxy-security-group")
        except ClientError as e:
            security_group_id = self.get_security_group_id("simple-sneaker-tools-proxy-security-group")
        
        spot_fleet_id = self.create_spot_instance_proxies(proxy_list_name, proxy_count, 'proxystartupscript', 'username', proxy_username, 'password', proxy_password, security_group_id, "simple-sneaker-tools-proxy-security-group")['SpotFleetRequestId']
        time.sleep(15)
        self.wait_for_spot_fleet_fulfillment(spot_fleet_id)
        ip_list = self.get_spot_instance_ip(spot_fleet_id, proxy_count)
        for x in ip_list:
            proxies.append(proxymodels.AWSProxy(x, 80, proxy_username, proxy_password, spot_fleet_id))
        
        return proxies

def main():
    proxy_gen = AWSProxyGen()
    proxy_count = int(input("How many proxies would you like to create: "))
    proxy_list_name = input("What do you want to name this proxy list: ")
    proxies = proxy_gen.create_proxies(proxy_list_name, proxy_count, 'testing', 'passtest')
    print(proxies)

if __name__ == "__main__":
    main()
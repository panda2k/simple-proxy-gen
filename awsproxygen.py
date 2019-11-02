import boto3
import random
import string
import time
import pytz
import datetime

class AWSProxyGen:
    ec2_client = None
    ec2_resource = None

    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.ec2_resource = boto3.resource('ec2')
    
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

    def create_spot_instance_proxies(self, proxy_count, proxy_expiration_time):
        spot_fleet_response = self.ec2_client.request_spot_fleet(
            DryRun=False,
            SpotFleetRequestConfig={
                'AllocationStrategy': 'lowestPrice',
                'OnDemandAllocationStrategy': 'lowestPrice',
                'ClientToken': self.generate_random_string(63),
                'ExcessCapacityTerminationPolicy': 'noTermination',
                'OnDemandFulfilledCapacity': 0,
                'IamFleetRole': 'arn:aws:iam::780702615922:role/aws-ec2-spot-fleet-tagging-role',
                'LaunchTemplateConfigs': [
                    {
                        'LaunchTemplateSpecification': {
                            'LaunchTemplateId': 'lt-07089b53d5d06678f',
                            'Version': '2'
                        },
                        'Overrides': [
                            {
                                'InstanceType': 't3.nano'
                            },
                        ]
                    },
                ],
                'TargetCapacity': proxy_count,
                'OnDemandTargetCapacity': 0,
                'TerminateInstancesWithExpiration': True,
                'Type': 'request',
                'ValidUntil': proxy_expiration_time,
                'ReplaceUnhealthyInstances': False,
                'InstanceInterruptionBehavior': 'terminate',
                'InstancePoolsToUseCount': 11
            }
        )

        return spot_fleet_response
    def wait_for_spot_fleet_fulfillment(self, request_id):
        fulfilled = False
        while(fulfilled == False):
            fleetDescription = self.ec2_client.describe_spot_fleet_requests(
                DryRun=False,
                SpotFleetRequestIds=[
                    request_id,
                ]
            )
            if(fleetDescription['SpotFleetRequestConfigs'][0]['ActivityStatus'] == 'fulfilled'):
                fulfilled = True
                print('Spot fleet ' + request_id + ' is now fulfilled')
            else:
                print('Spot fleet ' + request_id + ' not yet fulfilled')
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
        print(instance_id)
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

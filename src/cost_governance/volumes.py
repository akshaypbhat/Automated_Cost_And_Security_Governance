import boto3
 
def check_unattached_volumes():
    ec2 = boto3.client('ec2')
    
    # 1. Fetch all volumes in the region
    response = ec2.describe_volumes()
    
    unattached_volumes = []
    
    # 2. Loop through and find volumes with status 'available'
    for volume in response['Volumes']:
        if volume['State'] == 'available':
            unattached_volumes.append({
                'VolumeId': volume['VolumeId'],
                'SizeGb': volume['Size'],
                'AvailabilityZone': volume['AvailabilityZone']
            })
            
    return unattached_volumes
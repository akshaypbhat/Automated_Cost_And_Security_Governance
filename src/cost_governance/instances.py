import boto3
from datetime import datetime, timedelta
 
def check_idle_instances():
    ec2 = boto3.client('ec2')
    cw = boto3.client('cloudwatch')
    
    now = datetime.utcnow()
    six_months_ago = now - timedelta(days=180)
    
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    idle_instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Handle the CostException tag
            is_exempt = False
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'CostException' and tag['Value'] == 'Approved':
                    is_exempt = True
                    break
            
            if is_exempt:
                continue

            # Skip if the instance is less than 3 days old
            age = datetime.utcnow() - instance['LaunchTime'].replace(tzinfo=None)
            if age.days < 0: #Need to change this value
                continue
                
            # Fetch 6-month CPU metrics from CloudWatch
            metric = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=six_months_ago,
                EndTime=now,
                Period=86400,  # 1 day in seconds
                Statistics=['Maximum']
            )
            
            # Analyze data points
            datapoints = metric.get('Datapoints', [])
            if datapoints:
                # Find the highest CPU spike out of all the daily maximums
                max_cpu = max([d['Maximum'] for d in datapoints])
                
                # If it never spiked above 5%, it's idle
                if max_cpu < 5.0:
                    idle_instances.append({
                        'InstanceId': instance_id,
                        'MaxCpu': round(max_cpu, 2),
                        'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d')
                    })
                    
    return idle_instances
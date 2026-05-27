import boto3

def check_orphaned_snapshots():
    ec2 = boto3.client('ec2')

    # Get all active volume ids
    volume_resp = ec2.describe_volumes()
    active_volumes = [vol['VolumeId'] for vol in volume_resp['Volumes']]

    # Get all snapshots
    snapshot_resp = ec2.describe_snapshots(OwnerIds=['self'])

    orphened_snapshots =[]

    # Find the orphened snapshots
    for snap in snapshot_resp['Snapshots']:
        vol_id = snap.get('VolumeId')

        #If the volume ID isn't active, its an orphen
        if vol_id not in active_volumes:
            orphened_snapshots.append({
                'SnapshotId' : snap['SnapshotId'],
                'VolumeId' : vol_id,
                'SizeGb' : snap.get('VolumeSize'),
                'Description' : snap.get('Description','No description')
            })
    return orphened_snapshots
import boto3

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2_client = boto3.client('ec2')
    
    try:
        # Fetch all snapshots owned by the AWS account
        snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
        
        # Get a list of active volumes
        active_volumes = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['in-use']}])['Volumes']
        
        # Collect all volume IDs in use
        active_volume_ids = {volume['VolumeId'] for volume in active_volumes}
        
        # Identify unused snapshots
        unused_snapshots = [
            snapshot for snapshot in snapshots
            if snapshot['VolumeId'] not in active_volume_ids
        ]
        
        # Delete unused snapshots
        for snapshot in unused_snapshots:
            snapshot_id = snapshot['SnapshotId']
            try:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot: {snapshot_id}")
            except Exception as e:
                print(f"Error deleting snapshot {snapshot_id}: {e}")
        
        return {
            'statusCode': 200,
            'body': f"Deleted {len(unused_snapshots)} unused snapshots."
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Error occurred: {e}"
        }

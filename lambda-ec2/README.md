### Prerequisites
1. `IAM Role for Lambda`: Attach an IAM policy that allows the required permissions.
2. `Trigger`: Configure the Lambda function to run on a schedule using Amazon EventBridge.


### Lambda Function Code
```
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
```
### Explanation

1. `describe_snapshots`: Retrieves all snapshots owned by your account.
2. `describe_volumes`: Lists all active EBS volumes that are in use.
3. `Filter Active Volumes`: Creates a set of volume IDs that are actively associated with EC2 instances.
4. `Identify Unused Snapshots`: Compares the VolumeId of each snapshot to the list of active volumes.
5. `Delete Unused Snapshots`: Iterates through unused snapshots and deletes them.

### IAM Policy Example

Attach the following policy to your Lambda function's role:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSnapshots",
                "ec2:DescribeVolumes",
                "ec2:DeleteSnapshot"
            ],
            "Resource": "*"
        }
    ]
}
```
### Scheduling the Lambda Function

Use EventBridge to schedule the Lambda function. Example rule:

* `Rate-based`: Every day at midnight (rate(1 day)).
* `Cron-based`: Adjust to your needs (cron(0 0 * * ? *)).
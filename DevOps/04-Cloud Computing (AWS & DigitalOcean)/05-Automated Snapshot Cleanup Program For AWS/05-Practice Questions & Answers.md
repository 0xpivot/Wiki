---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain why automated snapshot cleanup is necessary in an AWS environment.**

Automated snapshot cleanup is necessary in an AWS environment to manage storage costs and prevent unnecessary accumulation of data. Without cleanup, daily snapshots can lead to a large number of snapshots over time, increasing storage usage and associated costs. By retaining only the most recent snapshots, organizations can ensure they have access to the latest data while minimizing storage expenses.

**Q2. How would you configure a Python program to clean up old snapshots in AWS, ensuring only the latest two snapshots are retained for each volume?**

To configure a Python program to clean up old snapshots in AWS, ensuring only the latest two snapshots are retained for each volume, follow these steps:

1. Import the necessary libraries (`boto3` and `operator`).
2. Create an EC2 client for the desired region.
3. List all snapshots owned by your account using the `describe_snapshots` method with the `OwnerIds` parameter set to `self`.
4. Filter the snapshots by volume ID to handle multiple volumes.
5. Sort the snapshots by their creation time (`StartTime`) in descending order.
6. Iterate through the sorted list of snapshots, skipping the first two (most recent) and deleting the rest.

Here’s a sample code snippet:

```python
import boto3
from operator import itemgetter

def cleanup_snapshots():
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    
    # Get all volumes tagged with 'prod'
    volumes_response = ec2.describe_volumes(Filters=[{'Name': 'tag:Name', 'Values': ['prod']}])
    volumes = volumes_response['Volumes']
    
    for volume in volumes:
        volume_id = volume['VolumeId']
        
        # List snapshots for this volume
        snapshots_response = ec2.describe_snapshots(
            OwnerIds=['self'],
            Filters=[{'Name': 'volume-id', 'Values': [volume_id]}]
        )
        snapshots = snapshots_response['Snapshots']
        
        # Sort snapshots by creation time in descending order
        sorted_snapshots = sorted(snapshots, key=itemgetter('StartTime'), reverse=True)
        
        # Delete all but the latest two snapshots
        for snapshot in sorted_snapshots[2:]:
            snapshot_id = snapshot['SnapshotId']
            ec2.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted snapshot {snapshot_id}")

cleanup_snapshots()
```

**Q3. Why is it important to filter snapshots by volume ID when managing multiple volumes?**

Filtering snapshots by volume ID is crucial when managing multiple volumes because it ensures that the cleanup process is applied correctly to each individual volume. Without filtering, the cleanup process might inadvertently delete snapshots that belong to different volumes, leading to data loss or incomplete backups. By filtering snapshots by volume ID, the program can accurately identify and manage snapshots for each volume separately, maintaining the integrity of the backup system.

**Q4. How would you schedule the automated snapshot cleanup program to run periodically in AWS?**

To schedule the automated snapshot cleanup program to run periodically in AWS, you can use AWS Lambda and CloudWatch Events. Here’s how you can set it up:

1. Package your Python script into a deployment package.
2. Create an AWS Lambda function and upload the deployment package.
3. Configure the Lambda function to have the necessary permissions to interact with EC2 resources.
4. Set up a CloudWatch Event rule to trigger the Lambda function at the desired interval (e.g., weekly or monthly).

Here’s a sample setup:

1. **Create a Lambda Function:**
   - Go to the AWS Lambda console.
   - Click "Create function."
   - Choose "Author from scratch," enter a function name, and select the appropriate runtime (Python 3.x).
   - Under "Permissions," choose "Use an existing role" and select a role with the necessary permissions (e.g., `AWSLambdaBasicExecutionRole`).

2. **Upload Deployment Package:**
   - Click "Upload from" and select "Local file."
   - Upload your zipped deployment package containing the Python script.

3. **Set Up CloudWatch Event Rule:**
   - Go to the CloudWatch console.
   - Click "Rules" under "Events."
   - Click "Create rule."
   - Select "Schedule" as the event source.
   - Define the schedule expression (e.g., `rate(1 week)` for weekly execution).
   - Under "Targets," click "Add target" and select the Lambda function you created.
   - Click "Configure details," enter a name and description, and click "Create rule."

By following these steps, you can ensure that the automated snapshot cleanup program runs periodically, maintaining optimal storage usage and cost management.

**Q5. Explain how the `itemgetter` function from the `operator` module is used to sort a list of dictionaries in Python.**

The `itemgetter` function from the `operator` module is used to extract a particular item from a sequence such as a dictionary. When sorting a list of dictionaries, `itemgetter` allows you to specify the key by which to sort the dictionaries.

For example, consider a list of dictionaries representing snapshots, where each dictionary contains a `StartTime` key. To sort this list by the `StartTime` key in descending order, you can use `itemgetter` as follows:

```python
from operator import itemgetter

# Sample list of dictionaries
snapshots = [
    {'SnapshotId': 'snap-1', 'StartTime': '2023-01-01T10:00:00Z'},
    {'SnapshotId': 'snap-2', 'StartTime': '2023-01-02T11:00:00Z'},
    {'SnapshotId': 'snap-3', 'StartTime': '2023-01-03T12:00:00Z'}
]

# Sort the list by the 'StartTime' key in descending order
sorted_snapshots = sorted(snapshots, key=itemgetter('StartTime'), reverse=True)

print(sorted_snapshots)
```

In this example, `itemgetter('StartTime')` creates a callable that extracts the `StartTime` value from each dictionary. The `sorted` function uses this callable to sort the list of dictionaries based on the `StartTime` values. The `reverse=True` parameter ensures that the list is sorted in descending order.

---
<!-- nav -->
[[04-Automated Snapshot Cleanup Program for AWS|Automated Snapshot Cleanup Program for AWS]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/05-Automated Snapshot Cleanup Program For AWS/00-Overview|Overview]]

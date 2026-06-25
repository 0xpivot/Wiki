---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the concept of volumes in AWS EC2 and how they relate to EC2 instances.**

Volumes in AWS EC2 are storage components that store the data of an EC2 instance. Each EC2 instance has its own volume, similar to a hard drive, which is automatically created and attached when the instance is launched. When an EC2 instance is deleted, the associated volume is also deleted. This means that the volume contains all the data written by the EC2 instance during its lifetime.

**Q2. How do volume snapshots work in AWS EC2, and why are they important?**

Volume snapshots in AWS EC2 are copies of the volume at a specific point in time. They capture the entire state of the volume, providing a backup that can be used to restore data in case of data corruption or loss. Snapshots are crucial for ensuring data availability and recovery, especially in scenarios where multiple EC2 instances need regular backups to prevent data loss.

**Q3. Write a Python script using the Boto3 library to automate the creation of daily snapshots for EC2 volumes.**

```python
import boto3
from datetime import datetime

def create_snapshots():
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    
    # Get all volumes
    volumes = ec2.describe_volumes()['Volumes']
    
    for volume in volumes:
        volume_id = volume['VolumeId']
        
        # Create a snapshot
        snapshot = ec2.create_snapshot(VolumeId=volume_id)
        
        # Tag the snapshot with a description
        snapshot_id = snapshot['SnapshotId']
        ec2.create_tags(
            Resources=[snapshot_id],
            Tags=[
                {'Key': 'Name', 'Value': f'{volume_id}_snapshot_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'}
            ]
        )
        
        print(f'Snapshot {snapshot_id} created for Volume {volume_id}')

# Schedule the function to run daily
import schedule
import time

schedule.every().day.at("02:00").do(create_snapshots)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Q4. How can you filter volumes to create snapshots only for production servers in AWS EC2?**

To filter volumes and create snapshots only for production servers, you can use the `describe_volumes` method with a filter that matches the tag `Name` with the value `prod`. Here’s an example:

```python
import boto3

def create_production_snapshots():
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    
    # Filter volumes with Name tag set to prod
    volumes = ec2.describe_volumes(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['prod']}
        ]
    )['Volumes']
    
    for volume in volumes:
        volume_id = volume['VolumeId']
        
        # Create a snapshot
        snapshot = ec2.create_snapshot(VolumeId=volume_id)
        
        # Tag the snapshot with a description
        snapshot_id = snapshot['SnapshotId']
        ec2.create_tags(
            Resources=[snapshot_id],
            Tags=[
                {'Key': 'Name', 'Value': f'{volume_id}_prod_snapshot_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'}
            ]
        )
        
        print(f'Snapshot {snapshot_id} created for Production Volume {volume_id}')

create_production_snapshots()
```

**Q5. Discuss recent real-world examples where automated backups could have prevented data loss.**

Automated backups can significantly mitigate the risk of data loss. For instance, in the case of the Capital One data breach in 2019 (CVE-2019-11510), automated backups could have helped restore services quickly and minimize the impact of the breach. By having regular backups, the company could have restored the system to a known good state before the breach occurred, reducing downtime and restoring trust among customers.

**Q6. How would you configure a Python script to handle errors and retries when creating snapshots?**

To handle errors and retries, you can use try-except blocks and implement retry logic using a loop. Here’s an example:

```python
import boto3
from botocore.exceptions import ClientError

def create_snapshot_with_retry(volume_id):
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            snapshot = ec2.create_snapshot(VolumeId=volume_id)
            snapshot_id = snapshot['SnapshotId']
            print(f'Snapshot {snapshot_id} created for Volume {volume_id}')
            return snapshot_id
        except ClientError as e:
            if attempt < max_retries - 1:
                print(f'Attempt {attempt + 1} failed. Retrying...')
            else:
                print(f'Failed to create snapshot after {max_retries} attempts.')
                raise e

def create_snapshots_with_retry():
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    volumes = ec2.describe_volumes()['Volumes']
    
    for volume in volumes:
        volume_id = volume['VolumeId']
        create_snapshot_with_retry(volume_id)

create_snapshots_with_retry()
```

This script includes error handling and retry logic to ensure that snapshot creation is robust against transient issues.

---
<!-- nav -->
[[10-Understanding Snapshots|Understanding Snapshots]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]]

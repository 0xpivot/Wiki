---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating EC2 Instance Backups with Python

### Background Theory

Automating backups is crucial for maintaining data integrity and availability. By automating the process, you ensure that backups are taken regularly and consistently, reducing the risk of human error. Python is a popular choice for automation due to its simplicity and powerful libraries.

### Prerequisites

Before diving into the code, ensure you have the following prerequisites:

1. **AWS Account**: You need an AWS account with appropriate permissions to manage EC2 instances and volumes.
2. **Python Environment**: Set up a Python environment with the necessary libraries installed.
3. **AWS SDK for Python (Boto3)**: Install the `boto3` library, which allows you to interact with AWS services programmatically.

### Installing Boto3

To install `boto3`, use the following command:

```bash
pip install boto3
```

### Setting Up AWS Credentials

To authenticate with AWS, you need to set up your AWS credentials. You can do this by configuring the `~/.aws/credentials` file or by setting environment variables.

#### Configuring `~/.aws/credentials`

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

#### Setting Environment Variables

```bash
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
```

### Writing the Python Script

Now, let's write a Python script to automate the creation of snapshots for EC2 instance volumes.

#### Step-by-Step Code Explanation

1. **Import Libraries**:
   Import the necessary libraries (`boto3` and `datetime`).

2. **Initialize Boto3 Client**:
   Initialize the `boto3` client for EC2.

3. **Get EC2 Instances**:
   Retrieve a list of EC2 instances.

4. **Iterate Over Instances**:
   Iterate over each instance to get its volumes.

5. **Create Snapshots**:
   Create a snapshot for each volume.

6. **Tag Snapshots**:
   Tag the snapshots with relevant metadata.

Here is the complete Python script:

```python
import boto3
from datetime import datetime

# Initialize the Boto3 client for EC2
ec2_client = boto3.client('ec2')

def create_snapshots():
    # Get a list of all EC2 instances
    instances_response = ec2_client.describe_instances()
    
    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Get the volumes attached to the instance
            volumes = [volume for volume in instance.get('BlockDeviceMappings', []) if 'Ebs' in volume]
            
            for volume in volumes:
                volume_id = volume['Ebs']['VolumeId']
                
                # Create a snapshot of the volume
                snapshot_response = ec2_client.create_snapshot(
                    VolumeId=volume_id,
                    Description=f'Snapshot for {instance_id} - {volume_id}'
                )
                
                snapshot_id = snapshot_response['SnapshotId']
                
                # Tag the snapshot with relevant metadata
                ec2_client.create_tags(
                    Resources=[snapshot_id],
                    Tags=[
                        {'Key': 'Name', 'Value': f'{instance_id}-{volume_id}'},
                        {'Key': 'InstanceID', 'Value': instance_id},
                        {'Key': 'VolumeID', 'Value': volume_id},
                        {'Key': 'CreatedOn', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    ]
                )
                
                print(f'Snapshot created: {snapshot_id}')

if __name__ == '__main__':
    create_snapshots()
```

### Full HTTP Request and Response Example

While the above script does not involve HTTP requests directly, you can use the AWS CLI to manually create a snapshot and observe the HTTP request and response. Here is an example using the AWS CLI:

#### Creating a Snapshot via AWS CLI

```bash
aws ec2 create-snapshot --volume-id vol-0abcdef1234567890 --description "Backup for instance i-0123456789abcdef0"
```

#### Full HTTP Request

```http
POST / HTTP/1.1
Host: ec2.us-west-2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231010/us-west-2/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=0000000000000000000000000000000000000000000000000000000000000000
X-Amz-Date: 20231010T193642Z
Content-Length: 100

Action=CreateSnapshot&Version=2016-11-15&VolumeId=vol-0abcdef1234567890&Description=Backup%20for%20instance%20i-0123456789abcdef0
```

#### Full HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 475
Date: Tue, 10 Oct 2023 19:36:42 GMT
Server: AmazonEC2

<?xml version="1.0" encoding="UTF-8"?>
<CreateSnapshotResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <snapshotId>snap-0abcdef1234567890</snapshotId>
</CreateSnapshotResponse>
```

### Common Pitfalls and How to Avoid Them

1. **Permissions Issues**: Ensure that your AWS credentials have the necessary permissions to create snapshots and tag resources.
2. **Volume Not Found**: Verify that the volume IDs are correct and that the volumes exist.
3. **Rate Limiting**: Be aware of AWS rate limits when creating multiple snapshots in quick succession.

### How to Prevent / Defend

#### Detection

Regularly monitor your AWS environment for any unauthorized changes or deletions. Use AWS CloudTrail to log API calls and monitor for suspicious activity.

#### Prevention

1. **IAM Policies**: Implement strict IAM policies to limit access to sensitive operations like creating and deleting snapshots.
2. **Multi-Factor Authentication (MFA)**: Enable MFA for your AWS account to add an extra layer of security.
3. **Scheduled Backups**: Use AWS Lambda and CloudWatch Events to schedule regular backups automatically.

#### Secure Coding Fixes

Compare the vulnerable code snippet with the secure version:

##### Vulnerable Code

```python
# Vulnerable code: Missing error handling and logging
def create_snapshots():
    instances_response = ec2_client.describe_instances()
    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            volumes = [volume for volume in instance.get('BlockDeviceMappings', []) if 'Ebs' in volume]
            for volume in volumes:
                volume_id = volume['Ebs']['VolumeId']
                snapshot_response = ec2_client.create_snapshot(VolumeId=volume_id)
                snapshot_id = snapshot_response['SnapshotId']
                print(f'Snapshot created: {snapshot_id}')
```

##### Secure Code

```python
# Secure code: Added error handling and logging
import logging

logging.basicConfig(level=logging.INFO)

def create_snapshots():
    try:
        instances_response = ec2_client.describe_instances()
        for reservation in instances_response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                volumes = [volume for volume in instance.get('BlockDeviceMappings', []) if 'Ebs' in volume]
                for volume in volumes:
                    volume_id = volume['Ebs']['VolumeId']
                    try:
                        snapshot_response = ec2_client.create_snapshot(VolumeId=volume_id)
                        snapshot_id = snapshot_response['SnapshotId']
                        logging.info(f'Snapshot created: {snapshot_id}')
                    except Exception as e:
                        logging.error(f'Failed to create snapshot for volume {volume_id}: {str(e)}')
    except Exception as e:
        logging.error(f'Error retrieving instances: {str(e)}')
```

### Configuration Hardening

1. **Enable Encryption**: Ensure that all snapshots are encrypted using AWS Key Management Service (KMS).
2. **Use IAM Roles**: Instead of using individual AWS credentials, use IAM roles to grant permissions to EC2 instances.

### Practice Labs

For hands-on practice with automating EC2 instance backups, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on AWS security practices.
- **OWASP Juice Shop**: While primarily a web application security lab, it can be extended to include AWS security exercises.
- **CloudGoat**: Provides a series of labs focused on AWS security, including EC2 instance management and backup strategies.

By following these steps and practicing with real-world scenarios, you can ensure that your EC2 instances are backed up regularly and securely.

---
<!-- nav -->
[[03-Automating Backups Using Python|Automating Backups Using Python]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]] | [[05-Automating the Backup Process|Automating the Backup Process]]

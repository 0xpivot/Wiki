---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## EC2 Instance Management

### What is an EC2 Instance?

An Amazon Elastic Compute Cloud (EC2) instance is a virtual server in the cloud. EC2 instances are the building blocks of many applications and services hosted on AWS.

### Why Manage EC2 Instances Programmatically?

Managing EC2 instances programmatically using Python allows you to automate tasks such as starting, stopping, and monitoring instances. This ensures consistency and reduces the risk of manual errors.

### Checking the Status of EC2 Instances

Here’s an example of how to check the status of EC2 instances using `boto3`:

```python
import boto3

# Create an EC2 client
ec2 = boto3.client('ec2')

# Describe instances
response = ec2.describe_instance_status()

# Print instance statuses
for instance in response['InstanceStatuses']:
    print(f"Instance ID: {instance['InstanceId']}, Status: {instance['InstanceState']['Name']}")
```

### Adding Text to EC2 Servers

You can use SSH to add text to EC2 servers. Here’s an example using the `paramiko` library:

```python
import paramiko

# Connect to the EC2 instance
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='your_ec2_public_ip', username='ubuntu', key_filename='/path/to/private/key.pem')

# Add text to a file
stdin, stdout, stderr = ssh.exec_command('echo "Hello, World!" > /home/ubuntu/hello.txt')

# Close the connection
ssh.close()
```

### Creating Automated Backups for EC2 Volumes

Here’s an example of how to create automated backups for EC2 volumes using `boto3`:

```python
import boto3

# Create an EC2 client
ec2 = boto3.client('ec2')

# Create a snapshot
snapshot_response = ec2.create_snapshot(VolumeId='vol-0123456789abcdef0')
snapshot_id = snapshot_response['SnapshotId']

print(f"Created Snapshot with ID: {snapshot_id}")
```

### Restoring an EC2 Volume from Backup

Here’s an example of how to restore an EC2 volume from a backup using `boto3`:

```python
# Restore the volume from the snapshot
volume_response = ec2.restore_volume_from_snapshot(SnapshotId=snapshot_id)
volume_id = volume_response['VolumeId']

print(f"Restored Volume with ID: {volume_id}")
```

### Common Pitfalls and How to Avoid Them

1. **SSH Key Management**: Ensure that your SSH keys are stored securely. Use IAM roles instead of hardcoding private keys whenever possible.
2. **Backup Retention**: Define a retention policy for your snapshots to avoid unnecessary storage costs.
3. **Security Groups**: Configure security groups to allow only necessary inbound and outbound traffic.

### How to Prevent / Defend

1. **Use IAM Roles**: Use IAM roles to grant permissions to your EC2 instance management scripts. This ensures that the scripts run with the minimum necessary privileges.
2. **Enable CloudWatch Monitoring**: Enable CloudWatch monitoring to track the health and performance of your EC2 instances.
3. **Regular Audits**: Regularly audit your EC2 configurations to ensure compliance with your organization's security policies.

---
<!-- nav -->
[[03-Comparing boto3 with Terraform|Comparing boto3 with Terraform]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/13-Python Automation for DevOps Use Cases/00-Overview|Overview]] | [[05-Getting Familiar with boto3|Getting Familiar with boto3]]

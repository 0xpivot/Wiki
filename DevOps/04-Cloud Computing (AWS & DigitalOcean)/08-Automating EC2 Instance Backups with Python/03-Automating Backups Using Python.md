---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating Backups Using Python

Now that we have our EC2 instances set up, let's proceed with automating the backup process using Python. We will use the Boto3 library, which is the AWS SDK for Python, to interact with AWS services programmatically.

### Prerequisites

Before writing the Python script, ensure you have the following prerequisites:

1. **Python Installed**: Ensure Python is installed on your local machine or server.
2. **Boto3 Installed**: Install the Boto3 library using pip:
    ```bash
    pip install boto3
    ```
3. **AWS CLI Configured**: Configure the AWS CLI with your credentials:
    ```bash
    aws configure
    ```

### Writing the Python Script

Let's write a Python script to create snapshots of the EBS volumes attached to our EC2 instances.

```python
import boto3
from datetime import datetime

def create_snapshot(volume_id, description):
    ec2 = boto3.resource('ec2')
    snapshot = ec2.create_snapshot(VolumeId=volume_id, Description=description)
    print(f"Snapshot created for Volume {volume_id}: {snapshot.id}")

def main():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:name', 'Values': ['dev', 'prod']}]
    )

    for instance in instances:
        for volume in instance.volumes.all():
            description = f"Automated Snapshot for {instance.tags[0]['Value']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            create_snapshot(volume.id, description)

if __name__ == "__main__":
    main()
```

### Explanation of the Script

1. **Import Libraries**: Import the necessary libraries (`boto3` and `datetime`).
2. **Create Snapshot Function**: Define a function `create_snapshot` that takes `volume_id` and `description` as parameters and creates a snapshot using Boto3.
3. **Main Function**: Define the `main` function to filter EC2 instances based on tags (`dev` and `prod`). Iterate through each instance and its attached volumes, and call the `create_snapshot` function for each volume.
4. **Execution**: Execute the script to create snapshots for the specified instances.

### Running the Script

To run the script, save it to a file (e.g., `backup_ec2.py`) and execute it using Python:

```bash
python backup_ec2.py
```

This will create snapshots for the EBS volumes attached to the tagged EC2 instances.

---
<!-- nav -->
[[02-Introduction to EC2 Instance Backups|Introduction to EC2 Instance Backups]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]] | [[04-Automating EC2 Instance Backups with Python|Automating EC2 Instance Backups with Python]]

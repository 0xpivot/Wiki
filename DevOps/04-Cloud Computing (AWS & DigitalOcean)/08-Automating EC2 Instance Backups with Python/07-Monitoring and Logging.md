---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Monitoring and Logging

To ensure the backup process is working correctly, it is essential to monitor and log the results. The script already includes basic logging by printing the snapshot IDs. For more detailed monitoring, consider integrating with AWS CloudWatch Logs or a third-party logging service.

### Example of CloudWatch Integration

1. **Install the AWS SDK for Python**:
    ```bash
    pip install boto3
    ```
2. **Modify the Script to Log to CloudWatch**:
    ```python
    import boto3
    from datetime import datetime

    def create_snapshot(volume_id, description):
        ec2 = boto3.resource('ec2')
        client = boto3.client('logs')
        log_group_name = '/aws/lambda/EC2Backup'
        log_stream_name = 'backup-stream'

        try:
            client.create_log_group(logGroupName=log_group_name)
        except Exception as e:
            pass

        try:
            client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        except Exception as e:
            pass

        sequence_token = None
        events = [
            {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'message': f"Creating snapshot for Volume {volume_id}..."
            }
        ]

        response = client.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=events,
            sequenceToken=sequence_token
        )

        snapshot = ec2.create_snapshot(VolumeId=volume_id, Description=description)
        print(f"Snapshot created for Volume {volume_id}: {snapshot.id}")
        events.append({
            'timestamp': int(datetime.now().timestamp() * 1000),
            'message': f"Snapshot created for Volume {volume_id}: {snapshot.id}"
        })

        client.put_log_events(
            logGroupName=log_group
```
assistant

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/06-How to Prevent  Defend|How to Prevent  Defend]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/08-Automating EC2 Instance Backups with Python/00-Overview|Overview]] | [[08-Setting Up the Environment|Setting Up the Environment]]

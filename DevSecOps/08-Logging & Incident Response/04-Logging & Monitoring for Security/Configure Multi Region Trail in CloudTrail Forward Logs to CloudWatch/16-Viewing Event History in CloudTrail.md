---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Viewing Event History in CloudTrail

Once the trail is configured, you can view the event history in the CloudTrail console. This includes actions such as creating an instance, attaching a security group, and terminating an instance.

### Step-by-Step Viewing

1. **Navigate to CloudTrail Console**:
    - Open the AWS Management Console.
    - Navigate to the CloudTrail service.

2. **View Event History**:
    - Click on "Event history".
    - Filter by date range and specific events.

3. **Switch Between Regions**:
    - Use the region selector to view events in different regions.

### Example of Event History

Here’s an example of event history entries:

```json
{
  "eventVersion": "1.05",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "<principal-id>",
    "arn": "arn:aws:iam::<account-id>:user/admin",
    "accountId": "<account-id>",
    "accessKeyId": "<access-key-id>",
    "userName": "admin"
  },
  "eventTime": "2023-10-01T12:00:00Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "RunInstances",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "123.45.67.89",
  "userAgent": "aws-cli/2.10.0 Python/3.8.10 Linux/5.4.0-106-generic botocore/2.10.0",
  "requestParameters": {
    "imageId": "ami-0abcdef1234567890",
    "instanceType": "t2.micro",
    "maxCount": 1,
    "minCount": 1
  },
  "responseElements": {
    "instancesSet": {
      "items": [
        {
          "instanceId": "i-0abcdef1234567890",
          "imageId": "ami-0abcdef1234567890",
          "instanceState": {
            "code": 0,
            "name": "pending"
          },
          "instanceType": "t2.micro",
          "placement": {
            "availabilityZone": "us-east-1a",
            "tenancy": "default"
          }
        }
      ]
    }
  },
  "requestID": "12345678-1234-1234-1234-1234567890ab",
  "eventID": "12345678-1234-1234-1234-1234567890ab",
  "readOnly": false,
  "resources": [],
  "sharedEventID": "",
  "vpcEndpointId": ""
}
```

### Filtering Events

You can filter events by various criteria, such as event name, user identity, and AWS region. For example, to filter by console login events:

1. **Filter by Event Name**:
    - Use the filter option to select "ConsoleLogin".

2. **List and Filter Events**:
    - List all console login events and filter by specific users or time ranges.

### Example of Filtering Console Login Events

Here’s an example of filtering console login events:

```json
{
  "eventVersion": "1.05",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "<principal-id>",
    "arn": "arn:aws:iam::<account-id>:user/admin",
    "accountId": "<account-id>",
    "accessKeyId": "<access-key-id>",
    "userName": "admin"
  },
  "eventTime": "2023-10-01T12:00:00Z",
  "eventSource": "signin.amazonaws.com",
  "eventName": "ConsoleLogin",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "123.45.67.89",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "requestParameters": {},
  "responseElements": {
    "ConsoleLogin": "Success"
  },
  "requestID": "12345678-1234-1234-1234-1234567890ab",
  "eventID": "12345678-1234-1234-1234-1234567890ab",
  "readOnly": true,
  "resources": [],
  "sharedEventID": "",
  "vpcEndpointId": ""
}
```

### Analyzing Events

By analyzing these events, you can gain insights into who is accessing your AWS environment and what actions they are performing. This information can be used to detect potential security threats and take proactive measures.

---
<!-- nav -->
[[15-Logging and Monitoring for Security in DevSecOps|Logging and Monitoring for Security in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Multi Region Trail in CloudTrail Forward Logs to CloudWatch/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Multi Region Trail in CloudTrail Forward Logs to CloudWatch/17-Conclusion|Conclusion]]

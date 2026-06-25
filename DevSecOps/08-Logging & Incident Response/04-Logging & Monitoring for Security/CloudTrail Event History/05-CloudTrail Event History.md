---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## CloudTrail Event History

### Introduction to CloudTrail

CloudTrail is a vital component of AWS's logging and monitoring capabilities. It captures API calls made to your AWS account and delivers them to you as log files. These logs provide a comprehensive view of the actions taken within your AWS environment, including who performed the actions, when they were performed, and which resources were involved. This information is crucial for auditing, compliance, and security purposes.

### Understanding CloudTrail Logs

#### Instance IDs and Actions

When you examine CloudTrail logs, one of the key pieces of information you will encounter is the instance ID. Each instance ID corresponds to an EC2 instance that performed an action within your AWS account. This means that not only human users but also other AWS resources can perform actions. For example, an EC2 instance might connect to another AWS resource and execute certain tasks.

**Example:**
```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROAJDPLRKEXAMPLE:example-session-name",
    "arn": "arn:aws:sts::123456789012:assumed-role/EC2InstanceProfile/example-session-name",
    "accountId": "123456789012",
    "sessionContext": {
      "attributes": {
        "mfaAuthenticated": false,
        "creationDate": "2023-01-01T00:00:00Z"
      }
    }
  },
  "eventTime": "2023-01-01T00:00:00Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "RunInstances",
  "awsRegion": "eu-west-3",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "ec2.amazonaws.com",
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
          "instanceId": "i-0abcdef1234567890"
        }
      ]
    }
  },
  "requestID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "eventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "readOnly": false,
  "resources": [
    {
      "ARN": "arn:aws:ec2:eu-west-3:123456789012:instance/i-0abcdef1234567890",
      "accountId": "123456789012",
      "type": "AWS::EC2::Instance"
    }
  ],
  "sharedEventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "vpcEndpointId": "vpce-0abcdef1234567890"
}
```

In this example, the `userIdentity` field shows that the action was performed by an assumed role (`AssumedRole`). The `eventSource` indicates that the action was related to EC2, and the `eventName` specifies that the action was `RunInstances`. The `responseElements` field includes the instance ID (`i-0abcdef1234567890`) that was created as a result of this action.

### User Agent Information

Another important piece of information in CloudTrail logs is the user agent. The user agent provides details about the software or tool that initiated the action. This can help you understand whether the action was performed via a browser, command-line interface, SDK, or other tools.

**Example:**
```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDPLRKLG7UEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin",
    "sessionContext": {
      "attributes": {
        "mfaAuthenticated": true,
        "creationDate": "2023-01-01T00:00:00Z"
      }
    }
  },
  "eventTime": "2023-01-01T00:00:00Z",
  "eventSource": "ssm.amazonaws.com",
  "eventName": "SendCommand",
  "awsRegion": "eu-west-3",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "AmazonSSM-Agent/2.3.1005.0",
  "requestParameters": {
    "documentName": "AWS-RunShellScript",
    "parameters": {
      "commands": ["echo 'Hello, World!'"]
    },
    "targets": [
      {
        "key": "tag:Environment",
        "values": ["Production"]
      }
    ]
  },
  "responseElements": {},
  "requestID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "eventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "readOnly": false,
  "resources": [],
  "sharedEventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "vpcEndpointId": "vpce-0abcdef1234567890"
}
```

In this example, the `userAgent` field indicates that the action was performed using the `AmazonSSM-Agent/2.3.1005.0`. This helps you understand that the action was initiated by the SSM agent on an EC2 instance.

### Detailed Log Analysis

To gain deeper insights into the actions performed within your AWS environment, you can analyze the detailed logs provided by CloudTrail. These logs contain extensive information about each action, including the user identity, event time, event source, event name, and other relevant parameters.

**Example:**
```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDPLRKLG7UEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin",
    "sessionContext": {
      "attributes": {
        "mfaAuthenticated": true,
        "creationDate": "2023-01-01T00:00:00Z"
      }
    }
  },
  "eventTime": "2023-01-01T00:00:00Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "DescribeInstances",
  "awsRegion": "eu-west-3",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "aws-sdk-java/2.17.100 Linux/5.4.0-103-generic Java/11.0.11",
  "requestParameters": {
    "filters": [
      {
        "name": "instance-state-name",
        "values": ["running"]
      }
    ]
  },
  "responseElements": {
    "reservationSet": [
      {
        "ownerId": "123456789012",
        "reservationId": "r-0abcdef1234567890",
        "instancesSet": {
          "items": [
            {
              "instanceId": "i-0abcdef1234567890",
              "imageId": "ami-0abcdef1234567890",
              "instanceState": {
                "code": 16,
                "name": "running"
              },
              "privateIpAddress": "10.0.0.1",
              "publicIpAddress": "192.0.2.1",
              "instanceType": "t2.micro",
              "launchTime": "2023-01-01T00:00:00Z",
              "placement": {
                "availabilityZone": "eu-west-3a"
              },
              "subnetId": "subnet-0abcdef1234567890",
              "vpcId": "vpc-0abcdef1234567890",
              "monitoring": {
                "state": "disabled"
              },
              "tags": [
                {
                  "key": "Name",
                  "value": "my-instance"
                }
              ]
            }
          ]
        }
      }
    ]
  },
  "requestID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "eventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "readOnly": true,
  "resources": [
    {
      "ARN": "arn:aws:ec2:eu-west-3:123456789012:instance/i-0abcdef1234567890",
      "accountId": "123456789012",
      "type": "AWS::EC2::Instance"
    }
  ],
  "sharedEventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "vpcEndpointId": "vpce-0abcdef1234567890"
}
```

In this example, the `eventName` is `DescribeInstances`, which means that the action was to describe the instances in the AWS account. The `requestParameters` field includes filters used to specify the criteria for the instances to be described. The `responseElements` field contains detailed information about the instances, including their instance ID, image ID, state, IP addresses, and tags.

### Regional Activity

It is important to note that CloudTrail logs are specific to a particular region. In the example provided, all the activity was recorded in the Paris region (`eu-west-3`). This means that the logs only capture actions performed within that region.

**Example:**
```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDPLRKLG7UEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin",
    "sessionContext": {
      "attributes": {
        "mfaAuthenticated": true,
        "creationDate": "2023-01-01T00:00:00Z"
      }
    }
  },
  "eventTime": "2023-01-01T00:00:00Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "CreateVolume",
  "awsRegion": "eu-west-3",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "aws-sdk-java/2.17.100 Linux/5.4.0-103-generic Java/11.0.11",
  "requestParameters": {
    "size": 10,
    "volumeType": "gp2",
    "availabilityZone": "eu-west-3a"
  },
  "responseElements": {
    "volumeId": "vol-0abcdef1234567890"
  },
  "requestID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "eventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "readOnly": false,
  "resources": [
    {
      "ARN": "arn:aws:ec2:eu-west-3:123456789012:volume/vol-0abcdef1234567890",
      "accountId": "123456789012",
      "type": "AWS::EC2::Volume"
    }
  ],
  "sharedEventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "vpcEndpointId": "vpce-0abcdef1234567890"
}
```

In this example, the `eventName` is `CreateVolume`, which means that the action was to create a volume in the AWS account. The `requestParameters` field includes the size, volume type, and availability zone of the volume. The `responseElements` field contains the volume ID that was created as a result of this action.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of proper logging and monitoring. For example, the SolarWinds breach in 2020 demonstrated the critical need for comprehensive logging and monitoring capabilities. By analyzing logs, organizations can identify unauthorized access, unusual activity, and potential security threats.

**Example:**
- **CVE-2020-1014**: This vulnerability in SolarWinds Orion allowed attackers to compromise the software and gain unauthorized access to networks. Proper logging and monitoring could have helped detect and mitigate such attacks.

### How to Prevent / Defend

#### Detection

To effectively detect unauthorized or suspicious activity, you should implement robust logging and monitoring practices. This includes:

1. **Enable CloudTrail**: Ensure that CloudTrail is enabled for all regions and services in your AWS account.
2. **Monitor Logs**: Regularly review CloudTrail logs to identify any unauthorized or suspicious activity.
3. **Use CloudWatch**: Integrate CloudTrail with CloudWatch to set up alerts for specific events or patterns.

**Example:**
```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDPLRKLG7UEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin",
    "sessionContext": {
      "attributes": {
        "mfaAuthenticated": true,
        "creationDate": "2023-01-01T00:00:00Z"
      }
    }
  },
  "eventTime": "2023-01-01T00:00:00Z",
  "eventSource": "iam.amazonaws.com",
  "eventName": "CreateAccessKey",
  "awsRegion": "eu-west-3",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "aws-sdk-java/2.17.100 Linux/5.4.0-103-generic Java/11.0.11",
  "requestParameters": {
    "userName": "admin"
  },
  "responseElements": {
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "secretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  },
  "requestID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "eventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "readOnly": false,
  "resources": [
    {
      "ARN": "arn:aws:iam::123456789012:user/admin",
      "accountId": "123456789012",
      "type": "AWS::IAM::User"
    }
  ],
  "sharedEventID": "abcd1234-abcd-1234-abcd-1234abcd1234",
  "vpcEndpointId": "vpce-0abcdef1234567890"
}
```

In this example, the `eventName` is `CreateAccessKey`, which means that an access key was created for the `admin` user. This could be a sign of unauthorized activity, especially if the user did not expect to create an access key.

#### Prevention

To prevent unauthorized access and ensure the security of your AWS environment, you should:

1. **Enable Multi-Factor Authentication (MFA)**: Require MFA for all IAM users to add an extra layer of security.
2. **Limit Permissions**: Use least privilege principles to limit permissions for IAM roles and users.
3. **Regular Audits**: Conduct regular audits of IAM policies and roles to ensure they are up-to-date and secure.

**Example:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes"
      ],
      "Resource": "*"
    }
  ]
}
```

In this example, the IAM policy allows the user to describe instances and volumes but does not grant any additional permissions. This ensures that the user has only the necessary permissions to perform their tasks.

### Secure Coding Practices

To ensure that your applications and infrastructure are secure, you should follow secure coding practices. This includes:

1. **Input Validation**: Validate all input to prevent injection attacks.
2. **Error Handling**: Implement proper error handling to avoid exposing sensitive information.
3. **Secure Configuration**: Ensure that all configurations are secure and up-to-date.

**Example:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Deny",
      "Action": [
        "iam:*"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

In this example, the IAM policy denies all IAM actions if MFA is not present. This ensures that only users with MFA enabled can perform IAM actions.

### Hands-On Labs

To practice and reinforce your understanding of CloudTrail and logging, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: This lab provides a comprehensive set of exercises to learn about web security, including logging and monitoring.
- **OWASP Juice Shop**: This lab simulates a vulnerable web application, allowing you to practice identifying and mitigating security issues.
- **DVWA (Damn Vulnerable Web Application)**: This lab provides a vulnerable web application to practice security testing and mitigation techniques.
- **WebGoat**: This lab provides a series of lessons to learn about web security, including logging and monitoring.

By completing these labs, you can gain practical experience in implementing and managing CloudTrail and other logging and monitoring tools.

### Conclusion

CloudTrail is a powerful tool for logging and monitoring activities within your AWS environment. By understanding and utilizing CloudTrail effectively, you can enhance the security and compliance of your AWS infrastructure. Regularly reviewing logs, enabling MFA, and following secure coding practices are essential steps to ensure the security of your environment.

---
<!-- nav -->
[[04-CloudTrail Event History Part 2|CloudTrail Event History Part 2]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/06-Practice Questions & Answers|Practice Questions & Answers]]

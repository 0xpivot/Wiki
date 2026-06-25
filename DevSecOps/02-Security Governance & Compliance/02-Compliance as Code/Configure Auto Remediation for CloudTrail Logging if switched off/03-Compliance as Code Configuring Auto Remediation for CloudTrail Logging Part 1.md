---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Compliance as Code: Configuring Auto Remediation for CloudTrail Logging

### Introduction to Compliance as Code

Compliance as Code is an approach to automating compliance checks and remediations within a cloud environment. This method leverages infrastructure-as-code (IaC) principles to ensure that systems adhere to regulatory requirements and internal policies. One critical aspect of compliance is ensuring that logging mechanisms, such as AWS CloudTrail, remain active and configured correctly.

### Understanding CloudTrail

AWS CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It provides a history of API calls made within your AWS account, including API calls made via the AWS Management Console, AWS SDKs, command-line tools, and other AWS services. CloudTrail captures API calls at the account level and delivers log files to an Amazon S3 bucket.

#### Why CloudTrail Matters

CloudTrail is essential for several reasons:

1. **Auditability**: It helps in tracking who performed what actions, when, and from which IP address.
2. **Security Monitoring**: It allows you to monitor and respond to unauthorized activities.
3. **Compliance**: Many regulations require logging and monitoring of system activity, and CloudTrail helps meet these requirements.

### Enabling CloudTrail Logging

To ensure that CloudTrail logging remains active, you can configure auto-remediation scripts that automatically re-enable CloudTrail if it is turned off. This process involves creating IAM roles and policies that grant the necessary permissions to perform these actions.

#### Creating an IAM Role for Auto Remediation

First, you need to create an IAM role that will be used by the auto-remediation scripts. This role should have permissions to execute Systems Manager (SSM) commands and manage CloudTrail settings.

```yaml
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudtrail:StartLogging",
                "cloudtrail:GetTrailStatus"
            ],
            "Resource": "arn:aws:cloudtrail:*:*:trail/*"
        }
    ]
}
```

### Configuring Auto Remediation

Once the IAM role is set up, you can configure the auto-remediation script to check if CloudTrail is enabled and re-enable it if necessary.

#### Example Auto Remediation Script

Here is an example of a Python script that uses the Boto3 library to interact with AWS services and re-enable CloudTrail if it is disabled.

```python
import boto3

def check_cloudtrail_status():
    client = boto3.client('cloudtrail')
    trails = client.describe_trails()['trailList']
    
    for trail in trails:
        trail_arn = trail['TrailARN']
        status = client.get_trail_status(TrailArn=trail_arn)
        
        if not status['IsLogging']:
            print(f"CloudTrail {trail_arn} is not logging. Re-enabling...")
            client.start_logging(Name=trail['Name'])
            print("CloudTrail logging re-enabled.")
        else:
            print(f"CloudTrail {trail_arn} is already logging.")

if __name__ == "__main__":
    check_cloudtrail_status()
```

### Automating the Script Execution

To automate the execution of this script, you can use AWS Lambda or AWS Systems Manager (SSM) to run the script periodically. Here’s an example using AWS Lambda:

1. **Create a Lambda Function**:
   - Write the Python script and package it along with any dependencies.
   - Upload the package to AWS Lambda.
   - Assign the IAM role created earlier to the Lambda function.

2. **Configure a CloudWatch Event Rule**:
   - Create a CloudWatch event rule to trigger the Lambda function at regular intervals (e.g., every hour).

### Ensuring Proper Permissions

It is crucial to ensure that the IAM role used by the auto-remediation script has the necessary permissions to re-enable CloudTrail. The policy should include the following actions:

- `cloudtrail:StartLogging`: To start logging for a trail.
- `cloudtrail:GetTrailStatus`: To check the current status of a trail.

#### Example IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudtrail:StartLogging",
                "cloudtrail:GetTrailStatus"
            ],
            "Resource": "arn:aws:cloudtrail:*:*:trail/*"
        }
    ]
}
```

### Testing and Validation

After configuring the auto-remediation script, it is important to test and validate that it works as expected. You can simulate a scenario where CloudTrail is turned off and verify that the script re-enables it.

#### Example Test Scenario

1. **Disable CloudTrail**:
   - Manually disable CloudTrail logging through the AWS Management Console or API.
   
2. **Run the Auto Remediation Script**:
   - Execute the script and verify that CloudTrail logging is re-enabled.

### Real-World Examples and Breaches

Recent breaches and vulnerabilities have highlighted the importance of maintaining proper logging and monitoring. For instance, the Capital One breach in 2019 involved unauthorized access to customer data. Proper logging and monitoring could have helped detect and mitigate the breach more quickly.

### How to Prevent / Defend

#### Detection

To detect if CloudTrail logging is disabled, you can use AWS Config rules or CloudWatch events to monitor the status of CloudTrail trails.

#### Prevention

Ensure that IAM roles and policies are properly configured to allow the necessary permissions for auto-remediation scripts. Regularly review and audit IAM roles and policies to ensure they are up-to-date and secure.

#### Secure Coding Fixes

Compare the insecure and secure versions of the IAM policy and script to understand the differences.

##### Insecure Version

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        }
    ]
}
```

##### Secure Version

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudtrail:StartLogging",
                "cloudtrail:GetTrailStatus"
            ],
            "Resource": "arn:aws:cloudtrail:*:*:trail/*"
        }
    ]
}
```

### Conclusion

By implementing auto-remediation scripts and ensuring proper permissions, you can maintain compliance and security in your AWS environment. Regular testing and validation are essential to ensure that these mechanisms work as intended.

### Practice Labs

For hands-on practice with compliance as code and auto-remediation, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on securing cloud environments and implementing compliance controls.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice securing cloud services.
- **AWS Well-Architected Labs**: Includes labs focused on implementing and maintaining compliance in AWS environments.

These resources will help you gain practical experience in configuring and maintaining compliance as code in your cloud environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for CloudTrail Logging if switched off/02-Compliance as Code Auto Remediation for CloudTrail Logging|Compliance as Code Auto Remediation for CloudTrail Logging]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for CloudTrail Logging if switched off/00-Overview|Overview]] | [[04-Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 2|Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 2]]

---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Compliance as Code: Configuring Auto Remediation for CloudTrail Logging

### Background Theory

Compliance as Code is an approach to ensuring that infrastructure and applications adhere to regulatory requirements and internal policies through automated checks and remediations. In the context of AWS, this often involves using AWS Config to monitor and enforce compliance rules across your resources. One critical aspect of compliance is ensuring that CloudTrail logging is enabled and functioning correctly, as it provides a detailed record of API calls made within your AWS environment.

### Why CloudTrail Logging Matters

CloudTrail logging is essential for several reasons:

1. **Auditability**: It allows you to track who performed actions in your AWS account, which services were used, and when these actions occurred.
2. **Security Monitoring**: By monitoring CloudTrail logs, you can detect unauthorized access attempts, unusual activity, and potential security breaches.
3. **Compliance**: Many regulatory frameworks require logging and auditing capabilities to ensure that operations are transparent and traceable.

### How CloudTrail Works

CloudTrail captures API calls made to your AWS account and delivers log files to an Amazon S3 bucket. These log files contain detailed information about the API calls, including the identity of the API caller, the time of the call, the source IP address, and the request parameters.

#### Enabling CloudTrail

To enable CloudTrail, you typically configure it via the AWS Management Console, AWS CLI, or AWS SDKs. Here’s an example of enabling CloudTrail using the AWS CLI:

```bash
aws cloudtrail create-trail --name MyCloudTrail --s3-bucket-name my-logs-bucket --include-global-service-events
```

This command creates a new CloudTrail trail named `MyCloudTrail` and specifies an S3 bucket (`my-logs-bucket`) where the log files will be stored.

### AWS Config and Auto Remediation

AWS Config is a service that continuously monitors and records configurations and changes to your AWS resources. You can define rules to check whether your resources comply with specific criteria. If a resource does not meet the criteria, AWS Config can automatically remediate the issue.

#### Configuring Auto Remediation for CloudTrail

To configure auto-remediation for CloudTrail logging, you first need to define a rule that checks if CloudTrail is enabled and logging correctly. Then, you can set up a remediation action to enable CloudTrail if it is disabled.

Here’s a step-by-step guide to setting this up:

1. **Define the Rule**:
   Create a rule in AWS Config that checks if CloudTrail is enabled and logging correctly. This can be done via the AWS Management Console or AWS CLI.

   ```bash
   aws configservice put-config-rule --config-rule-name "CloudTrailEnabledRule" --source '{"owner': 'AWS', 'sourceIdentifier': 'CLOUD_TRAIL_ENABLED'}'
   ```

2. **Configure Remediation Action**:
   Set up a remediation action that enables CloudTrail if it is disabled. This can be done using AWS Systems Manager Automation documents.

   ```yaml
   ---
   description: Enable CloudTrail if disabled
   schemaVersion: '0.3'
   assumeRole: arn:aws:iam::123456789012:role/AutomationServiceRole
   mainSteps:
     - name: CheckCloudTrailStatus
       action: aws:runCommand
       inputs:
         DocumentName: "AWS-RunShellScript"
         InstanceIds: ["i-0123456789abcdef0"]
         Parameters:
           commands:
             - aws cloudtrail describe-trails --query 'trailList[?IsLogging==`false`].Name'
     - name: EnableCloudTrail
       action: aws:runCommand
       precondition:
         StringEquals:
           - "CheckCloudTrailStatus.Output": "[]"
       inputs:
         DocumentName: "AWS-RunShellScript"
         InstanceIds: ["i-0123456789abcdef0"]
         Parameters:
           commands:
             - aws cloudtrail start-logging --name MyCloudTrail
   ```

3. **Trigger Re-evaluation**:
   Once the rule and remediation action are set up, you can trigger a re-evaluation to check the current status of CloudTrail.

   ```bash
   aws configservice start-config-rules-evaluation --config-rule-names "CloudTrailEnabledRule"
   ```

### Example Scenario

Let’s walk through an example scenario where CloudTrail is initially disabled, and then we trigger a re-evaluation to ensure it becomes compliant again.

#### Initial State

Assume CloudTrail is disabled. You can verify this by checking the status of CloudTrail trails:

```bash
aws cloudtrail describe-trails --query 'trailList[?IsLogging==`false`].Name'
```

If CloudTrail is disabled, the output will show the name of the trail that is not logging.

#### Trigger Re-evaluation

Now, trigger a re-evaluation of the rule:

```bash
aws configservice start-config-rules-evaluation --config-rule-names "CloudTrailEnabledRule"
```

After some time, the rule will re-evaluate the status of CloudTrail and trigger the remediation action if necessary.

#### Post-Re-evaluation

Once the re-evaluation is complete, check the status of CloudTrail again:

```bash
aws cloudtrail describe-trails --query 'trailList[?IsLogging==`true`].Name'
```

If the remediation was successful, the output will show the name of the trail that is now logging.

### Common Pitfalls and Best Practices

#### Pitfalls

1. **Incorrect Configuration**: Ensure that the rule and remediation action are correctly configured. Incorrect configurations can lead to false positives or failures in remediation.
2. **Permissions Issues**: Make sure that the IAM roles and permissions are correctly set up to allow AWS Config and Systems Manager to perform the necessary actions.
3. **Resource Dependencies**: Ensure that there are no dependencies that could prevent the remediation action from completing successfully.

#### Best Practices

1. **Regular Audits**: Regularly audit your AWS Config rules and remediation actions to ensure they remain effective.
2. **Testing**: Test your remediation actions in a non-production environment to ensure they work as expected.
3. **Documentation**: Maintain thorough documentation of your compliance rules and remediation actions to ensure that others can understand and maintain them.

### Real-World Examples

#### Recent Breaches and CVEs

In recent years, several high-profile breaches have been linked to misconfigured CloudTrail settings. For example, the Capital One breach in 2019 involved unauthorized access to sensitive data due to misconfigured AWS security groups and CloudTrail settings. Ensuring that CloudTrail is properly configured and monitored can help prevent such incidents.

### How to Prevent / Defend

#### Detection

To detect issues with CloudTrail logging, you can set up monitoring and alerting using AWS CloudWatch Events and AWS Lambda. For example, you can create a CloudWatch Event rule that triggers a Lambda function whenever CloudTrail logging is disabled.

```json
{
  "source": [
    "aws.config"
  ],
  "detail-type": [
    "Config Rules Compliance Change"
  ],
  "detail": {
    "configRuleName": [
      "CloudTrailEnabledRule"
    ],
    "newEvaluationResult": {
      "complianceType": [
        "NON_COMPLIANT"
      ]
    }
  }
}
```

The Lambda function can then take appropriate action, such as sending an alert or triggering a remediation action.

#### Prevention

To prevent issues with CloudTrail logging, follow these steps:

1. **Enable CloudTrail**: Ensure that CloudTrail is enabled and logging correctly.
2. **Set Up Auto Remediation**: Configure AWS Config and Systems Manager to automatically remediate issues with CloudTrail logging.
3. **Monitor and Alert**: Use CloudWatch Events and Lambda to monitor and alert on any issues with CloudTrail logging.

#### Secure-Coding Fixes

Here’s an example of a vulnerable configuration versus a secure configuration:

**Vulnerable Configuration**:
```json
{
  "trail": {
    "Name": "MyCloudTrail",
    "S3BucketName": "my-logs-bucket",
    "IncludeGlobalServiceEvents": false,
    "IsMultiRegionTrail": false
  }
}
```

**Secure Configuration**:
```json
{
  "trail": {
    "Name": "MyCloudTrail",
    "S3BucketName": "my-logs-bucket",
    "IncludeGlobalServiceEvents": true,
    "IsMultiRegionTrail": true
  }
}
```

### Complete Example

#### Full HTTP Request and Response

Here’s an example of a full HTTP request and response for enabling CloudTrail:

**Request**:
```http
POST /cloudtrail/start-logging HTTP/1.1
Host: cloudtrail.amazonaws.com
Content-Type: application/x-amz-json-1.1
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/cloudtrail/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5f356c689a4e6e274dc021bebbd9b8f9b97f9bb0ba1eb113b6f42c593908de
X-Amz-Date: 20150101T000000Z

{
  "Name": "MyCloudTrail"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890ab
Date: Thu, 01 Jan 2015 00:00:00 GMT

{}
```

### Diagrams

#### Mermaid Diagram: CloudTrail Configuration Flow

```mermaid
sequenceDiagram
  participant User
  participant AWS_Config
  participant CloudTrail
  participant S3_Bucket

  User->>AWS_Config: Define CloudTrail Enabled Rule
  AWS_Config->>CloudTrail: Check CloudTrail Status
  CloudTrail-->>AWS_Config: Return Status
  alt CloudTrail Disabled
    AWS_Config->>User: Notify Non-Compliance
    User->>AWS_Config: Trigger Remediation
    AWS_Config->>CloudTrail: Enable CloudTrail
    CloudTrail-->>AWS_Config: Confirm Enabled
  else CloudTrail Enabled
    AWS_Config-->>User: Notify Compliant
  end
  CloudTrail->>S3_Bucket: Log API Calls
```

### Practice Labs

For hands-on practice with Compliance as Code and CloudTrail logging, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to web application security, including compliance and logging.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and compliance.
- **CloudGoat**: Provides a series of labs focused on AWS security and compliance, including CloudTrail configuration and monitoring.

By following these steps and best practices, you can ensure that your AWS environment remains compliant and secure through automated monitoring and remediation.

---
<!-- nav -->
[[03-Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 1|Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for CloudTrail Logging if switched off/00-Overview|Overview]] | [[05-Compliance as Code Configuring Auto Remediation for CloudTrail Logging|Compliance as Code Configuring Auto Remediation for CloudTrail Logging]]

---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Introduction to Logging and Monitoring Security Events

In the realm of DevSecOps, logging and monitoring security events are critical components for maintaining the integrity and confidentiality of systems and data. This chapter delves into the specifics of defining key security events to log and monitor, focusing on a practical example using AWS services such as S3 buckets, AWS Config rules, and SNS topics. By the end of this chapter, you will understand the importance of these practices, how to implement them effectively, and how to defend against potential misconfigurations that could lead to data breaches.

### Background Theory

#### What Are Security Events?

Security events are significant occurrences within a system that can indicate potential security issues. These events can range from unauthorized access attempts to changes in system configurations. Logging and monitoring these events help in detecting and responding to security threats promptly.

#### Why Log and Monitor Security Events?

Logging and monitoring security events are essential for several reasons:

1. **Detection**: They enable the identification of suspicious activities or anomalies that might indicate a security breach.
2. **Compliance**: Many regulatory requirements mandate logging and monitoring certain types of events to ensure compliance.
3. **Incident Response**: Detailed logs provide crucial information for forensic analysis during incident response.
4. **Audit Trails**: Logs serve as audit trails, helping to trace actions taken by users and systems.

### Real-World Examples

Recent breaches and vulnerabilities highlight the importance of proper logging and monitoring:

- **CVE-2021-26855**: A misconfiguration in AWS S3 buckets led to the exposure of sensitive data. Proper logging and monitoring could have detected this misconfiguration earlier.
- **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack involved unauthorized access to systems. Comprehensive logging and monitoring would have helped in detecting and mitigating the attack sooner.

### Prerequisites for the Demo

Before diving into the demo, ensure you have the following prerequisites:

1. **AWS Account**: You need an active AWS account.
2. **Admin Access**: You should have administrative privileges to create and manage resources.
3. **Basic Knowledge of AWS Services**: Familiarity with S3, AWS Config, and SNS is beneficial but not mandatory.

### Step-by-Step Demo

#### Creating an S3 Bucket

1. **Log in to the AWS Console**:
    - Open your web browser and navigate to the AWS Management Console.
    - Enter your credentials to log in.

2. **Create an S3 Bucket**:
    - Navigate to the S3 service in the AWS Management Console.
    - Click on "Create bucket".
    - Provide a unique name for your bucket.
    - Select the region where you want to create the bucket.
    - Configure additional settings as needed (e.g., versioning, encryption).

```mermaid
sequenceDiagram
    participant User
    participant AWSConsole
    participant S3Service
    User->>AWSConsole: Log in
    AWSConsole->>User: Welcome
    User->>AWSConsole: Navigate to S3
    AWSConsole->>User: S3 Dashboard
    User->>S3Service: Create bucket
    S3Service->>User: Bucket created
```

#### Configuring an AWS Config Rule

1. **Navigate to AWS Config**:
    - In the AWS Management Console, go to the "Services" menu and select "Config".

2. **Create a New Rule**:
    - Click on "Rules" and then "Create rule".
    - Choose a rule type (e.g., "S3 bucket public access").
    - Configure the rule parameters as needed.
    - Enable the rule.

```mermaid
sequenceDiagram
    participant User
    participant AWSConsole
    participant ConfigService
    User->>AWSConsole: Navigate to Config
    AWSConsole->>User: Config Dashboard
    User->>ConfigService: Create new rule
    ConfigService->>User: Rule created
```

#### Creating an SNS Topic and Subscription

1. **Navigate to SNS**:
    - In the AWS Management Console, go to the "Services" menu and select "SNS".

2. **Create a New Topic**:
    - Click on "Topics" and then "Create topic".
    - Provide a name for your topic.
    - Configure additional settings as needed.

3. **Create a Subscription**:
    - Click on "Subscriptions" and then "Create subscription".
    - Select the topic you created.
    - Choose a protocol (e.g., email, SMS).
    - Provide the endpoint (e.g., email address).

```mermaid
sequenceDiagram
    participant User
    participant AWSConsole
    participant SNSService
    User->>AWSConsole: Navigate to SNS
    AWSConsole->>User: SNS Dashboard
    User->>SNSService: Create new topic
    SNSService->>User: Topic created
    User->>SNSService: Create subscription
    SNSService->>User: Subscription created
```

### Complete Example

#### Full HTTP Request and Response

When creating an S3 bucket via the AWS SDK, the process involves making HTTP requests to the AWS API. Here is an example of creating an S3 bucket using the AWS SDK for Python (Boto3):

```python
import boto3

# Initialize the S3 client
s3_client = boto3.client('s3')

# Create a new S3 bucket
response = s3_client.create_bucket(
    Bucket='my-new-bucket',
    CreateBucketConfiguration={
        'LocationConstraint': 'us-west-2'
    }
)

print(response)
```

The corresponding HTTP request and response would look like this:

```http
POST /?Action=CreateBucket&Version=2006-03-01&Bucket=my-new-bucket&LocationConstraint=us-west-2 HTTP/1.1
Host: s3.amazonaws.com
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=fe5f356c79c72b9e5a1c1f7e245e1c919fc34e8ac602e6d8847a9ce24bb174aa
X-Amz-Content-Sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
X-Amz-Date: 20150101T000000Z
Content-Type: application/x-www-form-urlencoded; charset=utf-8

HTTP/1.1 200 OK
Date: Thu, 01 Jan 2015 00:00:00 GMT
Server: AmazonS3
Content-Length: 0
```

### Common Pitfalls and How to Avoid Them

#### Misconfiguration of S3 Buckets

One common pitfall is misconfiguring S3 buckets, which can lead to unauthorized access. To avoid this:

1. **Enable Versioning**: This helps in recovering deleted objects.
2. **Use Bucket Policies**: Define strict policies to control access.
3. **Monitor Changes**: Use AWS Config to monitor changes in bucket configurations.

#### Example of Vulnerable vs. Secure Configuration

**Vulnerable Configuration**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

**Secure Configuration**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SpecificAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:user/my-user"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

### How to Prevent / Defend

#### Detection

1. **Use AWS CloudTrail**: It logs API calls made to your AWS account.
2. **Enable AWS Config**: It tracks changes to your AWS resources.
3. **Set Up Alerts**: Use AWS CloudWatch to set up alerts for specific events.

#### Prevention

1. **Implement Least Privilege**: Ensure users have only the permissions necessary.
2. **Regular Audits**: Conduct regular audits of your configurations.
3. **Automate Compliance Checks**: Use tools like AWS Config Rules to automate compliance checks.

#### Secure Coding Fixes

**Example of Secure Code**:
```python
import boto3

# Initialize the S3 client
s3_client = boto3.client('s3')

# Create a new S3 bucket with versioning enabled
response = s3_client.create_bucket(
    Bucket='my-secure-bucket',
    CreateBucketConfiguration={
        'LocationConstraint': 'us-west-2'
    }
)

# Enable versioning
versioning = s3_client.put_bucket_versioning(
    Bucket='my-secure-bucket',
    VersioningConfiguration={
        'Status': 'Enabled'
    }
)

print(versioning)
```

### Conclusion

Proper logging and monitoring of security events are crucial for maintaining the security of your systems and data. By following the steps outlined in this chapter, you can effectively detect and respond to potential security threats. Regular audits and automated compliance checks further enhance your security posture.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: Provides scenarios for learning AWS security best practices.

By engaging with these labs, you can gain practical experience in implementing and defending against security threats in real-world scenarios.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/04-Demo/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/04-Demo/02-Practice Questions & Answers|Practice Questions & Answers]]

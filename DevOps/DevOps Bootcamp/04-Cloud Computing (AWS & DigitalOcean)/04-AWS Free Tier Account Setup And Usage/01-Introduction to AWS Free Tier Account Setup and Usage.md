---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS Free Tier Account Setup and Usage

### Background Theory

Amazon Web Services (AWS) is a comprehensive and broadly adopted cloud platform, offering over 200 fully featured services from data centers globally. One of the key features that makes AWS accessible to a wide range of users, including students, hobbyists, and small businesses, is the AWS Free Tier. This section will delve into the details of setting up an AWS Free Tier account and how to effectively utilize its resources.

### Setting Up an AWS Free Tier Account

To begin using AWS, you first need to create an account. This process involves filling out several forms, providing personal information such as your address and credit card details. The requirement for a credit card is primarily to verify the authenticity of the user and ensure that the account is registered with valid data. Once you submit the necessary information, AWS will review it and activate your account.

#### Step-by-Step Account Creation

1. **Navigate to AWS Website**: Go to the official AWS website at [aws.amazon.com](https://aws.amazon.com).
2. **Click on Sign Up**: Locate the "Sign Up" button and click on it.
3. **Fill Out Personal Information**: Provide your name, email address, and other required details.
4. **Enter Address Information**: Enter your residential or business address.
5. **Provide Credit Card Details**: Input your credit card information for verification purposes.
6. **Review and Agree to Terms**: Read through the terms and conditions and agree to them.
7. **Complete Verification**: Follow any additional steps for verification, such as confirming your email address.

#### Example of Account Creation Process

```mermaid
sequenceDiagram
    participant User
    participant AWS_Website
    participant AWS_Server
    User->>AWS_Website: Navigate to AWS Website
    AWS_Website-->>User: Display Sign Up Page
    User->>AWS_Website: Fill out Personal Information
    AWS_Website-->>User: Request Address Information
    User->>AWS_Website: Provide Address Information
    AWS_Website-->>User: Request Credit Card Details
    User->>AWS_Website: Provide Credit Card Details
    AWS_Website-->>User: Display Terms and Conditions
    User->>AWS_Website: Agree to Terms and Conditions
    AWS_Website-->>User: Send Verification Email
    User->>AWS_Server: Confirm Email Address
    AWS_Server-->>User: Account Created
```

### Understanding the AWS Free Tier

Once your account is set up, you gain access to the AWS Free Tier. This tier provides a selection of AWS services for free for one year after account registration. The free tier includes:

- **EC2 Instances**: Virtual servers that can be used for computing tasks.
- **Storage Services**: Such as Amazon S3 for storing files.
- **Other Resources**: Various other services that are either free or have limited free usage.

#### Key Components of the Free Tier

1. **EC2 Instances**: These are virtual servers that can be configured with different types of hardware and operating systems. The free tier includes specific types of EC2 instances that can be used for one year.
2. **Amazon S3**: A highly scalable object storage service that allows you to store and retrieve any amount of data at any time.
3. **Always Free Resources**: Certain services like AWS Lambda, Amazon RDS, and others offer a certain level of usage that is always free, regardless of the account age.

#### Example of Free Tier Services

```mermaid
graph LR
    A[Free Tier] --> B[EC2 Instances]
    A --> C[Amazon S3]
    A --> D[Always Free Resources]
    B --> E[T2.micro Instance]
    C --> F[5GB Storage]
    D --> G[Lambda 1M Requests/Month]
    D --> H[RDS 750 Hours/Month]
```

### Utilizing the Free Tier Effectively

When using the AWS Free Tier, it is crucial to understand which resources are free-tier eligible and how to select them. This ensures that you maximize the benefits of the free tier without incurring unexpected charges.

#### Selecting Free-Tier Eligible Resources

1. **EC2 Instances**: When launching an EC2 instance, look for the "Free Tier Eligible" label. This indicates that the instance type is covered under the free tier.
2. **Amazon S3**: Ensure that your S3 bucket usage stays within the free tier limits (typically 5 GB of storage).

#### Example of Launching an EC2 Instance

```mermaid
sequenceDiagram
    participant User
    participant AWS_Console
    participant EC2_Service
    User->>AWS_Console: Log in to AWS Console
    AWS_Console-->>User: Display EC2 Dashboard
    User->>AWS_Console: Click on Launch Instance
    AWS_Console-->>User: Display Instance Types
    User->>AWS_Console: Select Free Tier Eligible Instance
    AWS_Console-->>User: Confirm Selection
    User->>EC2_Service: Launch Instance
    EC2_Service-->>User: Instance Launched
```

#### Full HTTP Request and Response Example

```http
POST /ec2/launchInstance HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/json
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/iam/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f4faa9b...

{
  "ImageId": "ami-0c94855ba95c71c99",
  "InstanceType": "t2.micro",
  "MinCount": 1,
  "MaxCount": 1,
  "KeyName": "my-key-pair",
  "SecurityGroupIds": ["sg-0123456789abcdef0"]
}

HTTP/1.1 200 OK
Content-Type: application/json
Date: Tue, 21 Mar 2023 12:00:00 GMT
Content-Length: 214

{
  "InstanceId": "i-0123456789abcdef0"
}
```

### Common Pitfalls and How to Avoid Them

One of the most common issues with the AWS Free Tier is inadvertently using resources that fall outside the free tier limits. This can lead to unexpected charges. To avoid this, always check the pricing and usage limits of the services you are using.

#### Example of Inadvertent Charges

Suppose you exceed the free tier limit for EC2 instances by running a t2.large instance instead of a t2.micro. This would result in charges being incurred.

#### Secure Coding Practices

Ensure that you always select the correct instance type and monitor your usage to stay within the free tier limits. Use AWS Cost Explorer to track your usage and costs.

#### Vulnerable vs. Secure Code Example

**Vulnerable Code:**
```python
import boto3

def launch_ec2_instance():
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-0c94855ba95c71c99',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.large',  # Incorrect instance type
        KeyName='my-key-pair',
        SecurityGroupIds=['sg-0123456789abcdef0']
    )
    return instance[0].id
```

**Secure Code:**
```python
import boto3

def launch_ec2_instance():
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-0c94855ba95c71c99',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',  # Correct instance type
        KeyName='my-key-pair',
        SecurityGroupIds=['sg-0123456789abcdef0']
    )
    return instance[0].id
```

### How to Prevent / Defend

#### Detection

Use AWS Cost Explorer to monitor your usage and identify any potential overages. Set up budget alerts to notify you when you approach the free tier limits.

#### Prevention

1. **Select Free-Tier Eligible Resources**: Always choose resources that are labeled as free-tier eligible.
2. **Monitor Usage**: Regularly check your usage through the AWS Management Console or Cost Explorer.
3. **Set Budget Alerts**: Configure budget alerts to receive notifications when you are approaching the free tier limits.

#### Secure Configuration Hardening

1. **IAM Policies**: Use IAM policies to restrict access to non-free tier resources.
2. **Resource Tags**: Tag your resources to easily identify and manage free tier usage.
3. **Cost Allocation Tags**: Use cost allocation tags to track and control spending.

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

While AWS itself has not been breached due to the free tier, there have been instances where users inadvertently exceeded their free tier limits and incurred unexpected charges. For example, a user might have launched a larger EC2 instance type without realizing it was not covered under the free tier.

#### Example of a Real-World Scenario

A company launched an EC2 instance with a t2.large type instead of a t2.micro, leading to unexpected charges. By monitoring their usage and selecting the correct instance type, they could have avoided these charges.

### Hands-On Practice Labs

To gain practical experience with AWS Free Tier, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning web security.
- **CloudGoat**: A series of labs designed to help you learn about cloud security on AWS.

These labs provide a safe environment to practice and learn about AWS services and security practices.

### Conclusion

Setting up and utilizing an AWS Free Tier account effectively requires a thorough understanding of the available resources and how to select them. By following the guidelines and best practices outlined in this chapter, you can maximize the benefits of the free tier while avoiding unexpected charges. Regular monitoring and secure coding practices are essential to maintaining a secure and cost-effective AWS environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/04-AWS Free Tier Account Setup And Usage/00-Overview|Overview]] | [[02-AWS Free Tier Account Setup and Usage|AWS Free Tier Account Setup and Usage]]

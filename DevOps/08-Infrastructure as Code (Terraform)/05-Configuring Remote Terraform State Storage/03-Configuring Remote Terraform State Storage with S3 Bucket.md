---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring Remote Terraform State Storage with S3 Bucket

One of the most common remote backends for Terraform is Amazon S3 (Simple Storage Service). S3 is a highly scalable and reliable object storage service provided by AWS.

### What is S3?

Amazon S3 is a cloud-based storage service that allows you to store and retrieve any amount of data at any time. S3 is designed to provide 99.999999999% durability and 99.99% availability of objects over a given year.

### Why use S3 for Terraform state storage?

Using S3 for Terraform state storage is beneficial for several reasons:

1. **Scalability**: S3 can handle large amounts of data and scale automatically.
2. **Durability**: S3 provides high durability and availability, ensuring that your state information is safe.
3. **Integration**: S3 integrates seamlessly with other AWS services, making it easy to manage and monitor your state information.

### How does S3 work under the hood?

S3 stores data as objects in buckets. Each object consists of a key (name), value (data), and metadata. When you configure Terraform to use S3 as a backend, Terraform stores the state information as an object in the specified bucket.

### Example

Here’s an example of a Terraform configuration file with an S3 backend:

```hcl
terraform {
  required_version = ">= 0.12"
  backend "s3" {
    bucket = "my-app-bucket"
    key    = "my-app-state"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}
```

In this example, the `backend` attribute is configured to use an S3 bucket named `my-app-bucket` in the `us-west-2` region.

### Creating the S3 Bucket

Before you can use an S3 bucket as a Terraform backend, you need to create the bucket. Here’s how to create an S3 bucket using the AWS Management Console:

1. Log in to the AWS Management Console.
2. Navigate to the S3 service.
3. Click on the "Create bucket" button.
4. Enter the bucket name (e.g., `my-app-bucket`).
5. Select the region (e.g., `us-west-2`).
6. Configure any additional settings as needed.
7. Click on the "Create" button.

### Example of Creating an S3 Bucket via AWS CLI

Alternatively, you can create the S3 bucket using the AWS CLI:

```sh
aws s3api create-bucket --bucket my-app-bucket --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
```

### Common Mistakes

One common mistake is not creating the S3 bucket before configuring Terraform. This can lead to errors when initializing the backend. Always ensure that the S3 bucket exists before configuring Terraform.

### How to Prevent / Defend

To ensure that your Terraform configurations are secure and consistent:

1. **Create the S3 bucket**: Always create the S3 bucket before configuring Terraform.
2. **Configure permissions**: Ensure that the S3 bucket has the correct permissions to allow Terraform to read and write state information.
3. **Monitor access**: Regularly monitor access to the S3 bucket to detect any unauthorized access.

### Real-World Example: CVE-2021-3539

CVE-2021-3539 is a security vulnerability in AWS S3 that allows unauthorized access to S3 buckets. This vulnerability highlights the importance of securing your S3 buckets and ensuring that they are properly configured.

### Secure Configuration

To secure your S3 bucket, follow these best practices:

1. **Enable versioning**: Enable versioning on your S3 bucket to prevent accidental deletion of objects.
2. **Enable server-side encryption**: Enable server-side encryption to protect your data at rest.
3. **Use IAM policies**: Use IAM policies to restrict access to your S3 bucket.
4. **Enable logging**: Enable logging to monitor access to your S3 bucket.

### Example of Secure Configuration

Here’s an example of a secure S3 bucket configuration using IAM policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessToBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    }
  ]
}
```

In this example, the IAM policy allows access to the S3 bucket for specific actions.

### How to Detect Unauthorized Access

To detect unauthorized access to your S3 bucket, you can use AWS CloudTrail and S3 access logs. CloudTrail logs API calls made to your AWS account, while S3 access logs log all requests made to your S3 bucket.

### Example of CloudTrail and S3 Access Logs

Here’s an example of enabling CloudTrail and S3 access logs:

```sh
# Enable CloudTrail
aws cloudtrail create-trail --name MyCloudTrail --s3-bucket-name my-cloudtrail-bucket --include-global-service-events true

# Enable S3 access logs
aws s3api put-bucket-logging --bucket my-app-bucket --bucket-logging-status '{"LoggingEnabled": {"TargetBucket": "my-s3-access-logs", "TargetPrefix": "my-app-bucket/"}}'
```

### How to Prevent Unauthorized Access

To prevent unauthorized access to your S3 bucket, follow these best practices:

1. **Use IAM roles**: Use IAM roles to restrict access to your S3 bucket.
2. **Enable MFA**: Enable multi-factor authentication (MFA) for your IAM users.
3. **Use VPC endpoints**: Use VPC endpoints to restrict access to your S3 bucket within your VPC.

### Example of IAM Role

Here’s an example of an IAM role that restricts access to your S3 bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessToBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    }
  ]
}
```

In this example, the IAM role allows access to the S3 bucket for specific actions.

### How to Monitor Access

To monitor access to your S3 bucket, you can use AWS CloudWatch and S3 access logs. CloudWatch provides real-time monitoring and alerting, while S3 access logs provide detailed information about all requests made to your S3 bucket.

### Example of CloudWatch and S3 Access Logs

Here’s an example of enabling CloudWatch and S3 access logs:

```sh
# Enable CloudWatch
aws cloudwatch put-metric-alarm --alarm-name MyCloudWatchAlarm --metric-name NumberOfRequests --namespace AWS/S3 --statistic Sum --period 300 --threshold 100 --comparison-operator GreaterThanThreshold --dimensions Name=Bucket,Value=my-app-bucket Name=StorageType,Value=AllStorageTypes --evaluation-periods 1 --alarm-actions arn:aws:sns:us-west-2:123456789012:MySNS

# Enable S3 access logs
aws s3api put-bucket-logging --bucket my-app-bucket --bucket-logging-status '{"LoggingEnabled": {"TargetBucket": "my-s3-access-logs", "TargetPrefix": "my-app-bucket/"}}'
```

### How to Harden Your S3 Bucket

To harden your S3 bucket, follow these best practices:

1. **Enable versioning**: Enable versioning on your S3 bucket to prevent accidental deletion of objects.
2. **Enable server-side encryption**: Enable server-side encryption to protect your data at rest.
3. **Use IAM policies**: Use IAM policies to restrict access to your S3 bucket.
4. **Enable logging**: Enable logging to monitor access to your S3 bucket.

### Example of Hardened S3 Bucket Configuration

Here’s an example of a hardened S3 bucket configuration using IAM policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessToBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    }
  ]
}
```

In this example, the IAM policy allows access to the SS bucket for specific actions.

### Practice Labs

For hands-on practice with configuring Terraform state storage with S3, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve configuring Terraform state storage with S3.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. While not specifically focused on Terraform, it can be used to practice configuring Terraform state storage with S3.
- **DVWA (Damn Vulnerable Web Application)**: Another deliberately insecure web application for security training. Similar to OWASP Juice Shop, it can be used to practice configuring Terraform state storage with S3.

These labs provide a practical way to apply the concepts learned in this chapter and gain hands-on experience with configuring Terraform state storage with S3.

---
<!-- nav -->
[[02-Backend Configuration in Terraform|Backend Configuration in Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/05-Configuring Remote Terraform State Storage/00-Overview|Overview]] | [[04-Configuring Remote Terraform State Storage|Configuring Remote Terraform State Storage]]

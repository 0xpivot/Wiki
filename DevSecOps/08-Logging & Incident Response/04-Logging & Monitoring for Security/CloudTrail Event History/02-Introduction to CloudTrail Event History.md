---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to CloudTrail Event History

### What is CloudTrail?

AWS CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It provides a record of actions taken by a user, role, or an AWS service in your AWS account and in your AWS resources. This includes API calls, management console actions, and CLI commands. CloudTrail captures every API call, regardless of the origin, and stores this information in log files. These log files are delivered to an Amazon S3 bucket that you specify.

### Why Use CloudTrail?

CloudTrail is crucial for several reasons:

1. **Compliance**: Many regulatory requirements mandate logging and auditing of actions performed in cloud environments. CloudTrail helps meet these requirements.
2. **Security Auditing**: By monitoring and recording API calls, you can detect unauthorized or unusual activity, which is essential for maintaining the security of your AWS environment.
3. **Operational Auditing**: CloudTrail logs provide a comprehensive audit trail that can help you understand how your AWS resources are being used and managed.

### How Does CloudTrail Work?

CloudTrail works by capturing API calls made to your AWS account and delivering them to an Amazon S3 bucket. Each log file contains details such as the identity of the requester, the time of the request, the source IP address, and the request parameters.

#### Components of CloudTrail

- **CloudTrail Trails**: A trail is a configuration that specifies where CloudTrail should deliver log files and what events to capture.
- **Event History**: This feature allows you to view recent API activity in your AWS account.

### Setting Up CloudTrail

To set up CloudTrail, you need to create a trail. Here’s how you can do it:

1. **Navigate to CloudTrail Console**:
    - Open the AWS Management Console.
    - Navigate to the CloudTrail service.

2. **Create a Trail**:
    - Click on "Create trail".
    - Specify the S3 bucket where the log files will be stored.
    - Optionally, enable additional features like logging all global services and enabling log file validation.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant S3
    User->>CloudTrail: Create Trail
    CloudTrail->>S3: Deliver Log Files
```

### Exploring Event History

Once CloudTrail is set up, you can explore the event history to view recent API activity.

1. **Access Event History**:
    - In the CloudTrail console, navigate to the "Event history" section.
    - Here, you can view a list of recent API calls made to your AWS account.

2. **Detailed View of Events**:
    - Click on an event to view detailed information.
    - This includes the user who initiated the action, the source IP address, the access key, and whether multi-factor authentication (MFA) was used.

### Real-World Example: CVE-2021-3539

In 2021, a critical vulnerability (CVE-2021-3539) was discovered in AWS CloudTrail. This vulnerability allowed attackers to bypass certain security controls and gain unauthorized access to sensitive data. The issue was related to how CloudTrail handled certain API calls.

#### Impact of CVE-2021-3539

- **Unauthorized Access**: Attackers could potentially access sensitive data by exploiting the vulnerability.
- **Data Exfiltration**: Once access was gained, attackers could exfiltrate data from the affected AWS accounts.

#### How to Prevent / Defend Against CVE-2021-3539

1. **Update to Latest Version**: Ensure that you are using the latest version of CloudTrail, as AWS regularly patches vulnerabilities.
2. **Enable Multi-Factor Authentication (MFA)**: Require MFA for all users to add an extra layer of security.
3. **Monitor CloudTrail Logs**: Regularly review CloudTrail logs to detect any suspicious activity.

### Detailed Example: Deleting Security Group

Let’s consider a specific example where a security group is deleted. Here’s how you can view and analyze this event in CloudTrail.

1. **View Event History**:
    - Navigate to the "Event history" section in the CloudTrail console.
    - Look for events related to the deletion of a security group.

2. **Detailed Information**:
    - Click on the event to view detailed information.
    - This includes the user who deleted the security group, the source IP address, the access key, and whether MFA was used.

#### Example HTTP Request and Response

Here’s an example of an HTTP request and response for deleting a security group:

```http
POST /?Action=DeleteSecurityGroup&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b15415dde6124c560c7ddbaa145a6c1c78b3b9a6a4b91c87f4a3d
X-Amz-Date: 20230401T120000Z

Action=DeleteSecurityGroup&Version=2016-11-15&GroupId=sg-12345678
```

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 267
Connection: keep-alive
Date: Mon, 01 Apr 2023 12:00:00 GMT
Server: AmazonEC2

<?xml version="1.0" encoding="UTF-8"?>
<DeleteSecurityGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-3465-4cf6-94ee-563e4b531750</requestId>
  <return>true</return>
</DeleteSecurityGroupResponse>
```

### Infrastructure as Code (IaC) Example: Terraform Destroy

Another important aspect of CloudTrail is its ability to track infrastructure as code (IaC) operations. Let’s consider an example where Terraform is used to destroy resources.

1. **Terraform Destroy Command**:
    - Run `terraform destroy` to delete resources.
    - CloudTrail will log these actions.

2. **Viewing Terraform Actions in CloudTrail**:
    - Navigate to the "Event history" section.
    - Look for events related to Terraform actions.

#### Example Terraform Configuration

Here’s an example of a Terraform configuration for creating and destroying resources:

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_eip" "example" {
  vpc = true
}

resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id
}
```

#### Running Terraform Destroy

When you run `terraform destroy`, CloudTrail will log the following actions:

```http
POST /?Action=DeleteSubnet&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b15415dde6124c560c7ddbaa145a6c1c78b3b9a6a4b91c87f4a3d
X-Amz-Date: 20230401T120000Z

Action=DeleteSubnet&Version=2016-11-15&SubnetId=subnet-12345678
```

```http
POST /?Action=ReleaseAddress&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b15415dde6124c560c7ddbaa145a6c1c78b3b9a6a4b91c87f4a3d
X-Amz-Date: 20230401T120000Z

Action=ReleaseAddress&Version=2016-11-15&AllocationId=eipalloc-12345678
```

```http
POST /?Action=DeleteVpc&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b15415dde6124c560c7ddbaa145a6c1c78b3b9a6a4b91c87f4a3d
X-Amz-Date: 20230401T120000Z

Action=DeleteVpc&Version=2016-11-15&VpcId=vpc-12345678
```

```http
POST /?Action=DeleteInternetGateway&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=5d672d79c15b15415dde6124c560c7ddbaa145a6c1c78b3b9a6a4b91c87f4a3d
X-Amz-Date: 20230401T120000Z

Action=DeleteInternetGateway&Version=2016-11-15&InternetGatewayId=igw-12345678
```

### How to Prevent / Defend Against Unauthorized Actions

1. **Enable CloudTrail**: Ensure that CloudTrail is enabled and configured to log all necessary events.
2. **Set Up Alerts**: Configure alerts in CloudTrail to notify you of suspicious activity.
3. **Use IAM Policies**: Implement strict IAM policies to limit permissions and ensure that only authorized users can perform certain actions.
4. **Regular Audits**: Conduct regular audits of CloudTrail logs to identify and address any unauthorized activity.

### Conclusion

CloudTrail is a powerful tool for monitoring and auditing API activity in your AWS account. By setting up trails and exploring event history, you can gain valuable insights into how your AWS resources are being used and managed. Regularly reviewing CloudTrail logs is essential for maintaining the security and compliance of your AWS environment.

### Practice Labs

For hands-on practice with CloudTrail, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing AWS environments, including CloudTrail.
- **OWASP Juice Shop**: Provides a web application with various security challenges, including logging and monitoring.
- **DVWA (Damn Vulnerable Web Application)**: Useful for practicing security auditing and logging in web applications.

By following these steps and utilizing the provided resources, you can effectively leverage CloudTrail to enhance the security and compliance of your AWS environment.

---
<!-- nav -->
[[01-Introduction to CloudTrail Event History Part 1|Introduction to CloudTrail Event History Part 1]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/00-Overview|Overview]] | [[03-CloudTrail Event History Part 1|CloudTrail Event History Part 1]]

---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the difference between AWS and Digital Ocean in terms of infrastructure management capabilities.**

AWS offers a significantly more granular and powerful approach to managing infrastructure compared to Digital Ocean. AWS provides a wide range of services and tools that allow for detailed configuration and control over various aspects of the infrastructure, such as compute, storage, networking, and security. This makes AWS suitable for large-scale, complex applications and environments. On the other hand, Digital Ocean is simpler and more straightforward, making it easier to set up and manage smaller or less complex infrastructures. However, it lacks the depth and breadth of customization options available in AWS.

**Q2. How would you exploit IAM roles and policies to ensure secure access to AWS resources?**

To ensure secure access to AWS resources using IAM roles and policies, follow these steps:

1. **Create IAM Users**: Define specific users who need access to AWS resources.
2. **Attach Policies**: Create and attach policies to these users that specify what actions they can perform and on which resources.
3. **Use Roles for Temporary Access**: For services like EC2 instances that need temporary access to AWS resources, create IAM roles and assign them to the instances. This way, the instances can assume the role and access necessary resources without hardcoding credentials.
4. **Least Privilege Principle**: Ensure that the policies attached to roles and users provide only the minimum permissions required to perform their tasks.
5. **Regular Audits**: Regularly review and audit IAM policies and roles to ensure they still meet security requirements and remove any unnecessary permissions.

Example policy snippet:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

**Q3. Describe the process of creating a private network on AWS using the VPC service.**

Creating a private network on AWS using the VPC service involves several steps:

1. **Launch VPC**: Go to the VPC dashboard and click on "Start VPC Wizard". Choose the type of VPC you want to create (e.g., VPC with Public and Private Subnets).
2. **Configure Network Settings**: Specify the CIDR block for your VPC and define subnets for public and private networks. Assign appropriate IP ranges to these subnets.
3. **Set Up Internet Gateway**: If you need internet connectivity for your instances, create an Internet Gateway and attach it to your VPC.
4. **Create Route Tables**: Define route tables for your subnets. Public subnets should have routes to the Internet Gateway, while private subnets should not.
5. **Launch Instances**: Launch EC2 instances into the appropriate subnets. Ensure that instances in private subnets do not have public IP addresses.
6. **Security Groups**: Configure security groups to control inbound and outbound traffic to your instances.

Example of creating a VPC via AWS CLI:
```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
```

**Q4. How would you deploy a web application using Docker and Docker Compose on an EC2 instance?**

Deploying a web application using Docker and Docker Compose on an EC2 instance involves the following steps:

1. **Provision EC2 Instance**: Launch an EC2 instance with the desired specifications.
2. **Install Docker**: SSH into the EC2 instance and install Docker using the package manager (e.g., `sudo apt-get update && sudo apt-get install docker.io`).
3. **Pull Docker Images**: Use Docker to pull the necessary images for your application (e.g., `docker pull nginx`).
4. **Create Docker Compose File**: Prepare a `docker-compose.yml` file that defines the services, networks, and volumes required for your application.
5. **Run Docker Compose**: Execute `docker-compose up -d` to start the containers defined in the `docker-compose.yml` file.
6. **Configure Security Groups**: Ensure that the EC2 instance's security group allows traffic on the necessary ports (e.g., port 80 for HTTP).

Example `docker-compose.yml`:
```yaml
version: '3'
services:
  web:
    image: nginx
    ports:
      - "80:80"
```

**Q5. What is the AWS CLI, and how would you use it to manage your AWS resources?**

The AWS Command Line Interface (CLI) is a unified tool to manage AWS services. It allows you to interact with AWS services using commands in your terminal or script files. To use the AWS CLI effectively:

1. **Install AWS CLI**: Install the AWS CLI on your local machine using pip (`pip install awscli`) or another method depending on your operating system.
2. **Configure AWS CLI**: Run `aws configure` to set up your AWS access key ID, secret access key, default region, and output format.
3. **Manage Resources**: Use various AWS CLI commands to manage your resources. For example, to list all S3 buckets, you can run `aws s3 ls`.
4. **Automate Tasks**: Write scripts that use the AWS CLI to automate repetitive tasks, such as deploying new instances or updating security groups.

Example of listing EC2 instances:
```bash
aws ec2 describe-instances
```

**Q6. Discuss recent real-world examples where AWS services were exploited, and explain how such vulnerabilities could have been mitigated.**

One notable example is the Capital One data breach in 2019 (CVE-2019-11309). The attacker exploited a misconfigured WAF rule on an S3 bucket, allowing unauthorized access to sensitive customer data. This vulnerability could have been mitigated by:

1. **Proper Configuration Management**: Ensuring that WAF rules and S3 bucket policies are correctly configured to restrict access to authorized users only.
2. **Regular Audits**: Conducting regular security audits and reviews of AWS configurations to identify and fix misconfigurations.
3. **Least Privilege Principle**: Applying the least privilege principle to ensure that IAM roles and policies grant only the necessary permissions required for a task.
4. **Monitoring and Logging**: Enabling monitoring and logging features to detect and respond to suspicious activities promptly.

By implementing these measures, organizations can significantly reduce the risk of similar breaches occurring in the future.

---
<!-- nav -->
[[01-Introduction to AWS|Introduction to AWS]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/01-AWS Services Overview And Hands-On Deployment/00-Overview|Overview]]

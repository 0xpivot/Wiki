---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Self-Managed GitLab Runners

In the realm of Continuous Integration and Continuous Deployment (CI/CD), having a robust and secure pipeline is paramount. One of the key components of a CI/CD pipeline is the runner, which executes the jobs defined in the pipeline. In this chapter, we will delve into the configuration and management of a self-managed GitLab runner, particularly focusing on setting up an EC2 instance on AWS as the runner. This approach allows organizations to maintain complete control over their infrastructure, ensuring that sensitive data remains within a private network.

### Why Use a Self-Managed GitLab Runner?

For companies with stringent security requirements, it is essential to have full control over the entire infrastructure, including the CI/CD environment. By using a self-managed GitLab runner, you can ensure that all sensitive data remains within your private network, reducing the risk of exposure to external threats. Additionally, a self-managed runner provides greater flexibility and customization options compared to shared runners.

### Key Concepts

Before diving into the setup process, let's define some key concepts:

- **GitLab Runner**: A program that runs your jobs and sends the results back to GitLab. It can be configured to run on various environments, including local machines, virtual machines, and cloud instances.
- **EC2 Instance**: An Amazon Elastic Compute Cloud (EC2) instance is a virtual server in Amazon's cloud. It provides the computing power needed to run applications and services.
- **AWS Role**: An AWS role is an IAM entity that you can use to delegate permissions to other entities. Roles are similar to users but are not associated with a specific person or service.

### Setting Up an EC2 Instance as a GitLab Runner

To set up an EC2 instance as a GitLab runner, follow these steps:

1. **Create an EC2 Instance**:
    - Log in to the AWS Management Console.
    - Navigate to the EC2 dashboard.
    - Click on "Launch Instance".
    - Choose an appropriate AMI (Amazon Machine Image) based on your requirements (e.g., Ubuntu Server).
    - Configure the instance type, storage, and networking settings.
    - Set up security groups to allow necessary inbound traffic (e.g., SSH).

2. **Install GitLab Runner**:
    - Connect to the EC2 instance via SSH.
    - Install GitLab Runner using the package manager. For example, on Ubuntu:
      ```bash
      curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
      sudo apt-get install gitlab-runner
      ```

3. **Register the Runner**:
    - Register the runner with your GitLab project. You will need the registration token provided by GitLab.
    - Run the following command:
      ```bash
      sudo gitlab-runner register
      ```
    - Follow the prompts to provide the URL of your GitLab instance, the registration token, and other details.

4. **Configure the Runner**:
    - Edit the configuration file `/etc/gitlab-runner/config.toml` to customize the runner settings.
    - Example configuration:
      ```toml
      concurrent = 1
      check_interval = 0

      [[runners]]
        name = "ec2-runner"
        url = "https://gitlab.example.com/"
        token = "your-registration-token"
        executor = "shell"
        [runners.custom_build_dir]
        [runners.cache]
          [runners.cache.s3]
            bucket = "your-s3-bucket"
            path = "cache"
            region = "us-east-1"
            access_key = "your-access-key"
            secret_key = "your-secret-key"
      ```

### Leveraging AWS Roles for Authentication

One of the significant advantages of using an EC2 instance as a GitLab runner is the ability to leverage AWS roles for authentication. Instead of managing separate AWS user credentials, you can assign an IAM role to the EC2 instance, allowing it to authenticate with AWS services directly.

#### Creating an IAM Role

1. **Create an IAM Role**:
    - Navigate to the IAM console in the AWS Management Console.
    - Click on "Roles" and then "Create role".
    - Select "EC2" as the trusted entity.
    - Attach policies that grant the necessary permissions (e.g., `AmazonS3FullAccess`, `AmazonEC2ReadOnlyAccess`).

2. **Assign the IAM Role to the EC2 Instance**:
    - Go to the EC2 dashboard.
    - Select the instance and click on "Actions" > "Security" > "Modify IAM role".
    - Assign the IAM role you created.

#### Using the IAM Role in the Pipeline

Once the IAM role is assigned, you can configure your pipeline to use the role for authentication. This eliminates the need to manage and store AWS credentials in your pipeline configuration.

Example `.gitlab-ci.yml` configuration:
```yaml
stages:
  - build
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application..."
    - aws s3 ls s3://your-bucket-name --region us-east-1

deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - aws ec2 describe-instances --region us-east-1
```

### Security Best Practices

While setting up a self-managed GitLab runner on an EC2 instance provides enhanced security, it is crucial to follow best practices to ensure the integrity and confidentiality of your pipeline.

#### Secure Configuration

- **Use Strong IAM Policies**: Ensure that the IAM role assigned to the EC2 instance has the minimum necessary permissions. Avoid using overly broad policies that grant unnecessary access.
- **Enable VPC Flow Logs**: Enable VPC flow logs to monitor network traffic to and from your EC2 instance. This helps in detecting unauthorized access attempts.
- **Use SSH Keys**: Securely manage SSH keys used to access the EC2 instance. Consider using SSH key pairs with strong passphrases and enabling two-factor authentication.

#### Monitoring and Logging

- **Enable CloudTrail**: Enable AWS CloudTrail to log API calls made to your AWS resources. This helps in auditing and monitoring activities performed by the EC2 instance.
- **Set Up CloudWatch Alarms**: Configure CloudWatch alarms to notify you of any unusual activity or resource usage spikes.

#### Regular Audits

- **Perform Regular Security Audits**: Conduct regular security audits to identify and mitigate potential vulnerabilities. Use tools like AWS Trusted Advisor to get recommendations on improving security posture.
- **Update Dependencies**: Keep all dependencies and libraries used in your pipeline up to date. Regularly review and update the versions to patch known vulnerabilities.

### Real-World Examples and Case Studies

#### Recent Breaches and CVEs

- **CVE-2021-21287**: This vulnerability in GitLab allowed attackers to execute arbitrary code on the server. Ensuring that your GitLab installation is up to date and applying security patches promptly can help mitigate such risks.
- **AWS S3 Bucket Exposure**: In 2020, several high-profile incidents occurred where S3 buckets were left exposed due to misconfigured IAM roles and permissions. Properly configuring IAM roles and regularly reviewing permissions can prevent such exposures.

### How to Prevent / Defend

#### Detection

- **Use Security Tools**: Utilize security tools like AWS Inspector to scan your EC2 instances for vulnerabilities. Regularly run scans to identify and address any security issues.
- **Monitor Access Logs**: Monitor access logs for both the EC2 instance and the IAM role. Look for any unauthorized access attempts or suspicious activity.

#### Prevention

- **Secure IAM Roles**: Ensure that IAM roles are tightly scoped with least privilege access. Regularly review and update IAM policies to reflect current security requirements.
- **Enable Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users who have access to the EC2 instance and the GitLab runner. This adds an extra layer of security by requiring a second form of verification.

#### Secure-Coding Fixes

##### Vulnerable Code Example
```yaml
deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - aws ec2 describe-instances --region us-east-1 --access-key $ACCESS_KEY --secret-key $SECRET_KEY
```

##### Secure Code Example
```yaml
deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - aws ec2 describe-instances --region us-east-1
```

#### Configuration Hardening

- **IAM Policy Example**
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeInstances",
          "s3:ListBucket"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

- **CloudTrail Configuration**
  ```json
  {
    "CloudTrail": {
      "IsEnabled": true,
      "S3BucketName": "your-cloudtrail-bucket",
      "IncludeGlobalServiceEvents": true,
      "IsLogging": true
    }
  }
  ```

### Conclusion

By setting up a self-managed GitLab runner on an EC2 instance, you can achieve a highly secure and flexible CI/CD pipeline. The ability to leverage AWS roles for authentication further enhances security by eliminating the need to manage separate AWS user credentials. Following best practices and regularly auditing your setup ensures that your pipeline remains robust against potential threats.

### Practice Labs

For hands-on experience with setting up a self-managed GitLab runner on AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on CI/CD security, including setting up GitLab runners.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice securing CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Useful for practicing secure coding and pipeline configurations.

These labs provide practical scenarios to reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/03-Introduction to GitLab Runners|Introduction to GitLab Runners]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[05-Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines Part 1|Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines Part 1]]

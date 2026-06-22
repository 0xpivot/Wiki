---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why using IAM roles for EC2 instances is a better security practice compared to using static AWS credentials in a CI/CD pipeline.**

IAM roles provide a more secure approach to managing access to AWS resources compared to using static AWS credentials. Static credentials, such as access keys and secret keys, pose several risks:

1. **Exposure Risk**: Static credentials can be exposed through various means, such as insecure storage or accidental inclusion in source code repositories. If compromised, these credentials can be used to gain unauthorized access to AWS resources.

2. **Limited Revocation**: Once static credentials are compromised, revoking access requires changing the credentials and updating them across all systems where they are used. This can be time-consuming and error-prone.

3. **Least Privilege Principle**: IAM roles allow you to define specific permissions for different resources, adhering to the principle of least privilege. This ensures that each resource has only the permissions it needs to function, reducing the potential impact of a breach.

4. **Dynamic Credentials**: IAM roles provide temporary, short-lived credentials that are automatically rotated. This reduces the risk associated with long-term static credentials.

By using IAM roles, you can ensure that your CI/CD pipeline has the necessary permissions to interact with AWS resources without the need to store and manage static credentials. This enhances security by limiting exposure and simplifying the management of access rights.

**Q2. How would you configure an IAM role for an EC2 instance running a GitLab runner to enable it to access AWS ECR and SSM services?**

To configure an IAM role for an EC2 instance running a GitLab runner to access AWS ECR and SSM services, follow these steps:

1. **Create the IAM Role**:
   - Go to the IAM console in the AWS Management Console.
   - Click on "Roles" and then "Create role".
   - Choose "EC2" as the trusted entity.
   - Attach policies that grant permissions to access ECR and SSM services. For example, you can attach the `AmazonEC2ContainerRegistryFullAccess` and `AmazonSSMFullAccess` managed policies.
   - Give the role a meaningful name, such as `GitLabRunnerRole`.

2. **Attach the Role to the EC2 Instance**:
   - Go to the EC2 console.
   - Select the EC2 instance running the GitLab runner.
   - Under the "Actions" menu, choose "Security" and then "Modify IAM role".
   - Assign the previously created IAM role (`GitLabRunnerRole`) to the EC2 instance.

3. **Update the Pipeline Configuration**:
   - Remove any static AWS credentials from the pipeline configuration.
   - Ensure that the pipeline jobs that require access to ECR and SSM are executed on the EC2 instance with the IAM role attached.

Here is an example of how you might update the pipeline configuration in `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - deploy

build_image:
  stage: build
  script:
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com
    - docker build -t my-image .
    - docker tag my-image:latest $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
    - docker push $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/my-image:latest

deploy_image:
  stage: deploy
  script:
    - aws ssm send-command --instance-ids $INSTANCE_ID --document-name "AWS-RunShellScript" --parameters '{"commands":["echo Hello World"]}'
```

In this example, the pipeline uses the IAM role attached to the EC2 instance to authenticate and authorize access to ECR and SSM services.

**Q3. Why is it important to remove static credentials from the CI/CD pipeline when using IAM roles?**

Removing static credentials from the CI/CD pipeline when using IAM roles is crucial for several reasons:

1. **Reduced Exposure Risk**: Static credentials, such as access keys and secret keys, can be exposed through various means, such as insecure storage or accidental inclusion in source code repositories. Removing these credentials from the pipeline reduces the risk of exposure.

2. **Easier Revocation**: If static credentials are compromised, revoking access requires changing the credentials and updating them across all systems where they are used. This can be time-consuming and error-prone. With IAM roles, you can simply detach the role from the EC2 instance or modify the role's permissions without affecting other systems.

3. **Least Privilege Principle**: IAM roles allow you to define specific permissions for different resources, adhering to the principle of least privilege. This ensures that each resource has only the permissions it needs to function, reducing the potential impact of a breach.

4. **Dynamic Credentials**: IAM roles provide temporary, short-lived credentials that are automatically rotated. This reduces the risk associated with long-term static credentials.

By removing static credentials from the CI/CD pipeline, you enhance security by limiting exposure and simplifying the management of access rights.

**Q4. How does the use of IAM roles for EC2 instances help in detecting and responding to suspicious activity in an AWS account?**

Using IAM roles for EC2 instances helps in detecting and responding to suspicious activity in an AWS account in several ways:

1. **Centralized Logging**: IAM roles provide centralized logging capabilities. When an EC2 instance assumes an IAM role, AWS CloudTrail logs the activity, including API calls made by the instance. This enables you to monitor and audit access to AWS resources.

2. **Fine-Grained Permissions**: IAM roles allow you to define specific permissions for different resources, adhering to the principle of least privilege. This ensures that each resource has only the permissions it needs to function, reducing the potential impact of a breach.

3. **Monitoring and Alerts**: You can set up monitoring and alerts using AWS CloudWatch to detect suspicious activity. For example, you can create CloudWatch alarms to notify you when certain API calls are made or when unusual patterns of activity are detected.

4. **Automated Responses**: You can automate responses to suspicious activity using AWS Lambda functions. For example, you can write a Lambda function that revokes access to an IAM role if suspicious activity is detected.

By using IAM roles for EC2 instances, you can centralize logging, monitor and audit access to AWS resources, and respond to suspicious activity in a timely manner.

**Q5. What recent real-world examples demonstrate the importance of using IAM roles for EC2 instances in a CI/CD pipeline?**

Recent real-world examples highlight the importance of using IAM roles for EC2 instances in a CI/CD pipeline:

1. **CVE-2021-26614**: In 2021, a vulnerability in the AWS SDK for Java allowed attackers to escalate privileges and gain unauthorized access to AWS resources. Using IAM roles with least privilege permissions would have mitigated the impact of this vulnerability.

2. **SolarWinds Supply Chain Attack**: In 2020, the SolarWinds supply chain attack compromised numerous organizations' networks. Using IAM roles with least privilege permissions would have reduced the attack surface and limited the impact of the breach.

3. **Capital One Data Breach**: In 2019, a Capital One data breach exposed sensitive customer information due to misconfigured AWS S3 buckets. Using IAM roles with least privilege permissions would have prevented unauthorized access to the S3 buckets.

These examples demonstrate the importance of using IAM roles for EC2 instances in a CI/CD pipeline to reduce the risk of unauthorized access and limit the impact of breaches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/07-Secure Continuous Deployment & Dynamic Application Security Testing (DAST)|Secure Continuous Deployment & Dynamic Application Security Testing (DAST)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/00-Overview|Overview]]

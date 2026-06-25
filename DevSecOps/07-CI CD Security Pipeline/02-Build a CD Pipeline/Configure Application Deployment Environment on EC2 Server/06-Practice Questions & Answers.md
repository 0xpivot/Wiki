---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. How do you create an EC2 instance for deploying a Docker image on AWS?**

To create an EC2 instance for deploying a Docker image on AWS, follow these steps:

1. Go to the EC2 service in the AWS Management Console.
2. Click on "Launch Instance".
3. Choose an Amazon Machine Image (AMI), such as the latest Ubuntu Server.
4. Select an instance type, like `t2.micro`, depending on your requirements.
5. Configure Instance Details, including the number of instances, network settings, and security groups.
6. Add storage if necessary, though the default settings often suffice.
7. Tag the instance for easy identification, e.g., naming it "App Server".
8. Configure Security Group settings to allow SSH access.
9. Create a new key pair for secure SSH access, ensuring the permissions are set correctly (e.g., `chmod 400 AppServerKey.pem`).
10. Launch the instance and note down the public IP address for SSH access.

**Q2. What are the security implications of allowing SSH access from anywhere, and how can you mitigate these risks?**

Allowing SSH access from anywhere (`0.0.0.0/0`) is highly insecure because it exposes your server to potential brute-force attacks and unauthorized access attempts. To mitigate these risks:

1. **Restrict Access**: Limit SSH access to specific IP addresses or ranges using the security group rules.
2. **Use Strong Authentication**: Enable two-factor authentication (2FA) for SSH access.
3. **Disable Root Login**: Ensure root login over SSH is disabled and use a non-root user with sudo privileges.
4. **Update Regularly**: Keep the OS and software up-to-date with the latest security patches.
5. **Monitor Logs**: Regularly review SSH logs for suspicious activity.

**Q3. Explain how to install Docker on an Ubuntu EC2 instance and configure it for running containers.**

To install Docker on an Ubuntu EC2 instance and configure it for running containers:

1. SSH into the EC2 instance.
2. Update the package lists: `sudo apt-get update`.
3. Install Docker: `sudo apt-get install docker.io`.
4. Verify Docker installation: `docker --version`.
5. Add the current user to the Docker group to avoid using `sudo` every time: `sudo usermod -aG docker ubuntu`.
6. Log out and log back in to apply the group changes.
7. Test Docker by running a simple container: `docker run hello-world`.

**Q4. How do you authenticate an EC2 instance to pull Docker images from a private ECR repository?**

To authenticate an EC2 instance to pull Docker images from a private ECR repository:

1. Install the AWS CLI on the EC2 instance: `sudo apt-get install awscli`.
2. Set up AWS credentials and default region:
   ```bash
   export AWS_ACCESS_KEY_ID=<your_access_key>
   export AWS_SECRET_ACCESS_KEY=<your_secret_key>
   export AWS_DEFAULT_REGION=<your_region>
   ```
3. Use the `aws ecr get-login-password` command to generate a password and authenticate Docker to the ECR repository:
   ```bash
   $(aws ecr get-login-password --region <your_region>) | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
   ```

**Q5. Why is it important to set the correct permissions on the private key file used for SSH access to an EC2 instance?**

Setting the correct permissions on the private key file used for SSH access to an EC2 instance is crucial for maintaining the security of your server. Incorrect permissions can lead to unauthorized access:

1. **Security Best Practices**: AWS enforces strict security practices, and incorrect permissions can cause SSH access to be rejected.
2. **Prevent Unauthorized Access**: Setting permissions to `chmod 400 <key_file>` ensures only the owner can read the file, preventing unauthorized users from accessing the server.
3. **Compliance**: Properly securing keys helps meet compliance standards and best practices for handling sensitive information.

**Q6. How can you automate the deployment process described in the lecture?**

Automating the deployment process involves using CI/CD pipelines and infrastructure-as-code (IaC) tools:

1. **CI/CD Pipeline**: Use tools like Jenkins, GitHub Actions, or AWS CodePipeline to automate the build, test, and deployment processes.
2. **Infrastructure-as-Code**: Utilize tools like Terraform or CloudFormation to define and manage your infrastructure in code.
3. **Docker Compose**: Use Docker Compose to define and run multi-container Docker applications.
4. **AWS Lambda Functions**: Automate tasks like creating EC2 instances, setting up security groups, and pulling Docker images from ECR.

By automating these steps, you reduce manual errors, improve consistency, and speed up the deployment process.

---
<!-- nav -->
[[05-Setting Up the AWS CLI and Environment Variables|Setting Up the AWS CLI and Environment Variables]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/00-Overview|Overview]]

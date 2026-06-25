---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring Application Deployment Environment on EC2 Server

### Introduction

In this section, we will walk through the process of configuring an Amazon EC2 instance to serve as the deployment environment for our application. This involves setting up the instance, securing SSH access, and installing Docker to run our application as a container. Each step will be detailed with explanations, code snippets, and diagrams to ensure a comprehensive understanding.

### Setting Up the EC2 Instance

#### Step 1: Launching the EC2 Instance

Before we begin, ensure that you have launched an EC2 instance using the AWS Management Console or the AWS CLI. For this example, we will assume you have launched an instance with an Ubuntu operating system.

#### Step 2: Waiting for Initialization

Once the instance is launched, it will take some time to initialize. You can check the status in the AWS Management Console. Once the instance is running, proceed to the next steps.

### Securing SSH Access

#### Step 3: Restricting Permissions on Private Key

To securely connect to the EC2 instance via SSH, we need to ensure that the private key used for authentication has the correct permissions. AWS requires that the private key file has restricted permissions to prevent unauthorized access.

**Command to Change File Permissions:**

```bash
chmod 400 app_server_key
```

This command sets the file permissions to `400`, which means:

- **Owner:** Read-only access.
- **Group:** No access.
- **Others:** No access.

This ensures that only the owner of the file can read it, enhancing security.

**Explanation:**
- **Why:** AWS enforces this security practice to prevent unauthorized access to the EC2 instance.
- **How:** The `chmod` command changes the file permissions. The `400` value restricts access to the owner only.
- **Pitfalls:** Failing to set the correct permissions can result in AWS rejecting the SSH connection attempt.

**Secure Coding Practice:**
Always store private keys in a secure location, such as the `.ssh` directory in your home directory, and ensure they have the correct permissions.

### Connecting to the EC2 Instance via SSH

#### Step 4: Retrieving Public IP Address

To connect to the EC2 instance, you need its public IP address. You can find this information in the AWS Management Console under the "Instances" section.

**Example Public IP Address:**
```
54.123.456.789
```

#### Step 5: SSH Connection Command

Use the following command to connect to the EC2 instance via SSH:

```bash
ssh -i app_server_key ubuntu@54.123.456.789
```

**Explanation:**
- **`-i app_server_key`:** Specifies the private key file to use for authentication.
- **`ubuntu`:** The default username for Ubuntu-based EC2 instances.
- **`54.123.456.789`:** The public IP address of the EC2 instance.

**Secure Coding Practice:**
Ensure that the private key (`app_server_key`) is stored in a secure location and has the correct permissions (`400`). Avoid storing the private key in easily accessible locations.

### Installing Docker on the EC2 Instance

#### Step 6: Installing Docker

Once connected to the EC2 instance, the next step is to install Docker. Docker is essential for running our application as a container.

**Command to Install Docker:**

```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

**Explanation:**
- **`apt-get update`:** Updates the package list to ensure you are installing the latest version of Docker.
- **`apt-get install -y docker.io`:** Installs Docker on the Ubuntu system.

**Secure Coding Practice:**
Always ensure that the system is up-to-date before installing new packages. This helps in avoiding vulnerabilities present in older versions.

### Verifying Docker Installation

#### Step 7: Verify Docker Installation

After installation, verify that Docker is correctly installed and running.

**Command to Verify Docker Installation:**

```bash
docker --version
```

**Expected Output:**
```
Docker version 20.10.7, build f0df350
```

**Explanation:**
- **`docker --version`:** Displays the version of Docker installed on the system.

**Secure Coding Practice:**
Regularly update Docker to the latest version to mitigate known vulnerabilities.

### Deploying the Docker Image

#### Step 8: Pulling the Docker Image from ECR

Assuming you have already built and pushed the Docker image to Amazon Elastic Container Registry (ECR), the next step is to pull the image onto the EC2 instance.

**Command to Pull Docker Image:**

```bash
docker pull <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>
```

**Explanation:**
- **`<aws_account_id>`:** Your AWS account ID.
- **`<region>`:** The AWS region where the ECR repository is located.
- **`<repository>`:** The name of the ECR repository.
- **`<tag>`:** The tag of the Docker image.

**Secure Coding Practice:**
Ensure that the ECR repository is properly configured with IAM policies to control access to the Docker images.

### Running the Docker Container

#### Step 9: Running the Docker Container

Once the Docker image is pulled, you can run the container.

**Command to Run Docker Container:**

```bash
docker run -d -p 80:80 <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>
```

**Explanation:**
- **`-d`:** Runs the container in detached mode.
- **`-p 80:80`:** Maps port 80 on the host to port 80 on the container.
- **`<aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>`:** The Docker image to run.

**Secure Coding Practice:**
Ensure that the container runs with the least privileges necessary. Use Docker security features like AppArmor or SELinux to enhance security.

### Monitoring and Logging

#### Step 10: Monitoring and Logging

To monitor the running container and log its activities, you can use Docker's logging capabilities.

**Command to Check Logs:**

```bash
docker logs <container_id>
```

**Explanation:**
- **`<container_id>`:** The ID of the running container.

**Secure Coding Practice:**
Configure Docker to send logs to a centralized logging service like AWS CloudWatch Logs for better monitoring and auditing.

### How to Prevent / Defend

#### Defense Mechanisms

1. **Secure SSH Access:**
   - Ensure that the private key has the correct permissions (`400`).
   - Store the private key in a secure location, such as the `.ssh` directory.
   - Use strong, unique passwords for SSH access.

2. **Docker Security:**
   - Regularly update Docker to the latest version.
   - Use Docker security features like AppArmor or SELinux.
   - Run containers with the least privileges necessary.

3. **Monitoring and Logging:**
   - Configure Docker to send logs to a centralized logging service.
   - Monitor container activities regularly.

### Real-World Examples

#### Example 1: CVE-2021-21287

In 2021, a critical vulnerability was discovered in Docker, allowing attackers to escalate privileges and gain root access to the host system. This vulnerability highlights the importance of keeping Docker updated and using security features.

**Secure Fix:**
Ensure that Docker is updated to the latest version and configure security features like AppArmor or SELinux.

#### Example 2: AWS ECR Breach

In 2020, a breach occurred in AWS ECR, where unauthorized access to Docker images was possible due to misconfigured IAM policies. This emphasizes the importance of proper IAM policy management.

**Secure Fix:**
Configure IAM policies to control access to ECR repositories and ensure that only authorized users have access.

### Conclusion

By following these steps, you can securely configure an EC2 instance for deploying your application as a Docker container. Ensuring that SSH access is secure, Docker is properly installed and updated, and monitoring and logging are in place will help protect your deployment environment from potential threats.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy:** Offers hands-on labs for web application security.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **CloudGoat:** A series of labs designed to teach cloud security concepts using AWS.

These labs provide real-world scenarios to apply the concepts learned in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/00-Overview|Overview]] | [[02-Configuring Application Deployment Environment on EC2 Server Part 2|Configuring Application Deployment Environment on EC2 Server Part 2]]

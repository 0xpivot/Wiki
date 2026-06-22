---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring Application Deployment Environment on EC2 Server

### Initial System Update

When setting up a new EC2 server, the first step is to ensure that the system is up-to-date. This involves refreshing and updating the repositories for the operating system package manager. This process ensures that you have the latest security patches and updates for the installed packages.

#### Why Perform an Update?

Performing an update is crucial for several reasons:

1. **Security**: New vulnerabilities are discovered frequently, and keeping your system updated helps mitigate these risks.
2. **Functionality**: Updates often include bug fixes and improvements that enhance the functionality of the system.
3. **Compatibility**: Ensuring that all packages are up-to-date helps maintain compatibility between different components of the system.

#### How to Perform an Update

For an Ubuntu-based system, you would typically use the `apt` package manager to perform the update. Here’s the command to do so:

```bash
sudo apt update && sudo apt upgrade -y
```

- `apt update`: This command refreshes the list of available packages and their versions, but it does not install or update any packages.
- `apt upgrade -y`: This command upgrades all the installed packages to their latest versions. The `-y` flag automatically answers "yes" to all prompts, making the process non-interactive.

### Installing Docker

Once the system is up-to-date, the next step is to install Docker. Docker is a platform that allows developers to build, ship, and run applications inside lightweight containers.

#### Why Use Docker?

Docker provides several benefits:

1. **Portability**: Applications packaged in Docker containers can run consistently across different environments.
2. **Isolation**: Containers provide a level of isolation, ensuring that applications do not interfere with each other.
3. **Efficiency**: Containers share the host OS kernel, making them more efficient than traditional virtual machines.

#### Installation Steps

To install Docker on an Ubuntu system using the `apt` package manager, follow these steps:

1. **Add Docker’s GPG Key**:
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```

2. **Set Up the Stable Repository**:
    ```bash
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

3. **Update the Package Database**:
    ```bash

sudo apt update
```

4. **Install Docker CE (Community Edition)**:
    ```bash
sudo apt install docker-ce docker-ce-cli containerd.io
```

### Adding User to Docker Group

After installing Docker, you may encounter permission issues when trying to run Docker commands. This is because Docker runs as a root process by default, and regular users do not have the necessary permissions.

#### Why Add User to Docker Group?

Adding the user to the Docker group allows them to run Docker commands without needing to use `sudo`. This is particularly useful in development environments where frequent Docker operations are required.

#### Steps to Add User to Docker Group

1. **Add User to Docker Group**:
    ```bash
sudo usermod -aG docker $USER
```

2. **Log Out and Log Back In**:
    After adding the user to the Docker group, you need to log out and log back in for the changes to take effect.

3. **Verify Docker Command Availability**:
    Once logged back in, verify that the Docker command is available:
    ```bash
docker ps
```

### Running Docker Image from Private Repository

To run a Docker image from a private repository, such as Amazon Elastic Container Registry (ECR), you need to authenticate with the repository.

#### Why Authenticate with ECR?

Private repositories require authentication to ensure that only authorized users can access the images. This is particularly important for security and compliance reasons.

#### Steps to Authenticate with ECR

1. **Install AWS CLI**:
    Before authenticating with ECR, you need to install the AWS Command Line Interface (CLI).

    ```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

2. **Configure AWS CLI**:
    Configure the AWS CLI with your credentials.

    ```bash
aws configure
```

3. **Authenticate with ECR**:
    Use the `aws ecr get-login-password` command to authenticate with ECR.

    ```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

### Example: Running Juice Shop from ECR

Let’s walk through an example of running the OWASP Juice Shop application from an ECR repository.

#### Step-by-Step Example

1. **Install Docker and Add User to Docker Group**:
    Follow the steps outlined earlier to install Docker and add the user to the Docker group.

2. **Install AWS CLI**:
    Install the AWS CLI as described above.

3. **Authenticate with ECR**:
    Replace `<region>` and `<account-id>` with your specific region and account ID.

    ```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

4. **Pull and Run the Docker Image**:
    Pull the Juice Shop image from the ECR repository and run it.

    ```bash
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/juice-shop:latest
docker run -d -p 3000:3000 123456789012.dkr.ecr.us-east-1.amazonaws.com/juice-shop:latest
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Permission Issues

**Symptom**: You receive a "permission denied" error when trying to run Docker commands.

**Cause**: The user is not part of the Docker group.

**Prevention**:
- Ensure the user is added to the Docker group using `usermod`.
- Log out and log back in after adding the user to the Docker group.

#### Pitfall 2: Authentication Errors

**Symptom**: You receive an authentication error when trying to pull an image from a private repository.

**Cause**: The AWS CLI is not configured correctly, or the authentication token is invalid.

**Prevention**:
- Ensure the AWS CLI is installed and configured with valid credentials.
- Verify the region and account ID in the authentication command.

### Real-World Examples and CVEs

#### Example: CVE-2021-21366

CVE-2021-21366 is a critical vulnerability in Docker that allows attackers to escalate privileges and gain full control of the host system. This vulnerability highlights the importance of keeping Docker and related tools up-to-date.

#### Secure Configuration Example

Here’s an example of a secure Docker configuration:

```yaml
version: '3'
services:
  juice-shop:
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/juice-shop:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    deploy:
      restart_policy:
        condition: on-failure
```

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Regularly audit Docker configurations and images for vulnerabilities.
- **Monitoring**: Use tools like Docker Security Scanning to monitor for known vulnerabilities.

#### Prevention

- **Keep Updated**: Always keep Docker and related tools up-to-date.
- **Use Secure Images**: Use trusted and secure Docker images from reputable sources.

#### Secure Coding Fixes

**Vulnerable Code**:
```yaml
version: '3'
services:
  juice-shop:
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/juice-shop:latest
    ports:
      - "3000:3000"
```

**Secure Code**:
```yaml
version: '3'
services:
  juice-shop:
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/juice-shop:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    deploy:
      restart_policy:
        condition: on-failure
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **CloudGoat**: A series of labs designed to teach cloud security concepts using AWS.

By following these detailed steps and best practices, you can effectively configure and secure your application deployment environment on an EC2 server.

---
<!-- nav -->
[[01-Configuring Application Deployment Environment on EC2 Server Part 1|Configuring Application Deployment Environment on EC2 Server Part 1]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/00-Overview|Overview]] | [[03-Configuring Application Deployment Environment on EC2 Server Part 3|Configuring Application Deployment Environment on EC2 Server Part 3]]

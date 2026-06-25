---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Continuous Delivery (CD) Pipelines

Continuous Delivery (CD) is an extension of Continuous Integration (CI) that aims to ensure that your software can be reliably released at any time. In the context of DevSecOps, this means integrating security practices throughout the development lifecycle, including the deployment phase. One of the critical steps in a CD pipeline is deploying the application to a production environment. In this chapter, we will focus on deploying a Dockerized application to an Amazon EC2 instance using a release pipeline.

### Background Theory

Before diving into the specifics of setting up the deployment job, it's essential to understand the underlying concepts:

- **Docker**: A platform that allows developers to package applications into containers, ensuring consistency across different environments.
- **Amazon EC2**: Elastic Compute Cloud, a service provided by Amazon Web Services (AWS) that offers scalable computing capacity in the cloud.
- **GitLab CI/CD**: A set of tools integrated into GitLab for automating the build, test, and deployment processes.

### Setting Up the Deployment Job

The deployment job in our pipeline will perform the following tasks:

1. Connect to the EC2 instance via SSH.
2. Pull the Docker image from the Amazon Elastic Container Registry (ECR).
3. Run the Docker image as a container on the EC2 instance.

#### Prerequisites

To set up the deployment job, you need the following information:

- **Public IP Address** of the EC2 instance.
- **Operating System User** with SSH access.
- **SSH Private Key** to authenticate the connection.

### Connecting to the EC2 Instance via SSH

In the previous steps, we connected to the EC2 instance from our local machine using SSH. Now, we need to enable the GitLab runner to perform the same task. This involves configuring the SSH agent within the GitLab pipeline.

#### SSH Agent Configuration

The SSH agent is a program that holds your SSH keys in memory and provides them to SSH clients when needed. To configure the SSH agent in the GitLab pipeline, follow these steps:

1. **Copy the SSH Private Key**: Retrieve the contents of the SSH private key file and store it in a GitLab CI/CD variable.

```bash
cat ~/.ssh/id_rsa | pbcopy
```

2. **Add Variable to GitLab Settings**: Navigate to the GitLab project settings and add a new CI/CD variable named `SSH_PRIVATE_KEY`.

```yaml
variables:
  SSH_PRIVATE_KEY: "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
```

### Pulling the Docker Image from ECR

Once the SSH connection is established, the next step is to pull the Docker image from the ECR repository. This requires logging into the ECR registry using the AWS CLI.

#### Logging into ECR

To log into the ECR registry, you need to use the `aws ecr get-login-password` command followed by `docker login`.

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <your-ecr-repo-url>
```

### Running the Docker Image as a Container

After pulling the Docker image, the final step is to run the container on the EC2 instance. This can be done using the `docker run` command.

```bash
docker run -d -p 80:80 <your-docker-image>
```

### Complete Example of the Deployment Job

Below is a complete example of the deployment job in a GitLab CI/CD pipeline:

```yaml
deploy:
  stage: deploy
  script:
    - echo "$SSH_PRIVATE_KEY" > ssh_key
    - chmod 600 ssh_key
    - ssh -i ssh_key $USER@$IP_ADDRESS "aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <your-ecr-repo-url>"
    - ssh -i ssh_key $USER@$IP_ADDRESS "docker pull <your-docker-image>"
    - ssh -i ssh_key $USER@$IP_ADDRESS "docker run -d -p 80:80 <your-docker-image>"
```

### Mermaid Diagrams

Let's visualize the deployment process using a mermaid diagram:

```mermaid
sequenceDiagram
  participant GitLabRunner as GitLab Runner
  participant EC2Instance as EC2 Instance
  participant ECR as ECR Repository
  participant Docker as Docker

  GitLabRunner->>EC2Instance: SSH Connection
  EC2Instance->>ECR: Pull Docker Image
  ECR-->>EC2Instance: Docker Image
  EC2Instance->>Docker: Run Docker Container
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Incorrect SSH Configuration

**Issue**: If the SSH private key is not correctly configured, the GitLab runner will fail to establish an SSH connection to the EC2 instance.

**Prevention**:
- Ensure the SSH private key is stored securely in a GitLab CI/CD variable.
- Verify the SSH private key is correctly formatted and matches the public key on the EC2 instance.

#### Pitfall: Unauthorized Access

**Issue**: If the SSH private key is compromised, unauthorized users could gain access to the EC2 instance.

**Prevention**:
- Rotate SSH keys regularly.
- Use SSH key-based authentication instead of password-based authentication.
- Enable two-factor authentication (2FA) for SSH access.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the **CVE-2021-20225**, which affected the AWS CLI. This vulnerability allowed attackers to execute arbitrary commands on the target system. To mitigate such risks, ensure that all tools used in the pipeline are up-to-date and patched.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
deploy:
  stage: deploy
  script:
    - ssh -i ~/.ssh/id_rsa $USER@$IP_ADDRESS "docker run -d -p 80:80 <your-docker-image>"
```

#### Secure Code Example

```yaml
deploy:
  stage: deploy
  script:
    - echo "$SSH_PRIVATE_KEY" > ssh_key
    - chmod 600 ssh_key
    - ssh -i ssh_key $USER@$IP_ADDRESS "aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <your--ecr-repo-url>"
    - ssh -i ssh_key $USER@$IP_ADDRESS "docker pull <your-docker-image>"
    - ssh -i ssh_key $USER@$IP_ADDRESS "docker run -d -p  80:80 <your-docker-image>"
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing.

### Conclusion

Deploying a Dockerized application to an EC2 instance using a release pipeline is a crucial step in the continuous delivery process. By following the steps outlined in this chapter, you can ensure a smooth and secure deployment. Remember to adhere to best practices for security and maintain regular updates to your tools and configurations.

---
<!-- nav -->
[[05-Introduction to Continuous Delivery (CD) Pipelines Part 5|Introduction to Continuous Delivery (CD) Pipelines Part 5]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Deploy Application to EC2 Server with Release Pipeline/00-Overview|Overview]] | [[07-Introduction to SSH Agent and Key Management|Introduction to SSH Agent and Key Management]]

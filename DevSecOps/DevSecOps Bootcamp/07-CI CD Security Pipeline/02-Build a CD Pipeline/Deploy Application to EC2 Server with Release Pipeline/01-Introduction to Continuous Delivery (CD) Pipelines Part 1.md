---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Continuous Delivery (CD) Pipelines

Continuous Delivery (CD) is a practice in software development where code changes are released to production in small, manageable increments. This ensures that the application is always in a deployable state, allowing teams to release new features quickly and reliably. A CD pipeline automates the process of building, testing, and deploying applications. In this chapter, we will focus on setting up a CD pipeline to deploy an application to an Amazon EC2 server using GitLab's release pipeline capabilities.

### Background Theory

Before diving into the specifics of setting up the pipeline, it's important to understand the components involved:

- **GitLab**: A web-based Git repository manager that provides a wide range of tools for project management, continuous integration, and continuous delivery.
- **Amazon EC2**: Elastic Compute Cloud, a service provided by Amazon Web Services (AWS) that allows users to rent virtual computers on which to run their own applications.
- **SSH Keys**: Secure Shell keys are used for secure authentication between the GitLab runner and the EC2 instance.

### Setting Up SSH Keys in GitLab

To securely connect to the EC2 instance, we need to set up SSH keys in GitLab. This involves creating a private key and uploading it as a file-type variable in GitLab.

#### Creating SSH Keys

First, generate an SSH key pair using the `ssh-keygen` command:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

This command generates a public and private key pair. The public key (`id_rsa.pub`) should be added to the EC2 instance's authorized_keys file, while the private key (`id_rsa`) will be stored in GitLab.

#### Adding SSH Keys to GitLab

In GitLab, navigate to your project's settings and go to the CI/CD variables section. Here, you need to add the private key as a file-type variable.

```markdown
Variable Name: SSH_PRIVATE_KEY
Type: File
Value: id_rsa
```

Make sure to add an extra line at the end of the file. This is a known issue in GitLab where the file format might not be recognized correctly without the extra line.

#### Example of Adding SSH Key Variable

```yaml
variables:
  SSH_PRIVATE_KEY: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA...
    -----END RSA PRIVATE KEY-----
    
    # Extra line at the end
```

### Configuring Other Variables

Next, we need to configure other necessary variables such as the server IP and the server user.

```yaml
variables:
  SERVER_IP: "192.168.1.100"
  SERVER_USER: "ubuntu"
```

These variables will be used in the deployment job to connect to the EC2 instance.

### Setting Up Stages and Jobs

A GitLab CI/CD pipeline is organized into stages and jobs. Each job runs in a specific stage, and stages are executed sequentially.

#### Defining Stages

We will define two stages: `build` and `deploy`.

```yaml
stages:
  - build
  - deploy
```

#### Defining Jobs

For the `deploy` stage, we will define a job called `deploy_image`.

```yaml
deploy_image:
  stage: deploy
  script:
    - echo "Deploying application to $SERVER_IP"
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "mkdir -p /var/www/html"
    - scp -i $SSH_PRIVATE_KEY ./app.tar.gz $SERVER_USER@$SERVER_IP:/var/www/html/
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "tar -xzvf /var/www/html/app.tar.gz -C /var/www/html/"
```

### Selecting the Appropriate Docker Image

When selecting the Docker image for the job, consider the commands needed within the job. For example, if you need to use `scp` and `ssh`, ensure the Docker image includes these utilities.

```yaml
image: ubuntu:latest
```

### Full `.gitlab-ci.yml` Configuration

Here is the complete `.gitlab-ci.yml` configuration:

```yaml
stages:
  - build
  - deploy

variables:
  SSH_PRIVATE_KEY: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA...
    -----END RSA PRIVATE KEY-----
    
    # Extra line at the end
  SERVER_IP: "192.168.1.100"
  SERVER_USER: "ubuntu"

build_job:
  stage: build
  script:
    - echo "Building application"
    - tar -czvf app.tar.gz .

deploy_image:
  stage: deploy
  image: ubuntu:latest
  script:
    - echo "Deploying application to $SERVER_IP"
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "mkdir -p /var/www/html"
    - scp -i $SSH_PRIVATE_KEY ./app.tar.gz $SERVER_USER@$SERVER_IP:/var/www/html/
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "tar -xzvf /var/www/html/app.tar.gz -C /var/www/html/"
```

### Mermaid Diagram of Pipeline Flow

```mermaid
graph TD
  A[Build] --> B[Deploy]
  B --> C[Server]
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Missing Extra Line in SSH Private Key

Ensure that the SSH private key has an extra line at the end. Without this, GitLab may not recognize the file format correctly.

#### Pitfall: Incorrect Permissions on SSH Keys

Ensure that the SSH private key has the correct permissions. The private key should be readable only by the owner.

```bash
chmod 600 id_rsa
```

#### Pitfall: Incorrect Docker Image Selection

Select a Docker image that includes all the necessary utilities required for the job. For example, if you need to use `scp` and `ssh`, ensure the Docker image includes these utilities.

### Real-World Examples and Recent Breaches

Recent breaches often involve misconfigured SSH keys and insecure deployment pipelines. For example, the breach of a major cloud provider in 2021 was partly due to misconfigured SSH keys and insecure deployment scripts.

### How to Prevent / Defend

#### Detection

Regularly audit your GitLab CI/CD configurations and SSH keys. Use tools like `trivy` to scan for vulnerabilities in your Docker images.

#### Prevention

- **Secure SSH Keys**: Ensure SSH keys are stored securely and have the correct permissions.
- **Use Secure Images**: Use trusted Docker images and regularly update them.
- **Audit Logs**: Enable and monitor audit logs for any suspicious activity.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the `.gitlab-ci.yml` configuration:

**Vulnerable Version**

```yaml
deploy_image:
  stage: deploy
  script:
    - echo "Deploying application to $SERVER_IP"
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "mkdir -p /var/www/html"
    - scp -i $SSH_PRIVATE_KEY ./app.tar.gz $SERVER_USER@$SERVER_IP:/var/www/html/
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "tar -xzvf /var/www/html/app.tar.gz -C /var/www/html/"
```

**Secure Version**

```yaml
deploy_image:
  stage: deploy
  script:
    - echo "Deploying application to $SERVER_IP"
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "mkdir -p /var/www/html"
    - scp -i $SSH_PRIVATE_KEY ./app.tar.gz $SERVER_USER@$SERVER_IP:/var/www/html/
    - ssh -i $SSH_PRIVATE_KEY $SERVER_USER@$SERVER_IP "tar -xzvf /var/www/html/app.tar.gz -C /var/www/html/"
  only:
    - master
```

### Conclusion

Setting up a CD pipeline to deploy an application to an EC2 server involves several steps, including configuring SSH keys, defining stages and jobs, and selecting appropriate Docker images. By following best practices and securing your pipeline, you can ensure reliable and secure deployments.

### Practice Labs

For hands-on experience with setting up CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security and CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning security concepts.

By completing these labs, you can gain practical experience in setting up and securing CD pipelines.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Deploy Application to EC2 Server with Release Pipeline/00-Overview|Overview]] | [[02-Introduction to Continuous Delivery (CD) Pipelines Part 2|Introduction to Continuous Delivery (CD) Pipelines Part 2]]

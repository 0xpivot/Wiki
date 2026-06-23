---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines

### Introduction

In the realm of DevSecOps, continuous delivery (CD) pipelines play a crucial role in automating the deployment process. A key component of these pipelines is the GitLab Runner, which executes jobs defined in your pipeline. This chapter delves into configuring a self-managed GitLab Runner, ensuring it has sufficient resources and is properly secured.

### Storage Requirements for GitLab Runner

When setting up a GitLab Runner, one of the critical considerations is the storage space required. The provided transcript mentions that at least 16 GB of space is needed, but it is recommended to allocate 20 GB to ensure there is ample room for the build process.

#### Why 20 GB?

During the build process, the Dockerfile performs several operations such as installing Node.js modules and verifying duplicates. These operations temporarily consume more disk space than the final image size. Here’s a breakdown:

1. **Node Modules Installation**: Installing dependencies via `npm` or `yarn` can take up significant space, especially if there are many modules or large packages.
2. **Temporary Files**: The build process often creates temporary files in `/tmp`, which can add up quickly.
3. **Layer Creation**: Docker builds images layer by layer, and each layer adds to the temporary storage usage.

#### Example Scenario

Consider a Node.js application that requires numerous dependencies. During the build process, the following steps occur:

1. **Cloning Repository**:
    ```bash
    git clone https://gitlab.com/my-project.git
    ```

2. **Installing Dependencies**:
    ```bash
    npm install
    ```

3. **Building Application**:
    ```bash
    npm run build
    ```

Each of these steps can temporarily increase the disk usage significantly.

#### Real-World Example

A recent breach involving a misconfigured GitLab Runner led to a denial-of-service (DoS) condition due to insufficient disk space. In this case, the runner was configured with only 10 GB of storage, leading to frequent failures and downtime. Ensuring adequate storage prevents such issues.

### Launching the Instance

Once the storage requirements are met, the next step is to launch the instance. This involves creating a virtual machine (VM) or container with the necessary specifications.

#### Creating the VM

For this example, we'll use a cloud provider like AWS EC2 to create the VM:

1. **Launch Instance**:
    - Choose an Amazon Machine Image (AMI) suitable for your environment (e.g., Ubuntu Server).
    - Select an instance type (e.g., t2.medium).
    - Allocate 20 GB of storage.
    - Configure security groups and key pairs.

```mermaid
graph LR
  A[Create EC2 Instance] --> B[Choose AMI]
  B --> C[Select Instance Type]
  C --> D[Allocate Storage]
  D --> E[Configure Security Groups]
  E --> F[Create Key Pair]
  F --> G[Launch Instance]
```

### Initializing the GitLab Runner Server

After launching the instance, the next step is to initialize the GitLab Runner server. This involves connecting to the server via SSH and performing initial setup tasks.

#### Connecting via SSH

To connect to the server, use the SSH key pair created earlier:

```bash
ssh -i /path/to/private-key ubuntu@your-instance-public-ip
```

#### Limiting Access to SSH Key File

It is essential to secure the SSH key file to prevent unauthorized access. This can be achieved by setting appropriate permissions:

```bash
chmod 400 /path/to/private-key
```

### Installing and Registering the GitLab Runner

The final step is to install the GitLab Runner software and register it with the GitLab project.

#### Installing GitLab Runner

First, download and install the GitLab Runner package:

```bash
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner
```

#### Registering the Runner

Register the runner with your GitLab project:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Shell Runner" \
  --tag-list "shell,mytags"
```

### Full Example of SSH Connection and Registration

Here is a complete example of connecting to the server via SSH and registering the GitLab Runner:

#### SSH Connection

```bash
ssh -i /path/to/private-key ubuntu@your-instance-public-ip
```

#### Registration Command

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "YOUR_REGISTRATION_TOKEN" \
  --executor "shell" \
  --description "My Shell Runner" \
  --tag-list "shell,mytags"
```

### How to Prevent / Defend

#### Detection

Regularly monitor the disk usage of your GitLab Runner instances to ensure they do not exceed allocated limits. Tools like `df -h` can help check disk space usage.

```bash
df -h
```

#### Prevention

1. **Increase Disk Space**: Ensure the runner has sufficient disk space as discussed earlier.
2. **Optimize Build Process**: Minimize the number of layers and temporary files generated during the build process.
3. **Automated Monitoring**: Set up alerts for low disk space conditions using monitoring tools like Prometheus and Grafana.

#### Secure Coding Fixes

Compare the insecure and secure versions of the Dockerfile:

**Insecure Version**

```Dockerfile
FROM node:14

WORKDIR /app

COPY . .

RUN npm install
RUN npm run build
```

**Secure Version**

```Dockerfile
FROM node:14

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm ci

COPY . .

RUN npm run build
```

### Conclusion

Configuring a self-managed GitLab Runner involves careful consideration of storage requirements, proper initialization, and secure registration with the GitLab project. By following these steps and implementing robust security measures, you can ensure a reliable and efficient CD pipeline.

### Practice Labs

For hands-on experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security.
- **GitLab CI/CD Documentation**: Official GitLab documentation provides detailed guides and examples for setting up CI/CD pipelines.

By completing these labs, you will gain practical experience in configuring and securing GitLab Runners for continuous delivery pipelines.

---
<!-- nav -->
[[05-Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines Part 1|Configuring a Self-Managed GitLab Runner for Continuous Delivery Pipelines Part 1]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[07-Configuring a Self-Managed GitLab Runner for Pipeline Jobs Part 1|Configuring a Self-Managed GitLab Runner for Pipeline Jobs Part 1]]

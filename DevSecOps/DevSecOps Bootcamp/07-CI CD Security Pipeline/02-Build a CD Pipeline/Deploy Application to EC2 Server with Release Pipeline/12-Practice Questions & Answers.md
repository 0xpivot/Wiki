---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of setting up an SSH connection from a GitLab CI/CD pipeline to an EC2 instance.**

To set up an SSH connection from a GitLab CI/CD pipeline to an EC2 instance, you need to perform several steps:

1. **Prepare SSH Key**: Ensure you have an SSH private key that can authenticate against the EC2 instance. This key should be securely stored as a GitLab CI/CD variable, specifically as a file type variable to maintain its integrity.

2. **Define Variables**: In GitLab CI/CD, define variables for the server IP address and the username used to log in to the EC2 instance. These variables will be used in the pipeline configuration.

3. **Install SSH Client**: Use a base Linux image (like Debian Bullseye Slim) and install the OpenSSH client in the pipeline job. This ensures that the necessary SSH commands are available.

4. **Setup SSH Agent**: Start the SSH agent and add the SSH private key to it. This allows the pipeline to use the key without needing to specify it explicitly in each SSH command.

5. **Execute Commands via SSH**: Use the SSH command to execute remote commands on the EC2 instance. For example, pulling a Docker image and running a container.

6. **Manage Permissions**: Ensure the SSH private key and related files have appropriate permissions (e.g., `chmod 400` for the key).

Here’s an example of how to configure the `.gitlab-ci.yml` file:

```yaml
stages:
  - build
  - deploy

deploy_image:
  stage: deploy
  image: debian:buster-slim
  before_script:
    - apt-get update && apt-get install -y openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' > /tmp/id_rsa
    - chmod 400 /tmp/id_rsa
    - ssh-add /tmp/id_rsa
  script:
    - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker pull $IMAGE_NAME"
    - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker stop juice-shop || true"
    - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker rm juice-shop || true"
    - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker run -d -p 3000:3000 --name juice-shop $IMAGE_NAME"
```

**Q2. How would you ensure that the SSH private key is securely managed within the GitLab CI/CD pipeline?**

To ensure that the SSH private key is securely managed within the GitLab CI/CD pipeline, follow these best practices:

1. **Store as a File Type Variable**: Store the SSH private key as a file type variable in GitLab CI/CD. This ensures that the key is treated as a file and not corrupted during transmission.

2. **Set Correct Permissions**: Set the correct permissions on the SSH private key file to prevent unauthorized access. Typically, this involves setting the file permissions to `400` using `chmod`.

3. **Use SSH Agent**: Use the SSH agent to manage the SSH private key. This allows the pipeline to use the key without needing to specify it explicitly in each SSH command, reducing the risk of exposure.

4. **Disable Strict Host Key Checking**: Disable strict host key checking (`StrictHostKeyChecking=no`) to avoid interactive prompts during automated SSH connections.

5. **Limit Access**: Limit access to the GitLab project and the CI/CD variables to only authorized personnel. This reduces the risk of unauthorized access to the SSH private key.

Example of setting up the SSH key in the pipeline:

```yaml
before_script:
  - apt-get update && apt-get install -y openssh-client
  - eval $(ssh-agent -s)
  - echo "$SSH_PRIVATE_KEY" | tr -d '\r' > /tmp/id_rsa
  - chmod 400 /tmp/id_rsa
  - ssh-add /tmp/id_rsa
```

**Q3. Why is it important to stop and remove existing containers before deploying a new version of the application?**

Stopping and removing existing containers before deploying a new version of the application is important for several reasons:

1. **Avoid Port Conflicts**: If a container is already running and listening on a specific port (e.g., 3000), attempting to start another container on the same port will result in a conflict. Stopping and removing the existing container ensures that the new container can start without any port conflicts.

2. **Ensure Clean Deployment**: Removing the existing container ensures that the deployment is clean and that there are no residual processes or data from the previous deployment that could interfere with the new version.

3. **Consistent State**: By stopping and removing the existing container, you ensure that the new container starts in a consistent state, without any lingering issues from the previous deployment.

4. **Resource Management**: Removing the existing container frees up resources (such as memory and CPU) that were being used by the previous container, allowing the new container to utilize these resources effectively.

Example of stopping and removing a container in the pipeline:

```yaml
script:
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker stop juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker rm juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker run -d -p 3000:30_00 --name juice-shop $IMAGE_NAME"
```

**Q4. What are the potential security risks associated with deploying applications to EC2 instances using SSH and how can they be mitigated?**

Deploying applications to EC2 instances using SSH carries several potential security risks:

1. **Exposure of SSH Private Keys**: If the SSH private key is exposed, an attacker could gain unauthorized access to the EC2 instance. To mitigate this, store the SSH private key securely as a GitLab CI/CD variable and limit access to the variable.

2. **Interactive Prompts**: Interactive prompts during SSH connections can disrupt automated deployments. Disabling strict host key checking (`StrictHostKeyChecking=no`) can help automate the process.

3. **Unauthorized Access**: Unauthorized users gaining access to the GitLab project or the SSH private key could deploy malicious code to the EC2 instance. Limit access to the project and the CI/CD variables to only authorized personnel.

4. **Port Security**: Exposing unnecessary ports can increase the attack surface of the EC2 instance. Only open the necessary ports and use security groups to control access.

Mitigation strategies include:

- Storing SSH private keys securely as GitLab CI/CD variables.
- Setting correct permissions on the SSH private key file.
- Using SSH agent to manage the key.
- Disabling strict host key checking.
- Limiting access to the GitLab project and CI/CD variables.
- Configuring security groups to control access to the EC2 instance.

Example of configuring security groups in the pipeline:

```yaml
script:
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker pull $IMAGE_NAME"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker stop juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker rm juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker run -d -p 3000:3000 --name juice-shop $IMAGE_NAME"
```

**Q5. How can you verify that the deployed application is running correctly on the EC2 instance?**

To verify that the deployed application is running correctly on the EC2 instance, you can perform the following checks:

1. **Check Container Status**: Use the `docker ps` command to check if the container is running and to verify its status.

2. **Access Application via Browser**: Open the specified port (e.g., 3000) in the security group and access the application via a web browser to ensure it is accessible and functioning correctly.

3. **Logs and Metrics**: Check the application logs and metrics to ensure that the application is performing as expected and that there are no errors or warnings.

Example of verifying the application in the pipeline:

```yaml
script:
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker pull $IMAGE_NAME"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker stop juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker rm juice-shop || true"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker run -d -p 3000:3000 --name juice-shop $IMAGE_NAME"
  - ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "docker ps"
```

**Q6. What recent real-world examples or CVEs highlight the importance of secure deployment practices?**

Recent real-world examples and CVEs highlight the importance of secure deployment practices:

1. **CVE-2021-20225**: A vulnerability in Kubernetes allowed attackers to bypass authentication and gain unauthorized access to cluster resources. This emphasizes the importance of securing deployment pipelines and ensuring that only authorized personnel can deploy applications.

2. **SolarWinds Supply Chain Attack (2020)**: This attack involved the compromise of software updates, leading to widespread breaches across multiple organizations. This highlights the importance of verifying the integrity of deployed applications and ensuring that deployment processes are secure.

3. **GitHub Actions Vulnerability (CVE-2021-22205)**: A vulnerability in GitHub Actions allowed attackers to execute arbitrary code on GitHub-hosted runners. This underscores the importance of securing deployment pipelines and ensuring that only trusted code is executed.

These examples emphasize the need for robust security measures in deployment pipelines, including secure storage and handling of credentials, verification of application integrity, and limiting access to deployment processes.

---
<!-- nav -->
[[11-Setting Up the Docker Image|Setting Up the Docker Image]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Deploy Application to EC2 Server with Release Pipeline/00-Overview|Overview]]

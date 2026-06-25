---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Environment Variables and Configuration Management in CI/CD Pipelines

In the context of continuous integration and continuous deployment (CI/CD) pipelines, managing configuration settings and environment-specific details is crucial for maintaining consistency across different stages of the development lifecycle. One effective method to achieve this is through the use of environment variables and configuration management techniques. This approach ensures that changes to configuration settings can be made in a centralized location, reducing the likelihood of errors and making maintenance easier.

### What Are Environment Variables?

Environment variables are dynamic-named values that can affect the way running processes behave on a computer. They are used to store information such as paths, database connection strings, API keys, and other sensitive data. In the context of CI/CD pipelines, environment variables can be used to store configuration details such as Docker repository URLs, server addresses, and other runtime parameters.

### Why Use Environment Variables?

Using environment variables in CI/CD pipelines offers several benefits:

1. **Centralized Configuration**: By defining environment variables in a central location, you can ensure that all stages of the pipeline use the same configuration settings. This reduces the risk of inconsistencies and makes it easier to manage changes.
   
2. **Security**: Sensitive information such as API keys and database passwords can be stored securely using environment variables. This helps to protect sensitive data from unauthorized access.

3. **Flexibility**: Environment variables can be easily modified without changing the underlying codebase. This allows you to adapt your pipeline to different environments (e.g., development, testing, production) without having to modify multiple files.

### How to Define Environment Variables in a CI/CD Pipeline

To define environment variables in a CI/CD pipeline, you typically use a configuration file specific to the CI/CD tool you are using. For example, in GitLab CI/CD, you can define environment variables in the `.gitlab-ci.yml` file.

#### Example: Defining Environment Variables in GitLab CI/CD

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_REPO: "my-docker-repo"
  DOCKER_REPO_SERVER: "my-docker-server"

build_job:
  stage: build
  script:
    - echo "Building image in $DOCKER_REPO"
    - docker build -t $DOCKER_REPO .

test_job:
  stage: test
  script:
    - echo "Testing image in $DOCKER_REPO"
    - docker run $DOCKER_REPO

deploy_job:
  stage: deploy
  script:
    - echo "Deploying image to $DOCKER_REPO_SERVER"
    - docker push $DOCKER_REPO
```

In this example, `DOCKER_REPO` and `DOCKER_REPO_SERVER` are defined as environment variables. These variables are then used in the `script` section of each job to perform actions such as building, testing, and deploying Docker images.

### Using Environment Variables in Docker Commands

When working with Docker commands, you can use environment variables to dynamically specify repository URLs and server addresses. This is particularly useful when integrating with services like Amazon Elastic Container Registry (ECR).

#### Example: Using Environment Variables in Docker Commands

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $DOCKER_REPO_SERVER

# Build and tag the Docker image
docker build -t $DOCKER_REPO .

# Push the Docker image to ECR
docker push $DOCKER_REPO
```

In this example, `$DOCKER_REPO_SERVER` is used to specify the server address for the ECR registry, and `$DOCKER_REPO` is used to specify the repository URL.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of properly managing environment variables and configuration settings. For example, in the case of the Capital One breach in 2019, misconfigured environment variables and lack of proper access controls led to the exposure of sensitive customer data.

#### Case Study: Capital One Data Breach

In July 2019, Capital One announced that a hacker had accessed personal information for approximately 100 million customers and potential customers. The breach was caused by a misconfiguration in the company's web application firewall, which allowed the attacker to bypass authentication checks and access sensitive data.

One of the key factors contributing to this breach was the improper handling of environment variables and configuration settings. The web application firewall was configured to allow access to certain resources based on environment variables, but these variables were not properly secured, leading to unauthorized access.

### How to Prevent and Defend Against Misconfigurations

To prevent and defend against misconfigurations and breaches, it is essential to implement robust security practices and configuration management techniques.

#### Secure Configuration Management Practices

1. **Use Centralized Configuration Management Tools**: Tools like Ansible, Terraform, and Helm can help you manage configuration settings in a centralized and consistent manner.

2. **Implement Access Controls**: Ensure that only authorized personnel have access to environment variables and configuration settings. Use role-based access control (RBAC) to restrict access based on user roles.

3. **Audit and Monitor Configuration Changes**: Regularly audit and monitor configuration changes to detect and respond to unauthorized modifications. Use tools like AWS Config and CloudTrail to track changes to your infrastructure.

4. **Use Secrets Management Tools**: Store sensitive information such as API keys and database passwords using secrets management tools like HashiCorp Vault or AWS Secrets Manager.

#### Secure Coding Practices

1. **Avoid Hardcoding Sensitive Information**: Avoid hardcoding sensitive information such as API keys and database passwords in your codebase. Instead, use environment variables to store this information.

2. **Validate Input**: Validate input from environment variables to ensure that it meets expected criteria. This can help prevent injection attacks and other types of vulnerabilities.

3. **Use Secure Defaults**: Configure your applications and services to use secure defaults. For example, disable unnecessary features and services to reduce the attack surface.

#### Example: Secure Configuration Management with Ansible

```yaml
---
- name: Configure Docker Repository
  hosts: all
  vars:
    docker_repo: "my-docker-repo"
    docker_repo_server: "my-docker-server"

  tasks:
    - name: Set Docker Repository Variable
      set_fact:
        docker_repo: "{{ docker_repo }}"
        docker_repo_server: "{{ docker_repo_server }}"

    - name: Login to ECR
      shell: |
        aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin {{ docker_repo_server }}

    - name: Build and Tag Docker Image
      shell: |
        docker build -t {{ docker_repo }} .

    - name: Push Docker Image to ECR
      shell: |
        docker push {{ docker_repo }}
```

In this example, Ansible is used to configure the Docker repository and server variables. The `set_fact` module is used to set the variables, and the `shell` module is used to execute the Docker commands.

### Conclusion

Properly managing environment variables and configuration settings is critical for maintaining the security and consistency of CI/CD pipelines. By using environment variables and configuration management tools, you can centralize configuration settings, reduce the risk of errors, and improve the overall security of your pipeline.

### Practice Labs

For hands-on practice with environment variables and configuration management in CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including topics related to environment variables and configuration management.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice secure coding and configuration management techniques.
- **GitLab CI/CD Documentation**: Provides detailed documentation and examples for setting up and configuring CI/CD pipelines using GitLab.

By following these guidelines and practicing with real-world examples, you can gain a deep understanding of how to effectively manage environment variables and configuration settings in CI/CD pipelines.

---
<!-- nav -->
[[06-Introduction to Docker Registries and AWS ECR|Introduction to Docker Registries and AWS ECR]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/18-Replacing Docker Hub with AWS ECR/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/18-Replacing Docker Hub with AWS ECR/08-Practice Questions & Answers|Practice Questions & Answers]]

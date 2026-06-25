---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Setting Up Environment Variables Globally

### Background Theory

In a Continuous Integration/Continuous Deployment (CI/CD) pipeline, environment variables play a crucial role in managing configurations and secrets. By setting these variables globally, you ensure that they are accessible to all jobs within the pipeline. This approach simplifies the management of shared configurations and reduces redundancy, making your pipeline more maintainable and less error-prone.

### Why Set Variables Globally?

Setting environment variables globally allows you to avoid defining them repeatedly for each job. This is particularly useful when you have multiple jobs that require the same set of variables, such as AWS credentials, Docker registry URLs, or any other configuration parameters. Additionally, global variables help in maintaining consistency across different stages of the pipeline.

### How to Set Variables Globally

To set environment variables globally, you typically configure them in the pipeline definition file (e.g., `.gitlab-ci.yml` for GitLab CI/CD). Here’s an example of how you might set up global environment variables in a GitLab CI/CD pipeline:

```yaml
variables:
  AWS_ACCESS_KEY_ID: "your_access_key_id"
  AWS_SECRET_ACCESS_KEY: "your_secret_access_key"
  AWS_DEFAULT_REGION: "us-west-2"
  DOCKER_REGISTRY_URL: "your_docker_registry_url"

stages:
  - build
  - test
  - deploy

build_image:
  stage: build
  script:
    - echo "Building the Docker image..."
    - docker build -t $DOCKER_REGISTRY_URL/myapp:$CI_COMMIT_SHORT_SHA .
    - docker build -t $DOCKER_REGISTRY_URL/myapp:latest .

test_image:
  stage: test
  script:
    - echo "Running tests..."
    - docker run $DOCKER_REGISTRY_URL/myapp:$CI_COMMIT_SHORT_SHA /bin/sh -c "pytest"

deploy_to_ecr:
  stage: deploy
  script:
    - echo "Deploying to ECR..."
    - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $DOCKER_REGISTRY_URL
    - docker push $DOCKER_REGISTRY_URL/myapp:$CI_COMMIT_SHORT_SHA
    - docker push $DOCKER_REGISTRY_URL/myapp:latest
```

### Pitfalls and Best Practices

#### Pitfall: Hardcoding Secrets

Hardcoding sensitive information like AWS access keys directly in the pipeline configuration file is a significant security risk. If the file is committed to a version control system, it could expose your credentials to unauthorized users.

#### Best Practice: Use Secure Storage

Use secure storage mechanisms provided by your CI/CD platform to manage secrets. For example, GitLab CI/CD supports secret variables that are encrypted and stored securely. You can define these variables in the GitLab UI and reference them in your pipeline configuration without exposing them in plain text.

```yaml
variables:
  AWS_ACCESS_KEY_ID: "$AWS_ACCESS_KEY_ID"
  AWS_SECRET_ACCESS_KEY: "$AWS_SECRET_ACCESS_KEY"
  AWS_DEFAULT_REGION: "us-west-2"
  DOCKER_REGISTRY_URL: "your_docker_registry_url"
```

### How to Prevent / Defend

#### Detection

Regularly audit your pipeline configuration files to ensure that no sensitive information is hardcoded. Use tools like `grep` to search for patterns that might indicate hardcoded secrets.

```sh
grep -r "AWS_ACCESS_KEY_ID" .
```

#### Prevention

1. **Use Secret Management Tools**: Leverage built-in secret management features of your CI/CD platform.
2. **Environment Variable Encryption**: Encrypt sensitive environment variables before storing them.
3. **Least Privilege Principle**: Ensure that the credentials used in the pipeline have the minimum necessary permissions.

### Real-World Example

Consider a scenario where a company’s CI/CD pipeline was compromised due to hardcoded AWS credentials. An attacker gained access to the pipeline configuration file and extracted the credentials, leading to unauthorized access to the company’s AWS resources. This breach could have been prevented by using secure storage mechanisms for managing secrets.

---
<!-- nav -->
[[15-Real-World Examples and Recent CVEs|Real-World Examples and Recent CVEs]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[17-Setting Up Environment Variables for AWS ECR Integration|Setting Up Environment Variables for AWS ECR Integration]]

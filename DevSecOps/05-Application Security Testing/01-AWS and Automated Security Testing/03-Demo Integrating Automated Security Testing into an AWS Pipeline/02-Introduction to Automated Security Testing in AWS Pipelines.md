---
course: DevSecOps
topic: AWS and Automated Security Testing
tags: [devsecops]
---

## Introduction to Automated Security Testing in AWS Pipelines

Automated security testing is a critical component of modern DevSecOps practices. By integrating security testing into your continuous integration and continuous delivery (CI/CD) pipelines, you can ensure that your applications are secure throughout their development lifecycle. In this section, we will focus on integrating automated security testing into an AWS CodePipeline, specifically using a tool called HadoLint.

### What is HadoLint?

HadoLint is a static analysis tool designed to identify potential security vulnerabilities and coding issues in Haskell codebases. While the original context might have been specific to Haskell, the principles and techniques can be applied to other languages and tools as well. HadoLint helps developers catch issues early in the development process, reducing the likelihood of security vulnerabilities making it into production.

#### Why Use HadoLint?

Using HadoLint in your CI/CD pipeline offers several benefits:

1. **Early Detection**: Identifies security issues and coding problems early in the development cycle.
2. **Consistency**: Ensures that all code adheres to a set of predefined rules and standards.
3. **Automation**: Automates the process of checking code, freeing up developers to focus on more complex tasks.
4. **Integration**: Can be easily integrated into existing CI/CD pipelines, such as AWS CodePipeline.

### Setting Up HadoLint in an AWS CodePipeline

To integrate HadoLint into an AWS CodePipeline, we need to define a new stage in the pipeline that will execute the HadoLint tool. This involves creating a new build project that uses a Docker image containing HadoLint.

#### Step-by-Step Guide

1. **Define the New Stage**:
   - Add a new stage to your pipeline that will run the HadoLint tool.
   - This stage will pull a Docker image containing HadoLint, execute the tool, and print the results.

2. **Create the Build Spec File**:
   - The build spec file (`buildspec.yml`) defines the steps that will be executed during the build process.
   - This file should specify the Docker image to use, the commands to run, and how to handle the output.

Here is an example `buildspec.yml` file:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      docker: 19
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - $(aws ecr get-login --no-include-email --region us-west-2)
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t hadolint .
      - docker tag hadolint:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
      - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
  post_build:
    commands:
      - echo Build completed on `date`
```

3. **Create the Build Project**:
   - Navigate to the AWS CodeBuild console.
   - Create a new build project using the `buildspec.yml` file.
   - Configure the project to use the specified Docker image and environment settings.

#### Detailed Configuration Steps

1. **Open the Build Menu**:
   - In the AWS CodePipeline console, navigate to the build menu on the left-hand side.
   - Collapse the source menu as it is no longer needed.

2. **Create a New Build Project**:
   - Click on "Build Project" and then "Create build project".
   - Name the project (e.g., "Lint").
   - Provide a description (e.g., "Lint Docker file using the tool HadoLint").

3. **Configure Input Source**:
   - Select the source provider for the stage (e.g., your repository).
   - Choose the repository and branch that contains the `buildspec.yml` file.

4. **Select Environment Settings**:
   - Scroll down to the "Environment" section.
   - Select the Docker container that will run the `buildspec.yml` file.
   - Choose "Amazon Linux" as the operating system.
   - Use the default runtime standard.
   - Select the latest Docker image (e.g., "standard:3.0").

### Example of Full HTTP Request and Response

When setting up the build project, you might interact with the AWS API to configure the build project programmatically. Here is an example of a full HTTP request and response:

```http
POST /build/projects HTTP/1.1
Host: codebuild.us-west-2.amazonaws.com
Content-Type: application/json
Authorization: Bearer <your-access-token>

{
  "name": "Lint",
  "description": "Lint Docker file using the tool HadoLint",
  "source": {
    "type": "GITHUB",
    "location": "https://github.com/your-repo/Tools-Image.git",
    "branch": "Builder"
  },
  "environment": {
    "type": "LINUX_CONTAINER",
    "image": "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
  }
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "project": {
    "name": "Lint",
    "arn": "arn:aws:codebuild:us-west-2:123456789012:project/Lint",
    "description": "Lint Docker file using the tool HadoLint",
    "source": {
      "type": "GITHUB",
      "location": "https://github.com/your-repo//Tools-Image.git",
      "branch": "Builder"
    },
    "environment": {
      "type": "LINUX_CONTAINER",
      "image": "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    }
  }
}
```

### Common Pitfalls and How to Avoid Them

1. **Incorrect Docker Image**:
   - Ensure that the Docker image used contains the necessary tools (e.g., HadoLint).
   - Verify the image tag and version to avoid compatibility issues.

2. **Misconfigured Build Spec**:
   - Double-check the `buildspec.yml` file for correct syntax and commands.
   - Test the build locally before deploying it to the pipeline.

3. **Security Vulnerabilities**:
   - Regularly update the Docker images and tools to mitigate known vulnerabilities.
   - Use tools like `hadolint` to check for security issues in the Dockerfile itself.

### How to Prevent / Defend

1. **Detection**:
   - Use AWS CloudTrail to monitor API calls related to CodeBuild and CodePipeline.
   - Set up alerts for unusual activity or changes to the build projects.

2. **Prevention**:
   - Implement least privilege access control for IAM roles used by CodeBuild.
   - Use AWS Secrets Manager to securely store sensitive data used in the build process.

3. **Secure Coding Fixes**:
   - Compare the vulnerable and secure versions of the `buildspec.yml` file:

   **Vulnerable Version**:
   ```yaml
   version: 0.2

   phases:
     install:
       runtime-versions:
         docker: 19
     pre_build:
       commands:
         - echo Logging in to Amazon ECR...
         - $(aws ecr get-login --no-include-email --region us-west-2)
     build:
       commands:
         - echo Build started on `date`
         - echo Building the Docker image...
         - docker build -t hadolint .
         - docker tag hadolint:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
         - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
     post_build:
       commands:
         - echo Build completed on `date`
   ```

   **Secure Version**:
   ```yaml
   version: 0.2

   phases:
     install:
       runtime-versions:
         docker: 19
     pre_build:
       commands:
         - echo Logging in to Amazon ECR...
         - $(aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com)
     build:
       commands:
         - echo Build started on `date`
         - echo Building the Docker image...
         - docker build -t hadolint .
         - docker tag hadolint:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
         - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/hadolint:latest
     post_build:
       commands:
         - echo Build completed on `date`
   ```

4. **Configuration Hardening**:
   - Use AWS Config to monitor and enforce compliance with security best practices.
   - Enable AWS GuardDuty to detect anomalous activity in your AWS environment.

### Real-World Examples and Recent Breaches

Recent breaches and CVEs highlight the importance of integrating security testing into CI/CD pipelines:

- **CVE-2021-44228 (Log4j)**: A widely exploited vulnerability that could have been detected earlier with proper static analysis tools.
- **SolarWinds Supply Chain Attack**: Emphasizes the need for comprehensive security checks in third-party dependencies.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers extensive modules on web application security.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security testing.
- **CloudGoat**: Provides scenarios for learning and practicing cloud security on AWS.

By integrating HadoLint into your AWS CodePipeline, you can significantly enhance the security of your applications through automated static analysis. This approach ensures that security issues are caught early, reducing the risk of vulnerabilities making it into production.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/03-Demo Integrating Automated Security Testing into an AWS Pipeline/01-Introduction to AWS and Automated Security Testing|Introduction to AWS and Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/03-Demo Integrating Automated Security Testing into an AWS Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/03-Demo Integrating Automated Security Testing into an AWS Pipeline/03-Practice Questions & Answers|Practice Questions & Answers]]

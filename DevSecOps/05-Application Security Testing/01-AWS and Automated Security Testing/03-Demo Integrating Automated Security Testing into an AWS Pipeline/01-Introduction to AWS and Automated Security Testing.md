---
course: DevSecOps
topic: AWS and Automated Security Testing
tags: [devsecops]
---

## Introduction to AWS and Automated Security Testing

In this section, we will delve into the process of integrating automated security testing into an existing AWS pipeline. This is a crucial step in ensuring that your applications are secure throughout their development lifecycle. We will cover the necessary steps to modify an existing pipeline, add a linting check for a Docker image, and modify the check as needed. 

### Background Theory

Before diving into the practical aspects, it's essential to understand the theoretical foundations behind these concepts.

#### What is an AWS Pipeline?

An AWS Pipeline is a service that automates the release process of your applications. It allows you to model your release process as a series of stages, such as source, build, test, and deploy. Each stage can have one or more actions associated with it, such as building a Docker image, running tests, or deploying the application.

#### Why Automate Security Testing?

Automating security testing is critical because it ensures that security checks are consistently applied throughout the development process. Manual security testing can be time-consuming and prone to human error, whereas automated testing can catch issues early and often, reducing the risk of vulnerabilities making it into production.

#### How Does AWS Support Automated Security Testing?

AWS provides several services that can be integrated into a pipeline to perform automated security testing:

- **CodeBuild**: A fully managed build service that compiles source code, runs tests, and produces artifacts that are ready to deploy.
- **CodePipeline**: A fully managed continuous delivery service that helps you automate your release processes.
- **Amazon Inspector**: An automated security assessment service that helps improve the security and compliance of applications deployed on AWS.
- **AWS Lambda**: A serverless compute service that can run security checks and other tasks without provisioning or managing servers.

### Setting Up the Environment

To follow along with this demo, ensure you have the following:

- An AWS account with appropriate permissions.
- Access to the AWS Management Console.
- A GitHub repository containing the source code for your application.

### Step-by-Step Guide

#### Step 1: Modify an Existing Pipeline

The first step is to modify an existing pipeline to include automated security testing. We will start by navigating to the AWS Management Console and locating the Code Pipeline service.

```mermaid
flowchart LR
    A[Login to AWS Console] --> B[Search for Code Pipeline]
    B --> C[Click on Code Pipeline]
    C --> D[Select Existing Pipeline]
```

1. **Login to AWS Console**: Ensure you are logged into your AWS account.
2. **Search for Code Pipeline**: Use the search bar in the AWS Management Console to find the Code Pipeline service.
3. **Click on Code Pipeline**: Once you've located the Code Pipeline service, click on it to access the list of pipelines.
4. **Select Existing Pipeline**: Identify the pipeline you want to modify. In this case, we will use the `Tools Image` pipeline.

#### Step 2: Add a Linting Check for a Docker Image

Next, we will add a linting check to the pipeline to ensure that the Docker image is free of common security issues.

```mermaid
sequenceDiagram
    participant User
    participant CodePipeline
    participant CodeBuild
    User->>CodePipeline: Click on Tools Image Pipeline
    CodePipeline-->>User: Display Current Pipeline Stages
    User->>CodeBuild: Add Linting Stage
    CodeBuild-->>User: Confirm Linting Stage Added
```

1. **Click on Tools Image Pipeline**: Navigate to the `Tools Image` pipeline.
2. **Display Current Pipeline Stages**: Observe the current stages in the pipeline, which include `Source`, `Build`, and `Push`.
3. **Add Linting Stage**: Add a new stage to the pipeline for linting the Docker image. This can be done by editing the pipeline configuration and adding a new action.

#### Step 3: Modify the Linting Check

Once the linting stage is added, we need to modify the check to ensure it performs the desired security tests.

```mermaid
flowchart LR
    A[Edit Pipeline Configuration] --> B[Add Linting Action]
    B --> C[Configure Linting Action]
    C --> D[Save Changes]
```

1. **Edit Pipeline Configuration**: Edit the pipeline configuration to add a new action for linting.
2. **Add Linting Action**: Add a new action to the pipeline that will perform the linting check.
3. **Configure Linting Action**: Configure the linting action to use a tool like `Hadolint` or `Clair`.

### Example Code and Configurations

Let's walk through a detailed example of how to set up the linting stage using `Hadolint`.

#### Dockerfile Example

Here is an example Dockerfile that we will use for this demonstration:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

#### Hadolint Configuration

To integrate `Hadolint` into the pipeline, we need to create a `buildspec.yml` file that defines the build and linting phases.

```yaml
version: 0.2

phases:
  install:
    commands:
      - apt-get update && apt-get install -y hadolint
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - $(aws ecr get-login --no-include-email --region us-west-2)
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t my-docker-image .
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Running Hadolint...
      - hadolint Dockerfile
  push:
    commands:
      - echo Pushing the Docker image...
      - docker tag my-docker-image:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-docker-image:latest
      - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-docker-image:latest
```

### Real-World Examples and Recent Breaches

#### Example: Docker Image Vulnerabilities

One of the most common vulnerabilities in Docker images is the presence of outdated or insecure packages. For instance, the Heartbleed vulnerability (CVE-2014-0160) affected OpenSSL and was present in many Docker images until they were updated.

By integrating automated security testing into your pipeline, you can catch such vulnerabilities early and ensure that your images are secure.

### Pitfalls and Common Mistakes

#### Common Mistakes

1. **Skipping Security Checks**: One of the most common mistakes is skipping security checks altogether. This leaves your application vulnerable to attacks.
2. **Incomplete Security Checks**: Another mistake is performing incomplete security checks. For example, only checking for known vulnerabilities but not for misconfigurations or other security issues.
3. **Ignoring False Positives**: Automated tools can sometimes generate false positives. Ignoring these can lead to important security issues being overlooked.

### How to Prevent / Defend

#### Detection

To detect security issues in your Docker images, you can use tools like `Hadolint` or `Clair`. These tools can scan your Dockerfiles and images for known vulnerabilities and misconfigurations.

#### Prevention

To prevent security issues, ensure that you:

1. **Keep Dependencies Updated**: Regularly update your dependencies to the latest versions.
2. **Use Secure Base Images**: Use base images that are known to be secure and regularly maintained.
3. **Run Security Scans**: Integrate security scans into your pipeline to catch issues early.

#### Secure Coding Fixes

Here is an example of a vulnerable Dockerfile and its secure counterpart:

**Vulnerable Dockerfile**

```Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]
```

**Secure Dockerfile**

```Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["python", "app.py"]
```

In the secure version, we first copy and install the dependencies separately to avoid caching issues and ensure that the dependencies are up-to-date.

### Complete Example with Raw HTTP Messages

#### Full HTTP Request and Response

When interacting with the AWS API to manage your pipeline, you might send a request like this:

```http
POST /codepipeline/pipelines HTTP/1.1
Host: codepipeline.us-west-2.amazonaws.com
Content-Type: application/json
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20170320/us-west-2/codepipeline/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5f80f77d5fa3beca038a28c952e1e967f8554e6b4f69ae9d90425e4eb08fn1
X-Amz-Date: 20170320T193642Z

{
  "pipeline": {
    "name": "Tools Image",
    "version": 1,
    "stages": [
      {
        "name": "Source",
        "actions": [
          {
            "name": "SourceAction",
            "actionTypeId": {
              "category": "Source",
              "owner": "AWS",
              "provider": "CodeCommit",
              "version": "1"
            },
            "configuration": {
              "RepositoryName": "Tools Image",
              "BranchName": "master"
            }
          }
        ]
      },
      {
        "name": "Build",
        "actions": [
          {
            "name": "BuildAction",
            "actionTypeId": {
              "category": "Build",
              "owner": "AWS",
              "provider": "CodeBuild",
              "version": "1"
            },
            "configuration": {
              "ProjectName": "Tools Image Build"
            }
          }
        ]
      },
      {
        "name": "Lint",
        "actions": [
          {
            "name": "LintAction",
            "actionTypeId": {
              "category": "Test",
              "owner": "Custom",
              "provider": "Hadolint",
              "version": "1"
            },
            "configuration": {
              "Command": "hadolint Dockerfile"
            }
          }
        ]
      },
      {
        "name": "Push",
        "actions": [
          {
            "name": "PushAction",
            "actionTypeId": {
              "category": "Deploy",
              "owner": "AWS",
              "provider": "ECS",
              "version": "1"
            },
            "configuration": {
              "ClusterName": "my-cluster",
              "ServiceName": "my-service",
              "ImageTag": "latest"
            }
          }
        ]
      }
    ]
  }
}
```

#### Expected Result

The expected result of this request would be a successful creation or modification of the pipeline with the added linting stage.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified security training application.

These labs provide a practical way to apply the concepts learned in this chapter.

### Conclusion

Integrating automated security testing into your AWS pipeline is a critical step in ensuring the security of your applications. By following the steps outlined in this chapter, you can effectively add security checks to your pipeline and catch potential vulnerabilities early in the development process.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/03-Demo Integrating Automated Security Testing into an AWS Pipeline/00-Overview|Overview]] | [[02-Introduction to Automated Security Testing in AWS Pipelines|Introduction to Automated Security Testing in AWS Pipelines]]

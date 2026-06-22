---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Overview of a CI/CD Pipeline

### Introduction to CI/CD Pipelines

Continuous Integration and Continuous Deployment (CI/CD) pipelines are essential components of modern DevSecOps practices. They automate the process of integrating code changes from multiple contributors into a shared repository and deploying those changes to production environments. This automation ensures that the software is built, tested, and deployed consistently and reliably.

### Components of a CI/CD Pipeline

A typical CI/CD pipeline consists of several stages:

1. **Source Control Management (SCM)**: This is where the code is stored and managed. Common tools include Git, SVN, and Bitbucket.
2. **Build**: This stage compiles the code and packages it into a deployable artifact.
3. **Test**: Automated tests are run to ensure the code meets quality standards.
4. **Security Scans**: Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and Secret Scanning are performed to identify vulnerabilities.
5. **Deploy**: The artifact is deployed to a staging or production environment.
6. **Monitor**: Post-deployment monitoring ensures the application is running as expected.

### Setting Up a CI/CD Pipeline

#### Source Control Management (SCM)

The first step in setting up a CI/CD pipeline is to establish a source control management system. Git is one of the most popular choices due to its distributed nature and robust feature set.

```markdown
# Example Git Repository Setup

1. Initialize a new Git repository:
    ```bash
    git init
    ```

2. Add files to the repository:
    ```bash
    git add .
    ```

3. Commit the changes:
    ```bash
    git commit -m "Initial commit"
    ```

4. Push the repository to a remote server (e.g., GitHub):
    ```bash
    git remote add origin https://github.com/username/repository.git
    git push -u origin master
    ```
```

### Build Stage

The build stage compiles the code and packages it into a deployable artifact. This can involve compiling source code, running unit tests, and creating Docker images.

#### Example: Building a Docker Image

```dockerfile
# Dockerfile Example

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

To build the Docker image:

```bash
docker build -t myapp:latest .
```

### Test Stage

Automated testing is crucial to ensure the code meets quality standards. Tests can be categorized into unit tests, integration tests, and end-to-end tests.

#### Example: Running Unit Tests with Pytest

```python
# test_example.py

import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 2 - 1 == 1
```

Run the tests using Pytest:

```bash
pytest
```

### Security Scans

Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and Secret Scanning are essential to identify vulnerabilities in the codebase.

#### Example: Using SonarQube for SAST

SonarQube is a popular tool for performing SAST. It integrates with CI/CD pipelines to automatically scan the code for vulnerabilities.

```yaml
# Jenkinsfile Example

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }
        stage('Security Scan') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }
    }
}
```

### Deploy Stage

The deploy stage involves pushing the artifact to a staging or production environment. This can be done using various tools such as Ansible, Kubernetes, or AWS services.

#### Example: Deploying to AWS EC2

```yaml
# CloudFormation Template Example

Resources:
  MyInstance:
    Type: 'AWS::EC2::Instance'
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t2.micro
      KeyName: my-key-pair
      SecurityGroupIds:
        - !Ref MySecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker
          service docker start
          usermod -a -G docker ec2-user
          docker run -d -p 80:80 myapp:latest

  MySecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupDescription: Enable HTTP access
      VpcId: vpc-0123456789abcdef0
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
```

### Monitor Stage

Post-deployment monitoring ensures the application is running as expected. Tools like Prometheus, Grafana, and ELK Stack can be used for monitoring.

#### Example: Monitoring with Prometheus

Prometheus is an open-source monitoring system and time series database. It collects metrics from configured targets at specified intervals and stores them internally.

```yaml
# prometheus.yml Example

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Adding Continuous Deployment (CD)

The current pipeline tests the application, scans for security issues, builds the Docker image, and pushes it to the Docker registry. However, to complete the release pipeline, we need to add the continuous deployment (CD) part.

#### Example: Deploying to AWS ECS

Elastic Container Service (ECS) is a fully managed container orchestration service provided by AWS. It allows you to run and scale containerized applications easily.

```yaml
# CloudFormation Template Example

Resources:
  MyCluster:
    Type: 'AWS::ECS::Cluster'
    Properties:
      ClusterName: MyCluster

  MyTaskDefinition:
    Type: 'AWS::ECS::TaskDefinition'
    Properties:
      Family: MyTask
      ContainerDefinitions:
        - Name: MyApp
          Image: myapp:latest
          Memory: 128
          PortMappings:
            - ContainerPort: 80

  MyService:
    Type: 'AWS::ECS::Service'
    Properties:
      Cluster: !Ref MyCluster
      TaskDefinition: !Ref MyTaskDefinition
      DesiredCount: 1
      LoadBalancers:
        - TargetGroupArn: !Ref MyTargetGroup
          ContainerName: MyApp
          ContainerPort: 80

  MyLoadBalancer:
    Type: 'AWS::ElasticLoadBalancingV2::LoadBalancer'
    Properties:
      Name: MyLoadBalancer
      Scheme: internet-facing
      Subnets:
        - subnet-0123456789abcdef0
        - subnet-0123456789abcdef1
      SecurityGroups:
        - !Ref MySecurityGroup

  MyTargetGroup:
    Type: 'AWS::ElasticLoadBalancingV2::TargetGroup'
    Properties:
      Name: MyTargetGroup
      Protocol: HTTP
      Port: 80
      VpcId: vpc-0123456789abcdef0
      HealthCheckPath: /

  MyListener:
    Type: 'AWS::ElasticLoadBalancingV2::Listener'
    Properties:
      LoadBalancerArn: !Ref MyLoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref MyTargetGroup
```

### How to Prevent / Defend

#### Vulnerability Detection and Prevention

1. **Regular Security Scans**: Use tools like SonarQube, OWASP ZAP, and TruffleHog to regularly scan the codebase for vulnerabilities.
2. **Secure Coding Practices**: Follow secure coding guidelines such as OWASP Top Ten and CWE (Common Weakness Enumeration).
3. **Configuration Hardening**: Harden the configuration of your infrastructure using tools like AWS Security Hub and CIS Benchmarks.
4. **Monitoring and Logging**: Implement comprehensive monitoring and logging to detect and respond to security incidents promptly.

#### Example: Secure Code Fix

**Vulnerable Code**

```python
# Vulnerable Code Example

import os

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()
```

**Fixed Code**

```python
# Fixed Code Example

import os

def read_file(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            return f.read()
    else:
        raise FileNotFoundError("File not found")
```

### Real-World Examples

#### Recent CVEs and Breaches

1. **CVE-2021-44228 (Log4Shell)**: A critical vulnerability in Apache Log4j that allowed attackers to execute arbitrary code on affected systems. This highlights the importance of regular security scans and keeping dependencies up to date.
2. **SolarWinds Supply Chain Attack (2020)**: A sophisticated supply chain attack that compromised SolarWinds Orion software, leading to widespread breaches across multiple organizations. This underscores the need for robust security practices throughout the entire software development lifecycle.

### Hands-On Labs

For hands-on practice with CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **CloudGoat**: A collection of vulnerable AWS configurations for learning cloud security.
- **Pacu**: A framework for automating AWS security assessments.

These labs provide practical experience in setting up and securing CI/CD pipelines.

### Conclusion

Setting up a CI/CD pipeline is a critical step in modern DevSecOps practices. By automating the integration, testing, and deployment processes, teams can ensure that their applications are built, tested, and deployed consistently and reliably. Regular security scans, secure coding practices, and comprehensive monitoring are essential to maintaining the security of the pipeline and the applications it deploys.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/02-Overview of a CICD Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/02-Overview of a CICD Pipeline/02-Practice Questions & Answers|Practice Questions & Answers]]

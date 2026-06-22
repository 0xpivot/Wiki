---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Overview of Automated Application Code and Image Scanning Steps

In the realm of DevSecOps, ensuring the security of both application code and the runtime environment is paramount. This chapter delves into the process of securing Docker images through automated scanning and extends this discussion to the deployment phase, particularly focusing on AWS EC2 environments.

### Application Code Scans

Before diving into Docker image scanning, it’s essential to understand the importance of application code scans. These scans aim to identify vulnerabilities and coding errors within the source code itself. Tools like SonarQube, Fortify, and Veracode are commonly used for this purpose.

#### Why Application Code Scans Matter

Application code scans help in identifying issues such as SQL injection, cross-site scripting (XSS), and buffer overflows. These vulnerabilities can lead to severe security breaches if left unaddressed. For instance, the Equifax breach in 2017 was partly due to an unpatched Apache Struts vulnerability, which could have been detected through proper code scanning.

#### How Application Code Scans Work

Code scanning tools typically analyze the source code using static analysis techniques. They look for patterns that indicate potential security issues and provide detailed reports. Here’s a simplified example of how a code scan might work:

```python
# Vulnerable code snippet
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    result = execute_query(query)
    return result

# Secure code snippet
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,))
    return result
```

In the first snippet, the `user_id` is concatenated directly into the SQL query, leading to a potential SQL injection vulnerability. In the second snippet, parameterized queries are used, which mitigate this risk.

### Docker Image Scans

Once the application code is scanned and secured, the next step is to ensure the Docker images used to deploy the application are also free from vulnerabilities. Docker image scanning tools like Clair, Trivy, and Aqua Security can be integrated into the CI/CD pipeline to automatically scan Docker images.

#### Why Docker Image Scans Matter

Docker images often contain base operating systems and libraries that may have known vulnerabilities. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous Docker images that included the vulnerable library. By scanning Docker images, these vulnerabilities can be identified and addressed before the images are deployed.

#### How Docker Image Scans Work

Docker image scanning tools analyze the layers of a Docker image to identify known vulnerabilities. They compare the packages and libraries within the image against a database of known vulnerabilities. Here’s an example of how to use Trivy to scan a Docker image:

```sh
trivy image my-docker-image:latest
```

This command will output a report detailing any vulnerabilities found in the Docker image.

### Deployment Environment Security

After ensuring the application code and Docker images are secure, the next critical step is securing the deployment environment. In this context, we focus on AWS EC2 instances.

#### Why Deployment Environment Security Matters

The deployment environment is the final frontier where the application runs. Any vulnerabilities in this environment can be exploited to gain unauthorized access. For example, the Capital One breach in 2019 was due to misconfigured AWS S3 buckets, which allowed unauthorized access to sensitive data.

#### How to Secure Deployment Environments

To secure deployment environments, several best practices should be followed:

1. **Least Privilege Principle**: Ensure that EC2 instances have the minimum necessary permissions to perform their tasks.
2. **Network Segmentation**: Use VPCs and security groups to isolate different parts of the infrastructure.
3. **Regular Patch Management**: Keep all software and dependencies up to date with the latest security patches.

Here’s an example of how to configure a security group in AWS:

```json
{
  "GroupId": "sg-0123456789abcdef0",
  "GroupName": "web-server-sg",
  "IpPermissions": [
    {
      "FromPort": 80,
      "ToPort": 80,
      "IpProtocol": "tcp",
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    },
    {
      "FromPort": 443,
      "ToPort": 443,
      "IpProtocol": "tcp",
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    }
  ]
}
```

This configuration allows inbound traffic on ports 80 and 443, which are commonly used for HTTP and HTTPS traffic.

### Integration with CI/CD Pipeline

To ensure continuous security, it’s crucial to integrate these security checks into the CI/CD pipeline. This ensures that every build and deployment undergoes thorough security validation.

#### Example CI/CD Pipeline Configuration

Here’s an example of a CI/CD pipeline configuration using Jenkins:

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-docker-image .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run my-docker-image pytest'
            }
        }
        stage('Scan') {
            steps {
                sh 'trivy image my-docker-image:latest'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def credentialsId = 'aws-credentials'
                    def region = 'us-east-1'
                    def instanceType = 't2.micro'
                    def ami = 'ami-0c55b159cbfafe1f0'

                    def ec2 = new AmazonWebServices(credentialsId)
                    def instance = ec2.createInstance(region, instanceType, ami)

                    // Additional deployment steps
                }
            }
        }
    }
}
```

This pipeline includes stages for building the Docker image, running tests, scanning the image for vulnerabilities, and deploying to an EC2 instance.

### Real-World Examples and Recent Breaches

Several recent breaches highlight the importance of comprehensive security measures:

1. **Equifax Breach (2017)**: An unpatched Apache Struts vulnerability led to the exposure of sensitive personal data.
2. **Capital One Breach (2019)**: Misconfigured AWS S3 buckets allowed unauthorized access to customer data.
3. **SolarWinds Supply Chain Attack (2020)**: Malware was injected into SolarWinds software updates, compromising numerous organizations.

These examples underscore the need for robust security practices at every stage of the development and deployment lifecycle.

### How to Prevent / Defend

#### Detection

Regularly scan your application code and Docker images using tools like SonarQube and Trivy. Monitor your deployment environment for unusual activity using AWS CloudTrail and CloudWatch.

#### Prevention

1. **Secure Coding Practices**: Follow secure coding guidelines and regularly review code for vulnerabilities.
2. **Automated Scanning**: Integrate automated scanning tools into your CI/CD pipeline.
3. **Patch Management**: Regularly update all software and dependencies to the latest versions.
4. **Least Privilege**: Ensure that EC2 instances have the minimum necessary permissions.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of code snippets:

**Vulnerable Code**
```python
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    result = execute_query(query)
    return result
```

**Secure Code**
```python
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,))
    return result
```

#### Configuration Hardening

Example of hardening an EC2 instance using AWS security groups:

**Insecure Configuration**
```json
{
  "GroupId": "sg-0123456789abcdef0",
  "GroupName": "web-server-sg",
  "IpPermissions": [
    {
      "FromPort": 80,
      "ToPort": 80,
      "IpProtocol": "tcp",
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    }
  ]
}
```

**Hardened Configuration**
```json
{
  "GroupId": "sg-0123456789abcdef0",
  "GroupName": "web-server-sg",
  "IpPermissions": [
    {
      "FromPort": 80,
      "ToPort": 80,
      "IpProtocol": "tcp",
      "IpRanges": [
        {
          "CidrIp": "192.168.1.0/24"
        }
      ]
    }
  ]
}
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **CloudGoat**: Provides scenarios to practice securing AWS environments.

By following these steps and best practices, you can significantly enhance the security of your applications and deployment environments.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/01-Overview of Automated Application Code and Image Scanning Steps/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/01-Overview of Automated Application Code and Image Scanning Steps/02-Practice Questions & Answers|Practice Questions & Answers]]

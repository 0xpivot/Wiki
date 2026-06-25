---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Logging into ECR

Before pushing the image to ECR, you need to authenticate with the ECR registry. AWS provides a command-line utility to handle this authentication.

### Step 1: Authenticate with ECR

Run the following command to authenticate with ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

This command retrieves a password from AWS and uses it to log in to the ECR registry.

### Step 2: Push the Image to ECR

Now that you are authenticated, you can push the image to the ECR repository using the following command:

```bash
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

This command pushes the tagged image to the ECR repository.

### Full Example of HTTP Request and Response

Here is a full example of the HTTP request and response when pushing an image to ECR:

#### HTTP Request

```http
POST /v2/123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp/blobs/uploads/ HTTP/1.1
Host: 123456789012.dkr.ecr.us-east-1.amazonaws.com
Authorization: Bearer <token>
Content-Length: 1024
Content-Type: application/octet-stream
```

#### HTTP Response

```http
HTTP/1.1 202 Accepted
Date: Tue, 01 Jan 2024 12:00:00 GMT
Content-Length: 0
Location: /v2/123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp/blobs/uploads/<upload_id>
```

### Explanation of Headers

- **Authorization**: Contains the bearer token for authentication.
- **Content-Length**: Specifies the length of the content being sent.
- **Content-Type**: Indicates the type of content being sent.

### Common Pitfalls and How to Avoid Them

1. **Incorrect Authentication**: Ensure that you are using the correct AWS account and region for authentication.
2. **Tagging Errors**: Double-check the tagging process to ensure that the image is tagged correctly with the full domain of the ECR repository.
3. **Network Issues**: Ensure that your network allows outbound connections to the ECR endpoint.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Enable logging and monitoring for your ECR repositories to detect any unauthorized access attempts.
- **IAM Policies**: Use IAM policies to restrict access to the ECR repositories to only authorized users.

#### Prevention

- **Secure Access**: Use IAM roles and policies to control access to the ECR repositories.
- **Regular Audits**: Regularly audit the access logs to identify any suspicious activity.

#### Secure Coding Fixes

- **Example Vulnerable Code**:
    ```bash
    aws ecr get-login --region us-east-1 | docker login --password-stdin
    ```
    This command does not specify the username, which can lead to unauthorized access.

- **Example Secure Code**:
    ```bash
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
    ```

### Configuration Hardening

- **IAM Policies**: Apply strict IAM policies to limit access to the ECR repositories.
- **Network ACLs**: Configure Network ACLs to restrict access to the ECR endpoint.

### Real-World Examples

#### Recent Breaches

- **CVE-2021-44228 (Log4Shell)**: This vulnerability affected many Docker images hosted on public registries. Using a private registry helps mitigate such risks.
- **AWS ECR Security Incident (2023)**: An unauthorized user accessed a private ECR repository due to misconfigured IAM policies. This highlights the importance of proper access controls.

### Hands-On Labs

To practice setting up and managing private Docker repositories on AWS ECR, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on container security, including ECR setup.
- **CloudGoat**: Provides hands-on labs for various AWS services, including ECR.

By following these steps and best practices, you can effectively set up and manage private Docker repositories on AWS ECR, ensuring the security and integrity of your containerized applications.

---
<!-- nav -->
[[06-Building and Tagging Docker Images|Building and Tagging Docker Images]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/08-Creating Private Docker Repositories on AWS ECR/00-Overview|Overview]] | [[08-Setting Up AWS ECR|Setting Up AWS ECR]]

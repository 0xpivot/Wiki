---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Default Credentials and Misconfigurations

### Default Credentials

Default credentials are pre-set usernames and passwords that come with software or hardware devices. These credentials are often well-known and documented, making them a prime target for attackers. When an engineer installs a service such as MySQL, PostgreSQL, or any other database management system, they might forget to change the default credentials. This oversight can lead to unauthorized access to the system.

#### Why Default Credentials Are Dangerous

Default credentials pose a significant security risk because they are widely known and easily accessible. Attackers often start their attempts with default credentials, knowing that many systems remain unchanged. This initial foothold can be exploited to gain deeper access to the system.

#### Real-World Example: Equifax Breach

One of the most notable breaches involving default credentials is the Equifax data breach in 2017. Hackers exploited a vulnerability in Apache Struts, but they also used default credentials to access the system. This breach exposed sensitive personal information of approximately 147 million people, including Social Security numbers, birth dates, addresses, and driver’s license numbers.

#### How to Prevent / Defend Against Default Credentials

**Detection:**
- **Automated Scanning Tools:** Use tools like `Nmap`, `Hydra`, or `Medusa` to scan for default credentials.
- **Security Audits:** Regularly audit systems to ensure default credentials have been changed.

**Prevention:**
- **Change Default Credentials:** Always change default credentials immediately after installation.
- **Password Policies:** Implement strong password policies that enforce complexity and regular changes.

**Secure Coding Fix:**

```python
# Vulnerable Code
default_username = "admin"
default_password = "password"

# Secure Code
import os
from getpass import getpass

def set_credentials():
    username = input("Enter new username: ")
    password = getpass("Enter new password: ")
    confirm_password = getpass("Confirm new password: ")

    if password == confirm_password:
        # Store securely (e.g., hashed)
        print(f"Credentials set successfully.")
    else:
        print("Passwords do not match.")

set_credentials()
```

### Security Misconfigurations

Security misconfigurations occur when a system or application is not properly configured to meet security requirements. This can happen due to human error, lack of knowledge, or oversight. One common example is the misconfiguration of Amazon S3 buckets.

#### Amazon S3 Bucket Misconfigurations

Amazon S3 (Simple Storage Service) is a cloud-based storage service provided by AWS. It is commonly used to store files, images, videos, and other media. S3 buckets can be configured to be either public or private. A public S3 bucket allows anyone to access its contents, which can lead to data exposure.

#### Real-World Example: Capital One Data Breach

In 2019, Capital One suffered a massive data breach where a hacker accessed sensitive information of over 100 million customers. The breach occurred due to a misconfigured S3 bucket that was left open to the internet. The hacker exploited this misconfiguration to gain unauthorized access to the data.

#### How to Prevent / Defend Against Security Misconfigurations

**Detection:**
- **AWS Security Hub:** Use AWS Security Hub to monitor and manage security configurations across your AWS environment.
- **Third-party Tools:** Utilize tools like `Bucket Explorer` or `S3 Browser` to check the permissions of S3 buckets.

**Prevention:**
- **Least Privilege Principle:** Ensure that S3 buckets are configured with the least privilege necessary.
- **IAM Policies:** Use AWS Identity and Access Management (IAM) policies to restrict access to S3 buckets.

**Secure Configuration Example:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

### Complex Modern Application Runtimes

Modern applications often run in complex environments involving containers, Kubernetes, and cloud platforms. Each layer introduces additional configuration options, increasing the likelihood of misconfigurations.

#### Containers and Kubernetes

Containers provide a lightweight and portable way to package and run applications. Kubernetes is an orchestration tool that manages containerized applications at scale. Both technologies introduce numerous configuration options that can be misconfigured.

#### Real-World Example: Docker Security Issues

Docker, a popular containerization platform, has faced several security issues due to misconfigurations. In 2018, a misconfigured Docker daemon allowed unauthorized access to the host system, leading to potential data breaches.

#### How to Prevent / Defend Against Misconfigurations in Modern Runtimes

**Detection:**
- **Container Security Tools:** Use tools like `Clair`, `Trivy`, or `Twistlock` to scan for vulnerabilities and misconfigurations in containers.
- **Kubernetes Security Best Practices:** Follow Kubernetes security best practices, such as using Network Policies and Role-Based Access Control (RBAC).

**Prevention:**
- **Configuration Management Tools:** Use tools like `Ansible`, `Terraform`, or `Puppet` to manage and enforce consistent configurations.
- **Regular Audits:** Conduct regular security audits to identify and correct misconfigurations.

**Secure Configuration Example:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    securityContext:
      runAsUser: 1000
      allowPrivilegeEscalation: false
```

### Hands-On Labs

To practice and reinforce the concepts covered in this chapter, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs to learn about web security, including default credentials and misconfigurations.
- **OWASP Juice Shop:** A deliberately insecure web application to practice security testing and exploitation techniques.
- **CloudGoat:** Provides hands-on labs to learn about cloud security, including AWS S3 bucket misconfigurations.
- **Kubernetes Goat:** A deliberately insecure Kubernetes cluster to practice security testing and exploitation techniques.

By thoroughly understanding and implementing the principles discussed in this chapter, you can significantly enhance the security of your applications and systems.

---
<!-- nav -->
[[14-Cryptographic Failures|Cryptographic Failures]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 1/00-Overview|Overview]] | [[16-Detailed Explanation of OWASP Top 10 Categories|Detailed Explanation of OWASP Top 10 Categories]]

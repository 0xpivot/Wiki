---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## What Are CIS Benchmarks?

### Introduction to CIS Benchmarks

The Center for Internet Security (CIS) provides a set of benchmarks designed to help organizations improve their security posture by following best practices. These benchmarks are detailed documents that outline specific configurations and settings for various systems, including operating systems, cloud platforms, and applications. They serve as a guide to ensure that systems are configured securely and are less susceptible to vulnerabilities and attacks.

### Downloading and Referencing CIS Benchmarks

To effectively utilize CIS Benchmarks, you should first obtain the relevant document for your specific environment. This can typically be done by downloading the benchmark from the CIS website or referencing an existing copy provided by your organization. Each benchmark is tailored to a particular system or cloud platform, ensuring that the recommendations are applicable and effective.

For example, if you are working with Amazon Web Services (AWS), you would download the CIS AWS Foundations Benchmark. Similarly, for Microsoft Azure, you would use the CIS Azure Foundations Benchmark. These documents provide a comprehensive list of security controls and configurations that can be implemented to enhance the security of your cloud environment.

### Understanding the Content of CIS Benchmarks

The CIS Benchmarks are structured into several sections, each addressing different aspects of security. Here’s a breakdown of what you might find in a typical CIS Benchmark:

1. **Introduction**: Provides an overview of the benchmark, its purpose, and the scope of the system it covers.
2. **Security Controls**: Detailed descriptions of security controls, categorized into different levels of importance (e.g., Level 1, Level 2).
3. **Implementation Guidance**: Step-by-step instructions on how to implement each control, including specific commands and configurations.
4. **Assessment Procedures**: Methods to verify that the controls have been correctly implemented.
5. **Appendices**: Additional resources, such as references to other standards and compliance frameworks.

### Example: CIS AWS Foundations Benchmark

Let’s take a closer look at the CIS AWS Foundations Benchmark as an example. This benchmark provides a series of security controls that can be applied to AWS environments to reduce the risk of security incidents.

#### Security Control Example: IAM User Permissions

One of the key security controls in the CIS AWS Foundations Benchmark is related to Identity and Access Management (IAM) user permissions. The benchmark recommends that IAM users should have the least privilege necessary to perform their job functions.

**Vulnerable Configuration:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
```

This policy grants full administrative access to all AWS services, which is highly insecure.

**Secure Configuration:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

This policy restricts the user to only the necessary actions (`GetObject` and `PutObject`) on a specific S3 bucket, adhering to the principle of least privilege.

### Implementation Steps

Implementing CIS Benchmarks involves several steps:

1. **Download the Benchmark**: Obtain the relevant CIS Benchmark document for your system or cloud platform.
2. **Review the Controls**: Understand the security controls recommended in the benchmark.
3. **Apply the Controls**: Implement the controls in your environment using the provided guidance.
4. **Verify Implementation**: Use the assessment procedures to ensure that the controls have been correctly implemented.

### Real-World Examples and Breaches

Understanding how CIS Benchmarks can prevent real-world security incidents is crucial. Consider the following examples:

#### Example 1: Equifax Data Breach (CVE-2017-5638)

In 2017, Equifax suffered a massive data breach due to unpatched Apache Struts vulnerabilities. Had Equifax followed the CIS benchmarks for their systems, they could have ensured that their software was up-to-date and patched against known vulnerabilities.

#### Example 2: Capital One Data Breach (CVE-2019-0708)

In 2019, Capital One experienced a data breach due to misconfigured AWS S3 buckets. Following the CIS AWS Foundations Benchmark would have helped Capital One ensure that their S3 buckets were properly secured and not accessible to unauthorized users.

### How to Prevent / Defend

#### Detection

To detect potential security issues, you can use tools like AWS Config, AWS Trusted Advisor, and third-party security scanners. These tools can help you identify misconfigurations and vulnerabilities in your environment.

#### Prevention

1. **Regular Audits**: Conduct regular audits of your environment to ensure compliance with CIS benchmarks.
2. **Automated Compliance Tools**: Utilize automated compliance tools like AWS Config Rules, Terraform modules, and Ansible playbooks to enforce CIS benchmarks.
3. **Training and Awareness**: Ensure that your team is trained on the principles of CIS benchmarks and understands the importance of following them.

#### Secure Coding Fixes

Here’s an example of how to apply secure coding practices based on CIS benchmarks:

**Vulnerable Code:**

```python
import boto3

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response
```

**Secure Code:**

```python
import boto3

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response
```

In the secure code, we ensure that the S3 client uses the `s3v4` signature version, which is more secure than the default version.

### Conclusion

CIS Benchmarks are essential tools for improving the security posture of your systems and cloud environments. By following these benchmarks, you can ensure that your configurations are secure and aligned with industry best practices. Regular audits and the use of automated compliance tools can help you maintain compliance and prevent security incidents.

### Practice Labs

For hands-on practice with CIS Benchmarks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to web application security, which can be extended to understand CIS benchmarks for web applications.
- **CloudGoat**: A cloud security training platform that includes scenarios based on CIS benchmarks for AWS and Azure.
- **flaws.cloud**: Provides a cloud-based environment to practice securing AWS environments according to CIS benchmarks.

By engaging in these labs, you can gain practical experience in implementing and verifying CIS benchmarks in real-world scenarios.

---
<!-- nav -->
[[03-Detailed Explanation of CIS Benchmarks|Detailed Explanation of CIS Benchmarks]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/What are CIS Benchmarks/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/What are CIS Benchmarks/05-Conclusion|Conclusion]]

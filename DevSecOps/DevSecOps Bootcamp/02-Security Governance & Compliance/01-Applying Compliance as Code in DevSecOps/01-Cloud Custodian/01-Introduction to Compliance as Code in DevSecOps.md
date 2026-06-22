---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Introduction to Compliance as Code in DevSecOps

### What is Compliance as Code?

Compliance as Code is a practice that integrates compliance requirements directly into the development process through automated tools and scripts. This approach ensures that compliance policies are enforced consistently across all environments, reducing the risk of non-compliance and the associated penalties. In the context of DevSecOps, compliance as code is crucial because it helps organizations maintain regulatory compliance while accelerating the delivery of secure applications.

### Why is Compliance as Code Important?

Compliance as Code is essential for several reasons:

1. **Consistency**: Manual processes can lead to inconsistencies and human errors. Automation ensures that compliance policies are applied uniformly across all systems.
2. **Speed**: Automated compliance checks can be integrated into the CI/CD pipeline, allowing teams to catch compliance issues early and often.
3. **Cost-Effectiveness**: Automating compliance reduces the need for manual audits and the associated costs.
4. **Scalability**: As organizations grow and expand into new regions, compliance as code helps manage the increasing complexity of regulatory requirements.

### How Does Compliance as Code Work?

Compliance as Code typically involves the following steps:

1. **Define Policies**: Compliance policies are defined using a declarative language such as YAML or JSON.
2. **Automate Enforcement**: These policies are then enforced using automation tools that integrate with the CI/CD pipeline.
3. **Monitor and Audit**: Continuous monitoring and auditing ensure that compliance policies are being followed and that any deviations are detected and addressed promptly.

### Example: Cloud Custodian

Cloud Custodian is one such tool that enables compliance as code. Developed by Capital One, it was initially designed to manage AWS infrastructure but has since expanded to support multi-cloud environments, including AWS, Azure, and Google Cloud Platform.

### Background Theory

#### What is Cloud Custodian?

Cloud Custodian is an open-source tool that provides a framework for managing cloud resources across multiple cloud providers. It allows you to define policies in YAML files and automate enforcement actions based on those policies. This includes security compliance, cost optimization, and operational management.

#### Why Use Cloud Custodian?

Cloud Custodian offers several benefits:

1. **Multi-Cloud Support**: It supports multiple cloud providers, making it ideal for organizations with a hybrid cloud environment.
2. **Active Community**: An active community contributes to regular updates and improvements.
3. **Detailed Documentation**: Comprehensive documentation and examples are available for various cloud environments.

### Installation and Setup

To get started with Cloud Custodian, follow these steps:

1. **Download Cloud Custodian**:
    - Visit the Cloud Custodian website at [CloudCustodian.io](https://cloudcustodian.io/) to access the documentation and installation files.
    - Alternatively, you can clone the repository from GitHub:
      ```bash
      git clone https://github.com/capitalone/cloud-custodian.git
      ```

2. **Install Dependencies**:
    - Ensure Python and pip are installed on your system.
    - Install Cloud Custodian using pip:
      ```bash
      pip install c7n
      ```

3. **Configure Environment**:
    - Set up your cloud provider credentials. For AWS, you can configure them using the `aws configure` command:
      ```bash
      aws configure
      ```
    - For Azure and Google Cloud, configure the respective environment variables.

### Creating Policies

Policies in Cloud Custodian are defined using YAML files. Here’s an example of a policy to ensure that all EC2 instances have a specific tag:

```yaml
policies:
  - name: ensure-tags-on-ec2
    resource: ec2
    filters:
      - "tag:Environment": absent
    actions:
      - type: tag
        key: Environment
        value: Production
```

### Detailed Explanation of the Policy

- **Resource**: Specifies the type of resource to which the policy applies (`ec2` in this case).
- **Filters**: Defines conditions that must be met for the policy to apply. In this example, the filter checks if the `Environment` tag is absent.
- **Actions**: Specifies the actions to be taken if the filter conditions are met. Here, the action is to add a `Environment` tag with the value `Production`.

### Running the Policy

To run the policy, use the following command:

```bash
custodian run -s output --region us-east-1 -c policy.yaml
```

This command runs the policy defined in `policy.yaml`, outputs the results to the `output` directory, and specifies the region as `us-east-1`.

### Monitoring and Auditing

Continuous monitoring and auditing are critical to ensuring compliance. Cloud Custodian provides mechanisms to monitor and audit policy enforcement:

1. **Logging**: Enable logging to track policy execution and any changes made.
2. **Reporting**: Generate reports to review compliance status and identify any deviations.

### Real-World Examples

#### Recent Breaches and CVEs

Recent breaches and vulnerabilities highlight the importance of compliance as code. For example:

- **CVE-2021-21972**: A vulnerability in AWS S3 bucket permissions led to unauthorized data exposure. Using Cloud Custodian, you could define policies to ensure proper S3 bucket permissions.
- **Azure Misconfiguration**: A misconfiguration in Azure VM settings allowed unauthorized access. Cloud Custodian can help enforce proper VM configurations.

### Detailed Example: Enforcing S3 Bucket Permissions

Here’s a detailed example of using Cloud Custodian to enforce S3 bucket permissions:

1. **Policy Definition**:
    ```yaml
    policies:
      - name: s3-bucket-permissions
        resource: s3
        filters:
          - type: bucket-policy
            key: Statement[?Sid == 'PublicAccess']
            value: present
        actions:
          - type: notify
            template: default
            subject: Public Access Detected in S3 Bucket
            priority: 1
    ```

2. **Explanation**:
    - **Resource**: Specifies the type of resource (`s3` in this case).
    - **Filters**: Checks if the S3 bucket policy contains a statement with `Sid` set to `PublicAccess`.
    - **Actions**: Sends a notification if the filter condition is met.

3. **Running the Policy**:
    ```bash
    custodian run -s output --region us-east-1 -c s3-policy.yaml
    ```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Broad Policies**: Avoid creating overly broad policies that may inadvertently affect unintended resources.
2. **Inconsistent Tagging**: Ensure consistent tagging practices to avoid confusion and misapplication of policies.
3. **Manual Overrides**: Be cautious of manual overrides that can bypass automated compliance checks.

#### Best Practices

1. **Regular Audits**: Perform regular audits to ensure compliance policies are being followed.
2. **Documentation**: Maintain comprehensive documentation for all policies and their rationale.
3. **Training**: Train team members on the use and importance of compliance as code.

### How to Prevent / Defend

#### Detection

- **Monitoring Tools**: Use monitoring tools like Cloud Custodian to continuously monitor compliance.
- **Logs and Reports**: Regularly review logs and reports to identify any deviations from compliance policies.

#### Prevention

- **Secure Coding**: Implement secure coding practices to prevent vulnerabilities.
- **Configuration Hardening**: Harden configurations to minimize the risk of misconfigurations.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of a policy:

**Vulnerable Version**:
```yaml
policies:
  - name: insecure-s3-policy
    resource: s3
    filters:
      - type: bucket-policy
        key: Statement[?Sid == 'PublicAccess']
        value: present
    actions:
      - type: notify
        template: default
        subject: Public Access Detected in S3 Bucket
        priority: 1
```

**Secure Version**:
```yaml
policies:
  - name: secure-s3-policy
    resource: s3
    filters:
      - type: bucket-policy
        key: Statement[?Sid == 'PublicAccess']
        value: absent
    actions:
      - type: notify
        template: default
        subject: Public Access Detected in S3 Bucket
        priority: 1
```

### Conclusion

Compliance as Code is a powerful practice that helps organizations maintain regulatory compliance while accelerating the delivery of secure applications. By leveraging tools like Cloud Custodian, you can automate compliance checks, reduce human error, and ensure consistency across all environments.

### Hands-On Labs

For practical experience with Cloud Custodian, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: Provides a vulnerable web application for learning security concepts.
- **DVWA (Damn Vulnerable Web Application)**: Another excellent resource for web application security training.
- **WebGoat**: A deliberately insecure Java application for learning about web application security.

These labs provide a comprehensive learning experience and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/01-Cloud Custodian/00-Overview|Overview]] | [[02-Applying Compliance as Code in DevSecOps Cloud Custodian|Applying Compliance as Code in DevSecOps Cloud Custodian]]

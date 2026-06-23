---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Applying Compliance as Code in DevSecOps: Cloud Custodian

### Introduction to Compliance as Code

Compliance as Code is a practice within DevSecOps that involves automating compliance checks and enforcement through code. This approach ensures that compliance requirements are integrated into the development lifecycle, making it easier to maintain regulatory adherence and reduce the risk of non-compliance. One of the tools used for this purpose is **Cloud Custodian**, which is an open-source framework designed to manage and enforce policies across cloud resources.

### What is Cloud Custodian?

**Cloud Custodian** is a powerful tool that allows you to define, monitor, and enforce policies across your cloud infrastructure. It supports multiple cloud providers, including AWS, Azure, and GCP. The primary goal of Cloud Custodian is to help organizations maintain compliance and security by automating the enforcement of policies.

#### Why Use Cloud Custodian?

- **Automation**: Automates the process of checking and enforcing policies, reducing manual effort.
- **Consistency**: Ensures that policies are applied consistently across all cloud resources.
- **Flexibility**: Supports a wide range of policies, from basic compliance checks to complex operational scripts.
- **Integration**: Integrates seamlessly with CI/CD pipelines, allowing compliance checks to be part of the deployment process.

### Example Policies in Cloud Custodian

Let's explore some of the existing policies that can be implemented using Cloud Custodian:

#### Detecting Logging In from an Invalid IP Address

One of the critical security measures is to ensure that access to your cloud resources is restricted to authorized IP addresses. Cloud Custodian can help you detect and respond to unauthorized access attempts.

```yaml
policies:
  - name: restrict-access-to-valid-ip-addresses
    resource: aws.iam.user
    filters:
      - type: ip-address
        value: ["192.168.1.1", "10.0.0.1"]
        op: not-in
    actions:
      - type: notify
        template: |
          Unauthorized access attempt detected from IP address {{ ip_address }}.
```

In this policy, we define a filter to check if the IP address from which a user is attempting to log in is not in the list of valid IP addresses. If the condition is met, a notification is sent.

#### Stopping Unapproved EC2 AMI Instances

Another important policy is to ensure that only approved AMIs are used to launch EC2 instances. This helps in maintaining consistency and security across your environment.

```yaml
policies:
  - name: stop-unapproved-ec2-amis
    resource: aws.ec2.instance
    filters:
      - type: image
        key: Name
        value: "approved-ami-name"
        op: ne
    actions:
      - type: stop
```

This policy checks if the AMI used to launch an EC2 instance is not the approved one. If the condition is met, the instance is stopped.

#### Shutting Down AWS Environments During Off Hours

To save costs, you might want to automatically shut down AWS environments during off hours. Cloud Custodian can help you automate this process.

```yaml
policies:
  - name: shutdown-environment-during-off-hours
    resource: aws.ec2.instance
    filters:
      - type: schedule
        expr: "@weekly @daily 00:00-08:00"
    actions:
      - type: stop
```

This policy uses a schedule filter to check if the current time falls within the specified off-hour period. If the condition is met, the EC2 instances are stopped.

### How to Implement Cloud Custodian Policies

Implementing Cloud Custodian policies involves several steps:

1. **Define Policies**: Write policies in YAML format.
2. **Deploy Policies**: Integrate policies into your CI/CD pipeline or run them manually.
3. **Monitor and Audit**: Regularly monitor and audit the enforcement of policies.

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of maintaining compliance and security in cloud environments. For example, the **Capital One breach** in 2019 exposed sensitive data due to misconfigured cloud resources. Using Cloud Custodian, such misconfigurations could have been detected and prevented.

### Common Pitfalls and Best Practices

#### Common Pitfalls

- **Overly Broad Policies**: Ensure that policies are specific enough to avoid false positives.
- **Manual Enforcement**: Avoid relying solely on manual enforcement; automate as much as possible.
- **Ignoring Operational Scripts**: Don’t overlook the importance of operational scripts in maintaining compliance.

#### Best Practices

- **Regular Audits**: Perform regular audits to ensure compliance.
- **Continuous Monitoring**: Continuously monitor cloud resources for compliance violations.
- **Automate Enforcement**: Automate the enforcement of policies to reduce human error.

### How to Prevent / Defend

#### Detection

Use Cloud Custodian to regularly scan your cloud resources for compliance violations. For example, to detect unauthorized access attempts:

```yaml
policies:
  - name: detect-unauthorized-access
    resource: aws.iam.user
    filters:
      - type: ip-address
        value: ["192.168.1.1", "10.0.0.1"]
        op: not-in
    actions:
      - type: notify
        template: |
          Unauthorized access attempt detected from IP address {{ ip_address }}.
```

#### Prevention

Ensure that only approved AMIs are used to launch EC2 instances:

```yaml
policies:
  - name: prevent-unapproved-ec2-amis
    resource: aws.ec2.instance
    filters:
      - type: image
        key: Name
        value: "approved-ami-name"
        op: ne
    actions:
      - type: stop
```

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a policy:

**Vulnerable Version:**

```yaml
policies:
  - name: allow-all-ip-access
    resource: aws.iam.user
    filters:
      - type: ip-address
        value: "*"
        op: in
    actions:
      - type: notify
        template: |
          Access attempt detected from IP address {{ ip_address }}.
```

**Secure Version:**

```yaml
policies:
  - name: restrict-access-to-valid-ip-addresses
    resource: aws.iam.user
    filters:
      - type: ip-address
        value: ["192.168.1.1", "10.0.0.1"]
        op: not-in
    actions:
      - type: notify
        template: |
          Unauthorized access attempt detected from IP address {{ ip_address }}.
```

### Hands-On Labs

To gain practical experience with Cloud Custodian, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning web security.
- **WebGoat**: An interactive training application for learning about web application security.

These labs provide a controlled environment to practice implementing and enforcing compliance policies using Cloud Custodian.

### Conclusion

Applying Compliance as Code in DevSecOps using Cloud Custodian is a powerful way to ensure that your cloud infrastructure remains compliant and secure. By automating the enforcement of policies, you can reduce the risk of non-compliance and maintain a consistent security posture. Regular audits and continuous monitoring are essential to ensure that your policies are effective and up-to-date.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/01-Cloud Custodian/01-Introduction to Compliance as Code in DevSecOps|Introduction to Compliance as Code in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/01-Cloud Custodian/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/01-Cloud Custodian/03-Practice Questions & Answers|Practice Questions & Answers]]

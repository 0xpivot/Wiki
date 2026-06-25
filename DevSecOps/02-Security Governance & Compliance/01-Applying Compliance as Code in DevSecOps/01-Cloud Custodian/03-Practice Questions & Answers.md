---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is Cloud Custodian and who developed it?**

Cloud Custodian is a tool designed to enforce governance and compliance across cloud environments. It was initially developed by Capital One to manage their AWS infrastructure and was later open-sourced in 2016. The tool supports multiple cloud providers, including AWS, Azure, and Google Cloud Platform.

**Q2. How does Cloud Custodian help with cost management?**

Cloud Custodian helps with cost management by allowing users to define policies that automate actions like shutting down resources during off-hours or terminating unused resources. This can significantly reduce unnecessary spending. For instance, you could configure a policy to automatically shut down AWS environments during non-working hours using YAML files, which are easy to write and maintain.

**Q3. Explain how Cloud Custodian can be used to detect and prevent unauthorized access.**

Cloud Custodian can be configured to monitor and enforce security policies, such as detecting logins from invalid IP addresses. By setting up a policy that identifies logins from unauthorized IPs, Cloud Custodian can alert administrators or automatically block these connections. This helps in maintaining strict access controls and preventing unauthorized access to cloud resources.

**Q4. How do you install and configure Cloud Custodian?**

To install Cloud Custodian, you can visit the official website at CloudCustodian.io. Here, you can find installation files and documentation. Once installed, you can start configuring policies using YAML files. These files define the conditions under which certain actions should be taken. For example:

```yaml
policies:
  - name: stop-unapproved-ec2-instances
    resource: ec2
    filters:
      - tag:Owner
        value: approved-owner
        op: ne
    actions:
      - stop
```

This policy stops EC2 instances that are not tagged with an approved owner.

**Q5. What are some recent real-world examples where tools like Cloud Custodian could have helped prevent breaches?**

Tools like Cloud Custodian could have helped prevent breaches such as the Capital One data breach (CVE-2019-11601). In this case, misconfigured cloud resources allowed unauthorized access to sensitive customer data. If Cloud Custodian had been in place, policies could have been set up to ensure proper configuration and monitoring of cloud resources, potentially preventing such a breach. 

Another example is the AWS S3 bucket exposure incidents, where sensitive data was left publicly accessible due to misconfigurations. Cloud Custodian could have enforced policies to ensure that S3 buckets were properly secured and monitored for public access.

**Q6. How does Cloud Custodian support multi-cloud environments?**

Cloud Custodian supports multi-cloud environments by providing a unified framework to manage policies across different cloud providers. This means you can write policies in YAML that apply to resources in AWS, Azure, and Google Cloud Platform. This flexibility allows organizations to enforce consistent governance and compliance standards regardless of the cloud environment they are using.

---
<!-- nav -->
[[02-Applying Compliance as Code in DevSecOps Cloud Custodian|Applying Compliance as Code in DevSecOps Cloud Custodian]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/01-Cloud Custodian/00-Overview|Overview]]

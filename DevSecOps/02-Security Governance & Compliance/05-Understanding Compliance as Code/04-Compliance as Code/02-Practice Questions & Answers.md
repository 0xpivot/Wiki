---
course: DevSecOps
topic: Understanding Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "infrastructure as code" (IAC) and how it relates to compliance as code.**

Infrastructure as Code (IAC) refers to the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. Essentially, it treats the infrastructure like software, enabling teams to use version control, testing, and automation to manage their environments. 

Compliance as Code extends this concept to ensure that the infrastructure meets specific regulatory and security standards. It involves writing code that tests the compliance of the environment against predefined specifications. This ensures that the infrastructure not only functions correctly but also adheres to necessary regulations and best practices.

**Q2. How does compliance as code help in ensuring that an organization’s infrastructure remains compliant over time?**

Compliance as Code helps in maintaining compliance over time by automating the process of checking against compliance standards. By embedding compliance checks into the infrastructure code, organizations can continuously validate that their systems meet the required standards. This is particularly useful in dynamic environments where changes are frequent. 

For example, if a new regulation requires certain network configurations, compliance as code can automatically verify these configurations whenever changes are made. This reduces the risk of non-compliance due to manual errors or oversight.

**Q3. Provide an example of how compliance as code could be implemented in a cloud environment.**

In a cloud environment, compliance as code can be implemented using tools like Terraform, Ansible, or AWS CloudFormation. For instance, suppose an organization needs to ensure that all EC2 instances in AWS comply with PCI-DSS standards. The following steps outline how this could be achieved:

1. Define the compliance rules in code using a tool like AWS Config or Ansible playbooks.
2. Use these rules to create automated compliance checks that run periodically.
3. Integrate these checks into the CI/CD pipeline to ensure that any new infrastructure deployed meets the compliance criteria.

Here is a simplified example using AWS Config:

```yaml
# Example of a compliance rule in AWS Config
resource:
  type: AWS::EC2::Instance
properties:
  SecurityGroupIds:
    - sg-12345678
  ImageId: ami-12345678
```

This rule ensures that all EC2 instances are launched with a specific security group and AMI, which are part of the compliance requirements.

**Q4. Discuss recent real-world examples where compliance as code could have prevented a breach or violation.**

One notable example is the Capital One data breach in 2019, where a misconfigured web application firewall allowed unauthorized access to customer data. Compliance as code could have helped prevent this breach by enforcing strict configuration rules and continuously monitoring for deviations from these rules.

By implementing compliance as code, the organization could have set up automated checks to ensure that the WAF was properly configured according to the company’s security policies. These checks could have detected the misconfiguration early and alerted the security team to take corrective action.

Another example is the GDPR violations faced by companies like British Airways and Marriott International. Compliance as code could have helped these organizations maintain continuous compliance with GDPR requirements by automating regular audits and ensuring that personal data handling practices met the required standards.

**Q5. How can compliance as code be integrated into a DevSecOps workflow?**

Integrating compliance as code into a DevSecOps workflow involves several key steps:

1. **Define Compliance Rules**: Create clear, machine-readable compliance rules that reflect the organization’s security and regulatory requirements.
2. **Automate Compliance Checks**: Use tools like Ansible, Terraform, or custom scripts to automate the enforcement and verification of these rules.
3. **Continuous Integration and Deployment (CI/CD)**: Incorporate compliance checks into the CI/CD pipeline to ensure that any new infrastructure changes are validated against compliance rules before deployment.
4. **Monitoring and Auditing**: Implement continuous monitoring to detect any deviations from compliance standards in real-time. Use logging and auditing tools to track compliance status and generate reports.

By integrating compliance as code into the DevSecOps workflow, organizations can ensure that compliance is not just a one-time check but an ongoing, automated process that supports secure and efficient operations.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/05-Understanding Compliance as Code/04-Compliance as Code/01-Understanding Compliance as Code|Understanding Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/05-Understanding Compliance as Code/04-Compliance as Code/00-Overview|Overview]]

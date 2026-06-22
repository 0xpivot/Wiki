---
course: DevSecOps
topic: Understanding Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of mapping compliance controls to code.**

To map compliance controls to code, you first need to understand the compliance requirements or specifications. This involves identifying the specific controls from compliance frameworks such as ISO 27001 or PCI DSS. Once identified, these controls are translated into code that can perform checks within your environment. These checks ensure that your systems meet the compliance criteria. The process is similar to implementing any other business requirement in code, where you start with a clear specification and then write code to enforce those rules.

**Q2. How do compliance frameworks like ISO 27001 and PCI DSS differ in their approach to compliance controls?**

ISO 27001 is a broad framework that outlines 114 different types of security controls, which include both technical and non-technical measures. Not all of these controls can be directly implemented in code; some may require manual processes or documentation. On the other hand, PCI DSS is more prescriptive and focuses heavily on technical controls that can be easily translated into code. For instance, PCI DSS requires specific configurations for firewalls and encryption, which can be directly enforced using code-based compliance checks.

**Q3. How can compliance checks be integrated into the development workflow using Infrastructure as Code (IaC)?**

Compliance checks can be integrated into the development workflow by leveraging Infrastructure as Code (IaC). IaC tools like Terraform, Ansible, or CloudFormation allow you to define your infrastructure configuration in code. By embedding compliance checks within these definitions, you can ensure that your infrastructure meets specific compliance requirements before deployment. For example, you could use a tool like Checkov to scan Terraform templates for compliance violations against frameworks like CIS Benchmarks or HIPAA. This ensures that your infrastructure is compliant from the outset and continues to remain so throughout its lifecycle.

**Q4. Provide an example of how compliance controls can be implemented in code using a recent real-world example.**

Consider the recent case of a company that was found to be non-compliant with GDPR due to inadequate data protection measures. To prevent such issues, compliance controls can be implemented in code. For example, you can use a tool like Open Policy Agent (OPA) to enforce data access policies. OPA allows you to define policies in Rego, a declarative policy language, and integrate these policies into your application stack. A simple example might look like this:

```rego
package data_access

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.user.role == "employee"
    input.resource.type == "personal_data"
}
```

This policy ensures that only users with the role "admin" or "employee" can access personal data, aligning with GDPR's data protection principles.

**Q5. Why is it important to run compliance checks through a console window or command line interface?**

Running compliance checks through a console window or command line interface (CLI) is crucial because it allows for automation and integration into continuous integration/continuous delivery (CI/CD) pipelines. By running these checks via CLI, you can easily script them to run automatically during the build or deployment process. This ensures that compliance is checked at every stage of the software development lifecycle, reducing the risk of non-compliance. Additionally, CLI tools provide a consistent and repeatable way to execute compliance checks across different environments, making it easier to maintain compliance across multiple systems and applications.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/05-Understanding Compliance as Code/05-Mapping Controls to Code/01-Understanding Compliance as Code|Understanding Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/05-Understanding Compliance as Code/05-Mapping Controls to Code/00-Overview|Overview]]

---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Mapping Security Controls from Specification to Code

### What is Compliance as Code?

Compliance as Code is a practice that involves translating compliance requirements into code. This approach ensures that security and compliance policies are enforced consistently across the organization.

### Why is Compliance as Code Important?

Compliance as Code is important because it helps organizations meet regulatory requirements and maintain security standards. By translating compliance requirements into code, teams can automate the enforcement of these policies and reduce the risk of non-compliance.

### How Does Compliance as Code Work?

Compliance as Code involves the following steps:

1. **Define Policies**: Define compliance policies in a machine-readable format.
2. **Enforce Policies**: Enforce these policies using automation tools.
3. **Monitor Compliance**: Continuously monitor compliance status and generate reports.

### Real-World Example: GDPR Compliance

The General Data Protection Regulation (GDPR) requires organizations to implement robust data protection measures. Compliance as Code can help organizations enforce GDPR requirements by automating data protection policies and monitoring compliance status.

### Tools for Compliance as Code

Some popular tools for Compliance as Code include:

- **Azure Policy**
- **AWS Config**
- **Cloud Custodian**
- **Terraform Sentinel**

### Example Configuration: Azure Policy

```json
{
  "if": {
    "allOf": [
      {
        "field": "type",
        "equals": "Microsoft.Compute/virtualMachines"
      },
      {
        "field": "Microsoft.Compute/virtualMachines/extensions/type",
        "notEquals": "CustomScriptExtension"
      }
    ]
  },
  "then": {
    "effect": "deny"
  }
}
```

### Example Configuration: AWS Config

```json
{
  "ConfigRuleName": "ec2-security-group-ingress",
  "Description": "Checks that EC2 instances have security group ingress rules.",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EC2::Instance"]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EC2_SECURITY_GROUP_INGRESS"
  }
}
```

### Example Configuration: Cloud Custodian

```yaml
policies:
  - name: ec2-security-group-ingress
    resource: aws.ec2
    filters:
      - type: ingress
        value: 22
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/05-How to Prevent  Defend|How to Prevent  Defend]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/07-Practice Labs|Practice Labs]]

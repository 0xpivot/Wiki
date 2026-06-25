---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Using Compliance Code Examples from AWS

### AWS Config

AWS Config is a service that enables organizations to assess, audit, and record changes to AWS resources. AWS Config rules define the conditions and actions that should be taken when a rule is evaluated.

### Example Configuration: AWS Config Rule

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

### Cloud Custodian

Cloud Custodian is an open-source tool that enables organizations to manage and govern cloud resources. Cloud Custodian policies define the conditions and actions that should be taken when a policy is evaluated.

### Example Configuration: Cloud Custodian Policy

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
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/09-Testing Phase|Testing Phase]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/11-Using Compliance Code Examples from Microsoft Azure|Using Compliance Code Examples from Microsoft Azure]]

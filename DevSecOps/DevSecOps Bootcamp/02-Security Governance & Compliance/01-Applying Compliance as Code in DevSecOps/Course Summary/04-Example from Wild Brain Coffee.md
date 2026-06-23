---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Example from Wild Brain Coffee

Wild Brain Coffee is a fictional company that uses various tools to enable good security governance and compliance. Let's look at how they use AWS Config and Cloud Custodian to achieve this.

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

### Example Configuration: Cloud Custodian Policy

```yaml
policies:
  - name: ec2-security-group-ingress
    resource: aws.ec2
    filters:
      - type: ingress
        value: 22
```

### Request and Response

#### Full HTTP Request

```http
POST /aws-config-rule HTTP/1.1
Host: api.example.com
Content-Type: application/json

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

#### Full HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "AWS Config rule created successfully."
}
```

### Expected Result

The AWS Config rule is created successfully, and the system starts enforcing the specified compliance requirements.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/03-Code Building and Testing Stage|Code Building and Testing Stage]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/05-How to Prevent  Defend|How to Prevent  Defend]]

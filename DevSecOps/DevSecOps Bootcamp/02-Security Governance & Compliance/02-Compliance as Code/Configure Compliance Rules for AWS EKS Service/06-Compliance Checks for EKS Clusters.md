---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Compliance Checks for EKS Clusters

After enabling logging, the next step is to perform compliance checks on the EKS clusters. This involves defining and enforcing compliance rules using AWS Config and other services.

### Defining Compliance Rules

AWS Config allows you to define compliance rules that check for specific configurations in your EKS clusters. These rules can be used to ensure that clusters are configured according to organizational policies and regulatory requirements.

#### Example Compliance Rules

1. **Cluster Encryption**: Ensure that all EKS clusters are encrypted.
2. **Node Security Groups**: Ensure that worker nodes are configured with appropriate security groups.
3. **IAM Roles**: Ensure that IAM roles are correctly configured for EKS clusters.

### Enforcing Compliance Rules

Once compliance rules are defined, they need to be enforced to ensure that clusters remain compliant. This can be done using AWS Config and other services.

#### Step-by-Step Guide

1. **Define Compliance Rules**:
    - Navigate to the AWS Config console.
    - Define rules to check for specific configurations.

2. **Force Re-Evaluation**:
    - Force a re-evaluation of the compliance rules to ensure that clusters are compliant.

3. **Take Action**:
    - If any clusters are found to be non-compliant, take corrective actions to bring them into compliance.

### Example Code for Defining Compliance Rules

```json
{
  "ConfigRuleName": "eks-cluster-encryption",
  "Description": "Checks if EKS clusters are encrypted.",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EKS::Cluster"]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EKS_CLUSTER_ENCRYPTION_ENABLED"
  }
}
```

### Example Code for Forcing Re-Evaluation

```bash
aws configservice start-config-rules-evaluation --config-rule-names eks-cluster-encryption
```

### Monitoring Compliance

Continuous monitoring is essential to ensure that clusters remain compliant over time. This can be done using AWS Config and other services.

#### Monitoring with AWS Config

AWS Config can be used to continuously monitor the compliance status of EKS clusters. Here’s how to set up continuous monitoring:

1. **Create a Configuration Recorder**:
    - Navigate to the AWS Config console.
    - Create a new configuration recorder to record the state of your resources.

2. **Create a Delivery Channel**:
    - Set up a delivery channel to send the recorded data to an Amazon S3 bucket.

3. **Define Compliance Rules**:
    - Define rules to check if clusters are compliant.

### Example AWS Config Rule for Continuous Monitoring

```json
{
  "ConfigRuleName": "eks-cluster-compliance",
  "Description": "Checks if EKS clusters are compliant.",
  1. **Scope**: {
    "ComplianceResourceTypes": ["AWS::EKS::Cluster"]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EKS_CLUSTER_COMPLIANCE_CHECK"
  }
}
```

### Monitoring with CloudWatch Events

CloudWatch Events can be used to trigger actions based on compliance events. This can be used to automatically notify stakeholders when a cluster becomes non-compliant.

#### Setting Up CloudWatch Events

1. **Create a Rule**:
    - Navigate to the CloudWatch console.
    - Create a new rule to trigger actions based on compliance events.

2. **Define Actions**:
    - Define actions to be taken when a compliance event occurs.

### Example CloudWatch Event Rule

```json
{
  "rule_name": "eks-compliance-event",
  "event_pattern": {
    "source": ["aws.config"],
    "detail-type": ["Config Rules Compliance Change"],
    "detail": {
      "config-rule-name": ["eks-cluster-compliance"],
      "compliance-type": ["NON_COMPLIANT"]
    }
  },
  "targets": [
    {
      "arn": "arn:aws:sns:us-west-2:123456789012:eks-compliance-topic",
      "id": "target1"
    }
  ]
}
```

### Pitfalls and Common Mistakes

1. **Inconsistent Compliance Rules**: Ensure that compliance rules are consistently applied across all clusters.
2. **Insufficient Monitoring**: Regularly monitor the compliance status of clusters to ensure that they remain compliant.
3. **Incorrect Rule Definitions**: Ensure that compliance rules are correctly defined to accurately reflect the desired compliance status.

### How to Prevent / Defend

1. **Regular Audits**: Conduct regular audits to ensure that clusters are compliant.
2. **Automated Monitoring**: Use AWS Config and CloudWatch Events to automatically monitor the compliance status of clusters.
3. **Remediation Actions**: Implement automated remediation actions to correct any issues detected during monitoring.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of proper compliance checks. For example, the Capital One breach in 2019 demonstrated the critical role of compliance checks in detecting and responding to security incidents.

### Conclusion

By implementing Compliance as Code for EKS clusters, organizations can ensure that their clusters adhere to compliance rules and are properly monitored. This approach reduces the risk of non-compliance and enhances overall security.

---
<!-- nav -->
[[05-Introduction to Compliance as Code|Introduction to Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[07-Compliance as Code for AWS EKS Service|Compliance as Code for AWS EKS Service]]

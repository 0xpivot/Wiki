---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why it is important to ensure that EKS clusters are running a supported version of Kubernetes.**

Using a supported version of Kubernetes ensures that the cluster benefits from the latest security patches and bug fixes. Outdated versions can expose the cluster to known vulnerabilities, which could be exploited by attackers. For instance, CVE-2021-25742, a critical vulnerability in Kubernetes, affected versions prior to 1.21. Ensuring that EKS clusters run supported versions helps mitigate such risks and keeps the cluster secure.

**Q2. How would you configure an AWS Config rule to ensure that EKS clusters are running a supported version of Kubernetes?**

To configure an AWS Config rule to ensure that EKS clusters are running a supported version of Kubernetes, follow these steps:

1. Navigate to the AWS Config console.
2. Click on "Rules" and then "Create Rule."
3. Choose the "EKS Cluster Supported Version" managed rule.
4. In the configuration section, specify the oldest version of Kubernetes that you want to allow. For example, if you want to ensure that all clusters use Kubernetes version 1.27 or newer, set the oldest allowed version to 1.27.
5. Name and describe the rule appropriately.
6. Ensure that the rule is applied to EKS clusters.
7. Click "Next," review the settings, and then "Save."

Here’s an example configuration snippet:

```yaml
{
  "configRuleName": "eks-cluster-supported-version",
  "description": "Ensure EKS clusters are running a supported version of Kubernetes.",
  "scope": {
    "complianceResourceTypes": ["AWS::EKS::Cluster"]
  },
  "source": {
    "owner": "AWS",
    "sourceIdentifier": "EKS_CLUSTER_SUPPORTED_VERSION"
  },
  "inputParameters": {
    "minVersion": "1.27"
  }
}
```

**Q3. Why is it important to enable logging for EKS clusters, and how can you configure an AWS Config rule to ensure logging is enabled?**

Enabling logging for EKS clusters is crucial for monitoring and auditing purposes. It allows you to track and analyze events within the cluster, which is essential for detecting and responding to security incidents. Additionally, logging provides valuable data for troubleshooting and compliance reporting.

To configure an AWS Config rule to ensure logging is enabled for EKS clusters:

1. Navigate to the AWS Config console.
2. Click on "Rules" and then "Create Rule."
3. Choose the "EKS Cluster Logging Enabled" managed rule.
4. Set the evaluation frequency (e.g., daily).
5. Name and describe the rule appropriately.
6. Ensure that the rule is applied to EKS clusters.
7. Click "Next," review the settings, and then "Save."

Here’s an example configuration snippet:

```yaml
{
  "configRuleName": "eks-cluster-logging-enabled",
  "description": "Ensure logging is enabled for all EKS clusters.",
  "scope": {
    "complianceResourceTypes": ["AWS::EKS::Cluster"]
  },
  "source": {
    "owner": "AWS",
    "sourceIdentifier": "EKS_CLUSTER_LOGGING_ENABLED"
  },
  "inputParameters": {
    "evaluationFrequency": "DAILY"
  }
}
```

**Q4. How would you handle non-compliant resources identified by AWS Config rules for EKS clusters?**

Handling non-compliant resources identified by AWS Config rules involves several steps:

1. **Notification**: Set up notifications (e.g., via SNS) to alert the appropriate team members when a resource becomes non-compliant.
2. **Remediation**: Implement automatic remediation actions using AWS Systems Manager Automation or AWS Lambda functions to automatically fix common issues.
3. **Manual Intervention**: For complex issues, manually intervene by reaching out to the responsible engineering teams and requesting them to fix the non-compliant resources.
4. **Review and Update**: Regularly review the compliance status and update the rules as needed to adapt to new security requirements and best practices.

For example, you can use AWS Systems Manager Automation to automatically upgrade Kubernetes versions or enable logging:

```yaml
{
  "name": "eks-upgrade-action",
  "description": "Automatically upgrade EKS clusters to a supported version.",
  "documentType": "Automation",
  "parameters": {
    "ClusterName": {
      "type": "String",
      "description": "Name of the EKS cluster to upgrade."
    },
    "TargetVersion": {
      "type": "String",
      "description": "Target Kubernetes version."
    }
  },
  "assumeRole": "arn:aws:iam::123456789012:role/AutoUpgradeRole"
}
```

**Q5. Explain how AWS Config rules can help maintain compliance for EKS clusters in a multi-team environment.**

In a multi-team environment, AWS Config rules can help maintain compliance for EKS clusters by providing centralized visibility and enforcement of security policies. Here’s how:

1. **Centralized Monitoring**: AWS Config rules provide a single dashboard to monitor the compliance status of all EKS clusters across different teams.
2. **Automated Checks**: Automated compliance checks ensure that security policies are consistently enforced without manual intervention.
3. **Notifications and Alerts**: Teams can be notified when their resources become non-compliant, prompting timely action.
4. **Policy Enforcement**: By defining and enforcing compliance rules, organizations can ensure that all EKS clusters adhere to the required security standards, regardless of who created or manages them.

For example, if a team creates an EKS cluster with an unsupported Kubernetes version, the AWS Config rule will identify it as non-compliant, triggering alerts and remediation actions. This ensures that all clusters meet the organization’s security requirements, even in a distributed development environment.

---
<!-- nav -->
[[11-Remediation Actions for Non-Compliant Resources|Remediation Actions for Non-Compliant Resources]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]]

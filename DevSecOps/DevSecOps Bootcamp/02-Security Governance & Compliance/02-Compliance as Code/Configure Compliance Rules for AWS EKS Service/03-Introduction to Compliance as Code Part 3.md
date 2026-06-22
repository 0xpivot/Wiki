---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is an approach to automating compliance requirements using code. This method ensures that infrastructure and applications adhere to specific regulatory and organizational policies. In the context of AWS Elastic Kubernetes Service (EKS), compliance as code can be implemented using AWS Config, a service that continuously audits, assesses, and evaluates the configurations of AWS resources.

### Why Compliance as Code?

Compliance as Code is essential for several reasons:

1. **Automation**: Automates the enforcement of compliance rules, reducing human error and ensuring consistency.
2. **Scalability**: Easily scales across multiple environments and resources.
3. **Visibility**: Provides real-time visibility into compliance status.
4. **Auditability**: Simplifies the audit process by maintaining a record of compliance checks and results.

### How Compliance as Code Works

AWS Config allows you to define and enforce compliance rules for your AWS resources. These rules can be custom or managed by AWS. Managed rules are pre-built and cover common compliance scenarios, such as ensuring that logging is enabled for all control plane components in an EKS cluster.

### Example Scenario: Enforcing Logging in EKS Clusters

Let's consider a scenario where an organization wants to ensure that logging is enabled for all control plane components in their EKS clusters. This is crucial for monitoring and auditing purposes.

### Step-by-Step Guide to Enforcing Logging in EKS Clusters

#### Step 1: Define the Compliance Rule

To enforce logging in EKS clusters, we need to create a compliance rule using AWS Config. AWS provides a managed rule specifically for this purpose: `EKS_CLUSTER_LOGGING_ENABLED`.

##### What is `EKS_CLUSTER_LOGGING_ENABLED`?

The `EKS_CLUSTER_LOGGING_ENABLED` rule checks whether logging is enabled for all control plane components in an EKS cluster. The control plane components include:

- `api`
- `audit`
- `authenticator`
- `controllerManager`
- `scheduler`

If logging is not enabled for any of these components, the rule will mark the cluster as non-compliant.

##### How to Create the Rule

1. **Navigate to AWS Config**:
   - Go to the AWS Management Console.
   - Navigate to the AWS Config service.

2. **Create a New Rule**:
   - Click on "Rules" in the left-hand menu.
   - Click on "Create rule".

3. **Select the Managed Rule**:
   - Search for `EKS_CLUSTER_LOGGING_ENABLED`.
   - Select the rule and click "Next".

4. **Configure the Rule**:
   - Set the evaluation frequency (e.g., once a day).
   - Click "Next" and then "Save".

```mermaid
sequenceDiagram
    participant User
    participant AWSConfig
    User->>AWSConfig: Create EKS_CLUSTER_LOGGING_ENABLED rule
    AWSConfig-->>User: Rule created and configured
```

#### Step 2: Evaluate the Rule

Once the rule is created, AWS Config will evaluate the compliance status of all EKS clusters in the account.

##### Evaluation Frequency

The evaluation frequency determines how often AWS Config checks the compliance status. A typical setting is once a day. This ensures that any changes to the logging configuration are detected promptly.

```mermaid
stateDiagram-v2
    [*] --> Checking
    Checking --> NonCompliant
    Checking --> Compliant
    NonCompliant --> Checking
    Compliant --> Checking
```

#### Step 3: Review Compliance Status

After the rule is evaluated, you can review the compliance status of your EKS clusters.

##### Viewing Compliance Status

1. **Navigate to AWS Config**:
   - Go to the AWS Config dashboard.
   - Click on "Compliance" in the left-hand menu.

2. **Review Compliance Results**:
   - You will see a list of resources and their compliance status.
   - Identify any non-compliant clusters and take corrective action.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of compliance as code. For instance, the Capital One breach in 2019 exposed sensitive customer data due to misconfigured AWS S3 buckets. Ensuring proper logging and monitoring could have helped detect and mitigate such issues earlier.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Inconsistent Configuration**: Ensure that logging is consistently enabled across all clusters.
2. **Manual Overrides**: Avoid manual overrides that can bypass compliance rules.
3. **False Positives**: Monitor for false positives and adjust the rule as needed.

#### Best Practices

1. **Automate Logging**: Use automation tools to ensure logging is enabled.
2. **Regular Audits**: Perform regular audits to verify compliance.
3. **Alerting**: Set up alerts for non-compliant resources.

### How to Prevent / Defend

#### Detection

1. **Use AWS Config**: Continuously monitor compliance status using AWS Config.
2. **Set Up Alerts**: Configure alerts for non-compliant resources.

#### Prevention

1. **Secure Configuration**: Ensure that logging is enabled for all control plane components.
2. **Automate Compliance**: Use automation tools to enforce compliance rules.

#### Secure Coding Fixes

Here’s an example of how to enable logging for all control plane components in an EKS cluster using the AWS CLI:

```bash
# Enable logging for all control plane components
aws eks update-cluster-config --name <cluster-name> --region <region> --logging '{"enable": true, "types": ["api", "audit", "authenticator", "controllerManager", "scheduler"]}'
```

#### Vulnerable vs. Secure Code

**Vulnerable Code**:
```bash
# Logging is not enabled for all control plane components
aws eks update-cluster-config --name <cluster-name> --region <region> --logging '{"enable": true, "types": ["api", "audit"]}'
```

**Secure Code**:
```bash
# Logging is enabled for all control plane components
aws eks update-cluster-config --name <cluster-name> --region <region> --logging '{"enable": true, "types": ["api", "audit", "authenticator", "controllerManager", "scheduler"]}'
```

### Complete Example: Full HTTP Request and Response

Here’s a complete example of enabling logging for an EKS cluster using the AWS API:

#### HTTP Request

```http
POST / HTTP/1.1
Host: eks.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonEKS.UpdateClusterConfig
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/eks/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=fe5f356c79821d4b1b1e84a2a40e16b97a9eb73fd27e1e6b70bf8dc4c00e0c2a
X-Amz-Date: 20150101T000000Z

{
    "name": "my-cluster",
    "logging": {
        "enable": true,
        "types": [
            "api",
            "audit",
            "authenticator",
            "controllerManager",
            "scheduler"
        ]
    }
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890ab
Date: Thu, 01 Jan 2015 00:00:00 GMT

{
    "cluster": {
        "name": "my-cluster",
        "logging": {
            "enable": true,
            "types": [
                "api",
                "audit",
                "authenticator",
                "controllerManager",
                "scheduler"
            ]
        }
    }
}
```

### Hands-On Labs

For practical experience with compliance as code in AWS EKS, consider the following labs:

- **CloudGoat**: A hands-on lab for practicing cloud security and compliance.
- **Pacu**: A framework for testing AWS security configurations.

These labs provide real-world scenarios and challenges to help you master compliance as code in AWS EKS.

### Conclusion

Implementing compliance as code in AWS EKS is crucial for maintaining a secure and compliant environment. By leveraging AWS Config and managed rules, you can automate the enforcement of compliance requirements, ensuring that your EKS clusters are properly configured and monitored. Regular audits and alerts can help detect and mitigate any compliance issues promptly.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/02-Introduction to Compliance as Code Part 2|Introduction to Compliance as Code Part 2]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/04-Introduction to Compliance as Code Part 4|Introduction to Compliance as Code Part 4]]

---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is an approach to ensuring that your infrastructure and applications adhere to regulatory requirements and internal policies through automated checks and configurations. This method leverages code to define compliance rules and continuously enforce them across your environment. In the context of AWS Elastic Kubernetes Service (EKS), compliance as code ensures that your Kubernetes clusters are running supported versions, thereby reducing the risk of security vulnerabilities.

### Importance of Using Supported Versions

Using outdated versions of technologies exposes you to unnecessary risks because no technology or version is perfect. Each version may contain security vulnerabilities that are fixed in subsequent releases. By keeping your software up to date, you benefit from both new features and critical security patches. Outdated versions can be exploited by attackers, leading to data breaches and other security incidents.

For instance, consider the case of the Log4j vulnerability (CVE-2021-44228), which affected many systems running outdated versions of the Log4j library. This vulnerability allowed remote code execution, leading to widespread exploitation and significant security concerns. Ensuring that your software is up to date helps mitigate such risks.

### Configuring Compliance Rules for AWS EKS

In AWS EKS, one of the key compliance rules is ensuring that your EKS clusters are running supported versions of Kubernetes. This rule, known as the "EKS cluster supported version," checks whether your EKS cluster is running a supported Kubernetes version. While it does not necessarily require the latest version, it ensures that the version is one of the supported ones, typically the latest three versions of the technology.

### Setting Up the Rule

To set up the EKS cluster supported version rule, follow these steps:

1. **Navigate to AWS Config**: Access the AWS Management Console and navigate to the AWS Config service.
2. **Create a New Rule**: Click on "Rules" and then "Create rule."
3. **Select Managed Rule**: Choose the "Managed rule" option and search for "EKS cluster supported version."
4. **Configure the Rule**: In the configuration section, you can specify the oldest version that you want to allow your Kubernetes cluster to have. This is done by setting the `MinimumSupportedVersion` parameter.

Here is an example of how to configure this rule using the AWS CLI:

```bash
aws configservice put-configuration-recorder \
    --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/aws-config-role \
    --recording-group allSupported=true,includeGlobalResourceTypes=true

aws configservice put-evaluation-results \
    --evaluation-results '[{"ComplianceResourceType":"AWS::EKS::Cluster","ComplianceResourceId":"cluster-id","OrderingTimestamp":"2023-10-01T12:00:00Z","ComplianceType":"NON_COMPLIANT","Annotation":"Kubernetes version is not supported"}]'
```

### Monitoring EKS Cluster Changes

The rule applies specifically to EKS clusters, so you should configure it to monitor only EKS cluster changes. This ensures that you are not monitoring all changes for all resources, which would be inefficient and unnecessary.

Here is an example of how to configure the rule using the AWS Management Console:

1. **Name and Description**: Provide a name and description for the rule.
2. **Resource Type**: Specify the resource type as `AWS::EKS::Cluster`.
3. **Configuration Settings**: Set the `MinimumSupportedVersion` parameter to the desired value.

### Example Configuration

Here is a complete example of configuring the EKS cluster supported version rule using the AWS Management Console:

```json
{
  "RuleId": "eks-cluster-supported-version",
  "Description": "Ensures that the EKS cluster is running a supported version of Kubernetes.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EKS::Cluster"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EKS_CLUSTER_SUPPORTED_VERSION"
  },
  "InputParameters": {
    "MinimumSupportedVersion": "1.21"
  }
}
```

### Detection and Prevention

#### Detection

To detect non-compliant EKS clusters, you can use AWS Config to generate compliance reports. These reports will highlight any clusters that are running unsupported versions of Kubernetes.

Here is an example of how to retrieve compliance details using the AWS CLI:

```bash
aws configservice get-compliance-details-by-config-rule \
    --config-rule-name eks-cluster-supported-version
```

#### Prevention

To prevent non-compliant EKS clusters, you can automate the process of updating Kubernetes versions using AWS Lambda functions or AWS Step Functions. Additionally, you can use AWS CloudFormation to manage your EKS clusters and ensure that they are always running supported versions.

Here is an example of how to update the Kubernetes version using AWS CloudFormation:

```yaml
Resources:
  EKSCluster:
    Type: 'AWS::EKS::Cluster'
    Properties:
      Name: my-cluster
      Version: 1.21
      RoleArn: arn:aws:iam::123456789012:role/EKSAdminRole
```

### Secure Coding Practices

To ensure that your EKS clusters are always running supported versions, follow these secure coding practices:

1. **Automate Updates**: Use automation tools like AWS Lambda and AWS Step Functions to automatically update Kubernetes versions.
2. **Use CloudFormation**: Manage your EKS clusters using AWS CloudFormation templates to ensure consistent and compliant configurations.
3. **Regular Audits**: Conduct regular audits of your EKS clusters to ensure they are running supported versions.

### Real-World Examples

Consider the following real-world example of a breach due to an outdated Kubernetes version:

**Example: CVE-2020-8558**

CVE-2020-8558 is a vulnerability in Kubernetes that allows an attacker to escalate privileges and gain unauthorized access to the cluster. This vulnerability was fixed in Kubernetes version 1.18.10, 1.19.4, and 1.20.2. Clusters running older versions were at risk of being exploited.

By ensuring that your EKS clusters are running supported versions, you can mitigate such risks and protect your infrastructure from similar vulnerabilities.

### Conclusion

Configuring compliance rules for AWS EKS is crucial for maintaining the security and integrity of your Kubernetes clusters. By ensuring that your clusters are running supported versions of Kubernetes, you can reduce the risk of security vulnerabilities and ensure compliance with regulatory requirements. Use automation tools and secure coding practices to maintain a compliant and secure environment.

### Practice Labs

For hands-on practice with compliance as code for AWS EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable application that can be deployed on EKS for testing and learning.
- **CloudGoat**: A series of labs designed to teach cloud security concepts, including compliance as code for AWS services.

These labs provide practical experience in configuring and enforcing compliance rules for EKS clusters, helping you to master the skills needed to maintain a secure and compliant environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/02-Introduction to Compliance as Code Part 2|Introduction to Compliance as Code Part 2]]

---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is a modern approach to ensuring that infrastructure and applications adhere to regulatory requirements and internal policies. This method leverages automation tools and scripts to continuously monitor and enforce compliance standards, reducing the risk of non-compliance and improving overall security posture. In this chapter, we will delve deep into the concepts, tools, and techniques used in Compliance as Code, focusing on AWS and Kubernetes environments.

### What is Compliance as Code?

Compliance as Code refers to the practice of using code to define and enforce compliance policies within an organization. Instead of relying on manual processes, Compliance as Code uses automated tools to ensure that systems and applications meet specific regulatory and organizational requirements. This approach is particularly useful in cloud environments like AWS and Kubernetes, where the scale and dynamic nature of resources can make manual compliance management challenging.

#### Why is Compliance as Code Important?

1. **Efficiency**: Automating compliance checks reduces the time and effort required to manually verify compliance.
2. **Consistency**: Automated processes ensure that compliance checks are performed consistently across all resources.
3. **Scalability**: Automation scales easily to handle large numbers of resources, making it ideal for cloud environments.
4. **Immediate Feedback**: Automated compliance checks provide immediate feedback, allowing issues to be addressed promptly.
5. **Reduced Risk**: By enforcing compliance policies automatically, organizations can reduce the risk of non-compliance and associated penalties.

### Key Concepts and Tools

To effectively implement Compliance as Code, several key concepts and tools are essential:

1. **CIS Benchmarks**: The Center for Internet Security (CIS) provides detailed security benchmarks for various technologies, including AWS and Kubernetes. These benchmarks serve as a foundation for defining compliance policies.
2. **Infrastructure as Code (IaC)**: Using tools like Terraform, Ansible, or CloudFormation to define infrastructure configurations in code.
3. **Configuration Management**: Tools like Ansible, Puppet, or Chef to manage and enforce system configurations.
4. **Policy Enforcement Tools**: Tools like AWS Config, AWS Trusted Advisor, and Kubernetes Policy Controller to enforce compliance policies.
5. **Automated Remediation**: Tools and scripts to automatically correct non-compliant resources.

### CIS Benchmarks

The Center for Internet Security (CIS) provides comprehensive security benchmarks for various technologies, including AWS and Kubernetes. These benchmarks outline best practices for securing systems and are widely recognized as a standard for compliance.

#### AWS CIS Benchmarks

The AWS CIS Benchmarks cover a wide range of security controls, including:

- Identity and Access Management (IAM)
- Network Security
- Encryption
- Logging and Monitoring
- Configuration Management

These benchmarks are crucial for ensuring that AWS resources are configured securely and comply with regulatory requirements.

#### Kubernetes CIS Benchmarks

The Kubernetes CIS Benchmarks focus on securing Kubernetes clusters and include controls for:

- Node Security
- Pod Security
- Network Policies
- RBAC (Role-Based Access Control)

These benchmarks help ensure that Kubernetes clusters are configured securely and meet compliance standards.

### Mapping CIS Benchmarks to Your Environment

To implement Compliance as Code, you need to map the CIS benchmarks to your environment. This involves translating the security controls defined in the benchmarks into actionable policies that can be enforced using automation tools.

#### Example: Mapping AWS CIS Benchmarks

Let's consider an example of mapping the AWS CIS Benchmarks to an AWS environment. Suppose we want to ensure that all EC2 instances are configured with a specific set of security groups and IAM roles.

```yaml
# Example CloudFormation template to enforce AWS CIS Benchmarks
Resources:
  EC2Instance:
    Type: 'AWS::EC2::Instance'
    Properties:
      ImageId: 'ami-0c55b159cbfafe1f0'
      InstanceType: 't2.micro'
      SecurityGroupIds:
        - !Ref SecurityGroup
      IamInstanceProfile: 'my-iam-profile'

  SecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupName: 'my-security-group'
      VpcId: 'vpc-12345678'
      SecurityGroupIngress:
        - IpProtocol: 'tcp'
          FromPort: '22'
          ToPort: '22'
          CidrIp: '0.0.0.0/0'
```

This CloudFormation template enforces specific security groups and IAM roles for EC2 instances, aligning with the AWS CIS Benchmarks.

### Automating Compliance Checks

Automating compliance checks is a critical component of Compliance as Code. This involves setting up automated tools to continuously monitor and evaluate resources against compliance policies.

#### AWS Config

AWS Config is a service that enables you to assess, audit, and record changes to your AWS resources. You can use AWS Config to create rules that enforce compliance policies.

```json
{
  "ConfigRuleName": "ec2-security-groups",
  "Description": "Ensure EC2 instances are associated with specific security groups.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "SECURITY_GROUP_ASSOCIATION"
  }
}
```

This AWS Config rule ensures that EC2 instances are associated with specific security groups.

#### Kubernetes Policy Controller

Kubernetes Policy Controller is a tool that allows you to define and enforce policies for Kubernetes resources. You can use it to ensure that pods are configured according to the Kubernetes CIS Benchmarks.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: pod-security-policy
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: restrict-root
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Pod should not run as root."
      deny:
        conditions:
        - key: spec.securityContext.runAsUser
          operator: NotEquals
          value: 0
```

This Kubernetes Policy Controller rule ensures that pods are not run as root.

### Automated Remediation

Automated remediation involves automatically correcting non-compliant resources. This can significantly reduce the time and effort required to address compliance issues.

#### Example: Automated Remediation in AWS

Suppose we have a rule that ensures all EC2 instances are associated with specific security groups. If an instance is found to be non-compliant, we can use an AWS Lambda function to automatically associate the correct security group.

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = event['detail']['instance-id']
    security_group_id = 'sg-12345678'

    response = ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=[security_group_id]
    )
    return response
```

This Lambda function automatically associates the correct security group with non-compliant EC2 instances.

### Real-World Examples

Real-world examples can help illustrate the importance and practical application of Compliance as Code.

#### Example: Recent Breach Due to Non-Compliance

Consider a recent breach where an organization failed to properly configure their AWS resources, leading to unauthorized access. By implementing Compliance as Code, the organization could have automatically enforced security policies, preventing the breach.

#### Example: Regulatory Requirement Compliance

Many organizations are subject to regulatory requirements such as HIPAA, GDPR, or PCI-DSS. Compliance as Code can help ensure that these regulations are met by continuously monitoring and enforcing compliance policies.

### How to Prevent / Defend

Implementing Compliance as Code requires a robust strategy for detection, prevention, and remediation. Here are some key steps:

1. **Detection**: Use tools like AWS Config and Kubernetes Policy Controller to continuously monitor resources for compliance.
2. **Prevention**: Define and enforce compliance policies using Infrastructure as Code (IaC) tools and configuration management tools.
3. **Remediation**: Implement automated remediation scripts to correct non-compliant resources.

#### Example: Secure Coding Practices

Secure coding practices are essential for preventing compliance issues. Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**
```python
import boto3

def get_instance_details(instance_id):
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    return instance.id, instance.state['Name']
```

**Secure Code:**
```python
import boto3

def get_instance_details(instance_id):
    ec2 = boto3.resource('ec2', config=boto3.session.Config(region_name='us-west-2'))
    instance = ec2.Instance(instance_id)
    return instance.id, instance.state['Name']
```

In the secure code, we explicitly specify the region to avoid potential misconfigurations.

### Conclusion

Compliance as Code is a powerful approach to ensuring that infrastructure and applications meet regulatory and organizational requirements. By leveraging automation tools and scripts, organizations can efficiently and effectively enforce compliance policies, reducing the risk of non-compliance and improving overall security posture.

### Practice Labs

For hands-on experience with Compliance as Code, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on compliance and automation.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security, including compliance.
- **CloudGoat**: A series of labs designed to teach cloud security concepts, including Compliance as Code.
- **Pacu**: A framework for AWS security testing that includes modules for compliance and automation.

By completing these labs, you can gain practical experience in implementing Compliance as Code in real-world scenarios.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/09-Wrap Up/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/09-Wrap Up/02-Practice Questions & Answers|Practice Questions & Answers]]

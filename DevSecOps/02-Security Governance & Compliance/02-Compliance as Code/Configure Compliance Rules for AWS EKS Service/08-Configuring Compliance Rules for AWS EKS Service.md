---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Configuring Compliance Rules for AWS EKS Service

In this section, we will configure two compliance rules specific to EKS:

1. Ensure that the EKS cluster is using a recent version of Kubernetes.
2. Restrict SSH access to the EKS nodes.

### Rule 1: Ensure Recent Kubernetes Version

#### Background Theory

Kubernetes versions are periodically updated to include new features, performance improvements, and security patches. Running an outdated version of Kubernetes can expose your cluster to known vulnerabilities. Therefore, it is crucial to ensure that your EKS cluster is always running a recent version.

#### Config Rule Setup

To set up a config rule to check the Kubernetes version, you can use AWS Config Managed Rules or create a custom rule using AWS Lambda.

#### Using AWS Config Managed Rules

AWS Config provides several managed rules out-of-the-box. However, for checking the Kubernetes version, you might need to create a custom rule.

#### Creating a Custom Rule with AWS Lambda

1. **Create an AWS Lambda Function**:
   - Write a Lambda function in Python that checks the Kubernetes version of the EKS cluster.
   - The function should compare the current version with a predefined list of acceptable versions.

```python
import boto3

def lambda_handler(event, context):
    eks_client = boto3.client('eks')
    config_client = boto3.client('config')

    # Get the list of EKS clusters
    clusters = eks_client.list_clusters()['clusters']

    for cluster_name in clusters:
        # Describe the cluster to get the Kubernetes version
        response = eks_client.describe_cluster(name=cluster_name)
        k8s_version = response['cluster']['version']

        # Define the acceptable versions
        acceptable_versions = ['1.21', '1.22', '1.23']

        # Check if the version is acceptable
        if k8s_version not in acceptable_versions:
            # Report non-compliance
            config_client.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType': 'AWS::EKS::Cluster',
                        'ComplianceResourceId': cluster_name,
                        'ComplianceType': 'NON_COMPLIANT',
                        'Annotation': f'Kubernetes version {k8s_version} is not in the acceptable range.'
                    }
                ],
                ResultToken=event['resultToken']
            )
```

2. **Create an AWS Config Rule**:
   - Use the AWS Management Console or AWS CLI to create a new Config rule that invokes the Lambda function.

```bash
aws configservice put-config-rule --config-rule file://config_rule.json
```

Where `config_rule.json` contains:

```json
{
  "ConfigRuleName": "eks-kubernetes-version",
  "Description": "Ensures that the EKS cluster is using a recent version of Kubernetes.",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EKS::Cluster"]
  },
  "Source": {
    "Owner": "CUSTOM_LAMBDA",
    "SourceIdentifier": "<lambda_function_arn>"
  }
}
```

3. **Test the Config Rule**:
   - Trigger a test evaluation to ensure the rule works as expected.

```bash
aws configservice start-config-rules-evaluation --config-rule-names eks-kubernetes-version
```

### Rule 2: Restrict SSH Access to EKS Nodes

#### Background Theory

SSH access to EKS nodes can pose a significant security risk if not properly controlled. Unauthorized access to the nodes can lead to data breaches and malicious activities. Therefore, it is important to restrict SSH access to only authorized IP addresses.

#### Config Rule Setup

To set up a config rule to check SSH access restrictions, you can use AWS Config Managed Rules or create a custom rule using AWS Lambda.

#### Using AWS Config Managed Rules

AWS Config provides several managed rules out-of-the-box. One such rule is `EC2_SSH_Inbound_Rule`, which checks if SSH access is restricted to specific IP addresses.

#### Creating a Custom Rule with AWS Lambda

1. **Create an AWS Lambda Function**:
   - Write a Lambda function in Python that checks the security group rules associated with the EKS nodes.
   - The function should ensure that the security group allows SSH access only from specific IP addresses.

```python
import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    config_client = boto3.client('config')

    # Get the list of security groups associated with EKS nodes
    security_groups = ec2_client.describe_security_groups(Filters=[{'Name': 'tag:aws:eks:cluster-name', 'Values': ['<your-cluster-name>']}])['SecurityGroups']

    for sg in security_groups:
        sg_id = sg['GroupId']
        ip_permissions = sg['IpPermissions']

        for permission in ip_permissions:
            if permission['IpProtocol'] == 'tcp' and permission['FromPort'] == 22 and permission['ToPort'] == 22:
                # Check if the rule allows SSH access from specific IP addresses
                if len(permission['IpRanges']) > 0:
                    allowed_ips = [ip_range['CidrIp'] for ip_range in permission['IpRanges']]
                    if len(allowed_ips) > 1 or allowed_ips[0] != '<authorized-ip-address>':
                        # Report non-compliance
                        config_client.put_evaluations(
                            Evaluations=[
                                {
                                    'ComplianceResourceType': 'AWS::EC2::SecurityGroup',
                                    'ComplianceResourceId': sg_id,
                                    'ComplianceType': 'NON_COMPLIANT',
                                    'Annotation': f'SSH access is not restricted to the authorized IP address.'
                                }
                            ],
                            ResultToken=event['resultToken']
                        )

```

2. **Create an AWS Config Rule**:
   - Use the AWS Management Console or AWS CLI to create a new Config rule that invokes the Lambda function.

```bash
aws configservice put-config-rule --config-rule file://config_rule_ssh.json
```

Where `config_rule_ssh.json` contains:

```json
{
  "ConfigRuleName": "eks-restrict-ssh-access",
  "Description": "Ensures that SSH access to EKS nodes is restricted to specific IP addresses.",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EC2::SecurityGroup"]
  },
  "Source": {
    "Owner": "CUSTOM_LAMBDA",
    "SourceIdentifier": "<lambda_function_arn>"
  }
}
```

3. **Test the Config Rule**:
   - Trigger a test evaluation to ensure the rule works as expected.

```bash
aws configservice start-config-rules-evaluation --config-rule-names eks-restrict-ssh-access
```

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Use AWS Config to regularly audit your EKS clusters and associated resources.
- **Automated Alerts**: Set up automated alerts in AWS Config to notify you of any non-compliant resources.

#### Prevention

- **IAM Policies**: Use IAM policies to restrict access to sensitive resources.
- **Security Groups**: Configure security groups to restrict inbound traffic to specific ports and IP addresses.
- **Network ACLs**: Use Network ACLs to further restrict traffic at the subnet level.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    ports:
    - containerPort: 22
```

##### Fixed Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    ports:
    - containerPort: 22
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
```

#### Configuration Hardening

##### Vulnerable Configuration

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

##### Fixed Configuration

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:Describe*",
        "iam:GetRole",
        "iam:ListRoles"
      ],
      "Resource": "*"
    }
  ]
}
```

### Real-World Examples

#### Recent CVEs/Breaches

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed attackers to bypass authentication and gain unauthorized access to the cluster. Ensuring that your EKS cluster is running a recent version of Kubernetes helps mitigate such risks.
- **Breaches due to misconfigured security groups**: Several breaches have occurred due to misconfigured security groups that allowed unrestricted SSH access. Properly configuring security groups to restrict SSH access to specific IP addresses can prevent such breaches.

### Practice Labs

For hands-on practice with configuring compliance rules for AWS EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and ethical hacking.
- **CloudGoat**: A set of labs designed to help you learn about securing AWS environments, including EKS clusters.

By following these steps and practices, you can ensure that your EKS clusters remain compliant with regulatory requirements and internal policies, thereby enhancing the overall security posture of your organization.

---
<!-- nav -->
[[07-Compliance as Code for AWS EKS Service|Compliance as Code for AWS EKS Service]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[09-Configuring Logging for EKS Components|Configuring Logging for EKS Components]]

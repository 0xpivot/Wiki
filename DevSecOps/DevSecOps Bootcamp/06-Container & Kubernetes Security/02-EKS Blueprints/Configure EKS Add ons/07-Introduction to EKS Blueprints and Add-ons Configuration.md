---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Introduction to EKS Blueprints and Add-ons Configuration

In the context of DevSecOps, managing and securing Kubernetes clusters is critical. Amazon Elastic Kubernetes Service (EKS) provides a managed service for deploying and managing Kubernetes clusters in the AWS cloud. One of the key aspects of securing an EKS cluster is configuring the appropriate permissions and roles for different users and services. This chapter will delve into the process of configuring EKS add-ons, focusing on the necessary steps to ensure proper access control and security.

### Background Theory

Before diving into the practical steps, it's essential to understand the underlying concepts:

#### Kubernetes Users and Roles

Kubernetes uses a Role-Based Access Control (RBAC) system to manage permissions within the cluster. Users and roles are defined to grant specific permissions to perform actions such as creating, deleting, or modifying resources.

- **Users**: Individual identities that can interact with the Kubernetes API.
- **Roles**: Define a set of permissions that can be granted to users or groups.
- **RoleBindings**: Bind roles to users or groups, granting them the specified permissions.

#### AWS IAM Integration

AWS integrates with Kubernetes through Identity and Access Management (IAM). IAM users and roles can be mapped to Kubernetes users and roles, allowing you to leverage AWS's robust IAM capabilities for Kubernetes access control.

### Configuring EKS Add-ons

The process of configuring EKS add-ons involves several steps, including setting up the necessary AWS credentials, assuming the correct IAM role, and retrieving the Kubernetes configuration file (`kubeconfig`).

#### Step 1: Setting Up AWS Credentials

To interact with an EKS cluster, you need to authenticate using AWS credentials. This involves setting the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

#### Step 2: Switching to the Kubernetes Admin User

Once the credentials are set, you need to switch to the Kubernetes admin user. This user typically has limited permissions and must assume an IAM role to gain access to the cluster.

```bash
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/KubernetesAdminRole --role-session-name KubernetesAdminSession
```

This command returns temporary credentials that you can use to authenticate as the Kubernetes admin user.

#### Step 3: Retrieving the `kubeconfig` File

With the correct IAM role assumed, you can retrieve the `kubeconfig` file, which contains the necessary information to connect to the EKS cluster.

```bash
aws eks update-kubeconfig --region us-west-2 --name my-cluster
```

This command updates the `~/.kube/config` file with the details of the EKS cluster.

### Detailed Steps and Code Examples

Let's break down each step with detailed explanations and code examples.

#### Setting AWS Credentials

First, you need to set the AWS credentials. These credentials are used to authenticate with AWS services, including EKS.

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

These environment variables store the access key ID and secret access key, respectively. Ensure these values are kept confidential and are not hardcoded in scripts or shared publicly.

#### Assuming the IAM Role

Next, you need to assume the IAM role that has the necessary permissions to access the EKS cluster. This is done using the `sts assume-role` command.

```bash
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/KubernetesAdminRole \
    --role-session-name KubernetesAdminSession
```

This command returns a JSON object containing temporary credentials. You need to extract these credentials and set them as environment variables.

```json
{
    "Credentials": {
        "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY",
        "SessionToken": "AQoDYXdzEJr...EXAMPLETOKEN"
    }
}
```

Set these credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID=ASIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY
export AWS_SESSION_TOKEN=AQoDYXdzEJr...EXAMPLETOKEN
```

#### Retrieving the `kubeconfig` File

Finally, you can retrieve the `kubeconfig` file using the `eks update-kubeconfig` command.

```bash
aws eks update-kubeconfig --region us-west-2 --name my-cluster
```

This command updates the `~/.kube/config` file with the necessary information to connect to the EKS cluster.

### Mermaid Diagrams

Let's visualize the process using a mermaid diagram.

```mermaid
sequenceDiagram
    participant User
    participant AWS
    participant EKS
    User->>AWS: Set AWS credentials
    User->>AWS: Assume IAM role
    AWS-->>User: Return temporary credentials
    User->>AWS: Retrieve kubeconfig
    AWS-->>User: Update kubeconfig
    User->>EKS: Connect to EKS cluster
```

### Common Pitfalls and How to Prevent Them

#### Incorrect IAM Role Assumption

One common pitfall is assuming the wrong IAM role. This can happen if the role ARN is incorrect or if the role does not have the necessary permissions.

**How to Prevent:**

- Double-check the role ARN.
- Ensure the role has the necessary permissions to access the EKS cluster.
- Use the `describe-role` command to verify the role's permissions.

```bash
aws iam describe-role --role-name KubernetesAdminRole
```

#### Exposing AWS Credentials

Another common issue is exposing AWS credentials. This can happen if the credentials are hardcoded in scripts or shared publicly.

**How to Prevent:**

- Use environment variables to store credentials.
- Use AWS Secrets Manager to securely store and manage credentials.
- Limit the scope of IAM roles to the minimum necessary permissions.

### Real-World Examples

#### Recent Breaches and CVEs

Recent breaches involving misconfigured IAM roles and exposed AWS credentials include:

- **CVE-2021-20225**: A misconfigured IAM role allowed unauthorized access to sensitive data.
- **CVE-2021-20226**: Exposed AWS credentials led to unauthorized access to AWS resources.

These breaches highlight the importance of properly configuring IAM roles and securely managing AWS credentials.

### Secure Coding Practices

#### Vulnerable Code Example

Here's an example of insecure code that exposes AWS credentials:

```python
import boto3

access_key = 'AKIAIOSFODNN7EXAMPLE'
secret_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

client = session.client('eks')
response = client.update_kubeconfig(region_name='us-west-2', name='my-cluster')
```

#### Secure Code Example

Here's the secure version of the code:

```python
import os
import boto3

session = boto3.Session()

client = session.client('eks')
response = client.update_kubeconfig(region_name='us-west-2', name='my-cluster')
```

In the secure version, the AWS credentials are automatically picked up from the environment variables.

### Detection and Prevention

#### Detection

To detect misconfigured IAM roles and exposed AWS credentials, you can use AWS CloudTrail and AWS Config.

- **CloudTrail**: Logs API calls made to AWS services, including EKS.
- **Config**: Tracks resource configurations and changes.

#### Prevention

To prevent unauthorized access, follow these best practices:

- **Limit IAM Role Permissions**: Grant the minimum necessary permissions to IAM roles.
- **Use AWS Secrets Manager**: Store and manage AWS credentials securely.
- **Enable Multi-Factor Authentication (MFA)**: Require MFA for accessing AWS resources.

### Conclusion

Configuring EKS add-ons involves setting up AWS credentials, assuming the correct IAM role, and retrieving the `kubeconfig` file. By following the steps outlined in this chapter and adhering to secure coding practices, you can ensure proper access control and security for your EKS cluster.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes EKS scenarios.
- **flaws.cloud**: A cloud security training platform that includes EKS scenarios.
- **AWS Official Workshops**: Provides guided labs for EKS setup and management.

By completing these labs, you can gain practical experience in configuring EKS add-ons and securing your Kubernetes clusters.

---
<!-- nav -->
[[06-Introduction to EKS Blueprints and Add-ons Configuration Part 1|Introduction to EKS Blueprints and Add-ons Configuration Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Configure EKS Add ons/00-Overview|Overview]] | [[08-Introduction to EKS Blueprints and Helm Charts|Introduction to EKS Blueprints and Helm Charts]]

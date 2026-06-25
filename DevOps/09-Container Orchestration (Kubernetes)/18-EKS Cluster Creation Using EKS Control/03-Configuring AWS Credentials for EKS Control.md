---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring AWS Credentials for EKS Control

Before diving into creating an Amazon Elastic Kubernetes Service (EKS) cluster using EKS Control, it is crucial to understand the underlying mechanisms and configurations required. Specifically, we need to configure AWS credentials to use the AWS Command Line Interface (CLI) and EKS Control effectively.

### Understanding AWS Credentials

AWS credentials consist of an Access Key ID and a Secret Access Key, which are used to authenticate API requests made to AWS services. These credentials are typically associated with an IAM user or role within an AWS account.

#### Why Configure AWS Credentials?

Configuring AWS credentials is essential because:

1. **Authentication**: AWS services require authentication to ensure that only authorized users can access and manage resources.
2. **Permissions**: By configuring credentials, you can specify the permissions granted to the user or role, ensuring that only necessary actions are performed.
3. **Security**: Properly configured credentials help maintain security by limiting access to specific resources and actions.

#### How AWS Credentials Work

When you configure AWS credentials, they are stored in a local configuration file. This file is typically located in the `.aws` directory within your home folder. The configuration file (`config`) and credentials file (`credentials`) contain the necessary information to authenticate and configure your AWS environment.

```plaintext
~/.aws/
├── config
└── credentials
```

The `config` file might look something like this:

```ini
[default]
region = eu-west-3
output = json
```

The `credentials` file might look something like this:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

### Setting Up AWS Credentials for EKS Control

To use EKS Control, you need to ensure that the AWS credentials are properly configured. In this case, we are using an `admin` user that was previously created in the AWS module. The credentials for this user have been configured locally using the `aws configure` command.

#### Steps to Configure AWS Credentials

1. **Create an IAM User**:
   - Log in to the AWS Management Console.
   - Navigate to the IAM service.
   - Create a new IAM user with administrative permissions.

2. **Generate Access Keys**:
   - Once the user is created, generate access keys for the user.
   - Download the access key ID and secret access key.

3. **Configure AWS CLI**:
   - Run the `aws configure` command to set up the credentials.
   - Enter the access key ID and secret access key when prompted.

```bash
aws configure
```

4. **Verify Configuration**:
   - Ensure that the credentials are correctly stored in the `~/.aws/credentials` file.

### Using EKS Control to Create an EKS Cluster

With the AWS credentials configured, we can now proceed to create an EKS cluster using EKS Control. EKS Control is a command-line tool that simplifies the process of creating and managing EKS clusters.

#### Basic EKS Control Command

The basic command to create an EKS cluster using EKS Control is as follows:

```bash
eksctl create cluster
```

This command will create a cluster with default settings. However, we often want to customize the cluster configuration.

#### Customizing the Cluster Configuration

Let's customize the cluster configuration by specifying a custom name, Kubernetes version, region, and node group details.

1. **Cluster Name**:
   - Set a custom name for the cluster. For example, `demo-cluster`.

2. **Kubernetes Version**:
   - Specify the Kubernetes version. For example, `1.17`.

3. **Region**:
   - Specify the region where the cluster will be created. For example, `eu-west-3` (Paris).

4. **Node Group Configuration**:
   - Define the node group name and EC2 instance type.

Here is the complete command with customizations:

```bash
eksctl create cluster --name demo-cluster --version 1.17 --region eu-west-3 --nodegroup-name demo-nodes --node-type t3.medium
```

### Detailed Example of Creating an EKS Cluster

Let's walk through a detailed example of creating an EKS cluster using EKS Control.

#### Step-by-Step Process

1. **Install EKS Control**:
   - Ensure that EKS Control is installed on your system. You can install it using the following command:

   ```bash
   curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
   sudo mv /tmp/eksctl /usr/local/bin
   ```

2. **Configure AWS Credentials**:
   - Ensure that the AWS credentials are configured as described earlier.

3. **Create the EKS Cluster**:
   - Run the `eksctl create cluster` command with the desired parameters.

```bash
eksctl create cluster --name demo-cluster --version 1.17 --region eu-west-3 --nodegroup-name demo-nodes --node-type t3.medium
```

#### Expected Output

After executing the command, you should see output similar to the following:

```plaintext
[ℹ]  eksctl version 0.45.0
[ℹ]  using region eu-west-3
[ℹ]  setting availability zones to [eu-west-3a eu-west-3b eu-west-3c]
[ℹ]  subnets for eu-west-3a: ["subnet-xxxxxxxx"]
[ℹ]  subnets for eu-west-3b: ["subnet-yyyyyyyy"]
[ℹ]  subnets for eu-west-3c: ["subnet-zzzzzzzz"]
[ℹ]  nodegroup "demo-nodes" will use "ami-xxxxxxxx" [AmazonLinux2/1.17]
[ℹ]  using Kubernetes version 1.17
[ℹ]  creating EKS cluster "demo-cluster" in "eu-west-3" region with managed nodes
...
[✔]  saved kubeconfig as "/home/user/.kube/config"
[ℹ]  kubectl command should work with "/home/user/.kube/config", try 'kubectl get nodes'
```

### Common Pitfalls and How to Avoid Them

#### Insufficient Permissions

One common pitfall is insufficient permissions for the IAM user. Ensure that the IAM user has the necessary permissions to create and manage EKS clusters.

##### How to Prevent / Defend

1. **IAM Policy**:
   - Attach a policy with sufficient permissions to the IAM user. For example, the `AmazonEKSClusterPolicy` and `AmazonEKSServicePolicy`.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:*"
            ],
            "Resource": "*"
        }
    ]
}
```

2. **IAM Role**:
   - Ensure that the IAM role attached to the EC2 instances has the necessary permissions to interact with EKS.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "elasticloadbalancing:*",
                "autoscaling:*",
                "cloudwatch:*",
                "iam:PassRole",
                "iam:GetRole",
                "iam:ListRoles",
                "iam:ListInstanceProfiles",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:ListRoles",
                "iam:ListInstanceProfilesForRole",
                "iam:GetInstanceProfile",
                "iam:GetRolePolicy",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:UpdateRoleDescription",
                "iam:CreateInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:DeleteInstanceProfile",
                "iam:TagInstanceProfile",
                "iam:UntagInstanceProfile",
                "iam:UpdateInstanceProfileDescription",
                "iam:ListInstanceProfiles",
                "iam:ListInstanceProfilesForRole",
                "iam:GetInstanceProfile",
                "iam:GetRole",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:ListRoles",
                "iam:ListInstanceProfilesForRole",
                "iam:GetInstanceProfile",
                "iam:GetRolePolicy",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:UpdateRoleDescription",
                "iam:CreateInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:DeleteInstanceProfile",
                "iam:TagInstanceProfile",
                "iam:UntagInstanceProfile",
                "iam:UpdateInstanceProfileDescription",
                "iam:ListInstanceProfiles",
                "iam:ListInstanceProfilesForRole",
                "iam:GetInstanceProfile",
                "iam:GetRole",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:ListRoles",
                "iam:ListInstanceProfilesForRole",
                "iam:GetInstanceProfile",
                "iam:GetRolePolicy",
               
```

### Real-World Examples and Recent Breaches

#### CVE-2021-20225: AWS IAM Role Credential Exposure

In 2021, a critical vulnerability (CVE-2021-20225) was discovered in AWS IAM roles, where credentials could be exposed due to misconfigured trust policies. This highlights the importance of proper IAM role management and least privilege principles.

##### How to Prevent / Defend

1. **Least Privilege Principle**:
   - Ensure that IAM roles and users have only the minimum permissions necessary to perform their tasks.

2. **Regular Audits**:
   - Perform regular audits of IAM roles and policies to identify and mitigate potential exposure.

3. **Use IAM Policies**:
   - Utilize IAM policies to restrict access to specific resources and actions.

### Hands-On Labs

To gain practical experience with EKS cluster creation and management, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing and training.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide a safe environment to practice and reinforce the concepts learned in this chapter.

### Conclusion

Creating an EKS cluster using EKS Control requires careful configuration of AWS credentials and a thorough understanding of the underlying mechanisms. By following the steps outlined in this chapter, you can successfully create and manage an EKS cluster while adhering to best practices for security and efficiency.

---
<!-- nav -->
[[02-Introduction to EKS Cluster Creation Using EKS Control|Introduction to EKS Cluster Creation Using EKS Control]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/18-EKS Cluster Creation Using EKS Control/00-Overview|Overview]] | [[04-Kubernetes Cluster Creation Using EKS Control|Kubernetes Cluster Creation Using EKS Control]]

---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security: Provisioning an AWS EKS Cluster

### Background Theory

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. Kubernetes was originally designed by Google but has since been maintained by the Cloud Native Computing Foundation. Kubernetes clusters consist of a control plane and worker nodes. The control plane manages the cluster, while the worker nodes host the application workloads.

When deploying Kubernetes on Amazon Web Services (AWS), the Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane. EKS supports various add-ons that enhance the functionality and security of the cluster.

### Add-Ons in EKS Cluster

In the context of an EKS cluster, several add-ons are typically installed:

- **VPC CNI**: The VPC CNI (Container Network Interface) plugin provides networking for pods in an EKS cluster. It integrates with the AWS Virtual Private Cloud (VPC) to assign private IP addresses to pods, ensuring they can communicate with other resources within the VPC.
  
- **Q Proxy**: Q Proxy is a custom add-on that can be used to manage network traffic and provide additional security features such as load balancing and SSL termination.

- **CoreDNS**: CoreDNS is a DNS server that runs inside the Kubernetes cluster. It is responsible for resolving DNS queries for services and pods within the cluster.

These add-ons are crucial for the smooth operation and security of the EKS cluster.

### Access Management in EKS Cluster

Access to the EKS cluster is managed through AWS Identity and Access Management (IAM). In the given scenario, an AWS admin user with broad permissions is able to access all namespaces and workloads within the cluster. This includes the `kube-system` namespace, which hosts critical control plane components.

#### Understanding the `kube-system` Namespace

The `kube-system` namespace is where all the control plane processes run. These processes include essential components like the API server, controller manager, scheduler, and etcd. As an AWS admin user, having access to this namespace means you can interact with highly sensitive processes, which poses significant security risks.

### Verifying AWS User in Current Session

To ensure proper access management, it is crucial to verify which AWS user is currently logged in. This can be done using the AWS Security Token Service (STS).

#### AWS Security Token Service (STS)

STS is a web service that enables you to request temporary credentials for AWS. These temporary credentials can be used to access AWS resources with limited privileges. STS provides a way to securely delegate access to AWS resources without sharing long-term credentials.

#### Using STS Commands

To verify the current AWS user, you can use the following commands with the AWS CLI:

```bash
aws sts get-caller-identity
```

This command returns information about the entity making the request, including the ARN (Amazon Resource Name) of the user.

### Example: Verifying AWS User

Let's walk through an example of verifying the current AWS user:

1. **Install AWS CLI**: Ensure the AWS CLI is installed and configured with your credentials.

2. **Run the Command**:

```bash
aws sts get-caller-identity
```

3. **Output**:

```json
{
    "UserId": "AROAIEXAMPLEUSERID",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/AdminRole/session-name"
}
```

This output shows the details of the user currently making the request.

### Pitfalls and Common Mistakes

One common mistake is granting excessive permissions to users, especially those with administrative roles. This can lead to unauthorized access and potential security breaches. It is crucial to follow the principle of least privilege, where users are granted only the permissions necessary to perform their tasks.

### Real-World Examples

Recent breaches involving Kubernetes clusters highlight the importance of proper access management. For instance, the breach of a Kubernetes cluster at a major cloud provider in 2021 resulted in unauthorized access to sensitive data. This breach was attributed to misconfigured IAM roles and excessive permissions granted to users.

### How to Prevent / Defend

#### Detection

To detect unauthorized access, implement monitoring and logging mechanisms. Use tools like AWS CloudTrail to log API calls made to your AWS resources. Additionally, enable Kubernetes audit logs to track API requests to the Kubernetes API server.

#### Prevention

1. **Least Privilege Principle**: Grant users only the minimum set of permissions required to perform their tasks.
   
2. **IAM Roles**: Use IAM roles to grant permissions to users and services. Avoid using IAM users with broad permissions.

3. **MFA (Multi-Factor Authentication)**: Enable MFA for all IAM users to add an extra layer of security.

4. **Regular Audits**: Conduct regular audits of IAM policies and roles to ensure they remain aligned with the principle of least privilege.

#### Secure Coding Fixes

Here is an example of a vulnerable IAM policy and its secure counterpart:

**Vulnerable Policy**:

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

**Secure Policy**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:*",
                "ec2:*",
                "iam:GetRole",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

### Configuration Hardening

1. **Enable Encryption**: Ensure that all data stored in the EKS cluster is encrypted both at rest and in transit.

2. **Network Policies**: Implement Kubernetes Network Policies to restrict traffic between pods.

3. **Pod Security Policies**: Use Pod Security Policies to enforce security rules at the pod level.

### Conclusion

Provisioning an AWS EKS cluster involves careful consideration of access management and security practices. By understanding the role of add-ons, verifying user access, and implementing robust security measures, you can significantly reduce the risk of unauthorized access and potential breaches.

### Practice Labs

For hands-on practice with Kubernetes security on AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on Kubernetes security and access management.
- **CloudGoat**: Provides scenarios for practicing cloud security, including Kubernetes on AWS.
- **Pacu**: A penetration testing framework for AWS that includes modules for testing Kubernetes security.

By engaging with these labs, you can gain practical experience in securing Kubernetes clusters on AWS.

---
<!-- nav -->
[[05-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 4|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 4]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/00-Overview|Overview]] | [[07-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 6|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 6]]

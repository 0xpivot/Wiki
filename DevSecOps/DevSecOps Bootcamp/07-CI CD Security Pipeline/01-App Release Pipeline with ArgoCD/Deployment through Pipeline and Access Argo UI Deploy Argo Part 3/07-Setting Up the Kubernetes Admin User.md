---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Setting Up the Kubernetes Admin User

To begin, we need to set up the Kubernetes admin user within our environment. This involves creating a new terminal session and configuring the necessary AWS access credentials. Let's break down each step and understand the underlying mechanisms.

### Creating a New Terminal Session

When working with Kubernetes, especially in a cloud environment like AWS, it's crucial to have a dedicated terminal session for administrative tasks. This ensures that your environment variables and configurations are isolated and specific to the task at hand.

```bash
# Open a new terminal session
```

### Setting AWS Access Credentials

Next, we need to set the AWS access credentials for our Kubernetes admin user. This involves setting the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

#### Explanation

- **AWS_ACCESS_KEY_ID**: This is a unique identifier for your AWS user. It is used in conjunction with the secret access key to authenticate API requests.
- **AWS_SECRET_ACCESS_KEY**: This is a secret key associated with your AWS user. It should be kept confidential and never shared.

#### Why This Matters

Setting these environment variables allows you to interact with AWS services programmatically. Without these credentials, you would not be able to perform actions such as assuming roles or accessing resources within your AWS account.

### Verifying the Credentials

Once the credentials are set, we can verify them using the `sts get-caller-identity` command. This command returns information about the AWS user making the request.

```bash
aws sts get-caller-identity
```

#### Expected Output

```json
{
    "UserId": "AROAEXAMPLEUSERID",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::111122223333:user/kubernetes-admin"
}
```

#### Explanation

- **UserId**: A unique identifier for the user.
- **Account**: The AWS account number.
- **Arn**: The Amazon Resource Name (ARN) uniquely identifies the user.

### Assuming the External Admin Role

In many organizations, users are granted permissions through roles rather than directly. To assume a role, you need to use the `sts assume-role` command.

```bash
export AWS_SESSION_TOKEN=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/external-admin --role-session-name kubernetes-admin | jq -r '.Credentials.SessionToken')
export AWS_ACCESS_KEY_ID=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/external-admin --role-session-name kubernetes-admin | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/external-admin --role-session-name k-ubernetes-admin | jq -r '.Credentials.SecretAccessKey')
```

#### Explanation

- **Role ARN**: The ARN of the role you want to assume.
- **Role Session Name**: A unique identifier for the session.

#### Why This Matters

Assuming a role allows you to temporarily gain the permissions associated with that role. This is a best practice for managing permissions securely.

### Authenticating with Kubernetes

Now that we have assumed the role, we need to authenticate with Kubernetes. This typically involves configuring `kubectl` to use the correct context.

```bash
aws eks update-kubeconfig --name my-cluster --region us-west-2
```

#### Explanation

- **Cluster Name**: The name of your EKS cluster.
- **Region**: The AWS region where your cluster is located.

#### Why This Matters

This command updates your `kubeconfig` file to include the necessary authentication information for your EKS cluster.

### Checking the Deployed Pods

With authentication in place, we can now check the pods deployed in the `argocd` namespace.

```bash
kubectl get pods -n argocd
```

#### Expected Output

```plaintext
NAME                       READY   STATUS    RESTARTS   AGE
argocd-dex-server-0        1/1     Running   0          10m
argocd-redis               1/1     Running   0          10m
argocd-repo-server-5b8c8f  1/1     Running   0          10m
argocd-server-758b9f       1/1     Running   0          10m
```

#### Explanation

These pods are part of the Argo CD installation. Each pod serves a specific function within the Argo CD architecture.

### Accessing the Argo CD UI

Argo CD comes with a web-based UI that provides an overview of the deployment status and repository connections.

#### Retrieving the Initial Admin Password

The initial admin password is stored in a Kubernetes secret named `argocd-initial-admin-secret`.

```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 --decode
```

#### Explanation

- **Secret Name**: `argocd-initial-admin-secret`
- **Namespace**: `argocd`

#### Why This Matters

The initial admin password is required to log in to the Argo CD UI for the first time.

### How to Prevent / Defend

#### Detection

Regularly monitor your AWS console and Kubernetes logs for unauthorized access attempts. Use tools like AWS CloudTrail and Kubernetes audit logs to track activity.

#### Prevention

- **Least Privilege Principle**: Grant users only the permissions they need.
- **MFA**: Enable Multi-Factor Authentication (MFA) for all users.
- **IAM Policies**: Use IAM policies to restrict access to sensitive resources.

#### Secure Coding Fixes

Compare the insecure setup with the secure setup:

**Insecure Setup**

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Secure Setup**

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws iam create-access-key --user-name kubernetes-admin
```

#### Hardening

- **Rotate Credentials Regularly**: Change access keys periodically.
- **Use IAM Roles**: Instead of granting direct permissions, use IAM roles.

### Real-World Examples

#### Recent Breaches

- **CVE-2021-44228 (Log4Shell)**: This vulnerability could allow attackers to execute arbitrary code on affected systems. Ensure that all dependencies are up-to-date and patched.
- **AWS S3 Bucket Exposure**: Misconfigured S3 buckets can lead to data exposure. Use bucket policies and encryption to protect data.

### Mermaid Diagrams

#### Architecture Diagram

```mermaid
graph LR
  A[Kubernetes Cluster] --> B[Argo CD]
  B --> C[Argo CD Server]
  B --> D[Argo CD Repo Server]
  B --> E[Argo CD Dex Server]
  B --> F[Argo CD Redis]
  G[AWS IAM] --> H[External Admin Role]
  H --> I[Kubernetes Admin User]
  I --> J[kubectl]
  K[User] --> L[Argo CD UI]
```

### Practice Labs

For hands-on experience with Argo CD and Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes Kubernetes modules.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security skills.
- **CloudGoat**: A series of labs designed to help you learn about securing AWS environments.
- **Pacu**: A collection of AWS security tools and labs.

By following these steps and understanding the underlying concepts, you can effectively manage and secure your Kubernetes cluster with Argo CD.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/06-Setting Up a CICD Pipeline with ArgoCD|Setting Up a CICD Pipeline with ArgoCD]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/08-Practice Questions & Answers|Practice Questions & Answers]]

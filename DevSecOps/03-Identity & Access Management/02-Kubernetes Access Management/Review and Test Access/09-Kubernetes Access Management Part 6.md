---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized users and services can interact with the cluster resources. This involves managing identities, roles, and permissions within the Kubernetes environment. The goal is to maintain a secure and controlled environment where access is granted based on the principle of least privilege.

### Understanding Temporary Users and Sessions

In Kubernetes, one common practice is to use temporary users for specific sessions. These temporary users are created for a short period to perform administrative tasks and then destroyed once the tasks are completed. This approach minimizes the exposure of sensitive credentials and reduces the risk of unauthorized access.

#### Creating a Temporary User

To create a temporary user, you typically use an identity provider (IDP) that integrates with Kubernetes. For example, you might use AWS Identity and Access Management (IAM) to create a temporary user. Here’s a step-by-step process:

1. **Assume a Role**: You assume a role that grants you the necessary permissions for the session.
2. **Generate Temporary Credentials**: The IDP generates temporary credentials (access key, secret key, and session token) for the session.
3. **Use Temporary Credentials**: You use these temporary credentials to authenticate and perform actions within the Kubernetes cluster.

Here’s an example using AWS CLI to assume a role and generate temporary credentials:

```bash
# Assume a role and generate temporary credentials
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/KubernetesAdminRole --role-session-name MySessionName
```

This command returns a JSON object containing the temporary credentials:

```json
{
    "Credentials": {
        "AccessKeyId": "ASIA...",
        "SecretAccessKey": "wJalrXUtnFEMI/K7DdlnZ3p...",
        "SessionToken": "FwoGZXIvY...==",
        "Expiration": "2023-10-10T12:34:56Z"
    }
}
```

### Testing Access with Admin User

Before testing access with a developer user, it’s essential to validate that the admin user has the correct permissions. This ensures that the setup is working as expected.

#### Setting Up the Admin User

To set up the admin user, you need to configure the `kubeconfig` file with the appropriate credentials. Here’s an example of how to set up the `kubeconfig` file:

```bash
# Export the access key and secret key
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7DdlnZ3p...

# Configure kubectl to use the admin user
kubectl config set-credentials admin-user --exec-command="aws-iam-authenticator" --exec-arg="token" --exec-arg="-i" --exec-arg="k8s-admin"

# Set the context to use the admin user
kubectl config set-context k8s-admin --cluster=k8s-cluster --user=admin-user

# Switch to the admin context
kubectl config use-context k8s-admin
```

### Testing Access with Developer User

After validating the admin user, the next step is to test the developer user. This ensures that the developer user has the correct permissions and cannot access resources they shouldn’t.

#### Setting Up the Developer User

To set up the developer user, you need to configure the `kubeconfig` file with the appropriate credentials. Here’s an example of how to set up the `kubeconfig` file:

```bash
# Export the access key and secret key for the developer user
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7DdlnZ3p...

# Configure kubectl to use the developer user
kubectl config set--credentials developer-user --exec-command="aws-iam-authenticator" --exec-arg="token" --exec-arg="-i" --exec-arg="k8s-developer"

# Set the context to use the developer user
kubectl config set-context k8s-developer --cluster=k8s-cluster --user=developer-user

# Switch to the developer context
kubectl config use-context k8s-developer
```

### Verifying Permissions

Once the developer user is set up, you need to verify that they have the correct permissions. This involves checking if they can access the necessary resources and cannot access restricted resources.

#### Checking Node Access

To check if the developer user can access nodes, you can run the following command:

```bash
kubectl get nodes
```

If the developer user does not have the necessary permissions, you will receive an error message indicating that they do not have access.

### Assuming External Developer Role

To grant the developer user the necessary permissions, you need to assume an external developer role. This role provides the required permissions to access the Kubernetes cluster.

#### Assuming the Role

To assume the role, you can use the following command:

```bash
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/ExternalDeveloperRole --role-session-name MySessionName
```

This command returns a JSON object containing the temporary credentials:

```json
{
    "Credentials": {
        "AccessKeyId": "ASIA...",
        "SecretAccessKey": "wJalrXUtnFEMI/K7DdlnZ3p...",
        "SessionToken": "FwoGZXIvY...==",
        "Expiration": "2023-10-10T12:34:56Z"
    }
}
```

### Secure Coding Practices

To ensure that your Kubernetes cluster remains secure, it’s important to follow secure coding practices. This includes using least privilege principles, regularly auditing permissions, and monitoring access logs.

#### Least Privilege Principle

The least privilege principle states that users should have the minimum level of access necessary to perform their tasks. This reduces the risk of unauthorized access and minimizes the potential damage if credentials are compromised.

#### Regular Auditing

Regularly auditing permissions ensures that users have the correct level of access. This involves reviewing roles and permissions periodically and making adjustments as needed.

#### Monitoring Access Logs

Monitoring access logs helps you detect unauthorized access attempts. This involves setting up logging and monitoring tools to track access to the Kubernetes cluster.

### Real-World Examples

Recent breaches and vulnerabilities in Kubernetes clusters highlight the importance of proper access management. For example, the Kubernetes API server was found to be vulnerable to a series of attacks, including unauthorized access and privilege escalation.

#### CVE-2021-25741

CVE-2021-25741 is a vulnerability in the Kubernetes API server that allows attackers to bypass authentication and gain unauthorized access to the cluster. This vulnerability highlights the importance of properly configuring and securing the API server.

#### CVE-2021-25742

CVE-2021-25742 is another vulnerability in the Kubernetes API server that allows attackers to escalate privileges and gain unauthorized access to the cluster. This vulnerability underscores the importance of using least privilege principles and regularly auditing permissions.

### How to Prevent / Defend

To prevent unauthorized access and ensure the security of your Kubernetes cluster, you should follow these best practices:

#### Use Least Privilege Principles

Ensure that users have the minimum level of access necessary to perform their tasks. This reduces the risk of unauthorized access and minimizes the potential damage if credentials are compromised.

#### Regularly Audit Permissions

Regularly review roles and permissions to ensure that users have the correct level of access. This involves making adjustments as needed and removing unnecessary permissions.

#### Monitor Access Logs

Set up logging and monitoring tools to track access to the Kubernetes cluster. This helps you detect unauthorized access attempts and respond quickly to potential threats.

#### Harden Configuration

Harden the configuration of the Kubernetes API server to prevent unauthorized access. This involves disabling unnecessary features and ensuring that the API server is properly configured.

### Conclusion

Proper access management is crucial for securing your Kubernetes cluster. By following best practices such as using least privilege principles, regularly auditing permissions, and monitoring access logs, you can ensure that your cluster remains secure and protected against unauthorized access.

### Practice Labs

For hands-on experience with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab that simulates a Kubernetes cluster and provides exercises to practice securing access.
- **OWASP WrongSecrets**: A lab that focuses on securing secrets in Kubernetes and provides exercises to practice managing access to secrets.
- **kube-hunter**: A tool that helps you identify and mitigate security vulnerabilities in your Kubernetes cluster. It provides a hands-on experience to practice securing access.

These labs provide practical experience and help you master the skills needed to manage access in a Kubernetes cluster securely.

---
<!-- nav -->
[[08-Kubernetes Access Management Part 5|Kubernetes Access Management Part 5]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[10-Kubernetes Access Management Part 7|Kubernetes Access Management Part 7]]

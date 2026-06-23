---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Secrets Management with HashiCorp Vault

### Introduction to Secrets Management

Secrets management is a critical aspect of modern DevSecOps practices. In the context of cloud-native applications, secrets such as API keys, database passwords, and encryption keys are essential for securing data and services. However, managing these secrets securely and efficiently can be challenging. This is where tools like HashiCorp Vault come into play.

Vault is an open-source tool designed to help organizations securely store, manage, and distribute secrets. It provides a centralized way to manage secrets across various environments and applications, ensuring that sensitive information remains protected.

### Dynamic Generation of Short-Lived Credentials

One of the primary use cases for Vault is the dynamic generation of short-lived credentials. This approach is particularly useful when dealing with cloud services like Amazon S3 buckets. Instead of providing static IAM credentials to applications, Vault allows you to define roles and dynamically generate short-lived credentials as needed.

#### Why Use Short-Lived Credentials?

Static credentials pose significant security risks. If a static credential is compromised, an attacker can potentially gain unauthorized access to your resources for an extended period. By using short-lived credentials, you minimize the window of opportunity for an attacker to exploit a stolen credential.

#### How Does Vault Generate Short-Lived Credentials?

Vault integrates with various cloud providers, including AWS, to generate short-lived credentials. Here’s a step-by-step breakdown of how this works:

1. **Define a Role**: You first define a role in Vault that specifies the permissions required for accessing a particular resource, such as an S3 bucket.
2. **Generate Credentials**: When an application needs to access the resource, it requests credentials from Vault. Vault then generates a set of short-lived credentials based on the defined role.
3. **Use Credentials**: The application uses these credentials to access the resource. Once the credentials expire, they cannot be reused.

#### Example: Generating Short-Lived AWS IAM Credentials

Let's walk through an example of generating short-lived AWS IAM credentials using Vault.

```bash
# Enable the AWS auth method in Vault
vault auth enable aws

# Configure the AWS auth method with the necessary parameters
vault write auth/aws/config \
    access_key=YOUR_ACCESS_KEY \
    secret_key=YOUR_SECRET_KEY \
    region=us-west-2

# Create a role that maps to an IAM policy
vault write auth/aws/role/my-role \
    policies=my-policy \
    bound_iam_role_arn=arn:aws:iam::123456789012:role/my-role \
    ttl=1h

# Authenticate with Vault using AWS credentials
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY

# Retrieve short-lived credentials
vault login -method=aws role=my-role
```

In this example, we first enable the AWS auth method in Vault and configure it with the necessary AWS credentials. We then create a role that maps to an IAM policy and specify the TTL (time-to-live) for the generated credentials. Finally, we authenticate with Vault using AWS credentials and retrieve the short-lived credentials.

### Public Key Infrastructure (PKI) for Certificate Management

Another common use case for Vault is managing public key infrastructure (PKI) for certificate management. PKI is a complex process that involves generating, distributing, and managing digital certificates. Traditionally, certificates have been long-lived, often lasting several years, due to the complexity involved in generating and rotating them.

#### Why Use Short-Lived Certificates?

Long-lived certificates pose significant security risks. If a certificate is compromised, an attacker can potentially impersonate the entity associated with the certificate for an extended period. By using short-lived certificates, you reduce the potential damage caused by a compromised certificate.

#### How Does Vault Manage Certificates?

Vault provides a PKI backend that allows you to programmatically generate and manage certificates. Here’s a step-by-step breakdown of how this works:

1. **Enable PKI Backend**: You first enable the PKI backend in Vault.
2. **Configure CA**: You configure a root CA or intermediate CA.
3. **Issue Certificates**: You issue certificates based on predefined policies.
4. **Renew Certificates**: You renew certificates before they expire.

#### Example: Issuing Short-Lived Certificates

Let's walk through an example of issuing short-lived certificates using Vault.

```bash
# Enable the PKI backend in Vault
vault secrets enable pki

# Configure the root CA
vault write pki/root/generate/internal \
    common_name="example.com" \
    ttl=8760h

# Create a role for issuing certificates
vault write pki/roles/example-dot-com \
    allowed_domains="example.com" \
    max_ttl=72h

# Issue a certificate
vault write pki/issue/example-dot-com \
    common_name="www.example.com"
```

In this example, we first enable the PKI backend in Vault and configure a root CA with a TTL of 8760 hours (one year). We then create a role for issuing certificates with a maximum TTL of 72 hours. Finally, we issue a certificate for `www.example.com`.

### SSH Secret Backend for Dynamic Key Generation

Vault also provides an SSH secret backend for generating SSH keys dynamically. This feature is particularly useful for managing SSH access to a fleet of servers. Instead of using a single SSH key for all servers, you can generate a unique key for each server.

#### Why Use Unique SSH Keys?

Using a single SSH key for all servers poses significant security risks. If the key is compromised, an attacker can potentially gain access to all servers. By using unique keys for each server, you isolate the impact of a compromised key to a single server.

#### How Does Vault Generate SSH Keys?

Vault integrates with the SSH backend to generate unique SSH keys for each server. Here’s a step-by-step breakdown of how this works:

1. **Enable SSH Backend**: You first enable the SSH backend in Vault.
2. **Configure SSH Keys**: You configure the SSH keys for each server.
3. **Generate SSH Keys**: You generate SSH keys for each server based on predefined policies.

#### Example: Generating Unique SSH Keys

Let's walk through an example of generating unique SSH keys using Vault.

```bash
# Enable the SSH backend in Vault
vault secrets enable ssh

# Configure the SSH backend
vault write ssh/config/ca \
    public_key=@public_key.pem \
    private_key=@private_key.pem

# Generate an SSH key for a server
vault write ssh/sign/my-role \
    public_key=@public_key.pem
```

In this example, we first enable the SSH backend in Vault and configure the CA with the public and private keys. We then generate an SSH key for a server based on the predefined role.

### Kubernetes Secret Backend for Service Account Tokens

Vault also provides a Kubernetes secret backend for generating Kubernetes service account tokens. This feature is particularly useful for managing access to Kubernetes resources.

#### Why Use Service Account Tokens?

Service account tokens provide a secure way to authenticate with Kubernetes resources. By using tokens, you can ensure that only authorized entities can access your resources.

#### How Does Vault Generate Service Account Tokens?

Vault integrates with the Kubernetes backend to generate service account tokens. Here’s a step-by-step breakdown of how this works:

1. **Enable Kubernetes Backend**: You first enable the Kubernetes backend in Vault.
2. **Configure Service Accounts**: You configure the service accounts for each resource.
3. **Generate Tokens**: You generate tokens for each service account based on predefined policies.

#### Example: Generating Service Account Tokens

Let's walk through an example of generating service account tokens using Vault.

```bash
# Enable the Kubernetes backend in Vault
vault auth enable kubernetes

# Configure the Kubernetes backend
vault write auth/kubernetes/config \
    token_reviewer_jwt=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token) \
    kubernetes_host=https://$KUBERNETES_PORT_443_TCP_ADDR:443 \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create a role for a service account
vault write auth/kubernetes/role/my-role \
    bound_service_account_names=default \
    bound_service_account_namespaces=default \
    policies=my-policy \
    ttl=1h

# Authenticate with Vault using a service account token
kubectl exec -it $(kubectl get pods -l app=vault -o jsonpath='{.items[0].metadata.name}') -- vault login -method=kubernetes role=my-role
```

In this example, we first enable the Kubernetes backend in Vault and configure it with the necessary parameters. We then create a role for a service account and specify the policies and TTL. Finally, we authenticate with Vault using a service account token.

### Integration with Various Tools

Vault ties in the mechanisms of various tools, including AWS IAM service, database access management, Kubernetes RBAC, and more. It uses the existing mechanisms of these tools to create temporary credentials for clients, acting as a broker of authentication.

#### How Does Vault Integrate with Different Tools?

Vault provides a unified interface for managing secrets across different tools. Here’s a step-by-step breakdown of how this works:

1. **Enable Auth Methods**: You first enable the appropriate auth methods in Vault.
2. **Configure Policies**: You configure policies for each tool.
3. **Generate Credentials**: You generate credentials based on the configured policies.

#### Example: Integrating with AWS IAM and Kubernetes

Let's walk through an example of integrating Vault with AWS IAM and Kubernetes.

```bash
# Enable the AWS auth method in Vault
vault auth enable aws

# Configure the AWS auth method with the necessary parameters
vault write auth/aws/config \
    access_key=YOUR_ACCESS_KEY \
    secret_key=YOUR_SECRET_KEY \
    region=us-west-2

# Create a role that maps to an IAM policy
vault write auth/aws/role/my-role \
    policies=my-policy \
    bound_iam_role_arn=arn:aws:iam::123456789012:role/my-role \
    ttl=1h

# Enable the Kubernetes auth method in Vault
vault auth enable kubernetes

# Configure the Kubernetes auth method with the necessary parameters
vault write auth/kubernetes/config \
    token_reviewer_jwt=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token) \
    kubernetes_host=https://$KUBERNETES_PORT_443_TCP_ADDR:443 \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create a role for a service account
vault write auth/kubernetes/role/my-role \
    bound_service_account_names=default \
    bound_service_account_namespaces=default \
    policies=my-policy \
    ttl=1h
```

In this example, we first enable the AWS auth method in Vault and configure it with the necessary parameters. We then create a role that maps to an IAM policy. Next, we enable the Kubernetes auth method in Vault and configure it with the necessary parameters. Finally, we create a role for a service account.

### Pitfalls and Best Practices

While Vault provides a robust solution for secrets management, there are several pitfalls to be aware of:

1. **Configuration Errors**: Incorrect configuration can lead to security vulnerabilities. Ensure that you follow best practices for configuring Vault.
2. **Credential Exposure**: Exposing credentials can lead to unauthorized access. Ensure that you use short-lived credentials and rotate them regularly.
3. **Insufficient Monitoring**: Lack of monitoring can make it difficult to detect and respond to security incidents. Ensure that you monitor Vault logs and alerts.

#### Best Practices

1. **Use Short-Lived Credentials**: Use short-lived credentials to minimize the window of opportunity for an attacker to exploit a stolen credential.
2. **Rotate Credentials Regularly**: Rotate credentials regularly to ensure that compromised credentials are no longer valid.
3. **Monitor Logs and Alerts**: Monitor Vault logs and alerts to detect and respond to security incidents.

### Real-World Examples

Several real-world examples demonstrate the importance of secrets management:

1. **Equifax Breach**: In 2017, Equifax suffered a massive breach that exposed the personal data of millions of customers. One of the contributing factors was the use of default credentials for a web application.
2. **Capital One Breach**: In 2019, Capital One suffered a breach that exposed the personal data of over 100 million customers. One of the contributing factors was the use of default credentials for an AWS S3 bucket.

### How to Prevent / Defend

To prevent and defend against secrets management vulnerabilities, follow these steps:

1. **Use Vault for Secrets Management**: Use Vault to centrally manage and distribute secrets.
2. **Implement Short-Lived Credentials**: Implement short-lived credentials to minimize the window of opportunity for an attacker to exploit a stolen credential.
3. **Rotate Credentials Regularly**: Rotate credentials regularly to ensure that compromised credentials are no longer valid.
4. **Monitor Logs and Alerts**: Monitor Vault logs and alerts to detect and respond to security incidents.

#### Secure Coding Fixes

Here’s an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**

```python
import boto3

def get_s3_client():
    return boto3.client('s3', aws_access_key_id='YOUR_ACCESS_KEY', aws_secret_access_key='YOUR_SECRET_KEY')
```

**Secure Code:**

```python
import boto3
import os

def get_s3_client():
    return boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
```

In the secure code, we use environment variables to store the AWS credentials instead of hardcoding them in the code.

### Configuration Hardening

To harden your Vault configuration, follow these steps:

1. **Enable TLS**: Enable TLS to encrypt communication between Vault and clients.
2. **Enable Auditing**: Enable auditing to log all actions performed within Vault.
3. **Restrict Access**: Restrict access to Vault by using least privilege principles.

#### Example: Enabling TLS

```bash
# Enable TLS in Vault
vault write sys/tls/config \
    cert=@cert.pem \
    key=@key.pem
```

In this example, we enable TLS in Vault by specifying the certificate and key files.

### Conclusion

Vault provides a robust solution for secrets management, enabling you to securely store, manage, and distribute secrets across various environments and applications. By following best practices and implementing secure coding fixes, you can effectively prevent and defend against secrets management vulnerabilities.

### Practice Labs

For hands-on experience with Vault, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application that includes challenges related to secrets management.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that includes challenges related to secrets management.
- **WebGoat**: An interactive training application that includes challenges related to secrets management.

These labs provide practical experience with secrets management and help you understand the real-world implications of misconfigurations and vulnerabilities.

---
<!-- nav -->
[[07-Secrets Management with HashiCorp Vault Part 2|Secrets Management with HashiCorp Vault Part 2]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/09-Practice Questions & Answers|Practice Questions & Answers]]

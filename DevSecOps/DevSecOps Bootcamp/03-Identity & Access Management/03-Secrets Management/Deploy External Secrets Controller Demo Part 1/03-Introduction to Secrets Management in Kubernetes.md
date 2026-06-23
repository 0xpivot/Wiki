---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in Kubernetes

### Background Theory

In modern DevOps environments, managing sensitive information such as API keys, database passwords, and other credentials securely is critical. Kubernetes provides several mechanisms to manage secrets, but these mechanisms often require additional layers of security to ensure that sensitive data remains protected both at rest and in transit. One popular approach is to use an external secrets controller, which allows you to store secrets in an external secrets management system (like AWS Secrets Manager) and automatically sync them into Kubernetes as native secrets.

### Kubernetes Service Accounts

A Kubernetes service account is a way to manage identities for processes that run in a pod. Each pod in Kubernetes runs with a service account, which provides the pod with an identity that can be used to authenticate to the Kubernetes API server and other services. Service accounts are defined in a `ServiceAccount` resource, which can be created using a Kubernetes manifest file.

#### Example of a Service Account Manifest

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: online-boutique
```

This manifest defines a service account named `my-service-account` in the `online-boutique` namespace. The `metadata` section contains the `name` and `namespace` attributes, which specify the name and namespace of the service account.

### Metadata Attribute

The `metadata` attribute in a Kubernetes manifest file is used to define metadata about the resource, such as its name, labels, and annotations. In the context of a service account, the `metadata` attribute is used to define the name and namespace of the service account.

#### Example of Metadata Attribute

```yaml
metadata:
  name: my-service-account
  namespace: online-boutique
```

Here, the `name` attribute specifies the name of the service account, and the `namespace` attribute specifies the namespace in which the service account will be created.

### Namespace Context

Namespaces in Kubernetes provide a way to divide cluster resources between multiple users or projects. By default, Kubernetes creates a `default` namespace, but you can create additional namespaces to isolate different parts of your application or different teams within your organization.

In the context of the `online-boutique` application, the service account and the secrets it manages will be created in the `online-boutique` namespace. This ensures that the secrets are accessible only to the pods running in the `online-boutique` namespace.

### External Secrets Controller

The External Secrets Controller is a Kubernetes operator that fetches secrets from an external secrets management system (such as AWS Secrets Manager) and stores them as native Kubernetes secrets. This allows you to manage your secrets in a centralized location while still being able to use them in your Kubernetes applications.

#### How External Secrets Work

When you configure the External Secrets Controller, you define a Custom Resource Definition (CRD) that specifies the external secrets to fetch and where to store them in Kubernetes. The controller periodically checks the external secrets management system and updates the corresponding Kubernetes secrets.

#### Example of External Secrets CRD

```yaml
apiVersion: externalsecrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
  namespace: online-boutique
spec:
  backendType: aws-secrets-manager
  dataFrom:
    - key: my-secret-key
      name: my-kubernetes-secret
```

This CRD defines an external secret named `my-external-secret` in the `online-boutique` namespace. The `backendType` attribute specifies the type of external secrets management system to use (in this case, AWS Secrets Manager). The `dataFrom` attribute specifies the key in the external secrets management system (`my-secret-key`) and the name of the Kubernetes secret to create (`my-kubernetes-secret`).

### Service Account Role Mapping

To allow the External Secrets Controller to fetch secrets from the external secrets management system, you need to map the Kubernetes service account to an AWS role. This is done by adding an annotation to the service account that specifies the AWS role to use.

#### Example of Service Account Annotation

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: online-boutique
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-role
```

Here, the `annotations` section contains an annotation that maps the service account to an AWS role. The `eks.amazonaws.com/role-arn` key specifies the ARN of the AWS role to use.

### AWS Role Configuration

The AWS role specified in the service account annotation must have the necessary permissions to access the secrets in the external secrets management system. This is typically done by attaching an IAM policy to the role that grants the required permissions.

#### Example of IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}
```

This IAM policy grants the role permission to retrieve secrets from AWS Secrets Manager.

### Full Example

Let's put all of this together into a complete example. We'll create a service account, an external secrets CRD, and an IAM policy to demonstrate how to set up the External Secrets Controller.

#### Step 1: Create the Service Account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: online-boutique
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-role
```

#### Step 2: Create the External Secrets CRD

```yaml
apiVersion: externalsecrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
  namespace: online-boutique
spec:
  backendType: aws-secrets-manager
  dataFrom:
    - key: my-secret-key
      name: my-kubernetes-secret
```

#### Step 3: Create the IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}
```

### Pitfalls and Best Practices

#### Pitfall: Incorrect Role Mapping

One common pitfall is incorrectly mapping the service account to the AWS role. Ensure that the ARN specified in the annotation matches the actual ARN of the role.

#### Best Practice: Least Privilege Principle

Always follow the least privilege principle when configuring IAM policies. Grant only the minimum permissions required to perform the necessary actions.

### Real-World Examples

#### Recent Breach: CVE-2021-25741

In 2021, a vulnerability was discovered in the AWS Secrets Manager that allowed unauthorized access to secrets. This highlights the importance of properly securing your secrets and ensuring that only authorized entities have access to them.

### How to Prevent / Defend

#### Detection

Regularly audit your IAM policies and roles to ensure that they are correctly configured and that only authorized entities have access to your secrets.

#### Prevention

1. **Use Strong IAM Policies**: Ensure that IAM policies are configured to grant only the minimum permissions required.
2. **Enable Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users to add an extra layer of security.
3. **Monitor Access Logs**: Regularly monitor access logs to detect any unauthorized access attempts.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: online-boutique
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-role
```

##### Secure Code

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: online-boutique
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-role
---
apiVersion: iam.aws.amazon.com/v1
kind: Policy
metadata:
  name: my-policy
spec:
  statements:
    - effect: Allow
      action: ["secretsmanager:GetSecretValue"]
      resource: "*"
```

### Conclusion

Managing secrets securely in a Kubernetes environment requires careful planning and implementation. By using an external secrets controller and properly configuring service accounts and IAM roles, you can ensure that your secrets remain secure both at rest and in transit.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including some aspects of secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on secrets management.

These labs provide practical experience with the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to Secrets Management in DevSecOps|Introduction to Secrets Management in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Deploy External Secrets Controller Demo Part 1/00-Overview|Overview]] | [[04-Introduction to Secrets Management Part 1|Introduction to Secrets Management Part 1]]

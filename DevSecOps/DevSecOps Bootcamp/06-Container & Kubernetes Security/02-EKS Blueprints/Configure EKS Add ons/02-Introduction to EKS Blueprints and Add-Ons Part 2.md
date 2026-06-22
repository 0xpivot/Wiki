---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Introduction to EKS Blueprints and Add-Ons

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes orchestration. EKS Blueprints are pre-configured templates that help you set up your EKS clusters quickly and securely. One of the key features of EKS is the ability to configure add-ons, which are additional services that enhance the functionality of your Kubernetes cluster.

### What Are EKS Add-Ons?

EKS Add-Ons are pre-built, managed services that extend the capabilities of your EKS cluster. These add-ons can include monitoring tools, logging solutions, security enhancements, and more. They are designed to integrate seamlessly with your EKS cluster and provide additional value without requiring you to manage the underlying infrastructure.

#### Why Use EKS Add-Ons?

Using EKS Add-Ons offers several benefits:

1. **Ease of Management**: Managed services handle the operational overhead, allowing you to focus on your applications.
2. **Integration**: Add-ons are designed to work seamlessly with EKS, ensuring compatibility and reducing integration issues.
3. **Security Enhancements**: Many add-ons provide security features such as network policies, intrusion detection, and compliance checks.
4. **Monitoring and Logging**: Add-ons can provide comprehensive monitoring and logging capabilities, helping you maintain visibility into your cluster's health and performance.

### Configuring EKS Add-Ons

To configure EKS Add-Ons, you typically follow these steps:

1. **Define the Configuration**: Create a Kubernetes configuration file that specifies the add-ons you want to enable.
2. **Commit the Changes**: Commit the configuration changes to your version control system.
3. **Trigger the Pipeline**: Ensure that your CI/CD pipeline is configured to apply these changes to your EKS cluster.
4. **Validate the Deployment**: Verify that the add-ons have been successfully deployed and are functioning as expected.

#### Example Configuration

Let's walk through an example of configuring an EKS add-on using Helm, a popular package manager for Kubernetes.

```yaml
# helm-provider.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: helm-provider-config
data:
  provider: aws
  region: us-west-2
  clusterName: my-cluster
```

This configuration defines a `ConfigMap` that specifies the Helm provider settings for an AWS EKS cluster.

### Committing the Configuration

Once the configuration is defined, you need to commit it to your version control system. This triggers your CI/CD pipeline to apply the changes to your EKS cluster.

```bash
git status
git add .
git commit -m "Add Helm provider configuration"
git push origin feature/helm-provider
```

#### CI/CD Pipeline Execution

The CI/CD pipeline will automatically trigger and apply the changes to the EKS cluster. You can monitor the progress of the deployment through the pipeline interface.

```bash
# Example pipeline output
Job: Deploy Helm Provider
Status: Success
```

### Validating the Deployment

After the deployment, you need to verify that the add-ons have been successfully added to the cluster. This can be done through both the AWS UI console and the Kubernetes CLI.

#### Accessing the Cluster via AWS Console

1. Log in to the AWS Management Console.
2. Navigate to the EKS dashboard.
3. Select your cluster and click on the "View cluster details" button.
4. Check the list of add-ons to ensure that the new add-on is listed.

#### Accessing the Cluster via CLI

You can also use the Kubernetes CLI to verify the deployment.

```bash
kubectl get pods --all-namespaces
```

This command lists all the pods across all namespaces, including those related to the newly deployed add-on.

### IAM Permissions and Access Control

One important aspect of managing EKS clusters is ensuring proper IAM permissions and access control. In the given transcript, the user encountered an issue where their IAM principal did not have access to Kubernetes objects in the cluster.

#### Understanding IAM Principals

An IAM principal is an entity that can make requests to AWS services. This includes IAM users, roles, and federated users. In the context of EKS, IAM principals are used to authenticate and authorize access to the Kubernetes API server.

#### Limiting Access

Limiting access to Kubernetes objects is crucial for maintaining security. By default, IAM users may not have the necessary permissions to view workloads in the cluster. This can be controlled through IAM policies and Kubernetes RBAC (Role-Based Access Control).

##### Example IAM Policy

Here is an example IAM policy that grants access to Kubernetes objects:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters",
                "eks:DescribeNodegroup",
                "eks:ListNodegroups",
                "eks:DescribeAddon",
                "eks:ListAddons"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": "arn:aws:iam::*:role/k8s-admin-role"
        }
    ]
}
```

This policy allows the IAM user to describe and list EKS clusters and addons, as well as assume a role that provides administrative access to the Kubernetes cluster.

##### Kubernetes RBAC

Kubernetes RBAC allows you to define roles and bindings that control access to resources within the cluster. Here is an example of a Kubernetes Role and RoleBinding:

```yaml
# k8s-rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: alice # Name is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This Role and RoleBinding grant the user `alice` permission to read pods in the `default` namespace.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can use AWS CloudTrail and Kubernetes audit logs. CloudTrail records API calls made to AWS services, while Kubernetes audit logs record API requests to the Kubernetes API server.

##### Example CloudTrail Log

```json
{
    "eventVersion": "1.05",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAJDPLRKLG7UEXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/admin",
        "accountId": "123456789012",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "userName": "admin"
    },
    "eventTime": "2023-10-01T12:34:56Z",
    "eventSource": "eks.amazonaws.com",
    "eventName": "DescribeCluster",
    "awsRegion": "us-west-2",
    "sourceIPAddress": "192.0.2.0",
    "userAgent": "aws-cli/2.0.0 Python/3.7.3 Linux/4.14.128-139.315.amzn2.x86_64 exe/macosx",
    "requestParameters": {
        "name": "my-cluster"
    },
    "responseElements": null,
    "requestID": "request-id",
    "eventID": "event-id",
    "readOnly": true,
    "resources": [
        {
            "ARN": "arn:aws:eks:us-west-2:123456789012:cluster/my-cluster",
            "accountId": "111122223333",
            "type": "AWS::EKS::Cluster"
        }
    ],
    "sharedEventID": "shared-event-id",
    "vpcEndpointId": "vpce-endpoint-id"
}
```

This log entry shows an attempt to describe an EKS cluster by the `admin` user.

##### Example Kubernetes Audit Log

```json
{
    "kind": "Event",
    "apiVersion": "audit.k8s.io/v1",
    "level": "Metadata",
    "timestamp": "2023-10-01T12:34:56Z",
    "source": {
        "component": "apiserver"
    },
    "requestURI": "/api/v1/namespaces/default/pods",
    "verb": "get",
    "user": {
        "username": "alice",
        "uid": "alice-uid",
        "groups": [
            "system:authenticated"
        ]
    },
    "impersonator": {},
    "objectRef": {
        "resource": "pods",
        "namespace": "default",
        "name": "",
        "apiVersion": "v1"
    },
    "responseStatus": {
        "metadata": {},
        "code": 200
    },
    "stage": "ResponseComplete",
    "requestReceivedTimestamp": "2023-10-01T12:34:56Z",
    "stageTimestamp": "2023-10-01T12:34:56Z",
    "annotations": {
        "authorization.k8s.io/decision": "allow",
        "authorization.k8s.io/reason": "RBAC: allowed by RoleBinding \"read-pods\" of Role \"pod-reader\" in namespace \"default\"",
        "k8s-audit-allowed": "true"
    }
}
```

This log entry shows a successful GET request to list pods in the `default` namespace by the user `alice`.

#### Prevention

To prevent unauthorized access, you should implement the following measures:

1. **Least Privilege Principle**: Grant users the minimum permissions required to perform their tasks.
2. **Multi-Factor Authentication (MFA)**: Require MFA for all IAM users.
3. **Regular Audits**: Perform regular audits of IAM policies and Kubernetes RBAC rules to ensure they remain secure.
4. **Network Policies**: Implement Kubernetes Network Policies to restrict traffic between pods and external networks.

##### Example Network Policy

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  ingress: []
```

This Network Policy denies all ingress traffic to pods in the namespace.

### Real-World Examples and CVEs

#### Recent Breaches

In 2023, a significant breach occurred at a major financial institution due to misconfigured IAM policies. The breach resulted in unauthorized access to sensitive data stored in EKS clusters. The root cause was identified as overly permissive IAM policies that granted unnecessary permissions to IAM users.

#### Secure Configuration

To avoid such breaches, it is essential to follow secure configuration practices. Here is an example of a secure IAM policy and Kubernetes RBAC setup:

##### Secure IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters",
                "eks:DescribeAddon",
                "eks:ListAddons"
            ],
            "Resource": "arn:aws:eks:us-west-2:123456789012:cluster/my-cluster"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": "arn:aws:iam::*:role/k8s-user-role"
        }
    ]
}
```

This policy grants the user permission to describe and list specific EKS clusters and addons, as well as assume a role that provides limited access to the Kubernetes cluster.

##### Secure Kubernetes RBAC

```yaml
# secure-k8s-rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: restricted-pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: restricted-read-pods
  namespace: default
subjects:
- kind: User
  name: bob # Name is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: restricted-pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This Role and RoleBinding grant the user `bob` restricted permission to read pods in the `default` namespace.

### Hands-On Practice

To gain practical experience with configuring EKS add-ons and managing IAM permissions, you can use the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can be adapted to understand the broader security context of EKS.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice securing Kubernetes environments.
- **CloudGoat**: A series of labs designed to teach cloud security concepts, including IAM and Kubernetes RBAC.

These labs provide a safe environment to experiment with different configurations and security practices.

### Conclusion

Configuring EKS add-ons and managing IAM permissions are critical aspects of securing your Kubernetes clusters on AWS. By following best practices, implementing secure configurations, and regularly auditing your setup, you can significantly reduce the risk of unauthorized access and potential breaches.

---
<!-- nav -->
[[01-Introduction to EKS Blueprints and Add-Ons Part 1|Introduction to EKS Blueprints and Add-Ons Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Configure EKS Add ons/00-Overview|Overview]] | [[03-Introduction to EKS Blueprints and Add-Ons Part 3|Introduction to EKS Blueprints and Add-Ons Part 3]]

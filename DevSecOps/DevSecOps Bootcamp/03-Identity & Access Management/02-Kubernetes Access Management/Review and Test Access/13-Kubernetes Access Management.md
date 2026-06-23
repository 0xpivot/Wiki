---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes cluster. It ensures that only authorized entities can interact with the cluster and perform specific actions. This involves managing identities, roles, and permissions within the cluster, as well as integrating with external identity providers like AWS IAM.

### Understanding Kubernetes Users and Roles

In Kubernetes, users and roles are fundamental concepts used to manage access control. A **user** is an entity that interacts with the cluster, such as a human operator or an automated system. A **role** defines a set of permissions that a user or group can have within the cluster.

#### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within the organization. In Kubernetes, RBAC allows you to define roles and bind them to users or groups. This ensures that users only have the permissions necessary to perform their tasks.

##### Example: Defining a Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This role grants read-only access to pods in the `default` namespace.

##### Example: Binding a Role to a User

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This binding associates the `pod-reader` role with the user `johndoe`.

### Integrating AWS IAM with Kubernetes

AWS Identity and Access Management (IAM) can be integrated with Kubernetes to manage access to the cluster. This integration allows you to use AWS IAM roles to control access to Kubernetes resources.

#### Mapping AWS IAM Roles to Kubernetes Users

To integrate AWS IAM with Kubernetes, you need to map AWS IAM roles to Kubernetes users. This is typically done using a webhook authentication mechanism provided by tools like `aws-iam-authenticator`.

##### Example: Configuring aws-iam-authenticator

First, install the `aws-iam-authenticator` tool:

```sh
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.20.4/2021-04-12/bin/linux/amazon-eks/aws-iam-authenticator
chmod +x ./aws-iam-authenticator
sudo mv ./aws-iam-authenticator /usr/local/bin/
```

Next, configure the authenticator to map AWS IAM roles to Kubernetes users:

```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-iam-authenticator/master/docs/examples/rbac.yaml
```

This sets up the necessary RBAC rules for the authenticator.

### Creating IAM Roles for Kubernetes

In the given transcript, IAM roles (`external admin` and `external developer`) were created using Terraform scripts. These roles are then mapped to Kubernetes users.

#### Example: Terraform Script for IAM Roles

```hcl
resource "aws_iam_role" "kubernetes_admin" {
  name = "kubernetes-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role" "kubernetes_developer" {
  name = "kubernetes-developer"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
```

These roles allow EC2 instances to assume the roles and interact with the Kubernetes cluster.

### Testing Access to the Kubernetes Cluster

Once the roles and mappings are configured, it's essential to test the access to ensure that the permissions work as intended.

#### Example: Testing Access with kubectl

To test access, you can use `kubectl` with the appropriate credentials.

```sh
export AWS_PROFILE=your-profile-name
aws-iam-authenticator token -i your-cluster-name | grep -o '"token": "[^"]*"' | sed 's/"token": "//' | sed 's/"$//'
```

This command retrieves an authentication token for the specified AWS profile and cluster.

Then, configure `kubectl` to use this token:

```sh
kubectl config set-credentials your-user --exec-command="aws-iam-authenticator token -i your-cluster-name"
kubectl config set-context your-context --cluster=your-cluster --user=your-user
kubectl config use-context your-context
```

Finally, test the access:

```sh
kubectl get pods
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Overly Permissive Roles

One common pitfall is creating overly permissive roles that grant more permissions than necessary. This can lead to security vulnerabilities.

##### How to Prevent: Least Privilege Principle

Always follow the least privilege principle. Ensure that roles are defined with the minimum set of permissions required to perform their tasks.

#### Pitfall: Incorrect Role Mappings

Incorrect role mappings can result in unauthorized access to the cluster.

##### How to Prevent: Regular Audits

Regularly audit role mappings and permissions to ensure they align with organizational policies.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows attackers to escalate privileges by manipulating the `extraArgs` field in the API server configuration. This highlights the importance of proper access management and regular security audits.

#### Example: AWS IAM Role Assumption Attack

In 2021, a series of attacks targeted organizations by exploiting misconfigured AWS IAM roles. Attackers were able to assume roles and gain unauthorized access to Kubernetes clusters. This underscores the need for strict role management and regular security assessments.

### Conclusion

Proper Kubernetes access management is crucial for maintaining the security and integrity of your cluster. By integrating AWS IAM with Kubernetes and following best practices, you can ensure that only authorized entities have the necessary permissions to interact with the cluster.

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A security-focused Kubernetes environment designed for learning and testing security configurations.
- **OWASP WrongSecrets**: A series of challenges focused on various aspects of Kubernetes security, including access management.

These labs provide practical experience in configuring and testing access controls in a Kubernetes environment.

### Summary

In summary, Kubernetes access management involves defining roles, mapping AWS IAM roles to Kubernetes users, and testing access to ensure proper permissions. By following best practices and regularly auditing configurations, you can maintain a secure Kubernetes environment.

---
<!-- nav -->
[[12-Kubernetes Access Management Part 9|Kubernetes Access Management Part 9]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/14-Practice Questions & Answers|Practice Questions & Answers]]

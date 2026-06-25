---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Rejecting Privileged Containers

### Background Theory

Policy as Code is a practice where security policies are defined in code, often using declarative languages like YAML or JSON. This approach allows for version control, automated testing, and consistent enforcement across environments. In the context of Kubernetes, policies can be enforced using tools like Open Policy Agent (OPA), Kyverno, or PodSecurityPolicies.

Privileged containers are a powerful feature in Kubernetes that allow containers to have nearly the same capabilities as the host machine. While this can be useful for certain types of applications, such as system monitoring or debugging tools, it also poses significant security risks. A privileged container can potentially bypass many of the security mechanisms designed to protect the host and other containers.

### Why Restrict Privileged Containers?

Restricting privileged containers is crucial for maintaining a secure environment. Here are some reasons why:

1. **Security Risks**: Privileged containers can access the host's filesystem, network interfaces, and other resources, which can lead to unauthorized access and potential attacks.
2. **Compliance**: Many regulatory frameworks require strict controls over privileged access to ensure data protection and compliance.
3. **Least Privilege Principle**: Following the principle of least privilege ensures that containers only have the permissions necessary to perform their intended functions, reducing the attack surface.

### How to Restrict Privileged Containers

To restrict privileged containers, we can define a policy that explicitly denies the creation of privileged pods. This can be done using tools like Kyverno, which provides a declarative way to define and enforce policies.

#### Step-by-Step Mechanics

1. **Define the Constraint Template**:
   - A constraint template defines the structure and logic of the policy.
   - This template is applied first to ensure that the Custom Resource Definition (CRD) is available in the cluster.

2. **Create the Constraint**:
   - Once the template is applied, we can create an instance of the constraint to enforce the policy.

3. **Push Changes to Repository**:
   - After defining the policy, we push the changes to the version control repository.

4. **Sync with Argo CD**:
   - Finally, we sync the changes with Argo CD to apply the policy in the cluster.

### Example Configuration

Let's walk through a complete example of how to define and enforce a policy to reject privileged containers.

#### Constraint Template

First, we define the constraint template using Kyverno. This template will be used to create the actual constraint.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicyTemplate
metadata:
  name: deny-privileged-containers-template
spec:
  validationFailureAction: enforce
  background: false
  rules:
    - name: deny-privileged-containers
      match:
        resources:
          kinds:
            - Pod
      validate:
        message: "Pods cannot be privileged"
        deny:
          conditions:
            - key: spec.containers[*].securityContext.privileged
              operator: Exists
```

This template defines a rule that matches all `Pod` resources and checks if any container within the pod has the `securityContext.privileged` field set to `true`. If such a condition is found, the pod creation is denied.

#### Constraint Instance

Next, we create an instance of the constraint using the template we just defined.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-privileged-containers
spec:
  templateRef:
    name: deny-privileged-containers-template
  background: false
  validationFailureAction: enforce
```

This constraint instance applies the template to the entire cluster, enforcing the policy.

### Pushing Changes to Repository

We now push these changes to our version control repository. Assuming we are using Git, the process would look something like this:

```sh
git add .
git commit -m "Add privileged container restriction policy"
git push origin main
```

### Syncing with Argo CD

Finally, we sync the changes with Argo CD to apply the policy in the cluster.

```sh
argocd app sync <app-name>
```

### Full Example

Here is a complete example of the full process, including the full HTTP request and response, and the expected result.

#### Full HTTP Request

```http
POST /apis/kyverno.io/v1/namespaces/default/clusternetworkpolicies HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "apiVersion": "kyverno.io/v1",
  "kind": "ClusterPolicyTemplate",
  "metadata": {
    "name": "deny-privileged-containers-template"
  },
  "spec": {
    "validationFailureAction": "enforce",
    "background": false,
    "rules": [
      {
        "name": "deny-privileged-containers",
        "match": {
          "resources": {
            "kinds": ["Pod"]
          }
        },
        "validate": {
          "message": "Pods cannot be privileged",
          "deny": {
            "conditions": [
              {
                "key": "spec.containers[*].securityContext.privileged",
                "operator": "Exists"
              }
            ]
          }
        }
      }
    ]
  }
}
```

#### Full HTTP Response

```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: application/json

{
  "kind": "ClusterPolicyTemplate",
  "apiVersion": "kyverno.io/v1",
  "metadata": {
    "name": "deny-privileged-containers-template",
    "namespace": "default",
    "uid": "abcd1234-abcd-1234-abcd-1234abcd1234",
    "resourceVersion": "123456789",
    "creationTimestamp": "2024-01-01T00:00:00Z"
  },
  "spec": {
    "validationFailureAction": "enforce",
    "background": false,
    "rules": [
      {
        "name": "deny-privileged-containers",
        "match": {
          "resources": {
            "kinds": ["Pod"]
          }
        },
        "validate": {
          "message": "Pods cannot be privileged",
          "deny": {
            "conditions": [
              {
                "key": "spec.containers[*].securityContext.privileged",
                "operator": "Exists"
              }
            ]
          }
        }
      }
    ]
  }
}
```

### Expected Result

After syncing with Argo CD, the policy should be applied, and any attempt to create a privileged pod should be denied.

### Pitfalls and Common Mistakes

1. **Incorrect Policy Definition**: Ensure that the policy is correctly defined and matches the desired behavior.
2. **Missing Constraint Template**: Ensure that the constraint template is applied before creating the constraint instance.
3. **Insufficient Permissions**: Ensure that the user or service account has the necessary permissions to create and apply policies.

### Real-World Examples

#### Recent Breaches

In a recent breach involving a Kubernetes cluster, attackers were able to gain elevated privileges by exploiting a misconfigured privileged container. This allowed them to access sensitive data and execute arbitrary commands on the host machine.

#### CVE Example

CVE-2021-25741: This CVE highlights the importance of restricting privileged containers. An attacker could exploit a misconfigured privileged container to gain unauthorized access to the host machine.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Regularly review audit logs to identify any attempts to create privileged containers.
2. **Monitoring Tools**: Use monitoring tools like Prometheus and Grafana to monitor the cluster for suspicious activity.

#### Prevention

1. **Policy Enforcement**: Enforce policies to restrict privileged containers using tools like Kyverno.
2. **Least Privilege Principle**: Follow the principle of least privilege to ensure that containers only have the permissions necessary to perform their intended functions.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
    - name: example-container
      image: example-image
      securityContext:
        privileged: true
```

##### Fixed Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
    - name: example-container
      image: example-image
```

### Configuration Hardening

1. **Network Policies**: Implement network policies to restrict communication between pods.
2. **RBAC**: Use Role-Based Access Control (RBAC) to limit the permissions of users and service accounts.

### Practice Labs

For hands-on experience with Policy as Code and restricting privileged containers, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning and practicing security.

By following these steps and best practices, you can effectively restrict privileged containers and maintain a secure Kubernetes environment.

---
<!-- nav -->
[[02-Policy as Code Rejecting Privileged Containers Part 2|Policy as Code Rejecting Privileged Containers Part 2]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[04-Policy as Code Rejecting Privileged Containers Part 4|Policy as Code Rejecting Privileged Containers Part 4]]

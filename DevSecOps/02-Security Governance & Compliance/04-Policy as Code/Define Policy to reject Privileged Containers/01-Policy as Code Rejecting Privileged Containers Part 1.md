---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Rejecting Privileged Containers

### Introduction to Policy as Code

Policy as Code is a practice where security policies are defined in machine-readable code rather than human-readable documents. This approach allows for automated enforcement and continuous compliance checks within the development lifecycle. In the context of Kubernetes, policies can be defined using tools such as Open Policy Agent (OPA) to enforce security rules across the cluster.

### Understanding Privileged Containers

A privileged container in Kubernetes is one that runs with elevated permissions, similar to the host system. This means the container has access to all devices and capabilities available on the host. While this can be useful for certain types of applications, it poses significant security risks. A privileged container can potentially bypass many security mechanisms and gain unauthorized access to sensitive resources.

#### Why Reject Privileged Containers?

Rejecting privileged containers is crucial for maintaining a secure environment. Here are some reasons why:

1. **Security Risks**: Privileged containers can execute arbitrary code with root privileges, leading to potential security breaches.
2. **Compliance Issues**: Many regulatory frameworks require strict control over privileged access. Allowing privileged containers can lead to non-compliance.
3. **Operational Complexity**: Managing privileged containers increases operational complexity and the likelihood of misconfigurations.

### Defining the Policy

To define a policy that rejects privileged containers, we will use Open Policy Agent (OPA). OPA is a powerful tool for enforcing policies across different systems, including Kubernetes.

#### Step-by-Step Policy Definition

1. **Create a Constraint Template**:
    - A constraint template defines the structure of the policy.
    - We will create a template to check for privileged containers.

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraintTemplate
metadata:
  name: k8s-block-privileged-container
spec:
  crd:
    spec:
      names:
        kind: BlockPrivilegedContainer
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8s.block.privileged.container
        
        violation[{"msg": msg, "details": {"containerName": container.name}}] {
          input.review.object.kind = "Pod"
          container := input.review.object.spec.containers[_]
          container.securityContext != null
          container.securityContext.privileged = true
          msg := sprintf("Container %s is running in privileged mode", [container.name])
        }
```

2. **Create a Constraint**:
    - A constraint applies the policy defined in the template.
    - We will create a constraint to enforce the policy.

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: BlockPrivilegedContainer
metadata:
  name: block-privileged-container
spec:
  match:
    kinds:
      - apiGroups: [""] # Core API group
        kinds: ["Pod"]
```

### Testing the Policy

To test the policy, we will create a sample pod that attempts to run in privileged mode and verify that the policy correctly flags it as a violation.

#### Sample Pod Configuration

Here is a sample pod configuration that attempts to run in privileged mode:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: privileged-container
    image: nginx
    securityContext:
      privileged: true
```

#### Expected Response

When the above pod configuration is applied, the policy should flag it as a violation. The response from the Kubernetes API server would look something like this:

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "admission webhook \"validation.gatekeeper.sh\" denied the request: [BlockPrivilegedContainer]: Container privileged-container is running in privileged mode",
  "reason": "Forbidden",
  "details": {
    "name": "privileged-pod",
    "group": "",
    "kind": "Pod"
  },
  "code": 403
}
```

### How to Prevent / Defend

#### Detection

To detect privileged containers, you can use tools like OPA or other Kubernetes admission controllers. These tools can automatically check for violations and provide detailed reports.

#### Prevention

1. **Secure Coding Practices**:
    - Ensure that developers are aware of the risks associated with privileged containers.
    - Use static analysis tools to identify and flag potential issues in code.

2. **Configuration Hardening**:
    - Implement strict security policies that prohibit the use of privileged containers.
    - Use tools like OPA to enforce these policies.

3. **Monitoring and Logging**:
    - Monitor Kubernetes clusters for any attempts to run privileged containers.
    - Log all violations and investigate them promptly.

#### Secure-Coding Fixes

Here is an example of a vulnerable pod configuration and its secure counterpart:

**Vulnerable Pod Configuration**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: nginx
    securityContext:
      privileged: true
```

**Secure Pod Configuration**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: nginx
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the breach at Capital One in 2019, where an attacker exploited a misconfigured Kubernetes cluster. Although the breach was not directly due to privileged containers, it highlights the importance of strict security policies and the risks associated with misconfigurations.

### Hands-On Labs

For hands-on practice with Policy as Code and rejecting privileged containers, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security, including policy enforcement.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice securing Kubernetes deployments.
- **Kubernetes Goat**: A deliberately insecure Kubernetes cluster designed for security testing and learning.

These labs provide practical experience in defining and enforcing security policies in Kubernetes environments.

### Conclusion

Defining policies to reject privileged containers is a critical step in maintaining a secure Kubernetes environment. By using tools like Open Policy Agent, you can automate the enforcement of these policies and ensure continuous compliance. Understanding the risks and implementing robust detection and prevention strategies are essential for effective security management.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[02-Policy as Code Rejecting Privileged Containers Part 2|Policy as Code Rejecting Privileged Containers Part 2]]

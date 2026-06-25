---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Rejecting Privileged Containers

### Introduction to Policy as Code

Policy as Code is a practice that involves defining infrastructure policies using code, rather than manual configurations. This approach allows for consistent enforcement of security policies across environments, making it easier to manage and audit compliance. In the context of Kubernetes, policy as code can be implemented using tools like Open Policy Agent (OPA) and Kubernetes Admission Controllers.

### Understanding Privileged Containers

Privileged containers are those that run with elevated permissions, essentially giving them access to all devices and capabilities available on the host system. This can pose significant security risks, as a compromised privileged container could potentially gain full control over the underlying host.

#### Why Privileged Containers Are Dangerous

- **Elevated Permissions**: A privileged container has access to all host resources, including hardware devices and kernel modules.
- **Security Risks**: If a malicious actor gains control of a privileged container, they can potentially execute arbitrary code on the host, leading to a full system compromise.
- **Compliance Issues**: Many regulatory frameworks require strict controls over container privileges to ensure that sensitive data and operations are protected.

#### Real-World Example: CVE-2019-14287

CVE-2019-14287 is a vulnerability in Docker that allowed a container to escape its namespace and gain root access to the host system. This was possible due to the use of privileged containers. The vulnerability highlights the importance of properly securing container privileges to prevent such attacks.

### Configuring Pod Security Context

In Kubernetes, the `securityContext` field within a pod specification can be used to define security settings for containers. One of the key attributes within `securityContext` is `privileged`, which determines whether a container runs with elevated permissions.

#### Example Pod Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    securityContext:
      privileged: false
```

In this example, the `privileged` attribute is explicitly set to `false`. This ensures that the container does not run with elevated permissions.

#### Default Behavior

If the `securityContext` block is omitted, Kubernetes defaults to `privileged: false`. This means that containers will not run with elevated permissions unless explicitly configured to do so.

### Implementing Policy to Reject Privileged Containers

To enforce a policy that rejects privileged containers, you can use Kubernetes Admission Controllers. These controllers intercept API requests and can modify or reject them based on predefined rules.

#### Example Constraint Definition

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraint
metadata:
  name: disallow-privileged-containers
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    allowedNamespaces:
    - kube-system
  severity: high
  message: "Privileged containers are not allowed in non-kube-system namespaces."
  remediation:
    action: enforce
  validation:
    path: spec.containers[*].securityContext.privileged
    function: "not"
```

This constraint definition uses Gatekeeper, an open-source policy controller for Kubernetes. The constraint specifies that privileged containers are not allowed in any namespace except `kube-system`.

### Testing the Policy

To test the policy, you can create a pod configuration with a privileged container and observe the behavior.

#### Vulnerable Pod Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: my-image
    securityContext:
      privileged: true
```

When this pod is created, the admission controller will reject it due to the policy constraint.

#### Secure Pod Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: my-image
    securityContext:
      privileged: false
```

This pod configuration adheres to the policy and will be accepted by the admission controller.

### How to Prevent / Defend

#### Detection

To detect violations of the policy, you can use logging and monitoring tools to track API requests and responses. Tools like Fluentd or ELK Stack can be used to collect and analyze logs.

#### Prevention

1. **Use Admission Controllers**: Implement admission controllers like Gatekeeper to enforce policy constraints.
2. **Audit Regularly**: Regularly audit your Kubernetes clusters to ensure compliance with security policies.
3. **Educate Developers**: Educate developers about the risks associated with privileged containers and the importance of following security best practices.

#### Secure Coding Fixes

**Vulnerable Code**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: my-image
    securityContext:
      privileged: true
```

**Secure Code**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: my-image
    securityContext:
      privileged: false
```

### Additional Considerations

#### Namespaces and Constraints

The policy can be configured to apply to specific namespaces. For example, the constraint can be modified to exclude certain namespaces where privileged containers might be necessary.

#### Extra Parameters and Configuration

The constraint definition can include additional parameters to fine-tune the policy. For example, you can specify which namespaces are excluded from the policy.

### Conclusion

Implementing policy as code to reject privileged containers is a critical step in securing Kubernetes environments. By leveraging tools like Gatekeeper and admission controllers, you can enforce strict security policies and prevent potential security risks. Regular auditing and education of developers are also essential to maintaining a secure environment.

### Hands-On Labs

For hands-on practice with policy as code and Kubernetes security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in implementing and testing security policies in real-world scenarios.

---
<!-- nav -->
[[01-Policy as Code Rejecting Privileged Containers Part 1|Policy as Code Rejecting Privileged Containers Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[03-Policy as Code Rejecting Privileged Containers Part 3|Policy as Code Rejecting Privileged Containers Part 3]]

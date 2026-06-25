---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Open Policy Agent (OPA) and OPA Gatekeeper

### Background Theory

Open Policy Agent (OPA) is a powerful, general-purpose policy engine designed to make decisions about what actions should be allowed or denied based on a set of rules defined in a declarative language. OPA can be used across various domains, including infrastructure management, application security, and compliance enforcement. Its primary function is to evaluate policies against data and return a decision (allow/deny).

#### What is OPA?

OPA is built around the Rego programming language, which is specifically designed for writing policies. Rego allows you to define complex logic and constraints in a readable and maintainable way. Policies written in Rego can be applied to any system that can send data to OPA for evaluation.

#### Why Use OPA?

- **Centralized Policy Management**: OPA centralizes policy management, making it easier to enforce consistent rules across different systems.
- **Declarative Policy Language**: Rego enables you to express policies declaratively, which makes them easier to write, read, and maintain.
- **Dynamic Policy Evaluation**: OPA can evaluate policies dynamically at runtime, allowing for real-time decision-making.
- **Extensibility**: OPA can be integrated with various systems and services, making it highly extensible.

### OPA Gatekeeper

OPA Gatekeeper is a Kubernetes-native admission controller that extends the capabilities of OPA to Kubernetes clusters. It leverages OPA's policy engine to enforce custom policies within a Kubernetes environment. This integration allows you to define and enforce policies that govern the behavior of your Kubernetes resources.

#### What is OPA Gatekeeper?

Gatekeeper is an open-source project that integrates OPA with Kubernetes. It acts as an admission webhook, intercepting and evaluating incoming requests to ensure they comply with predefined policies. By doing so, Gatekeeper helps maintain the integrity and security of your Kubernetes cluster.

#### Why Use OPA Gatekeeper?

- **Kubernetes-Native Integration**: Gatekeeper is designed specifically for Kubernetes, making it easy to integrate with existing Kubernetes workflows.
- **Custom Policy Enforcement**: You can define custom policies to enforce specific behaviors or restrictions within your Kubernetes cluster.
- **Dynamic Policy Evaluation**: Gatekeeper evaluates policies dynamically, ensuring that your cluster remains compliant even as new resources are added or modified.
- **Centralized Policy Management**: Gatekeeper allows you to manage policies centrally, making it easier to enforce consistent rules across your entire cluster.

### Key Concepts

#### Admission Controller

An admission controller is a component in Kubernetes that intercepts and evaluates incoming requests before they are processed by the API server. Admission controllers can modify or reject requests based on predefined rules. OPA Gatekeeper acts as an admission controller, evaluating incoming requests against policies defined in OPA.

#### Rego Language

Rego is the declarative policy language used by OPA. It allows you to define policies in a readable and maintainable way. Here is a simple example of a Rego policy:

```rego
package example

default allow = false

allow {
    input.method == "GET"
}
```

This policy allows GET requests but denies all other methods.

### Deployment and Configuration

To deploy and configure OPA Gatekeeper in your Kubernetes cluster, you need to install the Gatekeeper operator and define policies using Custom Resource Definitions (CRDs).

#### Installing Gatekeeper

You can install Gatekeeper using the following Helm chart:

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update
helm install gatekeeper gatekeeper/gatekeeper --namespace gatekeeper-system --create-namespace
```

#### Defining Policies

Policies in Gatekeeper are defined using CRDs. Here is an example of a policy that restricts the creation of pods with privileged containers:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraint
metadata:
  name: pod-no-privileged
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    containerSecurityContext:
      privileged: false
```

This policy ensures that no deployment in the `apps` API group can have a privileged container.

### Real-World Examples

#### Recent CVEs and Breaches

One recent example of a breach that could have been prevented by using OPA Gatekeeper is the Kubernetes API server privilege escalation vulnerability (CVE-2021-25741). This vulnerability allowed attackers to escalate their privileges by manipulating the API server. By enforcing strict policies using OPA Gatekeeper, such vulnerabilities can be mitigated.

### How to Prevent / Defend

#### Detection

To detect policy violations, you can use the `gatekeeper` CLI tool to check the status of your policies:

```bash
kubectl get constrainttemplate
kubectl get constraint
```

These commands will list all the constraint templates and constraints in your cluster, allowing you to verify that your policies are being enforced correctly.

#### Prevention

To prevent policy violations, you need to define and enforce strict policies using OPA Gatekeeper. Here is an example of a policy that restricts the creation of pods with privileged containers:

**Vulnerable Policy:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraint
metadata:
  name: pod-no-privileged
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    containerSecurityContext:
      privileged: true
```

**Secure Policy:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraint
metadata:
  name: pod-no-privileged
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    containerSecurityContext:
      privileged: false
```

By setting `privileged` to `false`, you ensure that no deployment can have a privileged container.

### Complete Example

Here is a complete example of deploying and configuring OPA Gatekeeper in a Kubernetes cluster:

#### Step 1: Install Gatekeeper

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update
helm install gatekeeper gatekeeper/gatekeeper --namespace gatekeeper-system --create-namespace
```

#### Step 2: Define Policies

Create a policy to restrict the creation of pods with privileged containers:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sConstraint
metadata:
  name: pod-no-privileged
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    containerSecurityContext:
      privileged: false
```

Apply the policy:

```bash
kubectl apply -f pod-no-privileged.yaml
```

#### Step 3: Verify Policy Enforcement

Check the status of your policies:

```bash
kubectl get constrainttemplate
kubectl get constraint
```

### Pitfalls and Common Mistakes

#### Overly Permissive Policies

One common mistake is creating overly permissive policies that do not effectively enforce security controls. Always ensure that your policies are strict enough to prevent unauthorized actions.

#### Inconsistent Policy Management

Another pitfall is inconsistent policy management. Ensure that all policies are managed centrally and that changes are propagated consistently across your cluster.

### Hands-On Labs

For hands-on practice with OPA Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: While primarily focused on web security, this platform offers exercises that can help you understand the principles of policy enforcement.
- **OWASP Juice Shop**: This interactive web application includes challenges that can help you practice applying security policies.
- **CloudGoat**: This lab provides a simulated environment for practicing cloud security, including the use of OPA Gatekeeper.

### Conclusion

OPA Gatekeeper is a powerful tool for enforcing policies in a Kubernetes cluster. By leveraging OPA's policy engine, you can define and enforce custom policies that help maintain the integrity and security of your cluster. Understanding the key concepts, deployment steps, and best practices for using OPA Gatekeeper is essential for effective policy management in a Kubernetes environment.

---
<!-- nav -->
[[01-Introduction to Open Policy Agent (OPA) and OPA Gatekeeper Part 1|Introduction to Open Policy Agent (OPA) and OPA Gatekeeper Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Introduction to Open Policy Agent OPA and OPA Gatekeeper/00-Overview|Overview]] | [[03-Introduction to Open Policy Agent (OPA) and OPA Gatekeeper|Introduction to Open Policy Agent (OPA) and OPA Gatekeeper]]

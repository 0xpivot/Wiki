---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure and application policies using declarative code. This method allows organizations to define, version, and enforce policies consistently across their environments. Two popular tools for implementing Policy as Code are Open Policy Agent (OPA) and Gatekeeper. Both tools provide mechanisms to define and enforce policies within Kubernetes clusters, ensuring that resources adhere to organizational standards and security requirements.

### What is Policy as Code?

Policy as Code involves writing policies in a declarative format, typically using YAML or JSON, which can then be enforced programmatically. This approach offers several benefits:

- **Consistency**: Policies are defined once and applied consistently across multiple environments.
- **Version Control**: Policies can be stored in version control systems like Git, enabling tracking of changes and rollbacks.
- **Automation**: Policies can be automatically enforced during deployment processes, reducing human error and improving compliance.

### Why Use Policy as Code?

Using Policy as Code helps organizations maintain consistency and enforce security policies across their infrastructure. It ensures that resources are configured correctly and securely, reducing the risk of misconfigurations and vulnerabilities.

### How Does Policy as Code Work?

In the context of Kubernetes, Policy as Code tools like OPA and Gatekeeper work by defining policies and enforcing them through admission controllers. Admission controllers intercept requests to the Kubernetes API server and apply policies before resources are created or updated.

### Key Concepts

#### Open Policy Agent (OPA)

OPA is a general-purpose policy engine that can be used to enforce policies across various systems, including Kubernetes. OPA provides a declarative language called Rego for defining policies and integrates with Kubernetes through custom resource definitions (CRDs).

#### Gatekeeper

Gatekeeper is a Kubernetes-native policy controller built on top of OPA. It simplifies the process of defining and enforcing policies within Kubernetes clusters. Gatekeeper uses Constraint Templates and Constraints to define and enforce policies.

### Constraint Templates and Constraints

Constraint Templates and Constraints are the core components used by Gatekeeper to define and enforce policies.

#### Constraint Templates

A Constraint Template defines the structure and logic of a policy. It specifies the type of resources that the policy applies to and the conditions that must be met.

#### Constraints

Constraints are instances of Constraint Templates. They specify the specific resources and conditions that should be enforced.

### Predefined Libraries

Both OPA and Gatekeeper come with predefined libraries of constraint templates and constraints. These libraries provide ready-to-use configurations for common policy enforcement scenarios, such as:

- Not allowing privileged containers in the cluster.
- Not allowing NodePort services in the cluster.
- Enforcing resource limits on containers.
- Enforcing certain annotations on components.
- Enforcing labels on components.

### Example: Predefined Constraint Templates

Let's look at some predefined constraint templates provided by Gatekeeper:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        
        violation[{"msg": msg, "details": {}}] {
          provided := [label | input.review.object.metadata.labels[label]]
          required := {"app", "version"}
          missing := required - provided
          msg := sprintf("missing labels: %v", [missing])
        }
```

This constraint template enforces that all resources must have `app` and ` `version` labels.

### Deploying Gatekeeper

To deploy Gatekeeper in a Kubernetes cluster, you can use the following steps:

1. **Install Gatekeeper**:
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
   ```

2. **Verify Installation**:
   ```sh
   kubectl get pods -n gatekeeper-system
   ```

### Creating Policies

Once Gatekeeper is installed, you can create policies using Constraint Templates and Constraints.

#### Example: Enforcing Resource Limits

Let's create a policy to enforce resource limits on containers.

1. **Define Constraint Template**:
   ```yaml
   apiVersion: templates.gatekeeper.sh/v1
   kind: ConstraintTemplate
   metadata:
     name: k8srequiredresourcelimits
   spec:
     crd:
       spec:
         names:
           kind: K8sRequiredResourceLimits
     targets:
       - target: admission.k8s.gatekeeper.sh
         rego: |
           package k8srequiredresourcelimits

           violation[{"msg": msg, "details": {}}] {
             container := input.review.object.spec.containers[_]
             not container.resources.limits.memory
             not container.resources.limits.cpu
             msg := sprintf("container %v is missing resource limits", [container.name])
           }
   ```

2. **Create Constraint**:
   ```yaml
   apiVersion: constraints.gatekeeper.sh/v1
   kind: K8sRequiredResourceLimits
   metadata:
     name: require-resource-limits
   spec:
     match:
       kinds:
         - apiGroups: ["apps"]
           kinds: ["Deployment"]
   ```

### Full Example: HTTP Request and Response

Here is a complete example of creating a policy and verifying its enforcement:

#### Create Constraint Template
```sh
kubectl apply -f k8srequiredresourcelimits_template.yaml
```

#### Create Constraint
```sh
kubectl apply -f require-resource-limits_constraint.yaml
```

#### Verify Enforcement
```sh
kubectl get pods -n gatekeeper-system
```

### Real-World Examples

#### CVE-2021-25741: Kubernetes Privilege Escalation

CVE-2021-25741 is a privilege escalation vulnerability in Kubernetes. By using a policy to disallow privileged containers, organizations can mitigate this risk.

#### Example Policy to Disallow Privileged Containers
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowprivilegedcontainers
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowPrivilegedContainers
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdisallowprivilegedcontainers

        violation[{"msg": msg, "details": {}}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged
          msg := sprintf("container %v is set to privileged", [container.name])
        }
```

#### Create Constraint
```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sDisallowPrivilegedContainers
metadata:
  name: disallow-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
```

### How to Prevent / Defend

#### Detection
Use tools like `kubectl` to verify that policies are being enforced correctly.

#### Prevention
Ensure that all policies are defined and enforced using Constraint Templates and Constraints.

#### Secure Coding Fixes
Compare vulnerable and secure versions of policies to ensure compliance.

#### Hardening
Regularly review and update policies to address new vulnerabilities and threats.

### Conclusion

Policy as Code is a powerful approach to managing infrastructure and application policies. Tools like OPA and Gatekeeper provide robust mechanisms for defining and enforcing policies within Kubernetes clusters. By leveraging predefined constraint templates and constraints, organizations can ensure that their resources are configured correctly and securely.

### Practice Labs

For hands-on practice with Policy as Code, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on securing Kubernetes deployments.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and policy enforcement.
- **CloudGoat**: Provides scenarios for practicing cloud security, including Kubernetes policy enforcement.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on policy as code.

By following these guidelines and practicing with real-world examples, you can master the art of Policy as Code and ensure your Kubernetes clusters are secure and compliant.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/How Gatekeeper and OPA works/01-Introduction to Policy as Code Part 1|Introduction to Policy as Code Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/How Gatekeeper and OPA works/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/How Gatekeeper and OPA works/03-Introduction to Policy as Code|Introduction to Policy as Code]]

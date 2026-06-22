---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is a practice that involves defining infrastructure policies using code, which can then be version-controlled, tested, and deployed alongside the rest of your infrastructure. This approach is particularly useful in DevSecOps environments where maintaining consistent security policies across multiple systems is critical. In this chapter, we will delve into the specifics of defining policies using the Open Policy Agent (OPA) and Gatekeeper, focusing on how to structure these policies within a Kubernetes environment.

### What is Open Policy Agent (OPA)?

Open Policy Agent (OPA) is an open-source project that provides a general-purpose policy engine. OPA allows you to define, enforce, and explain policies across various systems and services. It is designed to be language-agnostic and can be used with any system that can make HTTP requests.

#### Why Use OPA?

1. **Centralized Policy Management**: OPA centralizes policy management, making it easier to maintain and update policies.
2. **Consistency**: By defining policies in code, you ensure consistency across different environments and systems.
3. **Version Control**: Policies can be version-controlled, allowing you to track changes and roll back if necessary.
4. **Explainability**: OPA provides detailed explanations for policy decisions, helping you debug and understand policy behavior.

### What is Gatekeeper?

Gatekeeper is a Kubernetes-native policy controller built on top of OPA. It integrates seamlessly with Kubernetes and allows you to define and enforce policies at the cluster level. Gatekeeper uses Constraint Templates and Constraints to define and enforce policies.

#### Why Use Gatekeeper?

1. **Kubernetes Integration**: Gatekeeper is specifically designed for Kubernetes, making it easier to manage policies within a Kubernetes environment.
2. **Predefined Policies**: Gatekeeper comes with a library of predefined policies, which can be easily adopted and customized.
3. **Constraint Templates**: Constraint Templates allow you to define reusable policy templates, reducing the effort required to define new policies.

### Organizing Kubernetes Files

To effectively manage policies within a Kubernetes environment, it is essential to organize your files in a structured manner. This organization helps in maintaining clarity and ease of management.

#### Directory Structure

Let's consider the directory structure for our Kubernetes platform:

```markdown
platform/
├── admin/
│   ├── open-policy-agent/
│   │   ├── constraint-templates/
│   │   └── constraints/
│   ├── secrets-management/
│   └── eco/
└── services/
    ├── service1/
    ├── service2/
    └── service3/
```

In this structure:
- `admin` contains administrative policies.
- `open-policy-agent` contains OPA-related configurations.
- `constraint-templates` and `constraints` contain the respective policy definitions.
- `secrets-management` and `eco` contain other administrative policies.
- `services` contains individual service directories.

### Creating Constraint Templates

Constraint Templates are reusable policy templates that define the structure of a policy. They are defined using the `ConstraintTemplate` custom resource definition (CRD).

#### Example Constraint Template

Here is an example of a Constraint Template that enforces setting limits on containers:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlimits
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLimits
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlimits
        
        violation[{"msg": msg, "resource": {"apiVersion": input.apiVersion, "kind": input.kind, "name": input.metadata.name}}] {
          container := input.spec.template.spec.containers[_]
          not container.resources.limits.memory
          msg = sprintf("%v memory limit is required", [container.name])
        }
        
        violation[{"msg": msg, "resource": {"apiVersion": input.apiVersion, "kind": input.kind, "name": input.metadata.name}}] {
          container := input.spec.template.spec.containers[_]
          not container.resources.limits.cpu
          msg = sprintf("%v cpu limit is required", [container.name])
        }
```

This template ensures that all containers have both memory and CPU limits set.

### Creating Constraints

Constraints are specific instances of Constraint Templates that define the actual policy. They are defined using the `Constraint` custom resource definition (CRD).

#### Example Constraint

Here is an example of a Constraint that uses the `k8srequiredlimits` template:

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sRequiredLimits
metadata:
  name: k8srequiredlimits
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
```

This constraint ensures that all deployments have their containers with memory and CPU limits set.

### Deploying Constraint Templates and Constraints

To deploy the Constraint Template and Constraint, you can use `kubectl`:

```sh
kubectl apply -f constraint-template.yaml
kubectl apply -f constraint.yaml
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the Kubernetes API server vulnerability (CVE-2021-25740), where an attacker could bypass authentication and authorization checks. Using Gatekeeper, you can enforce strict RBAC policies to mitigate such vulnerabilities.

#### Example Policy for RBAC

Here is an example of a Constraint Template and Constraint that enforces strict RBAC policies:

**Constraint Template:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srbacpolicy
spec:
  crd:
    spec:
      names:
        kind: K8sRBACPolicy
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srbacpolicy
        
        violation[{"msg": msg, "resource": {"apiVersion": input.apiVersion, "kind": input.kind, "name": input.metadata.name}}] {
          not input.spec.rules[_].verbs[_]
          msg = "At least one verb must be specified"
        }
        
        violation[{"msg": msg, "resource": {"apiVersion": input.apiVersion, "kind": input.kind, "name": input.metadata.name}}] {
          not input.spec.rules[_].resources[_]
          msg = "At least one resource must be specified"
        }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sRBACPolicy
metadata:
  name: k8srbacpolicy
spec:
  match:
    kinds:
      - apiGroups: ["rbac.authorization.k8s.io"]
        kinds: ["Role", "ClusterRole"]
```

### How to Prevent / Defend

#### Detection

To detect policy violations, you can use Gatekeeper's audit functionality. This allows you to check existing resources against your policies.

```sh
kubectl get k8srequiredlimits -o json | jq '.status.audit'
```

#### Prevention

To prevent policy violations, ensure that all new resources are validated against your policies during admission control.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a policy:

**Vulnerable Version:**

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

**Secure Version:**

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
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
```

### Hardening

Ensure that your policies are comprehensive and cover all necessary aspects. Regularly review and update your policies to address new threats and vulnerabilities.

### Conclusion

By using Policy as Code with OPA and Gatekeeper, you can effectively manage and enforce policies within a Kubernetes environment. This approach ensures consistency, version control, and centralized management of policies, making it an essential practice in DevSecOps.

### Practice Labs

For hands-on experience with Policy as Code, consider the following labs:
- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on securing APIs and microservices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in applying security policies and practices in a controlled environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Defining Policies/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Defining Policies/02-Policy as Code Defining Policies Using Labels and Annotations|Policy as Code Defining Policies Using Labels and Annotations]]

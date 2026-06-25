---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

### What is Policy as Code?

Policy as Code is a practice that involves defining, managing, and enforcing policies using code. This approach allows organizations to automate the enforcement of compliance rules, security policies, and operational guidelines within their systems. By treating policies as code, teams can leverage version control, continuous integration, and continuous delivery (CI/CD) pipelines to ensure that policies are consistently applied across environments.

### Why Policy as Code Matters

In modern DevOps environments, manual enforcement of policies is impractical due to the scale and complexity of systems. Policy as Code enables teams to:

- **Automate Enforcement**: Policies can be automatically enforced during deployment and runtime.
- **Version Control**: Policies can be versioned alongside application code, ensuring traceability and consistency.
- **Continuous Integration**: Policies can be tested and validated as part of the CI/CD pipeline.
- **Consistency**: Ensures that policies are uniformly applied across different environments and teams.

### How Policy as Code Works

Policy as Code typically involves the following steps:

1. **Define Policies**: Write policies using a declarative language.
2. **Integrate with Systems**: Integrate policies with the target system (e.g., Kubernetes, cloud infrastructure).
3. **Enforce Policies**: Automatically enforce policies during deployment and runtime.
4. **Monitor Compliance**: Continuously monitor and report on compliance status.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of Policy as Code:

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed unauthorized access to sensitive resources. Policy as Code could have prevented this by enforcing strict access controls.
- **SolarWinds Supply Chain Attack**: This attack exploited weak security policies. Policy as Code could have enforced stricter validation and monitoring of supply chain components.

### Tools for Policy as Code

Two popular tools for implementing Policy as Code are Open Policy Agent (OPA) and OPA Gatekeeper.

#### Open Policy Agent (OPA)

OPA is a general-purpose policy engine that can be used to enforce policies in various systems, including Kubernetes, cloud infrastructure, and APIs.

##### What is OPA?

OPA is a policy engine that allows you to define, serve, and enforce policies as code. It provides a declarative language called Rego for writing policies and integrates with systems through APIs.

##### Why Use OPA?

- **General-Purpose**: Can be used in various systems beyond Kubernetes.
- **Declarative Language**: Rego is easy to read and write.
- **Integration**: Integrates with systems through APIs, making it versatile.

##### How OPA Works

OPA works by:

1. **Defining Policies**: Writing policies in Rego.
2. **Serving Policies**: Running OPA as a service to evaluate policies.
3. **Enforcing Policies**: Integrating OPA with systems to enforce policies.

##### Example: Defining a Policy in Rego

```rego
package kubernetes.pods

default allow = false

allow {
    input.kind == "Pod"
    input.metadata.namespace == "application"
    input.spec.replicas <= 10
}
```

This policy ensures that pods in the `application` namespace cannot have more than 10 replicas.

##### Example: Serving Policies with OPA

To serve policies with OPA, you need to run OPA as a service and configure it to evaluate policies.

```bash
opa run --server --listen 0.0.0.0:8181
```

##### Example: Enforcing Policies with OPA

To enforce policies with OPA, you need to integrate OPA with your system. For example, in Kubernetes, you can use OPA as a webhook to validate pod specifications.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: opa-webhook
webhooks:
- name: opa.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
  clientConfig:
    service:
      name: opa-service
      namespace: opa-namespace
      path: /v1/data/kubernetes/pods/allow
```

##### How to Prevent / Defend

**Detection**: Monitor OPA logs and alerts for policy violations.

**Prevention**: Ensure that all policies are correctly defined and integrated with systems.

**Secure-Coding Fix**: Compare vulnerable and secure versions of policies.

**Vulnerable Version**:
```rego
package kubernetes.pods

default allow = true
```

**Secure Version**:
```rego
package kubernetes.pods

default allow = false

allow {
    input.kind == "Pod"
    input.metadata.namespace == "application"
    input.spec.replicas <= 10
}
```

#### OPA Gatekeeper

OPA Gatekeeper is a Kubernetes-native policy controller built on top of OPA. It extends OPA's capabilities specifically for Kubernetes.

##### What is OPA Gatekeeper?

OPA Gatekeeper is a policy controller for Kubernetes that uses OPA to enforce policies. It provides a set of pre-defined policies and allows users to define custom policies.

##### Why Use OPA Gatekeeper?

- **Kubernetes-Native**: Specifically designed for Kubernetes.
- **Pre-Defined Policies**: Comes with a set of pre-defined policies for common use cases.
- **Custom Policies**: Allows users to define custom policies using Rego.

##### How OPA Gatekeeper Works

OPA Gatekeeper works by:

1. **Defining Policies**: Writing policies in Rego.
2. **Deploying Policies**: Deploying policies as Custom Resource Definitions (CRDs).
3. **Enforcing Policies**: Using OPA to evaluate policies and enforce them during deployment.

##### Example: Defining a Policy in Rego

```rego
package kubernetes.pods

default allow = false

allow {
    input.kind == "Pod"
    input.metadata.namespace == "application"
    input.spec.replicas <= 10
}
```

##### Example: Deploying Policies with OPA Gatekeeper

To deploy policies with OPA Gatekeeper, you need to define policies as CRDs and deploy them to your Kubernetes cluster.

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8s-pod-replicas
spec:
  crd:
    spec:
      names:
        kind: PodReplicas
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package kubernetes.pods

        default allow = false

        allow {
            input.kind == "Pod"
            input.metadata.namespace == "application"
            input.spec.replicas <= 10
        }
```

##### Example: Enforcing Policies with OPA Gatekeeper

To enforce policies with OPA Gatekeeper, you need to deploy the policies and configure OPA Gatekeeper to evaluate them.

```bash
kubectl apply -f pod-replicas-template.yaml
kubectl apply -f pod-replicas-constraint.yaml
```

##### How to Prevent / Defend

**Detection**: Monitor OPA Gatekeeper logs and alerts for policy violations.

**Prevention**: Ensure that all policies are correctly defined and deployed.

**Secure-Coding Fix**: Compare vulnerable and secure versions of policies.

**Vulnerable Version**:
```rego
package kubernetes.pods

default allow = true
```

**Secure Version**:
```rego
package kubernetes.pods

default allow = false

allow {
    input.kind == "Pod"
    input.metadata.namespace == "application"
    input.spec.replicas <= 10
}
```

### Comparison Between OPA and OPA Gatekeeper

While both OPA and OPA Gatekeeper serve similar purposes, they have some key differences:

- **General-Purpose vs. Kubernetes-Native**: OPA is a general-purpose policy engine, while OPA Gatekeeper is specifically designed for Kubernetes.
- **Pre-Defined Policies**: OPA Gatekeeper comes with a set of pre-defined policies, whereas OPA requires users to define all policies themselves.
- **Ease of Use**: OPA Gatekeeper is easier to use for Kubernetes-specific policies, while OPA offers more flexibility for general-purpose use cases.

### Conclusion

Policy as Code is a critical practice for modern DevOps environments. Tools like OPA and OPA Gatekeeper enable teams to automate the enforcement of policies, ensuring consistency and compliance across systems. By leveraging these tools, organizations can improve security, reduce manual overhead, and maintain high standards of operational excellence.

### Practice Labs

For hands-on experience with Policy as Code using OPA and OPA Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: Offers labs on web application security, including policy enforcement.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security policies.
- **CloudGoat**: Focuses on cloud security and includes labs on policy enforcement in cloud environments.
- **Pacu**: Offers labs on AWS security, including policy enforcement using OPA and OPA Gatekeeper.

These labs provide practical experience in implementing and enforcing policies using OPA and OPA Gatekeeper, helping you master the concepts covered in this chapter.

---
<!-- nav -->
[[03-Introduction to Open Policy Agent (OPA) and OPA Gatekeeper|Introduction to Open Policy Agent (OPA) and OPA Gatekeeper]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Introduction to Open Policy Agent OPA and OPA Gatekeeper/00-Overview|Overview]] | [[05-Introduction to Policy as Code|Introduction to Policy as Code]]

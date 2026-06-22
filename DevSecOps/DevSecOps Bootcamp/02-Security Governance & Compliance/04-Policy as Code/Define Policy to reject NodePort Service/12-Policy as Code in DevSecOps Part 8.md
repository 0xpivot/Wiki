---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure and application policies using code repositories and automated tools. This method ensures that policies are version-controlled, auditable, and enforceable across environments. In the context of Kubernetes, Policy as Code can be implemented using tools like Open Policy Agent (OPA) and Gatekeeper, which allow administrators to define and enforce policies declaratively.

### Background Theory

#### What is Policy as Code?

Policy as Code involves defining and enforcing policies using code rather than manual processes. This approach leverages the benefits of version control systems, continuous integration/continuous delivery (CI/CD) pipelines, and automated testing to ensure that policies are consistently applied and enforced.

#### Why Use Policy as Code?

- **Version Control**: Policies are stored in version control systems, allowing for tracking changes and rollbacks.
- **Automation**: Automated tools can enforce policies across multiple environments, reducing human error.
- **Auditability**: Version-controlled policies provide a clear audit trail of changes and enforcement actions.
- **Consistency**: Policies are applied uniformly across all environments, ensuring consistency.

### Implementing Policy as Code in Kubernetes

#### Tools and Components

- **Gatekeeper**: A Kubernetes admission controller that enforces custom policies.
- **Argo CD**: A declarative, continuous delivery tool for Kubernetes applications.
- **Open Policy Agent (OPA)**: A policy engine that integrates with various systems, including Kubernetes.

#### Example Scenario: Rejecting NodePort Services

In this scenario, we want to enforce a policy that rejects the creation of `NodePort` services in a Kubernetes cluster. This can be achieved using Gatekeeper and Argo CD.

### Step-by-Step Implementation

#### Step 1: Define the Policy

First, we need to define the policy that will reject `NodePort` services. This can be done using a Constraint Template and a Constraint in Gatekeeper.

```yaml
# constraint-template.yaml
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

        violation[{"msg": msg, "details": {"kind": input.request.object.kind, "name": input.request.object.metadata.name}}] {
          input.review.operation == "CREATE"
          input.request.object.kind == "Service"
          input.request.object.spec.type == "NodePort"
          msg = sprintf("%v %v is not allowed to be created", [input.request.object.kind, input.request.object.metadata.name])
        }
```

```yaml
# constraint.yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: deny-nodeport-services
spec:
  match:
    kinds:
      - apiGroups: [""] # "" refers to the core API group
        kinds: ["Service"]
```

#### Step 2: Apply the Policy

Next, we apply the policy definition to the Kubernetes cluster using `kubectl`.

```bash
kubectl apply -f constraint-template.yaml
kubectl apply -f constraint.yaml
```

#### Step 3: Integrate with Argo CD

To integrate this policy with Argo CD, we need to configure Argo CD to sync the policy definitions from a Git repository.

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: gatekeeper-policy
spec:
  project: default
  source:
    repoURL: https://github.com/example/gatekeeper-policies.git
    targetRevision: HEAD
    path: .
  destination:
    server: https://kubernetes.default.svc
    namespace: gatekeeper-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply the Argo CD application configuration:

```bash
kubectl apply -f argocd-application.yaml
```

### Testing the Policy

#### Step 1: Create a NodePort Service

Let's attempt to create a `NodePort` service to test the policy.

```yaml
# nodeport-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: NodePort
  selector:
    app: example
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

Apply the service definition:

```bash
kubectl apply -f nodeport-service.yaml
```

#### Step 2: Observe the Result

If the policy is correctly enforced, the `NodePort` service should be rejected.

```plaintext
Error from server (Forbidden): error when creating "nodeport-service.yaml": admission webhook "validation.gatekeeper.sh" denied the request: [denied by deny-nodeport-services] Service example-service is not allowed to be created
```

### Visualization and Error Handling

Argo CD provides a visual interface to monitor the sync status and errors.

```plaintext
Sync Status: Failed
Error: [denied by deny-nodeport-services] Service example-service is not allowed to be created
```

Clicking on the error message provides more details about the rejection.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Ensure that logs from Gatekeeper and Argo CD are monitored for policy violations.
- **Alerting**: Set up alerts for policy violations to notify administrators promptly.

#### Prevention

- **Secure Coding Practices**: Ensure that developers are aware of the policies and follow them.
- **Automated Testing**: Include policy checks in CI/CD pipelines to catch violations early.

#### Secure-Coding Fixes

**Vulnerable Code**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: NodePort
  selector:
    app: example
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

**Fixed Code**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: ClusterIP
  selector:
    app: example
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

### Real-World Examples

#### Recent Breaches

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed unauthorized access to `NodePort` services. Ensuring that `NodePort` services are restricted can help mitigate such risks.

### Conclusion

Implementing Policy as Code in Kubernetes using tools like Gatekeeper and Argo CD provides a robust framework for enforcing and monitoring policies. By following the steps outlined above, you can ensure that your Kubernetes cluster adheres to strict security policies, reducing the risk of unauthorized access and vulnerabilities.

### Practice Labs

For hands-on practice with Policy as Code in Kubernetes, consider the following labs:

- **Kubernetes Goat**: A Kubernetes-based security training platform.
- **OWASP WrongSecrets**: A series of challenges focused on Kubernetes security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

These labs provide practical experience in implementing and enforcing policies in a Kubernetes environment.

---
<!-- nav -->
[[11-Policy as Code in DevSecOps Part 7|Policy as Code in DevSecOps Part 7]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[13-Policy as Code in DevSecOps Part 9|Policy as Code in DevSecOps Part 9]]

---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the Open Policy Agent (OPA) Gatekeeper in a Kubernetes cluster.**

The Open Policy Agent (OPA) Gatekeeper is a policy controller for Kubernetes that enforces custom policies on the cluster. It provides a framework to define and enforce policies using Constraint Templates and Constraints, ensuring that Kubernetes manifests adhere to organizational policies before being deployed. This helps maintain compliance and security by preventing unauthorized configurations or deployments.

**Q2. How do you deploy the OPA Gatekeeper controller in a Kubernetes cluster using Terraform?**

To deploy the OPA Gatekeeper controller in a Kubernetes cluster using Terraform, follow these steps:

1. Create a new Terraform file, e.g., `gatekeeper.tf`.
2. Define the Helm chart for the Open Policy Agent Gatekeeper in the Terraform file.
3. Specify the repository address, chart name, and namespace where the controller will run.
4. Ensure dependencies are correctly managed, particularly for deletion order to avoid errors.
5. Apply the Terraform configuration to deploy the Gatekeeper controller.

Here’s an example Terraform snippet:

```hcl
resource "helm_release" "gatekeeper" {
  name       = "open-policy-agent"
  repository = "https://open-policy-agent.github.io/gatekeeper/charts"
  chart      = "gatekeeper"
  namespace  = "open-policy-agent"

  set {
    name  = "gatekeeper.namespace"
    value = "open-policy-agent"
  }
}
```

**Q3. Why is it necessary to increase the instance type for the managed node group in an EKS cluster when deploying the Gatekeeper controller?**

Increasing the instance type for the managed node group in an EKS cluster is necessary because the default instance type (e.g., `t3.micro`) may not provide sufficient resources to run the Gatekeeper controller and other components effectively. Larger instance types (e.g., `t3.small` or `t3.medium`) ensure that the nodes have enough CPU and memory to handle the additional load introduced by the Gatekeeper controller and other services like secrets management or ArgoCD.

**Q4. What are the key components deployed when the Gatekeeper controller is installed in a Kubernetes cluster?**

When the Gatekeeper controller is installed in a Kubernetes cluster, the following key components are typically deployed:

1. **Gatekeeper Controller Pods**: These are the main components responsible for enforcing policies.
2. **Gatekeeper Audit Pod**: This pod performs periodic audits to ensure compliance with policies.
3. **Webhook Service**: This service intercepts requests to the Kubernetes API server to validate Kubernetes manifests against defined policies.
4. **Custom Resource Definitions (CRDs)**: These CRDs allow the definition of policies and constraints using Constraint Templates and Constraints.

**Q5. How do you grant the necessary permissions to list all CRDs in a Kubernetes cluster?**

To grant the necessary permissions to list all CRDs in a Kubernetes cluster, you need to update the role bindings or RBAC roles. Here’s an example of how to add the required permissions using a Kubernetes Role and RoleBinding:

1. Define a Role with the necessary permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: kube-system
  name: crd-reader
rules:
- apiGroups: ["*"]
  resources: ["customresourcedefinitions"]
  verbs: ["get", "list", "watch"]
```

2. Bind the Role to a user or service account:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: crd-reader-binding
  namespace: kube-system
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: Role
  name: crd-reader
  apiGroup: rbac.authorization.k8s.io
```

Apply these definitions using `kubectl apply -f <filename>.yaml`.

**Q6. What are Constraint Templates and Constraints in the context of OPA Gatekeeper?**

In the context of OPA Gatekeeper, Constraint Templates and Constraints are used to define and enforce policies:

1. **Constraint Templates**: These are reusable templates that define the structure and logic of policies. They specify the conditions under which a resource is considered compliant or non-compliant.
   
   Example:
   ```yaml
   apiVersion: templates.gatekeeper.sh/v1
   kind: ConstraintTemplate
   metadata:
     name: k8sgenericrequiredlabels
   spec:
     crd:
       spec:
         names:
           kind: K8sGenericRequiredLabels
     targets:
     - target: admission.k8s.gatekeeper.sh
       rego: |
         package k8sgenericrequiredlabels
         
         violation[{"msg": msg, "reason": reason}] {
           provided := [label | input.review.object.metadata.labels[label]]
           required := {label | label := input.parameters.required_labels[_]}
           missing := [label | label := required[_]; not provided[label]]
           
           count(missing) > 0
           msg := sprintf("%v labels are missing: %v.", [input.constraint.metadata.name, missing])
           reason := "missingLabel"
         }
   ```

2. **Constraints**: These are specific instances of Constraint Templates applied to particular resources. They enforce the policies defined by the templates.

   Example:
   ```yaml
   apiVersion: constraints.gatekeeper.sh/v1beta1
   kind: K8sGenericRequiredLabels
   metadata:
     name: k8s-namespace-required-labels
   spec:
     match:
       kinds:
       - apiGroups: [""]
         kinds: ["Namespace"]
     parameters:
       required_labels:
       - "owner"
       - "environment"
   ```

These components together enable the enforcement of custom policies across the Kubernetes cluster.

---
<!-- nav -->
[[06-Policy as Code with OPA Gatekeeper|Policy as Code with OPA Gatekeeper]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/00-Overview|Overview]]

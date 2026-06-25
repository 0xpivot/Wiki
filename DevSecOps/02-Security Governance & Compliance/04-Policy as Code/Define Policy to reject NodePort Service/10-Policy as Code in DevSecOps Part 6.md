---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure and application policies using code, rather than manual configurations. This method allows organizations to enforce consistent security policies across their environments, ensuring compliance and reducing human error. In the context of Kubernetes, policies can be defined using tools like Open Policy Agent (OPA) and Gatekeeper, which allow you to define and enforce constraints on your cluster.

### Constraint Templates and Constraints in Gatekeeper

Gatekeeper is a Kubernetes admission controller that uses OPA to enforce policies. Policies are defined using two main components: **Constraint Templates** and **Constraints**.

#### Constraint Templates

A Constraint Template defines the structure of a constraint. It specifies the kind of resources it applies to and the logic used to evaluate those resources. Constraint Templates are reusable and can be shared across different constraints.

Here’s an example of a Constraint Template:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sblocknodeport
spec:
  crd:
    spec:
      names:
        kind: K8sBlockNodePort
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sblocknodeport
        
        violation[{"msg": msg, "resource": {"apiVersion": input.apiVersion, "kind": input.kind, "name": input.metadata.name}}] {
          input.kind == "Service"
          input.spec.type == "NodePort"
          msg = sprintf("%v/%v is of type NodePort", [input.metadata.namespace, input.metadata.name])
        }
```

This template defines a constraint that will block `Service` objects of type `NodePort`.

#### Constraints

A Constraint is an instance of a Constraint Template applied to specific resources. It references the Constraint Template and provides additional parameters if needed.

Here’s an example of a Constraint:

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sBlockNodePort
metadata:
  name: deny-nodeport-services
spec:
  match:
    kinds:
      - apiGroups: [""] # "" refers to the core API group
        kinds: ["Service"]
```

This constraint enforces the policy defined by the `k8sblocknodeport` template.

### Deploying Constraint Templates and Constraints

To deploy these policies in a Kubernetes cluster, you need to apply the YAML files to the cluster. Here’s how you can do it:

1. **Apply the Constraint Template:**

   ```bash
   kubectl apply -f constraint-template.yaml
   ```

2. **Apply the Constraint:**

   ```bash
   kubectl apply -f constraint.yaml
   ```

### Understanding the Race Condition

When deploying Constraint Templates and Constraints, there is a potential race condition. The Constraint Template must be deployed first to create the Custom Resource Definition (CRD) in the cluster. Only after the CRD is created can the Constraint be deployed.

#### Why the Race Condition Occurs

- **CRD Creation:** When a Constraint Template is applied, it creates a CRD in the cluster. This CRD defines the structure of the Constraint resource.
- **Constraint Deployment:** The Constraint resource cannot be created until the corresponding CRD exists in the cluster.

#### Example of the Race Condition

Let’s consider the following scenario:

1. You try to apply the Constraint first:

   ```bash
   kubectl apply -f constraint.yaml
   ```

   This will fail because the CRD for `K8sBlockNodePort` does not exist yet.

2. You then apply the Constraint Template:

   ```bash
   kubectl apply -f constraint-template.yaml
   ```

   This creates the CRD in the cluster.

3. Finally, you reapply the Constraint:

   ```bash
   kubectl apply -f constraint.yaml
   ```

   This succeeds because the CRD now exists.

### How to Prevent / Defend

To avoid the race condition and ensure that your policies are correctly enforced, follow these steps:

1. **Always Apply Constraint Templates First:**
   
   Ensure that the Constraint Template is applied before the Constraint. This guarantees that the CRD is created before any constraints are attempted to be applied.

2. **Use a Script to Automate Deployment:**

   Create a script that deploys the Constraint Template and then the Constraint. This ensures that the deployment order is maintained.

   ```bash
   #!/bin/bash
   
   kubectl apply -f constraint-template.yaml
   kubectl apply -f constraint.yaml
   ```

3. **Check for CRD Existence Before Applying Constraints:**

   Before applying a Constraint, check if the corresponding CRD exists in the cluster.

   ```bash
   kubectl get crd | grep k8sblocknodeport
   if [ $? -eq 0 ]; then
     kubectl apply -f constraint.yaml
   else
     echo "CRD does not exist. Please apply the constraint template first."
   fi
   ```

### Real-World Examples

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to bypass certain admission controllers. By enforcing strict policies using Gatekeeper, you can mitigate such vulnerabilities.

- **Vulnerable Configuration:**

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: vulnerable-service
  spec:
    type: NodePort
    ports:
      - port: 80
        targetPort: 8080
  ```

- **Secure Configuration:**

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: secure-service
  spec:
    type: ClusterIP
    ports:
      - port: 80
        targetPort: 8080
  ```

By enforcing the `K8sBlockNodePort` constraint, you can prevent the creation of services with `type: NodePort`, thus mitigating the risk associated with CVE-2021-25741.

### Hands-On Practice

For hands-on practice with Policy as Code in Kubernetes, you can use the following labs:

- **PortSwigger Web Security Academy:** While primarily focused on web security, this platform offers exercises that can help you understand the principles of Policy as Code in a broader context.
- **OWASP Juice Shop:** This interactive web application includes various security challenges that can help you understand how to enforce policies in a real-world environment.
- **DVWA (Damn Vulnerable Web Application):** Similar to OWASP Juice Shop, DVWA offers a range of security challenges that can help you understand the importance of enforcing policies.

### Conclusion

Policy as Code is a powerful approach to managing and enforcing security policies in Kubernetes clusters. By using tools like Gatekeeper and OPA, you can define and enforce constraints that ensure compliance and reduce the risk of security vulnerabilities. Understanding the deployment process and avoiding race conditions is crucial to effectively implementing these policies.

---
<!-- nav -->
[[09-Policy as Code in DevSecOps Part 5|Policy as Code in DevSecOps Part 5]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[11-Policy as Code in DevSecOps Part 7|Policy as Code in DevSecOps Part 7]]

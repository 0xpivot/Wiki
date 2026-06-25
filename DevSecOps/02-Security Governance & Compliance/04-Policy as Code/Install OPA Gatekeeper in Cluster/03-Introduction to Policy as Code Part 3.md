---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure and application policies using declarative code. This method allows teams to define, enforce, and audit policies in a consistent and repeatable manner. One of the most popular tools for implementing Policy as Code in Kubernetes clusters is Open Policy Agent (OPA) Gatekeeper.

### What is Open Policy Agent (OPA)?

Open Policy Agent (OPA) is a powerful open-source tool that enables organizations to implement policy as code. OPA provides a declarative language called Rego for defining policies and integrates seamlessly with various systems, including Kubernetes. By using OPA, you can enforce policies across your entire infrastructure, ensuring compliance and security.

### What is Gatekeeper?

Gatekeeper is a Kubernetes admission controller that leverages OPA to enforce custom policies within a cluster. It allows you to define and enforce constraints on Kubernetes resources, ensuring that your cluster adheres to organizational policies and best practices.

### Why Use Policy as Code?

Using Policy as Code offers several benefits:

1. **Consistency**: Policies are defined in code, making it easier to ensure consistency across different environments.
2. **Automation**: Policies can be automatically enforced and audited, reducing the risk of human error.
3. **Auditability**: Since policies are defined in code, they can be version-controlled and audited easily.
4. **Flexibility**: You can define complex policies using a powerful declarative language like Rego.

### Installing OPA Gatekeeper in a Kubernetes Cluster

To install OPA Gatekeeper in a Kubernetes cluster, follow these steps:

1. **Install the Gatekeeper Operator**:
   The Gatekeeper operator manages the installation and upgrade of Gatekeeper components.

   ```sh
   kubectl create namespace gatekeeper-system
   kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
   ```

2. **Verify Installation**:
   Check that the Gatekeeper components are running correctly.

   ```sh
   kubectl get pods -n gatekeeper-system
   ```

### Configuring Permissions for Admin Users

When installing Gatekeeper, you may need to grant specific permissions to admin users to manage the CRDs (Custom Resource Definitions) created by Gatekeeper.

#### Understanding CRDs

CRDs allow you to extend the Kubernetes API with custom resources. In the context of Gatekeeper, CRDs are used to define and manage policies.

#### Granting Permissions

To grant permissions to list all CRDs, you need to modify the Kubernetes RBAC (Role-Based Access Control) configuration.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["gatekeeper.sh"]
  resources: ["*"]
  verbs: ["get", "list", "describe"]
```

Apply the updated role:

```sh
kubectl apply -f admin-role.yaml
```

### Applying the Configuration

Once the permissions are configured, you can apply the changes using a CICD (Continuous Integration and Continuous Deployment) pipeline.

#### Example Pipeline Steps

1. **Checkout Code**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Apply Configuration**:
   ```sh
   kubectl apply -f admin-role.yaml
   ```

### Verifying the Changes

After applying the configuration, verify that the admin user can now list all CRDs.

```sh
kubectl get crds
```

### Using Constraint Templates

Gatekeeper uses Constraint Templates to define policies. A Constraint Template is a reusable template that defines the structure of a constraint.

#### Example Constraint Template

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
        
        violation[{"msg": msg, "resource": resource}] {
          provided := [label | input.review.object.metadata.labels[label]]
          required := {"app", "owner"}
          missing := required - provided
          
          count(missing) > 0
          msg := sprintf("missing labels: %v", [missing])
          resource := sprintf("%v/%v", [input.review.object.metadata.namespace, input.review.object.metadata.name])
        }
```

Apply the Constraint Template:

```sh
kubectl apply -f k8srequiredlabels-template.yaml
```

### Creating Constraints

Once the Constraint Template is defined, you can create constraints based on it.

#### Example Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sRequiredLabels
metadata:
  name: k8srequiredlabels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

Apply the Constraint:

```sh
kubectl apply -f k8srequiredlabels-constraint.yaml
```

### Verifying Constraints

To verify that the constraints are working, try creating a Pod without the required labels.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: test-container
    image: nginx
```

Apply the Pod:

```sh
kubectl apply -f test-pod.yaml
```

If the Pod does not have the required labels, the creation will be blocked by Gatekeeper.

### How to Prevent / Defend

#### Detection

To detect violations of policies, you can use the `kubectl` command to check the status of Gatekeeper constraints.

```sh
kubectl get constrainttemplate
kubectl get constraint
```

#### Prevention

Ensure that all policies are defined and enforced using Constraint Templates and Constraints. Regularly review and update the policies to reflect the latest security best practices.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Version**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: test-container
    image: nginx
```

**Secure Version**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  labels:
    app: test-app
    owner: test-owner
spec:
  containers:
  - name: test-container
    image: nginx
```

#### Hardening

1. **Enable Network Policies**: Restrict network access between pods.
2. **Use Pod Security Policies**: Define and enforce pod security policies.
3. **Regular Audits**: Perform regular audits to ensure compliance with policies.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed unauthorized access to sensitive information. Using Policy as Code with Gatekeeper could have prevented this by enforcing strict access controls.
- **SolarWinds Breach**: The SolarWinds breach demonstrated the importance of monitoring and enforcing policies. Using Gatekeeper could have helped detect and prevent such breaches by enforcing strict security policies.

### Conclusion

Implementing Policy as Code with OPA Gatekeeper in a Kubernetes cluster provides a robust framework for enforcing and auditing policies. By following the steps outlined in this chapter, you can ensure that your cluster adheres to organizational policies and best practices, enhancing security and compliance.

### Practice Labs

For hands-on practice with Policy as Code and OPA Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web security and policy enforcement.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security techniques.
- **CloudGoat**: A series of labs designed to help you understand and mitigate common cloud security issues.

By completing these labs, you can gain practical experience in implementing and managing policies in a Kubernetes environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/02-Introduction to Policy as Code Part 2|Introduction to Policy as Code Part 2]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/00-Overview|Overview]] | [[04-Introduction to Policy as Code|Introduction to Policy as Code]]

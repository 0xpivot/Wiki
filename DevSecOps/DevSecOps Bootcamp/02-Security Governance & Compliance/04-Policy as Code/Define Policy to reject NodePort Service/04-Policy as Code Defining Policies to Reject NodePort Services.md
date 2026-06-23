---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Defining Policies to Reject NodePort Services

### Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure policies using code rather than manual processes. This method allows teams to automate the enforcement of security and compliance rules across their environments. In the context of Kubernetes, this means defining policies that dictate how resources such as services, deployments, and pods should be configured. One specific use case is defining a policy to reject `NodePort` services, which can pose significant security risks if not properly managed.

### Understanding NodePort Services

A `NodePort` service in Kubernetes exposes the service on a static port on each node in the cluster. This allows external traffic to reach the service via the IP address of any node in the cluster. While this can be useful for certain applications, it also introduces potential security vulnerabilities:

- **Exposure to External Traffic**: Any node in the cluster can become an entry point for external traffic, increasing the attack surface.
- **Lack of Fine-grained Control**: Without proper policies, it becomes difficult to control which services are exposed externally and how they are accessed.

#### Real-world Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allowed attackers to bypass network policies and access `NodePort` services. This demonstrates the importance of having strict policies in place to mitigate such risks.

### Customization and Namespace Management

In Kubernetes, resources such as services, deployments, and pods are typically organized into namespaces. Namespaces provide a way to divide cluster resources between multiple users or projects. Managing namespaces effectively is crucial for maintaining a secure and organized environment.

#### Customization Files

Customization files allow you to define settings that apply to multiple resources. This includes specifying the namespace for various resources. By centralizing namespace definitions, you can ensure consistency and flexibility in your deployment process.

```yaml
# Example customization file
apiVersion: v1
kind: ConfigMap
metadata:
  name: namespace-config
data:
  defaultNamespace: "default"
```

### Defining Policies to Reject NodePort Services

To enforce a policy that rejects `NodePort` services, you can use tools like Open Policy Agent (OPA) or Kubernetes Network Policies. These tools allow you to define and enforce rules that govern how resources are configured and accessed.

#### Using Open Policy Agent (OPA)

Open Policy Agent (OPA) is a powerful tool for enforcing policies in Kubernetes. You can define policies that check for the presence of `NodePort` services and reject them if found.

##### Step-by-Step Implementation

1. **Install OPA**: First, install OPA in your Kubernetes cluster. This can be done using Helm charts or manually deploying the OPA operator.

    ```bash
    helm repo add openpolicyagent https://openpolicyagent.github.io/charts
    helm install opa openpolicyagent/opa
    ```

2. **Define the Policy**: Create a policy that checks for `NodePort` services and rejects them.

    ```rego
    package kubernetes.admission

    deny[msg] {
        input.request.kind.kind == "Service"
        input.request.object.spec.type == "NodePort"
        msg = sprintf("NodePort services are not allowed: %v", [input.request.object.metadata.name])
    }
    ```

3. **Deploy the Policy**: Deploy the policy to your Kubernetes cluster. This can be done by creating a ConfigMap and applying it to the OPA pod.

    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: opa-policy
      namespace: opa
    data:
      kubernetes.rego: |
        package kubernetes.admission

        deny[msg] {
            input.request.kind.kind == "Service"
            input.request.object.spec.type == "NodePort"
            msg = sprintf("NodePort services are not allowed: %v", [input.request.object.metadata.name])
        }
    ```

4. **Verify the Policy**: Test the policy by attempting to create a `NodePort` service. The policy should reject the request and return an error message.

    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: example-service
    spec:
      type: NodePort
      ports:
      - port: 80
        targetPort: 8080
      selector:
        app: example
    ```

    Attempting to apply this service should result in an error message indicating that `NodePort` services are not allowed.

### How to Prevent / Defend

#### Detection

To detect `NodePort` services in your cluster, you can use tools like `kubectl` or custom scripts. Here’s an example script that lists all `NodePort` services:

```bash
#!/bin/bash

echo "Listing NodePort services:"
kubectl get svc --all-namespaces | grep NodePort
```

#### Prevention

To prevent `NodePort` services from being created, you can implement the following measures:

1. **Use OPA Policies**: As demonstrated earlier, use OPA to enforce policies that reject `NodePort` services.
2. **Network Policies**: Implement Kubernetes Network Policies to restrict access to services based on their type.

    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: deny-nodeport-access
      namespace: default
    spec:
      podSelector: {}
      ingress:
      - from:
        - podSelector: {}
        ports:
        - protocol: TCP
          port: 30000-32767
    ```

3. **RBAC Controls**: Use Role-Based Access Control (RBAC) to limit who can create `NodePort` services.

    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      namespace: default
      name: restricted-role
    rules:
    - apiGroups: [""]
      resources: ["services"]
      verbs: ["get", "list", "watch"]
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      namespace: default
      name: restricted-binding
    subjects:
    - kind: User
      name: restricted-user
      apiGroup: rbac.authorization.k8s.io
    roleRef:
      kind: Role
      name: restricted-role
      apiGroup: rb
    ```

#### Secure Coding Fixes

Here’s an example of a vulnerable `NodePort` service definition and its secure counterpart:

**Vulnerable Definition:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: example
```

**Secure Definition:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: example
```

### Conclusion

By implementing policies to reject `NodePort` services, you can significantly enhance the security of your Kubernetes cluster. Tools like Open Policy Agent (OPA) provide powerful mechanisms for enforcing these policies, ensuring that only approved configurations are allowed. Additionally, using network policies and RBAC controls can further strengthen your security posture.

### Hands-on Labs

For practical experience with Policy as Code, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about securing Kubernetes.
- **Pacu**: A collection of offensive security modules for AWS.

These labs provide real-world scenarios and challenges to help you master the concepts discussed in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/03-Introduction to Policy as Code|Introduction to Policy as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[05-Policy as Code in DevSecOps Part 1|Policy as Code in DevSecOps Part 1]]

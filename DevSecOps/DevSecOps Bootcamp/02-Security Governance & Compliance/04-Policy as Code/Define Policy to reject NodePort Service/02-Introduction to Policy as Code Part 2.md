---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is a practice that involves defining policies and rules using code, rather than relying on manual processes or ad-hoc configurations. This approach is particularly useful in DevSecOps environments, where automation and consistency are paramount. By codifying policies, teams can ensure that security and compliance requirements are consistently enforced across different environments and applications.

### Why Policy as Code?

The primary benefits of Policy as Code include:

1. **Consistency**: Policies are defined once and applied uniformly across all environments.
2. **Automation**: Policies can be automatically enforced during deployment pipelines, reducing the risk of human error.
3. **Traceability**: Changes to policies can be tracked via version control systems, providing an audit trail.
4. **Scalability**: Policies can be easily scaled to accommodate growing infrastructures and applications.

### How Policy as Code Works

Policy as Code typically involves the following steps:

1. **Define Policies**: Write policies using a declarative language such as YAML or JSON.
2. **Integrate with CI/CD**: Integrate policy enforcement into the CI/CD pipeline.
3. **Enforce Policies**: Use tools to enforce policies during deployment and runtime.
4. **Monitor Compliance**: Continuously monitor compliance and generate alerts for violations.

### Example: Rejecting NodePort Services

Let's consider an example where we define a policy to reject `NodePort` services in a Kubernetes cluster. This is a common requirement in many organizations due to security concerns associated with exposing services directly to the internet.

#### Background Theory

Kubernetes services can be exposed using three types of service objects: `ClusterIP`, `NodePort`, and `LoadBalancer`. Each type serves a different purpose:

- **ClusterIP**: Exposes the service on a cluster-internal IP. This is the default type and makes the service reachable only within the cluster.
- **NodePort**: Exposes the service on each node’s IP at a static port (the NodePort). A ClusterIP service, to which the NodePort service routes, is automatically created.
- **LoadBalancer**: Exposes the service externally using a cloud provider’s load balancer.

The `NodePort` type is often considered less secure because it exposes the service directly to the internet, potentially allowing unauthorized access.

#### Defining the Policy

To define a policy that rejects `NodePort` services, we can use a tool like Open Policy Agent (OPA). OPA is a powerful, open-source policy engine that can be integrated into various systems, including Kubernetes.

Here is an example of a policy written in Rego, OPA's policy language:

```rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Service"
    input.request.object.spec.type == "NodePort"
    msg = sprintf("Creating NodePort services is not allowed: %v", [input.request.object.metadata.name])
}
```

This policy checks if the requested resource is a `Service` and if its `type` is set to `NodePort`. If both conditions are met, the policy denies the request and provides a descriptive message.

#### Integrating with Kubernetes

To integrate this policy with Kubernetes, we need to set up an admission controller. An admission controller is a piece of code that intercepts requests to the Kubernetes API server before persistence of the object but after the request is authenticated and authorized.

Here is an example of how to configure an admission controller using OPA:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: opa
  configuration:
    apiVersion: opa.example.com/v1
    kind: OpaConfiguration
    regoPolicies:
      - path: /path/to/policy.rego
```

This configuration specifies that the `opa` plugin should be used and points to the location of the Rego policy file.

#### Enforcing the Policy

Once the policy is defined and the admission controller is configured, Kubernetes will automatically enforce the policy during deployment. Any attempt to create a `NodePort` service will be rejected, and the user will receive an error message.

#### Monitoring Compliance

To ensure ongoing compliance, you can use monitoring tools to track policy violations. For example, you can set up alerts in Prometheus to notify you whenever a policy is violated.

### Real-World Examples

#### Recent Breaches

One notable breach involving misconfigured Kubernetes services occurred in 2021 when a misconfigured `NodePort` service led to the exposure of sensitive data. The incident highlighted the importance of enforcing strict policies to prevent such vulnerabilities.

#### Secure Configuration

To prevent similar incidents, organizations should implement strict policies that prohibit the use of `NodePort` services unless absolutely necessary. Here is an example of a secure configuration:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

This configuration uses `ClusterIP` instead of `NodePort`, ensuring that the service is only accessible within the cluster.

### How to Prevent / Defend

#### Detection

To detect violations of the policy, you can use tools like OPA to continuously monitor Kubernetes resources. Here is an example of how to set up monitoring:

```bash
kubectl get svc --all-namespaces | grep NodePort
```

This command lists all services of type `NodePort` across all namespaces.

#### Prevention

To prevent violations, ensure that the policy is strictly enforced by the admission controller. Additionally, educate developers about the risks associated with `NodePort` services and the importance of using more secure alternatives.

#### Secure Coding Fixes

Here is a comparison of a vulnerable configuration and a secure configuration:

**Vulnerable Configuration:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

**Secure Configuration:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

### Conclusion

Policy as Code is a powerful practice that helps ensure consistent and secure configurations across different environments. By defining policies using code and integrating them into CI/CD pipelines, organizations can automate policy enforcement and reduce the risk of security vulnerabilities.

### Practice Labs

For hands-on experience with Policy as Code, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

These labs provide practical experience in implementing and enforcing policies in real-world scenarios.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/01-Introduction to Policy as Code Part 1|Introduction to Policy as Code Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/03-Introduction to Policy as Code|Introduction to Policy as Code]]

---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is a fundamental practice in modern DevSecOps environments, where security policies are defined, managed, and enforced using code. This approach ensures consistency, automation, and traceability in enforcing security policies across development and operations processes. In the context of Kubernetes, one such policy might be to prevent the deployment of NodePort services, which can pose significant security risks.

### Understanding NodePort Services

NodePort services in Kubernetes expose the service on a static port on each node in the cluster. While this can be useful for certain applications, it also introduces security vulnerabilities. Specifically, exposing services on NodePorts can lead to unauthorized access and potential exploitation.

#### Why NodePort Services Are Considered Bad Practice

- **Exposure to External Networks**: NodePort services are accessible from outside the cluster, which increases the attack surface.
- **Lack of Fine-Grained Access Control**: Unlike LoadBalancer or ClusterIP services, NodePort services do not provide built-in mechanisms for controlling access based on network policies.
- **Potential for Misconfiguration**: Developers might inadvertently expose sensitive services to the internet, leading to data breaches or unauthorized access.

### Automated Guardrails Using Policy as Code

To mitigate these risks, organizations often implement automated guardrails that prevent the deployment of NodePort services. These guardrails are typically implemented using tools like Open Policy Agent (OPA) and Gatekeeper, which allow for defining and enforcing policies as code.

#### Open Policy Agent (OPA)

OPA is a powerful, open-source policy engine that enables organizations to define, enforce, and manage policies across their infrastructure. OPA uses Rego, a domain-specific language (DSL) designed specifically for defining policies.

#### Gatekeeper

Gatekeeper is a Kubernetes admission controller that integrates with OPA to enforce policies within a Kubernetes cluster. By leveraging Gatekeeper, organizations can automatically reject manifest files that violate predefined policies, such as the deployment of NodePort services.

### Defining the Constraint Template

To define a policy that rejects NodePort services, we need to create a constraint template using Rego. This template will specify the conditions under which a Kubernetes manifest should be rejected.

#### Creating the Constraint Template

The constraint template is defined in a YAML file, which includes the Rego code that specifies the policy logic.

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sServiceNodePort
metadata:
  name: k8s-service-nodeport
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Service"]
  parameters:
    allowed: false
```

#### Explanation of the Constraint Template

- **apiVersion**: Specifies the API version for the constraint template.
- **kind**: Specifies the kind of constraint template.
- **metadata.name**: The name of the constraint template.
- **spec.match.kinds**: Specifies the Kubernetes resources to which the policy applies. In this case, it applies to `Service` objects.
- **spec.parameters.allowed**: A parameter that controls whether NodePort services are allowed or not. Setting it to `false` means that NodePort services are not allowed.

### Rego Code for Policy Definition

Rego is the domain-specific language used by OPA to define policies. The Rego code within the constraint template specifies the logic for rejecting NodePort services.

```rego
package gatekeeper.constraints.k8s_service_nodeport

violation[{"msg": msg}] {
    input.review.object.kind == "Service"
    input.review.object.spec.type == "NodePort"
    params.allowed == false
    msg := sprintf("NodePort services are not allowed: %v", [input.review.object.metadata.name])
}
```

#### Explanation of the Rego Code

- **package**: Defines the package name for the policy.
- **violation**: A rule that defines when a violation occurs. In this case, a violation occurs if the `Service` object has a `type` of `NodePort` and `params.allowed` is set to `false`.
- **sprintf**: A function that formats the error message to include the name of the service.

### Testing the Policy

To ensure that the policy works as intended, we need to test it by attempting to deploy a NodePort service and verifying that it is rejected.

#### Example Deployment Manifest

Here is an example of a Kubernetes manifest that deploys a NodePort service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: NodePort
  selector:
    app: example-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

#### Expected Result

When this manifest is applied to the cluster, the policy should reject it, and an error message should be returned indicating that NodePort services are not allowed.

### How to Prevent / Defend

#### Detection

To detect violations of the policy, organizations can use tools like OPA and Gatekeeper to monitor Kubernetes clusters for unauthorized deployments. These tools can generate alerts or logs when a policy is violated.

#### Prevention

To prevent the deployment of NodePort services, organizations should:

- Implement automated guardrails using tools like OPA and Gatekeeper.
- Educate developers about the risks associated with NodePort services and the importance of adhering to security policies.
- Regularly review and update security policies to address new threats and vulnerabilities.

#### Secure Coding Fixes

Here is an example of a vulnerable deployment manifest and its secure counterpart:

**Vulnerable Deployment Manifest**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: NodePort
  selector:
    app: example-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

**Secure Deployment Manifest**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  type: ClusterIP
  selector:
    app: example-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

### Real-World Examples

#### Recent Breaches and CVEs

One notable example of a breach related to NodePort services occurred in 2021, where a misconfigured NodePort service exposed sensitive data to the internet. This incident highlights the importance of implementing strict security policies and automated guardrails to prevent such vulnerabilities.

### Hands-On Labs

For practical experience with implementing policy as code, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on exercises for learning about web application security, including policy enforcement.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and policy implementation.
- **CloudGoat**: A series of labs for practicing cloud security, including Kubernetes security policies.

### Conclusion

Implementing policy as code is a critical component of modern DevSecOps practices. By defining and enforcing policies using tools like OPA and Gatekeeper, organizations can significantly reduce the risk of security vulnerabilities, such as those associated with NodePort services. Through education, automation, and regular reviews, organizations can maintain a robust security posture and protect their infrastructure from unauthorized access and exploitation.

---
<!-- nav -->
[[04-Policy as Code Defining Policies to Reject NodePort Services|Policy as Code Defining Policies to Reject NodePort Services]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[06-Policy as Code in DevSecOps Part 2|Policy as Code in DevSecOps Part 2]]

---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of "policy as code" and how it relates to Kubernetes.**

Policy as code refers to the practice of writing policies in a structured, machine-readable format that can be version-controlled and integrated into the CI/CD pipeline. In the context of Kubernetes, this means creating policies that can be enforced across the cluster to ensure that resources are deployed in a secure and compliant manner. These policies can be defined for various aspects such as resource limits, pod security, network policies, and more. By implementing policy as code, Kubernetes administrators can automate the validation of configuration files and enforce organizational policies consistently across different environments.

**Q2. How does Open Policy Agent (OPA) function within a Kubernetes cluster?**

Open Policy Agent (OPA) functions as a generic policy engine that can be used to enforce policies in various environments, including Kubernetes. In a Kubernetes cluster, OPA acts as an admission controller, intercepting requests to the API server. When a request is made to create or modify a resource, OPA evaluates the request against a set of predefined policies. If the request complies with the policies, it is allowed to proceed; otherwise, it is rejected. This ensures that only valid and compliant configurations are applied to the cluster, thereby maintaining security and consistency.

**Q3. What is the primary difference between Open Policy Agent (OPA) and Gatekeeper in the context of Kubernetes?**

The primary difference between Open Policy Agent (OPA) and Gatekeeper lies in their scope and ease of use. OPA is a general-purpose policy engine that can be used in various contexts beyond Kubernetes, such as cloud infrastructure, APIs, and more. It offers a high degree of flexibility in defining policies, allowing for granular access control based on roles, IP addresses, and request parameters. On the other hand, Gatekeeper is a Kubernetes-specific admission controller that leverages OPA under the hood. It is designed to be more user-friendly and easier to configure for Kubernetes environments. While both tools use the same policy definition language (Rego), Gatekeeper simplifies the process of defining and enforcing policies within a Kubernetes cluster.

**Q4. How can you leverage OPA or Gatekeeper to enforce custom policies in a Kubernetes cluster?**

To leverage OPA or Gatekeeper for enforcing custom policies in a Kubernetes cluster, you first need to install and configure the tool in your cluster. Once installed, you can define your policies using the Rego language, which is a declarative language designed for expressing policy logic. For example, you might want to enforce a policy that limits the number of replicas in a deployment to 10. You would write a Rego policy that checks the `spec.replicas` field of a deployment and rejects the request if it exceeds the limit. After defining the policy, you need to apply it to the cluster. With Gatekeeper, you typically create a `ConstraintTemplate` and a corresponding `Constraint` object, which are then evaluated by the admission controller. This setup ensures that all incoming requests are validated against the defined policies, preventing non-compliant configurations from being applied to the cluster.

**Q5. Provide a recent real-world example where policy enforcement tools like OPA or Gatekeeper could have prevented a security breach.**

In the context of Kubernetes, a recent real-world example where policy enforcement tools like OPA or Gatekeeper could have been beneficial is the incident involving the compromise of Kubernetes clusters due to misconfigured resources. For instance, a misconfigured `Service` of type `LoadBalancer` or `NodePort` could expose sensitive internal services to the internet, leading to unauthorized access. A policy enforced by OPA or Gatekeeper could restrict the creation of such services, ensuring that only intended services are exposed externally. By defining and enforcing such policies, organizations can prevent accidental misconfigurations that could lead to security breaches. For example, a policy could be defined to disallow the creation of `LoadBalancer` or `NodePort` services in certain namespaces or environments, thereby mitigating the risk of exposure.

**Q6. How would you configure a Gatekeeper constraint to prevent the deployment of containers with privileged mode enabled in a Kubernetes cluster?**

To configure a Gatekeeper constraint that prevents the deployment of containers with privileged mode enabled in a Kubernetes cluster, you would follow these steps:

1. **Install Gatekeeper**: Ensure that Gatekeeper is installed in your Kubernetes cluster. You can use the official Helm chart or the YAML manifests provided by the Gatekeeper project.

2. **Define a Constraint Template**: Create a `ConstraintTemplate` that defines the structure of the constraint. For example, you might create a template named `K8sPrivilegedContainers`.

   ```yaml
   apiVersion: templates.gatekeeper.sh/v1beta1
   kind: ConstraintTemplate
   metadata:
     name: k8sprivilegedcontainers
   spec:
     crd:
       spec:
         names:
           kind: K8sPrivilegedContainers
     targets:
       - target: admission.k8s.gatekeeper.sh
         rego: |
           package k8sprivilegedcontainers

           violation[{"msg": msg, "details": {"kind": input.request.object.kind, "name": input.request.object.metadata.name}}] {
             input.request.operation == "CREATE"
             input.request.object.kind == "Pod"
             container := input.request.object.spec.containers[_]
             container.securityContext.privileged == true
             msg = sprintf("%v %v has a container with privileged mode enabled", [input.request.object.kind, input.request.object.metadata.name])
           }
   ```

3. **Create a Constraint**: Define a `Constraint` that uses the `ConstraintTemplate` to enforce the policy.

   ```yaml
   apiVersion: constraints.gatekeeper.sh/v1beta1
   kind: K8sPrivilegedContainers
   metadata:
     name: deny-privileged-containers
   spec:
     match:
       kinds:
         - apiGroups: ["apps"]
           kinds: ["Deployment", "StatefulSet", "DaemonSet"]
   ```

4. **Apply the Constraint**: Apply the `Constraint` to the cluster using `kubectl apply`.

   ```bash
   kubectl apply -f <path-to-constraint-template>.yaml
   kubectl apply -f <path-to-constraint>.yaml
   ```

By following these steps, you ensure that any attempt to deploy a container with privileged mode enabled will be blocked by Gatekeeper, thereby enhancing the security posture of your Kubernetes cluster.

---
<!-- nav -->
[[06-Empowering Teams While Ensuring Security in Kubernetes Clusters|Empowering Teams While Ensuring Security in Kubernetes Clusters]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Introduction to Open Policy Agent OPA and OPA Gatekeeper/00-Overview|Overview]]

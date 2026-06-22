---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is it important to prevent running privileged containers in a Kubernetes cluster?**

Running privileged containers in a Kubernetes cluster significantly increases the risk of security breaches. If a container is compromised and runs with root privileges, an attacker could potentially escape the container’s isolation and gain unauthorized access to the host system. This can lead to broader attacks on other resources and services within the cluster. By enforcing a policy to disallow privileged containers, the overall security posture of the cluster is improved, reducing the attack surface and mitigating potential damage.

**Q2. How can you ensure that images built do not contain root user privileges?**

To ensure that images built do not contain root user privileges, you can implement several measures:

1. **Image Scanning**: Use tools like Clair, Trivy, or Aqua Security to scan Docker images during the CI/CD pipeline. These tools check for various security vulnerabilities, including whether the image uses a root user.

2. **Build Configuration**: Ensure that the Dockerfile explicitly sets a non-root user for the container. For example:
    ```dockerfile
    FROM ubuntu:latest
    RUN useradd --create-home appuser
    USER appuser
    ```

3. **Policy Enforcement**: Use Kubernetes admission controllers like PodSecurityPolicy or Open Policy Agent (OPA) to enforce that pods cannot run with root privileges, even if the image itself allows it.

**Q3. What is the role of Open Policy Agent (OPA) in enforcing policies against privileged containers?**

Open Policy Agent (OPA) plays a crucial role in enforcing policies against privileged containers by providing a declarative framework to define and enforce policies across the Kubernetes cluster. OPA integrates with Kubernetes through the Gatekeeper admission controller, which enforces custom policies defined in Constraint Templates and Constraints.

For example, to enforce a policy against privileged containers, you might define a Constraint Template and a corresponding Constraint as follows:

```yaml
# ConstraintTemplate
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8spspprivilegedcontainers
spec:
  crd:
    spec:
      names:
        kind: K8SPSPPrivilegedContainers
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spspprivilegedcontainers
        
        violation[{"msg": msg, "details": {"containerName": input.request.object.spec.containers[i].name}}] {
          input.review.kind == "Pod"
          input.request.object.metadata.namespace != "kube-system"
          container := input.request.object.spec.containers[i]
          container.securityContext.privileged
          msg = sprintf("Container %s is configured to run with privileged mode", [container.name])
        }

# Constraint
apiVersion: constraints.gatekeeper.sh/v1
kind: K8SPSPPrivilegedContainers
metadata:
  name: deny-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: [""] # Core API group
        kinds: ["Pod"]
```

This setup ensures that any attempt to deploy a pod with a privileged container is blocked by Gatekeeper, adhering to the defined security policy.

**Q4. How can you configure a Kubernetes cluster to exclude certain namespaces from a policy that blocks privileged containers?**

To configure a Kubernetes cluster to exclude certain namespaces from a policy that blocks privileged containers, you can modify the Constraint to include exclusions. For example, you can exclude the `kube-system` namespace where critical control plane components reside. Here is how you can achieve this using Gatekeeper:

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8SPSPPrivilegedContainers
metadata:
  name: deny-privileged-containers-exclude-kube-system
spec:
  match:
    kinds:
      - apiGroups: [""] # Core API group
        kinds: ["Pod"]
  parameters:
    excludedNamespaces:
      - kube-system
```

In this configuration, the `excludedNamespaces` parameter specifies that the `kube-system` namespace should be exempted from the policy. This allows critical system components to run with elevated privileges while ensuring that regular pods adhere to the security policy.

**Q5. Explain how a recent breach or CVE might have been prevented by enforcing a policy against privileged containers.**

One notable example is the Kubernetes API server vulnerability (CVE-2021-25741), where an attacker could exploit a flaw to escalate their privileges and gain full control over the cluster. If a policy against privileged containers had been enforced, the attacker would have faced additional barriers:

- **Isolation**: Even if the attacker managed to compromise a container, the lack of root privileges would limit their ability to escape the container’s isolation.
- **Detection**: Policies enforced by tools like Gatekeeper would flag any attempts to run containers with elevated privileges, alerting administrators to suspicious activity.

By implementing such policies, organizations can significantly reduce the risk of such breaches, ensuring that even if a component is compromised, the impact is limited due to the restricted privileges of the containers involved.

---
<!-- nav -->
[[07-Policy as Code in DevSecOps|Policy as Code in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]]

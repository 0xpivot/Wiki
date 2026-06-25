---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is a practice in DevSecOps where policies are written in code, typically in YAML or JSON, and managed through version control systems like Git. This approach allows teams to define, manage, and enforce security policies consistently across their infrastructure and applications. In this context, we will focus on defining a policy to reject NodePort Services in a Kubernetes cluster using Gatekeeper, an open-source policy controller for Kubernetes.

### Background Theory

#### What is a NodePort Service?

A NodePort Service in Kubernetes exposes the service on a static port on each node in the cluster. This means that you can access the service from outside the cluster by using the IP address of any node and the specified port number. While this can be useful for development and testing purposes, it poses significant security risks in production environments because it exposes internal services to the external network.

#### Why Reject NodePort Services?

Rejecting NodePort Services is crucial for maintaining the security and integrity of your Kubernetes cluster. Exposing services via NodePort can lead to unauthorized access, data breaches, and other security vulnerabilities. By enforcing a policy to reject NodePort Services, you ensure that only secure and controlled methods of accessing services are allowed.

### Constraint Templates and Constraints

In Gatekeeper, policies are defined using constraint templates and constraints. A constraint template defines the structure and logic of a policy, while a constraint applies that policy to specific resources in the cluster.

#### Constraint Template

The constraint template defines the structure and logic of the policy. Here is an example of a constraint template that enforces the rejection of NodePort Services:

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

        violation[{"msg": msg, "details": {"kind": input.request.object.kind, "name": input.request.object.metadata.name}}] {
          input.request.operation == "CREATE"
          input.request.object.kind == "Service"
          input.request.object.spec.type == "NodePort"
          msg = sprintf("%v %v should not be of type NodePort", [input.request.object.kind, input.request.object.metadata.name])
        }
```

This constraint template defines a policy that checks if a new `Service` resource being created has a `type` of `NodePort`. If it does, the policy will generate a violation message.

#### Constraint

The constraint applies the policy defined in the constraint template to specific resources in the cluster. Here is an example of a constraint that uses the `K8sBlockNodePort` template:

```yaml
apiVersion: constraints.gatekeeper.sh/v1
kind: K8sBlockNodePort
metadata:
  name: deny-nodeport-services
spec:
  match:
    kinds:
      - apiGroups: [""] # Core API Group
        kinds: ["Service"]
```

This constraint matches all `Service` resources in the core API group and applies the `K8sBlockNodePort` policy to them.

### Applying the Policy

To apply these policies to your Kubernetes cluster, you need to deploy the constraint template and constraint using a tool like `kubectl`.

```sh
kubectl apply -f k8sblocknodeport-template.yaml
kubectl apply -f deny-nodeport-services.yaml
```

### How to Prevent / Defend

#### Detection

To detect if any NodePort Services are currently deployed in your cluster, you can use the following `kubectl` command:

```sh
kubectl get svc --all-namespaces -o json | jq '.items[] | select(.spec.type == "NodePort")'
```

This command lists all `Service` resources in the cluster and filters out those with a `type` of `NodePort`.

#### Prevention

To prevent the creation of NodePort Services, you can use the policy defined above. Additionally, you can configure your CI/CD pipeline to automatically check for and reject any changes that introduce NodePort Services.

#### Secure Coding Fix

Here is an example of a NodePort Service definition:

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
    app: example-app
```

To fix this, you can change the `type` to `ClusterIP`:

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
    app: example-app
```

### Real-World Examples

#### Recent Breaches

One notable breach involving NodePort Services occurred in a Kubernetes cluster where a misconfigured NodePort Service exposed sensitive data to the internet. This led to unauthorized access and data exfiltration. By enforcing a policy to reject NodePort Services, such incidents can be prevented.

### Configuration Hardening

To further harden your Kubernetes cluster, you can also configure network policies to restrict traffic between pods and nodes. Here is an example of a network policy that restricts traffic to only allow communication within the same namespace:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  ingress:
    - from:
        - podSelector: {}
```

### Practice Labs

For hands-on practice with Policy as Code in Kubernetes, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security, including policy enforcement.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can use to test and enforce security policies.
- **CloudGoat**: A cloud security training platform that includes Kubernetes security exercises.

### Conclusion

By implementing a policy to reject NodePort Services in your Kubernetes cluster, you can significantly enhance the security of your environment. Using tools like Gatekeeper, you can define, manage, and enforce these policies effectively. Always ensure that your policies are tested and validated in a controlled environment before deploying them to production.

---
<!-- nav -->
[[05-Policy as Code in DevSecOps Part 1|Policy as Code in DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject NodePort Service/00-Overview|Overview]] | [[07-Policy as Code in DevSecOps Part 3|Policy as Code in DevSecOps Part 3]]

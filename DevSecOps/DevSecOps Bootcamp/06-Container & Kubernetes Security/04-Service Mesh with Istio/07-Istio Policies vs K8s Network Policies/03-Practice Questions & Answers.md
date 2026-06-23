---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the key differences between Istio policies and Kubernetes network policies.**

Istio policies operate at Layer 7 (application layer), focusing on HTTP requests, methods, headers, and URL paths. They leverage Istio's Envoy proxies to handle detailed application-level traffic and can manage TLS tasks such as encryption, decryption, and certificate management. In contrast, Kubernetes network policies operate at Layers 3 and 4 (network and transport layers), dealing primarily with IP addresses and ports. They provide a powerful way to control traffic flow but lack the fine-grained application-layer controls available with Istio policies.

**Q2. How would you configure an Istio authorization policy to restrict access to specific API endpoints?**

To configure an Istio authorization policy to restrict access to specific API endpoints, you would define a policy that specifies the allowed HTTP methods, headers, and URL paths. Here’s an example YAML snippet:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-endpoint-restriction
spec:
  selector:
    matchLabels:
      app: my-app
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/my-service-account"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/resource/*"]
```

This policy allows only `GET` and `POST` requests to paths under `/api/v1/resource/*` from a specified service account.

**Q3. Why might Kubernetes recommend using Istio policies over network policies for certain scenarios?**

Kubernetes recommends using Istio policies over network policies for scenarios requiring fine-grained control at the application layer. Istio policies can enforce rules based on HTTP methods, headers, and URL paths, providing more granular control compared to network policies, which operate at the network and transport layers. Additionally, Istio policies can handle TLS-related tasks, such as encryption and certificate management, offering enhanced security features.

**Q4. How can network policies help prevent security breaches in a Kubernetes cluster?**

Network policies can help prevent security breaches by controlling traffic flow at the network and transport layers. By setting strict ingress and egress rules, you can limit which pods can communicate with each other and with external services. For example, you can restrict a backend application to only communicate with a MySQL database and Redis, blocking all other outgoing traffic. This minimizes the attack surface and prevents unauthorized access, as seen in recent vulnerabilities like CVE-2021-25741, where attackers exploited overly permissive network policies to gain unauthorized access.

**Q5. What are the advantages of using Istio policies for managing TLS tasks in a Kubernetes cluster?**

The advantages of using Istio policies for managing TLS tasks include centralized control over encryption, decryption, and certificate management. Istio policies can enforce TLS policies across the entire service mesh, ensuring consistent security practices. This is particularly useful for handling mutual TLS (mTLS) configurations, where both client and server authenticate each other. For instance, Istio policies can ensure that all inter-service communications are encrypted, reducing the risk of man-in-the-middle attacks. Recent real-world examples include the mitigation of vulnerabilities like CVE-2021-3711, where proper TLS enforcement could have prevented unauthorized access.

---
<!-- nav -->
[[02-Introduction to Service Mesh with Istio|Introduction to Service Mesh with Istio]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/07-Istio Policies vs K8s Network Policies/00-Overview|Overview]]

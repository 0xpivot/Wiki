---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Introduction to Service Mesh with Istio

Service mesh is a dedicated infrastructure layer for handling service-to-service communication. One of the most popular service mesh implementations is Istio, which provides a robust set of features including traffic management, observability, and security. In this chapter, we will focus on configuring authorization policies using Istio, which is crucial for ensuring that services within your mesh communicate securely and only with authorized entities.

### Background Theory

Before diving into the practical aspects of configuring authorization policies, it’s essential to understand the underlying concepts and theories.

#### What is a Service Mesh?

A service mesh is a dedicated infrastructure layer for handling service-to-service communication. It abstracts away the complexity of managing microservices interactions, providing features such as:

- **Traffic Management**: Routing, load balancing, retries, and timeouts.
- **Observability**: Metrics, logging, and distributed tracing.
- **Security**: Mutual TLS, authentication, and authorization.

#### What is Istio?

Istio is an open-source service mesh that provides a uniform way to secure, connect, and monitor microservices. It is designed to work with any platform and supports a wide range of environments, including Kubernetes, VMs, and bare metal.

#### Why Use IstService Mesh with Istio?

Using a service mesh like Istio offers several benefits:

- **Centralized Control**: Manage complex interactions between services from a single place.
- **Improved Observability**: Gain insights into the behavior of your services through metrics and logs.
- **Enhanced Security**: Implement strong security measures like mutual TLS and fine-grained access control.

### Setting Up the Environment

To demonstrate the configuration of authorization policies, we will use a Kubernetes cluster with Istio installed. The environment will consist of a simple application called "Online Boutique," which consists of multiple microservices.

#### Prerequisites

Ensure you have the following tools installed:

- `kubectl`: Command-line tool for interacting with Kubernetes clusters.
- `istioctl`: Command-line tool for installing and managing Istio.

#### Installing Istio

To install Istio, run the following commands:

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y
```

This will install Istio with a basic profile suitable for development and testing.

### Configuring Authorization Policies

Authorization policies in Istio are used to enforce access control rules for services within the mesh. These policies define who can access which resources and under what conditions.

#### Checking Current Communication Flow

Before configuring authorization policies, it’s important to understand how communication is currently flowing within the mesh. This involves checking the permissions and roles assigned to different users and services.

##### Granting Additional Permissions

As an administrator, you might need to grant additional permissions to perform certain actions, such as creating pods or executing commands within a container.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: custom-admin-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: custom-admin-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: custom-admin-role
  apiGroup: rbac.authorization.k8s.io
```

This YAML defines a `ClusterRole` with the necessary permissions and binds it to the `admin-user`.

#### Creating a Pod for Testing

To test the communication flow, we will create a pod in the `online-boutique` namespace. This pod will be used to execute commands and test connections.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: online-boutique
spec:
  containers:
  - name: test-container
    image: busybox
    command: ["sh", "-c", "sleep 3600"]
```

Apply the pod configuration:

```bash
kubectl apply -f test-pod.yaml
```

#### Executing Commands in the Pod

Once the pod is created, you can use `kubectl exec` to execute commands within the container.

```bash
kubectl exec -it test-pod -n online-boutique -- /bin/sh
```

This command opens an interactive shell session inside the pod.

### Configuring Authorization Policies with Istio

Now that we have set up the environment, let’s configure authorization policies using Istio.

#### Understanding Authorization Policies

Authorization policies in Istio are defined using the `AuthorizationPolicy` resource. This resource allows you to specify rules for allowing or denying access to services based on various criteria.

##### Example Authorization Policy

Here is an example of an authorization policy that allows access to a specific service only from a trusted source.

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-trusted-source
  namespace: online-boutique
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/online-boutique/sa/default"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/api/products"]
```

This policy allows GET requests to the `/api/products` endpoint from the `default` service account in the `online-boutique` namespace.

#### Applying the Authorization Policy

To apply the authorization policy, save it to a file (e.g., `allow-trusted-source.yaml`) and apply it using `kubectl`.

```bash
kubectl apply -f allow-trusted-source.yaml
```

### Testing the Authorization Policy

After applying the authorization policy, you should test it to ensure it behaves as expected.

#### Testing Allowed Access

Use the test pod to send a GET request to the `/api/products` endpoint.

```bash
kubectl exec -it test-pod -n online-boutique -- curl http://productpage.online-boutique.svc.cluster.local/api/products
```

If the request is allowed, you should receive a successful response.

#### Testing Denied Access

Modify the request to test denied access. For example, change the method to POST.

```bash
kubectl exec -it test-pod -n online-boutique -- curl -X POST http://productpage.online-boutique.svc.cluster.local/api/products
```

This request should be denied according to the authorization policy.

### Common Pitfalls and Best Practices

When configuring authorization policies, there are several common pitfalls to avoid:

- **Overly Permissive Policies**: Ensure that policies are not overly permissive, which could lead to unauthorized access.
- **Incomplete Coverage**: Make sure that all critical endpoints and operations are covered by appropriate policies.
- **Complexity**: Avoid overly complex policies that are difficult to maintain and understand.

#### Best Practices

- **Least Privilege Principle**: Apply the principle of least privilege, granting only the minimum necessary permissions.
- **Regular Audits**: Regularly audit and review authorization policies to ensure they remain effective and up-to-date.
- **Documentation**: Maintain thorough documentation of all authorization policies and their intended effects.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can use Istio’s built-in observability features, such as metrics and logs.

##### Example Metrics Query

Use the `istioctl` tool to query metrics related to authorization policies.

```bash
istioctl dashboard kiali
```

This command opens the Kiali dashboard, which provides detailed visualizations of service mesh traffic and authorization policies.

#### Prevention

To prevent unauthorized access, follow these steps:

- **Implement Strong Authentication**: Use strong authentication mechanisms, such as mutual TLS, to ensure that only authorized clients can access services.
- **Regularly Update Policies**: Regularly update and review authorization policies to ensure they remain effective against new threats.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the authorization policy.

**Vulnerable Version**

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-all
  namespace: online-boutique
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["*"]
    to:
    - operation:
        methods: ["*"]
        paths: ["*"]
```

**Secure Version**

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-trusted-source
  namespace: online-boutique
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/online-boutique/sa/default"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/api/products"]
```

### Real-World Examples

#### Recent CVEs and Breaches

Several recent CVEs and breaches highlight the importance of proper authorization policies:

- **CVE-2021-25282**: A vulnerability in Istio’s Envoy proxy allowed unauthorized access to internal services.
- **Breaches in Financial Services**: Multiple financial institutions experienced breaches due to inadequate authorization policies.

These examples underscore the need for robust authorization policies to protect sensitive data and services.

### Conclusion

Configuring authorization policies in Istio is a critical aspect of securing service-to-service communication within a service mesh. By understanding the underlying concepts, setting up the environment correctly, and applying best practices, you can ensure that your services are protected against unauthorized access.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security, including service mesh configurations.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **Kubernetes Goat**: Focuses on Kubernetes security and includes scenarios for configuring authorization policies.

By completing these labs, you can gain practical experience in configuring and managing authorization policies in Istio.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/11-Introduction to Service Mesh with Istio Part 9|Introduction to Service Mesh with Istio Part 9]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/00-Overview|Overview]] | [[13-Configuring Authorization Policies in Istio|Configuring Authorization Policies in Istio]]

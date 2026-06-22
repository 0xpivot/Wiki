---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to Kubernetes Manifests and Kustomize

In the realm of DevSecOps, managing the deployment and lifecycle of microservices applications within a Kubernetes cluster is a critical task. This chapter delves into the intricacies of configuring and deploying microservices using Kubernetes manifests and Kustomize. We'll cover the concepts of Kubernetes services, Ingress resources, and the benefits of using Kustomize for customizing deployments. Additionally, we'll explore real-world examples, potential pitfalls, and best practices for securing these configurations.

### Kubernetes Services and Load Balancers

A Kubernetes service is an abstraction that defines a logical set of pods and a policy by which to access them. Services provide a stable IP address and DNS name for your application, even as the underlying pods change. One common type of service is an external load balancer, which exposes your application to the internet.

#### External Load Balancer

An external load balancer is a service type that creates a load balancer in the cloud provider's infrastructure. This load balancer routes traffic to the pods associated with the service. Here’s how it works:

1. **Provisioning**: When you create a service of type `LoadBalancer`, the cloud provider provisions a load balancer.
2. **Routing**: The load balancer routes incoming traffic to the pods associated with the service.
3. **DNS Name/IP Address**: The load balancer provides an IP address or DNS name that can be used to access the service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
  selector:
    app: frontend
```

This service definition creates a load balancer that forwards traffic on port 80 to the pods labeled with `app: frontend`.

#### Example: Load Balancer in Action

Consider a scenario where you have a microservices application with a frontend service. The frontend service is exposed via a load balancer, allowing users to access the application over the internet.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
  selector:
    app: frontend
```

When this service is deployed, the cloud provider will create a load balancer and assign an IP address or DNS name to it. Users can access the frontend service using this IP address or DNS name.

### Ingress Resources

An Ingress resource is an API object that manages external access to the services in a cluster, typically HTTP. Ingress can provide load balancing, SSL termination, and name-based virtual hosting.

#### Ingress Controller

An Ingress controller is a piece of software that watches the Kubernetes API for Ingress resources and then configures a load balancer to route traffic accordingly. Common ingress controllers include NGINX, Traefik, and HAProxy.

#### Example: Ingress Resource

Here’s an example of an Ingress resource that routes traffic to the frontend service:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
spec:
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
```

This Ingress resource routes traffic to the `frontend-service` based on the hostname `myapp.example.com`.

### Kustomize for Customizing Deployments

Kustomize is a tool that helps you customize and manage Kubernetes manifests. It allows you to define a base set of resources and then customize them for different environments or purposes.

#### Kustomization File

A kustomization file (`kustomization.yaml`) specifies the resources to be included and customized. Here’s an example:

```yaml
resources:
- deployment.yaml
- service.yaml
- ingress.yaml

patchesStrategicMerge:
- patch.yaml
```

This kustomization file includes three resources (`deployment.yaml`, `service.yaml`, and `ingress.yaml`) and applies a strategic merge patch (`patch.yaml`).

#### Example: Using Kustomize

Suppose you have a base directory with the following files:

- `deployment.yaml`
- `service.yaml`
- `ingress.yaml`
- `kustomization.yaml`

The `kustomization.yaml` file might look like this:

```yaml
resources:
- deployment.yaml
- service.yaml
- ingress.yaml

patchesStrategicMerge:
- patch.yaml
```

And the `patch.yaml` file might contain customizations such as changing the image tag:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: myregistry/myimage:v2
```

### Real-World Examples and Pitfalls

#### Real-World Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in the NGINX Ingress Controller that allows attackers to bypass authentication and access protected resources. This vulnerability highlights the importance of securing Ingress resources and keeping your ingress controller up to date.

#### Pitfall: Exposing Internal Services

One common pitfall is exposing internal services to the internet unnecessarily. This can lead to security vulnerabilities if the service is not properly secured. Always ensure that only necessary services are exposed externally.

### How to Prevent / Defend

#### Detection

To detect misconfigurations, you can use tools like `kube-bench` and `kubescape`. These tools check your Kubernetes cluster against CIS benchmarks and other security best practices.

#### Prevention

1. **Secure Ingress Resources**: Ensure that Ingress resources are properly configured with authentication and authorization mechanisms.
2. **Use Network Policies**: Implement network policies to restrict traffic between pods.
3. **Keep Software Updated**: Regularly update your ingress controller and other components to patch known vulnerabilities.

#### Secure-Coding Fixes

Here’s an example of a vulnerable Ingress resource and its secure counterpart:

**Vulnerable Ingress Resource**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: insecure-ingress
spec:
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: insecure-service
                port:
                  number: 80
```

**Secure Ingress Resource**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
spec:
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: secure-service
                port:
                  number: 80
  tls:
    - hosts:
        - myapp.example.com
      secretName: tls-secret
```

In the secure version, TLS is enabled to encrypt traffic.

### Practice Labs

For hands-on practice with Kubernetes manifests and Kustomize, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers Kubernetes basics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning security.

These labs provide practical experience in deploying and securing microservices applications in a Kubernetes environment.

### Conclusion

Managing microservices applications in a Kubernetes cluster requires a deep understanding of Kubernetes services, Ingress resources, and tools like Kustomize. By following best practices and using secure configurations, you can ensure that your applications are both functional and secure.

---
<!-- nav -->
[[05-Introduction to Application Release Pipelines with ArgoCD and Kustomize|Introduction to Application Release Pipelines with ArgoCD and Kustomize]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]] | [[07-Introduction to Kubernetes Manifests and Microservices Deployment|Introduction to Kubernetes Manifests and Microservices Deployment]]

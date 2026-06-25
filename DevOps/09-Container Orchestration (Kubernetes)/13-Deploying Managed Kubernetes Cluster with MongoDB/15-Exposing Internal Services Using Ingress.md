---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Exposing Internal Services Using Ingress

To make the internal services accessible externally, we can use an Ingress controller. An Ingress controller manages external access to the services in a cluster, typically HTTP.

### Understanding Ingress

An Ingress is an API object that manages external access to the services in a cluster, typically HTTP. Ingress can provide load balancing, SSL termination, and name-based virtual hosting.

#### Components of Ingress

1. **Ingress Controller**: A component that watches the Kubernetes API for Ingress resources and configures an HTTP server to route traffic.
2. **Ingress Resource**: A configuration that defines rules for routing external traffic to services within the cluster.

### Deploying Ingress Controller

We will use the `nginx-ingress-controller` provided by the `stable` Helm repository.

#### Step-by-Step Deployment

1. Add the `stable` Helm repository.

```bash
helm repo add stable https://charts.helm.sh/stable
```

2. Install the `nginx-ingress-controller`.

```bash
helm install my-ingress stable/nginx-ingress
```

This command deploys the `nginx-ingress-controller` in the cluster.

### Configuring Ingress for Mongo Express

Next, configure an Ingress resource to expose the `mongo-express-service` externally.

#### Example: Ingress Resource for Mongo Express

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mongo-express-ingress
spec:
  rules:
    - host: mongo-express.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mongo-express-service
                port:
                  number: 8081
```

Apply this Ingress resource.

```bash
kubectl apply -f mongo-express-ingress.yaml
```

### Verifying Ingress

Verify that the Ingress is working by accessing the URL specified in the Ingress resource.

```bash
curl http://mongo-express.example.com
```

### How to Prevent / Defend

To ensure the security and reliability of your Ingress setup:

1. **Use TLS/SSL**: Ensure that all external traffic is encrypted using TLS/SSL.
2. **Rate Limiting**: Implement rate limiting to prevent abuse.
3. **Access Control**: Use network policies and RBAC to control access to the Ingress.

### Example: Enabling TLS/SSL in Ingress

To enable TLS/SSL, configure the Ingress with the appropriate certificates and keys.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mongo-express-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - mongo-express.example.com
      secretName: tls-secret
  rules:
    - host: mongo-express.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mongo-express-service
                port:
                  number: 8081
```

Apply this Ingress resource and ensure it uses the TLS secret.

```bash
kubectl apply -
```

---
<!-- nav -->
[[14-Deploying MongoDB with Persistent Volumes|Deploying MongoDB with Persistent Volumes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[16-Hands-On Labs|Hands-On Labs]]

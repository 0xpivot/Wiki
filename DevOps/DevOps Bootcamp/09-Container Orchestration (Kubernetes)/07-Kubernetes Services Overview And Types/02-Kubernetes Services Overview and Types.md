---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Services Overview and Types

### Introduction to Kubernetes Services

Kubernetes services are a fundamental component of the Kubernetes architecture, designed to provide a stable network identity to a set of pods. This allows applications to communicate with each other reliably within the cluster. In this section, we will delve deep into the concepts, types, and practical aspects of Kubernetes services.

### Understanding Pods and Their Networking

Before diving into services, it's crucial to understand how pods are networked within a Kubernetes cluster. Each pod in a Kubernetes cluster is assigned an IP address from a range specific to the node on which it runs. This IP address is used for communication between pods and external entities.

#### Pod IP Address Allocation

When a pod is scheduled on a node, it receives an IP address from a predefined range associated with that node. For instance, consider a Kubernetes cluster with three worker nodes:

- **Worker Node 1**: IP range 10.2.1.0/24
- **Worker Node 2**: IP range 10.2.2.0/24
- **Worker Node 3**: IP range 10.2.3.0/24

If a pod is scheduled on Worker Node 2, it might receive an IP address like `10.2.2.10`. Similarly, if another pod is scheduled on Worker Node 1, it could receive an IP address like `10.2.1.5`.

#### Checking Pod IP Addresses

To view the IP addresses assigned to pods in a Kubernetes cluster, you can use the `kubectl` command-line tool. Specifically, the `kubectl get pods --output=wide` command provides detailed information about each pod, including its IP address.

```bash
kubectl get pods --output=wide
```

The output might look like this:

```
NAME          READY   STATUS    RESTARTS   AGE   IP           NODE
pod1          1/1     Running   0          10m   10.2.1.10    worker-node-1
pod2          1/1     Running   0          5m    10.2.2.15    worker-node-2
```

### Kubernetes Services: An Overview

A Kubernetes service is an abstraction that defines a logical set of pods and a policy by which to access them. Services allow you to expose applications running in pods to the network, either within the cluster or externally.

#### Service Types

Kubernetes supports several types of services, each serving a different purpose:

1. **ClusterIP**: Exposes the service on a cluster-internal IP. This type makes the service reachable only from within the cluster.
2. **NodePort**: Exposes the service on each node's IP at a static port. This type makes the service reachable from outside the cluster.
3. **LoadBalancer**: Exposes the service externally using a cloud provider's load balancer.
4. **ExternalName**: Maps the service to an external DNS name rather than an IP address.

### ClusterIP Service

The `ClusterIP` service is the default type and is used to expose the service internally within the cluster. This type of service is useful for exposing services that should not be accessed from outside the cluster.

#### Example: Creating a ClusterIP Service

Let's create a simple `ClusterIP` service for a hypothetical application called `webapp`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

In this example:
- `selector`: Labels used to match the pods that this service should route traffic to.
- `ports`: Defines the port mapping. Traffic arriving on port 80 of the service will be forwarded to port 8080 of the selected pods.
- `type`: Specifies the service type as `ClusterIP`.

#### Accessing the Service Internally

Once the service is created, you can access it using its cluster-internal IP address. To find the IP address of the service, use the following command:

```bash
kubectl get svc webapp-service
```

Output might look like this:

```
NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
webapp-service    ClusterIP   10.96.0.1      <none>        80/TCP    5m
```

You can then access the service using its cluster-internal IP address and port:

```bash
curl http://10.96.0.1:80
```

### NodePort Service

The `NodePort` service exposes the service on each node's IP at a static port. This type of service is useful for exposing services that should be accessible from outside the cluster.

#### Example: Creating a NodePort Service

Let's create a `NodePort` service for the `webapp` application.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
      nodePort: 30080
  type: NodePort
```

In this example:
- `nodePort`: Specifies the port on each node where the service will be exposed. By default, Kubernetes assigns a random port between 30000 and 32767.

#### Accessing the Service Externally

Once the service is created, you can access it using the node's IP address and the specified `nodePort`. To find the node's IP address, use the following command:

```bash
kubectl get nodes -o wide
```

Output might look like this:

```
NAME            STATUS   ROLES    AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION   CONTAINER-RUNTIME
worker-node-1   Ready    <none>   10d   v1.20.0   192.168.1.10   <none>        Ubuntu 20.04 LTS     5.4.0-42-generic   containerd://1.4.12
```

You can then access the service using the node's IP address and the specified `nodePort`:

```bash
curl http://192.168.1.10:30080
```

### LoadBalancer Service

The `LoadBalancer` service uses a cloud provider's load balancer to expose the service externally. This type of service is useful for exposing services that should be accessible from the internet.

#### Example: Creating a LoadBalancer Service

Let's create a `LoadBalancer` service for the `webapp` application.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

In this example:
- `type`: Specifies the service type as `LoadBalancer`.

#### Accessing the Service via Load Balancer

Once the service is created, the cloud provider will assign an external IP address to the service. To find the external IP address, use the following command:

```bash
kubectl get svc webapp-service
```

Output might look like this:

```
NAME              TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)   AGE
webapp-service    LoadBalancer   10.96.0.1      203.0.113.10    80:30080/TCP   5m
```

You can then access the service using the external IP address and port:

```bash
curl http://203.0.113.10:80
```

### ExternalName Service

The `ExternalName` service maps the service to an external DNS name rather than an IP address. This type of service is useful for accessing external services from within the cluster.

#### Example: Creating an ExternalName Service

Let's create an `ExternalName` service for an external DNS name.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-dns-service
spec:
  type: ExternalName
  externalName: example.com
```

In this example:
- `externalName`: Specifies the external DNS name to which the service should map.

#### Accessing the External Service

Once the service is created, you can access the external service using the service name within the cluster.

```bash
curl http://external-dns-service.default.svc.cluster.local
```

### Replicas and Service Discovery

When you have multiple replicas of a pod, each replica will have its own IP address. A service can route traffic to all replicas, ensuring load balancing and fault tolerance.

#### Example: Deploying Multiple Replicas

Let's deploy multiple replicas of the `webapp` application.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp-container
        image: webapp-image:latest
        ports:
        - containerPort: 8080
```

In this example:
- `replicas`: Specifies the number of replicas to deploy.
- `selector`: Labels used to match the pods that this deployment should manage.
- `template`: Defines the pod template.

Once the deployment is created, you can check the IP addresses of the replicas using the following command:

```bash
kubectl get pods --output=wide
```

Output might look like this:

```
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
webapp-deployment-6b8c4b4f5   1/1     Running   0          5m    10.2.1.10    worker-node-1
webapp-deployment-6b8c4b4f5   1/1     Running   0          5m    10.2.2.15    worker-node-2
```

### Service Discovery and DNS

Kubernetes provides built-in DNS support for services, allowing you to discover services using their names rather than IP addresses. This simplifies service discovery and makes your applications more resilient to changes in IP addresses.

#### Example: Using DNS for Service Discovery

Let's create a service and use its name for service discovery.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

Once the service is created, you can access it using its name within the cluster.

```bash
curl http://webapp-service.default.svc.cluster.local
```

### Security Considerations

While services provide a powerful way to expose applications within a Kubernetes cluster, they also introduce potential security risks. It's essential to implement proper security measures to protect your services from unauthorized access and attacks.

#### How to Prevent / Defend

1. **Network Policies**: Use Kubernetes Network Policies to control traffic flow between pods and services.
2. **Service Mesh**: Implement a service mesh like Istio to provide advanced security features such as mutual TLS encryption and authentication.
3. **RBAC**: Use Role-Based Access Control (RBAC) to restrict access to sensitive services.
4. **Firewall Rules**: Configure firewall rules to restrict access to services based on IP addresses and ports.

#### Example: Implementing Network Policies

Let's create a network policy to restrict traffic to the `webapp-service`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: webapp-network-policy
spec:
  podSelector:
    matchLabels:
      app: webapp
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

In this example:
- `podSelector`: Selects the pods that this network policy should apply to.
- `ingress`: Defines the allowed traffic to the selected pods.

### Real-World Examples and Breaches

Recent breaches and vulnerabilities have highlighted the importance of securing Kubernetes services. For example, the `CVE-2021-25741` vulnerability in Kubernetes allowed attackers to bypass RBAC restrictions and gain unauthorized access to services.

#### Example: CVE-2021-25741

The `CVE-2021-25741` vulnerability in Kubernetes allowed attackers to bypass RBAC restrictions and gain unauthorized access to services. This vulnerability was exploited in several real-world attacks, highlighting the need for robust security measures.

#### How to Prevent / Defend

1. **Keep Kubernetes Up-to-Date**: Regularly update your Kubernetes cluster to the latest version to ensure you have the latest security patches.
2. **Implement RBAC**: Use Role-Based Access Control (RBAC) to restrict access to sensitive services.
3. **Monitor and Audit**: Regularly monitor and audit your Kubernetes cluster for suspicious activity.

### Conclusion

Kubernetes services are a critical component of the Kubernetes architecture, providing a stable network identity to a set of pods. Understanding the different types of services and how to secure them is essential for building reliable and secure applications in a Kubernetes cluster.

### Practice Labs

For hands-on practice with Kubernetes services, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges for learning Kubernetes security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

By completing these labs, you can gain practical experience with Kubernetes services and improve your skills in securing your applications.

---
<!-- nav -->
[[01-Introduction to Kubernetes Services|Introduction to Kubernetes Services]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/07-Kubernetes Services Overview And Types/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/07-Kubernetes Services Overview And Types/03-Practice Questions & Answers|Practice Questions & Answers]]

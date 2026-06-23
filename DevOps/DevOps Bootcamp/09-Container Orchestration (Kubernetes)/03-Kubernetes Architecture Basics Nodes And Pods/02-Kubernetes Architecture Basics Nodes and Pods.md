---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Architecture Basics: Nodes and Pods

### Introduction to Kubernetes Architecture

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. At its core, Kubernetes is designed to manage clusters of nodes, where each node runs one or more pods. A pod is the smallest deployable unit in Kubernetes, consisting of one or more containers that share the same network namespace and storage volumes.

### Nodes in Kubernetes

A **node** in Kubernetes is a worker machine in the cluster, which can be either a virtual or physical machine. Each node is managed by the Kubernetes master components and is responsible for running the pods scheduled to it. Nodes are typically part of a larger cluster, which allows for scalability and redundancy.

#### Components of a Node

Each node in a Kubernetes cluster must have the following components installed:

1. **Container Runtime**: This is the software that is responsible for running containers. Common container runtimes include Docker, containerd, and CRI-O. The choice of container runtime does not affect the functionality of Kubernetes, but it must be compatible with the Container Runtime Interface (CRI).

2. **Kubelet**: This is an agent that runs on each node and ensures that the containers defined in the pod manifests are running and healthy. Kubelet takes care of starting and stopping containers based on the instructions received from the Kubernetes API server.

3. **kube-proxy**: This is a network proxy that runs on each node and maintains network rules on the host. It also acts as a local load balancer for TCP and UDP traffic.

#### Example of a Node Configuration

Here is an example of a node configuration in a Kubernetes cluster:

```yaml
apiVersion: v1
kind: Node
metadata:
  name: node-1
spec:
  taints:
  - effect: NoSchedule
    key: dedicated
    value: db
```

In this example, `node-1` is configured with a taint that prevents pods from being scheduled unless they have a corresponding toleration.

### Pods in Kubernetes

A **pod** is the basic execution unit in Kubernetes. It represents a group of one or more containers that are tightly coupled and share the same resources. Containers within a pod share the same network namespace, meaning they can communicate with each other via localhost.

#### Pod Structure

A pod is defined by a pod specification (YAML or JSON format) that includes the following elements:

1. **Metadata**: Information about the pod, such as its name and labels.
2. **Spec**: The desired state of the pod, including the list of containers, their resources, and volumes.

Here is an example of a pod specification:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
spec:
  containers:
  - name: my-container
    image: my-image:latest
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

In this example, `my-pod` contains a single container named `my-container`, which uses the `my-image:latest` image. The container listens on port 80 and has resource requests and limits specified.

### Communication Between Pods

Communication between pods in a Kubernetes cluster is facilitated through **services**. Services act as load balancers that distribute traffic to the appropriate pods. They provide a stable IP address and DNS name for a set of pods.

#### Service Types

There are several types of services in Kubernetes:

1. **ClusterIP**: Exposes the service on a cluster-internal IP. This type makes the service only reachable from within the cluster.
2. **NodePort**: Exposes the service on each node’s IP at a static port. This type makes the service reachable from outside the cluster.
3. **LoadBalancer**: Exposes the service externally using a cloud provider’s load balancer.
4. **ExternalName**: Maps the service to an external DNS name by returning a CNAME record.

Here is an example of a service definition:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

In this example, `my-service` is a `ClusterIP` service that selects pods labeled with `app: my-app`.

### Kubelet and Its Role

The **Kubelet** is a critical component of each node in a Kubernetes cluster. It is responsible for ensuring that the containers described in the pod specifications are running and healthy. Kubelet communicates with the Kubernetes API server to receive instructions and report the status of the pods.

#### Kubelet Responsibilities

1. **Pod Management**: Kubelet manages the lifecycle of pods, including starting, stopping, and restarting containers.
2. **Resource Assignment**: Kubelet assigns resources such as CPU, memory, and storage to the containers.
3. **Health Checks**: Kubelet performs health checks on the containers and reports their status to the API server.

Here is an example of a Kubelet configuration:

```yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: cgroupfs
clusterDNS:
- 10.96.0.10
clusterDomain: cluster.local
```

In this example, the Kubelet is configured to use the `cgroupfs` driver and sets the DNS server to `10.96.0.10`.

### kube-proxy and Its Role

The **kube-proxy** is another essential component of each node in a Kubernetes cluster. It is responsible for maintaining network rules on the host and acts as a local load balancer for TCP and UDP traffic.

#### kube-proxy Responsibilities

1. **Network Rules**: kube-proxy maintains network rules on the host to allow communication between services and pods.
2. **Load Balancing**: kube-proxy balances traffic between the pods selected by a service.

Here is an example of a kube-proxy configuration:

```yaml
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: iptables
clusterCIDR: 10.244.0.0/16
```

In this example, the kube-proxy is configured to use the `iptables` mode and sets the cluster CIDR to `1.244.0.0/16`.

### Real-World Examples and Recent Breaches

Recent breaches involving Kubernetes include:

1. **CVE-2021-25741**: A vulnerability in the Kubernetes API server allowed attackers to bypass authentication and gain unauthorized access to the cluster.
2. **CVE-2021-25742**: Another vulnerability in the Kubernetes API server allowed attackers to escalate privileges and execute arbitrary commands.

These vulnerabilities highlight the importance of keeping Kubernetes components up to date and securing the API server.

### How to Prevent / Defend

To prevent and defend against attacks on Kubernetes clusters, follow these best practices:

1. **Keep Components Updated**: Regularly update Kubernetes components to the latest versions to patch known vulnerabilities.
2. **Secure the API Server**: Implement strong authentication and authorization mechanisms for the API server.
3. **Use Network Policies**: Define network policies to restrict traffic between pods and services.
4. **Monitor and Audit**: Continuously monitor the cluster for suspicious activity and regularly audit the configurations.

Here is an example of a secure configuration for a pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  labels:
    app: secure-app
spec:
  containers:
  - name: secure-container
    image: secure-image:latest
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    securityContext:
      runAsUser: 1000
      runAsGroup: 3000
      readOnlyRootFilesystem: true
```

In this example, the `secure-pod` is configured with a `securityContext` that specifies the user and group IDs and sets the root filesystem to read-only.

### Hands-On Labs

For hands-on practice with Kubernetes architecture basics, consider the following labs:

1. **Kubernetes Goat**: A hands-on lab that focuses on Kubernetes security and best practices.
2. **OWASP WrongSecrets**: A series of challenges that cover various aspects of Kubernetes security.

These labs provide practical experience with configuring and securing Kubernetes clusters.

### Conclusion

Understanding the architecture of Kubernetes, particularly the roles of nodes and pods, is crucial for managing containerized applications effectively. By mastering the concepts of Kubelet, kube-proxy, and services, you can ensure that your Kubernetes clusters are scalable, reliable, and secure.

---
<!-- nav -->
[[01-Introduction to Kubernetes Architecture|Introduction to Kubernetes Architecture]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/03-Kubernetes Architecture Basics Nodes And Pods/00-Overview|Overview]] | [[03-Kubernetes Cluster Architecture Basics Nodes and Pods|Kubernetes Cluster Architecture Basics Nodes and Pods]]

---
tags: [kubernetes, k8s, architecture, control-plane, nodes]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.10 K8s Architecture"
---

# Kubernetes Architecture — Control Plane, Nodes, Pods

## Introduction
Kubernetes (K8s) is a highly complex, distributed system designed to orchestrate containerized applications at scale. To effectively secure or exploit a Kubernetes cluster, a deep understanding of its architectural components and their interactions is mandatory. 

Kubernetes architecture follows a classic client-server model, divided into two primary logical segments: the **Control Plane** (the master/brain of the cluster) and the **Data Plane / Worker Nodes** (where the actual application workloads execute).

## The Architectural Blueprint

```text
+-----------------------------------------------------------------------+
|                       KUBERNETES CONTROL PLANE                        |
|                                                                       |
|   +----------------+      +-------------------+      +------------+   |
|   | Cloud Control  |      |   kube-scheduler  |      | Controller |   |
|   |    Manager     |      |                   |      |  Manager   |   |
|   +-------+--------+      +---------+---------+      +------+-----+   |
|           |                         |                       |         |
|           v                         v                       v         |
|   +---------------------------------------------------------------+   |
|   |                    kube-apiserver                             |   |
|   |             (The Central Communication Hub)                   |   |
|   +-------------------------------+-------------------------------+   |
|                                   |                                   |
|                                   v                                   |
|   +---------------------------------------------------------------+   |
|   |                        etcd (Key-Value Store)                 |   |
|   |               (The Source of Truth & Cluster State)           |   |
|   +---------------------------------------------------------------+   |
+-----------------------------------^-----------------------------------+
                                    | TLS / gRPC / HTTPS
+-----------------------------------------------------------------------+
|                            WORKER NODE 1                              |
|                                   |                                   |
|   +-------------------------------+-------------------------------+   |
|   |                            kubelet                            |   |
|   |               (The Node Agent / Process Manager)              |   |
|   +-------+-----------------------+-----------------------+-------+   |
|           |                       |                       |           |
|           v                       v                       v           |
|   +---------------+       +---------------+       +---------------+   |
|   |  Container    |       |  kube-proxy   |       |   Pod (App)   |   |
|   |  Runtime      |       |  (Networking) |       | [Container]   |   |
|   | (containerd)  |       |               |       | [Container]   |   |
|   +---------------+       +---------------+       +---------------+   |
+-----------------------------------------------------------------------+
```

## Deep Dive: The Control Plane

The Control Plane components make global decisions about the cluster (e.g., scheduling), detecting and responding to cluster events. From a security perspective, compromising the Control Plane is equivalent to domain admin compromise in an Active Directory environment.

### 1. kube-apiserver
The API Server is the heart of Kubernetes. It exposes the Kubernetes HTTP API. 
*   **Function**: It is the front-end for the Kubernetes control plane. Every single communication—whether from external users using `kubectl`, or internal components like the kubelet or scheduler—must go through the API Server. It handles authentication, authorization (RBAC), admission control, and API request validation.
*   **Security Implications**: If an attacker bypasses authentication on the API Server (e.g., via an anonymous access misconfiguration or a leaked cluster-admin token), they own the entire cluster. It is the most critical component to protect. It usually listens on port 6443.

### 2. etcd
`etcd` is a consistent, highly available, distributed key-value store used as Kubernetes' backing store for all cluster data.
*   **Function**: It stores the entire state of the cluster. This includes all configuration data, node status, and crucially, all Kubernetes Secrets.
*   **Security Implications**: By default, `etcd` data is not encrypted at rest. If an attacker gains filesystem access to the Control Plane node (or finds an exposed `etcd` client port, usually 2379/2380, without client certificate authentication), they can dump the entire database and extract all plaintext secrets, tokens, and configurations.

### 3. kube-scheduler
*   **Function**: The scheduler watches for newly created Pods that have no assigned Node, and selects a Node for them to run on based on resource requirements, hardware constraints, affinity/anti-affinity specifications, and taints/tolerations.
*   **Security Implications**: While rarely the primary target for a direct exploit, a compromised scheduler could be manipulated to schedule malicious pods onto sensitive nodes, bypassing intended isolation boundaries.

### 4. kube-controller-manager
*   **Function**: This component runs controller processes. Logically, each controller is a separate process, but to reduce complexity, they are all compiled into a single binary. Controllers include the Node controller (noticing when nodes go down), Replication controller (maintaining the correct number of pods), and ServiceAccount & Token controllers.
*   **Security Implications**: The Token Controller creates default accounts and API access tokens for new namespaces. Exploiting flaws in this logic can lead to privilege escalation.

## Deep Dive: The Data Plane (Worker Nodes)

Worker Nodes are the machines (VMs or physical servers) that run the containerized applications.

### 1. kubelet
The `kubelet` is the primary "node agent" that runs on each node.
*   **Function**: It registers the node with the `kube-apiserver`. It receives PodSpecs (primarily through the API Server) and ensures that the containers described in those PodSpecs are running and healthy. It interacts directly with the container runtime.
*   **Security Implications**: The `kubelet` exposes two ports. The read-only port (10255 - often disabled in modern clusters) leaks pod configuration data. The secure port (10250) allows full command execution. If an attacker finds port 10250 exposed without authentication (a classic misconfiguration, allowing anonymous access), they can execute `kubeletctl exec` commands on any pod running on that node, achieving immediate cluster-wide RCE.

### 2. kube-proxy
*   **Function**: `kube-proxy` is a network proxy that runs on each node in your cluster, implementing part of the Kubernetes Service concept. It maintains network rules on nodes (usually via iptables or IPVS). These rules allow network communication to your Pods from network sessions inside or outside of your cluster.
*   **Security Implications**: Vulnerabilities in `kube-proxy` or underlying iptables implementations can lead to internal traffic interception, Man-in-the-Middle attacks between microservices, or cluster IP spoofing.

### 3. Container Runtime
*   **Function**: The software that is responsible for running containers (e.g., containerd, CRI-O, Docker Engine). Kubernetes interfaces with the runtime via the Container Runtime Interface (CRI).
*   **Security Implications**: Vulnerabilities in the runtime itself (e.g., runc vulnerabilities like CVE-2019-5736) allow for container escapes, turning a compromised pod into a compromised worker node.

### 4. Pods
A Pod is the smallest, most basic deployable object in Kubernetes.
*   **Function**: A Pod represents a single instance of a running process in your cluster. Pods contain one or more containers, such as Docker containers. When a Pod runs multiple containers, the containers are managed as a single entity and share the Pod's resources (like the network namespace and IP address).
*   **Security Implications**: Pods are the initial beachhead for attackers. Applications running in pods are targeted via web vulnerabilities (RCE, SSRF). Once a pod is compromised, the attacker attempts to pivot to the node (container escape) or to the API server (abusing service account tokens).

## The Attack Surface Summary

Understanding the architecture reveals the primary attack vectors:
1.  **External Attack Surface**: Exposed API Server (6443), exposed `etcd` (2379), exposed NodePorts, exposed Ingress controllers.
2.  **Internal Attack Surface (Post-Compromise)**: An attacker inside a Pod will target the internal API Server IP (usually `10.96.0.1`), the local `kubelet` (port 10250), the cloud provider metadata service (e.g., `169.254.169.254`), or attempt lateral movement to other pods.
3.  **Supply Chain**: Malicious images deployed by the scheduler to the nodes.

## Chaining Opportunities
*   [[11 - Kubernetes RBAC — ClusterAdmin Misconfig]]: A compromised API server token from a pod allows interaction with the Control Plane components, requiring RBAC exploitation to elevate privileges.
*   [[12 - Exposed Kubernetes Dashboard]]: The dashboard communicates directly with the `kube-apiserver`. If exposed, it provides a GUI for architectural manipulation.
*   [[07 - Container Escape — Kernel Exploits]]: Exploiting the Worker Node's shared kernel allows an attacker to bypass the `kubelet` and container runtime completely.

## Related Notes
*   [[13 - Bypassing Kubernetes Pod Security Policies]]
*   [[15 - Kubelet API Exploitation and Anonymous Auth]]
*   [[16 - ETCD Data Extraction and Encryption at Rest]]

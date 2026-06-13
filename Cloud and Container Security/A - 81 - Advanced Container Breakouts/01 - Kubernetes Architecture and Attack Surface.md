---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.01 Kubernetes Architecture and Attack Surface"
---

# Kubernetes Architecture and Attack Surface

## Introduction to Kubernetes Architecture

Kubernetes (often abbreviated as K8s) is the industry standard for container orchestration. It provides a robust, resilient, and highly scalable framework for deploying, managing, and operating containerized applications at scale. While the abstractions Kubernetes provides offer immense power and flexibility for developers and system operators, the inherent complexity of the ecosystem introduces a massive, multifaceted attack surface. 

Understanding the granular details of Kubernetes architecture is an absolute prerequisite for any security professional, penetration tester, or cloud security researcher aiming to perform vulnerability assessments, red team operations, or threat hunting within cloud-native environments. Attackers do not attack Kubernetes as a single monolithic entity; they target the seams, misconfigurations, and specific components within its distributed architecture.

In a typical Kubernetes deployment, the architecture is logically and physically divided into two primary planes: the **Control Plane** (the master components that make global decisions about the cluster) and the **Data Plane** or Worker Nodes (where the actual application workloads execute). Understanding the interaction between these planes is crucial for identifying lateral movement and privilege escalation paths.

## Deep Dive: The Control Plane

The Control Plane is the "brain" of the Kubernetes cluster. It maintains the desired state of the cluster, schedules workloads, and stores all cluster configuration data. Compromising any component within the Control Plane typically results in total cluster compromise.

### 1. kube-apiserver
The `kube-apiserver` is the central management entity and the front-end for the Kubernetes control plane. It is the only component that interacts directly with the `etcd` storage backend. It exposes the Kubernetes API over HTTPS and handles:
- **Authentication:** Verifying who the user or service account is (via client certificates, bearer tokens, OIDC, etc.).
- **Authorization:** Verifying what the user can do (typically via Role-Based Access Control - RBAC).
- **Admission Control:** Mutating or validating requests before they are persisted to etcd (e.g., Pod Security Admission, Mutating Webhooks).
- **API Validation:** Ensuring the payloads are well-formed.
The API server is the primary entry point for administrators (via `kubectl`), internal cluster components, and end-users.

### 2. etcd
`etcd` is a consistent, highly-available, distributed key-value store used as Kubernetes' primary backing store for all cluster data. It stores the complete state of the cluster, including:
- All pod definitions and statuses.
- All secrets, configmaps, and service account tokens.
- All cluster roles and role bindings.
If an attacker gains direct, unauthenticated access to etcd, they can bypass the API server entirely, read all cluster secrets, and modify the cluster state (e.g., granting themselves cluster-admin privileges).

### 3. kube-scheduler
The `kube-scheduler` watches for newly created Pods that have no assigned node, and selects an optimal node for them to run on. It considers resource requirements, hardware/software/policy constraints, affinity and anti-affinity specifications, data locality, and inter-workload interference.

### 4. kube-controller-manager
The `kube-controller-manager` runs core controller processes. In Kubernetes, a controller is a control loop that watches the shared state of the cluster through the API server and makes changes attempting to move the current state towards the desired state. Examples include:
- **Node Controller:** Notices and responds when nodes go down.
- **Job Controller:** Watches for Job objects and creates Pods to run them to completion.
- **ServiceAccount Controller:** Creates default ServiceAccounts and API access tokens for new namespaces.

### 5. cloud-controller-manager
This component embeds cloud-specific control logic, linking the Kubernetes cluster into the cloud provider's API (e.g., AWS, GCP, Azure). It allows the cluster to interact with cloud resources like load balancers, network routes, and block storage.

## Deep Dive: The Worker Nodes (Data Plane)

Worker Nodes are the physical servers or virtual machines that actually execute the application containers. Each node runs a set of essential components.

### 1. kubelet
The `kubelet` is the primary "node agent" that runs on every node in the cluster. It ensures that containers are running and healthy inside a Pod. The kubelet receives PodSpecs from the API server and uses the Container Runtime Interface (CRI) to instruct the container runtime to pull images and start containers. The kubelet also exposes its own API (typically on port 10250) for log retrieval, exec commands, and metrics.

### 2. kube-proxy
The `kube-proxy` is a network proxy that runs on each node, implementing part of the Kubernetes Service concept. It maintains network routing rules (often using `iptables` or `IPVS`) on nodes, allowing network communication to your Pods from network sessions inside or outside of your cluster.

### 3. Container Runtime
The container runtime is the underlying software responsible for pulling container images and running containers. Modern Kubernetes clusters use runtimes that conform to the Container Runtime Interface (CRI), such as `containerd` or `CRI-O`. (Note: Docker runtime via dockershim was deprecated and removed in recent Kubernetes versions, though `containerd` relies on the same underlying Linux primitives).

## Detailed ASCII Architecture Diagram

Below is a detailed visualization of the Kubernetes architecture, demonstrating the flow of communication, network boundaries, and potential interception points for an attacker:

```text
                                  +-----------------------------------------------------+
                                  |                 Control Plane (Master Node)         |
                                  |                                                     |
  +------------------+            |   +-------------------+       +-----------------+   |
  | External Users / |---HTTPS--->|   |   kube-apiserver  |<=====>|      etcd       |   |
  | Administrators   |   (6443)   |   | (AuthN/AuthZ/Adm) |       | (Key-Value DB)  |   |
  | (kubectl, API)   |            |   +-------------------+       |     (2379)      |   |
  +------------------+            |      ^    ^       ^           +-----------------+   |
                                  |      |    |       |                                 |
                                  |      |    |       +------------------------+        |
                                  |      v    v                                v        |
                                  | +---------------+                 +---------------+ |
                                  | |kube-scheduler |                 |kube-controller| |
                                  | |   (10259)     |                 |   manager     | |
                                  | +---------------+                 +---------------+ |
                                  +-----------------------------------------------------+
                                         ^      ^
                                         |      |  (mTLS / API Server Communication)
                                         |      |
                    +--------------------+      +--------------------+
                    |                                                |
                    v                                                v
  +-----------------------------------+            +-----------------------------------+
  | Worker Node 1                     |            | Worker Node N                     |
  |                                   |            |                                   |
  |  +---------+         +---------+  |            |  +---------+         +---------+  |
  |  | kubelet |<---CRI->| Runtime |  |            |  | kubelet |<---CRI->| Runtime |  |
  |  | (10250) |         |(containerd)|            |  | (10250) |         |(containerd)|
  |  +---------+         +---------+  |            |  +---------+         +---------+  |
  |       |                   |       |            |       |                   |       |
  |       v                   v       |            |       v                   v       |
  |  +---------+         +---------+  |            |  +---------+         +---------+  |
  |  |  Pod 1  |         |  Pod 2  |  |            |  |  Pod 3  |         |  Pod N  |  |
  |  | [App A] |         | [App B] |  |            |  | [App C] |         | [App D] |  |
  |  +---------+         +---------+  |            |  +---------+         +---------+  |
  |                                   |            |                                   |
  |  +-----------------------------+  |            |  +-----------------------------+  |
  |  |        kube-proxy           |  |            |  |        kube-proxy           |  |
  |  |   (iptables / IPVS rules)   |  |            |  |   (iptables / IPVS rules)   |  |
  |  +-----------------------------+  |            |  +-----------------------------+  |
  +-----------------------------------+            +-----------------------------------+
                   |                                                 |
                   +------------------+------------------------------+
                                      |
                            Container Network Interface (CNI)
                            (e.g., Calico, Flannel, Cilium)
```

## Expanding the Attack Surface

The attack surface in a Kubernetes environment can be broadly categorized into several distinct vectors. A successful, advanced compromise almost always involves chaining minor misconfigurations or vulnerabilities across these different boundaries.

### 1. Control Plane Attack Vectors
- **API Server Exposure:** If the `kube-apiserver` is exposed to the public internet without strict source IP allow-listing, it becomes a prime target. Even with authentication enabled, exposed API servers are vulnerable to unauthenticated endpoints (like older health check paths), zero-day CVEs in the API server itself, or basic credential stuffing if weak authentication mechanisms (like basic auth or static tokens) are enabled.
- **Etcd Exposure:** Etcd operates on port 2379 (client requests) and 2380 (peer communication). If an attacker can reach etcd over the network and client-certificate authentication is not enforced, they can dump the entire database. This contains all cluster configurations, ServiceAccount tokens, and user-defined Secrets in plaintext (unless encryption at rest is explicitly configured).
  ```bash
  # Example command to dump all secrets if etcd is exposed without auth:
  etcdctl --endpoints=http://<etcd-ip>:2379 get /registry/secrets --prefix --keys-only
  # To retrieve a specific secret payload:
  etcdctl --endpoints=http://<etcd-ip>:2379 get /registry/secrets/default/my-database-secret
  ```
- **Controller Manager / Scheduler:** These components run with highly privileged internal service accounts. Exploiting a vulnerability in a custom controller (or an operator) can lead to arbitrary object manipulation.

### 2. Worker Node Attack Vectors
- **Unauthenticated Kubelet API (Port 10250/10255):** The kubelet exposes an API for the API server to control pods, execute commands, and fetch logs. If `anonymous-auth` is enabled and authorization is permissive (e.g., `AlwaysAllow`), an attacker can interact directly with the kubelet. This bypasses the API server entirely and allows direct command execution (`/exec`) inside any pod running on that specific node. Port 10255 is the read-only port that historically leaks pod and node configuration data.
- **Container Runtime Socket:** If a container is granted access to the underlying container runtime socket (e.g., mounting `/var/run/docker.sock` or `/run/containerd/containerd.sock`), the isolated container can directly communicate with the host's runtime daemon. The attacker can instruct the daemon to spawn a new, fully privileged container that mounts the root filesystem of the host, completely breaking out of the container isolation.

### 3. Application and Pod Attack Vectors
- **Vulnerable Applications:** The most common initial entry point into a cluster. An RCE, SSRF, or LFI in a web application hosted inside a Pod grants the attacker a foothold in the containerized environment.
- **Service Account Token Abuse:** By default, Kubernetes automounts a ServiceAccount token into every Pod at `/var/run/secrets/kubernetes.io/serviceaccount/token`. If the application is compromised, the attacker can extract this token and use it to interact with the API server. The impact is strictly bounded by the RBAC permissions assigned to that specific ServiceAccount. If the account is over-privileged (e.g., capable of reading secrets or creating new pods), the attacker can rapidly escalate privileges.
- **Cloud Metadata Services:** If the cluster runs on a managed cloud provider (AWS EKS, GCP GKE, Azure AKS), a compromised pod might be able to reach the cloud provider's Instance Metadata Service (IMDS).
  ```bash
  # Attempting to fetch AWS IAM credentials from within a Pod
  curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
  ```
  If successful, this leaks the underlying node's IAM role credentials, allowing the attacker to pivot from the Kubernetes cluster to the broader cloud infrastructure environment.

### 4. Network Architecture and Lateral Movement
- **Missing Network Policies:** By default, Kubernetes operates on a "flat network" model where any pod can communicate with any other pod in the cluster, regardless of namespaces. A compromise in a frontend pod allows unrestricted lateral movement to backend pods, databases, and internal services unless explicitly blocked by a well-defined `NetworkPolicy` restricting ingress and egress traffic.
- **Man-in-the-Middle (MitM) Attacks:** If mutual TLS (mTLS) is not enforced between microservices (often implemented via service meshes like Istio or Linkerd), an attacker who compromises a worker node or achieves network interception within the CNI can sniff unencrypted traffic traversing the cluster, intercepting sensitive tokens and data.

### 5. Supply Chain and Image Security
- **Malicious Images:** Images pulled from public, unverified registries may contain embedded backdoors, malware, or crypto-miners.
- **Vulnerable Base Images:** Using outdated base images or libraries introduces known OS-level CVEs into the cluster environment. Without continuous vulnerability scanning in the CI/CD pipeline, these vulnerabilities easily reach production.

## Securing the Architecture (Defensive Measures)

Defending the Kubernetes architecture requires a defense-in-depth approach:
1.  **Protect the Control Plane:** Never expose the API server directly to the internet. Use private clusters (Private EKS/GKE/AKS) where the API server is only accessible from an internal VPC or via a secure VPN/bastion host.
2.  **Harden Etcd:** Ensure etcd communicates over TLS and strictly enforces client certificate authentication. Implement encryption at rest for etcd to protect secret data if the underlying storage volume is compromised.
3.  **Implement Strict RBAC:** Adhere to the principle of least privilege. Do not use default service accounts. Create dedicated service accounts for each workload with minimal permissions. Avoid granting `cluster-admin` access.
4.  **Enforce Network Policies:** Implement a default-deny network policy for all namespaces and explicitly allow only required traffic between specific pods.
5.  **Secure the Kubelet:** Disable anonymous authentication on the kubelet (`--anonymous-auth=false`) and ensure authorization is delegated to the API server via Webhook (`--authorization-mode=Webhook`).
6.  **Use Admission Controllers:** Enforce security standards using Pod Security Admission (PSA) or third-party admission controllers like OPA Gatekeeper or Kyverno to block privileged containers, host mounts, and dangerous capabilities.

## Real-World Attack Scenario

Consider an organization deploying a legacy Node.js application on an Azure Kubernetes Service (AKS) cluster. The attack lifecycle unfolds as follows:
1. **Initial Access:** The Node.js application suffers from an insecure deserialization vulnerability. An attacker sends a crafted payload and gains remote code execution within the context of the container.
2. **Execution & Discovery:** The attacker explores the container environment, identifying it as a Kubernetes pod via environment variables (`KUBERNETES_SERVICE_HOST`, `KUBERNETES_PORT`) and mounted service account secrets.
3. **Privilege Escalation:** The attacker reads the ServiceAccount token located at `/var/run/secrets/kubernetes.io/serviceaccount/token`. By querying the API Server and checking permissions (`kubectl auth can-i --list`), they discover the token is bound to a `ClusterRole` that inadvertently permits `pods/exec` and `secrets/get` across multiple namespaces.
4. **Lateral Movement:** Using the stolen token, the attacker queries the API server for all cluster secrets, obtaining sensitive database credentials and third-party API keys. They then use the `pods/exec` permission to establish a reverse shell in a different, highly secure pod (e.g., a payment processing microservice) that has direct network access to the internal payment gateway.
5. **Data Exfiltration and Cloud Pivot:** From the payment pod, the attacker queries the sensitive backend databases using the extracted credentials and exfiltrates the data over standard HTTPS. Furthermore, the attacker queries the Azure IMDS endpoint, extracts the node's Managed Identity token, and uses it to pivot into the Azure environment to access Key Vaults.

## Chaining Opportunities

A thorough understanding of the architecture is the foundational element required for chaining complex attacks:
- **SSRF to Cloud Metadata:** A Server-Side Request Forgery (SSRF) in a Pod application can be directed at the IMDS endpoint (`169.254.169.254`) to steal node IAM credentials, leading to full cloud account compromise.
- **Kubelet Exposure to Full Cluster Takeover:** Finding an exposed port 10250 with anonymous auth allows direct command execution. The attacker execs into a `kube-system` pod (like `kube-proxy` or `calico-node`), steals its highly privileged service account token, and leverages it to gain `cluster-admin` rights.
- **RBAC Misconfiguration to Node Compromise:** Exploiting an overly permissive RBAC role (e.g., permission to `create pods` in the `kube-system` namespace) to deploy a malicious privileged DaemonSet. The DaemonSet mounts the host root filesystem (`/`), granting the attacker full root SSH access over every worker node in the cluster.

## Related Notes
- [[02 - Enumerating Kubernetes Clusters Kubelet API]]
- [[03 - Exploiting Unauthenticated Kubelet Endpoints]]
- [[04 - RBAC Exploitation and Privilege Escalation in K8s]]
- [[05 - Advanced Docker Breakouts Capabilities and Mounts]]

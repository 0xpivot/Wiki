---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.02 Enumerating Kubernetes Clusters Kubelet API"
---

# Enumerating Kubernetes Clusters and the Kubelet API

## Introduction to Kubernetes Enumeration

When an attacker or a penetration tester first gains execution within a containerized environment (often via a web application vulnerability like RCE or SSRF), the immediate priority shifts from application exploitation to environment enumeration. Identifying whether the compromised host is a standalone Docker container, a managed Kubernetes Pod, or a heavily restricted sandbox is the crucial first step. 

Once Kubernetes is identified as the underlying orchestration platform, the objective becomes mapping the cluster's internal topology, discovering exposed administrative APIs (like the API Server or the Kubelet), identifying the permissions assigned to the compromised Pod, and locating sensitive secrets or cloud metadata endpoints. Robust enumeration forms the bedrock of all subsequent privilege escalation and lateral movement strategies in a Kubernetes cluster.

## Initial Discovery: Am I in Kubernetes?

The first phase of enumeration occurs locally within the compromised container. Kubernetes injects specific artifacts into every Pod it schedules, making it relatively trivial to detect its presence.

### 1. Environment Variables
Kubernetes automatically injects environment variables into Pods for every active Service in the same namespace, as well as core cluster routing information.
```bash
# Check for Kubernetes environment variables
env | grep -i kube
```
Typical output indicating a Kubernetes environment:
```text
KUBERNETES_SERVICE_PORT_HTTPS=443
KUBERNETES_SERVICE_PORT=443
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
KUBERNETES_PORT_443_TCP_PROTO=tcp
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
KUBERNETES_SERVICE_HOST=10.96.0.1
KUBERNETES_PORT=tcp://10.96.0.1:443
KUBERNETES_PORT_443_TCP_PORT=443
```
The `KUBERNETES_SERVICE_HOST` variable points to the internal IP address of the Kubernetes API Server, providing an immediate target for further interaction.

### 2. Service Account Tokens
Unless explicitly disabled by the developer (`automountServiceAccountToken: false`), Kubernetes mounts a JSON Web Token (JWT), a CA certificate, and a namespace identifier into every Pod. These are used by the Pod to authenticate against the API Server.
```bash
# Verify the presence of the mounted secrets
ls -la /var/run/secrets/kubernetes.io/serviceaccount/
```
Output:
```text
ca.crt
namespace
token
```
The `token` file is the critical artifact. It is the identity of the Pod within the cluster. Extracting and decoding this JWT (e.g., via jwt.io or standard base64 decoding tools) reveals the ServiceAccount name and its associated namespace.

### 3. Filesystem and Mounts
Checking mounted filesystems can reveal if the container has access to sensitive host paths or if specific Kubernetes storage classes (like CSI drivers or ConfigMaps) are in use.
```bash
mount | grep -i kubernetes
cat /proc/mounts
```

## Enumerating the API Server

Once the `KUBERNETES_SERVICE_HOST` and the Service Account token are acquired, the attacker attempts to interact with the API Server to determine their privileges. The API Server typically listens on port 443 (internal) or 6443.

### 1. The `auth can-i` Query
The most critical enumeration step is asking the API Server, "What am I allowed to do?". Kubernetes provides the SelfSubjectAccessReview API for this exact purpose, commonly accessed via `kubectl auth can-i`.
If `kubectl` is not installed in the container, the attacker can either download a static binary of `kubectl` or use standard `curl` commands.

Using curl to hit the API Server:
```bash
export APISERVER="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT_HTTPS}"
export TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
export CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Test basic access to the API server
curl --cacert $CACERT --header "Authorization: Bearer $TOKEN" -X GET ${APISERVER}/api/v1/namespaces/default/pods
```

If the attacker drops a `kubectl` binary into the pod:
```bash
# Configure kubectl to use the local token
kubectl config set-cluster local --server=$APISERVER --certificate-authority=$CACERT
kubectl config set-credentials local-user --token=$TOKEN
kubectl config set-context local --cluster=local --user=local-user
kubectl config use-context local

# Check permissions
kubectl auth can-i --list
```
The output of `kubectl auth can-i --list` dictates the attacker's next move. If they see permissions like `create pods`, `get secrets`, `create clusterrolebindings`, or `impersonate`, they have a direct path to privilege escalation.

## Enumerating the Kubelet API

The Kubelet is the node agent running on every worker node. It communicates with the API Server but also exposes its own REST API. Enumerating the Kubelet is crucial because misconfigurations here allow an attacker to bypass the API Server entirely.

### Kubelet Ports Overview
- **10250 (HTTPS):** The primary Kubelet API. Used by the API server to control pods, fetch logs, and execute commands. This port requires authentication by default, but if `anonymous-auth=true` is set, it becomes highly vulnerable.
- **10255 (HTTP):** The read-only Kubelet port. Historically used for health checks and metrics. It does not allow code execution but leaks massive amounts of configuration data without any authentication. (Deprecated in modern K8s but still found in older clusters).
- **10248 (HTTP):** Kubelet healthz endpoint.

### Discovering the Underlying Node IP
To query the Kubelet, the attacker must know the IP address of the node hosting their Pod. This can be found via:
1. Environment variables (if downward API is used).
2. Querying cloud metadata services (e.g., `curl http://169.254.169.254/latest/meta-data/local-ipv4`).
3. Network scanning the local subnet.

```bash
# Example internal subnet scan for Kubelet ports
nmap -p 10250,10255 10.0.0.0/24 -T4 --open
```

### Enumerating Kubelet Endpoints
If port 10250 is exposed with anonymous authentication, or if port 10255 is accessible, the attacker can query several highly informative endpoints:

**1. The `/pods` Endpoint**
Retrieves the configuration of all Pods running on that specific node. This JSON response is a goldmine of information, containing environment variables, volume mounts, image names, and secret names.
```bash
# Querying the read-only port (if exposed)
curl http://<node-ip>:10255/pods | jq .

# Querying the primary port (if anonymous auth is enabled)
curl -k https://<node-ip>:10250/pods | jq .
```

**2. The `/spec` Endpoint**
Retrieves machine and system specifications.
```bash
curl -k https://<node-ip>:10250/spec
```

**3. The `/metrics` Endpoint**
Often exposed for Prometheus scraping. It leaks system metrics, container names, and sometimes sensitive labels.
```bash
curl -k https://<node-ip>:10250/metrics
```

## Detailed ASCII Architecture Diagram

The diagram below illustrates the enumeration flow from a compromised container outward into the cluster infrastructure.

```text
  +-------------+                 +---------------------+
  |   Attacker  |                 |    Compromised Pod  |
  |  (External) |                 |    (Initial Access) |
  +-------------+                 +---------------------+
         |                                   |
         | (1) Exploit Web App Vuln          | (2) Extract Env Vars & Token
         v                                   v
  +-------------+                 +-----------------------------------+
  | Application |                 | /var/run/secrets/kubernetes.io/.. |
  |   (RCE)     |                 |  - token (JWT)                    |
  +-------------+                 |  - ca.crt                         |
         |                        |  - namespace                      |
         |                        +-----------------------------------+
         |                                   |
         | (3) Network Scan Internal Subnet  | (4) Use Token against API Server
         v                                   v
  +-------------------------------------------------------------------+
  |                   Internal Kubernetes Network                     |
  |                                                                   |
  |  +----------------+           +-------------------------------+   |
  |  | kube-apiserver |<----------|  curl / kubectl auth can-i    |   |
  |  |   (Port 443)   |           |  (Checks RBAC Permissions)    |   |
  |  +----------------+           +-------------------------------+   |
  |          ^                                                        |
  |          | (5) Query Kubelet API directly (Bypass API Server)     |
  |          v                                                        |
  |  +----------------+           +-------------------------------+   |
  |  |   Kubelet      |---------->|   JSON Response (/pods)       |   |
  |  | (Port 10250)   |           |   - Env Vars, Secrets, Mounts |   |
  |  +----------------+           +-------------------------------+   |
  +-------------------------------------------------------------------+
```

## Automated Enumeration Tools

Manual enumeration is thorough but slow. Penetration testers frequently rely on specialized tools designed to map out Kubernetes environments rapidly:

1. **Am I Isolated (amicontained):** A lightweight tool that reports the container runtime, enabled capabilities, AppArmor/Seccomp profiles, and namespace restrictions.
   ```bash
   ./amicontained
   ```
2. **Kube-Hunter:** An open-source tool by Aqua Security that hunts for security weaknesses in Kubernetes clusters. It can be run from outside the cluster or deployed as a Pod to simulate an internal compromise.
   ```bash
   python3 kube-hunter.py --pod
   ```
3. **Peirates:** A Kubernetes penetration testing tool enabling an attacker to escalate privileges and pivot through a cluster. It automates the extraction of service account tokens and tests for risky RBAC permissions automatically.
4. **KDigger:** A context discovery tool for Kubernetes environments, pulling information about the local environment, tokens, capabilities, and API access.
   ```bash
   kdigger discover
   ```
5. **Trivy / Traitor:** Used to identify local node vulnerabilities or automatically exploit known container breakouts and RBAC misconfigurations.

## Defensive Countermeasures

Preventing effective enumeration is difficult since many features (like environment variables) are required for functionality, but limiting the blast radius is achievable:
- **Disable Automounting Service Account Tokens:** If a Pod does not need to speak to the API server, set `automountServiceAccountToken: false` in the Pod spec.
- **Network Policies:** Implement strict egress network policies to prevent a compromised Pod from scanning the internal network or reaching the Kubelet API/API Server if it doesn't explicitly require it.
- **Secure the Kubelet:** Ensure `--anonymous-auth=false` and `--authorization-mode=Webhook` are set on all node Kubelets to prevent unauthorized `/pods` querying.
- **Block Cloud Metadata:** Use Network Policies to drop traffic destined for `169.254.169.254` to prevent cloud credential extraction.

## Real-World Attack Scenario

An attacker discovers an unauthenticated Grafana dashboard exposed to the internet. They leverage CVE-2021-43798 (Path Traversal) to read arbitrary files from the server. They read `/var/run/secrets/kubernetes.io/serviceaccount/token` and `/var/run/secrets/kubernetes.io/serviceaccount/namespace`. 

Equipped with the token, the attacker realizes they are inside a Kubernetes cluster. They use the `curl` command against the API server's public endpoint (which they found via certificate transparency logs for the company). They issue an API request to the `/apis/authorization.k8s.io/v1/selfsubjectaccessreviews` endpoint. The API server responds, confirming the token belongs to the default ServiceAccount in the `monitoring` namespace, but surprisingly, someone granted this account the `ClusterRole` of `view`, allowing the attacker to read the configuration of every Pod across the entire cluster. The attacker uses this read access to map out the entire internal architecture, identifying databases, internal APIs, and poorly secured legacy applications.

## Chaining Opportunities

Enumeration is inherently chained with exploitation:
- **Token Discovery to API Abuse:** Discovering a mounted ServiceAccount token leads directly to interacting with the API server to perform RBAC exploitation.
- **Kubelet Discovery to RCE:** Discovering an open port 10250 with anonymous access during an internal Nmap scan leads directly to unauthenticated RCE on other pods via the `/exec` endpoint.
- **Pod Spec Extraction to Credential Theft:** Querying the read-only Kubelet port (`10255`) and parsing the `/pods` output can reveal hardcoded database passwords passed as environment variables in poorly configured deployment manifests.

## Related Notes
- [[01 - Kubernetes Architecture and Attack Surface]]
- [[03 - Exploiting Unauthenticated Kubelet Endpoints]]
- [[04 - RBAC Exploitation and Privilege Escalation in K8s]]
- [[05 - Advanced Docker Breakouts Capabilities and Mounts]]

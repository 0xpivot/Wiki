---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.08 Lateral Movement in Kubernetes Pod to Pod"
---

# 81.08 Lateral Movement in Kubernetes Pod to Pod

## 1. Introduction

Once an attacker compromises a single container within a Kubernetes cluster (e.g., via a Remote Code Execution vulnerability in a web application), the next objective is lateral movement. In Kubernetes, the internal network is flat by default. Every pod can communicate with every other pod across all namespaces unless explicitly restricted by Network Policies.

Pod-to-Pod lateral movement involves network reconnaissance, service discovery, exploiting internal services, and leveraging weak authentication mechanisms that developers often assume are protected because they reside "behind the firewall."

## 2. Kubernetes Networking Model

To execute lateral movement, an attacker must understand the Container Network Interface (CNI). CNIs like Flannel, Calico, or Cilium manage the overlay network.
- **Flat Overlay**: Pods are assigned IPs from a cluster-wide CIDR block. A pod on Node A can ping a pod on Node B using its pod IP.
- **Services**: Kubernetes Services provide stable IP addresses (ClusterIPs) that load-balance traffic to dynamic pod IPs.
- **Kube-DNS / CoreDNS**: Provides service discovery. A pod can resolve internal services using names like `service-name.namespace.svc.cluster.local`.

## 3. ASCII Diagram: Lateral Movement Paths

```text
                               Kubernetes Cluster
+--------------------------------------------------------------------------------+
|                                                                                |
|  Namespace: frontend                        Namespace: backend                 |
|  +------------------------+                 +-------------------------------+  |
|  | Compromised Pod        |                 | Target Pod (Database)         |  |
|  | IP: 10.244.1.5         |  2. Connects to | IP: 10.244.2.10               |  |
|  |                        |---------------->| Port: 5432 (Postgres)         |  |
|  |                        |  (No Auth, Default| Default Password used       |  |
|  +------------------------+  Network Policy) +-------------------------------+  |
|           |                                                                    |
|           | 1. DNS Query                                                       |
|           v                                                                    |
|  +------------------------+                 Namespace: kube-system             |
|  | CoreDNS Pod            |                 +-------------------------------+  |
|  | IP: 10.96.0.10         |                 | Tiller / Internal Dashboard   |  |
|  | (Resolves db.backend)  |                 | IP: 10.244.0.8                |  |
|  +------------------------+                 | Port: 44134 / 8080            |  |
|                                             +-------------------------------+  |
|                                                     ^                          |
|                                                     | 3. Exploit internal tool |
+-----------------------------------------------------|--------------------------+
                                                      |
                 From Compromised Pod ----------------+
```

## 4. Reconnaissance and Discovery

From the initially compromised pod, the attacker maps the internal network.

### 4.1 Environment Variables
Kubernetes injects environment variables into pods for services running in the same namespace.
```bash
env | grep _TCP
```
Output might reveal internal services:
```text
REDIS_MASTER_SERVICE_PORT_6379_TCP_ADDR=10.96.105.14
REDIS_MASTER_SERVICE_PORT_6379_TCP_PORT=6379
```

### 4.2 DNS Enumeration
Attackers query CoreDNS to find services across namespaces. They can bruteforce common service names and namespaces.
```bash
# Checking if a specific service exists in another namespace
nslookup mongodb.database.svc.cluster.local

# Brute-forcing subdomains with a static binary like massdns or custom scripts
```

### 4.3 Network Scanning
Since standard tools like `nmap` are rarely installed in production container images, attackers often upload static binaries or use built-in tools like `nc`, `curl`, or bash `/dev/tcp`.

```bash
# Bash port scanner for an internal subnet
for ip in $(seq 1 254); do
  for port in 80 443 3306 5432 6379 8080; do
    timeout 1 bash -c "echo >/dev/tcp/10.244.1.$ip/$port" 2>/dev/null && echo "Open: 10.244.1.$ip:$port"
  done
done
```

## 5. Exploitation Vectors

### 5.1 Unauthenticated Internal Services
Developers frequently deploy services internally without authentication, relying on network isolation that doesn't exist by default in K8s.
- **Redis/Memcached**: Connecting without a password to dump application data or inject SSH keys.
- **Elasticsearch/Kibana**: Accessing logging infrastructure to read sensitive data or execute queries.
- **JMX/Java Debug Ports**: Exploiting remote class loading to achieve RCE on backend pods.

### 5.2 Internal Admin Panels
Many clusters host tools like the Kubernetes Dashboard, Grafana, or custom admin portals on `ClusterIP` services. These may have weak default credentials or unpatched CVEs.

### 5.3 Cleartext Protocol Sniffing
If the compromised pod runs with `CAP_NET_RAW` or `hostNetwork: true`, the attacker can run `tcpdump` to sniff traffic. Because pod-to-pod traffic is unencrypted by default (unless a Service Mesh with mTLS is used), the attacker can capture HTTP authorization headers, database queries, and cleartext credentials traversing the node.

### 5.4 Exploiting the Kubelet API
Every node runs a Kubelet. The Kubelet exposes a read-only API on port 10255 (if not disabled) and a read-write API on port 10250.
From a pod, an attacker can attempt to connect to the node's internal IP on port 10250.
```bash
curl -sk https://10.244.0.1:10250/pods
```
If the Kubelet is configured with `anonymous-auth=true`, the attacker can execute commands on *any* pod running on that specific node:
```bash
curl -sk -X POST "https://10.244.0.1:10250/run/kube-system/tiller-deploy-xxx/tiller" -d "cmd=ls -la /"
```

## 6. Bypassing Network Policies

Network Policies act as the "firewall" for Kubernetes, implemented by the CNI. If policies restrict outbound traffic from the compromised pod, attackers look for bypasses.

### 6.1 Bypassing via DNS (Port 53)
Even strict Network Policies usually allow egress on UDP/TCP port 53 to the CoreDNS service for name resolution. Attackers can use DNS tunneling (e.g., Iodine or dnscat2) to exfiltrate data or establish Command and Control (C2) channels.

### 6.2 Bypassing via Allowed Labels
Network Policies often whitelist traffic based on pod labels. 
If the attacker compromises a pod, and they find a vulnerability in the application that allows them to interact with the Kubernetes API (e.g., they stole a Service Account token with `patch pods` permission), they can modify the labels of their own pod to match the whitelist.

```bash
curl -XPATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/strategic-merge-patch+json" \
  -d '{"metadata":{"labels":{"role":"db-admin"}}}' \
  https://kubernetes.default.svc/api/v1/namespaces/default/pods/compromised-pod
```
Once relabeled, the CNI automatically updates the IPtables/eBPF rules, granting the pod access to the database network.

### 6.3 Service Mesh Manipulation
If a Service Mesh (like Istio) enforces mTLS and authorization policies, an attacker who achieves root inside a container might attack the sidecar proxy (e.g., Envoy). By stealing the sidecar's certificates from memory or the filesystem (`/etc/certs/`), the attacker can spoof their identity and bypass Istio AuthorizationPolicies.

## 7. Mitigation and Hardening

1. **Default-Deny Network Policies**: Implement a default-deny Network Policy in all namespaces. Explicitly whitelist ingress and egress paths using labels and namespaces.
2. **Mutual TLS (mTLS)**: Implement a Service Mesh (Istio, Linkerd) to encrypt all pod-to-pod traffic, preventing sniffing and verifying pod identities.
3. **Internal Authentication**: Never trust the internal network. Databases, message queues, and internal APIs must require strong authentication.
4. **Disable Kubelet Anonymous Auth**: Ensure `--anonymous-auth=false` is set on all Kubelets.
5. **Least Privilege**: Ensure pods run as non-root to prevent the installation of networking tools or the capture of packets via `CAP_NET_RAW`.

## 8. Chaining Opportunities

- **API Server Lateral Movement**: After laterally moving to a pod with a highly privileged Service Account token, use the token to escalate privileges as detailed in [[04 - Kubernetes RBAC Exploitation]].
- **Etcd Access**: Laterally move to the control plane network or find a pod with etcd client certs to perform [[09 - Secrets Extraction from etcd]].

## 9. Related Notes

- [[04 - Kubernetes RBAC Exploitation]]
- [[09 - Secrets Extraction from etcd]]
- [[03 - Attacking the Kubelet API]]

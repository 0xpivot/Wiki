---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.09 Secrets Extraction from etcd"
---

# 81.09 Secrets Extraction from etcd

## 1. Introduction to etcd

`etcd` is a strongly consistent, distributed key-value store used as Kubernetes' primary backing store for all cluster data. It holds the complete state of the cluster, including Pod configurations, Deployments, ConfigMaps, and critically, all Kubernetes Secrets and Service Account tokens.

Because `etcd` contains the "keys to the kingdom," it is a primary target during advanced Kubernetes penetration testing. If an attacker can interact with the `etcd` API, they can bypass the Kubernetes API Server entirely, ignore RBAC restrictions, and extract plaintext secrets or modify the cluster state directly.

## 2. etcd Architecture in Kubernetes

In a standard Kubernetes deployment (like kubeadm), `etcd` runs as a static pod on the Control Plane (master) nodes. It typically listens on:
- **Port 2379**: Client communication (used by the `kube-apiserver`).
- **Port 2380**: Server-to-server communication (used for etcd cluster consensus).

Access to `etcd` is protected by mutual TLS (mTLS). To query `etcd`, a client must present a valid client certificate signed by the `etcd` Certificate Authority (CA). 

## 3. ASCII Diagram: The etcd Attack Vector

```text
    Attacker
    +---------------------------------------------------+
    | 1. Exploits vulnerability (e.g., SSRF, Path       |
    |    Traversal) to read files from Control Plane    |
    |    Node OR compromises the Control Plane Node     |
    +---------------------------------------------------+
              |
              | 2. Steals etcd mTLS Certificates
              |    (/etc/kubernetes/pki/etcd/healthcheck-client.crt)
              v
    Control Plane Node
    +---------------------------------------------------+
    |  +---------------------------------------------+  |
    |  | etcd Pod (Port 2379)                        |  |
    |  |  [ Data: Secrets, Configs, State ]          |  |
    |  +---------------------------------------------+  |
    |          ^                                        |
    |          | 3. Attacker connects directly to etcd  |
    |          |    bypassing the kube-apiserver & RBAC |
    +----------|----------------------------------------+
               |
    +---------------------------------------------------+
    |  Kubernetes API Server (Bypassed)                 |
    |  - Enforces RBAC                                  |
    |  - Enforces Audit Logging                         |
    +---------------------------------------------------+
```

## 4. Acquiring etcd Client Certificates

To attack `etcd`, the attacker must first obtain the CA certificate, a client certificate, and a client key. These are typically found on the Control Plane nodes.

### 4.1 Exploiting Path Traversal / LFI
If an application or component running on the Control Plane node (or mounting host paths) has an LFI vulnerability, the attacker can read the certificates directly from the filesystem.

Common locations on a `kubeadm` provisioned cluster:
- CA Cert: `/etc/kubernetes/pki/etcd/ca.crt`
- Client Cert: `/etc/kubernetes/pki/etcd/healthcheck-client.crt` or `server.crt`
- Client Key: `/etc/kubernetes/pki/etcd/healthcheck-client.key` or `server.key`
- API Server etcd client cert: `/etc/kubernetes/pki/apiserver-etcd-client.crt`

### 4.2 Exploiting Misconfigured Pods
If a pod is scheduled on the master node and mounts `/etc/kubernetes/` or the root filesystem `/` (via `hostPath`), an attacker who compromises this pod can simply copy the certificates.

### 4.3 Unauthenticated etcd (Misconfiguration)
In older clusters or severely misconfigured custom setups, `etcd` might be exposed over HTTP or without require-client-cert validation. In this case, no certificates are needed.
```bash
curl http://<etcd-ip>:2379/version
```

## 5. Querying etcd and Extracting Secrets

Once the certificates are obtained, the attacker uses the `etcdctl` CLI tool to interact with the database. `etcdctl` can be downloaded directly to the compromised host or run remotely if `etcd` is exposed to the internal network.

### 5.1 Setting up etcdctl

Set environment variables to streamline `etcdctl` commands:
```bash
export ETCDCTL_API=3
export ETCDCTL_ENDPOINTS="https://127.0.0.1:2379"
export ETCDCTL_CACERT="/path/to/ca.crt"
export ETCDCTL_CERT="/path/to/client.crt"
export ETCDCTL_KEY="/path/to/client.key"
```

Verify connectivity:
```bash
etcdctl endpoint health
```

### 5.2 Extracting Kubernetes Secrets

Kubernetes stores data in `etcd` under the `/registry/` prefix. Secrets are stored under `/registry/secrets/<namespace>/<secret-name>`.

To list all secrets in the cluster:
```bash
etcdctl get /registry/secrets/ --prefix --keys-only
```

To extract a specific secret (e.g., the default Service Account token in the `kube-system` namespace):
```bash
etcdctl get /registry/secrets/kube-system/default-token-xxxxx
```

### 5.3 Parsing the Output

The output from `etcdctl` is a protobuf-encoded structure, but strings (like JWTs or base64 encoded data) are usually readable in plaintext within the binary output.

To cleanly extract and parse the secret data, attackers often use tools like `hexdump` or custom Python scripts using the `etcd3` library to deserialize the protobuf and extract the raw JSON/YAML.

```bash
# Quick extraction using grep/strings
etcdctl get /registry/secrets/default/my-db-secret | strings
```

## 6. Bypassing Encryption at Rest

To mitigate the impact of `etcd` compromise, Kubernetes supports Encryption at Rest. When enabled, secrets are encrypted by the API Server before being written to `etcd`.

If Encryption at Rest is active, querying the secret in `etcd` will return ciphertext prefixed with the encryption provider name (e.g., `k8s:enc:aescbc:v1:key1:...`).

### 6.1 Defeating Local Providers
If the cluster uses the `aescbc` or `secretbox` local providers, the encryption key is stored in a configuration file on the Control Plane node (typically `/etc/kubernetes/enc/enc.yaml`). 
Because the attacker already has file read access (necessary to steal the etcd certificates), they can simply read the `enc.yaml` file, extract the base64 encoded AES key, and decrypt the `etcd` payloads offline.

### 6.2 Defeating KMS Providers
If the cluster uses a Key Management Service (KMS) plugin (e.g., AWS KMS, Azure Key Vault), the encryption key is not stored locally. The API Server sends the data to the external KMS for encryption/decryption.

To bypass this, the attacker must either:
1. Steal the API Server's credentials used to authenticate to the KMS (e.g., AWS IAM instance profile on the master node).
2. Modify the API Server configuration directly (since they have root on the master node) to disable encryption, forcing the API server to write new secrets in plaintext.

## 7. Direct Cluster Manipulation

Extracting secrets is not the only risk. An attacker with write access to `etcd` can:
- **Create Backdoor Pods**: Write a malicious pod specification directly into `/registry/pods/`.
- **Elevate Privileges**: Modify a ClusterRoleBinding in `/registry/clusterrolebindings/` to grant a low-privileged user `cluster-admin` rights.
- **Denial of Service**: Execute `etcdctl del /registry/ --prefix` to delete the entire cluster state.

## 8. Mitigation and Hardening

1. **Restrict Control Plane Access**: Never run workloads on the control plane nodes (ensure master taints are intact).
2. **mTLS Enforcement**: Ensure `etcd` strictly enforces mTLS for all client connections.
3. **Encryption at Rest**: Enable Encryption at Rest using an external KMS provider. Do not use local static keys.
4. **Network Segmentation**: Isolate `etcd` network traffic. Only the `kube-apiserver` should be able to route to port 2379.
5. **Filesystem Permissions**: Ensure strict `chmod 600` on all `/etc/kubernetes/pki/` files.

## 9. Chaining Opportunities

- **Node Compromise to etcd Extraction**: Use techniques from [[10 - Escaping Privileged Containers Deep Dive]] to break out of a pod on the master node, then steal certs to dump etcd.
- **Cluster Takeover**: Use the extracted `cluster-admin` Service Account tokens to completely take over the API Server as detailed in [[04 - Kubernetes RBAC Exploitation]].

## 10. Related Notes

- [[04 - Kubernetes RBAC Exploitation]]
- [[10 - Escaping Privileged Containers Deep Dive]]
- [[01 - Container Fundamentals and Namespaces]]

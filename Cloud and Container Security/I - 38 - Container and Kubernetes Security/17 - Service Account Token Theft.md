---
tags: [kubernetes, rbac, service-account, token-theft, lateral-movement]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.17 Token Theft"
---

# Service Account Token Theft

## Introduction
In Kubernetes, non-human entities (like applications running inside Pods) need a way to authenticate to the Kubernetes API Server to perform tasks. This is handled by **Service Accounts**. When a Pod is created, Kubernetes automatically mounts a Service Account token (a JSON Web Token, JWT) into the Pod's file system by default. 

If an attacker compromises a container running inside a Kubernetes cluster (e.g., via a remote code execution vulnerability in a web application), one of their first post-exploitation objectives is to locate, steal, and utilize this Service Account token. Depending on the Role-Based Access Control (RBAC) privileges bound to that Service Account, the attacker can use the token to escalate privileges, move laterally to other namespaces, or completely take over the cluster.

This document explores the mechanics of Service Account tokens, how attackers steal and abuse them, and strategies to mitigate this critical risk vector.

## Anatomy of a Service Account Token

By default, every namespace in Kubernetes has a `default` Service Account. Unless explicitly disabled by the developer, the Kubelet will mount the credentials for this Service Account into every Pod running in that namespace.

### The Mount Location
Inside the container filesystem, the Service Account credentials are automatically mounted at a highly predictable location:
```text
/var/run/secrets/kubernetes.io/serviceaccount/
```

This directory contains three files:
1. `token`: The actual JWT bearer token used for authentication.
2. `ca.crt`: The certificate authority bundle used to verify the API server's TLS certificate.
3. `namespace`: A text file containing the name of the namespace the Pod is currently running in.

### The Token Structure
The `token` is a standard JWT. If an attacker reads this file, they can decode the base64-encoded payload to view its claims.

```bash
# Inside the compromised pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

Decoded JWT Payload (example):
```json
{
  "iss": "kubernetes/serviceaccount",
  "kubernetes.io/serviceaccount/namespace": "finance-app",
  "kubernetes.io/serviceaccount/secret.name": "default-token-xxxxx",
  "kubernetes.io/serviceaccount/service-account.name": "default",
  "kubernetes.io/serviceaccount/service-account.uid": "12345678-abcd-efgh-ijkl-1234567890ab",
  "sub": "system:serviceaccount:finance-app:default"
}
```
The `sub` (subject) field defines the identity K8s uses to evaluate RBAC permissions.

## Visualizing the Attack Path

```ascii
   [ Internet ]
        |
        | (1) Exploit RCE / LFI in Web App
        v
 +---------------------------------------------------------+
 |  Kubernetes Worker Node                                 |
 |                                                         |
 |  +---------------------------------------------------+  |
 |  |  Vulnerable Pod                                   |  |
 |  |                                                   |  |
 |  |  [ Web Application ]                              |  |
 |  |        |                                          |  |
 |  |        | (2) Attacker reads /var/run/secrets/...  |  |
 |  |        v                                          |  |
 |  |  [ token | ca.crt | namespace ] <-----------------+  | (Mounted via Kubelet)
 |  +---------------------------------------------------+  |
 |           |                                             |
 |           | (3) Attacker makes REST call using Token    |
 +-----------|---------------------------------------------+
             |
             v
   +--------------------+       (4) K8s evaluates RBAC:
   |  Kube API Server   | <---- If SA is bound to 'cluster-admin',
   |  (Port 6443)       |       attacker takes over the cluster.
   +--------------------+
```

## Exploitation Methodology

Once an attacker has read the `token` file, they can immediately begin interacting with the Kubernetes API server from inside the Pod. 

### Step 1: Discovering the API Server
The Kubernetes API server is typically exposed internally via a default Service named `kubernetes` in the `default` namespace. The environment variables `KUBERNETES_SERVICE_HOST` and `KUBERNETES_SERVICE_PORT` are automatically injected into every container.

```bash
# Print API server variables
env | grep KUBERNETES

# Result:
# KUBERNETES_SERVICE_HOST=10.96.0.1
# KUBERNETES_SERVICE_PORT=443
```

### Step 2: Querying the API Server (Auth Check)
The attacker uses `curl` to test the validity of the token and check for authorization. They use the `ca.crt` to verify the connection and pass the token in the `Authorization` header.

```bash
export APISERVER=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}
export TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
export CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Test basic access (whoami equivalent)
curl -s --cacert $CACERT --header "Authorization: Bearer $TOKEN" $APISERVER/api/v1/
```

### Step 3: Enumerating Permissions (Self-Subject Access Review)
Kubernetes has an endpoint called `SelfSubjectAccessReview` or `SelfSubjectRulesReview` that allows a user (or Service Account) to ask the API Server, "What am I allowed to do?"

Offensive tools like `kubectl auth can-i --list` use this endpoint. If the attacker has downloaded the `kubectl` binary into the pod, the process is streamlined:

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl

# Point kubectl at the API using the stolen token
./kubectl --token=$TOKEN --certificate-authority=$CACERT --server=$APISERVER auth can-i --list
```

### Step 4: Abuse and Escalation
Depending on the output of `auth can-i --list`, the attacker executes their objective:

- **List Secrets (`get/list secrets`)**: The attacker can dump all passwords, API keys, and database credentials stored in the namespace. If the Service Account has cluster-wide read access, they can dump secrets for the entire cluster.
- **Create Pods (`create pods`)**: The attacker can deploy a malicious pod configured with `privileged: true` or `hostPath` mounts to escape to the host node.
- **RoleBinding Creation**: If the Service Account can create `RoleBindings`, the attacker can bind the `cluster-admin` ClusterRole to their own Service Account, achieving instant cluster takeover.

## The Problem of Over-Privileged Default Accounts

The most common reason Token Theft leads to severe compromise is RBAC misconfiguration. Often, developers find that their application is failing to access the API server due to permission errors. Instead of creating a tightly scoped Role, they take the "easy route" and bind the `default` Service Account to highly privileged roles.

**Dangerous Anti-Pattern:**
```bash
# A developer runs this to fix permission errors quickly:
kubectl create clusterrolebinding default-admin --clusterrole=cluster-admin --serviceaccount=default:default
```
With this command, EVERY pod in the `default` namespace is now running with root-equivalent access to the entire cluster. A single Remote Code Execution in a trivial web application now yields complete cluster destruction.

## Defensive Strategies

Securing Service Accounts requires defense-in-depth, combining configuration hardening with strict RBAC auditing.

### 1. Disable Automounting
If an application does not *need* to talk to the Kubernetes API Server (which is true for 90% of standard web applications, databases, and APIs), you should explicitly instruct Kubernetes NOT to mount the Service Account token.

Modify the Pod or ServiceAccount spec:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: restricted-sa
automountServiceAccountToken: false
```
or at the Pod level:
```yaml
spec:
  automountServiceAccountToken: false
  containers:
  ...
```
If an attacker compromises this pod, there will be no `/var/run/secrets/kubernetes.io/...` directory to steal from.

### 2. Implement Least Privilege RBAC
Never use the `default` Service Account for applications that require API access.
1. Create a dedicated Service Account for the application (e.g., `app-frontend-sa`).
2. Create a `Role` with the exact verbs and resources required (e.g., `get` on `configmaps`).
3. Bind the `Role` to the specific Service Account via a `RoleBinding`.
4. Ensure `ClusterRoleBindings` are heavily audited and never assigned to application Service Accounts.

### 3. Bound Service Account Tokens (Kubernetes v1.21+)
In modern Kubernetes, Service Account tokens are no longer static, non-expiring secrets. They are now "Bound Service Account Tokens." 
- They are time-bound (they expire, typically after 1 hour, and the Kubelet automatically refreshes them).
- They are bound to the specific Pod's lifecycle. If the Pod is deleted, the token is instantly invalidated.
- They are bound to the audience (e.g., only valid for the Kube API server).

While this significantly reduces the window of opportunity for an attacker to exfiltrate and use the token externally, it does not prevent an attacker who has active RCE inside the pod from using the token *during* the pod's lifespan.

### 4. Network Policies
If a Pod does not need to communicate with the API Server, use Kubernetes Network Policies to block egress traffic to the API Server's IP address (`10.96.0.1:443`). Even if the token is present, the attacker's `curl` requests will time out.

## Conclusion
Service Account Token theft is the primary mechanism for lateral movement and privilege escalation inside a Kubernetes cluster post-breach. Treating every container as a potential beachhead means assuming the token within will be stolen. By disabling automounting by default, strictly enforcing least privilege RBAC, and isolating the API server via Network Policies, organizations can effectively neutralize this exploitation path.

## Chaining Opportunities
- Stolen tokens with sufficient permissions can be used to deploy pods exploiting [[16 - HostPath Volume Mount Abuse]] or [[15 - Pod Security — Privileged Pods]].
- If the token allows reading secrets, it could expose credentials used for [[02 - Cloud Security Identity and Access Management]] pivoting.
- Often the result of initial access through web application vulnerabilities or [[12 - Kubernetes RBAC Misconfigurations]].

## Related Notes
- [[13 - Kubernetes API Server — Unauthenticated Access]]
- [[12 - Kubernetes RBAC Misconfigurations]]
- [[01 - JWT Security and Exploitation]]

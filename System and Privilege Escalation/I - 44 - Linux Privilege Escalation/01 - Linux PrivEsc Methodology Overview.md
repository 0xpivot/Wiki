---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.01 Linux PrivEsc Methodology"
---

# Linux Privilege Escalation Methodology Overview

## 1. Executive Summary

Privilege escalation in Linux environments is the critical transition from a low-privileged user account (e.g., `www-data`, `nobody`, or a compromised standard user) to the `root` superuser. Achieving root access grants complete control over the system, allowing the attacker to access sensitive data, install persistent backdoors, and pivot to other network segments. 

The methodology of Linux Privilege Escalation is not a single, linear path but rather a highly iterative process of enumeration, analysis, and exploitation. It requires a profound understanding of Linux system architecture, permission models, kernel mechanics, and administrative misconfigurations. 

This document serves as the foundational overview of the methodology, emphasizing a structured approach to identifying and exploiting privilege escalation vectors.

## 2. Core Principles of Privilege Escalation

Before diving into specific techniques, an attacker must adopt the "Privilege Escalation Mindset":
- **Assume Nothing, Enumerate Everything:** Do not rely on assumptions about the system's security posture. A fully patched kernel might still be vulnerable to a simple misconfigured cron job.
- **Understand the "Why":** Knowing *why* a vulnerability exists (e.g., how the `execve` syscall handles SUID bits) is more valuable than blindly running exploit scripts.
- **Minimize Noise:** In mature environments, aggressive automated tools (like poorly configured LinPEAS runs) might trigger EDR/XDR alerts. Manual enumeration is often stealthier and more precise.
- **Living off the Land (LotL):** Whenever possible, use built-in binaries (e.g., `find`, `awk`, `tar`) to escalate privileges to avoid dropping anomalous compiled binaries onto the disk.

## 3. The Linux Kernel and `cred` Structure

To deeply understand privilege escalation, one must understand how Linux tracks privileges. At the kernel level, every process is represented by a `task_struct`. This structure contains a pointer to a `cred` structure, which defines the subjective and objective security credentials of the process.

```c
struct cred {
    atomic_t    usage;
    kuid_t      uid;        /* real UID of the task */
    kgid_t      gid;        /* real GID of the task */
    kuid_t      suid;       /* saved UID of the task */
    kgid_t      sgid;       /* saved GID of the task */
    kuid_t      euid;       /* effective UID of the task */
    kgid_t      egid;       /* effective GID of the task */
    // ...
    kernel_cap_t cap_inheritable; /* caps our children can inherit */
    kernel_cap_t cap_permitted;   /* caps we're permitted */
    kernel_cap_t cap_effective;   /* caps we can actually use */
    kernel_cap_t cap_bset;        /* capability bounding set */
    // ...
};
```

Privilege escalation, at its core, is the manipulation of these kernel structures—either directly via kernel exploitation or indirectly by abusing system mechanics (like SUID) to force the kernel to update the `euid` to 0 (`root`).

## 4. Phase 1: Situational Awareness

The immediate first step upon gaining a shell is to understand the current context.

### 4.1. Identity and Context
- `id` / `whoami`: Determines current UID, GID, and group memberships. Groups like `docker`, `lxd`, or `adm` are immediate escalation vectors.
- `env`: Checking environment variables. Are there sensitive tokens? Is `PATH` exploitable?
- `tty`: Do we have a fully interactive TTY? If not, we must upgrade (e.g., `python3 -c 'import pty; pty.spawn("/bin/bash")'`).

### 4.2. Network Context
- `ip a` / `ifconfig`: Identifies internal IP addresses and secondary network interfaces.
- `arp -a`: Identifies neighboring systems.
- `netstat -tulpn` / `ss -tulpn`: Identifies locally bound services (e.g., an internal MySQL database bound to `127.0.0.1` running as root).

## 5. Phase 2: Host and OS Enumeration

Understanding the underlying operating system dictates which exploits are viable.

### 5.1. OS Release and Architecture
- `cat /etc/os-release`: Determines the distribution (Ubuntu, Debian, CentOS, RHEL).
- `uname -a`: Reveals kernel version and system architecture (x86, x86_64, aarch64). A legacy kernel (e.g., 2.6.x or 3.10.x) is often vulnerable to known kernel exploits (like Dirty COW).

### 5.2. Installed Packages
- Debian/Ubuntu: `dpkg -l`
- RHEL/CentOS: `rpm -qa`
Searching for vulnerable software versions running as root (e.g., outdated sudo versions vulnerable to Baron Samedit, or vulnerable polkit versions).

## 6. Phase 3: Privilege Vector Enumeration

This is the most critical phase, involving the systematic hunting for specific misconfigurations.

### 6.1. Sudo Misconfigurations
Checking `sudo -l` to see what commands the current user can run as root. Misconfigurations here are the most common privesc vectors.

### 6.2. SUID/SGID Binaries
Searching for binaries with the Set-User-ID or Set-Group-ID bit set. These binaries execute with the privileges of their owner (usually root).
```bash
find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null
```

### 6.3. Cron Jobs and Scheduled Tasks
Reviewing `/etc/crontab`, `/etc/cron.*`, and user crontabs. Exploitable conditions arise when:
- A cron job runs a script that is writable by our user.
- A cron job uses wildcard expansions (e.g., `tar *`) which can be exploited via path injection.

### 6.4. Capabilities
Linux Capabilities divide root privileges into granular pieces. An overly permissive capability on a binary can lead to full compromise.
```bash
getcap -r / 2>/dev/null
```

### 6.5. Writable Sensitive Files
Checking if critical system files are writable by the unprivileged user.
- `/etc/passwd`: Can we append a new root user?
- `/etc/shadow`: Can we replace the root password hash?

## 7. Phase 4: Exploitation & Post-Exploitation

Once a vector is identified, the exploitation phase begins. This may involve compiling C code locally, manipulating `LD_PRELOAD`, or crafting malicious shell scripts.

Upon successful exploitation (gaining an `euid=0` shell):
1. **Stabilize:** Ensure the shell is stable and won't unexpectedly die.
2. **Persist:** (If in scope) Drop an SSH key into `/root/.ssh/authorized_keys`, create a backdoor SUID binary, or add a root cron job.
3. **Pillage:** Extract `/etc/shadow`, root SSH keys, configuration files, and database passwords.

## 8. Methodology ASCII Workflow

```text
+-------------------------------------------------------------------------+
|                    LINUX PRIVILEGE ESCALATION WORKFLOW                  |
+-------------------------------------------------------------------------+
|                                                                         |
|  [INITIAL ACCESS] ---> Low-Privileged Shell (www-data, standard user)   |
|         |                                                               |
|         v                                                               |
|  +--------------------+                                                 |
|  | SITUATIONAL AWARE  | ---> id, env, uname -a, ip a, ss -tulpn         |
|  +--------------------+                                                 |
|         |                                                               |
|         v                                                               |
|  +--------------------+   YES    +---------------------------------+    |
|  | QUICK WINS?        | -------> | Exploit immediately             |    |
|  | (sudo -l, groups)  |          | (e.g., lxd group, sudo NOPASSWD)|    |
|  +--------------------+          +---------------------------------+    |
|         | NO                                                            |
|         v                                                               |
|  +--------------------+          +---------------------------------+    |
|  | DEEP ENUMERATION   | -------> | Automated: LinPEAS, lse.sh      |    |
|  | (The Hunt)         |          | Manual: SUID/SGID, Capabilities,|    |
|  |                    |          | Cron jobs, Writable /etc/passwd |    |
|  +--------------------+          +---------------------------------+    |
|         |                                                               |
|         v                                                               |
|  +--------------------+          +---------------------------------+    |
|  | VULN ANALYSIS      | -------> | GTFOBins, SearchSploit,         |    |
|  |                    |          | Source Code Review (scripts)    |    |
|  +--------------------+          +---------------------------------+    |
|         |                                                               |
|         v                                                               |
|  +--------------------+          +---------------------------------+    |
|  | EXPLOITATION       | -------> | Path hijacking, LD_PRELOAD,     |    |
|  |                    |          | Kernel Exploits (Dirty Pipe)    |    |
|  +--------------------+          +---------------------------------+    |
|         |                                                               |
|         v                                                               |
|  [ ROOT COMPROMISE ]  ---> euid=0, uid=0                                |
+-------------------------------------------------------------------------+
```

## 9. Chaining Opportunities

Privilege escalation rarely happens in isolation. It relies on chains:
- **Information Disclosure to PrivEsc:** Finding plain-text credentials in `/var/www/html/config.php` might allow SSH access as a user who has `sudo` privileges, chaining into a Sudo Misconfiguration exploit.
- **Path Traversal to PrivEsc:** Using a web app path traversal vulnerability to read `id_rsa` of a local user, connecting via SSH, and then leveraging an SGID binary.
- **Docker to Host Escape:** Finding oneself in a Docker container, enumerating capabilities, escaping the container to the host, and then performing standard Linux privesc.

## 10. Related Notes
- [[02 - Enumeration Tools]]
- [[03 - SUID Binaries Abuse]]
- [[04 - SGID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[07 - Writable etc passwd]]

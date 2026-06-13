---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.35 Defense Hardening"
---

# 44.35 Defense: File Permission Hardening

## 1. Introduction

Throughout this module, we have explored numerous privilege escalation vectors—from SUID binaries and cron jobs to race conditions and library hijacking. The fundamental root cause of almost all local privilege escalation in Linux is **insecure file permissions**. When unprivileged users are granted unintended read, write, or execute access to critical system files, binaries, or directories, the boundary between user space and root space crumbles.

File Permission Hardening is the defensive practice of systematically applying the Principle of Least Privilege to the Linux filesystem. It involves configuring standard Unix Discretionary Access Controls (DAC), enforcing restrictive defaults via `umask`, utilizing special file attributes (like the immutable bit), locking down temporary directories, and layering Mandatory Access Controls (MAC) to restrict even the `root` user.

## 2. Architecture: Defense-in-Depth for File Systems

The following ASCII diagram illustrates the layered defensive approach to filesystem security, showing how a request must pass through multiple checks before access is granted.

```text
+---------------------------------------------------------------------------------+
|                          Linux Kernel Security Layers                           |
|                                                                                 |
|  +--------------------+                                                         |
|  | User Request       | (e.g., attempt to modify /etc/shadow)                   |
|  +--------------------+                                                         |
|            |                                                                    |
|            v                                                                    |
|  +--------------------+ 1. Mount Options Layer                                  |
|  | Mount Points       | Is the filesystem mounted as 'ro' (Read-Only)?          |
|  | (/etc/fstab)       | Does it have 'noexec' or 'nosuid' flags?                |
|  +--------------------+                                                         |
|            | (If allowed...)                                                    |
|            v                                                                    |
|  +--------------------+ 2. Extended Attributes Layer                            |
|  | File Attributes    | Does the file have the 'i' (Immutable) or 'a'           |
|  | (chattr / lsattr)  | (Append-only) bit set? (Blocks even root!)              |
|  +--------------------+                                                         |
|            | (If not immutable...)                                              |
|            v                                                                    |
|  +--------------------+ 3. Discretionary Access Control (DAC) Layer             |
|  | Standard Unix      | User, Group, Others (rwx). Evaluated sequentially.      |
|  | Permissions & ACLs | Are there POSIX ACLs (setfacl) restricting access?      |
|  +--------------------+                                                         |
|            | (If permissions allow...)                                          |
|            v                                                                    |
|  +--------------------+ 4. Mandatory Access Control (MAC) Layer                 |
|  | SELinux / AppArmor | Does the security policy explicitly allow this process  |
|  |                    | to interact with this file context?                     |
|  +--------------------+                                                         |
|            | (If policy allows...)                                              |
|            v                                                                    |
|  +--------------------+                                                         |
|  | Access Granted     | File is modified.                                       |
|  +--------------------+                                                         |
+---------------------------------------------------------------------------------+
```

## 3. Standard Permission Auditing (DAC)

The first step in hardening is ensuring that critical system files are not world-writable or group-writable by untrusted groups.

### 3.1 Finding World-Writable Files
World-writable files (`o+w`) are prime targets for attackers to inject malicious code or corrupt configurations.

```bash
# Find all world-writable files, excluding common symlink directories
find / -type f -perm -0002 -ls 2>/dev/null | grep -v "/proc/" | grep -v "/sys/"

# Remediation: Remove world-writable permissions
chmod o-w /path/to/file
```

### 3.2 Finding Unowned Files
Files with no valid owner or group (e.g., an employee left and their UID was deleted) can sometimes be claimed by newly created users who happen to get that UID.

```bash
# Find unowned files
find / -nouser -o -nogroup -exec ls -l {} \; 2>/dev/null

# Remediation: Assign to root or delete
chown root:root /path/to/orphan_file
```

## 4. Default Creation Masks (`umask`)

The `umask` determines the default permissions applied to newly created files and directories. A permissive umask (like `0000` or `0022`) can lead to privilege escalation if root processes create sensitive files that are world-readable.

### 4.1 Secure Umask Values
*   **0022:** (Default on many distros) New files are `644` (rw-r--r--), directories are `755`. Safe for public reading, but bad for sensitive data.
*   **0027:** New files are `640` (rw-r-----), directories `750`. World has no access. Good for shared environments.
*   **0077:** New files are `600` (rw-------), directories `700`. Only the owner has access. Ideal for root and highly sensitive accounts.

### 4.2 Enforcing Umask
Set the global umask in `/etc/profile` and `/etc/login.defs`. Ensure `root`'s specific `.bashrc` enforces `0077`.

## 5. Locking Down SUID and SGID Binaries

SUID binaries run with the privileges of the file owner (usually `root`). An attacker only needs one vulnerable SUID binary to compromise the system.

### 5.1 Auditing SUID/SGID
```bash
# Find all SUID and SGID binaries
find / -type f \( -perm -4000 -o -perm -2000 \) -exec ls -la {} \; 2>/dev/null
```

### 5.2 Remediation Strategy
1.  **Remove Unnecessary SUIDs:** If a binary doesn't strictly need root privileges, remove the SUID bit.
    ```bash
    chmod u-s /usr/bin/ping  # Modern ping uses capabilities, not SUID
    ```
2.  **Use Capabilities Instead:** Linux capabilities break down root privileges into smaller, specific permissions. Instead of making a web server SUID root just to bind to port 80, grant it `CAP_NET_BIND_SERVICE`.
    ```bash
    setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx
    ```
3.  **Restrict Execution:** If an SUID binary is required but only by administrators, remove world-execute permissions and assign it to an administrative group.

## 6. Securing Temporary Directories (`/tmp`, `/var/tmp`, `/dev/shm`)

These directories are world-writable by necessity, making them the staging ground for almost all local exploits (race conditions, downloading payloads, executing scripts).

### 6.1 Mount Options
The most effective defense is mounting these partitions with restrictive flags in `/etc/fstab`:

*   **`nodev`:** Prevents the creation of character or block special devices (stops device node attacks).
*   **`nosuid`:** Ignores SUID/SGID bits on files within the partition. An attacker cannot compile an SUID root backdoor and place it in `/tmp`.
*   **`noexec`:** Prevents the execution of binaries or scripts directly from the partition. This drastically hinders attackers from running their downloaded exploit payloads.

**Example `/etc/fstab` entry:**
```text
tmpfs /tmp tmpfs defaults,nodev,nosuid,noexec 0 0
```

### 6.2 Symlink/Hardlink Protections
Prevent attackers from exploiting Time-of-Check to Time-of-Use (TOCTOU) race conditions by enabling kernel protections in `/etc/sysctl.conf`:
```text
fs.protected_symlinks = 1
fs.protected_hardlinks = 1
```

## 7. Extended Attributes: The Immutable Bit

Sometimes, you want to ensure a file is NEVER modified, even if an attacker gains root access or exploits a misconfiguration. The `chattr` command modifies file system attributes specific to ext2/ext3/ext4/XFS filesystems.

### 7.1 The 'i' (Immutable) Attribute
When the `i` attribute is set, the file cannot be modified, deleted, renamed, or linked to. Not even `root` can change it without first removing the attribute.

```bash
# Make a critical configuration file immutable
chattr +i /etc/passwd
chattr +i /etc/shadow

# Verify the attribute
lsattr /etc/passwd
# ----i---------e---- /etc/passwd
```
*Note:* This should be used sparingly, as it will break legitimate system updates or password changes until manually removed (`chattr -i`).

### 7.2 The 'a' (Append-Only) Attribute
Ideal for log files. The file can only be opened in append mode for writing; existing data cannot be overwritten or deleted.
```bash
chattr +a /var/log/auth.log
```

## 8. Access Control Lists (POSIX ACLs)

Standard DAC permissions (rwx) are limited to one owner and one group. What if `userA` needs read access, `userB` needs write access, and `userC` needs no access? Administrators often mistakenly use `chmod 777` to solve this. Instead, use ACLs.

### 8.1 Implementing ACLs
```bash
# Grant specific write access to user 'bob' without changing the primary owner/group
setfacl -m u:bob:rw /var/www/html/config.php

# View the ACLs (Notice the '+' sign in the standard ls -l output)
getfacl /var/www/html/config.php
```
Using ACLs ensures the Principle of Least Privilege is maintained in complex enterprise environments.

## 9. Real-World Hardening Checklist for Penetration Testers

When conducting a purple team exercise or providing remediation advice, verify the following:

1.  [ ] **No world-writable sensitive files:** Check `/etc`, `/root`, `/var/log`.
2.  [ ] **`/tmp` restrictions:** Ensure `/tmp`, `/var/tmp`, and `/dev/shm` are mounted `nodev,nosuid,noexec`.
3.  [ ] **SUID minimisation:** Compare the list of SUID binaries against a known-good baseline (e.g., CIS Benchmarks).
4.  [ ] **Umask enforcement:** Verify `umask 027` or stricter is enforced system-wide.
5.  [ ] **Kernel Symlink Protections:** Verify `fs.protected_symlinks` is active.
6.  [ ] **MAC Implementation:** Ensure SELinux is `Enforcing` or AppArmor profiles are active for critical network-facing services (e.g., Apache, Nginx, MySQL), confining them even if an RCE occurs.

## Chaining Opportunities
- Failure to implement these controls enables almost every attack in this module, specifically **[[12 - SUID Executable Exploitation]]**, **[[31 - tmp Race Conditions]]**, and **[[25 - Cron Job Exploitation]]**.
- Strong file permissions force attackers to rely on kernel exploits (**[[38 - Bypassing Kernel Exploit Mitigations]]**) rather than simple misconfigurations.

## Related Notes
- [[19 - Linux Process Enumeration]]
- [[24 - SUID vs SUDO Mechanisms]]
- [[40 - SELinux and AppArmor Bypasses]]

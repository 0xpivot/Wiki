---
tags: [linux, privesc, groups, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.44 Abusing Interesting Linux Groups"
---

# Abusing Interesting Linux Groups

## Introduction
Group membership is an under-appreciated privilege-escalation surface on Linux. Several built-in groups grant capabilities that, directly or indirectly, lead to root. Some are well known (`docker`, `lxd`, `disk` — covered in [[19 - Docker Group Membership]], [[20 - LXC LXD Group Abuse]], [[21 - Disk Group Reading Raw Device Files]]); this note rounds up the **other** "interesting groups" worth checking — `adm`, `shadow`, `video`, `sudo`/`wheel`, `sys`/`kmem`, `lxc`, `staff`, and others — and how each converts into elevated access. Always start by reading your group memberships:
```bash
id; groups
getent group | grep -E "$(id -un)|$(id -Gn | tr ' ' '|')"
```

## Group-by-Group Abuse
```text
+-------------+-------------------------------------------------+
| Group       | What it grants / how to abuse                   |
+-------------+-------------------------------------------------+
| docker      | talk to docker.sock -> mount host / -> root     |
| lxd / lxc   | launch privileged container -> mount host root  |
| disk        | read/write raw block devs -> read /etc/shadow,  |
|             | edit any file via debugfs                       |
| sudo/wheel  | sudo rights (check `sudo -l`)                   |
| adm         | read system logs -> creds/tokens in logs        |
| shadow      | read /etc/shadow -> crack password hashes       |
| video       | read framebuffer/GPU mem -> screen capture      |
| kmem / sys  | read /dev/mem,/dev/kmem -> kernel memory secrets|
| staff       | write /usr/local -> PATH/lib hijack -> root     |
| root (sec.) | secondary root group; write root-group files    |
+-------------+-------------------------------------------------+
```

### `shadow`
Members can read `/etc/shadow` — every user's password hash. Crack offline (hashcat/john) to recover root or admin passwords:
```bash
cat /etc/shadow            # readable as group 'shadow'
unshadow /etc/passwd /etc/shadow > h && john h
```

### `adm`
Grants read access to `/var/log/*`. Logs frequently leak credentials, tokens, session IDs, and command lines (apps logging secrets, web access logs with creds in URLs):
```bash
grep -riE 'pass|token|secret|key=' /var/log 2>/dev/null
```
Not direct root, but a reliable credential source for escalation/lateral movement.

### `disk`
Raw access to block devices (`/dev/sda*`). With `debugfs` you can read/write **any** file on the filesystem regardless of permissions — read `/etc/shadow`, or write a SUID binary / root SSH key:
```bash
debugfs /dev/sda1 -R 'cat /etc/shadow'      # read protected file
# or edit files to plant a backdoor
```
(Covered in depth in [[21 - Disk Group Reading Raw Device Files]].)

### `video`
Access to the framebuffer (`/dev/fb0`) and GPU devices — dump the screen to capture whatever a privileged user is viewing (passwords, tokens):
```bash
cat /dev/fb0 > /tmp/screen.raw      # decode to image to read the screen
```

### `kmem` / `sys`
Access to `/dev/mem`, `/dev/kmem` exposes physical/kernel memory — secrets, keys, and even direct kernel patching for root. Rare but devastating where present.

### `staff` (Debian)
Write access to `/usr/local/{bin,lib,sbin}`. These often precede system dirs in `PATH`/library search; planting a binary or library that a root process/cron later executes yields root — a [[11 - PATH Environment Variable Hijacking]] / [[13 - Shared Library Injection]] vector with a built-in writable directory.

### `sudo` / `wheel`
The obvious one — confirm with `sudo -l`; even a single permissive rule is escalation ([[06 - Sudo Misconfigurations]], [[32 - Insecure Sudo Rules]]).

## Methodology
```text
   1. id / groups  -> list memberships
   2. For each non-default group, map to the table above
   3. Pick the most direct path:
        - immediate root:  docker, lxd, disk, kmem, staff(+root cron)
        - credential source: shadow, adm, video -> crack/loot then escalate
   4. Verify and execute
```

## Why It Matters in an Engagement
Admins add users to convenience groups (`adm` for log access, `docker` for dev work, `disk`/`staff` historically) without realising several are root-equivalent or near it. Group enumeration is a 5-second check that frequently shortcuts the entire privesc hunt — especially `docker`, `lxd`, `disk`, and `staff` for direct root, and `shadow`/`adm` as credential goldmines.

## Detection and Mitigation
- Audit membership of `docker`, `lxd`, `disk`, `kmem`, `sys`, `shadow`, `adm`, `video`, `staff`, `sudo`/`wheel` — treat them as privileged.
- Apply least privilege: most users need none of these; use `sudo` with specific commands instead of broad group membership.
- Monitor reads of `/etc/shadow`, `/dev/mem|kmem|fb0`, raw block devices, and writes to `/usr/local`.

## Chaining Opportunities
- Direct-root groups → instant escalation ([[19 - Docker Group Membership]], [[20 - LXC LXD Group Abuse]], [[21 - Disk Group Reading Raw Device Files]]).
- Credential groups (`shadow`/`adm`/`video`) → crack/loot → reuse ([[16 - Password in Config Files History Env Vars]]).
- `staff` → [[11 - PATH Environment Variable Hijacking]] / [[13 - Shared Library Injection]].

## Related Notes
- [[19 - Docker Group Membership]]
- [[20 - LXC LXD Group Abuse]]
- [[21 - Disk Group Reading Raw Device Files]]
- [[06 - Sudo Misconfigurations]]
- [[11 - PATH Environment Variable Hijacking]]

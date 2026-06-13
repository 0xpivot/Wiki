---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.28 proc Information Leakage"
---

# /proc Filesystem Information Leakage

## Introduction
The `/proc` directory is not a real file system residing on a hard drive; it is a virtual, pseudo-filesystem created by the Linux kernel in memory. It serves as an interface to internal kernel data structures and provides a wealth of information about the system hardware, kernel configuration, and, most importantly, running processes. Every process running on the system is represented by a directory in `/proc` named after its Process ID (PID) (e.g., `/proc/1234/`).

While `/proc` is essential for system administration and monitoring tools (like `ps`, `top`, and `htop`), improper permission configurations or legacy kernel defaults can lead to catastrophic information leakage. For an attacker seeking privilege escalation, `/proc` is a goldmine. It can leak plaintext passwords passed via command-line arguments, sensitive environment variables, hidden network connections, and kernel memory addresses necessary to bypass modern exploit mitigations like KASLR.

## Core Mechanisms and Targets within `/proc`

When an attacker lands on a Linux system with a low-privileged shell, one of the first automated or manual tasks is sweeping `/proc` for sensitive data belonging to processes owned by `root` or other users.

### ASCII Diagram: /proc Memory Mapping and Information Flow

```text
+----------------------------------------------------------------------------------+
|                          /PROC FILESYSTEM LEAKAGE MAPPING                        |
+----------------------------------------------------------------------------------+
|                                                                                  |
|                      Kernel Space Memory (Virtual FS)                            |
|  +----------------------------------------------------------------------------+  |
|  | /proc/                                                                     |  |
|  |  |-- kallsyms (Kernel Address Map)                                         |  |
|  |  |-- cmdline  (Boot parameters)                                            |  |
|  |  |-- net/     (Network stack data)                                         |  |
|  |  |    |-- tcp, udp, route                                                  |  |
|  |  |                                                                         |  |
|  |  +-- [PID 1055 - Root Process (e.g., backup.sh)]                           |  |
|  |       |                                                                    |  |
|  |       |-- cmdline -> "sh backup.sh --password=SuperSecret!"                |  |
|  |       |-- environ -> "DB_USER=root\0DB_PASS=P@ssw0rd\0"                    |  |
|  |       |-- fd/     -> Symlinks to open files (/etc/shadow)                  |  |
|  |       |-- maps    -> Memory layout of the process                          |  |
|  +-------|--------------------------------------------------------------------+  |
|          |                                                                       |
|          v                                                                       |
|   Attacker (User Space)                                                          |
|   $ cat /proc/1055/cmdline | tr '\0' ' '                                         |
|   sh backup.sh --password=SuperSecret!                                           |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

### 1. `/proc/[pid]/cmdline`
This file contains the complete command line used to launch the process, with arguments separated by null bytes (`\0`). Administrators often make the fatal mistake of passing credentials directly via the command line in automated scripts.
**Exploitation:**
An attacker loops through all PIDs to search for sensitive strings:
```bash
for pid in /proc/[0-9]*; do cat $pid/cmdline 2>/dev/null | tr '\0' ' '; echo ""; done | grep -i "pass"
```
If a script runs `mysql -u root -pPassword123`, it is exposed here for any user to read unless `hidepid` is configured.

### 2. `/proc/[pid]/environ`
This file contains the environment variables present when the process was started. Similar to `cmdline`, variables are separated by null bytes. Applications often use environment variables to handle API keys, database credentials, or access tokens.
**Exploitation:**
```bash
strings /proc/*/environ | grep -i "AWS_ACCESS_KEY"
```

### 3. `/proc/net/tcp` and `/proc/net/udp`
These files contain active network connections and listening ports. Attackers use this to bypass stripped down environments (where `netstat` or `ss` are missing) to find internal, localhost-bound services (e.g., an internal Redis or MySQL instance listening on `127.0.0.1`) that might be vulnerable to local exploitation.
**Reading the Hex:**
Ports and IPs in `/proc/net/tcp` are represented in Little-Endian hexadecimal. For example, local address `0100007F:0016` translates to `127.0.0.1:22`.

### 4. Bypassing KASLR via `/proc/kallsyms`
Kernel Address Space Layout Randomization (KASLR) places the kernel code at a random memory location on boot. To write a successful kernel exploit (like Return-Oriented Programming (ROP) chains in kernel space), an attacker needs to know the exact memory addresses of kernel functions (like `commit_creds`).
Historically, `/proc/kallsyms` exposed these addresses to all users.
**Exploitation Check:**
```bash
head /proc/kallsyms
```
If the output shows actual memory addresses (`ffffffff81...`) instead of all zeros (`0000000000...`), the system is leaking kernel pointers, rendering KASLR useless.

### 5. Passing Open File Descriptors (`/proc/[pid]/fd`)
The `/fd` directory contains symbolic links to all files the process has open. If a highly privileged process opens a restricted file (like `/etc/shadow`) but has misconfigured permissions on its `/proc` directory, an attacker might read the file through the open file descriptor symlink.

## Defensive Countermeasures

Because `/proc` information leakage is heavily relied upon by attackers for situational awareness and credential harvesting, hardening this virtual filesystem is a crucial defense-in-depth strategy.

### 1. Implementing `hidepid`
The most effective defense against `cmdline` and `environ` snooping is mounting the `/proc` filesystem with the `hidepid` option. This restricts users so they can only see their *own* processes in `/proc` (and consequently in commands like `ps` and `top`).
To apply temporarily:
```bash
mount -o remount,rw,hidepid=2 /proc
```
To persist across reboots, modify `/etc/fstab`:
```text
proc    /proc    proc    defaults,hidepid=2    0 0
```
- `hidepid=1`: Users cannot access `/proc/[pid]/` directories of other users.
- `hidepid=2`: The `/proc/[pid]/` directories are entirely hidden from other users.

### 2. Restricting Kernel Pointers (`kptr_restrict`)
To prevent KASLR bypasses via `kallsyms`, the kernel pointers must be hidden from unprivileged users. This is usually the default on modern kernels, but should be verified.
```bash
sysctl -w kernel.kptr_restrict=1
```
Or `2` to hide them even from the root user (unless the root user changes it back).

### 3. Restricting `dmesg` (`dmesg_restrict`)
While not strictly `/proc` (though related to kernel ring buffers accessible via `/dev/kmsg` or syslog), `dmesg` often leaks kernel addresses during module loads or crashes.
```bash
sysctl -w kernel.dmesg_restrict=1
```

### 4. Avoiding Command-Line Credentials
Developers and administrators must be trained to *never* pass passwords, tokens, or API keys as command-line arguments. Instead, applications should read credentials from securely permissioned configuration files or standard input (STDIN), which are not exposed in `/proc`.

## Summary
The `/proc` filesystem acts as a window into the operating system's soul. For penetration testers, it provides the intelligence required to move laterally or escalate privileges locally. For defenders, securing `/proc` via `hidepid` and proper sysctl configurations creates a significant blind spot for attackers, drastically increasing the difficulty of post-exploitation.

## Chaining Opportunities
- Leaked credentials from `cmdline` or `environ` frequently lead directly to [[14 - Sudo Misconfigurations]] or allow access to internal services.
- Defeating KASLR via `kallsyms` is an essential prerequisite for many [[23 - Kernel Exploits]].
- Finding local, unexposed services via `/proc/net/tcp` can lead to exploiting [[09 - Internal Network Pivoting]].

## Related Notes
- [[04 - Enumerating Automated Tasks]]
- [[21 - Bash Script Weaknesses]]
- [[06 - Cron Job Misconfigurations]]

---
tags: [macos, privesc, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.01 macOS PrivEsc Methodology Overview"
---

# macOS PrivEsc Methodology Overview

## Introduction
Privilege escalation on macOS looks superficially like Linux — it is a Unix system with `sudo`, SUID binaries, cron-style jobs, and a POSIX permission model — but in practice the interesting attack surface is almost entirely **Apple-specific**. Modern macOS layers a stack of proprietary security subsystems on top of the BSD/Mach kernel: **SIP** (System Integrity Protection), **TCC** (Transparency, Consent & Control), **Gatekeeper**, the **App Sandbox**, **code signing**, **entitlements**, and **AMFI** (AppleMobileFileIntegrity). On a hardened, up-to-date Mac, classic Unix privesc is often a dead end and the real work is *bypassing these subsystems*.

It also helps to think in terms of **two distinct goals** that are frequently conflated on Linux but separate on macOS:
1. **Becoming root** (UID 0) — the classic vertical escalation.
2. **Defeating the security frameworks** — e.g. reading another user's private files protected by TCC, escaping the sandbox, or disabling SIP. On macOS, **root is not all-powerful**: SIP restricts even root, and TCC gates even root from certain user data.

## The macOS Privilege Model
macOS privilege is best understood as several overlapping layers:

```text
+---------------------------------------------------------------+
|                     macOS PRIVILEGE LAYERS                     |
+---------------------------------------------------------------+
|                                                               |
|  [ UNIX layer ]   uid/gid, sudo, SUID, file perms, ACLs       |
|         |                                                     |
|         v                                                     |
|  [ Entitlements ] code-signed capabilities a binary may hold  |
|         |          (e.g. com.apple.private.* , task_for_pid)  |
|         v                                                     |
|  [ Sandbox ]      seatbelt profiles limit syscalls/file/IPC   |
|         |                                                     |
|         v                                                     |
|  [ TCC ]          gates access to user-private data           |
|         |          (Documents, camera, mic, Full Disk Access) |
|         v                                                     |
|  [ SIP ]          protects system files & restricts root      |
|         |          even from UID 0 (rootless)                 |
|         v                                                     |
|  [ AMFI / KEXTs ] only validly-signed code runs in kernel     |
+---------------------------------------------------------------+
```

Because root is *not* the top of the stack, an attacker often needs to chain: low-priv user → root (Unix techniques) → SIP/TCC bypass (Apple-specific techniques) to reach truly sensitive data or kernel-level persistence.

## Enumeration Checklist
The first phase on any macOS host is orientation. Key commands (see also [[02 - macOS Enumeration and Useful Commands]]):

```bash
# System / version
sw_vers                       # ProductVersion, build
uname -a
system_profiler SPSoftwareDataType SPHardwareDataType

# Users & privileges
id; whoami; groups
dscl . list /Users | grep -v '^_'        # real (non-service) users
dscl . -read /Groups/admin GroupMembership # who is a local admin
sudo -l 2>/dev/null

# Security posture
csrutil status                # SIP enabled/disabled
spctl --status                # Gatekeeper assessment state
fdesetup status               # FileVault
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db .dump 2>/dev/null  # user TCC

# Interesting SUID / writable binaries
find / -perm -4000 -type f 2>/dev/null
find / -writable -type d 2>/dev/null | grep -vi '/Users/'

# Running services / launch items
launchctl list
ls -la /Library/LaunchDaemons /Library/LaunchAgents ~/Library/LaunchAgents
```

## Attack-Surface Map
The notes in this module group the macOS-specific surface as follows:

| Surface | Goal | Notes |
|---|---|---|
| Security protections | Defeat SIP / TCC / Gatekeeper / Sandbox | [[03 - System Integrity Protection SIP]], [[04 - TCC Transparency Consent and Control]], [[05 - Gatekeeper and Quarantine Bypass]], [[08 - App Sandbox Escapes]] |
| Code trust | Run untrusted code, forge trust | [[06 - Code Signing and Entitlements]], [[07 - AMFI and Launch Constraints]], [[09 - Dangerous Entitlements]] |
| Process injection | Inject into more-privileged processes | [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]], [[11 - XPC and Mach IPC Abuse]], [[12 - Electron Chromium and Interpreted App Injection]] |
| Persistence | Survive reboot / re-login | [[13 - macOS Auto-Start Locations and Persistence]] |
| Credentials | Steal secrets | [[14 - macOS Keychain Attacks]], [[15 - macOS Sensitive Locations and Credential Theft]] |
| Installers | Abuse privileged installs | [[16 - macOS Installers and Package Abuse]] |
| Fleet | Org-level compromise | [[17 - macOS MDM Abuse]] |

## General Privesc Workflow
1. **Enumerate** the host and, critically, the *security posture* (`csrutil`, `spctl`, TCC DB) — this dictates which techniques are even viable.
2. **Hunt for classic Unix wins** first (writable LaunchDaemons, sudo misconfig, SUID) — they are simplest and OS-agnostic.
3. **Look for misconfigured privileged helpers** (XPC Mach services, installers, auto-updaters) — the richest macOS-specific local root vector.
4. **Target a protection bypass** appropriate to the objective (TCC for data, SIP for system persistence, sandbox escape if you start sandboxed).
5. **Establish persistence** via a launch item or auto-start location, ideally code-signed to avoid Gatekeeper/notarization prompts.

## Defensive Notes
- Keep SIP **enabled** — disabling it (a common dev shortcut) removes the single biggest barrier to kernel persistence.
- Audit `/Library/LaunchDaemons` and privileged helper tools (`/Library/PrivilegedHelperTools`) for weak permissions and unsigned binaries.
- Minimise apps granted **Full Disk Access** and **Accessibility** in TCC — these are prime escalation pivots.
- Prefer notarized, hardened-runtime apps; deny the `com.apple.security.get-task-allow` entitlement in production builds.

## Related Notes
- [[02 - macOS Enumeration and Useful Commands]]
- [[03 - System Integrity Protection SIP]]
- [[04 - TCC Transparency Consent and Control]]
- [[01 - Linux PrivEsc Methodology Overview]]
- [[01 - Windows PrivEsc Methodology Overview]]

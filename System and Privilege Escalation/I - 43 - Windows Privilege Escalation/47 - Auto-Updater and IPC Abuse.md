---
tags: [windows, privesc, ipc, updater, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.47 Auto-Updater and IPC Abuse"
---

# Auto-Updater and IPC Abuse

## Introduction
Most installed desktop software ships an **auto-updater** and/or a **privileged helper service** so that updates can be applied without prompting for admin rights each time. To bridge the low-privileged GUI app and the SYSTEM-level update service, vendors use some form of **IPC** — named pipes, local TCP/HTTP sockets, COM, or WCF/.NET remoting. This pattern is a goldmine for local privilege escalation: if the privileged updater performs a sensitive action (download + execute an installer, copy files to `Program Files`, run a command) based on **unauthenticated or weakly-validated IPC input**, a low-privileged user can drive it to run code as SYSTEM. This is the Windows analogue of macOS XPC helper abuse.

## The Vulnerable Pattern
```text
+---------------------------------------------------------------+
|             AUTO-UPDATER PRIVILEGE-ESCALATION                |
+---------------------------------------------------------------+
|  Low-priv GUI app  --IPC-->  SYSTEM update service           |
|    (named pipe / localhost socket / COM / WCF)               |
|        |                                                       |
|   Does the SYSTEM service authenticate the caller & validate  |
|   what it's told to do?                                       |
|     NO  -> attacker sends the IPC message directly:           |
|            "install this package" / "run this path"           |
|            -> SYSTEM executes attacker-controlled code        |
|     weak (no signature check on the "update") -> serve a      |
|            malicious update -> SYSTEM runs it                 |
+---------------------------------------------------------------+
```

## Common Bug Classes
### 1. Unauthenticated IPC commands
The privileged service exposes a named pipe / local socket that accepts commands (`InstallUpdate`, `RunInstaller`, `SetConfig`) from **any** local process. The attacker replays/sends the message and the service acts as SYSTEM. Frequently there is *no* caller verification at all.

### 2. Missing update integrity validation
The updater downloads an installer to a (sometimes world-writable) staging directory and executes it as SYSTEM **without verifying its code signature** — or verifies it weakly. An attacker who can write to the staging path, or who controls the IPC "update location" parameter, supplies a malicious binary that runs elevated. Overlaps with [[05 - Modifiable Service Binaries]] when the staging dir is writable.

### 3. TOCTOU between validation and execution
The service checks the file (signature/hash) then executes it from the same path; an attacker swaps the file in the window between check and use (a race), getting their binary executed as SYSTEM. Predictable, writable temp paths make this reliable.

### 4. Path / argument injection in the privileged action
The IPC message includes a path or argument that the SYSTEM service passes to `CreateProcess`/`msiexec`/a shell without sanitization — classic argument injection leading to SYSTEM code execution.

### 5. DLL planting against the updater
The updater (or installer it runs) loads a DLL from a writable or current directory — combine with [[06 - DLL Hijacking]] / [[07 - DLL Search Order Abuse]] to get SYSTEM execution when the update runs.

## Enumeration & Probing
```cmd
:: privileged services from 3rd-party software (updaters/helpers)
sc query state= all | findstr /i "SERVICE_NAME"
:: their binaries / accounts
wmic service get Name,StartName,PathName | findstr /i "Update Helper Agent"
:: named pipes exposed locally
:: (Sysinternals: pipelist.exe / "PipeList")
pipelist.exe
:: writable staging dirs used by updaters
icacls "C:\ProgramData\<Vendor>" 2>nul | findstr /i "Everyone Users (M) (F) (W)"
```
Then trace the IPC: which pipe/socket the GUI talks to, the message format (capture with Process Monitor / a pipe sniffer), and whether the service checks the peer. Reproduce the message from a low-priv process and observe the privileged action.

## Why It Matters in an Engagement
Third-party auto-updaters are nearly ubiquitous on corporate endpoints (browsers, chat apps, VPNs, AV, hardware utilities) and have a long history of local-SYSTEM CVEs precisely because the IPC-to-privileged-service boundary is easy to get wrong. They are often the **fastest local root** on an otherwise-patched Windows host — and the same conceptual flaw recurs across vendors.

## Detection and Mitigation
- **Developers:** authenticate the IPC caller (verify the connecting process's code signature/identity, not just that it connected), strictly validate all parameters, verify update signatures *and* execute from a protected, non-writable path with no TOCTOU window.
- **Defenders:** inventory third-party privileged services/updaters; remove unused ones; monitor SYSTEM services spawning installers/shells and writes to updater staging directories.
- Apply vendor patches promptly — updater LPEs are frequently fixed CVEs.
- Application allow-listing (WDAC/AppLocker) limits what a coerced updater can execute.

## Chaining Opportunities
- Writable staging dir → [[06 - DLL Hijacking]] / [[05 - Modifiable Service Binaries]] against the update process.
- Conceptual sibling of [[44 - Local NTLM Reflection and Relay]] and [[28 - Named Pipe Impersonation]] (both abuse local IPC trust).

## Related Notes
- [[05 - Modifiable Service Binaries]]
- [[28 - Named Pipe Impersonation]]
- [[06 - DLL Hijacking]]
- [[42 - Service Trigger Abuse]]
- [[44 - Local NTLM Reflection and Relay]]

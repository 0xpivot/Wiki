---
tags: [macos, privesc, xpc, mach, ipc, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.11 XPC and Mach IPC Abuse"
---

# XPC and Mach IPC Abuse

## Introduction
Underneath macOS, processes talk to each other through **Mach IPC** — messages sent to **Mach ports**. **XPC** is Apple's higher-level framework built on Mach that powers most privilege boundaries: a sandboxed app asks a privileged **helper tool** to do something it can't, system daemons expose **Mach services** by name, and app components split work across processes. This makes XPC/Mach services the **#1 local privilege-escalation and sandbox-escape surface on macOS**: a privileged service that fails to properly verify *who is calling it* will perform privileged actions for an unprivileged attacker.

## The Trust Problem
A privileged XPC service (often a root **privileged helper tool** installed via `SMJobBless` into `/Library/PrivilegedHelperTools`) listens for requests. The critical question on every incoming connection is: **"Is this client allowed to ask me this?"** The correct answer requires validating the peer's **code-signing identity** (team ID, designated requirement) and **audit token**. Many helpers get this wrong.

```text
+---------------------------------------------------------------+
|              XPC PRIVILEGE-ESCALATION PATTERN                 |
+---------------------------------------------------------------+
|  Low-priv attacker process                                    |
|        |  xpc_connection_create_mach_service("com.vendor.helper")
|        v                                                       |
|  Root helper tool (/Library/PrivilegedHelperTools)            |
|        |                                                       |
|   Does it check the caller?                                   |
|     NO  validation        -> performs privileged op as root   |
|     weak validation (pid) -> PID-reuse / audit-token spoof     |
|     strong (audit token + |                                    |
|       code requirement)   -> request rejected                  |
+---------------------------------------------------------------+
```

## Common Vulnerability Classes
### 1. No client verification at all
The helper accepts any connection and exposes a method like `installPackage:`, `runCommand:`, or `setOwner:`. An attacker simply connects and calls it → instant root. Astonishingly common in third-party updater/helper tools.

### 2. PID-based checks (PID reuse)
The helper validates the client by **PID** (`pid_t`) — e.g. "is the caller's path /Applications/Trusted.app?". PIDs are reusable: an attacker starts a legitimate process, gets its PID approved, then the PID is recycled for the attacker's process, or the check races process exec. The robust fix is to use the **audit token**, not the PID.

### 3. Audit-token misuse
Even audit-token checks are abusable if the helper reads the token from the *message* rather than from the connection, or calls `xpc_connection_get_audit_token` incorrectly — the basis of the well-documented `xpc_connection_get_audit_token` attack, where the token can be confused/spoofed.

### 4. Weak code-signing requirement
The helper checks "signed by *some* Apple cert" or "bundle id == X" without pinning the team ID, letting an attacker satisfy the requirement with a different signed binary, or by injecting into the legitimate client (then the request genuinely comes from it).

### 5. Argument injection in the privileged op
The helper validates the caller but then runs an attacker-influenced command/path as root (classic command injection / path traversal inside a privileged action).

## Finding and Probing Helpers
```bash
# Installed privileged helpers
ls -la /Library/PrivilegedHelperTools
# Their declared Mach service names + who may talk to them
defaults read /Library/LaunchDaemons/<helper>.plist
codesign -d --entitlements - /Library/PrivilegedHelperTools/<helper>
# Enumerate registered Mach services
launchctl print system | grep -i endpoints -A50
```
Probing then means writing a small client that connects to the service name and invokes its exposed selectors, observing whether identity is checked. Tools in the research community (e.g. XPC fuzzers / `xpcspy`-style tracers) automate message discovery.

## Mach Ports Directly
Lower than XPC, raw Mach techniques include **task-port theft** (obtaining another process's `task` port → read/write its memory → inject; gated by entitlements, see [[09 - Dangerous Entitlements]]), **thread injection via task port**, and **MIG** (Mach Interface Generator) handler bugs in daemons. The **bootstrap server** maps service names to ports; **port name confusion** and **port substitution** have historically enabled service impersonation.

## Why It Matters
- **Local root:** a vulnerable third-party privileged helper is the most reliable macOS local-root vector — often a trivial "connect and call."
- **Sandbox escape:** a sandboxed process reaching a flawed broker over XPC is the canonical escape ([[08 - App Sandbox Escapes]]).
- **Bug-bounty / pentest gold:** every installed helper is worth auditing for caller verification.

## Defensive Notes
- Validate every XPC client with the **connection's audit token** + a **strict code-signing requirement pinning the Team ID** (`SecCodeCheckValidity` against a requirement string) — never PID, never bundle-id alone.
- Expose the **minimum** privileged operations; treat all arguments as hostile (no shelling out with caller-controlled strings/paths).
- Set `shouldAcceptNewConnection:` checks; reject connections that fail validation before processing any message.
- Inventory installed helpers; remove unused vendor updaters.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[08 - App Sandbox Escapes]]
- [[09 - Dangerous Entitlements]]
- [[06 - Code Signing and Entitlements]]
- [[12 - Electron Chromium and Interpreted App Injection]]

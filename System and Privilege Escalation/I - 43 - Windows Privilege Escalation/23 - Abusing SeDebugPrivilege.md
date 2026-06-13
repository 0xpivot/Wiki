---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.23 Abusing SeDebugPrivilege"
---

# 23 - Abusing SeDebugPrivilege

## Overview

In the Windows operating system, access to resources and processes is governed by Access Tokens and Privileges. One of the most powerful privileges a user can possess is `SeDebugPrivilege`. 

Originally designed to allow system developers and administrators to debug application crashes and trace system execution, `SeDebugPrivilege` grants the holder the ability to attach a debugger to *any* process on the system, bypassing standard Discretionary Access Control Lists (DACLs). Crucially, this includes highly sensitive system processes like `lsass.exe` (Local Security Authority Subsystem Service) and `winlogon.exe`.

For an attacker, holding `SeDebugPrivilege` is functionally equivalent to holding `SYSTEM` privileges, as it allows for trivial escalation, credential dumping, and process injection. By default, this privilege is granted to Local Administrators.

## The Architecture of SeDebugPrivilege

```text
+--------------------------------------------------------------------------+
|                      SeDebugPrivilege Execution Flow                     |
|                                                                          |
|  +-----------------------+              +-----------------------------+  |
|  | Attacker Process      |              | Target Process (SYSTEM)     |  |
|  | (Has SeDebugPrivilege)|              | e.g., winlogon.exe / lsass  |  |
|  +-----------+-----------+              +-------------+---------------+  |
|              |                                        ^                  |
|              | 1. OpenProcess() with                  |                  |
|              |    PROCESS_ALL_ACCESS                  |                  |
|              |----------------------------------------+                  |
|              |                                                           |
|              | 2. Bypass DACL checks due to SeDebugPrivilege             |
|              |                                                           |
|              | 3. ReadProcessMemory() -> Dump Hashes                     |
|              +---------------------------------------->                  |
|              |                                                           |
|              | 4. CreateRemoteThread() -> Inject Shellcode               |
|              +---------------------------------------->                  |
|                                                                          |
+--------------------------------------------------------------------------+
```

## Deep Dive: Windows Privileges

To check your current privileges, you can run:
```cmd
whoami /priv
```

If you see `SeDebugPrivilege` listed as `Disabled`, do not panic. The token holds the privilege, but it is currently inactive. Offensive tools automatically enable the privilege when needed using the `AdjustTokenPrivileges` API.

If you are running in a High-Integrity context (e.g., an Administrator shell), you will have `SeDebugPrivilege`. If you are in a Medium-Integrity shell (UAC restricted), the privilege is stripped from your token.

## Exploitation Scenarios

### 1. Dumping Credentials from LSASS
The most common abuse of `SeDebugPrivilege` is acquiring a handle to `lsass.exe` to read its memory. LSASS stores NTLM hashes, Kerberos tickets, and occasionally plaintext passwords.

**Using Mimikatz:**
Mimikatz explicitly requests the privilege to operate.
```mimikatz
privilege::debug
token::elevate
sekurlsa::logonpasswords
```

**Using ProcDump (Living off the Land):**
Sysinternals `procdump.exe` is a legitimate Microsoft tool. Attackers use it to dump LSASS memory to a file, bypassing Antivirus behavior heuristics that look for Mimikatz, and then parse the dump file offline.
```cmd
procdump.exe -accepteula -ma lsass.exe C:\Temp\lsass.dmp
```
The `.dmp` file can then be extracted to an attacker machine and parsed:
```mimikatz
sekurlsa::minidump C:\Temp\lsass.dmp
sekurlsa::logonpasswords
```

### 2. Privilege Escalation via Process Injection
If you want a shell as `NT AUTHORITY\SYSTEM`, you can use `SeDebugPrivilege` to inject a malicious payload into a SYSTEM-level process.

Using Metasploit:
```ruby
use post/windows/manage/migrate
set SESSION 1
set PID <Target_SYSTEM_Process_ID>
run
```

Alternatively, custom C# or C++ tooling can use `OpenProcess`, `VirtualAllocEx`, `WriteProcessMemory`, and `CreateRemoteThread` to inject shellcode into processes like `spoolsv.exe` or `winlogon.exe`.

### 3. Parent Process ID (PPID) Spoofing
With `SeDebugPrivilege`, an attacker can duplicate the access token of a SYSTEM process and launch a new process (like `cmd.exe`) that inherits that SYSTEM token. This is fundamentally how PsExec and similar tools elevate from Admin to SYSTEM.

Using an offensive tool like `Invoke-TokenManipulation` (PowerSploit):
```powershell
Invoke-TokenManipulation -CreateProcess "cmd.exe" -Username "NT AUTHORITY\SYSTEM"
```

## Defensive Strategies & Mitigation

1. **Restrict Local Administrators**: Because `SeDebugPrivilege` is granted to the Administrators group by default, the most effective mitigation is strictly limiting who has local admin rights.
2. **Remove the Privilege via GPO**: For specific high-security servers, administrators can manually modify the User Rights Assignment (`Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> User Rights Assignment -> Debug programs`) to remove the Administrators group entirely. This will break debugging tools but significantly harden the server against credential dumping.
3. **LSA Protection (RunAsPPL)**: Enable Local Security Authority Protection. This places `lsass.exe` inside a Protected Process Light (PPL) boundary. Even with `SeDebugPrivilege`, an attacker cannot use `OpenProcess` on `lsass.exe` because PPL overrides the debug privilege.
4. **Credential Guard**: Windows Defender Credential Guard uses virtualization-based security (VBS) to isolate secrets, making memory dumping of `lsass.exe` ineffective even with `SeDebugPrivilege`.

## Detection and Logging

- **Event ID 4656 (A handle to an object was requested)**: Specifically, look for requests targeting `lsass.exe` with `PROCESS_VM_READ` or `PROCESS_ALL_ACCESS` rights originating from non-system binaries.
- **Event ID 4673 (A privileged service was called)**: Triggers when `SeDebugPrivilege` is asserted. This can be noisy due to legitimate administrative tools, so it must be correlated with other events.
- **Sysmon Event ID 10 (ProcessAccess)**: Sysmon provides detailed telemetry when one process opens a handle to another. Filtering for `TargetImage` ending in `lsass.exe` and `GrantedAccess` containing `0x1FFFFF` (All Access) or `0x1010` (Read/Query) is a prime indicator of credential dumping.

## Chaining Opportunities

- **[[20 - Pass the Hash on Local Admin]]**: If you use PtH to gain an administrative session, you immediately inherit `SeDebugPrivilege`, allowing you to dump LSASS.
- **[[19 - DPAPI]]**: You need `SeDebugPrivilege` to extract the DPAPI Master Keys cached inside LSASS.
- **[[28 - Token Impersonation]]**: Process injection and token manipulation rely heavily on the access granted by the debug privilege.

## Related Notes
- [[17 - Stored Credentials Files]]
- [[24 - Abusing SeTakeOwnershipPrivilege]]
- [[22 - LAPS]]

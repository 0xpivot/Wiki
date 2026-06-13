---
tags: [tools, vapt, utility, credential-dumping, memory, active-directory]
difficulty: intermediate
module: "41 - Tools"
topic: "41.18 Mimikatz"
---

# Mimikatz: The Apex Credential Extraction Tool

## 1. Overview and Introduction

Mimikatz, developed by Benjamin Delpy (gentilkiwi), is arguably the most famous and impactful post-exploitation tool in Windows history. Originally developed to demonstrate flaws in Windows authentication protocols, it has evolved into a comprehensive suite for extracting plaintext passwords, hashes, PINs, and Kerberos tickets directly from memory.

For API Security (Module 31), Mimikatz is highly relevant when assessing the backend infrastructure hosting APIs. If an attacker compromises a Windows server running an API via an RCE vulnerability, Mimikatz is used to extract the credentials of the service accounts or domain administrators residing in the server's memory, leading to total network compromise.

## 2. Understanding LSASS (Local Security Authority Subsystem Service)

To understand Mimikatz, one must understand `LSASS.exe`.
LSASS is the process in Windows responsible for enforcing the security policy on the system. It verifies users logging on to a Windows computer or server, handles password changes, and creates access tokens.

To provide features like Single Sign-On (SSO), LSASS caches credentials (often in plaintext or easily reversible formats) in memory using various Security Support Providers (SSPs) such as:
- **WDigest:** Historically stored plaintext passwords for HTTP Digest authentication.
- **Kerberos:** Stores TGTs (Ticket Granting Tickets) and TGSs (Ticket Granting Services).
- **Tspkg:** Used for Remote Desktop authentication.
- **MSV1_0:** Stores NTLM hashes.

Mimikatz requires administrative privileges and `SeDebugPrivilege` to read the memory space of LSASS.

## 3. Architecture and Extraction Diagram

### 3.1 Custom ASCII Attack Diagram

```text
+-------------------------------------------------------+
|             Mimikatz LSASS Memory Extraction          |
+-------------------------------------------------------+
|                                                       |
|  +-------------------+       Read/Write        +----+ |
|  | Mimikatz Process  | ----------------------> |    | |
|  | (High Privileges) |                         |    | |
|  +--------+----------+      SeDebugPrivilege   |    | |
|           |                                    | L  | |
|           |         Extracts Tickets / Hashes  | S  | |
|           +<-----------------------------------+ A  | |
|           |                                    | S  | |
|  +--------v----------+                         | S  | |
|  | Credentials Dump  |                         |    | |
|  | (Wdigest, Kerb)   |                         | .  | |
|  +-------------------+                         | e  | |
|           |                                    | x  | |
|           |          Patching / Injection      | e  | |
|           +----------------------------------> |    | |
|                                                +----+ |
+-------------------------------------------------------+
```

## 4. Core Modules and Commands

Mimikatz operates as an interactive console but can also execute commands directly via the command line.

**Elevating Privileges:**
Before interacting with LSASS, Mimikatz must acquire debug privileges.
```text
mimikatz # privilege::debug
Privilege '20' OK
```

### 4.1 Sekurlsa Module
The `sekurlsa` module is the heart of Mimikatz. It interacts directly with LSASS to extract credentials.

**Dump all logon passwords:**
```text
mimikatz # sekurlsa::logonpasswords
```
*This command parses the WDigest, Kerberos, MSV, and SSP providers to dump plaintext passwords and hashes for all logged-in sessions.*

**Dump Kerberos Tickets:**
```text
mimikatz # sekurlsa::tickets /export
```
*Extracts `.kirbi` files containing Kerberos tickets, which can be reused for Pass-the-Ticket attacks.*

### 4.2 Lsadump Module
Interacts with the LSA to dump secrets, including the SAM database and Domain Controller hashes (DCSync).

**DCSync (Requires Domain Admin/DCSync privileges):**
```text
mimikatz # lsadump::dcsync /domain:target.local /user:Administrator
```
*Simulates a Domain Controller via DRSUAPI to request the password hash of a specific user. This leaves no traces on the target Domain Controller.*

### 4.3 Kerberos Module
Used for creating forged Kerberos tickets (Golden and Silver tickets).

**Creating a Golden Ticket (Requires KRBTGT hash):**
```text
mimikatz # kerberos::golden /admin:Administrator /domain:target.local /sid:S-1-5-21-... /krbtgt:hash /ticket:golden.kirbi
```
*A Golden Ticket is a forged TGT that grants complete, persistent access to the entire domain.*

## 5. Modern Evolutions and In-Memory Execution

Because Mimikatz `.exe` is instantly flagged by every antivirus engine on the planet, attackers rarely drop the binary to disk.

- **Invoke-Mimikatz:** A PowerShell script (part of PowerSploit) that reflectively loads the Mimikatz DLL into memory, bypassing disk-based AV.
- **SharpKatz:** A C# port of Mimikatz functionality designed to be executed via .NET reflection (e.g., via Cobalt Strike's `execute-assembly`).
- **ProcDump:** Attackers often use Microsoft's legitimate Sysinternals `procdump.exe` to create a memory dump of LSASS (`procdump -ma lsass.exe lsass.dmp`), download the dump file to their local machine, and run Mimikatz offline against the dump.

## 6. Detection Mechanisms

- **Process Access:** Monitor for `OpenProcess` API calls targeting `lsass.exe` requesting `PROCESS_VM_READ` or `PROCESS_ALL_ACCESS` rights.
- **Command Line Arguments:** Alert on known Mimikatz commands (`sekurlsa::logonpasswords`, `privilege::debug`).
- **Network Traffic:** Detect DCSync by monitoring for `GetNCChanges` RPC calls coming from IP addresses that are not known Domain Controllers.

## 7. Defenses and Mitigation

1.  **Credential Guard:** Microsoft's Virtualization-Based Security (VBS) isolates the LSASS process in a hypervisor-protected container. Even with SYSTEM privileges, an attacker cannot read LSASS memory.
2.  **LSA Protection:** Configure `RunAsPPL` (Protected Process Light) in the registry to prevent non-PPL processes from opening LSASS.
3.  **Disable WDigest:** Set the registry key `UseLogonCredential` to 0 to prevent plaintext passwords from being stored in memory (Default in Windows 10/Server 2016+).
4.  **Tiered Administration:** Ensure Domain Admins never log into lower-tier workstations, preventing their high-value credentials from ever being cached in a vulnerable LSASS process.

## 8. Conclusion

Mimikatz shifted the paradigm of Windows security. By exposing how easily credentials could be plucked from memory, it forced Microsoft to fundamentally redesign Windows authentication architectures with features like Credential Guard. Despite years of mitigations, understanding and utilizing Mimikatz remains a core competency for any security professional.

---

## Chaining Opportunities
- **[[15 - BloodHound]]:** Use BloodHound to map the shortest path to Domain Admin. If the path requires moving laterally to a machine where a high-privileged user has a session, compromise that machine and use Mimikatz `sekurlsa::logonpasswords` to steal their credentials.
- **[[16 - Impacket]]:** After using Mimikatz to extract an NTLM hash, use Impacket's `psexec.py` or `wmiexec.py` to Pass-the-Hash and execute commands on remote servers.
- **[[20 - Hashcat]]:** If Mimikatz extracts NTLM hashes but Pass-the-Hash is mitigated, export the hashes and use Hashcat to crack them into plaintext.

## Related Notes
- [[11 - Pass the Hash]]
- [[12 - Kerberos Attacks (Golden/Silver Tickets)]]
- [[13 - Windows LSA Internals]]

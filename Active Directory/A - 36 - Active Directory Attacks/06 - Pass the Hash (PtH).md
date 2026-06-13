---
tags: [pth, pass-the-hash, ntlm, active-directory, lateral-movement]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.06 Pass the Hash"
---

# Pass the Hash (PtH)

## 1. Introduction to Pass the Hash (PtH)

Pass the Hash (PtH) is a foundational post-exploitation lateral movement technique used in Windows Active Directory environments. It allows an attacker to authenticate to a remote server or service using the underlying NTLM hash of a user's password, rather than needing the plaintext password itself.

When an attacker compromises a Windows machine and dumps credentials from memory (LSASS) or the local database (SAM), they frequently recover NTLM hashes instead of cleartext passwords. Instead of spending days attempting to crack these hashes offline, the attacker can simply "pass" the hash directly to the authentication protocol to log in.

In the eyes of the NTLM authentication protocol, **the hash IS the password.**

## 2. The NTLM Challenge-Response Mechanics

To understand why PtH works, you must understand the NTLM Challenge-Response protocol.

1. **Negotiate:** The client tells the server it wants to authenticate.
2. **Challenge:** The server sends back a random 8-byte string called the Challenge.
3. **Response:** The client takes the user's NTLM hash, encrypts the server's 8-byte Challenge with it, and sends the result back to the server.
4. **Verification:** The server (or the Domain Controller acting on its behalf) performs the same encryption using the hash stored in its database. If the results match, authentication is granted.

**The Crucial Flaw:** At no point in this process does the client ever need the plaintext password. The mathematical operation relies entirely on the NTLM hash. Therefore, if an attacker possesses the hash, they can perform the client-side encryption perfectly.

## 3. Extracting Hashes

Before you can pass a hash, you must obtain one.
- **LSASS Memory:** The Local Security Authority Subsystem Service (LSASS) caches credentials in memory for active logon sessions. Tools like `Mimikatz` (`sekurlsa::logonpasswords`) dump these hashes.
- **SAM Database:** The local Security Account Manager database stores local account hashes.
- **NTDS.dit:** The Domain Controller's database containing all domain hashes (obtained via DCSync or NTDS extraction).

## 4. Exploitation and Tooling

Once a hash is obtained, numerous tools facilitate passing it.

### 4.1 Mimikatz (Windows)
Mimikatz can inject the hash into the current Windows session, spawning a new process (like `cmd.exe`) running in the context of the compromised user.

**Command:**
```cmd
mimikatz # sekurlsa::pth /user:Administrator /domain:corp.local /ntlm:88e4d9faba6980dc2ef34178bfd6ac2 /run:cmd.exe
```
This spawns a Command Prompt. Any network interaction from this prompt (e.g., `dir \\target-server\c$`) will seamlessly authenticate as the Administrator using the injected hash.

### 4.2 Impacket Suite (Linux)
Impacket provides several scripts that accept a hash instead of a password for remote execution.

**wmiexec.py (Stealthy, uses WMI/RPC):**
```bash
wmiexec.py -hashes :88e4d9faba6980dc2ef34178bfd6ac2 corp.local/Administrator@192.168.1.50
```
**psexec.py (Loud, creates a service):**
```bash
psexec.py -hashes :88e4d9faba6980dc2ef34178bfd6ac2 corp.local/Administrator@192.168.1.50
```
**smbexec.py (Stealthier alternative to psexec):**
```bash
smbexec.py -hashes :88e4d9faba6980dc2ef34178bfd6ac2 corp.local/Administrator@192.168.1.50
```
*Note: The format is `LMHASH:NTHASH`. Since LM hashes are obsolete, it is usually prepended with a colon `:NTHASH`.*

### 4.3 CrackMapExec / NetExec
Excellent for spraying a hash across an entire subnet to find out where the compromised user has local admin rights.
```bash
nxc smb 192.168.1.0/24 -u Administrator -H 88e4d9faba6980dc2ef34178bfd6ac2 --local-auth
```

### 4.4 Evil-WinRM
If WinRM (Port 5985) is enabled, Evil-WinRM provides an interactive PowerShell shell using PtH.
```bash
evil-winrm -i 192.168.1.50 -u Administrator -H 88e4d9faba6980dc2ef34178bfd6ac2
```

## 5. Overpass the Hash (PtH to PtT)

A severe limitation of traditional PtH is that it relies on NTLM. If a network strictly enforces Kerberos, NTLM PtH will fail. 
**Overpass the Hash** solves this. Instead of using the hash for NTLM authentication, the attacker uses the NTLM hash to request a Kerberos Ticket Granting Ticket (TGT) from the Domain Controller. 

Once the TGT is obtained, the attacker transitions to a "Pass the Ticket" (PtT) attack, moving laterally using native, fully trusted Kerberos tickets. Tools like Rubeus (`asktgt /rc4:<hash>`) facilitate this.

## 6. ASCII Workflow Diagram

```text
========================================================================
                      PASS THE HASH (PtH) WORKFLOW
========================================================================

 [ Compromised Host A ]                         [ Target Server B ]
           |                                             |
  1. Dump LSASS / SAM                                    |
     (Gets NTLM Hash: 88e4d...)                          |
           |                                             |
  2. Mimikatz sekurlsa::pth                              |
     (Spawns cmd.exe)                                    |
           |                                             |
  3. cmd.exe attempts access --------------------------> |
     (Negotiate NTLM Auth)                               |
           |                                             |
           | <------------------------------------------ |
           | (Server sends 8-byte Challenge)             |
           |                                             |
  4. Client encrypts challenge                           |
     using the dumped NTLM Hash                          |
           |                                             |
           | ------------------------------------------> |
           | (Sends Response)                            |
           |                                             |
           |                                 [ Local Auth / DC Auth ]
           |                                  Validates Response
           |                                             |
  5. Access Granted! <---------------------------------- |
     (Attacker gets remote shell via SMB/WMI/WinRM)
========================================================================
```

## 7. Limitations and Local Account Restrictions

Microsoft introduced restrictions (via KB2871997 and Windows 10 updates) to limit PtH for **Local** accounts.
- **Built-in Local Administrator (RID 500):** Can still PtH everywhere by default.
- **Other Local Admins:** Will be stripped of administrative privileges during network logon (UAC Remote Restrictions). PtH will authenticate, but you will not have admin rights, causing WMI/SMBExec to fail.
- **Domain Accounts:** Not affected by this restriction. A domain admin hash can be passed anywhere freely.

## 8. Defenses and Mitigation

1. **LAPS (Local Administrator Password Solution):** Randomizes local administrator passwords across the domain, breaking lateral movement via local admin PtH.
2. **Credential Guard:** A Windows virtualization-based security feature that isolates LSASS secrets in a protected memory container, preventing attackers from dumping the hashes in the first place.
3. **Restricted Admin Mode:** Prevents credentials of administrators logging into compromised machines from being stored in memory, stopping attackers from harvesting their hashes.
4. **Tiered Administration:** Ensuring Domain Admins only log into Tier 0 assets (DCs), never Tier 2 assets (Workstations) where their hashes could be stolen.

## 9. Chaining Opportunities

- PtH is the execution phase. The hashes passed are usually obtained by dumping memory, or by successfully executing **[[04 - Kerberoasting]]** or **[[05 - AS-REP Roasting]]** and cracking the resulting hash to get the plaintext (though PtH skips cracking entirely if you just have the NT hash).
- Extensive **[[02 - AD Enumeration]]** dictates *where* the attacker should pass the hash to gain maximum leverage.

## 10. Related Notes

- **[[01 - Active Directory Overview]]**
- **[[02 - AD Enumeration]]**
- **[[04 - Kerberoasting]]**
- **[[05 - AS-REP Roasting]]**

## Real-World Attack Scenario
## Real-World Attack Scenario

The attacker had successfully compromised a mid-level manager's laptop (`LAPTOP-104`) via a malicious macro in an Excel document.
After escalating privileges locally to SYSTEM using a kernel exploit, they dumped the local SAM database and LSASS memory.
Among the extracted credentials was the NTLM hash for the built-in local `Administrator` account: `31d6cfe0d16ae931b73c59d7e0c089c0`.
The environment strictly enforced complex, randomly generated passwords for domain users, making cracking impractical.
However, the attacker suspected that the IT department might have reused the same local `Administrator` password across multiple workstations.
This is a common misconfiguration known as local admin password reuse.
To test this hypothesis and move laterally without needing the plaintext password, the attacker employed a Pass the Hash (PtH) attack.
They used CrackMapExec (CME) from their attacking machine, targeting the entire `/24` workstation subnet.
The command executed was: `cme smb 10.0.1.0/24 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0 --local-auth`.
CME systematically attempted to authenticate to the SMB service on every IP address using the provided NTLM hash.
The results scrolled across the screen, showing "Pwn3d!" on 15 different workstations.
The attacker's suspicion was correct; the local administrator hash was valid across a significant portion of the network.
They focused on one of the compromised machines, `LAPTOP-210`, which belonged to a senior network engineer.
Using the Impacket suite, the attacker executed `psexec.py megacorp/Administrator@10.0.1.210 -hashes :31d6cfe0d16ae931b73c59d7e0c089c0`.
The PtH authentication succeeded, granting the attacker a highly privileged SYSTEM shell on the engineer's machine.
From this new vantage point, they dumped the LSASS memory of `LAPTOP-210`.
The engineer had recently logged in with their highly privileged Domain Admin account, `admin_engineer`.
The LSASS dump revealed the plaintext password for the `admin_engineer` account.
By passing a local hash, the attacker had hopped across the network, targeted a high-value user, and captured the keys to the kingdom.
The PtH technique proved invaluable in an environment where cracking complex passwords was not feasible.


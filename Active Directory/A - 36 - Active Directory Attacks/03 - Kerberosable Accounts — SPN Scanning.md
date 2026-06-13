---
tags: [spn, kerberos, active-directory, reconnaissance, evasion]
difficulty: intermediate
module: "36 - Active Directory Attacks"
topic: "36.03 Kerberosable Accounts - SPN Scanning"
---

# Kerberosable Accounts — SPN Scanning

## 1. Introduction to Service Principal Names (SPNs)

In an Active Directory environment leveraging Kerberos authentication, services must be uniquely identified so that the Key Distribution Center (KDC) knows which account's password to use when encrypting the Service Ticket (TGS). This unique identifier is called a Service Principal Name (SPN).

An SPN is a string attribute (`servicePrincipalName`) attached to an Active Directory object (either a Computer account or a User account). When a client wishes to authenticate to a service (like an SQL database, a web server, or a file share), it requests a Kerberos ticket for that specific SPN.

### 1.1 SPN Format Structure
The standard format for an SPN is:
`<ServiceClass>/<Host>:<Port>/<ServiceName>`

- **ServiceClass:** The type of service (e.g., `MSSQLSvc`, `HTTP`, `cifs`, `ldap`).
- **Host:** The FQDN or NetBIOS name of the computer hosting the service.
- **Port:** (Optional) The TCP/UDP port the service runs on.
- **ServiceName:** (Optional) Often used for replicated services or specific database names.

**Examples:**
- `HTTP/webserver01.corp.local`
- `MSSQLSvc/db01.corp.local:1433`
- `cifs/fileserver.corp.local`

## 2. SPN Mapping: Computer vs. User Accounts

SPNs can be mapped to two types of accounts in Active Directory:

1. **Computer Accounts (`MachineAccount$`)**: By default, when a Windows machine joins a domain, several default SPNs (like `HOST/`, `cifs/`) are automatically mapped to the machine's computer account. The password for this account is a long, randomly generated, 120-character string managed by the domain.
2. **User Accounts (Service Accounts)**: Often, enterprise applications (like Microsoft SQL Server, IIS Application Pools, or custom third-party services) require domain permissions. Administrators create a standard AD User account to run these services and manually register an SPN to that user account. 

### 2.1 The Concept of "Kerberosable Accounts"
The term "Kerberosable Accounts" (often synonymous with "Kerberoastable accounts") refers specifically to the second category: **Domain User accounts that have an SPN mapped to them.** 

Because these are standard user accounts, their passwords are created by humans, heavily prone to falling short of complexity requirements, and rarely rotated compared to machine account passwords.

## 3. Why SPN Scanning is Powerful (OPSEC)

Traditionally, attackers would find services on a network by performing active port scans (e.g., using `nmap`). Port scanning requires sending thousands of packets across the network to every IP address, interacting with firewalls, triggering IDS/IPS alerts, and leaving massive footprints.

**SPN Scanning is the OPSEC-safe alternative.**
Instead of actively touching the target endpoints, an attacker simply asks the Active Directory Domain Controller (via LDAP): 
*"Can you give me a list of all accounts that have a `servicePrincipalName` attribute set?"*

This is standard network behavior. The DC happily responds with the list. From this list, the attacker instantly knows:
1. What services are running in the domain.
2. Which servers are hosting them.
3. Which user accounts are running them.
4. The exact ports they are listening on.

All of this intelligence is gathered without sending a single packet to the actual target servers.

## 4. Tools for SPN Scanning

Multiple tools exist for executing an SPN scan depending on the operating environment.

### 4.1 setspn.exe
`setspn.exe` is a legitimate, built-in Microsoft binary used by administrators to read, modify, and delete SPN directory properties. It functions as an excellent "living off the land" (LotL) binary.

**Command:**
```cmd
setspn.exe -T corp.local -Q */*
```
This queries the `corp.local` domain for any object matching `*/*` in the SPN field, effectively dumping all SPNs.

### 4.2 PowerView
PowerView, part of the PowerSploit framework, provides highly targeted PowerShell cmdlets for SPN enumeration. It allows for advanced filtering, such as ignoring computer accounts.

**Command to find only User accounts with SPNs (High value targets):**
```powershell
Get-DomainUser -SPN | Select-Object sAMAccountName, servicePrincipalName
```

### 4.3 Impacket's GetUserSPNs.py
From a Linux attack machine, Impacket is the tool of choice. `GetUserSPNs.py` queries LDAP for user accounts with SPNs and can optionally request the TGS tickets directly for Kerberoasting.

**Command:**
```bash
GetUserSPNs.py corp.local/username:password -dc-ip 192.168.1.10
```

## 5. ASCII Diagram of SPN Resolution

```text
========================================================================
                   SPN RESOLUTION IN KERBEROS
========================================================================

[ Attacker / Client ]                                   [ Domain Controller ]
         |                                                       |
         | --- 1. LDAP Query: "Find objects with SPNs" --------> |
         |                                                       |
         | <--- 2. Returns SPNs (e.g., MSSQLSvc/sql01:1433) ---- |
         |                                                       |
         | --- 3. TGS-REQ: "I want to access MSSQLSvc/sql01" --> |
         |        (Client asks for a Service Ticket)             |
         |                                                       |
         | <--- 4. TGS-REP: Service Ticket returned ------------ |
         |        (Ticket is encrypted with the Service          |
         |         Account's NTLM hash)                          |
         |                                                       |
 [ Offline Crack ]                                               |
 (Attacker attempts to extract plaintext password)               |
========================================================================
```

## 6. Analyzing SPN Scanning Output

When you run an SPN scan, the objective is to filter out the noise.
- **Ignore:** Any account ending in `$`. These are machine accounts. Their passwords are 120 characters long and practically uncrackable offline.
- **Target:** Standard user accounts (e.g., `svc_mssql`, `svc_apache`, `sqladmin`).
- **Analyze:** Look at the `ServiceClass`. An SPN of `MSSQLSvc` means you found a database. An SPN of `WinRM` means remote management is enabled.

## 7. Defense and Detection

Defending against SPN scanning is notoriously difficult because LDAP querying is a fundamental feature of Active Directory.

- **Detection:** Watch for abnormal volumes of LDAP queries targeting the `servicePrincipalName` attribute. Advanced EDR and MDI platforms use behavioral analytics to detect tools like PowerView executing large-scale LDAP sweeps.
- **Honey SPNs:** Defenders can create fake user accounts with SPNs (Honeytokens). Because legitimate users have no reason to request a ticket for a fake service, any TGS request for that SPN will immediately trigger a high-fidelity alert in the SIEM.

## 8. Chaining Opportunities

SPN Scanning is the reconnaissance phase for one of the most critical Active Directory attacks:
- The direct and immediate next step after mapping SPNs to User Accounts is executing **[[04 - Kerberoasting]]** to extract the service tickets and crack the passwords offline.
- If the identified service account has administrative privileges, cracking it leads directly to domain dominance.
- The enumeration phase for finding these SPNs overlaps with generalized **[[02 - AD Enumeration]]**.

## 9. Related Notes

- **[[01 - Active Directory Overview]]**
- **[[02 - AD Enumeration]]**
- **[[04 - Kerberoasting]]**
- **[[05 - AS-REP Roasting]]**
- **[[06 - Pass the Hash (PtH)]]**

## Real-World Attack Scenario
## Real-World Attack Scenario

Having established a foothold in the `megacorp.local` domain, the attacker needed to identify valuable target services.
Instead of running a noisy `nmap` scan across the /16 subnet, which would immediately trigger the IDS/IPS, they opted for an OPSEC-safe SPN scan.
The attacker knew that enterprise applications often run under the context of standard domain user accounts.
These service accounts require Service Principal Names (SPNs) to function within the Kerberos authentication framework.
From the compromised Windows host, the attacker used the built-in `setspn.exe` utility to query Active Directory.
They executed `setspn.exe -T megacorp.local -Q */*`, redirecting the output to a text file for offline analysis.
The LDAP query asked the Domain Controller for all objects with a populated `servicePrincipalName` attribute.
The DC responded with a massive list, which the attacker meticulously filtered.
They ignored any SPNs ending with a `$` character, as these belonged to machine accounts with uncrackable 120-character passwords.
Instead, they focused on user accounts associated with high-value services.
They discovered an SPN formatted as `MSSQLSvc/sql01.megacorp.local:1433`, mapped to the user account `svc_sqladmin`.
This single LDAP query revealed four critical pieces of intelligence:
1. An MS SQL Server was running in the environment.
2. The service was hosted on `sql01.megacorp.local`.
3. It was listening on the default port `1433`.
4. It was running under the context of the `svc_sqladmin` domain user account.
All of this was achieved without sending a single packet to the `sql01` server itself.
The attacker realized that `svc_sqladmin` was a prime target for a Kerberoasting attack.
Because the account was a standard user account, its password was likely set by a human and potentially weak.
Furthermore, as an SQL administrator account, compromising it could lead to code execution on the database server via `xp_cmdshell`.
The SPN scanning phase was completed in seconds, leaving virtually no footprint, and perfectly setting the stage for the next phase of the attack.
The attacker now had a precise target list, prioritizing the `svc_sqladmin` account for immediate exploitation.


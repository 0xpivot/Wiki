---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.22 LAPS"
---

# 22 - LAPS (Local Administrator Password Solution)

## Overview

The Local Administrator Password Solution (LAPS) is a Microsoft tool designed to eliminate the risk of Pass the Hash (PtH) and lateral movement attacks utilizing identical local administrator passwords. LAPS automatically manages the passwords of local administrator accounts on domain-joined computers. 

It accomplishes this by randomizing the password for each machine, changing it on a scheduled basis, and storing the plaintext password securely in Active Directory as a computer object attribute. Access to read this attribute is heavily restricted via Access Control Lists (ACLs). However, misconfigurations in these ACLs, or compromising a user who legitimately possesses the rights to read LAPS passwords, can instantly give an attacker SYSTEM-level access to machines across the domain.

## The Architecture of LAPS

```text
+--------------------------------------------------------------------------+
|                            LAPS Architecture                             |
|                                                                          |
|  +--------------------+        1. Generates        +-------------------+ |
|  | Target Workstation |       Random Password      | Domain Controller | |
|  | (LAPS Client DLL)  |--------------------------->| (Active Directory)| |
|  +--------------------+                            +---------+---------+ |
|                                                              |           |
|                                2. Stores in AD Attribute     |           |
|                                   `ms-Mcs-AdmPwd`            v           |
|                                                    +-------------------+ |
|  +--------------------+        3. Query AD         | Computer Object   | |
|  | Attacker / Admin   |--------------------------->| (ACL Check applied| |
|  | (Domain context)   |<---------------------------| to read attribute)| |
|  +--------------------+   4. Returns Plaintext     +-------------------+ |
|                              Password (if ACL                            |
|                              permits)                                    |
+--------------------------------------------------------------------------+
```

## Deep Dive: How LAPS Works

LAPS extends the Active Directory schema to add two specific attributes to Computer objects:
1. `ms-Mcs-AdmPwd`: Stores the plaintext local administrator password.
2. `ms-Mcs-AdmPwdExpirationTime`: Stores the timestamp of when the password will expire and automatically rotate.

By default, only Domain Admins have the permission to read the `ms-Mcs-AdmPwd` attribute. However, in enterprise environments, Help Desk users, local IT support teams, or specific service accounts are often delegated this permission so they can perform troubleshooting. If these delegated groups are improperly nested or overly broad, an attacker who compromises a standard user account might unexpectedly inherit the ability to read LAPS passwords.

### Windows LAPS (Modern) vs Legacy LAPS
In 2023, Microsoft introduced "Windows LAPS" natively built into Windows 11 and Server 2022. 
- **Legacy LAPS**: Passwords are stored in plaintext in AD.
- **Windows LAPS**: Passwords can be stored encrypted in AD, or even stored in Azure AD (Entra ID). This significantly mitigates the risk of unauthorized read access, as decryption requires separate DSRM or Domain Admin rights.

## Exploitation Scenarios

### 1. Enumerating LAPS Permissions via BloodHound
The most effective way to abuse LAPS is to find out *who* is allowed to read the passwords. BloodHound naturally maps this using the `ReadLAPSPassword` edge.

If you compromise a user, you can query BloodHound to see if that user (or any group they belong to) has `ReadLAPSPassword` over specific computers or Organizational Units (OUs). 

### 2. Reading LAPS Passwords via PowerShell
If your current user context has the rights to read LAPS passwords, you can extract them easily using built-in PowerShell commands or Active Directory modules.

Using PowerView:
```powershell
Get-DomainComputer -Properties Name, ms-Mcs-AdmPwd | Where-Object { $_.'ms-Mcs-AdmPwd' -ne $null }
```

Using LAPSToolkit (a specialized offensive script):
```powershell
Import-Module .\LAPSToolkit.ps1
# Find computers with LAPS and attempt to read the password
Get-LAPSComputers
# Find groups that have been delegated read access
Find-LAPSDelegatedGroups
```

### 3. Reading LAPS using CrackMapExec / NetExec
If you have valid credentials for a delegated user, you can use NetExec to extract LAPS passwords remotely via LDAP.

```bash
netexec ldap 192.168.1.10 -u 'HelpDeskUser' -p 'Password123' --laps
```

### 4. Dumping LAPS Passwords from Memory (Bypassing AD ACLs)
If you have already compromised a host (e.g., via a software vulnerability) but need the local admin password to create persistence, you can extract the LAPS password directly from the local machine's memory without interacting with AD.
When the LAPS client updates the password, it temporarily resides in memory. Additionally, LAPS configurations can be inspected locally.

## Defensive Strategies & Mitigation

1. **Strict ACL Auditing**: Administrators must meticulously audit the permissions on the `ms-Mcs-AdmPwd` attribute. Never assign `All Extended Rights` to an OU, as this implicitly grants LAPS read access.
2. **Tiered Administration**: Users who can read LAPS passwords for workstations (Tier 2) should absolutely not be able to read LAPS passwords for Servers (Tier 1) or Domain Controllers (Tier 0).
3. **Migrate to Windows LAPS**: Modern environments should migrate away from legacy LAPS to the new native Windows LAPS, utilizing Password Encryption. This ensures that even if an attacker bypasses the ACL, they only retrieve an encrypted blob.
4. **Monitor Expiration Timestamps**: Ensure that computers are regularly checking in and rotating their passwords.

## Detection and Logging

- **Event ID 4662 (An operation was performed on an object)**: Monitor access to the Active Directory attribute `ms-Mcs-AdmPwd`. If a user account suddenly queries this attribute for hundreds of computers simultaneously (as LAPSToolkit or BloodHound would), trigger a high-severity alert.
- **LAPS Event Logs**: LAPS writes logs to the `Applications and Services Logs -> LAPS` channel. 
- **Decoy Computers**: Create a fake computer object in Active Directory, populate the `ms-Mcs-AdmPwd` attribute, and monitor for any user attempting to read it.

## Chaining Opportunities

- **[[20 - Pass the Hash on Local Admin]]**: LAPS is specifically designed to kill Pass the Hash. If LAPS is active, you cannot use PtH across the fleet.
- **[[28 - Token Impersonation]]**: If you compromise a host and find a Help Desk user logged in, you can impersonate their token to read LAPS passwords for other machines.
- **[[19 - DPAPI]]**: Extracting LAPS credentials gives you full SYSTEM access, allowing you to extract DPAPI master keys.

## Related Notes
- [[17 - Stored Credentials Files]]
- [[21 - Password in GPP]]
- [[23 - Abusing SeDebugPrivilege]]

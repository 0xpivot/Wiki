---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.09 Service Principal Names SPNs and Delegation"
---

# Service Principal Names (SPNs) and Delegation

## 1. Introduction

In modern Active Directory environments, services (like web servers, SQL databases, or file shares) frequently need to authenticate users and sometimes act on their behalf to access backend resources. To facilitate this securely within the Kerberos protocol, Active Directory relies on **Service Principal Names (SPNs)** and **Delegation**. 
Misconfigurations in SPNs and Delegation are among the most reliably abused privilege escalation vectors in AD penetration testing.

## 2. Service Principal Names (SPNs)

### 2.1 What is an SPN?
An SPN is a unique identifier for a service instance running on a server. When a client wants to connect to a service using Kerberos, it must know the SPN of that service to request a Service Ticket (TGS) from the Key Distribution Center (KDC).

SPNs act as the glue between the Kerberos protocol and the Active Directory accounts running the services.

### 2.2 SPN Anatomy
An SPN is a string value stored in the `servicePrincipalName` attribute of an AD User or Computer object.
Format: `ServiceClass/Host:Port/ServiceName`

Examples:
- `CIFS/FS01.domain.com` (File Share on FS01)
- `HTTP/intranet.domain.com` (Web server)
- `MSSQLSvc/sql01.domain.com:1433` (SQL Server on port 1433)

### 2.3 SPN Resolution Flow
When a user types `\\FS01.domain.com` into Explorer:
1. The client determines the service class is `CIFS` and the target is `FS01.domain.com`.
2. The client asks the KDC (Domain Controller): *"Please give me a ticket for CIFS/FS01.domain.com"*.
3. The KDC searches the Active Directory database for any account that has `CIFS/FS01.domain.com` listed in its `servicePrincipalName` attribute.
4. The KDC encrypts the Service Ticket using the password hash of the account it found, and returns it to the client.

## 3. Delegation in Active Directory

Delegation is the ability of a service to impersonate a user. 
Scenario: A user authenticates to a Web Server. The Web Server then needs to query a backend SQL Database *as that user* to retrieve their specific payroll data. The Web Server must be "delegated" the authority to pass the user's identity forward.

Active Directory provides three types of delegation, evolving over time due to security concerns.

### 3.1 Unconstrained Delegation
The oldest and most dangerous form of delegation.
- **How it works**: When a user authenticates to a server configured with Unconstrained Delegation, the KDC bundles the user's **Ticket Granting Ticket (TGT)** inside the Service Ticket. The server extracts this TGT, caches it in its local LSASS memory, and can use it to impersonate the user to **any** other service in the domain.
- **The Risk**: If an attacker compromises a server with Unconstrained Delegation, they can harvest the TGT of anyone who authenticates to it. Attackers often force Domain Controllers to authenticate to these compromised servers (via the Printer Bug / SpoolSample or PetitPotam) to capture a DC machine account TGT, leading to instant domain compromise.

### 3.2 Constrained Delegation
Introduced in Windows Server 2003 to fix the massive risks of Unconstrained Delegation.
- **How it works**: The service is only allowed to impersonate users to a **specifically defined list of target services** (e.g., the Web Server can only delegate to `MSSQLSvc/sql01.domain.com`).
- **Extensions**: Relies on two Kerberos extensions:
  - **S4U2Self (Service for User to Self)**: Allows a service to request a Kerberos ticket for itself on behalf of any user, without needing the user's password (Protocol Transition).
  - **S4U2Proxy (Service for User to Proxy)**: Allows the service to take the ticket obtained via S4U2Self and forward it to the KDC to get a ticket for the constrained backend service.
- **The Risk**: If an attacker compromises the frontend service account, they can abuse S4U2Self/S4U2Proxy to impersonate **any** domain user (including Domain Admins) to the specified backend service.

### 3.3 Resource-Based Constrained Delegation (RBCD)
Introduced in Windows Server 2012, RBCD flips the configuration model.
- **How it works**: Instead of configuring the *frontend* service to dictate where it can delegate to, the *backend target* resource dictates who is allowed to delegate to it.
- **Mechanism**: Managed via the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on the target object.
- **The Risk**: If an attacker has `GenericWrite` or `WriteProperty` over a target computer object, they can modify this attribute to point to a machine account they control. They can then perform an RBCD attack to impersonate a Domain Admin to the target machine, achieving remote code execution as SYSTEM.

## 4. Architecture Visualization (Delegation Types)

```text
=========================================================
1. UNCONSTRAINED DELEGATION (Total Trust)
=========================================================
User ---> [Web Server] ---> [Any Service]
             |
        (Holds User's TGT)

=========================================================
2. CONSTRAINED DELEGATION (Target list defined on Frontend)
=========================================================
User ---> [Web Server] ---> [SQL Server ONLY]
             |
    (msDS-AllowedToDelegateTo = MSSQLSvc/sql01)

=========================================================
3. RBCD (Allowed list defined on Backend Target)
=========================================================
[Attacker Machine] ---> [Target Server]
                              |
                 (msDS-AllowedToActOnBehalfOfOtherIdentity 
                  = Attacker Machine SID)
```

## 5. Offensive Perspective: Kerberoasting

Because any authenticated user can request a Service Ticket for any SPN, and the ticket is encrypted with the target service account's password hash, attackers perform **Kerberoasting**.
1. **Enumerate**: Query LDAP for all user objects with an SPN set (`servicePrincipalName=*`). (Note: We target User objects, not Computer objects, because computer account passwords are 120-character randomized strings, while user service accounts often have weak, human-created passwords).
2. **Request**: Ask the KDC for Service Tickets for those SPNs.
3. **Extract**: Dump the tickets from memory (e.g., using Rubeus).
4. **Crack**: Use Hashcat or John the Ripper to brute-force the RC4-encrypted ticket offline.

## 6. Offensive Perspective: Abusing Delegation

- **Unconstrained**: Compromise the server, use Rubeus to monitor for incoming TGTs (`Rubeus harvest /interval:1`), trigger a coerced authentication (Printer Bug) from a DC, and inject the captured DC TGT to perform DCSync.
- **Constrained**: Compromise the delegated service account, generate an S4U2Self ticket for the `Administrator` user, and use S4U2Proxy to access the backend target as the Administrator.
- **RBCD**: Gain `GenericWrite` over a target computer. Create a fake machine account using `addcomputer.py` (abusing `MachineAccountQuota`). Write the fake machine's SID to the target's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. Execute the S4U extensions using `getST.py` to impersonate an admin and gain SYSTEM access.

## 7. Remediation and Hardening

- **Account is sensitive and cannot be delegated**: Check this flag on the User Account properties for all highly privileged accounts (Domain Admins). This prevents their credentials from ever being forwarded, neutralizing delegation abuse against them.
- **Protected Users Group**: Add highly privileged administrators to the Protected Users security group, which automatically blocks Kerberos delegation.
- **Audit SPNs**: Ensure no Domain Admin accounts have SPNs assigned, as this exposes their hash to Kerberoasting. Use Managed Service Accounts (gMSA) for services, which have auto-rotating 120-character passwords.
- **Disable Unconstrained Delegation**: Identify all computers with the `TRUSTED_FOR_DELEGATION` flag and migrate them to Constrained Delegation or RBCD.

## Real-World Attack Scenario

**The Context:** An attacker has compromised a standard domain user (`t.stark`). Through BloodHound reconnaissance, they discover that `t.stark` was historically granted `GenericWrite` permissions over an older Exchange server (`EXCH01$`). The goal is to gain full remote command execution on `EXCH01$`.

**The Thought Process:** The attacker cannot directly extract passwords or modify the local Administrators group of `EXCH01$` with just `GenericWrite`. However, `GenericWrite` allows the attacker to modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. By abusing Active Directory's `MachineAccountQuota` (default set to 10), the attacker can create a fake computer account, write its SID into the Exchange server's RBCD attribute, and then use Kerberos extensions (S4U2Self/S4U2Proxy) to impersonate a Domain Admin directly to the Exchange server.

**The Execution:**
1. **Creating the Fake Computer:** The attacker uses `addcomputer.py` to create a new machine account in AD called `EVILPC$`.
   `addcomputer.py corp.local/t.stark:Password123 -computer-name EVILPC$ -computer-pass EvilPass1!`
2. **Modifying the Target:** The attacker uses `rbcd.py` to write the SID of `EVILPC$` into the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target `EXCH01$`.
   `rbcd.py -delegate-to EXCH01$ -delegate-from EVILPC$ -action write corp.local/t.stark:Password123`
3. **Executing S4U Extensions:** The attacker uses `getST.py` to request a Service Ticket for `EXCH01$`, impersonating the `Administrator` user. The script automatically handles the S4U2Self and S4U2Proxy Kerberos requests.
   `getST.py -spn cifs/EXCH01.corp.local -impersonate Administrator corp.local/EVILPC$:EvilPass1!`
4. **Pass-the-Ticket:** The tool outputs a `.ccache` file containing the forged Service Ticket. The attacker exports this file to their environment variables and accesses the server.
   `export KRB5CCNAME=Administrator.ccache; smbclient.py -k -no-pass @EXCH01.corp.local`

**The Outcome:** The attacker successfully exploited the `GenericWrite` ACL to configure RBCD, bypassing all local protections to gain full `SYSTEM`-level remote execution on the target Exchange server without needing to crack any passwords or interact with Domain Admins.

## 8. Chaining Opportunities

- **BloodHound -> RBCD**: Find a user with `GenericWrite` over a critical server, capture the user's hash via PtH, and use `Impacket` to execute an RBCD attack to compromise the server.
- **Kerberoasting -> Silver Ticket**: Successfully crack a Kerberoastable account to get its NTLM hash. If that account runs a service on a target machine, forge a Silver Ticket to gain persistence and local admin access to that service.

## 9. Related Notes

- [[08 - NTLM vs Kerberos Authentication Basics]]
- [[07 - Access Control Lists ACLs and Access Control Entries ACEs]]
- [[01 - Active Directory Structure and Components]]

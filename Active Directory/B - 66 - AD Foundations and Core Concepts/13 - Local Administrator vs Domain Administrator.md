---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.13 Local Administrator vs Domain Administrator"
---

# Local Administrator vs. Domain Administrator

In Active Directory environments, understanding the fundamental security boundaries and the distinction between local system authorities and domain-wide authorities is critical for comprehending privilege escalation and lateral movement. Misunderstanding this hierarchy is a primary reason why organizations fall victim to widespread ransomware and total domain compromise.

## The Two Authentication Databases

To understand the difference between Local Admins and Domain Admins, one must understand where identities are stored and evaluated.

1.  **The SAM Database (Security Account Manager):**
    *   **Location:** `C:\Windows\System32\config\SAM`
    *   **Scope:** Local to the specific endpoint or server.
    *   **Function:** Stores local user accounts (e.g., `.\Administrator`, `.\Guest`). When you log in as `HOSTNAME\Administrator`, Windows verifies the hash against this local database.

2.  **The NTDS.dit Database (NT Directory Services):**
    *   **Location:** `C:\Windows\NTDS\ntds.dit` (Only on Domain Controllers).
    *   **Scope:** The entire Active Directory domain.
    *   **Function:** Stores domain user accounts, groups, and computer accounts. When you log in as `DOMAIN\Administrator`, the authentication request is forwarded via Kerberos or NTLM to a Domain Controller for verification against `NTDS.dit`.

## Local Administrator: Scope and Limitations

A **Local Administrator** has the highest level of privilege on a *single, specific machine*. 
*   They can install software, change registry keys, dump local memory (LSASS), and manipulate local firewalls.
*   **The Limitation:** By default, a Local Administrator on `Workstation A` has absolutely zero rights on `Workstation B` or the `Domain Controller`. They cannot reset domain passwords, add users to domain groups, or access central file shares.
*   **The Risk:** If local administrator passwords are identical across multiple machines (a historically common IT practice), an attacker who compromises one machine can extract the local admin password hash and use **Pass-the-Hash (PtH)** to move laterally to every other machine in the network.

## Domain Administrator: The Keys to the Kingdom

A **Domain Administrator** is a member of the highly privileged `Domain Admins` group.
*   **Scope:** By default, the `Domain Admins` group is added to the local `Administrators` group of *every single machine* that joins the domain.
*   **Capabilities:** They can manage the `NTDS.dit` database, reset any user's password, modify Group Policy Objects (GPOs), deploy software forest-wide, and log into any Domain Controller.
*   **The Risk:** Because Domain Admins have local admin rights everywhere, they often log into standard workstations to perform IT support. This leaves their highly privileged credentials (or hashes/tickets) residing in the workstation's memory (LSASS), ripe for extraction by attackers who have already compromised the workstation.

## ASCII Diagram: Privilege Hierarchies & Attack Paths

```text
+---------------------------------------------------------------+
|                      THE DOMAIN BOUNDARY                      |
|                                                               |
|   +-------------------+              +--------------------+   |
|   | WORKSTATION 01    |              | DOMAIN CONTROLLER  |   |
|   | SAM Database      |              | NTDS.dit Database  |   |
|   | - .\LocalAdmin    |              | - LAB\Administrator|   |
|   | - .\UserA         |              | - LAB\DomainAdmins |   |
|   +-------------------+              +--------------------+   |
|           ^                                   ^               |
|           | Local Admin Rights                | Domain Rights |
|           v                                   v               |
|    [ ATTACKER ]                       [ DOMAIN ADMIN ]        |
|    Compromises WK-01                  Logs into WK-01 for IT  |
|    Dumps SAM hashes                   Support via RDP.        |
|                                                               |
|   +-------------------+                                       |
|   | WORKSTATION 02    | <--- PtH --- [ ATTACKER ] dumps DA    |
|   | SAM Database      | (Lateral)    hash from WK-01 memory.  |
|   | - .\LocalAdmin    |              Attacker is now DA!      |
|   +-------------------+              (Vertical Escalation)    |
|                                                               |
+---------------------------------------------------------------+
```

## AdminSDHolder and SDProp

Active Directory employs a self-healing mechanism to protect highly privileged groups (like Domain Admins, Enterprise Admins, and Backup Admins). 
*   **AdminSDHolder:** A container object located at `CN=AdminSDHolder,CN=System,DC=domain,DC=com`. It acts as a template for security permissions.
*   **SDProp (Security Descriptor Propagator):** A background process that runs every 60 minutes on the PDC Emulator. It compares the Access Control Lists (ACLs) of protected groups and their members against the `AdminSDHolder` template.
*   **Impact:** If an attacker modifies the ACL of a Domain Admin to grant themselves persistent control, SDProp will overwrite the attacker's changes within an hour. 
*   **Exploitation:** Attackers will instead modify the ACL of the `AdminSDHolder` object itself. When SDProp runs, it will propagate the attacker's backdoor ACL to *all* protected domain objects.

## Defense and Mitigation

Organizations implement several strategies to break the lateral and vertical movement paths associated with administrative accounts.

### 1. LAPS (Local Administrator Password Solution)
LAPS mitigates the Pass-the-Hash risk associated with shared local administrator accounts. It automatically randomizes the local administrator password on every single domain-joined machine and stores the password securely in an Active Directory attribute (`ms-Mcs-AdmPwd`).

### 2. Tiered Access Model (Red Forest / ESAE)
Microsoft recommends a tiered administrative model to prevent highly privileged credentials from touching low-trust systems.
*   **Tier 0:** Domain Controllers, PKI, ADFS. (Domain Admins only log in here).
*   **Tier 1:** Enterprise Servers, Application Servers. (Server Admins log in here).
*   **Tier 2:** End-user Workstations. (Helpdesk / Local Admins log in here).
A Tier 0 account is structurally prevented (via GPO `Deny log on`) from ever logging into a Tier 1 or Tier 2 machine, eliminating the risk of LSASS credential dumping by lower-tier attackers.

## Important Commands

**Checking Local Administrators Group (CMD):**
```cmd
net localgroup administrators
```

**Enumerating Domain Admins (PowerView):**
```powershell
Get-DomainGroupMember -Identity "Domain Admins"
```

**Extracting LAPS Passwords (requires rights):**
```powershell
# Using CrackMapExec / NetExec to dump LAPS passwords remotely
netexec smb 10.0.0.0/24 -u 'user' -p 'pass' --laps
```

---

## Real-World Attack Scenario

An attacker successfully phishes a helpdesk employee, gaining access to their workstation. The employee's account is not a Domain Admin but is nested into a "Workstation Admins" group, granting them Local Administrator rights across multiple endpoints. The attacker bypasses UAC and dumps the LSASS process memory on the compromised machine using Mimikatz, recovering the plaintext credentials of a Tier 1 server administrator who recently logged in. Using NetExec (CrackMapExec), the attacker sprays these newly acquired credentials across the network, discovering the Tier 1 admin holds Local Administrator privileges on several high-value internal application servers. The attacker pivots to these servers via SMB Exec, successfully escalating their access beyond the initial workstation without ever needing Domain Admin rights.

## Chaining Opportunities

*   **Lateral Movement (PtH)**: Compromising a Local Admin account allows the use of Mimikatz or Impacket's `wmiexec.py` to Pass-the-Hash to adjacent systems. 
*   **Credential Dumping**: Once Local Admin is achieved, attackers execute LSASS memory dumps (`procdump`, `comsvcs.dll`) to hunt for cached Domain Admin tokens. See [[14 - User Account Control UAC in AD Environments]].

## Related Notes
*   [[11 - Security Identifiers SIDs and Relative IDs RIDs]]
*   [[14 - User Account Control UAC in AD Environments]]
*   [[22 - Pass the Hash and Credential Dumping]]
*   [[27 - Active Directory Access Control List Attacks]]

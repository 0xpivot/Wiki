---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.15 Defending Against Basic AD Attacks"
---

# 15 - Defending Against Basic AD Attacks

## 1. Introduction to Active Directory Defense

Active Directory (AD) is the identity backbone for the vast majority of enterprise networks. Because it holds the "keys to the kingdom," it is constantly targeted by adversaries. Defending AD requires a multi-layered approach that addresses architectural flaws, legacy misconfigurations, and operational hygiene.

Defending against AD attacks is not about installing a single magic product; it relies on enforcing strict access controls, hardening authentication protocols, reducing lateral movement vectors, and enabling pervasive visibility across the domain.

## 2. The Tiering Model (Redesigning the Architecture)

The most robust defense against AD exploitation is the implementation of Microsoft's **Enterprise Access Model** (historically known as the Tiered Administration Model). This model fundamentally restricts where administrative credentials can be exposed.

- **Tier 0 (Identity and Control)**: This is the highest level of privilege. It includes Domain Controllers, Public Key Infrastructure (PKI), Azure AD Connect servers, and the Enterprise Admin/Domain Admin accounts. 
- **Tier 1 (Enterprise Servers)**: Includes application servers, database servers, file servers, and their respective local administrators.
- **Tier 2 (Workstations and Users)**: Includes standard user workstations, laptops, and standard helpdesk personnel.

**The Golden Rule of Tiering:** 
Administrators from a higher tier *must never* log into systems in a lower tier. For example, a Tier 0 Domain Admin should never log into a Tier 2 workstation. If they do, they risk exposing their credentials (hashes/tickets) to an attacker who has compromised that Tier 2 machine.

### ASCII Diagram: The Tiered Architecture Model

```text
    +-------------------------------------------------------+
    |                                                       |
    |  Tier 0: Domain Controllers, PKI, AD CS, ADFS         | <--- Only T0 Admins log in here.
    |                                                       |      No internet access.
    +---------------------------+---------------------------+
                                | (No downward login allowed)
                                X
    +---------------------------v---------------------------+
    |                                                       |
    |  Tier 1: Member Servers, SQL, IIS, File Servers       | <--- T1 Admins manage these.
    |                                                       |      T0 Admins NEVER log in here.
    +---------------------------+---------------------------+
                                | (No downward login allowed)
                                X
    +---------------------------v---------------------------+
    |                                                       |
    |  Tier 2: Workstations, Laptops, Mobile Devices        | <--- Users and T2 Helpdesk.
    |                                                       |      T0/T1 Admins NEVER log in.
    +-------------------------------------------------------+
```

## 3. Securing Credentials and Lateral Movement

### 3.1. Local Administrator Password Solution (LAPS)
To prevent Pass-the-Hash (PtH) and lateral movement, LAPS must be deployed across all Tier 1 and Tier 2 machines. LAPS ensures that the built-in local administrator account has a randomized, complex, and regularly rotating password.
- **Defense Action**: Implement Windows LAPS, enforce strong ACLs on the `ms-Mcs-AdmPwd` attribute, and heavily restrict who can read these passwords.

### 3.2. Principle of Least Privilege (PoLP) and the Protected Users Group
Users should only have the permissions strictly necessary for their roles. Over-privileged accounts are a massive liability.
- **Defense Action**: Place all highly privileged accounts (e.g., Domain Admins) into the built-in **Protected Users** group. This provides critical protections:
  - Disables NTLM authentication (forces Kerberos).
  - Prevents caching of credentials.
  - Prevents delegation of their TGTs (stops Unconstrained Delegation abuse).

### 3.3. LSA Protection and Credential Guard
To protect against credential dumping tools like Mimikatz, the Local Security Authority (LSA) must be hardened.
- **Defense Action**: Enable **RunAsPPL** (LSA Protection) via Group Policy. This prevents non-system, un-signed processes from injecting code or reading the memory of `lsass.exe`.
- **Defense Action**: Enable **Windows Defender Credential Guard**, which uses virtualization-based security (VBS) to isolate secrets entirely from the standard operating system environment.

## 4. Defending Kerberos and Delegation

Misconfigured Kerberos delegation is a primary escalation path in Active Directory.

### 4.1. Remediating Delegation Vulnerabilities
- **Eliminate Unconstrained Delegation**: Query AD for any machine with the `TRUSTED_FOR_DELEGATION` flag. Remove this flag entirely. There is no modern use-case that requires it.
- **Restrict Constrained Delegation (KCD)**: Audit the `msDS-AllowedToDelegateTo` attribute. If delegation is required, ensure it is limited strictly to the required backend service.
- **Migrate to RBCD**: Shift from traditional KCD to Resource-Based Constrained Delegation (RBCD). This puts the security control on the target resource rather than relying on the frontend service.

### 4.2. Securing LDAP and RPC
- **Enforce LDAP Signing and Channel Binding**: Prevent NTLM relay attacks (e.g., PetitPotam to AD CS, or NTLM relay to LDAP for RBCD attacks) by requiring LDAP signing on Domain Controllers.
- **Disable the Print Spooler Service**: On Domain Controllers and other sensitive Tier 0/Tier 1 infrastructure, disable the Print Spooler service to neutralize the MS-RPRN (Printer Bug) coercion technique.

## 5. Event Logging, Auditing, and Visibility

A robust defense is blind without proper telemetry. Windows Event Forwarding (WEF) should be used to aggregate critical logs into a SIEM.

### Critical Event IDs to Monitor:
| Event ID | Description | Attack Context |
| :--- | :--- | :--- |
| **4624** | Successful Logon | Monitor for abnormal logon types (Type 3: Network, Type 9: NewCredentials) |
| **4688** | Process Creation | Enable command-line auditing to catch obfuscated PowerShell or Mimikatz execution |
| **4768** | Kerberos TGT Requested | Monitor for abnormal TGT requests, indicative of Pass-the-Ticket or Golden Tickets |
| **4769** | Kerberos TGS Requested | High volume indicates Kerberoasting; specific flags indicate Delegation abuse |
| **4662** | Object Access (AD) | Monitor access to DCSync rights, LAPS properties, or AdminSDHolder modifications |
| **5136** | Directory Service Changes | Detects malicious ACL changes, adding RBCD rights, or backdoor creation |

## 6. Disrupting Active Directory Enumeration

Attackers rely on tools like BloodHound and PowerView to map the network. While complete obfuscation is impossible, defense-in-depth measures can slow them down.
- **Defense Action**: Restrict standard user access to the `NetCeiver` and `SAMR` RPC interfaces. This prevents standard users from querying local group memberships of remote machines, significantly degrading BloodHound's effectiveness.
- **Defense Action**: Utilize Honeypot Accounts and SPNs. Create a fake Domain Admin account or an account with a highly appealing SPN (for Kerberoasting). Alert immediately if these honeypots are interacted with.

## Real-World Attack Scenario

An Advanced Persistent Threat (APT) group successfully phished a senior network engineer, compromising their Tier-2 laptop (`LT-NET-ENG1`). The attackers used a local privilege escalation exploit to gain SYSTEM access on the laptop and dumped the engineer's cached credentials. 

The attackers extracted the NTLM hash of the engineer's highly privileged Domain Admin account (`admin_jdoe`), which they assumed was cached due to a recent remote desktop session. They immediately attempted a Pass-the-Hash (PtH) attack using CrackMapExec to move laterally to a Tier-1 infrastructure server and establish a foothold deeper in the network.

**The Execution & The Block:**
1. The attackers ran: `cme smb 10.10.5.50 -u admin_jdoe -H <NTLM_HASH> --local-auth`
2. The authentication attempt instantly failed with a `STATUS_LOGON_FAILURE` error.
3. Confused, the attackers attempted to use the hash to request a Kerberos ticket using Rubeus (`asktgt`), but the Domain Controller explicitly rejected the request.
4. The attackers attempted to abuse a known Unconstrained Delegation server they found via BloodHound, trying to coerce the `admin_jdoe` account to authenticate to it, hoping to steal the TGT. This also failed.

**The Outcome:**
The attack was completely neutralized because the organization's defensive team had recently implemented the Enterprise Access Model. They had placed all Tier-0 and Domain Admin accounts, including `admin_jdoe`, into the Active Directory **Protected Users** group. 

Because `admin_jdoe` was in this group:
1. Windows refused to cache the NTLM hash on the compromised laptop in the first place (the hash the attackers dumped was old and expired).
2. The Domain Controller refused to accept NTLM authentication for that account, killing the PtH attempt.
3. The account was restricted from Kerberos delegation, meaning its TGT could not be stolen via the Unconstrained Delegation server.
The defenders' SIEM triggered an alert on the anomalous NTLM logon failure (Event ID 4624/4625), allowing the SOC to isolate the compromised laptop and eject the APT before any lateral movement occurred.

## 7. Chaining Opportunities

Defensive strategies directly break the attack chains discussed in previous notes:
- Implementing LAPS prevents the lateral movement chains required after exploiting [[11 - Bypassing UAC User Account Control]].
- The `Protected Users` group breaks the exploitation chain of [[14 - Kerberos Unconstrained Delegation Basics]].
- Disabling the Print Spooler breaks the coercion chain required for Unconstrained Delegation and NTLM relay attacks.
- Advanced auditing provides the detection logic required to catch the abuse primitives in [[13 - Kerberos Constrained Delegation Basics]].

## 8. Related Notes
- [[11 - Bypassing UAC User Account Control]]
- [[12 - Exploiting LAPS Local Administrator Password Solution Basics]]
- [[13 - Kerberos Constrained Delegation Basics]]
- [[14 - Kerberos Unconstrained Delegation Basics]]
- [[25 - Implementing the Tiered Administration Model]]
- [[30 - Advanced Windows Event Logging and Telemetry]]

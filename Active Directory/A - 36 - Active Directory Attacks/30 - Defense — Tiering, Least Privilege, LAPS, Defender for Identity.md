---
tags: [active-directory, defense, tiering, laps, mdi, mitigation]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.30 Defense"
---

# 36.30 Defense — Tiering, Least Privilege, LAPS, Defender for Identity

## 1. Introduction
Active Directory is the backbone of identity for the vast majority of enterprise networks. Attackers recognize that compromising AD equals compromising the entire organization. Over decades of offensive security research—manifesting in tools like BloodHound, Mimikatz, and Rubeus—the defensive community has formulated robust, architectural strategies to protect Active Directory. 

Implementing a modern AD defense strategy is not about installing a single tool; it is a fundamental shift in architecture. The core pillars involve segmenting administrative privilege (**Tiering**), enforcing localized boundaries (**LAPS**), operating under **Least Privilege**, and deploying behavioral monitoring (**MDI**).

### ASCII Architecture Diagram: The AD Tiering Model

```text
       [ TIER 0 - IDENTITY & CONTROL ]
       (Domain Controllers, PKI, ADFS, Ent Admins)
      +-------------------------------------------+
      |  Access heavily restricted.               |
      |  No internet access.                      |
      |  Only managed via Secure Admin Workstation|
      +-------------------------------------------+
             | (No T0 credentials log in below T0)
             X (Strict Block)
             v
       [ TIER 1 - SERVERS & APPLICATIONS ]
       (File Servers, Database Servers, App Admins)
      +-------------------------------------------+
      |  Standard server administration.          |
      |  Tier 1 Admins manage these servers.      |
      +-------------------------------------------+
             | (No T1 credentials log in below T1)
             X (Strict Block)
             v
       [ TIER 2 - ENDPOINTS & WORKSTATIONS ]
       (User Laptops, Desktops, Helpdesk Admins)
      +-------------------------------------------+
      |  High risk of phishing / compromise.      |
      |  Tier 2 Admins manage endpoints.          |
      +-------------------------------------------+
```

## 2. The Tiering Model (ESAE / Enterprise Access Model)
Historically, Domain Admins would log into user workstations to troubleshoot issues. This left highly privileged credentials (NTLM hashes, Kerberos tickets) cached in the memory (`lsass.exe`) of Tier 2 endpoints. If a user downloaded malware, the attacker could dump the Domain Admin credentials and instantly take over the network.

**The Solution:** The Tiering Model logically isolates administrative credentials.
- **Tier 0**: Domain Controllers, Azure AD Connect, PKI, highly privileged accounts.
- **Tier 1**: Enterprise servers, line-of-business applications.
- **Tier 2**: Standard user workstations and devices.

### 2.1 Enforcement Rules
1. **Credentials do not traverse down**: A Tier 0 admin account must *never* log into a Tier 1 or Tier 2 machine. If a Domain Admin needs to manage a Tier 2 workstation, they must use a separate, dedicated Tier 2 admin account.
2. **Access does not flow up**: A Tier 2 admin cannot manage Tier 1 servers.
3. **Group Policy Enforced**: These rules are hardcoded via GPO (User Rights Assignment: "Deny log on locally", "Deny log on through Remote Desktop Services").
4. **Secure Admin Workstations (SAWs)**: Tier 0 management should only be performed from dedicated, locked-down jump boxes that do not have internet access or email clients.

## 3. LAPS (Local Administrator Password Solution)
One of the most common vectors for Lateral Movement is shared local administrator passwords. If the local `Administrator` account on `Workstation-A` has the same password as `Workstation-B`, an attacker who compromises `A` can Pass-the-Hash to compromise `B`, mapping the entire network.

### 3.1 How LAPS Works
Microsoft LAPS eliminates this attack vector entirely.
1. LAPS generates a unique, randomly generated, complex password for the local Administrator account on every single domain-joined machine.
2. The password is automatically rotated every 30 days (configurable).
3. The password is stored securely as a confidential attribute on the computer object in Active Directory.
4. Only authorized IT personnel (e.g., Helpdesk group) are granted the AD ACL permissions to read this password attribute.

When LAPS is deployed, lateral movement via local admin credentials becomes mathematically impossible. LAPS has recently been integrated natively into Windows (Windows LAPS) and Azure AD.

## 4. Principle of Least Privilege (PoLP)
AD environments often accumulate technical debt, leading to over-privileged accounts. Defending AD requires ruthlessly stripping away unnecessary rights.

### 4.1 Delegation and ACLs
Instead of adding users to `Domain Admins`, use native AD delegation. If a team needs to reset passwords for users in the "Sales" OU, use the Delegation of Control Wizard to grant them *only* `Reset Password` rights over that specific OU.
Avoid adding groups to `Builtin\Administrators` on Domain Controllers. Limit membership of `Account Operators` and `Server Operators`.

### 4.2 Removing Unnecessary Memberships
- Heavily audit the `Domain Admins`, `Enterprise Admins`, `Administrators`, and `Account Operators` groups.
- Remove standard service accounts from privileged groups. A service account should rarely be a Domain Admin. If it requires elevated privileges, investigate the exact permissions it needs and assign them via granular ACLs.

## 5. Modern Hardening Configurations

### 5.1 Disabling Legacy Protocols
- **Disable LLMNR and NBT-NS**: Prevents NTLM relay and poisoning attacks (Responder). Enforce this via Group Policy by disabling multicast name resolution.
- **Disable SMBv1**: Prevents legacy exploits like MS17-010 (EternalBlue) and limits the attack surface.
- **Enforce SMB Signing**: Stops NTLM relay attacks against internal servers and Domain Controllers. Requires digital signatures for SMB traffic.
- **Disable Print Spooler on DCs**: Protects against PrintNightmare and PrinterBug, forcing DCs to act solely as identity providers.

### 5.2 Kerberos Security
- **RC4 Deprecation**: Force AD to use AES-128/AES-256 for Kerberos tickets, mitigating AS-REP Roasting and making Kerberoasting offline cracking significantly harder. Ensure legacy systems are upgraded.
- **Enable Protected Users Security Group**: Add highly privileged accounts (Tier 0) to the `Protected Users` group. This prevents their credentials from being cached in memory, forces AES encryption, disables NTLM authentication entirely for those users, and sets ticket lifetimes to a maximum of 4 hours.

## 6. Microsoft Defender for Identity (MDI)
Previously known as Azure Advanced Threat Protection (ATP) / ATA. MDI is a cloud-based security solution that leverages sensors installed directly on Domain Controllers. It serves as the ultimate safety net for Active Directory.

### 6.1 Behavioral Analytics
MDI profiles user behavior. If a user who normally only logs into their workstation suddenly requests Kerberos tickets for 50 different servers in 10 seconds, MDI triggers an alert. It identifies deviations from established baselines.

### 6.2 Deterministic Detections
MDI excels at catching the specific techniques outlined in the Active Directory attack playbook:
- **DCSync**: Detects unauthorized directory replication requests, immediately flagging malicious replication.
- **Golden / Silver Tickets**: Detects anomalies in PAC signatures and Kerberos ticket encryption, identifying forged tickets.
- **Overpass-the-Hash**: Detects unusual encryption downgrades during authentication.
- **Kerberoasting**: Detects massive bursts of TGS requests for service accounts.
- **ZeroLogon**: Detects Netlogon cryptographic anomalies and failed brute-force attempts.

## 7. Continuous Auditing and Red Teaming
Defense is not a "set it and forget it" endeavor. Organizations must regularly audit their AD environment using tools like BloodHound (to identify dangerous ACLs and unexpected attack paths) and PingCastle (to score the overall AD health and identify misconfigurations). Regular penetration testing and Red Teaming are crucial to validate that the Tiering model holds under pressure.

## 8. Conclusion
Securing Active Directory is a continuous lifecycle. While tools like LAPS and MDI provide immense technical roadblocks for attackers, the true foundation of defense relies on strict architectural discipline—enforcing the Tiering model, adhering to Least Privilege, and rapidly patching vulnerabilities. When these principles are combined, the traditional "breach one box, take the domain" attack path is completely severed, forcing attackers to operate much louder and take significantly more risk.

## Real-World Attack Scenario

During a purple team exercise aimed at evaluating a mature enterprise's defenses, the red team achieved initial access on a Tier 2 marketing workstation. In a typical legacy environment, the attacker would dump local credentials and laterally move. However, this organization had strictly implemented the Microsoft Enterprise Access Model (Tiering) and Windows LAPS.

Upon executing Mimikatz, the attacker successfully dumped the local Administrator NTLM hash. However, because Windows LAPS was actively managing local credentials, that password was a complex, randomly generated string unique strictly to that single marketing workstation. Attempting a Pass-the-Hash (PtH) attack against adjacent Tier 2 workstations failed immediately. 

Next, the attacker attempted to elevate privileges by searching the AD environment for misconfigured ACLs or service accounts. They identified an IT support account and performed a Kerberoast attack. Unbeknownst to the attacker, the organization had deployed Microsoft Defender for Identity (MDI) sensors on all Domain Controllers. MDI instantly detected the anomalous burst of TGS-REQs originating from the marketing workstation and triggered a high-fidelity "Suspected Kerberoasting" alert in the SOC.

Simultaneously, the attacker attempted an NTLM Relay attack via Responder by poisoning LLMNR traffic. This also failed, as Group Policy had disabled LLMNR and enforced SMB Signing across all Tier 1 and Tier 0 assets. Finally, hoping to find cached privileged credentials, the attacker searched the workstation's memory. However, strict Tiering policies prevented any Tier 0 (Domain Admin) or Tier 1 (Server Admin) accounts from ever logging into Tier 2 endpoints. Blocked from lateral movement, unable to escalate privileges, and flagged by MDI behavioral analytics, the red team's attack path was completely severed within two hours, validating the effectiveness of defense-in-depth architectural hardening.

## 9. Chaining Opportunities
- **[[20 - BloodHound & Active Directory Enumeration]]**: Use BloodHound defensively to audit AD ACLs and verify that the Tiering model is actually intact.
- **[[18 - NTLM Relay Attacks]]**: Mitigated entirely by enforcing SMB Signing and disabling legacy multicast protocols.
- **[[24 - Golden Ticket Attacks]]**: Prevented by securing Tier 0 and monitoring with Defender for Identity.

## 10. Related Notes
- [[13 - Windows Privilege Escalation]]
- [[21 - Lateral Movement Techniques]]
- [[19 - Kerberos Fundamentals]]

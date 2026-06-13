---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 74"
---

# Active Directory Security Interview QnA: Resource-Based Constrained Delegation (RBCD)

## ASCII Diagram: RBCD Attack Flow

```text
+-----------------------------------------------------------------------------+
|                                                                             |
| +-------------------+ (1) Compromise Account with WriteAccess +-----------+ |
| |                   |       to Target Computer Object         |           | |
| | Attacker Machine  | --------------------------------------> | Domain    | |
| |                   | (2) Modify msDS-AllowedToActOnBehalf... | Controller| |
| +-------------------+                                         +-----------+ |
|          |                                                          ^       |
|          |                                                          |       |
|          | (3) S4U2Self: Request TGS for FakeUser to AttackerSystem |       |
|          | (4) S4U2Proxy: Request TGS for FakeUser to TargetSystem  |       |
|          v                                                          |       |
| +-------------------+                                               |       |
| | Attacker-Owned    | ----------------------------------------------+       |
| | Computer Account  |     (Kerberos TGS Requests)                           |
| +-------------------+                                                       |
|                                                                             |
|                                  (5) TGS for Target System Granted!         |
|                                 ------------------------------------> +---+ |
|                                                                       |   | |
|                                                                       |   | |
|                                                                       +---+ |
+-----------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Define Resource-Based Constrained Delegation (RBCD). How does its configuration architecture differ fundamentally from traditional Constrained Delegation and Unconstrained Delegation?**

**Answer:**
Resource-Based Constrained Delegation (RBCD) is an Active Directory feature introduced in Windows Server 2012. It allows a service (the resource) to explicitly specify which other accounts (delegates) are permitted to impersonate users and authenticate to it.

The fundamental architectural shift is where the delegation authority is defined:
1. **Unconstrained & Traditional Constrained Delegation:** The delegation configuration is placed on the *delegating account* (the front-end service). To configure this, an administrator must possess the `SeEnableDelegationPrivilege` (typically restricted to Domain Admins), as it is a highly sensitive domain-wide right.
2. **Resource-Based Constrained Delegation (RBCD):** The delegation configuration is placed on the *target resource* itself (the back-end service). The configuration is stored within the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target computer or service account.

This is a critical security distinction. Because the configuration is stored on the resource, anyone who holds generic `Write` access or specifically `WriteProperty` over the target computer account object in Active Directory can configure RBCD. They do *not* need the domain-wide `SeEnableDelegationPrivilege`.

**Q2: Describe the Kerberos extensions (S4U) utilized during the execution of an RBCD attack. What role do S4U2Self and S4U2Proxy play in the impersonation process?**

**Answer:**
RBCD heavily relies on two Service-for-User (S4U) Kerberos extensions to facilitate impersonation without requiring the user's password.
To execute an RBCD attack, the attacker must control a computer account (or an account with an SPN) that will act as the "delegate."

1. **S4U2Self (Service for User to Self):** The attacker utilizes their controlled computer account to request a Service Ticket (TGS) to *itself*, on behalf of an arbitrary user (e.g., a Domain Admin). Because the attacker controls the service account, the KDC issues this ticket. The resulting TGS contains the requested user's privileges in the PAC, and importantly, is flagged as "Forwardable."
2. **S4U2Proxy (Service for User to Proxy):** The attacker then takes the Forwardable TGS obtained via S4U2Self and presents it back to the KDC. They request a new TGS, this time targeting the compromised *resource* system.

The KDC checks the target system's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. If it finds the SID of the attacker's controlled computer account listed there (which the attacker configured in step 1), the KDC authorizes the delegation. It issues a new TGS for the target system, maintaining the impersonated identity (the Domain Admin).
The attacker now has a valid TGS to access the target system as a Domain Admin.

**Q3: Explain the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. What data type is it, and what specifically does an attacker write into this attribute to enable the attack?**

**Answer:**
The `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute is a security descriptor. Specifically, its data type is an `NT Security Descriptor` stored as an array of bytes.

When an attacker gains write privileges over a target computer object, they cannot simply write a plaintext username into this attribute. They must craft a valid Security Descriptor.
The attacker writes a Discretionary Access Control List (DACL) into this attribute. This DACL contains an Access Control Entry (ACE) granting the `PrincipalSelf` or explicit `Allow` right to the Security Identifier (SID) of the computer account they control.

Essentially, the security descriptor translates to: "The identity represented by SID X (the attacker's computer) is allowed to act on behalf of other identities when accessing me." Tools like PowerView or Impacket automate the complex process of converting a target SID into the correct byte array format required by the security descriptor.

## Scenario-Based Questions

**Q4: You are on an internal penetration test. You run BloodHound and discover that a standard user account you have compromised, `jdoe`, has `GenericWrite` permissions over a critical web server's computer object (`WEB-PROD-01$`). `jdoe` is not an administrator on the web server or the domain. Detail the exact, step-by-step methodology you would use to leverage this misconfiguration to gain SYSTEM access to `WEB-PROD-01$`.**

**Answer:**
This is a classic RBCD attack path. I will abuse the `GenericWrite` permission to configure delegation and impersonate a highly privileged user.

1. **Create a Controlled Computer Account:** By default, standard users (like `jdoe`) can add up to 10 computer accounts to the domain (controlled by the `MachineAccountQuota` attribute). Using `jdoe`'s credentials, I will use a tool like Impacket's `addcomputer.py` to create a new computer account, e.g., `EVIL-PC$`, and note its password.
2. **Modify the Target's RBCD Attribute:** Using `jdoe`'s `GenericWrite` permission, I will modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of `WEB-PROD-01$`. I will use a script (like `rbcd.py` from Impacket or PowerView's `Set-DomainObject`) to write a security descriptor containing the SID of `EVIL-PC$` into this attribute.
3. **Execute S4U2Self:** I will use Impacket's `getST.py` (Get Service Ticket). I will authenticate as `EVIL-PC$` using its password. I will request a ticket for `EVIL-PC$` (S4U2Self), but I will specify that I am impersonating the domain `Administrator` user.
4. **Execute S4U2Proxy:** In the same `getST.py` command, I will supply the SPN of the target (`cifs/WEB-PROD-01.domain.com`). The script automatically takes the forwardable ticket from step 3 and performs the S4U2Proxy request. The DC checks `WEB-PROD-01$`'s attribute, sees `EVIL-PC$` is allowed, and grants a TGS for the CIFS service as the `Administrator`.
5. **Gain Access:** I will export the resulting `.ccache` file and use `psexec.py -k -no-pass WEB-PROD-01.domain.com` to gain a SYSTEM shell on the web server.

**Q5: During a security architecture review, a system administrator argues that because they have set `MachineAccountQuota` to 0, their domain is completely immune to Resource-Based Constrained Delegation attacks. Do you agree or disagree? Provide a detailed technical justification.**

**Answer:**
I strongly disagree. Setting `MachineAccountQuota` (MAQ) to 0 is a vital hardening step, but it does *not* make the domain immune to RBCD attacks; it only removes one specific, albeit common, prerequisite.

MAQ=0 prevents standard, unprivileged users from arbitrarily creating *new* computer accounts to act as the delegate.
However, an attacker can still execute an RBCD attack if they can compromise an *existing* account that meets the criteria for being a delegate. To be a delegate in an S4U flow, the account simply needs to have a registered Service Principal Name (SPN).

If an attacker compromises the credentials (or hash) of:
1. Any existing computer account in the domain (e.g., a low-value kiosk machine, a developer's workstation).
2. Any user account configured with an SPN (a service account).

They can use that compromised account to perform the S4U2Self and S4U2Proxy requests. Therefore, if the attacker finds `GenericWrite` over a critical server and compromises a low-level service account, the RBCD attack will succeed perfectly, completely bypassing the MAQ=0 mitigation.

## Deep-Dive Defensive Questions

**Q6: Architecturally, how would you construct a comprehensive SIEM detection strategy for RBCD abuse, focusing on both the configuration modification phase and the active Kerberos exploitation phase?**

**Answer:**
A robust detection strategy must monitor both LDAP modifications and Kerberos anomalies.

**Phase 1: Configuration Modification (LDAP)**
1. **Event ID 5136 (A directory service object was modified):** You must audit directory service changes. Filter specifically for modifications where the `LDAP Display Name` of the attribute being changed is `msDS-AllowedToActOnBehalfOfOtherIdentity`.
2. **Contextual Analysis:** When this event fires, analyze the `SubjectUserName` (who made the change). If the user is a standard employee, a service account, or anyone outside the core Tier 0 identity management team, it is a massive red flag indicating potential abuse of delegated AD permissions (like BloodHound-identified `GenericWrite` paths).

**Phase 2: Active Exploitation (Kerberos)**
1. **Event ID 4769 (A Kerberos service ticket was requested):** This is where the S4U extensions are visible.
2. **S4U2Self Detection:** Look for a 4769 event where the `TargetUserName` (the service being requested) matches the `SubjectUserName` (the account requesting it) - this indicates a service requesting a ticket to itself. The critical anomaly is the `Transited Services` field, which will contain the name of the user being impersonated (e.g., the Domain Admin).
3. **S4U2Proxy Detection:** Look for a subsequent 4769 event where the `SubjectUserName` is the attacker-controlled computer account, the `TargetUserName` is the victim server, and the `Transited Services` field is populated.
4. **EDR Correlation:** Correlate these Kerberos anomalies with process execution logs (Event 4688) on the target server, looking for lateral movement artifacts like `psexecsvc.exe` or suspicious WMI activity immediately following the anomalous Kerberos tickets.

**Q7: Beyond monitoring, what proactive Active Directory hardening configurations must be implemented to neutralize the risk of RBCD attacks and protect highly sensitive accounts from being impersonated?**

**Answer:**
Proactive defense requires breaking the attack chain at multiple levels.

1. **Set `MachineAccountQuota` to 0:** This is the baseline. Stop unprivileged users from spawning delegate objects.
2. **Clean Up Active Directory ACLs:** This is the most crucial step. Use tools like BloodHound defensively. Identify and remediate all non-standard identities (users, groups) that hold `GenericAll`, `GenericWrite`, `WriteDACL`, `WriteOwner`, or `WriteProperty` over computer objects. Only designated provisioning accounts should hold these rights.
3. **Account is Sensitive and Cannot be Delegated:** For highly privileged accounts (Domain Admins, Enterprise Admins, core service accounts), explicitly check the box "Account is sensitive and cannot be delegated" in their AD object properties. When this is set, the KDC will refuse to issue a forwardable ticket for this user during the S4U2Self process, entirely neutralizing the attacker's ability to impersonate them via RBCD (or any delegation).
4. **Protected Users Group:** Add all privileged administrative accounts to the `Protected Users` security group. Members of this group cannot be delegated, providing the same protection as the checkbox but managed centrally via group membership.
5. **Tiered Administration:** Ensure that Tier 0 accounts (DA) cannot log into Tier 1 or Tier 2 systems. Even if an attacker uses RBCD to compromise a Tier 1 server and attempts to impersonate a DA, they cannot use that DA token to access other resources if Tiering restrictions are enforced at the authentication policy level.

## Real-World Attack Scenario

During an assumed-breach assessment against a large manufacturing company, the Red Team compromised a developer's workstation. Through LDAP enumeration, they discovered a nested group misconfiguration: the "Junior IT Support" group had been accidentally granted `GenericWrite` access over an Organizational Unit containing all production SQL servers. The developer's account was a member of a group nested within Junior IT Support.

The Red Team realized they had control over the SQL servers but lacked local admin credentials. They checked the `MachineAccountQuota` and found it was left at the default value of 10.
They executed an RBCD attack: they created a new rogue computer account named `DEV-TEST-PC$`. Using the nested `GenericWrite` permission, they modified the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the primary billing SQL server (`SQL-BILL-PRD$`) to trust `DEV-TEST-PC$`.

Using Impacket, they performed the S4U Kerberos exchange, requesting a ticket to the SQL server while impersonating the domain's Chief Information Officer (who was known to have DA rights). They successfully obtained the TGS, accessed the SQL server via SMB, dumped the database containing customer financial data, and moved laterally to the domain controllers—all without triggering a single "failed logon" or "brute force" alert.

## Chaining Opportunities
- **BloodHound ACL Abuse -> RBCD:** Utilizing BloodHound to map complex, non-obvious AD permission paths (e.g., nested groups, custom ACLs) that yield `GenericWrite` over a target system, enabling the RBCD setup.
- **RBCD -> Local Administrator Credential Dumping:** Using RBCD to gain SYSTEM access on a target server, then utilizing Mimikatz or a specialized tool to dump LSA secrets or SAM hashes to acquire local administrator credentials for further lateral movement.
- **NTLM Relay -> RBCD:** Relaying an NTLM authentication (e.g., via PetitPotam or LLMNR/NBT-NS spoofing) from a victim machine to the Domain Controller via LDAP to automatically write the malicious RBCD configuration onto a target computer object, bypassing the need for explicit AD permissions.

## Related Notes
- [[75 - Unconstrained Delegation Attacks]]
- [[52 - Active Directory ACL Abuse]]
- [[60 - Kerberos Authentication Deep Dive]]
- [[80 - NTLM Relaying Attacks]]

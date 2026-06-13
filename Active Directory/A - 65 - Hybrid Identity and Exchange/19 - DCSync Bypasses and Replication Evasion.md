---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.19 DCSync Bypasses"
---

# 19 - DCSync Bypasses and Replication Evasion

## Visual Architecture

```text
+-------------------------------------------------------------+
| DCSYNC BYPASSES AND REPLICATION EVASION                     |
+-------------------------------------------------------------+
| [Attacker]                                                  |
|   | 1. Compromise Sync Account (MSOL_...)                   |
|   | 2. DCSync over alternative RPC ports/named pipes        |
|   | 3. Partial replication (Only specific user hashes)      |
|   v                                                         |
| [Domain Controller] <------- Replication Protocol (DRSR)    |
|   |                                                         |
| [Security Monitoring] -> Detects anomalies? (Bypassed)      |
+-------------------------------------------------------------+
```

## DCSync Fundamentals

The DCSync attack leverages the Directory Replication Service (DRS) Remote Protocol (MS-DRSR). It simulates the behavior of a legitimate Domain Controller requesting replication data from another DC. This allows an attacker to extract password hashes (NTLM, Kerberos keys) directly from the directory without needing to execute code on the target DC.

The prerequisite permissions for DCSync are:
- `Replicating Directory Changes` (DS-Replication-Get-Changes)
- `Replicating Directory Changes All` (DS-Replication-Get-Changes-All)

### Evasion and Bypasses

Standard DCSync attacks (e.g., using Mimikatz or Impacket's secretsdump) are heavily monitored and easily detected by tools like MDI or network IDS.

**1. Machine Account Impersonation:**
Network monitoring often expects replication traffic to originate from known Domain Controller IP addresses and machine accounts. By compromising an existing, defunct DC machine account, or temporarily changing the `userAccountControl` of a compromised machine to appear as a DC, we can blend in with legitimate replication traffic.

**2. Specific Object DCSync (Targeted Replication):**
Instead of dumping the entire domain (which generates massive network traffic and easily identifiable anomalies), an attacker can request the replication data for a single, specific object.
```bash
secretsdump.py domain/user:password@DC_IP -just-dc-user krbtgt
```

**3. Exploiting Azure AD Connect (MSOL) Accounts:**
The account used by Entra Connect to synchronize identities to the cloud inherently possesses the required DCSync rights. This account is often excluded from certain monitoring alerts because its constant replication activity is deemed "normal."

**4. RPC over SMB Evasion:**
DCSync typically occurs over dynamically assigned high RPC ports. However, RPC can also be tunneled over SMB named pipes (e.g., `\pipe\lsass`).

**5. VSS and NTDS.dit Extraction as an Alternative:**
If network-based DCSync is strictly monitored, obtaining local administrative access to the DC and extracting the `NTDS.dit` file and the `SYSTEM` hive via Volume Shadow Copies (VSS) provides the same data without generating MS-DRSR network traffic.


## Real-World Attack Scenario
## Real-World Attack Scenario: DCSync Bypasses & Evasion

**1. Context and Environment:**
The attacker has gained control of a user account with `Replicating Directory Changes` privileges (a service account used for a legacy IAM synchronization tool) within a highly monitored financial institution. The Security Operations Center (SOC) heavily monitors for traditional DCSync attacks (Event ID 4662 and network IDS signatures for DRSUAPI). The objective is to dump the NTDS.dit hashes without triggering the SOC's DCSync alerts.

**2. Attacker Thought Process:**
"I have the privileges to perform a DCSync, but if I use standard Mimikatz `lsadump::dcsync`, the network IDS will catch the DRSUAPI traffic, and the DC will log the replication request from a non-DC IP address. I need to evade these detections. Instead of a full sync, I can perform a targeted synchronization of just one specific account. Alternatively, I can abuse the `DirSync` control via LDAP, which is older and often less monitored than the DRS protocol used by Mimikatz."

**3. Reconnaissance and Enumeration:**
The attacker verifies their privileges using AD module cmdlets, confirming the compromised service account (`svc_iam_sync`) possesses the necessary extended rights at the domain root.
```powershell
# Checking for replication rights
Get-Acl "AD:\DC=corp,DC=local" | Select-Object -ExpandProperty Access | Where-Object { $_.ObjectType -match "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2" }
```
Knowing the SOC monitors replication traffic targeting the primary Domain Controller (`DC01`), the attacker enumerates the domain to find a secondary or geographically distant Domain Controller (`DC02-ASIA`) that might have less stringent network monitoring applied.

**4. Exploitation and Execution:**
To evade detection, the attacker avoids Mimikatz and opts for a custom Python script utilizing the Impacket library, specifically targeting the `DirSync` LDAP control rather than DRSUAPI. This shifts the attack from the heavily scrutinized RPC endpoints to standard LDAP (TCP 389/636). They target only a specific, highly privileged service account rather than the `krbtgt` account, further reducing noise.
```bash
# Using a specialized script to exploit DirSync over LDAP
python3 dirsync_dump.py -u 'svc_iam_sync' -p 'ComplexPass123!' -d corp.local -dc-ip 10.100.5.10 --target-user 'Administrator'
```
Furthermore, the attacker configures the script to chunk the requests over a period of hours, blending the traffic with legitimate LDAP queries from other applications.

**5. Post-Exploitation and Outcome:**
The `DirSync` attack successfully extracts the password hash of the Domain Administrator. Because the attack utilized LDAP rather than DRSUAPI, network-based DCSync detections failed to trigger. Additionally, because the attacker targeted a secondary DC and stretched the attack over time, behavioral analytics missed the anomaly. The attacker proceeds to Pass-the-Hash with the Administrator account, establishing deep persistence while the SOC remains entirely unaware of the credential theft.

## Chaining Opportunities
- [[01 - Active Directory Enumeration]]
- [[16 - Bypassing Microsoft Defender for Identity MDI]]
- [[18 - Overcoming Tiered Administration Models]]

## Related Notes
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

---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.16 Bypassing MDI"
---

# 16 - Bypassing Microsoft Defender for Identity (MDI)

## Visual Architecture

```text
+-------------------------------------------------------------+
| MDI SENSOR BYPASS ARCHITECTURE                              |
+-------------------------------------------------------------+
| [Attacker]                                                  |
|   | 1. Encrypted RPC (Avoids Npcap)                         |
|   | 2. Low-volume LDAP queries (Avoids thresholds)          |
|   v                                                         |
| [Domain Controller] (MDI Sensor installed)                  |
|   | -> Npcap (Blind to encrypted payload)                   |
|   | -> Event Logs (Attacker avoids monitored Event IDs)     |
|   +--> [MDI Cloud Service] (No anomalies detected)          |
+-------------------------------------------------------------+
```

## Bypassing Mechanisms

MDI operates by monitoring network traffic, Windows events, and ETW. Bypassing it requires neutralizing these collection points.

**1. Network Inspection (Npcap):**
MDI uses Npcap to capture and parse AD-related traffic (Kerberos, DNS, RPC, SMB, LDAP). To bypass this:
- **Encrypted RPC:** Force RPC traffic over encrypted channels (e.g., using SMB3 encryption or RPC over HTTPS). If the payload is encrypted, the MDI sensor cannot inspect the contents to identify malicious intent.
- **LDAPS (LDAP over SSL):** Instead of standard LDAP (port 389), use LDAPS (port 636).

**2. Event Log Evasion:**
MDI relies on specific Windows Event Logs being forwarded from the DC.
- If an attacker compromises a DC, they can selectively patch or disable the EventLog service, or filter specific Event IDs (e.g., 4624, 4768, 4769) before they are consumed by the MDI sensor agent.

**3. Directory Services Directory Replication (DCSync):**
MDI detects DCSync by monitoring the network for the replication RPC calls (GetNCChanges) from non-Domain Controller IPs.
- **Bypass:** Execute DCSync from an IP address already recognized as a Domain Controller.


## Real-World Attack Scenario
## Real-World Attack Scenario: Bypassing MDI

**1. Context and Environment:**
The attacker has gained local administrator access on an internal application server within a defense contractor's network. The organization heavily utilizes Microsoft Defender for Identity (MDI) to monitor Domain Controllers for suspicious protocols, credential dumping, and lateral movement. The attacker's goal is to obtain Domain Admin credentials without triggering MDI's behavioral alerts.

**2. Attacker Thought Process:**
"MDI sensors are installed directly on the Domain Controllers. If I run standard attacks like DCSync (Directory Replication Service Remote Protocol), Overpass-the-Hash, or aggressive LDAP enumeration (SharpHound), MDI will instantly flag the abnormal behavior and burn my access. To bypass MDI, I need to 'blend in' with legitimate traffic. I shouldn't attack the DC directly from an unexpected IP. Instead, I need to hijack an existing, trusted session or utilize native Windows APIs that don't look like attack tools to the sensors."

**3. Reconnaissance and Enumeration:**
Instead of running loud network scanners, the attacker relies on passive enumeration. They use native WMI queries and monitor local network traffic to identify where IT administrators frequently log in.
```powershell
# Passive enumeration of logged-on users
Get-WmiObject -Class Win32_ComputerSystem | Select-Object UserName
# Checking active network connections to identify RDP sessions
netstat -ano | findstr ":3389"
```
They discover that a Domain Admin routinely connects to a jump server (`JUMP-SRV-01`) on the same subnet to perform maintenance.

**4. Exploitation and Execution:**
The attacker pivots to `JUMP-SRV-01` and waits for the Domain Admin to authenticate. Instead of dumping LSASS (which might trigger local EDR and subsequent MDI alerts), they opt for a stealthy token impersonation and Kerberos ticket extraction (Pass-the-Ticket) using native built-in Windows features or highly customized, memory-only tooling that avoids API hooks.
To bypass MDI's detection of unusual remote execution, the attacker avoids PsExec or standard WMI. They leverage DCOM (Distributed Component Object Model) via an Excel application object to execute commands laterally, as MDI often struggles to differentiate this from legitimate office macro traffic.
```powershell
# Instantiating a remote DCOM object to execute a payload stealthily
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("Excel.Application", "DC01.corp.local"))
$dcom.ExecuteExcel4Macro('EXEC("cmd.exe /c powershell -enc [Base64_Payload]")')
```

**5. Post-Exploitation and Outcome:**
The DCOM execution succeeds, executing a memory-resident payload on the DC without triggering standard remote execution alerts. Once on the DC, the attacker modifies the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on a target system using native LDAP modification scripts rather than known exploit frameworks. This Resource-Based Constrained Delegation (RBCD) attack grants them permanent, stealthy persistence. MDI fails to raise an alert because the attacker avoided known malicious signatures, minimized anomalous Kerberos requests, and operated entirely through hijacked, trusted communication channels.

## Chaining Opportunities
- [[01 - Active Directory Enumeration]]
- [[17 - Custom BloodHound Cypher Queries for Tier 0 Paths]]
- [[19 - DCSync Bypasses and Replication Evasion]]

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

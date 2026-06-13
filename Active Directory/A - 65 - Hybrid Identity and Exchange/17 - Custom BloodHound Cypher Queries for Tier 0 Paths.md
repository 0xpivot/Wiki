---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.17 Custom BloodHound Cypher Queries"
---

# 17 - Custom BloodHound Cypher Queries for Tier 0 Paths

## Visual Architecture

```text
+-------------------------------------------------------------+
| CUSTOM BLOODHOUND CYPHER QUERIES FOR TIER 0                 |
+-------------------------------------------------------------+
| (User A) --[MemberOf]--> (Group B)                          |
|                             |                               |
|                        [GenericAll]                         |
|                             v                               |
|                       (Group: Tier 0)                       |
|                             |                               |
|                        [AdminTo]                            |
|                             v                               |
|                    (Domain Controller)                      |
+-------------------------------------------------------------+
```

## Cypher Query Fundamentals

BloodHound utilizes Neo4j, a graph database that uses the Cypher query language. To uncover hidden paths to Tier 0 assets, standard queries are often insufficient. We must craft custom queries to identify complex, multi-hop relationships.

**1. Identifying Tier 0 Assets:**
First, we must define Tier 0. By default, BloodHound marks high-privilege groups, but we need to ensure all custom Tier 0 assets are tagged.
```cypher
MATCH (n:Group) WHERE n.name STARTS WITH "TIER0" SET n.highvalue = true RETURN n
```

**2. Advanced Pathfinding to Tier 0:**
Finding paths that avoid standard noisy relationships (like Domain Admins) and focus on delegation and ACL abuse.
```cypher
MATCH p=shortestPath((u:User)-[r:MemberOf|HasSession|AdminTo|AllExtendedRights|ForceChangePassword|GenericAll|GenericWrite|Owns|WriteDacl|WriteOwner|CanRDP|ExecuteDCOM|AllowedToDelegate|ReadLAPSPassword*1..5]->(c:Computer {highvalue:true}))
WHERE u.objectid <> c.objectid
RETURN p
```

**3. Detecting Entra ID / Azure AD Integration:**
With AzureHound, we can query hybrid paths.
```cypher
MATCH p=shortestPath((u:AZUser)-[r:AZAddMembers|AZContains|AZContributor|AZGlobalAdmin*1..5]->(t:AZTenant))
RETURN p
```

**4. Uncovering GPO Delegation:**
Attackers often hide backdoors in GPO permissions.
```cypher
MATCH p=(u:User)-[r:GenericAll|WriteDacl]->(g:GPO)-[r2:GPLink]->(ou:OU)-[r3:Contains]->(c:Computer {highvalue:true})
RETURN p
```


## Real-World Attack Scenario
## Real-World Attack Scenario: Custom BloodHound Cypher Queries

**1. Context and Environment:**
The attacker is performing an assumed-breach assessment against a sprawling, multi-forest Active Directory environment of a telecommunications giant. They have run SharpHound and collected millions of nodes and edges. The built-in BloodHound queries are yielding overwhelming, convoluted paths that are difficult to execute or rely on easily detected techniques (like RDP to 5 different servers). The objective is to find a stealthy, precise path to Tier 0 assets.

**2. Attacker Thought Process:**
"The default 'Shortest Path to Domain Admin' query is noisy and gives me paths involving helpdesk users and easily detected lateral movement. I need to write custom Cypher queries to filter out the noise. I want to find paths that exclusively rely on specific, stealthy abuse primitives—like `GenericWrite` or `ForceChangePassword`—and avoid paths that require me to compromise high-visibility jump servers or trigger multi-factor authentication (MFA) prompts."

**3. Reconnaissance and Enumeration:**
The attacker opens the Neo4j web interface to interact directly with the BloodHound database using Cypher. They begin by identifying all paths to the Domain Admins group that strictly utilize ACL abuse, explicitly filtering out `HasSession` or `AdminTo` edges, which imply active compromise of hosts.
```cypher
// Searching for paths relying only on ACL abuse
MATCH p=shortestPath((u:User)-[r:GenericAll|GenericWrite|ForceChangePassword|AddMember|AllExtendedRights*1..5]->(g:Group {name:'DOMAIN ADMINS@CORP.LOCAL'}))
WHERE NOT u.name CONTAINS 'GUEST'
RETURN p
```
This initial query returns too many results. They refine it to find the shortest path originating from *any* compromised computer account they currently control, rather than starting from a user.

**4. Exploitation and Execution:**
The attacker refines the custom Cypher query to look for paths involving Resource-Based Constrained Delegation (RBCD) or specific GPO modifications, as these are highly effective and often overlooked by defenders.
```cypher
// Finding paths where a controlled computer can compromise a Tier 0 GPO
MATCH (c:Computer {name: 'WEB-DEV-01.CORP.LOCAL'})
MATCH (gpo:GPO)
MATCH (t0:Group {name: 'ENTERPRISE ADMINS@CORP.LOCAL'})
MATCH p=shortestPath((c)-[*1..3]->(gpo)-[:GPLink]->(:OU)-[:Contains*1..2]->(t0))
RETURN p
```
The query immediately yields a highly specific, three-step path: The compromised web server `WEB-DEV-01` has `GenericWrite` access to a seemingly innocuous GPO named `Legacy-Printers`, which, due to a legacy configuration error, is linked to the Tier 0 OU containing the Enterprise Admins.

**5. Post-Exploitation and Outcome:**
Armed with this precise intelligence, the attacker completely ignores the noisy paths suggested by the default GUI. They leverage their existing access on `WEB-DEV-01` to modify the `Legacy-Printers` GPO, injecting a stealthy WMI event subscription payload. When the Enterprise Admins' jump server processes the GPO update, it executes the payload, granting the attacker a reverse shell with SYSTEM privileges in the heart of Tier 0. The custom Cypher query saved days of manual analysis and provided a practically undetectable escalation route.

## Chaining Opportunities
- [[01 - Active Directory Enumeration]]
- [[18 - Overcoming Tiered Administration Models]]

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

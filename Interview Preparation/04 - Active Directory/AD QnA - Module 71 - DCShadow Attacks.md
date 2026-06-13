---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 71"
---

# Active Directory Security Interview QnA: DCShadow Attacks

## ASCII Diagram: DCShadow Attack Flow

```text
+-----------------------------------------------------------------------------+
|                                                                             |
|                                                                             |
|   +---------------------+       (1) Register Rogue DC (CN=Sites)            |
|   |                     | --------------------------------------------> +-------------------+
|   | Attacker Machine    |                                               |                   |
|   | (Rogue DC - SYSTEM) | <-------------------------------------------- | Primary Domain    |
|   |                     |       (2) Replication Triggered (DRSUAPI)     | Controller (PDC)  |
|   +---------------------+                                               |                   |
|             |                                                           +-------------------+
|             |                                                                    ^          |
|             |   (3) Push Malicious Objects/Attributes (e.g., primaryGroupID)     |          |
|             +--------------------------------------------------------------------+          |
|             |                                                                               |
|             |   (4) Deregister Rogue DC                                                     |
|             +--------------------------------------------------------------------+          |
|                                                                                             |
+-----------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the fundamental mechanics of a DCShadow attack. How does it differ from a DCSync attack, and why is it considered more stealthy for establishing persistence?**

**Answer:**
DCShadow is a highly sophisticated post-compromise attack technique designed by Benjamin Delpy and Vincent Le Toux. It allows an attacker with sufficient privileges to temporarily register a rogue workstation as a Domain Controller within the Active Directory environment. Once registered, the attacker utilizes standard Active Directory replication protocols (specifically MS-DRSR) to push malicious changes directly into the AD database on legitimate Domain Controllers. These changes can include modifying `primaryGroupID`, injecting a backdoor SID into `sIDHistory`, altering the `AdminSDHolder` object, or creating entirely new hidden accounts.

The core difference between DCShadow and DCSync lies in their directionality and purpose. DCSync abuses the `DS-Replication-Get-Changes` right to *pull* data from a legitimate DC to the attacker's machine. It effectively mimics a DC to extract sensitive information like the KRBTGT password hash or other user credentials. It is a read operation.
Conversely, DCShadow is a *push* attack. It mimics a DC to *write* data into the domain environment. It requires the rogue DC to be formally (temporarily) registered in the Active Directory Configuration partition so that legitimate DCs will accept its replication data.

DCShadow is considered exceptionally stealthy for persistence because it completely bypasses the standard directory management APIs (like SAM RPC or LDAP). When an administrator typically modifies a user group via Active Directory Users and Computers (ADUC), the DC processes this through the SAM, generating standard event logs like Event ID 4728 (A member was added to a security-enabled global group). DCShadow injects the changes directly at the database replication level. The legitimate DCs accept these changes as valid replicated data from a peer DC, and therefore, they do NOT generate the standard user/group modification event logs. This creates a massive blind spot for SIEM solutions relying solely on typical AD auditing events.

**Q2: Detail the specific Active Directory replication protocols, RPC interfaces, and the step-by-step AD object modifications required to successfully stage and execute a DCShadow attack.**

**Answer:**
DCShadow heavily relies on abusing the Directory Replication Service (DRS) Remote Protocol. The primary RPC interface utilized is `drsuapi`, which operates over the UUID `E3514235-4B06-11D1-AB04-00C04FC2DCD2`.
The execution follows a strict sequence of AD object modifications and RPC calls:

1. **Rogue DC Registration:** The attacker must create new objects in the Active Directory Configuration partition. Specifically, under `CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=domain,DC=com`, they create a new `server` object representing the rogue DC workstation.
2. **nTDSDSA Object Creation:** Beneath the newly created `server` object, an `nTDSDSA` (NTDS Settings) object is instantiated. This object is critical as it formally designates the server as a directory service agent capable of replication.
3. **SPN Modification:** The computer account of the rogue DC must be updated with specific Service Principal Names (SPNs) to authenticate replication traffic, typically adding `GC/` (Global Catalog) and the DRSUAPI UUID SPNs.
4. **RPC Server Initialization:** On the attacker workstation, a malicious RPC server is started (usually via Mimikatz running as SYSTEM) that listens on the `drsuapi` endpoint. This server is pre-loaded with the malicious objects/attributes the attacker intends to push.
5. **Replication Trigger:** The attacker forces a replication event. This can be done by invoking `IDL_DRSReplicaAdd` against a legitimate DC, instructing it to replicate from the rogue DC, or by waiting for the Knowledge Consistency Checker (KCC) to naturally build the replication topology (which is slower).
6. **Data Push:** Once replication is triggered, the legitimate DC binds to the rogue DC's RPC server via `IDL_DRSBind`. The rogue DC then responds to replication requests (like `IDL_DRSGetNCChanges`) by supplying the crafted malicious data.
7. **Cleanup:** Immediately after the push, the attacker deletes the `nTDSDSA` and `server` objects from the Configuration partition to erase the most obvious footprint of the attack.

**Q3: What are the absolute minimum privileges and environmental prerequisites required for an attacker to successfully execute a DCShadow attack?**

**Answer:**
DCShadow is not a privilege escalation technique; it is a persistence and evasion technique that requires highly privileged access from the outset.
The prerequisites are:

1. **Administrative Privileges:** The attacker must possess Domain Admin, Enterprise Admin, or equivalent privileges. Specifically, they require the `Write` and `CreateChild` permissions within the `CN=Sites` container of the Configuration partition to register the rogue DC. They also need `Write` permissions on the specific target objects they intend to modify (e.g., if modifying a DA account, they need rights over that account).
2. **Local SYSTEM Access:** The attacker needs `NT AUTHORITY\SYSTEM` privileges on the workstation they are using as the rogue DC. This is required to start the RPC server, open the necessary network ports, and impersonate the machine account for Kerberos authentication during the DRSUAPI bind process.
3. **Network Connectivity:** The rogue DC workstation must have bidirectional RPC connectivity over TCP/IP to the primary Domain Controllers. If host-based firewalls or network segmentation block arbitrary workstations from initiating DRSUAPI traffic (TCP 135 and dynamic high ports) to the DCs, the attack will fail.
4. **Machine Account:** The attack must be executed from a domain-joined machine, as it utilizes the machine's credentials (or a crafted Silver Ticket for the machine account) to establish trust during replication.

## Scenario-Based Questions

**Q4: You are operating on a Red Team engagement. You have obtained Enterprise Admin credentials and have elevated to SYSTEM on a domain-joined Windows 10 workstation. Your objective is to grant long-term, undetectable persistence to a compromised standard user account (`jdoe`) by modifying its `sIDHistory` attribute to include the Enterprise Admins SID. Walk me through exactly how you would execute this using DCShadow, and explain why this specific attribute modification is so devastating.**

**Answer:**
To execute this objective, I would utilize two separate command-line sessions to handle the differing privilege contexts required.

**Session 1 (Running as SYSTEM on the workstation):**
1. I would launch Mimikatz. Since I am SYSTEM, I can interact directly with the local machine's identity and open the required RPC ports.
2. I would prepare the DCShadow payload by staging the malicious change locally. The command would be:
   `lsadump::dcshadow /object:jdoe /attribute:sIDHistory /value:S-1-5-21-DOMAIN-SID-519`
   (Where `S-1-5-...-519` is the SID for Enterprise Admins).
3. This command starts the malicious RPC server on the workstation, patiently waiting for a legitimate DC to request replication data. It effectively pauses and listens.

**Session 2 (Running in the context of the compromised Enterprise Admin user):**
1. In this session, I would trigger the actual registration and push mechanism, leveraging the EA rights to modify the Configuration partition.
2. I would run: `lsadump::dcshadow /push`
3. This command authenticates to the primary DC as the Enterprise Admin. It quickly writes the `server` and `nTDSDSA` objects to the Configuration partition, triggers an immediate replication cycle targeting the workstation, and then deletes the rogue DC objects.

**Why is this devastating?**
Modifying `sIDHistory` via DCShadow is exceptionally dangerous for several reasons. First, `sIDHistory` is a protected attribute. Standard LDAP modification tools (even running as Domain Admin) cannot easily write to it without using specialized APIs. DCShadow bypasses this entirely.
Second, by injecting the Enterprise Admins SID into the `sIDHistory` of a standard user (`jdoe`), whenever `jdoe` authenticates, the Domain Controller constructs a Ticket Granting Ticket (TGT) that includes the Enterprise Admin SID in the Privileged Attribute Certificate (PAC).
From that moment on, the `jdoe` account—which appears perfectly normal, belongs to no privileged groups, and has no suspicious group memberships—will be treated by every system in the forest as an Enterprise Admin. Because the change was injected via replication, no standard event logs (like group membership changes) were generated, making it practically invisible to a standard SOC that solely monitors Group Membership Event IDs.

**Q5: During a simulated adversary emulation exercise, you execute a DCShadow attack. The Blue Team, relying heavily on a standard SIEM deployment ingesting Windows Security Event Logs, claims they have zero visibility into your persistence mechanism. How do you explain the architectural blind spot to them, and what specific, high-fidelity Event IDs must they start monitoring to detect the staging phase of DCShadow?**

**Answer:**
I would explain that their SIEM is likely tuned to monitor the Directory Service Assessment APIs and SAM remote protocol interfaces. When changes are made via these standard management interfaces, the DC generates expected logs like Event ID 4728 (group modified) or 4738 (user account changed).
DCShadow intentionally avoids these APIs. It acts as a peer DC and injects raw database modifications via MS-DRSR replication. Legitimate DCs inherently trust replication data from other DCs and do not generate user-modification logs for replicated changes. If they did, it would cause massive log storms during normal domain operations. This is the architectural blind spot.

To detect DCShadow, the Blue Team must shift their focus from the *result* of the attack to the *staging* of the attack. They must monitor the Configuration partition.
The specific, high-fidelity detection mechanisms rely on:

1. **Event ID 4662 (An operation was performed on an object):** They must enable strict SACLs (System Access Control Lists) on the `CN=Sites,CN=Configuration...` container. They need to monitor for the creation of new `server` and specifically `nTDSDSA` objects. Because DCShadow requires creating these objects and then deleting them a few seconds later, an Event 4662 showing an `Add` followed almost immediately by a `Delete` for an `nTDSDSA` object from a non-DC IP address is a critical, high-fidelity indicator.
2. **Event ID 5127 (A directory service replication object was created):** This event is explicitly tied to the creation of replication links and should be scrutinized if it involves non-standard DC IPs.
3. **Event ID 4742 (A computer account was changed):** Monitoring for rapid, unusual SPN additions. A workstation computer account suddenly adding `GC/` or DRSUAPI UUID SPNs is highly anomalous and indicates the workstation is attempting to masquerade as a Domain Controller.

## Deep-Dive Defensive Questions

**Q6: From an Enterprise Architecture and Network Security perspective, how would you design a zero-trust network perimeter specifically to neutralize DCShadow attacks, even if the attacker possesses full Domain Admin credentials?**

**Answer:**
A Zero-Trust approach to mitigating DCShadow focuses on the principle that "identity alone is insufficient" and must be combined with strict network telemetry and micro-segmentation. Even if an attacker is a Domain Admin, their workstation should not be architecturally capable of acting as a Domain Controller.

1. **Strict DC Micro-Segmentation:** All legitimate Domain Controllers must be placed in a highly restricted, isolated VLAN (Tier 0 VLAN).
2. **Network-Level RPC Filtering:** DCShadow requires the legitimate DCs to establish an inbound RPC connection (DRSUAPI) to the rogue workstation. The enterprise firewall separating the workstation networks from the Tier 0 VLAN must implement strict stateful inspection. It must explicitly block any connection initiated from the Tier 0 VLAN *outbound* to the workstation network on RPC dynamic ports.
3. **Host-Based Windows Defender Firewall:** On the Domain Controllers themselves, Windows Firewall rules must be configured to only allow inbound and outbound DRSUAPI traffic (RPC UUID E3514235-4B06-11D1-AB04-00C04FC2DCD2) from explicitly defined IP addresses belonging to other known, legitimate DCs. Traffic from the workstation subnet attempting to bind to this UUID must be dropped and heavily alerted.
4. **Network Detection and Response (NDR):** Deploy an NDR solution (like Zeek or ExtraHop) parsing DCE/RPC traffic. The NDR should maintain a dynamic baseline of all legitimate DC MAC and IP addresses. Any RPC bind request utilizing the DRSUAPI UUID originating from an IP outside this trusted baseline should trigger an automated SOAR playbook to instantly quarantine the offending workstation port at the switch level.

**Q7: Assume a post-breach scenario where you suspect a DCShadow attack may have already occurred months ago. Standard logs have rolled over. How would you hunt for the lingering artifacts of a successful DCShadow attack within the Active Directory database?**

**Answer:**
Hunting for historical DCShadow artifacts requires deep AD introspection and analyzing metadata, as the standard event logs are gone.

1. **Replication Metadata Analysis:** Every attribute on every object in AD contains replication metadata. I would use the `repadmin /showobjmeta` command or PowerShell (`Get-ADReplicationAttributeMetadata`) against critical objects like `AdminSDHolder`, the `Domain Admins` group, or highly privileged user accounts.
2. **Originating DSA Identification:** The metadata reveals the `Originating DSA` (Directory System Agent) that made the last modification. A legitimate change will show the UUID of a known, current Domain Controller.
3. **Tombstone/Deleted Object Correlation:** If a modification was made via DCShadow, the `Originating DSA` will reflect the UUID of the rogue DC's temporary `nTDSDSA` object. Since the attacker deleted the rogue DC after the attack, this UUID will no longer resolve to an active DC in the Configuration partition.
4. **Hunting for Orphaned Invocation IDs:** Finding modifications attributed to a deleted or unknown Invocation ID/DSA UUID is a massive red flag. By correlating the timestamp of that modification with deleted object metadata in the Configuration partition (using tools that parse the AD Recycle Bin or deleted objects tombstone), you can definitively prove that a temporary, rogue DC was responsible for injecting the change.
5. **Auditing sIDHistory:** Systematically query the entire domain for any user objects where the `sIDHistory` attribute contains SIDs belonging to high-privileged groups (e.g., ending in -512, -519). Legitimate uses of `sIDHistory` (like inter-forest migrations) rarely involve assigning Domain Admin SIDs to standard users. Any such anomaly must be investigated immediately.

## Real-World Attack Scenario

In a recent high-profile ransomware incident, the threat actors gained initial access via a spear-phishing payload. After extensive lateral movement, they compromised a workstation belonging to a Helpdesk user who had overly permissive delegated rights, eventually allowing them to elevate to a Domain Admin equivalent through an ACL misconfiguration on the domain root.
Instead of dumping credentials directly or modifying groups which would trigger the organization's SIEM alerts, they utilized DCShadow. They registered the Helpdesk workstation as a rogue DC for precisely 4 seconds. During this window, they pushed a new, heavily obfuscated backdoor SID into the `sIDHistory` attribute of a dormant service account, granting it Enterprise Admin privileges. Because no Event ID 4728 or 5136 fired, the SOC missed the persistence mechanism. Three weeks later, the actors returned, utilized the service account to deploy ransomware across the entire estate, bypassing the incident response team's containment efforts.

## Chaining Opportunities

- **DCShadow + AdminSDHolder Modification:** Using DCShadow to stealthily append a malicious user to the `AdminSDHolder` ACL, ensuring persistence across all protected groups.
- **DCShadow + sIDHistory Injection:** Injecting high-privileged SIDs (like Enterprise Admins-519) into standard user accounts for covert lateral movement.
- **Kerberoasting -> Privilege Escalation -> DCShadow:** Obtaining initial access, kerberoasting a vulnerable service, escalating to DA, and then using DCShadow to establish untraceable persistence.

## Related Notes

- [[70 - DCSync Attacks]]
- [[65 - Active Directory Replication Protocols]]
- [[50 - Active Directory Persistence Mechanisms]]
- [[45 - AdminSDHolder and SDProp]]
- [[30 - Active Directory Auditing and Telemetry]]

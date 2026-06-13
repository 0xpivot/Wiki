---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 77"
---

# Cross-Forest and Cross-Domain Trust Attacks

## Custom ASCII Diagram: Forging Inter-Realm TGTs across a Forest Trust

```text
  +-------------------------------------------------------------+
  |                   FOREST: TARGET.LOCAL                      |
  |                                                             |
  |   +-------------------+              +------------------+   |
  |   |   Root Domain     |              |  Resource Server |   |
  |   |  (Target.local)   |              |  (DC.Target.local|   |
  |   +---------+---------+              +------------------+   |
  |             ^                                   ^           |
  +-------------|-----------------------------------|-----------+
                |                                   |
                | (3) Present Forged TGT            | (4) TGS Granted for
                |     with Enterprise Admin         |     Resource Server
                |     SID History                   |
                |                                   v
  +-------------|---------------------------------------------------------+
  |             |     FOREST: COMPROMISED.LOCAL                           |
  |             |                                                         |
  |   +---------+---------+                                               |
  |   |   Child Domain    |   (1) Attacker compromises Child DC,          |
  |   | (Child.Comp.local)|       extracts Trust Key (Inter-Realm Key)    |
  |   +-------------------+       shared between Child & Target Root      |
  |                                                                       |
  |     Attacker uses Mimikatz/Rubeus to forge an Inter-Realm TGT:        |
  |     - Sign with: Trust Key                                            |
  |     - User: Administrator                                             |
  |     - SID History: S-1-5-21-XXX-519 (Enterprise Admins of Target)     |
  |     (2) SID Filtering must be disabled (TGT_DELEGATION) for success!  |
  +-----------------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: Explain the fundamental difference between a Forest Trust and an External Trust, specifically regarding SID Filtering and Authentication routing.
**Expert Answer:**
**Forest Trusts** are transitive, two-way (by default) trusts established between two Active Directory forest root domains. Because they connect the root domains, the trust relationship inherently extends to all child domains within both forests (due to transitivity). Forest trusts utilize Kerberos as the primary authentication protocol. Crucially, by default, Forest Trusts enforce **SID Filtering**. This means that if a user from Forest A requests a ticket to access Forest B, Forest B's Domain Controller will strip out any SIDs in the Ticket Granting Service (TGS) ticket that do not authoritatively belong to Forest A. This prevents an attacker in Forest A from adding a Forest B Enterprise Admin SID into their SID History.

**External Trusts** are non-transitive trusts established between two specific domains in different forests, or a domain and an NT4 domain. Because they are non-transitive, a trust between Domain A and Domain B does not automatically grant access to Domain C (a child of B). External trusts often fall back to NTLM authentication, though Kerberos is supported if explicitly configured. Similar to Forest Trusts, SID Filtering is enabled by default to prevent privilege escalation via malicious SID History injection.

### Q2: What is an Inter-Realm Key, how is it generated, and why is it critical for Cross-Domain attacks within the same forest?
**Expert Answer:**
An Inter-Realm Key is the cryptographic trust key established between two domains that share a trust relationship. Under the hood, Active Directory creates a hidden trusted domain object (TDO) and an associated hidden user account (ending with a `$`, like `CHILD$`) in the trusting domain. The Inter-Realm Key is essentially the password hash (RC4, AES128, AES256) of this hidden trust account.

In a cross-domain attack within the same forest (e.g., child domain to parent domain), the Inter-Realm Key is critical because **SID Filtering is disabled by default within the same forest**. If an attacker compromises the child domain, they can dump the `krbtgt` hash or the specific Inter-Realm Key. Using this key, the attacker can forge an Inter-Realm Ticket Granting Ticket (TGT) using a Golden Ticket attack. They inject the `Enterprise Admins` SID of the parent domain into the `ExtraSids` (SID History) portion of the PAC. They then sign this ticket with the Inter-Realm Key and present it to the parent domain's Domain Controller. The parent DC decrypts the ticket, trusts the signature, ignores the injected SID because filtering is off, and grants the attacker full Enterprise Admin access.

### Q3: How does Unconstrained Delegation interact with Cross-Forest trusts, and what security boundary does it break if misconfigured?
**Expert Answer:**
Unconstrained Delegation allows a service (like a web server) to request and cache the TGT of any user who authenticates to it. If a user from Forest A authenticates to a server with Unconstrained Delegation in Forest B, the server in Forest B now holds the user's TGT and can impersonate them anywhere.
By default, the "Enable-TGT-Delegation" flag is disabled across Forest Trusts. This acts as a security boundary: even if a user from Forest A connects to an unconstrained server in Forest B, the Forest A DC will NOT forward the TGT across the trust boundary.
However, if an administrator mistakenly enables TGT Delegation across the forest trust (using `netdom trust /EnableTGTDelegation:Yes`), this security boundary is completely broken. An attacker who compromises the unconstrained server in Forest B can coerce a highly privileged account (like a Domain Controller machine account) from Forest A to authenticate. The attacker will then capture the TGT of the Forest A DC and use it to execute DCSync, completely compromising Forest A from Forest B.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You have fully compromised `child.corp.local`. You want to elevate to `corp.local`. Explain the exact commands and tools you would use to perform an ExtraSids attack to compromise the parent domain.
**Expert Answer:**
To compromise the parent domain `corp.local` from `child.corp.local` using ExtraSids, I need the child domain's `krbtgt` hash and the SID of the parent domain's Enterprise Admins group.

1. **Extract Data:** On the compromised child DC, I run Mimikatz to dump the `krbtgt` hash and the child domain SID.
   `mimikatz # lsadump::dcsync /domain:child.corp.local /user:krbtgt`
   I also resolve the SID for the parent domain `corp.local`. Let's say it's `S-1-5-21-1111-2222-3333`. The Enterprise Admins group is always `-519`.
2. **Forge the Golden Ticket:** On my attacker machine, I use Mimikatz to forge a Golden Ticket. I specify a fake user, the child domain SID, the child `krbtgt` hash, and inject the parent's Enterprise Admin SID into the `/sids` parameter.
   `mimikatz # kerberos::golden /user:Administrator /domain:child.corp.local /sid:S-1-5-21-4444-5555-6666 /sids:S-1-5-21-1111-2222-3333-519 /rc4:<krbtgt_hash> /ptt`
3. **Exploitation:** The ticket is injected into memory (`/ptt`). Because I am within the same forest, SID filtering is not enforced. I can now verify my access to the parent DC.
   `dir \\dc01.corp.local\c$`
4. **DCSync Parent:** Finally, I use DCSync against the parent DC to extract the parent `krbtgt` hash, achieving full Enterprise Admin compromise.
   `mimikatz # lsadump::dcsync /domain:corp.local /user:corp\krbtgt`

### Q2: You have compromised Forest A and notice a two-way Forest Trust with Forest B. You dump the Inter-Realm Trust Key. You attempt to forge a ticket injecting Forest B's Enterprise Admin SID, but access is denied. Why did it fail, and how can you leverage the trust if you find a misconfigured shared group?
**Expert Answer:**
**Why it failed:** It failed because SID Filtering is enabled by default across Forest Trusts. When the Domain Controller in Forest B received the forged ticket, the filtering engine identified that the injected Enterprise Admin SID (`S-1-5-21-ForestB-519`) did not originate from Forest A. The DC stripped this SID from the token, leaving me with only my Forest A privileges, which inherently have no administrative rights in Forest B.

**How to leverage a misconfigured shared group:** If a group from Forest A is manually added to a privileged local group (e.g., Local Administrators, RDP Users) on servers within Forest B, I can exploit this.
1. I enumerate Forest B to find resource-based privileges assigned to Foreign Security Principals (users/groups from Forest A). PowerView: `Get-DomainForeignGroupMember -Domain forestb.local`.
2. Let's say the Forest A group `HelpDesk_A` is an administrator on servers in Forest B.
3. I use the Forest A `krbtgt` to forge a standard Golden Ticket for Forest A, but I add the SID of the `HelpDesk_A` group to the ticket.
4. When I access the resource in Forest B, SID Filtering does NOT strip the `HelpDesk_A` SID because it legitimately belongs to Forest A.
5. The resource in Forest B sees the `HelpDesk_A` SID, maps it to the local Administrators group, and grants me SYSTEM-level access to that specific machine.

### Q3: You compromise a web server in Domain X that has a one-way outgoing trust to Domain Y (Domain X trusts Domain Y). You have local SYSTEM on the web server. How can you attack Domain Y?
**Expert Answer:**
A one-way outgoing trust where X trusts Y means users in Domain Y can access resources in Domain X, but users in X cannot access resources in Y. Since I am in Domain X, the trust direction is inherently against me for direct resource access.
However, I can use the compromised server in Domain X as a trap.
**Attack Vector: Coerced Authentication and Credentials harvesting.**
1. Since Y users access X, there might be administrators from Y logging into my compromised server. I can dump LSASS to harvest their plaintext credentials or Kerberos TGTs.
2. If the web server runs a service that users from Domain Y interact with, I can set up a rogue SMB share or use WebDAV. I can then phish or coerce a Domain Y user/admin to connect back to my compromised server.
3. If they connect, I can capture their NTLMv2 hash and attempt to crack it offline.
4. Alternatively, if Unconstrained Delegation is enabled on my compromised Domain X server, and a Domain Y admin accesses it, I will capture the Domain Y admin's TGT in memory. I can extract this TGT and use it to authenticate back into Domain Y, effectively bypassing the directional restriction of the trust.

## Deep-Dive Defensive Questions

### Q1: What specific Event IDs and anomalies should a SOC look for to detect an ExtraSids attack originating from a child domain?
**Expert Answer:**
Detecting ExtraSids requires analyzing Kerberos TGS requests on the parent Domain Controller.
1. **Event ID 4769 (A Kerberos service ticket was requested):** The SOC should monitor this event on the parent DC. The key indicator is the `Account Name` and `Account Domain` compared to the target service.
2. **SID History Anomaly:** In a legitimate cross-domain authentication, a user will have their base SID and potentially legitimate SID History if they were migrated. An alert should trigger if a TGS request is made where the user originates from a Child Domain, but the PAC contains a SID belonging to a highly privileged Parent Domain group (like Enterprise Admins `-519` or Domain Admins `-512`). 
3. **Advanced ATA/MDI Telemetry:** Microsoft Defender for Identity (MDI) explicitly flags this by analyzing the PAC signature and the SIDs contained within. If MDI sees a cross-domain TGT presented where the SIDs do not logically align with the user's origin, it throws a "Suspicious addition of SID History" alert.

### Q2: What is the risk of utilizing the `netdom trust /Quarantine:No` command, and when should a security engineer explicitly enforce quarantine?
**Expert Answer:**
The `netdom trust /Quarantine:No` command disables SID Filtering across an external trust. 
**The Risk:** By disabling quarantine (SID Filtering), the trusting domain will accept any SID presented in the Kerberos PAC or NTLM token from the trusted domain. If the trusted domain is compromised, an attacker can forge a ticket containing the `Domain Admins` SID of the trusting domain. Because filtering is disabled, the trusting domain will accept this injected SID, resulting in instant Domain Admin compromise of the trusting domain.
**When to enforce:** A security engineer should ALWAYS enforce quarantine (`/Quarantine:Yes`) on any external trust, especially if the trust is with a third-party vendor, an acquired company whose security posture is unknown, or an older legacy domain. Quarantine should only be disabled if absolutely necessary for a specific AD migration scenario, and even then, only temporarily and under heavy monitoring.

### Q3: How do Trust Passwords rotate, and can a SOC detect if an attacker has exported the Inter-Realm key and is using it offline?
**Expert Answer:**
Trust passwords (Inter-Realm keys) rotate automatically every 30 days by default. The Primary Domain Controller (PDC) emulator of the trusted domain initiates the password change and updates the trusting domain.
**Detecting Offline Use:**
If an attacker dumps the trust key and uses it offline to forge Inter-Realm TGTs, it is difficult to detect at the network level because the cryptography is technically valid. However, there are behavioral indicators:
1. **Ticket Lifetimes:** Forged tickets often have default lifetimes (e.g., 10 years in older Mimikatz builds) that violate the domain's Kerberos policy. Event 4769 will show abnormal ticket expiration times.
2. **Encryption Downgrades:** If the attacker's tooling defaults to forging RC4 signatures, but the domain policy mandates AES256 for trust tickets, the presence of an RC4-signed Inter-Realm TGT (seen in network PCAPs or advanced logging) is a massive red flag.
3. **Password Rotation Mismatch:** If the attacker dumps the key on Day 28, and the domain rotates the key on Day 30, the attacker's forged tickets will suddenly fail on Day 31. The DC will log Event ID 4624/4625 indicating an authentication failure due to a bad signature from a trusted domain, revealing that stale keys are being attempted.

## Real-World Attack Scenario

### The Mergers and Acquisitions Nightmare
"TechCorp" recently acquired "StartupInc". To facilitate collaboration, IT established a two-way Forest Trust between `techcorp.local` and `startupinc.local`. To allow StartupInc admins to manage specific shared servers in TechCorp, the IT team disabled SID Filtering (`/Quarantine:No`) to "make permissions easier to map", ignoring security best practices.

A Red Team was hired to assess the new posture. They started in the StartupInc network. Because StartupInc had weaker security controls, the Red Team quickly compromised a local workstation and used Kerberoasting to obtain a service account password that happened to be a Local Admin on the StartupInc Domain Controller. They dumped the `krbtgt` hash of `startupinc.local`.

Knowing about the Forest Trust, the Red Team ran BloodHound and identified that the TechCorp Enterprise Admin group SID was `S-1-5-21-1234-5678-9012-519`.
Using Mimikatz on their attacking machine, they forged an Inter-Realm TGT. They signed it with the StartupInc `krbtgt` hash and injected the TechCorp Enterprise Admin SID into the ExtraSids field. 

Because the IT team had disabled SID filtering on the forest trust, the TechCorp Domain Controller accepted the ticket without stripping the injected SID. The Red Team presented this ticket to the TechCorp DC, executed DCSync, and dumped the entire `techcorp.local` credential database, achieving total compromise of the parent company via the newly acquired, less secure startup.

## Chaining Opportunities
*   **Kerberos Golden Tickets (Module 80):** Cross-domain attacks heavily rely on the Golden Ticket mechanism to forge the initial TGT and inject the malicious SID history.
*   **Unconstrained Delegation (Module 81):** If a cross-forest trust allows TGT delegation, attackers can chain unconstrained delegation exploits across the trust boundary.
*   **Kerberoasting (Module 74):** Often used in the trusted domain to gain the initial foothold required to dump the child `krbtgt` or Inter-Realm key.

## Related Notes
*   [[04 - Active Directory/AD QnA - Module 80 - Golden Ticket Attacks]]
*   [[04 - Active Directory/AD QnA - Module 81 - Kerberos Delegation Attacks]]
*   [[04 - Active Directory/AD QnA - Module 74 - Kerberoasting and AS-REP Roasting]]
*   [[04 - Active Directory/AD QnA - Module 75 - Kerberos Attacks and Tickets]]

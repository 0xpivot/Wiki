---
tags: [active-directory, forest-trust, sid-history, golden-ticket]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.25 Forest Trust Attacks"
---

# 36.25 Forest Trust Attacks

## 1. Introduction and Architectural Overview
Active Directory (AD) uses a hierarchical structure where the highest logical boundary is the **Forest**. A single forest can contain multiple domains. By default, domains within the same forest implicitly trust each other, allowing users from one domain to access resources in another, assuming they have the requisite permissions.

However, many organizations operate multiple forests. This could be due to mergers, acquisitions, strict isolation requirements, or legacy architectural decisions. To allow users in one forest to access resources in another, administrators establish **Forest Trusts**.

While trusts facilitate collaboration and resource sharing, they also introduce attack paths. If an attacker fully compromises one forest, they can often leverage trust relationships to attack or compromise connected forests, especially when configuration flaws like missing **SID Filtering** are present.

### ASCII Architecture Diagram: Forest Trust Attack Flow

```text
       [ COMPROMISED FOREST ]                                   [ TARGET FOREST ]
       Forest A (attacker.local)                               Forest B (target.local)
      +-------------------------+                             +-------------------------+
      |                         |                             |                         |
      |    [Domain Controller]  |       Forest Trust          |    [Domain Controller]  |
      |    - krbtgt hash        |<===========================>|    - Resources          |
      |    - Trust Key          |     (Inter-Forest)          |    - Enterprise Admins  |
      |                         |                             |                         |
      +-------------------------+                             +-------------------------+
                 |                                                         ^
                 | 1. Compromise Forest A                                  |
                 | 2. Extract Trust Key ($)                                | 5. Access target resources
                 | 3. Forge Inter-Forest TGT                               |
                 |    (Inject SID History)                                 |
                 v                                                         |
          [ Attacker Machine ] --------------------------------------------+
                                  4. Present forged TGT to Target DC
```

## 2. Deep Dive into Trust Mechanics
To exploit trusts, one must understand how AD implements them under the hood.

### 2.1 Trust Types
- **Parent-Child Trusts**: Implicit, two-way, transitive trusts within a single forest.
- **Tree-Root Trusts**: Implicit, two-way, transitive trusts connecting different domain trees in the same forest.
- **External Trusts**: Explicit, one-way or two-way, non-transitive trusts connecting domains in different forests (or NT4 domains).
- **Forest Trusts**: Explicit, one-way or two-way, transitive trusts connecting the root domains of two different forests.

### 2.2 Directionality
The direction of the trust dictates the direction of access. A crucial AD mantra to remember is: **Access flows in the opposite direction of the trust.**
- **Outbound Trust**: The local domain trusts the remote domain. Users in the remote domain can access resources in the local domain.
- **Inbound Trust**: The remote domain trusts the local domain. Users in the local domain can access resources in the remote domain.
- **Two-Way Trust**: Both domains trust each other.

### 2.3 The Trust Key (Password)
When a trust is established, AD creates a **Trusted Domain Object (TDO)** in the `System` container. A special hidden user account is also created to represent the trust. The password for this account is known as the **Trust Key**.
For a trust from `DomainA` to `DomainB`, a computer account ending with `$` is created. The NTLM hash or RC4/AES keys of this password are used to encrypt and sign Kerberos tickets passing across the trust boundary (Inter-realm TGTs).

## 3. SID History and SID Filtering
### 3.1 SID History
When an organization migrates a user from one domain to another, the user receives a new Security Identifier (SID) in the new domain. To ensure the user doesn't lose access to resources they previously had permissions for, AD uses the `sIDHistory` attribute. The user's old SID is added to this attribute. When the user authenticates, AD includes SIDs from `sIDHistory` into the user's access token.

### 3.2 SID Filtering
If `sIDHistory` were implicitly trusted across all boundaries, an attacker in a trusted domain could simply add the SID of the `Enterprise Admins` group of the trusting domain into their own SID history and gain instant total control.
To prevent this, Microsoft introduced **SID Filtering** (also known as Quarantine).
When a ticket crosses a forest trust, the trusting Domain Controller inspects the SIDs in the PAC. If SID Filtering is enabled, any SID that does not belong to the trusted domain is stripped out.
- **Intra-Forest Trusts**: SID Filtering is disabled by default. A compromise of a child domain easily leads to the compromise of the forest root (via Golden Ticket with SID History).
- **Inter-Forest Trusts**: SID Filtering is enabled by default. Only SIDs belonging to the trusted forest are accepted.

## 4. Exploiting Forest Trusts

### 4.1 Prerequisites
To execute a forest trust attack (specifically forging an inter-realm ticket), you need:
1. Complete compromise of the trusted forest (Domain Admin/Enterprise Admin).
2. The Trust Key (the password hash of the inter-forest trust).
3. The exact name and SID of the trusted domain.
4. The exact name and SID of the trusting (target) domain.
5. (Crucial) **SID Filtering must be disabled** or bypassed.

### 4.2 Extracting the Trust Key
Once you hold Domain Admin in the trusted forest, you can dump the trust keys using Mimikatz.
```bash
# On the compromised DC
Invoke-Mimikatz -Command '"lsadump::trust /patch"'
```
This command outputs the domain trusts and the corresponding RC4 or AES keys. You need the `[OUT]` trust key if you are attacking the outbound trusting domain.
Alternatively, Impacket's `secretsdump.py` can be used to extract the Trust Key from the NTDS.dit file or via DCSync.
```bash
python3 secretsdump.py domain.local/administrator@192.168.1.10 -just-dc-ntlm
```
Look for the account name that matches the trust name, ending in a `$`.

### 4.3 Forging the Inter-Realm TGT
Using the extracted trust key, you can forge an Inter-Realm Golden Ticket. This is a ticket encrypted with the trust key, containing your desired user details and, most importantly, the `sIDHistory` containing the SID of a high-privileged group in the target domain (e.g., Enterprise Admins).

```bash
# Syntax using Rubeus
Rubeus.exe golden /rc4:<TRUST_KEY> /domain:<COMPROMISED_DOMAIN> /sid:<COMPROMISED_DOMAIN_SID> /sids:<TARGET_ENTERPRISE_ADMIN_SID> /user:Administrator /target:<TARGET_DOMAIN> /ticket:trust_tgs.kirbi
```
You can also use Impacket's `ticketer.py` from Linux:
```bash
python3 ticketer.py -nthash <TRUST_KEY_HASH> -domain-sid <COMPROMISED_DOMAIN_SID> -extra-sid <TARGET_ENTERPRISE_ADMIN_SID> -domain <COMPROMISED_DOMAIN> Administrator
```

### 4.4 Utilizing the Forged Ticket
Once the ticket is generated, you inject it into your session.
```bash
Rubeus.exe ptt /ticket:trust_tgs.kirbi
```
On Linux, export the ccache file:
```bash
export KRB5CCNAME=Administrator.ccache
```
Now, you can request a TGS for a service in the target domain. The target DC will decrypt the inter-realm TGT, read the SID History (assuming filtering is off), and grant you a service ticket with Enterprise Admin privileges.
```bash
dir \\target-dc.target.local\C$
python3 smbexec.py -k target.local -no-pass dc01.target.local
```

## 5. Bypassing SID Filtering
If SID Filtering is strictly enforced (which is the default for Forest Trusts), injecting `Enterprise Admins` will fail because the SID does not belong to the trusted domain's namespace.
However, attackers look for misconfigurations:

### 5.1 Misconfiguration 1: Disable SID Filter Quarantining
Sometimes administrators disable it using `netdom trust /quarantine:No` to solve legacy migration application issues. This completely opens up the forest trust to SID History injection.

### 5.2 Misconfiguration 2: Foreign Security Principals (FSP)
If a user in the trusted domain has been added to a group in the target domain, exploiting that user gives access to whatever that group has access to. You map the users/groups via BloodHound to see cross-forest nested group memberships. When an external user is added to a group, AD creates a Foreign Security Principal object. 
If an attacker compromises the trusted domain, they can simply reset the password or grab the hash of the user mapped via FSP, and use it to access resources in the trusting domain.

### 5.3 Misconfiguration 3: Unconstrained Delegation
If a machine in the trusting domain is configured for Unconstrained Delegation and an admin from the target domain authenticates to it (e.g., via CIFS or HTTP), the attacker can steal their TGT. This is a severe cross-forest attack vector that relies on service configurations rather than SID history.

### 5.4 Misconfiguration 4: Targeted SIDs
Depending on the exact trust type and patch level, some SIDs might slip through or explicit SID history injection might not be needed if cross-domain group membership is heavily abused. For example, injecting the SID of a specific highly-privileged group that is not a built-in group (like `Enterprise Admins`) but rather a custom IT admin group.

## 6. Enumerating Trusts with BloodHound
BloodHound is the best tool for visualizing forest trust attacks.
Using the Azure/AD ingestor:
```bash
SharpHound.exe -c All,Trusts
```
In BloodHound GUI, you can query:
- `Map Domain Trusts`
- `Shortest Path to Domain Admin`
Look for edges labeled `TrustedBy` or `HasSIDHistory`.
Trust analysis in BloodHound helps identify not only the direction of the trust but also the specific attributes, such as whether SID filtering is enabled.

## 7. Step-by-Step Scenario: The "Migration" Loophole
Organizations often undergo multi-year AD migrations. During this time, two forests coexist.
1. Admin sets up a Two-Way Forest Trust between `old.corp` and `new.corp`.
2. To ensure legacy apps work, Admin disables SID filtering: `netdom trust old.corp /domain:new.corp /enablesidhistory:yes`.
3. Attacker breaches `old.corp` via an unpatched vulnerability or phishing.
4. Attacker performs DCSync and dumps the trust key for `new.corp`.
5. Attacker uses Impacket's `ticketer.py` to forge a ticket including `new.corp-SID-519` (Enterprise Admins) in the SID History.
6. Attacker maps the C$ of the `new.corp` DC and dumps NTDS.dit. Both forests fall.
7. The attacker establishes persistence in the new forest.

## 8. Defending and Mitigating

### 8.1 Enforce SID Filtering
Never disable SID filtering on inter-forest or external trusts unless absolutely required for a temporary migration, and even then, understand the immense risk.
```cmd
netdom trust trustingdomain.local /domain:trusteddomain.local /quarantine:Yes
netdom trust trustingdomain.local /domain:trusteddomain.local /enablesidhistory:No
```

### 8.2 Treat Forests as Security Boundaries
The forest is the ultimate security boundary. If you trust another forest, you are implicitly accepting their security posture. If the trusted forest is weak, your forest is at risk. Always operate under the assumption that a two-way trust with SID filtering disabled merges the threat landscapes of both domains.
Consider implementing stricter boundaries or migrating users completely rather than relying on long-term trusts.

### 8.3 Selective Authentication
Instead of Forest-Wide Authentication, use **Selective Authentication** over trusts. This requires explicit assignment of the `Allowed to Authenticate` permission on specific computer objects in the target domain before users from the trusted domain can access them. This severely limits the blast radius if the trusted domain is compromised.

### 8.4 Monitoring and Detection
- **Event ID 4624 (Logon)**: Look for cross-domain authentications. Pay attention to `Logon Type 3` (Network) across trusts.
- **Event ID 4769 (Kerberos Service Ticket Requested)**: Analyze cross-realm TGT requests where the target is a highly sensitive service.
- **Event ID 4662 (Operation on an object)**: Monitor access to the `Trusted Domain Objects` in AD.
- **Microsoft Defender for Identity (MDI)**: Alerts on suspected Golden Ticket usage and abnormal SID history anomalies. Look for SIDs in the token that do not match the expected user domain.
- **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested)**: Monitor for unusual ticket requests.

## 9. Advanced Attack Concept: Trust Key Rotation
Trust passwords (keys) are rotated automatically by the system every 30 days. An attacker who dumps the trust key has a maximum of 30 days to use it before it becomes invalid. However, if the attacker compromises the Domain Controller of the trusting domain, they can manually reset the trust password or disable the automatic rotation to maintain persistent access.

## 10. Conclusion
Forest trust attacks remind us that Active Directory is built on transitive trust. While MS default settings (like enabling SID Filtering for inter-forest trusts) provide strong protection, organizational requirements often lead administrators to weaken these boundaries. Attackers rely on finding these misconfigurations to spread from a less secure, acquired domain into the highly secure corporate root. A deep understanding of trust mechanics, SID filtering, and Kerberos is required to successfully identify and exploit or defend against these attacks.

## Real-World Attack Scenario

During a red team engagement for a recently merged corporation, the attacker compromised the Active Directory forest of the acquired company, `legacy.local`. The ultimate goal was to pivot into the parent company's highly secure forest, `megacorp.local`. The two forests were connected via a Two-Way Forest Trust to facilitate resource sharing during the transition.

Enumeration with BloodHound revealed that to support legacy application migrations, the parent company administrators had explicitly disabled SID Filtering (Quarantine) on the trust. This critical misconfiguration meant the parent forest would accept SIDs injected into the SID History attribute from the legacy forest.

The attacker first established Domain Admin privileges in `legacy.local`. Using Mimikatz on the legacy Domain Controller, they extracted the Trust Key (the password hash for the inter-forest trust account):
```text
mimikatz # lsadump::trust /patch
```
This yielded the RC4 hash for the `MEGACORP.LOCAL$` trust account. The attacker also noted the SID of the target `megacorp.local` domain.

With the trust key, the attacker used Impacket's `ticketer.py` on their Linux attack box to forge an Inter-Realm Golden Ticket. They specifically injected the SID of `megacorp.local`'s Enterprise Admins group (`-519`) into the extra-sid parameter:
```bash
python3 ticketer.py -nthash <TRUST_KEY_HASH> -domain-sid <LEGACY_DOMAIN_SID> -extra-sid <MEGACORP_DOMAIN_SID>-519 -domain legacy.local Administrator
```

This generated a `kirbi` ticket file encrypted with the shared trust key. The attacker exported this ticket to their session:
```bash
export KRB5CCNAME=Administrator.ccache
```

Finally, the attacker used `smbexec.py` to authenticate to the primary Domain Controller of the target forest:
```bash
python3 smbexec.py -k megacorp.local -no-pass dc01.megacorp.local
```
Because SID filtering was disabled, the target DC accepted the inter-realm TGT, read the injected Enterprise Admin SID in the history, and granted the attacker a `SYSTEM` shell on the parent forest's DC, resulting in a total corporate compromise.

## 11. Chaining Opportunities
- **[[24 - Golden Ticket Attacks]]**: The fundamental mechanism used to create the Inter-Realm TGT.
- **[[20 - BloodHound & Active Directory Enumeration]]**: Essential for identifying the trust relationships and determining if SID filtering is disabled.
- **[[30 - Defense — Tiering, Least Privilege, LAPS, Defender for Identity]]**: How to properly segment networks to avoid lateral movement even if trusts exist.

## 12. Related Notes
- [[19 - Kerberos Fundamentals]]
- [[22 - Mimikatz Advanced Usage]]
- [[28 - MS14-068]]

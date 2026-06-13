---
tags: [active-directory, dcshadow, mimikatz, rogue-dc, persistence]
difficulty: expert
module: "36 - Active Directory Attacks"
topic: "36.16 DCShadow Attack"
---
# 36.16 DCShadow Attack

## 1. Introduction & Theory
The DCShadow attack is one of the most advanced and stealthy Active Directory manipulation techniques. While the DCSync attack allows an attacker to *pull* (read) data from Active Directory by simulating a Domain Controller, DCShadow allows an attacker to *push* (write) malicious data into Active Directory by temporarily registering a rogue workstation as a legitimate Domain Controller.

Created by Benjamin Delpy and Vincent Le Toux (the authors of Mimikatz), DCShadow bypasses traditional logging mechanisms. When a standard administrative action occurs (like adding a user to Domain Admins), it generates well-known Event IDs (e.g., 4728) on the DC processing the change. However, DCShadow injects the changes directly into the replication stream. To the other Domain Controllers, the rogue DC is simply synchronizing its database, and replication events are generally not logged as administrative actions. This results in no standard "user modified" Event Logs, making the attack practically invisible to standard SIEM rules.

## 2. ASCII Diagram of Attack Flow

```text
    [ Attacker Workstation (Rogue DC) ]                           [ Legitimate Domain Controller ]
              (e.g., WRKSTN-01)                                          (DC01.domain.local)
              |                                                                |
              | 1. Modifies AD Configuration Partition                         |
              |    (Registers WRKSTN-01 as a DC object)                        |
              |--------------------------------------------------------------->|
              |                                                                |
              | 2. Adds SPNs to Attacker Computer Account                      |
              |    (e.g., GC/WRKSTN-01, E3514235.../WRKSTN-01)                 |
              |--------------------------------------------------------------->|
              |                                                                |
              | 3. Starts local RPC server (Mimikatz)                          |
              |    (Acting as DRSUAPI endpoint)                                |
              |                                                                |
              | 4. Triggers KCC (Knowledge Consistency Checker)                |
              |    (Forces DC01 to replicate from the rogue DC)                |
              |--------------------------------------------------------------->|
              |                                                                |
              | 5. DC01 connects to WRKSTN-01 to pull changes                  |
              |<---------------------------------------------------------------|
              |                                                                |
              | 6. WRKSTN-01 responds with injected payload                    |
              |    (e.g., "Add 'attacker' to 'Domain Admins'")                 |
              |--------------------------------------------------------------->|
              |                                                                |
              | 7. DC01 commits changes to NTDS.DIT                            |
              |                                                                |
              | 8. Attacker removes rogue DC configuration (Cleanup)           |
              |--------------------------------------------------------------->|
```

## 3. Attack Mechanics
The DCShadow attack operates in several precise stages:
1. **Registration:** The attacker modifies the Configuration partition of AD to create a new `server` object representing the rogue DC, placing it under an existing site in `CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=domain,DC=local`. It also creates an `nTDSDSA` object.
2. **SPN Modification:** The attacker modifies the `servicePrincipalName` (SPN) attribute of their workstation's computer account to include SPNs required for a DC, primarily the Directory Replication Service (DRS) RPC interface (`E3514235-4B06-11D1-AB04-00C04FC2DCD2/...`) and Global Catalog (`GC/...`).
3. **Staging:** The attacker prepares the malicious changes locally in Mimikatz. Mimikatz starts a local RPC server waiting for incoming replication connections.
4. **Triggering Replication:** The attacker forces the legitimate DC to compute the replication topology using the Knowledge Consistency Checker (KCC) and request replication from the rogue DC. Mimikatz handles the incoming `DRSGetNCChanges` request and serves the malicious payload.
5. **Cleanup:** Once replication is complete, Mimikatz deletes the rogue server objects from the Configuration partition and removes the injected SPNs to hide tracks.

### Prerequisites
Because DCShadow modifies the Configuration partition and adds SPNs, the attacker must already possess **Domain Admin** or **Enterprise Admin** privileges. DCShadow is fundamentally a *post-exploitation* or *persistence* technique, not an initial privilege escalation vector. 

Furthermore, the attacker requires code execution on a domain-joined machine running as `SYSTEM` (to modify the machine account's SPNs and host the RPC service).

## 4. Execution

Execution requires two separate terminal windows with high privileges (e.g., `psexec -s cmd.exe` to get `NT AUTHORITY\SYSTEM`).

### Terminal 1: Staging the Attack (Mimikatz as SYSTEM)
In the first terminal, we stage the payload. For example, let's inject a new primary group ID for a standard user to elevate them to Domain Admins, or modify `AdminSDHolder`.
Here, we will add the `SID History` of the Enterprise Admins group to an attacker-controlled user.
```text
mimikatz # lsadump::dcshadow /object:attacker_user /attribute:SIDHistory /value:S-1-5-21-123456789-123456789-123456789-519
```
Mimikatz will start the RPC server and wait.
```text
[DC] 'domain.local' will be the domain
...
[+] RPC server started!
[*] Waiting for replication...
```

### Terminal 2: Pushing the Attack (Mimikatz as DA/SYSTEM)
In the second terminal, we trigger the push. This forces the legitimate DC to replicate from the rogue DC instance running in Terminal 1.
```text
mimikatz # lsadump::dcshadow /push
```
Mimikatz forces the KCC to run and requests replication.

### Back in Terminal 1:
You will see the incoming RPC connection from the legitimate DC:
```text
[*] Incoming DRSGetNCChanges request from DC01...
[+] Payload successfully pushed!
[*] Cleaning up Active Directory objects...
[+] Cleanup complete!
```

### Practical Uses for DCShadow
Because it bypasses standard auditing, DCShadow is ideal for stealthy persistence:
- **Modifying `AdminSDHolder`:** Injecting a malicious ACL into the AdminSDHolder object, which the SDProp process will eventually stamp onto all protected administrative groups.
- **Modifying `PrimaryGroupID`:** Changing a user's primary group to 512 (Domain Admins) without explicitly adding them to the group membership list, bypassing group membership monitoring.
- **Kerberos Key Injection:** Altering the `unicodePwd` or AES keys of an existing user or computer without triggering password change event logs.

## 5. Defense & Hardening
Like DCSync, there is no technical patch to prevent DCShadow because it utilizes the core design of Active Directory replication. The primary defense is strict credential hygiene to ensure attackers never obtain the Domain Admin or Enterprise Admin privileges required to execute the attack.

- **Tiering / ESAE:** Ensure highly privileged accounts are completely isolated from lower-tier workstations. If an attacker compromises a workstation but cannot obtain DA credentials, they cannot execute DCShadow.
- **Restrict Configuration Partition Access:** By default, only Enterprise Admins and Domain Admins can write to the Configuration partition. Regularly audit the ACLs on the Configuration partition to ensure no other accounts have been granted dangerous rights.

## 6. Detection Strategies
While DCShadow bypasses standard Event ID 4728/4724 logs, it generates its own unique artifacts during the setup and cleanup phases.

### Event Logs
- **Event ID 4932 / 4933:** Active Directory replica source was added / removed. Monitoring for these events is crucial. Legitimate DCs are rarely added or removed in a production environment.
- **Event ID 5136:** Directory Service Changes. If SACLs are enabled on the Configuration partition, you can detect the creation and deletion of the `server` and `nTDSDSA` objects.
- **Event ID 4742:** Computer Account Management. Detecting rapid modifications to a computer account's `servicePrincipalName` array, specifically the addition of SPNs beginning with `GC/` or `E3514235-4B06-11D1-AB04-00C04FC2DCD2/` by a non-administrative workstation.

### Network Monitoring
- Detection of `DRSUAPI` (RPC) traffic originating from a non-DC IP address and connecting *to* a legitimate DC.
- The use of dynamic high RPC ports originating from workstations acting as servers.

## Real-World Attack Scenario

During an internal penetration test, an attacker compromised a local administrator account on a standard engineering workstation. The primary objective was to establish deep, persistent access that would survive standard credential resets, without generating obvious "user added" logs.

**The Context**
The attacker had already extracted the NTLM hash of a Domain Admin from the memory of the workstation using Mimikatz. They intended to use this access to execute a DCShadow attack, modifying the SID History of a low-privileged decoy account to grant it Domain Admin privileges invisibly.

**The Execution**
1.  **Preparation (Terminal 1 - SYSTEM):** The attacker escalated to `NT AUTHORITY\SYSTEM` on the compromised workstation. They launched Mimikatz and staged the DCShadow payload. This payload instructed the rogue DC to add the Enterprise Admins SID to the `SIDHistory` attribute of a standard user.
    `lsadump::dcshadow /object:svc_backup_temp /attribute:SIDHistory /value:S-1-5-21-XXX-519`
    Mimikatz started the local RPC server and waited.
2.  **Triggering (Terminal 2 - Domain Admin):** In a separate terminal, the attacker used Pass-the-Hash with the compromised DA credentials to launch another Mimikatz instance with domain-wide privileges. They executed the push command to force the primary Domain Controller to replicate from the rogue workstation.
    `lsadump::dcshadow /push`
3.  **The Outcome:** The primary Domain Controller connected to the RPC server running on the workstation and pulled the injected AD configuration. The `svc_backup_temp` account now had Enterprise Admin privileges via SID History. Because the change occurred via the replication stream, no standard user management event logs were generated, allowing the persistent backdoor to remain completely undetected.

## 7. Chaining Opportunities
- **[[15 - DCSync Attack]]:** The natural counterpart. Pull data with DCSync, manipulate it, and push it back with DCShadow.
- **[[17 - ACL Abuse]]:** Use DCShadow to invisibly inject malicious ACEs into the DACLs of critical objects (like the domain root or AdminSDHolder).
- **Golden Ticket / SID History:** DCShadow is heavily used to stealthily inject SID History attributes to grant DA rights to low-privileged accounts across forest trusts.

## 8. Related Notes
- [[23 - Active Directory Persistence]]
- [[24 - Cross-Forest Attacks]]
- [[06 - Kerberos Protocol Mechanisms]]

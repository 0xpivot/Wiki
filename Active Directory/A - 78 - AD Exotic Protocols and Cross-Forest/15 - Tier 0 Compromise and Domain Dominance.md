---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.15 Tier 0 Compromise and Domain Dominance"
---

# 78.15 Tier 0 Compromise and Domain Dominance

## Introduction to Tier 0 and Domain Dominance
In the Microsoft Active Directory Administrative Tier Model, **Tier 0** encompasses the identity control plane. This includes Domain Controllers, Active Directory Certificate Services (AD CS), Active Directory Federation Services (AD FS), Microsoft Exchange, virtualization hosts (ESXi/Hyper-V) housing these servers, and any administrative accounts that manage them.
A compromise of a Tier 0 asset is a complete compromise of the domain and the forest.

Once an attacker breaches Tier 0, their primary objective shifts from lateral movement to **Domain Dominance**. Domain Dominance is the art of establishing covert, highly resilient persistence mechanisms deep within the architecture of Active Directory, ensuring the attacker can always regain control, even if their initial access vectors, malware implants, and backdoors are discovered and remediated.

## Advanced Persistence Mechanisms

### 1. DCShadow
DCShadow is a profound attack technique that completely bypasses traditional SIEM and logging telemetry. Instead of using standard administrative tools (like LDAP or ADSI) to modify domain objects, the attacker registers a rogue, attacker-controlled workstation as a temporary Domain Controller within the forest's Configuration partition.
The attacker then pushes malicious Active Directory modifications (such as modifying `AdminSDHolder`, adding SID History to low-privilege accounts, or changing delegation settings) via standard AD Replication protocols (DRS RPC). Because the changes are pushed via replication, they do not generate standard directory modification Event Logs (like Event ID 5136) on the target DCs. 
The rogue DC replicates the data, unregisters itself, and vanishes, leaving the malicious changes embedded in the directory.

### 2. AdminSDHolder and SDProp
`AdminSDHolder` is a special container object in Active Directory used as a security template for protected groups (like Domain Admins, Enterprise Admins). 
A background process called `SDProp` (Security Descriptor Propagator) runs every 60 minutes on the PDC Emulator. It takes the Access Control List (ACL) of the `AdminSDHolder` object and forcibly copies it to all protected objects in the domain.
If an attacker modifies the ACL of the `AdminSDHolder` object to grant a standard user `GenericAll` rights, within an hour, that standard user will have full control over the Domain Admins group. If the Blue Team removes the rogue user from the Domain Admins ACL, `SDProp` will quietly add it back an hour later.

### 3. Skeleton Key
Skeleton Key is an in-memory malware implant that targets the Local Security Authority Subsystem Service (LSASS) on a Domain Controller. 
When injected, it patches the cryptography and authentication validation routines. It allows all legitimate users to continue logging in with their normal passwords, but it also accepts a "master password" (the Skeleton Key) for *any* account. The attacker can then authenticate as any Domain Admin or CEO using the Skeleton Key without knowing their real password.

### 4. DSRM Password Sync and Persistence
Directory Services Restore Mode (DSRM) is a special boot mode for repairing AD databases. Every DC has a local Administrator account specifically for DSRM, with a password set during promotion. 
By modifying a specific registry key (`DsrmAdminLogonBehavior = 2`), an attacker can allow the DSRM Administrator account to log in over the network. They can then use Pass-The-Hash with the DSRM NTLM hash to access the DC at any time. Furthermore, the attacker can synchronize the DSRM password with a known domain account, ensuring they always have the backdoor credential.

## ASCII Diagram: DCShadow Attack Flow

```text
  [Attacker Workstation / Rogue DC]                    [Primary Domain Controller (PDC)]
             |                                                      |
             |-- 1. Attacker obtains DA Privileges ---------------->|
             |                                                      |
             |-- 2. Modify Configuration Partition ---------------->|
             |      (Register Workstation as a valid DC object)     |
             |                                                      |
             |<-- 3. AD acknowledges new "Domain Controller" -------|
             |                                                      |
             |=== 4. Prepare Malicious Payload Locally ===          |
             |    - Inject SID History into standard user           |
             |    - Modify AdminSDHolder ACLs                       |
             |                                                      |
             |-- 5. Force DRS Replication (Push) ------------------>|
             |      (Bypassing standard LDAP audit logs)            |
             |                                                      |
             |<-- 6. PDC accepts replicated changes ----------------|
             |                                                      |
             |-- 7. Remove Rogue DC from Configuration Partition -->|
             |      (Clean up and vanish)                           |
```

## Step-by-Step Execution Mechanics

### Phase 1: DCShadow Execution using Mimikatz
This requires two command-prompt windows. One runs as SYSTEM to act as the RPC server, the other runs as Domain Admin to trigger the replication.
```powershell
# Window 1 (Running as SYSTEM on attacker machine):
# Prepare the rogue replication payload to modify a user's description
mimikatz # lsadump::dcshadow /object:CN=TargetUser,CN=Users,DC=corp,DC=local /attribute:description /value:"Backdoored via DCShadow"

# Window 2 (Running as Domain Admin):
# Trigger the PDC to pull the replication from our rogue DC
mimikatz # lsadump::dcshadow /push
```

### Phase 2: DSRM Network Logon Enablement
To persist using the DSRM account across network interfaces.
```powershell
# Connect to the Domain Controller via WinRM / WMI
# Modify the registry key to allow network logons
reg add "HKLM\System\CurrentControlSet\Control\Lsa" /v DsrmAdminLogonBehavior /t REG_DWORD /d 2 /f

# Sync the DSRM password to a known, compromised account hash
ntdsutil
"set dsrm password"
"sync from domain account svc_backup"
"q"
"q"
```

### Phase 3: Custom Security Support Providers (SSP)
An attacker can write a custom `.dll` that acts as a Security Support Provider. Once registered in the `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa\Security Packages` registry key, LSASS will load the DLL upon reboot. 
The custom SSP intercepts all cleartext passwords as users authenticate to the DC, logging them to a hidden file (`C:\Windows\System32\memssp.log`) or exfiltrating them directly.

## Indicators of Compromise (IoCs) and Telemetry
1. **DCShadow Anomalies:** Event ID 4662 indicating an object creation in the `CN=Configuration` container, specifically the creation of `server` and `nTDSDSA` objects by non-DC computer accounts, followed rapidly by their deletion.
2. **AdminSDHolder Modifications:** Event ID 5136 showing ACL modifications on `CN=AdminSDHolder,CN=System,DC=...`
3. **Registry Auditing:** Changes to `HKLM\System\CurrentControlSet\Control\Lsa\DsrmAdminLogonBehavior` or the addition of unknown DLLs to the `Security Packages` registry value.
4. **Skeleton Key Memory Signatures:** Modern EDR platforms detect Skeleton Key by scanning LSASS memory for specific API hooking patterns (e.g., hooks on `CDLocateCSystem` and `SamIRetrievePrimaryCredentials`).

## Defensive Mitigations and Engineering
1. **ESAE (Red Forest) / Tiering Model:** The ultimate defense against Domain Dominance is to ensure Tier 0 is logically and physically separated from the rest of the network. Only dedicated Privileged Access Workstations (PAWs) should be able to communicate with Tier 0 assets.
2. **LAPS and Credential Guard:** Enforce Windows Defender Credential Guard to protect LSASS from in-memory patching (Skeleton Key) and deploy LAPS to prevent lateral movement via local administrator accounts.
3. **Advanced Identity Threat Detection (ITDR):** Implement tools like Microsoft Defender for Identity (MDI) which possess specific heuristics and sensors designed to catch DCShadow registrations and anomalous replication behaviors.
4. **Regular SDProp Auditing:** Continuously monitor the `AdminSDHolder` ACL and the membership of high-privileged groups to ensure SDProp is not propagating malicious permissions.

## Chaining Opportunities
- Achieving Tier 0 dominance allows for the execution of massive, forest-wide attacks such as [[11 - Forging Ticket Granting Tickets TGTs]] (Golden Tickets) and [[12 - Advanced Golden SAML Attacks]].
- Backdoors established here can be utilized long after vulnerabilities in [[14 - SCCM and WSUS Exploitation in AD]] have been patched.

## Related Notes
- [[11 - Forging Ticket Granting Tickets TGTs]]
- [[12 - Advanced Golden SAML Attacks]]
- [[14 - SCCM and WSUS Exploitation in AD]]

---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.07 Access Control Lists ACLs and ACEs"
---

# Access Control Lists (ACLs) and Access Control Entries (ACEs)

## 1. Introduction to AD Access Control

In Active Directory, every object (users, computers, groups, OUs, GPOs) is protected by a security mechanism that dictates exactly who can view, modify, or interact with that object. This mechanism is primarily governed by Access Control Lists (ACLs).

While we often think of permissions in the context of NTFS file systems, Active Directory has its own highly granular, directory-level permission model. Understanding how to enumerate, analyze, and abuse AD ACLs is one of the most critical skills for modern AD penetration testing and red teaming.

## 2. The Security Descriptor

Every object in Active Directory is assigned a **Security Descriptor**. The Security Descriptor is a data structure that contains the security information associated with the object. It consists of four main components:

1. **Owner SID**: The Security Identifier (SID) of the user or group that owns the object. The owner can always change the permissions on the object, regardless of what the DACL currently says.
2. **Primary Group SID**: Used primarily for POSIX compliance; rarely relevant in standard Windows security.
3. **Discretionary Access Control List (DACL)**: The list that explicitly defines *who* has *what* type of access to the object.
4. **System Access Control List (SACL)**: The list used for auditing. It defines which access attempts (success or failure) should be logged to the Windows Event Log.

## 3. Architecture Visualization

```text
+-----------------------------------------------------------------------+
|                     Active Directory Object (e.g., User: Bob)         |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |                    SECURITY DESCRIPTOR                          |  |
|  |                                                                 |  |
|  |  +-----------------------------------------------------------+  |  |
|  |  | Owner: S-1-5-21-...-500 (Domain Admins)                   |  |  |
|  |  +-----------------------------------------------------------+  |  |
|  |                                                                 |  |
|  |  +-----------------------------------------------------------+  |  |
|  |  | DACL (Discretionary Access Control List)                  |  |  |
|  |  |                                                           |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  |  | ACE 1: DENY - Eve - WriteProperty                   |  |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  |  | ACE 2: ALLOW - Alice - GenericAll (Full Control)    |  |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  |  | ACE 3: ALLOW - HelpDesk Group - ForceChangePassword |  |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  +-----------------------------------------------------------+  |  |
|  |                                                                 |  |
|  |  +-----------------------------------------------------------+  |  |
|  |  | SACL (System Access Control List)                         |  |  |
|  |  |                                                           |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  |  | ACE 1: AUDIT (Success/Fail) - Everyone - Write      |  |  |  |
|  |  |  +-----------------------------------------------------+  |  |  |
|  |  +-----------------------------------------------------------+  |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

## 4. Access Control Entries (ACEs)

An ACL is simply a container. The actual rules are called **Access Control Entries (ACEs)**. Each ACE contains:
- **Principal**: Who the rule applies to (represented by a SID).
- **Type**: Whether the access is `Allow` or `Deny`.
- **Rights**: The specific actions permitted or denied (e.g., `Read`, `Write`, `GenericAll`).
- **Inheritance Flags**: Whether this ACE should flow down to child objects.

### 4.1 ACE Evaluation Rules
When Windows evaluates access to an object, it reads the DACL sequentially based on a strict order:
1. **Explicit Deny** ACEs are evaluated first.
2. **Explicit Allow** ACEs are evaluated next.
3. **Inherited Deny** ACEs.
4. **Inherited Allow** ACEs.

If a matching Allow ACE is found granting the requested access, access is granted. If a Deny ACE matches, access is immediately blocked. If the end of the DACL is reached and no ACE explicitly grants access, the request is **Implicitly Denied**.

## 5. Security Identifiers (SIDs)

Permissions are not mapped to usernames; they are mapped to SIDs. A SID is a unique, immutable string assigned to an account or group when it is created.
Format: `S-1-5-21-<Domain-Identifier>-<Relative-ID (RID)>`
- `S-1-5`: Specifies the NT Authority.
- `21-<Domain-Identifier>`: The unique identifier for the specific AD domain.
- `RID`: The specific account ID. For example, `500` is always the built-in Administrator, and `512` is always Domain Admins.

## 6. Interesting AD Permissions from an Offensive Perspective

Certain ACEs grant a principal significant power over an object. Identifying these permissions is the core of AD lateral movement and privilege escalation.

### 6.1 GenericAll
- **What it is**: Absolute full control over the object.
- **Abuse**: If you have `GenericAll` over a user, you can reset their password, alter their SPNs, or add them to groups. If you have it over a group, you can add yourself to that group.

### 6.2 GenericWrite
- **What it is**: The ability to write to any non-protected property of the object.
- **Abuse**: Allows an attacker to modify the `scriptPath` (to run a payload on logon) or modify `msDS-AllowedToActOnBehalfOfOtherIdentity` to perform Resource-Based Constrained Delegation (RBCD) attacks.

### 6.3 WriteDacl
- **What it is**: The ability to modify the DACL of the object.
- **Abuse**: An attacker can rewrite the DACL to grant themselves `GenericAll`, effectively taking full control of the object.

### 6.4 WriteOwner
- **What it is**: The ability to change the owner of the object.
- **Abuse**: An attacker can change the owner to themselves. Since the owner can modify the DACL, the attacker can then grant themselves `GenericAll`.

### 6.5 Extended Rights (e.g., ForceChangePassword, AddMembers)
Active Directory utilizes "Extended Rights" for directory-specific actions.
- **User-Force-Change-Password**: Allows resetting a user's password without knowing their current one.
- **Self-Membership (AddMembers)**: Allows a principal to arbitrarily add members to a specific security group.

### 6.6 Directory Replication (DCSync)
- **What it is**: The `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` permissions.
- **Abuse**: These permissions belong at the domain root. If an attacker possesses them, they can execute a DCSync attack, simulating a Domain Controller to request password hashes (including the `krbtgt` hash) directly from the primary DC via the MS-DRSR protocol.

## 7. Offensive Perspective: Enumerating ACLs

Manually reading AD ACLs is tedious and visually confusing due to the SDDL (Security Descriptor Definition Language) format. Attackers use automated tools to parse these relationships.

- **BloodHound**: The premier tool for ACL enumeration. Tools like SharpHound automatically pull all DACLs, translate the SIDs, and map them into a Neo4j graph database. This allows attackers to see hidden paths to Domain Admin (e.g., User A can modify Group B, which has GenericAll over User C, who is a Domain Admin).
- **PowerView**: Excellent for targeted queries.
  ```powershell
  # Find objects where a specific user has dangerous rights
  Get-DomainObjectAcl -ResolveGUIDs | Where-Object { $_.SecurityIdentifier -eq 'S-1-5-21-...-1001' }
  ```

## 8. AD Defense Mechanisms

### 8.1 AdminSDHolder and SDProp
To protect highly privileged groups (like Domain Admins, Enterprise Admins), AD uses a mechanism called **AdminSDHolder**. 
A background process called **SDProp** runs every 60 minutes. It takes the ACL defined on the `CN=AdminSDHolder,CN=System,DC=domain,DC=com` object and forcefully overwrites the ACLs of all protected administrative users and groups.
**Offensive abuse**: If an attacker gains Domain Admin, they can add an ACE to the AdminSDHolder object granting their backdoor user `GenericAll`. SDProp will then automatically push this backdoor permission to all Domain Admins, acting as an incredibly persistent backdoor.

## 9. Remediation and Hardening

- **Audit Delegation**: Organizations often delegate rights to helpdesk teams (e.g., "reset passwords"). If done at a high-level OU, this can inadvertently grant helpdesk users control over server admin accounts. Use strict, compartmentalized OUs.
- **Remove Orphaned ACEs**: Remove ACEs pointing to unresolved SIDs (SIDs belonging to deleted objects) to keep the DACL clean and prevent SID-history attacks.
- **Monitor ACL Modifications**: Enable SACL auditing on critical objects (like Domain Admins and AdminSDHolder) and alert on Event IDs **5136** (Object Modified) and **4670** (Permissions Changed).

## Real-World Attack Scenario

**The Context:** An attacker has temporarily gained Domain Admin credentials during an engagement. Before the Blue Team detects the breach and resets the compromised Domain Admin's password, the attacker needs to establish deeply hidden, persistent access to the domain's most privileged groups.

**The Thought Process:** Standard persistence methods, like adding a new user to the Domain Admins group, are noisy and immediately flagged by SIEM rules. Instead, the attacker targets the `AdminSDHolder` object. Since the `SDProp` process automatically stamps the ACL of `AdminSDHolder` onto every highly privileged user and group in the domain every 60 minutes, modifying this single object will implicitly backdoor all Tier 0 assets.

**The Execution:**
1. **The Setup:** The attacker creates a completely standard, innocuous-sounding domain user account named `svc_metrics_monitor` and hides it in a generic OU.
2. **The Backdoor:** Using `PowerView`, the attacker modifies the DACL of the `AdminSDHolder` container, explicitly granting `GenericAll` (Full Control) rights to the newly created `svc_metrics_monitor` account.
   `Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=corp,DC=local" -PrincipalIdentity svc_metrics_monitor -Rights All`
3. **The Wait:** The attacker waits up to 60 minutes for the `SDProp` process to run. Once it executes, it automatically applies the `GenericAll` ACE for `svc_metrics_monitor` onto the Domain Admins group, Enterprise Admins group, and all individual Domain Admin accounts.
4. **The Exploitation:** Days later, after the initial breach is remediated and passwords are changed, the attacker returns using the `svc_metrics_monitor` credentials. Because they now have `GenericAll` over the Domain Admins group, they use a simple LDAP call to add themselves directly to the group.

**The Outcome:** The attacker successfully maintained undetectable persistence. Even if defenders manually removed the `svc_metrics_monitor` account from the Domain Admins group, the `SDProp` process would continually restore the backdoor ACL every hour until the `AdminSDHolder` object itself was cleaned.

## 10. Chaining Opportunities

- **BloodHound -> RBCD**: Discover a `GenericWrite` ACL over a target server via BloodHound, and chain it with a compromised machine account to execute Resource-Based Constrained Delegation (RBCD) and gain remote code execution as SYSTEM on the server.
- **WriteDacl -> DCSync**: Abuse `WriteDacl` on the Domain root object to grant yourself `DS-Replication-Get-Changes-All`, followed immediately by `secretsdump.py` to dump the NTDS.dit.

## 11. Related Notes

- [[06 - Group Policy Objects GPOs Explained]]
- [[09 - Service Principal Names SPNs and Delegation]]
- [[01 - Active Directory Structure and Components]]

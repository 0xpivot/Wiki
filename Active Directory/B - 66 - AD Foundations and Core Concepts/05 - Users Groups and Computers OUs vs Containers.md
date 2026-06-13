---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.05 Users, Groups, and Computers OUs vs Containers"
---

# Security Principals, Groups, and Organizational Units

Active Directory is essentially a highly structured database used to manage identities and apply security policies. To effectively manipulate or secure an AD environment, one must understand how identities (Security Principals) are categorized, how they are grouped together to grant permissions, and how their physical location within the Directory Information Tree (DIT) dictates the policies applied to them.

For a penetration tester, distinguishing between a default Container and an Organizational Unit (OU), or understanding the difference between a Domain Local group and a Global group, is the difference between blindly attempting exploits and surgically mapping a path to domain dominance.

## Security Principals

A Security Principal is any entity in Active Directory that can be authenticated by the operating system and can be assigned permissions to resources. Every security principal is assigned a unique Security Identifier (SID).

1. **User Accounts:** Represent individuals. They are assigned passwords, login restrictions, and interactive logon rights.
2. **Computer Accounts:** Yes, computers are identities too! When a machine is joined to a domain, a computer account (e.g., `DESKTOP-01$`) is created. The computer maintains its own password, which it negotiates with the Domain Controller automatically (typically every 30 days). Computer accounts are used to authenticate the machine itself to the domain to apply Group Policy.
3. **Managed Service Accounts (MSAs / gMSAs):** Designed specifically for running automated services. Unlike standard user accounts configured as service accounts (which suffer from static, rarely changed passwords), gMSAs automatically cycle their complex, 120-character passwords, making them immune to traditional Kerberoasting if properly implemented.

## ASCII Diagram: Groups vs OUs and GPO Linkage

```text
=============================================================================
                  ORGANIZATIONAL UNITS vs CONTAINERS 
=============================================================================

                          [ DOMAIN: corp.local ] <==== [ GPO: Default Domain Policy ]
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
  [ CN=Users ]                 [ CN=Computers ]          [ OU=Workstations ] <== [ GPO: Enforce AppLocker ]
 (Default Container)          (Default Container)        (Organizational Unit)
          |                         |                         |
    [ CN=Bob ]                 [ CN=Win10-Old ]          +----+----+
    [ CN=Domain Admins ]                                 |         |
                                                   [ CN=Win10-A ] [ CN=Win10-B ]

* NOTE: Containers (CN=) CANNOT have Group Policies applied directly to them.
* NOTE: OUs (OU=) CAN have Group Policies applied to them.
```

## Groups and Group Scoping

To efficiently manage permissions across thousands of users, administrators use Groups. Instead of applying access control lists (ACLs) to individual users, ACLs are applied to groups, and users are placed into those groups. Active Directory features three primary group scopes:

1. **Domain Local Groups:**
   - **Purpose:** Used to assign permissions to resources (like a file share or a printer) located *within the same domain* where the group was created.
   - **Membership:** Can contain users, global groups, and universal groups from *any* domain in the forest or trusted external domains.
   
2. **Global Groups:**
   - **Purpose:** Used to group users based on their business role (e.g., "HR Department", "Helpdesk"). 
   - **Membership:** Can ONLY contain users and other global groups from the *same domain* where the global group was created.
   
3. **Universal Groups:**
   - **Purpose:** Used to consolidate groups that span multiple domains. They are heavily utilized in multi-domain forests.
   - **Membership:** Can contain users and global groups from *any domain* in the forest. Universal group memberships are stored in the Global Catalog (GC), meaning changes to them replicate across the entire forest.

### The AGDLP / AGUDLP Strategy
Microsoft recommends a specific nesting strategy for granting permissions, known as AGDLP (Account, Global, Domain Local, Permission):
- **A**ccounts are placed into...
- **G**lobal groups, which are placed into...
- **D**omain **L**ocal groups, which are granted...
- **P**ermissions to resources.

## High-Value Default Groups

When AD is installed, several high-value built-in groups are created. Attackers target these groups to achieve privilege escalation.
- **Domain Admins:** Has full control over the domain. Members are automatically added to the local Administrators group of every domain-joined Windows machine.
- **Enterprise Admins:** Exists only in the forest root domain. Has full control over the entire forest and every domain within it.
- **Administrators (Builtin):** The local administrators group for the Domain Controllers themselves.
- **Backup Operators:** Can bypass file system permissions to back up files. Attackers abuse this to extract the `NTDS.dit` database from a DC.
- **DnsAdmins:** Can manage DNS, heavily abused to execute code as SYSTEM on DCs.

## OUs vs Containers (The Critical Difference)

From a structural perspective, both Organizational Units (OUs) and Containers hold objects. However, operationally, they are fundamentally different.

### Default Containers
When a domain is created, standard containers are generated automatically. The path uses `CN=` (Common Name).
- `CN=Users`: The default location where newly created users and built-in groups (like Domain Admins) are placed.
- `CN=Computers`: The default location for newly joined computer accounts.
- **CRITICAL FLAW:** You **cannot** link a Group Policy Object (GPO) directly to a Container. If an administrator leaves users or computers in the default containers, they can only be managed by GPOs linked at the domain root, which applies to everything. This often leads to poor security posture.

### Organizational Units (OUs)
OUs are administrative structures created by domain administrators to mirror business logic (e.g., `OU=Servers`, `OU=Sales`, `OU=Disabled Accounts`). The path uses `OU=`.
- **GPO Linkage:** OUs are specifically designed to have Group Policy Objects linked to them. You can link a GPO that restricts USB drives directly to the `OU=Workstations` without affecting the servers.
- **Delegation of Control:** OUs allow for granular delegation. An administrator can grant the "Helpdesk" group the right to reset passwords *only* for users located inside `OU=Sales`, preventing the Helpdesk from resetting the Domain Admin passwords located in another OU.

## Exploiting ACLs and Delegation

Security Principals and OUs are governed by Access Control Entries (ACEs) within an Access Control List (ACL). In mature AD environments, attackers often find that standard misconfigurations (like Kerberoasting) are patched. Instead, they pivot to **ACL Abuse**.

By mapping the directory with BloodHound, an attacker might discover that a standard user account has `GenericAll` or `ForceChangePassword` rights over a Global Group that is a member of the Domain Admins. Or, they may find they have `WriteDacl` permissions over an OU, allowing them to rewrite the security permissions of all objects within that OU, granting themselves DCSync rights.

## Real-World Attack Scenario

**The Context:** An attacker holds the credentials of a standard user (`h.granger`) in the IT department. The goal is to gain administrative access to the highly restricted "Tier 0" infrastructure, but the path is hidden behind complex group nesting.

**The Thought Process:** Direct attacks against Domain Admins are heavily monitored. Instead, the attacker looks for obscure Access Control List (ACL) configurations. By mapping the environment, they discover that `h.granger` is a member of the global group `IT_Support`. Through a misconfiguration, `IT_Support` has `WriteDacl` permissions over the `OU=ServiceAccounts`. Inside this OU is a service account that is nested deeply inside a Domain Local group, which ultimately has administrative access to a critical server.

**The Execution:**
1. **BloodHound Recon:** The attacker runs SharpHound and ingests the data into BloodHound. The query "Shortest Path to High Value Targets" reveals the complex chain.
2. **ACL Modification:** Since `h.granger` has `WriteDacl` on the `OU=ServiceAccounts`, the attacker uses `PowerView` to grant themselves `GenericAll` over the target `svc_deploy` account located inside that OU.
   `Add-DomainObjectAcl -TargetIdentity "svc_deploy" -PrincipalIdentity "h.granger" -Rights All`
3. **Password Reset:** Now possessing full control over the service account, the attacker forcefully resets its password.
   `Set-DomainUserPassword -Identity svc_deploy -AccountPassword (ConvertTo-SecureString "P@ssw0rd123!" -AsPlainText -Force)`
4. **The Pivot:** The attacker requests a Kerberos TGT for `svc_deploy`. Because `svc_deploy` is nested inside `Global_Infra_Admins`, which is inside `Local_Server_Admins`, the attacker now holds administrative rights over the domain's primary deployment server.

**The Outcome:** By exploiting a seemingly low-level `WriteDacl` permission on an Organizational Unit, the attacker hijacked a service account and leveraged complex AGDLP group nesting. This allowed them to pivot stealthily into the server infrastructure without ever directly interacting with the heavily monitored Domain Admins group.

## Chaining Opportunities

- **Default Container Hijacking:** Because newly joined computers drop into `CN=Computers` by default, an attacker controlling a machine account might poison the default domain policy or execute a Resource-Based Constrained Delegation (RBCD) attack against newly joined machines before they are securely moved to a hardened OU.
- **Nested Group Escalation:** Instead of targeting the `Domain Admins` group directly (which triggers alerts), an attacker targets a seemingly benign Global Group that, through multiple layers of Universal and Domain Local nesting (AGDLP), ultimately grants administrative access to a critical file server holding sensitive scripts.

## Related Notes
- [[01 - What is Active Directory Domains Trees and Forests]]
- [[02 - Understanding FSMO Roles and Domain Controllers]]
- [[04 - LDAP Structure and Querying Basics]]

---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.06 Group Policy Objects GPOs Explained"
---

# Group Policy Objects (GPOs) Explained

## 1. Introduction to Group Policy

Group Policy is a hierarchical administrative framework that allows a network administrator in charge of Microsoft's Active Directory to implement specific configurations for users and computers. It is primarily a management and security tool used to apply settings seamlessly across an enterprise.

Administrators use Group Policy Objects (GPOs) to centrally manage and configure operating systems, applications, and user settings. A GPO is a logical collection of policy settings that defines what a system will look like and how it will behave for a defined group of users or computers.

In a large-scale enterprise environment, managing individual machines manually is impossible. GPOs provide the scale required to uniformly apply password policies, disable legacy and insecure protocols (like SMBv1 or LLMNR), map network drives, push certificates, and distribute software across tens of thousands of endpoints simultaneously.

## 2. Core Components of a GPO

A Group Policy Object is not a single file, database, or setting. It is a logical entity composed of two distinct components stored in completely different locations within the Active Directory architecture.

### 2.1 Group Policy Container (GPC)

The Group Policy Container (GPC) is an Active Directory LDAP object stored in the domain-naming context. 
- **Purpose**: It contains the structural properties of the GPO, such as version information, GPO status, and a list of components that have settings configured. 
- **Function**: The GPC provides the logical link between Active Directory Organizational Units (OUs) and the actual files that store the configuration settings. 
- **Location**: It resides within the LDAP path: `CN=Policies,CN=System,DC=domain,DC=com`.

### 2.2 Group Policy Template (GPT)

The Group Policy Template (GPT) is a collection of folders and files stored in the file system of Domain Controllers.
- **Purpose**: Unlike the GPC which is an LDAP directory object, the GPT contains the actual policy data (registry settings, startup scripts, security settings, software installation files).
- **Function**: This is where the client computer actually downloads the settings it needs to apply.
- **Location**: It resides within the SYSVOL SMB share: `\\domain.com\SYSVOL\domain.com\Policies\{GPO_GUID}`.
- **Replication**: The SYSVOL share is replicated across all Domain Controllers in the domain using DFS-R (Distributed File System Replication).

## 3. Architecture Visualization

```text
+-------------------------------------------------------------+
|                     Domain Controller                       |
|                                                             |
|  +-----------------------+        +----------------------+  |
|  |   Active Directory    |        |     SYSVOL Share     |  |
|  |        (LDAP)         |        |        (SMB)         |  |
|  |                       |        |                      |  |
|  | +-------------------+ |        | +------------------+ |  |
|  | |        GPC        | |        | |       GPT        | |  |
|  | | CN=Policies...    | |        | | \\SYSVOL\...\    | |  |
|  | | Contains:         | |(Links) | | Contains:        | |  |
|  | | - GUID            | |------->| | - Registry.pol   | |  |
|  | | - Version         | |        | | - Scripts        | |  |
|  | | - Link details    | |        | | - Security info  | |  |
|  | +-------------------+ |        | +------------------+ |  |
|  +-----------------------+        +----------------------+  |
+-------------------------------------------------------------+
             |                                  |
             | 1. LDAP Query                    | 2. SMB Fetch
             |    (Discovers linked GPOs)       |    (Downloads policy files)
             v                                  v
+-------------------------------------------------------------+
|                       Target Client                         |
|                                                             |
|  +-------------------------------------------------------+  |
|  |             Core Group Policy Engine                  |  |
|  +-------------------------------------------------------+  |
|                                                             |
|  +-------------------------------------------------------+  |
|  |             Client-Side Extensions (CSEs)             |  |
|  |  [Registry]  [Security]  [Scripts]  [Folder Redir.]   |  |
|  +-------------------------------------------------------+  |
|                                                             |
|  3. Applies Settings to Windows Registry and OS core        |
+-------------------------------------------------------------+
```

## 4. The Application Hierarchy (LSDOU)

GPOs are applied in a highly specific, hierarchical order. This order dictates how conflicting settings are resolved when multiple GPOs apply to the same machine or user. The acronym to remember is **LSDOU**:

1. **L**ocal Group Policy: Settings applied directly on the local machine via `gpedit.msc`. Every Windows computer has exactly one Local GPO.
2. **S**ite GPOs: GPOs linked to an Active Directory Site (physical network locations).
3. **D**omain GPOs: GPOs linked to the Domain root. These apply to everything in the domain.
4. **O**rganizational **U**nit (OU) GPOs: GPOs linked to specific OUs, nested as deep as the AD structure goes.

**Rule of Thumb**: When multiple policies are applied, the *last policy applied wins*. Therefore, an OU policy generally overrides a Domain policy, which overrides a Site policy, which overrides a Local policy. This allows granular, specific configurations to supersede broad, general ones.

### 4.1 Inheritance and Enforcement

By default, policy settings flow down the AD hierarchy. However, administrators can manipulate this:
- **Block Inheritance**: An administrator can configure an OU to block settings flowing from higher-level containers (like the Domain root).
- **Enforced (No Override)**: A GPO can be marked as "Enforced". This means its settings cannot be overridden by lower-level GPOs, and it bypasses any "Block Inheritance" settings. (Often used for critical security baselines).

## 5. Security Filtering and WMI Filtering

Simply linking a GPO to an OU does not automatically mean every object inside that OU will apply the policy. Administrators use filtering mechanisms for precise targeting.

### 5.1 Security Filtering

Security Filtering restricts the application of a GPO based on AD security groups.
- By default, newly created GPOs have the **"Authenticated Users"** group in their Security Filtering scope. This group implicitly includes all user and computer accounts.
- By removing "Authenticated Users" and adding specific security groups (e.g., "HR_Laptops"), the GPO only applies to members of that group.
- **Technical Requirement**: For a GPO to apply to an object, that object must have both the `Read` and `Apply Group Policy` ACL permissions on the GPO's directory object.

### 5.2 WMI Filtering

WMI (Windows Management Instrumentation) filters allow GPOs to be evaluated dynamically based on the target machine's hardware, software, or OS attributes. 
The GPO will only apply if the WMI query returns true.

Example WMI query to apply a policy only to Windows 10 machines:
```sql
SELECT * FROM Win32_OperatingSystem WHERE Version like "10.%"
```

## 6. Client-Side Extensions (CSEs)

GPOs do not inherently "do" anything on their own. Instead, the Windows client Operating System relies on Client-Side Extensions (CSEs). CSEs are specific DLL files registered on the client that are responsible for interpreting the GPT files and executing the actual configuration changes.

When a computer updates its Group Policy, the core engine reads the GPC to see which CSEs are required, then triggers them.
Common CSEs include:
- **Registry Extension**: Reads `registry.pol` and applies registry keys.
- **Security Extension**: Applies user rights assignments, audit policies, and local group memberships.
- **Scripts Extension**: Configures and executes startup, shutdown, logon, and logoff scripts.

## 7. Group Policy Refresh Cycle

Group policy does not update instantly. Clients periodically poll the Domain Controller for updates.
- **Default Refresh Interval**: For standard workstations and member servers, the refresh interval is **90 minutes**, with a randomized offset of up to **30 minutes** to prevent network storms.
- **Domain Controllers**: DCs update their own policy every **5 minutes**.
- **Manual Refresh**: Administrators or attackers can force an immediate refresh on a client using the `gpupdate /force` command.

## 8. Group Policy Preferences (GPP) and the cPassword Flaw

Group Policy Preferences (GPP) were introduced to allow administrators to deploy configurations that users could later modify (unlike standard policies which are strictly enforced).

Historically, administrators heavily used GPP to push local administrator passwords or map network drives with specific credentials. These passwords were encrypted using AES-256 within the SYSVOL XML files. 
However, Microsoft accidentally published the private AES decryption key on MSDN.

This catastrophic flaw allowed any domain user to read the `Groups.xml` or `Drives.xml` files from SYSVOL, extract the `cPassword` attribute, and instantly decrypt it using the public key. This often led to immediate domain-wide privilege escalation. While Microsoft released MS14-025 to stop new passwords from being set this way, legacy XML files are still frequently found during VAPT engagements.

## 9. Offensive Perspective: Enumerating GPOs

From an attacker's perspective, GPOs are an incredible source of intelligence and a prime target for lateral movement.

### 9.1 Enumeration Tools
- **PowerView**: Can be used to map out policies and who controls them.
  ```powershell
  Get-DomainGPO -Properties DisplayName, Name
  Get-DomainGPOUserLocalGroupMapping
  ```
- **BloodHound**: The `GpoAddLocalAdmin` and `GenericAll` edges originating from GPOs reveal exactly how policies dictate administrative rights across the environment.
- **Manual SYSVOL Search**: Attackers routinely search SYSVOL for scripts, configuration files, and hardcoded credentials because every domain user has read access.

## 10. Offensive Perspective: Abusing GPOs

If an attacker compromises an account that has `WriteProperty` or `GenericAll` over a GPO (or over an OU to which they can link a new GPO), they can weaponize the policy infrastructure.

### 10.1 Common Abuse Vectors
- **Malicious Scheduled Tasks**: Modifying a GPO to deploy a scheduled task that executes a C2 beacon on all computers in the targeted OU.
- **Startup Scripts**: Dropping a PowerShell reverse shell into the GPO's logon script directory.
- **Local Group Modification**: Using the Restricted Groups CSE to add a compromised low-privileged domain user into the local `Administrators` group of every machine.
- **Ransomware Deployment**: APT groups and ransomware operators almost exclusively use compromised GPOs to deploy their encryptors to the entire network simultaneously, maximizing impact before defenders can react.

## 11. Remediation and Hardening

- **Implement Tiered Administration**: Only highly trusted Tier 0 accounts (Domain Admins) should have modification rights over critical GPOs (like the Default Domain Policy).
- **Audit Delegation**: Regularly review the ACLs on GPO objects in AD. Remove standard users or service accounts that have been improperly delegated modification rights.
- **Monitor Modifications**: Ingest Event ID **5136** (Directory Service object modified) to monitor for unexpected changes to GPOs.
- **SYSVOL Hygiene**: Regularly scan the SYSVOL share to remove legacy scripts containing hardcoded credentials or old GPP files containing `cPassword` attributes.

## 12. Real-World Attack Scenario

**The Context:** An Advanced Persistent Threat (APT) group has compromised an IT Helpdesk administrator's account. They discover that this account has been improperly granted `GenericWrite` permissions over a GPO named `Workstation_Baseline_Sec`, which is linked to the root of the domain and enforced across all client machines.

**The Thought Process:** The APT wants to deploy ransomware simultaneously to thousands of endpoints to maximize disruption before defenders can isolate the network. Instead of manually moving laterally and executing the payload machine-by-machine, they will weaponize the existing Group Policy infrastructure. By modifying the `Workstation_Baseline_Sec` GPO to include a malicious Scheduled Task, the domain controllers themselves will orchestrate the deployment.

**The Execution:**
1. **Payload Staging:** The attacker uploads their ransomware payload (`payload.exe`) to the domain's publicly readable SYSVOL share, knowing all computers can access it without triggering initial EDR alerts on network file transfers.
2. **GPO Weaponization:** Using a tool like `SharpGPOAbuse`, the attacker modifies the vulnerable GPO to create an immediate scheduled task on all targeted systems.
   `SharpGPOAbuse.exe --AddComputerTask --TaskName "WinUpdate" --Author "NT AUTHORITY\System" --Command "\\domain.local\SYSVOL\payload.exe" --GPOName "Workstation_Baseline_Sec"`
3. **Forcing the Update (Optional):** While standard workstations will naturally pull the updated policy within 90-120 minutes, the attacker could use WMI to remotely trigger `gpupdate /force` across the subnet to accelerate the execution.
4. **Execution:** As each client machine polls the DC for policy updates, the core policy engine fetches the modified GPO, reads the Client-Side Extension (CSE) instruction, and executes the ransomware payload as `SYSTEM`.

**The Outcome:** Within two hours, 95% of the organization's workstations concurrently fetch and execute the ransomware payload from the trusted SYSVOL share. The use of GPOs provides the attacker with perfect scaling, utilizing the organization's own management framework to execute a devastating, synchronized attack.

## 13. Chaining Opportunities

- **BloodHound -> GPO Abuse**: Identify a misconfigured ACL granting a developer account `GenericAll` over the "Server Infrastructure" GPO, compromise the developer, and push a malicious task to compromise the servers.
- **GPP Decryption -> Pass-the-Hash**: Find a `cPassword` in SYSVOL, decrypt it, and use the resulting credential to Pass-the-Hash against a Domain Controller if the local admin password was reused.
- **NTLM Relay -> GPO Modification**: Relay a Domain Admin's NTLM authentication to LDAP to modify a GPO if LDAP signing is not enforced.

## 14. Related Notes

- [[07 - Access Control Lists ACLs and Access Control Entries ACEs]]
- [[01 - Active Directory Structure and Components]]
- [[08 - NTLM vs Kerberos Authentication Basics]]

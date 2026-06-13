---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.11 Identifying Local Administrators via RPC"
---

# Identifying Local Administrators via RPC

## 1. Executive Summary & Introduction
Identifying local administrators across an Active Directory (AD) domain is an essential reconnaissance step during a Vulnerability Assessment and Penetration Testing (VAPT) engagement. Attackers seek out machines where they possess local administrator rights or identify users who hold these rights on high-value targets. Remote Procedure Call (RPC) offers a native, authenticated, and often unmonitored method to enumerate local administrators without relying on noisier techniques or deploying specialized agents.

In Windows environments, local administrators have full control over a system. This allows them to dump credentials (e.g., via LSASS memory dumping), install persistence mechanisms (such as scheduled tasks or malicious services), disable security controls (like Windows Defender or EDR solutions), and pivot to other systems within the network. By mapping out who has administrative access to which machines, an attacker can carefully plan a lateral movement path ultimately leading to domain dominance.

RPC, specifically the `MS-SAMR` (Security Account Manager Remote) and `MS-LSAD` (Local Security Authority Translation) protocols, allows a domain user to query remote machines to retrieve local group memberships. The prime target is the built-in `Administrators` group, universally identified by the well-known SID `S-1-5-32-544`. Historically, this enumeration was possible for any authenticated user, though modern Windows versions restrict this by default. Nevertheless, legacy configurations, backwards compatibility requirements, and specific misconfigurations frequently leave this vector open.

## 2. Technical Mechanisms and Protocol Deep Dive
### 2.1 The MS-SAMR Protocol
The Security Account Manager (SAM) Remote Protocol (`MS-SAMR`) is heavily utilized in AD environments for user and group management. It operates over RPC, typically using named pipes over SMB (e.g., `\pipe\samr`). When an attacker attempts to enumerate local administrators, they bind to the `MS-SAMR` interface on the target machine.

The typical API call sequence is:
1. `SamrConnect` or `SamrConnect5`: Establishes a connection to the server's SAM database.
2. `SamrLookupDomainInSamServer`: Resolves the built-in domain name (usually `Builtin`).
3. `SamrOpenDomain`: Opens a handle to the `Builtin` domain.
4. `SamrOpenAlias`: Opens a handle to the `Administrators` alias (RID 544).
5. `SamrGetMembersInAlias`: Retrieves the SIDs of the members within the `Administrators` group.

### 2.2 The MS-LSAD Protocol
Once the SIDs are retrieved via `MS-SAMR`, they are merely numerical identifiers (e.g., `S-1-5-21-123456789-123456789-123456789-1001`). To make this actionable, the attacker must translate these SIDs into human-readable domain accounts. This is where `MS-LSAD` (Local Security Authority Translation) comes in.
The attacker utilizes API calls such as `LsaLookupSids` to resolve the SIDs to account names, mapping out the exact users and groups that have administrative control.

### 2.3 Network Architecture and Port Requirements
To perform RPC enumeration, the attacker requires network line-of-sight to the target systems on the following ports:
- **TCP 445 (SMB)**: Used for RPC over Named Pipes (e.g., `ncacn_np`).
- **TCP 135 (RPC Endpoint Mapper)**: Used for dynamic port allocation if named pipes are not used or blocked.
- **TCP 49152-65535 (High RPC Ports)**: Used when the endpoint mapper directs the client to a dynamically assigned port.

## 3. Visual Attack Flow Diagram
```text
+----------------+                                +--------------------------+
|   Attacker     |                                |      Target Workstation  |
|   (Auth'd)     |                                |      (e.g., WS01)        |
+-------+--------+                                +-------------+------------+
        |                                                       |
        | 1. Connect via SMB (TCP 445)                          |
        |------------------------------------------------------>|
        |                                                       |
        | 2. Bind to MS-SAMR (\pipe\samr)                       |
        |------------------------------------------------------>|
        |                                                       |
        | 3. SamrConnect5 (Handle Request)                      |
        |------------------------------------------------------>|
        |                                                       |
        | 4. SamrOpenAlias (RID 544 - Administrators)           |
        |------------------------------------------------------>|
        |                                                       |
        | 5. SamrGetMembersInAlias (Returns SIDs)               |
        |<------------------------------------------------------|
        |                                                       |
        | 6. Bind to MS-LSAD (\pipe\lsarpc)                     |
        |------------------------------------------------------>|
        |                                                       |
        | 7. LsaLookupSids (Resolve SIDs to Names)              |
        |<------------------------------------------------------|
        |                                                       |
+-------+--------+                                +-------------+------------+
| Output:        |                                | Members of local         |
| Domain\Admin1  |                                | Admin group revealed     |
| Domain\GroupA  |                                | to unprivileged user.    |
+----------------+                                +--------------------------+
```

## 4. Execution and Tooling
Several open-source and native tools facilitate local administrator enumeration via RPC.

### 4.1 NetExec (formerly CrackMapExec)
NetExec is a highly effective tool for parallelizing this check across entire subnets or domains.
```bash
# Enumerate local admins on a single target
nxc smb 192.168.1.100 -u "user" -p "password" -d "domain.local" --local-auth

# Enumerate local admins across a /24 subnet using a domain account
nxc smb 192.168.1.0/24 -u "jsmith" -p "Password123!" -d "domain.local" --local-groups Administrators
```
The output will clearly highlight which machines the account `jsmith` has `Pwn3d!` (administrative access) to, and list the members of the Administrators group.

### 4.2 PowerView (PowerSploit)
PowerView, a PowerShell-based AD enumeration tool, uses native Windows APIs to query this information, blending in with legitimate administrative traffic.
```powershell
# Import PowerView
Import-Module .\PowerView.ps1

# Enumerate local administrators on a specific computer
Get-NetLocalGroupMember -ComputerName WS01.domain.local -GroupName Administrators
```

### 4.3 BloodHound (SharpHound)
BloodHound automates this process globally. When SharpHound runs with the `LocalAdmin` collection method, it attempts to query `MS-SAMR` on all domain-joined computers to build the `AdminTo` edges in the graph database.
```powershell
# Run SharpHound to collect local admin data
Invoke-BloodHound -CollectionMethod LocalGroup
```

### 4.4 Impacket (rpcdump.py and samrdump.py)
Impacket scripts can be used to interact with RPC directly from Linux hosts.
```bash
# Dump SAM database and local groups via SAMR
samrdump.py domain.local/jsmith:Password123!@192.168.1.100
```

## 5. Security Posture and Mitigations
### 5.1 The Evolution of SAMR Restrictions
Historically (Windows 2000/XP/7), any authenticated domain user could query SAMR remotely. Microsoft introduced the Group Policy setting **"Network access: Restrict clients allowed to make remote calls to SAM"** (introduced in Windows 10 Version 1607 and Windows Server 2016).
By default, in modern Windows 10/11 and Server 2016+ deployments, remote SAM querying is restricted to the local `Administrators` group. If a standard user attempts the query, the `SamrConnect` call returns `STATUS_ACCESS_DENIED`.

### 5.2 Hardening Recommendations
To secure environments against RPC enumeration of local administrators:
1. **Enforce SAMR Restrictions**: Ensure the GPO setting `Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> Security Options -> Network access: Restrict clients allowed to make remote calls to SAM` is configured. The recommended SDDL is `O:BAG:BAD:(A;;RC;;;BA)`, which translates to "Allow local Administrators only."
2. **Disable SMBv1**: Ensure legacy SMB is disabled to force more secure communication protocols.
3. **Network Segmentation**: Restrict workstation-to-workstation communication (micro-segmentation) on ports 135 and 445. If workstations cannot communicate with each other over SMB/RPC, lateral movement and enumeration are severely hindered.
4. **LAPS Implementation**: Implement Local Administrator Password Solution (LAPS) to randomize local administrator passwords, mitigating the impact if local admin access is achieved.

## 6. Detection Engineering
Detecting RPC enumeration is notoriously difficult because the protocols used (`MS-SAMR`, `MS-LSAD`) are heavily used for legitimate AD operations, such as Group Policy processing, authentication, and application compatibility.

### 6.1 Event ID 4624 / 4625 (Logon Events)
High volumes of network logons (Logon Type 3) originating from a single source workstation to multiple distinct destinations over a short period indicate potential enumeration scanning (e.g., NetExec behavior).
- **Metric**: Source IP X connects to > 50 unique Destination IPs within 5 minutes.

### 6.2 Event ID 5145 (Detailed Network Share)
When an attacker connects to the `IPC$` share to access named pipes (`\pipe\samr` or `\pipe\lsarpc`), Event ID 5145 is generated.
- **Rule Logic**: Look for `Share Name: \\*\IPC$` combined with `Relative Target Name: samr` or `lsarpc`. Frequency analysis is key here to weed out legitimate noise from domain controllers or vulnerability scanners.

### 6.3 Event ID 16953 (Directory Service)
If SAMR restrictions are enabled, blocked attempts will log an event. Monitoring for denied SAMR calls can act as a high-fidelity alert for reconnaissance activities.

### 6.4 KQL Threat Hunting Query
```kql
// Microsoft Sentinel query for excessive IPC$ connections
SecurityEvent
| where EventID == 5145
| where ShareName endswith "IPC$"
| where RelativeTargetName in~ ("samr", "lsarpc")
| summarize count(), make_set(Computer) by Account, IpAddress
| where count_ > 20
| project Account, IpAddress, TotalConnections=count_, TargetComputers=set_Computer
```

## 7. Operational Nuances in VAPT
During an assessment, an attacker must understand that failure to query SAMR directly does not imply a dead end. In mature environments with restricted SAMR, attackers fall back to:
- **GPO Analysis**: Parsing Group Policy Preference (GPP) or Group Policy objects (e.g., via `Get-GPO` or BloodHound's `GPOAdmin` edges) to infer who is placed in the local Administrators group.
- **Active Directory Delegation**: Checking domain-level ACLs to see who can reset passwords or modify user attributes, circumventing the need for local endpoint administrative rights entirely.

## 8. Real-World Case Study
In a recent incident response engagement, the initial access broker utilized a compromised low-privilege VPN account. Within 15 minutes of connecting, the attacker executed a single `nxc smb` command targeting a /16 subnet to enumerate local administrators. Because the organization had deployed Windows Server 2019 but failed to explicitly configure SAMR restriction GPOs, the attacker successfully identified a forgotten development server where the standard VPN user held local admin rights. This server contained cached credentials for a Domain Administrator, leading to total forest compromise within 4 hours.

## 9. Troubleshooting Enumeration Failures
- **STATUS_ACCESS_DENIED**: The target has SAMR restrictions enabled. The attacker must find another machine, elevate privileges locally, or use a different technique.
- **STATUS_OBJECT_NAME_NOT_FOUND**: The targeted named pipe does not exist. The service might be disabled.
- **RPC_S_SERVER_UNAVAILABLE**: Usually indicates a firewall blocking port 135 or 445, or the target machine is offline.

## 10. Chaining Opportunities
- **[[12 - Password Spraying Basics and Lockout Policies]]**: After identifying local administrators, an attacker might password spray those specific high-privilege accounts.
- **[[05 - BloodHound Data Collection]]**: The data gathered via RPC is directly fed into BloodHound to map out shortest paths to Domain Admin.
- **SMB Relay**: If SMB signing is disabled, an attacker might relay credentials to a machine where the victim is a local admin, bypassing the need to enumerate directly.

## 11. Related Notes
- [[12 - Password Spraying Basics and Lockout Policies]]
- [[13 - AS-REP Roasting Basics and Detection]]
- [[14 - Kerberoasting Basics and Identification]]
- [[15 - LLMNR and NBT-NS Poisoning Basics]]
- [[16 - SMB Relay Attacks]]

## Appendix A: Extended Troubleshooting & Common Error Codes
When executing Active Directory enumeration and exploitation attacks, practitioners frequently encounter a variety of error codes. Understanding these is critical for operational success.

### Kerberos and Authentication Errors
- **KDC_ERR_PREAUTH_REQUIRED (0x11)**: Expected behavior when a user requires pre-authentication. Occurs during normal AS-REQ if `DONT_REQ_PREAUTH` is not set.
- **KDC_ERR_CLIENT_REVOKED (0x12)**: The targeted user account has been disabled or locked out. Attackers should immediately cease spraying or brute-forcing this account to avoid further detection.
- **KDC_ERR_PREAUTH_FAILED (0x18)**: The password provided during pre-authentication was incorrect. This is the primary indicator of a failed password spray attempt.
- **KDC_ERR_ETYPE_NOSUPP (0x0E)**: The requested encryption type is not supported. This often happens if an attacker specifically requests an RC4 ticket but the domain has strictly enforced AES-only communication via GPO.

### SMB and RPC Errors
- **STATUS_LOGON_FAILURE (0xC000006D)**: Invalid credentials provided during an SMB or RPC connection attempt.
- **STATUS_ACCOUNT_LOCKED_OUT (0xC0000234)**: The user account is locked out. This is a critical failure in operational security if triggered inadvertently.
- **STATUS_ACCESS_DENIED (0xC0000022)**: The provided credentials are valid, but the user lacks the necessary authorization to perform the requested action (e.g., querying the SAM database, accessing an administrative share like `C$`).
- **STATUS_PASSWORD_MUST_CHANGE (0xC0000224)**: The password is correct, but the user must change it at next logon. Tools like NetExec can often automatically handle this if specified.

## Appendix B: Advanced Threat Hunting and Detection Playbooks
To build a robust defense-in-depth strategy, organizations must transition from reactive alerting to proactive threat hunting.

### SIEM Integration and Data Sources
Effective detection requires ingesting the following log sources into a centralized SIEM (e.g., Splunk, Microsoft Sentinel, Elastic Security):
1. **Windows Security Event Logs** from all Domain Controllers.
2. **Windows Security Event Logs** from critical tier-0 and tier-1 servers.
3. **Sysmon (System Monitor) Logs** (specifically Event ID 3 for network connections and Event ID 1 for process creation).
4. **Network Traffic Analysis (NTA) / Zeek** logs for identifying anomalous RPC and SMB traffic patterns.

### Developing High-Fidelity Alerts
When creating alerts, focus on combinations of events rather than single occurrences to reduce false positives:
- **Correlated Reconnaissance**: Alert when a single source IP generates Event ID 4624 (Logon) across more than 20 distinct destination IPs within a 15-minute window, followed by Event ID 5145 (Detailed Share) accessing `IPC$`.
- **Honeytoken Triggers**: Any authentication attempt (Event ID 4624) or ticket request (Event ID 4768/4769) against a designated honey account must trigger a critical, paging alert to the SOC immediately. Honeytokens have near-zero false positive rates.

## Appendix C: Glossary of Active Directory Terminology
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket issued by the KDC upon successful initial authentication. It acts as a passport, allowing the user to request access to specific services without re-entering their password.
- **TGS (Ticket Granting Service / Service Ticket)**: A secondary Kerberos ticket requested using the TGT, granting access to a specific service or resource (e.g., CIFS, MSSQLSvc).
- **KDC (Key Distribution Center)**: The Kerberos service running on Domain Controllers responsible for authenticating users and issuing tickets.
- **SPN (Service Principal Name)**: A unique identifier that maps a service instance to a domain account. Required for Kerberos mutual authentication.
- **NTDS.dit**: The central database file on a Domain Controller that stores all Active Directory data, including user objects, group memberships, and password hashes.
- **SID (Security Identifier)**: A unique, immutable value assigned to every principal (user, group, computer) in Active Directory.
- **RPC (Remote Procedure Call)**: A protocol that allows a program to execute code on a remote system. It is heavily used for Windows management and administration.
- **LSASS (Local Security Authority Subsystem Service)**: The Windows process responsible for enforcing security policies, verifying user logins, handling password changes, and creating access tokens. It often stores credentials in memory, making it a prime target for credential dumping.

## Real-World Attack Scenario
## Real-World Attack Scenario

During a targeted internal red team exercise for a technology firm, I obtained initial access as a standard, unprivileged user. To advance the attack, I needed to compromise an account with higher privileges. The most effective way to achieve this is to find a workstation where a highly privileged IT administrator is currently logged in, but to do so, I first needed to find a machine where my current low-privileged user had Local Administrator rights to extract credentials from memory (e.g., using Mimikatz or Procdump).

**Thought Process:**
Instead of blindly attempting to exploit every machine on the network—which is noisy and easily detected—I needed to systematically map out where my compromised account had administrative privileges. Organizations frequently misconfigure Active Directory by granting excessive local admin rights via Group Policy or manual assignments. By querying the Service Control Manager (SCM) or the SAM-Remote (SAMR) protocol over RPC, I could check my administrative access across the entire subnet without triggering traditional authentication failure alerts.

**Execution:**
I utilized NetExec, which leverages the Impacket library to interact directly with MSRPC. I configured it to check local administrative privileges across the `/24` workstation subnet using my compromised credentials (`jdoe` : `Winter2025!`).
```bash
nxc smb 192.168.200.0/24 -u 'jdoe' -p 'Winter2025!'
```
NetExec automatically attempts to connect to the ADMIN$ share or open the Service Control Manager (SCM) on each host. After scanning the subnet, the output displayed several endpoints, but specifically flagged `WS-DEV-04` and `WS-HELP-09` with the highly sought-after `(Pwn3d!)` tag, confirming my user had Local Administrator rights on those specific machines.

To verify and gather intelligence on who else was using those machines, I queried the active sessions via RPC:
```bash
nxc smb 192.168.200.45 -u 'jdoe' -p 'Winter2025!' --sessions
```

**Outcome:**
The RPC enumeration confirmed I was a local administrator on `WS-HELP-09`. Crucially, the `--sessions` check revealed that a Tier 1 Helpdesk Administrator (`admin_tsmith`) currently had an active session on that machine. Because I possessed local admin rights, I laterally moved to `WS-HELP-09`, dumped the LSASS process memory, and successfully extracted the cleartext password of the Helpdesk Administrator. This targeted RPC enumeration provided the exact stepping stone needed to dramatically escalate my privileges within the domain.


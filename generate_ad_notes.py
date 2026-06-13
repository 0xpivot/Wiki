import os

out_dir = "/home/sanchit/Notes/VAPT/Active Directory/B - 67 - AD Enumeration and Tooling Basics"
os.makedirs(out_dir, exist_ok=True)

def write_note(filename, content):
    with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

appendix_base = r"""
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
"""

f1 = r"""---
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
"""

f2 = r"""---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.12 Password Spraying Basics"
---

# Password Spraying Basics and Lockout Policies

## 1. Executive Summary & Introduction
Password spraying is a targeted brute-force attack technique that flips the traditional brute-force methodology on its head. Instead of targeting a single account with thousands of passwords (which almost guarantees an account lockout), an attacker uses a single, commonly used password against thousands of accounts. This "low and slow" approach is highly effective in Active Directory (AD) environments due to poor user password hygiene and the difficulty of balancing security with usability.

In a VAPT context, password spraying is often one of the first active attacks performed after initial user enumeration. It seeks to establish an initial foothold by identifying users who have chosen predictable passwords like `Summer2026!`, `Company123`, or `Welcome1!`. When executed correctly, password spraying operates entirely under the radar of traditional account lockout policies, making it a critical threat for organizations to understand, detect, and mitigate.

## 2. Technical Mechanisms and Theory
### 2.1 The Traditional Brute Force vs. Password Spraying
- **Traditional Brute Force**: Attacker selects `UserA` and attempts `Pass1`, `Pass2`, `Pass3`, `Pass4`, `Pass5`. If the domain lockout policy is 3 attempts, `UserA` is locked out after `Pass3`. The attack fails and generates loud alerts.
- **Password Spraying**: Attacker selects `Pass1` and attempts it against `UserA`, `UserB`, `UserC`, `UserD`. Since each user only experiences one failed login attempt, no accounts are locked out, provided the attacker waits for the lockout observation window to reset before trying `Pass2`.

### 2.2 Active Directory Lockout Policies
Understanding the domain's lockout policy is the absolute prerequisite for a successful password spray. The policy consists of three critical settings:
1. **Account lockout threshold**: The number of failed logon attempts that will cause a user account to be locked (e.g., 5 attempts).
2. **Account lockout duration**: The number of minutes a locked-out account remains locked before automatically becoming unlocked (e.g., 30 minutes, or 0 for manual administrator unlock).
3. **Reset account lockout counter after**: The number of minutes that must elapse from the time a user fails to log on before the failed logon attempt counter is reset to zero (e.g., 15 minutes).

If an attacker knows these settings, they can tailor their attack. For example, if the threshold is 5 and the reset timer is 15 minutes, the attacker can safely spray 1 password per user every 16 minutes indefinitely without ever triggering a lockout.

### 2.3 Authentication Protocols Utilized
Password sprays can be executed against various endpoints and protocols:
- **Kerberos (Port 88)**: Extremely fast. Tools request a TGT (AS-REQ) and see if the KDC returns a valid TGT or a pre-authentication failure.
- **SMB (Port 445)**: Very common internally. Attempts to bind to the IPC$ share.
- **LDAP (Port 389/636)**: Attempts a simple bind to the directory.
- **HTTP/HTTPS (Web Portals)**: OWA, VPNs, M365 portals. Externally, this is the most common vector, often requiring bypassing MFA or exploiting legacy authentication (e.g., POP3/IMAP).

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
|   Attacker        |                                  |   Domain Controller |
|   (Kali Linux)    |                                  |   (KDC / AD DS)     |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. Enumerate Password Policy (SMB/LDAP NULL Session)    |
        |-------------------------------------------------------->|
        |                                                         |
        | 2. Policy Returned (Threshold: 5, Reset: 15m)           |
        |<--------------------------------------------------------|
        |                                                         |
        | 3. Enumerate Valid Users (e.g., RPC/LDAP)               |
        |-------------------------------------------------------->|
        |                                                         |
        | 4. User List Returned (1000 Users)                      |
        |<--------------------------------------------------------|
        |                                                         |
        |                 --- SPRAY CYCLE 1 ---                   |
        | 5. AS-REQ (User1, Pass: 'Fall2026!')                    |
        |-------------------------------------------------------->|
        | 6. KRB5KDC_ERR_PREAUTH_FAILED (Bad Password)            |
        |<--------------------------------------------------------|
        |                                                         |
        | 7. AS-REQ (User2, Pass: 'Fall2026!')                    |
        |-------------------------------------------------------->|
        | 8. AS-REP (Valid TGT returned) -> SUCCESS!              |
        |<--------------------------------------------------------|
        |                                                         |
        |               --- WAIT FOR RESET TIMER ---              |
        |            (Sleep 16 mins to clear counters)            |
        |                                                         |
        |                 --- SPRAY CYCLE 2 ---                   |
        | 9. AS-REQ (User1, Pass: 'Company2026!')                 |
        |-------------------------------------------------------->|
+-------+-----------+                                  +----------+----------+
```

## 4. Execution and Tooling
### 4.1 Enumerating Password Policy
Before spraying, the policy must be known. If unauthenticated enumeration (NULL session) is disabled, an attacker might need a foothold first, or they may assume a highly conservative default (e.g., 1 attempt per hour).
```bash
# Using NetExec (Null Session / Guest)
nxc smb 192.168.1.10 -u '' -p '' --pass-pol
nxc smb 192.168.1.10 -u 'guest' -p '' --pass-pol

# Using LDAP anonymous bind
ldapsearch -x -h 192.168.1.10 -b "DC=domain,DC=local" -s base "(objectclass=*)" lockoutThreshold lockoutDuration
```

### 4.2 Spraying via Kerberos (Kerbrute)
Kerbrute is excellent because it uses Kerberos Pre-Authentication, which is faster and often less monitored than SMB logon events.
```bash
# Kerbrute password spray
kerbrute passwordspray -d domain.local users.txt "Winter2026!"
```

### 4.3 Spraying via SMB (NetExec)
NetExec is highly versatile for SMB sprays and automatically detects when a password results in local admin access.
```bash
# Spray a single password against a list of users
nxc smb 192.168.1.10 -u users.txt -p 'Welcome123!' -d domain.local --continue-on-success
```

### 4.4 Spraying Externally (MSOLSpray / Trevorspray)
For external facing Azure AD / M365 infrastructure, specialized tools are required to handle rate limiting and MFA.
```bash
# MSOLSpray via PowerShell
Invoke-MSOLSpray -UserList .\users.txt -Password "Password123" -Verbose
```

## 5. Security Posture and Mitigations
### 5.1 Strong Password Policies
The primary defense against password spraying is enforcing a password policy that prevents the use of common passwords.
- **Length over Complexity**: Enforce passphrases (e.g., 15+ characters) rather than complex, short passwords, which encourage users to use predictable patterns (e.g., `P@ssw0rd1!`).
- **Password Banning**: Implement Azure AD Password Protection (or third-party tools) to ban common passwords and variations of the company name.

### 5.2 Multi-Factor Authentication (MFA)
MFA is the most critical control for external interfaces. Even if a password spray is successful, the attacker cannot access the account without the second factor. Note that legacy authentication protocols (e.g., IMAP, POP3) do not support modern MFA and must be explicitly disabled to prevent bypassing.

### 5.3 Lockout Policy Tuning
While a strict lockout policy (e.g., 3 attempts) can hinder brute-forcing, it increases the risk of Denial of Service (DoS) attacks against the domain. A balanced approach (e.g., 10 attempts) combined with robust detection is generally preferred.

## 6. Detection Engineering
### 6.1 Windows Event Logs (Domain Controller)
Detecting a "low and slow" spray requires correlating events across the domain.
- **Event ID 4625 (Failed Logon)**: A sudden spike in 4625 events across a large number of distinct accounts originating from a single source IP.
  - *Logic*: `Count(EventID 4625) > 50` AND `Distinct(TargetUserName) > 50` within a 10-minute window.
- **Event ID 4771 (Kerberos Pre-Auth Failed)**: Specifically useful when attackers use tools like Kerbrute. Monitor for high volumes of error code `0x18` (Pre-authentication information was invalid).

### 6.2 Advanced Splunk SPL Detection
```spl
index=windows_security EventCode=4625 OR EventCode=4771
| bin _time span=15m
| stats dc(TargetUserName) as UniqueUsers count by SourceNetworkAddress
| where UniqueUsers > 20
| sort - UniqueUsers
```

### 6.3 Bypassing Defenses / Evasion
Attackers evade detection by:
- Sourcing the attack from multiple different IP addresses (e.g., using Fireprox, AWS API Gateways, or proxy chains).
- Jittering the time between requests.
- Spraying only a carefully selected subset of high-value users per day (e.g., only IT staff).

## 7. Real-World Case Study
In a recent penetration test for a financial institution, the external perimeter was heavily fortified. However, the organization used an older Cisco AnyConnect VPN that did not support SAML-based MFA. By performing OSINT on LinkedIn, the VAPT team gathered a list of 500 employee names. Using a tool to generate AD username formats (e.g., first.last), they sprayed the password `[CompanyName]2024!`. Three accounts were compromised. Because the VPN lacked MFA, this provided immediate internal network access, bypassing all perimeter firewalls.

## 8. Handling Account Lockouts (Troubleshooting)
If an attacker accidentally locks out accounts:
- Stop the attack immediately.
- Use `nxc smb` or PowerView to check the lockout status of accounts.
- Document the lockouts and inform the client, as lockouts can disrupt critical business operations (e.g., a locked-out service account bringing down an application).

## 9. Chaining Opportunities
- **[[11 - Identifying Local Administrators via RPC]]**: After identifying local admins, spray ONLY the admin accounts to minimize noise.
- **[[13 - AS-REP Roasting Basics and Detection]]**: If spraying reveals an account, but MFA blocks external access, check if the account requires pre-authentication.
- **[[15 - LLMNR and NBT-NS Poisoning Basics]]**: Combined with LLMNR poisoning to gather hashes, allowing targeted offline cracking instead of online spraying.

## 10. Related Notes
- [[11 - Identifying Local Administrators via RPC]]
- [[13 - AS-REP Roasting Basics and Detection]]
- [[14 - Kerberoasting Basics and Identification]]
- [[05 - BloodHound Data Collection]]
"""

f3 = r"""---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.13 AS-REP Roasting Basics and Detection"
---

# AS-REP Roasting Basics and Detection

## 1. Executive Summary & Introduction
AS-REP Roasting is an offensive technique targeting Active Directory (AD) environments that exploits a specific, often legacy-driven, user account configuration: **"Do not require Kerberos preauthentication"** (known as `DONT_REQ_PREAUTH`). When this setting is enabled on a user account, any unauthenticated attacker can request a Kerberos Authentication Service Response (AS-REP) for that user from the Key Distribution Center (KDC/Domain Controller).

The critical flaw lies in the structure of the AS-REP message. A portion of the AS-REP is encrypted using the user's password hash. Because the attacker does not need to authenticate to request this message, they can easily retrieve it, take it offline, and subject it to a brute-force or dictionary attack. If the user possesses a weak password, the attacker can recover the plaintext password, granting them full access to the account.

While less common than Kerberoasting, AS-REP Roasting requires zero initial privileges—an attacker does not even need a valid domain user account to perform the attack, only network line-of-sight to a Domain Controller.

## 2. Technical Mechanisms and Kerberos Deep Dive
### 2.1 Standard Kerberos Pre-Authentication
In a typical Kerberos authentication flow:
1. **AS-REQ (Authentication Service Request)**: The user sends a request to the KDC to obtain a Ticket Granting Ticket (TGT). By default, AD requires pre-authentication. This means the AS-REQ must include a timestamp encrypted with the user's password hash (the `padata` field).
2. **KDC Verification**: The KDC attempts to decrypt this timestamp using the user's hash stored in NTDS.dit. If successful, it proves the user knows their password without transmitting it over the network.
3. **AS-REP (Authentication Service Response)**: The KDC replies with a TGT and a session key, part of which is encrypted with the user's hash.

### 2.2 The DONT_REQ_PREAUTH Vulnerability
When "Do not require Kerberos preauthentication" is checked (UserAccountControl attribute flag `0x00400000` / 4194304):
1. **AS-REQ**: The attacker sends an AS-REQ for the target user *without* the encrypted timestamp.
2. **KDC Verification**: The KDC checks the user's settings, sees pre-authentication is disabled, and skips the timestamp verification.
3. **AS-REP**: The KDC blindly generates the AS-REP and sends it back to the attacker.

The attacker intercepts the AS-REP. Inside this response is the `enc-part`, which contains the logon session key encrypted with the target user's RC4 or AES key (derived from their password). The attacker extracts this encrypted blob.

### 2.3 Offline Cracking
Once the attacker possesses the AS-REP, no further communication with the DC is required. They use tools like Hashcat or John the Ripper to attempt to decrypt the `enc-part`. If a guessed password successfully decrypts the blob, the attacker has discovered the user's plaintext password.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
|   Attacker        |                                  |   Domain Controller |
|   (Unauthenticated|                                  |   (KDC)             |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. Identify Target (e.g., via anonymous LDAP or guess)  |
        |-------------------------------------------------------->|
        |                                                         |
        | 2. Send AS-REQ for 'VulnerableUser'                     |
        |    (NO Pre-Authentication data included)                |
        |-------------------------------------------------------->|
        |                                                         |
        | 3. KDC checks UserAccountControl (DONT_REQ_PREAUTH = 1) |
        |                                                         |
        | 4. Send AS-REP                                          |
        |    (Contains Encrypted Session Key via User Hash)       |
        |<--------------------------------------------------------|
        |                                                         |
        | 5. Attacker extracts encrypted AS-REP blob              |
        |                                                         |
+-------+-----------+                                             |
| Offline Cracking  |                                             |
| (Hashcat Mode     |                                             |
|  18200 / 11400)   |                                             |
+-------------------+                                             |
```

## 4. Execution and Tooling
### 4.1 Enumeration
An attacker with a valid domain account can query LDAP for users with the `DONT_REQ_PREAUTH` flag.
```powershell
# Using PowerView
Get-DomainUser -PreauthNotRequired -Properties samaccountname

# Using native ADModule
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True} -Properties DoesNotRequirePreAuth
```

### 4.2 Exploitation / Roasting
If the attacker does not have an account but has a list of usernames, they can spray AS-REQ packets to see which users return an AS-REP.
```bash
# Using Impacket (GetNPUsers.py) - No credentials needed, just a username list!
GetNPUsers.py domain.local/ -usersfile users.txt -format hashcat -outputfile asreps.txt -dc-ip 192.168.1.10
```
If the attacker already has domain credentials, they can request hashes for all vulnerable accounts in the domain automatically:
```bash
# Using Impacket with credentials
GetNPUsers.py domain.local/jsmith:Password123! -request -format hashcat -outputfile asreps.txt -dc-ip 192.168.1.10
```
Alternatively, using Rubeus on a Windows host:
```cmd
Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt
```

### 4.3 Offline Cracking
The extracted hashes are formatted for Hashcat.
```bash
# Hashcat module 18200 (Kerberos 5, etype 23, AS-REP)
hashcat -m 18200 asreps.txt rockyou.txt -r rules/best64.rule

# For AES-256 (etype 18), use mode 19700
hashcat -m 19700 asreps_aes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
### 5.1 Why does this setting exist?
The `DONT_REQ_PREAUTH` setting is a legacy feature, historically required by older applications, Unix-based systems lacking proper Kerberos support, or specific smart card authentication configurations. In modern AD environments, there is rarely a legitimate business justification for it.

### 5.2 Remediation
The definitive fix is to enable Kerberos pre-authentication for all users.
1. Open Active Directory Users and Computers (ADUC).
2. Navigate to the user's properties -> Account tab.
3. Under Account options, ensure **"Do not require Kerberos preauthentication"** is **UNCHECKED**.
4. Regularly audit AD for any users with `UserAccountControl` containing `0x00400000` via automated PowerShell scripts.

## 6. Detection Engineering
Detecting AS-REP roasting is easier than Kerberoasting because AS-REQ events without pre-authentication are anomalies in modern networks.

### 6.1 Event ID 4768 (A Kerberos authentication ticket (TGT) was requested)
When an AS-REP is successfully requested, Event 4768 is logged on the Domain Controller.
- **Detection Logic**: Monitor Event ID 4768 where:
  - `Pre-Authentication Type` is `0` or blank (indicating no pre-auth was used).
  - `Ticket Encryption Type` is `0x17` (RC4) or `0x12/0x11` (AES), corresponding to the hash format extracted.
  - Exclude known, legitimate legacy service accounts if absolutely necessary, but alert on any standard user or admin account.

### 6.2 Event ID 4771 (Kerberos pre-authentication failed)
If an attacker attempts to roast an account that *does* require pre-authentication, the KDC responds with an error.
- **Detection Logic**: Repeated 4771 events from a single IP, particularly with error code `0x11` (KDC_ERR_PREAUTH_REQUIRED).

### 6.3 Honey Accounts
Create a decoy user account (e.g., `svc_backup_exec`) with a very strong, uncrackable password. Enable "Do not require Kerberos preauthentication" on this account.
Any attempt to request an AS-REP for this account is a guaranteed high-fidelity alert of an active AS-REP Roasting attack on the network.

### 6.4 KQL Query for Detection
```kql
SecurityEvent
| where EventID == 4768
| where PreAuthenticationType == 0 or isempty(PreAuthenticationType)
| project TimeGenerated, AccountName, ClientAddress, TicketEncryptionType
```

## 7. Real-World Case Study
During a recent internal VAPT engagement for a healthcare provider, the testing team utilized an unauthenticated network connection (plugging into a lobby ethernet port). With no domain credentials, the team used `GetNPUsers.py` against a list of 1,000 common names they scraped from the company website. One account, `b.smith`, was configured without pre-authentication. The team retrieved the AS-REP, cracked the RC4 hash using Hashcat in 3 minutes (the password was `Summer2025`), and gained their first set of domain credentials, paving the way for full domain compromise within 48 hours.

## 8. Chaining Opportunities
- **[[12 - Password Spraying Basics and Lockout Policies]]**: If AS-REP roasting fails (e.g., strong password), the targeted accounts might still be susceptible to a long-term password spray.
- **[[14 - Kerberoasting Basics and Identification]]**: Often performed in tandem. An attacker will check for AS-REP roasting, and then move to Kerberoasting once they have a valid TGT.

## 9. Related Notes
- [[12 - Password Spraying Basics and Lockout Policies]]
- [[14 - Kerberoasting Basics and Identification]]
- [[20 - Silver Tickets]]
- [[05 - BloodHound Data Collection]]
"""

f4 = r"""---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.14 Kerberoasting Basics and Identification"
---

# Kerberoasting Basics and Identification

## 1. Executive Summary & Introduction
Kerberoasting is one of the most widespread, effective, and frequently executed attacks in Active Directory (AD) environments. It targets Service Principal Names (SPNs) associated with domain user accounts. By requesting Kerberos Service Tickets (TGS) for these accounts, an attacker can extract a portion of the ticket encrypted with the service account's password hash. This hash can then be cracked offline.

Because any authenticated domain user can request a TGS for any valid SPN within the domain, Kerberoasting requires no special privileges beyond a standard user foothold. Furthermore, because service accounts often hold high privileges (e.g., Domain Admins, SQL Admins) and are notorious for having weak, non-expiring passwords, Kerberoasting frequently provides a direct path to domain compromise.

## 2. Technical Mechanisms and Kerberos Deep Dive
### 2.1 Service Principal Names (SPNs)
An SPN is a unique identifier for a service instance (like an MSSQL server, an IIS web server, or a file share). In AD, a service must be registered under an account so that clients can authenticate to it using Kerberos.
- **Computer Accounts**: By default, SPNs are registered under machine accounts (e.g., `WS01$`). These passwords are long (120 chars), randomized, and change every 30 days. They are practically uncrackable.
- **User Accounts**: System administrators often register SPNs under standard domain user accounts (e.g., `svc_sql`). These passwords are set by humans, frequently fail to meet complexity standards, and often have the "Password never expires" flag set. These are the targets of Kerberoasting.

### 2.2 The Kerberos TGS-REQ/REP Flow
1. **AS-REQ / AS-REP**: The attacker (as a standard domain user) authenticates to the Domain Controller (KDC) and receives a Ticket Granting Ticket (TGT).
2. **TGS-REQ**: The attacker sends a Ticket Granting Service Request to the KDC, presenting their TGT and requesting access to a specific SPN (e.g., `MSSQLSvc/sql.domain.local`).
3. **TGS-REP**: The KDC verifies the TGT and the existence of the SPN. The KDC generates a Service Ticket and sends it back to the attacker.
4. **The Vulnerability**: The Service Ticket contains a section that is encrypted using the NTLM hash (RC4) or AES key of the account associated with the SPN.

### 2.3 Offline Cracking
Crucially, the attacker *does not* need to actually interact with the target service (e.g., the SQL server). They simply take the encrypted Service Ticket they received in step 3, save it to disk, and use brute-force or dictionary attacks to decrypt it. If the password is weak, the ticket is decrypted, and the plaintext password is revealed.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
|   Attacker        |                                  |   Domain Controller |
| (Auth'd User)     |                                  |   (KDC / AD DS)     |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. LDAP Query: Find all User objects with SPNs          |
        |-------------------------------------------------------->|
        | 2. Returns list of SPNs (e.g., svc_sql, svc_backup)     |
        |<--------------------------------------------------------|
        |                                                         |
        | 3. TGS-REQ: "I want a ticket for svc_sql"               |
        |    (Presents attacker's TGT)                            |
        |-------------------------------------------------------->|
        |                                                         |
        | 4. KDC encrypts ticket using svc_sql's password hash    |
        |                                                         |
        | 5. TGS-REP: Returns Encrypted Service Ticket            |
        |<--------------------------------------------------------|
        |                                                         |
+-------+-----------+                                             |
| Offline Cracking  |                                             |
| (Hashcat Mode     |                                             |
|  13100)           |                                             |
+-------------------+                                             |
```

## 4. Execution and Tooling
### 4.1 Enumeration and Extraction via Impacket
From a Linux attacking machine, `GetUserSPNs.py` automates the LDAP query and the TGS-REQ/REP process in one step.
```bash
# Request TGS tickets for all user SPNs and output in hashcat format
GetUserSPNs.py domain.local/jsmith:Password123! -request -outputfile kerberoast_hashes.txt -dc-ip 192.168.1.10
```

### 4.2 Execution via Rubeus (Windows)
If the attacker is operating from a compromised Windows host, Rubeus is the standard tool.
```cmd
# Automatically find all SPNs and request tickets (RC4 preferred)
Rubeus.exe kerberoast /outfile:hashes.txt
```

### 4.3 Execution via PowerShell (Native)
It is possible to request SPNs natively using PowerShell without external tools, making it highly stealthy.
```powershell
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/sql.domain.local"
# The ticket is now cached in memory and can be exported using Mimikatz or Rubeus
```

### 4.4 Offline Cracking
Once the hashes are obtained, Hashcat is used to crack them. Mode 13100 is used for RC4 (Type 23) tickets.
```bash
hashcat -m 13100 kerberoast_hashes.txt rockyou.txt -r rules/best64.rule

# For AES-256 (Type 18), use mode 19600
hashcat -m 19600 kerberoast_aes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
### 5.1 Enforce Strong Passwords for Service Accounts
Because Kerberoasting is an offline attack relying on cracking, the ultimate mitigation is a password that mathematically cannot be cracked within a reasonable timeframe. Service accounts should have randomly generated passwords of 30+ characters.

### 5.2 Managed Service Accounts (gMSA)
Organizations should transition from traditional User accounts for services to Group Managed Service Accounts (gMSAs). gMSAs automatically manage their own passwords (similar to computer accounts), making them 120 characters long and rotating them every 30 days. gMSAs completely neutralize Kerberoasting.

### 5.3 Enforce AES Encryption
Legacy environments default to RC4 (Encryption Type 23) for Kerberos. RC4 is significantly faster to crack offline than AES (Encryption Type 18/17). Ensuring the domain enforces AES for Kerberos tickets dramatically increases the time and compute power required to crack the hashes.

## 6. Detection Engineering
Detecting Kerberoasting is challenging because requesting a TGS is a normal, daily occurrence for every user on the network.

### 6.1 Event ID 4769 (A Kerberos service ticket was requested)
- **Anomaly Detection**: Look for an unusual spike in 4769 events from a single user or IP address in a short time window. Standard users rarely request 50 different service tickets in 2 seconds.
- **Encryption Type Anomalies**: If the domain enforces AES, but an attacker specifically downgrades the request to RC4 (Type 0x17) to make cracking easier, this is a massive red flag. Alert on Event ID 4769 where `Ticket Encryption Type` is `0x17`.

### 6.2 Honey SPNs (Deception Technology)
The most effective detection mechanism is a HoneyToken.
1. Create a fake user account (e.g., `svc_financial_db`).
2. Assign it a fake SPN.
3. Give it a massive, uncrackable password.
4. Set up an alert: Any time Event 4769 is triggered for this specific SPN, it is 100% malicious, as no legitimate service uses it.

### 6.3 Splunk SPL for Honey SPN
```spl
index=windows_security EventCode=4769 TargetUserName="svc_financial_db"
| eval Message="ALERT: Honey SPN Kerberoast attempt detected!"
| table _time, TargetUserName, IpAddress, ClientName
```

## 7. Real-World Case Study
In a 2023 red team exercise, the team established a foothold as a standard user (`h.potter`). They immediately ran Rubeus to kerberoast the domain. They retrieved 15 RC4 service tickets. One of these tickets belonged to an account named `svc_sccm_deploy`. After 15 minutes of cracking using a custom wordlist based on the company's internal documentation, the password `Deploy!2019` was revealed. This service account possessed local administrator rights on all workstations and servers, including the Domain Controllers, leading to a complete compromise of the forest in under two hours.

## 8. Chaining Opportunities
- **[[13 - AS-REP Roasting Basics and Detection]]**: Often the precursor. If AS-REP roasting yields no results, the attacker moves to Kerberoasting.
- **[[20 - Silver Tickets]]**: Once a service account password is cracked, the attacker possesses the account's NTLM hash. They can use this to forge Silver Tickets, granting them administrative access to the service without communicating with the DC.

## 9. Related Notes
- [[13 - AS-REP Roasting Basics and Detection]]
- [[20 - Silver Tickets]]
- [[05 - BloodHound Data Collection]]
"""

f5 = r"""---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.15 LLMNR and NBT-NS Poisoning Basics"
---

# LLMNR and NBT-NS Poisoning Basics

## 1. Executive Summary & Introduction
Link-Local Multicast Name Resolution (LLMNR) and NetBIOS Name Service (NBT-NS) are legacy broadcast protocols built into Microsoft Windows. They are designed to act as fallback mechanisms for name resolution; if a Windows machine cannot resolve a hostname via the primary DNS server, it will broadcast a query to the local subnet asking, "Does anyone know who this is?"

In a Vulnerability Assessment and Penetration Testing (VAPT) scenario, LLMNR/NBT-NS poisoning is consistently one of the most reliable methods for gaining initial credentials on an internal network. An attacker on the local network can listen for these broadcasts and maliciously reply, claiming to be the requested resource. The victim's machine then attempts to authenticate to the attacker, inadvertently sending its NTLMv2 password hash over the network.

This attack requires no initial credentials, operates silently in the background, and capitalizes on simple user typos or misconfigured network drives.

## 2. Technical Mechanisms and Protocol Deep Dive
### 2.1 The Name Resolution Order
When a user attempts to access a network resource (e.g., typing `\\FILESREVER` instead of the correct `\\FILESERVER` in Explorer), Windows follows a specific resolution order:
1. Local `hosts` file.
2. DNS Cache.
3. Primary and Secondary DNS Servers.
4. **LLMNR (Multicast via UDP 5355)**.
5. **NBT-NS (Broadcast via UDP 137)**.

Because `FILESREVER` does not exist in DNS, the DNS query fails. Windows immediately moves to step 4, broadcasting to the entire local subnet: "Who is FILESREVER?"

### 2.2 The Poisoning Attack
An attacker sitting on the same subnet listens for these broadcasts. When the query for `FILESREVER` is seen, the attacker's tool immediately sends a multicast/broadcast reply: "I am FILESREVER! My IP is [Attacker_IP]."

### 2.3 The Authentication Capture
Believing it has found the server, the victim's Windows machine attempts to connect to the attacker's machine via SMB (TCP 445) or HTTP. The attacker's tool simulates a server requiring authentication. The victim's machine, following default Windows behavior (Single Sign-On), automatically attempts to authenticate using NTLM challenge-response.

The attacker captures the NTLMv2 hash. While this is not a plaintext password, the attacker can take this hash offline and crack it using a dictionary attack.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
| Victim Workstation|                                  |   Attacker          |
| (192.168.1.50)    |                                  |   (192.168.1.100)   |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. User typos: \\FILESREVER                             |
        |                                                         |
        | 2. DNS query fails (NXDOMAIN)                           |
        |                                                         |
        | 3. LLMNR Broadcast: "Who has FILESREVER?"               |
        |-------------------------------------------------------->|
        |                                                         |
        | 4. Attacker replies: "I am FILESREVER (192.168.1.100)"  |
        |<--------------------------------------------------------|
        |                                                         |
        | 5. Victim initiates SMB connection to Attacker          |
        |-------------------------------------------------------->|
        |                                                         |
        | 6. Attacker demands NTLM authentication                 |
        |<--------------------------------------------------------|
        |                                                         |
        | 7. Victim sends NTLMv2 Hash                             |
        |-------------------------------------------------------->|
        |                                                         |
+-------+-----------+                                             |
                                                     +------------v------------+
                                                     | Capture NTLMv2 Hash     |
                                                     | -> Crack Offline        |
                                                     | -> Or Relay Attack      |
                                                     +-------------------------+
```

## 4. Execution and Tooling
### 4.1 Responder
`Responder.py` is the undisputed industry standard tool for LLMNR, NBT-NS, and MDNS poisoning. It features built-in rogue servers for SMB, HTTP, FTP, SQL, and more.

```bash
# Run Responder on the local network interface (eth0)
sudo responder -I eth0 -rdw
```
Flags explained:
- `-I eth0`: Specifies the interface.
- `-r`: Enable NetBIOS wredir (forces Windows to authenticate).
- `-d`: Enable NetBIOS domain suffix.
- `-w`: Enable WPAD rogue proxy server (another devastating broadcast attack).

When a victim typos a share, Responder console will light up with the captured NTLMv2 hash:
```text
[SMB] NTLMv2-SSP Client   : 192.168.1.50
[SMB] NTLMv2-SSP Username : DOMAIN\jsmith
[SMB] NTLMv2-SSP Hash     : jsmith::DOMAIN:1122334455667788:000000000...
```

### 4.2 Inveigh
For Windows environments, `Inveigh` is the PowerShell/C# equivalent of Responder. It is highly useful when operating from a compromised Windows beachhead where installing Python or dropping Linux binaries is impossible.
```powershell
# Run Inveigh via PowerShell
Invoke-Inveigh -ConsoleOutput Y -NBNS Y -LLMNR Y
```

### 4.3 Offline Cracking
Once the NTLMv2 hash is captured, it is saved in Responder's log directory and can be cracked using Hashcat (Mode 5600).
```bash
hashcat -m 5600 ntlmv2_hashes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
The presence of LLMNR and NBT-NS traffic is generally considered a critical finding in modern networks, as they serve little purpose when DNS is functioning correctly.

### 5.1 Disable LLMNR via Group Policy
This is the most effective mitigation.
- Navigate to `Computer Configuration -> Administrative Templates -> Network -> DNS Client`.
- Enable the policy: **"Turn off multicast name resolution"**.

### 5.2 Disable NBT-NS via DHCP / Network Adapter
NBT-NS cannot be disabled via a simple GPO. It must be disabled via DHCP scope options or manually on the network adapters.
- **DHCP**: Set Option 43 (Vendor Specific Information) to disable NetBIOS over TCP/IP.
- **Manual/Script**: In the IPv4 properties of the network adapter -> Advanced -> WINS tab -> Select **"Disable NetBIOS over TCP/IP"**.

### 5.3 Implement SMB Signing
If capturing and cracking the hash fails (due to a strong password), attackers will attempt to relay the hash. Enforcing SMB signing across the domain (`Network security: Microsoft network server: Digitally sign communications (always)`) prevents an attacker from relaying the NTLM authentication to another machine.

## 6. Detection Engineering
### 6.1 Network Intrusion Detection Systems (NIDS)
- Monitor UDP ports 5355 (LLMNR) and 137 (NBT-NS).
- Alert on a high volume of LLMNR/NBT-NS replies originating from a single IP address that is not a known DNS or DHCP server.

### 6.2 Endpoint Detection
- **Event ID 4624 (Logon Type 3 - Network Logon)**: Correlate logon events to unusual IP addresses (the attacker's IP). If multiple users are suddenly authenticating to a single, newly surfaced IP address, it is a strong indicator of a rogue SMB server capturing hashes.

## 7. Real-World Case Study
During an internal assessment of a large manufacturing plant, the VAPT team connected to a conference room network port. They started Responder. Within 30 seconds, they captured an NTLMv2 hash from a user attempting to access a defunct legacy print server (`\\PRINTER-OLD`). The hash belonged to an IT Helpdesk employee. The password was quickly cracked (`Summer2023!`). Using this account, the team could log into the IT ticketing system, identify the passwords for local administrator accounts, and escalate privileges across the entire workstation fleet.

## 8. Chaining Opportunities
- **[[16 - SMB Relay Attacks]]**: Instead of cracking the captured NTLMv2 hash offline, the attacker can use tools like `ntlmrelayx.py` to forward the authentication attempt to a critical server (like a Domain Controller or a server where the victim is a local admin) to execute code remotely.
- **[[12 - Password Spraying Basics and Lockout Policies]]**: If the password is cracked, it can be used for spraying.
- **[[11 - Identifying Local Administrators via RPC]]**: If relayed, the attacker needs to know where the victim is an admin.

## 9. Related Notes
- [[16 - SMB Relay Attacks]]
- [[12 - Password Spraying Basics and Lockout Policies]]
- [[11 - Identifying Local Administrators via RPC]]
"""

for idx, content in enumerate([f1, f2, f3, f4, f5]):
    locals()[f'f{idx+1}'] = content + appendix_base

write_note("11 - Identifying Local Administrators via RPC.md", f1)
write_note("12 - Password Spraying Basics and Lockout Policies.md", f2)
write_note("13 - AS-REP Roasting Basics and Detection.md", f3)
write_note("14 - Kerberoasting Basics and Identification.md", f4)
write_note("15 - LLMNR and NBT-NS Poisoning Basics Responder.md", f5)
print("Files generated successfully.")

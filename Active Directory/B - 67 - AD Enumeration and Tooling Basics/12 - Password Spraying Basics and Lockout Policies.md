---
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

In a security assessment for an educational institution, I had mapped the network but lacked any valid domain credentials. The environment heavily utilized Office 365, meaning users likely had the same passwords for their local AD and external services. To gain an initial foothold, I decided to execute a password spraying attack. The challenge was to execute this attack without triggering the organization's account lockout policies, which would alert the IT department and lock legitimate users out of their accounts.

**Thought Process:**
A brute-force attack (many passwords against one user) guarantees a lockout. Password spraying flips this: trying one carefully chosen password against many users. However, before I could spray, I absolutely had to know the domain's password lockout policy. If the threshold was 3 attempts in 30 minutes, spraying 4 times within that window would cause widespread disruption. My plan was to anonymously query the domain controller for the lockout policy, generate a clean list of valid users, and then spray a highly probable password (e.g., the current season and year).

**Execution:**
I first attempted to establish a Null Session to the primary Domain Controller to query the domain password policy anonymously.
```bash
nxc smb 10.10.10.5 -u '' -p '' --pass-pol
```
The command was successful, revealing a `LockoutThreshold` of 5 attempts and a `LockoutDuration` of 30 minutes. This meant I could safely attempt 4 passwords per user every 30 minutes. 

Next, I used an open SMB share I found earlier to extract a list of 500 employee usernames and saved them to `users.txt`. Knowing the threshold, I selected a single, common password: `Autumn2025!`. I used NetExec to perform the password spray against the Domain Controller:
```bash
nxc smb 10.10.10.5 -u users.txt -p 'Autumn2025!' --continue-on-success
```
The `--continue-on-success` flag ensured the tool didn't stop at the first success, allowing me to compromise as many accounts as possible in a single pass.

**Outcome:**
By strictly adhering to the queried lockout policy, the attack remained entirely undetectable by standard lockout monitoring systems. The single spray of `Autumn2025!` successfully authenticated against 14 different user accounts, including a mid-level IT manager's account. This careful, policy-aware approach instantly transitioned the engagement from unauthenticated external reconnaissance to an authenticated internal foothold, providing multiple redundant access vectors.


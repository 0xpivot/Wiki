---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.10 Abuse of Exchange Web Services in AD"
---

# Abuse of Exchange Web Services (EWS) in AD

## 1. Introduction to Exchange Web Services (EWS)

Microsoft Exchange Server is one of the most deeply integrated applications in an Active Directory environment. To facilitate the massive amount of directory reads and writes required for enterprise email (GAL synchronization, recipient routing, calendar sharing), Exchange is granted extremely high privileges within the Active Directory forest.

Exchange Web Services (EWS) is a SOAP-based API that allows client applications (like Outlook for Mac, mobile clients, and third-party integrations) to interact with the Exchange server. EWS provides comprehensive access to mailbox items, calendar data, contacts, and significantly, administrative directory functions.

From an attacker's perspective, EWS is an incredibly powerful, often unfiltered gateway into the domain. Because EWS operates over standard HTTP/HTTPS (ports 80/443), it easily bypasses internal network segmentation and firewall rules that might block traditional RPC, SMB, or LDAP traffic.

### 1.1 The High-Privilege Nature of Exchange
When Exchange is installed, it modifies the Active Directory schema and adds several high-privileged groups to the forest. Historically, the `Exchange Windows Permissions` group possessed `WriteDacl` rights over the Domain object itself, allowing an attacker who compromised an Exchange server to instantly grant themselves DCSync privileges. While Microsoft has mitigated the most egregious permissions in recent Exchange updates, Exchange servers still retain vast read/write access over user objects across the domain.

---

## 2. Exploiting EWS Functionality

If an attacker compromises valid domain credentials (even a low-privileged user with a mailbox), they can interact with the EWS API. If they compromise an Exchange administrative account, the impact is catastrophic.

### 2.1 Mailbox Access and Data Exfiltration
The primary use of EWS for an attacker is stealthy data exfiltration. Unlike connecting via IMAP/POP3, which are often monitored or disabled, EWS is virtually always enabled.

An attacker can use tools like `MailSniper` or custom Python scripts utilizing the `exchangelib` library to connect to EWS and silently search through mailboxes for sensitive information.
-   **Targeting:** Searching for keywords like "password", "VPN", "credentials", or "confidential" in the emails of IT support staff, HR, or executives.
-   **Delegation Abuse:** EWS allows users to read mailboxes to which they have been granted "Delegate Access" or "Folder Permissions." Attackers enumerate these permissions to map out the web of accessible inboxes.

### 2.2 EWS Impersonation (ApplicationImpersonation)
Exchange features a role called `ApplicationImpersonation`. This role is designed for service accounts (like backup software or CRM integrations) to act on behalf of other users without needing their passwords.

If an attacker compromises an account holding the `ApplicationImpersonation` role, they can use EWS to seamlessly impersonate *any* user in the organization, including the Domain Administrator, to read their emails or send malicious emails internally, bypassing all MFA controls.

```xml
<!-- Example EWS SOAP snippet demonstrating Impersonation -->
<soap:Header>
  <t:ExchangeImpersonation>
    <t:ConnectingSID>
      <t:PrimarySmtpAddress>domainadmin@corp.local</t:PrimarySmtpAddress>
    </t:ConnectingSID>
  </t:ExchangeImpersonation>
</soap:Header>
```

### 2.3 Malicious Inbox Rules
A highly persistent and stealthy backdoor technique involves using EWS to create malicious Inbox Rules. An attacker can create a rule that triggers whenever an email arrives containing a specific, obscure string in the subject line (e.g., `[[STATUS-UPDATE-991]]`).

The rule can be configured to:
-   Silently forward the email to an external address (data theft).
-   Move the email to the RSS Feeds folder and mark it as read (hiding alerts from the user).
-   Trigger a custom Outlook form or application (though heavily restricted in modern Exchange, historical exploits used this for remote code execution).

Because these rules are created server-side via EWS, they will execute even if the user never opens their Outlook client.

---

## 3. Relaying and Coercion via Exchange

Exchange's integration with AD and its various web endpoints make it a prime target for NTLM relaying and authentication coercion.

### 3.1 Exchange PushSubscriptions (PrivExchange / CVE-2019-0465)
The classic PrivExchange vulnerability abused the EWS `PushSubscription` feature. An attacker could use EWS to tell the Exchange server: "Send an HTTP notification to *this* URL whenever an event occurs in this mailbox."

By providing an attacker-controlled URL, the Exchange server would connect to the attacker's listener over HTTP and authenticate using NTLM. Because the Exchange server's machine account (`EXCH01$`) held extremely high privileges in AD, the attacker could relay this authentication to a Domain Controller via LDAP to grant themselves DCSync rights.

While the specific `WriteDacl` vulnerability has been patched, `PushSubscriptions` can still be used to coerce authentication from the Exchange server to relay to other services (like MSSQL or SCCM).

### 3.2 Outlook Anywhere (RPC/HTTP) and MAPI/HTTP
Exchange heavily relies on NTLM over HTTP for its MAPI and RPC interfaces. Attackers often target these endpoints (`/rpc/rpcproxy.dll` or `/mapi/emsmdb`) to perform password spraying or credential stuffing. Because these endpoints are designed to accept NTLM, they are highly robust against rate-limiting if not specifically protected by an Application Delivery Controller (ADC) or Web Application Firewall (WAF).

---

## 4. Visualizing the EWS Impersonation Flow

The following ASCII diagram illustrates how an attacker abuses the `ApplicationImpersonation` role via EWS to access executive communications.

```text
+-----------------------+          +------------------------------------+
| Attacker Machine      |          | Corporate Network Boundary         |
|                       |          |                                    |
|  +-----------------+  |          |   +----------------------------+   |
|  | Python Script   |  |          |   | Load Balancer / WAF        |   |
|  | (exchangelib)   |  |          |   +-------------+--------------+   |
|  +--------+--------+  |          |                 |                  |
|           |           |          |                 |                  |
|           | 1. HTTP POST to /EWS/Exchange.asmx     |                  |
|           |    Auth: Compromised Service Account   |                  |
|           |    Header: Impersonate 'CEO@corp.com'  |                  |
+-----------|-----------+          |                 |                  |
            |                      +-----------------|------------------+
            |                                        v
            |                      +-----------------+------------------+
            |                      | Microsoft Exchange Server          |
            |                      |                                    |
            |                      |  2. Validates Service Account Auth |
            |                      |  3. Checks RBAC for                |
            |                      |     'ApplicationImpersonation'     |
            |                      |  4. Role Granted. Grants access    |
            |                      |     to CEO's mailbox backend.      |
            +--------------------------------------->|                  |
                                   |                 |                  |
            5. Returns SOAP XML    |                 |                  |
               with CEO Emails     |<----------------+                  |
            <----------------------+                                    |
                                   +------------------------------------+
```

---

## 5. Defensive Considerations and Mitigation

Securing EWS is complex because it is required for normal business operations. Outright disabling it will break Outlook for Mac and many third-party integrations.

### 5.1 Restricting EWS Access
Use Exchange Client Access Rules (CARs) or EWS policies to restrict which applications and IP subnets can access the `/EWS/Exchange.asmx` endpoint. If third-party integrations originate from specific IPs, whitelist only those IPs.

### 5.2 Auditing ApplicationImpersonation
The `ApplicationImpersonation` Management Role must be heavily audited.
-   Regularly run PowerShell cmdlets to list all users and groups holding this role:
    ```powershell
    Get-ManagementRoleAssignment -Role "ApplicationImpersonation"
    ```
-   Remove the role from any account that does not strictly require it. Ensure service accounts that do require it are restricted to specific target OUs using Management Scopes, rather than the entire organization.

### 5.3 Enforce Multi-Factor Authentication (MFA)
Ensure that Hybrid Modern Authentication (HMA) is enabled, forcing all EWS connections to negotiate via OAuth and Azure AD, thereby enforcing conditional access and MFA policies. Legacy NTLM/Basic authentication to EWS should be explicitly blocked.

### 5.4 Monitoring for Malicious Inbox Rules
Implement SIEM rules to detect the creation of unusual server-side inbox rules. Focus on rules that forward mail externally or move mail based on obfuscated keyword patterns. The `Search-MailboxAuditLog` cmdlet can track rule creation if mailbox auditing is enabled.

---

## 6. Chaining Opportunities

- **[[08 - Advanced NTLM Relaying to MSSQL]]**: If an attacker can coerce the Exchange server using EWS PushSubscriptions, they can relay the Exchange machine account's hash to a backend SQL server, leveraging the Exchange server's high privileges to gain database control.
- **[[09 - PrinterBug and PetitPotam Alternatives]]**: Exchange servers are prime targets for remote coercion via MS-FSRVP or DFSCoerce due to their ubiquitous presence and historical high privileges in the domain.
- **[[01 - Introduction to Active Directory Trusts]]**: Cross-forest Exchange deployments can blur trust boundaries. Compromising EWS in one domain might allow an attacker to read the global address list or access calendars in a trusted domain.

## 7. Related Notes

- [[02 - Local Privilege Escalation Techniques in Windows]]
- [[06 - Exploiting Microsoft Identity Manager MIM]]
- [[04 - Extracting and Reversing DPAPI Secrets]]

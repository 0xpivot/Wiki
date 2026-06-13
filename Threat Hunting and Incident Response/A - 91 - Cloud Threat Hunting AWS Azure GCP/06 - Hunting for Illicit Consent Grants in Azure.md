---
tags: [threat-hunting, cloud, aws, azure, vapt]
difficulty: advanced
module: "91 - Cloud Threat Hunting: AWS, Azure, GCP"
topic: "91.06 Hunting for Illicit Consent Grants in Azure"
---

# Hunting for Illicit Consent Grants in Azure

## Introduction and Theoretical Foundation

In modern cloud identity architectures, traditional credential compromise is no longer the sole avenue for initial access. Threat actors are increasingly pivoting to attack the OAuth 2.0 authorization framework via a technique known as **Illicit Consent Grants**. 

At its core, an illicit consent grant attack occurs when an attacker tricks an end-user into granting a malicious OAuth 2.0 application access to their data. Unlike phishing that steals a password, this attack steals the user's *authorization* to access data, such as reading emails, accessing SharePoint, or sending emails.

Advantages for the attacker:
1. Bypasses Multi-Factor Authentication (MFA) because access is granted via a token after the user authenticates.
2. Access is persistent. Password resets do not revoke the malicious application's consent.
3. The attack relies on the platform's trusted consent screen.

## Mechanics of the Attack

The attack typically follows these phases:
1. **Application Registration**: The attacker registers a multi-tenant application in their own Azure AD (Entra ID) tenant.
2. **Permission Scopes**: The attacker configures the app to request highly sensitive delegated permissions (e.g., `Mail.ReadWrite`, `Contacts.Read`, `Files.Read.All`).
3. **Lure Creation**: The attacker crafts a phishing link pointing to the Microsoft OAuth 2.0 authorization endpoint, embedding their malicious `client_id`.
4. **Execution**: The victim clicks the link, authenticates to Microsoft (satisfying MFA), and is presented with a prompt to grant the app access.
5. **Exploitation**: Upon consent, Microsoft issues an authorization code, which the attacker exchanges for an access token and a refresh token.

## The Anatomy of an OAuth 2.0 Authorization Request

To truly hunt for this, one must understand the anatomy of the phishing link. The attacker crafts a URL to the Microsoft Identity platform:

`https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=12345678-abcd-efgh-ijkl-1234567890ab&response_type=code&redirect_uri=https://malicious-app.com/callback&scope=offline_access%20Mail.ReadWrite%20Contacts.Read&state=random_string`

Let's break down these parameters for the threat hunter:
- **`client_id`**: The unique identifier for the attacker's application. If you identify a malicious `client_id`, you can pivot on this in Azure AD audit logs across all your tenants.
- **`response_type=code`**: Indicates the authorization code flow. The attacker receives a code to exchange for tokens.
- **`redirect_uri`**: Where Microsoft sends the authorization code. A suspicious domain here (e.g., `ngrok.io`, recently registered domains) is a strong IOC.
- **`scope`**: The permissions the attacker is requesting.
- **`state`**: Used for CSRF protection, but often ignored or hardcoded by rudimentary attackers.

## ASCII Diagram: Illicit Consent Grant Flow

```text
+----------------+          (1) Phishing Link            +-------------------+
|    Attacker    | ------------------------------------> |   Victim (User)   |
| (Malicious App)|                                       |                   |
+----------------+                                       +-------------------+
        ^                                                         |
        | (4) App accesses APIs                                   | (2) Clicks link, authenticates
        |     using user's token                                  |     and reviews consent prompt
        |                                                         v
+----------------+          (3) Grants Consent           +-------------------+
| Microsoft Graph| <------------------------------------ |   Entra ID        |
| / O365 APIs    |         (Token issued to App)         |  (Authorization)  |
+----------------+                                       +-------------------+
```

## Deep Dive: Azure AD App Permissions

Understanding the difference between Delegated and Application permissions is crucial:
- **Delegated Permissions**: The application acts on behalf of the signed-in user. The app cannot do anything the user cannot do. Consent can be granted by the user (if allowed) or requires admin consent.
- **Application Permissions**: The application runs as a background service or daemon without a signed-in user. This always requires administrator consent and is highly dangerous if granted to a malicious app.

When hunting, prioritize applications that request wide-ranging permissions. Common abused scopes include:
- `Mail.Read` / `Mail.ReadWrite`
- `Mail.Send` (Used for lateral phishing)
- `offline_access` (Grants a refresh token for persistent access)
- `Directory.Read.All`
- `Notes.Read.All`

## Real-World Attack Scenario

### The Nobelium Playbook
In the aftermath of the SolarWinds breach, the Nobelium threat actor heavily utilized illicit consent grants. They compromised an IT administrator's account via a separate mechanism, but instead of just reading emails, they registered a new malicious application directly in the victim's tenant and granted it **Application Permissions** (`RoleManagement.ReadWrite.Directory`). 

This allowed the application to mint new credentials and maintain persistent, invisible access to the environment long after the original administrator's password was rotated and their session tokens were revoked. The attacker used the application's client credentials to interact with the Microsoft Graph API, silently exfiltrating terabytes of sensitive emails without triggering traditional "impossible travel" or "suspicious login" alerts on user accounts.

## Telemetry and Log Sources

To hunt for this activity, you need the following log sources ingested into your SIEM (e.g., Microsoft Sentinel):
1. **Azure AD Audit Logs**: Captures app registration, consent grants, and credential modifications.
2. **Office 365 Unified Audit Log (UAL)**: Captures `Consent to application` events.
3. **Azure AD Sign-in Logs (Service Principal Sign-ins)**: Crucial for detecting when the malicious application is actually exercising its tokens.

Ensure that your logging configuration captures both User and Admin consent operations.

### Example JSON Log Entry (Azure AD Audit Log)

```json
{
  "time": "2026-06-10T12:00:00Z",
  "resourceId": "/tenants/xxxx/providers/Microsoft.aadiam",
  "operationName": "Consent to application",
  "operationVersion": "1.0",
  "category": "AuditLogs",
  "tenantId": "xxxx",
  "resultSignature": "None",
  "durationMs": 0,
  "callerIpAddress": "192.168.1.1",
  "correlationId": "yyyy-yyyy-yyyy-yyyy",
  "identity": "user@victim.com",
  "properties": {
    "initiatedBy": {
      "user": {
        "userPrincipalName": "user@victim.com"
      }
    },
    "targetResources": [
      {
        "id": "app-object-id",
        "displayName": "Malicious App",
        "type": "ServicePrincipal",
        "modifiedProperties": [
          {
            "displayName": "ConsentAction.Permissions",
            "newValue": "Mail.Read, offline_access"
          }
        ]
      }
    ]
  }
}
```

## Detection Engineering & KQL Queries

### Query 1: Detecting New App Consent Grants
This query identifies when a user grants consent to an application, focusing on high-risk permissions.

```kql
AuditLogs
| where OperationName == "Consent to application"
| extend Actor = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetApp = tostring(TargetResources[0].displayName)
| extend Permissions = tostring(TargetResources[0].modifiedProperties)
| where Permissions has_any ("Mail.Read", "Mail.Send", "Files.Read", "offline_access")
| project TimeGenerated, Actor, TargetApp, Permissions, CorrelationId
| order by TimeGenerated desc
```

### Query 2: Detecting Admin Consent to Risky Applications
Admin consent affects the entire tenant. An attacker phishing an admin for consent is a critical severity incident.

```kql
AuditLogs
| where OperationName == "Admin consent to application"
| extend AdminUser = tostring(InitiatedBy.user.userPrincipalName)
| extend AppName = tostring(TargetResources[0].displayName)
| extend AppId = tostring(TargetResources[0].id)
| project TimeGenerated, AdminUser, AppName, AppId
```

### Query 3: Identifying Suspicious Service Principal Sign-ins
Once the app has consent, it will sign in to access data. Look for service principals authenticating from unexpected locations or ASNs.

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| summarize SignInCount = count() by AppId, ServicePrincipalName, IPAddress, Location
| where Location notin ("US", "UK") // Adjust to baseline
| order by SignInCount desc
```

### Query 4: Spikes in API Calls by Service Principals
If an app starts rapidly pulling data, it can be detected by examining the volume of Graph API calls.

```kql
OfficeActivity
| where RecordType == "SharePointFileOperation" or RecordType == "ExchangeItem"
| where ClientAppId != ""
| summarize Count = count() by bin(TimeGenerated, 1h), ClientAppId
| where Count > 1000 // Threshold for anomaly
| order by TimeGenerated desc
```

## Threat Hunting Hypotheses

1. **Hypothesis**: Users are bypassing security controls by granting third-party apps access to enterprise data.
   - **Hunt**: Review all third-party enterprise apps added in the last 30 days. Investigate the publisher verification status. Unverified publishers should be blocked.
2. **Hypothesis**: An attacker has compromised a global admin and deployed a multi-tenant app to establish a backdoor.
   - **Hunt**: Look for `Add service principal` operations followed by `Add app role assignment to service principal` where the role granted is `Global Administrator` or `Exchange Administrator`.

## Remediation and Incident Response

When a malicious application is discovered, rapid containment is critical:
1. **Revoke Consent**: Remove the service principal / enterprise application from the tenant.
   ```powershell
   Remove-AzureADServicePrincipal -ObjectId <ServicePrincipal_ObjectID>
   ```
2. **Revoke User Tokens**: Revoke all refresh tokens for the affected users to ensure no remaining sessions are valid.
   ```powershell
   Revoke-AzureADUserAllRefreshToken -ObjectId <User_ObjectID>
   ```
3. **Investigate API Usage**: Query Microsoft Graph activity logs or Office 365 UAL to determine exactly what data the application accessed during its dwell time.
4. **Harden Consent Policies**: Configure Azure AD to require admin approval for all app consents, or restrict consent to only apps published by verified publishers.

## Chaining Opportunities
- `[[01 - Credential Stuffing and Spraying in the Cloud]]`: Used to compromise the initial admin account before registering an app.
- `[[02 - Bypassing MFA via Token Theft]]`: Similar end-goal, but relies on stealing existing tokens rather than generating new ones via OAuth consent.
- `[[05 - Azure AD App Registrations vs Enterprise Applications]]`: Fundamental knowledge required to understand how multi-tenant apps instantiate in a victim tenant.

## Related Notes
- `[[07 - Microsoft Defender for Cloud Telemetry]]`
- `[[12 - Hunting for Malicious Azure Runbooks]]`
- `[[14 - Advanced KQL for Threat Hunters]]`

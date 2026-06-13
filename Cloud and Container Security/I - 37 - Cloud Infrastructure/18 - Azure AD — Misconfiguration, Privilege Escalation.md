---
tags: [cloud, azure, azure-ad, privesc, rbac, active-directory]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.18 Azure AD"
---

# Azure AD (Entra ID) — Misconfiguration and Privilege Escalation

Azure Active Directory (now officially rebranded as Microsoft Entra ID) is the backbone of identity and access management for Microsoft Azure, Microsoft 365, and thousands of third-party SaaS applications. Unlike traditional on-premises Active Directory (which uses Kerberos, LDAP, and Group Policy), Azure AD is a flat, REST API-driven identity service utilizing OAuth 2.0, OpenID Connect, and SAML. Misconfigurations in Azure AD frequently lead to devastating privilege escalation attacks, allowing adversaries to move from a standard user compromise to Global Administrator.

## 1. Architectural Deep Dive: Roles, Principals, and Scopes

To understand Azure AD privilege escalation, one must understand its distinct authorization models. Azure uses two completely separate Role-Based Access Control (RBAC) systems that frequently cause confusion:

1.  **Azure AD Roles (Entra ID Roles)**: These roles govern access to the *identity tenant itself* and Microsoft 365 services (e.g., Global Administrator, User Administrator, Helpdesk Administrator). They control who can reset passwords, create users, or manage enterprise applications.
2.  **Azure RBAC (Azure Resource Roles)**: These roles govern access to *Azure infrastructure resources* (e.g., Owner, Contributor, Reader on Subscriptions, Resource Groups, and VMs).

**Crucial Linkage**: By default, Azure AD Roles do not grant Azure RBAC permissions. However, a **Global Administrator** can elevate their access to gain the **User Access Administrator** role at the root scope (`/`), granting them the ability to assign themselves the `Owner` role on every single Azure Subscription tied to the tenant. This makes Azure AD compromise the ultimate prize.

### Identity Types

*   **Users**: Standard human identities.
*   **Groups**: Collections of users or service principals. Groups can be assigned roles. (Note: "Role-assignable groups" are a specific feature).
*   **Service Principals**: The local representation of an Application within a specific tenant. It is the identity used by apps to log in and access resources.
*   **Managed Identities**: Automatically managed Service Principals used by Azure resources (like VMs or Function Apps) to authenticate to other Azure services without managing credentials.

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                        Microsoft Entra ID (Azure AD)                    |
|                                                                         |
|  +-------------------+        +--------------------------------------+  |
|  | Compromised User  |        |      Target: Global Administrator    |  |
|  | "Alice (Helpdesk)"|        |                                      |  |
|  +---------+---------+        +------------------+-------------------+  |
|            |                                     ^                      |
|            | 1. Discovers Path                   |                      |
|            v                                     |                      |
|  +-------------------+        +------------------+-------------------+  |
|  | Dynamic Group     |        |   App Registration / Service Princ.  |  |
|  | "IT Admins"       +------->+   Permissions: RoleManagement.Read.  |  |
|  |                   | 2. Add |                Directory             |  |
|  +-------------------+        +--------------------------------------+  |
|                                                  | 3. Elevate           |
+--------------------------------------------------|----------------------+
                                                   v
                                        +-------------------------+
                                        | Azure Subscriptions     |
                                        | (VMs, Databases, KeyV)  |
                                        +-------------------------+
```

## 2. Common Privilege Escalation Vectors

Attack paths in Azure AD usually resemble complex graphs. Attackers use tools like **AzureHound** or **Stormspotter** to map these graphs and find the shortest path to Global Admin.

### 2.1 Group Membership Modification (Dynamic Groups)

Azure AD allows the creation of Dynamic Groups, where membership is evaluated based on user attributes rather than manual assignment.
*   **The Flaw**: If an attacker compromises a user who has the `User Administrator` role, or simply has the rights to modify user attributes (like changing their own "Department" field to "IT"), they might automatically be added to a highly privileged Dynamic Group.
*   **Exploitation**: The attacker updates their user profile. The Azure AD background engine evaluates the rule, adds the attacker to the "Cloud Admins" group, and grants them access to critical resources.

### 2.2 Application/Service Principal Abuse (Illicit Consent Grant)

Applications in Azure AD are granted API permissions (OAuth scopes) to interact with the directory via the Microsoft Graph API.
*   **The Flaw**: A Service Principal might possess the `RoleManagement.ReadWrite.Directory` permission, which allows it to assign Azure AD roles to any user. If an attacker can compromise the credentials (client secret or certificate) of this Service Principal, or if they own the Application Registration, they can use it to elevate themselves.
*   **Exploitation**:
    1. Attacker finds a Service Principal with high Graph API permissions.
    2. Attacker retrieves the cleartext Client Secret from an Azure Key Vault, a misconfigured CI/CD pipeline, or an exposed `.env` file on a VM.
    3. Attacker authenticates as the Service Principal using the Client ID and Secret.
    4. Attacker issues an API call to assign the `Global Administrator` role to their low-privileged user account.

**Example Graph API Call (Adding user to Global Admin):**
```http
POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments
Content-Type: application/json
Authorization: Bearer eyJ0eXAi...[Token of compromised Service Principal]

{
  "principalId": "attacker-object-id",
  "roleDefinitionId": "62e90394-69f5-4237-9190-012177145e10", /* Global Admin ID */
  "directoryScopeId": "/"
}
```

### 2.3 The "Add-Member" Attack Path

If a user is designated as the **Owner** of an Azure AD Group, they can add anyone to that group. If that group happens to have Azure RBAC roles assigned to it (e.g., `Contributor` on a Subscription), the group owner can add themselves to the group and instantly gain `Contributor` access to the infrastructure.
*   *Note: Standard Azure AD Groups cannot be assigned Azure AD Roles (like Global Admin) unless they are specifically created as "Role-assignable groups," which requires Global Admin/Privileged Role Admin to set up. But standard groups CAN be assigned Azure infrastructure RBAC roles.*

### 2.4 Device Registration and Primary Refresh Tokens (PRT)

If an attacker compromises a user's Windows device that is Hybrid Azure AD Joined or Azure AD Registered, they can extract the Primary Refresh Token (PRT) using tools like Mimikatz or roadtx.
*   The PRT represents a strong authentication claim, often satisfying Multi-Factor Authentication (MFA) requirements.
*   The attacker can inject the PRT into their own browser or use it via CLI tools to authenticate as the user and bypass Conditional Access policies requiring MFA.

## 3. Defense and Remediation

Securing Azure AD requires a strict Zero Trust approach and continuous auditing of identity graphs.

1.  **Tiered Administration model**: Do not mix standard user accounts with administrative accounts. Admins should have separate, dedicated "cloud-only" accounts for administration (e.g., `admin.alice@domain.onmicrosoft.com`) that are not used for daily email or web browsing.
2.  **Privileged Identity Management (PIM)**: Do not grant permanent standing access to privileged roles (Global Admin, Privileged Role Admin, etc.). Use Azure AD PIM to require Just-In-Time (JIT) activation, requiring approval and MFA at the time of elevation.
3.  **Strict Consent Policies**: Disable the ability for end-users to grant consent to third-party applications. Implement an admin consent workflow to prevent Illicit Consent Grant phishing attacks.
4.  **Audit Application Permissions**: Regularly review the Microsoft Graph API permissions granted to Service Principals. High-risk permissions like `RoleManagement.ReadWrite.Directory`, `AppRoleAssignment.ReadWrite.All`, and `Directory.ReadWrite.All` should be heavily restricted and monitored.
5.  **Conditional Access**: Implement strict Conditional Access policies. Require strong, phish-resistant MFA (FIDO2) for all administrative roles. Restrict admin portal access to specific compliant devices or trusted IP ranges.

## 4. Forensics and Detection

*   **Azure AD Audit Logs**: This is the primary forensic artifact. Monitor for:
    *   `Add member to role` events, especially outside of PIM activation workflows.
    *   `Add service principal` or `Update application` events, indicating potential backdooring of an app.
    *   `Consent to application` events granting high-risk permissions.
*   **Risky Sign-ins and User Risk**: Utilize Azure AD Identity Protection. Investigate any alerts regarding "Unfamiliar sign-in properties" or "Anonymous IP address."
*   **Graph API Monitoring**: Monitor access logs for unusual queries against the `roleManagement` or `applications` endpoints originating from Service Principals rather than human users.
*   **BloodHound Routine Audits**: Defenders should run AzureHound regularly to identify toxic combinations and unintended attack paths that form due to complex nested groups and overlapping permissions.

## Chaining Opportunities

*   **[[21 - Azure SSRF via Metadata]]**: An attacker uses SSRF to steal a Managed Identity token. They then use this token against Azure AD to execute the privilege escalation paths described here.
*   **[[20 - Azure Function Apps — Exposed Secrets]]**: Extracting a Service Principal client secret from a misconfigured Function App to perform Graph API abuse.
*   **[[05 - Pass-the-PRT Attacks]]**: Deep dive into extracting and utilizing Primary Refresh Tokens from compromised endpoints.

## Related Notes

*   [[13 - Cloud IAM Comparison]] - Comparing Azure AD RBAC vs AWS IAM vs GCP IAM.
*   [[06 - OAuth 2.0 and OIDC Security]] - The underlying protocols that Azure AD relies upon.

## Appendix D: Comprehensive Cloud Penetration Testing Methodology
When assessing cloud environments for default service account abuse and privilege escalation, standard network penetration testing methodologies fall short. The focus must shift to identity, metadata, and control plane interactions.

### Step 1: Reconnaissance & OSINT
*   Identify cloud provider footprint via ASN mapping and DNS enumeration.
*   Enumerate public storage buckets and exposed serverless functions.
*   Scrape GitHub and GitLab for accidentally committed service account keys or infrastructure-as-code (IaC) templates.

### Step 2: Initial Access & Foothold
*   Exploit traditional web vulnerabilities (SSRF, RCE, LFI) on exposed compute instances.
*   Phish internal developers for overly permissive tokens or CLI credentials.
*   Utilize compromised CI/CD pipelines as an entry point into the cloud fabric.

### Step 3: Local Enumeration & Metadata Extraction
*   Query the link-local metadata servers (`169.254.169.254`).
*   Extract instance identity tokens, project metadata, and user-data/startup scripts.
*   Analyze the local environment variables and hidden files (`.aws/credentials`, `gcloud/application_default_credentials.json`).

### Step 4: Lateral Movement & Privilege Escalation
*   Leverage stolen tokens to authenticate to the cloud provider's API.
*   Enumerate attached IAM policies, roles, and scopes.
*   Exploit misconfigurations (e.g., `iam.serviceAccounts.actAs` or missing scope limits) to jump to higher-privileged accounts or resources.

## Appendix E: Incident Response and Forensics Playbook
When a breach is suspected, responders must act quickly to contain the blast radius.

### Containment
1.  **Revoke Tokens**: Immediately revoke the stolen access tokens. In Azure, utilize Continuous Access Evaluation (CAE) to ensure token revocation is near-instantaneous.
2.  **Isolate the Instance**: Detach the compromised VM from the VNet or apply a strict deny-all Network Security Group (NSG) rule.
3.  **Rotate Keys**: Rotate any static access keys or secrets that were accessible from the compromised instance's environment.

### Advanced Threat Hunting in Azure AD
*   **Search for Unexpected App Registrations**: Query the Graph API for any newly created Service Principals with high-privilege directory roles.
*   **Identify Suspicious Consent Grants**: Look for OAuth apps requested by standard users that ask for `offline_access`, `Mail.Read`, or `Directory.AccessAsUser.All`.
*   **Monitor Conditional Access Bypass**: Search logs for logins originating from legacy authentication protocols (e.g., IMAP, POP3) which natively bypass MFA policies.
*   **Track PIM Elevations**: Graph out all Privileged Identity Management elevations. If a low-level admin account activated a Global Admin role at 3 AM from an unexpected IP, investigate immediately.

### Investigation
1.  **Audit Logs**: Query Azure AD Audit Logs and Azure Activity Logs for anomalous API calls originating from the compromised principal. Look for actions outside its normal baseline.
2.  **Network Flow**: Analyze NSG Flow Logs for unexpected outbound connections, particularly to known threat actor infrastructure.
3.  **Disk Forensics**: Image the instance's boot disk and analyze for dropped malware, modified startup scripts, or signs of lateral movement tooling.

## Appendix A: The Intricacies of Azure AD Roles

### Global Administrator vs. Privileged Role Administrator
While the Global Administrator is the ultimate prize, the **Privileged Role Administrator** (PRA) is often a more accessible stepping stone. A PRA can manage role assignments in Azure AD, meaning they can grant the Global Admin role to themselves or another compromised account. Furthermore, PRA can reset passwords for all users, including Global Admins, effectively seizing control of the tenant.

### Application Administrator vs. Cloud Application Administrator
Both roles can create and manage Enterprise Applications and App Registrations. The key difference is that the Application Administrator can manage the application proxy settings, while the Cloud Application Admin cannot. Both roles are highly targeted by attackers because they allow the creation of malicious OAuth applications that can be used for Illicit Consent Grant attacks.

## Appendix B: Tooling for Azure AD Exploitation

### AzureHound
AzureHound is the data collector for BloodHound in Azure environments. It utilizes the Microsoft Graph API to extract objects (Users, Groups, Service Principals) and their relationships.
*   **Usage**: `azurehound -u attacker@domain.com -p "Password123!" --tenant "domain.onmicrosoft.com" list --output results.json`
*   **Analysis**: In the BloodHound GUI, defenders and attackers alike can query for "Shortest Path to High Privilege Roles."

### ROADtools
Developed by Dirk-jan Mollema, ROADtools is a framework to interact with Azure AD.
*   **roadrecon**: Gathers data from Azure AD and stores it in a local SQLite database. It provides an offline GUI to browse the tenant structure, identifying misconfigured Service Principals and complex group nestings without generating noisy API traffic in real-time.
*   **roadtx**: A tool specifically designed for manipulating Azure AD tokens, including Primary Refresh Tokens (PRTs). It is essential for bypassing Conditional Access policies and simulating device-bound authentication.

## Appendix C: Hardening Azure AD (Step-by-Step)

1.  **Enforce FIDO2 Security Keys**: Migrate privileged users away from SMS or App-based push notifications to hardware security keys (FIDO2/WebAuthn). This mitigates AiTM (Adversary-in-the-Middle) phishing attacks.
2.  **Disable Legacy Authentication**: Ensure protocols like POP3, IMAP, and older versions of Exchange ActiveSync are completely blocked via Conditional Access. These protocols do not support MFA.
3.  **Regular Access Reviews**: Utilize Azure AD Identity Governance to automate access reviews for highly privileged groups and roles.
4.  **Monitor Emergency Access Accounts**: "Break-glass" accounts should be strictly monitored. Any sign-in from these accounts should trigger immediate, high-priority alerts to the SOC.

---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.01 Entra ID vs On-Prem AD Architecture"
---

# 65.01 - Entra ID vs On-Prem AD Architecture

## Executive Summary
The paradigm shift from on-premises Active Directory Domain Services (AD DS) to Microsoft Entra ID (formerly Azure AD) represents a fundamental restructuring of enterprise identity, authentication, and access management. For Vulnerability Assessment and Penetration Testing (VAPT) professionals, understanding the architectural dichotomy between these two environments—and the bridge that connects them (Azure AD Connect)—is critical. This note provides an extreme-depth technical analysis of the architectural differences, authentication protocol shifts, trust boundaries, and resulting attack surfaces in a hybrid identity environment.

## Foundational Architecture and Core Differences

### On-Premises Active Directory (AD DS)
Active Directory Domain Services is built on a hierarchical, directory-centric model designed primarily for closed, trusted local area networks (LANs). 
- **Structure:** Forests, Domains, Organizational Units (OUs).
- **Core Protocols:** Kerberos (authentication), NTLM (legacy authentication), LDAP (directory querying), DNS (service location), DCE/RPC (management and communication).
- **Trust Model:** Transitive and non-transitive domain/forest trusts. Perimeter-based security (firewall as the boundary).
- **Device Management:** Group Policy Objects (GPOs), System Center Configuration Manager (SCCM).

### Microsoft Entra ID (Azure AD)
Entra ID is a flat, cloud-native, multi-tenant identity and access management (IAM) service designed for internet-facing, Zero Trust architectures.
- **Structure:** Flat tenant structure with Users, Groups, and Administrative Units (AUs). No OUs, Forests, or Domains.
- **Core Protocols:** SAML 2.0, OAuth 2.0, OpenID Connect (OIDC), WS-Federation, Microsoft Graph API (REST).
- **Trust Model:** Zero Trust identity-centric model. The identity *is* the perimeter. Context-aware access via Conditional Access.
- **Device Management:** Mobile Device Management (MDM), Microsoft Intune, Entra Registered / Joined / Hybrid Joined states.

---

## Architectural Visualization: Hybrid Identity Topology

The following ASCII diagram illustrates the network boundaries, authentication flows, and synchronization mechanisms in a typical Hybrid Entra ID deployment utilizing Azure AD Connect with Password Hash Sync (PHS) and Seamless Single Sign-On (SSSO).

```text
+-----------------------------------------------------------------------------------+
|                                 MICROSOFT ENTRA ID (CLOUD)                        |
|                                                                                   |
|   +-------------------+    +----------------------+    +----------------------+   |
|   |                   |    |                      |    |                      |   |
|   | Entra ID Users &  |    |  Conditional Access  |    |  Microsoft Graph API |   |
|   | Administrative    |    |  Policies & MFA      |    |  & Role-Based Access |   |
|   | Units (Flat)      |    |  (Zero Trust Engine) |    |  Control (RBAC)      |   |
|   +--------+----------+    +----------+-----------+    +----------+-----------+   |
|            ^                          ^                           ^               |
|            | SAML/OAuth2/OIDC         |                           |               |
+------------|--------------------------|---------------------------|---------------+
             |                          |                           |
             | PRT / Tokens             | Policy Evaluation         | REST API Calls
             |                          v                           |
+------------|--------------------------+---------------------------|---------------+
|          [ INTERNET / EXTERNAL NETWORK BOUNDARY (HTTPS / TLS 1.2+) ]              |
+------------|--------------------------+---------------------------|---------------+
             |                          |                           |
+------------|--------------------------|---------------------------|---------------+
|            |                    ON-PREMISES NETWORK               |               |
|            v                          |                           |               |
|   +-------------------+     +---------+-----------+     +---------+-----------+   |
|   |                   |     |                     |     |                     |   |
|   | Corporate Enduser |     |  Azure AD Connect   |     |  Active Directory   |   |
|   | (Hybrid Joined /  |     |  Server (Syncs      |---->|  Domain Controllers |   |
|   | Seamless SSO)     |---->|  Users, Groups, &   |     |  (Kerberos, LDAP,   |   |
|   |                   |     |  Password Hashes)   |     |  NTLM, NTDS.dit)    |   |
|   +--------+----------+     +---------+-----------+     +---------------------+   |
|            |                          ^                           ^               |
|            | Kerberos (SSSO)          | MS-DRSR (DCSync)          |               |
|            +--------------------------+---------------------------+               |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Deep Dive: Authentication Protocol Shifts

### The Legacy World: Kerberos and NTLM
In on-prem AD, Kerberos relies on a trusted third party (the Key Distribution Center / KDC running on Domain Controllers). 
1. **AS-REQ / AS-REP:** User authenticates, gets a Ticket Granting Ticket (TGT).
2. **TGS-REQ / TGS-REP:** User requests a Ticket Granting Service (TGS) ticket for a specific service (SPN).
3. **AP-REQ:** User presents TGS to the target service.

*Vulnerability:* Susceptible to Pass-the-Hash (PtH), Overpass-the-Hash, Kerberoasting, AS-REP Roasting, and Golden/Silver Ticket attacks because cryptographic keys are statically tied to passwords and the domain trust.

### The Cloud World: OAuth 2.0, OIDC, and SAML 2.0
Entra ID relies on web-based federated identity and token-based authorization.
1. **SAML 2.0:** Primarily used for enterprise SSO. Entra ID acts as the Identity Provider (IdP), issuing signed XML assertions to Service Providers (SPs).
2. **OAuth 2.0 / OIDC:** Entra ID issues JSON Web Tokens (JWTs).
   - **Access Tokens:** Short-lived tokens (typically 1 hour) presented to APIs (like MS Graph) as Bearer tokens.
   - **Refresh Tokens:** Long-lived tokens used to request new Access Tokens without re-authenticating.
   - **Primary Refresh Tokens (PRT):** A specialized Entra ID token bound to a specific Windows/macOS/iOS device, enabling seamless SSO across cloud apps.

*Vulnerability:* Susceptible to Token Theft, Pass-the-PRT, Illicit Consent Grants (OAuth Phishing), Golden SAML, and App Registration abuse.

---

## Hybrid Identity Bridging Mechanisms

To allow users to log in to cloud applications using their on-premises credentials, Microsoft provides **Azure AD Connect** (now Microsoft Entra Connect Sync). There are three primary authentication architectures in a hybrid environment:

### 1. Password Hash Synchronization (PHS)
The simplest and most common method. 
- AD Connect hashes the on-prem NTLM password hash (using MD4) *again* using PBKDF2-HMAC-SHA256, and synchronizes this one-way hash to Entra ID.
- Entra ID handles the authentication entirely in the cloud.
- *Attack Surface:* AD Connect requires extreme privileges (`MS-DRSR` / DCSync) to read the on-prem `NTDS.dit`. If the AD Connect server is compromised, the attacker can extract the sync credentials and dump the entire on-prem AD.

### 2. Pass-Through Authentication (PTA)
Authentication happens on-premises, but the user logs into the cloud portal.
- Entra ID queues the authentication request.
- Lightweight PTA Agents installed on-prem (usually on DCs or dedicated servers) pull the request outbound via HTTPS, validate the password against the local DC, and send a Boolean success/failure back to Entra ID.
- *Attack Surface:* If an attacker compromises a PTA agent server, they can intercept authentication requests, log plaintext passwords, or force authentication approvals.

### 3. Federation (AD FS or PingFederate)
All authentication is redirected to an on-premises Identity Provider.
- Entra ID delegates authentication entirely to Active Directory Federation Services (AD FS).
- *Attack Surface:* Complex on-prem infrastructure. If an attacker extracts the AD FS Token-Signing Certificate (the DKM key), they can forge SAML tokens for any user, bypassing MFA completely (Golden SAML attack).

---

## Access Control and Privilege Management

### On-Premises
- **Mechanism:** Discretionary Access Control Lists (DACLs) and Access Control Entries (ACEs) stored as Security Descriptors on Active Directory objects.
- **Abuse:** BloodHound mapping of generic execution (`GenericAll`, `WriteDacl`), lateral movement via GPOs, AdminSDHolder modifications.

### Entra ID
- **Mechanism:** Role-Based Access Control (RBAC). Roles such as `Global Administrator`, `Privileged Authentication Administrator`, and `User Administrator`.
- **Abuse:** Abuse of Microsoft Graph API, adding credentials to Service Principals / App Registrations, bypassing Conditional Access policies via trusted IPs, Privilege Escalation via custom roles.

### Administrative Units (AUs) vs. Organizational Units (OUs)
- **OUs** in AD DS are structural and can have Group Policies (GPOs) linked to them to control endpoint configurations.
- **AUs** in Entra ID are purely logical containers used to delegate administrative boundaries (e.g., granting a user `Helpdesk Administrator` rights *only* over the "Germany Office" AU). They do not configure endpoints.

---

## The Concept of Conditional Access (CA)

In the perimeter-less cloud environment, Conditional Access replaces the corporate firewall. CA evaluates signals upon every authentication request:
- **User/Risk:** Is the user's behavior anomalous (Impossible Travel)?
- **Location:** Is the IP trusted? (Corporate VPN vs Tor network).
- **Device:** Is the device marked as "Compliant" in Intune? Is it Hybrid Entra Joined?
- **Application:** Which app are they trying to access?

**VAPT Note:** Bypassing Conditional Access is a primary objective in cloud penetration testing. Common bypasses include:
1. Identifying legacy authentication protocols (e.g., IMAP/POP3) which do not support CA MFA enforcement.
2. Compromising a fully managed, "Compliant" Entra Joined endpoint to leverage its Primary Refresh Token (PRT), thereby satisfying device-based CA policies.
3. Exploiting Trusted Named Locations (e.g., routing traffic through a compromised corporate VPN endpoint).

---

## Attack Surface and Lateral Movement (Cloud vs On-Prem)

The inter-connectivity between on-prem and cloud creates bidirectional attack vectors:

### On-Prem to Cloud Lateral Movement
1. **Compromising AD Connect:** As detailed in [[03 - Azure AD Connect Sync Credential Extraction]], compromising the AD Connect server allows attackers to manipulate synced objects, potentially escalating privileges in the cloud (e.g., modifying a synchronized user who holds an Entra ID Admin role, though Microsoft explicitly blocks syncing privileged cloud roles natively, workarounds via groups exist).
2. **Forging Federation Tokens:** Exporting the DKM key from on-prem AD FS to forge Golden SAML assertions, compromising the cloud tenant. (See [[05 - Golden SAML - Forging IDP Tokens]]).
3. **Seamless SSO Forgery:** Stealing the `AZUREADSSOACC` Kerberos hash to forge silver tickets and request Entra ID tokens as any on-prem user. (See [[04 - Seamless SSO Desktop SSO Abuse]]).

### Cloud to On-Prem Lateral Movement
1. **Password Writeback:** If Self-Service Password Reset (SSPR) with Password Writeback is enabled, a compromised cloud account could be used to reset an on-prem password, granting access to local resources.
2. **Endpoint Compromise via Intune:** A compromised Entra ID account with `Intune Administrator` privileges can deploy malicious PowerShell scripts or MSI payloads to all enrolled on-premises/hybrid endpoints.
3. **Azure App Proxy / VPN Configurations:** Cloud administrative access can be abused to modify VPN routing, Conditional Access trusted IPs, or Azure Application Proxy settings to tunnel directly into the on-prem network.

---

## Hardening and Defensive Posture

1. **Tiered Administration:** Implement a strict Tier-0 isolation model for on-prem AD, and mirror this with separate, cloud-only emergency access accounts ("Break Glass" accounts) in Entra ID.
2. **Disable Legacy Authentication:** Force modern authentication across the entire Entra ID tenant to block basic auth sprays.
3. **Protect the AD Connect Server:** Treat the AD Connect server as a Tier-0 asset (same security level as a Domain Controller). Restrict interactive logons.
4. **Enforce Phishing-Resistant MFA:** Utilize FIDO2 keys or Windows Hello for Business, and configure Conditional Access to require device compliance.

---


## Real-World Attack Scenario
## Real-World Attack Scenario: Navigating the Hybrid Perimeter

**The Context:** An advanced persistent threat (APT) actor has gained initial access to a corporate network via a sophisticated spear-phishing campaign. The target environment is a classic hybrid identity setup: an on-premises Active Directory Domain Services (AD DS) synchronized with Microsoft Entra ID via Azure AD Connect using Password Hash Synchronization (PHS) and Seamless Single Sign-On (SSSO). The attacker’s ultimate goal is to exfiltrate highly sensitive executive emails hosted in Exchange Online, which is protected by Entra ID Conditional Access policies blocking legacy authentication and enforcing MFA for non-corporate network access.

**The Reconnaissance:** 
Once inside the LAN, the attacker conducts local network reconnaissance. Using BloodHound and LDAP queries, they map the Active Directory topology. They observe a flat Entra ID structure mirrored by complex on-prem OUs, but their focus quickly shifts to the bridging mechanisms. They identify a server named `SVR-AADCONNECT-01`, which acts as the Azure AD Connect server. Knowing the architecture, the attacker realizes this server is the linchpin connecting the legacy Kerberos/NTLM world to the modern SAML/OAuth cloud environment.

**The Execution:**
1. **Lateral Movement:** The attacker finds a misconfigured GPO that grants local administrator rights over several servers, including the AD Connect server, to a compromised helpdesk account. Using Pass-the-Hash, they laterally move to `SVR-AADCONNECT-01`.
2. **On-Prem Escalation:** Recognizing the AD Connect server as a Tier-0 asset, the attacker impersonates the `ADSync` service account. They execute `adconnectdump` to decrypt the LocalDB credentials, extracting the plaintext password of the `MSOL_` account.
3. **DCSync & SSSO Key Extraction:** With the `MSOL_` account, the attacker executes a DCSync attack against the primary Domain Controller. They specifically target the `AZUREADSSOACC` computer account hash, which is critical for the Seamless SSO architecture.
4. **Cloud Pivot:** Because the Entra ID tenant implicitly trusts the on-premises SSSO kerberos tickets, the attacker uses the extracted `AZUREADSSOACC` hash to forge a Silver Ticket. 
5. **Bypassing Conditional Access:** They present this forged ticket to the Entra ID authentication endpoint (`autologon.microsoftazuread-sso.com`). Entra ID processes the valid Kerberos ticket and issues an Access Token and a Primary Refresh Token (PRT). Because the ticket appears to come from the trusted corporate network (satisfying the CA location policies), the attacker bypasses MFA entirely.

**The Outcome:**
By deeply understanding the architectural trust boundaries between the on-premises domain and Entra ID, the attacker seamlessly pivoted from a low-level helpdesk account on the LAN to full access in the cloud. They utilized the newly minted PRT to interact with the Microsoft Graph API, systematically dumping the executives' Exchange Online mailboxes without triggering traditional on-premises SIEM alerts, demonstrating the profound risks of hybrid identity architectures.

## Chaining Opportunities

- Understanding this architecture is the prerequisite for all hybrid identity attacks.
- Proceed to [[02 - Pass-the-PRT Primary Refresh Token Attacks]] to understand how attackers hijack cloud identities from compromised endpoints.
- Proceed to [[03 - Azure AD Connect Sync Credential Extraction]] for attacks targeting the synchronization layer.

## Related Notes
- [[04 - Seamless SSO Desktop SSO Abuse]]
- [[05 - Golden SAML - Forging IDP Tokens]]
- [[Active Directory Exploitation Fundamentals]]
- [[Microsoft Entra ID OAuth2 Abuse]]

---
*End of note.*

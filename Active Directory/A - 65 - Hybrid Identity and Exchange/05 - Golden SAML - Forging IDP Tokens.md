---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.05 Golden SAML - Forging IDP Tokens"
---

# 65.05 - Golden SAML - Forging IDP Tokens

## Executive Summary
Golden SAML is one of the most devastating identity-based attacks in a federated architecture. It allows an attacker with domain privileges to forge SAML 2.0 authentication assertions and impersonate *any* user to *any* Service Provider (SP) that trusts the compromised Identity Provider (IdP). First extensively documented by CyberArk and famously utilized by the UNC2452 threat actor during the SolarWinds supply chain attack, Golden SAML represents the ultimate bypass of cloud identity perimeters. 

When applied to a Microsoft ecosystem, it is typically executed by compromising an on-premises Active Directory Federation Services (AD FS) infrastructure. By extracting the AD FS token-signing certificate and its private key, an attacker can construct entirely valid, cryptographically signed SAML responses offline. These responses can unconditionally bypass Multi-Factor Authentication (MFA), Conditional Access policies, and password requirements in Entra ID (Azure AD).

---

## Architectural Visualization: Federated Trust and Golden SAML

```text
+----------------------------------------------------------------------------------------+
|                                MICROSOFT ENTRA ID (SP)                                 |
|                                                                                        |
|   +--------------------------------------------------------------------------------+   |
|   |  Domain: federated.company.com (Configured as a Federated Domain)              |   |
|   |                                                                                |   |
|   |  Trust Configuration:                                                          |   |
|   |  - Issuer URI: http://adfs.company.com/adfs/services/trust                     |   |
|   |  - Token-Signing Public Cert (Thumbprint: A1B2C3D4...)                         |   |
|   +--------------------------------------------------------------------------------+   |
|             ^                                                      |                   |
|             | 4. Attacker sends forged SAML Response directly      | 5. Entra ID       |
|             |    via HTTP POST. Evaluated as mathematically valid. |    issues tokens. |
+-------------|------------------------------------------------------|-------------------+
              |                                                      v
+-------------|--------------------------------------------------------------------------+
|             |                       ATTACKER MACHINE                                   |
|             |                                                                          |
|   +---------+----------------------------------------------------------------------+   |
|   | Tool: shimit / AADInternals                                                    |   |
|   | 1. Create a custom SAML Assertion for 'GlobalAdmin@federated.company.com'.     |   |
|   | 2. Inject arbitrary claims: (e.g., authmethod=password, MFA=completed).        |   |
|   | 3. Sign the XML blob using the stolen AD FS Token-Signing Private Key.         |   |
|   +---------+----------------------------------------------------------------------+   |
|             ^                                                                          |
|             | Stolen Key Material (Exported off-network)                               |
+-------------|--------------------------------------------------------------------------+
              |
+-------------|--------------------------------------------------------------------------+
|             |               ON-PREMISES NETWORK (TIER-0)                               |
|   +---------+-----------+                     +------------------------------------+   |
|   | AD FS Server        |                     | Active Directory Domain Controller |   |
|   | (Compromised)       |<--------------------| Container: CN=ADFS,CN=Microsoft... |   |
|   | Contains AD FS DB   |  Read DKM Key       | Contains the Distributed Key       |   |
|   | (WID or SQL)        |-------------------->| Management (DKM) master key.       |   |
|   +---------------------+                     +------------------------------------+   |
+----------------------------------------------------------------------------------------+
```

---

## Anatomy of the Vulnerability

In a SAML 2.0 federation, the SP (e.g., Entra ID, AWS, Salesforce) does not verify passwords. It blindly trusts the IdP (AD FS). The mechanism of trust is purely cryptographic: the IdP signs the SAML assertion (an XML document) using an asymmetric private key. The SP uses the IdP's previously shared public key to verify the signature.

If the attacker steals the IdP's private key, the trust model collapses. 

### The Key Material: AD FS and the DKM Key
In Microsoft AD FS, the token-signing private key is not stored as a simple `.pfx` file on the filesystem. It is stored inside the AD FS configuration database (either Windows Internal Database [WID] or a remote SQL server). 

To protect this key, AD FS encrypts it using **Distributed Key Management (DKM)**.
- The DKM master encryption key is stored as a blob in the on-premises Active Directory under a specific container (usually `CN=ADFS,CN=Microsoft,CN=Program Data,DC=domain,DC=com`).
- To extract the token-signing key, the attacker needs *both*:
  1. Access to the AD FS database to extract the encrypted certificate.
  2. The DKM master key from Active Directory to decrypt it.

*Note:* Because extracting the DKM key requires high privileges (Domain Admin or an AD FS service account), Golden SAML is an escalation/persistence technique, not an initial access vector.

---

## Step-by-Step Exploitation: Executing Golden SAML

### Phase 1: Extracting the AD FS Configuration and DKM Key
The attacker compromises the AD FS server and exports the database and keys. Tools like `Mimikatz`, `ADFSDump`, or `AADInternals` automate this complex extraction.

Using `Mimikatz` on the AD FS Server:
```powershell
privilege::debug
# Extract the DKM key from AD and decrypt the certificates from the AD FS WID
crypto::adfs
```
This command outputs the decrypted Base64 encoded `pfx` of the Token-Signing certificate and the Token-Decrypting certificate, along with their export passwords.

Alternatively, using `AADInternals`:
```powershell
Import-Module AADInternals
# Extracts keys directly and saves them locally
Export-AADIntADFSCertificates
```

### Phase 2: Forging the SAML Token
The attacker moves the extracted `.pfx` file to their unmanaged attacker machine. They now construct a forged SAML response. The most lethal aspect of this phase is **Claim Manipulation**. 

When forging the token, the attacker manually dictates the claims:
- **Identity:** They specify the UPN (User Principal Name) or ImmutableID of any cloud user (e.g., the cloud Global Admin).
- **MFA Bypass Claim:** They inject the claim `<AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</AuthnContextClassRef>` or specific MFA claims, signaling to Entra ID that "the IdP has already successfully performed MFA." Entra ID inherently trusts this and bypasses its own Conditional Access MFA prompts.

Using a tool like `shimit` or `AADInternals`:

```powershell
# Authenticate to Entra ID by forging a SAML token for an administrator
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("C:\Path\To\TokenSigningCert.pfx", "Password123")

$Token = New-AADIntSAMLToken -ImmutableID "xyz123" -Issuer "http://adfs.company.com/adfs/services/trust" -Certificate $cert

# Submit the SAML token to Entra ID's login endpoint to receive an Access Token / Session
Connect-AADInt -SAMLToken $Token
```

The attacker now possesses full, MFA-bypassed access to the cloud environment as the targeted user.

---

## Differences Between Golden Ticket and Golden SAML

While conceptually similar, they differ massively in scope and remediation:
- **Golden Ticket:** Forges Kerberos TGTs. Grants access to on-premises resources. Remediated by rolling the `krbtgt` password twice.
- **Golden SAML:** Forges SAML Assertions. Grants access to cloud and external SPs (Office 365, AWS, GCP, external SaaS). Remediated by rolling the AD FS token-signing certificate and updating all downstream SPs with the new public key.

---

## Indicators of Compromise (IoCs) and Detection Engineering

Golden SAML is exceptionally difficult to detect because the resulting tokens are cryptographically flawless. Detections must focus on the *extraction* phase or behavioral anomalies post-forgery.

### 1. DKM Key Extraction Anomalies
Monitor Active Directory for anomalous read operations against the DKM container.
- **Path:** `CN=ADFS,CN=Microsoft,CN=Program Data,DC=domain,DC=com`
- **Detection Logic:** Alert if a user or process other than the legitimate AD FS service account queries the `thumbnailPhoto` attribute (which holds the DKM key data) of objects within this container.

### 2. AD FS Server Telemetry
- Monitor for the execution of tools like `ADFSDump.exe`, or `mimikatz.exe` on the AD FS server.
- Monitor for WMI queries or Named Pipe connections to the Windows Internal Database (WID) `\\.\pipe\MICROSOFT##WID\tsql\query` by unauthorized processes.

### 3. Entra ID / Cloud Telemetry
- **Mismatched Authentication:** Look for sign-in logs where the identity is authenticated via SAML (federated), but the source IP address belongs to an anonymizer network, VPN, or geographic location completely inconsistent with the user's normal behavior, while the *IdP* IP address (if logged) is not the expected AD FS egress IP.
- **Impossible Travel:** Since the SAML token is often submitted from the attacker's infrastructure directly to the SP, it may trigger impossible travel alerts compared to the user's simultaneous normal on-premises or VPN activity.

---

## Hardening and Remediation Strategies

1. **Protect AD FS as Tier-0:** The AD FS servers, the SQL/WID database, and the DKM container in AD must be strictly managed under Tier-0 administrative protocols.
2. **Hardware Security Modules (HSM):** Store the AD FS token-signing and token-decrypting keys in a physical or network HSM rather than the software database. This prevents `mimikatz` or `ADFSDump` from extracting the private key, as the key never leaves the cryptographic boundary of the HSM.
3. **Migrate to Managed Cloud Authentication:** The most effective defense against Golden SAML is to dismantle the AD FS infrastructure entirely. Migrate from federated authentication to Microsoft Entra ID managed authentication (Password Hash Sync + Seamless SSO, or Pass-Through Authentication). By moving the IdP entirely to the cloud, the keys are managed by Microsoft and are not extractable by an on-premises compromise.

---


## Real-World Attack Scenario
## Real-World Attack Scenario: The Golden SAML Pivot

**The Context:** An advanced nation-state actor has infiltrated the Tier-0 on-premises infrastructure of a defense contractor. The contractor heavily relies on Microsoft 365 for sensitive communications, protected by strict conditional access and hardware MFA. All cloud authentication is federated through an on-premises Active Directory Federation Services (AD FS) farm. The attacker's objective is to access the CEO's Exchange Online mailbox without triggering MFA prompts or anomalous login alerts that usually accompany password resets.

**The Reconnaissance:** 
The attacker leverages their Domain Admin privileges to perform internal reconnaissance. They identify the AD FS database hosted on a dedicated SQL server. More importantly, they query Active Directory and locate the Distributed Key Management (DKM) container (`CN=ADFS,CN=Microsoft,CN=Program Data...`), which holds the master key required to decrypt the AD FS token-signing certificates.

**The Execution:**
1. **Extraction:** The attacker uses `Mimikatz` on the compromised AD FS server to extract the DKM key from Active Directory. With the DKM key in hand, they decrypt the WID/SQL database, extracting the AD FS Token-Signing private key and saving it as a `.pfx` file.
2. **Exfiltration:** The `.pfx` file is exfiltrated to the attacker’s external command and control (C2) infrastructure. At this point, the attacker no longer needs to interact with the on-premises network.
3. **SAML Forgery:** Using a tool like `shimit` or `AADInternals`, the attacker crafts a forged SAML 2.0 XML assertion. They manually set the identity claim to the CEO's ImmutableID. Crucially, they inject the `<AuthnContextClassRef>` claim to indicate that MFA was successfully completed at the Identity Provider level.
4. **Signing the Assertion:** The forged XML is cryptographically signed using the stolen AD FS private key.
5. **The Bypass:** The attacker sends an HTTP POST request containing the forged SAML token directly to Entra ID’s login endpoint.

**The Outcome:**
Entra ID evaluates the SAML token, verifies the cryptographic signature against the trusted public key, and unconditionally accepts it. Because the token explicitly claims MFA was satisfied, Entra ID bypasses all CA policies and issues a valid Access Token for the CEO. The attacker utilizes this token to authenticate to Exchange Online via the Graph API, seamlessly exfiltrating years of sensitive correspondence without the CEO ever receiving an MFA prompt, executing a perfect Golden SAML attack.

## Chaining Opportunities
- Requires high-level on-premises privileges (Domain Admin) to execute, typically achieved via Kerberoasting, NTLM relay, or local privilege escalation.
- Once Golden SAML is executed, attackers can move laterally to *other* connected cloud environments (e.g., if the compromised AD FS also provides SSO for AWS, the attacker can forge tokens for AWS roles).
- It is often used as a long-term persistence mechanism, as the token-signing certificates usually have a lifespan of 1 to 3 years.

## Related Notes
- [[01 - Entra ID vs On-Prem AD Architecture]]
- [[Active Directory Exploitation Fundamentals]]
- [[Active Directory - DCSync Attacks]]
- [[Microsoft Entra ID OAuth2 Abuse]]

---
*End of note.*

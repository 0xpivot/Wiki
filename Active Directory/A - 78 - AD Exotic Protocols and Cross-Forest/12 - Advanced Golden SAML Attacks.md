---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.12 Advanced Golden SAML Attacks"
---

# 78.12 Advanced Golden SAML Attacks

## Introduction to SAML and Federation Security
Security Assertion Markup Language (SAML) is an open standard that allows identity providers (IdP) to pass authorization credentials to service providers (SP). In enterprise environments, Microsoft Active Directory Federation Services (AD FS) is frequently deployed as the IdP to bridge on-premises Active Directory identities with cloud services like Microsoft 365, AWS, and Salesforce.
The "Golden SAML" attack allows a threat actor with administrative access to the AD FS environment to forge arbitrary SAML authentication objects (tokens). This grants the attacker the ability to impersonate any user across all federated cloud services, completely bypassing Multi-Factor Authentication (MFA), Conditional Access policies, and normal password checks. 
Notably, Golden SAML was a primary mechanism utilized in the SolarWinds supply chain attack (NOBELIUM) to pivot from on-premises networks into Microsoft 365 clouds.

## AD FS Architecture and the Token Signing Key
To trust the assertions made by the IdP, the SAML protocol relies on asymmetric cryptography. When AD FS generates a SAML Response indicating a user has successfully authenticated, it cryptographically signs this response using a specific private key known as the **Token Signing Private Key**.
The cloud Service Provider (e.g., Entra ID / Azure AD) holds the corresponding public certificate. If the signature matches, the SP assumes the assertion is legitimate.

If an attacker can extract the Token Signing Private Key, they can forge SAML assertions offline. Because the attacker mathematically signs the assertion with the valid, trusted private key, the Service Provider inherently trusts it.

### The Distributed Key Manager (DKM)
By default, AD FS stores its Token Signing and Token Decryption certificates inside an AD FS configuration database (either Windows Internal Database - WID, or Microsoft SQL Server). 
However, the private keys within this database are encrypted. Microsoft uses the **Distributed Key Manager (DKM)** architecture to protect these keys. The master DKM key is stored as a secret attribute within an Active Directory container, typically located at:
`CN=ADFS,CN=Microsoft,CN=Program Data,DC=domain,DC=com`

Therefore, extracting the Token Signing Private Key is a two-step process:
1. Obtain the DKM Master Key from Active Directory via LDAP or DCSync.
2. Read the encrypted Token Signing Private Key from the AD FS database and decrypt it using the DKM Master Key.

## ASCII Diagram: Golden SAML Attack Flow

```text
  [On-Premises AD Environment]             [AD FS Server / Database]                [Cloud (M365 / Entra ID)]
             |                                          |                                        |
             |<-- 1. Attacker compromises AD FS Server -|                                        |
             |                                          |                                        |
             |<-- 2. DCSync/LDAP Read of DKM Master Key |                                        |
             |       (CN=ADFS,CN=Microsoft...)          |                                        |
             |                                          |                                        |
             |                                          |<-- 3. Extract Encrypted Token Signing  |
             |                                          |       Key from WID/SQL Database        |
             |                                          |                                        |
  [Attacker Infrastructure]                             |                                        |
             |                                          |                                        |
             |=== 4. OFFLINE SAML FORGERY (Golden SAML)=|                                        |
             |    - Decrypt Token Signing Key via DKM   |                                        |
             |    - Craft SAML Assertion for Cloud Admin|                                        |
             |    - Inject "MFA Satisfied" Claims       |                                        |
             |    - Sign with Token Signing Private Key |                                        |
             |                                          |                                        |
             |--- 5. Submit Forged SAML Response (HTTP POST) ----------------------------------->|
             |<-- 6. Cloud SP Verifies Signature, Issues Session Cookie (e.g., ESTSAUTH) --------|
             |                                          |                                        |
             |--- 7. Pivot to Cloud Services as Global Administrator --------------------------->|
```

## The Mechanics of MFA Bypass
One of the most devastating aspects of Golden SAML is its ability to bypass MFA. 
When configuring federation, administrators often configure Entra ID to trust the MFA claims provided by the on-premises AD FS server. This is governed by the `FederatedIdpMfaBehavior` setting.
If an attacker forges a SAML token, they can simply inject the SAML claim indicating that MFA was successfully completed:
`<AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</AuthnContextClassRef>`
`<AuthnContextClassRef>urn:microsoft:adfs:mfa</AuthnContextClassRef>`
Because the token is perfectly signed, Entra ID honors this claim, skipping any secondary cloud-based MFA prompts.

## Step-by-Step Execution Mechanics

### Phase 1: Extracting the DKM Key and AD FS Configuration
Using tools like Mimikatz or specialized scripts (e.g., `ADFSDump`), an attacker with local admin privileges on the AD FS server can extract the necessary materials.
```powershell
# Using Mimikatz on the AD FS server to extract the DKM and Certificates
privilege::debug
token::elevate
# If using WID (Windows Internal Database)
lsadump::adfs /server:\\.\pipe\MICROSOFT##WID\tsql\query

# This command parses the AD FS database, automatically queries Active Directory 
# for the DKM key, decrypts the certificates, and exports them to .pfx files.
```

Alternatively, from a remote machine with DA privileges, an attacker can use `Impacket` and custom python scripts to remotely read the DKM container and SQL database.

### Phase 2: Forging the Golden SAML Token
With the `Token Signing Certificate (.pfx)` in hand, the attacker can use tools like `shimit` or `ADFSpoof` to generate the malicious SAML response.
```bash
# Using shimit (Python-based Golden SAML tool)
# We need the ImmutableID of the target cloud user, and the target Service Provider URL.
python3 shimit.py \
  -idp http://adfs.corp.local/adfs/services/trust \
  -sp urn:federation:MicrosoftOnline \
  -u "GlobalAdmin@corp.com" \
  -i "xyz123-immutable-id-of-admin" \
  -c "C:\Extracted_Certificates\TokenSigningCert.pfx" \
  -p "mimikatz_pfx_password" \
  -mfa \
  --endpoint https://login.microsoftonline.com/login.srf

# The tool outputs a Base64-encoded SAMLResponse string.
```

### Phase 3: Injecting the Token
The attacker opens a browser, navigates to the cloud login page, intercepts the SAML POST request (using Burp Suite), and replaces the legitimate SAMLResponse body parameter with the forged Base64 string. 
Upon forwarding the request, Entra ID issues the authentication cookies (`ESTSAUTH`, `ESTSAUTHPERSISTENT`), granting full access to the Microsoft 365 environment.

## Advanced Variations: Cross-Tenant Pivoting
If the AD FS server is configured to federate with multiple different cloud tenants (e.g., a managed service provider scenario), a single compromised Token Signing Key can be used to forge SAML assertions for *all* connected tenants, resulting in massive, multi-organizational compromise from a single AD FS breach.

## Indicators of Compromise (IoCs) and Telemetry
1. **DCSync against DKM Container:** Event ID 4662 indicating an attempt to read the AD FS DKM container (`CN=ADFS,CN=Microsoft,CN=Program Data...`) by an unusual account.
2. **Unusual Logon Behaviors:** A user logging into M365 from a completely unknown geo-location with a SAML token, but without any corresponding authentication event on the on-premises AD FS server's event logs (Event ID 1200 / 1202).
3. **MFA Claim Anomalies:** Anomalous logs in Entra ID Sign-in logs showing MFA satisfied by a trusted IdP for high-risk IP addresses.
4. **WID Database Access:** Unexpected local pipe connections to `\\.\pipe\MICROSOFT##WID\tsql\query` on the AD FS server.

## Defensive Mitigations and Engineering
1. **Tier 0 Designation for AD FS:** AD FS servers must be treated as Tier 0 assets, identical to Domain Controllers. They should be strictly isolated, and only accessible via highly secure Admin Workstations (PAWs).
2. **Hardware Security Modules (HSM):** Store the AD FS Token Signing and Token Decryption keys inside a dedicated HSM rather than the software-based DKM database. This prevents private key extraction even if the AD FS server OS is completely compromised.
3. **Cloud-Native Authentication:** Migrate away from federated authentication. Transition to Managed Authentication using Password Hash Sync (PHS) or Pass-Through Authentication (PTA) coupled with cloud-native Entra ID Conditional Access.
4. **Rotate Certificates:** If AD FS is compromised, the Token Signing Certificates must be forcefully rolled over, and the old certificates explicitly untrusted in the cloud tenant.

## Chaining Opportunities
- A Golden SAML attack is the ultimate pivot mechanism, bridging on-premises [[15 - Tier 0 Compromise and Domain Dominance]] into complete cloud tenant takeover.
- Initial compromise of the AD FS server can sometimes be achieved via [[13 - Delegated Authentication Bypass]] targeting the AD FS service accounts.

## Related Notes
- [[11 - Forging Ticket Granting Tickets TGTs]]
- [[13 - Delegated Authentication Bypass]]
- [[15 - Tier 0 Compromise and Domain Dominance]]

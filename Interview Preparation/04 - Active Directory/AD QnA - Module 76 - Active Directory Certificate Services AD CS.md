---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 76"
---

# Active Directory Certificate Services (AD CS) Security

## Custom ASCII Diagram: AD CS ESC1 Attack Path

```text
                                                                         +---------------------+
                                                                         |                     |
                                                +----------------------> | Domain Controller   |
                                                |  (3) Request TGT       | (KDC)               |
                                                |      using forged DA   |                     |
                                                |      certificate via   +---------------------+
                                                |      PKINIT            | NTAuthCertificates  |
                                                |                        +---------------------+
                                                |                                   ^
                                                |                                   | (Verifies CA
                                                |                                   |  trust)
+-----------------------+                       |                                   |
|                       |                       |                        +---------------------+
|   Attacker Machine    | <---------------------+                        |                     |
|  (Compromised Domain  |     (2) Issues certificate                     |  AD CS Enterprise   |
|   User: jsmith)       |         valid for Domain Admin                 |  Certificate        |
|                       |         (administrator)                        |  Authority (CA)     |
+-----------------------+                                                |                     |
            |                                                            +----------+----------+
            |                                                                       ^
            | (1) Request Certificate via vulnerable template (ESC1)                |
            |     - Requires: ENROLLEE_SUPPLIES_SUBJECT                             |
            |     - Requires: Client Authentication EKU                             |
            |     - Subject Alternate Name (SAN): administrator                     |
            +-----------------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: Explain the precise mechanical requirements that make a certificate template vulnerable to ESC1 (Domain Escalation via SAN).
**Expert Answer:**
For an AD CS template to be vulnerable to ESC1, four distinct conditions must be met simultaneously within the template's configuration:
1. **Client Authentication EKU:** The template must specify an Extended Key Usage (EKU) that allows for authentication. Common examples include `Client Authentication` (OID 1.3.6.1.5.5.7.3.2), `Smart Card Logon` (OID 1.3.6.1.4.1.311.20.2.2), `PKINIT Client Authentication` (OID 1.3.6.1.5.2.3.4), or `Any Purpose` (OID 2.5.29.37.0).
2. **Manager Approval is Disabled:** The `PEND_ALL_REQUESTS` flag in the `mspki-enrollment-flag` attribute must NOT be set. If approval is required, the CA issues the certificate in a pending state, requiring a CA administrator to manually approve it, which kills the automated attack path.
3. **Authorized Signatures are Not Required:** The `msPKI-RA-Signature` attribute must be 0. If authorized signatures are required (e.g., an Enrollment Agent certificate), a standard low-privileged user cannot enroll.
4. **ENROLLEE_SUPPLIES_SUBJECT Flag is Enabled:** This is the crux of the vulnerability. The `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` flag must be present in the `mspki-certificate-name-flag` attribute. This allows the requester to supply an arbitrary Subject Alternative Name (SAN) in the Certificate Signing Request (CSR). 

When all these are true, an attacker can request a certificate, specify a highly privileged user (like Domain Admin) in the SAN, and immediately receive a valid certificate for that user, which can then be used with PKINIT to request a TGT.

### Q2: Detail the underlying mechanism of ESC8 (NTLM Relay to AD CS Web Enrollment) and how the EPA (Extended Protection for Authentication) mitigates it.
**Expert Answer:**
ESC8 exploits the Active Directory Certificate Services Web Enrollment interface (typically located at `http://<CA_SERVER>/certsrv`). By default, this IIS application supports NTLM authentication and does NOT require SMB signing or enforce HTTPS.
The attack flow:
1. An attacker coerces a machine account (e.g., a Domain Controller) to authenticate to an attacker-controlled machine over HTTP or SMB (using tools like PetitPotam or PrinterBug).
2. The attacker relays this NTLM authentication to the CA's Web Enrollment HTTP interface.
3. Because the Web Enrollment interface accepts NTLM and lacks protections, the attacker successfully authenticates as the coerced victim.
4. The attacker requests a certificate using a default template (like `Machine` or `DomainController`), receiving a client authentication certificate for the victim machine.

**Mitigation via EPA:**
Extended Protection for Authentication (EPA) mitigates this by binding the outer TLS channel (if HTTPS is used) to the inner authentication channel. Specifically, it uses a Service Principal Name (SPN) target name validation and a Channel Binding Token (CBT). If an attacker relays NTLM to an EPA-enforced IIS endpoint, the SPN in the NTLM message will not match the target SPN of the CA web service, or the CBT generated over the TLS session will not match the one expected by the server. Thus, the relayed authentication is rejected. Disabling HTTP and enforcing HTTPS + EPA entirely kills ESC8.

### Q3: What is the purpose of the `NTAuthCertificates` object in Active Directory, and how does it play a role in Golden Certificate attacks?
**Expert Answer:**
The `NTAuthCertificates` object, located in the Configuration naming context (`CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local`), acts as a definitive list of CA certificates that Active Directory trusts for smart card and client certificate-based authentication (PKINIT). When a Domain Controller evaluates a certificate during Kerberos authentication, it verifies that the CA that signed the client's certificate exists in this `NTAuthCertificates` store.

In a **Golden Certificate** attack, the attacker steals the private key of the Enterprise Root CA (or Subordinate CA). With this key, the attacker can forge certificates for any user in the domain. The reason these forged certificates are seamlessly accepted by the DCs is that the stolen CA key is already trusted by the `NTAuthCertificates` object. Even if the actual CA server is taken offline, as long as the CA certificate remains in `NTAuthCertificates`, the forged client certificates will be honored by the DCs for TGT issuance.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You have obtained a valid TGT for a low-privileged user `jdoe`. You run Certify.exe and find a template with `ENROLLEE_SUPPLIES_SUBJECT` enabled, but it requires the `Enrollment Agent` EKU. However, you notice another template that allows any domain user to request an `Enrollment Agent` certificate. Walk through your attack chain.
**Expert Answer:**
This is a classic ESC3 attack chain. The scenario describes a situation where an Enrollment Agent (EA) certificate is required to request a certificate on behalf of another user (often via an "Exchange Enrollment Agent (Offline request)" template).

**Attack Steps:**
1. **Request the EA Certificate:** I will use my low-privileged user `jdoe` to request a certificate from the first vulnerable template that grants the `Enrollment Agent` EKU (let's call it `VulnEA`). 
   `Certify.exe request /ca:CA01.corp.local\Corp-CA /template:VulnEA`
   This outputs a `.pem` file containing the EA certificate and private key.
2. **Convert the EA Certificate:** I convert the PEM to a PFX format using OpenSSL.
   `openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out ea.pfx`
3. **Request the Target Certificate:** Now, I use the `ea.pfx` to sign a CSR for the secondary template (let's call it `VulnLogon`) that requires EA approval, specifying the Enterprise Admin `Administrator` as the target user.
   `Certify.exe request /ca:CA01.corp.local\Corp-CA /template:VulnLogon /onbehalfof:corp\Administrator /pfx:ea.pfx`
4. **Obtain TGT:** I take the resulting PFX for the Administrator account and use Rubeus to request a TGT via PKINIT.
   `Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /password:pfx_password /ptt`
5. **DCSync:** With the TGT loaded in memory, I execute Mimikatz or SecretsDump to DCSync the `krbtgt` hash and achieve full domain compromise.

### Q2: During an assessment, you extract the CA private key from a decommissioned CA server backup. The CA is no longer active, but you want to perform a Golden Certificate attack. What AD attribute must you check to ensure this attack will still work, and what tool do you use to forge the ticket?
**Expert Answer:**
If the CA is decommissioned, I must verify that its public certificate was not removed from the `NTAuthCertificates` object in Active Directory.
**Verification:** I can use PowerShell or LDAP queries to read the `cACertificate` attribute of the `CN=NTAuthCertificates` object in the Configuration partition. If the decommissioned CA's certificate is still present in this blob, the Domain Controllers will still trust certificates signed by its private key for authentication.
**Exploitation:** I will use the `ForgeCert` tool (or specialized scripts like `BofRoast/ForgeCert` or `Certify`) to forge a certificate.
`ForgeCert.exe --CaCert ca.pfx --CaPassword pass --Subject "CN=Administrator" --SubjectAltName administrator@corp.local --NewCert user.pfx --NewPassword userpass`
Once the certificate is forged, I use Rubeus `asktgt` to request the Kerberos TGT. Because the DC checks the `NTAuthCertificates` store and finds the CA cert, it validates the signature on my forged `user.pfx` and grants the ticket.

### Q3: You are attempting an ESC8 NTLM relay against the CA Web Enrollment, but you notice that the HTTP endpoint returns a 401 Unauthorized for NTLM and is prompting for Kerberos negotiation (Negotiate/NTLM is failing, maybe SPNs are strictly enforced). How might you pivot to exploit ESC11 instead?
**Expert Answer:**
ESC11 involves exploiting RPC over TCP or RPC over HTTP for CA enrollment where NTLM relay is possible. If the standard Web Enrollment (ESC8) is hardened, I would look for the CertSrv Request (RPC) interface (MS-ICPR). By default, this RPC interface allows NTLM authentication and does not enforce RPC encrypt/sign, making it vulnerable to relay.
**Attack Steps:**
1. I setup `ntlmrelayx.py` to target the CA server's RPC endpoint. 
   `ntlmrelayx.py -t rpc://<CA_IP> -rpc-mode DCOM --template DomainController`
2. I trigger a machine account authentication (e.g., using `Coerce_auth` or `PetitPotam`) targeting my attacker machine's IP.
3. `ntlmrelayx` receives the NTLM authentication and relays it to the CA's RPC interface.
4. Because the RPC interface does not enforce packet privacy/integrity by default, the CA accepts the relayed authentication and issues a certificate based on the `DomainController` template.
5. I extract the base64-encoded certificate from the output, convert it to PFX, and use PKINIT to obtain a TGT for the coerced machine account.

## Deep-Dive Defensive Questions

### Q1: What specific Event IDs and telemetry should a SOC ingest to detect an ESC1 (SAN abuse) attack in near real-time?
**Expert Answer:**
To comprehensively detect ESC1, the SOC must monitor both the CA server logs and the Domain Controller Kerberos logs.
**On the CA Server:**
*   Audit Object Access -> Audit Certification Services must be enabled.
*   **Event ID 4886 (Certificate Services received a certificate request):** This event logs the initial request. We must parse the `CertificateTemplate` field and the `RequestAttributes` field. If `RequestAttributes` contains `SAN:` with a highly privileged user, it is highly suspicious.
*   **Event ID 4887 (Certificate Services approved and issued a certificate):** This confirms the attack succeeded. The SOC should correlate 4886 and 4887 where the requester identity (e.g., `DOMAIN\jdoe`) differs drastically from the Subject Alternate Name issued (e.g., `administrator@domain.local`).

**On the Domain Controller:**
*   **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested):** When the attacker uses the resulting certificate via PKINIT, the DC logs this event. The SOC should look for `EventData.CertIssuerName` and `EventData.CertSerialNumber`. If these fields are populated, PKINIT was used. A sudden spike in PKINIT authentications for privileged accounts from unusual IP addresses (the attacker's machine) is a strong indicator of compromise.

### Q2: A system administrator proposes disabling NTLM entirely in the environment to mitigate ESC8. Is this sufficient, and what are the operational impacts and edge cases?
**Expert Answer:**
While disabling NTLM entirely (using Network Security: Restrict NTLM policies) is the ultimate mitigation for ESC8 (and all NTLM relay attacks), it is often functionally impossible for legacy environments without breaking production systems.
**Is it sufficient?** Yes, if NTLM is completely disabled, NTLM relay to the HTTP endpoint is impossible. However, an attacker might still attempt Kerberos relay (though much harder, relying on unconstrained delegation or RBCD misconfigurations).
**Operational Impacts:** Disabling NTLM will break legacy applications, IP-based file sharing (which falls back to NTLM), older scanners, non-domain joined devices communicating with domain resources, and certain MSSQL configurations.
**Alternative/Better Mitigation:** Instead of disabling NTLM domain-wide, the administrator should specifically harden the CA Web Enrollment service. This is done by:
1. Enforcing HTTPS on the IIS site.
2. Enabling Extended Protection for Authentication (EPA) in IIS.
3. Disabling HTTP entirely.
4. Removing the Web Enrollment feature if it is not strictly required, as certificate auto-enrollment via RPC is usually sufficient for modern domains.

### Q3: Explain the defensive concept of "Strong Certificate Mapping" introduced by Microsoft to combat AD CS abuses like ESC1, ESC9, and ESC10. How does it change the authentication flow?
**Expert Answer:**
Historically (Weak Mapping), when a user presented a certificate via PKINIT, the Domain Controller solely relied on the `Subject Alternative Name (SAN)` in the certificate to identify the user in Active Directory. Attackers abused this (ESC1, ESC9, ESC10) by injecting arbitrary UPNs into the SAN.

In May 2022 (KB5014754), Microsoft introduced **Strong Certificate Mapping**. This changes the authentication flow by requiring a cryptographically strong binding between the certificate and the AD account.
**How it works:**
1. When a CA issues a certificate, it now includes a new extension: the Object Identifier (OID) `1.3.6.1.4.1.311.25.2` containing the SID of the requesting user.
2. Alternatively, the certificate can be mapped manually using the `altSecurityIdentities` attribute in AD.
3. During PKINIT, the Domain Controller no longer blindly trusts the SAN. It extracts the SID from the OID extension and matches it against the SID of the account attempting to authenticate.
4. If an attacker uses ESC1 to request a certificate as `jdoe` but puts `Administrator` in the SAN, the CA will embed `jdoe`'s SID in the OID. When the attacker tries to authenticate as `Administrator`, the DC sees that the SID in the certificate (`jdoe`) does not match the SID of `Administrator`, and the authentication is immediately rejected (Event ID 39 in KDC logs).

## Real-World Attack Scenario

### The Compromise of "GlobalCorp" via Ghost CA
During an assumed breach engagement at GlobalCorp, the Red Team landed on a developer's workstation via a phishing payload, obtaining the credentials of a standard user, `dev_m.smith`.

The team began AD enumeration using `BloodHound` and `Certify.exe`. The Certify output revealed no obvious vulnerable templates (no ESC1, ESC2, or ESC3). However, a historical audit of the `Configuration` container revealed an old CA entry under `CN=NTAuthCertificates`. GlobalCorp had migrated from Windows Server 2012 to Windows Server 2019 CAs two years prior. They properly stood up the new CA, but they lazily turned off the old CA virtual machine without formally decommissioning it from Active Directory.

The Red Team searched the network file shares and discovered an IT archive share containing an old Acronis backup of the Server 2012 CA. Extracting the backup, the team used `secretsdump.py` against the CA's `NTDS.DIT` and extracted the local machine keys. They then recovered the `pfx` of the old Enterprise Root CA.

Because the old CA was never removed from `NTAuthCertificates`, the DCs still inherently trusted any certificate it signed. The Red Team moved to their attack infrastructure and utilized `ForgeCert`. They forged a client authentication certificate for `krbtgt` and `GlobalCorp\Administrator`. Using `Rubeus asktgt`, they presented the forged certificate. The DC validated the signature against the old CA public key still residing in AD, accepted it, and issued a TGT for the Enterprise Admin. The Red Team achieved complete domain dominance in under 4 hours without exploiting a single live misconfiguration, purely relying on residual cryptographic trust.

## Chaining Opportunities
*   **Coerced Authentication (Module 42):** Tools like PetitPotam, DFSCoerce, or ShadowCoerce are frequently chained with ESC8 to force Domain Controllers to authenticate to the attacker, allowing for NTLM relay to the CA web enrollment.
*   **Pass-the-Ticket (Module 75):** Once a TGT is acquired via PKINIT using a forged or abused certificate, it is injected into memory using Pass-the-Ticket techniques for lateral movement.
*   **Shadow Credentials (Module 83):** AD CS abuses can be used to gain write access over an object, which then allows the attacker to populate the `msDS-KeyCredentialLink` attribute to conduct a Shadow Credentials attack.

## Related Notes
*   [[04 - Active Directory/AD QnA - Module 75 - Kerberos Attacks and Tickets]]
*   [[04 - Active Directory/AD QnA - Module 42 - Coerced Authentication and NTLM Relay]]
*   [[04 - Active Directory/AD QnA - Module 83 - Shadow Credentials and RBCD]]
*   [[04 - Active Directory/AD QnA - Module 80 - Golden Ticket Attacks]]

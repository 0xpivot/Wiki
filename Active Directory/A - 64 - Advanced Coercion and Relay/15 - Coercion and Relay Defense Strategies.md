---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.15 Coercion and Relay Defense Strategies"
---

# 15 - Coercion and Relay Defense Strategies

## Introduction to Defensive Paradigms

The landscape of Active Directory coercion and relay attacks (NTLM Relaying, PetitPotam, Shadow Credentials, DFSCoerce, etc.) is characterized by attackers abusing intended, legacy functionality rather than exploiting traditional memory corruption bugs. Consequently, defending against these attacks requires architectural shifts, aggressive hardening of legacy protocols, and deep visibility into the authentication pipeline.

Defending against coercion and relay attacks is not a single configuration switch. It is a defense-in-depth strategy categorized into three primary pillars:
1. **Preventing Coercion**: Stopping the attacker from forcing an authentication in the first place.
2. **Breaking the Relay**: Ensuring that if an authentication is coerced and intercepted, it cannot be successfully forwarded to and accepted by a target service.
3. **Hardening the Target Object**: Ensuring that even if an attacker successfully relays authentication, the permissions and configuration of the AD environment prevent catastrophic compromise (e.g., DCSync, full domain takeover).

## ASCII Architecture: The Defensive Layers

```text
+-------------------+       LAYER 1: Prevent Coercion       +-------------------+
|                   |   <-------------------------------x   |                   |
|   Attacker Node   |      RPC Filters, Disable Spooler     | Target Server/DC  |
|                   |      Patching (PetitPotam, etc.)      |                   |
+-------------------+                                       +-------------------+
        |
        |
        v
+-------------------+       LAYER 2: Break the Relay        +-------------------+
|                   |   x------------------------------->   |                   |
|   Attacker Node   |      SMB Signing, LDAP Signing,       | Relayed-to Server |
|   (Relay Server)  |      EPA (Channel Binding) Required   | (AD CS, DC, etc.) |
+-------------------+                                       +-------------------+
                                                                    |
                                                                    v
                            LAYER 3: Object Hardening       +-------------------+
                            x--------------------------->   |                   |
                               Tiering, Restrict ACLs       | Victim AD Object  |
                               Protect msDS-KeyCredLink     |                   |
                                                            +-------------------+
```

## Layer 1: Preventing Coercion

The first line of defense is stopping the attacker's ability to trigger the NTLM authentication. Coercion tools rely on specific RPC endpoints.

### 1. Disable Unnecessary Services
Many coercion techniques abuse legacy services running on Domain Controllers and servers.
- **Print Spooler**: The `SpoolSample` (PrinterBug) attack abuses the Print Spooler service (`spoolsv.exe`). **Action**: Disable the Print Spooler service on all Domain Controllers and critical servers where printing is not strictly required.
  ```powershell
  Stop-Service -Name Spooler -Force
  Set-Service -Name Spooler -StartupType Disabled
  ```

### 2. Implement RPC Filters
Tools like `PetitPotam` abuse the Encrypting File System Remote (EFSRPC) protocol. Microsoft provides guidance on using RPC filters to block unauthenticated or unauthorized access to these specific named pipes without disabling the entire service.
- Use `rpcping` and advanced firewall rules to block remote access to the `\pipe\efsrpc`, `\pipe\lsarpc`, `\pipe\samr`, and `\pipe\netdfs` pipes from non-administrative subnets.

### 3. Patching and Updates
Microsoft frequently releases patches addressing specific coercion vulnerabilities (e.g., CVE-2021-36942 for PetitPotam). Ensure rapid deployment of security updates to Domain Controllers. However, patches often only fix specific methods; attackers frequently find alternative undocumented RPC calls. Hence, patching alone is insufficient.

## Layer 2: Breaking the Relay

If an attacker successfully coerces an authentication, the network must be hardened so that the relayed credentials are fundamentally useless.

### 1. Enforce SMB Signing
SMB signing adds a cryptographic signature to every SMB packet, verifying the sender's identity and preventing tampering. If an attacker relays NTLM to an SMB server, they cannot sign the subsequent SMB packets because they do not possess the session key.
- **Action**: Enable and enforce SMB signing on all workstations and servers.
- **GPO Path**: `Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Local Policies -> Security Options`
  - `Microsoft network client: Digitally sign communications (always)`: Enabled
  - `Microsoft network server: Digitally sign communications (always)`: Enabled

### 2. Enforce LDAP Signing and Channel Binding
Relaying to LDAP is a primary vector for RBCD and Shadow Credential attacks.
- **LDAP Signing**: Forces all LDAP traffic to be signed, preventing MitM modification.
  - **GPO**: `Domain controller: LDAP server signing requirements` -> Require signing.
- **LDAP Channel Binding**: Protects LDAPS (LDAP over TLS) from relay attacks.
  - Set the registry key `LdapEnforceChannelBinding` to `2` (Always) on all Domain Controllers.

### 3. Extended Protection for Authentication (EPA)
For web-based services (HTTP/HTTPS) such as Active Directory Certificate Services (AD CS), Exchange, and WSUS, EPA must be enforced.
- **Action**: In IIS Manager, under the authentication settings for the specific application (e.g., `/certsrv`), ensure "Extended Protection" is set to **Required** (not Supported). This completely mitigates ESC8 relay attacks.

### 4. Phasing out NTLM
The ultimate defense against NTLM relay is to stop using NTLM.
- **Audit Mode**: Enable NTLM auditing via GPO (`Network security: Restrict NTLM: Audit NTLM authentication in this domain`) to identify legacy applications relying on it.
- **Restrict NTLM**: Gradually implement rules to block incoming and outgoing NTLM traffic on Domain Controllers and critical servers, forcing negotiation to Kerberos.

## Layer 3: Hardening the Target Object

If an attacker bypasses the first two layers (e.g., finding an unpatched coercion bug and a server missing EPA), the AD architecture itself must resist compromise.

### 1. Account Tiering and Segmentation
Implement the Microsoft Enterprise Access Model (formerly Tier Model). 
- A Tier 0 machine (Domain Controller) should never be allowed to authenticate via NTLM to a Tier 1 or Tier 2 machine. Firewall rules and Authentication Policies should enforce these boundaries, stopping lateral and upward relay attacks.

### 2. Strict ACL Management
Attacks like RBCD and Shadow Credentials require the attacker to have write access (`GenericWrite`, `GenericAll`, `WriteProperty`) to the target object.
- **Action**: Use tools like BloodHound to continuously audit AD permissions. Remove any non-standard write privileges that standard users or compromised service accounts hold over critical computer or user objects.
- Ensure the `msDS-KeyCredentialLink` and `msDS-AllowedToActOnBehalfOfOtherIdentity` attributes are tightly controlled.

### 3. Protected Users Security Group
Add sensitive administrative accounts to the `Protected Users` group.
- Members of this group cannot authenticate using NTLM, and their Kerberos TGTs cannot be delegated. This prevents their credentials from being coerced and relayed.

### 4. Account is Sensitive and Cannot be Delegated
For critical service accounts and high-privileged users, check the box "Account is sensitive and cannot be delegated" in AD. This helps mitigate certain types of unconstrained delegation and relay chains.

## Advanced Detection Mechanisms

Defenders must assume prevention will eventually fail and build robust detection pipelines.

1. **Monitor Event ID 5136 (Directory Service Changes)**: Alert on any unexpected modifications to `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD) or `msDS-KeyCredentialLink` (Shadow Credentials).
2. **Monitor Event ID 4624 (Logon)**: Look for anomalous network logons. Specifically, a workstation or server authenticating to another server (that is not a DC or a file server) using NTLM is highly suspicious.
3. **Honeytokens and Decoys**: Deploy fake high-privileged accounts or fake vulnerable SPNs. Monitor any attempts to coerce authentication from these accounts or relay to them.
4. **Network Traffic Analysis**: Use Zeek or similar network monitoring tools to detect patterns indicative of coercion (e.g., an endpoint opening an RPC pipe to a DC, immediately followed by the DC initiating an NTLM authentication to a third IP address).

## Conclusion

Securing an Active Directory environment against coercion and relay attacks is an ongoing operational requirement. It demands a holistic approach combining protocol deprecation (NTLM), rigorous enforcement of integrity checks (Signing/EPA), and strict least-privilege access control within the directory itself.

## Real-World Attack Scenario

During a purple team exercise, an attacker attempted to execute a classic NTLM relay attack to compromise a Domain Controller. The attacker launched `ntlmrelayx.py` targeting the Active Directory Certificate Services (AD CS) server (`pki.corp.local`) and used `PetitPotam` to coerce the primary Domain Controller (`DC01`) into authenticating to the attacker's IP.

Almost immediately, the Security Operations Center (SOC) received a high-fidelity alert from their EDR and network monitoring tools. The alert indicated that an unprivileged workstation (the attacker's machine) had initiated a raw RPC connection to `\pipe\efsrpc` on `DC01`. Seconds later, a second alert triggered: `DC01` attempted to perform an NTLM network logon (Event ID 4624, Type 3) against the AD CS server, originating from the attacker's IP address rather than `DC01`'s actual IP.

Despite the successful coercion, the attack failed at Layer 2. The organization had proactively implemented strict Extended Protection for Authentication (EPA) and required HTTPS on the AD CS Web Enrollment virtual directory. When `ntlmrelayx` attempted to relay the NTLM authentication without valid Channel Binding Tokens, the IIS server outright rejected the connection, logging an authentication failure.

Following the exercise, the blue team decided to implement Layer 1 defenses to prevent the coercion step entirely. They applied an RPC filter via Windows Filtering Platform (WFP) that restricted access to `\pipe\efsrpc` and `\pipe\lsarpc`, allowing connections only from authorized administrative jump servers and explicitly blocking all standard workstation subnets. 

When the attacker re-attempted the `PetitPotam` coercion, the RPC bind request was silently dropped by the firewall. By successfully layering preventative RPC filters with hard authentication boundaries (EPA), the organization completely neutralized the coercion and relay attack vector without needing to disable legacy services entirely.

## Chaining Opportunities

- This file serves as the defensive counterpart to all attack vectors discussed in Module 64. Understanding the mitigations here directly informs how an attacker must chain bypasses (like dropping the MIC) to defeat specific layers of this defensive architecture.

## Related Notes
- [[11 - Shadow Credentials - MSDS-KeyCredentialLink]]
- [[12 - Drop-the-MIC - Bypassing NTLM MIC]]
- [[13 - EPA Extended Protection Bypasses]]
- [[14 - Relay across Forest Trusts]]
- [[02 - NTLM Relay Attacks Deep Dive]]

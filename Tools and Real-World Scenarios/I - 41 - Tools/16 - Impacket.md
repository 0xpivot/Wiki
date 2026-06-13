---
tags: [tools, vapt, utility, impacket, network, lateral-movement]
difficulty: intermediate
module: "41 - Tools"
topic: "41.16 Impacket"
---

# Impacket: The Swiss Army Knife of Network Protocol Manipulation

## 1. Overview and Introduction

Impacket is a collection of Python classes for working with network protocols. Developed by SecureAuth Corp (and heavily maintained by the community), it provides low-level, programmatic access to the packets and protocols used heavily in Microsoft Windows environments. 

For penetration testers, red teamers, and API security researchers (Module 31), Impacket is arguably the most critical tool for post-exploitation, lateral movement, and Active Directory manipulation. Rather than relying on native Windows binaries (which are heavily monitored by EDRs), Impacket allows attackers to interact with Windows APIs and RPC endpoints directly over the network from a Linux machine.

## 2. Core Capabilities and Protocol Support

Impacket implements several key protocols from scratch:
- **Ethernet, IP, TCP, UDP, ICMP, IGMP, ARP** (Low-level networking)
- **SMB1, SMB2, SMB3** (Server Message Block for file sharing and IPC)
- **MSRPC / DCERPC** (Microsoft Remote Procedure Call - the backbone of Windows administration)
- **NTLM and Kerberos** (Authentication protocols)
- **TDS** (MS SQL Server protocol)
- **LDAP** (Lightweight Directory Access Protocol)

By manipulating these protocols, Impacket scripts can perform actions that typically require proprietary Microsoft tools.

## 3. Architecture Diagram

### 3.1 Custom ASCII Architecture Diagram

```text
+-------------------------------------------------------+
|                 Impacket Protocol Stack               |
+-------------------------------------------------------+
|  +-------------------------------------------------+  |
|  |             Attacker Python Script              |  |
|  |        (e.g., secretsdump.py, psexec.py)        |  |
|  +-----------------------+-------------------------+  |
|                          |                            |
|                          v                            |
|  +-------------------------------------------------+  |
|  |                 Impacket Core                   |  |
|  |             (DCERPC, SMB, WMI, TDS)             |  |
|  +-----------------------+-------------------------+  |
|                          |                            |
|                          v                            |
|  +-------------------------------------------------+  |
|  |                Network Layer                    |  |
|  |               (TCP / UDP / IP)                  |  |
|  +-----------------------+-------------------------+  |
|                          |                            |
|                          v                            |
|  +-------------------------------------------------+  |
|  |                Target System                    |  |
|  |            (Windows AD / File Server)           |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
```

## 4. Deep Dive into Notable Scripts

Impacket ships with dozens of example scripts that have become industry standards.

### 4.1 secretsdump.py
Performs various techniques to dump secrets from the remote machine without executing any agent there.
- Extracts local SAM and LSA secrets via remote registry reading.
- Extracts NTDS.dit (Active Directory hashes) via DCSync (using `DRSUAPI`).

**Example Usage (DCSync):**
```bash
impacket-secretsdump domain.local/admin:password@10.10.10.10 -just-dc
```
*Note: This utilizes the Directory Replication Service (DRS) Remote Protocol API to simulate a domain controller requesting replication.*

### 4.2 psexec.py
A Python implementation of Sysinternals PsExec. It creates a semi-interactive shell.
- Connects to the `ADMIN$` share via SMB.
- Uploads a randomly named executable.
- Uses DCERPC `SVCCTL` to create a Windows service that runs the executable.
- Binds named pipes for stdin/stdout/stderr.

**Example Usage (Pass-the-Hash):**
```bash
impacket-psexec -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 Administrator@10.10.10.20
```

### 4.3 wmiexec.py
A stealthier alternative to `psexec.py`. It uses Windows Management Instrumentation (WMI) to execute commands.
- Connects to WMI via DCOM (Distributed Component Object Model).
- Executes commands using the `Win32_Process` class.
- Writes output to a temporary file on the `ADMIN$` share and reads it back via SMB.
- *Advantage:* Does not create a new service, bypassing many basic EDR detections.

**Example Usage:**
```bash
impacket-wmiexec domain/user:pass@10.10.10.30
```

### 4.4 smbexec.py
A similar approach to psexec but without uploading an executable. It instantiates a temporary service with the command to be executed (using `%COMSPEC%`) and outputs the result to a temp file.

### 4.5 ntlmrelayx.py
The crown jewel of Impacket for lateral movement. It sets up an SMB and HTTP server to capture NTLM authentication attempts and relays them to a target of the attacker's choosing.

**Example Usage (Relaying to LDAP to create a Domain Admin):**
```bash
impacket-ntlmrelayx -t ldap://domain_controller -smb2support --escalate-user attacker
```

## 5. API Integration and Custom Tooling (Module 31 Focus)

While the pre-built scripts are excellent, Impacket's true power lies in its Python API. Security researchers can import Impacket to build custom RPC clients, manipulate API endpoints over named pipes, or craft bespoke SMB packets to exploit zero-days (e.g., EternalBlue, PetitPotam).

**Building a custom DCERPC client:**
```python
from impacket.dcerpc.v5 import transport, rpcrt, scmr

# Connect to the Service Control Manager API
stringBinding = r'ncacn_np:10.10.10.10[\pipe\svcctl]'
rpctransport = transport.DCERPCTransportFactory(stringBinding)
rpctransport.set_credentials('admin', 'password', 'domain', '', '')

dce = rpctransport.get_dce_rpc()
dce.connect()
dce.bind(scmr.MSRPC_UUID_SCMR)

# Execute API calls...
```

## 6. Detection and OPSEC Considerations

Impacket is highly fingerprinted by modern security solutions.

### 6.1 OPSEC
- `psexec.py` uploads a binary. This is instantly flagged by Defender and EDRs.
- `wmiexec.py` leaves forensic artifacts in the Windows Event Logs (Event ID 4688 with `cmd.exe /Q /c ...` and `127.0.0.1` redirection).
- Relaying attacks generate anomalous network traffic patterns.

### 6.2 Detection Strategies
- **Network Traffic:** Monitor for anomalous DCERPC binds (e.g., `drsuapi` from non-DC IPs indicates DCSync).
- **Event Logs:** Monitor for service creation (Event ID 7045) with random alphanumeric names (default `psexec.py` behavior).
- **Named Pipes:** Monitor for unexpected SMB named pipe connections (`\pipe\svcctl`, `\pipe\atsvc`).

## 7. Mitigation Strategies

1.  **Disable NTLM:** Enforce Kerberos-only authentication where possible to mitigate NTLM relay attacks.
2.  **SMB Signing:** Enforce SMB signing across all hosts (not just Domain Controllers) to prevent SMB relaying.
3.  **LDAP Signing and Channel Binding:** Prevent NTLM relaying to LDAP.
4.  **Endpoint Detection and Response (EDR):** Deploy EDR to catch anomalous WMI execution, process injection, and unexpected service creation.

## 8. Conclusion

Impacket remains the foundational library for attacking Windows networks. Its deep understanding of Microsoft protocols allows attackers to leverage native administrative APIs against the target environment. Mastery of Impacket separates script kiddies from advanced operators.

---

## Chaining Opportunities
- **[[17 - Responder]]:** Use Responder to poison LLMNR/NBT-NS and force a victim to authenticate to your IP. Use Impacket's `ntlmrelayx.py` to relay that authentication to a critical server.
- **[[15 - BloodHound]]:** Use BloodHound to identify an administrator session, then use Impacket's `wmiexec.py` to move laterally to that box.
- **[[18 - Mimikatz]]:** After gaining a shell via Impacket, execute Mimikatz to dump memory, or use `secretsdump.py` as a remote alternative to Mimikatz's DCSync module.

## Related Notes
- [[05 - Windows API Abuse]]
- [[06 - MSRPC Internals]]
- [[07 - SMB and NTLM Authentication]]

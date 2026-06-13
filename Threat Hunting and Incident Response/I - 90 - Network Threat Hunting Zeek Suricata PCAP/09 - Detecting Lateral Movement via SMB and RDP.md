---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.09 Detecting Lateral Movement via SMB and RDP"
---

# 90.09 Detecting Lateral Movement via SMB and RDP

## 1. Introduction to Lateral Movement

Once an adversary establishes an initial foothold within a network (e.g., via phishing, an external exploit, or a web shell), their primary objective shifts to lateral movement. The goal is to traverse the network, escalate privileges, locate high-value assets (like Active Directory Domain Controllers, sensitive databases, or intellectual property), and deploy payloads (like ransomware or data collectors) widely across the enterprise.

In Windows environments, the two most ubiquitous administrative protocols—**Server Message Block (SMB)** and **Remote Desktop Protocol (RDP)**—are heavily abused for lateral movement. Because these protocols are essential for legitimate administrative tasks, detecting malicious abuse requires distinguishing anomalous behavior from normal IT operations.

## 2. Lateral Movement Architecture and Mechanics

```text
    +-------------------+                     +-------------------+
    |                   |  1. Pass-the-Hash   |                   |
    | Compromised Host  |  over SMB (Port 445)| Target Server     |
    | (10.0.1.50)       | ==================> | (10.0.1.100)      |
    |                   |                     |                   |
    +-------------------+                     +-------------------+
             |                                          |
             | 2. Deploy PsExec Service                 | 3. Execute payload
             |    (Write to ADMIN$)                     |    (e.g., ransomware)
             v                                          v
    +-------------------+                     +-------------------+
    |                   |                     |                   |
    | RDP Brute Force / |  4. RDP Session     | High-Value Target |
    | Hijacking         |  (Port 3389)        | (Domain Control.) |
    |                   | ==================> | (10.0.0.5)        |
    +-------------------+                     +-------------------+
```

### 2.1 Abuse of SMB (Server Message Block)
SMB (typically on TCP 445) is used for file sharing, IPC (Inter-Process Communication), and remote administration. Attackers abuse SMB via:
- **PsExec / WMI:** Legitimate Microsoft tools used to execute commands on remote systems. PsExec uploads a binary to the `ADMIN$` share and binds it to a named pipe (e.g., `\pipe\svcctl`) to execute it.
- **Pass-the-Hash (PtH):** Authenticating to SMB using an NTLM hash extracted from LSASS memory, bypassing the need for a plaintext password.
- **SMB Relay:** Intercepting an SMB authentication request and relaying it to a target server to gain unauthorized access.

### 2.2 Abuse of RDP (Remote Desktop Protocol)
RDP (TCP/UDP 3389) provides graphical access. Attackers abuse RDP via:
- **Credential Stuffing / Brute Forcing:** Attempting thousands of logins.
- **RDP Hijacking:** Taking over an existing, disconnected RDP session (often the SYSTEM or Admin session) using tools like `tscon.exe`.
- **RDP Tunneling:** Encapsulating RDP traffic inside an SSH or HTTP tunnel to bypass network segmentation firewalls.

## 3. Threat Hunting with Zeek

Zeek parses SMB and RDP traffic extensively, logging transaction metadata into `smb_files.log`, `smb_mapping.log`, `dce_rpc.log`, and `rdp.log`.

### 3.1 Hunting Malicious SMB and PsExec
A classic indicator of PsExec lateral movement is an administrative share mapping followed by an executable write and an RPC call.

```bash
# Search smb_mapping.log for connections mapping to the IPC$ or ADMIN$ hidden shares
cat smb_mapping.log | zeek-cut id.orig_h id.resp_h path | grep -E "IPC\$|ADMIN\$"
```

When PsExec runs, it transfers an executable. We can hunt for `.exe` or `.dll` files being transferred over SMB in `smb_files.log`:
```bash
cat smb_files.log | zeek-cut id.orig_h id.resp_h name action | grep "\.exe"
```

### 3.2 Hunting Anomalous RDP Sessions
A massive volume of RDP connections from a single IP to multiple internal IP addresses indicates scanning or lateral movement behavior (e.g., BloodHound/SharpHound mapping followed by RDP probing).

```bash
# Count RDP connections per source IP in rdp.log
cat rdp.log | zeek-cut id.orig_h id.resp_h | awk '{print $1}' | sort | uniq -c | sort -nr | head -n 10
```

Additionally, analyzing the `keyboard_layout` field in `rdp.log` can be a high-fidelity IoC. If your enterprise uses US English keyboards, and you suddenly see an RDP connection with a Russian (`0x00000419`) keyboard layout, it is highly suspect.

## 4. Threat Hunting with Suricata

Suricata provides deep protocol inspection capabilities to write precise rules for lateral movement techniques.

### 4.1 Suricata Rule for PsExec Lateral Movement
This rule looks for the specific Named Pipe used by PsExec (`PSEXESVC`).

```suricata
alert smb any any -> $HOME_NET any (msg:"ET HUNTING Possible PsExec Lateral Movement (PSEXESVC Named Pipe)"; flow:established,to_server; content:"|50 00 53 00 45 00 58 00 45 00 53 00 56 00 43|"; nocase; distance:0; classtype:suspicious-filename-detect; sid:4040001; rev:1;)
```

### 4.2 Suricata Rule for RDP Brute Force
This rule detects multiple excessive connection attempts over RDP in a short timeframe.

```suricata
alert tcp $HOME_NET any -> $HOME_NET 3389 (msg:"ET SCAN RDP Brute Force Attempt"; flow:established,to_server; content:"|03 00 00|"; depth:3; threshold: type both, track by_src, count 20, seconds 60; classtype:attempted-admin; sid:4040002; rev:1;)
```

## 5. Threat Hunting with PCAP and Wireshark

When diving into PCAPs for SMB/RDP anomalies, specific filters help cut through the noise.

### 5.1 Wireshark SMB Filters
- Find administrative share access: `smb2.tree == "\\\\10.0.1.100\\ADMIN$"`
- Find specific named pipe access (RPC binding): `dcerpc.endpoint == "svcctl"`
- Detect file creations over SMB: `smb2.cmd == 5` (Create) AND `smb2.filename contains ".exe"`

### 5.2 Wireshark RDP Filters
Because RDP payload is encrypted, hunters look at the initial negotiation phases (CredSSP, X.224).
- Look for RDP Negotiation Request packets: `rdp.neg_type == 1`
- Filter for specific RDP cookies (often used by attackers to route connections through load balancers): `rdp.cookie == "mstshash=Administrator"`

## 6. Real-World Attack Scenario

### 6.1 NotPetya and EternalBlue (MS17-010)
The NotPetya wiper malware (2017) demonstrated the most devastating use of lateral movement in history. 
Once a single machine in a network was infected, NotPetya used a two-pronged approach to spread laterally at blinding speed.

**Attack Flow:**
1. **Exploitation:** The malware scanned the local subnet (TCP 445) and utilized the EternalBlue exploit to execute kernel-level shellcode on vulnerable machines.
2. **Credential Theft:** Simultaneously, it extracted NTLM hashes and plaintext credentials from LSASS memory using a bundled Mimikatz module.
3. **Legitimate Abuse:** Armed with credentials, it used `PsExec` and `WMIC` to legitimately log into patched machines, drop its payload to the `ADMIN$` share, and execute it.

Network hunters analyzing the PCAPs during the outbreak saw massive spikes in SMBv1 Trans2 requests (EternalBlue exploit signature) immediately followed by thousands of `smb2.tree == ADMIN$` connections using stolen credentials. The combined abuse of an exploit and native administrative tools meant that patching EternalBlue alone did not stop the propagation.

## 7. Advanced Evasion Techniques
- **Renaming PsExec:** Attackers routinely rename `psexec.exe` to blend in (e.g., `svchost.exe`). Defenders must look at the Named Pipe (`\pipe\psexecsvc`) rather than just the file name.
- **WMI over SMB:** Using Windows Management Instrumentation (WMI) leaves significantly fewer network footprints than PsExec, avoiding the drop of an executable on the `ADMIN$` share and executing commands directly in memory.
- **Network Segmentation Bypasses:** Attackers use tools like `ngrok` or `Chisel` to tunnel RDP traffic over port 443, making it look like normal HTTPS web browsing to the firewall.

## 8. Incident Response Playbook

1. **Identification:**
   - Detect anomalous source-to-destination SMB mappings (e.g., a receptionist PC connecting to the `ADMIN$` share of the Domain Controller).
   - Review Windows Event Logs (Event ID 4624/4625 for Logon, Event ID 7045 for Service Creation) to corroborate network alerts.
2. **Containment:**
   - Deploy host-based firewalls (Windows Defender Firewall) to immediately block lateral SMB/RDP traffic between workstations.
   - Isolate the source machine generating the scanning/lateral movement attempts.
3. **Eradication:**
   - Force a global password reset for any compromised accounts (especially Service Accounts or Domain Admins) used in the Pass-the-Hash attacks.
   - Delete any malicious services created by PsExec (e.g., `sc delete PSEXESVC`).
4. **Recovery:**
   - Implement Microsoft's Local Administrator Password Solution (LAPS) to prevent future Pass-the-Hash lateral movement.
   - Enforce multi-factor authentication (MFA) on all RDP connections.

## 9. Chaining Opportunities
- Attackers moving laterally via SMB often drop staging files or web shells on internal IIS servers. Pivot to [[10 - Hunting for Web Shells in HTTP Traffic]] to hunt for backdoors placed during lateral movement.
- If lateral movement traffic is communicating with an external IP, the attacker may be tunneling RDP over TLS. Pivot to [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]].
- Check if compromised hosts are resolving strange domains. Pivot to [[06 - Detecting Domain Generation Algorithms DGAs]].

## 10. Related Notes
- [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]]
- [[10 - Hunting for Web Shells in HTTP Traffic]]
- [[06 - Detecting Domain Generation Algorithms DGAs]]

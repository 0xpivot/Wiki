---
tags: [tools, network, poisoning, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.61 Responder All Modes and Config"
---

# 61 - Responder All Modes and Config

## 1. Executive Summary

Responder is the premier network exploitation tool designed specifically to capture, poison, and relay NetBIOS (NBT-NS), LLMNR (Link-Local Multicast Name Resolution), and mDNS (Multicast DNS) broadcast queries. In modern Active Directory environments, Windows endpoints inherently trust local network broadcast queries to resolve hostnames when DNS fails. Responder exploits this fallback mechanism by answering these queries with its own IP address, forcing the victim to authenticate to the attacker's machine. By doing so, it captures NTLMv1/NTLMv2 hashes that can be cracked offline or relayed to other hosts.

## 2. Core Concepts & Underlying Protocols

To understand Responder deeply, one must grasp the underlying resolution protocols Windows uses when standard DNS fails to resolve a hostname.

### LLMNR (Link-Local Multicast Name Resolution)
- **Port:** UDP 5355
- **Mechanism:** Operates on multicast address `224.0.0.252` (IPv4) or `FF02::1:3` (IPv6). When a Windows machine searches for a hostname (e.g., `\\FILESHARE`), and DNS fails, it sends an LLMNR query to the local subnet.
- **Exploitation:** Responder listens on multicast and instantly responds: "I am FILESHARE, connect to me."

### NBT-NS (NetBIOS Name Service)
- **Port:** UDP 137
- **Mechanism:** An older fallback protocol using broadcast address (e.g., `192.168.1.255`). Functions similarly to LLMNR but is legacy and primarily supports IPv4.
- **Exploitation:** Responder intercepts the UDP broadcast and answers the query.

### WPAD (Web Proxy Auto-Discovery)
- **Mechanism:** Browsers are often configured to "Automatically detect settings". They search for a file named `wpad.dat` by querying the hostname `wpad`.
- **Exploitation:** Responder spoofs the `wpad` resolution, acts as the HTTP server hosting a malicious `wpad.dat`, and configures the victim's browser to route all traffic through the attacker's proxy, demanding authentication (HTTP 407 Proxy Authentication Required).

## 3. Architecture & Attack Flow Diagram

```text
[Victim Windows Host]                      [Attacker (Responder)]                       [Target Server]
         |                                           |                                         |
         |--- 1. DNS Query "FS01" (Fails) ---------->| [DNS Server ignores/fails]              |
         |                                           |                                         |
         |--- 2. LLMNR Query "FS01" (Multicast) ---->|                                         |
         |                                           |                                         |
         |<-- 3. LLMNR Response: "I am FS01" --------|                                         |
         |                                           |                                         |
         |--- 4. SMB Negotiate (Port 445) ---------->|                                         |
         |                                           |                                         |
         |<-- 5. SMB Challenge (NTLM Auth) ----------|                                         |
         |                                           |                                         |
         |--- 6. SMB Auth (NTLMv2 Hash) ------------>| (Hash Captured for Cracking)            |
         |                                           |                                         |
         |    [If Relaying is Configured]            |-- 7. NTLM Relay (SMB/HTTP/LDAP) ------->|
         |                                           |<-- 8. Challenge ------------------------|
         |                                           |-- 9. Forwards Victim's Response ------->|
         |                                           |<-- 10. Access Granted / Pwned ----------|
```

## 4. Deep Dive: Key Modes and Options

Responder supports multiple operational modes and allows granular control over which services to spoof.

### Basic Execution
```bash
sudo responder -I eth0
```
This starts Responder on the `eth0` interface with default settings, listening for LLMNR, NBT-NS, and mDNS, and starting all rogue servers (SMB, HTTP, HTTPS, SQL, FTP, etc.).

### Command Line Flags
| Flag | Description | Deep Dive / OPSEC Use Case |
|------|-------------|----------------------------|
| `-I` | Interface   | Specify the network interface (e.g., `eth0`, `tap0`). Mandatory. |
| `-i` | IP Address  | Specify the IP to use. Useful if interface has multiple IPs or routing is complex. |
| `-A` | Analyze     | Analyze mode. Passively listens and maps out LLMNR/NBT-NS requests without poisoning. *Crucial for OPSEC to gauge noise before attacking.* |
| `-w` | WPAD Proxy  | Start the WPAD rogue proxy server. Extremely effective against browser traffic. |
| `-r` | NBT-NS      | Enable answers for NetBIOS wlan/domain queries. |
| `-d` | DHCP        | Enable answers for DHCP broadcast requests (rogue DHCP server). |
| `-P` | Proxy Auth  | Force NTLM authentication for the proxy server. |
| `-v` | Verbose     | Shows detailed hash captures and protocol interactions. |

### Analyze Mode (`-A`)
Always run Analyze mode first in stealth-heavy engagements to assess what hosts are broadcasting.
```bash
sudo responder -I eth0 -A
```
This will build a profile of the subnet without actively poisoning any responses.

### WPAD Exploitation (`-wF`)
```bash
sudo responder -I eth0 -w -F
```
Forces WPAD proxy authentication. Whenever a user opens a browser, they are met with a proxy login prompt or seamless auth, capturing the hash over HTTP.

## 5. Configuration File Breakdown (`Responder.conf`)

The power of Responder lies in its configuration file, typically found at `/etc/responder/Responder.conf` or `/usr/share/responder/Responder.conf`.

### Server Configuration
You can toggle which rogue services Responder spins up. When relaying hashes with `ntlmrelayx.py`, you **MUST** turn off the SMB and HTTP servers in Responder to avoid port conflicts.

```ini
[Responder Core]
; Servers to start
SQL = On
SMB = Off      ; Turn OFF if relaying SMB with ntlmrelayx
RDP = On
Kerberos = On
FTP = On
POP = On
SMTP = On
IMAP = On
HTTP = Off     ; Turn OFF if relaying HTTP with ntlmrelayx
HTTPS = On
DNS = On
LDAP = On
```

### Advanced Settings
```ini
; Challenge setting
Challenge = 1122334455667788
```
By setting a static challenge, captured NTLMv1 hashes can be subjected to advanced cracking techniques or Rainbow Table lookups. If NTLMv1 is enforced, an attacker can guarantee breaking the hash to retrieve the NTLM hash directly.

## 6. Offline Cracking Strategies

Once Responder captures hashes, they are stored in `/usr/share/responder/logs/`.
The hashes usually look like this:
`admin::DOMAIN:challenge:hash1:hash2`

Use Hashcat to crack NTLMv2:
```bash
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```
- `-m 5600`: NetNTLMv2
- `-m 5500`: NetNTLMv1

## 7. OPSEC & Evasion

1. **Network Disruption**: Responder can cause legitimate network disruption. If it answers queries for real servers that are temporarily slow, legitimate users will be redirected to the attacker machine, breaking functionality.
2. **Detection via Honeypots**: Blue teams often deploy LLMNR honeypots that constantly query fake names. If you respond, your MAC/IP is immediately flagged. Analyze mode (`-A`) helps map out these automated queries (they look like random string queries occurring exactly every X seconds).
3. **Pcap Generation**: Responder creates PCAPs of captured traffic in the logs directory. Be mindful of disk space during long-running engagements on noisy networks.

## 8. Detection & Mitigation (Blue Team)

### Mitigations
1. **Disable LLMNR/NBT-NS**: The only effective mitigation.
   - GPO for LLMNR: `Computer Configuration -> Administrative Templates -> Network -> DNS Client -> Turn off multicast name resolution` (Set to Enabled).
   - NBT-NS: Disable via DHCP scope options (Option 43/Vendor Specific) or manually on network adapters.
2. **WPAD DNS Entry**: Create a legitimate static DNS entry for `wpad` pointing to the corporate proxy, or a sinkhole, to prevent broadcast fallback.
3. **SMB Signing**: Require SMB signing globally to prevent NTLM relay attacks from SMB to SMB.
4. **LDAP Signing**: Enforce LDAP signing and LDAP Channel Binding to prevent NTLM relaying to Domain Controllers.

### Detection
- Monitor for UDP 5355 and UDP 137 traffic.
- Detect unsolicited ARP/DNS responses mapping to a single IP.
- Alert on HTTP 407 Proxy Authentication requests internally where proxies are not configured.

## 9. Chaining Opportunities

- **Relaying to ntlmrelayx**: Turn off SMB and HTTP in `Responder.conf`, run Responder, and simultaneously run `ntlmrelayx.py -tf targets.txt -smb2support`. The hashes captured by Responder's LLMNR/NBT-NS poisoning are relayed to execute code or dump SAM databases on target machines. See [[60 - Impacket ntlmrelayx Deep Dive]].
- **NTLMv1 to NTLM Downgrade**: If NTLMv1 is captured with a known challenge (`1122334455667788`), use `crack.sh` or local Rainbow Tables to obtain the raw NTLM hash, enabling Pass-the-Hash against the entire domain via tools like [[62 - Mimikatz All Modules]].
- **IPv6 DNS Takeover (mitm6)**: If IPv4 protections are in place, chain Responder's HTTP/SMB servers with `mitm6`, which poisons DHCPv6 to achieve the exact same result bypassing IPv4 mitigations. See [[66 - mitm6 IPv6 Spoofing]].

## 10. Related Notes

- [[60 - Impacket ntlmrelayx Deep Dive]]
- [[62 - Mimikatz All Modules]]
- [[65 - hashcat Full Mode and Rule Reference]]
- [[66 - mitm6 IPv6 Spoofing]]
- [[21 - Network Layer Attacks]]

---
tags: [tools, vapt, utility, networking, poisoning, ntlm]
difficulty: intermediate
module: "41 - Tools"
topic: "41.17 Responder"
---

# Responder: Dominating Local Area Networks via Protocol Poisoning

## 1. Overview and Introduction

Responder is a wildly successful network exploitation tool created by Laurent Gaffié. It is an LLMNR, NBT-NS, and MDNS poisoner, equipped with built-in rogue authentication servers (HTTP, SMB, MSSQL, FTP, LDAP). 

When a user or automated API service in a Windows environment attempts to resolve a hostname that DNS cannot find (e.g., due to a typo like `\\fileservr` instead of `\\fileserver`), the Windows machine falls back to broadcast protocols. Responder listens for these broadcast queries, falsely claims to be the requested machine, and forces the victim to authenticate to it, capturing their NTLMv1 or NTLMv2 hash.

In the context of API Security (Module 31), backend APIs often attempt to reach internal microservices or database hostnames. If these hostnames are misconfigured or fail DNS resolution, the server running the API may broadcast its service account credentials to the local network, which Responder can capture.

## 2. The Name Resolution Fallback Mechanism

To understand Responder, one must understand how Windows resolves names:
1.  **Local Hosts File:** Checks `C:\Windows\System32\drivers\etc\hosts`.
2.  **DNS Cache:** Checks local DNS cache (`ipconfig /displaydns`).
3.  **DNS Server:** Queries the configured DNS server.
4.  **LLMNR (Link-Local Multicast Name Resolution):** Multicasts to `224.0.0.252` on UDP port 5355.
5.  **NBT-NS (NetBIOS Name Service):** Broadcasts to the local subnet on UDP port 137.

Responder exploits steps 4 and 5. It sits on the network, waits for a multicast/broadcast query for a failed DNS lookup, and immediately responds: *"Yes, I am `fileservr`, connect to me!"*

## 3. Architecture and Attack Flow Diagram

### 3.1 Custom ASCII Attack Diagram

```text
+-------------------------------------------------------+
|                  Responder Attack Flow                |
+-------------------------------------------------------+
|                                                       |
|  +-----------------+           +-------------------+  |
|  |  Victim Client  |           | Attacker System   |  |
|  | (Typo Domain)   |           | (Responder.py)    |  |
|  +-------+---------+           +---------+---------+  |
|          |                               |            |
|          | 1. LLMNR Query (fileservr)    |            |
|          +------------------------------>|            |
|          |                               |            |
|          | 2. Poisoned Response (I am!)  |            |
|          |<------------------------------+            |
|          |                               |            |
|          | 3. SMB Auth (NTLMv2 Hash)     |            |
|          +------------------------------>|            |
|          |                               |            |
|          | 4. Hash Captured to Logs      |            |
|          |                               v            |
|          |                     +-------------------+  |
|          |                     |   Hashcat / JtR   |  |
|          |                     +-------------------+  |
|          |                               |            |
+----------+-------------------------------+------------+
```

## 4. Key Features and Modules

Responder is highly configurable via its `Responder.conf` file. It spins up multiple rogue servers to handle incoming connections.

### 4.1 Rogue Servers
- **SMB Server:** Captures hashes from file share access attempts (`\\server\share`).
- **HTTP Server:** Captures hashes from web requests, often leveraging WPAD (Web Proxy Auto-Discovery).
- **MSSQL Server:** Captures hashes from SQL Server Management Studio or backend API database connections.
- **FTP/POP3/IMAP Servers:** Captures cleartext credentials from legacy protocols.

### 4.2 WPAD Exploitation
Windows devices are configured by default to automatically detect proxy settings. They do this by looking for a host named `WPAD`.
Responder poisons this request, provides a malicious `wpad.dat` proxy configuration file, and routes all the victim's HTTP traffic through the attacker's machine. When the victim browses the web, Responder prompts them for authentication, capturing their hash.

## 5. Typical Usage and Command Execution

**Basic Poisoning on an Interface:**
```bash
sudo responder -I eth0
```

**Analyze Mode (Passive):**
To passively listen to the network without poisoning (useful for OPSEC to map the environment first):
```bash
sudo responder -I eth0 -A
```

**Disabling SMB and HTTP for Relaying:**
If you intend to use `ntlmrelayx.py` in conjunction with Responder, you MUST turn off Responder's built-in SMB and HTTP servers so they don't bind to those ports. Edit `Responder.conf`:
```ini
[Responder Core]
SMB = Off
HTTP = Off
```
Then start Responder and run Impacket's relay script on the side.

## 6. Anatomy of an NTLMv2 Hash

When Responder captures a hash, it looks like this:
```text
admin::DOMAIN:1122334455667788:AABBCCDDEEFF00112233445566778899:0101000000...
```
- **Username:** `admin`
- **Domain:** `DOMAIN`
- **Challenge:** `1122334455667788` (The 8-byte challenge sent by Responder's rogue server).
- **HMAC-MD5:** The cryptographic response generated by the victim's password hash.

This captured value cannot be "Passed" (Pass-the-Hash requires the actual NT hash). It must either be relayed or cracked offline using a tool like Hashcat.

## 7. Detection and OPSEC

### 7.1 OPSEC
Responder is extremely noisy. As soon as it is turned on, it spews LLMNR and NBT-NS responses across the broadcast domain. Network Intrusion Detection Systems (NIDS) easily detect this anomaly.

### 7.2 Detection Mechanisms
- **Network Baselines:** Look for hosts responding to a high volume of LLMNR queries for diverse hostnames.
- **Duplicate Name Resolution:** Alert when a host that is not a known DNS server begins answering name queries.
- **Honey Tokens:** Create a script that periodically queries a non-existent hostname (e.g., `\\fake-server-do-not-use`). If an SMB connection is established, an attacker is running a poisoner on the network.

## 8. Defenses and Mitigation

Mitigating Responder is straightforward but requires network-wide group policy changes.
1.  **Disable LLMNR:** Via Group Policy (`Computer Configuration > Administrative Templates > Network > DNS Client > Turn off multicast name resolution`).
2.  **Disable NBT-NS:** Via DHCP Scope options or network adapter properties.
3.  **Disable WPAD:** Disable "Automatically detect settings" in Internet Explorer/Edge proxy configurations.
4.  **Enforce SMB Signing:** Prevents attackers from relaying the captured authentication to another machine.
5.  **Strong Passwords:** If hashes are captured, long and complex passwords prevent offline cracking via Hashcat.

## 9. Conclusion

Responder exploits a fundamental flaw in how Windows handles failure. By abusing legacy broadcast protocols designed for network convenience, an attacker can rapidly escalate privileges on a local network. It is almost always the first tool executed by a penetration tester upon gaining internal network access.

---

## Chaining Opportunities
- **[[16 - Impacket]]:** After turning off SMB/HTTP in `Responder.conf`, use Responder to poison the network and drive victim traffic to Impacket's `ntlmrelayx.py`. Relay this traffic to a Domain Controller (over LDAP/SMB) to dump the NTDS.dit or create a new Domain Admin.
- **[[20 - Hashcat]]:** Take the NetNTLMv2 hashes captured by Responder and crack them offline using Hashcat (Mode 5600) to retrieve plaintext passwords.
- **[[15 - BloodHound]]:** Use the cracked plaintext credentials to run SharpHound and map the Active Directory environment.

## Related Notes
- [[08 - NTLM Relay Attacks]]
- [[09 - Windows Name Resolution]]
- [[10 - Broadcast Protocol Abuse]]

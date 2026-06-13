---
tags: [active-directory, llmnr, nbt-ns, poisoning, responder, mitm]
difficulty: intermediate
module: "36 - Active Directory Attacks"
topic: "36.14 LLMNR / NBT-NS Poisoning"
---
# 36.14 LLMNR / NBT-NS Poisoning

## 1. Introduction & Theory
In Microsoft Windows environments, when a system attempts to resolve a hostname to an IP address, it follows a specific sequence of protocols. If the primary method (DNS) fails, Windows falls back to legacy broadcast and multicast protocols to ask the local network for help. The two most common fallback protocols are **LLMNR** (Link-Local Multicast Name Resolution) and **NBT-NS** (NetBIOS Name Service).

- **LLMNR:** Introduced in Windows Vista, it operates over UDP port 5355 using multicast (IPv4 224.0.0.252 or IPv6 FF02::1:3).
- **NBT-NS:** A legacy protocol from the 1980s, it operates over UDP port 137 using network broadcasts.
- **mDNS:** Multicast DNS (UDP 5353) is also often utilized by Apple devices and modern Windows 10/11 systems.

Because these protocols are unauthenticated and rely on broadcast/multicast requests to the entire local subnet, they are inherently vulnerable to spoofing. An attacker on the same local network can listen for these queries and aggressively respond, claiming to be the requested resource. 

When the victim machine receives the spoofed response, it connects to the attacker's machine. If the victim was attempting to access a file share (SMB) or an internal web application, it will automatically attempt to authenticate to the attacker using NTLM (NT LAN Manager) authentication, providing the attacker with the victim's NTLMv2 hash.

## 2. ASCII Diagram of Attack Flow

```text
    [ Victim (192.168.1.50) ]                                     [ Attacker (192.168.1.100) ]
              |                                                                |
              | 1. User types \\FILESRV-TYPO in Explorer                       |
              |                                                                |
              | 2. DNS Query for FILESRV-TYPO -> DNS Server (Fails: NXDOMAIN)  |
              |                                                                |
              | 3. LLMNR Multicast: "Who is FILESRV-TYPO?"                     |
              |--------------------------------------------------------------->| (Attacker is listening)
              |                                                                |
              | 4. LLMNR Poisoned Response: "I am FILESRV-TYPO! (192.168.1.100)|
              |<---------------------------------------------------------------|
              |                                                                |
              | 5. Victim initiates SMB connection to 192.168.1.100            |
              |--------------------------------------------------------------->|
              |                                                                |
              | 6. Attacker demands NTLM authentication (Challenge)            |
              |<---------------------------------------------------------------|
              |                                                                |
              | 7. Victim sends NTLMv2 Response (Hash)                         |
              |--------------------------------------------------------------->|
              |                                                                |
              |                                                                | 8. Attacker captures hash or relays it
```

## 3. Attack Mechanics
The name resolution sequence in Windows typically follows this order:
1. Local Hosts file (`C:\Windows\System32\drivers\etc\hosts`)
2. Local DNS Cache
3. Primary DNS Server (Unicast)
4. LLMNR (Multicast)
5. NBT-NS (Broadcast)

When a user mistypes a server name (e.g., `\\fileserverr` instead of `\\fileserver`) or attempts to access a defunct legacy server, DNS will reply with `NXDOMAIN` (Non-Existent Domain). The OS immediately fires off LLMNR and NBT-NS requests to the local subnet.

The attacker, running a tool like **Responder**, continuously listens on UDP 5355 and UDP 137. When it sees a query, it immediately replies, overriding any legitimate (but slower) responses or answering queries for non-existent hosts. The victim machine trusts this response and establishes a connection to the attacker's IP on the requested port (usually SMB tcp/445, or HTTP tcp/80).

Responder sets up rogue servers (SMB, HTTP, FTP, SQL, etc.) to catch these incoming connections. When the victim connects, the rogue server initiates an NTLM challenge-response sequence. The attacker provides a custom challenge (often fixed, like `1122334455667788`) and the victim replies with the encrypted response (the NTLMv2 hash).

### Capture vs. Relay
- **Capture:** The attacker saves the NTLMv2 hash locally and attempts to crack it offline using tools like Hashcat. This relies on weak passwords.
- **Relay:** Instead of capturing the hash, the attacker intercepts the connection and forwards the authentication to another target (like a Domain Controller or a file server). This is known as SMB/LDAP Relaying and bypasses the need to crack the hash, granting immediate access to the target system as the victim user.

## 4. Prerequisites
- **Network Placement:** The attacker must have local subnet access (Layer 2 connectivity) to intercept and respond to multicast/broadcast traffic.
- **Vulnerable Configuration:** LLMNR and NBT-NS must be enabled on the victim machines (which is the default on Windows).
- **Trigger Event:** The victim must perform a lookup that fails in DNS, or the attacker must wait for background services (like SCCM, WPAD lookups) to trigger resolution.
- **SMB Signing (For Relaying):** If the attacker intends to relay the captured authentication via SMB, the target machine must have SMB Signing disabled or set to "Enabled but not Required" (default for Windows workstations).

## 5. Execution

The industry standard tool for this attack is **Responder**.

### Step 1: Configuration
Before running Responder, verify its configuration in `/etc/responder/Responder.conf`.
Ensure the rogue servers you want to run are set to `On` (e.g., SMB, HTTP). If you plan to relay the hashes later with `ntlmrelayx`, you must turn the SMB and HTTP servers in `Responder.conf` to `Off` so they don't conflict.

### Step 2: Running Responder
To capture hashes, simply run Responder on your active network interface:
```bash
sudo responder -I eth0 -dwv
```
- `-I eth0`: Specifies the interface.
- `-d`: Enable answers for DHCP broadcast requests.
- `-w`: Start the WPAD rogue proxy server.
- `-v`: Verbose mode.

When a victim performs a broadcast query, you will see output like this:
```text
[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [ON]

[*] [LLMNR]  Poisoned answer sent to 192.168.1.50 for name FILESRVR (service: type=ANY)
[*] [SMB] NTLMv2-SSP Client   : 192.168.1.50
[*] [SMB] NTLMv2-SSP Username : DOMAIN\jdoe
[*] [SMB] NTLMv2-SSP Hash     : jdoe::DOMAIN:1122334455667788:5A6B7C...
```

### Step 3: Offline Cracking
Once the NetNTLMv2 hash is captured, it is saved in Responder's log directory (e.g., `/usr/share/responder/logs/`). You can crack it using Hashcat:
```bash
# Hash mode 5600 is for NetNTLMv2
hashcat -m 5600 captured_hashes.txt /usr/share/wordlists/rockyou.txt -O
```

### Alternative: Inveigh (For Windows Environments)
If you are operating from a compromised Windows host and cannot run Python/Responder easily, **Inveigh** is a PowerShell/C# alternative.
```powershell
Import-Module .\Inveigh.ps1
Invoke-Inveigh -ConsoleOutput Y -LLMNR Y -NBNS Y -mDNS Y
```

## 6. Defensive Mechanisms & Mitigation

To secure an environment against this attack, both LLMNR and NBT-NS must be explicitly disabled, as they provide negligible value in modern DNS-managed domains.

### Disabling LLMNR
LLMNR can be disabled via Group Policy Object (GPO):
1. Navigate to: `Computer Configuration` -> `Administrative Templates` -> `Network` -> `DNS Client`.
2. Enable the policy: `Turn off multicast name resolution`.

### Disabling NBT-NS
Disabling NBT-NS is slightly more complex, as it is tied to the DHCP configuration or the network adapter properties.
- **Via DHCP:** In the DHCP Server options, configure Scope Option `001 Microsoft Disable Netbios Option` and set its value to `0x2`.
- **Via GPO / Scripting:** NBT-NS can be disabled via registry or PowerShell script pushed via GPO.
  ```powershell
  $adapters = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled = 'True'"
  $adapters | ForEach-Object { $_.SetTcpipNetbios(2) }
  ```

### Disabling WPAD (Web Proxy Auto-Discovery)
WPAD is another common protocol abused by Responder. Disable it via GPO:
- `User Configuration` -> `Preferences` -> `Windows Settings` -> `Registry`. Add a key to disable `AutoDetect` for proxy settings.

### Enforcing Network Segmentation
Isolating client workstations from each other (Private VLANs) prevents multicast and broadcast traffic from propagating across the subnet, neutering Responder's ability to see the queries.

## 7. Detection Strategies
- **Network Intrusion Detection (IDS/IPS):** Signature-based detection for unusually high volumes of LLMNR (UDP 5355) and NBT-NS (UDP 137) traffic originating from a single host.
- **Endpoint Detection & Response (EDR):** Monitoring for rogue processes binding to ports 137, 138, 5355, and 445 on client machines.
- **Honeypots:** Deploying a script that periodically queries a non-existent hostname and alerts if a response is received. Since no legitimate server should answer for `\\fake-server-alert`, any response indicates poisoning.
- **Event ID 4624 / 4625:** Monitoring for unexpected authentication successes or failures originating from unknown or unusual IP addresses on the local subnet.

## Real-World Attack Scenario

During an internal penetration test for a large retail organization, the team landed on a standard user's workstation. After performing initial enumeration, they identified that LLMNR and NBT-NS were enabled across the user subnet. The goal was to capture credentials to pivot to other systems.

**The Context**
The target network relied heavily on an old internal web portal that had been decommissioned. However, many user workstations still had hardcoded startup scripts attempting to map a drive to the old portal's hostname. Because the DNS record for this server had been deleted, these requests consistently failed back to LLMNR/NBT-NS broadcasts.

**The Execution**
1.  **Preparation:** The attacker started `Responder` on their compromised Linux VM connected to the user VLAN, configuring it to listen for and poison multicast requests.
    `responder -I eth0 -dwv`
2.  **The Trigger:** When a nearby user logged into their workstation, the legacy startup script executed, attempting to mount the defunct share.
3.  **The Interception:** The DNS query failed, and the workstation broadcast an LLMNR request. Responder instantly replied, spoofing the IP address of the requested server.
4.  **The Outcome:** The victim's workstation, believing the attacker's IP was the file server, initiated an SMB connection and automatically provided the user's NTLMv2 hash to authenticate. Responder captured the hash in its log files. The attacker then used `hashcat` offline to crack the hash, recovering the plaintext password, which granted them administrative access to several other servers in the domain.

## 8. Chaining Opportunities
- **[[12 - SMB Relay Attacks]]:** Captured authentication can be relayed to SMB endpoints to achieve RCE or dump the SAM database.
- **[[13 - LDAP Relay]]:** Captured authentication can be relayed to Domain Controllers to modify Active Directory objects and configurations.
- **IPv6 DNS Takeover (mitm6):** A modern counterpart to LLMNR poisoning that exploits IPv6 router advertisements.

## 9. Related Notes
- [[02 - NTLM Protocol Deep Dive]]
- [[08 - Password Cracking Strategies]]
- [[22 - Active Directory Enumeration]]

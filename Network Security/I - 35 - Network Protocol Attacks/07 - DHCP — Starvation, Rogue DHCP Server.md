---
tags: [dhcp, starvation, rogue-server, mitm, network]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.07 DHCP"
---

# DHCP — Starvation, Rogue DHCP Server

## 1. Introduction to Dynamic Host Configuration Protocol (DHCP)
The Dynamic Host Configuration Protocol (DHCP) is a fundamental network management protocol (RFC 2131) used on IPv4 networks. A DHCP server dynamically assigns an IP address and other network configuration parameters to each device on a network so they can communicate with other IP networks.

DHCP operates using connectionless **UDP**, utilizing **Port 67** for the server and **Port 68** for the client.

Because DHCP is a broadcast-based protocol designed for plug-and-play network convenience, it inherently trusts the local network. It does not authenticate clients requesting IPs, nor does it typically authenticate the server handing out the configurations. This trust model is highly susceptible to layer 2 network attacks.

### 1.1 The DORA Process
When a client joins a network, it goes through a four-step process to obtain an IP lease, remembered by the acronym **DORA**:
1. **Discover:** The client broadcasts a `DHCPDISCOVER` packet to the local subnet (`255.255.255.255`) asking if any DHCP servers are available.
2. **Offer:** Any listening DHCP server responds with a `DHCPOFFER` packet containing a proposed IP address, subnet mask, default gateway, and DNS servers.
3. **Request:** The client broadcasts a `DHCPREQUEST` packet formally requesting the offered IP address from the specific server that made the offer.
4. **Acknowledge:** The chosen server finalizes the lease and responds with a `DHCPACK` packet, confirming the lease duration and configuration.

## 2. ASCII Diagram: Rogue DHCP Architecture

```text
    [Legitimate DHCP Server]                      [Attacker (Rogue DHCP)]
          (Slower response)                             (Faster response)
                 |                                             |
                 |                                             |
                 |             [New Client Victim]             |
                 |                     |                       |
                 |<-------(1) DHCPDISCOVER (Broadcast)-------->|
                 |                     |                       |
                 |                     |<---(2) DHCPOFFER------| (Attacker responds FIRST)
                 |---(2) DHCPOFFER---->|                       |
                 |                     |                       |
                 |        (Victim accepts the first offer)     |
                 |                     |                       |
                 |<-------(3) DHCPREQUEST (To Attacker)------->|
                 |                     |                       |
                 |                     |<---(4) DHCPACK--------|
                 |                     |                       |
                 V                     V                       V
             [Ignored]         Victim is now configured to use the Attacker's IP 
                               as its Default Gateway and DNS Server!
```

## 3. DHCP Starvation Attacks
A DHCP Starvation attack is a Denial of Service (DoS) attack designed to deplete the legitimate DHCP server of all its available IP addresses in its scope.

**The Mechanics:**
The attacker rapidly broadcasts thousands of `DHCPDISCOVER` packets. Crucially, for each packet, the attacker spoofs a unique, random client MAC address.
The legitimate DHCP server receives these requests, allocates an IP address for each fake MAC address, and replies with a `DHCPOFFER`. The server's IP pool (the scope) quickly fills up.

**The Impact:**
Once the scope is entirely depleted (starved), the legitimate server cannot assign IP addresses to new, genuine clients joining the network. This causes a localized denial of service for new devices. Furthermore, this attack is almost always used as the precursor to a Rogue DHCP Server attack.

**Exploitation via Yersinia:**
Yersinia is a robust network framework designed to exploit Layer 2 protocols.
```bash
yersinia -I   # Interactive mode
# Select 'dhcp' mode and press 'x' to launch the "sending DISCOVER packet" attack, enabling the MAC spoofing option.
```
Alternatively, using Python / Scapy or dedicated tools like `dhcpstarv`:
```bash
dhcpstarv -i eth0
```

## 4. Rogue DHCP Server (MITM)
Once the legitimate server is starved, or simply by being faster on the local network, an attacker can stand up their own Rogue DHCP server.

**The Mechanics:**
The attacker runs a DHCP daemon on their machine. When a new client broadcasts a `DHCPDISCOVER`, the attacker's rogue server responds with a `DHCPOFFER`.
Because the legitimate server is either starved (cannot respond) or slower than the local attacker, the client accepts the attacker's offer.

**The Poisoned Configuration:**
The attacker doesn't just hand out an IP address; they completely dictate the client's network routing. They provide a configuration where:
- **Default Gateway:** The attacker's IP address.
- **DNS Server:** The attacker's IP address.

**The Impact (Full Man-in-the-Middle):**
Every single packet the victim intends to send to the internet is now routed directly through the attacker's machine. Every DNS query is sent to the attacker. The attacker can transparently proxy the traffic using `iptables`, sniff cleartext credentials, strip SSL/TLS via SSLstrip, and poison DNS to redirect the victim to phishing sites.

**Exploitation via Metasploit:**
```bash
msfconsole
msf6 > use auxiliary/server/dhcp
msf6 auxiliary(server/dhcp) > set DHCPIPSTART 192.168.1.100
msf6 auxiliary(server/dhcp) > set DHCPIPEND 192.168.1.150
msf6 auxiliary(server/dhcp) > set ROUTER 192.168.1.50   <-- Attacker's IP
msf6 auxiliary(server/dhcp) > set DNSSERVER 192.168.1.50 <-- Attacker's IP
msf6 auxiliary(server/dhcp) > run
```

### 4.1 IPv6 Rogue DHCP (SLAAC / MITM6)
Modern corporate networks often disable IPv4 DHCP to prevent rogue servers, but completely forget about IPv6. By default, Windows machines prefer IPv6 over IPv4.
Attackers use tools like `mitm6` to listen for IPv6 Router Solicitations. The attacker replies with a Router Advertisement, configuring the Windows machine to use the attacker as its IPv6 DNS server. Because IPv6 is preferred, the attacker successfully hijacks the DNS traffic, even if the IPv4 network is heavily secured.

## 5. Identifying Rogue DHCP Servers
Administrators and penetration testers must proactively hunt for rogue servers on the network.

**Using Nmap:**
Nmap provides a broadcast script to identify all responding DHCP servers on the subnet.
```bash
nmap --script broadcast-dhcp-discover -e eth0
```
If the output shows two different DHCP servers responding with different Gateway IPs, a rogue server is likely present.

## 6. Defensive Strategies & Mitigation
Defending against Layer 2 attacks requires implementing security features directly on the network switches.

### 6.1 DHCP Snooping
DHCP Snooping is a Layer 2 switch feature that acts as a firewall between untrusted hosts and legitimate DHCP servers.
- **Trusted Ports:** The network administrator explicitly configures the switch port connected to the legitimate corporate DHCP server as "Trusted."
- **Untrusted Ports:** All other ports (where end-users plug in) are "Untrusted."
- **Enforcement:** If the switch receives a `DHCPOFFER` or `DHCPACK` packet originating from an "Untrusted" port, it immediately drops the packet and logs the violation. This completely neutralizes Rogue DHCP servers.

### 6.2 Port Security (MAC Limiting)
To defend against DHCP Starvation, switches should be configured with Port Security.
Port Security limits the number of unique MAC addresses allowed to communicate through a single switch port. If an attacker runs `dhcpstarv` and generates thousands of spoofed MAC addresses, the switch will detect the violation after a set threshold (e.g., 5 MACs) and dynamically shut down the attacker's port (`err-disable` state).

### 6.3 802.1X Authentication
Implement robust Network Access Control (NAC) using IEEE 802.1X. This requires devices to authenticate cryptographically (via certificates or RADIUS credentials) before the switch port even activates and allows them onto the data VLAN. This prevents an unauthorized attacker from plugging into the wall and launching broadcast attacks.

## 7. Chaining Opportunities
- **Rogue DHCP to WPAD Spoofing:** Use the rogue DHCP server to push a malicious Web Proxy Auto-Discovery (WPAD) configuration (DHCP Option 252) to Windows clients. The clients will route all their web traffic through the attacker's proxy, yielding NTLMv2 hashes. -> [[10 - Active Directory Attacks]]
- **IPv6 MITM to NTLM Relay:** Run `mitm6` to become the IPv6 DNS server. When a client requests a resource, prompt them for authentication, capture the NTLMv2 hash, and relay it to the Domain Controller to escalate privileges. -> [[11 - NTLM Relaying]]
- **DHCP Starvation to Network Disruption:** In an ICS/SCADA environment, starving the DHCP pool can prevent PLCs and engineering workstations from obtaining leases after a reboot, causing a critical physical denial of service. -> [[18 - OT and ICS Security]]

## 8. Related Notes
- [[02 - Man-in-the-Middle Attacks]]
- [[06 - DNS — Zone Transfer (AXFR), Cache Poisoning, Spoofing]]
- [[10 - Active Directory Attacks]]
- [[11 - NTLM Relaying]]

---
*End of Note*

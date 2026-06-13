---
tags: [vapt, ultra-scenario, interview, expert, red-team]
difficulty: extreme
module: "Ultimate Expert Scenario Bank"
topic: "Ultra-Scenario - Network 02"
---

# Ultra-Scenario - Network 02: Pivoting through Segmented VLANs via Double Tagging and VRF Leaks

## 1. Scenario Overview

You have successfully established a foothold on a low-privileged workstation in a restricted Guest/Contractor VLAN (VLAN 50). The network architecture is heavily segmented using Virtual Routing and Forwarding (VRF) instances. The core switches are running Cisco NX-OS, and your ultimate objective is to access the highly secured Datacenter Management VRF (VRF-MGMT, VLAN 200) where the vCenter and Domain Controllers reside.

Direct routing between the Contractor VRF and the Management VRF is completely dropped at the firewall. However, upon investigating switch port configurations and routing tables, you discover a legacy native VLAN misconfiguration on an adjacent switch and a Route Target (RT) leak within the MPLS/VRF backbone. 

This scenario requires executing a precise combination of Layer 2 VLAN Double Tagging (QinQ exploitation) to hop into a transit network, followed by exploiting a BGP route leak to inject traffic into the isolated management plane.

## 2. The Attack Path

### Stage 1: Layer 2 Reconnaissance and Identifying the Native VLAN Mismatch
*   **Packet Capture Analysis:** Using Wireshark/tcpdump to analyze spanning-tree (STP), CDP, and DTP frames. 
*   **DTP Exploitation:** Attempting Dynamic Trunking Protocol (DTP) negotiation using tools like Yersinia. If the switch port is hardcoded to access mode, DTP negotiation fails.
*   **Discovering the Native VLAN:** By observing CDP packets, you notice the switch is broadcasting a Native VLAN ID of 1 (the default), while your access port is on VLAN 50. You suspect the trunk link connecting the access switch to the core switch might be using VLAN 1 as the native, untagged VLAN.

### Stage 2: VLAN Double Tagging (QinQ) Exploitation
*   **The Theory:** 802.1Q double tagging allows an attacker connected to an 802.1Q port (where the native VLAN matches the attacker's VLAN, or via a specific crafting technique) to prepend two VLAN tags. The first switch strips the outer tag (the native VLAN) and forwards the frame across the trunk. The second switch reads the inner tag and forwards the frame into the target VLAN.
*   **Crafting the Payload:** Using Scapy to craft ICMP or UDP packets with an outer tag of VLAN 1 (Native) and an inner tag of VLAN 100 (Transit/Server VLAN).
*   **One-Way Limitation:** Double tagging is strictly a unidirectional attack. The target in VLAN 100 will receive the packet, but the response will be tagged for VLAN 100 and routed normally, meaning it will never return to the attacker in VLAN 50.
*   **Achieving Two-Way Comm:** To bypass the unidirectional limitation, you must exploit a stateless protocol (UDP) or establish a reverse shell connection back to an attacker-controlled external IP, or spoof the source IP to a system in VLAN 100 that you control. In this scenario, we use double tagging to send a malicious SNMP SET command or UDP payload to a vulnerable transit router interface.

### Stage 3: Exploiting the Transit Router
*   **Target:** A legacy Cisco IOS router sitting in VLAN 100 acting as a PE (Provider Edge) for the internal MPLS network.
*   **Exploitation:** Using the one-way double-tagged packet to exploit a known UDP vulnerability (e.g., IKEv1, SNMP, or an older IOS RCE) to execute code or change the configuration. We craft a payload that forces the router to initiate a TFTP download of a new configuration or establish a reverse shell.
*   **Result:** We gain execution on the PE router in VLAN 100.

### Stage 4: VRF Route Leaking and Lateral Movement
*   **VRF Architecture:** The compromised PE router has multiple VRFs defined. You are in `VRF-TRANSIT`. The target is `VRF-MGMT`.
*   **Route Targets (RT):** VRFs isolate routing tables, but they can share routes using BGP Route Targets (`route-target export` and `route-target import`).
*   **The Leak:** You examine the BGP configuration and find a misconfigured export/import policy. `VRF-TRANSIT` is exporting its routes with an RT of `65000:100`. `VRF-MGMT` is mistakenly importing `65000:100` to allow access to a specific monitoring server.
*   **The Injection:** You configure a loopback interface on the compromised PE router with an IP in a subnet routed to `VRF-MGMT`. You advertise this loopback via BGP into `VRF-TRANSIT` with the RT `65000:100`. The core routers leak this route into `VRF-MGMT`.
*   **The Pivot:** Now, from the compromised router, you can route traffic directly into the management datacenter network, completely bypassing the firewall that sits between the Contractor and Management zones.

---

## 3. Interview Deep-Dive: Q&A Interaction

### Q1: "You mention VLAN Double Tagging. Explain the exact mechanism of how the packet traverses the first switch, why the outer tag is stripped, and why this attack only works if the attacker is connected to a port that shares the trunk's native VLAN."

**Candidate Expert Answer:**
"VLAN double tagging exploits how switches process 802.1Q tags across trunk links.
When a switch receives a frame on an access port, it internally tags it with that port's VLAN ID. However, if an attacker crafts a packet that *already* has an 802.1Q tag, and the switch port isn't dropping tagged frames on access ports (a common misconfiguration), we can insert two tags.

Let's assume the trunk link's Native VLAN is VLAN 1, and the attacker is somehow on VLAN 1 (or the switch processes the outer tag regardless). 
The attacker sends a frame: `[MAC Header] -> [802.1Q Outer Tag: VLAN 1] -> [802.1Q Inner Tag: VLAN 100] -> [IP Payload]`.

1. **Switch A (Access Switch):** Receives the frame. It sees the outer tag is VLAN 1. It looks at its MAC address table and decides to forward the frame across the trunk link to Switch B.
2. **The Trunk Link:** Because VLAN 1 is the *Native VLAN* on the trunk, Switch A must send the frame *untagged*. Therefore, Switch A strips the outer 802.1Q header (VLAN 1).
3. **Switch B (Core/Distribution):** Receives the frame. Because the outer tag was stripped, Switch B looks at the *next* header. It sees the Inner Tag (VLAN 100). Switch B assumes this frame legitimately originated from VLAN 100 and forwards it to the target in VLAN 100.

This attack *requires* the attacker's outer tag to match the trunk's Native VLAN. If the trunk's native VLAN is 99, and the attacker uses an outer tag of 1, Switch A will *not* strip the tag (it will leave it as VLAN 1). Switch B will receive a tagged VLAN 1 frame and process it in VLAN 1. The inner VLAN 100 tag will never be evaluated. That's why changing the native VLAN to an unused, non-routed VLAN (like 999) and pruning it from trunks is the primary defense."

### Q2: "Since Double Tagging is unidirectional, you can't establish a standard TCP connection. How exactly do you execute a payload against the PE router in VLAN 100 using only one-way UDP or ICMP traffic?"

**Candidate Expert Answer:**
"The unidirectional nature of double tagging means we are firing blind. We cannot complete a 3-way TCP handshake. Therefore, we must rely on stateless protocols (UDP/ICMP) and 'fire-and-forget' exploits.

One of the most reliable methods against legacy infrastructure is SNMP (Simple Network Management Protocol) versions 1 or 2c. If I have enumerated or brute-forced the SNMP Write community string (e.g., `private` or `admin`), I can use a single UDP packet to execute a configuration change.

Using a Scapy script, I craft a double-tagged UDP packet targeting port 161 on the PE router. The SNMP payload will use the `CISCO-CONFIG-COPY-MIB` to instruct the router to copy a configuration file from a TFTP server I control into its running-config.

*The Scapy Payload Physics:*
```python
# Outer Tag: Native VLAN (1), Inner Tag: Target VLAN (100)
dot1q_outer = Dot1Q(vlan=1)
dot1q_inner = Dot1Q(vlan=100)
ip = IP(src="10.10.50.5", dst="10.10.100.1") # Target PE Router
udp = UDP(sport=161, dport=161)

# SNMP payload instructing TFTP download (OIDs simplified for brevity)
# Setting ccCopyProtocol to tftp(1), ccCopySourceFileType to networkFile(1)
# ccCopyDestFileType to runningConfig(4), etc.
snmp_payload = SNMP(community="private", PDU=SNMPset(...))

packet = Ether(src="attacker_mac", dst="switch_mac") / dot1q_outer / dot1q_inner / ip / udp / snmp_payload
sendp(packet, iface="eth0")
```

The router receives the command in VLAN 100. It processes the valid SNMP SET request and immediately initiates a TFTP connection to my external IP (or an internal pivot). Since the router's TFTP request originates *from* the router natively, it is routed normally, bypassing the one-way restriction. The router downloads my malicious config, which adds a GRE tunnel or creates a new administrative user with privilege level 15, granting me full two-way access."

### Q3: "Brilliant. You now have full control of the PE router in `VRF-TRANSIT`. The target is `VRF-MGMT`. You mentioned Route Target (RT) leaks. Walk me through the exact BGP commands on the compromised router to execute the leak and establish the pivot."

**Candidate Expert Answer:**
"VRFs isolate routing tables, creating virtual routers within the physical router. However, in an MPLS/BGP VPN environment, routes are shared between VRFs using Multiprotocol BGP (MP-BGP) via Route Distinguishers (RD) and Route Targets (RT).
- **RD:** Makes an IP prefix globally unique across the backbone (e.g., `65000:1 10.0.0.0/24`).
- **RT:** Extended BGP communities that dictate which VRFs import which routes.

I analyze the BGP config on the PE router:
```text
vrf definition VRF-MGMT
 rd 65000:200
 route-target export 65000:200
 route-target import 65000:200
 route-target import 65000:100  <-- THE VULNERABILITY
```
Because `VRF-MGMT` imports `65000:100`, any route I advertise into the BGP backbone tagged with `65000:100` will be injected straight into the highly secure Management routing table.

**The Execution:**
1. I create a loopback interface on my compromised router to act as my tunnel endpoint or NAT pool.
   ```text
   interface Loopback1337
    ip address 192.168.13.37 255.255.255.255
   ```
2. I assign this interface to a VRF. Since I control the router, I can actually just create a rogue VRF, or use `VRF-TRANSIT`. Let's use `VRF-TRANSIT`.
3. I enter the BGP configuration and redistribute my loopback into the MP-BGP process, ensuring it's tagged with the vulnerable RT.
   ```text
   router bgp 65000
    address-family ipv4 vrf VRF-TRANSIT
     redistribute connected
     exit-address-family
   ```
   Wait, by default it uses the VRF's export RT. If `VRF-TRANSIT` already exports `65000:100`, my route is automatically leaked into `VRF-MGMT`!
4. If I need a specific IP to reach the vCenter (e.g., `10.200.0.50`), I configure a NAT overload (PAT) on my router. Traffic from my C2 traversing the router will be NAT'd to `192.168.13.37`.
5. I establish a GRE tunnel or SSH port forward from my router back to my attacker machine.
6. Now, I route my attack traffic through the GRE tunnel, hitting the router. The router NATs it to `192.168.13.37`. The route to the Management subnet is in the router's global or VRF table due to the leak. The traffic enters `VRF-MGMT`, hits the vCenter, and the return traffic routes back to `192.168.13.37`, traversing the leak backward.

I have completely bypassed the physical and logical firewalls separating the zones."

### Q4: "How would a SOC or Network Engineering team detect this route leak occurring in real-time?"

**Candidate Expert Answer:**
"Detecting BGP anomalies requires continuous monitoring of the routing plane, which many organizations fail to do internally (they only monitor external BGP).
1. **BGP Route Analytics:** Tools like BGPlay or internal route reflectors feeding into a monitoring engine (like Cisco Crosswork or open-source ExaBGP scripts). The SOC should trigger a Critical alert if the total prefix count in `VRF-MGMT` suddenly changes, or if a new origin AS or unexpected RD appears in the table.
2. **NetFlow/IPFIX Analysis:** The firewall between Contractor and Management will see absolutely zero traffic. However, NetFlow on the core routers will show traffic flowing directly from the PE router's IP (`192.168.13.37`) into the Management VLAN. An NBA (Network Behavioral Analytics) tool should flag this because `192.168.13.37` has no historical baseline of communicating with vCenter.
3. **Configuration Auditing:** Tools like SolarWinds NCM or Ansible playbooks should continuously diff the running-config of the PE routers against a golden baseline. The moment I execute `interface Loopback1337` or modify the BGP process, an alert should fire."

---

## 4. Technical Appendix: Advanced DTP Exploitation

While Double Tagging is elegant, if the switch port is left in `dynamic desirable` or `dynamic auto` mode, DTP exploitation is vastly superior as it yields a full two-way trunk link.

**The Physics of DTP:**
Dynamic Trunking Protocol uses multi-cast MAC `01:00:0c:cc:cc:cc` with SNAP SAP `0x2004`.
If an attacker sends a DTP Desirable frame, the switch will negotiate a trunk. Once a trunk is formed, the attacker's network interface (configured with 802.1Q sub-interfaces) can tag and inject traffic into *any* VLAN allowed on the trunk.

**Yersinia Execution:**
```bash
yersinia dtp -attack 1 -interface eth0
```
Once the trunk is up:
```bash
modprobe 8021q
vconfig add eth0 100
vconfig add eth0 200
ifconfig eth0.100 up
ifconfig eth0.200 up
dhclient eth0.100
```
The attacker now has direct, bi-directional Layer 2 access to all segmented subnets, rendering Layer 3 firewalls completely irrelevant.

*End of Scenario 02*

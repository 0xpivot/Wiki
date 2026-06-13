---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.13 VoIP and SIP Protocol Attacks"
---

# 79.13 VoIP and SIP Protocol Attacks

## 1. Introduction to VoIP Ecosystem

Voice over IP (VoIP) revolutionizes telecommunications by routing voice, video, and multimedia sessions over IP networks rather than traditional PSTN (Public Switched Telephone Network) lines. Because VoIP infrastructure integrates directly with corporate LANs and WANs, it inherently inherits the vulnerabilities of IP networks while introducing new protocol-specific attack surfaces. 

Compromising a VoIP system can lead to severe consequences:
- **Toll Fraud (Phreaking)**: Attackers routing expensive international calls through corporate PBX systems.
- **Eavesdropping**: Intercepting highly sensitive executive phone calls.
- **Vishing & Social Engineering**: Spoofing internal caller IDs to extract credentials from employees.
- **Denial of Service**: Bringing down the entire communication grid of an enterprise.

---

## 2. SIP, SDP, and RTP Fundamentals

VoIP is not a single protocol but a suite of protocols working in tandem. 
1. **SIP (Session Initiation Protocol)**: Operates on port `5060` (UDP/TCP) or `5061` (TLS). It handles the signaling—setting up, modifying, and tearing down calls. Think of it as the control plane.
2. **SDP (Session Description Protocol)**: Carried inside SIP payloads. It negotiates media capabilities (codecs, ports, IPs) between endpoints.
3. **RTP (Real-time Transport Protocol)**: Operates on dynamic high UDP ports (e.g., `10000-20000`). It carries the actual voice/video data streams. Think of it as the data plane.

### SIP Message Types (Methods)
- `REGISTER`: An IP phone registering its IP address with the PBX.
- `INVITE`: Initiating a call session.
- `OPTIONS`: Querying a server/phone for its capabilities (heavily used for scanning).
- `BYE`: Terminating a session.

---

## 3. Reconnaissance and Enumeration

The first step in VoIP exploitation is locating SIP endpoints and Private Branch Exchanges (PBXs) like Asterisk, FreePBX, or Cisco CallManager.

**Nmap SIP Enumeration:**
```bash
nmap -p 5060,5061 -sU -sV --script sip-enum-users,sip-methods <target_subnet>
```

**Using SIPVicious (The Industry Standard for VoIP Recon):**
`svmap` is used to discover SIP devices and PBX servers.
```bash
# Scan a network for SIP devices
svmap 192.168.1.0/24

# Identify valid extensions on a discovered PBX
svwar -e 100-999 <PBX_IP>
```
*Note: `svwar` sends `REGISTER` or `INVITE` requests. If the server responds with "401 Unauthorized" instead of "404 Not Found", the extension exists.*

---

## 4. VoIP Exploitation Vectors

### 4.1 Extension Brute-forcing and Password Cracking
Once valid extensions are enumerated, attackers will attempt to guess the SIP password (secret). VoIP administrators notoriously use weak passwords, often setting the password identical to the extension number.

**Cracking with `svcrack`:**
```bash
# Brute-force extension 100 using a dictionary
svcrack -u 100 -d passwords.txt <PBX_IP>
```

### 4.2 Offline SIP Digest Authentication Cracking
SIP uses HTTP-like Digest Authentication. If an attacker can capture the network traffic during a device registration (`REGISTER`) or call setup (`INVITE`), they can extract the authentication hash and crack it offline.
1. Capture SIP traffic using Wireshark or `tcpdump`.
2. Extract the SIP digest response.
3. Use Hashcat or John the Ripper to crack the hash.
```bash
# Crack SIP auth (Hashcat mode 11400)
hashcat -m 11400 sip_hashes.txt wordlist.txt
```

### 4.3 RTP Eavesdropping and Call Recording
If SIP and RTP are transmitted in plaintext (which is shockingly common inside internal networks), an attacker performing ARP spoofing or connecting to a span port can intercept the RTP audio streams.

**Using Wireshark for Eavesdropping:**
1. Capture the network traffic.
2. Go to **Telephony > VoIP Calls**.
3. Select the intercepted call and click **Play Streams**.
4. Wireshark automatically decodes the G.711 or G.722 codecs and plays the audio.

**Using UCSniff:**
UCSniff is an advanced tool that automates VLAN hopping, ARP poisoning, and automated capturing/decoding of RTP streams directly to `.wav` files.

### 4.4 Caller ID Spoofing
The `From` header in a SIP `INVITE` packet dictates the Caller ID displayed on the recipient's phone. Because SIP inherently lacks validation, an attacker can modify this header.
**SIP INVITE Payload Example:**
```text
INVITE sip:target@192.168.1.100 SIP/2.0
Via: SIP/2.0/UDP 192.168.1.50:5060;branch=z9hG4bK...
From: "CEO" <sip:100@192.168.1.50>;tag=12345
To: <sip:target@192.168.1.100>
Call-ID: spoofed-call-001@192.168.1.50
CSeq: 1 INVITE
```
By sending this packet, the attacker's call appears to come from the CEO (Extension 100), enabling highly effective social engineering attacks against the Helpdesk.

### 4.5 SIP Denial of Service (DoS)
- **INVITE Flooding**: Sending thousands of fake `INVITE` requests depletes the PBX's memory and CPU, making it unable to process legitimate calls.
- **BYE Teardown**: If an attacker sniffs an active call's `Call-ID` and `Tag`, they can inject a spoofed `BYE` message to abruptly terminate the ongoing call.

---

## 5. ASCII Diagram: SIP Call Setup & MiTM

```text
       [Alice - Ext 101]                               [Bob - Ext 102]
              |                                               |
              | 1. SIP INVITE (I want to call Bob)            |
              |---------------------------------------------->|
              |                                               |
              | 2. SIP 200 OK (I accept, here is my SDP/IP)   |
              |<----------------------------------------------|
              |                                               |
              | 3. SIP ACK                                    |
              |---------------------------------------------->|
              |                                               |
              |========== 4. RTP AUDIO STREAM ================|
              |      (UDP High Ports, e.g., 16384)            |
              |                                               |
              
              
      ==== MAN-IN-THE-MIDDLE / ARP POISONING SCENARIO ====
      
              [Attacker / UCSniff]
               /                \
      (Captures RTP)        (Forwards RTP)
             /                    \
       [Alice]                    [Bob]
```

---

## 6. Defense-in-Depth for VoIP

1. **VLAN Segmentation**: Place all VoIP endpoints and PBX servers on an isolated Voice VLAN. Implement 802.1X to prevent unauthorized devices from joining the VLAN.
2. **Use SIPS and SRTP**: Secure SIP (SIPS) encrypts the signaling over TLS, preventing credential harvesting. SRTP (Secure RTP) encrypts the media streams, rendering eavesdropping attacks useless.
3. **Strong SIP Credentials**: Enforce complex SIP passwords via PBX policies.
4. **SBC Deployment**: Deploy Session Border Controllers (SBCs) at the network edge to filter anomalous SIP traffic, rate-limit INVITEs, and hide internal topology.

---

## 7. Chaining Opportunities
- **VLAN Hopping -> VoIP Interception**: Using Double Tagging or DTP (Dynamic Trunking Protocol) spoofing to hop from the Data VLAN into the strictly controlled Voice VLAN, subsequently launching ARP spoofing to capture SRTP negotiation keys or plaintext RTP.
- **Web UI to Root**: Many PBX systems (like FreePBX) host web administrative panels. Exploiting an authenticated command injection flaw in the web panel (after cracking a SIP admin credential) provides root access to the underlying Linux server.

---

## 8. Related Notes
- [[11 - IoT Protocols MQTT and CoAP Exploitation]]
- [[14 - Attacking BGP Routing and Infrastructure]]
- [[04 - VLAN Hopping and Layer 2 Attacks]]
- [[15 - Physical Security Systems and Access Control Bypass]]

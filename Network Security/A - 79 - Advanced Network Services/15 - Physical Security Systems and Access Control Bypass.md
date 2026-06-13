---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.15 Physical Security Systems and Access Control Bypass"
---

# 79.15 Physical Security Systems and Access Control Bypass

## 1. Physical Access Control Systems (PACS) Overview

In advanced red teaming, the boundary between physical and logical security blurs. Physical Access Control Systems (PACS) regulate human entry into data centers, server rooms, and corporate facilities. A typical PACS consists of:
1. **Credentials**: Smart cards, RFID badges, NFC devices, or BLE mobile apps.
2. **Readers**: Scanners mounted near doors that read the credentials.
3. **Controllers**: Processing units located in secure IT closets that store access rules. They receive data from the reader, validate it against a database, and trigger the door relay.
4. **Electronic Locks/Relays**: The physical mechanisms (magnetic locks, electric strikes) that unlock the door.

Compromising the PACS allows an attacker to bypass physical barriers, insert rogue hardware (like a Raspberry Pi dropbox) directly into the internal network, or steal server chassis.

---

## 2. Protocol Weaknesses: Wiegand vs. OSDP

The communication link between the Door Reader and the Door Controller is a prime target for hardware implants.
### 2.1 The Wiegand Vulnerability
The majority of legacy PACS use the **Wiegand protocol**. Wiegand is an unencrypted, unidirectional serial protocol. When a card is swiped, the reader simply pulses the raw 1s and 0s (often 26-bit to 37-bit binary payloads) over the data wires.
- **Vulnerability**: Since there is no encryption or mutual authentication, an attacker can pry the reader off the wall, tap the data lines with a malicious implant (like an ESPKey or BLEkey), and capture badge numbers in plaintext. The attacker can then replay these numbers later to unlock the door without a physical card.

### 2.2 OSDP (Open Supervised Device Protocol)
OSDP is the modern replacement for Wiegand, utilizing RS-485 serial communication.
- **Secure Channel (OSDP SC)**: Encrypts the traffic using AES-128.
- **Vulnerability**: OSDP SC is optional. Many installations run OSDP in plaintext mode. Furthermore, downgrade attacks exist. An attacker can inject noise on the line to force the reader and controller to negotiate down to unencrypted communications, allowing data extraction.

---

## 3. RFID and Smart Card Exploitation

### 3.1 Low-Frequency (125 kHz) Cloning
Formats like HID Prox, AWID, and EM4100 are extremely common and completely devoid of cryptographic security. The card blindly broadcasts its UID (Unique Identifier) when energized.
- **Exploitation**: Attackers use tools like the **Proxmark3** or cheap T5577 cloner devices to read the card data simply by standing near an employee (RFID skimming). The UID is then written to a blank T5577 card, creating a perfect duplicate.
```bash
# Using Proxmark3 to clone a 125kHz HID card
lf search
# Output reveals HID ID: 200426A
lf hid clone 200426A
```

### 3.2 High-Frequency (13.56 MHz) Mifare Attacks
HF cards like Mifare Classic and iCLASS provide cryptographic sector protection. 
- **Mifare Classic Weaknesses**: Uses the broken proprietary CRYPTO1 cipher. Attackers use the **Nested Authentication Attack** or **Hardnested Attack** to recover sector keys. If even one sector uses a default key (e.g., `FF FF FF FF FF FF`), the Proxmark3 can mathematically derive all other keys, allowing a full card dump and clone.
```bash
# Proxmark3 Auto-PWN on Mifare Classic
hf mf autopwn
# Dumps all keys and data to a file for writing to a "Magic" UID-changeable card
```

---

## 4. Hardware and Network Vectors

### 4.1 Exposed Controller Interfaces
Door controllers are network-attached devices connected to the corporate LAN. They frequently suffer from:
- **Default Credentials**: Installers often leave HTTP or Telnet interfaces exposed with `admin:admin`.
- **Legacy Vulnerabilities**: Outdated firmware susceptible to unauthenticated RCE.
If an attacker compromises the controller over the network, they can remotely trigger door relays, add backdoored user badges, or disable alarm sensors.

### 4.2 Lock Picking and Physical Bypass
While strictly physical, IT security personnel must understand mechanical bypasses:
- **Request to Exit (REX) Sensors**: Passive Infrared (PIR) sensors inside the door unlock the maglock when someone approaches to leave. Attackers use canned air or hot whiskey (thermal change) sprayed under the door crack to trick the PIR sensor into opening the door from the outside.
- **Under-Door Tools**: Manipulating the internal door handle with a custom wire tool.

---

## 5. BLE Mobile Access Vulnerabilities
Modern PACS allow employees to unlock doors via Bluetooth Low Energy (BLE) on their smartphones. 
- **Relay Attacks**: Attackers can execute a BLE relay attack. Attacker A stands near the door reader, Attacker B stands near the victim (e.g., at a coffee shop). Attacker B captures the victim's BLE signals and forwards them over the internet to Attacker A, who transmits them to the door, unlocking it without the victim's knowledge.

---

## 6. ASCII Diagram: PACS Architecture and Attack Surfaces

```text
    [Victim Badge] 
         |  (RFID Skimming via Proxmark3)
         v
    [RFID Reader] ------(Wiegand Data Lines)--------> [Door Controller]
         |             ^                                      | (LAN Network)
         |             | (Hardware Implant / ESPKey)          v
   (Door Frame)                                         [Access Server]
         |                                                    |
         +----------(Door Relay / Maglock)--------------------+
                       ^
                       | (Under-Door Tool / REX Sensor Bypass)
                  [Attacker]
```

---

## 7. Defensive Countermeasures

1. **Hardware Upgrades**: Replace 125kHz Prox and Mifare Classic cards with High-Frequency, highly secure cards like DESFire EV2/EV3 or Seos, which use AES encryption and protect against cloning.
2. **Enforce OSDP Secure Channel**: Mandate OSDP with Secure Channel (AES-128) enabled between readers and controllers, disabling fallback to unencrypted modes.
3. **Tamper Switches**: Enable and actively monitor reader and controller tamper switches to alert security personnel if a device is opened to install an implant.
4. **Network Isolation**: Place all door controllers and PACS servers on an isolated, non-routable VLAN. 

---

## 8. Chaining Opportunities
- **Physical to Logical Pivot**: Cloning a badge -> Entering server room -> Plugging a rogue Raspberry Pi into the core switch -> Gaining unauthenticated internal network access.
- **Network to Physical Pivot**: Exploiting a SQL injection in the internal HR Web Portal -> Modifying employee badge permissions in the database -> Walking through the front door using an unauthorized badge.

---

## 9. Related Notes
- [[11 - IoT Protocols MQTT and CoAP Exploitation]]
- [[12 - CAN Bus and Automotive Network Exploitation]]
- [[14 - Attacking BGP Routing and Infrastructure]]
- [[04 - VLAN Hopping and Layer 2 Attacks]]

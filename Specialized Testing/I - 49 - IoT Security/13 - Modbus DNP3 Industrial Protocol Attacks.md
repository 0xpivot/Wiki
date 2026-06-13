---
tags: [iot, pentesting, hardware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.13 Modbus DNP3 Industrial Protocol Attacks"
---

# Modbus DNP3 Industrial Protocol Attacks

## 1. Introduction to Industrial Protocols

Modbus and Distributed Network Protocol 3 (DNP3) are the foundational communication protocols of Industrial Control Systems (ICS) and Supervisory Control and Data Acquisition (SCADA) networks. Originally designed in the late 1970s and 1990s respectively for serial communication across isolated, physically secure networks, they were later adapted to run over TCP/IP to support modern networking infrastructure.

The core vulnerability of these protocols lies in their legacy design: they fundamentally lack intrinsic security features such as authentication, encryption, and authorization. When connected to modern networks, these protocols operate on the dangerous assumption of implicit trust—any device that can reach the network port is trusted to issue commands.

## 2. Architecture and Protocol Mechanics

### Modbus Architecture
Modbus is a master/slave (or client/server in TCP terminology) protocol. The master requests data or issues commands, and the slaves respond. Modbus organizes data into four primary tables:
1. **Coils:** Read/Write Booleans (e.g., turning a motor on/off).
2. **Discrete Inputs:** Read-Only Booleans (e.g., a limit switch state).
3. **Input Registers:** Read-Only 16-bit Integers (e.g., a temperature sensor reading).
4. **Holding Registers:** Read/Write 16-bit Integers (e.g., PID controller setpoints).

Over TCP/IP, Modbus utilizes port 502 and encapsulates the serial frame in a Modbus Application Protocol (MBAP) header.

### DNP3 Architecture
DNP3 is significantly more complex and robust than Modbus. It was designed specifically for utilities (electrical grids, water systems) and supports features like unsolicited reporting (slaves sending data without being polled), time synchronization, and multiple data types. It operates over TCP/UDP port 20000. Despite its complexity, standard DNP3 suffers from the same lack of cryptographic authentication as Modbus.

## 3. ASCII Diagram: Modbus Command Injection Flow

```text
     [ Attacker ]
          |
          | 1. Gains network access (e.g., via compromised VPN or IT pivot)
          | 2. Crafts malicious Modbus/TCP packet 
          |    (Function Code 05: Write Single Coil)
          v
   +-------------------+
   |  Network Switch   | (IT/OT Boundary lacks DPI firewalls)
   +-------------------+
          |
          | 3. Packet routed to TCP Port 502
          v
   +-------------------+
   |   Target PLC      | (Programmable Logic Controller)
   |   Modbus TCP Svc  |
   +-------------------+
          |
          | 4. PLC processes Function Code 05 without authentication
          | 5. Alters physical output state
          v
   [ Physical Actuator ]
   (e.g., Critical Cooling Valve shuts down)
```

## 4. Exploitation Techniques

### 4.1 Discovery and Interrogation

The first phase is identifying ICS devices on the network. Aggressive scanning must be avoided, as legacy PLCs possess fragile network stacks that crash easily, potentially causing physical disruption.
```bash
# Gentle Nmap scan for Modbus
nmap -Pn -sT -p 502 --script modbus-discover <target_ip>
```
The `modbus-discover` script attempts to extract the Unit ID and device identification strings, revealing the manufacturer and model (e.g., Schneider Electric, Siemens).

### 4.2 Data Exfiltration (Reading Registers)

Attackers use tools like `modpoll` to dump the contents of the registers. Understanding this data requires analyzing the ICS documentation, as Modbus does not transmit metadata (variable names are not sent, only addresses and raw values).
```bash
modpoll -m tcp -r 1 -c 50 <target_ip>
```
This reads 50 registers starting from address 1, providing the attacker with insight into the current physical state of the process.

### 4.3 Command Injection (Writing Coils/Registers)

The most devastating attacks involve writing unauthorized values to Coils or Holding Registers.
Using custom Python scripts with libraries like `pymodbus`, an attacker can precisely target an actuator.
```python
from pymodbus.client.sync import ModbusTcpClient

# Connect to the target PLC
client = ModbusTcpClient('10.0.0.50', port=502)

# Write to Coil address 10 (e.g., turning on a pump)
result = client.write_coil(10, True)

# Write to Holding Register 5 (e.g., drastically altering a pressure threshold)
result = client.write_register(5, 9999)
```
Because the protocol performs no verification, the PLC unquestioningly executes these commands, leading to physical consequences.

### 4.4 Denial of Service (DoS)

ICS environments prioritize availability above all else. Attackers can disrupt operations without needing deep knowledge of the register maps simply by flooding the PLC with TCP requests, exhausting its limited memory, or sending malformed MBAP headers that trigger parsing crashes.

## 5. Case Studies in ICS Exploitation

### Stuxnet
The most famous example of ICS exploitation. While it relied on zero-days for propagation, the payload itself manipulated the communication between Siemens Step7 software and the PLCs. It issued specific, unauthorized commands to alter the frequency of centrifuge drives while simultaneously recording normal operating data and replaying it to the SCADA monitors, blinding the operators to the sabotage.

### CrashOverride / Industroyer
A malware framework designed specifically to attack power grids. It contained dedicated modules to "speak" ICS protocols directly, including IEC 104, IEC 61850, OPC, and DNP3. By communicating in the native language of the grid infrastructure, the malware could autonomously open circuit breakers, plunging substations into darkness.

## 6. Defensive Hardening and Mitigation

Securing environments relying on Modbus/DNP3 requires architectural rather than protocol-level solutions:
1. **Purdue Model Segmentation:** The OT (Operational Technology) network must be strictly separated from the IT network. Communication between layers should be heavily restricted.
2. **Deep Packet Inspection (DPI) Firewalls:** Standard firewalls only see TCP port 502. Specialized ICS firewalls can inspect the Modbus payload and enforce rules (e.g., "Allow Read commands, Block all Write commands").
3. **Data Diodes:** For pure monitoring networks, physical unidirectional gateways ensure data can leave the ICS network but no packets can flow back in.
4. **Protocol Upgrades:** Implement DNP3 Secure Authentication (DNP3-SA) or wrap Modbus TCP inside IPsec or TLS tunnels to provide cryptographic assurance of the sender's identity.
5. **Anomaly Detection:** Deploy passive network monitoring tools (like Zeek with ICS parsers) to establish a baseline of normal polling behavior and alert on sudden parameter changes or new master nodes.

## 7. Comprehensive VAPT Checklist for ICS

- [ ] Map the network to identify all ICS protocols (Modbus 502, DNP3 20000, Ethernet/IP 44818, S7Comm 102).
- [ ] Verify the segmentation between IT and OT networks (attempt to ping/route to OT subnets from corporate).
- [ ] Perform gentle enumeration to identify PLC vendor, model, and firmware version.
- [ ] Attempt unauthenticated read operations on holding registers to confirm data accessibility.
- [ ] Attempt unauthenticated write operations (only in heavily controlled, simulated environments) to verify lack of access controls.
- [ ] Review HMI and SCADA server security (often running outdated Windows OS with unpatched SMB vulnerabilities).
- [ ] Verify if DPI firewalls successfully block unauthorized function codes.
- [ ] Test the resilience of PLCs against malformed packets and network floods.

## 8. Advanced ICS Exploitation Concepts

When generic protocol manipulation is insufficient, attackers focus on the engineering workstations. The software used to program the PLCs (e.g., RSLogix, TIA Portal) often contains proprietary mechanisms to stop, start, or entirely overwrite the logic running on the PLC. Compromising the engineering workstation grants the attacker "God mode" over the physical process, allowing them to download entirely new, malicious logic into the controller that bypasses all physical safety interlocks.

## 9. Appendix: Nmap Scanning Details
```text
PORT    STATE SERVICE
502/tcp open  modbus
| modbus-discover:
|   sid 0x01:
|     Slave ID data: \x0F\x00\x00\x00
|     Device identification: Schneider Electric Modicon M221
|   sid 0x02:
|     error: Illegal function
```

## Chaining Opportunities
- Success usually requires prior **[[02 - Network Scanning and Enumeration]]** to pivot into the OT network.
- Often chained with **[[21 - ICS SCADA Architecture Security]]** for a comprehensive physical impact.
- Relies on weaknesses identified in **[[08 - Active Directory Enumeration]]** to compromise the SCADA servers managing the PLCs.

## Related Notes
- [[11 - MQTT Unauthenticated Broker Exploitation]]
- [[12 - CoAP Protocol Attacks]]
- [[14 - Shodan for IoT Device Discovery]]

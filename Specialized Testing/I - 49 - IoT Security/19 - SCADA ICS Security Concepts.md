---
tags: [iot, pentesting, hardware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.19 SCADA ICS Security Concepts"
---

# 49.19 SCADA ICS Security Concepts

## 1. Introduction

Supervisory Control and Data Acquisition (SCADA) and Industrial Control Systems (ICS) form the cyber-physical backbone of modern critical infrastructure. They manage the power grid, water treatment facilities, nuclear centrifuges, oil pipelines, and advanced manufacturing floors. 

Historically, ICS networks relied on "security by obscurity" and physical isolation (the "air gap"). As Industry 4.0 drives the convergence of Information Technology (IT) and Operational Technology (OT), these systems are increasingly connected to corporate networks and the internet. The fundamental problem is that ICS hardware and protocols were engineered decades ago for reliability, real-time determinism, and safety—*not* cybersecurity. Consequently, compromising a SCADA network often bypasses the digital realm and manifests as kinetic, physical destruction.

This note comprehensively covers the architecture, protocols, vulnerability landscape, and exploitation methodologies specific to SCADA and ICS environments.

## 2. Architecture: The Purdue Model

The Purdue Enterprise Reference Architecture (PERA) is the foundational model for ICS network segmentation. A typical OT environment is broken into functional levels.

- **Level 5/4 (Enterprise IT Network)**: Corporate desktops, ERP systems, email.
- **Level 3.5 (Industrial Demilitarized Zone - IDMZ)**: Firewalls, proxy servers, jump hosts, and patch management servers separating IT and OT.
- **Level 3 (Site Operations)**: Manufacturing Execution Systems (MES), Historians (databases tracking physical state over time).
- **Level 2 (Control Systems)**: Human-Machine Interfaces (HMIs), Engineering Workstations (EWS), SCADA supervisory servers.
- **Level 1 (Basic Control)**: Programmable Logic Controllers (PLCs), Remote Terminal Units (RTUs), Intelligent Electronic Devices (IEDs).
- **Level 0 (Physical Process)**: Sensors (temperature, pressure) and Actuators (valves, motors, pumps).

## 3. Attack Surface Diagram

```text
       [Enterprise IT Network] (Levels 4 & 5)
                 |
========[ Corporate Firewall ]===================================
                 |
       [Industrial DMZ (IDMZ)] (Level 3.5) -- (Jump Servers / Historian Replicas)
                 |
========[ OT Edge Firewall ]=====================================
                 |
       [Supervisory Control] (Level 2 & 3)
         +---------------+    +-----------------+    +---------------+
         |   SCADA HMI   |    | Eng. Workstation|    | OT Historian  |
         | (Monitors GUI)|    | (Programs PLCs) |    | (Data Logger) |
         +---------------+    +-----------------+    +---------------+
                 |                    |                      |
-------------------------------------------------------------------------
                 |                    |
       [Local Controllers] (Level 1)
         +---------------+    +-----------------+
         |     PLC 1     |    |      RTU 1      |
         | (Modbus/DNP3) |    | (Remote Comm)   |
         +---------------+    +-----------------+
                 |                    |
=========================================================================
                 |                    |
       [Physical Process] (Level 0)
         +---------------+    +-----------------+
         | Actuator Valve|    | Temp Sensor     |
         +---------------+    +-----------------+
```

## 4. Insecure-by-Design Protocols

The Achilles heel of ICS is its reliance on legacy industrial protocols that universally lack authentication, encryption, and integrity checks. If an attacker can route packets to an ICS protocol port, they can usually control the process.

### Modbus TCP (Port 502)
Modbus is the granddaddy of industrial protocols.
- **Structure**: A Master (HMI/SCADA) requests data from or writes data to a Slave (PLC/RTU). Data is stored in Coils (booleans) and Registers (16-bit integers).
- **Vulnerability**: Modbus TCP wraps the serial Modbus protocol inside a TCP packet. There is absolute zero authentication. 
- **Exploitation**: An attacker can simply use a Python script or Metasploit to write to a coil, instantly opening a physical valve.
  ```bash
  # Using standard penetration testing tools to write to Modbus Coil 0
  msfconsole -x "use auxiliary/scanner/scada/modbusclient; set RHOSTS 192.168.1.100; set DATA 1; set ACTION WRITE_COIL; set DATA_ADDRESS 0; run"
  ```

### Siemens S7 Comm (Port 102)
Used heavily in Siemens SIMATIC PLCs.
- **Vulnerability**: Older iterations (S7-300, S7-400) suffer from replay attacks. An attacker can record the traffic of an Engineering Workstation deploying a logic block to a PLC, alter the binary logic, and replay it.
- **Stuxnet Context**: Stuxnet famously exploited S7 communications to inject malicious step-logic into the PLCs controlling Iranian nuclear centrifuges, spinning them out of control while reporting "normal operations" to the HMI.

### Other Notable Protocols
- **DNP3 (Port 20000)**: Used in the power sector. Vulnerable to interception and unauthorized command execution if Secure Authentication (DNP3-SA) is not implemented.
- **BACnet (UDP 47808)**: Building automation. Completely unauthenticated. Allows attackers to control HVAC systems, potentially causing overheating in server rooms.
- **EtherNet/IP (TCP/UDP 44818)**: CIP (Common Industrial Protocol) over Ethernet. Prone to unauthenticated firmware updates and denial of service.

## 5. ICS Attack Methodology and the ICS Kill Chain

Attacking an ICS environment requires a specialized kill chain (e.g., the SANS ICS Cyber Kill Chain), divided into two phases.

### Phase 1: IT Compromise and OT Discovery
1. **Initial Access**: Phishing an engineer, compromising a VPN, or exploiting an internet-exposed IT asset.
2. **Pivoting to OT**: Compromising the jump host in the IDMZ or finding a dual-homed machine that bridges IT and OT (a massive architectural violation, but incredibly common).
3. **Passive OT Reconnaissance**: Active scanning (like `nmap`) can crash fragile PLCs. Attackers rely on passive network sniffing (Wireshark on spanned ports) to build an asset inventory and map the physical processes.

### Phase 2: ICS Exploitation and Kinetic Impact
1. **Targeting the EWS/HMI**: The attacker compromises the Engineering Workstation or HMI using standard IT exploits (Windows local privilege escalation, credential dumping).
2. **Process Comprehension**: The attacker studies the HMI screens and the Historian data to understand the physical process (e.g., "Coil 4 controls the chlorine valve").
3. **Execution/Manipulation**: 
   - *Loss of View*: Disabling the HMI so operators are blind to the physical process.
   - *Loss of Control*: Preventing operators from sending commands.
   - *Manipulation of Control*: Sending malicious setpoints to the PLCs to over-pressurize a pipeline or halt a manufacturing line.

## 6. Deep Dive: The Triton (TRISIS) Malware

To understand advanced ICS exploitation, one must analyze TRITON.
- **Target**: Triconex Safety Instrumented Systems (SIS). SIS are the failsafe controllers designed to shut down a plant if the primary PLCs fail or cause an unsafe condition (e.g., shutting off gas if pressure is too high).
- **The Exploit**: Attackers gained access to the OT network, compromised the Engineering Workstation, and reverse-engineered the proprietary TriStation protocol.
- **The Payload**: They injected a custom backdoor into the firmware of the SIS controllers. The goal was incredibly dangerous: silently disable the safety system, allowing a subsequent attack on the primary PLCs to cause a massive, unmitigated physical explosion.

## 7. Defenses and Mitigation

1. **Strict Purdue Model Enforcement**: Implement rigorous firewall rules between IT, the IDMZ, and OT. Drop all traffic from IT attempting to directly route to Level 1 PLCs.
2. **Unidirectional Security Gateways (Data Diodes)**: Use hardware-enforced one-way data transfers. This allows the OT Historian to push data to the IT network for analytics, but makes it physically impossible for IT to send packets back into the OT network.
3. **Network Security Monitoring (NSM)**: Deploy specialized OT IDS (e.g., Nozomi Networks, Claroty, Dragos). These systems passively parse proprietary protocols (S7, DNP3, CIP) and alert on anomalies, such as an unauthorized engineering workstation attempting to push code to a PLC.
4. **Secure Remote Access**: Mandate MFA and jump hosts with session recording for any vendor or engineer attempting to remotely access the OT environment.

## 8. Chaining Opportunities

- **VPN Compromise to OT Jump Host**: Exploiting a perimeter VPN vulnerability (e.g., Fortinet or Pulse Secure), dumping Active Directory credentials, and using those credentials to RDP into the OT Jump Server located in the IDMZ.
- **Dual-Homed Workstation Pivot**: Finding a rogue desktop connected to both the corporate Wi-Fi and the physical OT switch. Exploiting the workstation via a malicious macro, then bridging the adapters to route Metasploit traffic directly to unauthenticated Modbus endpoints.

## 9. Related Notes
- [[20 - Defense Network Segmentation Patch Management]]
- [[18 - Medical Device Security Overview]]
- [[01 - Active Directory Lateral Movement]]
- [[04 - Hardware Hacking via UART and JTAG]]

---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.01 Introduction to ICS and SCADA Security"
---

# Introduction to ICS and SCADA Security

Industrial Control Systems (ICS) and Supervisory Control and Data Acquisition (SCADA) systems form the technological foundation of modern critical infrastructure. Unlike traditional IT environments where data confidentiality is often paramount, operational technology (OT) environments prioritize **Availability** and **Safety** above all else. 

This fundamental shift in the CIA triad (often inverted to AIC—Availability, Integrity, Confidentiality in ICS contexts) drastically alters the methodology, risk appetite, and tooling used during security assessments. A misconfigured Nmap scan in an IT environment might cause a temporary web server DoS; in an OT environment, it could cause a Programmable Logic Controller (PLC) to halt, potentially resulting in catastrophic physical damage, loss of life, or environmental hazards.

---

## The Purdue Enterprise Reference Architecture (PERA)

The Purdue Model provides a structural hierarchy for ICS network segmentation. Understanding this model is critical for VAPT professionals to map attack paths from corporate IT networks down to physical controllers.

### ASCII Diagram: The Purdue Model for ICS Architecture

```text
+-------------------------------------------------------------------+
|                     Enterprise Network (IT)                       |
+-------------------------------------------------------------------+
| Level 5: Enterprise Network (Corporate IT, Email, ERP)            |
| Level 4: Site Business Planning and Logistics Network             |
+-------------------------------------------------------------------+
                               | (IT/OT DMZ - Level 3.5)
                               v
======================== FIREWALL / DMZ =============================
                               | (Historians, Patch Servers, Proxies)
                               v
+-------------------------------------------------------------------+
|             Industrial Control System Network (OT)                |
+-------------------------------------------------------------------+
| Level 3: Site Manufacturing Operations and Control                |
|          (Production Control, centralized HMI, Domain Controllers)|
+-------------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------+
| Level 2: Area Supervisory Control                                 |
|          (Local HMI, SCADA nodes, Supervisory Control)            |
+-------------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------+
| Level 1: Basic Control                                            |
|          (PLCs, RTUs, IEDs - The "Brains" of the operation)       |
+-------------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------+
| Level 0: Process (Physical)                                       |
|          (Sensors, Actuators, Motors, Pumps, Valves)              |
+-------------------------------------------------------------------+
```

### Breakdown of the Purdue Levels
- **Level 4/5 (IT Network):** Standard corporate environments. Attackers usually breach here first via phishing or exposed RDP.
- **Level 3.5 (IDMZ):** The Industrial Demilitarized Zone. Critical boundary. Ideally, no direct traffic should pass between IT and OT without terminating here first. 
- **Level 3 (Operations):** Centralized control. Systems here manage overall plant operations. Compromising an Engineering Workstation (EWS) at this level is the "Holy Grail" for ICS attackers.
- **Level 2 (Supervisory Control):** Human-Machine Interfaces (HMIs) directly interacting with Level 1 controllers.
- **Level 1 (Basic Control):** Programmable Logic Controllers (PLCs), Remote Terminal Units (RTUs). These devices run real-time operating systems (RTOS) and have extreme sensitivity to network anomalies.
- **Level 0 (Physical Process):** The actual physical world components.

---

## Key ICS/SCADA Components

### Programmable Logic Controller (PLC)
A hardened, microprocessor-based controller designed for manufacturing processes. PLCs read digital/analog inputs, execute custom logic (often written in Ladder Logic or Structured Text), and trigger physical outputs. They typically operate at Level 1 of the Purdue Model.

### Remote Terminal Unit (RTU)
Similar to PLCs but usually deployed over wide geographical areas (e.g., pipelines, electrical grids). RTUs frequently rely on wireless, microwave, or cellular communication telemetry back to a centralized SCADA Master.

### Human-Machine Interface (HMI)
The interface (often a Windows-based PC or specialized touch panel) that allows human operators to monitor the state of a process, modify control parameters, and override automated systems. 

### Engineering Workstation (EWS)
Specialized workstations used by plant engineers to write, compile, and upload logic to PLCs/RTUs. These workstations hold the proprietary software (e.g., Siemens TIA Portal, Rockwell Studio 5000) and have the highest level of administrative access to the controllers.

### Data Historian
A database server (often located in Level 3 or the DMZ) that aggregates and stores time-series data from the ICS process. Attackers often target historians because they sit at the boundary and frequently have bi-directional trusts.

---

## Vulnerability Landscape in OT

Unlike IT systems, which undergo regular patch cycles, OT systems suffer from unique, systemic vulnerabilities:

1. **Insecure-by-Design Protocols:** Modbus, DNP3, and S7Comm were designed decades ago for closed, serial networks. They entirely lack authentication, authorization, and encryption. 
2. **Patching Paralysis:** Upgrading a PLC firmare might require halting a billion-dollar manufacturing line. Thus, devices routinely run vulnerabilities from 10+ years ago.
3. **Fragile TCP/IP Stacks:** The network stacks on many Level 1 devices are notoriously fragile. A standard Nmap SYN scan or a Nessus vulnerability scan can cause the device stack to crash, requiring a physical power cycle.
4. **Convergence Risks:** The modern push for "Industry 4.0" and IoT has resulted in bridging previously air-gapped OT networks to the internet or corporate IT networks.

---

## Active vs. Passive Security Assessments

Because of the fragility of Level 1 and Level 2 devices, ICS VAPT heavily relies on passive assessment techniques.

### Passive Assessment Methodology
1. **Network Tap / SPAN Port:** The primary method for data collection. Pcap analysis provides near complete visibility into the cleartext protocols.
2. **Asset Identification:** Utilizing tools like `Zeek` or `Malcolm` to parse ICS protocols from pcaps to identify PLC IP addresses, manufacturer, firmware versions, and communication maps.
3. **Configuration Review:** Offline review of PLC logic files, HMI project files, and firewall rule bases. 
4. **Vulnerability Mapping:** Correlating passively identified firmware versions against known CVE databases (e.g., ICS-CERT advisories).

### Active Assessment Methodology (Use with Extreme Caution)
Active scanning should **never** be performed on a live production ICS network without explicit client authorization and physical engineers standing by the emergency stop (E-stop) buttons.
1. **Targeted Scanning:** Instead of scanning a whole subnet `192.168.1.0/24`, targeted identification of known IT-centric devices (e.g., Windows HMIs).
2. **Protocol-Specific Probing:** Using specialized scripts (like Nmap's `modbus-discover` or `s7-info`) rather than aggressive generic port scanning. 
3. **Test Environments:** Active exploitation should only occur in digital twin environments, FAT (Factory Acceptance Testing), or isolated lab setups.

---

## Real-World Threat Actors and ICS Malware

Understanding how real adversaries operate provides the blueprint for Red Teaming ICS networks.

### Stuxnet (2010)
The watershed moment for ICS security. Stuxnet targeted Iranian uranium enrichment centrifuges. It spread via USB, exploited Windows zero-days to reach the EWS, and intercepted Siemens S7 protocol communications. It modified the PLC logic to spin centrifuges at catastrophic speeds while replaying normal telemetry to the HMIs, hiding the physical destruction from operators.

### BlackEnergy (2015)
Targeted the Ukrainian power grid. The attackers compromised the IT network via spear-phishing, stole VPN credentials, and traversed to the OT network. They then seized control of the HMIs, manually switching off breakers (causing a massive blackout), and bricked serial-to-ethernet converters using malicious firmware updates.

### CrashOverride / Industroyer (2016)
The first malware framework explicitly designed to automate power grid disruptions. It included modular payloads capable of speaking native ICS protocols (IEC 60870-5-104, IEC 61850, OPC DA) to interact directly with RTUs and protective relays without needing to hijack an HMI.

---

## Assessment Tooling for ICS

While traditional IT tools like Metasploit and Nmap are relevant, the ICS domain requires specialized toolsets:

- **Grassmarlin / Malcolm:** Passive network mapping and protocol identification.
- **Wireshark:** ICS-specific dissectors (Modbus, DNP3, CIP, S7Comm, IEC-104).
- **S7Scan / PLCScan:** Specific active enumerators for Siemens and generalized PLCs.
- **ISF (Industrial Security Framework):** An exploitation framework heavily inspired by Metasploit but containing modules for attacking PLCs, RTUs, and specific industrial protocols.

---

## Chaining Opportunities

1. **Initial Access to Lateral Movement:** Phishing an enterprise user -> Dumping credentials -> Using stolen creds to access the VPN/Citrix portal leading into the OT DMZ.
2. **DMZ to Operations:** Compromising the Data Historian via a web vulnerability -> Pivot through dual-homed Historian into the Level 3 Operations network.
3. **EWS to PLC:** Dumping project files from an Engineering Workstation -> Modifying the logic to introduce a backdoor -> Uploading the modified logic to the Level 1 PLC.

---

## Related Notes
- [[02 - Modbus Protocol Exploitation]]
- [[03 - DNP3 Protocol Exploitation]]
- [[04 - Siemens S7 Protocol Attacks]]
- [[05 - Attacking SAP NetWeaver and RFCs]]

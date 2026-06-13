---
tags: [iot, pentesting, hardware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.18 Medical Device Security Overview"
---

# 49.18 Medical Device Security Overview

## 1. Introduction

The Internet of Medical Things (IoMT) represents one of the most critical subsets of the IoT ecosystem. Security failures in this domain do not simply result in data loss or financial damage—they pose an immediate, direct threat to human life. Medical devices range from implantable cardioverter-defibrillators (ICDs) and insulin pumps to massive hospital infrastructure components like MRI machines, CT scanners, and patient monitoring networks.

The overarching challenge in IoMT security is the conflict between clinical availability and cybersecurity. Medical devices must be instantly accessible to healthcare professionals in emergency scenarios, which historically led to architectures with hardcoded credentials, absent authentication, and widespread use of legacy, unpatched operating systems. Compounding this is the rigid regulatory landscape (e.g., FDA, HIPAA), which historically made manufacturers hesitant to issue software patches for fear of triggering expensive recertification processes.

This note explores the unique architecture, attack surface, communication protocols, and profound exploitation risks associated with medical devices.

## 2. Regulatory Landscape and Risk Models

Unlike consumer IoT, medical device security is heavily scrutinized by regulatory bodies.
- **FDA Pre-Market and Post-Market Guidance**: Modern guidelines require manufacturers to build in cybersecurity controls (e.g., secure boot, updatability) and maintain a Software Bill of Materials (SBOM).
- **HIPAA/HITECH**: Dictates strict controls over Electronic Protected Health Information (ePHI). A compromised medical device often leads directly to massive ePHI breaches, triggering severe regulatory penalties.
- **Risk Model Shift**: The traditional CIA triad (Confidentiality, Integrity, Availability) is often inverted in healthcare. Availability and Integrity are paramount. If a patient monitor's data (Integrity) is altered, or if an infusion pump is disabled (Availability), patient mortality is a direct consequence.

## 3. Architecture of the IoMT Ecosystem

The IoMT ecosystem is divided into three primary tiers: Implantable/Wearable, Capital Equipment, and Clinical Backend.

### Tiers of IoMT
1. **Body Area Networks (BANs)**: Pacemakers, neurostimulators, and insulin pumps. These communicate via extremely low-power RF (Medical Implant Communication Service - MICS band) or BLE to an external bedside telemetry wand or smartphone.
2. **Point-of-Care & Capital Equipment**: Infusion pumps, ECG monitors, Ultrasound and MRI machines. These usually sit on specialized clinical VLANs, running embedded Windows (CE, XP, 7, 10 IoT) or Linux, and communicate over Ethernet or Wi-Fi.
3. **Clinical Backend (Hospital Information Systems)**: Electronic Health Records (EHR), Picture Archiving and Communication Systems (PACS), and Central Monitoring Stations. They aggregate data from endpoints using healthcare-specific protocols.

## 4. Attack Surface Diagram

```text
                                +-------------------------------------------+
                                |      Hospital Information System (HIS)    |
                                |   +----------+             +----------+   |
                                |   |   EHR    |             |  PACS    |   |
                                |   +----------+             +----------+   |
                                +-------------------------------------------+
                                          ^                       ^
                                          | HL7 / FHIR            | DICOM
                                          v                       v
+-----------------------+       +-------------------------------------------+
|   Implantable Device  |       |         Point-of-Care Equipment           |
|  (e.g., Pacemaker)    |       |   +----------------+   +----------------+ |
|                       | MICS /|   | Infusion Pump  |   |   MRI Machine  | |
| +-------------------+ | BLE   |   | (Embedded OS)  |   | (Legacy WinXP) | |
| | Proprietary Logic | | <---> |   +----------------+   +----------------+ |
| +-------------------+ |       |           ^                     ^         |
+-----------------------+       +-----------|---------------------|---------+
                                            |                     |
   [Attacker with SDR /             [Attacker on LAN via          |
    Proximity Device]                Compromised Workstation]-----+
```

## 5. Medical-Specific Protocols and Flaws

Standard IT protocols are heavily supplemented by healthcare-specific protocols that are notoriously insecure by design.

### Health Level Seven (HL7) and FHIR
HL7 (specifically version 2.x and 3) is the global standard for the transfer of clinical and administrative data.
- **The Flaw**: HL7 v2 transmits messages over TCP (often port 2575) in pure plaintext. There is no built-in encryption, authentication, or message integrity validation.
- **Exploitation**: An attacker on the clinical VLAN can passively sniff patient data (ePHI), or worse, actively inject malicious HL7 messages. By sending crafted MLLP (Minimum Lower Layer Protocol) packets, an attacker can alter a patient's blood type in the EHR or change drug allergy statuses, leading to fatal clinical decisions.

### DICOM (Digital Imaging and Communications in Medicine)
DICOM is used for handling, storing, and transmitting medical images (X-Rays, MRIs).
- **The Flaw**: Like HL7, standard DICOM implementations communicate without TLS and lack robust authentication, relying on "Application Entity (AE) Titles" which act more like usernames without passwords.
- **Exploitation**: An attacker can intercept DICOM traffic and modify image pixel data in transit. Researchers have demonstrated the ability to programmatically add or remove lung cancer nodules from CT scans in real-time as they transit from the scanner to the PACS, entirely subverting radiologist diagnoses.

## 6. Common Attack Vectors and Deep Dives

### Legacy Operating Systems and Missing Patches
Capital equipment (like an MRI machine costing $2M) has an operational lifespan of 10-15 years.
- **Vector**: They frequently run end-of-life operating systems like Windows XP or Windows 7. 
- **Exploitation**: These devices are highly susceptible to older, reliable exploits like MS08-067 or EternalBlue (MS17-010). Ransomware operators (e.g., WannaCry, Ryuk) frequently cripple hospitals precisely because these critical devices get infected, rendering oncology or radiology departments inoperable.

### Battery Depletion Attacks (Implantables)
Implantable devices are constrained by battery life. Surgery is required to replace them.
- **Exploitation**: An attacker with a proximate RF transmitter can continuously "wake up" the implant by spamming telemetry requests. Even if the attacker cannot break the encryption or send malicious commands, keeping the processor awake drains a 10-year battery in a matter of weeks, constituting a physical Denial of Service requiring immediate surgical intervention.

### Hardcoded Service Credentials
To ensure vendor technicians can service equipment in emergencies, manufacturers often leave undocumented, hardcoded credentials in the firmware (e.g., `service:service123` or backdoors via Telnet/SSH).
- **Exploitation**: Attackers extract the firmware, reverse-engineer the binaries to recover the hash/plaintext, and can trivially gain root access across every device of that model globally.

## 7. Exploitation Ethics and Safe Testing

Penetration testing in healthcare is fundamentally different from traditional VAPT.
- **CRITICAL RULE**: Never execute active exploits (e.g., memory corruption, aggressive port scanning, or spoofing) against live, patient-connected medical equipment.
- **Methodology**: Testing must be performed on dedicated staging equipment in a lab environment. Even a simple `nmap` version scan can cause a legacy infusion pump's network stack to panic, resulting in a reboot or cessation of drug delivery. Passive traffic analysis (PCAP) is preferred for live clinical networks.

## 8. Defenses and Mitigation Strategies

Securing IoMT requires a "Zero Trust" and compensating control mindset, as the endpoints themselves often cannot be patched or secured natively.
1. **Micro-segmentation and VLAN Isolation**: Medical devices should be on strictly segmented VLANs. An infusion pump should only be able to communicate with the specific pharmacy server it requires, blocking all other lateral traffic.
2. **Compensating Controls**: Where a device lacks native TLS, utilize network-level encryption tunnels (e.g., IPsec) or place inline security appliances (like a transparent firewall) in front of the device to perform Deep Packet Inspection (DPI) on clinical protocols.
3. **Passive Anomaly Detection**: Utilizing solutions like Medigate, Claroty, or Armis that ingest span port traffic. They build baselines of acceptable medical device behavior (e.g., "The MRI machine only talks DICOM to the PACS") and trigger alerts on deviations (e.g., "The MRI machine is executing an SMB connection to a workstation").

## 9. Chaining Opportunities

- **Phishing to Lateral Movement to PACS Alteration**: Compromising a nurse's workstation via a phishing payload, stealing their Active Directory credentials, pivoting into the clinical VLAN, and silently modifying DICOM images en route to the centralized archive to disrupt hospital operations.
- **Guest Wi-Fi to IoMT Bypass**: Finding a misconfigured Guest Wi-Fi network that bleeds into the MICS/BLE range of bedside telemetry monitors, allowing an external attacker in the hospital lobby to spoof telemetry data.

## 10. Related Notes
- [[19 - SCADA ICS Security Concepts]]
- [[20 - Defense Network Segmentation Patch Management]]
- [[01 - Active Directory Lateral Movement]]
- [[11 - Exploiting Legacy Windows Services (SMB, RDP)]]
- [[08 - Cryptography and Plaintext Protocol Exploitation]]

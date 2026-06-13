---
tags: [snmp, network, enumeration, info-disclosure, vapt, protocol-attack]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.08 SNMP"
---

# Simple Network Management Protocol (SNMP) Exploitation

The Simple Network Management Protocol (SNMP) is a widely deployed, foundational networking protocol used for the management and monitoring of network-connected devices in IP networks. Devices that typically support SNMP include routers, switches, servers, workstations, printers, modem racks, and more. While incredibly useful for network administrators, SNMP is historically plagued by severe security misconfigurations, most notably default community strings and the lack of encryption in early versions (v1 and v2c).

## Protocol Overview and Architecture

SNMP operates primarily over UDP port 161 (for polling/requests) and UDP port 162 (for asynchronous traps/notifications). The architecture relies on an agent-manager model:
- **SNMP Manager**: The centralized system (often a Network Management Station or NMS) that polls agents, requesting information or sending configuration updates.
- **SNMP Agent**: A software module running on the managed device that maintains local data variables and reports them to the Manager.
- **MIB (Management Information Base)**: A hierarchical namespace containing Object Identifiers (OIDs). MIBs define the structure of the management data on a device.
- **OID (Object Identifier)**: A sequence of numbers separated by dots (e.g., `1.3.6.1.2.1.1.1.0`) that uniquely identifies a variable or data point within the MIB hierarchy.

### The SNMP Version Problem

SNMP has three primary versions, each with distinct security characteristics:
1. **SNMPv1**: The original specification. Authentication relies solely on a plaintext "community string" (essentially a password). Zero encryption.
2. **SNMPv2c**: Introduced bulk retrieval capabilities (GetBulk) but retained the weak community-string-based authentication ("c" stands for community-based). Zero encryption.
3. **SNMPv3**: Introduced a robust cryptographic security model, offering Authentication (MD5/SHA) and Privacy (DES/AES encryption).

From an attacker's perspective, finding SNMPv1 or v2c on a network is a goldmine due to its cleartext transmission and frequent use of vendor defaults like `public` (for Read-Only) or `private` (for Read-Write).

---

## The Attack Flow

```ascii
+-----------------------+                            +-------------------------+
|                       |  1. SNMP GetRequest        |                         |
|      Attacker         |  Community: 'public'       |      SNMP Agent         |
|   (Kali Linux VM)     +--------------------------->+   (Router/Switch/Host)  |
|                       |                            |                         |
|   Tools:              |  2. SNMP Response          |   Port: UDP/161         |
|   - snmpwalk          |  Data: SysDesc, Interfaces,+                         |
|   - onesixtyone       +<---------------------------+   MIB Hierarchy         |
|   - snmp-check        |  Routing Tables, Processes |                         |
|                       |                            |                         |
+-----------------------+                            +-------------------------+
           |                                                      ^
           |                                                      |
           |               3. SNMP SetRequest                     |
           +------------------------------------------------------+
                           Community: 'private'
                           Data: OID modification (e.g., Routing, Config)
```

---

## Core Vulnerabilities

### 1. Default Community Strings
The most common flaw in SNMP deployments is the failure to change default community strings. Vendors often ship devices with the read-only (RO) community string set to `public` and the read-write (RW) string set to `private`. Even if the defaults are changed, network administrators sometimes use highly predictable strings like `cisco`, `admin`, `network`, `monitor`, `manager`, or company-specific names.

### 2. Information Disclosure via SNMP Polling
With valid read-only access, an attacker can dump extensive amounts of sensitive information from the device. This process is often referred to as "walking the MIB tree."
Information commonly exposed includes:
- **System details**: OS version, hostname, uptime.
- **Network Interfaces**: IP addresses, subnet masks, MAC addresses, interface status.
- **Routing Tables**: Active routes, gateways, which helps map internal networks.
- **Running Processes and Services**: Extremely critical on servers (e.g., exposing running AV, backup agents, web servers).
- **Installed Software**: Including version numbers for CVE mapping.
- **User Accounts**: Valid usernames on a Windows or Linux system.

### 3. Unauthorized Modification (Read-Write Exploitation)
If the attacker obtains a Read-Write (RW) community string, they transcend information disclosure and achieve remote configuration capabilities. This can lead to:
- Overwriting device configurations.
- Altering routing tables to sinkhole or intercept traffic (Man-in-the-Middle).
- Rebooting the device.
- On some systems, executing arbitrary commands or altering access control lists (ACLs).

---

## Enumeration and Exploitation Mechanics

### Step 1: Locating SNMP Services
Since SNMP is UDP-based, standard TCP scans will miss it.
```bash
# Nmap UDP scan targeting SNMP
sudo nmap -sU -p 161 10.10.10.0/24 --open

# Nmap script to check for default community strings
sudo nmap -sU -p 161 --script snmp-brute 10.10.10.50
```

### Step 2: Brute-Forcing Community Strings
If standard defaults aren't in play, we use tools like `onesixtyone`, a fast SNMP scanner that tests community strings against a target list.
```bash
# Creating a small dictionary
echo "public" > dict.txt
echo "private" >> dict.txt
echo "manager" >> dict.txt
echo "cisco" >> dict.txt

# Running onesixtyone
onesixtyone -c dict.txt 10.10.10.50
```

Hydra can also be leveraged for this task:
```bash
hydra -P dict.txt -v 10.10.10.50 snmp
```

### Step 3: Walking the MIB Tree
Once a valid community string is found, we extract the data using `snmpwalk`.

```bash
# Basic snmpwalk targeting the entire tree using SNMPv2c
snmpwalk -v 2c -c public 10.10.10.50

# Targeting a specific OID (e.g., hrSWRunName for running processes)
snmpwalk -v 2c -c public 10.10.10.50 1.3.6.1.2.1.25.4.2.1.2
```

**Common OIDs for Enumeration (Windows/Linux):**
- `1.3.6.1.2.1.1.1` - System Description
- `1.3.6.1.2.1.1.5` - Hostname
- `1.3.6.1.2.1.25.4.2.1.2` - Running Processes
- `1.3.6.1.2.1.25.6.3.1.2` - Installed Software
- `1.3.6.1.4.1.77.1.2.25` - Local User Accounts (Windows)
- `1.3.6.1.2.1.6.13.1.3` - Active TCP Connections

### Step 4: Automated Data Extraction
Parsing raw `snmpwalk` output can be tedious. `snmp-check` is a Ruby script that automates the collection and formatting of SNMP data into readable categories.
```bash
snmp-check -v 2c -c public 10.10.10.50
```

### Advanced: IPv6 SNMP Enumeration
SNMP often listens on IPv6 as well, providing a bypass if IPv4 access control lists (ACLs) block port 161.
```bash
snmpwalk -v 2c -c public udp6:[fe80::1234:5678:9abc:def0]
```

---

## Modifying Configurations (RW Community Strings)

If you uncover the RW string (e.g., `private`), you can use `snmpset` to alter parameters.
For example, to change the system contact information (often a harmless proof of concept):
```bash
snmpset -v 2c -c private 10.10.10.50 1.3.6.1.2.1.1.4.0 s "hacked@attacker.com"
```
*Note: `s` indicates the data type is a string.*

In more severe scenarios, RW access to Cisco routers can be used to TFTP upload a new `running-config` that grants the attacker a backdoor account or alters routing behavior, effectively compromising the entire network segment.

---

## Defensive Countermeasures & Hardening

1. **Migrate to SNMPv3**: This is the most crucial step. Disable v1 and v2c completely. SNMPv3 provides confidentiality via AES encryption and authentication via SHA, mitigating both eavesdropping and brute-force/replay attacks.
2. **Change Default Community Strings**: If v2c must be used (due to legacy device constraints), treat the community string like a complex password. Do not use guessable terms.
3. **Network Segmentation and ACLs**: SNMP should never be exposed to the internet. Internally, restrict access to port 161/162 only from dedicated management subnets or NMS IP addresses.
4. **Disable SNMP if Unused**: If a device does not need to be monitored centrally, disable the SNMP service entirely to reduce the attack surface.
5. **View-Based Access Control Model (VACM)**: Implement VACM to restrict which OIDs the community string can query. Do not grant access to the entire MIB tree if the NMS only needs to read interface traffic stats.

---

## Chaining Opportunities

- **SNMP -> Passwords/Credentials**: Often, routing configs pulled via SNMP contain passwords or keys (sometimes hashed, sometimes cleartext) which can be cracked or reused.
- **SNMP -> Vulnerability Exploitation**: By enumerating exactly which software versions are running (`1.3.6.1.2.1.25.6.3.1.2`), an attacker can quietly select a tailored exploit without aggressively port-scanning the target.
- **SNMP -> Lateral Movement**: Extracting the routing tables and ARP caches via SNMP provides a map of hidden subnets, VPN tunnels, and trust relationships that the attacker can use to pivot.

## Related Notes
- [[04 - Port Scanning and Enumeration]]
- [[01 - Reconnaissance Fundamentals]]
- [[11 - NetBIOS — Enumeration, NBNS Poisoning]]
- [[10 - SMB — EternalBlue, Null Session, Relay Attacks]]


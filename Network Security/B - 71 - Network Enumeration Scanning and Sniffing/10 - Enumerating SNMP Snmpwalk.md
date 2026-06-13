---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.10 Enumerating SNMP Snmpwalk"
---

# Enumerating SNMP: Architecture and Snmpwalk

## Introduction to SNMP
The Simple Network Management Protocol (SNMP) is an application-layer protocol used extensively for network management. It is designed to monitor, configure, and manage network devices such as routers, switches, firewalls, servers, printers, and IoT devices. SNMP operates primarily over UDP ports 161 (for general queries and responses) and 162 (for asynchronous alerts known as "Traps" sent from devices to the central management station).

For a penetration tester, SNMP is an absolute goldmine of information. Because it is explicitly designed to manage the entire device, a successfully queried SNMP service can reveal intimate details about the target's internal configuration, routing tables, network interfaces, running software, active TCP/UDP ports, and even local user accounts. In highly misconfigured environments, SNMP can even be used to modify device configurations (e.g., changing routing tables, downloading configuration files, or rebooting the device), transitioning an enumeration vector into a direct exploitation vector.

## The Architecture of SNMP

### SNMP Versions and Security
Understanding the versions of SNMP is critical, as the security model changed drastically across iterations:
- **SNMPv1:** The original specification. Extremely insecure. Authentication is based on a plaintext "Community String" sent with every packet. It supports no encryption.
- **SNMPv2c:** The "c" stands for Community-Based. It introduced bulk retrieval capabilities (improving performance) and new data types, but retained the exact same plaintext Community String authentication model as v1. **This is the most commonly found and exploited version in internal enterprise networks.**
- **SNMPv3:** A massive security overhaul. It introduces true cryptographic authentication (MD5/SHA) and privacy/encryption (DES/AES). If SNMPv3 is properly configured, enumeration via brute-forcing is significantly harder, and sniffing the traffic yields encrypted ciphertext.

### Community Strings: The Keys to the Kingdom
In SNMPv1 and v2c, the "Community String" acts as a password. There are two primary types of access:
- **Read-Only (RO):** Allows the querying of information from the device. The default RO string is almost universally `public`.
- **Read-Write (RW):** Allows querying AND modifying the configuration of the device. The default RW string is often `private`.

If a network administrator deploys a router and leaves the default `public` or `private` strings active, any machine on the network can query or control that router.

### ASN.1, MIBs, and OIDs
SNMP payloads are encoded using Abstract Syntax Notation One (ASN.1), specifically using BER (Basic Encoding Rules).
SNMP organizes data hierarchically into a logical structure called the Management Information Base (MIB). The MIB is essentially a database schema that describes what data can be queried on a device.
Individual pieces of data within the MIB are addressed using Object Identifiers (OIDs). OIDs are sequences of numbers separated by dots, resembling a tree structure.
- Example OID: `1.3.6.1.2.1.1.1.0` (sysDescr) - Returns the system description (OS version, hardware).
- Example OID: `1.3.6.1.2.1.2.2.1.2` (ifDescr) - Returns the descriptions of network interfaces.
- Example OID: `1.3.6.1.4.1.77.1.2.25` - Specifically targets Windows systems to enumerate local user accounts.

Because remembering numerical OIDs is difficult, MIB files translate these numbers into human-readable names (like `sysDescr`). Penetration testers often maintain large databases of MIBs to interpret the numerical responses.

## Tool 1: Snmpwalk
`snmpwalk` is the fundamental command-line tool for querying SNMP devices. As the name implies, it "walks" the MIB tree. Instead of querying a single OID, you point it at a root node, and it recursively queries the device using `GETNEXT` requests to retrieve every OID underneath that node until the tree is exhausted.

### Basic Syntax
`snmpwalk -v [version] -c [community_string] [target_ip]`
- `-v 1` or `-v 2c`: Specifies the SNMP version. (Usually, you start with 2c).
- `-c public`: Specifies the community string.
- `target_ip`: The IP address of the target device.

**Example: Full System Walk**
`snmpwalk -v 2c -c public 192.168.1.254`
If successful, this command will dump thousands of lines of output to your terminal, detailing everything from system uptime to routing tables. It is highly recommended to redirect the output to a file:
`snmpwalk -v 2c -c public 192.168.1.254 > snmp_dump.txt`

### Targeted Walking
Dumping the entire tree is noisy and time-consuming. You can specify a specific OID to walk only a portion of the tree.
- **Enumerate System Information:** `snmpwalk -v 2c -c public 192.168.1.100 1.3.6.1.2.1.1`
- **Enumerate Running Processes (Host Resources MIB):** `snmpwalk -v 2c -c public 192.168.1.100 1.3.6.1.2.1.25.4.2.1.2`
- **Enumerate Installed Software:** `snmpwalk -v 2c -c public 192.168.1.100 1.3.6.1.2.1.25.6.3.1.2`
- **Enumerate Windows Users:** `snmpwalk -v 2c -c public 192.168.1.100 1.3.6.1.4.1.77.1.2.25`

## Tool 2: Brute-forcing with onesixtyone
If the default `public` or `private` community strings do not work, you must brute-force them. Because SNMP runs over UDP (a connectionless protocol), brute-forcing is incredibly fast. You don't have to wait for TCP handshakes.
`onesixtyone` is a purpose-built SNMP scanner and brute-forcer. It sends SNMP requests at a high rate and waits for valid responses.

**Usage:**
`onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 192.168.1.254`
- `-c`: Specifies the dictionary file containing potential community strings.
This tool can scan entire subnets rapidly to identify any device responding to a common community string.

## Tool 3: SNMP-Check
`snmp-check` is an automated enumeration script (similar to enum4linux, but for SNMP). Instead of giving you raw OID data like `snmpwalk`, it parses the results and formats them into highly readable, categorized sections (System Info, Network Interfaces, Routing Info, TCP Connections, User Accounts, Share Information).

**Usage:**
`snmp-check -v 2c -c public 192.168.1.100`

---

## ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                     SNMP Architecture & Enumeration Flow                    |
+-----------------------------------------------------------------------------+

      [ Attacker Machine ]                            [ Target Router/Server ]
      (Running snmpwalk)                                (IP: 10.0.0.1)
               |                                              |
               |                                              |
               | (1) UDP Port 161                             |
               |     SNMPv2c GETNEXT Request                  |
               |     Community: "public"                      |
               |     OID: 1.3.6.1.2.1.1 (system)              |
               |--------------------------------------------->|
               |                                              | [ Authentication Check ]
               |                                              | If "public" matches RO string:
               |                                              |    Process Request
               |                                              | Else:
               |                                              |    Drop Packet (No response)
               |                                              |
               | (2) SNMPv2c Response                         |
               |     OID: 1.3.6.1.2.1.1.1.0                   |
               |     Value: "Cisco IOS Software, C2960..."    |
               |<---------------------------------------------|
               |                                              |
               | (3) UDP Port 161                             |
               |     SNMPv2c GETNEXT Request                  |
               |     Community: "public"                      |
               |     OID: 1.3.6.1.2.1.1.1.0                   |
               |--------------------------------------------->|
               |                                              |
               | (4) SNMPv2c Response                         |
               |     OID: 1.3.6.1.2.1.1.2.0                   |
               |     Value: OID for Cisco Hardware            |
               |<---------------------------------------------|
               |                                              |
               |  (Process repeats automatically traversing   |
               |   the entire MIB tree structure using        |
               |   sequential GETNEXT requests)               |
               v
```

## Defensive Perspective and Mitigation
- **Upgrade to SNMPv3:** The absolute best defense is to disable SNMPv1 and v2c entirely and migrate to SNMPv3, ensuring strong cryptographic authentication and encryption are mandated.
- **Change Default Strings:** If legacy systems absolutely require v2c, immediately change the default `public` and `private` community strings to complex, random passwords. Treat community strings like administrative credentials.
- **Access Control Lists (ACLs):** Restrict SNMP access at the network level. Configure the SNMP daemon (and surrounding firewalls) to only accept UDP 161 traffic from specific, authorized IP addresses (e.g., the dedicated network monitoring server). Drop all other requests.
- **Disable Read-Write Access:** Unless explicitly required for remote management, never enable Read-Write community strings. Read-Only is sufficient for almost all monitoring purposes.

## Chaining Opportunities
- **SNMP to Routing Attacks:** If a Read-Write (RW) community string is discovered, an attacker can modify the routing tables of a core switch or router, redirecting all traffic through their machine to facilitate a massive Man-in-the-Middle attack. See [[26 - Advanced Routing Protocol Exploitation]].
- **Configuration Downloading:** RW access on Cisco devices allows an attacker to instruct the router via SNMP to upload its full `startup-config` (which contains passwords and hashes) to an attacker-controlled TFTP server. See [[32 - Exploiting Network Infrastructure Devices]].
- **Process Enumeration to Exploitation:** Enumerating running processes via SNMP reveals exactly what vulnerable services are running on the host, guiding subsequent exploitation efforts. See [[09 - Vulnerability Mapping and Exploit Selection]].
- **User Enumeration to Password Spraying:** Just like SMB, SNMP can leak local usernames, which are then fed into brute-force tools against SSH, RDP, or web portals. See [[12 - Password Spraying Techniques]].

## Related Notes
- [[04 - Nmap Advanced Port Scanning]]
- [[01 - Introduction to Network Protocols]]
- [[17 - Penetration Testing Network Appliances]]
- [[24 - Information Gathering via UDP Protocols]]

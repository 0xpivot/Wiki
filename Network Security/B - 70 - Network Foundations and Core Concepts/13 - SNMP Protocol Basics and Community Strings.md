---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.13 SNMP Protocol Basics and Community Strings"
---

# 70.13 SNMP Protocol Basics and Community Strings

## 1. SNMP Architecture
Simple Network Management Protocol (UDP 161/162) monitors devices.
- **Manager (NMS):** Polls data.
- **Agent:** Runs on target device.
- **MIB (Management Information Base):** Hierarchical tree of variables.
- **OID (Object Identifier):** Unique numeric path to a MIB variable.

## 2. Protocol Versions
- **v1:** Plaintext community strings (`public`/`private`).
- **v2c:** Adds bulk requests. Still plaintext.
- **v3:** Introduces strong authentication (MD5/SHA) and encryption (AES/DES).

## 3. Core Commands
- `GetRequest`: Fetch value.
- `GetNextRequest`: Fetch next value in MIB tree.
- `SetRequest`: Modify a value (requires write access).
- `Trap`: Asynchronous alert from Agent to Manager (UDP 162).

## 4. ASCII Diagram: SNMP Operations
```text
      [ NMS Manager ]                        [ Managed Device (Agent) ]
             |                                            |
             | --- GetRequest (UDP 161, OID X) ---------> |
             | <--- Response (Value Y) ------------------ |
             |                                            |
             | --- SetRequest (UDP 161, OID Z, Val W) --> |
             | <--- Response (Acknowledge) -------------- |
             |                                            |
             | <--- Trap (UDP 162, Interface Down) ------ |
```

## 5. VAPT Context and Exploitation
- **Information Disclosure:** `public` string allows massive data exfiltration.
- **Remote Code Execution:** `private` string allows modifying configs.
- **Amplification DDoS:** Spoofing source IP in a `GetBulk` request causes the Agent to flood the victim with data.

## Chaining Opportunities
- **Lateral Movement:** Pivot through compromised segments using [[11 - SSH Protocol Basics and Key Authentication]].
- **Payload Delivery:** Combine with [[12 - SMTP POP3 and IMAP Email Protocols]] for access.
- **Recon:** Findings feed into [[13 - SNMP Protocol Basics and Community Strings]].
- **Evasion:** Bypasses [[14 - Firewalls IDS IPS and NAT Explained]].
- **VPNs:** Compare with [[15 - VPNs IPsec and Tunneling Basics]].

## Related Notes
- [[11 - SSH Protocol Basics and Key Authentication]]
- [[12 - SMTP POP3 and IMAP Email Protocols]]
- [[13 - SNMP Protocol Basics and Community Strings]]
- [[14 - Firewalls IDS IPS and NAT Explained]]
- [[15 - VPNs IPsec and Tunneling Basics]]

## 6. Comprehensive OID and SNMPv3 Configuration Reference

### 6.1 Critical OIDs for Enumeration (VAPT Targets)
```text
# System Info
1.3.6.1.2.1.1.1.0        sysDescr (System Description, OS version)
1.3.6.1.2.1.1.5.0        sysName (Hostname)
1.3.6.1.2.1.1.4.0        sysContact (Admin Contact)
1.3.6.1.2.1.1.6.0        sysLocation (Physical Location)

# Network Interfaces & Routing
1.3.6.1.2.1.2.2.1.2      ifDescr (Interface descriptions)
1.3.6.1.2.1.4.20.1.1     ipAdEntAddr (IP Addresses assigned to device)
1.3.6.1.2.1.4.21.1.1     ipRouteDest (Routing Table Destinations)
1.3.6.1.2.1.4.21.1.7     ipRouteNextHop (Routing Table Next Hops)
1.3.6.1.2.1.3.1.1.2      atPhysAddress (ARP Table / MAC addresses)

# Processes and Software (Host Resources MIB)
1.3.6.1.2.1.25.4.2.1.2   hrSWRunName (Running processes)
1.3.6.1.2.1.25.4.2.1.4   hrSWRunPath (Path to running processes)
1.3.6.1.2.1.25.6.3.1.2   hrSWInstalledName (Installed software list)

# Windows Specific (LAN Manager MIB)
1.3.6.1.4.1.77.1.2.25.1.1  svUserTable (Windows Local Users)
1.3.6.1.4.1.77.1.2.27.1.1  svShareName (Windows SMB Shares)
1.3.6.1.4.1.77.1.2.3.1.1   svSvcName (Windows Services)
```

### 6.2 Hardened `snmpd.conf` Template (Linux)
```text
# Disable SNMPv1 and v2c entirely by not defining any 'rocommunity'
# or 'rwcommunity' strings.

# Define an SNMPv3 User (requires 'net-snmp-config --create-snmpv3-user' to set passwords)
# The user below is configured for authPriv (Authentication + Encryption)
rouser  vapt_monitor  authpriv

# Create a restricted View that only allows access to the system group and interface group
# This prevents an attacker from reading the routing table or process list even if authenticated
view    restricted_view    included   .1.3.6.1.2.1.1
view    restricted_view    included   .1.3.6.1.2.1.2

# Apply the view to a group
group   readonly_group     usm        vapt_monitor

# Bind the group to the view with authpriv requirements
access  readonly_group     ""         usm       authpriv   exact  restricted_view none none

# System Contact Information
syslocation Server Room, Rack 4
syscontact admin@example.com

# Do not listen on all interfaces. Bind specifically to the management interface.
agentaddress  udp:192.168.100.5:161

# Logging and debugging
dontLogTCPWrappersConnects yes
```

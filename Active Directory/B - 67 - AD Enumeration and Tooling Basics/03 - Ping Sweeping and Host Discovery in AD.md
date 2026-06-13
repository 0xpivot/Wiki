---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.03 Ping Sweeping and Host Discovery in AD"
---

# 67.03 Ping Sweeping and Host Discovery in AD

## 1. The Fundamentals of Host Discovery

Before an attacker can map vulnerabilities, exploit services, or move laterally within an Active Directory (AD) environment, they must first identify live hosts. Host discovery, often initiated through "ping sweeping," is the process of determining which IP addresses in a given subnet are active and responding.

In a mature AD environment, host discovery goes far beyond simply finding live IPs; it involves associating those IP addresses with computer names, operating systems, roles (e.g., Domain Controllers, File Servers, End-user Workstations), and domain affiliations.

### 1.1 Why Active Directory Discovery is Different
In a standard, unmanaged network, an attacker might rely solely on aggressive ARP or ICMP sweeping. However, in an AD environment, Domain Name System (DNS) and Lightweight Directory Access Protocol (LDAP) act as the core pillars of the network. Instead of blindly scanning large `/16` or `/24` subnets, attackers can leverage the Domain Controller's inherent knowledge of the network to pinpoint exact targets, significantly reducing noise and the likelihood of detection.

## 2. Host Discovery Mechanisms and Protocols

Understanding the layers at which discovery operates is crucial for both evading detection and ensuring accurate results.

```text
+-----------------------+
|   Attacker Machine    |
|   (Kali / Windows)    |
+---+-------+-------+---+
    |       |       |
ICMP|    ARP|    DNS|
    |       |       |
+---v-------v-------v---+        +--------------------+
|                       |  LDAP  |                    |
|   Target Subnet       +<------>+  Domain Controller |
|                       |        |  (DNS/LDAP Server) |
+-----------------------+        +--------------------+
```

### 2.1 Layer 2: ARP Sweeping
If the attacker is situated on the same physical segment or VLAN as the targets, the Address Resolution Protocol (ARP) is the most reliable discovery method.
- **Mechanism**: The attacker broadcasts "Who has IP X?" requests. Live hosts must reply with their MAC address to allow routing.
- **Pros**: ARP requests cannot be blocked by local host firewalls (such as the Windows Defender Firewall). If the network interface is active, it must answer ARP.
- **Cons**: It is strictly limited to the local broadcast domain/subnet. It cannot traverse routers.
- **Tools**: `arp-scan`, `netdiscover`, `nmap -PR`.

### 2.2 Layer 3: ICMP Echo Requests (Ping Sweeps)
This involves sending ICMP Type 8 (Echo Request) packets to a range of IPs and waiting for ICMP Type 0 (Echo Reply) packets.
- **Mechanism**: Standard network pinging.
- **Pros**: Can cross subnets and routing boundaries, allowing discovery of remote segments.
- **Cons**: Modern Windows environments heavily filter ICMP. By default, the Windows Defender Firewall blocks inbound ICMP Echo Requests unless "File and Printer Sharing" is explicitly enabled. This results in a massive false-negative rate during sweeps.
- **Tools**: `nmap -sn`, `ping`, `fping`.

### 2.3 Layer 4: TCP/UDP Port Sweeping
Instead of relying on often-blocked ICMP, checking if common Windows administrative ports are open is highly effective and accurate.
- **Target Ports**:
  - `445` (SMB) - The absolute most critical port for AD environments. If 445 is open, the machine is almost certainly a Windows host.
  - `135` (RPC) - RPC Endpoint Mapper, standard on Windows.
  - `3389` (RDP) - Remote Desktop Protocol.
  - `88` (Kerberos), `389` (LDAP), `53` (DNS) - Highly indicative of a Domain Controller.
- **Tools**: `nmap -PS445,135,3389`, NetExec.

## 3. Active Directory Native Host Discovery (Living off the Land)

The most effective, stealthy way to discover hosts in an AD environment isn't to scan the network via packets—it's to ask the network infrastructure directly.

### 3.1 DNS Zone Transfers (AXFR)
If the primary DNS server (typically the Domain Controller) is severely misconfigured, it may allow any unauthenticated client to request a full, complete copy of the DNS zone. This provides an immediate, complete list of all hostnames and their corresponding IP addresses in the domain.
```bash
# Attempt a zone transfer against the Domain Controller
dig axfr @<DC_IP> target.local
```

### 3.2 DNS Reverse Lookups (PTR Sweeps)
If zone transfers fail, attackers can perform Reverse DNS lookups across the subnet range. Because AD automatically registers and manages DNS records for all domain-joined machines, reverse lookups will systematically yield computer names for active IPs.

### 3.3 LDAP Computer Enumeration
Every domain-joined machine possesses a computer object within Active Directory. By querying LDAP directly, an attacker can obtain a comprehensive list of every machine that has ever been joined to the domain.
- **PowerView**: `Get-NetComputer -Ping`
- **Impacket**: `GetADUsers.py target.local/user:pass -all` (Also fetches computer objects)
- **NetExec**: `nxc smb <DC_IP> -u user -p pass --computers`

*Note: LDAP provides a list of domain computers, but it does not inherently indicate if they are currently powered on or what their current dynamic IP is. The attacker must resolve the returned hostnames to IPs and probe them.*

## 4. Practical Tool Usage and Command Reference

### 4.1 Nmap Host Discovery
Nmap remains the industry standard for network-level host discovery.

```bash
# Classic Ping Sweep (Prone to false negatives due to Windows Firewall)
nmap -sn 192.168.1.0/24

# TCP SYN Ping on AD Ports (Highly reliable for Windows networks, skips ICMP)
nmap -sn -PS445,135,3389,80,443 192.168.1.0/24

# Outputting to a 'grepable' format to quickly extract live IPs for other tools
nmap -sn -PS445 192.168.1.0/24 -oG sweep.txt
grep "Status: Up" sweep.txt | cut -d ' ' -f 2 > live_hosts.txt
```

### 4.2 NetExec (CrackMapExec) for Intelligent Sweeping
NetExec is exceptional because it does not just discover the host via SMB (Port 445); it immediately fingerprints the operating system, hostname, and domain architecture.

```bash
# Sweep a /24 network using anonymous/null sessions to discover hosts
nxc smb 192.168.1.0/24

# Extracting live hosts and specifically identifying Domain Controllers
nxc smb 192.168.1.0/24 | grep -i "Windows"
nxc smb 192.168.1.0/24 | grep -i "(name:" | grep -i "DC"
```

## 5. Operational Security (OPSEC) and Evasion

### 5.1 Noise Reduction Strategies
- Sweeping a large `/16` network using fast Nmap settings (`-T4` or `-T5`) generates millions of packets. Network Intrusion Detection Systems (NIDS) and modern EDR network sensors will instantly flag this anomalous behavior.
- **Stealth Approach**: Instead of scanning blindly, limit sweeping to specific `/24` subnets obtained from analyzing LDAP data (e.g., pulling the `operatingSystem` attribute, identifying the Domain Controllers, and targeting their specific subnets first).

### 5.2 Bypassing Defenses
- To evade simple port scanning detection heuristics, randomize the target order (`--randomize-hosts` in nmap) and introduce significant packet delays (`--scan-delay`).
- Rely heavily on LDAP queries and DNS queries rather than direct packet-level probing whenever possible. Querying LDAP is considered "living off the land," while network port sweeps are inherently adversarial and easier to detect.

## 6. Defensive Countermeasures and Detection

### 6.1 Detecting Host Discovery
1. **Network Sensors**: Tools like Zeek, Suricata, or Snort can easily detect ICMP sweeps, ARP sweeps, and horizontal port scans (e.g., a single internal IP connecting to port 445 on 200 distinct IPs within a 5-second window).
2. **Deception Technology (Honeypots)**: Deploying internal honeypots or "honey ports." If any machine attempts to communicate with an unassigned IP address or interacts with a fake service on an internal honeypot, a high-fidelity alert is immediately triggered.
3. **DNS Anomaly Detection**: Monitoring for anomalous volumes of Reverse DNS (PTR) lookups originating from a single endpoint, which strongly indicates an active network sweep.

### 6.2 Mitigation and Hardening
- **Network Segmentation**: Implement strict VLANs and routing rules. A compromised workstation in the HR VLAN should fundamentally not be able to route traffic to the IT Admin VLAN.
- **Host-Based Firewalls**: Maintain the Windows Defender Firewall in an active state. Restrict inbound SMB/RPC strictly to management IPs (e.g., authorized jump boxes, vulnerability scanners) rather than allowing lateral, unrestricted workstation-to-workstation SMB traffic.
- **Secure DNS Configurations**: Ensure DNS zone transfers are strictly limited to authorized replication partners (other Domain Controllers).

## Real-World Attack Scenario

An attacker breaches the perimeter and lands on an isolated corporate VLAN. Knowing that standard ICMP ping sweeps are blocked by the Windows Defender Firewall, they avoid noisy `nmap -sn` scans that would trigger the network intrusion detection system (NIDS). Instead, they live off the land by querying the Domain Controller directly using LDAP (`Get-NetComputer` via PowerView) to obtain a complete list of all active computer objects. With this precise list, the attacker performs a targeted TCP SYN sweep (`nmap -PS445`) solely on the identified IPs to confirm which machines are currently online, dramatically reducing network noise and discovering several undocumented development servers ripe for exploitation.

## Chaining Opportunities
- Once live hosts are identified and their operating systems fingerprinted, use tools to authenticate against them, validate credentials, or look for lateral movement paths. See [[04 - NetExec CrackMapExec Basics and Module Usage]].
- Use the discovered IP list to feed into **BloodHound** or **PowerView** to correlate active IPs with Active Directory objects, group memberships, and session data.
- Explore LDAP-based computer enumeration techniques described in [[05 - Enumerating Users and Groups via LDAP]] to narrow down target lists before sweeping.

## Related Notes
- [[01 - Introduction to BloodHound and SharpHound]]
- [[02 - Using PowerView for AD Enumeration]]
- [[04 - NetExec CrackMapExec Basics and Module Usage]]
- [[05 - Enumerating Users and Groups via LDAP]]

## Advanced Threat Hunting and Behavioral Analytics

As evasion techniques evolve, reliance on static indicators of compromise (IoCs) is insufficient. Defenders must pivot to behavioral analytics.

### Baseline Deviation Analysis
Instead of hunting for specific tool signatures (like `SharpHound.exe` or `PowerView.ps1`), mature SOCs establish baselines of administrative behavior.
1. **Administrative Logon Baselines**: Identify the standard jump boxes and IP ranges used by authorized administrators. Any high-privileged authentication originating from a non-standard workstation (e.g., a receptionist's PC) triggers an immediate severity-high alert, regardless of the tool used.
2. **Protocol Baselines**: Standard users rarely, if ever, initiate raw RPC or WMI connections to other workstations. Detecting a high volume of lateral SMB/RPC traffic originating from a standard subnet is a strong behavioral indicator of enumeration or lateral movement.

### Leveraging Graph Databases for Defense
Defenders can utilize the exact same graph theory concepts employed by attackers to secure the environment proactively.
- **Continuous Ingestion**: By scheduling daily or weekly automated ingestions of AD data into a defensive Neo4j database, defenders can track changes over time.
- **Chokepoint Identification**: Graph analysis reveals "chokepoints"—specific users or groups that serve as critical bridges in numerous attack paths. Removing privileges from these chokepoint accounts fractures the attack graph, significantly increasing the effort required by an attacker.
- **Unintended Permission Auditing**: Graph databases easily highlight misconfigurations such as standard users accidentally granted `GenericAll` rights over critical infrastructure OUs due to complex, nested group memberships.

### Conclusion
Active Directory enumeration is a delicate balance of noise versus insight. Attackers must constantly adapt to increasingly sophisticated telemetry and detection mechanisms. For defenders, understanding the mechanics of these enumeration tools is paramount. Security is no longer just about preventing the initial compromise; it is about anticipating the attacker's post-exploitation reconnaissance and disrupting their ability to discover the pathways to domain dominance.

### Real-World Incident Response Scenarios
When responding to suspected AD enumeration:
1. **Isolate Suspect Endpoints**: Immediately quarantine the endpoint initiating the anomalous LDAP or RPC queries.
2. **Review TGT Requests**: Correlate the endpoint activity with Event ID 4768 (A Kerberos authentication ticket (TGT) was requested) to identify the compromised account.
3. **Analyze BloodHound Execution**: If SharpHound is suspected, search for Event ID 4688 containing command-line arguments like `--CollectionMethod` or `--Loop`.
4. **Implement Tiered Administration**: If widespread enumeration is detected, immediately restrict Tier-0 accounts from authenticating to lower-tier systems to break potential `HasSession` escalation paths.

## Glossary of Advanced Terms
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket used to request access to other services.
- **SPN (Service Principal Name)**: A unique identifier for a service instance, used in Kerberos authentication.
- **ACL (Access Control List)**: A list of permissions attached to an object.
- **DCSync**: An attack technique simulating a Domain Controller to request password hashes via the Directory Replication Service (DRS) Remote Protocol.
- **Pass-the-Hash (PtH)**: Authenticating to a remote system using the underlying NTLM hash of a user's password, rather than the plaintext password itself.

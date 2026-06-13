---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.09 Identifying Domain Controllers"
---

# 09 - Identifying Domain Controllers and Global Catalogs

## 1. Introduction to Domain Controllers (DCs)

In an Active Directory (AD) infrastructure, the Domain Controller (DC) is the ultimate source of truth. It is the server that responds to security authentication requests (logging in, checking permissions) within the Windows domain. It stores user account information, authenticates users, and enforces security policies. 

For a penetration tester or red teamer, identifying the Domain Controllers is usually step zero after gaining initial access. The DCs represent the "crown jewels" of the network. Compromising a DC typically grants complete administrative control over the entire domain. Furthermore, DCs are the primary targets for numerous enumeration techniques, including LDAP queries, SMB share enumeration (SYSVOL), and Kerberos ticket requests.

### 1.1 The Global Catalog (GC)
A Global Catalog (GC) is a specific role held by one or more Domain Controllers in a forest. While a standard DC holds a complete replica of all objects in its own domain, a Global Catalog server holds a complete replica of its own domain AND a partial, read-only replica of all objects in *every other domain* within the forest.
- Standard LDAP operates on TCP port **389** (and 636 for LDAPS).
- Global Catalog LDAP operates on TCP port **3268** (and 3269 for GC over SSL).
Querying the GC is incredibly valuable during a VAPT engagement in multi-domain forests, as it allows an attacker to search for users, groups, and attributes across the entire forest boundary from a single endpoint.

### 1.2 FSMO Roles
Flexible Single Master Operations (FSMO) roles are specialized tasks assigned to specific Domain Controllers. While all DCs can handle authentication, certain operations must be handled by a single DC to prevent conflicts. The five FSMO roles are:
1. Schema Master (Forest-wide)
2. Domain Naming Master (Forest-wide)
3. PDC Emulator (Domain-wide) - *Critical for password changes and time sync.*
4. RID Master (Domain-wide) - *Allocates SIDs.*
5. Infrastructure Master (Domain-wide)

## 2. Architecture and Discovery Diagram

The following ASCII diagram shows how a client (or an attacker) dynamically locates a Domain Controller using DNS Service (SRV) records.

```text
+-----------------------+                                      +-------------------------------+
|   Attacker / Client   |                                      |        DNS Server (DC)        |
|   IP: 192.168.1.100   |                                      |        IP: 192.168.1.10       |
+-----------+-----------+                                      +---------------+---------------+
            |                                                                  |
            | 1. DNS Query: SRV _ldap._tcp.dc._msdcs.domain.local              |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 2. DNS Response: Target=dc01.domain.local, Port=389              |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 3. DNS Query: A Record for dc01.domain.local                     |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 4. DNS Response: 192.168.1.10                                    |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 5. Initiate LDAP / Kerberos Connection to 192.168.1.10           |
            |----------------------------------------------------------------->|
            |                                                                  |
+-----------+-----------+                                      +-------------------------------+
| Attacker now knows    |                                      | AD heavily relies on DNS.     |
| exactly where to aim  |                                      | Discovering the DC is a built-|
| BloodHound or NetExec.|                                      | in, native network function.  |
+-----------------------+                                      +-------------------------------+
```

## 3. Enumeration Tooling and Techniques

Identifying DCs and GCs does not require complex exploits; it relies entirely on native network protocols and administrative tools.

### 3.1 DNS SRV Record Lookups (nslookup / dig)

Because Active Directory relies fundamentally on DNS to function, domain-joined machines use DNS Service (SRV) records to locate DCs. Attackers can query these exact same records.

**Using native Windows `nslookup`:**
```cmd
nslookup -type=SRV _ldap._tcp.dc._msdcs.domain.local
```

**Using Linux `dig`:**
```bash
dig _ldap._tcp.dc._msdcs.domain.local SRV
```

**Finding the PDC Emulator (Primary Domain Controller):**
```bash
dig _ldap._tcp.pdc._msdcs.domain.local SRV
```

**Finding Global Catalog Servers:**
```bash
dig _ldap._tcp.gc._msdcs.domain.local SRV
```

### 3.2 Network Scanning (Nmap)

If you are on an internal network but do not know the domain name to query DNS, you can scan the subnet for servers exposing typical DC ports.

**Command:**
```bash
nmap -p 88,389,445,3268 192.168.1.0/24 -sV
```
**Indicators of a Domain Controller:**
- Port 88 (Kerberos) is open.
- Port 389 (LDAP) is open.
- Port 3268 (Global Catalog) is open.
If a machine has port 88 open, it is almost certainly a Domain Controller.

### 3.3 Living off the Land (nltest)

`nltest` is a highly valuable built-in Windows command-line utility used by administrators to test domain trusts and secure channels. It is excellent for OpSec as it is a native binary.

**Identify the authenticating DC:**
```cmd
nltest /dsgetdc:domain.local
```

**Output snippet:**
```text
           DC: \\DC01.domain.local
      Address: \\192.168.1.10
     Dom Guid: a1b2c3d4-e5f6-7a8b-9c0d-1234567890ab
     Dom Name: domain.local
  Forest Name: domain.local
 Dc Site Name: Default-First-Site-Name
Our Site Name: Default-First-Site-Name
        Flags: PDC GC DS LDAP KDC TIMESERV GTIME WRITABLE DNS_DC DNS_DOMAIN DNS_FOREST CLOSE_SITE FULL_SECRET WS DS_8 DS_9 DS_10
The command completed successfully
```
*Note the Flags: `GC` indicates it is a Global Catalog, `PDC` indicates the PDC Emulator, `KDC` indicates Kerberos Key Distribution Center.*

### 3.4 PowerView (PowerShell)

PowerView abstracts complex LDAP queries into simple cmdlets.

**Find all Domain Controllers:**
```powershell
Get-DomainController
```

**Find Global Catalogs:**
```powershell
Get-DomainController -GlobalCatalog
```

### 3.5 NetExec (formerly CrackMapExec)

If you have a large list of IPs and want to identify which ones are DCs, you can use NetExec.

**Command:**
```bash
nxc smb 192.168.1.0/24
```
NetExec parses the SMB response and explicitly tags Domain Controllers in its output with `(name:DC01) (domain:domain.local) (signing:True) (SMBv1:False)`. Note that DCs require SMB signing by default.

## 4. Why Target the Global Catalog?

When performing AD enumeration in a large corporate network consisting of a root domain (e.g., `corp.local`) and multiple child domains (e.g., `us.corp.local`, `eu.corp.local`), querying standard LDAP (389) will only return objects in the specific domain you are querying.

If you direct BloodHound, PowerView, or standard LDAP queries to the Global Catalog port (3268), the GC will return objects across the entire forest. This allows an attacker in a low-privileged child domain to map out users, groups, and potential attack paths in the highly privileged root domain without directly querying the root DC.

## 5. Defensive Considerations

### 5.1 The Reality of DC Discovery
It is practically impossible to hide Domain Controllers or prevent their discovery. AD architecture requires clients to easily and rapidly locate DCs to function. Defensive efforts should not focus on hiding DCs, but rather on protecting them and monitoring the traffic directed at them.

### 5.2 Telemetry and Monitoring
- **Excessive LDAP Queries:** Implement detections for excessive or anomalous LDAP queries targeting DCs, especially those pulling large amounts of data (like BloodHound's SharpHound collector).
- **DNS Monitoring:** Monitor for unexpected internal endpoints querying SRV records extensively, although this can be noisy.
- **Rogue DCs:** Monitor for Event ID 4624 (Logon) from unusual machines, or implement DC Shadow detection (Event ID 5136 - Directory Service Object Modification) to detect attackers attempting to register rogue Domain Controllers in the environment.

## 6. Chaining Opportunities

- **DCSync Attacks:** Once a DC is identified and the attacker has obtained Domain Admin or Replicator privileges, they can target the DC with a DCSync attack to replicate password hashes (NTLM) over the network.
- **Pass-the-Ticket (PtT):** Knowing the DC's IP allows the attacker to forcefully point their tools at it to request Service Tickets or TGTs using compromised Kerberos keys.
- **ZeroLogon / PetitPotam:** High-impact vulnerabilities often target the DC directly via MSRPC. Identifying the DC is the required first step before launching these exploits.

## 7. Related Notes
- [[05 - Active Directory Architecture Overview]]
- [[10 - Enumerating AD Trusts and Forest Boundaries]]
- [[25 - DCSync Attacks and Secrets Extraction]]
- [[13 - BloodHound and Active Directory Graph Analysis]]

## Real-World Attack Scenario
## Real-World Attack Scenario

During a red team engagement for a large manufacturing enterprise, I was dropped into an isolated VLAN with no prior knowledge of the network architecture. Before any offensive actions could be taken, I needed to precisely locate the Active Directory Domain Controllers (DCs) and Global Catalog (GC) servers. Identifying these core infrastructure assets is the critical first step for any AD-based attacks, such as password spraying, AS-REP roasting, or dumping NTDS.dit.

**Thought Process:**
Randomly scanning the `/16` network for port 389 (LDAP) or 53 (DNS) would be incredibly noisy and likely trigger immediate SOC alerts. Instead, I opted to passively leverage the environment's own DNS infrastructure. Domain computers rely on specific DNS Service (SRV) records to locate DCs and GCs. By querying these standard records, I could map out the forest hierarchy and identify the primary authentication servers completely legitimately, blending in with normal network traffic.

**Execution:**
Using the standard Linux `dig` utility on my attack box, I first queried the SOA (Start of Authority) record to confirm the domain name of the environment, which was `corp.manufacturing.local`.
```bash
dig SOA corp.manufacturing.local
```
Next, to locate the Domain Controllers, I queried the `_ldap._tcp.dc._msdcs` SRV records:
```bash
dig _ldap._tcp.dc._msdcs.corp.manufacturing.local SRV
```
The response returned three distinct IP addresses, indicating multiple DCs (e.g., `dc01.corp...`, `dc02.corp...`). 

Knowing that multi-domain forests heavily rely on Global Catalogs for cross-domain searches, I specifically queried the GC SRV records to find the servers holding the universal group membership information:
```bash
dig _gc._tcp.corp.manufacturing.local SRV
```
This revealed that only `dc01.corp.manufacturing.local` was acting as the Global Catalog. 

To verify connectivity and exact OS version without an intrusive scan, I used NetExec to perform an anonymous SMB connection check against the identified DCs:
```bash
nxc smb 10.50.10.10 10.50.10.11
```

**Outcome:**
Through legitimate DNS queries alone, I mapped the entire AD hierarchy, pinpointing the primary DCs and the sole Global Catalog server. This allowed me to perfectly target my subsequent LDAP enumeration and Kerberos-based attacks (like Kerberoasting) directly at `dc01`, maximizing efficiency and remaining entirely under the radar of network intrusion detection systems that look for broad port scans.


